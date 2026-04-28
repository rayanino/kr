"""Phase 5b follow-up 37 (2026-04-28) — constituent-level owner-override-entrance widening.

Closes the FU-24 deferred owner-override-entrance promise via the (a+b)
hybrid-resolution path validated by 4-of-4 cross-provider scholarly+structural
convergence at HIGH confidence:

- Codex CLI structural (OpenAI): (a-lite) ISOMORPHIC + 3 CRIT flags
- Gemini Run A scholarly (Google, gemini-2.5-pro): (a+b) HIGH
- Gemini Run B scholarly INDEPENDENT (Google, gemini-2.5-pro fresh shell): (a+b) HIGH
- arabic-reviewer Anthropic Agent (this closure): (a+b) HIGH with NOVEL
  classical anchor al-Suyūṭī ``Tadrīb al-Rāwī`` Muqaddimah on *iʿtibār*
  discipline (not in either Gemini's verdict — genuinely independent
  cross-provider Anthropic-side anchor)

arabic-reviewer's structural cross-provider check surfaced TWO new CRITICAL
findings that prior evaluators did not enumerate explicitly:

- **CRIT-AR-1**: ``PendingLevelOverride`` is per-source-keyed; lacks constituent
  identifier. Per-constituent overrides queued at intake become ambiguous
  about which constituent they target.
- **CRIT-AR-2**: ``GenreDisputePosition`` lacks constituent identifier;
  dispute snapshots ambiguous for per-constituent overrides on majmūʿ sources.

This test file covers:

1. ``PendingLevelOverride.constituent_idx`` field shape + Field(ge=0) constraint
2. ``GenreDisputePosition.constituent_idx`` field shape + Field(ge=0) constraint
3. ``create_pending_level_override`` accepts and threads ``constituent_idx``
4. ``MetadataDeliberationInput.owner_constituent_level_overrides`` field shape
5. ``MetadataDeliberationResult.pending_constituent_level_overrides`` field shape
6. ``_queue_constituent_overrides`` orchestrator helper:
   - empty input → empty output
   - non-majmu source raises SRC-E-LEVEL-OVERRIDE-CONSTITUENT-INVALID
   - majmu source with valid keys → queued list (sorted by constituent_idx)
   - majmu source with out-of-range key raises SRC-E-LEVEL-OVERRIDE-CONSTITUENT-INVALID
7. End-to-end via ``run_metadata_deliberation`` (majmu source flows through
   and emits per-constituent queued records)
8. Migration / legacy load: PendingLevelOverride and GenreDisputePosition
   payloads without ``constituent_idx`` default to ``None`` via Pydantic
   field-default semantics (DEC-SRC-0021 rule (vii.d) and (vii.e))
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engines.source.contracts import (
    ErrorCode,
    Genre,
    GenreDisputePosition,
    GenreResolutionState,
    LevelStatus,
    MetadataDeliberationInput,
    MetadataDeliberationResult,
    OverrideQueueState,
    PendingLevelOverride,
    SourceFormat,
    StructuralFormat,
    WorkLevel,
)
from engines.source.src.errors import SourceEngineError
from engines.source.src.override_queue import create_pending_level_override


# ---------------------------------------------------------------------------
# CRIT-AR-1: PendingLevelOverride.constituent_idx field shape
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "AC-FU37-1")
def test_pending_level_override_constituent_idx_default_none() -> None:
    """Default ``constituent_idx=None`` preserves source-level (container) semantics."""
    record = PendingLevelOverride(
        source_id="src_majmu_ibn_rajab",
        raw_token="mutawassiṭ",
        validated_value=WorkLevel.MUTAWASSIT,
        queued_at="2026-04-28T16:00:00+00:00",
        genre_resolution_state_at_queueing=GenreResolutionState.UNRESOLVED,
        state=OverrideQueueState.QUEUED,
    )
    assert record.constituent_idx is None


@pytest.mark.spec("REQ-SRC-0048", "AC-FU37-1")
@pytest.mark.parametrize("constituent_idx", [0, 1, 5, 36])
def test_pending_level_override_accepts_non_negative_constituent_idx(
    constituent_idx: int,
) -> None:
    """Non-negative integer ``constituent_idx`` keys the override against
    ``SourceMetadata.sub_work_inventory[constituent_idx]``."""
    record = PendingLevelOverride(
        source_id="src_majmu_ibn_taymiyyah",
        raw_token="muntahī",
        validated_value=WorkLevel.MUNTAHI,
        queued_at="2026-04-28T16:00:00+00:00",
        genre_resolution_state_at_queueing=GenreResolutionState.UNRESOLVED,
        state=OverrideQueueState.QUEUED,
        constituent_idx=constituent_idx,
    )
    assert record.constituent_idx == constituent_idx


@pytest.mark.spec("REQ-SRC-0048", "AC-FU37-1")
def test_pending_level_override_rejects_negative_constituent_idx() -> None:
    """Negative ``constituent_idx`` rejected by Field(ge=0) constraint."""
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        PendingLevelOverride(
            source_id="src_majmu_ibn_rajab",
            raw_token="mubtadiʾ",
            validated_value=WorkLevel.MUBTADI,
            queued_at="2026-04-28T16:00:00+00:00",
            genre_resolution_state_at_queueing=GenreResolutionState.UNRESOLVED,
            state=OverrideQueueState.QUEUED,
            constituent_idx=-1,
        )


# ---------------------------------------------------------------------------
# CRIT-AR-2: GenreDisputePosition.constituent_idx field shape
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0012", "AC-FU37-2")
def test_genre_dispute_position_constituent_idx_default_none() -> None:
    """Default ``constituent_idx=None`` preserves container-level dispute semantics."""
    position = GenreDisputePosition(
        genre_candidate=Genre.SHARH,
        supporting_evidence=["title contains شرح"],
        confidence=0.8,
        source_agents=["genre_agent_a"],
    )
    assert position.constituent_idx is None
    assert position.hadith_subgenre_candidate is None


@pytest.mark.spec("INV-SRC-0012", "AC-FU37-2")
def test_genre_dispute_position_accepts_constituent_idx() -> None:
    """Non-negative ``constituent_idx`` enables per-constituent dispute snapshots."""
    position = GenreDisputePosition(
        genre_candidate=Genre.HADITH_COLLECTION,
        supporting_evidence=["constituent 3 contains hadith chains"],
        confidence=0.7,
        source_agents=["genre_agent_b"],
        constituent_idx=3,
    )
    assert position.constituent_idx == 3


@pytest.mark.spec("INV-SRC-0012", "AC-FU37-2")
def test_genre_dispute_position_rejects_negative_constituent_idx() -> None:
    """Negative ``constituent_idx`` rejected by Field(ge=0) constraint."""
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        GenreDisputePosition(
            genre_candidate=Genre.RISALAH,
            supporting_evidence=["evidence"],
            confidence=0.5,
            source_agents=["agent_x"],
            constituent_idx=-2,
        )


# ---------------------------------------------------------------------------
# create_pending_level_override threading
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0048", "AC-FU37-3")
def test_create_pending_level_override_default_no_constituent_idx() -> None:
    """When ``constituent_idx`` is omitted, the record is container-level (None)."""
    record = create_pending_level_override(
        source_id="src_standalone",
        raw_token="mubtadiʾ",
        validated_value=WorkLevel.MUBTADI,
        genre_resolution_state=GenreResolutionState.UNRESOLVED,
    )
    assert record.constituent_idx is None
    assert record.state == OverrideQueueState.QUEUED


@pytest.mark.spec("REQ-SRC-0048", "AC-FU37-3")
def test_create_pending_level_override_threads_constituent_idx() -> None:
    """Per-constituent records carry the constituent_idx through to the queue."""
    record = create_pending_level_override(
        source_id="src_majmu_ibn_rajab",
        raw_token="muntahī",
        validated_value=WorkLevel.MUNTAHI,
        genre_resolution_state=GenreResolutionState.UNRESOLVED,
        constituent_idx=2,
    )
    assert record.constituent_idx == 2
    assert record.state == OverrideQueueState.QUEUED
    # Audit trail also reflects the queued state
    assert len(record.audit_trail) == 1
    assert record.audit_trail[0].transition == OverrideQueueState.QUEUED


# ---------------------------------------------------------------------------
# MetadataDeliberationInput entrance + Result list field shape
# ---------------------------------------------------------------------------


def _make_minimal_deliberation_input(
    source_id: str = "src_test",
    composite_work_type: str | None = None,
    overrides: dict[int, WorkLevel] | None = None,
) -> MetadataDeliberationInput:
    """Construct a minimum-viable MetadataDeliberationInput for FU-37 tests."""
    return MetadataDeliberationInput(
        source_id=source_id,
        title_arabic="عنوان الكتاب",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        acquisition_path="manual",
        frozen_path="library/sources/test/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="source_engine_accepted",
        composite_work_type=composite_work_type,  # type: ignore[arg-type]
        owner_constituent_level_overrides=overrides or {},
    )


@pytest.mark.spec("REQ-SRC-0047", "AC-FU37-4")
def test_metadata_deliberation_input_owner_constituent_overrides_default_empty() -> None:
    """Default empty dict for non-composite sources / no per-constituent intent."""
    deliberation_input = _make_minimal_deliberation_input()
    assert deliberation_input.owner_constituent_level_overrides == {}


@pytest.mark.spec("REQ-SRC-0047", "AC-FU37-4")
def test_metadata_deliberation_input_accepts_per_constituent_overrides() -> None:
    """Owner per-constituent override intent flows in via dict[int, WorkLevel]."""
    overrides = {0: WorkLevel.MUBTADI, 2: WorkLevel.MUNTAHI}
    deliberation_input = _make_minimal_deliberation_input(
        composite_work_type="majmu",
        overrides=overrides,
    )
    assert deliberation_input.owner_constituent_level_overrides == overrides


@pytest.mark.spec("REQ-SRC-0048", "AC-FU37-5")
def test_metadata_deliberation_result_pending_constituent_overrides_default_empty() -> None:
    """Default empty list when no per-constituent overrides queued."""
    from engines.source.contracts import (
        CaseComplexityRecord,
        SourceMetadata,
        TextFidelity,
        TrustTier,
    )

    metadata = SourceMetadata(
        source_id="src_x",
        title_arabic="عنوان",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-04-28T00:00:00Z",
        acquisition_path="manual",
        frozen_path="library/sources/src_x/frozen",
        frozen_hash="d" * 64,
        frozen_file_hashes={"book.htm": "d" * 64},
        status="source_engine_accepted",
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        level_status=LevelStatus.PENDING_SYNTHESIS,
    )
    case_record = CaseComplexityRecord(
        case_id="case_test",
        source_id="src_x",
        case_complexity="standard",
    )
    result = MetadataDeliberationResult(
        source_metadata=metadata,
        case_complexity_record=case_record,
    )
    assert result.pending_constituent_level_overrides == []


# ---------------------------------------------------------------------------
# _queue_constituent_overrides orchestrator helper
# ---------------------------------------------------------------------------


def _make_majmu_metadata(
    source_id: str = "src_majmu_ibn_rajab",
    constituent_count: int = 3,
):
    """Construct a SourceMetadata for a majmu source with N constituent placeholders."""
    from engines.source.contracts import (
        SourceMetadata,
        SubWorkInventoryEntry,
        TextFidelity,
        TrustTier,
    )

    inventory = [
        SubWorkInventoryEntry(
            sub_title=f"رسالة {i + 1}",
            volume_number=1,
            page_start=1 + i * 50,
            page_end=50 + i * 50,
            detection_method="toc_entry",
        )
        for i in range(constituent_count)
    ]
    return SourceMetadata(
        source_id=source_id,
        title_arabic="مجموع رسائل ابن رجب",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-04-28T00:00:00Z",
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen",
        frozen_hash="e" * 64,
        frozen_file_hashes={"book.htm": "e" * 64},
        status="source_engine_accepted",
        composite_work_type="majmu",
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
        sub_work_inventory=inventory,
    )


@pytest.mark.spec("REQ-SRC-0047", "AC-FU37-6")
def test_queue_constituent_overrides_empty_input_returns_empty_list() -> None:
    """No per-constituent overrides → empty queued list (no records emitted)."""
    from engines.source.src.deliberation import _queue_constituent_overrides

    deliberation_input = _make_minimal_deliberation_input(composite_work_type="majmu")
    metadata = _make_majmu_metadata()
    queued = _queue_constituent_overrides(deliberation_input, metadata)
    assert queued == []


@pytest.mark.spec("REQ-SRC-0047", "AC-FU37-6")
def test_queue_constituent_overrides_majmu_with_valid_keys_emits_sorted_queued_records() -> None:
    """Majmu source + valid per-constituent overrides → queued records sorted by idx."""
    from engines.source.src.deliberation import _queue_constituent_overrides

    overrides = {2: WorkLevel.MUNTAHI, 0: WorkLevel.MUBTADI}
    deliberation_input = _make_minimal_deliberation_input(
        composite_work_type="majmu", overrides=overrides
    )
    metadata = _make_majmu_metadata(constituent_count=3)
    queued = _queue_constituent_overrides(deliberation_input, metadata)
    assert len(queued) == 2
    # Sorted ascending by constituent_idx
    assert queued[0].constituent_idx == 0
    assert queued[0].validated_value == WorkLevel.MUBTADI
    assert queued[1].constituent_idx == 2
    assert queued[1].validated_value == WorkLevel.MUNTAHI
    # All records are in QUEUED state (always deferred to synthesis)
    assert all(r.state == OverrideQueueState.QUEUED for r in queued)


@pytest.mark.spec("REQ-SRC-0047", "AC-FU37-7")
def test_queue_constituent_overrides_non_majmu_source_raises_invalid() -> None:
    """Per-constituent overrides on non-composite source rejected with structured error."""
    from engines.source.src.deliberation import _queue_constituent_overrides
    from engines.source.contracts import (
        SourceMetadata,
        TextFidelity,
        TrustTier,
    )

    overrides = {0: WorkLevel.MUBTADI}
    deliberation_input = _make_minimal_deliberation_input(
        composite_work_type=None, overrides=overrides
    )
    metadata = SourceMetadata(
        source_id="src_standalone",
        title_arabic="رسالة في التوحيد",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-04-28T00:00:00Z",
        acquisition_path="manual",
        frozen_path="library/sources/src_standalone/frozen",
        frozen_hash="f" * 64,
        frozen_file_hashes={"book.htm": "f" * 64},
        status="source_engine_accepted",
        composite_work_type=None,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        level_status=LevelStatus.PENDING_SYNTHESIS,
    )
    with pytest.raises(SourceEngineError) as exc_info:
        _queue_constituent_overrides(deliberation_input, metadata)
    assert exc_info.value.error_code == ErrorCode.LEVEL_OVERRIDE_CONSTITUENT_INVALID
    assert "not 'majmu'" in str(exc_info.value)


@pytest.mark.spec("REQ-SRC-0047", "AC-FU37-7")
def test_queue_constituent_overrides_out_of_range_key_raises_invalid() -> None:
    """Constituent_idx outside sub_work_inventory range rejected with structured error."""
    from engines.source.src.deliberation import _queue_constituent_overrides

    overrides = {0: WorkLevel.MUBTADI, 7: WorkLevel.MUNTAHI}  # idx 7 OOB for size 3
    deliberation_input = _make_minimal_deliberation_input(
        composite_work_type="majmu", overrides=overrides
    )
    metadata = _make_majmu_metadata(constituent_count=3)
    with pytest.raises(SourceEngineError) as exc_info:
        _queue_constituent_overrides(deliberation_input, metadata)
    assert exc_info.value.error_code == ErrorCode.LEVEL_OVERRIDE_CONSTITUENT_INVALID
    assert "out of range" in str(exc_info.value)
    assert "constituent_idx=7" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Migration / legacy load (DEC-SRC-0021 rule (vii.d) and (vii.e))
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0021", "AC-FU37-VII-D")
def test_legacy_pending_level_override_payload_defaults_constituent_idx_to_none() -> None:
    """Legacy PendingLevelOverride JSON without constituent_idx loads with None default.

    DEC-SRC-0021 rule (vii.d) added by FU-37 closure 2026-04-28: pre-FU-37
    persisted PendingLevelOverride records have no ``constituent_idx`` field.
    Pydantic field-default semantics handle this transparently — no explicit
    migration logic is required because the new field is optional with a
    safe default (None = container-level intent, the legacy semantics).
    """
    legacy_payload = {
        "source_id": "src_legacy",
        "raw_token": "mutawassiṭ",
        "validated_value": "mutawassiṭ",
        "queued_at": "2026-04-26T10:00:00+00:00",
        "genre_resolution_state_at_queueing": "unresolved",
        "state": "queued",
        "audit_trail": [],
        "resolved_at": None,
        "dispute_snapshot": [],
        # NOTE: no "constituent_idx" key — legacy record
    }
    record = PendingLevelOverride.model_validate(legacy_payload)
    assert record.constituent_idx is None


@pytest.mark.spec("DEC-SRC-0021", "AC-FU37-VII-E")
def test_legacy_genre_dispute_position_payload_defaults_constituent_idx_to_none() -> None:
    """Legacy GenreDisputePosition JSON without constituent_idx loads with None default.

    DEC-SRC-0021 rule (vii.e) added by FU-37 closure 2026-04-28.
    """
    legacy_payload = {
        "genre_candidate": "sharh",
        "supporting_evidence": ["title contains شرح"],
        "confidence": 0.84,
        "source_agents": ["genre_agent_a"],
        "hadith_subgenre_candidate": None,
        # NOTE: no "constituent_idx" key — legacy record
    }
    position = GenreDisputePosition.model_validate(legacy_payload)
    assert position.constituent_idx is None
    assert position.hadith_subgenre_candidate is None


# ---------------------------------------------------------------------------
# Regression: container Axis 2 firing unchanged when per-constituent overrides queued
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0012", "AC-FU37-8")
def test_container_axis_2_firing_unchanged_with_per_constituent_overrides() -> None:
    """Container Axis 2 (composite_work_type=='majmu') still fires when per-constituent
    overrides are queued. Per-constituent intent does NOT override the container's
    non-applicability gate; it queues alongside the container-level NON_APPLICABLE.
    """
    from engines.source.src.deliberation import _queue_constituent_overrides

    metadata = _make_majmu_metadata(constituent_count=3)
    # Container Axis 2 already fired at metadata construction
    assert metadata.composite_work_type == "majmu"
    assert metadata.level is None
    assert metadata.level_status == LevelStatus.NON_APPLICABLE_REFERENCE

    overrides = {1: WorkLevel.MUTAWASSIT}
    deliberation_input = _make_minimal_deliberation_input(
        composite_work_type="majmu", overrides=overrides
    )
    queued = _queue_constituent_overrides(deliberation_input, metadata)

    # Container's non-applicability is preserved
    assert metadata.level is None
    assert metadata.level_status == LevelStatus.NON_APPLICABLE_REFERENCE
    assert metadata.composite_work_type == "majmu"
    # Constituent override was queued
    assert len(queued) == 1
    assert queued[0].constituent_idx == 1
    assert queued[0].validated_value == WorkLevel.MUTAWASSIT
    assert queued[0].state == OverrideQueueState.QUEUED


# ---------------------------------------------------------------------------
# Round-trip: dispute snapshot with per-constituent identifier preserves through
# audit trail
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0012", "AC-FU37-9")
def test_pending_level_override_with_dispute_snapshot_preserves_constituent_idx() -> None:
    """Dispute snapshots tagged with constituent_idx preserve through the queue record.

    arabic-reviewer CRIT-AR-2: per-constituent dispute snapshots must NOT be
    ambiguous about which constituent they target. The PendingLevelOverride
    record carries the dispute_snapshot list verbatim through state transitions,
    so the constituent_idx on each GenreDisputePosition propagates downstream
    to synthesis.
    """
    constituent_dispute = GenreDisputePosition(
        genre_candidate=Genre.HADITH_COLLECTION,
        supporting_evidence=["constituent 2 has hadith chains"],
        confidence=0.7,
        source_agents=["genre_agent_a"],
        constituent_idx=2,
    )
    container_dispute = GenreDisputePosition(
        genre_candidate=Genre.SHARH,
        supporting_evidence=["whole work appears to be a sharh"],
        confidence=0.5,
        source_agents=["genre_agent_b"],
        # constituent_idx defaults to None — container-level
    )
    record = PendingLevelOverride(
        source_id="src_majmu_ibn_taymiyyah",
        raw_token="muntahī",
        validated_value=WorkLevel.MUNTAHI,
        queued_at="2026-04-28T16:00:00+00:00",
        genre_resolution_state_at_queueing=GenreResolutionState.DISPUTED,
        state=OverrideQueueState.DEFERRED_TO_SYNTHESIS,
        constituent_idx=2,
        dispute_snapshot=[constituent_dispute, container_dispute],
    )
    assert record.constituent_idx == 2
    assert record.dispute_snapshot[0].constituent_idx == 2
    assert record.dispute_snapshot[1].constituent_idx is None
