"""Tests for batch diagnostics (SPEC §3.5, §4.A.6).

Tests cover batch report computation, all four warning conditions,
confidence distribution, and editorial placement rate.
"""

from __future__ import annotations

import pytest

from engines.taxonomy.contracts_core import BatchReport, RunConfig
from engines.taxonomy.src.diagnostics import (
    _build_confidence_distribution,
    check_warnings,
    compute_batch_report,
    compute_editorial_placement_rate,
    compute_median_confidence,
)
from engines.taxonomy.tests.conftest import make_excerpt, make_run_config


def _make_result(
    stage: str = "placed",
    route: str = "live",
    leaf: str | None = "leaf/a",
    confidence: float | None = 0.85,
    primary_function: str = "rule_statement",
) -> dict:
    """Create a minimal merged result dict for diagnostics testing."""
    return {
        "excerpt_id": "exc_test",
        "lifecycle_stage": stage,
        "placement_route": route,
        "confirmed_leaf": leaf,
        "placement_confidence": confidence,
        "primary_function": primary_function,
    }


# ── Batch Report Computation ──────────────────────────────────────


class TestComputeBatchReport:
    def test_counts_correct(self) -> None:
        results = [
            _make_result(stage="placed"),
            _make_result(stage="placed"),
            _make_result(stage="staged", route="staged_low_confidence"),
            _make_result(stage="unplaced", route="unplaced", leaf=None),
            _make_result(stage="pending_no_tree", route="pending_no_tree", leaf=None),
        ]
        config = make_run_config()
        report = compute_batch_report(results, config, None, "2026-03-30T12:00:00Z")

        assert report.total_excerpts == 5
        assert report.placed_count == 2
        assert report.staged_count == 1
        assert report.unplaced_count == 1
        assert report.pending_no_tree_count == 1

    def test_empty_batch(self) -> None:
        config = make_run_config()
        report = compute_batch_report([], config, None, "2026-03-30T12:00:00Z")
        assert report.total_excerpts == 0
        assert report.placed_count == 0
        assert report.median_confidence is None

    def test_leaf_distribution(self) -> None:
        results = [
            _make_result(leaf="leaf/a"),
            _make_result(leaf="leaf/a"),
            _make_result(leaf="leaf/b"),
            _make_result(stage="staged", route="staged_low_confidence", leaf="leaf/a"),
        ]
        config = make_run_config()
        report = compute_batch_report(results, config, None, "2026-03-30T12:00:00Z")
        assert report.leaf_distribution["leaf/a"] == 3
        assert report.leaf_distribution["leaf/b"] == 1


# ── Confidence Distribution ───────────────────────────────────────


class TestConfidenceDistribution:
    def test_distribution_buckets(self) -> None:
        confidences = [0.45, 0.55, 0.78, 0.85, 0.92]
        dist = _build_confidence_distribution(confidences)
        assert dist["0.4-0.5"] == 1
        assert dist["0.5-0.6"] == 1
        assert dist["0.7-0.8"] == 1
        assert dist["0.8-0.9"] == 1
        assert dist["0.9-1.0"] == 1

    def test_perfect_score_in_last_bucket(self) -> None:
        dist = _build_confidence_distribution([1.0])
        assert dist["0.9-1.0"] == 1

    def test_empty_list(self) -> None:
        dist = _build_confidence_distribution([])
        assert all(v == 0 for v in dist.values())


# ── Median Confidence ─────────────────────────────────────────────


class TestMedianConfidence:
    def test_odd_count(self) -> None:
        assert compute_median_confidence([0.5, 0.6, 0.7, 0.8, 0.9]) == 0.7

    def test_even_count(self) -> None:
        result = compute_median_confidence([0.5, 0.6, 0.7, 0.8])
        assert result == pytest.approx(0.65)

    def test_empty_returns_none(self) -> None:
        assert compute_median_confidence([]) is None

    def test_single_value(self) -> None:
        assert compute_median_confidence([0.85]) == 0.85


# ── Editorial Placement Rate ──────────────────────────────────────


class TestEditorialPlacementRate:
    def test_some_editorial_live(self) -> None:
        results = [
            _make_result(primary_function="editorial_note", route="live"),
            _make_result(primary_function="editorial_note", route="staged_front_matter"),
            _make_result(primary_function="rule_statement", route="live"),
        ]
        rate = compute_editorial_placement_rate(results)
        assert rate == pytest.approx(0.5)  # 1 of 2 editorial live

    def test_no_editorial_returns_none(self) -> None:
        results = [_make_result(primary_function="rule_statement")]
        assert compute_editorial_placement_rate(results) is None

    def test_all_editorial_live(self) -> None:
        results = [
            _make_result(primary_function="editorial_note", route="live"),
            _make_result(primary_function="editorial_note", route="live"),
        ]
        assert compute_editorial_placement_rate(results) == 1.0


# ── Warning Conditions ────────────────────────────────────────────


class TestCheckWarnings:
    def test_science_mismatch_triggered(self) -> None:
        report = BatchReport(
            batch_id="t", science_id="nahw", tree_version="v1",
            timestamp_utc="", total_excerpts=10, placed_count=5,
            median_confidence=0.55,  # < 0.65 threshold
            warnings=[],
        )
        warnings = check_warnings(report)
        assert "TAX_POSSIBLE_SCIENCE_MISMATCH" in warnings

    def test_high_unplacement_triggered(self) -> None:
        report = BatchReport(
            batch_id="t", science_id="nahw", tree_version="v1",
            timestamp_utc="", total_excerpts=10, unplaced_count=5,
            warnings=[],
        )
        warnings = check_warnings(report)
        assert "TAX_HIGH_UNPLACEMENT_RATE" in warnings

    def test_leaf_concentration_triggered(self) -> None:
        report = BatchReport(
            batch_id="t", science_id="nahw", tree_version="v1",
            timestamp_utc="", total_excerpts=12,
            placed_count=8, staged_count=4,
            leaf_distribution={"leaf/a": 8, "leaf/b": 4},  # 8/12 = 67% > 25%
            warnings=[],
        )
        warnings = check_warnings(report)
        assert "TAX_LEAF_CONCENTRATION" in warnings

    def test_editorial_placement_triggered(self) -> None:
        report = BatchReport(
            batch_id="t", science_id="nahw", tree_version="v1",
            timestamp_utc="", total_excerpts=10,
            editorial_placement_rate=0.60,  # > 0.50 threshold
            warnings=[],
        )
        warnings = check_warnings(report)
        assert "TAX_HIGH_EDITORIAL_PLACEMENT" in warnings

    def test_healthy_batch_no_warnings(self) -> None:
        report = BatchReport(
            batch_id="t", science_id="nahw", tree_version="v1",
            timestamp_utc="", total_excerpts=20,
            placed_count=14, staged_count=3, unplaced_count=3,
            median_confidence=0.78,
            leaf_distribution={"a": 4, "b": 3, "c": 3, "d": 2, "e": 2, "f": 3},
            editorial_placement_rate=0.30,
            warnings=[],
        )
        warnings = check_warnings(report)
        assert warnings == []
