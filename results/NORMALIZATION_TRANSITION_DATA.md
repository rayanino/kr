# Normalization Engine — Transition Data

**Date:** 2026-03-22
**Engine:** Normalization (محرك التطبيع)
**Status:** Build sessions 1-7 complete, corpus sweep validated, bug fixes verified

---

## 1. Build Metrics

| Metric | Value |
|--------|-------|
| Test count | 452 passed, 14 skipped, 0 failures |
| Implementation lines | ~7,797 (src/) |
| Build sessions | 7 (contracts → Passes 1-3 → structure → layers → assembly → validation/writer → integration) |
| ADV cases covered | 37/51 (73%) |
| Known limitations | L-001 through L-012 |
| Edge case fixtures | 15 (5 existing + 10 new from overnight Phase 1) |

### Known Limitations Summary

| ID | Description | Severity | Fix Point |
|----|-------------|----------|-----------|
| L-001 | Bare-number footnotes not parsed | Low | Enhancement later |
| L-002 | ضياء السالك commentary numbering collision | Low | 1 book affected |
| L-003 | Same-page same-level headings create chains | Medium | SPEC-level fix needed |
| L-004 | Arabic conjunction prefixes on markers | Low | Regex extension |
| L-005 | Bold threshold 50 vs SPEC 80 | Low | Calibration deviation |
| L-006 | Hashiyah quotation detection not implemented | Medium | Needs 3-layer fixture |
| L-007 | Marker-only MATN over-extension | Medium | Content inference needed |
| L-008 | Conditional reasoning markers excluded from BC | Low | Position requirement |
| L-009 | Guillemet hadith distance heuristic (50 chars) | Low | Tunable parameter |
| L-010 | Division overlap = WARNING not FATAL | Low | 15.4% of corpus, no data impact |
| L-011 | Writer recovery: prev-only orphan state | Very low | Near-zero practical risk |
| L-012 | Arabic-Indic digit footnotes not parsed | Low | Precision-over-recall choice |

---

## 2. Corpus Sweep Results

From `results/CALIBRATION_REPORT.md` (post-fix v2 sweep):

| Metric | Value |
|--------|-------|
| Total books processed | 7,475 |
| OK | 7,475 (100.0%) |
| Crashes | 0 (0.0%) |
| Total content units | 2,059,924 |
| Total raw pages | 2,069,347 |
| Processing time | 18.3 minutes (0.15s/book mean) |

### Key Calibration Points

| Check | Value |
|-------|-------|
| Multi-layer auto-upgrade rate | 5.4% (401 books) |
| Suspected false positives (>50% multi-layer ratio) | 85 books (21.2% of auto-upgraded) |
| Division overlap warnings | 15.4% of corpus |
| Mean Arabic ratio | 80.1% |
| Books with Arabic ratio < 70% | 58 (0.8%) |
| Mean boundary continuity coverage | 98.0% |
| Mean page loss | 1.26 (median 1, near-perfect) |
| Books with page loss > 5 | 25 (0.3%) |

---

## 3. Bug Fix Impact

From `results/VERIFICATION_REPORT.md`:

### Fix 1: Pageless books (48 books)
- **Before:** 48 books with status=OK but 0 content units (silent failure)
- **After:** All 48 produce content. +3,045 content units recovered
- **Root cause:** `_pass1_parse()` classified all pages as metadata in books without `(ص: N)` page numbers

### Fix 2: Diacritics canary crash (1 book)
- **Before:** 1 crash (NORM_DIACRITICS_ENTITY_CORRUPTION)
- **After:** Normalizes to 90 pages, 79,732 chars
- **Root cause:** `_ARABIC_DIACRITICS` used 20 codepoints (broader than SPEC's 10)

### Regression Check
- Full re-sweep: 7,475/7,475 OK
- No new crashes, no new zero-content books
- Warning count stable (+13 from newly-producing books)

---

## 4. Passaging Contract Readiness

From `results/CALIBRATION_REPORT.md` section B.8:

| Contract Check | Failures | Percentage |
|----------------|----------|-----------|
| check4_count_match (units match manifest) | 0 | 0.0% |
| check5 (ordered, no gaps) | 0 | 0.0% |
| check6_division_consistent | 1,148 | 15.4% |

**Books passing ALL checks:** 6,327 (84.6%)

The 15.4% check6 failures are division overlap warnings (L-010) — advisory metadata, not content corruption. The passaging engine uses `unit_index` adjacency, not the division tree.

---

## 5. Edge Cases (Phase 1 Fixtures)

10 new fixtures added during overnight Phase 1:

| Fixture | Category | Key Feature |
|---------|----------|-------------|
| edge_extreme_small_2kb.htm | extreme | 2KB, ~2 pages |
| edge_tiny_zero_diacritics.htm | extreme | 3 pages, zero diacritics |
| edge_zero_diacritics_hadith.htm | extreme | 52 units, zero diacritics |
| edge_zero_flags_nahw.htm | extreme | Zero content flags |
| edge_low_arabic_ratio.htm | extreme | 55.4% Arabic ratio |
| edge_high_page_loss.htm | extreme | 13 pages lost |
| edge_zero_diacritics_large.htm | extreme | 361 units, zero diacritics |
| edge_multi_layer_99pct.htm | multi_layer | 99.3% multi-layer |
| edge_nahw_grammar.htm | extreme | Pure grammar, no flags |
| edge_warning_heavy.htm | warning | High warning density |

All 10 pass the full normalization pipeline with 27 dedicated tests.

---

## 6. SPEC Errata

From `reference/SPEC_ERRATA.md`:

| ID | Issue | Status |
|----|-------|--------|
| SPEC-NOTE-1 | §4.B.8 mid_argument confidence contradiction | RESOLVED |
| SPEC-NOTE-2 | §4.B.8 marker table missing `ولنا` | RESOLVED |
| SPEC-NOTE-3 | §5 check 4 sharh-majority for 3-layer texts | RESOLVED (documented) |

All errata resolved during normalization engine evaluation.

---

## 7. Open Questions for Architect

1. **L-003 / L-010 (division overlap):** Is the 15.4% overlap rate acceptable for the passaging engine, or does the division tree need sub-page ranges?

2. **Multi-layer false positive rate:** 85 books (21.2% of auto-upgraded) have >50% multi-layer ratio. Should these be reviewed before passaging uses layer data?

3. **Page loss tolerance:** 25 books (0.3%) have page loss > 5. The maximum is 62 (التهذيب في اختصار المدونة). Is the current ±5 tolerance in integration tests appropriate?

4. **L-005 bold threshold:** The calibrated 50-char threshold deviates from SPEC's provisional 80. Should the SPEC be updated, or should additional fixtures be tested?

5. **Cross-engine validation:** 9 multi-layer disagreements between source engine LLM and normalization auto-detection. Should these be reconciled before passaging?

6. **Passaging readiness:** With 84.6% passing all contract checks, is this sufficient to start passaging engine development, or should the 15.4% division consistency issue be resolved first?
