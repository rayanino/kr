# NEXT — Excerpting Engine SPEC Design

## Current Position

- Source engine: validation in progress (Step 2 — deterministic sweep)
- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Architecture: COMMITTED at 5636ceb (5 engines: Source → Normalization → Excerpting → Taxonomy → Synthesis)
- Architecture C experiment: ✅ 10 prose divisions validated
- Format diversity experiment: ✅ 13 divisions validated (6 verse-commentary, 4 longer prose, 2 masala, 1 QA)
  - Verse-commentary: PASS — no Phase 1 restructuring needed
  - Longer divisions: PASS — quality holds at 2500-3100w
  - Evaluation: `experiments/format_diversity_test/EVALUATION.md`

## What to Do

Design the excerpting engine SPEC. This is the third engine in the pipeline (Source → Normalization → **Excerpting** → Taxonomy → Synthesis).

The excerpting engine takes normalized text divisions and produces teaching units — self-contained passages that each teach one concept, rule, or topic. These teaching units are the atoms that feed into the taxonomy and synthesis engines.

## Validated Constraints (from experiments)

These are empirically validated and MUST be incorporated into the SPEC:

1. **Two-phase extraction (Approach B):** Classify segments first, then group into teaching units. Validated on 23 divisions across 2 experiments.
2. **MAX_TOKENS=32768 for classify phase** on divisions >2000 words. Default 8192 is insufficient.
3. **Minimum teaching unit size: ~50 words.** Adjacent sub-threshold units merged with nearest neighbor.
4. **Full coverage verification:** Union of teaching unit word ranges must equal total division text. No gaps or overlaps.
5. **Verse-commentary Phase 1 handler: DEFERRED.** Not architecturally required. Add as quality optimization if Step 3 reveals edge cases.
6. **Phase 1 splitting threshold: 5000w.** No evidence of degradation up to 3100w. 96.8% of Shamela divisions are ≤2000w.

## Open Questions for SPEC Design

1. What are the excerpting engine's input and output contracts? (Input from normalization, output to taxonomy)
2. How does Phase 1 (deterministic preprocessing) interact with Phase 2 (LLM extraction)?
3. What error codes and error handling does the excerpting engine define?
4. How are teaching units stored? (Schema, file format, relationship to source divisions)
5. What quality gates exist between Phase 1 and Phase 2?
6. How does the engine handle divisions that are too short for meaningful teaching units (<50 words)?
7. How does the engine handle very long divisions (>5000w) that need splitting?

## Read First

1. `experiments/format_diversity_test/EVALUATION.md` — the evaluation you're building on
2. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — the architecture that committed to this design
3. `experiments/architecture_test/EVALUATION_WORKBOOK.md` — original 10-division evaluation
4. `experiments/format_diversity_test/EVALUATION_WORKBOOK.md` — 13-division evaluation (verse-commentary + longer prose)
5. `SPEC_CORE.md` — source engine SPEC (for contract patterns)
6. `engines/normalization/SPEC.md` — normalization SPEC (for input contract)
7. `KNOWLEDGE_INTEGRITY.md` — corruption threats T-1 through T-7
8. `reference/ENGINE_BUILD_BLUEPRINT.md` — build process

## Design Approach

Use `kr-research` for deep research on teaching unit extraction from Arabic scholarly text. Use `thinking-frameworks` for multi-angle analysis of architectural decisions. Use `kr-integrity` to audit the SPEC for silent failure patterns.

The SPEC should follow the same structure as SPEC_CORE.md (source engine) and the normalization SPEC.

## After This

Once the SPEC is designed and reviewed, Claude Code builds the engine following the ENGINE_BUILD_BLUEPRINT.md process (7 sessions, same as normalization).
