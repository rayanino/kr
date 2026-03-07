"""Dictionary Entry Strategy.

Implements SPEC §4.A.8.

For lexical/biographical dictionaries. Each entry (identified by lemma marker
or biographical name marker) is a natural passage unit. Entries vary widely
in length — some are one line, others span pages. Standard merge/split
rules apply to very short or very long entries.
"""

from __future__ import annotations


def create_dictionary_passages(assembled_text: dict, division, config) -> list:
    """Apply dictionary entry strategy to produce passage boundaries."""
    raise NotImplementedError
