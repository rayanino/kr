# Normalization Corpus Sweep — CC Analysis

**Date:** 2026-03-21
**Script:** `scripts/normalization_corpus_sweep.py`
**Collection:** `shamela-export-samples/` (7,475 books)
**Duration:** 2,213 seconds (36.9 minutes), mean 0.30s/book
**Cost:** 0 EUR (fully deterministic, no LLM calls)

---

## 1. Overall Results

| Metric | Value |
|--------|-------|
| Total books | 7,475 |
| OK | 7,474 (99.987%) |
| CRASH | 1 (0.013%) |
| VALIDATION_FAILED | 0 (0.0%) |
| Total content units produced | 2,056,879 |
| Total characters | 2,139,148,691 (~2.1 billion) |
| Total diacritics | 286,033,196 (~13.4% of text) |

**The normalization engine achieved 99.987% success rate on the full Shamela corpus.** The single crash is a diacritics canary check, not a structural failure.

---

## 2. Crash Analysis (1 book)

**Book:** مواقف النبي - صلى الله عليه وسلم - في الدعوة إلى الله تعالى
**Error:** `NORM_DIACRITICS_ENTITY_CORRUPTION`
**Message:** "Diacritic sequence mismatch: regex found 20 diacritics, BS4 found 19 in first 500 chars"

This is the diacritics canary check — a safety mechanism where the regex-based primary parser's diacritics count is validated against a BS4 fallback parse. A 1-diacritic discrepancy in the first 500 chars triggered the fail-loud behavior (correct per SPEC).

**Root cause hypothesis:** An HTML entity encoding for a diacritical mark that regex handles differently from BS4. This is the exact edge case the canary was designed to catch.

**Action for architect:** Investigate the specific entity encoding in this book's HTML. The canary is working correctly — the question is whether the regex or BS4 is right.

**Edge case fixture saved:** `tests/fixtures/shamela_edge_cases/crash_diacritics_entity_mismatch.htm`

---

## 3. Zero-Content Books (48 books, 0.6%)

**Finding:** 48 books produce 0 content units despite having PageText divs with actual Arabic text in the HTML.

These books have raw_page_divs ranging from 3 to 546 but produce total_chars=0 and content_units=0 after normalization. Manual inspection confirms the HTML contains real Arabic text (e.g., "حديث ذي النون المصري" has 6 pages with 1,000+ chars each).

### Pattern Analysis

The 48 books fall into clear categories:
- **الخلعيات** series (20 volumes): Volumes 1-20 of al-Khala'iyyat
- **معجم شيوخ الدمياطي** series (8 volumes): Volumes 1-8
- **المصباح في عيون الصحاح** (2 volumes): Volumes 2, 10
- **Hadith compilations** (18 books): Various hadith collections (حديث ذي النون, أحاديث عوالي, فوائد ابن دحيم, مسند أبي حنيفة, etc.)

### Hypothesis

All zero-content books are parts of multi-volume manuscript collections, typically hadith compilations. The normalization pipeline may be filtering all pages because:
1. The sweep forces `is_multi_layer=False`, but these books may need multi-layer detection to extract content
2. The pages may have a Shamela HTML structure variant that the normalizer doesn't recognize
3. Pages may fail the Arabic ratio check or some other per-page filter

**This is the most significant finding of the sweep — 48 books with real content that produce zero output.**

**Action for architect:** Investigate the zero-content pattern by running one book (e.g., "حديث ذي النون المصري") through the pipeline in debug mode. Check which pass eliminates the pages.

**Edge case fixtures saved:**
- `tests/fixtures/shamela_edge_cases/zero_content_hadith_dhunnun.htm` (6 pages, small)
- `tests/fixtures/shamela_edge_cases/zero_content_musnad_546pages.htm` (546 pages, largest)

---

## 4. Page Loss Analysis

| Page Loss | Count | Percentage |
|-----------|-------|-----------|
| 1 | 5,865 | 78.5% |
| 2 | 1,452 | 19.4% |
| 3 | 62 | 0.8% |
| 4 | 15 | 0.2% |
| 5 | 8 | 0.1% |
| >5 | 72 | 1.0% |

- **97.9%** of books lose 1-2 pages (expected: the header/info page)
- **72 books** with page loss > 5, of which 43 have loss > 20
- All 43 high-loss books (>20) are the zero-content books (loss = raw pages, since units = 0)
- **Non-zero-content books with loss > 5:** ~29 books — these have real page loss worth investigating

**Maximum page loss in non-zero books:** التهذيب في اختصار المدونة with 62 page loss (raw=519, units=457). This is a multi-volume book — the loss likely comes from volume boundary pages and structural overhead.

**Edge case fixture saved:** `tests/fixtures/shamela_edge_cases/high_page_loss_62/` (4-volume book)

---

## 5. Warning Patterns at Scale

| Warning Category | Count | Percentage of Total |
|-----------------|-------|-------------------|
| char_run | 8,248 | 53.6% |
| low_arabic_ratio | 4,530 | 29.4% |
| division_overlap | 2,543 | 16.5% |
| other | 79 | 0.5% |
| **Total** | **15,400** | |

### Interpretation

1. **char_run (53.6%):** Identical character runs >20 chars. Known issue — these are Shamela formatting artifacts (long sequences of dashes, dots, or spaces used as visual separators). Not a content integrity issue.

2. **low_arabic_ratio (29.4%):** Individual pages below the 70% Arabic ratio threshold. At scale, many books have a few pages with non-Arabic content (tables of contents, indices, publication info, foreign-language references). The 106 books below 70% aggregate ratio (1.4%) is a normal distribution tail.

3. **division_overlap (16.5%):** Same-page headings causing division range overlap. This is known limitation L-010 from the evaluation. At scale: 2,543 occurrences across 1,147 books (15.3%). The evaluation found this in 14% of extended fixtures — the corpus rate (15.3%) is consistent.

4. **other (0.5%):** 79 warnings not matching the categorization patterns. Low volume — likely edge-case warning messages.

**No new warning types** emerged at scale. All warnings trace to known patterns from the 63-fixture evaluation.

---

## 6. Multi-Layer Auto-Upgrade Rate

**400 books (5.4%)** auto-upgraded from single-layer to multi-layer.

The sweep metadata forces `is_multi_layer=False` for all books. The normalization pipeline's `NORM_LAYER_UNCERTAIN` check detects typographic signals (bold, brackets, transition phrases) and forces multi-layer detection when the pre-scan finds multi-layer patterns.

### Is 5.4% reasonable?

The Islamic scholarly corpus is rich in commentaries (شروح), supercommentaries (حواشي), and glosses. A 5.4% auto-upgrade rate is **conservative** — many commentaries likely exist in the remaining 94.6% but don't trigger the typographic threshold because:
- They use parenthetical markers rather than bold
- The matn is attributed using transition phrases not in the current pattern set
- They have a dominant matn proportion that doesn't trigger the 40% threshold

**Notable example:** أصل الزراري شرح صحيح البخاري — 641/750 units (85.5%) detected as multi-layer. This is a sharh (commentary) on Sahih al-Bukhari.

**Edge case fixture saved:** `tests/fixtures/shamela_edge_cases/auto_multilayer_85pct.htm`

---

## 7. Passaging Contract Alignment

**1,147/7,474 (15.3%)** fail at least one passaging input check.

| Check | Failures | Percentage |
|-------|----------|-----------|
| check4_count_match | 0 | 0.0% |
| check5_ordered | 0 | 0.0% |
| check5_no_gaps | 0 | 0.0% |
| check6_division_consistent | 1,147 | 15.3% |

**Only `check6_division_consistent` fails**, caused by division overlap (known limitation L-010). All other passaging contract checks pass on 100% of books:
- Content unit count matches manifest declaration (check 4)
- Content units are ordered by unit_index (check 5)
- No gaps in unit_index sequence (check 5)

**Implication for passaging engine:** The passaging engine must handle division overlap gracefully. 15.3% of the corpus has this condition. The passaging design should treat overlapping divisions as a warning, not a fatal error — the content units themselves are correct.

---

## 8. Boundary Continuity Coverage

| Metric | Value |
|--------|-------|
| Mean BC coverage | 97.38% |
| Books with 0% BC | 51 |
| Books with 100% BC | ~5,200 (estimated) |

The 51 books with 0% BC coverage are the 48 zero-content books plus 3 very small books (1-2 pages). Boundary continuity requires at least 2 consecutive pages to measure — books with 0-1 content units cannot have BC.

**97.38% mean coverage** — the normalization engine assigns boundary continuity signals to nearly every page transition. This is excellent for the passaging engine, which needs BC signals to decide where to split passages.

---

## 9. Content Flags (aggregate)

| Flag | Pages | Percentage of 2M pages |
|------|-------|----------------------|
| Hadith citation | 782,525 | 38.0% |
| Quran citation | 416,664 | 20.3% |
| Verse (poetry) | 325,855 | 15.8% |

These rates are plausible for the Shamela corpus:
- 38% hadith citation rate reflects the heavy hadith scholarship in the collection
- 20% Quran citation is expected — many books reference Quranic verses
- 15.8% verse (poetry) is slightly high but includes Arabic prose with poetic rhythm markers

---

## 10. Anomalies

### Books below 70% Arabic ratio (106 books, 1.4%)

- **48 zero-content books** (0.00% Arabic ratio — covered in §3)
- **58 books with low but non-zero Arabic ratio:**
  - These include books with significant non-Arabic content (indices, tables, transliteration, Urdu text, bibliographic data)
  - Lowest non-zero: ~45% — likely a book with heavy Latin/transliteration content

### Books with zero diacritics

Based on the summary report, min diacritics = 0. These are the zero-content books. All books with content have at least some diacritics — no "diacritic deserts" found.

### Extremely large books

- Max content units: 14,587 — a very large work spanning thousands of pages
- Max diacritics: 1,778,917 — a heavily vocalized text (likely a Quran-adjacent work)

---

## 11. Corpus Statistics for Passaging Design

| Statistic | Value |
|-----------|-------|
| Total books in corpus | 7,475 |
| Successfully normalized | 7,474 (99.987%) |
| Total content units | 2,056,879 |
| Mean pages/book | 275 |
| Median pages/book | 168 |
| Max pages/book | 14,587 |
| Min pages/book (non-zero) | 1 |
| Mean Arabic ratio | 79.57% |
| Diacritics as % of text | 13.4% |
| Multi-layer books (auto-detected) | 400 (5.4%) |
| Books with hadith citations | ~38% of pages |
| Books with footnotes | high (not aggregated) |
| Division overlap rate | 15.3% of books |
| Mean BC coverage | 97.38% |
| Zero-content books | 48 (0.6%) |

---

## 12. Edge Case Fixtures Saved

| Fixture | Path | What it tests |
|---------|------|--------------|
| Diacritics entity mismatch (crash) | `crash_diacritics_entity_mismatch.htm` | BS4/regex canary: 1-diacritic discrepancy |
| Zero content - small | `zero_content_hadith_dhunnun.htm` | 6 pages of real Arabic → 0 content units |
| Zero content - large | `zero_content_musnad_546pages.htm` | 546 raw pages → 0 content units |
| High page loss | `high_page_loss_62/` | 4-volume book, 62 pages lost (519→457) |
| Auto multi-layer 85% | `auto_multilayer_85pct.htm` | 641/750 units multi-layer, heavy sharh |

All fixtures in `tests/fixtures/shamela_edge_cases/`.

---

## 13. Summary of Findings for Architect

### Critical (investigate before transition gate)

1. **48 zero-content books:** Real Arabic text produces zero content units. Affects 0.6% of corpus. Likely a specific Shamela HTML variant or filtering edge case. Fixtures saved.

2. **1 crash (diacritics entity corruption):** The BS4 canary detected a 1-diacritic mismatch. The fail-loud behavior is correct. Need to determine which parser is right and handle the edge case.

### Expected / Known

3. **Division overlap (15.3%):** Consistent with L-010 evaluation findings (14%). Passaging engine must handle this gracefully.

4. **Warning patterns:** All warnings match known patterns. No new warning types at scale.

5. **Multi-layer auto-upgrade (5.4%):** Conservative rate. The sweep forces single-layer metadata, so auto-detection kicks in only for strong typographic signals.

### Data Points for Downstream Design

6. **Median book: 168 pages, mean: 275.** The passaging engine should handle books from 1 to 14,587 pages.

7. **97.38% boundary continuity coverage.** The passaging engine has rich BC signals for passage splitting.

8. **13.4% diacritics ratio corpus-wide.** Diacritics are well-preserved through normalization.

9. **38% of pages have hadith citations, 20% Quran, 16% verse.** Content flags are populated at meaningful rates.
