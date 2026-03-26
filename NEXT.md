# NEXT — Fix compute_page_range Crash on Split Chunks

## Current Position

- **Baseline:** 588 tests passing, 2 skipped, 0 failed (588 passed, 2 skipped)
- **Commit:** `7a925269` (master HEAD)
- **Engine:** Excerpting
- **Phase:** Build / Harden (fixing pre-existing Phase 3 crash)

## What To Do

Fix the `IndexError` crash in `compute_page_range()` caused by split chunks having mismatched `physical_pages` and `join_points` lengths. Two changes required:

1. **Primary fix:** Partition `physical_pages` in `split_oversized_division()` alongside `join_points` (currently copies ALL pages to each split half).
2. **Defensive guard:** Clamp the loop in `compute_page_range()` to prevent `IndexError` even if lengths are mismatched.

## Context

When `split_oversized_division` splits a chunk, it correctly partitions `join_points` between the two halves (line 712–727) but copies ALL `physical_pages` to each half (lines 767, 795). This breaks the invariant `len(physical_pages) == len(join_points) + 1` that `compute_page_range` assumes at line 386.

**The crashing case (ibn_aqil_v1):**
```
div_src_test0001_2_008 ("الابتداء") — 73 pages, split into 2 chunks:
  chunk_0: 73 pages, 39 join_points → expects 40 pages, has 73 → IndexError
  chunk_1: 73 pages, 33 join_points → expects 34 pages, has 73 → IndexError
```

This affects 3 of 5 test packages: ibn_aqil_v1, ext_39_masala, taysir.

## Owner Action Needed

None. This is a CC-only implementation task. After CC pushes, owner relays the commit hash to the architect for review.

## Read First

| # | File | Lines | What |
|---|------|-------|------|
| 1 | `engines/excerpting/src/phase1_assembly.py` | 683–840 | `split_oversized_division()` — the function creating the mismatch |
| 2 | `engines/excerpting/src/phase3_deterministic.py` | 354–414 | `compute_page_range()` — the crashing function |
| 3 | `engines/excerpting/tests/test_phase3_deterministic.py` | 463–504 | Existing `TestPageRange` tests |
| 4 | `engines/excerpting/tests/test_phase1_split.py` | 1–222 | Existing split tests (no physical_pages coverage) |
| 5 | `engines/excerpting/tests/conftest.py` | 63–104 | `_make_assembled_chunk` helper with defaults |

## What to Build

### Change 1: Partition physical_pages in split_oversized_division

**File:** `engines/excerpting/src/phase1_assembly.py`

**Location:** Lines 756–810 (chunk_0 and chunk_1 construction)

**Current code (line 767):**
```python
physical_pages=chunk.physical_pages,  # BUG: copies ALL pages
```

**Fix:** Replace with partitioned pages. The split boundary page must be included in BOTH halves (so neither chunk's page range has a gap at the split boundary):

```python
# Partition physical_pages to match join_point partitioning.
# jp_0 covers the first N page boundaries → first N+1 pages.
# The boundary page (index len(jp_0)) is shared between both halves
# so that teaching units near the split boundary get correct page refs.
pages_0 = chunk.physical_pages[:len(jp_0) + 1]
pages_1 = chunk.physical_pages[len(jp_0):]
```

Then use `pages_0` for chunk_0 (line 767) and `pages_1` for chunk_1 (line 795).

**Invariant to verify after the fix:**
- `len(pages_0) == len(jp_0) + 1` (or `len(pages_0) == 1` when `jp_0` is empty)
- `len(pages_1) == len(jp_1) + 1` (or `len(pages_1) == 1` when `jp_1` is empty)

**Edge case:** If `jp_0` is empty (all join_points went to the second half), `pages_0` should be `[chunk.physical_pages[0]]` — a single page. The formula `chunk.physical_pages[:0 + 1]` handles this correctly. Similarly if `jp_1` is empty.

### Change 2: Defensive guard in compute_page_range

**File:** `engines/excerpting/src/phase3_deterministic.py`

**Location:** Line 386

**Current code:**
```python
for i in range(len(physical_pages)):
```

**Fix:** Clamp to the number of pages that join_points can actually map:
```python
# Defensive: clamp to pages addressable by join_points.
# After the split fix, len(physical_pages) == len(offsets) + 1 always holds.
# This guard prevents IndexError if a future code path breaks that invariant.
n_pages = min(len(physical_pages), len(offsets) + 1)
for i in range(n_pages):
```

This ensures the function never crashes even if the invariant is violated — it simply ignores unmappable pages (which is safe because those pages have no join_point-defined character range).

## Design Decisions (Pre-Resolved)

**DD-1: Why partition physical_pages instead of just fixing compute_page_range?**

Clamping the loop alone would produce WRONG page numbers for chunk_1. In chunk_1, `join_points` are re-indexed relative to chunk_1's text (subtracted `split_offset`), but `physical_pages` would still start from page 0 of the original division. The first join_point offset in chunk_1 maps to the first page *of chunk_1's text*, not to `physical_pages[0]` (which is the first page of the original unsplit division). Data alignment must happen at the source.

**DD-2: Why overlap the boundary page in both halves?**

A teaching unit near the split boundary might reference text that straddles the last page of chunk_0 and the first page of chunk_1. Including the boundary page in both halves ensures both chunks can correctly attribute page ranges for units near the split point. The worst case is a PageRange that includes one extra page — acceptable for citation purposes.

**DD-3: Recursive splitting.**

After the fix, if chunk_0 or chunk_1 is recursively split again, the same partitioning logic applies correctly because each recursive call starts with correctly-partitioned `physical_pages` and `join_points`.

## Do NOT Do

- Do NOT change the `constituent_unit_indices` sharing behavior (I-AC-4). That is correct and must remain unchanged.
- Do NOT change how `join_points` are partitioned — that logic (lines 712–727) is correct.
- Do NOT modify any Phase 2 or Phase 3 code except the defensive guard in `compute_page_range`.
- Do NOT implement anything beyond what is specified here. After completing the fix, commit and push. Do NOT proceed to the next task.

## Verification

### Tests to add

**Test 1: Split chunk physical_pages partitioning** (in `test_phase1_split.py`)

Create an oversized chunk with N physical_pages (e.g., 10 pages numbered 50–59) and N-1 join_points with `char_offset_in_assembled` values evenly spaced through the text. Split it and verify:
- `len(result[0].physical_pages) == len(result[0].assembly_metadata.join_points) + 1`
- `len(result[1].physical_pages) == len(result[1].assembly_metadata.join_points) + 1`
- The last page of result[0] equals the first page of result[1] (boundary overlap)
- result[0].physical_pages contains pages from the FIRST portion of the original (e.g., pages 50–54)
- result[1].physical_pages contains pages from the SECOND portion (e.g., pages 54–59)
- The union of both halves' page numbers covers the full original range

**Test helper note:** The existing `_make_oversized_chunk` helper does NOT set physical_pages or join_points. You will need to construct an `AssembledChunk` via `_make_assembled_chunk` (from conftest.py) with explicit `physical_pages` and `assembly_metadata.join_points`. Use the existing `_oversized_text()` helper for the text, and construct `PhysicalPage` and `JoinPoint` objects directly (see `test_phase3_deterministic.py:470-498` for the pattern).

**Test 2: compute_page_range with split-like dimensions** (in `test_phase3_deterministic.py`)

Create a scenario where physical_pages and join_points have the dimensions of a split chunk (e.g., 40 pages, 39 join_points — the correctly-partitioned state) and verify correct PageRange output.

**Test 3: compute_page_range defensive guard** (in `test_phase3_deterministic.py`)

Create a scenario where `len(physical_pages) > len(join_points) + 1` (the broken state that used to crash) and verify it returns a sensible result instead of crashing.

### Pass criteria

1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → ≥591 passed (588 baseline + 3 new), 2 skipped, 0 failed
2. Mock integration test completes without crash on ALL 5 packages:
```bash
for pkg in experiments/format_diversity_test/packages/*/; do
    echo "=== $(basename $pkg) ==="
    PYTHONPATH=. python scripts/run_integration_test.py --mock --package-path "$pkg" --output-dir "/tmp/mock_$(basename $pkg)" 2>&1 | tail -5
done
```
3. No regressions in existing tests

### Automated validation

```bash
python tools/validate_handoff.py --engine excerpting
```

## After This

Stop. Commit and push. Do not continue to the next task. The architect will review the fix, then run the mock integration test and first real LLM call separately.
