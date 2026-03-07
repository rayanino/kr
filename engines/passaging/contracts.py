"""Passaging Engine Contracts — Machine-readable schemas derived from SPEC.md §3.

These Pydantic models define the PASSAGE STREAM — the artifact that downstream
engines (atomization, excerpting) consume.

When SPEC.md §3 and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# Import upstream types used in pass-through
from engines.normalization.contracts import (
    FootnoteType,
    HeadingConfidence,
    LayerType,
    TextFidelityLevel,
)


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────

class ReviewFlag(str, Enum):
    """Machine-generated flags for human review on passages (SPEC §3).

    Each flag identifies a specific quality concern. Passages may carry
    zero or more flags.
    """
    LOW_CONFIDENCE_BOUNDARY = "low_confidence_boundary"
    CROSS_VOLUME = "cross_volume"
    VERY_SHORT = "very_short"
    VERY_LONG = "very_long"
    LOW_FIDELITY_CONTENT = "low_fidelity_content"
    SPLIT_FROM_LARGE = "split_from_large"
    MERGED_SIBLINGS = "merged_siblings"
    MIXED_LAYERS = "mixed_layers"
    IMPLICIT_BOUNDARY = "implicit_boundary"
    ARGUMENT_PRESERVED = "argument_preserved"
    FORMAT_DETECTION_FAILED = "format_detection_failed"
    HIGH_COST_BOUNDARY = "high_cost_boundary"
    INCOMPLETE_SCHOLARLY_CONTENT = "incomplete_scholarly_content"
    AUTHORIAL_INCOMPLETENESS = "authorial_incompleteness"
    ARGUMENT_DEPTH_EXCEEDED = "argument_depth_exceeded"


class HeadingSource(str, Enum):
    """How a passage's heading was obtained (SPEC §3)."""
    DIVISION_TREE = "division_tree"
    LLM_INFERRED = "llm_inferred"


class PassageStructuralFormat(str, Enum):
    """Per-passage structural format (SPEC §3).

    These are passage-level format classifications, which may differ from
    the source-level StructuralFormat when the source is 'mixed'.
    """
    PROSE = "prose"
    VERSE = "verse"
    QA_PAIR = "qa_pair"
    TABULAR_MASALA = "tabular_masala"
    DICTIONARY_ENTRY = "dictionary_entry"
    COMMENTARY_UNIT = "commentary_unit"


class SizingAction(str, Enum):
    """How this passage was sized relative to divisions (SPEC §3)."""
    DIRECT = "direct"       # Division became passage directly (in target range)
    MERGED = "merged"       # Multiple small divisions merged into one passage
    SPLIT = "split"         # Large division split into multiple passages


class ArgumentCompleteness(str, Enum):
    """Scholarly argument completeness in a passage (SPEC §4.B.6)."""
    COMPLETE = "complete"               # Full argument: opening through conclusion
    PARTIAL_OPENING = "partial_opening"  # Argument opens but doesn't close in this passage
    PARTIAL_CLOSING = "partial_closing"  # Argument closes but opened in previous passage


class ArgumentDetectionSource(str, Enum):
    """How the argument structure was detected (SPEC §4.B.6)."""
    DISCOURSE_FLOW = "discourse_flow"             # Primary: normalization engine's §4.B.10
    KEYWORD_STATE_MACHINE = "keyword_state_machine"  # Fallback: passaging engine's own detection
    CROSS_VALIDATED = "cross_validated"            # Both signals agreed


class CompletenessLevel(str, Enum):
    """Predicted scholarly completeness of a passage (SPEC §4.B.8)."""
    COMPLETE = "complete"               # At least one full argument cycle detected
    PARTIAL_OPENING = "partial_opening"  # Opens with content from previous passage
    PARTIAL_CLOSING = "partial_closing"  # Closes with incomplete argument
    FRAGMENT = "fragment"               # Discourse segments that don't form a scholarly unit
    UNKNOWN = "unknown"                 # Discourse flow unavailable


class CommentarySensitivity(str, Enum):
    """Commentary-unit detection granularity (SPEC §4.B.5)."""
    FINE = "fine"       # Detect at every layer transition
    NORMAL = "normal"   # Detect at transitions with ≥10-word matn segments
    COARSE = "coarse"   # Detect only at paragraph-level transitions


# ──────────────────────────────────────────────────────────────────
# Sub-models
# ──────────────────────────────────────────────────────────────────

class PassageTextLayerSegment(BaseModel):
    """A text layer segment rebased to passage_text offsets (SPEC §3, §4.A.2)."""
    layer_type: LayerType
    author_canonical_id: Optional[str] = None
    start: int = Field(ge=0, description="Start char offset in passage_text (inclusive)")
    end: int = Field(ge=0, description="End char offset in passage_text (exclusive)")
    confidence: float = Field(ge=0.0, le=1.0)


class PassageFootnote(BaseModel):
    """A footnote within a passage, with renumbered marker (SPEC §3, §4.A.2)."""
    ref_marker: str = Field(description="Renumbered marker as it appears in passage_text, e.g. '1'")
    text: str
    footnote_type: FootnoteType
    confidence: float = Field(ge=0.0, le=1.0)
    source_unit_index: int = Field(
        ge=0, description="unit_index of the content unit this footnote originated from"
    )


class DivisionPathEntry(BaseModel):
    """One node in the division path from root to passage (SPEC §3)."""
    div_id: str = Field(description="Passaging-engine-generated ID: div_{source_id}_{depth}_{index}")
    heading_text: str
    heading_level: int = Field(ge=1, le=10)


class UnitRange(BaseModel):
    """Content unit index range covered by a passage (SPEC §3)."""
    start: int = Field(ge=0, description="First unit_index (inclusive)")
    end: int = Field(ge=0, description="Last unit_index (inclusive)")


class PhysicalPages(BaseModel):
    """Human-readable page range for citation (SPEC §3)."""
    volume: Optional[int] = None
    start_page_display: Optional[str] = None
    end_page_display: Optional[str] = None
    start_page_int: Optional[int] = None
    end_page_int: Optional[int] = None
    page_count: int = Field(ge=1)


class PassageVerseLineInfo(BaseModel):
    """A verse line in a verse passage (SPEC §3)."""
    verse_number: Optional[int] = None
    first_hemistich: str
    second_hemistich: str


class PassageVerseInfo(BaseModel):
    """Verse information for verse-format passages (SPEC §3)."""
    verse_lines: list[PassageVerseLineInfo]
    verse_count: int = Field(ge=1)


class PassageContentFlags(BaseModel):
    """Aggregated content flags from constituent units (SPEC §3).

    True if ANY constituent content unit has the flag set.
    """
    has_verse: bool = False
    has_table: bool = False
    has_quran_citation: bool = False
    has_hadith_citation: bool = False


class PassageTextFidelity(BaseModel):
    """Aggregate text fidelity across constituent units (SPEC §3)."""
    min_score: TextFidelityLevel = Field(description="Lowest fidelity among constituent units")
    mean_score: float = Field(
        ge=0.0, le=1.0,
        description="Mean fidelity (high=1.0, medium=0.7, low=0.4, very_low=0.1)"
    )
    pages_with_warnings: int = Field(ge=0)


class PassageSizing(BaseModel):
    """Sizing metadata: how this passage was formed (SPEC §3)."""
    action: SizingAction
    word_count: int = Field(ge=0, description="Arabic word count (whitespace tokenization)")
    char_count: int = Field(ge=0, description="Character count of passage_text")
    notes: Optional[str] = Field(
        None, description="Explanation of merge/split, e.g. 'Split 2 of 3 from division div_...'"
    )


# ──────────────────────────────────────────────────────────────────
# §4.B output models (transformative capabilities)
# ──────────────────────────────────────────────────────────────────

class QualityPrediction(BaseModel):
    """Passage quality prediction scores (SPEC §4.B.1). [NOT YET IMPLEMENTED]"""
    coherence: float = Field(ge=0.0, le=1.0)
    boundary_quality: float = Field(ge=0.0, le=1.0)
    extractability: float = Field(ge=0.0, le=1.0)
    overall: float = Field(
        ge=0.0, le=1.0,
        description="Weighted: coherence×0.4 + boundary_quality×0.3 + extractability×0.3"
    )


class MatnSegment(BaseModel):
    """A matn segment in commentary alignment (SPEC §4.B.3)."""
    text: str
    start: int = Field(ge=0, description="Start char offset in passage_text")
    end: int = Field(ge=0, description="End char offset in passage_text")
    verse_number: Optional[int] = None


class CommentarySpan(BaseModel):
    """A commentary span aligned to a matn segment (SPEC §4.B.3)."""
    start: int = Field(ge=0)
    end: int = Field(ge=0)


class CommentaryAlignmentRecord(BaseModel):
    """One matn-commentary alignment pair (SPEC §4.B.3). [NOT YET IMPLEMENTED]"""
    matn_segment: MatnSegment
    commentary_span: CommentarySpan
    alignment_confidence: float = Field(ge=0.0, le=1.0)


class AdaptiveParams(BaseModel):
    """Content census-driven adaptation parameters applied to this passage (SPEC §4.B.5)."""
    adapted_target_high: int = Field(description="Adapted upper target passage size")
    footnote_factor: float = Field(
        ge=0.0, le=1.0,
        description="Footnote density adjustment factor (1.0 = no adjustment)"
    )
    adapted_merge_threshold: Optional[int] = Field(
        None, description="Adapted merge threshold (null if default used)"
    )
    adapted_llm_splitting_threshold: Optional[int] = Field(
        None, description="Adapted LLM splitting threshold (null if default used)"
    )
    commentary_sensitivity: Optional[CommentarySensitivity] = Field(
        None, description="Adapted commentary sensitivity (null for non-commentary sources)"
    )
    adaptation_rationale: str = Field(description="Human-readable explanation of adaptations")


class ArgumentStructure(BaseModel):
    """Scholarly argument detection results for this passage (SPEC §4.B.6). [NOT YET IMPLEMENTED]"""
    detected: bool = Field(description="Whether argument markers were found")
    argument_markers_found: list[str] = Field(
        default_factory=list,
        description="Arabic markers found, e.g. ['مسألة:', 'والدليل', 'والراجح']"
    )
    completeness: ArgumentCompleteness
    protected_from_split: bool = Field(
        description="Whether argument preservation prevented this passage from being split"
    )
    depth: int = Field(ge=0, description="Nesting depth of deepest argument in passage")
    detection_source: ArgumentDetectionSource = Field(
        description="Which signal was used: discourse_flow (primary), "
        "keyword_state_machine (fallback), or cross_validated (both agreed)"
    )


class DanglingDiscourse(BaseModel):
    """A discourse segment that expects continuation (SPEC §4.B.8). [NOT YET IMPLEMENTED]"""
    type: str = Field(description="The discourse segment type that is dangling")
    expects: str = Field(description="What discourse type is expected next")


class CompletenessForecast(BaseModel):
    """Predicted scholarly completeness for a passage (SPEC §4.B.8). [NOT YET IMPLEMENTED]"""
    forecast: CompletenessLevel
    discourse_types_present: list[str] = Field(
        default_factory=list,
        description="Discourse segment types found in this passage"
    )
    complete_argument_cycles: int = Field(
        ge=0, description="Number of complete argument cycles detected"
    )
    dangling_discourse: Optional[DanglingDiscourse] = Field(
        None, description="If forecast is partial_closing or fragment, what's missing"
    )
    structural_incompleteness: bool = Field(
        default=False,
        description="True if incompleteness is due to boundary placement, not authorial choice"
    )
    confidence: float = Field(ge=0.0, le=1.0)


# ──────────────────────────────────────────────────────────────────
# Primary output: Passage record
# ──────────────────────────────────────────────────────────────────

class PassageRecord(BaseModel):
    """One record in the passage stream (passages.jsonl) — SPEC §3.

    Written to: library/sources/{source_id}/passages/passages.jsonl
    Each passage is a processing unit for downstream engines.
    """
    schema_version: str = Field(default="passage_v2.0")
    passage_id: str = Field(
        description="Globally unique: psg_{source_id}_{zero_padded_sequence}"
    )
    source_id: str
    sequence_index: int = Field(ge=0, description="Zero-based, monotonically increasing, gapless")

    # Text content
    passage_text: str = Field(
        min_length=1,
        description="Assembled text with cross-page joining. "
        "Footnote markers ⌜N⌝ inline. Diacritics preserved exactly."
    )
    text_layers: list[PassageTextLayerSegment] = Field(
        description="Layer segments rebased to passage_text offsets. "
        "Every char covered by exactly one segment."
    )
    footnotes: list[PassageFootnote] = Field(default_factory=list)

    # Structural context
    division_path: list[DivisionPathEntry] = Field(
        description="Path from root to this passage's position in division tree"
    )
    division_ids: list[str] = Field(
        min_length=1,
        description="Leaf division div_id(s). Multiple if merged siblings."
    )
    heading_text: Optional[str] = Field(
        None,
        description="Heading of primary division. Null for split pieces (except first)."
    )
    heading_source: Optional[HeadingSource] = Field(
        None,
        description="How heading was obtained: division_tree, llm_inferred, or null"
    )

    # Location
    unit_range: UnitRange
    physical_pages: PhysicalPages

    # Format and content
    structural_format: PassageStructuralFormat
    verse_info: Optional[PassageVerseInfo] = None
    content_flags: PassageContentFlags = Field(default_factory=PassageContentFlags)
    text_fidelity: PassageTextFidelity

    # Sizing
    sizing: PassageSizing

    # Navigation
    predecessor_id: Optional[str] = None
    successor_id: Optional[str] = None

    # Quality signals
    review_flags: list[ReviewFlag] = Field(default_factory=list)

    # §4.B transformative capability outputs
    quality_prediction: Optional[QualityPrediction] = None
    commentary_alignment: Optional[list[CommentaryAlignmentRecord]] = None
    adaptive_params: Optional[AdaptiveParams] = None
    argument_structure: Optional[ArgumentStructure] = None
    completeness_forecast: Optional[CompletenessForecast] = None


# ──────────────────────────────────────────────────────────────────
# Cross-edition correspondence (§4.B.4 — separate file)
# ──────────────────────────────────────────────────────────────────

class CrossEditionCorrespondence(BaseModel):
    """One passage-level correspondence between editions (SPEC §4.B.4). [NOT YET IMPLEMENTED]

    Written to: library/sources/{source_id}/passages/cross_edition_map.json
    """
    this_passage_id: str
    other_source_id: str
    other_passage_id: str
    overlap_score: float = Field(ge=0.0, le=1.0)
    alignment_method: str = Field(
        description="One of: character_ngram, division_tree, sequential_dtw"
    )


class CrossEditionMap(BaseModel):
    """Cross-edition passage correspondence map (SPEC §4.B.4). [NOT YET IMPLEMENTED]"""
    source_id: str
    correspondences: list[CrossEditionCorrespondence] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Full passage stream — convenience wrapper
# ──────────────────────────────────────────────────────────────────

class PassageStream(BaseModel):
    """The complete passage stream for a source (SPEC §3).

    Logical wrapper — on disk this is passages.jsonl (one record per line).
    """
    source_id: str
    passages: list[PassageRecord] = Field(
        description="Ordered by sequence_index. No gaps. Non-overlapping."
    )


# ──────────────────────────────────────────────────────────────────
# Error codes (SPEC §7)
# ──────────────────────────────────────────────────────────────────

class ErrorSeverity(str, Enum):
    """Error severity levels (SPEC §7)."""
    FATAL = "fatal"
    WARNING = "warning"
    INFO = "info"


class PassagingErrorCode(str, Enum):
    """All error codes defined in SPEC §7.

    Fatal errors abort processing. Warnings are logged and processing continues.
    Info events are logged for diagnostics.
    """
    # Input validation (§2)
    MANIFEST_INVALID = "PSG_MANIFEST_INVALID"
    SCHEMA_UNSUPPORTED = "PSG_SCHEMA_UNSUPPORTED"
    CONTENT_MISSING = "PSG_CONTENT_MISSING"
    CONTENT_COUNT_MISMATCH = "PSG_CONTENT_COUNT_MISMATCH"
    CONTENT_UNORDERED = "PSG_CONTENT_UNORDERED"
    CONTENT_GAP = "PSG_CONTENT_GAP"
    DIVISION_INCONSISTENT = "PSG_DIVISION_INCONSISTENT"

    # Processing (§4.A)
    FORMAT_DETECTION_FAILED = "PSG_FORMAT_DETECTION_FAILED"
    SPLIT_FALLBACK = "PSG_SPLIT_FALLBACK"
    LLM_UNAVAILABLE = "PSG_LLM_UNAVAILABLE"

    # Self-validation (§4.A.10)
    VALIDATION_COVERAGE = "PSG_VALIDATION_COVERAGE"
    VALIDATION_OVERLAP = "PSG_VALIDATION_OVERLAP"
    VALIDATION_SIZE = "PSG_VALIDATION_SIZE"
    VALIDATION_FOOTNOTE = "PSG_VALIDATION_FOOTNOTE"
    VALIDATION_COVERAGE_GAP = "PSG_VALIDATION_COVERAGE_GAP"
    VALIDATION_BOUNDARY_MIDSENTENCE = "PSG_VALIDATION_BOUNDARY_MIDSENTENCE"
    VALIDATION_LINK_BROKEN = "PSG_VALIDATION_LINK_BROKEN"
    VALIDATION_AUTHOR_LOST = "PSG_VALIDATION_AUTHOR_LOST"
    VALIDATION_FOOTNOTE_ORPHAN = "PSG_VALIDATION_FOOTNOTE_ORPHAN"
    VALIDATION_TEXT_LOSS = "PSG_VALIDATION_TEXT_LOSS"

    # Quality checks (§5)
    SIZE_DISTRIBUTION_SKEWED = "PSG_SIZE_DISTRIBUTION_SKEWED"
    LOW_COHERENCE = "PSG_LOW_COHERENCE"
    WEAK_BOUNDARIES = "PSG_WEAK_BOUNDARIES"
    DIVISION_PATHOLOGICAL = "PSG_DIVISION_PATHOLOGICAL"

    # §4.B capabilities
    ARGUMENT_OVERSIZED = "PSG_ARGUMENT_OVERSIZED"
    ADAPTATION_FAILED = "PSG_ADAPTATION_FAILED"
    ISNAD_SPLIT = "PSG_ISNAD_SPLIT"
    ARGUMENT_NO_SUBBOUNDARY = "PSG_ARGUMENT_NO_SUBBOUNDARY"
    ARGUMENT_SIGNAL_DISAGREEMENT = "PSG_ARGUMENT_SIGNAL_DISAGREEMENT"
    DISCOURSE_FLOW_ABSENT = "PSG_DISCOURSE_FLOW_ABSENT"
    BOUNDARY_HIGH_COST = "PSG_BOUNDARY_HIGH_COST"
    COMPLETENESS_FRAGMENT = "PSG_COMPLETENESS_FRAGMENT"
    COMPLETENESS_MERGE_REPAIR = "PSG_COMPLETENESS_MERGE_REPAIR"
    AUTHORIAL_INCOMPLETENESS = "PSG_AUTHORIAL_INCOMPLETENESS"
    ARGUMENT_DEPTH_CAP_HIT = "PSG_ARGUMENT_DEPTH_CAP_HIT"

    # Assembly-specific
    ASSEMBLY_QURAN_UNCLOSED = "PSG_ASSEMBLY_QURAN_UNCLOSED"
    ASSEMBLY_FOOTNOTE_COLLISION = "PSG_ASSEMBLY_FOOTNOTE_COLLISION"
    ASSEMBLY_LAYER_MISMATCH = "PSG_ASSEMBLY_LAYER_MISMATCH"
    ASSEMBLY_CONTINUITY_OVERRIDE = "PSG_ASSEMBLY_CONTINUITY_OVERRIDE"


# Map error codes to their severity for programmatic use
ERROR_SEVERITY: dict[PassagingErrorCode, ErrorSeverity] = {
    PassagingErrorCode.MANIFEST_INVALID: ErrorSeverity.FATAL,
    PassagingErrorCode.SCHEMA_UNSUPPORTED: ErrorSeverity.FATAL,
    PassagingErrorCode.CONTENT_MISSING: ErrorSeverity.FATAL,
    PassagingErrorCode.CONTENT_COUNT_MISMATCH: ErrorSeverity.WARNING,
    PassagingErrorCode.CONTENT_UNORDERED: ErrorSeverity.FATAL,
    PassagingErrorCode.CONTENT_GAP: ErrorSeverity.WARNING,
    PassagingErrorCode.DIVISION_INCONSISTENT: ErrorSeverity.WARNING,
    PassagingErrorCode.FORMAT_DETECTION_FAILED: ErrorSeverity.WARNING,
    PassagingErrorCode.SPLIT_FALLBACK: ErrorSeverity.INFO,
    PassagingErrorCode.LLM_UNAVAILABLE: ErrorSeverity.WARNING,
    PassagingErrorCode.VALIDATION_COVERAGE: ErrorSeverity.FATAL,
    PassagingErrorCode.VALIDATION_OVERLAP: ErrorSeverity.FATAL,
    PassagingErrorCode.VALIDATION_SIZE: ErrorSeverity.WARNING,
    PassagingErrorCode.VALIDATION_FOOTNOTE: ErrorSeverity.WARNING,
    PassagingErrorCode.VALIDATION_COVERAGE_GAP: ErrorSeverity.FATAL,
    PassagingErrorCode.VALIDATION_BOUNDARY_MIDSENTENCE: ErrorSeverity.WARNING,
    PassagingErrorCode.VALIDATION_LINK_BROKEN: ErrorSeverity.FATAL,
    PassagingErrorCode.VALIDATION_AUTHOR_LOST: ErrorSeverity.FATAL,
    PassagingErrorCode.VALIDATION_FOOTNOTE_ORPHAN: ErrorSeverity.WARNING,
    PassagingErrorCode.VALIDATION_TEXT_LOSS: ErrorSeverity.FATAL,
    PassagingErrorCode.SIZE_DISTRIBUTION_SKEWED: ErrorSeverity.WARNING,
    PassagingErrorCode.LOW_COHERENCE: ErrorSeverity.WARNING,
    PassagingErrorCode.WEAK_BOUNDARIES: ErrorSeverity.WARNING,
    PassagingErrorCode.DIVISION_PATHOLOGICAL: ErrorSeverity.WARNING,
    PassagingErrorCode.ARGUMENT_OVERSIZED: ErrorSeverity.WARNING,
    PassagingErrorCode.ADAPTATION_FAILED: ErrorSeverity.INFO,
    PassagingErrorCode.ISNAD_SPLIT: ErrorSeverity.WARNING,
    PassagingErrorCode.ARGUMENT_NO_SUBBOUNDARY: ErrorSeverity.WARNING,
    PassagingErrorCode.ARGUMENT_SIGNAL_DISAGREEMENT: ErrorSeverity.INFO,
    PassagingErrorCode.DISCOURSE_FLOW_ABSENT: ErrorSeverity.INFO,
    PassagingErrorCode.BOUNDARY_HIGH_COST: ErrorSeverity.WARNING,
    PassagingErrorCode.COMPLETENESS_FRAGMENT: ErrorSeverity.WARNING,
    PassagingErrorCode.COMPLETENESS_MERGE_REPAIR: ErrorSeverity.INFO,
    PassagingErrorCode.AUTHORIAL_INCOMPLETENESS: ErrorSeverity.INFO,
    PassagingErrorCode.ARGUMENT_DEPTH_CAP_HIT: ErrorSeverity.INFO,
    PassagingErrorCode.ASSEMBLY_QURAN_UNCLOSED: ErrorSeverity.WARNING,
    PassagingErrorCode.ASSEMBLY_FOOTNOTE_COLLISION: ErrorSeverity.FATAL,
    PassagingErrorCode.ASSEMBLY_LAYER_MISMATCH: ErrorSeverity.WARNING,
    PassagingErrorCode.ASSEMBLY_CONTINUITY_OVERRIDE: ErrorSeverity.INFO,
}


# ──────────────────────────────────────────────────────────────────
# Configuration (SPEC §8)
# ──────────────────────────────────────────────────────────────────

class PassagingConfig(BaseModel):
    """Passaging engine configuration parameters (SPEC §8).

    All parameters have defaults. Per-science overrides via SCIENCE.md files.
    """
    # Size parameters
    min_passage_words: int = Field(default=50, ge=20, le=200)
    target_passage_words_low: int = Field(default=200, ge=50, le=500)
    target_passage_words_high: int = Field(default=800, ge=300, le=3000)
    hard_max_passage_words: int = Field(default=2000, ge=500, le=5000)
    verse_min_passage_words: int = Field(default=100, ge=20, le=200)
    merge_threshold: int = Field(default=50, ge=20, le=200)

    # Quality thresholds
    coherence_threshold: float = Field(default=0.5, ge=0.2, le=0.9)
    boundary_distance_threshold: float = Field(default=0.3, ge=0.1, le=0.7)

    # Processing thresholds
    llm_splitting_threshold: int = Field(default=1000, ge=500, le=2000)
    cross_edition_overlap_threshold: float = Field(default=0.8, ge=0.5, le=1.0)
    argument_max_expansion: float = Field(default=1.5, ge=1.1, le=2.0)

    # Feature toggles
    enable_quality_prediction: bool = False
    enable_implicit_structure: bool = True
    enable_commentary_alignment: bool = True
    enable_adaptive_passaging: bool = True
    enable_argument_detection: bool = True
