# Codex Runtime Policy

## Host

- Preferred unattended host: WSL2 runtime clone.
- Do not run the long-lived unattended runtime from the interactive Windows checkout.
- Keep tool caches, temp files, and Python runtimes inside the WSL environment.

## Bootstrap

- Windows-side prerequisites: enable `Microsoft-Windows-Subsystem-Linux`, reboot, and install `Ubuntu 24.04 LTS`.
- First post-reboot launch: run `ubuntu2404.exe` once and finish the Linux user creation.
- Canonical bootstrap entrypoint after that: `powershell -ExecutionPolicy Bypass -File scripts/overnight_codex_wsl_resume.ps1 -RunShadowRehearsal -RuntimeDir ~/kr-canonical-unattended`
- The PowerShell wrapper invokes `scripts/overnight_codex_wsl_bootstrap.sh` inside WSL, syncs the selected clean Windows source checkout into its target runtime dir, mirrors local Codex/Gemini/Claude auth where available, verifies required tools, and optionally runs the first queue-only shadow rehearsal. Do not use the dirty original Windows checkout as that source.

## Runtime Profiles

The repo-local Codex config defines these profiles:

- `kr_interactive`
- `kr_shadow`
- `kr_peer_review`
- `kr_research`

Recommended usage:

- interactive local setup: `codex -p kr_interactive`
- queue-only shadow work: `codex -p kr_shadow`
- read-only review packets: `codex -p kr_peer_review`
- docs or web verification: `codex -p kr_research`

## Runtime Modes

### `shadow_setup`

- Active authority is not Codex.
- The runtime may execute read-only tasks and repo-neutral setup tasks.
- Discovery may create or update `overnight_codex/backlog.json`, but it must not create new engine-code patches or queued commits.
- Guarded write tasks outside Codex setup prefixes must be skipped, not queued for auto-apply.
- Apply mode stays `queue_only`.

### `autonomous_codex`

- Codex is the active authority.
- Guarded-write tasks must come from pre-approved backlog items. Same-run discovery must not generate same-run implementation.
- The runtime starts in `queue_only` even after cutover.
- Promotion beyond `queue_only` is governed by `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md`.
- During the doctrine period, engine-source auto-apply remains out of scope.

## Owner Interaction

- The owner is not a reviewer in routine unattended runs.
- The owner only provides resources the runtime cannot acquire itself, such as subscriptions, tools, or credentials.

## Protected Areas

The unattended runtime must never edit:

- `.claude/`
- `CLAUDE.md`
- `NEXT.md`
- `ACTIVE_AUTHORITY.md`
- `.kr/ACTIVE.md`
- `.kr/HANDOFF.md`
- `.kr/DECISIONS.md`
- `.kr/*.md`
- `.kr/codex_write_prefixes.txt`
- the repo-local Codex control-plane directory when restored (`.codex/`)
- `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md`
- `docs/codex/operating-model.md`
- `docs/codex/runtime-policy.md`
- `docs/codex/coworker-policy.md`
- `docs/codex/shadow-24x7-runbook.md`
- `docs/codex/backend-proof-status.md`
- `docs/superpowers/`
- `reference/GOVERNANCE.md`
- `scripts/overnight_codex_orchestrator.py`
- `scripts/overnight_codex_wsl_bootstrap.sh`
- `scripts/overnight_codex_wsl_resume.ps1`
- `scripts/run_overnight_codex_shadow_loop.ps1`
- `scripts/check_codex_kr_setup.py`
- `scripts/check_runtime_cli_auth.py`
- `scripts/quality_gate.py`

Protected-area enforcement must be synchronous. It must block the write before a commit or apply completes rather than relying on a later audit cycle.

## Startup Checklist

1. Confirm `ACTIVE_AUTHORITY.md`.
2. Confirm runtime mode.
3. Run the setup audit from the canonical host.
4. Verify Codex CLI, Python, pytest, and git are available.
5. Run preflight.
6. Start `overnight_codex`.

## Shutdown Artifacts

Every unattended run must leave:

- `overnight_codex/backlog.json`
- `overnight_codex/state.json`
- `overnight_codex/progress.md`
- `overnight_codex/MORNING_REPORT.md`
- queued patches or explicit blockers for anything unresolved

## Daily Report Contract

During the active April 2, 2026 to July 1, 2026 doctrine period:

- the single source of truth is `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md`
- the owner gets one frozen daily `MORNING_REPORT.md`
- default on silence is `defer_and_continue`, which means the item stays blocked and the runtime proceeds only to unrelated work

## Degraded Modes

- authority mode and health state are separate dimensions
- `full`: Codex, Claude Code, and Gemini healthy
- `reduced`: Codex plus exactly one peer coworker healthy; no gate promotion and no auto-apply
- `solo`: Codex only; read-only audits, report generation, state repair, and backlog shaping only
- `halted`: Codex unavailable, setup/parity failure, protected-area violation, or repeated rollback/circuit-breaker trigger

Exact degraded-mode behavior is defined by `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md`.
