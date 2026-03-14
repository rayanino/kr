# NEXT — Phase C Evaluation: Session 6 (Edition Groups)

## Status
- Session 0 (Calibration): ✅ COMPLETE — 3 books
- Session 1 (Fixture Regression): ✅ COMPLETE — 11 books
- Session 2 (Famous Works A): ✅ COMPLETE — 8 books, 8 VERIFIED (1 with ML field-level flag)
- Session 3 (Famous Works B): ✅ COMPLETE — 7 books, 7 VERIFIED (1 with ML field-level flag)
- Session 4 (Multi-Layer + Commentary): ✅ COMPLETE — 10 books, 9 VERIFIED + 1 PLAUSIBLE
- Session 5 (Attribution + Trust + Obscure): ✅ COMPLETE — 10 books, 4 VERIFIED + 6 PLAUSIBLE
  - Report: PHASE_C_SESSION5_REPORT.md (commit 416daeb, 4 review rounds)
  - Running totals: 38 VERIFIED, 11 PLAUSIBLE, 0 FLAG, 0 ESCALATE (49 books)
- Sessions 6–7: PENDING

## Session 6 overview — Edition Groups (15 books)

This session evaluates **15 new books** (not individually evaluated in prior sessions) plus performs **cross-edition consistency checks** against 2 previously-evaluated books (حاشية ابن عابدين from Session 2, شرح العقيدة الطحاوية - ط الرسالة from Session 4).

The framework (§Session 6) says the focus is **consistency across editions.** Each edition group must agree on author, death date, genre, ML, science, and attribution. Disagreements within an edition group are the most important finding — they reveal either an extraction problem or an LLM inconsistency. Genre differences between editions of the same text (as found for الإبانة in Session 5) should be documented but are not necessarily errors.

**This session is LARGE.** 15 books is 50% more than any prior session. Budget time accordingly.

## Session 6 books (15)

All 15 are new evaluations. 14 use **opus + command_a**. 1 uses **opus + gpt_5_4** (تفسير الطبري ط التربية).

| # | Book (exact directory name) | Status | Models | ML (agree?) | Genre (Opus) | Key risk |
|---|---------------------------|--------|--------|-------------|--------------|----------|
| 1 | أعلام الموقعين عن رب العالمين - ط عطاءات العلم | gate_abort | opus + command_a | false (agree) | matn | **consensus=False; genre: Opus=matn, CA=usul_al_fiqh** |
| 2 | إعلام الموقعين عن رب العالمين - ت مشهور | gate_abort | opus + command_a | false (agree) | other | **consensus=False (name format); genre=other (both)** |
| 3 | إعلام الموقعين عن رب العالمين - ط العلمية | gate_abort | opus + command_a | false (agree) | other | consensus=True; genre disagree: Opus=other, CA=matn |
| 4 | البداية والنهاية - ت التركي | **success** | opus + command_a | false (agree) | tarikh | Low risk; trust=verified |
| 5 | البداية والنهاية - ط السعادة | **success** | opus + command_a | false (agree) | tarikh | Low risk; trust=verified |
| 6 | تفسير الطبري جامع البيان - ت التركي | gate_abort | opus + command_a | false (agree) | tafsir | Low risk |
| 7 | تفسير الطبري جامع البيان - ط دار التربية والتراث | gate_abort | **opus + gpt_5_4** | **false/true DISAGREE** | tafsir | **GPT-5.4 book; ML disagree (GPT=true with tahqiq_note)** |
| 8 | تحفة المودود بأحكام المولود - ت الأرنؤوط | gate_abort | opus + command_a | false (agree) | risalah | Low risk |
| 9 | تحفة المودود بأحكام المولود - ط عطاءات العلم | gate_abort | opus + command_a | false (agree) | risalah | **consensus=False (name format)** |
| 10 | فتاوى اللجنة الدائمة - المجموعة الأولى | **success** | opus + command_a | false (agree) | fatawa | **Institutional author, no death date; trust=flagged** |
| 11 | فتاوى اللجنة الدائمة - المجموعة الثانية | gate_abort | opus + command_a | false (agree) | fatawa | Institutional author, no death date |
| 12 | ألفية ابن مالك - ت القاسم | **success** | opus + command_a | false (agree) | nazm | **First nazm (versification) in corpus; trust=verified** |
| 13 | ألفية ابن مالك - ط التعاون | gate_abort | opus + command_a | false (agree) | nazm | First nazm in corpus |
| 14 | شرح العقيدة الطحاوية - ط الأوقاف السعودية - بتعليقات أحمد شاكر | gate_abort | opus + command_a | **true (agree)** | sharh | Cross-check with Session 4 ط الرسالة |
| 15 | تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد المحتار - ط الفكر | gate_abort | opus + command_a | true (agree) | hashiyah | **consensus=False; death: Opus=1306, CA=null; VERIFY author ≠ father** |

4 SUCCESS books (البداية ×2, فتاوى المجموعة الأولى, ألفية ت القاسم): check result.json for trust_tier, model source, confidence_scores.
11 GATE_ABORT books: get all classification data from llm_responses/, not result.json.
1 GPT-5.4 book (تفسير الطبري ط التربية): use gpt_5_4.json as second model.
1 ML=true disagreement (تفسير الطبري ط التربية): Opus=false, GPT=true (tahqiq_note bias).
4 consensus=False books: أعلام ط عطاءات, إعلام ت مشهور, تحفة ط عطاءات, تكملة حاشية.

## Pre-identified risks for Session 6

### CRITICAL PRIORITY

1. **إعلام/أعلام الموقعين (3 editions): Genre inconsistency across editions.**
   All 3 editions are by ابن القيم (ت 751), ML=false (all agree — framework critical check PASSED). But genre varies wildly:
   - ط عطاءات: Opus=matn (0.85), CA=usul_al_fiqh (0.95) — consensus=False (genre disagree)
   - ت مشهور: Opus=other (0.75), CA=other (0.85) — consensus=False (name format)
   - ط العلمية: Opus=other (0.75), CA=matn (0.95) — consensus=True
   
   The framework expects "risalah/other" which is closest to "other." Opus labels range from matn to other. CA labels range from usul_al_fiqh to other to matn. This is the worst cross-edition genre consistency in the corpus.
   
   NOTE: The أعلام spelling (ط عطاءات) vs إعلام (ت مشهور, ط العلمية) is a known orthographic variant of the same title. The evaluator should note this but NOT flag it as an error.
   
   NOTE: ط عطاءات has author_death_hijri=None in extraction BUT author_name_raw contains "(691 - 751)" — the date IS embedded in the raw text. This is NOT a genuine inference; it's a false positive on the strategic analysis inference list (extraction regex missed the "691 - 751" format without "ت"). The other 2 editions have death=751 as pass-through.
   
   From Errata §6: ط عطاءات is one of the 6 disagreed books: "Genre (matn vs usul_al_fiqh) + name format + attribution." ت مشهور is another: "Name format only (same person: ابن القيم)."

2. **تفسير الطبري ط التربية: GPT-5.4 + ML disagreement.**
   This is one of the 6 GPT-5.4 books in the entire corpus (Errata §1). GPT says ML=true with layers [matn: الطبري + tahqiq_note: محمود شاكر]. Opus says ML=false. This is the SAME tahqiq-as-layer bias documented in Errata §9 — but from GPT-5.4 instead of Opus. The correct answer is ML=false (tahqiq is editorial apparatus). Cross-check with the ت التركي edition (both say ML=false there).

3. **تكملة حاشية ابن عابدين: Author must be SON, not father.**
   Framework critical check: "تكملة حاشية ابن عابدين: علاء الدين عابدين (SON), ~1306, hashiyah, T, fiqh, ≠ father."
   - Opus identifies: محمد علاء الدين بن محمد أمين عابدين (death=1306, conf=0.92) — this is the SON ✓
   - CA identifies: محمد علاء الدين أفندي (death=null, conf=0.85) — name vaguer but still the son
   - Cross-check with Session 2: حاشية ابن عابدين author = محمد أمين بن عمر عابدين (death=1252) — the FATHER
   - Pipeline MUST distinguish father from son. Both models correctly identify the son as author.
   - Consensus=False: death date disagreement (1306 vs null). From Errata §6, this is listed as "Name format + death date (1306 vs null)" disagreement.
   - Death date 1306 is a **GENUINE INFERENCE** — extraction has author_death_hijri=None AND author_name_raw=None (both fields completely absent). Opus inferred 1306; CA could not. This is the last test case from the strategic analysis. Verify 1306 independently.

### HIGH PRIORITY

4. **شرح العقيدة الطحاوية: Cross-edition consistency with Session 4.**
   Session 4 evaluated ط الرسالة: author=ابن أبي العز (ت 792), genre=sharh, ML=true, science=['aqidah'], attribution: Opus=traditional, CA=definitive.
   Session 6 evaluates ط الأوقاف: author=ابن أبي العز (ت 792), genre=sharh, ML=true, attribution: Opus=traditional, CA=definitive.
   Expected: FULL agreement across editions. Verify layer chains match (matn=العقيدة الطحاوية by الطحاوي, sharh by ابن أبي العز).
   Session 4 also found this book had the tahqiq_note pattern (التركي + الأرنؤوط as muhaqiqs). Check if ط الأوقاف also shows this pattern (أحمد شاكر is the muhaqiq for this edition).

5. **فتاوى اللجنة الدائمة (2 editions): Institutional author handling.**
   Both editions identify "اللجنة الدائمة للبحوث العلمية والإفتاء" — an institutional body, not a person. No death date (correct for an institution). Genre: fatawa (both agree). Science: Opus=['aqidah', 'fiqh'], CA=['aqidah', 'fiqh'] (both agree). This tests the pipeline's handling of non-person authors.
   المجموعة الأولى is success (trust=flagged), المجموعة الثانية is gate_abort.

6. **ألفية ابن مالك (2 editions): First versification (nazm) in the corpus.**
   Both editions have genre=nazm — the first occurrence of this genre label in 49+ books evaluated. Verify: ألفية ابن مالك IS a versification (1000-line poem summarizing Arabic grammar). Genre=nazm is precisely correct. Author: ابن مالك (ت 672). Cross-edition consistency expected to be clean.

### MEDIUM PRIORITY

7. **البداية والنهاية (2 editions): Framework critical check.**
   Framework says: "البداية والنهاية (2 eds): ابن كثير, 774, tarikh NOT tafsir, F, tarikh, Critical."
   Pre-scan: both editions have genre=tarikh ✓ (not tafsir). Both success, both trust=verified. Straightforward.

8. **تحفة المودود (2 editions): Cross-edition consistency.**
   Both: ابن القيم 751, risalah, ML=false. ط عطاءات has consensus=False (name format only — same person). Clean otherwise.

## Key Session 5 findings (carry forward)

1. **Zero author errors across 49 books.** Running total: 0 in 49 books evaluated. The pipeline's author identification is the strongest field.

2. **Opus attribution taxonomy confirmed:**
   - "definitive": famous well-established works (both models agree)
   - "traditional": conventionally-attributed works (Opus; CA often overrides to definitive)
   - "disputed": genuinely contested works (only 3 books so far: الفقه الأكبر, الإبانة ×2)
   Session 6 has no genuinely disputed attributions. The standard Opus=traditional vs CA=definitive pattern applies to several books (شرح العقيدة, تكملة حاشية).

3. **Cross-edition genre inconsistency confirmed (الإبانة):** Same text classified as risalah in one edition and matn in another. Session 6 has the إعلام الموقعين group with WORSE inconsistency (3 editions, at least 4 different genre labels across both models).

4. **Death date genuine inference running total:** 2 correct (728, 324), 1 wrong (1432 vs 1439), 4 false positives. Session 6 has 1 genuine inference: تكملة حاشية (1306 — both extraction fields null, Opus inferred). Also: أعلام الموقعين ط عطاءات has death embedded in raw text as "(691 - 751)" but extraction field is null — this is a false positive (extraction regex missed non-standard format), NOT a genuine inference.

5. **Tahqiq-as-layer bias:** Errata §9 documented 3 Opus instances. Session 6 has the FIRST GPT-5.4 instance: تفسير الطبري ط التربية (GPT says ML=true with tahqiq_note layer). The correct answer is ML=false.

6. **Authority_level disagreements:** Session 5 had 0/10 (no sharh works). Session 6 has 2 ML=true sharh/hashiyah books (شرح العقيدة, تكملة حاشية) — the Opus=reference vs CA=primary pattern from Session 4 may reappear.

7. **Result.json model source for success books:** Check which model's values appear in result.json for the 4 success books (البداية ×2, فتاوى المجموعة الأولى, ألفية ت القاسم).

8. **Opus genre=hashiyah contradiction (Session 4 finding):** When Opus labels genre=hashiyah, verify the layer structure has 3 distinct layers. If only 2, it's an internal contradiction. Relevant for تكملة حاشية (which IS genuinely a hashiyah/takmliah — verify layer chain).

## Cross-edition comparison protocol

For each edition group, after writing individual verdicts:

1. **Create a comparison table** with these fields: Author name, Death date, Genre (Opus), Genre (CA), ML, Science, Attribution (Opus), Attribution (CA), Authority_level (Opus/CA).
2. **Mark ✓ or ✗** for each field across editions.
3. **For ✗ fields:** determine if the disagreement is: (a) extraction difference (different input → different output, expected), (b) model inconsistency (same input → different output, concerning), or (c) genuine bibliographic difference (different editions of the same text may legitimately differ).
4. **Compare with prior sessions** where applicable: شرح العقيدة with Session 4, تكملة حاشية with Session 2's حاشية.

## Methodology fixes (ALL still apply)

1. Search BEFORE writing verdict
2. Use web_fetch on at least 1 URL per book (Sessions 4-5 achieved low compliance — aim for 50%+)
3. Shamela category cross-check in every verdict
4. Death date pass-through vs inference — check author_name_raw text, not just author_death_hijri field
5. Result.json model source for the 4 success books
6. Session-end consistency check as SEPARATE pass
7. Confidence calibration section required
8. For consensus=False books (4 in this session): examine both models and note whether disagreement is substantive or name-format
9. For ML=true books (2 in this session): verify layer chains against external sources. Check for tahqiq-as-layer bias.
10. For the GPT-5.4 book (تفسير الطبري ط التربية): use gpt_5_4.json as second model, not command_a.json

## Before starting Session 6, read these in order:
1. PHASE_C_ERRATA.md (corrections override framework — DEEP READ, especially §6 on the 4 disagreed books in this session and §9 on tahqiq-as-layer)
2. PHASE_C_EVALUATION_FRAMEWORK.md (SKIM — verdict scale, expected values table for Session 6 books, edition group cross-checks §Session 6)
3. PHASE_C_SESSION5_REPORT.md (READ findings + cross-book patterns, SKIM per-book details)
4. PHASE_C_SESSION4_REPORT.md (READ شرح العقيدة الطحاوية verdict for cross-edition check)
5. PHASE_C_SESSION2_REPORT.md (READ حاشية ابن عابدين verdict for تكملة cross-check)
6. PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md (READ death date inference list — 1 genuine inference pending + 1 false positive to confirm)
7. **EVALUATION_QUICK_REFERENCE.md** — re-read this before EACH book

## After completing all verdicts:
Paste the contents of SELF_REVIEW_PROMPT.md five times total:
- Pastes 1-4: Review the report (Rounds 1-4, auto-detected). Each round attacks from a different angle.
- After Round 4: Write the handoff (NEXT.md) for Session 7, including pre-scanned pipeline data for all Session 7 books.
- Paste 5: Review the handoff (Round 5, auto-detected). Verifies every claim in NEXT.md against pipeline data.
Do not skip rounds.

## Key corrections from calibration (still apply):
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- 14/15 Session 6 books use `command_a.json` as second model; 1 uses `gpt_5_4.json` (تفسير الطبري ط التربية)
- 0/73 single-model fallback
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/
- Framework Section 7 (single-model) does not apply
- Consensus does NOT check multi-layer (Correction 7) — relevant for تفسير الطبري ط التربية (ML disagrees but consensus=True)
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) count as ONE source for VERIFIED threshold

## SESSION 6 SPECIFIC: Edition group evaluation order

Evaluate in this order (grouped by edition, cross-compare after each group):

**Group 1: إعلام الموقعين (3 editions) — HARDEST, do first while context is fresh**
Books 1-3. Evaluate individually, then cross-compare. 2/3 have consensus=False. Genre is the main concern.

**Group 2: تكملة حاشية + cross-check with حاشية (Session 2)**
Book 15. Evaluate, then cross-check author identity (son ≠ father) against Session 2 data.

**Group 3: تفسير الطبري (2 editions)**
Books 6-7. Book 7 is GPT-5.4 with ML disagreement — the key finding.

**Group 4: شرح العقيدة الطحاوية + cross-check with Session 4**
Book 14. Evaluate, then cross-check against Session 4 ط الرسالة.

**Group 5: البداية والنهاية (2 editions) — straightforward**
Books 4-5. Both success. Quick evaluation + cross-compare.

**Group 6: تحفة المودود (2 editions)**
Books 8-9. Both gate_abort, both risalah. Quick evaluation.

**Group 7: فتاوى اللجنة الدائمة (2 editions)**
Books 10-11. Institutional author. Quick evaluation.

**Group 8: ألفية ابن مالك (2 editions)**
Books 12-13. First nazm in corpus. Quick evaluation.

Mid-session quality gate after Group 4 (after ~8 books).
