---
name: kr-codex-env-audit
description: Use when auditing KR Codex environment health, home-config trust, MCP noise, backend auth, and WSL-vs-Windows readiness.
---

# KR Codex Environment Audit

Run these checks in order:

1. `python scripts/check_codex_kr_setup.py`
2. `python scripts/check_runtime_cli_auth.py --json`
3. `codex mcp list`

Focus on:

- repo-local files missing from the active tree
- home config trust for `/home/rayane/kr-codex`
- unexpected enabled MCP servers that create auth noise
- backend auth drift for `claude`, `codex`, and `gemini`
- whether the Windows checkout is safe to use as a bootstrap source

Record blockers explicitly. Do not silently treat auth-noise or parity drift as resolved.
