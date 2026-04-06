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
import hashlib
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
    """Condition 1: all files in verification_status.json are VERIFIED.

    Uses protocol-correct schema: files[].state (not entries[].status).
    """
    failures: list[str] = []
    for file_entry in status.get("files", []):
        if file_entry.get("state") != "VERIFIED":
            failures.append(
                f"  {file_entry.get('path', 'UNKNOWN')}: state={file_entry.get('state', 'MISSING')}"
            )
    if not status.get("files"):
        failures.append("  No 'files' array found in verification_status.json")
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


def sha256_of_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def check_inventory_hash_drift(
    inventory: dict, batch_dir: Path
) -> tuple[bool, list[str]]:
    """Condition 6: recompute SHA-256 for each file and detect hash drift."""
    failures: list[str] = []
    for file_entry in inventory.get("files", []):
        rel_path = file_entry.get("path", "")
        stored_hash = file_entry.get("sha256", "")
        abs_path = batch_dir / rel_path
        if not abs_path.is_file():
            failures.append(f"  {rel_path}: FILE MISSING (expected by inventory)")
            continue
        current_hash = sha256_of_file(abs_path)
        if current_hash != stored_hash:
            failures.append(
                f"  {rel_path}: DRIFTED (stored={stored_hash[:16]}..., "
                f"current={current_hash[:16]}...)"
            )
    passed = len(failures) == 0
    return passed, failures


def check_queue_terminality(traces: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Condition 7: all MCUs resolved — each has a maq_id or explicit reject."""
    failures: list[str] = []
    for t in traces:
        mcu_id = t.get("mcu_id", "unknown")
        has_maq = bool(t.get("maq_id"))
        mapping = t.get("mapping", "")
        if not has_maq and mapping != "REJECT":
            failures.append(
                f"  {mcu_id}: no maq_id and mapping={mapping or 'NONE'} "
                f"(expected maq_id or REJECT)"
            )
    passed = len(failures) == 0
    return passed, failures


def run_gate(
    status: dict,
    traces: list[dict[str, Any]],
    inventory: dict | None,
    batch_dir: Path,
) -> tuple[bool, str]:
    """Run all conditions and produce a report."""
    conditions: list[tuple[str, tuple[bool, list[str]]]] = [
        ("C1: All files VERIFIED", check_all_files_verified(status)),
        ("C2: Zero MISSED at CRITICAL/HIGH", check_no_critical_high_missed(traces)),
        ("C3: Zero SKIPPED-FILE", check_no_skipped_files(traces)),
        ("C4: All MCUs mapped to MAQ/META/REJECT", check_all_mcus_mapped(traces)),
    ]
    if inventory is not None:
        conditions.append(
            ("C6: No inventory hash drift", check_inventory_hash_drift(inventory, batch_dir))
        )
    conditions.append(
        ("C7: Queue terminality (all MCUs resolved)", check_queue_terminality(traces))
    )

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

    inventory_path = batch_dir / "inventory.json"
    inventory: dict | None = None
    if inventory_path.is_file():
        log.info("Loading inventory from %s", inventory_path)
        inventory = load_json(inventory_path)
    else:
        log.warning("inventory.json not found in %s — hash-drift check skipped", batch_dir)

    log.info("Loading verification status from %s", status_path)
    status = load_json(status_path)

    log.info("Loading MCU traces from %s", trace_path)
    traces = load_jsonl(trace_path)

    passed, report = run_gate(status, traces, inventory, batch_dir)
    log.info("\n%s", report)

    report_path = batch_dir / "gate_report.txt"
    report_path.write_text(report, encoding="utf-8")
    log.info("Gate report written to %s", report_path)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
