# NEXT — Phase C Evaluation: Session 3 (Famous Works B)

## Status
- Session 0 (Calibration): ✅ COMPLETE — 3 books
- Session 1 (Fixture Regression): ✅ COMPLETE — 11 books
- Session 2 (Famous Works A): ✅ COMPLETE — 8 books, 8 VERIFIED (1 with ML field-level flag)
  - Report: PHASE_C_SESSION2_REPORT.md
  - Running totals: 18 VERIFIED, 4 PLAUSIBLE, 0 FLAG, 0 ESCALATE (22 books)
- Sessions 3–7: PENDING

## Session 3 books (7) — Famous Works B:
الرحيق المختوم, الأم للشافعي, الرسالة للشافعي, الأذكار للنووي ت الأرنؤوط, شرح النووي على مسلم, مجموع الفتاوى, الأربعون النووية

Note: مجموع الفتاوى and الأربعون النووية were evaluated in Session 0 (calibration). They serve as regression checks — verdicts should be consistent with calibration.

## Pre-identified risks for Session 3 (from strategic analysis):
- الرسالة للشافعي: HIGH RISK — ML disagreement (tahqiq-as-layer, same as مسند أحمد). Opus=true with tahqiq_note (Ahmad Shakir), CA=false. Expected: false.
- الرسالة للشافعي: death date inference — check if 204 is embedded in raw text or genuine inference
- الرحيق المختوم: death date inference (المباركفوري, 1427) — check raw text vs genuine inference
- الأم للشافعي: genre ambiguity — what genre fits best? (verify against sources, not training data)
- الأذكار للنووي: note this uses GPT-5.4 as second model (one of the 6 GPT-5.4 books)
- شرح النووي على مسلم: genuine sharh — ML=true expected, both models should agree

## Key Session 2 findings (carry forward):
1. **Tahqiq-as-layer bias confirmed 3 times** (الرسالة, مختصر صحيح مسلم, مسند أحمد). مسند أحمد had 0.90 ML confidence on a WRONG answer — high-conf+wrong is the most dangerous pattern.
2. **Death date "real inferences" were false positives** for حاشية ابن عابدين and بداية المجتهد — dates were embedded in author_name_raw. Check raw text before classifying as genuine inference.
3. **Attribution: Opus says "definitive" for famous classical works** (not "traditional" as SPEC predicts). Only obscure books get "traditional." This is arguably more accurate.
4. **CA's 'sirah' in science_scope for سير أعلام النبلاء is technically wrong** — sirah means prophetic biography, not general biographical dictionary. Watch for similar science_scope precision issues.
5. **CA layer structure can be wrong** even when binary ML is correct — for حاشية ابن عابدين, CA conflated matn and sharh authors.

## Methodology fixes (ALL still apply):
1. Search BEFORE writing verdict
2. Use web_fetch on at least 1 URL per book (Session 2 achieved 4/8 — aim for 7/7)
3. Shamela category cross-check in every verdict
4. Death date pass-through vs inference — check author_name_raw text, not just author_death_hijri field
5. Result.json model source for success books
6. Session-end consistency check as SEPARATE pass
7. **NEW: Confidence calibration section required** (was missing in Session 2 initial draft)

## Before starting Session 3, read these in order:
1. PHASE_C_EVALUATION_FRAMEWORK.md
2. PHASE_C_ERRATA.md (corrections override framework)
3. PHASE_C_SESSION2_REPORT.md (for cross-session consistency and carried-forward findings)
4. PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md (Session 3 risk predictions)

## After completing all verdicts:
Paste the contents of SELF_REVIEW_PROMPT.md four times (once after output, then after each review round). The prompt auto-detects which round it is. Each round attacks from a different angle — do not skip rounds.

## Key corrections from calibration (still apply):
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- 6 books use `gpt_5_4.json` instead of `command_a.json` — check per-book (الأذكار is one of them)
- 0/73 single-model fallback
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/
- Framework Section 7 (single-model) does not apply
- Consensus does NOT check multi-layer (Correction 7)
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) count as ONE source for VERIFIED threshold

## Attribution decision (RESOLVED — updated by Session 2):
Opus says "definitive" for famous well-established classical works (not "traditional" as originally expected). Opus says "traditional" for obscure conventionally-attributed works. Both are correct in their respective contexts. Only flag when Opus says "disputed" — those are genuine scholarly disputes.
