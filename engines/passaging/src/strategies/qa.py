"""Q&A Pair Strategy.

Implements SPEC §4.A.6.

For فتاوى and Q&A-format texts. Each question-answer pair is a natural
passage unit. Detection uses سؤال/جواب markers and their variants.
Adjacent small Q&A pairs may be merged if both are under merge threshold.
"""

from __future__ import annotations


def create_qa_passages(assembled_text: dict, division, config) -> list:
    """Apply Q&A pair strategy to produce passage boundaries."""
    raise NotImplementedError
