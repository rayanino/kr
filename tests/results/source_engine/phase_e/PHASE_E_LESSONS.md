# Phase E Lessons Learned

**Phase:** E — Edge-Case LLM Probes
**Date:** 2026-03-21
**Books processed:** 70
**Cost:** €7.00 (€0.10/book average)
**Pipeline version:** d4aeb44

---

## Results Summary

| Metric | Value |
|--------|-------|
| Total books | 70 |
| Success | 54 (77.1%) |
| Gate abort | 16 (22.9%) |
| Errors | 0 (0.0%) |
| Consensus disagreements | 0 |
| Sanity check failures | 0 |
| Cost | €7.00 |
| Runtime | ~18 minutes |

**Comparison with Phase D:**
- Phase D: 204/204 success (100%), 0 gate aborts
- Phase E: 54/70 success (77.1%), 16 gate aborts, 0 errors
- The higher gate abort rate is expected — Phase E specifically targeted edge cases with sparse metadata (anonymous manuscript collections, volume fragments, etc.)

## Patterns Observed

### 1. Gate aborts cluster around sparse-metadata book types

All 16 gate aborts are books with limited metadata:
- **Volume fragments** (الأول من الخلعيات, الخامس عشر من الخلعيات) — manuscript series volumes with no standalone author data
- **Hadith compilation fragments** (تسمية الإخوة, أحاديث يزيد بن أبي حبيب) — single-author excerpts from larger collections
- **Anonymous works** (آداب الأكل, يوم في بيت الرسول) — small treatises without clear attribution
- **Commentary fragments** (أصل الزراري شرح صحيح البخاري - مخطوط, حاشية الصبان) — sharh/hashiyah manuscripts

The gate correctly identifies these as needing human review rather than auto-accepting uncertain metadata.

### 2. Zero consensus disagreements

All 54 success books had full agreement between Opus 4.6 and Command A across all metadata fields. This is notable because Phase E included deliberately challenging books (sparse metadata, extreme sizes, multi-layer). The models are highly aligned even on edge cases.

### 3. Genre diversity achieved for 19/32 Shamela categories

Phase E targeted 24 thin categories. After Phase E, 19 of 32 Shamela categories now have ≥3 books with SourceMetadata. See genre coverage section below.

### 4. LLM multi-layer detection partially agrees with normalization

6 disagreements out of 54 compared books. All 6 were cases where normalization detected multi-layer content (auto_upgraded_multi=true) but the LLM classified is_multi_layer=false. See multi-layer comparison section below.

## What Worked

1. **Pipeline robustness confirmed** — 0 errors across 70 edge-case books, including formerly zero-content hadith compilations, extreme-size books, and manuscript fragments. The pipeline handles everything without crashing.

2. **Strategic book selection** — Building category mapping from source sweep JSONs (32 categories) instead of PHASE_D_CATEGORY_DISTRIBUTION.json (10 categories) revealed 14 zero-coverage categories that Phase D missed entirely.

3. **Formerly zero-content books work** — 5 of 7 formerly zero-content books succeeded. The 2 gate aborts (الخلعيات volumes) are appropriate — these are anonymous manuscript fragments where gate_abort is the correct response.

4. **Cost predictability** — €0.10/book continues to hold exactly: 70 × €0.10 = €7.00.

## What to Watch

1. **6 zero-coverage categories remain** — الفرائض والوصايا, الفرق والردود, المنطق, علوم الحديث, علوم الفقه والقواعد الفقهية, علوم القرآن وأصول التفسير still have zero processed books. Category 1 selection was capped at 25 books, which truncated alphabetically-later categories.

2. **Gate abort rate on manuscript fragments** — 22.9% overall, but concentrated in specific book types. If downstream work needs SourceMetadata for these types, the gate thresholds may need tuning.

3. **LLM multi-layer disagreements** — The LLM tends to classify as single-layer when normalization detects multi-layer. This may be because the LLM sees the text content (which might have subtle sharh markers) while normalization uses structural HTML patterns. Needs investigation for atomization engine design.

## Field Stability Notes

No field instability detected. All 54 success books produced complete SourceMetadata with all required fields populated. The consensus mechanism continues to be reliable.

## New Findings Not Seen in Phase D

1. **Manuscript volume fragments gate correctly** — Books like "الأول من الخلعيات" (vol 1 of a 20-volume manuscript) correctly trigger gate_abort because they lack standalone author/title metadata. This is by design.

2. **Heavy diacritic books succeed** — The 2 highest diacritic density books both succeeded, confirming the pipeline handles heavily vocalized texts correctly.

3. **Very small books (3-10 content units) succeed** — All 3 minimal-size books processed successfully, showing the pipeline doesn't require a minimum text length.

4. **Very large books succeed** — The 3 largest books (up to 14,587 content units) processed without timeout or error, confirming scale resilience.

---

## Genre Coverage Analysis

After Phase E, coverage across 32 Shamela categories:

| Category | Phase D | Phase E | Total | Status |
|----------|---------|---------|-------|--------|
| (الطبراني) | 1 | 1 | 2 | THIN |
| أصول الفقه | 7 | 1 | 8 | ≥3 |
| الأنساب | 0 | 3 | 3 | ≥3 |
| البلاغة | 3 | 0 | 3 | ≥3 |
| التاريخ | 2 | 1 | 3 | ≥3 |
| التجويد والقراءات | 0 | 3 | 3 | ≥3 |
| التخريج والأطراف | 0 | 3 | 3 | ≥3 |
| التراجم والطبقات | 1 | 2 | 3 | ≥3 |
| التفسير | 12 | 0 | 12 | ≥3 |
| الرقائق والآداب والأذكار | 0 | 4 | 4 | ≥3 |
| السياسة الشرعية والقضاء | 0 | 3 | 3 | ≥3 |
| السيرة النبوية | 0 | 3 | 3 | ≥3 |
| العقيدة | 1 | 6 | 7 | ≥3 |
| العلل والسؤلات الحديثية | 0 | 1 | 1 | THIN |
| الفتاوى | 4 | 0 | 4 | ≥3 |
| الفرائض والوصايا | 0 | 0 | 0 | ZERO |
| الفرق والردود | 0 | 0 | 0 | ZERO |
| الفقه الحنبلي | 0 | 5 | 5 | ≥3 |
| الفقه الحنفي | 2 | 0 | 2 | THIN |
| الفقه الشافعي | 1 | 0 | 1 | THIN |
| الفقه العام | 5 | 1 | 6 | ≥3 |
| الفقه المالكي | 1 | 0 | 1 | THIN |
| المنطق | 0 | 0 | 0 | ZERO |
| النحو والصرف | 4 | 1 | 5 | ≥3 |
| شروح الحديث | 4 | 1 | 5 | ≥3 |
| علوم الحديث | 0 | 0 | 0 | ZERO |
| علوم الفقه والقواعد الفقهية | 0 | 0 | 0 | ZERO |
| علوم القرآن وأصول التفسير | 0 | 0 | 0 | ZERO |
| كتب السنة | 11 | 5 | 16 | ≥3 |
| كتب اللغة | 1 | 0 | 1 | THIN |
| كتب عامة | 2 | 0 | 2 | THIN |
| مسائل فقهية | 1 | 2 | 3 | ≥3 |

**Summary:** 19/32 categories now have ≥3 books (up from ~8 in Phase D). 7 remain thin (1-2 books), 6 remain zero. The 6 zero-coverage categories were not reached because Category 1 selection was capped at 25 books — alphabetically later categories (الفرائض through علوم القرآن) were truncated.

---

## Multi-Layer LLM vs Normalization Comparison

**Scope:** 54 books with both LLM is_multi_layer and normalization auto_upgraded_multi classifications.

**Agreement:** 48/54 (88.9%)
**Disagreement:** 6/54 (11.1%)

All 6 disagreements follow the same pattern: **normalization says multi-layer, LLM says single-layer**.

| Book | LLM | Norm | Norm Ratio |
|------|-----|------|------------|
| أصول أهل السنة والجماعة | False | True | 33.3% |
| ألقاب الشعراء ومن يعرف منهم بأمه - ضمن نوادر المخطوطات | False | True | 50.0% |
| السواك وسنن الفطرة - المقدم | False | True | 23.5% |
| النظام القضائي في الفقه الإسلامي | False | True | 2.3% |
| تدارك بقية العمر في تدبير سورة النصر | False | True | 10.0% |
| فقه الصيام والحج من دليل الطالب | False | True | 62.5% |

**Interpretation:** The normalization engine detects multi-layer content via HTML structure patterns (bracket-delimited commentary, footnote-like insertions). The LLM classifies based on text content semantics. Low-ratio multi-layer books (2.3%, 10%, 23.5%) may have occasional structural markers that don't constitute a "true" multi-layer work in scholarly terms. This is expected — the normalization engine is conservative (any multi-layer content triggers the flag), while the LLM applies a scholarly definition.

**Impact on atomization engine:** Both signals should be available. The atomization engine should use normalization's structural detection (more sensitive) rather than LLM's semantic classification (more specific) for layer separation decisions.

---

## Formerly Zero-Content Books

7 formerly zero-content books were processed (from the 48 fixed in Task 2):

| Book | Status | Notes |
|------|--------|-------|
| الأول من الخلعيات | gate_abort | Expected — anonymous manuscript fragment |
| الخامس عشر من الخلعيات | gate_abort | Expected — same series |
| الرابع من معجم شيوخ الدمياطي | success | Dictionary of hadith narrators — good metadata |
| الثاني من المصباح في عيون الصحاح | success | Hadith anthology — clear attribution |
| حديث ذي النون المصري | success | Named hadith compilation — fixture book |
| فوائد ابن دحيم | success | Named hadith benefits — clear attribution |
| حديث عباس الترقفي | success | Named hadith compilation — clear attribution |

**Result:** 5/7 success (71.4%), 2/7 gate_abort. The 2 gate aborts are الخلعيات volumes — anonymous manuscript fragments where gate_abort is the correct behavior. All 5 success books produced valid SourceMetadata with appropriate genre, author, and structural classifications.

**Conclusion:** The Task 2 pageless-books fix enables these books to flow through the full pipeline. LLM inference works correctly on them. The pipeline correctly distinguishes between books with sufficient metadata (success) and anonymous fragments (gate_abort).

---

## Budget Status

| Phase | Books | Cost (EUR) | Status |
|-------|-------|------------|--------|
| 0 | 13 | 1.80 | complete |
| A | 2,519 | 0.00 | complete |
| C | 73 | 7.00 | complete |
| D | 204 | 20.40 | complete |
| E2E | 5 | 0.50 | complete |
| E | 70 | 7.00 | complete |
| **Total** | | **36.70** | |

Remaining budget: €63.30 (of €100 ceiling)

---

## Recommendations for Future Work

1. **Fill remaining zero-coverage categories** — 6 categories still have zero processed books. A targeted ~20-book selection from الفرائض والوصايا, الفرق والردود, المنطق, علوم الحديث, علوم الفقه والقواعد الفقهية, and علوم القرآن وأصول التفسير would complete coverage.

2. **Multi-layer disagreement investigation** — The 6 LLM-vs-normalization disagreements should be reviewed during atomization engine design. The normalization engine's structural detection may produce false positives at low ratios (2-10%).

3. **Gate abort threshold review** — 16 gate aborts in Phase E suggests the gate is correctly conservative, but the types of books that gate (manuscript fragments, anonymous compilations) are a known scholarly category. Consider whether these should have a specialized metadata path.
