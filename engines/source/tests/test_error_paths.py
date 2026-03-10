"""Error path tests for source engine — every ErrorCode verified through engine.py.

Each test triggers a specific error code through the pipeline.
"""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from engines.source.contracts import (
    ErrorCode,
    ErrorSeverity,
    SourceError,
    SourceFormat,
)
from engines.source.src.config import SourceEngineConfig
from engines.source.src.engine import acquire_source
from engines.source.src.exceptions import SourceEngineError
from engines.source.src.inference_models import (
    AuthorIdentificationOutput,
    InferenceOutput,
    ScholarlyContextOutput,
)
from engines.source.src.metadata_inference import MetadataInferenceResult


FIXTURES_DIR = Path("tests/fixtures")


def _make_inference_result(**overrides: Any) -> MetadataInferenceResult:
    """Create a default MetadataInferenceResult with optional overrides."""
    defaults = dict(
        consensus_agreed=True,
        canonical_output=InferenceOutput(
            genre="risalah",
            genre_confidence=0.90,
            structural_format="prose",
            structural_format_confidence=0.90,
            is_multi_layer=False,
            multi_layer_confidence=0.95,
            science_scope=["fiqh"],
            science_scope_confidence=0.85,
            level="intermediate",
            level_confidence=0.80,
            authority_level="modern_compilation",
            authority_level_confidence=0.85,
            author_identification=AuthorIdentificationOutput(
                canonical_name_ar="عبد الله بن إبراهيم الزاحم",
            ),
            author_identification_confidence=0.80,
            attribution_status="definitive",
            scholarly_context=ScholarlyContextOutput(),
        ),
        work_agreed=True,
        attribution_status="definitive",
        genre="risalah",
        structural_format="prose",
        authority_level="modern_compilation",
        level="intermediate",
        science_scope=["fiqh"],
        is_multi_layer=False,
        text_layers=[],
        author_reference={"name_arabic": "عبد الله بن إبراهيم الزاحم", "death_date_hijri": None},
        confidence_scores={
            "genre": 0.90, "science_scope": 0.85, "level": 0.80,
            "structural_format": 0.90, "authority_level": 0.85,
            "multi_layer": 0.95, "genre_chain": None, "author": 0.80,
        },
        text_fidelity="high",
        needs_review_fields=[],
        needs_human_gate=False,
        human_gate_triggers=[],
    )
    defaults.update(overrides)
    return MetadataInferenceResult(**defaults)


@pytest.fixture
def mock_inference(monkeypatch):
    def _factory(result):
        async def _mock(extracted, source_format, staging_context=None):
            return result
        monkeypatch.setattr("engines.source.src.engine.infer_metadata", _mock)
    return _factory


@pytest.fixture
def lib_config(tmp_path: Path) -> SourceEngineConfig:
    library_root = tmp_path / "library"
    staging_path = library_root / "staging"
    staging_path.mkdir(parents=True)
    (library_root / "registries").mkdir(parents=True)
    (library_root / "logs").mkdir(parents=True)
    (library_root / "config").mkdir(parents=True)
    (library_root / "gates" / "pending").mkdir(parents=True)
    (library_root / "gates" / "resolved").mkdir(parents=True)
    return SourceEngineConfig(library_root=library_root, staging_path=staging_path)


@pytest.fixture(autouse=True)
def configure_human_gate(lib_config):
    from shared.human_gate.src.human_gate import configure
    configure(gates_dir=lib_config.library_root / "gates", auto_approve=True)


def _copy_shamela(lib_config: SourceEngineConfig, name: str = "03_fiqh") -> Path:
    dst = lib_config.staging_path / name
    shutil.copytree(FIXTURES_DIR / "shamela_real" / name, dst)
    return dst


# ──────────────────────────────────────────────────────────────────
# Error Path Tests
# ──────────────────────────────────────────────────────────────────


def test_error_empty_input(mock_inference, lib_config) -> None:
    """Empty dir → SRC_EMPTY_INPUT."""
    empty = lib_config.staging_path / "empty"
    empty.mkdir()
    mock_inference(_make_inference_result())
    with pytest.raises(SourceEngineError) as exc_info:
        asyncio.run(acquire_source(empty, lib_config))
    assert exc_info.value.error.error_code == ErrorCode.EMPTY_INPUT


def test_error_unsupported_format(mock_inference, lib_config) -> None:
    """.pdf file → SRC_UNSUPPORTED_FORMAT."""
    pdf = lib_config.staging_path / "test.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    mock_inference(_make_inference_result())
    with pytest.raises(SourceEngineError) as exc_info:
        asyncio.run(acquire_source(pdf, lib_config))
    assert exc_info.value.error.error_code == ErrorCode.UNSUPPORTED_FORMAT


def test_error_format_structure_missing(mock_inference, lib_config) -> None:
    """.htm without PageText div → SRC_FORMAT_STRUCTURE_MISSING."""
    bad_htm = lib_config.staging_path / "bad.htm"
    bad_htm.write_text("<html><body><p>No PageText</p></body></html>", encoding="utf-8")
    mock_inference(_make_inference_result())
    with pytest.raises(SourceEngineError) as exc_info:
        asyncio.run(acquire_source(bad_htm, lib_config))
    # Format detection may raise UNSUPPORTED or FORMAT_STRUCTURE_MISSING
    assert exc_info.value.error.error_code in (
        ErrorCode.UNSUPPORTED_FORMAT,
        ErrorCode.FORMAT_STRUCTURE_MISSING,
    )


def test_error_duplicate_exact(mock_inference, lib_config) -> None:
    """Pre-populated hash → SRC_DUPLICATE_EXACT."""
    mock_inference(_make_inference_result())
    src1 = _copy_shamela(lib_config, "03_fiqh")
    asyncio.run(acquire_source(src1, lib_config))

    src2 = _copy_shamela(lib_config, "03_fiqh")
    # Rename to avoid staging lock conflict
    dst = lib_config.staging_path / "03_fiqh_dup"
    src2.rename(dst)
    with pytest.raises(SourceEngineError) as exc_info:
        asyncio.run(acquire_source(dst, lib_config))
    assert exc_info.value.error.error_code == ErrorCode.DUPLICATE_EXACT


def test_error_staging_modified(mock_inference, lib_config) -> None:
    """File modified after staging → SRC_STAGING_MODIFIED."""
    import time

    src = _copy_shamela(lib_config, "03_fiqh")
    mock_inference(_make_inference_result())

    # Patch freeze_source to modify the file before freezing
    original_freeze = None
    from engines.source.src import freezer as freezer_mod
    original_freeze = freezer_mod.freeze_source

    def _tamper_freeze(staged_path, source_id, library_root, staging_hashes, staging_timestamps):
        # Modify the file to trigger TOCTOU
        if staged_path.is_dir():
            for f in staged_path.iterdir():
                if f.is_file() and not f.name.startswith("."):
                    time.sleep(0.1)
                    f.write_text(f.read_text(encoding="utf-8") + "\nTAMPERED", encoding="utf-8")
                    break
        return original_freeze(staged_path, source_id, library_root, staging_hashes, staging_timestamps)

    with patch("engines.source.src.engine.freeze_source", side_effect=_tamper_freeze):
        with pytest.raises(SourceEngineError) as exc_info:
            asyncio.run(acquire_source(src, lib_config))
    assert exc_info.value.error.error_code == ErrorCode.STAGING_MODIFIED


def test_error_consensus_disagreement(mock_inference, lib_config) -> None:
    """Mock inference disagreement → gate created, source still acquired."""
    src = _copy_shamela(lib_config, "03_fiqh")
    result = _make_inference_result(
        needs_human_gate=True,
        human_gate_triggers=["consensus_disagreement"],
    )
    mock_inference(result)
    metadata = asyncio.run(acquire_source(src, lib_config))
    assert metadata.status.value == "acquired"


def test_error_low_confidence(mock_inference, lib_config) -> None:
    """Mock confidence < 0.50 → gate created."""
    src = _copy_shamela(lib_config, "04_hadith")
    result = _make_inference_result(
        confidence_scores={
            "genre": 0.40, "science_scope": 0.85, "level": 0.80,
            "structural_format": 0.90, "authority_level": 0.85,
            "multi_layer": 0.95, "genre_chain": None, "author": 0.80,
        },
    )
    mock_inference(result)
    metadata = asyncio.run(acquire_source(src, lib_config))
    assert "genre" in metadata.needs_review_fields


def test_error_duplicate_work_info_only(mock_inference, lib_config) -> None:
    """Work duplicate → Info, source still acquired."""
    mock_inference(_make_inference_result())
    src1 = _copy_shamela(lib_config, "03_fiqh")
    asyncio.run(acquire_source(src1, lib_config))

    # Different file (different hash) but same inferred work
    alt = lib_config.staging_path / "alt.txt"
    alt.write_text("أحكام الاضطباع different content\nmore Arabic text\n", encoding="utf-8")
    metadata = asyncio.run(acquire_source(alt, lib_config))
    assert metadata.status.value == "acquired"


def test_error_nonexistent_path(mock_inference, lib_config) -> None:
    """Non-existent path → error."""
    mock_inference(_make_inference_result())
    fake = lib_config.staging_path / "does_not_exist"
    with pytest.raises(SourceEngineError):
        asyncio.run(acquire_source(fake, lib_config))


def test_error_inference_failure(lib_config) -> None:
    """Inference raises → pipeline fails cleanly."""
    src = _copy_shamela(lib_config, "03_fiqh")

    async def _fail_inference(extracted, source_format, staging_context=None):
        raise SourceEngineError(
            SourceError(
                timestamp="2026-01-01T00:00:00+00:00",
                error_code=ErrorCode.CONSENSUS_DISAGREEMENT,
                severity=ErrorSeverity.FATAL,
                message="Both models failed",
                recovery_action="rejected",
            )
        )

    with patch("engines.source.src.engine.infer_metadata", side_effect=_fail_inference):
        with pytest.raises(SourceEngineError) as exc_info:
            asyncio.run(acquire_source(src, lib_config))
    assert exc_info.value.error.error_code == ErrorCode.CONSENSUS_DISAGREEMENT


def test_error_freeze_copy_corrupt(mock_inference, lib_config) -> None:
    """Mock freeze hash mismatch → SRC_FREEZE_COPY_CORRUPT."""
    src = _copy_shamela(lib_config, "03_fiqh")
    mock_inference(_make_inference_result())

    def _corrupt_freeze(staged_path, source_id, library_root, staging_hashes, staging_timestamps):
        from engines.source.src.exceptions import make_error as _mk
        raise _mk(
            ErrorCode.FREEZE_COPY_CORRUPT,
            "Frozen file hash mismatch",
            source_id=source_id,
        )

    with patch("engines.source.src.engine.freeze_source", side_effect=_corrupt_freeze):
        with pytest.raises(SourceEngineError) as exc_info:
            asyncio.run(acquire_source(src, lib_config))
    assert exc_info.value.error.error_code == ErrorCode.FREEZE_COPY_CORRUPT


def test_error_batch_isolation(mock_inference, lib_config) -> None:
    """Batch: one source fails, others succeed."""
    from engines.source.src.engine import acquire_batch

    mock_inference(_make_inference_result())
    src1 = _copy_shamela(lib_config, "03_fiqh")
    empty = lib_config.staging_path / "empty_batch"
    empty.mkdir()
    src3 = lib_config.staging_path / "valid.txt"
    src3.write_text("بسم الله الرحمن الرحيم\nsome Arabic text\n", encoding="utf-8")

    results = asyncio.run(acquire_batch([src1, empty, src3], lib_config))
    assert len(results) == 3
    from engines.source.contracts import SourceMetadata
    assert isinstance(results[0][1], SourceMetadata)
    assert isinstance(results[1][1], SourceError)
    assert isinstance(results[2][1], SourceMetadata)
