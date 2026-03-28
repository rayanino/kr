# NEXT — Harden Overnight Sprint System for Unmonitored Operation

## Context

The overnight sprint system (`scripts/weekend_parallel.py` + `scripts/overnight_orchestrator.py`) ran on 2026-03-28 and completed 24/27 readonly tasks but **zero** write tasks. The write orchestrator circuit-breaker triggered after 3 consecutive test-generation timeouts, killing 48 queued tasks. Full diagnosis: `overnight/DIAGNOSIS.md`.

**Goal:** Make this system trustworthy enough to run 8-20 hours completely unmonitored — sleep, leave the house, come back to useful work done.

## Architecture Files (read these first)

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/weekend_parallel.py` | 519 | Parallel coordinator — 3 readonly workers + write orchestrator subprocess |
| `scripts/overnight_orchestrator.py` | 1689 | Sequential write task executor with quality gates, circuit breaker, dependency DAG |
| `scripts/overnight_task_generator.py` | 878 | 9 scanners that discover hardening tasks from codebase state |
| `scripts/sprint_dashboard.py` | 175 | Real-time monitoring dashboard |
| `overnight/sprint_manifest.json` | — | Task definitions for the sprint |
| `overnight/weekend_state.json` | — | Readonly pool state (last run results) |
| `overnight/DIAGNOSIS.md` | — | Detailed failure analysis from 2026-03-28 run |

## What to Fix (ordered by impact)

### FIX-1: Smart Circuit Breaker (CRITICAL)

**Problem:** Circuit breaker treats all failures equally. 3 test-generation timeouts (same root cause — task too complex for sonnet) killed 48 unrelated tasks.

**Fix:** Categorize failures and use per-category breakers:
- `timeout` — task ran out of time (may have partial output)
- `crash` — subprocess died unexpectedly
- `quality_gate` — task completed but failed quality checks
- `max_turns` — hit conversation turn limit

Only `crash` failures should count toward the hard circuit breaker. Timeouts get a softer limit (e.g., 5 consecutive timeouts before pausing that task category). Quality gate failures already don't trigger the breaker (existing behavior).

**Where:** `overnight_orchestrator.py` lines ~924-999 (circuit breaker logic in main loop)

### FIX-2: Write Orchestrator Health Monitoring (CRITICAL)

**Problem:** `weekend_parallel.py` launches the write orchestrator as fire-and-forget `Popen` (line 315-327), then only checks it at the very end via `communicate()` (line 464). If the write orchestrator dies in minute 5, the parent doesn't know until hour 20.

**Fix:** Monitor write orchestrator health from the parent:
- Poll `overnight/state.json` or write orchestrator heartbeat every 60 seconds
- If write orchestrator process has exited, log it immediately and report in dashboard
- If write orchestrator has been idle (no state change) for 2x the current task's timeout, treat as stalled
- Dashboard should show write orchestrator status: `running|stalled|dead|completed`

**Where:** `weekend_parallel.py` lines 400-472 (write orchestrator lifecycle)

### FIX-3: Task Ordering — Easy Wins First (HIGH)

**Problem:** First 3 tasks in the write queue were the hardest (12-15 test cases each). All timed out, triggering circuit breaker before any easier task could succeed.

**Fix:** Sort write tasks by estimated complexity, not just priority:
- Simpler tasks first (fewer tests, shorter prompts, script tasks before test tasks)
- Mix task types — don't cluster all test-generation tasks together
- Add `estimated_complexity: "low"|"medium"|"high"` to TaskDef
- Sort: low-complexity first, then medium, then high — within each priority band

**Where:** `weekend_parallel.py` `split_tasks()` (line 308) and task sorting (line 385)

### FIX-4: Crash Resume (HIGH)

**Problem:** If the parent process is killed (Ctrl+C, terminal close, system restart), all in-flight work is lost and there's no way to resume.

**Fix:** Implement resume from last known state:
- On startup, check if `weekend_state.json` exists with `status != "completed"`
- If so, load it, skip already-completed tasks, resume from the next pending task
- Add `--resume` flag to the CLI
- Each task's result is already persisted to `overnight/results/{task_id}/result.json` — use these as source of truth for what's done

**Where:** `weekend_parallel.py` `run_parallel()` (line 330) — add resume logic before task scheduling

### FIX-5: Partial Success Detection (MEDIUM)

**Problem:** Tasks that produce 90% of their output but timeout are counted as total failures. The core-extract tasks wrote 22K of useful analysis but were marked "timeout."

**Fix:** After a timeout, check if the task produced meaningful output:
- If `findings.json` or `findings.md` exists in the results dir AND has content > 1KB, mark as `partial_success`
- Partial success does NOT count toward circuit breaker
- Morning report flags these for human review: "Task X timed out but produced findings — review results/"

**Where:** `weekend_parallel.py` `execute_readonly_task()` (line 230, timeout handler) and `overnight_orchestrator.py` timeout handler

### FIX-6: Unified Heartbeat (MEDIUM)

**Problem:** Heartbeat is written only by the write orchestrator. The readonly pool writes to a different state file. Monitoring tools see stale heartbeat data.

**Fix:** Single heartbeat file updated by both:
- Readonly pool: update heartbeat after each task completion with `readonly_completed`, `readonly_active` counts
- Write orchestrator: update heartbeat with `write_completed`, `write_active` counts
- Use file locking or atomic writes to avoid corruption
- Dashboard reads one file to get full picture

**Where:** `weekend_parallel.py` (add heartbeat writes after line 444) and `overnight_orchestrator.py` `_write_heartbeat()` (line ~543)

### FIX-7: Adaptive Timeouts for Write Tasks (MEDIUM)

**Problem:** Test-generation tasks got 20-25 minute timeouts with `sonnet` model. These are insufficient for generating 500+ lines of test code.

**Fix:** Scale timeout with task complexity:
- If `estimated_complexity == "high"`: timeout *= 1.5, use `opus` model
- If `estimated_complexity == "low"`: use shorter timeout, `sonnet` is fine
- After a timeout on a specific task TYPE (e.g., `sprint_test`), automatically increase timeout for remaining tasks of that type by 50%
- Cap at 45 minutes per task (anything longer should be split)

**Where:** `overnight_orchestrator.py` task execution section (~line 700) and `weekend_parallel.py` `execute_readonly_task()` (line 217)

### FIX-8: Dashboard Shows Write Orchestrator Status (LOW)

**Problem:** Dashboard only shows readonly pool progress. Write orchestrator status is invisible.

**Fix:** `sprint_dashboard.py` should also:
- Read write orchestrator `state.json` for write task progress
- Show write orchestrator process status (running/dead/completed)
- Show last write task attempted and its result

**Where:** `scripts/sprint_dashboard.py` (line ~175)

## Scope Guard

- Do NOT rewrite the overnight system from scratch — improve what exists
- Do NOT add new task types or scanners
- Do NOT change the quality gate levels (L1-L6)
- Do NOT modify the manifest format (keep backwards compatible)
- Do NOT add external dependencies (no Redis, no SQLite, no message queues)
- Keep changes within `scripts/weekend_parallel.py`, `scripts/overnight_orchestrator.py`, `scripts/sprint_dashboard.py`
- Test manually with `--dry-run` and single-task mode (`--task`) before full runs

## Verification

After changes:
1. `python scripts/weekend_parallel.py --manifest overnight/sprint_manifest.json --dry-run` — should list all tasks with new ordering
2. `python scripts/weekend_parallel.py --manifest overnight/sprint_manifest.json --task audit-stale-artifacts` — single task should complete successfully
3. Create a test manifest with 1 task that will timeout (set timeout_minutes: 1) — verify partial success detection works
4. Kill the process mid-run, restart with `--resume` — verify it picks up where it left off

## After Completing Fixes

Commit with: `fix(overnight): harden sprint system — smart breaker, resume, health monitoring`

Then launch a fresh overnight run to validate everything works unmonitored.
