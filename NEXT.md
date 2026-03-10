# NEXT — Source Engine Validation, Step 3: Targeted LLM Probes

**Governing document:** `engines/source/VALIDATION_PLAN.md` — read this first in every new session.
**Result preservation:** `/RESULT_PRESERVATION.md` — every test result is a reusable artifact, not disposable validation. Read this before any pipeline run.

**Previous steps:**
- Step 0 COMPLETE — 12/13 fixtures pass. See `engines/source/review/STEP0_RESULTS.md`.
- Step 1 COMPLETE — Code audit + 6 bug fixes. See `engines/source/review/CODE_AUDIT_SESSION6.md`. Fixes in commit `4b51718`. 768 tests passing, 22 skipped.
- Step 2 COMPLETE — Deterministic sweep on 2,519 books: zero crashes, zero errors. 5 extraction bugs found and fixed (commit `8beff68`). Post-fix: title_full 100%, author_name_raw 96.2%, zero false muhaqiqs. See `engines/source/review/PHASE_A_LESSONS.md`.

**Current step:** Step 3 — Targeted LLM Probes (Phase C). Run full pipeline (with LLM inference) on 25–30 owner-selected books. €5–10 estimated.

**What to do:**

1. **Owner selects 30 books** for diversity coverage (see VALIDATION_PLAN.md §Step 3 for the selection matrix: genre coverage, multi-layer, disputed attribution, edge cases, high-value, modern).
2. **Write `scripts/run_phase_c.py`** — full pipeline run on selected books with real API calls. Saves per-book results following RESULT_PRESERVATION.md protocol: per-book directory with result.json, extraction.json, llm_responses/ (raw per-model), consensus.json, ground_truth_comparison.json. Plus PHASE_C_MANIFEST.json and PHASE_C_SUMMARY.json.
3. **Owner reviews all 30** in Claude Chat sessions (5 per session, using kr-evaluate).
4. **Categorize findings** — CORE GAP / ENGINE BUG / LLM QUALITY / DATA ISSUE.
5. **Fix any ENGINE BUGs** found. Expand GROUND_TRUTH.json from 13 → ~43 entries.

**Known gaps going into Step 3:**
- 96 books lack author_name_raw (only author_short available) — these need LLM inference from text_sample + author_short. Include at least 2 in the 30-book selection.
- No Format B test fixture exists — the Bug 2 colon-split fix in shamela_html.py is untested by unit tests. Create a synthetic Format B fixture during Step 3.
- 3 non-blocking cosmetic issues from Step 1 remain unfixed (duplicate gate checkpoint, empty diagnostic values, staging cleanup log). Fix opportunistically.

**Required environment:**
```bash
export ANTHROPIC_API_KEY="..."
export OPENROUTER_API_KEY="..."
```

**Budget:** €98 remaining. Step 3 budget: €5–10 (30 books × ~€0.10/book + buffer for retries).
