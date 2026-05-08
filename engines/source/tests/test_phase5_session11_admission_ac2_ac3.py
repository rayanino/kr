"""REQ-SRC-0043 AC-2 + AC-3 deterministic tests — Phase 5 Session 11 (2026-05-08).

Covers the consumer extension at ``engines/source/src/scholar_admission.py:
register_provisional_scholars`` for the second and third REQ-SRC-0043
acceptance criteria:

  - **AC-2 (integration)**: a second book by the same provisional scholar
    arrives with consistent evidence (same display_name, same death_hijri
    or both null) AND the combined evidence across the two sources
    satisfies INV-SRC-0013 ≥2-non-name floor → existing entry is promoted
    to ``status=confirmed``, ``source_book_ids`` is extended, and
    ``authority_level`` is re-evaluated from ``UNKNOWN``.
  - **AC-2 floor-not-met fallback**: same display_name + death_hijri match
    but combined evidence falls short of the ≥2-non-name floor → the
    second source creates a separate ``status=provisional`` entry with
    cross-disambiguation referencing the existing entry. Conservative
    semantics per "library never refuses knowledge".
  - **AC-3 (deterministic)**: a new scholar with display_name matching an
    existing entry but ``death_hijri`` differs by >0 years (or one is null
    and the other populated) → separate entry with own ``canonical_id``;
    both entries get ``disambiguation_notes`` referencing the other.
    AC-3 takes priority over AC-2 because divergent death_hijri defeats
    the AC-2 precondition.

Real Arabic fixtures throughout — no transliteration, no synthetic
placeholder text. The AC-3 fixture uses the SPEC's canonical Ibn Taymiyya
example (death_hijri=728 vs 652, divergence=76 years). The AC-2 fixture
uses عبد الرحمن بن ناصر السعدي (death_hijri=1376) — a contemporary
Saudi tafsir scholar deliberately outside the 50-scholar gold seed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engines.source.contracts import (
    AuthorityLevel,
    ProvisionalScholarRegistration,
    ScholarAuthorityRecord,
)
from engines.source.src.scholar_admission import (
    ProvisionalRegistrationOutcome,
    _append_disambiguation_note,
    _century_from_death_hijri,
    _count_combined_non_name_attributes,
    _describe_near_collision_reason,
    _format_disambiguation_note,
    _lookup_existing_match,
    _re_evaluate_authority_level_after_promotion,
    register_provisional_scholars,
)


# ──────────────────────────────────────────────────────────────────
# Fixtures: real Arabic scholars
# ──────────────────────────────────────────────────────────────────


def _saadi_book_one() -> ProvisionalScholarRegistration:
    """First book attributed to عبد الرحمن السعدي — primary AC-2 fixture."""
    return ProvisionalScholarRegistration(
        position_index=0,
        display_name="عبد الرحمن بن ناصر السعدي",
        full_name_lineage="عبد الرحمن بن ناصر بن عبد الله السعدي",
        death_hijri=1376,
        nisba_tokens=["السعدي"],
        primary_science="tafsir",
        evidence=["metadata_card", "title_page"],
        source_book_id="src_taysir_al_karim",
        triggering_match_result_id="smr_saadi_001",
    )


def _saadi_book_two() -> ProvisionalScholarRegistration:
    """Second book attributed to the same scholar — triggers AC-2 promotion."""
    return ProvisionalScholarRegistration(
        position_index=0,
        display_name="عبد الرحمن بن ناصر السعدي",
        full_name_lineage="عبد الرحمن بن ناصر بن عبد الله السعدي",
        death_hijri=1376,  # same → century 14 corroborates
        nisba_tokens=["السعدي"],
        primary_science="tafsir",  # same → corroborates
        evidence=["colophon"],
        source_book_id="src_qawaid_hisan",
        triggering_match_result_id="smr_saadi_002",
    )


def _saadi_book_two_floor_not_met() -> ProvisionalScholarRegistration:
    """Second book with display_name + death_hijri match but DIFFERENT primary_science.

    Combined corroboration: century only (1) → floor not met → fallback
    to separate entry with cross-disambiguation.
    """
    return ProvisionalScholarRegistration(
        position_index=0,
        display_name="عبد الرحمن بن ناصر السعدي",
        full_name_lineage="عبد الرحمن بن ناصر بن عبد الله السعدي",
        death_hijri=1376,
        nisba_tokens=["السعدي"],
        primary_science="hadith",  # diverges from book one's tafsir
        evidence=["colophon"],
        source_book_id="src_other_saadi_book",
        triggering_match_result_id="smr_saadi_floor_not_met",
    )


def _ibn_taymiyya_classical() -> ProvisionalScholarRegistration:
    """Classical Hanbali ابن تيمية, death_hijri=728. AC-3 baseline fixture."""
    return ProvisionalScholarRegistration(
        position_index=0,
        display_name="ابن تيمية",
        full_name_lineage="أحمد بن عبد الحليم بن تيمية الحراني",
        death_hijri=728,
        nisba_tokens=["الحراني"],
        primary_science="aqidah",
        evidence=["title_page"],
        source_book_id="src_majmu_fatawa",
        triggering_match_result_id="smr_ibn_taymiyya_classical",
    )


def _ibn_taymiyya_grandfather() -> ProvisionalScholarRegistration:
    """Different ابن تيمية — Majd al-Din the grandfather, death_hijri=652.

    Per REQ-SRC-0043 AC-3 example: divergence = 76 years → AC-3 fires.
    """
    return ProvisionalScholarRegistration(
        position_index=0,
        display_name="ابن تيمية",
        full_name_lineage="عبد السلام بن عبد الله بن تيمية",
        death_hijri=652,
        nisba_tokens=["الحراني"],
        primary_science="fiqh",
        evidence=["title_page"],
        source_book_id="src_muharrar",
        triggering_match_result_id="smr_ibn_taymiyya_grandfather",
    )


def _scholar_no_death_date() -> ProvisionalScholarRegistration:
    """Living/contemporary scholar without death_hijri."""
    return ProvisionalScholarRegistration(
        position_index=0,
        display_name="سعد بن ناصر الشثري",
        full_name_lineage="سعد بن ناصر بن عبد العزيز الشثري",
        death_hijri=None,
        nisba_tokens=["الشثري"],
        primary_science="fiqh",
        evidence=["metadata_card"],
        source_book_id="src_shathri_first",
        triggering_match_result_id="smr_shathri_001",
    )


def _scholar_namesake_with_death_date() -> ProvisionalScholarRegistration:
    """Same display_name as the contemporary scholar but with a death_hijri.

    Triggers AC-3 null-vs-populated mismatch.
    """
    return ProvisionalScholarRegistration(
        position_index=0,
        display_name="سعد بن ناصر الشثري",
        full_name_lineage="سعد بن ناصر الشثري",
        death_hijri=1200,
        nisba_tokens=["الشثري"],
        primary_science="fiqh",
        evidence=["title_page"],
        source_book_id="src_shathri_classical",
        triggering_match_result_id="smr_shathri_002",
    )


def _isolated_registry_path(tmp_path: Path) -> Path:
    """Build a tmp_path scholars.json so tests do not touch the real registry."""
    registry_dir = tmp_path / "library" / "registries"
    registry_dir.mkdir(parents=True, exist_ok=True)
    return registry_dir / "scholars.json"


# ──────────────────────────────────────────────────────────────────
# Helper-function unit tests
# ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "year,expected_century",
    [
        (1, 1),
        (100, 1),
        (101, 2),
        (200, 2),
        (652, 7),  # Ibn Taymiyya the grandfather
        (728, 8),  # Ibn Taymiyya the famous
        (1376, 14),  # al-Saʿdi
    ],
)
def test_century_from_death_hijri_correct_boundaries(
    year: int, expected_century: int
) -> None:
    """The century computation handles the boundary years 100/101/200 correctly."""
    assert _century_from_death_hijri(year) == expected_century


def test_re_evaluate_authority_level_thresholds() -> None:
    """Heuristic thresholds: 0/1 → UNKNOWN; 2/3 → REFERENCE; ≥4 → PRIMARY."""
    assert _re_evaluate_authority_level_after_promotion(0) == AuthorityLevel.UNKNOWN
    assert _re_evaluate_authority_level_after_promotion(1) == AuthorityLevel.UNKNOWN
    assert _re_evaluate_authority_level_after_promotion(2) == AuthorityLevel.REFERENCE
    assert _re_evaluate_authority_level_after_promotion(3) == AuthorityLevel.REFERENCE
    assert _re_evaluate_authority_level_after_promotion(4) == AuthorityLevel.PRIMARY
    assert _re_evaluate_authority_level_after_promotion(8) == AuthorityLevel.PRIMARY


def test_format_disambiguation_note_uses_iso_date_form() -> None:
    """Note format is ``[YYYY-MM-DD] Distinct from {id} — {reason}``."""
    note = _format_disambiguation_note(
        "sch_00042", reason="display_name match but death_hijri differs by 76 years"
    )
    assert note.startswith("[")
    # Date is 10 chars: YYYY-MM-DD; closing bracket follows immediately
    assert note[11] == "]"
    assert "Distinct from sch_00042" in note
    assert "death_hijri differs by 76 years" in note


def test_append_disambiguation_note_handles_empty_existing() -> None:
    """First note replaces empty/None; subsequent notes accumulate via newline."""
    assert _append_disambiguation_note(None, "first") == "first"
    assert _append_disambiguation_note("", "first") == "first"
    assert _append_disambiguation_note("first", "second") == "first\nsecond"
    assert (
        _append_disambiguation_note("first\nsecond", "third")
        == "first\nsecond\nthird"
    )


# ──────────────────────────────────────────────────────────────────
# Lookup function tests
# ──────────────────────────────────────────────────────────────────


def test_lookup_existing_match_no_match_returns_none(
    tmp_path: Path,
) -> None:
    """An empty registry returns ``("none", None)`` for any registration."""
    match_type, record = _lookup_existing_match({}, _saadi_book_one())
    assert match_type == "none"
    assert record is None


def test_lookup_existing_match_finds_exact_provisional_when_death_dates_equal(
    tmp_path: Path,
) -> None:
    """Display_name match + same death_hijri → exact_provisional path."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars([_saadi_book_one()], registry_path=registry_path)
    from shared.scholar_authority.src.scholar_authority import get_all
    registry = get_all(registry_path=registry_path)

    match_type, record = _lookup_existing_match(registry, _saadi_book_two())
    assert match_type == "exact_provisional"
    assert record is not None
    assert record.canonical_name_ar == "عبد الرحمن بن ناصر السعدي"


def test_lookup_existing_match_returns_near_collision_for_divergent_dates(
    tmp_path: Path,
) -> None:
    """Display_name match + diff > 0 years → near_collision path (AC-3 trigger)."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars(
        [_ibn_taymiyya_classical()], registry_path=registry_path
    )
    from shared.scholar_authority.src.scholar_authority import get_all
    registry = get_all(registry_path=registry_path)

    match_type, record = _lookup_existing_match(
        registry, _ibn_taymiyya_grandfather()
    )
    assert match_type == "near_collision"
    assert record is not None
    assert record.death_date_hijri == 728


def test_lookup_existing_match_handles_both_null_death_dates(
    tmp_path: Path,
) -> None:
    """Display_name match + both death_hijri=None → exact_provisional path."""
    contemporary_first = _scholar_no_death_date()
    contemporary_second = ProvisionalScholarRegistration(
        position_index=0,
        display_name="سعد بن ناصر الشثري",
        full_name_lineage="سعد بن ناصر بن عبد العزيز الشثري",
        death_hijri=None,
        nisba_tokens=["الشثري"],
        primary_science="fiqh",
        evidence=["title_page"],
        source_book_id="src_shathri_second",
        triggering_match_result_id="smr_shathri_003",
    )
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars([contemporary_first], registry_path=registry_path)
    from shared.scholar_authority.src.scholar_authority import get_all
    registry = get_all(registry_path=registry_path)

    match_type, record = _lookup_existing_match(registry, contemporary_second)
    assert match_type == "exact_provisional"
    assert record is not None


def test_lookup_existing_match_routes_null_vs_populated_to_near_collision(
    tmp_path: Path,
) -> None:
    """Display_name match + (null vs populated) death_hijri → near_collision."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars(
        [_scholar_no_death_date()], registry_path=registry_path
    )
    from shared.scholar_authority.src.scholar_authority import get_all
    registry = get_all(registry_path=registry_path)

    match_type, record = _lookup_existing_match(
        registry, _scholar_namesake_with_death_date()
    )
    assert match_type == "near_collision"
    assert record is not None
    assert record.death_date_hijri is None


def test_count_combined_non_name_attributes_counts_century_and_science() -> None:
    """Helper counts the two PSR-reachable INV-SRC-0013 classes."""
    existing = ScholarAuthorityRecord(
        canonical_id="sch_00001",
        canonical_name_ar="عبد الرحمن بن ناصر السعدي",
        status="provisional",
        display_name="عبد الرحمن بن ناصر السعدي",
        full_name_lineage="عبد الرحمن بن ناصر بن عبد الله السعدي",
        birth_date_hijri=None,
        birth_date_ce=None,
        death_date_hijri=1376,
        death_date_ce=None,
        era_century_hijri=None,
        primary_science="tafsir",
        record_completeness=0.0,
        data_provenance_score=0.0,
        last_updated="2026-05-08T00:00:00Z",
    )
    matching = _saadi_book_two()
    # century 14 + primary_science=tafsir both match → count = 2
    assert _count_combined_non_name_attributes(existing, matching) == 2

    # primary_science diverges (hadith vs tafsir) → only century corroborates
    assert (
        _count_combined_non_name_attributes(
            existing, _saadi_book_two_floor_not_met()
        )
        == 1
    )

    # Different century via different death_hijri → only primary_science (if matches)
    diff_century = ProvisionalScholarRegistration(
        position_index=0,
        display_name="عبد الرحمن بن ناصر السعدي",
        full_name_lineage="عبد الرحمن بن ناصر بن عبد الله السعدي",
        death_hijri=1300,  # century 13, not 14
        nisba_tokens=["السعدي"],
        primary_science="tafsir",
        evidence=["colophon"],
        source_book_id="src_diff_century",
        triggering_match_result_id="smr_diff_century",
    )
    assert _count_combined_non_name_attributes(existing, diff_century) == 1


def test_describe_near_collision_reason_renders_specific_diff() -> None:
    """The reason string is human-readable and conveys the exact divergence."""
    existing = ScholarAuthorityRecord(
        canonical_id="sch_00001",
        canonical_name_ar="ابن تيمية",
        status="provisional",
        display_name="ابن تيمية",
        birth_date_hijri=None,
        birth_date_ce=None,
        death_date_hijri=728,
        death_date_ce=None,
        era_century_hijri=None,
        record_completeness=0.0,
        data_provenance_score=0.0,
        last_updated="2026-05-08T00:00:00Z",
    )
    reason = _describe_near_collision_reason(existing, _ibn_taymiyya_grandfather())
    assert "76 years" in reason
    assert "728" in reason
    assert "652" in reason


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0043 AC-2 — happy path (promotion)
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0043", "AC-2")
def test_ac2_second_book_with_consistent_evidence_promotes_to_confirmed(
    tmp_path: Path,
) -> None:
    """REQ-SRC-0043 AC-2: second book by same scholar with consistent
    evidence (same display_name, same death_hijri, same primary_science)
    triggers promotion. ``status`` flips from ``provisional`` to
    ``confirmed``; ``source_book_ids`` extends; ``authority_level`` is
    re-evaluated from ``UNKNOWN`` to ``REFERENCE`` (heuristic: 2
    corroborating non-name attributes)."""
    registry_path = _isolated_registry_path(tmp_path)

    first = register_provisional_scholars(
        [_saadi_book_one()], registry_path=registry_path
    )
    [created] = first.registered
    assert created.status == "provisional"
    assert created.authority_level == AuthorityLevel.UNKNOWN
    assert created.source_book_ids == ["src_taysir_al_karim"]

    # Second book registers — should trigger AC-2 promotion
    second = register_provisional_scholars(
        [_saadi_book_two()], registry_path=registry_path
    )
    assert second.registered == []
    assert len(second.promoted) == 1
    assert second.near_collision_disambiguations == []

    promoted = second.promoted[0]
    assert promoted.canonical_id == created.canonical_id
    assert promoted.status == "confirmed"
    assert promoted.authority_level == AuthorityLevel.REFERENCE
    assert set(promoted.source_book_ids) == {
        "src_taysir_al_karim",
        "src_qawaid_hisan",
    }

    # Persisted state matches the in-memory record
    raw = json.loads(registry_path.read_text(encoding="utf-8"))
    persisted = raw[promoted.canonical_id]
    assert persisted["status"] == "confirmed"
    assert persisted["authority_level"] == "reference"
    assert "src_taysir_al_karim" in persisted["source_book_ids"]
    assert "src_qawaid_hisan" in persisted["source_book_ids"]


@pytest.mark.spec("REQ-SRC-0043", "AC-2")
def test_ac2_promotion_merges_evidence_sources_without_duplicates(
    tmp_path: Path,
) -> None:
    """Promotion merges ``evidence_sources`` from both registrations.

    The two book registrations contribute distinct evidence types
    (book one: metadata_card + title_page; book two: colophon). All
    three should appear on the promoted record bound to their respective
    source_book_id values."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars([_saadi_book_one()], registry_path=registry_path)
    second = register_provisional_scholars(
        [_saadi_book_two()], registry_path=registry_path
    )

    [promoted] = second.promoted
    evidence_book_pairs = {
        (ev.book_id, ev.evidence_type) for ev in promoted.evidence_sources
    }
    assert evidence_book_pairs == {
        ("src_taysir_al_karim", "metadata_card"),
        ("src_taysir_al_karim", "title_page"),
        ("src_qawaid_hisan", "colophon"),
    }


@pytest.mark.spec("REQ-SRC-0043", "AC-2")
def test_ac2_idempotent_re_registration_no_duplicate_book_ids(
    tmp_path: Path,
) -> None:
    """Re-registering the SAME book a second time on a confirmed entry
    does not duplicate ``source_book_ids`` entries.

    Locks the contract that the underlying ``update()`` deduplicates
    list-field merges by Python equality. ``str`` equality is used for
    ``source_book_ids``; ``ScholarEvidenceSource`` field equality is
    used for ``evidence_sources``."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars([_saadi_book_one()], registry_path=registry_path)
    register_provisional_scholars([_saadi_book_two()], registry_path=registry_path)

    # Re-apply book two — should be idempotent
    third = register_provisional_scholars(
        [_saadi_book_two()], registry_path=registry_path
    )
    [promoted] = third.promoted
    assert promoted.status == "confirmed"
    # source_book_ids has exactly 2 entries, no duplicates
    assert len(promoted.source_book_ids) == 2
    assert set(promoted.source_book_ids) == {
        "src_taysir_al_karim",
        "src_qawaid_hisan",
    }
    # evidence_sources has 3 entries, no duplicates
    assert len(promoted.evidence_sources) == 3


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0043 AC-2 — floor-not-met fallback
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0043", "AC-2")
def test_ac2_floor_not_met_creates_separate_provisional_with_disambiguation(
    tmp_path: Path,
) -> None:
    """When display_name + death_hijri match but combined evidence falls
    short of INV-SRC-0013 ≥2-non-name floor, a SEPARATE provisional
    entry is created with cross-disambiguation referencing the existing
    entry. Neither entry is promoted; both keep ``status=provisional``.

    Conservative semantics: weak matches are not silently merged; the
    library accepts the second source per "library never refuses
    knowledge" but keeps it distinct until richer evidence accumulates."""
    registry_path = _isolated_registry_path(tmp_path)
    first = register_provisional_scholars(
        [_saadi_book_one()], registry_path=registry_path
    )
    [original] = first.registered

    second = register_provisional_scholars(
        [_saadi_book_two_floor_not_met()], registry_path=registry_path
    )
    # No promotion — separate registration with disambiguation
    assert second.promoted == []
    assert len(second.registered) == 1
    assert len(second.near_collision_disambiguations) == 1

    [new_record] = second.registered
    [(existing_post, paired_new)] = second.near_collision_disambiguations
    assert paired_new.canonical_id == new_record.canonical_id
    assert existing_post.canonical_id == original.canonical_id

    # Both entries kept at status=provisional
    assert new_record.status == "provisional"
    assert existing_post.status == "provisional"

    # Cross-references applied
    assert new_record.disambiguation_notes is not None
    assert existing_post.disambiguation_notes is not None
    assert original.canonical_id in new_record.disambiguation_notes
    assert new_record.canonical_id in existing_post.disambiguation_notes
    # Reason string explicitly mentions the floor shortfall
    assert "≥2-non-name floor" in new_record.disambiguation_notes
    assert "1 corroborating attribute" in new_record.disambiguation_notes


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0043 AC-3 — near-collision (death_hijri >50yr divergence)
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0043", "AC-3")
def test_ac3_death_hijri_divergence_creates_separate_entries_with_cross_disambiguation(
    tmp_path: Path,
) -> None:
    """REQ-SRC-0043 AC-3: a new scholar with display_name matching an
    existing entry but ``death_hijri`` differs by >50 years → separate
    entry with own ``canonical_id``; both entries get
    ``disambiguation_notes`` referencing the other.

    SPEC fixture: ابن تيمية (728 vs 652) → 76-year divergence."""
    registry_path = _isolated_registry_path(tmp_path)
    first = register_provisional_scholars(
        [_ibn_taymiyya_classical()], registry_path=registry_path
    )
    [original] = first.registered
    assert original.death_date_hijri == 728

    second = register_provisional_scholars(
        [_ibn_taymiyya_grandfather()], registry_path=registry_path
    )
    # AC-3 path: separate entry created, no promotion
    assert second.promoted == []
    assert len(second.registered) == 1
    assert len(second.near_collision_disambiguations) == 1

    [new_record] = second.registered
    assert new_record.canonical_id != original.canonical_id
    assert new_record.death_date_hijri == 652

    [(existing_post, paired_new)] = second.near_collision_disambiguations
    assert paired_new.canonical_id == new_record.canonical_id
    assert existing_post.canonical_id == original.canonical_id

    # Cross-references explicitly mention the 76-year divergence
    assert new_record.disambiguation_notes is not None
    assert existing_post.disambiguation_notes is not None
    assert "76 years" in new_record.disambiguation_notes
    assert "76 years" in existing_post.disambiguation_notes
    assert original.canonical_id in new_record.disambiguation_notes
    assert new_record.canonical_id in existing_post.disambiguation_notes


@pytest.mark.spec("REQ-SRC-0043", "AC-3")
def test_ac3_null_vs_populated_death_hijri_triggers_disambiguation(
    tmp_path: Path,
) -> None:
    """AC-3 error_condition variant: display_name match + (one death_hijri
    null, the other populated) triggers near-collision routing."""
    registry_path = _isolated_registry_path(tmp_path)
    first = register_provisional_scholars(
        [_scholar_no_death_date()], registry_path=registry_path
    )
    [original] = first.registered
    assert original.death_date_hijri is None

    second = register_provisional_scholars(
        [_scholar_namesake_with_death_date()], registry_path=registry_path
    )
    assert second.promoted == []
    assert len(second.registered) == 1
    assert len(second.near_collision_disambiguations) == 1

    [new_record] = second.registered
    assert new_record.canonical_id != original.canonical_id
    assert new_record.death_date_hijri == 1200

    # Disambiguation reason explicitly mentions null vs populated
    assert new_record.disambiguation_notes is not None
    assert "null" in new_record.disambiguation_notes
    assert "populated" in new_record.disambiguation_notes


@pytest.mark.spec("REQ-SRC-0043", "AC-3")
def test_ac3_disambiguation_notes_format_uses_iso_date_and_canonical_id(
    tmp_path: Path,
) -> None:
    """Disambiguation note format is auditable: starts with
    ``[YYYY-MM-DD]`` and contains the other entry's canonical_id."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars(
        [_ibn_taymiyya_classical()], registry_path=registry_path
    )
    second = register_provisional_scholars(
        [_ibn_taymiyya_grandfather()], registry_path=registry_path
    )
    [(existing_post, new_record)] = second.near_collision_disambiguations

    for note in (new_record.disambiguation_notes, existing_post.disambiguation_notes):
        assert note is not None
        assert note.startswith("[")
        # Format guarantees: opening bracket, 10-char ISO date, closing bracket
        assert note[11] == "]"
        assert "Distinct from sch_" in note


# ──────────────────────────────────────────────────────────────────
# AC-3 priority over AC-2
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0043", "AC-3")
def test_ac3_takes_priority_over_ac2_when_death_hijri_diverges(
    tmp_path: Path,
) -> None:
    """If a new registration has matching display_name but divergent
    death_hijri, the lookup function returns ``near_collision`` (AC-3)
    even if other corroborating evidence (e.g., matching primary_science)
    is present. AC-3 is the conservative path because divergent
    death_hijri defeats the AC-2 precondition.

    Without this priority, a Saʿdi-with-tafsir matching a different
    Saʿdi with death year 1300 (76 years apart) would erroneously
    promote because primary_science alone clears 1 of 2 floor."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars([_saadi_book_one()], registry_path=registry_path)

    # Same display_name + tafsir, but death_hijri differs by 76 years
    confused_registration = ProvisionalScholarRegistration(
        position_index=0,
        display_name="عبد الرحمن بن ناصر السعدي",
        full_name_lineage="someone else with same display_name",
        death_hijri=1300,  # century 13 — diverges from existing (1376 → 14)
        nisba_tokens=["السعدي"],
        primary_science="tafsir",  # corroborates by itself but irrelevant
        evidence=["colophon"],
        source_book_id="src_unrelated_namesake",
        triggering_match_result_id="smr_namesake",
    )
    second = register_provisional_scholars(
        [confused_registration], registry_path=registry_path
    )
    # AC-3 fired, NOT AC-2 — no promotion despite matching primary_science
    assert second.promoted == []
    assert len(second.near_collision_disambiguations) == 1
    assert len(second.registered) == 1

    [new_record] = second.registered
    # Reason mentions death_hijri divergence specifically (the AC-3 trigger)
    assert new_record.disambiguation_notes is not None
    assert "death_hijri differs" in new_record.disambiguation_notes


# ──────────────────────────────────────────────────────────────────
# Defensive coverage: AC-1 path preserved unchanged from Session 9
# ──────────────────────────────────────────────────────────────────


def test_ac1_unmatched_registration_creates_provisional_unchanged_from_session_9(
    tmp_path: Path,
) -> None:
    """Session 9's AC-1 path is preserved: when no display_name matches
    an existing entry, a new provisional entry is created. Empty
    ``promoted`` and ``near_collision_disambiguations`` lists are
    returned in the outcome."""
    registry_path = _isolated_registry_path(tmp_path)
    outcome = register_provisional_scholars(
        [_saadi_book_one()], registry_path=registry_path
    )
    assert len(outcome.registered) == 1
    assert outcome.promoted == []
    assert outcome.near_collision_disambiguations == []
    [created] = outcome.registered
    assert created.status == "provisional"
    assert created.authority_level == AuthorityLevel.UNKNOWN
    assert created.disambiguation_notes is None  # no near-collision


def test_outcome_dataclass_default_construction_has_empty_lists() -> None:
    """``ProvisionalRegistrationOutcome()`` returns three empty lists.

    Empty registrations input must return this default-constructed
    outcome without any list-identity surprises (e.g., shared mutable
    default lists across instances)."""
    o1 = ProvisionalRegistrationOutcome()
    o2 = ProvisionalRegistrationOutcome()
    assert o1.registered == []
    assert o1.promoted == []
    assert o1.near_collision_disambiguations == []
    # field(default_factory=list) means each instance gets its own list
    o1.registered.append(
        ScholarAuthorityRecord(
            canonical_id="sch_00001",
            canonical_name_ar="x",
            status="provisional",
            birth_date_hijri=None,
            birth_date_ce=None,
            death_date_hijri=None,
            death_date_ce=None,
            era_century_hijri=None,
            record_completeness=0.0,
            data_provenance_score=0.0,
            last_updated="2026-05-08T00:00:00Z",
        )
    )
    assert o2.registered == []  # not shared — independent lists


def test_empty_registrations_input_returns_empty_outcome(
    tmp_path: Path,
) -> None:
    """Locks the side-effect-free contract: empty input → no registry write."""
    registry_path = _isolated_registry_path(tmp_path)
    outcome = register_provisional_scholars([], registry_path=registry_path)
    assert outcome.registered == []
    assert outcome.promoted == []
    assert outcome.near_collision_disambiguations == []
    assert not registry_path.exists()


# ──────────────────────────────────────────────────────────────────
# Defensive: persisted-state correctness after AC-2 + AC-3 paths
# ──────────────────────────────────────────────────────────────────


def test_ac2_promotion_persists_revision_history_entry(
    tmp_path: Path,
) -> None:
    """Promotion via ``update()`` should record the status flip in
    revision_history. This locks that the ``status`` field change
    (provisional → confirmed) is captured for audit."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars([_saadi_book_one()], registry_path=registry_path)
    register_provisional_scholars([_saadi_book_two()], registry_path=registry_path)

    raw = json.loads(registry_path.read_text(encoding="utf-8"))
    [persisted] = raw.values()
    history = persisted.get("revision_history", [])
    # At minimum: status, source_book_ids, evidence_sources, authority_level
    fields_changed = {entry["field"] for entry in history}
    assert "status" in fields_changed
    assert "authority_level" in fields_changed


def test_ac3_disambiguation_creates_two_persisted_entries_in_registry(
    tmp_path: Path,
) -> None:
    """Both Ibn Taymiyya entries are persisted with distinct canonical_ids
    and distinct death_date_hijri values. The registry file holds both."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars(
        [_ibn_taymiyya_classical()], registry_path=registry_path
    )
    register_provisional_scholars(
        [_ibn_taymiyya_grandfather()], registry_path=registry_path
    )

    raw = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(raw) == 2
    death_dates = {record["death_date_hijri"] for record in raw.values()}
    assert death_dates == {652, 728}
    canonical_names = {record["canonical_name_ar"] for record in raw.values()}
    assert canonical_names == {"ابن تيمية"}  # both share the display_name


def test_ac3_arabic_byte_faithful_in_disambiguation_notes(
    tmp_path: Path,
) -> None:
    """Critical Rule 8: Arabic byte-faithful preservation through the
    disambiguation pipeline. The reason string is ASCII (parameter names
    + integers), but the canonical_name_ar field that flows alongside
    must remain unchanged. We assert the persisted display_name carries
    no Unicode normalization side-effects."""
    registry_path = _isolated_registry_path(tmp_path)
    register_provisional_scholars(
        [_ibn_taymiyya_classical()], registry_path=registry_path
    )
    register_provisional_scholars(
        [_ibn_taymiyya_grandfather()], registry_path=registry_path
    )
    raw_text = registry_path.read_text(encoding="utf-8")
    # The Arabic display_name and full_name_lineage strings are persisted
    # exactly as supplied (ensure_ascii=False; no NFC/NFD/NFKC normalization).
    assert "ابن تيمية" in raw_text
    assert "أحمد بن عبد الحليم بن تيمية الحراني" in raw_text
    assert "عبد السلام بن عبد الله بن تيمية" in raw_text
