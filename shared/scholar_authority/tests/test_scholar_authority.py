"""Tests for scholar authority registry — SPEC §4.A.5.

Tests 1–20 from session5-test-plan.md.
All tests use real Arabic scholarly names.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engines.source.contracts import ScholarAuthorityRecord
from shared.scholar_authority.src.scholar_authority import (
    ScholarMatchResult,
    ScholarUpdateResult,
    compute_scholar_match_score,
    get_all,
    lookup,
    register,
    update,
    _compute_record_completeness,
)


def _make_record(**kwargs: object) -> ScholarAuthorityRecord:
    """Helper to create a ScholarAuthorityRecord with sensible defaults."""
    defaults = {
        "canonical_id": "",
        "canonical_name_ar": "النووي",
        "last_updated": "2026-01-01T00:00:00+00:00",
    }
    defaults.update(kwargs)
    return ScholarAuthorityRecord(**defaults)


class TestLookup:
    """Tests 1–8: Scholar lookup and matching."""

    def test_01_exact_canonical_match(self, tmp_path: Path) -> None:
        """Test 1: Exact canonical name match → auto_link, score 1.0."""
        reg = tmp_path / "scholars.json"
        register(_make_record(
            canonical_name_ar="أبو زكريا يحيى بن شرف النووي",
            death_date_hijri=676,
        ), registry_path=reg)

        result = lookup(
            "أبو زكريا يحيى بن شرف النووي",
            death_date_hijri=676,
            registry_path=reg,
        )
        assert result.action == "auto_link"
        assert result.match_score >= 0.95

    def test_02_known_as_match(self, tmp_path: Path) -> None:
        """Test 2: Match via known_as variant."""
        reg = tmp_path / "scholars.json"
        register(_make_record(
            canonical_name_ar="أبو زكريا يحيى بن شرف النووي",
            known_as=["النووي", "محيي الدين النووي"],
            death_date_hijri=676,
        ), registry_path=reg)

        result = lookup("محيي الدين النووي", death_date_hijri=676, registry_path=reg)
        assert result.found
        assert result.match_score >= 0.85

    def test_03_name_variants_match(self, tmp_path: Path) -> None:
        """Test 3: Match via name_variants."""
        reg = tmp_path / "scholars.json"
        register(_make_record(
            canonical_name_ar="أبو زكريا يحيى بن شرف النووي",
            name_variants=["يحيى بن شرف"],
            death_date_hijri=676,
        ), registry_path=reg)

        result = lookup("يحيى بن شرف", death_date_hijri=676, registry_path=reg)
        assert result.found

    def test_04_short_vs_long_name_with_date(self, tmp_path: Path) -> None:
        """Test 4 (A3-1): Short name + death date → auto_link."""
        reg = tmp_path / "scholars.json"
        register(_make_record(
            canonical_name_ar="أبو زكريا يحيى بن شرف النووي",
            death_date_hijri=676,
        ), registry_path=reg)

        result = lookup("النووي", death_date_hijri=676, registry_path=reg)
        assert result.action == "auto_link"
        assert result.match_score >= 0.85

    def test_05_ambiguous_name_human_gate(self, tmp_path: Path) -> None:
        """Test 5: Ambiguous 'ابن حجر' without death date → human_gate zone."""
        reg = tmp_path / "scholars.json"
        register(_make_record(
            canonical_name_ar="أحمد بن علي بن حجر العسقلاني",
            death_date_hijri=852,
        ), registry_path=reg)

        # Name only — capped at 0.65, so human_gate zone
        result = lookup("ابن حجر", registry_path=reg)
        assert result.action == "human_gate"
        assert 0.50 <= result.match_score <= 0.65

    def test_06_disambiguated_by_death_date(self, tmp_path: Path) -> None:
        """Test 6: Same name + correct death date → auto_link."""
        reg = tmp_path / "scholars.json"
        register(_make_record(
            canonical_name_ar="أحمد بن علي بن حجر العسقلاني",
            death_date_hijri=852,
        ), registry_path=reg)

        result = lookup("ابن حجر", death_date_hijri=852, registry_path=reg)
        assert result.action == "auto_link"

    def test_07_no_match_low_score(self, tmp_path: Path) -> None:
        """Test 7: Completely different scholar → new_record."""
        reg = tmp_path / "scholars.json"
        register(_make_record(
            canonical_name_ar="النووي",
            death_date_hijri=676,
        ), registry_path=reg)

        result = lookup("ابن تيمية", death_date_hijri=728, registry_path=reg)
        assert result.action == "new_record"
        assert result.match_score < 0.50

    def test_08_empty_registry(self, tmp_path: Path) -> None:
        """Test 8: Empty registry → new_record."""
        reg = tmp_path / "scholars.json"
        result = lookup("البخاري", registry_path=reg)
        assert result.action == "new_record"
        assert result.match_score == 0.0


class TestRegister:
    """Tests 9–12: Scholar registration."""

    def test_09_sequential_ids(self, tmp_path: Path) -> None:
        """Test 9: Sequential ID assignment."""
        reg = tmp_path / "scholars.json"
        r1 = register(_make_record(canonical_name_ar="النووي"), registry_path=reg)
        r2 = register(_make_record(canonical_name_ar="البخاري"), registry_path=reg)

        assert r1.canonical_id == "sch_00001"
        assert r2.canonical_id == "sch_00002"

    def test_10_validates_required_fields(self) -> None:
        """Test 10: Empty canonical_name_ar raises."""
        with pytest.raises(ValueError, match="canonical_name_ar"):
            register(_make_record(canonical_name_ar=""))

    def test_11_required_canonical_name(self) -> None:
        """Test 11: Whitespace-only canonical_name_ar raises."""
        with pytest.raises(ValueError, match="canonical_name_ar"):
            register(_make_record(canonical_name_ar="   "))

    def test_12_appends_sources_encountered(self, tmp_path: Path) -> None:
        """Test 12: source_id appended to sources_encountered_in."""
        reg = tmp_path / "scholars.json"
        record = _make_record(
            canonical_name_ar="النووي",
            sources_encountered_in=["src_abc12345"],
        )
        result = register(record, registry_path=reg)
        assert "src_abc12345" in result.sources_encountered_in


class TestUpdate:
    """Tests 13–19: Scholar update with consistency checks."""

    def _setup_nawawi(self, tmp_path: Path) -> tuple[Path, str]:
        """Register al-Nawawi and return (registry_path, canonical_id)."""
        reg = tmp_path / "scholars.json"
        result = register(_make_record(
            canonical_name_ar="النووي",
            death_date_hijri=676,
            school_affiliations={"fiqh": "شافعي"},
        ), registry_path=reg)
        return reg, result.canonical_id

    def test_13_death_date_drift_gates(self, tmp_path: Path) -> None:
        """Test 13: Death date drift > 5 years triggers gate conflict."""
        reg, cid = self._setup_nawawi(tmp_path)

        result = update(
            cid, {"death_date_hijri": 690}, "src_test", registry_path=reg,
        )
        assert result.applied  # Gate conflicts still apply the update
        assert len(result.conflicts) == 1
        assert result.conflicts[0].check_name == "death_date_drift"
        assert result.conflicts[0].severity == "gate"

    def test_14_death_date_small_drift_ok(self, tmp_path: Path) -> None:
        """Test 14: Death date drift <= 5 years is OK."""
        reg, cid = self._setup_nawawi(tmp_path)

        result = update(
            cid, {"death_date_hijri": 680}, "src_test", registry_path=reg,
        )
        assert result.applied
        assert len(result.conflicts) == 0

    def test_15_school_change_gates(self, tmp_path: Path) -> None:
        """Test 15: School affiliation change triggers gate."""
        reg, cid = self._setup_nawawi(tmp_path)

        result = update(
            cid,
            {"school_affiliations": {"fiqh": "حنبلي"}},
            "src_test",
            registry_path=reg,
        )
        assert result.applied
        assert any(c.check_name == "school_affiliation_change" for c in result.conflicts)

    def test_16_name_change_blocked(self, tmp_path: Path) -> None:
        """Test 16: canonical_name_ar change is BLOCKED."""
        reg, cid = self._setup_nawawi(tmp_path)

        result = update(
            cid,
            {"canonical_name_ar": "الإمام النووي"},
            "src_test",
            registry_path=reg,
        )
        assert not result.applied
        assert any(c.check_name == "name_change_blocked" for c in result.conflicts)

    def test_17_self_reference_rejected(self, tmp_path: Path) -> None:
        """Test 17: Scholar as own teacher → blocked."""
        reg, cid = self._setup_nawawi(tmp_path)

        result = update(
            cid, {"teachers": [cid]}, "src_test", registry_path=reg,
        )
        assert not result.applied
        assert any(c.check_name == "self_reference" for c in result.conflicts)

    def test_18_temporal_inconsistency(self, tmp_path: Path) -> None:
        """Test 18: Teacher died > 30 years after student → gate."""
        reg = tmp_path / "scholars.json"
        student = register(_make_record(
            canonical_name_ar="الطالب",
            death_date_hijri=400,
        ), registry_path=reg)
        teacher = register(_make_record(
            canonical_name_ar="الشيخ",
            death_date_hijri=450,
        ), registry_path=reg)

        result = update(
            student.canonical_id,
            {"teachers": [teacher.canonical_id]},
            "src_test",
            registry_path=reg,
        )
        assert result.applied
        assert any(c.check_name == "temporal_inconsistency" for c in result.conflicts)

    def test_19_revision_history_preserved(self, tmp_path: Path) -> None:
        """Test 19: Old values saved in revision_history."""
        reg, cid = self._setup_nawawi(tmp_path)

        result = update(
            cid,
            {"scholarly_standing": "Major Shafi'i authority"},
            "src_enrichment",
            registry_path=reg,
        )
        assert result.applied
        assert len(result.record.revision_history) >= 1
        entry = result.record.revision_history[-1]
        assert entry.field == "scholarly_standing"
        assert entry.old_value is None
        assert '"Major Shafi\'i authority"' in entry.new_value


class TestRecordCompleteness:
    """Test 20: Record completeness calculation."""

    def test_20_completeness_fraction(self) -> None:
        """Test 20: record_completeness correctly computed (24-field fraction)."""
        record = _make_record(
            canonical_name_ar="النووي",
            death_date_hijri=676,
        )
        completeness = _compute_record_completeness(record)
        # canonical_name_ar + death_date_hijri + death_date_approximate (bool always counts) = 3/24
        assert completeness == pytest.approx(3 / 24, abs=0.01)

    def test_completeness_empty_lists_not_counted(self) -> None:
        """Empty list fields don't count toward completeness."""
        record = _make_record(
            canonical_name_ar="النووي",
            known_as=[],
            name_variants=[],
        )
        completeness = _compute_record_completeness(record)
        # canonical_name_ar + death_date_approximate (bool) = 2/24
        assert completeness == pytest.approx(2 / 24, abs=0.01)

    def test_completeness_filled_lists_counted(self) -> None:
        """Non-empty list fields count toward completeness."""
        record = _make_record(
            canonical_name_ar="النووي",
            known_as=["محيي الدين"],
            nisba=["النووي"],
            death_date_hijri=676,
            school_affiliations={"fiqh": "شافعي"},
        )
        completeness = _compute_record_completeness(record)
        # canonical_name_ar + known_as + nisba + death_date_hijri + school_affiliations + death_date_approximate = 6/24
        assert completeness == pytest.approx(6 / 24, abs=0.01)


class TestNameOnlyCap:
    """Verify the 0.65 name-only score cap."""

    def test_name_only_capped_at_065(self) -> None:
        """Name-only match capped at 0.65 — below auto_link threshold."""
        record = _make_record(
            canonical_name_ar="النووي",
        )
        score = compute_scholar_match_score(
            "النووي", None, None, None, record
        )
        assert score <= 0.65

    def test_name_plus_date_not_capped(self) -> None:
        """Name + death date is NOT capped — can reach auto_link."""
        record = _make_record(
            canonical_name_ar="النووي",
            death_date_hijri=676,
        )
        score = compute_scholar_match_score(
            "النووي", 676, None, None, record
        )
        assert score >= 0.85
