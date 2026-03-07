"""Atomization Engine — Scholarly Attribution Chain Resolution.

Implements SPEC §4.B.4: Detecting who is being quoted, cited, or attributed
within each atom and through what mechanism.

Attribution types: direct (named scholar), via_work (referenced through a work
title), school_collective (school attribution), isnad (hadith transmission chain),
anonymous (unidentified), self (author's own position), refutation_target
(position being refuted).

Attribution detection runs during the LLM atomization phase (Phase 3) when
enable_attribution_detection is true. Post-processing (Phase 4) verifies
marker_text appears in atom_text (ADV-3).

Raw scholar names — NOT canonical IDs. Downstream resolution is the
excerpting engine's responsibility via the scholar authority model.
"""

from __future__ import annotations


def extract_attributions(atom_text: str, scholarly_function: str,
                         config: "AtomizationConfig") -> list[dict]:
    """Extract scholarly attributions from a single atom's text.

    Called during LLM classification. Returns ScholarlyAttribution dicts.
    """
    raise NotImplementedError
