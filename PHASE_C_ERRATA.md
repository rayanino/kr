# Phase C Errata — Corrections to Framework and Lessons

**Created:** 2026-03-10 (Calibration session)
**Purpose:** Corrections discovered during Phase 1 calibration. All future evaluation sessions MUST read this file before starting work.

---

## 1. LESSONS.md Contains Three Factual Errors

PHASE_C_LESSONS.md (Claude Code's self-assessment) states:

> "Command A (Cohere) completely unavailable... timed out on every single attempt... All books fell back to single-model mode... No consensus comparison occurred for any book."

**This is entirely false.** Verified by reading `consensus.json` and `llm_responses/` for all 73 books:

| Claim | Reality |
|-------|---------|
| "All books single-model fallback" | 0/73 books are single_model_fallback |
| "Command A timed out on every attempt" | 67/73 used Command A successfully (with real latencies 12-47s) |
| "No consensus comparison occurred" | 73/73 have dual-model consensus: 67 agreed, 6 disagreed |

Additionally, 6 books used **GPT-5.4** (not Command A) as the second model:
- أبنية الأسماء والأفعال والمصادر
- أنوار الهلالين في التعقبات على الجلالين
- الأذكار للنووي ت الأرنؤوط
- المستدرك على مجموع الفتاوى
- تفسير الطبري جامع البيان - ط دار التربية والتراث
- حاشية العطار على شرح الجلال المحلي على جمع الجوامع

**Action for evaluators:** Ignore LESSONS.md claims about model availability. Check `llm_responses/` directory contents per-book to identify the actual model pair (command_a.json or gpt_5_4.json).

---

## 2. Framework LLM Filename Wrong

The framework (§ Output File Structure) says:

> `llm_responses/opus_4_6.json and command_a.json`

**Actual filename:** `claude_opus_4_6.json` (not `opus_4_6.json`)

Second model is either `command_a.json` (67 books) or `gpt_5_4.json` (6 books).

---

## 3. Framework Section 7 (Single-Model Fallback) Is Inapplicable

The entire section "Single-Model Fallback Assessment" does not apply to Phase C:
- 0/73 books are single_model_fallback
- The 0.85 confidence cap for single-model biographical inference was never triggered
- `consensus["agreed"]` IS meaningful for all 73 books — both models ran
- Author confidence is NOT artificially capped

**Action for evaluators:** Skip Section 7 entirely. Instead, note that we have genuine dual-model consensus throughout. The 6 disagreements are real disagreements worth examining.

---

## 4. result.json Author Confidence Is Always 1.0 (ENGINE BUG)

`result["author"]["confidence"]` is always 1.0 for all 22 success books. This is NOT the LLM's identification confidence — it is the scholar registry's "new record" confidence (trivially 1.0 since Phase C starts with an empty registry).

The actual LLM author confidence is in:
`llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence`

**Range observed:** 0.55 (الورقة النحوية) to 0.99 (famous books).

Similarly, `result["confidence_scores"]` does NOT include an "author" field — the `InferredFieldConfidence` model in the engine drops it during assembly. The capped author confidence is computed in `metadata_inference.py:apply_confidence_caps()` but never surfaces in the final output.

**Action for evaluators:**
- NEVER read author confidence from result.json — it's meaningless
- ALWAYS read from llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence
- For confidence calibration analysis, use LLM values exclusively

---

## 5. Corrected Field Source Table

Replace the framework's "Field Evaluation Protocol" table with:

| Field | Source (success) | Source (gate_abort) | Notes |
|-------|-----------------|---------------------|-------|
| Author name | result["author"]["name_arabic"] | llm_responses/*["parsed"]["author_identification"]["canonical_name_ar"] | |
| Author confidence | **llm_responses/*["parsed"]["author_identification_confidence"]** | Same | NOT result["author"]["confidence"] (always 1.0) |
| Death date | llm_responses/*["parsed"]["author_identification"]["death_date_hijri"] | Same | |
| Genre | result["genre"] | llm_responses/*["parsed"]["genre"] | |
| Genre confidence | **llm_responses/*["parsed"]["genre_confidence"]** | Same | result confidence_scores.genre may differ (rounding) |
| Multi-layer | result["is_multi_layer"] | llm_responses/*["parsed"]["is_multi_layer"] | |
| Science | result["science_scope"] | llm_responses/*["parsed"]["science_scope"] | |
| Trust | result["trust_tier"] | NOT AVAILABLE — skip | |
| Attribution | result["attribution_status"] | llm_responses/*["parsed"]["attribution_status"] | |
| Model pair | consensus["successful_models"] | Same | Check for gpt_5_4 vs command_a |

---

## 6. Consensus Disagreement Analysis

The 6 "disagreed" books and their actual disagreement types:

| Book | Models | Disagreement Type | Substantive? |
|------|--------|------------------|-------------|
| أبنية الأسماء | Opus + GPT-5.4 | Genre (matn vs other) + name format + attribution | Yes |
| أعلام الموقعين - ط عطاءات العلم | Opus + Command A | Genre (matn vs usul_al_fiqh) + name format | Partially |
| إعلام الموقعين - ت مشهور | Opus + Command A | Name format only (same person: ابن القيم) | No |
| تحفة المودود - ط عطاءات العلم | Opus + Command A | Name format only (same person: ابن القيم) | No |
| تكملة حاشية ابن عابدين | Opus + Command A | Name format + death date (1306 vs null) | Partially |
| من أحاديث سفيان الثوري | Opus + Command A | Name format only (same person: السري بن يحيى) | No |

3/6 are pure name-format disagreements where both models identify the same person with different nasab chains. The name similarity function correctly flags these as below 0.90 threshold, but the underlying identifications match.

---

## 7. Ground Truth Comparison Incomplete

GROUND_TRUTH.json has 14 entries. Only 5 produced ground_truth_comparison.json in Phase C:
- أحكام الاضطباع والرمل في الطواف → all_match: true
- أساليب بلاغية → mismatch: level only (intermediate→beginner)
- أسلوب خطبة الجمعة → mismatch: level only (intermediate→null)
- البدر التمام → mismatch: level only (intermediate→beginner)
- مذكرات مالك بن نبي → all_match: true

3 fixtures are absent from Phase C entirely (04_hadith, 13_format_b, alfiyyah_versified — likely different directory names in the collection). The remaining 6 present fixtures failed title matching.

PHASE_C_SUMMARY.json reports `total_compared: 0` — this counter is broken.

All 3 mismatches are exclusively the `level` field (intermediate→beginner), confirming LESSONS.md's finding of systematic level underestimation.

---

## 8. Evaluation Protocol Adjustments for Phase 2

Based on calibration findings, Phase 2 evaluators should:

1. **Read this errata FIRST**, before reading the framework
2. **Read extraction.json and prompt_sent.json BEFORE** evaluating LLM output (protocol order matters for assessing extraction quality vs inference quality)
3. **Check `llm_responses/` directory** to identify model pair per-book
4. **Read author confidence from llm_responses/ only** — never from result.json
5. **Skip level field evaluation** — known systematic issue, not informative per-book
6. **For science scope**: FLAG only when primary science is wrong; broad supersets → PLAUSIBLE
7. **For the 6 disagreement books**: examine both models and note whether disagreement is substantive or name-format
8. **For VERIFIED**: require 2+ genuinely independent non-Shamela-ecosystem sources. Shamela + ketabonline + turath.io + waqfeya all draw from the same database → count as 1 source. Independent means: Wikipedia Arabic, academic catalogs, university syllabi, or publisher sites.

---

## 9. Corrected Calibration Verdicts

### Book 1: أحكام الاضطباع والرمل في الطواف
```
Status: success
Verdict: PLAUSIBLE (downgraded from VERIFIED — only 1 independent source for obscure modern author)
Author: PLAUSIBLE — Pipeline: عبد الله بن إبراهيم الزاحم / Death: null
  Sources: efatwa.ir (independent), shamela.ws/book/12134 (origin DB, weak)
  Note: Modern academic, no death date, low author conf (Opus: 0.72)
Genre: VERIFIED — risalah (fiqh treatise, confirmed by title analysis + content)
Multi-Layer: VERIFIED — false
Science: VERIFIED — ["fiqh"]
Trust: VERIFIED — flagged (appropriate for modern academic)
Consensus: agreed=true, models=[command_a, opus_4_6]
Ground truth: all_match=true (fixture 03_fiqh)
```

### Book 2: الأربعون النووية
```
Status: gate_abort (author-science mismatch — registry has "primary", no overlap with {"hadith","ulum_al_hadith"})
Verdict: VERIFIED
Author: VERIFIED — Pipeline (Opus): أبو زكريا محيي الدين يحيى بن شرف النووي (ت 676هـ)
  LLM confidence: 0.99 (Opus). Both models agree.
  Sources: ar.wikipedia.org (النووي), noor-book.com, shamela.ws/book/12836
Genre: VERIFIED — hadith_collection (both models agree; "matn" also acceptable per framework)
Multi-Layer: VERIFIED — false
Science: PLAUSIBLE — Opus: ["hadith","ulum_al_hadith","fiqh","aqidah","tasawwuf"]; CA: ["hadith","ulum_al_hadith"]
  Primary science (hadith) correct. Opus superset reasonable but broad.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
```

### Book 3: مجموع الفتاوى
```
Status: gate_abort (author-science mismatch — registry has "primary", no overlap with broad science list)
Verdict: VERIFIED
Author: VERIFIED — Pipeline (Opus): أحمد بن عبد الحليم بن عبد السلام ابن تيمية الحراني (ت 728هـ)
  LLM confidence: 0.99 (Opus). Both models agree.
  CRITICAL CHECK PASSED: Pipeline identified ابن تيمية (author), NOT ابن القاسم (compiler).
  Note: Extraction pre-labeled author vs compiler fields in the prompt — the LLM correctly used them.
  Sources: ketabonline.com/ar/books/5564, ar.wikipedia.org (مجموع_الفتاوى), goodreads.com, archive.org
Genre: VERIFIED — fatawa (confirmed by all 4 sources)
Multi-Layer: VERIFIED — false (fatwa collection, not commentary)
Science: PLAUSIBLE — ["aqidah","fiqh","usul_al_fiqh","tafsir","hadith","tasawwuf"]
  Broad superset reflects the encyclopedic 37-volume scope. Primary sciences (fiqh, aqidah) correct.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
```
