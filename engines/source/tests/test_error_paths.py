"""Tests for spec-defined error paths.

Each test verifies that a specific ErrorCode or WarningCode is raised
under the conditions described in the corresponding spec atom's
error_conditions field. Organized by pipeline step.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from engines.source.contracts import (
    AuthorOutput,
    AuthorOutputPosition,
    CaseComplexityRecord,
    ErrorCode,
    FrozenSource,
    Genre,
    IntakeDossier,
    IntegrityStatus,
    MetadataDeliberationInput,
    MetadataDeliberationResult,
    MonitorEvidenceCoverage,
    MonitorFeedbackRecord,
    MonitorIndependenceCheck,
    MonitorUncertaintyFlags,
    NormalizationRoute,
    PdfTextLayerStatus,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TrustDecision,
    TrustTier,
    WarningCode,
    WorkOutput,
)
from engines.source.src.admission import _validate_pdf_handoff, admit_source_and_build_handoff
from engines.source.src.deliberation import (
    _validate_dossier_complete,
    _validate_work_output,
)
from engines.source.src.errors import SourceEngineError
from engines.source.src.pipeline import SourcePipeline
from engines.source.tests.conftest import FIXTURES_ROOT


# ──────────────────────────────────────────────────────────────────
# Step 10 — upload_receipt
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0001", "error-PATH-NOT-FOUND")
def test_upload_receipt_rejects_missing_path(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0001: missing path → SRC-E-PATH-NOT-FOUND."""
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "does_not_exist" / "book.htm")
    assert exc.value.error_code == ErrorCode.PATH_NOT_FOUND


@pytest.mark.spec("REQ-SRC-0001", "error-EMPTY-FILE")
def test_upload_receipt_rejects_empty_file(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    """REQ-SRC-0001: 0-byte file → SRC-E-EMPTY-FILE."""
    empty = tmp_path / "empty.htm"
    empty.write_bytes(b"")
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.upload_receipt(empty)
    assert exc.value.error_code == ErrorCode.EMPTY_FILE


@pytest.mark.spec("REQ-SRC-0001", "error-PATH-UNREADABLE")
def test_upload_receipt_rejects_unreadable_path(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    """REQ-SRC-0001: path exists but not readable → SRC-E-PATH-UNREADABLE."""
    locked = tmp_path / "locked.htm"
    locked.write_text("content", encoding="utf-8")
    with patch("os.access", return_value=False):
        with pytest.raises(SourceEngineError) as exc:
            source_pipeline.upload_receipt(locked)
        assert exc.value.error_code == ErrorCode.PATH_UNREADABLE


# ──────────────────────────────────────────────────────────────────
# Step 20 — freeze_and_manifest
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0018", "error-DUPLICATE-INGEST")
def test_freeze_rejects_duplicate_ingest(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0018: same file frozen twice → SRC-E-DUPLICATE-INGEST."""
    receipt = source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.freeze_and_manifest(receipt.submission_id)
    receipt_2 = source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.freeze_and_manifest(receipt_2.submission_id)
    assert exc.value.error_code == ErrorCode.DUPLICATE_INGEST


@pytest.mark.spec("REQ-SRC-0018", "error-FREEZE-VERIFY")
def test_freeze_rejects_sha_mismatch(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    """REQ-SRC-0018: SHA changes during freeze → SRC-E-FREEZE-VERIFY."""
    source = tmp_path / "volatile.htm"
    source.write_text("<html>بسم الله</html>", encoding="utf-8")
    receipt = source_pipeline.upload_receipt(source)
    # Modify the file between receipt and freeze to cause SHA mismatch
    source.write_text("<html>بسم الله الرحمن الرحيم</html>", encoding="utf-8")
    # The freeze copies first, then verifies — but since the source changed,
    # the copy will differ from the original hash. We need to simulate
    # a frozen copy that diverges from the original manifest.
    # Actually, the pipeline hashes before copying, then re-hashes after.
    # Since we changed the file, the first hash won't match any existing frozen
    # source, so DUPLICATE_INGEST won't fire. But the frozen copy will match
    # the NEW content while source_sha256 was computed from the OLD content.
    # Wait — the pipeline re-reads the source when building the manifest inside
    # freeze_and_manifest. So the hash will be from the modified file.
    # The real way to trigger FREEZE_VERIFY is to have the copy operation
    # produce a different result from the source. Let's mock the copy step.
    original_freeze = source_pipeline._freeze_source

    def corrupt_freeze(source_path: Path, source_id: str) -> Path:
        target = original_freeze(source_path, source_id)
        # Corrupt one frozen file to make SHA mismatch
        for f in Path(target).rglob("*"):
            if f.is_file():
                f.write_bytes(f.read_bytes() + b"\x00")
                break
        return target

    with patch.object(source_pipeline, "_freeze_source", corrupt_freeze):
        with pytest.raises(SourceEngineError) as exc:
            source_pipeline.freeze_and_manifest(receipt.submission_id)
        assert exc.value.error_code == ErrorCode.FREEZE_VERIFY


# ──────────────────────────────────────────────────────────────────
# Step 30 — container_classification
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0041", "error-EMPTY-DIRECTORY")
def test_classification_rejects_empty_directory(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    """REQ-SRC-0041: directory with only supplementary files → SRC-E-EMPTY-DIRECTORY."""
    source_dir = tmp_path / "source_dir"
    source_dir.mkdir()
    # Create only non-numbered (supplementary) files — no primary content
    (source_dir / "appendix.htm").write_text("<html>ملحق</html>", encoding="utf-8")
    (source_dir / "introduction.htm").write_text("<html>مقدمة</html>", encoding="utf-8")
    receipt = source_pipeline.upload_receipt(source_dir)
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.classify_container(frozen.source_id)
    assert exc.value.error_code == ErrorCode.EMPTY_DIRECTORY


@pytest.mark.spec("REQ-SRC-0041", "warning-MIXED-FORMAT")
def test_classification_emits_mixed_format_warning(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    """REQ-SRC-0041: mixed file types → SRC-W-MIXED-FORMAT warning."""
    source_dir = tmp_path / "mixed_dir"
    source_dir.mkdir()
    (source_dir / "chapter.htm").write_text("<html>فصل</html>", encoding="utf-8")
    (source_dir / "notes.txt").write_text("ملاحظات", encoding="utf-8")
    receipt = source_pipeline.upload_receipt(source_dir)
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    classification = source_pipeline.classify_container(frozen.source_id)
    assert WarningCode.MIXED_FORMAT in classification.warnings


@pytest.mark.spec("REQ-SRC-0020", "error-ENCODING")
def test_classification_rejects_undecodable_encoding(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    """REQ-SRC-0020: undecodable text file → SRC-E-ENCODING."""
    bad_file = tmp_path / "garbage.htm"
    # All 128 high bytes — charset_normalizer returns None for this pattern
    bad_file.write_bytes(bytes(range(128, 256)) * 3)
    receipt = source_pipeline.upload_receipt(bad_file)
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    source_pipeline.classify_container(frozen.source_id)
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.intake_analysis(frozen.source_id)
    assert exc.value.error_code == ErrorCode.ENCODING


# ──────────────────────────────────────────────────────────────────
# Step 40 — intake_analysis
# ──────────────────────────────────────────────────────────────────


@pytest.mark.spec("REQ-SRC-0021", "error-PDF-CORRUPT")
def test_intake_rejects_corrupt_pdf(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    """REQ-SRC-0021: corrupted PDF → SRC-E-PDF-CORRUPT."""
    bad_pdf = tmp_path / "corrupt.pdf"
    bad_pdf.write_bytes(b"%PDF-1.4 GARBAGE DATA NOT A REAL PDF")
    receipt = source_pipeline.upload_receipt(bad_pdf)
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    source_pipeline.classify_container(frozen.source_id)
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.intake_analysis(frozen.source_id)
    assert exc.value.error_code == ErrorCode.PDF_CORRUPT


# ──────────────────────────────────────────────────────────────────
# Step 50 — metadata_deliberation
# ──────────────────────────────────────────────────────────────────


def _base_request(source_id: str = "src_test") -> MetadataDeliberationInput:
    """Minimal valid deliberation input for error path testing."""
    return MetadataDeliberationInput(
        source_id=source_id,
        title_arabic="كتاب الاختبار",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        acquisition_path="manual",
        frozen_path="library/sources/src_test/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="accepted",
        science_scope=["fiqh"],
        genre=Genre.RISALAH,
        is_multi_layer=False,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        author_positions=[
            AuthorOutputPosition(
                position="مؤلف الاختبار",
                display_name="مؤلف الاختبار",
                evidence=["metadata_card"],
                confidence=0.8,
                source_agent="agent_a",
                death_hijri=None,
            ),
            AuthorOutputPosition(
                position="مؤلف الاختبار",
                display_name="مؤلف الاختبار",
                evidence=["title_page"],
                confidence=0.75,
                source_agent="agent_b",
                death_hijri=None,
            ),
        ],
        owner_hint_payload={},
        verification_agents=["agent_a", "agent_b"],
        research_source_types=["metadata_card", "title_page"],
        author_death_hijri=None,
    )


@pytest.mark.spec("REQ-SRC-0004", "error-AUTHOR-AGENT-COUNT")
def test_deliberation_rejects_single_author_agent(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0004: < 2 independent author agents → SRC-E-AUTHOR-AGENT-COUNT."""
    receipt = source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    source_pipeline.classify_container(frozen.source_id)
    source_pipeline.intake_analysis(frozen.source_id)
    request = _base_request(source_id=frozen.source_id)
    request.author_positions = [
        AuthorOutputPosition(
            position="مؤلف واحد",
            display_name="مؤلف واحد",
            evidence=["metadata_card"],
            confidence=0.9,
            source_agent="agent_a",
            death_hijri=None,
        ),
    ]
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.metadata_deliberation(source_id=frozen.source_id, deliberation_input=request)
    assert exc.value.error_code == ErrorCode.AUTHOR_AGENT_COUNT


@pytest.mark.spec("REQ-SRC-0002", "error-HINT-FIELD")
def test_deliberation_rejects_invalid_hint_field(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0002: invalid hint key → SRC-E-HINT-FIELD."""
    receipt = source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    source_pipeline.classify_container(frozen.source_id)
    source_pipeline.intake_analysis(frozen.source_id)
    request = _base_request(source_id=frozen.source_id)
    request.owner_hint_payload = {"publisher": "دار الفكر"}
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.metadata_deliberation(source_id=frozen.source_id, deliberation_input=request)
    assert exc.value.error_code == ErrorCode.HINT_FIELD


@pytest.mark.spec("REQ-SRC-0008", "error-TRUST-AGENT-COUNT")
def test_deliberation_rejects_single_trust_agent(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0008: < 2 verification agents → SRC-E-TRUST-AGENT-COUNT."""
    receipt = source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    source_pipeline.classify_container(frozen.source_id)
    source_pipeline.intake_analysis(frozen.source_id)
    request = _base_request(source_id=frozen.source_id)
    request.verification_agents = ["agent_a"]
    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.metadata_deliberation(source_id=frozen.source_id, deliberation_input=request)
    assert exc.value.error_code == ErrorCode.TRUST_AGENT_COUNT


@pytest.mark.spec("REQ-SRC-0028", "error-DOSSIER-INCOMPLETE")
def test_dossier_incomplete_rejects_missing_fields() -> None:
    """REQ-SRC-0028: missing completeness_status → SRC-E-DOSSIER-INCOMPLETE."""
    dossier = IntakeDossier(
        dossier_id="test",
        source_id="src_test",
        completeness_status=None,
        integrity_status=IntegrityStatus.SOUND,
    )
    with pytest.raises(SourceEngineError) as exc:
        _validate_dossier_complete(dossier)
    assert exc.value.error_code == ErrorCode.DOSSIER_INCOMPLETE


@pytest.mark.spec("REQ-SRC-0026", "error-WORK-OUTPUT-MISSING")
def test_work_output_missing_rejects_none() -> None:
    """REQ-SRC-0026: work_output is None → SRC-E-WORK-OUTPUT-MISSING."""
    with pytest.raises(SourceEngineError) as exc:
        _validate_work_output(None)  # type: ignore[arg-type]
    assert exc.value.error_code == ErrorCode.WORK_OUTPUT_MISSING


@pytest.mark.spec("REQ-SRC-0026", "error-WORK-EVIDENCE")
def test_work_output_definitive_without_positions_rejects() -> None:
    """REQ-SRC-0026: definitive with no positions → SRC-E-WORK-EVIDENCE."""
    empty_definitive = WorkOutput(status="definitive", positions=[])
    with pytest.raises(SourceEngineError) as exc:
        _validate_work_output(empty_definitive)
    assert exc.value.error_code == ErrorCode.WORK_EVIDENCE


@pytest.mark.spec("REQ-SRC-0029", "error-INCOMPLETE-RESEARCH")
def test_monitor_flags_single_research_source(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0029: single research source_type → SRC-E-INCOMPLETE-RESEARCH in spec_violations."""
    receipt = source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    source_pipeline.classify_container(frozen.source_id)
    source_pipeline.intake_analysis(frozen.source_id)
    request = _base_request(source_id=frozen.source_id)
    request.research_source_types = ["metadata_card"]
    result = source_pipeline.metadata_deliberation(source_id=frozen.source_id, deliberation_input=request)
    assert result.monitor_feedback[0].evidence_coverage.meets_minimum is False
    assert ErrorCode.INCOMPLETE_RESEARCH in result.monitor_feedback[0].spec_violations


# ──────────────────────────────────────────────────────────────────
# Step 60 — source_admission_and_normalization_handoff
# ──────────────────────────────────────────────────────────────────


def _accepted_metadata(
    source_id: str,
    *,
    source_format: SourceFormat = SourceFormat.SHAMELA_HTML,
    pdf_text_layer_status: PdfTextLayerStatus | None = None,
    normalization_route: NormalizationRoute | None = None,
) -> SourceMetadata:
    return SourceMetadata(
        source_id=source_id,
        title_arabic="كتاب الاختبار",
        source_format=source_format,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-01-01T00:00:00Z",
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="accepted",
        work_id="wrk_test",
        genre=Genre.RISALAH,
        science_scope=["fiqh"],
        text_fidelity=TextFidelity.HIGH,
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
                ),
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
        pdf_text_layer_status=pdf_text_layer_status,
        normalization_route=normalization_route,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
        death_date_hijri=None,
    )


def _deliberation_result(source_id: str, metadata: SourceMetadata) -> MetadataDeliberationResult:
    return MetadataDeliberationResult(
        source_metadata=metadata,
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
                suggested_policy_updates=[],
            )
        ],
        disagreement_cases=[],
    )


@pytest.mark.spec("REQ-SRC-0022", "error-PDF-STATUS-MISSING")
def test_handoff_rejects_pdf_without_text_layer_status(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0022: PDF source missing pdf_text_layer_status → SRC-E-PDF-STATUS-MISSING."""
    frozen = _freeze_fixture(source_pipeline, "shamela_real/03_fiqh/book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    # Override dossier to claim PDF format — _finalize_metadata uses dossier.source_format
    # as ground truth, overwriting the deliberation metadata's source_format.
    pdf_dossier = dossier.model_copy(update={
        "source_format": SourceFormat.PDF,
        "pdf_text_layer_status": None,
    })
    metadata = _accepted_metadata(
        frozen.source_id,
        source_format=SourceFormat.PDF,
        pdf_text_layer_status=None,
        normalization_route=NormalizationRoute.PDF_OCR_PRIMARY,
    )
    delib = _deliberation_result(frozen.source_id, metadata)
    _persist_deliberation(source_pipeline, delib)
    with pytest.raises(SourceEngineError) as exc:
        admit_source_and_build_handoff(
            store=source_pipeline.store,
            frozen=frozen,
            dossier=pdf_dossier,
            deliberation_result=delib,
            owner_acknowledged=True,
        )
    assert exc.value.error_code == ErrorCode.PDF_STATUS_MISSING


@pytest.mark.spec("REQ-SRC-0022", "error-PDF-ROUTE")
def test_handoff_rejects_pdf_with_wrong_route() -> None:
    """REQ-SRC-0022: PDF metadata with non-pdf_ocr_primary route → SRC-E-PDF-ROUTE.

    Unit test against _validate_pdf_handoff directly.  In normal flow
    _finalize_metadata forces the correct route via _source_metadata_route,
    so this guard is a safety net — tested at the unit level.
    """
    metadata = _accepted_metadata(
        "unit_test_src",
        source_format=SourceFormat.PDF,
        pdf_text_layer_status=PdfTextLayerStatus.CLEAN,
        normalization_route=NormalizationRoute.PDF_TEXT_PRIMARY,
    )
    with pytest.raises(SourceEngineError) as exc:
        _validate_pdf_handoff(metadata)
    assert exc.value.error_code == ErrorCode.PDF_ROUTE


@pytest.mark.spec("REQ-SRC-0027", "AC-1")
def test_risk_gate_passes_when_no_risk_flags(source_pipeline: SourcePipeline) -> None:
    """REQ-SRC-0027 AC-1: empty risk flags → no risk case, source admitted."""
    frozen = _freeze_fixture(source_pipeline, "shamela_real/03_fiqh/book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    metadata = _accepted_metadata(frozen.source_id)
    delib = _deliberation_result(frozen.source_id, metadata)
    _persist_deliberation(source_pipeline, delib)
    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=delib,
        owner_acknowledged=True,
    )
    assert result.owner_submission_risk_case is None
    assert result.handoff_bundle is not None


@pytest.mark.spec("REQ-SRC-0025", "AC-4")
def test_risk_gate_blocks_admission_when_unacknowledged(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    """REQ-SRC-0025 AC-4: risk flags + no owner ack → blocked, no handoff."""
    frozen = _freeze_fixture(source_pipeline, "shamela_real/03_fiqh/book.htm")
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    # Inject risk flags into the dossier
    dossier.study_quality_risk_flags = ["suspicious_integrity"]
    source_pipeline.store.save_intake_dossier(dossier)
    metadata = _accepted_metadata(frozen.source_id)
    delib = _deliberation_result(frozen.source_id, metadata)
    _persist_deliberation(source_pipeline, delib)
    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=delib,
        owner_acknowledged=False,
    )
    assert result.owner_submission_risk_case is not None
    assert result.handoff_bundle is None
    assert result.source_collection_records == []


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────


def _freeze_fixture(pipeline: SourcePipeline, fixture_path: str) -> FrozenSource:
    """Upload + freeze a fixture, returning the FrozenSource."""
    receipt = pipeline.upload_receipt(FIXTURES_ROOT / fixture_path)
    return pipeline.freeze_and_manifest(receipt.submission_id)


def _persist_deliberation(pipeline: SourcePipeline, delib: MetadataDeliberationResult) -> None:
    """Persist step-50 artifacts so step 60 validation passes."""
    pipeline.store.save_case_complexity_record(delib.case_complexity_record)
    for fb in delib.monitor_feedback:
        pipeline.store.save_monitor_feedback(fb)
