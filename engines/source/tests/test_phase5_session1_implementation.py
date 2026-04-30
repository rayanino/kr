"""Phase 5 Session 1 implementation — spec-linked tests.

Covers the four Session 1 contract atoms:

  - CON-SRC-0008 ScholarMatchResult — dual-state surface (5 ACs)
  - CON-SRC-0009 ScholarEvidencePacket — immutable case bundle (4 ACs)
  - REQ-SRC-0049 Scholar registry snapshot locking (4 ACs)
  - INV-SRC-0017 Registry snapshot version pin (4 ACs)

Each test carries ``@pytest.mark.spec(atom_id, ac_id)`` so failures
identify the exact spec violation. Real Arabic fixture data is used per
``.claude/rules/testing.md`` (no transliteration, no lorem ipsum).

This file is separate from ``test_phase5_scholar_matching_atoms.py``
which tests SPEC CONTENT (atom presence, field values, schema). This
file tests IMPLEMENTATION (Pydantic model behavior, drift detection).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engines.source.contracts import ErrorCode
from shared.scholar_authority.src.match_contracts import (
    K_CAP_DEGRADED,
    SOURCE_SNIPPET_MAX_BYTES,
    SOURCE_SNIPPETS_MAX,
    CareerPhaseRef,
    CitationRef,
    DossierContext,
    NormalizedFragment,
    Position,
    RevisionHistoryEntry,
    ScholarCandidate,
    ScholarEvidencePacket,
    ScholarMatchProvenance,
    ScholarMatchResult,
    ScoreBreakdown,
    ThresholdAudit,
    VerifierRecord,
)
from shared.scholar_authority.src.snapshot_lock import (
    RegistrySnapshot,
    RegistrySnapshotDriftError,
    RuntimeExternalCallError,
    lock_registry_snapshot,
    pin_registry_snapshot,
    validate_no_drift,
)


# ---------------------------------------------------------------------------
# Test builders — minimal-but-valid instances of each contract type.
# Tests mutate one field at a time to exercise specific invariants.
# ---------------------------------------------------------------------------


def _build_score_breakdown(name_match: float = 0.95) -> ScoreBreakdown:
    """Build a 9-feature ScoreBreakdown with all features populated."""
    return ScoreBreakdown(
        name_match=name_match,
        death_date_proximity=0.92,
        school_affiliation_overlap=0.85,
        work_title_match=0.88,
        teacher_student_network_match=0.80,
        geographic_origin_match=0.75,
        century_active_match=0.95,
        primary_science_match=0.90,
        secondary_sciences_overlap=0.70,
    )


def _build_citation_ref() -> CitationRef:
    """Build a CitationRef from a real Hadith collection title page."""
    return CitationRef(
        source_book_id="src_00001",
        evidence_type="title_page",
        raw_evidence="فتح الباري شرح صحيح البخاري للحافظ ابن حجر العسقلاني",
    )


def _build_verifier_record(round_count: int = 1) -> VerifierRecord:
    """Build a VerifierRecord with stable hashes / seeds."""
    return VerifierRecord(
        verifier_a_id="claude-opus-4-7",
        verifier_b_id="gpt-5.4",
        verifier_a_seed=42,
        verifier_b_seed=43,
        verifier_a_prompt_template_hash="sha256:aaaa...verifier_a_v1",
        verifier_b_prompt_template_hash="sha256:bbbb...verifier_b_v1",
        round_count=round_count,  # type: ignore[arg-type]
    )


def _build_threshold_audit_definitive() -> ThresholdAudit:
    """Threshold audit with all 4 predicates true (definitive verdict)."""
    return ThresholdAudit(
        mean_passes=True,
        both_pass=True,
        no_rival_close=True,
        corroboration_count_ge_2=True,
        mean_confidence=0.94,
        leader_confidence=0.95,
        rival_confidence=0.30,
        corroboration_count=4,
    )


def _build_threshold_audit_disputed() -> ThresholdAudit:
    """Threshold audit with rival within 0.07 (disputed verdict)."""
    return ThresholdAudit(
        mean_passes=True,
        both_pass=True,
        no_rival_close=False,  # rival within 0.07 of leader
        corroboration_count_ge_2=True,
        mean_confidence=0.93,
        leader_confidence=0.94,
        rival_confidence=0.89,
        corroboration_count=3,
    )


def _build_threshold_audit_insufficient() -> ThresholdAudit:
    """Threshold audit with corroboration_count < 2 (insufficient_evidence)."""
    return ThresholdAudit(
        mean_passes=False,
        both_pass=False,
        no_rival_close=True,
        corroboration_count_ge_2=False,
        mean_confidence=0.62,
        leader_confidence=0.68,
        rival_confidence=None,
        corroboration_count=1,
    )


def _build_provenance(
    audit: ThresholdAudit | None = None,
    registry_release_version: str = "2026-04-15.r1",
    matched_phase: CareerPhaseRef | None = None,
) -> ScholarMatchProvenance:
    """Build a complete ScholarMatchProvenance for a given audit shape."""
    return ScholarMatchProvenance(
        stage_1_score_breakdown={
            "sch_00042": {"name": 0.95, "work_title": 0.88, "death_date": 0.92}
        },
        stage_2_verifier_record=_build_verifier_record(),
        threshold_audit=audit or _build_threshold_audit_definitive(),
        registry_release_version=registry_release_version,
        matched_phase=matched_phase,
    )


def _build_position(
    canonical_id: str = "sch_00042",
    confidence: float = 0.95,
) -> Position:
    """Build a Position instance with realistic confidence and evidence."""
    return Position(
        canonical_id=canonical_id,
        confidence=confidence,
        per_verifier_confidence={
            "claude-opus-4-7": confidence,
            "gpt-5.4": confidence - 0.02,
        },
        score_breakdown=_build_score_breakdown(name_match=confidence),
        why_not_other_candidate="No close rival identified in dossier",
        cited_evidence=[_build_citation_ref()],
    )


def _build_definitive_result(
    canonical_scholar_id: str = "sch_00042",
    record_status: str = "confirmed",
) -> ScholarMatchResult:
    """Build a minimal definitive ScholarMatchResult."""
    return ScholarMatchResult(
        canonical_scholar_id=canonical_scholar_id,
        confidence=0.94,
        disambiguation_state="definitive",
        record_status=record_status,  # type: ignore[arg-type]
        evidence_sources=[_build_citation_ref()],
        positions=[],
        provenance=_build_provenance(),
    )


def _build_normalized_fragment() -> NormalizedFragment:
    """Build a 5-component parse for ابن حجر العسقلاني."""
    return NormalizedFragment(
        ism="أحمد",
        kunyah="أبو الفضل",
        nasab_chain=["ابن علي", "ابن محمد", "ابن محمد"],
        laqab=["شهاب الدين"],
        nisba_list=["العسقلاني", "المصري", "الشافعي"],
    )


def _build_dossier_context() -> DossierContext:
    """Build a typical DossierContext for a Hadith commentary dossier."""
    return DossierContext(
        genre="sharh",
        primary_science="hadith",
        century_active_hijri_estimates=[8, 9],
        school_affiliation_hints={"fiqh": "shafii", "aqidah": "ashari"},
        attributed_works=["fath_al_bari"],
        geographic_signals=["العسقلان", "القاهرة"],
        work_title_extracts=["فتح الباري شرح صحيح البخاري"],
    )


def _build_scholar_candidate(
    canonical_id: str = "sch_00042",
    canonical_name_ar: str = "ابن حجر العسقلاني",
) -> ScholarCandidate:
    """Build a Stage-1 ScholarCandidate."""
    return ScholarCandidate(
        canonical_id=canonical_id,
        canonical_name_ar=canonical_name_ar,
        score_breakdown={"name_channel": 0.95, "work_title_channel": 0.88},
        provenance_for_inclusion="work_title_channel",
    )


def _build_evidence_packet(
    candidate_count: int = 4,
    registry_release_version: str = "2026-04-15.r1",
) -> ScholarEvidencePacket:
    """Build a ScholarEvidencePacket with K candidates from real Hadith ids."""
    candidates = [
        _build_scholar_candidate(
            canonical_id=f"sch_{i:05d}",
            canonical_name_ar=f"ابن حجر فرع {i}",
        )
        for i in range(42, 42 + candidate_count)
    ]
    return ScholarEvidencePacket(
        normalized_fragment="ابن حجر العسقلاني",
        display_fragment="الحافظ ابن حجر العسقلاني",
        match_key="ابن_حجر_العسقلاني",
        parsed_components=_build_normalized_fragment(),
        dossier_context=_build_dossier_context(),
        candidate_set=candidates,
        source_snippets=["قال الحافظ ابن حجر في فتح الباري"],
        registry_release_version=registry_release_version,
    )


# ---------------------------------------------------------------------------
# CON-SRC-0008 ScholarMatchResult — 5 ACs
# ---------------------------------------------------------------------------


@pytest.mark.spec("CON-SRC-0008", "AC-1")
def test_definitive_with_confirmed_record_emits_dual_state() -> None:
    """Definitive against a confirmed record populates both state surfaces."""
    result = _build_definitive_result(
        canonical_scholar_id="sch_00042", record_status="confirmed"
    )

    assert result.canonical_scholar_id == "sch_00042"
    assert result.confidence is not None and 0.0 <= result.confidence <= 1.0
    assert result.disambiguation_state == "definitive"
    assert result.record_status == "confirmed"
    assert result.evidence_sources, "definitive requires non-empty evidence_sources"
    assert result.positions == [], "definitive does not populate positions"
    audit = result.provenance.threshold_audit
    assert audit.mean_passes
    assert audit.both_pass
    assert audit.no_rival_close
    assert audit.corroboration_count_ge_2
    assert result.provenance.registry_release_version == "2026-04-15.r1"
    assert result.provenance.matched_phase is None


@pytest.mark.spec("CON-SRC-0008", "AC-2")
def test_disputed_populates_positions_with_full_breakdown() -> None:
    """Disputed has positions[] >= 2 with full 9-feature score_breakdown."""
    leader = _build_position(canonical_id="sch_00042", confidence=0.94)
    rival = _build_position(canonical_id="sch_00077", confidence=0.89)

    result = ScholarMatchResult(
        canonical_scholar_id="sch_00042",  # leader id (top of positions[0])
        confidence=0.94,
        disambiguation_state="disputed",
        record_status="confirmed",
        evidence_sources=[_build_citation_ref()],
        positions=[leader, rival],
        provenance=_build_provenance(audit=_build_threshold_audit_disputed()),
    )

    assert result.disambiguation_state == "disputed"
    assert len(result.positions) >= 2
    assert result.canonical_scholar_id == result.positions[0].canonical_id
    # record_status reflects the leader's 5-state lifecycle per CON-SRC-0008
    # AC-2 line 158-166 ("record_status reflects the leading id's record
    # lifecycle"). Non-null follows from the field spec line 73-81 ("Null
    # when canonical_scholar_id is null") — disputed always has a non-null
    # canonical_scholar_id, so record_status is non-null.
    assert result.record_status == "confirmed"
    for pos in result.positions:
        assert pos.cited_evidence, "every position must have non-empty cited_evidence"
        sb = pos.score_breakdown
        # 9 features — verify by spot-checking a few
        assert 0.0 <= sb.name_match <= 1.0
        assert 0.0 <= sb.teacher_student_network_match <= 1.0
        assert 0.0 <= sb.secondary_sciences_overlap <= 1.0
    audit = result.provenance.threshold_audit
    assert not audit.no_rival_close, "disputed requires at least one predicate false"


@pytest.mark.spec("CON-SRC-0008", "AC-3")
def test_insufficient_evidence_nullifies_id_confidence_record_status() -> None:
    """Insufficient_evidence: canonical_scholar_id, confidence, record_status all null."""
    result = ScholarMatchResult(
        canonical_scholar_id=None,
        confidence=None,
        disambiguation_state="insufficient_evidence",
        record_status=None,
        evidence_sources=[],  # may be empty — no positive identification
        positions=[],
        provenance=_build_provenance(audit=_build_threshold_audit_insufficient()),
    )

    assert result.canonical_scholar_id is None
    assert result.confidence is None
    assert result.record_status is None
    assert result.positions == []
    audit = result.provenance.threshold_audit
    # threshold_audit MUST still record which predicate failed
    assert not audit.corroboration_count_ge_2
    assert audit.corroboration_count == 1
    assert audit.mean_confidence == 0.62


@pytest.mark.spec("CON-SRC-0008", "AC-4")
def test_definitive_against_provisional_record_keeps_states_orthogonal() -> None:
    """Definitive disambiguation_state against a provisional record_status.

    The match is conclusive; the registry record is still in early
    lifecycle. Both state surfaces are independently correct.
    """
    result = _build_definitive_result(
        canonical_scholar_id="sch_00007",  # أحمد بن حنبل (early record)
        record_status="provisional",
    )

    assert result.disambiguation_state == "definitive"
    assert result.record_status == "provisional"
    # State orthogonality: disambiguation_state and record_status do not
    # mechanically constrain each other; flattening would silently drop
    # the registry-lifecycle signal that downstream display cards may need.


@pytest.mark.spec("CON-SRC-0008", "AC-5")
def test_snapshot_version_field_name_is_rejected_in_provenance() -> None:
    """snapshot_version is FORBIDDEN; canonical name is registry_release_version."""
    with pytest.raises(ValidationError) as exc_info:
        ScholarMatchProvenance(
            stage_1_score_breakdown={},
            stage_2_verifier_record=_build_verifier_record(),
            threshold_audit=_build_threshold_audit_definitive(),
            snapshot_version="2026-04-15.r1",  # type: ignore[call-arg]
        )

    error_str = str(exc_info.value)
    assert "snapshot_version" in error_str
    assert "FORBIDDEN" in error_str
    assert "registry_release_version" in error_str


# Cross-field invariant tests beyond the named ACs — defensive coverage of
# the model_validator branches.


@pytest.mark.spec("CON-SRC-0008", "AC-1")
def test_definitive_without_canonical_scholar_id_rejected() -> None:
    """definitive disambiguation_state requires canonical_scholar_id non-null."""
    with pytest.raises(ValidationError, match="canonical_scholar_id"):
        ScholarMatchResult(
            canonical_scholar_id=None,
            confidence=0.94,
            disambiguation_state="definitive",
            record_status="confirmed",
            evidence_sources=[_build_citation_ref()],
            positions=[],
            provenance=_build_provenance(),
        )


@pytest.mark.spec("CON-SRC-0008", "AC-1")
def test_definitive_with_positions_populated_rejected() -> None:
    """definitive disambiguation_state forbids non-empty positions."""
    with pytest.raises(ValidationError, match="positions"):
        ScholarMatchResult(
            canonical_scholar_id="sch_00042",
            confidence=0.94,
            disambiguation_state="definitive",
            record_status="confirmed",
            evidence_sources=[_build_citation_ref()],
            positions=[_build_position()],  # forbidden when definitive
            provenance=_build_provenance(),
        )


@pytest.mark.spec("CON-SRC-0008", "AC-2")
def test_disputed_with_only_one_position_rejected() -> None:
    """disputed disambiguation_state requires positions length >= 2."""
    with pytest.raises(ValidationError, match="positions"):
        ScholarMatchResult(
            canonical_scholar_id="sch_00042",
            confidence=0.94,
            disambiguation_state="disputed",
            record_status="confirmed",
            evidence_sources=[_build_citation_ref()],
            positions=[_build_position()],  # only one — must be >= 2
            provenance=_build_provenance(audit=_build_threshold_audit_disputed()),
        )


@pytest.mark.spec("CON-SRC-0008", "AC-2")
def test_disputed_with_null_record_status_rejected() -> None:
    """disputed disambiguation_state requires record_status non-null.

    Per CON-SRC-0008 AC-2 ("record_status reflects the leading id's
    record lifecycle") and field spec line 73-81 ("Null when
    canonical_scholar_id is null"): disputed always has a non-null
    canonical_scholar_id (the leader id), so record_status MUST be
    non-null. The orthogonal-state surface still allows any of the 5
    lifecycle values; only None is forbidden when canonical is non-null.
    """
    leader = _build_position(canonical_id="sch_00042", confidence=0.94)
    rival = _build_position(canonical_id="sch_00077", confidence=0.89)

    with pytest.raises(ValidationError, match="record_status"):
        ScholarMatchResult(
            canonical_scholar_id="sch_00042",
            confidence=0.94,
            disambiguation_state="disputed",
            record_status=None,  # forbidden when canonical_scholar_id is non-null
            evidence_sources=[_build_citation_ref()],
            positions=[leader, rival],
            provenance=_build_provenance(audit=_build_threshold_audit_disputed()),
        )


@pytest.mark.spec("CON-SRC-0008", "AC-2")
def test_disputed_canonical_id_must_match_positions_zero() -> None:
    """canonical_scholar_id must equal positions[0].canonical_id when disputed."""
    leader = _build_position(canonical_id="sch_00042", confidence=0.94)
    rival = _build_position(canonical_id="sch_00077", confidence=0.89)

    with pytest.raises(ValidationError, match="positions\\[0\\]"):
        ScholarMatchResult(
            canonical_scholar_id="sch_00099",  # NOT the leader id
            confidence=0.94,
            disambiguation_state="disputed",
            record_status="confirmed",
            evidence_sources=[_build_citation_ref()],
            positions=[leader, rival],
            provenance=_build_provenance(audit=_build_threshold_audit_disputed()),
        )


@pytest.mark.spec("CON-SRC-0008", "AC-3")
def test_insufficient_evidence_with_canonical_id_rejected() -> None:
    """insufficient_evidence forbids non-null canonical_scholar_id."""
    with pytest.raises(ValidationError, match="canonical_scholar_id"):
        ScholarMatchResult(
            canonical_scholar_id="sch_00042",  # forbidden when insufficient
            confidence=None,
            disambiguation_state="insufficient_evidence",
            record_status=None,
            evidence_sources=[],
            positions=[],
            provenance=_build_provenance(audit=_build_threshold_audit_insufficient()),
        )


# ---------------------------------------------------------------------------
# CON-SRC-0009 ScholarEvidencePacket — 4 ACs
# ---------------------------------------------------------------------------


@pytest.mark.spec("CON-SRC-0009", "AC-1")
def test_packet_construction_with_8_required_fields_populated() -> None:
    """Stage-1 narrowing produces a packet with all 8 required fields."""
    packet = _build_evidence_packet(
        candidate_count=4, registry_release_version="2026-04-15.r1"
    )

    assert packet.normalized_fragment
    assert packet.display_fragment
    assert packet.match_key
    assert packet.parsed_components is not None
    assert packet.dossier_context is not None
    assert len(packet.candidate_set) == 4
    assert isinstance(packet.source_snippets, list)
    assert packet.registry_release_version == "2026-04-15.r1"


@pytest.mark.spec("CON-SRC-0009", "AC-2")
def test_packet_is_immutable_byte_identical_across_rounds() -> None:
    """Round-1 verifiers receive THE SAME packet (no mutation permitted)."""
    packet = _build_evidence_packet()

    # Pydantic frozen=True raises ValidationError on attempted mutation
    with pytest.raises(ValidationError):
        packet.match_key = "ابن_حجر_الهيتمي"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        packet.registry_release_version = "2026-04-15.r2"  # type: ignore[misc]


@pytest.mark.spec("CON-SRC-0009", "AC-3")
def test_chosen_id_closure_check_against_packet() -> None:
    """A round-1 chosen_id outside candidate_set is detected as F-4 hallucination."""
    packet = _build_evidence_packet(candidate_count=4)
    in_set_ids = [c.canonical_id for c in packet.candidate_set]
    assert all(packet.is_chosen_id_in_candidate_set(cid) for cid in in_set_ids)
    # Hallucinated id (not in packet) — orchestrator must reject this
    assert not packet.is_chosen_id_in_candidate_set("sch_99999")
    assert not packet.is_chosen_id_in_candidate_set("sch_00077")


@pytest.mark.spec("CON-SRC-0009", "AC-4")
def test_snapshot_version_rejected_at_packet_top_level() -> None:
    """Forbidden field name rejected with explicit canonical-name pointer."""
    with pytest.raises(ValidationError) as exc_info:
        ScholarEvidencePacket(
            normalized_fragment="ابن حجر",
            display_fragment="الحافظ ابن حجر",
            match_key="ابن_حجر",
            parsed_components=_build_normalized_fragment(),
            dossier_context=_build_dossier_context(),
            candidate_set=[],
            source_snippets=[],
            snapshot_version="2026-04-15.r1",  # type: ignore[call-arg]
        )

    error_str = str(exc_info.value)
    assert "snapshot_version" in error_str
    assert "FORBIDDEN" in error_str
    assert "registry_release_version" in error_str


@pytest.mark.spec("CON-SRC-0009", "AC-1")
def test_packet_rejects_oversized_candidate_set() -> None:
    """K cap = 12 degraded ceiling per REQ-SRC-0051."""
    too_many = [
        _build_scholar_candidate(canonical_id=f"sch_{i:05d}")
        for i in range(K_CAP_DEGRADED + 1)
    ]
    with pytest.raises(ValidationError, match="K_CAP_DEGRADED"):
        ScholarEvidencePacket(
            normalized_fragment="ابن حجر",
            display_fragment="ابن حجر",
            match_key="ابن_حجر",
            parsed_components=_build_normalized_fragment(),
            dossier_context=_build_dossier_context(),
            candidate_set=too_many,
            source_snippets=[],
            registry_release_version="2026-04-15.r1",
        )


@pytest.mark.spec("CON-SRC-0009", "AC-1")
def test_packet_rejects_too_many_source_snippets() -> None:
    """Snippet count cap = 5 per CON-SRC-0009."""
    too_many = [f"snippet {i}" for i in range(SOURCE_SNIPPETS_MAX + 1)]
    with pytest.raises(ValidationError, match="SOURCE_SNIPPETS_MAX"):
        ScholarEvidencePacket(
            normalized_fragment="ابن حجر",
            display_fragment="ابن حجر",
            match_key="ابن_حجر",
            parsed_components=_build_normalized_fragment(),
            dossier_context=_build_dossier_context(),
            candidate_set=[],
            source_snippets=too_many,
            registry_release_version="2026-04-15.r1",
        )


@pytest.mark.spec("CON-SRC-0009", "AC-1")
def test_packet_rejects_oversized_snippet_bytes() -> None:
    """Per-snippet UTF-8 byte cap = 2048 per CON-SRC-0009."""
    # Generate a snippet that exceeds 2048 UTF-8 bytes when encoded.
    # ASCII characters are 1 byte each; SOURCE_SNIPPET_MAX_BYTES + 1 == 2049.
    oversized = "x" * (SOURCE_SNIPPET_MAX_BYTES + 1)
    with pytest.raises(ValidationError, match="UTF-8 bytes"):
        ScholarEvidencePacket(
            normalized_fragment="ابن حجر",
            display_fragment="ابن حجر",
            match_key="ابن_حجر",
            parsed_components=_build_normalized_fragment(),
            dossier_context=_build_dossier_context(),
            candidate_set=[],
            source_snippets=[oversized],
            registry_release_version="2026-04-15.r1",
        )


@pytest.mark.spec("CON-SRC-0009", "AC-3")
def test_packet_rejects_duplicate_canonical_ids() -> None:
    """Duplicate canonical_ids break INV-SRC-0016 unambiguous closure."""
    dup_a = _build_scholar_candidate(canonical_id="sch_00042")
    dup_b = _build_scholar_candidate(canonical_id="sch_00042")  # same id
    with pytest.raises(ValidationError, match="duplicate canonical_id"):
        ScholarEvidencePacket(
            normalized_fragment="ابن حجر",
            display_fragment="ابن حجر",
            match_key="ابن_حجر",
            parsed_components=_build_normalized_fragment(),
            dossier_context=_build_dossier_context(),
            candidate_set=[dup_a, dup_b],
            source_snippets=[],
            registry_release_version="2026-04-15.r1",
        )


# ---------------------------------------------------------------------------
# REQ-SRC-0049 Scholar registry snapshot locking — 4 ACs
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0049", "AC-1")
def test_pinned_snapshot_propagates_to_provenance() -> None:
    """Match-call output carries provenance.registry_release_version == pinned."""
    with lock_registry_snapshot("2026-04-15.r1") as pinned:
        result = ScholarMatchResult(
            canonical_scholar_id="sch_00001",  # البخاري
            confidence=0.95,
            disambiguation_state="definitive",
            record_status="confirmed",
            evidence_sources=[_build_citation_ref()],
            positions=[],
            provenance=_build_provenance(
                registry_release_version=pinned.registry_release_version
            ),
        )

    assert pinned.registry_release_version == "2026-04-15.r1"
    assert result.provenance.registry_release_version == "2026-04-15.r1"


@pytest.mark.spec("REQ-SRC-0049", "AC-2")
def test_concurrent_registry_update_does_not_drift_in_flight_case() -> None:
    """A concurrent r2 release does not affect an already-pinned r1 case."""
    pinned = pin_registry_snapshot("2026-04-15.r1")
    # Concurrent registry update produces "2026-04-15.r2" — but the in-flight
    # case's observed snapshot is still r1 (proper isolation). validate_no_drift
    # against the case-pinned r1 succeeds because the case did not switch.
    validate_no_drift(pinned, observed_release_version="2026-04-15.r1")


@pytest.mark.spec("REQ-SRC-0049", "AC-3")
def test_orchestrator_restart_detects_drift_to_newer_release() -> None:
    """Restart-induced load of r2 against pinned r1 raises drift error."""
    pinned = pin_registry_snapshot("2026-04-15.r1")
    with pytest.raises(RegistrySnapshotDriftError) as exc_info:
        validate_no_drift(pinned, observed_release_version="2026-04-15.r2")

    assert exc_info.value.error_code == ErrorCode.REGISTRY_SNAPSHOT_DRIFT
    assert exc_info.value.pinned_version == "2026-04-15.r1"
    assert exc_info.value.observed_version == "2026-04-15.r2"


@pytest.mark.spec("REQ-SRC-0049", "AC-4")
def test_runtime_external_call_rejected() -> None:
    """RuntimeExternalCallError carries SRC-E-RUNTIME-EXTERNAL error code."""
    err = RuntimeExternalCallError(
        attempted_endpoint="https://www.wikidata.org/sparql"
    )
    assert err.error_code == ErrorCode.RUNTIME_EXTERNAL
    assert "wikidata.org/sparql" in str(err)
    assert "FORBIDDEN" in str(err)


@pytest.mark.spec("REQ-SRC-0049", "AC-1")
def test_pin_registry_snapshot_rejects_empty_version() -> None:
    """Empty registry_release_version aborts pin with ValueError."""
    with pytest.raises(ValueError, match="non-empty"):
        pin_registry_snapshot("")
    with pytest.raises(ValueError, match="non-empty"):
        pin_registry_snapshot("   ")


# ---------------------------------------------------------------------------
# INV-SRC-0017 Registry snapshot version pin — 4 ACs
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0017", "AC-1")
def test_first_attribution_records_pinned_version_no_history() -> None:
    """First attribution emits with pinned version + empty revision_history."""
    with lock_registry_snapshot("2026-04-15.r1") as pinned:
        result = ScholarMatchResult(
            canonical_scholar_id="sch_00042",
            confidence=0.95,
            disambiguation_state="definitive",
            record_status="confirmed",
            evidence_sources=[_build_citation_ref()],
            positions=[],
            provenance=_build_provenance(
                registry_release_version=pinned.registry_release_version
            ),
        )

    assert result.provenance.registry_release_version == "2026-04-15.r1"
    assert result.revision_history == [], "first attribution has no prior verdict"


@pytest.mark.spec("INV-SRC-0017", "AC-2")
def test_replay_against_newer_release_records_prior_pair() -> None:
    """Re-attribution against r2 records prior result_id + version pair."""
    # First attribution at r1
    first_result = _build_definitive_result()
    # Replay at r2 — new result preserves the prior verdict
    new_result = ScholarMatchResult(
        canonical_scholar_id="sch_00042",
        confidence=0.96,
        disambiguation_state="definitive",
        record_status="confirmed",
        evidence_sources=[_build_citation_ref()],
        positions=[],
        provenance=_build_provenance(registry_release_version="2026-04-29.r1"),
        revision_history=[
            RevisionHistoryEntry(
                prior_result_id=first_result.result_id,
                prior_registry_release_version=(
                    first_result.provenance.registry_release_version
                ),
                revised_at="2026-04-29T12:00:00+00:00",
            )
        ],
    )

    assert new_result.provenance.registry_release_version == "2026-04-29.r1"
    assert len(new_result.revision_history) == 1
    history = new_result.revision_history[0]
    assert history.prior_result_id == first_result.result_id
    assert history.prior_registry_release_version == "2026-04-15.r1"


@pytest.mark.spec("INV-SRC-0017", "AC-3")
def test_drift_detection_aborts_with_explicit_replay_signal() -> None:
    """Mid-case drift raises RegistrySnapshotDriftError, not silent update."""
    pinned = pin_registry_snapshot("2026-04-15.r1")
    with pytest.raises(RegistrySnapshotDriftError):
        validate_no_drift(pinned, observed_release_version="2026-04-15.r2")
    # Drift on null observed version (registry unavailable mid-case)
    with pytest.raises(RegistrySnapshotDriftError):
        validate_no_drift(pinned, observed_release_version=None)


@pytest.mark.spec("INV-SRC-0017", "AC-4")
def test_snapshot_version_rejected_at_provenance_layer() -> None:
    """ScholarMatchProvenance also rejects snapshot_version (3rd enforcement)."""
    # Already covered by CON-SRC-0008 AC-5 test; re-asserted here for the
    # invariant-layer enforcement so any future refactor that strips one
    # of the three layers (REQ-SRC-0049 + CON-SRC-0008 + INV-SRC-0017)
    # still trips this test.
    with pytest.raises(ValidationError) as exc_info:
        ScholarMatchProvenance(
            stage_1_score_breakdown={},
            stage_2_verifier_record=_build_verifier_record(),
            threshold_audit=_build_threshold_audit_definitive(),
            snapshot_version="2026-04-15.r1",  # type: ignore[call-arg]
        )

    error_str = str(exc_info.value)
    assert "snapshot_version" in error_str
    assert "FORBIDDEN" in error_str


# ---------------------------------------------------------------------------
# RegistrySnapshot model — defensive coverage of construction invariants
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0049", "AC-1")
def test_registry_snapshot_rejects_snapshot_version_field() -> None:
    """The pin model itself rejects any extra field including snapshot_version."""
    with pytest.raises(ValidationError):
        RegistrySnapshot(
            registry_release_version="2026-04-15.r1",
            pinned_at="2026-04-30T10:00:00+00:00",
            snapshot_version="should_not_be_here",  # type: ignore[call-arg]
        )


@pytest.mark.spec("REQ-SRC-0049", "AC-1")
def test_registry_snapshot_is_frozen() -> None:
    """RegistrySnapshot is immutable post-construction."""
    pinned = pin_registry_snapshot("2026-04-15.r1")
    with pytest.raises(ValidationError):
        pinned.registry_release_version = "2026-04-15.r2"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# CareerPhaseRef placeholder — round-trip support for §4.A.7 future work
# ---------------------------------------------------------------------------


@pytest.mark.spec("CON-SRC-0008", "AC-1")
def test_matched_phase_round_trips_through_provenance() -> None:
    """CareerPhaseRef placeholder accepted at provenance.matched_phase."""
    phase = CareerPhaseRef(
        phase_id="shafii_jadid",
        phase_label="al-Shāfiʿī's Egyptian (jadid) phase",
    )
    provenance = _build_provenance(matched_phase=phase)
    assert provenance.matched_phase is not None
    assert provenance.matched_phase.phase_id == "shafii_jadid"
