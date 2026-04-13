"""Shared text utilities for the source engine (SPEC §4.A.1).

Functions used by metadata extraction (§4.A.3), slug generation,
scholar matching (§4.A.5), and work matching. These are shared
utilities, not engine-specific.
"""

from __future__ import annotations

import hashlib
import html as html_module
import re
import uuid
from typing import Optional

# ──────────────────────────────────────────────────────────────────
# HTML tag stripping
# ──────────────────────────────────────────────────────────────────


def strip_tags(html_text: str) -> str:
    """Remove HTML tags and decode HTML entities.

    Two-step process:
    1. Remove all HTML tags: <anything> -> empty string
    2. Decode HTML entities: &nbsp; -> space, &amp; -> &, &#NNN; -> character

    Used by the Shamela extractor (§4.A.3) to extract clean text from
    the metadata card and body pages.

    Args:
        html_text: Raw HTML string.

    Returns:
        Clean text with tags removed and entities decoded.

    >>> strip_tags("<span class='title'>الكتاب</span>")
    'الكتاب'
    >>> strip_tags("Title&nbsp;&nbsp;Extra")
    'Title  Extra'
    >>> strip_tags("<b>bold &#1576;</b>")
    'bold ب'
    """
    text = re.sub(r"<[^>]+>", "", html_text)
    return html_module.unescape(text)


# ──────────────────────────────────────────────────────────────────
# Arabic ordinal parsing
# ──────────────────────────────────────────────────────────────────

ARABIC_ORDINALS: dict[str, int] = {
    "الأولى": 1,
    "الأول": 1,
    "الثانية": 2,
    "الثاني": 2,
    "الثالثة": 3,
    "الثالث": 3,
    "الرابعة": 4,
    "الرابع": 4,
    "الخامسة": 5,
    "الخامس": 5,
    "السادسة": 6,
    "السادس": 6,
    "السابعة": 7,
    "السابع": 7,
    "الثامنة": 8,
    "الثامن": 8,
    "التاسعة": 9,
    "التاسع": 9,
    "العاشرة": 10,
    "العاشر": 10,
    "العشرون": 20,
}


def parse_arabic_ordinal(text: str) -> Optional[int]:
    """Extract edition number from Arabic ordinal text.

    Checks for Arabic ordinal words first, then falls back to
    extracting the first bare integer from the string.

    Args:
        text: Edition string, e.g. "الأولى، 1408 هـ".

    Returns:
        Integer edition number, or None if not found.

    >>> parse_arabic_ordinal("الأولى، 1408 هـ")
    1
    >>> parse_arabic_ordinal("الطبعة 3")
    3
    >>> parse_arabic_ordinal("no number here")
    """
    for word, num in ARABIC_ORDINALS.items():
        if word in text:
            return num
    digits = re.findall(r"\d+", text)
    return int(digits[0]) if digits else None


# ──────────────────────────────────────────────────────────────────
# Slug generation (SPEC §4.A.1)
# ──────────────────────────────────────────────────────────────────

# 9 Unicode tashkeel marks (U+064B–U+0652, U+0670)
ARABIC_DIACRITICS: set[str] = {
    "\u064B",  # FATHATAN
    "\u064C",  # DAMMATAN
    "\u064D",  # KASRATAN
    "\u064E",  # FATHAH
    "\u064F",  # DAMMAH
    "\u0650",  # KASRAH
    "\u0651",  # SHADDAH
    "\u0652",  # SUKUN
    "\u0670",  # SUPERSCRIPT ALEF
}

# Arabic → Latin char mappings for slug generation
TRANSLIT_MAP: dict[str, str] = {
    "ا": "a", "أ": "a", "إ": "i", "آ": "a",
    "ب": "b", "ت": "t", "ث": "th", "ج": "j",
    "ح": "h", "خ": "kh", "د": "d", "ذ": "dh",
    "ر": "r", "ز": "z", "س": "s", "ش": "sh",
    "ص": "s", "ض": "d", "ط": "t", "ظ": "z",
    "ع": "a", "غ": "gh", "ف": "f", "ق": "q",
    "ك": "k", "ل": "l", "م": "m", "ن": "n",
    "ه": "h", "ة": "h", "و": "w", "ي": "y",
    "ى": "a", "ئ": "i", "ؤ": "u",
}


def strip_diacritics(text: str) -> str:
    """Remove Arabic tashkeel marks from text."""
    return "".join(ch for ch in text if ch not in ARABIC_DIACRITICS)


def transliterate_chars(text: str) -> str:
    """Transliterate Arabic text to Latin characters for slug use.

    Steps: strip "ال" prefix → char-by-char mapping → spaces to "_"
    → remove non-alphanumeric → collapse underscores → strip edges.
    """
    # Strip definite article "ال" (including sun-letter assimilations)
    text = re.sub(r"\bال", "al_", text)
    # Char-by-char transliteration
    result = []
    for ch in text:
        if ch in TRANSLIT_MAP:
            result.append(TRANSLIT_MAP[ch])
        elif ch in (" ", "_"):
            result.append("_")
        elif ch.isascii() and ch.isalnum():
            result.append(ch)
        # else: skip non-mapped characters
    slug = "".join(result)
    # Collapse underscores and strip edges
    slug = re.sub(r"_+", "_", slug)
    return slug.strip("_")


def generate_slug(arabic_text: str, table: dict[str, str]) -> str:
    """Generate a slug from Arabic text using a lookup table with fallback.

    1. Longest substring match in table
    2. Fallback: strip diacritics + transliterate
    3. Truncate to 20 chars
    4. If empty: first 8 hex of MD5
    """
    if not arabic_text or not arabic_text.strip():
        # Use uuid4 to avoid collision: all empty inputs would otherwise
        # produce the same MD5 hash (d41d8cd9).
        fallback_seed = f"_empty_{uuid.uuid4().hex[:8]}"
        return hashlib.md5(fallback_seed.encode("utf-8")).hexdigest()[:8]

    text = arabic_text.strip()

    # 1. Try table lookup — longest substring match
    best_match = ""
    best_slug = ""
    for key, slug_val in table.items():
        if key in text and len(key) > len(best_match):
            best_match = key
            best_slug = slug_val

    if best_slug:
        return best_slug[:20]

    # 2. Fallback: strip diacritics + transliterate
    cleaned = strip_diacritics(text)
    slug = transliterate_chars(cleaned)

    # 3. Truncate to 20 chars
    slug = slug[:20]

    # 4. If empty: MD5 hash
    if not slug:
        return hashlib.md5(text.encode("utf-8")).hexdigest()[:8]

    return slug


def generate_work_id(
    author_name: str,
    title: str,
    transliteration_table: dict[str, dict[str, str]],
) -> str:
    """Generate a work_id: wrk_{author_slug}_{title_slug}, max 50 chars.

    Uses table["scholars"] for author slug and table["titles"] for title slug.
    """
    scholar_table = transliteration_table.get("scholars", {})
    title_table = transliteration_table.get("titles", {})

    author_slug = generate_slug(author_name, scholar_table)
    title_slug = generate_slug(title, title_table)

    work_id = f"wrk_{author_slug}_{title_slug}"
    return work_id[:50]


def generate_human_label(
    title: str,
    transliteration_table: dict[str, dict[str, str]],
) -> str:
    """Generate a human-readable label: transliterated, lowercased, max 30 chars."""
    title_table = transliteration_table.get("titles", {})
    slug = generate_slug(title, title_table)
    label = slug.lower()
    return label[:30]
