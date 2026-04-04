# ChatGPT F2 Collection

This directory preserves the lightweight `F-2` study-workflow package.

It is a collection/preservation lane, not a doctrine canon.

## Layer meanings

- `01_owner_answer.md`
  The owner-answer layer. This is the closest preserved answer to the questionnaire response itself.

- `02_workflow_notes.yaml`
  Machine-friendly internal workflow notes derived from the retained implications.

- `03_retained_implications.md`
  Internal retained implications for later engineering interpretation. Not the owner answer.

- `04_model_inference_non_authoritative.md`
  Explicitly non-authoritative model-strengthened inference. Must not be treated as direct owner truth.

## Provenance

- `source_artifacts/chatgpt_f2_collection_2026_04_03.zip`
  The original downloaded ZIP bundle preserved verbatim for auditability.
- `source_artifacts/f2_owner_raw_draft_and_followups_2026_04_03.txt`
  The raw owner draft plus the six follow-up answers and the exact revision steering sent back to ChatGPT.

## Usage rule

When later implementation or hardening work consults `F-2`, read in this order:

1. `source_artifacts/f2_owner_raw_draft_and_followups_2026_04_03.txt`
2. `01_owner_answer.md`
3. `02_workflow_notes.yaml`
4. `03_retained_implications.md`
5. `04_model_inference_non_authoritative.md` only as a clearly separated inference layer
