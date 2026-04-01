---
name: kr-codex-session-start
description: Use when starting or resuming serious KR work in Codex, especially after compaction, context drift, or runtime confusion. This skill reloads the KR authority lane, active frontier, and Codex-specific operating constraints.
---

# KR Codex Session Start

Read these files in order:

1. `ACTIVE_AUTHORITY.md`
2. `CLAUDE.md`
3. `docs/codex/operating-model.md`
4. `.kr/ACTIVE.md`
5. `.kr/HANDOFF.md`
6. the relevant `engines/<engine>/CLAUDE.md`

Then lock these facts before doing work:

- `active_authority`
- `runtime_mode`
- whether the task is setup/runtime/review-only or engine-lane implementation
- whether WSL is required for the intended checks

Use the WSL clone at `/home/rayane/kr-codex` whenever hooks, repo MCP, quality-gate, or unattended runtime behavior matters.
