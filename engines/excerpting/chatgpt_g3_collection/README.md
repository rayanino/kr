# G3 collection

This is a questionnaire-side collection bundle for **G3**. It is **not promoted doctrine** and it is **not canon/backfill work**. It preserves two layers separately:

1. **Owner-faithful questionnaire answer**
   - what the owner could honestly stand behind as the answer to the questionnaire

2. **Engineering / protocol expansion**
   - structured analysis of what this tiny numbered-point case reveals about excerpting, placement, reassurance, and methodology risk

## Raw owner source artifacts

This collection preserves two raw-source files:

- `source_artifacts/g3_full_user_input_2026_04_04.txt`
  - the full relevant question/excerpt/context/options/raw-comments input, preserved verbatim

- `source_artifacts/g3_owner_raw_reaction_2026_04_04.txt`
  - the owner raw comments only, preserved verbatim

These raw files are not cleaned, normalized, or converted into doctrine.

## `source_basis`

`source_basis` marks where a structured item came from:

- `explicit_draft` = directly grounded in the owner’s raw comments
- `inferred_from_prior_chat` = strong inference from already established owner standards in this chat
- `model_expansion` = additional engineering expansion that must not be mistaken for owner truth

## `owner_relation`

`owner_relation` marks how close an item is to the owner’s actual position:

- `owner_explicit` = explicitly stated by the owner
- `owner_consistent_inference` = not literally stated, but strongly consistent with prior owner material
- `model_only` = engineering expansion only

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — owner-faithful questionnaire answer only
- `02_case_dossier.md` — human-readable engineering/protocol analysis
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered reasoning chain
- `05_numbering_noncriterion_analysis.jsonl` — why numbering must not decide excerpting
- `06_point_identity_analysis.jsonl` — point-by-point excerpt-candidate analysis
- `07_function_multiplicity.jsonl` — multi-function behavior and placement pressure
- `08_candidate_packaging_patterns.jsonl` — packaging alternatives
- `09_context_reassurance_pressures.jsonl` — reassurance questions raised by numbered extraction
- `10_multi_leaf_placement.jsonl` — multiple legitimate placements when function multiplies
- `11_methodology_risk.jsonl` — broader methodology/adoption risk
- `12_nonnegotiables.jsonl` — machine-readable constraints
- `13_red_team_tests.jsonl` — adversarial tests
- `14_priority_matrix.yaml` — ranked issue landscape
- `15_traceability.jsonl` — source-to-output routing proof
- `16_open_questions.jsonl` — unresolved items, if any
- `17_hard_judgment.md` — blunt final assessment
