# S-1 collection bundle

This bundle preserves questionnaire-side material for **S-1 — Priority ranking under conflict**.

It is a **collection bundle**, not promoted doctrine.

## Two-layer separation

1. **Owner-faithful questionnaire answer**  
   What the owner could honestly stand behind as the answer to the questionnaire.

2. **Engineering / protocol expansion**  
   Structured analysis that expands the implications of the answer for engine design, safeguards, and red-team evaluation.

These layers are intentionally kept separate.

## Raw owner source artifacts

This collection preserves two raw source artifacts:

- `source_artifacts/s1_full_user_input_2026_04_07.txt`  
  The full question block and raw owner reaction as provided in the prompt.

- `source_artifacts/s1_owner_raw_reaction_2026_04_07.txt`  
  The raw owner reaction only.

These artifacts are preserved verbatim for traceability and no-loss routing.

## Metadata fields

- `source_basis`
  - `explicit_draft` = directly stated in the owner’s raw reaction
  - `inferred_from_prior_chat` = strongly implied by earlier established owner principles in this same chat
  - `model_expansion` = additional structured analysis added for engineering usefulness; not owner truth by default

- `owner_relation`
  - `owner_explicit` = directly owned by the raw reaction
  - `owner_consistent_inference` = strongly consistent with the owner’s established views
  - `model_only` = useful engineering expansion only

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — owner-faithful app-ready answer
- `02_case_dossier.md` — disciplined narrative analysis
- `03_terms.yaml` — controlled vocabulary
- `04_priority_decision_ladder.jsonl` — atomic ranking decisions
- `05_priority_ranking_matrix.yaml` — one structured record per ranked item
- `06_tradeoff_scenarios.jsonl` — operational conflict scenarios
- `07_term_disambiguation.jsonl` — dangerous alternative readings of the question terms
- `08_goal_vs_constraint_analysis.jsonl` — structural asymmetry analysis
- `09_failure_modes_by_priority.jsonl` — what fails when each priority loses
- `10_nonnegotiables.jsonl` — non-negotiable constraints
- `11_red_team_tests.jsonl` — adversarial tests
- `12_traceability.jsonl` — no-loss routing of raw points
- `13_open_questions.jsonl` — genuine unresolved questions only
- `14_hard_judgment.md` — blunt concluding judgment
