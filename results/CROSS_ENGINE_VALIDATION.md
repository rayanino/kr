# Cross-Engine Validation Report

**Date:** 2026-03-22
**Source:** Phase E source engine results (70 books) vs normalization sweep
**Cost:** 0 EUR (deterministic only)

## 1. Overview

| Metric | Value |
|--------|-------|
| Phase E books in source manifest | 70 |
| Books matched in normalization sweep | 70 |
| Normalization OK | 70 |
| Normalization crashes | 0 |
| Success rate | 100.0% |

## 2. Crashes

**None.** All 70 books that the source engine processed also normalize successfully.

## 3. Multi-Layer Detection Comparison

Comparing source engine LLM `is_multi_layer` with normalization auto-detection.

| Metric | Value |
|--------|-------|
| Books compared | 70 |
| Agreement | 61 (87%) |
| Disagreement | 9 |

### Disagreements

| Book | Source (LLM) | Norm (auto) | Multi-layer units |
|------|-------------|-------------|-------------------|
| أصل الزراري شرح صحيح البخاري - مخطوط | False | True | 641 |
| أصول أهل السنة والجماعة | False | True | 3 |
| ألقاب الشعراء ومن يعرف منهم بأمه - ضمن نوادر المخطوطات | False | True | 16 |
| السواك وسنن الفطرة - المقدم | False | True | 4 |
| الفوائد الأصولية - ضمن «آثار المعلمي» | False | True | 11 |
| النظام القضائي في الفقه الإسلامي.htm | False | True | 14 |
| تدارك بقية العمر في تدبير سورة النصر | False | True | 3 |
| حاشية الصبان على شرح الأشمونى لألفية ابن مالك | False | True | 419 |
| فقه الصيام والحج من دليل الطالب | False | True | 10 |

> **Note:** Disagreements where source says single-layer but normalization 
> auto-detects multi-layer suggest the normalization engine's typographic 
> detection is finding layer signals the LLM missed, or vice versa.

## 4. Content Unit Counts vs Source Engine Page Counts

| Metric | Value |
|--------|-------|
| Total source engine pages | 41380 |
| Total normalization content units | 44670 |
| Books with page loss > 5 | 0 |

## 5. Gate Abort Books — Normalization Behavior

Books where source engine LLM processing was gate_abort (insufficient scholar data).

| Metric | Value |
|--------|-------|
| Gate abort books | 16 |
| Successfully normalized | 16 |
| Failed to normalize | 0 |

> Gate abort is a source engine LLM issue (insufficient scholar data for consensus). 
> The normalization engine operates on the raw HTML, independent of LLM metadata. 
> All gate_abort books normalize fine because normalization is deterministic.

## 6. Normalization Quality Metrics (Phase E Subset)

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Arabic ratio | 79.6% | 64.9% | 88.2% |
| BC coverage | 95.5% | 50.0% | 100.0% |
| Warnings | 29.3 | 0 | 1812 |
| Multi-layer units | 66.0 | 0 | 1186 |

## 7. Conclusion

**Cross-engine compatibility: PASS.** All 70 Phase E books normalize 
successfully with 0 crashes. The normalization engine handles every book the source 
engine can process, regardless of LLM gate status.

Key findings:
- 100% normalization success rate on Phase E books
- Gate abort books normalize identically to success books (normalization is LLM-independent)
- 9 multi-layer detection disagreements warrant review
- Page loss patterns consistent with full corpus sweep (B.9)
