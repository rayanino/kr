# Phase A Lessons — Shamela HTML Extractor Bug Fixes

**Date:** 2026-03-10
**Scope:** 5 fixes in `engines/source/src/extractors/shamela_html.py`
**Collection:** 2,519 Shamela desktop HTML exports

---

## Bugs Found and Fixed

### Bug 1 + Fix 5 (CRITICAL): القسم header line leaking into field parsing

**Root cause:** `_RE_FIELD.finditer()` matched the card header line (`TITLE&nbsp;(AUTHOR)القسم: CATEGORY`) as a bibliographic field. After `strip_tags()`, the label ended with `القسم`.

**Impact:**
- Bug 1: 32 books had Shamela category (e.g., "كتب السنة") falsely assigned as `muhaqiq_name_raw` because MUHAQIQ_KEYWORDS matched title words like تحقيق/تخريج/تعليق
- Fix 5: 2,193 books had redundant header data cluttering `_extra_card_fields`

**Fix:** Guard at top of field loop: `if "القسم" in label: continue`

**Verification:** 0 category-as-muhaqiq, 0 القسم in extra_card_fields.

### Bug 2 (CRITICAL): Format B colon-in-label value embedding (64 books)

**Root cause:** Two HTML card formats exist:
- Format A (standard): `<span class='title'>LABEL<font>:</font></span> VALUE`
- Format B (variant): `<span class='title'>LABEL <font>:</font> VALUE ... <font>:</font></span> CONTINUATION`

In Format B, the value is inside the `<span>` tag. The regex's non-greedy `(.*?)` expanded to a later colon, making group 1 = `LABEL : VALUE (المتوفى` and group 2 = just a fragment.

**Fix:** After `strip_tags()`, detect `:` in label → split on first `:` to recover real label and value. Space-join prefix+value (not colon-join) works universally.

**Verification:** أجنحة المكر الثلاثة now extracts full author with death date. author_name_raw: 2,375 → 2,423 (+48).

### Bug 3 (MODERATE): 32 books missing title_full despite having display_title

**Fix:** Fallback after field parsing: if `title_full` absent but `display_title` exists, copy it. Most of these 32 were actually resolved by Fix 2 (Format B الكتاب fields). Only 3 needed the fallback.

**Verification:** title_full: 2,472 → 2,519 (100%).

### Fix 4 (MINOR): 5 unmapped FIELD_MAP labels

Added: `تأليف` → author_name_raw (4 books), `بعناية` → muhaqiq_name_raw (3), `جمعها` → compiler_name_raw (3), `انتقاء` → compiler_name_raw (11), `تاريخ النشر` → publication_year_raw (4).

**Not added:** `رواية` (26 books) — hadith-specific narration label, needs owner decision.

---

## Final Metrics Comparison

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| successful | 2,519 | 2,519 | 0 (no regressions) |
| errors | 0 | 0 | 0 |
| title_full | 2,472 (98.1%) | 2,519 (100%) | +47 |
| author_name_raw | 2,375 (94.3%) | 2,423 (96.2%) | +48 |
| muhaqiq_name_raw | 1,372 (54.5%) | 1,350 (53.6%) | -22 (false positives removed) |
| category-as-muhaqiq | 32 | 0 | -32 |
| القسم in extra_card_fields | 2,193 | 0 | -2,193 |
| Processing time | 28.5s | 17.5s | -11s (cleaner data, less extra_card_fields) |

---

## Field Distribution Patterns

### High coverage (>90%)
- display_title, author_short, shamela_category, shamela_publish_date: 100%
- title_full: 100% (after fixes)
- author_name_raw: 96.2%

### Medium coverage (50–90%)
- publisher: 88.1%
- edition_raw: 73.8%
- page_count_raw: 73.1%
- author_death_hijri: 67.8%
- edition_year_hijri/miladi: ~60%
- muhaqiq_name_raw: 53.6%

### Low coverage (<5%)
- muhaqiq_death_hijri: 4.8%
- author_birth_hijri: 4.6%
- publication_year_raw: 3.9%
- editorial_note: 3.0%
- compiler_name_raw: 1.1%
- commentator_name_raw: 0.3%

---

## Quality Issue Patterns

| Issue | Count | Notes |
|-------|-------|-------|
| page_count_mismatch | 90 | Digital vs physical page count ratio anomalies — real Shamela data quality issues |
| truncation_with_mismatch | 32 | Last page lacks sentence-ending punctuation + page mismatch — likely partial exports |
| content_minimal | 10 | Books with <3 content pages |

These are NOT extraction bugs — they reflect genuine data quality characteristics of the Shamela exports.

---

## Recommendations for Step 3 (LLM Probes)

1. **96 books missing author_name_raw** — these need LLM inference from text_sample + author_short. The author_short (from card header) is always present and provides a starting point.

2. **Remaining 57 books with author_short only** (subset of the 96) — no card field author at all. LLM must infer from text sample and contextual clues.

3. **`رواية` label (26 books)** — needs owner decision on mapping before Step 3. Currently in extra_card_fields.

4. **Zero duplicate groups** — deduplication logic found no exact-hash or title+author matches, confirming collection diversity.

5. **muhaqiq_name_raw at 53.6%** — roughly half the collection has editorial attribution. For the other half, LLM can infer tahqiq status from text features (critical apparatus, footnote density, etc.).
