"""Shared text utilities for the source engine (SPEC §4.A.1).

Functions used by metadata extraction (§4.A.3), slug generation,
scholar matching (§4.A.5), and work matching. These are shared
utilities, not engine-specific.
"""

from __future__ import annotations

import html as html_module
import re
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
