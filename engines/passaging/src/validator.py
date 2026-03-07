"""Passaging Engine — Self-Validation.

Implements SPEC §4.A.10 (self-validation checks 1–11).

Eleven checks run on every output:
  Fatal checks (abort on failure):
    #1  Coverage — every substantive unit in exactly one passage
    #2  Non-overlap — no unit in multiple passages
    #4b Text integrity — character count invariant
    #5  Layer coverage — every char covered by one layer segment
    #9  Link consistency — predecessor/successor chain valid
    #10 Author preservation — no (layer_type, author_id) pairs lost

  Warning checks (flag but write):
    #3  Ordering — sequence_index monotonic, unit_range.start increasing
    #6  Size sanity — no passage >3x hard max
    #7  Footnote reference — every ⌜N⌝ has a footnote entry
    #8  Boundary integrity — no mid-sentence boundaries
    #11 Bidirectional footnote — every footnote entry has a marker
"""

from __future__ import annotations


def validate_passage_stream(passages: list, content_units: list, manifest) -> list:
    """Run all 11 self-validation checks.

    Returns list of validation errors/warnings.
    Raises PassagingFatalError if any fatal check fails.
    """
    raise NotImplementedError
