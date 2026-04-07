# Shadow 24x7 Runbook

This runbook defines the pre-cutover shadow shape for KR Codex from the intended Windows checkout.

## Host

- The current Windows checkout is the canonical Codex lane for interactive work and queue-only shadow runs.
- Use the repo-local `.venv` when present.
- Pre-cutover runs remain in `shadow_setup` and `queue_only`.
- Legacy WSL tooling is fallback-only and should stay out of the default path.

## Coworkers

Peer major coworkers for current control-plane work:

- `Claude Code`
- `Gemini CLI (Pro 3.1)`

## Scheduler Shape

Use repeated bounded runs, not one infinite process.

Recommended preflight:

- `powershell -ExecutionPolicy Bypass -File .\scripts\start_codex_kr.ps1 -Profile kr_shadow -RunAuthPreflight -NoLaunch`

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

Before a bounded run, verify the runtime surface from the current checkout:

- `python scripts/check_codex_kr_setup.py --auth-preflight`

If setup or auth preflight fails, do not start another cycle until the checkout is healthy again.

## Backend-Proof Routine

Run separately from the normal 2-hour cycle until the CLI path is proven stable:

- `bash scripts/run_codex_backend_proof_smoke.sh`

The proof path must begin with fast auth preflight for:

- `codex`
- `claude`
- `gemini`

## Current Sign-Off Status

- Windows auth preflight is green for `codex`, `claude`, and `gemini`.
- The queue-only Windows shadow loop now lives in the intended checkout instead of depending on the WSL resume wrapper.
- Canonical readiness still requires proving the loop from the intended checkout after control-plane changes land there.

## Cutover Readiness

Do not switch authority on **April 9, 2026** unless:

- Gate 0 from the canonical doctrine is fully green
- shadow runs are stable from the intended Windows checkout
- backend proof is green enough for the path Codex will own
