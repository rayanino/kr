# G4 collection bundle

This bundle preserves questionnaire-side collection material for **G4**.

It is **not promoted doctrine**. It is a structured preservation package for one questionnaire item so the owner-faithful answer and the engineering / protocol expansion remain clearly separated.

## What G4 is

G4 is a question about a continued set of conditions for cutting the thief's hand, where the excerpt explicitly says that some conditions were already mentioned earlier.

On the surface the question asks whether this block should stand on its own or be merged with earlier conditions.

At the deeper level, the case is about:

- condition-level excerpting
- continuation support
- short-and-harmless retention
- proximity-aware overlap
- continued-topic detection
- naming / vocabulary / machine-readable structure

## Two-layer separation

### Layer A — owner-faithful questionnaire answer
This is the answer the owner could honestly stand behind as the questionnaire response.

### Layer B — engineering / protocol expansion
This is the broader structured analysis extracted from the same case for future protocol / red-team / implementation use.

These layers must not be blurred together.

## Raw owner source artifacts

This collection preserves two raw source artifacts:

- `source_artifacts/g4_full_user_input_2026_04_04.txt`
- `source_artifacts/g4_owner_raw_reaction_2026_04_04.txt`

They are preserved verbatim and are not cleaned, normalized, or summarized.

## Meaning of source_basis

- `explicit_draft` — directly stated in the owner's raw comments or prompt
- `inferred_from_prior_chat` — strongly supported by earlier established owner positions in this chat
- `model_expansion` — engineering expansion beyond direct owner wording

## Meaning of owner_relation

- `owner_explicit` — directly owner-stated
- `owner_consistent_inference` — strongly consistent with the owner's established position
- `model_only` — engineering-layer content that should not be treated as direct owner truth

## File map

- `00_manifest.yaml` — bundle metadata and counts
- `01_questionnaire_answer.md` — owner-faithful app-ready answer
- `02_case_dossier.md` — human-readable engineering dossier
- `03_terms.yaml` — controlled vocabulary for this case
- `04_decision_ladder.jsonl` — layered reasoning steps
- `05_condition_excerpts.jsonl` — condition and subcondition excerpt candidates
- `06_context_carryover_analysis.jsonl` — carryover text analysis
- `07_short_harmless_rule.jsonl` — short-and-harmless logic
- `08_proximity_rules.jsonl` — branch-proximity logic
- `09_condition_branching_map.jsonl` — ideal branching structure
- `10_continued_topic_detection.jsonl` — continued-topic detection analysis
- `11_naming_vocabulary_pressures.jsonl` — naming and machine-readability pressure
- `12_nonnegotiables.jsonl` — machine-readable constraints
- `13_red_team_tests.jsonl` — adversarial tests
- `14_priority_matrix.yaml` — ranked issue landscape
- `15_traceability.jsonl` — raw-to-output routing proof
- `16_open_questions.jsonl` — genuine unresolved questions
- `17_hard_judgment.md` — blunt owner-faithful vs engineering judgment
