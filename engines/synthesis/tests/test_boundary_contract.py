"""Synthesis input boundary contract tests.

Validates TaxonomyPlacedExcerpt against the taxonomy runtime output shape
(PlacementAdditions merged onto upstream excerpt). Documents the A1 partial
boundary gap: the tracer still emits legacy shapes that do not match.

These are deterministic contract tests — no LLM, no synthesis logic.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engines.synthesis.contracts import TaxonomyPlacedExcerpt
from engines.taxonomy.contracts_core import PlacementAdditions


# ── Fixtures ─────────────────────────────────────────────────────


def _upstream_excerpt() -> dict:
    """Minimal upstream excerpt fields (from excerpting engine)."""
    return {
        "excerpt_id": "exc_test_001",
        "source_id": "src_ibn_aqil_v3",
        "primary_text": "باب الكلام وما يتألف منه",
    }


def _placement_additions() -> dict:
    """Minimal PlacementAdditions fields (runtime shape)."""
    return {
        "lifecycle_stage": "placed",
        "placement_route": "live",
        "confirmed_leaf": "nahw/kalaam/definition",
        "placement_confidence": 0.85,
        "placed_utc": "2026-04-01T12:00:00Z",
        "taxonomy_version_at_placement": "nahw_v1.0",
        "tie_detected": False,
    }


def _runtime_placed_excerpt() -> dict:
    """A placed excerpt as the taxonomy runtime actually produces it.

    Shape: {**original_excerpt, **PlacementAdditions.model_dump()}.
    This is the D-023 merge the writer performs.
    """
    return {**_upstream_excerpt(), **_placement_additions()}


# ── Runtime shape validates ──────────────────────────────────────


class TestRuntimeShapeAccepted:
    """The runtime-shaped placed excerpt must validate against both contracts."""

    def test_placement_additions_valid(self) -> None:
        PlacementAdditions.model_validate(_placement_additions())

    def test_taxonomy_placed_excerpt_valid(self) -> None:
        TaxonomyPlacedExcerpt.model_validate(_runtime_placed_excerpt())

    def test_verified_flagged_status_defaults_to_verified(self) -> None:
        """Pre-human-gate default: absent field → 'verified'."""
        data = _runtime_placed_excerpt()
        assert "verified_flagged_status" not in data
        exc = TaxonomyPlacedExcerpt.model_validate(data)
        assert exc.verified_flagged_status == "verified"

    def test_optional_upstream_fields_degrade_gracefully(self) -> None:
        """Synthesis runs degraded when optional upstream fields are absent."""
        data = _runtime_placed_excerpt()
        exc = TaxonomyPlacedExcerpt.model_validate(data)
        assert exc.primary_function is None
        assert exc.school is None
        assert exc.excerpt_topic == []

    def test_full_upstream_fields_accepted(self) -> None:
        """Runtime excerpt with all optional upstream fields."""
        data = _runtime_placed_excerpt()
        data.update({
            "primary_function": "rule_statement",
            "school": "hanafi",
            "school_confidence": 0.9,
            "content_types": ["definition", "evidence_quran"],
            "excerpt_topic": ["تعريف الكلام"],
            "description_arabic": "تعريف الكلام عند النحاة",
        })
        exc = TaxonomyPlacedExcerpt.model_validate(data)
        assert exc.primary_function == "rule_statement"
        assert exc.excerpt_topic == ["تعريف الكلام"]


# ── Required fields enforced ─────────────────────────────────────


class TestRequiredFieldsEnforced:
    """TaxonomyPlacedExcerpt must reject inputs missing required fields."""

    @pytest.mark.parametrize("missing_field", [
        "excerpt_id",
        "source_id",
        "primary_text",
        "lifecycle_stage",
        "confirmed_leaf",
        "placement_route",
    ])
    def test_missing_required_field_rejected(self, missing_field: str) -> None:
        data = _runtime_placed_excerpt()
        del data[missing_field]
        with pytest.raises(ValidationError):
            TaxonomyPlacedExcerpt.model_validate(data)

    def test_empty_primary_text_accepted(self) -> None:
        """Contract does not enforce non-empty at the Pydantic level.

        Non-emptiness is a SPEC rule (F-DET-2), enforced upstream by
        the excerpting engine, not by the synthesis input model.
        """
        data = _runtime_placed_excerpt()
        data["primary_text"] = ""
        TaxonomyPlacedExcerpt.model_validate(data)


# ── Constraint validation ────────────────────────────────────────


class TestConstraintValidation:
    """Field constraints must match across the boundary."""

    def test_placement_confidence_range(self) -> None:
        data = _runtime_placed_excerpt()
        data["placement_confidence"] = 1.5
        with pytest.raises(ValidationError):
            TaxonomyPlacedExcerpt.model_validate(data)

    def test_placement_confidence_negative_rejected(self) -> None:
        data = _runtime_placed_excerpt()
        data["placement_confidence"] = -0.1
        with pytest.raises(ValidationError):
            TaxonomyPlacedExcerpt.model_validate(data)

    def test_placement_confidence_null_accepted(self) -> None:
        data = _runtime_placed_excerpt()
        data["placement_confidence"] = None
        exc = TaxonomyPlacedExcerpt.model_validate(data)
        assert exc.placement_confidence is None


# ── Field alignment between contracts ────────────────────────────


class TestFieldAlignment:
    """PlacementAdditions fields must be a subset of TaxonomyPlacedExcerpt."""

    def test_all_placement_additions_fields_present(self) -> None:
        """Every field in PlacementAdditions must exist in TaxonomyPlacedExcerpt.

        Fields only in PlacementAdditions (unplaced/pending routing) are
        excluded — synthesis only receives placed excerpts.
        """
        # Fields that only apply to non-placed excerpts
        non_placed_only = {
            "unplaced_reason",
            "best_candidates",
            "declared_science_id",
            "pending_since_utc",
        }
        pa_fields = set(PlacementAdditions.model_fields.keys()) - non_placed_only
        tpe_fields = set(TaxonomyPlacedExcerpt.model_fields.keys())
        missing = pa_fields - tpe_fields
        assert missing == set(), (
            f"PlacementAdditions fields missing from TaxonomyPlacedExcerpt: {missing}"
        )


# ── A1 partial: tracer-era gap ───────────────────────────────────


class TestTracerLegacyGap:
    """Document that the tracer output does NOT match the runtime contract.

    These tests codify the A1 partial state. When the tracer is updated
    to emit the runtime shape, these tests should be inverted or removed.
    """

    def _tracer_placement(self) -> dict:
        """Shape the taxonomy tracer currently emits (legacy)."""
        return {
            "excerpt_id": "exc_test_001",
            "source_id": "src_test",
            "confirmed_leaf": "nahw/kalaam/definition",
            "placement_confidence": 0.6,
            "placed_utc": "2026-04-01T00:00:00Z",
            "review_metadata": {"review_outcome": "auto_approved"},
            "verified_flagged_status": "verified",
            "taxonomy_version_at_placement": "tracer_v0",
            "placement_reasoning": "Tracer stub",
            "proposed_leaf_override": False,
            "proposed_leaf_original": None,
            "override_reason": None,
        }

    def test_tracer_output_fails_placement_additions(self) -> None:
        """Tracer lacks lifecycle_stage and placement_route."""
        with pytest.raises(ValidationError, match="lifecycle_stage"):
            PlacementAdditions.model_validate(self._tracer_placement())

    def test_tracer_output_fails_taxonomy_placed_excerpt(self) -> None:
        """Tracer lacks primary_text (no upstream merge)."""
        with pytest.raises(ValidationError, match="primary_text"):
            TaxonomyPlacedExcerpt.model_validate(self._tracer_placement())
