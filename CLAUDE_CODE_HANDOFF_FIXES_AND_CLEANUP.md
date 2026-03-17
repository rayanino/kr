# Claude Code — Defect Fixes + Repo Cleanup

## Context

An adversarial review of `reference/ENGINE_BUILD_BLUEPRINT.md` and
`reference/DECISION_PLAYBOOK.md` found defects the first review pass
(commit 0d95cf5) missed. This session fixes all defects and then
archives stale files. Two parts: (A) fix defects, (B) repo cleanup.

## Read First (in this order)

1. `CLAUDE.md` — repo orientation
2. This file — the task spec
3. Files referenced in each fix below (read right before editing)

---

## Part A: Defect Fixes

### Fix 1 — Blueprint: "4 contract defects" → "5"

**File:** `reference/ENGINE_BUILD_BLUEPRINT.md` ~line 55
**What:** Change "4 contract defects" to "5 contract defects"
**Why:** `reference/CONTRACT_VERIFICATION_REPORT.md` §1 lists 5 defects
(2 field name mismatches + 1 enum gap + 1 undeclared dependency +
1 stale field count). The Blueprint says 4.

### Fix 2 — Blueprint: "10 fields verified" → "12"

**File:** `reference/ENGINE_BUILD_BLUEPRINT.md` ~line 1147
**What:** Change "10 fields verified" to "12 fields verified (9 declared
+ 3 undeclared dependencies)"
**Why:** CONTRACT_VERIFICATION_REPORT §4.1 has 9 rows, §4.2 has 3 rows
= 12 total. "10" matches neither table.

### Fix 3 — Playbook: duplicate source numbering

**File:** `reference/DECISION_PLAYBOOK.md` §6.1
**What:** The last entry is numbered "8." but should be "10." The list
currently goes 1-8, 9, 8. Fix the second "8." to "10."
**Verify:** Read §6.1 after editing — numbers should go 1 through 10
with no duplicates.

### Fix 4 — Blueprint: owner-unavailable recovery conflicts with preference gates

**File:** `reference/ENGINE_BUILD_BLUEPRINT.md` ~line 1039-1043
**What:** The "Owner not providing domain comments" recovery says
"proceed with best assessment after 3 days." Add an explicit
exception: "This does NOT apply to preference gates (edition choice,
curriculum decisions), which block until the owner responds per
KNOWLEDGE_INTEGRITY.md Invariant 5."
**Why:** KNOWLEDGE_INTEGRITY.md says preference gates cannot be
automated. The Blueprint recovery path contradicts this.

### Fix 5 — Create MASTER_MANIFEST.json

**File to create:** `tests/results/source_engine/MASTER_MANIFEST.json`
**What:** Merge Phase C and Phase D manifests into a unified cross-phase
manifest. RESULT_PRESERVATION.md (governing doc, line 110) promises
this file exists. It doesn't.

**Logic:**
1. Read `tests/results/source_engine/e2e_validation/PHASE_C_MANIFEST.json`
2. Read `tests/results/source_engine/phase_d/PHASE_D_MANIFEST.json`
3. For each book that appears in BOTH, keep the Phase D entry (later,
   more complete pipeline)
4. For books only in Phase C, keep the Phase C entry
5. For books only in Phase D, keep the Phase D entry
6. Add a top-level `generated_from` field listing source manifests
7. Add `total_books` count

**Also:** Read the actual manifest files first to understand their
format. They may be simple key-value mappings or structured objects.
Adapt accordingly.

**Also update** `RESULT_PRESERVATION.md` line ~110: change the future
tense "A MASTER_MANIFEST.json is produced" to past tense referencing
the actual file location.

### Fix 6 — Blueprint: stale check 5c example

**File:** `reference/ENGINE_BUILD_BLUEPRINT.md` ~line 803-805
**What:** The example says "check 5c was downgraded from gate to
warning in code but SPEC still said gate." Commit 473a7a9 fixed the
code back to "gate." Add a parenthetical: "(since fixed in commit
473a7a9 — code now matches SPEC)". This preserves the lesson while
being honest that the specific discrepancy no longer exists.

### Fix 7 — Blueprint: "~15 core capabilities" is wrong

**File:** `reference/ENGINE_BUILD_BLUEPRINT.md` ~line 174
**What:** Change "the source engine shipped with ~15 core capabilities"
to "the source engine shipped with 10 core capabilities (§4.A.1
through §4.A.10)."
**Why:** SPEC_CORE.md §4.A has exactly 10 numbered subsections.

### Fix 8 — Blueprint: "~117 commits" scope ambiguity

**File:** `reference/ENGINE_BUILD_BLUEPRINT.md` ~line 960
**What:** Change "~117 commits touching engine code" to "~118 commits
touching the source engine directory (engines/source/)."
**Why:** `git log --oneline -- engines/source/ | wc -l` = 118.
The "~117" was close but the scope was ambiguous.

### Fix 9 — Playbook §9.1: upgrade "inferred" to confirmed

**File:** `reference/DECISION_PLAYBOOK.md` §9.1
**What:** Replace the opening paragraph that says "Inferred behavior
(not confirmed by code reading)" with confirmed behavior based on
reading the actual code.

**The confirmed facts (from reading the code):**
- `engines/source/src/consensus.py` has 4 functions:
  `make_author_agreement_fn` (§6.1), `check_work_agreement` (§6.2),
  `compare_attribution_status` (§6.3), `select_canonical_result`
- `shared/consensus/src/consensus.py` line 343: `agreed` is set by
  calling `agreement_fn(resp_a.parsed, resp_b.parsed)` — which in the
  source engine is the author agreement function
- There are NO agreement functions for genre, ML, or science_scope
- Therefore: `consensus.agreed` reflects ONLY author identification
  agreement. Genre, ML, and science_scope disagreements are invisible
  to the consensus module. This was previously inferred; it is now
  confirmed by code reading.

**New text for §9.1 opening:**
```
**Confirmed behavior (verified by code reading, consensus.py lines
343-346):** The consensus module's `agreed` field reflects ONLY author
identification agreement (via `make_author_agreement_fn`). It does NOT
check genre, ML, or science_scope — these fields have no agreement
function. This is confirmed by the absence of any genre/ML/science
comparison in `engines/source/src/consensus.py` (4 functions: author
agreement, work agreement, attribution status comparison, canonical
result selection) and by `shared/consensus/src/consensus.py` line 343
which calls `agreement_fn` — set to the author agreement function for
the source engine.
```

### Fix 10 — Blueprint: add forward pointers for excluded topics

**File:** `reference/ENGINE_BUILD_BLUEPRINT.md` — final section "What
This Blueprint Does NOT Cover"
**What:** Add file locations for each excluded topic:
1. Stage 2 expansion → "To be defined. Extension hooks documented in
   each engine's §4.B."
2. Agent team architecture → "Discussion pending. See NEXT.md."
3. ENGINE_PROTOCOL → `skills/shared/ENGINE_PROTOCOL.md` (note: defines
   4 steps where Blueprint uses 5 — Blueprint elevates completion
   documentation to its own Step 5)
4. ENGINE_FACTORY_PLAN → "Deferred as over-engineered. Previous draft
   archived."

### Fix 11 — Blueprint: "22 false positives" claim is unverifiable

**File:** `reference/ENGINE_BUILD_BLUEPRINT.md` ~line 47-49
**What:** The claim about "22 false positives during source engine
hardening from matching enum value names as field names" cannot be
traced to any specific incident in the repo. The only "22" count found
is from the SPEC quality checker (VAGUE_QUANTIFIER), not from
verify_metadata_flow.py.

Change to: "this script can produce false positives from matching enum
value names as field names — manually verify each flagged field before
treating it as a real gap"

Remove the specific "22" number since it's unverifiable.

---

## Part B: Repo Cleanup

### Archive Phase D evaluation files

Move from root to `reference/archive/sessions/phase_d/`:
- `PHASE_D_AGGREGATION_REPORT.md`
- `PHASE_D_CRITICAL_REVIEW.md`
- `PHASE_D_EVALUATION_PROTOCOL.md`
- `PHASE_D_PATTERN_ANALYSIS.md`
- `PHASE_D_PROGRAMMATIC_ANALYSIS.md`
- `PHASE_D_REVIEW_PREPARATION.md`
- `PHASE_D_REVIEW_PROMPT.md`
- `PHASE_D_SESSION_A_REPORT.md`
- `PHASE_D_SESSION_BCD_PROMPT.md`
- `PHASE_D_SESSION_B_REPORT.md`
- `PHASE_D_SESSION_C_REPORT.md`
- `PHASE_D_SESSION_D_REPORT.md`
- `PHASE_D_SESSION_ERRATA.md`
- `EVALUATION_QUICK_REFERENCE.md`

### Archive handoff and completed files

Move to `reference/archive/sessions/handoffs/`:
- `CLAUDE_CODE_POST_EVAL_FIXES.md`
- `SESSION_C_HANDOFF.md`
- `SESSION_C_PREPARATION.md`

Move to `reference/archive/`:
- `CONTEXT_BUDGET.md`
- `DOMAIN_ACCURACY_TODOS.md`
- `STEERING.md`
- `VISION.md`

### Keep at root (do NOT move)

- `NEXT.md`
- `CLAUDE.md`
- `KNOWLEDGE_INTEGRITY.md`
- `RESULT_PRESERVATION.md`
- `SILENT_FAILURES.md`
- `OPEN_PROBLEMS.md`

### After moves: broken reference check

```bash
# Get list of moved filenames (basenames only)
# Grep for them in all active .md files at root and reference/
# Fix any broken paths
```

### Update CLAUDE.md if it references moved files

### Update NEXT.md

Replace current content with:

```markdown
# NEXT — Agent Team Discussion

## Current position: Repo cleanup COMPLETE → discuss agent architecture
## What to do: Discuss builder + researcher agent team architecture
## Context: Blueprint, Playbook, and repo are clean. Source engine is
  complete. Normalization engine is next but agent team architecture
  discussion comes first.
## Owner action needed: YES — this is a Claude Chat discussion topic.
```

### Delete this handoff file after completing all tasks

`git rm` this file (`CLAUDE_CODE_HANDOFF_FIXES_AND_CLEANUP.md`) as
part of the final commit. It has served its purpose.

---

## Do NOT Change

- `engines/source/src/` — no engine code changes in this session
- `engines/source/tests/` — no test changes
- `shared/` — no shared module changes
- `engines/source/SPEC_CORE.md` — SPEC is stable
- `engines/source/contracts.py` — contracts are stable

## Verification

After all fixes:
```bash
# Part A verification
grep "5 contract defects" reference/ENGINE_BUILD_BLUEPRINT.md
grep "12 fields verified" reference/ENGINE_BUILD_BLUEPRINT.md
grep "10\." reference/DECISION_PLAYBOOK.md  # verify numbering fix
test -f tests/results/source_engine/MASTER_MANIFEST.json
grep "Confirmed behavior" reference/DECISION_PLAYBOOK.md

# Part B verification
ls *.md  # should show ≤8 files
ls reference/archive/sessions/phase_d/*.md | wc -l  # should be 14
```

## Commits

Two commits:
1. `"fix: 11 defects in Blueprint and Playbook (adversarial review round 2)"`
2. `"chore: repo cleanup — archive Phase D evaluation and stale files"`
