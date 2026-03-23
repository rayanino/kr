"""Phase 2a: Segment Classification + Offset Normalization (SPEC §5.2, §5.4.1–2).

Classifies each AssembledChunk's text into ClassifiedSegment objects using
one LLM call per chunk. Normalizes LLM-produced word offsets to canonical
tokenization using text_snippet anchors. Verifies segment coverage invariants.

All LLM calls go through OpenRouter via Instructor.
"""

from __future__ import annotations

import logging
from typing import Optional

import instructor

from engines.excerpting.contracts import (
    AssembledChunk,
    ClassificationResult,
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    validate_cs_invariants,
)

logger = logging.getLogger(__name__)


def classify_chunk(
    chunk: AssembledChunk,
    client: instructor.Instructor,
    config: ExcerptingConfig,
) -> ClassificationResult:
    """Send chunk's assembled_text to LLM for segment classification (§5.2).

    Uses the system prompt from §5.2.2 and user message from §5.2.3.
    Returns raw ClassificationResult (offsets not yet normalized).
    """
    raise NotImplementedError


def normalize_offsets(
    segments: list[ClassifiedSegment],
    assembled_text: str,
    total_tokens: int,
) -> list[ClassifiedSegment]:
    """Remap LLM-produced word offsets to canonical tokenization (§5.4.1).

    Uses text_snippet fields as alignment anchors. Left-to-right search
    prevents misalignment from duplicate snippets.

    Matching cascade: exact → whitespace-normalized → diacritic-stripped (EX-A-012).

    Returns new list of ClassifiedSegment with canonical offsets.
    Raises ValueError if any snippet cannot be located after all matching attempts.
    """
    raise NotImplementedError


def verify_segments(
    segments: list[ClassifiedSegment],
    total_tokens: int,
) -> None:
    """Verify segment coverage invariants V-P2-1 through V-P2-9 (§5.4.2).

    Delegates to validate_cs_invariants() in contracts.py.
    Raises ValueError on any fatal violation.
    """
    raise NotImplementedError


def _compute_classify_max_tokens(word_count: int) -> int:
    """Compute MAX_TOKENS for classification call based on input size (§5.5.1).

    <=2000 words: 8192. >2000 words: 32768. >4000 words: 32768 (provisional).
    """
    raise NotImplementedError


def run_phase2a(
    chunks: list[AssembledChunk],
    client: instructor.Instructor,
    config: ExcerptingConfig,
) -> dict[str, list[ClassifiedSegment]]:
    """Execute Phase 2a for all chunks: classify + normalize + verify (§5.1 steps 1–3).

    Retries per §5.5.2. Flags failed chunks with EX-C-001/EX-C-003/EX-C-004.
    Returns dict mapping chunk_id → list[ClassifiedSegment].
    Failed chunks are absent from the result (logged, not silently dropped).
    """
    raise NotImplementedError
