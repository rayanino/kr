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
7. **Multi-layer text identification (CRITICAL).** Many sources are multi-layer compositions: matn (Layer 1) + sharh (Layer 2) + hashiyah (Layer 3) + tahqiq notes (Layer 4). Each layer has a different author and time period. The normalization engine must identify these layers using format-specific markup (bold, brackets, font size, "قال المصنف" markers). If layers aren't identified here, the excerpting engine will misattribute text — a scholarly integrity violation. See DOMAIN.md "The Multi-Layer Text Problem."
8. **Versified text structure.** Some sources are in verse form (منظومات like الألفية). Each بيت (couplet) is a self-contained unit with two hemistichs. The normalization engine must detect verse structure and preserve verse numbering. See DOMAIN.md "Versified Texts."
9. **Diacritics (tashkil) preservation is MANDATORY.** Arabic diacritical marks carry semantic weight — "عِلْم" (knowledge) vs. "عَلَم" (flag) are the same word without diacritics. Many scholarly texts include diacritics on ambiguous words; tahqiq editors add them systematically. The normalization engine must PRESERVE all diacritics — stripping them is information destruction that makes downstream processing harder. See DOMAIN.md "Arabic as a Processing Language."
10. **Book structural format detection.** Sources come in multiple formats: prose, verse, Q&A (مسائل), tabular disagreement catalogs, dictionary format. The normalization output should tag the structural format so downstream engines can apply format-appropriate processing. See DOMAIN.md "Book Structures Beyond Prose."
11. **Page boundary preservation (CRITICAL).** Scholars cite by volume and page number: "المغني vol.3 p.245." Every excerpt must carry a physical citation the owner can verify. The normalization engine must preserve page boundaries from the source format (Shamela HTML page markers, PDF pages, individual photo pages). Page numbers must survive as metadata through passaging and excerpting. See DOMAIN.md "Physical Reference Preservation."
