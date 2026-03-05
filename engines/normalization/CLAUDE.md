# Normalization Engine — محرك التطبيع

**Responsibility:** Transforming frozen sources from their native format into the universal normalized format (§2.2). One normalizer per source type. Guardian of the normalization boundary.
**Phase:** 1 (source-format-specific, above the normalization boundary).
**SPEC:** `engines/normalization/SPEC.md` (664 lines, complete §1-§10)

## Required Reading
1. This engine's SPEC.md — the authoritative specification
2. VISION.md §7.5–§7.6 (normalization, boundary)
3. VISION.md §2.2 (engine definition), §2.5 (normalized package)
4. Input boundary: frozen source + source metadata from source engine (see source engine SPEC §3)
5. Output boundary: normalized package → passaging engine (crosses the normalization boundary)

## Architecture Summary
- Dispatcher-normalizer pattern: dispatcher reads `source_type`, selects normalizer
- 7 normalizer types defined: shamela_html (existing), pdf_text, pdf_scanned, image_scan, epub, plain_text, owner_authored
- Output: normalized package = manifest.json + content.jsonl at `library/sources/{source_id}/normalized/`
- OCR: Mistral OCR 3 (primary) + Qari-OCR (Arabic diacritics specialist) + dual-OCR comparison mode (D-028)
- Schema: source_id reference model — no metadata duplication (D-029)

## Key Constraints
1. **Nothing format-specific crosses the boundary** (§7.6). The normalized package is fully source-agnostic.
2. **Multi-layer text identification (CRITICAL).** Matn/sharh/hashiyah/tahqiq layers identified with character-level segments and confidence scores. Conservative default: attribute uncertain text to commentary author, not matn author (D-030).
3. **Diacritics preservation is ABSOLUTE.** No Unicode normalization of tashkeel.
4. **Footnote separation and classification.** Footnotes typed as tahqiq_editor/author_original + fine-grained taxonomy (variant_reading, hadith_takhrij, cross_reference, biographical_note, linguistic_note, correction_note).
5. **Page boundary preservation.** `unit_index` is the ONLY positional identifier for Phase 2 engines. Physical page numbers are display metadata only.
6. **Text fidelity per page.** Every content unit carries its own fidelity score, not just source-level.
7. **Metadata pass-through (D-023).** source_id reference model — Phase 2 engines access source metadata via reference, not duplication.
8. **Universal footnote markers.** `⌜N⌝` format in primary_text (D-031).

## Current State
Legacy code migrated from ABD. Only Shamela normalizer exists (1123L). Structure discovery exists (2896L). 292 tests pass. Major gaps: no multi-layer detection, no footnote classification, no non-Shamela normalizers, no OCR pipeline, no KR output schema.

## Commands
```
cd engines/normalization && python -m pytest tests/
```

## Key Decisions
- D-028: OCR strategy (Mistral OCR 3 + Qari-OCR)
- D-029: source_id reference model for normalized packages
- D-030: Conservative layer default (commentary author)
- D-031: Universal footnote reference marker format
