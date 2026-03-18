"""Contract round-trip tests for normalization engine (Session 1).

Tests the Pydantic models in contracts.py — serialization, deserialization,
validation constraints, and enum behavior. Uses real Arabic text throughout.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from engines.normalization.contracts import (
    ContentFlags,
    ContentUnit,
    DivisionNode,
    DivisionType,
    HeadingConfidence,
    HeadingDetectionMethod,
    LayerMapEntry,
    LayerType,
    NormalizedManifest,
    PhysicalPage,
    QualityReport,
    StructuralFormat,
    StructuralMarkers,
    TextFidelity,
    TextFidelityLevel,
    TextFidelitySummary,
    TextLayerSegment,
)
from engines.normalization.src.errors import ERROR_SEVERITY, NormErrorCode


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _make_division_node(**overrides) -> DivisionNode:
    """Create a DivisionNode with sensible defaults, overridable."""
    defaults = {
        "div_id": "div_src_00147_1_000",
        "division_type": DivisionType.KITAB,
        "heading_text": "كتاب الطهارة",
        "heading_level": 1,
        "start_unit_index": 0,
        "end_unit_index": 142,
        "detection_method": HeadingDetectionMethod.HTML_TAGGED,
        "confidence": HeadingConfidence.CONFIRMED,
    }
    defaults.update(overrides)
    return DivisionNode(**defaults)


def _make_layer_map_entry(**overrides) -> LayerMapEntry:
    """Create a LayerMapEntry with sensible defaults, overridable."""
    defaults = {
        "layer_type": LayerType.MATN,
        "confidence": 0.95,
        "markers": ["bold"],
    }
    defaults.update(overrides)
    return LayerMapEntry(**defaults)


# ──────────────────────────────────────────────────────────────────
# 1. DivisionNode round-trip
# ──────────────────────────────────────────────────────────────────

class TestDivisionNodeRoundTrip:
    """DivisionNode with all 9 fields survives JSON serialization."""

    def test_basic_roundtrip(self):
        # Arrange
        node = _make_division_node()

        # Act
        json_str = node.model_dump_json()
        restored = DivisionNode.model_validate_json(json_str)

        # Assert
        assert restored.div_id == "div_src_00147_1_000"
        assert restored.division_type == DivisionType.KITAB
        assert restored.heading_text == "كتاب الطهارة"
        assert restored.heading_level == 1
        assert restored.start_unit_index == 0
        assert restored.end_unit_index == 142
        assert restored.detection_method == HeadingDetectionMethod.HTML_TAGGED
        assert restored.confidence == HeadingConfidence.CONFIRMED
        assert restored.children == []

    def test_arabic_division_type_survives_json(self):
        """Arabic enum values must not be corrupted by JSON encoding."""
        # Arrange
        node = _make_division_node(division_type=DivisionType.BAB)

        # Act
        json_str = node.model_dump_json()
        data = json.loads(json_str)
        restored = DivisionNode.model_validate_json(json_str)

        # Assert — check both raw JSON and deserialized
        assert data["division_type"] == "باب"
        assert restored.division_type == DivisionType.BAB
        assert restored.division_type.value == "باب"

    def test_none_division_type(self):
        """division_type=None when heading doesn't match known keywords."""
        # Arrange
        node = _make_division_node(
            division_type=None,
            heading_text="ملحق: فوائد منثورة",
        )

        # Act
        json_str = node.model_dump_json()
        restored = DivisionNode.model_validate_json(json_str)

        # Assert
        assert restored.division_type is None

    def test_nested_children_roundtrip(self):
        """Nested division tree survives JSON round-trip."""
        # Arrange
        child1 = _make_division_node(
            div_id="div_src_00147_2_000",
            division_type=DivisionType.BAB,
            heading_text="باب الوضوء",
            heading_level=2,
            start_unit_index=0,
            end_unit_index=50,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.HIGH,
        )
        child2 = _make_division_node(
            div_id="div_src_00147_2_001",
            division_type=DivisionType.BAB,
            heading_text="باب الغسل",
            heading_level=2,
            start_unit_index=51,
            end_unit_index=100,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.HIGH,
        )
        grandchild = _make_division_node(
            div_id="div_src_00147_3_000",
            division_type=DivisionType.FASL,
            heading_text="فصل في المسح على الخفين",
            heading_level=3,
            start_unit_index=0,
            end_unit_index=20,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.HIGH,
        )
        child1_with_grandchild = child1.model_copy(
            update={"children": [grandchild]}
        )
        root = _make_division_node(children=[child1_with_grandchild, child2])

        # Act
        json_str = root.model_dump_json()
        restored = DivisionNode.model_validate_json(json_str)

        # Assert
        assert len(restored.children) == 2
        assert restored.children[0].heading_text == "باب الوضوء"
        assert len(restored.children[0].children) == 1
        assert restored.children[0].children[0].heading_text == "فصل في المسح على الخفين"
        assert restored.children[0].children[0].division_type == DivisionType.FASL

    def test_dict_roundtrip(self):
        """model_dump() → model_validate() round-trip."""
        # Arrange
        node = _make_division_node()

        # Act
        data = node.model_dump()
        restored = DivisionNode.model_validate(data)

        # Assert
        assert restored == node


# ──────────────────────────────────────────────────────────────────
# 2. DivisionNode validation
# ──────────────────────────────────────────────────────────────────

class TestDivisionNodeValidation:
    """DivisionNode field constraints are enforced."""

    def test_heading_level_min(self):
        """heading_level=-1 is invalid (ge=0 for volume boundaries at level 0)."""
        with pytest.raises(ValidationError, match="heading_level"):
            _make_division_node(heading_level=-1)

    def test_heading_level_max(self):
        with pytest.raises(ValidationError, match="heading_level"):
            _make_division_node(heading_level=11)

    def test_heading_level_boundary_valid(self):
        """Boundaries 0 (volume) and 10 are valid."""
        node_vol = _make_division_node(heading_level=0)
        node_min = _make_division_node(heading_level=1)
        node_max = _make_division_node(heading_level=10)
        assert node_vol.heading_level == 0
        assert node_min.heading_level == 1
        assert node_max.heading_level == 10

    def test_start_unit_index_negative(self):
        with pytest.raises(ValidationError, match="start_unit_index"):
            _make_division_node(start_unit_index=-1)

    def test_end_unit_index_negative(self):
        with pytest.raises(ValidationError, match="end_unit_index"):
            _make_division_node(end_unit_index=-1)

    def test_zero_indices_valid(self):
        """Zero is valid for both start and end."""
        node = _make_division_node(start_unit_index=0, end_unit_index=0)
        assert node.start_unit_index == 0
        assert node.end_unit_index == 0


# ──────────────────────────────────────────────────────────────────
# 3. DivisionType enum
# ──────────────────────────────────────────────────────────────────

class TestDivisionTypeEnum:
    """All 13 DivisionType values serialize/deserialize correctly."""

    @pytest.mark.parametrize(
        "member",
        list(DivisionType),
        ids=[m.name for m in DivisionType],
    )
    def test_json_roundtrip_all_values(self, member: DivisionType):
        """Every DivisionType value survives JSON serialization."""
        # Arrange
        node = _make_division_node(division_type=member)

        # Act
        json_str = node.model_dump_json()
        data = json.loads(json_str)
        restored = DivisionNode.model_validate_json(json_str)

        # Assert
        assert data["division_type"] == member.value
        assert restored.division_type == member

    def test_enum_count(self):
        """Exactly 13 division types defined."""
        assert len(DivisionType) == 13

    def test_arabic_values_preserved(self):
        """Arabic string values are not mangled."""
        assert DivisionType.KITAB.value == "كتاب"
        assert DivisionType.BAB.value == "باب"
        assert DivisionType.FASL.value == "فصل"
        assert DivisionType.MABHATH.value == "مبحث"
        assert DivisionType.MATLAB.value == "مطلب"
        assert DivisionType.FAIDAH.value == "فائدة"
        assert DivisionType.TANBIH.value == "تنبيه"
        assert DivisionType.QAIDAH.value == "قاعدة"
        assert DivisionType.KHATIMAH.value == "خاتمة"
        assert DivisionType.MUQADDIMAH.value == "مقدمة"

    def test_non_arabic_values(self):
        """Non-Arabic sentinel values."""
        assert DivisionType.IMPLICIT.value == "implicit"
        assert DivisionType.VOLUME.value == "volume"
        assert DivisionType.ROOT.value == "root"

    def test_str_enum_behavior(self):
        """DivisionType is a str enum — usable in string comparisons."""
        assert DivisionType.KITAB == "كتاب"
        assert DivisionType.IMPLICIT == "implicit"


# ──────────────────────────────────────────────────────────────────
# 4. LayerMapEntry round-trip
# ──────────────────────────────────────────────────────────────────

class TestLayerMapEntryRoundTrip:
    """LayerMapEntry with renamed field and new markers field."""

    def test_basic_roundtrip(self):
        # Arrange
        entry = _make_layer_map_entry(
            author_canonical_id="sch_00042",
            author_name_arabic="ابن قدامة",
            markers=["bold", "قال المصنف"],
        )

        # Act
        json_str = entry.model_dump_json()
        restored = LayerMapEntry.model_validate_json(json_str)

        # Assert
        assert restored.layer_type == LayerType.MATN
        assert restored.confidence == 0.95
        assert restored.markers == ["bold", "قال المصنف"]
        assert restored.author_canonical_id == "sch_00042"
        assert restored.author_name_arabic == "ابن قدامة"

    def test_json_key_is_confidence_not_detection_confidence(self):
        """The JSON key must be 'confidence', not 'detection_confidence'."""
        # Arrange
        entry = _make_layer_map_entry()

        # Act
        data = json.loads(entry.model_dump_json())

        # Assert
        assert "confidence" in data
        assert "detection_confidence" not in data

    def test_empty_markers_default(self):
        """markers defaults to empty list."""
        entry = LayerMapEntry(layer_type=LayerType.SHARH, confidence=0.8)
        assert entry.markers == []

    def test_markers_with_arabic_content(self):
        """Arabic marker strings survive round-trip."""
        # Arrange
        entry = _make_layer_map_entry(
            markers=["قال الشارح", "brackets", "والحاصل"],
        )

        # Act
        json_str = entry.model_dump_json()
        restored = LayerMapEntry.model_validate_json(json_str)

        # Assert
        assert restored.markers == ["قال الشارح", "brackets", "والحاصل"]


# ──────────────────────────────────────────────────────────────────
# 5. LayerMapEntry backward incompatibility
# ──────────────────────────────────────────────────────────────────

class TestLayerMapEntryBackwardIncompatibility:
    """Old JSON with 'detection_confidence' must NOT deserialize."""

    def test_old_json_rejected(self):
        """JSON using the old field name 'detection_confidence' is rejected."""
        # Arrange — old-format JSON
        old_json = json.dumps({
            "layer_type": "matn",
            "detection_confidence": 0.95,
        })

        # Act & Assert — confidence is required, detection_confidence is unknown
        with pytest.raises(ValidationError):
            LayerMapEntry.model_validate_json(old_json)

    def test_new_json_accepted(self):
        """JSON using the new field name 'confidence' works."""
        # Arrange
        new_json = json.dumps({
            "layer_type": "matn",
            "confidence": 0.95,
        })

        # Act
        entry = LayerMapEntry.model_validate_json(new_json)

        # Assert
        assert entry.confidence == 0.95


# ──────────────────────────────────────────────────────────────────
# 6. NormalizedManifest with expanded DivisionNode
# ──────────────────────────────────────────────────────────────────

class TestNormalizedManifestWithDivisionNode:
    """Full NormalizedManifest with the 9-field DivisionNode."""

    def test_manifest_roundtrip_with_division_tree(self):
        # Arrange
        child = _make_division_node(
            div_id="div_src_00147_2_000",
            division_type=DivisionType.BAB,
            heading_text="باب الوضوء",
            heading_level=2,
            start_unit_index=0,
            end_unit_index=50,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.HIGH,
        )
        root_div = _make_division_node(
            div_id="div_src_00147_1_000",
            division_type=DivisionType.KITAB,
            heading_text="كتاب الطهارة",
            heading_level=1,
            start_unit_index=0,
            end_unit_index=142,
            children=[child],
        )
        manifest = NormalizedManifest(
            source_id="src_00147",
            normalizer_id="kr.normalization.shamela_v2",
            normalization_utc="2026-03-18T10:00:00Z",
            division_tree=[root_div],
            layer_map=[
                _make_layer_map_entry(
                    author_canonical_id="sch_00042",
                    author_name_arabic="ابن قدامة",
                    markers=["bold"],
                ),
            ],
            structural_format=StructuralFormat.COMMENTARY,
            text_fidelity_summary=TextFidelitySummary(),
            total_content_units=143,
            quality_report=QualityReport(),
        )

        # Act
        json_str = manifest.model_dump_json()
        restored = NormalizedManifest.model_validate_json(json_str)

        # Assert
        assert len(restored.division_tree) == 1
        tree_root = restored.division_tree[0]
        assert tree_root.div_id == "div_src_00147_1_000"
        assert tree_root.division_type == DivisionType.KITAB
        assert tree_root.heading_text == "كتاب الطهارة"
        assert len(tree_root.children) == 1
        assert tree_root.children[0].division_type == DivisionType.BAB
        assert tree_root.children[0].heading_text == "باب الوضوء"
        assert restored.layer_map[0].confidence == 0.95
        assert restored.layer_map[0].markers == ["bold"]

    def test_manifest_with_empty_division_tree(self):
        """Manifest with no divisions is valid."""
        # Arrange
        manifest = NormalizedManifest(
            source_id="src_00001",
            normalizer_id="kr.normalization.plain_text_v1",
            normalization_utc="2026-03-18T10:00:00Z",
            division_tree=[],
            layer_map=[_make_layer_map_entry()],
            structural_format=StructuralFormat.PROSE,
            text_fidelity_summary=TextFidelitySummary(),
            total_content_units=5,
            quality_report=QualityReport(),
        )

        # Act
        json_str = manifest.model_dump_json()
        restored = NormalizedManifest.model_validate_json(json_str)

        # Assert
        assert restored.division_tree == []


# ──────────────────────────────────────────────────────────────────
# 7. Error code completeness
# ──────────────────────────────────────────────────────────────────

class TestErrorCodeCompleteness:
    """Every NormErrorCode has a severity mapping."""

    def test_all_codes_have_severity(self):
        """Every enum value in NormErrorCode must appear in ERROR_SEVERITY."""
        # Arrange
        missing = [
            code for code in NormErrorCode
            if code not in ERROR_SEVERITY
        ]

        # Assert
        assert missing == [], f"NormErrorCode values missing from ERROR_SEVERITY: {missing}"

    def test_no_extra_severity_entries(self):
        """ERROR_SEVERITY must not contain keys that aren't in NormErrorCode."""
        extra = [
            code for code in ERROR_SEVERITY
            if code not in NormErrorCode
        ]
        assert extra == [], f"ERROR_SEVERITY has keys not in NormErrorCode: {extra}"

    def test_code_count(self):
        """We expect exactly 31 error codes after Session 1."""
        assert len(NormErrorCode) == 31

    def test_severity_count_matches(self):
        """ERROR_SEVERITY has exactly as many entries as NormErrorCode."""
        assert len(ERROR_SEVERITY) == len(NormErrorCode)
