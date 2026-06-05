# PROVE Step 6: Completion (Phase 5 — Assembly + §1 + Audit + Multi-livrable)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER skip the audit run — it is mandatory before declaring completion
- ✅ ALWAYS write §1 Synthèse exécutive as the LAST section (after all others are finalized)
- 📋 YOU ARE the orchestrator — final assembly and quality gate
- 💬 FOCUS on: §1 synthesis, multi-livrable split, audit run, corrections if needed
- 🔍 No mandatory WebSearch in this phase (research is complete)
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Write §1, run audit, correct FAIL findings, present final deliverable
- ⚠️ Present [C] complete option only after audit passes (PASS or WARN-only)
- 💾 ONLY complete workflow when user selects [C]
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4, 5, 6]` on final completion
- 🚫 FORBIDDEN to complete without running audit.py

## CONTEXT BOUNDARIES:

- §2 through §7 are written in livrable.md
- All sources recorded in sources.jsonl
- process-artifacts/ contains: process-log.md, brainstorm-candidates.md, gates-log.md, cross-validation.md, ip-analysis.md
- `{{prove_run_dir}}` is the output directory

## YOUR TASK:

Write §1, run audit.py (28 checks), fix FAIL findings, produce the 3-deliverable split, present final output.

---

## PHASE 5 SEQUENCE:

### 1. Write §1. Synthèse exécutive (LAST section written)

Write **§1. Synthèse exécutive** (200-350 words net) to `{{prove_run_dir}}/livrable.md`, replacing the `[Executive summary will be written here]` placeholder:

```markdown
## §1. Synthèse exécutive

**Technology**: {{brick_name}} [version if known]
**Date**: {{date}}
**Run ID**: {{prove_slug}}-{{date}}

### Verdict de qualification
[3-4 sentences: what the technology is, who it indispensably serves, what its key differentiator is]

### Top cibles INDISPENSABLE
[Numbered list of Tier-1 targets with 1-line "why indispensable" per target]

### Revenu potentiel estimé
[Conservative/base range in EUR/year, explicitly flagged as estimate, source: §6]

### 3 décisions à prendre
1. [Decision 1 — strategic / IP / commercial]
2. [Decision 2]
3. [Decision 3]

### Prochaine étape recommandée
[Specific action: which target to approach first, via what channel, what trigger to watch]
```

### 2. Write Consolidated Bibliography

At the end of `{{prove_run_dir}}/livrable.md`, append a bibliography section (deduplicated list of all URLs cited):

```markdown
---

## Bibliographie (sources consolidées)

[Deduplicated list of all https:// URLs cited in §1-§7, one per line]
```

### 3. Run Audit

Run the audit tool:
```bash
python3 {skill-root}/tools/audit.py --run {{prove_run_dir}}
```

If the script is not executable, run:
```bash
python3 "{skill-root}/tools/audit.py" --run "{{prove_run_dir}}"
```

**Read the audit output carefully**:
- PASS: proceed to multi-livrable split
- WARN: note the warnings, proceed (WARN does not block)
- FAIL: fix ALL FAIL findings before proceeding

**Common FAIL fixes**:
- C1 (structure): add missing section or trim overlong section
- C5b (hypotheses): find and remove all `[HYPOTHESIS-NON-SOURCED]` / `[HYPOTHESIS]` / `[SOURCE-PENDING]` occurrences
- C8 (websearch): verify sources.jsonl has ≥15 + ≥3/target entries
- C14 (brainstorm): verify brainstorm-candidates.md has ≥75 numbered entries
- C23 (tier1 tangibility): ensure all Tier-1 fiches name a real entity
- C26 (tier1 triplet): ensure all Tier-1 fiches carry (1)+(2)+(3) TRIPLET with sources
- C27 (ip_tam): ensure §5 contains patent registry search results and TAM figures for each Tier-1
- C28 (cross_validation): ensure process-artifacts/cross-validation.md exists with traces for each Tier-1

After any FAIL fix, re-run audit until clean.

### 4. Produce 3-Livrable Split

After audit PASS/WARN, produce the 3 separate deliverable files:

**`{{prove_run_dir}}/livrable-summary.md`** (≤500 words):
```markdown
---
type: prove-summary
brick_name: {{brick_name}}
date: {{date}}
prove_lite_version: "1.0.0"
---
# PROVE — {{brick_name}} — Summary (Board)

## TL;DR
[3 bullets: what it is, who it indispensably serves, what the deal looks like]

## Top Tier-1 Targets
[Numbered list: entity name + 1-line INDISPENSABLE reason]

## Revenue Potential
[Conservative/base estimate in EUR/year]

## 3 Decisions to Make
1. [Decision 1]
2. [Decision 2]
3. [Decision 3]
```

**`{{prove_run_dir}}/livrable-go-to-market.md`** (~3000 words):
Includes: §1 summary, §3 sector map, §4 target fiches (all 15), §6 monetization plan.
Full bibliography at the end.

**`{{prove_run_dir}}/livrable-technical-deep-dive.md`** (~3000 words):
Includes: §2 technical profile, §5 Tier-1 deep dive (6-axis + IP/TAM + validation), §7 anti-targets.
Full bibliography at the end.

Each file must have the YAML frontmatter:
```yaml
---
type: prove-[summary|go-to-market|technical-deep-dive]
brick_name: {{brick_name}}
date: {{date}}
prove_lite_version: "1.0.0"
session_id: {{prove_slug}}-{{date}}
---
```

### 5. Run URL Verification (optional but recommended)

```bash
python3 {skill-root}/tools/verify_urls.py --run {{prove_run_dir}}
```

Report result: if FAIL (≥1 confirmed 404/410/5xx), replace or remove the broken URL in the deliverable.

### 6. Final Phase Separator + Completion

Write as visible text AND in process-log.md:
```
--- [C] ATTENTE OPÉRATEUR — Phase 5 Complet — Valide ou Reformule ---
```

Present final summary:
"I've completed **PROVE qualification for {{brick_name}}**.

**Deliverables produced in `{{prove_run_dir}}/`:**
- `livrable.md` — consolidated deliverable (audit entry point)
- `livrable-summary.md` — board-level TL;DR (≤500 words)
- `livrable-go-to-market.md` — commercial kit (~3000 words)
- `livrable-technical-deep-dive.md` — R&D/IP/legal dossier (~3000 words)

**Process artifacts in `{{prove_run_dir}}/process-artifacts/`:**
- `process-log.md`, `brainstorm-candidates.md`, `gates-log.md`, `cross-validation.md`, `ip-analysis.md`

**Audit result:** [PASS | WARN — {N warnings}]

**Top Tier-1 targets identified**: [list]

**Recommended next step**: [specific action from §1]

[C] Complete — mark PROVE run as complete
[Modify] Request any last changes

**HALT — wait for user response before completing.**"

### 7. Handle Completion

#### If [C] (Complete):
- Update frontmatter: `stepsCompleted: [1, 2, 3, 4, 5, 6]`
- Run: `python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow.on_complete`
- If `workflow.on_complete` is non-empty, follow it as the final terminal instruction.

## SUCCESS METRICS:

✅ §1 Synthèse exécutive written (200-350 words net) with 3 decisions
✅ Consolidated bibliography appended to livrable.md
✅ audit.py run and result documented
✅ All FAIL findings fixed (WARN acceptable)
✅ 3-livrable split produced (summary + go-to-market + technical-deep-dive)
✅ Each split file has proper YAML frontmatter
✅ URL verification run (optional but recommended)
✅ Phase separator written in process-log.md
✅ Frontmatter stepsCompleted updated to [1, 2, 3, 4, 5, 6]

## FAILURE MODES:

❌ Skipping audit.py run
❌ Completing with FAIL findings unresolved
❌ Missing 3-livrable split
❌ §1 written before §2-§7 are final
❌ Bibliography missing or not deduplicated
❌ on_complete customization not followed

## On Complete

Run: `python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow.on_complete`

If the resolved `workflow.on_complete` is non-empty, follow it as the final terminal instruction before exiting.

Congratulations on completing your PROVE qualification! 🎯
