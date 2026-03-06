"""Synthesis Engine Contracts — Machine-readable schemas derived from SPEC.md §2 and §3.

These Pydantic models define:
  - The INPUT contract: lifecycle signals, regeneration requests (§2.3)
  - The OUTPUT contract: entries, entry content, citations, versions (§3)
  - Phase 2 analysis intermediates: positions, khilaf, contradictions (§4.A.3)
  - Phase 3 construction intermediates: planned claims, attributions (§4.A.4)
  - Transformative capability outputs: consensus, genealogy, gaps, quality,
    khilaf disambiguation, Socratic assessment (§4.B)

When SPEC.md and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────


class GroundingType(str, Enum):
    """How a claim in the entry is grounded (SPEC §3.2, §6.4)."""
    LIBRARY_EXCERPT = "library_excerpt"
    LIBRARY_METADATA = "library_metadata"
    LLM_RESEARCH = "llm_research"


class KhilafClassificationType(str, Enum):
    """Types of scholarly disagreement (SPEC §4.A.3 Step 2)."""
    LAFZI = "lafzi"       # verbal — same meaning, different words
    HAQIQI = "haqiqi"     # substantive — genuinely different positions
    MU_TABAR = "mu_tabar"   # respected — valid evidence on each side
    SHADH = "shadh"       # aberrant — held by very few


class ContradictionNature(str, Enum):
    """Nature of intra-author contradiction (SPEC §4.A.3 Step 4)."""
    RETRACTION = "retraction"
    GENERAL_VS_SPECIFIC = "general_vs_specific"
    GENUINE = "genuine"
    CONTEXT_DEPENDENT = "context_dependent"
    UNDATABLE = "undatable"


class ClaimType(str, Enum):
    """Types of planned claims in the factual layer (SPEC §4.A.4.1 Step 1)."""
    DEFINITION = "definition"
    POSITION_STATEMENT = "position_statement"
    EVIDENCE_CITATION = "evidence_citation"
    EXAMPLE = "example"
    EDGE_CASE = "edge_case"
    PREREQUISITE_LINK = "prerequisite_link"
    CONSENSUS_STATEMENT = "consensus_statement"
    RETRACTION_NOTE = "retraction_note"


class TargetSection(str, Enum):
    """Which content section a claim belongs to (SPEC §4.A.4.1 Step 1)."""
    CORE_TREATMENT = "core_treatment"
    SCHOLARLY_POSITIONS = "scholarly_positions"
    EDGE_CASES = "edge_cases"
    COMMON_MISUNDERSTANDINGS = "common_misunderstandings"


class StalenessTriggertType(str, Enum):
    """What triggered an entry becoming stale (SPEC §2.3)."""
    NEW_EXCERPT = "new_excerpt"
    EXCERPT_REMOVED = "excerpt_removed"
    EXCERPT_RELOCATED_IN = "excerpt_relocated_in"
    EXCERPT_RELOCATED_OUT = "excerpt_relocated_out"
    METADATA_CORRECTION = "metadata_correction"
    RECLASSIFICATION = "reclassification"


class RegenerationPriority(str, Enum):
    """Priority level for entry regeneration (SPEC §2.3)."""
    USER_INITIATED = "user_initiated"
    BACKGROUND = "background"
    BATCH = "batch"


class CorrectionType(str, Enum):
    """Types of owner corrections (SPEC §2.3)."""
    FACTUAL_ERROR = "factual_error"
    ATTRIBUTION_ERROR = "attribution_error"
    MISSING_POSITION = "missing_position"
    MISREPRESENTATION = "misrepresentation"
    STRUCTURAL_FEEDBACK = "structural_feedback"


class ConsensusStrength(str, Enum):
    """Scholarly consensus spectrum (SPEC §4.B.1)."""
    ABSOLUTE_CONSENSUS = "absolute_consensus"      # إجماع قطعي
    NEAR_CONSENSUS = "near_consensus"               # إجماع ظني / قول الجمهور
    STRONG_MAJORITY = "strong_majority"
    WEAK_MAJORITY = "weak_majority"
    EVENLY_DISPUTED = "evenly_disputed"
    MINORITY_ABERRANT = "minority_aberrant"


class DisagreementLocusType(str, Enum):
    """Types of disagreement locus in khilaf disambiguation (SPEC §4.B.5)."""
    LAFZI = "lafzi"
    ISHTIRAKI = "ishtiraki"
    HAQIQI = "haqiqi"
    SU_AL_MUKHTALIF = "su_al_mukhtalif"


class AtomicSubClaimType(str, Enum):
    """Types of atomic sub-claims in khilaf decomposition (SPEC §4.B.5)."""
    DEFINITIONAL = "definitional"
    CONDITIONAL = "conditional"
    RULING = "ruling"
    SCOPE = "scope"
    METHODOLOGICAL = "methodological"
    TERMINOLOGICAL = "terminological"


class AssessmentLevel(int, Enum):
    """Cognitive levels for Socratic questions (SPEC §4.B.6)."""
    RECALL = 1          # حفظ
    RECOGNITION = 2     # تمييز
    APPLICATION = 3     # تطبيق
    COMPARISON = 4      # موازنة


class PositionRelationship(str, Enum):
    """How a student's position relates to a teacher's (SPEC §4.B.2)."""
    INHERITED = "inherited"
    DIVERGED = "diverged"
    REFINED = "refined"


class GapType(str, Enum):
    """Types of coverage gaps (SPEC §4.B.3)."""
    SCHOOL = "school"
    TEMPORAL = "temporal"
    SOURCE_DIVERSITY = "source_diversity"


# ──────────────────────────────────────────────────────────────────
# Input Contract Models (SPEC §2)
# ──────────────────────────────────────────────────────────────────


class StalenessSignal(BaseModel):
    """Notification that an entry is stale (SPEC §2.3)."""
    leaf_path: str
    science_id: str
    school_group: Optional[str] = None
    trigger_type: StalenessTriggertType
    trigger_excerpt_id: str
    timestamp: str = Field(description="ISO 8601 datetime")


class RegenerationRequest(BaseModel):
    """Request to regenerate an entry (SPEC §2.3)."""
    leaf_path: str
    science_id: str
    school_group: Optional[str] = None
    priority: RegenerationPriority
    owner_constraints: list[str] = Field(
        default_factory=list,
        description="Permanent owner corrections applied during generation"
    )


class OwnerCorrection(BaseModel):
    """Owner-identified error in an entry (SPEC §2.3)."""
    entry_id: str
    correction_type: CorrectionType
    description: str
    permanent_constraint: bool = Field(
        default=False,
        description="If true, this correction survives all future regenerations"
    )


# ──────────────────────────────────────────────────────────────────
# Phase 2: Scholarly Analysis Intermediates (SPEC §4.A.3)
# ──────────────────────────────────────────────────────────────────


class PositionHolder(BaseModel):
    """A scholar who holds a specific position."""
    scholar_id: Optional[str] = None
    name: str
    death_hijri: Optional[int] = None
    school: Optional[str] = None


class ScholarlyPosition(BaseModel):
    """A distinct scholarly position identified at a leaf (SPEC §4.A.3 Step 1)."""
    position_id: str = Field(description="Format: pos_{sequence}")
    position_summary: str = Field(
        description="Arabic, ≤ 50 words",
        max_length=500
    )
    holders: list[PositionHolder]
    evidence_types: list[str] = Field(default_factory=list)
    supporting_excerpt_ids: list[str]
    is_response_to: Optional[str] = Field(
        default=None,
        description="position_id of a position this one responds to"
    )


class KhilafClassification(BaseModel):
    """Disagreement classification for a pair of positions (SPEC §4.A.3 Step 2)."""
    position_a: str
    position_b: str
    classification: KhilafClassificationType
    reasoning: str = Field(max_length=500)
    confidence: float = Field(ge=0.0, le=1.0)


class ContradictionCheckResult(BaseModel):
    """Intra-author contradiction check (SPEC §4.A.3 Step 4)."""
    author_id: str
    contradictions_found: bool
    contradictions: list[IntraAuthorContradiction] = Field(default_factory=list)


class IntraAuthorContradiction(BaseModel):
    """A detected contradiction within a single author's works."""
    excerpt_id_a: str
    excerpt_id_b: str
    nature: ContradictionNature


class AbrogationFlag(BaseModel):
    """An abrogation detected in cited evidence (SPEC §4.A.3 Step 6)."""
    position_id: str
    evidence_ref: str
    abrogated_by: str
    confidence: float = Field(ge=0.0, le=1.0)
    grounding_type: GroundingType


class ScholarlyAnalysis(BaseModel):
    """Complete Phase 2 output (SPEC §4.A.3)."""
    positions: list[ScholarlyPosition]
    khilaf_classifications: list[KhilafClassification] = Field(default_factory=list)
    tahrir_questions_identified: int = Field(
        default=1,
        description="How many distinct questions are addressed at this leaf"
    )
    contradictions: list[ContradictionCheckResult] = Field(default_factory=list)
    mu_tamad_positions: dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="School → position_id that is mu'tamad, or null"
    )
    abrogation_flags: list[AbrogationFlag] = Field(default_factory=list)
    school_ratio: dict[str, int] = Field(
        default_factory=dict,
        description="School → excerpt count for bias assessment"
    )
    source_concentration: float = Field(
        default=0.0,
        description="Herfindahl index of source_ids (>0.25 indicates concentration)"
    )
    temporal_skew: float = Field(
        default=0.0,
        description="Coefficient of variation of author death dates"
    )
    landscape_used: bool = False
    landscape_confidence: Optional[float] = None


# ──────────────────────────────────────────────────────────────────
# Phase 3: Narrative Construction Intermediates (SPEC §4.A.4)
# ──────────────────────────────────────────────────────────────────


class PlannedClaim(BaseModel):
    """A single claim in the entry outline (SPEC §4.A.4.1 Step 1)."""
    claim_id: str
    claim_text: str = Field(description="One-sentence description")
    claim_type: ClaimType
    target_section: TargetSection


class ClaimAttribution(BaseModel):
    """Source spans grounding a planned claim (SPEC §4.A.4.1 Step 2)."""
    claim_id: str
    attributed_excerpt_ids: list[str] = Field(min_length=0, max_length=5)
    attributed_spans: list[ExcerptSpan] = Field(default_factory=list)
    attribution_confidence: float = Field(ge=0.0, le=1.0)
    grounding_type: GroundingType = GroundingType.LIBRARY_EXCERPT


class ExcerptSpan(BaseModel):
    """A best-effort character range within an excerpt's primary_text.

    Used for highlighting in the scholar interface, not for extraction.
    Offset error of ±50 characters is acceptable — the full excerpt
    text remains the source of truth.
    """
    excerpt_id: str
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=0)


class EntailmentResult(BaseModel):
    """Result of verifying a generated sentence against its attributed spans (§4.A.4.1 Step 4)."""
    claim_id: str
    entailed: bool
    unsupported_elements: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Output Contract: Entry (SPEC §3)
# ──────────────────────────────────────────────────────────────────


class Citation(BaseModel):
    """A single citation in the entry (SPEC §3.3)."""
    citation_id: str = Field(description="Format: cit_{sequence}")
    excerpt_id: str
    source_title: str
    author_name: str
    tahqiq_editor: Optional[str] = None
    publisher: Optional[str] = None
    volume: Optional[int] = None
    page_start: Optional[str] = None
    page_end: Optional[str] = None
    grounding_type: GroundingType
    formatted_citation: str = Field(
        description="Academic format: Author, Work (ed. Tahqiq, Publisher), vol:page"
    )


class ScholarlyPositionEntry(BaseModel):
    """A position as presented in the entry (SPEC §3.2)."""
    position_id: str
    position_summary: str
    holders: list[PositionHolder]
    evidence_types: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    mu_tamad_in_school: Optional[str] = None
    is_consensus: bool = False
    consensus_strength: Optional[ConsensusStrength] = None
    confidence: float = Field(ge=0.0, le=1.0)


class EntryContent(BaseModel):
    """The content structure of an entry (SPEC §3.2)."""
    prerequisites: str = Field(description="Arabic, prerequisite topics")
    topic_situation: str = Field(description="Where this topic fits")
    core_treatment: str = Field(description="Main body with [cit:N] markers")
    scholarly_positions: list[ScholarlyPositionEntry] = Field(default_factory=list)
    edge_cases: Optional[str] = None
    common_misunderstandings: Optional[str] = None
    khilaf_analysis: Optional[str] = Field(
        default=None,
        description="Khilaf disambiguation narrative from §4.B.5, if enabled"
    )
    temporal_narrative: Optional[str] = None
    what_next: Optional[str] = None
    analytical_layer: Optional[str] = Field(
        default=None,
        description="Engine's intellectual contribution: cross-excerpt analysis, "
        "metadata-driven context, LLM research (§4.A.4.2)"
    )
    critical_analysis: Optional[str] = Field(
        default=None,
        description="Analysis based on flagged (non-verified) excerpts only"
    )


class GenerationMetadata(BaseModel):
    """Metadata about the generation process (SPEC §3.1)."""
    duration_seconds: float
    total_excerpts_used: int
    verified_excerpts: int
    flagged_excerpts_referenced: int = 0
    unique_authors: int
    unique_sources: int
    temporal_span_hijri: Optional[tuple[int, int]] = Field(
        default=None,
        description="(earliest, latest) author death dates hijri"
    )
    library_grounded_claim_count: int
    llm_contributed_claim_count: int
    deduplication_clusters_found: int = 0
    quality_assessment: Optional[QualityAssessment] = None
    self_verification: Optional[SelfVerificationResult] = None
    khilaf_disambiguation: Optional[KhilafDisambiguationResult] = None
    genealogy_chains: list[GenealogyChain] = Field(default_factory=list)
    gap_notes: list[GapNote] = Field(default_factory=list)
    consensus_mappings: list[ConsensusMapping] = Field(default_factory=list)


class Entry(BaseModel):
    """The primary knowledge product (SPEC §3.1)."""
    entry_id: str = Field(
        description="Format: ent_{science_id}_{leaf_slug}_{school_or_all}_v{version}"
    )
    leaf_path: str
    science_id: str
    school_group: Optional[str] = None
    generated_utc: str = Field(description="ISO 8601 datetime")
    generator_config: dict = Field(
        description="Model ID, prompt version hash, SCIENCE.md version hash"
    )
    source_excerpt_ids: list[str] = Field(min_length=1)
    content: EntryContent
    citations: list[Citation]
    staleness_hash: str = Field(description="SHA-256 for staleness detection")
    version: int = Field(ge=1)
    previous_version_id: Optional[str] = None
    owner_constraints: list[str] = Field(default_factory=list)
    is_stale: bool = False
    taxonomy_version: str
    generation_metadata: GenerationMetadata


# ──────────────────────────────────────────────────────────────────
# Transformative Capability Models (SPEC §4.B)
# ──────────────────────────────────────────────────────────────────


class ConsensusMapping(BaseModel):
    """Consensus strength for a position (SPEC §4.B.1)."""
    position_id: str
    consensus_strength: ConsensusStrength
    evidence_excerpts: list[str] = Field(
        default_factory=list,
        description="Excerpt IDs that claim or evidence consensus"
    )
    library_distribution_note: str = Field(
        default="",
        description="How the library's position distribution relates to the claim"
    )
    confidence: float = Field(ge=0.0, le=1.0)


class GenealogyChain(BaseModel):
    """An intellectual genealogy chain (SPEC §4.B.2)."""
    chain: list[PositionHolder] = Field(
        description="Ordered: teacher → ... → student"
    )
    chain_source: str = Field(description="'library_graph' or 'llm_research'")
    narrative_relevance: str
    position_relationship: PositionRelationship


class GapNote(BaseModel):
    """A coverage gap with provisional content (SPEC §4.B.3)."""
    gap_type: GapType
    gap_description: str
    provisional_content: str
    confidence: float = Field(ge=0.0, le=1.0)
    grounding_type: GroundingType = GroundingType.LLM_RESEARCH
    recommended_acquisitions: list[str] = Field(
        default_factory=list,
        description="Work IDs from the registry's placeholder records"
    )


class QualityAssessment(BaseModel):
    """Entry quality self-assessment (SPEC §4.B.4)."""
    source_diversity: float = Field(ge=0.0, le=1.0)
    temporal_coverage: float = Field(ge=0.0, le=1.0)
    school_balance: float = Field(ge=0.0, le=1.0)
    evidence_completeness: float = Field(ge=0.0, le=1.0)
    citation_density: float = Field(ge=0.0, le=1.0)
    confidence_floor: float = Field(ge=0.0, le=1.0)
    overall_quality: float = Field(ge=0.0, le=1.0)
    quality_narrative: str


class AtomicSubClaim(BaseModel):
    """An atomic sub-claim from position decomposition (SPEC §4.B.5)."""
    claim_text: str = Field(description="Arabic")
    claim_type: AtomicSubClaimType
    shared_by: list[str] = Field(
        default_factory=list,
        description="Position IDs that share this sub-claim"
    )


class DisagreementLocus(BaseModel):
    """A specific point of disagreement between positions (SPEC §4.B.5)."""
    locus_description: str
    classification: DisagreementLocusType
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)
    positions_involved: list[str] = Field(description="Position IDs")


class KhilafDisambiguationResult(BaseModel):
    """Full khilaf disambiguation output (SPEC §4.B.5)."""
    atomic_subclaims: list[AtomicSubClaim]
    disagreement_loci: list[DisagreementLocus]
    common_ground_summary: str
    disambiguation_confidence: float = Field(ge=0.0, le=1.0)


class AssessmentQuestion(BaseModel):
    """A comprehension question for Socratic assessment (SPEC §4.B.6)."""
    question_text: str = Field(description="Arabic")
    level: AssessmentLevel
    expected_answer: str
    answer_excerpt_ids: list[str] = Field(default_factory=list)
    prerequisite_knowledge: list[str] = Field(default_factory=list)


class SelfVerificationResult(BaseModel):
    """Result of Socratic self-verification (SPEC §4.B.6)."""
    questions_generated: int
    questions_passed: int
    coherence_defects_found: int
    defects_resolved: int
    verification_confidence: float = Field(ge=0.0, le=1.0)


class AssessmentSet(BaseModel):
    """Collection of assessment questions stored alongside an entry (SPEC §4.B.6)."""
    entry_id: str
    entry_version: int
    science_id: str
    leaf_path: str
    questions: list[AssessmentQuestion]
    generated_utc: str


# ──────────────────────────────────────────────────────────────────
# Entry Version History (SPEC §3.4)
# ──────────────────────────────────────────────────────────────────


class ChangeSummary(BaseModel):
    """Structured change summary between entry versions (SPEC §3.4)."""
    change_summary_id: str
    old_version: int
    new_version: int
    trigger: str = Field(description="What caused the regeneration")
    positions_added: list[str] = Field(default_factory=list)
    positions_removed: list[str] = Field(default_factory=list)
    positions_modified: list[str] = Field(default_factory=list)
    new_excerpts_incorporated: list[str] = Field(default_factory=list)
    structural_changes: str = Field(default="")


class EntryVersionRecord(BaseModel):
    """A record in the entry's version history (SPEC §3.4)."""
    entry_id: str
    version: int
    generated_utc: str
    source_excerpt_ids: list[str]
    staleness_hash: str
    generation_metadata_summary: str = Field(
        description="One-line summary for the scholar interface"
    )
    change_summary: Optional[ChangeSummary] = Field(
        default=None,
        description="Structured diff from previous version (null for v1)"
    )
