# Claude Code Spec Alignment Packet

- Reviewer lane: `claude_code_spec_alignment`
- Access mode: local checkout
- Goal: check which answers create SPEC conflicts, cross-engine implications, or implementation-heavy consequences

## Fill This In Before Finalizing The Review

- Reviewer:
- Date:
- Review target:
- Known limitations:

## Use These Inputs

- `integration_tests/questionnaire/questionnaire_responses.jsonl`
- `integration_tests/questionnaire/external_questionnaire_responses.json`
- `integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.md`
- `integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.md`
- `integration_tests/questionnaire/OWNER_FEEDBACK_GUARDRAIL.md`
- `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md`
- `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md`
- `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md`

## Required Stance

- owner answers are signal, not authority
- owner confidence is metadata, not proof
- scholarly invariants outrank preference
- if access is remote-only, do not pretend unpushed local files are visible

## Expected Output

Place the final report in:

- `integration_tests/questionnaire/evaluation_reports/`

Use a filename matching this lane, for example:

- `claude_code_spec_alignment_YYYY_MM_DD.md`

## Minimum Questions To Answer

1. What are the highest-risk answers in this response set?
2. Which answers are safe to translate, and which must be challenged?
3. Which answers are only local preference or only point to a deeper need?
4. Which follow-up questions are truly necessary, if any?

## Reminder

Do not translate owner answers directly into implementation.
