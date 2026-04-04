# F3 collection bundle

This bundle preserves the F3 questionnaire work as a **collection bundle**, not as promoted doctrine.

## What F3 is

F3 is a single-excerpt judgment question about a passage on **باب المسح على الخفين**. The question looks like a local multiple-choice judgment, but the owner's raw reaction makes clear that the passage exposes deeper issues:
- function detection
- sub-excerpting
- title retention
- linking-word preservation
- source-scope mismatch

## Why this is a collection bundle, not promoted doctrine

The material here is preserved for later use and inspection. It is not a canon/backfill artifact like the F1 doctrine bundle. It records:
1. the owner's questionnaire answer
2. the engineering / protocol expansion around that answer
3. the raw owner source artifacts

## Two-layer separation

### Layer A — owner-faithful questionnaire answer
This is the narrow answer the owner could honestly stand behind as the response to the questionnaire.

### Layer B — engineering / protocol expansion
This is the broader structured analysis extracted from the raw reaction and prior chat context. It is for later engineering / protocol interpretation and must not be mistaken for direct owner wording.

## Raw owner source artifacts

This collection preserves two raw source artifacts:

- `source_artifacts/f3_full_user_input_2026_04_04.txt`
  - the full question block, excerpt block, option block, and raw reaction
- `source_artifacts/f3_owner_raw_reaction_2026_04_04.txt`
  - the raw owner reaction only

These are preserved verbatim so the owner source layer is not lost or silently normalized.

## Metadata fields

### `source_basis`
Where a nontrivial item came from:
- `explicit_draft`
- `inferred_from_prior_chat`
- `model_expansion`

### `owner_relation`
How closely an item relates to owner truth:
- `owner_explicit`
- `owner_consistent_inference`
- `model_only`

## File map

- `README.md` — this file
- `00_manifest.yaml` — bundle manifest and counts
- `01_questionnaire_answer.md` — owner-faithful app-ready answer
- `02_case_dossier.md` — human-readable engineering / protocol artifact
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered decision steps
- `05_candidate_excerpts.jsonl` — resulting excerpt candidates
- `06_linking_dependencies.jsonl` — linking-word / dependency records
- `07_function_placement.jsonl` — function vs placement classification
- `08_granularity_analysis.jsonl` — split/keep analysis
- `09_nonnegotiables.jsonl` — machine-readable constraints
- `10_red_team_tests.jsonl` — adversarial tests
- `11_priority_matrix.yaml` — ranked issue landscape
- `12_traceability.jsonl` — proof the raw answer was not flattened
- `13_open_questions.jsonl` — unresolved protocol questions that still matter
- `14_hard_judgment.md` — blunt summary
