from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SourceFormat(str, Enum):
    SHAMELA_HTML = "shamela_html"
    SHAMELA_MULTI_VOLUME_HTML = "shamela_multi_volume_html"
    MULTIPART_WITH_SUPPLEMENTARY = "multipart_with_supplementary"
    PLAIN_TEXT = "plain_text"
    PLAIN_TEXT_MULTI_VOLUME = "plain_text_multi_volume"
    PDF = "pdf"
    PDF_TEXT = "pdf_text"
    PDF_SCANNED = "pdf_scanned"
    PDF_MULTI_VOLUME = "pdf_multi_volume"
    MIXED_FORMAT_DIRECTORY = "mixed_format_directory"
    IMAGE_SCAN = "image_scan"
    WORD_DOC = "word_doc"
    OWNER_AUTHORED = "owner_authored"


class SourcePathKind(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"


class IntakeMode(str, Enum):
    FILESYSTEM_PATH = "filesystem_path"


class RawUploadStatus(str, Enum):
    RECEIVED = "received"
    FROZEN = "frozen"
    AWAITING_OWNER_ACK = "awaiting_owner_ack"
    SOURCE_ENGINE_ACCEPTED = "source_engine_accepted"
    REJECTED_AT_SOURCE = "rejected_at_source"


class FreezeVerificationStatus(str, Enum):
    VERIFIED = "verified"
    FAILED = "failed"


class MemberKind(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"


class ContainerType(str, Enum):
    SHAMELA_SINGLE_HTML = "shamela_single_html"
    SHAMELA_MULTI_VOLUME_HTML = "shamela_multi_volume_html"
    MULTIPART_WITH_SUPPLEMENTARY = "multipart_with_supplementary"
    PDF = "pdf"
    PDF_MULTI_VOLUME = "pdf_multi_volume"
    PLAIN_TEXT = "plain_text"
    PLAIN_TEXT_MULTI_VOLUME = "plain_text_multi_volume"
    MIXED_FORMAT_DIRECTORY = "mixed_format_directory"


class NormalizationRoute(str, Enum):
    HTML_PARSE_PRIMARY = "html_parse_primary"
    PLAIN_TEXT_PARSE = "plain_text_parse"
    PDF_OCR_PRIMARY = "pdf_ocr_primary"
    PDF_TEXT_PRIMARY = "pdf_text_primary"


class CompletenessStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    MIXED = "mixed"
    INDETERMINATE = "indeterminate"


class SelfContainmentAssessment(str, Enum):
    SELF_CONTAINED = "self_contained"
    PARTIALLY_SELF_CONTAINED = "partially_self_contained"
    CONTEXT_DEPENDENT = "context_dependent"


class CrossVolumeDependencyAssessment(str, Enum):
    NON_MATERIAL = "non_material"
    MATERIAL = "material"
    UNKNOWN = "unknown"


class IntegrityStatus(str, Enum):
    SOUND = "sound"
    SUSPICIOUS = "suspicious"
    CORRUPT = "corrupt"


class PdfTextLayerStatus(str, Enum):
    ABSENT = "absent"
    CORRUPT = "corrupt"
    PRESENTATION_FORMS = "presentation_forms"
    CLEAN = "clean"


class PageLayoutHint(str, Enum):
    SINGLE_COLUMN = "single_column"
    DUAL_COLUMN = "dual_column"
    MARGINAL_NOTES = "marginal_notes"
    MIXED = "mixed"


class TrustTier(str, Enum):
    VERIFIED = "verified"
    FLAGGED = "flagged"
    OWNER_OVERRIDE = "owner_override"


class TextFidelity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class AuthorityLevel(str, Enum):
    PRIMARY = "primary"
    REFERENCE = "reference"
    MODERN_COMPILATION = "modern_compilation"
    UNKNOWN = "unknown"


class StructuralFormat(str, Enum):
    PROSE = "prose"
    VERSE = "verse"
    QA_FORMAT = "qa_format"
    TABULAR_KHILAF = "tabular_khilaf"
    TABULAR = "tabular"
    DICTIONARY = "dictionary"
    REFERENCE_ENTRIES = "reference_entries"
    COMMENTARY = "commentary"
    MIXED = "mixed"


class Genre(str, Enum):
    MATN = "matn"
    SHARH = "sharh"
    HASHIYAH = "hashiyah"
    MUKHTASAR = "mukhtasar"
    NAZM = "nazm"
    RISALAH = "risalah"
    TAQRIRAT = "taqrirat"
    MAWSUAH = "mawsuah"
    FATAWA = "fatawa"
    MUJAM = "mujam"
    TABAQAT = "tabaqat"
    FIQH_COMPARATIVE = "fiqh_comparative"
    HADITH_COLLECTION = "hadith_collection"
    TAFSIR = "tafsir"
    SIRAH = "sirah"
    TARIKH = "tarikh"
    ADAB = "adab"
    RIHLAH = "rihlah"
    USUL_AL_FIQH = "usul_al_fiqh"
    AMALI = "amali"
    MUSHAF = "mushaf"
    THABAT = "thabat"
    BARNAMAJ = "barnamaj"
    MASHYAKHAH = "mashyakhah"
    FAHRASAH = "fahrasah"
    WASIYYAH = "wasiyyah"
    JUZ = "juz"
    RADD = "radd"
    MUNAZARAH = "munazarah"
    OTHER = "other"


class HadithSubgenre(str, Enum):
    MUSANNAF = "musannaf"
    MUSNAD = "musnad"
    SUNAN = "sunan"
    JAMI = "jami"
    JUZ = "juz"
    TABAQAT_RIJAL = "tabaqat_rijal"
    HADITH_COMMENTARY = "hadith_commentary"
    MUJAM = "mujam"
    MUSTADRAK = "mustadrak"
    MUSTAKHRAJ = "mustakhraj"
    ARBAIN = "arbain"
    TAKHRIJ = "takhrij"
    ATRAF = "atraf"
    ILAL = "ilal"


class AttributionStatus(str, Enum):
    DEFINITIVE = "definitive"
    TRADITIONAL = "traditional"
    DISPUTED = "disputed"
    UNKNOWN = "unknown"


class WorkLevel(str, Enum):
    """Classical pedagogical-level vocabulary per CON-SRC-0011.

    The three-tier ladder mubtadiʾ → mutawassiṭ → muntahī is the classical
    tradition's own vocabulary for learner progression. The historiographic
    term ``mutaqaddim`` is REJECTED (category error — it denotes chronological
    priority among scholars, not pedagogical level).
    """

    MUBTADI = "mubtadiʾ"
    MUTAWASSIT = "mutawassiṭ"
    MUNTAHI = "muntahī"


class LevelStatus(str, Enum):
    """Processing-state enum for SourceMetadata per CON-SRC-0004 middle-path.

    The source engine emits only ``pending_taxonomy``, ``non_applicable_reference``,
    or ``assigned``; ``unprocessable_error`` is reserved for downstream engines
    after an attempted level determination concludes the text cannot be leveled.
    """

    PENDING_TAXONOMY = "pending_taxonomy"
    NON_APPLICABLE_REFERENCE = "non_applicable_reference"
    UNPROCESSABLE_ERROR = "unprocessable_error"
    ASSIGNED = "assigned"


class LevelProvenance(str, Enum):
    """Origin-tracking for an assigned ``level`` per ADV-012 stickiness.

    Populated IFF ``level`` is non-null. Prevents a downstream engine from
    silently overwriting an owner-asserted level.
    """

    OWNER_OVERRIDE = "owner_override"
    TAXONOMY_ENGINE = "taxonomy_engine"
    SYNTHESIS_ENGINE = "synthesis_engine"


# INV-SRC-0012 Axis 1: genre-level non-applicability set (the fann of the
# work has no classical pedagogical level). Phase 5b item 4 Option E-prime-final
# reconciled this set to six values that are ALL existing Genre enum members.
# Four values (mashyakhah, thabat, barnamaj, fahrasah) are archival/documentary
# forms whose organizing principle is transmission attestation or cataloging,
# not graduated pedagogical exposition. Two values (mushaf, hadith_collection)
# are retained from the pre-Phase-5b-item-4 set.
#
# This axis handles genre-level non-applicability only. Composite-structure
# non-applicability (a majmuʿ whose constituent rasāʾil carry leveled genres)
# is enforced via Axis 2 (composite_work_type == "majmu") — see INV-SRC-0012
# rule statement and SourceMetadata.enforce_level_invariants.
#
# Removed from the prior 7-value set per 2026-04-22 2-run Gemini CLI unanimous
# scholarly findings:
#   - rijal_dictionary, biographical_dictionary — English aliases / nawʿ of
#     the existing Genre.TABAQAT (tarajim family); not fann-level themselves.
#   - majmu — a structural composite (Axis 2), not a fann.
#   - fatwa_compilation, lexicon — English aliases of the existing Genre.FATAWA
#     and Genre.MUJAM which are canonical classical forms, not non-applicable.
NON_APPLICABLE_GENRE_VALUES: frozenset[str] = frozenset(
    {
        "mushaf",
        "hadith_collection",
        "mashyakhah",
        "thabat",
        "barnamaj",
        "fahrasah",
    }
)


class ProcessingStatus(str, Enum):
    STAGING = "staging"
    ACQUIRED = "acquired"
    NORMALIZING = "normalizing"
    NORMALIZED = "normalized"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    WITHDRAWN = "withdrawn"


class AcquisitionPath(str, Enum):
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"


class ErrorSeverity(str, Enum):
    FATAL = "fatal"
    WARNING = "warning"
    INFO = "info"


class ErrorCode(str, Enum):
    # Step 10 — upload_receipt
    PATH_NOT_FOUND = "SRC-E-PATH-NOT-FOUND"
    PATH_UNREADABLE = "SRC-E-PATH-UNREADABLE"
    EMPTY_FILE = "SRC-E-EMPTY-FILE"
    # Step 20 — freeze_and_manifest
    FREEZE_VERIFY = "SRC-E-FREEZE-VERIFY"
    DUPLICATE_INGEST = "SRC-E-DUPLICATE-INGEST"
    # Step 30 — container_classification
    EMPTY_DIRECTORY = "SRC-E-EMPTY-DIRECTORY"
    SUPPLEMENTARY_UNRECORDED = "SRC-E-SUPPLEMENTARY-UNRECORDED"
    ENCODING = "SRC-E-ENCODING"
    # Step 40 — intake_analysis
    PDF_CORRUPT = "SRC-E-PDF-CORRUPT"
    INTEGRITY_CORRUPT = "SRC-E-INTEGRITY-CORRUPT"
    INTAKE_TEAM_INCOMPLETE = "SRC-E-INTAKE-TEAM-INCOMPLETE"
    NO_WORK_IDENTITY = "SRC-E-NO-WORK-IDENTITY"
    PDF_TEXT_EVIDENCE_MUTATED = "SRC-E-PDF-TEXT-EVIDENCE-MUTATED"
    PDF_TEXT_EVIDENCE_DROPPED = "SRC-E-PDF-TEXT-EVIDENCE-DROPPED"
    # Step 50 — metadata_deliberation
    HINT_FIELD = "SRC-E-HINT-FIELD"
    TRUST_AGENT_COUNT = "SRC-E-TRUST-AGENT-COUNT"
    DOSSIER_INCOMPLETE = "SRC-E-DOSSIER-INCOMPLETE"
    INCOMPLETE_RESEARCH = "SRC-E-INCOMPLETE-RESEARCH"
    AUTHOR_AGENT_COUNT = "SRC-E-AUTHOR-AGENT-COUNT"
    METADATA_OWNER_GATE = "SRC-E-METADATA-OWNER-GATE"
    SCIENCE_BLOCK = "SRC-E-SCIENCE-BLOCK"
    SINGLE_SCIENCE_CONTRACT = "SRC-E-SINGLE-SCIENCE-CONTRACT"
    HONORIFIC_ONLY_NAME = "SRC-E-HONORIFIC-ONLY-NAME"
    WORK_OUTPUT_MISSING = "SRC-E-WORK-OUTPUT-MISSING"
    WORK_EVIDENCE = "SRC-E-WORK-EVIDENCE"
    # Step 60 — source_admission_and_normalization_handoff
    PREMATURE_ADMISSION = "SRC-E-PREMATURE-ADMISSION"
    INVALID_ADMISSION = "SRC-E-INVALID-ADMISSION"
    SUBMISSION_RISK_BYPASS = "SRC-E-SUBMISSION-RISK-BYPASS"
    PDF_STATUS_MISSING = "SRC-E-PDF-STATUS-MISSING"
    PDF_ROUTE = "SRC-E-PDF-ROUTE"
    VOLUME_COUNT_MISSING = "SRC-E-VOLUME-COUNT-MISSING"
    LEVEL_FIELD_MISSING = "SRC-E-LEVEL-FIELD-MISSING"
    LEVEL_OVERRIDE_NONAPPLICABLE = "SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE"
    HANDOFF_EVIDENCE_DROPPED = "SRC-E-HANDOFF-EVIDENCE-DROPPED"
    HANDOFF_EVIDENCE_DROPPED_NESTED = "SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED"
    # Implementation-only (not spec-derived, used for internal guards)
    SOURCE_ID_MISMATCH = "SRC-E-SOURCE-ID-MISMATCH"
    DELIBERATION_NOT_PERSISTED = "SRC-E-DELIBERATION-NOT-PERSISTED"


class WarningCode(str, Enum):
    """Non-fatal warnings emitted during pipeline processing."""

    MIXED_FORMAT = "SRC-W-MIXED-FORMAT"
    LAYOUT_HINT_UNKNOWN = "SRC-W-LAYOUT-HINT-UNKNOWN"
    AMBIGUOUS_SCHOLAR_IDENTITY = "SRC-W-AMBIGUOUS-SCHOLAR-IDENTITY"
    MONITOR_MISSING = "SRC-W-MONITOR-MISSING"
    GENRE_UNKNOWN = "SRC-W-GENRE-UNKNOWN"
    MULTILAYER_NO_EVIDENCE = "SRC-W-MULTILAYER-NO-EVIDENCE"
    STRUCTURAL_FORMAT_DEFAULT = "SRC-W-STRUCTURAL-FORMAT-DEFAULT"
    NO_DATES_FOR_ROLE_CHECK = "SRC-W-NO-DATES-FOR-ROLE-CHECK"


class HumanGateTrigger(str, Enum):
    AUTHOR_DISAMBIGUATION = "author_disambiguation"
    WORK_MATCH_UNCERTAIN = "work_match_uncertain"
    LOW_CONFIDENCE_FIELD = "low_confidence_field"
    TRUST_FLAGGED = "trust_flagged"
    CONSENSUS_DISAGREEMENT = "consensus_disagreement"
    GENRE_CHAIN_UNRESOLVED = "genre_chain_unresolved"
    ENRICHMENT_CRITICAL_FIELD = "enrichment_critical_field"
    SCHOLAR_CONFLICT = "scholar_conflict"
    AUTHOR_SCIENCE_MISMATCH = "author_science_mismatch"
    OWNER_SUBMISSION_RISK = "owner_submission_risk"


class ScholarReference(BaseModel):
    canonical_id: str
    name_arabic: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_of_identification: str


class TextLayer(BaseModel):
    layer_type: Literal["matn", "sharh", "hashiyah", "tahqiq_note"]
    author: ScholarReference


class TrustworthinessFactor(BaseModel):
    name: str
    weight: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=0.0, le=1.0)
    reason: str


class InferredFieldConfidence(BaseModel):
    genre: float = Field(ge=0.0, le=1.0)
    science_scope: float = Field(ge=0.0, le=1.0)
    level: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    structural_format: float = Field(ge=0.0, le=1.0)
    authority_level: float = Field(ge=0.0, le=1.0)
    multi_layer: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    genre_chain: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    author: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class MetadataHistoryEntry(BaseModel):
    field: str
    old_value: Optional[str] = None
    new_value: str
    changed_by: str
    timestamp: str


class HumanGateCheckpoint(BaseModel):
    checkpoint_id: str
    source_id: str
    trigger: HumanGateTrigger
    trigger_detail: str
    fields_to_review: list[str]
    current_values: dict[str, Any]
    alternatives: Optional[list[dict[str, Any]]] = None
    created_at: str
    status: str = "pending"
    resolution: Optional[str] = None
    resolved_at: Optional[str] = None
    elevated_result: Optional[dict[str, Any]] = None


class ScholarAuthorityRecord(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    canonical_id: str
    canonical_name_ar: str = Field(min_length=1)
    status: Literal[
        "provisional",
        "confirmed",
        "merged_into",
        "split_disputed",
        "deprecated",
    ] = "confirmed"
    display_name: Optional[str] = None
    full_name_lineage: Optional[str] = None
    known_as: list[str] = Field(default_factory=list)
    name_variants: list[str] = Field(default_factory=list)
    kunya: Optional[str] = None
    laqab: list[str] = Field(default_factory=list)
    nisba: list[str] = Field(default_factory=list)
    birth_date_hijri: Optional[int] = Field(None, ge=0)
    birth_date_ce: Optional[int] = Field(None, ge=0)
    death_date_hijri: Optional[int] = Field(default=None, ge=0)
    death_date_ce: Optional[int] = Field(None, ge=0)
    death_date_approximate: bool = False
    era_century_hijri: Optional[int] = Field(None, ge=0)
    geographic_origin: Optional[str] = None
    geographic_active: list[str] = Field(default_factory=list)
    school_affiliations: dict[str, Optional[str]] = Field(default_factory=dict)
    sectarian_tradition: Optional[str] = None
    teachers: list[str] = Field(default_factory=list)
    students: list[str] = Field(default_factory=list)
    known_works: list[str] = Field(default_factory=list)
    primary_science: Optional[str] = None
    source_book_ids: list[str] = Field(default_factory=list)
    scholarly_standing: Optional[str] = None
    methodology_notes: Optional[str] = None
    methodological_stance: Optional[str] = None
    disambiguation_notes: Optional[str] = None
    sources_encountered_in: list[str] = Field(default_factory=list)
    record_completeness: float = Field(0.0, ge=0.0, le=1.0)
    data_provenance_score: float = Field(0.0, ge=0.0, le=1.0)
    record_sources: list[str] = Field(default_factory=list)
    evidence_sources: list[ScholarEvidenceSource] = Field(default_factory=list)
    external_anchor_references: list[ExternalAnchorReference] = Field(default_factory=list)
    evidence_quality: Optional[str] = None
    merged_into: Optional[str] = None
    revision_history: list[MetadataHistoryEntry] = Field(default_factory=list)
    last_updated: str
    genealogy_metadata: Optional[dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_name(self) -> "ScholarAuthorityRecord":
        if not self.canonical_name_ar.strip():
            raise ValueError("canonical_name_ar must be non-empty")
        return self


class SourceError(BaseModel):
    timestamp: str
    source_id: Optional[str] = None
    error_code: ErrorCode
    severity: ErrorSeverity
    message: str
    recovery_action: str
    context: Optional[dict[str, Any]] = None


class RawUploadRecord(BaseModel):
    submission_id: str
    submitted_path: str
    submitted_path_kind: SourcePathKind
    intake_mode: IntakeMode = IntakeMode.FILESYSTEM_PATH
    owner_hint_payload: dict[str, Any] = Field(default_factory=dict)
    receipt_timestamp: str
    status: RawUploadStatus
    error_code: Optional[ErrorCode] = None


class FrozenMemberManifestEntry(BaseModel):
    member_name: str
    member_kind: MemberKind
    member_size_bytes: int = Field(ge=0)
    member_sha256: str = Field(min_length=64, max_length=64)


class FrozenSource(BaseModel):
    source_id: str
    source_sha256: str = Field(min_length=64, max_length=64)
    frozen_blob_path: str
    freeze_verification_status: FreezeVerificationStatus
    frozen_member_manifest: list[FrozenMemberManifestEntry] = Field(default_factory=list)
    submission_id: Optional[str] = None
    duplicate_of_source_id: Optional[str] = None


class ManifestVolumeMember(BaseModel):
    member_name: str
    member_kind: MemberKind = MemberKind.FILE
    member_sha256: Optional[str] = Field(None, min_length=64, max_length=64)
    member_size_bytes: Optional[int] = Field(None, ge=0)
    volume_number: Optional[int] = Field(None, ge=1)
    format: Optional[SourceFormat] = None


class ContainerClassification(BaseModel):
    source_id: Optional[str] = None
    container_type: ContainerType
    normalization_route: NormalizationRoute
    volume_manifest: list[ManifestVolumeMember] = Field(default_factory=list)
    supplementary_members: list[ManifestVolumeMember] = Field(default_factory=list)
    text_encoding: Optional[str] = None
    warnings: list[WarningCode] = Field(default_factory=list)


class TitleEvidence(BaseModel):
    title_text: str
    provenance: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class WorkIdentityCandidate(BaseModel):
    canonical_title_arabic: str
    work_id: Optional[str] = None
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    source_agent: Optional[str] = None


class WorkIdentityProposal(BaseModel):
    candidates: list[WorkIdentityCandidate] = Field(default_factory=list)


class CollectionMatchOutput(BaseModel):
    match_status: Optional[str] = None
    matched_work_id: Optional[str] = None
    matched_edition_group_id: Optional[str] = None
    parent_work_id: Optional[str] = None
    present_volumes: list[int] = Field(default_factory=list)
    missing_volumes: list[int] = Field(default_factory=list)
    candidate_match_ids: list[CollectionMatchCandidate] = Field(default_factory=list)
    evidence_summary: Optional[str] = None


class DeclaredVsObservedCounts(BaseModel):
    physical_page_count: Optional[int] = Field(default=None, ge=0)
    declared_volume_count: Optional[int] = Field(default=None, ge=0)
    observed_volume_count: Optional[int] = Field(default=None, ge=0)


class ParentWorkPresenceModel(BaseModel):
    appears_part_of_larger_work: bool = False
    present_volumes: list[int] = Field(default_factory=list)
    missing_volumes: list[int] = Field(default_factory=list)


class PdfTextEvidence(BaseModel):
    physical_page_number: int = Field(ge=1)
    extracted_text: str


class SubWorkInventoryEntry(BaseModel):
    sub_title: str
    volume_number: Optional[int] = Field(None, ge=1)
    page_start: Optional[int] = Field(None, ge=1)
    page_end: Optional[int] = Field(None, ge=1)
    detection_method: Literal["toc_entry", "volume_boundary", "structural_signal"]


class HoldingCompletenessDelta(BaseModel):
    holding_id: str
    newly_present_volumes: list[int] = Field(default_factory=list)


class IntakeDossier(BaseModel):
    dossier_id: str
    source_id: Optional[str] = None
    source_format: Optional[SourceFormat] = None
    normalization_route: Optional[NormalizationRoute] = None
    title_evidence: list[TitleEvidence] = Field(default_factory=list)
    work_identity_proposal: WorkIdentityProposal = Field(default_factory=WorkIdentityProposal)
    collection_match_candidates: CollectionMatchOutput = Field(default_factory=CollectionMatchOutput)
    declared_vs_observed_counts: DeclaredVsObservedCounts = Field(
        default_factory=lambda: DeclaredVsObservedCounts(
            physical_page_count=None,
            declared_volume_count=None,
            observed_volume_count=None,
        )
    )
    completeness_status: Optional[CompletenessStatus] = None
    partiality_reasons: list[str] = Field(default_factory=list)
    self_containment_assessment: Optional[SelfContainmentAssessment] = None
    cross_volume_dependency_assessment: Optional[CrossVolumeDependencyAssessment] = None
    integrity_status: Optional[IntegrityStatus] = None
    integrity_findings: list[str] = Field(default_factory=list)
    study_quality_risk_flags: list[str] = Field(default_factory=list)
    parent_work_presence_model: ParentWorkPresenceModel = Field(default_factory=ParentWorkPresenceModel)
    pdf_text_layer_status: Optional[PdfTextLayerStatus] = None
    pdf_text_encoding: Optional[str] = None
    pdf_text_evidence: list[PdfTextEvidence] = Field(default_factory=list)
    page_layout_hint: Optional[PageLayoutHint] = None
    composite_work_type: Optional[Literal["majmu", "possible"]] = None
    sub_work_inventory: list[SubWorkInventoryEntry] = Field(default_factory=list)
    contains_isnad_chains: bool = False
    holding_completeness_delta: Optional[HoldingCompletenessDelta] = None


class HintComparisonResult(BaseModel):
    hint_field: str
    hint_value: Any
    inferred_value: Any
    match: bool
    confidence_delta: float = 0.0


class HintInvestigation(BaseModel):
    field: str
    hint_value: Any
    inferred_value: Any
    status: str
    opened_reason: str


class CollectionMatchCandidate(BaseModel):
    candidate_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class ScholarProfileSource(str, Enum):
    SCHOLAR_AUTHORITY = "scholar_authority"
    STRUCTURED_DATABASE = "structured_database"
    AGENT_SYNTHESIS = "agent_synthesis"
    UNAVAILABLE = "unavailable"


class ScholarEvidenceSource(BaseModel):
    book_id: str
    evidence_type: str
    raw_evidence: str


class ExternalAnchorReference(BaseModel):
    source: str
    identifier: str
    retrieval_date: str
    confidence: float = Field(ge=0.0, le=1.0)


class ScholarProfile(BaseModel):
    full_name_lineage: Optional[str] = None
    scholarly_title: Optional[str] = None
    madhab: Optional[str] = None
    primary_science: Optional[str] = None
    era_description: Optional[str] = None
    profile_source: ScholarProfileSource = ScholarProfileSource.UNAVAILABLE
    status: str = "available"
    unavailable_reason: Optional[str] = None
    data_conflicts: list[dict[str, Any]] = Field(default_factory=list)


class WorkRelationship(BaseModel):
    relationship_type: Literal[
        "is_commentary_on",
        "is_supercommentary_on",
        "is_abridgement_of",
        "is_versification_of",
        "has_part",
        "is_part_of",
        "is_lecture_notes_of",
    ]
    target_work_title: str
    target_work_author: Optional[str] = None
    confidence: Literal["high", "medium", "low"]


class AuthorOutputPosition(BaseModel):
    position: str
    display_name: str
    canonical_id: Optional[str] = None
    canonical_match_name: Optional[str] = None
    full_name_lineage: Optional[str] = None
    ism: Optional[str] = None
    nasab_tokens: list[str] = Field(default_factory=list)
    kunya: Optional[str] = None
    laqab_tokens: list[str] = Field(default_factory=list)
    laqab_is_primary_identifier: bool = False
    death_hijri: Optional[int] = Field(default=None, ge=0)
    death_hijri_verification: Optional[str] = None
    nisba_tokens: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    source_agent: str
    source_agents: list[str] = Field(default_factory=list)
    entity_type: Literal["person", "institution"] = "person"
    scholar_profile: Optional[ScholarProfile] = None

    @model_validator(mode="after")
    def sync_source_agents(self) -> "AuthorOutputPosition":
        if not self.source_agents:
            self.source_agents = [self.source_agent]
        return self


class AuthorOutput(BaseModel):
    status: str
    positions: list[AuthorOutputPosition] = Field(default_factory=list)
    attribution_confidence: Optional[str] = None
    attribution_confidence_ar: Optional[str] = None
    anonymous_evidence: Optional[str] = None
    attributed_author: Optional[str] = None
    false_attribution_evidence: list[str] = Field(default_factory=list)


class WorkOutputPosition(BaseModel):
    work_id: Optional[str] = None
    canonical_title_arabic: str
    edition_label: Optional[str] = None
    volume_designation: Optional[str] = None
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    source_agent: str


class WorkOutput(BaseModel):
    status: str
    positions: list[WorkOutputPosition] = Field(default_factory=list)


class TrustDecisionPosition(BaseModel):
    decision: str
    evidence_summary: str
    confidence: float = Field(ge=0.0, le=1.0)


class TrustDecision(BaseModel):
    decision: str
    trust_path: str
    supporting_agents: list[str] = Field(default_factory=list)
    evidence_summary: str = ""
    positions: list[TrustDecisionPosition] = Field(default_factory=list)


class CaseComplexityRecord(BaseModel):
    case_id: Optional[str] = None
    source_id: Optional[str] = None
    field: Optional[str] = None
    case_complexity: str
    trust_path: Optional[str] = None
    signals: dict[str, Any] = Field(default_factory=dict)
    status: Optional[str] = None
    completed_at: Optional[str] = None


class MonitorEvidenceCoverage(BaseModel):
    used_source_types: list[str] = Field(default_factory=list)
    meets_minimum: bool


class MonitorIndependenceCheck(BaseModel):
    agent_ids: list[str] = Field(default_factory=list)
    distinct_agent_ids: bool
    independent_before_exchange: bool


class MonitorUncertaintyFlags(BaseModel):
    multi_position_output: bool
    ocr_unreliable_source: bool
    confidence_ordering_applied: bool


class MonitorSuggestedPolicyUpdate(BaseModel):
    code: str
    summary: str


class MonitorFeedbackRecord(BaseModel):
    case_id: str
    source_id: str
    field: str
    trust_path: str
    completed_at: str
    evidence_coverage: MonitorEvidenceCoverage
    independence_check: MonitorIndependenceCheck
    uncertainty_flags: MonitorUncertaintyFlags
    spec_violations: list[ErrorCode] = Field(default_factory=list)
    suggested_policy_updates: list[MonitorSuggestedPolicyUpdate] = Field(default_factory=list)


class FailureAnalysis(BaseModel):
    agent_id: str
    error_type: str
    what_missed: str
    corrective_evidence: list[str] = Field(default_factory=list)
    guardrail_suggestion: str


class DisagreementCaseRecord(BaseModel):
    case_id: str
    source_id: str
    field: str
    round_count: int = Field(ge=0)
    resolution_state: str
    positions: list[AuthorOutputPosition] = Field(default_factory=list)
    failure_analysis: Optional[FailureAnalysis] = None


class MetadataDeliberationInput(BaseModel):
    source_id: str
    title_arabic: str
    source_format: SourceFormat
    structural_format: StructuralFormat
    acquisition_path: str
    frozen_path: str
    frozen_hash: str
    frozen_file_hashes: dict[str, str]
    status: str
    science_scope: list[str] = Field(default_factory=list)
    genre: Optional[Genre] = None
    is_multi_layer: bool = False
    text_fidelity: TextFidelity = TextFidelity.UNKNOWN
    trust_tier: TrustTier = TrustTier.VERIFIED
    trust_score: float = Field(default=0.0, ge=0.0, le=1.0)
    authority_level: Optional[AuthorityLevel | str] = None
    author_death_hijri: Optional[int] = Field(default=None, ge=0)
    work_id: Optional[str] = None
    work_output: Optional[WorkOutput] = None
    collection_match_output: Optional[CollectionMatchOutput] = None
    level: Optional[WorkLevel] = None
    level_status: Optional[LevelStatus] = None
    level_provenance: Optional[LevelProvenance] = None
    composite_work_type: Optional[Literal["majmu", "possible"]] = None
    edition_info: Optional[dict[str, Any]] = None
    publisher: Optional[str] = None
    author_positions: list[AuthorOutputPosition] = Field(default_factory=list)
    owner_hint_payload: dict[str, Any] = Field(default_factory=dict)
    verification_agents: list[str] = Field(default_factory=list)
    research_source_types: list[str] = Field(default_factory=list)


class MetadataDeliberationResult(BaseModel):
    source_metadata: SourceMetadata
    case_complexity_record: CaseComplexityRecord
    monitor_feedback: list[MonitorFeedbackRecord] = Field(default_factory=list)
    disagreement_cases: list[DisagreementCaseRecord] = Field(default_factory=list)


class MuhaqiqAssessment(BaseModel):
    standing_level: str
    evidence_sources: list[str] = Field(default_factory=list)
    last_verified: str


class EditionFingerprint(BaseModel):
    publisher: Optional[str] = None
    muhaqqiq: Optional[str] = None
    distinguishing_signals: list[str] = Field(default_factory=list)


class EditionGroup(BaseModel):
    edition_group_id: str
    work_id: Optional[str] = None
    edition_fingerprint: EditionFingerprint = Field(default_factory=EditionFingerprint)
    expected_volume_count: Optional[int] = Field(None, ge=1)


class VolumeHolding(BaseModel):
    volume_number: int = Field(ge=1)
    presence_state: Literal["missing", "present_primary", "present_alternate", "conflict"]
    source_ids: list[str] = Field(default_factory=list)


class EditionHolding(BaseModel):
    holding_id: str
    edition_group_id: str
    holding_state: Literal[
        "draft",
        "active_partial",
        "active_complete",
        "active_mixed",
        "superseded",
        "archived",
        "indeterminate",
    ]
    coherence_state: Literal["coherent", "mixed", "unknown"] = "unknown"
    expected_volume_count: Optional[int] = Field(None, ge=1)
    volume_holdings: list[VolumeHolding] = Field(default_factory=list)
    preferred_rank: Optional[Literal["primary"]] = None
    superseded_by: Optional[str] = None
    supersession_policy: Optional[Literal["regen_required", "regen_optional"]] = None


class OwnerSubmissionRiskCase(BaseModel):
    source_id: str
    owner_ack_required: bool = True
    risk_flags: list[str] = Field(default_factory=list)
    gate_status: str = "awaiting_owner_ack"
    risk_summary: Optional[str] = None
    recommended_owner_action: Optional[str] = None
    notes_from_owner: Optional[str] = None


class DisplayCard(BaseModel):
    status: str = "complete"
    display_name: Optional[str] = None
    scholarly_title: Optional[str] = None
    death_date_display: Optional[str] = None
    madhab: Optional[str] = None
    book_title: Optional[str] = None
    science_and_genre: Optional[str] = None
    author_blurb: Optional[str] = None
    layer_tree_short: Optional[str] = None
    partial_reasons: list[str] = Field(default_factory=list)


class SourceMetadata(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="allow")

    source_id: str
    title_arabic: str
    source_format: SourceFormat
    structural_format: StructuralFormat
    intake_timestamp: str
    acquisition_path: str
    frozen_path: str
    frozen_hash: str
    frozen_file_hashes: dict[str, str]
    status: str

    work_id: Optional[str] = None
    human_label: Optional[str] = None
    author: Optional[ScholarReference] = None
    science_scope: list[str] = Field(default_factory=list)
    genre: Optional[Genre] = None
    hadith_subgenre: Optional[HadithSubgenre] = None
    candidate_subgenres: list[HadithSubgenre] = Field(default_factory=list)
    genre_dispute: list[str] = Field(default_factory=list)
    authority_level: Optional[AuthorityLevel] = None
    is_multi_layer: bool = False
    multi_layer_evidence: list[str] = Field(default_factory=list)
    matn_embedding_style: Optional[Literal["interlinear", "separated", "marginal", "mazj"]] = None
    text_layers: list[TextLayer] = Field(default_factory=list)
    trust_tier: TrustTier = TrustTier.VERIFIED
    trust_score: float = Field(default=0.0, ge=0.0, le=1.0)
    trust_factors: list[TrustworthinessFactor] = Field(default_factory=list)
    trust_reason: str = ""
    text_fidelity: TextFidelity = TextFidelity.UNKNOWN
    text_fidelity_reason: str = ""
    confidence_scores: Optional[InferredFieldConfidence] = None
    page_count: Optional[int] = Field(default=None, ge=1)
    volume_count: Optional[int] = Field(default=None, ge=1)
    source_sha256: Optional[str] = None
    frozen_blob_path: Optional[str] = None
    registry_entry_id: Optional[str] = None
    author_output: Optional[AuthorOutput] = None
    work_output: Optional[WorkOutput] = None
    collection_match_output: Optional[CollectionMatchOutput] = None
    trust_decision: Optional[TrustDecision] = None
    completeness_status: Optional[CompletenessStatus] = None
    integrity_status: Optional[IntegrityStatus] = None
    normalization_route: Optional[NormalizationRoute] = None
    pdf_text_layer_status: Optional[PdfTextLayerStatus] = None
    page_count_physical: Optional[int] = Field(default=None, ge=1)
    page_layout_hint: Optional[PageLayoutHint] = None
    muhaqiq_output: Optional[MuhaqiqAssessment] = None
    death_date_hijri: Optional[int] = Field(default=None, ge=0)
    level: Optional[WorkLevel] = None
    level_status: LevelStatus
    level_provenance: Optional[LevelProvenance] = None
    composite_work_type: Optional[Literal["majmu", "possible"]] = None
    edition_info: Optional[dict[str, Any]] = None
    publisher: Optional[str] = None
    hint_comparison_results: list[HintComparisonResult] = Field(default_factory=list)
    hint_investigation: list[HintInvestigation] = Field(default_factory=list)
    admission_reason: Optional[str] = None
    display_card: Optional[DisplayCard] = None
    work_relationships: list[WorkRelationship] = Field(default_factory=list)
    study_quality_risk_flags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def sync_compatibility_fields(self) -> "SourceMetadata":
        if self.source_sha256 is None:
            self.source_sha256 = self.frozen_hash
        if self.frozen_blob_path is None:
            self.frozen_blob_path = self.frozen_path
        return self

    @model_validator(mode="after")
    def enforce_level_invariants(self) -> "SourceMetadata":
        # CON-SRC-0004 invariant 1: level_status == "assigned" IFF level non-null.
        if self.level_status == LevelStatus.ASSIGNED and self.level is None:
            raise ValueError(
                "CON-SRC-0004 invariant 1 violation: level_status='assigned' "
                "requires level to be non-null"
            )
        # CON-SRC-0004 invariant 2: non-assigned level_status IMPLIES level is null.
        if self.level_status != LevelStatus.ASSIGNED and self.level is not None:
            raise ValueError(
                "CON-SRC-0004 invariant 2 violation: level_status="
                f"'{self.level_status.value}' requires level to be null, "
                f"got level='{self.level.value if isinstance(self.level, WorkLevel) else self.level}'"
            )
        # CON-SRC-0004 invariant 3 + INV-SRC-0012 3-axis gate:
        # non_applicable_reference IMPLIES at least one non-applicability axis
        # fires. Axis 1: genre.value is in the six-value
        # NON_APPLICABLE_GENRE_VALUES frozenset. Axis 2: composite_work_type ==
        # "majmu" (the work is a structural composite whose container-level
        # pedagogy does not apply even if the declared genre is leveled — see
        # INV-SRC-0012 AC-3/AC-4). Axis 3 (HadithSubgenre pedagogical carve-
        # out) is deferred to Phase 5b item 23. An invariant-3 violation
        # fires only when NEITHER Axis 1 NOR Axis 2 fires.
        if self.level_status == LevelStatus.NON_APPLICABLE_REFERENCE:
            genre_value = self.genre.value if self.genre is not None else None
            axis_1_fires = genre_value in NON_APPLICABLE_GENRE_VALUES
            axis_2_fires = self.composite_work_type == "majmu"
            if not (axis_1_fires or axis_2_fires):
                raise ValueError(
                    "CON-SRC-0004 invariant 3 violation: level_status="
                    "'non_applicable_reference' requires genre in "
                    f"{sorted(NON_APPLICABLE_GENRE_VALUES)} (Axis 1) OR "
                    "composite_work_type == 'majmu' (Axis 2) per "
                    f"INV-SRC-0012; got genre='{genre_value}', "
                    f"composite_work_type='{self.composite_work_type}'"
                )
        # CON-SRC-0004 invariant 4 (level_status non-null) is enforced by the
        # field declaration: ``level_status: LevelStatus`` has no default.

        # ADV-012 stickiness: level_provenance tracks who assigned the level,
        # so it is non-null IFF level is non-null. Prevents a downstream
        # engine from silently overwriting an owner-asserted level.
        if self.level is not None and self.level_provenance is None:
            raise ValueError(
                "ADV-012 stickiness violation: level is populated but "
                "level_provenance is null — provenance must be set whenever "
                "level is set"
            )
        if self.level is None and self.level_provenance is not None:
            raise ValueError(
                "ADV-012 stickiness violation: level is null but "
                f"level_provenance='{self.level_provenance.value}' is set"
            )
        return self


class NormalizationInput(BaseModel):
    source_id: str
    source_format_legacy: str
    frozen_path: str
    frozen_hash: str
    page_count: Optional[int] = Field(default=None, ge=1)
    volume_count: Optional[int] = Field(default=None, ge=1)
    title_arabic: str
    author: Optional[str] = None
    work_id: Optional[str] = None
    structural_format: StructuralFormat
    is_multi_layer: bool
    genre: Optional[Genre] = None
    text_fidelity: Optional[TextFidelity] = None
    trust_tier: Optional[TrustTier] = None


class NormalizationHandoffBundle(BaseModel):
    source_metadata: SourceMetadata
    normalization_input: NormalizationInput
    frozen_member_manifest: list[FrozenMemberManifestEntry] = Field(default_factory=list)
    completeness_status: Optional[CompletenessStatus] = None
    integrity_status: Optional[IntegrityStatus] = None
    declared_vs_observed_counts: DeclaredVsObservedCounts = Field(
        default_factory=lambda: DeclaredVsObservedCounts(
            physical_page_count=None,
            declared_volume_count=None,
            observed_volume_count=None,
        )
    )
    pdf_text_layer_status: Optional[PdfTextLayerStatus] = None
    page_layout_hint: Optional[PageLayoutHint] = None
    unresolved_disputes: list[dict[str, Any]] = Field(default_factory=list)
