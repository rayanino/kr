---
name: kr-codex-environment-audit
description: Use when KR Codex needs a fast environment health check across repo config, hooks, MCP visibility, auth state, and the active Windows checkout.
---

# KR Codex Environment Audit

Run the narrowest useful preflight:

- Default Windows audit:
  - `python scripts/check_codex_kr_setup.py`
- Windows audit with backend health:
  - `python scripts/check_codex_kr_setup.py --auth-preflight`
- Legacy WSL drift check when needed:
  - `python scripts/check_codex_kr_setup.py --check-wsl-parity`

Interpret results conservatively:

- repo-local MCP servers must be visible
- global irrelevant MCP servers should be disabled inside KR
- auth preflight failures are runtime blockers
- legacy WSL drift is advisory unless the task explicitly depends on that clone
