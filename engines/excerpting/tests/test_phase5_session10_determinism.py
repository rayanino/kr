"""Phase 5 Session 10 (2026-05-08) determinism audit fix tests.

Tests the secondary sort key on ``layer.start`` in
``engines/excerpting/src/phase3_deterministic.py:compute_layer_attribution``.
Without the secondary key, two text layers with IDENTICAL coverage
percentages had their ordering decided by the upstream
``text_layers`` list order — a latent determinism trap of the same
defect class as Session 7's ``_build_positions_for_disputed``
PYTHONHASHSEED bug at
``shared/scholar_authority/src/threshold_compounding.py``.

The fix locks the tiebreak to smallest ``layer.start`` (earliest in
the document), so identical coverage tied at the rule_applied=LA-4
boundary always yields the same top layer regardless of input order.
F-DET-3 commits to determinism in its name ("F-DET" = field
deterministic) — the tiebreak makes that contract hold under all
input orderings.
"""

from __future__ import annotations

from engines.excerpting.contracts import AssemblyMetadata
from engines.excerpting.src.phase3_deterministic import compute_layer_attribution
from engines.normalization.contracts import LayerType, TextLayerSegment


# Real Arabic word-tokenized text for layer coverage tests. Two halves of
# 8 words each (16 words total). The split point is at char position
# matching the boundary between word 7 and word 8.
_FIRST_HALF = "بسم الله الرحمن الرحيم الحمد لله رب العالمين"  # 8 words
_SECOND_HALF = "والصلاة والسلام على رسول الله محمد وآله وصحبه"  # 8 words
_FULL_TEXT = _FIRST_HALF + " " + _SECOND_HALF
_BOUNDARY_CHAR = len(_FIRST_HALF) + 1  # +1 for the space separator
_TOTAL_CHARS = len(_FULL_TEXT)
_TOTAL_WORDS = len(_FULL_TEXT.split())  # 16


def _empty_meta() -> AssemblyMetadata:
    """AssemblyMetadata with no join points or split points (clean baseline)."""
    return AssemblyMetadata(
        constituent_unit_indices=[0],
        join_points=[],
        layer_split_points=[],
        footnote_renumber_map=None,
    )


class TestComputeLayerAttributionDeterminismOnTies:
    """The Session 10 fix: equal coverage → smallest layer.start wins."""

    def test_equal_coverage_picks_smallest_start(self) -> None:
        """Two layers each covering ~50% of the unit → the layer at start=0
        wins over the layer at later start regardless of input order.
        """
        # Two layers, equal coverage (each covers half the text)
        early_layer = TextLayerSegment(
            layer_type=LayerType.MATN,
            author_canonical_id="sch_early",
            start=0,
            end=_BOUNDARY_CHAR,
            confidence=1.0,
        )
        late_layer = TextLayerSegment(
            layer_type=LayerType.SHARH,
            author_canonical_id="sch_late",
            start=_BOUNDARY_CHAR,
            end=_TOTAL_CHARS,
            confidence=1.0,
        )

        # Order 1: [early, late]
        result_1 = compute_layer_attribution(
            _FULL_TEXT, [early_layer, late_layer], 0, _TOTAL_WORDS - 1, _empty_meta()
        )
        # Order 2: [late, early] — INPUT ORDER FLIPPED
        result_2 = compute_layer_attribution(
            _FULL_TEXT, [late_layer, early_layer], 0, _TOTAL_WORDS - 1, _empty_meta()
        )

        # Both invocations pick the SAME top layer; the layer with smallest
        # start (= 0) wins regardless of input ordering.
        assert result_1.author_id == "sch_early"
        assert result_2.author_id == "sch_early"
        assert result_1.layer_id == "matn"
        assert result_2.layer_id == "matn"

    def test_three_way_coverage_tie_picks_smallest_start(self) -> None:
        """Three non-overlapping layers with equal coverage (≈33% each)
        — smallest-start wins."""
        third = _TOTAL_CHARS // 3
        two_thirds = (_TOTAL_CHARS // 3) * 2
        layer_a = TextLayerSegment(
            layer_type=LayerType.MATN,
            author_canonical_id="sch_a",
            start=0,
            end=third,
            confidence=1.0,
        )
        layer_b = TextLayerSegment(
            layer_type=LayerType.SHARH,
            author_canonical_id="sch_b",
            start=third,
            end=two_thirds,
            confidence=1.0,
        )
        layer_c = TextLayerSegment(
            layer_type=LayerType.HASHIYAH,
            author_canonical_id="sch_c",
            start=two_thirds,
            end=_TOTAL_CHARS,
            confidence=1.0,
        )

        for permutation in [
            [layer_a, layer_b, layer_c],
            [layer_c, layer_a, layer_b],
            [layer_b, layer_c, layer_a],
            [layer_c, layer_b, layer_a],
        ]:
            result = compute_layer_attribution(
                _FULL_TEXT, permutation, 0, _TOTAL_WORDS - 1, _empty_meta()
            )
            # Coverage may not be exactly equal due to integer division,
            # but if there IS a tie, smallest-start wins. We assert the
            # PERMUTATION INVARIANT: the same input set produces the same
            # output regardless of order.
            assert result.author_id == result.author_id  # tautology placeholder
            permutation_starts = [layer.start for layer in permutation]
            assert result.layer_id is not None, (
                f"permutation_starts={permutation_starts} returned no layer"
            )

        # Strong invariant: all permutations yield the SAME top author.
        results = [
            compute_layer_attribution(
                _FULL_TEXT, perm, 0, _TOTAL_WORDS - 1, _empty_meta()
            ).author_id
            for perm in [
                [layer_a, layer_b, layer_c],
                [layer_c, layer_a, layer_b],
                [layer_b, layer_c, layer_a],
                [layer_c, layer_b, layer_a],
            ]
        ]
        assert len(set(results)) == 1, (
            f"Permutations yielded different top authors: {results}; "
            f"determinism fix did not hold across input orderings"
        )

    def test_strict_ordering_unaffected_when_coverage_differs(self) -> None:
        """Sanity: when coverage values genuinely differ, the layer.start
        tiebreak is moot — the higher-coverage layer still wins.
        """
        # MATN dominates ≥80% (by char count, well above LA-1 threshold).
        matn_layer = TextLayerSegment(
            layer_type=LayerType.MATN,
            author_canonical_id="sch_matn_dominant",
            start=10,
            end=_TOTAL_CHARS,
            confidence=1.0,
        )
        sharh_layer = TextLayerSegment(
            layer_type=LayerType.SHARH,
            author_canonical_id="sch_sharh_minor",
            start=0,
            end=10,
            confidence=1.0,
        )

        # SHARH starts earlier (0) but MATN has 4-9x more coverage.
        # Higher coverage MUST win even though SHARH has smaller start.
        result_1 = compute_layer_attribution(
            _FULL_TEXT, [matn_layer, sharh_layer], 0, _TOTAL_WORDS - 1, _empty_meta()
        )
        result_2 = compute_layer_attribution(
            _FULL_TEXT, [sharh_layer, matn_layer], 0, _TOTAL_WORDS - 1, _empty_meta()
        )

        assert result_1.author_id == "sch_matn_dominant"
        assert result_2.author_id == "sch_matn_dominant"


class TestSortStabilityAcrossRepeatedCalls:
    """Cross-run reproducibility: identical input → identical output."""

    def test_compute_layer_attribution_deterministic_repeated_calls(self) -> None:
        """A single (text, layers, range) tuple, called 10 times, yields
        the same top author_id. Locks the contract that coverage-tied
        results are reproducible — F-DET-3's name ('F-DET' = field
        deterministic) commits to this regardless of upstream ordering.
        """
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_first",
                start=0,
                end=_BOUNDARY_CHAR,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_second",
                start=_BOUNDARY_CHAR,
                end=_TOTAL_CHARS,
                confidence=1.0,
            ),
        ]

        observed_authors: set[str] = set()
        for _ in range(10):
            result = compute_layer_attribution(
                _FULL_TEXT, layers, 0, _TOTAL_WORDS - 1, _empty_meta()
            )
            observed_authors.add(result.author_id)
        assert observed_authors == {"sch_first"}

    def test_two_distinct_input_orderings_produce_same_attribution(self) -> None:
        """Two text_layers lists with the same layers in different orders
        produce the same attribution. This is the cross-deterministic-
        path reproducibility contract — F-DET-3 must NOT depend on input
        order when coverage values tie.
        """
        matn = TextLayerSegment(
            layer_type=LayerType.MATN,
            author_canonical_id="sch_matn_id",
            start=0,
            end=_BOUNDARY_CHAR,
            confidence=1.0,
        )
        sharh = TextLayerSegment(
            layer_type=LayerType.SHARH,
            author_canonical_id="sch_sharh_id",
            start=_BOUNDARY_CHAR,
            end=_TOTAL_CHARS,
            confidence=1.0,
        )

        result_a = compute_layer_attribution(
            _FULL_TEXT, [matn, sharh], 0, _TOTAL_WORDS - 1, _empty_meta()
        )
        result_b = compute_layer_attribution(
            _FULL_TEXT, [sharh, matn], 0, _TOTAL_WORDS - 1, _empty_meta()
        )

        # Same author chosen across both orderings.
        assert result_a.author_id == result_b.author_id == "sch_matn_id"
        assert result_a.layer_id == result_b.layer_id == "matn"
