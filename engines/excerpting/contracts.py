"""Excerpting Engine Contracts — Machine-readable schemas derived from SPEC.md §2/§3/§5/§7/§8.

These Pydantic models define the excerpting engine's data pipeline:

    NormalizedPackage (input — normalization contracts, NOT redefined here)
      → AssembledChunk (Phase 1 output)
        → ClassifiedSegment (Phase 2a output)
          → TeachingUnit (Phase 2b output)
            → ExcerptRecord (Phase 3 output / engine output)

Plus: LLM response schemas, error codes, configuration, and invariant validators.

When SPEC.md and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from engines.normalization.contracts import (
    BoundaryContinuityType,
    ContentFlags,
    Footnote,
    PhysicalPage,
    StructuralFormat,
    TextLayerSegment,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Enumerations
# ═══════════════════════════════════════════════════════════════════


class ScholarlyFunction(str, Enum):
    """16-type flat taxonomy for segment classification (SPEC §2.3.1).

    Validated across 23 divisions in 7 formats. The LLM classifies based
    on semantic analysis, not marker matching.
    """

    DEFINITION = "definition"
    RULE_STATEMENT = "rule_statement"
    EVIDENCE_QURAN = "evidence_quran"
    EVIDENCE_HADITH = "evidence_hadith"
    EVIDENCE_IJMA = "evidence_ijma"
    EVIDENCE_QIYAS = "evidence_qiyas"
    EVIDENCE_RATIONAL = "evidence_rational"
    OPINION_STATEMENT = "opinion_statement"
    REFUTATION = "refutation"
    EXAMPLE = "example"
    CONDITION_EXCEPTION = "condition_exception"
    CROSS_REFERENCE = "cross_reference"
    NARRATION = "narration"
    EDITORIAL_NOTE = "editorial_note"
    STRUCTURAL_TRANSITION = "structural_transition"
    UNCLASSIFIED = "unclassified"


class SelfContainmentLevel(str, Enum):
    """Self-containment assessment for a teaching unit (SPEC §2.3.1, §3).

    FULL: All §3 criteria met. Excerpt stands alone.
    PARTIAL: Most criteria met, context would help. Phase 3 adds context_hint.
    DEPENDENT: Cannot be understood alone. Flagged for human gate review.
    """

    FULL = "FULL"
    PARTIAL = "PARTIAL"
    DEPENDENT = "DEPENDENT"


# StructuralFormat is imported from engines.normalization.contracts — NOT redefined.


# ═══════════════════════════════════════════════════════════════════
# Sub-types — Output and Shared
# ═══════════════════════════════════════════════════════════════════


class PageRange(BaseModel):
    """Physical page range for an excerpt (SPEC §2.2.2).

    Derived from AssembledChunk.physical_pages in §7.1 F-DET-6.
    Null on ExcerptRecord when physical page information is unavailable.
    """

    volume: Optional[int] = None
    start_page: int
    end_page: int


class AuthorAttribution(BaseModel):
    """Author attribution for a teaching unit (SPEC §2.2.2, §6.2).

    The rule_applied field identifies which attribution rule determined
    this attribution: LA-1 (single-layer), LA-2 (dominant layer >=80%),
    LA-3 (ambiguous — consensus needed), LA-4 (explicit authorial voice).
    """

    layer_id: str
    author_id: str
    coverage_pct: float = Field(ge=0.0, le=1.0)
    rule_applied: str = Field(
        description="One of: LA-1, LA-2, LA-3, LA-4 (§6.2)"
    )


class ScholarAttribution(BaseModel):
    """A quoted or referenced scholar in an excerpt (SPEC §2.2.2).

    The source field distinguishes structural detection ('layer_overlap'
    from F-DET-9) from LLM resolution ('llm_enrichment' from §7.2).
    """

    mention_text: str
    resolved_name: Optional[str] = None
    role: str = Field(
        description="One of: quoted_opinion, classification_frame, refuted_position"
    )
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = Field(
        description="One of: layer_overlap (F-DET-9), llm_enrichment (§7.2)"
    )


class EvidenceRef(BaseModel):
    """A structured evidence reference extracted from text (SPEC §2.2.2, §7.1 F-DET-5).

    F-DET-5 performs structural pattern matching only. Fields not applicable
    to the evidence type are null.
    """

    type: str = Field(description="One of: quran, hadith, ijma")
    surah: Optional[int] = None
    ayah_start: Optional[int] = None
    ayah_end: Optional[int] = None
    text_snippet: str
    marker_text: Optional[str] = None
    scope: Optional[str] = None


class TakhrijEntry(BaseModel):
    """Hadith source tracing data (SPEC §2.2.2, §7.2.4)."""

    hadith_text_snippet: str
    collections: list[str]
    hadith_numbers: list[str] = Field(
        description="Hadith numbers if mentioned (may be empty)"
    )
    grade: Optional[str] = None
    grade_source: Optional[str] = None


class CrossReference(BaseModel):
    """A cross-reference to another section or work (SPEC §2.2.2, §7.2.4).

    Shared between ExcerptRecord (§2.2.2) and LLM response schema (§7.2.4).
    target_div_id MUST default to None because the LLM schema does not produce
    it — Phase 3 deterministic processing fills it in via division tree heading
    search.
    """

    reference_text: str
    target_description: Optional[str] = None
    target_div_id: Optional[str] = None
    resolved: bool


class TermVariant(BaseModel):
    """A terminology variant mapping (SPEC §2.2.2, §7.2.4)."""

    term: str
    variants: list[str]


class ConsensusDecision(BaseModel):
    """One decision within a consensus record (SPEC §2.2.2, §7.3)."""

    decision_type: str
    enrichment_value: str
    verifier_value: Optional[str] = None
    verifier_agrees: Optional[bool] = None
    escalation_value: Optional[str] = None
    final_value: str
    resolution_method: str


class ConsensusRecord(BaseModel):
    """Consensus metadata for an excerpt (SPEC §2.2.2, §7.3)."""

    decisions: list[ConsensusDecision]


class SplitInfo(BaseModel):
    """Split provenance for an oversized division (SPEC §2.3.2)."""

    original_div_id: str
    chunk_index: int = Field(ge=0, description="0-based index within the split result")
    total_chunks: int = Field(ge=1)
    split_method: str = Field(
        description="One of: heading_marker, section_break, paragraph_break, "
        "sentence_boundary"
    )


# ═══════════════════════════════════════════════════════════════════
# Sub-types — Assembly
# ═══════════════════════════════════════════════════════════════════


class JoinPoint(BaseModel):
    """A page boundary join within an assembled chunk (SPEC §2.3.2)."""

    after_unit_index: int
    before_unit_index: int
    boundary_type: BoundaryContinuityType
    separator_used: str = Field(
        description='Separator inserted: "" for mid_sentence, '
        '"\\n" for mid_paragraph/mid_argument/unknown, '
        '"\\n\\n" for section_break/division_break'
    )
    char_offset_in_assembled: int = Field(ge=0)


class AssemblyMetadata(BaseModel):
    """Provenance record for chunk assembly (SPEC §2.3.2)."""

    constituent_unit_indices: list[int] = Field(
        description="unit_index values of all ContentUnits assembled into this chunk"
    )
    join_points: list[JoinPoint] = Field(
        default_factory=list,
        description="One entry per page boundary within this chunk",
    )
    layer_split_points: list[int] = Field(
        default_factory=list,
        description="Character offsets where text layers were artificially divided "
        "by §4.5 splitting. Empty for unsplit chunks. Phase 3 treats split-induced "
        "boundaries as non-meaningful.",
    )
    footnote_renumber_map: Optional[dict[str, str]] = Field(
        None,
        description="Maps old ref_marker to new ref_marker when renumbering "
        "occurred (§4.7). Null when no renumbering was needed.",
    )


# ═══════════════════════════════════════════════════════════════════
# Intermediate Types
# ═══════════════════════════════════════════════════════════════════


class AssembledChunk(BaseModel):
    """Phase 1 output: a processable unit of text (SPEC §2.3.2).

    One leaf division (or merged/split portion thereof) with all cross-page
    text assembled into a single continuous string. Fully deterministic.
    16 fields.
    """

    chunk_id: str = Field(
        description="Format: {div_id} for unsplit; {div_id}_chunk_{N} for split"
    )
    source_id: str
    div_id: str = Field(
        description="Leaf division ID. Format: div_{source_id}_{depth}_{index}"
    )
    div_path: list[str] = Field(
        description="Heading hierarchy from root to this division, root-first"
    )
    assembled_text: str = Field(
        description="Full text of this chunk. All diacritics preserved exactly. "
        "Footnote refs preserved as ⌜N⌝."
    )
    word_count: int = Field(
        description="Arabic word count: whitespace-delimited tokens with "
        ">=1 char in U+0600-U+06FF"
    )
    total_tokens: int = Field(
        description="Total token count: len(assembled_text.split()). "
        "Coordinate space for Phase 2 word offsets."
    )
    text_layers: list[TextLayerSegment] = Field(
        description="Layer attribution rebased to assembled_text offsets (§4.6). "
        "Every character covered by exactly one segment."
    )
    footnotes: list[Footnote] = Field(
        default_factory=list,
        description="Footnotes from constituent content units, deduplicated by ref_marker",
    )
    content_flags: ContentFlags = Field(
        description="OR-aggregate across all constituent content units"
    )
    physical_pages: list[PhysicalPage] = Field(
        description="Physical page records from all constituent content units"
    )
    structural_format: StructuralFormat = Field(
        description="Inherited from manifest structural_format"
    )
    heading_alignment_ok: bool = Field(
        description="Whether division heading aligns with assembled text (§4.8)"
    )
    assembly_metadata: AssemblyMetadata
    merge_history: Optional[list[str]] = Field(
        None,
        description="Original div_id values merged to form this chunk. "
        "Null for unmerged chunks.",
    )
    split_info: Optional[SplitInfo] = Field(
        None,
        description="Split provenance. Null for unsplit chunks.",
    )

    @model_validator(mode="after")
    def check_split_chunk_id(self) -> AssembledChunk:
        """I-AC-5: split_info present -> chunk_id ends with _chunk_{index}."""
        if self.split_info is not None:
            expected_suffix = f"_chunk_{self.split_info.chunk_index}"
            if not self.chunk_id.endswith(expected_suffix):
                raise ValueError(
                    f"I-AC-5: chunk_id '{self.chunk_id}' must end with "
                    f"'{expected_suffix}'"
                )
        return self

    @model_validator(mode="after")
    def check_merge_history(self) -> AssembledChunk:
        """I-AC-6: merge_history present -> len >= 2 and first == div_id."""
        if self.merge_history is not None:
            if len(self.merge_history) < 2:
                raise ValueError(
                    f"I-AC-6: merge_history has {len(self.merge_history)} "
                    f"entries, need >= 2"
                )
            if self.merge_history[0] != self.div_id:
                raise ValueError(
                    f"I-AC-6: merge_history[0] '{self.merge_history[0]}' != "
                    f"div_id '{self.div_id}'"
                )
        return self

    @model_validator(mode="after")
    def check_mutual_exclusion(self) -> AssembledChunk:
        """I-AC-7: merge_history and split_info are mutually exclusive."""
        if self.merge_history is not None and self.split_info is not None:
            raise ValueError(
                "I-AC-7: merge_history and split_info are mutually exclusive"
            )
        return self


class ClassifiedSegment(BaseModel):
    """Phase 2a output: a classified text span (SPEC §2.3.3).

    A contiguous span of text within an AssembledChunk that serves a single
    scholarly function. Word offsets are post-normalization (§5.4).
    6 fields.
    """

    segment_index: int = Field(description="0-based index within chunk classification")
    start_word: int = Field(
        description="0-based inclusive start in assembled_text tokens"
    )
    end_word: int = Field(
        description="0-based inclusive end in assembled_text tokens"
    )
    text_snippet: str = Field(description="First 50 chars of segment's text")
    scholarly_function: ScholarlyFunction
    confidence: float = Field(ge=0.0, le=1.0)


class TeachingUnit(BaseModel):
    """Phase 2b output: a self-contained teaching unit (SPEC §2.3.4).

    Groups one or more ClassifiedSegments into the smallest segment of text
    a student can study and learn something complete from.
    10 fields.
    """

    unit_index: int = Field(description="0-based index within chunk grouping")
    segment_indices: list[int] = Field(
        default_factory=list,
        description="segment_index values of constituent ClassifiedSegments. "
        "Must be contiguous ascending.",
    )
    start_word: int = Field(
        description="0-based inclusive start in assembled_text tokens"
    )
    end_word: int = Field(
        description="0-based inclusive end in assembled_text tokens"
    )
    text_snippet: str = Field(description="First 80 chars of unit's text")
    primary_function: ScholarlyFunction
    secondary_functions: list[ScholarlyFunction] = Field(default_factory=list)
    description_arabic: str = Field(
        description="Brief Arabic description (target: 5-35 Arabic words)"
    )
    self_containment: SelfContainmentLevel
    self_containment_notes: Optional[str] = Field(
        None,
        description="What context is missing. Required when PARTIAL or DEPENDENT, "
        "must be null when FULL (I-TU-6, I-TU-7).",
    )

    @model_validator(mode="after")
    def check_self_containment_notes(self) -> TeachingUnit:
        """I-TU-6/I-TU-7: self_containment <-> self_containment_notes consistency."""
        if self.self_containment == SelfContainmentLevel.FULL:
            if self.self_containment_notes is not None:
                raise ValueError(
                    "I-TU-6: FULL self_containment -> "
                    "self_containment_notes must be None"
                )
        else:
            if not self.self_containment_notes:
                raise ValueError(
                    f"I-TU-7: {self.self_containment.value} self_containment -> "
                    f"self_containment_notes must be present and non-empty"
                )
        return self


# ═══════════════════════════════════════════════════════════════════
# Output Type — ExcerptRecord
# ═══════════════════════════════════════════════════════════════════


class ExcerptRecord(BaseModel):
    """The excerpting engine's final output (SPEC §2.2).

    One ExcerptRecord per teaching unit. Contains all TeachingUnit fields
    plus Phase 3 enrichment: attribution, topic, evidence, cross-references.
    33 fields across 7 categories. Invariants I-ER-1 through I-ER-7.
    """

    # ── Identification (6) ─────────────────────────────────────────
    excerpt_id: str = Field(
        description="Globally unique. Format: "
        "exc_{source_id}_{div_id}_{chunk_index}_{unit_index} (§7.1 F-DET-1)"
    )
    source_id: str
    div_id: str
    chunk_index: int = Field(
        description="0 for unsplit chunks. "
        "For split chunks: split_info.chunk_index (§2.2.2)"
    )
    unit_index: int
    div_path: list[str] = Field(
        description="Heading hierarchy from root to this division, root-first "
        "(§7.1 F-DET-7)"
    )

    # ── Text (6) ──────────────────────────────────────────────────
    primary_text: str = Field(
        description="Extracted from assembled_text via word offsets (F-DET-2). "
        "Never modified after extraction. "
        "Substring: ' '.join(assembled_text.split()[start_word:end_word+1])"
    )
    text_snippet: str = Field(description="First 80 chars of this unit's text")
    start_word: int = Field(
        description="0-based inclusive start in assembled_text tokens"
    )
    end_word: int = Field(
        description="0-based inclusive end in assembled_text tokens"
    )
    segment_indices: list[int] = Field(default_factory=list)
    physical_pages: Optional[PageRange] = None

    # ── Classification (4) ────────────────────────────────────────
    primary_function: ScholarlyFunction
    secondary_functions: list[ScholarlyFunction] = Field(default_factory=list)
    content_types: list[ScholarlyFunction] = Field(
        default_factory=list,
        description="Deduplicated set of all scholarly functions (§7.1 F-DET-4)",
    )
    description_arabic: str = Field(
        description="Brief Arabic description (5-35 Arabic words)"
    )

    # ── Self-containment (3) ──────────────────────────────────────
    self_containment: SelfContainmentLevel
    self_containment_notes: Optional[str] = None
    context_hint: Optional[str] = None

    # ── Attribution (5) ───────────────────────────────────────────
    primary_author_layer: AuthorAttribution = Field(
        description="Must have non-null layer_id and author_id (I-ER-5)"
    )
    attribution_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Null for deterministic LA-1/2/4. "
        "0.67 for 2-of-3 consensus (LA-3). "
        "0.0 for all-3-disagree (EX-G-001).",
    )
    quoted_scholars: list[ScholarAttribution] = Field(default_factory=list)
    school: Optional[str]  # DD8 Pattern 1: required=yes, nullable, NO default
    school_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

    # ── Topic/taxonomy (2) ────────────────────────────────────────
    excerpt_topic: list[str] = Field(
        description="1-3 Arabic topic keywords. "
        "Empty only when llm_enrichment_failed."
    )
    terminology_variants: list[TermVariant] = Field(default_factory=list)

    # ── Evidence/references (4) ───────────────────────────────────
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    takhrij_data: Optional[list[TakhrijEntry]] = None
    cross_references: list[CrossReference] = Field(default_factory=list)
    footnotes_relevant: list[Footnote] = Field(default_factory=list)

    # ── Metadata/flags (3) ────────────────────────────────────────
    consensus_metadata: Optional[ConsensusRecord] = None
    gate_flags: list[str] = Field(
        default_factory=list,
        description="EX-G-* codes that triggered. Empty if no gates triggered.",
    )
    review_flags: list[str] = Field(
        default_factory=list,
        description="Operational issue flags. Known: llm_enrichment_failed, "
        "school_consensus_disagreement, attribution_consensus_escalated, "
        "decontextualization_risk (§2.2.2), verification_skipped (§2.2.2).",
    )

    @model_validator(mode="after")
    def check_self_containment_consistency(self) -> ExcerptRecord:
        """I-ER-4: self-containment level <-> notes <-> context_hint consistency."""
        if self.self_containment == SelfContainmentLevel.FULL:
            if self.self_containment_notes is not None:
                raise ValueError(
                    "I-ER-4: FULL -> self_containment_notes must be None"
                )
            if self.context_hint is not None:
                raise ValueError("I-ER-4: FULL -> context_hint must be None")
        elif self.self_containment == SelfContainmentLevel.PARTIAL:
            if not self.self_containment_notes:
                raise ValueError(
                    "I-ER-4: PARTIAL -> self_containment_notes required"
                )
            if (
                self.context_hint is None
                and "llm_enrichment_failed" not in self.review_flags
            ):
                raise ValueError(
                    "I-ER-4: PARTIAL -> context_hint required "
                    "unless llm_enrichment_failed in review_flags"
                )
        elif self.self_containment == SelfContainmentLevel.DEPENDENT:
            if not self.self_containment_notes:
                raise ValueError(
                    "I-ER-4: DEPENDENT -> self_containment_notes required"
                )
            if self.context_hint is not None:
                raise ValueError(
                    "I-ER-4: DEPENDENT -> context_hint must be None"
                )
        return self

    @model_validator(mode="after")
    def check_attribution_completeness(self) -> ExcerptRecord:
        """I-ER-5: primary_author_layer has non-null layer_id and author_id."""
        if not self.primary_author_layer.layer_id:
            raise ValueError(
                "I-ER-5: primary_author_layer.layer_id must be non-null/non-empty"
            )
        if not self.primary_author_layer.author_id:
            raise ValueError(
                "I-ER-5: primary_author_layer.author_id must be non-null/non-empty"
            )
        return self


# ═══════════════════════════════════════════════════════════════════
# LLM Response Schemas
# ═══════════════════════════════════════════════════════════════════


class ResolvedScholar(BaseModel):
    """LLM-resolved scholar reference (SPEC §7.2.4)."""

    mention_text: str
    resolved_name: Optional[str] = None
    role: str = Field(
        description="One of: quoted_opinion, classification_frame, refuted_position"
    )
    confidence: float = Field(ge=0.0, le=1.0)


class UnitEnrichment(BaseModel):
    """Per-unit LLM enrichment response (SPEC §7.2.4).

    CRITICAL optionality differences from ExcerptRecord:
    - takhrij_data: list[TakhrijEntry] default [] (NOT nullable)
      vs ExcerptRecord Optional[list[TakhrijEntry]] = None
    - school_confidence: required=yes (no default)
      vs ExcerptRecord required=no (default None)
    """

    unit_index: int
    excerpt_topic: list[str] = Field(description="1-3 Arabic topic keywords")
    school: Optional[str]  # DD8 Pattern 1: required=yes, nullable
    school_confidence: Optional[float] = Field(
        ge=0.0, le=1.0, description="Null when school is null"
    )  # DD8 Pattern 1: required=yes, nullable
    resolved_scholars: list[ResolvedScholar]
    takhrij_data: list[TakhrijEntry] = Field(
        default_factory=list,
        description="Present only for units with hadith content. "
        "NOT nullable — empty list, not None.",
    )
    terminology_variants: list[TermVariant]
    cross_references: list[CrossReference]
    context_hint: Optional[str] = Field(
        description="Non-null only when self_containment is PARTIAL"
    )  # DD8 Pattern 1: required=yes, nullable


class EnrichmentResult(BaseModel):
    """Top-level LLM enrichment response (SPEC §7.2.4)."""

    enrichments: list[UnitEnrichment]
    total_units: int


class ClassificationResult(BaseModel):
    """Phase 2a LLM classification response (SPEC §5.2.4)."""

    segments: list[ClassifiedSegment]
    total_segments: int


class ExtractionResult(BaseModel):
    """Phase 2b LLM grouping response (SPEC §5.3.4)."""

    teaching_units: list[TeachingUnit]
    total_units: int
    notes: Optional[str] = None


class VerificationItem(BaseModel):
    """One verification assessment (SPEC §7.3.2)."""

    item_index: int
    agrees: bool
    alternative: Optional[str] = None
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Verifier confidence in own assessment. "
        "Used for school_confidence computation (§7.3.3).",
    )
    reasoning: str


class VerificationResult(BaseModel):
    """Top-level verification response (SPEC §7.3.2)."""

    items: list[VerificationItem]


# ═══════════════════════════════════════════════════════════════════
# Error Codes
# ═══════════════════════════════════════════════════════════════════


class ExcerptingErrorCodes:
    """All 28 error codes from SPEC §8.1.

    String constants, not an Enum — error codes are logged as strings,
    compared as strings, and never used as Pydantic field types.
    """

    # Phase 1 — Assembly (EX-A-*)
    EX_A_002 = "EX-A-002"  # Empty content unit range
    EX_A_003 = "EX-A-003"  # Layer rebasing gap
    EX_A_004 = "EX-A-004"  # Layer segment overflow
    EX_A_005 = "EX-A-005"  # Duplicate footnote ref_marker
    EX_A_006 = "EX-A-006"  # Heading misalignment
    EX_A_010 = "EX-A-010"  # Empty division tree
    EX_A_011 = "EX-A-011"  # Content unit not found
    EX_A_012 = "EX-A-012"  # Diacritic-mismatched snippet (§5.4.1 step d2)

    # Phase 2 — Classification and Grouping (EX-C-*)
    EX_C_001 = "EX-C-001"  # Classification LLM failed
    EX_C_002 = "EX-C-002"  # Grouping LLM failed
    EX_C_003 = "EX-C-003"  # Offset normalization failed
    EX_C_004 = "EX-C-004"  # Segment coverage violated
    EX_C_005 = "EX-C-005"  # Unit coverage violated

    # Phase 3 — Metadata Enrichment (EX-M-*)
    EX_M_001 = "EX-M-001"  # Attribution ambiguous (LA-3)
    EX_M_002 = "EX-M-002"  # LLM enrichment failed
    EX_M_003 = "EX-M-003"  # School disagreement
    EX_M_004 = "EX-M-004"  # Null primary_author after Phase 3
    EX_M_005 = "EX-M-005"  # Topic count outside 1-3
    EX_M_006 = "EX-M-006"  # Self-containment metadata inconsistency
    EX_M_007 = "EX-M-007"  # Invalid Quran reference
    EX_M_008 = "EX-M-008"  # Gate entry not written (CRITICAL)
    EX_M_009 = "EX-M-009"  # Footnote offset outside excerpt range
    EX_M_010 = "EX-M-010"  # Unknown content type

    # Validation (EX-V-*)
    EX_V_001 = "EX-V-001"  # Phase 1 self-validation failed
    EX_V_002 = "EX-V-002"  # Primary text integrity check failed

    # Human Gate Triggers (EX-G-*)
    EX_G_001 = "EX-G-001"  # 3 models all disagree on attribution
    EX_G_002 = "EX-G-002"  # DEPENDENT self-containment
    EX_G_003 = "EX-G-003"  # School conflict with source metadata


# ═══════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════


class ExcerptingConfig(BaseModel):
    """Static configuration parameters (SPEC §8.3).

    CLASSIFY_MAX_TOKENS is dynamic (scales with input per §5.5.1)
    and is NOT included here.
    """

    # Phase 1
    TINY_DIVISION_WORDS: int = 50
    OVERSIZED_DIVISION_WORDS: int = 5000

    # Phase 2
    CLASSIFY_MODEL: str = "anthropic/claude-opus-4.6"
    GROUP_MODEL: str = "anthropic/claude-opus-4.6"
    LLM_TEMPERATURE: float = 0.0
    GROUP_MAX_TOKENS: int = 16384
    RETRY_COUNT: int = 2
    TIMEOUT_SECONDS: int = 120

    # Phase 3
    ENRICH_MODEL: str = "anthropic/claude-opus-4.6"
    ENRICH_MAX_TOKENS: int = 16384
    VERIFY_MODEL: str = "openai/gpt-4.1"
    VERIFY_MAX_TOKENS: int = 8192
    ESCALATION_MODEL: str = "cohere/command-a-03-2025"

    # Human gates
    GATE_ON_DEPENDENT: bool = True
    GATE_ON_ATTRIBUTION_DISAGREEMENT: bool = True
    GATE_ON_SCHOOL_CONFLICT: bool = True

    # Telemetry
    LOG_LEVEL: str = "INFO"
    TELEMETRY_ENABLED: bool = True


# ═══════════════════════════════════════════════════════════════════
# Invariant Validators — Standalone Functions
# ═══════════════════════════════════════════════════════════════════


def _count_arabic_words(text: str) -> int:
    """Count whitespace-delimited tokens containing >=1 Arabic character (U+0600-U+06FF)."""
    return sum(
        1
        for token in text.split()
        if any("\u0600" <= c <= "\u06FF" for c in token)
    )


def validate_ac_invariants(chunk: AssembledChunk) -> None:
    """Validate AssembledChunk invariants I-AC-1, I-AC-5, I-AC-6, I-AC-7.

    I-AC-2 (layer coverage) is checked separately via validate_layer_coverage.
    I-AC-3 and I-AC-4 require runtime data not available in contracts.
    """
    # I-AC-1: word_count and total_tokens consistency
    expected_total = len(chunk.assembled_text.split())
    if chunk.total_tokens != expected_total:
        raise ValueError(
            f"I-AC-1: total_tokens {chunk.total_tokens} != "
            f"len(assembled_text.split()) {expected_total}"
        )
    expected_words = _count_arabic_words(chunk.assembled_text)
    if chunk.word_count != expected_words:
        raise ValueError(
            f"I-AC-1: word_count {chunk.word_count} != "
            f"Arabic word count {expected_words}"
        )

    # I-AC-5: split chunk_id format (defense in depth with model_validator)
    if chunk.split_info is not None:
        expected_suffix = f"_chunk_{chunk.split_info.chunk_index}"
        if not chunk.chunk_id.endswith(expected_suffix):
            raise ValueError(
                f"I-AC-5: chunk_id '{chunk.chunk_id}' must end with "
                f"'{expected_suffix}'"
            )

    # I-AC-6: merge_history validity (defense in depth)
    if chunk.merge_history is not None:
        if len(chunk.merge_history) < 2:
            raise ValueError(
                f"I-AC-6: merge_history has {len(chunk.merge_history)} "
                f"entries, need >= 2"
            )
        if chunk.merge_history[0] != chunk.div_id:
            raise ValueError(
                f"I-AC-6: merge_history[0] '{chunk.merge_history[0]}' != "
                f"div_id '{chunk.div_id}'"
            )

    # I-AC-7: mutual exclusion (defense in depth)
    if chunk.merge_history is not None and chunk.split_info is not None:
        raise ValueError(
            "I-AC-7: merge_history and split_info are mutually exclusive"
        )


def validate_layer_coverage(
    text_layers: list[TextLayerSegment], assembled_text_len: int
) -> None:
    """Validate I-AC-2: text_layers cover [0, assembled_text_len) exactly."""
    if not text_layers:
        if assembled_text_len > 0:
            raise ValueError(
                f"I-AC-2: no text_layers but assembled_text has "
                f"{assembled_text_len} chars"
            )
        return

    sorted_layers = sorted(text_layers, key=lambda s: s.start)

    if sorted_layers[0].start != 0:
        raise ValueError(
            f"I-AC-2: first layer segment starts at "
            f"{sorted_layers[0].start}, expected 0"
        )

    for i in range(1, len(sorted_layers)):
        if sorted_layers[i].start != sorted_layers[i - 1].end:
            raise ValueError(
                f"I-AC-2: gap or overlap at position {i}: "
                f"previous ends at {sorted_layers[i - 1].end}, "
                f"next starts at {sorted_layers[i].start}"
            )

    if sorted_layers[-1].end != assembled_text_len:
        raise ValueError(
            f"I-AC-2: last layer segment ends at {sorted_layers[-1].end}, "
            f"expected {assembled_text_len}"
        )


def validate_cs_invariants(
    segments: list[ClassifiedSegment], total_tokens: int
) -> None:
    """Validate ClassifiedSegment invariants I-CS-1 through I-CS-6."""
    if not segments:
        if total_tokens > 0:
            raise ValueError("I-CS-5: no segments but total_tokens > 0")
        return

    for i, seg in enumerate(segments):
        # I-CS-1: segment_index matches position
        if seg.segment_index != i:
            raise ValueError(
                f"I-CS-1: segment at position {i} has "
                f"segment_index {seg.segment_index}"
            )
        # I-CS-6: confidence in range (defense in depth with Field constraint)
        if not 0.0 <= seg.confidence <= 1.0:
            raise ValueError(
                f"I-CS-6: segment {i} confidence {seg.confidence} "
                f"outside [0.0, 1.0]"
            )

    # I-CS-3: first segment starts at 0
    if segments[0].start_word != 0:
        raise ValueError(
            f"I-CS-3: first segment start_word "
            f"{segments[0].start_word} != 0"
        )

    # I-CS-4: last segment ends at total_tokens - 1
    if segments[-1].end_word != total_tokens - 1:
        raise ValueError(
            f"I-CS-4: last segment end_word {segments[-1].end_word} "
            f"!= {total_tokens - 1}"
        )

    # I-CS-2: contiguous
    for i in range(1, len(segments)):
        if segments[i].start_word != segments[i - 1].end_word + 1:
            raise ValueError(
                f"I-CS-2: gap between segments {i - 1} and {i}: "
                f"end_word {segments[i - 1].end_word} -> "
                f"start_word {segments[i].start_word}"
            )

    # I-CS-5: full coverage (explicit check — implied by I-CS-2+3+4)
    covered = set()
    for seg in segments:
        covered.update(range(seg.start_word, seg.end_word + 1))
    expected = set(range(total_tokens))
    if covered != expected:
        missing = expected - covered
        extra = covered - expected
        raise ValueError(
            f"I-CS-5: coverage mismatch. Missing: {missing}, Extra: {extra}"
        )


def validate_tu_invariants(
    units: list[TeachingUnit],
    segments: list[ClassifiedSegment],
    total_tokens: int,
) -> None:
    """Validate TeachingUnit invariants I-TU-1 through I-TU-9.

    I-TU-8 (description_arabic word count 5-35) is WARNING only, not rejection.
    """
    if not units:
        if segments:
            raise ValueError("I-TU-3: no units but segments exist")
        return

    all_segment_indices: set[int] = set()

    for i, unit in enumerate(units):
        # I-TU-1: unit_index matches position
        if unit.unit_index != i:
            raise ValueError(
                f"I-TU-1: unit at position {i} has unit_index {unit.unit_index}"
            )

        # I-TU-2: segment_indices is contiguous ascending
        si = unit.segment_indices
        if not si:
            raise ValueError(f"I-TU-2: unit {i} has empty segment_indices")
        expected_si = list(range(si[0], si[0] + len(si)))
        if si != expected_si:
            raise ValueError(
                f"I-TU-2: unit {i} segment_indices {si} "
                f"not contiguous ascending (expected {expected_si})"
            )

        all_segment_indices.update(si)

        # I-TU-5: start_word/end_word match segment boundaries
        expected_start = segments[si[0]].start_word
        expected_end = segments[si[-1]].end_word
        if unit.start_word != expected_start:
            raise ValueError(
                f"I-TU-5: unit {i} start_word {unit.start_word} != "
                f"segments[{si[0]}].start_word {expected_start}"
            )
        if unit.end_word != expected_end:
            raise ValueError(
                f"I-TU-5: unit {i} end_word {unit.end_word} != "
                f"segments[{si[-1]}].end_word {expected_end}"
            )

        # I-TU-6/I-TU-7: self_containment <-> notes (defense in depth)
        if unit.self_containment == SelfContainmentLevel.FULL:
            if unit.self_containment_notes is not None:
                raise ValueError(
                    f"I-TU-6: unit {i} is FULL but "
                    f"self_containment_notes is not None"
                )
        else:
            if not unit.self_containment_notes:
                raise ValueError(
                    f"I-TU-7: unit {i} is {unit.self_containment.value} "
                    f"but self_containment_notes is missing or empty"
                )

        # I-TU-8: description_arabic word count (WARNING only)
        arabic_word_count = _count_arabic_words(unit.description_arabic)
        if not 5 <= arabic_word_count <= 35:
            logger.warning(
                "I-TU-8: unit %d description_arabic has %d Arabic words "
                "(expected 5-35): %.50s",
                i,
                arabic_word_count,
                unit.description_arabic,
            )

        # I-TU-9: primary_function in constituent segments
        segment_functions = {
            segments[idx].scholarly_function for idx in si
        }
        if unit.primary_function not in segment_functions:
            raise ValueError(
                f"I-TU-9: unit {i} primary_function "
                f"{unit.primary_function.value} not in constituent "
                f"segments' functions: "
                f"{[f.value for f in segment_functions]}"
            )

    # I-TU-4: units contiguous in word space
    for i in range(1, len(units)):
        if units[i].start_word != units[i - 1].end_word + 1:
            raise ValueError(
                f"I-TU-4: gap between units {i - 1} and {i}: "
                f"end_word {units[i - 1].end_word} -> "
                f"start_word {units[i].start_word}"
            )

    # I-TU-3: every segment assigned to exactly one unit
    expected_indices = set(range(len(segments)))
    if all_segment_indices != expected_indices:
        missing = expected_indices - all_segment_indices
        extra = all_segment_indices - expected_indices
        raise ValueError(
            f"I-TU-3: segment assignment mismatch. "
            f"Missing: {missing}, Extra: {extra}"
        )


def validate_er_invariants(record: ExcerptRecord) -> None:
    """Validate ExcerptRecord invariants I-ER-4, I-ER-5.

    Defense in depth — same checks as model_validators on ExcerptRecord.
    """
    # I-ER-4: self-containment consistency
    if record.self_containment == SelfContainmentLevel.FULL:
        if record.self_containment_notes is not None:
            raise ValueError(
                "I-ER-4: FULL -> self_containment_notes must be None"
            )
        if record.context_hint is not None:
            raise ValueError("I-ER-4: FULL -> context_hint must be None")
    elif record.self_containment == SelfContainmentLevel.PARTIAL:
        if not record.self_containment_notes:
            raise ValueError(
                "I-ER-4: PARTIAL -> self_containment_notes required"
            )
        if (
            record.context_hint is None
            and "llm_enrichment_failed" not in record.review_flags
        ):
            raise ValueError(
                "I-ER-4: PARTIAL -> context_hint required "
                "unless llm_enrichment_failed in review_flags"
            )
    elif record.self_containment == SelfContainmentLevel.DEPENDENT:
        if not record.self_containment_notes:
            raise ValueError(
                "I-ER-4: DEPENDENT -> self_containment_notes required"
            )
        if record.context_hint is not None:
            raise ValueError(
                "I-ER-4: DEPENDENT -> context_hint must be None"
            )

    # I-ER-5: primary_author_layer completeness
    if not record.primary_author_layer.layer_id:
        raise ValueError(
            "I-ER-5: primary_author_layer.layer_id must be "
            "non-null/non-empty"
        )
    if not record.primary_author_layer.author_id:
        raise ValueError(
            "I-ER-5: primary_author_layer.author_id must be "
            "non-null/non-empty"
        )


def validate_er_collection_invariants(
    records: list[ExcerptRecord],
) -> None:
    """Validate collection-level invariants I-ER-1 (uniqueness), I-ER-3 (ordering)."""
    if not records:
        return

    # I-ER-1: no duplicate excerpt_id
    seen_ids: set[str] = set()
    for record in records:
        if record.excerpt_id in seen_ids:
            raise ValueError(
                f"I-ER-1: duplicate excerpt_id '{record.excerpt_id}'"
            )
        seen_ids.add(record.excerpt_id)

    # I-ER-3: ordering by (div_id, chunk_index, unit_index)
    for i in range(1, len(records)):
        prev = records[i - 1]
        curr = records[i]
        prev_key = (prev.div_id, prev.chunk_index, prev.unit_index)
        curr_key = (curr.div_id, curr.chunk_index, curr.unit_index)
        if curr_key <= prev_key:
            raise ValueError(
                f"I-ER-3: records not in order at position {i}: "
                f"{prev_key} should come before {curr_key}"
            )
