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


def load_mcu_traces(path: Path) -> tuple[list[dict[str, Any]], int]:
    """Load mcu_trace.jsonl (one JSON object per line).

    Returns (valid_traces, malformed_count). Malformed lines are counted
    separately so callers can fail-closed on data corruption.
    """
    traces: list[dict[str, Any]] = []
    malformed_count = 0
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                traces.append(json.loads(stripped))
            except json.JSONDecodeError as e:
                malformed_count += 1
                log.error(
                    "Malformed line %d in mcu_trace.jsonl: %s", line_num, e
                )
    return traces, malformed_count


def load_verification_status(path: Path) -> dict | None:
    """Load verification_status.json if it exists."""
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_coverage(
    inventory: dict,
    traces: list[dict[str, Any]],
    verification_status: dict | None,
    malformed_count: int,
) -> dict[str, int | float]:
    """Compute coverage metrics from inventory, traces, and verification_status."""
    total_files = inventory.get("file_count", len(inventory.get("files", [])))

    # Fix #8: Count unique file_path values from traces, not total rows.
    trace_verified_files = len(
        {t["file_path"] for t in traces if t.get("file_path") and t.get("file_status") == "VERIFIED"}
    )

    # Fix #9: Use verification_status.json as authoritative file coverage source
    # when available, and cross-check with trace-derived counts.
    if verification_status is not None:
        files_list = verification_status.get("files", [])
        vs_verified = sum(
            1 for f in files_list if f.get("state") == "VERIFIED"
        )
        vs_total = len(files_list)
        if trace_verified_files != vs_verified:
            log.warning(
                "Verified file count mismatch: trace-derived=%d, "
                "verification_status=%d (using verification_status as authoritative)",
                trace_verified_files,
                vs_verified,
            )
        verified_files = vs_verified
        # Use verification_status total if available for cross-check
        if vs_total != total_files:
            log.warning(
                "File count mismatch: inventory=%d, verification_status=%d",
                total_files,
                vs_total,
            )
    else:
        verified_files = trace_verified_files

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
        "malformed_count": malformed_count,
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
    traces, malformed_count = load_mcu_traces(trace_path)
    log.info("Loaded %d MCU trace entries (%d malformed)", len(traces), malformed_count)

    # Fix #9: Load verification_status.json as authoritative file coverage source
    vs_path = batch_dir / "verification_status.json"
    verification_status = load_verification_status(vs_path)
    if verification_status is not None:
        log.info("Loaded verification_status.json from %s", vs_path)
    else:
        log.warning("verification_status.json not found in %s — using trace-derived counts only", batch_dir)

    coverage = compute_coverage(inventory, traces, verification_status, malformed_count)
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

    # Fix #1: Fail-closed on malformed trace lines — data corruption invalidates coverage
    if malformed_count > 0:
        log.error(
            "FAIL: %d malformed line(s) in mcu_trace.jsonl — coverage unreliable",
            malformed_count,
        )
        return 1

    threshold: float = args.threshold
    if coverage["coverage_pct"] >= threshold:
        log.info("PASS: coverage %.1f%% >= threshold %.1f%%", coverage["coverage_pct"], threshold)
        return 0
    else:
        log.error("FAIL: coverage %.1f%% < threshold %.1f%%", coverage["coverage_pct"], threshold)
        return 1


if __name__ == "__main__":
    sys.exit(main())
