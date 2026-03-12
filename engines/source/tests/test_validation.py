"""Tests for source engine validation — SPEC §5 Layer 1.

Tests 34–50 from session5-test-plan.md.
Uses real Arabic scholarly text where applicable.
"""

from __future__ import annotations

import pytest

from engines.source.src.validation import (
    _check_confidence_thresholds,
    _check_consistency,
    _check_multi_layer_coherence,
    validate_source_metadata,
)
from shared.validation.src.validation import (
    validate_enrichment_passthrough,
    validate_referential_integrity,
    validate_schema,
)
from pydantic import BaseModel


# ── Minimal data helpers ──


class SimpleModel(BaseModel):
    """Minimal Pydantic model for schema validation tests."""
    name: str
    value: int


def _make_data(**overrides: object) -> dict:
    """Create a minimal validation test data dict (NOT full SourceMetadata)."""
    base = {
        "genre": "risalah",
        "structural_format": "prose",
        "level": "intermediate",
        "is_multi_layer": False,
        "text_layers": [],
        "science_scope": ["fiqh"],
        "attribution_status": "definitive",
        "author": {
            "canonical_id": "sch_00001",
            "name_arabic": "النووي",
            "confidence": 0.90,
            "source_of_identification": "extraction",
        },
        "confidence_scores": {
            "genre": 0.85,
            "science_scope": 0.80,
            "structural_format": 0.90,
            "authority_level": 0.85,
        },
        "source_id": "src_test0001",
        "work_id": "wrk_nawawi_adab",
    }
    base.update(overrides)
    return base


# ── Check 1–2: Schema + Referential Integrity (shared validation) ──


class TestSharedValidation:
    """Tests 34–36: Schema and referential integrity (delegated to shared)."""

    def test_34_valid_metadata_passes(self) -> None:
        """Test 34: Valid data passes schema validation."""
        errors = validate_schema({"name": "test", "value": 42}, SimpleModel)
        assert len(errors) == 0

    def test_35_missing_required_field(self) -> None:
        """Test 35: Missing required field → fatal."""
        errors = validate_schema({"name": "test"}, SimpleModel)
        assert len(errors) >= 1
        assert errors[0].severity == "fatal"
        assert errors[0].recovery == "abort"

    def test_36_referential_integrity_author(self) -> None:
        """Test 36: Author canonical_id not in scholars → fatal."""
        data = {"author": {"canonical_id": "sch_99999"}}
        registries = {"scholars": {"sch_00001": {}}}
        errors = validate_referential_integrity(
            data, registries,
            [("author.canonical_id", "scholars")],
        )
        assert len(errors) == 1
        assert errors[0].error_code == "SRC_REGISTRY_CONFLICT"

    def test_37_referential_integrity_work(self) -> None:
        """Test 37: work_id not in works → fatal."""
        data = {"work_id": "wrk_nonexistent"}
        registries = {"works": {"wrk_existing": {}}}
        errors = validate_referential_integrity(
            data, registries,
            [("work_id", "works")],
        )
        assert len(errors) == 1


# ── Check 3: Confidence Thresholds ──


class TestConfidenceThresholds:
    """Tests 38–39: Confidence threshold checks."""

    def test_38_low_confidence_gates(self) -> None:
        """Test 38: Confidence < 0.50 → gate."""
        data = _make_data()
        data["author"]["confidence"] = 0.40
        errors = _check_confidence_thresholds(data)
        assert len(errors) == 1
        assert errors[0].severity == "gate"
        assert errors[0].error_code == "SRC_LOW_CONFIDENCE"

    def test_39_adequate_confidence_passes(self) -> None:
        """Test 39: Confidence >= 0.50 → no error."""
        data = _make_data()
        data["author"]["confidence"] = 0.60
        errors = _check_confidence_thresholds(data)
        assert len(errors) == 0


# ── Check 5: Consistency Cross-Checks ──


class TestConsistencyChecks:
    """Tests 40–45: Consistency cross-checks (5a-5e)."""

    def test_40_nazm_verse_ok(self) -> None:
        """Test 40: nazm + verse → no error."""
        data = _make_data(genre="nazm", structural_format="verse")
        errors = _check_consistency(data, None, None)
        genre_format_errors = [e for e in errors if e.check == "consistency_genre_format"]
        assert len(genre_format_errors) == 0

    def test_41_sharh_commentary_ok(self) -> None:
        """Test 41: sharh + commentary → no error."""
        data = _make_data(genre="sharh", structural_format="commentary", is_multi_layer=True)
        errors = _check_consistency(data, None, None)
        genre_format_errors = [e for e in errors if e.check == "consistency_genre_format"]
        assert len(genre_format_errors) == 0

    def test_42_sharh_prose_ok(self) -> None:
        """Test 42: sharh + prose → no error (running prose is valid for sharh)."""
        data = _make_data(genre="sharh", structural_format="prose", is_multi_layer=True)
        errors = _check_consistency(data, None, None)
        genre_format_errors = [e for e in errors if e.check == "consistency_genre_format"]
        assert len(genre_format_errors) == 0

    def test_43_hashiyah_beginner_warning(self) -> None:
        """Test 43: hashiyah + beginner → warning."""
        data = _make_data(genre="hashiyah", level="beginner", is_multi_layer=True,
                          structural_format="commentary")
        errors = _check_consistency(data, None, None)
        level_errors = [e for e in errors if e.check == "consistency_level_genre"]
        assert len(level_errors) == 1
        assert level_errors[0].severity == "warning"

    def test_44_author_science_mismatch_gates(self) -> None:
        """Test 44: Author known in nahw but source says fiqh → warning (BUG-01 fix)."""
        data = _make_data(science_scope=["fiqh"])
        registries = {
            "scholars": {
                "sch_00001": {
                    "school_affiliations": {"nahw": "بصري"},
                }
            }
        }
        errors = _check_consistency(data, registries, None)
        science_errors = [e for e in errors if e.check == "consistency_author_science"]
        assert len(science_errors) == 1
        assert science_errors[0].severity == "warning"
        assert science_errors[0].recovery == "human_gate"

    def test_45_sharh_auto_corrects_multi_layer(self) -> None:
        """Test 45: sharh + is_multi_layer=false + layers present → auto-corrected to true."""
        data = _make_data(
            genre="sharh",
            is_multi_layer=False,
            structural_format="commentary",
            text_layers=[{"layer_type": "sharh", "author_name": "الشارح"}],
        )
        errors = _check_consistency(data, None, None)
        # After check 5e, data should be auto-corrected
        assert data["is_multi_layer"] is True
        ml_errors = [e for e in errors if e.check == "consistency_genre_multi_layer"]
        assert len(ml_errors) == 1
        assert "auto-corrected" in ml_errors[0].message


# ── Check 6: Multi-Layer Coherence ──


class TestMultiLayerCoherence:
    """Tests 46–48: Multi-layer coherence checks (6a-6c)."""

    def test_46_multi_layer_empty_layers_gates(self) -> None:
        """Test 46: is_multi_layer=true + empty text_layers → gate."""
        data = _make_data(is_multi_layer=True, text_layers=[])
        errors = _check_multi_layer_coherence(data, None)
        assert len(errors) == 1
        assert errors[0].severity == "gate"
        assert errors[0].recovery == "human_gate"

    def test_47_not_multi_layer_with_layers_auto_corrects(self) -> None:
        """Test 47: is_multi_layer=false + has layers → auto-correct."""
        data = _make_data(
            is_multi_layer=False,
            text_layers=[{
                "layer_type": "matn",
                "author": {"canonical_id": "sch_00001", "name_arabic": "ابن مالك",
                           "confidence": 0.90, "source_of_identification": "extraction"},
            }],
        )
        errors = _check_multi_layer_coherence(data, None)
        assert data["is_multi_layer"] is True
        assert any("auto-corrected" in e.message for e in errors)

    def test_48_layer_author_ref_missing_fatal(self) -> None:
        """Test 48: Layer author canonical_id not in scholars → fatal."""
        data = _make_data(
            is_multi_layer=True,
            text_layers=[{
                "layer_type": "matn",
                "author": {"canonical_id": "sch_99999", "name_arabic": "مجهول",
                           "confidence": 0.50, "source_of_identification": "inference"},
            }],
        )
        registries = {"scholars": {"sch_00001": {}}}
        errors = _check_multi_layer_coherence(data, registries)
        fatal_errors = [e for e in errors if e.severity == "fatal"]
        assert len(fatal_errors) == 1
        assert fatal_errors[0].error_code == "SRC_REGISTRY_CONFLICT"


# ── D-023 Pass-Through ──


class TestPassthrough:
    """Tests 49–50: D-023 enrichment pass-through."""

    def test_49_deleted_field_fatal(self) -> None:
        """Test 49: Field deleted during enrichment → fatal."""
        before = {"title": "أحكام الاضطباع", "author": "النووي"}
        after = {"title": "أحكام الاضطباع", "author": None}
        errors = validate_enrichment_passthrough(before, after)
        assert len(errors) == 1
        assert errors[0].error_code == "SRC_INVALID_ENRICHMENT"
        assert errors[0].severity == "fatal"

    def test_50_added_field_ok(self) -> None:
        """Test 50: New field added during enrichment → OK."""
        before = {"title": "أحكام الاضطباع"}
        after = {"title": "أحكام الاضطباع", "muhaqiq": "أحمد شاكر"}
        errors = validate_enrichment_passthrough(before, after)
        assert len(errors) == 0


# ── Chain: Check 5e → Check 6 ──


class TestAutoCorrectChain:
    """Verify that check 5e auto-correction chains to check 6."""

    def test_sharh_empty_layers_no_auto_correct(self) -> None:
        """sharh + is_multi_layer=false + empty layers → warning, NO auto-correct (BUG-05 fix)."""
        data = _make_data(
            genre="sharh",
            is_multi_layer=False,
            text_layers=[],
            structural_format="commentary",
        )
        errors_5 = _check_consistency(data, None, None)
        # After BUG-05 fix: is_multi_layer stays False (no auto-correct)
        assert data["is_multi_layer"] is False

        no_layers_warns = [e for e in errors_5 if e.check == "consistency_genre_multi_layer_no_layers"]
        assert len(no_layers_warns) == 1
        assert no_layers_warns[0].severity == "warning"

        # Check 6a should NOT fire since is_multi_layer is still False
        errors_6 = _check_multi_layer_coherence(data, None)
        gate_errors = [e for e in errors_6 if e.severity == "gate"]
        assert len(gate_errors) == 0


# ── Check 5f: Tahqiq-note override (BUG-03) ──


class TestTahqiqNoteOverride:
    """Tests for check 5f: auto-correct ML when all layers are {matn, tahqiq_note}."""

    def test_tahqiq_only_layers_clears_ml(self) -> None:
        """is_multi_layer=True + only matn/tahqiq_note → corrected to False, layers cleared."""
        data = _make_data(
            is_multi_layer=True,
            text_layers=[
                {"layer_type": "matn", "author_name": "المؤلف"},
                {"layer_type": "tahqiq_note", "author_name": "المحقق"},
            ],
        )
        errors = _check_consistency(data, None, None)
        assert data["is_multi_layer"] is False
        assert data["text_layers"] == []
        override_errors = [e for e in errors if e.check == "tahqiq_note_override"]
        assert len(override_errors) == 1
        assert "tahqiq editorial apparatus" in override_errors[0].message

    def test_sharh_layer_prevents_override(self) -> None:
        """is_multi_layer=True + sharh layer present → stays True (real commentary)."""
        data = _make_data(
            is_multi_layer=True,
            text_layers=[
                {"layer_type": "matn", "author_name": "المؤلف"},
                {"layer_type": "sharh", "author_name": "الشارح"},
            ],
        )
        errors = _check_consistency(data, None, None)
        assert data["is_multi_layer"] is True
        assert len(data["text_layers"]) == 2
        override_errors = [e for e in errors if e.check == "tahqiq_note_override"]
        assert len(override_errors) == 0

    def test_matn_only_still_overrides(self) -> None:
        """is_multi_layer=True + only matn → corrected (matn ⊂ {matn, tahqiq_note})."""
        data = _make_data(
            is_multi_layer=True,
            text_layers=[{"layer_type": "matn", "author_name": "المؤلف"}],
        )
        errors = _check_consistency(data, None, None)
        assert data["is_multi_layer"] is False
        assert data["text_layers"] == []

    def test_5e_then_5f_chain(self) -> None:
        """sharh + ML=false + tahqiq layers → 5e sets True, 5f overrides back to False."""
        data = _make_data(
            genre="sharh",
            is_multi_layer=False,
            structural_format="commentary",
            text_layers=[
                {"layer_type": "matn", "author_name": "المؤلف"},
                {"layer_type": "tahqiq_note", "author_name": "المحقق"},
            ],
        )
        errors = _check_consistency(data, None, None)
        # Check 5e fires (auto-correct to True), then 5f fires (override to False)
        assert data["is_multi_layer"] is False
        assert data["text_layers"] == []
        # Both corrections should produce warnings
        check_names = {e.check for e in errors}
        assert "consistency_genre_multi_layer" in check_names
        assert "tahqiq_note_override" in check_names
