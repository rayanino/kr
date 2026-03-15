# Phase D Lessons Learned

**Phase:** D (Full-Scale Validation)
**Date:** 2026-03-13
**Books:** 204 (204 success, 0 gate_abort, 0 errors)
**Cost:** 20.4 EUR (budget ceiling: 100 EUR)
**Pipeline version:** b81d5cb

---

## Results Summary

- **100% success rate** — 204/204 books processed without errors or gate aborts
- **0 regressions** from Phase C reruns (51 gate_abort → success, 22 success → success)
- **9 edition groups** detected with consistent genre/author/multi-layer classification
- **20 multi-layer books** correctly identified (14 matn+sharh, 3 matn+sharh+hashiyah, 3 matn+sharh+tahqiq_note)
- **14 consensus disagreements** — all resolved via fallback path, no single-model results
- **174 clean books** (85.3%) with zero sanity check flags

## What Improved from Phase C

- **Gate abort rate: 70% → 0%**: Phase C had 51/73 gate_aborts, almost all from author-science mismatch in sparse scholar registry. Phase D fixed this by populating science_scope data for major scholars before the run.

- **Regression rate: 0%**: All 22 Phase C successes remained successful in Phase D. All 51 Phase C gate_aborts became successes. Zero regressions validates that the pipeline is stable across runs.

- **Sanity check flags: 83 → 30**: Phase C had 51 errors + 32 info flags. Phase D has 0 errors + 2 warnings + 28 info. The reduction reflects both pipeline improvements and better scholar registry data.

- **Cost efficiency**: Phase C was 0.096 EUR/book, Phase D was 0.10 EUR/book. Nearly identical, confirming predictable costs at scale.

## Patterns Observed

- **muhaqiq_not_in_context (26 flags)**: LLM detected a muhaqiq but the text sample didn't contain clear edition details. This is a data characteristic (many Shamela exports don't include tahqiq metadata in the text body), not a pipeline bug. The muhaqiq was correctly inferred from the metadata card.

- **genre_title_mismatch (4 flags)**: Title format conflicts with genre classification (e.g., poetry-style title on a non-poetry work). These are legitimate edge cases where the title structure doesn't match the content genre. Worth owner review.

- **Trust score clustering at 0.4325**: 24 books share the exact same trust score (0.4325). These are all modern works with no death date, no muhaqiq, and no known publisher — the trust algorithm produces the same score for identical factor profiles. This is correct behavior, not a bug.

- **Confidence outliers predominantly on `level` field**: 31 of 32 confidence outliers have low confidence on the `level` field. This matches Phase C's finding that both models systematically underestimate scholarly level for modern academic works.

## Field Stability Across Reruns

Of the 22 books that succeeded in both Phase C and Phase D, only 3 had any field changes:

| Book | Changed Field | Phase C | Phase D | Assessment |
|------|-------------|---------|---------|------------|
| التعليق على الرحيق المختوم | trust_score | 0.4625 | 0.4325 | Minor score shift from registry changes |
| لسان العرب | author | ...الرويفعي | ...الرويفعى | Cosmetic: ي vs ى (ya/alef maqsura) |
| معالم بيانية في آيات قرآنية | author | صالح... | أبو هاشم صالح... | Kunya added — more complete name |
| معالم بيانية في آيات قرآنية | trust_score | 0.4325 | 0.5000 | Improvement from registry enrichment |
| معالم بيانية في آيات قرآنية | science_scope | 3 scopes | 2 scopes | Dropped ulum_al_quran — arguably more precise |

All changes are minor and defensible. No field changed to a wrong value.

## What Worked

- **Scholar registry enrichment eliminated gate_aborts**: The Phase C recommendation to populate science_scope for major scholars was the single most impactful fix. 51 gate_aborts → 51 successes.

- **Edition group detection**: All 9 edition groups had consistent genre, author, and multi-layer classification across editions. This validates that the pipeline produces reproducible results regardless of which edition is processed.

- **Multi-layer detection at scale**: 20 multi-layer books correctly identified across 3 layer configurations (matn+sharh, matn+sharh+hashiyah, matn+sharh+tahqiq_note). Zero false positives or false negatives on the fixture-validated layer detection.

- **Category coverage**: 24 Shamela categories represented across 204 books, with largest groups being كتب السنة (77), كتب عامة (21), التفسير (18), النحو والصرف (17), الفقه العام (13).

## What to Watch

- **Level field confidence**: Both models consistently produce level confidence of 0.60-0.70 for modern academic works. This may need calibration in the inference prompt or acceptance of lower confidence as normal for this field.

- **14 consensus disagreements**: These are the highest-value items for Phase E review. The owner should examine whether the canonical model's choice was correct in each case.

- **69 flagged trust books** (trust_score < 0.65): All processed successfully. The flagged status is correct (modern works without established tahqiq tradition). The owner should decide whether any deserve trust override.

## Impact on Phase E

- **204 complete SourceMetadata records** ready for owner review in GUI
- Diverse genre coverage: all major genres represented (sharh, matn, risalah, hadith_collection, tafsir, fatawa, mawsuah, mujam, adab, nazm, other)
- Multi-layer books included (20 of 204) — validates normalization engine can receive varied inputs
- Edition groups provide natural cross-validation points for owner review

## Budget Status

| Phase | Books | Cost (EUR) | Per-Book |
|-------|-------|-----------|----------|
| Phase 0 | 13 | 1.8 | 0.14 |
| Phase A | 2,519 | 0.0 | 0.00 |
| Phase C | 73 | 7.0 | 0.10 |
| Phase D | 204 | 20.4 | 0.10 |
| Testing | — | 0.9 | — |
| **Total** | — | **30.1** | — |
| **Remaining** | — | **69.9** | — |

69.9% of budget remaining for Phase E and downstream engine development.
