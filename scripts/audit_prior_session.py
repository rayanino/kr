#!/usr/bin/env python3
"""S-11: Inter-Session Compliance Audit.

Verifies a prior session's handoff claims against the ledger and
dispatch log.  Produces an audit_report.json with per-check verdicts.

Usage:
    python scripts/audit_prior_session.py \
        --handoff reference/handoffs/session3.md \
        --ledger engines/excerpting/FOUNDATIONS_HARDENING_LEDGER.md \
        --dispatch-log .kr/runtime/dispatch_log.jsonl
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _extract_int_field(text: str, pattern: str) -> int | None:
    """Extract a single integer from a named field using a regex pattern."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            return None
    return None


def _extract_session_date(text: str) -> str | None:
    """Extract a date string (YYYY-MM-DD) from the handoff."""
    match = re.search(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text)
    return match.group(0) if match else None


def _load_dispatch_log(log_path: Path) -> list[dict[str, object]]:
    """Load dispatch_log.jsonl, skipping malformed lines."""
    entries: list[dict[str, object]] = []
    if not log_path.exists():
        return entries
    for line in log_path.read_text(encoding="utf-8").strip().splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            logger.warning("Skipping malformed dispatch log line: %s", line[:80])
    return entries


def _count_ledger_entries_for_date(
    ledger_text: str, date_str: str,
) -> int:
    """Count ledger lines referencing a given date string."""
    return sum(1 for line in ledger_text.splitlines() if date_str in line)


# ---------------------------------------------------------------------------
# Audit checks
# ---------------------------------------------------------------------------

def check_atom_count(
    handoff_text: str, ledger_text: str,
) -> dict[str, str | list[str]]:
    """A1: Verify claimed atom counts against ledger entries."""
    processed = _extract_int_field(handoff_text, r"Atoms?\s+processed:\s*([0-9]+)")
    closed = _extract_int_field(handoff_text, r"Atoms?\s+CLOSED:\s*([0-9]+)")
    date_str = _extract_session_date(handoff_text)

    details: list[str] = []
    if processed is None and closed is None:
        return {
            "name": "A1_atom_count",
            "status": "WARN",
            "details": ["Could not extract atom counts from handoff"],
        }

    if date_str and ledger_text:
        ledger_count = _count_ledger_entries_for_date(ledger_text, date_str)
        details.append(f"Handoff claims processed={processed}, closed={closed}")
        details.append(f"Ledger entries for {date_str}: {ledger_count}")
        if processed is not None and ledger_count != processed:
            return {
                "name": "A1_atom_count",
                "status": "FAIL",
                "details": details + ["Mismatch between claimed and ledger counts"],
            }
    else:
        details.append("Could not determine date or ledger is empty")
        return {"name": "A1_atom_count", "status": "WARN", "details": details}

    return {"name": "A1_atom_count", "status": "PASS", "details": details}


def check_dispatch_count(
    handoff_text: str, entries: list[dict[str, object]],
) -> dict[str, str | list[str]]:
    """A2: Verify claimed dispatch count against dispatch_log."""
    claimed = _extract_int_field(handoff_text, r"Total\s+dispatches:\s*([0-9]+)")
    details: list[str] = []

    if claimed is None:
        return {
            "name": "A2_dispatch_count",
            "status": "WARN",
            "details": ["Could not extract 'Total dispatches' from handoff"],
        }

    actual = len(entries)
    details.append(f"Handoff claims {claimed} dispatches, log has {actual} entries")
    if claimed != actual:
        return {
            "name": "A2_dispatch_count",
            "status": "FAIL",
            "details": details + ["Dispatch count mismatch"],
        }
    return {"name": "A2_dispatch_count", "status": "PASS", "details": details}


def check_doctrine_compliance(
    handoff_text: str, entries: list[dict[str, object]],
) -> dict[str, str | list[str]]:
    """A3: Spot-check doctrine compliance claims."""
    violations = _extract_int_field(
        handoff_text, r"Autonomous\s+violations:\s*([0-9]+)"
    )
    pa_skips = _extract_int_field(
        handoff_text, r"Prompt-architect\s+skips:\s*([0-9]+)"
    )
    details: list[str] = []

    if violations is None and pa_skips is None:
        return {
            "name": "A3_doctrine_compliance",
            "status": "WARN",
            "details": ["Could not extract violation/skip counts from handoff"],
        }

    details.append(f"Claimed violations={violations}, PA skips={pa_skips}")

    if entries:
        sample_size = max(1, len(entries) // 10)
        sample = random.sample(entries, min(sample_size, len(entries)))
        pa_missing = sum(
            1 for e in sample if e.get("prompt_architect_used") is not True
        )
        details.append(
            f"Sampled {len(sample)} entries: {pa_missing} missing prompt_architect"
        )
        if pa_skips is not None and pa_missing > 0 and pa_skips == 0:
            details.append("Claimed 0 PA skips but sample found missing entries")
            return {
                "name": "A3_doctrine_compliance",
                "status": "FAIL",
                "details": details,
            }

    return {"name": "A3_doctrine_compliance", "status": "PASS", "details": details}


def check_session_end(handoff_text: str) -> dict[str, str | list[str]]:
    """A4: Handoff must end with a next-directive or what-remains section."""
    directive_pat = re.compile(
        r"next\s+session\s+directive|what\s+remains", re.IGNORECASE
    )
    found = directive_pat.search(handoff_text) is not None
    status = "PASS" if found else "FAIL"
    details: list[str] = (
        [] if found
        else ["Missing 'NEXT SESSION DIRECTIVE' or 'What Remains' section"]
    )
    return {"name": "A4_session_end", "status": status, "details": details}


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def build_report(
    checks: list[dict[str, str | list[str]]],
) -> dict[str, object]:
    """Assemble the audit report.  WARN does not trigger FAIL."""
    has_fail = any(c["status"] == "FAIL" for c in checks)
    overall = "FAIL" if has_fail else "PASS"
    return {
        "checks": checks,
        "overall": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="S-11: Inter-Session Compliance Audit."
    )
    parser.add_argument(
        "--handoff", type=Path, required=True,
        help="Path to prior session's handoff .md file.",
    )
    parser.add_argument(
        "--ledger", type=Path, required=True,
        help="Path to FOUNDATIONS_HARDENING_LEDGER.md.",
    )
    parser.add_argument(
        "--dispatch-log", type=Path, required=True,
        help="Path to dispatch_log.jsonl.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    args = parse_args(argv)

    # --- Validate inputs ---
    if not args.handoff.exists():
        logger.error("Handoff file not found: %s", args.handoff)
        return 1

    try:
        handoff_text = args.handoff.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("Failed to read handoff: %s", exc)
        return 1

    ledger_text = ""
    if args.ledger.exists():
        try:
            ledger_text = args.ledger.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Failed to read ledger: %s", exc)

    entries = _load_dispatch_log(args.dispatch_log)

    # --- Run audit checks ---
    checks: list[dict[str, str | list[str]]] = [
        check_atom_count(handoff_text, ledger_text),
        check_dispatch_count(handoff_text, entries),
        check_doctrine_compliance(handoff_text, entries),
        check_session_end(handoff_text),
    ]

    # --- Write report ---
    report = build_report(checks)
    report_path = args.handoff.parent / "audit_report.json"
    try:
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as exc:
        logger.error("Failed to write audit report: %s", exc)
        return 1

    logger.info("Audit report written to %s", report_path)
    logger.info("Overall: %s", report["overall"])

    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
