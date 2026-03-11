# NEXT — Phase C Evaluation: Session 4 (Multi-Layer + Commentary)

## Status
- Session 0 (Calibration): ✅ COMPLETE — 3 books
- Session 1 (Fixture Regression): ✅ COMPLETE — 11 books
- Session 2 (Famous Works A): ✅ COMPLETE — 8 books, 8 VERIFIED (1 with ML field-level flag)
- Session 3 (Famous Works B): ✅ COMPLETE — 7 books, 7 VERIFIED (1 with ML field-level flag)
  - Report: PHASE_C_SESSION3_REPORT.md (commit 27cada7, 4 review rounds)
  - Running totals: 25 VERIFIED, 4 PLAUSIBLE, 0 FLAG, 0 ESCALATE (29 books)
- Sessions 4–7: PENDING

## Session 4 books (10) — Multi-Layer + Commentary

All 10 are commentary/sharh-family works or related. 7 have ML=true (expected). This session tests multi-layer classification depth — not just binary ML, but whether layer chains are bibliographically correct.

| # | Book (exact directory name) | Status | Models | ML (both agree) | Genre (Opus) |
|---|---------------------------|--------|--------|-----------------|--------------|
| 1 | فتح الباري لابن رجب | gate_abort | opus + command_a | true (agree) | sharh |
| 2 | شرح الورقات في أصول الفقه - المحلي | gate_abort | opus + command_a | true (agree) | sharh |
| 3 | حاشية العطار على شرح الجلال المحلي على جمع الجوامع | gate_abort | **opus + gpt_5_4** | true (agree) | hashiyah |
| 4 | شرح العقيدة الطحاوية - ط الرسالة | gate_abort | opus + command_a | true (agree) | sharh |
| 5 | مقامات الحريري | **success** | opus + command_a | false (agree) | adab |
| 6 | شرح مقامات الحريري | gate_abort | opus + command_a | true (agree) | sharh |
| 7 | شرح ديوان المتنبي للواحدي | gate_abort | opus + command_a | true (agree) | sharh |
| 8 | اللامع العزيزي شرح ديوان المتنبي | gate_abort | opus + command_a | true (agree) | sharh |
| 9 | المآخذ على شراح ديوان أبي الطيب المتنبي | **success** | opus + command_a | false (agree) | other |
| 10 | التعليق على الرحيق المختوم | **success** | opus + command_a | true (agree) | hashiyah |

Note: حاشية العطار uses GPT-5.4 as second model (one of the 6 GPT-5.4 books).
Note: 3 books are **success** status — check result.json model source, trust_tier, and confidence_scores for these.
Note: 0 ML disagreements in this batch — consensus agrees on all 10. No tahqiq-as-layer issues expected (the 3 Errata §9 instances are all confirmed in Sessions 2-3).

## Pre-identified risks for Session 4

### HIGH PRIORITY

1. **المآخذ على شراح ديوان أبي الطيب المتنبي: Genre must NOT be sharh.**
   Strategic analysis calls this out explicitly: "Genre for المآخذ (NOT sharh — it's criticism)."
   Pipeline has genre=other, ML=false — correct per framework. But verify: this is a critique OF commentators on المتنبي, not itself a commentary. The title "المآخذ على شراح" = "criticisms of the commentators." Author: الأزدي (ت 644). Success book — check trust.

2. **التعليق على الرحيق المختوم: Genre=hashiyah may be wrong.**
   Opus says hashiyah (which implies 3 layers: matn→sharh→hashiyah) but the layer structure shows only 2 layers: matn=المباركفوري, sharh=الملاح. A real hashiyah requires 3 distinct layers. If this is a 2-layer commentary on الرحيق المختوم, genre should be sharh, not hashiyah. Framework expected: sharh/risalah. Success book — check trust + result.json genre.
   **Death date risk:** Author الملاح has NO death date in extraction (author_death_hijri=null, author_name_raw="محمود بن محمد الملاح" with no embedded date). Any LLM death date is a **genuine inference** — verify independently. This is one of very few genuine inference tests in the corpus.

3. **حاشية العطار: Verify 3-layer chain against external sources.**
   This is a genuine hashiyah. Opus identifies: matn=تاج الدين السبكي (جمع الجوامع), sharh=جلال الدين المحلي, hashiyah=حسن العطار (ت 1250). This is the ONLY hashiyah in Session 4 — the layer chain must be verified. Framework expected: hashiyah/taqrirat, death=1250, ML=true, science=usul_al_fiqh.
   Uses GPT-5.4 — compare its layer structure against Opus for accuracy.

### MEDIUM PRIORITY

4. **Tahqiq-as-layer on genuine sharh books (3 books).**
   فتح الباري لابن رجب, شرح الورقات, and شرح العقيدة الطحاوية all have tahqiq_note as an additional layer from Opus — BUT binary ML=true is correct for all three because they ARE genuine sharh works. Do NOT flag these. Same pattern as فتح الباري بشرح البخاري in Session 2 (noted, not flagged). Note the tahqiq_note but confirm binary classification is correct.

5. **المتنبي commentary cluster (3 books).**
   شرح ديوان المتنبي للواحدي (sharh, الواحدي ت 468), اللامع العزيزي (sharh, أبو العلاء المعري ت 449), and المآخذ (other/criticism, الأزدي ت 644) are all related to المتنبي's poetry. Verify: the two sharh books should share the same matn author (المتنبي = أبو الطيب أحمد بن الحسين). المآخذ should NOT have المتنبي as matn — it critiques the commentators, not the poetry itself.

6. **Cross-check الرحيق المختوم → التعليق على الرحيق المختوم.**
   Session 3 evaluated الرحيق المختوم by المباركفوري (ت 1427). التعليق is a commentary ON that book by الملاح. Verify: the matn author in التعليق's layer structure matches Session 3's verified author (صفي الرحمن المباركفوري).

### LOW PRIORITY

7. **مقامات الحريري: Genre=adab, ML=false.**
   Literary work, not a commentary. Framework expected: adab/other, ML=false. Success book — check trust_tier. الحريري (ت 516) is well-known.

8. **شرح مقامات الحريري: Author unknown (VERIFY in framework).**
   Framework says author=VERIFY. Opus identifies: أبو العباس أحمد بن عبد المؤمن (sharh=القيسي, death=619). Look up this author independently.

## Key Session 3 findings (carry forward)

1. **Tahqiq-as-layer: all 3 Errata §9 instances now confirmed.** The pattern is: non-commentary book + tahqiq → Opus says ML=true with tahqiq_note → CA/GPT says false. On genuine sharh/hashiyah books, the tahqiq_note layer is harmless (binary ML=true is correct regardless). Session 4 has 3 genuine sharh books with tahqiq_note — note but do NOT flag.

2. **Muhaqiq presence is necessary but NOT sufficient for the bias.** الأذكار has muhaqiq (الأرنؤوط) yet ML=false correctly. The differentiating mechanism is unknown.

3. **Death date "real inferences": at least 4/10 from strategic analysis were false positives** (dates embedded in author_name_raw). Only 1 genuine correct inference confirmed (مجموع الفتاوى 728), 1 confirmed wrong (أساليب بلاغية 1432 vs actual 1439). Session 4 has 1 potential genuine inference: التعليق على الرحيق المختوم (الملاح — no date in extraction).

4. **Attribution: Opus says "definitive" for famous works, "traditional" for mediated-transmission works.** Only flag "disputed."

5. **Genre confidence correlates with genuine ambiguity.** Good calibration signal.

6. **GPT-5.4 performs comparably to Command A.** Session 4 has one GPT-5.4 book (حاشية العطار).

## Methodology fixes (ALL still apply)

1. Search BEFORE writing verdict
2. Use web_fetch on at least 1 URL per book (Session 3 achieved 1/7 — aim for higher)
3. Shamela category cross-check in every verdict
4. Death date pass-through vs inference — check author_name_raw text, not just author_death_hijri field
5. Result.json model source for the 3 success books (مقامات, المآخذ, التعليق)
6. Session-end consistency check as SEPARATE pass
7. Confidence calibration section required
8. **NEW for Session 4:** For ML=true books, verify layer chain against external sources

## Before starting Session 4, read these in order:
1. PHASE_C_ERRATA.md (corrections override framework — DEEP READ, these are the actual rules)
2. PHASE_C_EVALUATION_FRAMEWORK.md (SKIM for context — verdict scale, expected values table for Session 4 books)
3. PHASE_C_SESSION3_REPORT.md (READ verdicts + findings sections, SKIM per-book details)
4. PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md (Session 4 risk: MEDIUM, المتنبي commentaries are edge cases)
5. **EVALUATION_QUICK_REFERENCE.md** — re-read this before EACH book

## After completing all verdicts:
Paste the contents of SELF_REVIEW_PROMPT.md four times (once after output, then after each review round). The prompt auto-detects which round it is. Each round attacks from a different angle — do not skip rounds.

## Key corrections from calibration (still apply):
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- 1 book in Session 4 uses `gpt_5_4.json` instead of `command_a.json` (حاشية العطار)
- 0/73 single-model fallback
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/
- Framework Section 7 (single-model) does not apply
- Consensus does NOT check multi-layer (Correction 7) — though in Session 4 all 10 books have ML agreement
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) count as ONE source for VERIFIED threshold

## Attribution decision (RESOLVED):
Opus says "definitive" for famous well-established classical works. Opus says "traditional" for obscure conventionally-attributed works OR for works with complex transmission history (e.g., الأم). Both are correct in their respective contexts. Only flag when Opus says "disputed."

## SESSION 4 SPECIFIC: Multi-layer verification protocol
For every ML=true book (7/10 in this session):
1. Read the layer structure from Opus
2. For each layer: verify the author name and role against external sources
3. If there's a tahqiq_note layer on a genuine sharh: NOTE it but do NOT flag (binary ML=true is correct)
4. If there's a genre=hashiyah: verify there ARE 3 distinct layers (matn→sharh→hashiyah) with 3 distinct authors
5. Cross-check layer matn authors across related books (المتنبي cluster: 3 books share the same matn author)
6. Session 2 found that CA's layer detail can be wrong even when binary ML is correct (حاشية ابن عابدين: CA conflated matn/sharh authors). Check both models' layer structures, not just Opus.
