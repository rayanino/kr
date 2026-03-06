"""Source Engine Contracts — Machine-readable schemas derived from SPEC.md §2-§3.

These Pydantic models are the AUTHORITATIVE data contracts for the source engine.
They serve three purposes:
1. Implementation reference — Claude Code uses these to build the engine
2. Runtime validation — every output is validated against these before writing to disk
3. Test generation — tests use these to create valid/invalid test data

SPEC.md remains the behavioral authority (HOW to process). These models define
WHAT the data looks like at each boundary.

When SPEC.md §2/§3 and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

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
    WORD_DOC = "word_doc"       # .doc/.docx files (e.g., mughni_comparative fixture)
    OWNER_AUTHORED = "owner_authored"

class OwnerAuthoredType(str, Enum):
    """Types of owner-authored content (SPEC §2)."""
    STUDY_NOTE = "study_note"
    TARJIH = "tarjih"
    RESEARCH_DRAFT = "research_draft"
    LESSON_TRANSCRIPTION = "lesson_transcription"
    OBSERVATION = "observation"

class TrustTier(str, Enum):
    """Source trustworthiness tiers (SPEC §4.A.8)."""
    VERIFIED = "verified"     # Combined score >= 0.65, no critical factor at 0.0
    FLAGGED = "flagged"       # Combined score < 0.65 OR any critical factor at 0.0

class AuthorityLevel(str, Enum):
    """Source authority level (SPEC §4.A.4)."""
    PRIMARY = "primary"                    # مصادر أصلية — original scholarly works
    REFERENCE = "reference"                # مراجع — secondary reference works
    MODERN_COMPILATION = "modern_compilation"  # معاصر — modern compilations/textbooks

class StructuralFormat(str, Enum):
    """Structural format of the source text (SPEC §4.A.4)."""
    PROSE = "prose"
    QA = "qa"                 # Question-and-answer format
    VERSIFIED = "versified"   # منظومات — poetry/verse format
    TABULAR = "tabular"
    DICTIONARY = "dictionary"
    COMMENTARY = "commentary" # Multi-layer text (sharh, hashiyah)

class GenreRelationType(str, Enum):
    """Types of work-to-work relationships (SPEC §4.A.9)."""
    SHARH = "sharh"           # Commentary on base work
    HASHIYAH = "hashiyah"     # Supercommentary on a sharh
    MUKHTASAR = "mukhtasar"   # Abridgment of a larger work
    NAZM = "nazm"             # Versification of a prose work
    TAKHREEJ = "takhreej"     # Hadith verification/tracing
    TAQRIRAT = "taqrirat"     # Lecture notes on a work
    RESPONDS_TO = "responds_to"  # Written in response to or refutation of
    CITES = "cites"           # References another work (discovered during processing)

class WorkLevel(str, Enum):
    """Scholarly level of a work (SPEC §4.A.4)."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SPECIALIST = "specialist"


# ──────────────────────────────────────────────────────────────────
# Sub-models
# ──────────────────────────────────────────────────────────────────

class ScholarReference(BaseModel):
    """Reference to a scholar in the scholar authority registry (SPEC §4.A.5)."""
    canonical_id: str = Field(description="sch_{5_digit_sequence}, e.g. sch_00042")
    name_arabic: str = Field(description="Primary Arabic name as found in the source")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in identification")
    source_of_identification: str = Field(description="How identified: 'extracted', 'inferred', 'owner_provided'")

class TextLayer(BaseModel):
    """A text layer in a multi-layer source (SPEC §4.A.4, D-030)."""
    layer_type: str = Field(description="One of: matn, sharh, hashiyah, tahqiq")
    author: ScholarReference = Field(description="Author of this specific layer")

class GenreChain(BaseModel):
    """Work-to-work relationship (SPEC §4.A.4, §4.A.9)."""
    relation_type: GenreRelationType
    base_work_title: str = Field(description="Arabic title of the base work")
    base_work_author: str = Field(description="Arabic name of the base work's author")
    base_work_id: Optional[str] = Field(None, description="work_id if the base work is in the library")

class TrustworthinessFactor(BaseModel):
    """Individual trust evaluation factor (SPEC §4.A.8)."""
    name: str = Field(description="Factor name: author_verified, muhaqiq_present, publisher_known, edition_indicator, text_completeness")
    weight: float = Field(description="Factor weight in combined score")
    score: float = Field(ge=0.0, le=1.0)
    reason: str = Field(description="Why this score was assigned")

class MetadataHistoryEntry(BaseModel):
    """Record of a metadata field change (SPEC §3)."""
    field: str
    old_value: Optional[str] = None
    new_value: str
    changed_by: str = Field(description="Engine or component that made the change")
    timestamp: str = Field(description="ISO 8601 timestamp")


class ScholarAuthorityRecord(BaseModel):
    """Full scholar record in the scholar authority registry (SPEC §4.A.5).

    Written to: library/registries/scholars.json (keyed by canonical_id).
    Created by the source engine, enriched by downstream engines.
    """
    canonical_id: str = Field(description="sch_{5_digit_sequence}, e.g. sch_00042")
    canonical_name_ar: str = Field(description="Full Arabic name")
    known_as: list[str] = Field(default_factory=list, description="Common short names, e.g. ['سيبويه']")
    name_variants: list[str] = Field(default_factory=list, description="All known name forms")
    kunya: Optional[str] = None
    laqab: list[str] = Field(default_factory=list)
    nisba: list[str] = Field(default_factory=list)
    birth_date_hijri: Optional[int] = None
    birth_date_ce: Optional[int] = None
    death_date_hijri: Optional[int] = None
    death_date_ce: Optional[int] = None
    death_date_approximate: bool = False
    era_century_hijri: Optional[int] = None
    geographic_origin: Optional[str] = None
    geographic_active: list[str] = Field(default_factory=list)
    school_affiliations: dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Science → school mapping, e.g. {'nahw': 'بصري', 'fiqh': 'حنبلي'}"
    )
    teachers: list[str] = Field(default_factory=list, description="List of canonical_ids")
    students: list[str] = Field(default_factory=list, description="List of canonical_ids")
    known_works: list[str] = Field(default_factory=list, description="List of work_ids")
    scholarly_standing: Optional[str] = Field(None, description="Brief assessment of scholarly importance")
    methodology_notes: Optional[str] = None
    disambiguation_notes: Optional[str] = Field(
        None,
        description="Notes for disambiguating this scholar from others with similar names"
    )
    sources_encountered_in: list[str] = Field(default_factory=list, description="List of source_ids")
    record_completeness: float = Field(0.0, ge=0.0, le=1.0, description="Fraction of fields filled")
    record_sources: list[str] = Field(default_factory=list, description="e.g. ['auto_inference', 'openiti_metadata', 'owner_input']")
    revision_history: list[MetadataHistoryEntry] = Field(default_factory=list)
    last_updated: str = Field(description="ISO 8601 timestamp")


class WorkRegistryEntry(BaseModel):
    """A work record in the work registry (SPEC §3, §4.A.1).

    Written to: library/registries/works.json (keyed by work_id).
    """
    work_id: str = Field(description="wrk_{author_slug}_{title_slug}")
    canonical_title: str = Field(description="Canonical Arabic title")
    author_canonical_id: str = Field(description="Reference to scholar authority registry")
    genre: Optional[str] = None
    science_scope: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list, description="All sources for this work")
    preferred_source_id: Optional[str] = Field(None, description="Owner's preferred edition")
    relationships: list[GenreChain] = Field(default_factory=list, description="Edges in the work graph")
    status: str = Field(description="active | referenced_not_acquired")
    citation_count: int = Field(0, description="Times cited by excerpts from other works")


class SourceRegistryEntry(BaseModel):
    """A source record in the source registry (SPEC §3).

    Written to: library/registries/sources.json (keyed by source_id).
    """
    source_id: str
    work_id: str
    title_arabic: str
    author_canonical_id: str
    trust_tier: TrustTier
    processing_status: str = Field(description="staging|acquired|normalizing|normalized|processing|complete|error|withdrawn")
    frozen_hash: str
    intake_timestamp: str
    acquisition_path: str = Field(description="manual | autonomous")
    error_detail: Optional[str] = None

class VolumeInfo(BaseModel):
    """Volume mapping for multi-volume works (SPEC §4.A.1)."""
    volume_number: int
    file_path: str = Field(description="Path relative to frozen directory")
    page_range: Optional[str] = Field(None, description="e.g. '1-350'")


# ──────────────────────────────────────────────────────────────────
# Primary Output: Source Metadata Record
# ──────────────────────────────────────────────────────────────────

class SourceMetadata(BaseModel):
    """The complete source metadata record (SPEC §3, §4.A.4).

    Written to: library/sources/{source_id}/metadata.json
    This is the ORIGIN of the metadata chain that flows through the entire pipeline.
    """

    # ── Identity (SPEC §4.A.1) ──
    source_id: str = Field(description="Permanent ID: src_{8_char_hash}")
    work_id: str = Field(description="Work grouping: wrk_{author_slug}_{title_slug}")
    human_label: str = Field(description="Human-readable shorthand, not a primary key")

    # ── Bibliographic (SPEC §4.A.3, §4.A.4) ──
    title_arabic: str = Field(description="Full Arabic title as extracted from source")
    title_transliterated: Optional[str] = Field(None, description="Transliterated title for search")
    author: ScholarReference = Field(description="Primary author identification")
    additional_authors: list[ScholarReference] = Field(default_factory=list, description="Co-authors, editors, etc.")
    science_scope: list[str] = Field(description="Sciences this source covers, e.g. ['fiqh', 'usul_al_fiqh']")
    genre: str = Field(description="Primary genre classification")
    genre_chain: Optional[GenreChain] = Field(None, description="If this work is a sharh/hashiyah/mukhtasar/nazm of another work")
    level: Optional[WorkLevel] = Field(None, description="Scholarly level: beginner/intermediate/advanced/specialist")

    # ── Source characteristics (SPEC §4.A.4) ──
    source_format: SourceFormat
    authority_level: AuthorityLevel
    structural_format: StructuralFormat
    language: str = Field(default="ar", description="ISO 639-1 language code")

    # ── Multi-layer (SPEC §4.A.4, D-030) ──
    is_multi_layer: bool = Field(default=False)
    text_layers: list[TextLayer] = Field(default_factory=list, description="Non-empty only if is_multi_layer=True")

    # ── Edition and trust (SPEC §4.A.8) ──
    muhaqiq: Optional[str] = Field(None, description="Tahqiq editor name (Arabic)")
    publisher: Optional[str] = Field(None, description="Publisher name")
    edition_number: Optional[int] = Field(None)
    publication_year_hijri: Optional[int] = Field(None)
    publication_year_miladi: Optional[int] = Field(None)
    trust_tier: TrustTier
    trust_score: float = Field(ge=0.0, le=1.0, description="Combined trustworthiness score")
    trust_factors: list[TrustworthinessFactor] = Field(description="Individual factor evaluations")
    trust_reason: str = Field(description="Human-readable reason for trust tier assignment")

    # ── Text quality (SPEC §4.A.4, D-026) ──
    text_fidelity: float = Field(ge=0.0, le=1.0, description="Text quality separate from scholarly trust")
    text_fidelity_reason: str

    # ── Volumes (SPEC §4.A.1) ──
    volume_count: Optional[int] = Field(None)
    volumes: list[VolumeInfo] = Field(default_factory=list)
    volumes_missing: list[int] = Field(default_factory=list, description="Known missing volume numbers")

    # ── Frozen source (SPEC §3) ──
    frozen_path: str = Field(description="library/sources/{source_id}/frozen/")
    frozen_hash: str = Field(description="SHA-256 composite hash of all frozen files")
    frozen_file_hashes: dict[str, str] = Field(description="Filename → SHA-256 hash for each file")

    # ── Work relationships (SPEC §4.A.9) ──
    work_relationships: list[GenreChain] = Field(default_factory=list, description="All known relationships to other works")

    # ── Processing state (SPEC §4.A.2) ──
    status: str = Field(description="staging|acquired|normalizing|normalized|processing|complete|error|withdrawn")
    intake_timestamp: str = Field(description="ISO 8601 timestamp of acquisition")
    acquisition_path: str = Field(description="manual | autonomous")

    # ── Progressive enrichment (SPEC §3) ──
    metadata_history: list[MetadataHistoryEntry] = Field(default_factory=list)
    enrichment_sources: list[str] = Field(default_factory=list, description="Sources of enrichment: 'openiti', 'llm_inference', 'owner_input'")

    # ── Owner-authored specific (SPEC §2) ──
    owner_authored_type: Optional[OwnerAuthoredType] = Field(None, description="Non-null only for owner-authored content")

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "src_a3f2b1c4",
                "work_id": "wrk_ibn_qudamah_mughni",
                "human_label": "mughni_ibn_qudamah",
                "title_arabic": "المغني",
                "author": {
                    "canonical_id": "sch_00042",
                    "name_arabic": "ابن قدامة المقدسي",
                    "confidence": 0.98,
                    "source_of_identification": "extracted"
                },
                "science_scope": ["fiqh"],
                "genre": "fiqh_comparative",
                "source_format": "shamela_html",
                "authority_level": "primary",
                "structural_format": "prose",
                "is_multi_layer": False,
                "trust_tier": "verified",
                "trust_score": 0.82,
                "text_fidelity": 0.95,
                "status": "acquired"
            }
        }
