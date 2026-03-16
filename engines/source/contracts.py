"""Source Engine Contracts — Machine-readable schemas derived from SPEC.md §2-§3.

These Pydantic models are the AUTHORITATIVE data contracts for the source engine.
They serve three purposes:
1. Implementation reference — Claude Code uses these to build the engine
2. Runtime validation — every output is validated against these before writing to disk
3. Test generation — tests use these to create valid/invalid test data

SPEC.md remains the behavioral authority (HOW to process). These models define
WHAT the data looks like at each boundary.

When SPEC.md §2/§3 and these models disagree, update the models — they must match the SPEC.

CHANGELOG (IMPLEMENTATION_PREP session, 2026-03-06):
- Added TextFidelity enum (SPEC §4.A.4 — was float, now categorical)
- Added ProcessingStatus enum (SPEC §4.A.10)
- Added AcquisitionPath enum (SPEC §4.A.2)
- Added ErrorCode enum with all 18+ SRC_* codes (SPEC §7)
- Added ErrorSeverity enum (SPEC §7)
- Added OWNER_OVERRIDE to TrustTier (SPEC §4.A.8)
- Changed SourceMetadata.muhaqiq from str to ScholarReference (SPEC §4.A.5)
- Added InferredFieldConfidence + needs_review_fields (SPEC §4.A.4, §5)
- Added format_specific_metadata dict (SPEC §4.A.3)
- Added page_count to SourceMetadata (SPEC §4.A.3)
- Added EnrichmentRequest, HumanGateCheckpoint, WorkRelationshipEdge,
  SourceError, RegistryPendingWrite, CitationDiscoveryRequest,
  RelevanceEvaluation, GapAnalysisItem models
- Fixed WorkRegistryEntry.genre to use Genre enum
- Added human_label to SourceRegistryEntry
- Fixed StructuralFormat enum values to match SPEC exactly
- Fixed GenreRelationType enum values to match SPEC §4.A.9 exactly
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────

class SourceFormat(str, Enum):
    """Recognized source formats (SPEC §4.A.2 Step 2: Format Detection)."""
    SHAMELA_HTML = "shamela_html"
    PDF_TEXT = "pdf_text"
    PDF_SCANNED = "pdf_scanned"
    IMAGE_SCAN = "image_scan"
    PLAIN_TEXT = "plain_text"
    EPUB = "epub"
    WORD_DOC = "word_doc"
    OWNER_AUTHORED = "owner_authored"


class OwnerAuthoredType(str, Enum):
    """Types of owner-authored content (SPEC §2)."""
    STUDY_NOTE = "study_note"
    TARJIH = "tarjih"
    RESEARCH_DRAFT = "research_draft"
    LESSON_TRANSCRIPTION = "lesson_transcription"
    OBSERVATION = "observation"


class TrustTier(str, Enum):
    """Source trustworthiness tiers (SPEC §4.A.8).

    Three tiers — not two. OWNER_OVERRIDE preserves the original evaluation.
    """
    VERIFIED = "verified"
    FLAGGED = "flagged"
    OWNER_OVERRIDE = "owner_override"


class TextFidelity(str, Enum):
    """Text quality assessment separate from scholarly trust (SPEC §4.A.4).

    Determined by source type:
    - Shamela structured text → HIGH
    - Text-embedded PDF → HIGH
    - Professionally scanned PDF → MEDIUM
    - iPhone photos → LOW
    - Unknown provenance → UNKNOWN
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class AuthorityLevel(str, Enum):
    """Source authority level (SPEC §4.A.4)."""
    PRIMARY = "primary"
    REFERENCE = "reference"
    MODERN_COMPILATION = "modern_compilation"


class StructuralFormat(str, Enum):
    """Structural format of the source text (SPEC §4.A.4).

    Values match SPEC exactly: prose, verse, qa_format, tabular_khilaf,
    dictionary, commentary, mixed.
    """
    PROSE = "prose"
    VERSE = "verse"
    QA_FORMAT = "qa_format"
    TABULAR_KHILAF = "tabular_khilaf"
    DICTIONARY = "dictionary"
    COMMENTARY = "commentary"
    MIXED = "mixed"


class Genre(str, Enum):
    """Primary genre classification (SPEC §4.A.4).

    Exhaustive list — no additions without SPEC update AND enum update here.
    """
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
    OTHER = "other"


class GenreRelationType(str, Enum):
    """Types of work-to-work relationships (SPEC §4.A.9).

    Values match the SPEC relationship type names exactly.
    """
    SHARH_OF = "sharh_of"
    HASHIYAH_ON = "hashiyah_on"
    MUKHTASAR_OF = "mukhtasar_of"
    NAZM_OF = "nazm_of"
    TAQRIRAT_ON = "taqrirat_on"
    RESPONDS_TO = "responds_to"
    CITES = "cites"


class WorkLevel(str, Enum):
    """Scholarly level of a work (SPEC §4.A.4)."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SPECIALIST = "specialist"


class AttributionStatus(str, Enum):
    """Authorship attribution certainty (SPEC §4.A.4).

    Captures whether the work's authorship is historically secure.
    - definitive: uncontested and well-documented
    - traditional: conventionally accepted but not independently established (default for classical works)
    - disputed: actively contested among scholars
    - unknown: no author identified or identifiable

    When disputed, author.confidence is capped at 0.70.
    When unknown, author.confidence is set to 0.0.
    """
    DEFINITIVE = "definitive"
    TRADITIONAL = "traditional"
    DISPUTED = "disputed"
    UNKNOWN = "unknown"


class ProcessingStatus(str, Enum):
    """Pipeline processing status (SPEC §4.A.10).

    Transitions: staging → acquired → normalizing → normalized → processing → complete
    Any stage can → error. Owner decision can → withdrawn.
    """
    STAGING = "staging"
    ACQUIRED = "acquired"
    NORMALIZING = "normalizing"
    NORMALIZED = "normalized"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    WITHDRAWN = "withdrawn"


class AcquisitionPath(str, Enum):
    """How a source was acquired (SPEC §4.A.2)."""
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"


class ErrorSeverity(str, Enum):
    """Error severity levels (SPEC §7)."""
    FATAL = "fatal"
    WARNING = "warning"
    INFO = "info"


class ErrorCode(str, Enum):
    """All source engine error codes (SPEC §7).

    Every code has a defined severity and recovery action in the SPEC.
    """
    UNSUPPORTED_FORMAT = "SRC_UNSUPPORTED_FORMAT"
    EMPTY_INPUT = "SRC_EMPTY_INPUT"
    INVALID_ENRICHMENT = "SRC_INVALID_ENRICHMENT"
    DUPLICATE_EXACT = "SRC_DUPLICATE_EXACT"
    DUPLICATE_WORK = "SRC_DUPLICATE_WORK"
    AUTHOR_AMBIGUOUS = "SRC_AUTHOR_AMBIGUOUS"
    WORK_MATCH_UNCERTAIN = "SRC_WORK_MATCH_UNCERTAIN"
    LOW_CONFIDENCE = "SRC_LOW_CONFIDENCE"
    METADATA_INCONSISTENCY = "SRC_METADATA_INCONSISTENCY"
    FREEZE_FAILED = "SRC_FREEZE_FAILED"
    REGISTRY_CONFLICT = "SRC_REGISTRY_CONFLICT"
    OCR_LOW_QUALITY = "SRC_OCR_LOW_QUALITY"
    REPO_UNAVAILABLE = "SRC_REPO_UNAVAILABLE"
    CONSENSUS_DISAGREEMENT = "SRC_CONSENSUS_DISAGREEMENT"
    FREEZE_COPY_CORRUPT = "SRC_FREEZE_COPY_CORRUPT"
    FREEZE_PERMISSION_FAILED = "SRC_FREEZE_PERMISSION_FAILED"
    STAGING_MODIFIED = "SRC_STAGING_MODIFIED"
    REGISTRATION_INTERRUPTED = "SRC_REGISTRATION_INTERRUPTED"
    ENRICHMENT_CRITICAL_FIELD = "SRC_ENRICHMENT_CRITICAL_FIELD"
    SCHOLAR_DATE_CONFLICT = "SRC_SCHOLAR_DATE_CONFLICT"
    SCHOLAR_SCHOOL_CONFLICT = "SRC_SCHOLAR_SCHOOL_CONFLICT"
    SCHOLAR_TEMPORAL_INCONSISTENCY = "SRC_SCHOLAR_TEMPORAL_INCONSISTENCY"
    FORMAT_STRUCTURE_MISSING = "SRC_FORMAT_STRUCTURE_MISSING"
    # Content quality inspection codes (SPEC §4.A.3 / §7, Comment #1 session)
    PAGE_COUNT_MISMATCH = "SRC_PAGE_COUNT_MISMATCH"
    CONTENT_MINIMAL = "SRC_CONTENT_MINIMAL"
    ENCODING_SUSPECT = "SRC_ENCODING_SUSPECT"
    HIGH_EMPTY_RATIO = "SRC_HIGH_EMPTY_RATIO"
    # Attribution status code (SPEC §4.A.4 / §7, Comment #1 session)
    ATTRIBUTION_DISPUTED = "SRC_ATTRIBUTION_DISPUTED"
    # Death date verification (SPEC §4.A.4, ERR-03 pattern)
    DEATH_DATE_UNVERIFIED = "SRC_DEATH_DATE_UNVERIFIED"
    # Validation and scholar authority codes (Session 5a)
    SCHEMA_VIOLATION = "SRC_SCHEMA_VIOLATION"
    MULTI_LAYER_VIOLATION = "SRC_MULTI_LAYER_VIOLATION"
    SCHOLAR_NAME_BLOCKED = "SRC_SCHOLAR_NAME_BLOCKED"
    SCHOLAR_SELF_REFERENCE = "SRC_SCHOLAR_SELF_REFERENCE"
    # Generic internal error — used only for truly unexpected exceptions
    INTERNAL_ERROR = "SRC_INTERNAL_ERROR"
    # Deferred error codes (only fire from deferred capabilities, not implemented in Stage 1)
    KITAB_CACHE_MISSING = "SRC_KITAB_CACHE_MISSING"
    KITAB_CACHE_CORRUPT = "SRC_KITAB_CACHE_CORRUPT"
    USUL_DATA_MISSING = "SRC_USUL_DATA_MISSING"
    WIKIDATA_TIMEOUT = "SRC_WIKIDATA_TIMEOUT"
    COMPARISON_DEFERRED = "SRC_COMPARISON_DEFERRED"
    FREEZE_CLEANUP_FAILED = "SRC_FREEZE_CLEANUP_FAILED"
    OPENITI_CACHE_CORRUPT = "SRC_OPENITI_CACHE_CORRUPT"
    COMPARISON_INCONCLUSIVE = "SRC_COMPARISON_INCONCLUSIVE"


class HumanGateTrigger(str, Enum):
    """Reasons a human gate checkpoint is created (SPEC §5, Layer 2)."""
    AUTHOR_DISAMBIGUATION = "author_disambiguation"
    WORK_MATCH_UNCERTAIN = "work_match_uncertain"
    LOW_CONFIDENCE_FIELD = "low_confidence_field"
    TRUST_FLAGGED = "trust_flagged"
    CONSENSUS_DISAGREEMENT = "consensus_disagreement"
    GENRE_CHAIN_UNRESOLVED = "genre_chain_unresolved"
    ENRICHMENT_CRITICAL_FIELD = "enrichment_critical_field"
    SCHOLAR_CONFLICT = "scholar_conflict"
    AUTHOR_SCIENCE_MISMATCH = "author_science_mismatch"


# ──────────────────────────────────────────────────────────────────
# Sub-models
# ──────────────────────────────────────────────────────────────────

class ScholarReference(BaseModel):
    """Reference to a scholar in the scholar authority registry (SPEC §4.A.5).

    confidence = registry match score (1.0 for new records, match_score for
    auto-linked records). This is NOT the LLM identification confidence.
    Downstream engines must use SourceMetadata.confidence_scores.author for
    the LLM identification confidence (capped per D-027).
    """
    canonical_id: str = Field(description="sch_{5_digit_sequence}, e.g. sch_00042")
    name_arabic: str = Field(description="Primary Arabic name as found in the source")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Registry match confidence (1.0 for new records). "
                    "NOT LLM identification confidence — use confidence_scores.author for that."
    )
    source_of_identification: str = Field(
        description="How identified: 'extracted', 'inferred', 'owner_provided', 'consensus'"
    )


class TextLayer(BaseModel):
    """A text layer in a multi-layer source (SPEC §4.A.4, D-030).

    layer_type values match the normalization engine's LayerType enum to ensure
    cross-boundary compatibility (see STEP1_HARDENING.md defect D-H02).
    """
    layer_type: Literal["matn", "sharh", "hashiyah", "tahqiq_note"] = Field(
        description="One of: matn, sharh, hashiyah, tahqiq_note"
    )
    author: ScholarReference = Field(description="Author of this specific layer")


class GenreChain(BaseModel):
    """Work-to-work genre relationship discovered at intake (SPEC §4.A.4, §4.A.9)."""
    relation_type: GenreRelationType
    base_work_title: str = Field(description="Arabic title of the base work")
    base_work_author: str = Field(description="Arabic name of the base work's author")
    base_work_id: Optional[str] = Field(
        None, description="work_id if base work is in library; null if placeholder needed"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in relationship")


class WorkRelationshipEdge(BaseModel):
    """An edge in the work relationship graph (SPEC §4.A.9).

    Stored in work registry. Directed: from_work_id relates to to_work_id.
    """
    from_work_id: str
    to_work_id: str
    relation_type: GenreRelationType
    confidence: float = Field(ge=0.0, le=1.0)
    discovered_by: str = Field(description="'source_engine' or 'excerpting_engine'")


class TrustworthinessFactor(BaseModel):
    """Individual trust evaluation factor (SPEC §4.A.8).

    Five defined factors with weights:
    - author_standing (0.30)
    - tahqiq_quality (0.25)
    - publisher_reputation (0.15)
    - source_authority (0.15)
    - text_fidelity (0.15)
    """
    name: str = Field(description="Factor name from the five defined factors")
    weight: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=0.0, le=1.0)
    reason: str = Field(description="Why this score was assigned")


class MetadataHistoryEntry(BaseModel):
    """Record of a metadata field change (SPEC §3, enrichment invariant #4)."""
    field: str
    old_value: Optional[str] = None
    new_value: str
    changed_by: str = Field(description="Engine or component that made the change")
    timestamp: str = Field(description="ISO 8601 timestamp")


class VolumeInfo(BaseModel):
    """Volume mapping for multi-volume works (SPEC §4.A.1)."""
    volume_number: int
    file_path: str = Field(description="Path relative to frozen directory")
    page_range: Optional[str] = Field(None, description="e.g. '1-350'")


class InferredFieldConfidence(BaseModel):
    """Confidence scores for all LLM-inferred fields (SPEC §4.A.4).

    Fields with confidence < 0.70 → needs_review.
    Fields with confidence < 0.50 → block metadata write (§5 Layer 1).
    Single-LLM biographical inference capped at 0.85 (§6).
    """
    genre: float = Field(ge=0.0, le=1.0)
    science_scope: float = Field(ge=0.0, le=1.0)
    level: Optional[float] = Field(None, ge=0.0, le=1.0)
    structural_format: float = Field(ge=0.0, le=1.0)
    authority_level: float = Field(ge=0.0, le=1.0)
    multi_layer: Optional[float] = Field(None, ge=0.0, le=1.0)
    genre_chain: Optional[float] = Field(None, ge=0.0, le=1.0)
    author: Optional[float] = Field(None, ge=0.0, le=1.0, description="LLM author identification confidence, post-caps")


class ScholarlyContext(BaseModel):
    """LLM-inferred scholarly background for a source (SPEC §4.A.4).

    Contains narrative context about this work and edition that is not
    available from any other field in the pipeline. Author-level context
    (school affiliations, standing, death dates, methodology) lives in
    ScholarAuthorityRecord. Source-level classification (genre, format,
    trust, fidelity) lives in SourceMetadata's main fields.

    This model stores ONLY genuinely new LLM-inferred context that
    enables the synthesis engine to build richer analytical narratives.
    Every field here has a traced and verified downstream consumer
    (verified by downstream contract audit, 2026-03-09):

    - composition_date_hijri → synthesis §4.A.3 Step 4 (intra-author retraction detection)
    - composition_period → synthesis §4.A.3 Step 4 (intra-author contradiction narrative)
    - tradition_position → synthesis §4.A.4.2 (analytical layer authority weighting)
    - known_textual_issues → synthesis §4.A.4.2 (analytical layer quality caveats)
    - historical_significance → synthesis §4.A.4.2 (analytical layer framing)
    - muhaqiq_reputation → trust evaluation context + synthesis §4.A.4.2 (citation quality notes)
    - tahqiq_methodology_note → trust evaluation + synthesis §4.A.4.2 (citation quality notes)
    - edition_known_issues → synthesis §4.A.4.2 (analytical layer quality caveats)
    - context_richness → synthesis §4.A.2 (scholarly context reliance gating)
    - uncertain_dimensions → synthesis §4.A.2 + §4.A.4.2 (field-level veto list)

    Optional on SourceMetadata — null means the context inference call
    failed or was skipped. All downstream engines handle null gracefully
    by falling back to registry-only data with no narrative enrichment.
    """

    # ── Work-level context ──
    composition_period: Optional[str] = Field(
        None,
        description="Whether this is an early, middle, or late work of the author, "
                    "and what that implies. E.g. 'Late comprehensive synthesis, "
                    "reflecting the author's mature methodology' or 'Early work, "
                    "may not represent final positions'. Used by synthesis engine "
                    "for intra-author contradiction resolution (§4.A.3 Step 4)."
    )
    composition_date_hijri: Optional[int] = Field(
        None,
        description="Approximate hijri year the work was composed, when the LLM "
                    "has knowledge of this. E.g. 670 for a work known to have "
                    "been written around 670 AH. Used by synthesis engine for "
                    "intra-author retraction detection (§4.A.3 Step 4) — when "
                    "an author's positions differ between two works, the later "
                    "work may supersede the earlier. Null when the composition "
                    "date is unknown (the common case for classical works). When "
                    "null, synthesis falls back to composition_period (narrative "
                    "proxy) or author death dates (rough proxy)."
    )
    tradition_position: Optional[str] = Field(
        None,
        description="The work's role in its scholarly tradition. E.g. 'Standard "
                    "matn in the Shafi'i nahw curriculum for over 700 years' or "
                    "'Marginal work, rarely cited outside specialist circles'. "
                    "Encompasses reception history. Used by synthesis for authority "
                    "weighting beyond the authority_level enum."
    )
    known_textual_issues: list[str] = Field(
        default_factory=list,
        description="Specific, documented problems with the work's textual "
                    "transmission. E.g. 'Popular editions omit the final chapter "
                    "on al-waqf', 'Contains interpolations not in the oldest "
                    "manuscripts'. Only populated when the LLM has concrete "
                    "knowledge — empty list is correct and preferred when uncertain."
    )
    historical_significance: Optional[str] = Field(
        None,
        description="What makes this work notable in its tradition — historical "
                    "importance, known controversies, composition context, the "
                    "work's position in its scholarly lineage. Absorbs the former "
                    "work_notes concept. E.g. 'The most widely taught sharh of "
                    "the Alfiyyah, generating more commentaries than any other "
                    "grammar text.' Null when unremarkable."
    )

    # ── Edition-level context ──
    muhaqiq_reputation: Optional[str] = Field(
        None,
        description="One-sentence characterization of the tahqiq editor's "
                    "reputation. Absorbs the former muhaqiq_reputation_note. "
                    "E.g. 'Abd al-Salam Harun's editions are widely considered "
                    "among the finest in Arabic linguistics.' Null when the "
                    "muhaqiq is unrecognized or absent."
    )
    tahqiq_methodology_note: Optional[str] = Field(
        None,
        description="How the tahqiq was performed, when known. E.g. 'Based on "
                    "7 manuscripts including the author's autograph' or "
                    "'Commercial reprint with no critical apparatus'. Used by "
                    "trust evaluation and synthesis quality caveats."
    )
    edition_known_issues: list[str] = Field(
        default_factory=list,
        description="Specific problems with THIS edition (not the work's textual "
                    "tradition). E.g. 'Missing footnotes in volumes 3-4', 'Known "
                    "printing errors in the first edition'. Only populated when "
                    "the LLM has concrete knowledge."
    )

    # ── Quality signal ──
    context_richness: Literal["rich", "partial", "minimal"] = Field(
        "minimal",
        description="LLM self-assessment of its knowledge about this work/edition. "
                    "'rich' = strong knowledge, most fields populated with substance. "
                    "'partial' = some knowledge, key fields populated but gaps exist. "
                    "'minimal' = little knowledge, mostly nulls. Synthesis engine uses "
                    "this to decide how heavily to lean on scholarly context."
    )
    uncertain_dimensions: list[str] = Field(
        default_factory=list,
        description="Names of specific fields the LLM flagged as uncertain. "
                    "E.g. ['composition_period', 'known_textual_issues']. Synthesis "
                    "engine checks this before using specific context fields in claims."
    )


# ──────────────────────────────────────────────────────────────────
# §4.B Transformative Capability Output Models
# ──────────────────────────────────────────────────────────────────

class TextReuseEntry(BaseModel):
    """A single text-reuse relationship from KITAB data (SPEC §4.B.5)."""
    work: str = Field(description="OpenITI URI, e.g. '0676Nawawi.MajmucSharh'")
    shared_words: int = Field(ge=0)
    pct_of_target: float = Field(ge=0.0, le=1.0)


class IntertextualMetrics(BaseModel):
    """Aggregated text-reuse metrics from KITAB (SPEC §4.B.5)."""
    reuse_as_source_count: int = Field(ge=0)
    reuse_as_source_top_5: list[TextReuseEntry]
    reuse_from_source_count: int = Field(ge=0)
    reuse_from_source_top_5: list[TextReuseEntry]
    originality_estimate: float = Field(ge=0.0, le=1.0)
    network_centrality_rank: int = Field(ge=1)


class CompositionalProfile(BaseModel):
    """KITAB text reuse profile (SPEC §4.B.5). [NOT YET IMPLEMENTED]"""
    kitab_uri_match: str
    kitab_match_confidence: float = Field(ge=0.0, le=1.0)
    intertextual_metrics: IntertextualMetrics


class EditionDivergence(BaseModel):
    """A single divergence region between two editions (SPEC §4.B.6)."""
    location: dict = Field(description="{'volume': int, 'page_approx': int}")
    edition_a_text: str
    edition_b_text: str
    divergence_type: str = Field(
        description="tahqiq_correction | variant_reading | ocr_artifact | "
                    "editorial_addition | structural_difference"
    )
    analysis: str


class EditionComparisonSummary(BaseModel):
    """Summary statistics for edition comparison (SPEC §4.B.6)."""
    total_divergence_regions: int = Field(ge=0)
    by_type: dict[str, int]
    preferred_edition_recommendation: Optional[str] = Field(
        None, description="Null when comparison is inconclusive (< 20% alignment)"
    )
    preference_reason: str


class EditionComparison(BaseModel):
    """Full edition comparison record (SPEC §4.B.6). [NOT YET IMPLEMENTED]

    Written to: library/sources/{work_id}/edition_comparison.json
    """
    work_id: str
    editions_compared: list[str] = Field(min_length=2)
    comparison_timestamp: str
    summary: EditionComparisonSummary
    sample_divergences: list[EditionDivergence]


class GenealogyMetadata(BaseModel):
    """Scholarly genealogy record (SPEC §4.B.7). [NOT YET IMPLEMENTED]

    Stored within ScholarAuthorityRecord.genealogy_metadata.
    """
    canonical_id: str
    genealogy_chain_upward: list[str] = Field(description="Teacher canonical_ids by generation")
    genealogy_chain_upward_names: list[str] = Field(description="Arabic names matching above")
    chain_confidence: float = Field(ge=0.0, le=1.0)
    chain_sources: list[str]
    link_provenance: dict[str, str] = Field(
        default_factory=dict,
        description="Maps each teacher/student canonical_id to provenance: "
                    "'llm_only' (max conf 0.70), 'openiti_corroborated', "
                    "'wikidata_corroborated', 'source_text', 'multi_source' (conf up to 0.95)"
    )
    scholarly_generation: int = Field(ge=1)
    genealogy_community: str
    centrality_score: float = Field(ge=0.0, le=1.0)
    bridges_to_communities: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Scholar Authority Model (SPEC §4.A.5)
# ──────────────────────────────────────────────────────────────────

class ScholarAuthorityRecord(BaseModel):
    """Full scholar record in the scholar authority registry (SPEC §4.A.5).

    Written to: library/registries/scholars.json (keyed by canonical_id).
    Created by the source engine, enriched by downstream engines.
    33 defined fields — record_completeness tracks fill rate.

    Consistency checks on update (§4.A.5):
    1. Death date drift > 5 years → SRC_SCHOLAR_DATE_CONFLICT
    2. School affiliation change → SRC_SCHOLAR_SCHOOL_CONFLICT
    3. canonical_name_ar change → blocked (add to known_as instead)
    4. Teacher/student self-reference → rejected
    5. Teacher death > student death + 30yr → SRC_SCHOLAR_TEMPORAL_INCONSISTENCY
    """
    canonical_id: str = Field(description="sch_{5_digit_sequence}")
    canonical_name_ar: str = Field(description="Full Arabic name — immutable after creation")
    known_as: list[str] = Field(default_factory=list)
    name_variants: list[str] = Field(default_factory=list)
    kunya: Optional[str] = None
    laqab: list[str] = Field(default_factory=list)
    nisba: list[str] = Field(default_factory=list)
    birth_date_hijri: Optional[int] = None
    birth_date_ce: Optional[int] = None
    death_date_hijri: Optional[int] = None
    death_date_ce: Optional[int] = None
    death_date_approximate: bool = False
    death_date_source: Optional[Literal["extraction", "author_raw_text", "inference", "absent"]] = Field(
        None,
        description="Provenance of death_date_hijri: 'extraction' (from structured fields), "
                    "'author_raw_text' (parsed from author name string), "
                    "'inference' (LLM training knowledge), 'absent' (no date available)"
    )
    era_century_hijri: Optional[int] = None
    geographic_origin: Optional[str] = None
    geographic_active: list[str] = Field(default_factory=list)
    school_affiliations: dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Science → school, e.g. {'nahw': 'بصري', 'fiqh': 'حنبلي'}"
    )
    sectarian_tradition: Optional[str] = Field(
        None,
        description="Broad sectarian frame: 'sunni', 'twelver_shii', 'zaydi', "
                    "'ibadi', etc. Prevents silent mixing of traditions from "
                    "different sectarian contexts in synthesis. Default for the "
                    "owner's collection is 'sunni' — only deviate when there is "
                    "positive evidence of a different tradition."
    )
    teachers: list[str] = Field(default_factory=list, description="List of canonical_ids")
    students: list[str] = Field(default_factory=list, description="List of canonical_ids")
    known_works: list[str] = Field(default_factory=list, description="List of work_ids")
    scholarly_standing: Optional[str] = None
    methodology_notes: Optional[str] = None
    methodological_stance: Optional[str] = Field(
        None,
        description="Interpretive characterization of the scholar's approach. "
                    "E.g. 'Tends toward strictness (tashaddud) in hadith grading', "
                    "'Known for reconciling (tawfiq) between seemingly contradictory "
                    "positions'. Used by synthesis for authority weighting when "
                    "evaluating positions from this scholar."
    )
    disambiguation_notes: Optional[str] = None
    sources_encountered_in: list[str] = Field(default_factory=list)
    record_completeness: float = Field(0.0, ge=0.0, le=1.0)
    data_provenance_score: float = Field(
        0.0, ge=0.0, le=1.0,
        description="Fraction of non-null biographical fields corroborated by ≥1 non-LLM source. "
                    "< 0.30 → low_provenance flag. Recomputed on every update (§5 Layer 1)."
    )
    record_sources: list[str] = Field(default_factory=list)
    revision_history: list[MetadataHistoryEntry] = Field(default_factory=list)
    last_updated: str = Field(description="ISO 8601 timestamp")
    genealogy_metadata: Optional[GenealogyMetadata] = Field(
        None, description="§4.B.7 scholarly genealogy. [NOT YET IMPLEMENTED]"
    )
    cross_validation: Optional[CrossValidationResult] = Field(
        None, description="§4.B.8 cross-validated authority bootstrapping. [NOT YET IMPLEMENTED]"
    )


# ──────────────────────────────────────────────────────────────────
# Registry Models
# ──────────────────────────────────────────────────────────────────

class WorkRegistryEntry(BaseModel):
    """A work record in the work registry (SPEC §3, §4.A.1).

    Written to: library/registries/works.json (keyed by work_id).
    """
    work_id: str = Field(description="wrk_{author_slug}_{title_slug}")
    canonical_title: str = Field(description="Canonical Arabic title")
    canonical_title_transliterated: Optional[str] = None
    author_canonical_id: str
    genre: Optional[Genre] = None
    science_scope: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    preferred_source_id: Optional[str] = None
    relationships: list[WorkRelationshipEdge] = Field(default_factory=list)
    status: str = Field(description="active | referenced_not_acquired")
    citation_count: int = Field(0, description="§4.B.3 citation tracking")
    volumes_present: list[int] = Field(default_factory=list)
    volumes_missing: list[int] = Field(default_factory=list)


class SourceRegistryEntry(BaseModel):
    """A source record in the source registry (SPEC §3).

    Written to: library/registries/sources.json (keyed by source_id).
    """
    source_id: str
    work_id: str
    human_label: str
    title_arabic: str
    author_canonical_id: str
    trust_tier: TrustTier
    processing_status: ProcessingStatus
    frozen_hash: str
    intake_timestamp: str
    acquisition_path: AcquisitionPath
    error_detail: Optional[str] = None


# ──────────────────────────────────────────────────────────────────
# Primary Output: Source Metadata Record
# ──────────────────────────────────────────────────────────────────

class SourceMetadata(BaseModel):
    """The complete source metadata record (SPEC §3, §4.A.4).

    Written to: library/sources/{source_id}/metadata.json
    This is the ORIGIN of the metadata chain that flows through the entire pipeline.

    Validation (§5 Layer 1) checks before every write:
    1. Schema compliance (this model)
    2. Referential integrity (author.canonical_id → scholars.json, work_id → works.json)
    3. Confidence threshold (critical fields < 0.50 block write)
    4. Duplicate re-check
    5. Consistency cross-check (genre vs structural_format, level vs genre)
    """

    # ── Identity (SPEC §4.A.1) ──
    source_id: str = Field(description="Permanent: src_{8_char_hash}")
    work_id: str = Field(description="Work grouping: wrk_{author_slug}_{title_slug}")
    human_label: str = Field(description="Human-readable shorthand, not a primary key")

    # ── Bibliographic (SPEC §4.A.3, §4.A.4) ──
    title_arabic: str
    title_transliterated: Optional[str] = None
    author: ScholarReference
    attribution_status: AttributionStatus = Field(
        default=AttributionStatus.TRADITIONAL,
        description="How secure the authorship attribution is. 'traditional' is the "
                    "safe default for classical works. When 'disputed', author.confidence "
                    "is capped at 0.70. When 'unknown', author.confidence is set to 0.0."
    )
    attribution_notes: Optional[str] = Field(
        None,
        description="Description of the attribution dispute. Required when "
                    "attribution_status is 'disputed'. Null otherwise."
    )
    muhaqiq: Optional[ScholarReference] = Field(
        None, description="Tahqiq editor — also a scholar in the authority registry"
    )
    additional_authors: list[ScholarReference] = Field(default_factory=list)
    science_scope: list[str] = Field(description="e.g. ['fiqh', 'usul_al_fiqh']")
    genre: Genre
    genre_chain: Optional[GenreChain] = None
    level: Optional[WorkLevel] = None
    publisher: Optional[str] = None
    edition_number: Optional[int] = None
    publication_year_hijri: Optional[int] = None
    publication_year_miladi: Optional[int] = None

    # ── Source characteristics (SPEC §4.A.4) ──
    source_format: SourceFormat
    authority_level: AuthorityLevel
    structural_format: StructuralFormat
    language: str = Field(default="ar")
    page_count: Optional[int] = None

    # ── Multi-layer (SPEC §4.A.4, D-030) ──
    is_multi_layer: bool = Field(default=False)
    text_layers: list[TextLayer] = Field(default_factory=list)

    # ── Trust and quality (SPEC §4.A.8) ──
    trust_tier: TrustTier
    trust_score: float = Field(ge=0.0, le=1.0)
    trust_factors: list[TrustworthinessFactor]
    trust_reason: str
    text_fidelity: TextFidelity
    text_fidelity_reason: str

    # ── Confidence tracking (SPEC §4.A.4, §5) ──
    confidence_scores: InferredFieldConfidence
    needs_review_fields: list[str] = Field(
        default_factory=list, description="Fields with confidence < 0.70"
    )

    # ── Volumes (SPEC §4.A.1) ──
    volume_count: Optional[int] = None
    volumes: list[VolumeInfo] = Field(default_factory=list)
    volumes_missing: list[int] = Field(default_factory=list)

    # ── Frozen source (SPEC §3, §4.A.2 Step 6) ──
    frozen_path: str = Field(description="library/sources/{source_id}/frozen/")
    frozen_hash: str = Field(description="SHA-256 composite hash")
    frozen_file_hashes: dict[str, str] = Field(description="Filename → SHA-256")

    # ── Format-specific (SPEC §4.A.3) ──
    format_specific_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="e.g. shamela_book_id, shamela_category for Shamela sources"
    )

    # ── Scholarly context (SPEC §4.A.4) ──
    scholarly_context: Optional[ScholarlyContext] = Field(
        None,
        description="LLM-inferred scholarly background about this work and edition. "
                    "Null when context inference was skipped or failed. Downstream "
                    "engines fall back to registry-only data when null. Contains "
                    "only genuinely new context not available elsewhere in the "
                    "pipeline — author-level context lives in ScholarAuthorityRecord."
    )

    # ── Work relationships (SPEC §4.A.9) ──
    work_relationships: list[GenreChain] = Field(default_factory=list)

    # ── Processing state (SPEC §4.A.10) ──
    status: ProcessingStatus
    intake_timestamp: str
    acquisition_path: AcquisitionPath

    # ── Progressive enrichment (SPEC §3) ──
    metadata_history: list[MetadataHistoryEntry] = Field(default_factory=list)
    enrichment_sources: list[str] = Field(default_factory=list)
    enrichment_tracking: Optional[dict[str, Any]] = Field(
        None,
        description="Per-field enrichment generation counters for cycle detection "
                    "(SPEC §2.2, invariant #8). Persisted between sessions. "
                    "Structure: {field_name: {'changed_by': str, 'timestamp': str, "
                    "'generation': int}}. Entries expire after enrichment_cycle_timeout seconds."
    )

    # ── Owner-authored specific (SPEC §2) ──
    owner_authored_type: Optional[OwnerAuthoredType] = None

    # ── §4.B Transformative capability outputs ──
    compositional_profile: Optional[CompositionalProfile] = Field(
        None, description="KITAB text reuse (§4.B.5). [NOT YET IMPLEMENTED]"
    )
    difficulty_prediction: Optional[DifficultyPrediction] = Field(
        None, description="Pipeline difficulty prediction (§4.B.9). [NOT YET IMPLEMENTED]"
    )
    tahqiq_fingerprint: Optional[TahqiqFingerprint] = Field(
        None, description="Tahqiq apparatus quality analysis (§4.B.10). [NOT YET IMPLEMENTED]"
    )


# ──────────────────────────────────────────────────────────────────
# Workflow Models (not persisted as primary artifacts)
# ──────────────────────────────────────────────────────────────────

class EnrichmentRequest(BaseModel):
    """Enrichment write-back from a downstream engine (SPEC §2).

    Validated against the 9 enrichment invariants before applying.
    For critical field updates (author, work_id, genre, science_scope),
    verification_context is required (invariant #9).
    """
    source_id: str
    updates: dict[str, Any] = Field(description="Field name → new value")
    requesting_engine: str
    timestamp: str
    reason: Optional[str] = None
    verification_context: Optional[dict[str, str]] = Field(
        None,
        description="Required for critical field updates. Must contain "
                    "'expected_work_id' and 'expected_author_canonical_id' "
                    "matching the actual source metadata."
    )


class HumanGateCheckpoint(BaseModel):
    """A pending human review item (SPEC §5, Layer 2).

    Multiple checkpoints per source are batched for owner review.
    """
    checkpoint_id: str
    source_id: str
    trigger: HumanGateTrigger
    trigger_detail: str
    fields_to_review: list[str]
    current_values: dict[str, Any]
    alternatives: Optional[list[dict[str, Any]]] = None
    created_at: str
    status: str = Field(
        default="pending",
        description="pending|approved|rejected|elevated|auto_approved"
    )
    resolution: Optional[str] = None
    resolved_at: Optional[str] = None
    elevated_result: Optional[dict[str, Any]] = None


class SourceError(BaseModel):
    """Structured error record (SPEC §7).

    Logged to library/logs/source_engine.jsonl.
    """
    timestamp: str
    source_id: Optional[str] = None
    error_code: ErrorCode
    severity: ErrorSeverity
    message: str
    recovery_action: Literal[
        "rejected", "human_gate_created", "field_flagged", "skipped", "retry_scheduled"
    ] = Field(description="Recovery action taken for this error (SPEC §7)")
    context: Optional[dict[str, Any]] = None


class RegistryPendingWrite(BaseModel):
    """Write-ahead log for atomic registry updates (SPEC §4.A.2 Step 7).

    Written to library/logs/pending_registration_{source_id}.json.
    Deleted after successful completion. Orphans indicate interrupted registrations.
    """
    source_id: str
    timestamp: str
    intended_changes: dict[str, Any] = Field(description="Registry file → changes")
    completed_files: list[str] = Field(default_factory=list)


class CitationDiscoveryRequest(BaseModel):
    """Request from excerpting engine (SPEC §4.B.3). [NOT YET IMPLEMENTED]"""
    referenced_author: str
    referenced_title: str
    citing_excerpt_id: str
    citing_source_id: str
    citing_work_id: str
    context_text: Optional[str] = None


class RelevanceEvaluation(BaseModel):
    """Result of autonomous discovery relevance check (SPEC §4.A.6)."""
    candidate_title: str
    candidate_author: Optional[str]
    repository: str
    classification: str = Field(description="relevant | partially_relevant | not_relevant")
    reason: str
    gap_fill_match: Optional[bool] = None


class GapAnalysisItem(BaseModel):
    """Single item in acquisition gap analysis (SPEC §4.B.4). [NOT YET IMPLEMENTED]"""
    priority_rank: int = Field(ge=1)
    gap_type: str = Field(
        description="citation_priority | school_coverage | curricular_gap | author_completeness"
    )
    description: str
    recommended_work: Optional[str] = None
    recommended_author: Optional[str] = None
    source_of_recommendation: str


# --- §4.B.8: Cross-Validated Scholar Authority Bootstrapping ---

class DeathDateAgreement(BaseModel):
    """Cross-validation result for scholar death date across multiple sources."""
    openiti: Optional[int] = None
    usul_data: Optional[int] = None
    wikidata: Optional[int] = None
    status: str = Field(description="unanimous | majority | disagreement | insufficient_data")
    confidence_boost: float = Field(ge=0.0, le=0.15, default=0.0)


class KnownWorksUnion(BaseModel):
    """Union of known works across enrichment sources."""
    openiti_only: List[str] = Field(default_factory=list)
    usul_data_only: List[str] = Field(default_factory=list)
    wikidata_only: List[str] = Field(default_factory=list)
    all_three: List[str] = Field(default_factory=list)
    total_unique_works: int = Field(ge=0)


class WikidataTeacherStudentLinks(BaseModel):
    """Teacher-student links discovered from Wikidata."""
    teachers_from_wikidata: List[str] = Field(default_factory=list)
    students_from_wikidata: List[str] = Field(default_factory=list)
    novel_links: int = Field(ge=0, description="Links not found in OpenITI or LLM inference")


class CrossValidationDiscrepancy(BaseModel):
    """A discrepancy found during cross-validation."""
    field: str
    openiti_value: Optional[str] = None
    usul_data_value: Optional[str] = None
    wikidata_value: Optional[str] = None
    resolution: str = Field(description="majority | human_gate | pending")


class CrossValidationResult(BaseModel):
    """Cross-validation results for scholar authority bootstrapping (SPEC §4.B.8). [NOT YET IMPLEMENTED]"""
    death_date_agreement: DeathDateAgreement
    known_works_union: KnownWorksUnion
    teacher_student_wikidata: WikidataTeacherStudentLinks
    discrepancies: List[CrossValidationDiscrepancy] = Field(default_factory=list)


# --- §4.B.9: Source Difficulty Prediction ---

class DifficultySignal(BaseModel):
    """A single signal contributing to difficulty prediction."""
    score: float = Field(ge=0.0, le=1.0)
    reason: str


class DifficultyPrediction(BaseModel):
    """Source difficulty prediction computed before pipeline processing (SPEC §4.B.9). [NOT YET IMPLEMENTED]"""
    overall_score: float = Field(ge=0.0, le=1.0)
    difficulty_tier: str = Field(description="easy | moderate | hard | very_hard")
    signals: Dict[str, DifficultySignal] = Field(
        description="Keys: format_complexity, genre_processing_depth, multi_layer_complexity, "
                    "science_scope_breadth, text_fidelity, source_size, author_disambiguation"
    )
    expected_human_gates: int = Field(ge=0)
    expected_processing_hours: Optional[float] = None
    priority_recommendation: str = Field(description="critical | high | medium | low")
    priority_reason: str


# --- §4.B.10: Tahqiq Apparatus Fingerprinting ---

class TahqiqFingerprint(BaseModel):
    """Tahqiq apparatus quality analysis (SPEC §4.B.10). [NOT YET IMPLEMENTED]"""
    apparatus_present: bool
    manuscript_reference_density: float = Field(
        ge=0.0, description="Count of manuscript references per 1000 footnote words"
    )
    variant_reading_density: float = Field(
        ge=0.0, description="Count of variant reading notations per 1000 footnote words"
    )
    hadith_takhrij_present: bool = False
    footnote_entropy: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Shannon entropy of footnote word unigrams, normalized to 0-1"
    )
    formulaic_ratio: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Proportion of footnotes detected as formulaic/repetitive"
    )
    muhaqiq_reputation: str = Field(
        description="recognized | unknown | watchlisted"
    )
    tahqiq_quality_classification: str = Field(
        description="genuine_critical | scholarly_reprint | commercial_reprint | "
                    "claimed_but_absent | insufficient_data"
    )
    classification_confidence: float = Field(ge=0.0, le=1.0)
    classification_evidence: str
