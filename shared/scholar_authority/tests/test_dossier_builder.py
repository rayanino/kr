"""Unit tests for the engine-agnostic DossierContext builder (Phase 5 Session 5).

Per ``.claude/rules/testing.md``:
  - Real Arabic text from fixtures, never transliteration
  - Arrange-Act-Assert structure
  - Edge cases: empty input, missing fields, deduplication, non-zero year
"""

from __future__ import annotations

import pytest

from shared.scholar_authority.src.dossier_builder import (
    build_dossier_context,
    hijri_century_of_year,
)


# ---------------------------------------------------------------------------
# hijri_century_of_year — formula correctness across the calendar
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "year,expected_century",
    [
        (1, 1),  # earliest year — first century
        (50, 1),  # mid 1st century
        (100, 1),  # boundary — last year of 1st century
        (101, 2),  # boundary — first year of 2nd century
        (200, 2),  # boundary — last year of 2nd century
        (256, 3),  # al-Bukhārī death year
        (728, 8),  # Ibn Taymiyya al-Ḥarrānī
        (852, 9),  # Ibn Ḥajar al-ʿAsqalānī
        (974, 10),  # Ibn Ḥajar al-Haytamī
        (1000, 10),  # boundary — last year of 10th century
        (1001, 11),  # boundary — first year of 11th century
        (1450, 15),  # contemporary
    ],
)
def test_hijri_century_of_year_formula(year: int, expected_century: int) -> None:
    """Hijri century formula: ``((year - 1) // 100) + 1`` matches scholarly convention."""
    assert hijri_century_of_year(year) == expected_century


def test_hijri_century_of_year_zero_returns_zero() -> None:
    """Year 0 (sentinel for unknown) returns century 0; will not align registry records."""
    assert hijri_century_of_year(0) == 0


def test_hijri_century_of_year_negative_raises() -> None:
    """Negative year is invalid — fail loud per Critical Rule 4."""
    with pytest.raises(ValueError, match="must be >= 0"):
        hijri_century_of_year(-1)


# ---------------------------------------------------------------------------
# build_dossier_context — primitive-input mapping
# ---------------------------------------------------------------------------


def test_build_dossier_context_full_inputs_populates_all_fields() -> None:
    """All-input case: every DossierContext field is populated and types are correct."""
    ctx = build_dossier_context(
        genre="matn",
        primary_science="hadith",
        death_year_hijri=256,
        school_affiliation_hints={"hadith": "shafii"},
        title_strings=["الجامع الصحيح", "صحيح البخاري"],
        geographic_origin="بخارى",
        geographic_active=["نيسابور", "بخارى"],
    )
    assert ctx.genre == "matn"
    assert ctx.primary_science == "hadith"
    assert ctx.century_active_hijri_estimates == [3]
    assert ctx.school_affiliation_hints == {"hadith": "shafii"}
    assert ctx.attributed_works == ["الجامع الصحيح", "صحيح البخاري"]
    # geographic_origin prepended, then geographic_active deduped
    assert ctx.geographic_signals == ["بخارى", "نيسابور"]
    assert ctx.work_title_extracts == ["الجامع الصحيح", "صحيح البخاري"]


def test_build_dossier_context_empty_inputs_returns_empty_dossier() -> None:
    """Empty-input case: every list/dict default-empty per CON-SRC-0009 spec."""
    ctx = build_dossier_context()
    assert ctx.genre is None
    assert ctx.primary_science is None
    assert ctx.century_active_hijri_estimates == []
    assert ctx.school_affiliation_hints == {}
    assert ctx.attributed_works == []
    assert ctx.geographic_signals == []
    assert ctx.work_title_extracts == []


def test_build_dossier_context_dedupe_preserves_first_occurrence_order() -> None:
    """Title dedupe preserves order of first occurrence — D-023 audit-stability spirit."""
    ctx = build_dossier_context(
        title_strings=[
            "صحيح البخاري",
            "الجامع الصحيح",
            "صحيح البخاري",  # duplicate — should be dropped
            "التاريخ الكبير",
        ],
    )
    assert ctx.attributed_works == ["صحيح البخاري", "الجامع الصحيح", "التاريخ الكبير"]


def test_build_dossier_context_dedupe_drops_empty_and_whitespace_strings() -> None:
    """Empty + whitespace strings carry no signal and would pollute alignment scoring."""
    ctx = build_dossier_context(
        title_strings=["", "  ", "صحيح البخاري", "\t\n"],
    )
    assert ctx.attributed_works == ["صحيح البخاري"]


def test_build_dossier_context_geographic_origin_dedupes_with_active() -> None:
    """When geographic_origin appears in geographic_active, dedupe to one entry."""
    ctx = build_dossier_context(
        geographic_origin="دمشق",
        geographic_active=["دمشق", "القاهرة"],
    )
    # geographic_origin prepended, then geographic_active; دمشق already in
    assert ctx.geographic_signals == ["دمشق", "القاهرة"]


def test_build_dossier_context_only_origin_no_active_returns_origin_only() -> None:
    """Origin without active list returns single-element geographic_signals."""
    ctx = build_dossier_context(geographic_origin="فاس")
    assert ctx.geographic_signals == ["فاس"]


def test_build_dossier_context_only_active_no_origin_returns_active_dedup() -> None:
    """Active list without origin returns deduplicated active list."""
    ctx = build_dossier_context(
        geographic_active=["بغداد", "البصرة", "بغداد"],
    )
    assert ctx.geographic_signals == ["بغداد", "البصرة"]


def test_build_dossier_context_work_title_extracts_default_to_attributed_works() -> None:
    """When work_title_extracts is None, defaults to attributed_works copy."""
    ctx = build_dossier_context(
        title_strings=["شرح صحيح مسلم"],
    )
    assert ctx.attributed_works == ["شرح صحيح مسلم"]
    assert ctx.work_title_extracts == ["شرح صحيح مسلم"]


def test_build_dossier_context_work_title_extracts_explicit_override() -> None:
    """Explicit work_title_extracts overrides the default attributed_works copy."""
    ctx = build_dossier_context(
        title_strings=["المنهاج"],
        work_title_extracts=["شرح صحيح مسلم", "المنهاج في علوم الحديث"],
    )
    assert ctx.attributed_works == ["المنهاج"]
    assert ctx.work_title_extracts == ["شرح صحيح مسلم", "المنهاج في علوم الحديث"]


def test_build_dossier_context_only_death_year_provides_century_estimate() -> None:
    """death_year_hijri alone produces a single-element century_active_hijri_estimates."""
    # Ibn Taymiyya al-Ḥarrānī died 728 → century 8
    ctx = build_dossier_context(death_year_hijri=728)
    assert ctx.century_active_hijri_estimates == [8]


def test_build_dossier_context_no_death_year_leaves_century_empty() -> None:
    """No death_year → empty century_active_hijri_estimates per CON-SRC-0009 default."""
    ctx = build_dossier_context(genre="sharh")
    assert ctx.century_active_hijri_estimates == []


def test_build_dossier_context_returns_frozen_dossier() -> None:
    """DossierContext.model_config.frozen=True — mutation must raise."""
    ctx = build_dossier_context(genre="risalah")
    with pytest.raises((ValueError, TypeError)):  # pydantic raises ValidationError on frozen
        ctx.genre = "matn"  # type: ignore[misc]
