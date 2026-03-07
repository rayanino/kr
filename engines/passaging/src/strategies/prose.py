"""Prose Strategy — Division-Guided with Semantic Splitting.

Implements SPEC §4.A.4.

The default and most common strategy. Three-step process:
  Step 1: Division tree evaluation — classify each leaf division by size.
  Step 2: Boundary refinement using boundary_continuity signals.
  Step 3: Semantic splitting for oversized divisions (LLM-assisted above threshold).

Size ranges (configurable):
  - Direct: 200–800 words (target range)
  - Merge: <50 words (merge with adjacent sibling)
  - Split: >2000 words (hard max, must split)

Sentence integrity: no boundary falls mid-sentence.
Isnad preservation: حدثنا chains never split from their matn.
"""

from __future__ import annotations


def create_prose_passages(assembled_text: dict, division, config) -> list:
    """Apply prose strategy to produce passage boundaries."""
    raise NotImplementedError
