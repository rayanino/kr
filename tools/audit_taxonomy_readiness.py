#!/usr/bin/env python3
"""Audit excerpts for taxonomy readiness risks.

Flags excerpts at risk of downstream damage in the taxonomy engine:
  - structural_transition with >20 words (might contain hidden rulings)
  - excerpt_topic with only 1 very broad term
  - primary_function = editorial_note for >100 words (misclassified muqaddimah?)
  - evidence_hadith with no takhrij_data and no evidence_refs (orphaned evidence)
  - quoted_scholars with role=quoted_opinion where transmission formula present

Usage:
    python tools/audit_taxonomy_readiness.py --root integration_tests/campaign_20260331
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from collections import Counter, defaultdict
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

# Broad topic terms that are too generic for taxonomy placement
BROAD_TOPICS = {
    "كتاب الطهارة", "كتاب الصلاة", "كتاب الزكاة", "كتاب الصيام",
    "كتاب الحج", "كتاب البيوع", "كتاب النكاح", "كتاب الطلاق",
    "كتاب الجنايات", "كتاب الحدود", "كتاب الأقضية",
    "باب", "فصل", "كتاب",
}

# Transmission formula patterns (isnad indicators)
# Using explicit Unicode ranges instead of \b for Arabic
TRANSMISSION_PATTERNS = [
    re.compile(r"حدثنا"),
    re.compile(r"أخبرنا"),
    re.compile(r"أنبأنا"),
    re.compile(r"سمعت"),
    re.compile(r"قرأت على"),
    re.compile(r"أجاز[نل]"),
    re.compile(r"عن[\s\u200c]+[\u0600-\u06ff].*عن[\s\u200c]+[\u0600-\u06ff]"),  # chain pattern
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read JSONL file."""
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows


def count_arabic_words(text: str) -> int:
    """Count whitespace-delimited tokens containing Arabic characters."""
    count = 0
    for token in text.split():
        for ch in token:
            if "\u0600" <= ch <= "\u06ff":
                count += 1
                break
    return count


def has_transmission_formula(text: str) -> bool:
    """Check if text contains hadith transmission formulas."""
    for pattern in TRANSMISSION_PATTERNS:
        if pattern.search(text):
            return True
    return False


def audit_package(root: Path, pkg_name: str) -> list[dict[str, Any]]:
    """Audit one package for taxonomy readiness risks."""
    flags: list[dict[str, Any]] = []
    exc_path = root / pkg_name / "excerpts.jsonl"
    if not exc_path.exists():
        return flags

    for line in exc_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        exc = json.loads(stripped)
        excerpt_id = exc.get("excerpt_id", "")
        primary_text = exc.get("primary_text", "")
        primary_function = exc.get("primary_function", "")
        excerpt_topic = exc.get("excerpt_topic", [])
        quoted_scholars = exc.get("quoted_scholars", [])
        evidence_refs = exc.get("evidence_refs", [])
        takhrij_data = exc.get("takhrij_data")
        word_count = count_arabic_words(primary_text)

        # Check 1: structural_transition with >20 words
        if primary_function == "structural_transition" and word_count > 20:
            flags.append({
                "package": pkg_name,
                "excerpt_id": excerpt_id,
                "flag_type": "structural_transition_long",
                "severity": "high",
                "word_count": word_count,
                "message": (
                    f"structural_transition with {word_count} words — may contain "
                    f"hidden rulings or substantive content"
                ),
                "text_snippet": primary_text[:100],
            })

        # Check 2: excerpt_topic with only 1 very broad term
        if len(excerpt_topic) == 1:
            topic = excerpt_topic[0]
            is_broad = False
            for broad in BROAD_TOPICS:
                if topic == broad or topic.startswith(broad):
                    is_broad = True
                    break
            # Also flag if topic is just a single common word
            if is_broad or len(topic) <= 6:
                flags.append({
                    "package": pkg_name,
                    "excerpt_id": excerpt_id,
                    "flag_type": "broad_topic",
                    "severity": "medium",
                    "topic": topic,
                    "message": (
                        f"Single broad topic '{topic}' — needs specifics for "
                        f"taxonomy placement"
                    ),
                })

        # Check 3: editorial_note for >100 words
        if primary_function == "editorial_note" and word_count > 100:
            flags.append({
                "package": pkg_name,
                "excerpt_id": excerpt_id,
                "flag_type": "editorial_note_long",
                "severity": "medium",
                "word_count": word_count,
                "message": (
                    f"editorial_note with {word_count} words — might be "
                    f"misclassified muqaddimah or substantive commentary"
                ),
                "text_snippet": primary_text[:100],
            })

        # Check 4: evidence_hadith with no takhrij_data and no evidence_refs
        if primary_function == "evidence_hadith":
            has_takhrij = takhrij_data is not None and len(takhrij_data) > 0
            has_evidence = len(evidence_refs) > 0
            if not has_takhrij and not has_evidence:
                flags.append({
                    "package": pkg_name,
                    "excerpt_id": excerpt_id,
                    "flag_type": "orphaned_evidence",
                    "severity": "high",
                    "message": (
                        "evidence_hadith with no takhrij_data and no evidence_refs — "
                        "orphaned evidence that cannot be linked"
                    ),
                    "text_snippet": primary_text[:100],
                })

        # Check 5: quoted_scholars with role=quoted_opinion + transmission formula
        for scholar in quoted_scholars:
            if scholar.get("role") == "quoted_opinion":
                mention = scholar.get("mention_text", "")
                # Check surrounding text for transmission formulas
                if has_transmission_formula(primary_text):
                    # Check if the scholar mention is near a transmission formula
                    if mention in primary_text:
                        mention_pos = primary_text.find(mention)
                        context_start = max(0, mention_pos - 50)
                        context_end = min(len(primary_text), mention_pos + len(mention) + 50)
                        context = primary_text[context_start:context_end]
                        if has_transmission_formula(context):
                            flags.append({
                                "package": pkg_name,
                                "excerpt_id": excerpt_id,
                                "flag_type": "narrator_as_opinion",
                                "severity": "high",
                                "scholar": mention,
                                "message": (
                                    f"Scholar '{mention}' has role=quoted_opinion but "
                                    f"transmission formula detected nearby — should "
                                    f"likely be narrator"
                                ),
                                "context": context[:150],
                            })
                    break  # One flag per excerpt is sufficient

    return flags


def build_summary(flags: list[dict[str, Any]]) -> dict[str, Any]:
    """Build taxonomy readiness summary."""
    by_type: dict[str, int] = Counter()
    by_severity: dict[str, int] = Counter()
    by_package: dict[str, int] = Counter()

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
    flags_path = analysis_dir / "taxonomy_readiness_flags.jsonl"
    with flags_path.open("w", encoding="utf-8") as f:
        for flag in all_flags:
            f.write(json.dumps(flag, ensure_ascii=False) + "\n")

    # Write summary
    summary = build_summary(all_flags)
    summary_path = analysis_dir / "taxonomy_readiness_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nTaxonomy readiness audit: {len(all_flags)} total flags")
    print(f"  High: {summary['high_severity_count']}")
    print(f"  Medium: {summary['medium_severity_count']}")
    print(f"Output: {flags_path}")
    print(f"Summary: {summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
