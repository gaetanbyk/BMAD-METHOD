# PROVE Step 1: Intake (Phase 0 — Mini-intake + Auto-completion)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate target content or market analysis in intake step
- ✅ ALWAYS collect the mini-intake before auto-completing the full intake
- 📋 YOU ARE THE PROVE ORCHESTRATOR — intake is the foundation
- 💬 FOCUS on understanding the technology, not researching targets yet
- 🔍 NO WebSearch in intake — that begins in Phase 1
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ⛔ ZERO mandatory AskUserQuestion — use free-text validation only (≤1 AskUserQuestion, ≤4 questions if a human field is truly missing)
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with `{communication_language}`

## MINI-INTAKE TEMPLATE

If the user hasn't provided a filled mini-intake, present this template and ask them to fill it:

```yaml
# PROVE Mini-intake — fill ~10 fields, say "go"
prove_lite_version: "1.0.0"
session_id: ""                       # leave empty, auto-generated

identity:
  brick_name: ""                     # short name for your technology (e.g. "<YourTech>")
  organization: ""                   # your company / entity name
  market_posture: "auto"             # auto | vertical | horizontal
  existing_use_case: ""              # 1-2 sentences: (who pays today) × (for what) × (business model)
  must_consider_targets: []          # 3-5 real entity names you want scored (optional)

known_facts:
  direct_competitors: []             # 0-5 real names of competitors doing similar things
  excluded_sectors: []               # sectors to exclude
  excluded_targets: []               # specific entities NOT to arm (strategic competitors)
  preferred_vehicle: ""              # SDK_royalty | exclusive | NRE_runrate | licence | JV | open
  budget_min_per_deal_eur: 0         # minimum deal size you'd accept (EUR)
  budget_max_per_deal_eur: 0         # target deal size (EUR)

user_signature: ""                   # your initials + ISO date, e.g. "AB 2026-06-01"
```

## EXECUTION PROTOCOLS:

### 1. Receive Intake + Attachments

**If mini-intake received** (pasted or attached) AND/OR attachments (PDF, datasheets, patents, demo videos, code):
- Read mini-intake and ALL attachments in full
- Proceed to auto-completion

**If no mini-intake AND no attachments**:
- Ask user (one short message): "Please fill the mini-intake above and/or attach your technology documentation (PDF specs, datasheets, patents, demo videos). Then say 'go'."
- WAIT for response. Do not fabricate anything.

**If mini-intake but 0 attachments**: Continue with auto-completion, but flag clearly that without attachments the deliverable will rely more on `⟨À CONFIRMER⟩` markers.

### 2. Auto-complete Full Intake (intake.v5.yaml)

Write `{{prove_run_dir}}/intake.v5.yaml` — a complete 19-field intake — from the mini-intake + attachments:

**Fields reprise from mini-intake** (remap to canonical positions):
- `identity.brick_name`, `identity.brick_version` (if given), `identity.organization`
- `identity.market_posture` (default `auto`)
- `identity.existing_use_case`, `identity.must_consider_targets`
- `known_facts.*` (preferred_vehicle, budget_min/max, excluded_sectors/targets, direct_competitors)
- `user_signature`

**Fields derived from attachments**:
- `functional.what_it_is`, `what_it_is_not`, `primary_function`
- `performance.kpis`, `trl_declared`, `demonstrator`
- `corpus.references_urls`, `internal_docs_paths`
- `identity.existing_clients_subsectors`

**🔒 VERROU 1 — Source fidelity**: any figure/KPI/threshold taken from an attachment MUST be followed by verbatim citation:
> `_Source: [Internal: <filename>]_ > "exact verbatim passage"`
Never paraphrase a threshold. A SUCCESS threshold = the value that PASSES in the source.

**🔒 VERROU 2 — Anti-hallucination**: any field NOT sourced by attachment OR mini-intake → mark `⟨À CONFIRMER⟩`. Never invent a figure, URL, name, or date.

Write the complete YAML once as a new file (not incremental edits). Before writing: `mkdir -p {{prove_run_dir}}/`.

### 3. Display Summary + Request Free-text Validation

Display to user:
**(a) 6-line RÉSUMÉ**: brick_name · what it is (1 line) · current use · market_posture · preferred_vehicle · budget range. **Highlight `⟨À CONFIRMER⟩` fields in bold.**
**(b) Full YAML** in a code block for review.

Then write:
> "Validate (type 'go'/'ok') or correct in plain language (e.g. 'market_posture vertical, budget max 500k, remove X from excluded'). I'll update and confirm the changes."

- User corrects in free text → parse, update multiple fields at once, show diff `before→after` of changed fields only, re-ask validation.
- NEVER re-ask a field already provided.
- NEVER emit an AskUserQuestion per field.

### 4. Finalize Intake

On 'go'/'ok':
- Update frontmatter: `stepsCompleted: [1]`
- Add confirmation note to livrable.md: "Intake confirmed by user on {{date}}"
- Load: `./step-02-tech-profile.md`

## SUCCESS METRICS:

✅ Mini-intake received and all attachments read in full
✅ Full intake.v5.yaml auto-completed in one Write (not incremental)
✅ All figures from attachments cited verbatim (VERROU 1)
✅ All unsourced fields marked ⟨À CONFIRMER⟩ (VERROU 2)
✅ 6-line summary displayed with ⟨À CONFIRMER⟩ fields highlighted
✅ Free-text validation (not per-field AskUserQuestion)
✅ Document frontmatter updated before loading next step

## FAILURE MODES:

❌ Starting without mini-intake or attachments (fabricating intake data)
❌ Paraphrasing a threshold from an attachment instead of verbatim citation
❌ Inventing a field value not sourced in mini-intake or attachments
❌ Using AskUserQuestion per field (the old 37-AUQ gauntlet)
❌ Re-asking a field already provided
❌ Writing intake as incremental edits instead of single Write

## NEXT STEP:

After intake validation, load `./step-02-tech-profile.md` to begin Phase 1: technical profiling.
