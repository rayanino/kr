"""§4.B.3 — Commentary-Matn Precision Alignment. [NOT YET IMPLEMENTED]

For commentary-format passages: maps each matn segment to its
corresponding commentary span with character-level precision.

Output: list[CommentaryAlignmentRecord] on commentary-unit passages.
Gated by config.enable_commentary_alignment (default: true).
"""

from __future__ import annotations
