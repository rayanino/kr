"""Dictionary Entry Atomization Strategy.

Implements SPEC §4.A.7 dictionary_entry strategy: for lexical/biographical entries.

Dictionary entries typically have a headword (heading atom) followed by
definition(s), examples, and cross-references. The strategy prioritizes
correct definition atom classification and concordance extraction (§4.B.7).
"""

from __future__ import annotations


def atomize_dictionary(passage_text: str, heading_text: str | None,
                       predetection_hints: list[dict],
                       config: "AtomizationConfig") -> list[dict]:
    """Apply dictionary entry atomization strategy. Returns raw LLM atom objects."""
    raise NotImplementedError
