# Sweep Fix Summary

**Date:** 2026-03-21
**Session:** Weekend Task 2 — Bug Fix Sprint
**Cost:** 0 EUR (no LLM calls)

## Normalization Engine

- Crashes found: 1 (NORM_DIACRITICS_ENTITY_CORRUPTION)
- Crashes fixed (FIX NOW): 1 (with test coverage)
- Crashes deferred: 0
- Crashes for architect review: 0
- Silent failures found: 48 (zero-content books, status=OK but 0 content units)
- Silent failures fixed: 48 (with test coverage)
- Test count before fixes: 434 (420 passed, 14 skipped)
- Test count after fixes: 439 (425 passed, 14 skipped)
- New tests added: 5

## Source Engine

- Errors found (excluding UNSUPPORTED_FORMAT): 0
- Errors fixed: 0
- No action needed — 100% success rate on 7,475 items

## Fixes Applied

### Fix 1: Pageless books metadata misclassification (48 books)
- **Commit:** `fix: [normalization] handle books without page numbers`
- **File:** `engines/normalization/src/normalizers/shamela.py`
- **Change:** Added pre-scan for page numbers in `_pass1_parse()`. For books without any `(ص: N)` markers, only the first page is metadata; subsequent pages are content.
- **Tests:** 4 new tests (pass1, full pipeline, large fixture, regression)
- **Verification:** Both zero-content fixtures produce content after fix:
  - `zero_content_hadith_dhunnun.htm`: 5 units, 11,511 chars
  - `zero_content_musnad_546pages.htm`: 545 units, 217,950 chars

### Fix 2: Diacritics canary false positive (1 book)
- **Commit:** `fix: [normalization] resolve diacritics canary false positive crash`
- **File:** `engines/normalization/src/normalizers/shamela.py`
- **Change:** (a) Aligned `_ARABIC_DIACRITICS` with SPEC §5 range (20→10 codepoints). (b) Changed canary from exact sequence to count comparison with ±1 tolerance.
- **Tests:** 1 new test (canary with crash fixture)
- **Verification:** Crash fixture normalizes to 90 pages, 79,732 chars

## Crash Books List

### Fixed (49 books total)

**Crash — now fixed (1 book):**
- مواقف النبي - صلى الله عليه وسلم - في الدعوة إلى الله تعالى

**Silent failure — now fixed (48 books):**
- الخلعيات series (20 volumes: الأول through العشرون)
- معجم شيوخ الدمياطي series (8 volumes)
- المصباح في عيون الصحاح (2 volumes)
- حديث ذي النون المصري
- أحاديث عوالي للدمياطي
- فوائد ابن دحيم
- حديث عباس الترقفي
- فوائد أبي عبد الله النعالي
- منتخب من حديث يونس بن عبيد
- مسند أبي حنيفة رواية الحصكفي
- أسرار البيان في التعبير القرآني - كتاب
- أمالي ابن منده- رواية البزاني
- التوسعة على العيال لأبي زرعة
- الثاني من أمالي أبي الحسين بن بشران
- (and other hadith compilations)

## Before/After Comparison

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Normalization crashes | 1 | 0 | -1 |
| Zero-content books | 48 | 0 | -48 |
| Total tests | 434 | 439 | +5 |
| Tests passing | 420 | 425 | +5 |
| Files modified | — | 1 src + 1 test | — |
| SPECs modified | — | 0 | — |
| Contracts modified | — | 0 | — |
