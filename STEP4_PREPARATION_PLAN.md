# Step 4 Preparation Plan — Complete Workflow

**Produced by:** Claude Chat (Architect)
**Date:** 2026-03-12
**Status:** DRAFT — owner must approve before execution

---

## Critical Issues Found During Plan Self-Review

Five issues that would have caused Step 4 to fail if not addressed:

1. **NO SMOKE TEST.** Claude Code fixed 5 bugs and ran unit tests, but did NOT test with real Shamela books and real LLM calls. BUG-01 changed the `lookup_or_register_author` interface (school → school_affiliations dict). If the dict contains None values or unexpected types from real LLM output, 200 books × €0.10 = €20 wasted.

2. **MANIFEST NOT UPDATED.** Phase C manifest says `needs_rerun: false` for all 73 books, but they were processed on pipeline version `10644a6` (pre-fix). The current version is `c640a9b`. All 51 gate_abort books MUST be rerun (BUG-01 fix changes their outcome from gate_abort to success). The 22 success books should also be rerun for regression verification.

3. **EXHAUSTIVE REVIEW IS UNREALISTIC.** Phase C reviewed 73 books in 8 Claude Chat sessions. 200 books at 10/session = 20 sessions. Each session requires the owner to start a new conversation, paste the prompt, and wait. This is 2.5x the Phase C effort for diminishing returns — Phase C already validated the pipeline's core behavior.

4. **BOOK SELECTION NEEDS DATA WE DON'T HAVE.** The 2,519-book Shamela category distribution is only available on the owner's machine (Phase A extraction data). Stratified sampling requires this distribution.

5. **PHASE C GATE_ABORT BOOKS BECOME FULL RESULTS.** After BUG-01 fix, 51 previously-gate_abort books will produce complete SourceMetadata (trust tier, frozen files, full result.json). This is valuable — but it means Step 4 results include both "old books, new pipeline" and "new books, new pipeline." The review must distinguish regression checks from new-book evaluation.

---

## Revised Plan: 4 Steps

### Step A: Verify Fixes + Smoke Test + Book Selection (Claude Code on owner's machine)

**What:** One Claude Code session that does four things:
1. Run full test suite (verify 562 tests still pass)
2. Run 5 books end-to-end with real LLM calls as a smoke test
3. Analyze Shamela category distribution across all 2,519 books (reads Phase A extraction data)
4. Generate stratified random sample of ~130 new books for Step 4

**Smoke test books (chosen to validate each bug fix):**
- 1 previously-gate_abort famous book (e.g., فتح الباري) — verifies BUG-01 fix
- 1 previously-success book (e.g., البداية والنهاية ط السعادة) — verifies no regression
- 1 tahqiq-note book (e.g., مسند أحمد ت شاكر) — verifies BUG-03 override fires
- 1 obscure modern book (e.g., أحكام الاضطباع) — verifies edge case handling
- 1 sharh book (e.g., شرح النووي على مسلم) — verifies BUG-03 override does NOT fire on real multi-layer

**Smoke test GO/NO-GO:**
- All 5 complete with no crashes
- Previously-gate_abort book now produces status=success with full SourceMetadata
- Previously-success book produces identical or better results (no regression)
- Tahqiq-note book has is_multi_layer=false (override fired correctly)
- Sharh book has is_multi_layer=true (override correctly did NOT fire)

**Book selection stratification criteria:**
- Proportional to Shamela category distribution (major categories get more books)
- Minimum 3 books per category that has 10 or more books in the collection
- At least 5 books with muhaqiq present in extraction (tahqiq editions)
- At least 5 books with no author_name_raw (tests pure LLM author inference)
- Exclude all 73 Phase C books from the "new" selection (they are rerun separately)

**Output:**
- Smoke test results in `tests/results/source_engine/smoke_test/`
- `PHASE_D_CATEGORY_DISTRIBUTION.json` — full distribution of all 2,519 books
- `scripts/phase_d_books.txt` — the ~130 new book directory names
- `PHASE_D_SELECTION.md` — selection rationale and strata breakdown

**Cost:** ~€0.50 (5 smoke test books × €0.10/book). Category analysis and selection are free (no LLM calls).

**Who does what:**
- Owner opens Claude Code in kr/ directory
- Owner pastes the prompt I write (I write it after owner approves this plan)
- Claude Code does everything
- Owner can review the book selection and swap books if desired (domain judgment)
- Owner tells me "done" → I pull repo, verify smoke test results and selection

---

### Step B: Build Tools + Run Pipeline (Claude Code on owner's machine)

**Prerequisites:** Step A passed smoke test GO/NO-GO. I (Claude Chat) have verified the smoke test results and approved the book selection.

**What:** One Claude Code session that:
1. Updates Phase C manifest: all 73 books → `needs_rerun: true`, `pipeline_version: c640a9b`
2. Builds `scripts/run_phase_d.py` (adapted from `run_phase_c.py`, includes all 73 Phase C reruns + ~130 new books)
3. Builds the owner review GUI generator script

Then the owner runs the pipeline script manually (1-2 hours, independent of Claude Code). After the run completes, Claude Code generates the GUI HTML and auto-screening report.

**Auto-screening report flags:**
- Regression: Phase C books where author, genre, or ML changed vs old results
- Confidence outliers: author_confidence < 0.75 or genre_confidence < 0.75
- Gate events: any remaining gate_abort books (should be near zero after BUG-01 fix)
- Consensus disagreements (expected ~6% based on Phase C rate)
- trust_tier=flagged success books (investigate why flagged)
- is_multi_layer=true books (list all, for layer structure verification)
- Check 5c warnings (the downgraded author-science check — diagnostic only)
- Check 5f overrides (tahqiq-note auto-correction — verify correctness)

**Owner Review GUI:** Single self-contained HTML file with all result data embedded (~400KB). No server, no file access, no installation. Arabic titles and author names. Color-coded confidence (green/yellow/red). Owner marks ✅/❌/❓ per book. Downloads verdicts as JSON.

**Cost:** ~€20 (200 books × €0.10/book)

**Who does what:**
- Owner opens Claude Code, pastes prompt → Claude Code builds tools and scripts
- Owner runs `python scripts/run_phase_d.py "C:\Users\Rayane\Desktop\kr\shamela export samples"` manually (1-2 hours, can walk away)
- After run completes: owner opens Claude Code again, gives it a short prompt to generate the review GUI HTML file and auto-screening report
- Owner tells me "done" → I pull repo and begin evaluation

---

### Step C: Dual-Track Review

**This is the core evaluation phase.** Two tracks run concurrently.

**Track 1: Claude Chat Evaluation (me)**
Tiered review, not exhaustive:

| Tier | Books | Depth | Sessions |
|------|-------|-------|----------|
| Tier 1 (deep) | ~60-80 books: all anomalies from auto-screening, all consensus disagreements, all confidence < 0.85, all ML=true, Phase C regression checks, 10% random | Full Phase C-style evaluation with self-review protocol (4-5 rounds per session) | ~8 sessions at 10 books each |
| Tier 2 (statistical) | Remaining ~120-140 books | Auto-screening script already checked these. Claude Chat does a statistical review of the batch (distributions, patterns) but not per-book evaluation | 1-2 sessions |

Total: ~10 Claude Chat sessions (vs 20 if exhaustive). Each session produces a report with structured verdicts.

**Track 2: Owner Review in GUI**
The owner opens the generated HTML file in any browser. Books are sorted by confidence (lowest first). The owner reviews:
- All books flagged by the auto-screening report (~30-40 books)
- Any additional books he wants to spot-check based on domain knowledge
- His verdicts are downloaded as a JSON file when done

**The GUI is a single self-contained HTML file** with all result data embedded as a `<script>` JSON blob (~400KB for 200 books). No server, no file access, no installation. Claude Code generates it after the pipeline run by reading result.json files and embedding the key fields. The owner just double-clicks the HTML file.

**Timeline:** Track 1 and Track 2 can happen in parallel. The owner reviews in the GUI while I evaluate in Claude Chat sessions.

**Disagreement resolution:** After both tracks complete, I compare:
- Books where Claude Chat said VERIFIED but owner said ❌ wrong → investigate, owner wins on domain
- Books where Claude Chat said PLAUSIBLE/FLAG but owner said ✅ correct → investigate, may upgrade
- Books neither track reviewed → accepted based on auto-screening (no anomalies detected)

---

### Step D: Aggregation + GO/NO-GO

**What:** One Claude Chat session that:
1. Reads all Track 1 session reports
2. Reads owner's GUI verdicts JSON
3. Produces `PHASE_D_AGGREGATION_REPORT.md` (same structure as Phase C)
4. Produces `MASTER_MANIFEST.json` covering all ~273 processed books
5. Writes GO/NO-GO verdict for the source engine

**GO criteria (from VALIDATION_PLAN):**
- Trust distribution reasonable (not all flagged, not all verified)
- Gate rate < 15% (should be near 0% after BUG-01 fix)
- No systematic scholar duplicates in registry
- No CORE GAP findings
- Zero author identification errors
- Regression: Phase C VERIFIED books still produce correct results after rerun

**After GO:**
- Source engine is VALIDATED
- The ~273 processed books are the normalization engine's development input
- Begin normalization engine design

---

## What the Owner Does (complete list)

| Step | Owner action | Time |
|------|-------------|------|
| 0 | Approve this plan | 5 min |
| A | Open Claude Code, paste prompt, wait for smoke test + selection, tell me "done" | ~20 min active |
| — | (I verify smoke test results and book selection) | Owner waits |
| B1 | Open Claude Code, paste prompt → tools and run script built | ~10 min |
| B2 | Run the pipeline script manually in terminal (can walk away) | ~5 min active + 1-2 hour wait |
| B3 | Open Claude Code again, paste short prompt → GUI + screening report generated | ~5 min |
| B3 | Tell me "done" | 30 seconds |
| C (Track 2) | Open GUI HTML in browser, review ~30-40 flagged books, download verdict JSON | ~2-3 hours at own pace |
| C (Track 1) | Start ~10 Claude Chat sessions (paste prompt per session, wait for completion) | ~10 min per session |
| D | Read GO/NO-GO verdict | 5 min |

**Total owner active time:** ~4-5 hours spread across several days
**Total API cost:** ~€21 (€0.50 smoke test + €20 pipeline run)
**Budget remaining after Step 4:** ~€69 (of €100 ceiling)

---

## Risk Mitigation

| Risk | Mitigation | When |
|------|-----------|------|
| Bug fix regression | Smoke test with 5 real books catches before €20 spend | Step A |
| Bad book selection | Category distribution analysis + stratification + owner review | Step A |
| Shamela collection access | All pipeline execution on owner's machine via Claude Code | Steps A + B |
| Review workload collapse | Tiered review (60-80 deep, rest statistical) not exhaustive | Step C |
| Owner doesn't use GUI | GUI is single self-contained HTML file, no setup, Arabic display, auto-sorted by priority | Step B |
| Phase C regression | All 73 books rerun; old vs new results compared in screening report | Step B + C |
| Manifest stale | Updated in Step B before pipeline run | Step B |
| Scale-specific bugs | 200 books stress test: registry collisions, work_id truncation | Step C analysis |
| Browser file access issues | GUI has ALL data embedded in HTML — no file system access needed | Step B |
| Long pipeline run disconnects Claude Code | Owner runs script manually; Claude Code only writes it | Step B |

---

## What Comes After Step 4 (NOT planned now, just context)

If GO: normalization engine design begins. The ~273 processed books become its development input.
If NO-GO: fix identified issues, re-run affected subset, re-evaluate. Budget allows 1-2 re-runs.
