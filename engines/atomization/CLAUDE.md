# Atomization Engine — محرك التذرية

**Responsibility:** Breaking passages into typed atoms — the smallest indivisible text units — classified by structural type and scholarly function.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Fourth engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (1,205 lines — the authoritative specification)
2. This engine's `contracts.py` (676 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. Input boundary: passage stream from passaging engine
6. Output boundary: atom stream → excerpting engine

## Current State

**SPEC:** 1,205 lines. Has been through PRECISION (partially). Has 9 HIGH-severity defects. Needs core extraction and defect resolution at Step 1.

**Contracts:** 676 lines.

**Code:** 26 pre-protocol stub files, 866 total lines. Most extensive stubs in the repo. Includes advanced features (fingerprinting, distribution analytics, rhetorical analysis) that are deferred. Must be pruned to core during Step 3.

**Tests:** None.

## What This Engine Does (Core Only)

- Receives passage stream from passaging engine
- Segments each passage into non-overlapping atoms via a multi-phase pipeline
- Classifies each atom on two dimensions: structural type + scholarly function
- The LLM does the primary classification work — Step 2 research is critical to verify LLM accuracy on scholarly function classification before building
- Produces atom stream consumed by excerpting engine
