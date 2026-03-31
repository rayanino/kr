#!/usr/bin/env python3
"""Select gold standard candidate excerpts from a campaign catalog.

Usage:
    python tools/select_gold_candidates.py --root integration_tests/campaign_20260331

Reads excerpt_catalog.jsonl from <root>/analysis/ and produces gold_candidates.jsonl
in the same directory. Selects ~100 candidates stratified by package and function.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace",
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace",
    )

REPO_ROOT = Path(__file__).resolve().parents[1]

# Target counts per package
TARGETS: dict[str, int] = {
    "taysir": 30,
    "ibn_aqil_v1": 15,
    "ibn_aqil_v3": 15,
    "ext_39_masala": 20,
    "ext_46_qa": 20,
}

# Genre labels for each package
GENRES: dict[str, str] = {
    "taysir": "fiqh_sharh",
    "ibn_aqil_v1": "nahw_sharh",
    "ibn_aqil_v3": "nahw_sharh",
    "ext_39_masala": "fiqh_masala",
    "ext_46_qa": "usul_al_nahw",
}

# Minimum word count and max word count
MIN_WORDS = 30
MAX_WORDS = 350


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read JSONL file."""
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows


def load_full_excerpts(root: Path, pkg_name: str) -> dict[str, dict[str, Any]]:
    """Load full excerpt records for a package, keyed by excerpt_id."""
    exc_path = root / pkg_name / "excerpts.jsonl"
    result: dict[str, dict[str, Any]] = {}
    if exc_path.exists():
        for line in exc_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                exc = json.loads(stripped)
                result[exc["excerpt_id"]] = exc
    return result


def load_failure_chunk_ids(root: Path, pkg_name: str) -> set[str]:
    """Load chunk IDs that had phase2a or phase2b failures."""
    failed_chunks: set[str] = set()
    for fail_file in ("phase2a_failures.jsonl", "phase2b_failures.jsonl"):
        path = root / pkg_name / fail_file
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped:
                    data = json.loads(stripped)
                    chunk_id = data.get("chunk_id", "")
                    if chunk_id:
                        failed_chunks.add(chunk_id)
    return failed_chunks


def load_drop_excerpt_ids(root: Path, pkg_name: str) -> set[str]:
    """Load excerpt IDs that were validation-dropped."""
    dropped: set[str] = set()
    path = root / pkg_name / "validation_drops.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                data = json.loads(stripped)
                eid = data.get("excerpt_id", "")
                if eid:
                    dropped.add(eid)
    return dropped


def is_eligible(
    row: dict[str, Any],
    failed_chunks: set[str],
    dropped_ids: set[str],
) -> bool:
    """Check if an excerpt catalog row is eligible for gold selection."""
    excerpt_id = row.get("excerpt_id", "")

    # Not from a failed chunk
    # Extract chunk_id from excerpt_id: exc_{source}_{div_id}_{chunk_idx}_{unit_idx}
    parts = excerpt_id.split("_")
    # Reconstruct possible chunk_id patterns
    # The div_id is embedded in the excerpt_id
    # For simplicity, check if any failed chunk_id is a prefix of the div portion

    # Self-containment filter
    sc = row.get("self_containment", "")
    if sc not in ("FULL", "PARTIAL"):
        return False

    # Word count filter
    wc = row.get("word_count", 0)
    if wc < MIN_WORDS or wc > MAX_WORDS:
        return False

    # Not validation-dropped
    if excerpt_id in dropped_ids:
        return False

    # Has gate_flags or review_flags? Still eligible, but lower tier
    # All required metadata present
    if not row.get("excerpt_id"):
        return False
    if row.get("topic_count", 0) == 0:
        return False
    if not row.get("primary_function"):
        return False

    return True


def assign_tier(row: dict[str, Any]) -> str:
    """Assign quality tier A/B/C to a candidate."""
    flags = row.get("gate_flags", [])
    review_flags = row.get("review_flags", [])
    sc = row.get("self_containment", "")
    topic_count = row.get("topic_count", 0)
    scholar_count = row.get("scholar_count", 0)
    wc = row.get("word_count", 0)

    # Tier A: no flags, FULL, good word count, topics present
    if (
        not flags
        and not review_flags
        and sc == "FULL"
        and topic_count >= 2
        and 50 <= wc <= 250
    ):
        return "A"

    # Tier B: minor flags or PARTIAL, but otherwise good
    if (
        sc in ("FULL", "PARTIAL")
        and topic_count >= 1
        and not any("failed" in f for f in review_flags)
    ):
        return "B"

    return "C"


def select_for_package(
    catalog_rows: list[dict[str, Any]],
    full_excerpts: dict[str, dict[str, Any]],
    failed_chunks: set[str],
    dropped_ids: set[str],
    target: int,
) -> list[dict[str, Any]]:
    """Select gold candidates for one package, stratified by function."""
    # Filter eligible
    eligible = [
        row for row in catalog_rows
        if is_eligible(row, failed_chunks, dropped_ids)
    ]

    # Group by primary_function
    by_function: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        by_function[row["primary_function"]].append(row)

    # Sort each group by tier (A first), then word count (prefer mid-range)
    for func in by_function:
        by_function[func].sort(
            key=lambda r: (
                {"A": 0, "B": 1, "C": 2}.get(assign_tier(r), 3),
                abs(r.get("word_count", 0) - 120),  # prefer mid-range
            )
        )

    # Distribute target across functions proportionally
    total_eligible = len(eligible)
    if total_eligible == 0:
        return []

    selected: list[dict[str, Any]] = []
    functions_sorted = sorted(by_function.keys(), key=lambda f: -len(by_function[f]))

    # Allocate proportionally, minimum 1 per function if possible
    remaining = target
    allocations: dict[str, int] = {}
    for func in functions_sorted:
        proportion = len(by_function[func]) / total_eligible
        alloc = max(1, round(proportion * target))
        allocations[func] = min(alloc, len(by_function[func]), remaining)
        remaining -= allocations[func]
        if remaining <= 0:
            break

    # If remaining > 0, give extras to largest groups
    if remaining > 0:
        for func in functions_sorted:
            can_add = len(by_function[func]) - allocations.get(func, 0)
            add = min(can_add, remaining)
            allocations[func] = allocations.get(func, 0) + add
            remaining -= add
            if remaining <= 0:
                break

    # Select from each function
    for func, alloc in allocations.items():
        candidates = by_function[func][:alloc]
        for row in candidates:
            excerpt_id = row["excerpt_id"]
            full_exc = full_excerpts.get(excerpt_id, {})
            tier = assign_tier(row)

            selected.append({
                "package": row["package"],
                "genre": GENRES.get(row["package"], "unknown"),
                "excerpt_id": excerpt_id,
                "primary_function": row["primary_function"],
                "self_containment": row["self_containment"],
                "word_count": row["word_count"],
                "excerpt_topic": row.get("excerpt_topic", []),
                "primary_text": full_exc.get("primary_text", ""),
                "text_snippet": row.get("text_snippet", ""),
                "candidate_tier": tier,
                "selection_reason": (
                    f"Tier {tier}: {row['primary_function']}, "
                    f"{row['word_count']}w, sc={row['self_containment']}, "
                    f"{row['topic_count']} topics"
                ),
            })

    return selected


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

    # Load catalog
    catalog_path = analysis_dir / "excerpt_catalog.jsonl"
    if not catalog_path.exists():
        print(f"ERROR: {catalog_path} not found. Run build_campaign_catalog.py first.")
        return 1
    catalog = read_jsonl(catalog_path)

    # Group catalog by package
    by_package: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in catalog:
        by_package[row["package"]].append(row)

    all_gold: list[dict[str, Any]] = []

    for pkg_name, target in TARGETS.items():
        pkg_rows = by_package.get(pkg_name, [])
        if not pkg_rows:
            print(f"WARNING: No catalog rows for {pkg_name}")
            continue

        full_excerpts = load_full_excerpts(root, pkg_name)
        failed_chunks = load_failure_chunk_ids(root, pkg_name)
        dropped_ids = load_drop_excerpt_ids(root, pkg_name)

        selected = select_for_package(
            pkg_rows, full_excerpts, failed_chunks, dropped_ids, target,
        )
        all_gold.extend(selected)
        print(f"  {pkg_name}: {len(selected)}/{target} selected "
              f"(eligible: {sum(1 for r in pkg_rows if is_eligible(r, failed_chunks, dropped_ids))})")

    # Write output
    out_path = analysis_dir / "gold_candidates.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in all_gold:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Summary
    tier_counts = defaultdict(int)
    for row in all_gold:
        tier_counts[row["candidate_tier"]] += 1

    print(f"\nGold candidates: {len(all_gold)} total")
    for tier in ("A", "B", "C"):
        print(f"  Tier {tier}: {tier_counts.get(tier, 0)}")
    print(f"Output: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
