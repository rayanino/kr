# KR Overnight Codex

`overnight_codex/` is a separate, Codex-first autonomous runtime.

It is intentionally lower authority than the existing Claude overnight system:
- It may do bounded hardening and local structural analysis.
- It may not own architecture, roadmap, specs, or Claude-facing operational files.
- It may not touch `.claude/`, `overnight/`, `docs/superpowers/`, `CLAUDE.md`, or `NEXT.md`.
- Codex tasks run in isolated worktrees; readonly tasks are discarded from those worktrees, guarded-write tasks are queued or conditionally applied only after host-side gates.

Runtime artifacts live here, not under `overnight/`:
- `manifest.json`
- `backlog.json`
- `state.json`
- `progress.md`
- `MORNING_REPORT.md`
- `results/`
- `queue/` (secondary; only for post-gate write tasks that could not auto-apply)
- `worktrees/`
- `FINDINGS_TRACKER.md` (legacy mirror, no longer the primary state)

Operating model:
- Read-only tasks run in disposable detached worktrees and stage their task output outside the main checkout before artifacts are copied back into `overnight_codex/results/`.
- Guarded-write tasks may only come from `approved` backlog items; discovery tasks no longer create same-run write tasks.
- In `shadow_setup`, the runtime is backlog-only for project code: it may discover and synchronize implementation-ready backlog items, but it does not generate new engine-code patches.
- When the main repo is dirty or drifts during a write run, guarded-write tasks stay isolated and are queued as patches instead of being auto-applied.
- When a live Claude session is detected, `overnight_codex` also forces queue-only mode to avoid trampling active Claude work.

## WSL Bootstrap

Use the dedicated WSL runtime clone, not the interactive Windows checkout.

1. Reboot after enabling the Windows WSL feature.
2. Run `ubuntu2404.exe` once to finish distro registration.
3. Run `powershell -ExecutionPolicy Bypass -File scripts/overnight_codex_wsl_resume.ps1 -RunShadowRehearsal`.

That wrapper calls `scripts/overnight_codex_wsl_bootstrap.sh` inside WSL, syncs the current checkout into `~/kr-codex`, mirrors the local Codex/Gemini/Claude auth state where available, verifies the required CLI stack, and launches the first safe queue-only shadow rehearsal when requested.
