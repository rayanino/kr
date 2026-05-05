"""Phase 5 Session 5 — scholar identity resolution at Step 50.

Brownfield integration of ``scholar_match_cell`` (DEC-SRC-0013) into the
source-engine ``run_metadata_deliberation`` flow. Per REQ-SRC-0008 + Phase
5 amendment 2026-04-30 + REQ-SRC-0043 Phase 5 amendment 2026-04-30, this
module:

  - Builds a ``DossierContext`` from source-engine state primitives (this
    is the engine-side adapter; the engine-agnostic primitives layer
    lives in ``shared.scholar_authority.src.dossier_builder``).
  - Invokes ``scholar_match_cell`` per ``AuthorOutputPosition`` (one
    independent match call per candidate author).
  - Routes the three terminal disambiguation states (definitive /
    disputed / insufficient_evidence) into AuthorOutput updates,
    HumanGateCheckpoint emissions, and ProvisionalScholarRegistration
    requests.

Design notes (Session 5):

  - Per-position match calls. ``agent_no_evidence`` skips the cell
    entirely (no positions to resolve). ``agent_consensus`` and
    ``agent_disagreement`` each invoke the cell once per
    AuthorOutputPosition. The cell itself is deterministic (snapshot-
    pinned) so multiple calls within one deliberation run see the same
    Registry state per INV-SRC-0017.

  - INSUFFICIENT_EVIDENCE discriminator. ScholarMatchResult does not
    expose a "new identity vs verifier-issue" flag directly; we infer
    from ``provenance.stage_1_score_breakdown``: an EMPTY breakdown
    means Stage-1 found zero candidates (scholar genuinely not in
    registry as of this snapshot → REQ-SRC-0043 NEW IDENTITY); a
    non-empty breakdown with INSUFFICIENT_EVIDENCE means either verifier
    unavailability or "verifiers ran but no candidate cleared the floor"
    — both route to HOLD-FOR-EXPLICIT-REPLAY (INV-SRC-0017) because we
    cannot conservatively claim a new identity when Stage-1 surfaced
    plausible candidates. Future sessions may extend the cell to expose
    a richer signal; this discriminator is the conservative interim
    contract.

  - Variant-name consensus collapse. ``agent_disagreement`` positions
    that ALL resolve definitively to the SAME canonical_scholar_id
    represent variant-name disagreement, not genuine scholarly dispute.
    The downstream AuthorOutput.status is collapsed to ``agent_consensus``
    in this case, with the merged position carrying the canonical id.

  - HumanGateTrigger reuse. The existing
    ``HumanGateTrigger.AUTHOR_DISAMBIGUATION`` covers DISPUTED scholar
    match outcomes — no new enum value introduced.

  - Frame-of-reference. This module is the ENGINE adapter. The shared
    ``dossier_builder`` is engine-agnostic; the orchestrator lives in
    ``shared.scholar_authority.src.scholar_match_cell``. Only this
    module knows ``IntakeDossier`` / ``MetadataDeliberationInput``
    shape.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from engines.source.contracts import (
    AuthorOutput,
    AuthorOutputPosition,
    HumanGateCheckpoint,
    HumanGateTrigger,
    IntakeDossier,
    MetadataDeliberationInput,
    ProvisionalScholarRegistration,
    ScholarAuthorityRecord,
    ScholarMatchHold,
)
from shared.scholar_authority.src.dossier_builder import build_dossier_context
from shared.scholar_authority.src.match_contracts import (
    DossierContext,
    ScholarMatchResult,
)
from shared.scholar_authority.src.scholar_match_cell import (
    ScholarMatchCellOrchestration,
    scholar_match_cell,
)
from shared.scholar_authority.src.snapshot_lock import pin_registry_snapshot
from shared.scholar_authority.src.stage1_narrowing import CaseComplexity, Registry
from shared.scholar_authority.src.stage2_verifier import (
    VerifierCallable,
    VerifierSpec,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Orchestration construction (sub-task 4: per-pipeline-run setup)
# ---------------------------------------------------------------------------


_DEFAULT_REGISTRY_RELEASE_VERSION: str = "v0_session5_empty"
"""Sentinel release version used when scholars.json is absent or ``{}``.

A truly empty registry still needs a pinned snapshot so the
ScholarMatchCellOrchestration can be constructed; downstream code routes
all match calls to ``insufficient_evidence`` (empty narrowing) until the
registry is populated. The sentinel string is distinguishable from a
real release tag so audit logs are unambiguous."""


def load_registry_from_path(path: Path) -> Registry:
    """Load a ``Registry`` from ``library/registries/scholars.json``.

    Expected JSON shape:

      {
        "release_version": "v_<tag>",
        "scholars": [<ScholarAuthorityRecord JSON>, ...]
      }

    Empty / placeholder shapes (``{}`` or absent file) return a Registry
    with the sentinel release_version and an empty scholar list. This
    lets the production pipeline run end-to-end before the registry has
    been populated — every match call routes to insufficient_evidence
    (empty narrowing → REQ-SRC-0043 new identity path).
    """
    if not path.exists():
        logger.info(
            "load_registry_from_path: %s does not exist; returning empty Registry",
            path,
        )
        return Registry(release_version=_DEFAULT_REGISTRY_RELEASE_VERSION, scholars=[])

    raw_text = path.read_text(encoding="utf-8").strip()
    if not raw_text:
        logger.info(
            "load_registry_from_path: %s is empty; returning empty Registry", path
        )
        return Registry(release_version=_DEFAULT_REGISTRY_RELEASE_VERSION, scholars=[])

    raw = json.loads(raw_text)
    if not isinstance(raw, dict):
        raise ValueError(
            f"load_registry_from_path: {path} top-level must be a JSON object, "
            f"got {type(raw).__name__}"
        )
    if not raw or "scholars" not in raw:
        # Placeholder ``{}`` — registry not yet populated.
        return Registry(release_version=_DEFAULT_REGISTRY_RELEASE_VERSION, scholars=[])

    release_version = raw.get("release_version") or _DEFAULT_REGISTRY_RELEASE_VERSION
    scholars_raw = raw.get("scholars", [])
    if not isinstance(scholars_raw, list):
        raise ValueError(
            f"load_registry_from_path: {path} 'scholars' must be a list, "
            f"got {type(scholars_raw).__name__}"
        )
    scholars = [
        ScholarAuthorityRecord.model_validate(record_raw) for record_raw in scholars_raw
    ]
    return Registry(release_version=release_version, scholars=scholars)


def build_orchestration_for_pipeline(
    *,
    registry: Registry,
    verifier_a_spec: VerifierSpec,
    verifier_b_spec: VerifierSpec,
    call_verifier: VerifierCallable,
    case_complexity: CaseComplexity = "standard",
) -> ScholarMatchCellOrchestration:
    """Build a ScholarMatchCellOrchestration for one pipeline run.

    Pins the snapshot to ``registry.release_version`` per REQ-SRC-0049.
    The same orchestration is shared across all match-cell calls within
    one pipeline run, so all cells see the same registry state per
    INV-SRC-0017.

    To re-pin (e.g., after a registry release rotation), construct a new
    orchestration via this helper and rebuild the SourcePipeline; do NOT
    mutate an existing orchestration (it is frozen).
    """
    snapshot = pin_registry_snapshot(registry.release_version)
    return ScholarMatchCellOrchestration(
        registry=registry,
        snapshot=snapshot,
        verifier_a_spec=verifier_a_spec,
        verifier_b_spec=verifier_b_spec,
        call_verifier=call_verifier,
        case_complexity=case_complexity,
    )


# ---------------------------------------------------------------------------
# DossierContext builder (engine adapter)
# ---------------------------------------------------------------------------


def build_dossier_from_source_state(
    intake_dossier: IntakeDossier,
    deliberation_input: MetadataDeliberationInput,
    *,
    school_affiliation_hints: Optional[dict[str, Optional[str]]] = None,
    geographic_origin: Optional[str] = None,
    geographic_active: Optional[list[str]] = None,
) -> DossierContext:
    """Build a DossierContext from source-engine intake + deliberation state.

    Maps:
      - ``genre`` ← ``deliberation_input.genre.value`` (Genre enum value or None)
      - ``primary_science`` ← ``deliberation_input.science_scope[0]`` if non-empty
      - ``death_year_hijri`` ← ``deliberation_input.author_death_hijri``
      - ``school_affiliation_hints`` ← caller-passed (None → {})
      - ``title_strings`` ← title_arabic + work_identity_proposal candidates +
        title_evidence entries
      - ``geographic_origin`` / ``geographic_active`` ← caller-passed (typically
        ``None`` / ``[]`` at Step 50 since the source-engine state does not
        directly carry author biographical geography)

    The school + geography signals are caller-supplied because Step 50 has
    no native source for them; the integration layer (run_metadata_deliberation
    Session 5 wiring) may choose to pull them from owner_hint_payload or
    leave them empty, depending on configuration.

    Returns a frozen DossierContext per CON-SRC-0009.
    """
    title_strings: list[str] = []
    if deliberation_input.title_arabic:
        title_strings.append(deliberation_input.title_arabic)
    for candidate in intake_dossier.work_identity_proposal.candidates:
        if candidate.canonical_title_arabic:
            title_strings.append(candidate.canonical_title_arabic)
    for evidence in intake_dossier.title_evidence:
        if evidence.title_text:
            title_strings.append(evidence.title_text)

    primary_science: Optional[str] = (
        deliberation_input.science_scope[0]
        if deliberation_input.science_scope
        else None
    )

    genre_value: Optional[str] = (
        deliberation_input.genre.value
        if deliberation_input.genre is not None
        else None
    )

    return build_dossier_context(
        genre=genre_value,
        primary_science=primary_science,
        death_year_hijri=deliberation_input.author_death_hijri,
        school_affiliation_hints=school_affiliation_hints,
        title_strings=title_strings,
        geographic_origin=geographic_origin,
        geographic_active=list(geographic_active) if geographic_active else [],
    )


# ---------------------------------------------------------------------------
# Per-position match invocation + terminal routing
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    """ISO-8601 UTC timestamp matching deliberation.py convention."""
    return datetime.now(timezone.utc).isoformat()


def _classify_insufficient_evidence(
    result: ScholarMatchResult,
) -> str:
    """Return ``"new_identity"`` or ``"hold_for_replay"`` for an INSUFFICIENT_EVIDENCE result.

    Discriminator: ``provenance.stage_1_score_breakdown`` empty means
    Stage-1 found zero registry candidates (the scholar is genuinely not
    in the registry at this snapshot → REQ-SRC-0043 NEW IDENTITY route).
    Non-empty breakdown means either Stage-1 narrowed candidates but the
    verifier cell either could not run (REQ-SRC-0052 AC-6 verifier
    unavailable) or ran but no candidate cleared the compound thresholds
    (REQ-SRC-0053 below floor) — both route to HOLD-FOR-EXPLICIT-REPLAY
    per INV-SRC-0017 because we cannot conservatively assert a new
    identity when Stage-1 surfaced plausible candidates.

    Caller must have verified
    ``result.disambiguation_state == "insufficient_evidence"`` before
    calling.
    """
    if not result.provenance.stage_1_score_breakdown:
        return "new_identity"
    return "hold_for_replay"


def _bind_canonical_id_to_position(
    position: AuthorOutputPosition,
    result: ScholarMatchResult,
) -> AuthorOutputPosition:
    """Return a copy of ``position`` with canonical_id bound from a DEFINITIVE result.

    Caller must have verified
    ``result.disambiguation_state == "definitive"`` and that
    ``result.canonical_scholar_id`` is non-null before calling.
    """
    if result.canonical_scholar_id is None:
        raise ValueError(
            "_bind_canonical_id_to_position called with definitive result "
            "but canonical_scholar_id is None — CON-SRC-0008 invariant "
            "violation"
        )
    return position.model_copy(
        update={"canonical_id": result.canonical_scholar_id}
    )


def _build_disambiguation_checkpoint(
    *,
    source_id: str,
    position: AuthorOutputPosition,
    result: ScholarMatchResult,
    case_id: str,
) -> HumanGateCheckpoint:
    """Build a HumanGateCheckpoint for a DISPUTED scholar match outcome.

    Per REQ-SRC-0008 Phase 5 amendment 2026-04-30 line 52(e):
    trust_decision.positions per-position MUST carry cited_evidence
    bound to the source_book_ids referenced in evidence_sources. The
    HumanGateCheckpoint surfaces the disputed positions[] with
    canonical_id, confidence, and per-position cited_evidence so the
    owner can resolve the disambiguation.
    """
    alternatives: list[dict[str, object]] = []
    for cell_position in result.positions:
        alternatives.append(
            {
                "canonical_scholar_id": cell_position.canonical_id,
                "confidence": cell_position.confidence,
                "score_breakdown": dict(cell_position.score_breakdown.model_dump()),
                "cited_evidence": [
                    {
                        "source_book_id": ev.source_book_id,
                        "evidence_type": ev.evidence_type,
                        "raw_evidence": ev.raw_evidence,
                    }
                    for ev in cell_position.cited_evidence
                ],
            }
        )
    return HumanGateCheckpoint(
        checkpoint_id=f"hgc_{uuid4().hex[:12]}",
        source_id=source_id,
        trigger=HumanGateTrigger.AUTHOR_DISAMBIGUATION,
        trigger_detail=(
            f"scholar_match_cell DISPUTED for position display_name="
            f"{position.display_name!r} at case_id={case_id}"
        ),
        fields_to_review=["author_output.canonical_id"],
        current_values={
            "display_name": position.display_name,
            "leader_canonical_scholar_id": result.canonical_scholar_id,
            "leader_confidence": result.confidence,
            "scholar_match_result_id": result.result_id,
        },
        alternatives=alternatives,
        created_at=_utc_now_iso(),
    )


def _build_provisional_registration(
    *,
    source_id: str,
    position: AuthorOutputPosition,
    position_index: int,
    result: ScholarMatchResult,
    deliberation_input: MetadataDeliberationInput,
) -> ProvisionalScholarRegistration:
    """Build a ProvisionalScholarRegistration request per REQ-SRC-0043.

    Phase 5 amendment 2026-04-30: triggered ONLY when scholar_match_cell
    emits INSUFFICIENT_EVIDENCE with empty stage_1_score_breakdown
    (Stage-1 found zero registry candidates → "new identity"
    interpretation).

    The registration request carries the data needed to create a
    ``status=provisional`` ScholarAuthorityRecord during normalization
    handoff: display_name, full_name_lineage, death_hijri, nisba_tokens,
    inferred primary_science, evidence strings, source_book_id.
    """
    primary_science: Optional[str] = (
        deliberation_input.science_scope[0]
        if deliberation_input.science_scope
        else None
    )
    return ProvisionalScholarRegistration(
        position_index=position_index,
        display_name=position.display_name,
        full_name_lineage=position.full_name_lineage,
        death_hijri=position.death_hijri,
        nisba_tokens=list(position.nisba_tokens),
        primary_science=primary_science,
        evidence=list(position.evidence),
        source_book_id=source_id,
        triggering_match_result_id=result.result_id,
    )


def _build_scholar_match_hold(
    *,
    position: AuthorOutputPosition,
    position_index: int,
    result: ScholarMatchResult,
) -> ScholarMatchHold:
    """Build a ScholarMatchHold record per INV-SRC-0017 explicit-replay protocol.

    Created when scholar_match_cell yields INSUFFICIENT_EVIDENCE with a
    non-empty stage_1_score_breakdown (verifier unavailable or
    verifiers ran but no candidate cleared the floor). Distinguishing
    these two sub-cases is intentionally deferred — both route to
    HOLD because we cannot conservatively claim "new identity" when
    Stage-1 surfaced plausible candidates.
    """
    candidate_ids = list(result.provenance.stage_1_score_breakdown.keys())
    return ScholarMatchHold(
        position_index=position_index,
        display_name=position.display_name,
        triggering_match_result_id=result.result_id,
        stage_1_candidate_ids=candidate_ids,
        registry_release_version=result.provenance.registry_release_version,
    )


def resolve_scholar_identities(
    *,
    source_id: str,
    case_id: str,
    author_output: AuthorOutput,
    intake_dossier: IntakeDossier,
    deliberation_input: MetadataDeliberationInput,
    orchestration: ScholarMatchCellOrchestration,
    school_affiliation_hints: Optional[dict[str, Optional[str]]] = None,
    geographic_origin: Optional[str] = None,
    geographic_active: Optional[list[str]] = None,
) -> tuple[
    AuthorOutput,
    list[ScholarMatchResult],
    list[HumanGateCheckpoint],
    list[ProvisionalScholarRegistration],
    list[ScholarMatchHold],
]:
    """Resolve canonical scholar ids for every position in author_output.

    Per-position semantics:
      - DEFINITIVE: bind canonical_id to the position
      - DISPUTED: emit HumanGateCheckpoint(AUTHOR_DISAMBIGUATION); position
        canonical_id stays None; AuthorOutput.disambiguation_pending=True
      - INSUFFICIENT_EVIDENCE + empty stage_1_score_breakdown: emit
        ProvisionalScholarRegistration request (REQ-SRC-0043 new identity)
      - INSUFFICIENT_EVIDENCE + non-empty stage_1_score_breakdown: emit
        ScholarMatchHold (INV-SRC-0017 explicit replay)

    Variant-name consensus collapse: when ``author_output.status ==
    "agent_disagreement"`` and ALL positions resolve DEFINITIVELY to the
    SAME canonical_scholar_id, the AuthorOutput is collapsed to
    ``status="agent_consensus"`` with a single merged position. This
    handles the common case where two agents proposed different name
    spellings of the same scholar.

    Returns a 5-tuple:
      - updated AuthorOutput (positions may have canonical_ids bound;
        status may be collapsed; disambiguation_pending may be set)
      - per-position ScholarMatchResult records (full audit trail)
      - human gate checkpoints (one per DISPUTED position)
      - provisional registration requests (one per "new identity" position)
      - hold records (one per "hold for replay" position)
    """
    if author_output.status == "agent_no_evidence" or not author_output.positions:
        return author_output, [], [], [], []

    dossier = build_dossier_from_source_state(
        intake_dossier=intake_dossier,
        deliberation_input=deliberation_input,
        school_affiliation_hints=school_affiliation_hints,
        geographic_origin=geographic_origin,
        geographic_active=geographic_active,
    )

    match_results: list[ScholarMatchResult] = []
    updated_positions: list[AuthorOutputPosition] = []
    checkpoints: list[HumanGateCheckpoint] = []
    provisional_registrations: list[ProvisionalScholarRegistration] = []
    holds: list[ScholarMatchHold] = []
    disambiguation_pending = False

    for idx, position in enumerate(author_output.positions):
        fragment = position.display_name
        if not fragment or not fragment.strip():
            logger.warning(
                "scholar_match_integration: position[%d] has empty display_name; "
                "skipping scholar match",
                idx,
            )
            updated_positions.append(position)
            continue

        result = scholar_match_cell(fragment, dossier, orchestration)
        match_results.append(result)

        state = result.disambiguation_state
        if state == "definitive":
            updated_positions.append(_bind_canonical_id_to_position(position, result))
        elif state == "disputed":
            checkpoints.append(
                _build_disambiguation_checkpoint(
                    source_id=source_id,
                    position=position,
                    result=result,
                    case_id=case_id,
                )
            )
            updated_positions.append(position)
            disambiguation_pending = True
        elif state == "insufficient_evidence":
            classification = _classify_insufficient_evidence(result)
            if classification == "new_identity":
                provisional_registrations.append(
                    _build_provisional_registration(
                        source_id=source_id,
                        position=position,
                        position_index=idx,
                        result=result,
                        deliberation_input=deliberation_input,
                    )
                )
            else:
                holds.append(
                    _build_scholar_match_hold(
                        position=position,
                        position_index=idx,
                        result=result,
                    )
                )
            updated_positions.append(position)
        else:
            raise ValueError(
                f"scholar_match_cell returned unknown disambiguation_state="
                f"{state!r}; expected definitive / disputed / insufficient_evidence"
            )

    collapsed_output = _maybe_collapse_variant_name_consensus(
        author_output=author_output,
        updated_positions=updated_positions,
        disambiguation_pending=disambiguation_pending,
    )
    return collapsed_output, match_results, checkpoints, provisional_registrations, holds


def _maybe_collapse_variant_name_consensus(
    *,
    author_output: AuthorOutput,
    updated_positions: list[AuthorOutputPosition],
    disambiguation_pending: bool,
) -> AuthorOutput:
    """Collapse agent_disagreement → agent_consensus when all positions resolve to same canonical_id.

    Variant-name consensus: two agents proposed different display strings
    for the SAME scholar (e.g., ``ابن حجر`` vs ``الحافظ ابن حجر العسقلاني``).
    Both resolve DEFINITIVELY to the same canonical_scholar_id. The
    apparent ``agent_disagreement`` was actually variant-name disagreement,
    not a genuine scholarly dispute. Collapse to ``agent_consensus`` with a
    single merged position carrying the canonical_id.

    Collapse conditions (all must hold):
      - Original status was ``agent_disagreement``
      - At least 2 positions
      - Every position has a non-null canonical_id
      - All canonical_ids are equal
    """
    base_update: dict[str, object] = {
        "positions": updated_positions,
        "disambiguation_pending": disambiguation_pending,
    }

    if (
        author_output.status == "agent_disagreement"
        and len(updated_positions) >= 2
        and all(p.canonical_id is not None for p in updated_positions)
        and len({p.canonical_id for p in updated_positions}) == 1
    ):
        canonical = updated_positions[0].canonical_id
        merged_evidence: list[str] = []
        merged_agents: list[str] = []
        max_confidence = 0.0
        for p in updated_positions:
            for ev in p.evidence:
                if ev not in merged_evidence:
                    merged_evidence.append(ev)
            for agent in p.source_agents:
                if agent not in merged_agents:
                    merged_agents.append(agent)
            if p.confidence > max_confidence:
                max_confidence = p.confidence
        leader = updated_positions[0]
        merged_position = leader.model_copy(
            update={
                "evidence": merged_evidence,
                "source_agents": merged_agents,
                "confidence": max_confidence,
                "canonical_id": canonical,
            }
        )
        return author_output.model_copy(
            update={
                "status": "agent_consensus",
                "positions": [merged_position],
                "disambiguation_pending": disambiguation_pending,
            }
        )
    return author_output.model_copy(update=base_update)


__all__ = [
    "build_dossier_from_source_state",
    "build_orchestration_for_pipeline",
    "load_registry_from_path",
    "resolve_scholar_identities",
]
