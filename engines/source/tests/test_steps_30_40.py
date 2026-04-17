from __future__ import annotations

import logging
from pathlib import Path

import fitz
import pytest

from engines.source.contracts import ErrorCode
from engines.source.src.errors import SourceEngineError
from engines.source.src.pipeline import SourcePipeline
from engines.source.tests.conftest import FIXTURES_ROOT


logger = logging.getLogger(__name__)


def _freeze_fixture(source_pipeline: SourcePipeline, path: Path) -> str:
    record = source_pipeline.upload_receipt(path)
    frozen = source_pipeline.freeze_and_manifest(record.submission_id)
    return frozen.source_id


def _write_pdf(path: Path, text: str | None = None) -> None:
    """Write a PDF with optional Arabic text via PyMuPDF insert_text + Arial.

    Arabic extracts as visual-order presentation forms (U+FE70-FEFF) due to
    Arial's ToUnicode CMap, not byte-identical logical order. Tests tolerate
    this via `pdf_text_layer_status in {"clean", "presentation_forms"}`.
    arabic_reshaper + python-bidi produce the same extraction class; see
    Phase 5a Track B investigation (2026-04-17).
    """
    doc = fitz.open()
    page = doc.new_page()
    if text is not None:
        font_path = Path(r"C:\Windows\Fonts\arial.ttf")
        page.insert_font(fontname="arial-custom", fontfile=str(font_path))
        page.insert_text((72, 72), text, fontname="arial-custom", fontsize=14)
    doc.save(path)
    doc.close()


@pytest.mark.spec("REQ-SRC-0017", "AC-1")
def test_container_classification_detects_shamela_multi_volume(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "shamela_real" / "11_multi_small")

    classification = source_pipeline.classify_container(source_id)

    assert classification.container_type == "shamela_multi_volume_html"
    assert len(classification.volume_manifest) == 3
    assert classification.normalization_route == "html_parse_primary"


@pytest.mark.spec("REQ-SRC-0017", "AC-2")
def test_container_classification_rejects_html_directory_without_numbered_volumes(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    root = tmp_path / "supplementary_only"
    root.mkdir()
    (root / "appendix.htm").write_text("<html></html>", encoding="utf-8")
    (root / "introduction.htm").write_text("<html></html>", encoding="utf-8")
    source_id = _freeze_fixture(source_pipeline, root)

    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.classify_container(source_id)

    assert exc.value.error_code == ErrorCode.EMPTY_DIRECTORY


@pytest.mark.spec("REQ-SRC-0017", "AC-3")
def test_container_classification_splits_supplementary_html_members(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    root = tmp_path / "multipart_html"
    root.mkdir()
    (root / "001.htm").write_text("<html></html>", encoding="utf-8")
    (root / "المقدمة.htm").write_text("<html></html>", encoding="utf-8")
    source_id = _freeze_fixture(source_pipeline, root)

    classification = source_pipeline.classify_container(source_id)

    assert classification.container_type == "multipart_with_supplementary"
    assert classification.volume_manifest[0].member_name == "001.htm"
    assert classification.supplementary_members[0].member_name == "المقدمة.htm"


@pytest.mark.spec("REQ-SRC-0020", "AC-1")
def test_container_classification_detects_plain_text(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "alfiyyah_versified" / "alfiyyah.txt")

    classification = source_pipeline.classify_container(source_id)

    assert classification.container_type == "plain_text"
    assert classification.normalization_route == "plain_text_parse"
    assert classification.text_encoding == "utf-8"


@pytest.mark.spec("REQ-SRC-0041", "AC-1")
def test_container_classification_detects_pdf_multi_volume(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    root = tmp_path / "pdf_set"
    root.mkdir()
    _write_pdf(root / "vol1.pdf")
    _write_pdf(root / "vol2.pdf")
    _write_pdf(root / "vol3.pdf")
    source_id = _freeze_fixture(source_pipeline, root)

    classification = source_pipeline.classify_container(source_id)

    assert classification.container_type == "pdf_multi_volume"
    assert [item.member_name for item in classification.volume_manifest] == [
        "vol1.pdf",
        "vol2.pdf",
        "vol3.pdf",
    ]


@pytest.mark.spec("REQ-SRC-0041", "AC-2")
def test_container_classification_detects_plain_text_multi_volume(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    root = tmp_path / "txt_set"
    root.mkdir()
    (root / "001.txt").write_text("الأول", encoding="utf-8")
    (root / "002.txt").write_text("الثاني", encoding="utf-8")
    source_id = _freeze_fixture(source_pipeline, root)

    classification = source_pipeline.classify_container(source_id)

    assert classification.container_type == "plain_text_multi_volume"
    assert classification.normalization_route == "plain_text_parse"


@pytest.mark.spec("REQ-SRC-0041", "AC-3")
def test_container_classification_keeps_single_pdf_single_volume(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    pdf_path = tmp_path / "single.pdf"
    _write_pdf(pdf_path)
    source_id = _freeze_fixture(source_pipeline, pdf_path)

    classification = source_pipeline.classify_container(source_id)

    assert classification.container_type == "pdf"


def test_intake_analysis_flags_mixed_format_directory_as_suspicious(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    root = tmp_path / "mixed"
    root.mkdir()
    _write_pdf(root / "a.pdf")
    (root / "b.txt").write_text("نص", encoding="utf-8")
    source_id = _freeze_fixture(source_pipeline, root)
    classification = source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert classification.container_type == "mixed_format_directory"
    assert dossier.integrity_status == "suspicious"
    assert "mixed_format_directory" in dossier.study_quality_risk_flags


@pytest.mark.spec("REQ-SRC-0019", "AC-1")
def test_intake_analysis_builds_identity_dossier_for_single_html(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.dossier_id
    assert len(dossier.title_evidence) >= 1
    assert len(dossier.work_identity_proposal.candidates) >= 1


@pytest.mark.spec("REQ-SRC-0019", "AC-2")
def test_intake_analysis_builds_identity_dossier_for_multi_volume_html(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "shamela_real" / "11_multi_small")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert len(dossier.work_identity_proposal.candidates) >= 1
    assert dossier.collection_match_candidates is not None


@pytest.mark.spec("REQ-SRC-0021", "AC-1")
def test_intake_analysis_classifies_absent_pdf_text_layer(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "ibn_aqil_alfiyyah" / "vol6.pdf")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.source_format == "pdf"
    assert dossier.pdf_text_layer_status == "absent"
    assert dossier.normalization_route == "pdf_ocr_primary"
    assert dossier.declared_vs_observed_counts.physical_page_count == 398


@pytest.mark.spec("REQ-SRC-0021", "AC-2")
def test_intake_analysis_classifies_corrupt_pdf_text_layer(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "waraqat_usul" / "waraqat.pdf")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.source_format == "pdf"
    assert dossier.pdf_text_layer_status == "corrupt"
    assert dossier.normalization_route == "pdf_ocr_primary"
    assert dossier.declared_vs_observed_counts.physical_page_count == 13


@pytest.mark.spec("REQ-SRC-0021", "AC-3")
def test_intake_analysis_classifies_clean_pdf_text_layer(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    pdf_path = tmp_path / "clean.pdf"
    _write_pdf(pdf_path, "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
    source_id = _freeze_fixture(source_pipeline, pdf_path)
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.source_format == "pdf"
    assert dossier.pdf_text_layer_status in {"clean", "presentation_forms"}
    assert dossier.normalization_route == "pdf_text_primary"
    assert dossier.declared_vs_observed_counts.physical_page_count == 1


@pytest.mark.spec("REQ-SRC-0021", "AC-4")
def test_intake_analysis_rejects_corrupt_pdf(source_pipeline: SourcePipeline, tmp_path: Path) -> None:
    pdf_path = tmp_path / "corrupt.pdf"
    pdf_path.write_bytes(b"not a real pdf")
    source_id = _freeze_fixture(source_pipeline, pdf_path)
    source_pipeline.classify_container(source_id)

    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.intake_analysis(source_id)

    assert exc.value.error_code == ErrorCode.PDF_CORRUPT


@pytest.mark.spec("REQ-SRC-0024", "AC-2")
def test_intake_analysis_records_single_column_layout_for_waraqat(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "waraqat_usul" / "waraqat.pdf")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.page_layout_hint == "single_column"


def test_intake_analysis_aggregates_multi_pdf_page_counts(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    root = tmp_path / "pdfs"
    root.mkdir()
    pdf1 = root / "vol1.pdf"
    pdf2 = root / "vol2.pdf"
    _write_pdf(pdf1)
    _write_pdf(pdf2, "بسم الله الرحمن الرحيم")
    source_id = _freeze_fixture(source_pipeline, root)
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.declared_vs_observed_counts.physical_page_count == 2


@pytest.mark.spec("REQ-SRC-0036", "AC-1")
def test_intake_analysis_records_observed_volume_count_for_multi_volume_html(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "shamela_real" / "11_multi_small")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.declared_vs_observed_counts.observed_volume_count == 3
    assert dossier.completeness_status in {"complete", "indeterminate"}


@pytest.mark.spec("REQ-SRC-0036", "AC-3")
def test_intake_analysis_marks_single_html_complete_and_self_contained(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.completeness_status == "complete"
    assert dossier.self_containment_assessment == "self_contained"
    assert dossier.cross_volume_dependency_assessment == "non_material"


@pytest.mark.spec("REQ-SRC-0037", "AC-1")
def test_intake_analysis_marks_well_formed_html_sound(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.integrity_status == "sound"
    assert dossier.study_quality_risk_flags == []


@pytest.mark.spec("REQ-SRC-0037", "AC-3")
def test_intake_analysis_detects_isnad_chains(source_pipeline: SourcePipeline) -> None:
    source_id = _freeze_fixture(source_pipeline, FIXTURES_ROOT / "shamela_real" / "04_hadith" / "book.htm")
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.contains_isnad_chains is True


def test_intake_analysis_does_not_false_positive_on_non_isnad_word(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    path = tmp_path / "non_isnad.txt"
    path.write_text("استحدثنا هذا الباب للتجربة", encoding="utf-8")
    source_id = _freeze_fixture(source_pipeline, path)
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.contains_isnad_chains is False


def test_intake_analysis_detects_additional_transmission_formula(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    path = tmp_path / "isnad.txt"
    path.write_text("أجاز لي الشيخ هذا الكتاب", encoding="utf-8")
    source_id = _freeze_fixture(source_pipeline, path)
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.contains_isnad_chains is True


@pytest.mark.spec("REQ-SRC-0038", "AC-1")
def test_intake_analysis_detects_majmu_from_title_and_multiple_volumes(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    root = tmp_path / "majmu"
    root.mkdir()
    html_template = (
        "<html><head><title>مجموع فتاوى ابن تيمية - جـ {vol}</title></head>"
        "<body><span class='title'>رسالة في الطهارة</span>"
        "<span class='title'>رسالة في الصلاة</span></body></html>"
    )
    (root / "001.htm").write_text(html_template.format(vol="١"), encoding="utf-8")
    (root / "002.htm").write_text(html_template.format(vol="٢"), encoding="utf-8")
    source_id = _freeze_fixture(source_pipeline, root)
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.composite_work_type == "majmu"
    assert dossier.sub_work_inventory


@pytest.mark.spec("REQ-SRC-0038", "AC-4")
def test_intake_analysis_marks_ambiguous_single_volume_rasail_as_possible(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    path = tmp_path / "rasail.htm"
    path.write_text(
        "<html><head><title>رسائل</title></head><body>نص متصل بلا حدود داخلية واضحة</body></html>",
        encoding="utf-8",
    )
    source_id = _freeze_fixture(source_pipeline, path)
    source_pipeline.classify_container(source_id)

    dossier = source_pipeline.intake_analysis(source_id)

    assert dossier.composite_work_type == "possible"
    assert "ambiguous_composite_detection" in dossier.study_quality_risk_flags
