# NEXT — Excerpting Engine: Session 1 Fix (F-1 + F-2)

## Current Position

- Excerpting Phase 1: implemented in commit 1ae4a991
- Architect review: **BLOCKED** — 2 findings
- Test baseline: **81 passed** (excerpting), 503 passed (normalization)
- Review checklist: `reference/archive/sessions/reviews/review_excerpting_session_1.md`

## What to Do

Fix two findings from the architect's 3-round review. Both are surgical — no new features, no SPEC changes.

### F-1: Stale join_point offsets after footnote renumbering

**Bug:** `renumber_footnotes()` can change `assembled_text` length (e.g., `⌜1⌝` → `⌜10⌝` adds 1 char per marker). But `assembly_metadata.join_points` are never updated. `rebase_text_layers()` uses these stale offsets, producing silently wrong layer attribution coordinates.

**Confirmed on real data:** 03_fiqh fixture, `div_src_test0001_5_011`: 19 pages each with `⌜1⌝`. After renumbering, markers 10–19 become 2-digit → 10-char text growth. 9 join points have stale offsets (drift 1–9 chars). All 6 validation checks pass silently.

**Fix (3 parts):**

#### Part 1: Add helper function

Add this function in phase1_assembly.py, in the "Utility Functions" section (after `_should_insert_space_mid_sentence`, before the `§4.2` section header):

```python
def _adjust_join_points_after_renumber(
    old_text: str,
    new_text: str,
    join_points: list[JoinPoint],
) -> list[JoinPoint]:
    """Adjust join_point char_offset_in_assembled after footnote renumbering.

    When renumbering changes marker lengths (e.g., ⌜1⌝→⌜10⌝), character
    offsets downstream of the change shift. This recomputes offsets to match
    the renumbered text.

    Returns join_points unchanged if text length didn't change.
    """
    if len(old_text) == len(new_text) or not join_points:
        return join_points

    # Find all marker positions in old and new text
    old_markers = list(_FOOTNOTE_MARKER_RE.finditer(old_text))
    new_markers = list(_FOOTNOTE_MARKER_RE.finditer(new_text))

    # Build cumulative delta table
    # Each entry: (position_in_old_text after this marker, cumulative_shift)
    deltas: list[tuple[int, int]] = []
    cumulative = 0
    for om, nm in zip(old_markers, new_markers):
        delta = (nm.end() - nm.start()) - (om.end() - om.start())
        if delta != 0:
            cumulative += delta
            deltas.append((om.end(), cumulative))

    if not deltas:
        return join_points

    # Adjust each join_point's char_offset_in_assembled
    adjusted: list[JoinPoint] = []
    for jp in join_points:
        shift = 0
        for pos, cum_delta in deltas:
            if jp.char_offset_in_assembled >= pos:
                shift = cum_delta
        if shift != 0:
            adjusted.append(
                JoinPoint(
                    after_unit_index=jp.after_unit_index,
                    before_unit_index=jp.before_unit_index,
                    boundary_type=jp.boundary_type,
                    separator_used=jp.separator_used,
                    char_offset_in_assembled=jp.char_offset_in_assembled + shift,
                )
            )
        else:
            adjusted.append(jp)

    return adjusted
```

#### Part 2: Apply in run_phase1

In `run_phase1()`, replace the step 4 loop (the `for chunk in merged_chunks:` block, lines ~1396–1429) with the following. The key changes are marked with `# F-1 fix`:

```python
    for chunk in merged_chunks:
        indices = chunk.assembly_metadata.constituent_unit_indices
        flags = aggregate_content_flags(content_units, indices)
        all_fn = aggregate_footnotes(content_units, indices)

        # Filter footnotes to only those whose markers appear in this chunk's text
        chunk_fn = [
            fn for fn in all_fn if f"⌜{fn.ref_marker}⌝" in chunk.assembled_text
        ]

        new_text, new_fn, rmap = renumber_footnotes(chunk.assembled_text, chunk_fn)

        # F-1 fix: adjust join_points for renumbering-induced offset shifts
        adjusted_jps = _adjust_join_points_after_renumber(
            chunk.assembled_text, new_text,
            chunk.assembly_metadata.join_points,
        )

        # Save ADJUSTED join_points for split chunk layer rebasing (step 6)
        original_join_points[chunk.div_id] = adjusted_jps

        pages = collect_physical_pages(content_units, indices)
        wc = _count_arabic_words(new_text)
        tt = len(new_text.split())

        finalized.append(
            chunk.model_copy(
                update={
                    "assembled_text": new_text,
                    "word_count": wc,
                    "total_tokens": tt,
                    "footnotes": new_fn,
                    "content_flags": flags,
                    "physical_pages": pages,
                    "assembly_metadata": chunk.assembly_metadata.model_copy(
                        update={
                            "footnote_renumber_map": rmap,
                            "join_points": adjusted_jps,  # F-1 fix
                        }
                    ),
                }
            )
        )
```

Key changes vs current code:
1. `_adjust_join_points_after_renumber()` called after `renumber_footnotes()`
2. `original_join_points[chunk.div_id]` now stores ADJUSTED join_points (moved AFTER renumbering — was BEFORE)
3. Finalized chunk's `assembly_metadata.join_points` explicitly set to `adjusted_jps`

#### Part 3: Add regression test

Add to `engines/excerpting/tests/test_phase1_metadata.py`, at the end of the file:

```python
class TestJoinPointAdjustmentAfterRenumber:
    """Regression test for F-1: stale join_points after footnote renumbering."""

    def test_join_points_adjusted_for_multi_digit_renumbering(self) -> None:
        """15 pages each with ⌜1⌝ → markers 10-15 become 2-digit.

        Join_point offsets must reflect the renumbered text, not the original.
        """
        from engines.excerpting.contracts import ExcerptingConfig
        from engines.excerpting.src.phase1_assembly import run_phase1
        from engines.excerpting.tests.conftest import (
            _make_content_unit,
            _make_normalized_package,
        )
        from engines.normalization.contracts import (
            BoundaryContinuity,
            BoundaryContinuityType,
            ContinuityDetectionMethod,
            Footnote,
            FootnoteType,
        )

        # Build 15 content units, each with ⌜1⌝ in text and one footnote
        units = []
        for i in range(15):
            bc = None
            if i < 14:  # All but last have boundary_continuity
                bc = BoundaryContinuity(
                    type=BoundaryContinuityType.MID_PARAGRAPH,
                    confidence=0.9,
                    detection_method=ContinuityDetectionMethod.PUNCTUATION_ANALYSIS,
                    continuation_hint=None,
                )
            units.append(
                _make_content_unit(
                    unit_index=i,
                    primary_text=f"نص الصفحة رقم {i + 1} في الكتاب ⌜1⌝ وبقية النص هنا",
                    boundary_continuity=bc,
                    footnotes=[
                        Footnote(
                            ref_marker="1",
                            text=f"حاشية الصفحة {i + 1}",
                            footnote_type=FootnoteType.AUTHOR_ORIGINAL,
                            confidence=0.9,
                        )
                    ],
                )
            )

        pkg = _make_normalized_package(
            content_units=units,
            num_units=15,
        )
        config = ExcerptingConfig()
        chunks, results = run_phase1(pkg, config)

        assert len(chunks) >= 1
        # All validation must pass
        for r in results:
            assert r["status"] in ("pass", "warning"), (
                f"{r['check']} failed: {r['detail']}"
            )

        # The chunk should have renumbered markers (10+ are 2-digit)
        chunk = chunks[0]
        assert "⌜10⌝" in chunk.assembled_text, (
            "Marker 10 should be 2-digit after renumbering"
        )
        assert "⌜15⌝" in chunk.assembled_text, (
            "Marker 15 should be 2-digit after renumbering"
        )

        # Verify join_points: each offset must point to the correct position
        # in the RENUMBERED assembled_text
        for jp in chunk.assembly_metadata.join_points:
            offset = jp.char_offset_in_assembled
            sep = jp.separator_used
            assert offset <= len(chunk.assembled_text), (
                f"JP offset {offset} exceeds text length "
                f"{len(chunk.assembled_text)}"
            )
            # The separator should appear at the offset position
            if sep:
                actual = chunk.assembled_text[offset : offset + len(sep)]
                assert actual == sep, (
                    f"JP at offset {offset}: expected separator "
                    f"{repr(sep)}, got {repr(actual)}"
                )
```

### F-2: Unused imports (lint not clean)

Run:
```bash
ruff check --fix engines/excerpting/tests/
```

This auto-removes all 17 unused imports.

## Read First

1. `engines/excerpting/src/phase1_assembly.py` — the file you're modifying
2. `engines/excerpting/tests/test_phase1_metadata.py` — where the new test goes
3. `reference/archive/sessions/reviews/review_excerpting_session_1.md` — the review findings

## Do NOT Do

- Do NOT modify `contracts.py`.
- Do NOT modify any existing test — only ADD the new test class.
- Do NOT change `renumber_footnotes()` signature or return type.
- Do NOT change any other function behavior — only `run_phase1()` and the new helper.
- Do NOT run CC self-review — just run pytest. The architect will re-verify.

## Verification

```bash
# 1. All tests pass (expect 82+ after adding the new test)
python -m pytest engines/excerpting/tests/ -v --tb=short

# 2. Lint clean
ruff check engines/excerpting/src/phase1_assembly.py engines/excerpting/tests/

# 3. Normalization regression
python -m pytest engines/normalization/tests/ --tb=short

# 4. F-1 specific: run the regression test in isolation
python -m pytest engines/excerpting/tests/test_phase1_metadata.py::TestJoinPointAdjustmentAfterRenumber -v --tb=long
```

## After This

Push the fix commit. Architect will do abbreviated re-verification:
1. Re-run the F-1 trigger test on 03_fiqh's 19-marker division
2. Confirm join_point offsets are now correct
3. Re-run lint
4. Deliver final ACCEPT or BLOCKED
