# Taysir Timeout Repair Map — 2026-04-02

Goal: identify the first runtime and engine-adjacent symbols to open for the
`taysir` long-run timeout / incomplete-finalization lane, without assuming the
problem is only “the model was slow.”

## Highest-Probability Loci

### 1. `scripts/run_full_integration.py`

Primary symbols:

- `_run_package_subprocess(...)`
- `_terminate_process_tree(...)`
- `_persist_resume_marker(...)`
- `_write_timeout_report(...)`
- `_run_single_package(...)`

Why this is first:

- this is the parent process that actually enforced the `28800s` timeout
- it is the only place that can explain why the child was killed before final
  excerpt writing
- it now owns the post-timeout truth artifacts (`run_metadata.json`,
  `STALL_REPORT.md`, trace-health summaries)

What to inspect first:

- whether the 8-hour timeout is still the right package-level budget
- whether the graceful interrupt-first path lands useful partial artifacts on
  real long-running package processes, not just the synthetic harness
- whether timeout reports should record more child-state context before kill

## 2. `scripts/run_integration_test.py`

Primary symbols:

- `make_hook_logger(...)`
- `_persist_failure_artifacts(...)`
- the `KeyboardInterrupt` handling paths around phase3 and output writing

Why this is second:

- this is where partial artifacts can still be salvaged if the child is
  interrupted instead of hard-killed
- it is also where the new `last_llm_activity.json` telemetry now lives

What to inspect first:

- whether a real long-running verification wait exits through the
  `KeyboardInterrupt` handlers cleanly
- whether `processing_log.jsonl`, `timing.json`, and partial outputs can land
  before parent shutdown on large packages

## 3. `engines/excerpting/src/phase3_consensus.py`

Primary symbols:

- `verify_chunk(...)`
- `run_consensus(...)`

Why this is third:

- the last concrete artifact before collapse is the missing verifier response
  `verify_0124`
- the child reached deep into this stage before the timeout boundary won

What to inspect first:

- whether there is any retry/escalation/skip behavior on slow or abnormal
  verifier responses that could preserve more progress
- whether metadata-only anomalies like `finish_reason = null` are harmless or
  should become explicit warning signals

## 4. Timeout-Tail Evidence To Open First

1. `docs/codex/taysir_timeout_analysis_2026_04_02.md`
2. `docs/codex/taysir_verify_tail_analysis_2026_04_02.md`
3. `integration_tests/smoke_api_v2/taysir/STALL_REPORT.md`
4. `integration_tests/smoke_api_v2/taysir/progress.jsonl`
5. `integration_tests/smoke_api_v2/taysir/run_metadata.json`
6. `integration_tests/smoke_api_v2/taysir/analysis/book_summary.md`

## Working Hypothesis

The strongest current reading is:

- the child was still alive inside `phase3_consensus`
- `verify_0124` was the next in-flight verifier call
- the parent timeout killed the child before a response artifact or final
  write-out could land

So the next serious session should start from the runtime/consensus boundary,
not from writer code.
