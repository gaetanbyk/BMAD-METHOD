#!/usr/bin/env python3
"""PROVE (bmad-prove) — Audit post-delivery.

28 structural checks on the deliverable (C1-C26 ported from PROVE-Lite v1.0.0,
plus C27 ip_tam_competitive_sourced and C28 cross_validation_traced).

Run in <10 seconds. Out of session.

Framework 100% agnostic — no real company/technology/product names.
Checks C27 and C28 are specific to bmad-prove's cross-agent validation and
IP/TAM/competitive analysis requirements.

Usage:
    python3 tools/audit.py --run <output-folder>

Output:
    - stdout: JSON summary verdict
    - <output-folder>/audit.json: full report

Verdict: PASS | WARN | FAIL
Exit code: 0 (PASS/WARN) | 1 (FAIL)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_VALID_MARKET_POSTURES = {"auto", "vertical", "horizontal"}


# ============================================================
# Helpers
# ============================================================

def _split_sections(text: str) -> dict[str, str]:
    """Split livrable.md into sections keyed by §N marker."""
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(§\d+)\b", line)
        if m:
            if current_key:
                sections[current_key] = "\n".join(current_lines)
            current_key = m.group(1)
            current_lines = []
        elif current_key:
            current_lines.append(line)
    if current_key:
        sections[current_key] = "\n".join(current_lines)
    return sections


def _count_argumentative_words(text: str) -> int:
    """Count words excluding URLs and _Source: [...] blocks (P0-α7-6)."""
    cleaned = re.sub(r"_Source:\s*\[[^\]]*\]_?", " ", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"https?://\S+", " ", cleaned)
    return len(cleaned.split())


def _extract_tier1_fiches(livrable: str) -> list[str]:
    """Extract fiche bodies for Tier-1 (INDISPENSABLE) targets from §4/§5."""
    return re.findall(
        r"###\s+#\d+[^#\n]*INDISPENSABLE[^#\n]*\n(.*?)(?=###\s+#|\Z)",
        livrable, re.DOTALL | re.IGNORECASE,
    )


def _extract_all_fiches(livrable: str) -> list[tuple[str, str]]:
    """Extract all fiches (name, body) from §4."""
    sections = _split_sections(livrable)
    s4 = sections.get("§4", "")
    return re.findall(
        r"###\s+#\d+\s+—\s+([^\n]+)\n(.*?)(?=###\s+#\d+\s+—|\Z)",
        s4, re.DOTALL,
    )


def _extract_origin_sectors(intake_text: str) -> list[str]:
    m = re.search(r"existing_clients_subsectors\s*:\s*\[([^\]]*)\]", intake_text)
    if m:
        return [s.strip().strip('"\'') for s in m.group(1).split(",") if s.strip()]
    return []


def _extract_existing_use_case(intake_text: str) -> str:
    m = re.search(r"existing_use_case\s*:\s*[\"']?(.+?)[\"']?\s*(?:\n|$)", intake_text)
    return m.group(1).strip() if m else ""


def _extract_must_consider_targets(intake_text: str) -> list[str]:
    m = re.search(r"must_consider_targets\s*:\s*\[([^\]]*)\]", intake_text)
    if m:
        return [s.strip().strip('"\'') for s in m.group(1).split(",") if s.strip()]
    return []


def _extract_market_posture(intake_text: str) -> str:
    m = re.search(r"market_posture\s*:\s*[\"']?(\w+)[\"']?", intake_text)
    if m:
        v = m.group(1).strip().lower()
        return v if v in _VALID_MARKET_POSTURES else "auto"
    return "auto"


def _extract_direct_competitors(intake_text: str) -> list[str]:
    m = re.search(r"direct_competitors\s*:\s*\[([^\]]*)\]", intake_text)
    if m:
        return [s.strip().strip('"\'') for s in m.group(1).split(",") if s.strip()]
    return []


def _extract_session_id(intake_text: str) -> str:
    m = re.search(r"session_id\s*:\s*[\"']?(.+?)[\"']?\s*(?:\n|$)", intake_text)
    return m.group(1).strip() if m else ""


# ============================================================
# C1 — Complete structure (§1..§7)
# ============================================================
def _check_structure(livrable: str, findings: list[dict]) -> str:
    expected = [
        ("§1", 200, 350), ("§2", 500, 900), ("§3", 300, 500),
        ("§4", 1200, 3000), ("§5", 1000, 3000), ("§6", 500, 900), ("§7", 200, 350),
    ]
    sections = _split_sections(livrable)
    missing = [m for m, _, _ in expected if m not in sections]
    if missing:
        findings.append({"check": "C1", "severity": "FAIL",
                         "title": f"Missing required sections: {', '.join(missing)}",
                         "fix": "Add missing sections according to prove.template.md"})
        return "FAIL"

    out_of_range = []
    for marker, wc_min, wc_max in expected:
        wc = _count_argumentative_words(sections[marker])
        if wc < wc_min or wc > wc_max * 1.3:
            out_of_range.append(f"{marker} ({wc} words, expected {wc_min}-{wc_max})")

    stray = sorted(
        (m for m in sections if re.fullmatch(r"§\d+", m) and int(m[1:]) >= 8),
        key=lambda s: int(s[1:]),
    )
    if stray:
        findings.append({"check": "C1", "severity": "WARN",
                         "title": f"Sections beyond §7 present: {', '.join(stray)} — deliverable stops at §7",
                         "fix": "Remove §8+ sections. Integrate useful content into §6 or §7."})
        return "WARN"

    if out_of_range:
        findings.append({"check": "C1", "severity": "WARN",
                         "title": f"Wordcount out of range: {', '.join(out_of_range[:3])}",
                         "fix": "Extend or condense affected sections to match format"})
        return "WARN"
    return "PASS"


# ============================================================
# C2 — 3 cardinal questions answered in §1
# ============================================================
def _check_three_questions(livrable: str, findings: list[dict]) -> str:
    sections = _split_sections(livrable)
    s1 = sections.get("§1", "").lower()
    if not s1:
        findings.append({"check": "C2", "severity": "FAIL",
                         "title": "§1 Synthèse exécutive absent",
                         "fix": "Add §1 answering the 3 cardinal questions (who / indispensable / monetize)"})
        return "FAIL"
    missing = []
    if not re.search(r"\bà\s*qui\b|\ba\s*qui\b|who\s+needs\b|qui\s+ça\s+sert", s1):
        missing.append('"à qui"')
    if "indispensable" not in s1:
        missing.append('"indispensable"')
    if not re.search(r"monétis|monetis|monetiz", s1):
        missing.append('"monétiser"')
    if missing:
        findings.append({"check": "C2", "severity": "FAIL",
                         "title": f"§1 does not answer all 3 cardinal questions (missing: {', '.join(missing)})",
                         "fix": "Rewrite §1 explicitly answering: who / indispensable / monetize"})
        return "FAIL"
    return "PASS"


# ============================================================
# C3 — Applicative diversity (monetization model field)
# ============================================================
_BASELINE_MODEL = "install_projet"
_KNOWN_MODELS = {"sdk_royalty", "licence_ip", "certification", "service",
                 "kit_vente", "nre_runrate", "install_projet", "abonnement"}


def _extract_monetisation_model(fiche_body: str) -> str | None:
    m = re.search(r"mod[èe]le\s+de\s+mon[ée]tisation\s*\**\s*[:=]\s*\**\s*([^\n*]+)",
                  fiche_body, re.IGNORECASE)
    if not m:
        return None
    raw = m.group(1).strip().lower().strip("*_`.,:;()[] ")
    raw = re.sub(r"[\s\-]+", "_", raw)
    raw = raw.translate(str.maketrans("àâäéèêëîïôöùûüç", "aaaeeeeiioouuuc"))
    return raw


def _check_applicative_diversity(livrable: str, existing_use_case: str,
                                  origin_sectors: list[str],
                                  findings: list[dict],
                                  market_posture: str = "auto") -> str:
    fiches = _extract_all_fiches(livrable)
    if not fiches:
        findings.append({"check": "C3", "severity": "FAIL",
                         "title": "§4 contains no fiches in `### #N — <Name>` format",
                         "fix": "Format fiches as ### #N — Name with structured bullets"})
        return "FAIL"
    total = len(fiches)
    models = [_extract_monetisation_model(body) for _, body in fiches]
    fiches_with_model = [m for m in models if m is not None]
    if not fiches_with_model:
        findings.append({"check": "C3", "severity": "WARN",
                         "title": "No `Modèle de monétisation` field found in any fiche",
                         "fix": "Add `- **Modèle de monétisation**: <model>` to every §4 fiche"})
        return "WARN"
    n_distinct = sum(1 for m in fiches_with_model if m != _BASELINE_MODEL)
    ratio = n_distinct / total if total > 0 else 0.0
    if ratio < 0.60:
        findings.append({"check": "C3", "severity": "FAIL",
                         "title": f"Applicative diversity insufficient: {n_distinct}/{total} fiches have model ≠ baseline ({ratio*100:.0f}%, need ≥80%)",
                         "fix": f"Diversify monetization models: SDK_royalty, licence_IP, certification, NRE_runrate, service, abonnement. Baseline `{_BASELINE_MODEL}` must cover <20% of fiches."})
        return "FAIL"
    if ratio < 0.80:
        findings.append({"check": "C3", "severity": "WARN",
                         "title": f"Applicative diversity marginal: {ratio*100:.0f}% (≥80% recommended)",
                         "fix": "Review fiches with install_projet model and consider more diverse monetization approaches"})
        return "WARN"
    return "PASS"


# ============================================================
# C4 — EUR figures with explicit derivation in §6
# ============================================================
def _check_eur_figures(livrable: str, findings: list[dict]) -> str:
    sections = _split_sections(livrable)
    s6 = sections.get("§6", "")
    if not s6:
        return "WARN"  # already flagged by C1
    has_eur = bool(re.search(r"\d[\d\s]*(?:€|EUR|k€|M€|K€)", s6))
    has_derivation = bool(re.search(r"(?:×|x|\*)\s*\d+%|capture\s+rate|valeur\s+générée|économie\s+générée", s6, re.IGNORECASE))
    if not has_eur:
        findings.append({"check": "C4", "severity": "WARN",
                         "title": "§6 has no EUR pricing figures",
                         "fix": "Add explicit EUR price ranges to §6 using derivation formula: Value(EUR/year) × capture_rate% → pricing"})
        return "WARN"
    if has_eur and not has_derivation:
        findings.append({"check": "C4", "severity": "WARN",
                         "title": "§6 has EUR figures but no visible derivation formula",
                         "fix": "Show explicit derivation: `Value generated (EUR/year) × capture rate (10-30%) → price range`"})
        return "WARN"
    return "PASS"


# ============================================================
# C5a — Real sources (≥1 https:// or Internal: per §)
# ============================================================
def _check_real_sources(livrable: str, findings: list[dict]) -> str:
    sections = _split_sections(livrable)
    no_source = []
    for marker in ["§2", "§3", "§4", "§5", "§6"]:
        body = sections.get(marker, "")
        if body and not re.search(r"_Source:\s*\[https?://|_Source:\s*\[Internal:", body, re.IGNORECASE):
            no_source.append(marker)
    if no_source:
        findings.append({"check": "C5a", "severity": "WARN",
                         "title": f"Sections without real sources (_Source: [https://... or Internal:]): {', '.join(no_source)}",
                         "fix": "Add _Source: [URL accessed YYYY-MM-DD]_ or _Source: [Internal: <file>]_ for factual claims"})
        return "WARN"
    return "PASS"


# ============================================================
# C5b — Hypothesis / bypass patterns FORBIDDEN (P0-7)
# ============================================================
_FORBIDDEN_PATTERNS = [
    r"\[HYPOTHESIS[-_]NON[-_]SOURCED\]",
    r"\[HYPOTHESIS\]",
    r"\[HYPOTHESIS:",
    r"\[NON[-_]SOURCED\]",
    r"\[SOURCE[-_]PENDING\]",
    r"\[TBD\s+source\]",
    r"_Source:\s*\[General[-_]knowledge\]_",
    r"_Source:\s*\[À\s+sourcer\]",
    r"_Source:\s*\[À\s+valider\]",
    r"_Source:\s*\[A\s+sourcer\]",
    r"_Source:\s*\[A\s+valider\]",
]


def _check_hypotheses_ratio(livrable: str, findings: list[dict]) -> str:
    combined = "|".join(_FORBIDDEN_PATTERNS)
    matches = re.findall(combined, livrable, re.IGNORECASE)
    if matches:
        findings.append({"check": "C5b", "severity": "FAIL",
                         "title": f"{len(matches)} forbidden bypass pattern(s) found: {', '.join(set(matches[:3]))}",
                         "fix": "Remove ALL [HYPOTHESIS*], [NON-SOURCED], [SOURCE-PENDING], [TBD source] and similar patterns. If not sourceable → delete the claim."})
        return "FAIL"
    return "PASS"


# ============================================================
# C6 — Multi-channel: each Tier-1 fiche has ≥1 real source
# ============================================================
def _check_multi_channel(livrable: str, findings: list[dict]) -> str:
    sections = _split_sections(livrable)
    s4 = sections.get("§4", "")
    fiches = re.findall(r"###\s+#\d+[^#\n]*Tier.*?1[^#\n]*INDISPENSABLE[^#\n]*\n(.*?)(?=###|\Z)",
                        s4, re.DOTALL | re.IGNORECASE)
    no_source = []
    for i, body in enumerate(fiches):
        if not re.search(r"_Source:\s*\[https?://|_Source:\s*\[Internal:", body, re.IGNORECASE):
            no_source.append(f"#T1-{i+1}")
    if no_source:
        findings.append({"check": "C6", "severity": "WARN",
                         "title": f"Tier-1 fiche(s) without real source: {', '.join(no_source)}",
                         "fix": "Every Tier-1 fiche must have ≥1 _Source: [URL]_ or _Source: [Internal: <file>]_"})
        return "WARN"
    return "PASS"


# ============================================================
# C7 — Confidence anti-fraud: HIGH without source
# ============================================================
def _check_confidence_anti_fraud(livrable: str, findings: list[dict]) -> str:
    highs = list(re.finditer(r"\[CONFIDENCE:\s*HIGH\]", livrable, re.IGNORECASE))
    violations = []
    for m in highs:
        window = livrable[m.end():m.end() + 300]
        if not re.search(r"_Source:\s*\[https?://|_Source:\s*\[Internal:", window, re.IGNORECASE):
            violations.append(m.start())
    if violations:
        findings.append({"check": "C7", "severity": "FAIL",
                         "title": f"{len(violations)} [CONFIDENCE: HIGH] without immediate _Source: [URL]_ in following 300 chars",
                         "fix": "Every [CONFIDENCE: HIGH] must be immediately followed by _Source: [URL]_ or _Source: [Internal: <file>]_. Downgrade to MED/LOW or delete if not sourceable."})
        return "FAIL"
    return "PASS"


# ============================================================
# C8 — WebSearch count (≥15 total in sources.jsonl)
# ============================================================
def _check_websearch(run_dir: Path, livrable: str, findings: list[dict]) -> str:
    sources_path = run_dir / "sources.jsonl"
    process_sources = run_dir / "process-artifacts" / "sources.jsonl"
    entries: list[dict] = []
    for p in [sources_path, process_sources]:
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique = []
    for e in entries:
        url = e.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(e)
    count = len(unique)
    if count < 15:
        findings.append({"check": "C8", "severity": "WARN",
                         "title": f"WebSearch count insufficient: {count} unique sources in sources.jsonl (min 15)",
                         "fix": "Record all WebSearch results in <run>/sources.jsonl as JSONL: {\"phase\":\"...\",\"target\":\"...\",\"query\":\"...\",\"url\":\"...\",\"accessed\":\"...\",\"extract\":\"...\"}"})
        return "WARN"
    return "PASS"


# ============================================================
# C9 — 3 buckets covered in §3 or §4
# ============================================================
def _check_3_buckets(livrable: str, findings: list[dict]) -> str:
    text = livrable.lower()
    missing = []
    if not re.search(r"end.?user|final\s+client|client\s+final|utilisateur\s+final", text):
        missing.append("(a) end-users/final clients")
    if not re.search(r"int[ée]grateur|service\s+provider|prestataire", text):
        missing.append("(b) integrators/service providers")
    if not re.search(r"oem|[ée]diteur|sdk.*royalt|royalt.*sdk|software.*vendor", text):
        missing.append("(c) OEM/software editors")
    if missing:
        findings.append({"check": "C9", "severity": "WARN",
                         "title": f"3-bucket coverage incomplete: {', '.join(missing)}",
                         "fix": "Ensure §3/§4 covers all 3 buyer categories: end-users, integrators, OEM/software editors"})
        return "WARN"
    return "PASS"


# ============================================================
# C10 — Self-adversarial section in process-artifacts
# ============================================================
def _check_self_adversarial(run_dir: Path, livrable: str, findings: list[dict]) -> str:
    pa = run_dir / "process-artifacts"
    files = list(pa.glob("*")) if pa.exists() else []
    has_adversarial = any(re.search(r"adversar|auto.?criti|anti.?cible|gates.?log|self.?challenge",
                                    f.name, re.IGNORECASE) for f in files)
    # Also check if gates-log.md exists
    has_gates = (pa / "gates-log.md").exists() if pa.exists() else False
    if not has_adversarial and not has_gates:
        findings.append({"check": "C10", "severity": "WARN",
                         "title": "No adversarial/gates-log file in process-artifacts/",
                         "fix": "Write process-artifacts/gates-log.md with 6-gate application log per candidate"})
        return "WARN"
    return "PASS"


# ============================================================
# C11 — Multi-livrable: 3 split files present
# ============================================================
def _check_multi_livrables(run_dir: Path, findings: list[dict]) -> str:
    missing = []
    for fname in ["livrable-summary.md", "livrable-go-to-market.md", "livrable-technical-deep-dive.md"]:
        if not (run_dir / fname).exists():
            missing.append(fname)
    if missing:
        findings.append({"check": "C11", "severity": "WARN",
                         "title": f"Multi-livrable split incomplete: missing {', '.join(missing)}",
                         "fix": "Produce all 3 deliverable files: livrable-summary.md, livrable-go-to-market.md, livrable-technical-deep-dive.md"})
        return "WARN"
    return "PASS"


# ============================================================
# C12 — State checkpoint YAML present
# ============================================================
def _check_state_checkpoint(livrable: str, findings: list[dict]) -> str:
    if "STATE_CHECKPOINT" not in livrable and "steps_completed" not in livrable.lower():
        findings.append({"check": "C12", "severity": "WARN",
                         "title": "No STATE_CHECKPOINT or steps_completed marker found in livrable",
                         "fix": "Add frontmatter YAML with steps_completed field, updated after each phase"})
        return "WARN"
    return "PASS"


# ============================================================
# C13 — Bibliography present in deliverables
# ============================================================
def _check_bibliography(run_dir: Path, findings: list[dict]) -> str:
    for fname in ["livrable-go-to-market.md", "livrable-technical-deep-dive.md", "livrable.md"]:
        path = run_dir / fname
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if re.search(r"bibliograph|sources\s+consol", content, re.IGNORECASE):
                return "PASS"
    findings.append({"check": "C13", "severity": "WARN",
                     "title": "No bibliography/consolidated sources section found in deliverables",
                     "fix": "Add a 'Bibliographie (sources consolidées)' section with all cited URLs at the end of livrable.md or split deliverables"})
    return "WARN"


# ============================================================
# C14 — Brainstorm volume ≥75 candidates
# ============================================================
def _check_brainstorm_volume(run_dir: Path, findings: list[dict]) -> str:
    pa = run_dir / "process-artifacts"
    candidates_path = pa / "brainstorm-candidates.md"
    if not candidates_path.exists():
        findings.append({"check": "C14", "severity": "FAIL",
                         "title": "process-artifacts/brainstorm-candidates.md not found",
                         "fix": "Create brainstorm-candidates.md with ≥75 numbered candidates before any filtering"})
        return "FAIL"
    content = candidates_path.read_text(encoding="utf-8")
    # Count numbered entries
    count = len(re.findall(r"^\s*\d+[\.\)]\s+", content, re.MULTILINE))
    if count < 75:
        findings.append({"check": "C14", "severity": "FAIL",
                         "title": f"Brainstorm candidates count insufficient: {count} (min 75)",
                         "fix": "Produce ≥75 numbered candidates in brainstorm-candidates.md (≥15 per mode × 5 modes)"})
        return "FAIL"
    return "PASS"


# ============================================================
# C16 — Phase separator [C] ATTENTE OPÉRATEUR present ≥5 times
# ============================================================
def _check_separator(run_dir: Path, livrable: str, findings: list[dict]) -> str:
    pa = run_dir / "process-artifacts"
    log_path = pa / "process-log.md"
    search_text = livrable
    if log_path.exists():
        search_text += log_path.read_text(encoding="utf-8")
    count = len(re.findall(r"\[C\]\s+ATTENTE\s+OP[ÉE]RATEUR", search_text, re.IGNORECASE))
    if count < 5:
        findings.append({"check": "C16", "severity": "WARN",
                         "title": f"Only {count} phase separator(s) `[C] ATTENTE OPÉRATEUR` found (min 5 for 6-step workflow)",
                         "fix": "Write `--- [C] ATTENTE OPÉRATEUR — Phase N ... ---` at every phase transition, both in visible text and in process-artifacts/process-log.md"})
        return "WARN"
    return "PASS"


# ============================================================
# C17 — must_consider_targets covered in §4
# ============================================================
def _check_must_consider_coverage(livrable: str, must_consider: list[str],
                                   findings: list[dict]) -> str:
    if not must_consider:
        return "PASS"
    sections = _split_sections(livrable)
    s4 = sections.get("§4", livrable)
    missing = [t for t in must_consider if t.lower() not in s4.lower()]
    if missing:
        findings.append({"check": "C17", "severity": "FAIL",
                         "title": f"must_consider_targets not covered in §4: {', '.join(missing)}",
                         "fix": "Add explicit §4 fiche for each entity in must_consider_targets with Tier verdict"})
        return "FAIL"
    return "PASS"


# ============================================================
# C19 — Incumbent coverage for vertical tech
# ============================================================
def _check_incumbent_coverage(livrable: str, origin_sectors: list[str],
                               findings: list[dict]) -> str:
    if len(origin_sectors) < 3:
        return "PASS"  # not vertical
    # For vertical tech, §3/§4 must have a top-5 incumbents section
    if not re.search(r"incumbent|top\s*5|licens(?:eur|ors)|format\s+owner|standard\s+bod",
                     livrable, re.IGNORECASE):
        findings.append({"check": "C19", "severity": "FAIL",
                         "title": "Vertical technology detected (≥3 subsectors same domain) but no incumbent coverage section found",
                         "fix": "Add 'Top 5 incumbents/licensors' section in §3 or §4. Each incumbent must be classified Tier-2 long-cycle OR anti-target with ≥50-word justification."})
        return "FAIL"
    # Check ≥5 incumbents listed
    n_incumbents = len(re.findall(r"incumbent|licens(?:eur|or)\s+\d|format\s+owner\s+\d",
                                   livrable, re.IGNORECASE))
    if n_incumbents < 5:
        findings.append({"check": "C19", "severity": "WARN",
                         "title": f"Vertical technology: incumbent section present but fewer than 5 incumbents listed ({n_incumbents})",
                         "fix": "List ≥5 incumbents/licensors with Tier classification and ≥50-word justification each"})
        return "WARN"
    return "PASS"


# ============================================================
# C21 — Internal source fidelity: verbatim citations
# ============================================================
def _check_internal_source_fidelity(run_dir: Path, findings: list[dict]) -> str:
    livrable_path = run_dir / "livrable.md"
    if not livrable_path.exists():
        return "PASS"
    content = livrable_path.read_text(encoding="utf-8")
    # Find Internal: citations
    internal_refs = list(re.finditer(r"_Source:\s*\[Internal:\s*([^\]]+)\]_?", content, re.IGNORECASE))
    if not internal_refs:
        return "PASS"  # No internal sources, no check
    # Check each has verbatim quote within 350 chars
    violations = 0
    for m in internal_refs:
        window = content[m.end():m.end() + 350]
        # Look for > "..." or > '...' (verbatim quote)
        has_verbatim = bool(re.search(r'>\s*["“”][\w\s]{3,}["“”]', window))
        if not has_verbatim:
            violations += 1
    if violations > 0:
        ratio = violations / len(internal_refs)
        severity = "FAIL" if violations >= 3 else "WARN"
        findings.append({"check": "C21", "severity": severity,
                         "title": f"{violations}/{len(internal_refs)} Internal: source citations missing verbatim quote (> \"exact passage\") within 350 chars",
                         "fix": "After each _Source: [Internal: <file>]_ add: > \"exact verbatim passage from source\". Never paraphrase thresholds."})
        return severity
    return "PASS"


# ============================================================
# C22 — Tier-1 redundancy (same entity in multiple Tier-1 slots)
# ============================================================
def _check_tier1_redundancy(livrable: str, findings: list[dict]) -> str:
    sections = _split_sections(livrable)
    s4 = sections.get("§4", "")
    tier1_names = re.findall(r"###\s+#\d+[^#\n]*INDISPENSABLE[^#\n]*—\s+([^\n(]+)", s4, re.IGNORECASE)
    tier1_names = [n.strip().lower() for n in tier1_names]
    seen: dict[str, int] = {}
    for name in tier1_names:
        seen[name] = seen.get(name, 0) + 1
    duplicates = [k for k, v in seen.items() if v > 1]
    if duplicates:
        findings.append({"check": "C22", "severity": "WARN",
                         "title": f"Tier-1 redundancy detected: {', '.join(duplicates[:3])}",
                         "fix": "Each entity should appear only once as Tier-1. Merge or distinguish."})
        return "WARN"
    return "PASS"


# ============================================================
# C23 — Tier-1 tangibility: must name real entities
# ============================================================
_ARCHETYPE_SIGNALS = [
    r"\bfabricants?\b", r"\b[ée]diteurs?\b", r"\bint[ée]grateurs?\b",
    r"\bprestataires?\b", r"\bfournisseurs?\b", r"\bop[ée]rateurs?\b",
    r"\bstudios?\b(?!\s+\w+\s+\w)", r"\bmarqu(?:e|es)\b",
    r"\bsoci[ée]t[ée]s?\b", r"\bentreprises?\b", r"\bacteurs?\b",
]


def _check_tier1_tangibility(livrable: str, findings: list[dict]) -> str:
    sections = _split_sections(livrable)
    s4 = sections.get("§4", "")
    tier1_fiches = re.findall(
        r"(###\s+#\d+[^#\n]*INDISPENSABLE[^#\n]*\n.*?)(?=###\s+#|\Z)",
        s4, re.DOTALL | re.IGNORECASE,
    )
    if not tier1_fiches:
        return "PASS"  # C1/C26 will catch missing fiches

    abstract_fiches = []
    for fiche in tier1_fiches:
        # Extract fiche header (first line)
        header = fiche.split("\n")[0]
        # Check for known archetype-only patterns (no real named entity)
        is_archetype_only = any(re.search(p, header, re.IGNORECASE) for p in _ARCHETYPE_SIGNALS)
        # If header contains a capitalized proper noun beyond generic terms → real entity
        has_real_entity = bool(re.search(r"\b[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][a-zàâäéèêëîïôöùûü]{2,}\b", header))
        if is_archetype_only and not has_real_entity:
            abstract_fiches.append(header.strip()[:60])

    if abstract_fiches:
        findings.append({"check": "C23", "severity": "FAIL",
                         "title": f"Tier-1 fiche(s) name abstract market category instead of real entity: {'; '.join(abstract_fiches[:3])}",
                         "fix": "Each Tier-1 fiche MUST name ≥1 real entity (derived by WebSearch, not copied from prompt examples) in the fiche header or body. Abstract categories (e.g. 'integrators', 'manufacturers') are FORBIDDEN as Tier-1."})
        return "FAIL"
    return "PASS"


# ============================================================
# C24 — Tier-1 FTO contradiction
# ============================================================
def _check_tier1_fto_contradiction(livrable: str, findings: list[dict]) -> str:
    sections = _split_sections(livrable)
    s4 = sections.get("§4", "") + sections.get("§5", "")
    tier1_fiches = re.findall(
        r"###\s+#\d+[^#\n]*INDISPENSABLE[^#\n]*\n(.*?)(?=###\s+#|\Z)",
        s4, re.DOTALL | re.IGNORECASE,
    )
    contradictions = []
    for i, body in enumerate(tier1_fiches):
        has_reimpl = bool(re.search(r"r[ée]-impl[ée]ment|ré-implement|can reimpl|peut reimpl", body, re.IGNORECASE))
        has_fto = bool(re.search(r"FTO\s+non\s+lev[ée]e|FTO\s+not\s+clear|brevet\s+bloquant", body, re.IGNORECASE))
        if has_reimpl or has_fto:
            contradictions.append(f"T1-fiche-{i+1}")
    if contradictions:
        findings.append({"check": "C24", "severity": "WARN",
                         "title": f"Tier-1 fiche(s) contain FTO/re-implementation contradiction signal: {', '.join(contradictions)}",
                         "fix": "If target can re-implement OR FTO not cleared → must downgrade to Tier-2 'FTO-first'. A Tier-1 entity that can self-implement is a logical contradiction."})
        return "WARN"
    return "PASS"


# ============================================================
# C25 — Differentiator vs named competitor (WARN-only, Flag #3)
# ============================================================
def _check_differentiator_vs_competitor(livrable: str, direct_competitors: list[str],
                                         findings: list[dict]) -> str:
    if not direct_competitors:
        return "PASS"
    sections = _split_sections(livrable)
    s2 = sections.get("§2", "")
    # §2 should articulate differentiator vs at least one named competitor
    articulated = any(c.lower() in s2.lower() for c in direct_competitors)
    if not articulated:
        findings.append({"check": "C25", "severity": "WARN",
                         "title": f"§2 does not explicitly articulate differentiator vs known competitor(s): {', '.join(direct_competitors[:3])}",
                         "fix": "In §2, name ≥1 direct competitor and articulate the precise differentiator (NOT a metric the competitor already equals). Source the competitor's capability with a real URL."})
        return "WARN"
    return "PASS"


# ============================================================
# C26 — Tier-1 TRIPLET: (1)+(2)+(3) in every Tier-1 fiche
# ============================================================
def _check_tier1_triplet(livrable: str, findings: list[dict]) -> str:
    sections = _split_sections(livrable)
    s4 = sections.get("§4", "")
    tier1_fiches = re.findall(
        r"(###\s+#\d+[^#\n]*INDISPENSABLE[^#\n]*\n.*?)(?=###\s+#|\Z)",
        s4, re.DOTALL | re.IGNORECASE,
    )
    if not tier1_fiches:
        return "PASS"

    incomplete = []
    for i, fiche in enumerate(tier1_fiches):
        header = fiche.split("\n")[0].strip()
        has_1 = bool(re.search(r"\(1\)\s*(?:POURQUOI|WHY)|pourquoi\s+cette\s+cible", fiche, re.IGNORECASE))
        has_2 = bool(re.search(r"\(2\)\s*(?:USE.CASES?|CAS\s+D.USAGE)", fiche, re.IGNORECASE))
        has_3 = bool(re.search(r"\(3\)\s*(?:BESOINS?|IDENTIFIED\s+NEEDS?|NEEDS?\s+IDENTIF)", fiche, re.IGNORECASE))
        if not (has_1 and has_2 and has_3):
            missing_parts = []
            if not has_1: missing_parts.append("(1)WHY")
            if not has_2: missing_parts.append("(2)USE-CASES")
            if not has_3: missing_parts.append("(3)NEEDS")
            incomplete.append(f"{header[:40]} missing {', '.join(missing_parts)}")

    if incomplete:
        findings.append({"check": "C26", "severity": "FAIL",
                         "title": f"Tier-1 fiche(s) missing TRIPLET elements: {'; '.join(incomplete[:3])}",
                         "fix": "Every Tier-1 fiche must carry all 3 TRIPLET sub-fields: (1) POURQUOI / WHY, (2) USE-CASES concrets, (3) BESOINS / IDENTIFIED NEEDS — each with _Source: [URL]_"})
        return "FAIL"
    return "PASS"


# ============================================================
# C27 — IP/TAM/Competitive analysis present and sourced (NEW)
# ============================================================
def _check_ip_tam_competitive(run_dir: Path, livrable: str, findings: list[dict]) -> str:
    """C27: §5 or process-artifacts must contain IP analysis (patent registry search)
    and TAM/competitive data with sources."""
    sections = _split_sections(livrable)
    s5 = sections.get("§5", "")
    pa = run_dir / "process-artifacts"

    # Check 1: IP analysis evidence (patent registry keywords)
    patent_registries = r"Espacenet|Google\s+Patents|USPTO|WIPO|INPI|epo\.org|patentscope\.wipo"
    has_ip_in_s5 = bool(re.search(patent_registries, s5, re.IGNORECASE))
    has_ip_in_pa = False
    if pa.exists():
        ip_file = pa / "ip-analysis.md"
        if ip_file.exists():
            has_ip_in_pa = bool(re.search(patent_registries, ip_file.read_text(encoding="utf-8"), re.IGNORECASE))

    if not has_ip_in_s5 and not has_ip_in_pa:
        findings.append({"check": "C27", "severity": "FAIL",
                         "title": "No patent registry search evidence in §5 or process-artifacts/ip-analysis.md",
                         "fix": "In Phase 3 (step-04-deep-dive.md), search patent registries (Espacenet, Google Patents, USPTO, WIPO, INPI) for each Tier-1 target. Document results in process-artifacts/ip-analysis.md and reference in §5."})
        return "FAIL"

    # Check 2: TAM figures with sources
    has_tam = bool(re.search(r"\bTAM\b|\bSAM\b|total\s+addressable|march[ée]\s+adressable", s5, re.IGNORECASE))
    has_tam_source = bool(re.search(r"\bTAM\b.*?_Source:|_Source:.*?\bTAM\b|Statista|Strategy\s+Analytics|IDC|Gartner", s5, re.IGNORECASE | re.DOTALL))

    if not has_tam:
        findings.append({"check": "C27", "severity": "WARN",
                         "title": "§5 has no TAM/SAM estimate",
                         "fix": "Add TAM/SAM estimates for each Tier-1 target in §5, with _Source: [URL]_. Suppress if not sourceable (do not invent)."})
        return "WARN"

    if has_tam and not has_tam_source:
        findings.append({"check": "C27", "severity": "WARN",
                         "title": "§5 has TAM figures but no visible source for market sizing",
                         "fix": "Source TAM figures with analyst reports or trade press: _Source: [https://statista.com/... accessed YYYY-MM-DD]_"})
        return "WARN"

    return "PASS"


# ============================================================
# C28 — Cross-agent technical validation traced (NEW)
# ============================================================
def _check_cross_validation_traced(run_dir: Path, livrable: str, findings: list[dict]) -> str:
    """C28: process-artifacts/cross-validation.md must exist and contain
    per-Tier-1-target validation traces with verdict."""
    pa = run_dir / "process-artifacts"
    cv_path = pa / "cross-validation.md" if pa.exists() else None

    if cv_path is None or not cv_path.exists():
        findings.append({"check": "C28", "severity": "FAIL",
                         "title": "process-artifacts/cross-validation.md not found",
                         "fix": "In Phase 3 (step-04-deep-dive.md), for each Tier-1 target: spawn a technical-validator agent (or run devil's-advocate pass) and write the validation trace to process-artifacts/cross-validation.md. Include: method (agent-spawn|devil-advocate-pass), per-axis verdict (PASS/WARN/FAIL), final verdict (ACCEPTED_AS_TIER1|DOWNGRADED)."})
        return "FAIL"

    cv_content = cv_path.read_text(encoding="utf-8")

    # Check for validation structure (per-target sections with verdicts)
    has_method = bool(re.search(r"method\s*[:=]|agent.?spawn|devil.?advocate", cv_content, re.IGNORECASE))
    has_verdict = bool(re.search(r"ACCEPTED_AS_TIER1|DOWNGRADED|verdict\s*[:=]", cv_content, re.IGNORECASE))
    has_axes = bool(re.search(r"Axis\s+[1-6]|Axe\s+[1-6]|\(PASS\)|\(WARN\)|\(FAIL\)", cv_content, re.IGNORECASE))

    if not has_method:
        findings.append({"check": "C28", "severity": "WARN",
                         "title": "cross-validation.md exists but missing method declaration (agent-spawn or devil-advocate-pass)",
                         "fix": "Add `**Method**: agent-spawn | devil-advocate-pass` to each target section in cross-validation.md"})
        return "WARN"

    if not has_verdict:
        findings.append({"check": "C28", "severity": "WARN",
                         "title": "cross-validation.md exists but missing final verdict per target (ACCEPTED_AS_TIER1 or DOWNGRADED_TO_TIER2)",
                         "fix": "Add `**Verdict**: ACCEPTED_AS_TIER1 | DOWNGRADED_TO_TIER2 | NEEDS_REVISION` for each target in cross-validation.md"})
        return "WARN"

    if not has_axes:
        findings.append({"check": "C28", "severity": "WARN",
                         "title": "cross-validation.md does not show per-axis (1-6) validation verdict",
                         "fix": "Document validation for each of the 6 axes: `- Axis N: [PASS/WARN/FAIL] — [note]`"})
        return "WARN"

    return "PASS"


# ============================================================
# Helpers
# ============================================================
def _extract_actions(findings: list[dict], max_actions: int = 3) -> list[str]:
    severity_order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    sorted_findings = sorted(findings, key=lambda f: severity_order.get(f.get("severity", "PASS"), 2))
    return [f.get("fix", "") for f in sorted_findings[:max_actions] if f.get("fix")]


# ============================================================
# Main
# ============================================================
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PROVE (bmad-prove) audit — 28 checks (C1-C26 + C27 ip_tam + C28 cross_validation)"
    )
    parser.add_argument("--run", required=True,
                        help="Path to the PROVE output directory")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress stdout JSON, only write audit.json")
    args = parser.parse_args(argv)

    run_dir = Path(args.run).resolve()
    if not run_dir.exists() or not run_dir.is_dir():
        print(json.dumps({"error": f"Run directory not found: {run_dir}"}, indent=2))
        return 2

    livrable_path = run_dir / "livrable.md"
    intake_path = run_dir / "intake.v5.yaml"

    if not livrable_path.exists():
        print(json.dumps({"error": f"livrable.md missing in {run_dir}"}, indent=2))
        return 2

    livrable = livrable_path.read_text(encoding="utf-8")
    intake_text = intake_path.read_text(encoding="utf-8") if intake_path.exists() else ""

    origin_sectors = _extract_origin_sectors(intake_text)
    existing_use_case = _extract_existing_use_case(intake_text)
    must_consider = _extract_must_consider_targets(intake_text)
    market_posture = _extract_market_posture(intake_text)
    direct_competitors = _extract_direct_competitors(intake_text)

    findings: list[dict] = []
    check_results = {
        "C1_structure": _check_structure(livrable, findings),
        "C2_three_questions": _check_three_questions(livrable, findings),
        "C3_applicative_diversity": _check_applicative_diversity(
            livrable, existing_use_case, origin_sectors, findings, market_posture=market_posture),
        "C4_eur_figures": _check_eur_figures(livrable, findings),
        "C5a_real_sources": _check_real_sources(livrable, findings),
        "C5b_hypotheses_ratio": _check_hypotheses_ratio(livrable, findings),
        "C6_multi_channel": _check_multi_channel(livrable, findings),
        "C7_confidence_anti_fraud": _check_confidence_anti_fraud(livrable, findings),
        "C8_websearch_count": _check_websearch(run_dir, livrable, findings),
        "C9_3_buckets": _check_3_buckets(livrable, findings),
        "C10_self_adversarial": _check_self_adversarial(run_dir, livrable, findings),
        "C11_multi_livrables": _check_multi_livrables(run_dir, findings),
        "C12_state_checkpoint": _check_state_checkpoint(livrable, findings),
        "C13_bibliography": _check_bibliography(run_dir, findings),
        "C14_brainstorm_volume": _check_brainstorm_volume(run_dir, findings),
        "C16_separator": _check_separator(run_dir, livrable, findings),
        "C17_must_consider": _check_must_consider_coverage(livrable, must_consider, findings),
        "C19_incumbent_coverage": _check_incumbent_coverage(livrable, origin_sectors, findings),
        "C21_internal_source_fidelity": _check_internal_source_fidelity(run_dir, findings),
        "C22_tier1_redundancy": _check_tier1_redundancy(livrable, findings),
        "C23_tier1_tangibility": _check_tier1_tangibility(livrable, findings),
        "C24_tier1_fto_contradiction": _check_tier1_fto_contradiction(livrable, findings),
        "C25_differentiator_vs_competitor": _check_differentiator_vs_competitor(
            livrable, direct_competitors, findings),
        "C26_tier1_triplet": _check_tier1_triplet(livrable, findings),
        # New checks (bmad-prove specific)
        "C27_ip_tam_competitive": _check_ip_tam_competitive(run_dir, livrable, findings),
        "C28_cross_validation_traced": _check_cross_validation_traced(run_dir, livrable, findings),
    }

    if any(v == "FAIL" for v in check_results.values()):
        verdict = "FAIL"
    elif any(v == "WARN" for v in check_results.values()):
        verdict = "WARN"
    else:
        verdict = "PASS"

    actions = _extract_actions(findings, max_actions=3)
    livrable_sha256 = hashlib.sha256(livrable.encode("utf-8")).hexdigest()

    report = {
        "tool": "audit.py",
        "skill": "bmad-prove",
        "prove_version": "bmad-prove-1.0.0",
        "session_id": _extract_session_id(intake_text) or run_dir.name,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "existing_clients_subsectors_detected": origin_sectors or ["unknown"],
        "existing_use_case_detected": existing_use_case or "",
        "must_consider_targets_detected": must_consider or [],
        "market_posture": market_posture,
        "verdict": verdict,
        "checks": check_results,
        "corrective_actions": actions,
        "findings": findings,
        "livrable_sha256": livrable_sha256,
        "livrable_size_chars": len(livrable),
    }

    out_path = run_dir / "audit.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if not args.quiet:
        summary = {
            "verdict": verdict,
            "market_posture": market_posture,
            "checks": check_results,
            "actions": actions,
            "audit_report": str(out_path),
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    return 0 if verdict != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
