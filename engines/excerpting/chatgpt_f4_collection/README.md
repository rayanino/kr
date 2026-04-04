# F4 collection bundle

This bundle preserves questionnaire-side material for **F4**. It is **not promoted doctrine**. It is a structured collection built from one single-excerpt judgment question plus the owner's raw reaction.

## What F4 is

F4 is a layered judgment on the excerpt:

`واختلف العلماء في حقيقة اليد التي تقطع على أقوال: وأصحها، ما ذهب إليه الجمهور،`

The surface question is whether the excerpt works as its own entry. The deeper issue is how one short segment reveals problems of function detection, disagreement-marking, tarjih separation, attribution sensitivity, question-cluster reasoning, and intelligent context diagnosis.

## Why this is a collection bundle, not promoted doctrine

This folder is questionnaire-side collection material. It preserves:
1. the **owner-faithful questionnaire answer**
2. an **engineering / protocol expansion layer**

It does **not** promote these materials into the excerpt canon automatically. It exists so the owner answer is preserved cleanly while the engineering implications are also captured without being mislabeled as owner truth.

## Two-layer separation

### Layer A — owner-faithful questionnaire answer
The file `01_questionnaire_answer.md` contains only what the owner could honestly stand behind as the answer to the questionnaire.

### Layer B — engineering / protocol expansion
The other analytical files expand the case into function analysis, candidate sub-excerpts, context dependencies, question clusters, nonnegotiables, and red-team tests.

## Raw owner source artifacts

Two raw source artifacts are preserved verbatim:

- `source_artifacts/f4_full_user_input_2026_04_04.txt`
- `source_artifacts/f4_owner_raw_reaction_2026_04_04.txt`

These are not cleaned, normalized, or doctrinally rewritten. They preserve the owner wording directly.

## Metadata conventions

### `source_basis`
Where an item came from:
- `explicit_draft` — directly stated in the owner's raw input
- `inferred_from_prior_chat` — strong inference from earlier established standards in this chat
- `model_expansion` — engineering expansion generated beyond explicit owner wording

### `owner_relation`
How closely the item relates to owner truth:
- `owner_explicit` — explicitly stated by the owner
- `owner_consistent_inference` — not directly stated, but strongly consistent with owner standards
- `model_only` — engineering expansion only; not owner truth

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — owner-faithful app-ready answer
- `02_case_dossier.md` — human-readable engineering/protocol analysis
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered reasoning chain
- `05_candidate_excerpts.jsonl` — corrected excerpt candidates
- `06_function_placement.jsonl` — surface vs actual function mapping
- `07_question_cluster_analysis.jsonl` — what questions belong together
- `08_context_dependency_analysis.jsonl` — context and dependency handling
- `09_nonnegotiables.jsonl` — machine-readable constraints
- `10_red_team_tests.jsonl` — adversarial tests for this case
- `11_priority_matrix.yaml` — ranked issue landscape
- `12_traceability.jsonl` — proof that the owner's raw reaction was not flattened
- `13_open_questions.jsonl` — residual protocol gaps, if any
- `14_hard_judgment.md` — blunt final assessment
