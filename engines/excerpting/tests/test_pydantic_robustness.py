"""Pydantic parsing robustness tests — simulates Instructor's model_validate behavior.

Tests how response models handle LLM-produced JSON that deviates from the schema:
extra fields, wrong types, missing defaults, invalid enums, and Literal constraints.
These are the failure modes that occur when real LLM output hits Pydantic validation.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engines.excerpting.contracts import (
    ClassificationResult,
    ClassifiedSegment,
    EnrichmentResult,
    ExtractionResult,
    ResolvedScholar,
    UnitEnrichment,
    VerificationResult,
)


class TestClassificationResultExtras:
    """LLM may return fields not in our schema."""

    def test_extra_fields_accepted(self) -> None:
        """ClassificationResult with unknown extra fields → accepted."""
        data = {
            "segments": [
                {
                    "segment_index": 0,
                    "start_word": 0,
                    "end_word": 5,
                    "text_snippet": "بسم الله الرحمن",
                    "scholarly_function": "definition",
                    "confidence": 0.9,
                }
            ],
            "total_segments": 1,
            "extra_field": "should be ignored",
            "another_unknown": 42,
        }
        result = ClassificationResult.model_validate(data)
        assert len(result.segments) == 1
        assert result.total_segments == 1


class TestClassifiedSegmentEnumValidation:
    """scholarly_function must be a valid ScholarlyFunction."""

    def test_invalid_enum_raises(self) -> None:
        """ClassifiedSegment with scholarly_function='unknown_type' → raises."""
        data = {
            "segment_index": 0,
            "start_word": 0,
            "end_word": 5,
            "text_snippet": "بسم الله الرحمن",
            "scholarly_function": "unknown_type",
            "confidence": 0.9,
        }
        with pytest.raises(ValidationError, match="scholarly_function"):
            ClassifiedSegment.model_validate(data)


class TestUnitEnrichmentCoercion:
    """Pydantic coercion of string→float, absent→default, etc."""

    def test_string_school_confidence_coerced(self) -> None:
        """UnitEnrichment with school_confidence as string '0.8' → float 0.8."""
        data = {
            "unit_index": 0,
            "excerpt_topic": ["فقه"],
            "school": "حنبلي",
            "school_confidence": "0.8",
            "resolved_scholars": [],
            "takhrij_data": [],
            "terminology_variants": [],
            "cross_references": [],
            "context_hint": None,
        }
        result = UnitEnrichment.model_validate(data)
        assert result.school_confidence == 0.8
        assert isinstance(result.school_confidence, float)

    def test_absent_takhrij_data_defaults_to_empty_list(self) -> None:
        """UnitEnrichment with takhrij_data key absent → defaults to []."""
        data = {
            "unit_index": 0,
            "excerpt_topic": ["توحيد"],
            "school": None,
            "school_confidence": None,
            "resolved_scholars": [],
            "terminology_variants": [],
            "cross_references": [],
            "context_hint": None,
            # takhrij_data intentionally absent
        }
        result = UnitEnrichment.model_validate(data)
        assert result.takhrij_data == []

    def test_empty_excerpt_topic_accepted(self) -> None:
        """UnitEnrichment with excerpt_topic as empty list → accepted (V-P3-4 flags later)."""
        data = {
            "unit_index": 0,
            "excerpt_topic": [],
            "school": None,
            "school_confidence": None,
            "resolved_scholars": [],
            "takhrij_data": [],
            "terminology_variants": [],
            "cross_references": [],
            "context_hint": None,
        }
        result = UnitEnrichment.model_validate(data)
        assert result.excerpt_topic == []


class TestResolvedScholarLiteralValidation:
    """FIX-6: role is Literal, not free-form str."""

    def test_invalid_role_raises(self) -> None:
        """ResolvedScholar with role='narrator' → raises ValidationError."""
        data = {
            "mention_text": "ابن حجر",
            "resolved_name": "ابن حجر العسقلاني",
            "role": "narrator",
            "confidence": 0.9,
        }
        with pytest.raises(ValidationError, match="role"):
            ResolvedScholar.model_validate(data)

    def test_valid_roles_accepted(self) -> None:
        """All three valid role values are accepted."""
        for role in ("quoted_opinion", "classification_frame", "refuted_position"):
            result = ResolvedScholar.model_validate({
                "mention_text": "ابن تيمية",
                "role": role,
                "confidence": 0.85,
            })
            assert result.role == role

    def test_confidence_out_of_range_raises(self) -> None:
        """ResolvedScholar with confidence=1.5 → raises (ge=0.0, le=1.0)."""
        data = {
            "mention_text": "النووي",
            "role": "quoted_opinion",
            "confidence": 1.5,
        }
        with pytest.raises(ValidationError, match="confidence"):
            ResolvedScholar.model_validate(data)


class TestVerificationResultValidator:
    """Model validator checks for duplicate item_index."""

    def test_duplicate_item_index_raises(self) -> None:
        """VerificationResult with duplicate item_index values → raises."""
        data = {
            "items": [
                {
                    "item_index": 0,
                    "agrees": True,
                    "confidence": 0.9,
                    "reasoning": "Correct",
                },
                {
                    "item_index": 0,
                    "agrees": False,
                    "alternative": "شافعي",
                    "confidence": 0.8,
                    "reasoning": "Different school",
                },
            ]
        }
        with pytest.raises(ValidationError, match="Duplicate item_index"):
            VerificationResult.model_validate(data)

    def test_unique_item_indices_accepted(self) -> None:
        """VerificationResult with unique item_index values → accepted."""
        data = {
            "items": [
                {
                    "item_index": 0,
                    "agrees": True,
                    "confidence": 0.9,
                    "reasoning": "Correct",
                },
                {
                    "item_index": 1,
                    "agrees": True,
                    "confidence": 0.85,
                    "reasoning": "Also correct",
                },
            ]
        }
        result = VerificationResult.model_validate(data)
        assert len(result.items) == 2


class TestEnrichmentResultMismatch:
    """Document behavior when enrichment count doesn't match total_units."""

    def test_mismatched_count_accepted(self) -> None:
        """EnrichmentResult with len(enrichments) != total_units → accepted.

        No model_validator checks this. The mismatch is caught by
        apply_enrichment's per-unit matching (logs warning for missing units).
        """
        data = {
            "enrichments": [
                {
                    "unit_index": 0,
                    "excerpt_topic": ["فقه"],
                    "school": None,
                    "school_confidence": None,
                    "resolved_scholars": [],
                    "takhrij_data": [],
                    "terminology_variants": [],
                    "cross_references": [],
                    "context_hint": None,
                },
            ],
            "total_units": 5,  # Claims 5 but only 1 enrichment
        }
        result = EnrichmentResult.model_validate(data)
        assert len(result.enrichments) == 1
        assert result.total_units == 5


class TestExtractionResultNotes:
    """notes field can be None or absent — both valid."""

    def test_notes_none_accepted(self) -> None:
        """ExtractionResult with notes=None → accepted."""
        data = {
            "teaching_units": [],
            "total_units": 0,
            "notes": None,
        }
        result = ExtractionResult.model_validate(data)
        assert result.notes is None

    def test_notes_absent_accepted(self) -> None:
        """ExtractionResult with notes key absent → accepted (defaults to None)."""
        data = {
            "teaching_units": [],
            "total_units": 0,
        }
        result = ExtractionResult.model_validate(data)
        assert result.notes is None


def _make_unit_enrichment(unit_index: int) -> dict:
    """Minimal valid UnitEnrichment data."""
    return {
        "unit_index": unit_index,
        "excerpt_topic": ["فقه"],
        "school": None,
        "school_confidence": None,
        "resolved_scholars": [],
        "takhrij_data": [],
        "terminology_variants": [],
        "cross_references": [],
        "context_hint": None,
    }


def _make_teaching_unit(unit_index: int) -> dict:
    """Minimal valid TeachingUnit data."""
    return {
        "unit_index": unit_index,
        "segment_indices": [unit_index],
        "start_word": unit_index * 10,
        "end_word": unit_index * 10 + 9,
        "text_snippet": "بسم الله الرحمن الرحيم",
        "primary_function": "definition",
        "self_containment": "FULL",
        "description_arabic": "تعريف المسألة",
    }


class TestEnrichmentResultUnitIndexUniqueness:
    """Model validator checks for duplicate unit_index in enrichments."""

    def test_unique_unit_indices_accepted(self) -> None:
        """EnrichmentResult with unique unit_index values → accepted."""
        data = {
            "enrichments": [_make_unit_enrichment(0), _make_unit_enrichment(1)],
            "total_units": 2,
        }
        result = EnrichmentResult.model_validate(data)
        assert len(result.enrichments) == 2

    def test_duplicate_unit_index_raises(self) -> None:
        """EnrichmentResult with duplicate unit_index → raises ValidationError."""
        data = {
            "enrichments": [_make_unit_enrichment(0), _make_unit_enrichment(0)],
            "total_units": 2,
        }
        with pytest.raises(ValidationError, match="Duplicate unit_index"):
            EnrichmentResult.model_validate(data)

    def test_error_message_includes_duplicate_value(self) -> None:
        """Error message includes the specific duplicate index value."""
        data = {
            "enrichments": [
                _make_unit_enrichment(3),
                _make_unit_enrichment(3),
                _make_unit_enrichment(5),
            ],
            "total_units": 3,
        }
        with pytest.raises(ValidationError, match=r"\{3\}"):
            EnrichmentResult.model_validate(data)

    def test_single_enrichment_accepted(self) -> None:
        """EnrichmentResult with one enrichment → accepted (no duplicates possible)."""
        data = {
            "enrichments": [_make_unit_enrichment(0)],
            "total_units": 1,
        }
        result = EnrichmentResult.model_validate(data)
        assert len(result.enrichments) == 1


class TestExtractionResultUnitIndexUniqueness:
    """Model validator checks for duplicate unit_index in teaching_units."""

    def test_unique_unit_indices_accepted(self) -> None:
        """ExtractionResult with unique unit_index values → accepted."""
        data = {
            "teaching_units": [_make_teaching_unit(0), _make_teaching_unit(1)],
            "total_units": 2,
        }
        result = ExtractionResult.model_validate(data)
        assert len(result.teaching_units) == 2

    def test_duplicate_unit_index_raises(self) -> None:
        """ExtractionResult with duplicate unit_index → raises ValidationError."""
        data = {
            "teaching_units": [_make_teaching_unit(0), _make_teaching_unit(0)],
            "total_units": 2,
        }
        with pytest.raises(ValidationError, match="Duplicate unit_index"):
            ExtractionResult.model_validate(data)

    def test_error_message_includes_duplicate_value(self) -> None:
        """Error message includes the specific duplicate index value."""
        data = {
            "teaching_units": [
                _make_teaching_unit(2),
                _make_teaching_unit(2),
                _make_teaching_unit(4),
            ],
            "total_units": 3,
        }
        with pytest.raises(ValidationError, match=r"\{2\}"):
            ExtractionResult.model_validate(data)

    def test_single_teaching_unit_accepted(self) -> None:
        """ExtractionResult with one teaching_unit → accepted."""
        data = {
            "teaching_units": [_make_teaching_unit(0)],
            "total_units": 1,
        }
        result = ExtractionResult.model_validate(data)
        assert len(result.teaching_units) == 1
