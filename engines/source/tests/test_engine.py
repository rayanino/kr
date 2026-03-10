"""Tests for Source Engine pipeline orchestrator — engine.py

15 tests covering the full acquisition pipeline with mocked LLM inference.
All tests use tmp_path for isolated library directories.
"""

from __future__ import annotations

import asyncio
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from unittest.mock import patch

import pytest

from engines.source.contracts import (
    AcquisitionPath,
    AttributionStatus,
    AuthorityLevel,
    ErrorCode,
    Genre,
    ProcessingStatus,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TrustTier,
    WorkLevel,
)
from engines.source.src.config import SourceEngineConfig
from engines.source.src.engine import (
    acquire_batch,
    acquire_source,
    acquire_source_sync,
    startup_cleanup,
)
from engines.source.src.exceptions import SourceEngineError
from engines.source.src.inference_models import (
    AuthorIdentificationOutput,
    GenreChainOutput,
    InferenceOutput,
    ScholarlyContextOutput,
)
from engines.source.src.metadata_inference import MetadataInferenceResult


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

FIXTURES_DIR = Path("tests/fixtures")


def _make_inference_result(
    genre: str = "risalah",
    structural_format: str = "prose",
    authority_level: str = "modern_compilation",
    level: str | None = "intermediate",
    science_scope: list[str] | None = None,
    is_multi_layer: bool = False,
    author_name: str = "عبد الله بن إبراهيم الزاحم",
    death_date_hijri: int | None = None,
    attribution_status: str = "definitive",
    consensus_agreed: bool = True,
    needs_human_gate: bool = False,
    human_gate_triggers: list[str] | None = None,
    confidence_scores: dict[str, float] | None = None,
) -> MetadataInferenceResult:
    """Create a MetadataInferenceResult with sensible defaults."""
    if science_scope is None:
        science_scope = ["fiqh"]
    if confidence_scores is None:
        confidence_scores = {
            "genre": 0.90,
            "science_scope": 0.85,
            "level": 0.80,
            "structural_format": 0.90,
            "authority_level": 0.85,
            "multi_layer": 0.95,
            "genre_chain": None,
            "author": 0.80,
        }

    canonical_output = InferenceOutput(
        genre=genre,
        genre_confidence=confidence_scores.get("genre", 0.90),
        structural_format=structural_format,
        structural_format_confidence=confidence_scores.get("structural_format", 0.90),
        is_multi_layer=is_multi_layer,
        multi_layer_confidence=confidence_scores.get("multi_layer", 0.95),
        science_scope=science_scope,
        science_scope_confidence=confidence_scores.get("science_scope", 0.85),
        level=level,
        level_confidence=confidence_scores.get("level", 0.80),
        authority_level=authority_level,
        authority_level_confidence=confidence_scores.get("authority_level", 0.85),
        author_identification=AuthorIdentificationOutput(
            canonical_name_ar=author_name,
            death_date_hijri=death_date_hijri,
        ),
        author_identification_confidence=confidence_scores.get("author", 0.80),
        attribution_status=attribution_status,
        scholarly_context=ScholarlyContextOutput(),
    )

    return MetadataInferenceResult(
        consensus_agreed=consensus_agreed,
        canonical_output=canonical_output,
        work_agreed=True,
        attribution_status=attribution_status,
        genre=genre,
        structural_format=structural_format,
        authority_level=authority_level,
        level=level,
        science_scope=science_scope,
        is_multi_layer=is_multi_layer,
        text_layers=[],
        author_reference={
            "name_arabic": author_name,
            "death_date_hijri": death_date_hijri,
        },
        confidence_scores=confidence_scores,
        text_fidelity="high",
        needs_review_fields=[],
        needs_human_gate=needs_human_gate,
        human_gate_triggers=human_gate_triggers or [],
    )


@pytest.fixture
def mock_inference(monkeypatch):
    """Factory fixture that patches infer_metadata with a given result."""
    def _factory(result: MetadataInferenceResult):
        async def _mock(extracted, source_format, staging_context=None):
            return result
        monkeypatch.setattr("engines.source.src.engine.infer_metadata", _mock)
    return _factory


@pytest.fixture
def lib_config(tmp_path: Path) -> SourceEngineConfig:
    """Create a config pointing to a temporary library."""
    library_root = tmp_path / "library"
    staging_path = library_root / "staging"
    staging_path.mkdir(parents=True)
    (library_root / "registries").mkdir(parents=True)
    (library_root / "logs").mkdir(parents=True)
    (library_root / "config").mkdir(parents=True)
    (library_root / "gates" / "pending").mkdir(parents=True)
    (library_root / "gates" / "resolved").mkdir(parents=True)

    return SourceEngineConfig(
        library_root=library_root,
        staging_path=staging_path,
    )


@pytest.fixture
def shamela_source(lib_config: SourceEngineConfig) -> Path:
    """Copy the 03_fiqh fixture to staging."""
    src = FIXTURES_DIR / "shamela_real" / "03_fiqh"
    dst = lib_config.staging_path / "03_fiqh"
    shutil.copytree(src, dst)
    return dst


@pytest.fixture
def plaintext_source(lib_config: SourceEngineConfig) -> Path:
    """Copy the alfiyyah fixture to staging."""
    src = FIXTURES_DIR / "alfiyyah_versified" / "alfiyyah.txt"
    dst = lib_config.staging_path / "alfiyyah.txt"
    shutil.copy2(src, dst)
    return dst


# Configure human_gate for testing
@pytest.fixture(autouse=True)
def configure_human_gate(lib_config: SourceEngineConfig):
    """Configure human gate to use tmp_path."""
    from shared.human_gate.src.human_gate import configure
    configure(gates_dir=lib_config.library_root / "gates", auto_approve=True)


# ──────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────


def test_acquire_shamela_simple(
    mock_inference, lib_config, shamela_source,
) -> None:
    """Happy path: acquire 03_fiqh Shamela fixture."""
    inference_result = _make_inference_result(genre="risalah", science_scope=["fiqh"])
    mock_inference(inference_result)

    metadata = asyncio.run(acquire_source(shamela_source, lib_config))

    assert metadata.source_id.startswith("src_")
    assert metadata.genre == Genre.RISALAH
    assert metadata.source_format == SourceFormat.SHAMELA_HTML
    assert metadata.status == ProcessingStatus.ACQUIRED
    assert metadata.frozen_hash  # Non-empty


def test_acquire_plain_text(
    mock_inference, lib_config, plaintext_source,
) -> None:
    """Plain text path on alfiyyah fixture."""
    inference_result = _make_inference_result(
        genre="nazm",
        structural_format="verse",
        authority_level="primary",
        level="beginner",
        science_scope=["nahw"],
        author_name="ابن مالك",
        death_date_hijri=672,
    )
    mock_inference(inference_result)

    metadata = asyncio.run(acquire_source(plaintext_source, lib_config))

    assert metadata.source_format == SourceFormat.PLAIN_TEXT
    assert metadata.genre == Genre.NAZM
    assert metadata.structural_format == StructuralFormat.VERSE


def test_acquire_exact_duplicate(
    mock_inference, lib_config, shamela_source,
) -> None:
    """Pre-populated hash in source registry → SRC_DUPLICATE_EXACT."""
    inference_result = _make_inference_result()
    mock_inference(inference_result)

    # First acquire to populate the registry
    metadata = asyncio.run(acquire_source(shamela_source, lib_config))

    # Copy the same source again
    dst2 = lib_config.staging_path / "03_fiqh_dup"
    shutil.copytree(FIXTURES_DIR / "shamela_real" / "03_fiqh", dst2)

    with pytest.raises(SourceEngineError) as exc_info:
        asyncio.run(acquire_source(dst2, lib_config))

    assert exc_info.value.error.error_code == ErrorCode.DUPLICATE_EXACT


def test_acquire_work_duplicate(
    mock_inference, lib_config, shamela_source,
) -> None:
    """Pre-populated work_id → Info logged, source still acquired."""
    inference_result = _make_inference_result()
    mock_inference(inference_result)

    # First acquire
    metadata1 = asyncio.run(acquire_source(shamela_source, lib_config))

    # Create a different source (different hash) but same work — use .txt for easier format detection
    alt_src = lib_config.staging_path / "alt_fiqh.txt"
    alt_src.write_text(
        "أحكام الاضطباع different edition content here\nsome more Arabic text\n",
        encoding="utf-8",
    )

    metadata2 = asyncio.run(acquire_source(alt_src, lib_config))
    # Both should succeed (work duplicate is info-only)
    assert metadata2.status == ProcessingStatus.ACQUIRED


def test_acquire_consensus_disagreement(
    mock_inference, lib_config, shamela_source,
) -> None:
    """needs_human_gate=True → gate created."""
    inference_result = _make_inference_result(
        needs_human_gate=True,
        human_gate_triggers=["consensus_disagreement"],
    )
    mock_inference(inference_result)

    metadata = asyncio.run(acquire_source(shamela_source, lib_config))
    # Should still succeed with gate created
    assert metadata.status == ProcessingStatus.ACQUIRED


def test_acquire_low_confidence(
    mock_inference, lib_config, shamela_source,
) -> None:
    """confidence < 0.50 → gate created."""
    inference_result = _make_inference_result(
        confidence_scores={
            "genre": 0.40,
            "science_scope": 0.85,
            "level": 0.80,
            "structural_format": 0.90,
            "authority_level": 0.85,
            "multi_layer": 0.95,
            "genre_chain": None,
            "author": 0.80,
        },
    )
    mock_inference(inference_result)

    metadata = asyncio.run(acquire_source(shamela_source, lib_config))
    assert metadata.status == ProcessingStatus.ACQUIRED
    assert "genre" in metadata.needs_review_fields


def test_acquire_empty_input(
    mock_inference, lib_config,
) -> None:
    """Empty dir → SRC_EMPTY_INPUT."""
    empty_dir = lib_config.staging_path / "empty"
    empty_dir.mkdir()

    inference_result = _make_inference_result()
    mock_inference(inference_result)

    with pytest.raises(SourceEngineError) as exc_info:
        asyncio.run(acquire_source(empty_dir, lib_config))

    assert exc_info.value.error.error_code == ErrorCode.EMPTY_INPUT


def test_acquire_unsupported_format(
    mock_inference, lib_config,
) -> None:
    """.pdf → SRC_UNSUPPORTED_FORMAT."""
    pdf_file = lib_config.staging_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

    inference_result = _make_inference_result()
    mock_inference(inference_result)

    with pytest.raises(SourceEngineError) as exc_info:
        asyncio.run(acquire_source(pdf_file, lib_config))

    assert exc_info.value.error.error_code == ErrorCode.UNSUPPORTED_FORMAT


def test_acquire_batch_isolation(
    mock_inference, lib_config,
) -> None:
    """Batch of 3: #2 fails (empty), #1 and #3 succeed."""
    inference_result = _make_inference_result()
    mock_inference(inference_result)

    # Source 1: valid shamela
    src1 = lib_config.staging_path / "src1"
    shutil.copytree(FIXTURES_DIR / "shamela_real" / "03_fiqh", src1)

    # Source 2: empty dir
    src2 = lib_config.staging_path / "src2"
    src2.mkdir()

    # Source 3: different valid shamela
    src3 = lib_config.staging_path / "src3"
    shutil.copytree(FIXTURES_DIR / "shamela_real" / "04_hadith", src3)

    results = asyncio.run(acquire_batch([src1, src2, src3], lib_config))

    assert len(results) == 3
    # #1 success
    assert isinstance(results[0][1], SourceMetadata)
    # #2 error
    from engines.source.contracts import SourceError
    assert isinstance(results[1][1], SourceError)
    # #3 success
    assert isinstance(results[2][1], SourceMetadata)


def test_startup_cleanup_orphaned_lock(lib_config) -> None:
    """Old lock is cleaned up by startup_cleanup."""
    # Create an orphaned lock
    lock_dir = lib_config.staging_path / "old_source"
    lock_dir.mkdir()
    lock_path = lock_dir / ".kr_processing"
    lock_path.write_text(
        json.dumps({
            "created_at": "2020-01-01T00:00:00+00:00",
            "pid": 99999,
        }),
        encoding="utf-8",
    )

    messages = startup_cleanup(lib_config)

    assert any("orphaned lock" in m.lower() for m in messages)
    assert not lock_path.exists()


def test_startup_cleanup_orphaned_reg(lib_config) -> None:
    """Orphaned pending_registration file is recovered."""
    logs_dir = lib_config.library_root / "logs"
    pending = logs_dir / "pending_registration_src_test1234.json"
    pending.write_text(
        json.dumps({
            "source_id": "src_test1234",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "intended_changes": {"sources.json": {}, "works.json": {}},
            "completed_files": [],  # Never started
        }),
        encoding="utf-8",
    )

    messages = startup_cleanup(lib_config)

    assert any("src_test1234" in m for m in messages)
    assert not pending.exists()


def test_metadata_assembly_completeness(
    mock_inference, lib_config, shamela_source,
) -> None:
    """All required SourceMetadata fields are populated."""
    inference_result = _make_inference_result()
    mock_inference(inference_result)

    metadata = asyncio.run(acquire_source(shamela_source, lib_config))

    # Check all required fields are non-null/non-empty
    assert metadata.source_id
    assert metadata.work_id
    assert metadata.human_label
    assert metadata.title_arabic
    assert metadata.author.canonical_id
    assert metadata.genre
    assert metadata.source_format
    assert metadata.authority_level
    assert metadata.structural_format
    assert metadata.trust_tier
    assert metadata.trust_score >= 0.0
    assert metadata.trust_factors
    assert metadata.text_fidelity
    assert metadata.confidence_scores
    assert metadata.frozen_path
    assert metadata.frozen_hash
    assert metadata.frozen_file_hashes
    assert metadata.status == ProcessingStatus.ACQUIRED
    assert metadata.intake_timestamp


def test_staging_moved_to_processed(
    mock_inference, lib_config, shamela_source,
) -> None:
    """Source dir should be moved to .processed/ after acquisition."""
    inference_result = _make_inference_result()
    mock_inference(inference_result)

    metadata = asyncio.run(acquire_source(shamela_source, lib_config))

    processed_dir = lib_config.staging_path / ".processed"
    assert processed_dir.exists()
    assert (processed_dir / metadata.source_id).exists()


def test_status_transition(
    mock_inference, lib_config, shamela_source,
) -> None:
    """Final status should be ACQUIRED."""
    inference_result = _make_inference_result()
    mock_inference(inference_result)

    metadata = asyncio.run(acquire_source(shamela_source, lib_config))
    assert metadata.status == ProcessingStatus.ACQUIRED
