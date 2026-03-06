# Session Log — خزانة ريان

## Session 7 — Normalization Engine HARDENING
**Date:** 2026-03-06
**Type:** HARDENING
**Engine:** Normalization

### What Was Done

Systematic threat enumeration against KNOWLEDGE_INTEGRITY.md for every §4.A processing step. Identified 8 coverage gaps where corruption paths had no detection mechanism. Patched all 8:

1. **Atomic write guarantee (Pass 6).** Added temp-directory + atomic-rename procedure to prevent partial packages on disk. New error code `NORM_WRITE_FAILED`.
2. **Unit index integrity (§5 check #7).** Added validation that unit_index forms contiguous 0-based sequence. New error code `NORM_UNIT_INDEX_VIOLATION`.
3. **Diacritics preservation verification (§5 check #8).** Added character-class comparison between source and output Arabic diacritics for digital-text sources. New error code `NORM_DIACRITICS_DRIFT`.
4. **Format-specific input validation (§5 check #9).** Each normalizer validates input matches expected format before processing. New error code `NORM_NO_TEXT_LAYER`.
5. **Footnote separator absence handling (§4.A.2 Pass 2).** Explicit rule: absent separator → treat entire page as primary text, log info. New error code `NORM_FOOTNOTE_SEPARATOR_ABSENT`.
6. **Image page ordering conflict resolution (§4.A.4).** Defined precedence: filename sort authoritative, OCR page numbers for cross-reference. New error code `NORM_PAGE_ORDER_CONFLICT`.
7. **Tighter coverage check for deterministic sources (§5 check #2).** Shamela/text PDF: exact page count match (minus explicitly skipped pages), not ±10%.
8. **Contracts updated.** FootnoteType enum expanded for §4.B.4 fine-grained types. Added VariantReadingData, TakhrijData, BiographicalNoteData, CorrectionNoteData models.

Added 2 Arabic text examples: §4.B.1 (content-based layer inference in شرح الورقات), §4.B.4 (4-footnote classification from المغني tahqiq edition).

### Quality Metrics
- HIGH defects: 6 → 4 (target: ≤6) ✓
- Creative score: 90/100 maintained ✓
- Arabic examples added: 2 (target: ≥2) ✓
- New error codes: 6
- New §5 validation checks: 3
- SPEC lines: 1013 → 1073

### Decisions
- Atomic write uses temp directory + rename (not file-level locking) — simpler, portable, sufficient for single-writer.
- Diacritics drift check is fatal (not warning) — any diacritic loss is a code bug, not a data quality issue.
- Filename sort is authoritative for image sets over OCR page numbers — captures owner's physical sequencing intent.

### No Domain Questions This Session

## Session 8 — Normalization Engine IMPL_PREP
**Date:** 2026-03-06
**Type:** IMPLEMENTATION_PREP
**Engine:** Normalization

### What Was Done

Prepared the normalization engine directory for Claude Code implementation. This is the last Claude Chat session for the normalization engine.

**Phase 1 — Contract alignment verification:**
- Verified all 16 fields the normalization engine reads from SourceMetadata exist in source contracts.py.
- Verified StructuralFormat enum values match exactly between source and normalization contracts.
- Identified one mapping note: source TextLayer uses string "tahqiq" → normalization LayerType uses "tahqiq_note". Documented in IMPL_BRIEF.

**Phase 2 — Test fixture gap analysis:**
- Existing html_export_minimal fixture uses NON-STANDARD format (div.page) not actual Shamela format (div.PageText). Cannot be used with ABD normalizer code.
- Created new fixture `engines/normalization/tests/fixtures/shamela_ibn_aqil.htm` in REAL Shamela export format: PageText divs, PageHead headers, PageNumber spans, hr footnote separators.
- Fixture covers: multi-page, footnotes (numbered_parens), bold matn signal, HTML-tagged headings, ZWNJ heading, verse detection, Quran citation, diacritics, no-separator page.
- Gold baseline directory created with README documenting what baselines are needed.
- ABD tests (204 test functions) are in archive; equivalent tests needed in new structure.

**Phase 3 — Directory skeleton:**
- Created module stubs with SPEC-referencing docstrings:
  - `src/errors.py` (complete — all 20 error codes, severity mapping, NormalizationError class)
  - `src/normalizers/base.py` (complete — BaseNormalizer interface)
  - `src/dispatcher.py` (stub — normalizer registry + dispatch logic)
  - `src/normalizers/shamela.py` (stub — 6-pass pipeline)
  - `src/validation.py` (stub — 8 validation check functions)
  - `src/writer.py` (stub — atomic write procedure)
  - `src/layer_detector.py` (stub — multi-layer detection)
  - `src/content_flagger.py` (stub — content type flagging)
  - `src/content_census.py` (stub — statistical profiling)
- Created test stubs: `tests/test_kr_output.py` with 30 test methods organized by SPEC §10 categories.

**Phase 4 — Implementation brief:**
- Wrote `engines/normalization/IMPL_BRIEF.md` — 6-step build plan for Claude Code.
- Steps: (1) output schema upgrade + atomic writer, (2) validation framework, (3) footnote classification, (4) multi-layer detection, (5) content flagging, (6) content census.
- Each step specifies: what to do, field mappings, thresholds, test criteria.
- Documents ABD→KR field mapping table, constraints, dependencies, final file layout.

### Quality Metrics
- Contract alignment: ✓ All fields verified
- Test fixture: ✓ Created in real Shamela format (6 pages, covers key scenarios)
- Module stubs: 9 files created (2 complete, 7 stubs with SPEC references)
- Test stubs: 30 test methods across 10 test classes
- IMPL_BRIEF: 6 implementation steps with concrete build criteria

### Decisions
- errors.py and base.py implemented fully (not stubs) since they're pure definitions with no behavioral complexity — saves Claude Code a step.
- New Shamela fixture created rather than fixing html_export_minimal — the existing fixture may be useful for other purposes and shouldn't be changed.
- IMPL_BRIEF uses 6-step incremental build rather than big-bang — each step is independently testable.

### No Domain Questions This Session
