# Normalization Engine — محرك التطبيع

**Responsibility:** Transforming raw sources from their native format into the universal normalized format (§2.2).
**Phase:** 1 (source-format-specific, above the normalization boundary). This engine's output crosses the boundary.

## Required Reading
1. This engine's SPEC.md
2. VISION.md §7.5 (source normalization), §7.6 (the normalization boundary)
3. VISION.md §2.2 (engine definition, normalization boundary)
4. Input: frozen source + source metadata (from source engine, Phase 1 internal)
5. Output schema: `schemas/normalized_package` (the normalization boundary expressed as data)

## Current State
Status: Not started. ABD codebase has Shamela normalizer (`tools/normalize_shamela.py`) and structure discovery (`tools/discover_structure.py`) to be restructured into `engines/normalization/src/normalizers/` per §12.2.
Tests: 0 passing, 0 failing.
Known issues: Only Shamela source type supported. Per-source-type normalizer subdirectory structure not yet created.

## Commands
```
cd engines/normalization && python -m pytest tests/
```

## Key Constraints
1. **One normalizer per source type** (§7.5): each supported format gets its own module in `src/normalizers/`. Normalizer complexity is unlimited as long as output conforms to the universal schema.
2. **Structure discovery is part of normalization** (§7.5): structural signals exist in format-specific markup available only before stripping.
3. **Output uniformity is absolute** (§7.5): all normalizers produce identical schema output. Phase 2 engines cannot distinguish between normalizers' output.
