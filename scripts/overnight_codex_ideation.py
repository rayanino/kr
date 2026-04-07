"""Ideation helpers for overnight_codex creative output scoring."""

from __future__ import annotations

from typing import Any

BENCHMARK_DIMENSIONS = (
    "product_reframing",
    "live_system_contrast",
    "primary_boundary_accuracy",
    "latent_ingredient_leverage",
    "invariant_coverage",
    "owner_value",
    "autonomous_originality",
    "evaluability",
)

# Classification thresholds over the 8-dimension sum (max 32).
IDEA_CLASS_THRESHOLDS: list[tuple[int, str]] = [
    (28, "benchmark_grade"),
    (20, "major"),
    (0, "non_major"),
]


def normalize_benchmark_scores(
    payload: dict[str, Any],
) -> tuple[dict[str, int], list[str]]:
    """Extract and validate self-reported benchmark scores from a payload.

    Returns (scores_dict, errors_list).  On invalid input the scores dict is
    empty and errors describes what went wrong.
    """
    raw = payload.get("benchmark_scores")
    if not isinstance(raw, dict):
        return {}, ["benchmark_scores missing or not a dict"]
    errors: list[str] = []
    scores: dict[str, int] = {}
    for dim in BENCHMARK_DIMENSIONS:
        val = raw.get(dim)
        if val is None:
            errors.append(f"missing dimension: {dim}")
            continue
        try:
            int_val = int(val)
        except (TypeError, ValueError):
            errors.append(f"non-integer value for {dim}: {val!r}")
            continue
        if not 0 <= int_val <= 4:
            errors.append(f"{dim} out of range [0,4]: {int_val}")
            continue
        scores[dim] = int_val
    return scores, errors


def classify_idea(scores: dict[str, int]) -> tuple[str, int]:
    """Classify an idea based on the sum of its benchmark dimension scores.

    Returns (class_name, total_score).
    """
    total = sum(scores.values())
    for threshold, class_name in IDEA_CLASS_THRESHOLDS:
        if total >= threshold:
            return class_name, total
    return "non_major", total
