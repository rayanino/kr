---
globs: ["**/*"]
---
## Context & Session Discipline

- **One engine per session.** Start fresh context for each engine, each SPEC section, each implementation block. Cross-engine work causes context pollution.
- **Use `/smart-compact` proactively** at ~60% context rather than waiting for auto-compaction at 80%. Controlled compaction preserves more state.
- **Use `/catchup` at session start** to reload context from git + NEXT.md rather than relying on prior conversational state.
- **Before implementing:** always read the SPEC section from the file, not from memory. Paraphrased versions introduce subtle errors.
- **After any compaction:** immediately re-read (1) active engine CLAUDE.md, (2) active SPEC section, (3) NEXT.md. These are compaction-fragile:
  - D-023 metadata pass-through semantics (never delete upstream fields)
  - Arabic text handling rules (diacritics, normalization, encoding)
  - Enum values and their precise definitions (Genre, StructuralFormat, etc.)
  - Multi-model consensus requirements (D-041)
- MCP tools consume context. Keep enabled MCP servers to <=5. Prefer Bash-wrapped CLI tools for simple operations: `git log` over GitHub MCP.
- When dispatching subagents, pass OBJECTIVE CONTEXT not raw data. Include: SPEC section, files changed, deliberate trade-offs. Max 3 retrieval iterations per subagent.
- Large tool results (>500 lines): note key findings in response text, since tool results may be cleared during compaction.
- When context is filling, prioritize retaining: (1) SPEC rules, (2) test failures, (3) Arabic handling constraints, (4) D-023 semantics. Deprioritize: verbose output, exploratory reads, completed work.
- **After LLM pipeline sessions:** report trace count, storage location, and whether `recursive-improve eval` was run.
