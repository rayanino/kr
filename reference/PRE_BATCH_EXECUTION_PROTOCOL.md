# Pre-Batch Hardening — Autonomous Execution Protocol

## How this works

This protocol drives the pre-batch hardening phase with minimal owner
involvement. The owner's only actions are:

1. Start a new Claude Chat session (or say "continue" in the current one)
2. When prompted: start Claude Code with the provided prompt
3. When prompted: confirm "looks good" or raise concerns
4. Say "continue" to advance between steps

Claude Chat reads NEXT.md at session start, executes the current step,
self-reviews, updates NEXT.md, and commits. The owner never needs to
decide what to do next — the protocol decides.

## Self-Review Protocol (mandatory for every step)

Every step produces work. Every piece of work gets 3 review rounds before
delivery. This is non-negotiable.

**Round 1 — Completeness check.** Re-read the step's requirements. For each
requirement, verify the work product addresses it. List any gaps found.
Fix them before proceeding.

**Round 2 — Adversarial check.** Attack your own work. For each finding or
conclusion: "What if this is wrong? What evidence would disprove it?
What am I assuming?" For each code change specification: "Could this
break something else? What edge case did I miss?" Fix anything found.

**Round 3 — Scope check.** Did you stay within the step's boundaries? Did
you accidentally defer something that should have been caught? Did you
gold-plate something that should be minimal? Did you miss something that
the NEXT step assumes is done? Adjust.

After all 3 rounds, append to the step's output:

```
## Self-Review Summary
- Round 1 (completeness): [what was found and fixed]
- Round 2 (adversarial): [what was challenged and the result]
- Round 3 (scope): [any boundary adjustments]
```

If any round finds a significant issue, the fix gets its own mini-review
(1 round of adversarial check on the fix itself).

---

## Step Sequence

### STEP 1: mypy crash fixes — Claude Code handoff
**Who:** Claude Chat writes prompt → Owner runs Claude Code
**Input:** reference/PRE_BATCH_VERIFICATION_PLAN.md Layer 1
**Output:** Claude Code prompt committed as `CLAUDE_CODE_MYPY_FIXES.md`

Claude Chat actions:
1. Clone repo, read PRE_BATCH_VERIFICATION_PLAN.md
2. Read the mypy errors listed in the plan (crash risks + contract mismatches)
3. Read the actual source files involved to understand the context
4. Write a precise Claude Code handoff prompt specifying:
   - Each crash-risk fix with exact file, line, and the change needed
   - Each contract-mismatch fix with exact file and approach
   - What NOT to fix (type narrowing issues — document only)
   - Test command to run after: `pytest engines/source/tests/ -v`
   - mypy command to verify: `mypy engines/source/src/ --ignore-missing-imports --explicit-package-bases`
   - Expected outcome: 0 crash-risk errors, 0 contract-mismatch errors
5. Run 3-round self-review on the handoff prompt
6. Commit as `CLAUDE_CODE_MYPY_FIXES.md`, update NEXT.md to say:
   "STEP 1 COMPLETE — handoff ready. Owner: run Claude Code in /plan mode,
    read CLAUDE_CODE_MYPY_FIXES.md"
7. Push

Owner action: start Claude Code, point it at the prompt.

**NEXT.md after this step:**
```
## Current step: STEP 1 — OWNER ACTION NEEDED
Run Claude Code in /plan mode. Entry point: CLAUDE_CODE_MYPY_FIXES.md
After Claude Code finishes: say "continue" in Claude Chat.
```

---

### STEP 2: Verify Claude Code's mypy work
**Who:** Claude Chat
**Input:** Claude Code's commit (mypy fixes applied)
**Output:** Verification report appended to PRE_BATCH_VERIFICATION_PLAN.md

Claude Chat actions:
1. Clone repo, read NEXT.md
2. Read Claude Code's diff (`git log --oneline -3` then `git diff` the relevant commit)
3. For each fix, verify:
   - Does the fix address the actual mypy error?
   - Could the fix introduce a new bug?
   - Is the fix minimal (no unnecessary changes)?
4. Check: did Claude Code run the test suite? Did all tests pass?
5. Check: did Claude Code run mypy? How many errors remain?
6. If remaining mypy errors are type-narrowing only → acceptable
7. If crash risks or contract mismatches remain → write a follow-up prompt
8. Run 3-round self-review
9. Append verification results to PRE_BATCH_VERIFICATION_PLAN.md
10. Update NEXT.md, commit, push

**NEXT.md after this step:**
```
## Current step: STEP 3 — contract boundary verification
Claude Chat: execute STEP 3 from the protocol.
```

---

### STEP 3: Contract boundary verification
**Who:** Claude Chat (this is analysis work, no Claude Code needed)
**Input:** Source engine contracts.py, normalization engine contracts.py + src/
**Output:** Contract verification report committed to reference/

Claude Chat actions:
1. Clone repo
2. Read `engines/source/contracts.py` — identify all output fields of `SourceMetadata`
3. Read `engines/normalization/contracts.py` — identify what it imports from source
4. Read `engines/normalization/src/dispatcher.py`, `normalizers/shamela.py`,
   `normalizers/base.py`, `validation.py` — trace how source output is consumed
5. For each of the 22 fields flagged by verify_metadata_flow.py:
   - Is it a real field the normalization engine reads? → document the gap
   - Is it an enum value matched as a field name? → mark as false positive
6. Specific questions to resolve:
   - Does normalization read death dates? From where?
   - Does normalization use genre? How? String or enum?
   - Does normalization need rihlah/usul_al_fiqh values?
   - Do any Fix 3 fields (death_date_single_model) need downstream propagation?
7. Run 3-round self-review
8. Commit report as `reference/CONTRACT_VERIFICATION_REPORT.md`
9. Update NEXT.md, push

**NEXT.md after this step:**
```
## Current step: STEP 4 — SPEC consistency audit
Claude Chat: execute STEP 4 from the protocol.
```

---

### STEP 4: SPEC consistency audit
**Who:** Claude Chat
**Input:** SPEC_CORE.md, the 4 fix diffs, check_spec_quality.py output
**Output:** SPEC fixes committed directly (if small) or handoff prompt (if large)

Claude Chat actions:
1. Clone repo
2. Read `engines/source/SPEC_CORE.md`
3. Read the 4 fix diffs: `git diff a8b17ff~1..a8b17ff -- engines/source/SPEC_CORE.md`
4. For each fix that modified the SPEC:
   - Does the SPEC description match the actual code implementation?
   - Are there stale references (describing old behavior)?
   - Are new checks (5g, consistency_hashiyah_no_layers) properly documented?
5. Check: does SPEC's genre list match the Genre enum in contracts.py?
6. Triage the 34 HIGH SPEC defects from check_spec_quality.py:
   - Which affect correctness? (wrong threshold, ambiguous rule an implementer
     would misinterpret) → these need fixing
   - Which are style? (vague quantifiers in descriptive text) → document in
     OPEN_PROBLEMS.md, don't fix now
7. If SPEC fixes are small (< 20 lines): make them directly via str_replace,
   commit with clear message
8. If SPEC fixes are large: write a Claude Code handoff prompt
9. Run 3-round self-review
10. Update NEXT.md, commit, push

**NEXT.md after this step:**
```
## Current step: STEP 5 — targeted end-to-end validation
Claude Chat: write the Claude Code handoff for e2e fix validation.
```

---

### STEP 5: Targeted end-to-end validation — Claude Code handoff
**Who:** Claude Chat writes prompt → Owner runs Claude Code
**Input:** PRE_BATCH_VERIFICATION_PLAN.md Layer 4, contract verification results
**Output:** Claude Code prompt committed as `CLAUDE_CODE_E2E_VALIDATION.md`

Claude Chat actions:
1. Clone repo, read PRE_BATCH_VERIFICATION_PLAN.md Layer 4
2. Read contract verification results from STEP 3
3. Write Claude Code handoff prompt specifying:
   - Exactly which 4-5 books to run (with full directory names)
   - What each book tests (which fix, expected behavioral change)
   - How to verify results (specific fields to check in result.json)
   - The control book and what "identical to Phase D" means concretely
   - Budget cap: max €2.00 for this run
4. Include verification script: a Python script Claude Code should write and
   run AFTER the pipeline runs, that automatically checks each expected change
5. Run 3-round self-review
6. Commit as `CLAUDE_CODE_E2E_VALIDATION.md`, update NEXT.md
7. Push

Owner action: start Claude Code, point it at the prompt.

**NEXT.md after this step:**
```
## Current step: STEP 5 — OWNER ACTION NEEDED
Run Claude Code. Entry point: CLAUDE_CODE_E2E_VALIDATION.md
Budget cap: €2.00. After Claude Code finishes: say "continue" in Claude Chat.
```

---

### STEP 6: Verify e2e results + batch design
**Who:** Claude Chat
**Input:** Claude Code's e2e results
**Output:** Batch design document, final NEXT.md pointing to batch execution

Claude Chat actions:
1. Clone repo, read NEXT.md
2. Read Claude Code's e2e results — the verification script output
3. For each fix, verify the expected behavioral change occurred:
   - Fix 1: ملء العيبة genre=rihlah? (was other)
   - Fix 2: النكت triggered gate? (was warning)
   - Fix 3: أساليب بلاغية has death_date_hijri in needs_review_fields?
   - Control: صحيح البخاري matches Phase D?
4. If any fix didn't produce expected change → investigate, write follow-up
5. If all pass → design the final batch:
   - Select ~50 books from the 2,519 sample
   - Prioritize: genres underrepresented in Phase D (sirah, tarikh, mujam,
     rihlah, usul_al_fiqh), multi-volume books, books with complex structures
   - Document selection rationale
   - Write the Claude Code batch handoff prompt
6. Run 3-round self-review on both the verification AND the batch design
7. Commit batch design + handoff as `CLAUDE_CODE_FINAL_BATCH.md`
8. Update NEXT.md
9. Push

**NEXT.md after this step:**
```
## Current step: STEP 6 — OWNER ACTION NEEDED
Run Claude Code. Entry point: CLAUDE_CODE_FINAL_BATCH.md
Budget cap: €10.00. This is the ENGINE TRANSITION final batch.
After Claude Code finishes: say "continue" in Claude Chat.
```

---

### STEP 7: Final batch review + source engine wrap-up
**Who:** Claude Chat
**Input:** Batch results
**Output:** Source engine completion report, NEXT.md pointing to normalization

Claude Chat actions:
1. Clone repo, read batch results
2. Statistical review of batch:
   - Genre distribution — any new genre=other cases?
   - Trust tier distribution — flag rate reasonable?
   - Any crashes or errors?
   - Any patterns suggesting new bugs?
3. Spot-check 5 books from the batch (famous works if possible)
4. Compare batch statistics to Phase D statistics — any drift?
5. If issues found → investigate, possibly write fix prompt
6. If clean → write source engine completion report:
   - Final statistics (total books processed, trust distribution, etc.)
   - Known limitations (documented in OPEN_PROBLEMS.md)
   - What the normalization engine receives (contract summary)
   - Lessons learned
7. Run 3-round self-review
8. Update NEXT.md to point to normalization engine SPEC design
9. Commit and push

**NEXT.md after this step:**
```
## Status: SOURCE ENGINE COMPLETE
## Current task: Begin normalization engine SPEC design
Read reference/ENGINE_FACTORY_PLAN.md for the autonomous build system.
First deliverable: reference/DECISION_PLAYBOOK.md (Oracle's institutional memory).
```

---

## Session Protocol (every Claude Chat session)

```
ON SESSION START:
  1. Clone repo: git clone https://{token}@github.com/rayanino/kr.git
  2. Read NEXT.md — it tells you the current step
  3. Read this protocol file for the step's instructions
  4. Execute the step

ON STEP COMPLETION:
  1. Run 3-round self-review (mandatory, no exceptions)
  2. Update NEXT.md with:
     - What was done
     - What the next step is
     - Whether owner action is needed (Claude Code run)
  3. Commit all changes with descriptive message
  4. Push to GitHub
  5. Tell the owner: "Step N complete. [Next action needed]."

ON ERROR OR UNCERTAINTY:
  1. Do NOT proceed past the uncertain point
  2. Document exactly what's uncertain and why
  3. Update NEXT.md with: "BLOCKED — [description]. Owner: [what's needed]"
  4. Commit and push
  5. Tell the owner what's blocked and what they need to decide
```

## What the owner does

The owner's complete action set:

| Owner sees | Owner does |
|------------|-----------|
| "Step N complete. Continue to Step N+1." | Says "continue" (or starts new chat) |
| "OWNER ACTION NEEDED — run Claude Code" | Opens Claude Code, says "read NEXT.md" |
| "Claude Code finished. Continue." | Says "continue" in Claude Chat |
| "BLOCKED — need your input on X" | Answers the question or says "your call" |
| "Source engine COMPLETE" | Starts new chat for normalization engine |

That's it. No technical decisions. No evaluation. No code review.
The protocol handles everything.
