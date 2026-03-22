# Excerpting Engine — محرك الاقتطاف

**Responsibility:** Transforming normalized text divisions into self-contained, attributed, metadata-rich excerpts — the building blocks of Rayane's knowledge library.
**Phase:** 2 (source-agnostic, below the normalization boundary).
**Position:** Third engine in the pipeline: Source ✅ → Normalization ✅ → **Excerpting** → Taxonomy → Synthesis.

## What This Engine Absorbs

The excerpting engine absorbs the responsibilities of two previously separate engines:
- **Passaging** (deterministic): cross-page text assembly, division merging (<50w), division splitting (>5000w), format-specific handling
- **Atomization/Classification** (LLM-driven): segment classification by scholarly function, teaching unit boundary detection

These are internal phases, not separate engines. The architecture decision (commit 5636ceb) documents the evidence and rationale.

## Input Boundary

Normalized packages from the normalization engine:
- `library/sources/{source_id}/normalized/manifest.json` — NormalizedManifest (division tree, layer map, structural format, quality report)
- `library/sources/{source_id}/normalized/content.jsonl` — ContentUnit stream (one per physical page: primary_text, text_layers, footnotes, structural_markers, boundary_continuity, discourse_flow)

See `engines/normalization/contracts.py` for the authoritative schema definitions.

## Output Boundary

Draft excerpt stream consumed by the taxonomy engine:
- `library/sources/{source_id}/excerpts/excerpts.jsonl` — one ExcerptRecord per line

See `engines/excerpting/contracts.py` for the authoritative schema definitions.

## Internal Architecture (Three Phases)

**Phase 1 — Deterministic Preprocessing (absorbs passaging):**
- Walk division tree → identify leaf divisions
- Assemble text from content units using boundary_continuity separators
- Merge tiny divisions (<50w) with adjacent siblings
- Split oversized divisions (>5000w) at structural markers
- Rebase text_layers to assembled-text offsets
- Aggregate content_flags, collect footnotes
- ~800 lines estimated, independently unit-testable

**Phase 2 — LLM Teaching Unit Extraction (absorbs atomization):**
- Phase 2a: LLM classifies segments by scholarly function (Approach B classify step)
- Phase 2b: LLM groups segments into self-contained teaching units with self-containment evaluation
- Two-phase approach validated: B ≥ A in 23/23 experiment divisions
- MAX_TOKENS ≥ 32768 required for classify step on >2000w text
- D-011 enforced: teaching units cannot span division/chunk boundaries

**Phase 3 — Metadata Enrichment:**
- Deterministic: author attribution from text_layers, content type aggregation, evidence assembly, physical pages
- LLM-driven: topic classification, school attribution, quoted scholar resolution, takhrij extraction, terminology variants
- Multi-model consensus on self-containment and school attribution

## Current State

**SPEC:** Under rewrite. Original SPEC (98KB) was written for old 7-engine architecture and was BLOCKED in review (16 findings). Section-by-section rewrite in progress. See `reference/archive/sessions/reviews/excerpting_spec_review.md`.

**Contracts:** 557 lines. Will be updated after SPEC rewrite to reflect new architecture (div_id replaces passage_id, segments replace atoms as internal concept).

**Code:** No implementation code. Only ABD-era files (historical reference).

**Tests:** None.

## Key Integrity Concerns

This engine is where text becomes knowledge. The highest-risk corruption threats:
- **T-2 (Attribution Error):** Multi-layer texts must be attributed to the correct author. Decontextualized quotation is the most dangerous failure mode.
- **T-4 (Context Loss):** Self-containment is the primary quality gate. An excerpt that can't be understood alone is a broken piece of knowledge.
- **T-6 (Metadata Poisoning):** Wrong school, wrong science, wrong author propagates to every downstream product.

## Required Reading

1. `NEXT.md` — current task directive
2. `reference/archive/sessions/reviews/excerpting_spec_review.md` — review findings
3. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — why this architecture
4. `engines/normalization/contracts.py` — what this engine receives
5. `KNOWLEDGE_INTEGRITY.md` — the threats this engine must defend against
6. `experiments/architecture_test/run_tests.py` — the validated LLM approach
7. `experiments/format_diversity_test/results/RUN_SUMMARY.md` — operational findings
