"""Follow-up 29 — REQ-SRC-0048 owner_level_override deferred-validation queue.

Spec-linked tests covering AC-1..AC-6 of REQ-SRC-0048 plus the two queue-
specific blocking error paths (SRC-E-OVERRIDE-QUEUE-ABANDONED,
SRC-E-OVERRIDE-QUEUE-UNANIMOUSLY-NONAPPLICABLE) and the staleness warning
(SRC-W-OVERRIDE-QUEUE-STALE).

The queue surface lives at ``engines/source/src/override_queue.py``. The test
file exercises the pure-function API (per Codex follow-up-29 review MED-4):

- ``create_pending_level_override(...)`` builds a QUEUED record.
- ``resolve_pending_level_override(record, *, resolved_genre, ...)`` produces
  an ``OverrideQueueResolution`` with the resolved (level, level_status,
  level_provenance) triple plus any ``error_code`` / ``warning_codes`` /
  ``triggered_axis`` info.
- ``abandon_pending_level_override(record, *, reason)`` produces an ABANDONED
  resolution carrying the SRC-E-OVERRIDE-QUEUE-ABANDONED error code.
- ``apply_override_queue_resolution(metadata, resolution)`` performs the
  atomic three-field swap on SourceMetadata via ``model_copy(update=...)``;
  raises ``SourceEngineError`` if ``resolution.error_code`` is set.

Cross-evaluator amendments applied:
- AC-3 deferred path RAISES ``SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE`` rather than
  recording audit-only, per Gemini Run A Q2.2 (bayān principle).
- ``dispute_snapshot`` reuses ``GenreDisputePosition`` to preserve full
  ``supporting_evidence`` for synthesis-engine consumption, per Codex HIGH-2
  and Gemini Run B DIM1 (iʿtibār discipline).
- ``MetadataDeliberationResult`` and ``NormalizationHandoffBundle`` carry the
  queued record across the handoff boundary, per Codex HIGH-1.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from engines.source.contracts import (
    ErrorCode,
    Genre,
    GenreDisputePosition,
    GenreResolutionState,
    HadithSubgenre,
    LevelProvenance,
    LevelStatus,
    MetadataDeliberationResult,
    NormalizationHandoffBundle,
    OverrideQueueAuditEntry,
    OverrideQueueState,
    PendingLevelOverride,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TrustTier,
    WarningCode,
    WorkLevel,
)
from engines.source.src.errors import SourceEngineError
from engines.source.src.override_queue import (
    DEFAULT_STALENESS_WINDOW_HOURS,
    abandon_pending_level_override,
    apply_override_queue_resolution,
    create_pending_level_override,
    resolve_pending_level_override,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _utc_iso(year: int = 2026, month: int = 4, day: int = 26, hour: int = 12) -> str:
    """Return a deterministic ISO 8601 UTC timestamp for tests."""
    return datetime(year, month, day, hour, 0, 0, tzinfo=timezone.utc).isoformat()


def _later_iso(base_iso: str, *, hours: int = 1) -> str:
    """Add `hours` to an ISO 8601 UTC timestamp."""
    base = datetime.fromisoformat(base_iso)
    return (base + timedelta(hours=hours)).isoformat()


def _build_pending_override(
    *,
    source_id: str = "src_followup29_test",
    raw_token: str = "mutawassiṭ",
    validated_value: WorkLevel = WorkLevel.MUTAWASSIT,
    genre_resolution_state: GenreResolutionState = GenreResolutionState.UNRESOLVED,
    queued_at: str | None = None,
) -> PendingLevelOverride:
    """Helper for AC-1: construct a queued override record at intake.

    Wraps ``create_pending_level_override`` so individual tests can override
    just the field they care about.
    """
    return create_pending_level_override(
        source_id=source_id,
        raw_token=raw_token,
        validated_value=validated_value,
        genre_resolution_state=genre_resolution_state,
        queued_at=queued_at or _utc_iso(),
    )


def _build_intermediate_metadata(
    *,
    source_id: str = "src_followup29_test",
    genre: Genre | None = Genre.RISALAH,
    composite_work_type: str | None = None,
    is_multi_layer: bool = False,
) -> SourceMetadata:
    """Helper: build a SourceMetadata in pending_synthesis state for AC tests."""
    return SourceMetadata(
        source_id=source_id,
        title_arabic="كتاب الاختبار",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp=_utc_iso(),
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="accepted",
        science_scope=["fiqh"],
        genre=genre,
        is_multi_layer=is_multi_layer,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
        death_date_hijri=None,
        level=None,
        level_status=LevelStatus.PENDING_SYNTHESIS,
        level_provenance=None,
        composite_work_type=composite_work_type,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# AC-1 — queueing on unresolved genre at intake
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "AC-1")
def test_req_src_0048_ac1_queue_on_unresolved_genre() -> None:
    """An override at intake with unresolved genre is queued, not applied.

    REQ-SRC-0048 AC-1: source submitted with owner_level_override="mutawassiṭ"
    where metadata deliberation has not yet emitted a genre classification at
    the moment of intake. The override is queued with provenance=
    "owner_override_deferred", interim SourceMetadata emits level=null and
    level_status="pending_synthesis", and intake_analysis completes without
    blocking on genre resolution.
    """
    queued_at = _utc_iso()
    record = create_pending_level_override(
        source_id="src_ac1",
        raw_token="mutawassiṭ",
        validated_value=WorkLevel.MUTAWASSIT,
        genre_resolution_state=GenreResolutionState.UNRESOLVED,
        queued_at=queued_at,
    )

    # The record carries the validated value byte-exactly.
    assert record.source_id == "src_ac1"
    assert record.raw_token == "mutawassiṭ"
    assert record.validated_value is WorkLevel.MUTAWASSIT
    assert record.validated_value.value == "mutawassiṭ"
    # Byte-exact diacritic preservation (CON-SRC-0011 U+1E6D ṭ).
    assert "ṭ" in record.raw_token
    assert record.queued_at == queued_at
    assert (
        record.genre_resolution_state_at_queueing is GenreResolutionState.UNRESOLVED
    )
    assert record.state is OverrideQueueState.QUEUED
    assert record.resolved_at is None
    assert record.dispute_snapshot == []

    # Audit trail records the queueing event with provenance frozen to the
    # spec literal.
    assert len(record.audit_trail) == 1
    audit = record.audit_trail[0]
    assert audit.transition is OverrideQueueState.QUEUED
    assert audit.provenance == "owner_override_deferred"
    assert audit.timestamp == queued_at
    assert audit.raw_token == "mutawassiṭ"
    assert audit.validated_value is WorkLevel.MUTAWASSIT
    assert audit.genre_resolution_state is GenreResolutionState.UNRESOLVED


@pytest.mark.spec("REQ-SRC-0048", "AC-1")
def test_req_src_0048_ac1_interim_metadata_pending_synthesis() -> None:
    """The interim SourceMetadata emits level=null + level_status=pending_synthesis.

    AC-1: while the override is queued, intake's interim SourceMetadata
    surface emits ``level=null`` and ``level_status="pending_synthesis"`` —
    standard CON-SRC-0004 invariant 2 + invariant 3 on a leveled-genre source
    awaiting resolution.
    """
    metadata = _build_intermediate_metadata(genre=Genre.RISALAH)
    assert metadata.level is None
    assert metadata.level_status is LevelStatus.PENDING_SYNTHESIS
    assert metadata.level_provenance is None


# ---------------------------------------------------------------------------
# AC-2 — apply on leveled-genre resolution with no axis firing
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "AC-2")
def test_req_src_0048_ac2_apply_on_leveled_resolution() -> None:
    """Genre resolves to a leveled genre with no axis firing → override applied.

    AC-2: when metadata deliberation subsequently resolves genre="sharh"
    (leveled, NOT in Axis 1) and composite_work_type=None (Axis 2 does not
    fire), the queued override is applied: SourceMetadata.level updated to
    "mutawassiṭ", level_status updated to "assigned", audit-trail entry
    records the applied-on-resolution event with both queued_at and
    resolved_at.
    """
    queued_at = _utc_iso(hour=10)
    resolved_at = _later_iso(queued_at, hours=2)
    record = _build_pending_override(queued_at=queued_at)

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.SHARH,
        composite_work_type=None,
        genre_dispute=None,
        resolved_at=resolved_at,
    )

    assert resolution.outcome_state is OverrideQueueState.APPLIED
    assert resolution.resolved_level is WorkLevel.MUTAWASSIT
    assert resolution.resolved_level_status is LevelStatus.ASSIGNED
    assert resolution.resolved_level_provenance is LevelProvenance.OWNER_OVERRIDE
    assert resolution.error_code is None
    assert resolution.error_detail is None
    assert resolution.triggered_axis is None
    assert WarningCode.OVERRIDE_QUEUE_STALE not in resolution.warning_codes

    # The record's audit trail now carries QUEUED + APPLIED entries.
    audit_states = [entry.transition for entry in resolution.record.audit_trail]
    assert audit_states == [OverrideQueueState.QUEUED, OverrideQueueState.APPLIED]
    assert resolution.record.state is OverrideQueueState.APPLIED
    assert resolution.record.resolved_at == resolved_at


@pytest.mark.spec("REQ-SRC-0048", "AC-2")
def test_req_src_0048_ac2_apply_helper_swaps_metadata_atomically() -> None:
    """``apply_override_queue_resolution`` performs the atomic 3-field swap.

    Codex MED-5: the (level, level_status, level_provenance) triple must be
    swapped via ``model_copy(update=...)`` — sequential mutation under
    ``validate_assignment=True`` would trip CON-SRC-0004 invariants mid-
    transition.
    """
    queued_at = _utc_iso(hour=10)
    record = _build_pending_override(queued_at=queued_at)
    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.SHARH,
        composite_work_type=None,
        resolved_at=_later_iso(queued_at, hours=2),
    )

    metadata = _build_intermediate_metadata(genre=Genre.SHARH)
    updated = apply_override_queue_resolution(metadata, resolution)

    assert updated.level is WorkLevel.MUTAWASSIT
    assert updated.level_status is LevelStatus.ASSIGNED
    assert updated.level_provenance is LevelProvenance.OWNER_OVERRIDE
    # Genre and other upstream metadata preserved (D-023).
    assert updated.genre is Genre.SHARH
    assert updated.title_arabic == metadata.title_arabic
    assert updated.science_scope == metadata.science_scope
    # Original metadata is unmutated (model_copy returns a new model).
    assert metadata.level is None
    assert metadata.level_status is LevelStatus.PENDING_SYNTHESIS


# ---------------------------------------------------------------------------
# AC-3 — reject on Axis-1 / Axis-2 firing (RAISES per Run A Q2.2)
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "AC-3")
def test_req_src_0048_ac3_reject_on_axis1_mushaf_resolution() -> None:
    """Genre resolves to Axis-1 member (mushaf) → override rejected with
    SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE.

    AC-3: when metadata deliberation resolves genre="mushaf" (Axis 1
    non-applicable), the queued override is rejected via the REQ-SRC-0047
    AC-3 path. Per Gemini Run A Q2.2 (bayān principle): the rejection MUST
    raise loudly so the owner-facing UI can surface the correction; silent
    audit-only would fail the "errors fail loudly" project rule.
    """
    queued_at = _utc_iso()
    record = _build_pending_override(
        raw_token="mubtadiʾ",
        validated_value=WorkLevel.MUBTADI,
        queued_at=queued_at,
    )

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.MUSHAF,
        composite_work_type=None,
        resolved_at=_later_iso(queued_at, hours=1),
    )

    assert resolution.outcome_state is OverrideQueueState.REJECTED_NONAPPLICABLE
    assert resolution.resolved_level is None
    assert resolution.resolved_level_status is LevelStatus.NON_APPLICABLE_REFERENCE
    assert resolution.resolved_level_provenance is None
    assert resolution.error_code is ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE
    assert resolution.error_detail is not None
    assert "Axis 1" in resolution.error_detail
    assert "mushaf" in resolution.error_detail
    assert resolution.triggered_axis == "genre"

    # Audit trail captures the QUEUED + REJECTED transitions.
    audit_states = [entry.transition for entry in resolution.record.audit_trail]
    assert audit_states == [
        OverrideQueueState.QUEUED,
        OverrideQueueState.REJECTED_NONAPPLICABLE,
    ]


@pytest.mark.spec("REQ-SRC-0048", "AC-3")
def test_req_src_0048_ac3_reject_on_axis2_majmu_resolution() -> None:
    """composite_work_type='majmu' → override rejected with axis 2 cited.

    AC-3 + INV-SRC-0012 Axis 2: when the resolved genre is leveled (e.g.
    risalah) but composite_work_type='majmu' fires Axis 2, the override
    is rejected.
    """
    queued_at = _utc_iso()
    record = _build_pending_override(
        raw_token="mutawassiṭ",
        validated_value=WorkLevel.MUTAWASSIT,
        queued_at=queued_at,
    )

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.RISALAH,
        composite_work_type="majmu",
        resolved_at=_later_iso(queued_at, hours=1),
    )

    assert resolution.outcome_state is OverrideQueueState.REJECTED_NONAPPLICABLE
    assert resolution.error_code is ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE
    assert resolution.triggered_axis == "composite"
    assert resolution.error_detail is not None
    assert "Axis 2" in resolution.error_detail
    assert "majmu" in resolution.error_detail


@pytest.mark.spec("REQ-SRC-0048", "AC-3")
def test_req_src_0048_ac3_hadith_collection_arbain_applies() -> None:
    """ARBAIN carve-back via the queue path: APPLIED outcome.

    INV-SRC-0012 Axis 3 carve-back: hadith_collection + ARBAIN = pedagogical;
    the queued owner_level_override is applied per Phase 5b item 23
    closure 2026-04-26. The 3-of-3 evaluator wave confirmed this path
    (al-Kattānī, *al-Risālah al-Mustaṭrafah* p. 69-72; Codex CRITICAL
    DIM4 BLOCK on ARBAIN-overload — addressed by single-value carve-back set).
    """
    queued_at = _utc_iso()
    record = _build_pending_override(
        raw_token="mubtadiʾ",
        validated_value=WorkLevel.MUBTADI,
        queued_at=queued_at,
    )

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.HADITH_COLLECTION,
        hadith_subgenre=HadithSubgenre.ARBAIN,
        resolved_at=_later_iso(queued_at, hours=1),
    )

    assert resolution.outcome_state is OverrideQueueState.APPLIED
    assert resolution.resolved_level is WorkLevel.MUBTADI
    assert resolution.resolved_level_status is LevelStatus.ASSIGNED
    assert resolution.resolved_level_provenance is LevelProvenance.OWNER_OVERRIDE
    assert resolution.triggered_axis is None
    assert resolution.error_code is None


@pytest.mark.spec("REQ-SRC-0048", "AC-3")
def test_req_src_0048_ac3_hadith_collection_musnad_rejects_on_axis3() -> None:
    """Transmission subgenre via the queue path: REJECTED with Axis 3 citation.

    Musnad Aḥmad: hadith_subgenre=MUSNAD is in the transmission set;
    the queue rejects the override and surfaces the Axis 3 citation
    in the error_detail per Codex DIM5 amendment.
    """
    queued_at = _utc_iso()
    record = _build_pending_override(
        raw_token="muntahī",
        validated_value=WorkLevel.MUNTAHI,
        queued_at=queued_at,
    )

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.HADITH_COLLECTION,
        hadith_subgenre=HadithSubgenre.MUSNAD,
        resolved_at=_later_iso(queued_at, hours=1),
    )

    assert resolution.outcome_state is OverrideQueueState.REJECTED_NONAPPLICABLE
    assert resolution.error_code is ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE
    assert resolution.triggered_axis == "hadith_subgenre"
    assert resolution.error_detail is not None
    assert "Axis 3" in resolution.error_detail
    assert "musnad" in resolution.error_detail
    assert "كُتُب الرِّوَايَة" in resolution.error_detail


@pytest.mark.spec("REQ-SRC-0048", "AC-3")
def test_req_src_0048_ac3_hadith_collection_unknown_subgenre_rejects_on_axis3() -> None:
    """Path A safeguard: hadith_subgenre=None on hadith_collection still fires Axis 3.

    Default-None behavior per the *iḥtiyāṭ* / *tawaqquf* principle (3-of-3
    evaluator wave; Ibn Ḥajar, *Nuzhat al-Naẓar*; al-Suyūṭī, *Tadrīb al-
    Rāwī*): silence defaults to transmission-by-default. The queue must
    reject the override even when no explicit subgenre is asserted.
    """
    queued_at = _utc_iso()
    record = _build_pending_override(
        raw_token="muntahī",
        validated_value=WorkLevel.MUNTAHI,
        queued_at=queued_at,
    )

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.HADITH_COLLECTION,
        hadith_subgenre=None,
        resolved_at=_later_iso(queued_at, hours=1),
    )

    assert resolution.outcome_state is OverrideQueueState.REJECTED_NONAPPLICABLE
    assert resolution.error_code is ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE
    assert resolution.triggered_axis == "hadith_subgenre"
    assert resolution.error_detail is not None
    assert "Axis 3" in resolution.error_detail


@pytest.mark.spec("REQ-SRC-0048", "AC-3")
def test_req_src_0048_ac3_apply_helper_raises_on_rejection() -> None:
    """``apply_override_queue_resolution`` raises SourceEngineError on AC-3 path.

    Per Run A Q2.2 (bayān): the rejection must be communicated with the
    same force as the synchronous REQ-SRC-0047 AC-3 path, not silently
    audited. The helper raises after the audit-trail entry has been
    appended, so audit history remains complete on the persisted record.
    """
    queued_at = _utc_iso()
    record = _build_pending_override(queued_at=queued_at)
    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.MUSHAF,
        resolved_at=_later_iso(queued_at, hours=1),
    )
    metadata = _build_intermediate_metadata(genre=Genre.MUSHAF)

    with pytest.raises(SourceEngineError) as excinfo:
        apply_override_queue_resolution(metadata, resolution)

    assert excinfo.value.error_code is ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE
    assert "mushaf" in str(excinfo.value)
    assert "Axis 1" in str(excinfo.value)


# ---------------------------------------------------------------------------
# AC-4 — defer on genre_dispute
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "AC-4")
def test_req_src_0048_ac4_defer_on_genre_dispute() -> None:
    """genre_dispute → queue stays queued, dispute snapshot captured.

    AC-4: when metadata deliberation resolves with genre_dispute (two agents
    propose "risalah" leveled, third proposes "mushaf" non-applicable, no
    consensus), the queued override remains queued (not applied, not
    rejected), level_status stays pending_synthesis, audit trail captures
    the per-agent dispute, and the handoff payload to normalization carries
    the queued-override record so the synthesis engine can consume it.
    """
    queued_at = _utc_iso()
    record = _build_pending_override(queued_at=queued_at)

    dispute = [
        GenreDisputePosition(
            genre_candidate=Genre.RISALAH,
            supporting_evidence=[
                "أسلوب الكتاب رسالة قصيرة في مسألة فقهية",
                "العنوان يصرح بأنه رسالة",
            ],
            confidence=0.78,
            source_agents=["genre_agent_a", "genre_agent_b"],
        ),
        GenreDisputePosition(
            genre_candidate=Genre.MUSHAF,
            supporting_evidence=["النسخة الورقية تحتوي على آيات مؤطرة"],
            confidence=0.42,
            source_agents=["genre_agent_c"],
        ),
    ]

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=None,
        composite_work_type=None,
        genre_dispute=dispute,
        resolved_at=_later_iso(queued_at, hours=3),
    )

    assert resolution.outcome_state is OverrideQueueState.DEFERRED_TO_SYNTHESIS
    assert resolution.resolved_level is None
    assert resolution.resolved_level_status is LevelStatus.PENDING_SYNTHESIS
    assert resolution.resolved_level_provenance is None
    assert resolution.error_code is None

    # The dispute snapshot is preserved verbatim (Run B DIM1 + Codex HIGH-2:
    # supporting_evidence MUST survive so synthesis can perform iʿtibār).
    assert resolution.record.dispute_snapshot == dispute
    # Each position's supporting_evidence retains all entries byte-exactly.
    assert resolution.record.dispute_snapshot[0].supporting_evidence == [
        "أسلوب الكتاب رسالة قصيرة في مسألة فقهية",
        "العنوان يصرح بأنه رسالة",
    ]
    assert resolution.record.dispute_snapshot[1].supporting_evidence == [
        "النسخة الورقية تحتوي على آيات مؤطرة"
    ]

    audit_states = [entry.transition for entry in resolution.record.audit_trail]
    assert audit_states == [
        OverrideQueueState.QUEUED,
        OverrideQueueState.DEFERRED_TO_SYNTHESIS,
    ]
    audit_deferred = resolution.record.audit_trail[-1]
    assert audit_deferred.genre_resolution_state is GenreResolutionState.DISPUTED


@pytest.mark.spec("REQ-SRC-0048", "AC-4")
def test_req_src_0048_ac4_handoff_carries_pending_override() -> None:
    """The persisted handoff bundle carries the pending_level_override record.

    Per Codex follow-up-29 review HIGH-1: REQ-SRC-0048 AC-4 explicitly says
    "the handoff payload to normalization carries the queued-override record".
    The MetadataDeliberationResult and NormalizationHandoffBundle therefore
    expose ``pending_level_override`` so the synthesis engine inherits the
    full record (state, audit trail, dispute snapshot).
    """
    queued_at = _utc_iso()
    record = _build_pending_override(queued_at=queued_at)
    dispute = [
        GenreDisputePosition(
            genre_candidate=Genre.RISALAH,
            supporting_evidence=["دليل أ"],
            confidence=0.6,
            source_agents=["agent_a"],
        ),
        GenreDisputePosition(
            genre_candidate=Genre.MUSHAF,
            supporting_evidence=["دليل ب"],
            confidence=0.4,
            source_agents=["agent_b"],
        ),
    ]
    resolution = resolve_pending_level_override(
        record,
        resolved_genre=None,
        genre_dispute=dispute,
        resolved_at=_later_iso(queued_at, hours=2),
    )
    persisted = resolution.record
    assert persisted.state is OverrideQueueState.DEFERRED_TO_SYNTHESIS
    assert MetadataDeliberationResult.model_fields["pending_level_override"] is not None
    assert NormalizationHandoffBundle.model_fields["pending_level_override"] is not None

    # Round-trip through model_dump(mode="json") preserves the persisted shape
    # the synthesis engine reads.
    dumped = persisted.model_dump(mode="json")
    assert dumped["state"] == "deferred_to_synthesis"
    assert dumped["dispute_snapshot"][0]["supporting_evidence"] == ["دليل أ"]
    assert dumped["audit_trail"][-1]["transition"] == "deferred_to_synthesis"
    assert dumped["audit_trail"][-1]["provenance"] == "owner_override_deferred"


# ---------------------------------------------------------------------------
# AC-5 — bypass when genre is already resolved at intake
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "AC-5")
def test_req_src_0048_ac5_synchronous_path_bypasses_queue() -> None:
    """When genre is resolved at intake, REQ-SRC-0047 sync path runs; queue is bypassed.

    AC-5: a source submitted with owner_level_override="mubtadiʾ" where
    metadata deliberation has ALREADY completed (genre="sharh",
    composite_work_type=null) at the moment of intake — the standard
    REQ-SRC-0047 path. No pending-override record is created, no
    "pending_synthesis" transition is emitted, and SourceMetadata emits
    level="mubtadiʾ" with level_status="assigned" directly via the
    synchronous resolver.
    """
    from engines.source.contracts import MetadataDeliberationInput
    from engines.source.src.deliberation import _resolve_level_fields

    request = MetadataDeliberationInput(
        source_id="src_ac5",
        title_arabic="شرح الورقات",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        acquisition_path="manual",
        frozen_path="library/sources/src_ac5/frozen",
        frozen_hash="b" * 64,
        frozen_file_hashes={"book.htm": "b" * 64},
        status="source_engine_accepted",
        science_scope=["usul_al_fiqh"],
        genre=Genre.SHARH,
        is_multi_layer=False,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        level=WorkLevel.MUBTADI,
        level_status=None,
        level_provenance=None,
        composite_work_type=None,
        author_positions=[],
        owner_hint_payload={},
        verification_agents=["agent_a", "agent_b"],
        research_source_types=["metadata_card"],
        author_death_hijri=None,
    )

    level, status, provenance = _resolve_level_fields(request)

    # Synchronous REQ-SRC-0047 path produces the assigned triple directly.
    assert level is WorkLevel.MUBTADI
    assert status is LevelStatus.ASSIGNED
    assert provenance is LevelProvenance.OWNER_OVERRIDE


# ---------------------------------------------------------------------------
# AC-6 — staleness warning when window elapsed
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "AC-6")
def test_req_src_0048_ac6_stale_warning_on_apply_path() -> None:
    """Staleness window elapsed → SRC-W-OVERRIDE-QUEUE-STALE warning emitted.

    AC-6: when (resolved_at - queued_at) exceeds the staleness window
    (default 48h), the override is still applied/rejected per the resolved
    genre, but SRC-W-OVERRIDE-QUEUE-STALE is emitted as a warning and the
    audit-trail entry marks the override as applied-after-stale-window.

    Default staleness window matches REQ-SRC-0048 spec verbatim (48h). A
    SPEC_AMENDMENT_REQUESTED tracker (Run B DIM3) considers extending to 168h
    for Zarnūjī's tawaqquf principle; not applied here.
    """
    queued_at = _utc_iso(hour=10)
    stale_resolved_at = _later_iso(
        queued_at, hours=DEFAULT_STALENESS_WINDOW_HOURS + 2
    )
    record = _build_pending_override(queued_at=queued_at)

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.SHARH,
        composite_work_type=None,
        resolved_at=stale_resolved_at,
    )

    assert resolution.outcome_state is OverrideQueueState.APPLIED
    assert resolution.resolved_level is WorkLevel.MUTAWASSIT
    assert WarningCode.OVERRIDE_QUEUE_STALE in resolution.warning_codes


@pytest.mark.spec("REQ-SRC-0048", "AC-6")
def test_req_src_0048_ac6_stale_warning_also_on_reject_path() -> None:
    """Stale window also fires on the AC-3 reject path (per spec text)."""
    queued_at = _utc_iso(hour=10)
    stale_resolved_at = _later_iso(
        queued_at, hours=DEFAULT_STALENESS_WINDOW_HOURS + 1
    )
    record = _build_pending_override(queued_at=queued_at)

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.MUSHAF,
        resolved_at=stale_resolved_at,
    )

    assert resolution.outcome_state is OverrideQueueState.REJECTED_NONAPPLICABLE
    assert resolution.error_code is ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE
    assert WarningCode.OVERRIDE_QUEUE_STALE in resolution.warning_codes


@pytest.mark.spec("REQ-SRC-0048", "AC-6")
def test_req_src_0048_ac6_no_stale_within_window() -> None:
    """Resolution within the staleness window emits no STALE warning."""
    queued_at = _utc_iso(hour=10)
    in_window_resolved_at = _later_iso(
        queued_at, hours=DEFAULT_STALENESS_WINDOW_HOURS - 1
    )
    record = _build_pending_override(queued_at=queued_at)

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.SHARH,
        resolved_at=in_window_resolved_at,
    )

    assert WarningCode.OVERRIDE_QUEUE_STALE not in resolution.warning_codes


# ---------------------------------------------------------------------------
# Queue-specific blocking errors (non-AC paths from REQ-SRC-0048 error_conditions)
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "error_conditions")
def test_req_src_0048_unanimously_nonapplicable_dispute_rejects() -> None:
    """genre_dispute where every branch fires non-applicability → REJECTED.

    REQ-SRC-0048 error_conditions: when the dispute and queued override are
    both present but no agent-proposed genre passes the CON-SRC-0011/
    INV-SRC-0012 cross-check (every disputed genre independently fires a
    non-applicability axis), emit
    SRC-E-OVERRIDE-QUEUE-UNANIMOUSLY-NONAPPLICABLE; the override is
    rejected (consistent with REQ-SRC-0047 AC-3 path).
    """
    queued_at = _utc_iso()
    record = _build_pending_override(queued_at=queued_at)
    convergent_dispute = [
        GenreDisputePosition(
            genre_candidate=Genre.MUSHAF,
            supporting_evidence=["العنوان: المصحف الشريف"],
            confidence=0.55,
            source_agents=["agent_a"],
        ),
        GenreDisputePosition(
            genre_candidate=Genre.HADITH_COLLECTION,
            supporting_evidence=["البنية: مجموعة أحاديث"],
            confidence=0.45,
            source_agents=["agent_b"],
        ),
    ]

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=None,
        genre_dispute=convergent_dispute,
        resolved_at=_later_iso(queued_at, hours=2),
    )

    assert resolution.outcome_state is OverrideQueueState.REJECTED_NONAPPLICABLE
    assert (
        resolution.error_code
        is ErrorCode.OVERRIDE_QUEUE_UNANIMOUSLY_NONAPPLICABLE
    )
    assert resolution.resolved_level is None
    assert resolution.resolved_level_status is LevelStatus.NON_APPLICABLE_REFERENCE
    assert resolution.resolved_level_provenance is None
    # The dispute snapshot is still preserved verbatim for synthesis (it must
    # remain even though the source engine rejected — the audit chain must
    # carry every evaluator's bayyinah).
    assert resolution.record.dispute_snapshot == convergent_dispute


@pytest.mark.spec("REQ-SRC-0048", "error_conditions")
def test_req_src_0048_abandoned_on_intake_close() -> None:
    """Intake closes without genre resolving → ABANDONED state.

    REQ-SRC-0048 error_conditions: when intake_analysis closes without genre
    ever resolving (upstream metadata deliberation timed out or failed
    permanently) AND no genre_dispute was recorded, emit
    SRC-E-OVERRIDE-QUEUE-ABANDONED. The queued record is not lost
    (persisted in the audit trail with the timeout reason);
    SourceMetadata.level_status stays "pending_synthesis" so synthesis can
    consume the queued record when it resumes determination.
    """
    queued_at = _utc_iso()
    record = _build_pending_override(queued_at=queued_at)
    abandon_at = _later_iso(queued_at, hours=12)

    resolution = abandon_pending_level_override(
        record,
        reason="metadata deliberation timed out",
        timestamp=abandon_at,
    )

    assert resolution.outcome_state is OverrideQueueState.ABANDONED
    assert resolution.error_code is ErrorCode.OVERRIDE_QUEUE_ABANDONED
    assert "timed out" in (resolution.error_detail or "")
    # SourceMetadata.level_status remains pending_synthesis; the queued
    # record is preserved for synthesis to consume.
    assert resolution.resolved_level is None
    assert resolution.resolved_level_status is LevelStatus.PENDING_SYNTHESIS
    assert resolution.resolved_level_provenance is None

    audit_states = [entry.transition for entry in resolution.record.audit_trail]
    assert audit_states == [OverrideQueueState.QUEUED, OverrideQueueState.ABANDONED]


# ---------------------------------------------------------------------------
# Audit-trail structure invariants (cross-cutting)
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "audit_trail")
def test_req_src_0048_audit_trail_provenance_constant() -> None:
    """Audit-trail provenance is the frozen literal "owner_override_deferred".

    Spec says provenance="owner_override_deferred" verbatim. A
    SPEC_AMENDMENT_REQUESTED (Run B DIM2) tracks possible future rename to
    owner_override_pending_genre_resolution; not applied here.
    """
    record = _build_pending_override()
    for entry in record.audit_trail:
        assert entry.provenance == "owner_override_deferred"


@pytest.mark.spec("REQ-SRC-0048", "audit_trail")
def test_req_src_0048_audit_trail_extra_fields_forbidden() -> None:
    """OverrideQueueAuditEntry forbids extra fields (Codex LOW-8)."""
    with pytest.raises(ValidationError):
        OverrideQueueAuditEntry(  # type: ignore[call-arg]
            transition=OverrideQueueState.QUEUED,
            timestamp=_utc_iso(),
            raw_token="mubtadiʾ",
            validated_value=WorkLevel.MUBTADI,
            genre_resolution_state=GenreResolutionState.UNRESOLVED,
            unexpected_field="value",  # type: ignore[arg-type]
        )


@pytest.mark.spec("REQ-SRC-0048", "audit_trail")
def test_req_src_0048_pending_override_extra_fields_forbidden() -> None:
    """PendingLevelOverride forbids extra fields (Codex LOW-8)."""
    with pytest.raises(ValidationError):
        PendingLevelOverride(  # type: ignore[call-arg]
            source_id="src_test",
            raw_token="mubtadiʾ",
            validated_value=WorkLevel.MUBTADI,
            queued_at=_utc_iso(),
            genre_resolution_state_at_queueing=GenreResolutionState.UNRESOLVED,
            unexpected_field="value",  # type: ignore[arg-type]
        )


@pytest.mark.spec("REQ-SRC-0048", "audit_trail")
def test_req_src_0048_audit_trail_append_only_on_transition() -> None:
    """Each transition appends to the audit trail; existing entries are preserved."""
    queued_at = _utc_iso()
    record = _build_pending_override(queued_at=queued_at)
    initial_audit_count = len(record.audit_trail)
    assert initial_audit_count == 1
    initial_audit = record.audit_trail[0]

    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.SHARH,
        resolved_at=_later_iso(queued_at, hours=1),
    )

    # The original QUEUED entry is preserved byte-exactly; the APPLIED entry
    # is appended (not replacing) — D-023 metadata-preservation discipline.
    assert resolution.record.audit_trail[0] == initial_audit
    assert len(resolution.record.audit_trail) == initial_audit_count + 1


# ---------------------------------------------------------------------------
# D-023 metadata preservation (cross-cutting)
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "d023")
def test_req_src_0048_apply_preserves_upstream_metadata() -> None:
    """``apply_override_queue_resolution`` does not delete any upstream field.

    D-023: every transform passes through ALL upstream metadata. Apply only
    swaps the (level, level_status, level_provenance) triple atomically.
    """
    queued_at = _utc_iso()
    record = _build_pending_override(queued_at=queued_at)
    resolution = resolve_pending_level_override(
        record,
        resolved_genre=Genre.SHARH,
        resolved_at=_later_iso(queued_at, hours=1),
    )

    metadata = _build_intermediate_metadata(genre=Genre.SHARH)
    before_dump = metadata.model_dump(mode="json")
    after = apply_override_queue_resolution(metadata, resolution)
    after_dump = after.model_dump(mode="json")

    # Only the three level fields change.
    changed_fields = {
        key
        for key in before_dump
        if before_dump[key] != after_dump.get(key)
    }
    assert changed_fields == {"level", "level_status", "level_provenance"}
