# NEXT — Taxonomy Session 1 Review Fixes (F-1, F-3, F-4, F-6)

## Context

Session 1 review (checklist: `reference/archive/sessions/reviews/review_taxonomy_session1.md`) found 4 issues. This directive fixes all 4.
Session 2 NEXT.md preserved at: `reference/archive/NEXT_taxonomy_session2_deferred.md`

**Read first:**
1. `engines/taxonomy/SPEC.md` §2.1 (expected fields), §4.A.3 (type classification)
2. `engines/taxonomy/src/placer.py` lines 76-102 (`classify_excerpt_type`)
3. `engines/taxonomy/src/engine.py` lines 46-54 (`_EXPECTED_FIELDS`)
4. `engines/taxonomy/src/diagnostics.py` lines 136-152 (`compute_editorial_placement_rate`)
5. `engines/excerpting/contracts.py` — search for `class ScholarlyFunction` to see all valid enum values

## Fix 1: F-6 (CRITICAL) — classify_excerpt_type must default unknown to EDITORIAL

**File:** `engines/taxonomy/src/placer.py`

**Problem:** Unrecognized `primary_function` values (like `"unclassified"` from excerpting's `ScholarlyFunction.UNCLASSIFIED`) are classified as TEACHING (threshold 0.80). SPEC §4.A.3 says "not recognized" → EDITORIAL (threshold 0.85).

**Fix:** Add an explicit `_TEACHING_FUNCTIONS` frozenset with all known teaching values from the excerpting engine's `ScholarlyFunction` enum. Change `classify_excerpt_type` so anything not in any known set defaults to EDITORIAL with a warning log.

The known teaching functions are: `definition`, `rule_statement`, `evidence_quran`, `evidence_hadith`, `evidence_ijma`, `evidence_qiyas`, `evidence_rational`, `opinion_statement`, `refutation`, `example`, `condition_exception`, `narration`.

Add a `logger.warning` when the unknown-default path is hit so we can detect new function values.

**New tests** in `test_routing.py::TestClassifyExcerptType`:
- `"unclassified"` → EDITORIAL
- `"some_future_unknown_type"` → EDITORIAL
- Every value in `_TEACHING_FUNCTIONS` → TEACHING (parametrized or loop)

## Fix 2: F-1 — _EXPECTED_FIELDS must include all 8 SPEC fields

**File:** `engines/taxonomy/src/engine.py`

**Problem:** `_EXPECTED_FIELDS` has 4 of 8 SPEC §2.1 expected fields. Missing: `terminology_variants`, `primary_author_layer`, `quoted_scholars`, `school`.

**Fix:** Add the 4 missing fields. Also change the warning check from `excerpt.get(field) is None` to `field not in excerpt` — this prevents false warnings on nullable fields like `school: null` which are present but legitimately null.

**New tests** in `test_engine.py::TestInputValidation`:
- Missing expected field still proceeds (not rejected)
- `school=None` with key present does NOT trigger warning

## Fix 3: F-4 — compute_editorial_placement_rate must use classify_excerpt_type

**File:** `engines/taxonomy/src/diagnostics.py`

**Problem:** Only counts `primary_function == "editorial_note"`. Misses null/missing/unknown values that are routed as editorial by `classify_excerpt_type`.

**Fix:** Import `classify_excerpt_type` from `placer.py` and `ExcerptType` from contracts. Use `classify_excerpt_type(r) == ExcerptType.EDITORIAL` instead of string comparison.

**New/updated test** in `test_diagnostics.py::TestEditorialPlacementRate`:
- Null `primary_function` counted as editorial in rate calculation

## Fix 4: F-3 — Create test_real_data.py

**File:** `engines/taxonomy/tests/test_real_data.py` (CREATE)

Use the existing `real_excerpts` fixture from `conftest.py` (currently orphaned — defined but never used).

Tests to include:
- All excerpts have the 4 required fields
- `excerpt_topic` is a non-empty list in all excerpts
- No crash when running `classify_excerpt_type` on real data shapes
- `primary_text` contains Arabic characters (sanity check)
- Use `pytest.skip` if excerpts file not available

## Verification (Definition of Done)

- [ ] `classify_excerpt_type({"primary_function": "unclassified"})` returns `ExcerptType.EDITORIAL`
- [ ] `classify_excerpt_type({"primary_function": "rule_statement"})` returns `ExcerptType.TEACHING`
- [ ] `_EXPECTED_FIELDS` has exactly 8 entries
- [ ] Excerpt with `school=None` (key present) does NOT trigger expected-field warning
- [ ] `compute_editorial_placement_rate` counts null primary_function as editorial
- [ ] `test_real_data.py` exists and all tests pass
- [ ] All tests pass: `PYTHONPATH=. python -m pytest engines/taxonomy/tests/ -q --tb=short`
- [ ] Test count: ≥ 125 (was 119, expect ~6-8 new tests)

## Do NOT Do

- Do NOT modify `tree_loader.py`, `writer.py`, or `validator.py`
- Do NOT modify `contracts_core.py`
- Do NOT implement anything beyond the 4 fixes specified above
- After completing the fixes, commit and push. Do NOT proceed to Session 2.
