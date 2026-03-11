# NEXT — Phase C Evaluation: Session 5 (Attribution + Trust + Obscure)

## Status
- Session 0 (Calibration): ✅ COMPLETE — 3 books
- Session 1 (Fixture Regression): ✅ COMPLETE — 11 books
- Session 2 (Famous Works A): ✅ COMPLETE — 8 books, 8 VERIFIED (1 with ML field-level flag)
- Session 3 (Famous Works B): ✅ COMPLETE — 7 books, 7 VERIFIED (1 with ML field-level flag)
- Session 4 (Multi-Layer + Commentary): ✅ COMPLETE — 10 books, 9 VERIFIED + 1 PLAUSIBLE
  - Report: PHASE_C_SESSION4_REPORT.md (commit 844044b, 4 review rounds)
  - Running totals: 34 VERIFIED, 5 PLAUSIBLE, 0 FLAG, 0 ESCALATE (39 books)
- Sessions 5–7: PENDING

## Session 5 books (10) — Attribution + Trust + Obscure

This is the **critical session.** It contains the only genuinely disputed-attribution books (الفقه الأكبر, الإبانة ×2), the lowest-confidence author in the corpus (الورقة النحوية, 0.55), the highest concentration of obscure works, and 5/10 books with at least one pre-identified concern. **Strategic analysis rates this session HIGH difficulty.**

All 10 books use **opus + command_a** (no GPT-5.4 books in this session).

| # | Book (exact directory name) | Status | ML (both agree) | Genre (Opus) | Key risk |
|---|---------------------------|--------|-----------------|--------------|----------|
| 1 | الفقه الأكبر | gate_abort | false (agree) | matn | **attrib: Opus=disputed, CA=traditional** |
| 2 | الإبانة عن أصول الديانة - ت العصيمي | gate_abort | false (agree) | risalah | **attrib: Opus=disputed, CA=definitive; death 324 GENUINE INFERENCE** |
| 3 | الإبانة عن أصول الديانة - ت فوقية | gate_abort | false (agree) | matn | **attrib: Opus=disputed, CA=definitive** |
| 4 | البيان والتبيين | **success** | false (agree) | adab | Low risk |
| 5 | الورقة النحوية | **success** | false (agree) | matn | **Lowest author conf in corpus: 0.55 (Opus), 0.70 (CA)** |
| 6 | حديث الضب الذي تكلم بين يدي النبي للطبراني | gate_abort | false (agree) | hadith_collection | 1 page, content_minimal |
| 7 | نصيحة لطالب الحق - ضمن «آثار المعلمي» | gate_abort | false (agree) | risalah | 2 pages, content_minimal, modern author |
| 8 | أدب النفوس للآجري | gate_abort | false (agree) | risalah | **Truncated: 24 of 271 pages exported** |
| 9 | أحاديث العطار عن شيوخه | gate_abort | false (agree) | hadith_collection | **Truncated + truncation flag; author=VERIFY** |
| 10 | الكلام على حديث الإستلقاء لأبي موسى المديني | **success** | false (agree) | risalah | 2 pages, obscure |

3 SUCCESS books (البيان والتبيين, الورقة النحوية, الكلام على حديث الإستلقاء): check result.json for trust_tier, model source, confidence_scores.
7 GATE_ABORT books: get all classification data from llm_responses/, not result.json.
0 ML=true books in this session. All 10 agree ML=false.
0 GPT-5.4 books (all use Command A).

## Pre-identified risks for Session 5

### CRITICAL PRIORITY

1. **الفقه الأكبر: Disputed attribution — the genuine hard case.**
   Extraction explicitly says "ينسب لأبي حنيفة النعمان" — "attributed to Abu Hanifa." The title_full even includes "المنسوبين لأبي حنيفة" (attributed to Abu Hanifa). Opus says attribution=disputed. CA says traditional. Genre disagreement: Opus=matn (0.90), CA=risalah (0.90). Both are acceptable per framework. Science: both agree aqidah. Death 150 is pass-through.
   **The core question is attribution.** Is this genuinely by أبو حنيفة? This is a famous scholarly debate — the text is widely attributed but contested. Opus's "disputed" may be more accurate than CA's "traditional." The evaluator MUST research the attribution debate independently and take a position.
   Framework expected: أبو حنيفة, 150, risalah/matn, F, aqidah, attrib=disputed.

2. **الإبانة عن أصول الديانة (2 editions): Text authenticity dispute.**
   Both editions are attributed to أبو الحسن الأشعري (ت 324). The الإبانة is one of the most debated texts in Islamic intellectual history — Ash'ari scholars question whether the surviving text reflects الأشعري's original, or was altered/interpolated by later Hanbali transmitters. Opus says attribution=disputed for both editions. CA says definitive for both.
   **Critical difference between editions:**
   - ت العصيمي: author_death_hijri=NULL in extraction. author_name_raw="أبو الحسن علي بن إسماعيل الأشعري" — NO embedded death date. Opus death=324 is a **GENUINE INFERENCE** (one of the last remaining real inference test cases from the strategic analysis). Verify 324 independently.
   - ت فوقية: author_death_hijri=324 in extraction. Full nasab in author_name_raw with "(ت 324هـ)". Death is pass-through.
   Genre disagreement between editions: ت العصيمي → Opus=risalah (0.82), CA=risalah (0.90). ت فوقية → Opus=matn (0.90), CA=matn (0.95). Different genre labels for the SAME text (different editions) — the evaluator should note this inconsistency but NOT necessarily flag it (the genre enum may not distinguish between short standalone aqidah texts).
   **Session 6 cross-check:** Both editions must agree on author name and death date. Genre inconsistency should be noted.
   Framework expected: الأشعري, 324, risalah, F, aqidah, attrib=disputed.

3. **الورقة النحوية: Lowest confidence in the entire corpus.**
   Author: حازم خنفر. No death date in extraction or LLM output. Author confidence: Opus 0.55, CA 0.70. Framework says author=VERIFY (not pre-populated). Genre disagreement: Opus=matn (0.90), CA=risalah (0.90). Only 2 pages of content. quality_issues: content_minimal.
   **This is the test case for low-confidence handling.** The pipeline classified it as success (not gate_abort) despite the lowest author confidence in the corpus. trust_tier=flagged (0.4325). The evaluator should search for حازم خنفر independently — this may be a modern author with very limited online presence.
   Framework expected: VERIFY, —, risalah/matn, F, nahw, low conf OK.

### HIGH PRIORITY

4. **أحاديث العطار عن شيوخه: Author=VERIFY + truncated export.**
   Framework says author=VERIFY. Opus identifies: محمد بن الحسن بن يعقوب بن مقسم العطار (ت 354). CA agrees. Author confidence: Opus 0.92, CA 0.90. But: extraction has 2 quality warnings — page_count_mismatch (10 of 279 pages) AND truncation_with_mismatch (last page ends without sentence-ending punctuation). This book may be too truncated for reliable genre classification.
   Framework expected: VERIFY, —, hadith_collection, F, hadith, trust=flagged.

5. **أدب النفوس للآجري: Truncated export.**
   Digital pages: 24 of 271 claimed physical pages (9%). quality_issues: page_count_mismatch warning. The full title from extraction is "مجموعة أجزاء حديثية - أدب النفوس" suggesting this may be part of a larger compilation. Attribution: Opus=traditional, CA=definitive. Science disagreement: Opus=['tasawwuf', 'aqidah'], CA=['tasawwuf', 'adab'].
   Framework expected: الآجري, 360, risalah/other, F, —, truncated.

### MEDIUM PRIORITY

6. **Attribution disagreements (6/10 books).**
   الفقه الأكبر (Opus=disputed, CA=traditional), الإبانة ×2 (Opus=disputed, CA=definitive), حديث الضب (Opus=traditional, CA=definitive), أدب النفوس (Opus=traditional, CA=definitive), الكلام على حديث (Opus=traditional, CA=definitive). Only الفقه الأكبر and الإبانة are genuinely disputed works; the other 3 disagreements follow the Opus=traditional vs CA=definitive pattern seen in Sessions 3-4.

7. **حديث الضب: 1-page hadith juz'.**
   Only 1 content page. الطبراني (ت 360) is well-known but this specific juz' (part) is obscure. Genre: hadith_collection (both agree). content_minimal quality flag.

8. **نصيحة لطالب الحق: Modern author, 2 pages.**
   المعلمي اليماني (1313-1386 هـ) — death date pass-through. Part of آثار المعلمي compilation. Both models agree on all fields. Only 2 pages of content. Framework expected: المعلمي, ~1386, risalah/other, F, —, trust=flagged.

### LOW PRIORITY

9. **البيان والتبيين: Famous adab work.**
   الجاحظ (ت 255) — one of the most famous classical Arabic prose writers. Success book: trust=verified (0.6925), genre=adab, ML=false. Both models agree on everything. Science: Opus=['adab', 'balagha', 'lughah'], CA=['adab', 'lughah']. Result.json carries CA values. Straightforward.

10. **الكلام على حديث الإستلقاء: Obscure but straightforward.**
    أبو موسى المديني (ت 581). Success book: trust=verified (0.6925), genre=risalah. Only 2 content pages. Attribution: Opus=traditional, CA=definitive. Both agree on author and all other fields.

## Key Session 4 findings (carry forward)

1. **Zero author errors across 39 books.** Running total: 0 in 39 books evaluated.

2. **Opus genre=hashiyah contradiction confirmed:** التعليق على الرحيق المختوم has Opus genre=hashiyah (0.82) but only 2 layers (matn + sharh). Hashiyah requires 3 layers. CA correctly says sharh. Result.json carries correct value. This is the first genre-level high-conf + wrong case (cumulative: 2 ML wrong at 0.85-0.90, 1 genre wrong at 0.82).

3. **Tahqiq_note mechanism still unknown.** Session 4 data: 3/4 books with muhaqiq got tahqiq_note; 1/4 (اللامع العزيزي) did not. Combined with الأذكار (Session 3), muhaqiq is necessary but NOT sufficient. Not relevant to Session 5 (no ML=true books).

4. **Authority_level: systematic Opus=reference vs CA=primary on sharh works.** 6/10 Session 4 books had this disagreement. Not checked by consensus. Document but do not flag.

5. **Attribution: Opus says "traditional" for obscure conventionally-attributed works, "definitive" for famous well-established works, "disputed" for genuinely contested works.** CA tends toward "definitive" even for traditionally-attributed works. Only flag when Opus says "disputed" — those require independent investigation.

6. **Death date genuine inference running total:** 1 confirmed correct (مجموع الفتاوى 728), 1 confirmed wrong (أساليب بلاغية 1432 vs 1439), 4 confirmed false positives (dates embedded in author_name_raw). Session 5 has 1 genuine inference: الإبانة ت العصيمي (324). The others on the strategic analysis list are in Sessions 6-7.

## Methodology fixes (ALL still apply)

1. Search BEFORE writing verdict
2. Use web_fetch on at least 1 URL per book (Session 4 achieved 0/10 — aim higher)
3. Shamela category cross-check in every verdict
4. Death date pass-through vs inference — check author_name_raw text, not just author_death_hijri field
5. Result.json model source for the 3 success books (البيان والتبيين, الورقة النحوية, الكلام على حديث)
6. Session-end consistency check as SEPARATE pass
7. Confidence calibration section required
8. **NEW for Session 5:** For disputed-attribution books (الفقه الأكبر, الإبانة ×2), the evaluator MUST independently research the attribution debate and take a position. Do not simply accept either model's label without investigation.
9. **NEW for Session 5:** For VERIFY-author books (الورقة النحوية, أحاديث العطار), search for the specific author name independently. Do not assume the pipeline is correct just because both models agree — both may be wrong on an obscure author.

## Before starting Session 5, read these in order:
1. PHASE_C_ERRATA.md (corrections override framework — DEEP READ)
2. PHASE_C_EVALUATION_FRAMEWORK.md (SKIM for context — verdict scale, expected values table for Session 5 books)
3. PHASE_C_SESSION4_REPORT.md (READ findings + cross-book patterns, SKIM per-book details)
4. PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md (Session 5 risk: HIGH — disputed attributions)
5. **EVALUATION_QUICK_REFERENCE.md** — re-read this before EACH book

## After completing all verdicts:
Paste the contents of SELF_REVIEW_PROMPT.md five times total:
- Pastes 1-4: Review the report (Rounds 1-4, auto-detected). Each round attacks from a different angle.
- After Round 4: Write the handoff (NEXT.md) for Session 6, including pre-scanned pipeline data for all Session 6 books.
- Paste 5: Review the handoff (Round 5, auto-detected). Verifies every claim in NEXT.md against pipeline data.
Do not skip rounds.

## Key corrections from calibration (still apply):
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- All 10 Session 5 books use `command_a.json` as second model
- 0/73 single-model fallback
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/
- Framework Section 7 (single-model) does not apply
- Consensus does NOT check multi-layer (Correction 7) — though in Session 5 all 10 books have ML=false (no ML disagreements possible)
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) count as ONE source for VERIFIED threshold

## SESSION 5 SPECIFIC: Attribution investigation protocol
For the 3 disputed-attribution books (الفقه الأكبر, الإبانة ×2):
1. Search for the specific attribution debate (not just the book title)
2. Identify the scholarly positions: who accepts the attribution? who disputes it? what are the arguments?
3. Compare Opus (disputed) vs CA (traditional/definitive) — which better reflects the scholarly consensus?
4. If the attribution IS genuinely disputed, the correct pipeline value is "disputed" — not "definitive" or "traditional"
5. The verdict should reflect honest uncertainty: if scholars disagree, PLAUSIBLE or UNVERIFIABLE may be more appropriate than VERIFIED for the attribution field
6. For the 2 الإبانة editions: cross-check that author, death date, and attribution are consistent across both editions. Genre may differ (risalah vs matn) — note but do not necessarily flag.

## SESSION 5 SPECIFIC: Low-confidence author handling
For الورقة النحوية (0.55 Opus, 0.70 CA):
1. Search for the author name حازم خنفر independently
2. If the author cannot be found online: UNVERIFIABLE is the correct verdict (not PLAUSIBLE or FLAG)
3. The pipeline classified it as success despite low confidence — this means trust_tier and result.json values exist. Check them.
4. Do NOT assume that "both models agree" means correct — both may be drawing from the same training data gap
