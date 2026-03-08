# KR Skills — مهارات خزانة ريان

Skills are uploaded to Claude Chat (Customize > Skills) as .zip files. They activate when you invoke them by name in a chat.

## The 5 Skills

| Skill | Step | What It Does |
|-------|------|-------------|
| **kr-core-extract** | Step 1 | Separates core architecture from extensions. Produces classification table, then rewrites SPEC for core-only depth. |
| **kr-spec-review** | Step 1 | Resolves owner domain comments on the core SPEC. Investigates each comment with deep research before forming a position. |
| **kr-research** | Steps 1-2 | Deep architectural research. Explores approaches, validates tools, compares similar systems. Minimum 8 searches. |
| **kr-build-prep** | Step 3 | Prepares Claude Code environment. Technology survey, architecture, stubs, tests, CLAUDE.md. |
| **kr-evaluate** | Step 4 | Reviews test results. Categorizes findings as core gaps, extension opportunities, or lessons learned. |

## How to Install

1. Go to Customize > Skills in Claude Chat
2. Upload all 5 `.zip` files from this directory
3. Toggle each skill ON
4. Test: say "use kr-research" in any chat — if it activates, skills work

## Other Directories

- `engine-project-template/` — Ready-to-paste custom instructions per engine
- `shared/` — ENGINE_PROTOCOL.md (the 4-step process), COMMENT_TEMPLATE.md, HANDOFF_PROTOCOL.md
- `handoffs/` — Session handoff documents

Each engine gets its own Claude Chat project. Setup files are in `engine-project-template/` with a ready-to-paste file per engine.
