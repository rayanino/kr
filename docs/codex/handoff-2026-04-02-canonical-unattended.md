# Codex Handoff

## Canonical unattended lane

- repo path: `/home/rayane/kr-canonical-unattended`
- branch: `codex/canonical-unattended-20260402`
- source proof lane preserved at: `C:\Users\Rayane\Desktop\kr-mainline-proof`
- dirty Windows checkout preserved at: `C:\Users\Rayane\Desktop\kr`

This lane is the clean WSL canonical unattended host chosen to avoid trampling the dirty Windows checkout.

## Landed commits on this branch

- `6abcb824` `codex: reconcile doctrine and harden WSL shadow runtime`
- `579e8367` `docs(codex): record successful proof-worktree shadow loop evidence`
- `da4e7709` `docs(codex): add bulletproof fresh-chat handoff`
- `e5717ee8` `docs(codex): activate clean canonical unattended lane`
- `23cd43d8` `docs(codex): reconcile April 2 autonomous control plane`
- `efa72b27` `fix(codex): bound runtime auth preflight timeouts`
- `0b025eaf` `docs(codex): align canonical unattended lane controls`

## What was verified here

- `make quality-gate MODE=integration PATHS="ACTIVE_AUTHORITY.md docs/codex/operating-model.md docs/codex/runtime-policy.md docs/codex/shadow-24x7-runbook.md docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md scripts/check_runtime_cli_auth.py tests/test_codex_control_plane.py"`
  - passed
- `python scripts/check_codex_kr_setup.py --auth-preflight`
  - passed
- `python -m pytest tests/test_codex_control_plane.py -q`
  - passed under system Python
- `.venv/bin/python -m pytest tests/test_codex_control_plane.py -q`
  - passed
- bounded canonical-lane confirmation run:
  - `.venv/bin/python scripts/overnight_codex_task_generator.py --output overnight_codex/manifest.json`
  - `.venv/bin/python scripts/overnight_codex_orchestrator.py --manifest overnight_codex/manifest.json --task val-contracts --hours 0.35`
  - result: success
  - artifacts:
    - `overnight_codex/results/val-contracts/final_response.json`
    - `overnight_codex/results/val-contracts/summary.md`
    - `overnight_codex/progress.md`
    - `overnight_codex/state.json`
    - `overnight_codex/MORNING_REPORT.md`

## Important current truths

- `ACTIVE_AUTHORITY.md` now says `active_authority: codex` and `runtime_mode: autonomous_codex`.
- The doctrine and runtime-policy docs are reconciled to the April 2 cutover and the chosen canonical WSL lane.
- The auth preflight script no longer hangs indefinitely because it now enforces a per-backend timeout.
- The runtime auth preflight succeeded with all three backends using the script path.
- Direct ad hoc `claude --bare -p ...` calls were inconsistent earlier in the session, so treat Claude Code coworker health as something to verify explicitly at each milestone rather than assume from a single shell probe.

## Remaining blockers / next steps

1. Re-run the wrapper or loop entrypoint with the explicit canonical runtime dir:
   - `powershell -ExecutionPolicy Bypass -File .\scripts\overnight_codex_wsl_resume.ps1 -RuntimeDir ~/kr-canonical-unattended -RunCycle -Hours 1.5`
   - or `powershell -ExecutionPolicy Bypass -File .\scripts\run_overnight_codex_shadow_loop.ps1 -RuntimeDir ~/kr-canonical-unattended -TotalHours 8 -CycleHours 1.5 -IntervalMinutes 120`
2. Resync the Windows checkout before any Windows-launched bootstrap or resume. The setup audit currently reports WSL-first parity drift because the WSL lane has newer control-plane content, including `scripts/check_runtime_cli_auth.py`.
3. Keep the dirty original Windows checkout untouched unless a deliberate landing plan back into that lane is chosen later.
4. The latest bounded proof finding is high-value and still open:
   - `overnight_codex/results/val-contracts/summary.md`
   - validation tooling still reasons over stale or non-runtime boundary shapes
   - taxonomy keeps dual outward contracts
   - taxonomy to synthesis remains permissive enough to hide malformed inputs

## Incidental dirty files

Ignore unless they become the task:

- `.claude/session_state.json`
- `overnight_codex/MORNING_REPORT.md`

They reflect live coworker/runtime activity, not control-plane source drift.
