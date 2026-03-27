# CC Critique Prompt — Ready to Paste into Claude Code

Copy everything below this line and paste it as a prompt to Claude Code.

---

Read `reference/FACTORY_ROADMAP.md` in full. This is the governing plan for building an autonomous engine-building factory for KR.

**Your role: ADVERSARIAL CRITIC.** You are NOT here to agree, confirm, or praise the roadmap. Your job is to find problems. If you find fewer than 5 problems, you haven't looked hard enough. Every "this looks good" is a failure of your review.

## Task 1: Assumption Audit

The roadmap makes assumptions about YOUR capabilities as Claude Code. For each assumption below, state whether it is **TRUE**, **FALSE**, or **UNVERIFIED** based on your actual experience running in this repo:

1. `claude -p` can run headlessly and produce structured JSON output via `--output-format json`
2. You can read and act on CLAUDE.md and `.claude/` context automatically in headless mode
3. You can reliably process work units that require reading 5+ large files (SPEC, contracts, engine code, test output) within your context window
4. Your 13 hooks fire correctly in headless mode (not just interactive mode)
5. Your agents (e.g., code-reviewer, spec-adversary) can be dispatched as subagents in headless mode
6. You can produce artifact bundles (prompt hash, inputs, outputs, git SHA) as part of your output
7. You can run `pytest` and capture results in headless mode
8. You can commit and push to git in headless mode
9. You can be called repeatedly by a Python orchestrator script without session state leaking between calls
10. `--json-schema` works reliably for structured output in headless mode (not just sometimes)

For each FALSE or UNVERIFIED item: what is the actual behavior? What would the orchestrator need to handle?

## Task 2: Missing Requirements

What does the roadmap NOT address that you would need to function as the autonomous builder? Think about:

- What context do you need at the start of each work unit? Does the orchestrator provide it?
- What happens when you hit a problem mid-work-unit that requires a design decision? You can't ask the architect (Claude Chat isn't in the loop).
- How do you know when a work unit is "done" vs "stuck"? What's your signal to the orchestrator?
- What about CLAUDE.md staleness? If the orchestrator calls you 48 times/day, and CLAUDE.md is updated by Session 1, does your headless invocation re-read it each time?
- What about tool availability? Can you access web search in headless mode? Can you use MCP servers?

List at least 5 things the roadmap doesn't address.

## Task 3: Failure Mode Analysis

For each of these scenarios, describe what actually happens (not what should happen):

1. The orchestrator calls `claude -p "Implement function X per SPEC section 4.3" --output-format json`. The SPEC has an ambiguity. What do you do? (Remember: you can't ask the architect.)
2. The orchestrator calls you to implement a bug fix. You fix it, but the fix breaks 3 other tests. You try to fix those, but now you've been running for 20 minutes and the orchestrator's timeout is 15 minutes.
3. The orchestrator calls you with a work unit, but the work unit's `inputs[]` references a file that doesn't exist (typo in the orchestrator's config).
4. You're implementing a work unit and you realize the SPEC itself has a bug. The orchestrator expects implementation output, not SPEC critique.
5. The orchestrator calls you 48 times in one day. By call 40, the Max subscription's usage limits are hit. What error do you return?

## Task 4: Your Top 3 Additions

Based on Tasks 1-3, propose the 3 most important additions to the roadmap from YOUR perspective as the execution layer. For each:
- What is the addition?
- Why is it necessary?
- What happens if it's not addressed?

## Output Format

Respond as structured JSON:
```json
{
  "assumption_audit": [
    {"id": 1, "assumption": "...", "verdict": "TRUE|FALSE|UNVERIFIED", "actual_behavior": "...", "orchestrator_implication": "..."},
    ...
  ],
  "missing_requirements": [
    {"id": 1, "requirement": "...", "why_needed": "...", "what_happens_without": "..."},
    ...
  ],
  "failure_modes": [
    {"scenario": 1, "actual_behavior": "...", "orchestrator_impact": "..."},
    ...
  ],
  "top_additions": [
    {"addition": "...", "rationale": "...", "risk_if_missing": "..."},
    ...
  ]
}
```

**Remember: your job is to find problems. Be ruthlessly honest about your own limitations. The architect will use your critique to improve the roadmap — but only if you're honest.**

Stop after this task. Do not continue to the next session.
