---
name: kr-codex-runtime
description: "Use for KR Codex runtime work: Windows launchers, overnight_codex, auth preflights, bounded backend proof, and scheduler-safe shadow operation."
---

# KR Codex Runtime

Read these files first:

1. `ACTIVE_AUTHORITY.md`
2. `docs/codex/runtime-policy.md`
3. `docs/codex/operating-model.md`
4. `overnight_codex/README.md`
5. `docs/codex/shadow-24x7-runbook.md`

Operational defaults:

- Windows checkout is the canonical Codex host
- WSL is legacy fallback only when a Windows blocker is documented
- in `shadow_setup`, keep project-code work queue-only
- never touch protected KR areas from unattended runs

Before calling the runtime healthy, verify:

- Codex CLI
- Python
- pytest
- git
- MCP visibility from the repo config
- `scripts/check_runtime_cli_auth.py`
