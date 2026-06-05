# PROVE Step 3: Market Mapping (Phase 2 — market-analyst)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER use target names from prompt examples — derive ALL targets by WebSearch + reasoning
- ✅ ALWAYS produce ≥75 brainstorm candidates BEFORE any filtering
- 📋 YOU ARE THE market-analyst — multi-sector, friction-first reasoning (not sector-first)
- 💬 FOCUS on the pivot question from Phase 1: "Who else needs to reduce friction X?"
- 🔍 WebSearch min ≥15: ≥1 per retained segment, mandatory for Tier-1 candidates
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Run 5 generative modes in parallel → ≥75 brainstorm candidates
- ⚠️ Apply 3-bucket gate and 6 logical gates before scoring
- 💾 Write brainstorm-candidates.md IMMEDIATELY after generative phase
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3]` before loading next step
- 🚫 FORBIDDEN to load next step until [C] is selected after presenting 15 target fiches

## CONTEXT BOUNDARIES:

- §2 Profil technique exploitable (brick_name, friction, pivot question) is available
- `identity.existing_clients_subsectors`, `existing_use_case`, `market_posture`, `must_consider_targets` are loaded
- `known_facts.excluded_sectors`, `excluded_targets`, `direct_competitors` are loaded
- WebSearch capabilities are ENABLED

## YOUR TASK:

Phase 2a → Phase 2b → Phase 2c → 15 target fiches → §3 + §4.

---

## PHASE 2a — BRAINSTORM GÉNÉRATIF 5 MODES

Produce ≥75 brainstorm candidates using all 5 modes in parallel. Write results IMMEDIATELY to `{{prove_run_dir}}/process-artifacts/brainstorm-candidates.md` as a numbered list (≥1 line per candidate: number, name, source mode, 1-line justification).

**Mode 1 — INVERSION**: "Where does friction X (from pivot question) reach a DISPROPORTIONATE cost or delay — by order of magnitude (10×, 100×, 1000×)?" Force reasoning by magnitude of effect, not sector membership.

**Mode 2 — TRANSVERSAL ANALOGY**: "Our technology processes `<objects X>` in a given context. Where are objects processed that are NOT X but share the same dual algorithm?" Transpose the principle toward other signal natures/objects: other waves, other sensors, other media.

**Mode 3 — ABSURD CHALLENGE**: "Give 10 sectors where the technology is OBJECTIVELY USELESS and explain why." Often reveals sectors where it's subtly useful in another form.

**Mode 4 — 3-YEAR PROSPECTIVE**: "Which sectors will STRUCTURALLY need this in 3 years due to regulatory/tech trends?" (new regulations, electrification, robotics, AI, etc. — adapt to the technology domain).

**Mode 5 — WHO OWNS THE FORMAT**: Search for the real entities that own the standards/formats/certifications/patents of the domain. Minimum 8-12 real named candidates (sourced by WebSearch). Search: "standard bodies [domain]", "format licensors [domain]", "patent holders [technology type]".

**Minimum per mode**: ≥15 candidates each (5 × 15 = 75 minimum total).

After brainstorm, record WebSearch results in `{{prove_run_dir}}/sources.jsonl`.

---

## PHASE 2b — GATE 3 BUCKETS (MANDATORY)

Before scoring, confirm your ≥75 candidates explicitly cover ALL 3 buckets:

- **(a) End-users / final clients** (who pays the recurring usage licence)
- **(b) Integrators / service providers** (who pays a pro tool to serve their own clients)
- **(c) Software editors / OEM** (who integrates via SDK/royalty and distributes in their ecosystem)

If any bucket is empty → invoke AskUserQuestion: "Give me your intuition of representative actors for this bucket before I dig further."

---

## PHASE 2c — SCORING + 6 LOGICAL GATES

For each candidate, apply ALL 6 gates BEFORE scoring. Log each gate decision (1 line per candidate × 6 gates) in `{{prove_run_dir}}/process-artifacts/gates-log.md`.

**Gate 1 — COMPLETE DIFFERENTIATING CAPACITY**: Does this target exercise the COMPLETE differentiating capacity of the technology, or only a DEGRADED/partial/trivial version? If degraded → Tier-3 or excluded with explicit mention.

**Gate 2 — USAGE FREQUENCY (Mary)**: How many times per year does the target recalibrate/redeploy/iterate? 1× = one-shot non-profitable → Tier-3 or excluded (unless NRE > 200 k€ explicitly stated).

**Gate 3 — VISIBLE ALTERNATIVE COST (Mary)**: Does the cost of the current alternative appear in the target's P&L, or is it hidden in internal technician salaries? If invisible → no external purchase → Tier-3 or excluded.

**Gate 4 — BUYER EXISTS (Mary)**: Who in the organization has the signature budget (50-500 k€) without Board approval? If nobody → cycle ≥18 months → flag "long cycle, incompatible with 3-month hunt".

**Gate 5 — INTERNAL R&D + IP ASYMMETRY (Mary) — FORCED-DOWNGRADE**: Does the target have a larger R&D team + core competence on the subject AND a massive legal department making contract negotiation structurally unbalanced? If yes → flag "FTO-first mandatory". **HARD RULE**: if a Tier-1 candidate (a) has R&D capable of re-implementing the technology OR (b) FTO is not cleared (blocking adjacent patent not bypassed) → MUST be downgraded to Tier-2 "FTO-first". Log reason in gates-log.md.

**Gate 6 — INCUMBENT COVERAGE**: If technology is vertical (≥3 subsectors from same domain in `existing_clients_subsectors`), the top 5 incumbents/licensors of the sector MUST be listed and classified as Tier-2 long-cycle OR anti-target, with ≥50-word justification each. No silent kill allowed.

**Scoring axes** (after gates pass): 
- Latent size (1=niche / 2=mid / 3=large)
- Urgency of need (1=nice-to-have / 2=real pain / 3=blocking)
- Commercial accessibility (1=closed/captive / 2=intermediated / 3=open)
- Score = sum (3-9)

---

## PRODUCTION OF 15 TARGET FICHES

**MARKET POSTURE** from `identity.market_posture`:
- `vertical`: diversity of MONETIZATION MODELS within the ecosystem (not forced cross-market). No ecosystem concentration penalty.
- `horizontal`: push explicitly toward distinct markets. Ecosystem concentration = WARN.
- `auto` (default): historical behavior — ecosystem concentration WARN (non-blocking).

**APPLICATIVE DIVERSITY RULE (≥80%)**: ≥12 of the 15 fiches must have a USE CASE APPLICATIF different from `identity.existing_use_case`. A use case = (who buys) × (for what) × (business model). The `Modèle de monétisation` field (structured) must differ from the baseline.

**must_consider_targets**: each entity in `identity.must_consider_targets` MUST appear as an explicit fiche with Tier-1/2/3/anti-target verdict.

For each of the 15 retained segments, produce ONE target fiche (≤220 words net, excluding source tags):

```
### #N — <Real entity name (derived by WebSearch) or archetype>
- **Tier**: 1 (INDISPENSABLE) / 2 (STRONG INTEREST) / 3 (OPPORTUNISTIC)
- **Family**: A (recurring final clients) / B (OEM editors) / A+B
- **Modèle de monétisation**: <SDK_royalty | licence_IP | certification | service | kit_vente | NRE_runrate | install_projet | abonnement>
- **Complete differentiating capacity?**:
  - **YES**: 2-3 sentences (≥30 words) sourced, proving complete capacity exercise. _Source: [URL YYYY-MM-DD or Internal: <file>]_
  - **NO**: Target DEGRADED Tier-3 MANDATORY — "degraded/partial capacity, does not justify the technology"
  - **PARTIAL**: Justified — specify which sub-segment exercises full capacity
- **Usage frequency**: Recurring N×/year / One-shot [downgrade]
- **(1) WHY this target needs the technology**: ≤80 words, NON-INTERCHANGEABLE (if you can replace the name with another entity without changing the text → too generic, rewrite). _Source: [URL]_
- **(2) CONCRETE USE-CASES**: 2-3 precise cases where the technology inserts in THEIR real workflow. _Source: [URL]_
- **(3) IDENTIFIED NEEDS**: concrete gaps filled (quantified if possible: time/EUR/quality). _Source: [URL]_
- **Current alternative**: specific product/service name (real, sourced). _Source: [URL]_
- **Trigger event**: regulation/product cycle/named event. _Source: [URL or conference name + date]_ or [TRIGGER-UNCERTAIN]
```

**🔒 TIER-1 REQUIRES REAL NAMED ENTITY**: Any Tier-1 (INDISPENSABLE) target MUST name ≥1 real entity (derived by WebSearch, NOT copied from prompt examples) in the fiche name OR body. An abstract market category is FORBIDDEN as Tier-1. A grouping that ENUMERATES real named entities is accepted (e.g. "integrators immersive live: <Company-A>, <Company-B>, <Company-C>").

**Buyer designation**: by FUNCTION (e.g. "technical director", "VP engineering", "studio manager") — NEVER a person's name.

---

## WRITE §3 AND §4

After 15 fiches, write to `{{prove_run_dir}}/livrable.md`:
- **§3. Cartographie marchés** (300-500 words net): sector map, Tier distribution, market posture note, incumbent section (if vertical tech), bucket coverage
- **§4. Top 10-15 cibles** (15 fiches, ≤220 words net each)

Record all WebSearch results in `{{prove_run_dir}}/sources.jsonl`.

Write phase separator as visible text AND in process-log.md:
```
--- [C] ATTENTE OPÉRATEUR — Phase 2 §3+§4 prêts — Valide ou Reformule ---
```

Then HALT and present:
"I've completed **Phase 2: Market Mapping** for **{{brick_name}}**.

**Summary:**
- {{N}} brainstorm candidates generated (≥75 required)
- 6 gates applied → {{N}} candidates eliminated or downgraded
- 15 target fiches produced (Tier-1: {{N}}, Tier-2: {{N}}, Tier-3: {{N}})
- {{N}} WebSearch executed

**Please review §3 and §4. Which 3-5 Tier-1 targets do you want me to deep-dive in Phase 3?**
[C] Continue — specify your 3-5 Tier-1 targets for deep dive
[Modify] Request changes to market mapping

**HALT — wait for user response before proceeding.**"

---

## SUCCESS METRICS:

✅ ≥75 brainstorm candidates produced and written to brainstorm-candidates.md
✅ Minimum 5 modes used (INVERSION/ANALOGY/ABSURD/PROSPECTIVE/FORMAT_OWNERS)
✅ 3-bucket gate confirmed (end-users, integrators, OEM editors)
✅ All 6 logical gates applied and logged in gates-log.md
✅ 15 target fiches produced (≤220 words net each)
✅ ≥12/15 fiches with Modèle de monétisation ≠ existing_use_case baseline
✅ All Tier-1 fiches name real entities (derived by WebSearch)
✅ All Tier-1 fiches carry complete TRIPLET (1)+(2)+(3) with sources
✅ must_consider_targets all covered
✅ FTO-first downgrade applied when applicable (Gate 5)
✅ Incumbent coverage section present if vertical tech (Gate 6)
✅ ≥15 WebSearch executed and recorded in sources.jsonl
✅ Phase separator written in process-log.md

## FAILURE MODES:

❌ <75 brainstorm candidates (quota not met — audit C14)
❌ Tier-1 fiche without real named entity (audit C23 FAIL)
❌ Tier-1 fiche missing TRIPLET or partial TRIPLET (audit C26 FAIL)
❌ Modèle de monétisation field missing from fiches (audit C3 FAIL)
❌ Abstract market category as Tier-1 target (audit C23 FAIL)
❌ Gates not applied or not logged in gates-log.md
❌ FTO-first downgrade skipped for a Tier-1 that can re-implement (audit C24 WARN)
❌ Incumbent coverage section absent for vertical tech (audit C19 FAIL)
❌ <15 WebSearch executed (audit C8 WARN)
❌ Sources not recorded in sources.jsonl

## NEXT STEP:

After [C] confirmation with user-selected Tier-1 targets, load `./step-04-deep-dive.md` to begin Phase 3: Tier-1 deep dive with TRIPLET, IP/TAM, and cross-agent technical validation.
