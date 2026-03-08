# Taxonomy Engine — محرك التصنيف

**Responsibility:** Placing excerpts at taxonomy leaf nodes, managing tree structure, computing coverage analytics.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Sixth engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (945 lines — the authoritative specification)
2. This engine's `contracts.py` (491 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. Input boundary: excerpt stream from excerpting engine
6. Output boundary: placed excerpts + tree structure → synthesis engine

## Current State

**SPEC:** 945 lines. Has been through PRECISION and HARDENING. 0 HIGH-severity defects. Core extraction should be surgical.

**Contracts:** 491 lines.

**Code:** No implementation code. Only an empty __init__.py.

**Tests:** None.

**Prerequisite:** The engine needs a parsed science tree to place excerpts into. Five sciences have tree.yaml files in library/sciences/ (nahw, aqidah, balagha, sarf, imlaa), but these were created without owner validation. The owner must validate at minimum the nahw tree before Step 3.

## What This Engine Does (Core Only)

- Places each excerpt at the best-matching taxonomy leaf using two-stage placement
- Uses multi-model consensus for ambiguous placements
- Triggers human gate for cross-science placements
- Computes coverage analytics (density, gaps) per leaf
- Produces placed excerpts consumed by synthesis engine
