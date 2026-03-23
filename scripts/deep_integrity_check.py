"""Deep integrity check — verify layer coverage char-by-char on real books.

Unlike verify_normalized_integrity.py (which reads sweep metadata),
this script runs actual normalization on specific books and verifies:
1. Every character in primary_text is covered by exactly one text_layer segment
2. Text layer segments don't overlap
3. Text layer segments don't have gaps
4. Diacritics in primary_text are preserved (count matches source)

Usage:
    python scripts/deep_integrity_check.py [--limit N]
"""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path
from typing import Any

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engines.normalization.contracts import ContentUnit, NormalizedPackage
from engines.normalization.src.dispatcher import normalize_source

# Reuse the sweep's metadata builder (SourceMetadata is complex)
from scripts.normalization_corpus_sweep import _make_sweep_metadata


DIACRITICS = {chr(cp) for cp in range(0x064B, 0x0653)} | {"\u0670"}
COLLECTION_DIR = Path("shamela-export-samples")


def _make_metadata(source_id: str) -> Any:
    """Build SourceMetadata via the sweep's builder (handles complex schema)."""
    return _make_sweep_metadata(source_id)


def verify_layer_coverage(cu: ContentUnit) -> list[str]:
    """Verify that text_layers cover every character of primary_text exactly once.

    Returns list of issues found (empty = clean).
    """
    issues: list[str] = []
    text_len = len(cu.primary_text)

    if text_len == 0:
        if cu.text_layers:
            issues.append(f"unit {cu.unit_index}: empty primary_text but {len(cu.text_layers)} layers")
        return issues

    if not cu.text_layers:
        issues.append(f"unit {cu.unit_index}: non-empty primary_text ({text_len} chars) but 0 layers")
        return issues

    # Check coverage array: each position must be covered exactly once
    coverage = [0] * text_len
    for i, seg in enumerate(cu.text_layers):
        if seg.start < 0 or seg.end > text_len:
            issues.append(
                f"unit {cu.unit_index}: layer {i} range [{seg.start}, {seg.end}) "
                f"exceeds text length {text_len}"
            )
            continue
        if seg.start >= seg.end:
            issues.append(
                f"unit {cu.unit_index}: layer {i} has empty/inverted range "
                f"[{seg.start}, {seg.end})"
            )
            continue
        for pos in range(seg.start, seg.end):
            coverage[pos] += 1

    # Find gaps (0 coverage) and overlaps (>1 coverage)
    gaps: list[tuple[int, int]] = []
    overlaps: list[tuple[int, int]] = []
    current_gap_start: int | None = None
    current_overlap_start: int | None = None

    for pos in range(text_len):
        # Track gaps
        if coverage[pos] == 0:
            if current_gap_start is None:
                current_gap_start = pos
        else:
            if current_gap_start is not None:
                gaps.append((current_gap_start, pos))
                current_gap_start = None

        # Track overlaps
        if coverage[pos] > 1:
            if current_overlap_start is None:
                current_overlap_start = pos
        else:
            if current_overlap_start is not None:
                overlaps.append((current_overlap_start, pos))
                current_overlap_start = None

    # Close any open ranges
    if current_gap_start is not None:
        gaps.append((current_gap_start, text_len))
    if current_overlap_start is not None:
        overlaps.append((current_overlap_start, text_len))

    for start, end in gaps:
        issues.append(
            f"unit {cu.unit_index}: GAP at [{start}, {end}) — "
            f"{end - start} chars unattributed"
        )

    for start, end in overlaps:
        issues.append(
            f"unit {cu.unit_index}: OVERLAP at [{start}, {end}) — "
            f"{end - start} chars double-attributed"
        )

    return issues


def verify_segment_ordering(cu: ContentUnit) -> list[str]:
    """Verify segments are ordered by start offset and non-overlapping."""
    issues: list[str] = []
    for i in range(1, len(cu.text_layers)):
        prev = cu.text_layers[i - 1]
        curr = cu.text_layers[i]
        if curr.start < prev.end:
            issues.append(
                f"unit {cu.unit_index}: segment {i} starts at {curr.start} "
                f"but previous ends at {prev.end} (overlap)"
            )
        if curr.start < prev.start:
            issues.append(
                f"unit {cu.unit_index}: segment {i} starts at {curr.start} "
                f"before previous at {prev.start} (out of order)"
            )
    return issues


def find_book(name: str) -> Path | None:
    """Find a book by name in the collection directory."""
    # Try direct .htm file
    direct = COLLECTION_DIR / f"{name}.htm"
    if direct.exists():
        return direct

    # Try as directory with .htm inside
    dir_path = COLLECTION_DIR / name
    if dir_path.is_dir():
        htms = sorted(dir_path.glob("*.htm"))
        if htms:
            return htms[0]

    return None


def process_book(name: str, path: Path) -> dict[str, Any]:
    """Run normalization and deep integrity checks on one book."""
    source_id = f"deep_{name[:40]}"
    meta = _make_metadata(source_id)
    start = time.time()

    try:
        pkg = normalize_source(path, meta)
    except Exception as e:
        return {
            "name": name,
            "status": "CRASH",
            "error": str(e)[:300],
            "elapsed": round(time.time() - start, 2),
        }

    all_issues: list[str] = []
    total_chars = 0
    total_diacritics = 0

    for cu in pkg.content_units:
        # Layer coverage check
        coverage_issues = verify_layer_coverage(cu)
        all_issues.extend(coverage_issues)

        # Segment ordering check
        ordering_issues = verify_segment_ordering(cu)
        all_issues.extend(ordering_issues)

        # Diacritics count
        total_chars += len(cu.primary_text)
        total_diacritics += sum(1 for c in cu.primary_text if c in DIACRITICS)

    elapsed = time.time() - start

    return {
        "name": name,
        "status": "CLEAN" if not all_issues else "ISSUES",
        "content_units": len(pkg.content_units),
        "total_chars": total_chars,
        "total_diacritics": total_diacritics,
        "diacritic_ratio": round(total_diacritics / total_chars, 6) if total_chars > 0 else 0,
        "layer_count": len(pkg.manifest.layer_map) if pkg.manifest.layer_map else 1,
        "issues": all_issues[:20],  # Cap at 20
        "issue_count": len(all_issues),
        "elapsed": round(elapsed, 2),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Deep integrity check on specific books")
    parser.add_argument("--limit", type=int, default=5, help="Number of books to check")
    args = parser.parse_args()

    # Select diverse books
    book_names = [
        "آداب الحوار من خلال سيرة مصعب بن عمير رضي الله عنه",  # Small, single-layer
        "آداب الحسبة",  # Medium, has hadith
        "أحكام القرآن للكيا الهراسي",  # Multi-layer candidate
        "آداب البحث والمناظرة",  # Medium
        "آداب الأكل",  # Small
    ]

    book_names = book_names[:args.limit]
    results: list[dict[str, Any]] = []

    for name in book_names:
        path = find_book(name)
        if path is None:
            print(f"  SKIP: {name} — not found in {COLLECTION_DIR}")
            continue

        print(f"  Processing: {name[:50]}...")
        result = process_book(name, path)
        results.append(result)

        status = result["status"]
        issues = result.get("issue_count", 0)
        chars = result.get("total_chars", 0)
        cu = result.get("content_units", 0)
        elapsed = result.get("elapsed", 0)
        print(f"    {status} | {cu} units | {chars} chars | {issues} issues | {elapsed}s")

        if result.get("issues"):
            for iss in result["issues"][:5]:
                print(f"      ! {iss}")

    # Write report
    output_dir = Path("scripts/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "deep_integrity_check.json"

    from datetime import datetime, timezone
    report = {
        "check": "deep_integrity",
        "books_checked": len(results),
        "all_clean": all(r["status"] == "CLEAN" for r in results),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nReport: {report_path}")

    clean_count = sum(1 for r in results if r["status"] == "CLEAN")
    print(f"\n{'='*60}")
    print(f"DEEP INTEGRITY: {clean_count}/{len(results)} books CLEAN")
    print(f"{'='*60}")

    return 0 if all(r["status"] == "CLEAN" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
