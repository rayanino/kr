# After Completion Checklist

Use this only after you finish the active questionnaire packet.

## What Counts As "Finished"

Current questionnaire state:

- 40 core slots total
- 38 answerable right now
- 2 intentionally blocked: `CJ-2`, `CJ-3`
- 6 optional supplementals

You are "finished enough" when you have:

1. answered the active core questions
2. answered any supplementals you have energy for
3. saved any DR outputs you received

## Source Files That Matter

If you used the review UI, your main response artifacts are:

- `integration_tests/questionnaire/questionnaire_responses.jsonl`
- `integration_tests/questionnaire/comparison_responses.jsonl` (only if comparison becomes available later)

If you also answered supplementals outside the UI, keep those markdown/text files
with the same review packet.

## Deep Research Next Step

After the questionnaire is done, use the **post-completion** prompts in:

- `docs/codex/weekend_dr_prompts.md`

Before dispatching reviewers, generate a quick completion snapshot:

```bash
python scripts/summarize_questionnaire_responses.py
```

This writes:

- `integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.md`
- `integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.json`

Then run a response audit:

```bash
python scripts/audit_questionnaire_responses.py
```

This writes:

- `integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.md`
- `integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.json`

Important access rule:

- ChatGPT DR = remote-only
- Claude DR (browser) = remote-only unless you paste files
- Gemini DR = upload current local files

So for unpushed current work, Gemini is the safest browser DR path.

To build a ready-made Gemini upload folder from the current local checkout:

```bash
python scripts/build_questionnaire_dr_bundle.py --profile gemini-post --output-dir overnight_codex/gemini_questionnaire_bundle_post
```

## What To Upload Or Paste For Post-Completion DR

Minimum useful set:

- `questionnaire_responses.jsonl`
- `OWNER_QUESTIONNAIRE.md`
- `SUPPLEMENTAL_OWNER_QUESTIONS.md`
- `TEAM_TRANSLATION_GUIDE.md`
- `CRITICAL_EVALUATION_GUIDE.md`
- `OWNER_FEEDBACK_GUARDRAIL.md`

## Where To Save Returned Reviews

Preferred folder:

- `integration_tests/questionnaire/evaluation_reports/`

Use clear names like:

- `chatgpt_dr_feasibility_YYYY_MM_DD.md`
- `claude_dr_scholarly_YYYY_MM_DD.md`
- `gemini_dr_pedagogical_YYYY_MM_DD.md`

## Non-Negotiable Rule

Do not treat the finished questionnaire as the final answer.

The questionnaire is the input to the evaluation phase, not the end of it.

The right sequence is:

1. owner answers
2. coworker review
3. synthesis
4. narrow follow-up questions if needed
5. only then bounded translation into SPEC / prompt / policy

## If You Want To Commit Your Review Work

Safe narrow command:

```bash
git add integration_tests/questionnaire
```

Avoid `git add -A` in this repo.
