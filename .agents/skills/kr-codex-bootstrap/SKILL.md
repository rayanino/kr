---
name: kr-codex-bootstrap
description: Use when building or repairing KR's repo-local Codex layer, especially `.codex/`, `.agents/skills/`, the Windows launcher, and shadow-control surfaces.
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
- Windows launcher and shadow-loop scripts
- preserving Claude Code and Gemini workflow surfaces

Before concluding bootstrap work:

- run `python scripts/check_codex_kr_setup.py`
- run `python scripts/check_codex_kr_setup.py --auth-preflight` if coworker/runtime health matters
- note any legacy WSL fallback dependency explicitly instead of assuming it
