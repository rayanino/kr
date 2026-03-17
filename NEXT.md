# NEXT — Complete Agent Definitions Before Probe 2

## Current position: Probe 1 COMPLETE. Agent writing task INCOMPLETE — CC did SPEC fixes + hooks instead of writing 7 agents.
## What to do: CC must self-review, then write the 7 missing agents, then run SPEC adversary.
## Context: The 18-agent architecture requires all agents defined before the build starts.
  13 agents exist. 7 are missing: build-prober, spec-adversary, verdict-adversary,
  triage-analyst, verifier-a, verifier-b, consolidator.
## Owner action needed: Give CC the self-review prompt, then the agent-writing task.

---

## Step 1: CC Self-Review (owner pastes prompt)

Have CC run the self-review prompt (reference/CC_SELF_REVIEW_PROMPT.md or the prompt
the Architect prepared). CC will assess what it produced vs what was assigned.

## Step 2: Write the 7 Missing Agents

Read reference/AGENT_ARCHITECTURE.md. Write these agent definitions:

1. .claude/agents/build-prober.md (Red Team §2.4 — reviews build session diffs vs SPEC)
2. .claude/agents/spec-adversary.md (Red Team §2.4 — adversarial test cases from finalized SPEC)
3. .claude/agents/verdict-adversary.md (Red Team §2.4 — re-probes VERIFIED items)
4. .claude/agents/triage-analyst.md (Verification §2.3 — automated checks, Sonnet model, €0)
5. .claude/agents/verifier-a.md (Verification §2.3 — Playbook-guided, Opus model)
6. .claude/agents/verifier-b.md (Verification §2.3 — first-principles ONLY, NO Playbook, Opus model)
7. .claude/agents/consolidator.md (Verification §2.3 — compares A vs B, 5-round self-review, Opus)

After writing all 7, review the 6 existing agents from the pre-architecture era
(boundary-validator, code-reviewer, integrity-checker, researcher, result-analyst,
scholarly-verifier, test-engineer, spec-writer) and update any that need alignment.

## Step 3: Run SPEC Adversary

Run the newly written spec-adversary agent on engines/normalization/SPEC.md.
Commit output as reference/SPEC_ADVERSARY_NORMALIZATION.md.

## Step 4: Commit Everything

All 7 new agents + any updated agents + SPEC adversary output.

## After This

Architect (Claude Chat) reviews all output using kr-reviewing-cc-output.
Then uses kr-gating-transitions to verify all prerequisites for Probe 2 (build).
