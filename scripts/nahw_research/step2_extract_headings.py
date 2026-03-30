"""Step 2: Extract heading structures from identified nahw books.

For each nahw book, parse all HTML files to extract:
- Content headings (<span class="title"> with double quotes)
- Heading type classification
- Position within the book

Output: reference/research/nahw_headings_by_book.json
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.nahw_research._common import (
    OUTPUT_DIR,
    extract_headings_from_file,
    extract_title_fast,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Extract headings from all identified nahw books."""
    start = time.time()

    # Load Step 1 output
    books_path = OUTPUT_DIR / "nahw_books_identified.json"
    with open(books_path, encoding="utf-8") as f:
        data = json.load(f)

    results: list[dict] = []
    total_headings = 0
    empty_count = 0

    for i, book in enumerate(data["books"]):
        first_file = Path(book["first_file"])
        title = book["title"]
        is_multi = book["is_multivolume"]

        # Collect all files for this book
        if is_multi:
            book_dir = first_file.parent
            all_files = sorted(book_dir.glob("*.htm"))
        else:
            all_files = [first_file]

        all_headings: list[dict] = []
        for vol_idx, htm_file in enumerate(all_files, 1):
            headings = extract_headings_from_file(htm_file, volume=vol_idx)
            for h in headings:
                all_headings.append({
                    "raw": h.raw,
                    "full": h.full,
                    "type": h.heading_type,
                    "position": h.position,
                    "volume": h.volume,
                    "file": h.file_name,
                })

        total_headings += len(all_headings)
        if not all_headings:
            empty_count += 1

        results.append({
            "title": title,
            "name": book["name"],
            "category": book["category"],
            "match_tier": book["match_tier"],
            "total_headings": len(all_headings),
            "volume_count": len(all_files),
            "headings": all_headings,
        })

        if (i + 1) % 50 == 0:
            logger.info("  Processed %d/%d books...", i + 1, len(data["books"]))

    elapsed = time.time() - start

    # Summary stats
    heading_counts = [r["total_headings"] for r in results]
    non_empty = [c for c in heading_counts if c > 0]

    logger.info("═" * 60)
    logger.info("Books processed: %d", len(results))
    logger.info("Total headings extracted: %d", total_headings)
    logger.info("Books with 0 headings: %d", empty_count)
    if non_empty:
        logger.info("Headings per book: min=%d, max=%d, median=%d, mean=%.1f",
                     min(non_empty), max(non_empty),
                     sorted(non_empty)[len(non_empty) // 2],
                     sum(non_empty) / len(non_empty))
    logger.info("Elapsed: %.1fs", elapsed)
    logger.info("═" * 60)

    # Top 10 books by heading count
    top10 = sorted(results, key=lambda r: r["total_headings"], reverse=True)[:10]
    logger.info("Top 10 books by heading count:")
    for r in top10:
        logger.info("  %4d headings: %s", r["total_headings"], r["title"][:60])

    # Write output
    out_path = OUTPUT_DIR / "nahw_headings_by_book.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_books": len(results),
            "total_headings": total_headings,
            "books_with_zero_headings": empty_count,
            "books": results,
        }, f, ensure_ascii=False, indent=2)

    logger.info("Output written to %s", out_path)


if __name__ == "__main__":
    main()
