# Source Engine Deterministic Sweep — CC Analysis

**Date:** 2026-03-21
**Script:** `scripts/phases/run_phase_a.py`
**Collection:** `shamela-export-samples/` (7,475 items)
**Duration:** 124.5 seconds (2.1 minutes)
**Cost:** 0 EUR (fully deterministic, no LLM calls)

---

## 1. Overall Results

| Metric | Value |
|--------|-------|
| Total items | 7,475 |
| Successful | 7,475 (100.0%) |
| Errors | 0 (0.0%) |
| Avg processing time | 16.7ms per item |
| Slowest item | فتاوى الشبكة الإسلامية (910.1ms) |

### UNSUPPORTED_FORMAT Note

**Per NEXT.md Task B Step 6:** The source sweep iterates ALL items in the collection directory. `SRC_UNSUPPORTED_FORMAT` errors are expected for non-book items (metadata files, etc.).

**Finding:** This collection contains exclusively Shamela HTML content — every item is either a `.htm` file or a directory containing `.htm` files. There are **zero non-book items** in the collection, so:

- **Total errors (including UNSUPPORTED_FORMAT):** 0
- **Genuine errors (excluding UNSUPPORTED_FORMAT):** 0
- **UNSUPPORTED_FORMAT errors:** 0

The format detection correctly classified all 7,475 items as `shamela_html`.

---

## 2. Format Detection

| Format | Count | Percentage |
|--------|-------|-----------|
| shamela_html | 7,475 | 100.0% |

All items detected as Shamela HTML. No ambiguous formats, no detection failures.

### Volume Distribution

| Type | Count | Percentage |
|------|-------|-----------|
| Single-file books (.htm) | 5,576 | 74.6% |
| Multi-volume books (directories) | 1,899 | 25.4% |

**Note for passaging design:** One quarter of the corpus consists of multi-volume works. The passaging engine needs robust multi-volume handling from the start.

---

## 3. Metadata Field Coverage

Fields extracted from 7,475 successful items, sorted by coverage:

| Field | Count | Coverage |
|-------|-------|---------|
| is_multi_volume | 7,475 | 100.0% |
| volume_count | 7,475 | 100.0% |
| has_muqaddima | 7,475 | 100.0% |
| display_title | 7,475 | 100.0% |
| author_short | 7,475 | 100.0% |
| shamela_category | 7,475 | 100.0% |
| title_full | 7,475 | 100.0% |
| shamela_publish_date | 7,475 | 100.0% |
| body_page_count | 7,475 | 100.0% |
| page_count | 7,475 | 100.0% |
| text_sample | 7,474 | 99.99% |
| author_name_raw | 7,212 | 96.5% |
| publisher | 6,510 | 87.1% |
| page_count_raw | 5,286 | 70.7% |
| edition_raw | 5,252 | 70.3% |
| edition_number | 5,143 | 68.8% |
| edition_year_hijri | 4,785 | 64.0% |
| author_name_clean | 4,445 | 59.5% |
| author_death_hijri | 4,233 | 56.6% |
| edition_year_miladi | 4,127 | 55.2% |
| muhaqiq_name_raw | 3,468 | 46.4% |
| volume_count_raw | 1,723 | 23.1% |
| preparer | 1,059 | 14.2% |
| author_birth_hijri | 396 | 5.3% |
| muhaqiq_name_clean | 341 | 4.6% |
| muhaqiq_death_hijri | 325 | 4.3% |
| publication_year_raw | 312 | 4.2% |
| editorial_note | 212 | 2.8% |
| source_note | 194 | 2.6% |
| foreword_by | 156 | 2.1% |
| distributor | 104 | 1.4% |
| supervisor | 78 | 1.0% |
| thesis_info | 71 | 0.9% |
| original_author_name_raw | 46 | 0.6% |
| riwayah | 45 | 0.6% |
| compiler_name_raw | 44 | 0.6% |
| commentator_name_raw | 42 | 0.6% |
| translator | 9 | 0.1% |

### Observations

1. **Core fields (100%):** Title, category, author_short, page counts, volume info — all extracted from every book.
2. **text_sample gap:** 1 book (of 7,475) has no text_sample. This means the book either has no body content or the first page has no extractable text. Worth investigating — may be an empty/placeholder book.
3. **Author name coverage:** `author_name_raw` at 96.5% (263 missing) vs `author_name_clean` at 59.5% — the clean parsing regex fails on 37% of books that have raw names. This is an area for LLM inference in Phase B.
4. **Author death date:** Only 56.6% — meaning 43.4% of books will need LLM inference or external lookup for scholar identification. The trust evaluator's first-intake scoring (death ≤ 1000 → 0.90; > 1000 → 0.70; None → 0.30) will assign low trust to nearly half the corpus.
5. **Muhaqiq (editor):** 46.4% have raw names but only 4.6% have clean names — the muhaqiq parsing is much less robust than author parsing.
6. **Rare scholarly roles:** commentator (0.6%), compiler (0.6%), original_author (0.6%), translator (0.1%) — these are genuine minority cases in the corpus.

---

## 4. Duplicate Detection

**1 duplicate group found:**

| Hash | Sources |
|------|---------|
| `0eef3482...` | النكت على شرح النووي على صحيح مسلم (dir), النكت على شرح النووي على صحيح مسلم.htm (file) |

This is the same book existing as both a single .htm file and a directory. The deduplication logic in the source engine should handle this correctly — the composite hash matches because the content is identical.

**Duplicate rate:** 1 group out of 7,475 items = 0.01%. Extremely low, indicating the collection is well-curated.

---

## 5. Quality Issues

| Issue Type | Count | Percentage | Description |
|-----------|-------|-----------|-------------|
| page_count_mismatch | 158 | 2.1% | Declared page count != actual PageText divs |
| truncation_with_mismatch | 47 | 0.6% | Content appears truncated + page count mismatch |
| content_minimal | 16 | 0.2% | Very little extractable content |
| high_empty_ratio | 1 | 0.01% | High proportion of empty pages |
| **Total** | **222** | **3.0%** | |

### Analysis

- **page_count_mismatch (158):** The Shamela header declares a page count but the actual HTML has a different number of PageText divs. This is a known issue (per EVALUATION_REPORT.md: "29.8% of Shamela has duplicate/non-sequential page numbers"). The normalization engine correctly uses unit_index instead of page numbers.
- **truncation_with_mismatch (47):** Books where content appears cut short AND the page count is wrong — these may be incomplete exports or corrupted files. Worth cross-referencing with normalization results to see if these also cause normalization failures.
- **content_minimal (16):** Books with very little text. Could be metadata-only entries, empty collections, or very short treatises (رسائل). Check if these normalize to near-zero content units.
- **high_empty_ratio (1):** Single book with mostly empty pages — could be a placeholder or badly corrupted export.

---

## 6. Timing Analysis

| Metric | Value |
|--------|-------|
| Total time | 124.5 seconds |
| Mean per item | 16.7ms |
| Slowest | فتاوى الشبكة الإسلامية (910.1ms) |

The slowest book is 54x slower than average — likely a very large multi-volume work or a book with unusual HTML structure requiring more parsing time. Even at 910ms, this is well within acceptable bounds for a deterministic pipeline step.

---

## 7. Findings for Architect Review

### No Action Needed (Observations Only)

1. **100% format detection accuracy** — the collection is homogeneous (all Shamela HTML). The source engine's format detection handles this flawlessly.
2. **Zero extraction errors** — every item extracts successfully. The robustness of the extraction pipeline is confirmed at scale.
3. **1 duplicate** — expected and harmless. Deduplication works correctly.
4. **222 quality issues (3%)** — all are non-blocking warnings, not errors.

### Potential Improvements (for architect consideration)

1. **author_name_clean parsing (59.5% success):** The clean-name regex may be too strict. 37% of books with raw names fail clean parsing. Consider expanding the regex or adding fallback patterns.
2. **muhaqiq_name_clean (4.6% success):** Editor name cleaning extracts clean names from only 10% of books that have raw muhaqiq names. This is a much larger gap than author names.
3. **text_sample coverage (99.99%):** 1 book has no text sample. Minor but worth investigating — could indicate an edge case in content extraction.
4. **truncation_with_mismatch (47 books):** These books may be corrupted exports. Consider adding a quality flag that downstream engines can use to skip or handle these differently.

---

## 8. Corpus Statistics for Passaging Design

| Statistic | Value |
|-----------|-------|
| Total books | 7,475 |
| Multi-volume books | 1,899 (25.4%) |
| Single-file books | 5,576 (74.6%) |
| With muqaddima | 7,475 (100%) |
| With publisher info | 6,510 (87.1%) |
| With edition info | 5,252 (70.3%) |
| Quality issues | 222 (3.0%) |
| Duplicates | 1 pair |
