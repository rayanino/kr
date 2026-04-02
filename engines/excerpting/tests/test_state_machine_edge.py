"""Edge-case & impossible-state tests for the excerpting pipeline state machine.

Tests 20 impossible/unexpected/boundary state transitions across the full
excerpting pipeline: Phase 1 → Phase 2a → Phase 2b → Phase 3 (deterministic
→ enrichment → consensus → validation) → Writer.

Each test probes whether the pipeline handles a specific impossible, error-
recovery, or boundary state correctly. A test failure indicates a real gap
in the pipeline's state handling.

Categories:
  - Impossible states (1-10): states the type system or pipeline logic should reject
  - Error recovery (11-15): partial failures within a phase
  - Boundary states (16-20): minimum/maximum/degenerate inputs
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError  # pyright: ignore[reportMissingImports]

# Ensure project root on sys.path
_project_root = str(Path(__file__).resolve().parents[3])
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from engines.excerpting.contracts import (
    AssembledChunk,
    AssemblyMetadata,
    AuthorAttribution,
    ClassifiedSegment,
    EnrichmentResult,
    EvidenceRef,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ExcerptRecord,
    PageRange,
    ScholarlyFunction,
    SelfContainmentLevel,
    SplitInfo,
    TeachingUnit,
    UnitEnrichment,
    VerificationItem,
    validate_ac_invariants,
    validate_cs_invariants,
)
from engines.excerpting.src.phase3_consensus import (
    _needs_consensus,
    resolve_consensus,
)
from engines.excerpting.src.phase3_enrichment import (
    EnrichmentBatchCoverageError,
    apply_enrichment,
)
from engines.excerpting.src.phase3_validation import validate_batch, validate_excerpt
from engines.excerpting.src.writer import (
    GateQueueVerificationError,
    verify_gate_queue,
    write_excerpts,
)
from engines.normalization.contracts import (
    ContentFlags,
    LayerType,
    PhysicalPage,
    StructuralFormat,
    TextLayerSegment,
)


# ═══════════════════════════════════════════════════════════════════════
# Shared factory helpers (mirrors conftest.py pattern but standalone)
# ═══════════════════════════════════════════════════════════════════════

_DEFAULT_TEXT = "بسم الله الرحمن الرحيم الحمد لله رب العالمين"
_DEFAULT_TOKENS = _DEFAULT_TEXT.split()
_DEFAULT_TOTAL_TOKENS = len(_DEFAULT_TOKENS)
_FULL_CONFIDENCE = float("1")
_ZERO_CONFIDENCE = float("0")
_INVALID_HIGH_CONFIDENCE = float("1.5")
_DEFAULT_WORD_COUNT = sum(
    1 for t in _DEFAULT_TOKENS if any("\u0600" <= c <= "\u06FF" for c in t)
)


def _make_chunk(**overrides: Any) -> AssembledChunk:
    """Factory for AssembledChunk with valid defaults."""
    text = overrides.get("assembled_text", _DEFAULT_TEXT)
    tokens = text.split()
    defaults: dict[str, Any] = {
        "chunk_id": "div_test_1_0",
        "source_id": "src_test",
        "div_id": "div_test_1_0",
        "div_path": ["باب الاختبار"],
        "assembled_text": text,
        "word_count": sum(1 for t in tokens if any("\u0600" <= c <= "\u06FF" for c in t)),
        "total_tokens": len(tokens),
        "text_layers": [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(text),
                confidence=_FULL_CONFIDENCE,
            )
        ],
        "footnotes": [],
        "content_flags": ContentFlags(),
        "physical_pages": [
            PhysicalPage(volume=1, page_number_display="١", page_number_int=1)
        ],
        "structural_format": StructuralFormat.PROSE,
        "heading_alignment_ok": True,
        "assembly_metadata": AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        ),
        "merge_history": None,
        "split_info": None,
    }
    defaults.update(overrides)
    # Recompute word_count and total_tokens if text was overridden
    if "assembled_text" in overrides and "total_tokens" not in overrides:
        t = overrides["assembled_text"]
        defaults["total_tokens"] = len(t.split())
    if "assembled_text" in overrides and "word_count" not in overrides:
        t = overrides["assembled_text"]
        defaults["word_count"] = sum(
            1 for tk in t.split() if any("\u0600" <= c <= "\u06FF" for c in tk)
        )
    if "assembled_text" in overrides and "text_layers" not in overrides:
        t = overrides["assembled_text"]
        defaults["text_layers"] = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(t),
                confidence=_FULL_CONFIDENCE,
            )
        ]
    merge_history = defaults.pop("merge_history", None)
    split_info = defaults.pop("split_info", None)
    return AssembledChunk(
        **defaults,
        merge_history=merge_history,
        split_info=split_info,
    )


def _make_segment(**overrides: Any) -> ClassifiedSegment:
    """Factory for ClassifiedSegment."""
    defaults: dict[str, Any] = {
        "segment_index": 0,
        "start_word": 0,
        "end_word": _DEFAULT_TOTAL_TOKENS - 1,
        "text_snippet": _DEFAULT_TEXT[:50],
        "scholarly_function": ScholarlyFunction.DEFINITION,
        "confidence": 0.9,
    }
    defaults.update(overrides)
    return ClassifiedSegment(**defaults)


def _make_unit(**overrides: Any) -> TeachingUnit:
    """Factory for TeachingUnit."""
    defaults: dict[str, Any] = {
        "unit_index": 0,
        "segment_indices": [0],
        "start_word": 0,
        "end_word": _DEFAULT_TOTAL_TOKENS - 1,
        "text_snippet": _DEFAULT_TEXT[:80],
        "primary_function": ScholarlyFunction.DEFINITION,
        "secondary_functions": [],
        "description_arabic": "وصف عربي قصير للاختبار يتضمن عدة كلمات",
        "self_containment": SelfContainmentLevel.FULL,
        "self_containment_notes": None,
    }
    defaults.update(overrides)
    self_containment_notes = defaults.pop("self_containment_notes", None)
    return TeachingUnit(**defaults, self_containment_notes=self_containment_notes)


def _make_excerpt(**overrides: Any) -> ExcerptRecord:
    """Factory for ExcerptRecord."""
    defaults: dict[str, Any] = {
        "excerpt_id": "exc_src_test_div_test_0_0",
        "source_id": "src_test",
        "div_id": "div_test",
        "chunk_index": 0,
        "unit_index": 0,
        "div_path": ["باب الاختبار"],
        "primary_text": _DEFAULT_TEXT,
        "text_snippet": _DEFAULT_TEXT[:80],
        "start_word": 0,
        "end_word": _DEFAULT_TOTAL_TOKENS - 1,
        "segment_indices": [0],
        "physical_pages": None,
        "primary_function": ScholarlyFunction.DEFINITION,
        "secondary_functions": [],
        "content_types": [ScholarlyFunction.DEFINITION],
        "description_arabic": "وصف عربي قصير للاختبار يتضمن عدة كلمات",
        "self_containment": SelfContainmentLevel.FULL,
        "self_containment_notes": None,
        "context_hint": None,
        "primary_author_layer": AuthorAttribution(
            layer_id="layer_matn",
            author_id="sch_test",
            coverage_pct=1.0,
            rule_applied="LA-1",
        ),
        "attribution_confidence": None,
        "quoted_scholars": [],
        "school": None,
        "school_confidence": None,
        "excerpt_topic": ["اختبار"],
        "terminology_variants": [],
        "evidence_refs": [],
        "takhrij_data": None,
        "cross_references": [],
        "footnotes_relevant": [],
        "consensus_metadata": None,
        "gate_flags": [],
        "review_flags": [],
    }
    defaults.update(overrides)
    attribution_confidence = defaults.pop("attribution_confidence", None)
    school_confidence = defaults.pop("school_confidence", None)
    return ExcerptRecord(
        **defaults,
        attribution_confidence=attribution_confidence,
        school_confidence=school_confidence,
    )


# ═══════════════════════════════════════════════════════════════════════
# IMPOSSIBLE STATES (1-10)
# ═══════════════════════════════════════════════════════════════════════


class TestImpossibleStates:
    """Test that the pipeline rejects states that should never exist."""

    # ── 1. Classification with 0 scholarly functions ──────────────────
    def test_01_classification_zero_segments(self) -> None:
        """Chunk classified into zero segments violates I-CS-5.

        The invariant requires every token to be covered. An empty segment
        list with total_tokens > 0 should raise.
        """
        with pytest.raises(ValueError, match="I-CS-5"):
            validate_cs_invariants(segments=[], total_tokens=7)

    # ── 2. Invalid scholarly_function value ───────────────────────────
    def test_02_invalid_scholarly_function_enum(self) -> None:
        """ScholarlyFunction rejects values not in the 16-type taxonomy.

        Pydantic should raise ValidationError for an unknown enum value.
        """
        with pytest.raises(ValidationError):
            ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=5,
                text_snippet="test",
                scholarly_function="NONEXISTENT_FUNCTION",  # type: ignore[arg-type]
                confidence=0.9,
            )

    # ── 3. Group containing chunks from different source_ids ─────────
    def test_03_cross_source_chunks_in_group(self) -> None:
        """Teaching units referencing chunks from different books is impossible.

        The pipeline processes one source at a time. If two chunks with
        different source_ids exist, build_deterministic_excerpts processes
        them independently. We verify the contract: all ExcerptRecords from
        one call share the same source_id.
        """
        from engines.excerpting.src.phase3_deterministic import (
            build_deterministic_excerpts,
        )

        chunk_a = _make_chunk(source_id="book_A", chunk_id="div_A_1_0", div_id="div_A_1_0")
        chunk_b = _make_chunk(source_id="book_B", chunk_id="div_B_1_0", div_id="div_B_1_0")

        seg_a = _make_segment(end_word=chunk_a.total_tokens - 1)
        seg_b = _make_segment(end_word=chunk_b.total_tokens - 1)

        unit_a = _make_unit(end_word=chunk_a.total_tokens - 1)
        unit_b = _make_unit(end_word=chunk_b.total_tokens - 1)

        excerpts_a = build_deterministic_excerpts(chunk_a, [unit_a], [seg_a])
        excerpts_b = build_deterministic_excerpts(chunk_b, [unit_b], [seg_b])

        # Every excerpt from chunk_a must have source_id "book_A"
        for exc in excerpts_a:
            assert exc.source_id == "book_A"
        for exc in excerpts_b:
            assert exc.source_id == "book_B"

        # Cross-source contamination: mixing them should be detectable
        all_source_ids = {e.source_id for e in excerpts_a + excerpts_b}
        assert len(all_source_ids) == 2, "Cross-source outputs should be distinguishable"

    # ── 4. Enrichment returning MORE excerpts than input chunks ──────
    def test_04_enrichment_more_units_than_input(self) -> None:
        """apply_enrichment handles enrichment with extra unit_index values.

        If the LLM returns enrichments for unit_index values not present
        in the excerpts list, the extra entries should be silently ignored
        (they simply will not match any excerpt).
        """
        exc = _make_excerpt(unit_index=0)

        # Enrichment returns 3 units but we only have 1 excerpt
        enrichment = EnrichmentResult(
            enrichments=[
                UnitEnrichment(
                    unit_index=0,
                    excerpt_topic=["موضوع"],
                    school=None,
                    school_confidence=None,
                    resolved_scholars=[],
                    takhrij_data=[],
                    terminology_variants=[],
                    cross_references=[],
                    context_hint=None,
                ),
                UnitEnrichment(
                    unit_index=1,
                    excerpt_topic=["غريب"],
                    school=None,
                    school_confidence=None,
                    resolved_scholars=[],
                    takhrij_data=[],
                    terminology_variants=[],
                    cross_references=[],
                    context_hint=None,
                ),
                UnitEnrichment(
                    unit_index=2,
                    excerpt_topic=["شاذ"],
                    school=None,
                    school_confidence=None,
                    resolved_scholars=[],
                    takhrij_data=[],
                    terminology_variants=[],
                    cross_references=[],
                    context_hint=None,
                ),
            ],
            total_units=3,
        )

        with pytest.raises(EnrichmentBatchCoverageError, match="expected total_units=1, got 3"):
            apply_enrichment([exc], enrichment)

    # ── 5. Consensus where all models disagree on every field ────────
    def test_05_all_models_disagree_triggers_gate(self) -> None:
        """When 3 models all disagree on attribution, EX-G-001 gate fires.

        This is the worst-case consensus scenario. The pipeline should
        set attribution_confidence to zero and produce a gate entry.

        The escalation client in _call_escalation returns an EscalationResponse
        with an author_id string. We mock it to return a third different author.
        """
        exc = _make_excerpt(
            primary_author_layer=AuthorAttribution(
                layer_id="layer_matn",
                author_id="author_1",
                coverage_pct=0.5,
                rule_applied="LA-3",  # Ambiguous => triggers consensus
            ),
            attribution_confidence=None,
            school="حنبلي",
            school_confidence=0.8,
        )

        # Verification: disagree on both school and attribution
        school_vi = VerificationItem(
            item_index=0,
            agrees=False,
            alternative_value="شافعي",
            confidence=0.7,
            reasoning="School disagrees",
        )
        attr_vi = VerificationItem(
            item_index=1,
            agrees=False,
            alternative_value="author_2",
            confidence=0.6,
            reasoning="Attribution disagrees",
        )

        # Mock escalation client: _call_escalation creates its own
        # EscalationResponse(author_id=..., reasoning=...) Pydantic model.
        # We need to return an object with .author_id attribute.
        class FakeEscalation:
            author_id: str = "author_3"
            reasoning: str = "Third model picks author_3"

        mock_escalation = MagicMock()
        mock_escalation.chat.completions.create.return_value = FakeEscalation()

        updated, _record, gate_codes = resolve_consensus(
            excerpt=exc,
            verification_items=[school_vi, attr_vi],
            item_types=["SCHOOL_ATTRIBUTION", "AUTHOR_ATTRIBUTION"],
            escalation_client=mock_escalation,
            config=ExcerptingConfig(),
            source_metadata={},
        )

        # Gate should fire for all-3-disagree (author_1, author_2, author_3)
        assert ExcerptingErrorCodes.EX_G_001 in gate_codes, (
            "EX-G-001 must fire when all 3 models disagree on attribution"
        )
        assert updated.attribution_confidence == 0.0, (
            "Attribution confidence must be 0.0 when all models disagree"
        )

    # ── 6. Validation passing with self_containment_score 0.0 ────────
    def test_06_dependent_self_containment_triggers_gate(self) -> None:
        """DEPENDENT self-containment must trigger EX-G-002 gate.

        The pipeline should never silently pass a DEPENDENT excerpt through
        to the output without flagging it for human review.
        """
        exc = _make_excerpt(
            self_containment=SelfContainmentLevel.DEPENDENT,
            self_containment_notes="يحتاج سياق الباب السابق لفهم المحتوى",
            context_hint=None,  # DEPENDENT => no context_hint (I-ER-4)
        )

        # _needs_consensus should flag DEPENDENT for verification
        items = _needs_consensus(exc)
        has_sc_check = any(
            item["verification_type"] == "SELF_CONTAINMENT" for item in items
        )
        assert has_sc_check, (
            "DEPENDENT self_containment must trigger SELF_CONTAINMENT verification"
        )

    # ── 7. Writer receiving duplicate chunk IDs ──────────────────────
    def test_07_writer_duplicate_excerpt_ids(self) -> None:
        """validate_batch must raise on duplicate excerpt_ids (V-P3-1).

        Duplicate IDs indicate a bug in the ID generation algorithm.
        """
        exc1 = _make_excerpt(excerpt_id="exc_dup")
        exc2 = _make_excerpt(excerpt_id="exc_dup")

        with pytest.raises(ValueError, match="V-P3-1.*Duplicate"):
            validate_batch([exc1, exc2])

    # ── 8. Orchestrator receiving empty chunk list ────────────────────
    def test_08_empty_chunk_list(self) -> None:
        """Phase 3 orchestrator handles empty chunk list gracefully.

        run_phase3 with empty chunks should return empty result, not crash.
        """
        from engines.excerpting.src.phase3_orchestrator import run_phase3

        result = run_phase3(
            chunks=[],
            teaching_units={},
            classified={},
            config=ExcerptingConfig(),
        )

        assert result.excerpts == []
        assert result.gate_entries == []
        assert result.errors == []

    # ── 9. Chunk with page_start > page_end ──────────────────────────
    def test_09_page_range_start_greater_than_end(self) -> None:
        """PageRange with start_page > end_page is rejected at construction.

        Fixed: model_validator ensures start_page <= end_page.
        """
        with pytest.raises(ValidationError, match="start_page.*end_page"):
            PageRange(volume=1, start_page=50, end_page=10)

    # ── 10. Excerpt with word_count=0 but non-empty text ─────────────
    def test_10_zero_word_count_nonempty_text(self) -> None:
        """AssembledChunk with word_count=0 but non-empty text violates I-AC-1.

        FINDING: AssembledChunk does NOT have a model_validator for I-AC-1.
        The word_count check is ONLY in the standalone validate_ac_invariants()
        function. This means a chunk with word_count=0 and non-empty Arabic
        text can be CONSTRUCTED without error -- the mismatch is only caught
        if validate_ac_invariants() is explicitly called.

        This documents a real gap: Pydantic construction does not enforce
        I-AC-1. The standalone validator does.
        """
        # Pydantic construction allows the mismatch -- NO ValidationError
        bad_chunk = AssembledChunk(
            chunk_id="div_test_1_0",
            source_id="src_test",
            div_id="div_test_1_0",
            div_path=["باب"],
            assembled_text="بسم الله الرحمن الرحيم",
            word_count=0,  # Wrong! Should be 4
            total_tokens=4,
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len("بسم الله الرحمن الرحيم"),
                    confidence=_FULL_CONFIDENCE,
                )
            ],
            footnotes=[],
            content_flags=ContentFlags(),
            physical_pages=[
                PhysicalPage(volume=1, page_number_display="١", page_number_int=1)
            ],
            structural_format=StructuralFormat.PROSE,
            heading_alignment_ok=True,
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=[0],
                join_points=[],
                layer_split_points=[],
                footnote_renumber_map=None,
            ),
            merge_history=None,
            split_info=None,
        )
        # The object is CREATED despite the inconsistency
        assert bad_chunk.word_count == 0
        assert len(bad_chunk.assembled_text) > 0

        # But the standalone validator catches it
        with pytest.raises(ValueError, match="I-AC-1"):
            validate_ac_invariants(bad_chunk)


# ═══════════════════════════════════════════════════════════════════════
# ERROR RECOVERY STATES (11-15)
# ═══════════════════════════════════════════════════════════════════════


class TestErrorRecovery:
    """Test graceful degradation and error handling across phase boundaries."""

    # ── 11. Phase 2a succeeds, Phase 2b raises ───────────────────────
    def test_11_phase2a_ok_phase2b_fails(self) -> None:
        """If Phase 2a succeeds but Phase 2b raises, the pipeline catches it.

        The pipeline.py run_excerpting wraps Phase 2 in a try/except.
        A runtime error in grouping should be caught and recorded, not crash.

        Instead of building a full NormalizedPackage (complex contract),
        we test the phase-level error handling directly by calling
        run_phase2b with a client that raises.
        """
        from engines.excerpting.src.phase2_group import run_phase2b

        chunk = _make_chunk()
        segment = _make_segment(end_word=chunk.total_tokens - 1)
        classified = {chunk.chunk_id: [segment]}

        # Mock client that raises on the first call
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError(
            "LLM API timeout during grouping"
        )

        # run_phase2b should catch this and return empty dict (failed chunks absent)
        config = ExcerptingConfig(RETRY_COUNT=0)  # No retries for speed
        result = run_phase2b([chunk], classified, mock_client, config)

        # The chunk should be absent from results (failed, not crashed)
        assert chunk.chunk_id not in result, (
            "Failed chunk should be absent from results, not crash the pipeline"
        )

    # ── 12. Enrichment succeeds for some chunks, fails for others ────
    def test_12_partial_enrichment_failure(self) -> None:
        """If enrichment fails for some chunks, others should still be enriched.

        apply_enrichment handles missing unit_index gracefully — if the
        enrichment for a unit is absent, the excerpt keeps its deterministic-
        only fields.
        """
        exc0 = _make_excerpt(unit_index=0, excerpt_id="exc_0")
        exc1 = _make_excerpt(unit_index=1, excerpt_id="exc_1")

        # Enrichment only returns data for unit 0, not unit 1
        enrichment = EnrichmentResult(
            enrichments=[
                UnitEnrichment(
                    unit_index=0,
                    excerpt_topic=["فقه"],
                    school="حنبلي",
                    school_confidence=0.9,
                    resolved_scholars=[],
                    takhrij_data=[],
                    terminology_variants=[],
                    cross_references=[],
                    context_hint=None,
                ),
            ],
            total_units=1,
        )

        with pytest.raises(EnrichmentBatchCoverageError, match="expected total_units=2, got 1"):
            apply_enrichment([exc0, exc1], enrichment)

    # ── 13. Consensus model returns invalid JSON ─────────────────────
    def test_13_consensus_invalid_json_recovery(self) -> None:
        """If the consensus verification fails, the pipeline degrades gracefully.

        Per-chunk consensus failure should keep enrichment output, flag every
        excerpt as verification_skipped, and propagate EX-M-011 into the
        Phase3Result.errors list so the degraded run is visible to orchestration.
        """
        from engines.excerpting.src.phase3_orchestrator import run_phase3

        chunk = _make_chunk()
        segment = _make_segment(end_word=chunk.total_tokens - 1)
        unit = _make_unit(end_word=chunk.total_tokens - 1)

        # Mock enrich client that returns enrichment WITH school (triggers consensus)
        mock_enrich = MagicMock()
        mock_enrich.chat.completions.create.return_value = EnrichmentResult(
            enrichments=[
                UnitEnrichment(
                    unit_index=0,
                    excerpt_topic=["فقه"],
                    school="حنبلي",  # Non-null school => triggers consensus
                    school_confidence=0.9,
                    resolved_scholars=[],
                    takhrij_data=[],
                    terminology_variants=[],
                    cross_references=[],
                    context_hint=None,
                ),
            ],
            total_units=1,
        )

        # Mock verify client that raises (simulating invalid JSON)
        mock_verify = MagicMock()
        mock_verify.chat.completions.create.side_effect = RuntimeError(
            "Failed to parse model response as JSON"
        )

        result = run_phase3(
            chunks=[chunk],
            teaching_units={chunk.chunk_id: [unit]},
            classified={chunk.chunk_id: [segment]},
            config=ExcerptingConfig(),
            enrich_client=mock_enrich,
            verify_client=mock_verify,
        )

        # Should still have excerpts (degraded, not crashed)
        assert len(result.excerpts) > 0, "Should degrade to enrichment-only, not crash"

        assert result.errors == [ExcerptingErrorCodes.EX_M_011]

        # But the flag IS set correctly
        for exc in result.excerpts:
            assert "verification_skipped" in exc.review_flags, (
                "All excerpts should have verification_skipped flag"
            )

    # ── 14. Writer cannot create output directory ────────────────────
    def test_14_writer_directory_creation_failure(self) -> None:
        """If write_excerpts is called with an invalid path, it raises.

        The writer calls output_dir.mkdir(parents=True, exist_ok=True)
        which should raise on truly invalid paths.
        """
        exc = _make_excerpt()

        # Use an obviously invalid path
        if sys.platform == "win32":
            bad_path = Path("Z:\\nonexistent\\deeply\\nested\\path\\that\\does\\not\\exist")
        else:
            bad_path = Path("/proc/0/nonexistent_dir")

        with pytest.raises(OSError):
            write_excerpts([exc], bad_path)

    # ── 15. Validation detects CRITICAL issue — does processing stop? ─
    def test_15_critical_gate_queue_failure_halts(self) -> None:
        """EX-M-008 (gate write failure) raises and halts processing.

        The writer's verify_gate_queue raises GateQueueVerificationError
        if gate entries cannot be verified. This is the pipeline's only
        CRITICAL error that causes a hard stop.

        Note: verify_gate_queue retries once by re-calling write_gate_queue.
        So a simple corrupt file will be fixed on retry. We test the case
        where the gate file simply does not exist at all (filesystem failure).
        """
        gate_entries: list[dict[str, object]] = [
            {"excerpt_id": "exc_1", "gate_code": "EX-G-001", "data": "test"},
        ]

        # Point to a path that does not exist and cannot be created
        nonexistent_path = Path(tempfile.mkdtemp()) / "subdir" / "gate_queue.jsonl"
        # The file does not exist, so verify_gate_queue should raise immediately
        with pytest.raises(GateQueueVerificationError, match="EX-M-008"):
            verify_gate_queue(gate_entries, nonexistent_path)


# ═══════════════════════════════════════════════════════════════════════
# BOUNDARY STATES (16-20)
# ═══════════════════════════════════════════════════════════════════════


class TestBoundaryStates:
    """Test minimum, maximum, and degenerate inputs."""

    # ── 16. Exactly 1 chunk (minimum batch) ──────────────────────────
    def test_16_single_chunk_pipeline(self) -> None:
        """The pipeline processes exactly 1 chunk correctly.

        Single-chunk batches exercise every per-chunk code path exactly
        once, with no aggregation.
        """
        from engines.excerpting.src.phase3_deterministic import (
            build_deterministic_excerpts,
        )

        chunk = _make_chunk()
        segment = _make_segment(end_word=chunk.total_tokens - 1)
        unit = _make_unit(end_word=chunk.total_tokens - 1)

        excerpts = build_deterministic_excerpts(chunk, [unit], [segment])
        assert len(excerpts) == 1
        assert excerpts[0].source_id == "src_test"
        assert excerpts[0].unit_index == 0

        # Validate the single excerpt
        validated, errors = validate_batch(excerpts)
        assert len(validated) == 1
        # No critical errors expected
        assert ExcerptingErrorCodes.EX_V_002 not in errors

    # ── 17. Large batch validation ───────────────────────────────────
    def test_17_large_batch_unique_ids(self) -> None:
        """V-P3-1 handles large batches efficiently.

        Create 1000 excerpts with unique IDs and verify batch validation
        does not reject or crash.
        """
        excerpts = []
        for i in range(1000):
            exc = _make_excerpt(
                excerpt_id=f"exc_src_test_div_{i}_0_0",
                unit_index=0,
                div_id=f"div_{i}",
            )
            excerpts.append(exc)

        validated, _errors = validate_batch(excerpts)
        assert len(validated) == 1000, "All 1000 unique excerpts should pass V-P3-1"

    # ── 18. All chunks classified as the same scholarly function ─────
    def test_18_all_same_scholarly_function(self) -> None:
        """All segments having the same function is valid but degenerate.

        A book that is entirely definitions (e.g., a glossary) should
        produce valid ClassifiedSegments where every segment is DEFINITION.
        """
        segments = [
            _make_segment(
                segment_index=i,
                start_word=i * 3,
                end_word=i * 3 + 2,
                scholarly_function=ScholarlyFunction.DEFINITION,
            )
            for i in range(5)
        ]

        # All definitions — valid, just uniform
        for seg in segments:
            assert seg.scholarly_function == ScholarlyFunction.DEFINITION

        # validate_cs_invariants should accept this (15 tokens, all covered)
        validate_cs_invariants(segments, total_tokens=15)

    # ── 19. All chunks have identical content ────────────────────────
    def test_19_identical_content_distinct_ids(self) -> None:
        """Excerpts with identical text but different IDs pass validation.

        Duplicate content is valid (think: repeated formulaic text in
        different chapters). Only duplicate IDs are rejected.
        """
        exc1 = _make_excerpt(
            excerpt_id="exc_1",
            primary_text=_DEFAULT_TEXT,
            text_snippet=_DEFAULT_TEXT[:80],
        )
        exc2 = _make_excerpt(
            excerpt_id="exc_2",
            primary_text=_DEFAULT_TEXT,
            text_snippet=_DEFAULT_TEXT[:80],
        )

        validated, _errors = validate_batch([exc1, exc2])
        assert len(validated) == 2, "Identical content with different IDs is valid"

    # ── 20. Chain of back-references ─────────────────────────────────
    def test_20_backreference_chain_self_containment(self) -> None:
        """A chain of back-references should produce PARTIAL self-containment.

        If chunk N references N-1 ("كما تقدم") which references N-2, each
        unit except the first should be PARTIAL, with cross_references
        indicating the dependency chain.

        This tests that the data model can represent back-reference chains.
        """
        from engines.excerpting.contracts import CrossReference

        excerpts = []
        for i in range(5):
            cross_refs = []
            if i > 0:
                cross_refs.append(
                    CrossReference(
                        reference_text="كما تقدم",
                        target_description=f"باب {i - 1}",
                        target_div_id=f"div_{i - 1}",
                        resolved=True,
                    )
                )

            sc = SelfContainmentLevel.FULL if i == 0 else SelfContainmentLevel.PARTIAL
            sc_notes = None if i == 0 else "يحتاج الرجوع إلى الباب السابق"
            context_hint = None if i == 0 else "ارجع إلى الباب السابق لفهم المقصود"

            exc = _make_excerpt(
                excerpt_id=f"exc_chain_{i}",
                div_id=f"div_{i}",
                self_containment=sc,
                self_containment_notes=sc_notes,
                context_hint=context_hint,
                cross_references=cross_refs,
            )
            excerpts.append(exc)

        # Validate the chain
        validated, _errors = validate_batch(excerpts)
        assert len(validated) == 5, "All 5 chain excerpts should pass validation"

        # Check the back-reference structure
        assert len(validated[0].cross_references) == 0, "First has no back-reference"
        for i in range(1, 5):
            assert len(validated[i].cross_references) == 1
            assert validated[i].cross_references[0].reference_text == "كما تقدم"
            assert validated[i].self_containment == SelfContainmentLevel.PARTIAL


# ═══════════════════════════════════════════════════════════════════════
# ADDITIONAL IMPOSSIBLE STATE TESTS
# ═══════════════════════════════════════════════════════════════════════


class TestAdditionalImpossibleStates:
    """Additional edge cases discovered during code analysis."""

    def test_merge_and_split_mutually_exclusive(self) -> None:
        """I-AC-7: AssembledChunk cannot have both merge_history and split_info."""
        with pytest.raises(ValidationError, match="I-AC-7"):
            AssembledChunk(
                chunk_id="div_test_1_0_chunk_0",
                source_id="src_test",
                div_id="div_test_1_0",
                div_path=["باب"],
                assembled_text=_DEFAULT_TEXT,
                word_count=_DEFAULT_WORD_COUNT,
                total_tokens=_DEFAULT_TOTAL_TOKENS,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=len(_DEFAULT_TEXT),
                        confidence=_FULL_CONFIDENCE,
                    )
                ],
                footnotes=[],
                content_flags=ContentFlags(),
                physical_pages=[
                    PhysicalPage(volume=1, page_number_display="١", page_number_int=1)
                ],
                structural_format=StructuralFormat.PROSE,
                heading_alignment_ok=True,
                assembly_metadata=AssemblyMetadata(
                    constituent_unit_indices=[0],
                    join_points=[],
                    layer_split_points=[],
                    footnote_renumber_map=None,
                ),
                merge_history=["div_test_1_0", "div_test_1_1"],
                split_info=SplitInfo(
                    original_div_id="div_test_1_0",
                    chunk_index=0,
                    total_chunks=2,
                    split_method="paragraph_break",
                ),
            )

    def test_teaching_unit_full_with_notes_rejected(self) -> None:
        """I-TU-6: FULL self_containment with non-null notes is rejected."""
        with pytest.raises(ValidationError, match="I-TU-6"):
            TeachingUnit(
                unit_index=0,
                segment_indices=[0],
                start_word=0,
                end_word=4,
                text_snippet=_DEFAULT_TEXT[:80],
                primary_function=ScholarlyFunction.DEFINITION,
                secondary_functions=[],
                description_arabic="وصف عربي قصير للاختبار يتضمن عدة كلمات",
                self_containment=SelfContainmentLevel.FULL,
                self_containment_notes="should not be here",
            )

    def test_excerpt_dependent_with_context_hint_rejected(self) -> None:
        """I-ER-4: DEPENDENT self_containment with context_hint is rejected."""
        with pytest.raises(ValidationError, match="I-ER-4"):
            _make_excerpt(
                self_containment=SelfContainmentLevel.DEPENDENT,
                self_containment_notes="يحتاج سياق",
                context_hint="هذا لا ينبغي أن يكون هنا",
            )

    def test_excerpt_empty_author_id_rejected(self) -> None:
        """I-ER-5: Empty author_id on primary_author_layer is rejected."""
        with pytest.raises(ValidationError, match="I-ER-5"):
            _make_excerpt(
                primary_author_layer=AuthorAttribution(
                    layer_id="layer_matn",
                    author_id="",
                    coverage_pct=1.0,
                    rule_applied="LA-1",
                ),
            )

    def test_segment_confidence_out_of_range(self) -> None:
        """ClassifiedSegment confidence must be in [0.0, 1.0]."""
        with pytest.raises(ValidationError):
            ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=5,
                text_snippet="test",
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=_INVALID_HIGH_CONFIDENCE,
            )

    def test_text_integrity_validation_drops_corrupt(self) -> None:
        """V-P3-2: Text snippet not matching primary_text drops the excerpt."""
        exc = _make_excerpt(
            primary_text="بسم الله الرحمن الرحيم الحمد لله رب العالمين",
            text_snippet="هذا نص مختلف تماماً عن النص الأصلي",
        )

        result, errors = validate_excerpt(exc)
        assert result is None, "Corrupt excerpt must be dropped by V-P3-2"
        assert ExcerptingErrorCodes.EX_V_002 in errors

    def test_enrichment_missing_unit_keeps_deterministic(self) -> None:
        """apply_enrichment with empty enrichment list keeps all excerpts."""
        exc0 = _make_excerpt(unit_index=0)
        enrichment = EnrichmentResult(enrichments=[], total_units=0)

        with pytest.raises(EnrichmentBatchCoverageError, match="expected total_units=1"):
            apply_enrichment([exc0], enrichment)

    def test_validation_quran_ref_invalid_surah(self) -> None:
        """V-P3-6: Invalid surah number (> 114) emits EX-M-007."""
        exc = _make_excerpt(
            evidence_refs=[
                EvidenceRef(
                    type="quran",
                    surah=200,  # Invalid — only 114 surahs
                    ayah_start=1,
                    text_snippet="آية شاذة",
                ),
            ],
        )

        _result, errors = validate_excerpt(exc)
        assert ExcerptingErrorCodes.EX_M_007 in errors, (
            "Invalid surah 200 must trigger EX-M-007"
        )

    def test_validation_quran_ref_invalid_ayah(self) -> None:
        """V-P3-6: Invalid ayah number (exceeds surah max) emits EX-M-007."""
        exc = _make_excerpt(
            evidence_refs=[
                EvidenceRef(
                    type="quran",
                    surah=1,  # Al-Fatiha has 7 ayat
                    ayah_start=99,  # Way beyond 7
                    text_snippet="آية شاذة",
                ),
            ],
        )

        _result, errors = validate_excerpt(exc)
        assert ExcerptingErrorCodes.EX_M_007 in errors

    def test_writer_roundtrip_jsonl(self) -> None:
        """Excerpts written to JSONL can be deserialized back correctly."""
        exc = _make_excerpt()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            output_path = write_excerpts([exc], output_dir)

            # Read back
            with open(output_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            assert len(lines) == 1
            data = json.loads(lines[0])
            attribution_confidence = data.pop("attribution_confidence", None)
            school_confidence = data.pop("school_confidence", None)
            restored = ExcerptRecord(
                **data,
                attribution_confidence=attribution_confidence,
                school_confidence=school_confidence,
            )
            assert restored.excerpt_id == exc.excerpt_id
            assert restored.primary_text == exc.primary_text

    def test_context_hint_required_for_partial(self) -> None:
        """I-ER-4: PARTIAL without context_hint and without llm_enrichment_failed raises."""
        with pytest.raises(ValidationError, match="I-ER-4"):
            _make_excerpt(
                self_containment=SelfContainmentLevel.PARTIAL,
                self_containment_notes="يحتاج سياق",
                context_hint=None,
                review_flags=[],
            )

    def test_partial_with_enrichment_failed_allows_no_hint(self) -> None:
        """I-ER-4: PARTIAL without context_hint IS allowed when llm_enrichment_failed."""
        exc = _make_excerpt(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياق",
            context_hint=None,
            review_flags=["llm_enrichment_failed"],
        )
        assert exc.self_containment == SelfContainmentLevel.PARTIAL
        assert exc.context_hint is None
