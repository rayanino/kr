# Shadow 24x7 Runbook

This runbook defines the pre-cutover shadow shape for KR Codex on the current Windows + WSL machine.

## Host

- Windows is the supervisory host and secondary interactive lane.
- WSL clone at `~/kr-codex` is the canonical unattended lane.
- `.venv` lives inside the WSL clone.
- Pre-cutover runs remain in `shadow_setup` and `queue_only`.

## Coworkers

Peer major coworkers for current control-plane work:

- `Claude Code`
- `Gemini CLI (Pro 3.1)`

## Scheduler Shape

Use repeated bounded runs, not one infinite process.

Recommended entrypoint:

- `powershell -ExecutionPolicy Bypass -File .\scripts\overnight_codex_wsl_resume.ps1 -RunCycle -Hours 1.5`

Recommended overnight loop:

- `powershell -ExecutionPolicy Bypass -File .\scripts\run_overnight_codex_shadow_loop.ps1 -TotalHours 8 -CycleHours 1.5 -IntervalMinutes 120`

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
- WSL: `cd ~/kr-codex && .venv/bin/python scripts/check_codex_kr_setup.py --auth-preflight`

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
- a short repeating-loop rehearsal via `scripts/run_overnight_codex_shadow_loop.ps1` also completed successful `val-contracts` cycles

Treat the loop logic as proven on the reconciliation branch.

Canonical readiness still requires rerunning the same proof from the intended checkout after these fixes are landed there:

1. `scripts/run_overnight_codex_shadow_loop.ps1`
2. the intended checkout, not just the reconciliation worktree

## Cutover Readiness

Do not switch authority on **April 9, 2026** unless:

- Gate 0 from the canonical doctrine is fully green
- shadow runs are stable
- backend proof is green enough for the path Codex will own
