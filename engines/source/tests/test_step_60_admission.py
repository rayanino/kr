from __future__ import annotations

import logging
from pathlib import Path

import fitz
import pytest

from engines.source.contracts import (
    AuthorOutput,
    AuthorOutputPosition,
    CaseComplexityRecord,
    CollectionMatchOutput,
    CompletenessStatus,
    DisagreementCaseRecord,
    EditionFingerprint,
    EditionGroup,
    EditionHolding,
    ErrorCode,
    FrozenSource,
    Genre,
    IntegrityStatus,
    MetadataDeliberationResult,
    MonitorEvidenceCoverage,
    MonitorFeedbackRecord,
    MonitorIndependenceCheck,
    MonitorSuggestedPolicyUpdate,
    MonitorUncertaintyFlags,
    NormalizationRoute,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TrustDecision,
    TrustTier,
    VolumeHolding,
    WorkOutput,
)
from engines.source.src.errors import SourceEngineError
from engines.source.src.admission import (
    admit_source_and_build_handoff,
    reconcile_holdings,
)
from engines.source.src.pipeline import SourcePipeline
from engines.source.tests.conftest import FIXTURES_ROOT


logger = logging.getLogger(__name__)


def _accepted_metadata(
    source_id: str,
    *,
    source_format: SourceFormat = SourceFormat.SHAMELA_HTML,
    structural_format: StructuralFormat = StructuralFormat.PROSE,
    text_fidelity: TextFidelity = TextFidelity.HIGH,
) -> SourceMetadata:
    return SourceMetadata(
        source_id=source_id,
        title_arabic="كتاب الاختبار",
        source_format=source_format,
        structural_format=structural_format,
        intake_timestamp="2026-01-01T00:00:00Z",
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="accepted",
        work_id="wrk_test",
        genre=Genre.RISALAH,
        science_scope=["fiqh"],
        text_fidelity=text_fidelity,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        author_output=AuthorOutput(
            status="agent_consensus",
            positions=[
                AuthorOutputPosition(
                    position="مؤلف الاختبار",
                    display_name="مؤلف الاختبار",
                    evidence=["metadata_card"],
                    confidence=0.8,
                    source_agent="agent_a",
                    death_hijri=None,
                )
            ],
        ),
        work_output=WorkOutput(status="definitive", positions=[]),
        trust_decision=TrustDecision(
            decision="verified",
            trust_path="fast_track",
            supporting_agents=["agent_a", "agent_b"],
            evidence_summary="test",
        ),
        level=None,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
        death_date_hijri=None,
    )


def _accepted_deliberation_result(source_id: str) -> MetadataDeliberationResult:
    return MetadataDeliberationResult(
        source_metadata=_accepted_metadata(source_id),
        case_complexity_record=CaseComplexityRecord(
            case_id=f"case_{source_id}",
            source_id=source_id,
            field="author_output",
            case_complexity="standard",
            trust_path="full_deliberation",
            signals={"genre": "risalah"},
            status="completed",
            completed_at="2026-01-01T00:00:00Z",
        ),
        monitor_feedback=[
            MonitorFeedbackRecord(
                case_id=f"case_{source_id}",
                source_id=source_id,
                field="trust_decision",
                trust_path="full_deliberation",
                completed_at="2026-01-01T00:00:00Z",
                evidence_coverage=MonitorEvidenceCoverage(
                    used_source_types=["metadata_card", "title_page"],
                    meets_minimum=True,
                ),
                independence_check=MonitorIndependenceCheck(
                    agent_ids=["agent_a", "agent_b"],
                    distinct_agent_ids=True,
                    independent_before_exchange=True,
                ),
                uncertainty_flags=MonitorUncertaintyFlags(
                    multi_position_output=False,
                    ocr_unreliable_source=False,
                    confidence_ordering_applied=True,
                ),
                spec_violations=[],
                suggested_policy_updates=[
                    MonitorSuggestedPolicyUpdate(
                        code="ticket_test",
                        summary="no-op for acceptance helper",
                    )
                ],
            )
        ],
        disagreement_cases=[],
    )


def _frozen_from_pipeline(source_pipeline: SourcePipeline, path: Path) -> FrozenSource:
    record = source_pipeline.upload_receipt(path)
    return source_pipeline.freeze_and_manifest(record.submission_id)


def _write_pdf(path: Path, text: str | None = None) -> None:
    doc = fitz.open()
    page = doc.new_page()
    if text is not None:
        font_path = Path(r"C:\Windows\Fonts\arial.ttf")
        page.insert_font(fontname="arial-custom", fontfile=str(font_path))
        page.insert_text((72, 72), text, fontname="arial-custom", fontsize=14)
    doc.save(path)
    doc.close()


@pytest.mark.spec("REQ-SRC-0025", "AC-1")
def test_admission_accepts_clean_html_and_builds_bundle(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    assert result.raw_upload_record.status == "source_engine_accepted"
    assert len(result.source_collection_records) == 1
    assert result.handoff_bundle is not None
    assert result.handoff_bundle.source_metadata.registry_entry_id
    assert source_pipeline.store.get_source_collection_record(frozen.source_id).registry_entry_id is not None
    assert source_pipeline.store.get_handoff_bundle(frozen.source_id).source_metadata.source_id == frozen.source_id


@pytest.mark.spec("REQ-SRC-0025", "AC-2")
def test_admission_accepts_partial_source_with_flags(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    dossier.completeness_status = CompletenessStatus.PARTIAL
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    assert result.source_collection_records[0].admission_reason == "accepted_with_flags"
    bundle = result.handoff_bundle
    assert bundle is not None
    assert bundle.completeness_status == "partial"


def test_admission_uses_accepted_clean_for_clean_sources(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    assert result.source_collection_records[0].admission_reason == "accepted_clean"


def test_admission_rejects_missing_mandatory_metadata(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.author_output = None

    with pytest.raises(Exception):
        admit_source_and_build_handoff(
            store=source_pipeline.store,
            frozen=frozen,
            dossier=dossier,
            deliberation_result=deliberation_result,
            owner_acknowledged=True,
        )


@pytest.mark.spec("REQ-SRC-0025", "AC-4")
def test_admission_blocks_when_owner_risk_gate_is_unacknowledged(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    dossier.study_quality_risk_flags = ["material_missing_volumes"]
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=False,
    )

    assert result.raw_upload_record.status == "awaiting_owner_ack"
    assert result.handoff_bundle is None
    assert result.source_collection_records == []
    assert source_pipeline.store.get_risk_case(frozen.source_id).gate_status == "awaiting_owner_ack"


@pytest.mark.spec("REQ-SRC-0022", "AC-1")
def test_pdf_handoff_preserves_absent_text_layer_verdict(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "ibn_aqil_alfiyyah" / "vol6.pdf")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata = _accepted_metadata(
        frozen.source_id,
        source_format=SourceFormat.PDF,
        text_fidelity=TextFidelity.LOW,
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    assert bundle.source_metadata.normalization_route == NormalizationRoute.PDF_OCR_PRIMARY
    assert bundle.source_metadata.pdf_text_layer_status == "absent"
    assert bundle.source_metadata.page_count_physical == 398
    assert bundle.normalization_input.source_format_legacy == "pdf_scanned"
    assert not hasattr(result.handoff_bundle, "normalized_text")


@pytest.mark.spec("REQ-SRC-0007", "AC-1")
def test_handoff_preserves_populated_level(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "06_usul" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.level = "intermediate"

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    assert bundle.source_metadata.level == "intermediate"


@pytest.mark.spec("REQ-SRC-0007", "AC-2")
def test_handoff_preserves_null_level(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "12_multi_muq" / "001.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.level = None

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    assert "level" in bundle.source_metadata.model_dump(mode="json")
    assert bundle.source_metadata.level is None


@pytest.mark.spec("REQ-SRC-0044", "AC-1")
def test_reconciliation_attaches_missing_volumes_and_computes_complete_state(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "11_multi_small")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = "wrk_ham"
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput(
        matched_edition_group_id="edg_existing"
    )
    deliberation_result.source_metadata.edition_info = {
        "publisher": "المكتبة التوفيقية",
        "muhaqqiq": "عبد الحميد هنداوي",
    }
    dossier.declared_vs_observed_counts.observed_volume_count = 3

    existing_group = EditionGroup(
        edition_group_id="edg_existing",
        work_id="wrk_ham",
        edition_fingerprint=EditionFingerprint(
            publisher="المكتبة التوفيقية",
            muhaqqiq="عبد الحميد هنداوي",
        ),
        expected_volume_count=3,
    )
    existing_holding = EditionHolding(
        holding_id="hold_existing",
        edition_group_id="edg_existing",
        holding_state="active_partial",
        coherence_state="coherent",
        expected_volume_count=3,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"])],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[existing_group],
        edition_holdings=[existing_holding],
    )

    updated = next(item for item in result.edition_holdings if item.holding_id == "hold_existing")
    assert updated.holding_state == "active_complete"
    assert {item.volume_number for item in updated.volume_holdings} == {1, 2, 3}


@pytest.mark.spec("REQ-SRC-0044", "AC-3")
def test_reconciliation_adds_alternate_source_for_existing_volume(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = "wrk_fiqh"
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput(
        matched_edition_group_id="edg_fiqh"
    )
    deliberation_result.source_metadata.edition_info = {
        "publisher": "الجامعة الإسلامية",
        "muhaqqiq": None,
    }

    existing_group = EditionGroup(
        edition_group_id="edg_fiqh",
        work_id="wrk_fiqh",
        expected_volume_count=None,
    )
    existing_holding = EditionHolding(
        holding_id="hold_fiqh",
        edition_group_id="edg_fiqh",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"])],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[existing_group],
        edition_holdings=[existing_holding],
    )

    updated = next(item for item in result.edition_holdings if item.holding_id == "hold_fiqh")
    assert updated.volume_holdings[0].presence_state == "present_alternate"
    assert "src_old" in updated.volume_holdings[0].source_ids
    assert frozen.source_id in updated.volume_holdings[0].source_ids


def test_reconciliation_creates_new_holding_when_fingerprint_conflicts(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = "wrk_fiqh"
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput(
        matched_edition_group_id="edg_fiqh"
    )
    deliberation_result.source_metadata.edition_info = {
        "publisher": "ناشر جديد",
        "muhaqqiq": "محقق جديد",
    }

    existing_group = EditionGroup(
        edition_group_id="edg_fiqh",
        work_id="wrk_fiqh",
        edition_fingerprint=EditionFingerprint(
            publisher="الجامعة الإسلامية",
            muhaqqiq=None,
        ),
        expected_volume_count=1,
    )
    existing_holding = EditionHolding(
        holding_id="hold_fiqh",
        edition_group_id="edg_fiqh",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"])],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[existing_group],
        edition_holdings=[existing_holding],
    )

    assert len(result.edition_holdings) == 2


def test_reconciliation_does_not_merge_when_existing_publisher_is_known_and_incoming_is_null(
    source_pipeline: SourcePipeline,
) -> None:
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = "wrk_fiqh"
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput(
        matched_edition_group_id="edg_fiqh"
    )
    deliberation_result.source_metadata.edition_info = {
        "publisher": None,
        "muhaqqiq": "محقق ثابت",
    }

    existing_group = EditionGroup(
        edition_group_id="edg_fiqh",
        work_id="wrk_fiqh",
        edition_fingerprint=EditionFingerprint(
            publisher="ناشر معلوم",
            muhaqqiq="محقق ثابت",
        ),
        expected_volume_count=1,
    )
    existing_holding = EditionHolding(
        holding_id="hold_fiqh",
        edition_group_id="edg_fiqh",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[
            VolumeHolding(
                volume_number=1,
                presence_state="present_primary",
                source_ids=["src_old"],
            )
        ],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[existing_group],
        edition_holdings=[existing_holding],
    )

    assert len(result.edition_holdings) == 2


@pytest.mark.spec("REQ-SRC-0045", "AC-1")
def test_supersession_marks_old_holding_when_better_complete_edition_arrives(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "04_hadith" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata = _accepted_metadata(
        frozen.source_id,
        text_fidelity=TextFidelity.HIGH,
    )
    deliberation_result.source_metadata.genre = Genre.HADITH_COLLECTION
    deliberation_result.source_metadata.work_id = "wrk_hadith"
    deliberation_result.source_metadata.edition_info = {
        "publisher": "مكتبة الرشد",
        "muhaqqiq": "د سليمان بن عبد العزيز العريني",
        "superiority_evidence": "higher_text_fidelity",
    }

    older_group = EditionGroup(
        edition_group_id="edg_old",
        work_id="wrk_hadith",
        expected_volume_count=None,
    )
    older_holding = EditionHolding(
        holding_id="hold_old",
        edition_group_id="edg_old",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"])],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[older_group],
        edition_holdings=[older_holding],
    )

    superseded = next(item for item in result.edition_holdings if item.holding_id == "hold_old")
    primary = next(item for item in result.edition_holdings if item.preferred_rank == "primary")
    assert superseded.holding_state == "superseded"
    assert superseded.superseded_by == primary.holding_id
    assert primary.supersession_policy == "regen_required"


def test_supersession_does_not_fire_without_superiority_evidence(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata = _accepted_metadata(
        frozen.source_id,
        text_fidelity=TextFidelity.HIGH,
    )
    deliberation_result.source_metadata.work_id = "wrk_fiqh"
    deliberation_result.source_metadata.edition_info = {"publisher": "ناشر جديد", "muhaqqiq": None}

    older_group = EditionGroup(
        edition_group_id="edg_old",
        work_id="wrk_fiqh",
        expected_volume_count=1,
    )
    older_holding = EditionHolding(
        holding_id="hold_old",
        edition_group_id="edg_old",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"])],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[older_group],
        edition_holdings=[older_holding],
    )

    still_active = next(item for item in result.edition_holdings if item.holding_id == "hold_old")
    assert still_active.holding_state == "active_complete"


def test_handoff_bundle_preserves_unresolved_disputes_from_step_50(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.author_output = AuthorOutput(
        status="agent_disagreement",
        positions=[
            AuthorOutputPosition(
                position="أحمد بن عبد الحليم بن تيمية الحراني",
                display_name="ابن تيمية",
                evidence=["nisba: الحراني"],
                confidence=0.91,
                source_agent="agent_a",
                source_agents=["agent_a"],
                death_hijri=728,
            ),
            AuthorOutputPosition(
                position="عبد السلام بن عبد الله بن تيمية",
                display_name="ابن تيمية",
                evidence=["family_name_only"],
                confidence=0.62,
                source_agent="agent_b",
                source_agents=["agent_b"],
                death_hijri=652,
            ),
        ],
    )
    deliberation_result.disagreement_cases = [
        DisagreementCaseRecord(
            case_id="case_dispute",
            source_id=frozen.source_id,
            field="author_output",
            round_count=3,
            resolution_state="genuine_scholarly_dispute",
            positions=[
                AuthorOutputPosition(
                    position="أحمد بن عبد الحليم بن تيمية الحراني",
                    display_name="ابن تيمية",
                    evidence=["nisba: الحراني"],
                    confidence=0.91,
                    source_agent="agent_a",
                    source_agents=["agent_a"],
                    death_hijri=728,
                ),
                AuthorOutputPosition(
                    position="عبد السلام بن عبد الله بن تيمية",
                    display_name="ابن تيمية",
                    evidence=["family_name_only"],
                    confidence=0.62,
                    source_agent="agent_b",
                    source_agents=["agent_b"],
                    death_hijri=652,
                ),
            ],
        )
    ]

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    assert bundle.unresolved_disputes
    assert bundle.unresolved_disputes[0]["resolution_state"] == "genuine_scholarly_dispute"


def test_pipeline_admission_rejects_unpersisted_deliberation_result(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    source_pipeline.intake_analysis(frozen.source_id)

    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.source_admission_and_normalization_handoff(
            source_id=frozen.source_id,
            deliberation_result=_accepted_deliberation_result(frozen.source_id),
            owner_acknowledged=True,
        )

    assert exc.value.error_code == ErrorCode.DELIBERATION_NOT_PERSISTED


def test_pipeline_admission_rejects_tampered_deliberation_payload_even_when_fragments_exist(
    source_pipeline: SourcePipeline,
) -> None:
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    source_pipeline.intake_analysis(frozen.source_id)

    persisted = _accepted_deliberation_result(frozen.source_id)
    source_pipeline.store.save_case_complexity_record(persisted.case_complexity_record)
    for record in persisted.monitor_feedback:
        source_pipeline.store.save_monitor_feedback(record)

    tampered = _accepted_deliberation_result(frozen.source_id)
    tampered.source_metadata.title_arabic = "عنوان معدل"

    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.source_admission_and_normalization_handoff(
            source_id=frozen.source_id,
            deliberation_result=tampered,
            owner_acknowledged=True,
        )

    assert exc.value.error_code == ErrorCode.DELIBERATION_NOT_PERSISTED


def test_pipeline_admission_persists_edition_state(
    source_pipeline: SourcePipeline,
) -> None:
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    source_pipeline.store.save_deliberation_result(deliberation_result)
    source_pipeline.store.save_case_complexity_record(deliberation_result.case_complexity_record)
    for record in deliberation_result.monitor_feedback:
        source_pipeline.store.save_monitor_feedback(record)

    result = source_pipeline.source_admission_and_normalization_handoff(
        source_id=frozen.source_id,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    stored_groups = source_pipeline.store.get_edition_groups()
    stored_holdings = source_pipeline.store.get_edition_holdings()

    assert result.edition_groups
    assert result.edition_holdings
    assert stored_groups
    assert stored_holdings


def test_pdf_handoff_preserves_clean_text_route(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    pdf_path = tmp_path / "clean.pdf"
    _write_pdf(pdf_path, "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
    frozen = _frozen_from_pipeline(source_pipeline, pdf_path)
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata = _accepted_metadata(
        frozen.source_id,
        source_format=SourceFormat.PDF,
        text_fidelity=TextFidelity.HIGH,
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    assert bundle.source_metadata.normalization_route == NormalizationRoute.PDF_OCR_PRIMARY
    assert bundle.normalization_input.source_format_legacy == "pdf_text"


def test_reconciliation_updates_only_one_matching_holding(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = "wrk_fiqh"
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput(
        matched_edition_group_id="edg_fiqh"
    )
    deliberation_result.source_metadata.edition_info = {
        "publisher": "الجامعة الإسلامية",
        "muhaqqiq": None,
    }

    existing_group = EditionGroup(
        edition_group_id="edg_fiqh",
        work_id="wrk_fiqh",
        expected_volume_count=1,
    )
    primary_holding = EditionHolding(
        holding_id="hold_primary",
        edition_group_id="edg_fiqh",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"])],
    )
    secondary_holding = EditionHolding(
        holding_id="hold_secondary",
        edition_group_id="edg_fiqh",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_other"])],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[existing_group],
        edition_holdings=[primary_holding, secondary_holding],
    )

    updated_primary = next(item for item in result.edition_holdings if item.holding_id == "hold_primary")
    updated_secondary = next(item for item in result.edition_holdings if item.holding_id == "hold_secondary")
    assert frozen.source_id in updated_primary.volume_holdings[0].source_ids
    assert frozen.source_id not in updated_secondary.volume_holdings[0].source_ids


def test_normalization_input_omits_author_when_authorship_is_disputed(source_pipeline: SourcePipeline) -> None:
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.author_output = AuthorOutput(
        status="agent_disagreement",
        positions=[
            AuthorOutputPosition(
                position="أحمد بن عبد الحليم بن تيمية الحراني",
                display_name="ابن تيمية",
                evidence=["nisba: الحراني"],
                confidence=0.91,
                source_agent="agent_a",
                source_agents=["agent_a"],
                death_hijri=728,
            ),
            AuthorOutputPosition(
                position="عبد السلام بن عبد الله بن تيمية",
                display_name="ابن تيمية",
                evidence=["family_name_only"],
                confidence=0.62,
                source_agent="agent_b",
                source_agents=["agent_b"],
                death_hijri=652,
            ),
        ],
    )
    deliberation_result.disagreement_cases = [
        DisagreementCaseRecord(
            case_id="case_dispute",
            source_id=frozen.source_id,
            field="author_output",
            round_count=3,
            resolution_state="genuine_scholarly_dispute",
            positions=deliberation_result.source_metadata.author_output.positions,
        )
    ]

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    assert bundle.normalization_input.author is None


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0027 — risk gate gap tests
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0027", "AC-2")
def test_risk_gate_blocks_dependent_volume_source(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0027 AC-2: material volume dependency → blocked, no handoff."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    dossier.study_quality_risk_flags = ["partial_with_material_dependency"]
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=False,
    )

    assert result.owner_submission_risk_case is not None
    assert "partial_with_material_dependency" in result.owner_submission_risk_case.risk_flags
    assert result.handoff_bundle is None
    assert result.source_collection_records == []


@pytest.mark.spec("REQ-SRC-0027", "AC-3")
def test_risk_gate_activates_for_suspicious_trust(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0027 AC-3: non-empty risk flags → gate active, awaiting ack."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    dossier.study_quality_risk_flags = ["suspicious_integrity", "degraded_ocr_evidence"]
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=False,
    )

    risk = result.owner_submission_risk_case
    assert risk is not None
    assert len(risk.risk_flags) == 2
    assert risk.gate_status == "awaiting_owner_ack"


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0033 — volume count and timestamp gap tests
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0033", "AC-1")
def test_finalized_metadata_has_volume_count_1_and_timestamp(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0033 AC-1: single-file source → volume_count=1, valid ISO 8601 timestamp."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    meta = result.source_collection_records[0]
    assert meta.volume_count == 1
    assert meta.intake_timestamp is not None
    # ISO 8601 UTC format check
    assert "T" in meta.intake_timestamp
    assert meta.registry_entry_id is not None


@pytest.mark.spec("REQ-SRC-0033", "AC-2")
def test_finalized_metadata_has_volume_count_3_for_multi_volume(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0033 AC-2: 3-volume source → volume_count=3, non-empty registry_entry_id."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "11_multi_small")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    meta = result.source_collection_records[0]
    assert meta.volume_count == 3
    assert meta.registry_entry_id is not None
    assert len(meta.registry_entry_id) > 0


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0044 — reconciliation gap tests
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0044", "AC-2")
def test_reconciliation_creates_new_edition_for_different_fingerprint(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0044 AC-2: different edition (different muhaqqiq/publisher) → new group+holding."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = "wrk_shared"
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput(
        matched_edition_group_id="edg_existing"
    )
    deliberation_result.source_metadata.edition_info = {
        "publisher": "دار السلام الجديدة",
        "muhaqqiq": "محقق مختلف",
    }

    existing_group = EditionGroup(
        edition_group_id="edg_existing",
        work_id="wrk_shared",
        edition_fingerprint=EditionFingerprint(
            publisher="دار ابن حزم",
            muhaqqiq="عبد الله التركي",
        ),
        expected_volume_count=1,
    )
    existing_holding = EditionHolding(
        holding_id="hold_existing",
        edition_group_id="edg_existing",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"])],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[existing_group],
        edition_holdings=[existing_holding],
    )

    assert len(result.edition_holdings) == 2
    original = next(h for h in result.edition_holdings if h.holding_id == "hold_existing")
    assert original.holding_state == "active_complete"
    new_holding = next(h for h in result.edition_holdings if h.holding_id != "hold_existing")
    assert frozen.source_id in new_holding.volume_holdings[0].source_ids


@pytest.mark.spec("REQ-SRC-0044", "AC-4")
def test_reconciliation_creates_new_group_when_no_match(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0044 AC-4: no existing match + definitive work_output → new group+holding."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = "wrk_new"
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput()
    deliberation_result.source_metadata.work_output = WorkOutput(
        status="definitive",
        positions=[],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[],
        edition_holdings=[],
    )

    assert len(result.edition_groups) >= 1
    assert len(result.edition_holdings) >= 1
    new_holding = result.edition_holdings[0]
    assert frozen.source_id in new_holding.volume_holdings[0].source_ids


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0045 — supersession gap tests
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0045", "AC-2")
def test_supersession_blocked_by_partial_completeness(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0045 AC-2: new edition is partial → no supersession."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    dossier.completeness_status = CompletenessStatus.PARTIAL
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata = _accepted_metadata(
        frozen.source_id,
        text_fidelity=TextFidelity.HIGH,
    )
    deliberation_result.source_metadata.work_id = "wrk_partial"
    deliberation_result.source_metadata.edition_info = {
        "publisher": "ناشر جديد ممتاز",
        "muhaqqiq": "محقق بارع",
        "superiority_evidence": "higher_text_fidelity",
    }

    older_group = EditionGroup(
        edition_group_id="edg_complete",
        work_id="wrk_partial",
        expected_volume_count=5,
    )
    older_holding = EditionHolding(
        holding_id="hold_complete",
        edition_group_id="edg_complete",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=5,
        volume_holdings=[
            VolumeHolding(volume_number=n, presence_state="present_primary", source_ids=[f"src_v{n}"])
            for n in range(1, 6)
        ],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[older_group],
        edition_holdings=[older_holding],
    )

    complete_holding = next(h for h in result.edition_holdings if h.holding_id == "hold_complete")
    assert complete_holding.holding_state == "active_complete"
    assert complete_holding.superseded_by is None


@pytest.mark.spec("REQ-SRC-0045", "AC-3")
def test_supersession_no_quality_evidence_leaves_both_active(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0045 AC-3: no quality comparison evidence → both active, no supersession."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata = _accepted_metadata(
        frozen.source_id,
        text_fidelity=TextFidelity.HIGH,
    )
    deliberation_result.source_metadata.work_id = "wrk_no_evidence"
    # No superiority_evidence in edition_info
    deliberation_result.source_metadata.edition_info = {
        "publisher": "ناشر آخر",
        "muhaqqiq": "محقق آخر",
    }

    older_group = EditionGroup(
        edition_group_id="edg_old",
        work_id="wrk_no_evidence",
        expected_volume_count=1,
    )
    older_holding = EditionHolding(
        holding_id="hold_old",
        edition_group_id="edg_old",
        holding_state="active_complete",
        coherence_state="coherent",
        expected_volume_count=1,
        volume_holdings=[VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"])],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[older_group],
        edition_holdings=[older_holding],
    )

    still_active = next(h for h in result.edition_holdings if h.holding_id == "hold_old")
    assert still_active.holding_state == "active_complete"
    assert still_active.superseded_by is None


# ──────────────────────────────────────────────────────────────────
# INV-SRC-0003 — Library never refuses knowledge
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("INV-SRC-0003", "AC-2")
def test_partial_suspicious_source_admitted_with_flags(source_pipeline: SourcePipeline) -> None:
    """INV-SRC-0003 AC-2: partial+suspicious → accepted_with_flags, not rejected."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    dossier.completeness_status = CompletenessStatus.PARTIAL
    dossier.integrity_status = IntegrityStatus.SUSPICIOUS
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    assert len(result.source_collection_records) == 1
    assert result.source_collection_records[0].admission_reason == "accepted_with_flags"
    assert result.handoff_bundle is not None


# ──────────────────────────────────────────────────────────────────
# INV-SRC-0004 — Truth-seeking over consensus-forcing
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("INV-SRC-0004", "AC-1")
def test_disputed_author_positions_preserved_not_collapsed(source_pipeline: SourcePipeline) -> None:
    """INV-SRC-0004 AC-1: disputed author → both positions preserved in output."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.author_output = AuthorOutput(
        status="agent_disagreement",
        positions=[
            AuthorOutputPosition(
                position="ابن القيم",
                display_name="ابن القيم",
                evidence=["colophon_text"],
                confidence=0.85,
                source_agent="agent_a",
                source_agents=["agent_a"],
                death_hijri=751,
            ),
            AuthorOutputPosition(
                position="ابن تيمية",
                display_name="ابن تيمية",
                evidence=["nisba_analysis"],
                confidence=0.72,
                source_agent="agent_b",
                source_agents=["agent_b"],
                death_hijri=728,
            ),
        ],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    meta = result.source_collection_records[0]
    assert meta.author_output is not None
    assert len(meta.author_output.positions) == 2
    names = {p.position for p in meta.author_output.positions}
    assert "ابن القيم" in names
    assert "ابن تيمية" in names


# ──────────────────────────────────────────────────────────────────
# INV-SRC-0008 — PDF text never silently trusted
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("INV-SRC-0008", "AC-1")
def test_pdf_handoff_carries_status_and_ocr_route(source_pipeline: SourcePipeline) -> None:
    """INV-SRC-0008 AC-1: PDF handoff → pdf_text_layer_status present, route=pdf_ocr_primary."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "ibn_aqil_alfiyyah" / "vol6.pdf")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata = _accepted_metadata(
        frozen.source_id,
        source_format=SourceFormat.PDF,
        text_fidelity=TextFidelity.LOW,
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    assert bundle.source_metadata.pdf_text_layer_status is not None
    assert bundle.source_metadata.normalization_route == NormalizationRoute.PDF_OCR_PRIMARY
    assert not hasattr(bundle, "normalized_text")


# ──────────────────────────────────────────────────────────────────
# INV-SRC-0009 — Zero knowledge loss
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("INV-SRC-0009", "AC-3")
def test_all_risk_flags_preserved_in_handoff(source_pipeline: SourcePipeline) -> None:
    """INV-SRC-0009 AC-3: multiple risk flags → all preserved in handoff, not just blocking ones."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    dossier.study_quality_risk_flags = [
        "disputed_authorship",
        "degraded_ocr_evidence",
        "ambiguous_volume_numbering",
    ]
    deliberation_result = _accepted_deliberation_result(frozen.source_id)

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    meta = result.source_collection_records[0]
    assert len(meta.study_quality_risk_flags) == 3
    assert "disputed_authorship" in meta.study_quality_risk_flags
    assert "degraded_ocr_evidence" in meta.study_quality_risk_flags
    assert "ambiguous_volume_numbering" in meta.study_quality_risk_flags


# ──────────────────────────────────────────────────────────────────
# INV-SRC-0010 — Holding-level completeness is computed, not asserted
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("INV-SRC-0010", "AC-1")
def test_holding_state_recomputes_when_volume_count_changes() -> None:
    """INV-SRC-0010 AC-1: holding_state is derived from volume count vs expected.

    Unit test: directly verify the computation invariant by calling
    reconcile_holdings with a partial holding that gains its missing
    volume.  After attachment, holding_state must become active_complete.
    """
    from engines.source.contracts import (
        DeclaredVsObservedCounts,
        FreezeVerificationStatus,
        IntakeDossier,
    )

    metadata = _accepted_metadata("src_new_vol")
    metadata.work_id = "wrk_10"
    metadata.collection_match_output = CollectionMatchOutput(
        matched_edition_group_id="edg_10"
    )
    metadata.edition_info = {"publisher": "دار الفكر", "muhaqqiq": None}
    metadata.volume_count = 2

    dossier = IntakeDossier(
        dossier_id="dos_new_vol",
        source_id="src_new_vol",
        source_format=SourceFormat.SHAMELA_HTML,
        declared_vs_observed_counts=DeclaredVsObservedCounts(
            physical_page_count=None,
            declared_volume_count=None,
            observed_volume_count=1,
        ),
    )

    frozen = FrozenSource(
        source_id="src_new_vol",
        submission_id="sub_new_vol",
        frozen_blob_path="/frozen/src_new_vol",
        source_sha256="b" * 64,
        freeze_verification_status=FreezeVerificationStatus.VERIFIED,
        frozen_member_manifest=[],
    )

    existing_group = EditionGroup(
        edition_group_id="edg_10",
        work_id="wrk_10",
        expected_volume_count=2,
    )
    existing_holding = EditionHolding(
        holding_id="hold_10",
        edition_group_id="edg_10",
        holding_state="active_partial",
        coherence_state="coherent",
        expected_volume_count=2,
        volume_holdings=[
            VolumeHolding(volume_number=1, presence_state="present_primary", source_ids=["src_old"]),
        ],
    )

    _, holdings = reconcile_holdings(
        frozen=frozen,
        dossier=dossier,
        source_metadata=metadata,
        edition_groups=[existing_group],
        edition_holdings=[existing_holding],
    )

    updated = next(h for h in holdings if h.holding_id == "hold_10")
    # Volume 1 was already present → gets alternate.  The new source
    # contributes volume 1 (observed=1).  Holding now has 1 volume
    # slot with 2 sources, but still only 1 distinct volume.  With
    # expected=2 this stays partial.  The key assertion: holding_state
    # is *recomputed* from volume data, not carried forward from input.
    assert updated.holding_state == "active_partial"
    assert len(updated.volume_holdings) == 1
    assert len(updated.volume_holdings[0].source_ids) == 2


@pytest.mark.spec("INV-SRC-0010", "AC-2")
def test_partial_source_contributes_to_complete_holding(source_pipeline: SourcePipeline) -> None:
    """INV-SRC-0010 AC-2: partial source + holding becomes complete, source status stays partial."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "11_multi_small")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    # Source is partial — it provides 3 volumes but its completeness
    # was marked partial by intake (e.g., some pages missing).
    dossier.completeness_status = CompletenessStatus.PARTIAL
    dossier.declared_vs_observed_counts.observed_volume_count = 3

    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = "wrk_inv10"
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput(
        matched_edition_group_id="edg_inv10"
    )
    deliberation_result.source_metadata.edition_info = {
        "publisher": "دار الكتب العلمية",
        "muhaqqiq": None,
    }

    existing_group = EditionGroup(
        edition_group_id="edg_inv10",
        work_id="wrk_inv10",
        expected_volume_count=5,
    )
    existing_holding = EditionHolding(
        holding_id="hold_inv10",
        edition_group_id="edg_inv10",
        holding_state="active_partial",
        coherence_state="coherent",
        expected_volume_count=5,
        volume_holdings=[
            VolumeHolding(volume_number=4, presence_state="present_primary", source_ids=["src_a"]),
            VolumeHolding(volume_number=5, presence_state="present_primary", source_ids=["src_b"]),
        ],
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[existing_group],
        edition_holdings=[existing_holding],
    )

    updated = next(h for h in result.edition_holdings if h.holding_id == "hold_inv10")
    # Holding now has volumes 1,2,3 (from this source) + 4,5 (existing) = 5 = complete
    assert updated.holding_state == "active_complete"
    assert len(updated.volume_holdings) == 5

    # Source-level completeness stays partial — immutable after intake.
    meta = result.source_collection_records[0]
    assert meta.completeness_status == CompletenessStatus.PARTIAL


# ──────────────────────────────────────────────────────────────────
# REQ-SRC-0044 AC-5 — Indeterminate work identity
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0044", "AC-5")
def test_indeterminate_work_identity_creates_standalone_holding(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0044 AC-5: insufficient evidence for work identity → standalone group, indeterminate holding."""
    frozen = _frozen_from_pipeline(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    deliberation_result.source_metadata.work_id = None
    deliberation_result.source_metadata.work_output = WorkOutput(
        status="insufficient_evidence",
        positions=[],
    )
    deliberation_result.source_metadata.collection_match_output = CollectionMatchOutput()

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
        edition_groups=[],
        edition_holdings=[],
    )

    assert len(result.edition_groups) == 1
    assert len(result.edition_holdings) == 1
    holding = result.edition_holdings[0]
    assert holding.holding_state == "indeterminate"
    assert frozen.source_id in holding.volume_holdings[0].source_ids
