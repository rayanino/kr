#!/usr/bin/env python3
"""Campaign-level excerpting run aggregator.

Reads a campaign directory containing multiple book run subdirectories
and produces:
  analysis/campaign_summary.json
  analysis/campaign_summary.md
  analysis/campaign_book_table.json

Also runs per-book analysis if not already present.

Usage:
  python scripts/analyze_excerpting_campaign.py <campaign_dir>
  python scripts/analyze_excerpting_campaign.py <campaign_dir> --output-dir <dir>
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from excerpting_eval.analysis import analyze_book
from excerpting_eval.ingest import load_book_run
from excerpting_eval.models import BookAnalysisResult, StructuralStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def discover_books(campaign_dir: Path) -> list[Path]:
    """Find book run subdirectories in a campaign directory."""
    books = []
    for child in sorted(campaign_dir.iterdir()):
        if not child.is_dir():
            continue
        # A book directory has phase1_chunks.json or run_metadata.json
        if (child / "phase1_chunks.json").exists() or (
            child / "run_metadata.json"
        ).exists():
            books.append(child)
    return books


def determine_recommendation(
    results: list[BookAnalysisResult],
) -> str:
    """Determine campaign-level recommendation.

    Returns: 'proceed' | 'fix_before_scale' | 'block'
    """
    fail_count = sum(
        1 for r in results
        if r.structural_status == StructuralStatus.STRUCTURAL_FAIL
    )
    concern_count = sum(
        1 for r in results
        if r.structural_status == StructuralStatus.STRUCTURAL_CONCERN
    )

    if fail_count >= 2:
        return "block"
    if fail_count >= 1:
        return "fix_before_scale"
    if concern_count >= 2:
        return "fix_before_scale"
    return "proceed"


def write_campaign_outputs(
    results: list[BookAnalysisResult],
    output_dir: Path,
) -> None:
    """Write campaign-level analysis outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    recommendation = determine_recommendation(results)

    # Totals
    total_excerpts = sum(r.excerpt_count for r in results)
    total_units = sum(r.phase2b_unit_count for r in results)
    total_chunks = sum(r.phase1_chunk_count for r in results)
    total_anomalies = sum(len(r.anomalies) for r in results)
    total_cost = sum(r.total_cost for r in results)
    total_time = sum(r.total_time_seconds for r in results)

    # --- campaign_summary.json ---
    summary = {
        "recommendation": recommendation,
        "book_count": len(results),
        "structural_fail_count": sum(
            1 for r in results
            if r.structural_status == StructuralStatus.STRUCTURAL_FAIL
        ),
        "structural_concern_count": sum(
            1 for r in results
            if r.structural_status == StructuralStatus.STRUCTURAL_CONCERN
        ),
        "structurally_clean_count": sum(
            1 for r in results
            if r.structural_status == StructuralStatus.STRUCTURALLY_CLEAN
        ),
        "total_chunks": total_chunks,
        "total_units": total_units,
        "total_excerpts": total_excerpts,
        "total_anomalies": total_anomalies,
        "total_cost": round(total_cost, 6),
        "total_time_seconds": round(total_time, 2),
        "per_book": [
            {
                "book_name": r.book_name,
                "source_id": r.source_id,
                "structural_status": r.structural_status.value,
                "phase1_chunks": r.phase1_chunk_count,
                "phase2b_units": r.phase2b_unit_count,
                "excerpts": r.excerpt_count,
                "errors": r.error_count,
                "anomalies": len(r.anomalies),
                "time_seconds": round(r.total_time_seconds, 2),
                "cost": round(r.total_cost, 6),
            }
            for r in results
        ],
    }
    _write_json(output_dir / "campaign_summary.json", summary)

    # --- campaign_summary.md ---
    md = _format_campaign_md(results, recommendation, summary)
    (output_dir / "campaign_summary.md").write_text(md, encoding="utf-8")

    # --- campaign_book_table.json ---
    table = [
        {
            "book_name": r.book_name,
            "source_id": r.source_id,
            "structural_status": r.structural_status.value,
            "phase1_chunks": r.phase1_chunk_count,
            "phase2b_units": r.phase2b_unit_count,
            "excerpts": r.excerpt_count,
            "errors": r.error_count,
            "anomaly_count": len(r.anomalies),
            "anomaly_categories": sorted(set(
                a.category for a in r.anomalies
            )),
            "time_seconds": round(r.total_time_seconds, 2),
            "cost": round(r.total_cost, 6),
        }
        for r in results
    ]
    _write_json(output_dir / "campaign_book_table.json", table)

    logger.info(
        "Campaign analysis complete: %d books, recommendation=%s, "
        "%d total excerpts, %d anomalies",
        len(results), recommendation, total_excerpts, total_anomalies,
    )


def _format_campaign_md(
    results: list[BookAnalysisResult],
    recommendation: str,
    summary: dict,
) -> str:
    """Format campaign summary as markdown."""
    lines = [
        "# Excerpting Campaign Analysis",
        "",
        f"**Recommendation:** {recommendation}",
        f"**Books:** {len(results)}",
        "",
        "## Book Status Table",
        "",
        "| Book | Status | Chunks | Units | Excerpts | Errors | Anomalies | Time | Cost |",
        "|------|--------|--------|-------|----------|--------|-----------|------|------|",
    ]

    for r in results:
        lines.append(
            f"| {r.book_name} | {r.structural_status.value} | "
            f"{r.phase1_chunk_count} | {r.phase2b_unit_count} | "
            f"{r.excerpt_count} | {r.error_count} | "
            f"{len(r.anomalies)} | {r.total_time_seconds:.0f}s | "
            f"EUR {r.total_cost:.4f} |"
        )

    lines.extend([
        "",
        "## Campaign Totals",
        "",
        f"- Total chunks: {summary['total_chunks']}",
        f"- Total units: {summary['total_units']}",
        f"- Total excerpts: {summary['total_excerpts']}",
        f"- Total anomalies: {summary['total_anomalies']}",
        f"- Total cost: EUR {summary['total_cost']:.4f}",
        f"- Total time: {summary['total_time_seconds']:.0f}s",
        "",
        "## Key Questions Answered",
        "",
    ])

    # Which books are structurally healthy?
    clean = [
        r.book_name for r in results
        if r.structural_status == StructuralStatus.STRUCTURALLY_CLEAN
    ]
    failed = [
        r.book_name for r in results
        if r.structural_status == StructuralStatus.STRUCTURAL_FAIL
    ]

    lines.append(
        f"**Structurally healthy:** "
        f"{', '.join(clean) if clean else 'none'}"
    )
    lines.append(
        f"**Structural failures:** "
        f"{', '.join(failed) if failed else 'none'}"
    )

    # Are issues isolated or systematic?
    all_categories = []
    for r in results:
        for a in r.anomalies:
            all_categories.append(a.category)
    from collections import Counter
    cat_counts = Counter(all_categories)
    recurring = {k: v for k, v in cat_counts.items() if v > 1}

    if recurring:
        lines.append(
            f"**Recurring anomaly patterns:** "
            f"{json.dumps(recurring, ensure_ascii=False)}"
        )
    else:
        lines.append("**Recurring anomaly patterns:** none detected")

    lines.append("")

    # Anomaly details per book
    for r in results:
        if r.anomalies:
            lines.append(f"### {r.book_name} anomalies")
            lines.append("")
            for a in r.anomalies:
                lines.append(
                    f"- **{a.anomaly_id}** [{a.severity}] "
                    f"({a.evidence_basis.value}): {a.summary}"
                )
            lines.append("")

    return "\n".join(lines)


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a campaign of excerpting runs.",
    )
    parser.add_argument(
        "campaign_dir",
        type=Path,
        help="Path to the campaign directory (contains book subdirs)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: <campaign_dir>/analysis/)",
    )
    args = parser.parse_args()

    campaign_dir = args.campaign_dir.resolve()
    if not campaign_dir.is_dir():
        logger.error("Campaign directory does not exist: %s", campaign_dir)
        sys.exit(1)

    output_dir = args.output_dir or (campaign_dir / "analysis")

    book_dirs = discover_books(campaign_dir)
    if not book_dirs:
        logger.error("No book run directories found in %s", campaign_dir)
        sys.exit(1)

    logger.info("Found %d book(s): %s", len(book_dirs),
                ", ".join(d.name for d in book_dirs))

    results: list[BookAnalysisResult] = []
    for book_dir in book_dirs:
        logger.info("Analyzing %s ...", book_dir.name)
        run_data = load_book_run(book_dir)
        result = analyze_book(run_data)

        # Also write per-book outputs
        book_output = book_dir / "analysis"
        from analyze_excerpting_run import write_outputs
        write_outputs(result, book_output)

        results.append(result)

    write_campaign_outputs(results, output_dir)


if __name__ == "__main__":
    main()
