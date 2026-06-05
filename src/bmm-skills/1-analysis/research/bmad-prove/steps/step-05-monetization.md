# PROVE Step 5: Monetization Plan (Phase 4 — monetization-analyst)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER invent pricing figures — derive from explicit formula OR suppress if not sourceable
- ✅ ALWAYS use explicit EUR derivation: `Value generated for target (EUR/year) × capture rate (10-30%) → price (EUR/year)`
- 📋 YOU ARE THE monetization-analyst — multi-sector, model-first reasoning
- 💬 FOCUS on: pricing formula per target, preferred vehicle, deal structure, anti-targets
- 🔍 WebSearch min ≥1 per Tier-1 target on market comparables (analyst reports, Statista)
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Derive pricing for each Tier-1 target with explicit formula
- ⚠️ Present [C] continue option after §6 + §7 are written
- 💾 ONLY append to livrable.md when user selects [C]
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4, 5]` before loading next step
- 🚫 FORBIDDEN to load next step until [C] is selected

## CONTEXT BOUNDARIES:

- §2 (technical profile), §4 (15 fiches), §5 (Tier-1 deep dive with IP/TAM) are available
- `known_facts.preferred_vehicle`, `budget_min_per_deal_eur`, `budget_max_per_deal_eur` are loaded
- WebSearch capabilities are ENABLED

## YOUR TASK:

Produce **§6. Plan de monétisation** (500-900 words net) and **§7. Anti-cibles** (200-350 words net).

---

## PHASE 4 SEQUENCE:

### 1. WebSearch — Market Comparables

For each Tier-1 target, search for market pricing comparables:
- Search: `"<technology type>" licensing pricing SaaS` or `"<domain>" SDK royalty comparable`
- Search: `"<target segment>" software tools pricing analyst report`
- Sources prioritized: Statista, Strategy Analytics, IDC, Gartner, trade analyst reports

Record in `{{prove_run_dir}}/sources.jsonl`:
```json
{"phase":"phase-4","target":"<Target>","query":"...","url":"...","accessed":"...","extract":"..."}
```

### 2. Pricing Derivation per Tier-1 Target

For each Tier-1 target, apply the **mandatory pricing formula**:

```
PRICING DERIVATION — <Target>
Step 1: Quantified value generated (EUR/year):
  [X hours saved × hourly cost] + [Y errors avoided × cost per error] + [Z revenue uplift]
  = Total economic value = V EUR/year
  _Source: [URL or Internal: <file> for underlying figures]_

Step 2: Capture rate (10-30%):
  Comparable market data → capture rate = R%
  _Source: [URL for comparable]_

Step 3: Proposed price:
  V × R% = Price = [MIN EUR/year] — [MAX EUR/year]
  Vehicle: {{known_facts.preferred_vehicle}} (or best fit if not specified)
```

**If the derivation is not sourceable** (V or comparable not found after ≥2 WebSearch attempts):
→ **Suppress pricing for this target** explicitly: "Pricing suppressed — market comparable not found. Manual validation required."
Do NOT invent a number. A deliverable without pricing for one target > a deliverable with invented pricing.

### 3. Produce §6. Plan de monétisation

Write to `{{prove_run_dir}}/livrable.md`:

**§6 structure** (500-900 words net):

```markdown
## §6. Plan de monétisation

### Vehicle recommandé
[Derived from known_facts.preferred_vehicle + target fit analysis]

### Pricing par cible Tier-1

#### <Target 1>
[Pricing derivation formula + result]
[Vehicle recommendation for this specific target]
[Deal structure recommendation: NRE + runrate / pure royalty / licence flat / etc.]
_Source: [URL for comparables]_

#### <Target 2>
[Same structure]

...

### Pipeline recommandé
[Sequencing: which target to approach first, why, what signal triggers approach]

### Route-to-market
[Direct / via integrator / via distributor / via standards body]
[Budget and timeline considerations from intake]

### Revenue model projection
[Conservative / base / optimistic scenarios if comparables allow]
[Explicitly flagged as projection, not commitment]
_Source: [URL for market comparables]_
```

### 4. Produce §7. Anti-cibles

Write to `{{prove_run_dir}}/livrable.md`:

**§7 structure** (200-350 words net):

```markdown
## §7. Anti-cibles

### Secteurs exclus (from intake)
[List from known_facts.excluded_sectors with brief rationale]

### Entités exclues (from intake)
[List from known_facts.excluded_targets — e.g. strategic competitors — with rationale]

### Cibles downgradées (Tier-2 FTO-first ou Gate-5)
[List targets that were downgraded in Phase 2/3 and why — Gate 5 / FTO-first / re-implementation risk]
_Each with ≥50-word justification_

### Secteurs objectivement non-adressables
[From Phase 2a Mode 3 (Absurd Challenge): sectors where the tech is truly not useful — brief honest statement]
```

### 5. Write Phase Separator

Write as visible text AND in process-log.md:
```
--- [C] ATTENTE OPÉRATEUR — Phase 4 §6+§7 prêts — Valide ou Reformule ---
```

Then HALT and present:
"I've completed **Phase 4: Monetization Plan** for **{{brick_name}}**.

**What I've produced:**
- §6 Monetization plan with explicit EUR pricing derivation for each Tier-1 target
- §7 Anti-targets with justified exclusions
- WebSearch comparables recorded in sources.jsonl

**Please review §6 and §7. Ready to proceed to final assembly?**
[C] Continue — proceed to final deliverable assembly and audit
[Modify] Request changes to pricing or anti-targets

**HALT — wait for user response before proceeding.**"

---

## SUCCESS METRICS:

✅ ≥1 WebSearch per Tier-1 target on comparables
✅ Pricing derivation formula explicit for each target (V × R% → EUR range)
✅ Pricing suppressed (not invented) when comparables not found
✅ All figures sourced (or explicitly marked as suppressed)
✅ §6 covers: vehicle, pricing per target, pipeline, route-to-market, revenue projection
✅ §7 covers: excluded sectors, excluded targets, FTO-first downgrades, non-addressable sectors
✅ Each anti-target exclusion ≥50 words justified
✅ Phase separator written in process-log.md

## FAILURE MODES:

❌ Pricing figure without explicit derivation formula (audit C4 FAIL)
❌ Pricing invented without source (HYPOTHESIS → audit C5b FAIL)
❌ §6 missing vehicle or pipeline recommendations
❌ §7 missing or without justification (silent anti-target kill)
❌ [HYPOTHESIS-NON-SOURCED] or equivalent bypass patterns in §6/§7 (audit C5b FAIL)

## NEXT STEP:

After [C] confirmation, load `./step-06-completion.md` to begin Phase 5: final assembly, §1 executive summary, audit run, and multi-livrable output.
