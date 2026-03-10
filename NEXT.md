# NEXT — Source Engine Validation, Step 3: Targeted LLM Probes

**Governing document:** `engines/source/VALIDATION_PLAN.md` — read this first in every new session.
**Result preservation:** `/RESULT_PRESERVATION.md` — every test result is a reusable artifact, not disposable validation. Read this before any pipeline run.

**Completed steps:**
- Step 0 COMPLETE — 12/13 fixtures pass. See `engines/source/review/STEP0_RESULTS.md`.
- Step 1 COMPLETE — Code audit + 6 bug fixes. See `engines/source/review/CODE_AUDIT_SESSION6.md`. Fixes in commit `4b51718`.
- Step 2 COMPLETE — Deterministic sweep: 2,519/2,519 success, 5 extraction bugs fixed (commit `8beff68`), رواية field mapping added (commit `bd45baa`). Pre-Step-3 audit: 5 code-level fixes (B1-B5) applied, 548 tests passing, 0 failures.

**Current step:** Step 3 — Targeted LLM Probes (Phase C). Run full pipeline (with LLM inference) on 25–30 owner-selected books. €5–10 estimated.

**Budget:** EUR 5-10 (LLM inference costs for consensus pair: Command A + Opus 4.6).

1. **Owner selects 30 books** for diversity coverage (see VALIDATION_PLAN.md §Step 3 for the selection matrix: genre coverage, multi-layer, disputed attribution, edge cases, high-value, modern).
2. **Write `scripts/run_phase_c.py`** — full pipeline run on selected books with real API calls. Saves per-book results following RESULT_PRESERVATION.md protocol: per-book directory with result.json, extraction.json, llm_responses/ (raw per-model), consensus.json, ground_truth_comparison.json. Plus PHASE_C_MANIFEST.json and PHASE_C_SUMMARY.json.
3. **Owner reviews all 30** in Claude Chat sessions (5 per session, using kr-evaluate).
4. **Categorize findings** — CORE GAP / ENGINE BUG / LLM QUALITY / DATA ISSUE.
5. **Fix any ENGINE BUGs** found. Expand GROUND_TRUTH.json from 13 → ~43 entries.

**Known gaps going into Step 3:**
- 57 books have `author_short` only (no card field) — these genuinely need LLM inference, not a bug. Include at least 2 in the 30-book selection.
- No Format B test fixture exists — the Bug 2 colon-split fix in shamela_html.py is untested by unit tests. Create a synthetic Format B fixture during Step 3.
- Consensus pair: Command A + Opus 4.6 (92.3% at-least-one-right from Step 2 validation).

**Known deferred issues (fix before Step 5, not blocking Step 3):**
- C1: Layer authors use muhaqiq registration (no human gate) — acceptable for 25-30 books with owner review.
- C2: Check 5d `prior_sources` dead code — no prior sources exist yet.
- C3: Concurrent scholar updates race condition — Steps 3-5 are sequential.

**Required environment:**
```bash
export ANTHROPIC_API_KEY="..."
export OPENROUTER_API_KEY="..."
```

**After Step 3:** Proceed to Step 4 (Full Collection LLM Run) per `VALIDATION_PLAN.md`.
