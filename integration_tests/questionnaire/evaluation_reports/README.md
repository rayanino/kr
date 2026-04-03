# Questionnaire Evaluation Reports

This folder is the single collection point for all post-questionnaire evaluation
artifacts.

Use it only after the owner has answered the active questionnaire.

## Purpose

The owner-feedback guardrail is only real if every evaluator output is captured,
compared, and synthesized in one place.

This folder prevents:

- vague oral summaries
- losing one coworker's challenge
- turning "the owner said X" into "we implemented X"
- mixing pushed/remote reviews with current local-file reviews without saying so
- self-confirming loops where one person both interprets and approves the same owner signal

## Required Inputs

At minimum, collect:

- Codex internal consistency review
- Claude Code / local scholarly-spec alignment review
- Gemini CLI review when available
- ChatGPT DR report
- Claude DR report
- Gemini DR report

If a coworker is unavailable:

- record the failure explicitly
- record whether it was auth, quota, missing files, stale remote state, or tool failure
- continue under degraded mode, but do not silently omit that coworker

## Owner Answer Source Of Truth

Preferred answer artifact:

- `integration_tests/questionnaire/questionnaire_responses.jsonl`

Supported normalized external mirror:

- `integration_tests/questionnaire/external_questionnaire_responses.json`

Preferred generated summary artifacts:

- `integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.md`
- `integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.json`

Generate them with:

```bash
python scripts/summarize_questionnaire_responses.py
```

Preferred generated audit artifacts:

- `integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.md`
- `integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.json`

Generate them with:

```bash
python scripts/audit_questionnaire_responses.py
```

Preferred generated dispatch artifacts:

- `integration_tests/questionnaire/evaluation_reports/dispatch_packets/`

Generate them with:

```bash
python scripts/generate_questionnaire_review_packets.py
```

If the owner answered outside the review UI, reviewers may instead receive:

- pasted markdown answers
- uploaded text files
- screenshots
- a pushed remote copy of the responses

In that case:

1. say so explicitly in the report header
2. do not pretend the JSONL existed if it did not
3. normalize the answers into a stable artifact before final synthesis if possible
4. if `external_questionnaire_responses.json` exists, use it and follow its referenced source layers

## Naming Convention

Use filenames like:

- `codex_consistency_YYYY_MM_DD.md`
- `claude_code_spec_alignment_YYYY_MM_DD.md`
- `gemini_cli_accuracy_YYYY_MM_DD.md`
- `chatgpt_dr_feasibility_YYYY_MM_DD.md`
- `claude_dr_scholarly_YYYY_MM_DD.md`
- `gemini_dr_pedagogical_YYYY_MM_DD.md`

If a report reviewed only remote/pushed state, put that in the file header.
If a report reviewed pasted/uploaded local files, put that in the file header.

## Required Header For Every Report

Every report in this folder should begin with:

```md
# <title>

- Reviewer:
- Date:
- Access mode: local checkout / remote-only / pasted files / uploaded files
- Review target:
- Known limitations:
```

## External Report Adjudication Rule

Browser research outputs do not become local truth automatically.

Treat them like this:

- remote-only repo review: useful pressure-test, not current-local file review
- uploaded-file review: stronger, but still must be adjudicated against the local packet before changes are applied
- methodology/doctrine review: useful for principles, but still must be grounded in local files before patching

For every external report, record:

1. source mode
2. accepted grounded findings
3. rejected / already-fixed / generic claims
4. the local commit(s) that implemented any accepted changes

## Required Synthesis Artifacts

After all available reviews are collected, create:

- `SYNTHESIS_<date>.md`
- `OWNER_FOLLOWUP_<date>.md` if any challenges must go back to the owner

Use the templates in this folder.

If owner-relayed browser research was part of the input set, also consult:

- `OWNER_RELAYED_BROWSER_REPORTS_DIGEST_2026_04_02.md`
- `docs/codex/questionnaire_external_report_adjudication_2026_04_02.md`

## Non-Negotiable Rule

No SPEC change, prompt change, code change, or default policy should be justified
from `questionnaire_responses.jsonl` alone.

The minimum chain is:

`owner answer -> evaluator challenge/confirmation -> synthesis decision -> bounded translation`

And the minimum governance expectation is:

- at least one independent challenge between owner answer and implementation
