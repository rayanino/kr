# NEXT — Source Engine Validation, Step 3: Targeted LLM Probes

**Governing document:** `engines/source/VALIDATION_PLAN.md` — read this first in every new session.
**Result preservation:** `/RESULT_PRESERVATION.md` — every test result is a reusable artifact, not disposable validation. Read this before any pipeline run.

**Previous steps:**
- Step 0 COMPLETE — 12/13 fixtures pass. See `engines/source/review/STEP0_RESULTS.md`.
- Step 1 COMPLETE — Code audit + 6 bug fixes. See `engines/source/review/CODE_AUDIT_SESSION6.md`. Fixes in commit `4b51718`. 768 tests passing, 22 skipped.
- Step 2 COMPLETE — Deterministic sweep on 2,519 books: zero crashes, zero errors. 5 extraction bugs found and fixed (commit `8beff68`). Post-fix: title_full 100%, author_name_raw 96.2%, zero false muhaqiqs. See `engines/source/review/PHASE_A_LESSONS.md`.
- Claude Code deep inspection: 5 minor fixes in commit `638a134` (lock tracking, structural_format default, logging).

**Current step:** Step 3 — Targeted LLM Probes (Phase C). Run full pipeline (with LLM inference) on 73 owner-selected books. ~€10-12 estimated.

**Phase C preparation status (as of commit 1155122):**

Three governing documents prepared by Claude Chat (Architect):
1. `PHASE_C_TASK_SPEC.md` — Complete implementation spec for Claude Code. 5 pre-requisites (numbered 0-4), processing flow, output structure, budget protection, error handling, test checklist.
2. `PHASE_C_FINAL_SELECTION.md` — 50-book selection rationale (owner provided 73 total with extras).
3. `PHASE_C_PREFLIGHT_AUDIT.md` — Full audit of everything touching real money. 2 critical bugs found and fixed in the task spec. Cost model, risk register.

Books ready:
- `scripts/phase_c_books.txt` — 73 book names
- `tests/fixtures/phase_c_fixture_mappings.json` — 12 books that map to ground truth fixtures
- Owner has the books as a zip on Google Drive (172 MB, 415 .htm files)

**Pre-requisites for Claude Code (do these before any API call):**
0. CRITICAL: Fix `build_prompt_context` field-name mismatches (muhaqiq_name_raw, edition_raw) + add 5 missing fields
1. Add `temperature=0` to `_call_model` in `shared/consensus/src/consensus.py`
2. Expose full ConsensusResult in `MetadataInferenceResult` (`_full_consensus_result` field)
3. Create Format B test fixture (`tests/fixtures/shamela_real/13_format_b/`)
4. Create `tests/results/source_engine/COST_LOG.json`

**Critical bugs found and fixed in the task spec (self-analysis):**
- BUG 1: Monkey-patch targeted wrong Python module (consensus_mod.evaluate instead of engine_mod.infer_metadata). Python `from X import Y` creates a local copy.
- BUG 2: Pre-pipeline `stage_source()` creates lock that blocks `acquire_source()`. Fixed to use `detect_format()` + `extract_metadata()` directly.

**What to do next:**
1. Continue hardening Phase C preparation in Claude Chat (review all documents critically)
2. Consider agent team architecture for Claude Code execution (each agent runs a book)
3. Once fully hardened, hand everything to Claude Code for implementation
4. Owner runs the validated script on 73 books
5. Review results in Claude Chat (5 books per session, using kr-evaluate)

**Budget:** ~€88 remaining (€100 - €1.80 Step 0 - ~€10 Step 3 estimate). Step 3 budget: €10-15.
