# NEXT — Excerpting Engine SPEC Design

## Current Position

- Source engine: validation in progress (Step 2 — deterministic sweep)
- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Architecture: COMMITTED at 5636ceb (5 engines: Source → Normalization → Excerpting → Taxonomy → Synthesis)
- Architecture C experiment: ✅ 10 prose divisions validated (536-1040w)
- Format diversity experiment: ✅ 13 divisions validated (6 verse-commentary, 4 longer prose, 2 masala, 1 QA)
  - Verse-commentary: PASS — no Phase 1 restructuring needed (pure verse deferred to Step 3)
  - Longer divisions: PASS for well-structured text (2500-3100w); marker-free long text untested
  - Evaluation: `experiments/format_diversity_test/EVALUATION.md` (v2, with self-review findings)

## What to Do

Design the excerpting engine SPEC. This is the third engine in the pipeline (Source → Normalization → **Excerpting** → Taxonomy → Synthesis).

The excerpting engine takes normalized text divisions and produces teaching units — self-contained passages that each teach one concept, rule, or topic. These teaching units are the atoms that feed into the taxonomy and synthesis engines.

## Empirically Validated Facts (from experiments)

These are genuinely validated and safe to build on:

1. **Two-phase extraction works.** Both Approach A (single-call) and Approach B (classify-then-group) produce correct teaching unit boundaries across 23 divisions in 2 experiments. Neither is strictly superior — the SPEC decides which to use.
2. **MAX_TOKENS=32768 for classify phase** on divisions >2000 words. Default 8192 is insufficient.
3. **Full coverage verification required.** Union of teaching unit word ranges must equal total division text. No gaps or overlaps.
4. **Verse-commentary Phase 1 handler: DEFERRED.** Not architecturally required. Can be added if Step 3 or engine evaluation reveals edge cases.
5. **Phase 1 splitting threshold: 5000w supported for well-structured text.** No degradation observed up to 3100w WITH explicit markers. 96.8% of Shamela divisions are ≤2000w.

## Open Design Questions (from experiments + architecture gaps)

These need decisions during SPEC design:

1. **Approach selection:** Which approach (A, B, or hybrid) is primary? B provides finer granularity and more control points. A produces larger, more self-contained units. Trade-offs depend on downstream requirements.
2. **Minimum teaching unit size.** B produces units as small as 20-40 words at longer lengths. A minimum is needed but the threshold requires calibration. ~50w is a starting hypothesis, not a validated number.
3. **Marker-free long divisions.** All tested long divisions had explicit structural markers. Should the splitting threshold be lower for marker-free text? How does the engine detect marker presence?
4. **Input/output contracts.** What does the excerpting engine receive from normalization and produce for taxonomy?
5. **Error codes and error handling.** What error taxonomy does the excerpting engine define?
6. **Teaching unit storage schema.** Format, relationship to source divisions, fields.
7. **Quality gates between Phase 1 and Phase 2.**
8. **Divisions too short for teaching units (<50 words).** Merge strategy.
9. **Very long divisions (>5000w) that need splitting.** Split strategy.
10. **Books with empty/minimal division trees (Gap 4).** 5,901 Shamela books with <5 headings. What does the engine do when it receives an empty or near-empty normalized package?
11. **Same-model evaluation bias (Gap 3).** The architect must design structural mitigations for the 30-book probe and engine evaluation — e.g., adversarial probes with known boundaries, different model for spot-checks, mechanical criteria. Owner spot-checks supplement but do not replace architect-designed verification.

## Read First

1. `experiments/format_diversity_test/EVALUATION.md` — the evaluation you're building on (read v2 with self-review)
2. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — the architecture that committed to this design
3. `reference/archive/sessions/architecture_decision_handoff.md` — the 4 gaps and session lessons
4. `experiments/architecture_test/EVALUATION_WORKBOOK.md` — original 10-division evaluation
5. `experiments/format_diversity_test/EVALUATION_WORKBOOK.md` — 13-division evaluation (verse-commentary + longer prose)
6. `SPEC_CORE.md` — source engine SPEC (for contract patterns)
7. `engines/normalization/SPEC.md` — normalization SPEC (for input contract)
8. `KNOWLEDGE_INTEGRITY.md` — corruption threats T-1 through T-7
9. `reference/ENGINE_BUILD_BLUEPRINT.md` — build process

## Design Approach

Use `kr-research` for deep research on teaching unit extraction from Arabic scholarly text. Use `thinking-frameworks` for multi-angle analysis of architectural decisions. Use `kr-integrity` to audit the SPEC for silent failure patterns.

The SPEC should follow the same structure as SPEC_CORE.md (source engine) and the normalization SPEC.

## After This

Once the SPEC is designed and reviewed, Claude Code builds the engine following the ENGINE_BUILD_BLUEPRINT.md process.
