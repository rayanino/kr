"""Integration tests: Phase 3 Orchestrator + Full Pipeline (Session 6).

Tests the orchestrator glue code that chains stages together,
NOT individual stage logic (covered by 489 existing tests).

Test categories:
1. Phase 3 orchestrator: deterministic → enrichment → consensus → validation
2. Full pipeline: NormalizedPackage → Phase 1 → Phase 2 (mocked) → Phase 3 → JSONL
3. Deterministic-only mode (no LLM client)
4. Gate queue round-trip in pipeline context
5. Error accumulation across phases
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from engines.excerpting.contracts import (
    AssembledChunk,
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ExcerptRecord,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
)
from engines.excerpting.src.phase3_orchestrator import Phase3Result, run_phase3
from engines.excerpting.src.pipeline import ExcerptingResult, run_excerpting

from .conftest import (
    _make_assembled_chunk,
    _make_classified_segment,
    _make_excerpt_record,
    _make_normalized_package,
    _make_teaching_unit,
)


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════


def _make_chunk_and_units(
    chunk_id: str = "div_test_1_0",
    source_id: str = "src_test",
    n_units: int = 2,
) -> tuple[AssembledChunk, list[TeachingUnit], list[ClassifiedSegment]]:
    """Create a matched chunk + teaching units + classified segments.

    Each unit's text_snippet matches what extract_primary_text produces
    for its word range, so V-P3-2 passes.
    """
    from engines.excerpting.src.phase3_deterministic import extract_primary_text

    chunk = _make_assembled_chunk(
        chunk_id=chunk_id,
        source_id=source_id,
        div_id=chunk_id,
    )
    units: list[TeachingUnit] = []
    segments: list[ClassifiedSegment] = []
    for i in range(n_units):
        sw = i * 4
        ew = i * 4 + 3
        primary_text = extract_primary_text(chunk.assembled_text, sw, ew)
        units.append(
            _make_teaching_unit(
                unit_index=i,
                start_word=sw,
                end_word=ew,
                text_snippet=primary_text[:80],
            )
        )
        segments.append(
            _make_classified_segment(segment_index=i, start_word=sw, end_word=ew)
        )
    return chunk, units, segments


# ═══════════════════════════════════════════════════════════════════
# Phase 3 Orchestrator Tests
# ═══════════════════════════════════════════════════════════════════


class TestPhase3Orchestrator:
    """Tests for run_phase3: stage chaining and graceful degradation."""

    def test_deterministic_only_no_clients(self) -> None:
        """No LLM clients → deterministic excerpts only, no enrichment/consensus."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()

        result = run_phase3(
            chunks=[chunk],
            teaching_units={chunk.chunk_id: units},
            classified={chunk.chunk_id: segments},
            config=config,
            enrich_client=None,
            verify_client=None,
        )

        assert isinstance(result, Phase3Result)
        assert len(result.excerpts) > 0
        assert result.timings["enrichment"] == 0.0
        assert result.timings["consensus"] == 0.0
        # Deterministic fields populated
        for exc in result.excerpts:
            assert exc.source_id == "src_test"
            assert exc.primary_function is not None

    def test_deterministic_only_produces_valid_excerpts(self) -> None:
        """Deterministic-only excerpts pass validation (V-P3 checks)."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()

        result = run_phase3(
            chunks=[chunk],
            teaching_units={chunk.chunk_id: units},
            classified={chunk.chunk_id: segments},
            config=config,
        )

        # Validation ran (stage 4) — check no fatal errors
        assert all(
            code != ExcerptingErrorCodes.EX_V_001
            for code in result.errors
        )
        assert len(result.excerpts) == len(units)

    def test_enrichment_failure_degrades_gracefully(self) -> None:
        """LLM enrichment exception → deterministic fields survive."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()
        mock_client = MagicMock()

        with patch(
            "engines.excerpting.src.phase3_orchestrator.run_phase3_enrichment",
            side_effect=RuntimeError("LLM service unavailable"),
        ):
            result = run_phase3(
                chunks=[chunk],
                teaching_units={chunk.chunk_id: units},
                classified={chunk.chunk_id: segments},
                config=config,
                enrich_client=mock_client,
            )

        assert ExcerptingErrorCodes.EX_M_002 in result.errors
        # Excerpts still produced from deterministic stage
        assert len(result.excerpts) > 0

    def test_consensus_crash_degrades_gracefully(self) -> None:
        """FIX-1: Consensus RuntimeError degrades to enrichment-only with flag."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()
        mock_client = MagicMock()

        with patch(
            "engines.excerpting.src.phase3_orchestrator.run_phase3_enrichment",
            side_effect=lambda **kw: kw["excerpts"],
        ), patch(
            "engines.excerpting.src.phase3_orchestrator.run_consensus",
            side_effect=RuntimeError("Consensus model timeout"),
        ):
            result = run_phase3(
                chunks=[chunk],
                teaching_units={chunk.chunk_id: units},
                classified={chunk.chunk_id: segments},
                config=config,
                enrich_client=mock_client,
                verify_client=mock_client,
            )

        # Graceful degradation: excerpts produced with verification_skipped flag
        assert len(result.excerpts) > 0
        assert any("verification_skipped" in e.review_flags for e in result.excerpts)
        assert ExcerptingErrorCodes.EX_M_011 in result.errors

    def test_multi_chunk_processing(self) -> None:
        """Multiple chunks → all processed, excerpts collected."""
        chunk_a, units_a, segs_a = _make_chunk_and_units(
            chunk_id="div_a_0", source_id="src_test"
        )
        chunk_b, units_b, segs_b = _make_chunk_and_units(
            chunk_id="div_b_0", source_id="src_test"
        )
        config = ExcerptingConfig()

        result = run_phase3(
            chunks=[chunk_a, chunk_b],
            teaching_units={
                chunk_a.chunk_id: units_a,
                chunk_b.chunk_id: units_b,
            },
            classified={
                chunk_a.chunk_id: segs_a,
                chunk_b.chunk_id: segs_b,
            },
            config=config,
        )

        # Both chunks contribute excerpts
        div_ids = {exc.div_id for exc in result.excerpts}
        assert "div_a_0" in div_ids
        assert "div_b_0" in div_ids
        assert len(result.excerpts) == len(units_a) + len(units_b)

    def test_empty_chunks_returns_empty(self) -> None:
        """No chunks → empty result, no errors."""
        config = ExcerptingConfig()
        result = run_phase3(
            chunks=[], teaching_units={}, classified={}, config=config
        )
        assert result.excerpts == []
        assert result.gate_entries == []

    def test_missing_teaching_units_skips_chunk(self) -> None:
        """Chunk with no teaching units → skipped, not crash."""
        chunk = _make_assembled_chunk(chunk_id="div_no_units")
        config = ExcerptingConfig()

        result = run_phase3(
            chunks=[chunk],
            teaching_units={},
            classified={},
            config=config,
        )

        assert result.excerpts == []

    def test_timings_populated(self) -> None:
        """All timing keys present after run."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()

        result = run_phase3(
            chunks=[chunk],
            teaching_units={chunk.chunk_id: units},
            classified={chunk.chunk_id: segments},
            config=config,
        )

        assert "deterministic" in result.timings
        assert "enrichment" in result.timings
        assert "consensus" in result.timings
        assert "validation" in result.timings

    def test_gate_entries_collected_from_consensus(self) -> None:
        """Gate entries from consensus stage are collected in result."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()
        mock_client = MagicMock()

        fake_gate: dict[str, object] = {
            "excerpt_id": "exc_test_0_0_0",
            "gate_code": "EX-G-001",
            "timestamp": "2026-03-24T00:00:00+00:00",
            "context": {
                "primary_text": "النص الكامل للاقتطاف",
                "primary_text_snippet": "النص الكامل",
            },
            "status": "pending",
        }

        def mock_enrichment(**kwargs: Any) -> list[ExcerptRecord]:
            return kwargs["excerpts"]

        def mock_consensus(**kwargs: Any) -> tuple[list[ExcerptRecord], list[dict[str, object]]]:
            return kwargs["excerpts"], [fake_gate]

        with patch(
            "engines.excerpting.src.phase3_orchestrator.run_phase3_enrichment",
            side_effect=mock_enrichment,
        ), patch(
            "engines.excerpting.src.phase3_orchestrator.run_consensus",
            side_effect=mock_consensus,
        ):
            result = run_phase3(
                chunks=[chunk],
                teaching_units={chunk.chunk_id: units},
                classified={chunk.chunk_id: segments},
                config=config,
                enrich_client=mock_client,
                verify_client=mock_client,
            )

        assert len(result.gate_entries) == 1
        assert result.gate_entries[0]["gate_code"] == "EX-G-001"

    def test_enrichment_skipped_but_consensus_still_runs(self) -> None:
        """verify_client present should still run consensus on deterministic excerpts."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()
        mock_verify = MagicMock()
        deterministic_excerpt = _make_excerpt_record(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint="باب الطهارة",
        )

        with patch(
            "engines.excerpting.src.phase3_orchestrator.build_deterministic_excerpts",
            return_value=[deterministic_excerpt],
        ), patch(
            "engines.excerpting.src.phase3_orchestrator.run_consensus",
            return_value=([deterministic_excerpt], []),
        ) as mock_consensus:
            result = run_phase3(
                chunks=[chunk],
                teaching_units={chunk.chunk_id: units},
                classified={chunk.chunk_id: segments},
                config=config,
                enrich_client=None,
                verify_client=mock_verify,
            )

        mock_consensus.assert_called_once()
        assert mock_consensus.call_args.kwargs["excerpts"] == [deterministic_excerpt]
        assert result.timings["consensus"] >= 0.0
        assert len(result.excerpts) > 0

    def test_verify_only_clears_placeholder_enrichment_failure_flag(self) -> None:
        """Real deterministic verify-only path must not label success as enrichment failure."""
        chunk = _make_assembled_chunk(chunk_id="div_verify_only_0", div_id="div_verify_only_0")
        segments = [
            _make_classified_segment(
                start_word=0,
                end_word=4,
                text_snippet=chunk.assembled_text[:50],
            )
        ]
        units = [
            _make_teaching_unit(
                start_word=0,
                end_word=4,
                text_snippet=chunk.assembled_text[:80],
                self_containment=SelfContainmentLevel.PARTIAL,
                self_containment_notes="يحتاج سياقاً",
            )
        ]
        config = ExcerptingConfig()

        def echo_consensus(**kwargs: Any) -> tuple[list[ExcerptRecord], list[dict[str, object]]]:
            return kwargs["excerpts"], []

        with patch(
            "engines.excerpting.src.phase3_orchestrator.run_consensus",
            side_effect=echo_consensus,
        ) as mock_consensus:
            result = run_phase3(
                chunks=[chunk],
                teaching_units={chunk.chunk_id: units},
                classified={chunk.chunk_id: segments},
                config=config,
                enrich_client=None,
                verify_client=MagicMock(),
            )

        seeded_excerpt = mock_consensus.call_args.kwargs["excerpts"][0]
        assert "llm_enrichment_failed" in seeded_excerpt.review_flags
        assert len(result.excerpts) == 1
        assert "llm_enrichment_failed" not in result.excerpts[0].review_flags
        assert result.excerpts[0].context_hint == "يحتاج سياقاً"

    def test_deterministic_crash_propagates(self) -> None:
        """Exception in deterministic assembly propagates (Fix 3 — bugs crash)."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.phase3_orchestrator.build_deterministic_excerpts",
            side_effect=ValueError("Bug in deterministic code"),
        ), pytest.raises(ValueError, match="Bug in deterministic code"):
            run_phase3(
                chunks=[chunk],
                teaching_units={chunk.chunk_id: units},
                classified={chunk.chunk_id: segments},
                config=config,
            )


# ═══════════════════════════════════════════════════════════════════
# Full Pipeline Tests (Phase 1 → Phase 2 (mock) → Phase 3 → Writer)
# ═══════════════════════════════════════════════════════════════════


class TestFullPipeline:
    """End-to-end tests with Phase 2 mocked."""

    def _mock_phase2(
        self, chunks: list[AssembledChunk]
    ) -> tuple[dict[str, list[ClassifiedSegment]], dict[str, list[TeachingUnit]]]:
        """Build fake Phase 2 output matching chunks from Phase 1."""
        classified: dict[str, list[ClassifiedSegment]] = {}
        grouped: dict[str, list[TeachingUnit]] = {}

        for chunk in chunks:
            cid = chunk.chunk_id
            # One segment covering the whole chunk
            seg = ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=max(1, chunk.word_count - 1),
                text_snippet=chunk.assembled_text[:50],
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
            classified[cid] = [seg]

            # One teaching unit covering the whole chunk
            tu = TeachingUnit(
                unit_index=0,
                segment_indices=[0],
                start_word=0,
                end_word=max(1, chunk.word_count - 1),
                text_snippet=chunk.assembled_text[:80],
                primary_function=ScholarlyFunction.DEFINITION,
                secondary_functions=[],
                description_arabic="وصف عربي للاختبار يتضمن عدة كلمات مفيدة",
                self_containment=SelfContainmentLevel.FULL,
                self_containment_notes=None,
            )
            grouped[cid] = [tu]

        return classified, grouped

    def test_end_to_end_produces_jsonl(self, tmp_path: Path) -> None:
        """NormalizedPackage → Phase 1 → Phase 2 (mock) → Phase 3 → excerpts.jsonl."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        # We need to mock Phase 2 (LLM calls)
        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b:
            # Run Phase 1 for real to get actual chunks
            from engines.excerpting.src.phase1_assembly import run_phase1

            chunks, _ = run_phase1(package, config)
            classified, grouped = self._mock_phase2(chunks)
            mock_2a.return_value = classified
            mock_2b.return_value = grouped

            mock_client = MagicMock()
            result = run_excerpting(
                package=package,
                config=config,
                output_dir=tmp_path,
                enrich_client=mock_client,
            )

        assert isinstance(result, ExcerptingResult)
        assert len(result.excerpts) > 0
        assert "excerpts" in result.output_paths
        # Verify JSONL file exists and is valid
        excerpts_path = result.output_paths["excerpts"]
        assert excerpts_path.exists()
        lines = excerpts_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == len(result.excerpts)
        for line in lines:
            obj = json.loads(line)
            assert "excerpt_id" in obj

    def test_no_llm_client_returns_early(self) -> None:
        """No enrich_client → Phase 2 skipped, returns with error."""
        package = _make_normalized_package()
        result = run_excerpting(package=package, enrich_client=None)

        assert any("PHASE2_SKIPPED" in e for e in result.errors)
        assert result.excerpts == []

    def test_timings_all_phases(self, tmp_path: Path) -> None:
        """Pipeline produces timing data for all phases."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b:
            from engines.excerpting.src.phase1_assembly import run_phase1

            chunks, _ = run_phase1(package, config)
            classified, grouped = self._mock_phase2(chunks)
            mock_2a.return_value = classified
            mock_2b.return_value = grouped

            result = run_excerpting(
                package=package,
                config=config,
                output_dir=tmp_path,
                enrich_client=MagicMock(),
            )

        assert "phase1" in result.timings
        assert "phase2" in result.timings
        assert "phase3" in result.timings

    def test_arabic_preserved_in_output(self, tmp_path: Path) -> None:
        """Arabic text preserved byte-for-byte in JSONL output."""
        arabic_text = "بسم الله الرحمن الرحيم وبعد فهذا كتاب في النحو"
        package = _make_normalized_package(primary_text=arabic_text)
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b:
            from engines.excerpting.src.phase1_assembly import run_phase1

            chunks, _ = run_phase1(package, config)
            classified, grouped = self._mock_phase2(chunks)
            mock_2a.return_value = classified
            mock_2b.return_value = grouped

            result = run_excerpting(
                package=package,
                config=config,
                output_dir=tmp_path,
                enrich_client=MagicMock(),
            )

        content = result.output_paths["excerpts"].read_text(encoding="utf-8")
        # Arabic text present in output, not escaped
        assert "الله" in content
        assert "\\u" not in content

    def test_gate_queue_written_and_verified(self, tmp_path: Path) -> None:
        """Gate entries → gate_queue.jsonl written + V-P3-7 verified."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        fake_gate = {
            "excerpt_id": "exc_gate_test",
            "gate_code": "EX-G-001",
            "timestamp": "2026-03-24T00:00:00+00:00",
            "context": {
                "primary_text": "بسم الله الرحمن الرحيم كاملة",
                "primary_text_snippet": "بسم الله الرحمن الرحيم",
            },
            "status": "pending",
        }

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b, patch(
            "engines.excerpting.src.pipeline.run_phase3"
        ) as mock_p3:
            from engines.excerpting.src.phase1_assembly import run_phase1

            run_phase1(package, config)

            mock_2a.return_value = {}
            mock_2b.return_value = {}

            # Mock Phase 3 to return excerpts + gate entries
            mock_p3.return_value = Phase3Result(
                excerpts=[_make_excerpt_record()],
                gate_entries=[fake_gate],
                errors=[],
                timings={"deterministic": 0.0, "enrichment": 0.0, "consensus": 0.0, "validation": 0.0},
            )

            result = run_excerpting(
                package=package,
                config=config,
                output_dir=tmp_path,
                enrich_client=MagicMock(),
            )

        assert "gate_queue" in result.output_paths
        gate_path = result.output_paths["gate_queue"]
        assert gate_path.exists()
        data = json.loads(gate_path.read_text(encoding="utf-8").strip())
        assert data["gate_code"] == "EX-G-001"

    def test_no_output_dir_skips_write(self) -> None:
        """output_dir=None → no files written, excerpts still returned."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b:
            from engines.excerpting.src.phase1_assembly import run_phase1

            chunks, _ = run_phase1(package, config)
            classified: dict[str, list[ClassifiedSegment]] = {}
            grouped: dict[str, list[TeachingUnit]] = {}
            for chunk in chunks:
                cid = chunk.chunk_id
                seg = ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=max(1, chunk.word_count - 1),
                    text_snippet=chunk.assembled_text[:50],
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.9,
                )
                classified[cid] = [seg]
                tu = TeachingUnit(
                    unit_index=0,
                    segment_indices=[0],
                    start_word=0,
                    end_word=max(1, chunk.word_count - 1),
                    text_snippet=chunk.assembled_text[:80],
                    primary_function=ScholarlyFunction.DEFINITION,
                    secondary_functions=[],
                    description_arabic="وصف عربي للاختبار يتضمن عدة كلمات مفيدة",
                    self_containment=SelfContainmentLevel.FULL,
                    self_containment_notes=None,
                )
                grouped[cid] = [tu]
            mock_2a.return_value = classified
            mock_2b.return_value = grouped

            result = run_excerpting(
                package=package,
                config=config,
                output_dir=None,  # No output
                enrich_client=MagicMock(),
            )

        assert len(result.excerpts) > 0
        assert result.output_paths == {}

    def test_error_accumulation_across_phases(self, tmp_path: Path) -> None:
        """Errors from Phase 3 stages accumulated in pipeline result."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b, patch(
            "engines.excerpting.src.pipeline.run_phase3"
        ) as mock_p3:
            mock_2a.return_value = {}
            mock_2b.return_value = {}
            mock_p3.return_value = Phase3Result(
                excerpts=[_make_excerpt_record()],
                gate_entries=[],
                errors=[ExcerptingErrorCodes.EX_M_002, ExcerptingErrorCodes.EX_M_004],
                timings={"deterministic": 0.0, "enrichment": 0.0, "consensus": 0.0, "validation": 0.0},
            )

            result = run_excerpting(
                package=package,
                config=config,
                output_dir=tmp_path,
                enrich_client=MagicMock(),
            )

        assert ExcerptingErrorCodes.EX_M_002 in result.errors
        assert ExcerptingErrorCodes.EX_M_004 in result.errors


# ═══════════════════════════════════════════════════════════════════
# Deterministic-Only Mode Tests
# ═══════════════════════════════════════════════════════════════════


class TestDeterministicOnlyMode:
    """Tests for running Phase 3 without any LLM client."""

    def test_no_topic_in_deterministic_only(self) -> None:
        """Deterministic-only: excerpt_topic stays default (no LLM to populate it)."""
        chunk, units, segments = _make_chunk_and_units()
        config = ExcerptingConfig()

        result = run_phase3(
            chunks=[chunk],
            teaching_units={chunk.chunk_id: units},
            classified={chunk.chunk_id: segments},
            config=config,
        )

        for exc in result.excerpts:
            # Without enrichment, excerpt_topic is empty
            assert exc.excerpt_topic == []

    def test_no_consensus_metadata(self) -> None:
        """Deterministic-only: consensus_metadata stays None."""
        chunk, units, segments = _make_chunk_and_units()
        result = run_phase3(
            chunks=[chunk],
            teaching_units={chunk.chunk_id: units},
            classified={chunk.chunk_id: segments},
            config=ExcerptingConfig(),
        )

        for exc in result.excerpts:
            assert exc.consensus_metadata is None

    def test_multiple_chunks_deterministic(self) -> None:
        """Multiple chunks in deterministic-only mode all produce excerpts."""
        chunks_and_units = [
            _make_chunk_and_units(chunk_id=f"div_chunk_{i}", source_id="src_test")
            for i in range(3)
        ]
        config = ExcerptingConfig()

        result = run_phase3(
            chunks=[c for c, _, _ in chunks_and_units],
            teaching_units={c.chunk_id: u for c, u, _ in chunks_and_units},
            classified={c.chunk_id: s for c, _, s in chunks_and_units},
            config=config,
        )

        # 3 chunks × 2 units each = 6 excerpts
        assert len(result.excerpts) == 6


# ═══════════════════════════════════════════════════════════════════
# Cross-phase Boundary Tests
# ═══════════════════════════════════════════════════════════════════


class TestCrossPhaseBoundary:
    """Tests verifying data flows correctly across phase boundaries."""

    def test_phase1_output_feeds_phase3(self) -> None:
        """Phase 1 chunks can be used directly by Phase 3 deterministic."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        from engines.excerpting.src.phase1_assembly import run_phase1

        chunks, _ = run_phase1(package, config)
        assert len(chunks) > 0

        # Build minimal Phase 2 output for these chunks
        teaching_units: dict[str, list[TeachingUnit]] = {}
        classified: dict[str, list[ClassifiedSegment]] = {}
        for chunk in chunks:
            classified[chunk.chunk_id] = [
                ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=max(1, chunk.word_count - 1),
                    text_snippet=chunk.assembled_text[:50],
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.9,
                )
            ]
            teaching_units[chunk.chunk_id] = [
                TeachingUnit(
                    unit_index=0,
                    segment_indices=[0],
                    start_word=0,
                    end_word=max(1, chunk.word_count - 1),
                    text_snippet=chunk.assembled_text[:80],
                    primary_function=ScholarlyFunction.DEFINITION,
                    secondary_functions=[],
                    description_arabic="وصف عربي للاختبار يتضمن عدة كلمات مفيدة",
                    self_containment=SelfContainmentLevel.FULL,
                    self_containment_notes=None,
                )
            ]

        result = run_phase3(
            chunks=chunks,
            teaching_units=teaching_units,
            classified=classified,
            config=config,
        )

        assert len(result.excerpts) == len(chunks)
        # Source ID preserved from Phase 1
        for exc in result.excerpts:
            assert exc.source_id == "src_test"

    def test_excerpt_ids_unique_across_chunks(self) -> None:
        """Each excerpt gets a unique ID even across multiple chunks."""
        chunks_and_units = [
            _make_chunk_and_units(chunk_id=f"div_uid_{i}", source_id="src_test")
            for i in range(3)
        ]
        config = ExcerptingConfig()

        result = run_phase3(
            chunks=[c for c, _, _ in chunks_and_units],
            teaching_units={c.chunk_id: u for c, u, _ in chunks_and_units},
            classified={c.chunk_id: s for c, _, s in chunks_and_units},
            config=config,
        )

        ids = [exc.excerpt_id for exc in result.excerpts]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {ids}"

    def test_div_path_preserved(self) -> None:
        """Division path from chunk preserved in excerpt."""
        from engines.excerpting.src.phase3_deterministic import extract_primary_text

        chunk = _make_assembled_chunk(
            chunk_id="div_path_test",
            div_path=["كتاب الطهارة", "باب الوضوء"],
        )
        primary_text = extract_primary_text(chunk.assembled_text, 0, 4)
        units = [_make_teaching_unit(text_snippet=primary_text[:80])]
        segments = [_make_classified_segment()]

        result = run_phase3(
            chunks=[chunk],
            teaching_units={chunk.chunk_id: units},
            classified={chunk.chunk_id: segments},
            config=ExcerptingConfig(),
        )

        assert len(result.excerpts) > 0
        assert result.excerpts[0].div_path == ["كتاب الطهارة", "باب الوضوء"]

    def test_output_sorted_by_reading_order(self, tmp_path: Path) -> None:
        """Written JSONL sorted by div_id, chunk_index, unit_index."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b, patch(
            "engines.excerpting.src.pipeline.run_phase3"
        ) as mock_p3:
            mock_2a.return_value = {}
            mock_2b.return_value = {}

            # Two excerpts in reverse order
            exc_b = _make_excerpt_record(
                excerpt_id="exc_b_0_0_0", div_id="div_b", chunk_index=0, unit_index=0
            )
            exc_a = _make_excerpt_record(
                excerpt_id="exc_a_0_0_0", div_id="div_a", chunk_index=0, unit_index=0
            )
            mock_p3.return_value = Phase3Result(
                excerpts=[exc_b, exc_a],
                gate_entries=[],
                errors=[],
                timings={"deterministic": 0.0, "enrichment": 0.0, "consensus": 0.0, "validation": 0.0},
            )

            result = run_excerpting(
                package=package,
                config=config,
                output_dir=tmp_path,
                enrich_client=MagicMock(),
            )

        lines = result.output_paths["excerpts"].read_text(encoding="utf-8").strip().split("\n")
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        assert first["div_id"] == "div_a"
        assert second["div_id"] == "div_b"


# ═══════════════════════════════════════════════════════════════════
# Fix 2: Pipeline catches Phase 3 crash
# ═══════════════════════════════════════════════════════════════════


class TestPipelineCatchesPhase3Fatal:
    """Fix 2: run_excerpting catches Phase 3 crash, returns PHASE3_FATAL."""

    def test_phase3_runtime_error_caught(self) -> None:
        """Phase 3 RuntimeError → pipeline returns result with PHASE3_FATAL."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b, patch(
            "engines.excerpting.src.pipeline.run_phase3",
            side_effect=RuntimeError("Consensus crashed"),
        ):
            mock_2a.return_value = {}
            mock_2b.return_value = {}

            result = run_excerpting(
                package=package,
                config=config,
                enrich_client=MagicMock(),
            )

        assert any("PHASE3_FATAL" in e for e in result.errors)
        assert result.excerpts == []

    def test_phase3_programming_bug_propagates(self) -> None:
        """Phase 3 TypeError → pipeline re-raises (programming bug)."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b, patch(
            "engines.excerpting.src.pipeline.run_phase3",
            side_effect=TypeError("Bug in code"),
        ):
            mock_2a.return_value = {}
            mock_2b.return_value = {}

            with pytest.raises(TypeError, match="Bug in code"):
                run_excerpting(
                    package=package,
                    config=config,
                    enrich_client=MagicMock(),
                )

    def test_phase3_indexerror_propagates(self) -> None:
        """Phase 3 IndexError → pipeline re-raises (programming bug, not LLM failure)."""
        package = _make_normalized_package()
        config = ExcerptingConfig()

        with patch(
            "engines.excerpting.src.pipeline.run_phase2a"
        ) as mock_2a, patch(
            "engines.excerpting.src.pipeline.run_phase2b"
        ) as mock_2b, patch(
            "engines.excerpting.src.pipeline.run_phase3",
            side_effect=IndexError("off by one in enrichment"),
        ):
            mock_2a.return_value = {}
            mock_2b.return_value = {}

            with pytest.raises(IndexError, match="off by one"):
                run_excerpting(
                    package=package,
                    config=config,
                    enrich_client=MagicMock(),
                )
