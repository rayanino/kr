"""Excerpting Engine Contracts — Machine-readable schemas derived from SPEC.md §3.

These Pydantic models define the DRAFT EXCERPT STREAM — the artifact that
downstream engines (taxonomy, synthesizing) consume.

When SPEC.md §3 and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────


class LifecycleStage(str, Enum):
    """Excerpt lifecycle stages (SPEC §3)."""
    DRAFT = "draft"
    REVIEWED = "reviewed"
    PLACED = "placed"
    FLAGGED = "flagged"


class ContextAtomRole(str, Enum):
    """Role of a context atom in the excerpt (SPEC §3)."""
    PREREQUISITE = "prerequisite"
    EVIDENCE = "evidence"
    CLASSIFICATION_FRAME = "classification_frame"
    TRANSITION = "transition"
    EXAMPLE = "example"
    EDITORIAL = "editorial"


class QuotedScholarRole(str, Enum):
    """Role of a quoted/referenced scholar within the excerpt (SPEC §3)."""
    QUOTED_OPINION = "quoted_opinion"
    CITED_SOURCE = "cited_source"
    REFUTED_POSITION = "refuted_position"
    REPORTED_CONSENSUS = "reported_consensus"
    TEACHER_REFERENCE = "teacher_reference"


class EvidenceType(str, Enum):
    """Types of scholarly evidence (SPEC §4.A.4, DOMAIN.md)."""
    QURAN = "quran"
    HADITH = "hadith"
    IJMA = "ijma"
    QIYAS = "qiyas"
    COMPANION_STATEMENT = "companion_statement"
    RATIONAL = "rational"
    ISTISHAB = "istishab"


class ExcerptKind(str, Enum):
    """The kind of content this excerpt represents (SPEC §3)."""
    TEACHING = "teaching"
    EXERCISE = "exercise"
    APPARATUS = "apparatus"


class ArgumentRole(str, Enum):
    """Argumentative discourse role of the excerpt (SPEC §4.B.1)."""
    MASALA_FORMULATION = "masala_formulation"
    POSITION_STATEMENT = "position_statement"
    EVIDENCE_PRESENTATION = "evidence_presentation"
    DISCUSSION_REFUTATION = "discussion_refutation"
    WEIGHING_PREFERENCE = "weighing_preference"
    CONCLUSION_SUMMARY = "conclusion_summary"
    DEFINITION_EXPOSITION = "definition_exposition"
    EXAMPLE_APPLICATION = "example_application"
    MIXED = "mixed"


class DialogueType(str, Enum):
    """Type of scholarly dialogue between excerpts (SPEC §4.B.4)."""
    AGREES = "agrees"
    DISAGREES = "disagrees"
    REFINES = "refines"
    SUPERSEDES = "supersedes"
    CITES = "cites"
    SHARED_EVIDENCE = "shared_evidence"


class SemanticDuplicateRelation(str, Enum):
    """Relationship between semantically similar excerpts (SPEC §4.B.2)."""
    VERBATIM_DUPLICATE = "verbatim_duplicate"
    SHARED_QUOTATION = "shared_quotation"
    PARAPHRASE = "paraphrase"
    RELATED_NOT_DUPLICATE = "related_not_duplicate"


class RepairSuggestionType(str, Enum):
    """Type of self-containment repair suggestion (SPEC §4.B.5)."""
    ADD_CONTEXT_ATOM = "add_context_atom"
    MERGE_WITH_ADJACENT = "merge_with_adjacent"
    FLAG_PASSAGING_ERROR = "flag_passaging_error"
    FLAG_MISSING_SOURCE_CONTEXT = "flag_missing_source_context"
    GENERATE_CONTEXT_NOTE = "generate_context_note"


# ──────────────────────────────────────────────────────────────────
# Sub-models
# ──────────────────────────────────────────────────────────────────


class ContextAtom(BaseModel):
    """A context atom included for self-containment (SPEC §3)."""
    atom_id: str
    role: ContextAtomRole


class QuotedScholar(BaseModel):
    """A scholar quoted or referenced within the excerpt (SPEC §3)."""
    canonical_id: Optional[str] = None
    name_text: str = Field(description="Name as it appears in the text")
    role: QuotedScholarRole
    confidence: float = Field(ge=0.0, le=1.0)


class QuranDetail(BaseModel):
    """Quran reference detail (SPEC §3)."""
    surah: int = Field(ge=1, le=114)
    ayah_start: int = Field(ge=1)
    ayah_end: int = Field(ge=1)


class HadithDetail(BaseModel):
    """Hadith reference detail (SPEC §3)."""
    collection: Optional[str] = None
    hadith_number: Optional[str] = None
    grade: Optional[str] = None
    grade_source: Optional[str] = None


class EvidenceRef(BaseModel):
    """An evidence reference within the excerpt (SPEC §4.A.4)."""
    evidence_type: EvidenceType
    text_snippet: str = Field(max_length=200)
    quran_detail: Optional[QuranDetail] = None
    hadith_detail: Optional[HadithDetail] = None
    source_atom_id: str


class TakhrijEntry(BaseModel):
    """Hadith source-tracing data from editor footnotes (SPEC §4.A.4)."""
    hadith_ref: str
    collections: list[str] = Field(default_factory=list)
    numbers: list[str] = Field(default_factory=list)
    grade: Optional[str] = None
    grade_source: Optional[str] = None


class TerminologyVariant(BaseModel):
    """A term that may have alternative names across sources (SPEC §3)."""
    term_in_text: str
    standard_term: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class PhysicalPages(BaseModel):
    """Physical location in the source edition (SPEC §3)."""
    volume: Optional[int] = None
    start_page: Optional[str] = None
    end_page: Optional[str] = None


class ProcessingMetadata(BaseModel):
    """Provenance information for the excerpt (SPEC §3)."""
    engine_version: str
    model_used: str
    consensus_used: bool
    processing_timestamp: str = Field(
        description="ISO 8601 datetime"
    )


# ──────────────────────────────────────────────────────────────────
# §4.B.1 — Argument map segment
# ──────────────────────────────────────────────────────────────────


class ArgumentMapSegment(BaseModel):
    """A segment of the internal argument map (SPEC §4.B.1)."""
    start_atom_id: str
    end_atom_id: str
    role: ArgumentRole


# ──────────────────────────────────────────────────────────────────
# §4.B.2 — Semantic duplicate link
# ──────────────────────────────────────────────────────────────────


class SemanticDuplicateLink(BaseModel):
    """Link to a semantically similar excerpt in another source (SPEC §4.B.2)."""
    target_excerpt_id: str
    target_source_id: str
    relationship: SemanticDuplicateRelation
    confidence: float = Field(ge=0.0, le=1.0)
    primary_source: Optional[str] = Field(
        default=None,
        description="source_id of the 'primary' source for this content"
    )


# ──────────────────────────────────────────────────────────────────
# §4.B.3 — Argument completeness
# ──────────────────────────────────────────────────────────────────


class ArgumentCompleteness(BaseModel):
    """Assessment of whether the excerpt's argument is complete (SPEC §4.B.3)."""
    score: float = Field(ge=0.0, le=1.0)
    missing_elements: list[str] = Field(default_factory=list)
    continuation_detected: bool = False
    continuation_passage_id: Optional[str] = None
    notes: str = ""


# ──────────────────────────────────────────────────────────────────
# §4.B.4 — Dialogue link
# ──────────────────────────────────────────────────────────────────


class DialogueLink(BaseModel):
    """Link to another excerpt in a scholarly dialogue (SPEC §4.B.4)."""
    target_excerpt_id: str
    dialogue_type: DialogueType
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str = Field(description="Brief explanation of why this link exists")


# ──────────────────────────────────────────────────────────────────
# §4.B.5 — Repair suggestion
# ──────────────────────────────────────────────────────────────────


class RepairSuggestion(BaseModel):
    """Self-containment repair suggestion (SPEC §4.B.5)."""
    suggestion_type: RepairSuggestionType
    detail: str
    target_atom_id: Optional[str] = None
    generated_context: Optional[str] = Field(
        default=None,
        description="Brief Arabic context note (≤50 words), "
        "grounding_type: analytical. NEVER presented as source text."
    )


# ──────────────────────────────────────────────────────────────────
# Main excerpt record
# ──────────────────────────────────────────────────────────────────


class ExcerptRecord(BaseModel):
    """A single excerpt record in the draft excerpt stream (SPEC §3).

    Written to: library/sources/{source_id}/excerpts/excerpts.jsonl
    One record per line.
    """

    # Identity
    schema_version: str = Field(default="excerpt_v2.0")
    excerpt_id: str = Field(
        description="Format: exc_{source_id}_{zero_padded_sequence}"
    )
    source_id: str
    passage_id: str
    lifecycle_stage: LifecycleStage = Field(default=LifecycleStage.DRAFT)

    # Atom composition
    atom_ids: list[str] = Field(
        description="All atom IDs in reading order (core + context)"
    )
    core_atom_ids: list[str] = Field(
        description="Atoms that substantively address the topic"
    )
    context_atom_ids: list[ContextAtom] = Field(default_factory=list)

    # Text fields
    primary_text: str = Field(
        description="Verbatim Arabic text from atom_text concatenation. "
        "Never edited (D-004)."
    )
    derived_normalized_text: str = Field(
        description="Normalized for search/dedup: diacritics stripped, "
        "alef/teh normalized, whitespace standardized."
    )

    # Attribution
    primary_author_id: Optional[str] = None
    primary_author_name: Optional[str] = None
    quoted_scholars: list[QuotedScholar] = Field(default_factory=list)
    source_layer: str = Field(
        description="Dominant authorial layer: matn, sharh, hashiyah, tahqiq, footnote"
    )

    # Classification
    excerpt_topic: str = Field(
        description="Concise Arabic topic description"
    )
    proposed_leaf: Optional[str] = Field(
        default=None,
        description="Proposed taxonomy leaf path, e.g. nahw/المبتدأ_والخبر/تعريف_المبتدأ"
    )
    proposed_leaf_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    science_id: str
    school: Optional[str] = None
    school_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    content_types: list[str] = Field(
        default_factory=list,
        description="Aggregated from atoms' scholarly_function values"
    )
    excerpt_kind: ExcerptKind = Field(default=ExcerptKind.TEACHING)

    # Evidence and references
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    takhrij_data: list[TakhrijEntry] = Field(default_factory=list)
    terminology_variants: list[TerminologyVariant] = Field(default_factory=list)

    # Quality
    self_containment_score: float = Field(ge=0.0, le=1.0)
    self_containment_notes: Optional[str] = None
    excerpt_confidence: float = Field(ge=0.0, le=1.0)

    # Source reference
    physical_pages: PhysicalPages = Field(default_factory=PhysicalPages)
    division_path: list[str] = Field(default_factory=list)

    # Review flags
    review_flags: list[str] = Field(default_factory=list)

    # Provenance
    processing_metadata: ProcessingMetadata

    # §4.B.1 — Argumentative discourse mapping
    argument_role: Optional[ArgumentRole] = None
    argument_role_confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0
    )
    argument_map: Optional[list[ArgumentMapSegment]] = Field(
        default=None,
        description="Non-null for excerpts with ≥5 core atoms"
    )

    # §4.B.2 — Cross-source semantic deduplication
    semantic_duplicates: Optional[list[SemanticDuplicateLink]] = Field(
        default=None,
        description="Null when deduplication has not run. "
        "Empty list when run but no duplicates found."
    )

    # §4.B.3 — Argument completeness
    argument_completeness: Optional[ArgumentCompleteness] = None

    # §4.B.4 — Scholarly dialogue links
    dialogue_links: Optional[list[DialogueLink]] = Field(
        default=None,
        description="Null during bulk loading. Populated during incremental processing."
    )

    # §4.B.5 — Self-containment repair suggestions
    repair_suggestions: Optional[list[RepairSuggestion]] = Field(
        default=None,
        description="Non-null only when self_containment_score < 0.7"
    )


# ──────────────────────────────────────────────────────────────────
# Excerpt stream — convenience wrapper
# ──────────────────────────────────────────────────────────────────


class ExcerptStream(BaseModel):
    """The complete excerpt stream for a source (SPEC §3).

    Logical wrapper — on disk this is excerpts.jsonl (one record per line).
    """
    source_id: str
    excerpts: list[ExcerptRecord] = Field(
        description="Ordered by excerpt_id. Globally monotonic. "
        "Non-overlapping atom assignments."
    )
