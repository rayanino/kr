# Taysir Timeout Analysis — 2026-04-02

## Verdict

The strongest current explanation is:

- the weekend `taysir` run was still inside `phase3_consensus`
- chunk `div_src_test0001_6_083` was the last chunk to complete consensus
- the next verifier call (`verify_0124`) was sent but never produced a persisted response
- the parent batch runner hit the 8-hour package timeout and killed the child process before it reached final output writing

## Evidence

1. `integration_tests/smoke_api_v2/SUMMARY.json`
   - `taysir.status = "error"`
   - `excerpt_count = 0`
   - `error_count = 1`
   - `errors = ["batch_timeout: exceeded 28800s in batch runner"]`

2. `integration_tests/smoke_api_v2/taysir/run_metadata.json`
   - records the same timeout marker
   - does not have the normal rich runner metadata written by `run_integration_test.py`

3. `integration_tests/smoke_api_v2/taysir/progress.jsonl`
   - `phase2a`: 180 `done`, 4 `failed`
   - `phase2b`: 179 `done`, 1 `failed`
   - `phase3_enrich`: 179 `done`
   - `phase3_consensus`: 124 `done`
   - last entry: `div_src_test0001_6_083` at `2026-04-01T16:17:47.154918+00:00`

4. Windows-origin raw trace artifacts from the same run
   - requests: `verify_0124.json` exists
   - responses stop at `verify_0123.json`
   - there is no `verify_0124.json` response and no `verify_0124_error.json`

5. Missing final runner artifacts
   - no `integration_tests/smoke_api_v2/taysir/excerpts.jsonl`
   - no `integration_tests/smoke_api_v2/taysir/processing_log.jsonl`
   - no `integration_tests/smoke_api_v2/taysir/timing.json`

## Likely Control Flow

1. `scripts/run_full_integration.py` launched `scripts/run_integration_test.py` as a child process with `timeout=28800`.
2. The child advanced through Phase 1, Phase 2a, Phase 2b, and part of Phase 3.
3. During Phase 3 consensus, the child logged the final completed chunk to `progress.jsonl`.
4. The next external verifier request was issued (`verify_0124`) and then never completed on disk.
5. The parent timeout fired, killed the child process, and wrote the timeout marker into `run_metadata.json`.
6. Because the child never reached the final output-writing block, the partial excerpts already completed in memory were never flushed to `excerpts.jsonl`.

## What This Means

- The run did not fail in summary writing or post-processing.
- It failed upstream, while waiting on an in-flight verification call.
- The available artifacts do not prove whether the missing response was caused by provider stall, transport stall, or the process being killed mid-wait. They do prove that no response landed on disk before termination.

## Improvements Landed On 2026-04-02

1. `scripts/run_full_integration.py`
   - now writes `STALL_REPORT.md` automatically on future package timeouts

2. `scripts/run_integration_test.py`
   - now writes `last_llm_activity.json` from the request/response/error hook layer

3. `scripts/run_full_integration.py`
   - timeout reports now include `last_llm_activity.json` when available

These changes will make the next timeout materially easier to diagnose.

## Next Useful Steps

1. Preserve and inspect the exact `verify_0124` request payload against the target chunk and unit count.
2. If another long run is attempted in the future, prefer graceful interruption before hard kill so partial outputs can land.
3. Keep treating `taysir` as blocked for review/comparison until a valid `excerpts.jsonl` exists.
