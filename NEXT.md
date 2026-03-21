# NEXT — Session 7: Integration Testing & ADV Gap Closure

## Current Position

- **Phase:** Build → Session 7 of 7 (final build session)
- **Previous:** Session 6 ACCEPTED at commit `760b5f4` (validation, writer, plain text normalizer, dispatcher)
- **Test baseline:** `335 passed, 12 skipped` (pytest engines/normalization/tests/)
- **Smoke test:** 63/63 PASS (13 real + 50 extended fixtures)
- **ADV coverage:** 29/51 implemented (9 remaining core, 13 deferred)
- **Known limitations:** L-001 through L-011 documented
- **SPEC errata:** SPEC-NOTE-1 through SPEC-NOTE-3 documented

## What to Do

This is the **final normalization engine build session**. Focus: integration testing on real fixtures, unskip deferred tests, close remaining core ADV gaps.

**All new tests in a single new file: `engines/normalization/tests/test_integration.py`.**

The 12 skipped tests in `test_kr_output.py` are unskipped by **implementing equivalent tests** in `test_integration.py`. Do NOT modify `test_kr_output.py` skip bodies — only update the skip reason strings to reference the superseding test.

### Owner Action Needed

None. The architect prepared this handoff. CC executes.

## Read First (in this order)

1. `engines/normalization/CLAUDE.md` — module map, build metrics, critical rules
2. `engines/normalization/SPEC.md` §4.A.9 (content flags), §4.A.2 Pass 6 (assembly), §5 (validation)
3. `engines/normalization/tests/conftest.py` — all test factories (`_make_source_metadata`, `_make_content_unit`, `_make_normalized_package`, `_make_cleaned_page`, `_full_pipeline`, `_wrap_page`, `_make_html`)
4. `engines/normalization/contracts.py` — `NormalizedPackage`, `ContentUnit`, `NormalizedManifest`, `ContentFlags`
5. `engines/normalization/src/dispatcher.py` — `normalize_source()`, `normalize_and_write()`
6. `engines/normalization/src/content_flagger.py` — `compute_content_flags()`, pattern definitions
7. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — ADV cases referenced below
8. `engines/normalization/KNOWN_LIMITATIONS.md` — L-001 through L-011
9. `tools/smoke_test_validation.py` — existing integration test pattern (metadata factory, fixture iteration)

## What to Build

### Part A: Integration Tests (12 unskip + 1 new = 13 tests)

Create `engines/normalization/tests/test_integration.py`. All tests in this file run `normalize_source()` on real fixture files — they are integration tests, not unit tests.

**A1. TestShamelaNormalizer (9 tests):**

1. `test_output_schema_compliance` — Run `normalize_source()` on `02_nahw_muhaqiq` with `is_multi_layer=True`. Verify result is a `NormalizedPackage` with valid `NormalizedManifest`. Verify `manifest.source_id`, `manifest.total_content_units == len(content_units)`, `manifest.division_tree` is non-empty, `manifest.layer_map` has 2 entries (matn + sharh).

2. `test_content_preservation_arabic_text` — Run on `02_nahw_muhaqiq`. Verify `primary_text` on every content unit is non-empty. Verify total Arabic characters ([\u0600-\u06FF]) across all units exceeds 50% of all text characters. Verify no `<` or `>` in any primary_text (HTML tags stripped).

3. `test_footnote_separation` — Use `03_fiqh` fixture (32 pages with footnotes confirmed). Verify at least 20 content units have `len(footnotes) > 0`. Verify footnote entries have non-empty `.text`.

4. `test_multi_layer_detection` — Use `02_nahw_muhaqiq` with `is_multi_layer=True`. Verify `manifest.layer_map` has entries for both `LayerType.MATN` and `LayerType.SHARH`. Verify at least 3 content units have `len(text_layers) >= 2`.

5. `test_diacritics_preservation` — Use `04_hadith` fixture. Verify diacritics codepoints (\u064b-\u0652, \u0670, \u0640) exist in output. Verify total diacritic count > 5000 (confirmed: 11,120 in 04_hadith).

6. `test_page_boundaries` — Run on `02_nahw_muhaqiq`. Verify `unit_index` values form a contiguous sequence `0..N-1`. Verify each `physical_page.volume >= 1`. Verify `len(content_units) == manifest.total_content_units`.

7. `test_structure_discovery` — Use `06_usul` fixture (9 divisions confirmed). Verify `manifest.division_tree` has >= 5 entries. Verify each `DivisionNode` has non-empty `heading_text`. Verify `start_unit_index <= end_unit_index` for all nodes.

8. `test_content_flags` — Use `04_hadith`. Verify at least 30 content units have `content_flags.has_hadith_citation == True` (confirmed: 36). Use `01_nahw_simple` and verify 0 or very few hadith flags (it's a nahw grammar text, not hadith).

9. `test_boundary_continuity_signals` **(F2 — Session 5 integration coverage)** — Run on `01_nahw_simple`. Verify: (a) at least 50% of content units have `boundary_continuity is not None`, (b) the set of `boundary_continuity.type` values across all units contains at least 2 distinct types, (c) every non-None `boundary_continuity.confidence > 0`. Confirmed values: 01_nahw_simple has mid_sentence: 47, mid_paragraph: 17, mid_argument: 1, section_break: 7 out of 73 units = 72/73 with signals.

**A2. TestContentFlagger (3 tests) — unit-level flag verification:**

10. `test_quran_verse_detection` — Construct a `CleanedPage` with `primary_text` containing `قال تعالى {وَأَقِيمُوا الصَّلَاةَ}`. Call `compute_content_flags()`. Assert `has_quran_citation == True`. Also test text without pattern → `False`.

11. `test_hadith_marker_detection` — Construct a `CleanedPage` with `primary_text` containing `رواه البخاري`. Assert `has_hadith_citation == True`. Also with ﷺ → `True`. Also clean text → `False`.

12. `test_poetry_verse_detection` — Construct a `CleanedPage` with `has_verse=True`. Assert `has_verse == True`. Test `has_verse=False` → `False`. (Poetry detection happens in Pass 3; the flagger passes through the signal.)

**A3. TestContentCensus — remains skipped:**

13. Add `test_census_deferred` → `pytest.skip("§4.B.5 DEFERRED — content census not in core build")`.

**Design decision D7-1:** Census stays deferred per CORE_EXTRACTION.md. Explicit skip documents it.

**Note:** Part B's page-loss check uses `BeautifulSoup` (already a project dependency in `requirements.txt` as `beautifulsoup4>=4.12`). Import it locally inside the test method, not at module level.

### Part B: Parametrized Fixture Integration Test

Add `TestFixtureIntegration` class with a single parametrized test.

`test_normalize_source_all_fixtures` — Parametrize over all `.htm` files in `tests/fixtures/shamela_real/` (13) and `tests/fixtures/shamela_extended/` (50).

For each fixture:
1. Build metadata using `_make_source_metadata()`. For `02_nahw_muhaqiq`, use `is_multi_layer=True`.
2. Call `normalize_source(htm_file, metadata)`.
3. Assert result is a `NormalizedPackage`.
4. Assert `len(content_units) == manifest.total_content_units`.
5. Assert `unit_index` values are contiguous `0..N-1`.
6. Assert every `primary_text` contains Arabic characters ([\u0600-\u06FF]).
7. Assert `manifest.layer_map` is non-empty.
8. **Silent page loss check (F1):** Count `<div class='PageText'>` tags in the raw HTML. Assert `abs(raw_count - len(content_units)) <= 5`. (Gap is typically 1-2 due to metadata pages filtered by Pass 1. Tolerance of 5 allows for edge cases. A broken normalizer dropping pages would miss by tens or hundreds.)

Fixture discovery pattern:
```python
def _discover_fixtures():
    project_root = Path(__file__).parent.parent.parent.parent  # kr/
    fixtures = []
    for base in [project_root / "tests" / "fixtures" / "shamela_real",
                 project_root / "tests" / "fixtures" / "shamela_extended"]:
        if not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            htms = list(d.glob("*.htm"))
            if htms:
                fixtures.append((d.name, htms[0]))
    return fixtures

FIXTURES = _discover_fixtures()
MULTI_LAYER_FIXTURES = {"02_nahw_muhaqiq"}

@pytest.mark.parametrize("name,path", FIXTURES, ids=[f[0] for f in FIXTURES])
def test_normalize_source_all_fixtures(self, name, path):
    is_multi = name in MULTI_LAYER_FIXTURES
    meta = _make_source_metadata(is_multi_layer=is_multi)
    pkg = normalize_source(path, meta)
    assert isinstance(pkg, NormalizedPackage)
    assert len(pkg.content_units) == pkg.manifest.total_content_units
    indices = [cu.unit_index for cu in pkg.content_units]
    assert indices == list(range(len(indices)))
    for cu in pkg.content_units:
        if not cu.content_flags.is_blank:
            assert any('\u0600' <= c <= '\u06FF' for c in cu.primary_text)
    assert len(pkg.manifest.layer_map) >= 1
    # F1: Silent page loss check — count raw PageText divs
    from bs4 import BeautifulSoup
    raw_html = path.read_text(encoding="utf-8")
    raw_page_count = len(BeautifulSoup(raw_html, "lxml").find_all("div", class_="PageText"))
    assert abs(raw_page_count - len(pkg.content_units)) <= 5, (
        f"Silent page loss: {raw_page_count} raw pages → {len(pkg.content_units)} content units"
    )
```

### Part C: End-to-End normalize_and_write Tests

Add `TestNormalizeAndWrite` class:

1. `test_end_to_end_write_and_read` — Use `01_nahw_simple` fixture. Call `normalize_and_write()` with `tmp_path`. Verify `manifest.json` and `content.jsonl` exist. Read back. Verify manifest source_id. Verify JSONL line count matches manifest total_content_units. Verify first JSONL line parses as valid JSON with `primary_text` key.

2. `test_roundtrip_content_integrity` — Write then read back first content unit's `primary_text`. Assert identical.

3. `test_plain_text_normalize_and_write` **(F3 — Session 6 integration coverage)** — Create a temp `.txt` file with 3 Arabic paragraphs separated by double newlines. Call `normalize_and_write()` with `source_format='plain_text'` in metadata. Verify `manifest.json` and `content.jsonl` exist. Verify at least 1 content unit. Verify `primary_text` contains the original Arabic text. Verify `manifest.normalizer_id` contains `plain_text`. Construction:
```python
def test_plain_text_normalize_and_write(self, tmp_path):
    arabic = "بسم الله الرحمن الرحيم\n\nالحمد لله رب العالمين\n\nوالصلاة والسلام على رسوله الكريم\n"
    txt_file = tmp_path / "source.txt"
    txt_file.write_text(arabic, encoding="utf-8")
    meta = _make_source_metadata(source_format="plain_text", source_id="pt_test")
    result_dir = normalize_and_write(txt_file, meta, tmp_path)
    assert (result_dir / "manifest.json").exists()
    assert (result_dir / "content.jsonl").exists()
    import json
    with open(result_dir / "manifest.json") as f:
        manifest = json.load(f)
    assert manifest["source_id"] == "pt_test"
    assert "plain_text" in manifest["normalizer_id"]
    with open(result_dir / "content.jsonl") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    assert len(lines) >= 1
    assert "بسم الله" in lines[0]["primary_text"]
```

### Part D: Remaining Core ADV Tests

Add `TestAdversarialGap` class:

1. **ADV-019** `test_adv019_unit_index_contiguity` — Run on `02_nahw_muhaqiq` (295 pages) and `03_fiqh` (102 pages). Assert `unit_index` values form `range(N)` for each.

2. **ADV-020** `test_adv020_duplicate_page_numbers` — Construct 2-page HTML where both pages have `(ص: 12)`. Run normalize_source. Assert 2 content units with unique unit_index (0, 1) and both page_number_int == 12.

3. **ADV-022** `test_adv022_trailing_diacritics_preserved` — Construct HTML with text ending in kasra (U+0650): `بِسْمِ اللَّهِ الرَّحِيمِ`. Run normalize_source. Assert U+0650 is present in output primary_text.

4. **ADV-034** `test_adv034_universal_footnote_marker` — Construct HTML with `(1)` reference and matching footnote below `<hr width='95'>`. Run normalize_source. Assert `⌜1⌝` (U+231C + U+231D) in primary_text. Assert no literal `(1)` in primary_text.

5. **ADV-038** `test_adv038_interrupted_write_missing_content` — Check if test_writer.py already has a test creating temp with manifest but no content.jsonl. If yes, document as "covered by test_writer::test_adv047_*". If no, add the test.

6. **ADV-040** `test_adv040_arabic_filename_multi_volume` — Create temp dir with `المجلد_الأول.htm` and `المجلد_الثاني.htm`, each valid single-page HTML. Run normalize_source on the directory. Assert 2 units, sequential volumes.

7. **ADV-048** `test_adv048_windows_1256_encoding` — Create temp file with Arabic text encoded in Windows-1256. Run normalize_source. Assert Arabic preserved. Assert NORM_ENCODING_ERROR in logs (use `caplog`).

8. **ADV-049** `test_adv049_page_number_overflow` — Construct HTML with `(ص: 999999999999999)`. Run normalize_source. Assert no crash. Assert content unit exists.

### Part E: Update test_kr_output.py Skip Reasons

Update each of the 11 skipped tests (not TestContentCensus) to:
```python
pytest.skip("Superseded by test_integration.py::TestXxx::test_yyy — Session 7")
```

Update TestContentCensus to:
```python
pytest.skip("§4.B.5 DEFERRED — content census not in core build (CORE_EXTRACTION.md)")
```

### Part F: Update Build Metrics

Update `engines/normalization/CLAUDE.md` Session 7 row and metrics. **F5 correction:** CLAUDE.md currently says "30/51 ADV" — the actual count is 29/51 (verified by grep). Fix to 29/51 before adding Session 7's new ADV cases.
Update `engines/normalization/KNOWN_LIMITATIONS.md` with L-012 (ADV-023 ASCII-only footnotes):

```markdown
## L-012: Arabic-Indic digit footnote markers not parsed

**Discovered:** Session 7 ADV gap analysis (March 2026).
**SPEC reference:** ADV-023.
**Behavior:** Footnote regex uses [0-9] (ASCII only). Arabic-Indic markers (١, ٢, ٣)
in format (١) are NOT detected as footnote references.
**Rationale:** Arabic-Indic digits in parentheses commonly appear as hadith/verse
numbers. Matching them as footnote markers introduces false positives. ASCII-only is a
precision-over-recall design choice documented in shamela.py line 115-122.
**Fix point:** If corpus analysis finds Shamela exports using Arabic-Indic footnote
markers, add a configurable detection mode.
```

## Context

### Fixture Characteristics (verified empirically by architect)

| Fixture | Units | Footnotes | Hadith flags | Quran flags | Divisions | Multi-layer | Diacritics |
|---------|-------|-----------|-------------|-------------|-----------|-------------|------------|
| 01_nahw_simple | 73 | 0 pages | 0 | 0 | 1 | No | 2,101 |
| 02_nahw_muhaqiq | 295 | 0 pages | 0 | 0 | 19 | Yes (5 pages 2+ layers) | 3,587 |
| 03_fiqh | 102 | 32 pages | — | — | 1 | No | — |
| 04_hadith | 41 | 0 pages | 36 pages | 0 | — | No | 11,120 |
| 05_tafsir | 47 | — | — | — | 1 | No | 1,090 |
| 06_usul | 74 | — | — | — | 9 | No | — |

Use these numbers in test assertions. They are confirmed from the current codebase at commit `f37babe`.

### Content Flagger Test Construction

`compute_content_flags()` takes a `CleanedPage` and `is_toc_page: bool`. The `_make_cleaned_page()` factory needs explicit fields for flagger tests:
```python
from engines.normalization.src.content_flagger import compute_content_flags

page = _make_cleaned_page(
    primary_text="رواه البخاري ومسلم",
    unit_index=0,
    title_spans=[],
    has_verse=False,
    has_tables=False,
    is_blank=False,
    is_image_only=False,
)
flags = compute_content_flags(page, is_toc_page=False)
assert flags.has_hadith_citation is True
```

### ADV-040 and ADV-048 Test Construction

These create temp files. Use `tmp_path` fixture and conftest helpers:
```python
# ADV-040: Arabic filename multi-volume
html1 = _make_html(_wrap_page("حدثنا أبو بكر", page_num="1"))
(tmp_path / "المجلد_الأول.htm").write_text(html1, encoding="utf-8")

# ADV-048: Windows-1256 encoding
htm_file = tmp_path / "book.htm"
htm_file.write_bytes(html.encode("windows-1256"))
```

## Design Decisions (pre-resolved — do not re-decide)

| ID | Decision | Rationale |
|----|----------|-----------|
| D7-1 | TestContentCensus stays skipped | §4.B.5 is DEFERRED per CORE_EXTRACTION.md |
| D7-2 | ADV-023 classified as L-012 (known limitation) | ASCII-only footnote regex is precision-over-recall. Changing introduces hadith/verse number false positives. |
| D7-3 | Tests go in test_integration.py (new file) | Separates integration tests from existing unit tests |
| D7-4 | ADV-038 verified against existing ADV-047 tests | If test_writer.py covers it, document as covered; don't duplicate |
| D7-5 | 13 deferred ADV cases documented, not implemented | OCR, discourse flow, fingerprint, content census, footnote classification, format auto-detection, write-back, tahqiq threshold |

## Do NOT Do

1. **Do NOT modify existing test files** except `test_kr_output.py` skip reasons.
2. **Do NOT modify any `src/` implementation files.** Session 7 is testing-only. If a test reveals a bug, document it — do not fix it.
3. **Do NOT implement deferred ADV cases** (027, 030-032, 035-037, 039, 041-044, 046).
4. **Do NOT change the footnote regex** for Arabic-Indic digits.
5. **Do NOT add parametrized pytest tests for individual files from `shamela-export-samples/`.** The `smoke_test_validation.py` already samples 50 random files from that directory if it exists — let it do its job via Verification check #3. Do NOT duplicate that coverage in test_integration.py.
6. **Do NOT change conftest.py** unless a new factory is strictly needed.
7. **Do NOT touch SPEC.md.**

## Verification

```bash
# 1. Full test suite — zero failures
python -m pytest engines/normalization/tests/ -v --tb=short
# Expected: N passed, 13 skipped (12 in test_kr_output.py + 1 census in test_integration.py)

# 2. Integration tests specifically
python -m pytest engines/normalization/tests/test_integration.py -v --tb=short
# Expected: all pass except 1 skip (census)

# 3. Smoke test (regression — also samples from shamela-export-samples/ if it exists)
python tools/smoke_test_validation.py
# Expected: 63/63 PASS on repo fixtures (+ local sample results if available)

# 4. No src/ changes
git diff --name-only engines/normalization/src/
# Expected: empty

# 5. ADV coverage in new file
grep -oi "adv.0[0-9][0-9]" engines/normalization/tests/test_integration.py | sort -u | wc -l
# Expected: >= 8
```

**Pass criteria:** All 5 checks pass. 335 existing tests still pass. Test count increases from 335 to >= 420 (335 existing + ~86 new). Skip count goes from 12 to 13 (12 existing + 1 new census skip).

## After This

Session 7 completes the normalization engine build. Next:
1. 3-probe evaluation using `kr-evaluate`
2. Transition gate using `kr-gating-transitions`
3. SPEC maintenance pass (SPEC-NOTE-1 through SPEC-NOTE-3)
