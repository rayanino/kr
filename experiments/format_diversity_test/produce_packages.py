"""Deliverable 1: Produce normalized packages for format diversity fixtures.

Runs normalize_source() on each fixture and writes manifest.json + content.jsonl
to experiments/format_diversity_test/packages/{fixture_name}/.

Fixtures:
  - ibn_aqil_v1 (verse-commentary, multi-layer) — PRIMARY
  - ibn_aqil_v3 (verse-commentary, multi-layer) — PRIMARY
  - taysir (longer fiqh prose) — PRIMARY
  - ext_39_masala (masala format) — OPTIONAL
  - ext_46_qa (QA format) — OPTIONAL
"""
from __future__ import annotations

import re
import statistics
import sys
import traceback
from pathlib import Path
from typing import Any

# Project root for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.tests.conftest import _make_source_metadata

FIXTURES: list[dict[str, Any]] = [
    # PRIMARY — must succeed
    {
        "name": "ibn_aqil_v1",
        "path": "experiments/format_diversity_test/fixtures/ibn_aqil/001.htm",
        "is_multi_layer": True,
        "priority": "PRIMARY",
    },
    {
        "name": "ibn_aqil_v3",
        "path": "experiments/format_diversity_test/fixtures/ibn_aqil/003.htm",
        "is_multi_layer": True,
        "priority": "PRIMARY",
    },
    {
        "name": "taysir",
        "path": "experiments/format_diversity_test/fixtures/taysir_al_ilam/book.htm",
        "is_multi_layer": False,
        "priority": "PRIMARY",
    },
    # OPTIONAL — skip on failure or <5 leaf divisions
    {
        "name": "ext_39_masala",
        "path": "tests/fixtures/shamela_extended/ext_39/book.htm",
        "is_multi_layer": False,
        "priority": "OPTIONAL",
    },
    {
        "name": "ext_46_qa",
        "path": "tests/fixtures/shamela_extended/ext_46/book.htm",
        "is_multi_layer": False,
        "priority": "OPTIONAL",
    },
]

OUT_ROOT = Path(__file__).resolve().parent / "packages"


def count_leaf_divisions(nodes: list[Any]) -> int:
    """Count leaf divisions (nodes with no children) in the division tree."""
    count = 0
    for node in nodes:
        if not node.children:
            count += 1
        else:
            count += count_leaf_divisions(node.children)
    return count


def arabic_word_count(text: str) -> int:
    """Count words containing at least one Arabic character."""
    return len([w for w in text.split() if any("\u0600" <= c <= "\u06FF" for c in w)])


def collect_leaf_word_counts(
    nodes: list[Any], content_units: list[Any]
) -> list[int]:
    """Collect Arabic word counts for each leaf division."""
    cu_by_index: dict[int, Any] = {cu.unit_index: cu for cu in content_units}
    word_counts: list[int] = []

    def walk(node_list: list[Any]) -> None:
        for node in node_list:
            if not node.children:
                # Leaf — assemble text from start_unit_index to end_unit_index
                parts: list[str] = []
                for idx in range(node.start_unit_index, node.end_unit_index + 1):
                    cu = cu_by_index.get(idx)
                    if cu:
                        parts.append(cu.primary_text)
                text = " ".join(parts)
                wc = arabic_word_count(text)
                if wc > 0:
                    word_counts.append(wc)
            else:
                walk(node.children)

    walk(nodes)
    return word_counts


def main() -> None:
    print(f"{'Fixture':<20} {'CUs':>6} {'Leaf Divs':>10} {'Median Words':>13}")
    print("-" * 55)

    for fixture in FIXTURES:
        htm_path = PROJECT_ROOT / fixture["path"]
        if not htm_path.exists():
            msg = f"ERROR: {htm_path} not found"
            if fixture["priority"] == "PRIMARY":
                raise FileNotFoundError(msg)
            print(f"{fixture['name']:<20} SKIPPED — file not found")
            continue

        try:
            meta = _make_source_metadata(is_multi_layer=fixture["is_multi_layer"])
            pkg = normalize_source(htm_path, meta)
        except Exception as e:
            if fixture["priority"] == "PRIMARY":
                print(f"\nFATAL: PRIMARY fixture {fixture['name']} failed normalization:")
                traceback.print_exc()
                sys.exit(1)
            else:
                print(f"{fixture['name']:<20} SKIPPED — normalization error: {e}")
                continue

        leaf_count = count_leaf_divisions(pkg.manifest.division_tree)

        # Check OPTIONAL fixture leaf count threshold
        if fixture["priority"] == "OPTIONAL" and leaf_count < 5:
            print(
                f"{fixture['name']:<20} SKIPPED — only {leaf_count} leaf divisions (<5)"
            )
            continue

        # Write package to disk
        out_dir = OUT_ROOT / fixture["name"]
        out_dir.mkdir(parents=True, exist_ok=True)

        with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
            f.write(pkg.manifest.model_dump_json(indent=2))

        with open(out_dir / "content.jsonl", "w", encoding="utf-8") as f:
            for cu in pkg.content_units:
                f.write(cu.model_dump_json())
                f.write("\n")

        # Compute median division word count
        leaf_wcs = collect_leaf_word_counts(
            pkg.manifest.division_tree, pkg.content_units
        )
        median_wc = int(statistics.median(leaf_wcs)) if leaf_wcs else 0

        print(
            f"{fixture['name']:<20} {len(pkg.content_units):>6} "
            f"{leaf_count:>10} {median_wc:>13}"
        )

    print(f"\nPackages written to: {OUT_ROOT}")


if __name__ == "__main__":
    main()
