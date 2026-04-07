# SC1 Collection Bundle

This bundle preserves questionnaire-side material for **SC1**.

SC1 is not promoted doctrine. It is a **collection bundle** that preserves:
1. an **owner-faithful questionnaire answer**
2. an **expanded engineering / protocol collection**

## Why this is a collection bundle, not promoted doctrine

The purpose of this bundle is to preserve one high-value edge-case analysis without silently promoting it into canon. It captures the owner reaction, the structural tensions exposed by the case, and the engineering implications that should be inspectable later.

## Two-layer separation

- **Owner-faithful questionnaire answer**  
  What the owner could honestly stand behind as the answer to the questionnaire.

- **Engineering / protocol expansion**  
  A broader structured collection that explores what the case reveals about reference-back handling, author-flow assumptions, context restoration, passage linkage, and the pressure to evolve excerpts into teaching units.

These layers must not be blurred together.

## Raw owner source artifacts

This collection includes two raw preservation files:

- `source_artifacts/sc1_full_user_input_2026_04_04.txt`  
  The full questionnaire prompt material and raw owner comments, preserved verbatim.

- `source_artifacts/sc1_owner_raw_reaction_2026_04_04.txt`  
  The raw owner comments only, preserved verbatim.

These are not normalized, cleaned, or doctrinalized.

## Provenance fields

- **source_basis**  
  One of:
  - `explicit_draft`
  - `inferred_from_prior_chat`
  - `model_expansion`

- **owner_relation**  
  One of:
  - `owner_explicit`
  - `owner_consistent_inference`
  - `model_only`

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — owner-faithful app-ready answer
- `02_case_dossier.md` — human-readable engineering dossier
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered reasoning steps
- `05_reference_back_dependencies.jsonl` — reference-back dependency analysis
- `06_author_flow_assumptions.jsonl` — author/reader-flow assumptions
- `07_summary_note_sufficiency.jsonl` — when the summary is enough and when not
- `08_context_restoration_mechanisms.jsonl` — library-side remedies
- `09_teaching_unit_expansion.jsonl` — excerpt-to-teaching-unit pressure
- `10_passage_linkage_patterns.jsonl` — ways excerpts can link to larger passages
- `11_nonnegotiables.jsonl` — machine-readable constraints
- `12_red_team_tests.jsonl` — adversarial tests
- `13_priority_matrix.yaml` — ranked risk landscape
- `14_traceability.jsonl` — proof that the raw answer was not flattened
- `15_open_questions.jsonl` — unresolved protocol questions
- `16_hard_judgment.md` — blunt final judgment
