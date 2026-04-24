"""DEC-SRC-0021 legacy SourceMetadata load-boundary migration tests."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from engines.source.contracts import (
    ErrorCode,
    Genre,
    LevelStatus,
    SourceFormat,
    StructuralFormat,
    TextFidelity,
    TrustTier,
    WorkLevel,
)
from engines.source.src.errors import SourceEngineError
from engines.source.src.store import SourceStore
from shared.human_gate.src.human_gate import configure, get_pending


logger = logging.getLogger(__name__)


REAL_USUL_TITLE = "آداب الفتوى والمفتي والمستفتي"


def _legacy_source_metadata_payload(
    *,
    source_id: str = "src_legacy_dec_0021",
    genre: str = Genre.RISALAH.value,
    level: str | None = None,
    level_status: str | None = None,
    level_provenance: str | None = None,
    composite_work_type: str | None = None,
) -> dict[str, object]:
    """Build persisted legacy JSON with real Arabic fixture metadata."""
    payload: dict[str, object] = {
        "source_id": source_id,
        "title_arabic": REAL_USUL_TITLE,
        "source_format": SourceFormat.SHAMELA_HTML.value,
        "structural_format": StructuralFormat.PROSE.value,
        "intake_timestamp": "2026-04-23T00:00:00Z",
        "acquisition_path": "tests/fixtures/shamela_real/06_usul/book.htm",
        "frozen_path": f"library/sources/{source_id}/frozen",
        "frozen_hash": "a" * 64,
        "frozen_file_hashes": {"book.htm": "a" * 64},
        "status": "accepted",
        "science_scope": ["usul_al_fiqh"],
        "genre": genre,
        "text_fidelity": TextFidelity.HIGH.value,
        "trust_tier": TrustTier.VERIFIED.value,
        "trust_score": 0.0,
        "level": level,
    }
    if level_status is not None:
        payload["level_status"] = level_status
    if level_provenance is not None:
        payload["level_provenance"] = level_provenance
    if composite_work_type is not None:
        payload["composite_work_type"] = composite_work_type
    return payload


def _write_source_collection(
    workspace_root: Path, payload: dict[str, object]
) -> SourceStore:
    workspace_root.mkdir(parents=True, exist_ok=True)
    (workspace_root / "source_collection.json").write_text(
        json.dumps([payload], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return SourceStore(workspace_root)


@pytest.fixture(autouse=True)
def _human_gate_tmp(tmp_path: Path) -> None:
    gates_dir = tmp_path / "gates"
    gates_dir.mkdir()
    (gates_dir / "pending").mkdir()
    (gates_dir / "resolved").mkdir()
    configure(gates_dir=gates_dir, auto_approve=False)


@pytest.mark.spec("DEC-SRC-0021", "OPT-B-i")
def test_dec_src_0021_i_missing_status_defaults_pending_synthesis(
    tmp_path: Path,
) -> None:
    """Missing level_status + null level + leveled genre defaults on read."""
    # Arrange
    payload = _legacy_source_metadata_payload()
    store = _write_source_collection(tmp_path / "workspace", payload)

    # Act
    metadata = store.get_source_collection_record("src_legacy_dec_0021")

    # Assert
    assert metadata.level is None
    assert metadata.level_status is LevelStatus.PENDING_SYNTHESIS
    assert metadata.level_provenance is None
    assert metadata.composite_work_type is None
    assert metadata.legacy_migration_events[0].fields_defaulted == [
        "level_status",
        "level_provenance",
        "composite_work_type",
    ]


@pytest.mark.spec("DEC-SRC-0021", "OPT-B-ii")
@pytest.mark.parametrize(
    ("payload", "source_id"),
    [
        (
            _legacy_source_metadata_payload(
                source_id="src_legacy_hadith",
                genre=Genre.HADITH_COLLECTION.value,
            ),
            "src_legacy_hadith",
        ),
        (
            _legacy_source_metadata_payload(
                source_id="src_legacy_majmu",
                composite_work_type="majmu",
            ),
            "src_legacy_majmu",
        ),
    ],
)
def test_dec_src_0021_ii_missing_status_defaults_non_applicable(
    tmp_path: Path,
    payload: dict[str, object],
    source_id: str,
) -> None:
    """Missing level_status defaults non_applicable when Axis 1 or Axis 2 fires."""
    # Arrange
    store = _write_source_collection(tmp_path / "workspace", payload)

    # Act
    metadata = store.get_source_collection_record(source_id)

    # Assert
    assert metadata.level is None
    assert metadata.level_status is LevelStatus.NON_APPLICABLE_REFERENCE
    assert metadata.level_provenance is None


@pytest.mark.spec("DEC-SRC-0021", "OPT-B-iii")
def test_dec_src_0021_iii_missing_status_with_level_routes_human_gate(
    tmp_path: Path,
) -> None:
    """Missing level_status + non-null level is ambiguous and owner-routed."""
    # Arrange
    payload = _legacy_source_metadata_payload(level=WorkLevel.MUTAWASSIT.value)
    store = _write_source_collection(tmp_path / "workspace", payload)

    # Act / Assert
    with pytest.raises(SourceEngineError) as exc_info:
        store.get_source_collection_record("src_legacy_dec_0021")
    assert exc_info.value.error_code is ErrorCode.LEGACY_RECORD_AMBIGUOUS_STATUS

    pending = get_pending("src_legacy_dec_0021")
    assert len(pending) == 1
    checkpoint = pending[0]
    assert "هل سبق أن حدّدتَ درجةَ هذا الكتاب بنفسك؟" in checkpoint.trigger_detail
    checkpoint_payload = json.dumps(checkpoint.model_dump(mode="json"), ensure_ascii=False)
    assert "owner_override" not in checkpoint_payload
    assert "synthesis_engine" not in checkpoint_payload


@pytest.mark.spec("DEC-SRC-0021", "OPT-B-iv")
def test_dec_src_0021_iv_missing_provenance_with_null_level_defaults_null(
    tmp_path: Path,
) -> None:
    """Missing level_provenance + null level defaults to null on read."""
    # Arrange
    payload = _legacy_source_metadata_payload(
        level_status=LevelStatus.PENDING_SYNTHESIS.value
    )
    store = _write_source_collection(tmp_path / "workspace", payload)

    # Act
    metadata = store.get_source_collection_record("src_legacy_dec_0021")

    # Assert
    assert metadata.level is None
    assert metadata.level_provenance is None
    assert metadata.legacy_migration_events[0].fields_defaulted == [
        "level_provenance",
        "composite_work_type",
    ]


@pytest.mark.spec("DEC-SRC-0021", "OPT-B-v")
def test_dec_src_0021_v_missing_provenance_with_level_routes_human_gate(
    tmp_path: Path,
) -> None:
    """Missing level_provenance + non-null level is ambiguous and owner-routed."""
    # Arrange
    payload = _legacy_source_metadata_payload(
        level=WorkLevel.MUTAWASSIT.value,
        level_status=LevelStatus.ASSIGNED.value,
    )
    store = _write_source_collection(tmp_path / "workspace", payload)

    # Act / Assert
    with pytest.raises(SourceEngineError) as exc_info:
        store.get_source_collection_record("src_legacy_dec_0021")
    assert (
        exc_info.value.error_code
        is ErrorCode.LEGACY_RECORD_AMBIGUOUS_PROVENANCE
    )

    pending = get_pending("src_legacy_dec_0021")
    assert len(pending) == 1
    checkpoint = pending[0]
    assert "مصدر التقييم" in checkpoint.trigger_detail
    checkpoint_payload = json.dumps(checkpoint.model_dump(mode="json"), ensure_ascii=False)
    assert "سند" not in checkpoint_payload
    assert "بينة" not in checkpoint_payload
    assert "شهادة" not in checkpoint_payload
    assert "owner_override" not in checkpoint_payload
    assert "synthesis_engine" not in checkpoint_payload


@pytest.mark.spec("DEC-SRC-0021", "OPT-B-vi")
def test_dec_src_0021_vi_missing_composite_work_type_defaults_none(
    tmp_path: Path,
) -> None:
    """Missing composite_work_type defaults to None and is audited."""
    # Arrange
    payload = _legacy_source_metadata_payload(
        level_status=LevelStatus.PENDING_SYNTHESIS.value,
        level_provenance=None,
    )
    store = _write_source_collection(tmp_path / "workspace", payload)

    # Act
    metadata = store.get_source_collection_record("src_legacy_dec_0021")

    # Assert
    assert metadata.composite_work_type is None
    assert metadata.legacy_migration_events[0].fields_defaulted == [
        "level_provenance",
        "composite_work_type",
    ]
