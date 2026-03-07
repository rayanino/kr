"""Passaging Engine — Strategy Selection.

Implements SPEC §4.A.3.

Selects the passaging strategy based on the manifest's structural_format field:
  prose → ProseStrategy (§4.A.4)
  verse → VerseStrategy (§4.A.5)
  qa_format → QAStrategy (§4.A.6)
  tabular_khilaf → MasalaStrategy (§4.A.7)
  dictionary → DictionaryStrategy (§4.A.8)
  commentary → CommentaryStrategy (§4.A.9)
  mixed → per-division strategy selection based on division content analysis

For 'mixed' format: each leaf division is classified independently using
content analysis (presence of verse markers, Q&A patterns, etc.).
Falls back to prose for unclassifiable divisions (PSG_FORMAT_DETECTION_FAILED).
"""

from __future__ import annotations


def select_strategy(structural_format: str, manifest=None):
    """Select the passaging strategy for a source or division.

    For 'mixed' format, returns a strategy selector function
    that picks per-division strategy.

    Returns a strategy callable: (assembled_text, division, config) → list[PassageBoundary]
    """
    raise NotImplementedError
