# Overnight Work Queue — CronCreate Driven

This file is read by the cron-triggered prompt every 10 minutes.
Each task is a self-contained unit of work (~10 min).
Mark tasks [x] when complete. Commit after each task.

## Rules for the Cron Worker
1. Read this file at the start of each cron cycle
2. Find the first unchecked `[ ]` task
3. Do that ONE task thoroughly (quality > speed)
4. Mark it `[x]` and commit
5. STOP — let the next cron cycle pick up the next task
6. NEVER ask questions. NEVER /clear. NEVER edit settings.json.
7. If blocked, mark task `[BLOCKED: reason]` and move to next

## Queue

- [x] **T1: Deep integrity — read actual content.jsonl for 5 books and verify layer coverage char-by-char**
  Files: `scripts/verify_normalized_integrity.py` (add new check)
  Input: Pick 5 diverse books from results/normalization_sweep_v2/corpus_sweep.jsonl
  Acceptance: New check reads content.jsonl, verifies text_layers span full primary_text

- [ ] **T2: Full corpus re-sweep (all 7,475 books) with L-009/L-008/L-004 fixes**
  Command: `PYTHONIOENCODING=utf-8 python scripts/normalization_corpus_sweep.py --output-dir results/normalization_sweep_v3`
  Acceptance: All 7,475 OK, results persisted

- [ ] **T3: Compare v2 vs v3 sweep — measure full corpus impact of limitation fixes**
  Input: results/normalization_sweep_v2/ vs results/normalization_sweep_v3/
  Output: scripts/results/full_corpus_fix_impact.json
  Acceptance: Report shows delta for hadith, mid_argument, multi_layer across all books

- [ ] **T4: Write adversarial test for L-004 — words starting with وق that are NOT markers**
  Example: وقف (waqf - endowment) should NOT trigger marker detection
  File: engines/normalization/tests/test_layer_detection.py
  Acceptance: Test passes, proves no false positives from common و-initial words

- [ ] **T5: Write test for L-008 edge case — إذا after Arabic semicolon (؛)**
  Arabic semicolon (؛) is terminal punctuation in SPEC but less standard
  File: engines/normalization/tests/test_boundary_continuity.py
  Acceptance: إذا after ؛ is correctly detected as sentence-initial

- [ ] **T6: Investigate the 39 undiacritized books — are any hadith/Quran texts?**
  Input: scripts/results/integrity_diacritics.json
  Check: Cross-reference with genre data from source sweep
  Output: Log findings to .claude/pending_decisions.log
  Acceptance: Determine if any undiacritized books are classical texts where diacritics are expected

- [ ] **T7: Investigate the 1,892 books with validation warnings**
  Input: scripts/results/integrity_validation_gaps.json
  Analyze: char_run (8,260 warnings), low_arabic_ratio (4,530), division_overlap (2,544)
  Output: scripts/results/warning_deep_analysis.json
  Acceptance: Root cause each warning category, determine if any are actionable

- [ ] **T8: Wire safety hooks into settings.json (if owner approved)**
  Check: Read .claude/pending_decisions.log for owner approval
  If approved: Edit settings.json with JSON from HOOK_WIRING.md
  If not approved: Skip, mark BLOCKED

- [ ] **T9: Run full 7,475-book integrity check**
  Command: `PYTHONIOENCODING=utf-8 python scripts/verify_normalized_integrity.py --sweep results/normalization_sweep_v3/corpus_sweep.jsonl`
  Acceptance: All checks CLEAN or INFORMATIONAL on v3 data

- [ ] **T10: Update memory and session state**
  Update overnight_session_march22.md in memory with full results
  Update KNOWN_LIMITATIONS.md with calibration data from v3 sweep
  Commit everything, run final verification
