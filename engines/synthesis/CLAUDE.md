# Synthesis Engine — محرك التركيب

**Responsibility:** Generating encyclopedic scholarly entries from placed excerpts. This is the engine that produces the knowledge products the owner actually reads.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Seventh and final engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (918 lines — the authoritative specification)
2. This engine's `contracts.py` (565 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. `reference/ENTRY_EXAMPLE.md` — THE quality target. Shows what a finished entry looks like.
6. `reference/DOMAIN.md` — scholarly methodology concepts
7. Input boundary: placed excerpts + tree structure from taxonomy engine
8. Output boundary: entries → Scholar Interface (Stage 2)

## Current State

**SPEC:** 918 lines. Has been through 3 refinement stages (CREATIVE, PRECISION, HARDENING). Has 6 HIGH-severity defects. Core extraction needed — full scholarly narrative quality is the target even for v0.0.1, but advanced features (staleness detection, versioning, regeneration) are deferred.

**Contracts:** 565 lines.

**Code:** No implementation code. Only an empty __init__.py.

**Tests:** None.

## What This Engine Does (Core Only)

- Compiles placed excerpts into scholarly entries with temporal ordering, school attribution, and traceability (all claims to excerpt IDs)
- Every claim tagged with grounding_type: source_grounded | metadata_derived | analytical (D-040)
- Cross-provider entailment verification: the model that generates cannot also verify (T-5 prevention)
- Quality bar: structured compilation with narrative, not flat bullet-point compilation
- Builds a minimal entry viewer (scripts/render_entry.py) at Step 4 for owner review
