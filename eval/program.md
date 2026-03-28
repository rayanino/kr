## Objective

Improve KR pipeline LLM call quality: reduce JSON retry rate, reduce
consensus disagreement rate, improve clean success rate.  Focus on
non-content prompt improvements (schema directives, formatting
instructions) — NEVER modify content classification prompts.

## Agent Run Command

python scripts/run_pipeline.py --fixture tests/fixtures/01_nahw_simple --traces eval/traces

## Traces Directory

eval/traces

## Metrics

- clean_success_rate: maximize (weight: 2.0)
- json_retry_rate: minimize (weight: 1.5)
- consensus_disagreement_rate: minimize (weight: 1.0)
- arabic_encoding_error_rate: minimize (weight: 3.0)
- error_rate: minimize (weight: 1.0)
- validation_retry_rate: minimize (weight: 1.0)

## Custom Evaluations

eval/compute_baselines.py

## Stopping Conditions

- max_iterations: 5
- max_duration_hours: 4
- plateau_patience: 2

## Time Budget

- minutes_per_iteration: 20

## Constraints

- NEVER modify prompts in engines/*/prompts/ that affect genre, author,
  science scope, school attribution, or any content classification
- NEVER modify Arabic text handling or encoding logic
- Changes limited to: JSON schema directives, error recovery instructions,
  output format specifications, retry augmentation text
- All changes must pass through human gate review before acceptance
