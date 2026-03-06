"""Content flagging — SPEC §4.A.9.

Detects content types per page: Quran citations, hadith citations,
verse (poetry), tables, TOC pages, index pages, blank pages.

Existing ABD code handles has_verse and has_table. KR adds:
  - has_quran_citation: Quran verse markers (بسم الله, آية patterns, surah names)
  - has_hadith_citation: Hadith collection references (البخاري, مسلم, etc.)
  - is_toc_page: Table of contents page detection
  - is_index_page: Index/فهرس page detection
  - is_blank: Page with no meaningful text

Implementation order: Step 5 in IMPL_BRIEF.md.
"""

from __future__ import annotations

from engines.normalization.contracts import ContentFlags


def flag_content(primary_text: str, html_raw: str = "") -> ContentFlags:
    """Classify content types present on a single page.

    Args:
        primary_text: Cleaned text for this page.
        html_raw: Raw HTML (for table detection via <table> tags).

    Returns:
        ContentFlags with boolean flags for each detected content type.
    """
    # TODO (Claude Code): Implement. See SPEC §4.A.9.
    raise NotImplementedError("flag_content")
