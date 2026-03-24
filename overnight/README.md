# KR Overnight Autonomous System v2

The overnight system runs quality improvement tasks while no human is present. Each task gets a fresh 1M-token context via separate `claude -p` invocations. The system focuses exclusively on **hardening** — code review, edge case tests, bug fixes, spec audits, validation — never feature implementation.

## Architecture

```
overnight_task_generator.py  →  manifest.json  →  overnight_orchestrator.py
        (9 scanners)              (task DAG)         (execute → quality gate → report)
                                                           ↓
                                                    MORNING_REPORT.md
```

1. **Task Generator** scans repo state, produces a prioritized manifest with dependencies
2. **Orchestrator** executes tasks sequentially, runs quality gates after each, tracks state
3. **Quality Gate** (5 levels): L1 tests, L2 git state, L3 compliance, L4 pyright, L5 Codex
4. **Recycling**: when all tasks finish but time remains (>30 min), generator runs again
5. **Bookend tasks**: `bookend=true` tasks (e.g., regression test) always run last regardless of failures

## Key Files

| File | Purpose |
|------|---------|
| `scripts/overnight_orchestrator.py` | Main loop, quality gate, state persistence, morning report |
| `scripts/overnight_task_generator.py` | 9 scanners that discover hardening work |
| `scripts/start_overnight.sh` | Bash launcher with pre-flight checks |
| `overnight/manifest.json` | Current task definitions (input to orchestrator) |
| `overnight/state.json` | Persistent execution state (tasks completed, costs, results) |
| `overnight/progress.md` | Human-readable task checklist |
| `overnight/decisions.log` | Append-only log of autonomous decisions |
| `overnight/MORNING_REPORT.md` | Auto-generated summary for morning review |
| `overnight/.heartbeat` | PID + status, updated after each task |
| `overnight/results/<task_id>/` | Per-task outputs (result.json, summary.md, review.md) |

## Philosophy: Hardening Only

The safety prompt explicitly forbids:
- Implementing new features, modules, or capabilities
- Creating new source files under `engines/*/src/`
- Any work categorized as `implementation`, `integration`, or `research`

Allowed work: `review`, `test`, `validation`, `spec`, `doc`, `code_quality`, `verification`.

## How to Launch

```powershell
# Generate a fresh manifest (optional — orchestrator can also auto-generate)
python scripts/overnight_task_generator.py --output overnight/manifest.json

# Review the plan
python scripts/overnight_orchestrator.py --manifest overnight/manifest.json --dry-run

# Launch
$env:KR_OVERNIGHT=1; $env:PYTHONIOENCODING="utf-8"; python scripts/overnight_orchestrator.py --manifest overnight/manifest.json --hours 8.5
```

## How to Review Results (Morning)

1. **Read `overnight/MORNING_REPORT.md`** — summary with costs, task statuses, issues, review pointers
2. **Check `overnight/decisions.log`** — every autonomous decision with timestamps
3. **Read review outputs** — `overnight/results/<task_id>/review.md` for code review findings
4. **Check `overnight/state.json`** — detailed per-task results with durations and costs
5. **Run `git log --oneline -20`** — overnight commits have prefix `overnight: `
6. **Run full test suite** — `python -m pytest engines/excerpting/tests/ -v --tb=short`

## Known Limitations

- **Codex L5 gate disabled on Windows** — `codex` CLI not on PATH. Pre-flight detects this and sets `KR_SKIP_CODEX=1`. No action needed.
- **Code quality scanner fragile** — sometimes fails with `'NoneType' object has no attribute 'strip'` when grep returns None. Non-blocking.
- **Dry-run print encoding** — `→` character in dependency display can't encode in cp1252 on Windows console. Use `PYTHONIOENCODING=utf-8`.
- **Old state.json shows $0 cost** — cost tracking was broken before 2026-03-24 (read `cost_usd` instead of `total_cost_usd`). Fixed now.

## Recent Changes (2026-03-24)

**Bugs fixed:**
1. Cost tracking: `cost_usd` → `total_cost_usd` (Claude Code CLI field name)
2. State initialization: stale cleanup now runs BEFORE new state write (was after — race condition)
3. Transitive skip propagation: `"skipped"` now propagates through dependency chains (was 1-level only)
4. max_turns truncation: `error_max_turns` subtype detected and logged in decisions.log

**Features added:**
5. Bookend tasks: `bookend=true` field — tasks that always run last regardless of failures
6. Hardening-only safety prompt: explicit rules forbidding feature implementation
7. Task recycling: when all tasks finish, generator re-runs to discover new work
8. Codex pre-check: `shutil.which("codex")` in preflight, single log message instead of per-task errors
9. Enhanced morning report: actual costs, per-task breakdown, "Review First" section
10. Knowledge integrity scanner: probes T-1 (attribution) and T-3 (text corruption) in excerpting engine
11. Recent changes scanner: auto-reviews files modified in last 24h

## Manifest Format

```json
{
  "task_id": "unique-slug",
  "name": "human readable",
  "category": "review|test|validation|spec|doc|code_quality|verification",
  "prompt": "full task instructions",
  "safety_level": "readonly|additive|modifying",
  "execution_mode": "cli|codex|sdk",
  "model": "opus|sonnet",
  "timeout_minutes": 30,
  "max_turns": 30,
  "priority": 1-99,
  "depends_on": ["other-task-id"],
  "bookend": false,
  "allowed_tools": ["Read", "Bash", "..."],
  "permission_mode": "bypassPermissions"
}
```

- **bookend** — If `true`, task skips dependency propagation and runs after ALL non-bookend tasks resolve. Use for regression tests that must always execute.
- **priority** — Lower = earlier. Bookend tasks typically use 99.
- **safety_level** — `readonly` tasks skip quality gate. `modifying` tasks get L1-L5 gate + git rollback on failure.
- **category** — Must be in allowed set. `implementation`/`research` are rejected by the task generator.

## Task Generator Scanners (9)

| # | Scanner | What it finds | Priority |
|---|---------|---------------|----------|
| 1 | Knowledge Integrity | T-1 attribution + T-3 text corruption probes | 1 |
| 2 | Recent Changes | Code review + hardening for files modified <24h | 1-2 |
| 3 | Test Health | Coverage gaps per engine | 4 |
| 4 | SPEC Quality | SPEC defects (ambiguity, missing examples) | 5 |
| 5 | Code Quality | Arabic-unsafe patterns, bare except, missing hints | 6 |
| 6 | Corpus Integrity | Stale normalization sweep (>1 week) | 2 |
| 7 | Contract Boundaries | D-023 metadata flow, cross-engine contracts | 3 |
| 8 | Known Limitations | Stale calibration data in KNOWN_LIMITATIONS.md | 7 |
| 9 | Documentation | NEXT.md/CLAUDE.md freshness check | 7 |
