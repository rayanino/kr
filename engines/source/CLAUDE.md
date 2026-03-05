# Source Engine — محرك المصادر

**Responsibility:** Discovering, identifying, acquiring, freezing, and documenting raw knowledge sources (§2.2).
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Required Reading
1. This engine's SPEC.md (the authoritative document)
2. VISION.md §7 (source pipeline architecture), §2.2, §2.5
3. Output boundary: frozen source + metadata → normalization engine

## What This Engine Does
- Acquires sources from any format (Shamela, PDF, manual input, etc.)
- Assigns three-tier identity: `source_id`, `work_id`, `canonical_id` (D-024)
- Freezes source immediately upon acquisition (§2.5)
- Extracts and enriches metadata (author, school, dates, work relationships)
- Maintains three registries: sources.json, works.json, scholars.json
- Evaluates trustworthiness via 5-factor weighted scoring

## Current State
Legacy ABD code (D-019: zero design authority). Works for Shamela intake only.
Code: `src/` (intake.py 1476L, enrich.py 580L, corpus_audit.py 228L).
Tests: 112 tests in `tests/`.

## Commands
```
cd engines/source && python -m pytest tests/ -q
```

## Transformative Capabilities (§4.B)
1. **OpenITI corpus enrichment** for scholar authority bootstrapping (§4.B.1)
2. **Bibliographic intelligence** from minimal input (§4.B.2)
3. **Citation network discovery** [NOT YET IMPLEMENTED] (§4.B.3)
4. **Acquisition gap analysis** [NOT YET IMPLEMENTED] (§4.B.4)

## Key Constraints
1. **Freezing immediate and absolute (§2.5):** frozen before any processing, never modified
2. **Not Shamela-only (D-019):** design for ALL scholarly source types
3. **Manual acquisition first-class (D-020):** iPhone photos, manual downloads are primary paths
4. **Metadata is synthesis fuel (D-023):** biography, dates, schools, relationships enable scholarly narratives
5. **Multi-layer detection (D-030):** identify matn+sharh composition, attribute each layer's author
6. **Work vs. source distinction (D-024):** same work, different tahqiq = different sources
7. **Fail-loud (D-033):** uncertain identification → human gate, not silent default
