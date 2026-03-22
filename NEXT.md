# NEXT — Excerpting Engine SPEC Rewrite (Section-by-Section)

## Current Position

- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Architecture: COMMITTED at 5636ceb (5 engines: Source ✅ → Normalization ✅ → Excerpting → Taxonomy → Synthesis)
- Architecture C experiment: ✅ 23 divisions tested (10 original + 13 format diversity)
- Format diversity experiment: ✅ verse-commentary + longer prose validated (commit 0cd57a6)
- **Excerpting SPEC review: BLOCKED** — 16 findings, 3 CRITICAL (architecture mismatch)

## What Happened

The excerpting engine SPEC (98KB) was written for the old 7-engine architecture where passaging and atomization were separate upstream engines. The committed 5-engine architecture absorbed both into excerpting, but the SPEC was never restructured. Full review: `reference/archive/sessions/reviews/excerpting_spec_review.md`.

The domain knowledge in the SPEC (decontextualization prevention, multi-layer handling, evidence handling, implicit references, verse format, adversarial test cases) is excellent. The structural framework is wrong.

## What to Do

**Section-by-section SPEC rewrite.** Each section is analyzed deeply, not scanned. For each section ask:

1. Does this align with the committed architecture (normalized packages as input, three-phase internal model)?
2. Is this the best possible design, or can it be improved?
3. Will this cause future regrets when building or extending the engine?
4. Is every claim grounded in evidence (experiment results, normalization contracts, domain research)?
5. Are there edge cases or failure modes not covered?

### Rewrite Order

Process sections in dependency order — later sections depend on earlier ones being correct:

1. **§1 Purpose and Scope** — Align with 5-engine architecture. Define what this engine absorbs.
2. **§2 Input Contract** — Replace atom streams with normalized packages. Reference normalization contracts.py directly.
3. **§4.A.1 Processing Model** — Replace atom-grouping three-phase with architecture decision's three-phase: (a) Deterministic Preprocessing/passaging, (b) LLM classify-then-group, (c) Metadata Enrichment.
4. **§5 Quality & Self-Containment Standard** — Define §5.1 (self-containment standard), §5.2 (completeness), §5.3 (cross-topic rules) as formal referenceable sections.
5. **§4.A.2–§4.A.7 Domain Handling** — Adapt decontextualization, multi-layer, evidence, implicit refs, cross-topic, verse format to new processing model. These sections are domain-correct but reference atoms/passages.
6. **§3 Output Contract** — Redesign excerpt record for new architecture (div_id not passage_id, segment references not atom references). Separate core vs §4.B fields.
7. **§4.B Transformative Capabilities** — Review which are still relevant, remove atomization-engine dependencies, mark clearly as deferred.
8. **§6–§8 Consensus, Errors, Config** — Adapt to new model.
9. **§9–§10 Implementation State, Test Requirements** — Rewrite for correct starting point and test plan.

### One section per prompt

Each section gets its own deep analysis response. The architect reads the current SPEC section, the relevant governing documents (normalization contracts, architecture decision, experiment results), and produces a rewritten section with full reasoning for every design choice.

## Read First (Fresh Session)

1. `reference/archive/sessions/reviews/excerpting_spec_review.md` — the 16 findings
2. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — committed architecture + three-phase internal model
3. `engines/normalization/contracts.py` — the ACTUAL input (NormalizedManifest, ContentUnit, DivisionNode)
4. `experiments/architecture_test/run_tests.py` — the VALIDATED LLM approach (Approach B prompts + schemas)
5. `experiments/format_diversity_test/results/RUN_SUMMARY.md` — MAX_TOKENS finding + segment count data
6. `experiments/architecture_test/extract_divisions.py` — the VALIDATED division assembly logic
7. `engines/excerpting/SPEC.md` — current SPEC (to be rewritten section by section)
8. `engines/excerpting/contracts.py` — current contracts (to be updated after SPEC rewrite)
9. `KNOWLEDGE_INTEGRITY.md` — T-1 through T-7 threats (every section must defend against these)

## Design Decisions Already Made

- **5-engine pipeline.** Source → Normalization → Excerpting → Taxonomy → Synthesis.
- **Passaging absorbed.** Division assembly, merging (<50w), splitting (>5000w) are internal Phase 1.
- **Atomization absorbed.** LLM classify-then-group (Approach B) is internal Phase 2.
- **D-011 = division containment.** Excerpts cannot span division/chunk boundaries.
- **Two-phase LLM validated.** Approach B ≥ A in 23/23 tested divisions across 7 genres.
- **MAX_TOKENS = 32768+** for classify step on >2000w divisions.
- **All LLM calls through OpenRouter.** Model: anthropic/claude-opus-4.6.
- **Multi-model consensus** for self-containment and school attribution.
- **§4.B capabilities are deferred.** Core engine first, transformative capabilities later.

## Do NOT Do

- Do NOT review the SPEC as a whole in a single pass — section by section only.
- Do NOT preserve the atom-as-input model. The input is normalized packages.
- Do NOT keep passage_id. The processing unit is division (or chunk).
- Do NOT write implementation code. The SPEC defines behavior; CC implements.
- Do NOT skip domain research. Every scholarly convention claim must be verified.
- Do NOT defer findings. Every issue in a section is fixed before moving to the next.
