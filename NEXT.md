# NEXT — Phase C Evaluation: Session 7 (Remaining — All Unevaluated Books)

## Status
- Session 0 (Calibration): ✅ COMPLETE — 3 books
- Session 1 (Fixture Regression): ✅ COMPLETE — 11 books
- Session 2 (Famous Works A): ✅ COMPLETE — 8 books, 8 VERIFIED (1 with ML field-level flag)
- Session 3 (Famous Works B): ✅ COMPLETE — 7 books, 7 VERIFIED (1 with ML field-level flag)
- Session 4 (Multi-Layer + Commentary): ✅ COMPLETE — 10 books, 9 VERIFIED + 1 PLAUSIBLE
- Session 5 (Attribution + Trust + Obscure): ✅ COMPLETE — 10 books, 4 VERIFIED + 6 PLAUSIBLE
  - Report: PHASE_C_SESSION5_REPORT.md (commit 416daeb, 4 review rounds)
- Session 6 (Edition Groups): ✅ COMPLETE — 17 books, 17 VERIFIED
  - Report: PHASE_C_SESSION6_REPORT.md (commit 7cc38e5, 4 review rounds)
  - Running totals: 55 VERIFIED, 11 PLAUSIBLE, 0 FLAG, 0 ESCALATE (66 books)
- Session 7 (Remaining): **PENDING** ← YOU ARE HERE
- Aggregation: PENDING

## Session 7 — All Remaining Books (23 books)

The framework planned Session 7 as "Riwayah + Remaining (10 books)." The actual count is **23 books** — all books in Phase C that have not been evaluated in Sessions 0-6. This is the largest session by book count. It includes edition variants, riwayah books, famous classics, and a handful of high-risk books requiring deep investigation.

**Strategy:** Group the 23 books into 4 categories. Evaluate Groups A and B quickly (cross-edition checks reuse prior session verdicts). Concentrate effort on Groups C and D.

### Group A: Edition Variants of Already-Evaluated Works (7 books)
These are different editions of works already evaluated in prior sessions. For each, run the Edition Group Protocol: author, genre, ML, and science MUST match the prior edition. Muhaqiq and trust MAY differ.

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Prior session evaluation | Key check |
|---|---------------------------|--------|--------|--------------|-----|------------------------|-----------|
| 1 | الرحيق المختوم | gate_abort | opus + command_a | sirah | F | Session 3: الرحيق المختوم - ط العلمية (VERIFIED) | Cross-edition match |
| 2 | الرسالة للشافعي | gate_abort | opus + command_a | risalah | **T** | Session 2: ت شاكر (VERIFIED, ML flag); Session 3: ت كيلاني (VERIFIED) | **ML=true (Opus) — tahqiq_note pattern instance** |
| 3 | مختصر صحيح مسلم للمنذري ت الألباني | gate_abort | opus + command_a | mukhtasar | **T** | Session 2: مختصر صحيح مسلم (VERIFIED, ML flag) | **ML=true (Opus) — tahqiq_note pattern instance** |
| 4 | مسند أحمد - ت شاكر - ط دار الحديث | gate_abort | opus + command_a | hadith_collection | **T** | Session 2: مسند أحمد - ط الرسالة (VERIFIED, ML flag) | **ML=true (Opus) — tahqiq_note pattern instance** |
| 5 | فتح الباري بشرح البخاري - ط السلفية | gate_abort | opus + command_a | sharh | T | Session 2: فتح الباري بشرح صحيح البخاري (VERIFIED) | ML=true (genuine sharh) |
| 6 | مذكرات مالك بن نبي - العفن | success | opus + command_a | other | F | Session 1: مذكرات مالك بن نبي (VERIFIED) | trust=flagged (0.6075) |
| 7 | من أحاديث سفيان الثوري - رواية السري بن يحيى - جوامع الكلم | success | opus + command_a | hadith_collection | F | Session 1: من أحاديث سفيان الثوري (VERIFIED) | **Consensus DISAGREED** (name format only — not substantive per Errata §6); trust=verified (0.6925); riwayah variant |

### Group B: Riwayah Books (3 books)
These are hadith collections identified by their narration chains. All 3 use Opus + Command A.

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Key risk |
|---|---------------------------|--------|--------|--------------|-----|----------|
| 8 | حديث يحيى بن معين رواية أبي منصور الشيباني | gate_abort | opus + command_a | hadith_collection | F | Riwayah field present in extraction; author=ابن معين (ت 233); 43 pages |
| 9 | تاريخ ابن معين - رواية الدارمي | gate_abort | opus + command_a | tabaqat | F | Same author as #8 (ابن معين ت 233) but genre=tabaqat — correct, this IS a different work (biographical, not hadith) |
| 10 | مسند أبي حنيفة رواية الحصكفي | gate_abort | opus + command_a | hadith_collection | F | author=أبو حنيفة (ت 150), conf=0.92 |

### Group C: Framework-Listed Session 7 Books (5 books)
These are specifically listed in the framework's Session 7 plan. Several have VERIFY flags.

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Key risk |
|---|---------------------------|--------|--------|--------------|-----|----------|
| 11 | الأحاديث الأربعين النووية مع ما زاد عليها ابن رجب وعليها الشرح الموجز المفيد | success | opus + command_a | sharh | T | **Framework: VERIFY.** trust=flagged (0.4325). Author conf=0.82. death=None. Result.json genre=sharh, ML=true. Session 0 evaluated الأربعون النووية (the base matn) — cross-check matn author |
| 12 | الإبدال في لغات الأزد دراسة صوتية في ضوء علم اللغة الحديث | success | opus + command_a | risalah | F | **Framework: VERIFY.** trust=flagged (0.455). **Page mismatch: 73 digital of 494 physical (15%).** Modern academic work. Author conf=0.92 |
| 13 | المستدرك على مجموع الفتاوى | gate_abort | opus + **gpt_5_4** | fatawa | F | **Framework: VERIFY.** GPT-5.4 as second model. Cross-check: Session 0 evaluated مجموع الفتاوى (ابن تيمية ت 728) — المستدرك is a DIFFERENT work (missed fatwas) by a DIFFERENT compiler. death=728 (both models) |
| 14 | النكت على شرح النووي على صحيح مسلم | gate_abort | opus + command_a | other | F | **Framework: VERIFY.** Author=هاني فقيه (modern), conf=**0.75** (lowest in session). death=None (both models). **Genre disagreement: Opus=other, CA=hashiyah.** Gate error: "is_multi_layer=true but text_layers is empty" |
| 15 | معالم بيانية في آيات قرآنية | success | opus + command_a | tafsir | F | **Framework: VERIFY.** trust=flagged (0.4325). **Only 2 content pages (content_minimal).** Author=المغامسي (modern). NOTE: This is a DIFFERENT BOOK from Session 3's "معالم بيانية في أحاديث نبوية" — same author, different content |

### Group D: Additional Remaining Books (8 books)
These are new works not in the original Session 7 plan but remaining in the corpus.

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Key risk |
|---|---------------------------|--------|--------|--------------|-----|----------|
| 16 | أبنية الأسماء والأفعال والمصادر | gate_abort | opus + **gpt_5_4** | matn | F | **Consensus DISAGREED** (genre: matn vs other + name format + attribution — SUBSTANTIVE per Errata §6). GPT-5.4 as second model. Author=ابن القطاع الصقلي (ت 515) |
| 17 | الموسوعة الفقهية الكويتية | success | opus + command_a | mawsuah | F | Institutional author (وزارة الأوقاف الكويتية). trust=flagged (0.4625). death=None. Genre=mawsuah — verify encyclopedic scope |
| 18 | بداية المجتهد ونهاية المقتصد | gate_abort | opus + command_a | fiqh_comparative | F | ابن رشد (ت 595). Genre=fiqh_comparative — non-standard enum value, verify classification |
| 19 | زاد المستقنع في اختصار المقنع - ت العسكر | gate_abort | opus + command_a | mukhtasar | F | الحجاوي (ت 968). Genre=mukhtasar — verify genre_chain names source work (المقنع by ابن قدامة) |
| 20 | سير أعلام النبلاء - ط الحديث | success | opus + command_a | tabaqat | F | الذهبي (ت 748). trust=verified (0.7175). Science=['tarikh', 'sirah'] — 'sirah' is imprecise for a biographical dictionary (not prophetic biography) |
| 21 | شرح النووي على مسلم | gate_abort | opus + command_a | sharh | T | النووي (ت 676). Famous sharh. Cross-check: Session 0 evaluated الأربعون النووية (same author) |
| 22 | لسان العرب | success | opus + command_a | mujam | F | ابن منظور (ت 711). trust=verified (0.655). Genre=mujam — verify lexicographic organization |
| 23 | همع الهوامع في شرح جمع الجوامع | gate_abort | opus + command_a | sharh | T | السيوطي (ت 911). Sharh on nahw matn. Layer chain verification needed |

**Totals:** 9 SUCCESS books, 14 GATE_ABORT books. 2 GPT-5.4 books (#13, #16). 2 consensus-DISAGREED (#7, #16). 5 framework-VERIFY books (#11-15).

## Pre-identified risks

### CRITICAL PRIORITY

1. **النكت على شرح النووي (#14): Lowest confidence in session, genre disagreement, special gate error.**
   Author=هاني فقيه (modern), conf=0.75 (Opus), death=None. Genre: Opus=other, CA=hashiyah. The gate error is unusual: "is_multi_layer=true but text_layers is empty" — the pipeline detected an ML/layer inconsistency that neither model's output resolves cleanly. This is the most uncertain identification in the remaining corpus.

2. **أبنية الأسماء والأفعال والمصادر (#16): GPT-5.4, consensus DISAGREED (SUBSTANTIVE).**
   From Errata §6: genre (matn vs other) + name format + attribution disagreement. Author=ابن القطاع الصقلي (ت 515). Verify both author and genre independently.

3. **ML=true tahqiq_note pattern (Books #2, #3, #4): 3 additional instances.**
   الرسالة للشافعي, مختصر صحيح مسلم, and مسند أحمد all have Opus=ML=true, CA=ML=false. These are the SAME tahqiq_note pattern as Sessions 2-3. These are additional editions of the same works — confirm the pattern persists. Running total will reach 7 instances (Opus: 6, GPT-5.4: 1, Command A: 0/67).

### HIGH PRIORITY

4. **معالم بيانية في آيات قرآنية (#15): Only 2 content pages, content_minimal.**
   DIFFERENT BOOK from Session 3's "معالم بيانية في أحاديث نبوية." Same author (المغامسي), different content (آيات vs أحاديث). Genre: result.json=tafsir. With only 2 pages, all classification is based on minimal evidence.

5. **الأحاديث الأربعين مع ابن رجب (#11): Framework VERIFY, author conf=0.82, death=None.**
   Result.json: genre=sharh, ML=true. Cross-check: Session 0 evaluated الأربعون النووية (the base matn by النووي ت 676). Identify the actual sharh author from the title — "الشرح الموجز المفيد" — and verify the layer chain.

6. **المستدرك على مجموع الفتاوى (#13): GPT-5.4 as second model.**
   Cross-check with Session 0's مجموع الفتاوى. المستدرك is NOT the same work — verify: is the pipeline author ابن تيمية (original fatwa issuer) or the compiler (ابن القاسم)?

7. **Edition variants with ML discrepancies (#2, #3, #4):**
   These 3 books were already evaluated in Session 2 with ML field-level flags. The new editions should show the SAME pattern (Opus=true tahqiq_note, CA=false). Cross-edition match required.

### MEDIUM PRIORITY

8. **Genre precision checks for rare/non-standard genres:**
   - الموسوعة الفقهية (#17): mawsuah — verify encyclopedic scope
   - بداية المجتهد (#18): fiqh_comparative — non-standard enum value
   - زاد المستقنع (#19): mukhtasar — verify genre_chain names المقنع
   - لسان العرب (#22): mujam — verify lexicographic organization
   - سير أعلام النبلاء (#20): Science='sirah' is imprecise for a biographical dictionary

9. **Success books (9 total) — check trust_tier and result.json model source for each.**

10. **Cross-edition checks (Group A):** For each of the 7 edition variants, compare author, genre, ML, and science against the prior session's verdict on the original edition. Document consistency in structured tables.

## Key Session 6 findings (carry forward)

1. **Zero author errors across 66 books.** Running total: 0 in 66 books evaluated.

2. **Opus attribution taxonomy confirmed across Sessions 2-6:** "definitive" for famous well-established works; "traditional" for conventionally-attributed works; "disputed" for genuinely contested works. CA tends toward "definitive" even for traditionally-attributed works.

3. **Death date genuine inference running total:** 3 confirmed correct (مجموع الفتاوى 728, الإبانة ت العصيمي 324, تكملة حاشية 1306), 1 confirmed wrong (أساليب بلاغية 1432 vs actual 1439), 9 confirmed false positives. Session 7: check author_name_raw for embedded dates before classifying any inference as "genuine."

4. **Tahqiq_note ML=true pattern — cumulative 4 instances:**
   Opus: 3 instances (الرسالة, مختصر صحيح مسلم, مسند أحمد). GPT-5.4: 1 instance (تفسير الطبري ط التربية). Command A: 0 instances in 67 books. Session 7 has 3 edition variants (#2, #3, #4) that will likely add 3 more Opus instances.

5. **Authority_level disagreements:** Opus=reference vs CA=primary on sharh works persists (9/11 across Sessions 4-6). Session 7 has 4 sharh works (#5, #11, #21, #23) — check for this pattern.

6. **Cross-edition genre inconsistency:** إعلام الموقعين had matn/other/usul_al_fiqh (Session 6). الإبانة had risalah/matn (Session 5). Check Session 7 edition variants for similar drift.

7. **web_fetch compliance:** Sessions 4-6 had 0-1/N actual web_fetch. Session 7 should target at least 5/23 web_fetch calls on high-priority books.

## Methodology fixes (ALL still apply)

1. Search BEFORE writing verdict
2. Use web_fetch on at least 1 URL per high-priority book (target 5/23 minimum)
3. Shamela category cross-check in every verdict
4. Death date pass-through vs inference — check author_name_raw text, not just author_death_hijri field
5. Result.json model source for the 9 success books
6. Session-end consistency check as SEPARATE pass
7. Confidence calibration section required
8. **Session 7 specific:** For edition variants (Group A), run the Edition Group Protocol: compare with the prior session's verdict on the original edition
9. **Session 7 specific:** For the 2 GPT-5.4 books (#13, #16), check for model-specific biases
10. **Session 7 specific:** For the 5 framework-VERIFY books (#11-15), deeper investigation (2+ web searches, 1+ web_fetch)

## Before starting Session 7, read these in order:
1. PHASE_C_ERRATA.md (DEEP READ — especially §6 on consensus disagreements, §9 on tahqiq_note)
2. PHASE_C_EVALUATION_FRAMEWORK.md (SKIM — expected values table for Session 7 books, verdict scale)
3. PHASE_C_SESSION2_REPORT.md (READ فتح الباري, مختصر صحيح مسلم, مسند أحمد, الرسالة verdicts for cross-edition checks)
4. PHASE_C_SESSION3_REPORT.md (READ الرحيق المختوم verdict for cross-edition check)
5. PHASE_C_SESSION6_REPORT.md (READ findings + cross-book patterns)
6. **EVALUATION_QUICK_REFERENCE.md** — re-read before EACH book

## Key corrections from calibration (still apply):
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- Second model: 21/23 books use `command_a.json`; 2 books (#13 المستدرك, #16 أبنية) use `gpt_5_4.json`
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/
- Framework Section 7 (single-model) does not apply (0/73 single-model fallback)
- Consensus does NOT check multi-layer — ML must be compared manually between both models
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) count as ONE source for VERIFIED threshold
- For the 2 consensus-DISAGREED books (#7, #16): examine both models and note whether disagreement is substantive or name-format only (see Errata §6)

## RECOMMENDED ORDER:
1. **CRITICAL books while context is fresh:** النكت (#14), أبنية (#16)
2. **Framework VERIFY books:** الأحاديث الأربعين (#11), الإبدال (#12), المستدرك (#13), معالم بيانية (#15)
3. **Edition variants (Group A):** Quick cross-edition checks (#1-7)
4. **Riwayah books (Group B):** #8-10
5. **Remaining new works (Group D):** Famous classics first (#20 سير, #22 لسان, #18 بداية المجتهد), then sharh works (#21, #23), then institutional (#17), then mukhtasar (#19)
6. **After all 23 verdicts:** Produce cross-edition consistency tables for Group A, consistency self-check, confidence calibration, and cross-book patterns.

**After book 12:** pause and run the mid-session quality gate from EVALUATION_QUICK_REFERENCE.md.

**After all 23 verdicts:** This is the FINAL evaluation session. The report must include everything needed for aggregation. Commit the report, then the owner will run review rounds.
