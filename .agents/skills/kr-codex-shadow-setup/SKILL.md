---
name: kr-codex-shadow-setup
description: "Use when KR still has `active_authority: claude` and Codex must stay inside setup, runtime, or read-only shadow lanes. This skill narrows the allowed write surface and blocks accidental engine-lane drift."
---

# KR Codex Shadow Setup

When `ACTIVE_AUTHORITY.md` says `active_authority: claude`, Codex is not the primary engineer.

Allowed work:

- `.codex/`
- `.agents/skills/`
- `docs/codex/`
- `overnight_codex/`
- `scripts/overnight_codex_*`
- `scripts/check_codex_kr_setup.py`
- `scripts/check_runtime_cli_auth.py`
- `scripts/run_codex_backend_proof_smoke.sh`
- `scripts/start_overnight_codex.sh`
- read-only inspection and queued shadow analysis

Do not edit:

- `.claude/`
- `CLAUDE.md`
- `NEXT.md`
- `docs/superpowers/`
- engine/shared/library implementation paths unless the authority file changes

If the requested task drifts toward engine implementation, stop and re-check the authority lane before proceeding.
