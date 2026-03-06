"""Atomization Engine Contracts — Machine-readable schemas derived from SPEC.md §3.

These Pydantic models define the ATOM STREAM — the artifact that downstream
engines (excerpting) consume.

When SPEC.md §3 and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────


class StructuralType(str, Enum):
    """Structural type — the physical shape of the text unit (SPEC §4.A.3)."""
    PROSE_SENTENCE = "prose_sentence"
    BONDED_CLUSTER = "bonded_cluster"
    HEADING = "heading"
    VERSE_LINE = "verse_line"
    LIST_ITEM = "list_item"
    TABLE_CELL = "table_cell"
    WHITESPACE_SEPARATOR = "whitespace_separator"


class ScholarlyFunction(str, Enum):
    """Scholarly function — the role the text plays in scholarly discourse (SPEC §4.A.3)."""
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


class SourceLayer(str, Enum):
    """Text layer attribution for multi-layer sources (SPEC §4.A.6)."""
    MATN = "matn"
    SHARH = "sharh"
    HASHIYAH = "hashiyah"
    TAHQIQ = "tahqiq"
    FOOTNOTE = "footnote"


class EmbeddedRefType(str, Enum):
    """Type of embedded content fragment within an atom (SPEC §3)."""
    QURAN_AYAH = "quran_ayah"
    HADITH_TEXT = "hadith_text"
    POETRY_LINE = "poetry_line"
    SCHOLARLY_QUOTE = "scholarly_quote"
    FORMULA = "formula"


class DetectionMethod(str, Enum):
    """How an embedded reference was detected (SPEC §4.A.4)."""
    PATTERN_MATCH = "pattern_match"
    CANONICAL_LOOKUP = "canonical_lookup"
    LLM_DETECTED = "llm_detected"


class AtomRelationType(str, Enum):
    """Typed relationships between atoms within a passage (SPEC §3)."""
    ILLUSTRATES = "illustrates"
    EVIDENCES = "evidences"
    CONDITIONS = "conditions"
    REFUTES = "refutes"
    CONTINUES = "continues"
    RESPONDS_TO = "responds_to"
    FOOTNOTE_FOR = "footnote_for"


class AttributionType(str, Enum):
    """Scholarly attribution type within an atom (SPEC §4.B.4)."""
    DIRECT = "direct"
    VIA_WORK = "via_work"
    SCHOOL_COLLECTIVE = "school_collective"
    ISNAD = "isnad"
    ANONYMOUS = "anonymous"
    SELF = "self"
    REFUTATION_TARGET = "refutation_target"


# ──────────────────────────────────────────────────────────────────
# Sub-models
# ──────────────────────────────────────────────────────────────────


class AnchorSpan(BaseModel):
    """Character offsets within passage_text (SPEC §3).

    Invariant: atom_text == passage_text[start:end]
    """
    start: int = Field(ge=0, description="Start char offset (inclusive)")
    end: int = Field(ge=0, description="End char offset (exclusive)")


class QuranRefDetail(BaseModel):
    """Detail for a Quran ayah reference (SPEC §3)."""
    surah: int = Field(ge=1, le=114)
    ayah: int = Field(ge=1)
    match_confidence: float = Field(ge=0.0, le=1.0)


class HadithRefDetail(BaseModel):
    """Detail for a hadith text reference (SPEC §3)."""
    collection: Optional[str] = None
    hadith_number: Optional[str] = None


class PoetryRefDetail(BaseModel):
    """Detail for a poetry line reference (SPEC §3)."""
    poet: Optional[str] = None
    diwan: Optional[str] = None


class ScholarlyQuoteRefDetail(BaseModel):
    """Detail for a scholarly quotation reference (SPEC §3)."""
    quoted_scholar: Optional[str] = None


class EmbeddedRef(BaseModel):
    """An embedded content fragment within an atom (SPEC §3)."""
    ref_type: EmbeddedRefType
    span_start: int = Field(ge=0, description="Start offset within atom_text")
    span_end: int = Field(ge=0, description="End offset within atom_text")
    ref_detail: Optional[
        QuranRefDetail | HadithRefDetail | PoetryRefDetail | ScholarlyQuoteRefDetail
    ] = None
    detection_method: DetectionMethod


class FootnoteRef(BaseModel):
    """Links an atom to a footnote (SPEC §3)."""
    ref_marker: str = Field(description="Footnote marker text, e.g. '1'")
    linked_footnote_atom_id: Optional[str] = Field(
        None,
        description="atom_id of the corresponding footnote atom"
    )


class AtomRelation(BaseModel):
    """A typed relationship between atoms within the same passage (SPEC §3)."""
    relation_type: AtomRelationType
    target_atom_id: str
    confidence: float = Field(ge=0.0, le=1.0)


class ScholarlyAttribution(BaseModel):
    """A scholarly attribution detected within an atom (SPEC §4.B.4).

    Identifies WHO is being quoted/cited/attributed and through what mechanism.
    Raw names — NOT canonical IDs. Downstream resolution is the excerpting
    engine's responsibility via the scholar authority model.
    """
    attributed_to: Optional[str] = Field(
        None,
        description="Raw scholar name, work reference, or school name. "
        "Null for anonymous attributions."
    )
    attribution_type: AttributionType
    work_reference: Optional[str] = Field(
        None, description="Work title for via_work type"
    )
    school_scope: Optional[str] = Field(
        None, description="School name for school_collective / anonymous with school context"
    )
    isnad_chain: Optional[list[str]] = Field(
        None,
        description="Ordered transmitter names for isnad type. Raw names, not canonical IDs."
    )
    confidence: float = Field(ge=0.0, le=1.0)
    marker_text: str = Field(
        description="Arabic text that triggered this detection, e.g. 'قال الشافعي'"
    )


# ──────────────────────────────────────────────────────────────────
# Primary output: Atom record
# ──────────────────────────────────────────────────────────────────


class AtomRecord(BaseModel):
    """One record in the atom stream (atoms.jsonl) — SPEC §3.

    Written to: library/sources/{source_id}/atoms/atoms.jsonl
    Each atom is the smallest indivisible unit of scholarly text.
    """
    schema_version: str = Field(default="atom_v2.0")
    atom_id: str = Field(
        description="Globally unique: atm_{source_id}_{zero_padded_sequence}"
    )
    passage_id: str = Field(description="Parent passage ID")
    source_id: str
    sequence_in_passage: int = Field(
        ge=0, description="Zero-based position within passage"
    )

    # Text and location
    atom_text: str = Field(
        min_length=1,
        description="Verbatim text from passage_text[start:end]. Never modified."
    )
    anchor_span: AnchorSpan

    # Two-tier type classification
    structural_type: StructuralType
    scholarly_function: Optional[ScholarlyFunction] = Field(
        None,
        description="Null only for heading and whitespace_separator"
    )
    function_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Confidence in scholarly_function. 1.0 for rule-based detections."
    )

    # Layer attribution
    source_layer: SourceLayer
    layer_author_id: Optional[str] = Field(
        None,
        description="canonical_id of the layer's author. Null if unidentified."
    )

    # Embedded content
    embedded_refs: list[EmbeddedRef] = Field(default_factory=list)

    # Footnote linkage
    footnote_source_index: Optional[int] = Field(
        None, ge=0,
        description="For footnote atoms (source_layer=='footnote'): zero-based index "
        "into the passage's footnotes array. Null for main text atoms."
    )
    footnote_refs: list[FootnoteRef] = Field(default_factory=list)

    # Intra-passage relationships
    atom_relations: list[AtomRelation] = Field(default_factory=list)

    # Scholarly attribution (§4.B.4)
    attributions: Optional[list[ScholarlyAttribution]] = Field(
        None,
        description="Present when enable_attribution_detection is true"
    )

    # Semantic fingerprints (§4.B.5)
    fingerprint_text_hash: Optional[str] = Field(
        None,
        description="SHA-256 of normalized atom text (Tier 1). 64 hex chars.",
        max_length=64, min_length=64
    )
    fingerprint_key_terms: Optional[list[str]] = Field(
        None,
        description="2-5 key Arabic terms (Tier 2). Normalized."
    )
    fingerprint_embedding: Optional[list[float]] = Field(
        None,
        description="Semantic embedding vector (Tier 3). "
        "Dimensions per config (default 256)."
    )

    # Diagnostics
    classification_notes: Optional[str] = None
    bonded_reason: Optional[str] = Field(
        None,
        description="Required non-null when structural_type is bonded_cluster"
    )
    review_flags: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# §4.B.3 — Distribution report
# ──────────────────────────────────────────────────────────────────


class PassageTypeDistribution(BaseModel):
    """Type distribution statistics for a single passage (SPEC §4.B.3)."""
    passage_id: str
    total_atoms: int = Field(ge=0)
    structural_type_counts: dict[str, int] = Field(default_factory=dict)
    scholarly_function_counts: dict[str, int] = Field(default_factory=dict)
    evidence_to_opinion_ratio: Optional[float] = None
    example_to_definition_ratio: Optional[float] = None
    has_isnad_chains: bool = False
    bonded_cluster_count: int = Field(ge=0, default=0)
    mean_function_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    stddev_function_confidence: float = Field(ge=0.0, default=0.0)
    review_flag_counts: dict[str, int] = Field(default_factory=dict)


class SourceTypeDistribution(BaseModel):
    """Aggregate type distribution for an entire source (SPEC §4.B.3)."""
    source_id: str
    total_atoms: int = Field(ge=0)
    total_passages: int = Field(ge=0)
    structural_type_counts: dict[str, int] = Field(default_factory=dict)
    scholarly_function_counts: dict[str, int] = Field(default_factory=dict)
    mean_evidence_to_opinion_ratio: Optional[float] = None
    structural_profile: str = Field(
        description="One of: definitional, evidential, argumentative, narrative, mixed"
    )
    anomalous_passages: list[str] = Field(
        default_factory=list,
        description="passage_ids of passages whose distribution deviates >2σ from source mean"
    )
    passage_distributions: list[PassageTypeDistribution] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# §4.B.5 — Fingerprint manifest
# ──────────────────────────────────────────────────────────────────


class FingerprintManifestEntry(BaseModel):
    """One entry in the per-source fingerprint manifest (SPEC §4.B.5)."""
    atom_id: str
    fingerprint_text_hash: Optional[str] = None
    fingerprint_key_terms: Optional[list[str]] = None
    scholarly_function: Optional[ScholarlyFunction] = None


class FingerprintManifest(BaseModel):
    """Per-source fingerprint manifest (SPEC §4.B.5).

    Written to: library/sources/{source_id}/atoms/fingerprint_manifest.json
    Used by downstream engines for cross-source deduplication detection.
    """
    source_id: str
    atom_count: int = Field(ge=0)
    entries: list[FingerprintManifestEntry] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Full atom stream — convenience wrapper
# ──────────────────────────────────────────────────────────────────


class AtomStream(BaseModel):
    """The complete atom stream for a source (SPEC §3).

    Logical wrapper — on disk this is atoms.jsonl (one record per line).
    """
    source_id: str
    atoms: list[AtomRecord] = Field(
        description="Ordered by atom_id. Globally monotonic. "
        "Non-overlapping anchor_spans within each passage."
    )
