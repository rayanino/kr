"""Owner-level-override deferred-validation queue per REQ-SRC-0048.

The queue surface is the intake-stage handler for ``owner_level_override``
records that arrive before metadata deliberation has resolved a genre. The
synchronous REQ-SRC-0047 path (``deliberation._resolve_level_fields``) handles
the case where genre IS known at intake. This module handles the deferred
case: an override is accepted at intake, queued under
provenance="owner_override_deferred", and resolved when genre subsequently
arrives — applied if the resolved genre is leveled and no INV-SRC-0012 axis
fires, rejected with SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE if Axis 1 or Axis 2
fires, deferred to synthesis if agents return ``genre_dispute`` without
consensus, or abandoned if intake closes without resolution.

Design follows the 3-evaluator hardening review (`.kr/runtime/
followup29_evaluator_synthesis_final.md`):

- Pure-function API (Codex MED-4): caller owns queue state. The pipeline /
  store decides where to persist ``PendingLevelOverride`` records.
- Atomic three-field swap (Codex MED-5): ``apply_override_queue_resolution``
  uses ``model_copy(update=...)`` so ``validate_assignment=True`` does not
  trip CON-SRC-0004 invariants 1/2 mid-transition.
- Reuses ``GenreDisputePosition`` for the dispute snapshot (Codex HIGH-2 +
  Gemini Run B DIM1): synthesis-engine consumption needs full
  ``supporting_evidence`` to perform iʿtibār without losing bayyinah.
- AC-3 path raises (Gemini Run A Q2.2): the caller invokes
  ``apply_override_queue_resolution`` which raises ``SourceEngineError``
  whenever ``resolution.error_code`` is set — silent rejection would fail
  the project's "errors fail loudly" rule and the bayān principle.
- Persistence in scope (Codex HIGH-1): the resolved ``PendingLevelOverride``
  record is carried on ``MetadataDeliberationResult`` and
  ``NormalizationHandoffBundle`` so synthesis inherits the full audit
  history and dispute snapshot.

Spec literals frozen verbatim:
- audit-trail provenance: "owner_override_deferred" (REQ-SRC-0048
  postconditions). SPEC_AMENDMENT_REQUESTED (Run B DIM2) tracks possible
  future rename to "owner_override_pending_genre_resolution".
- staleness window default: 48 hours (REQ-SRC-0048 error_conditions).
  SPEC_AMENDMENT_REQUESTED (Run B DIM3) tracks possible future extension to
  168h per Zarnūjī's tawaqquf principle.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from engines.source.contracts import (
    NON_APPLICABLE_GENRE_VALUES,
    ErrorCode,
    Genre,
    GenreDisputePosition,
    GenreResolutionState,
    LevelProvenance,
    LevelStatus,
    OverrideQueueAuditEntry,
    OverrideQueueState,
    PendingLevelOverride,
    SourceMetadata,
    WarningCode,
    WorkLevel,
)
from engines.source.src.errors import SourceEngineError


logger = logging.getLogger(__name__)


DEFAULT_STALENESS_WINDOW_HOURS: int = 48
"""Spec verbatim per REQ-SRC-0048 error_conditions (default 48 hours)."""


class OverrideQueueResolution(BaseModel):
    """Outcome of feeding a genre resolution to a queued override.

    Carries both happy-path data (resolved level triple) and blocking
    information (error_code + axis + detail) so callers can apply via
    ``apply_override_queue_resolution`` without losing context. Per Codex
    HIGH-3 the resolution must be capable of expressing every AC outcome
    including the AC-3 reject and the queue-specific blocking errors.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    record: PendingLevelOverride
    resolved_level: Optional[WorkLevel]
    resolved_level_status: LevelStatus
    resolved_level_provenance: Optional[LevelProvenance]
    warning_codes: list[WarningCode] = Field(default_factory=list)
    error_code: Optional[ErrorCode] = None
    error_detail: Optional[str] = None
    triggered_axis: Optional[Literal["genre", "composite"]] = None
    outcome_state: OverrideQueueState


# ---------------------------------------------------------------------------
# Queue API — pure functions (caller owns state)
# ---------------------------------------------------------------------------


def create_pending_level_override(
    *,
    source_id: str,
    raw_token: str,
    validated_value: WorkLevel,
    genre_resolution_state: GenreResolutionState,
    queued_at: Optional[str] = None,
) -> PendingLevelOverride:
    """Build a ``PendingLevelOverride`` in the QUEUED state with one audit entry.

    Per REQ-SRC-0048 AC-1: the queue record is keyed by source_id, carries
    ``raw_token``, the CON-SRC-0011-validated WorkLevel value, an ISO 8601
    ``queued_at`` timestamp, and the genre-resolution state observed at
    queueing. The first audit-trail entry records the QUEUED transition with
    provenance="owner_override_deferred".
    """
    timestamp = queued_at or _utc_now_iso()
    audit_entry = OverrideQueueAuditEntry(
        transition=OverrideQueueState.QUEUED,
        timestamp=timestamp,
        raw_token=raw_token,
        validated_value=validated_value,
        genre_resolution_state=genre_resolution_state,
        detail=None,
    )
    return PendingLevelOverride(
        source_id=source_id,
        raw_token=raw_token,
        validated_value=validated_value,
        queued_at=timestamp,
        genre_resolution_state_at_queueing=genre_resolution_state,
        state=OverrideQueueState.QUEUED,
        audit_trail=[audit_entry],
        resolved_at=None,
        dispute_snapshot=[],
    )


def resolve_pending_level_override(
    record: PendingLevelOverride,
    *,
    resolved_genre: Optional[Genre],
    composite_work_type: Optional[Literal["majmu", "possible"]] = None,
    genre_dispute: Optional[list[GenreDisputePosition]] = None,
    resolved_at: Optional[str] = None,
    staleness_window_hours: int = DEFAULT_STALENESS_WINDOW_HOURS,
) -> OverrideQueueResolution:
    """Resolve a queued override against a genre resolution.

    Branch order (matches REQ-SRC-0048 behavior.postconditions):

    1. ``genre_dispute`` populated: route by whether every dispute branch
       fires non-applicability. If yes, REJECT with
       SRC-E-OVERRIDE-QUEUE-UNANIMOUSLY-NONAPPLICABLE. If at least one
       branch is leveled, DEFER to synthesis (level_status remains
       pending_synthesis, dispute snapshot preserved verbatim).
    2. ``resolved_genre`` is not None: apply the INV-SRC-0012 3-axis gate.
       Axis 1 (genre in NON_APPLICABLE_GENRE_VALUES) or Axis 2
       (composite_work_type=="majmu") → REJECT with
       SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE. Otherwise APPLY (level=
       record.validated_value, level_status="assigned",
       level_provenance="owner_override").
    3. Neither resolved_genre nor genre_dispute: caller should have invoked
       ``abandon_pending_level_override`` instead. We treat this as ABANDONED
       defensively to keep the contract closed.

    Stale warning is added to ``warning_codes`` whenever
    ``(resolved_at - queued_at)`` exceeds ``staleness_window_hours``,
    independent of which AC path fires.
    """
    timestamp = resolved_at or _utc_now_iso()
    is_stale = _is_stale(record.queued_at, timestamp, staleness_window_hours)
    warning_codes: list[WarningCode] = []
    if is_stale:
        warning_codes.append(WarningCode.OVERRIDE_QUEUE_STALE)

    # Branch 1 — genre_dispute populated.
    if genre_dispute:
        return _resolve_disputed(
            record,
            dispute=genre_dispute,
            timestamp=timestamp,
            warning_codes=warning_codes,
        )

    # Branch 2 — single-genre resolution.
    if resolved_genre is not None:
        return _resolve_single_genre(
            record,
            resolved_genre=resolved_genre,
            composite_work_type=composite_work_type,
            timestamp=timestamp,
            warning_codes=warning_codes,
        )

    # Branch 3 — neither: defensive abandoned outcome. The caller should
    # have called ``abandon_pending_level_override`` directly.
    return abandon_pending_level_override(
        record,
        reason="resolve called without resolved_genre or genre_dispute",
        timestamp=timestamp,
    )


def abandon_pending_level_override(
    record: PendingLevelOverride,
    *,
    reason: str,
    timestamp: Optional[str] = None,
) -> OverrideQueueResolution:
    """Mark a queued override as ABANDONED when intake closes without resolution.

    Per REQ-SRC-0048 error_conditions: when intake_analysis closes without
    genre ever resolving (deliberation timed out or failed permanently) AND
    no genre_dispute was recorded, the queued override is not lost — it is
    persisted in the audit trail with the timeout reason, and
    SourceMetadata.level_status stays "pending_synthesis" so synthesis can
    consume the queued record on resume.
    """
    abandon_at = timestamp or _utc_now_iso()
    detail = f"override queue abandoned: {reason}"
    abandoned_record = _append_transition(
        record,
        new_state=OverrideQueueState.ABANDONED,
        timestamp=abandon_at,
        genre_resolution_state=GenreResolutionState.UNRESOLVED,
        detail=detail,
        resolved_at=abandon_at,
    )
    return OverrideQueueResolution(
        record=abandoned_record,
        resolved_level=None,
        resolved_level_status=LevelStatus.PENDING_SYNTHESIS,
        resolved_level_provenance=None,
        warning_codes=[],
        error_code=ErrorCode.OVERRIDE_QUEUE_ABANDONED,
        error_detail=detail,
        triggered_axis=None,
        outcome_state=OverrideQueueState.ABANDONED,
    )


def apply_override_queue_resolution(
    metadata: SourceMetadata,
    resolution: OverrideQueueResolution,
) -> SourceMetadata:
    """Atomically swap the (level, level_status, level_provenance) triple.

    Per Codex MED-5: a single ``model_copy(update=...)`` produces a new
    SourceMetadata with all three fields applied at once, so
    ``validate_assignment=True`` runs the cross-field validator once on the
    consistent target triple rather than tripping invariants mid-mutation.

    Per Gemini Run A Q2.2 (bayān): if ``resolution.error_code`` is set, raise
    ``SourceEngineError`` so the rejection is communicated loudly. Errors
    fail loudly (project Critical Rule 4) — silent audit-only would mask
    knowledge corruption.
    """
    if resolution.error_code is not None:
        raise SourceEngineError(
            resolution.error_code,
            resolution.error_detail or resolution.error_code.value,
        )
    return metadata.model_copy(
        update={
            "level": resolution.resolved_level,
            "level_status": resolution.resolved_level_status,
            "level_provenance": resolution.resolved_level_provenance,
        }
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_disputed(
    record: PendingLevelOverride,
    *,
    dispute: list[GenreDisputePosition],
    timestamp: str,
    warning_codes: list[WarningCode],
) -> OverrideQueueResolution:
    """Resolve a record where agents returned genre_dispute.

    Two outcomes:

    - All proposed genres independently fire non-applicability (every
      genre is in NON_APPLICABLE_GENRE_VALUES) → REJECT with
      SRC-E-OVERRIDE-QUEUE-UNANIMOUSLY-NONAPPLICABLE.
    - At least one proposed genre is leveled → DEFER to synthesis
      (level_status remains pending_synthesis, dispute snapshot
      preserved). The synthesis engine adjudicates per DEC-SRC-0003.
    """
    all_nonapplicable = all(
        position.genre_candidate.value in NON_APPLICABLE_GENRE_VALUES
        for position in dispute
    )
    if all_nonapplicable:
        detail = (
            "owner_level_override rejected: every proposed dispute genre fires "
            "INV-SRC-0012 Axis 1 non-applicability — the override cannot apply "
            f"under any branch (proposed={sorted({p.genre_candidate.value for p in dispute})})"
        )
        rejected_record = _append_transition(
            record,
            new_state=OverrideQueueState.REJECTED_NONAPPLICABLE,
            timestamp=timestamp,
            genre_resolution_state=GenreResolutionState.DISPUTED,
            detail=detail,
            resolved_at=timestamp,
            dispute_snapshot=list(dispute),
        )
        return OverrideQueueResolution(
            record=rejected_record,
            resolved_level=None,
            resolved_level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
            resolved_level_provenance=None,
            warning_codes=warning_codes,
            error_code=ErrorCode.OVERRIDE_QUEUE_UNANIMOUSLY_NONAPPLICABLE,
            error_detail=detail,
            triggered_axis="genre",
            outcome_state=OverrideQueueState.REJECTED_NONAPPLICABLE,
        )

    # Mixed dispute (at least one leveled candidate) → defer to synthesis.
    detail = (
        "owner_level_override deferred to synthesis: agents returned "
        f"genre_dispute with {len(dispute)} positions, no D-041 consensus"
    )
    deferred_record = _append_transition(
        record,
        new_state=OverrideQueueState.DEFERRED_TO_SYNTHESIS,
        timestamp=timestamp,
        genre_resolution_state=GenreResolutionState.DISPUTED,
        detail=detail,
        resolved_at=timestamp,
        dispute_snapshot=list(dispute),
    )
    return OverrideQueueResolution(
        record=deferred_record,
        resolved_level=None,
        resolved_level_status=LevelStatus.PENDING_SYNTHESIS,
        resolved_level_provenance=None,
        warning_codes=warning_codes,
        error_code=None,
        error_detail=None,
        triggered_axis=None,
        outcome_state=OverrideQueueState.DEFERRED_TO_SYNTHESIS,
    )


def _resolve_single_genre(
    record: PendingLevelOverride,
    *,
    resolved_genre: Genre,
    composite_work_type: Optional[Literal["majmu", "possible"]],
    timestamp: str,
    warning_codes: list[WarningCode],
) -> OverrideQueueResolution:
    """Resolve a record where a single genre consensus was reached."""
    axis_1_fires = resolved_genre.value in NON_APPLICABLE_GENRE_VALUES
    axis_2_fires = composite_work_type == "majmu"

    if axis_1_fires:
        detail = (
            f"owner_level_override='{record.validated_value.value}' rejected: "
            f"INV-SRC-0012 Axis 1 (genre) fires — genre='{resolved_genre.value}' "
            f"is in the non-applicable set {sorted(NON_APPLICABLE_GENRE_VALUES)}; "
            "these works MUST serialize level as null regardless of any override "
            "attempt"
        )
        rejected_record = _append_transition(
            record,
            new_state=OverrideQueueState.REJECTED_NONAPPLICABLE,
            timestamp=timestamp,
            genre_resolution_state=GenreResolutionState.RESOLVED,
            detail=detail,
            resolved_at=timestamp,
        )
        return OverrideQueueResolution(
            record=rejected_record,
            resolved_level=None,
            resolved_level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
            resolved_level_provenance=None,
            warning_codes=warning_codes,
            error_code=ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE,
            error_detail=detail,
            triggered_axis="genre",
            outcome_state=OverrideQueueState.REJECTED_NONAPPLICABLE,
        )

    if axis_2_fires:
        detail = (
            f"owner_level_override='{record.validated_value.value}' rejected: "
            f"INV-SRC-0012 Axis 2 (composite) fires — composite_work_type="
            f"'{composite_work_type}' marks the work as a structural composite "
            "whose container-level pedagogy does not apply"
        )
        rejected_record = _append_transition(
            record,
            new_state=OverrideQueueState.REJECTED_NONAPPLICABLE,
            timestamp=timestamp,
            genre_resolution_state=GenreResolutionState.RESOLVED,
            detail=detail,
            resolved_at=timestamp,
        )
        return OverrideQueueResolution(
            record=rejected_record,
            resolved_level=None,
            resolved_level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
            resolved_level_provenance=None,
            warning_codes=warning_codes,
            error_code=ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE,
            error_detail=detail,
            triggered_axis="composite",
            outcome_state=OverrideQueueState.REJECTED_NONAPPLICABLE,
        )

    # Happy path — apply the override.
    applied_detail = (
        f"owner_level_override='{record.validated_value.value}' applied: "
        f"genre='{resolved_genre.value}' is leveled and no INV-SRC-0012 axis fires"
    )
    applied_record = _append_transition(
        record,
        new_state=OverrideQueueState.APPLIED,
        timestamp=timestamp,
        genre_resolution_state=GenreResolutionState.RESOLVED,
        detail=applied_detail,
        resolved_at=timestamp,
    )
    return OverrideQueueResolution(
        record=applied_record,
        resolved_level=record.validated_value,
        resolved_level_status=LevelStatus.ASSIGNED,
        resolved_level_provenance=LevelProvenance.OWNER_OVERRIDE,
        warning_codes=warning_codes,
        error_code=None,
        error_detail=None,
        triggered_axis=None,
        outcome_state=OverrideQueueState.APPLIED,
    )


def _append_transition(
    record: PendingLevelOverride,
    *,
    new_state: OverrideQueueState,
    timestamp: str,
    genre_resolution_state: GenreResolutionState,
    detail: Optional[str],
    resolved_at: Optional[str] = None,
    dispute_snapshot: Optional[list[GenreDisputePosition]] = None,
) -> PendingLevelOverride:
    """Append a state-transition entry and return a new immutable record.

    D-023 metadata-preservation discipline: the existing audit_trail entries
    are preserved verbatim; the new entry is appended. ``model_copy(update=...)``
    re-runs Pydantic validation once on the resulting model so the record
    remains internally consistent.
    """
    new_audit_entry = OverrideQueueAuditEntry(
        transition=new_state,
        timestamp=timestamp,
        raw_token=record.raw_token,
        validated_value=record.validated_value,
        genre_resolution_state=genre_resolution_state,
        detail=detail,
    )
    updates: dict[str, object] = {
        "state": new_state,
        "audit_trail": [*record.audit_trail, new_audit_entry],
    }
    if resolved_at is not None:
        updates["resolved_at"] = resolved_at
    if dispute_snapshot is not None:
        updates["dispute_snapshot"] = dispute_snapshot
    return record.model_copy(update=updates)


def _is_stale(queued_at: str, resolved_at: str, window_hours: int) -> bool:
    """True if (resolved_at - queued_at) exceeds the staleness window."""
    queued = datetime.fromisoformat(queued_at)
    resolved = datetime.fromisoformat(resolved_at)
    return (resolved - queued) > timedelta(hours=window_hours)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
