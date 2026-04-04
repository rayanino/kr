# ChatGPT F7 Collection

This directory preserves the `F-7` trust-failure package.

It is a collection/preservation lane, not a promoted doctrine canon.

## Layer meanings

- `source_artifacts/f7_owner_raw_draft_2026_04_04.txt`
  The raw owner-source draft for `F-7`.

- `01_questionnaire_answer.md`
  The cleaned owner-answer layer.

- `02_failure_dossier.md`
  The expanded engineering/red-team dossier.

- `03_terms.yaml` through `13_hard_judgment.md`
  Machine-readable and human-readable failure-canon artifacts derived from the prompt.

## Provenance

- `source_artifacts/chatgpt_f7_collection_2026_04_04.zip`
  The original downloaded ZIP bundle preserved verbatim for auditability.

## Usage rule

When later implementation or hardening work consults `F-7`, read in this order:

1. `source_artifacts/f7_owner_raw_draft_2026_04_04.txt`
2. `01_questionnaire_answer.md`
3. `02_failure_dossier.md`
4. the machine-readable supporting files

Do not treat the broader failure canon as direct owner truth unless the file itself clearly belongs to the owner-answer layer.
