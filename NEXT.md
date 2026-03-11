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
- Session 6 (Edition Groups): **PENDING** ← YOU ARE HERE
- Session 7 (Riwayah + Remaining): PENDING

## Session 6 — Edition Groups (17 books)

This session evaluates **edition groups**: multiple editions of the same work, where the primary question is cross-edition consistency. The framework's Edition Group Protocol (§ Edition Group Protocol) requires: author, genre, multi-layer, and science MUST match across editions. Muhaqiq and trust MAY differ.

**This is the largest session by book count.** 17 books across 7 edition groups plus the تكملة/حاشية author-verification pair. Prioritize cross-comparison checks over individual deep-dives — the books are mostly famous works where identification is not in doubt.

### Book Table

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Key risk |
|---|---------------------------|--------|--------|--------------|-----|----------|
| **إعلام الموقعين (3 editions)** |||||
| 1 | أعلام الموقعين عن رب العالمين - ط عطاءات العلم | gate_abort | opus + command_a | matn | F | **Consensus DISAGREED** (genre + name + attribution) |
| 2 | إعلام الموقعين عن رب العالمين - ت مشهور | gate_abort | opus + command_a | other | F | Consensus DISAGREED (name format only) |
| 3 | إعلام الموقعين عن رب العالمين - ط العلمية | gate_abort | opus + command_a | other | F | — |
| **البداية والنهاية (2 editions)** |||||
| 4 | البداية والنهاية - ت التركي | **success** | opus + command_a | tarikh | F | trust=verified |
| 5 | البداية والنهاية - ط السعادة | **success** | opus + command_a | tarikh | F | trust=verified |
| **تفسير الطبري (2 editions)** |||||
| 6 | تفسير الطبري جامع البيان - ت التركي | gate_abort | opus + command_a | tafsir | F | — |
| 7 | تفسير الطبري جامع البيان - ط دار التربية والتراث | gate_abort | opus + **GPT-5.4** | tafsir | **F/T disagree** | **ML disagreement: Opus=F, GPT-5.4=T (tahqiq_note)** |
| **تحفة المودود (2 editions)** |||||
| 8 | تحفة المودود بأحكام المولود - ت الأرنؤوط | gate_abort | opus + command_a | risalah | F | — |
| 9 | تحفة المودود بأحكام المولود - ط عطاءات العلم | gate_abort | opus + command_a | risalah | F | **Consensus DISAGREED** (name format only) |
| **فتاوى اللجنة الدائمة (2 editions)** |||||
| 10 | فتاوى اللجنة الدائمة - المجموعة الأولى | **success** | opus + command_a | fatawa | F | Institutional author, no death date |
| 11 | فتاوى اللجنة الدائمة - المجموعة الثانية | gate_abort | opus + command_a | fatawa | F | Institutional author, science scope broader |
| **ألفية ابن مالك (2 editions)** |||||
| 12 | ألفية ابن مالك - ت القاسم | **success** | opus + command_a | nazm | F | genre=nazm (not matn) — verify |
| 13 | ألفية ابن مالك - ط التعاون | gate_abort | opus + command_a | nazm | F | — |
| **شرح العقيدة الطحاوية (2 editions)** |||||
| 14 | شرح العقيدة الطحاوية - ط الأوقاف السعودية - بتعليقات أحمد شاكر | gate_abort | opus + command_a | sharh | T | Cross-check with Session 4 |
| 15 | شرح العقيدة الطحاوية - ط الرسالة | gate_abort | opus + command_a | sharh | T | **Already evaluated Session 4: VERIFIED** |
| **حاشية ابن عابدين + تكملة (author verification pair)** |||||
| 16 | حاشية ابن عابدين = رد المحتار - ط الحلبي | gate_abort | opus + command_a | hashiyah | T | FATHER: ابن عابدين (ت 1252) |
| 17 | تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد المحتار - ط الفكر | gate_abort | opus + command_a | hashiyah | T | **SON: علاء الدين (ت ~1306); consensus DISAGREED; death GENUINE INFERENCE; author_raw EMPTY** |

4 SUCCESS books: البداية (×2), فتاوى اللجنة الأولى, ألفية ت القاسم — check result.json trust_tier and genre.
13 GATE_ABORT books: get classification data from llm_responses/.
1 GPT-5.4 book: تفسير الطبري ط دار التربية والتراث. All others use Command A.
4 consensus-DISAGREED books (from Errata §6): أعلام ط عطاءات, إعلام ت مشهور, تحفة ط عطاءات, تكملة حاشية.

## Pre-identified risks

### CRITICAL PRIORITY

1. **تكملة حاشية ابن عابدين: Author verification — MUST be the SON, not the father.**
   Framework expected: علاء الدين عابدين (SON), death ~1306. Pipeline: Opus identifies محمد علاء الدين بن محمد أمين عابدين (death 1306). CA identifies محمد علاء الدين أفندي (no death). Both correctly identify the SON, not the father. BUT: author_raw is EMPTY (extraction found no author field), and death 1306 is a GENUINE INFERENCE (no death in extraction, no embedded date in raw text — because raw text is empty). CA gives null for death. Consensus DISAGREED (name format + death date 1306 vs null — a substantive disagreement).
   **Cross-check with Book 16 (حاشية ابن عابدين):** Father's book has author=محمد أمين ابن عابدين (ت 1252), extraction has "ت 1252 هـ" embedded in author_raw. The evaluator MUST verify that Book 17's author is the SON and Book 16's is the FATHER — a different person despite nearly identical names.

2. **إعلام الموقعين: Genre inconsistency across 3 editions.**
   This is the ONLY work in the corpus with 3 editions. Genre varies: ط عطاءات → Opus=matn (0.85), CA=usul_al_fiqh (0.95); ت مشهور → Opus=other (0.75), CA=other (0.85); ط العلمية → Opus=other (0.75), CA=matn (0.95). The framework expects risalah/other with ML=false. ALL 3 correctly identify ابن القيم (ت 751). ML=false for all 3 ✓ (critical check from framework: MUST NOT be ML=true).
   Note: أعلام ط عطاءات is in the Errata §6 consensus-disagreed list (genre + name format + attribution disagreement — the only substantive disagreement in that list).

3. **تفسير الطبري ط دار التربية: ML disagreement (Opus=false, GPT-5.4=true).**
   GPT-5.4 says ML=true with layers [matn: الطبري, tahqiq_note: محمود محمد شاكر]. This is the SAME tahqiq_note-as-layer pattern seen in Sessions 2-3 (الرسالة, مختصر صحيح مسلم, مسند أحمد — documented in Errata §9). Opus correctly says ML=false. The other edition (ت التركي, using Command A) has both models saying ML=false. The ML disagreement is model-specific (GPT-5.4) and edition-specific. Note the pattern but do not flag it as an error — it is a known model-level bias. Cumulative tahqiq_note instances: 4 (3 from Errata §9 + this one).

### HIGH PRIORITY

4. **شرح العقيدة الطحاوية: Cross-session check with Session 4.**
   Session 4 evaluated ط الرسالة: VERIFIED. Session 4 findings: author=ابن أبي العز (ت 792), genre=sharh, ML=true, science=['aqidah'], attribution: Opus=traditional, CA=definitive. Session 6 must verify ط الأوقاف matches. Pre-scan confirms: ط الأوقاف has identical classification (sharh, ML=true, ابن أبي العز 792, science=['aqidah'], Opus=traditional, CA=definitive).

5. **حاشية ابن عابدين: 3-layer hashiyah verification.**
   Framework expects hashiyah=T with 3 distinct layers. Both models say hashiyah, ML=true. The evaluator should verify the actual layer chain (matn → sharh → hashiyah) from llm_responses/. The layer chain should be: الدر المختار (sharh by الحصكفي, ت 1088) on تنوير الأبصار (matn by التمرتاشي, ت 1004), with hashiyah by ابن عابدين (ت 1252). Death date 1252: extraction has death=None but "ت 1252 هـ" is embedded in author_raw — this is a false positive inference.

6. **Death date classification for ابن القيم books (أعلام + تحفة ط عطاءات).**
   Both ط عطاءات editions have extraction death=None BUT "691 - 751" is embedded in author_name_raw. Pipeline death 751 appears as "genuine inference" by the extraction field, but dates ARE visible in the raw text. These are FALSE POSITIVE inferences (not genuine). The other editions have death 751 as proper pass-through.
   Updated death date inference running total: 2 correct (728, 324), 1 wrong (1432 vs 1439), 6 false positives (4 prior + 2 new from ابن القيم ط عطاءات editions). تكملة حاشية 1306 is the only new GENUINE inference in Session 6.

### MEDIUM PRIORITY

7. **البداية والنهاية: Both tarikh, NOT tafsir.**
   Critical check (framework top-tier): pre-scan confirms both editions have genre=tarikh, ML=false, ابن كثير (ت 774). Both are success books (check result.json). The danger was misclassifying this as tafsir (ابن كثير also wrote تفسير ابن كثير). Clean.

8. **ألفية ابن مالك: Genre=nazm (not matn).**
   Framework expects matn/nazm. Both editions have genre=nazm — more precise than matn for a versified grammar text. ابن مالك (ت 672), science=['nahw', 'sarf']. ت القاسم is success (check result.json), ط التعاون is gate_abort.

9. **فتاوى اللجنة الدائمة: Institutional author, no death date.**
   Both correctly identify اللجنة الدائمة. Both genre=fatawa. ML=false. Science scope: المجموعة الأولى=['aqidah', 'fiqh']; المجموعة الثانية broader (Opus adds tafsir, usul_al_fiqh). No death date for institutional author — correct. المجموعة الأولى is success (check result.json).

## Key Session 5 findings (carry forward)

1. **Zero author errors across 49 books.** Running total: 0 in 49 books evaluated.

2. **Opus attribution taxonomy confirmed across Sessions 3-5:** "definitive" for famous well-established works; "traditional" for conventionally-attributed works; "disputed" for genuinely contested works. CA tends toward "definitive" even for traditionally-attributed works.

3. **Death date genuine inference running total:** 2 confirmed correct (مجموع الفتاوى 728, الإبانة ت العصيمي 324), 1 confirmed wrong (أساليب بلاغية 1432 vs actual 1439), 4+2 confirmed false positives. Session 6 adds: تكملة حاشية 1306 (GENUINE INFERENCE — empty author_raw).

4. **Tahqiq_note ML=true pattern:** 3 instances (Errata §9: الرسالة, مختصر صحيح مسلم, مسند أحمد). Session 6 has 1 new: تفسير الطبري ط دار التربية (GPT-5.4). Cumulative: 4 instances.

5. **Authority_level disagreements:** Session 4 had 6/10 (Opus=reference vs CA=primary on sharh works). Session 5 had 0/10 (no sharh works). Session 6 has 4 sharh/hashiyah works — check for this pattern.

6. **Cross-edition genre inconsistency:** الإبانة had risalah vs matn (Session 5). إعلام الموقعين has matn vs other vs usul_al_fiqh across 3 editions.

7. **web_fetch compliance:** Session 4: 0/10. Session 5: 1/10. Target at least 3/17 for Session 6.

## Methodology fixes (ALL still apply)

1. Search BEFORE writing verdict
2. Use web_fetch on at least 1 URL per book for high-priority books
3. Shamela category cross-check in every verdict
4. Death date pass-through vs inference — check author_name_raw text, not just author_death_hijri field
5. Result.json model source for the 4 success books
6. Session-end consistency check as SEPARATE pass
7. Confidence calibration section required
8. **Session 6 specific:** For each edition group, run the Edition Group Protocol: author, genre, ML, science MUST match. Muhaqiq and trust MAY differ. Document all inconsistencies.
9. **Session 6 specific:** For تكملة vs حاشية, verify different authors (SON vs FATHER). This is a DIFFERENT-AUTHOR pair, not an edition group.
10. **Session 6 specific:** For books already evaluated in Session 4 (شرح الطحاوية ط الرسالة), cross-reference the Session 4 verdict.

## Before starting Session 6, read these in order:
1. PHASE_C_ERRATA.md (DEEP READ — especially §6 on consensus disagreements, §9 on tahqiq_note)
2. PHASE_C_EVALUATION_FRAMEWORK.md (SKIM — Edition Group Protocol, expected values table)
3. PHASE_C_SESSION4_REPORT.md (READ شرح العقيدة الطحاوية verdict for cross-session check)
4. PHASE_C_SESSION5_REPORT.md (READ findings + cross-book patterns)
5. **EVALUATION_QUICK_REFERENCE.md** — re-read before EACH book

## Key corrections from calibration (still apply):
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- Second model: 16/17 books use `command_a.json`; 1 book (تفسير الطبري ط دار التربية) uses `gpt_5_4.json`
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/
- Framework Section 7 (single-model) does not apply (0/73 single-model fallback)
- Consensus does NOT check multi-layer (Correction 7) — ML must be compared manually
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) count as ONE source for VERIFIED threshold
- For the 4 consensus-DISAGREED books: examine both models and note whether disagreement is substantive or name-format only (see Errata §6)
