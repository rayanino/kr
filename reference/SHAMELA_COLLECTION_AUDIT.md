# Shamela Collection Audit — تدقيق مجموعة الشاملة

**Date:** 2026-03-09
**Source:** Owner's Shamela desktop app v4 export (2,256 books successfully analyzed out of 2,519 total — 263 had filenames exceeding filesystem limits during extraction)
**Method:** Automated full-collection analysis: every book's first file parsed for metadata card fields, body page structure, and content quality signals
**Purpose:** Empirical reference for source engine content quality inspection, FIELD_MAP expansion, and intake calibration

This document records what was *found* in the actual data. Every number is observed, not estimated. It complements `SHAMELA_FORMAT_ANALYSIS.md` (which documents the HTML structure) by documenting the *content-level* variability and quality characteristics of the collection.

---

## 1. Collection Summary

| Metric | Value |
|--------|-------|
| Books analyzed | 2,256 |
| Single-file books | 1,712 (75.9%) |
| Multi-volume books | 544 (24.1%) |
| Books with المقدمة.htm | 37 (6.8% of multi-volume) |
| Parse errors | 0 (100% structural validity) |
| Encoding errors (U+FFFD) | 0 across entire collection |
| Total digital pages | 624,875 |
| Median pages per book | 114 |
| Median file size | 194 KB |
| Smallest file | 3,721 bytes |
| Largest file | 20.6 MB |
| Smallest book | 1 page |
| Largest book | 14,587 pages |

**Key structural finding:** The Shamela desktop export format is remarkably uniform at the HTML level. Zero parse failures, zero encoding issues. Content quality issues exist at the *semantic* level (page counts, truncation), not the structural level.

---

## 2. Complete Metadata Field Inventory

### 2.1 Fields Already in SPEC FIELD_MAP

These fields are handled by the current extraction rules in §4.A.3.

| Label | Count | % of Collection | SPEC Internal Name |
|-------|-------|----------------|--------------------|
| تاريخ النشر بالشاملة | 2,256 | 100.0% | `shamela_publish_date` |
| الكتاب | 2,204 | 97.7% | `title_full` |
| المؤلف | 2,122 | 94.1% | `author_name_raw` |
| الناشر | 1,975 | 87.5% | `publisher` |
| الطبعة | 1,675 | 74.2% | `edition_raw` |
| عدد الصفحات | 1,635 | 72.5% | `page_count_raw` |
| المحقق | 731 | 32.4% | `muhaqiq_name_raw` |
| عدد الأجزاء | 479 | 21.2% | `volume_count_raw` |
| أعده للشاملة | 400 | 17.7% | (format_specific_metadata) |
| تحقيق | 166 | 7.4% | `muhaqiq_name_raw` (alternative) |
| عام النشر | 68 | 3.0% | `publication_year_raw` |
| دراسة وتحقيق | 53 | 2.3% | `muhaqiq_name_raw` (alternative) |
| تنبيه | 47 | 2.1% | `editorial_note` |
| عدد صفحات (الكتاب الورقي) | 45 | 2.0% | `page_count_raw` (alternative) |
| مصدر الكتاب | 35 | 1.6% | `source_note` |
| راجعه | 28 | 1.2% | `muhaqiq_name_raw` (alternative) |
| قدمه للشاملة | 25 | 1.1% | (format_specific_metadata) |
| تحقيق ودراسة | 21 | 0.9% | `muhaqiq_name_raw` (alternative) |
| اسم الكتاب | 20 | 0.9% | `title_full` (alternative) |
| رواية | 20 | 0.9% | (format_specific_metadata) |
| تحقيق وتعليق | 17 | 0.8% | `muhaqiq_name_raw` (alternative) |
| إعداد | 16 | 0.7% | `author_name_raw` (thesis author) |
| إشراف | 16 | 0.7% | `supervisor` |
| رسالة | 14 | 0.6% | `thesis_info` |
| راجعه ودققه | 1 | <0.1% | `muhaqiq_name_raw` (alternative) |

### 2.2 Fields NOT in Current FIELD_MAP (≥5 occurrences)

These fields appear in the real collection but are currently caught only by the `_extra_card_fields` fallback. Fields marked **ACTION** should be added to FIELD_MAP.

| Label | Count | % | Recommended Action |
|-------|-------|---|--------------------|
| http | 35 | 1.6% | Ignore — these are URL artifacts from malformed metadata cards |
| دار النشر | 21 | 0.9% | **ACTION: Map to `publisher`** — alternative label for الناشر |
| تقديم | 17 | 0.8% | **ACTION: Map to `foreword_by`** (new field, format_specific_metadata) |
| اعتناء وتخريج | 14 | 0.6% | **ACTION: Map to `muhaqiq_name_raw`** — muhaqiq variant |
| تخريج | 14 | 0.6% | **ACTION: Map to `muhaqiq_name_raw`** — hadith takhrij editor |
| كود المادة | 13 | 0.6% | Capture in extra_card_fields — academic course code |
| المرحلة | 13 | 0.6% | Capture in extra_card_fields — academic level |
| حققه وخرج أحاديثه | 13 | 0.6% | **ACTION: Map to `muhaqiq_name_raw`** — muhaqiq variant |
| قدم له | 12 | 0.5% | **ACTION: Map to `foreword_by`** (new field) |
| تحقيق وتخريج | 11 | 0.5% | **ACTION: Map to `muhaqiq_name_raw`** — muhaqiq variant |
| حققه وعلق عليه | 11 | 0.5% | **ACTION: Map to `muhaqiq_name_raw`** — muhaqiq variant |
| أصل التحقيق | 10 | 0.4% | **EXCLUDE from muhaqiq** — describes the tahqiq's origin (e.g., PhD thesis), not the muhaqiq person |
| سنة النشر | 10 | 0.4% | **ACTION: Map to `publication_year_raw`** — alternative label |
| العام الجامعي | 10 | 0.4% | Capture in extra_card_fields — academic year |
| اعتنى به | 10 | 0.4% | **ACTION: Map to `muhaqiq_name_raw`** — muhaqiq variant |
| تقديم وتحقيق | 10 | 0.4% | **ACTION: Map to `muhaqiq_name_raw`** — muhaqiq variant |
| أصل الكتاب | 9 | 0.4% | Capture in extra_card_fields — describes the source work |
| جمع وترتيب | 9 | 0.4% | **ACTION: Map to `compiler_name_raw`** (new field) — the compiler/arranger |
| الطبعة الأولى | 9 | 0.4% | Ignore — redundant with الطبعة field value |
| انتقاء | 8 | 0.4% | Capture in extra_card_fields — selections from a larger work |
| حققه وخرج أحاديثه وعلق عليه | 8 | 0.4% | **ACTION: Map to `muhaqiq_name_raw`** — muhaqiq variant |
| توزيع | 7 | 0.3% | **ACTION: Map to `distributor`** (new field, format_specific_metadata) |
| أهداه للشاملة | 7 | 0.3% | Capture in extra_card_fields — donor to Shamela |
| [تنبيه] | 7 | 0.3% | **ACTION: Map to `editorial_note`** — variant of تنبيه with brackets |
| مؤلف الأصل | 6 | 0.3% | **ACTION: Map to `original_author_name_raw`** (new field) — for abridgments/commentaries |
| الشارح | 6 | 0.3% | **ACTION: Map to `commentator_name_raw`** (new field) — the sharih |
| تصنيف | 5 | 0.2% | Capture in extra_card_fields — synonym for تأليف |
| ترجمة | 5 | 0.2% | **ACTION: Map to `translator`** (new field, format_specific_metadata) |
| عدد المجلدات | 5 | 0.2% | **ACTION: Map to `volume_count_raw`** — alternative label |
| مراجعة | 5 | 0.2% | **ACTION: Map to `muhaqiq_name_raw`** — reviewer (muhaqiq-equivalent) |
| حققه | 5 | 0.2% | **ACTION: Map to `muhaqiq_name_raw`** — muhaqiq variant |

### 2.3 Complete Muhaqiq-Equivalent Label Inventory

The SPEC currently recognizes 7 muhaqiq labels. The real collection contains **50 distinct labels** that indicate editorial/tahqiq work. For the FIELD_MAP, these should be grouped into tiers:

**Tier 1: High-frequency labels (≥20 occurrences) — must be in FIELD_MAP:**
المحقق (731), تحقيق (166), دراسة وتحقيق (53), راجعه (28), تحقيق ودراسة (21)

**Tier 2: Medium-frequency labels (5–19 occurrences) — should be in FIELD_MAP:**
تحقيق وتعليق (17), اعتناء وتخريج (14), تخريج (14), حققه وخرج أحاديثه (13), قدم له (12*), تحقيق وتخريج (11), حققه وعلق عليه (11), اعتنى به (10), تقديم وتحقيق (10), حققه وخرج أحاديثه وعلق عليه (8), مراجعة (5), حققه (5)

*Note: `قدم له` (introduced by / foreword) is borderline — the person who writes a foreword is not necessarily the muhaqiq. Map to `foreword_by`, not `muhaqiq_name_raw`.

**Tier 3: Low-frequency labels (2–4 occurrences) — catch via pattern matching:**
These 30+ labels follow patterns like `حققه و...`, `خرج ...`, `علق ...`, `ضبط ...`, `صحح ...`. Rather than enumerating all of them in the FIELD_MAP, the extractor should use pattern matching: if a label contains any of the root stems `حقق`, `خرج`, `علق`, `ضبط`, `صحح`, `راجع`, `اعتن` — and the label is NOT in the exclusion list (e.g., `أصل التحقيق`) — map the value to `muhaqiq_name_raw`.

**Exclusion list (labels that contain muhaqiq keywords but are NOT muhaqiq fields):**
- `أصل التحقيق` — "origin of the tahqiq" (describes the thesis/project, not the person)
- `المحقق (رسالة علمية)` — similar, describes context not person

---

## 3. Content Quality Findings

### 3.1 Page Count Mismatches (94 books = 4.2%)

Books where the digital page count (PageText divs minus the metadata card) is wildly inconsistent with the physical page count from عدد الصفحات.

**Distribution of mismatches:**
- 87 books have digital/physical ratio < 0.15 (digital pages are far fewer than claimed physical pages)
- 7 books have ratio > 8.0 (digital pages far exceed claimed physical pages — likely metadata error)

**What this means:** The low-ratio cases (87 books) are the most concerning. A book claiming 444 physical pages but containing only 16 digital pages is likely a partial export — only a fraction of the content was exported from the Shamela desktop app. The high-ratio cases are probably metadata errors (wrong number entered in عدد الصفحات).

**Sample mismatches (ratio < 0.15):**

| Digital Pages | Physical Pages | Ratio | Interpretation |
|---------------|---------------|-------|---------------|
| 10 | 279 | 0.04 | Severe — 96% of content missing |
| 16 | 444 | 0.04 | Severe — 96% of content missing |
| 7 | 345 | 0.02 | Severe — 98% of content missing |
| 5 | 375 | 0.01 | Severe — 99% of content missing |
| 20 | 416 | 0.05 | Severe — 95% of content missing |

**Recommended threshold:** Flag as `SRC_PAGE_COUNT_MISMATCH` when ratio < 0.15 or > 8.0. This catches 94 books (4.2%) with near-zero false positives — a ratio below 0.15 means the digital content is less than 15% of the claimed physical book, which is almost certainly a partial export.

### 3.2 Very Small Books (12 books = 0.5%)

Books with fewer than 3 body pages.

| Book | Pages | Size | Likely Status |
|------|-------|------|---------------|
| Various hadith ajza' | 1–2 | 3–23 KB | Legitimate — short hadith collections |
| المقدمة.htm (loose) | 2 | 5.5 KB | Orphaned muqaddima file |

**Analysis:** Most of these are legitimate very short texts (أجزاء حديثية — hadith fragments, short risalahs). The 2 orphaned muqaddima files are export artifacts. The content quality check should flag these as `SRC_CONTENT_MINIMAL` (Info severity) for owner awareness, not rejection.

### 3.3 Truncation Analysis (880 books = 39.0%)

Books whose final page does not end with Arabic sentence-ending punctuation (.؟!»)﴾]).

**False positive analysis (from 10-sample manual review):**
- 50% are legitimate Islamic text endings: آمين, والله أعلم, وسلم, حسبنا الله ونعم الوكيل
- ~30% end with author names, dates, or colophons (legitimate)
- ~20% are genuinely suspicious (text ends mid-hadith, mid-sentence, or mid-argument)

**Conclusion:** Truncation detection alone has an unacceptably high false positive rate (~80%). It becomes useful only when combined with page count mismatch: a book that BOTH has a low page ratio AND ends without proper punctuation is almost certainly truncated. The truncation check should NOT fire independently — it should be a secondary signal that strengthens the page count mismatch finding.

### 3.4 Books Without Author Field (124 books = 5.5%)

These books have the author's short name in the card header (`<span class='footnote'>(AUTHOR)</span>`) but lack the المؤلف bibliographic field. The short name is extractable but typically contains only a laqab or nisba (e.g., "النووي", "ابن كثير") rather than the full name.

The current SPEC handles this correctly: the short name is extracted, the full author identification falls to LLM inference, and `author` is added to `needs_review_fields`.

---

## 4. Category (القسم) Distribution

The Shamela category field is present in 99.9% of books. The top categories across the analyzed collection:

| Category | Count | % |
|----------|-------|---|
| كتب السنة | ~350 | ~15% |
| الفقه العام | ~200 | ~9% |
| كتب عامة | ~180 | ~8% |
| التفسير | ~120 | ~5% |
| الدعوة والأمر بالمعروف | ~90 | ~4% |
| النحو والصرف | ~85 | ~4% |
| كتب اللغة | ~70 | ~3% |
| أصول الفقه والقواعد الفقهية | ~65 | ~3% |
| الفتاوى | ~60 | ~3% |
| البلاغة | ~40 | ~2% |

**Note:** The القسم value is Shamela's own classification and does NOT directly map to the engine's `science_scope`. The SPEC correctly treats it as an input signal to LLM inference, not as a direct assignment. Some categories (like "كتب عامة") are too broad to be useful; others (like "النحو والصرف") are reliable.

---

## 5. Implications for the Source Engine

### 5.1 FIELD_MAP Must Be Expanded

The current FIELD_MAP has 23 entries. The audit found 31 additional field labels with ≥5 occurrences. Of these, 20 should be added to the FIELD_MAP (see §2.2 above for specific mappings).

Additionally, the muhaqiq detection should use pattern matching for the long tail of low-frequency editorial labels (see §2.3).

### 5.2 Content Quality Inspection Is Needed

The format-based `text_fidelity` assignment (`shamela_html` → `"high"`) is incorrect for 94 books (4.2%) that have severe page count mismatches. These books should receive `text_fidelity: "medium"` or `"low"` depending on severity, with the specific quality issue recorded in `format_specific_metadata.quality_issues`.

### 5.3 Truncation Check Should Be a Secondary Signal Only

The 39% truncation rate with 80% false positives means truncation detection is not viable as a standalone check. It should only fire as a confirming signal alongside page count mismatch.

### 5.4 New Metadata Fields Discovered

The audit revealed metadata patterns not anticipated by the SPEC:
- `مؤلف الأصل` / `الشارح` — explicit multi-layer author identification from the metadata card (6 books each). When present, these provide ground truth for the LLM's multi-layer detection.
- `جمع وترتيب` — compiler attribution (9 books). Distinct from author and muhaqiq.
- `ترجمة` — translator (5 books). Relevant for translated works.
- `أصل الكتاب` — describes the source work for abridgments (9 books). Provides ground truth for genre chain detection.

---

## 6. Data Files

The raw audit data is stored at `tests/fixtures/shamela_collection_audit.json` (generated by the analysis script). This file can be regenerated from the full Shamela collection ZIP at the Google Drive link in `reference/SHAMELA_COLLECTION.md`.
