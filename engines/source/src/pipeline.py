from __future__ import annotations

import hashlib
import logging
import os
import re
import shutil
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from bs4 import BeautifulSoup
from charset_normalizer import from_bytes

from engines.source.contracts import (
    CollectionMatchOutput,
    CompletenessStatus,
    ContainerClassification,
    ContainerType,
    CrossVolumeDependencyAssessment,
    DeclaredVsObservedCounts,
    ErrorCode,
    FreezeVerificationStatus,
    FrozenMemberManifestEntry,
    FrozenSource,
    IntakeDossier,
    IntakeMode,
    IntegrityStatus,
    ManifestVolumeMember,
    MemberKind,
    MetadataDeliberationInput,
    MetadataDeliberationResult,
    NormalizationRoute,
    ParentWorkPresenceModel,
    PdfTextEvidence,
    PdfTextLayerStatus,
    RawUploadRecord,
    RawUploadStatus,
    SelfContainmentAssessment,
    SourceFormat,
    SourcePathKind,
    TitleEvidence,
    WarningCode,
    WorkIdentityCandidate,
    WorkIdentityProposal,
)
from engines.source.src.admission import SourceAdmissionResult, admit_source_and_build_handoff
from engines.source.src.deliberation import run_metadata_deliberation
from engines.source.src.errors import SourceEngineError
from engines.source.src.pdf_inspection import PdfInspectionResult, inspect_pdf
from engines.source.src.store import SourceStore


_ISNAD_PATTERN = re.compile(
    r"(?<![\u0600-\u06FF])(?:حدثنا|اخبرنا|انبانا|سمعت|قرات\s+(?:على|علي)|اجاز لي|ناولني)(?![\u0600-\u06FF])"
)
_MOJIBAKE_MARKERS = ("ط£", "ط§", "ط®")
logger = logging.getLogger(__name__)


class SourcePipeline:
    def __init__(self, workspace_root: Path) -> None:
        self.store = SourceStore(workspace_root)

    def upload_receipt(
        self,
        submitted_path: Path,
        owner_hint_payload: dict[str, object] | None = None,
    ) -> RawUploadRecord:
        path = submitted_path.resolve()
        self._validate_receipt_input(path)
        record = RawUploadRecord(
            submission_id=f"sub_{uuid4().hex[:8]}",
            submitted_path=str(path),
            submitted_path_kind=SourcePathKind.DIRECTORY if path.is_dir() else SourcePathKind.FILE,
            intake_mode=IntakeMode.FILESYSTEM_PATH,
            owner_hint_payload=owner_hint_payload or {},
            receipt_timestamp=self._utc_now(),
            status=RawUploadStatus.RECEIVED,
        )
        self.store.save_raw_upload(record)
        return record

    def freeze_and_manifest(self, submission_id: str) -> FrozenSource:
        record = self.store.get_raw_upload(submission_id)
        source_path = Path(record.submitted_path)
        manifest = self._build_manifest(source_path)
        source_sha256 = self._hash_manifest(manifest)
        if self.store.find_frozen_by_sha(source_sha256) is not None:
            raise SourceEngineError(ErrorCode.DUPLICATE_INGEST, source_path.as_posix())
        source_id = f"src_{source_sha256[:8]}"
        frozen_blob_path = self._freeze_source(source_path, source_id)
        frozen_manifest = self._build_manifest(Path(frozen_blob_path))
        if self._hash_manifest(frozen_manifest) != source_sha256:
            raise SourceEngineError(ErrorCode.FREEZE_VERIFY, source_path.as_posix())
        frozen = FrozenSource(
            source_id=source_id,
            source_sha256=source_sha256,
            frozen_blob_path=str(frozen_blob_path),
            freeze_verification_status=FreezeVerificationStatus.VERIFIED,
            frozen_member_manifest=manifest,
            submission_id=submission_id,
        )
        self.store.save_frozen_source(frozen)
        record.status = RawUploadStatus.FROZEN
        self.store.update_raw_upload(record)
        return frozen

    def classify_container(self, source_id: str) -> ContainerClassification:
        frozen = self.store.get_frozen_source(source_id)
        members = frozen.frozen_member_manifest
        classification = (
            self._classify_single_member(source_id, members[0])
            if len(members) == 1
            else self._classify_multi_member(source_id, members)
        )
        self.store.save_container_classification(classification)
        return classification

    def intake_analysis(self, source_id: str) -> IntakeDossier:
        frozen = self.store.get_frozen_source(source_id)
        classification = self.store.get_container_classification(source_id)
        if classification.container_type == ContainerType.MIXED_FORMAT_DIRECTORY:
            dossier = self._build_mixed_format_dossier(frozen, classification)
            self.store.save_intake_dossier(dossier)
            return dossier
        dossier = (
            self._build_pdf_dossier(frozen, classification)
            if classification.container_type in {ContainerType.PDF, ContainerType.PDF_MULTI_VOLUME}
            else self._build_textual_dossier(frozen, classification)
        )
        self.store.save_intake_dossier(dossier)
        return dossier

    def metadata_deliberation(
        self,
        source_id: str,
        deliberation_input: MetadataDeliberationInput,
    ) -> MetadataDeliberationResult:
        frozen = self.store.get_frozen_source(source_id)
        dossier = self.store.get_intake_dossier(source_id)
        result = run_metadata_deliberation(
            source_id=source_id,
            frozen=frozen,
            dossier=dossier,
            deliberation_input=deliberation_input,
        )
        self.store.save_case_complexity_record(result.case_complexity_record)
        for record in result.monitor_feedback:
            self.store.save_monitor_feedback(record)
        for record in result.disagreement_cases:
            self.store.save_disagreement_case(record)
        return result

    def source_admission_and_normalization_handoff(
        self,
        source_id: str,
        deliberation_result: MetadataDeliberationResult,
        owner_acknowledged: bool,
    ) -> SourceAdmissionResult:
        self._validate_persisted_deliberation_result(source_id, deliberation_result)
        frozen = self.store.get_frozen_source(source_id)
        dossier = self.store.get_intake_dossier(source_id)
        return admit_source_and_build_handoff(
            store=self.store,
            frozen=frozen,
            dossier=dossier,
            deliberation_result=deliberation_result,
            owner_acknowledged=owner_acknowledged,
        )

    def _validate_persisted_deliberation_result(
        self,
        source_id: str,
        deliberation_result: MetadataDeliberationResult,
    ) -> None:
        if deliberation_result.source_metadata.source_id != source_id:
            raise SourceEngineError(
                ErrorCode.SOURCE_ID_MISMATCH,
                f"deliberation result source_id={deliberation_result.source_metadata.source_id} does not match pipeline source_id={source_id}",
            )
        try:
            stored_case = self.store.get_case_complexity_record(source_id)
        except KeyError as exc:
            raise SourceEngineError(
                ErrorCode.DELIBERATION_NOT_PERSISTED,
                f"no persisted step-50 artifact set exists for source_id={source_id}",
            ) from exc
        stored_feedback = self.store.get_monitor_feedback(source_id)
        if (
            stored_case.case_id != deliberation_result.case_complexity_record.case_id
            or not stored_feedback
            or any(record.case_id != stored_case.case_id for record in stored_feedback)
        ):
            raise SourceEngineError(
                ErrorCode.DELIBERATION_NOT_PERSISTED,
                f"no persisted step-50 artifact set matches case_id={deliberation_result.case_complexity_record.case_id}",
            )

    def _classify_single_member(
        self,
        source_id: str,
        member: FrozenMemberManifestEntry,
    ) -> ContainerClassification:
        suffix = Path(member.member_name).suffix.lower()  # safe: ASCII file extension only
        mapping = {
            ".htm": (ContainerType.SHAMELA_SINGLE_HTML, NormalizationRoute.HTML_PARSE_PRIMARY, None),
            ".html": (ContainerType.SHAMELA_SINGLE_HTML, NormalizationRoute.HTML_PARSE_PRIMARY, None),
            ".txt": (ContainerType.PLAIN_TEXT, NormalizationRoute.PLAIN_TEXT_PARSE, "utf-8"),
            ".pdf": (ContainerType.PDF, NormalizationRoute.PDF_OCR_PRIMARY, None),
        }
        container_type, route, encoding = mapping[suffix]
        volume_manifest = [self._volume_member(member, None, self._format_for_suffix(suffix))]
        return ContainerClassification(
            source_id=source_id,
            container_type=container_type,
            normalization_route=route,
            volume_manifest=volume_manifest,
            text_encoding=encoding,
        )

    def _classify_multi_member(
        self,
        source_id: str,
        members: list[FrozenMemberManifestEntry],
    ) -> ContainerClassification:
        suffixes = {
            Path(member.member_name).suffix.lower()  # safe: ASCII file extensions only
            for member in members
        }
        if suffixes <= {".htm", ".html"}:
            return self._classify_html_directory(source_id, members)
        if suffixes <= {".pdf"}:
            return self._uniform_directory(source_id, members, ContainerType.PDF_MULTI_VOLUME)
        if suffixes <= {".txt"}:
            return self._uniform_directory(source_id, members, ContainerType.PLAIN_TEXT_MULTI_VOLUME)
        ordered = sorted(members, key=lambda member: member.member_name)
        return ContainerClassification(
            source_id=source_id,
            container_type=ContainerType.MIXED_FORMAT_DIRECTORY,
            normalization_route=NormalizationRoute.PLAIN_TEXT_PARSE,
            volume_manifest=[
                self._volume_member(
                    item,
                    None,
                    self._format_for_suffix(
                        Path(item.member_name).suffix.lower()  # safe: ASCII file extension only
                    ),
                )
                for item in ordered
            ],
            warnings=[WarningCode.MIXED_FORMAT],
        )

    def _classify_html_directory(
        self,
        source_id: str,
        members: list[FrozenMemberManifestEntry],
    ) -> ContainerClassification:
        numbered = [item for item in members if Path(item.member_name).stem.isdigit()]
        supplementary = [item for item in members if not Path(item.member_name).stem.isdigit()]
        if not numbered:
            raise SourceEngineError(ErrorCode.EMPTY_DIRECTORY, source_id)
        ordered = sorted(numbered, key=lambda item: int(Path(item.member_name).stem))
        return ContainerClassification(
            source_id=source_id,
            container_type=(
                ContainerType.MULTIPART_WITH_SUPPLEMENTARY
                if supplementary
                else ContainerType.SHAMELA_MULTI_VOLUME_HTML
            ),
            normalization_route=NormalizationRoute.HTML_PARSE_PRIMARY,
            volume_manifest=[
                self._volume_member(item, index + 1, SourceFormat.SHAMELA_HTML)
                for index, item in enumerate(ordered)
            ],
            supplementary_members=[
                self._volume_member(item, None, SourceFormat.SHAMELA_HTML)
                for item in sorted(supplementary, key=lambda item: item.member_name)
            ],
        )

    def _uniform_directory(
        self,
        source_id: str,
        members: list[FrozenMemberManifestEntry],
        container_type: ContainerType,
    ) -> ContainerClassification:
        ordered = sorted(members, key=lambda member: member.member_name)
        route = NormalizationRoute.PLAIN_TEXT_PARSE
        source_format = (
            SourceFormat.PLAIN_TEXT
            if container_type == ContainerType.PLAIN_TEXT_MULTI_VOLUME
            else SourceFormat.PDF
        )
        if container_type == ContainerType.PDF_MULTI_VOLUME:
            route = self._classify_pdf_directory_route(source_id, ordered)
        return ContainerClassification(
            source_id=source_id,
            container_type=container_type,
            normalization_route=route,
            volume_manifest=[
                self._volume_member(item, index + 1, source_format)
                for index, item in enumerate(ordered)
            ],
            text_encoding="utf-8" if container_type == ContainerType.PLAIN_TEXT_MULTI_VOLUME else None,
        )

    def _classify_pdf_directory_route(
        self,
        source_id: str,
        members: list[FrozenMemberManifestEntry],
    ) -> NormalizationRoute:
        statuses = [
            inspect_pdf(self.store.frozen_root / source_id / member.member_name).text_layer_status
            for member in members
        ]
        if all(
            status in {PdfTextLayerStatus.CLEAN, PdfTextLayerStatus.PRESENTATION_FORMS}
            for status in statuses
        ):
            return NormalizationRoute.PDF_TEXT_PRIMARY
        return NormalizationRoute.PDF_OCR_PRIMARY

    def _build_pdf_dossier(
        self,
        frozen: FrozenSource,
        classification: ContainerClassification,
    ) -> IntakeDossier:
        inspections = [
            inspect_pdf(self._member_path(frozen, member.member_name))
            for member in classification.volume_manifest
        ]
        primary_path = self._member_path(frozen, classification.volume_manifest[0].member_name)
        inspection = self._aggregate_pdf_inspections(inspections)
        title = primary_path.stem
        return IntakeDossier(
            dossier_id=f"dossier_{uuid4().hex[:8]}",
            source_id=frozen.source_id,
            source_format=SourceFormat.PDF,
            normalization_route=inspection.normalization_route,
            title_evidence=[TitleEvidence(title_text=title, provenance="filename")],
            work_identity_proposal=WorkIdentityProposal(
                candidates=[WorkIdentityCandidate(canonical_title_arabic=title, evidence=["filename"], confidence=0.6)]
            ),
            collection_match_candidates=CollectionMatchOutput(),
            declared_vs_observed_counts=DeclaredVsObservedCounts(
                physical_page_count=inspection.page_count,
                declared_volume_count=None,
                observed_volume_count=len(classification.volume_manifest),
            ),
            completeness_status=CompletenessStatus.COMPLETE if classification.container_type == ContainerType.PDF else CompletenessStatus.INDETERMINATE,
            self_containment_assessment=SelfContainmentAssessment.SELF_CONTAINED,
            cross_volume_dependency_assessment=CrossVolumeDependencyAssessment.NON_MATERIAL,
            integrity_status=IntegrityStatus.SOUND,
            parent_work_presence_model=ParentWorkPresenceModel(
                appears_part_of_larger_work=classification.container_type == ContainerType.PDF_MULTI_VOLUME,
                present_volumes=[item.volume_number for item in classification.volume_manifest if item.volume_number is not None],
            ),
            pdf_text_layer_status=inspection.text_layer_status,
            pdf_text_encoding=inspection.text_encoding,
            pdf_text_evidence=self._pdf_evidence(inspection),
            page_layout_hint=inspection.page_layout_hint,
        )

    def _build_textual_dossier(
        self,
        frozen: FrozenSource,
        classification: ContainerClassification,
    ) -> IntakeDossier:
        primary_path = self._member_path(frozen, classification.volume_manifest[0].member_name)
        title = self._extract_title(primary_path)
        content = self._read_text(primary_path)
        observed_volumes = len(classification.volume_manifest) or 1
        return IntakeDossier(
            dossier_id=f"dossier_{uuid4().hex[:8]}",
            source_id=frozen.source_id,
            source_format=self._textual_source_format(classification.container_type),
            normalization_route=classification.normalization_route,
            title_evidence=[TitleEvidence(title_text=title, provenance="document_title")],
            work_identity_proposal=WorkIdentityProposal(
                candidates=[WorkIdentityCandidate(canonical_title_arabic=title, evidence=["document_title"], confidence=0.8)]
            ),
            collection_match_candidates=CollectionMatchOutput(),
            declared_vs_observed_counts=DeclaredVsObservedCounts(
                physical_page_count=None,
                declared_volume_count=None,
                observed_volume_count=observed_volumes,
            ),
            completeness_status=CompletenessStatus.COMPLETE,
            self_containment_assessment=SelfContainmentAssessment.SELF_CONTAINED,
            cross_volume_dependency_assessment=CrossVolumeDependencyAssessment.NON_MATERIAL,
            integrity_status=IntegrityStatus.SOUND,
            study_quality_risk_flags=[],
            parent_work_presence_model=ParentWorkPresenceModel(
                appears_part_of_larger_work=observed_volumes > 1,
                present_volumes=[item.volume_number for item in classification.volume_manifest if item.volume_number is not None],
            ),
            contains_isnad_chains=self._contains_isnad(content),
        )

    def _build_mixed_format_dossier(
        self,
        frozen: FrozenSource,
        classification: ContainerClassification,
    ) -> IntakeDossier:
        return IntakeDossier(
            dossier_id=f"dossier_{uuid4().hex[:8]}",
            source_id=frozen.source_id,
            source_format=None,
            normalization_route=None,
            title_evidence=[TitleEvidence(title_text=Path(frozen.frozen_blob_path).name, provenance="directory_name")],
            work_identity_proposal=WorkIdentityProposal(candidates=[]),
            collection_match_candidates=CollectionMatchOutput(),
            declared_vs_observed_counts=DeclaredVsObservedCounts(
                physical_page_count=None,
                declared_volume_count=None,
                observed_volume_count=len(classification.volume_manifest),
            ),
            completeness_status=CompletenessStatus.INDETERMINATE,
            self_containment_assessment=SelfContainmentAssessment.CONTEXT_DEPENDENT,
            cross_volume_dependency_assessment=CrossVolumeDependencyAssessment.UNKNOWN,
            integrity_status=IntegrityStatus.SUSPICIOUS,
            study_quality_risk_flags=["mixed_format_directory"],
        )

    def _extract_title(self, path: Path) -> str:
        if path.suffix.lower() in {".htm", ".html"}:  # safe: ASCII file extension only
            soup = BeautifulSoup(self._read_text(path), "html.parser")
            if soup.title and soup.title.string:
                return soup.title.string.strip(" \t\n\r")
        return path.stem

    def _read_text(self, path: Path) -> str:
        """Read text file with encoding detection per REQ-SRC-0020."""
        raw = path.read_bytes()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            best = from_bytes(raw).best()
            if best is None or best.encoding is None:
                raise SourceEngineError(ErrorCode.ENCODING, path.as_posix())
            decoded = str(best)
            if any(marker in decoded for marker in _MOJIBAKE_MARKERS):
                raise SourceEngineError(ErrorCode.ENCODING, path.as_posix())
            return decoded

    def _contains_isnad(self, content: str) -> bool:
        soup = BeautifulSoup(content, "html.parser")
        flattened = soup.get_text(" ")
        simplified = "".join(
            char for char in flattened if not unicodedata.combining(char)
        ).replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")
        return bool(_ISNAD_PATTERN.search(simplified))

    def _aggregate_pdf_inspections(
        self,
        inspections: list[PdfInspectionResult],
    ) -> PdfInspectionResult:
        total_pages = sum(item.page_count for item in inspections)
        worst = {
            "corrupt": 3,
            "absent": 2,
            "presentation_forms": 1,
            "clean": 0,
        }
        chosen = max(inspections, key=lambda item: worst[item.text_layer_status.value])
        layout_values = {item.page_layout_hint for item in inspections}
        sample = next((item for item in inspections if item.sample_text.strip(" \t\n\r")), chosen)
        return PdfInspectionResult(
            page_count=total_pages,
            text_layer_status=chosen.text_layer_status,
            text_encoding=chosen.text_encoding,
            normalization_route=chosen.normalization_route,
            sample_text=sample.sample_text,
            sample_page_number=sample.sample_page_number,
            page_layout_hint=chosen.page_layout_hint if len(layout_values) == 1 else chosen.page_layout_hint.MIXED,
        )

    def _textual_source_format(self, container_type: ContainerType) -> SourceFormat:
        return (
            SourceFormat.PLAIN_TEXT
            if container_type in {ContainerType.PLAIN_TEXT, ContainerType.PLAIN_TEXT_MULTI_VOLUME}
            else SourceFormat.SHAMELA_HTML
        )

    def _pdf_evidence(self, inspection: PdfInspectionResult) -> list[PdfTextEvidence]:
        if not inspection.sample_text or inspection.sample_page_number is None:
            return []
        return [
            PdfTextEvidence(
                physical_page_number=inspection.sample_page_number,
                extracted_text=inspection.sample_text,
            )
        ]

    def _member_path(self, frozen: FrozenSource, member_name: str) -> Path:
        return Path(frozen.frozen_blob_path) / Path(member_name)

    def _volume_member(
        self,
        member: FrozenMemberManifestEntry,
        volume_number: int | None,
        source_format: SourceFormat,
    ) -> ManifestVolumeMember:
        return ManifestVolumeMember(
            member_name=member.member_name,
            member_kind=member.member_kind,
            member_sha256=member.member_sha256,
            member_size_bytes=member.member_size_bytes,
            volume_number=volume_number,
            format=source_format,
        )

    def _format_for_suffix(self, suffix: str) -> SourceFormat:
        return {
            ".htm": SourceFormat.SHAMELA_HTML,
            ".html": SourceFormat.SHAMELA_HTML,
            ".txt": SourceFormat.PLAIN_TEXT,
            ".pdf": SourceFormat.PDF,
        }[suffix]

    def _validate_receipt_input(self, path: Path) -> None:
        """Validate submitted path per REQ-SRC-0001 error_conditions."""
        if not path.exists():
            raise SourceEngineError(ErrorCode.PATH_NOT_FOUND, path.as_posix())
        if not os.access(path, os.R_OK):
            raise SourceEngineError(ErrorCode.PATH_UNREADABLE, path.as_posix())
        if path.is_file() and path.stat().st_size == 0:
            raise SourceEngineError(ErrorCode.EMPTY_FILE, path.as_posix())

    def _build_manifest(self, source_path: Path) -> list[FrozenMemberManifestEntry]:
        if source_path.is_file():
            return [self._manifest_entry(source_path, source_path.name)]
        files = sorted(path for path in source_path.rglob("*") if path.is_file())
        return [self._manifest_entry(path, path.relative_to(source_path).as_posix()) for path in files]

    def _manifest_entry(self, path: Path, member_name: str) -> FrozenMemberManifestEntry:
        return FrozenMemberManifestEntry(
            member_name=member_name,
            member_kind=MemberKind.FILE,
            member_size_bytes=path.stat().st_size,
            member_sha256=self._sha256_bytes(path.read_bytes()),
        )

    def _hash_manifest(self, manifest: list[FrozenMemberManifestEntry]) -> str:
        if len(manifest) == 1:
            return manifest[0].member_sha256
        joined = "\n".join(
            f"{entry.member_name}\0{entry.member_sha256}" for entry in manifest
        ).encode("utf-8")
        return self._sha256_bytes(joined)

    def _freeze_source(self, source_path: Path, source_id: str) -> Path:
        target = self.store.frozen_root / source_id
        if source_path.is_file():
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target / source_path.name)
            return target
        shutil.copytree(source_path, target)
        return target

    def _sha256_bytes(self, payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
