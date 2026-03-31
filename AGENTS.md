# KR Codex Entry

Start every serious Codex session in this order:

1. Read `ACTIVE_AUTHORITY.md`.
2. Read `CLAUDE.md`.
3. Read `docs/codex/operating-model.md`.
4. Read `.kr/ACTIVE.md` and `.kr/HANDOFF.md` for the current frontier.
5. Read the relevant `engines/<engine>/CLAUDE.md`.
6. Read `docs/codex/dispatch-templates.md` before using subagents.
7. Read `.claude/skills/arabic-text/SKILL.md` and `.claude/skills/knowledge-safety/SKILL.md` before touching Arabic text or scholarly metadata.

Critical rules:

- One active authority at a time. If `ACTIVE_AUTHORITY.md` says `claude`, Codex stays in setup or shadow lanes only.
- Do not rewrite `.claude/` or create parallel authority files like `NEXT_CODEX.md`.
- `NEXT.md` remains the repo-global construction frontier. `.kr/ACTIVE.md` is the current serious-work frontier for hardening and post-v1 execution.
- Use `make quality-gate MODE=<mode> PATHS="<space-separated paths>"` before declaring implementation complete.
- If a task needs domain judgment, unavailable subscriptions, external purchases, or owner action, record the blocker and move on.
- The owner supplies external resources only. Routine runtime operation must not depend on owner approvals.
- Treat Arabic text integrity, metadata preservation, and silent-failure risks as blocking defects.

Codex skills to use when available:

- `kr-claude-bridge` for KR `.claude` guidance.
- `kr-authority-handoff` for switching or rolling back authority.
- `kr-quality-gate` for post-change verification.
- `kr-hardening-loop` for bug-hunt and regression work.
- `kr-autonomous-runtime` for unattended overnight runs.
- `kr-review-dispatch` for worker and explorer prompt templates.
