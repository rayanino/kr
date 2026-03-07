"""Prose Atomization Strategy.

Implements SPEC §4.A.7 prose strategy: the default for most scholarly text.

Prose passages are the most common format. Atom boundaries follow AB-1
(one assertion per atom) with AB-2 bonded cluster rules. The LLM receives
the full atom boundary ruleset and scholarly function taxonomy.

Few-shot examples from gold baselines for: definitions, rule statements,
evidence citations (Quran, hadith, rational), opinion statements,
refutations, examples, condition-exception atoms, and bonded clusters.
"""

from __future__ import annotations


def atomize_prose(passage_text: str, predetection_hints: list[dict],
                  text_layers: list[dict],
                  config: "AtomizationConfig") -> list[dict]:
    """Apply prose atomization strategy. Returns raw LLM atom objects."""
    raise NotImplementedError
