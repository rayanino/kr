"""Phase 2b: Teaching Unit Grouping (SPEC §5.3, §5.4.3).

Groups classified segments into TeachingUnit objects using one LLM call
per chunk. Verifies unit coverage invariants.

All LLM calls go through OpenRouter via Instructor.
"""

from __future__ import annotations

import logging

import instructor

from engines.excerpting.contracts import (
    AssembledChunk,
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ExtractionResult,
    TeachingUnit,
    validate_tu_invariants,
)

logger = logging.getLogger(__name__)


def group_chunk(
    chunk: AssembledChunk,
    segments: list[ClassifiedSegment],
    client: instructor.Instructor,
    config: ExcerptingConfig,
) -> ExtractionResult:
    """Send chunk + classified segments to LLM for grouping (§5.3).

    Uses the system prompt from §5.3.2 and user message from §5.3.3.
    Returns raw ExtractionResult.
    """
    raise NotImplementedError


def verify_units(
    units: list[TeachingUnit],
    segments: list[ClassifiedSegment],
    total_tokens: int,
) -> None:
    """Verify teaching unit invariants V-P2-10 through V-P2-19 (§5.4.3).

    Delegates to validate_tu_invariants() in contracts.py.
    Auto-repairs V-P2-14 (word range derivation) and V-P2-15 (notes consistency).
    Raises ValueError on any fatal violation.
    """
    raise NotImplementedError


def run_phase2b(
    chunks: list[AssembledChunk],
    classified: dict[str, list[ClassifiedSegment]],
    client: instructor.Instructor,
    config: ExcerptingConfig,
) -> dict[str, list[TeachingUnit]]:
    """Execute Phase 2b for all chunks: group + verify (§5.1 steps 4–5).

    Only processes chunks that succeeded Phase 2a (present in classified dict).
    Retries per §5.5.2. Flags failed chunks with EX-C-002/EX-C-005.
    Returns dict mapping chunk_id → list[TeachingUnit].
    """
    raise NotImplementedError
