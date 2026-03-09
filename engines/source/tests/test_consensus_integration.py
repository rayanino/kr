"""Tests for source engine consensus integration — SPEC §6 rules.

Tests use real Arabic scholarly names from the Islamic tradition.
"""

from __future__ import annotations

from typing import Optional

import pytest

from engines.source.src.consensus import (
    check_work_agreement,
    compare_attribution_status,
    make_author_agreement_fn,
    select_canonical_result,
)
from engines.source.src.inference_models import (
    AuthorIdentificationOutput,
    GenreChainOutput,
    InferenceOutput,
)
from shared.consensus.src.consensus import ModelResponse


def _make_inference(
    author_name: str = "النووي",
    death_date: Optional[int] = 676,
    confidence: float = 0.90,
    genre: str = "sharh",
    attribution_status: str = "definitive",
    genre_chain: Optional[GenreChainOutput] = None,
) -> InferenceOutput:
    """Helper to build InferenceOutput for testing."""
    return InferenceOutput(
        genre=genre,
        genre_confidence=0.90,
        genre_chain=genre_chain,
        structural_format="prose",
        structural_format_confidence=0.90,
        is_multi_layer=False,
        multi_layer_confidence=0.90,
        science_scope=["fiqh"],
        science_scope_confidence=0.90,
        authority_level="primary",
        authority_level_confidence=0.90,
        author_identification=AuthorIdentificationOutput(
            canonical_name_ar=author_name,
            death_date_hijri=death_date,
        ),
        author_identification_confidence=confidence,
        attribution_status=attribution_status,
    )


class TestAuthorAgreement:
    """Tests for make_author_agreement_fn() — SPEC §6.1."""

    def test_both_match_same_existing_record(self) -> None:
        """Case A: Both models match the same scholar record."""
        registry = {"النووي": {"canonical_id": "sch_00042"}}
        fn = make_author_agreement_fn(lambda name: registry.get(name) or next(
            (v for k, v in registry.items() if k in name or name in k), None
        ))
        resp_a = _make_inference(author_name="النووي")
        resp_b = _make_inference(author_name="النووي")
        assert fn(resp_a, resp_b) is True

    def test_both_new_similar_names(self) -> None:
        """Case B: Both new, similar names → agree."""
        fn = make_author_agreement_fn(lambda name: None)  # No matches
        resp_a = _make_inference(author_name="جلال الدين السيوطي", death_date=911)
        resp_b = _make_inference(
            author_name="عبد الرحمن بن أبي بكر جلال الدين السيوطي",
            death_date=911,
        )
        assert fn(resp_a, resp_b) is True

    def test_both_new_different_names(self) -> None:
        """Case B: Both new, different names → disagree."""
        fn = make_author_agreement_fn(lambda name: None)
        resp_a = _make_inference(author_name="البخاري", death_date=256)
        resp_b = _make_inference(author_name="ابن تيمية", death_date=728)
        assert fn(resp_a, resp_b) is False

    def test_one_match_one_new(self) -> None:
        """One matches existing, other says new → disagree."""
        registry = {"النووي": {"canonical_id": "sch_00042"}}
        fn = make_author_agreement_fn(lambda name: registry.get(name))
        resp_a = _make_inference(author_name="النووي")
        resp_b = _make_inference(author_name="البخاري")
        assert fn(resp_a, resp_b) is False

    def test_both_new_death_dates_differ_gt_10(self) -> None:
        """Both new, but death dates differ > 10 years → disagree."""
        fn = make_author_agreement_fn(lambda name: None)
        resp_a = _make_inference(author_name="السيوطي", death_date=911)
        resp_b = _make_inference(author_name="السيوطي", death_date=850)
        assert fn(resp_a, resp_b) is False

    def test_both_new_death_dates_within_10(self) -> None:
        """Both new, death dates within ±10 → agree."""
        fn = make_author_agreement_fn(lambda name: None)
        resp_a = _make_inference(author_name="السيوطي", death_date=911)
        resp_b = _make_inference(author_name="السيوطي", death_date=915)
        assert fn(resp_a, resp_b) is True

    def test_both_new_one_death_none(self) -> None:
        """Both new, one death date None → still agree if names match."""
        fn = make_author_agreement_fn(lambda name: None)
        resp_a = _make_inference(author_name="السيوطي", death_date=911)
        resp_b = _make_inference(author_name="السيوطي", death_date=None)
        assert fn(resp_a, resp_b) is True


class TestWorkAgreement:
    """Tests for check_work_agreement() — SPEC §6.2."""

    def test_both_no_genre_chain(self) -> None:
        """Both None → agree (independent works)."""
        resp_a = _make_inference(genre_chain=None)
        resp_b = _make_inference(genre_chain=None)
        agreed, trigger = check_work_agreement(resp_a, resp_b)
        assert agreed is True
        assert trigger is None

    def test_one_has_chain_other_doesnt(self) -> None:
        """One has chain, other doesn't → disagree."""
        chain = GenreChainOutput(
            relation_type="sharh_of",
            base_work_title="جمع الجوامع",
            base_work_author="ابن السبكي",
        )
        resp_a = _make_inference(genre_chain=chain)
        resp_b = _make_inference(genre_chain=None)
        agreed, trigger = check_work_agreement(resp_a, resp_b)
        assert agreed is False
        assert trigger == "work_match_uncertain"

    def test_both_have_matching_chains(self) -> None:
        """Both have chains with matching title and author → agree."""
        chain_a = GenreChainOutput(
            relation_type="sharh_of",
            base_work_title="جمع الجوامع",
            base_work_author="ابن السبكي",
        )
        chain_b = GenreChainOutput(
            relation_type="sharh_of",
            base_work_title="جمع الجوامع",
            base_work_author="تاج الدين ابن السبكي",
        )
        resp_a = _make_inference(genre_chain=chain_a)
        resp_b = _make_inference(genre_chain=chain_b)
        agreed, trigger = check_work_agreement(resp_a, resp_b)
        assert agreed is True

    def test_both_have_different_chains(self) -> None:
        """Both have chains but different base works → disagree."""
        chain_a = GenreChainOutput(
            relation_type="sharh_of",
            base_work_title="ألفية ابن مالك",
            base_work_author="ابن مالك",
        )
        chain_b = GenreChainOutput(
            relation_type="sharh_of",
            base_work_title="قطر الندى",
            base_work_author="ابن هشام",
        )
        resp_a = _make_inference(genre_chain=chain_a)
        resp_b = _make_inference(genre_chain=chain_b)
        agreed, trigger = check_work_agreement(resp_a, resp_b)
        assert agreed is False


class TestAttributionStatus:
    """Tests for compare_attribution_status() — SPEC §6.3."""

    def test_both_agree_definitive(self) -> None:
        status, gate = compare_attribution_status("definitive", "definitive")
        assert status == "definitive"
        assert gate is False

    def test_both_agree_disputed(self) -> None:
        status, gate = compare_attribution_status("disputed", "disputed")
        assert status == "disputed"
        assert gate is False

    def test_traditional_vs_definitive_no_gate(self) -> None:
        status, gate = compare_attribution_status("traditional", "definitive")
        assert status == "traditional"
        assert gate is False

    def test_disputed_vs_definitive_gate(self) -> None:
        """Disputed vs definitive → conservative wins, triggers gate."""
        status, gate = compare_attribution_status("disputed", "definitive")
        assert status == "disputed"
        assert gate is True

    def test_unknown_vs_traditional_gate(self) -> None:
        """Unknown vs traditional → conservative wins, triggers gate."""
        status, gate = compare_attribution_status("unknown", "traditional")
        assert status == "unknown"
        assert gate is True

    def test_unknown_vs_definitive_gate(self) -> None:
        status, gate = compare_attribution_status("unknown", "definitive")
        assert status == "unknown"
        assert gate is True

    def test_disputed_vs_traditional_gate(self) -> None:
        status, gate = compare_attribution_status("disputed", "traditional")
        assert status == "disputed"
        assert gate is True

    def test_symmetric_order(self) -> None:
        """Result is same regardless of argument order."""
        s1, g1 = compare_attribution_status("disputed", "definitive")
        s2, g2 = compare_attribution_status("definitive", "disputed")
        assert s1 == s2 == "disputed"
        assert g1 == g2 is True


class TestSelectCanonical:
    """Tests for select_canonical_result()."""

    def test_higher_confidence_wins(self) -> None:
        resp_a = ModelResponse(
            "model_a", "openrouter",
            _make_inference(confidence=0.95), {}, True,
        )
        resp_b = ModelResponse(
            "model_b", "anthropic",
            _make_inference(confidence=0.85), {}, True,
        )
        result = select_canonical_result([resp_a, resp_b])
        assert result.author_identification_confidence == 0.95

    def test_tie_prefers_model_b(self) -> None:
        resp_a = ModelResponse(
            "model_a", "openrouter",
            _make_inference(author_name="النووي", confidence=0.90), {}, True,
        )
        resp_b = ModelResponse(
            "model_b", "anthropic",
            _make_inference(author_name="السيوطي", confidence=0.90), {}, True,
        )
        result = select_canonical_result([resp_a, resp_b])
        # Model B wins on tie
        assert result.author_identification.canonical_name_ar == "السيوطي"

    def test_single_response(self) -> None:
        resp = ModelResponse(
            "model_b", "anthropic",
            _make_inference(confidence=0.88), {}, True,
        )
        result = select_canonical_result([resp])
        assert result.author_identification_confidence == 0.88
