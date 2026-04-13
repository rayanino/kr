"""Boundary value tests for source engine thresholds.

SPEC references:
- Trust threshold 0.65: §4.A.8, §8 — "Combined >= 0.65 → verified. < 0.65 → flagged."
- Confidence auto-accept 0.70: §5 Layer 2, §8 — "Fields with confidence < 0.70 → needs_review"
- Confidence block 0.50: §5 Layer 1, §8 — "Fields with confidence < 0.50 → block metadata write"
- Empty page ratio 0.25: §4.A.3 — "SRC_HIGH_EMPTY_RATIO | >25% of pages have <50 chars"
- 5-factor weights: §4.A.8 — author=0.30, tahqiq=0.25, publisher=0.15, source=0.15, fidelity=0.15

Every test targets exactly ONE boundary condition with a precisely named test.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engines.source.contracts import (
    AuthorityLevel,
    InferredFieldConfidence,
    ScholarAuthorityRecord,
    ScholarReference,
    TextFidelity,
    TrustTier,
)
from engines.source.src.config import load_config
from engines.source.src.engine import _build_needs_review
from engines.source.src.extractors.shamela_html import _run_quality_inspection
from engines.source.src.metadata_inference import build_needs_review
from engines.source.src.trust_evaluator import evaluate_trust
from engines.source.src.validation import _check_confidence_thresholds
from shared.validation.src.validation import ValidationError


_CONFIG = load_config(Path("library"))


# ── Helpers ──────────────────────────────────────────────────────────


def _make_author_record(death_date: int | None = None) -> ScholarAuthorityRecord:
    """Create a minimal ScholarAuthorityRecord with real Arabic name."""
    return ScholarAuthorityRecord(
        canonical_id="sch_00001",
        canonical_name_ar="ابن عقيل",
        death_date_hijri=death_date,
        last_updated="2026-01-01T00:00:00+00:00",
    )


def _make_ref() -> ScholarReference:
    return ScholarReference(
        canonical_id="sch_00001",
        name_arabic="ابن عقيل",
        confidence=0.90,
        source_of_identification="extraction",
    )


def _eval(
    death_date: int | None = None,
    muhaqiq: str | None = None,
    publisher: str | None = None,
    authority: AuthorityLevel = AuthorityLevel.PRIMARY,
    fidelity: TextFidelity = TextFidelity.HIGH,
) -> tuple:
    """Call evaluate_trust with controlled inputs."""
    record = _make_author_record(death_date)
    if death_date is None:
        record.death_date_hijri = None
    return evaluate_trust(
        author_ref=_make_ref(),
        author_record=record,
        muhaqiq_name=muhaqiq,
        publisher=publisher,
        authority_level=authority,
        text_fidelity=fidelity,
        source_id="src_boundary",
        recognized_muhaqiqs=_CONFIG.recognized_muhaqiqs,
        known_publishers=_CONFIG.known_publishers,
    )


def _make_quality_segments(
    total_pages: int,
    empty_count: int,
) -> list[str]:
    """Build page_segments for quality inspection testing.

    Returns a list where index 0-1 are skipped (metadata),
    and subsequent entries are either 'empty' (<50 chars) or 'non-empty' (>=50 chars).
    """
    non_empty_text = "هذا نص طويل بما يكفي لتجاوز خمسين حرفا ويحتوي على محتوى عربي حقيقي يتعلق بالفقه الإسلامي"
    empty_text = "قصير"

    segments = ["preamble_before_first_div", "metadata_card_content"]
    non_empty_count = total_pages - empty_count
    for _ in range(non_empty_count):
        segments.append(non_empty_text)
    for _ in range(empty_count):
        segments.append(empty_text)
    return segments


# ══════════════════════════════════════════════════════════════════════
# TRUST THRESHOLD (0.65) — SPEC §4.A.8
# "Combined >= 0.65 → verified. < 0.65 → flagged."
# ══════════════════════════════════════════════════════════════════════


class TestTrustThresholdBoundary:
    """Boundary tests for the 0.65 trust score threshold.

    SPEC §4.A.8: 'Combined >= 0.65 → verified. < 0.65 → flagged.'
    The comparison is >= (not >), confirmed by code:
        if trust_score >= 0.65 and not critical_low:
    """

    def test_trust_at_exactly_0_650_verified(self) -> None:
        """Score = 0.650 exactly → VERIFIED (tests >= boundary).

        Factor scores: author=0.90, tahqiq=0.50, publisher=0.40, source=0.40, fidelity=0.90
        = 0.270 + 0.125 + 0.060 + 0.060 + 0.135 = 0.650
        """
        # Classical scholar + unknown muhaqiq + no publisher + modern_compilation + high fidelity
        tier, score, _, _ = _eval(
            death_date=500,
            muhaqiq="محقق غير معروف",  # unknown muhaqiq → 0.50
            publisher=None,
            authority=AuthorityLevel.MODERN_COMPILATION,
            fidelity=TextFidelity.HIGH,
        )
        assert score == pytest.approx(0.650, abs=1e-9), f"Expected 0.650, got {score}"
        assert tier == TrustTier.VERIFIED, "Score of exactly 0.650 should be VERIFIED (>= 0.65)"

    def test_trust_below_0_65_flagged(self) -> None:
        """Nearest achievable score below 0.65 → FLAGGED.

        Factor scores: author=0.90, tahqiq=0.50, publisher=0.40, source=0.85, fidelity=0.40
        = 0.270 + 0.125 + 0.060 + 0.1275 + 0.060 = 0.6425
        """
        tier, score, _, _ = _eval(
            death_date=500,
            muhaqiq="محقق غير معروف",
            publisher=None,
            authority=AuthorityLevel.PRIMARY,
            fidelity=TextFidelity.UNKNOWN,
        )
        assert score == pytest.approx(0.6425, abs=1e-9), f"Expected 0.6425, got {score}"
        assert score < 0.65
        assert tier == TrustTier.FLAGGED, "Score below 0.65 must be FLAGGED"

    def test_trust_above_0_65_verified(self) -> None:
        """Nearest achievable score above 0.65 → VERIFIED.

        Factor scores: author=0.70, tahqiq=0.50, publisher=0.40, source=0.85, fidelity=0.90
        = 0.210 + 0.125 + 0.060 + 0.1275 + 0.135 = 0.6575
        """
        tier, score, _, _ = _eval(
            death_date=1200,           # post-classical → 0.70
            muhaqiq="محقق غير معروف",  # unknown → 0.50
            publisher=None,            # unknown → 0.40
            authority=AuthorityLevel.PRIMARY,   # → 0.85
            fidelity=TextFidelity.HIGH,         # → 0.90
        )
        assert score == pytest.approx(0.6575, abs=1e-9), f"Expected 0.6575, got {score}"
        assert score > 0.65
        assert tier == TrustTier.VERIFIED

    def test_trust_minimum_achievable_flagged(self) -> None:
        """Lowest achievable trust score → FLAGGED.

        Factor scores: author=0.30, tahqiq=0.30, publisher=0.40, source=0.40, fidelity=0.30
        = 0.090 + 0.075 + 0.060 + 0.060 + 0.045 = 0.330
        """
        tier, score, _, _ = _eval(
            death_date=None,  # unknown → 0.30
            muhaqiq=None,     # no muhaqiq, modern (>1300 needs death_date but None→0.35)
            publisher=None,   # unknown → 0.40
            authority=AuthorityLevel.MODERN_COMPILATION,  # → 0.40
            fidelity=TextFidelity.LOW,  # → 0.30
        )
        assert score < 0.65
        assert tier == TrustTier.FLAGGED

    def test_trust_maximum_achievable_verified(self) -> None:
        """Highest achievable trust score → VERIFIED.

        Classical + recognized muhaqiq + primary + high fidelity
        Factor scores: author=0.90, tahqiq=0.90, publisher=0.40, source=0.85, fidelity=0.90
        = 0.270 + 0.225 + 0.060 + 0.1275 + 0.135 = 0.8175
        """
        tier, score, _, _ = _eval(
            death_date=500,
            muhaqiq="شعيب الأرناؤوط",  # recognized → 0.90
            publisher=None,             # unknown → 0.40
            authority=AuthorityLevel.PRIMARY,
            fidelity=TextFidelity.HIGH,
        )
        assert score > 0.65
        assert tier == TrustTier.VERIFIED


# ══════════════════════════════════════════════════════════════════════
# CONFIDENCE AUTO-ACCEPT (0.70) — SPEC §5 Layer 2
# "Fields with confidence < 0.70 → needs_review"
# ══════════════════════════════════════════════════════════════════════


class TestConfidenceAutoAcceptBoundary:
    """Boundary tests for the 0.70 confidence auto-accept threshold.

    SPEC §5 Layer 2: 'Any critical field with confidence < 0.70 → needs_review'
    The comparison is strict < (not <=).
    """

    def test_confidence_at_0_699_needs_review_engine(self) -> None:
        """Genre confidence 0.699 → added to needs_review (engine._build_needs_review)."""
        scores = InferredFieldConfidence(
            genre=0.699,
            science_scope=0.90,
            structural_format=0.90,
            authority_level=0.90,
        )
        result = _build_needs_review(scores)
        assert "genre" in result, "0.699 < 0.70 → genre must be in needs_review"

    def test_confidence_at_0_700_auto_accepted_engine(self) -> None:
        """Genre confidence 0.700 → NOT in needs_review (auto-accepted)."""
        scores = InferredFieldConfidence(
            genre=0.700,
            science_scope=0.90,
            structural_format=0.90,
            authority_level=0.90,
        )
        result = _build_needs_review(scores)
        assert "genre" not in result, "0.700 is NOT < 0.70 → genre must NOT be in needs_review"

    def test_confidence_at_0_701_auto_accepted_engine(self) -> None:
        """Genre confidence 0.701 → NOT in needs_review."""
        scores = InferredFieldConfidence(
            genre=0.701,
            science_scope=0.90,
            structural_format=0.90,
            authority_level=0.90,
        )
        result = _build_needs_review(scores)
        assert "genre" not in result, "0.701 is NOT < 0.70 → genre must NOT be in needs_review"

    def test_confidence_at_0_699_needs_review_inference(self) -> None:
        """Genre confidence 0.699 → added to needs_review (metadata_inference.build_needs_review)."""
        confidence = {"genre": 0.699, "science_scope": 0.90}
        extracted = {"author_name_raw": "ابن عقيل"}
        result = build_needs_review(confidence, extracted)
        assert "genre" in result, "0.699 < 0.70 → genre must be flagged"

    def test_confidence_at_0_700_auto_accepted_inference(self) -> None:
        """Genre confidence 0.700 → NOT in needs_review (metadata_inference.build_needs_review)."""
        confidence = {"genre": 0.700, "science_scope": 0.90}
        extracted = {"author_name_raw": "ابن عقيل"}
        result = build_needs_review(confidence, extracted)
        assert "genre" not in result, "0.700 NOT < 0.70 → genre auto-accepted"

    def test_confidence_at_0_701_auto_accepted_inference(self) -> None:
        """Genre confidence 0.701 → NOT in needs_review (metadata_inference.build_needs_review)."""
        confidence = {"genre": 0.701, "science_scope": 0.90}
        extracted = {"author_name_raw": "ابن عقيل"}
        result = build_needs_review(confidence, extracted)
        assert "genre" not in result, "0.701 NOT < 0.70 → genre auto-accepted"


# ══════════════════════════════════════════════════════════════════════
# CONFIDENCE BLOCK (0.50) — SPEC §5 Layer 1
# "Fields with confidence < 0.50 → block metadata write"
# ══════════════════════════════════════════════════════════════════════


class TestConfidenceBlockBoundary:
    """Boundary tests for the 0.50 confidence block threshold.

    SPEC §5 Layer 1: 'SRC_LOW_CONFIDENCE | Warning | Critical field confidence < 0.50'
    Code in validation.py: 'if value is not None and value < 0.50'
    The comparison is strict < (not <=).
    """

    def test_confidence_block_at_0_499_blocked(self) -> None:
        """Genre confidence 0.499 → SRC_LOW_CONFIDENCE validation error (blocked)."""
        data: dict[str, Any] = {
            "confidence_scores": {
                "genre": 0.499,
                "science_scope": 0.90,
                "structural_format": 0.90,
                "authority_level": 0.90,
            }
        }
        errors = _check_confidence_thresholds(data)
        blocked_fields = [e.field for e in errors]
        assert "confidence_scores.genre" in blocked_fields, (
            "0.499 < 0.50 → genre must trigger SRC_LOW_CONFIDENCE"
        )

    def test_confidence_block_at_0_500_not_blocked(self) -> None:
        """Genre confidence 0.500 → NOT blocked (strict < comparison)."""
        data: dict[str, Any] = {
            "confidence_scores": {
                "genre": 0.500,
                "science_scope": 0.90,
                "structural_format": 0.90,
                "authority_level": 0.90,
            }
        }
        errors = _check_confidence_thresholds(data)
        blocked_fields = [e.field for e in errors]
        assert "confidence_scores.genre" not in blocked_fields, (
            "0.500 is NOT < 0.50 → genre must NOT be blocked"
        )

    def test_confidence_block_at_0_501_not_blocked(self) -> None:
        """Genre confidence 0.501 → NOT blocked."""
        data: dict[str, Any] = {
            "confidence_scores": {
                "genre": 0.501,
                "science_scope": 0.90,
                "structural_format": 0.90,
                "authority_level": 0.90,
            }
        }
        errors = _check_confidence_thresholds(data)
        blocked_fields = [e.field for e in errors]
        assert "confidence_scores.genre" not in blocked_fields, (
            "0.501 is NOT < 0.50 → genre must NOT be blocked"
        )


# ══════════════════════════════════════════════════════════════════════
# EMPTY PAGE RATIO (0.25) — SPEC §4.A.3
# "SRC_HIGH_EMPTY_RATIO | Warning | >25% of pages have <50 chars"
# Code: if body_page_count > 10 and empty_page_count / body_page_count > 0.25
# ══════════════════════════════════════════════════════════════════════


class TestEmptyPageRatioBoundary:
    """Boundary tests for the empty page ratio quality check.

    SPEC §4.A.3: 'SRC_HIGH_EMPTY_RATIO | Warning | >25% of pages have <50 characters'
    Code guard: body_page_count > 10 (small books exempt).
    Threshold comparison: strict > 0.25 (not >=).
    """

    def _has_empty_ratio_issue(self, issues: list[dict[str, str]]) -> bool:
        """Check if high_empty_ratio appears in quality issues."""
        return any(q["check"] == "high_empty_ratio" for q in issues)

    def test_empty_ratio_at_0_250_no_warning(self) -> None:
        """Ratio exactly 0.25 (5/20) → NO warning (strict > comparison).

        SPEC: '>25%' means strictly greater than, not >=.
        """
        body_page_count = 20
        empty_count = 5  # 5/20 = 0.25 exactly
        segments = _make_quality_segments(body_page_count, empty_count)
        issues = _run_quality_inspection(
            body_page_count, {}, "", segments
        )
        assert not self._has_empty_ratio_issue(issues), (
            "Ratio of exactly 0.25 should NOT trigger warning (strict >)"
        )

    def test_empty_ratio_above_0_25_warning(self) -> None:
        """Ratio 0.30 (6/20) → SRC_HIGH_EMPTY_RATIO warning triggered.

        6 out of 20 pages empty = 30% > 25%.
        """
        body_page_count = 20
        empty_count = 6  # 6/20 = 0.30
        segments = _make_quality_segments(body_page_count, empty_count)
        issues = _run_quality_inspection(
            body_page_count, {}, "", segments
        )
        assert self._has_empty_ratio_issue(issues), (
            "Ratio of 0.30 (> 0.25) must trigger high_empty_ratio warning"
        )

    def test_empty_ratio_below_0_25_no_warning(self) -> None:
        """Ratio 0.20 (4/20) → NO warning.

        4 out of 20 pages empty = 20% < 25%.
        """
        body_page_count = 20
        empty_count = 4  # 4/20 = 0.20
        segments = _make_quality_segments(body_page_count, empty_count)
        issues = _run_quality_inspection(
            body_page_count, {}, "", segments
        )
        assert not self._has_empty_ratio_issue(issues), (
            "Ratio of 0.20 (< 0.25) should NOT trigger warning"
        )

    def test_empty_ratio_small_book_exempt(self) -> None:
        """body_page_count = 10 → ratio check skipped regardless of empty count.

        SPEC guard: 'body_page_count > 10'. A 10-page book is exempt.
        """
        body_page_count = 10
        empty_count = 8  # 8/10 = 0.80 — extreme ratio, but book too small
        segments = _make_quality_segments(body_page_count, empty_count)
        issues = _run_quality_inspection(
            body_page_count, {}, "", segments
        )
        assert not self._has_empty_ratio_issue(issues), (
            "Books with <= 10 pages must be exempt from empty ratio check"
        )

    def test_empty_ratio_11_pages_checked(self) -> None:
        """body_page_count = 11 → ratio check IS applied (boundary of > 10).

        3 out of 11 empty = 0.2727 > 0.25 → warning triggered.
        """
        body_page_count = 11
        empty_count = 3  # 3/11 = 0.2727
        segments = _make_quality_segments(body_page_count, empty_count)
        issues = _run_quality_inspection(
            body_page_count, {}, "", segments
        )
        assert self._has_empty_ratio_issue(issues), (
            "11-page book with 27% empty ratio must trigger warning (> 10 guard passed)"
        )


# ══════════════════════════════════════════════════════════════════════
# 5-FACTOR TRUST WEIGHTING — SPEC §4.A.8
# author=0.30, tahqiq=0.25, publisher=0.15, source=0.15, fidelity=0.15
# ══════════════════════════════════════════════════════════════════════


class TestTrustWeights:
    """Verify the 5-factor trust weight constants and their arithmetic.

    SPEC §4.A.8: 'author_standing (0.30), tahqiq_quality (0.25),
    publisher_reputation (0.15), source_authority (0.15), text_fidelity (0.15)'
    """

    def test_weights_sum_to_1_0(self) -> None:
        """All 5 trust factor weights must sum to exactly 1.0."""
        _, _, factors, _ = _eval(death_date=500)
        weights = [f.weight for f in factors]
        assert len(weights) == 5, "Must have exactly 5 trust factors"
        assert sum(weights) == pytest.approx(1.0, abs=1e-9), (
            f"Weights {weights} sum to {sum(weights)}, expected 1.0"
        )

    def test_individual_weight_values(self) -> None:
        """Each weight matches SPEC §4.A.8 exactly."""
        _, _, factors, _ = _eval(death_date=500)
        weight_map = {f.name: f.weight for f in factors}
        assert weight_map["author_standing"] == 0.30
        assert weight_map["tahqiq_quality"] == 0.25
        assert weight_map["publisher_reputation"] == 0.15
        assert weight_map["source_authority"] == 0.15
        assert weight_map["text_fidelity"] == 0.15

    def test_single_factor_maximum_author(self) -> None:
        """Author standing at max (0.90) with all others at minimum → verify weighted result.

        Max author contribution: 0.30 * 0.90 = 0.270.
        """
        tier, score, factors, _ = _eval(
            death_date=500,   # classical → 0.90
            muhaqiq=None,     # no muhaqiq, unknown date → 0.35
            publisher=None,   # unknown → 0.40
            authority=AuthorityLevel.MODERN_COMPILATION,  # → 0.40
            fidelity=TextFidelity.LOW,  # → 0.30
        )
        author_factor = next(f for f in factors if f.name == "author_standing")
        assert author_factor.score == 0.90
        assert author_factor.weight * author_factor.score == pytest.approx(0.270, abs=1e-9)

    def test_all_factors_produce_exactly_0_65(self) -> None:
        """Verify that the combination producing exactly 0.650 is arithmetically correct.

        This validates the trust score formula: sum(weight_i * score_i).
        Factors: author=0.90, tahqiq=0.50, publisher=0.40, source=0.40, fidelity=0.90
        """
        tier, score, factors, _ = _eval(
            death_date=500,
            muhaqiq="محقق غير معروف",
            publisher=None,
            authority=AuthorityLevel.MODERN_COMPILATION,
            fidelity=TextFidelity.HIGH,
        )
        # Verify each factor's contribution
        expected_contributions = {
            "author_standing": 0.30 * 0.90,     # 0.270
            "tahqiq_quality": 0.25 * 0.50,      # 0.125
            "publisher_reputation": 0.15 * 0.40, # 0.060
            "source_authority": 0.15 * 0.40,     # 0.060
            "text_fidelity": 0.15 * 0.90,        # 0.135
        }
        for f in factors:
            expected = expected_contributions[f.name]
            actual = f.weight * f.score
            assert actual == pytest.approx(expected, abs=1e-9), (
                f"{f.name}: expected contribution {expected}, got {actual}"
            )
        assert score == pytest.approx(0.650, abs=1e-9)


# ══════════════════════════════════════════════════════════════════════
# CRITICAL LOW OVERRIDE — SPEC §4.A.8
# "author_standing < 0.30 AND tahqiq_quality < 0.40 → flagged regardless"
# ══════════════════════════════════════════════════════════════════════


class TestCriticalLowOverride:
    """Tests for the critical_low flag that overrides high trust scores.

    SPEC §4.A.8: When author_standing < 0.30 AND tahqiq_quality < 0.40,
    the source is FLAGGED regardless of total score.
    Code: critical_low = author_score < 0.30 and tahqiq_score < 0.40

    Note: With the current scoring formula, author_standing minimum is 0.30
    (unknown/contemporary), so critical_low requires author < 0.30 which
    can only happen if author_record is None.
    """

    def test_author_at_0_30_no_critical_low(self) -> None:
        """author_standing = 0.30 → critical_low NOT triggered (strict <).

        With author=0.30 and tahqiq=0.35, the critical_low check
        (author < 0.30 AND tahqiq < 0.40) is False because 0.30 < 0.30 is False.
        """
        tier, score, factors, _ = _eval(
            death_date=None,  # author = 0.30
            muhaqiq=None,     # no muhaqiq, unknown date → tahqiq = 0.35
        )
        author_factor = next(f for f in factors if f.name == "author_standing")
        tahqiq_factor = next(f for f in factors if f.name == "tahqiq_quality")
        assert author_factor.score == 0.30
        assert tahqiq_factor.score == 0.35
        # critical_low = 0.30 < 0.30 AND 0.35 < 0.40 = False AND True = False
        # So tier is determined only by score vs 0.65

    def test_no_author_record_critical_low(self) -> None:
        """author_record=None → author_standing=0.30, which is NOT < 0.30.

        This confirms the formula's minimum author score of 0.30 does NOT
        trigger critical_low by itself.
        """
        record = None
        tier, score, factors, _ = evaluate_trust(
            author_ref=_make_ref(),
            author_record=record,
            muhaqiq_name=None,
            publisher=None,
            authority_level=AuthorityLevel.PRIMARY,
            text_fidelity=TextFidelity.HIGH,
            source_id="src_boundary",
            recognized_muhaqiqs=_CONFIG.recognized_muhaqiqs,
            known_publishers=_CONFIG.known_publishers,
        )
        author_factor = next(f for f in factors if f.name == "author_standing")
        assert author_factor.score == 0.30, "None author_record should give 0.30"
        assert tier == TrustTier.FLAGGED, "Score below 0.65 → FLAGGED"
