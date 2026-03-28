"""KR-specific evaluation detectors for recursive-improve.

Extends ri's built-in detectors with domain-specific metrics for Arabic
scholarly text processing.  These detect patterns that ri's generic
loop/error/give-up detectors cannot see.

Usage:
    from eval.compute_baselines import ALL_DETECTORS
    results = [detector(trace) for detector in ALL_DETECTORS]
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from recursive_improve.eval.detectors import DetectorResult


# ═══════════════════════════════════════════════════════════════════
# Helper: extract messages from trace
# ═══════════════════════════════════════════════════════════════════


def _get_messages(trace: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract the message list from a trace."""
    return trace.get("messages", [])


def _get_assistant_messages(
    trace: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract assistant messages (LLM responses) from a trace."""
    return [m for m in _get_messages(trace) if m.get("role") == "assistant"]


def _get_user_messages(trace: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract user messages (prompts) from a trace."""
    return [m for m in _get_messages(trace) if m.get("role") == "user"]


def _get_error_messages(trace: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract error messages from a trace."""
    return [m for m in _get_messages(trace) if m.get("error")]


# ═══════════════════════════════════════════════════════════════════
# KR-specific detectors
# ═══════════════════════════════════════════════════════════════════


def detect_json_retry_rate(trace: dict[str, Any]) -> DetectorResult:
    """Detect how often the CLI adapter retries due to JSON parse failures.

    Looks for the retry augmentation text that the CLI adapter injects
    when a previous attempt produced invalid JSON.
    """
    user_msgs = _get_user_messages(trace)
    total = len(user_msgs)
    retries = sum(
        1
        for m in user_msgs
        if "PREVIOUS ATTEMPT PRODUCED INVALID JSON" in m.get("content", "")
    )

    rate = retries / max(total, 1)
    return DetectorResult(
        name="json_retry_rate",
        fired=rate > 0.1,  # >10% retry rate is concerning
        numerator=retries,
        denominator=total,
        value=round(rate, 4),
        details={"threshold": 0.1},
    )


def detect_validation_retry_rate(trace: dict[str, Any]) -> DetectorResult:
    """Detect how often the CLI adapter retries due to Pydantic validation failures."""
    user_msgs = _get_user_messages(trace)
    total = len(user_msgs)
    retries = sum(
        1
        for m in user_msgs
        if "PREVIOUS ATTEMPT FAILED VALIDATION" in m.get("content", "")
    )

    rate = retries / max(total, 1)
    return DetectorResult(
        name="validation_retry_rate",
        fired=rate > 0.1,
        numerator=retries,
        denominator=total,
        value=round(rate, 4),
        details={"threshold": 0.1},
    )


def detect_consensus_disagreement(trace: dict[str, Any]) -> DetectorResult:
    """Detect consensus disagreement between models.

    Looks for assistant messages from different providers on
    semantically similar inputs within the same trace.  When two
    models produce different structured outputs for the same input,
    that's a disagreement.
    """
    assistant_msgs = _get_assistant_messages(trace)
    if len(assistant_msgs) < 2:
        return DetectorResult(name="consensus_disagreement_rate")

    # Group by provider
    by_provider: dict[str, list[dict[str, Any]]] = {}
    for msg in assistant_msgs:
        provider = msg.get("provider", "unknown")
        by_provider.setdefault(provider, []).append(msg)

    if len(by_provider) < 2:
        return DetectorResult(name="consensus_disagreement_rate")

    # Compare outputs from different providers
    providers = list(by_provider.keys())
    total_pairs = 0
    disagreements = 0

    for i in range(len(providers)):
        for j in range(i + 1, len(providers)):
            msgs_a = by_provider[providers[i]]
            msgs_b = by_provider[providers[j]]
            pairs = min(len(msgs_a), len(msgs_b))
            for k in range(pairs):
                total_pairs += 1
                content_a = msgs_a[k].get("content", "")
                content_b = msgs_b[k].get("content", "")
                try:
                    parsed_a = json.loads(content_a)
                    parsed_b = json.loads(content_b)
                    if parsed_a != parsed_b:
                        disagreements += 1
                except (json.JSONDecodeError, TypeError):
                    pass

    rate = disagreements / max(total_pairs, 1)
    return DetectorResult(
        name="consensus_disagreement_rate",
        fired=rate > 0.15,  # >15% disagreement is concerning
        numerator=disagreements,
        denominator=total_pairs,
        value=round(rate, 4),
        details={"providers": providers, "threshold": 0.15},
    )


# Arabic corruption patterns
_MOJIBAKE_PATTERN = re.compile(
    r"[\xc0-\xff]{2,}"  # Latin-1 misencoding sequences
    r"|Ã[\x80-\xbf]"  # Common UTF-8→Latin-1 mojibake
    r"|Ø[\x00-\x7f]"  # Broken Arabic byte sequences
)

_ISOLATED_DIACRITICS = re.compile(
    r"(?<![" + "\u0600-\u06FF" + r"])"  # not preceded by Arabic letter
    r"[\u064B-\u065F\u0670]"  # Arabic diacritical marks
    r"(?![" + "\u0600-\u06FF" + r"])",  # not followed by Arabic letter
)


def detect_arabic_encoding_errors(trace: dict[str, Any]) -> DetectorResult:
    """Detect Arabic text corruption in trace messages.

    Checks for mojibake patterns, isolated diacritics (diacritics
    without a base letter), and other encoding corruption signals.
    """
    all_msgs = _get_messages(trace)
    total = len(all_msgs)
    corrupted = 0
    corruption_details: list[str] = []

    for msg in all_msgs:
        content = msg.get("content", "")
        if not content:
            continue

        issues: list[str] = []

        # Check mojibake
        if _MOJIBAKE_PATTERN.search(content):
            issues.append("mojibake")

        # Check isolated diacritics
        if _ISOLATED_DIACRITICS.search(content):
            issues.append("isolated_diacritics")

        # Check for null bytes
        if "\x00" in content:
            issues.append("null_bytes")

        if issues:
            corrupted += 1
            corruption_details.append(
                f"{msg.get('role', '?')}: {', '.join(issues)}"
            )

    rate = corrupted / max(total, 1)
    return DetectorResult(
        name="arabic_encoding_error_rate",
        fired=rate > 0.0,  # any corruption is a problem
        numerator=corrupted,
        denominator=total,
        value=round(rate, 4),
        details={"corrupted_messages": corruption_details[:10]},
    )


def detect_human_gate_triggers(trace: dict[str, Any]) -> DetectorResult:
    """Detect how often pipeline results trigger human gate review.

    Looks for gate trigger indicators in trace output or messages.
    """
    output = trace.get("output", "") or ""
    msgs = _get_messages(trace)

    gate_keywords = [
        "human_gate",
        "EX-G-001",
        "EX-G-002",
        "EX-G-003",
        "needs_human_gate",
        "gate_trigger",
    ]

    gate_count = 0
    for keyword in gate_keywords:
        if keyword in output:
            gate_count += 1
        for msg in msgs:
            if keyword in msg.get("content", ""):
                gate_count += 1

    total_calls = len(_get_assistant_messages(trace))
    rate = gate_count / max(total_calls, 1)

    return DetectorResult(
        name="human_gate_trigger_rate",
        fired=gate_count > 0,
        numerator=gate_count,
        denominator=total_calls,
        value=round(rate, 4),
        details={"gate_mentions": gate_count},
    )


def detect_low_confidence(trace: dict[str, Any]) -> DetectorResult:
    """Detect LLM responses with low confidence scores.

    Parses JSON responses looking for confidence fields below
    threshold (0.7).
    """
    assistant_msgs = _get_assistant_messages(trace)
    total = 0
    low_conf = 0
    threshold = 0.7

    for msg in assistant_msgs:
        content = msg.get("content", "")
        try:
            parsed = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            continue

        # Recursively find confidence fields
        conf_values = _find_confidence_values(parsed)
        for val in conf_values:
            total += 1
            if val < threshold:
                low_conf += 1

    rate = low_conf / max(total, 1)
    return DetectorResult(
        name="low_confidence_rate",
        fired=rate > 0.2,  # >20% low-confidence responses
        numerator=low_conf,
        denominator=total,
        value=round(rate, 4),
        details={"threshold": threshold},
    )


def _find_confidence_values(obj: Any) -> list[float]:
    """Recursively find numeric 'confidence' fields in a parsed JSON object."""
    values: list[float] = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            if "confidence" in key.lower() and isinstance(val, (int, float)):
                values.append(float(val))
            else:
                values.extend(_find_confidence_values(val))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(_find_confidence_values(item))
    return values


def detect_attribution_conflict(trace: dict[str, Any]) -> DetectorResult:
    """Detect attribution conflicts between models.

    Looks for cases where different assistant messages contain
    different author names or school attributions for the same content.
    """
    assistant_msgs = _get_assistant_messages(trace)
    authors_seen: set[str] = set()
    schools_seen: set[str] = set()

    for msg in assistant_msgs:
        content = msg.get("content", "")
        try:
            parsed = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            continue

        if isinstance(parsed, dict):
            author = parsed.get("author") or parsed.get("author_name") or ""
            school = parsed.get("school") or parsed.get("madhab") or ""
            if author:
                authors_seen.add(str(author))
            if school:
                schools_seen.add(str(school))

    author_conflict = len(authors_seen) > 1
    school_conflict = len(schools_seen) > 1
    conflicts = int(author_conflict) + int(school_conflict)

    return DetectorResult(
        name="attribution_conflict_rate",
        fired=conflicts > 0,
        numerator=conflicts,
        denominator=2,  # author + school
        value=round(conflicts / 2, 4),
        details={
            "authors_seen": sorted(authors_seen),
            "schools_seen": sorted(schools_seen),
            "author_conflict": author_conflict,
            "school_conflict": school_conflict,
        },
    )


# ═══════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════

ALL_DETECTORS = [
    detect_json_retry_rate,
    detect_validation_retry_rate,
    detect_consensus_disagreement,
    detect_arabic_encoding_errors,
    detect_human_gate_triggers,
    detect_low_confidence,
    detect_attribution_conflict,
]


def run_all(trace: dict[str, Any]) -> list[DetectorResult]:
    """Run all KR-specific detectors on a trace."""
    return [detector(trace) for detector in ALL_DETECTORS]


def run_all_on_directory(traces_dir: str | Path) -> dict[str, list[DetectorResult]]:
    """Run all detectors on every trace file in a directory."""
    traces_path = Path(traces_dir)
    results: dict[str, list[DetectorResult]] = {}
    for trace_file in sorted(traces_path.glob("*.json")):
        trace = json.loads(trace_file.read_text(encoding="utf-8"))
        results[trace_file.name] = run_all(trace)
    return results
