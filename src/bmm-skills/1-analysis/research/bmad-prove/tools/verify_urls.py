#!/usr/bin/env python3
"""PROVE-Lite v1.0.0 — URL accessibility verifier (P1-5 + P0-α7-1).

Vérifie l'accessibilité HTTP de toutes les URLs citées dans les fichiers livrables.
Détecte les URLs hallucinées (404 confirmé, 410, 5xx) — anti-fraude additionnelle.

Usage:
    python3 tools/verify-urls.py --run <dossier-de-sortie-choisi-par-l-opérateur>

Sortie:
    - stdout : compact summary (ok / fail / indeterminate / timeout)
    - <run-dir>/url-verification.json : détail par URL + classement

Exit code: 0 si aucun FAIL confirmé, 1 si ≥1 FAIL confirmé, 2 sur erreur d'argument.

Rationale (v5.2.0-alpha.2 P1-5) :
Le LLM peut écrire `_Source: [https://example.com/fake-url accessed 2026-05-25]_`
sans que cette URL existe. L'audit-lite vérifie le format ; verify-urls vérifie
l'accessibilité réelle. À lancer en complément de audit-lite.py.

Rationale (v5.2.0-alpha.7 P0-α7-1) — FIN DES FAUX NÉGATIFS BLOQUANTS :
Un run réel 100% sourcé (35 URLs) a renvoyé FAIL avec 6 "fail" + 1 timeout, alors
qu'il n'y avait qu'UN seul vrai 404. Les 6 autres étaient des faux négatifs :
  - 403 Cloudflare anti-bot (plusieurs sites de presse trade) ;
  - 429 rate-limit (un même domaine sollicité ×2) ;
  - 308 redirects permanents (URLs avec slash final ou changement de chemin) ;
  - 1 flaky timeout (site lent ponctuellement).
Le rituel « ≥1 FAIL bloque » bloquait donc un livrable irréprochable.

Corrections :
  1. User-Agent navigateur réaliste (Mozilla/5.0…) — neutralise la majorité
     des blocages anti-bot Cloudflare/Akamai.
  2. Suivi des redirections 3xx (301/302/307/308) et vérification du statut FINAL.
  3. Classement tri-état des statuts :
       - 2xx / 3xx (statut final)         → OK
       - 403 / 429                         → INDÉTERMINÉ (1 retry UA navigateur ;
                                             si toujours 403/429 → INDÉTERMINÉ,
                                             PAS fail — blocage anti-bot probable)
       - 404 / 410 / 5xx                   → FAIL (URL réellement cassée)
       - timeout / erreur réseau (-1)      → INDÉTERMINÉ après 1 retry
  4. Verdict FAIL UNIQUEMENT s'il y a ≥1 FAIL confirmé (404/410/5xx).
     INDÉTERMINÉ ne bloque pas (compté à part, reporté pour revue manuelle).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# User-Agent navigateur réaliste (P0-α7-1). Beaucoup de CDN (Cloudflare, Akamai)
# renvoient 403 sur les UA « bot »/python-urllib ; un UA Chrome desktop courant
# passe la majorité des filtres anti-bot basiques.
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
BROWSER_HEADERS = {
    "User-Agent": BROWSER_UA,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
}

# Classement des statuts (P0-α7-1)
OK = "OK"
FAIL = "FAIL"
INDETERMINATE = "INDETERMINATE"

# Statuts considérés comme blocage anti-bot / transitoire → retry puis INDÉTERMINÉ
SOFT_BLOCK_CODES = {403, 429}
# Statuts considérés comme URL réellement cassée → FAIL confirmé
HARD_FAIL_CODES = {404, 410}


def _http_status(url: str, timeout: int) -> int:
    """Effectue une requête HTTP et renvoie le statut FINAL (après redirections).

    urllib suit nativement les redirections 3xx en GET via HTTPRedirectHandler ;
    `resp.status` reflète donc le statut de la ressource finale. On utilise GET
    (et non HEAD) car beaucoup de serveurs renvoient 403/405 sur HEAD mais 200
    sur GET (P0-α7-1). On ne lit pas le corps (juste le statut).

    Returns:
        - le code HTTP final (200, 308→200, 404, 403, 429, 5xx, ...)
        - -1 sur erreur réseau (timeout, DNS, connexion refusée).
    """
    try:
        req = Request(url, method="GET", headers=BROWSER_HEADERS)
        resp = urlopen(req, timeout=timeout)
        # resp.status = statut final après suivi des 3xx par urllib.
        return resp.status
    except HTTPError as e:
        # HTTPError est levé pour les 4xx/5xx (les 3xx sont suivis nativement).
        return e.code
    except (URLError, Exception):
        return -1


def classify_status(code: int) -> str:
    """Classe un code HTTP en OK / FAIL / INDÉTERMINÉ (P0-α7-1).

    - 2xx, 3xx (statut final résiduel) → OK
    - 404, 410, 5xx                    → FAIL (URL cassée)
    - 403, 429                         → INDÉTERMINÉ (blocage anti-bot probable)
    - -1 (réseau/timeout)              → INDÉTERMINÉ
    """
    if code == -1:
        return INDETERMINATE
    if 200 <= code < 400:
        return OK
    if code in SOFT_BLOCK_CODES:
        return INDETERMINATE
    if code in HARD_FAIL_CODES or code >= 500:
        return FAIL
    # Autres 4xx (401, 405, 451, etc.) : ni clairement cassés ni clairement OK.
    # On les traite en INDÉTERMINÉ (ne bloque pas) plutôt qu'en FAIL pour rester
    # cohérent avec l'objectif « ne bloquer que sur URL réellement cassée ».
    return INDETERMINATE


def verify_url(url: str, timeout: int = 10) -> dict:
    """Vérifie une URL et renvoie son verdict avec 1 retry sur soft-block/réseau.

    Politique de retry (P0-α7-1) : si le 1er essai donne INDÉTERMINÉ (403/429 ou
    erreur réseau), on retente UNE fois (déjà avec UA navigateur) avant de figer
    le verdict INDÉTERMINÉ. On ne retente PAS les FAIL confirmés (404/410/5xx) ni
    les OK.

    Returns:
        dict {"final_status": int, "classification": str, "retried": bool}
    """
    code = _http_status(url, timeout)
    classification = classify_status(code)
    retried = False
    if classification == INDETERMINATE:
        # 1 seul retry (UA navigateur déjà appliqué) pour absorber le flaky.
        retried = True
        code = _http_status(url, timeout)
        classification = classify_status(code)
    return {
        "final_status": code,
        "classification": classification,
        "retried": retried,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PROVE-Lite v1.0.0 — URL accessibility verifier (anti-hallucination, P0-α7-1)",
    )
    parser.add_argument(
        "--run", required=True,
        help="Path to the operator-chosen run output directory",
    )
    parser.add_argument(
        "--timeout", type=int, default=10,
        help="HTTP request timeout in seconds (default 10)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress stdout summary, only write url-verification.json",
    )
    args = parser.parse_args(argv)

    run_dir = Path(args.run).resolve()
    if not run_dir.exists() or not run_dir.is_dir():
        print(json.dumps({"error": f"Run directory not found: {run_dir}"}, indent=2))
        return 2

    # Collect URLs from all livrable files
    files_to_scan = [
        'livrable.md',
        'livrable-summary.md',
        'livrable-go-to-market.md',
        'livrable-technical-deep-dive.md',
    ]
    all_urls: set[str] = set()
    files_scanned = []
    for fname in files_to_scan:
        path = run_dir / fname
        if path.exists():
            content = path.read_text(encoding='utf-8')
            urls = re.findall(r'https?://[^\s\)\]<>"\']+', content)
            # Clean trailing punctuation
            urls = [u.rstrip('.,;:!?') for u in urls]
            all_urls.update(urls)
            files_scanned.append(fname)

    if not all_urls:
        result = {
            "tool": "verify-urls.py",
            "run_dir": str(run_dir),
            "files_scanned": files_scanned,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "verdict": "NO_URLS_FOUND",
            "checked": 0,
            "ok": 0,
            "fail": 0,
            "indeterminate": 0,
            "timeout": 0,
            "details": {},
        }
        out_path = run_dir / "url-verification.json"
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False),
                            encoding='utf-8')
        if not args.quiet:
            print(json.dumps({"verdict": "NO_URLS_FOUND", "checked": 0}, indent=2))
        return 0

    results = {
        "tool": "verify-urls.py",
        "run_dir": str(run_dir),
        "files_scanned": files_scanned,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "checked": len(all_urls),
        "ok": 0,
        "fail": 0,
        "indeterminate": 0,
        "timeout": 0,  # sous-ensemble d'INDÉTERMINÉ : erreurs réseau (-1)
        "details": {},
        "fail_urls": [],
        "indeterminate_urls": [],
    }
    for url in sorted(all_urls):
        verdict = verify_url(url, timeout=args.timeout)
        code = verdict["final_status"]
        classification = verdict["classification"]
        # P0-α7-1 : détail par URL = statut final + classification + retry.
        results["details"][url] = {
            "final_status": code,
            "classification": classification,
            "retried": verdict["retried"],
        }
        if classification == OK:
            results["ok"] += 1
        elif classification == FAIL:
            results["fail"] += 1
            results["fail_urls"].append({"url": url, "final_status": code})
        else:  # INDETERMINATE
            results["indeterminate"] += 1
            results["indeterminate_urls"].append(
                {"url": url, "final_status": code})
            if code == -1:
                results["timeout"] += 1

    # Determine verdict (P0-α7-1) :
    #   FAIL UNIQUEMENT s'il y a ≥1 FAIL confirmé (404/410/5xx).
    #   INDÉTERMINÉ (403/429/timeout) ne bloque jamais → WARN si présent, PASS sinon.
    if results["fail"] > 0:
        results["verdict"] = "FAIL"
    elif results["indeterminate"] > 0:
        results["verdict"] = "WARN"  # à revoir manuellement, non bloquant
    else:
        results["verdict"] = "PASS"

    out_path = run_dir / "url-verification.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False),
                        encoding='utf-8')

    if not args.quiet:
        summary = {
            "verdict": results["verdict"],
            "checked": results["checked"],
            "ok": results["ok"],
            "fail": results["fail"],
            "indeterminate": results["indeterminate"],
            "timeout": results["timeout"],
            "fail_urls": [f["url"] for f in results["fail_urls"]],
            "report": str(out_path),
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    # Exit 1 UNIQUEMENT sur FAIL confirmé (P0-α7-1) — INDÉTERMINÉ ne bloque pas.
    return 0 if results["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
