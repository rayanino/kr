# Agent Handoff Format

Standard envelope for all KR agent outputs. Ensures consistent handoff between chained agents (see `/orchestrate`).

## Envelope

Every agent report MUST wrap its findings in this structure:

```
## [Agent Name] Report — [Engine] [Context]

**Date:** [ISO 8601]
**Agent:** [agent filename, e.g., code-reviewer.md]
**Scope:** [files/data reviewed — list or summary]

### Summary

- HIGH: [count] — [one-line description of each]
- MEDIUM: [count]
- LOW: [count]

### Findings

[Agent-specific detail using the agent's existing format]

### Downstream Context

For next agent: [what the downstream agent needs to know]
Unresolved: [open questions that need investigation]
Files to re-examine: [specific paths worth re-reading]
```

## Rules

1. **Summary first.** The receiving agent (or human) should understand severity in 5 seconds.
2. **Preserve agent-specific formats.** The `### Findings` section uses whatever format the agent already defines (code-reviewer uses SPEC Fidelity + Issues, build-prober uses DEVIATION/IMPROVISATION/OMISSION).
3. **Downstream Context is mandatory.** Even if empty: `For next agent: none`. This prevents downstream agents from operating without awareness of upstream findings.
4. **Severity classification:**
   - HIGH = wrong behavior, data corruption risk, SPEC violation
   - MEDIUM = missing behavior, incomplete coverage, style
   - LOW = improvements, suggestions, minor quality
5. **No agent modifies files.** All agents are read-only. Action items are for the builder.
