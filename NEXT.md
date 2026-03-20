# NEXT — Fix Session 5 Review Findings (2 findings in boundary_continuity.py)

## Current position: Session 5 review BLOCKED (commit dbb8982). Two findings in `engines/normalization/src/boundary_continuity.py`. Content flagger and output assembly are clean. 253 tests passing.
## What to do: Fix both findings, update tests, re-verify.
## Context: Architect review found (1) over-broad argument markers not in SPEC and (2) missing leading word boundary check causing 13.7% substring false positives. Both are in the boundary continuity module only.
## Owner action needed: NO — start new CC session for fix.
## Git range for review: from `dbb8982` to HEAD after fix.

---

## Read First

1. `engines/normalization/src/boundary_continuity.py` (266L) — The file being fixed.
2. `reference/archive/sessions/reviews/review_session_5.md` — Full review checklist with evidence for both findings.
3. `engines/normalization/tests/test_boundary_continuity.py` (335L) — Tests to update.

---

## Finding 1: Remove over-broad markers `لأن` and `وقال`

**Evidence:** `لأن` ("because") fires on 2.8% of all fixture pages (17% of tafsir). `وقال` ("and he said") fires on 4.1%. Together they account for 82% of all opener hits. Neither is in the SPEC §4.B.8 marker table. Both are generic Arabic constructions, not scholarly argument markers.

**Fix:**
- Line 67: Remove `"لأن"` from `evidence_chain.opening_patterns`. The line should become:
  ```python
  "ولنا", "واستدل", "والدليل", "بدليل",
  ```
- Line 78: Remove `"وقال"` from `position_statement.opening_patterns`. The line should become:
  ```python
  "وذهب", "ومذهب", "واختار",
  ```

**Test impact:** No existing tests use `لأن` or `وقال` as markers. Zero test changes needed for this finding.

---

## Finding 2: Add leading word boundary check to `_find_argument_marker`

**Evidence:** The function only checks `_has_word_boundary_after` (trailing). This causes:
- `ولنا` to match inside `فقولنا` ("so our saying") — ibn_aqil page 0
- `لأن` to match inside `الأنصاري` — 01_nahw_simple (this marker is being removed by Finding 1, but the bug affects ALL markers)
- `قلنا` (closer) to match inside `فقلنا` ("so we said") and `وقلنا` ("and we said") — 33.3% false positive rate for this closer

29/211 total marker occurrences (13.7%) are substring false positives across all fixtures.

**Fix:**

1. Add a `_has_word_boundary_before` function (mirror of `_has_word_boundary_after`):
```python
def _has_word_boundary_before(text: str, match_start: int) -> bool:
    """Check that the character before match_start is space, punct, or start.

    Mirrors _has_word_boundary_after for leading boundary detection.
    """
    if match_start <= 0:
        return True
    ch = text[match_start - 1]
    return ch in (" ", "\t", "\n", "\r") or ch in _TERMINAL_PUNCT or ch in ("،", ":", "؛")
```

2. Update `_find_argument_marker` to apply BOTH checks:
```python
def _find_argument_marker(
    text: str, patterns: list[str],
) -> bool:
    """Check if any pattern appears in text with proper word boundaries."""
    for pattern in patterns:
        idx = 0
        while True:
            pos = text.find(pattern, idx)
            if pos == -1:
                break
            if (_has_word_boundary_before(text, pos) and
                    _has_word_boundary_after(text, pos + len(pattern))):
                return True
            idx = pos + 1
    return False
```

**Test additions (3 new tests):**

1. Test leading boundary rejects substring: `فقولنا` should NOT trigger `ولنا` marker.
2. Test leading boundary accepts standalone: `ولنا حديث` with space before SHOULD trigger.
3. Test closer leading boundary: `فقلنا` should NOT trigger `قلنا` closer (verifies closers also benefit from the fix).

---

## Do NOT Do

- Do NOT change `content_flagger.py` — it passed review clean.
- Do NOT change `_pass6_assemble` in `shamela.py` — it passed review clean.
- Do NOT change the confidence values (0.80/0.70) — they follow the SPEC definition range.
- Do NOT add new markers to replace `لأن`/`وقال` — let empirical data from the deterministic sweep (Step 2 of source engine roadmap) inform future marker additions.
- Do NOT change any Pass 1-5 logic.

---

## Verification

```bash
# All tests pass (existing + new)
python -m pytest engines/normalization/tests/ -v

# Cross-engine contracts still consistent
python tools/check_cross_engine_contracts.py
```

**Pass criteria:**
- 253 existing tests still pass (zero regressions). Note: some boundary continuity tests may need confidence value adjustments if the marker removal changes the fixture-based tests — check `test_03_fiqh_has_argument_flow` in particular.
- 3+ new tests pass (leading boundary checks)
- Cross-engine contracts: PASS

---

## After This

Return to the architect for re-verification. The architect will:
1. Re-run the false positive analysis (29/211 should drop to near-zero)
2. Re-run the mid_argument fixture rates (should match the simulated post-fix rates)
3. Verify the SPEC concrete example still traces correctly
4. If clean → mark Finding 1 and Finding 2 as Fixed in the review checklist → ACCEPT
