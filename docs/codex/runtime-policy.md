# Codex Runtime Policy

## Host

- Preferred unattended host: WSL2 runtime clone.
- Do not run the long-lived unattended runtime from the interactive Windows checkout.
- Keep tool caches, temp files, and Python runtimes inside the WSL environment.

## Bootstrap

- Windows-side prerequisites: enable `Microsoft-Windows-Subsystem-Linux`, reboot, and install `Ubuntu 24.04 LTS`.
- First post-reboot launch: run `ubuntu2404.exe` once and finish the Linux user creation.
- Canonical bootstrap entrypoint after that: `powershell -ExecutionPolicy Bypass -File scripts/overnight_codex_wsl_resume.ps1 -RunShadowRehearsal`
- The PowerShell wrapper invokes `scripts/overnight_codex_wsl_bootstrap.sh` inside WSL, syncs the current Windows checkout into `~/kr-codex`, mirrors local Codex/Gemini/Claude auth where available, verifies required tools, and optionally runs the first queue-only shadow rehearsal.

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
- The runtime may auto-apply bounded changes only when:
  - the runtime clone is clean at launch
  - baseline tests pass
  - the changed files stay inside the task allowlist
  - the shared quality gate passes
- If any condition fails, queue the patch or skip the task and continue.

## Owner Interaction

- The owner is not a reviewer in routine unattended runs.
- The owner only provides resources the runtime cannot acquire itself, such as subscriptions, tools, or credentials.

## Protected Areas

The unattended runtime must never edit:

- `.claude/`
- `CLAUDE.md`
- `NEXT.md`
- `docs/superpowers/`
- architect-facing planning files

## Startup Checklist

1. Confirm `ACTIVE_AUTHORITY.md`.
2. Confirm runtime mode.
3. Verify Codex CLI, Python, pytest, and git are available.
4. Run preflight.
5. Start `overnight_codex`.

## Shutdown Artifacts

Every unattended run must leave:

- `overnight_codex/backlog.json`
- `overnight_codex/state.json`
- `overnight_codex/progress.md`
- `overnight_codex/MORNING_REPORT.md`
- queued patches or explicit blockers for anything unresolved
