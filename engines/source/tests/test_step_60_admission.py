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
from engines.source.src.admission import admit_source_and_build_handoff
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
    assert bundle.source_metadata.normalization_route == NormalizationRoute.PDF_TEXT_PRIMARY
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
