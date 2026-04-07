# D3 collection

This collection preserves questionnaire-side material for **D3 — A Multi-Layered Definition**.

It is a **collection bundle**, not promoted doctrine.

## Two-layer separation

Layer A is the **owner-faithful questionnaire answer**.
Layer B is the **engineering / protocol expansion** that extracts deeper structural implications from the same case.

These layers are intentionally kept separate. The owner answer is conservative and owner-faithful. The engineering layer is broader, but every nontrivial item is tagged with:

- `source_basis`
- `owner_relation`

## Raw source artifacts

This bundle preserves two raw artifacts:

- `source_artifacts/d3_full_user_input_2026_04_07.txt`
- `source_artifacts/d3_owner_raw_reaction_2026_04_07.txt`

These are preserved as raw owner-source materials and are not normalized into doctrine inside those files.

## What `source_basis` means

- `explicit_draft`: explicitly stated in the owner raw reaction or prompt text
- `inferred_from_prior_chat`: strong consequence of earlier established owner principles in this chat
- `model_expansion`: engineering-level expansion that is **not** owner truth by default

## What `owner_relation` means

- `owner_explicit`: directly stated by the owner
- `owner_consistent_inference`: strongly implied by the owner’s established standards
- `model_only`: engineering expansion only

## File map

- `01_questionnaire_answer.md` — owner-faithful answer
- `02_case_dossier.md` — disciplined case analysis
- `03_terms.yaml` — load-bearing vocabulary for this case
- `04_decision_ladder.jsonl` — atomic reasoning steps
- `05_hypothetical_definition_layers.jsonl` — the forced menu analyzed on its own terms
- `06_current_excerpt_function_layers.jsonl` — what the current excerpt actually contains
- `07_school_specific_branching.jsonl` — school-specific meaning handling
- `08_short_harmless_carryover.jsonl` — packaging exception logic
- `09_attribution_and_proof_coupling.jsonl` — coupled layers and when they may travel together
- `10_leaf_pollution_and_significance.jsonl` — mention vs excerpt-worthy unit pressure
- `11_source_hints_and_nondeciding_signals.jsonl` — useful-but-nondeciding source cues
- `12_security_and_verification_gates.jsonl` — pre-excerpt analysis and verification pressure
- `13_nonnegotiables.jsonl` — hard constraints
- `14_red_team_tests.jsonl` — adversarial tests
- `15_priority_matrix.yaml` — seriousness ranking
- `16_traceability.jsonl` — no-loss routing map
- `17_open_questions.jsonl` — real unresolved edges only
- `18_hard_judgment.md` — blunt concluding judgment
