"""Phase D Book Selection — Category distribution + stratified random sample.

Reads Phase A extraction results (no LLM calls), builds category distribution,
then selects ~130 books via stratified sampling for Step 4 pipeline validation.
"""
from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

PHASE_A_DIR = Path("tests/results/source_engine/phase_a")
PHASE_C_MANIFEST = Path("tests/results/source_engine/phase_c/PHASE_C_MANIFEST.json")
OUTPUT_DISTRIBUTION = Path("tests/results/source_engine/PHASE_D_CATEGORY_DISTRIBUTION.json")
OUTPUT_SELECTION_MD = Path("tests/results/source_engine/PHASE_D_SELECTION.md")
OUTPUT_BOOKLIST = Path("scripts/phases/data/phase_d_books.txt")

TARGET_BOOKS = 130
MIN_BOOKS = 120
MAX_BOOKS = 140
MIN_MUHAQIQ = 5
MIN_NO_AUTHOR = 5
SEED = 42

SKIP_FILES = {"PHASE_A_SUMMARY.json", "PHASE_A_LESSONS.md"}
UNCATEGORIZED = "بدون تصنيف"


def load_phase_a() -> dict[str, dict]:
    """Load all Phase A results. Returns {book_name: {category, muhaqiq, author, source_name}}."""
    books: dict[str, dict] = {}
    errors: list[dict] = []

    files = sorted(PHASE_A_DIR.glob("*.json"))
    total = 0
    for f in files:
        if f.name in SKIP_FILES:
            continue
        total += 1
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            em = data.get("extracted_metadata", {})
            source_name = data.get("source_name", f.stem)
            book_name = source_name.removesuffix(".htm")

            books[book_name] = {
                "source_name": source_name,
                "shamela_category": em.get("shamela_category") or "",
                "muhaqiq_name_raw": em.get("muhaqiq_name_raw") or "",
                "author_name_raw": em.get("author_name_raw") or "",
                "title_full": em.get("title_full") or "",
            }
        except Exception as e:
            errors.append({"file": f.name, "error": str(e)})

    print(f"Loaded {len(books)} books from {total} Phase A results ({len(errors)} errors)")
    return books


def load_phase_c_exclusions() -> set[str]:
    """Load Phase C manifest keys as exclusion set."""
    if not PHASE_C_MANIFEST.exists():
        print("WARNING: Phase C manifest not found, no exclusions applied")
        return set()
    data = json.loads(PHASE_C_MANIFEST.read_text(encoding="utf-8"))
    keys = set(data.get("books", {}).keys())
    print(f"Phase C exclusions: {len(keys)} books")
    return keys


def build_distribution(
    books: dict[str, dict], phase_c: set[str]
) -> tuple[dict[str, list[str]], list[str], list[str], list[str]]:
    """Build category distribution and special lists.

    Returns (categories, muhaqiq_books, no_author_books, phase_c_in_collection).
    """
    categories: dict[str, list[str]] = {}
    muhaqiq_books: list[str] = []
    no_author_books: list[str] = []
    phase_c_in_collection: list[str] = []

    for name, info in books.items():
        cat = info["shamela_category"].strip() or UNCATEGORIZED
        categories.setdefault(cat, []).append(name)

        if info["muhaqiq_name_raw"].strip():
            muhaqiq_books.append(name)
        if not info["author_name_raw"].strip():
            no_author_books.append(name)
        if name in phase_c:
            phase_c_in_collection.append(name)

    return categories, muhaqiq_books, no_author_books, phase_c_in_collection


def stratified_select(
    categories: dict[str, list[str]],
    phase_c: set[str],
    muhaqiq_books: list[str],
    no_author_books: list[str],
) -> list[str]:
    """Stratified random selection of ~130 books."""
    random.seed(SEED)

    # Build per-category pools (exclude Phase C)
    pools: dict[str, list[str]] = {}
    total_available = 0
    for cat, cat_books in categories.items():
        pool = sorted(set(cat_books) - phase_c)
        if pool:
            pools[cat] = pool
            total_available += len(pool)

    print(f"Total available (excl Phase C): {total_available}")

    # Proportional allocation
    allocations: dict[str, int] = {}
    for cat, pool in pools.items():
        alloc = max(1, round(len(pool) / total_available * TARGET_BOOKS))
        if len(pool) >= 10:
            alloc = max(3, alloc)
        allocations[cat] = min(alloc, len(pool))

    # Select
    selected: list[str] = []
    per_category: dict[str, list[str]] = {}
    for cat in sorted(pools.keys()):
        pool = pools[cat]
        n = allocations[cat]
        picked = random.sample(pool, n)
        per_category[cat] = picked
        selected.extend(picked)

    print(f"Initial selection: {len(selected)} books from {len(pools)} categories")

    # Ensure minimum muhaqiq books
    selected_set = set(selected)
    muhaqiq_in_sel = [b for b in selected if b in set(muhaqiq_books)]
    if len(muhaqiq_in_sel) < MIN_MUHAQIQ:
        needed = MIN_MUHAQIQ - len(muhaqiq_in_sel)
        candidates = [b for b in muhaqiq_books if b not in selected_set and b not in phase_c]
        random.shuffle(candidates)
        # Swap: for each needed muhaqiq, replace a non-muhaqiq from its category
        muhaqiq_set = set(muhaqiq_books)
        swapped = 0
        for candidate in candidates:
            if swapped >= needed:
                break
            # Find candidate's category
            for cat, cat_books in categories.items():
                if candidate in cat_books and cat in per_category:
                    # Find a non-muhaqiq in this category's selection to swap
                    non_muh = [b for b in per_category[cat] if b not in muhaqiq_set]
                    if non_muh:
                        victim = non_muh[0]
                        per_category[cat].remove(victim)
                        per_category[cat].append(candidate)
                        selected.remove(victim)
                        selected.append(candidate)
                        selected_set.discard(victim)
                        selected_set.add(candidate)
                        swapped += 1
                        break
        if swapped < needed:
            # Add remaining from largest categories
            for candidate in candidates:
                if swapped >= needed:
                    break
                if candidate not in selected_set:
                    selected.append(candidate)
                    selected_set.add(candidate)
                    swapped += 1
        print(f"  Muhaqiq swap: {swapped} books added/swapped (now {len([b for b in selected if b in set(muhaqiq_books)])} muhaqiq)")

    # Ensure minimum no-author books
    no_author_set = set(no_author_books)
    no_auth_in_sel = [b for b in selected if b in no_author_set]
    if len(no_auth_in_sel) < MIN_NO_AUTHOR:
        needed = MIN_NO_AUTHOR - len(no_auth_in_sel)
        candidates = [b for b in no_author_books if b not in selected_set and b not in phase_c]
        random.shuffle(candidates)
        swapped = 0
        for candidate in candidates:
            if swapped >= needed:
                break
            for cat, cat_books in categories.items():
                if candidate in cat_books and cat in per_category:
                    non_na = [b for b in per_category[cat] if b not in no_author_set]
                    if non_na:
                        victim = non_na[0]
                        per_category[cat].remove(victim)
                        per_category[cat].append(candidate)
                        selected.remove(victim)
                        selected.append(candidate)
                        selected_set.discard(victim)
                        selected_set.add(candidate)
                        swapped += 1
                        break
        if swapped < needed:
            for candidate in candidates:
                if swapped >= needed:
                    break
                if candidate not in selected_set:
                    selected.append(candidate)
                    selected_set.add(candidate)
                    swapped += 1
        print(f"  No-author swap: {swapped} books added/swapped (now {len([b for b in selected if b in no_author_set])} no-author)")

    # Trim if too many
    if len(selected) > MAX_BOOKS:
        # Remove from largest categories first
        by_size = sorted(per_category.items(), key=lambda x: len(x[1]), reverse=True)
        while len(selected) > MAX_BOOKS:
            for cat, picks in by_size:
                if len(picks) > 1 and len(selected) > MAX_BOOKS:
                    victim = picks.pop()
                    selected.remove(victim)

    # Add if too few
    if len(selected) < MIN_BOOKS:
        by_size = sorted(pools.items(), key=lambda x: len(x[1]), reverse=True)
        for cat, pool in by_size:
            if len(selected) >= MIN_BOOKS:
                break
            remaining = [b for b in pool if b not in selected_set]
            for b in remaining:
                if len(selected) >= MIN_BOOKS:
                    break
                selected.append(b)
                selected_set.add(b)

    return sorted(set(selected)), per_category


def print_distribution(
    categories: dict[str, list[str]],
    total: int,
    muhaqiq_count: int,
    no_author_count: int,
    error_count: int,
) -> None:
    """Print category distribution table."""
    print(f"\n{'Category':<45} | {'Count':>5} | {'%':>6}")
    print("─" * 45 + "─│─" + "─" * 5 + "─│─" + "─" * 6)
    for cat, books in sorted(categories.items(), key=lambda x: -len(x[1])):
        pct = len(books) / total * 100
        print(f"{cat:<45} | {len(books):>5} | {pct:>5.1f}%")
    print()
    print(f"Total books: {total}")
    print(f"Categories: {len(categories)}")
    print(f"With muhaqiq: {muhaqiq_count}")
    print(f"Without author: {no_author_count}")
    print(f"Extraction errors: {error_count}")


def save_distribution(
    categories: dict[str, list[str]],
    books: dict[str, dict],
    muhaqiq_books: list[str],
    no_author_books: list[str],
    phase_c_in_coll: list[str],
    errors: list[dict],
) -> None:
    """Save PHASE_D_CATEGORY_DISTRIBUTION.json."""
    cat_data = {}
    for cat, cat_books in sorted(categories.items(), key=lambda x: -len(x[1])):
        cat_data[cat] = {"count": len(cat_books), "books": sorted(cat_books)}

    no_cat = sorted(categories.get(UNCATEGORIZED, []))

    output = {
        "total_books": len(books),
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        "categories": cat_data,
        "books_without_category": no_cat,
        "books_with_muhaqiq": sorted(muhaqiq_books),
        "books_without_author": sorted(no_author_books),
        "phase_c_books": sorted(phase_c_in_coll),
        "extraction_errors": errors,
    }
    OUTPUT_DISTRIBUTION.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DISTRIBUTION.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nSaved: {OUTPUT_DISTRIBUTION}")


def save_selection_md(
    selected: list[str],
    per_category: dict[str, list[str]],
    categories: dict[str, list[str]],
    phase_c: set[str],
    muhaqiq_books: list[str],
    no_author_books: list[str],
) -> None:
    """Save PHASE_D_SELECTION.md."""
    muhaqiq_set = set(muhaqiq_books)
    no_author_set = set(no_author_books)
    selected_set = set(selected)

    sel_muhaqiq = sorted(b for b in selected if b in muhaqiq_set)
    sel_no_auth = sorted(b for b in selected if b in no_author_set)

    lines = [
        "# Phase D Book Selection\n",
        "## Summary",
        f"- Target: {TARGET_BOOKS} books",
        f"- Selected: {len(selected)}",
        f"- Phase C reruns (separate): {len(phase_c)}",
        f"- Total Step 4 pipeline: {len(selected) + len(phase_c)}",
        f"- Muhaqiq books in selection: {len(sel_muhaqiq)}",
        f"- No-author books in selection: {len(sel_no_auth)}",
        f"- Seed: {SEED}",
        "",
        "## Category Breakdown\n",
        "| Category | In collection | Available (excl Phase C) | Selected | Rate |",
        "|----------|--------------|------------------------|----------|------|",
    ]

    for cat in sorted(categories.keys(), key=lambda c: -len(categories[c])):
        total_in_cat = len(categories[cat])
        available = len(set(categories[cat]) - phase_c)
        sel_count = len(per_category.get(cat, []))
        rate = f"{sel_count / available * 100:.1f}%" if available > 0 else "—"
        lines.append(f"| {cat} | {total_in_cat} | {available} | {sel_count} | {rate} |")

    lines.extend([
        "",
        f"## Muhaqiq Books ({len(sel_muhaqiq)} tahqiq editions)\n",
    ])
    for b in sel_muhaqiq:
        lines.append(f"- {b}")

    lines.extend([
        "",
        f"## No-Author Books ({len(sel_no_auth)} — pure LLM inference)\n",
    ])
    for b in sel_no_auth:
        lines.append(f"- {b}")

    lines.extend([
        "",
        f"## Full Selection ({len(selected)} books, alphabetical)\n",
    ])
    for b in selected:
        lines.append(f"- {b}")

    lines.append("")
    OUTPUT_SELECTION_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SELECTION_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {OUTPUT_SELECTION_MD}")


def save_booklist(selected: list[str]) -> None:
    """Save phase_d_books.txt."""
    OUTPUT_BOOKLIST.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_BOOKLIST.write_text("\n".join(selected) + "\n", encoding="utf-8")
    print(f"Saved: {OUTPUT_BOOKLIST} ({len(selected)} books)")


def main() -> None:
    books = load_phase_a()
    phase_c = load_phase_c_exclusions()

    categories, muhaqiq_books, no_author_books, phase_c_in_coll = build_distribution(
        books, phase_c
    )

    print_distribution(categories, len(books), len(muhaqiq_books), len(no_author_books), 0)

    selected, per_category = stratified_select(
        categories, phase_c, muhaqiq_books, no_author_books
    )

    print(f"\nFinal selection: {len(selected)} books")

    save_distribution(
        categories, books, muhaqiq_books, no_author_books, phase_c_in_coll, []
    )
    save_selection_md(
        selected, per_category, categories, phase_c, muhaqiq_books, no_author_books
    )
    save_booklist(selected)

    # Print summary table
    muhaqiq_set = set(muhaqiq_books)
    no_author_set = set(no_author_books)
    sel_muh = len([b for b in selected if b in muhaqiq_set])
    sel_na = len([b for b in selected if b in no_author_set])
    print(f"\n{'='*60}")
    print(f"SELECTION COMPLETE")
    print(f"  Books selected: {len(selected)}")
    print(f"  Phase C reruns: {len(phase_c)}")
    print(f"  Total Step 4:   {len(selected) + len(phase_c)}")
    print(f"  With muhaqiq:   {sel_muh}")
    print(f"  Without author: {sel_na}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
