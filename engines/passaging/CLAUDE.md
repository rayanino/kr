# Passaging Engine — محرك التقطيع

**Responsibility:** Segmenting normalized content into passages for downstream processing.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Third engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (1,037 lines — the authoritative specification)
2. This engine's `contracts.py` (556 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. Input boundary: normalized package from normalization engine
6. Output boundary: passage stream → atomization engine

## Current State

**SPEC:** 1,037 lines. Has been through multiple refinement passes but has 25 HIGH-severity defects (highest in the repo). Needs substantive Step 1 work, not just core extraction. §4.A requires rewriting for core-only focus and defect resolution.

**Contracts:** 556 lines. Imports from normalization contracts (the only cross-engine import currently).

**Code:** 22 pre-protocol stub files, 544 total lines. Includes 6 strategy variants (prose, verse, Q&A, masala, dictionary, commentary) — only prose and commentary-with-layers are core. Deferred strategies must be pruned or disabled during Step 3.

**Tests:** None.

## What This Engine Does (Core Only)

- Receives normalized packages (manifest.json + content.jsonl)
- Selects strategy based on structural_format: prose or commentary-with-layers
- Splits text into passages targeting 200-800 Arabic words
- Preserves heading hierarchy, page boundaries, footnote associations
- Aligns commentary spans to base text segments (for multi-layer texts)
- Produces passage stream consumed by atomization engine
