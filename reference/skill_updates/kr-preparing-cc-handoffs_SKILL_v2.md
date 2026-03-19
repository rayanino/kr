---
name: kr-preparing-cc-handoffs
description: "Prepares complete NEXT.md directives for Claude Code sessions. ALWAYS invoke when writing NEXT.md or CC task prompts. Do not hand off work to CC without verified file refs and prereqs."
---

# KR Claude Code Handoff Preparation

Claude Code follows instructions literally. An incomplete handoff produces improvised work. An ambiguous handoff produces wrong work. A handoff referencing stale files produces broken work. This skill ensures every NEXT.md is complete, correct, and adversarially reviewed before Claude Code sees it.

**QUALITY AXIOM:** The architect is the sole quality gate. No one checks the handoff after the architect commits it. If the NEXT.md contains a wrong SPEC reference, a stale line number, an incorrect threshold, or an ambiguous instruction, CC will implement it literally. The resulting bug will enter the pipeline and eventually corrupt the owner's knowledge. See `reference/protocols/QUALITY_AXIOM.md`.

## When this skill activates

Whenever the Architect writes NEXT.md, prepares a Claude Code prompt, or plans what Claude Code should do next.

## Protocol — Two Rounds (QUALITY AXIOM: multi-round)

### ROUND 1: Draft and preliminary checks

#### Step 1: Establish context
Answer four questions from files read in THIS session (not memory):
1. What phase are we entering?
2. What did the previous session produce? (read latest commits)
3. What does AGENT_ARCHITECTURE.md require for this phase?
4. What does the Blueprint require for this step?

#### Step 2: Verify every file reference
For each file in "Read First," verify it exists, check last modified, and confirm content is still relevant. Line number references are especially fragile — verify the lines still contain what you think.

#### Step 3: Write the NEXT.md
Use the standard template (Current position, What to do, Context, Read First, What to Build, Do NOT Do, Verification, After This). Every section must be filled.

#### Step 4: Check prerequisites
- [ ] Every "Read First" file exists in repo right now
- [ ] "What to Build" references specific SPEC sections with line numbers verified in THIS session
- [ ] "Do NOT Do" covers the most likely scope creep paths
- [ ] "Verification" has concrete pass/fail (not "looks good")
- [ ] Every claim about fixture data verified by running code and printing output
- [ ] Every SPEC threshold copy-pasted from SPEC.md with line number

**→ End Round 1. Commit the draft NEXT.md. End the response.**

### ROUND 2: Adversarial verification (separate response)

This round exists because the architect cannot trust their own assessment of the handoff in the same context where they wrote it. Session 4's NEXT.md went through two adversarial rounds and found 22 issues — proving that single-response handoffs miss problems.

#### Step 5: Re-read as Claude Code
Open the committed NEXT.md with the view tool (do NOT rely on memory of what you wrote). Answer:
1. Is there any point where CC would need to make a judgment call not covered by the SPEC?
2. Is there any file CC would need that isn't in "Read First"?
3. Is there any ambiguity about what "done" means?
4. Could CC follow these instructions and produce something wrong that passes verification?
5. Are there any fixture claims or SPEC values I stated without verification?

#### Step 6: Trace data flow
For the key deliverable, trace the input→processing→output flow through the NEXT.md instructions. Does anything get lost? Does any field get assigned from the wrong source?

#### Step 7: Fix and re-commit
Fix any issues found in Steps 5-6. Re-commit. If zero issues found after genuine adversarial reading, state what you checked and why you're confident.

## After the handoff

The committed NEXT.md is what CC reads. There is no review step between the architect's commit and CC's execution. The quality of the handoff IS the quality of CC's output.
