# NEXT — Step 4 Phase D Complete

## Status: Phase D pipeline run + post-processing COMPLETE. Owner reviews in GUI.

## What the owner does

1. Open `tests/results/source_engine/phase_d/review_gui.html` in a browser (double-click)
2. Review 204 books using the GUI:
   - Dashboard shows stats, distributions, known issues
   - Review Queue walks through books one at a time (keyboard: 1=Correct, 2=Wrong, 3=Unsure, arrows=navigate)
   - List View for filtering and searching
3. Export feedback as JSON when done (Export button)
4. Give the exported `kr_phase_d_feedback.json` to Claude Chat for Phase E evaluation

## Results summary

- **204 books processed, 100% success rate** (0 gate_abort, 0 errors)
- **73 reruns** from Phase C: 51 gate_abort→success (BUG-01 fix), 22 stable success→success, 0 regressions
- **131 new books** all successful
- **14 consensus disagreements** (models disagreed on some fields)
- **69 flagged trust** books (mostly unknown muhaqiq → low trust score)
- **20 multi-layer** books detected
- **Cost:** EUR 20.4 (total cumulative: EUR 30.1)

## Key files

- `tests/results/source_engine/phase_d/review_gui.html` — self-contained review GUI
- `tests/results/source_engine/phase_d/PHASE_D_AUTO_SCREENING.md` — auto-screening report
- `tests/results/source_engine/phase_d/PHASE_D_MANIFEST.json` — book manifest
- `tests/results/source_engine/phase_d/PHASE_D_SUMMARY.json` — run summary
- `scripts/phase_d_postprocess.py` — post-processing script
- `scripts/generate_review_gui.py` — GUI generator
