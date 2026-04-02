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

import datetime
import json
import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

PROGRAMMING_BUG_EXCEPTIONS = (
    TypeError,
    AttributeError,
    NameError,
    KeyError,
    IndexError,
    ZeroDivisionError,
    StopIteration,
)


class CircuitBreaker:
    """Prevents retry storms when CLI backends are down.

    State machine: CLOSED -> OPEN -> HALF_OPEN -> CLOSED (or back to OPEN).
    Thread-safe: all state changes are locked.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        base_cooldown: float = 60.0,
        max_cooldown: float = 1800.0,
    ) -> None:
        self._lock = threading.Lock()
        self._failure_threshold = failure_threshold
        self._base_cooldown = base_cooldown
        self._max_cooldown = max_cooldown
        self._consecutive_failures = 0
        self._state = "CLOSED"
        self._cooldown = base_cooldown
        self._open_since: float = 0.0

    @property
    def state(self) -> str:
        """Current circuit state: CLOSED, OPEN, or HALF_OPEN."""
        with self._lock:
            return self._state

    def record_success(self) -> None:
        """Record a successful call. Resets circuit to CLOSED."""
        with self._lock:
            self._consecutive_failures = 0
            self._state = "CLOSED"
            self._cooldown = self._base_cooldown

    def record_failure(self) -> None:
        """Record a failed call. Opens circuit after threshold failures."""
        with self._lock:
            self._consecutive_failures += 1
            if self._state == "HALF_OPEN":
                self._state = "OPEN"
                self._open_since = time.monotonic()
                self._cooldown = min(
                    self._cooldown * 2, self._max_cooldown
                )
                logger.warning(
                    "Circuit breaker HALF_OPEN -> OPEN, cooldown %.0fs",
                    self._cooldown,
                )
            elif self._consecutive_failures >= self._failure_threshold:
                self._state = "OPEN"
                self._open_since = time.monotonic()
                logger.warning(
                    "Circuit breaker OPEN — %d failures, cooldown %.0fs",
                    self._consecutive_failures,
                    self._cooldown,
                )

    def check(self) -> None:
        """Check circuit state before making a call.

        CLOSED: returns immediately.
        OPEN: blocks until cooldown expires, then transitions to HALF_OPEN.
        HALF_OPEN: returns immediately (one thread probes).

        Does NOT raise — just blocks. The calling code should still make
        the LLM call; the circuit breaker observes the result via
        record_success/record_failure.
        """
        wait_time = 0.0
        with self._lock:
            if self._state == "CLOSED":
                return
            if self._state == "HALF_OPEN":
                return  # Let one thread probe
            # OPEN state
            elapsed = time.monotonic() - self._open_since
            if elapsed >= self._cooldown:
                self._state = "HALF_OPEN"
                logger.info("Circuit breaker -> HALF_OPEN (probing)")
                return
            wait_time = self._cooldown - elapsed

        # Wait OUTSIDE the lock
        logger.info(
            "Circuit breaker OPEN, waiting %.0fs before probe...",
            wait_time,
        )
        time.sleep(wait_time)
        with self._lock:
            if self._state == "OPEN":  # Still open after wait
                self._state = "HALF_OPEN"
                logger.info("Circuit breaker -> HALF_OPEN (probing)")


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


class StatusWriter:
    """Writes pipeline status to a JSON file for external monitoring.

    Updated periodically by a background thread.
    Thread-safe: all state updates are locked.
    """

    def __init__(
        self, status_path: Path, update_interval: float = 30.0
    ) -> None:
        self._path = status_path
        self._interval = update_interval
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._data: dict[str, Any] = {
            "total_chunks": 0,
            "completed": 0,
            "failed": 0,
            "pending": 0,
            "in_progress": {},
            "elapsed_seconds": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        self._start_time = time.monotonic()
        self._thread: Optional[threading.Thread] = None

    def start(self, total_chunks: int) -> None:
        """Start the background writer thread."""
        with self._lock:
            self._data["total_chunks"] = total_chunks
            self._data["pending"] = total_chunks
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background writer and write final status."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        self._write()

    def record_phase_start(self, chunk_id: str, phase: str) -> None:
        """Record that a chunk has started a pipeline phase."""
        with self._lock:
            phases = self._data.setdefault("in_progress", {})
            phases[phase] = phases.get(phase, 0) + 1

    def record_phase_end(self, chunk_id: str, phase: str) -> None:
        """Record that a chunk has finished a pipeline phase."""
        with self._lock:
            phases = self._data.get("in_progress", {})
            if phase in phases:
                phases[phase] = max(0, phases[phase] - 1)

    def record_chunk_complete(self) -> None:
        """Record a successfully completed chunk."""
        with self._lock:
            self._data["completed"] = self._data.get("completed", 0) + 1
            self._data["pending"] = max(
                0, self._data.get("pending", 0) - 1
            )

    def record_chunk_failed(self) -> None:
        """Record a failed chunk."""
        with self._lock:
            self._data["failed"] = self._data.get("failed", 0) + 1
            self._data["pending"] = max(
                0, self._data.get("pending", 0) - 1
            )

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        with self._lock:
            self._data["cache_hits"] = (
                self._data.get("cache_hits", 0) + 1
            )

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        with self._lock:
            self._data["cache_misses"] = (
                self._data.get("cache_misses", 0) + 1
            )

    def _run(self) -> None:
        """Background thread: write status every N seconds."""
        while not self._stop.wait(timeout=self._interval):
            self._write()

    def _write(self) -> None:
        """Write current status to file."""
        with self._lock:
            elapsed = time.monotonic() - self._start_time
            self._data["elapsed_seconds"] = round(elapsed, 1)
            self._data["updated"] = datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat()
            completed = self._data.get("completed", 0)
            if completed > 0:
                avg = elapsed / completed
                self._data["avg_seconds_per_chunk"] = round(avg, 1)
                remaining = self._data.get("pending", 0)
                self._data["estimated_remaining_seconds"] = round(
                    avg * remaining, 1
                )
            snapshot = dict(self._data)

        try:
            # Write to temp then rename for atomic update
            tmp = self._path.with_suffix(".json.tmp")
            tmp.write_text(
                json.dumps(snapshot, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            tmp.replace(self._path)
        except OSError as exc:
            logger.debug("Status write failed: %s", exc)


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
    breaker: Optional[CircuitBreaker] = None,
    status_writer: Optional[StatusWriter] = None,
) -> ChunkPipelineContext:
    """Run the full pipeline for one chunk. Called in its own thread.

    Uses the Semaphore only around LLM calls.
    Returns the updated context with results or error.
    """
    from pydantic import ValidationError  # pyright: ignore[reportMissingImports]

    from engines.excerpting.src.phase2_classify import (
        classify_chunk,
        normalize_offsets,
        verify_segments,
    )
    from engines.excerpting.src.phase2_group import group_chunk, verify_units
    from engines.excerpting.src.phase3_consensus import (
        _build_gate_entry,
        _needs_consensus,
        check_gate_triggers,
        resolve_consensus,
        verify_chunk,
    )
    from engines.excerpting.src.phase3_deterministic import (
        build_deterministic_excerpts,
    )
    from engines.excerpting.src.phase3_enrichment import (
        ENRICH_SYSTEM_PROMPT,
        EnrichmentBatchCoverageError,
        _build_enrichment_user_message,
        _compute_enrich_max_tokens,
        apply_enrichment,
        enrich_chunk,
    )
    from engines.excerpting.src.phase3_consensus import (
        VERIFY_SYSTEM_PROMPT,
        _build_verification_user_message,
    )
    from engines.excerpting.src.cache import compute_cache_key
    from engines.excerpting.contracts import EnrichmentResult, VerificationResult

    chunk = ctx.chunk
    chunk_id = ctx.chunk_id
    max_attempts = 1 + config.RETRY_COUNT
    active_phase = "phase2"

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
                    if breaker is not None:
                        breaker.check()
                    if status_writer is not None:
                        status_writer.record_phase_start(
                            chunk_id, "phase2a"
                        )
                    controller.acquire()
                    try:
                        cr = classify_chunk(
                            chunk,
                            enrich_client,
                            config,
                            error_feedback,
                            timeout_override=current_timeout,
                        )
                        if breaker is not None:
                            breaker.record_success()
                    finally:
                        controller.release()
                        if status_writer is not None:
                            status_writer.record_phase_end(
                                chunk_id, "phase2a"
                            )

                    canonical = normalize_offsets(
                        cr.segments, chunk.assembled_text, chunk.total_tokens
                    )
                    verify_segments(canonical, chunk.total_tokens)
                    ctx.segments = canonical
                    if progress is not None:
                        progress.mark_done(chunk_id, "phase2a")
                    break
                except ValidationError:
                    if breaker is not None:
                        breaker.record_failure()
                    error_feedback = None
                    logger.warning(
                        "[%s] Phase 2a attempt %d/%d: validation error",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                    )
                except ValueError as exc:
                    if breaker is not None:
                        breaker.record_failure()
                    error_feedback = f"\n\nPrevious output error: {exc}"
                    logger.warning(
                        "[%s] Phase 2a attempt %d/%d: %s",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                        exc,
                    )
                except Exception as exc:
                    if breaker is not None:
                        breaker.record_failure()
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
                    if breaker is not None:
                        breaker.check()
                    if status_writer is not None:
                        status_writer.record_phase_start(
                            chunk_id, "phase2b"
                        )
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
                        if breaker is not None:
                            breaker.record_success()
                    finally:
                        controller.release()
                        if status_writer is not None:
                            status_writer.record_phase_end(
                                chunk_id, "phase2b"
                            )

                    verified_units = verify_units(
                        er.teaching_units, ctx.segments, chunk.total_tokens
                    )
                    ctx.units = verified_units
                    if progress is not None:
                        progress.mark_done(chunk_id, "phase2b")
                    break
                except ValidationError:
                    if breaker is not None:
                        breaker.record_failure()
                    error_feedback = None
                    logger.warning(
                        "[%s] Phase 2b attempt %d/%d: validation error",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                    )
                except ValueError as exc:
                    if breaker is not None:
                        breaker.record_failure()
                    error_feedback = f"\n\nPrevious output error: {exc}"
                    logger.warning(
                        "[%s] Phase 2b attempt %d/%d: %s",
                        chunk_id,
                        attempt + 1,
                        max_attempts,
                        exc,
                    )
                except Exception as exc:
                    if breaker is not None:
                        breaker.record_failure()
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
        active_phase = "phase3_deterministic"
        ctx.excerpts = build_deterministic_excerpts(
            chunk=chunk,
            units=ctx.units,
            segments=ctx.segments,
        )

        # Phase 3 Enrichment
        if enrich_client is not None:
            active_phase = "phase3_enrich"
            is_enrich_resume = (
                progress is not None and progress.is_done(chunk_id, "phase3_enrich")
            )
            enrich_cache_key = ""
            cached_enrichment: Optional[EnrichmentResult] = None
            if cache is not None:
                enrich_user_message = _build_enrichment_user_message(
                    chunk,
                    ctx.excerpts,
                    source_metadata or {},
                )
                enrich_cache_key = compute_cache_key(
                    "enrich",
                    ENRICH_SYSTEM_PROMPT,
                    enrich_user_message,
                    config.ENRICH_MODEL,
                    config.LLM_TEMPERATURE,
                    _compute_enrich_max_tokens(chunk.word_count),
                )
                cached_enrichment = cache.load(
                    "enrich",
                    enrich_cache_key,
                    EnrichmentResult,
                )

            if cached_enrichment is not None:
                try:
                    logger.info(
                        "[%s] Phase 3 enrich: cache hit%s",
                        chunk_id,
                        " (resume)" if is_enrich_resume else "",
                    )
                    ctx.enriched_excerpts = apply_enrichment(
                        ctx.excerpts,
                        cached_enrichment,
                    )
                except EnrichmentBatchCoverageError as exc:
                    logger.error(
                        "%s: [%s] Cached enrichment batch failed coverage validation: %s",
                        "EX-M-002",
                        chunk_id,
                        exc,
                    )
                    if is_enrich_resume:
                        ctx.enriched_excerpts = [
                            ex.model_copy(
                                update={
                                    "review_flags": [
                                        *list(ex.review_flags or []),
                                        *(
                                            []
                                            if "llm_enrichment_failed" in (ex.review_flags or [])
                                            else ["llm_enrichment_failed"]
                                        ),
                                    ]
                                }
                            )
                            for ex in ctx.excerpts
                        ]
                        if progress is not None:
                            progress.mark_failed(chunk_id, "phase3_enrich", "EX-M-002")
                    else:
                        cached_enrichment = None
                else:
                    if progress is not None:
                        progress.mark_done(chunk_id, "phase3_enrich")
            elif is_enrich_resume:
                logger.error(
                    "%s: [%s] Phase 3 enrich was marked done but cache is missing. "
                    "Keeping deterministic-only fields with llm_enrichment_failed.",
                    "EX-M-002",
                    chunk_id,
                )
                ctx.enriched_excerpts = [
                    exc.model_copy(
                        update={
                            "review_flags": [
                                *list(exc.review_flags or []),
                                *(
                                    []
                                    if "llm_enrichment_failed" in (exc.review_flags or [])
                                    else ["llm_enrichment_failed"]
                                ),
                            ]
                        }
                    )
                    for exc in ctx.excerpts
                ]
                if progress is not None:
                    progress.mark_failed(chunk_id, "phase3_enrich", "EX-M-002")
            else:
                current_timeout = config.ENRICH_TIMEOUT
                for attempt in range(max_attempts):
                    try:
                        if breaker is not None:
                            breaker.check()
                        if status_writer is not None:
                            status_writer.record_phase_start(
                                chunk_id, "phase3_enrich"
                            )
                        controller.acquire()
                        try:
                            enrichment = enrich_chunk(
                                chunk,
                                ctx.excerpts,
                                enrich_client,
                                config,
                                source_metadata,
                                timeout_override=current_timeout,
                            )
                            if breaker is not None:
                                breaker.record_success()
                        finally:
                            controller.release()
                            if status_writer is not None:
                                status_writer.record_phase_end(
                                    chunk_id, "phase3_enrich"
                                )

                        ctx.enriched_excerpts = apply_enrichment(
                            ctx.excerpts, enrichment
                        )
                        if cache is not None and enrich_cache_key:
                            cache.save(
                                "enrich",
                                enrich_cache_key,
                                chunk_id,
                                config.ENRICH_MODEL,
                                enrichment,
                            )
                        if progress is not None:
                            progress.mark_done(chunk_id, "phase3_enrich")
                        break
                    except Exception as exc:
                        if isinstance(exc, PROGRAMMING_BUG_EXCEPTIONS):
                            raise
                        if breaker is not None:
                            breaker.record_failure()
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

        assert ctx.enriched_excerpts is not None

        # Phase 3 Consensus
        if verify_client is not None:
            is_consensus_resume = (
                progress is not None and progress.is_done(chunk_id, "phase3_consensus")
            )
            any_needs = any(
                _needs_consensus(e) for e in ctx.enriched_excerpts
            )
            if not any_needs:
                ctx.final_excerpts = ctx.enriched_excerpts
                if progress is not None:
                    progress.mark_done(chunk_id, "phase3_consensus")
            else:
                excerpts_with_items_for_cache: list[tuple[Any, list[dict[str, str]]]] = []
                for exc in ctx.enriched_excerpts:
                    items = _needs_consensus(exc)
                    if items:
                        excerpts_with_items_for_cache.append((exc, items))

                verify_cache_key = ""
                cached_vr: Optional[VerificationResult] = None
                if cache is not None and excerpts_with_items_for_cache:
                    verify_user_message = _build_verification_user_message(
                        excerpts_with_items_for_cache,
                        source_metadata or {},
                    )
                    verify_cache_key = compute_cache_key(
                        "verify",
                        VERIFY_SYSTEM_PROMPT,
                        verify_user_message,
                        config.VERIFY_MODEL,
                        config.LLM_TEMPERATURE,
                        config.VERIFY_MAX_TOKENS,
                    )
                    cached_vr = cache.load(
                        "verify",
                        verify_cache_key,
                        VerificationResult,
                    )

                verification_result = None
                verification_done = False
                if cached_vr is not None:
                    logger.info(
                        "[%s] Phase 3 consensus: cache hit%s",
                        chunk_id,
                        " (resume)" if is_consensus_resume else "",
                    )
                    verification_result = (
                        cached_vr,
                        excerpts_with_items_for_cache,
                    )
                    verification_done = True
                elif is_consensus_resume:
                    logger.error(
                        "%s: [%s] Phase 3 consensus was marked done but cache is missing. "
                        "Passing through with verification_skipped.",
                        "EX-M-011",
                        chunk_id,
                    )
                    ctx.final_excerpts = [
                        exc.model_copy(
                            update={
                                "review_flags": [
                                    *list(exc.review_flags or []),
                                    *(
                                        []
                                        if "verification_skipped" in (exc.review_flags or [])
                                        else ["verification_skipped"]
                                    ),
                                ]
                            }
                        )
                        for exc in ctx.enriched_excerpts
                    ]
                    if progress is not None:
                        progress.mark_failed(chunk_id, "phase3_consensus", "EX-M-011")
                    verification_done = True
                else:
                    active_phase = "phase3_consensus"
                    current_timeout = config.VERIFY_TIMEOUT
                    for attempt in range(max_attempts):
                        try:
                            if breaker is not None:
                                breaker.check()
                            if status_writer is not None:
                                status_writer.record_phase_start(
                                    chunk_id, "phase3_consensus"
                                )
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
                                if breaker is not None:
                                    breaker.record_success()
                            finally:
                                controller.release()
                                if status_writer is not None:
                                    status_writer.record_phase_end(
                                        chunk_id, "phase3_consensus"
                                    )

                            if vr_result is None:
                                ctx.final_excerpts = ctx.enriched_excerpts
                                verification_done = True
                                break

                            if cache is not None and verify_cache_key:
                                cache.save(
                                    "verify",
                                    verify_cache_key,
                                    chunk_id,
                                    config.VERIFY_MODEL,
                                    vr_result[0],
                                )

                            verification_result = (
                                vr_result[0],
                                vr_result[1],
                            )
                            verification_done = True
                            break

                        except Exception as exc_err:
                            if isinstance(exc_err, PROGRAMMING_BUG_EXCEPTIONS):
                                raise
                            if breaker is not None:
                                breaker.record_failure()
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

                if verification_result is not None:
                    vr_obj, excerpts_with_items = verification_result

                    # Index verification items by item_index
                    vi_by_index: dict[int, Any] = {
                        vi.item_index: vi
                        for vi in vr_obj.items
                    }

                    # Map each excerpt to its verification items
                    excerpt_to_vi: dict[int, list[tuple[Any, str]]] = {}
                    excerpt_expected_counts: dict[int, int] = {}
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
                        excerpt_expected_counts[ewi_exc.unit_index] = len(ewi_items)

                    resolved: list[Any] = []
                    chunk_had_verification_failure = False
                    units_needing_verification = set(excerpt_expected_counts)
                    for exc in ctx.enriched_excerpts:
                        vis_for_exc = excerpt_to_vi.get(
                            exc.unit_index, []
                        )
                        expected_count = excerpt_expected_counts.get(exc.unit_index, 0)
                        if exc.unit_index in units_needing_verification and (
                            not vis_for_exc or len(vis_for_exc) != expected_count
                        ):
                            chunk_had_verification_failure = True
                            if progress is not None:
                                progress.mark_failed(chunk_id, "phase3_consensus", "EX-M-011")
                            degraded = exc.model_copy(
                                update={
                                    "review_flags": [
                                        *list(exc.review_flags or []),
                                        *(
                                            []
                                            if "verification_skipped" in (exc.review_flags or [])
                                            else ["verification_skipped"]
                                        ),
                                    ]
                                }
                            )
                            resolved.append(degraded)
                            continue

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
                            for gc in gate_codes:
                                ctx.gate_entries.append(
                                    _build_gate_entry(
                                        updated,
                                            gc,
                                        source_metadata or {},
                                    )
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
                                _build_gate_entry(
                                    updated,
                                    gc,
                                    source_metadata or {},
                                )
                            )

                        resolved.append(updated)

                    ctx.final_excerpts = resolved
                    if progress is not None and not chunk_had_verification_failure:
                        progress.mark_done(
                            chunk_id, "phase3_consensus"
                        )
                if not verification_done:
                    ctx.final_excerpts = [
                        exc.model_copy(
                            update={
                                "review_flags": [
                                    *list(exc.review_flags or []),
                                    *(
                                        []
                                        if "verification_skipped" in (exc.review_flags or [])
                                        else ["verification_skipped"]
                                    ),
                                ]
                            }
                        )
                        for exc in ctx.enriched_excerpts
                    ]
                    if progress is not None:
                        progress.mark_failed(
                            chunk_id, "phase3_consensus", "EX-M-011"
                        )
        else:
            ctx.final_excerpts = ctx.enriched_excerpts

        ctx.completed = True

    except Exception as exc:
        if isinstance(exc, PROGRAMMING_BUG_EXCEPTIONS) or (
            active_phase == "phase3_deterministic" and isinstance(exc, ValueError)
        ):
            raise
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
    output_dir: Optional[Path] = None,
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
        output_dir: Optional directory for status.json monitoring file.

    Returns:
        (all_excerpts, all_gate_entries)
    """
    concurrency = max(1, config.CONCURRENCY)
    controller = ConcurrencyController(concurrency)
    breaker = CircuitBreaker() if concurrency > 1 else None

    status_writer: Optional[StatusWriter] = None
    if output_dir is not None:
        status_writer = StatusWriter(output_dir / "status.json")

    contexts = [
        ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        for chunk in chunks
    ]

    if status_writer is not None:
        status_writer.start(len(contexts))

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
                breaker,
                status_writer,
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
                        if status_writer is not None:
                            status_writer.record_chunk_complete()
                    else:
                        failed += 1
                        if status_writer is not None:
                            status_writer.record_chunk_failed()
                        logger.warning(
                            "Chunk %s failed: %s",
                            result_ctx.chunk_id,
                            result_ctx.error or "unknown",
                        )
                except Exception as exc:
                    if isinstance(exc, PROGRAMMING_BUG_EXCEPTIONS + (ValueError,)):
                        raise
                    failed += 1
                    if status_writer is not None:
                        status_writer.record_chunk_failed()
                    logger.error(
                        "Chunk %s thread error: %s", ctx.chunk_id, exc
                    )
        except KeyboardInterrupt:
            logger.warning(
                "Pipeline interrupted, waiting for in-flight calls..."
            )
            executor.shutdown(wait=True, cancel_futures=True)
            if status_writer is not None:
                status_writer.stop()
            raise

    if status_writer is not None:
        status_writer.stop()

    logger.info(
        "Parallel pipeline complete: %d/%d chunks succeeded, %d failed",
        completed,
        len(contexts),
        failed,
    )

    # Re-sort to deterministic order (Codex review F5: as_completed returns
    # completion order, not chunk order). Sort by (div_id, chunk_index, unit_index)
    # to match the sequential pipeline's output ordering.
    try:
        all_excerpts.sort(
            key=lambda e: (
                str(getattr(e, "div_id", "")),
                int(getattr(e, "chunk_index", 0) or 0),
                int(getattr(e, "unit_index", 0) or 0),
            )
        )
    except (TypeError, ValueError):
        pass  # Non-sortable items (e.g. mocks in tests) — keep insertion order

    return all_excerpts, all_gates
