You just completed a task. Before anything else, you must perform a structured self-review of your own work. This review is mandatory — the Architect will verify it independently, and any gaps you miss here will be caught and flagged.

<task_that_was_assigned>
Read reference/AGENT_ARCHITECTURE.md. Probe 1 wrote the 6 SPEC team agents. Write ALL remaining agent definitions so the full 18-agent system is in place before building starts. Specifically:

1. Write .claude/agents/build-prober.md (Red Team — reviews build session diffs vs SPEC)
2. Write .claude/agents/spec-adversary.md (Red Team — writes adversarial test cases from finalized SPEC)
3. Write .claude/agents/verdict-adversary.md (Red Team — re-probes VERIFIED items to disprove them)
4. Write .claude/agents/triage-analyst.md (Verification — automated checks on all items, €0)
5. Write .claude/agents/verifier-a.md (Verification — Playbook-guided verification)
6. Write .claude/agents/verifier-b.md (Verification — first-principles, NO Playbook access)
7. Write .claude/agents/consolidator.md (Verification — compares A vs B, resolves disagreements, 5-round self-review)

After writing all 7, review existing agents and update any that need alignment with the architecture.
Then run the SPEC adversary on engines/normalization/SPEC.md.
Commit everything.
</task_that_was_assigned>

<review_instructions>
Perform the following checks in order. For each check, state the result explicitly — do not skip any.

Step 1 — Deliverables inventory. For each of the 7 agents listed above, check whether the file exists at `.claude/agents/{name}.md`. List each one with EXISTS or MISSING. Then list any files you created or modified that were NOT in the original task.

Step 2 — If any agents are MISSING, explain why. Did you skip them? Did you run out of context? Did you interpret the task differently? State the reason plainly.

Step 3 — For each agent file that EXISTS, verify it against `reference/AGENT_ARCHITECTURE.md`:
  - Does the agent's role match the architecture's description for that agent?
  - Does the agent definition include: clear input/output contract, self-review protocol, specific failure modes to watch for?
  - Is the model field set correctly (opus for Red Team and Verification, sonnet for triage-analyst)?

Step 4 — SPEC adversary check. Did you run the SPEC adversary on `engines/normalization/SPEC.md`? If yes, where is the output? If no, why not?

Step 5 — Unplanned work. List any work you did that was NOT in the task assignment (e.g., hooks, rules, config changes). For each item, explain why you did it and whether it should be kept, reverted, or reviewed by the Architect.

Step 6 — Honest assessment. Rate your completion of the assigned task:
  - COMPLETE: all 7 agents written, SPEC adversary run, everything committed
  - PARTIAL: some agents written, or SPEC adversary not run
  - INCOMPLETE: most deliverables missing
  - OFF-TRACK: did different work than what was assigned
</review_instructions>

<output_format>
Produce your review as a structured report:

## Self-Review Report

### Deliverables Inventory
| # | Agent | File Path | Status |
|---|-------|-----------|--------|
| 1 | build-prober | .claude/agents/build-prober.md | EXISTS / MISSING |
| ... | ... | ... | ... |

### Missing Deliverables (if any)
[Explanation for each missing item]

### Agent Verification (for each that exists)
[Architecture alignment check per agent]

### SPEC Adversary
[Did it run? Where is the output?]

### Unplanned Work
[List with justification for each]

### Completion Rating: [COMPLETE / PARTIAL / INCOMPLETE / OFF-TRACK]

### What the Architect Should Know
[Anything the reviewing Architect needs to be aware of — blockers, concerns, decisions you made]
</output_format>

After completing this review, commit the review report as `reference/CC_SELF_REVIEW_AGENTS.md` and push.
