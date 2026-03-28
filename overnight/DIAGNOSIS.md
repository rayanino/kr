# Overnight Sprint System — Failure Diagnosis (2026-03-28)

## Run Summary

| Metric | Value |
|--------|-------|
| Started | 2026-03-28 19:16 UTC |
| Duration | ~2.7 hours |
| Readonly tasks | 24/27 succeeded (88.9%) |
| Write tasks | 0/51 executed |
| Circuit breakers | 1 (write orchestrator) |

## CRITICAL: Write Orchestrator Produced Zero Output

**Root cause chain:**

1. `weekend_parallel.py` launches write orchestrator as background `subprocess.Popen` (line 323)
2. Write orchestrator (`overnight_orchestrator.py`) loads 51 tasks from `sprint_write_manifest.json`
3. First 3 tasks were ALL test-generation tasks (priority 2): `test-consensus-edge-cases` (25m), `test-scholar-name-edge` (20m), `test-validation-passthrough` (20m)
4. All 3 timed out — CLI mode + sonnet model + 12-15 test cases per task = too slow
5. Circuit breaker triggered (3 consecutive failures) -> orchestrator stopped
6. 48 remaining write tasks never executed

**Why the tasks timed out:**
- Task complexity: each required generating 500+ lines of test code with real Arabic fixtures
- Model: `sonnet` (cheaper but slower for code generation)
- Timeout: 20-25 minutes — insufficient for large test scaffolding via CLI mode
- Max turns: 25-30 — may have hit turn limit before timeout

**Why circuit breaker was wrong here:**
- These were NOT systemic failures — they were 3 similar tasks that share the same bottleneck
- The remaining 48 tasks include simpler operations that would likely succeed
- Circuit breaker treats all failures equally — no distinction between timeout vs crash vs bad output

## MEDIUM: 3 Readonly Timeouts

| Task | Allocated | Actual | Output? |
|------|-----------|--------|---------|
| core-extract-taxonomy | 25m | 25m | Yes — 22K CORE_EXTRACTION.md + findings |
| core-extract-synthesis | 25m | 25m | Yes — 23K CORE_EXTRACTION.md + findings |
| bughunt-exc-phase3-validation | 30m | 30m | Only result.json stub |

**Key insight:** The first two tasks DID produce useful output but were killed by the wall-clock timeout. They were ~90% complete. The system has no concept of "partial success."

## LOW: State Tracking Desync

- Heartbeat at investigation time showed: `tasks_completed: 0, tasks_remaining: 48`
- Actual state: 24 readonly completed
- Cause: heartbeat is written by the write orchestrator only, not the readonly pool
- The weekend_state.json (written by readonly pool) was accurate

## LOW: Lock File Disappeared

- `.overnight.lock` was missing when checked at ~7:12 PM
- Sprint continued running despite missing lock
- Cause: write orchestrator released its lock when circuit breaker stopped it
- Readonly pool has no lock mechanism of its own

## Failure Mode Classification

| Mode | Count | Impact | Current Handling |
|------|-------|--------|-----------------|
| Task timeout (readonly) | 3 | Lost analysis time | Mark failed, continue |
| Task timeout (write) | 3 | Triggered circuit breaker | Mark failed, count toward breaker |
| Circuit breaker | 1 | Killed all remaining write work | Stop orchestrator |
| Write orchestrator death | 1 | Zero write output | Silent — parent just waits |
| Heartbeat desync | 1 | Misleading monitoring | No detection |
| Lock file loss | 1 | No concurrent-run protection | No detection |

## What Worked Well

1. Readonly parallel pool (3 workers) — efficient, 24 tasks in 2.7h
2. Task isolation — each task in its own results directory
3. Atomic state writes — weekend_state.json stayed consistent
4. Output preservation — even timed-out tasks preserved partial results
5. Contract-sync-audit found 10 real cross-engine mismatches
6. Bug hunts found actionable bugs (5 in writer.py alone)
