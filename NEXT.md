# NEXT SESSION

## Context

The owner conducted a skills design session (2026-03-07). Six Claude Chat skills were written and iterated through 3 versions. The architecture shifted to a repo-first workflow where Claude Chat clones the repo at each chat start.

Read the handoff document for full context:
`skills/handoffs/workflow-research-2026-03-07.md`

## Immediate Task

**Deep research into Claude Chat optimization for complex multi-session projects.**

The skills are functional but the setup is untested. Before the owner starts real spec review, investigate:

1. Community patterns (Reddit r/ClaudeCode, r/ClaudeAI) for Claude Chat project management
2. Available MCPs that could enhance the workflow (GitHub MCP, filesystem MCPs)
3. Claude Chat-specific limitations and workarounds
4. How people handle the Claude Chat → Claude Code transition
5. Skill triggering reliability improvements
6. Whether our repo-first approach (clone at chat start) has known issues

Then: apply findings to improve the 6 skills and the project setup.

## Owner Status

- Currently reading the source engine SPEC and writing numbered domain comments
- Has OpenRouter API key ready
- Will create the source engine Claude Chat project after the workflow is optimized
- No rush — quality over speed
