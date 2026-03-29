# KR Overnight Codex

`overnight_codex/` is a separate, Codex-first autonomous runtime.

It is intentionally lower authority than the existing Claude overnight system:
- It may do bounded hardening and local structural analysis.
- It may not own architecture, roadmap, specs, or Claude-facing operational files.
- It may not touch `.claude/`, `overnight/`, `docs/superpowers/`, `CLAUDE.md`, or `NEXT.md`.
- Codex tasks run in isolated worktrees; readonly tasks are discarded from those worktrees, guarded-write tasks are queued or conditionally applied only after host-side gates.

Runtime artifacts live here, not under `overnight/`:
- `manifest.json`
- `state.json`
- `progress.md`
- `MORNING_REPORT.md`
- `results/`
- `queue/`
- `worktrees/`
- `FINDINGS_TRACKER.md`

When the main repo is dirty or drifts during a run, guarded-write tasks stay isolated and are queued as patches instead of being auto-applied.
