# Active Authority

active_authority: shared
effective_date: 2026-04-13
branch: clean-start
runtime_mode: full_access
frontier_file: NEXT.md

## Rules

- Both Claude Code and Codex CLI have full read/write access to all files.
- No lane restrictions. No shadow mode. No protected paths.
- Both tools commit directly to `clean-start` (the only branch).
- Quality gates still apply: run tests before committing, follow CLAUDE.md rules.
- If both are working simultaneously, coordinate via `.kr/ACTIVE.md` to avoid editing the same files.
