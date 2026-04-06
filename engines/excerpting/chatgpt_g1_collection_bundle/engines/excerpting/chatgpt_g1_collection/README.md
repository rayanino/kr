# G1 collection

This bundle preserves questionnaire-side material for **G1 — a very short structural transition**.

It is a **collection bundle**, not promoted doctrine. Its job is to preserve two layers without blurring them:

1. **Owner-faithful questionnaire answer** — what the owner could honestly stand behind in the questionnaire.
2. **Engineering / protocol expansion** — structured analysis of why this tiny case matters for excerpt packaging, added benefit, harmlessness, and the tension between objective excerpting and subjective usefulness.

## Raw owner source artifacts

- `source_artifacts/g1_full_user_input_2026_04_04.txt` preserves the full user input for this item verbatim.
- `source_artifacts/g1_owner_raw_reaction_2026_04_04.txt` preserves the raw owner reaction verbatim.

These artifacts are not cleaned, summarized, or normalized.

## Metadata conventions

- `source_basis` means where an item comes from:
  - `explicit_draft`
  - `inferred_from_prior_chat`
  - `model_expansion`
- `owner_relation` means how closely an item should be treated as owner truth:
  - `owner_explicit`
  - `owner_consistent_inference`
  - `model_only`

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — app-ready owner answer only
- `02_case_dossier.md` — human-readable engineering / protocol analysis
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered reasoning path
- `05_added_benefit_analysis.jsonl` — benefit analysis of the micro-transition
- `06_harmlessness_analysis.jsonl` — harmlessness vs obstruction analysis
- `07_candidate_packaging_patterns.jsonl` — candidate ways to package the line
- `08_objectivity_vs_preference.jsonl` — tension analysis
- `09_context_dependency_analysis.jsonl` — role of full context
- `10_nonnegotiables.jsonl` — machine-readable constraints
- `11_red_team_tests.jsonl` — adversarial tests
- `12_priority_matrix.yaml` — ranked issue map
- `13_traceability.jsonl` — proof that the raw answer was not flattened
- `14_open_questions.jsonl` — unresolved gaps, if any
- `15_hard_judgment.md` — blunt local judgment
