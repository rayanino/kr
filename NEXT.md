# NEXT — Step 4 Preparation

## Status: Step 3 COMPLETE → 3 Bug Fixes → Step 4

Phase C (Step 3) evaluated 73 books across 7 sessions. Results: 59 VERIFIED, 17 PLAUSIBLE, 0 FLAG, 0 ESCALATE. Zero author errors. 3 must-fix bugs identified. Full analysis in `PHASE_C_AGGREGATION_REPORT.md`.

---

## CRITICAL FRAMING — READ THIS FIRST

**We are building a 7-engine pipeline, NOT populating a library.** The 2,519 Shamela books on the owner's machine are a local test sample — not the full Shamela collection, not "the library." Library population happens only after all 7 engines are proven end-to-end.

**Step 4 is the FINAL source engine validation step.** There is no Step 5. After Step 4:
- If results are verified correct → source engine is validated → move to normalization engine
- If results reveal new bugs → fix, re-run affected books, verify again

**Step 4 output serves dual purpose:**
1. Final validation proving the source engine is robust and reliable
2. The verified results become structured input for normalization engine development — so the normalization engine has real data to build against from day one

**Test outputs are real products.** Per RESULT_PRESERVATION.md, every API call produces persisted artifacts. Phase C's 73 books are already finished source engine products. Step 4's ~200 books will be too — if they verify clean.

---

## What Must Happen Before Step 4 Runs

### 3 Must-Fix Bugs (Claude Code session)

**Bug 1 — Tahqiq-note ML auto-correction** (PHASE_C_AGGREGATION_REPORT.md §4.1.1)
Opus classifies tahqiq editorial notes as scholarly commentary layers → 3 books have wrong is_multi_layer=true.
Fix: Post-inference validation rule. When layers are only [matn, tahqiq_note] and muhaqiq is present in extraction → auto-correct ML to false and log the override for owner review.

**Bug 2 — Author confidence not surfaced** (§4.1.2)
result.json author confidence is always 1.0 (registry artifact). Actual LLM confidence (0.55–0.99) is buried in llm_responses/.
Fix: Route LLM author_identification_confidence through to result.json.

**Bug 3 — 71% gate-abort rate** (§4.1.3)
Scholar registry starts empty → author-science mismatch fires on every new author.
Fix: Seed the registry with the 45 unique verified authors from Phase C, OR change the mismatch gate to warning-on-first-encounter.

### Step 4 Design (Claude Chat session — THIS IS THE NEXT SESSION'S PRIMARY JOB)

A fresh Claude Chat session must design:

1. **Book selection strategy** (~200 books, random-stratified from the 2,519 sample, excluding the 73 already processed in Phase C)

2. **Review protocol** — must be heavy/rigorous, similar to Phase C's 7-session structure:
   - Phase C used: first review → 4 critical self-check rounds → handoff
   - Step 4 needs a similar autonomous protocol for Claude Chat
   - The joint confidence threshold (ac≥0.95 AND gc≥0.95 = 100% VERIFIED in Phase C) can be used for triage but NOT to skip verification entirely
   - Owner reviews flagged books, disagreements, and a random sample

3. **Verification criteria** — what does "verified correct" mean for Step 4?
   - Bug fixes confirmed working (tahqiq ML, author confidence, gate-abort)
   - No new bug categories discovered
   - Author accuracy maintained at 100%
   - Genre accuracy maintained at 100%
   - Confidence calibration holds at scale

4. **Output structure** — must follow RESULT_PRESERVATION.md protocol exactly

---

## Governing Documents (read in this order)

1. **This file** (NEXT.md) — the task directive
2. **PHASE_C_AGGREGATION_REPORT.md** — full Phase C analysis with 13 findings and 3 must-fix bugs
3. **PHASE_C_ERRATA.md** — corrections to the evaluation framework
4. **RESULT_PRESERVATION.md** — how results must be saved for downstream reuse
5. **CLAUDE_CODE_MEMORY_PRINCIPLES.md** — 33 governing principles

---

## Phase C Artifacts Available

| Artifact | Location | What it contains |
|----------|----------|-----------------|
| All 76 verdicts | `phase_c_collection/PHASE_C_ALL_VERDICTS.json` | Structured data for every evaluated book |
| Per-book results | `tests/results/source_engine/phase_c/{book_name}/` | result.json, extraction.json, llm_responses/, consensus.json |
| Aggregation report | `PHASE_C_AGGREGATION_REPORT.md` | 13 findings, 3 must-fix bugs, 39 ground truth candidates |
| Session reports | `PHASE_C_SESSION1_REPORT.md` through `SESSION7_REPORT.md` | Individual evaluation sessions |
| Errata | `PHASE_C_ERRATA.md` | Framework corrections (author confidence bug, consensus limitations) |

---

## Budget

| Item | Cost |
|------|------|
| Spent (Steps 0–3) | ~€10 |
| Step 4 (~200 books) | ~€15–25 |
| Remaining for normalization engine + beyond | ~€65–75 |
| Total budget | €100 |

---

## What Comes After Step 4

Source engine validated → normalization engine development begins.

The normalization engine will consume source engine output (the verified Step 4 results) as its development input. It does NOT wait for "all 2,519 books" — it works with whatever verified results exist.

The sequence of remaining engines: Source ✅ → Normalization → Indexing → Navigation → Teaching → Discovery → Owner Interface. Each engine must be rock-solid before the next starts.
