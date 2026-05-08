"""REQ-SRC-0043 AC-1 deterministic tests — Phase 5 Session 9 (2026-05-08).

Tests the new admission-step consumer that registers ``status=provisional``
``ScholarAuthorityRecord`` entries in ``library/registries/scholars.json``
when ``scholar_match_cell`` emits ``ProvisionalScholarRegistration`` records
under INSUFFICIENT_EVIDENCE NEW IDENTITY routing (Phase 5 amendment
2026-04-30 to REQ-SRC-0043).

Coverage:
  - AC-1 happy path: minor modern scholar not in registry → new entry
    with status=provisional, authority_level=AuthorityLevel.UNKNOWN,
    source_book_ids=[source_id], evidence_sources populated
  - Empty input preserves existing admission behavior (no registry write)
  - Trust fast-track is BLOCKED via ``partial_fragment_author_identity``
    (REQ-SRC-0028 Phase 5 amendment 2026-04-30)
  - Registry write atomicity: ``.bak`` backup created on overwrite
  - Multiple registrations in one source admit-pass: sequential
    ``sch_NNNNN`` IDs assigned deterministically
  - Defensive: arabic byte-faithful preservation in display_name +
    evidence_sources.raw_evidence (no normalization, no diacritic strip)
  - Defensive: existing registered records preserved across new
    registrations (registry write is append-then-replace, not truncate)

Real Arabic fixtures are used throughout — no transliteration, no
synthetic placeholder text. Test scholar identities are chosen to be
contemporary Saudi/Egyptian scholars deliberately outside the
50-scholar gold seed (which targets classical scholars sch_00001..
sch_00050) to satisfy AC-1's "minor modern scholar not in registry"
precondition without overlap risk.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engines.source.contracts import (
    AuthorityLevel,
    AuthorOutput,
    AuthorOutputPosition,
    CaseComplexityRecord,
    FrozenSource,
    Genre,
    LevelStatus,
    MetadataDeliberationResult,
    ProvisionalScholarRegistration,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TrustDecision,
    TrustTier,
    WorkOutput,
)
from engines.source.src.admission import admit_source_and_build_handoff
from engines.source.src.deliberation import (
    assess_case_complexity,
    evaluate_trust_decision,
)
from engines.source.src.scholar_admission import (
    register_provisional_scholars,
)
from engines.source.src.pipeline import SourcePipeline
from engines.source.tests.conftest import FIXTURES_ROOT


# ──────────────────────────────────────────────────────────────────
# Fixtures: real Arabic minor modern scholars (NOT in 50-scholar gold seed)
# ──────────────────────────────────────────────────────────────────


_SHATHRI_REGISTRATION = ProvisionalScholarRegistration(
    position_index=0,
    display_name="سعد بن ناصر الشثري",
    full_name_lineage="سعد بن ناصر بن عبد العزيز الشثري",
    death_hijri=None,  # contemporary; no death date
    nisba_tokens=["الشثري"],
    primary_science="fiqh",
    evidence=["metadata_card", "title_page"],
    source_book_id="src_test_minor_modern",
    triggering_match_result_id="smr_test_001",
)


_TURKI_REGISTRATION = ProvisionalScholarRegistration(
    position_index=1,
    display_name="عبد الله بن عبد المحسن التركي",
    full_name_lineage="عبد الله بن عبد المحسن بن عبد الله التركي",
    death_hijri=None,
    nisba_tokens=["التركي"],
    primary_science="fiqh",
    evidence=["colophon"],
    source_book_id="src_test_minor_modern",
    triggering_match_result_id="smr_test_002",
)


def _isolated_registry_path(tmp_path: Path) -> Path:
    """Build a tmp_path scholars.json so tests do not touch the real registry."""
    registry_dir = tmp_path / "library" / "registries"
    registry_dir.mkdir(parents=True, exist_ok=True)
    return registry_dir / "scholars.json"


def _accepted_metadata_for_minor_modern(
    source_id: str,
    *,
    trust_path: str = "full_deliberation",
) -> SourceMetadata:
    """SourceMetadata shaped for a minor modern fiqh risalah.

    Uses ``risalah`` genre + ``modern_compilation`` authority so the case
    naturally routes to ``standard`` not ``fast_track`` even before the
    Phase 5 ``partial_fragment_author_identity`` gate fires. The
    ``trust_path`` parameter lets a test override to ``"fast_track"`` to
    prove the gate's blocking behavior is enforced at deliberation time.
    """
    return SourceMetadata(
        source_id=source_id,
        title_arabic="رسالة في فقه الزكاة",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-05-08T00:00:00Z",
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="accepted",
        work_id="wrk_test_modern",
        genre=Genre.RISALAH,
        science_scope=["fiqh"],
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        author_output=AuthorOutput(
            status="agent_consensus",
            positions=[
                AuthorOutputPosition(
                    position="سعد بن ناصر الشثري",
                    display_name="سعد بن ناصر الشثري",
                    evidence=["metadata_card"],
                    confidence=0.85,
                    source_agent="agent_a",
                    death_hijri=None,
                )
            ],
        ),
        work_output=WorkOutput(status="definitive", positions=[]),
        trust_decision=TrustDecision(
            decision="verified",
            trust_path=trust_path,
            supporting_agents=["agent_a", "agent_b"],
            evidence_summary="test",
        ),
        level=None,
        level_status=LevelStatus.PENDING_SYNTHESIS,
        level_provenance=None,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
        death_date_hijri=None,
    )


def _deliberation_result_with_provisional(
    source_id: str,
    registrations: list[ProvisionalScholarRegistration],
) -> MetadataDeliberationResult:
    """Build a MetadataDeliberationResult that surfaces N ProvisionalScholarRegistrations.

    The result also carries the corresponding ScholarMatchResult records
    on the audit trail so the admission consumer sees a fully-shaped
    Phase 5 deliberation output (matches the Session 5 wiring contract).
    Other audit trails (human_gate_checkpoints, scholar_match_holds) are
    intentionally empty — REQ-SRC-0043 NEW IDENTITY routing does not
    emit them.
    """
    return MetadataDeliberationResult(
        source_metadata=_accepted_metadata_for_minor_modern(source_id),
        case_complexity_record=CaseComplexityRecord(
            case_id=f"case_{source_id}",
            source_id=source_id,
            field="author_output",
            case_complexity="standard",
            trust_path="full_deliberation",
            signals={
                "genre": "risalah",
                "authority_level": "modern_compilation",
                "partial_fragment_author_identity": True,
            },
            status="completed",
            completed_at="2026-05-08T00:00:00Z",
        ),
        monitor_feedback=[],
        disagreement_cases=[],
        scholar_match_results=[],
        human_gate_checkpoints=[],
        provisional_scholar_registrations=list(registrations),
        scholar_match_holds=[],
    )


def _frozen_from_pipeline(source_pipeline: SourcePipeline, path: Path) -> FrozenSource:
    record = source_pipeline.upload_receipt(path)
    return source_pipeline.freeze_and_manifest(record.submission_id)


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0043 AC-1 — happy path
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0043", "AC-1")
def test_ac1_minor_modern_scholar_creates_provisional_entry(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    """REQ-SRC-0043 AC-1: a book attributed to a minor modern scholar not
    in scholar_authority → registry gains a new entry with status=
    provisional, authority_level=unknown, source_book_ids containing the
    current book_id."""
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    triggering_registration = ProvisionalScholarRegistration(
        position_index=0,
        display_name="سعد بن ناصر الشثري",
        full_name_lineage="سعد بن ناصر بن عبد العزيز الشثري",
        death_hijri=None,
        nisba_tokens=["الشثري"],
        primary_science="fiqh",
        evidence=["metadata_card", "title_page"],
        source_book_id=frozen.source_id,
        triggering_match_result_id="smr_test_001",
    )
    deliberation_result = _deliberation_result_with_provisional(
        frozen.source_id, [triggering_registration]
    )
    registry_path = _isolated_registry_path(tmp_path)
    assert not registry_path.exists()  # pre-condition: empty registry

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        scholar_registry_path=registry_path,
    )

    assert len(result.provisional_scholars_registered) == 1
    registered = result.provisional_scholars_registered[0]
    assert registered.status == "provisional"
    assert registered.authority_level == AuthorityLevel.UNKNOWN
    assert registered.source_book_ids == [frozen.source_id]
    assert registered.canonical_id.startswith("sch_")
    assert len(registered.canonical_id) == 9  # sch_NNNNN
    assert registered.canonical_name_ar == "سعد بن ناصر الشثري"
    assert registered.display_name == "سعد بن ناصر الشثري"
    assert registered.full_name_lineage == "سعد بن ناصر بن عبد العزيز الشثري"
    assert registered.nisba == ["الشثري"]
    assert registered.primary_science == "fiqh"
    assert registered.death_date_hijri is None

    # Evidence sources preserve every raw evidence string with the
    # triggering source_book_id for provenance.
    assert len(registered.evidence_sources) == 2
    assert {ev.evidence_type for ev in registered.evidence_sources} == {
        "metadata_card",
        "title_page",
    }
    for ev in registered.evidence_sources:
        assert ev.book_id == frozen.source_id

    # Registry file exists and contains the new entry.
    assert registry_path.exists()
    raw = json.loads(registry_path.read_text(encoding="utf-8"))
    assert registered.canonical_id in raw
    persisted = raw[registered.canonical_id]
    assert persisted["status"] == "provisional"
    assert persisted["authority_level"] == "unknown"
    assert persisted["source_book_ids"] == [frozen.source_id]
    assert persisted["canonical_name_ar"] == "سعد بن ناصر الشثري"


@pytest.mark.spec("REQ-SRC-0043", "AC-1")
def test_ac1_no_registrations_leaves_registry_untouched(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    """Empty provisional_scholar_registrations preserves existing
    admission behavior — registry file is not touched, no .bak created.

    Critical for backward-compatibility with all pre-Session-9 tests
    that build a MetadataDeliberationResult with the default empty
    list."""
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _deliberation_result_with_provisional(frozen.source_id, [])
    registry_path = _isolated_registry_path(tmp_path)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        scholar_registry_path=registry_path,
    )

    assert result.provisional_scholars_registered == []
    assert not registry_path.exists()
    assert not registry_path.with_suffix(".json.bak").exists()
    assert result.handoff_bundle is not None  # source admission unaffected


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0043 AC-1 + REQ-SRC-0028 — fast-track block via
# partial_fragment_author_identity (Phase 5 amendment 2026-04-30)
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0043", "AC-1")
def test_ac1_partial_fragment_blocks_fast_track_in_assess_complexity(
    source_pipeline: SourcePipeline,
) -> None:
    """REQ-SRC-0028 Phase 5 amendment 2026-04-30: partial_fragment_author_
    identity=True FORCES standard path even when other fast-track
    predicates apply. This is the gate that satisfies REQ-SRC-0043 AC-1
    "trust fast-track is blocked for this source"."""
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "05_tafsir" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    dossier = source_pipeline.intake_analysis(source_id)

    # Without the gate: tafsir + primary + author_death_hijri populated → fast_track
    fast_track_complexity = assess_case_complexity(
        dossier=dossier,
        genre="tafsir",
        author_death_hijri=774,
        authority_level="primary",
    )
    assert fast_track_complexity.case_complexity == "fast_track"
    assert fast_track_complexity.signals["partial_fragment_author_identity"] is False

    # With the gate: same predicates EXCEPT partial_fragment_author_identity=True → standard
    blocked_complexity = assess_case_complexity(
        dossier=dossier,
        genre="tafsir",
        author_death_hijri=774,
        authority_level="primary",
        partial_fragment_author_identity=True,
    )
    assert blocked_complexity.case_complexity == "standard"
    assert blocked_complexity.signals["partial_fragment_author_identity"] is True


@pytest.mark.spec("REQ-SRC-0043", "AC-1")
def test_ac1_partial_fragment_blocks_fast_track_in_evaluate_trust(
    source_pipeline: SourcePipeline,
) -> None:
    """The gate signal threads through evaluate_trust_decision so the
    surfaced TrustDecision.trust_path reflects the block."""
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "05_tafsir" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    dossier = source_pipeline.intake_analysis(source_id)

    # Without gate: trust_path == "fast_track"
    fast_decision = evaluate_trust_decision(
        dossier=dossier,
        genre="tafsir",
        author_death_hijri=774,
        authority_level="primary",
        verification_agents=["agent_a", "agent_b"],
    )
    assert fast_decision.trust_path == "fast_track"

    # With gate: trust_path == "full_deliberation"
    blocked_decision = evaluate_trust_decision(
        dossier=dossier,
        genre="tafsir",
        author_death_hijri=774,
        authority_level="primary",
        verification_agents=["agent_a", "agent_b"],
        partial_fragment_author_identity=True,
    )
    assert blocked_decision.trust_path == "full_deliberation"


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0043 AC-1 — defensive coverage
# ──────────────────────────────────────────────────────────────────


def test_register_provisional_scholars_assigns_sequential_ids(
    tmp_path: Path,
) -> None:
    """Multiple registrations in one source admission → sequential
    sch_NNNNN ids assigned by the underlying register() helper.

    Locks a contract that callers can rely on registration order to
    derive id ordering — useful for AC-2 promotion logic in Session 11
    that must look up "the most recently registered provisional entry"
    by id sequence."""
    registry_path = _isolated_registry_path(tmp_path)
    outcome = register_provisional_scholars(
        [_SHATHRI_REGISTRATION, _TURKI_REGISTRATION],
        registry_path=registry_path,
    )

    assert len(outcome.registered) == 2
    assert outcome.promoted == []
    assert outcome.near_collision_disambiguations == []
    first_num = int(outcome.registered[0].canonical_id[4:])
    second_num = int(outcome.registered[1].canonical_id[4:])
    assert second_num == first_num + 1


def test_register_provisional_scholars_preserves_existing_entries(
    tmp_path: Path,
) -> None:
    """A second registration call must NOT clobber entries from the first
    call — the registry is append-style.

    Critical because in production, scholars.json accumulates across
    many sources; a write-truncate bug would silently delete the entire
    library catalog of identified scholars."""
    registry_path = _isolated_registry_path(tmp_path)
    first_outcome = register_provisional_scholars(
        [_SHATHRI_REGISTRATION],
        registry_path=registry_path,
    )
    second_outcome = register_provisional_scholars(
        [_TURKI_REGISTRATION],
        registry_path=registry_path,
    )

    assert len(first_outcome.registered) == 1
    assert len(second_outcome.registered) == 1
    assert first_outcome.promoted == []
    assert second_outcome.promoted == []
    assert first_outcome.near_collision_disambiguations == []
    assert second_outcome.near_collision_disambiguations == []
    first_record = first_outcome.registered[0]
    second_record = second_outcome.registered[0]
    assert first_record.canonical_id != second_record.canonical_id

    raw = json.loads(registry_path.read_text(encoding="utf-8"))
    assert first_record.canonical_id in raw
    assert second_record.canonical_id in raw
    assert raw[first_record.canonical_id]["canonical_name_ar"] == "سعد بن ناصر الشثري"
    assert raw[second_record.canonical_id]["canonical_name_ar"] == (
        "عبد الله بن عبد المحسن التركي"
    )


def test_register_provisional_scholars_creates_bak_on_overwrite(
    tmp_path: Path,
) -> None:
    """Atomic-write contract: the second call to register triggers a .bak
    backup of the first version of scholars.json, per
    shared/scholar_authority/src/scholar_authority.py:_save_registry."""
    registry_path = _isolated_registry_path(tmp_path)
    bak_path = registry_path.with_suffix(".json.bak")
    register_provisional_scholars(
        [_SHATHRI_REGISTRATION],
        registry_path=registry_path,
    )
    assert not bak_path.exists()  # first write — no prior file to back up

    register_provisional_scholars(
        [_TURKI_REGISTRATION],
        registry_path=registry_path,
    )
    # After the second write, .bak holds the first-call version.
    assert bak_path.exists()
    bak_data = json.loads(bak_path.read_text(encoding="utf-8"))
    assert len(bak_data) == 1


def test_register_provisional_scholars_preserves_arabic_byte_faithful(
    tmp_path: Path,
) -> None:
    """Arabic byte-faithful preservation: display_name, full_name_lineage,
    nisba, and evidence raw_evidence are persisted exactly as supplied
    — no NFC/NFD/NFKC normalization, no taa-marbuta mutation, no
    diacritic strip.

    The test uses a name carrying ة (taa marbuta), ا (alef without hamza),
    and a kasratan diacritic to ensure none of these are mutated by the
    registration path. Critical Rule 8 ("Arabic text is fragile —
    NEVER apply Unicode normalization") must hold end-to-end through
    the persistence layer."""
    arabic_with_diacritics = ProvisionalScholarRegistration(
        position_index=0,
        display_name="عبد الرحمن بن ناصر السعدي",
        full_name_lineage="عبد الرحمن بن ناصر بن عبد الله السعدي",
        death_hijri=1376,
        nisba_tokens=["السعدي"],
        primary_science="tafsir",
        evidence=["تيسير الكريم الرحمن"],  # raw evidence carrying Arabic
        source_book_id="src_taysir",
        triggering_match_result_id="smr_taysir",
    )
    registry_path = _isolated_registry_path(tmp_path)
    outcome = register_provisional_scholars(
        [arabic_with_diacritics], registry_path=registry_path
    )
    [registered] = outcome.registered
    assert outcome.promoted == []
    assert outcome.near_collision_disambiguations == []

    # In-memory record preserves bytes exactly.
    assert registered.canonical_name_ar == "عبد الرحمن بن ناصر السعدي"
    assert registered.full_name_lineage == "عبد الرحمن بن ناصر بن عبد الله السعدي"
    assert registered.nisba == ["السعدي"]
    assert registered.evidence_sources[0].raw_evidence == "تيسير الكريم الرحمن"

    # JSON round-trip through scholars.json preserves bytes exactly
    # (json.dumps with ensure_ascii=False per _save_registry contract).
    raw_text = registry_path.read_text(encoding="utf-8")
    assert "عبد الرحمن بن ناصر السعدي" in raw_text
    assert "تيسير الكريم الرحمن" in raw_text


def test_register_provisional_scholars_unknown_evidence_types_become_agent_inference(
    tmp_path: Path,
) -> None:
    """Evidence strings outside the REQ-SRC-0043 known-type set
    (metadata_card / title_page / colophon / agent_inference) are
    classified as agent_inference. The raw_evidence string itself is
    preserved byte-faithfully for downstream provenance — never mutated
    or reduced to its category tag."""
    arbitrary_evidence = ProvisionalScholarRegistration(
        position_index=0,
        display_name="فلان بن فلان",
        full_name_lineage="فلان بن فلان",
        death_hijri=None,
        nisba_tokens=[],
        primary_science=None,
        evidence=["some_unrecognized_tag", "title_page"],
        source_book_id="src_arbitrary",
        triggering_match_result_id="smr_arbitrary",
    )
    registry_path = _isolated_registry_path(tmp_path)
    outcome = register_provisional_scholars(
        [arbitrary_evidence], registry_path=registry_path
    )
    [registered] = outcome.registered
    assert outcome.promoted == []
    assert outcome.near_collision_disambiguations == []

    by_raw = {ev.raw_evidence: ev for ev in registered.evidence_sources}
    assert by_raw["some_unrecognized_tag"].evidence_type == "agent_inference"
    assert by_raw["title_page"].evidence_type == "title_page"
    # Even the unrecognized tag's literal string is preserved.
    assert "some_unrecognized_tag" in by_raw


def test_register_provisional_scholars_empty_input_is_no_op(
    tmp_path: Path,
) -> None:
    """Empty registrations list returns an empty outcome and does NOT
    create the registry file. Locks the contract relied on by
    test_ac1_no_registrations_leaves_registry_untouched at the
    higher-level admission test."""
    registry_path = _isolated_registry_path(tmp_path)
    outcome = register_provisional_scholars([], registry_path=registry_path)
    assert outcome.registered == []
    assert outcome.promoted == []
    assert outcome.near_collision_disambiguations == []
    assert not registry_path.exists()


def test_register_provisional_scholars_default_path_is_library_registries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When ``registry_path`` is None, the consumer falls back to
    ``library/registries/scholars.json``. Verified by monkeypatching
    the working directory so the default path resolves into tmp_path
    rather than touching the real repo registry."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "library" / "registries").mkdir(parents=True, exist_ok=True)
    register_provisional_scholars([_SHATHRI_REGISTRATION])
    expected_path = tmp_path / "library" / "registries" / "scholars.json"
    assert expected_path.exists()
    raw = json.loads(expected_path.read_text(encoding="utf-8"))
    assert any(
        record["canonical_name_ar"] == "سعد بن ناصر الشثري" for record in raw.values()
    )


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0043 AC-1 — admission integration: provisional admission
# coexists with normal source admission flow
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0043", "AC-1")
def test_ac1_admission_persists_handoff_bundle_alongside_provisional(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    """When both a provisional registration AND the normal admission
    path execute, the handoff bundle is built correctly and the
    SourceAdmissionResult carries both.

    This locks that REQ-SRC-0043 admission is ADDITIVE on top of the
    existing source admission flow — not a replacement — and that no
    pre-Session-9 admission behavior is regressed."""
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    triggering = ProvisionalScholarRegistration(
        position_index=0,
        display_name="سعد بن ناصر الشثري",
        full_name_lineage="سعد بن ناصر بن عبد العزيز الشثري",
        death_hijri=None,
        nisba_tokens=["الشثري"],
        primary_science="fiqh",
        evidence=["metadata_card"],
        source_book_id=frozen.source_id,
        triggering_match_result_id="smr_001",
    )
    deliberation_result = _deliberation_result_with_provisional(
        frozen.source_id, [triggering]
    )
    registry_path = _isolated_registry_path(tmp_path)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        scholar_registry_path=registry_path,
    )

    # Both the source-side admission outputs AND the registry-side
    # provisional registration succeeded.
    assert result.handoff_bundle is not None
    assert result.handoff_bundle.source_metadata.source_id == frozen.source_id
    assert len(result.source_collection_records) == 1
    assert len(result.provisional_scholars_registered) == 1
    assert result.raw_upload_record.status == "source_engine_accepted"


@pytest.mark.spec("REQ-SRC-0043", "AC-1")
def test_ac1_risk_gate_blocks_provisional_registration(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    """When the dossier has unacknowledged risk flags, the source
    admission returns AWAITING_OWNER_ACK and registration is DEFERRED
    — the registry file is NOT written.

    Critical because the alternative (writing provisional records for
    risk-blocked sources) would pollute scholars.json with entries
    derived from sources the owner has not yet authorized for ingest."""
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    dossier.study_quality_risk_flags = ["material_missing_volumes"]
    triggering = ProvisionalScholarRegistration(
        position_index=0,
        display_name="سعد بن ناصر الشثري",
        full_name_lineage="سعد بن ناصر بن عبد العزيز الشثري",
        death_hijri=None,
        nisba_tokens=["الشثري"],
        primary_science="fiqh",
        evidence=["metadata_card"],
        source_book_id=frozen.source_id,
        triggering_match_result_id="smr_001",
    )
    deliberation_result = _deliberation_result_with_provisional(
        frozen.source_id, [triggering]
    )
    registry_path = _isolated_registry_path(tmp_path)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=False,
        scholar_registry_path=registry_path,
    )

    assert result.owner_submission_risk_case is not None
    assert result.handoff_bundle is None
    assert result.provisional_scholars_registered == []
    assert not registry_path.exists()
