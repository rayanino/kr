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


class ReviewFlag(str, Enum):
    """Machine-generated review flag values for atoms (SPEC §3)."""
    LOW_FUNCTION_CONFIDENCE = "low_function_confidence"
    AMBIGUOUS_LAYER = "ambiguous_layer"
    POSSIBLE_MISATTRIBUTION = "possible_misattribution"
    OFFSET_DRIFT_CORRECTED = "offset_drift_corrected"
    UNRESOLVED_QURAN_REF = "unresolved_quran_ref"
    LOW_ATTRIBUTION_CONFIDENCE = "low_attribution_confidence"
    MID_WORD_BOUNDARY = "mid_word_boundary"
    COVERAGE_GAP_UNRESOLVED = "coverage_gap_unresolved"
    INCOMPLETE_ARGUMENT = "incomplete_argument"
    EVIDENCE_TYPE_CONFLICT = "evidence_type_conflict"
    ORPHANED_FOOTNOTE_MARKER = "orphaned_footnote_marker"
    ATOM_REORDERING_APPLIED = "atom_reordering_applied"
    OVER_SEGMENTED = "over_segmented"
    SINGLE_LAYER_IN_COMMENTARY = "single_layer_in_commentary"
    NFC_NORMALIZATION_APPLIED = "nfc_normalization_applied"


class EvidenceQualitySignalType(str, Enum):
    """Evidence quality signal type detected in evidence atoms (SPEC §4.B.8)."""
    HADITH_STRONG_COLLECTION = "hadith_strong_collection"
    HADITH_WEAKNESS_FLAG = "hadith_weakness_flag"
    HADITH_CHAIN_QUALITY = "hadith_chain_quality"
    EVIDENCE_EXPLICIT_STRENGTH = "evidence_explicit_strength"
    EVIDENCE_EXPLICIT_WEAKNESS = "evidence_explicit_weakness"
    CONSENSUS_QUALIFIER = "consensus_qualifier"
    AUTHOR_TARJIH_MARKER = "author_tarjih_marker"


class QualityDirection(str, Enum):
    """Direction of an evidence quality signal (SPEC §4.B.8)."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


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


class ConcordanceEntry(BaseModel):
    """Terminological concordance entry for a definition atom (SPEC §4.B.7).

    Extracted from definition atoms to build a term-concept mapping.
    """
    defined_term: str = Field(description="The Arabic term being defined")
    definition_genus: Optional[str] = Field(
        None, description="Broader category (genus in genus-differentia pattern)"
    )
    definition_differentia: list[str] = Field(
        default_factory=list,
        description="Distinguishing features"
    )
    alternate_terms: list[str] = Field(
        default_factory=list,
        description="Synonyms mentioned in the definition text"
    )
    science_scope: str = Field(
        description="Science this term belongs to, from source metadata"
    )


class EvidenceQualitySignal(BaseModel):
    """Author's explicit evaluation of evidence strength (SPEC §4.B.8).

    NOT the system's evaluation — the source author's own quality markers.
    """
    signal_type: EvidenceQualitySignalType
    signal_text: str = Field(
        description="Arabic text that triggered this detection"
    )
    quality_direction: QualityDirection
    span_start: int = Field(ge=0, description="Start offset within atom_text")
    span_end: int = Field(ge=0, description="End offset within atom_text")
    confidence: float = Field(ge=0.0, le=1.0)


class ArgumentCompletenessScore(BaseModel):
    """Argument completeness analysis for a passage (SPEC §4.B.6).

    Detects structural gaps in scholarly argument patterns.
    Stored in the distribution report, not per atom.
    """
    pattern_type: Optional[str] = Field(
        None, description="Detected rhetorical pattern from §4.B.1. Null if none."
    )
    required_present: list[str] = Field(default_factory=list)
    required_missing: list[str] = Field(default_factory=list)
    optional_present: list[str] = Field(default_factory=list)
    completeness_ratio: float = Field(
        ge=0.0, le=1.0,
        description="|required_present| / |required_present ∪ required_missing|"
    )
    gap_description: Optional[str] = Field(
        None,
        description="Human-readable description of missing components. "
        "Null when completeness_ratio is 1.0."
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
        description="None when enable_attribution_detection is false (feature disabled — "
        "downstream must NOT interpret as 'no attributions'). Empty list [] when "
        "enabled but no attributions detected. Non-empty list when attributions found."
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

    # Terminological concordance (§4.B.7)
    concordance_entry: Optional[ConcordanceEntry] = Field(
        None,
        description="Present only on definition atoms when "
        "enable_concordance_extraction is true. Null otherwise."
    )

    # Evidence quality signals (§4.B.8)
    evidence_quality_signals: Optional[list[EvidenceQualitySignal]] = Field(
        None,
        description="None when enable_evidence_quality_detection is false. "
        "Empty list [] when enabled but no signals detected. "
        "Non-empty list when signals found. Only on evidence atoms."
    )

    # Diagnostics
    classification_notes: Optional[str] = None
    bonded_reason: Optional[str] = Field(
        None,
        description="Required non-null when structural_type is bonded_cluster"
    )
    review_flags: list[ReviewFlag] = Field(
        default_factory=list,
        description="Machine-generated flags for human review."
    )


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
    completeness_score: Optional[ArgumentCompletenessScore] = Field(
        None,
        description="§4.B.6 argument completeness analysis. "
        "Null when completeness scoring is disabled or no pattern detected."
    )


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
# §4.B.7 — Terminological index
# ──────────────────────────────────────────────────────────────────


class TermIndexEntry(BaseModel):
    """One entry in the per-source terminological index (SPEC §4.B.7)."""
    atom_id: str
    passage_id: str
    source_layer: SourceLayer
    layer_author_id: Optional[str] = None
    concordance: ConcordanceEntry


class TermIndex(BaseModel):
    """Per-source terminological index (SPEC §4.B.7).

    Written to: library/sources/{source_id}/atoms/term_index.json
    Used by downstream engines for cross-source terminology mapping.
    """
    source_id: str
    term_count: int = Field(ge=0)
    entries: list[TermIndexEntry] = Field(default_factory=list)


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


# ──────────────────────────────────────────────────────────────────
# Error handling (SPEC §7)
# ──────────────────────────────────────────────────────────────────


class ErrorSeverity(str, Enum):
    """Severity levels for atomization errors."""
    FATAL = "fatal"
    WARNING = "warning"
    INFO = "info"


class AtomizationErrorCode(str, Enum):
    """All error codes the atomization engine can produce (SPEC §7)."""
    INVALID_INPUT = "ATOM_INVALID_INPUT"
    LLM_FAILURE = "ATOM_LLM_FAILURE"
    SCHEMA_VIOLATION = "ATOM_SCHEMA_VIOLATION"
    OFFSET_UNRESOLVABLE = "ATOM_OFFSET_UNRESOLVABLE"
    COVERAGE_VIOLATION = "ATOM_COVERAGE_VIOLATION"
    OFFSET_INTEGRITY_FAILURE = "ATOM_OFFSET_INTEGRITY_FAILURE"
    LAYER_DISTRIBUTION_SUSPICIOUS = "ATOM_LAYER_DISTRIBUTION_SUSPICIOUS"
    HIGH_UNCLASSIFIED_RATE = "ATOM_HIGH_UNCLASSIFIED_RATE"
    QURAN_REF_UNRESOLVED = "ATOM_QURAN_REF_UNRESOLVED"
    ATTRIBUTION_PARSE_FAILURE = "ATOM_ATTRIBUTION_PARSE_FAILURE"
    ATTRIBUTION_MARKER_MISSING = "ATOM_ATTRIBUTION_MARKER_MISSING"
    ATTRIBUTION_LOW_CONFIDENCE = "ATOM_ATTRIBUTION_LOW_CONFIDENCE"
    EVIDENCE_TYPE_CONFLICT = "ATOM_EVIDENCE_TYPE_CONFLICT"
    FOOTNOTE_INDEX_OUT_OF_RANGE = "ATOM_FOOTNOTE_INDEX_OUT_OF_RANGE"
    OVER_SEGMENTATION = "ATOM_OVER_SEGMENTATION"
    FINGERPRINT_HASH_FAILURE = "ATOM_FINGERPRINT_HASH_FAILURE"
    FINGERPRINT_EMBEDDING_FAILURE = "ATOM_FINGERPRINT_EMBEDDING_FAILURE"
    FINGERPRINT_KEY_TERMS_EMPTY = "ATOM_FINGERPRINT_KEY_TERMS_EMPTY"
    UNKNOWN_LAYER_TYPE = "ATOM_UNKNOWN_LAYER_TYPE"
    COMPLETENESS_PATTERN_MISMATCH = "ATOM_COMPLETENESS_PATTERN_MISMATCH"
    CONCORDANCE_EXTRACTION_FAILURE = "ATOM_CONCORDANCE_EXTRACTION_FAILURE"
    EVIDENCE_QUALITY_PARSE_FAILURE = "ATOM_EVIDENCE_QUALITY_PARSE_FAILURE"


ERROR_SEVERITY: dict[AtomizationErrorCode, ErrorSeverity] = {
    AtomizationErrorCode.INVALID_INPUT: ErrorSeverity.WARNING,
    AtomizationErrorCode.LLM_FAILURE: ErrorSeverity.WARNING,
    AtomizationErrorCode.SCHEMA_VIOLATION: ErrorSeverity.WARNING,
    AtomizationErrorCode.OFFSET_UNRESOLVABLE: ErrorSeverity.WARNING,
    AtomizationErrorCode.COVERAGE_VIOLATION: ErrorSeverity.FATAL,
    AtomizationErrorCode.OFFSET_INTEGRITY_FAILURE: ErrorSeverity.FATAL,
    AtomizationErrorCode.LAYER_DISTRIBUTION_SUSPICIOUS: ErrorSeverity.INFO,
    AtomizationErrorCode.HIGH_UNCLASSIFIED_RATE: ErrorSeverity.WARNING,
    AtomizationErrorCode.QURAN_REF_UNRESOLVED: ErrorSeverity.INFO,
    AtomizationErrorCode.ATTRIBUTION_PARSE_FAILURE: ErrorSeverity.WARNING,
    AtomizationErrorCode.ATTRIBUTION_MARKER_MISSING: ErrorSeverity.WARNING,
    AtomizationErrorCode.ATTRIBUTION_LOW_CONFIDENCE: ErrorSeverity.INFO,
    AtomizationErrorCode.EVIDENCE_TYPE_CONFLICT: ErrorSeverity.INFO,
    AtomizationErrorCode.FOOTNOTE_INDEX_OUT_OF_RANGE: ErrorSeverity.WARNING,
    AtomizationErrorCode.OVER_SEGMENTATION: ErrorSeverity.WARNING,
    AtomizationErrorCode.FINGERPRINT_HASH_FAILURE: ErrorSeverity.WARNING,
    AtomizationErrorCode.FINGERPRINT_EMBEDDING_FAILURE: ErrorSeverity.WARNING,
    AtomizationErrorCode.FINGERPRINT_KEY_TERMS_EMPTY: ErrorSeverity.INFO,
    AtomizationErrorCode.UNKNOWN_LAYER_TYPE: ErrorSeverity.WARNING,
    AtomizationErrorCode.COMPLETENESS_PATTERN_MISMATCH: ErrorSeverity.INFO,
    AtomizationErrorCode.CONCORDANCE_EXTRACTION_FAILURE: ErrorSeverity.WARNING,
    AtomizationErrorCode.EVIDENCE_QUALITY_PARSE_FAILURE: ErrorSeverity.WARNING,
}


# ──────────────────────────────────────────────────────────────────
# Configuration (SPEC §8)
# ──────────────────────────────────────────────────────────────────


class AtomizationConfig(BaseModel):
    """Atomization engine configuration parameters (SPEC §8).

    All parameters have defaults matching SPEC §8's "Default" column.
    """
    primary_llm_model: str = Field(
        default="anthropic/claude-sonnet-4-5-20250929",
        description="Model for standard atomization"
    )
    escalation_llm_model: str = Field(
        default="anthropic/claude-opus-4-5-20250929",
        description="Model for escalation retries and low-fidelity sources"
    )
    max_retries_per_passage: int = Field(
        default=2, ge=0, le=5,
        description="Maximum LLM retries on validation failure"
    )
    function_confidence_threshold: float = Field(
        default=0.6, ge=0.0, le=1.0,
        description="Below this, low_function_confidence review flag is set"
    )
    quran_match_confidence_threshold: float = Field(
        default=0.85, ge=0.5, le=1.0,
        description="Minimum confidence for canonical Quran text matching"
    )
    quran_hard_constraint_threshold: float = Field(
        default=0.95, ge=0.8, le=1.0,
        description="Above this, Quran detection overrides LLM classification"
    )
    offset_correction_window: int = Field(
        default=50, ge=10, le=200,
        description="Characters to search when correcting LLM offsets"
    )
    offset_correction_max_distance: int = Field(
        default=3, ge=0, le=10,
        description="Maximum Levenshtein distance for offset fuzzy matching"
    )
    unclassified_rate_warning_threshold: float = Field(
        default=0.05, ge=0.01, le=0.20,
        description="Fraction of unclassified atoms triggering source-level review"
    )
    review_flag_rate_warning_threshold: float = Field(
        default=0.20, ge=0.05, le=0.50,
        description="Fraction of flagged atoms triggering source-level review"
    )
    fidelity_escalation_threshold: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="text_fidelity.min_score below which escalation model is used"
    )
    gold_baseline_path: str = Field(
        default="engines/atomization/gold/",
        description="Directory containing gold baseline files for few-shot examples"
    )
    enable_attribution_detection: bool = Field(
        default=True,
        description="Whether to run §4.B.4 scholarly attribution chain detection"
    )
    attribution_confidence_threshold: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Below this, low_attribution_confidence review flag is set"
    )
    enable_text_fingerprinting: bool = Field(
        default=True,
        description="Whether to compute Tier 1 (text hash) and Tier 2 (key terms)"
    )
    enable_semantic_fingerprinting: bool = Field(
        default=False,
        description="Whether to compute Tier 3 (embedding). Requires GPU."
    )
    fingerprint_embedding_model: str = Field(
        default="Omartificial/Arabic-STS-Matryoshka",
        description="Embedding model for Tier 3 fingerprinting"
    )
    fingerprint_embedding_dimensions: int = Field(
        default=256, ge=64, le=1024,
        description="Matryoshka truncation dimension for Tier 3"
    )
    fingerprint_key_terms_count: int = Field(
        default=5, ge=2, le=10,
        description="Maximum number of key terms extracted per atom for Tier 2"
    )
    enable_completeness_scoring: bool = Field(
        default=True,
        description="Whether to run §4.B.6 argument completeness scoring"
    )
    enable_concordance_extraction: bool = Field(
        default=True,
        description="Whether to extract concordance entries from definition atoms"
    )
    enable_evidence_quality_detection: bool = Field(
        default=True,
        description="Whether to detect evidence quality signals in evidence atoms"
    )
    evidence_quality_lexicon_path: str = Field(
        default="engines/atomization/lexicons/evidence_quality.json",
        description="Path to the quality signal phrase lexicon"
    )
