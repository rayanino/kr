# Excerpting Engine — محرك الاقتطاف

**Responsibility:** Grouping atoms into self-contained excerpts enriched with metadata for synthesis.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Fifth engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (1,038 lines — the authoritative specification)
2. This engine's `contracts.py` (557 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. Input boundary: atom stream from atomization engine
6. Output boundary: excerpt stream → taxonomy engine

## Current State

**SPEC:** 1,038 lines. Has been through PRECISION and HARDENING. 0 HIGH-severity defects — the cleanest SPEC in the repo. Core extraction should be surgical.

**Contracts:** 557 lines.

**Code:** No implementation code. Only an empty __init__.py.

**Tests:** None.

## What This Engine Does (Core Only)

- Groups atoms into candidate excerpts using LLM boundary detection
- Evaluates self-containment: can each excerpt be understood without surrounding context?
- Self-containment is the highest-risk LLM task in the pipeline (T-4: Context Loss)
- Enriches excerpts with metadata: author attribution, school, evidence references
- Produces excerpt stream consumed by taxonomy engine
