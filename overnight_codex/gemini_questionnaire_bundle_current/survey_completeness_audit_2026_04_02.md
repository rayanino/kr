# Survey Completeness Audit — 2026-04-02

Scope:

- `integration_tests/questionnaire/interactions.json` (current 40 interactions)
- `OWNER_QUESTIONNAIRE.md`
- `TEAM_TRANSLATION_GUIDE.md`
- `QUESTIONNAIRE_EXAMPLES.md`
- prior Phase 0 DR/coworker reports from `docs/coworker_reports/2026-04-01_phase0_hardening/`

## Overall Judgment

After the 2026-04-02 hardening pass, the questionnaire package is strong enough
to start owner review without wasting the weekend. The biggest pre-review flaws
have been corrected:

1. `L-2` now uses a real mixed-layer matn + sharh example instead of an abstract prompt
2. `L-3` now uses a real substantive footnote example and explicitly asks about takhrij/grading-style notes
3. `CJ-2` / `CJ-3` are explicitly treated as blocked pending source material instead of pretending to be live questions
4. the translation guide and excerpt audit trail are being kept in sync with the live packet
5. the owner-feedback non-authority rule is now explicit via `OWNER_FEEDBACK_GUARDRAIL.md`

The survey is still **not exhaustive**, but the remaining gaps are now the
right kind of gaps to leave in a supplemental packet rather than the core:

1. term-resolution / technical-term recognition threshold
2. comparative-madhhab text structure as its own teaching unit
3. pedagogical workflow modes (lesson prep vs. memorization vs. review)
4. theology-like cases where linguistic and technical meanings are themselves part of the dispute

## Current Documentation Gaps

- The core packet still needs to stay honest that it contains **40 slots but only 38 currently answerable questions**.
- `QUESTIONNAIRE_EXAMPLES.md` historically lagged behind live owner-facing questions; it must continue to track every excerpt-bearing interaction precisely.
- The current package should still not be treated as the final, exhaustive owner-signal surface without the supplementals.

## Recommendation

Do **not** rewrite or invalidate the current 40-question core.

Instead:

1. keep the current hardened core packet as the primary questionnaire
2. keep `CJ-2` / `CJ-3` visibly blocked until valid comparison material exists
3. use the supplemental owner packet to close the remaining focused gaps
4. treat the supplemental answers as first-class calibration input if the owner
   has time/energy during the weekend

## Supplemental Packet

See:

- `integration_tests/questionnaire/SUPPLEMENTAL_OWNER_QUESTIONS.md`
- `integration_tests/questionnaire/SUPPLEMENTAL_TRANSLATION_GUIDE.md`

These supplementals are designed to minimize extra burden while closing the
most important remaining calibration gaps.
