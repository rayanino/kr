"""Phase 3 Orchestrator: deterministic → enrichment → consensus → validation (SPEC §7).

Chains all Phase 3 stages in order. Each stage produces the input for the next.
Graceful degradation: LLM failures degrade to deterministic-only output, not crashes.
Gate queue is collected across all chunks and returned for a single write after all processing.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import instructor  # pyright: ignore[reportMissingImports]

from engines.excerpting.contracts import (
    AssembledChunk,
    ClassifiedSegment,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    TeachingUnit,
)
from engines.excerpting.src.phase3_deterministic import build_deterministic_excerpts
from engines.excerpting.src.phase3_enrichment import run_phase3_enrichment
from engines.excerpting.src.phase3_consensus import run_consensus
from engines.excerpting.src.phase3_validation import validate_batch

if TYPE_CHECKING:
    from engines.excerpting.src.cache import CacheManager
    from engines.excerpting.src.progress import ProgressTracker

logger = logging.getLogger(__name__)


@dataclass
class Phase3Result:
    """Result of Phase 3 processing.

    Attributes:
        excerpts: Validated ExcerptRecords ready for output.
        gate_entries: Human gate entries to write to gate_queue.jsonl.
        errors: All error codes emitted during Phase 3 processing.
        timings: Per-stage timing in seconds.
        validation_drops: Excerpts dropped by V-P3-2 validation, with identity.
    """

    excerpts: list[ExcerptRecord] = field(default_factory=list)
    gate_entries: list[dict[str, object]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)
    validation_drops: list[dict[str, object]] = field(default_factory=list)


def run_phase3(
    chunks: list[AssembledChunk],
    teaching_units: dict[str, list[TeachingUnit]],
    classified: dict[str, list[ClassifiedSegment]],
    config: ExcerptingConfig,
    enrich_client: Optional[instructor.Instructor] = None,
    verify_client: Optional[instructor.Instructor] = None,
    escalation_client: Optional[instructor.Instructor] = None,
    source_metadata: Optional[dict[str, str]] = None,
    progress: Optional["ProgressTracker"] = None,
    cache: Optional["CacheManager"] = None,
) -> Phase3Result:
    """Execute Phase 3: deterministic → enrichment → consensus → validation.

    Args:
        chunks: AssembledChunks from Phase 1.
        teaching_units: dict[chunk_id → list[TeachingUnit]] from Phase 2b.
        classified: dict[chunk_id → list[ClassifiedSegment]] from Phase 2a.
        config: Engine configuration.
        enrich_client: Instructor client for LLM enrichment. None = deterministic-only.
        verify_client: Instructor client for consensus verification. None = skip consensus.
        escalation_client: Instructor client for 3-model escalation. Optional.
        source_metadata: Source-level metadata passed to LLM prompts.

    Returns:
        Phase3Result with validated excerpts, gate entries, and error summary.
    """
    result = Phase3Result()

    # ── Stage 1: Deterministic metadata assembly ──────────────────
    t0 = time.monotonic()
    all_excerpts: list[ExcerptRecord] = []

    for chunk in chunks:
        chunk_id = chunk.chunk_id
        units = teaching_units.get(chunk_id, [])
        segments = classified.get(chunk_id, [])

        if not units:
            logger.warning(
                "No teaching units for chunk %s — skipping deterministic assembly.",
                chunk_id,
            )
            continue

        excerpts = build_deterministic_excerpts(chunk, units, segments)
        all_excerpts.extend(excerpts)

    result.timings["deterministic"] = time.monotonic() - t0
    logger.info(
        "Phase 3 deterministic: %d excerpts from %d chunks (%.2fs).",
        len(all_excerpts),
        len(chunks),
        result.timings["deterministic"],
    )

    if not all_excerpts:
        logger.warning("No excerpts after deterministic assembly — returning empty result.")
        return result

    # ── Stage 2: LLM enrichment (graceful degradation) ────────────
    if enrich_client is not None:
        t1 = time.monotonic()
        try:
            all_excerpts = run_phase3_enrichment(
                excerpts=all_excerpts,
                chunks=chunks,
                client=enrich_client,
                config=config,
                source_metadata=source_metadata,
                progress=progress,
                cache=cache,
                error_sink=result.errors,
            )
        except Exception as exc:
            if isinstance(exc, (TypeError, AttributeError, NameError, KeyError, IndexError, ZeroDivisionError, StopIteration)):
                raise  # Programming bugs must crash
            logger.error(
                "%s: LLM enrichment failed — degrading to deterministic-only: %s",
                ExcerptingErrorCodes.EX_M_002,
                exc,
            )
            result.errors.append(ExcerptingErrorCodes.EX_M_002)
        result.timings["enrichment"] = time.monotonic() - t1
        logger.info(
            "Phase 3 enrichment: %.2fs.",
            result.timings["enrichment"],
        )
    else:
        logger.info("Phase 3 enrichment: SKIPPED (no LLM client).")
        result.timings["enrichment"] = 0.0

    # ── Stage 3: Consensus verification (graceful degradation) ────
    if verify_client is not None:
        t2 = time.monotonic()
        try:
            all_excerpts, gate_entries = run_consensus(
                excerpts=all_excerpts,
                chunks=chunks,
                verify_client=verify_client,
                escalation_client=escalation_client,
                config=config,
                source_metadata=source_metadata,
                progress=progress,
                cache=cache,
                error_sink=result.errors,
            )
            result.gate_entries.extend(gate_entries)
        except Exception as exc:
            if isinstance(exc, (TypeError, AttributeError, NameError, KeyError,
                                IndexError, ZeroDivisionError, StopIteration)):
                raise  # Programming bugs must crash
            logger.error(
                "Consensus verification failed — degrading to current excerpt output: %s", exc,
            )
            result.errors.append(ExcerptingErrorCodes.EX_M_011)
            flagged = []
            for e in all_excerpts:
                flags = list(e.review_flags)
                if "verification_skipped" not in flags:
                    flags.append("verification_skipped")
                flagged.append(e.model_copy(update={"review_flags": flags}))
            all_excerpts = flagged
        result.timings["consensus"] = time.monotonic() - t2
        logger.info(
            "Phase 3 consensus: %d gate entries (%.2fs).",
            len(result.gate_entries),
            result.timings["consensus"],
        )
    else:
        logger.info(
            "Phase 3 consensus: SKIPPED (verify_client=%s).",
            verify_client is not None,
        )
        result.timings["consensus"] = 0.0

    # ── Stage 4: Validation (V-P3-1 through V-P3-9) ──────────────
    t3 = time.monotonic()
    validated_excerpts, validation_errors = validate_batch(all_excerpts)
    result.errors.extend(validation_errors)
    result.excerpts = validated_excerpts
    result.timings["validation"] = time.monotonic() - t3

    # Record exactly which excerpts were dropped (per-unit identity)
    validated_ids = {e.excerpt_id for e in validated_excerpts}
    for exc in all_excerpts:
        if exc.excerpt_id not in validated_ids:
            result.validation_drops.append({
                "excerpt_id": exc.excerpt_id,
                "source_id": exc.source_id,
                "div_id": exc.div_id,
                "chunk_index": exc.chunk_index,
                "unit_index": exc.unit_index,
                "text_snippet": exc.text_snippet[:80] if exc.text_snippet else "",
            })

    logger.info(
        "Phase 3 validation: %d excerpts, %d errors, %d drops (%.2fs).",
        len(result.excerpts),
        len(validation_errors),
        len(result.validation_drops),
        result.timings["validation"],
    )

    return result
