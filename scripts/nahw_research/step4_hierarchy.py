"""Step 4: Discover natural hierarchy patterns in nahw books.

Analyzes how books nest topics under other topics using positional
analysis and heading-type depth levels.

Output: reference/research/nahw_hierarchy_patterns.json
"""
from __future__ import annotations

import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.nahw_research._common import (
    HEADING_DEPTH,
    HeadingType,
    OUTPUT_DIR,
    classify_heading,
    normalize_arabic,
    strip_heading_prefix,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Skip noise headings
SKIP_TOPICS = {
    "فهرس", "المحتويات", "فهرس الموضوعات", "فهرس الكتاب",
    "بسم الله الرحمن الرحيم",
}


def is_noise(text: str) -> bool:
    """Check if heading is noise."""
    norm = normalize_arabic(text)
    return any(normalize_arabic(s) in norm for s in SKIP_TOPICS)


def infer_hierarchy(headings: list[dict]) -> list[dict]:
    """Infer parent-child relationships from a book's heading sequence.

    Returns list of {heading, depth, parent_heading, children} dicts.
    """
    nodes: list[dict] = []
    # Stack: [(depth, heading_text, node_index)]
    stack: list[tuple[int, str, int]] = []

    for h in headings:
        raw = h["raw"]
        if is_noise(raw):
            continue

        htype = classify_heading(raw)
        depth = HEADING_DEPTH.get(htype, -1)

        # For unclassified headings, assign to same depth as previous
        if depth == -1 and stack:
            depth = stack[-1][0]
        elif depth == -1:
            depth = 2  # Default to BAB level

        # Pop stack until we find a parent (lower depth number)
        while stack and stack[-1][0] >= depth:
            stack.pop()

        parent_text = stack[-1][1] if stack else ""
        parent_idx = stack[-1][2] if stack else -1

        node = {
            "heading": raw,
            "type": htype.value if isinstance(htype, HeadingType) else htype,
            "depth": depth,
            "parent_heading": parent_text,
            "parent_idx": parent_idx,
            "topic": strip_heading_prefix(raw),
        }
        idx = len(nodes)
        nodes.append(node)
        stack.append((depth, raw, idx))

    return nodes


def main() -> None:
    """Discover hierarchy patterns across all nahw books."""
    start = time.time()

    # Load Step 2 output
    headings_path = OUTPUT_DIR / "nahw_headings_by_book.json"
    with open(headings_path, encoding="utf-8") as f:
        data = json.load(f)

    # Track parent-child relationships
    parent_child_freq: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # Track topic depth distribution
    topic_depth: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    # Track hierarchy patterns per book (serialized paths)
    pattern_counts: dict[str, list[str]] = defaultdict(list)
    # Track max depth per book
    book_depths: list[int] = []
    # Track per-book hierarchy summaries
    per_book: list[dict] = []

    for book in data["books"]:
        if book["total_headings"] == 0:
            continue

        nodes = infer_hierarchy(book["headings"])
        if not nodes:
            book_depths.append(0)
            continue

        max_depth = max(n["depth"] for n in nodes)
        book_depths.append(max_depth)

        # Extract parent-child pairs
        for node in nodes:
            parent_topic = normalize_arabic(strip_heading_prefix(node["parent_heading"])) if node["parent_heading"] else ""
            child_topic = normalize_arabic(node["topic"])

            if parent_topic and child_topic and len(child_topic) >= 3:
                parent_type = classify_heading(node["parent_heading"]).value
                child_type = node["type"]
                # Track type-to-type relationships
                parent_child_freq[parent_type][child_type] += 1

            # Track topic depth
            if child_topic and len(child_topic) >= 3:
                topic_depth[child_topic][node["depth"]] += 1

        # Track hierarchy pattern for this book
        depth_types = [n["type"] for n in nodes if n["depth"] >= 1]
        if depth_types:
            # Extract the unique depth sequence
            unique_levels = []
            for t in depth_types:
                if not unique_levels or unique_levels[-1] != t:
                    unique_levels.append(t)
            pattern = " > ".join(unique_levels[:5])
            pattern_counts[pattern].append(book["title"])

        # Per-book summary
        type_counts: dict[str, int] = defaultdict(int)
        for n in nodes:
            type_counts[n["type"]] += 1

        per_book.append({
            "title": book["title"],
            "total_headings": book["total_headings"],
            "max_depth": max_depth,
            "heading_types": dict(type_counts),
            "hierarchy_levels": max_depth + 1,
        })

    elapsed = time.time() - start

    # Compute topic typical depths
    topic_typical_depth: dict[str, dict] = {}
    for topic, depths in sorted(topic_depth.items(),
                                 key=lambda x: sum(x[1].values()), reverse=True)[:200]:
        total = sum(depths.values())
        if total < 2:
            continue
        most_common_depth = max(depths, key=depths.get)
        topic_typical_depth[topic] = {
            "typical_depth": most_common_depth,
            "depth_distribution": dict(depths),
            "total_occurrences": total,
        }

    # Top hierarchy patterns
    sorted_patterns = sorted(pattern_counts.items(),
                              key=lambda x: len(x[1]), reverse=True)

    logger.info("═" * 60)
    logger.info("Books analyzed: %d", len(per_book))
    if book_depths:
        logger.info("Max heading depth: min=%d, max=%d, median=%d",
                     min(book_depths), max(book_depths),
                     sorted(book_depths)[len(book_depths) // 2])
    logger.info("Unique hierarchy patterns: %d", len(sorted_patterns))
    logger.info("Elapsed: %.1fs", elapsed)
    logger.info("═" * 60)

    # Top 15 patterns
    logger.info("Top 15 hierarchy patterns:")
    for pattern, books in sorted_patterns[:15]:
        logger.info("  %3d books: %s", len(books), pattern[:60])

    # Parent-child type frequencies
    logger.info("\nParent type → child type frequencies:")
    for parent_type in sorted(parent_child_freq.keys()):
        children = parent_child_freq[parent_type]
        top_children = sorted(children.items(), key=lambda x: -x[1])[:5]
        if top_children:
            child_str = ", ".join(f"{c}({n})" for c, n in top_children)
            logger.info("  %s → %s", parent_type, child_str)

    # Write output
    out_path = OUTPUT_DIR / "nahw_hierarchy_patterns.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_books_analyzed": len(per_book),
            "depth_stats": {
                "min": min(book_depths) if book_depths else 0,
                "max": max(book_depths) if book_depths else 0,
                "median": sorted(book_depths)[len(book_depths) // 2] if book_depths else 0,
            },
            "hierarchy_patterns": [
                {
                    "pattern": pattern,
                    "book_count": len(books),
                    "example_books": books[:10],
                }
                for pattern, books in sorted_patterns[:50]
            ],
            "parent_child_frequency": {
                parent: dict(sorted(children.items(), key=lambda x: -x[1]))
                for parent, children in sorted(parent_child_freq.items())
            },
            "topic_depth_distribution": topic_typical_depth,
            "per_book_summaries": per_book,
        }, f, ensure_ascii=False, indent=2)

    logger.info("Output written to %s", out_path)


if __name__ == "__main__":
    main()
