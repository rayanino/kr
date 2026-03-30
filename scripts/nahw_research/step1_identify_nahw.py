"""Step 1: Identify nahw books from all Shamela exports.

Three-tier classification:
  A — Category match (القسم: النحو والصرف)
  B — Title keyword match (nahw-specific terms)
  C — Known book fragment match (famous nahw works)

Output: reference/research/nahw_books_identified.json
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.nahw_research._common import (
    OUTPUT_DIR,
    discover_all_books,
    extract_category_fast,
    extract_title_fast,
    normalize_arabic,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# Tier B: title keywords
# ──────────────────────────────────────────────────────────────────

# High-confidence: these words strongly indicate a nahw book
NAHW_KEYWORDS_HIGH = [
    "النحو", "نحو",
    "الإعراب", "إعراب",
    "الألفية", "ألفية",
    "الأجرومية", "الآجرومية", "أجرومية",
    "قطر الندى", "شذور الذهب",
    "أوضح المسالك",
    "المقتضب",
    "الخصائص",
    "اللمع في العربية",
    "المفصل في صنعة الإعراب",
    "ملحة الإعراب",
    "شرح ابن عقيل",
    "شرح الأشموني",
    "شرح التصريح",
    "حاشية الصبان",
    "شرح شذور",
    "شرح قطر",
    "شرح الكافية",
    "الكناش في النحو",
    "المقرب",
    "التسهيل",
    "همع الهوامع",
    "الارتشاف",
    "مغني اللبيب",
    "شرح المفصل",
    "الأصول في النحو",
    "الإيضاح في شرح المفصل",
    "المحلى بالآثار",  # Not nahw, but test exclusion
]

# Context-dependent: only match if combined with other evidence
NAHW_KEYWORDS_CONTEXT = [
    "شرح", "حاشية", "تعليق",
]

# Nahw-adjacent: Arabic language books that likely contain nahw sections
NAHW_ADJACENT_KEYWORDS = [
    "العربية", "اللغة العربية",
]

# ──────────────────────────────────────────────────────────────────
# Tier C: known book fragments (famous nahw works)
# ──────────────────────────────────────────────────────────────────

KNOWN_NAHW_BOOKS = [
    "الكتاب لسيبويه",
    "كتاب سيبويه",
    "المقتضب للمبرد",
    "الأصول في النحو لابن السراج",
    "الخصائص لابن جني",
    "اللمع في العربية لابن جني",
    "الإنصاف في مسائل الخلاف",
    "أسرار العربية",
    "الجمل في النحو للزجاجي",
    "المفصل في صنعة الإعراب للزمخشري",
    "شرح المفصل لابن يعيش",
    "شرح الكافية الشافية",
    "أوضح المسالك",
    "شرح ابن عقيل",
    "شرح الأشموني",
    "حاشية الصبان",
    "شرح شذور الذهب",
    "شرح قطر الندى",
    "مغني اللبيب عن كتب الأعاريب",
    "شرح التسهيل",
    "همع الهوامع",
    "الارتشاف",
    "التصريح بمضمون التوضيح",
    "شرح الأجرومية",
    "شرح الآجرومية",
    "المقدمة الآجرومية",
    "الفوائد السنية في شرح الألفية",
    "المقاصد النحوية",
    "النكت الوفية",
    "إرشاد السالك",
    "التحفة السنية",
    "متممة الأجرومية",
    "قواعد الإعراب",
    "عوامل الإعراب",
    "الإعراب عن قواعد الإعراب",
    "شرح كتاب الحدود في النحو",
    "شرح اللمحة البدرية",
    "الكافية في النحو",
    "شرح الرضي على الكافية",
]


def classify_book(
    name: str,
    title: str,
    category: str,
) -> tuple[str, str] | None:
    """Classify a book as nahw or not.

    Returns (tier, reason) or None if not nahw.
    """
    title_norm = normalize_arabic(title)
    category_norm = normalize_arabic(category)

    # Tier A: category match
    if "النحو" in category_norm or "الصرف" in category_norm:
        # Accept "النحو والصرف" and similar
        if "النحو" in category_norm:
            return ("A", f"category='{category}'")

    # Tier B: title keyword match (high confidence)
    for kw in NAHW_KEYWORDS_HIGH:
        kw_norm = normalize_arabic(kw)
        if kw_norm in title_norm:
            return ("B", f"title contains '{kw}'")

    # Tier C: known book fragments — strict substring matching
    # Only if category is not clearly non-nahw
    NON_NAHW_CATEGORIES = {
        "الفقه", "العقيدة", "الحديث", "علوم الحديث", "التفسير",
        "أصول الفقه", "السيرة", "التاريخ", "التراجم",
    }
    cat_is_non_nahw = any(
        normalize_arabic(exc) in category_norm for exc in NON_NAHW_CATEGORIES
    )
    if not cat_is_non_nahw:
        name_norm = normalize_arabic(name)
        combined = title_norm + " " + name_norm
        for known in KNOWN_NAHW_BOOKS:
            known_norm = normalize_arabic(known)
            # Require the known title to appear as a substring,
            # or at least 80% of its words (for word-order differences)
            if known_norm in combined:
                return ("C", f"matches known book '{known}'")
            known_words = known_norm.split()
            if len(known_words) >= 3:
                matches = sum(1 for w in known_words if w in combined)
                if matches / len(known_words) >= 0.8:
                    return ("C", f"matches known book '{known}'")

    # Tier B (context): شرح/حاشية + any nahw term
    for ctx_kw in NAHW_KEYWORDS_CONTEXT:
        ctx_norm = normalize_arabic(ctx_kw)
        if ctx_norm in title_norm:
            for nahw_kw in NAHW_KEYWORDS_HIGH:
                nahw_norm = normalize_arabic(nahw_kw)
                if nahw_norm in title_norm:
                    return ("B", f"title contains '{ctx_kw}' + '{nahw_kw}'")

    return None


def main() -> None:
    """Scan all books and identify nahw works."""
    start = time.time()

    logger.info("Discovering all books in shamela-export-samples/...")
    all_books = discover_all_books()
    logger.info("Found %d books total", len(all_books))

    nahw_books: list[dict] = []
    seen_titles: set[str] = set()

    for name, first_file, is_multi, all_files in all_books:
        title = extract_title_fast(first_file)
        if not title:
            continue

        # Dedup by normalized title
        title_norm = normalize_arabic(title)
        if title_norm in seen_titles:
            continue
        seen_titles.add(title_norm)

        category = extract_category_fast(first_file)
        result = classify_book(name, title, category)

        if result is not None:
            tier, reason = result
            nahw_books.append({
                "name": name,
                "title": title,
                "category": category,
                "match_tier": tier,
                "match_reason": reason,
                "is_multivolume": is_multi,
                "volume_count": len(all_files),
                "files": [str(f.relative_to(first_file.parent.parent))
                          if is_multi else str(f.relative_to(f.parent))
                          for f in all_files],
                "first_file": str(first_file),
            })

    # Sort: Tier A first, then B, then C; within tier by title
    nahw_books.sort(key=lambda b: (b["match_tier"], b["title"]))

    elapsed = time.time() - start

    # Summary
    tier_counts = {"A": 0, "B": 0, "C": 0}
    for b in nahw_books:
        tier_counts[b["match_tier"]] = tier_counts.get(b["match_tier"], 0) + 1

    logger.info("═" * 60)
    logger.info("Nahw books identified: %d / %d total", len(nahw_books), len(all_books))
    logger.info("  Tier A (category):  %d", tier_counts.get("A", 0))
    logger.info("  Tier B (keywords):  %d", tier_counts.get("B", 0))
    logger.info("  Tier C (known):     %d", tier_counts.get("C", 0))
    logger.info("Elapsed: %.1fs", elapsed)
    logger.info("═" * 60)

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "nahw_books_identified.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_scanned": len(all_books),
            "nahw_count": len(nahw_books),
            "tier_counts": tier_counts,
            "books": nahw_books,
        }, f, ensure_ascii=False, indent=2)

    logger.info("Output written to %s", out_path)


if __name__ == "__main__":
    main()
