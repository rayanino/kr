"""Atomization Engine — Multi-Layer Attribution.

Implements SPEC §4.A.6: Deriving source_layer and layer_author_id
for each atom based on the passage's text_layers array.

For single-layer passages: all atoms get source_layer "matn".

For multi-layer passages: each atom's character range [start, end) is matched
against the text_layers segments. The segment with the largest overlap
determines the atom's source_layer and layer_author_id.

Edge cases:
  - Atom spanning a layer boundary: attributed to the first layer segment.
    Carries "ambiguous_layer" review flag.
  - Bonded cluster spanning a layer transition: attributed to first layer,
    carries both "ambiguous_layer" and "possible_misattribution" flags,
    classification_notes explains the overlap.
  - Unrecognized layer_type: defaults to "matn", sets "ambiguous_layer" flag,
    logs ATOM_UNKNOWN_LAYER_TYPE.
"""

from __future__ import annotations


def attribute_layers(atoms: list[dict], text_layers: list[dict]) -> list[dict]:
    """Assign source_layer and layer_author_id to each atom.

    Modifies atoms in place and returns them.
    """
    raise NotImplementedError
