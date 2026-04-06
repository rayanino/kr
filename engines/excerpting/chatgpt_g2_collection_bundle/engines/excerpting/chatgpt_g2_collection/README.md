# G2 collection bundle

This bundle preserves questionnaire-side collection material for **G2**. It is **not promoted doctrine**. It captures two layers at the same time without collapsing them:

1. **Owner-faithful questionnaire answer** — what the owner could honestly stand behind as the answer to the prompt.
2. **Engineering / protocol expansion** — deeper structural analysis, packaging implications, proof-layer implications, and red-team material extracted from the case.

## Raw owner source artifacts

This collection preserves two raw source artifacts exactly as source artifacts rather than normalized doctrine:

- `source_artifacts/g2_full_user_input_2026_04_04.txt` — the full user input block for this question.
- `source_artifacts/g2_owner_raw_reaction_2026_04_04.txt` — the owner's raw reaction only.

These files are preserved verbatim and are not summarized there.

## Meaning of metadata fields

- `source_basis`
  - `explicit_draft`: directly stated by the owner in the raw reaction.
  - `inferred_from_prior_chat`: strongly implied by the owner’s earlier established standards in this chat.
  - `model_expansion`: broader engineering or red-team expansion that should **not** be mistaken for owner truth.

- `owner_relation`
  - `owner_explicit`: explicitly stated by the owner.
  - `owner_consistent_inference`: not directly stated in this exact raw reaction, but strongly consistent with the owner’s established stance.
  - `model_only`: engineering expansion only.

## File map

- `00_manifest.yaml` — bundle metadata and counts.
- `01_questionnaire_answer.md` — app-ready owner answer only.
- `02_case_dossier.md` — human-readable engineering / protocol analysis.
- `03_terms.yaml` — controlled vocabulary for this case.
- `04_decision_ladder.jsonl` — layered reasoning trail.
- `05_candidate_split_map.jsonl` — minimal and deeper split candidates.
- `06_explanation_layers.jsonl` — distinct explanatory layer classifications.
- `07_hadith_chunking_strategy.jsonl` — chunk-based explanation strategy.
- `08_proof_relationships.jsonl` — relationships between proofs.
- `09_proof_identifier_strategy.jsonl` — identifier uniqueness strategy.
- `10_vocabulary_branching.jsonl` — vocabulary / grammar / dictionary branching implications.
- `11_cross_topic_proof_reuse.jsonl` — same-proof multiple-topic reuse implications.
- `12_nonnegotiables.jsonl` — machine-readable constraints.
- `13_red_team_tests.jsonl` — adversarial tests.
- `14_priority_matrix.yaml` — ranked issue landscape.
- `15_traceability.jsonl` — proof that the raw owner answer was not flattened.
- `16_open_questions.jsonl` — genuine unresolved protocol gaps only.
- `17_hard_judgment.md` — blunt summary judgment.
