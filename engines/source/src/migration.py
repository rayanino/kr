from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime, timezone

from pydantic import BaseModel

from engines.source.contracts import (
    ErrorCode,
    HumanGateTrigger,
    LEVELED_HADITH_SUBGENRES,
    LevelStatus,
    MetadataDeliberationResult,
    NON_APPLICABLE_GENRE_VALUES,
    NormalizationHandoffBundle,
    SourceMetadata,
)
from engines.source.src.errors import SourceEngineError
from shared.human_gate.src.human_gate import create_checkpoint


logger = logging.getLogger(__name__)


_SOURCE_METADATA_NESTED_MODEL_TYPES: tuple[type[BaseModel], ...] = (
    MetadataDeliberationResult,
    NormalizationHandoffBundle,
)


def migrate_persisted_source_payload(
    model_type: type[BaseModel],
    payload: object,
) -> object:
    """Apply DEC-SRC-0021 only at persisted JSON load boundaries."""
    if not isinstance(payload, dict):
        return payload
    if model_type is SourceMetadata:
        return migrate_source_metadata_payload(payload)
    if model_type in _SOURCE_METADATA_NESTED_MODEL_TYPES:
        return _migrate_nested_source_metadata(payload)
    return payload


def migrate_source_metadata_payload(payload: Mapping[str, object]) -> dict[str, object]:
    """Default safe legacy SourceMetadata fields without mutating the input."""
    migrated = dict(payload)
    defaulted: list[str] = []

    if "level_status" not in migrated:
        if migrated.get("level") is not None:
            _raise_ambiguous_status(migrated)
        migrated["level_status"] = _default_level_status(migrated).value
        defaulted.append("level_status")

    if "level_provenance" not in migrated:
        if migrated.get("level") is not None:
            _raise_ambiguous_provenance(migrated)
        migrated["level_provenance"] = None
        defaulted.append("level_provenance")

    if "composite_work_type" not in migrated:
        migrated["composite_work_type"] = None
        defaulted.append("composite_work_type")

    if defaulted:
        _append_migration_event(migrated, defaulted)

    return migrated


def _migrate_nested_source_metadata(payload: Mapping[str, object]) -> dict[str, object]:
    migrated = dict(payload)
    source_metadata = migrated.get("source_metadata")
    if isinstance(source_metadata, dict):
        migrated["source_metadata"] = migrate_source_metadata_payload(source_metadata)
    return migrated


def _default_level_status(payload: Mapping[str, object]) -> LevelStatus:
    """Default INV-SRC-0012 status for legacy payloads per DEC-SRC-0021.

    Phase 5b follow-up 34 (2026-04-27) closure: Axis-3 carve-back is now
    consulted before Axis 1 falls back to non_applicable_reference. A
    legacy hadith_collection payload carrying a leveled hadith_subgenre
    (ARBAIN, AHKAM) defaults to pending_synthesis so the synthesis engine
    can run authoritative level determination per DEC-SRC-0003 — the
    pre-closure default of non_applicable_reference would have wrongly
    quarantined Bulūgh al-Marām (Ibn Ḥajar d. 852 AH) and similar
    pedagogical aḥkām anthologies on legacy load.
    """
    genre = payload.get("genre")
    hadith_subgenre = payload.get("hadith_subgenre")
    axis_3_carves_back = (
        genre == "hadith_collection"
        and isinstance(hadith_subgenre, str)
        and hadith_subgenre in LEVELED_HADITH_SUBGENRES
    )
    axis_1_fires = (
        isinstance(genre, str)
        and genre in NON_APPLICABLE_GENRE_VALUES
        and not axis_3_carves_back
    )
    axis_2_fires = payload.get("composite_work_type") == "majmu"
    if axis_1_fires or axis_2_fires:
        return LevelStatus.NON_APPLICABLE_REFERENCE
    return LevelStatus.PENDING_SYNTHESIS


def _append_migration_event(
    payload: dict[str, object],
    fields_defaulted: list[str],
) -> None:
    existing_events = payload.get("legacy_migration_events")
    events = existing_events if isinstance(existing_events, list) else []
    events.append(
        {
            "decision_id": "DEC-SRC-0021",
            "load_boundary": "SourceStore._load_models",
            "fields_defaulted": fields_defaulted,
            "ambiguous_fields": [],
            "human_gate_routed": False,
            "human_gate_checkpoint_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    payload["legacy_migration_events"] = events


def _raise_ambiguous_status(payload: Mapping[str, object]) -> None:
    source_id = _source_id(payload)
    checkpoint = create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.LOW_CONFIDENCE_FIELD,
        trigger_detail=(
            f"سجل قديم للكتاب «{_title(payload)}»: "
            "هل سبق أن حدّدتَ درجةَ هذا الكتاب بنفسك؟"
        ),
        fields_to_review=["reading_level_history"],
        current_values={
            "book_title": _title(payload),
            "reading_level": payload.get("level"),
        },
    )
    raise SourceEngineError(
        ErrorCode.LEGACY_RECORD_AMBIGUOUS_STATUS,
        (
            "legacy SourceMetadata has level populated but no level_status; "
            f"routed to human_gate checkpoint {checkpoint.checkpoint_id}"
        ),
    )


def _raise_ambiguous_provenance(payload: Mapping[str, object]) -> None:
    source_id = _source_id(payload)
    checkpoint = create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.LOW_CONFIDENCE_FIELD,
        trigger_detail=(
            f"سجل قديم للكتاب «{_title(payload)}»: "
            "مصدر التقييم غير واضح. هل سبق أن حدّدتَ درجةَ هذا الكتاب بنفسك؟"
        ),
        fields_to_review=["reading_level_assessment_source"],
        current_values={
            "book_title": _title(payload),
            "reading_level": payload.get("level"),
        },
    )
    raise SourceEngineError(
        ErrorCode.LEGACY_RECORD_AMBIGUOUS_PROVENANCE,
        (
            "legacy SourceMetadata has level populated but no level_provenance; "
            f"routed to human_gate checkpoint {checkpoint.checkpoint_id}"
        ),
    )


def _source_id(payload: Mapping[str, object]) -> str:
    value = payload.get("source_id")
    if isinstance(value, str) and value:
        return value
    return "unknown_source"


def _title(payload: Mapping[str, object]) -> str:
    value = payload.get("title_arabic")
    if isinstance(value, str) and value:
        return value
    return "هذا الكتاب"
