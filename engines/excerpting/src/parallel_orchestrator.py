"""Parallel chunk pipeline orchestrator.

Processes chunks through the full excerpting pipeline concurrently
using ThreadPoolExecutor. A global Semaphore limits simultaneous
CLI/API calls to prevent backend overload.

Each worker thread owns:
- Its own CLIInstructorAdapter instance (F2: no shared hook state)
- Its own ChunkPipelineContext (per-chunk state)
- Access to shared ConcurrencyController (thread-safe Semaphore)

Integrates with ProgressTracker (Layer 2) and CacheManager (Layer 3).
"""
from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class ConcurrencyController:
    """Global semaphore limiting total simultaneous CLI/API calls."""

    def __init__(self, max_concurrent: int) -> None:
        self._semaphore = threading.Semaphore(max_concurrent)
        self._max = max_concurrent
        self._active = 0
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Acquire a slot. Blocks if all slots are in use."""
        self._semaphore.acquire()
        with self._lock:
            self._active += 1

    def release(self) -> None:
        """Release a slot."""
        with self._lock:
            self._active -= 1
        self._semaphore.release()

    @property
    def active_count(self) -> int:
        """Number of currently held slots."""
        with self._lock:
            return self._active


@dataclass
class ChunkPipelineContext:
    """Tracks one chunk's progress through all phases."""

    chunk: Any  # AssembledChunk
    chunk_id: str
    segments: Optional[list[Any]] = None        # Phase 2a output
    units: Optional[list[Any]] = None            # Phase 2b output
    excerpts: Optional[list[Any]] = None         # Phase 3 deterministic output
    enriched_excerpts: Optional[list[Any]] = None  # Phase 3 enrichment output
    final_excerpts: Optional[list[Any]] = None     # Phase 3 consensus output
    gate_entries: list[Any] = field(default_factory=list)
    error: Optional[str] = None
    completed: bool = False


def _process_chunk(
    ctx: ChunkPipelineContext,
    enrich_client: Any,
    verify_client: Any,
    escalation_client: Any,
    config: Any,
    controller: ConcurrencyController,
    progress: Optional[Any],
    cache: Optional[Any],
    classified_data: Optional[dict[str, list[Any]]],
    grouped_data: Optional[dict[str, list[Any]]],
    source_metadata: Optional[dict[str, str]],
) -> ChunkPipelineContext:
    """Run the full pipeline for one chunk. Called in its own thread.

    Uses the Semaphore only around LLM calls.
    Returns the updated context with results or error.
    """
    from pydantic import ValidationError

    from engines.excerpting.src.phase2_classify import (
        classify_chunk,
        normalize_offsets,
        verify_segments,
    )
    from engines.excerpting.src.phase2_group import group_chunk, verify_units
    from engines.excerpting.src.phase3_consensus import (
        _needs_consensus,
        check_gate_triggers,
        resolve_consensus,
        verify_chunk,
    )
    from engines.excerpting.src.phase3_deterministic import (
        build_deterministic_excerpts,
    )
    from engines.excerpting.src.phase3_enrichment import (
        apply_enrichment,
        enrich_chunk,
    )

    chunk = ctx.chunk
    chunk_id = ctx.chunk_id
    max_attempts = 1 + config.RETRY_COUNT

    try:
        # Phase 2a: Classify
        if progress is not None and progress.is_done(chunk_id, "phase2a"):
            if classified_data and chunk_id in classified_data:
                ctx.segments = classified_data[chunk_id]
                logger.info("[%s] Phase 2a: loaded from resume", chunk_id)
            else:
                logger.warning(
                    "[%s] Phase 2a: marked done but no data, re-processing",
                    chunk_id,
                )
                ctx.segments = None

        if ctx.segments is None:
            current_timeout = config.CLASSIFY_TIMEOUT
            error_feedback: Optional[str] = None
            for attempt in range(max_attempts):
                try:
                    controller.acquire()
                    try:
                        cr = classify_chunk(
                            chunk,
                            enrich_client,
                            config,
                            error_feedback,
                            timeout_override=current_timeout,
                        )
                    finally:
                        controller.release()

                    canonical = normalize_offsets(
                        cr.segments, chunk.assembled_text, chunk.total_tokens
                    )
                    verify_segments(canonical, chunk.total_tokens)
                    ctx.segments = canonical
                    if progress is not None:
                        progress.mark_done(chunk_id, "phase2a")
                    break
                except ValidationError:
                    error_feedback = None
                    logger.warning(
                        "[%s] Phase 2a attempt %d/%d: validation error",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                    )
                except ValueError as exc:
                    error_feedback = f"\n\nPrevious output error: {exc}"
                    logger.warning(
                        "[%s] Phase 2a attempt %d/%d: %s",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                        exc,
                    )
                except Exception as exc:
                    error_feedback = None
                    current_timeout = min(
                        int(current_timeout * 1.5),
                        config.CLASSIFY_TIMEOUT * 2,
                    )
                    logger.warning(
                        "[%s] Phase 2a attempt %d/%d: %s, backing off",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                        exc,
                    )
                    time.sleep(2**attempt)

            if ctx.segments is None:
                ctx.error = "phase2a_failed"
                if progress is not None:
                    progress.mark_failed(chunk_id, "phase2a", "EX-C-001")
                return ctx

        # Phase 2b: Group
        if progress is not None and progress.is_done(chunk_id, "phase2b"):
            if grouped_data and chunk_id in grouped_data:
                ctx.units = grouped_data[chunk_id]
                logger.info("[%s] Phase 2b: loaded from resume", chunk_id)
            else:
                logger.warning(
                    "[%s] Phase 2b: marked done but no data, re-processing",
                    chunk_id,
                )
                ctx.units = None

        if ctx.units is None:
            current_timeout = config.GROUP_TIMEOUT
            error_feedback = None
            for attempt in range(max_attempts):
                try:
                    controller.acquire()
                    try:
                        er = group_chunk(
                            chunk,
                            ctx.segments,
                            enrich_client,
                            config,
                            error_feedback,
                            timeout_override=current_timeout,
                        )
                    finally:
                        controller.release()

                    verified_units = verify_units(
                        er.teaching_units, ctx.segments, chunk.total_tokens
                    )
                    ctx.units = verified_units
                    if progress is not None:
                        progress.mark_done(chunk_id, "phase2b")
                    break
                except ValidationError:
                    error_feedback = None
                    logger.warning(
                        "[%s] Phase 2b attempt %d/%d: validation error",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                    )
                except ValueError as exc:
                    error_feedback = f"\n\nPrevious output error: {exc}"
                    logger.warning(
                        "[%s] Phase 2b attempt %d/%d: %s",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                        exc,
                    )
                except Exception as exc:
                    error_feedback = None
                    current_timeout = min(
                        int(current_timeout * 1.5),
                        config.GROUP_TIMEOUT * 2,
                    )
                    logger.warning(
                        "[%s] Phase 2b attempt %d/%d: %s",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                        exc,
                    )
                    time.sleep(2**attempt)

            if ctx.units is None:
                ctx.error = "phase2b_failed"
                if progress is not None:
                    progress.mark_failed(chunk_id, "phase2b", "EX-C-002")
                return ctx

        # Phase 3 Deterministic
        ctx.excerpts = build_deterministic_excerpts(
            chunk=chunk,
            units=ctx.units,
            segments=ctx.segments,
        )

        # Phase 3 Enrichment
        if enrich_client is not None:
            if progress is not None and progress.is_done(
                chunk_id, "phase3_enrich"
            ):
                logger.info(
                    "[%s] Phase 3 enrich: skipping (already done)", chunk_id
                )
                ctx.enriched_excerpts = ctx.excerpts
            else:
                current_timeout = config.ENRICH_TIMEOUT
                for attempt in range(max_attempts):
                    try:
                        controller.acquire()
                        try:
                            enrichment = enrich_chunk(
                                chunk,
                                ctx.excerpts,
                                enrich_client,
                                config,
                                source_metadata,
                            )
                        finally:
                            controller.release()

                        ctx.enriched_excerpts = apply_enrichment(
                            ctx.excerpts, enrichment
                        )
                        if progress is not None:
                            progress.mark_done(chunk_id, "phase3_enrich")
                        break
                    except Exception as exc:
                        current_timeout = min(
                            int(current_timeout * 1.5),
                            config.ENRICH_TIMEOUT * 2,
                        )
                        logger.warning(
                            "[%s] Phase 3 enrich attempt %d/%d: %s",
                            chunk_id,
                            attempt + 1,
                            max_attempts,
                            exc,
                        )
                        time.sleep(2**attempt)

                if ctx.enriched_excerpts is None:
                    logger.warning(
                        "[%s] Enrichment failed, using deterministic-only",
                        chunk_id,
                    )
                    ctx.enriched_excerpts = [
                        exc.model_copy(
                            update={
                                "review_flags": [
                                    *exc.review_flags,
                                    "llm_enrichment_failed",
                                ]
                            }
                        )
                        for exc in ctx.excerpts
                    ]
                    if progress is not None:
                        progress.mark_failed(
                            chunk_id, "phase3_enrich", "EX-M-002"
                        )
        else:
            ctx.enriched_excerpts = ctx.excerpts

        # Phase 3 Consensus
        if verify_client is not None and enrich_client is not None:
            if progress is not None and progress.is_done(
                chunk_id, "phase3_consensus"
            ):
                logger.info(
                    "[%s] Phase 3 consensus: skipping (already done)",
                    chunk_id,
                )
                ctx.final_excerpts = ctx.enriched_excerpts
            else:
                any_needs = any(
                    _needs_consensus(e) for e in ctx.enriched_excerpts
                )
                if not any_needs:
                    ctx.final_excerpts = ctx.enriched_excerpts
                    if progress is not None:
                        progress.mark_done(chunk_id, "phase3_consensus")
                else:
                    current_timeout = config.VERIFY_TIMEOUT
                    verification_done = False
                    for attempt in range(max_attempts):
                        try:
                            controller.acquire()
                            try:
                                vr_result = verify_chunk(
                                    chunk,
                                    ctx.enriched_excerpts,
                                    verify_client,
                                    config,
                                    source_metadata,
                                    timeout_override=current_timeout,
                                )
                            finally:
                                controller.release()

                            if vr_result is None:
                                ctx.final_excerpts = ctx.enriched_excerpts
                                verification_done = True
                                break

                            vr_obj, excerpts_with_items = vr_result

                            # Index verification items by item_index
                            vi_by_index: dict[int, Any] = {
                                vi.item_index: vi
                                for vi in vr_obj.items
                            }

                            # Map each excerpt to its verification items
                            excerpt_to_vi: dict[int, list[tuple[Any, str]]] = {}
                            item_index = 0
                            for ewi_exc, ewi_items in excerpts_with_items:
                                vis_list: list[tuple[Any, str]] = []
                                for item in ewi_items:
                                    vi = vi_by_index.get(item_index)
                                    if vi is not None:
                                        vis_list.append(
                                            (vi, item["verification_type"])
                                        )
                                    item_index += 1
                                excerpt_to_vi[ewi_exc.unit_index] = vis_list

                            resolved: list[Any] = []
                            for exc in ctx.enriched_excerpts:
                                vis_for_exc = excerpt_to_vi.get(
                                    exc.unit_index, []
                                )
                                if not vis_for_exc:
                                    resolved.append(exc)
                                    continue

                                vi_list_items = [v[0] for v in vis_for_exc]
                                type_list = [v[1] for v in vis_for_exc]

                                updated, _cr, gate_codes = resolve_consensus(
                                    exc,
                                    vi_list_items,
                                    type_list,
                                    escalation_client,
                                    config,
                                    source_metadata,
                                )

                                if gate_codes:
                                    gate_flags = (
                                        list(updated.gate_flags)
                                        + gate_codes
                                    )
                                    updated = updated.model_copy(
                                        update={"gate_flags": gate_flags}
                                    )

                                additional_gates = check_gate_triggers(
                                    updated,
                                    source_metadata or {},
                                    config,
                                )
                                for gc in additional_gates:
                                    if gc not in (updated.gate_flags or []):
                                        updated = updated.model_copy(
                                            update={
                                                "gate_flags": list(
                                                    updated.gate_flags
                                                )
                                                + [gc]
                                            }
                                        )
                                    ctx.gate_entries.append(
                                        {
                                            "excerpt_id": updated.excerpt_id,
                                            "gate_code": gc,
                                        }
                                    )

                                resolved.append(updated)

                            ctx.final_excerpts = resolved
                            if progress is not None:
                                progress.mark_done(
                                    chunk_id, "phase3_consensus"
                                )
                            verification_done = True
                            break
                        except Exception as exc_err:
                            current_timeout = min(
                                int(current_timeout * 1.5),
                                config.VERIFY_TIMEOUT * 2,
                            )
                            logger.warning(
                                "[%s] Phase 3 consensus attempt %d/%d: %s",
                                chunk_id,
                                attempt + 1,
                                max_attempts,
                                exc_err,
                            )
                            time.sleep(2**attempt)

                    if not verification_done:
                        ctx.final_excerpts = ctx.enriched_excerpts
                        if progress is not None:
                            progress.mark_failed(
                                chunk_id, "phase3_consensus", "EX-M-011"
                            )
        else:
            ctx.final_excerpts = ctx.enriched_excerpts

        ctx.completed = True

    except Exception as exc:
        logger.error(
            "[%s] Unexpected error in pipeline: %s",
            chunk_id,
            exc,
            exc_info=True,
        )
        ctx.error = f"pipeline_error: {exc}"

    return ctx


def run_parallel_pipeline(
    chunks: list[Any],
    config: Any,
    enrich_client_factory: Optional[Callable[[], Any]],
    verify_client_factory: Optional[Callable[[], Any]],
    escalation_client_factory: Optional[Callable[[], Any]],
    progress: Optional[Any] = None,
    cache: Optional[Any] = None,
    source_metadata: Optional[dict[str, str]] = None,
    classified_data: Optional[dict[str, list[Any]]] = None,
    grouped_data: Optional[dict[str, list[Any]]] = None,
) -> tuple[list[Any], list[Any]]:
    """Process all chunks through the full pipeline concurrently.

    Each worker thread gets its own CLIInstructorAdapter instance (F2 fix).
    A shared Semaphore limits total concurrent CLI calls.

    Args:
        chunks: List of AssembledChunk to process.
        config: ExcerptingConfig with CONCURRENCY setting.
        enrich_client_factory: Callable returning a fresh client, or None.
        verify_client_factory: Callable returning a fresh client, or None.
        escalation_client_factory: Callable returning a fresh client, or None.
        progress: Optional ProgressTracker for resume.
        cache: Optional CacheManager for caching.
        source_metadata: Source metadata dict.
        classified_data: Pre-loaded classified data from resume.
        grouped_data: Pre-loaded grouped data from resume.

    Returns:
        (all_excerpts, all_gate_entries)
    """
    concurrency = max(1, config.CONCURRENCY)
    controller = ConcurrencyController(concurrency)

    contexts = [
        ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        for chunk in chunks
    ]

    all_excerpts: list[Any] = []
    all_gates: list[Any] = []
    completed = 0
    failed = 0

    # Thread pool with 2x concurrency for pipeline overlap
    pool_size = min(len(contexts), concurrency * 2)

    logger.info(
        "Starting parallel pipeline: %d chunks, concurrency %d, pool size %d",
        len(contexts),
        concurrency,
        pool_size,
    )

    with ThreadPoolExecutor(max_workers=pool_size) as executor:
        futures: dict[Future[ChunkPipelineContext], ChunkPipelineContext] = {}

        for ctx in contexts:
            future = executor.submit(
                _process_chunk,
                ctx,
                enrich_client_factory() if enrich_client_factory else None,
                verify_client_factory() if verify_client_factory else None,
                (
                    escalation_client_factory()
                    if escalation_client_factory
                    else None
                ),
                config,
                controller,
                progress,
                cache,
                classified_data,
                grouped_data,
                source_metadata,
            )
            futures[future] = ctx

        try:
            for future in as_completed(futures):
                ctx = futures[future]
                try:
                    result_ctx = future.result()
                    if (
                        result_ctx.completed
                        and result_ctx.final_excerpts
                    ):
                        all_excerpts.extend(result_ctx.final_excerpts)
                        all_gates.extend(result_ctx.gate_entries)
                        completed += 1
                    else:
                        failed += 1
                        logger.warning(
                            "Chunk %s failed: %s",
                            result_ctx.chunk_id,
                            result_ctx.error or "unknown",
                        )
                except Exception as exc:
                    failed += 1
                    logger.error(
                        "Chunk %s thread error: %s", ctx.chunk_id, exc
                    )
        except KeyboardInterrupt:
            logger.warning(
                "Pipeline interrupted, waiting for in-flight calls..."
            )
            executor.shutdown(wait=True, cancel_futures=True)
            raise

    logger.info(
        "Parallel pipeline complete: %d/%d chunks succeeded, %d failed",
        completed,
        len(contexts),
        failed,
    )

    return all_excerpts, all_gates
