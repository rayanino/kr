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
    heading_source: Optional[str] = Field(
        None,
        description="How heading was obtained: 'division_tree', 'llm_inferred', or null"
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
    review_flags: list[str] = Field(default_factory=list)

    # §4.B transformative capability outputs
    quality_prediction: Optional[QualityPrediction] = None
    commentary_alignment: Optional[list[CommentaryAlignmentRecord]] = None
    adaptive_params: Optional[AdaptiveParams] = None
    argument_structure: Optional[ArgumentStructure] = None


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
