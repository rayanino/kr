from __future__ import annotations

import logging
from pathlib import Path

import pytest

from engines.source.contracts import ErrorCode, RawUploadStatus
from engines.source.src.errors import SourceEngineError
from engines.source.src.pipeline import SourcePipeline
from engines.source.tests.conftest import FIXTURES_ROOT

logger = logging.getLogger(__name__)


@pytest.mark.spec("REQ-SRC-0001", "AC-1")
def test_upload_receipt_registers_file_submission(source_pipeline: SourcePipeline) -> None:
    path = FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"

    record = source_pipeline.upload_receipt(path)

    assert record.submission_id
    assert record.submitted_path_kind == "file"
    assert record.status == RawUploadStatus.RECEIVED
    assert not hasattr(record, "source_id")


@pytest.mark.spec("REQ-SRC-0001", "AC-2")
def test_upload_receipt_registers_directory_submission(source_pipeline: SourcePipeline) -> None:
    path = FIXTURES_ROOT / "shamela_real" / "11_multi_small"

    record = source_pipeline.upload_receipt(path)

    assert record.submitted_path_kind == "directory"
    assert record.status == RawUploadStatus.RECEIVED


@pytest.mark.spec("REQ-SRC-0001", "AC-3")
def test_upload_receipt_aborts_for_missing_path(source_pipeline: SourcePipeline) -> None:
    path = FIXTURES_ROOT / "shamela_real" / "does_not_exist" / "book.htm"

    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.upload_receipt(path)

    assert exc.value.error_code == ErrorCode.PATH_NOT_FOUND


@pytest.mark.spec("REQ-SRC-0001", "AC-4")
def test_upload_receipt_aborts_for_zero_byte_file(
    source_pipeline: SourcePipeline,
    tmp_path: Path,
) -> None:
    path = tmp_path / "empty.htm"
    path.write_bytes(b"")

    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.upload_receipt(path)

    assert exc.value.error_code == ErrorCode.EMPTY_FILE


@pytest.mark.spec("REQ-SRC-0018", "AC-1")
def test_freeze_and_manifest_writes_single_file_record(source_pipeline: SourcePipeline) -> None:
    path = FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    record = source_pipeline.upload_receipt(path)

    frozen = source_pipeline.freeze_and_manifest(record.submission_id)
    stored_record = source_pipeline.store.get_raw_upload(record.submission_id)

    assert frozen.source_id
    assert len(frozen.source_sha256) == 64
    assert frozen.freeze_verification_status == "verified"
    assert len(frozen.frozen_member_manifest) == 1
    assert stored_record.status == RawUploadStatus.FROZEN


@pytest.mark.spec("REQ-SRC-0018", "AC-2")
def test_freeze_and_manifest_writes_directory_manifest(source_pipeline: SourcePipeline) -> None:
    path = FIXTURES_ROOT / "shamela_real" / "11_multi_small"
    record = source_pipeline.upload_receipt(path)

    frozen = source_pipeline.freeze_and_manifest(record.submission_id)

    assert frozen.freeze_verification_status == "verified"
    assert len(frozen.frozen_member_manifest) == 3


@pytest.mark.spec("REQ-SRC-0018", "AC-3")
def test_freeze_and_manifest_aborts_for_duplicate_ingest(source_pipeline: SourcePipeline) -> None:
    path = FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    first = source_pipeline.upload_receipt(path)
    source_pipeline.freeze_and_manifest(first.submission_id)
    second = source_pipeline.upload_receipt(path)

    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.freeze_and_manifest(second.submission_id)

    assert exc.value.error_code == ErrorCode.DUPLICATE_INGEST


def test_freeze_and_manifest_rejects_corrupted_frozen_copy(
    source_pipeline: SourcePipeline,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
    record = source_pipeline.upload_receipt(path)
    original_freeze = source_pipeline._freeze_source

    def corrupting_freeze(source_path: Path, source_id: str) -> Path:
        frozen_root = original_freeze(source_path, source_id)
        frozen_file = frozen_root / source_path.name
        frozen_file.write_text("corrupted", encoding="utf-8")
        return frozen_root

    monkeypatch.setattr(source_pipeline, "_freeze_source", corrupting_freeze)

    with pytest.raises(SourceEngineError):
        source_pipeline.freeze_and_manifest(record.submission_id)
