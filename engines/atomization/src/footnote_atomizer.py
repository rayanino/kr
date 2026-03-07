"""Atomization Engine — Footnote Atomization.

Implements SPEC §4.A.9: Processing footnotes from the passage's footnotes array.

Each footnote becomes a separate atom with:
  - source_layer: "footnote"
  - footnote_source_index: zero-based index into passage's footnotes array
  - atom_relations: footnote_for relation linking to the main text atom

Footnote atoms appear after all main text atoms in the atom stream.
They are excluded from V-1 exhaustive coverage check over passage_text.

Offset integrity for footnote atoms: atom_text == footnote.text[start:end].
Footnotes may contain embedded content (Quran citations, etc.) — the same
pre-detection and LLM classification applies.

ADV-8: orphaned footnote markers (⌜N⌝ referencing non-existent footnotes)
are detected and flagged with ATOM_FOOTNOTE_INDEX_OUT_OF_RANGE.
"""

from __future__ import annotations


def atomize_footnotes(footnotes: list[dict], main_text_atoms: list[dict],
                      passage: dict, atom_id_counter: int,
                      config: "AtomizationConfig") -> tuple[list[dict], int]:
    """Atomize all footnotes for a passage.

    Returns (footnote_atoms, next_atom_id_counter).
    Footnote atoms have source_layer "footnote" and are linked
    to their referencing main text atoms via atom_relations.
    """
    raise NotImplementedError
