# Normalization Engine — محرك التسوية

**Responsibility:** Transforming frozen sources from their native format into the universal normalized format. One normalizer per source type. Guardian of the normalization boundary.
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Second engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (2,006 lines — the authoritative specification)
2. This engine's `contracts.py` (697 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. `KNOWLEDGE_INTEGRITY.md` — especially T-1 (silent text corruption)
6. Input boundary: frozen source + metadata from source engine
7. Output boundary: normalized package → passaging engine (crosses the normalization boundary)

## Current State

**SPEC:** 2,006 lines. Most mature SPEC in the repo (4 refinement passes). §4.A content has been through PRECISION and HARDENING — core extraction should be surgical (move §4.B to deferred, add extension hooks, verify §4.A is implementation-ready). Do NOT rewrite refined §4.A content.

**Contracts:** 697 lines. Boundary with source engine has known mismatches — tracer bullet addresses this.

**Code:** 9 pre-protocol stub files, 567 total lines. Includes dispatcher, Shamela normalizer skeleton, layer detector, content census, writer, validation, error definitions. More substantive than other engines' stubs but still not functional.

**Tests:** 1 test file (test_kr_output.py) with structure but no passing tests.

## What This Engine Does (Core Only)

- Receives frozen source + metadata from source engine
- Dispatches to format-specific normalizer (Shamela HTML only for Stage 1)
- Extracts content units with heading hierarchy, page boundaries, footnotes
- Detects text layers (matn vs sharh vs hashiyah) using CSS classes — CORE, not deferred
- Produces manifest.json + content.jsonl in the universal normalized format
- All downstream engines consume this format — nothing below the normalization boundary sees source-specific structure
