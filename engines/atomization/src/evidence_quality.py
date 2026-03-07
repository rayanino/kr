"""Atomization Engine — Evidence Quality Signal Detection.

Implements SPEC §4.B.8: Detecting author's explicit evaluation of evidence strength.

NOT the system's evaluation — the source author's own quality markers.

Signal types:
  - hadith_strong_collection: reference to sahihayn or other strong collections
  - hadith_weakness_flag: explicit weakness notation
  - hadith_chain_quality: isnad quality commentary
  - evidence_explicit_strength: author's explicit strengthening
  - evidence_explicit_weakness: author's explicit weakening
  - consensus_qualifier: qualifying a consensus claim
  - author_tarjih_marker: author's preference/weighting indicator

Uses a phrase lexicon (evidence_quality_lexicon_path) for pattern matching,
with LLM verification for ambiguous cases.
"""

from __future__ import annotations


def detect_evidence_quality_signals(atom_text: str, scholarly_function: str,
                                    config: "AtomizationConfig") -> list[dict]:
    """Detect evidence quality signals in an evidence atom.

    Returns list of EvidenceQualitySignal dicts.
    Returns empty list for non-evidence atoms or when detection is disabled.
    """
    raise NotImplementedError


def load_quality_lexicon(path: str) -> dict:
    """Load the evidence quality signal phrase lexicon."""
    raise NotImplementedError
