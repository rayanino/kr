"""Tests for metadata inference — SPEC §4.A.4.

All tests mock consensus evaluate() — no real API calls.
Uses real Arabic text from Islamic scholarly sources.

Test structure:
- TestBuildPromptContext: prompt assembly from extracted metadata
- TestValidateEnumValue:  synonym mapping and fallback logic
- TestApplyConfidenceCaps: biographical and attribution caps
- TestSetTextFidelity: deterministic fidelity from format
- TestBuildNeedsReview: fields needing human review
- TestInferMetadata: full async integration with mocked consensus
"""

from __future__ import annotations

from typing import Optional
from unittest.mock import AsyncMock, patch

import pytest

from engines.source.contracts import (
    AuthorityLevel,
    Genre,
    SourceFormat,
    StructuralFormat,
    WorkLevel,
)
from engines.source.src.inference_models import (
    AuthorIdentificationOutput,
    GenreChainOutput,
    InferenceOutput,
    LayerOutput,
    ScholarlyContextOutput,
)
from engines.source.src.metadata_inference import (
    MetadataInferenceResult,
    apply_confidence_caps,
    build_needs_review,
    build_prompt_context,
    infer_metadata,
    set_text_fidelity,
    validate_enum_value,
)
from shared.consensus.src.consensus import ConsensusResult, ModelResponse


# ──────────────────────────────────────────────────────────────────
# Test helpers
# ──────────────────────────────────────────────────────────────────


def _make_output(
    genre: str = "sharh",
    author_name: str = "النووي",
    death_date: Optional[int] = 676,
    confidence: float = 0.90,
    attribution: str = "definitive",
    structural_format: str = "commentary",
    is_multi_layer: bool = True,
    layers: Optional[list[LayerOutput]] = None,
    genre_chain: Optional[GenreChainOutput] = None,
    science_scope: Optional[list[str]] = None,
    level: Optional[str] = "advanced",
    authority_level: str = "primary",
) -> InferenceOutput:
    """Build an InferenceOutput for testing.

    Defaults model a classical Arabic sharh (commentary) — the most common genre
    in the collection. Real Arabic author name النووي (al-Nawawi, d. 676 AH).
    """
    return InferenceOutput(
        genre=genre,
        genre_confidence=0.90,
        genre_chain=genre_chain,
        genre_chain_confidence=0.90 if genre_chain else None,
        structural_format=structural_format,
        structural_format_confidence=0.85,
        is_multi_layer=is_multi_layer,
        multi_layer_confidence=0.90,
        layers=layers,
        science_scope=science_scope if science_scope is not None else ["nahw"],
        science_scope_confidence=0.85,
        level=level,
        level_confidence=0.80 if level else None,
        authority_level=authority_level,
        authority_level_confidence=0.90,
        author_identification=AuthorIdentificationOutput(
            canonical_name_ar=author_name,
            death_date_hijri=death_date,
        ),
        author_identification_confidence=confidence,
        attribution_status=attribution,
    )


def _make_consensus_result(
    output_a: Optional[InferenceOutput] = None,
    output_b: Optional[InferenceOutput] = None,
    agreed: bool = True,
    needs_human_gate: bool = False,
    human_gate_trigger: Optional[str] = None,
) -> ConsensusResult:
    """Build a ConsensusResult with two model responses.

    Model B (Opus 4.6) is canonical when agreed, per _select_canonical() logic.
    """
    a = output_a or _make_output()
    b = output_b or _make_output()
    responses = [
        ModelResponse(
            model_id="openrouter/cohere/command-a",
            provider="openrouter",
            parsed=a,
            raw_response=a.model_dump(),
            parse_success=True,
            latency=1.0,
        ),
        ModelResponse(
            model_id="anthropic/claude-opus-4-6",
            provider="anthropic",
            parsed=b,
            raw_response=b.model_dump(),
            parse_success=True,
            latency=1.2,
        ),
    ]
    return ConsensusResult(
        agreed=agreed,
        canonical_result=b if agreed else None,
        model_responses=responses,
        agreement_detail="Models agreed" if agreed else "Models disagreed",
        needs_human_gate=needs_human_gate,
        human_gate_trigger=human_gate_trigger,
    )


# ──────────────────────────────────────────────────────────────────
# TestBuildPromptContext
# ──────────────────────────────────────────────────────────────────


class TestBuildPromptContext:
    """Tests for build_prompt_context()."""

    def test_shamela_full_metadata(self) -> None:
        """Full Shamela metadata — همع الهوامع (al-Suyuti's grammar commentary)."""
        extracted = {
            "display_title": "همع الهوامع في شرح جمع الجوامع",
            "author_name_raw": "عبد الرحمن بن أبي بكر، جلال الدين السيوطي",
            "publisher": "المكتبة التوفيقية",
            "muhaqiq_name": "عبد الحميد هنداوي",
            "shamela_category": "النحو والصرف",
            "edition": "الأولى",
            "page_count": 450,
            "volume_count": 3,
            "source_format": "shamela_html",
        }
        ctx = build_prompt_context(extracted)

        assert "همع الهوامع في شرح جمع الجوامع" in ctx
        assert "السيوطي" in ctx
        assert "المكتبة التوفيقية" in ctx
        assert "هنداوي" in ctx
        assert "النحو والصرف" in ctx
        assert "450" in ctx
        assert "3" in ctx

    def test_plain_text_minimal(self) -> None:
        """Plain text extractor provides only title_arabic."""
        extracted = {"title_arabic": "ألفية ابن مالك"}
        ctx = build_prompt_context(extracted)
        assert "ألفية ابن مالك" in ctx

    def test_title_precedence_display_over_title_full(self) -> None:
        """display_title takes precedence over title_full."""
        extracted = {
            "display_title": "شرح ابن عقيل",
            "title_full": "شرح ابن عقيل على ألفية ابن مالك",
        }
        ctx = build_prompt_context(extracted)
        # display_title wins
        assert ctx.startswith("Title: شرح ابن عقيل")
        # title_full is not duplicated
        assert "على ألفية ابن مالك" not in ctx

    def test_title_precedence_full_over_arabic(self) -> None:
        """title_full takes precedence over title_arabic when display_title absent."""
        extracted = {
            "title_full": "كتاب سيبويه",
            "title_arabic": "الكتاب",
        }
        ctx = build_prompt_context(extracted)
        assert "كتاب سيبويه" in ctx
        assert "الكتاب" not in ctx

    def test_muhaqiq_from_muhaqiq_field(self) -> None:
        """Falls back to 'muhaqiq' key if 'muhaqiq_name' is absent."""
        extracted = {
            "title_full": "شرح المنهاج",
            "muhaqiq": "عبد الحميد هنداوي",
        }
        ctx = build_prompt_context(extracted)
        assert "هنداوي" in ctx

    def test_author_from_author_name_fallback(self) -> None:
        """Falls back to 'author_name' when 'author_name_raw' is absent."""
        extracted = {
            "title_arabic": "الرسالة",
            "author_name": "الشافعي",
        }
        ctx = build_prompt_context(extracted)
        assert "الشافعي" in ctx

    def test_empty_extracted_returns_empty_string(self) -> None:
        """Empty dict → empty string (no lines)."""
        ctx = build_prompt_context({})
        assert ctx == ""

    def test_category_from_category_fallback(self) -> None:
        """Falls back to 'category' when 'shamela_category' is absent."""
        extracted = {
            "title_arabic": "الموافقات",
            "category": "أصول الفقه",
        }
        ctx = build_prompt_context(extracted)
        assert "أصول الفقه" in ctx


# ──────────────────────────────────────────────────────────────────
# TestValidateEnumValue
# ──────────────────────────────────────────────────────────────────


class TestValidateEnumValue:
    """Tests for validate_enum_value()."""

    def test_valid_genre_passes_direct(self) -> None:
        """Valid enum string returns itself without fallback."""
        val, fallback = validate_enum_value("sharh", Genre, {}, "other")
        assert val == "sharh"
        assert fallback is False

    def test_arabic_synonym_منظومة_maps_to_nazm(self) -> None:
        """Arabic synonym منظومة → nazm (canonical enum value)."""
        synonyms = {"منظومة": "nazm", "حاشية": "hashiyah"}
        val, fallback = validate_enum_value("منظومة", Genre, synonyms, "other")
        assert val == "nazm"
        assert fallback is True

    def test_arabic_synonym_حاشية_maps_to_hashiyah(self) -> None:
        """Arabic synonym حاشية → hashiyah."""
        synonyms = {"حاشية": "hashiyah"}
        val, fallback = validate_enum_value("حاشية", Genre, synonyms, "other")
        assert val == "hashiyah"
        assert fallback is True

    def test_unknown_value_uses_default(self) -> None:
        """Completely unknown value falls back to default."""
        val, fallback = validate_enum_value("unknown_xyz", Genre, {}, "other")
        assert val == "other"
        assert fallback is True

    def test_synonym_to_invalid_target_falls_back_to_default(self) -> None:
        """Synonym that maps to an invalid enum value falls back to default."""
        synonyms = {"مجهول": "not_a_valid_genre"}
        val, fallback = validate_enum_value("مجهول", Genre, synonyms, "other")
        assert val == "other"
        assert fallback is True

    def test_structural_format_commentary_valid(self) -> None:
        """commentary is a valid StructuralFormat."""
        val, fallback = validate_enum_value("commentary", StructuralFormat, {}, "mixed")
        assert val == "commentary"
        assert fallback is False

    def test_structural_format_unknown_uses_mixed(self) -> None:
        """Unknown structural_format falls back to mixed."""
        val, fallback = validate_enum_value("novel_format", StructuralFormat, {}, "mixed")
        assert val == "mixed"
        assert fallback is True

    def test_work_level_advanced_valid(self) -> None:
        """advanced is a valid WorkLevel."""
        val, fallback = validate_enum_value("advanced", WorkLevel, {}, None)
        assert val == "advanced"
        assert fallback is False

    def test_work_level_none_default_for_optional(self) -> None:
        """When default is None and value is unknown, returns (None, True)."""
        val, fallback = validate_enum_value("inapplicable", WorkLevel, {}, None)
        assert val is None
        assert fallback is True

    def test_authority_level_primary_valid(self) -> None:
        """primary is a valid AuthorityLevel."""
        val, fallback = validate_enum_value(
            "primary", AuthorityLevel, {}, "modern_compilation"
        )
        assert val == "primary"
        assert fallback is False

    def test_all_genre_synonyms_from_config_are_valid(self) -> None:
        """Every synonym in genre_synonyms.json must map to a valid Genre value."""
        import json
        from pathlib import Path

        synonyms_path = Path("library/config/genre_synonyms.json")
        if not synonyms_path.exists():
            pytest.skip("genre_synonyms.json not found")
        synonyms: dict[str, str] = json.loads(
            synonyms_path.read_text(encoding="utf-8")
        )
        for arabic_key, canonical_value in synonyms.items():
            val, fallback = validate_enum_value(
                arabic_key, Genre, synonyms, "other"
            )
            # Should not fall through to "other" — every synonym should hit its canonical
            assert val == canonical_value, (
                f"Synonym '{arabic_key}' → '{canonical_value}' is not a valid Genre value"
            )
            assert fallback is True  # synonym was used

    def test_valid_genre_rihlah_passes_direct(self) -> None:
        """rihlah is a valid Genre enum value (Fix 1 — post-evaluation)."""
        val, fallback = validate_enum_value("rihlah", Genre, {}, "other")
        assert val == "rihlah"
        assert fallback is False

    def test_valid_genre_usul_al_fiqh_passes_direct(self) -> None:
        """usul_al_fiqh is a valid Genre enum value (Fix 1 — post-evaluation)."""
        val, fallback = validate_enum_value("usul_al_fiqh", Genre, {}, "other")
        assert val == "usul_al_fiqh"
        assert fallback is False

    def test_arabic_synonym_رحلة_maps_to_rihlah(self) -> None:
        """Arabic synonym رحلة → rihlah."""
        synonyms = {"رحلة": "rihlah"}
        val, fallback = validate_enum_value("رحلة", Genre, synonyms, "other")
        assert val == "rihlah"
        assert fallback is True

    def test_arabic_synonym_أصول_الفقه_maps_to_usul_al_fiqh(self) -> None:
        """Arabic synonym أصول الفقه → usul_al_fiqh."""
        synonyms = {"أصول الفقه": "usul_al_fiqh"}
        val, fallback = validate_enum_value("أصول الفقه", Genre, synonyms, "other")
        assert val == "usul_al_fiqh"
        assert fallback is True


# ──────────────────────────────────────────────────────────────────
# TestApplyConfidenceCaps
# ──────────────────────────────────────────────────────────────────


class TestApplyConfidenceCaps:
    """Tests for apply_confidence_caps() — SPEC §6 confidence caps."""

    def test_biographical_cap_clamps_high_confidence(self) -> None:
        """Confidence 0.95 → capped at 0.85 for any LLM biographical inference."""
        output = _make_output(confidence=0.95, attribution="definitive")
        scores = apply_confidence_caps(output, "definitive")
        assert scores["author"] == pytest.approx(0.85)

    def test_biographical_cap_does_not_raise_low_confidence(self) -> None:
        """Confidence 0.60 remains 0.60 — cap only clamps from above."""
        output = _make_output(confidence=0.60, attribution="definitive")
        scores = apply_confidence_caps(output, "definitive")
        assert scores["author"] == pytest.approx(0.60)

    def test_disputed_attribution_cap_at_070(self) -> None:
        """Disputed attribution: confidence capped at 0.70 (below 0.85 cap)."""
        output = _make_output(confidence=0.95, attribution="disputed")
        scores = apply_confidence_caps(output, "disputed")
        assert scores["author"] <= 0.70

    def test_disputed_cap_applies_even_below_085(self) -> None:
        """Disputed: confidence 0.75 → capped to 0.70."""
        output = _make_output(confidence=0.75, attribution="disputed")
        scores = apply_confidence_caps(output, "disputed")
        assert scores["author"] == pytest.approx(0.70)

    def test_unknown_attribution_sets_zero(self) -> None:
        """Unknown attribution: author confidence forced to 0.0."""
        output = _make_output(confidence=0.95, attribution="unknown")
        scores = apply_confidence_caps(output, "unknown")
        assert scores["author"] == 0.0

    def test_genre_confidence_not_capped(self) -> None:
        """Genre confidence is returned at face value, regardless of attribution."""
        output = _make_output(confidence=0.95, attribution="definitive")
        scores = apply_confidence_caps(output, "definitive")
        assert scores["genre"] == pytest.approx(0.90)

    def test_all_expected_keys_present(self) -> None:
        """Result dict contains all expected field keys."""
        output = _make_output()
        scores = apply_confidence_caps(output, "traditional")
        expected_keys = {
            "genre", "science_scope", "level", "structural_format",
            "authority_level", "multi_layer", "genre_chain", "author",
        }
        assert set(scores.keys()) == expected_keys

    def test_traditional_attribution_uses_085_cap_only(self) -> None:
        """Traditional attribution: only the 0.85 biographical cap applies."""
        output = _make_output(confidence=0.90, attribution="traditional")
        scores = apply_confidence_caps(output, "traditional")
        assert scores["author"] == pytest.approx(0.85)


# ──────────────────────────────────────────────────────────────────
# TestSetTextFidelity
# ──────────────────────────────────────────────────────────────────


class TestSetTextFidelity:
    """Tests for set_text_fidelity() — SPEC §4.A.4 deterministic fidelity."""

    def test_shamela_html_returns_high(self) -> None:
        """Shamela HTML → high fidelity (structured digital text)."""
        assert set_text_fidelity(SourceFormat.SHAMELA_HTML) == "high"

    def test_plain_text_returns_medium(self) -> None:
        """Plain text → medium fidelity."""
        assert set_text_fidelity(SourceFormat.PLAIN_TEXT) == "medium"

    def test_pdf_text_returns_medium(self) -> None:
        """PDF text-embedded → medium fidelity (not shamela)."""
        assert set_text_fidelity(SourceFormat.PDF_TEXT) == "medium"

    def test_owner_authored_returns_medium(self) -> None:
        """Owner-authored content → medium fidelity."""
        assert set_text_fidelity(SourceFormat.OWNER_AUTHORED) == "medium"


# ──────────────────────────────────────────────────────────────────
# TestBuildNeedsReview
# ──────────────────────────────────────────────────────────────────


class TestBuildNeedsReview:
    """Tests for build_needs_review()."""

    def test_low_confidence_field_included(self) -> None:
        """Field with confidence < 0.70 is included in needs_review."""
        scores = {"genre": 0.90, "author": 0.50, "level": 0.65}
        review = build_needs_review(scores, {"author_name_raw": "النووي"})
        assert "author" in review
        assert "level" in review

    def test_high_confidence_field_excluded(self) -> None:
        """Field with confidence >= 0.70 is excluded from needs_review."""
        scores = {"genre": 0.90, "author": 0.80}
        review = build_needs_review(scores, {"author_name_raw": "النووي"})
        assert "genre" not in review
        assert "author" not in review

    def test_no_author_raw_adds_author(self) -> None:
        """When no author_name_raw is extracted, 'author' is always added."""
        scores = {"genre": 0.90}
        review = build_needs_review(scores, {})
        assert "author" in review

    def test_empty_author_name_raw_adds_author(self) -> None:
        """Empty string author_name_raw counts as absent."""
        scores = {"genre": 0.90}
        review = build_needs_review(scores, {"author_name_raw": ""})
        assert "author" in review

    def test_author_raw_present_high_conf_no_review(self) -> None:
        """Author in extracted + high confidence → not in needs_review."""
        scores = {"genre": 0.90, "author": 0.80}
        review = build_needs_review(scores, {"author_name_raw": "النووي"})
        assert "author" not in review

    def test_none_confidence_skipped(self) -> None:
        """Fields with None confidence (e.g. level=None) are not added."""
        scores = {"genre": 0.90, "level": None}
        review = build_needs_review(scores, {"author_name_raw": "ابن مالك"})
        assert "level" not in review

    def test_result_is_sorted(self) -> None:
        """Returned list is sorted alphabetically."""
        scores = {"science_scope": 0.60, "author": 0.55, "genre": 0.65}
        review = build_needs_review(scores, {})
        assert review == sorted(review)

    def test_exact_threshold_boundary_excluded(self) -> None:
        """Confidence exactly at threshold (0.70) is NOT included (< not <=)."""
        scores = {"genre": 0.70}
        review = build_needs_review(scores, {"author_name_raw": "الشافعي"})
        assert "genre" not in review

    def test_author_not_duplicated_when_already_low_conf(self) -> None:
        """When author is in needs_review from low confidence, it is not added twice."""
        scores = {"author": 0.50}
        review = build_needs_review(scores, {})  # No author_name_raw
        assert review.count("author") == 1


# ──────────────────────────────────────────────────────────────────
# TestInferMetadata — integration with mocked consensus
# ──────────────────────────────────────────────────────────────────


class TestInferMetadata:
    """Integration tests for infer_metadata() with mocked consensus.

    All tests patch `engines.source.src.metadata_inference.evaluate`.
    No real API calls are made.
    """

    @pytest.mark.asyncio
    async def test_basic_agreed_inference_shamela(self) -> None:
        """Happy path: both models agree on شرح النووي على صحيح مسلم."""
        output = _make_output()
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "شرح النووي على صحيح مسلم",
                    "author_name_raw": "النووي",
                    "text_sample": "بسم الله الرحمن الرحيم، هذا شرح صحيح الإمام مسلم",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.consensus_agreed is True
        assert result.genre == "sharh"
        assert result.text_fidelity == "high"
        assert result.canonical_output is not None
        assert result.is_multi_layer is True

    @pytest.mark.asyncio
    async def test_plain_text_source_fidelity_medium(self) -> None:
        """Plain text source → text_fidelity is 'medium'."""
        output = _make_output()
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "title_arabic": "ألفية ابن مالك",
                    "author_name_raw": "ابن مالك",
                    "text_sample": "قال محمد هو ابن مالك أحمد اللهَ خيرَ ما يُحمد",
                },
                source_format=SourceFormat.PLAIN_TEXT,
            )

        assert result.text_fidelity == "medium"

    @pytest.mark.asyncio
    async def test_no_author_raw_adds_author_to_review(self) -> None:
        """No author_name_raw → 'author' appears in needs_review_fields."""
        output = _make_output()
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "كتاب مجهول المؤلف",
                    "text_sample": "بسم الله الرحمن الرحيم",
                },
                source_format=SourceFormat.PLAIN_TEXT,
            )

        assert "author" in result.needs_review_fields

    @pytest.mark.asyncio
    async def test_disputed_attribution_caps_author_confidence(self) -> None:
        """Disputed attribution → author confidence <= 0.70 in confidence_scores."""
        # Model A says disputed, model B says traditional → compare_attribution_status
        # returns ("disputed", needs_gate=True)
        output_a = _make_output(attribution="disputed", confidence=0.95)
        output_b = _make_output(attribution="traditional", confidence=0.90)
        cr = _make_consensus_result(output_a, output_b, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "كتاب في مسألة خلافية",
                    "author_name_raw": "مجهول",
                    "text_sample": "بسم الله",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.confidence_scores is not None
        assert result.confidence_scores["author"] <= 0.70

    @pytest.mark.asyncio
    async def test_unknown_attribution_sets_author_confidence_zero(self) -> None:
        """Both models say unknown attribution → author confidence == 0.0."""
        output = _make_output(attribution="unknown", confidence=0.90)
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "نص مجهول المؤلف",
                    "text_sample": "بسم الله",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.confidence_scores is not None
        assert result.confidence_scores["author"] == 0.0

    @pytest.mark.asyncio
    async def test_both_models_fail_returns_early_with_gate(self) -> None:
        """Both models fail → needs_human_gate=True, no canonical_output."""
        cr = ConsensusResult(
            agreed=False,
            canonical_result=None,
            model_responses=[
                ModelResponse(
                    "openrouter/cohere/command-a",
                    "openrouter",
                    None,
                    {},
                    False,
                    error="timeout",
                ),
                ModelResponse(
                    "anthropic/claude-opus-4-6",
                    "anthropic",
                    None,
                    {},
                    False,
                    error="timeout",
                ),
            ],
            agreement_detail="Both models failed",
            needs_human_gate=True,
            human_gate_trigger="consensus_disagreement",
        )

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "كتاب",
                    "text_sample": "بسم الله",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.needs_human_gate is True
        assert result.canonical_output is None
        assert "consensus_disagreement" in result.human_gate_triggers

    @pytest.mark.asyncio
    async def test_enum_synonym_منظومة_maps_to_nazm(self) -> None:
        """LLM returns Arabic genre 'منظومة' → maps to 'nazm' via synonyms."""
        # ألفية ابن مالك is a well-known Arabic grammar poem (nazm)
        output = _make_output(genre="منظومة")
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            # Temporarily inject the Arabic synonym into the module-level dict
            import engines.source.src.metadata_inference as mi

            old_synonyms = mi._GENRE_SYNONYMS
            mi._GENRE_SYNONYMS = {"منظومة": "nazm"}
            try:
                mock_eval.return_value = cr
                result = await infer_metadata(
                    extracted={
                        "display_title": "ألفية ابن مالك",
                        "author_name_raw": "ابن مالك",
                        "text_sample": "قال محمد هو ابن مالك أحمد اللهَ خيرَ ما يُحمد",
                    },
                    source_format=SourceFormat.SHAMELA_HTML,
                )
            finally:
                mi._GENRE_SYNONYMS = old_synonyms

        assert result.genre == "nazm"
        # Genre fallback flag means it's in needs_review_fields (synonym used)
        assert "genre" in result.needs_review_fields

    @pytest.mark.asyncio
    async def test_layers_mapped_correctly(self) -> None:
        """Multi-layer sharh with two layers → text_layers populated."""
        # شرح ابن عقيل on ألفية ابن مالك — a classical multi-layer text
        layers = [
            LayerOutput(layer_type="matn", author_name="ابن مالك"),
            LayerOutput(layer_type="sharh", author_name="ابن عقيل"),
        ]
        output = _make_output(is_multi_layer=True, layers=layers)
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "شرح ابن عقيل على ألفية ابن مالك",
                    "author_name_raw": "ابن عقيل",
                    "text_sample": "بسم الله الرحمن الرحيم",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.is_multi_layer is True
        assert len(result.text_layers) == 2
        assert result.text_layers[0]["layer_type"] == "matn"
        assert result.text_layers[0]["author_name"] == "ابن مالك"
        assert result.text_layers[1]["layer_type"] == "sharh"
        assert result.text_layers[1]["author_name"] == "ابن عقيل"

    @pytest.mark.asyncio
    async def test_author_reference_populated(self) -> None:
        """Author reference dict is populated from canonical output."""
        output = _make_output(
            author_name="جلال الدين السيوطي",
            death_date=911,
        )
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "همع الهوامع",
                    "author_name_raw": "السيوطي",
                    "text_sample": "بسم الله",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.author_reference is not None
        assert result.author_reference["name_arabic"] == "جلال الدين السيوطي"
        assert result.author_reference["death_date_hijri"] == 911
        assert result.author_reference["source_of_identification"] == "consensus"

    @pytest.mark.asyncio
    async def test_single_model_fallback_source_of_identification_inferred(
        self,
    ) -> None:
        """When only one model succeeds, source_of_identification is 'inferred'."""
        output = _make_output()
        # One failed model
        cr = ConsensusResult(
            agreed=False,
            canonical_result=output,
            model_responses=[
                ModelResponse(
                    "openrouter/cohere/command-a",
                    "openrouter",
                    output,
                    output.model_dump(),
                    True,
                    latency=1.0,
                ),
                ModelResponse(
                    "anthropic/claude-opus-4-6",
                    "anthropic",
                    None,
                    {},
                    False,
                    error="timeout",
                ),
            ],
            agreement_detail="Model B failed",
            needs_human_gate=True,
            human_gate_trigger="consensus_disagreement",
        )

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "شرح المنهاج",
                    "author_name_raw": "النووي",
                    "text_sample": "الحمد لله رب العالمين",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.author_reference is not None
        assert result.author_reference["source_of_identification"] == "inferred"

    @pytest.mark.asyncio
    async def test_work_match_disagreement_triggers_gate(self) -> None:
        """Models disagree on genre_chain (work matching) → gate triggered."""
        chain_a = GenreChainOutput(
            relation_type="sharh_of",
            base_work_title="جمع الجوامع",
            base_work_author="ابن السبكي",
        )
        chain_b = GenreChainOutput(
            relation_type="hashiyah_on",
            base_work_title="المنهاج",
            base_work_author="النووي",
        )
        output_a = _make_output(genre="sharh", genre_chain=chain_a)
        output_b = _make_output(genre="hashiyah", genre_chain=chain_b)
        # consensus agreed=True to bypass top-level gate; work disagreement comes from local compare
        cr = _make_consensus_result(output_a, output_b, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "نص غامض",
                    "author_name_raw": "مؤلف",
                    "text_sample": "بسم الله",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.work_agreed is False
        assert result.work_human_gate_trigger == "work_match_uncertain"
        assert "work_match_uncertain" in result.human_gate_triggers

    @pytest.mark.asyncio
    async def test_science_scope_mapped(self) -> None:
        """science_scope from canonical output is passed through."""
        output = _make_output(science_scope=["fiqh", "usul_al_fiqh"])
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "الموافقات في أصول الشريعة",
                    "author_name_raw": "إبراهيم بن موسى الشاطبي",
                    "text_sample": "الحمد لله على نعمه الظاهرة والباطنة",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.science_scope == ["fiqh", "usul_al_fiqh"]

    @pytest.mark.asyncio
    async def test_raw_model_responses_stored(self) -> None:
        """raw_model_responses contains diagnostic info for both models."""
        output = _make_output()
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "صحيح مسلم",
                    "author_name_raw": "مسلم بن الحجاج",
                    "text_sample": "بسم الله الرحمن الرحيم",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert len(result.raw_model_responses) == 2
        for resp in result.raw_model_responses:
            assert "model_id" in resp
            assert "parse_success" in resp
            assert "error" in resp

    @pytest.mark.asyncio
    async def test_level_none_for_non_pedagogical_work(self) -> None:
        """Works with level=None (e.g. memoirs) preserve None for result.level."""
        output = _make_output(level=None)
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "مذكرات العفن — مالك بن نبي",
                    "author_name_raw": "مالك بن نبي",
                    "text_sample": "في سنة ألف وتسعمائة واثنين وثلاثين",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.level is None

    @pytest.mark.asyncio
    async def test_consensus_disagreement_human_gate_propagated(self) -> None:
        """When consensus sets needs_human_gate, it propagates to result."""
        cr = _make_consensus_result(
            agreed=False,
            needs_human_gate=True,
            human_gate_trigger="consensus_disagreement",
        )
        # canonical_result is None when disagreed
        cr.canonical_result = _make_output()  # inject so processing continues

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "كتاب خلافي",
                    "author_name_raw": "مؤلف مختلف عليه",
                    "text_sample": "بسم الله",
                },
                source_format=SourceFormat.SHAMELA_HTML,
            )

        assert result.needs_human_gate is True
        assert "consensus_disagreement" in result.human_gate_triggers

    @pytest.mark.asyncio
    async def test_unknown_genre_defaults_to_other(self) -> None:
        """LLM returns unknown genre string → defaults to 'other', in needs_review."""
        output = _make_output(genre="completely_unknown_genre_xyz")
        cr = _make_consensus_result(output, output, agreed=True)

        with patch(
            "engines.source.src.metadata_inference.evaluate",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = cr
            result = await infer_metadata(
                extracted={
                    "display_title": "نص غير مصنف",
                    "author_name_raw": "مؤلف",
                    "text_sample": "بسم الله",
                },
                source_format=SourceFormat.PLAIN_TEXT,
            )

        assert result.genre == "other"
        assert "genre" in result.needs_review_fields


# ── Death date source determination (BUG-04) ──


class TestDeathDateSource:
    """Tests for _determine_death_date_source provenance logic."""

    def test_absent_when_no_date(self) -> None:
        """No death date → 'absent'."""
        from engines.source.src.metadata_inference import _determine_death_date_source

        result = _determine_death_date_source(None, {"author_name_raw": "السيوطي"})
        assert result == "absent"

    def test_author_raw_text(self) -> None:
        """Death date visible in author_name_raw → 'author_raw_text'."""
        from engines.source.src.metadata_inference import _determine_death_date_source

        result = _determine_death_date_source(
            911, {"author_name_raw": "جلال الدين السيوطي (ت 911هـ)"}
        )
        assert result == "author_raw_text"

    def test_extraction_from_edition(self) -> None:
        """Death date in edition_raw but not author_raw → 'extraction'."""
        from engines.source.src.metadata_inference import _determine_death_date_source

        result = _determine_death_date_source(
            911,
            {
                "author_name_raw": "جلال الدين السيوطي",
                "edition_raw": "طبعة 911هـ",
            },
        )
        assert result == "extraction"

    def test_inference_when_not_in_fields(self) -> None:
        """Death date not in any extraction field → 'inference'."""
        from engines.source.src.metadata_inference import _determine_death_date_source

        result = _determine_death_date_source(
            911,
            {
                "author_name_raw": "جلال الدين السيوطي",
                "edition_raw": "الطبعة الأولى",
                "publisher_raw": "دار الكتب العلمية",
            },
        )
        assert result == "inference"

    def test_none_field_values_handled(self) -> None:
        """Fields with None values don't cause errors."""
        from engines.source.src.metadata_inference import _determine_death_date_source

        result = _determine_death_date_source(
            911,
            {
                "author_name_raw": None,
                "author_name": None,
                "edition_raw": None,
                "publisher_raw": None,
            },
        )
        assert result == "inference"
