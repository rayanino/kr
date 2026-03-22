"""Deliverable 1: Produce normalized packages for 5 test fixtures.

Runs normalize_source() on each fixture and writes manifest.json + content.jsonl
to experiments/architecture_test/packages/{fixture_name}/.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Project root for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.tests.conftest import _make_source_metadata

FIXTURES = [
    {"name": "03_fiqh", "htm": "book.htm", "is_multi_layer": False},
    {"name": "07_balagha", "htm": "book.htm", "is_multi_layer": False},
    {"name": "06_usul", "htm": "book.htm", "is_multi_layer": False},
    {"name": "02_nahw_muhaqiq", "htm": "book.htm", "is_multi_layer": True},
    {"name": "10_no_author", "htm": "book.htm", "is_multi_layer": False},
]


def count_leaf_divisions(nodes: list) -> int:
    """Count leaf divisions (nodes with no children) in the division tree."""
    count = 0
    for node in nodes:
        if not node.children:
            count += 1
        else:
            count += count_leaf_divisions(node.children)
    return count


def main() -> None:
    fixture_root = PROJECT_ROOT / "tests" / "fixtures" / "shamela_real"
    out_root = Path(__file__).resolve().parent / "packages"

    print(f"{'Fixture':<20} {'CUs':>6} {'Leaf Divs':>10}")
    print("-" * 40)

    for fixture in FIXTURES:
        htm_path = fixture_root / fixture["name"] / fixture["htm"]
        if not htm_path.exists():
            print(f"ERROR: {htm_path} not found, skipping")
            continue

        meta = _make_source_metadata(is_multi_layer=fixture["is_multi_layer"])
        pkg = normalize_source(htm_path, meta)

        # Write package to disk
        out_dir = out_root / fixture["name"]
        out_dir.mkdir(parents=True, exist_ok=True)

        with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
            f.write(pkg.manifest.model_dump_json(indent=2))

        with open(out_dir / "content.jsonl", "w", encoding="utf-8") as f:
            for cu in pkg.content_units:
                f.write(cu.model_dump_json())
                f.write("\n")

        leaf_count = count_leaf_divisions(pkg.manifest.division_tree)
        print(f"{fixture['name']:<20} {len(pkg.content_units):>6} {leaf_count:>10}")

    print(f"\nPackages written to: {out_root}")


if __name__ == "__main__":
    main()
