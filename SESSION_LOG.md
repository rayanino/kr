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

---

## Session 9: Passaging Engine CREATIVE
**Date:** 2026-03-06
**Type:** CREATIVE
**Engine:** Passaging (محرك التقطيع)

### What Was Done

**Research phase:**
- Surveyed Arabic NLP text segmentation landscape (ArabicNLP 2024-2025, KITAB project, OpenITI mARkdown)
- Studied KITAB's passim algorithm: 300-word milestones, Smith-Waterman alignment for text reuse detection
- Researched RAG chunking strategies (2024-2025): semantic chunking, adaptive chunking (87% vs 13% accuracy over fixed-size), late chunking, proposition-based chunking
- Examined OpenITI mARkdown structural tagging: `### |` for chapters, `### ||` for sections, paragraph tags, milestone markers

**Key research insight:** Adaptive chunking that respects document structure dramatically outperforms fixed-size and even semantic-only approaches. This validates KR's division-guided approach AND motivates the new content census-driven adaptation capability.

**Creative output — SPEC rewrite (502 → 643 lines):**

1. **§2 input contract updated:** Added content_census and tahqiq_topology from normalization manifest, quality_report for boundary confidence adjustment
2. **§4.A.2 Arabic cross-page joining examples:** Two concrete Arabic examples (mid-word break on المبتدأ, sentence-boundary break), taa marbuta/hamza page boundary handling
3. **§4.A.4 scholarly keyword scan expansion:** Organized 25+ Arabic keywords into 5 categories (ordinal, new-topic, contrastive, evidence, position), with concrete مغني example showing splitting at position boundaries
4. **§4.A.4 Arabic sentence detection specification:** Four-tier priority system (terminal punctuation, paragraph breaks, Quran citation boundaries, long comma-span heuristic), explicit rule that Arabic comma is NOT sentence-terminal
5. **§4.A.4 isnad chain integrity rule:** Pattern-based detection of حدثنا/أخبرنا/أنبأنا chains, never split isnad+matn across passages
6. **§4.A.6 Q&A markers expanded:** Added فأجاب, الجواب:, قيل له:, وسأله; concrete example from مجموع الفتاوى
7. **Arabic word count method specified:** Whitespace tokenization (matching KITAB convention), not morphological tokenization
8. **NEW §4.B.5 — Content Census-Driven Adaptive Passaging:** Uses normalization content census to adapt passage size, splitting thresholds, commentary sensitivity, and footnote adjustment per-source. Concrete formulas with worked examples (شرح ابن عقيل → 643 effective target)
9. **NEW §4.B.6 — Scholarly Argument Boundary Detection:** Pattern-based state machine detecting مسألة → evidence → counter → refutation → conclusion structure. Boundary protection rule (arguments up to 150% hard max preserved intact). Concrete example from المغني
10. **New error codes:** PSG_ARGUMENT_OVERSIZED, PSG_ADAPTATION_FAILED, PSG_ISNAD_SPLIT
11. **New test requirements:** Isnad chain preservation (4 tests), adaptation formulas (4 tests), argument detection (5 tests)
12. **New gold baseline:** Masala-block source for argument boundary verification

### Quality Metrics
- Creative verification score: 90/100 (6 capabilities, 3 named technologies, examples, 0 vague phrases)
- Invention ratio: 89% (32 invention signals, 4 correction signals)
- Assessment: CREATIVE

### Decisions
- Arabic word counting uses whitespace tokenization (not morphological) — matches KITAB/OpenITI convention and how scholars estimate text length
- Isnad chains treated as atomic units — splitting a narration chain is worse than an oversized passage
- Argument preservation can expand passages up to 150% of hard max — a complete argument in one passage is more valuable than two broken halves
- Content census adaptation formulas use conservative multipliers (0.3, 15-20-30%) — aggressive adaptation risks unexpected behavior on edge cases

### No Domain Questions This Session

