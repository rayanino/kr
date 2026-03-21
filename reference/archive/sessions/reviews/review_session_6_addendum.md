# Session 6 Review Addendum — Deep Analysis Pass

> Written AFTER the initial ACCEPT verdict, triggered by owner challenge: "why are you leaving these findings for a next session?"
> This addendum documents issues found during the deep critical analysis that the initial 3-pass review missed.

## Additional findings

### F1: Writer recovery gap — prev-only orphan state (L-011)

**File:** `engines/normalization/src/writer.py`, `recover_interrupted_write()`
**Issue:** If both `rename` and `shutil.move` fail after `final_dir.rename(prev_dir)` succeeded, the temp is cleaned but prev is orphaned. Recovery doesn't detect "no temp, no normalized/, but prev exists."
**Severity:** LOW — requires near-impossible filesystem failure. Failure is loud (NORM_WRITE_FAILED raised). Impact is re-processing, not corruption.
**Fix:** Add prev-only recovery case. CC instructions below.
**Status:** Documented as L-011. CC fix pending.

### F2: Misleading comment in validation.py orchestrator

**File:** `engines/normalization/src/validation.py`, line 119
**Issue:** Comment says "Non-fatal checks accumulate warnings" but the block includes `_check_text_extraction` which produces fatals.
**Severity:** Cosmetic — zero behavioral impact.
**Fix:** Update comment. CC instructions below.
**Status:** CC fix pending.

### F3: Smoke test never exercises check 4 (layer consistency)

**File:** `tools/smoke_test_validation.py`, `_make_smoke_metadata()`
**Issue:** All fixtures use `is_multi_layer=False`. Check 4 is always skipped. The smoke test's purpose is catching false positives on real data — skipping check 4 means layer consistency is never tested against the real 50-fixture extended set.
**Severity:** MEDIUM — test coverage gap. Unit tests cover check 4 with synthetic data, and ibn_aqil tests exercise it through the full pipeline, but the smoke test's value is exercising on data the build was NOT calibrated against.
**Fix:** Add multi-layer metadata for fixtures known to have bold-based layer signals. CC instructions below.
**Status:** CC fix pending.

### F4: SPEC sharh-majority check not implemented for 3-layer texts (SPEC-NOTE-3)

**File:** `engines/normalization/src/validation.py`, `_check_layer_consistency()`
**Issue:** SPEC says "sharh should be the majority in a sharh" but only `matn_ratio >= 0.40` is checked. The gap is architecturally inert until L-006 (hashiyah detection) is implemented.
**Severity:** INERT — 3-layer detection doesn't exist yet.
**Fix:** Documented as SPEC-NOTE-3 in `reference/SPEC_ERRATA.md`. No code change needed now.
**Status:** Documented. Will be implemented when L-006 is addressed.

## CC Fix Instructions

See below — exact changes for Claude Code.
