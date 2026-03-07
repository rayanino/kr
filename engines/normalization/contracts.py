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
    LAYOUT_DETECTED = "layout_detected"
    KEYWORD_HEURISTIC = "keyword_heuristic"
    LLM_DISCOVERED = "llm_discovered"
    TOC_INFERRED = "toc_inferred"
    HUMAN_OVERRIDE = "human_override"


class FootnoteType(str, Enum):
    """Footnote classification (SPEC §4.A.2 Pass 2, refined by §4.B.4).

    Pass 2 assigns coarse types (tahqiq_editor, author_original, unknown).
    §4.B.4 refines tahqiq_editor into fine-grained sub-types for
    structured metadata extraction. The fine-grained types replace
    the coarse 'tahqiq_editor' when classification succeeds.
    """
    # Coarse types (Pass 2)
    TAHQIQ_EDITOR = "tahqiq_editor"         # Modern editor's annotation (unrefined)
    AUTHOR_ORIGINAL = "author_original"      # Part of original text
    UNKNOWN = "unknown_footnote_type"        # Could not determine

    # Fine-grained types (§4.B.4 — all are sub-types of tahqiq_editor)
    VARIANT_READING = "variant_reading"      # Manuscript textual differences
    HADITH_TAKHRIJ = "hadith_takhrij"        # Hadith source tracing
    CROSS_REFERENCE = "cross_reference"      # Internal/external reference
    BIOGRAPHICAL_NOTE = "biographical_note"  # Scholar identification
    LINGUISTIC_NOTE = "linguistic_note"      # Word/grammar explanation
    CORRECTION_NOTE = "correction_note"      # Editor's text correction
    GENERAL_COMMENTARY = "general_commentary"  # Editor's opinion/analysis


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


class VariantReadingData(BaseModel):
    """Structured data from a variant_reading footnote (SPEC §4.B.4)."""
    sigla_cited: list[str] = Field(description="Manuscript sigla mentioned")
    variant_text: str = Field(description="The alternative reading")
    main_text_reading: str = Field(description="The reading in the main text")
    editor_preferred: Optional[str] = Field(
        None, description="Which siglum the editor chose"
    )


class TakhrijData(BaseModel):
    """Structured data from a hadith_takhrij footnote (SPEC §4.B.4)."""
    collections: list[dict] = Field(
        description="List of {name, book?, number} for each cited collection"
    )
    grading: Optional[dict] = Field(
        None, description="{grader, grade, reference} if hadith grading is present"
    )


class BiographicalNoteData(BaseModel):
    """Structured data from a biographical_note footnote (SPEC §4.B.4)."""
    scholar_name: str
    death_date_ah: Optional[int] = None
    description: Optional[str] = None


class CorrectionNoteData(BaseModel):
    """Structured data from a correction_note footnote (SPEC §4.B.4)."""
    corrected_text: str
    original_text: str
    basis: Optional[str] = Field(None, description="Manuscript or reasoning basis")


class Footnote(BaseModel):
    """An extracted footnote (SPEC §3, enriched by §4.B.4).

    Base fields are always present. Type-specific structured data fields
    are populated when §4.B.4 fine-grained classification succeeds.
    """
    ref_marker: str = Field(description="Reference marker as it appears in text, e.g. '1'")
    text: str = Field(description="Footnote content")
    footnote_type: FootnoteType
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in type classification")
    # §4.B.4 type-specific structured data (exactly one populated based on footnote_type)
    variant_data: Optional[VariantReadingData] = None
    takhrij_data: Optional[TakhrijData] = None
    bio_data: Optional[BiographicalNoteData] = None
    correction_data: Optional[CorrectionNoteData] = None


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
# §4.B.8 — Cross-Page Continuity Intelligence
# ──────────────────────────────────────────────────────────────────

class BoundaryContinuityType(str, Enum):
    """Boundary type between consecutive content units (SPEC §4.B.8)."""
    MID_SENTENCE = "mid_sentence"
    MID_PARAGRAPH = "mid_paragraph"
    MID_ARGUMENT = "mid_argument"
    SECTION_BREAK = "section_break"
    DIVISION_BREAK = "division_break"
    UNKNOWN = "unknown"


class ContinuityDetectionMethod(str, Enum):
    """How boundary continuity was determined (SPEC §4.B.8)."""
    PUNCTUATION_ANALYSIS = "punctuation_analysis"
    STRUCTURAL_MARKER = "structural_marker"
    ARGUMENT_FLOW = "argument_flow"
    FORMAT_SPECIFIC = "format_specific"
    LLM_INFERRED = "llm_inferred"


class BoundaryContinuity(BaseModel):
    """Continuity signal for the boundary after this content unit (SPEC §4.B.8).

    Present on all content units except the last. Classifies whether
    the content flowing across the page boundary is mid-sentence,
    mid-argument, or at a natural break point.
    """
    type: BoundaryContinuityType
    confidence: float = Field(ge=0.0, le=1.0)
    detection_method: ContinuityDetectionMethod
    continuation_hint: Optional[str] = Field(
        None, description="Human-readable description of what continues"
    )


# ──────────────────────────────────────────────────────────────────
# §4.B.10 — Scholarly Discourse Flow Annotation
# ──────────────────────────────────────────────────────────────────

class DiscourseSegmentType(str, Enum):
    """Types of scholarly discourse segments (SPEC §4.B.10)."""
    DEFINITION = "definition"
    RULING = "ruling"
    POSITION = "position"
    EVIDENCE_QURAN = "evidence_quran"
    EVIDENCE_HADITH = "evidence_hadith"
    EVIDENCE_ATHAR = "evidence_athar"
    EVIDENCE_QIYAS = "evidence_qiyas"
    EVIDENCE_IJMA = "evidence_ijma"
    OBJECTION = "objection"
    RESPONSE = "response"
    CONDITION = "condition"
    EXCEPTION = "exception"
    EXAMPLE = "example"
    PREFERRED = "preferred"
    NARRATION = "narration"


class DominantDiscourseType(str, Enum):
    """Overall discourse character of a content unit (SPEC §4.B.10)."""
    ARGUMENTATIVE = "argumentative"
    DEFINITIONAL = "definitional"
    EVIDENTIAL = "evidential"
    NARRATIVE = "narrative"
    ENUMERATIVE = "enumerative"
    INSUFFICIENT_TEXT = "insufficient_text"


class DiscourseSegment(BaseModel):
    """A labeled discourse segment within a content unit (SPEC §4.B.10)."""
    type: DiscourseSegmentType
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)
    detection_method: str = Field(description="'marker' or 'llm_inferred'")
    marker_text: Optional[str] = Field(None, description="The Arabic marker that triggered detection")
    position_metadata: Optional[dict] = Field(
        None, description="For 'position' segments: {school_hint, attribution_hint}"
    )


class DiscourseFlow(BaseModel):
    """Discourse flow annotation for a content unit (SPEC §4.B.10).

    Identifies the sequence of scholarly discourse moves within a page.
    Null for pages with <100 characters of text.
    """
    segments: list[DiscourseSegment] = Field(default_factory=list)
    dominant_discourse_type: DominantDiscourseType
    argument_cycle_complete: bool = False
    argument_cycle_started_at_segment: Optional[int] = Field(
        None, description="Index into segments array where cycle begins"
    )
    cycle_missing_elements: list[str] = Field(
        default_factory=list, description="Discourse types expected but not found"
    )


# ──────────────────────────────────────────────────────────────────
# §4.B.9 — Authorial Voice Fingerprint
# ──────────────────────────────────────────────────────────────────

class SentenceLengthStats(BaseModel):
    """Sentence length distribution statistics (SPEC §4.B.9)."""
    mean: float
    median: float
    std_dev: float


class LayerFingerprint(BaseModel):
    """Stylometric fingerprint for one text layer (SPEC §4.B.9).

    Quantitative writing characteristics that distinguish layers.
    Used for statistical validation of layer attribution decisions.
    """
    author_canonical_id: Optional[str] = None
    total_words_attributed: int = Field(ge=0)
    sentence_length: SentenceLengthStats
    type_token_ratio: float = Field(ge=0.0, le=1.0)
    connective_frequency: float = Field(ge=0.0, le=1.0)
    technical_term_density: float = Field(ge=0.0, le=1.0)
    pronoun_reference_frequency: float = Field(ge=0.0, le=1.0)
    self_reference_frequency: float = Field(ge=0.0, le=1.0)
    citation_density: float = Field(ge=0.0, le=1.0)
    information_density: float = Field(ge=0.0, le=1.0)
    fingerprint_reliability: str = Field(
        default="normal",
        description="'normal' or 'insufficient_data' (when <2000 words attributed)"
    )


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
    boundary_continuity: Optional[BoundaryContinuity] = Field(
        None, description="§4.B.8: Continuity signal for boundary after this page. "
        "Null for last content unit and non-paginated sources."
    )
    discourse_flow: Optional[DiscourseFlow] = Field(
        None, description="§4.B.10: Discourse segment annotation. "
        "Null for pages with <100 characters of text."
    )


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
    division_count_by_tier: dict[str, int] = Field(
        default_factory=dict,
        description="Tier name → count, e.g. {'confirmed': 5, 'high': 12, 'medium': 3, 'low': 1}"
    )
    layer_transition_count: int = 0
    pages_with_warnings: int = 0
    high_fidelity_pct: float = Field(ge=0.0, le=1.0, default=1.0)
    unclassified_footnote_count: int = 0
    overall_confidence: HeadingConfidence = HeadingConfidence.HIGH


# ──────────────────────────────────────────────────────────────────
# Content Census — §4.B.5 downstream adaptation signals
# ──────────────────────────────────────────────────────────────────

class TextDensityProfile(BaseModel):
    """Text density statistics across all content units (SPEC §4.B.5)."""
    mean_chars_per_page: int
    median_chars_per_page: int
    std_dev: float
    sparse_page_count: int = Field(description="Pages with <200 chars")
    dense_page_count: int = Field(description="Pages with >3000 chars")


class LayerComplexity(BaseModel):
    """Multi-layer complexity metrics (SPEC §4.B.5)."""
    layer_count: int = Field(ge=1)
    transition_density: float = Field(description="Mean layer transitions per page")
    matn_ratio: float = Field(ge=0.0, le=1.0, description="Proportion of text attributed to Layer 1")


class StructuralDepth(BaseModel):
    """Division tree depth metrics (SPEC §4.B.5)."""
    division_count: int
    max_depth: int
    mean_pages_per_leaf_division: float


class FootnoteDensity(BaseModel):
    """Footnote distribution metrics (SPEC §4.B.5)."""
    mean_footnotes_per_page: float
    max_footnotes_on_single_page: int
    footnote_text_ratio: float = Field(ge=0.0, le=1.0)


class VocabularyProfile(BaseModel):
    """Vocabulary analysis from sampled pages (SPEC §4.B.5)."""
    estimated_unique_terms: int = Field(description="HyperLogLog estimate, ~0.8% standard error")
    technical_term_density: float = Field(ge=0.0, le=1.0)
    diacritics_density: float = Field(ge=0.0, le=1.0)


class FidelityDistribution(BaseModel):
    """Distribution of text fidelity across pages (SPEC §4.B.5)."""
    high_pct: float = Field(ge=0.0, le=1.0)
    medium_pct: float = Field(ge=0.0, le=1.0)
    low_pct: float = Field(ge=0.0, le=1.0)
    very_low_pct: float = Field(ge=0.0, le=1.0)


class ContentCensus(BaseModel):
    """Statistical profile of source content for downstream adaptation (SPEC §4.B.5).

    Computed as a post-processing step after all content units are generated.
    Enables downstream engines to adapt processing strategy per-source.
    """
    total_pages: int
    text_density_profile: TextDensityProfile
    verse_ratio: float = Field(ge=0.0, le=1.0)
    table_ratio: float = Field(ge=0.0, le=1.0)
    quran_citation_ratio: float = Field(ge=0.0, le=1.0)
    hadith_citation_ratio: float = Field(ge=0.0, le=1.0)
    layer_complexity: Optional[LayerComplexity] = Field(
        None, description="Present only for multi-layer sources"
    )
    structural_depth: StructuralDepth
    footnote_density: FootnoteDensity
    vocabulary_profile: VocabularyProfile
    fidelity_distribution: FidelityDistribution


# ──────────────────────────────────────────────────────────────────
# Tahqiq Apparatus Topology — §4.B.7
# ──────────────────────────────────────────────────────────────────

class ManuscriptWitness(BaseModel):
    """A manuscript witness referenced in the tahqiq apparatus (SPEC §4.B.7)."""
    siglum: str = Field(description="Editor's abbreviation, e.g. 'أ' or 'الأصل'")
    description: Optional[str] = Field(None, description="Full name if available from introduction")
    citation_count: int = Field(ge=0)
    first_cited_unit: int = Field(ge=0)
    last_cited_unit: int = Field(ge=0)


class DivisionDisagreement(BaseModel):
    """Variant reading density for one division (SPEC §4.B.7)."""
    div_id: str
    variant_count: int
    pages: int


class EditionReliability(BaseModel):
    """Aggregate reliability signal for the tahqiq edition (SPEC §4.B.7)."""
    witness_count: int
    witness_coverage: float = Field(ge=0.0, le=1.0, description="Proportion of text supported by ≥2 witnesses")
    editor_transparency: float = Field(ge=0.0, le=1.0, description="Proportion of variants with editor reasoning")
    reliability_signal: str = Field(description="One of: high, moderate, low, minimal")
    reliability_rationale: str


class TahqiqTopology(BaseModel):
    """Manuscript witness network extracted from footnote apparatus (SPEC §4.B.7).

    Transforms the footnote apparatus from flat text into scholarly intelligence
    about the quality and reliability of the edition itself.
    """
    has_tahqiq_apparatus: bool
    manuscript_witnesses: list[ManuscriptWitness] = Field(default_factory=list)
    total_variant_readings: int = 0
    variant_density_per_100_pages: float = 0.0
    anonymous_variant_count: int = Field(
        default=0, description="Variants referencing unnamed witnesses ('في بعض النسخ')"
    )
    disagreement_by_division: list[DivisionDisagreement] = Field(default_factory=list)
    edition_reliability: Optional[EditionReliability] = None
    extraction_confidence: HeadingConfidence = HeadingConfidence.MEDIUM
    extraction_method: str = "pattern_matching_with_llm_fallback"


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
    content_census: Optional[ContentCensus] = Field(
        None, description="§4.B.5 statistical profile for downstream adaptation"
    )
    tahqiq_topology: Optional[TahqiqTopology] = Field(
        None, description="§4.B.7 manuscript witness network from footnote apparatus"
    )
    layer_fingerprints: Optional[dict[str, LayerFingerprint]] = Field(
        None, description="§4.B.9: Per-layer stylometric fingerprints. "
        "Keys are layer type names (e.g. 'matn', 'sharh'). "
        "Null for single-layer sources."
    )
    discourse_flow_summary: Optional[dict] = Field(
        None, description="§4.B.10: Aggregate discourse flow statistics. "
        "Contains dominant_discourse_type, argument_cycle_count, "
        "evidence_type_distribution, discourse_segment_distribution."
    )


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
