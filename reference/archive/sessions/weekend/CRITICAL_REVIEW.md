# Weekend Plan — Architect Critical Review

**Date:** 2026-03-21
**Reviewer:** Claude Chat (Architect)
**Method:** Adversarial review of NEXT.md, sweep scripts, task queue, and NEXT.md drafts

---

## Issues Found — Must Fix Before Dispatch

### F-1 (HIGH): Source sweep will produce 20K+ individual JSON files in git

**Location:** `scripts/phases/run_phase_a.py` line 422-425, NEXT.md Task B commit instruction
**Problem:** The source sweep writes one JSON file per item to `results/source_sweep/`. With 20K+ items in `shamela-export-samples/`, this creates 20K+ files. The NEXT.md instruction `git add results/source_sweep/` would commit all of them — catastrophic for repo health.
**Fix:** CC must only commit `PHASE_A_SUMMARY.json` and `CC_ANALYSIS.md`. Per-book files stay local. Added to CC dispatch message.

### F-2 (MEDIUM): Source sweep iterates ALL filesystem items, not just books

**Location:** `scripts/phases/run_phase_a.py` line 323: `items = sorted(collection_dir.iterdir())`
**Problem:** Unlike the normalization sweep's `discover_books()` (which filters for directories with .htm files), the source sweep processes EVERY child of the collection directory — including non-book items, metadata files, etc. These produce UNSUPPORTED_FORMAT errors that inflate the error count.
**Impact:** Not a correctness issue. CC's analysis should filter these out (genuine errors vs format-unsupported). Added note to CC dispatch message.

### F-3 (MEDIUM): Task 2 references nonexistent --book-list flag

**Location:** Task 2 NEXT.md Step 4
**Problem:** The normalization sweep script has `--collection-dir`, `--output-dir`, `--limit`, `--resume`. No `--book-list` flag exists.
**Fix:** Task 2 NEXT.md now instructs CC to write a small wrapper script that filters the book list, rather than assuming the flag exists.

### F-4 (MEDIUM): Original plan missing post-fix verification

**Problem:** Task 2 fixes bugs but the original plan had no re-sweep to prove the fixes work. Without re-running crashed books, we can't measure the actual improvement.
**Fix:** Added Task 3 as explicit "verification re-sweep" — re-runs previously-crashing books to produce clean before/after numbers for the transition gate.

---

## Issues Acknowledged — Acceptable for Weekend Scope

### A-1: Normalization sweep uses is_multi_layer=False for all books

**Location:** `scripts/normalization_corpus_sweep.py` line 130
**Impact:** Auto-upgrade from single→multi-layer IS tested (pre_scan_multi_layer runs). Explicit multi-layer path (where source engine metadata says True) is NOT tested at scale — only on 63 fixtures (4 multi-layer).
**Rationale:** Acceptable because: (a) auto-upgrade is the harder/riskier path, (b) explicit multi-layer was tested on fixtures, (c) we can't generate real SourceMetadata for 20K books this weekend. Noted in calibration task for architect review.

### A-2: Cross-engine integration with real SourceMetadata infeasible

**Impact:** The 204 phase_d books have real metadata but may not be in the 20K+ collection (different Shamela sets). Can't run normalization with real metadata at scale.
**Rationale:** The sweep's passaging contract checks (4, 5, 6) validate the output format. The metadata content (genre, structural_format) doesn't affect normalization processing in the Shamela normalizer — only `is_multi_layer` matters (covered by A-1).

### A-3: detect_layers fast path never exercised with is_multi_layer=True from metadata

**Location:** `engines/normalization/src/layer_detector.py` line 661
**Impact:** When is_multi_layer=False and auto-upgrade doesn't trigger, detect_layers returns single-MATN fast path. This is correct behavior for single-layer books. The gap is: multi-layer books where auto-upgrade fails to detect them.
**Rationale:** If auto-upgrade fails to detect a multi-layer book, that's a detection gap (analogous to L-004/L-005), not a sweep methodology flaw. The sweep correctly tests what the production pipeline would do for these books.

---

## Plan Adjustments Made

1. Merged Tasks 3+4 (cross-engine integration + calibration) into a single "Verification Re-Sweep + Calibration" task
2. Added explicit post-fix re-run of crashing books
3. Pre-wrote all NEXT.md files for Tasks 2-5 and pushed to repo
4. Created dispatch protocol with green-light / red-flag criteria
5. Simplified Task 5 (LLM probes) book selection criteria
