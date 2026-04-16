from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any
from uuid import uuid4

from engines.source.contracts import (
    AuthorityLevel,
    AuthorOutput,
    AuthorOutputPosition,
    CaseComplexityRecord,
    DisagreementCaseRecord,
    ErrorCode,
    FailureAnalysis,
    FrozenSource,
    HintComparisonResult,
    HintInvestigation,
    IntakeDossier,
    IntegrityStatus,
    MetadataDeliberationInput,
    MetadataDeliberationResult,
    MonitorEvidenceCoverage,
    MonitorFeedbackRecord,
    MonitorIndependenceCheck,
    MonitorSuggestedPolicyUpdate,
    MonitorUncertaintyFlags,
    PdfTextLayerStatus,
    SourceMetadata,
    TrustDecision,
    WorkOutput,
    WorkOutputPosition,
)
from engines.source.src.errors import SourceEngineError


_FAST_TRACK_GENRES = {"matn", "sharh", "hadith_collection", "tafsir", "tabaqat", "fatawa"}
_FAST_TRACK_AUTHORITIES = {"primary", "reference"}
_ALLOWED_HINT_FIELDS = {"author_name", "genre", "science_scope"}
logger = logging.getLogger(__name__)


def assess_case_complexity(
    dossier: IntakeDossier,
    genre: str | None,
    author_death_hijri: int | None,
    authority_level: str | None,
) -> CaseComplexityRecord:
    genre_value = _enum_value(genre)
    authority_value = _enum_value(authority_level)
    if dossier.integrity_status == IntegrityStatus.SUSPICIOUS or dossier.pdf_text_layer_status in {
        PdfTextLayerStatus.ABSENT,
        PdfTextLayerStatus.CORRUPT,
    }:
        return CaseComplexityRecord(
            case_complexity="degraded_evidence",
            signals={
                "pdf_text_layer_status": _enum_value(dossier.pdf_text_layer_status),
                "integrity_status": _enum_value(dossier.integrity_status),
            },
        )
    if authority_value in _FAST_TRACK_AUTHORITIES and genre_value in _FAST_TRACK_GENRES and author_death_hijri is not None:
        return CaseComplexityRecord(
            case_complexity="fast_track",
            signals={
                "authority_level": authority_value,
                "genre": genre_value,
                "author_death_hijri": author_death_hijri,
            },
        )
    return CaseComplexityRecord(
        case_complexity="standard",
        signals={
            "authority_level": authority_value,
            "genre": genre_value,
            "author_death_hijri": author_death_hijri,
        },
    )


def deliberate_author_output(positions: list[AuthorOutputPosition]) -> AuthorOutput:
    ordered = _ordered_positions(positions)
    unique_positions = {item.position for item in ordered}
    if not ordered:
        return AuthorOutput(status="agent_no_evidence", positions=[])
    if len(unique_positions) == 1:
        return AuthorOutput(status="agent_consensus", positions=[_merge_consensus_positions(ordered)])
    return AuthorOutput(status="agent_disagreement", positions=ordered)


def compare_owner_hints(
    metadata: SourceMetadata,
    owner_hint_payload: dict[str, Any],
) -> SourceMetadata:
    _validate_hint_fields(owner_hint_payload)
    updated = metadata.model_copy(deep=True)
    for key, value in owner_hint_payload.items():
        if key == "author_name":
            updated = _compare_author_hint(updated, value)
        else:
            updated = _compare_generic_hint(updated, key, value)
    return updated


def evaluate_trust_decision(
    dossier: IntakeDossier,
    genre: str | None,
    author_death_hijri: int | None,
    authority_level: str | None,
    verification_agents: list[str],
) -> TrustDecision:
    distinct_agents = sorted(set(verification_agents))
    if len(distinct_agents) < 2:
        raise SourceEngineError(ErrorCode.TRUST_AGENT_COUNT, "trust evaluation requires 2 agents")
    complexity = assess_case_complexity(dossier, genre, author_death_hijri, authority_level)
    decision = "needs_review" if dossier.study_quality_risk_flags else "verified"
    return TrustDecision(
        decision=decision,
        trust_path=_trust_path_for_complexity(complexity.case_complexity),
        supporting_agents=distinct_agents,
        evidence_summary=f"routed via {complexity.case_complexity}",
    )


def run_metadata_deliberation(
    source_id: str,
    frozen: FrozenSource,
    dossier: IntakeDossier,
    deliberation_input: MetadataDeliberationInput,
) -> MetadataDeliberationResult:
    """Orchestrate step 50 per REQ-SRC-0028, REQ-SRC-0004, REQ-SRC-0026."""
    case_id = _new_case_id()
    if deliberation_input.source_id != source_id:
        raise SourceEngineError(
            ErrorCode.SOURCE_ID_MISMATCH,
            f"metadata deliberation input source_id={deliberation_input.source_id} does not match pipeline source_id={source_id}",
        )
    _validate_dossier_complete(dossier)
    metadata = _build_source_metadata(deliberation_input, frozen)
    author_output, disagreement_cases = _resolve_author_output(
        source_id, deliberation_input.author_positions, case_id,
        verification_agents=deliberation_input.verification_agents,
    )
    metadata.author_output = author_output
    metadata = compare_owner_hints(metadata, deliberation_input.owner_hint_payload)
    metadata.trust_decision = evaluate_trust_decision(
        dossier=dossier,
        genre=_enum_value(metadata.genre),
        author_death_hijri=deliberation_input.author_death_hijri,
        authority_level=_enum_value(deliberation_input.authority_level),
        verification_agents=deliberation_input.verification_agents,
    )
    metadata.work_output = deliberation_input.work_output or _fallback_work_output(dossier)
    _validate_work_output(metadata.work_output)
    metadata.collection_match_output = deliberation_input.collection_match_output or dossier.collection_match_candidates
    metadata.work_id = _derive_work_id(metadata.work_output, metadata.work_id)
    complexity = assess_case_complexity(
        dossier=dossier,
        genre=_enum_value(metadata.genre),
        author_death_hijri=deliberation_input.author_death_hijri,
        authority_level=_enum_value(deliberation_input.authority_level),
    )
    case_record = _case_record(source_id, complexity, case_id)
    monitor_feedback = [
        _monitor_feedback(
            case_record=case_record,
            dossier=dossier,
            deliberation_input=deliberation_input,
            author_output=author_output,
        )
    ]
    return MetadataDeliberationResult(
        source_metadata=metadata,
        case_complexity_record=case_record,
        monitor_feedback=monitor_feedback,
        disagreement_cases=disagreement_cases,
    )


def _build_source_metadata(
    deliberation_input: MetadataDeliberationInput,
    frozen: FrozenSource,
) -> SourceMetadata:
    return SourceMetadata(
        source_id=frozen.source_id,
        title_arabic=deliberation_input.title_arabic,
        source_format=deliberation_input.source_format,
        structural_format=deliberation_input.structural_format,
        intake_timestamp=_utc_now(),
        acquisition_path=deliberation_input.acquisition_path,
        frozen_path=frozen.frozen_blob_path,
        frozen_hash=frozen.source_sha256,
        frozen_file_hashes={
            item.member_name: item.member_sha256
            for item in frozen.frozen_member_manifest
        },
        status=deliberation_input.status,
        work_id=deliberation_input.work_id,
        science_scope=list(deliberation_input.science_scope),
        genre=deliberation_input.genre,
        authority_level=_authority_level_or_none(deliberation_input.authority_level),
        is_multi_layer=deliberation_input.is_multi_layer,
        text_fidelity=deliberation_input.text_fidelity,
        trust_tier=deliberation_input.trust_tier,
        trust_score=deliberation_input.trust_score,
        death_date_hijri=deliberation_input.author_death_hijri,
        level=deliberation_input.level,
        edition_info=deliberation_input.edition_info,
        publisher=deliberation_input.publisher,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
    )


def _validate_dossier_complete(dossier: IntakeDossier) -> None:
    """Guard per REQ-SRC-0028: dossier must be complete for deliberation."""
    if dossier.completeness_status is None or dossier.integrity_status is None:
        raise SourceEngineError(
            ErrorCode.DOSSIER_INCOMPLETE,
            "intake dossier lacks completeness_status or integrity_status",
        )


def _validate_work_output(work_output: WorkOutput) -> None:
    """Guard per REQ-SRC-0026: work_output must exist and be evidence-backed."""
    if work_output is None:
        raise SourceEngineError(
            ErrorCode.WORK_OUTPUT_MISSING,
            "metadata finalization completed without emitting work_output",
        )
    if work_output.status == "definitive" and not work_output.positions:
        raise SourceEngineError(
            ErrorCode.WORK_EVIDENCE,
            "definitive work_output has no evidence-backed positions",
        )


def _resolve_author_output(
    source_id: str,
    positions: list[AuthorOutputPosition],
    case_id: str,
    *,
    verification_agents: list[str] | None = None,
) -> tuple[AuthorOutput, list[DisagreementCaseRecord]]:
    if verification_agents is not None:
        distinct_agents = {p.source_agent for p in positions if p.source_agent}
        if len(distinct_agents) < 2:
            raise SourceEngineError(
                ErrorCode.AUTHOR_AGENT_COUNT,
                f"author attribution requires >= 2 independent agents, got {len(distinct_agents)}",
            )
    ordered = _ordered_positions(positions)
    if not ordered:
        return AuthorOutput(status="agent_no_evidence", positions=[]), []
    if _has_resolved_error(ordered):
        return _resolved_error_output(source_id, ordered, case_id)
    if len({item.position for item in ordered}) == 1:
        return AuthorOutput(status="agent_consensus", positions=[_merge_consensus_positions(ordered)]), []
    case = DisagreementCaseRecord(
        case_id=case_id,
        source_id=source_id,
        field="author_output",
        round_count=3,
        resolution_state="genuine_scholarly_dispute",
        positions=ordered,
    )
    return AuthorOutput(status="agent_disagreement", positions=ordered), [case]


def _resolved_error_output(
    source_id: str,
    positions: list[AuthorOutputPosition],
    case_id: str,
) -> tuple[AuthorOutput, list[DisagreementCaseRecord]]:
    evidence_backed = [item for item in positions if item.evidence]
    winner = _merge_consensus_positions(evidence_backed)
    loser = max((item for item in positions if not item.evidence), key=lambda item: item.confidence)
    case = DisagreementCaseRecord(
        case_id=case_id,
        source_id=source_id,
        field="author_output",
        round_count=1,
        resolution_state="resolved_error",
        positions=positions,
        failure_analysis=FailureAnalysis(
            agent_id=loser.source_agent,
            error_type="empty_evidence_after_challenge",
            what_missed="position lost all evidence during disagreement review",
            corrective_evidence=list(winner.evidence),
            guardrail_suggestion="require non-empty corrective evidence before preserving a disputed position",
        ),
    )
    return AuthorOutput(status="agent_consensus", positions=[winner]), [case]


def _fallback_work_output(dossier: IntakeDossier) -> WorkOutput:
    if not dossier.work_identity_proposal.candidates:
        return WorkOutput(status="insufficient_evidence", positions=[])
    positions = [
        WorkOutputPosition(
            work_id=candidate.work_id,
            canonical_title_arabic=candidate.canonical_title_arabic,
            edition_label=None,
            volume_designation=None,
            evidence=candidate.evidence,
            confidence=candidate.confidence,
            source_agent=candidate.source_agent or "intake_analysis",
        )
        for candidate in dossier.work_identity_proposal.candidates
    ]
    return WorkOutput(status="definitive", positions=positions)


def _case_record(
    source_id: str,
    complexity: CaseComplexityRecord,
    case_id: str,
) -> CaseComplexityRecord:
    return complexity.model_copy(
        update={
            "case_id": case_id,
            "source_id": source_id,
            "field": "author_output",
            "trust_path": _trust_path_for_complexity(complexity.case_complexity),
            "status": "completed",
            "completed_at": _utc_now(),
        }
    )


def _monitor_feedback(
    case_record: CaseComplexityRecord,
    dossier: IntakeDossier,
    deliberation_input: MetadataDeliberationInput,
    author_output: AuthorOutput,
) -> MonitorFeedbackRecord:
    used_source_types = sorted(set(deliberation_input.research_source_types))
    meets_minimum = len(used_source_types) >= 2
    spec_violations: list[ErrorCode] = []
    suggestions: list[MonitorSuggestedPolicyUpdate] = []
    if not meets_minimum:
        spec_violations.append(ErrorCode.INCOMPLETE_RESEARCH)
        suggestions.append(
            MonitorSuggestedPolicyUpdate(
                code="expand_research_sources",
                summary="high-impact metadata used fewer than 2 distinct source types",
            )
        )
    return MonitorFeedbackRecord(
        case_id=case_record.case_id or _new_case_id(),
        source_id=case_record.source_id or deliberation_input.source_id,
        field="trust_decision",
        trust_path=case_record.trust_path or "full_deliberation",
        completed_at=case_record.completed_at or _utc_now(),
        evidence_coverage=MonitorEvidenceCoverage(
            used_source_types=used_source_types,
            meets_minimum=meets_minimum,
        ),
        independence_check=MonitorIndependenceCheck(
            agent_ids=sorted(set(deliberation_input.verification_agents)),
            distinct_agent_ids=len(set(deliberation_input.verification_agents)) >= 2,
            independent_before_exchange=True,
        ),
        uncertainty_flags=MonitorUncertaintyFlags(
            multi_position_output=author_output.status == "agent_disagreement",
            ocr_unreliable_source=dossier.pdf_text_layer_status in {
                PdfTextLayerStatus.ABSENT,
                PdfTextLayerStatus.CORRUPT,
            },
            confidence_ordering_applied=_is_confidence_descending(author_output.positions),
        ),
        spec_violations=spec_violations,
        suggested_policy_updates=suggestions,
    )


def _validate_hint_fields(owner_hint_payload: dict[str, Any]) -> None:
    invalid = sorted(set(owner_hint_payload) - _ALLOWED_HINT_FIELDS)
    if invalid:
        raise SourceEngineError(ErrorCode.HINT_FIELD, ",".join(invalid))


def _compare_author_hint(metadata: SourceMetadata, hint_value: Any) -> SourceMetadata:
    if metadata.author_output is None or not metadata.author_output.positions:
        return metadata
    matching_position = next(
        (position for position in metadata.author_output.positions if position.position == hint_value),
        None,
    )
    inferred_value = matching_position.position if matching_position is not None else metadata.author_output.positions[0].position
    matched = matching_position is not None
    delta = 0.05 if matched else 0.0
    metadata.hint_comparison_results.append(
        HintComparisonResult(
            hint_field="author_name",
            hint_value=hint_value,
            inferred_value=inferred_value,
            match=matched,
            confidence_delta=delta,
        )
    )
    if not matched:
        metadata.hint_investigation.append(
            HintInvestigation(
                field="author_name",
                hint_value=hint_value,
                inferred_value=inferred_value,
                status="opened",
                opened_reason="hint contradiction",
            )
        )
    return metadata


def _compare_generic_hint(
    metadata: SourceMetadata,
    hint_field: str,
    hint_value: Any,
) -> SourceMetadata:
    inferred_value = getattr(metadata, hint_field if hint_field != "science_scope" else "science_scope")
    comparable = inferred_value.value if hasattr(inferred_value, "value") else inferred_value
    matched = comparable == hint_value
    metadata.hint_comparison_results.append(
        HintComparisonResult(
            hint_field=hint_field,
            hint_value=hint_value,
            inferred_value=comparable,
            match=matched,
            confidence_delta=0.05 if matched else 0.0,
        )
    )
    if not matched:
        metadata.hint_investigation.append(
            HintInvestigation(
                field=hint_field,
                hint_value=hint_value,
                inferred_value=inferred_value,
                status="opened",
                opened_reason="hint contradiction",
            )
        )
    return metadata


def _ordered_positions(positions: list[AuthorOutputPosition]) -> list[AuthorOutputPosition]:
    return sorted(positions, key=lambda item: item.confidence, reverse=True)


def _has_resolved_error(positions: list[AuthorOutputPosition]) -> bool:
    evidence_backed = [item for item in positions if item.evidence]
    return bool(evidence_backed) and any(not item.evidence for item in positions) and len(
        {item.position for item in evidence_backed}
    ) == 1


def _merge_consensus_positions(positions: list[AuthorOutputPosition]) -> AuthorOutputPosition:
    ordered = _ordered_positions(positions)
    canonical = ordered[0].model_copy(deep=True)
    canonical.evidence = _unique_in_order(
        evidence
        for item in ordered
        for evidence in item.evidence
    )
    canonical.source_agents = _unique_in_order(
        agent
        for item in ordered
        for agent in item.source_agents
    )
    return canonical


def _is_confidence_descending(positions: list[AuthorOutputPosition]) -> bool:
    return all(
        earlier.confidence >= later.confidence
        for earlier, later in zip(positions, positions[1:], strict=False)
    )


def _trust_path_for_complexity(case_complexity: str) -> str:
    return "fast_track" if case_complexity == "fast_track" else "full_deliberation"


def _derive_work_id(work_output: WorkOutput, current_work_id: str | None) -> str | None:
    if work_output.status == "definitive" and work_output.positions and work_output.positions[0].work_id is not None:
        return work_output.positions[0].work_id
    return current_work_id


def _authority_level_or_none(value: AuthorityLevel | str | None) -> AuthorityLevel | None:
    if value is None or isinstance(value, AuthorityLevel):
        return value
    return AuthorityLevel(value)


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _unique_in_order(values: Any) -> list[Any]:
    seen: set[Any] = set()
    ordered: list[Any] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _new_case_id() -> str:
    return f"case_{uuid4().hex[:8]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
