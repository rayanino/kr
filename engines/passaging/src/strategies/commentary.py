"""Commentary-Unit Strategy.

Implements SPEC §4.A.9.

For sharh/hashiyah texts with multiple text layers. Commentary units are
matn segment + its commentary. Boundary detection uses layer_map transitions.

Layer fingerprints (§4.B.9 of normalization SPEC) may adjust detection
sensitivity for pages where layer attribution is uncertain.

Commentary-matn precision alignment (§4.B.3) runs after initial passaging
to produce detailed matn-commentary correspondence records.
"""

from __future__ import annotations


def create_commentary_passages(assembled_text: dict, division, config) -> list:
    """Apply commentary-unit strategy to produce passage boundaries."""
    raise NotImplementedError
