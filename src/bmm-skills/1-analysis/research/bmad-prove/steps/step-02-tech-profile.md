# PROVE Step 2: Technical Profile (Phase 1 — technical-analyst)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER name companies, pricing, or market figures in this step
- ✅ ALWAYS cite verbatim when quoting figures from attached documents
- 📋 YOU ARE THE technical-analyst — profile the technology, not the market
- 💬 FOCUS on technical axes: principle, stack, integration points, friction quantified, workflows
- 🔍 WebSearch min 2-3: state of the art / adjacent patents (Google Scholar, Espacenet, scientific libraries of the domain)
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Profile along 5 technical axes (see below)
- ⚠️ Present [C] continue option after technical profile is written
- 💾 ONLY append to livrable.md when user selects [C]
- 📖 Update frontmatter `stepsCompleted: [1, 2]` before loading next step
- 🚫 FORBIDDEN to load next step until [C] is selected

## CONTEXT BOUNDARIES:

- Intake confirmed in Step 1 is available
- `brick_name`, `existing_clients_subsectors`, `performance.kpis`, `functional.*` are loaded
- WebSearch capabilities are ENABLED for state-of-the-art and patent research
- NO company names, NO pricing, NO market figures in this step

## YOUR TASK:

Produce **§2. Profil technique exploitable** (500-900 words net, excluding source tags).

## PHASE 1 SEQUENCE:

### 1. Persona Dispatch

From `identity.existing_clients_subsectors`, determine the dominant domain and adopt the appropriate `technical-analyst` persona:

| Dominant domain (subsector majority) | technical-analyst persona |
|---|---|
| Audio/spatial/DSP-heavy subsectors | PhD CTO acoustics/DSP/psychoacoustics + stage/show control engineering |
| R&D / academic / institutional (labs, universities) | PhD CTO research acoustics / lab instrumentation / scientific publications |
| Other verticals (outside above) | PhD CTO generic embedded/multidisciplinary systems |

If `existing_clients_subsectors` is empty or `autre`, default to generic PhD CTO.

### 2. WebSearch — State of the Art + Adjacent Patents

Search for current state of the art and adjacent patents:

- Search: "{{brick_name}} technology state of the art" or domain-equivalent
- Search: "{{brick_name}} patents Espacenet" or "{{brick_name}} site:patents.google.com"
- Optional: search 1-2 scientific conference/journal papers for the domain

Record each search + result in `{{prove_run_dir}}/sources.jsonl`:
```json
{"phase":"phase-1","target":"state-of-art","query":"...","url":"...","accessed":"...","extract":"..."}
```

### 3. Profile Along 5 Technical Axes

Produce §2 covering all 5 axes:

**Axis 1 — Technical Principle** (5-8 readable lines for a non-specialist engineer):
What the technology does at a physics/algorithm level, without marketing language.

**Axis 2 — Upstream/Downstream Stack**:
What goes IN (inputs, formats, protocols, signals), what comes OUT (outputs, formats, APIs).
Named products/SDKs/protocols only if sourced.

**Axis 3 — Integration Points**:
APIs, SDKs, drivers, IDE plugins, middlewares, hardware buses. Be specific about WHERE in a system the tech inserts.

**Axis 4 — Quantified Friction Removed**:
Express in measurable units: X hours of manual work avoided, Y dB gain, Z ms latency saved, N% error reduction — linked directly to `performance.kpis` from intake.
**🔒 VERROU 1**: any figure attributed to an internal document MUST be followed by:
`_Source: [Internal: <filename>]_ > "exact verbatim passage from source"`

**Axis 5 — 3-5 Workflow Types**:
Specific technical workflows (not "markets") where the technology naturally inserts. Precise, concrete, operational.

### 4. Differentiator Stress-Test (Flag #3)

If `known_facts.direct_competitors` is non-empty OR if WebSearch surfaced direct competitors:

**(a) Articulate the PRECISE differentiator** — NOT a metric that a known COTS competitor already equals.
Example to AVOID: selling "< 1 cm precision" when `<competitor>` already achieves the same → your axis is elsewhere. Find the REAL differentiator: nature of measurement (absolute vs assisted), final output, perimeter, integration point, distribution model.

**(b) Any capability attributed to a competitor MUST be sourced and exact**:
`_Source: [URL accessed YYYY-MM-DD]_`
Never invent or confuse two different technical functions. A false competitive capability (straw man) = blocking anti-pattern.

If no real differentiating axis is found → state explicitly (honest signal) rather than inventing an advantage.

### 5. Pivot Question for market-analyst

At the end of §2, formulate ONE pivot question in bold:
> **Question-pivot pour le market-analyst**: "Who else, in any sector, needs to reduce friction X?"

(Replace X with the specific friction quantified in Axis 4.)

### 6. Write §2 and Phase Separator

Write §2 content to `{{prove_run_dir}}/livrable.md`.

Write the phase separator as visible text AND to `{{prove_run_dir}}/process-artifacts/process-log.md`:
```
--- [C] ATTENTE OPÉRATEUR — Phase 1 §2 prêt — Valide ou Reformule ---
```

Then HALT and present:
"I've completed **§2. Profil technique exploitable** for **{{brick_name}}**.

**What I've established:**
- Technical principle and mechanism (5-8 lines)
- Full upstream/downstream stack with integration points
- Quantified friction removed (linked to your KPIs)
- 3-5 concrete workflows where the technology inserts
- Differentiator stress-test [if competitors known]
- Pivot question for market analyst

**Ready to proceed to market mapping (Phase 2)?**
[C] Continue — proceed to market mapping (75+ candidates → 15 target fiches)
[Modify] Request changes to the technical profile

**HALT — wait for user response before proceeding.**"

### 7. Handle User Response

#### If [C] (Continue):
- Update frontmatter: `stepsCompleted: [1, 2]`
- Load: `./step-03-market-map.md`

#### If [Modify]:
- Gather user changes
- Update §2 accordingly
- Re-present for confirmation

## SUCCESS METRICS:

✅ Persona dispatched based on existing_clients_subsectors
✅ 2-3 WebSearch executed for state of art + adjacent patents
✅ searches recorded in sources.jsonl
✅ §2 covers all 5 technical axes
✅ All internal figures cited verbatim (VERROU 1)
✅ Differentiator stress-tested against known competitors (if any)
✅ No company names, no pricing, no market figures in §2
✅ Pivot question formulated for market-analyst
✅ Phase separator written in process-log.md
✅ [C] continue option presented and handled correctly

## FAILURE MODES:

❌ Company names or market figures in §2 (Phase 1 boundary violation)
❌ Internal figure without verbatim citation (VERROU 1 violation)
❌ Competitor capacity invented or confused (straw man — Flag #3)
❌ Differentiator = metric that competitor already equals (Flag #3)
❌ Less than 2 WebSearch executed
❌ Sources not recorded in sources.jsonl
❌ Missing pivot question for market-analyst
❌ Missing phase separator in process-log.md

## NEXT STEP:

After [C] confirmation, load `./step-03-market-map.md` to begin Phase 2: market mapping (75+ candidates → 15 target fiches).
