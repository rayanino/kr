# NEXT — Step 4 Phase B (Claude Code)

## Status: Phase A COMPLETE → Phase B (this session)

Phase A verified bug fixes via smoke test (5 books, all pass), analyzed category distribution, and selected 131 new books via stratified sampling. See commits `d309b48` through `ac29b7a`.

---

## Current Task: Build Step 4 Tooling

Claude Chat produced the task specification in the owner's message. Read it fully before writing any code.

**Four deliverables:**
1. Update Phase C manifest (mark 73 books for rerun)
2. `scripts/run_phase_d.py` (adapted from run_phase_c.py — 204 books)
3. `scripts/generate_screening_report.py` (auto-flag anomalies)
4. `scripts/generate_review_gui.py` (self-contained HTML review tool)

Commit after each deliverable.

---

## Key State

- **Pipeline version:** `ac29b7a` (HEAD, includes all bug fixes from `c640a9b` plus Phase A work)
- **Tests passing:** 573
- **Budget spent:** €9.70 | **Remaining:** €90.30
- **Phase C manifest:** `tests/results/source_engine/phase_c/PHASE_C_MANIFEST.json` — needs `needs_rerun: true` for all 73 books
- **Book lists:** `scripts/phase_c_books.txt` (73 reruns) + `scripts/phase_d_books.txt` (131 new) = 204 total
- **Phase C results for regression comparison:** `tests/results/source_engine/phase_c/{book}/result.json`

## After This Session

The owner runs `python scripts/run_phase_d.py COLLECTION_DIR` on their Windows machine (1-2 hours, can walk away). Then runs `generate_screening_report.py` and `generate_review_gui.py` to produce the review tools. Claude Chat evaluates results in Phase C sessions.

## Governing Documents (read in this order)

1. **This file** (NEXT.md)
2. **The owner's message** — contains the full task specification
3. **STEP4_PREPARATION_PLAN.md** — overall Step 4 workflow context
4. **scripts/run_phase_c.py** — the script to adapt (read thoroughly)
5. **RESULT_PRESERVATION.md** — output structure requirements
6. **STEP3_FINAL_BUG_LIST.md** — what the bug fixes changed
