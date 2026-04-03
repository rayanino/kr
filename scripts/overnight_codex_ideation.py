"""Benchmark helpers for strategic idea generation in overnight_codex."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


IDEATION_DIMENSIONS = [
    "product_reframing",
    "live_system_contrast",
    "primary_boundary_accuracy",
    "latent_ingredient_leverage",
    "invariant_coverage",
    "owner_value",
    "autonomous_originality",
    "evaluability",
]

ALLOWED_PROVIDER_PREFERENCES = {"codex", "claude", "gemini"}
ALLOWED_REPORT_CLASSES = {"standard", "strategic_idea"}
ALLOWED_IDEA_CLASSES = {"non_major", "major", "benchmark_grade"}
ALLOWED_AGREEMENT_STATUSES = {
    "candidate_pending_coworker",
    "candidate_degraded",
    "disputed",
    "confirmed_major",
    "confirmed_benchmark_grade",
}
ALLOWED_COWORKER_VERDICTS = {
    "benchmark_grade",
    "major",
    "non_major",
    "unavailable",
}


def load_ideation_benchmarks(path: Path) -> list[dict[str, Any]]:
    """Load the tracked benchmark registry."""
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    benchmarks = payload.get("benchmarks", [])
    if not isinstance(benchmarks, list):
        return []
    valid: list[dict[str, Any]] = []
    for raw in benchmarks:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title", "")).strip()
        benchmark_id = str(raw.get("benchmark_id", "")).strip()
        summary = str(raw.get("summary", "")).strip()
        reference_doc = str(raw.get("reference_doc", "")).strip()
        if not all((title, benchmark_id, summary, reference_doc)):
            continue
        valid.append(raw)
    return valid


def pick_benchmark_for_surface(
    benchmarks: list[dict[str, Any]],
    focus_engine: str,
) -> dict[str, Any] | None:
    """Pick the strongest matching benchmark for a focus engine."""
    for benchmark in benchmarks:
        pilot_surfaces = benchmark.get("pilot_surfaces", [])
        if isinstance(pilot_surfaces, list) and focus_engine in pilot_surfaces:
            return benchmark
    return benchmarks[0] if benchmarks else None


def normalize_benchmark_scores(payload: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    """Validate and normalize benchmark scores."""
    raw_scores = payload.get("benchmark_scores", {})
    if not isinstance(raw_scores, dict):
        return {}, ["benchmark_scores must be an object."]

    normalized: dict[str, int] = {}
    errors: list[str] = []
    for dimension in IDEATION_DIMENSIONS:
        value = raw_scores.get(dimension)
        if not isinstance(value, int):
            errors.append(f"benchmark_scores.{dimension} must be an integer 0-4.")
            continue
        if value < 0 or value > 4:
            errors.append(f"benchmark_scores.{dimension} must be between 0 and 4.")
            continue
        normalized[dimension] = value
    return normalized, errors


def classify_idea(scores: dict[str, int]) -> tuple[str, int]:
    """Classify an idea by the benchmark rubric."""
    total = sum(scores.values())
    must_be_strong = (
        "product_reframing",
        "live_system_contrast",
        "primary_boundary_accuracy",
        "owner_value",
    )
    if any(scores.get(key, 0) < 2 for key in IDEATION_DIMENSIONS):
        return "non_major", total
    if any(scores.get(key, 0) < 3 for key in must_be_strong):
        return "non_major", total
    if (
        total >= 28
        and scores.get("product_reframing", 0) == 4
        and scores.get("primary_boundary_accuracy", 0) == 4
        and scores.get("owner_value", 0) == 4
    ):
        return "benchmark_grade", total
    if total >= 22:
        return "major", total
    return "non_major", total


def derive_agreement_status(
    coworker_verdicts: list[dict[str, Any]],
    idea_class: str,
) -> str:
    """Derive the agreement state from available coworker verdicts."""
    if not coworker_verdicts:
        return "candidate_pending_coworker"

    verdicts: list[str] = []
    unavailable = False
    for raw in coworker_verdicts:
        if not isinstance(raw, dict):
            continue
        verdict = str(raw.get("verdict", "")).strip()
        if verdict not in ALLOWED_COWORKER_VERDICTS:
            continue
        if verdict == "unavailable":
            unavailable = True
            continue
        verdicts.append(verdict)

    if not verdicts:
        return "candidate_degraded" if unavailable else "candidate_pending_coworker"

    if "non_major" in verdicts and any(v in {"major", "benchmark_grade"} for v in verdicts):
        return "disputed"

    if len(verdicts) >= 2 and all(v in {"major", "benchmark_grade"} for v in verdicts):
        if idea_class == "benchmark_grade" and all(v == "benchmark_grade" for v in verdicts):
            return "confirmed_benchmark_grade"
        return "confirmed_major"

    if unavailable:
        return "candidate_degraded"
    return "candidate_pending_coworker"


def validate_coworker_verdicts(
    payload: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Validate coworker verdict structure."""
    verdicts = payload.get("coworker_verdicts", [])
    if verdicts in ("", None):
        return [], []
    if not isinstance(verdicts, list):
        return [], ["coworker_verdicts must be an array."]

    normalized: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, raw in enumerate(verdicts):
        if not isinstance(raw, dict):
            errors.append(f"coworker_verdicts[{index}] must be an object.")
            continue
        coworker = str(raw.get("coworker", "")).strip()
        verdict = str(raw.get("verdict", "")).strip()
        rationale = str(raw.get("rationale", "")).strip()
        if not coworker:
            errors.append(f"coworker_verdicts[{index}].coworker must be non-empty.")
        if verdict not in ALLOWED_COWORKER_VERDICTS:
            errors.append(
                f"coworker_verdicts[{index}].verdict must be one of "
                f"{sorted(ALLOWED_COWORKER_VERDICTS)}."
            )
        if verdict != "unavailable" and not rationale:
            errors.append(f"coworker_verdicts[{index}].rationale must be non-empty.")
        normalized.append(
            {
                "coworker": coworker,
                "verdict": verdict,
                "rationale": rationale,
            }
        )
    return normalized, errors


def validate_strategic_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and enrich a strategic-idea payload."""
    errors: list[str] = []
    required_text = [
        "current_system_limit",
        "proposed_reframe",
        "primary_insertion_boundary",
        "owner_value_statement",
    ]
    for field_name in required_text:
        if not str(payload.get(field_name, "")).strip():
            errors.append(f"{field_name} must be non-empty.")

    for list_field, min_items in (
        ("secondary_required_changes", 1),
        ("benefits", 3),
        ("risks", 3),
    ):
        value = payload.get(list_field, [])
        if not isinstance(value, list) or len(value) < min_items or any(
            not str(item).strip() for item in value
        ):
            errors.append(f"{list_field} must contain at least {min_items} non-empty items.")

    scores, score_errors = normalize_benchmark_scores(payload)
    errors.extend(score_errors)
    verdicts, verdict_errors = validate_coworker_verdicts(payload)
    errors.extend(verdict_errors)

    if errors:
        raise ValueError("Invalid strategic idea payload: " + "; ".join(errors))

    idea_class, benchmark_total = classify_idea(scores)
    agreement_status = derive_agreement_status(verdicts, idea_class)
    if agreement_status not in ALLOWED_AGREEMENT_STATUSES:
        raise ValueError(f"Derived invalid agreement_status: {agreement_status}")

    payload["benchmark_scores"] = scores
    payload["benchmark_total"] = benchmark_total
    payload["idea_class"] = idea_class
    payload["agreement_status"] = agreement_status
    payload["coworker_verdicts"] = verdicts
    return payload
