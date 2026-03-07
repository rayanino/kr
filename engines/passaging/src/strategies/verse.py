"""Verse Strategy.

Implements SPEC §4.A.5.

For versified texts (منظومات). Verse lines (بيت) are atomic units —
never split across passages. Grouping respects:
  - Division tree headings (chapter/section = passage boundary)
  - Target size: verse_min_passage_words to target_passage_words_high
  - Verse numbering continuity (no renumbering within a passage)
"""

from __future__ import annotations


def create_verse_passages(assembled_text: dict, division, config) -> list:
    """Apply verse strategy to produce passage boundaries."""
    raise NotImplementedError
