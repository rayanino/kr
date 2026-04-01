---
name: kr-codex-wsl-preflight
description: Use before unattended KR Codex runs or after bootstrap changes to confirm the WSL runtime, auth mirrors, and scheduler-safe entrypoints.
---

# KR Codex WSL Preflight

Run these checks in order:

1. `python scripts/check_codex_kr_setup.py`
2. `python scripts/check_runtime_cli_auth.py --json`
3. `bash scripts/run_codex_backend_proof_smoke.sh` when the CLI backend path needs proof

Confirm:

- repo-local `.codex/` and `.agents/skills/` are present in the WSL clone
- repo-local MCP servers are visible and unrelated home-level servers are disabled for KR
- `codex`, `claude`, and `gemini` are native Linux installs in WSL
- the Windows checkout is not stale enough to overwrite the runtime on the next bootstrap

If parity is broken, do not treat the runtime as healthy until the drift is explained or corrected.
