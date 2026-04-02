"""Tests for the parallel chunk pipeline orchestrator.

Tests verify orchestration logic using mock clients — no actual CLI/LLM calls.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from engines.excerpting.contracts import (
    EnrichmentResult,
    SelfContainmentLevel,
    VerificationItem,
    VerificationResult,
)
from engines.excerpting.src.parallel_orchestrator import (
    ChunkPipelineContext,
    CircuitBreaker,
    ConcurrencyController,
    StatusWriter,
    _process_chunk,
    run_parallel_pipeline,
)
from engines.excerpting.tests.conftest import _make_excerpt_record


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


def _mock_consensus_item() -> dict[str, str]:
    """Minimal consensus item matching the real prompt builder shape."""
    return {
        "verification_type": "SCHOOL_ATTRIBUTION",
        "decision_text": 'School attributed as "حنبلي". Is this correct given the text content?',
        "unit_text": "بسم الله الرحمن الرحيم الحمد لله رب العالمين",
        "scholarly_function": "definition",
        "school_confidence": "0.9",
    }


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
    @patch("engines.excerpting.src.phase3_consensus.verify_chunk")
    @patch("engines.excerpting.src.phase3_consensus._needs_consensus")
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
        mock_needs_consensus: MagicMock,
        mock_verify_chunk: MagicMock,
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
        mock_needs_consensus.return_value = []
        mock_verify_chunk.return_value = None

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

    @patch("engines.excerpting.src.phase3_enrichment.enrich_chunk")
    @patch("engines.excerpting.src.phase3_enrichment.apply_enrichment")
    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase3_consensus.verify_chunk")
    @patch("engines.excerpting.src.phase3_consensus._needs_consensus")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_marks_verification_skipped_when_consensus_exhausted(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_needs_consensus: MagicMock,
        mock_verify_chunk: MagicMock,
        mock_build_det: MagicMock,
        mock_apply_enrich: MagicMock,
        mock_enrich: MagicMock,
    ) -> None:
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=1)
        controller = ConcurrencyController(2)

        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpt = _make_mock_excerpt()
        excerpt.unit_index = 0

        def clone_with_update(*, update: dict[str, Any]) -> MagicMock:
            clone = _make_mock_excerpt()
            clone.unit_index = excerpt.unit_index
            clone.review_flags = update.get("review_flags", excerpt.review_flags)
            clone.model_copy.side_effect = lambda *, update: clone_with_update(update=update)
            return clone

        excerpt.model_copy.side_effect = lambda *, update: clone_with_update(update=update)

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units
        mock_needs_consensus.return_value = [_mock_consensus_item()]
        mock_verify_chunk.side_effect = RuntimeError("verify boom")

        mock_build_det.return_value = [excerpt]
        mock_enrich.return_value = MagicMock()
        mock_apply_enrich.return_value = [excerpt]

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=MagicMock(),
            escalation_client=MagicMock(),
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
        assert result.final_excerpts[0].review_flags == ["verification_skipped"]

    @patch("engines.excerpting.src.phase3_enrichment.enrich_chunk")
    @patch("engines.excerpting.src.phase3_enrichment.apply_enrichment")
    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase3_consensus.verify_chunk")
    @patch("engines.excerpting.src.phase3_consensus._needs_consensus")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_preserves_existing_verification_skipped_flag_and_marks_progress_failed(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_needs_consensus: MagicMock,
        mock_verify_chunk: MagicMock,
        mock_build_det: MagicMock,
        mock_apply_enrich: MagicMock,
        mock_enrich: MagicMock,
    ) -> None:
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=1)
        controller = ConcurrencyController(2)
        progress = MagicMock()
        progress.is_done.return_value = False

        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpt = _make_mock_excerpt()
        excerpt.unit_index = 0
        excerpt.review_flags = ["verification_skipped"]

        def _clone_with(update: dict[str, Any]) -> MagicMock:
            clone = _make_mock_excerpt()
            clone.unit_index = excerpt.unit_index
            clone.review_flags = update.get("review_flags", excerpt.review_flags)
            clone.model_copy.side_effect = lambda update: _clone_with(update)
            return clone

        excerpt.model_copy.side_effect = lambda update: _clone_with(update)

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units
        mock_needs_consensus.return_value = [_mock_consensus_item()]
        mock_verify_chunk.side_effect = RuntimeError("verify boom")

        mock_build_det.return_value = [excerpt]
        mock_enrich.return_value = MagicMock()
        mock_apply_enrich.return_value = [excerpt]

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=MagicMock(),
            escalation_client=MagicMock(),
            config=config,
            controller=controller,
            progress=progress,
            cache=None,
            classified_data=None,
            grouped_data=None,
            source_metadata=None,
        )

        assert result.final_excerpts is not None
        assert result.final_excerpts[0].review_flags == ["verification_skipped"]
        progress.mark_failed.assert_called_once_with(
            chunk.chunk_id, "phase3_consensus", "EX-M-011"
        )

    @patch("engines.excerpting.src.phase3_enrichment.enrich_chunk")
    @patch("engines.excerpting.src.phase3_enrichment.apply_enrichment")
    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase3_consensus.resolve_consensus")
    @patch("engines.excerpting.src.phase3_consensus.verify_chunk")
    @patch("engines.excerpting.src.phase3_consensus.check_gate_triggers")
    @patch("engines.excerpting.src.phase3_consensus._needs_consensus")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_emits_full_gate_entries(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_needs_consensus: MagicMock,
        mock_check_gates: MagicMock,
        mock_verify_chunk: MagicMock,
        mock_resolve_consensus: MagicMock,
        mock_build_det: MagicMock,
        mock_apply_enrich: MagicMock,
        mock_enrich: MagicMock,
    ) -> None:
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=0)
        controller = ConcurrencyController(2)

        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpt = _make_excerpt_record(
            excerpt_id="exc_gate_test",
            div_id=chunk.div_id,
            unit_index=0,
            school="حنبلي",
            school_confidence=0.9,
        )

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units
        mock_needs_consensus.return_value = [_mock_consensus_item()]

        vi = MagicMock()
        vi.item_index = 0
        mock_verify_chunk.return_value = (
            MagicMock(items=[vi]),
            [(excerpt, [_mock_consensus_item()])],
        )
        mock_resolve_consensus.return_value = (excerpt, None, ["EX-G-001"])
        mock_check_gates.return_value = ["EX-G-003"]

        mock_build_det.return_value = [excerpt]
        mock_enrich.return_value = MagicMock()
        mock_apply_enrich.return_value = [excerpt]

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=MagicMock(),
            escalation_client=MagicMock(),
            config=config,
            controller=controller,
            progress=None,
            cache=None,
            classified_data=None,
            grouped_data=None,
            source_metadata={"source_school": "حنبلي"},
        )

        assert result.completed is True
        assert [entry["gate_code"] for entry in result.gate_entries] == [
            "EX-G-001",
            "EX-G-003",
        ]
        for entry in result.gate_entries:
            assert entry["excerpt_id"] == "exc_gate_test"
            assert entry["status"] == "pending"
            assert "timestamp" in entry
            assert "context" in entry
            assert "primary_text_snippet" in entry["context"]

    @patch("engines.excerpting.src.phase3_enrichment.enrich_chunk")
    @patch("engines.excerpting.src.phase3_enrichment.apply_enrichment")
    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase3_consensus._needs_consensus")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_reconstructs_enrichment_from_cache_on_resume(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_needs_consensus: MagicMock,
        mock_build_det: MagicMock,
        mock_apply_enrich: MagicMock,
        mock_enrich: MagicMock,
    ) -> None:
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=0)
        controller = ConcurrencyController(2)
        progress = MagicMock()
        progress.is_done.side_effect = lambda _cid, phase: phase == "phase3_enrich"
        cache = MagicMock()
        cache.load.return_value = EnrichmentResult(enrichments=[], total_units=0)

        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpt = _make_excerpt_record(excerpt_id="exc_resume_enrich", div_id=chunk.div_id)

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units
        mock_needs_consensus.return_value = []
        mock_build_det.return_value = [excerpt]
        mock_apply_enrich.return_value = [excerpt]

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=None,
            escalation_client=None,
            config=config,
            controller=controller,
            progress=progress,
            cache=cache,
            classified_data=None,
            grouped_data=None,
            source_metadata={},
        )

        assert result.completed is True
        assert result.error is None
        assert result.final_excerpts is not None
        cache.load.assert_called_once()
        mock_enrich.assert_not_called()

    @patch("engines.excerpting.src.phase3_enrichment.enrich_chunk")
    @patch("engines.excerpting.src.phase3_enrichment.apply_enrichment")
    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase3_consensus.resolve_consensus")
    @patch("engines.excerpting.src.phase3_consensus.verify_chunk")
    @patch("engines.excerpting.src.phase3_consensus._needs_consensus")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_reconstructs_consensus_from_cache_on_resume(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_needs_consensus: MagicMock,
        mock_verify_chunk: MagicMock,
        mock_resolve_consensus: MagicMock,
        mock_build_det: MagicMock,
        mock_apply_enrich: MagicMock,
        mock_enrich: MagicMock,
    ) -> None:
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=0)
        controller = ConcurrencyController(2)
        progress = MagicMock()
        progress.is_done.side_effect = lambda _cid, phase: phase == "phase3_consensus"
        cache = MagicMock()
        cache.load.side_effect = [
            None,
            VerificationResult(
                items=[
                    VerificationItem(
                        item_index=0,
                        agrees=True,
                        alternative_value=None,
                        confidence=0.9,
                        reasoning="ok",
                    )
                ]
            ),
        ]

        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpt = _make_excerpt_record(
            excerpt_id="exc_resume_consensus",
            div_id=chunk.div_id,
            school="حنبلي",
            school_confidence=0.9,
        )

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units
        mock_needs_consensus.return_value = [_mock_consensus_item()]
        mock_build_det.return_value = [excerpt]
        mock_enrich.return_value = MagicMock()
        mock_apply_enrich.return_value = [excerpt]
        mock_resolve_consensus.return_value = (excerpt, None, [])

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=MagicMock(),
            escalation_client=MagicMock(),
            config=config,
            controller=controller,
            progress=progress,
            cache=cache,
            classified_data=None,
            grouped_data=None,
            source_metadata={},
        )

        assert result.completed is True
        assert result.error is None
        assert result.final_excerpts is not None
        mock_verify_chunk.assert_not_called()
        assert cache.load.call_count == 2

    @patch("engines.excerpting.src.phase3_enrichment.enrich_chunk")
    @patch("engines.excerpting.src.phase3_enrichment.apply_enrichment")
    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase3_consensus.resolve_consensus")
    @patch("engines.excerpting.src.phase3_consensus.verify_chunk")
    @patch("engines.excerpting.src.phase3_consensus._needs_consensus")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_degrades_partial_verification_batches(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_needs_consensus: MagicMock,
        mock_verify_chunk: MagicMock,
        mock_resolve_consensus: MagicMock,
        mock_build_det: MagicMock,
        mock_apply_enrich: MagicMock,
        mock_enrich: MagicMock,
    ) -> None:
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=0)
        controller = ConcurrencyController(2)
        progress = MagicMock()
        progress.is_done.return_value = False

        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpt = _make_excerpt_record(
            excerpt_id="exc_partial_verify",
            div_id=chunk.div_id,
            school="حنبلي",
            school_confidence=0.9,
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint="باب الطهارة",
        )

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units
        mock_needs_consensus.return_value = [
            _mock_consensus_item(),
            {
                "verification_type": "SELF_CONTAINMENT",
                "decision_text": "Unit assessed as PARTIAL. Is this correct?",
                "unit_text": "بسم الله الرحمن الرحيم الحمد لله رب العالمين",
            },
        ]
        vi = MagicMock()
        vi.item_index = 0
        mock_verify_chunk.return_value = (
            MagicMock(items=[vi]),
            [(excerpt, mock_needs_consensus.return_value)],
        )
        mock_build_det.return_value = [excerpt]
        mock_enrich.return_value = MagicMock()
        mock_apply_enrich.return_value = [excerpt]

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=MagicMock(),
            escalation_client=MagicMock(),
            config=config,
            controller=controller,
            progress=progress,
            cache=None,
            classified_data=None,
            grouped_data=None,
            source_metadata={"source_school": "حنبلي"},
        )

        assert result.completed is True
        assert result.error is None
        assert result.final_excerpts is not None
        assert "verification_skipped" in result.final_excerpts[0].review_flags
        progress.mark_failed.assert_called_once_with(
            chunk.chunk_id, "phase3_consensus", "EX-M-011"
        )
        mock_resolve_consensus.assert_not_called()

    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_marks_enrichment_failed_on_resume_cache_miss(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_build_det: MagicMock,
    ) -> None:
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=0)
        controller = ConcurrencyController(2)
        progress = MagicMock()
        progress.is_done.side_effect = lambda _cid, phase: phase == "phase3_enrich"
        cache = MagicMock()
        cache.load.return_value = None

        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpt = _make_excerpt_record(excerpt_id="exc_resume_miss", div_id=chunk.div_id)

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units
        mock_build_det.return_value = [excerpt]

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=None,
            escalation_client=None,
            config=config,
            controller=controller,
            progress=progress,
            cache=cache,
            classified_data=None,
            grouped_data=None,
            source_metadata={},
        )

        assert result.completed is True
        assert result.error is None
        assert result.final_excerpts is not None
        assert "llm_enrichment_failed" in result.final_excerpts[0].review_flags
        progress.mark_failed.assert_called_once_with(
            chunk.chunk_id, "phase3_enrich", "EX-M-002"
        )

    @patch("engines.excerpting.src.phase3_enrichment.enrich_chunk")
    @patch("engines.excerpting.src.phase3_enrichment.apply_enrichment")
    @patch("engines.excerpting.src.phase3_deterministic.build_deterministic_excerpts")
    @patch("engines.excerpting.src.phase3_consensus._needs_consensus")
    @patch("engines.excerpting.src.phase2_group.verify_units")
    @patch("engines.excerpting.src.phase2_group.group_chunk")
    @patch("engines.excerpting.src.phase2_classify.verify_segments")
    @patch("engines.excerpting.src.phase2_classify.normalize_offsets")
    @patch("engines.excerpting.src.phase2_classify.classify_chunk")
    def test_process_chunk_marks_verification_skipped_on_consensus_resume_cache_miss(
        self,
        mock_classify: MagicMock,
        mock_normalize: MagicMock,
        mock_verify_seg: MagicMock,
        mock_group: MagicMock,
        mock_verify_units: MagicMock,
        mock_needs_consensus: MagicMock,
        mock_build_det: MagicMock,
        mock_apply_enrich: MagicMock,
        mock_enrich: MagicMock,
    ) -> None:
        chunk = _make_mock_chunk()
        config = _make_mock_config(RETRY_COUNT=0)
        controller = ConcurrencyController(2)
        progress = MagicMock()
        progress.is_done.side_effect = lambda _cid, phase: phase == "phase3_consensus"
        cache = MagicMock()
        cache.load.side_effect = [None, None]

        segments = [_make_mock_segment()]
        units = [_make_mock_unit()]
        excerpt = _make_excerpt_record(
            excerpt_id="exc_consensus_resume_miss",
            div_id=chunk.div_id,
            school="حنبلي",
            school_confidence=0.9,
        )

        cr_result = MagicMock()
        cr_result.segments = segments
        mock_classify.return_value = cr_result
        mock_normalize.return_value = segments

        er_result = MagicMock()
        er_result.teaching_units = units
        mock_group.return_value = er_result
        mock_verify_units.return_value = units
        mock_needs_consensus.return_value = [_mock_consensus_item()]
        mock_build_det.return_value = [excerpt]
        mock_enrich.return_value = MagicMock()
        mock_apply_enrich.return_value = [excerpt]

        ctx = ChunkPipelineContext(chunk=chunk, chunk_id=chunk.chunk_id)
        result = _process_chunk(
            ctx=ctx,
            enrich_client=MagicMock(),
            verify_client=MagicMock(),
            escalation_client=MagicMock(),
            config=config,
            controller=controller,
            progress=progress,
            cache=cache,
            classified_data=None,
            grouped_data=None,
            source_metadata={},
        )

        assert result.completed is True
        assert result.error is None
        assert result.final_excerpts is not None
        assert "verification_skipped" in result.final_excerpts[0].review_flags
        progress.mark_failed.assert_called_once_with(
            chunk.chunk_id, "phase3_consensus", "EX-M-011"
        )

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


# ===================================================================
# CircuitBreaker tests
# ===================================================================


class TestCircuitBreaker:
    """Tests for the CircuitBreaker state machine."""

    def test_circuit_breaker_starts_closed(self) -> None:
        """Initial state is CLOSED."""
        cb = CircuitBreaker()
        assert cb.state == "CLOSED"

    def test_circuit_breaker_opens_after_threshold(self) -> None:
        """5 consecutive failures transition from CLOSED to OPEN."""
        cb = CircuitBreaker(failure_threshold=5)
        for _ in range(4):
            cb.record_failure()
            assert cb.state == "CLOSED"
        cb.record_failure()
        assert cb.state == "OPEN"

    def test_circuit_breaker_closes_on_success(self) -> None:
        """record_success resets to CLOSED and clears failure count."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "CLOSED"  # Not yet at threshold
        cb.record_success()
        assert cb.state == "CLOSED"
        # Failure count was reset: need 3 more to open
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "CLOSED"
        cb.record_failure()
        assert cb.state == "OPEN"

    @patch("engines.excerpting.src.parallel_orchestrator.time.sleep")
    @patch("engines.excerpting.src.parallel_orchestrator.time.monotonic")
    def test_circuit_breaker_half_open_success(
        self, mock_monotonic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """HALF_OPEN + success -> CLOSED with reset cooldown."""
        cb = CircuitBreaker(
            failure_threshold=2, base_cooldown=10.0
        )
        # Open the breaker
        mock_monotonic.return_value = 100.0
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "OPEN"

        # Simulate cooldown elapsed: check() transitions to HALF_OPEN
        mock_monotonic.return_value = 200.0  # 100s later, > 10s cooldown
        cb.check()
        assert cb.state == "HALF_OPEN"

        # Success closes it
        cb.record_success()
        assert cb.state == "CLOSED"

    @patch("engines.excerpting.src.parallel_orchestrator.time.sleep")
    @patch("engines.excerpting.src.parallel_orchestrator.time.monotonic")
    def test_circuit_breaker_half_open_failure(
        self, mock_monotonic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """HALF_OPEN + failure -> OPEN with doubled cooldown."""
        cb = CircuitBreaker(
            failure_threshold=2, base_cooldown=10.0
        )
        # Open the breaker
        mock_monotonic.return_value = 100.0
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "OPEN"

        # Transition to HALF_OPEN
        mock_monotonic.return_value = 200.0
        cb.check()
        assert cb.state == "HALF_OPEN"

        # Failure during probe doubles cooldown
        mock_monotonic.return_value = 201.0
        cb.record_failure()
        assert cb.state == "OPEN"
        # Cooldown should have doubled from 10 -> 20
        assert cb._cooldown == 20.0

    @patch("engines.excerpting.src.parallel_orchestrator.time.sleep")
    @patch("engines.excerpting.src.parallel_orchestrator.time.monotonic")
    def test_circuit_breaker_cooldown_doubling(
        self, mock_monotonic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """Cooldown doubles on each HALF_OPEN failure, capped at max."""
        cb = CircuitBreaker(
            failure_threshold=1,
            base_cooldown=60.0,
            max_cooldown=1800.0,
        )

        t = 0.0
        mock_monotonic.return_value = t

        # Open
        cb.record_failure()
        assert cb.state == "OPEN"
        assert cb._cooldown == 60.0

        # Cycle through HALF_OPEN failures, verifying doubling
        expected_cooldowns = [120.0, 240.0, 480.0, 960.0, 1800.0, 1800.0]
        for expected_cd in expected_cooldowns:
            t += cb._cooldown + 1.0
            mock_monotonic.return_value = t
            cb.check()
            assert cb.state == "HALF_OPEN"
            mock_monotonic.return_value = t + 0.1
            cb.record_failure()
            assert cb.state == "OPEN"
            assert cb._cooldown == expected_cd

    @patch("engines.excerpting.src.parallel_orchestrator.time.sleep")
    @patch("engines.excerpting.src.parallel_orchestrator.time.monotonic")
    def test_circuit_breaker_check_closed_returns_immediately(
        self, mock_monotonic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """check() in CLOSED state returns without sleeping."""
        cb = CircuitBreaker()
        cb.check()
        mock_sleep.assert_not_called()

    def test_circuit_breaker_state_property(self) -> None:
        """state property is readable and reflects internal state."""
        cb = CircuitBreaker(failure_threshold=2)
        assert cb.state == "CLOSED"

        cb.record_failure()
        assert cb.state == "CLOSED"

        cb.record_failure()
        assert cb.state == "OPEN"

        cb.record_success()
        assert cb.state == "CLOSED"

    @patch("engines.excerpting.src.parallel_orchestrator.time.sleep")
    @patch("engines.excerpting.src.parallel_orchestrator.time.monotonic")
    def test_circuit_breaker_check_blocks_when_open(
        self, mock_monotonic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """check() in OPEN state sleeps for remaining cooldown time."""
        cb = CircuitBreaker(
            failure_threshold=1, base_cooldown=60.0
        )
        mock_monotonic.return_value = 100.0
        cb.record_failure()
        assert cb.state == "OPEN"

        # 20s have passed out of 60s cooldown
        mock_monotonic.return_value = 120.0
        cb.check()
        # Should have slept for ~40s (60 - 20)
        mock_sleep.assert_called_once()
        sleep_arg = mock_sleep.call_args[0][0]
        assert 39.0 <= sleep_arg <= 41.0
        assert cb.state == "HALF_OPEN"


# ===================================================================
# StatusWriter tests
# ===================================================================


class TestStatusWriter:
    """Tests for the StatusWriter monitoring file."""

    def test_status_writer_creates_file(self, tmp_path: Path) -> None:
        """StatusWriter writes status.json to the given path."""
        status_path = tmp_path / "status.json"
        writer = StatusWriter(status_path, update_interval=0.1)
        writer.start(total_chunks=10)
        # Give the background thread one cycle to write
        time.sleep(0.3)
        writer.stop()

        assert status_path.exists()
        data = json.loads(status_path.read_text(encoding="utf-8"))
        assert data["total_chunks"] == 10
        assert data["pending"] == 10
        assert data["completed"] == 0
        assert data["failed"] == 0
        assert "updated" in data
        assert "elapsed_seconds" in data

    def test_status_writer_records_counts(self, tmp_path: Path) -> None:
        """record_chunk_complete increments completed, decrements pending."""
        status_path = tmp_path / "status.json"
        writer = StatusWriter(status_path, update_interval=60.0)
        writer.start(total_chunks=5)

        writer.record_chunk_complete()
        writer.record_chunk_complete()
        writer.record_chunk_failed()
        writer.record_cache_hit()
        writer.record_cache_hit()
        writer.record_cache_miss()
        writer.record_phase_start("chunk_0", "phase2a")
        writer.record_phase_end("chunk_0", "phase2a")

        writer.stop()

        data = json.loads(status_path.read_text(encoding="utf-8"))
        assert data["completed"] == 2
        assert data["failed"] == 1
        assert data["pending"] == 2  # 5 - 2 completed - 1 failed
        assert data["cache_hits"] == 2
        assert data["cache_misses"] == 1
        assert data["in_progress"]["phase2a"] == 0

    def test_status_writer_stop_writes_final(self, tmp_path: Path) -> None:
        """stop() writes final status even without background thread cycle."""
        status_path = tmp_path / "status.json"
        # Very long interval so background thread never fires
        writer = StatusWriter(status_path, update_interval=9999.0)
        writer.start(total_chunks=3)

        writer.record_chunk_complete()
        writer.stop()

        assert status_path.exists()
        data = json.loads(status_path.read_text(encoding="utf-8"))
        assert data["total_chunks"] == 3
        assert data["completed"] == 1
        assert data["pending"] == 2
        assert "avg_seconds_per_chunk" in data
