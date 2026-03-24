# Phase 3.1 Deterministic Metadata Assembly — Deep Code Review (Pass 2)

**Reviewer:** Claude Opus 4.6 (overnight autonomous, second-pass independent review)
**Date:** 2026-03-24
**Previous review:** Pass 1 (same session) found 1 HIGH, 5 MEDIUM, 6 LOW. This pass confirms all prior findings and adds 4 new findings.

**Files reviewed:**
- `engines/excerpting/src/phase3_deterministic.py` (637 lines)
- `engines/excerpting/tests/test_phase3_deterministic.py` (739 lines)
- `engines/excerpting/tests/conftest.py` (598 lines)
- `engines/excerpting/contracts.py` (ExcerptRecord model, validators, sub-models, error codes)
- `engines/excerpting/src/phase2_classify.py` lines 105-123 (`_build_token_char_map`)
- `engines/excerpting/SPEC.md` sections 6.2 (lines 1260-1340) and 7.1 (lines 1397-1518)
- `NEXT.md` (design decisions DD-S3-1 through DD-S3-9)
- `reference/SPEC_ERRATA.md` (SPEC-NOTE-8, SPEC-NOTE-9)

**Governing spec:** SPEC.md §7.1 (10 deterministic functions), §6.2 (layer attribution rules LA-1 through LA-4)
**Test count:** 37 test functions, all passing (target was >= 30)

---

## Overall Assessment

**PASS with findings.** The implementation is well-structured and SPEC-compliant. No critical bugs found. All 10 deterministic functions are correctly implemented, the LA-1 through LA-4 rule cascade is correctly ordered, Arabic text is handled safely throughout, and D-023 metadata pass-through is complete across all 33 ExcerptRecord fields.

**Key strengths verified:**
- Correct LA rule cascade: LA-4 (100%) -> LA-1 (>=80%) -> LA-2 (2 layers, outermost) -> LA-3 (ambiguous)
- Shared `_compute_layer_coverages()` avoids code duplication between F-DET-3 and F-DET-9
- Evidence detection uses plain substring matching per DD-S3-8 (empirically justified)
- `_build_token_char_map` imported from phase2_classify.py (DD-S3-2), not duplicated
- Word-to-char conversion uses exclusive-end convention consistently — no off-by-one errors
- `school=None` explicitly passed (DD-S3-1, DD8 Pattern 1)
- No Arabic text safety violations (no `.lower()`, `.upper()`, `.strip()` on Arabic; no `\d` in regex)
- SPEC deviations documented in SPEC_ERRATA.md (SPEC-NOTE-8, SPEC-NOTE-9)

---

## CRITICAL — Bugs that produce wrong output

None found.

---

## HIGH — Edge cases that could produce wrong attribution or miss data

### H-1: Missing adjacency check in layer split-point merging (confirmed from Pass 1)

**File:** `phase3_deterministic.py` lines 124-133
**SPEC ref:** SPEC §7.1 F-DET-3 step 2; DD-S3-7

The merge condition checks same type/author and previous-end-in-split-set, but omits the explicit adjacency check `layer.start == merged[-1][2]` that DD-S3-7 requires ("the second segment's start follows immediately").

```python
# Current (line 125-129) — missing condition 3:
if (
    merged
    and merged[-1][0].layer_type == layer.layer_type              # condition 1
    and merged[-1][0].author_canonical_id == layer.author_canonical_id  # condition 1
    and merged[-1][2] in split_set                                # condition 2
    # MISSING: and layer.start == merged[-1][2]                   # condition 3
):
```

**Risk:** With valid I-AC-2 input, segments at split points are always adjacent, making this inert. Requires simultaneous I-AC-2 violation (gap) + split point at gap boundary. Fix is one line.

**Fix:** Add `and layer.start == merged[-1][2]` to the merge condition. Add test with gapped same-type segments at a split point, verifying they are NOT merged.

### H-2: Interleaved same-layer-type segments inflate "layer count" for LA rule dispatch (NEW)

**File:** `phase3_deterministic.py` lines 234, 245
**SPEC ref:** SPEC §6.2 LA-2 "exactly two layers", LA-3 "three or more layers"

When a teaching unit spans text with genuine interleaving (e.g., MATN-SHARH-MATN — a commentator quoting the matn, commenting, then quoting more matn), the `_compute_layer_coverages` function returns 3 entries (two MATN segments + one SHARH segment). The LA rules use `len(coverages)` for dispatch:

```
Actual interleaving:  MATN[0,50)  SHARH[50,80)  MATN[80,100)
Coverage entries:     [(MATN, 50%), (SHARH, 20%), (MATN, 30%)]
len(coverages) = 3   →  LA-3 fires (3+ entries, ambiguous)
```

But conceptually there are only 2 unique layer types (MATN and SHARH). With aggregation:
```
Aggregated:           MATN = 80%,  SHARH = 20%
2 unique layers       →  LA-1 fires (MATN >= 80%)
```

**Impact analysis:** The non-aggregated outcome (LA-3) is MORE conservative — it flags for consensus review instead of silently attributing. This is arguably safer than wrong silent attribution. The scenario requires a single teaching unit that spans a MATN→SHARH→MATN transition, which Phase 2's grouping by scholarly function tends to prevent (each transition would be a separate teaching unit).

**Why this matters:** In Islamic scholarly texts, sharh-with-embedded-matn is extremely common (the commentator quotes a verse of the matn, explains it, then quotes the next verse). If Phase 2 grouping occasionally produces a unit that spans this pattern, LA-3 fires unnecessarily, creating noise in the consensus queue.

**Classification:** MEDIUM-HIGH. No data corruption (conservative outcome), but potentially frequent false LA-3 triggers in multi-layer texts.

**Recommendation:** After the Phase 3 build is accepted, consider adding a coverage aggregation step by `(layer_type, author_canonical_id)` before applying LA rules. This is a design decision, not a bug fix — file as a future improvement in KNOWN_LIMITATIONS.md.

---

## MEDIUM — Code quality issues and SPEC ambiguities

### M-1: `review_flags` set unnecessarily for DEPENDENT units (confirmed from Pass 1)

**File:** `phase3_deterministic.py` lines 583-588

```python
if unit.self_containment in (
    SelfContainmentLevel.PARTIAL,
    SelfContainmentLevel.DEPENDENT,
):
    review_flags = ["llm_enrichment_failed"]
```

For **PARTIAL**: Required by I-ER-4 validator (bypasses context_hint requirement). Correct.
For **DEPENDENT**: I-ER-4 validator doesn't check review_flags. The flag is semantically wrong (DEPENDENT was assigned by Phase 2, not because enrichment failed) but functionally harmless.

**Fix:** Split condition: `if unit.self_containment == SelfContainmentLevel.PARTIAL:`

### M-2: Multi-layer test fixture violates I-AC-2 (confirmed from Pass 1)

**File:** `conftest.py` lines 466-510

`_make_multi_layer_chunk` creates MATN=[0, 35) and SHARH=[36, end), leaving position 35 (the space) uncovered. Real Phase 1 output never has this gap. The 1-char gap barely impacts coverage percentages, so tests pass, but they run on structurally invalid data.

**Fix:** Set `_SHARH_START = _MATN_END` (no gap) or `end=_MATN_END + 1` for MATN (cover the space).

### M-3: Magic sentinel in page range last-page computation (confirmed from Pass 1)

**File:** `phase3_deterministic.py` line 388

```python
page_end = offsets[i] if i < len(offsets) else char_end + 1_000_000
```

The `+ 1_000_000` is semantically meaningless. Works because the overlap check only compares against `[char_start, char_end)`, but fragile under refactoring.

**Fix:** Use `float('inf')` or pass `assembled_text_length` as parameter.

### M-4: SPEC LA-2/LA-3 tension — condition (b) is unreachable (confirmed from Pass 1)

**SPEC ref:** §6.2 LA-3 vs §7.1 F-DET-3

SPEC §6.2 defines LA-3 as firing when "the dominant layer has <60% coverage." SPEC §7.1 defines rule order LA-4→LA-1→LA-2→LA-3, where LA-2 catches ALL 2-layer cases before LA-3 evaluates condition (b). Result: a 2-layer unit with 55% dominant triggers LA-2, bypassing LA-3's EX-M-001 safety check.

The implementation correctly follows §7.1's algorithm. Test `test_la2_even_with_dominant_below_60pct` documents this as intentional. This is a SPEC design question, not a code bug.

**Action:** Document in SPEC_ERRATA.md. No code change.

### M-5: Test name misleading — dominant is ABOVE 60%, not below (confirmed from Pass 1)

**File:** `test_phase3_deterministic.py` lines 221-255

`test_la2_even_with_dominant_below_60pct` creates MATN=~37%, SHARH=~63%. The dominant (SHARH at 63%) is ABOVE 60%. The test verifies correct behavior (LA-2 fires) but the name is misleading.

**Fix:** Rename to `test_la2_two_layers_regardless_of_dominant_coverage` or adjust fixture so dominant is actually <60%.

### M-6: Unused `primary_text` parameter in `filter_relevant_footnotes` (NEW)

**File:** `phase3_deterministic.py` lines 427-452

```python
def filter_relevant_footnotes(
    primary_text: str,        # <-- NEVER USED in function body
    assembled_text: str,
    all_footnotes: list[Footnote],
    char_start: int,
    char_end: int,
) -> list[Footnote]:
```

The `primary_text` parameter was specified in NEXT.md's function signature but is never referenced inside the function. All footnote searching is done against `assembled_text`. The parameter is dead code — it's passed from the orchestrator (line 564) but discarded.

**Risk:** None (no wrong behavior). But dead parameters violate the "minimum complexity" principle and confuse future readers about what data the function needs.

**Fix:** Either remove the parameter (and update the orchestrator call at line 564), or document why it exists (e.g., "reserved for future snippet validation").

### M-7: Missing test for `author_canonical_id=None` → `"unknown"` fallback (NEW)

**File:** `phase3_deterministic.py` lines 219, 229, 239, 258

All four LA-rule return paths use `author_id=top_layer.author_canonical_id or "unknown"`. This fallback is never tested — all test fixtures set `author_canonical_id` to a value. The `_make_assembled_chunk` default has `author_canonical_id=None` (single-layer), but the orchestrator test doesn't assert `author_id == "unknown"`.

**Risk:** Low (the `or "unknown"` pattern is standard Python), but the I-ER-5 validator requires `author_id` to be non-empty. If someone changed the fallback, the validator would catch it — but a dedicated test is clearer.

**Fix:** Add a test in `TestLayerAttribution` with `author_canonical_id=None`, asserting `result.author_id == "unknown"`.

---

## LOW — Style, documentation, and minor test coverage gaps

### L-1: No test for F-DET-6 with all pages having `page_number_int=None` (confirmed)

**SPEC:** "If ALL overlapping pages have page_number_int=None, return None."
**Gap:** No test exercises this path. Only empty-pages and valid-pages are tested.

### L-2: No test for F-DET-5 evidence deduplication at same position (confirmed)

**SPEC:** "If the same marker matches at the same position from overlapping patterns, deduplicate."
**Gap:** The `seen_positions` set exists but no test exercises the dedup path.

### L-3: No test for F-DET-9 split-point merging effect on quoted scholars (confirmed)

**SPEC:** "You must also perform the same layer segment merging as Function 3 Step 2."
**Gap:** `compute_quoted_scholars` uses `_compute_layer_coverages` (shared), but no test verifies that split-point merging changes quoted scholar detection. Only F-DET-3 tests exercise split-point merging.

### L-4: F-DET-8 `filter_relevant_footnotes` finds only first marker occurrence (confirmed)

**File:** `phase3_deterministic.py` line 443

```python
pos = assembled_text.find(pattern)  # Returns FIRST occurrence only
```

If `⌜1⌝` appeared at two positions, only the first is checked against the unit range. Upstream invariants (Phase 1 footnote renumbering) guarantee unique markers within a chunk, making this safe in practice.

### L-5: `first_volume` takes first overlapping page only (confirmed)

**File:** `phase3_deterministic.py` lines 398-401

If the first overlapping page has `volume=None` but later pages have valid volumes, `volume=None` is returned. Matches SPEC ("take from the first overlapping PhysicalPage.volume") but loses available information.

### L-6: No `KNOWN_LIMITATIONS.md` for excerpting engine (confirmed)

SPEC-NOTE-8 and SPEC-NOTE-9 are OPEN errata with implementation deviations. The normalization engine documents such deviations in KNOWN_LIMITATIONS.md. The excerpting engine should have one too.

### L-7: No validation that `text_layers` are sorted by position (NEW)

**File:** `phase3_deterministic.py` lines 124-135

`_compute_layer_coverages` iterates `text_layers` sequentially and merges "consecutive" entries. If text_layers were unsorted, the merge step would miss valid merge candidates and produce incorrect results. Phase 1's layer rebasing (§4.6) should guarantee sort order, but no assertion or sort-before-merge exists in Phase 3.

**Risk:** Low (upstream guarantee), but a one-line `assert` would add defense-in-depth.

### L-8: No test for F-DET-9 with single-layer source (empty result) (NEW)

**File:** `test_phase3_deterministic.py` — `TestQuotedScholars`

When all layers match the primary layer (single-layer source), `compute_quoted_scholars` should return `[]`. This path is exercised indirectly by the orchestrator test (single-layer default chunk), but no dedicated test asserts it.

---

## Verification Matrix

| Check | Status | Detail |
|-------|--------|--------|
| **F-DET-1** excerpt_id format | PASS | `exc_{source_id}_{div_id}_{chunk_index}_{unit_index}` |
| **F-DET-2** substring extraction | PASS | Preserves `\n\n`; not split-rejoin |
| **F-DET-3** LA rule cascade order | PASS | LA-4 → LA-1 → LA-2 → LA-3 |
| **F-DET-3** LA-4 threshold (100%) | PASS | `>= 1.0`, integer division ensures exact 1.0 |
| **F-DET-3** LA-1 threshold (80%) | PASS | `>= 0.8` |
| **F-DET-3** LA-2 outermost rule | PASS | `max(coverages, key=_LAYER_LEVEL)` |
| **F-DET-3** LA-3 EX-M-001 emission | PASS | `logger.warning(EX_M_001, ...)` |
| **F-DET-3** split-point merging | PARTIAL | Missing adjacency check (H-1) |
| **F-DET-3** interleaved same-type | DESIGN | Treated as separate entries (H-2) |
| **F-DET-4** deduplication | PASS | `set` + `list` preserves insertion order |
| **F-DET-5** plain substring (DD-S3-8) | PASS | No word-boundary checks |
| **F-DET-5** Quran `﴿...﴾` regex | PASS | `\uFD3F([^\uFD3E]+)\uFD3E`, no `\d` |
| **F-DET-5** snippet clamping | PASS | `max(0, pos-25) : min(len, pos+len+25)` |
| **F-DET-6** page range computation | PASS | Correct overlap, fast single-page path |
| **F-DET-8** footnote `⌜N⌝` matching | PASS | U+231C/U+231D pattern |
| **F-DET-9** quoted scholars role | PASS | MATN in non-MATN = classification_frame |
| **F-DET-9** shared merging | PASS | Same `_compute_layer_coverages` |
| **D-023** metadata pass-through | PASS | All 33 fields explicitly populated |
| **school=None** (DD-S3-1) | PASS | Line 619 |
| **attribution_confidence=None** (DD-S3-6) | PASS | Line 617 |
| **Arabic text safety** | PASS | No `.lower()`/`.strip()`/`\d` violations |
| **Error codes** | PASS | Only EX-M-001 used |
| **SPEC deviations documented** | PASS | SPEC-NOTE-8, SPEC-NOTE-9 |
| **Off-by-one errors** | PASS | Exclusive-end consistent throughout |
| **Test count** | PASS | 37 functions (>= 30 target) |
| **All 10 functions tested** | PASS | F-DET-1 through F-DET-9 + orchestrator |
| **All 4 LA rules tested** | PASS | LA-1, LA-2, LA-3, LA-4 + split-point |

---

## Summary Statistics

| Severity | Count | Pass 1 | New | Action |
|----------|-------|--------|-----|--------|
| CRITICAL | 0 | 0 | 0 | — |
| HIGH | 2 | 1 | 1 | H-1: fix before Session 4. H-2: track as design item |
| MEDIUM | 7 | 5 | 2 | Fix before transition gate |
| LOW | 8 | 6 | 2 | Track for future improvement |

**Recommendation:** The implementation is ready for Session 4 after addressing H-1 (one-line adjacency check). H-2 should be filed in KNOWN_LIMITATIONS.md as a design observation — the conservative LA-3 outcome does not corrupt data. MEDIUM findings should be resolved before the transition gate but do not block development.

**Test suite assessment:** 37 tests cover all 10 functions and all 4 LA rules. The identified test gaps (L-1, L-2, L-3, L-7, L-8, M-7) are edge cases that real data is unlikely to hit, but adding them would strengthen the safety net for future refactoring.
