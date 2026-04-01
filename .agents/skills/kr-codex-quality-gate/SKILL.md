---
name: kr-codex-quality-gate
description: Use after KR code or runtime-control-plane changes when Codex needs the exact verification surface to run before declaring work complete. This skill complements the installed `kr-quality-gate` skill with repo-local Codex setup checks.
---

# KR Codex Quality Gate

Read `docs/codex/operating-model.md` first.

For engine or shared code changes, use the canonical command:

`make quality-gate MODE=<mode> PATHS="<space-separated paths>"`

For Codex setup and runtime-control-plane changes, also run:

`python scripts/check_codex_kr_setup.py`

Use WSL for the real gate whenever hooks, MCP, or unattended-runtime behavior is part of the task.

Do not declare KR setup work complete until:

- the narrowest required quality gate passes
- the Codex setup audit passes
- any runtime/auth blockers are stated explicitly
