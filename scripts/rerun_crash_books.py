#!/usr/bin/env python3
"""Copy a subset of books from a collection for targeted re-runs.

Copies book directories (or single files) from a collection to a subset
directory, based on a list of book names. Used for re-running previously
crashed books after bug fixes.

Uses shutil.copytree (not symlinks) because symlinks need admin on Windows.

Usage:
    python scripts/rerun_crash_books.py CRASH_LIST.txt COLLECTION_DIR OUTPUT_DIR

Example:
    python scripts/rerun_crash_books.py results/normalization_sweep/crash_books.txt shamela-export-samples results/normalization_sweep/rerun_subset
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} CRASH_LIST.txt COLLECTION_DIR OUTPUT_DIR")
        sys.exit(1)

    crash_file = Path(sys.argv[1])
    base = Path(sys.argv[2])
    out = Path(sys.argv[3])

    if not crash_file.exists():
        print(f"ERROR: Crash list not found: {crash_file}")
        sys.exit(1)
    if not base.exists():
        print(f"ERROR: Collection directory not found: {base}")
        sys.exit(1)

    raw_text = crash_file.read_text(encoding="utf-8").strip()
    if not raw_text:
        print("Crash list is empty — nothing to copy.")
        return

    books = raw_text.split("\n")
    out.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0
    not_found = 0

    for b in books:
        b = b.strip()
        if not b:
            continue
        src = base / b
        dst = out / b
        if not src.exists():
            not_found += 1
            print(f"  NOT FOUND: {b}")
            continue
        if dst.exists():
            skipped += 1
            continue
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied += 1

    total = copied + skipped + not_found
    print(f"Copied {copied}/{total} crash books to {out}")
    if skipped:
        print(f"  Skipped {skipped} (already exist)")
    if not_found:
        print(f"  Not found {not_found} (not in collection)")


if __name__ == "__main__":
    main()
