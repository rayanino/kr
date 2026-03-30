"""Step 3: Topic frequency analysis across all identified nahw books.

Normalizes headings, strips structural prefixes, clusters similar topics,
and ranks by how many books contain each topic.

Output: reference/research/codex_nahw_topic_frequency.json
"""
from __future__ import annotations

import json
import logging
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.codex_nahw_research._common import (
    OUTPUT_DIR,
    normalize_arabic,
    strip_heading_prefix,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# Generic headings (no topic content)
# ──────────────────────────────────────────────────────────────────

GENERIC_HEADINGS = {
    "فصل", "الفصل", "باب", "الباب", "مسالة", "المسالة",
    "مبحث", "المبحث", "مدخل", "المدخل", "مقدمة", "خاتمة",
    "تنبيه", "تنبيهات", "فايدة", "فوايد", "قاعدة", "قواعد",
    "تتمة", "فرع", "الفرع", "مطلب", "المطلب",
    "شرح", "الشرح", "تفسير", "اعراب",
    "هذا باب", "هذا فصل",
}

# Ordinals to strip
ORDINALS = [
    "الاول", "الثاني", "الثالث", "الرابع", "الخامس",
    "السادس", "السابع", "الثامن", "التاسع", "العاشر",
    "الحادي عشر", "الثاني عشر", "الثالث عشر",
]

# Noise headings to skip entirely
SKIP_HEADINGS = {
    "فهرس", "المحتويات", "فهرس الموضوعات", "فهرس الكتاب",
    "بسم الله الرحمن الرحيم",
}


def is_generic(text: str) -> bool:
    """Check if a heading is generic (keyword-only, no qualifying text)."""
    norm = normalize_arabic(text)
    # Strip brackets
    norm = re.sub(r"[\[\](){}]", "", norm).strip()
    # Strip ordinals
    for ordi in ORDINALS:
        norm = norm.replace(ordi, "").strip()
    # Strip colons and في/فى
    norm = norm.strip(": ").strip()
    if norm in GENERIC_HEADINGS:
        return True
    # Also generic if just an ordinal with a prefix
    if re.match(r"^(باب|فصل|المبحث|المطلب|الفصل|الباب)\s*$", norm):
        return True
    return False


def is_skip(text: str) -> bool:
    """Check if heading should be skipped entirely (noise)."""
    norm = normalize_arabic(text)
    for skip in SKIP_HEADINGS:
        if normalize_arabic(skip) in norm:
            return True
    return False


def extract_core_topic(heading: str) -> str:
    """Extract the core topic from a heading, stripping structural prefixes."""
    if is_skip(heading) or is_generic(heading):
        return ""
    topic = strip_heading_prefix(heading)
    # Additional cleanup
    topic = normalize_arabic(topic)
    # Remove leading/trailing punctuation
    topic = topic.strip("[](){}:، .؟")
    # Skip very short topics (likely noise)
    if len(topic) < 3:
        return ""
    return topic


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    """Word-set Jaccard similarity."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cluster_topics(
    topic_map: dict[str, list[tuple[str, str]]],
) -> list[dict]:
    """Cluster similar topics using inverted word index + Jaccard similarity.

    topic_map: normalized_topic → [(book_title, raw_heading), ...]
    Returns: list of cluster dicts with canonical name, variants, book list.
    """
    # Arabic stop words to exclude from the inverted index
    STOP_WORDS = {
        "في", "فى", "من", "على", "الى", "ان", "ما", "لا", "هذا", "هذه",
        "التي", "الذي", "اذا", "اذ", "كل", "بين", "عن", "مع", "او",
        "هو", "هي", "ذلك", "تلك", "بعض", "غير", "قبل", "بعد",
        "اول", "ثاني", "ثالث", "رابع", "خامس",
        "الاول", "الثاني", "الثالث", "الرابع", "الخامس",
    }

    # Separate: cluster only multi-book topics, leave singletons as-is
    multi_topics = {t: entries for t, entries in topic_map.items()
                    if len(set(e[0] for e in entries)) >= 2}
    single_topics = {t: entries for t, entries in topic_map.items()
                     if len(set(e[0] for e in entries)) < 2}

    # Sort by frequency (most common first for canonical name selection)
    topics = sorted(multi_topics.keys(),
                    key=lambda t: len(set(e[0] for e in multi_topics[t])), reverse=True)

    logger.info("Clustering %d multi-book topics (%d singleton topics kept as-is)",
                len(topics), len(single_topics))

    # Build inverted index (skip stop words, skip words in >500 topics)
    word_index: dict[str, set[str]] = defaultdict(set)
    topic_words_cache: dict[str, set[str]] = {}
    for topic in topics:
        words = set(topic.split()) - STOP_WORDS
        topic_words_cache[topic] = words
        for w in words:
            word_index[w].add(topic)

    # Prune overly common words
    word_index = {w: ts for w, ts in word_index.items() if len(ts) < 500}

    clusters: list[dict] = []
    used: set[str] = set()

    for topic in topics:
        if topic in used:
            continue

        cluster_members = [topic]
        topic_words = topic_words_cache[topic]

        # Only check topics that share at least one non-stop word
        candidates: set[str] = set()
        for w in topic_words:
            if w in word_index:
                candidates |= word_index[w]
        candidates -= used
        candidates.discard(topic)

        for other in candidates:
            # Use full word sets (including stop words) for Jaccard
            all_a = set(topic.split())
            all_b = set(other.split())
            sim = jaccard_similarity(all_a, all_b)
            if sim >= 0.65:
                cluster_members.append(other)

        # Mark all as used
        for m in cluster_members:
            used.add(m)

        # Collect all books and raw headings
        all_entries: list[tuple[str, str]] = []
        for m in cluster_members:
            all_entries.extend(topic_map[m])

        # Unique books
        books = sorted(set(e[0] for e in all_entries))
        raw_variants = sorted(set(e[1] for e in all_entries))

        # Canonical = the most common variant (by book count)
        variant_counts: dict[str, int] = defaultdict(int)
        for m in cluster_members:
            variant_counts[m] = len(set(e[0] for e in topic_map[m]))
        canonical = max(cluster_members, key=lambda m: variant_counts[m])

        clusters.append({
            "topic": canonical,
            "count": len(books),
            "books": books,
            "variant_headings": raw_variants[:20],  # Cap variants
            "cluster_members": cluster_members,
        })

    # Add singleton topics (1 book only) unclustered
    for topic, entries in single_topics.items():
        books = sorted(set(e[0] for e in entries))
        raw_variants = sorted(set(e[1] for e in entries))
        clusters.append({
            "topic": topic,
            "count": len(books),
            "books": books,
            "variant_headings": raw_variants[:5],
            "cluster_members": [topic],
        })

    return sorted(clusters, key=lambda c: c["count"], reverse=True)


def main() -> None:
    """Run topic frequency analysis."""
    start = time.time()

    # Load Step 2 output
    headings_path = OUTPUT_DIR / "codex_nahw_headings_by_book.json"
    with open(headings_path, encoding="utf-8") as f:
        data = json.load(f)

    # Build topic → [(book, raw_heading)] map
    topic_map: dict[str, list[tuple[str, str]]] = defaultdict(list)
    generic_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total_headings = 0
    total_generic = 0
    total_skipped = 0

    for book in data["books"]:
        book_title = book["title"]
        seen_topics: set[str] = set()  # Dedup within book

        for h in book["headings"]:
            raw = h["raw"]
            total_headings += 1

            if is_skip(raw):
                total_skipped += 1
                continue

            if is_generic(raw):
                total_generic += 1
                htype = h.get("type", "غير مصنف")
                generic_counts[htype][book_title] = generic_counts[htype].get(book_title, 0) + 1
                continue

            core = extract_core_topic(raw)
            if not core:
                continue

            if core not in seen_topics:
                seen_topics.add(core)
                topic_map[core].append((book_title, raw))

    logger.info("Extracted %d unique raw topics from %d headings (%d generic, %d skipped)",
                len(topic_map), total_headings, total_generic, total_skipped)

    # Cluster similar topics
    clusters = cluster_topics(topic_map)

    elapsed = time.time() - start

    # Summary
    logger.info("═" * 60)
    logger.info("Total headings processed: %d", total_headings)
    logger.info("Generic (no topic): %d", total_generic)
    logger.info("Skipped (noise): %d", total_skipped)
    logger.info("Unique raw topics: %d", len(topic_map))
    logger.info("After clustering: %d topic clusters", len(clusters))
    logger.info("Elapsed: %.1fs", elapsed)
    logger.info("═" * 60)

    # Top 30 topics
    logger.info("Top 30 topics by book count:")
    for c in clusters[:30]:
        logger.info("  %3d books: %s", c["count"], c["topic"][:60])

    # Generic heading stats
    generic_summary = {}
    for htype, book_counts in generic_counts.items():
        generic_summary[htype] = {
            "total_count": sum(book_counts.values()),
            "book_count": len(book_counts),
        }

    # Write output
    out_path = OUTPUT_DIR / "codex_nahw_topic_frequency.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_books": data["total_books"],
            "total_headings": total_headings,
            "generic_headings": total_generic,
            "skipped_headings": total_skipped,
            "unique_raw_topics": len(topic_map),
            "cluster_count": len(clusters),
            "topics": clusters,
            "generic_heading_stats": generic_summary,
        }, f, ensure_ascii=False, indent=2)

    logger.info("Output written to %s", out_path)


if __name__ == "__main__":
    main()
