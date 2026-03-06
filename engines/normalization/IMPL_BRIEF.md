# Normalization Engine — Implementation Brief

**Audience:** Claude Code. This document tells you what to build, in what order, with what constraints.

**Read before coding:**
- `engines/normalization/SPEC.md` §4.A.2 (Shamela normalizer — the full behavioral spec)
- `engines/normalization/contracts.py` (Pydantic models — your output schema)
- `engines/normalization/src/errors.py` (error codes — already implemented)
- `engines/normalization/src/normalizers/base.py` (normalizer interface — already implemented)
- `reference/archive/abd_code/normalization/normalize_shamela.py` (ABD code to adapt)
- `reference/archive/abd_code/normalization/discover_structure.py` (structure discovery to integrate)
- `engines/normalization/reference/ABD_NORMALIZATION_SPEC.md` (ABD processing rules)
- `engines/normalization/reference/SHAMELA_HTML_REFERENCE.md` (HTML format documentation)

---

## What Exists Today

| File | Lines | Status |
|------|-------|--------|
| `contracts.py` | 475 | Complete — do not modify unless SPEC changes |
| `src/errors.py` | ~100 | Complete — all error codes defined |
| `src/normalizers/base.py` | ~55 | Complete — normalizer interface |
| `src/dispatcher.py` | ~70 | Stub — register ShamelaNormalizer after building it |
| `src/normalizers/shamela.py` | ~85 | Stub — implement the 6-pass pipeline |
| `src/validation.py` | ~100 | Stub — implement 8 validation checks |
| `src/writer.py` | ~45 | Stub — implement atomic write |
| `src/layer_detector.py` | ~40 | Stub — implement layer detection |
| `src/content_flagger.py` | ~30 | Stub — implement content flagging |
| `src/content_census.py` | ~40 | Stub — implement statistical profiling |
| ABD `normalize_shamela.py` | 1123 | Working ABD code — adapt, don't rewrite from scratch |
| ABD `discover_structure.py` | 2896 | Working ABD code — integrate for Pass 4 |
| ABD tests | ~2600 | Working tests — preserve and extend |

## Implementation Order

Build these steps sequentially. Each step must pass its tests before proceeding.

### Step 1: Output Schema Upgrade + Atomic Writer

**Goal:** Make the Shamela normalizer produce KR normalized packages instead of ABD JSONL.

**What to do:**
1. Copy ABD `normalize_shamela.py` into `src/normalizers/shamela.py` as the starting point.
2. Refactor the ABD output assembly (currently writes flat JSONL records with `book_id`, `matn_text`, `footnotes`) to produce `ContentUnit` objects (from `contracts.py`).
3. Assemble a `NormalizedManifest` with: source_id, normalizer_id (`kr.normalization.shamela_v2`), schema_version, total_content_units, structural_format, text_fidelity_summary, quality_report.
4. Implement `src/writer.py` — the atomic write procedure.
5. Register `ShamelaNormalizer` in `src/dispatcher.py`.

**Field mapping (ABD → KR):**

| ABD field | KR ContentUnit field | Notes |
|-----------|---------------------|-------|
| `page_num` | `physical_page.page_number_int` | Also compute `page_number_display` as Arabic numerals |
| `volume` | `physical_page.volume` | From filename stem |
| `matn_text` | `primary_text` | Rename only — content identical |
| `footnotes` (list) | `footnotes` (list of Footnote) | Add `footnote_type=UNKNOWN`, `confidence=0.0` initially |
| `unit_index` | `unit_index` | Already computed in ABD |
| (not in ABD) | `text_layers` | Empty list initially (Step 4 adds this) |
| (not in ABD) | `structural_markers` | Empty initially (Pass 4 integration fills this) |
| (not in ABD) | `verse_info` | ABD has verse detection — convert to VerseLine objects |
| (not in ABD) | `content_flags` | ABD has `has_verse`, `has_table` — extend in Step 5 |
| (not in ABD) | `text_fidelity` | Set to `high`/`1.0` for all Shamela pages (digital text) |

**Source metadata layer_type mapping:**
- Source engine uses string `"tahqiq"` in TextLayer.layer_type
- Normalization engine uses `LayerType.TAHQIQ_NOTE` (value: `"tahqiq_note"`)
- Map `"tahqiq"` → `LayerType.TAHQIQ_NOTE` during Pass 5 initialization

**Test:** Run on `tests/fixtures/shamela_ibn_aqil.htm`. Output must validate against `NormalizedPackage` schema. Every content unit must have valid `unit_index`, `physical_page`, non-empty `primary_text`.

### Step 2: Self-Validation Framework (§5 Checks 1–9)

**Goal:** Implement all 8 automated validation checks (check 9 is already in validate_input).

**What to do:**
1. Implement each `_check_*` function in `src/validation.py`.
2. Wire `validate_package()` to call all checks and aggregate results.
3. Call `validate_package()` in Pass 6 BEFORE the atomic write.
4. Any fatal check failure → abort normalization with `NORM_SCHEMA_VIOLATION`.

**Check thresholds (from SPEC §5):**
- Coverage: ±10% tolerance (or exact match for deterministic sources like Shamela)
- Arabic character ratio: >70% (excluding whitespace and punctuation)
- Garbage run: >20 identical consecutive characters
- Layer transitions per page: ≤20 (>20 suggests misdetection)
- Matn ratio in sharh: <40%
- Unit index: contiguous 0-based, no gaps, no duplicates

**Test:** Construct invalid packages programmatically (missing pages, bad unit_index, non-Arabic text) and verify each check catches the violation.

### Step 3: Footnote Type Classification (Pass 2 Upgrade)

**Goal:** Classify footnotes as `tahqiq_editor`, `author_original`, or `unknown_footnote_type`.

**What to do:**
1. In the ABD footnote parsing code (Pass 2), after separating footnotes, add classification logic.
2. Classification rules (SPEC §4.A.2 Pass 2):
   - **tahqiq_editor:** Contains tahqiq markers — hadith grading terms, manuscript variant notation ("في نسخة:"), bibliographic collection references.
   - **author_original:** Matches main text writing style, no tahqiq markers.
   - **unknown_footnote_type:** Uncertain — assign with confidence score.
3. Use pattern matching as primary classifier. LLM fallback is §4.B.4 (later step, not this one).
4. Set `confidence` score: 0.9 for clear pattern matches, 0.5 for heuristic matches, 0.0 for unknown.

**Patterns for tahqiq detection:**
- Hadith grading: `صحيح`, `ضعيف`, `حسن`, `موضوع`, `أخرجه`, `رواه`
- Manuscript variants: `في نسخة`, `في الأصل`, `كذا في`, `والصواب`
- Bibliographic: `انظر:`, `راجع:`, `ذكره في`, `أشار إليه`
- Editor voice: `قلت:` (when preceded by editorial context), `المحقق`

**Test:** Fixture page with footnote `"انظر: التسهيل لابن مالك ص ٤٥. وقد أخرج البخاري (٢٣٤٥) نحوه."` → classified as `tahqiq_editor` with confidence ≥0.8. Fixture page with footnote containing variant reading `"في نسخة أ: «فإن كل واحد من هذه» وفي نسخة ب: «فإن كلاً من هذه»"` → classified as `tahqiq_editor` (specifically `variant_reading` pattern).

### Step 4: Multi-Layer Detection (Pass 5)

**Goal:** Identify matn vs sharh text boundaries on each page.

**What to do:**
1. Implement `src/layer_detector.py` with Shamela-specific signals.
2. In Pass 1, BEFORE HTML stripping, record bold spans (`<b>` tag positions) and font size tags.
3. In Pass 5, use recorded signals + transition phrases to segment each page.
4. Produce `text_layers` array per content unit.

**Signal priority (SPEC §4.A.2 Pass 5):**
1. Bold text (`<b>` tags) — highest confidence for Shamela commentaries (~75% use this)
2. Bracket markers `[ matn text ]` — high confidence
3. Transition phrases (`قال المصنف`, `قوله`, `قال الشارح`) — medium confidence
4. Font size differences (`<font size>`) — minority of exports

**Single-layer handling:** If `is_multi_layer` is false in source metadata AND no layer signals detected, produce a single `TextLayerSegment` covering the full text with `layer_type=SHARH` (or whatever the source's primary layer is) and `confidence=1.0`.

**Test:** Fixture page 2 (has `<b>` matn): matn layer detected for bold text, sharh for the rest. Full character coverage verified. Fixture page 5 (no multi-layer signals): single segment covering entire text.

### Step 5: Content Flagging Expansion (§4.A.9)

**Goal:** Detect Quran citations, hadith citations, TOC pages, index pages, blank pages.

**What to do:**
1. Implement `src/content_flagger.py`.
2. Extend ABD's existing `has_verse` and `has_table` detection.
3. Add new detections:
   - **has_quran_citation:** Look for `﴿...﴾` brackets, `قال الله تعالى`, surah names + verse numbers.
   - **has_hadith_citation:** Look for collection names (البخاري, مسلم, أبو داود, الترمذي, النسائي, ابن ماجه, أحمد) + numbers.
   - **is_toc_page:** Detect فهرس/محتويات headers, dot-leader patterns, page-number-only columns.
   - **is_index_page:** Similar to TOC but at end of book; detect فهرس الموضوعات, فهرس الأعلام.
   - **is_blank:** Page with <10 non-whitespace characters after cleaning.

**Test:** Fixture page 4 (has `﴿إِنَّا أَنْزَلْنَاهُ﴾`) → `has_quran_citation=true`. Fixture page 2 (footnote mentions البخاري) → `has_hadith_citation=true`. Fixture page 2 (has verse with `*`) → `has_verse=true`.

### Step 6: Content Census (§4.B.5)

**Goal:** Compute statistical profile after all content units are generated.

**What to do:**
1. Implement `src/content_census.py`.
2. Compute all metrics defined in `ContentCensus` contract.
3. Call after Pass 6 assembles all content units, before writing manifest.
4. Store result in manifest's `content_census` field.

**Metrics to compute:**
- `text_density_profile`: chars per page statistics (mean, median, std_dev, sparse/dense counts)
- `verse_ratio`, `table_ratio`, `quran_citation_ratio`, `hadith_citation_ratio`: proportion of pages with each flag
- `layer_complexity`: layer count, transition density, matn ratio (multi-layer sources only)
- `structural_depth`: division count, max depth, mean pages per leaf division
- `footnote_density`: mean footnotes per page, max on single page, text ratio
- `vocabulary_profile`: estimated unique terms (HyperLogLog), technical term density, diacritics density
- `fidelity_distribution`: percentage of pages at each fidelity level

**Test:** Census computed for fixture source. Verify `total_pages` matches, verse_ratio > 0 (fixture has verse pages), hadith_citation_ratio > 0.

---

## Integration with Structure Discovery

Pass 4 integrates the ABD `discover_structure.py`. This code is 2896 lines and already works.

**Integration approach:**
1. Copy `discover_structure.py` to `src/structure_discovery.py`.
2. Adapt its input: instead of reading HTML files directly, receive parsed page data from Pass 1.
3. Adapt its output: instead of ABD division format, produce `DivisionNode` objects from `contracts.py`.
4. The 4-tier confidence architecture (HTML-tagged, TOC, keyword heuristics, LLM) stays the same.
5. The structural_patterns.yaml file is already in `reference/`.

**Do NOT rewrite structure discovery.** Adapt the interface, preserve the logic.

---

## Constraints

1. **Never modify primary text.** No spelling correction, no diacritic changes, no cleanup. SPEC core rule.
2. **Arabic text is fragile.** Read `.claude/skills/arabic-text/SKILL.md` before any text processing. Watch for Unicode normalization, ZWNJ handling, diacritics stripping by Python libraries.
3. **Pydantic models are the contract.** Output must validate against `contracts.py` models. Do not add fields or change types.
4. **Errors fail loudly.** Use `NormalizationError` from `src/errors.py`. Never silently skip a page or drop data.
5. **ABD tests must pass.** After adapting ABD code, the existing test logic (adapted for new output format) must still pass. Create equivalent tests in `tests/test_kr_output.py`.
6. **Atomic writes only.** Never write partial output. Use `src/writer.py`.

---

## Dependencies

All in `requirements.txt`:
- `beautifulsoup4` + `lxml` — HTML parsing (existing ABD dependency)
- `pydantic` — schema validation
- `PyYAML` — structural_patterns.yaml loading
- `pyarabic` — Arabic text utilities (diacritics detection, character classification)

No new dependencies needed for Shamela normalizer. OCR dependencies (Mistral, Qari) are only for future PDF/image normalizers.

---

## File Layout After Implementation

```
engines/normalization/
├── SPEC.md                          # Behavioral authority (read-only for Claude Code)
├── IMPL_BRIEF.md                    # This file
├── contracts.py                     # Pydantic schemas (read-only unless SPEC changes)
├── src/
│   ├── __init__.py
│   ├── dispatcher.py                # Routes to correct normalizer
│   ├── errors.py                    # Error codes (complete)
│   ├── writer.py                    # Atomic write procedure
│   ├── validation.py                # §5 self-validation checks
│   ├── layer_detector.py            # Multi-layer detection
│   ├── content_flagger.py           # Content type flagging
│   ├── content_census.py            # Statistical profiling
│   ├── structure_discovery.py       # Adapted from ABD discover_structure.py
│   └── normalizers/
│       ├── __init__.py
│       ├── base.py                  # Normalizer interface (complete)
│       └── shamela.py               # Shamela normalizer (6-pass pipeline)
└── tests/
    ├── __init__.py
    ├── test_kr_output.py            # Output format tests (stubs ready)
    ├── fixtures/
    │   └── shamela_ibn_aqil.htm     # Shamela-format test fixture
    └── gold_baselines/
        └── README.md                # Gold baseline requirements
```
