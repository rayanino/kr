"""Stress-test Shamela extractors against a full collection.

Runs detect_format() → extract_shamela_metadata() on every book in a
Shamela export collection, collects statistics, and writes a structured
audit report.

Usage:
    python scripts/stress_test_collection.py <collection_dir>
    python scripts/stress_test_collection.py C:/Users/Rayane/Desktop/kr_shamela_collection

Output:
    tests/fixtures/shamela_collection_audit_fresh.json
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

# ── Add project root to path ──
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.source.contracts import SourceFormat
from engines.source.src.exceptions import SourceEngineError
from engines.source.src.extractors import extract_metadata
from engines.source.src.extractors.shamela_html import (
    FIELD_MAP,
    MUHAQIQ_KEYWORDS,
)
from engines.source.src.format_detection import detect_format


def discover_books(collection_dir: Path) -> list[Path]:
    """Find all books (single .htm files and multi-volume directories).

    The Shamela export structure is:
      collection_dir/
        تصدير من الشاملة/        ← top-level wrapper dir
          book1.htm               ← single-file book
          book2_dir/              ← multi-volume book
            1.htm
            2.htm
            المقدمة.htm
    """
    # Find the actual content root (may be wrapped in a parent dir)
    content_root = collection_dir
    children = [c for c in collection_dir.iterdir() if not c.name.startswith(".")]
    if len(children) == 1 and children[0].is_dir():
        content_root = children[0]

    books: list[Path] = []
    for entry in sorted(content_root.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_file() and entry.suffix.lower() in (".htm", ".html"):
            books.append(entry)
        elif entry.is_dir():
            # Multi-volume book directory
            htm_files = [
                f
                for f in entry.iterdir()
                if f.suffix.lower() in (".htm", ".html")
            ]
            if htm_files:
                books.append(entry)
    return books


def run_extraction(book_path: Path) -> dict[str, Any]:
    """Run format detection + metadata extraction on a single book.

    Returns:
        Dict with keys: path, success, result|error, elapsed_ms
    """
    t0 = time.perf_counter()
    try:
        fmt = detect_format(book_path)
        result = extract_metadata(book_path, fmt)
        elapsed = (time.perf_counter() - t0) * 1000
        return {
            "path": str(book_path.name),
            "success": True,
            "format": fmt.value,
            "result": result,
            "elapsed_ms": round(elapsed, 1),
        }
    except SourceEngineError as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return {
            "path": str(book_path.name),
            "success": False,
            "error_code": e.error.error_code.value,
            "error_message": str(e),
            "elapsed_ms": round(elapsed, 1),
        }
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return {
            "path": str(book_path.name),
            "success": False,
            "error_code": "UNEXPECTED",
            "error_message": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
            "elapsed_ms": round(elapsed, 1),
        }


def compute_audit(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute the collection audit from extraction results."""
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    # ── Field frequencies ──
    field_freq: Counter[str] = Counter()
    for r in successes:
        res = r["result"]
        # Check which FIELD_MAP source labels were encountered
        for key in res:
            if key.startswith("_field_source_"):
                label = res[key]
                field_freq[label] += 1
        # Also count extra card fields
        if "_extra_card_fields" in res:
            for label in res["_extra_card_fields"]:
                field_freq[label] += 1
        # Count fields parsed by non-_RE_FIELD paths (category comes from _RE_CATEGORY)
        if "shamela_category" in res:
            field_freq["القسم"] += 1

    # ── FIELD_MAP hit rate ──
    total_field_hits = sum(field_freq.values())
    fieldmap_hits = sum(
        count for label, count in field_freq.items() if label in FIELD_MAP
    )
    muhaqiq_keyword_hits = 0
    extra_hits = 0
    for label, count in field_freq.items():
        if label in FIELD_MAP:
            continue
        if label.startswith("_"):
            continue
        if any(kw in label for kw in MUHAQIQ_KEYWORDS):
            muhaqiq_keyword_hits += count
        else:
            extra_hits += count

    # ── Category distribution ──
    category_freq: Counter[str] = Counter()
    for r in successes:
        cat = r["result"].get("shamela_category")
        if cat:
            category_freq[cat] += 1

    # ── Muhaqiq label distribution ──
    muhaqiq_labels: Counter[str] = Counter()
    for r in successes:
        res = r["result"]
        source_label = res.get("_field_source_muhaqiq_name_raw")
        if source_label:
            muhaqiq_labels[source_label] += 1

    # ── Death date extraction rate ──
    has_author = sum(1 for r in successes if "author_name_raw" in r["result"])
    has_death_date = sum(
        1 for r in successes if "author_death_hijri" in r["result"]
    )

    # ── Edition parsing success ──
    has_edition_raw = sum(1 for r in successes if "edition_raw" in r["result"])
    has_edition_number = sum(
        1 for r in successes if r["result"].get("edition_number") is not None
    )
    has_edition_year = sum(
        1
        for r in successes
        if "edition_year_hijri" in r["result"]
        or "edition_year_miladi" in r["result"]
    )

    # ── Quality inspection distribution ──
    quality_check_freq: Counter[str] = Counter()
    books_with_quality_issues = 0
    for r in successes:
        issues = r["result"].get("_quality_issues", [])
        if issues:
            books_with_quality_issues += 1
        for issue in issues:
            quality_check_freq[issue["check"]] += 1

    # ── Multi-volume stats ──
    multi_volume = sum(1 for r in successes if r["result"].get("is_multi_volume"))
    single_volume = sum(
        1 for r in successes if not r["result"].get("is_multi_volume")
    )
    has_muqaddima = sum(1 for r in successes if r["result"].get("has_muqaddima"))

    # ── New unmapped fields (≥5 occurrences) ──
    extra_field_freq: Counter[str] = Counter()
    for r in successes:
        extra = r["result"].get("_extra_card_fields", {})
        for label in extra:
            extra_field_freq[label] += 1
    new_unmapped_fields = {
        label: count
        for label, count in extra_field_freq.most_common()
        if count >= 5
    }

    # ── Page count stats ──
    page_counts = [
        r["result"]["body_page_count"]
        for r in successes
        if "body_page_count" in r["result"]
    ]
    total_pages = sum(page_counts) if page_counts else 0

    # ── Page mismatches ──
    page_mismatches: list[dict[str, Any]] = []
    for r in successes:
        res = r["result"]
        issues = res.get("_quality_issues", [])
        for issue in issues:
            if issue["check"] == "page_count_mismatch":
                page_mismatches.append(
                    {
                        "file": r["path"],
                        "digital": res.get("body_page_count"),
                        "physical": res.get("_physical_page_count"),
                        "detail": issue["detail"],
                    }
                )

    # ── Tiny books (< 3 pages) ──
    tiny_books: list[dict[str, Any]] = []
    for r in successes:
        res = r["result"]
        if res.get("body_page_count", 999) < 3:
            tiny_books.append(
                {
                    "file": r["path"],
                    "pages": res.get("body_page_count"),
                }
            )

    # ── Failure details ──
    failure_details: list[dict[str, str]] = []
    error_code_freq: Counter[str] = Counter()
    for f in failures:
        failure_details.append(
            {
                "file": f["path"],
                "error_code": f["error_code"],
                "error_message": f["error_message"],
            }
        )
        error_code_freq[f["error_code"]] += 1

    # ── Timing stats ──
    elapsed_values = [r["elapsed_ms"] for r in results]
    elapsed_values.sort()

    n = len(successes)

    audit: dict[str, Any] = {
        "summary": {
            "total_books": len(results),
            "successes": n,
            "failures": len(failures),
            "success_rate_pct": round(n / len(results) * 100, 1) if results else 0,
            "single_volume": single_volume,
            "multi_volume": multi_volume,
            "has_muqaddima": has_muqaddima,
            "total_pages": total_pages,
        },
        "field_frequencies": {
            label: {
                "count": count,
                "pct": round(count / n * 100, 1) if n else 0,
            }
            for label, count in field_freq.most_common()
        },
        "field_map_coverage": {
            "total_field_hits": total_field_hits,
            "fieldmap_hits": fieldmap_hits,
            "muhaqiq_keyword_hits": muhaqiq_keyword_hits,
            "extra_unmapped_hits": extra_hits,
            "fieldmap_hit_rate_pct": (
                round(fieldmap_hits / total_field_hits * 100, 1)
                if total_field_hits
                else 0
            ),
        },
        "category_distribution": dict(category_freq.most_common()),
        "muhaqiq_labels": dict(muhaqiq_labels.most_common()),
        "death_date_stats": {
            "books_with_author": has_author,
            "books_with_death_date": has_death_date,
            "extraction_rate_pct": (
                round(has_death_date / has_author * 100, 1) if has_author else 0
            ),
        },
        "edition_stats": {
            "books_with_edition_raw": has_edition_raw,
            "books_with_edition_number": has_edition_number,
            "edition_number_rate_pct": (
                round(has_edition_number / has_edition_raw * 100, 1)
                if has_edition_raw
                else 0
            ),
            "books_with_edition_year": has_edition_year,
            "edition_year_rate_pct": (
                round(has_edition_year / has_edition_raw * 100, 1)
                if has_edition_raw
                else 0
            ),
        },
        "quality_inspection": {
            "books_with_issues": books_with_quality_issues,
            "issue_rate_pct": (
                round(books_with_quality_issues / n * 100, 1) if n else 0
            ),
            "check_frequencies": dict(quality_check_freq.most_common()),
        },
        "new_unmapped_fields": new_unmapped_fields,
        "page_stats": {
            "total_pages": total_pages,
            "min": min(page_counts) if page_counts else 0,
            "max": max(page_counts) if page_counts else 0,
            "median": (
                sorted(page_counts)[len(page_counts) // 2] if page_counts else 0
            ),
            "page_mismatches": len(page_mismatches),
        },
        "tiny_books_count": len(tiny_books),
        "timing": {
            "total_seconds": round(sum(elapsed_values) / 1000, 1),
            "min_ms": round(min(elapsed_values), 1) if elapsed_values else 0,
            "max_ms": round(max(elapsed_values), 1) if elapsed_values else 0,
            "median_ms": (
                round(
                    elapsed_values[len(elapsed_values) // 2], 1
                )
                if elapsed_values
                else 0
            ),
            "p95_ms": (
                round(
                    elapsed_values[int(len(elapsed_values) * 0.95)], 1
                )
                if elapsed_values
                else 0
            ),
        },
        "failures": failure_details if failure_details else [],
        "error_code_distribution": dict(error_code_freq.most_common()),
        "page_mismatches_sample": page_mismatches[:30],
        "tiny_books_sample": tiny_books[:20],
    }

    return audit


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/stress_test_collection.py <collection_dir>")
        sys.exit(1)

    collection_dir = Path(sys.argv[1])
    if not collection_dir.exists():
        print(f"ERROR: Directory not found: {collection_dir}")
        sys.exit(1)

    output_path = PROJECT_ROOT / "tests" / "fixtures" / "shamela_collection_audit_fresh.json"

    print(f"Collection: {collection_dir}")
    print("Discovering books...")
    books = discover_books(collection_dir)
    print(f"Found {len(books)} books")

    results: list[dict[str, Any]] = []
    t_start = time.perf_counter()

    for i, book_path in enumerate(books):
        result = run_extraction(book_path)
        results.append(result)

        # Progress every 100 books
        if (i + 1) % 100 == 0 or (i + 1) == len(books):
            elapsed = time.perf_counter() - t_start
            failures = sum(1 for r in results if not r["success"])
            rate = (i + 1) / elapsed
            print(
                f"  [{i + 1}/{len(books)}] "
                f"{failures} failures, "
                f"{rate:.0f} books/sec, "
                f"{elapsed:.1f}s elapsed"
            )

    total_time = time.perf_counter() - t_start
    print(f"\nExtraction complete: {total_time:.1f}s total")

    # Compute audit
    print("Computing audit...")
    audit = compute_audit(results)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
    print(f"Audit written to: {output_path}")

    # Print summary
    s = audit["summary"]
    print(f"\n{'='*60}")
    print(f"COLLECTION STRESS TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total books:     {s['total_books']}")
    print(f"Successes:       {s['successes']} ({s['success_rate_pct']}%)")
    print(f"Failures:        {s['failures']}")
    print(f"Single-volume:   {s['single_volume']}")
    print(f"Multi-volume:    {s['multi_volume']}")
    print(f"Has muqaddima:   {s['has_muqaddima']}")
    print(f"Total pages:     {s['total_pages']}")

    fmc = audit["field_map_coverage"]
    print(f"\nFIELD_MAP coverage: {fmc['fieldmap_hit_rate_pct']}%")
    print(f"  FIELD_MAP hits:     {fmc['fieldmap_hits']}")
    print(f"  Muhaqiq keyword:    {fmc['muhaqiq_keyword_hits']}")
    print(f"  Unmapped (extra):   {fmc['extra_unmapped_hits']}")

    dd = audit["death_date_stats"]
    print(f"\nDeath date extraction: {dd['extraction_rate_pct']}%")
    print(f"  Authors found: {dd['books_with_author']}, death dates: {dd['books_with_death_date']}")

    ed = audit["edition_stats"]
    print(f"\nEdition parsing: number={ed['edition_number_rate_pct']}%, year={ed['edition_year_rate_pct']}%")

    qi = audit["quality_inspection"]
    print(f"\nQuality issues: {qi['books_with_issues']} books ({qi['issue_rate_pct']}%)")
    for check, count in qi["check_frequencies"].items():
        print(f"  {check}: {count}")

    if audit["new_unmapped_fields"]:
        print(f"\nNEW UNMAPPED FIELDS (>=5 occurrences):")
        for label, count in audit["new_unmapped_fields"].items():
            print(f"  {label}: {count}")

    if audit["failures"]:
        print(f"\nFAILURE DETAILS:")
        for f in audit["failures"][:20]:
            print(f"  [{f['error_code']}] {f['file']}: {f['error_message']}")

    t = audit["timing"]
    print(f"\nTiming: {t['total_seconds']}s total, median={t['median_ms']}ms, p95={t['p95_ms']}ms")

    # ── Step 5: Compare against old audit ──
    old_audit_path = PROJECT_ROOT / "tests" / "fixtures" / "shamela_collection_audit.json"
    if old_audit_path.exists():
        print(f"\n{'='*60}")
        print("COMPARISON WITH OLD AUDIT")
        print(f"{'='*60}")
        with open(old_audit_path, encoding="utf-8") as f:
            old = json.load(f)
        old_total = old["summary"]["total"]
        print(f"Old collection: {old_total} books")
        print(f"New collection: {s['total_books']} books")

        # Compare key field frequencies (as %)
        old_ff = old.get("field_freq", {})
        print("\nField frequency comparison (old% → new%):")
        key_fields = ["الكتاب", "المؤلف", "الناشر", "الطبعة", "عدد الصفحات", "المحقق"]
        for field in key_fields:
            old_count = old_ff.get(field, 0)
            old_pct = round(old_count / old_total * 100, 1) if old_total else 0
            new_entry = audit["field_frequencies"].get(field, {})
            new_pct = new_entry.get("pct", 0)
            new_count = new_entry.get("count", 0)
            delta = round(new_pct - old_pct, 1)
            sign = "+" if delta > 0 else ""
            print(f"  {field}: {old_pct}% ({old_count}) → {new_pct}% ({new_count}) [{sign}{delta}pp]")

        # New unmapped fields not in old audit
        old_new_fields = set(old.get("new_fields_above_5", {}).keys())
        fresh_new_fields = set(audit["new_unmapped_fields"].keys())
        truly_new = fresh_new_fields - old_new_fields
        if truly_new:
            print(f"\nTRULY NEW unmapped fields (not in old audit):")
            for label in truly_new:
                print(f"  {label}: {audit['new_unmapped_fields'][label]}")
        else:
            print("\nNo truly new unmapped fields vs old audit.")

        # Compare muhaqiq labels
        old_muhaqiq = set(old.get("muhaqiq_labels", {}).keys())
        new_muhaqiq = set(audit["muhaqiq_labels"].keys())
        new_muhaqiq_labels = new_muhaqiq - old_muhaqiq
        if new_muhaqiq_labels:
            print(f"\nNew muhaqiq labels not in old audit:")
            for label in new_muhaqiq_labels:
                print(f"  {label}: {audit['muhaqiq_labels'][label]}")


if __name__ == "__main__":
    main()
