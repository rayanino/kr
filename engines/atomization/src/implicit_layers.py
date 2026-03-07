"""Atomization Engine — Implicit Layer Transition Detection.

Implements SPEC §4.B.2: Detecting unmarked shifts between text layers.

[NOT YET IMPLEMENTED] — Full specification in SPEC §4.B.2.

In commentary texts, authors sometimes shift between layers (matn → sharh)
without explicit markers. This module detects probable layer transitions
by analyzing stylistic and content shifts, preventing misattribution.
"""

from __future__ import annotations


def detect_implicit_transitions(atoms: list[dict], text_layers: list[dict],
                                config: "AtomizationConfig") -> list[dict]:
    """Detect probable implicit layer transitions within a passage's atoms.

    Returns list of transition candidates with atom_id, proposed_layer,
    and confidence. Does NOT modify atoms — returns suggestions for
    postprocessor to evaluate.
    """
    raise NotImplementedError
