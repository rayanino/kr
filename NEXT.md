# NEXT — Source Engine Validation, Step 3: Targeted LLM Probes

**Governing document:** `engines/source/VALIDATION_PLAN.md`
**Result preservation:** `/RESULT_PRESERVATION.md`

## Previous Steps (all complete)

- **Step 0:** 12/13 fixtures pass with real LLM calls. Cost €1.80. See `engines/source/review/STEP0_RESULTS.md`.
- **Step 1:** Code audit + 6 bug fixes (commit `4b51718`). 768 tests passing.
- **Step 2:** Deterministic sweep on 2,519 books: zero crashes. 5 extraction bugs fixed (commit `8beff68`). title_full 100%, author_name_raw 96.2%.
- **Claude Code inspection:** 5 minor fixes (commit `638a134`).

## Current: Phase C Preparation (hardening before execution)

Phase C is the first validation step that costs real money. It runs the FULL 13-step pipeline (including LLM inference) on 73 owner-selected books. Every API call costs ~$0.15/book. A preventable error that forces re-running wastes ~€10.

### What's been prepared (read these documents in order):

1. **`PHASE_C_TASK_SPEC.md`** — The implementation spec for Claude Code. Contains 5 pre-requisites, processing flow, output structure, budget protection, error handling, and a test checklist.

2. **`PHASE_C_PREFLIGHT_AUDIT.md`** — Audit of every component that touches real money. Found 5 issues (2 fixes, 3 documented non-fixes). Found 2 critical bugs in my own task spec. Contains cost model, risk register.

3. **`PHASE_C_FINAL_SELECTION.md`** — Why each of the 50 originally-selected books was chosen. (Owner provided 73 total with valuable extras like multiple editions.)

4. **`scripts/phase_c_books.txt`** — The 73 book names, grouped by test category.

5. **`tests/fixtures/phase_c_fixture_mappings.json`** — Maps 12 collection books to ground truth fixture keys.

### Pre-requisites for Claude Code (WHY each matters):

**Pre-req 0 (CRITICAL): Fix `build_prompt_context` field-name mismatches.**
WHY: The function that builds the metadata section the LLM sees looks for `muhaqiq_name` and `edition`, but extraction saves `muhaqiq_name_raw` and `edition_raw`. Result: 54% of books have muhaqiq data the LLM NEVER sees. Without fixing, every API call on books with muhaqiqs produces results where the LLM couldn't factor in tahqiq quality. We'd discover this during review and have to re-run all affected books.

**Pre-req 1: Add `temperature=0` to consensus model calls.**
WHY: Default temperature introduces non-determinism and slightly inflates output tokens. For structured JSON classification, temperature=0 is standard practice. Makes results reproducible.

**Pre-req 2: Expose full ConsensusResult in MetadataInferenceResult.**
WHY: `acquire_source` doesn't expose per-model LLM responses. Adding a `_full_consensus_result` field lets the Phase C script capture the complete response from each model (Opus + Command A) for diagnostic analysis. Without this, we can't see what each model individually said — only the consensus output.

**Pre-req 3: Create Format B test fixture.**
WHY: Phase A Bug 2 (colon-in-label, affecting 64 books) was fixed in code but has no unit test. A test fixture prevents regressions.

**Pre-req 4: Create COST_LOG.json.**
WHY: Budget tracking infrastructure. Script refuses to start if estimated cost exceeds remaining budget.

### Critical bugs found in the task spec (self-analysis):

**BUG 1: Monkey-patch targeted wrong Python module.**
The task spec originally said to patch `shared.consensus.src.consensus.evaluate`. This is WRONG. Python's `from X import Y` creates a local reference copy in the importing module. Patching `X.Y` does NOT affect the copy. metadata_inference.py's local `evaluate` reference would still point to the original. FIXED: patch `engines.source.src.engine.infer_metadata` instead, which captures the full MetadataInferenceResult return value.

**BUG 2: Pre-pipeline extraction creates lock that blocks pipeline.**
The task spec originally called `stage_source()` before `acquire_source()` to capture extraction data. But `stage_source()` creates an exclusive `.kr_processing` lock file. When `acquire_source()` internally calls `stage_source()`, it finds the lock and CRASHES. FIXED: use `detect_format()` + `extract_metadata()` directly (read-only, no lock).

### What to do next:

1. **Critically review** all Phase C documents. Look for: remaining bugs in the task spec, inconsistencies between documents, untested code paths, anything that could waste money or produce unusable results.
2. **When satisfied**, hand `PHASE_C_TASK_SPEC.md` + the books to Claude Code for implementation.
3. **Claude Code** implements pre-requisites, writes `scripts/run_phase_c.py`, tests on 2 books.
4. **Owner** runs the validated script on all 73 books on his Windows machine.
5. **Review** results in Claude Chat using kr-evaluate (5 books per session).

**Budget:** ~€98 remaining (€100 ceiling − €1.80 spent in Step 0). Step 3 estimate: €10-15. Step 3 ceiling: €50.
