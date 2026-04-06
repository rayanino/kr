#!/usr/bin/env python3
"""S-10: Norm-Linter Gate for session handoff documents.

Scans a handoff .md file for permission-seeking language, missing
next-step directives, orphaned dispatches, and prompt-architect
compliance.  Produces a lint_report.json alongside the handoff.

Usage:
    python scripts/lint_session_norms.py --handoff reference/handoffs/session4.md
    python scripts/lint_session_norms.py --handoff session.md --dispatch-log .kr/runtime/dispatch_log.jsonl
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# C1: Permission-seeking / passivity patterns (case-insensitive)
_PERMISSION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bshould I\b", re.IGNORECASE),
    re.compile(r"\bdo you want me to\b", re.IGNORECASE),
    re.compile(r"\bwant me to\b", re.IGNORECASE),
    re.compile(r"\bshall I\b", re.IGNORECASE),
    re.compile(r"\bstanding by\b", re.IGNORECASE),
    re.compile(r"\bwaiting for your\b", re.IGNORECASE),
    re.compile(r"\blet me know\b", re.IGNORECASE),
    re.compile(r"\bhow would you like\b", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------

def check_permission_language(lines: list[str]) -> dict[str, str | list[str]]:
    """C1: Scan for permission-seeking language."""
    violations: list[str] = []
    for lineno, line in enumerate(lines, 1):
        for pat in _PERMISSION_PATTERNS:
            if pat.search(line):
                violations.append(f"line {lineno}: matched '{pat.pattern}'")
    status = "FAIL" if violations else "PASS"
    return {"name": "C1_permission_language", "status": status, "details": violations}


def check_next_step_presence(text: str) -> dict[str, str | list[str]]:
    """C2: Handoff must contain a NEXT SESSION DIRECTIVE section."""
    pattern = re.compile(r"next\s+session\s+directive", re.IGNORECASE)
    found = pattern.search(text) is not None
    status = "PASS" if found else "FAIL"
    details: list[str] = [] if found else ["Missing 'NEXT SESSION DIRECTIVE' section"]
    return {"name": "C2_next_step_presence", "status": status, "details": details}


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


def check_dispatch_completeness(
    entries: list[dict[str, object]],
) -> dict[str, str | list[str]]:
    """C3: Every 'dispatched' entry must have a 'completed' or 'unavailable' peer."""
    dispatched: dict[str, int] = {}
    resolved: set[str] = set()
    for entry in entries:
        status = str(entry.get("status", ""))
        agent = str(entry.get("target_agent", "unknown"))
        ts = str(entry.get("timestamp", ""))
        key = f"{agent}:{ts}"
        if status == "dispatched":
            dispatched[key] = dispatched.get(key, 0) + 1
        elif status in ("completed", "unavailable"):
            resolved.add(key)

    orphaned = [k for k in dispatched if k not in resolved]
    status = "FAIL" if orphaned else "PASS"
    details = [f"Orphaned dispatch: {k}" for k in orphaned]
    return {"name": "C3_dispatch_completeness", "status": status, "details": details}


def check_prompt_architect_compliance(
    entries: list[dict[str, object]],
) -> dict[str, str | list[str]]:
    """C4: Every dispatch entry must have prompt_architect_used=true."""
    non_compliant = 0
    detail_lines: list[str] = []
    for entry in entries:
        if entry.get("prompt_architect_used") is not True:
            non_compliant += 1
            agent = entry.get("target_agent", "unknown")
            ts = entry.get("timestamp", "")
            detail_lines.append(
                f"prompt_architect_used != true for {agent} at {ts}"
            )
    status = "FAIL" if non_compliant > 0 else "PASS"
    if non_compliant:
        detail_lines.insert(0, f"Total non-compliant entries: {non_compliant}")
    return {
        "name": "C4_prompt_architect_compliance",
        "status": status,
        "details": detail_lines,
    }


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def build_report(
    checks: list[dict[str, str | list[str]]],
) -> dict[str, object]:
    """Assemble the lint report with overall verdict."""
    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "checks": checks,
        "overall": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="S-10: Norm-Linter Gate for session handoff documents."
    )
    parser.add_argument(
        "--handoff", type=Path, required=True,
        help="Path to the handoff .md file.",
    )
    parser.add_argument(
        "--dispatch-log", type=Path, default=None,
        help="Path to dispatch_log.jsonl (optional).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    args = parse_args(argv)

    if not args.handoff.exists():
        logger.error("Handoff file not found: %s", args.handoff)
        return 1

    try:
        handoff_text = args.handoff.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("Failed to read handoff: %s", exc)
        return 1

    lines = handoff_text.splitlines()

    # --- Run checks ---
    checks: list[dict[str, str | list[str]]] = [
        check_permission_language(lines),
        check_next_step_presence(handoff_text),
    ]

    if args.dispatch_log is not None:
        entries = _load_dispatch_log(args.dispatch_log)
        checks.append(check_dispatch_completeness(entries))
        checks.append(check_prompt_architect_compliance(entries))
    else:
        logger.info("No dispatch log provided; skipping C3/C4 checks.")

    # --- Write report ---
    report = build_report(checks)
    report_path = args.handoff.parent / "lint_report.json"
    try:
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as exc:
        logger.error("Failed to write lint report: %s", exc)
        return 1

    logger.info("Lint report written to %s", report_path)
    logger.info("Overall: %s", report["overall"])

    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
