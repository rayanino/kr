"""Tests for scholar name matching — real Arabic text only.

Tests the three functions copied from eval_harness.py to production.
Uses real scholarly names from the Islamic tradition.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from shared.scholar_authority.src.name_matching import (
    _extract_name_tokens,
    normalize_arabic_name,
    normalized_name_similarity,
)


class TestNormalizeArabicName:
    """Tests for normalize_arabic_name()."""

    def test_strips_diacritics(self) -> None:
        name = "مُحَمَّدُ بْنُ إِدْرِيسَ الشَّافِعِيُّ"
        result = normalize_arabic_name(name)
        # Should not contain any tashkeel
        assert "ُ" not in result
        assert "َ" not in result
        assert "ِ" not in result
        assert "ّ" not in result

    def test_normalizes_hamza(self) -> None:
        result = normalize_arabic_name("أبو إسحاق آل")
        assert "أ" not in result
        assert "إ" not in result
        assert "آ" not in result

    def test_normalizes_taa_marbuta(self) -> None:
        result = normalize_arabic_name("حاشية")
        assert "ة" not in result
        assert "ه" in result

    def test_strips_definite_article(self) -> None:
        result = normalize_arabic_name("النووي")
        assert not result.startswith("ال")

    def test_strips_parenthetical_death_date(self) -> None:
        result = normalize_arabic_name("السيوطي (ت 911هـ)")
        assert "911" not in result
        assert "(" not in result

    def test_collapses_whitespace(self) -> None:
        result = normalize_arabic_name("محمد   بن   أحمد")
        assert "   " not in result


class TestExtractNameTokens:
    """Tests for _extract_name_tokens()."""

    def test_removes_patronymic_particles(self) -> None:
        tokens = _extract_name_tokens("يحيى بن شرف النووي")
        assert "بن" not in tokens
        assert "ابن" not in tokens

    def test_keeps_significant_tokens(self) -> None:
        tokens = _extract_name_tokens("يحيى بن شرف النووي")
        assert "يحيى" in tokens or normalize_arabic_name("يحيى") in {normalize_arabic_name(t) for t in tokens}

    def test_empty_string(self) -> None:
        tokens = _extract_name_tokens("")
        assert tokens == set()


class TestNormalizedNameSimilarity:
    """Tests for normalized_name_similarity()."""

    def test_exact_match_returns_one(self) -> None:
        score = normalized_name_similarity("النووي", "النووي")
        assert score == 1.0

    def test_a3_1_edge_case_short_vs_long(self) -> None:
        """A3-1: النووي vs full nasab chain must score >= 0.85."""
        score = normalized_name_similarity(
            "النووي", "أبو زكريا يحيى بن شرف النووي"
        )
        assert score >= 0.85

    def test_completely_different_scholars(self) -> None:
        score = normalized_name_similarity("البخاري", "ابن تيمية")
        assert score < 0.50

    def test_empty_string_returns_zero(self) -> None:
        assert normalized_name_similarity("", "النووي") == 0.0
        assert normalized_name_similarity("النووي", "") == 0.0

    def test_both_empty_returns_one(self) -> None:
        # Two empty strings are equal after normalization ("" == ""), so the
        # function returns 1.0 (exact-match path fires before the empty-guard).
        # Validated against eval_harness.py reference implementation.
        assert normalized_name_similarity("", "") == 1.0

    def test_suyuti_variants(self) -> None:
        """السيوطي vs full name."""
        score = normalized_name_similarity(
            "السيوطي",
            "عبد الرحمن بن أبي بكر جلال الدين السيوطي",
        )
        assert score >= 0.85

    def test_different_scholars_low_score(self) -> None:
        score = normalized_name_similarity(
            "محمد بن إدريس الشافعي",
            "أحمد بن حنبل",
        )
        assert score < 0.50

    def test_same_scholar_different_forms(self) -> None:
        """ابن حجر العسقلاني — short vs medium form."""
        score = normalized_name_similarity(
            "ابن حجر",
            "أحمد بن علي بن حجر العسقلاني",
        )
        # "حجر" is shared, should get at least a partial match
        assert score > 0.0

    def test_diacritics_do_not_affect_matching(self) -> None:
        """Same name with and without diacritics should match."""
        score = normalized_name_similarity(
            "مُحَمَّد بن إدريس الشافعي",
            "محمد بن إدريس الشافعي",
        )
        assert score >= 0.85


class TestScholarAuthorityLookup:
    """Integration tests: lookup with the production scholar_authority module."""

    def test_lookup_exact_match(self, tmp_path: Path) -> None:
        from engines.source.contracts import ScholarAuthorityRecord
        from shared.scholar_authority.src import lookup, register

        reg_path = tmp_path / "scholars.json"
        record = ScholarAuthorityRecord(
            canonical_id="", canonical_name_ar="النووي",
            death_date_hijri=676, last_updated="2026-01-01T00:00:00+00:00",
        )
        register(record, registry_path=reg_path)
        result = lookup("النووي", death_date_hijri=676, registry_path=reg_path)
        assert result.found
        assert result.record is not None
        assert result.record.death_date_hijri == 676

    def test_lookup_token_similarity(self, tmp_path: Path) -> None:
        from engines.source.contracts import ScholarAuthorityRecord
        from shared.scholar_authority.src import lookup, register

        reg_path = tmp_path / "scholars.json"
        record = ScholarAuthorityRecord(
            canonical_id="", canonical_name_ar="أبو زكريا يحيى بن شرف النووي",
            death_date_hijri=676, last_updated="2026-01-01T00:00:00+00:00",
        )
        register(record, registry_path=reg_path)
        result = lookup("النووي", death_date_hijri=676, registry_path=reg_path)
        assert result.found

    def test_lookup_no_match(self, tmp_path: Path) -> None:
        from shared.scholar_authority.src import lookup

        reg_path = tmp_path / "scholars.json"
        result = lookup("البخاري", registry_path=reg_path)
        assert not result.found
        assert result.action == "new_record"

    def test_lookup_with_death_date(self, tmp_path: Path) -> None:
        from engines.source.contracts import ScholarAuthorityRecord
        from shared.scholar_authority.src import lookup, register

        reg_path = tmp_path / "scholars.json"
        record = ScholarAuthorityRecord(
            canonical_id="", canonical_name_ar="النووي",
            death_date_hijri=676, last_updated="2026-01-01T00:00:00+00:00",
        )
        register(record, registry_path=reg_path)
        result = lookup("النووي", death_date_hijri=676, registry_path=reg_path)
        assert result.found
        assert result.match_score >= 0.85
