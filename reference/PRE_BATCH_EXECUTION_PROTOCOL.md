# Pre-Batch Hardening — Autonomous Execution Protocol

## How this works

This protocol drives the pre-batch hardening phase with minimal owner
involvement. The owner's only actions are:

1. Start a new Claude Chat session (or say "continue" in the current one)
2. When prompted: start Claude Code with the provided prompt
3. Say "continue" or "go on" to advance between subtasks

Claude Chat reads NEXT.md at session start, executes the current subtask,
stops, then on "continue" performs the critical review as a separate step.
The owner never needs to decide what to do next — the protocol decides.

---

## Critical Review Protocol

Review is NOT part of the work. It is a SEPARATE STEP that happens AFTER
the work, triggered by the owner saying "continue." This forces a context
break between production and evaluation.

Every piece of work follows this cycle:

```
Subtask A: DO the work
  ↓ (owner says "continue")
Subtask B: REVIEW the work (separate step, tool-grounded)
  ↓ (owner says "continue")
Next subtask or next step
```

### Review requirements (Subtask B)

**Round 1 — Tool-grounded verification.** Do NOT just re-read your output
and think about it. USE TOOLS:
- Re-read the actual source files your work references (view tool)
- Re-run any scripts that verify your claims (bash tool)
- If you made factual claims, web-search to verify them
- If you wrote a handoff prompt, re-read the target files to confirm your
  line numbers, function names, and file paths are still correct
- List every claim in your output. For each: how do you KNOW this? If
  the answer is "I inferred it," verify with a tool.

**Round 2 — Adversarial challenge.** For each conclusion or recommendation:
- "What is the strongest argument this is wrong?"
- "What would I see if the opposite were true?"
- "What am I assuming that I haven't verified?"
- For code change specs: "Could this break an unrelated test? What
  side effect did I miss?"
Fix anything this round surfaces.

**Round 3 — Thinking framework application.** Use the thinking-frameworks
skill explicitly:
- Pre-mortem: "It's one week later and this work caused a problem. What
  went wrong?" Generate 2-3 distinct failure scenarios.
- Scope check: Did I stay within boundaries? Did I defer something that
  should have been caught? Did I over-engineer?
- Second-order effects: What happens downstream when the next step
  consumes this output? Did I create assumptions the next step can't meet?

After all 3 rounds, write a review summary that states:
- What was verified with tools (and what the tools showed)
- What was challenged and survived (or was fixed)
- What failure scenarios were considered
- Confidence level: HIGH / MEDIUM / LOW with reasoning

If confidence is LOW on anything, do NOT proceed. Mark as BLOCKED.

---

## Step Sequence

Each STEP is broken into subtasks. The owner says "continue" between each
subtask. This keeps each unit of work focused and reviewable.

---

### STEP 1: mypy crash fix handoff

**Subtask 1A — Research and write the handoff prompt**
- Clone repo, read PRE_BATCH_VERIFICATION_PLAN.md Layer 1
- Read EVERY source file listed in the mypy errors (not just the plan's
  summary — the actual files). Use the view tool.
- For each crash-risk error: read the surrounding code context (±20 lines),
  understand the actual data flow, determine the minimal fix
- For each contract-mismatch error: read the Pydantic model definition,
  understand which fields have defaults vs. which are required
- Write the Claude Code handoff prompt with:
  - Each fix: file, function, the specific change, WHY this fixes it
  - What NOT to fix (type-narrowing — list them so Claude Code doesn't
    over-fix)
  - Verification commands: pytest + mypy
  - Expected outcome
- Stop. Tell owner: "Handoff prompt drafted. Say 'continue' for review."

**Subtask 1B — Critical review of the handoff prompt**
- Execute the 3-round review protocol (above)
- Specifically: re-read each source file AGAIN and verify the fix
  specifications are still correct (files may have changed since the
  plan was written — commit a8b17ff modified these files)
- Verify: does the handoff prompt reference the correct line numbers
  AFTER Claude Code's 4-fix commit?
- Commit as `CLAUDE_CODE_MYPY_FIXES.md`, update NEXT.md, push
- Tell owner: "Step 1 complete. Run Claude Code with CLAUDE_CODE_MYPY_FIXES.md"

---

### STEP 2: Verify Claude Code's mypy work

**Subtask 2A — Read and analyze Claude Code's changes**
- Clone repo, read Claude Code's diff
- For EACH fix in the diff:
  - Does the fix address the mypy error?
  - Read the surrounding code: could this fix break anything?
  - Is the fix minimal?
- Check test results and mypy results from Claude Code's output
- Write a verification report
- Stop. Tell owner: "Verification drafted. Say 'continue' for review."

**Subtask 2B — Critical review of the verification**
- Execute 3-round review protocol
- Specifically: re-run mypy yourself if possible (install + run)
- If mypy can't run in this environment, verify by reading the exact
  code lines Claude Code changed and manually checking the types
- Append verification to PRE_BATCH_VERIFICATION_PLAN.md
- Update NEXT.md, commit, push
- Tell owner: "Step 2 complete. Say 'continue' for contract verification."

---

### STEP 3: Contract boundary verification

This step is analysis-heavy. It uses the thinking-frameworks skill
explicitly. Split into 3 subtasks.

**Subtask 3A — Map the source engine output schema**
- Read `engines/source/contracts.py` — the full SourceMetadata class
- Read `engines/source/contracts.py` — ScholarAuthorityRecord, WorkRegistryEntry
- List every field the source engine produces, organized by:
  - Per-book output (result.json → SourceMetadata)
  - Scholar registry (scholars.json → ScholarAuthorityRecord)
  - Work registry (works.json → WorkRegistryEntry)
  - Frozen files (frozen source files + hashes)
- Stop. Tell owner: "Source schema mapped. Say 'continue'."

**Subtask 3B — Map the normalization engine input expectations**
- Read `engines/normalization/contracts.py` — what it imports from source
- Read `engines/normalization/src/dispatcher.py` — how it receives input
- Read `engines/normalization/src/normalizers/shamela.py` — what fields it accesses
- Read `engines/normalization/src/normalizers/base.py` — base class expectations
- Read `engines/normalization/src/validation.py` — what it validates
- For each field the normalization engine reads from source output:
  document WHERE it reads it from and HOW it uses it
- Apply thinking framework: for each of the 22 flagged fields, generate
  two competing hypotheses (real gap vs. false positive) and determine
  which has more evidence
- Stop. Tell owner: "Normalization expectations mapped. Say 'continue'."

**Subtask 3C — Critical review and gap resolution**
- Execute 3-round review protocol on BOTH subtask outputs
- Cross-reference: every field normalization reads, does source produce?
- Resolve the specific questions:
  - Death dates: where, how
  - Genre: string or enum, new values
  - Fix 3 fields: propagation needed?
- Write `reference/CONTRACT_VERIFICATION_REPORT.md`
- Update NEXT.md, commit, push
- Tell owner: "Step 3 complete. Say 'continue' for SPEC audit."

---

### STEP 4: SPEC consistency audit

**Subtask 4A — Audit SPEC against code changes**
- Read `engines/source/SPEC_CORE.md` (full file)
- Read the 4-fix diff: `git diff a8b17ff~1..a8b17ff -- engines/source/`
- For each code change, find the corresponding SPEC section:
  - Does the SPEC describe the current behavior (not pre-fix behavior)?
  - Are new checks (5g, consistency_hashiyah_no_layers) documented?
  - Does SPEC's genre list match contracts.py's Genre enum?
- List all inconsistencies found
- Stop. Tell owner: "SPEC audit drafted. Say 'continue'."

**Subtask 4B — Triage SPEC quality defects**
- Run `check_spec_quality.py` (or read cached output from earlier)
- For each of the 34 HIGH defects, classify:
  - CORRECTNESS: an implementer would misinterpret this → fix now
  - STYLE: vague but wouldn't cause wrong code → defer to reference/OPEN_PROBLEMS.md
- List the correctness-affecting defects with proposed fixes
- Stop. Tell owner: "Triage complete. Say 'continue' for review."

**Subtask 4C — Critical review and apply fixes**
- Execute 3-round review protocol on BOTH the audit and the triage
- For each proposed SPEC fix: re-read the corresponding code to verify
  the SPEC change matches what the code actually does
- Apply small fixes (< 20 lines) directly via str_replace
- If large fixes needed: write a Claude Code handoff prompt
- Update NEXT.md, commit, push
- Tell owner: "Step 4 complete. Say 'continue' for e2e validation handoff."

---

### STEP 5: End-to-end validation handoff

**Subtask 5A — Design the validation and write the handoff**
- Read PRE_BATCH_VERIFICATION_PLAN.md Layer 4
- Read contract verification results from Step 3
- For each target book, verify the directory name exists in the Shamela
  sample: `ls "C:\Users\Rayane\Desktop\kr\shamela export samples\"` (or
  the book list file in the repo)
- Write the Claude Code handoff prompt with:
  - Exact book directory names (verified they exist)
  - Per-book: which fix it tests, expected behavioral change, specific
    field to check in result.json
  - A verification script that Claude Code writes and runs automatically
  - Budget cap: €2.00
  - Control book comparison criteria
- Stop. Tell owner: "Handoff drafted. Say 'continue' for review."

**Subtask 5B — Critical review of the handoff**
- Execute 3-round review protocol
- Specifically: verify book directory names against the actual Shamela
  collection file (reference/exhaustive_collection... or the repo copy)
- Verify that the expected behavioral changes are correct by re-reading
  the fix code (not the fix description — the ACTUAL code)
- Commit as `CLAUDE_CODE_E2E_VALIDATION.md`, update NEXT.md, push
- Tell owner: "Step 5 complete. Run Claude Code with CLAUDE_CODE_E2E_VALIDATION.md"

---

### STEP 6: Verify e2e results

**Subtask 6A — Analyze e2e results**
- Clone repo, read Claude Code's verification script output
- For each fix, verify the expected change occurred
- If any fix didn't work: investigate root cause, don't just note it
- Stop. Tell owner: "E2e verification analyzed. Say 'continue' for review."

**Subtask 6B — Critical review of e2e verification**
- Execute 3-round review protocol
- Specifically: read the actual result.json files Claude Code produced
  (not just the verification script's summary) to confirm the script
  checked the right things
- Update NEXT.md, commit, push
- Tell owner: "Step 6 complete. Say 'continue' for batch design."

---

### STEP 7: Final batch design

**Subtask 7A — Design the batch**
- Read Phase D results: genre distribution, trust distribution, gaps
- Read the Shamela collection list (exhaustive .htm book file)
- Select ~50 books optimizing for:
  - Genres underrepresented in Phase D (sirah, tarikh, mujam, rihlah,
    usul_al_fiqh — 0-2 examples each currently)
  - Multi-volume books (normalization engine needs these)
  - Mix of classical and modern works
  - Books with complex structures (multi-layer, versified)
- Document selection rationale for each category
- Write the Claude Code batch handoff prompt
- Stop. Tell owner: "Batch design drafted. Say 'continue' for review."

**Subtask 7B — Critical review of batch design**
- Execute 3-round review protocol
- Pre-mortem: "The batch ran and the normalization engine can't use the
  output. What went wrong?" → verify book selection covers normalization's
  needs
- Verify every selected book directory name exists
- Commit as `CLAUDE_CODE_FINAL_BATCH.md`, update NEXT.md, push
- Tell owner: "Step 7 complete. Run Claude Code with CLAUDE_CODE_FINAL_BATCH.md"

---

### STEP 8: Final batch review

**Subtask 8A — Statistical analysis of batch results**
- Read batch summary JSON
- Analyze: genre distribution, trust distribution, error rate, crash count
- Compare to Phase D statistics — any unexpected drift?
- Spot-check 5 books (prioritize famous works for easy verification)
- Stop. Tell owner: "Batch analysis done. Say 'continue' for review."

**Subtask 8B — Critical review of batch analysis**
- Execute 3-round review protocol
- Specifically: for each spot-checked book, do a quick web search to
  verify the author attribution is correct
- If issues found → document and assess severity
- Stop. Tell owner: "Review complete. Say 'continue' for wrap-up."

**Subtask 8C — Source engine completion report**
- Write the completion report:
  - Final statistics
  - Known limitations (from reference/OPEN_PROBLEMS.md)
  - Contract summary (what normalization engine receives)
  - Lessons learned
- Run 3-round review on the report
- Update NEXT.md to point to normalization engine
- Commit and push
- Tell owner: "SOURCE ENGINE COMPLETE. Start new chat for normalization."

---

## Session Protocol

```
ON SESSION START:
  1. Clone repo: git clone https://{token}@github.com/rayanino/kr.git
  2. Read NEXT.md — it tells you the current step AND subtask
  3. Read this protocol file for the subtask's instructions
  4. Execute the subtask
  5. STOP and wait for owner to say "continue"

WITHIN A SESSION (owner says "continue"):
  1. Read NEXT.md to confirm current subtask
  2. Execute the next subtask
  3. STOP and wait

ON SUBTASK COMPLETION:
  1. If this is a "B" subtask (review): commit and push
  2. If this is an "A" subtask (work): do NOT commit yet — review comes next
  3. Update NEXT.md with current subtask position
  4. Tell owner what was done and what "continue" will trigger next

ON SESSION END (context getting long, or natural break):
  1. Update NEXT.md with EXACT position: step number + subtask letter
  2. Document any in-progress findings that would be lost
  3. Commit and push
  4. Tell owner: "Session saved at Step N, Subtask X.
     Start new chat and say 'continue'."

ON ERROR OR UNCERTAINTY:
  1. Do NOT proceed past the uncertain point
  2. Document exactly what's uncertain and why in NEXT.md
  3. Commit and push
  4. Tell owner: "BLOCKED at Step N — [what's needed]"
```

## NEXT.md format

NEXT.md always contains:
```
## Current position: STEP [N] — Subtask [A/B/C]
## What to do: [exact instruction for Claude Chat]
## Context: [any state needed from previous subtask]
## Owner action needed: [yes/no, what]
```

This allows any fresh Claude Chat session to pick up exactly where the
last one left off, even mid-step.

## What the owner does

| Owner sees | Owner does |
|------------|-----------|
| "Subtask done. Say 'continue'." | Says "continue" |
| "Run Claude Code with [file]" | Opens Claude Code, says "read NEXT.md" |
| "BLOCKED — need input on X" | Answers the question |
| "Session saved at Step N. Start new chat." | Starts new chat, says "continue" |
| "SOURCE ENGINE COMPLETE" | Starts new chat for normalization |
