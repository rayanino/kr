"""Verse Atomization Strategy.

Implements SPEC §4.A.7 verse strategy: for versified texts (نظم/شعر).

Each بيت (verse line) is one atom with structural_type verse_line (AB-7).
Hemistichs (صدر/عجز) are NOT split. Verse numbering from verse_info is
preserved. The scholarly function of each verse line is classified by the LLM.

If verse_info.verse_lines count disagrees with LLM-detected count,
the engine trusts verse_info (§4.A.7).
"""

from __future__ import annotations


def atomize_verse(passage_text: str, verse_info: dict,
                  predetection_hints: list[dict],
                  config: "AtomizationConfig") -> list[dict]:
    """Apply verse atomization strategy. Returns raw LLM atom objects."""
    raise NotImplementedError
