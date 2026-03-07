"""Q&A Pair Atomization Strategy.

Implements SPEC §4.A.7 Q&A strategy: for qa_pair format passages.

Each question-answer pair is a bonded cluster atom (AB-2).
The question and its answer are never split.
"""

from __future__ import annotations


def atomize_qa(passage_text: str, predetection_hints: list[dict],
               config: "AtomizationConfig") -> list[dict]:
    """Apply Q&A atomization strategy. Returns raw LLM atom objects."""
    raise NotImplementedError
