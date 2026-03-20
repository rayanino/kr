---
description: Chain specialized agents in sequence with structured handoffs. Usage /orchestrate <chain> <engine>. Chains are post-build and verify.
allowed-tools: Bash(python *), Bash(python3 *), Bash(git *), Read, Glob, Grep
---
Orchestrate a chain of agents with structured handoffs.

Parse `$ARGUMENTS` as `<chain> <engine>`, e.g., `post-build normalization`.

Read `reference/protocols/AGENT_HANDOFF_FORMAT.md` first — every agent output MUST use this envelope.

## Chain A: `post-build`

Run after a build session to validate work. Sequence:

1. **code-reviewer** — dispatch with:
   - Files changed: `git diff --name-only HEAD~3..HEAD -- engines/<engine>/ shared/`
   - The engine's SPEC.md section being implemented (read from NEXT.md)
   - Context: "Post-build review for <engine>"

2. Wait for code-reviewer to complete.

3. **build-prober** — dispatch with:
   - The same git range
   - The code-reviewer's `### Downstream Context` as input
   - Context: "Build probe for <engine>"

4. Wait for build-prober to complete.

5. **Combined report** — merge both outputs:
   ```
   ## Post-Build Orchestration Report — <engine>

   ### Code Review Summary
   HIGH: [count] | MEDIUM: [count] | LOW: [count]
   [Key findings from code-reviewer]

   ### Build Probe Summary
   DEVIATION: [count] | IMPROVISATION: [count] | OMISSION: [count]
   Health: [CLEAN/MINOR_DRIFT/SIGNIFICANT_DRIFT]
   [Key findings from build-prober]

   ### Combined Action Items
   [Merged, deduplicated list ordered by severity]
   ```

## Chain B: `verify`

Run during evaluation phases. Sequence:

1. **triage-analyst** — run automated pre-checks on pipeline output
2. Wait for triage to complete.
3. **verifier-a** + **verifier-b** — dispatch in parallel with triage output
4. Wait for both verifiers to complete.
5. **consolidator** — dispatch with both verifier reports
6. Present final consolidated verdicts.

Pass `### Downstream Context` from each agent's output as input to the next agent.
