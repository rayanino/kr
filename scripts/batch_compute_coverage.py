#!/usr/bin/env python3
"""S-03: Compute MCU mapping completeness for a batch.

Reads mcu_trace.jsonl and inventory.json to report coverage statistics:
total files, verified files, total MCUs, mapped MCUs, missed/softened/
distorted counts, and overall coverage percentage.

Exit 0 if coverage >= threshold (default 100%), exit 1 otherwise.

Usage:
    python scripts/batch_compute_coverage.py --batch-dir path/to/bundle
    python scripts/batch_compute_coverage.py --batch-dir path/to/bundle --threshold 95
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def load_inventory(path: Path) -> dict:
    """Load inventory.json."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_mcu_traces(path: Path) -> list[dict[str, Any]]:
    """Load mcu_trace.jsonl (one JSON object per line)."""
    traces: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                traces.append(json.loads(stripped))
            except json.JSONDecodeError as e:
                log.warning("Skipping malformed line %d in mcu_trace.jsonl: %s", line_num, e)
    return traces


def compute_coverage(
    inventory: dict,
    traces: list[dict[str, Any]],
) -> dict[str, int | float]:
    """Compute coverage metrics from inventory and MCU traces."""
    total_files = inventory.get("file_count", len(inventory.get("files", [])))

    verified_files = sum(
        1 for t in traces if t.get("file_status") == "VERIFIED"
    )
    total_mcus = len(traces)

    mapped_mcus = sum(
        1 for t in traces
        if t.get("mapping") in ("MAQ", "META", "REJECT")
    )
    missed = sum(1 for t in traces if t.get("status") == "MISSED")
    softened = sum(1 for t in traces if t.get("status") == "SOFTENED")
    distorted_tashif = sum(
        1 for t in traces
        if t.get("status") == "DISTORTED" and t.get("distortion_type") == "tashif"
    )
    distorted_tahrif = sum(
        1 for t in traces
        if t.get("status") == "DISTORTED" and t.get("distortion_type") == "tahrif"
    )

    coverage_pct = (mapped_mcus / total_mcus * 100.0) if total_mcus > 0 else 0.0

    return {
        "total_files": total_files,
        "verified_files": verified_files,
        "total_mcus": total_mcus,
        "mapped_mcus": mapped_mcus,
        "missed_count": missed,
        "softened_count": softened,
        "distorted_tashif_count": distorted_tashif,
        "distorted_tahrif_count": distorted_tahrif,
        "coverage_pct": round(coverage_pct, 2),
    }


def main() -> int:
    """Entry point: compute coverage, write coverage.json, check threshold."""
    parser = argparse.ArgumentParser(
        description="S-03: Compute MCU mapping completeness for a batch.",
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        required=True,
        help="Path to the batch collection directory.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=100.0,
        help="Minimum coverage percentage to pass (default: 100).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for coverage.json (default: <batch-dir>/coverage.json).",
    )
    args = parser.parse_args()

    batch_dir: Path = args.batch_dir.resolve()
    if not batch_dir.is_dir():
        log.error("Batch directory does not exist: %s", batch_dir)
        return 1

    inventory_path = batch_dir / "inventory.json"
    if not inventory_path.is_file():
        log.error("inventory.json not found in %s", batch_dir)
        return 1

    trace_path = batch_dir / "mcu_trace.jsonl"
    if not trace_path.is_file():
        log.error("mcu_trace.jsonl not found in %s", batch_dir)
        return 1

    output_path: Path = (args.output or batch_dir / "coverage.json").resolve()

    log.info("Loading inventory from %s", inventory_path)
    inventory = load_inventory(inventory_path)

    log.info("Loading MCU traces from %s", trace_path)
    traces = load_mcu_traces(trace_path)
    log.info("Loaded %d MCU trace entries", len(traces))

    coverage = compute_coverage(inventory, traces)
    log.info(
        "Coverage: %d/%d MCUs mapped (%.1f%%), %d missed, %d softened, "
        "%d tashif, %d tahrif",
        coverage["mapped_mcus"],
        coverage["total_mcus"],
        coverage["coverage_pct"],
        coverage["missed_count"],
        coverage["softened_count"],
        coverage["distorted_tashif_count"],
        coverage["distorted_tahrif_count"],
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(coverage, f, indent=2, ensure_ascii=False)
    log.info("Coverage report written to %s", output_path)

    threshold: float = args.threshold
    if coverage["coverage_pct"] >= threshold:
        log.info("PASS: coverage %.1f%% >= threshold %.1f%%", coverage["coverage_pct"], threshold)
        return 0
    else:
        log.error("FAIL: coverage %.1f%% < threshold %.1f%%", coverage["coverage_pct"], threshold)
        return 1


if __name__ == "__main__":
    sys.exit(main())
