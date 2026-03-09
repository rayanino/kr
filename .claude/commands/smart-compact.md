---
description: Compact context while preserving critical KR project state. Use instead of bare /compact.
---
Before compacting, dump the following to memory:

1. **Active task**: What are we working on? Which engine? Which SPEC section?
2. **Modified files**: List every file modified in this session.
3. **Decisions made**: Any architectural or design decisions reached.
4. **Blockers/open questions**: Anything unresolved.
5. **Next action**: What should happen immediately after compaction.

Then run `/compact` with focus instructions:
"Preserve: all modified file paths, architectural decisions, the active engine name and SPEC section, test commands, and the next action. Drop: file contents that can be re-read, exploratory dead ends, verbose tool output."

After compaction completes, read NEXT.md and the active engine's CLAUDE.md to restore working context.
