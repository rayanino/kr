# SC3 collection bundle

This bundle preserves questionnaire-side material for **SC3**.

SC3 is an edge-case question about an excerpt that begins **mid-instruction**. The visible wording is partly readable, but the owner's reaction shows that local readability is not enough when identity, scope, and earlier dependencies are lost.

This is **not promoted doctrine**. It is a collection bundle that preserves two distinct layers:

1. **Owner-faithful questionnaire answer**
   - the strongest answer the owner could honestly stand behind for the questionnaire as asked

2. **Engineering / protocol expansion**
   - structured analysis of the deeper issues this case reveals:
     - mid-instruction dependency
     - explanation-identity loss
     - catastrophic scope reference
     - zero-precontext assumptions
     - copy-forward needs
     - missing pass/refuse validation gates

## Raw owner source artifacts

Two raw source artifacts are preserved:

- `source_artifacts/sc3_full_user_input_2026_04_04.txt`
  - full user prompt block, verbatim

- `source_artifacts/sc3_owner_raw_reaction_2026_04_04.txt`
  - raw owner reaction block, verbatim

These are preserved as source artifacts, not normalized doctrine.

## Meaning of metadata fields

- `source_basis`
  - `explicit_draft`: directly grounded in the owner’s raw wording
  - `inferred_from_prior_chat`: a conservative inference grounded in earlier established standards from this chat
  - `model_expansion`: broader engineering expansion not to be treated as owner truth

- `owner_relation`
  - `owner_explicit`: directly stated by the owner
  - `owner_consistent_inference`: strongly implied by the owner’s standards and wording
  - `model_only`: engineering-side expansion only

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — owner-faithful app-ready answer
- `02_case_dossier.md` — human-readable engineering / protocol analysis
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered reasoning steps
- `05_mid_instruction_dependencies.jsonl` — what the excerpt depends on from omitted earlier text
- `06_explanation_identity_loss.jsonl` — what identity is lost when the excerpt is detached
- `07_scope_reference_failures.jsonl` — catastrophic reference-scope failures
- `08_context_recovery_mechanisms.jsonl` — candidate recovery mechanisms
- `09_copy_forward_requirements.jsonl` — what later scope text may need to be copied forward
- `10_passage_analysis_gates.jsonl` — missing validation-gate ideas
- `11_zero_precontext_assumption.jsonl` — the owner’s zero-precontext rule
- `12_nonnegotiables.jsonl` — machine-readable must-not-violate constraints
- `13_red_team_tests.jsonl` — adversarial tests for this failure family
- `14_priority_matrix.yaml` — ranked issue landscape
- `15_traceability.jsonl` — proof that the raw answer was not flattened
- `16_open_questions.jsonl` — unresolved questions, if any
- `17_hard_judgment.md` — blunt owner-faithful and engineering judgment
