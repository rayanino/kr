---
name: kr-reviewing-cc-output
description: "Reviews Claude Code deliverables against KR architecture and SPEC. ALWAYS invoke when Claude Code completes a task. Do not approve CC work without structured adversarial review first."
---

# KR Claude Code Review — Mandatory 3-Pass, Multi-Round

When Claude Code finishes a task, the Architect's review is the quality gate between "done" and "we can proceed." The source engine's code audit found 6 bugs in 1,500 lines that all tests missed — because tests written by the same agent as the code tend to verify what the code does, not what the SPEC says it should do. This skill ensures the review catches what tests miss.

**CRITICAL: REVIEW_PROTOCOL.md (in the repo) is the AUTHORITY. This skill triggers the workflow; the protocol defines the rules. Always pull the repo and read the protocol before starting. If this skill and the protocol conflict, the protocol wins.**

**QUALITY AXIOM:** The architect is the sole quality gate. The owner is not a safety net. The owner says "continue" and does not check output. Every error the architect misses reaches the pipeline. See `reference/protocols/QUALITY_AXIOM.md`.

## When this skill activates

Whenever Claude Code completes any deliverable: a probe, a build session, agent definitions, SPEC revisions, or any committed work. The trigger is the owner saying "Claude Code finished" or "it's done" or the Architect seeing new commits.

## Mandatory multi-round structure (RULE 8)

Reviews are NEVER crammed into one response. The structure is enforced:

### Round 1 → Pass 1 (Structural)

1. Pull repo, read NEXT.md, read commit diffs.
2. Copy REVIEW_CHECKLIST_TEMPLATE.md to reviews/.
3. Open and read every modified file **in full** (RULE 7: if truncated, request the rest). After reading each file, state the count of functions/patterns/classes and verify by grep.
4. Run all tests. Run cross-engine contract checker.
5. SPEC cross-reference: every function traces to a § rule.
6. Cross-engine boundary check for every modified contract type.

**→ End response. Context switch forces fresh eyes for adversarial probing.**

### Round 2 → Pass 2 (Adversarial)

1. 3+ probing scripts with constructed inputs (regex boundaries, state machine traces, data flow).
2. 2+ fixture semantic spot-checks with printed Arabic text.
3. **SPEC concrete example trace (RULE 5):** For EVERY SPEC section with a worked example, trace it through the implementation. Print actual output. Compare field-by-field. Document every divergence as either a finding or a documented deferred capability. This is the single most obvious test — Session 4 proved that skipping it misses real limitations.
4. Cross-engine data flow verification.
5. Edge case probes.

**→ End response. Verdict is NEVER in the same response as probes.**

### Round 3 → Pass 3 (Self-Verification + Verdict)

1. **Verify own claims (RULE 6):** For every factual claim in Passes 1-2 ("N patterns," "not implemented," "correctly handles X"), run a tool call to verify. grep -c for counts. grep for existence. No assertions from memory.
2. **Check for rationalization:** Re-read every "not a finding" conclusion. Ask: am I explaining this away because fixing it is hard?
3. Draft Notes — each verified against code before writing.
4. Fill the checklist. Every checkbox checked. Commit.
5. **Deliver verdict.** The verdict is NEVER in the same response as Pass 2 probes.

## Verdicts

**The REVIEW_PROTOCOL.md is the authority on verdicts, not this skill.**

Two verdicts only: ACCEPT or BLOCKED.

ACCEPT means: zero unfixed findings in the repo. All fixes committed and pushed. The review checklist (reference/archive/sessions/reviews/review_session_N.md) is filled and committed. The repo is clean RIGHT NOW.

BLOCKED means: at least one finding exists that couldn't be fixed. State what must be fixed. Prepare a fix directive.

BANNED: "ACCEPT WITH FIXES", "non-blocking", "architect action item", "maintenance item", "future cleanup". These are all the same pattern: find problem → defer it → move on. Fix before verdict.

## Session 4 lesson (why 3 rounds exist)

Session 4 review ran 16 adversarial probes and delivered "ACCEPT, zero findings" in a single response. When forced to self-review, three gaps were found: (1) factual error in review notes from reading a truncated file, (2) never traced the SPEC's own concrete example — the most obvious test — missing a real T-2 limitation (L-007), (3) no cooling-off period between probing and judging. The review LOOKED thorough but wasn't.

The multi-round structure works because each round uses a structurally different verification method, and the context break between rounds forces the architect to re-enter fresh rather than continuing in the same frame of mind that produced the initial conclusions. The owner just says "continue" — the quality comes from the architect's mandatory self-verification in Round 3, not from owner intervention.

## After the review

If ACCEPT: commit the filled review checklist, then invoke kr-gating-transitions.
If BLOCKED: tell the owner to send Claude Code the specific fixes, then re-review (start a fresh checklist for the re-review).
