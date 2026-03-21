# Cross-Engine Findings Report

**Date:** 2026-03-21
**Engines:** Source (deterministic, Phase A) + Normalization (full pipeline)
**Collection:** `shamela-export-samples/` (7,475 items)
**Cost:** 0 EUR (both sweeps fully deterministic)

---

## 1. Cross-Engine Success Rates

| Engine | Processed | Success | Failures | Rate |
|--------|-----------|---------|----------|------|
| Source (Phase A) | 7,475 | 7,475 | 0 | 100.0% |
| Normalization | 7,475 | 7,474 | 1 | 99.987% |

**One book fails in normalization but succeeds in source:**
- مواقف النبي - صلى الله عليه وسلم - في الدعوة إلى الله تعالى
- Source: extracts metadata successfully
- Normalization: crashes on `NORM_DIACRITICS_ENTITY_CORRUPTION` (BS4/regex canary mismatch)

**Zero books fail in source but succeed in normalization** — the source engine's 100% success rate means it never blocks the normalization engine.

---

## 2. Common Failure Patterns

### Source Engine

No failures. Zero errors across all 7,475 items. The deterministic pipeline (format detection + extraction + hashing) is fully robust for this collection.

### Normalization Engine

Only 1 crash (diacritics canary). However, 48 books produce zero content units despite having valid HTML. These are "silent failures" — the books succeed (status=OK) but produce no useful output. The source engine extracts these same books successfully, confirming the content exists.

### Cross-Engine Observation

The normalization engine is the first point where content quality matters. The source engine only detects format and extracts metadata — it never processes page content. The normalization engine's 6-pass pipeline processes every page, which is where the 48 zero-content books fail silently.

---

## 3. Corpus Statistics for Passaging Design

### Book Size Distribution (content units)

| Percentile | Content Units | Description |
|-----------|---------------|-------------|
| Min | 1 | Single-page treatise |
| P10 | 20 | Short risala |
| P25 | 53 | Short book |
| Median | 170 | Typical book |
| P75 | 421 | Large book |
| P90 | 588 | Major work |
| P99 | 1,413 | Multi-volume opus |
| Max | 14,587 | الجامع الصغير وزيادته |

**Passaging implication:** The engine must handle 3 orders of magnitude in book size (1 to 14,587 pages). Passage chunking strategies that work for 170-page books may fail on 14,587-page books (memory, indexing). Design for the P99 case (1,413 pages) at minimum, with a separate strategy for outliers.

### Footnote Density

| Metric | Value |
|--------|-------|
| Mean | 26.2% of pages have footnotes |
| Median | 0.0% |
| P90 | 84.3% |
| Books with 0% footnotes | 3,920 (52.8%) |

**Bimodal distribution:** Half the corpus has zero footnotes, but among books with footnotes, density is high (median ~50%, P90 at 84%). The passaging engine should handle footnote-rich and footnote-free books as distinct modes.

### Multi-Layer Frequency

| Category | Count | Percentage |
|----------|-------|-----------|
| Single-layer (metadata) | 7,075 | 94.7% |
| Auto-upgraded to multi-layer | 400 | 5.4% |

The 5.4% auto-upgrade rate is conservative (sweep forces `is_multi_layer=False` for all books). With real metadata from the source engine's LLM inference, the true multi-layer rate is likely 15-25% based on the Islamic scholarly corpus composition (sharh, hashiya, tahqiq).

### Volume Distribution

| Type | Count | Percentage |
|------|-------|-----------|
| Single-file | 5,576 | 74.6% |
| Multi-volume | 1,899 | 25.4% |

The passaging engine receives multi-volume books as a single normalized package (content units indexed 0 to N). Volume boundaries are encoded in the division tree as top-level divisions. No special multi-volume handling needed beyond respecting division structure.

### Content Flag Distribution

| Flag | Pages | Percentage of 2M pages |
|------|-------|----------------------|
| Hadith citation | 782,525 | 38.0% |
| Quran citation | 416,664 | 20.3% |
| Verse (poetry) | 325,855 | 15.8% |

These flags feed directly into the passaging engine's passage boundary decisions — a passage should not split in the middle of a hadith chain or Quranic quotation.

### Boundary Continuity

| Metric | Value |
|--------|-------|
| Mean coverage | 97.38% |
| Books with 0% BC | 51 (0.7%) |

97% of page transitions have boundary continuity signals. The passaging engine has strong signals for: mid-paragraph (continue), mid-sentence (caution), section-break (good split point), mid-argument (avoid splitting).

### Diacritics Preservation

| Metric | Value |
|--------|-------|
| Total diacritics | 286,033,196 |
| Diacritics as % of text | 13.4% |
| Zero-diacritic books | 48 (zero-content only) |

Every book with content preserves its diacritics through normalization. 13.4% diacritics ratio is consistent with the mixed corpus (some fully vocalized works, many partially vocalized).

---

## 4. Top 10 Most Unusual Books

### Zero-Content (highest anomaly score)

| # | Book | Raw Pages | What Makes It Unusual |
|---|------|-----------|----------------------|
| 1 | مسند أبي حنيفة رواية الحصكفي | 546 | Largest zero-content: 546 pages → 0 units |
| 2 | فوائد ابن دحيم | 168 | 168 pages of hadith → 0 units |
| 3 | حديث عباس الترقفي | 129 | Hadith collection, completely empty after normalization |
| 4 | فوائد أبي عبد الله النعالي | 102 | Same pattern |
| 5 | منتخب من حديث يونس بن عبيد | 96 | Same pattern |

### Non-Empty Unusual Books

| # | Book | What Makes It Unusual |
|---|------|-----------------------|
| 6 | تفسير ابن عاشور التحرير والتنوير | 36 page loss + 841,732 diacritics (heavily vocalized tafsir) |
| 7 | موسوعة الرقائق والأدب | 8,319 pages, 1.5M diacritics — one of the largest works |
| 8 | الجامع الصغير وزيادته | 14,587 pages — the single largest work in the corpus |
| 9 | الشرح الصوتي لزاد المستقنع | 8,426 pages — audio transcription of sharh |
| 10 | أصل الزراري شرح صحيح البخاري | 85% auto-detected multi-layer — heaviest commentary |

---

## 5. Quality Issues Across Both Engines

### Source Engine Quality Issues (222 items, 3%)

| Issue | Count | Cross-Reference |
|-------|-------|----------------|
| page_count_mismatch | 158 | Header count ≠ actual pages — normalization uses unit_index instead |
| truncation_with_mismatch | 47 | Potentially incomplete exports — check normalization output |
| content_minimal | 16 | Very little content — some overlap with normalization zero-content |
| high_empty_ratio | 1 | Single book with mostly empty pages |

### Normalization Warning Patterns (15,400 warnings)

| Warning | Count | Architectural Impact |
|---------|-------|---------------------|
| char_run | 8,248 | Formatting artifacts — passaging should ignore |
| low_arabic_ratio | 4,530 | Per-page warning — some pages have non-Arabic content |
| division_overlap | 2,543 | L-010: passaging must handle overlapping divisions |
| other | 79 | Edge cases — no systematic pattern |

### Cross-Engine Correlation

- **content_minimal (source) vs zero-content (normalization):** Only 1 of the 16 source `content_minimal` books appears in the normalization zero-content list (الأول من الخلعيات: 2 content pages in source, 0 units in normalization). The other 15 content_minimal books normalize successfully. This means content_minimal in source doesn't predict zero-content in normalization.

- **truncation_with_mismatch (source) vs high page loss (normalization):** The 47 truncation books should be cross-referenced with normalization's high-page-loss books. Both engines detect the same underlying issue (incomplete export) through different mechanisms.

---

## 6. Findings Summary for Architect

### Critical Investigation Items

1. **48 zero-content books** — source extracts them fine, normalization produces zero output. The content exists in HTML but something in the 6-pass pipeline eliminates all pages. This is the only cross-engine discrepancy.

2. **1 diacritics canary crash** — the canary works correctly (detects BS4/regex mismatch). Need to determine which parser is right.

### Passaging Design Inputs

3. **Book sizes span 1 to 14,587 pages** (median 170, P99 1,413). Design for the long tail.
4. **52.8% of books have zero footnotes**, but among footnoted books, density is high. Bimodal.
5. **15.3% of books have division overlap** — passaging must not treat this as an error.
6. **97.38% boundary continuity coverage** — strong signal for passage splitting.
7. **5.4% auto-detected multi-layer** (conservative; real rate with LLM metadata likely 15-25%).

### No Action Required

8. Source engine: 100% success, zero errors, robust at scale.
9. Both engines: consistent behavior between 63-fixture evaluation and 7,475-book corpus.
10. Warning patterns: no new types emerged at scale — the 63 fixtures were representative.
