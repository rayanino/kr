#!/usr/bin/env python3
"""S-04: Generate verification_report.md from coverage data and MCU traces.

Produces a human-readable verification report with coverage table, gap
inventory sorted by severity, and recommendations. Also generates
delta_queue_patch.md listing MCUs that need new MAQ entries.

Usage:
    python scripts/batch_generate_trace_report.py --batch-dir path/to/bundle
    python scripts/batch_generate_trace_report.py --batch-dir path/to/bundle --output-dir reports/
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file."""
    entries: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                entries.append(json.loads(stripped))
    return entries


def format_coverage_table(coverage: dict) -> str:
    """Format coverage metrics as a markdown table."""
    rows = [
        ("Total files", str(coverage.get("total_files", 0))),
        ("Verified files", str(coverage.get("verified_files", 0))),
        ("Total MCUs", str(coverage.get("total_mcus", 0))),
        ("Mapped MCUs", str(coverage.get("mapped_mcus", 0))),
        ("Missed", str(coverage.get("missed_count", 0))),
        ("Softened", str(coverage.get("softened_count", 0))),
        ("Distorted (tashif)", str(coverage.get("distorted_tashif_count", 0))),
        ("Distorted (tahrif)", str(coverage.get("distorted_tahrif_count", 0))),
        ("Coverage %", f"{coverage.get('coverage_pct', 0.0):.1f}%"),
    ]
    lines = ["| Metric | Value |", "|---|---|"]
    for label, value in rows:
        lines.append(f"| {label} | {value} |")
    return "\n".join(lines)


def collect_gaps(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect gap entries (non-mapped MCUs) sorted by severity."""
    gaps: list[dict[str, Any]] = []
    for t in traces:
        if t.get("mapping") not in ("MAQ", "META", "REJECT"):
            gaps.append(t)
    gaps.sort(key=lambda g: SEVERITY_ORDER.get(g.get("severity", "LOW"), 99))
    return gaps


def format_gap_inventory(gaps: list[dict[str, Any]]) -> str:
    """Format gaps as a markdown list grouped by severity."""
    if not gaps:
        return "_No gaps found._"
    lines: list[str] = []
    current_severity: str | None = None
    for g in gaps:
        severity = g.get("severity", "UNKNOWN")
        if severity != current_severity:
            current_severity = severity
            lines.append(f"\n### {severity}")
        mcu_id = g.get("mcu_id", "unknown")
        status = g.get("status", "UNMAPPED")
        source = g.get("source_file", "")
        lines.append(f"- **{mcu_id}** [{status}] from `{source}`")
    return "\n".join(lines)


def collect_delta_queue(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect MCUs that need new MAQ entries."""
    return [
        t for t in traces
        if t.get("status") == "MISSED" or (
            t.get("mapping") not in ("MAQ", "META", "REJECT")
            and t.get("status") != "SKIPPED-FILE"
        )
    ]


def generate_report(coverage: dict, traces: list[dict[str, Any]]) -> str:
    """Generate the full verification_report.md content."""
    gaps = collect_gaps(traces)
    lines = [
        f"# Batch Verification Report",
        f"",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"",
        f"## Coverage Summary",
        f"",
        format_coverage_table(coverage),
        f"",
        f"## Gap Inventory ({len(gaps)} gaps)",
        f"",
        format_gap_inventory(gaps),
        f"",
        f"## Recommendations",
        f"",
    ]
    if not gaps:
        lines.append("All MCUs are mapped. No action required.")
    else:
        critical = sum(1 for g in gaps if g.get("severity") == "CRITICAL")
        high = sum(1 for g in gaps if g.get("severity") == "HIGH")
        if critical > 0:
            lines.append(f"- **CRITICAL:** {critical} MCU(s) require immediate attention.")
        if high > 0:
            lines.append(f"- **HIGH:** {high} MCU(s) should be addressed before batch approval.")
        lines.append("- Review each gap and create MAQ entries or document REJECT rationale.")
    return "\n".join(lines) + "\n"


def generate_delta_queue(traces: list[dict[str, Any]]) -> str:
    """Generate delta_queue_patch.md listing MCUs needing MAQ entries."""
    items = collect_delta_queue(traces)
    lines = [
        "# Delta Queue Patch",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"MCUs requiring new MAQ entries: {len(items)}",
        "",
    ]
    if not items:
        lines.append("_No MCUs require new MAQ entries._")
    else:
        lines.append("| MCU ID | Status | Source File | Severity |")
        lines.append("|---|---|---|---|")
        for item in items:
            mcu_id = item.get("mcu_id", "unknown")
            status = item.get("status", "UNMAPPED")
            source = item.get("source_file", "")
            severity = item.get("severity", "UNKNOWN")
            lines.append(f"| {mcu_id} | {status} | `{source}` | {severity} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    """Entry point: load data, generate reports."""
    parser = argparse.ArgumentParser(
        description="S-04: Generate verification_report.md from coverage + MCU traces.",
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        required=True,
        help="Path to the batch collection directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for reports (default: <batch-dir>).",
    )
    args = parser.parse_args()

    batch_dir: Path = args.batch_dir.resolve()
    if not batch_dir.is_dir():
        log.error("Batch directory does not exist: %s", batch_dir)
        return 1

    coverage_path = batch_dir / "coverage.json"
    if not coverage_path.is_file():
        log.error("coverage.json not found in %s (run batch_compute_coverage.py first)", batch_dir)
        return 1

    trace_path = batch_dir / "mcu_trace.jsonl"
    if not trace_path.is_file():
        log.error("mcu_trace.jsonl not found in %s", batch_dir)
        return 1

    output_dir: Path = (args.output_dir or batch_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    log.info("Loading coverage from %s", coverage_path)
    coverage = load_json(coverage_path)

    log.info("Loading MCU traces from %s", trace_path)
    traces = load_jsonl(trace_path)

    report = generate_report(coverage, traces)
    report_path = output_dir / "verification_report.md"
    report_path.write_text(report, encoding="utf-8")
    log.info("Verification report written to %s", report_path)

    delta = generate_delta_queue(traces)
    delta_path = output_dir / "delta_queue_patch.md"
    delta_path.write_text(delta, encoding="utf-8")
    log.info("Delta queue patch written to %s", delta_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
