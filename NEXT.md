# NEXT — Architecture Decision: Evaluate Experiment Results

## Your Task

Read the experiment results and make the architecture decision for KR's remaining engines. This is the most consequential decision in the project — it determines whether we build 4 or 6 engines, and how they're structured.

## Background (read carefully)

KR has 7 engines planned. 2 are COMPLETE:
- Source engine ✅ (566 tests, 274 books validated)
- Normalization engine ✅ (470 tests, 7,475 books at 100% success)

The remaining 5 were designed as: passaging → atomization → excerpting → taxonomy → synthesis.

An architecture review concluded that **atomization and excerpting should merge into a single engine** (Architecture C), based on:
- The atom stream has NO external consumer (taxonomy and synthesis read excerpt-level data only)
- The atomization→excerpting boundary creates error propagation with no isolation benefit
- 60% of the passaging SPEC (§4.B) describes machinery to solve problems that passaging itself creates (argument detection, completeness forecasting) — and these depend on `discourse_flow` which is `None` in all normalization code
- D-011 (passage containment rule) forces passaging to be near-perfect at boundary placement, driving excessive complexity

**Architecture C proposes:**
- **Passaging engine** — deterministic, core-only, keeps cross-page assembly and format-specific chunking
- **Excerpting engine** — LLM-powered, absorbs atomization, identifies teaching units + classifies + evaluates self-containment
- **Taxonomy engine** — unchanged
- **Synthesis engine** — unchanged
- **D-011** softened from hard constraint to soft preference

**The experiment tests whether Architecture C is viable** by running LLM extraction on 10 real normalized Arabic scholarly text divisions.

## The Three Questions

**Q1: Can an LLM identify teaching units from normalized division text?**
- Pass: The LLM produces teaching unit boundaries that a careful reader would agree with for ≥7 of 10 divisions
- Fail: Boundaries are nonsensical or consistently wrong → Architecture C is not viable

**Q2: Is two-phase LLM (classify then group) better than single-phase (joint)?**
- Look at Approach A (single-call) vs Approach B (two-call) across all 10 divisions
- If B produces more sensible boundaries than A → use two-phase internally
- If A matches or beats B → use single-phase (simpler)

**Q3: Does cross-boundary context improve split argument detection?**
- Look at Approach C (with context) vs Approach B (without) on the 03_fiqh divisions
- If C detects or handles argument splits that B missed → soft D-011 validated
- If C adds nothing → D-011 relaxation provides no measured benefit

## How to Evaluate

### Step 1: Read the experiment data
```
experiments/architecture_test/EVALUATION_WORKBOOK.md    — PRIMARY (full Arabic text + all results)
experiments/architecture_test/results/RUN_SUMMARY.md    — overview (unit counts, errors)
experiments/architecture_test/EXPERIMENT_DESIGN.md       — methodology and decision criteria
```

### Step 2: For each of the 10 divisions

Read the full Arabic text. Then for each approach's results:
1. **Are the unit boundaries sensible?** Would you, reading this text as a scholar, agree that each teaching unit is a coherent, self-contained segment?
2. **Are the scholarly function classifications correct?** Is a definition actually a definition? Is evidence_hadith actually hadith evidence?
3. **Is the self-containment judgment accurate?** Units marked self-contained — are they really?

Focus on BOUNDARY QUALITY above all else. Classification can be tuned with prompts. Boundaries determine whether the architecture works.

### Step 3: Compare approaches

For each division where A and B disagree on unit count or boundaries:
- Which approach produced more sensible boundaries?
- Is one consistently over-segmenting (too many tiny units) or under-segmenting (too few large units)?

For the 03_fiqh divisions where C was run:
- Did the cross-boundary context cause C to handle any split arguments differently from B?

### Step 4: Make the decision

Based on the decision matrix in EXPERIMENT_DESIGN.md:

| Outcome | Action |
|---------|--------|
| Q1 Pass + Q2 two-phase wins | Commit Architecture C with two-phase internal LLM (C-1) |
| Q1 Pass + Q2 single-phase wins or tie | Commit Architecture C with single-phase LLM (C-2) |
| Q1 Pass + Q3 context helps | Also commit soft D-011 |
| Q1 Pass + Q3 context doesn't help | Keep D-011 hard for now |
| Q1 Fail | Abort Architecture C. Revert to Architecture B (7 engines). |

### Step 5: Write the decision

If committing to Architecture C, write a concrete specification of:
1. The 6-engine (or 4-remaining) architecture with clear engine boundaries
2. What the merged Excerpting Engine's internal phases look like
3. What D-011 becomes (hard/soft/eliminated)
4. What changes in the passaging SPEC (which §4.B capabilities are dropped)
5. Update NEXT.md to direct the next session (passaging engine SPEC design under the new architecture)

If reverting to Architecture B, explain why and update NEXT.md to continue with the original 7-engine plan.

## Experiment Data Summary

From `RUN_SUMMARY.md`:
- 10 divisions tested across 5 fixtures (fiqh, balagha, usul, nahw, hadith-evidence)
- Model: Claude Opus 4.6 via OpenRouter
- 34 API calls, zero errors
- Approach A (single-call) produced 11-26 units per division
- Approach B (two-call) produced 8-20 units per division
- Approach C (cross-boundary) ran on 2 fiqh divisions, produced 7-9 units

**Notable pattern from the summary:** A consistently produces MORE units than B (sometimes 2x: 26 vs 13 on nahw div_20). This suggests A may be over-segmenting or B may be grouping more aggressively. The evaluator must read the Arabic to determine which is correct.

## Read First

1. This file (NEXT.md)
2. `experiments/architecture_test/EVALUATION_WORKBOOK.md` — the primary evaluation input
3. `experiments/architecture_test/results/RUN_SUMMARY.md` — quantitative overview
4. `experiments/architecture_test/EXPERIMENT_DESIGN.md` — methodology reference

## Skills to Use

- `thinking-frameworks` (DEEP tier — irreversible decision)
- `critical-review` (verify your own evaluation)
- `kr-research` (only if the results are ambiguous and you need external evidence)

## Do NOT Do

1. Do NOT re-run the experiment or make new API calls
2. Do NOT modify normalization or source engine code
3. Do NOT skip reading the Arabic text — quantitative metrics alone cannot decide this
4. Do NOT let momentum ("we've done so much work on Architecture C") override quality ("the results show it doesn't work")
