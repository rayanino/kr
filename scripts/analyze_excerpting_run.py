#!/usr/bin/env python3
"""Per-book excerpting run analyzer.

Reads a single book run directory and produces:
  analysis/book_summary.json
  analysis/book_summary.md
  analysis/anomalies.json
  analysis/review_candidates.jsonl

Usage:
  python scripts/analyze_excerpting_run.py <run_dir>
  python scripts/analyze_excerpting_run.py <run_dir> --output-dir <dir>
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure scripts/ is importable
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from excerpting_eval.analysis import analyze_book
from excerpting_eval.ingest import load_book_run
from excerpting_eval.models import BookAnalysisResult

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def write_outputs(result: BookAnalysisResult, output_dir: Path) -> None:
    """Write all per-book analysis outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- book_summary.json ---
    summary = {
        "book_name": result.book_name,
        "source_id": result.source_id,
        "structural_status": result.structural_status.value,
        "phase1_chunk_count": result.phase1_chunk_count,
        "phase2b_unit_count": result.phase2b_unit_count,
        "excerpt_count": result.excerpt_count,
        "error_count": result.error_count,
        "anomaly_count": len(result.anomalies),
        "review_candidate_count": len(result.review_candidates),
        "total_time_seconds": round(result.total_time_seconds, 2),
        "total_cost": round(result.total_cost, 6),
        "metrics": {m.name: m.to_dict() for m in result.metrics},
        "trace_summary": [t.to_dict() for t in result.traces],
        "observability_limitations": result.observability_limitations,
    }
    _write_json(output_dir / "book_summary.json", summary)

    # --- book_summary.md ---
    md = _format_book_md(result)
    (output_dir / "book_summary.md").write_text(md, encoding="utf-8")

    # --- anomalies.json ---
    anomalies = [a.to_dict() for a in result.anomalies]
    _write_json(output_dir / "anomalies.json", anomalies)

    # --- review_candidates.jsonl ---
    with (output_dir / "review_candidates.jsonl").open(
        "w", encoding="utf-8"
    ) as f:
        for cand in result.review_candidates:
            f.write(json.dumps(cand.to_dict(), ensure_ascii=False) + "\n")

    logger.info(
        "Wrote analysis for %s → %s "
        "(status=%s, anomalies=%d, candidates=%d)",
        result.book_name, output_dir,
        result.structural_status.value,
        len(result.anomalies),
        len(result.review_candidates),
    )


def _format_book_md(result: BookAnalysisResult) -> str:
    """Format a human-readable book summary."""
    lines = [
        f"# Book Analysis: {result.book_name}",
        "",
        f"**Structural Status:** {result.structural_status.value}",
        f"**Source ID:** {result.source_id}",
        "",
        "## Pipeline Accounting",
        "",
        f"| Stage | Count |",
        f"|-------|-------|",
        f"| Phase 1 chunks | {result.phase1_chunk_count} |",
        f"| Phase 2b units | {result.phase2b_unit_count} |",
        f"| Final excerpts | {result.excerpt_count} |",
        f"| Errors | {result.error_count} |",
        "",
        "## Operational",
        "",
        f"- Total time: {result.total_time_seconds:.1f}s",
        f"- Total cost: EUR {result.total_cost:.4f}",
        f"- LLM calls: {len(result.traces)}",
        "",
    ]

    if result.anomalies:
        lines.append("## Anomalies")
        lines.append("")
        for a in result.anomalies:
            lines.append(
                f"- **{a.anomaly_id}** [{a.severity}] "
                f"({a.evidence_basis.value}): {a.summary}"
            )
        lines.append("")

    # Metrics by tier
    for tier_label, tier_value in [
        ("Decision-Grade Structural", "decision_grade_structural"),
        ("Operational", "operational"),
        ("Review-Risk", "review_risk_triage"),
        ("Descriptive", "descriptive"),
    ]:
        tier_metrics = [
            m for m in result.metrics if m.tier.value == tier_value
        ]
        if tier_metrics:
            lines.append(f"## Metrics: {tier_label}")
            lines.append("")
            for m in tier_metrics:
                val = m.value
                if isinstance(val, dict):
                    val = json.dumps(val, ensure_ascii=False)
                lines.append(f"- **{m.name}:** {val}")
            lines.append("")

    # Trace summary
    if result.traces:
        lines.append("## LLM Trace Summary")
        lines.append("")
        lines.append("| Call | Phase (inferred) | Model | Finish | Label Match |")
        lines.append("|------|------------------|-------|--------|-------------|")
        for t in result.traces:
            lines.append(
                f"| {t.file_stem} | {t.inferred_phase.value} | "
                f"{t.model or '?'} | {t.finish_reason or '?'} | "
                f"{'yes' if t.label_matches_content else 'NO'} |"
            )
        lines.append("")

    if result.observability_limitations:
        lines.append("## Observability Limitations")
        lines.append("")
        for lim in result.observability_limitations:
            lines.append(f"- {lim}")
        lines.append("")

    return "\n".join(lines)


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a single excerpting run directory.",
    )
    parser.add_argument(
        "run_dir",
        type=Path,
        help="Path to a book run directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: <run_dir>/analysis/)",
    )
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        logger.error("Run directory does not exist: %s", run_dir)
        sys.exit(1)

    output_dir = args.output_dir or (run_dir / "analysis")

    run_data = load_book_run(run_dir)
    result = analyze_book(run_data)
    write_outputs(result, output_dir)


if __name__ == "__main__":
    main()
