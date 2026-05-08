from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Literal, Optional, cast
from uuid import uuid4

from engines.source.contracts import (
    CompletenessStatus,
    DisagreementCaseRecord,
    EditionFingerprint,
    EditionGroup,
    EditionHolding,
    ErrorCode,
    FrozenSource,
    IntakeDossier,
    MetadataDeliberationResult,
    NormalizationHandoffBundle,
    NormalizationInput,
    NormalizationRoute,
    OwnerSubmissionRiskCase,
    PdfTextLayerStatus,
    RawUploadRecord,
    RawUploadStatus,
    ScholarAuthorityRecord,
    SourceFormat,
    SourceMetadata,
    VolumeHolding,
)
from engines.source.src.errors import SourceEngineError
from engines.source.src.scholar_admission import register_provisional_scholars
from engines.source.src.store import SourceStore


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceAdmissionResult:
    raw_upload_record: RawUploadRecord
    source_collection_records: list[SourceMetadata]
    handoff_bundle: NormalizationHandoffBundle | None
    owner_submission_risk_case: OwnerSubmissionRiskCase | None
    edition_groups: list[EditionGroup]
    edition_holdings: list[EditionHolding]
    # Phase 5 Session 9 (2026-05-08) per REQ-SRC-0043 AC-1: status=provisional
    # ScholarAuthorityRecords created in this admission pass via the
    # ``register_provisional_scholars`` consumer. Empty when the source did
    # not trigger any NEW IDENTITY emissions (Stage-1 found ≥1 candidate
    # for every position OR ``scholar_match_orchestration`` was None).
    provisional_scholars_registered: list[ScholarAuthorityRecord] = field(
        default_factory=list
    )


def admit_source_and_build_handoff(
    store: SourceStore,
    frozen: FrozenSource,
    dossier: IntakeDossier,
    deliberation_result: MetadataDeliberationResult,
    owner_acknowledged: bool,
    edition_groups: list[EditionGroup] | None = None,
    edition_holdings: list[EditionHolding] | None = None,
    *,
    scholar_registry_path: Optional[Path] = None,
) -> SourceAdmissionResult:
    """Admit the source and build the normalization handoff bundle.

    Phase 5 Session 9 (2026-05-08) — REQ-SRC-0043 AC-1: when
    ``deliberation_result.provisional_scholar_registrations`` is non-empty,
    invokes ``register_provisional_scholars`` to write
    ``status=provisional`` entries to the scholar registry
    (default: ``library/registries/scholars.json``). The
    ``scholar_registry_path`` keyword argument allows tests and
    out-of-tree deployments to redirect to an isolated registry. If the
    deliberation produced no NEW IDENTITY emissions, the registry is
    untouched (the consumer short-circuits on empty input).

    Risk-gate-blocked sources (``risk_case is not None``) skip
    registration entirely — registry mutations are deferred until the
    owner acknowledges the gate. Provisional scholar admission is a
    side-effect of source admission and inherits the same gate.
    """
    _validate_deliberation_source_identity(frozen, deliberation_result)
    raw_upload = store.get_raw_upload(frozen.submission_id or "")
    risk_case = _risk_case_for_dossier(frozen.source_id, dossier, owner_acknowledged)
    if risk_case is not None:
        raw_upload.status = RawUploadStatus.AWAITING_OWNER_ACK
        store.update_raw_upload(raw_upload)
        store.save_risk_case(risk_case)
        return SourceAdmissionResult(
            raw_upload_record=raw_upload,
            source_collection_records=[],
            handoff_bundle=None,
            owner_submission_risk_case=risk_case,
            edition_groups=edition_groups or [],
            edition_holdings=edition_holdings or [],
        )
    finalized = _finalize_metadata(deliberation_result.source_metadata, frozen, dossier)
    bundle = _build_handoff_bundle(
        source_metadata=finalized,
        dossier=dossier,
        frozen=frozen,
        disagreement_cases=deliberation_result.disagreement_cases,
    )
    # REQ-SRC-0043 AC-1: register status=provisional scholars for NEW
    # IDENTITY match-cell emissions before persisting source collection
    # state. Failures here propagate as exceptions per Critical Rule 4
    # (errors fail loudly) — a registry write failure must NOT silently
    # admit a source whose attribution depends on a not-yet-recorded
    # provisional scholar.
    provisional_registered = register_provisional_scholars(
        deliberation_result.provisional_scholar_registrations,
        registry_path=scholar_registry_path,
    )
    raw_upload.status = RawUploadStatus.SOURCE_ENGINE_ACCEPTED
    store.update_raw_upload(raw_upload)
    store.save_source_collection_record(finalized)
    store.save_handoff_bundle(bundle)
    groups, holdings = reconcile_holdings(
        frozen=frozen,
        dossier=dossier,
        source_metadata=finalized,
        edition_groups=edition_groups or [],
        edition_holdings=edition_holdings or [],
    )
    apply_supersession(groups, holdings, finalized, dossier.completeness_status)
    return SourceAdmissionResult(
        raw_upload_record=raw_upload,
        source_collection_records=[finalized],
        handoff_bundle=bundle,
        owner_submission_risk_case=None,
        edition_groups=groups,
        edition_holdings=holdings,
        provisional_scholars_registered=provisional_registered,
    )


def reconcile_holdings(
    frozen: FrozenSource,
    dossier: IntakeDossier,
    source_metadata: SourceMetadata,
    edition_groups: list[EditionGroup],
    edition_holdings: list[EditionHolding],
) -> tuple[list[EditionGroup], list[EditionHolding]]:
    matched_group_id = (
        source_metadata.collection_match_output.matched_edition_group_id
        if source_metadata.collection_match_output
        else None
    )
    if matched_group_id is not None:
        matching_holdings = [
            holding for holding in edition_holdings if holding.edition_group_id == matched_group_id
        ]
        matched_group = next(
            (group for group in edition_groups if group.edition_group_id == matched_group_id),
            None,
        )
        if matched_group is not None and _fingerprints_conflict(
            matched_group.edition_fingerprint,
            source_metadata.edition_info or {},
        ):
            new_group = _new_group(source_metadata)
            new_holding = _new_holding(new_group, dossier, frozen.source_id, source_metadata)
            return [*edition_groups, new_group], [*edition_holdings, new_holding]
        if not matching_holdings:
            if matched_group is None:
                new_group = _new_group(source_metadata)
                new_holding = _new_holding(new_group, dossier, frozen.source_id, source_metadata)
                return [*edition_groups, new_group], [*edition_holdings, new_holding]
            new_holding = _new_holding(matched_group, dossier, frozen.source_id, source_metadata)
            return edition_groups, [*edition_holdings, new_holding]
        target_holding_id = _select_target_holding(matching_holdings).holding_id
        updated = [
            _attach_to_holding(item, dossier, frozen.source_id)
            if item.holding_id == target_holding_id
            else item
            for item in edition_holdings
        ]
        return edition_groups, updated
    new_group = _new_group(source_metadata)
    new_holding = _new_holding(new_group, dossier, frozen.source_id, source_metadata)
    return [*edition_groups, new_group], [*edition_holdings, new_holding]


def apply_supersession(
    edition_groups: list[EditionGroup],
    edition_holdings: list[EditionHolding],
    source_metadata: SourceMetadata,
    completeness_status: CompletenessStatus | None = None,
) -> None:
    """Apply supersession per REQ-SRC-0045.

    Guard: partial new holdings must NOT supersede complete old ones.
    """
    if source_metadata.work_id is None:
        return
    candidate_groups = {group.edition_group_id for group in edition_groups if group.work_id == source_metadata.work_id}
    candidate_holdings = [holding for holding in edition_holdings if holding.edition_group_id in candidate_groups]
    if len(candidate_holdings) < 2:
        return
    primary = candidate_holdings[-1]
    if primary.holding_state != "active_complete":
        return
    superiority_evidence = (source_metadata.edition_info or {}).get("superiority_evidence")
    if superiority_evidence is None:
        return
    # REQ-SRC-0045 error_condition: do not supersede a complete holding
    # with a partial new source. The source's own completeness is the ground
    # truth, not the holding state (which may be optimistically set).
    if completeness_status is not None and completeness_status != CompletenessStatus.COMPLETE:
        logger.warning(
            "supersession_blocked_by_completeness: source completeness=%s, skipping supersession",
            completeness_status,
        )
        return
    primary.preferred_rank = "primary"
    primary.supersession_policy = "regen_required" if source_metadata.genre == "hadith_collection" else "regen_optional"
    for holding in candidate_holdings[:-1]:
        if holding.holding_state == "active_complete":
            holding.holding_state = cast(Literal["superseded"], "superseded")
            holding.superseded_by = primary.holding_id


def _risk_case_for_dossier(
    source_id: str,
    dossier: IntakeDossier,
    owner_acknowledged: bool,
) -> OwnerSubmissionRiskCase | None:
    if not dossier.study_quality_risk_flags or owner_acknowledged:
        return None
    return OwnerSubmissionRiskCase(
        source_id=source_id,
        risk_flags=dossier.study_quality_risk_flags,
        risk_summary="; ".join(dossier.study_quality_risk_flags),
        recommended_owner_action="review_and_acknowledge",
        notes_from_owner=None,
    )


def _finalize_metadata(
    source_metadata: SourceMetadata,
    frozen: FrozenSource,
    dossier: IntakeDossier,
) -> SourceMetadata:
    """Finalize metadata per REQ-SRC-0025, REQ-SRC-0033."""
    finalized = source_metadata.model_copy(deep=True)
    _validate_mandatory_metadata(finalized)
    _validate_volume_count(dossier)
    finalized.registry_entry_id = f"reg_{uuid4().hex[:8]}"
    finalized.source_sha256 = frozen.source_sha256
    finalized.frozen_blob_path = frozen.frozen_blob_path
    finalized.frozen_hash = frozen.source_sha256
    finalized.frozen_path = frozen.frozen_blob_path
    finalized.frozen_file_hashes = {
        item.member_name: item.member_sha256
        for item in frozen.frozen_member_manifest
    }
    finalized.completeness_status = dossier.completeness_status
    finalized.integrity_status = dossier.integrity_status
    finalized.volume_count = dossier.declared_vs_observed_counts.observed_volume_count or 1
    finalized.intake_timestamp = datetime.now(timezone.utc).isoformat()
    finalized.page_count_physical = dossier.declared_vs_observed_counts.physical_page_count
    finalized.source_format = dossier.source_format or finalized.source_format
    finalized.pdf_text_layer_status = dossier.pdf_text_layer_status
    finalized.page_layout_hint = dossier.page_layout_hint
    finalized.normalization_route = _source_metadata_route(dossier)
    finalized.admission_reason = _admission_reason(dossier.completeness_status)
    finalized.study_quality_risk_flags = list(dossier.study_quality_risk_flags)
    return finalized


def _build_handoff_bundle(
    source_metadata: SourceMetadata,
    dossier: IntakeDossier,
    frozen: FrozenSource,
    disagreement_cases: list[DisagreementCaseRecord],
) -> NormalizationHandoffBundle:
    """Build handoff per REQ-SRC-0025, REQ-SRC-0022, REQ-SRC-0007, REQ-SRC-0046."""
    _validate_pdf_handoff(source_metadata)
    _validate_level_field(source_metadata)
    bundle = NormalizationHandoffBundle(
        source_metadata=source_metadata,
        normalization_input=_build_normalization_input(source_metadata),
        frozen_member_manifest=frozen.frozen_member_manifest,
        completeness_status=dossier.completeness_status,
        integrity_status=dossier.integrity_status,
        declared_vs_observed_counts=dossier.declared_vs_observed_counts,
        pdf_text_layer_status=dossier.pdf_text_layer_status,
        page_layout_hint=dossier.page_layout_hint,
        intake_dossier_contains_isnad_chains=dossier.contains_isnad_chains,
        unresolved_disputes=_unresolved_disputes(disagreement_cases),
    )
    _validate_handoff_evidence(bundle.model_dump(mode="json"))
    return bundle


def _build_normalization_input(source_metadata: SourceMetadata) -> NormalizationInput:
    return NormalizationInput(
        source_id=source_metadata.source_id,
        source_format_legacy=_legacy_source_format(source_metadata),
        frozen_path=source_metadata.frozen_blob_path or source_metadata.frozen_path,
        frozen_hash=source_metadata.source_sha256 or source_metadata.frozen_hash,
        page_count=source_metadata.page_count_physical,
        volume_count=source_metadata.volume_count,
        title_arabic=source_metadata.title_arabic,
        author=_normalization_author(source_metadata),
        work_id=_normalization_work_id(source_metadata),
        structural_format=source_metadata.structural_format,
        is_multi_layer=source_metadata.is_multi_layer,
        genre=source_metadata.genre,
        text_fidelity=source_metadata.text_fidelity,
        trust_tier=source_metadata.trust_tier,
    )


def _source_metadata_route(dossier: IntakeDossier) -> NormalizationRoute:
    """Derive route per REQ-SRC-0022: all PDFs use pdf_ocr_primary at handoff."""
    if dossier.source_format == SourceFormat.PDF:
        return NormalizationRoute.PDF_OCR_PRIMARY
    return dossier.normalization_route or NormalizationRoute.HTML_PARSE_PRIMARY


def _legacy_source_format(source_metadata: SourceMetadata) -> str:
    if source_metadata.source_format == SourceFormat.SHAMELA_HTML:
        return "shamela_html"
    if source_metadata.source_format == SourceFormat.PLAIN_TEXT:
        return "plain_text"
    if source_metadata.pdf_text_layer_status in {PdfTextLayerStatus.CLEAN, PdfTextLayerStatus.PRESENTATION_FORMS}:
        return "pdf_text"
    return "pdf_scanned"


def _admission_reason(completeness_status: CompletenessStatus | None) -> str:
    if completeness_status in {
        CompletenessStatus.PARTIAL,
        CompletenessStatus.MIXED,
        CompletenessStatus.INDETERMINATE,
    }:
        return "accepted_with_flags"
    return "accepted_clean"


def _validate_mandatory_metadata(source_metadata: SourceMetadata) -> None:
    missing: list[str] = []
    if source_metadata.author_output is None:
        missing.append("author_output")
    if source_metadata.work_output is None:
        missing.append("work_output")
    if source_metadata.trust_decision is None:
        missing.append("trust_decision")
    if source_metadata.genre is None:
        missing.append("genre")
    if not source_metadata.science_scope:
        missing.append("science_scope")
    if missing:
        raise SourceEngineError(
            ErrorCode.DOSSIER_INCOMPLETE,
            f"missing mandatory metadata: {', '.join(missing)}",
        )


def _new_group(source_metadata: SourceMetadata) -> EditionGroup:
    info = source_metadata.edition_info or {}
    return EditionGroup(
        edition_group_id=f"edg_{uuid4().hex[:8]}",
        work_id=source_metadata.work_id,
        edition_fingerprint=EditionFingerprint(
            publisher=info.get("publisher"),
            muhaqqiq=info.get("muhaqqiq"),
        ),
        expected_volume_count=source_metadata.volume_count,
    )


def _new_holding(
    group: EditionGroup,
    dossier: IntakeDossier,
    source_id: str,
    source_metadata: SourceMetadata,
) -> EditionHolding:
    """Create a new holding.  REQ-SRC-0044 AC-5: indeterminate work identity."""
    if (
        source_metadata.work_output is not None
        and source_metadata.work_output.status == "insufficient_evidence"
    ):
        state: Literal[
            "active_complete", "active_partial", "indeterminate"
        ] = "indeterminate"
        logger.warning(
            "unresolved_work_identity: source_id=%s, creating indeterminate holding",
            source_metadata.source_id,
        )
    else:
        state = _holding_state(
            dossier.declared_vs_observed_counts.observed_volume_count or 1,
            source_metadata.volume_count or 1,
        )
    return EditionHolding(
        holding_id=f"hold_{uuid4().hex[:8]}",
        edition_group_id=group.edition_group_id,
        holding_state=state,
        coherence_state="coherent",
        expected_volume_count=source_metadata.volume_count,
        volume_holdings=_volume_holdings(
            dossier.declared_vs_observed_counts.observed_volume_count or 1,
            source_id,
        ),
    )


def _attach_to_holding(
    holding: EditionHolding,
    dossier: IntakeDossier,
    source_id: str,
) -> EditionHolding:
    updated = holding.model_copy(deep=True)
    incoming = set(range(1, (dossier.declared_vs_observed_counts.observed_volume_count or 1) + 1))
    seen = {item.volume_number: item for item in updated.volume_holdings}
    for volume_number in sorted(incoming):
        if volume_number in seen:
            seen[volume_number].presence_state = "present_alternate"
            if source_id not in seen[volume_number].source_ids:
                seen[volume_number].source_ids.append(source_id)
            continue
        updated.volume_holdings.append(
            VolumeHolding(
                volume_number=volume_number,
                presence_state="present_primary",
                source_ids=[source_id],
            )
        )
    updated.holding_state = _holding_state(
        len(updated.volume_holdings),
        updated.expected_volume_count or len(updated.volume_holdings),
    )
    return updated


def _volume_holdings(volume_count: int, source_id: str) -> list[VolumeHolding]:
    return [
        VolumeHolding(
            volume_number=index,
            presence_state="present_primary",
            source_ids=[source_id],
        )
        for index in range(1, volume_count + 1)
    ]


def _holding_state(
    present_count: int,
    expected_count: int,
) -> Literal["active_complete", "active_partial"]:
    return "active_complete" if present_count >= expected_count else "active_partial"


def _select_target_holding(holdings: list[EditionHolding]) -> EditionHolding:
    active_partial = next((holding for holding in holdings if holding.holding_state == "active_partial"), None)
    if active_partial is not None:
        return active_partial
    active_complete = next((holding for holding in holdings if holding.holding_state == "active_complete"), None)
    if active_complete is not None:
        return active_complete
    return holdings[0]


def _fingerprints_conflict(
    existing: EditionFingerprint,
    incoming_info: dict[str, object],
) -> bool:
    publisher = incoming_info.get("publisher")
    muhaqqiq = incoming_info.get("muhaqqiq")
    incoming_signals_raw = incoming_info.get("distinguishing_signals")
    incoming_signals = (
        incoming_signals_raw
        if isinstance(incoming_signals_raw, list)
        and all(isinstance(item, str) for item in incoming_signals_raw)
        else None
    )

    publisher_conflict = (existing.publisher is not None and publisher is None) or (
        existing.publisher is not None
        and publisher is not None
        and existing.publisher != publisher
    )
    muhaqqiq_conflict = (existing.muhaqqiq is not None and muhaqqiq is None) or (
        existing.muhaqqiq is not None
        and muhaqqiq is not None
        and existing.muhaqqiq != muhaqqiq
    )
    signals_conflict = (bool(existing.distinguishing_signals) and incoming_signals is None) or (
        bool(existing.distinguishing_signals)
        and incoming_signals is not None
        and set(existing.distinguishing_signals) != set(incoming_signals)
    )
    return publisher_conflict or muhaqqiq_conflict or signals_conflict


def _validate_pdf_handoff(source_metadata: SourceMetadata) -> None:
    """Guard per REQ-SRC-0022: PDF handoff must include text layer status and correct route."""
    is_pdf = source_metadata.source_format in {
        SourceFormat.PDF, SourceFormat.PDF_TEXT, SourceFormat.PDF_SCANNED, SourceFormat.PDF_MULTI_VOLUME,
    }
    if not is_pdf:
        return
    if source_metadata.pdf_text_layer_status is None:
        raise SourceEngineError(
            ErrorCode.PDF_STATUS_MISSING,
            f"source_format={source_metadata.source_format.value} but pdf_text_layer_status is missing",
        )
    if source_metadata.normalization_route != NormalizationRoute.PDF_OCR_PRIMARY:
        raise SourceEngineError(
            ErrorCode.PDF_ROUTE,
            f"source_format={source_metadata.source_format.value} requires pdf_ocr_primary route, got {source_metadata.normalization_route}",
        )


def _validate_level_field(source_metadata: SourceMetadata) -> None:
    """Guard per REQ-SRC-0007: level key must be present (even if null)."""
    payload = source_metadata.model_dump(mode="json")
    if "level" not in payload:
        raise SourceEngineError(
            ErrorCode.LEVEL_FIELD_MISSING,
            "handoff payload omits the level key",
        )


_REQ_SRC_0046_SOURCE_METADATA_SIGNALS: tuple[str, ...] = (
    "title_arabic",
    "genre",
    "science_scope",
    "is_multi_layer",
    "structural_format",
    "edition_info",
    "publisher",
    "muhaqiq_output",
    "page_layout_hint",
    "matn_embedding_style",
    "pdf_text_layer_status",
    "volume_count",
    "genre_dispute",
    "author_output",
)


def _validate_handoff_evidence(bundle_dict: dict[str, object]) -> None:
    """Guard per REQ-SRC-0046: 15-signal required-preserved contract.

    Validates that every signal in the required-preserved set appears as a key
    in the serialized handoff payload, even when the underlying value is None.
    Absent keys raise SRC-E-HANDOFF-EVIDENCE-DROPPED at the top level or
    SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED for sub-field omissions.

    Detail strings follow the REQ-SRC-0046 closure-wave Arabic-localization
    constraint: `إيقاف مؤقت` (īqāf muʾaqqat — temporary halt) per CON-SRC-0012
    blocking tier. Forbidden vocabulary (ردّ / إعلال / جرح / تضعيف / إسقاط /
    إبطال / نقض / طعن / ترك / شذوذ) is excluded because these tokens carry
    hadith-science or fiqh adverse-finding semantics. Preferred tokens: غياب,
    فقدان, إعادة التشغيل.
    """
    metadata = bundle_dict.get("source_metadata")
    if not isinstance(metadata, dict):
        raise SourceEngineError(
            ErrorCode.HANDOFF_EVIDENCE_DROPPED,
            "إيقاف مؤقت: كائن source_metadata غائب من حزمة التسليم — أعد تشغيل تحليل الاستيعاب",
        )
    for signal in _REQ_SRC_0046_SOURCE_METADATA_SIGNALS:
        if signal not in metadata:
            detail = (
                f'إيقاف مؤقت: الحقل المطلوب "{signal}" غائب من حزمة التسليم '
                f"— أعد تشغيل تحليل الاستيعاب"
            )
            raise SourceEngineError(ErrorCode.HANDOFF_EVIDENCE_DROPPED, detail)
    if "intake_dossier_contains_isnad_chains" not in bundle_dict:
        raise SourceEngineError(
            ErrorCode.HANDOFF_EVIDENCE_DROPPED,
            'إيقاف مؤقت: الحقل "intake_dossier_contains_isnad_chains" غائب '
            "من سطح حزمة التسليم — أعد تشغيل تحليل الاستيعاب",
        )
    muhaqiq_output = metadata.get("muhaqiq_output")
    if isinstance(muhaqiq_output, dict) and "last_verified" not in muhaqiq_output:
        raise SourceEngineError(
            ErrorCode.HANDOFF_EVIDENCE_DROPPED_NESTED,
            'إيقاف مؤقت: الحقل الفرعي "muhaqiq_output.last_verified" '
            "غائب من حزمة التسليم — أعد تشغيل تحليل الاستيعاب",
        )
    genre_dispute = metadata.get("genre_dispute")
    if isinstance(genre_dispute, list):
        for index, position in enumerate(genre_dispute):
            if not isinstance(position, dict):
                raise SourceEngineError(
                    ErrorCode.HANDOFF_EVIDENCE_DROPPED_NESTED,
                    f'إيقاف مؤقت: عنصر "genre_dispute[{index}]" '
                    "لا يحمل بنية موثقة — أعد تشغيل تحليل الاستيعاب",
                )
            for subfield in (
                "genre_candidate",
                "supporting_evidence",
                "confidence",
                "source_agents",
            ):
                if subfield not in position:
                    raise SourceEngineError(
                        ErrorCode.HANDOFF_EVIDENCE_DROPPED_NESTED,
                        f'إيقاف مؤقت: الحقل الفرعي "genre_dispute[{index}].{subfield}" '
                        "غائب داخل عنصر القائمة — أعد تشغيل تحليل الاستيعاب",
                    )
    author_output = metadata.get("author_output")
    if isinstance(author_output, dict):
        positions = author_output.get("positions")
        if isinstance(positions, list):
            for index, position in enumerate(positions):
                if not isinstance(position, dict):
                    continue
                if "death_hijri" not in position:
                    detail = (
                        f'إيقاف مؤقت: الحقل الفرعي '
                        f'"author_output.positions[{index}].death_hijri" '
                        f"غائب داخل عنصر القائمة — أعد تشغيل تحليل الاستيعاب"
                    )
                    raise SourceEngineError(
                        ErrorCode.HANDOFF_EVIDENCE_DROPPED_NESTED, detail
                    )


def _validate_volume_count(dossier: IntakeDossier) -> None:
    """Guard per REQ-SRC-0033: multi-volume must have observed_volume_count."""
    observed = dossier.declared_vs_observed_counts.observed_volume_count
    if observed is not None and observed > 1:
        return
    if observed is None and dossier.declared_vs_observed_counts.declared_volume_count is not None:
        raise SourceEngineError(
            ErrorCode.VOLUME_COUNT_MISSING,
            "multi-volume source has null observed_volume_count",
        )


def _unresolved_disputes(disagreement_cases: list[DisagreementCaseRecord]) -> list[dict[str, object]]:
    return [
        record.model_dump(mode="json")
        for record in disagreement_cases
        if record.resolution_state == "genuine_scholarly_dispute"
    ]


def _validate_deliberation_source_identity(
    frozen: FrozenSource,
    deliberation_result: MetadataDeliberationResult,
) -> None:
    if deliberation_result.source_metadata.source_id != frozen.source_id:
        raise SourceEngineError(
            ErrorCode.SOURCE_ID_MISMATCH,
            f"deliberation result source_id={deliberation_result.source_metadata.source_id} does not match frozen source_id={frozen.source_id}",
        )
    if (
        deliberation_result.case_complexity_record.source_id is not None
        and deliberation_result.case_complexity_record.source_id != frozen.source_id
    ):
        raise SourceEngineError(
            ErrorCode.SOURCE_ID_MISMATCH,
            f"case record source_id={deliberation_result.case_complexity_record.source_id} does not match frozen source_id={frozen.source_id}",
        )


def _normalization_author(source_metadata: SourceMetadata) -> str | None:
    if source_metadata.author_output is None or not source_metadata.author_output.positions:
        return None
    if source_metadata.author_output.status == "agent_disagreement":
        return None
    return source_metadata.author_output.positions[0].display_name


def _normalization_work_id(source_metadata: SourceMetadata) -> str | None:
    if source_metadata.work_output is None or source_metadata.work_output.status != "definitive":
        return None
    return source_metadata.work_id
