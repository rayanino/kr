# Source Engine Validation Plan — Post-Session 6

**Status:** ACTIVE — governs all testing from Session 6 completion through source engine validation
**Derived from:** `engines/source/TESTING_PROTOCOL.md` (base plan), adapted to current state
**Budget ceiling:** €80-100 total API credits across all phases
**Date:** 2026-03-10

---

## Current State

- **Engine code:** Complete. engine.py (658 lines), logger.py (115 lines), all modules built.
- **Tests:** 758 passing, 22 skipped, 0 failures.
- **Code review:** 6 bugs found and fixed in post-Session-6 review (see commit `e3e22b9`).
- **Integration run:** NOT YET DONE. No real LLM calls have been made against the pipeline.
- **Blocking conditions:** CG-1 (confidence calibration) and CG-5 (author complementarity) unresolved — require real LLM output.

---

## Step 0: 13-Fixture Integration Run (~$1-2) — ✅ COMPLETE

**Status:** GO — 12/13 pass. See `engines/source/review/STEP0_RESULTS.md`.

**Purpose:** First end-to-end pipeline test with real LLM calls. Resolves the two formal blocking conditions.

**What runs:** Full pipeline (Steps 1-13) on all 13 fixtures (12 Shamela + 1 plain text) with real API calls to Opus 4.6 and Command A.

**Script:** `scripts/run_session6_integration.py`

**Environment:**
```bash
export ANTHROPIC_API_KEY="..."
export OPENROUTER_API_KEY="..."
python scripts/run_session6_integration.py
```

**Output:** `tests/results/source_engine/session6/` — one JSON per fixture + SESSION6_SUMMARY.json

**What to check:**
- Compare each result against `tests/fixtures/GROUND_TRUTH.json` (13 entries)
- Fill in `CONFIDENCE_ANALYSIS.md` from real confidence scores (CG-1)
- Fill in `AUTHOR_COMPLEMENTARITY.md` from real per-model outputs (CG-5)

**GO/NO-GO:** 12+ of 13 ground truth checks pass → proceed. Fewer than 10 → debug. Any crash → fix and re-run.

---

## Step 1: Code Audit — Phase B (€0)

**Purpose:** Find logic bugs that unit tests miss because the tests were written by the same agent as the code.

**Method:** Claude Chat session (not Claude Code). Architect reads each module against the SPEC.

**Checklist:**

1. **Consensus retry flow.** Does `infer_metadata` pass `simplified_messages` to `evaluate()`? Does the fallback model (GPT-5.4 via OpenRouter) actually get called when both primary models fail? Trace from engine.py → metadata_inference.py → consensus.py.

2. **Registration atomicity.** The rollback logic restores from `.bak` if registry JSON is corrupt. What if `.bak` is also corrupt? Current code silently fails (`except OSError: pass` in `_rollback_registries`). This can lead to empty registries and scholar duplicates. **Expected finding: needs fix.**

3. **Concurrent scholar updates.** `lookup_or_register_author` in engine.py Step 6 reads scholars.json without a file lock, then may register a new scholar. Two simultaneous intakes could both create records for the same author. File locking currently only applies during `register_source` (Step 12), not during author registration (Step 6). **Expected finding: needs fix.**

4. **Human gate auto-approve.** Does `auto_approve=True` use the same code path as real owner review? Verify `create_checkpoint()` → `resolve()` with status `auto_approved`.

5. **Validation check ordering.** Does Check 5e (genre↔multi-layer auto-correction) propagate before Check 6 (multi-layer coherence) runs? Trace through `validate_source_metadata`.

6. **Trust re-evaluation gating.** Trust evaluator uses validated formula (death_date only). SPEC says "prior sources" check applies during re-evaluation on enrichment. Document the extension hook for Stage 2.

7. **[Step 0 finding A1] Validation gate-severity errors ignored.** Engine.py only handles `severity="fatal"` from validation, ignoring `severity="gate"` errors that SPEC §5 says should create human gate checkpoints. Three gate conditions exist: confidence < 0.50 (Check 3), author-science mismatch (Check 5c), multi_layer=true with empty layers (Check 6a). **Expected finding: needs fix.**

8. **[Step 0 finding A4] Name matching punctuation bug.** `normalize_arabic_name` doesn't strip Arabic commas (،) or other punctuation, causing token mismatches. LLM-generated full nasab names include commas (e.g., "الزجاجي، أبو القاسم"). **Expected finding: needs fix.**

9. **[Step 0 finding] `validate_enrichment_passthrough` imported but never called.** D-023 passthrough validation function is imported in validation.py but not wired into any check. Assess whether this is needed for Stage 1 or is a Stage 2 concern.

**Deliverable:** `engines/source/review/CODE_AUDIT_SESSION6.md`

**GO/NO-GO:** All findings fixed or documented as deferred-to-Stage-2 with clear rationale.

---

## Step 2: Deterministic Sweep — Phase A (€0)

**Purpose:** Find every bug that doesn't require an LLM call to discover.

**Prerequisites:**
- Owner downloads Shamela collection (1.3 GB zip from Google Drive link in `reference/SHAMELA_COLLECTION.md`)
- Unzips to a local directory

**What runs:** Steps 1-3 only (staging → format detection → extraction) on all 2,519 files. Plus: hashing and deduplication check against empty registry. No LLM calls. No API costs.

**Script:** `scripts/run_phase_a.py` (to be written by Claude Code)

**Output:** `tests/results/source_engine/phase_a/` — one JSON per book with full extraction results, hashes, and any errors + `PHASE_A_SUMMARY.json`. After review: `PHASE_A_LESSONS.md` documenting bugs found, field distribution patterns, and recommendations for Phase C. Per RESULT_PRESERVATION.md, Phase A results are reusable by the normalization engine for field distribution analysis.

**Success criteria:**
- 0 crashes (every file either extracts or produces a structured error code)
- No uncaught exceptions (every failure uses SPEC §7 error codes)
- Owner spot-checks 20 random results for extraction correctness (titles, authors, publishers match the Shamela metadata card)

**What to fix before Step 3:**
- Every crash → code bug → fix in Claude Code session
- Every unexpected error code → investigate
- Structural variants not handled → extend extractor

**GO/NO-GO:** 0 crashes. 20/20 spot-checks correct. All error codes match SPEC §7.

---

## Step 3: Targeted LLM Probes — Phase C (€10-15)

**Purpose:** Test LLM inference quality and consensus behavior on real diversity.

**Prerequisites:** Steps 0, 1, and 2 complete. Zero known code bugs. Owner has reviewed 20 extraction samples.

**Selection: 73 books** (owner expanded from original 30 to include edition variants, riwayah books, and additional coverage). See `PHASE_C_FINAL_SELECTION.md` for full rationale and `scripts/phase_c_books.txt` for the list.

| Category | Count | Selection Criteria |
|----------|-------|--------------------|
| Fixture regression (Group A) | 14 | 12 with ground truth + 2 alfiyyah editions |
| Genre coverage (Group B) | 16 | All 18 Genre enum values covered, including edition variants |
| Multi-layer (Group C) | 7 | Sharh, hashiyah, false-positive trap, tahqiq pseudo-layer, edition variants |
| Disputed attribution (Group D) | 8 | Disputed, institutional, author-short-only, edition variants |
| Trust calibration (Group E) | 5 | Clearly verified, clearly flagged, borderline, degraded |
| Technical edge cases (Group F) | 6 | Riwayah, minimal content, truncated exports, page mismatches |
| Consensus stress (Group G) | 6 | Obscure, genre-ambiguous, school-dependent, format-ambiguous, edition variants |
| Additional coverage (Group H) | 11 | Same-author pairs, diwan, poetry, massive musnad, edition variants |

**Cost estimate:** 73 books × ~$0.15/book (Step 0 actual) = ~$11. With retries: ~€12. Budget ceiling: €50.

**Output:** `tests/results/source_engine/phase_c/` — per RESULT_PRESERVATION.md protocol:
- Per-book directory with `result.json` (full SourceMetadata), `extraction.json`, `llm_responses/` (raw per-model), `consensus.json`, `ground_truth_comparison.json`
- `PHASE_C_MANIFEST.json` — reusability index (Step 4 skips successfully processed books)
- `PHASE_C_SUMMARY.json` — aggregate statistics including edition-group consistency analysis
- `PHASE_C_LESSONS.md` — bugs found, LLM quality patterns, recommendations for Phase D

**Review workflow:**
- Owner reviews all 73 in ~15 Claude Chat sessions (5 books per session, using kr-evaluate)
- Every finding categorized: CORE GAP / ENGINE BUG / LLM QUALITY / DATA ISSUE
- Each validated result becomes new ground truth → GROUND_TRUTH.json expands from 13 to ~74 entries

**GO/NO-GO:** Zero CORE GAP findings. All ENGINE BUG findings fixed. Confidence thresholds adjusted if needed.

---

## Step 4: Final Validation — Phase D (~200 books, €20-30)

**Purpose:** Final validation of the source engine at scale. Test scaling behavior: scholar registry growth, work deduplication, trust distribution, gate rates. **Secondary purpose:** produce verified structured output that becomes the normalization engine's development input.

**Prerequisites:** Step 3 findings all resolved (3 must-fix bugs from Phase C aggregation report). Owner has reviewed all Phase C results.

**Selection:** ~200 books, random stratified sample:
- Stratified by: Shamela category (proportional), estimated era (pre-1000 AH, 1000-1300, post-1300), with/without muhaqiq
- All Phase C books included (regression check — skipped via manifest if already processed and not needs_rerun)

**Output:** `tests/results/source_engine/phase_d/` — same structure as Phase C per RESULT_PRESERVATION.md. `PHASE_D_MANIFEST.json` covers all ~200 books. Phase C's 73 books included as regression checks. `PHASE_D_LESSONS.md` documents scaling patterns. `MASTER_MANIFEST.json` maps every book processed across all phases to its result.

**Review:** Owner reviews targeted subset:
- All ground truth mismatches
- All human gate triggers
- All consensus disagreements
- 10% random sample of "clean" books
- All trust_score within ±0.05 of the 0.65 boundary

**GO/NO-GO:** Trust distribution reasonable. Gate rate <15%. No systematic scholar duplicates. No CORE GAP. Results verified as correct and reliable.

**After Step 4 passes:** Source engine is validated. The verified results (Phase C + Phase D combined: ~273 books) are saved as structured input for normalization engine development. The source engine code is proven correct and ready to process any Shamela book. Library population is a future activity — it happens only after all 7 engines are validated end-to-end. There is no Step 5.

---

## Cost Tracking

File: `tests/results/source_engine/COST_LOG.json`

```json
{
  "phases": {
    "0": {"books": 13,    "cost_usd": 1.95, "cost_eur": 1.80, "status": "complete"},
    "A": {"books": 2519,  "cost_usd": 0.00, "cost_eur": 0.00, "status": "complete"},
    "C": {"books": 73,    "cost_usd": 0.00, "cost_eur": 0.00, "status": "complete"},
    "D": {"books": 0,     "cost_usd": 0.00, "cost_eur": 0.00, "status": "pending"}
  },
  "total_eur": 1.80,
  "budget_ceiling_eur": 100.00
}
```

Updated after every run. Script refuses to start if remaining budget is below estimated cost.

---

## Key Rules

1. **No run without a saved result file.** Every API call produces a persisted JSON artifact.
2. **No phase starts without the previous phase's GO/NO-GO gate passing.**
3. **Fixes happen between phases, not during.** Run → review → fix → next phase.
4. **Cost log updated before every run.**
5. **Owner reviews happen in Claude Chat with kr-evaluate.** 3-5 result files per turn.
6. **Ground truth expanded incrementally.** Phase C adds ~30 entries, Phase D adds more.
7. **Results are reusable, not disposable.** Phase C/D results are finished products. Later phases skip books already processed. Raw LLM responses saved alongside structured results. See `/RESULT_PRESERVATION.md` for the full protocol.
8. **The 2,519 books are a test sample, not the library.** Processing the full sample is not a validation goal. ~200 diverse books prove reliability. Library population happens after all 7 engines are validated.

---

## Known Vulnerability

This plan assumes the LLM consensus pair (Opus 4.6 + Command A) remains available and stable throughout testing. If either model is deprecated or significantly changed mid-testing, the consensus pair may need re-evaluation using the Phase 2 methodology from STEP2_EVALUATION.md.
