"""Batch diagnostics for the taxonomy engine.

Computes batch-level statistics and warning conditions after a placement
run completes. See SPEC §3.5 (batch report) and §4.A.6 (warnings).
"""

from __future__ import annotations

import logging
from statistics import median

from engines.taxonomy.contracts_core import (
    BatchReport,
    LoadedTree,
    RunConfig,
    TaxonomyWarning,
)

logger = logging.getLogger(__name__)

# SPEC §4.A.6 — Warning thresholds
_SCIENCE_MISMATCH_THRESHOLD = 0.65
_UNPLACEMENT_RATE_THRESHOLD = 0.40
_LEAF_CONCENTRATION_THRESHOLD = 0.25
_EDITORIAL_PLACEMENT_THRESHOLD = 0.50


def compute_batch_report(
    results: list[dict],
    config: RunConfig,
    tree: LoadedTree | None,
    timestamp_utc: str,
) -> BatchReport:
    """Compute a full batch report from placement results.

    Args:
        results: List of merged excerpt dicts (excerpt + placement additions).
        config: The run configuration.
        tree: The loaded tree (None for pending-no-tree batches).
        timestamp_utc: ISO timestamp for the report.
    """
    total = len(results)
    placed = 0
    staged = 0
    unplaced = 0
    pending = 0
    confidences: list[float] = []
    leaf_counts: dict[str, int] = {}

    for r in results:
        stage = r.get("lifecycle_stage")
        if stage == "placed":
            placed += 1
        elif stage == "staged":
            staged += 1
        elif stage == "unplaced":
            unplaced += 1
        elif stage == "pending_no_tree":
            pending += 1

        conf = r.get("placement_confidence")
        if conf is not None:
            confidences.append(conf)

        leaf = r.get("confirmed_leaf")
        if leaf is not None and stage in ("placed", "staged"):
            leaf_counts[leaf] = leaf_counts.get(leaf, 0) + 1

    conf_dist = _build_confidence_distribution(confidences)
    median_conf = compute_median_confidence(confidences)
    editorial_rate = compute_editorial_placement_rate(results)

    report = BatchReport(
        batch_id=config.batch_id,
        science_id=config.science_id,
        tree_version=tree.tree_version if tree else "no_tree",
        timestamp_utc=timestamp_utc,
        total_excerpts=total,
        placed_count=placed,
        staged_count=staged,
        unplaced_count=unplaced,
        pending_no_tree_count=pending,
        confidence_distribution=conf_dist,
        median_confidence=median_conf,
        leaf_distribution=leaf_counts,
        editorial_placement_rate=editorial_rate,
        warnings=[],
    )

    report.warnings = check_warnings(report)
    return report


def check_warnings(report: BatchReport) -> list[str]:
    """Check batch-level warning conditions (SPEC §4.A.6)."""
    warnings: list[str] = []

    # TAX_POSSIBLE_SCIENCE_MISMATCH: median confidence < 0.65
    if (
        report.median_confidence is not None
        and report.median_confidence < _SCIENCE_MISMATCH_THRESHOLD
    ):
        warnings.append(TaxonomyWarning.POSSIBLE_SCIENCE_MISMATCH.value)

    # TAX_HIGH_UNPLACEMENT_RATE: > 40% unplaced
    if report.total_excerpts > 0:
        unplacement_rate = report.unplaced_count / report.total_excerpts
        if unplacement_rate > _UNPLACEMENT_RATE_THRESHOLD:
            warnings.append(TaxonomyWarning.HIGH_UNPLACEMENT_RATE.value)

    # TAX_LEAF_CONCENTRATION: any leaf > 25% of placements
    total_placed_staged = report.placed_count + report.staged_count
    if total_placed_staged > 0:
        for _leaf_path, count in report.leaf_distribution.items():
            if count / total_placed_staged > _LEAF_CONCENTRATION_THRESHOLD:
                warnings.append(TaxonomyWarning.LEAF_CONCENTRATION.value)
                break  # One warning is enough

    # TAX_HIGH_EDITORIAL_PLACEMENT: > 50% editorial excerpts live
    if (
        report.editorial_placement_rate is not None
        and report.editorial_placement_rate > _EDITORIAL_PLACEMENT_THRESHOLD
    ):
        warnings.append(TaxonomyWarning.HIGH_EDITORIAL_PLACEMENT.value)

    return warnings


def compute_median_confidence(confidences: list[float]) -> float | None:
    """Compute median placement confidence. Returns None if empty."""
    if not confidences:
        return None
    return median(confidences)


def compute_editorial_placement_rate(results: list[dict]) -> float | None:
    """Compute fraction of editorial excerpts that reached live tree.

    Returns None if there are no editorial excerpts in the batch.
    """
    editorial_total = 0
    editorial_live = 0

    for r in results:
        if r.get("primary_function") == "editorial_note":
            editorial_total += 1
            if r.get("placement_route") == "live":
                editorial_live += 1

    if editorial_total == 0:
        return None
    return editorial_live / editorial_total


def _build_confidence_distribution(
    confidences: list[float],
) -> dict[str, int]:
    """Build histogram of confidence scores in 0.1-width buckets."""
    buckets = {
        "0.0-0.1": 0,
        "0.1-0.2": 0,
        "0.2-0.3": 0,
        "0.3-0.4": 0,
        "0.4-0.5": 0,
        "0.5-0.6": 0,
        "0.6-0.7": 0,
        "0.7-0.8": 0,
        "0.8-0.9": 0,
        "0.9-1.0": 0,
    }

    for c in confidences:
        if c >= 1.0:
            buckets["0.9-1.0"] += 1
        elif c < 0.0:
            buckets["0.0-0.1"] += 1
        else:
            bucket_idx = int(c * 10)
            bucket_idx = min(bucket_idx, 9)
            keys = list(buckets.keys())
            buckets[keys[bucket_idx]] += 1

    return buckets
