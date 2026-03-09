---
description: Deep research on a topic using web search, Context7, Tavily, and project context. Returns a structured findings report.
argument-hint: <topic or question>
allowed-tools: WebSearch, WebFetch, Bash(python3:*), Read, Grep, Glob
---
Research this topic thoroughly: $ARGUMENTS

Protocol:
1. **Map the space** (3-5 searches): What exists? What tools/techniques are available? What's the state of the art?
2. **Go deep** (3-5 searches): For the most promising findings, get specifics — version numbers, API docs, benchmarks, Arabic support status.
3. **Check project context**: Search the codebase for existing related work. Check reference/RESOURCES.md for prior findings.
4. **Synthesize**: Produce a structured report with:
   - **Summary**: 2-3 sentence overview
   - **Key findings**: Specific tools, libraries, or techniques with version numbers
   - **Arabic support**: Explicitly assess Arabic text handling for each finding
   - **Recommendation**: What to use and why
   - **Risks**: Known issues, limitations, maintenance status
   - **Sources**: URLs for everything cited

If a finding should be preserved, suggest adding it to reference/RESOURCES.md.
