"""Step 6: Gap analysis report.

Analyzes the corpus-derived tree for completeness, identifies
orphan topics, and documents surprising findings.

Output: reference/research/codex_nahw_corpus_gaps.md
"""
from __future__ import annotations

import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.codex_nahw_research._common import OUTPUT_DIR, normalize_arabic

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_tree_topics(tree_path: Path) -> set[str]:
    """Extract all leaf topic titles from the YAML tree (simple parse)."""
    topics: set[str] = set()
    text = tree_path.read_text(encoding="utf-8")
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("title:"):
            title = stripped[6:].strip().strip('"')
            topics.add(normalize_arabic(title))
    return topics


def main() -> None:
    """Generate gap analysis report."""
    start = time.time()

    # Load all data
    with open(OUTPUT_DIR / "codex_nahw_topic_frequency.json", encoding="utf-8") as f:
        freq_data = json.load(f)
    with open(OUTPUT_DIR / "codex_nahw_hierarchy_patterns.json", encoding="utf-8") as f:
        hier_data = json.load(f)
    with open(OUTPUT_DIR / "codex_nahw_books_identified.json", encoding="utf-8") as f:
        _books_data = json.load(f)

    tree_topics = load_tree_topics(OUTPUT_DIR / "codex_nahw_corpus_tree.yaml")

    topics = freq_data["topics"]
    total_books = freq_data["total_books"]

    # ─── Analysis 1: Topics not in the tree ─────────────────────
    significant_not_in_tree = []
    for t in topics:
        if t["count"] >= 5:
            norm = normalize_arabic(t["topic"])
            if norm not in tree_topics:
                significant_not_in_tree.append(t)

    # ─── Analysis 2: Specialized topics (1-2 books) ─────────────
    rare_topics = [t for t in topics if 1 <= t["count"] <= 2 and len(t["topic"]) >= 5]

    # ─── Analysis 3: Heading depth stats ─────────────────────────
    depth_stats = hier_data["depth_stats"]
    per_book = hier_data["per_book_summaries"]
    depth_distribution: dict[int, int] = defaultdict(int)
    for b in per_book:
        depth_distribution[b["max_depth"]] += 1

    # ─── Analysis 4: Tree leaf count vs unique topics ────────────
    unique_topics_5plus = len([t for t in topics if t["count"] >= 5])
    unique_topics_10plus = len([t for t in topics if t["count"] >= 10])
    tree_leaf_count = len(tree_topics)

    # ─── Analysis 5: Surprising findings ─────────────────────────
    # Topics with unexpectedly high frequency
    high_freq = [t for t in topics if t["count"] >= 20]

    # Generic heading proportion
    generic_pct = freq_data["generic_headings"] / freq_data["total_headings"] * 100

    # Books with zero headings
    zero_heading_books = [b for b in per_book if b["total_headings"] == 0]

    # ─── Analysis 6: Distribution of heading types across corpus ──
    type_totals: dict[str, int] = defaultdict(int)
    for b in per_book:
        for htype, count in b.get("heading_types", {}).items():
            type_totals[htype] += count

    elapsed = time.time() - start

    # ──────────────────────────────────────────────────────────────
    # Generate Markdown report
    # ──────────────────────────────────────────────────────────────

    lines: list[str] = []
    lines.append("# Nahw Corpus Gap Analysis")
    lines.append("")
    lines.append(f"**Date:** 2026-03-30")
    lines.append(f"**Books analyzed:** {total_books}")
    lines.append(f"**Total headings:** {freq_data['total_headings']}")
    lines.append(f"**Unique topics (>= 5 books):** {unique_topics_5plus}")
    lines.append(f"**Unique topics (>= 10 books):** {unique_topics_10plus}")
    lines.append(f"**Tree leaves:** {tree_leaf_count}")
    lines.append("")

    # Section 1: Topics not in the tree
    lines.append("## 1. Topics Not Captured by the Tree")
    lines.append("")
    lines.append(f"**{len(significant_not_in_tree)} topics** appear in >= 5 books but are not")
    lines.append("represented as explicit nodes in the proposed tree:")
    lines.append("")
    lines.append("| Topic | Books | Notes |")
    lines.append("|-------|-------|-------|")
    for t in sorted(significant_not_in_tree, key=lambda x: -x["count"])[:50]:
        lines.append(f"| {t['topic']} | {t['count']} | {', '.join(t['books'][:3])} |")
    lines.append("")

    # Section 2: Specialized topics
    lines.append("## 2. Specialized Topics (1-2 Books)")
    lines.append("")
    lines.append(f"**{len(rare_topics)} topics** appear in only 1-2 books. These represent")
    lines.append("specialized content not shared across the nahw canon.")
    lines.append("")
    lines.append("Sample of rare topics:")
    lines.append("")
    for t in rare_topics[:30]:
        books_str = ", ".join(t["books"][:2])
        lines.append(f"- **{t['topic']}** ({t['count']} book{'s' if t['count'] > 1 else ''}): {books_str}")
    lines.append("")
    lines.append(f"*(showing 30 of {len(rare_topics)} rare topics)*")
    lines.append("")

    # Section 3: Heading depth
    lines.append("## 3. Heading Depth Distribution")
    lines.append("")
    lines.append(f"- **Minimum depth:** {depth_stats['min']}")
    lines.append(f"- **Maximum depth:** {depth_stats['max']}")
    lines.append(f"- **Median depth:** {depth_stats['median']}")
    lines.append("")
    lines.append("| Max Depth | Book Count | Percentage |")
    lines.append("|-----------|------------|------------|")
    for depth in sorted(depth_distribution.keys()):
        count = depth_distribution[depth]
        pct = count / len(per_book) * 100
        lines.append(f"| {depth} | {count} | {pct:.1f}% |")
    lines.append("")
    lines.append("Most books use 2-3 levels of heading depth (باب → فصل → مسألة).")
    lines.append("")

    # Section 4: Coverage gap
    lines.append("## 4. Unique Topics vs. Tree Leaves")
    lines.append("")
    lines.append(f"- **Unique topics (>= 5 books):** {unique_topics_5plus}")
    lines.append(f"- **Unique topics (>= 10 books):** {unique_topics_10plus}")
    lines.append(f"- **Tree nodes (all levels):** {tree_leaf_count}")
    lines.append(f"- **Coverage ratio (>= 5):** {tree_leaf_count / unique_topics_5plus * 100:.1f}%")
    lines.append("")
    lines.append("The tree captures a fraction of the topic space. Many topics in the long tail")
    lines.append("are verse-specific (إعراب سورة X), book-specific, or variant formulations")
    lines.append("of the same underlying topic.")
    lines.append("")

    # Section 5: Surprising findings
    lines.append("## 5. Surprising Findings")
    lines.append("")

    lines.append("### 5.1 High-frequency topics")
    lines.append("")
    lines.append(f"**{len(high_freq)} topics** appear in 20+ books:")
    lines.append("")
    for t in sorted(high_freq, key=lambda x: -x["count"])[:20]:
        lines.append(f"- **{t['topic']}** — {t['count']} books")
    lines.append("")

    lines.append("### 5.2 Generic heading proportion")
    lines.append("")
    lines.append(f"**{generic_pct:.1f}%** of all headings are generic (bare فصل, باب, etc.)")
    lines.append("without qualifying topic text. This means most heading-based topic extraction")
    lines.append("works well — the majority of headings carry meaningful topic information.")
    lines.append("")

    lines.append("### 5.3 Heading type distribution")
    lines.append("")
    lines.append("| Heading Type | Count | Percentage |")
    lines.append("|-------------|-------|------------|")
    total = sum(type_totals.values())
    for htype, count in sorted(type_totals.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        lines.append(f"| {htype} | {count} | {pct:.1f}% |")
    lines.append("")

    lines.append("### 5.4 Books with zero headings")
    lines.append("")
    if zero_heading_books:
        lines.append(f"**{len(zero_heading_books)} books** have no extractable headings:")
        lines.append("")
        for b in zero_heading_books[:20]:
            lines.append(f"- {b['title']}")
        lines.append("")
        lines.append("These are typically short risalahs, poems, or works with no structural")
        lines.append("divisions (content flows as continuous prose).")
    else:
        lines.append("All books have at least one heading.")
    lines.append("")

    lines.append("### 5.5 Sarf (morphology) topics in nahw books")
    lines.append("")
    lines.append("Several topics traditionally classified under sarf (صرف) appear")
    lines.append("frequently in nahw books, confirming the historical overlap:")
    lines.append("")
    sarf_topics = ["التصغير", "النسب", "جمع التكسير", "الابدال", "الاعلال",
                   "الامالة", "الوقف"]
    for st in sarf_topics:
        norm = normalize_arabic(st)
        found = [t for t in topics if normalize_arabic(t["topic"]) == norm]
        if found:
            lines.append(f"- **{st}** — {found[0]['count']} books")
    lines.append("")
    lines.append("This suggests the nahw/sarf boundary is porous in practice — many")
    lines.append("'grammar' books include morphological topics as integral chapters.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated by scripts/codex_nahw_research/step6_gap_analysis.py*")
    lines.append("")

    # Write report
    out_path = OUTPUT_DIR / "codex_nahw_corpus_gaps.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")

    logger.info("═" * 60)
    logger.info("Gap analysis report written to %s", out_path)
    logger.info("Elapsed: %.1fs", elapsed)
    logger.info("═" * 60)


if __name__ == "__main__":
    main()
