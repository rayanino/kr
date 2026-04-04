# F6 collection

This bundle preserves questionnaire-side material for **F6**. It is a **collection bundle**, not promoted doctrine.

## What F6 is

F6 looks like a reading-preference question, but the deeper issue is structural: how a scholar-book proof witness should be studied, what should be memorized directly, what should remain unchanged, and what help belongs in parallel layers instead of inside the original text.

## Two-layer separation

This collection keeps two layers separate:

1. **Owner-faithful questionnaire answer**
   - what the owner could honestly stand behind as the answer to the questionnaire

2. **Engineering / protocol expansion**
   - structured analysis, proof-layer logic, memorization policy, variant-difference handling, and red-team material derived from the case

These layers must not be blurred.

## Raw owner source artifacts

The `source_artifacts/` directory preserves:

- the full F6 user input exactly as supplied
- the raw owner reaction exactly as supplied

These artifacts are preserved as raw source, not normalized doctrine.

## What `source_basis` means

- `explicit_draft`: directly stated in the owner’s raw comments
- `inferred_from_prior_chat`: a disciplined inference from prior owner-stated goals and standards in this chat
- `model_expansion`: engineering expansion beyond direct owner wording; not owner truth

## What `owner_relation` means

- `owner_explicit`: directly owner-stated
- `owner_consistent_inference`: strongly consistent with the owner’s prior stated standards
- `model_only`: useful engineering expansion, but not owner truth

## File map

- `00_manifest.yaml` — bundle summary and counts
- `01_questionnaire_answer.md` — owner-faithful app-ready answer
- `02_case_dossier.md` — human engineering/protocol dossier
- `03_terms.yaml` — controlled vocabulary
- `04_decision_ladder.jsonl` — layered reasoning steps
- `05_focus_segments.jsonl` — what the owner focuses on in the text
- `06_slowdown_skip_analysis.jsonl` — what slows study down or gets reclassified
- `07_proof_layer_relationships.jsonl` — proof-source architecture
- `08_variant_difference_policy.jsonl` — variant-comparison policy
- `09_memorization_policy.jsonl` — what is or is not memorized directly
- `10_text_preservation_vs_study_structuring.jsonl` — what can be transformed and what must remain unchanged
- `11_data_analysis_opportunities.jsonl` — unprecedented analysis opportunities
- `12_nonnegotiables.jsonl` — machine-readable constraints
- `13_red_team_tests.jsonl` — adversarial tests
- `14_priority_matrix.yaml` — ranked issue landscape
- `15_traceability.jsonl` — routing from raw owner points to collection files
- `16_open_questions.jsonl` — remaining genuine gaps
- `17_hard_judgment.md` — blunt case judgment
