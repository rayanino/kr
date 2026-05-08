"""Phase 5 Session 10 (2026-05-08) determinism audit fix tests.

Tests the secondary sort key on ``leaf_path`` in
``engines/taxonomy/src/placer.py:route_excerpt`` and
``place_excerpt``'s diagnostics fallback. Without the secondary key,
score ties between leaves resulted in input-order-dependent top picks
— a latent determinism trap of the same defect class as Session 7's
``_build_positions_for_disputed`` PYTHONHASHSEED bug at
``shared/scholar_authority/src/threshold_compounding.py``.

The fix locks the tiebreak to alphabetically smallest leaf_path so
identical scores always yield the same top pick regardless of LLM
output ordering.
"""

from __future__ import annotations

from engines.taxonomy.contracts_core import (
    ExcerptType,
    LeafScore,
    PlacementRanking,
    PlacementRoute,
)
from engines.taxonomy.src.placer import route_excerpt


def _ranking(*pairs: tuple[str, float]) -> PlacementRanking:
    """Construct a PlacementRanking from (leaf_path, score) tuples."""
    return PlacementRanking(
        rankings=[
            LeafScore(leaf_path=path, score=score, reasoning=f"Score {score}")
            for path, score in pairs
        ],
        primary_topic_used="حروف الجر",
    )


class TestRouteExcerptDeterminismOnTies:
    """The Session 10 fix: equal scores → smallest leaf_path wins."""

    def test_equal_scores_picks_alphabetically_smallest_path(self) -> None:
        """Two leaves at score=0.92 → 'a/x' wins over 'b/x' regardless of input order."""
        ranking_ab = _ranking(("a/x", 0.92), ("b/x", 0.92))
        ranking_ba = _ranking(("b/x", 0.92), ("a/x", 0.92))

        _route_ab, path_ab, _conf_ab, _tie_ab = route_excerpt(
            ranking_ab, ExcerptType.TEACHING
        )
        _route_ba, path_ba, _conf_ba, _tie_ba = route_excerpt(
            ranking_ba, ExcerptType.TEACHING
        )

        # Both invocations pick the same path; the alphabetically smallest
        # leaf_path wins regardless of input ordering.
        assert path_ab == "a/x"
        assert path_ba == "a/x"

    def test_three_way_score_tie_picks_smallest_path(self) -> None:
        """Three leaves at the same score — smallest leaf_path always wins."""
        for permutation in [
            (("alif/baa", 0.88), ("baa/jiim", 0.88), ("jiim/daal", 0.88)),
            (("jiim/daal", 0.88), ("alif/baa", 0.88), ("baa/jiim", 0.88)),
            (("baa/jiim", 0.88), ("jiim/daal", 0.88), ("alif/baa", 0.88)),
        ]:
            _route, path, _conf, _tie = route_excerpt(
                _ranking(*permutation), ExcerptType.TEACHING
            )
            assert path == "alif/baa", f"permutation={permutation}"

    def test_tie_detection_still_fires_on_score_ties(self) -> None:
        """Determinism fix preserves SPEC §4.A.3 tie_detected=True semantics:
        when top 2 within TIE_THRESHOLD AND both ≥ STAGING_THRESHOLD, the
        gate fires and routes to STAGED regardless of which leaf is picked.
        """
        ranking = _ranking(("a/x", 0.92), ("b/y", 0.92))
        route, _path, _conf, tie_detected = route_excerpt(
            ranking, ExcerptType.TEACHING
        )

        assert tie_detected is True
        # Tie override (line 169-173): teaching above LIVE_THRESHOLD becomes STAGED_LOW_CONFIDENCE
        assert route == PlacementRoute.STAGED_LOW_CONFIDENCE

    def test_strict_order_unaffected_when_scores_differ(self) -> None:
        """Sanity: when scores genuinely differ, leaf_path tiebreak is moot —
        the higher score still wins (the secondary key only matters on ties)."""
        ranking = _ranking(("z/last", 0.95), ("a/first", 0.80))
        _route, path, conf, _tie = route_excerpt(
            ranking, ExcerptType.TEACHING
        )

        # Higher score wins; alphabetic order does NOT override real score difference.
        assert path == "z/last"
        assert conf == 0.95


class TestSortStabilityAcrossSessions:
    """Cross-run reproducibility check: identical input → identical output."""

    def test_route_excerpt_deterministic_across_repeated_calls(self) -> None:
        """A single PlacementRanking instance, called 10 times, yields the
        same top path. This is not just stable Python sort — it locks the
        contract that score-tied results are reproducible.
        """
        ranking = _ranking(
            ("xyz/leaf", 0.85),
            ("abc/leaf", 0.85),
            ("def/leaf", 0.85),
        )
        observed_paths: set[str] = set()
        for _ in range(10):
            _route, path, _conf, _tie = route_excerpt(
                ranking, ExcerptType.TEACHING
            )
            observed_paths.add(path or "")
        assert observed_paths == {"abc/leaf"}

    def test_two_distinct_input_orderings_produce_same_output(self) -> None:
        """Two PlacementRanking instances built with the same scores in
        different orders produce the same routing output. This is the
        cross-LLM-call reproducibility contract — the LLM may emit leaves
        in different orders across runs at temperature=0; the routing
        decision must NOT depend on that order when scores tie.
        """
        order_1 = _ranking(("p/leaf", 0.91), ("q/leaf", 0.91), ("r/leaf", 0.91))
        order_2 = _ranking(("r/leaf", 0.91), ("p/leaf", 0.91), ("q/leaf", 0.91))
        order_3 = _ranking(("q/leaf", 0.91), ("r/leaf", 0.91), ("p/leaf", 0.91))

        results = [
            route_excerpt(r, ExcerptType.TEACHING)[1]
            for r in [order_1, order_2, order_3]
        ]
        # All three orderings produce the SAME top leaf_path.
        assert results == ["p/leaf", "p/leaf", "p/leaf"]
