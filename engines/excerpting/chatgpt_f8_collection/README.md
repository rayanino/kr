# F8 collection bundle

This collection preserves the F8 questionnaire work as **collection material**, not promoted doctrine.

## What F8 is

F8 asks which failure feels more dangerous when comparing:
- premature structure
- structurelessness
- or neither extreme because the real issue is where guidance should and should not be used

The owner's answer is not flat. It is hierarchical:
1. the most dangerous overall failure is excerpt corruption / knowledge corruption
2. excerpting must not be biased by the taxonomy tree
3. rightful excerpt output should stay invariant under tree granulation changes
4. only after excerpting is held correct and independent do placement failures get compared
5. within that narrower comparison, overgranulation is more dangerous than undergranulation
6. therefore the questionnaire choice is `C`, not because both extremes are equal, but because guidance boundaries are the real issue

## Why this is a collection bundle, not promoted doctrine

This bundle captures:
- the owner-faithful questionnaire answer
- a structured engineering / adversarial expansion
- the raw owner draft artifact

It does **not** promote these materials into the F1 canon or any broader doctrine system.

## Two-layer separation

### 1. Owner-faithful questionnaire answer
This is the answer the owner could honestly stand behind in the questionnaire.

### 2. Engineering / adversarial expansion
This layer expands the comparison into machine-readable decision ladders, guidance boundaries, failure families, scenarios, thresholds, nonnegotiables, and red-team tests.

These layers must not be blurred together.

## Raw owner source artifact

`source_artifacts/f8_owner_raw_draft_2026_04_04.txt` preserves the rough owner wording verbatim as a source artifact. It is not cleaned, normalized, or converted into doctrine there.

## Meaning of `source_basis`

- `explicit_draft`: directly grounded in the owner's rough draft for F8
- `inferred_from_prior_chat`: not stated verbatim in the raw F8 draft, but strongly implied by prior established goals and thresholds in this chat
- `model_expansion`: broader comparative/adversarial expansion added by the model for engineering use

## Meaning of `owner_relation`

- `owner_explicit`: directly stated by the owner
- `owner_consistent_inference`: not stated verbatim here, but consistent with the owner's prior established position
- `model_only`: model-generated expansion that must not be treated as owner truth without later confirmation

## File map

- `README.md` — this overview
- `source_artifacts/f8_owner_raw_draft_2026_04_04.txt` — verbatim owner raw draft
- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — owner-faithful app-ready answer
- `02_assessment_dossier.md` — human engineering/red-team assessment artifact
- `03_terms.yaml` — controlled vocabulary for this question
- `04_decision_ladder.jsonl` — hierarchical reasoning without flattening
- `05_guidance_boundaries.jsonl` — where guidance may and must not operate
- `06_failure_taxonomy.jsonl` — normalized failure families
- `07_scenarios.jsonl` — concrete scenarios
- `08_thresholds.jsonl` — owner reaction thresholds
- `09_nonnegotiables.jsonl` — machine-readable constraints
- `10_red_team_tests.jsonl` — adversarial tests
- `11_priority_matrix.yaml` — ranked risk surface
- `12_traceability.jsonl` — routing from owner source points into collection outputs
- `13_open_questions.jsonl` — genuine remaining questions only
- `14_hard_judgment.md` — blunt final judgment
