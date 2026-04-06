# SC2 Collection Bundle

This bundle preserves questionnaire-side material for **SC2**.

SC2 is an edge-case question about backward references to an earlier hadith inside an explanation excerpt. On the surface it asks whether the owner can still benefit without seeing the previous hadith. At the deeper level it reveals pressures around explained↔explanation linkage, exact proof proximity, version binding, self-containment without manhunt, and the possibility that the pipeline is missing a passage-analysis stage before excerpting.

## Why this is a collection bundle, not promoted doctrine

This folder is a **collection bundle** for questionnaire capture, not a promoted canon artifact. It preserves:

1. the owner-faithful questionnaire answer for SC2
2. the expanded engineering / protocol / red-team analysis extracted from the same case
3. the raw owner-source artifacts so the upstream reasoning is never lost

## Two-layer separation

- **Layer A — owner-faithful questionnaire answer**: what the owner could honestly stand behind in the questionnaire.
- **Layer B — engineering / protocol expansion**: deeper structural implications, machine-readable records, risks, and safeguards.

These layers must not be blurred.

## Raw owner source artifacts

- `source_artifacts/sc2_full_user_input_2026_04_04.txt` preserves the full SC2 prompt and raw owner comments verbatim.
- `source_artifacts/sc2_owner_raw_reaction_2026_04_04.txt` preserves the raw owner reaction block verbatim.

## source_basis

- `explicit_draft`: directly stated in the owner’s raw comments or prompt.
- `inferred_from_prior_chat`: not word-for-word in this one draft, but directly grounded in already established context from this chat.
- `model_expansion`: added by the model for engineering completeness and must never be treated as owner truth.

## owner_relation

- `owner_explicit`: explicitly stated by the owner.
- `owner_consistent_inference`: not stated verbatim, but strongly implied and consistent with the owner’s prior positions.
- `model_only`: model-generated engineering expansion only.

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — app-ready owner answer only
- `02_case_dossier.md` — human-readable engineering / protocol analysis
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered reasoning steps
- `05_explained_explanation_linkage.jsonl` — linkage quality requirements
- `06_linked_hadith_requirements.jsonl` — exact reference requirements
- `07_reference_sufficiency_analysis.jsonl` — sufficiency comparison of reference modes
- `08_study_chunk_flow.jsonl` — study flow implications
- `09_variant_mismatch_risks.jsonl` — wording/version mismatch risks
- `10_passage_analysis_gap.jsonl` — missing pipeline-stage pressure
- `11_self_containment_thresholds.jsonl` — no-manhunt thresholds
- `12_nonnegotiables.jsonl` — machine-readable hard constraints
- `13_red_team_tests.jsonl` — adversarial test ideas
- `14_priority_matrix.yaml` — ranked risk landscape
- `15_traceability.jsonl` — raw-point routing proof
- `16_open_questions.jsonl` — unresolved questions/gaps
- `17_hard_judgment.md` — blunt final judgment
