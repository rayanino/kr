---
description: Compact context while preserving critical KR project state. Use instead of bare /compact.
---
Before compacting, do ALL of these:

1. **Save live state to Serena memory** (survives compaction):
   Call Serena's write_memory with name 'session_state' containing:
   - Active engine and session number
   - Current module/function being worked on
   - Test count (last known)
   - Files modified this session
   - Decisions made
   - Open blockers
   - Exact next action
   - Session cost (EUR spent, from COST_LOG.json if available)
   - Circuit breaker triggers this session (from .claude/circuit_breaker.log)
   - Print warnings in modified files
   - Recent hook failures or warnings

2. **Update MEMORY.md** if any stable facts changed (new session complete, new test count milestone, new architecture decision).

3. **Run /compact** with focus:
   "Preserve: active engine name, SPEC section, modified file paths, architectural decisions, test counts, next action. Drop: file contents, exploratory output, verbose tool results."

4. **After compaction**: Read NEXT.md, active engine CLAUDE.md, and call Serena read_memory('session_state').
