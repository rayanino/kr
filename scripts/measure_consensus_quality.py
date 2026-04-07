"""D-041 Inter-Annotator Agreement measurement for multi-model consensus.

Reads consensus results from tests/results/ and computes Cohen's kappa
between model pairs. Outputs statistical quality of agreement — not just
binary agree/disagree.

Usage:
    python scripts/measure_consensus_quality.py [--phase PHASE] [--field FIELD]

Interpretation:
    kappa > 0.80 — strong agreement (consensus is reliable)
    kappa 0.60-0.80 — moderate agreement (investigate disagreement patterns)
    kappa < 0.60 — weak agreement (prompt or model selection problem)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def load_consensus_results(
    results_dir: Path, phase: str | None = None
) -> list[dict]:
    """Load all consensus result files from the results directory."""
    patterns = []
    if phase:
        patterns.append(f"**/phase_{phase}/**/consensus.json")
    else:
        patterns.append("**/consensus.json")

    results = []
    for pattern in patterns:
        for path in results_dir.rglob("consensus.json" if not phase else f"phase_{phase}/**/consensus.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                data["_source_path"] = str(path)
                results.append(data)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to read %s: %s", path, e)
    return results


def extract_model_labels(
    results: list[dict], field: str = "primary_function"
) -> tuple[list[str], list[str], list[str]]:
    """Extract paired labels from two models for a given field.

    Returns (book_ids, model_a_labels, model_b_labels).
    """
    book_ids: list[str] = []
    model_a_labels: list[str] = []
    model_b_labels: list[str] = []

    for result in results:
        models = result.get("model_outputs", result.get("models", {}))
        if not models or len(models) < 2:
            continue

        model_names = sorted(models.keys())
        a_val = models[model_names[0]].get(field)
        b_val = models[model_names[1]].get(field)

        if a_val is not None and b_val is not None:
            book_ids.append(result.get("book_id", result.get("_source_path", "unknown")))
            model_a_labels.append(str(a_val))
            model_b_labels.append(str(b_val))

    return book_ids, model_a_labels, model_b_labels


def compute_agreement_metrics(
    model_a_labels: list[str], model_b_labels: list[str]
) -> dict:
    """Compute Cohen's kappa and raw agreement rate."""
    try:
        from sklearn.metrics import cohen_kappa_score
    except ImportError:
        logger.error(
            "scikit-learn not installed. Run: pip install scikit-learn"
        )
        sys.exit(1)

    n = len(model_a_labels)
    if n == 0:
        return {"n": 0, "error": "No paired labels found"}

    raw_agreement = sum(
        1 for a, b in zip(model_a_labels, model_b_labels) if a == b
    ) / n

    kappa = cohen_kappa_score(model_a_labels, model_b_labels)

    # Identify disagreement patterns
    disagreements: dict[str, int] = {}
    for a, b in zip(model_a_labels, model_b_labels):
        if a != b:
            key = f"{a} vs {b}"
            disagreements[key] = disagreements.get(key, 0) + 1

    # Sort disagreements by frequency
    sorted_disagreements = dict(
        sorted(disagreements.items(), key=lambda x: x[1], reverse=True)
    )

    return {
        "n": n,
        "raw_agreement": round(raw_agreement, 4),
        "cohens_kappa": round(kappa, 4),
        "interpretation": (
            "strong" if kappa > 0.80
            else "moderate" if kappa > 0.60
            else "weak"
        ),
        "disagreement_patterns": sorted_disagreements,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure inter-annotator agreement for D-041 consensus"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("tests/results/source_engine"),
        help="Directory containing consensus results",
    )
    parser.add_argument("--phase", help="Filter to specific phase (e.g., 'c')")
    parser.add_argument(
        "--field",
        default="primary_function",
        help="Field to measure agreement on (default: primary_function)",
    )
    parser.add_argument(
        "--fields",
        nargs="*",
        help="Measure multiple fields (overrides --field)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    results = load_consensus_results(args.results_dir, args.phase)
    if not results:
        logger.info("No consensus results found in %s", args.results_dir)
        sys.exit(0)

    logger.info("Found %d consensus result files", len(results))

    fields = args.fields or [args.field]
    for field in fields:
        book_ids, a_labels, b_labels = extract_model_labels(results, field)
        metrics = compute_agreement_metrics(a_labels, b_labels)

        logger.info("\n=== %s ===", field)
        logger.info("  Pairs: %d", metrics.get("n", 0))
        logger.info("  Raw agreement: %.1f%%", metrics.get("raw_agreement", 0) * 100)
        logger.info("  Cohen's kappa: %.4f (%s)", metrics.get("cohens_kappa", 0), metrics.get("interpretation", "?"))

        if metrics.get("disagreement_patterns"):
            logger.info("  Top disagreements:")
            for pattern, count in list(metrics["disagreement_patterns"].items())[:5]:
                logger.info("    %s: %d", pattern, count)

    # Output full results as JSON for programmatic use
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
