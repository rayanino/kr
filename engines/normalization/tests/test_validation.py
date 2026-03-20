"""Tests for §5 Layer 1 validation checks — SPEC §5.

Each check has at least one positive (valid input passes) and one negative
(invalid input caught) test. ADV adversarial cases have dedicated tests
with exact inputs from the adversary file.
"""

from __future__ import annotations

import pytest

from engines.normalization.contracts import (
    BoundaryContinuity,
    BoundaryContinuityType,
    ContentFlags,
    ContentUnit,
    ContinuityDetectionMethod,
    DivisionNode,
    Footnote,
    FootnoteType,
    HeadingConfidence,
    HeadingDetectionMethod,
    LayerMapEntry,
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
    PhysicalPage,
    QualityReport,
    StructuralFormat,
    TextFidelity,
    TextFidelityLevel,
    TextFidelitySummary,
    TextLayerSegment,
)
from engines.normalization.src.errors import NormErrorCode
from engines.normalization.src.validation import (
    DIACRITICS_CHECK8,
    ValidationResult,
    check_diacritics_page,
    validate_package,
)
from engines.normalization.tests.conftest import (
    _make_content_unit,
    _make_normalized_package,
    _make_source_metadata,
)


# ══════════════════════════════════════════════════════════════════════
# Check 8 utility — check_diacritics_page
# ══════════════════════════════════════════════════════════════════════


class TestCheckDiacriticsPage:
    """Tests for the standalone diacritics preservation utility."""

    def test_matching_diacritics_returns_true(self):
        """ADV-045: identical diacritics → True."""
        text = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
        assert check_diacritics_page(text, text) is True

    def test_missing_diacritic_returns_false(self):
        """ADV-045: single diacritic removed → False."""
        source = "بِسْمِ"  # has kasra on ba and mim
        output = "بسْمِ"   # kasra removed from ba
        assert check_diacritics_page(source, output) is False

    def test_adv021_no_normalization_drift(self):
        """ADV-021: text with U+0670 superscript alef passes unchanged."""
        text = "لَا إِلٰهَ إِلَّا اللّٰهُ"
        assert check_diacritics_page(text, text) is True

    def test_tatweel_counted(self):
        """U+0640 (tatweel/kashida) is in the check 8 set."""
        assert 0x0640 in DIACRITICS_CHECK8
        source = "كتـــاب"  # 3 tatweels
        output = "كتاب"     # 0 tatweels
        assert check_diacritics_page(source, output) is False

    def test_empty_strings_match(self):
        """Two empty strings have matching (zero) diacritics."""
        assert check_diacritics_page("", "") is True

    def test_check8_set_has_10_codepoints(self):
        """DIACRITICS_CHECK8 must have exactly 10 codepoints per D6-3."""
        assert len(DIACRITICS_CHECK8) == 10


# ══════════════════════════════════════════════════════════════════════
# Check 1 — Schema compliance
# ══════════════════════════════════════════════════════════════════════


class TestSchemaCompliance:
    """§5 check 1: schema re-validation and total_content_units consistency."""

    def test_valid_package_passes(self):
        """A correctly formed package passes schema compliance."""
        pkg = _make_normalized_package()
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert result.passed

    def test_adv033_total_content_units_mismatch(self):
        """ADV-033: total_content_units disagrees with actual count → fatal."""
        pkg = _make_normalized_package(num_units=4)
        # Tamper: set total_content_units to 5 but only 4 CUs
        pkg.manifest.total_content_units = 5
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed
        assert any(
            NormErrorCode.SCHEMA_VIOLATION == e.code
            for e in result.fatal_errors
        )

    def test_empty_content_units_with_nonzero_total(self):
        """Zero CUs but total_content_units > 0 → fatal."""
        pkg = _make_normalized_package(num_units=0)
        pkg.manifest.total_content_units = 1
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed


# ══════════════════════════════════════════════════════════════════════
# Check 2 — Coverage check
# ══════════════════════════════════════════════════════════════════════


class TestCoverageCheck:
    """§5 check 2: loose ±10% page count tolerance."""

    def test_adv028_89_of_100_triggers_warning(self):
        """ADV-028: 89/100 = 11% → warning."""
        pkg = _make_normalized_package(num_units=89)
        meta = _make_source_metadata(page_count=100)
        result = validate_package(pkg, meta)
        assert result.passed  # warning, not fatal
        assert any("NORM_PAGE_COUNT_MISMATCH" in w for w in result.warnings)

    def test_adv028_91_of_100_passes(self):
        """ADV-028: 91/100 = 9% → no warning."""
        pkg = _make_normalized_package(num_units=91)
        meta = _make_source_metadata(page_count=100)
        result = validate_package(pkg, meta)
        assert not any("NORM_PAGE_COUNT_MISMATCH" in w for w in result.warnings)

    def test_adv028_90_of_100_passes(self):
        """ADV-028: 90/100 = exactly 10% → no warning (> not >=)."""
        pkg = _make_normalized_package(num_units=90)
        meta = _make_source_metadata(page_count=100)
        result = validate_package(pkg, meta)
        assert not any("NORM_PAGE_COUNT_MISMATCH" in w for w in result.warnings)

    def test_skip_when_page_count_none(self):
        """Coverage check skipped when page_count is None."""
        pkg = _make_normalized_package(num_units=1)
        meta = _make_source_metadata()  # page_count defaults to None
        result = validate_package(pkg, meta)
        assert not any("NORM_PAGE_COUNT_MISMATCH" in w for w in result.warnings)


# ══════════════════════════════════════════════════════════════════════
# Check 3 — Text extraction verification
# ══════════════════════════════════════════════════════════════════════


class TestTextExtraction:
    """§5 check 3: Arabic ratio, garbage runs, mojibake."""

    def test_adv025_arabic_ratio_exactly_70_passes(self):
        """ADV-025: exactly 70% Arabic → passes (>= 0.70)."""
        # 7 Arabic chars + 3 Latin chars = 10 non-ws-non-punct = 70%
        text = "ا" * 7 + "abc"
        pkg = _make_normalized_package(primary_text=text)
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not any("Low Arabic ratio" in w for w in result.warnings)

    def test_adv025_arabic_ratio_below_70_warns(self):
        """ADV-025: below 70% Arabic → warning."""
        # 69 Arabic + 31 Latin = 69%
        text = "ا" * 69 + "a" * 31
        pkg = _make_normalized_package(primary_text=text)
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert any("Low Arabic ratio" in w for w in result.warnings)

    def test_adv029_run_of_20_no_flag(self):
        """ADV-029: exactly 20 identical chars → no flag."""
        text = "كتاب " + "a" * 20 + " النحو العربي وعلومه"
        pkg = _make_normalized_package(primary_text=text)
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not any("Identical character run" in w for w in result.warnings)

    def test_adv029_run_of_21_flags(self):
        """ADV-029: 21 identical chars → flag."""
        text = "كتاب " + "a" * 21 + " النحو العربي وعلومه"
        pkg = _make_normalized_package(primary_text=text)
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert any("Identical character run" in w for w in result.warnings)

    def test_mojibake_detection(self):
        """3+ consecutive Latin Extended chars → mojibake warning."""
        text = "كتاب النحو ÀÁÂ العربي وعلومه"
        pkg = _make_normalized_package(primary_text=text)
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert any("mojibake" in w for w in result.warnings)

    def test_empty_text_on_non_blank_page_fatal(self):
        """Empty primary_text on non-blank page → fatal."""
        cu = _make_content_unit(primary_text="   ")
        cu.content_flags = ContentFlags(is_blank=False)
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed

    def test_blank_page_skipped(self):
        """Blank pages (is_blank=True) are skipped entirely."""
        cu = _make_content_unit(primary_text="")
        cu.content_flags = ContentFlags(is_blank=True)
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert result.passed


# ══════════════════════════════════════════════════════════════════════
# Check 4 — Layer consistency
# ══════════════════════════════════════════════════════════════════════


class TestLayerConsistency:
    """§5 check 4: multi-layer coverage, proportions, transitions."""

    def test_single_layer_skipped(self):
        """Check 4 only runs on multi-layer sources."""
        pkg = _make_normalized_package()
        meta = _make_source_metadata(is_multi_layer=False)
        result = validate_package(pkg, meta)
        assert result.passed

    def test_full_coverage_violation_fatal(self):
        """Gap in text_layers coverage → fatal."""
        text = "بسم الله الرحمن الرحيم وبعد"
        cu = _make_content_unit(
            primary_text=text,
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.SHARH,
                    author_canonical_id=None,
                    start=0,
                    end=10,  # gap from 10 to len(text)
                    confidence=1.0,
                ),
            ],
        )
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata(is_multi_layer=True)
        result = validate_package(pkg, meta)
        assert not result.passed

    def test_matn_ratio_warning_in_sharh(self):
        """Matn ratio >= 0.40 in sharh → warning."""
        text = "م" * 50 + "ش" * 50  # 50% matn
        cu = _make_content_unit(
            primary_text=text,
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0, end=50, confidence=1.0,
                ),
                TextLayerSegment(
                    layer_type=LayerType.SHARH,
                    author_canonical_id=None,
                    start=50, end=100, confidence=1.0,
                ),
            ],
        )
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata(is_multi_layer=True, genre="sharh")
        result = validate_package(pkg, meta)
        assert any("matn ratio" in w.lower() for w in result.warnings)

    def test_excessive_transitions_warning(self):
        """More than 20 layer transitions on one page → warning."""
        # 22 segments = 21 transitions (>20)
        text = "ا" * 44
        segments = []
        for i in range(22):
            layer = LayerType.MATN if i % 2 == 0 else LayerType.SHARH
            segments.append(TextLayerSegment(
                layer_type=layer,
                author_canonical_id=None,
                start=i * 2, end=(i * 2) + 2, confidence=1.0,
            ))
        cu = _make_content_unit(primary_text=text, text_layers=segments)
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata(is_multi_layer=True)
        result = validate_package(pkg, meta)
        assert any("transition" in w.lower() for w in result.warnings)


# ══════════════════════════════════════════════════════════════════════
# Check 5 — Division tree validity
# ══════════════════════════════════════════════════════════════════════


class TestDivisionTree:
    """§5 check 5: ordering, overlap, child bounds, coverage."""

    def test_valid_tree_passes(self):
        """A well-formed division tree passes."""
        pkg = _make_normalized_package(num_units=5)
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert result.passed

    def test_start_greater_than_end_fatal(self):
        """start_unit_index > end_unit_index → fatal."""
        pkg = _make_normalized_package(num_units=5)
        pkg.manifest.division_tree = [
            DivisionNode(
                div_id="div_bad_0_0",
                division_type=None,
                heading_text="bad",
                heading_level=0,
                start_unit_index=3,
                end_unit_index=1,  # bad: start > end
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
            ),
        ]
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed

    def test_sibling_overlap_warning(self):
        """Overlapping sibling divisions → warning (inclusive end)."""
        pkg = _make_normalized_package(num_units=10)
        pkg.manifest.division_tree = [
            DivisionNode(
                div_id="div_a_0_0", division_type=None, heading_text="A",
                heading_level=0, start_unit_index=0, end_unit_index=5,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
            ),
            DivisionNode(
                div_id="div_b_0_1", division_type=None, heading_text="B",
                heading_level=0, start_unit_index=5, end_unit_index=9,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
            ),
        ]
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        # [0,5] and [5,9] overlap at index 5 (inclusive end) — warning
        assert result.passed
        assert any("overlap" in w.lower() for w in result.warnings)

    def test_non_overlapping_siblings_pass(self):
        """[0,5] and [6,9] do not overlap."""
        pkg = _make_normalized_package(num_units=10)
        pkg.manifest.division_tree = [
            DivisionNode(
                div_id="div_a_0_0", division_type=None, heading_text="A",
                heading_level=0, start_unit_index=0, end_unit_index=5,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
            ),
            DivisionNode(
                div_id="div_b_0_1", division_type=None, heading_text="B",
                heading_level=0, start_unit_index=6, end_unit_index=9,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
            ),
        ]
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert result.passed

    def test_child_outside_parent_fatal(self):
        """Child division extending beyond parent → fatal."""
        pkg = _make_normalized_package(num_units=10)
        pkg.manifest.division_tree = [
            DivisionNode(
                div_id="div_parent_0_0", division_type=None, heading_text="Parent",
                heading_level=0, start_unit_index=0, end_unit_index=5,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
                children=[
                    DivisionNode(
                        div_id="div_child_1_0", division_type=None,
                        heading_text="Child",
                        heading_level=1, start_unit_index=0, end_unit_index=7,
                        detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                        confidence=HeadingConfidence.HIGH,
                    ),
                ],
            ),
        ]
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed

    def test_coverage_gap_warning(self):
        """Gap in top-level coverage → warning (not fatal)."""
        pkg = _make_normalized_package(num_units=10)
        # Only covers [0,3] — gap at [4,9]
        pkg.manifest.division_tree = [
            DivisionNode(
                div_id="div_a_0_0", division_type=None, heading_text="A",
                heading_level=0, start_unit_index=0, end_unit_index=3,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
            ),
        ]
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert result.passed  # warning, not fatal
        assert any("does not cover" in w for w in result.warnings)


# ══════════════════════════════════════════════════════════════════════
# Check 6 — Footnote integrity
# ══════════════════════════════════════════════════════════════════════


class TestFootnoteIntegrity:
    """§5 check 6: non-empty text, orphan references."""

    def test_empty_footnote_text_warning(self):
        """Empty footnote text → warning."""
        cu = _make_content_unit()
        cu.footnotes = [
            Footnote(
                ref_marker="1", text="", footnote_type=FootnoteType.UNKNOWN,
                confidence=0.5,
            ),
        ]
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert any("Empty footnote text" in w for w in result.warnings)

    def test_orphan_footnote_ref_info(self):
        """⌜3⌝ marker in text with no matching footnote → warning."""
        cu = _make_content_unit(primary_text="كتاب النحو ⌜3⌝ العربي")
        cu.footnotes = [
            Footnote(
                ref_marker="1", text="حاشية", footnote_type=FootnoteType.UNKNOWN,
                confidence=0.5,
            ),
        ]
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert any("NORM_ORPHAN_FOOTNOTE_REF" in w and "⌜3⌝" in w for w in result.warnings)

    def test_matching_footnote_no_orphan(self):
        """⌜1⌝ marker with matching footnote → no orphan warning."""
        cu = _make_content_unit(primary_text="كتاب النحو ⌜1⌝ العربي")
        cu.footnotes = [
            Footnote(
                ref_marker="1", text="حاشية", footnote_type=FootnoteType.UNKNOWN,
                confidence=0.5,
            ),
        ]
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not any("NORM_ORPHAN_FOOTNOTE_REF" in w for w in result.warnings)


# ══════════════════════════════════════════════════════════════════════
# Check 7 — Unit index integrity
# ══════════════════════════════════════════════════════════════════════


class TestUnitIndexIntegrity:
    """§5 check 7: contiguous zero-based sequence."""

    def test_contiguous_sequence_passes(self):
        """0, 1, 2 → passes."""
        pkg = _make_normalized_package(num_units=3)
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert result.passed

    def test_gap_in_sequence_fatal(self):
        """0, 1, 3 (missing 2) → fatal."""
        units = [
            _make_content_unit(unit_index=0),
            _make_content_unit(unit_index=1),
            _make_content_unit(unit_index=3),
        ]
        pkg = _make_normalized_package(content_units=units)
        pkg.manifest.total_content_units = 3
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed
        assert any(e.code == NormErrorCode.UNIT_INDEX_VIOLATION for e in result.fatal_errors)

    def test_duplicate_index_fatal(self):
        """0, 1, 1, 2 → fatal (duplicate 1)."""
        units = [
            _make_content_unit(unit_index=0),
            _make_content_unit(unit_index=1),
            _make_content_unit(unit_index=1),
            _make_content_unit(unit_index=2),
        ]
        pkg = _make_normalized_package(content_units=units)
        pkg.manifest.total_content_units = 4
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed


# ══════════════════════════════════════════════════════════════════════
# Check 10 — Boundary continuity consistency
# ══════════════════════════════════════════════════════════════════════


class TestBoundaryContinuity:
    """§5 check 10: type, confidence, mid_sentence + punct, last unit."""

    def _make_boundary(
        self,
        btype: BoundaryContinuityType = BoundaryContinuityType.MID_PARAGRAPH,
        confidence: float = 0.8,
    ) -> BoundaryContinuity:
        return BoundaryContinuity(
            type=btype,
            confidence=confidence,
            detection_method=ContinuityDetectionMethod.PUNCTUATION_ANALYSIS,
            continuation_hint=None,
        )

    def test_adv026_mid_sentence_terminal_period(self):
        """ADV-026: mid_sentence + period → warning + confidence 0.0."""
        cu = _make_content_unit(
            primary_text="وقد اختلف العلماء في هذه المسألة.",
        )
        cu.boundary_continuity = self._make_boundary(
            BoundaryContinuityType.MID_SENTENCE, 0.9,
        )
        # Need a second unit (last unit has no boundary)
        cu2 = _make_content_unit(unit_index=1)
        pkg = _make_normalized_package(content_units=[cu, cu2])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert any("NORM_CONTINUITY_INCONSISTENT" in w for w in result.warnings)
        assert cu.boundary_continuity.confidence == 0.0

    def test_adv026_arabic_question_mark(self):
        """mid_sentence + Arabic question mark ؟ → warning."""
        cu = _make_content_unit(primary_text="هل هذا صحيح؟")
        cu.boundary_continuity = self._make_boundary(
            BoundaryContinuityType.MID_SENTENCE, 0.85,
        )
        cu2 = _make_content_unit(unit_index=1)
        pkg = _make_normalized_package(content_units=[cu, cu2])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert any("NORM_CONTINUITY_INCONSISTENT" in w for w in result.warnings)
        assert cu.boundary_continuity.confidence == 0.0

    def test_mid_sentence_no_terminal_punct_passes(self):
        """mid_sentence without terminal punct → no warning."""
        cu = _make_content_unit(primary_text="وقد اختلف العلماء في")
        cu.boundary_continuity = self._make_boundary(
            BoundaryContinuityType.MID_SENTENCE, 0.9,
        )
        cu2 = _make_content_unit(unit_index=1)
        pkg = _make_normalized_package(content_units=[cu, cu2])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not any("NORM_CONTINUITY_INCONSISTENT" in w for w in result.warnings)

    def test_last_unit_with_boundary_warns(self):
        """Last content unit having boundary_continuity → warning."""
        cu = _make_content_unit()
        cu.boundary_continuity = self._make_boundary()
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert any(
            "last content unit" in w and "NORM_CONTINUITY_INCONSISTENT" in w
            for w in result.warnings
        )

    def test_last_unit_none_boundary_passes(self):
        """Last unit with boundary_continuity=None → no warning."""
        cu = _make_content_unit()
        cu.boundary_continuity = None
        pkg = _make_normalized_package(content_units=[cu])
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not any("NORM_CONTINUITY_INCONSISTENT" in w for w in result.warnings)
