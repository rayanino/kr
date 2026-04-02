"""Tests for Phase 3 LLM Enrichment (SPEC §7.2).

All tests use mocked LLM clients — no real API calls.
Tests cover: system prompt construction, user message formatting,
enrichment application, failure graceful degradation, scholar merge.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from engines.excerpting.contracts import (
    CrossReference,
    EnrichmentResult,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ResolvedScholar,
    ScholarAttribution,
    ScholarlyFunction,
    SelfContainmentLevel,
    TakhrijEntry,
    TermVariant,
    UnitEnrichment,
)
from engines.excerpting.src.phase3_enrichment import (
    ENRICH_SYSTEM_PROMPT,
    EnrichmentBatchCoverageError,
    _build_enrichment_user_message,
    _merge_scholars,
    apply_enrichment,
    enrich_chunk,
    run_phase3_enrichment,
)

# Import test factories
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_excerpt_record,
    _make_mock_instructor_client,
)

_FULL_CONFIDENCE = float("1")


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════


_ARABIC_TEXT = "بسم الله الرحمن الرحيم وبعد فإن الوضوء شرط من شروط الصلاة"
_SOURCE_META = {
    "author_name": "ابن قدامة",
    "work_title": "المغني",
    "science": "فقه",
    "source_school": "حنبلي",
}


def _make_unit_enrichment(unit_index: int = 0, **overrides: Any) -> UnitEnrichment:
    """Factory for UnitEnrichment with sensible defaults."""
    defaults: dict[str, Any] = {
        "unit_index": unit_index,
        "excerpt_topic": ["شروط الوضوء"],
        "school": "حنبلي",
        "school_confidence": 0.85,
        "resolved_scholars": [],
        "takhrij_data": [],
        "terminology_variants": [],
        "cross_references": [],
        "context_hint": None,
    }
    defaults.update(overrides)
    return UnitEnrichment(**defaults)


def _make_enrichment_result(
    n_units: int = 1, **overrides: Any
) -> EnrichmentResult:
    """Factory for EnrichmentResult."""
    enrichments = [_make_unit_enrichment(i) for i in range(n_units)]
    if "enrichments" in overrides:
        enrichments = overrides.pop("enrichments")
    return EnrichmentResult(
        enrichments=enrichments,
        total_units=len(enrichments),
        **overrides,
    )


# ═══════════════════════════════════════════════════════════════════
# 1. System Prompt Construction
# ═══════════════════════════════════════════════════════════════════


class TestSystemPrompt:
    """Verify system prompt contains required §7.2.2 elements."""

    def test_prompt_contains_arabic_expert_declaration(self) -> None:
        assert "تحليل النصوص العلمية الإسلامية" in ENRICH_SYSTEM_PROMPT

    def test_prompt_contains_all_7_fields(self) -> None:
        assert "TOPIC KEYWORDS" in ENRICH_SYSTEM_PROMPT
        assert "SCHOOL ATTRIBUTION" in ENRICH_SYSTEM_PROMPT
        assert "QUOTED SCHOLAR RESOLUTION" in ENRICH_SYSTEM_PROMPT
        assert "TAKHRIJ DATA" in ENRICH_SYSTEM_PROMPT
        assert "TERMINOLOGY VARIANTS" in ENRICH_SYSTEM_PROMPT
        assert "CROSS-REFERENCES" in ENRICH_SYSTEM_PROMPT
        assert "CONTEXT HINT" in ENRICH_SYSTEM_PROMPT

    def test_prompt_contains_school_position_distinction(self) -> None:
        """§7.2.2: Attribute the POSITION, not the AUTHOR."""
        assert "POSITION" in ENRICH_SYSTEM_PROMPT
        assert "AUTHOR" in ENRICH_SYSTEM_PROMPT

    def test_prompt_contains_hadith_grade_prohibition(self) -> None:
        """§7.2.2: Do NOT invent or infer grades."""
        assert "Do NOT invent" in ENRICH_SYSTEM_PROMPT

    def test_prompt_contains_epithet_resolution(self) -> None:
        """§7.2.2: Common epithets are context-dependent."""
        assert "الإمام" in ENRICH_SYSTEM_PROMPT
        assert "الشيخ" in ENRICH_SYSTEM_PROMPT


# ═══════════════════════════════════════════════════════════════════
# 2. User Message Formatting
# ═══════════════════════════════════════════════════════════════════


class TestUserMessage:
    """Verify user message matches §7.2.3 template."""

    def test_message_contains_source_metadata(self) -> None:
        chunk = _make_assembled_chunk(assembled_text=_ARABIC_TEXT)
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            primary_text=_ARABIC_TEXT[:40],
        )
        msg = _build_enrichment_user_message(chunk, [exc], _SOURCE_META)

        assert "<source_metadata>" in msg
        assert "ابن قدامة" in msg
        assert "المغني" in msg
        assert "فقه" in msg
        assert "حنبلي" in msg

    def test_message_contains_full_text(self) -> None:
        chunk = _make_assembled_chunk(assembled_text=_ARABIC_TEXT)
        exc = _make_excerpt_record(div_id=chunk.div_id)
        msg = _build_enrichment_user_message(chunk, [exc], _SOURCE_META)

        assert "<text>" in msg
        assert _ARABIC_TEXT in msg
        assert "</text>" in msg

    def test_message_contains_unit_details(self) -> None:
        chunk = _make_assembled_chunk(assembled_text=_ARABIC_TEXT)
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            unit_index=0,
            start_word=0,
            end_word=4,
            primary_function=ScholarlyFunction.DEFINITION,
            self_containment=SelfContainmentLevel.FULL,
        )
        msg = _build_enrichment_user_message(chunk, [exc], _SOURCE_META)

        assert "Unit 0:" in msg
        assert "function: definition" in msg
        assert "self_containment: FULL" in msg

    def test_message_contains_evidence_summary(self) -> None:
        from engines.excerpting.contracts import EvidenceRef

        chunk = _make_assembled_chunk(assembled_text=_ARABIC_TEXT)
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            evidence_refs=[
                EvidenceRef(type="quran", text_snippet="﴿بسم الله﴾")
            ],
        )
        msg = _build_enrichment_user_message(chunk, [exc], _SOURCE_META)
        assert "evidence_detected:" in msg
        assert "quran" in msg

    def test_message_no_evidence_shows_none(self) -> None:
        chunk = _make_assembled_chunk(assembled_text=_ARABIC_TEXT)
        exc = _make_excerpt_record(div_id=chunk.div_id, evidence_refs=[])
        msg = _build_enrichment_user_message(chunk, [exc], _SOURCE_META)
        assert "evidence_detected: none" in msg


# ═══════════════════════════════════════════════════════════════════
# 3. Enrichment Application
# ═══════════════════════════════════════════════════════════════════


class TestApplyEnrichment:
    """Verify fields correctly merged, unit_index matching, edge cases."""

    def test_apply_updates_all_fields(self) -> None:
        exc = _make_excerpt_record(
            unit_index=0,
            school=None,
            excerpt_topic=[],
            review_flags=["llm_enrichment_failed"],
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint=None,
        )
        ue = _make_unit_enrichment(
            unit_index=0,
            excerpt_topic=["أحكام الوضوء", "شروط الصلاة"],
            school="حنبلي",
            school_confidence=0.9,
            context_hint="هذا في سياق باب الطهارة",
            terminology_variants=[
                TermVariant(term="الوضوء", variants=["الطهارة الصغرى"])
            ],
            cross_references=[
                CrossReference(
                    reference_text="كما تقدم",
                    target_description="باب الطهارة",
                    resolved=False,
                )
            ],
        )
        enrichment = EnrichmentResult(enrichments=[ue], total_units=1)

        result = apply_enrichment([exc], enrichment)
        assert len(result) == 1
        r = result[0]

        assert r.excerpt_topic == ["أحكام الوضوء", "شروط الصلاة"]
        assert r.school == "حنبلي"
        assert r.school_confidence == 0.9
        assert r.context_hint == "هذا في سياق باب الطهارة"
        assert len(r.terminology_variants) == 1
        assert len(r.cross_references) == 1
        assert "llm_enrichment_failed" not in r.review_flags

    def test_apply_with_takhrij_data(self) -> None:
        exc = _make_excerpt_record(unit_index=0, takhrij_data=None)
        ue = _make_unit_enrichment(
            unit_index=0,
            takhrij_data=[
                TakhrijEntry(
                    hadith_text_snippet="من توضأ فأحسن الوضوء",
                    collections=["صحيح مسلم"],
                    hadith_numbers=["245"],
                    grade="صحيح",
                    grade_source="المؤلف",
                )
            ],
        )
        enrichment = EnrichmentResult(enrichments=[ue], total_units=1)

        result = apply_enrichment([exc], enrichment)
        assert result[0].takhrij_data is not None
        assert len(result[0].takhrij_data) == 1
        assert result[0].takhrij_data[0].collections == ["صحيح مسلم"]

    def test_apply_empty_enrichment_keeps_deterministic(self) -> None:
        """Empty enrichment batches must fail loudly instead of looking successful."""
        exc = _make_excerpt_record(unit_index=0)
        enrichment = EnrichmentResult(enrichments=[], total_units=0)

        with pytest.raises(EnrichmentBatchCoverageError, match="expected total_units=1"):
            apply_enrichment([exc], enrichment)

    def test_apply_mismatched_unit_index_keeps_original(self) -> None:
        """Mismatched unit coverage must fail loudly instead of passing through."""
        exc = _make_excerpt_record(unit_index=0)
        ue = _make_unit_enrichment(unit_index=99)
        enrichment = EnrichmentResult(enrichments=[ue], total_units=1)

        with pytest.raises(EnrichmentBatchCoverageError, match="missing=\\[0\\], extra=\\[99\\]"):
            apply_enrichment([exc], enrichment)

    def test_apply_context_hint_only_for_partial(self) -> None:
        """I-ER-4: context_hint only for PARTIAL, not FULL or DEPENDENT."""
        exc_full = _make_excerpt_record(
            unit_index=0,
            self_containment=SelfContainmentLevel.FULL,
        )
        ue = _make_unit_enrichment(
            unit_index=0,
            context_hint="هذا السياق",  # LLM erroneously provides hint
        )
        enrichment = EnrichmentResult(enrichments=[ue], total_units=1)

        result = apply_enrichment([exc_full], enrichment)
        # FULL → context_hint should remain None (I-ER-4)
        assert result[0].context_hint is None

    def test_apply_multiple_units(self) -> None:
        """Multiple units in one chunk all get enriched."""
        excerpts = [
            _make_excerpt_record(
                unit_index=i,
                excerpt_id=f"exc_test_{i}",
            )
            for i in range(3)
        ]
        enrichments = [
            _make_unit_enrichment(
                unit_index=i,
                excerpt_topic=[f"موضوع {i}"],
            )
            for i in range(3)
        ]
        er = EnrichmentResult(enrichments=enrichments, total_units=3)

        result = apply_enrichment(excerpts, er)
        assert len(result) == 3
        for i, r in enumerate(result):
            assert r.excerpt_topic == [f"موضوع {i}"]


# ═══════════════════════════════════════════════════════════════════
# 4. Failure Graceful Degradation
# ═══════════════════════════════════════════════════════════════════


class TestGracefulDegradation:
    """On LLM error → EX-M-002 emitted, review_flag set, deterministic fields survive."""

    def test_enrichment_failure_emits_ex_m_002(self, caplog: pytest.LogCaptureFixture) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(div_id=chunk.div_id)
        client = _make_mock_instructor_client(
            side_effect=Exception("API timeout")
        )
        config = ExcerptingConfig()

        with caplog.at_level("ERROR"):
            result = run_phase3_enrichment([exc], [chunk], client, config)

        assert len(result) == 1
        assert "llm_enrichment_failed" in result[0].review_flags

    def test_enrichment_failure_appends_ex_m_002_to_error_sink(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(div_id=chunk.div_id)
        client = _make_mock_instructor_client(
            side_effect=Exception("API timeout")
        )
        config = ExcerptingConfig()
        errors: list[str] = []

        result = run_phase3_enrichment(
            [exc], [chunk], client, config, error_sink=errors
        )

        assert len(result) == 1
        assert "llm_enrichment_failed" in result[0].review_flags
        assert errors == [ExcerptingErrorCodes.EX_M_002]

    def test_deterministic_fields_survive_failure(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            primary_text="بسم الله الرحمن الرحيم",
            excerpt_topic=[],
        )
        client = _make_mock_instructor_client(
            side_effect=Exception("LLM error")
        )
        config = ExcerptingConfig()

        result = run_phase3_enrichment([exc], [chunk], client, config)

        # Deterministic fields intact
        assert result[0].primary_text == "بسم الله الرحمن الرحيم"
        assert result[0].primary_function == exc.primary_function
        assert result[0].div_path == exc.div_path
        assert result[0].primary_author_layer == exc.primary_author_layer

    def test_retry_count_respected(self) -> None:
        """Should try 1 + RETRY_COUNT times before giving up."""
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(div_id=chunk.div_id)
        client = _make_mock_instructor_client(
            side_effect=Exception("fail")
        )
        config = ExcerptingConfig(RETRY_COUNT=2)

        run_phase3_enrichment([exc], [chunk], client, config)

        # 1 + 2 = 3 attempts
        assert client.chat.completions.create.call_count == 3

    def test_chunk_remap_miss_emits_ex_m_002_without_llm_call(self) -> None:
        missing_chunk_id = "missing_div"
        exc = _make_excerpt_record(
            div_id=missing_chunk_id,
            primary_text="بسم الله الرحمن الرحيم",
            excerpt_topic=[],
        )
        client = _make_mock_instructor_client(return_value=_make_enrichment_result(1))
        progress = MagicMock()
        config = ExcerptingConfig()
        errors: list[str] = []

        result = run_phase3_enrichment(
            [exc],
            [_make_assembled_chunk()],
            client,
            config,
            _SOURCE_META,
            progress=progress,
            error_sink=errors,
        )

        assert len(result) == 1
        assert result[0].primary_text == "بسم الله الرحمن الرحيم"
        assert result[0].excerpt_topic == []
        assert "llm_enrichment_failed" in result[0].review_flags
        assert errors == [ExcerptingErrorCodes.EX_M_002]
        progress.mark_failed.assert_called_once_with(
            missing_chunk_id,
            "phase3_enrich",
            ExcerptingErrorCodes.EX_M_002,
        )
        assert client.chat.completions.create.call_count == 0


# ═══════════════════════════════════════════════════════════════════
# 5. Scholar Merge (DD-S4-4)
# ═══════════════════════════════════════════════════════════════════


class TestScholarMerge:
    """LLM resolved_scholars merged with F-DET-9 structural quoted_scholars."""

    def test_llm_scholars_added_to_structural(self) -> None:
        structural = [
            ScholarAttribution(
                mention_text="[structural: sharh]",
                resolved_name="sch_ibn_aqeel",
                role="quoted_opinion",
                confidence=_FULL_CONFIDENCE,
                source="layer_overlap",
            )
        ]
        llm = [
            ResolvedScholar(
                mention_text="الإمام أحمد",
                resolved_name="أحمد بن حنبل",
                role="quoted_opinion",
                confidence=0.9,
            )
        ]
        result = _merge_scholars(structural, llm)
        assert len(result) == 2
        assert result[0].source == "layer_overlap"
        assert result[1].source == "llm_enrichment"
        assert result[1].resolved_name == "أحمد بن حنبل"

    def test_duplicate_scholar_not_added_twice(self) -> None:
        """If LLM identifies same scholar as structural, keep the LLM entry."""
        structural = [
            ScholarAttribution(
                mention_text="[structural: sharh]",
                resolved_name="sch_ibn_aqeel",
                role="quoted_opinion",
                confidence=_FULL_CONFIDENCE,
                source="layer_overlap",
            )
        ]
        llm = [
            ResolvedScholar(
                mention_text="ابن عقيل",
                resolved_name="sch_ibn_aqeel",
                role="quoted_opinion",
                confidence=0.85,
            )
        ]
        result = _merge_scholars(structural, llm)
        assert len(result) == 1  # No duplicate
        assert result[0].mention_text == "ابن عقيل"
        assert result[0].confidence == 0.85
        assert result[0].source == "llm_enrichment"

    def test_empty_llm_scholars(self) -> None:
        structural = [
            ScholarAttribution(
                mention_text="[structural: matn]",
                resolved_name="sch_test",
                role="classification_frame",
                confidence=_FULL_CONFIDENCE,
                source="layer_overlap",
            )
        ]
        result = _merge_scholars(structural, [])
        assert len(result) == 1
        assert result[0] is structural[0]

    def test_empty_structural_scholars(self) -> None:
        llm = [
            ResolvedScholar(
                mention_text="الإمام الشافعي",
                resolved_name="الشافعي",
                role="quoted_opinion",
                confidence=0.95,
            )
        ]
        result = _merge_scholars([], llm)
        assert len(result) == 1
        assert result[0].source == "llm_enrichment"


# ═══════════════════════════════════════════════════════════════════
# 6. enrich_chunk LLM Call
# ═══════════════════════════════════════════════════════════════════


class TestEnrichChunk:
    """Verify the LLM call is made correctly."""

    def test_enrich_chunk_calls_correct_model(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(div_id=chunk.div_id)
        er = _make_enrichment_result(1)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()

        result = enrich_chunk(chunk, [exc], client, config, _SOURCE_META)

        call_kwargs = client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == config.ENRICH_MODEL
        assert call_kwargs.kwargs["temperature"] == 0.0
        assert call_kwargs.kwargs["response_model"] is EnrichmentResult
        assert result == er

    def test_enrich_chunk_passes_system_and_user_messages(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(div_id=chunk.div_id)
        er = _make_enrichment_result(1)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()

        enrich_chunk(chunk, [exc], client, config, _SOURCE_META)

        call_kwargs = client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "ابن قدامة" in messages[1]["content"]


# ═══════════════════════════════════════════════════════════════════
# 7. run_phase3_enrichment Orchestration
# ═══════════════════════════════════════════════════════════════════


class TestRunPhase3Enrichment:
    """Test the orchestrator groups by chunk and handles success/failure."""

    def test_successful_enrichment_for_single_chunk(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(
            div_id=chunk.div_id, excerpt_topic=[], school=None
        )
        er = _make_enrichment_result(1)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()

        result = run_phase3_enrichment([exc], [chunk], client, config, _SOURCE_META)

        assert len(result) == 1
        assert result[0].excerpt_topic == ["شروط الوضوء"]
        assert result[0].school == "حنبلي"

    def test_multiple_chunks_each_get_one_call(self) -> None:
        chunk1 = _make_assembled_chunk(chunk_id="div_a_0", div_id="div_a")
        chunk2 = _make_assembled_chunk(chunk_id="div_b_0", div_id="div_b")
        exc1 = _make_excerpt_record(div_id="div_a", excerpt_id="exc_a_0")
        exc2 = _make_excerpt_record(div_id="div_b", excerpt_id="exc_b_0")

        er = _make_enrichment_result(1)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()

        result = run_phase3_enrichment(
            [exc1, exc2], [chunk1, chunk2], client, config
        )
        assert len(result) == 2
        # One call per chunk
        assert client.chat.completions.create.call_count == 2

    def test_resume_cache_miss_marks_enrichment_failed(self) -> None:
        chunk = _make_assembled_chunk()
        exc = _make_excerpt_record(
            div_id=chunk.div_id,
            excerpt_topic=[],
            school=None,
        )
        client = _make_mock_instructor_client(return_value=_make_enrichment_result(1))
        config = ExcerptingConfig()
        progress = MagicMock()
        progress.is_done.side_effect = lambda _cid, phase: phase == "phase3_enrich"
        cache = MagicMock()
        cache.load.return_value = None

        result = run_phase3_enrichment(
            [exc],
            [chunk],
            client,
            config,
            _SOURCE_META,
            progress=progress,
            cache=cache,
        )

        assert len(result) == 1
        assert "llm_enrichment_failed" in result[0].review_flags
        progress.mark_failed.assert_called_once_with(
            chunk.chunk_id,
            "phase3_enrich",
            ExcerptingErrorCodes.EX_M_002,
        )
        assert client.chat.completions.create.call_count == 0

    def test_incomplete_batch_degrades_and_skips_cache_save(self) -> None:
        chunk = _make_assembled_chunk()
        exc1 = _make_excerpt_record(
            div_id=chunk.div_id,
            unit_index=0,
            excerpt_id="exc_enrich_0",
        )
        exc2 = _make_excerpt_record(
            div_id=chunk.div_id,
            unit_index=1,
            excerpt_id="exc_enrich_1",
        )
        client = _make_mock_instructor_client(
            return_value=EnrichmentResult(
                enrichments=[_make_unit_enrichment(unit_index=0)],
                total_units=1,
            )
        )
        config = ExcerptingConfig(RETRY_COUNT=0)
        progress = MagicMock()
        progress.is_done.return_value = False
        cache = MagicMock()
        cache.load.return_value = None
        errors: list[str] = []

        result = run_phase3_enrichment(
            [exc1, exc2],
            [chunk],
            client,
            config,
            _SOURCE_META,
            progress=progress,
            cache=cache,
            error_sink=errors,
        )

        assert len(result) == 2
        assert all("llm_enrichment_failed" in exc.review_flags for exc in result)
        assert errors == [ExcerptingErrorCodes.EX_M_002]
        progress.mark_failed.assert_called_once_with(
            chunk.chunk_id,
            "phase3_enrich",
            ExcerptingErrorCodes.EX_M_002,
        )
        progress.mark_done.assert_not_called()
        cache.save.assert_not_called()


# ═══════════════════════════════════════════════════════════════════
# Fix 2 Tests: PARTIAL context_hint None fallback
# ═══════════════════════════════════════════════════════════════════


class TestPartialContextHintFallback:
    """Fix 2: PARTIAL + None hint → fallback chain prevents I-ER-4 crash."""

    def test_apply_partial_with_none_hint_uses_notes_fallback(self) -> None:
        """PARTIAL + notes + LLM hint=None → uses notes as hint."""
        exc = _make_excerpt_record(
            unit_index=0,
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يعتمد على ما سبق",
            context_hint="placeholder",
            review_flags=["llm_enrichment_failed"],
        )
        ue = _make_unit_enrichment(
            unit_index=0,
            context_hint=None,  # LLM omitted it
        )
        enrichment = EnrichmentResult(enrichments=[ue], total_units=1)

        result = apply_enrichment([exc], enrichment)
        assert result[0].context_hint == "يعتمد على ما سبق"

    def test_apply_partial_with_none_hint_no_notes_uses_generic(self) -> None:
        """PARTIAL + notes present + LLM hint=None → fallback to notes, roundtrip OK."""
        exc = _make_excerpt_record(
            unit_index=0,
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="needed",
            context_hint="placeholder",
            review_flags=["llm_enrichment_failed"],
        )
        ue = _make_unit_enrichment(
            unit_index=0,
            context_hint=None,
        )
        enrichment = EnrichmentResult(enrichments=[ue], total_units=1)

        result = apply_enrichment([exc], enrichment)
        assert result[0].context_hint is not None
        # Roundtrip: model_validate MUST NOT raise
        ExcerptRecord.model_validate(result[0].model_dump())

    def test_apply_partial_roundtrip_after_enrichment(self) -> None:
        """ACID TEST: PARTIAL → apply_enrichment with hint=None → roundtrip MUST NOT raise."""
        exc = _make_excerpt_record(
            unit_index=0,
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يحتاج سياقاً",
            context_hint="placeholder",
            review_flags=["llm_enrichment_failed"],
        )
        ue = _make_unit_enrichment(
            unit_index=0,
            context_hint=None,
        )
        enrichment = EnrichmentResult(enrichments=[ue], total_units=1)

        result = apply_enrichment([exc], enrichment)
        # Roundtrip validation MUST NOT raise
        ExcerptRecord.model_validate(result[0].model_dump())


# ═══════════════════════════════════════════════════════════════════
# Fix 4 Tests: Split chunk matching (enrichment side)
# ═══════════════════════════════════════════════════════════════════


class TestSplitChunkEnrichmentMatching:
    """Fix 4: Split chunks matched by exact div_id + chunk_index."""

    def test_split_chunk_matched_correctly(self) -> None:
        """Split chunk div_1_chunk_1 matched via split_id fallback."""
        chunk = _make_assembled_chunk(
            chunk_id="div_1_chunk_1", div_id="div_1",
        )
        exc = _make_excerpt_record(
            div_id="div_1", chunk_index=1,
            excerpt_topic=[], school=None,
        )
        er = _make_enrichment_result(1)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()

        result = run_phase3_enrichment([exc], [chunk], client, config, _SOURCE_META)

        assert len(result) == 1
        # Should have been enriched (not kept as-is)
        assert result[0].excerpt_topic == ["شروط الوضوء"]
        assert client.chat.completions.create.call_count == 1
