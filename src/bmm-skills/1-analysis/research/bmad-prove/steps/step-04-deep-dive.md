# PROVE Step 4: Tier-1 Deep Dive (Phase 3 — 6-axis profile + IP/TAM/Competitive + Cross-agent Validation)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER classify a target Tier-1 without a complete 6-axis profile AND cross-agent technical validation
- ✅ ALWAYS run a distinct validation agent (or dedicated validation pass) for each Tier-1 target
- 📋 YOU RETAIN the orchestrator role — the technical-analyst persona produces the 6-axis profile
- 💬 FOCUS on: 6-axis profile, IP/TAM/competitive analysis, and cross-agent validation trace
- 🔍 WebSearch min ≥3 per Tier-1 target (≥15 total): official site + IR/investor relations + LinkedIn functions + trade press
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 For each user-selected Tier-1 target: 6-axis profile + IP/TAM + cross-agent validation
- ⚠️ Present [C] continue option after §5 is complete
- 💾 ONLY append §5 to livrable.md when user selects [C]
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4]` before loading next step
- 🚫 FORBIDDEN to load next step until [C] is selected

## CONTEXT BOUNDARIES:

- §2 (technical profile) and §3+§4 (15 target fiches) are available
- User has selected 3-5 Tier-1 targets to deep-dive
- WebSearch capabilities are ENABLED

## YOUR TASK:

For each user-selected Tier-1 target (3-5 targets), produce:
1. 6-axis technical profile (technical-analyst pass 2)
2. IP/TAM/Competitive analysis with patent registry search
3. Cross-agent technical validation (traced in process-artifacts)

Then write **§5. Top 3-5 cibles INDISPENSABLE** (≤600 words net per target).

---

## PER-TARGET SEQUENCE:

### Phase 3A — WebSearch (≥3 queries per target)

For each Tier-1 target `<Target>`:

1. Search: official site + product pages: `"<Target>" site:<target-domain>` or `"<Target>" products`
2. Search: investor relations / press releases: `"<Target>" investor relations annual report` or `"<Target>" press release`
3. Search: LinkedIn functions validation: `"<Target>" "technical director" OR "VP engineering" OR "CTO" site:linkedin.com`
4. Search: trade press: `"<Target>" [domain keywords] acquisition partnership`

Record all in `{{prove_run_dir}}/sources.jsonl`:
```json
{"phase":"phase-3","target":"<Target>","query":"...","url":"...","accessed":"...","extract":"..."}
```

---

### Phase 3B — 6-Axis Profile

For each Tier-1 target, produce a structured 6-axis profile (≤600 words net per target):

```
#### <Target> — 6-Axis Profile

**Axis 1 — Workflow step-by-step with duration/cost**:
Describe their current workflow for the process where the technology inserts.
Duration, cost, resources. What steps are manual, error-prone, slow. _Source: [URL]_

**Axis 2 — Named stack (product by product)**:
Current tools/software/hardware they use for this workflow. Named products with confidence flag:
[CONFIDENCE: HIGH | MED | LOW] _Source: [URL]_
Stack items without confidence flag → FAIL.

**Axis 3 — Exact insertion point**:
Where EXACTLY does the technology insert in their workflow?
Before which step? After which step? Which interface (API/SDK/hardware)? _Source: [URL]_

**Axis 4 — Quantified pain removed**:
Concrete measurable improvement: hours saved, EUR/year recovered, error rate reduction.
_Source: [URL or Internal: <file>]_

**Axis 5 — Structural gap not fillable internally**:
Why can they NOT build this themselves? (absent expertise, IP lock, time-to-market, cost).
_Source: [URL]_

**Axis 6 — Integration risks**:
Technical compatibility risks, deployment constraints, security/compliance issues, organizational change management. _Source: [URL]_
```

**Completeness rule**: a Tier-1 fiche without all 6 axes → INVALID, downgrade to Tier-2.

---

### Phase 3C — IP/TAM/Competitive Analysis

For each Tier-1 target, produce:

#### IP Analysis (patent registry search — MANDATORY)

Search patent registries for relevant patents:
- Search Espacenet: `"<technology domain>" patent site:epo.org` or `"<brick_name>" CPC classification`
- Search Google Patents: `"<brick_name>" OR "<technology principle>"` 
- Search USPTO: `site:patents.google.com "<technology domain>"`
- Search WIPO: `"<technology domain>" site:patentscope.wipo.int`
- Search INPI (if French context): `"<technology domain>" site:bases-brevets.inpi.fr`

Document findings:
- Known blocking patents (by title + registry reference + assignee)
- Adjacent IP landscape
- FTO risk level: LOW / MEDIUM / HIGH (with source)
- If `known_facts.direct_competitors` holds entities → check if they hold blocking IP

Record in `{{prove_run_dir}}/process-artifacts/ip-analysis.md`:
```markdown
## IP Analysis — <Target>
- **Relevant patents found**: [list with titles, registry refs, assignees]
- **FTO risk**: LOW / MEDIUM / HIGH
- **Blocking risk**: [description if any]
- **Sources**: [list of registry URLs searched]
```

#### TAM Analysis

Search for Total Addressable Market data for this target's segment:
- Search: `"<Target> segment" TAM market size analyst report`
- Search: `"<Target> sector" market forecast 2026 2027`
- Sources: Statista, Strategy Analytics, IDC, Gartner (if accessible), or trade press estimates

Document in §5 for this target:
- Estimated TAM for this segment (EUR/year, with source and year of estimate)
- Serviceable Addressable Market (SAM) = what fraction is reachable with this technology
- _Source: [URL]_ mandatory for each figure (or suppress figure if not sourceable)

#### Competitive Analysis

For each Tier-1 target, document:
- Direct alternatives the target uses today (`Alternative-actuelle` from §4 fiche)
- Pricing/licensing model of the alternative (if sourceable)
- Gap vs. this technology (what the alternative CANNOT do)
- Why switching cost is acceptable (or flag barriers)
- If competitor capacity is claimed → MUST be sourced: `_Source: [URL accessed YYYY-MM-DD]_`

---

### Phase 3D — Cross-Agent Technical Validation (BMAD advantage)

**This step is the key BMAD advantage over mono-LLM PROVE runs.**

For each Tier-1 target, spawn OR simulate a dedicated `technical-validator` perspective to adversarially challenge the 6-axis profile:

**If BMAD Party Mode or Agent spawning is available**:
- Invoke a `technical-validator` agent with the prompt:
  > "You are a skeptical senior systems engineer. Your task: CHALLENGE this 6-axis technical profile for target `<Target>`. Find: (1) technical assumptions not backed by source, (2) integration claims that are over-optimistic, (3) quantified pain removals that are not credibly sourced, (4) structural gaps that the target COULD fill internally. Return a structured critique with PASS / WARN / FAIL per axis."

**If agent spawning is not available**:
- Switch explicitly to "devil's advocate" mode, challenge your own 6-axis profile, and document the critique as a distinct labeled section:
  > `## Cross-validation Critique — <Target>`

**Mandatory output** regardless of approach: write validation trace to `{{prove_run_dir}}/process-artifacts/cross-validation.md`:
```markdown
## Cross-validation — <Target> — {{date}}
**Method**: [agent-spawn | devil-advocate-pass]
**Axes reviewed**: [1-6]
**Findings**:
- Axis 1: [PASS/WARN/FAIL] — [note]
- Axis 2: [PASS/WARN/FAIL] — [note]
...
**Verdict**: [ACCEPTED_AS_TIER1 | DOWNGRADED_TO_TIER2 | NEEDS_REVISION]
**Revision applied**: [yes/no + what changed]
```

Any axis FAIL that is not addressed → target MUST be downgraded to Tier-2.

---

### Phase 3E — Assemble §5

After all targets are profiled, validated, and IP/TAM analysed:

Write **§5. Top 3-5 cibles INDISPENSABLE** to `{{prove_run_dir}}/livrable.md`.

Each entry includes:
- Full TRIPLET from §4 fiche (reinforced with Phase 3 research)
- 6-axis profile summary (≤300 words per target, full profile in process-artifacts)
- IP risk summary (FTO level + key patents if any)
- TAM/SAM estimate (with source)
- Cross-validation verdict
- Buyer: function + recommended approach channel

Write phase separator as visible text AND in process-log.md:
```
--- [C] ATTENTE OPÉRATEUR — Phase 3 §5 prêt — Valide ou Reformule ---
```

Then HALT and present:
"I've completed **Phase 3: Tier-1 Deep Dive** for **{{brick_name}}**.

**What I've produced:**
- 6-axis profiles for {{N}} Tier-1 targets
- IP analysis (patent registry search: Espacenet, Google Patents, USPTO, WIPO)
- TAM/SAM estimates for each target
- Cross-agent technical validation (traced in process-artifacts/cross-validation.md)

**Please review §5. Ready to proceed to Phase 4: Monetization?**
[C] Continue — proceed to monetization plan
[Modify] Request changes to deep-dive profiles

**HALT — wait for user response before proceeding.**"

---

## SUCCESS METRICS:

✅ ≥3 WebSearch per Tier-1 target (≥15 total for 5 targets)
✅ 6-axis profile complete for each Tier-1 target (all 6 axes present and sourced)
✅ Stack items carry confidence flags [CONFIDENCE: HIGH | MED | LOW]
✅ Patent registry search conducted (Espacenet + Google Patents + USPTO/WIPO)
✅ IP analysis documented in process-artifacts/ip-analysis.md
✅ TAM/SAM figures sourced (or explicitly suppressed if not sourceable)
✅ Cross-agent validation conducted and traced in process-artifacts/cross-validation.md
✅ Validation method documented (agent-spawn OR devil-advocate-pass)
✅ Targets failing validation downgraded to Tier-2
✅ Sources recorded in sources.jsonl
✅ Phase separator written in process-log.md

## FAILURE MODES:

❌ Missing axis in 6-axis profile (Tier-1 fiche invalid)
❌ Stack items without confidence flag
❌ No patent registry search conducted (audit C27 FAIL)
❌ TAM figures without sources (suppress instead of inventing)
❌ No cross-agent validation trace in process-artifacts (audit C28 FAIL)
❌ Cross-validation method not documented
❌ Downgrade not applied when validation finds axis FAIL
❌ <3 WebSearch per target

## NEXT STEP:

After [C] confirmation, load `./step-05-monetization.md` to begin Phase 4: monetization plan with explicit EUR pricing derivation.
