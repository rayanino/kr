# Weekend Dispatch Protocol

**For:** Owner (Rayane)
**From:** Architect (Claude Chat)
**Purpose:** Step-by-step instructions for dispatching CC between tasks

---

## Task Files Location

All pre-written NEXT.md files are at:
```
reference/archive/sessions/weekend/
  TASK_2_NEXT.md  — Bug Fix Sprint
  TASK_3_NEXT.md  — Verification Re-Sweep + Calibration
  TASK_4_NEXT.md  — Source Engine LLM Probes  
  TASK_5_NEXT.md  — Test Fixture Expansion
```

## When CC Finishes a Task

### Step 1: Read CC's final message (30 seconds)

Look for:
- "Done" / "Complete" → proceed
- "Stuck on X" / "Need clarification" → paste the question to architect chat
- Error/crash in CC itself → restart CC, tell it to `--resume`

### Step 2: Check the output (1 minute)

Each task produces a key summary file. Skim it for red flags:

| Task | Key File | Red Flags |
|------|----------|-----------|
| 1 (Sweeps) | `results/normalization_sweep/CC_ANALYSIS.md` | Crash rate > 5%, any "needs architect decision" |
| 2 (Bug Fix) | `results/SWEEP_ARCHITECT_REVIEW.md` | Any bugs classified as ARCHITECT REVIEW |
| 3 (Re-Sweep) | `results/VERIFICATION_REPORT.md` | Remaining crash rate > 1% |
| 4 (LLM Probes) | `tests/results/source_engine/phase_e/PHASE_E_LESSONS.md` | Gate abort rate > 20% |
| 5 (Fixtures) | Check test count: last line of CC output | Test count decreased |

### Step 3: Decide — Green Light or Check With Architect

**GREEN LIGHT** (proceed to next task without architect):
- CC says "Done"
- No ARCHITECT REVIEW items
- No red flags in summary
- No questions from CC

**CHECK WITH ARCHITECT** (paste summary to a new Claude Chat):
- CC flagged items needing design decisions
- Crash rate unexpectedly high
- CC asked questions
- Anything that surprises you

### Step 4: Swap NEXT.md and Start CC (2 minutes)

```powershell
# On your Windows machine, in the kr repo directory:

# Copy the next task's NEXT.md
copy reference\archive\sessions\weekend\TASK_N_NEXT.md NEXT.md

# Commit and push
git add NEXT.md
git commit -m "chore: NEXT.md for Weekend Task N"
git push

# Start CC
# Tell CC: "Start on NEXT.md"
```

Replace N with the next task number (2, 3, 4, or 5).

---

## Task Order

```
Task 1 (Sweeps) → Task 2 (Bug Fix) → Task 3 (Re-Sweep) → Task 4 (LLM Probes) → Task 5 (Fixtures)
```

If time runs short, cut from the end. Tasks 1-3 are the highest value.

## Emergency: CC Gets Stuck Mid-Task

Tell CC:
> Save your progress, commit what you have with the prefix "wip:", and write a brief status in results/CC_STATUS.md. Then stop.

Then paste CC_STATUS.md to the architect chat.

## Emergency: CC Modifies Files It Shouldn't

Check with: `git diff engines/*/SPEC*.md engines/*/contracts.py`
If any of these are modified, tell CC:
> Revert changes to SPEC and contracts files: git checkout engines/*/SPEC*.md engines/*/contracts.py
