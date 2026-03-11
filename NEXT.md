# NEXT — Phase C Evaluation: Session 7 (Remaining — 10 Unevaluated Books)

## Status
- Session 0 (Calibration): ✅ COMPLETE — 3 books
- Session 1 (Fixture Regression): ✅ COMPLETE — 14 books (includes 3 calibration + أبنية, مذكرات العفن, همع الهوامع)
- Session 2 (Famous Works A): ✅ COMPLETE — 14 books (includes بداية المجتهد, زاد المستقنع, سير أعلام, الموسوعة الفقهية, لسان العرب, فتح الباري ط السلفية, مسند أحمد ت شاكر)
- Session 3 (Famous Works B): ✅ COMPLETE — 7 books (includes الرحيق المختوم, الرسالة للشافعي, شرح النووي على مسلم)
- Session 4 (Multi-Layer + Commentary): ✅ COMPLETE — 10 books, 9 VERIFIED + 1 PLAUSIBLE
- Session 5 (Attribution + Trust + Obscure): ✅ COMPLETE — 10 books, 4 VERIFIED + 6 PLAUSIBLE
- Session 6 (Edition Groups): ✅ COMPLETE — 17 books, 17 VERIFIED
  - Report: PHASE_C_SESSION6_REPORT.md (commit 7cc38e5, 4 review rounds)
  - Running totals: 55 VERIFIED, 11 PLAUSIBLE, 0 FLAG, 0 ESCALATE (66 verdicts across 63 unique books)
- Session 7 (Remaining): **PENDING** ← YOU ARE HERE
- Aggregation: PENDING

## CRITICAL NOTE: Prior session coverage was broader than originally tracked

Round 5 handoff verification discovered that Sessions 1-3 evaluated MORE books than the original tracking assumed. 13 books that were initially listed as "unevaluated" were found in prior session reports with exact directory-name matches. The corrected count is **10 truly unevaluated books**, not the 23 originally planned. The 13 already-evaluated books and their sessions are documented at the end of this file.

## Session 7 — 10 Unevaluated Books

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Key risk |
|---|---------------------------|--------|--------|--------------|-----|----------|
| **Framework VERIFY books (5)** |||||
| 1 | الأحاديث الأربعين النووية مع ما زاد عليها ابن رجب وعليها الشرح الموجز المفيد | success | opus + command_a | sharh | T | **Framework: VERIFY.** trust=flagged (0.4325). Author conf=0.82. death=None. Result.json genre=sharh, ML=true. Cross-check: Session 0 evaluated الأربعون النووية (the base matn) |
| 2 | الإبدال في لغات الأزد دراسة صوتية في ضوء علم اللغة الحديث | success | opus + command_a | risalah | F | **Framework: VERIFY.** trust=flagged (0.455). **Page mismatch: 73 digital of 494 physical (15%).** Modern academic work. Author conf=0.92 |
| 3 | المستدرك على مجموع الفتاوى | gate_abort | opus + **gpt_5_4** | fatawa | F | **Framework: VERIFY.** GPT-5.4 as second model. Cross-check: Session 0 evaluated مجموع الفتاوى (ابن تيمية ت 728) — المستدرك is a DIFFERENT work by a DIFFERENT compiler. death=728 (both models) |
| 4 | النكت على شرح النووي على صحيح مسلم | gate_abort | opus + command_a | other | F | **Framework: VERIFY.** Author=هاني فقيه (modern), conf=**0.75** (lowest in corpus). death=None. **Genre disagreement: Opus=other, CA=hashiyah.** Gate error: "is_multi_layer=true but text_layers is empty" |
| 5 | معالم بيانية في آيات قرآنية | success | opus + command_a | tafsir | F | **Framework: VERIFY.** trust=flagged (0.4325). **Only 2 content pages (content_minimal).** Author=المغامسي (modern). DIFFERENT BOOK from Session 3's "معالم بيانية في أحاديث نبوية" — same author, different content |
| **Riwayah + hadith books (3)** |||||
| 6 | تاريخ ابن معين - رواية الدارمي | gate_abort | opus + command_a | tabaqat | F | author=ابن معين (ت 233). Genre=tabaqat — biographical, not hadith_collection |
| 7 | حديث يحيى بن معين رواية أبي منصور الشيباني | gate_abort | opus + command_a | hadith_collection | F | Same author as #6 (ابن معين ت 233) but DIFFERENT work (hadith juz'). Riwayah field present in extraction. 43 pages |
| 8 | مسند أبي حنيفة رواية الحصكفي | gate_abort | opus + command_a | hadith_collection | F | author=أبو حنيفة (ت 150), conf=0.92. Verify: is the pipeline author the original narrator (أبو حنيفة) or the compiler (الحصكفي)? |
| **Edition variant + riwayah variant (2)** |||||
| 9 | مختصر صحيح مسلم للمنذري ت الألباني | gate_abort | opus + command_a | mukhtasar | **T** | **Opus ML=true (tahqiq_note) — same pattern as Session 2's مختصر صحيح مسلم.** CA ML=false. Cross-edition check with Session 2 verdict |
| 10 | من أحاديث سفيان الثوري - رواية السري بن يحيى - جوامع الكلم | success | opus + command_a | hadith_collection | F | **Consensus DISAGREED** (name format only — not substantive per Errata §6). trust=verified (0.6925). Riwayah variant of Session 1's من أحاديث سفيان الثوري |

**Totals:** 4 SUCCESS books (#1, #2, #5, #10), 6 GATE_ABORT (#3, #4, #6, #7, #8, #9). 1 GPT-5.4 book (#3). 1 consensus-DISAGREED (#10). 5 framework-VERIFY books (#1-5).

## Pre-identified risks

### CRITICAL PRIORITY

1. **النكت على شرح النووي (#4): Lowest confidence in entire corpus, genre disagreement, special gate error.**
   Author=هاني فقيه (modern), conf=0.75 (Opus), 0.85 (CA), death=None. Genre: Opus=other (0.82), CA=hashiyah (0.90). The gate error is unusual: "is_multi_layer=true but text_layers is empty." This is the most uncertain identification in the remaining corpus. Needs deepest investigation.

2. **المستدرك على مجموع الفتاوى (#3): GPT-5.4 as second model.**
   Cross-check with Session 0's مجموع الفتاوى. المستدرك is NOT the same work — it compiles fatwas MISSED in the original. Verify: is the pipeline author ابن تيمية (original fatwa issuer) or the compiler (ابن القاسم)?

### HIGH PRIORITY

3. **معالم بيانية في آيات قرآنية (#5): Only 2 content pages, content_minimal.**
   DIFFERENT BOOK from Session 3's "معالم بيانية في أحاديث نبوية" (confirmed: different directory name, different title_full). Same author (المغامسي), different content (آيات vs أحاديث). Genre: result.json=tafsir. With only 2 pages, all classification is minimal evidence.

4. **الأحاديث الأربعين مع ابن رجب (#1): Framework VERIFY, author conf=0.82, death=None.**
   Result.json: genre=sharh, ML=true, trust=flagged (0.4325). Cross-check: Session 0 evaluated الأربعون النووية (the base matn by النووي ت 676). Identify the actual sharh author from the title and verify the layer chain.

5. **مختصر صحيح مسلم ت الألباني (#9): Tahqiq_note pattern (5th Opus instance).**
   Opus ML=true (layers: matn + tahqiq_note), CA ML=false. Same pattern as Session 2's مختصر صحيح مسلم. Cross-edition check required.

### MEDIUM PRIORITY

6. **مسند أبي حنيفة (#8): Author attribution ambiguity.** conf=0.92. The pipeline identifies أبو حنيفة (ت 150) as author, but this is a musnad compiled from his narrations — verify whether the correct primary attribution is to أبو حنيفة or to the compiler الحصكفي.

7. **ابن معين pair (#6, #7): Same author, different works.** Both correctly identify يحيى بن معين (ت 233). #6 is tabaqat (biographical), #7 is hadith_collection. Verify the genre distinction is correct.

8. **من أحاديث سفيان الثوري (#10): Riwayah variant.** Consensus DISAGREED (name format only — not substantive per Errata §6). Cross-check with Session 1's verdict on the other رواية.

## Success books — trust tiers (4 books)

| Book | Trust tier | Score |
|------|-----------|-------|
| الأحاديث الأربعين مع ابن رجب (#1) | flagged | 0.4325 |
| الإبدال في لغات الأزد (#2) | flagged | 0.4550 |
| معالم بيانية في آيات قرآنية (#5) | flagged | 0.4325 |
| من أحاديث سفيان الثوري رواية السري (#10) | verified | 0.6925 |

## Key findings carried forward from Session 6

1. **Zero author errors across 66 verdicts (63 unique books).** Running total: 0 errors.

2. **Opus attribution taxonomy:** "definitive" for famous works; "traditional" for conventional; "disputed" for genuinely contested. CA tends toward "definitive."

3. **Death date genuine inference running total:** 3 correct (728, 324, 1306), 1 wrong (1432 vs 1439), 9 false positives. Session 7: check author_name_raw for embedded dates before classifying any inference as "genuine."

4. **Tahqiq_note ML=true pattern — cumulative 4 instances:** Opus: 3 (الرسالة, مختصر صحيح مسلم, مسند أحمد). GPT-5.4: 1 (تفسير الطبري ط التربية). Command A: 0/67. Session 7 has 1 new expected instance (#9 مختصر صحيح مسلم ت الألباني).

5. **Authority_level disagreements:** Opus=reference vs CA=primary on sharh works (9/11 across Sessions 4-6). Session 7 has 1 sharh work (#1 الأحاديث الأربعين) — check for this pattern.

6. **web_fetch compliance:** Sessions 4-6 had 0-1/N actual web_fetch. Session 7 should target at least 3/10 web_fetch calls on high-priority books.

## Methodology fixes (ALL still apply)

1. Search BEFORE writing verdict
2. Use web_fetch on at least 1 URL per VERIFY book (target 3/10 minimum)
3. Shamela category cross-check in every verdict
4. Death date pass-through vs inference — check author_name_raw text
5. Result.json model source for the 4 success books
6. Session-end consistency check as SEPARATE pass
7. Confidence calibration section required
8. **Session 7 specific:** For the 1 GPT-5.4 book (#3), check for model-specific biases
9. **Session 7 specific:** For the 5 framework-VERIFY books (#1-5), deeper investigation (2+ web searches, 1+ web_fetch)
10. **Session 7 specific:** Cross-edition checks for #9 (vs Session 2) and #10 (vs Session 1)

## Before starting Session 7, read these in order:
1. PHASE_C_ERRATA.md (DEEP READ — especially §6, §9)
2. PHASE_C_EVALUATION_FRAMEWORK.md (SKIM — expected values table)
3. PHASE_C_SESSION2_REPORT.md (READ مختصر صحيح مسلم verdict for cross-edition check)
4. PHASE_C_SESSION1_REPORT.md (READ من أحاديث سفيان الثوري verdict for cross-edition check)
5. PHASE_C_SESSION6_REPORT.md (READ findings + cross-book patterns)
6. **EVALUATION_QUICK_REFERENCE.md** — re-read before EACH book

## Key corrections from calibration (still apply):
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- Second model: 9/10 books use `command_a.json`; 1 book (#3 المستدرك) uses `gpt_5_4.json`
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/
- Consensus does NOT check multi-layer — ML must be compared manually
- Shamela-ecosystem sources count as ONE source for VERIFIED threshold
- For the 1 consensus-DISAGREED book (#10): name format only — not substantive (Errata §6)

## RECOMMENDED ORDER:
1. **CRITICAL books while context is fresh:** النكت (#4), المستدرك (#3)
2. **Framework VERIFY books:** الأحاديث الأربعين (#1), الإبدال (#2), معالم بيانية (#5)
3. **Riwayah books:** تاريخ ابن معين (#6), حديث يحيى (#7), مسند أبي حنيفة (#8)
4. **Edition/riwayah variants:** مختصر صحيح مسلم (#9), من أحاديث سفيان (#10)
5. **After all 10 verdicts:** Consistency self-check, confidence calibration, cross-book patterns.

**After all 10 verdicts:** This is the FINAL evaluation session. The report must include everything needed for aggregation. Commit the report, then the owner will run review rounds.

---

## Appendix: Books Already Evaluated in Prior Sessions (13 books)

These were initially listed as unevaluated but found to have exact directory-name matches in prior session reports:

| Book | Already evaluated in | Verdict |
|------|---------------------|---------|
| أبنية الأسماء والأفعال والمصادر | Session 1 | (check report) |
| الرحيق المختوم | Session 3 | (check report) |
| الرسالة للشافعي | Session 3 | (check report) |
| الموسوعة الفقهية الكويتية | Session 2 | (check report) |
| بداية المجتهد ونهاية المقتصد | Session 2 | (check report) |
| زاد المستقنع في اختصار المقنع - ت العسكر | Session 2 | (check report) |
| سير أعلام النبلاء - ط الحديث | Session 2 | (check report) |
| شرح النووي على مسلم | Session 3 | (check report) |
| فتح الباري بشرح البخاري - ط السلفية | Session 2 | (check report) |
| لسان العرب | Session 2 | (check report) |
| مذكرات مالك بن نبي - العفن | Session 1 | (check report) |
| مسند أحمد - ت شاكر - ط دار الحديث | Session 2 | (check report) |
| همع الهوامع في شرح جمع الجوامع | Session 1 | (check report) |

The aggregation session must count these from their original session reports, NOT re-evaluate them.
