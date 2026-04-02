# Taysir Timeout Report

Status on 2026-04-02: `FAILED`, not `COMPLETE`.

## What happened

- `integration_tests/smoke_api_v2/SUMMARY.json` records `taysir.status = "error"`, `excerpt_count = 0`, `error_count = 1`, `time_seconds = 28800.96`, and `cost_estimate = 42.819313`.
- `integration_tests/smoke_api_v2/taysir/run_metadata.json` records the terminal error `batch_timeout: exceeded 28800s in batch runner` at `2026-04-01T16:18:30.624340+00:00`.
- `integration_tests/smoke_api_v2/taysir/excerpts.jsonl` does not exist.

## Last observed progress

- `progress.jsonl` contains 667 entries total.
- Phase counts:
  - `phase2a`: 180 `done`, 4 `failed`
  - `phase2b`: 179 `done`, 1 `failed`
  - `phase3_enrich`: 179 `done`
  - `phase3_consensus`: 124 `done`
- Last progress entry:

```json
{"chunk_id":"div_src_test0001_6_083","phase":"phase3_consensus","status":"done","timestamp":"2026-04-01T16:17:47.154918+00:00"}
```

## Active-write check

- Last raw request write observed in the Windows-origin artifact set: `raw_llm_requests/verify_0124.json` at `2026-04-01T16:17:47.163143Z`
- Last raw response write observed: `raw_llm_responses/verify_0123.json` at `2026-04-01T16:17:47.150808Z`

No later progress or raw-response writes were found after the timeout record.

## Impact

- Treat Task 1 as `FAILED`.
- Skip Tasks 2, 4, and 5 because the required `taysir` v2 output never materialized.
- Do not rerun or restart the smoke test from this handoff lane.

## Note on checkout state

The original `smoke_api_v2` artifacts were present in the Windows checkout at `C:\\Users\\Rayane\\Desktop\\kr` but missing from the WSL checkout at session start. On 2026-04-02, Codex mirrored only the safe non-raw, non-cache artifacts into the WSL checkout so the weekend audit and UI validation could proceed from the preferred WSL lane.
