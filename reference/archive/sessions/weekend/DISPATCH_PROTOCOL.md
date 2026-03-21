# Weekend Dispatch Protocol

**For:** Owner (Rayane)
**From:** Architect (Claude Chat)
**Purpose:** Step-by-step instructions for dispatching CC between tasks

---

## The CC Work Cycle (Every Task)

```
┌─ PLAN ───────────────────────────────────────┐
│ 1. You tell CC: "Read NEXT.md, use /plan"    │
│ 2. CC produces execution plan                 │
│ 3. You paste the plan to Architect chat       │
│ 4. Architect reviews → approve or comment     │
│ 5. You relay to CC → CC executes              │
└──────────────────────────────────────────────┘
           ↓ CC finishes ↓
┌─ REVIEW ─────────────────────────────────────┐
│ 6. You skim CC's output summary              │
│ 7. You paste summary to Architect chat       │
│ 8. Architect reviews → approve or fix list   │
│ 9. If fixes needed: you relay to CC          │
│ 10. Task done → start next cycle             │
└──────────────────────────────────────────────┘
```

**Why /plan first:** CC's plan reveals misunderstandings of the task BEFORE it spends 2 hours going the wrong direction. S5 lesson: "review the plan before execution, not the code after."

---

## Starting Each Task

### What to tell CC:

**For Task 1 (first task, NEXT.md already in repo):**
```
Read NEXT.md carefully — it was updated since last commit. Pay special attention to 
Task B step 5 (git commit rules) and step 6 (UNSUPPORTED_FORMAT note). 
Use /plan to show me your execution plan before starting. Do NOT execute yet.
```

**For Tasks 2-5 (after swapping NEXT.md):**
```
Read NEXT.md. Use /plan to show me your execution plan before starting. Do NOT execute yet.
```

### What to paste to Architect:

Copy CC's entire plan output. Preface it with:
```
KR Weekend — CC produced this plan for Task N. Review and approve or comment:

[paste CC's plan]
```

### After Architect approves:

Tell CC:
```
Plan approved. Execute.
```

Or if Architect has comments:
```
Architect comments on your plan:
[paste architect comments]

Revise plan, then execute.
```

---

## After CC Finishes Executing

### Step 1: Read CC's final message (30 seconds)

Look for:
- "Done" / "Complete" → proceed to review
- "Stuck on X" / "Need clarification" → paste the question to architect chat
- Error/crash in CC itself → restart CC, tell it to `--resume`

### Step 2: Skim the key output (1 minute)

| Task | Key File to Skim | Red Flags |
|------|-----------------|-----------|
| 1 (Sweeps) | `results/normalization_sweep/CC_ANALYSIS.md` | Crash rate > 5% |
| 2 (Bug Fix) | `results/SWEEP_FIX_SUMMARY.md` + `results/SWEEP_ARCHITECT_REVIEW.md` | ARCHITECT REVIEW items |
| 3 (Re-Sweep) | `results/VERIFICATION_REPORT.md` + `results/CALIBRATION_REPORT.md` | Remaining crash rate > 1% |
| 4 (LLM Probes) | `tests/results/source_engine/phase_e/PHASE_E_LESSONS.md` | Gate abort rate > 20%, cost > €15 |
| 5 (Fixtures) | CC's final message (test count) | Test count decreased |

### Step 3: Send to Architect for review

Paste to Architect chat:
```
KR Weekend — CC finished Task N. Here's the summary:

[paste key output file]

[if relevant: paste SWEEP_ARCHITECT_REVIEW.md]
```

### Step 4: Architect responds with verdict

- **"Approved — move to Task N+1"** → proceed to swap NEXT.md
- **"Fixes needed: [list]"** → relay fixes to CC, wait for CC to complete, then re-check
- **"I need to see [specific file]"** → paste that file to architect

### Step 5: Swap NEXT.md for next task

```powershell
# On your Windows machine, in the kr repo directory:
copy reference\archive\sessions\weekend\TASK_N_NEXT.md NEXT.md
git add NEXT.md
git commit -m "chore: NEXT.md for Weekend Task N"
git push
```

Then start the cycle again (tell CC to read NEXT.md and /plan).

---

## Task Order

```
Task 1 (Sweeps) → Task 2 (Bug Fix) → Task 3 (Re-Sweep) → Task 4 (LLM Probes) → Task 5 (Fixtures)
```

If time runs short, cut from the end. Tasks 1-3 are the core value.

---

## Task Files Location

All pre-written NEXT.md files:
```
reference/archive/sessions/weekend/
  TASK_2_NEXT.md  — Bug Fix Sprint
  TASK_3_NEXT.md  — Verification Re-Sweep + Calibration
  TASK_4_NEXT.md  — Source Engine LLM Probes  
  TASK_5_NEXT.md  — Test Fixture Expansion
```

---

## Emergency Procedures

**CC gets stuck mid-task:**
Tell CC: "Save your progress, commit what you have with prefix 'wip:', write status in results/CC_STATUS.md, then stop."
Paste CC_STATUS.md to architect.

**CC modifies files it shouldn't:**
Check: `git diff engines/*/SPEC*.md engines/*/contracts.py`
If modified: `git checkout engines/*/SPEC*.md engines/*/contracts.py`

**CC exceeds budget (Task 4):**
CC should self-enforce the €15 cap. If you notice it running for >3 hours on Task 4, check in.
