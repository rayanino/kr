"""Normalization Engine Contracts — Machine-readable schemas derived from SPEC.md §2-§3.

These Pydantic models define the NORMALIZED PACKAGE — the artifact that crosses
the normalization boundary. Every Phase 2 engine consumes this schema.

The normalization boundary's test: if adding a new source type requires changing
any of these models, the boundary has been violated.

When SPEC.md §2/§3 and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────

class TextFidelityLevel(str, Enum):
    """Per-page text quality assessment (SPEC §3 content unit schema)."""
    HIGH = "high"           # Clean digital text, no OCR issues
    MEDIUM = "medium"       # Minor issues (OCR artifacts, encoding quirks)
    LOW = "low"             # Significant issues (poor OCR, damaged source)
    VERY_LOW = "very_low"   # Barely usable (heavy OCR errors, partial page)


class LayerType(str, Enum):
    """Text layer types in multi-layer compositions (SPEC §4.A.5)."""
    MATN = "matn"                   # Original author's base text
    SHARH = "sharh"                 # Commentary
    HASHIYAH = "hashiyah"           # Marginal/supercommentary
    TAHQIQ_NOTE = "tahqiq_note"     # Modern editor's notes
    UNCERTAIN = "uncertain"         # Layer could not be determined


class HeadingConfidence(str, Enum):
    """Confidence level for detected headings (SPEC §4.A.6)."""
    CONFIRMED = "confirmed"     # HTML-tagged or human-verified
    HIGH = "high"               # Strong keyword + context signals
    MEDIUM = "medium"           # Keyword match but weak context
    LOW = "low"                 # LLM-inferred or single weak signal


class HeadingDetectionMethod(str, Enum):
    """How a heading was detected (SPEC §4.A.6, structure discovery)."""
    HTML_TAGGED = "html_tagged"
    KEYWORD_HEURISTIC = "keyword_heuristic"
    LLM_DISCOVERED = "llm_discovered"
    TOC_INFERRED = "toc_inferred"
    HUMAN_OVERRIDE = "human_override"


class FootnoteType(str, Enum):
    """Footnote authorship classification (SPEC §4.A.2 Pass 2)."""
    TAHQIQ_EDITOR = "tahqiq_editor"     # Modern editor's annotation
    AUTHOR_ORIGINAL = "author_original"  # Part of original text
    UNKNOWN = "unknown_footnote_type"    # Could not determine


class StructuralFormat(str, Enum):
    """Source structural format as determined by normalization (SPEC §3).
    May differ from the source engine's initial classification.
    """
    PROSE = "prose"
    VERSE = "verse"
    QA_FORMAT = "qa_format"
    TABULAR_KHILAF = "tabular_khilaf"
    DICTIONARY = "dictionary"
    COMMENTARY = "commentary"
    MIXED = "mixed"


# ──────────────────────────────────────────────────────────────────
# Content Unit Sub-models
# ──────────────────────────────────────────────────────────────────

class PhysicalPage(BaseModel):
    """Physical page location in the source (SPEC §3 content unit schema)."""
    volume: Optional[int] = None
    page_number_display: Optional[str] = Field(
        None, description="Arabic-numeral form for citations, e.g. '٤٥'"
    )
    page_number_int: Optional[int] = None


class TextLayerSegment(BaseModel):
    """A contiguous text segment attributed to a specific layer (SPEC §4.A.5).

    In multi-layer sources, every character in primary_text is covered by
    exactly one segment. Segments are ordered by start offset.
    """
    layer_type: LayerType
    author_canonical_id: Optional[str] = Field(
        None, description="sch_XXXXX reference to scholar authority registry"
    )
    start: int = Field(description="Start character offset in primary_text (inclusive)")
    end: int = Field(description="End character offset in primary_text (exclusive)")
    confidence: float = Field(ge=0.0, le=1.0)


class Footnote(BaseModel):
    """An extracted footnote (SPEC §3 content unit schema)."""
    ref_marker: str = Field(description="Reference marker as it appears in text, e.g. '1'")
    text: str = Field(description="Footnote content")
    footnote_type: FootnoteType
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in type classification")


class StructuralMarkers(BaseModel):
    """Heading detection results for a content unit (SPEC §4.A.6)."""
    heading_detected: bool = False
    heading_text: Optional[str] = None
    heading_level: Optional[int] = Field(None, ge=1, le=10)
    heading_detection_method: Optional[HeadingDetectionMethod] = None
    heading_confidence: Optional[HeadingConfidence] = None


class VerseLineHemistich(BaseModel):
    """A hemistich (half-verse) in versified text."""
    text: str
    position: str = Field(description="'first' or 'second'")


class VerseLine(BaseModel):
    """A single verse line in versified text (SPEC §3)."""
    hemistichs: list[VerseLineHemistich]
    verse_number: Optional[int] = None


class VerseInfo(BaseModel):
    """Verse detection results for a content unit (SPEC §3)."""
    verse_lines: list[VerseLine]


class ContentFlags(BaseModel):
    """Boolean flags for content classification (SPEC §3)."""
    has_verse: bool = False
    has_table: bool = False
    has_quran_citation: bool = False
    has_hadith_citation: bool = False
    is_toc_page: bool = False
    is_index_page: bool = False
    is_blank: bool = False


class TextFidelity(BaseModel):
    """Per-page text quality assessment (SPEC §3)."""
    score: TextFidelityLevel
    ocr_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Content Unit — one per physical page
# ──────────────────────────────────────────────────────────────────

class ContentUnit(BaseModel):
    """One record in the content stream (content.jsonl).

    Each ContentUnit corresponds to one physical page of the source.
    This is the atomic unit that Phase 2 engines process.
    """
    schema_version: str = Field(default="content_unit_v2.0")
    source_id: str
    unit_index: int = Field(
        ge=0,
        description="Zero-based sequential index, globally unique within this source"
    )
    physical_page: PhysicalPage
    primary_text: str = Field(
        description="Main text content. All diacritics preserved exactly. "
        "Format-specific markup removed. Footnote refs replaced with ⌜N⌝."
    )
    text_layers: list[TextLayerSegment] = Field(
        description="Layer attribution. Every character in primary_text is covered "
        "by exactly one segment."
    )
    footnotes: list[Footnote] = Field(default_factory=list)
    structural_markers: StructuralMarkers = Field(default_factory=StructuralMarkers)
    verse_info: Optional[VerseInfo] = None
    content_flags: ContentFlags = Field(default_factory=ContentFlags)
    text_fidelity: TextFidelity


# ──────────────────────────────────────────────────────────────────
# Division Tree — structural hierarchy
# ──────────────────────────────────────────────────────────────────

class DivisionNode(BaseModel):
    """A node in the division tree (SPEC §4.A.6, manifest.division_tree).

    Represents a structural division (chapter, section, etc.) in the source.
    """
    heading_text: str
    heading_level: int = Field(ge=1, le=10)
    start_unit_index: int = Field(ge=0)
    end_unit_index: int = Field(ge=0, description="Inclusive end")
    detection_method: HeadingDetectionMethod
    confidence: HeadingConfidence
    children: list[DivisionNode] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Layer Map — multi-layer source specification
# ──────────────────────────────────────────────────────────────────

class LayerMapEntry(BaseModel):
    """One layer in the source's multi-layer composition (SPEC §3 manifest)."""
    layer_type: LayerType
    author_canonical_id: Optional[str] = Field(
        None, description="sch_XXXXX reference; null if author unknown"
    )
    author_name_arabic: Optional[str] = None
    detection_confidence: float = Field(ge=0.0, le=1.0)


# ──────────────────────────────────────────────────────────────────
# Manifest — the normalized package metadata
# ──────────────────────────────────────────────────────────────────

class TextFidelitySummary(BaseModel):
    """Aggregate text fidelity for the entire source (SPEC §3 manifest)."""
    mean_ocr_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    character_level_fidelity_estimate: Optional[float] = Field(None, ge=0.0, le=1.0)
    pages_with_warnings: int = 0
    total_pages: int = 0


class QualityReport(BaseModel):
    """Normalization quality summary (SPEC §3 manifest)."""
    divisions_discovered: int = 0
    division_confidence_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="HeadingConfidence → count, e.g. {'confirmed': 5, 'high': 12}"
    )
    layer_transitions_detected: int = 0
    pages_with_warnings: int = 0
    high_fidelity_percentage: float = Field(ge=0.0, le=1.0)


class NormalizedManifest(BaseModel):
    """The manifest.json of a normalized package (SPEC §3).

    Written to: library/sources/{source_id}/normalized/manifest.json
    """
    schema_version: str = Field(default="normalized_package_v2.0")
    source_id: str
    normalizer_id: str = Field(
        description="Which normalizer produced this, e.g. 'kr.normalization.shamela_v2'"
    )
    normalization_utc: str = Field(description="ISO 8601 timestamp")
    division_tree: list[DivisionNode] = Field(
        default_factory=list,
        description="Top-level divisions; children form the tree"
    )
    layer_map: list[LayerMapEntry] = Field(
        description="Layers present in this source. Single-layer sources have one entry."
    )
    structural_format: StructuralFormat
    text_fidelity_summary: TextFidelitySummary
    verse_detection: bool = Field(
        default=False,
        description="Whether versified text was detected"
    )
    verse_numbering_scheme: Optional[str] = Field(
        None, description="Detected numbering scheme if verses found"
    )
    total_content_units: int = Field(ge=0)
    quality_report: QualityReport
    normalization_warnings: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Full Normalized Package — convenience wrapper
# ──────────────────────────────────────────────────────────────────

class NormalizedPackage(BaseModel):
    """The complete normalized package (SPEC §3).

    This is a logical wrapper — on disk, the manifest and content stream
    are separate files (manifest.json + content.jsonl).
    """
    manifest: NormalizedManifest
    content_units: list[ContentUnit] = Field(
        description="Ordered by unit_index. One per physical page."
    )
