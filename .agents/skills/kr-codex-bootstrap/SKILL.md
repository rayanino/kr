---
name: kr-codex-bootstrap
description: Use when building or repairing KR's repo-local Codex layer, especially `.codex/`, `.agents/skills/`, and WSL bootstrap surfaces.
---

# KR Codex Bootstrap

Read these files first:

1. `ACTIVE_AUTHORITY.md`
2. `docs/codex/operating-model.md`
3. `docs/codex/runtime-policy.md`
4. `docs/codex/wsl-bootstrap.md`

Focus on:

- repo-local `.codex/config.toml`
- repo-local `.codex/agents/`
- repo-local `.agents/skills/`
- WSL bootstrap and resume scripts
- preserving Claude Code and Gemini workflow surfaces

Before concluding bootstrap work:

- run `python scripts/check_codex_kr_setup.py`
- note whether Windows checkout parity is current, advisory-only, or explicitly stale
