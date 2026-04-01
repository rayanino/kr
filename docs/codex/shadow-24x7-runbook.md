# Shadow 24x7 Runbook (Historical Pre-Cutover Reference)

This runbook records the pre-cutover shadow shape that proved the runtime before the early April 2, 2026 Codex cutover. Keep it as historical proof guidance; the live authority lane is defined by `ACTIVE_AUTHORITY.md`.

## Host

- Windows is the supervisory host and secondary interactive lane.
- The clean WSL clone at `/home/rayane/kr-canonical-unattended` is the current canonical unattended lane.
- `.venv` lives inside the WSL clone.
- The pre-cutover proof runs remained in `shadow_setup` and `queue_only`.

## Coworkers

Peer major coworkers for current control-plane work:

- `Claude Code`
- `Gemini CLI (Pro 3.1)`

## Scheduler Shape

Use repeated bounded runs, not one infinite process.

Recommended entrypoint:

- `powershell -ExecutionPolicy Bypass -File .\scripts\overnight_codex_wsl_resume.ps1 -RuntimeDir ~/kr-canonical-unattended -RunCycle -Hours 1.5`

Recommended overnight loop:

- `powershell -ExecutionPolicy Bypass -File .\scripts\run_overnight_codex_shadow_loop.ps1 -RuntimeDir ~/kr-canonical-unattended -TotalHours 8 -CycleHours 1.5 -IntervalMinutes 120`

Scheduler rules:

- every `2` hours
- do not start a new instance if the previous one is still running
- keep the orchestrator lockfile as the second line of defense

## Allowed Pre-Cutover Work

- read-only audits
- validation and regression checks
- doc freshness checks
- backlog shaping from runtime evidence
- backend-proof smoke runs

Not allowed:

- engine-code implementation in Claude-owned lanes
- auto-apply into engine paths
- protected-area edits

## Preflight

Before a bounded run, verify the runtime surface from both sides:

- Windows: `python scripts/check_codex_kr_setup.py`
- WSL: `cd /home/rayane/kr-canonical-unattended && .venv/bin/python scripts/check_codex_kr_setup.py --auth-preflight`

If setup audit fails, do not start another cycle until parity is fixed.

## Backend-Proof Routine

Run separately from the normal 2-hour cycle until the CLI path is proven stable:

- `bash scripts/run_codex_backend_proof_smoke.sh`

The proof path must begin with fast auth preflight for:

- `codex`
- `claude`
- `gemini`

## Current Sign-Off Status

The old `.codex/hooks` sync-mismatch failure is no longer the active blocker. Cycle 1 succeeding validated that fix.

The later shell-construction failure and the subsequent Windows-worktree bootstrap issue are both fixed on the reconciliation branch.

Observed branch-local proof:

- two consecutive bounded `-RunCycle` runs succeeded
- a short repeating-loop rehearsal via `scripts/run_overnight_codex_shadow_loop.ps1` also completed multiple successful `val-contracts` cycles on a clean mainline proof worktree when pointed at a fresh runtime dir

Treat the loop logic as proven on proof worktrees.

The final sign-off step for the landing path is one confirmation run from the chosen canonical unattended lane:

1. `scripts/run_overnight_codex_shadow_loop.ps1`
2. the clean WSL canonical lane at `/home/rayane/kr-canonical-unattended`

## Historical Cutover Readiness

The April 2, 2026 owner-approved cutover was supposed to stay blocked unless:

- Gate 0 from the canonical doctrine is fully green
- shadow runs are stable
- backend proof is green enough for the path Codex will own
