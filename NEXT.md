# NEXT — Source Engine Validation, Step 2: Deterministic Sweep

**Governing document:** `engines/source/VALIDATION_PLAN.md` — read this first in every new session.
**Result preservation:** `/RESULT_PRESERVATION.md` — every test result is a reusable artifact, not disposable validation. Read this before any pipeline run.

**Previous steps:**
- Step 0 COMPLETE — 12/13 fixtures pass. See `engines/source/review/STEP0_RESULTS.md`.
- Step 1 COMPLETE — Code audit + 6 bug fixes. See `engines/source/review/CODE_AUDIT_SESSION6.md`. Fixes in commit `4b51718`. 768 tests passing, 22 skipped.

**Current step:** Step 2 — Deterministic Sweep (Phase A). Run Steps 1–3 of the pipeline (staging → format detection → extraction) on all 2,519 Shamela books. No LLM calls. €0 cost.

**What to do:**

1. **Write `scripts/run_phase_a.py`** — a script that:
   - Takes a path to the unzipped Shamela collection directory as argument
   - For each `.htm` file or multi-volume directory: runs staging, format detection, and metadata extraction (Steps 1–3 only — no LLM inference, no freezing, no registration)
   - Also computes SHA-256 hashes and checks for duplicates against an empty registry
   - Catches all exceptions and produces structured error output (SPEC §7 error codes)
   - Writes one JSON result per book to `tests/results/source_engine/phase_a/`
   - Writes `PHASE_A_SUMMARY.json` with aggregate statistics

2. **Owner downloads the collection** (1.3 GB zip from Google Drive link in `reference/SHAMELA_COLLECTION.md`), unzips to a local directory, and runs the script.

3. **Review results** in a Claude Chat session using kr-evaluate.

**Success criteria (from VALIDATION_PLAN.md):**
- 0 crashes (every file either extracts or produces a structured error code)
- No uncaught exceptions (every failure uses SPEC §7 error codes)
- Owner spot-checks 20 random results for extraction correctness

**GO/NO-GO:** 0 crashes. 20/20 spot-checks correct. All error codes match SPEC §7.

**Important context:**
- 263 of 2,519 books had filenames exceeding filesystem limits during the owner's original export (reference/SHAMELA_COLLECTION_AUDIT.md). The script must handle long filenames gracefully.
- The Shamela Collection Audit (reference/SHAMELA_COLLECTION_AUDIT.md) provides empirical data on the full collection: field frequencies, structural variants, quality anomalies. Required reading before writing the script.
- Step 2 does NOT run Steps 4–13 (no LLM, no freezing, no registration). This is a pure extraction test.
- The 3 non-blocking fixes from the code audit (structural_format default, genre chain log, staging cleanup log) were NOT implemented. They are low priority but can be done opportunistically.

**After Step 2:** Fix any crashes or extraction bugs found. Then Step 3 (targeted LLM probes on 25–30 books, ~€5–10).
