---
name: kr-codex-wsl-preflight
description: Legacy fallback skill. Use only when a concrete Windows blocker forces KR Codex work back onto the WSL runtime.
---

# KR Codex WSL Preflight

Only use this skill after documenting why the Windows checkout is insufficient.

Run these checks in order:

1. `python scripts/check_codex_kr_setup.py`
2. `python scripts/check_runtime_cli_auth.py --json`
3. `bash scripts/run_codex_backend_proof_smoke.sh` when the CLI backend path needs proof

Confirm:

- repo-local `.codex/` and `.agents/skills/` are present in the WSL clone
- repo-local MCP servers are visible and unrelated home-level servers are disabled for KR
- `codex`, `claude`, and `gemini` are native Linux installs in WSL
- the Windows checkout is not stale enough to overwrite the runtime on the next bootstrap

If parity is broken, do not treat the runtime as healthy until the drift is explained or corrected. This is fallback-only, not the default KR path.
