#!/usr/bin/env python3
"""Phase E Book Selection Script.

Selects ~70 books across 6 strategic categories for LLM edge-case probes.
Outputs PHASE_E_SELECTION.md and books.txt.

Fixes from v1:
- Builds category mapping from source sweep JSONs (32 categories) instead of
  PHASE_D_CATEGORY_DISTRIBUTION.json (only 10 categories)
- Uses correct normalization sweep field names: 'name' not 'book_name',
  'diacritic_count' not 'diacritics_count'
- Uses correct zero-content book names (Arabic ordinals on disk)
"""
from __future__ import annotations

import json
import os
import random
from collections import defaultdict
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
MANIFEST_PATH = Path("tests/results/source_engine/MASTER_MANIFEST.json")
NORM_SWEEP_PATH = Path("results/normalization_sweep_v2/corpus_sweep.jsonl")
SOURCE_SWEEP_DIR = Path("results/source_sweep")
OUTPUT_DIR = Path("tests/results/source_engine/phase_e")
SAMPLES_DIR = Path("shamela-export-samples")

# ── Zero-content books (actual filenames from disk) ────────────────────
# Uses Arabic ordinals matching the actual file naming convention.
ZERO_CONTENT_KHALIYAT: list[str] = [
    "الأول من الخلعيات",
    "الثاني من الخلعيات",
    "الثالث من الخلعيات",
    "الرابع من الخلعيات",
    "الخامس من الخلعيات",
    "السادس من الخلعيات",
    "السابع من الخلعيات",
    "الثامن من الخلعيات",
    "التاسع من الخلعيات",
    "العاشر من الخلعيات",
    "الحادي عشر من الخلعيات",
    "الثاني عشر من الخلعيات",
    "الثالث عشر من الخلعيات",
    "الرابع عشر من الخلعيات",
    "الخامس عشر من الخلعيات",
    "السادس عشر من الخلعيات",
    "السابع عشر من الخلعيات",
    "الثامن عشر من الخلعيات",
    "التاسع عشر من الخلعيات",
    "العشرون من الخلعيات",
]

ZERO_CONTENT_MUJAM: list[str] = [
    "الأول من معجم شيوخ الدمياطي",
    "الثاني من معجم شيوخ الدمياطي",
    "الثالث من معجم شيوخ الدمياطي",
    "الرابع من معجم شيوخ الدمياطي",
    "الخامس من معجم شيوخ الدمياطي",
    "السادس من معجم شيوخ الدمياطي",
    "السابع من معجم شيوخ الدمياطي",
    "الثامن من معجم شيوخ الدمياطي",
]

ZERO_CONTENT_MISBAH: list[str] = [
    "الثاني من المصباح في عيون الصحاح",
    "العاشر من المصباح في عيون الصحاح",
]

ZERO_CONTENT_INDIVIDUAL: list[str] = [
    "حديث ذي النون المصري",
    "مسند أبي حنيفة رواية الحصكفي",
    "فوائد ابن دحيم",
    "حديث عباس الترقفي",
    "أحاديث عوالي",
    "أخبار الشيوخ وأخلاقهم",
]


def resolve_book_path(book_name: str) -> Path | None:
    """Check if a book exists in shamela-export-samples."""
    p = SAMPLES_DIR / book_name
    if p.is_dir():
        return p
    htm = SAMPLES_DIR / (book_name + ".htm")
    if htm.is_file():
        return htm
    if p.is_file():
        return p
    return None


def load_existing_books() -> set[str]:
    """Load 204 Phase D book names from MASTER_MANIFEST."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return set(manifest["books"].keys())


def build_category_mapping() -> dict[str, list[str]]:
    """Build Shamela category → book names from source sweep per-book JSONs.

    This gives 32 categories vs the 10 in PHASE_D_CATEGORY_DISTRIBUTION.json.
    """
    cat_map: dict[str, list[str]] = defaultdict(list)
    sweep_files = [f for f in os.listdir(SOURCE_SWEEP_DIR)
                   if f.endswith(".json") and f != "PHASE_A_SUMMARY.json"]

    for sf in sweep_files:
        try:
            data = json.loads((SOURCE_SWEEP_DIR / sf).read_text(encoding="utf-8"))
            book_name = data.get("source_name", "")
            meta = data.get("extracted_metadata", {})
            cat = meta.get("shamela_category", "")
            if cat and book_name:
                cat_map[cat].append(book_name)
        except Exception:
            pass

    return dict(cat_map)


def load_norm_sweep() -> list[dict]:
    """Load normalization sweep v2 JSONL — one dict per book."""
    entries: list[dict] = []
    with open(NORM_SWEEP_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def load_source_sweep_metadata(book_name: str) -> dict | None:
    """Load a book's source sweep JSON to get extracted_metadata."""
    for suffix in [".json", ".htm.json"]:
        p = SOURCE_SWEEP_DIR / (book_name + suffix)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("extracted_metadata", {})
    return None


def main() -> None:
    existing = load_existing_books()
    print(f"Existing Phase D books: {len(existing)}")

    # Build category mapping from source sweep (32 categories)
    print("Building category mapping from source sweep JSONs...")
    cat_map = build_category_mapping()
    print(f"Shamela categories found: {len(cat_map)}")

    # ── Compute Phase D coverage per category ──────────────────────────
    phase_d_per_cat: dict[str, int] = {}
    for cat_name, books in cat_map.items():
        pd_books = [b for b in books if b in existing]
        phase_d_per_cat[cat_name] = len(pd_books)

    print("\nPhase D coverage per category:")
    for cat, count in sorted(phase_d_per_cat.items(), key=lambda x: x[1]):
        total = len(cat_map[cat])
        print(f"  {cat}: {count}/{total} Phase D books")

    # ── Category 1: Genre diversity gaps (20-25 books) ─────────────────
    print("\n=== Category 1: Genre Diversity Gaps ===")
    cat1_selected: list[tuple[str, str, str]] = []

    # Find ALL thin categories (≤2 Phase D books)
    thin_cats = {cat: count for cat, count in phase_d_per_cat.items() if count <= 2}
    print(f"Thin categories (≤2 Phase D books): {len(thin_cats)}")

    for cat_name in sorted(thin_cats.keys()):
        pd_count = thin_cats[cat_name]
        available = [b for b in cat_map[cat_name]
                     if b not in existing and resolve_book_path(b) is not None]
        if not available:
            print(f"  {cat_name}: {pd_count} PD books, 0 available — SKIP")
            continue

        # Pick enough to reach 3 total (Phase D + new picks)
        need = 3 - pd_count
        need = max(need, 1)
        need = min(need, len(available))

        # Pick from start, middle, end for diversity
        picks: list[str] = []
        if need >= 1:
            picks.append(available[0])
        if need >= 2 and len(available) > 1:
            picks.append(available[len(available) // 2])
        if need >= 3 and len(available) > 2:
            picks.append(available[-1])

        for book in picks:
            rationale = f"Fills thin category '{cat_name}' ({pd_count} PD books → needs ≥3)"
            cat1_selected.append((book, cat_name, rationale))

        print(f"  {cat_name}: {pd_count} PD, picked {len(picks)}/{len(available)} avail")

    # Cap at 25
    if len(cat1_selected) > 25:
        cat1_selected = cat1_selected[:25]

    print(f"Category 1 total: {len(cat1_selected)} books")
    all_selected = {b[0] for b in cat1_selected}

    # ── Category 2: Multi-layer candidates (15 books) ──────────────────
    print("\n=== Category 2: Multi-Layer Candidates ===")
    norm_data = load_norm_sweep()
    print(f"Normalization sweep entries: {len(norm_data)}")

    # Filter multi-layer books — field is 'name' not 'book_name'
    multi_layer: list[tuple[str, int, int, float]] = []
    for entry in norm_data:
        name = entry.get("name", "")
        if name in existing or name in all_selected:
            continue
        ml_units = entry.get("multi_layer_units", 0)
        total_units = entry.get("content_units", 0)
        if ml_units > 0 and total_units > 0:
            ratio = ml_units / total_units
            multi_layer.append((name, ml_units, total_units, ratio))

    multi_layer.sort(key=lambda x: x[3])
    print(f"Multi-layer candidates (excl Phase D): {len(multi_layer)}")

    # Bucket by ratio
    low = [m for m in multi_layer if 0.10 <= m[3] <= 0.40]
    medium = [m for m in multi_layer if 0.50 <= m[3] <= 0.75]
    high = [m for m in multi_layer if m[3] >= 0.85]
    print(f"  Low (10-40%): {len(low)}, Medium (50-75%): {len(medium)}, High (85%+): {len(high)}")

    cat2_selected: list[tuple[str, str, str]] = []

    def pick_ml(bucket: list[tuple[str, int, int, float]], count: int, label: str) -> None:
        avail = [b for b in bucket
                 if b[0] not in all_selected and resolve_book_path(b[0]) is not None]
        if not avail:
            print(f"  {label}: 0 available on disk")
            return
        step = max(1, len(avail) // count)
        picked = 0
        for i in range(0, len(avail), step):
            if picked >= count:
                break
            name, ml, total, ratio = avail[i]
            rationale = f"Multi-layer {label} ratio: {ratio:.1%} ({ml}/{total} units)"
            cat2_selected.append((name, "multi-layer", rationale))
            all_selected.add(name)
            picked += 1

    pick_ml(low, 5, "low")
    pick_ml(medium, 5, "medium")
    pick_ml(high, 5, "high")

    print(f"Category 2 total: {len(cat2_selected)} books")

    # ── Category 3: Source extraction anomalies (10 books) ─────────────
    print("\n=== Category 3: Source Extraction Anomalies ===")
    cat3_selected: list[tuple[str, str, str]] = []

    sweep_files = [f for f in os.listdir(SOURCE_SWEEP_DIR)
                   if f.endswith(".json") and f != "PHASE_A_SUMMARY.json"]

    anomalies: list[tuple[str, str]] = []
    for sf in sweep_files:
        try:
            data = json.loads((SOURCE_SWEEP_DIR / sf).read_text(encoding="utf-8"))
            book_name = data.get("source_name", "")
            if not book_name or book_name in existing or book_name in all_selected:
                continue

            meta = data.get("extracted_metadata", {})
            if not meta.get("author_name_raw"):
                anomalies.append((book_name, "missing_author_name_raw"))
            elif not meta.get("publisher") and not meta.get("edition_raw"):
                anomalies.append((book_name, "missing_publisher_and_edition"))
        except Exception:
            pass

    missing_author = [a for a in anomalies if a[1] == "missing_author_name_raw"]
    missing_pub = [a for a in anomalies if a[1] != "missing_author_name_raw"]
    print(f"Anomalies found: {len(missing_author)} missing author, {len(missing_pub)} missing pub+edition")

    picked_3 = 0
    for book_name, anomaly in missing_author:
        if picked_3 >= 7:
            break
        if resolve_book_path(book_name) is not None and book_name not in all_selected:
            rationale = f"Sparse metadata: {anomaly} — tests LLM inference from limited extraction"
            cat3_selected.append((book_name, "anomaly", rationale))
            all_selected.add(book_name)
            picked_3 += 1

    for book_name, anomaly in missing_pub:
        if picked_3 >= 10:
            break
        if resolve_book_path(book_name) is not None and book_name not in all_selected:
            rationale = f"Sparse metadata: {anomaly} — tests LLM inference from limited extraction"
            cat3_selected.append((book_name, "anomaly", rationale))
            all_selected.add(book_name)
            picked_3 += 1

    print(f"Category 3 total: {len(cat3_selected)} books")

    # ── Category 4: Extreme metrics (8 books) ──────────────────────────
    print("\n=== Category 4: Extreme Metrics ===")
    cat4_selected: list[tuple[str, str, str]] = []

    # Use correct field name: 'name' and 'diacritic_count'
    valid_entries = [
        (e.get("name", ""), e.get("content_units", 0),
         e.get("diacritic_count", 0), e.get("total_chars", 0))
        for e in norm_data
        if e.get("name", "") not in existing
        and e.get("name", "") not in all_selected
        and e.get("content_units", 0) > 0
    ]
    print(f"Valid entries for extreme metrics: {len(valid_entries)}")

    # 3 largest
    by_size_desc = sorted(valid_entries, key=lambda x: x[1], reverse=True)
    large_picked = 0
    for name, units, diac, chars in by_size_desc:
        if large_picked >= 3:
            break
        if resolve_book_path(name) is not None and name not in all_selected:
            cat4_selected.append((name, "extreme", f"Largest book: {units:,} content units — tests pipeline at scale"))
            all_selected.add(name)
            large_picked += 1

    # 3 smallest non-trivial (3-10 content units)
    by_size_asc = sorted(valid_entries, key=lambda x: x[1])
    small_picked = 0
    for name, units, diac, chars in by_size_asc:
        if small_picked >= 3:
            break
        if 3 <= units <= 10 and resolve_book_path(name) is not None and name not in all_selected:
            cat4_selected.append((name, "extreme", f"Smallest non-trivial: {units} content units — tests minimal input"))
            all_selected.add(name)
            small_picked += 1

    # 2 highest diacritic density
    density_entries = [
        (name, units, diac, chars, diac / chars)
        for name, units, diac, chars in valid_entries
        if chars > 0 and name not in all_selected
    ]
    by_density = sorted(density_entries, key=lambda x: x[4], reverse=True)
    diac_picked = 0
    for name, units, diac, chars, density in by_density:
        if diac_picked >= 2:
            break
        if resolve_book_path(name) is not None and name not in all_selected:
            cat4_selected.append((name, "extreme", f"Highest diacritic density: {density:.1%} ({diac:,}/{chars:,}) — tests diacritic handling"))
            all_selected.add(name)
            diac_picked += 1

    print(f"Category 4 total: {len(cat4_selected)} books (3 large, {small_picked} small, {diac_picked} diacritics)")

    # ── Category 5: Formerly zero-content (8 books) ───────────────────
    print("\n=== Category 5: Formerly Zero-Content ===")
    cat5_selected: list[tuple[str, str, str]] = []

    # Diverse picks: 2 الخلعيات, 1 معجم شيوخ, 1 المصباح, 4 individual
    zc_picks: list[tuple[str, str]] = [
        (ZERO_CONTENT_KHALIYAT[0], "الخلعيات vol 1 (الأول)"),
        (ZERO_CONTENT_KHALIYAT[14], "الخلعيات vol 15 (الخامس عشر)"),
        (ZERO_CONTENT_MUJAM[3], "معجم شيوخ الدمياطي vol 4"),
        (ZERO_CONTENT_MISBAH[0], "المصباح في عيون الصحاح vol 2"),
    ]
    for book in ZERO_CONTENT_INDIVIDUAL[:4]:
        zc_picks.append((book, "Individual hadith compilation"))

    for book_name, desc in zc_picks:
        if book_name not in existing and book_name not in all_selected:
            if resolve_book_path(book_name) is not None:
                rationale = f"Formerly zero-content ({desc}) — fixed in Task 2, verify LLM inference works"
                cat5_selected.append((book_name, "zero-content", rationale))
                all_selected.add(book_name)
            else:
                print(f"  WARNING: not found on disk: '{book_name}'")

    print(f"Category 5 total: {len(cat5_selected)} books")

    # ── Category 6: Previously unknown (5 books) ──────────────────────
    print("\n=== Category 6: Previously Unknown ===")
    cat6_selected: list[tuple[str, str, str]] = []

    all_sample_books: set[str] = set()
    for entry in os.listdir(SAMPLES_DIR):
        if entry.endswith(".htm"):
            all_sample_books.add(entry[:-4])
        elif os.path.isdir(SAMPLES_DIR / entry):
            all_sample_books.add(entry)

    unknown = sorted(all_sample_books - existing - all_selected)
    print(f"Unknown candidates: {len(unknown)}")

    random.seed(42)
    if len(unknown) > 5:
        step = len(unknown) // 5
        picks_6 = [unknown[i * step] for i in range(5)]
    else:
        picks_6 = unknown[:5]

    for book_name in picks_6:
        if book_name not in all_selected:
            meta = load_source_sweep_metadata(book_name)
            sham_cat = meta.get("shamela_category", "unknown") if meta else "unknown"
            rationale = f"Previously unknown — max novelty. Shamela category: {sham_cat}"
            cat6_selected.append((book_name, "unknown", rationale))
            all_selected.add(book_name)

    print(f"Category 6 total: {len(cat6_selected)} books")

    # ── Combine and output ─────────────────────────────────────────────
    all_categories = [
        ("Genre Diversity Gaps", cat1_selected),
        ("Multi-Layer Candidates", cat2_selected),
        ("Source Extraction Anomalies", cat3_selected),
        ("Extreme Metrics", cat4_selected),
        ("Formerly Zero-Content", cat5_selected),
        ("Previously Unknown", cat6_selected),
    ]

    total = sum(len(items) for _, items in all_categories)
    print(f"\n{'='*60}")
    print(f"TOTAL SELECTED: {total} books")
    for name, items in all_categories:
        print(f"  {name}: {len(items)}")

    # ── Verify all selected books exist on disk ────────────────────────
    missing_disk = []
    for _, items in all_categories:
        for book_name, _, _ in items:
            if resolve_book_path(book_name) is None:
                missing_disk.append(book_name)
    if missing_disk:
        print(f"\nERROR: {len(missing_disk)} books not found on disk:")
        for b in missing_disk:
            print(f"  '{b}'")
        return

    # ── Write books.txt ────────────────────────────────────────────────
    books_txt = OUTPUT_DIR / "books.txt"
    lines: list[str] = []
    for _, items in all_categories:
        for book_name, _, _ in items:
            lines.append(book_name)

    # Deduplicate (shouldn't happen but safety check)
    seen: set[str] = set()
    deduped: list[str] = []
    for line in lines:
        if line not in seen:
            deduped.append(line)
            seen.add(line)
    if len(deduped) != len(lines):
        print(f"WARNING: Removed {len(lines) - len(deduped)} duplicates")
    lines = deduped

    books_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {len(lines)} books to {books_txt}")

    # ── Write PHASE_E_SELECTION.md ─────────────────────────────────────
    md_lines: list[str] = [
        "# Phase E Book Selection",
        "",
        f"**Total books selected:** {total}",
        f"**Date:** 2026-03-21",
        f"**Selection criteria:** 6 strategic categories targeting Phase D blind spots",
        f"**Excluded:** {len(existing)} Phase D books (from MASTER_MANIFEST.json)",
        "",
        "## Summary",
        "",
        "| Category | Count | Purpose |",
        "|----------|-------|---------|",
    ]
    purposes = {
        "Genre Diversity Gaps": "Fill Shamela categories with ≤2 Phase D books to reach ≥3 each",
        "Multi-Layer Candidates": "Test LLM is_multi_layer vs normalization auto-detection across diverse ratios",
        "Source Extraction Anomalies": "Stress-test LLM inference on books with sparse extraction metadata",
        "Extreme Metrics": "Test pipeline at scale extremes (largest, smallest, highest diacritics)",
        "Formerly Zero-Content": "Verify LLM metadata works on hadith compilations fixed in Task 2",
        "Previously Unknown": "Maximum novelty — books not in any prior results",
    }
    for cat_name, items in all_categories:
        md_lines.append(f"| {cat_name} | {len(items)} | {purposes[cat_name]} |")

    for cat_name, items in all_categories:
        md_lines.extend(["", f"## {cat_name}", ""])
        md_lines.append("| # | Book | Shamela Category | Rationale |")
        md_lines.append("|---|------|-----------------|-----------|")
        for i, (book_name, _, rationale) in enumerate(items, 1):
            meta = load_source_sweep_metadata(book_name)
            sham_cat = meta.get("shamela_category", "unknown") if meta else "unknown"
            md_lines.append(f"| {i} | {book_name} | {sham_cat} | {rationale} |")

    selection_md = OUTPUT_DIR / "PHASE_E_SELECTION.md"
    selection_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote selection rationale to {selection_md}")


if __name__ == "__main__":
    main()
