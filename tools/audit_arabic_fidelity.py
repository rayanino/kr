#!/usr/bin/env python3
"""Audit Arabic text fidelity across campaign excerpts.

Checks for:
  - Honorific completeness: mention of محمد/النبي without صلى الله عليه وسلم nearby
  - Quranic bracket consistency: unmatched { } or ﴿ ﴾
  - ZWNJ debris: double U+200C sequences
  - Isnad truncation: عن + name that ends mid-word at excerpt boundary
  - Diacritic density: compare density in text_snippet vs primary_text

Usage:
    python tools/audit_arabic_fidelity.py --root integration_tests/campaign_20260331
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace",
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace",
    )

PACKAGES = ["ext_39_masala", "ext_46_qa", "ibn_aqil_v1", "ibn_aqil_v3", "taysir"]

# Prophet name patterns — using explicit ranges, not \b
PROPHET_MENTION_RE = re.compile(
    r"(?:النبي|الرسول|محمد(?:[\s\u200c]*بن[\s\u200c]*عبد[\s\u200c]*الله)?)"
    r"(?![\u0600-\u06ff])"
)

# Honorific patterns that should follow prophet mentions
HONORIFIC_RE = re.compile(
    r"صلى[\s\u200c]*الله[\s\u200c]*عليه[\s\u200c]*وسلم"
    r"|ﷺ"
    r"|صلعم"
    r"|\u0001\u0002"  # catch encoding artifacts
)

# ZWNJ = U+200C
ZWNJ = "\u200c"
DOUBLE_ZWNJ_RE = re.compile(r"\u200c{2,}")

# Quranic bracket pairs
BRACKET_PAIRS = [
    ("{", "}"),
    ("\ufb50", "\ufb51"),  # rarely used
    ("\ufd3e", "\ufd3f"),  # ornate parens
    ("\ufe59", "\ufe5a"),  # small parens
]
# Standard Quranic brackets
QURAN_OPEN = "\ufd3f"   # ﴿
QURAN_CLOSE = "\ufd3e"  # ﴾

# Isnad truncation: عن + name near excerpt boundary
# Using explicit Arabic character range
AN_PATTERN = re.compile(r"عن[\s\u200c]+([\u0600-\u06ff\s]{3,}?)$")


def diacritic_density(text: str) -> float:
    """Compute fraction of characters that are combining marks (diacritics)."""
    if not text:
        return 0.0
    combining = sum(1 for ch in text if unicodedata.combining(ch))
    return combining / len(text) if len(text) > 0 else 0.0


def check_honorific_completeness(
    primary_text: str, excerpt_id: str, pkg_name: str,
) -> list[dict[str, Any]]:
    """Flag prophet mentions without nearby honorific."""
    flags: list[dict[str, Any]] = []
    for match in PROPHET_MENTION_RE.finditer(primary_text):
        pos = match.start()
        # Search for honorific within 50 chars after the mention
        search_end = min(len(primary_text), pos + len(match.group()) + 80)
        search_start = max(0, pos - 20)
        context = primary_text[search_start:search_end]

        if not HONORIFIC_RE.search(context):
            flags.append({
                "package": pkg_name,
                "excerpt_id": excerpt_id,
                "flag_type": "missing_honorific",
                "severity": "high",
                "mention": match.group(),
                "position": pos,
                "context": primary_text[max(0, pos - 10):min(len(primary_text), pos + 60)],
                "message": (
                    f"Prophet mention '{match.group()}' without honorific nearby"
                ),
            })
    return flags


def check_quranic_brackets(
    primary_text: str, excerpt_id: str, pkg_name: str,
) -> list[dict[str, Any]]:
    """Flag unmatched Quranic brackets."""
    flags: list[dict[str, Any]] = []

    # Check curly braces used for Quranic text
    open_curly = primary_text.count("{")
    close_curly = primary_text.count("}")
    if open_curly != close_curly:
        flags.append({
            "package": pkg_name,
            "excerpt_id": excerpt_id,
            "flag_type": "unmatched_curly_brackets",
            "severity": "medium",
            "open_count": open_curly,
            "close_count": close_curly,
            "message": (
                f"Unmatched curly brackets: {open_curly} open vs {close_curly} close"
            ),
        })

    # Check ornate Quranic brackets ﴿ ﴾
    open_quran = primary_text.count(QURAN_OPEN)
    close_quran = primary_text.count(QURAN_CLOSE)
    if open_quran != close_quran:
        flags.append({
            "package": pkg_name,
            "excerpt_id": excerpt_id,
            "flag_type": "unmatched_quranic_brackets",
            "severity": "high",
            "open_count": open_quran,
            "close_count": close_quran,
            "message": (
                f"Unmatched Quranic brackets ﴿﴾: {open_quran} open vs {close_quran} close"
            ),
        })

    return flags


def check_zwnj_debris(
    primary_text: str, excerpt_id: str, pkg_name: str,
) -> list[dict[str, Any]]:
    """Flag double ZWNJ sequences."""
    flags: list[dict[str, Any]] = []
    matches = list(DOUBLE_ZWNJ_RE.finditer(primary_text))
    if matches:
        flags.append({
            "package": pkg_name,
            "excerpt_id": excerpt_id,
            "flag_type": "double_zwnj",
            "severity": "low",
            "count": len(matches),
            "positions": [m.start() for m in matches[:5]],
            "message": f"{len(matches)} double-ZWNJ sequences found",
        })
    return flags


def check_isnad_truncation(
    primary_text: str, excerpt_id: str, pkg_name: str,
) -> list[dict[str, Any]]:
    """Flag isnad chains that appear truncated at excerpt boundary."""
    flags: list[dict[str, Any]] = []

    # Check last 100 chars for an عن + name pattern that might be truncated
    tail = primary_text[-100:] if len(primary_text) > 100 else primary_text
    match = AN_PATTERN.search(tail)
    if match:
        name_fragment = match.group(1).strip()
        # If the name ends with a common incomplete pattern
        # (e.g., "عبد ال" without completion, or a single word)
        words = name_fragment.split()
        if len(words) <= 1 or name_fragment.endswith("ال"):
            flags.append({
                "package": pkg_name,
                "excerpt_id": excerpt_id,
                "flag_type": "isnad_truncation",
                "severity": "medium",
                "fragment": name_fragment,
                "message": (
                    f"Possible isnad truncation at excerpt boundary: "
                    f"'عن {name_fragment}'"
                ),
            })

    return flags


def check_diacritic_density(
    primary_text: str, text_snippet: str, excerpt_id: str, pkg_name: str,
) -> list[dict[str, Any]]:
    """Flag significant diacritic density differences between snippet and full text."""
    flags: list[dict[str, Any]] = []
    if len(primary_text) < 50 or len(text_snippet) < 20:
        return flags

    snippet_density = diacritic_density(text_snippet)
    full_density = diacritic_density(primary_text)

    # Flag if snippet density differs by >50% relative
    if full_density > 0.02:  # Only check if text has meaningful diacritics
        ratio = snippet_density / full_density if full_density > 0 else 0
        if ratio < 0.5 or ratio > 2.0:
            flags.append({
                "package": pkg_name,
                "excerpt_id": excerpt_id,
                "flag_type": "diacritic_density_mismatch",
                "severity": "low",
                "snippet_density": round(snippet_density, 4),
                "full_density": round(full_density, 4),
                "ratio": round(ratio, 2),
                "message": (
                    f"Diacritic density mismatch: snippet={snippet_density:.3f} "
                    f"vs full={full_density:.3f} (ratio={ratio:.2f})"
                ),
            })

    return flags


def audit_package(root: Path, pkg_name: str) -> list[dict[str, Any]]:
    """Audit one package for Arabic fidelity issues."""
    all_flags: list[dict[str, Any]] = []
    exc_path = root / pkg_name / "excerpts.jsonl"
    if not exc_path.exists():
        return all_flags

    for line in exc_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        exc = json.loads(stripped)
        excerpt_id = exc.get("excerpt_id", "")
        primary_text = exc.get("primary_text", "")
        text_snippet = exc.get("text_snippet", "")

        all_flags.extend(
            check_honorific_completeness(primary_text, excerpt_id, pkg_name)
        )
        all_flags.extend(
            check_quranic_brackets(primary_text, excerpt_id, pkg_name)
        )
        all_flags.extend(
            check_zwnj_debris(primary_text, excerpt_id, pkg_name)
        )
        all_flags.extend(
            check_isnad_truncation(primary_text, excerpt_id, pkg_name)
        )
        all_flags.extend(
            check_diacritic_density(primary_text, text_snippet, excerpt_id, pkg_name)
        )

    return all_flags


def build_summary(flags: list[dict[str, Any]]) -> dict[str, Any]:
    """Build Arabic fidelity summary."""
    by_type: Counter[str] = Counter()
    by_severity: Counter[str] = Counter()
    by_package: Counter[str] = Counter()

    for flag in flags:
        by_type[flag["flag_type"]] += 1
        by_severity[flag["severity"]] += 1
        by_package[flag["package"]] += 1

    return {
        "total_flags": len(flags),
        "by_type": dict(by_type.most_common()),
        "by_severity": dict(by_severity.most_common()),
        "by_package": dict(by_package.most_common()),
        "high_severity_count": by_severity.get("high", 0),
        "medium_severity_count": by_severity.get("medium", 0),
        "low_severity_count": by_severity.get("low", 0),
    }


def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory of the campaign run.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    analysis_dir = root / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    all_flags: list[dict[str, Any]] = []
    for pkg_name in PACKAGES:
        pkg_flags = audit_package(root, pkg_name)
        all_flags.extend(pkg_flags)
        print(f"  {pkg_name}: {len(pkg_flags)} flags")

    # Write flags
    flags_path = analysis_dir / "arabic_fidelity_flags.jsonl"
    with flags_path.open("w", encoding="utf-8") as f:
        for flag in all_flags:
            f.write(json.dumps(flag, ensure_ascii=False) + "\n")

    # Write summary
    summary = build_summary(all_flags)
    summary_path = analysis_dir / "arabic_fidelity_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nArabic fidelity audit: {len(all_flags)} total flags")
    print(f"  High: {summary['high_severity_count']}")
    print(f"  Medium: {summary['medium_severity_count']}")
    print(f"  Low: {summary['low_severity_count']}")
    for flag_type, count in sorted(summary["by_type"].items(), key=lambda x: -x[1]):
        print(f"    {flag_type}: {count}")
    print(f"Output: {flags_path}")
    print(f"Summary: {summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
