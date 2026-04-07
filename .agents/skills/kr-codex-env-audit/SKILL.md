---
name: kr-codex-env-audit
description: Use when auditing KR Codex environment health, home-config trust, MCP noise, backend auth, and Windows control-plane readiness.
---

# KR Codex Environment Audit

Run these checks in order:

1. `python scripts/check_codex_kr_setup.py`
2. `python scripts/check_runtime_cli_auth.py --json`
3. `codex mcp list`

Focus on:

- repo-local files missing from the active tree
- home config trust for the current Windows checkout
- unexpected enabled MCP servers that create auth noise
- backend auth drift for `claude`, `codex`, and `gemini`
- whether the current Windows checkout is safe to use as the canonical Codex lane

Use `python scripts/check_codex_kr_setup.py --check-wsl-parity` only when diagnosing the legacy WSL clone.

Record blockers explicitly. Do not silently treat auth-noise or stale host assumptions as resolved.
