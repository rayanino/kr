# Phase 3.1 Deterministic Metadata Assembly — Code Review

**Reviewer:** Claude Opus 4.6 (overnight autonomous)
**Date:** 2026-03-24
**Files reviewed:**
- `engines/excerpting/src/phase3_deterministic.py` (637 lines)
- `engines/excerpting/tests/test_phase3_deterministic.py` (739 lines)
- `engines/excerpting/tests/conftest.py` (598 lines, Phase 3 additions)
- `engines/excerpting/contracts.py` (ExcerptRecord model, validators, error codes)
- `engines/excerpting/SPEC.md` (sections 6.2, 7.1)
- `NEXT.md` (design decisions DD-S3-1 through DD-S3-9)
- `reference/SPEC_ERRATA.md` (SPEC-NOTE-8, SPEC-NOTE-9)

**Governing spec:** SPEC.md lines 1397-1518 (section 7.1), lines 1260-1340 (section 6.2)
**Test count:** 37 test functions (target was >=30)

---

## Overall Assessment

**PASS with minor findings.** The implementation is well-structured, SPEC-compliant, and thoroughly tested. No critical bugs were found. The code correctly implements all 10 deterministic functions (F-DET-1 through F-DET-9 plus orchestrator), all 4 LA attribution rules, and handles Arabic text safely throughout.

Key strengths:
- Correct LA rule cascade order: LA-4 -> LA-1 -> LA-2 -> LA-3 (matching SPEC section 7.1)
- Shared `_compute_layer_coverages()` helper avoids code duplication between F-DET-3 and F-DET-9
- Evidence detection correctly uses plain substring matching (DD-S3-8), with empirical justification
- D-023 metadata pass-through is complete across all 33 ExcerptRecord fields
- `school=None` explicitly passed (DD-S3-1, DD8 Pattern 1)
- SPEC deviations properly documented in SPEC_ERRATA.md (SPEC-NOTE-8, SPEC-NOTE-9)
- No Arabic text safety violations (no `.lower()`, `.upper()`, `.strip()` on Arabic; no `\d` in regex)
- No off-by-one errors in word-to-char conversion (verified against `_build_token_char_map` exclusive-end convention)

---

## CRITICAL — Bugs that produce wrong output

None found.

---

## HIGH — Edge cases that could fail under specific conditions

### H-1: Missing adjacency check in layer split-point merging

**File:** `phase3_deterministic.py` lines 124-133
**SPEC ref:** SPEC 7.1 F-DET-3 step 2; NEXT.md DD-S3-7

The `_compute_layer_coverages()` merge logic checks three conditions:
1. Same `layer_type` and `author_canonical_id`
2. Previous merged segment's end is in `layer_split_points`

But DD-S3-7 explicitly requires a fourth condition: **"the second segment's start follows immediately"** (i.e., `layer.start == merged[-1][2]`). This adjacency check is absent.

```python
# Current (line 125-129):
if (
    merged
    and merged[-1][0].layer_type == layer.layer_type
    and merged[-1][0].author_canonical_id == layer.author_canonical_id
    and merged[-1][2] in split_set
):

# Should be:
if (
    merged
    and merged[-1][0].layer_type == layer.layer_type
    and merged[-1][0].author_canonical_id == layer.author_canonical_id
    and merged[-1][2] in split_set
    and layer.start == merged[-1][2]  # DD-S3-7: "start follows immediately"
):
```

**Impact analysis:** With valid input (I-AC-2 guarantees full layer coverage), segments at split points are always adjacent, so the missing check is inert. The pathological case requires BOTH an I-AC-2 violation (gap between layers) AND a split point at the exact gap boundary — two upstream bugs simultaneously. Risk is negligible in production, but the fix is trivial and adds defense-in-depth per the project's "fix the edge case" philosophy.

**Recommended action:** Add `and layer.start == merged[-1][2]` to the merge condition. Add a test with non-adjacent same-type segments where the first ends at a split point, verifying they are NOT merged.

---

## MEDIUM — Code quality issues and SPEC ambiguities

### M-1: `review_flags` set to `["llm_enrichment_failed"]` for DEPENDENT units unnecessarily

**File:** `phase3_deterministic.py` lines 583-588
**SPEC ref:** I-ER-4 model validator (contracts.py line 557-565)

```python
if unit.self_containment in (
    SelfContainmentLevel.PARTIAL,
    SelfContainmentLevel.DEPENDENT,
):
    review_flags = ["llm_enrichment_failed"]
```

For **PARTIAL** units, this flag is REQUIRED by I-ER-4 (validator requires either `context_hint` or `llm_enrichment_failed` when `self_containment=PARTIAL`). Correct.

For **DEPENDENT** units, the I-ER-4 validator only checks that `self_containment_notes` exists and `context_hint is None`. It does NOT require `llm_enrichment_failed`. Setting this flag for DEPENDENT is:
- **Semantically incorrect:** DEPENDENT self-containment was assigned by Phase 2, not because LLM enrichment failed
- **Functionally harmless:** The validator doesn't check it, and Session 4 will reset review_flags

**Recommended action:** Split the condition to only set the flag for PARTIAL:
```python
review_flags: list[str] = []
if unit.self_containment == SelfContainmentLevel.PARTIAL:
    review_flags = ["llm_enrichment_failed"]
```

### M-2: Multi-layer test fixture has 1-character gap between layers

**File:** `conftest.py` lines 466-510 (`_make_multi_layer_chunk`)
**SPEC ref:** I-AC-2 (every character attributed to exactly one layer)

The fixture creates:
- MATN layer: `start=0, end=35` (length of "قال ابن مالك كلامنا لفظ مفيد كاستقم")
- SHARH layer: `start=36, end=len(full_text)` (starts after the joining space)

Position 35 (the space between MATN and SHARH text) is not covered by any layer. This violates I-AC-2. While it doesn't affect test outcomes (the 1-char gap barely impacts coverage percentages), it means tests run on data that real production code would never produce.

Per `feedback_fixture_fidelity.md`: "Verify hand-crafted fixtures match real data format."

**Recommended action:** Either:
- Extend MATN to `end=36` (cover the space), OR
- Extend SHARH to `start=35`, OR
- Use `_MATN_END = len(_MATN_TEXT) + 1` and `_SHARH_START = _MATN_END` to eliminate the gap

### M-3: F-DET-6 `compute_page_range` uses magic sentinel for last page

**File:** `phase3_deterministic.py` line 388

```python
page_end = offsets[i] if i < len(offsets) else char_end + 1_000_000
```

The sentinel `char_end + 1_000_000` is an arbitrary large number to represent "extends to end of text." While functionally correct (the overlap check only needs `page_end > char_start`), this is fragile:
- The number has no semantic meaning
- A future refactor might compare `page_end` to the actual text length

**Recommended action:** Use a named constant or document the sentinel:
```python
_LAST_PAGE_SENTINEL = float('inf')  # or sys.maxsize
```
Or pass `assembled_text_len` as a parameter and use it as the last page's end.

### M-4: SPEC internal tension — LA-2 catches 2-layer cases that LA-3 condition (b) would flag

**SPEC ref:** SPEC section 6.2 LA-3 vs section 7.1 F-DET-3 algorithm

SPEC section 6.2 defines LA-3 as firing when "the dominant layer has <60% coverage." This condition is independent of layer count.

SPEC section 7.1 F-DET-3 defines the rule cascade as LA-4 -> LA-1 -> LA-2 -> LA-3, where LA-2 catches ALL 2-layer cases before LA-3 can evaluate condition (b).

Result: a 2-layer unit with dominant layer at 55% (neither layer >= 80%) triggers LA-2 (outermost wins), bypassing LA-3's safety check (EX-M-001 warning + consensus verification). The implementation correctly follows the section 7.1 algorithm.

This is a **SPEC design question**, not a code bug. The test `test_la2_even_with_dominant_below_60pct` documents this as intentional behavior. If the intent is for <60% dominant to always trigger LA-3 (even with 2 layers), section 7.1 needs a coverage guard on LA-2: "if no layer has >=80% AND exactly 2 layers **AND dominant >= 60%**."

**Recommended action:** Document this SPEC tension in SPEC_ERRATA.md. No code change unless the SPEC is updated.

### M-5: Test name/comment mismatch in `test_la2_even_with_dominant_below_60pct`

**File:** `test_phase3_deterministic.py` line 221-255

The test name says "dominant below 60%" but the actual fixture creates MATN=~37%, SHARH=~63%. The dominant (SHARH at 63%) is **above** 60%, not below. The test verifies the right behavior (LA-2 fires), but the name and comment are misleading.

**Recommended action:** Rename to `test_la2_two_layers_regardless_of_coverage` or adjust the fixture so the dominant is actually <60%.

---

## LOW — Style, documentation, and minor test coverage gaps

### L-1: No test for F-DET-6 with all overlapping pages having `page_number_int=None`

**File:** `test_phase3_deterministic.py` — `TestPageRange` class
**SPEC ref:** SPEC 7.1 F-DET-6: "If ALL overlapping pages have `page_number_int=None`, return `None`."

The test suite covers single-page, multi-page, and empty pages. Missing: a multi-page scenario where all overlapping pages have `page_number_int=None`, verifying `compute_page_range` returns `None`.

### L-2: No test for F-DET-5 evidence deduplication at same position

**File:** `test_phase3_deterministic.py` — `TestEvidenceRefs` class
**SPEC ref:** NEXT.md Function 5: "If the same marker matches at the same position from overlapping patterns, deduplicate."

The deduplication logic (`seen_positions` set) exists but has no dedicated test exercising it.

### L-3: No test for F-DET-9 `compute_quoted_scholars` with layer split-point merging

**File:** `test_phase3_deterministic.py` — `TestQuotedScholars` class
**SPEC ref:** NEXT.md Function 9: "You must also perform the same layer segment merging as Function 3 Step 2"

The `compute_quoted_scholars` function uses `_compute_layer_coverages` (which handles split-point merging), but no test verifies that split-point merging affects quoted scholar detection. The `test_split_point_merging` test only exercises F-DET-3.

### L-4: F-DET-8 `filter_relevant_footnotes` only finds first marker occurrence

**File:** `phase3_deterministic.py` line 443

```python
pos = assembled_text.find(pattern)
```

`str.find()` returns the first occurrence. If `⌜1⌝` appears multiple times in `assembled_text`, only the first position is checked. This relies on the upstream invariant EX-A-005 (duplicate footnote ref_marker detected in Phase 1). With valid input, each marker appears exactly once.

Not a bug (upstream guarantees uniqueness), but a defensive `findall()` + position check would be more robust.

### L-5: F-DET-6 `first_volume` takes first overlapping page only

**File:** `phase3_deterministic.py` lines 398-401

If the first overlapping page has `volume=None` and subsequent pages have valid volumes, the function returns `volume=None` despite volume information being available. Per SPEC: "volume: take from the first overlapping PhysicalPage.volume." The implementation matches the SPEC. This is a SPEC design choice, not a bug, but worth noting for future improvement.

### L-6: No `KNOWN_LIMITATIONS.md` for excerpting engine

The normalization engine documents deviations from SPEC thresholds in `engines/normalization/KNOWN_LIMITATIONS.md`. The excerpting engine has none despite two OPEN errata (SPEC-NOTE-8, SPEC-NOTE-9). Consider creating `engines/excerpting/KNOWN_LIMITATIONS.md` with these entries.

---

## Verification Checklist

| Check | Status | Notes |
|-------|--------|-------|
| F-DET-1 excerpt_id format | PASS | `exc_{source_id}_{div_id}_{chunk_index}_{unit_index}` |
| F-DET-2 substring (not split-rejoin) | PASS | Preserves `\n\n` paragraph breaks |
| F-DET-3 LA rule cascade order | PASS | LA-4 -> LA-1 -> LA-2 -> LA-3 |
| F-DET-3 LA-4 threshold (100%) | PASS | `>= 1.0` |
| F-DET-3 LA-1 threshold (80%) | PASS | `>= 0.8` |
| F-DET-3 LA-2 outermost rule | PASS | `max(coverages, key=_LAYER_LEVEL)` |
| F-DET-3 LA-3 EX-M-001 emission | PASS | `logger.warning(ExcerptingErrorCodes.EX_M_001, ...)` |
| F-DET-3 split-point merging (DD-S3-7) | PARTIAL | Missing adjacency check (H-1) |
| F-DET-4 deduplication | PASS | `set` + `list` preserves insertion order |
| F-DET-5 plain substring matching (DD-S3-8) | PASS | No word-boundary checks |
| F-DET-5 Quran `﴿...﴾` detection | PASS | Regex with U+FD3F/U+FD3E |
| F-DET-5 snippet clamping | PASS | `max(0, pos-25)` / `min(len, pos+len+25)` |
| F-DET-6 page range from join_points | PASS | Correct overlap computation |
| F-DET-8 footnote `⌜N⌝` matching | PASS | U+231C/U+231D pattern search |
| F-DET-9 quoted scholars role assignment | PASS | MATN in non-MATN primary = classification_frame |
| F-DET-9 shared layer merging with F-DET-3 | PASS | Uses same `_compute_layer_coverages` |
| D-023 metadata pass-through | PASS | All 33 ExcerptRecord fields populated |
| school=None explicit (DD-S3-1) | PASS | Line 619: `school=None` |
| attribution_confidence=None (DD-S3-6) | PASS | Line 617 |
| Arabic text safety | PASS | No `.lower()`, `.strip()`, no `\d` in regex |
| Error codes from SPEC | PASS | Only EX-M-001 used (from `ExcerptingErrorCodes`) |
| SPEC deviations documented | PASS | SPEC-NOTE-8, SPEC-NOTE-9 in SPEC_ERRATA.md |
| Test count | PASS | 37 functions (target >=30) |
| Tests cover all 10 functions | PASS | F-DET-1 through F-DET-9 + orchestrator |
| Tests cover all 4 LA rules | PASS | LA-1, LA-2, LA-3, LA-4 + split-point merging |
| Off-by-one in word-to-char conversion | PASS | `_build_token_char_map` exclusive end used correctly |

---

## Summary Statistics

| Severity | Count | Action Required |
|----------|-------|-----------------|
| CRITICAL | 0 | — |
| HIGH | 1 | Fix before Session 4 |
| MEDIUM | 5 | Fix before transition gate |
| LOW | 6 | Track for future improvement |

**Recommendation:** The implementation is ready for Session 4 after addressing H-1 (one-line fix). The MEDIUM findings should be resolved before the transition gate review but do not block development progress.
