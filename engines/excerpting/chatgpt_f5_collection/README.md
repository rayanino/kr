# F5 collection bundle

This bundle preserves questionnaire-side collection material for **F5 — An Excerpt With a Summary Note**.

It is **not promoted doctrine**. It is a layered preservation bundle for one high-stakes questionnaire item.

## Why this bundle exists

F5 looks like a simple note-visibility question, but the owner reaction makes the deeper issue structural:

- the explanation was separated from what it explains
- the note helps only because that deeper split already happened
- source-preserving context may be preferable to a generated summary note
- proof integrity, version sensitivity, grading sensitivity, and unseen scholar methodologies all matter here

## Two-layer separation

### Layer A — owner-faithful questionnaire answer
This is the answer the owner could honestly stand behind for the pair as currently given.

### Layer B — engineering / protocol expansion
This is the broader machine-readable analysis of why the pair is structurally suspicious, what the note is compensating for, and what deeper safeguards the pipeline needs.

These two layers must **not** be blurred together.

## Raw owner source artifacts

- `source_artifacts/f5_full_user_input_2026_04_04.txt` preserves the full question block, note block, excerpt block, option block, and raw comments verbatim.
- `source_artifacts/f5_owner_raw_reaction_2026_04_04.txt` preserves the raw owner comments verbatim.

These artifacts are raw sources, not normalized doctrine.

## Source metadata fields

### `source_basis`
Where an item comes from:
- `explicit_draft`
- `inferred_from_prior_chat`
- `model_expansion`

### `owner_relation`
How closely the item relates to owner truth:
- `owner_explicit`
- `owner_consistent_inference`
- `model_only`

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — app-ready owner answer only
- `02_case_dossier.md` — human engineering/protocol artifact
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered reasoning steps
- `05_note_necessity_analysis.jsonl` — direct analysis of note necessity and visibility
- `06_candidate_context_blocks.jsonl` — alternative context block candidates
- `07_explained_explanation_analysis.jsonl` — core explained/explanation structural issue
- `08_proof_integrity_layers.jsonl` — proof-source layering analysis
- `09_methodology_risk.jsonl` — variability and uncertainty-gate pressures
- `10_nonnegotiables.jsonl` — machine-readable constraints
- `11_red_team_tests.jsonl` — adversarial tests for this case
- `12_priority_matrix.yaml` — prioritized issue landscape
- `13_traceability.jsonl` — routing from raw owner points to bundle artifacts
- `14_open_questions.jsonl` — genuine unresolved questions only
- `15_hard_judgment.md` — blunt owner vs engineering judgment
