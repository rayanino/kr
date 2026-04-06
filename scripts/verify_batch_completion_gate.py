#!/usr/bin/env python3
"""S-05: The 5-condition batch completion gate check.

Verifies that a batch meets all completion criteria before approval:
  1. All files VERIFIED in verification_status.json
  2. Zero MISSED at CRITICAL/HIGH severity in mcu_trace.jsonl
  3. Zero SKIPPED-FILE entries in mcu_trace.jsonl
  4. All MCUs mapped to MAQ/META/REJECT
  5. All above conditions met simultaneously

Exit 0 if all conditions pass, exit 1 with detailed failure report otherwise.

Usage:
    python scripts/verify_batch_completion_gate.py --batch-dir path/to/bundle
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


def check_all_files_verified(status: dict) -> tuple[bool, list[str]]:
    """Condition 1: all files in verification_status.json are VERIFIED."""
    failures: list[str] = []
    for entry in status.get("entries", []):
        if entry.get("status") != "VERIFIED":
            failures.append(
                f"  {entry['path']}: status={entry.get('status', 'MISSING')}"
            )
    passed = len(failures) == 0
    return passed, failures


def check_no_critical_high_missed(traces: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Condition 2: zero MISSED at CRITICAL or HIGH severity."""
    failures: list[str] = []
    for t in traces:
        if t.get("status") == "MISSED" and t.get("severity") in ("CRITICAL", "HIGH"):
            mcu_id = t.get("mcu_id", "unknown")
            severity = t.get("severity", "UNKNOWN")
            failures.append(f"  {mcu_id}: MISSED at {severity}")
    passed = len(failures) == 0
    return passed, failures


def check_no_skipped_files(traces: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Condition 3: zero SKIPPED-FILE entries."""
    failures: list[str] = []
    for t in traces:
        if t.get("status") == "SKIPPED-FILE":
            source = t.get("source_file", "unknown")
            failures.append(f"  {source}: SKIPPED-FILE")
    passed = len(failures) == 0
    return passed, failures


def check_all_mcus_mapped(traces: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Condition 4: all MCUs mapped to MAQ, META, or REJECT."""
    valid_mappings = {"MAQ", "META", "REJECT"}
    failures: list[str] = []
    for t in traces:
        mapping = t.get("mapping")
        if mapping not in valid_mappings:
            mcu_id = t.get("mcu_id", "unknown")
            failures.append(f"  {mcu_id}: mapping={mapping or 'NONE'}")
    passed = len(failures) == 0
    return passed, failures


def run_gate(status: dict, traces: list[dict[str, Any]]) -> tuple[bool, str]:
    """Run all 5 conditions and produce a report."""
    conditions = [
        ("C1: All files VERIFIED", check_all_files_verified(status)),
        ("C2: Zero MISSED at CRITICAL/HIGH", check_no_critical_high_missed(traces)),
        ("C3: Zero SKIPPED-FILE", check_no_skipped_files(traces)),
        ("C4: All MCUs mapped to MAQ/META/REJECT", check_all_mcus_mapped(traces)),
    ]

    all_passed = True
    report_lines = ["Batch Completion Gate Report", "=" * 40, ""]

    for label, (passed, failures) in conditions:
        status_str = "PASS" if passed else "FAIL"
        report_lines.append(f"[{status_str}] {label}")
        if not passed:
            all_passed = False
            for f in failures:
                report_lines.append(f)
        report_lines.append("")

    # Condition 5 is the conjunction of C1-C4
    c5_str = "PASS" if all_passed else "FAIL"
    report_lines.append(f"[{c5_str}] C5: All conditions met")
    report_lines.append("")

    if all_passed:
        report_lines.append("GATE VERDICT: APPROVED")
    else:
        report_lines.append("GATE VERDICT: BLOCKED")

    return all_passed, "\n".join(report_lines)


def main() -> int:
    """Entry point: load data, run gate, report result."""
    parser = argparse.ArgumentParser(
        description="S-05: 5-condition batch completion gate check.",
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        required=True,
        help="Path to the batch collection directory.",
    )
    args = parser.parse_args()

    batch_dir: Path = args.batch_dir.resolve()
    if not batch_dir.is_dir():
        log.error("Batch directory does not exist: %s", batch_dir)
        return 1

    status_path = batch_dir / "verification_status.json"
    if not status_path.is_file():
        log.error("verification_status.json not found in %s", batch_dir)
        return 1

    trace_path = batch_dir / "mcu_trace.jsonl"
    if not trace_path.is_file():
        log.error("mcu_trace.jsonl not found in %s", batch_dir)
        return 1

    log.info("Loading verification status from %s", status_path)
    status = load_json(status_path)

    log.info("Loading MCU traces from %s", trace_path)
    traces = load_jsonl(trace_path)

    passed, report = run_gate(status, traces)
    log.info("\n%s", report)

    report_path = batch_dir / "gate_report.txt"
    report_path.write_text(report, encoding="utf-8")
    log.info("Gate report written to %s", report_path)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
