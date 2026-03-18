---
name: kr-reviewing-cc-output
description: Reviews Claude Code deliverables against KR architecture and SPEC. ALWAYS invoke when Claude Code completes a task. Do not approve CC work without structured adversarial review first.
---

# KR Claude Code Review

When Claude Code finishes a task, the Architect's review is the quality gate between "done" and "we can proceed." The source engine's code audit found 6 bugs in 1,500 lines that all tests missed — because tests written by the same agent as the code tend to verify what the code does, not what the SPEC says it should do. This skill ensures the review catches what tests miss.

**CRITICAL RULE: There are exactly TWO verdicts. ACCEPT (zero findings) or BLOCKED (any findings). "ACCEPT WITH FIXES" is BANNED. "Non-blocking findings" are BANNED. If a finding was worth writing down, it blocks. This rule exists because the Architect once found 15 real problems, classified 12 as "non-blocking," approved the transition, and the errors cascaded. Every finding gets fixed. No shortcuts. No deferrals.**

## When this skill activates

Whenever Claude Code completes any deliverable: a probe, a build session, agent definitions, SPEC revisions, or any committed work. The trigger is the owner saying "Claude Code finished" or "it's done" or the Architect seeing new commits.

## Protocol

### Step 1: Inventory deliverables

Procedural: pull the repo, read the commit log, diff each commit, list every file created or modified. Compare against what NEXT.md requested.

Template:
```
## Deliverables inventory

NEXT.md requested:
- [ ] [deliverable 1] → [produced? path?]
- [ ] [deliverable 2] → [produced? path?]

Unexpected work (not in NEXT.md):
- [file] — [reason it exists]

Missing (requested but absent):
- [deliverable] — [this is a finding]
```

Criteria: every item in NEXT.md must map to a produced file. Missing items are findings. Unexpected items need investigation (legitimate scope discovery or scope creep?).

### Step 2: Read every produced file

Procedural: open each file with the view tool. Read it section by section — not skimming, not summaries, the actual content.

Criteria: after reading a file, you should be able to state one specific concern about it. If you can't, you read too fast. Re-read with the question: "If this were implemented literally, what would go wrong?"

Guardrail: reading the probe results report is not a substitute for reading the underlying audit files, agent definitions, or code. The report summarizes — the files contain the truth.

### Step 3: Cross-reference against governing documents

Procedural: for each deliverable, check alignment with the relevant governing documents (AGENT_ARCHITECTURE.md, Blueprint, KNOWLEDGE_INTEGRITY.md, SILENT_FAILURES.md, the engine SPEC). Open each governing document — do not rely on memory of what it says.

The minimum set of cross-references:
1. The engine's SPEC.md — does the deliverable match the behavioral rules?
2. The engine's contracts.py — do data structures align?
3. reference/AGENT_ARCHITECTURE.md — does the deliverable fit the agent/phase structure?
4. The upstream and downstream engine contracts — does the deliverable preserve contract boundaries?
5. KNOWLEDGE_INTEGRITY.md threats T-1 through T-7 — for each code change, does it introduce or fail to prevent: T-1 (silent text corruption), T-2 (attribution error), T-3 (taxonomic misplacement), T-4 (context loss), T-5 (synthesis hallucination), T-6 (metadata poisoning), T-7 (duplication)? This check is not optional — a code change that passes all tests but introduces a T-2 path (wrong author attribution) is MORE dangerous than one that crashes.

Criteria: any misalignment is a finding, even if the deliverable "looks correct." The governing documents define correct — not the reviewer's impression.

### Step 4: Run tests and verification commands

Procedural: run the verification commands from the NEXT.md that governed this CC session. Then run the full existing test suite to check for regressions.

```bash
# 1. Run NEXT.md verification commands (copied from the session's NEXT.md)
[paste each command and run it]

# 2. Run existing test suite for regressions
python -m pytest engines/{engine}/tests/ -v

# 3. If the engine imports from other engines, check those tests too
python -m pytest engines/ -v --ignore=engines/source/tests/results 2>&1 | tail -30
```

Criteria: any test failure is a finding. Verification command failures are blocking findings. Regression failures in other engines are blocking findings.

### Step 5: Adversarial probing

For agent definitions: "Would this agent catch real errors, or would it produce correct-looking output that misses problems? Is the prompt specific enough to prevent improvisation?"

For code: "What input would break this? What happens when the LLM returns garbage? Are error paths tested? What about Arabic text with diacritics — does the code handle combining characters correctly?"

For SPEC changes: "Did the fix address the root cause or just the symptom? Did it introduce new inconsistencies? Are any §9.1 items now stale?"

For reports: "Does the data support the conclusions? What's the weakest claim?"

### Step 6: Verdict

**Two verdicts only. No exceptions.**

Template:
```
## Review verdict: ACCEPT

Zero findings. [State what you verified to reach this conclusion — if this section is short, you didn't verify enough.]
```

OR:

```
## Review verdict: BLOCKED

Findings (ALL are blocking — there is no non-blocking category):
1. [finding — file — what's wrong — exact fix required]
2. ...

What CC must do: [specific fix directive, ready for the owner to paste to CC]
```

Criteria: if zero findings in a substantial deliverable (>100 lines changed), the review was too shallow. The source engine had ~1 bug per 250 lines. Finding nothing in a large deliverable is a signal to re-read, not a signal of quality.

## Example: a real finding

Reviewing Probe 1, the integrity audit found that both SPEC auditors missed a `NORM_FOOTNOTE_CLASSIFICATION_FAILED` error code. This was caught because the integrity auditor applied Lens 4 (error path completeness) to a section both auditors had reviewed. The finding was real — pattern 6 (missing error path) applied to §4.B.4. Neither auditor caught it because their checklist scopes didn't include "newly created fields from applied fixes."

This is the kind of finding this review should produce: specific, traceable, with a clear fix.

## After the review

If ACCEPT: invoke `kr-gating-transitions` to verify the phase transition prerequisites (if transitioning). If continuing within the same phase, write the next session's NEXT.md via `kr-preparing-cc-handoffs`.

If BLOCKED: write a fix directive and give it to the owner to send to CC. Re-review after CC pushes the fix. Do not write the next session's handoff until the current session is ACCEPTED.
