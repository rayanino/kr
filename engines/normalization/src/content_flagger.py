"""Content flagging — SPEC §4.A.9.

Detects content types per page: Quran citations, hadith citations,
verse (poetry), tables, TOC pages, index pages, blank pages.

Each flag is computed independently. Pass 3 already provides has_verse,
has_tables, is_blank, is_image_only on CleanedPage — this module adds
the remaining flags from text analysis.

Arabic-safe regex rules:
  - [\\u0600-\\u06FF] for Arabic chars (NOT \\w)
  - [0-9] for ASCII digits (NOT \\d — matches Arabic-Indic digits)
  - No \\b for Arabic word boundaries (clitics break it)
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from engines.normalization.contracts import ContentFlags

if TYPE_CHECKING:
    from engines.normalization.src.normalizers.shamela import CleanedPage


# ──────────────────────────────────────────────────────────────────
# Quran citation patterns
# ──────────────────────────────────────────────────────────────────

# Pattern 1: قال تعالى (with optional colon)
_QURAN_QALA_TAALA = re.compile(r"قال\s+تعالى")

# Pattern 2: Curly bracket Quran markers {Arabic text}
_QURAN_CURLY = re.compile(r"\{[\u0600-\u06FF\s]{3,}\}")

# Pattern 3: Ornate Quran brackets ﴿Arabic text﴾
_QURAN_ORNATE = re.compile(r"\uFD3F[\u0600-\u06FF\s]{3,}\uFD3E")

# Pattern 4: سورة + surah name
_QURAN_SURAH = re.compile(r"سورة\s+[\u0600-\u06FF]+")


def _has_quran_citation(text: str) -> bool:
    """Detect Quran citations via 4 independent patterns."""
    return bool(
        _QURAN_QALA_TAALA.search(text)
        or _QURAN_CURLY.search(text)
        or _QURAN_ORNATE.search(text)
        or _QURAN_SURAH.search(text)
    )


# ──────────────────────────────────────────────────────────────────
# Hadith citation patterns
# ──────────────────────────────────────────────────────────────────

# Major hadith collector names
_HADITH_COLLECTORS = (
    "البخاري",
    "مسلم",
    "أبو داود",
    "الترمذي",
    "النسائي",
    "ابن ماجه",
    "أحمد",
)

# Pattern 1: ﷺ (Unicode sallallahu alayhi wasallam)
_HADITH_SAWS_CHAR = "\uFDFA"

# Pattern 2: صلى الله عليه وسلم
_HADITH_SAWS_PHRASE = re.compile(r"صلى\s+الله\s+عليه\s+وسلم")

# Pattern 3: رواه + collector name
_HADITH_RAWAHU = re.compile(
    r"رواه\s+(?:" + "|".join(re.escape(c) for c in _HADITH_COLLECTORS) + r")"
)

# Pattern 4: «Arabic text» with قال within 80 chars before (D8, L-009 fix)
# Distance 80 catches long isnad chains: حدثنا فلان عن فلان عن فلان قال
# re.DOTALL: قال and « may be on different lines in primary_text
_HADITH_GUILLEMET = re.compile(
    r"قال.{0,80}«[\u0600-\u06FF\s]{3,}»",
    re.DOTALL,
)


def _has_hadith_citation(text: str) -> bool:
    """Detect hadith citations via 4 independent patterns."""
    return bool(
        _HADITH_SAWS_CHAR in text
        or _HADITH_SAWS_PHRASE.search(text)
        or _HADITH_RAWAHU.search(text)
        or _HADITH_GUILLEMET.search(text)
    )


# ──────────────────────────────────────────────────────────────────
# Index page detection (NOT TOC — separate from toc_page)
# ──────────────────────────────────────────────────────────────────

_INDEX_KEYWORDS = (
    "فهرس الأعلام",
    "فهرس الأحاديث",
    "فهرس الآيات",
    "فهرس المصادر",
    "فهرس الأبيات",
)


def _is_index_page(
    primary_text: str, title_spans: list[str],
) -> bool:
    """Detect index pages by keywords in first 200 chars or title_spans."""
    head = primary_text[:200]
    for kw in _INDEX_KEYWORDS:
        if kw in head:
            return True
    for span in title_spans:
        for kw in _INDEX_KEYWORDS:
            if kw in span:
                return True
    return False


# ──────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────


def compute_content_flags(page: CleanedPage, is_toc_page: bool) -> ContentFlags:
    """Compute content flags for a single CleanedPage.

    Args:
        page: A CleanedPage from Pass 3.
        is_toc_page: Whether structure discovery identified this as a TOC page.

    Returns:
        ContentFlags with all boolean flags populated.
    """
    text = page.primary_text

    return ContentFlags(
        has_verse=page.has_verse,
        has_table=page.has_tables,
        has_quran_citation=_has_quran_citation(text),
        has_hadith_citation=_has_hadith_citation(text),
        is_toc_page=is_toc_page,
        is_index_page=_is_index_page(text, page.title_spans),
        is_blank=(
            page.is_blank
            or page.is_image_only
            or len(text.strip()) == 0
        ),
    )
