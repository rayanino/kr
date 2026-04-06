#!/usr/bin/env python3
"""S-12: Quantitative Norm Metrics — session scorecard generator.

Extracts norm-compliance metrics from a handoff document and dispatch log,
producing a flat JSON scorecard.  Always exits 0 (metrics are informational).

Usage:
    python scripts/compute_session_scorecard.py \
        --handoff reference/handoffs/session4.md \
        --dispatch-log .kr/runtime/dispatch_log.jsonl \
        --output session_scorecard.json
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Severity patterns for M1 autonomy violation detection
_SEVERITY_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "CRITICAL": [
        re.compile(r"\basked\s+(?:the\s+)?owner\s+for\s+technical\b", re.IGNORECASE),
    ],
    "HIGH": [
        re.compile(r"\bshould I proceed\b", re.IGNORECASE),
        re.compile(r"\bshall I\b", re.IGNORECASE),
    ],
    "MEDIUM": [
        re.compile(r"\bpresented\s+options\b", re.IGNORECASE),
        re.compile(r"\bdo you want me to\b", re.IGNORECASE),
        re.compile(r"\bwant me to\b", re.IGNORECASE),
        re.compile(r"\bhow would you like\b", re.IGNORECASE),
    ],
    "LOW": [
        re.compile(r"\bstanding by\b", re.IGNORECASE),
        re.compile(r"\bwaiting for your\b", re.IGNORECASE),
        re.compile(r"\blet me know\b", re.IGNORECASE),
    ],
}


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _extract_int_field(text: str, pattern: str) -> int | None:
    """Extract a single integer via regex, or None if not found."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            return None
    return None


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


# ---------------------------------------------------------------------------
# Metric computations
# ---------------------------------------------------------------------------

def compute_autonomy_violations(
    handoff_text: str,
) -> dict[str, int]:
    """M1: Detect and classify autonomy violations by severity."""
    counts: dict[str, int] = {
        "CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0,
    }
    claimed = _extract_int_field(
        handoff_text, r"Autonomous\s+violations:\s*([0-9]+)"
    )
    for severity, patterns in _SEVERITY_PATTERNS.items():
        for pat in patterns:
            counts[severity] += len(pat.findall(handoff_text))

    total_detected = sum(counts.values())
    return {
        "claimed": claimed if claimed is not None else -1,
        "detected_total": total_detected,
        **{f"detected_{k.lower()}": v for k, v in counts.items()},
    }


def compute_prompt_architect_compliance(
    entries: list[dict[str, object]],
) -> dict[str, float | int]:
    """M2: Prompt-architect compliance percentage."""
    if not entries:
        return {"compliant": 0, "total": 0, "pct": 0.0}
    compliant = sum(
        1 for e in entries if e.get("prompt_architect_used") is True
    )
    total = len(entries)
    pct = round((compliant / total) * 100, 1) if total else 0.0
    return {"compliant": compliant, "total": total, "pct": pct}


def compute_dispatches_by_agent(
    entries: list[dict[str, object]],
) -> dict[str, int]:
    """M3: Group dispatch_log entries by target_agent."""
    counter: Counter[str] = Counter()
    for entry in entries:
        agent = str(entry.get("target_agent", "unknown"))
        counter[agent] += 1
    return dict(counter)


def compute_session_metrics(
    handoff_text: str,
) -> dict[str, int | None]:
    """M4: Extract session-level metrics from handoff."""
    return {
        "atoms_processed": _extract_int_field(
            handoff_text, r"Atoms?\s+processed:\s*([0-9]+)"
        ),
        "atoms_closed": _extract_int_field(
            handoff_text, r"Atoms?\s+CLOSED:\s*([0-9]+)"
        ),
        "test_count": _extract_int_field(
            handoff_text, r"[Tt]ests?:\s*([0-9]+)"
        ),
        "context_peak_pct": _extract_int_field(
            handoff_text, r"[Cc]ontext\s+peak[^0-9]*([0-9]+)"
        ),
    }


# ---------------------------------------------------------------------------
# Scorecard assembly
# ---------------------------------------------------------------------------

def build_scorecard(
    m1: dict[str, int],
    m2: dict[str, float | int],
    m3: dict[str, int],
    m4: dict[str, int | None],
) -> dict[str, object]:
    """Flatten all metrics into a single JSON-serialisable dict."""
    scorecard: dict[str, object] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    # M1
    for key, val in m1.items():
        scorecard[f"m1_autonomy_{key}"] = val
    # M2
    for key, val in m2.items():
        scorecard[f"m2_prompt_architect_{key}"] = val
    # M3
    scorecard["m3_dispatches_by_agent"] = m3
    # M4
    for key, val in m4.items():
        scorecard[f"m4_{key}"] = val

    return scorecard


def _warn_missing(label: str, value: object) -> None:
    """Emit a warning if a key metric is missing."""
    if value is None or value == -1:
        logger.warning("Missing metric: %s", label)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="S-12: Compute Quantitative Norm Metrics."
    )
    parser.add_argument(
        "--handoff", type=Path, required=True,
        help="Path to the handoff .md file.",
    )
    parser.add_argument(
        "--dispatch-log", type=Path, default=None,
        help="Path to dispatch_log.jsonl.",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("session_scorecard.json"),
        help="Path to output scorecard JSON (default: session_scorecard.json).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point.  Always exits 0 — metrics are informational."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    args = parse_args(argv)

    # --- Read handoff ---
    if not args.handoff.exists():
        logger.error("Handoff file not found: %s", args.handoff)
        return 0  # informational — do not gate

    try:
        handoff_text = args.handoff.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("Failed to read handoff: %s", exc)
        return 0

    # --- Load dispatch log ---
    entries: list[dict[str, object]] = []
    if args.dispatch_log is not None:
        entries = _load_dispatch_log(args.dispatch_log)

    # --- Compute metrics ---
    m1 = compute_autonomy_violations(handoff_text)
    m2 = compute_prompt_architect_compliance(entries)
    m3 = compute_dispatches_by_agent(entries)
    m4 = compute_session_metrics(handoff_text)

    # --- Warn on missing ---
    _warn_missing("atoms_processed", m4.get("atoms_processed"))
    _warn_missing("autonomy_claimed", m1.get("claimed"))

    # --- Write scorecard ---
    scorecard = build_scorecard(m1, m2, m3, m4)
    output_path = args.output
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as exc:
        logger.error("Failed to write scorecard: %s", exc)
        return 0

    logger.info("Scorecard written to %s", output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
