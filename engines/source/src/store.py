from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, TypeVar

from pydantic import BaseModel

from engines.source.contracts import (
    CaseComplexityRecord,
    ContainerClassification,
    DisagreementCaseRecord,
    FrozenSource,
    IntakeDossier,
    MonitorFeedbackRecord,
    NormalizationHandoffBundle,
    OwnerSubmissionRiskCase,
    RawUploadRecord,
    SourceMetadata,
)


ModelT = TypeVar("ModelT", bound=BaseModel)


class SourceStore:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.raw_uploads_path = workspace_root / "raw_upload_registry.json"
        self.frozen_sources_path = workspace_root / "frozen_sources.json"
        self.container_classifications_path = workspace_root / "container_classifications.json"
        self.intake_dossiers_path = workspace_root / "intake_dossiers.json"
        self.source_collection_path = workspace_root / "source_collection.json"
        self.handoff_bundles_path = workspace_root / "normalization_handoffs.json"
        self.risk_cases_path = workspace_root / "owner_submission_risk_cases.json"
        self.case_complexity_records_path = workspace_root / "case_complexity_records.json"
        self.monitor_feedback_path = workspace_root / "monitor_feedback.json"
        self.disagreement_cases_path = workspace_root / "disagreement_cases.json"
        self.frozen_root = workspace_root / "frozen"
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.frozen_root.mkdir(parents=True, exist_ok=True)

    def get_container_classification(self, source_id: str) -> ContainerClassification:
        for record in self._load_models(
            self.container_classifications_path, ContainerClassification
        ):
            if getattr(record, "source_id", None) == source_id:
                return record
        raise KeyError(source_id)

    def get_frozen_source(self, source_id: str) -> FrozenSource:
        for record in self._load_models(self.frozen_sources_path, FrozenSource):
            if record.source_id == source_id:
                return record
        raise KeyError(source_id)

    def get_intake_dossier(self, source_id: str) -> IntakeDossier:
        for record in self._load_models(self.intake_dossiers_path, IntakeDossier):
            if getattr(record, "source_id", None) == source_id:
                return record
        raise KeyError(source_id)

    def get_source_collection_record(self, source_id: str) -> SourceMetadata:
        for record in self._load_models(self.source_collection_path, SourceMetadata):
            if record.source_id == source_id:
                return record
        raise KeyError(source_id)

    def get_handoff_bundle(self, source_id: str) -> NormalizationHandoffBundle:
        for record in self._load_models(
            self.handoff_bundles_path, NormalizationHandoffBundle
        ):
            if record.source_metadata.source_id == source_id:
                return record
        raise KeyError(source_id)

    def get_risk_case(self, source_id: str) -> OwnerSubmissionRiskCase:
        for record in self._load_models(self.risk_cases_path, OwnerSubmissionRiskCase):
            if record.source_id == source_id:
                return record
        raise KeyError(source_id)

    def get_raw_upload(self, submission_id: str) -> RawUploadRecord:
        for record in self._load_models(self.raw_uploads_path, RawUploadRecord):
            if record.submission_id == submission_id:
                return record
        raise KeyError(submission_id)

    def get_case_complexity_record(self, source_id: str) -> CaseComplexityRecord:
        history = self.get_case_complexity_history(source_id)
        if history:
            return history[-1]
        raise KeyError(source_id)

    def get_case_complexity_history(self, source_id: str) -> list[CaseComplexityRecord]:
        return [
            record
            for record in self._load_models(self.case_complexity_records_path, CaseComplexityRecord)
            if record.source_id == source_id
        ]

    def get_monitor_feedback(self, source_id: str) -> list[MonitorFeedbackRecord]:
        try:
            latest_case_id = self.get_case_complexity_record(source_id).case_id
        except KeyError:
            return []
        return [
            record
            for record in self._load_models(self.monitor_feedback_path, MonitorFeedbackRecord)
            if record.source_id == source_id and record.case_id == latest_case_id
        ]

    def get_disagreement_cases(self, source_id: str) -> list[DisagreementCaseRecord]:
        try:
            latest_case_id = self.get_case_complexity_record(source_id).case_id
        except KeyError:
            return []
        return [
            record
            for record in self._load_models(self.disagreement_cases_path, DisagreementCaseRecord)
            if record.source_id == source_id and record.case_id == latest_case_id
        ]

    def find_frozen_by_sha(self, source_sha256: str) -> FrozenSource | None:
        for record in self._load_models(self.frozen_sources_path, FrozenSource):
            if record.source_sha256 == source_sha256:
                return record
        return None

    def save_raw_upload(self, record: RawUploadRecord) -> None:
        records = self._load_models(self.raw_uploads_path, RawUploadRecord)
        records.append(record)
        self._write_models(self.raw_uploads_path, records)

    def save_frozen_source(self, record: FrozenSource) -> None:
        records = self._load_models(self.frozen_sources_path, FrozenSource)
        records.append(record)
        self._write_models(self.frozen_sources_path, records)

    def save_container_classification(self, record: ContainerClassification) -> None:
        records = [
            item
            for item in self._load_models(
                self.container_classifications_path, ContainerClassification
            )
            if item.source_id != record.source_id
        ]
        records.append(record)
        self._write_models(self.container_classifications_path, records)

    def save_intake_dossier(self, record: IntakeDossier) -> None:
        records = [
            item
            for item in self._load_models(self.intake_dossiers_path, IntakeDossier)
            if item.source_id != record.source_id
        ]
        records.append(record)
        self._write_models(self.intake_dossiers_path, records)

    def save_source_collection_record(self, record: SourceMetadata) -> None:
        records = [
            item
            for item in self._load_models(self.source_collection_path, SourceMetadata)
            if item.source_id != record.source_id
        ]
        records.append(record)
        self._write_models(self.source_collection_path, records)

    def save_handoff_bundle(self, record: NormalizationHandoffBundle) -> None:
        records = [
            item
            for item in self._load_models(
                self.handoff_bundles_path, NormalizationHandoffBundle
            )
            if item.source_metadata.source_id != record.source_metadata.source_id
        ]
        records.append(record)
        self._write_models(self.handoff_bundles_path, records)

    def save_risk_case(self, record: OwnerSubmissionRiskCase) -> None:
        records = [
            item
            for item in self._load_models(self.risk_cases_path, OwnerSubmissionRiskCase)
            if item.source_id != record.source_id
        ]
        records.append(record)
        self._write_models(self.risk_cases_path, records)

    def save_case_complexity_record(self, record: CaseComplexityRecord) -> None:
        records = self._load_models(self.case_complexity_records_path, CaseComplexityRecord)
        records = [item for item in records if item.case_id != record.case_id]
        records.append(record)
        self._write_models(self.case_complexity_records_path, records)

    def save_monitor_feedback(self, record: MonitorFeedbackRecord) -> None:
        records = self._load_models(self.monitor_feedback_path, MonitorFeedbackRecord)
        records = [
            item
            for item in records
            if not (item.source_id == record.source_id and item.case_id == record.case_id and item.field == record.field)
        ]
        records.append(record)
        self._write_models(self.monitor_feedback_path, records)

    def save_disagreement_case(self, record: DisagreementCaseRecord) -> None:
        records = self._load_models(self.disagreement_cases_path, DisagreementCaseRecord)
        records = [item for item in records if item.case_id != record.case_id]
        records.append(record)
        self._write_models(self.disagreement_cases_path, records)

    def update_raw_upload(self, record: RawUploadRecord) -> None:
        records = self._load_models(self.raw_uploads_path, RawUploadRecord)
        updated = [
            record if item.submission_id == record.submission_id else item for item in records
        ]
        self._write_models(self.raw_uploads_path, updated)

    def _load_models(self, path: Path, model_type: type[ModelT]) -> list[ModelT]:
        if not path.exists():
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [model_type.model_validate(item) for item in raw]

    def _write_models(self, path: Path, records: Sequence[BaseModel]) -> None:
        payload = [record.model_dump(mode="json") for record in records]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
