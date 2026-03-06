# Taxonomy Engine — محرك التصنيف

**Responsibility:** Placing excerpts at taxonomy leaves, managing tree lifecycle (construction, evolution, rollback), computing coverage analytics, and maintaining the structural knowledge graph (prerequisite edges, cross-science links, terminology synonyms).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md (source of truth — 562 lines, all 10 sections)
2. VISION.md §4 (science trees), §5.3 (cross-topic content), §5.5 (one-per-source diagnostic)
3. VISION.md §9 (human gates — taxonomy is a primary gate site)
4. Input boundary: draft excerpts from excerpting engine (see excerpting SPEC §3)
5. Output boundary: placed excerpts + coverage data + tree structure → synthesizing engine

## Current State
Legacy evolution code migrated from ABD. ABD design decisions have zero authority in KR (D-019).

Code: `engines/taxonomy/src/evolve_taxonomy.py` (2377L) — evolution signal detection, proposal generation, YAML modification.
Tests: 109 tests in `engines/taxonomy/tests/`.
Reference: 1 ABD-era doc (reference only).
Taxonomy trees: `library/sciences/` (5 sciences with tree.yaml files — nahw, sarf, imlaa, aqidah, balagha).

## Key Architecture

### Placement (§4.A.1)
Two-stage: candidate generation (3 sources: excerpting proposal + LLM topic search + embedding similarity) → candidate ranking (LLM scoring 0–1). Thresholds: ≥0.8 auto-approve with policy, 0.5–0.8 human gate, <0.5 unplaceable + evolution signal. Multi-model consensus for ambiguous range.

### Tree Construction (§4.A.3)
Four-phase: Research (analyze TOCs of authoritative works) → Draft (generate tree with narrative ordering + prerequisites) → Validation (test against real content) → Commitment (version and activate).

### Evolution (§4.A.5–§4.A.7)
Five signal types → accumulation threshold → proposal generation → four §4.4 invariant checks → human gate → application with atomic redistribution. Full rollback capability.

### Coverage (§4.A.6)
Six gap types: school, source diversity, temporal, evidence, prerequisite, empty leaf. Per-leaf scholarly landscape data. Duplicate cluster detection via embeddings.

### Transformative Capabilities (§4.B)
1. **Topic significance scoring** — structural importance within a science (prerequisite dependency + cross-reference frequency + source breadth + LLM assessment). [NOT YET IMPLEMENTED]
2. **Difficulty estimation** — cognitive load per topic for study path optimization. [NOT YET IMPLEMENTED]
3. **Corpus-driven tree construction** — generate draft trees from computational analysis of multiple works' TOCs. [NOT YET IMPLEMENTED]

## Key Constraints
1. Excerpts placed only at leaves (§2.3).
2. Trees branch by topic, never by school (§4.5).
3. Evolution always human-gated (§9.3).
4. All upstream metadata preserved on placed excerpts (D-023).
5. Every error logged, never silently swallowed (D-033).
6. Tree version history never pruned.

## External Dependencies
NetworkX (tree/DAG operations), sentence-transformers (embeddings), Instructor (structured LLM output), CAMeL Tools (Arabic normalization), OpenRouter/Anthropic/OpenAI APIs, PyYAML.

## SPEC Refinement Status
- Cycle 0 (not yet started)
- Implementation-ready: NO — refinement required before implementation
