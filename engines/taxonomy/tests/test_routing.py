"""Tests for excerpt type classification and placement routing (SPEC §4.A.3).

Tests cover all routing matrix combinations, tie handling, and type classification.
"""

from __future__ import annotations

import pytest

from engines.taxonomy.contracts_core import (
    ExcerptType,
    LeafScore,
    LoadedTree,
    PlacementAdditions,
    PlacementRanking,
    PlacementRoute,
)
from engines.taxonomy.src.placer import (
    HIERARCHICAL_SEARCH_LEAF_LIMIT,
    LIVE_THRESHOLD_EDITORIAL,
    LIVE_THRESHOLD_TEACHING,
    STAGING_THRESHOLD,
    TIE_THRESHOLD,
    _should_skip_stage1,
    classify_excerpt_type,
    place_excerpt,
    route_excerpt,
)
from engines.taxonomy.tests.conftest import MockPlacementAdapter, make_excerpt, make_ranking


# ── Excerpt Type Classification ───────────────────────────────────


class TestClassifyExcerptType:
    def test_rule_statement_is_teaching(self) -> None:
        exc = make_excerpt(primary_function="rule_statement")
        assert classify_excerpt_type(exc) == ExcerptType.TEACHING

    def test_definition_is_teaching(self) -> None:
        exc = make_excerpt(primary_function="definition")
        assert classify_excerpt_type(exc) == ExcerptType.TEACHING

    def test_opinion_statement_is_teaching(self) -> None:
        exc = make_excerpt(primary_function="opinion_statement")
        assert classify_excerpt_type(exc) == ExcerptType.TEACHING

    def test_evidence_hadith_is_teaching(self) -> None:
        exc = make_excerpt(primary_function="evidence_hadith")
        assert classify_excerpt_type(exc) == ExcerptType.TEACHING

    def test_editorial_note_is_editorial(self) -> None:
        exc = make_excerpt(primary_function="editorial_note")
        assert classify_excerpt_type(exc) == ExcerptType.EDITORIAL

    def test_structural_transition_is_always_staged(self) -> None:
        exc = make_excerpt(primary_function="structural_transition")
        assert classify_excerpt_type(exc) == ExcerptType.ALWAYS_STAGED

    def test_cross_reference_is_always_staged(self) -> None:
        exc = make_excerpt(primary_function="cross_reference")
        assert classify_excerpt_type(exc) == ExcerptType.ALWAYS_STAGED

    def test_missing_primary_function_defaults_editorial(self) -> None:
        exc = make_excerpt()
        del exc["primary_function"]
        assert classify_excerpt_type(exc) == ExcerptType.EDITORIAL

    def test_null_primary_function_defaults_editorial(self) -> None:
        exc = make_excerpt(primary_function=None)
        assert classify_excerpt_type(exc) == ExcerptType.EDITORIAL

    def test_empty_string_defaults_editorial(self) -> None:
        exc = make_excerpt(primary_function="")
        assert classify_excerpt_type(exc) == ExcerptType.EDITORIAL


# ── Routing Matrix ────────────────────────────────────────────────


class TestRouteExcerpt:
    # Teaching content
    def test_teaching_high_score_live(self) -> None:
        ranking = make_ranking([("leaf/a", 0.90)])
        route, leaf, conf, tie = route_excerpt(ranking, ExcerptType.TEACHING)
        assert route == PlacementRoute.LIVE
        assert leaf == "leaf/a"
        assert conf == 0.90
        assert tie is False

    def test_teaching_at_threshold_live(self) -> None:
        ranking = make_ranking([("leaf/a", 0.80)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.TEACHING)
        assert route == PlacementRoute.LIVE

    def test_teaching_below_threshold_staged(self) -> None:
        ranking = make_ranking([("leaf/a", 0.75)])
        route, leaf, _, _ = route_excerpt(ranking, ExcerptType.TEACHING)
        assert route == PlacementRoute.STAGED_LOW_CONFIDENCE
        assert leaf == "leaf/a"

    def test_teaching_at_staging_threshold_staged(self) -> None:
        ranking = make_ranking([("leaf/a", 0.50)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.TEACHING)
        assert route == PlacementRoute.STAGED_LOW_CONFIDENCE

    def test_teaching_below_staging_unplaced(self) -> None:
        ranking = make_ranking([("leaf/a", 0.30)])
        route, leaf, conf, _ = route_excerpt(ranking, ExcerptType.TEACHING)
        assert route == PlacementRoute.UNPLACED
        assert leaf is None
        assert conf == 0.30

    # Editorial content
    def test_editorial_high_score_live(self) -> None:
        ranking = make_ranking([("leaf/a", 0.90)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.EDITORIAL)
        assert route == PlacementRoute.LIVE

    def test_editorial_at_threshold_live(self) -> None:
        ranking = make_ranking([("leaf/a", 0.85)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.EDITORIAL)
        assert route == PlacementRoute.LIVE

    def test_editorial_below_threshold_staged(self) -> None:
        ranking = make_ranking([("leaf/a", 0.83)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.EDITORIAL)
        assert route == PlacementRoute.STAGED_FRONT_MATTER

    def test_editorial_at_staging_staged(self) -> None:
        ranking = make_ranking([("leaf/a", 0.60)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.EDITORIAL)
        assert route == PlacementRoute.STAGED_FRONT_MATTER

    def test_editorial_below_staging_unplaced(self) -> None:
        ranking = make_ranking([("leaf/a", 0.30)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.EDITORIAL)
        assert route == PlacementRoute.UNPLACED

    # Always-staged content
    def test_always_staged_high_score_still_staged(self) -> None:
        ranking = make_ranking([("leaf/a", 0.95)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.ALWAYS_STAGED)
        assert route == PlacementRoute.STAGED_FRONT_MATTER

    def test_always_staged_at_threshold_staged(self) -> None:
        ranking = make_ranking([("leaf/a", 0.50)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.ALWAYS_STAGED)
        assert route == PlacementRoute.STAGED_FRONT_MATTER

    def test_always_staged_below_threshold_unplaced(self) -> None:
        ranking = make_ranking([("leaf/a", 0.30)])
        route, _, _, _ = route_excerpt(ranking, ExcerptType.ALWAYS_STAGED)
        assert route == PlacementRoute.UNPLACED


# ── Tie Handling ──────────────────────────────────────────────────


class TestTieHandling:
    def test_tie_forces_teaching_to_staged(self) -> None:
        """Two scores within 0.10 and both ≥0.50 → tie → forced staged."""
        ranking = make_ranking([("leaf/a", 0.85), ("leaf/b", 0.80)])
        route, leaf, _, tie = route_excerpt(ranking, ExcerptType.TEACHING)
        assert tie is True
        assert route == PlacementRoute.STAGED_LOW_CONFIDENCE
        assert leaf == "leaf/a"

    def test_tie_forces_editorial_to_staged(self) -> None:
        ranking = make_ranking([("leaf/a", 0.90), ("leaf/b", 0.85)])
        route, _, _, tie = route_excerpt(ranking, ExcerptType.EDITORIAL)
        assert tie is True
        assert route == PlacementRoute.STAGED_FRONT_MATTER

    def test_no_tie_when_gap_large(self) -> None:
        ranking = make_ranking([("leaf/a", 0.90), ("leaf/b", 0.70)])
        route, _, _, tie = route_excerpt(ranking, ExcerptType.TEACHING)
        assert tie is False
        assert route == PlacementRoute.LIVE

    def test_no_tie_when_second_below_staging(self) -> None:
        """Tie requires both scores ≥ STAGING_THRESHOLD."""
        ranking = make_ranking([("leaf/a", 0.55), ("leaf/b", 0.48)])
        _, _, _, tie = route_excerpt(ranking, ExcerptType.TEACHING)
        assert tie is False

    def test_tie_just_within_threshold(self) -> None:
        """Difference of 0.09 (< 0.10) is a tie."""
        ranking = make_ranking([("leaf/a", 0.85), ("leaf/b", 0.76)])
        _, _, _, tie = route_excerpt(ranking, ExcerptType.TEACHING)
        assert tie is True  # 0.85 - 0.76 = 0.09 < TIE_THRESHOLD

    def test_no_tie_just_outside_threshold(self) -> None:
        """Difference of 0.11 (> 0.10) is NOT a tie."""
        ranking = make_ranking([("leaf/a", 0.85), ("leaf/b", 0.74)])
        _, _, _, tie = route_excerpt(ranking, ExcerptType.TEACHING)
        assert tie is False  # 0.85 - 0.74 = 0.11 > TIE_THRESHOLD

    def test_single_candidate_no_tie(self) -> None:
        ranking = make_ranking([("leaf/a", 0.90)])
        _, _, _, tie = route_excerpt(ranking, ExcerptType.TEACHING)
        assert tie is False


# ── Stage 1 Skip Logic ────────────────────────────────────────────


class TestShouldSkipStage1:
    def test_small_tree_skips(self, aqidah_tree: LoadedTree) -> None:
        assert _should_skip_stage1(aqidah_tree) is True  # 30 ≤ 200

    def test_large_tree_uses_stage1(self, nahw_tree: LoadedTree) -> None:
        assert _should_skip_stage1(nahw_tree) is False  # 226 > 200

    def test_imlaa_skips(self, all_trees: dict[str, LoadedTree]) -> None:
        assert _should_skip_stage1(all_trees["imlaa"]) is True  # 105 ≤ 200


# ── place_excerpt with mock adapter ───────────────────────────────


class TestPlaceExcerptMock:
    def test_high_teaching_score_produces_live(
        self, aqidah_tree: LoadedTree
    ) -> None:
        leaf = aqidah_tree.all_leaves[0]
        ranking = make_ranking([(leaf.path, 0.92)])
        adapter = MockPlacementAdapter(stage2_result=ranking)
        exc = make_excerpt(primary_function="rule_statement")

        result = place_excerpt(exc, aqidah_tree, adapter)
        assert result.placement_route == PlacementRoute.LIVE
        assert result.confirmed_leaf == leaf.path
        assert result.lifecycle_stage.value == "placed"

    def test_low_score_produces_unplaced(
        self, aqidah_tree: LoadedTree
    ) -> None:
        leaf = aqidah_tree.all_leaves[0]
        ranking = make_ranking([(leaf.path, 0.20)])
        adapter = MockPlacementAdapter(stage2_result=ranking)
        exc = make_excerpt(primary_function="rule_statement")

        result = place_excerpt(exc, aqidah_tree, adapter)
        assert result.placement_route == PlacementRoute.UNPLACED
        assert result.confirmed_leaf is None
        assert result.best_candidates is not None

    def test_small_tree_skips_stage1(
        self, aqidah_tree: LoadedTree
    ) -> None:
        """Aqidah (30 leaves) should skip Stage 1 entirely."""
        leaf = aqidah_tree.all_leaves[0]
        ranking = make_ranking([(leaf.path, 0.85)])
        adapter = MockPlacementAdapter(stage2_result=ranking)
        exc = make_excerpt()

        place_excerpt(exc, aqidah_tree, adapter)
        assert len(adapter.stage1_calls) == 0
        assert len(adapter.stage2_calls) == 1
