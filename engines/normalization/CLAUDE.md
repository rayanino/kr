# Normalization Engine — محرك التطبيع

**Responsibility:** Transforming frozen sources from their native format into the universal normalized format (§2.2). One normalizer per source type.
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §7.5–§7.6 (normalization, boundary)
3. VISION.md §2.2 (engine definition), §2.5 (normalized package)
4. Input boundary: frozen source + source metadata from source engine
5. Output boundary: normalized package → passaging engine (crosses the normalization boundary)

## Current State
Legacy code migrated from ABD. Only a Shamela normalizer exists — ABD was Shamela-only. ABD design decisions have zero authority in KR (D-019). The SPEC defines what this engine SHOULD be, including normalizers for source types that don't exist yet.

Code: `engines/normalization/src/` (normalizers/normalize_shamela.py 1123L, discover_structure.py 2896L, validate_structure.py 333L).
Tests: 292 tests in `engines/normalization/tests/`.
Reference: 15 ABD-era docs in `engines/normalization/reference/` — describe what WAS built.

## Commands
```
cd engines/normalization && python -m pytest tests/
```

## Key Constraints
1. **One normalizer per source type** (§7.5): complexity is unlimited within a normalizer, but output must conform to universal schema.
2. **Structure discovery is normalization's job** (§7.5): structural signals exist in format-specific markup.
3. **Nothing format-specific crosses the boundary** (§7.6): the normalized package must be fully source-agnostic.
4. **Editor-author separation is critical.** Tahqiq editions contain editor footnotes, variant readings, manuscript notes, and commentary that are NOT the original author's words. If the normalization engine fails to separate these, the excerpting engine will attribute the editor's analysis to the original author — a scholarly integrity violation. The normalized package must clearly distinguish primary text from editorial apparatus.
5. **Text fidelity signal.** Different source types produce different quality text. The normalization engine must produce a confidence signal alongside text: structured digital text → high fidelity, professional scans → medium (OCR error patterns), iPhone photos → variable. This signal flows downstream to affect excerpt flagging, synthesis weighting, and scholar interface warnings.
6. **Metadata pass-through (D-023).** The normalized package must carry ALL source metadata through to downstream engines. The synthesizer is the ultimate consumer.
