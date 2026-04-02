---
name: kr-codex-environment-audit
description: Use when KR Codex needs a fast environment health check across repo config, hooks, MCP visibility, auth state, and WSL-vs-Windows parity.
---

# KR Codex Environment Audit

Run the narrowest useful preflight:

- Default WSL-first audit:
  - `bash scripts/run_codex_wsl_preflight.sh`
- Windows-launch parity audit:
  - `bash scripts/run_codex_wsl_preflight.sh --strict-parity`

Interpret results conservatively:

- repo-local MCP servers must be visible
- global irrelevant MCP servers should be disabled inside KR
- auth preflight failures are runtime blockers
- Windows drift is a warning in WSL-first work, but a blocker for Windows-launched bootstrap paths
