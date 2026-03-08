# Source Engine — محرك المصادر

**Responsibility:** Acquiring raw sources, assigning identifiers, extracting and inferring metadata, freezing originals, evaluating trustworthiness, and producing the metadata record that every downstream engine consumes.
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. This engine is first in pipeline order and bootstraps the shared components (consensus, human_gate, scholar_authority, validation).

## Required Reading

1. This engine's `SPEC.md` (1,465 lines — the authoritative specification)
2. This engine's `contracts.py` (825 lines — Pydantic input/output schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process (Step 0-4)
4. `reference/TESTING_FRAMEWORK.md` — test architecture (5a/5b/5c dimensions)
5. `KNOWLEDGE_INTEGRITY.md` — 7 corruption threats this engine must prevent
6. `SILENT_FAILURES.md` — 7 failure patterns to check against
7. Output boundary: frozen source + metadata → normalization engine

## Current State

**SPEC:** 1,465 lines. Has been through prior refinement but needs core extraction (Step 1) — §4.B features and non-core formats must be deferred with extension hooks. §4.A needs rewriting for core-only focus. Immature by ENGINE_PROTOCOL's criteria.

**Contracts:** 825 lines. Written against the full SPEC including deferred features. Will be pruned during core extraction. Boundary with normalization has known mismatches (22+ fields) — the tracer bullet (Step 0) addresses this.

**Code:** 27 pre-protocol stub files, 265 total lines. These are SPEC-derived placeholders, not working implementations. They include deferred features. The tracer bullet uses them as starting points; Step 3 replaces them with real code.

**Tests:** None.

**Shared component bootstrap:** This engine builds the first real implementations of consensus, human_gate, scholar_authority, and validation. See ENGINE_PROTOCOL.md engine-specific notes for the minimum viable method signatures needed.

## What This Engine Does (Core Only)

- Acquires sources from Shamela HTML exports and plain text (2 formats for Stage 1)
- Assigns three-tier identity: source_id, work_id, canonical_id (D-024)
- Extracts metadata from format-specific markup
- Infers metadata via LLM when extraction is insufficient (multi-model consensus)
- Detects duplicates via composite key matching
- Freezes the raw source immediately upon acquisition (SHA-256 hash)
- Evaluates trustworthiness: 3-tier classification (verified / flagged / unknown)
- Produces metadata.json consumed by the normalization engine

## Key Domain Concepts

- **tahqiq**: Critical scholarly edition. The muhaqiq (editor) is NOT the author.
- **source_format**: Shamela HTML has specific structure (info.html + content.html)
- **trust_tier**: Based on publisher reputation, tahqiq quality, manuscript lineage
- **Three-tier ID**: source_id (this specific file), work_id (this book), canonical_id (this scholar's identity)
