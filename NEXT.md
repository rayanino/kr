# NEXT — Phase C Evaluation: Session 2 (Famous Works A)

## Status
- Session 0 (Calibration): ✅ COMPLETE — 3 books, framework validated
- Session 1 (Fixture Regression): ✅ COMPLETE — 11 books (14 total with calibration)
  - Verdicts: 10 VERIFIED, 4 PLAUSIBLE, 0 FLAG
  - Reports: PHASE_C_SESSION1_REPORT.md, PHASE_C_SESSION1_DEEP_ANALYSIS.md, PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md
- Sessions 2–7: PENDING

## Session 2 books (8):
حاشية ابن عابدين, لسان العرب, سير أعلام النبلاء, فتح الباري - ط السلفية, بداية المجتهد, الموسوعة الفقهية الكويتية, مسند أحمد, زاد المستقنع

## Pre-identified risks for Session 2 (from strategic analysis):
- مسند أحمد: HIGH RISK — ML disagree + tahqiq-as-layer bias
- فتح الباري: tahqiq-as-layer bias (Opus ML may be over-extended)
- حاشية ابن عابدين: death date real inference (1252 — verify independently)
- بداية المجتهد: death date real inference (595 — verify independently)
- تكملة حاشية ابن عابدين: death date real inference (1306 — verify independently, Session 6 cross-compare)

## CRITICAL methodology fixes from Session 1 (MUST follow):
1. **Search BEFORE writing verdict** — never after, never skip
2. **Use web_fetch** on at least 1 URL per book
3. **Add shamela_category cross-check** to every verdict
4. **Distinguish death-date pass-through vs inference** — only inference is diagnostic
5. **Check result.json model source** for every success book (which model won?)
6. **Session-end consistency check** as a SEPARATE pass, not inline

## Before starting Session 2, read these in order:
1. PHASE_C_EVALUATION_FRAMEWORK.md (632 lines — full protocol)
2. **PHASE_C_ERRATA.md** (CRITICAL — corrections to framework and LESSONS.md)
3. PHASE_C_CALIBRATION_BUGS.md (engine bugs found, with workarounds)
4. PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md (predictions + risk map for all sessions)

## Key corrections from calibration (still apply):
- LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
- 6 books use `gpt_5_4.json` instead of `command_a.json` — check per-book
- 0/73 single-model fallback (LESSONS.md claim of 73/73 is false)
- result.json author confidence is always 1.0 (ENGINE BUG) — read from llm_responses/ instead
- Framework Section 7 (single-model) does not apply
