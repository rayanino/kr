"""Tests for the parallel chunk pipeline orchestrator.

Tests verify orchestration logic using mock clients — no actual CLI/LLM calls.
"""
from __future__ import annotations

import threading
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from engines.excerpting.src.parallel_orchestrator import (
    ChunkPipelineContext,
    ConcurrencyController,
    _process_chunk,
    run_parallel_pipeline,
)


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════


def _make_mock_config(**overrides: Any) -> MagicMock:
    """Create a mock ExcerptingConfig with sensible defaults."""
    config = MagicMock()
    config.CONCURRENCY = overrides.get("CONCURRENCY", 2)
    config.RETRY_COUNT = overrides.get("RETRY_COUNT", 0)
    config.CLASSIFY_TIMEOUT = overrides.get("CLASSIFY_TIMEOUT", 30)
    config.GROUP_TIMEOUT = overrides.get("GROUP_TIMEOUT", 30)
    config.ENRICH_TIMEOUT = overrides.get("ENRICH_TIMEOUT", 30)
    config.VERIFY_TIMEOUT = overrides.get("VERIFY_TIMEOUT", 30)
    config.CLASSIFY_MODEL = "test/model"
    config.GROUP_MODEL = "test/model"
    config.ENRICH_MODEL = "test/model"
    config.VERIFY_MODEL = "test/model"
    config.LLM_TEMPERATURE = 0.0
    config.GROUP_MAX_TOKENS = 8192
    config.ENRICH_MAX_TOKENS = 8192
    config.VERIFY_MAX_TOKENS = 4096
    return config


def _make_mock_chunk(chunk_id: str = "chunk_0") -> MagicMock:
    """Create a mock AssembledChunk."""
    chunk = MagicMock()
    chunk.chunk_id = chunk_id
    chunk.source_id = "src_test"
    chunk.div_id = "div_test"
    chunk.assembled_text = "بسم الله الرحمن الرحيم الحمد لله رب العالمين"
    chunk.total_tokens = 7
    chunk.word_count = 7
    chunk.structural_format = MagicMock()
    chunk.structural_format.value = "PROSE"
    chunk.split_info = None
    return chunk


def _make_mock_segment() -> MagicMock:
    """Create a mock ClassifiedSegment."""
    seg = MagicMock()
    seg.segment_index = 0
    seg.start_word = 0
    seg.end_word = 6
    seg.text_snippet = "بسم الله الرحمن الرحيم الحمد"
    return seg


def _make_mock_unit() -> MagicMock:
    """Create a mock TeachingUnit."""
    unit = MagicMock()
    unit.unit_index = 0
    unit.segment_indices = [0]
    unit.start_word = 0
    unit.end_word = 6
    return unit


def _make_mock_excerpt() -> MagicMock:
    """Create a mock ExcerptRecord."""
    exc = MagicMock()
    exc.excerpt_id = "exc_test_0"
    exc.school = None
    exc.review_flags = []
    exc.model_copy = MagicMock(return_value=exc)
    return exc


# ═══════════════════════════════════════════════════════════════════
# ConcurrencyController tests
# ═══════════════════════════════════════════════════════════════════


class TestConcurrencyController:
    """Tests for ConcurrencyController semaphore logic."""

    def test_concurrency_controller_limits(self) -> None:
        """Semaphore limits concurrent access to max_concurrent."""
        controller = ConcurrencyController(2)
        acquired_count = 0
        barrier = threading.Barrier(3, timeout=5)
        results: list[bool] = []

        def worker() -> None:
            nonlocal acquired_count
            controller.acquire()
            acquired_count += 1
            try:
                barrier.wait(timeout=2)
            except threading.BrokenBarrierError:
                pass
            results.append(True)
            controller.release()

        # Launch 3 threads with concurrency limit of 2
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()

        # Give threads time to acquire
        time.sleep(0.3)
        # At most 2 should have acquired at this point
        assert controller.active_count <= 2

        for t in threads:
            t.join(timeout=10)

        # All 3 eventually completed
        assert len(results) == 3

    def test_concurrency_controller_active_count(self) -> None:
        """active_count tracks correctly through acquire/release."""
        controller = ConcurrencyController(3)
        assert controller.active_count == 0

        controller.acquire()
        assert controller.active_count == 1

        controller.acquire()
        assert controller.active_count == 2

        controller.release()
        assert controller.active_count == 1

        controller.release()
        assert controller.active_count == 0


# ═══════════════════════════════════════════════════════════════════
# ChunkPipelineContext tests
# ═══════════════════════════════════════════════════════════════════


class TestChunkPipelineContext:
    """Tests for ChunkPipelineContext dataclass."""

    def test_chunk_pipeline_context_defaults(self) -> None:
        """Dataclass defaults are all None/empty/False."""
        chunk = _make_mock_chunk()
        ctx = ChunkPipelineContext(chunk=chunk, chunk_id="test_0")

        assert ctx.chunk is chunk
        assert ctx.chunk_id == "test_0"
        assert ctx.segments is None
        assert ctx.units is None
        assert ctx.excerpts is None
        assert ctx.enriched_excerpts is None
        assert ctx.final_excerpts is None
        assert ctx.gate_entries == []
        assert ctx.error is None
        assert ctx.completed is False


# ═══════════════════════════════════════════════════════════════════
# _process_chunk tests
# ═══════════════════════════════════════════════════════════════════


class TestProcessChunk:
    """Tests for the per-chunk worker function."""

    @patch("engines.excerpting.src.phase3_enrichment.enrich_chunk")
    @patch("engines.excerpting.src.phase3_enrichment.apply_enrichment")
    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_success_mock(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_build_det: MagicMock,
        mock_apply_enrich: MagicMock,
        mock_enrich: MagicMock,
    ) -> None:
        """Full pipeline produces results when all phases succeed."""
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=0)
        controller = ConcurrencyController(2)

        # Set up return values
        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpts = [_make_mock_excerpt()]

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units

        mock_build_det.return_value = excerpts
        mock_enrich.return_value = MagicMock()
        mock_apply_enrich.return_value = excerpts

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=None,
            escalation_client=None,
            config=config,
            controller=controller,
            progress=None,
            cache=None,
            classified_data=None,
            grouped_data=None,
            source_metadata=None,
        )

        assert result.completed is True
        assert result.error is None
        assert result.final_excerpts is not None
        assert len(result.final_excerpts) == 1

    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_classify_failure(
        self,
        mock_classify: MagicMock,
    ) -> None:
        """Phase 2a failure produces error, not crash."""
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=0)
        controller = ConcurrencyController(2)
        mock_classify.side_effect = ValueError("bad LLM output")

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=None,
            escalation_client=None,
            config=config,
            controller=controller,
            progress=None,
            cache=None,
            classified_data=None,
            grouped_data=None,
            source_metadata=None,
        )

        assert result.completed is False
        assert result.error == "phase2a_failed"
        assert result.final_excerpts is None


# ═══════════════════════════════════════════════════════════════════
# run_parallel_pipeline tests
# ═══════════════════════════════════════════════════════════════════


class TestRunParallelPipeline:
    """Tests for the main parallel pipeline entry point."""

    @patch("engines.excerpting.src.parallel_orchestrator._process_chunk")
    def test_run_parallel_pipeline_basic(
        self, mock_process: MagicMock
    ) -> None:
        """3 chunks at concurrency 2: all processed, results aggregated."""
        chunks = [_make_mock_chunk(f"chunk_{i}") for i in range(3)]
        config = _make_mock_config(CONCURRENCY=2)

        mock_excerpt = _make_mock_excerpt()

        def side_effect(
            ctx: Any, *args: Any, **kwargs: Any
        ) -> ChunkPipelineContext:
            ctx.completed = True
            ctx.final_excerpts = [mock_excerpt]
            ctx.gate_entries = []
            return ctx

        mock_process.side_effect = side_effect

        factory = MagicMock(return_value=MagicMock())
        excerpts, gates = run_parallel_pipeline(
            chunks=chunks,
            config=config,
            enrich_client_factory=factory,
            verify_client_factory=factory,
            escalation_client_factory=factory,
        )

        assert len(excerpts) == 3
        assert len(gates) == 0
        assert mock_process.call_count == 3

    @patch("engines.excerpting.src.parallel_orchestrator._process_chunk")
    def test_run_parallel_pipeline_sequential(
        self, mock_process: MagicMock
    ) -> None:
        """Concurrency 1: same behavior as sequential."""
        chunks = [_make_mock_chunk("chunk_0")]
        config = _make_mock_config(CONCURRENCY=1)

        mock_excerpt = _make_mock_excerpt()

        def side_effect(
            ctx: Any, *args: Any, **kwargs: Any
        ) -> ChunkPipelineContext:
            ctx.completed = True
            ctx.final_excerpts = [mock_excerpt]
            ctx.gate_entries = []
            return ctx

        mock_process.side_effect = side_effect

        factory = MagicMock(return_value=MagicMock())
        excerpts, _gates = run_parallel_pipeline(
            chunks=chunks,
            config=config,
            enrich_client_factory=factory,
            verify_client_factory=factory,
            escalation_client_factory=factory,
        )

        assert len(excerpts) == 1
        assert mock_process.call_count == 1

    @patch("engines.excerpting.src.parallel_orchestrator._process_chunk")
    def test_run_parallel_pipeline_with_progress(
        self, mock_process: MagicMock
    ) -> None:
        """Progress tracker is forwarded to each chunk worker."""
        chunks = [_make_mock_chunk("chunk_0")]
        config = _make_mock_config(CONCURRENCY=1)
        progress = MagicMock()

        def side_effect(
            ctx: Any, *args: Any, **kwargs: Any
        ) -> ChunkPipelineContext:
            ctx.completed = True
            ctx.final_excerpts = [_make_mock_excerpt()]
            ctx.gate_entries = []
            return ctx

        mock_process.side_effect = side_effect

        factory = MagicMock(return_value=MagicMock())
        run_parallel_pipeline(
            chunks=chunks,
            config=config,
            enrich_client_factory=factory,
            verify_client_factory=factory,
            escalation_client_factory=factory,
            progress=progress,
        )

        # Progress was passed to _process_chunk
        call_args = mock_process.call_args
        # progress is the 7th positional arg (index 6)
        assert call_args[0][6] is progress

    def test_per_thread_client_isolation(self) -> None:
        """Each thread gets its own client (factory called N times)."""
        chunks = [_make_mock_chunk(f"chunk_{i}") for i in range(3)]
        config = _make_mock_config(CONCURRENCY=3)

        enrich_factory = MagicMock(return_value=MagicMock())
        verify_factory = MagicMock(return_value=MagicMock())
        escalation_factory = MagicMock(return_value=MagicMock())

        with patch(
            "engines.excerpting.src.parallel_orchestrator._process_chunk"
        ) as mock_process:

            def side_effect(
                ctx: Any, *args: Any, **kwargs: Any
            ) -> ChunkPipelineContext:
                ctx.completed = True
                ctx.final_excerpts = [_make_mock_excerpt()]
                ctx.gate_entries = []
                return ctx

            mock_process.side_effect = side_effect

            run_parallel_pipeline(
                chunks=chunks,
                config=config,
                enrich_client_factory=enrich_factory,
                verify_client_factory=verify_factory,
                escalation_client_factory=escalation_factory,
            )

        # Each factory called once per chunk = 3 times
        assert enrich_factory.call_count == 3
        assert verify_factory.call_count == 3
        assert escalation_factory.call_count == 3

    @patch("engines.excerpting.src.parallel_orchestrator._process_chunk")
    def test_run_parallel_pipeline_handles_failed_chunks(
        self, mock_process: MagicMock
    ) -> None:
        """Failed chunks counted in results, don't crash the pipeline."""
        chunks = [_make_mock_chunk(f"chunk_{i}") for i in range(2)]
        config = _make_mock_config(CONCURRENCY=2)

        call_count = {"n": 0}

        def side_effect(
            ctx: Any, *args: Any, **kwargs: Any
        ) -> ChunkPipelineContext:
            call_count["n"] += 1
            if call_count["n"] == 1:
                # First chunk succeeds
                ctx.completed = True
                ctx.final_excerpts = [_make_mock_excerpt()]
                ctx.gate_entries = []
            else:
                # Second chunk fails
                ctx.completed = False
                ctx.error = "phase2a_failed"
            return ctx

        mock_process.side_effect = side_effect

        factory = MagicMock(return_value=MagicMock())
        excerpts, _gates = run_parallel_pipeline(
            chunks=chunks,
            config=config,
            enrich_client_factory=factory,
            verify_client_factory=factory,
            escalation_client_factory=factory,
        )

        # Only the successful chunk's excerpts are included
        assert len(excerpts) == 1

    @patch("engines.excerpting.src.parallel_orchestrator._process_chunk")
    def test_keyboard_interrupt_cleanup(
        self, mock_process: MagicMock
    ) -> None:
        """KeyboardInterrupt triggers graceful shutdown."""
        chunks = [_make_mock_chunk(f"chunk_{i}") for i in range(3)]
        config = _make_mock_config(CONCURRENCY=1)

        mock_process.side_effect = KeyboardInterrupt("test interrupt")

        factory = MagicMock(return_value=MagicMock())
        with pytest.raises(KeyboardInterrupt):
            run_parallel_pipeline(
                chunks=chunks,
                config=config,
                enrich_client_factory=factory,
                verify_client_factory=factory,
                escalation_client_factory=factory,
            )

    def test_null_client_factories(self) -> None:
        """None factories produce None clients without crashing."""
        chunks = [_make_mock_chunk("chunk_0")]
        config = _make_mock_config(CONCURRENCY=1)

        with patch(
            "engines.excerpting.src.parallel_orchestrator._process_chunk"
        ) as mock_process:

            def side_effect(
                ctx: Any, *args: Any, **kwargs: Any
            ) -> ChunkPipelineContext:
                ctx.completed = True
                ctx.final_excerpts = [_make_mock_excerpt()]
                ctx.gate_entries = []
                return ctx

            mock_process.side_effect = side_effect

            excerpts, _gates = run_parallel_pipeline(
                chunks=chunks,
                config=config,
                enrich_client_factory=None,
                verify_client_factory=None,
                escalation_client_factory=None,
            )

        assert len(excerpts) == 1
        # Verify None was passed for all three client args
        call_args = mock_process.call_args[0]
        assert call_args[1] is None  # enrich_client
        assert call_args[2] is None  # verify_client
        assert call_args[3] is None  # escalation_client
