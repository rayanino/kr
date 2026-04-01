"""Taxonomy Engine Contracts — Machine-readable schemas derived from SPEC.md §2 and §3.

These Pydantic models define:
  - The INPUT contract: what the taxonomy engine expects from upstream (§2)
  - The OUTPUT contract: placed excerpts, tree structures, coverage, evolution artifacts (§3)
  - Transformative capability outputs: disagreement topology, landscape, predictions (§4.B)

When SPEC.md and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────


class PlacementReviewOutcome(str, Enum):
    """Outcomes of human gate review for placement (SPEC §3.1)."""
    APPROVED = "approved"
    APPROVED_WITH_MODIFICATIONS = "approved_with_modifications"
    AUTO_APPROVED = "auto_approved"
    EVOLUTION_REDISTRIBUTED = "evolution_redistributed"


class VerifiedFlaggedStatus(str, Enum):
    """Whether a placed excerpt is verified or flagged (SPEC §3.1)."""
    VERIFIED = "verified"
    FLAGGED = "flagged"


class TreeNodeType(str, Enum):
    """Whether a node is a leaf or a branch."""
    LEAF = "leaf"
    BRANCH = "branch"


class PrerequisiteStrength(str, Enum):
    """Strength of a prerequisite dependency (SPEC §3.2)."""
    HARD = "hard"
    SOFT = "soft"


class CrossScienceLinkType(str, Enum):
    """Types of cross-science relationships (SPEC §3.2)."""
    SAME_CONCEPT = "same_concept"
    RELATED_CONCEPT = "related_concept"
    PREREQUISITE_CROSS_SCIENCE = "prerequisite_cross_science"
    APPLICATION_OF = "application_of"


class EvolutionChangeType(str, Enum):
    """Types of tree evolution (SPEC §3.4)."""
    LEAF_SPLIT = "leaf_split"
    BRANCH_RESTRUCTURE = "branch_restructure"
    NODE_RENAME = "node_rename"
    NODE_MOVE = "node_move"
    LEAF_MERGE = "leaf_merge"


class GapType(str, Enum):
    """Types of coverage gaps (SPEC §4.A.6)."""
    SCHOOL = "school"
    SOURCE_DIVERSITY = "source_diversity"
    TEMPORAL = "temporal"
    EVIDENCE = "evidence"
    PREREQUISITE = "prerequisite"
    EMPTY = "empty"


class HumanGateType(str, Enum):
    """Types of human gate decisions (SPEC §2.2)."""
    PLACEMENT_REVIEW = "placement_review"
    EVOLUTION_REVIEW = "evolution_review"
    COVERAGE_REVIEW = "coverage_review"


class HumanGateDecision(str, Enum):
    """Owner's decision at a human gate (SPEC §2.2)."""
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"


class DisagreementCategory(str, Enum):
    """Categories of scholarly disagreement at a leaf (SPEC §4.B.4)."""
    IJMA_DETECTED = "ijma_detected"
    ACTIVE_KHILAF = "active_khilaf"
    APPARENT_CONSENSUS_UNVERIFIED = "apparent_consensus_unverified"
    INTRA_SCHOOL_DISAGREEMENT = "intra_school_disagreement"
    INSUFFICIENT_DATA = "insufficient_for_disagreement_analysis"
    POSITIONAL_DISAGREEMENT = "positional_disagreement"  # For sciences without schools


class DiscourseTransitionType(str, Enum):
    """Types of scholarly discourse transitions (SPEC §4.B.6)."""
    REFINEMENT = "refinement"
    OPPOSITION = "opposition"
    SYNTHESIS = "synthesis"


class InfluenceType(str, Enum):
    """Types of scholarly influence evidence (SPEC §4.B.6)."""
    EXPLICIT_CITATION = "explicit_citation"
    TEACHER_STUDENT = "teacher_student"
    TEMPORAL_INFERENCE = "temporal_inference"


class EvolutionPredictionType(str, Enum):
    """Types of proactive evolution predictions (SPEC §4.B.5)."""
    SPLIT_PREDICTION = "split_prediction"
    GAP_PREDICTION = "gap_prediction"


# ──────────────────────────────────────────────────────────────────
# §2 — Input Contract Models
# ──────────────────────────────────────────────────────────────────


class HumanGateDecisionRecord(BaseModel):
    """Owner's response at a human gate checkpoint (SPEC §2.2)."""
    decision_id: str
    gate_type: HumanGateType
    decision: HumanGateDecision
    modifications: Optional[dict] = None
    reviewer_notes: Optional[str] = None
    timestamp: str = Field(description="ISO datetime")


class ExcerptRelocationRequest(BaseModel):
    """Request to relocate a misplaced excerpt (SPEC §2.2, Scenario 8)."""
    excerpt_id: str
    current_leaf: str
    target_leaf: str
    reason: str


# ──────────────────────────────────────────────────────────────────
# §3.1 — Placed Excerpt Output
# ──────────────────────────────────────────────────────────────────


class PlacementReviewMetadata(BaseModel):
    """Documents the human gate outcome for a placement (SPEC §3.1)."""
    review_outcome: PlacementReviewOutcome
    evolution_proposal_id: Optional[str] = None
    reviewer_notes: Optional[str] = None


class PlacedExcerptAdditions(BaseModel):
    """DEPRECATED: Not used by runtime code.

    The runtime uses contracts_core.py:PlacementAdditions, which contains
    only CORE v1 fields. This model represents the full SPEC (including
    deferred fields like verified_flagged_status that require human gate
    implementation). When the human gate step is built, verified_flagged_status
    will be added to contracts_core.py:PlacementAdditions.

    See: engines/taxonomy/contracts_core.py:PlacementAdditions (authoritative)
    See: engines/synthesis/contracts.py:TaxonomyPlacedExcerpt (synthesis input)
    """
    confirmed_leaf: str = Field(description="Actual leaf path. May differ from proposed_leaf.")
    placement_confidence: float = Field(ge=0.0, le=1.0)
    placed_utc: str = Field(description="ISO datetime of placement")
    review_metadata: PlacementReviewMetadata
    verified_flagged_status: VerifiedFlaggedStatus
    taxonomy_version_at_placement: str
    placement_reasoning: str = Field(description="LLM-generated explanation of leaf choice")
    proposed_leaf_override: bool = False
    proposed_leaf_original: Optional[str] = None
    override_reason: Optional[str] = None


# ──────────────────────────────────────────────────────────────────
# §3.2 — Tree Structure Models
# ──────────────────────────────────────────────────────────────────


class TreeNode(BaseModel):
    """A single node in a science tree (SPEC §3.2)."""
    id: str = Field(description="ASCII slug, unique within tree")
    title: str = Field(description="Arabic display name")
    children: list[TreeNode] = Field(default_factory=list)
    leaf: bool = Field(description="True for leaf nodes (no children)")


class PrerequisiteEdge(BaseModel):
    """A prerequisite dependency between topics (SPEC §3.2)."""
    from_node_id: str = Field(description="The prerequisite topic")
    to_node_id: str = Field(description="The dependent topic")
    strength: PrerequisiteStrength
    rationale: str


class CrossScienceLink(BaseModel):
    """A link between related concepts in different sciences (SPEC §3.2)."""
    source_leaf: str = Field(description="Format: {science_id}/{leaf_path}")
    target_leaf: str = Field(description="Format: {science_id}/{leaf_path}")
    relationship_type: CrossScienceLinkType
    confidence: float = Field(ge=0.0, le=1.0)
    description: str


class TerminologySynonym(BaseModel):
    """A terminology variant mapping (SPEC §3.2)."""
    canonical_term: str = Field(description="Standard term used in tree node title")
    variants: list[TermVariant] = Field(default_factory=list)


class TermVariant(BaseModel):
    """A single terminology variant (SPEC §3.2)."""
    term: str
    context: str = Field(description="Which school, period, or author uses this variant")


# Fix forward reference
TerminologySynonym.model_rebuild()


# ──────────────────────────────────────────────────────────────────
# §3.3 — Coverage Analytics
# ──────────────────────────────────────────────────────────────────


class CoverageGap(BaseModel):
    """A specific coverage gap at a leaf (SPEC §4.A.6)."""
    gap_type: GapType
    leaf_path: str
    missing_school: Optional[str] = None
    current_source_count: Optional[int] = None
    covered_period: Optional[dict] = None
    science_total_period: Optional[dict] = None
    missing_evidence_types: Optional[list[str]] = None
    missing_prerequisite_leaf: Optional[str] = None


class TemporalSpan(BaseModel):
    """Chronological range of scholarship at a leaf (SPEC §3.3)."""
    earliest_author_death: Optional[int] = Field(None, description="Hijri year")
    latest_author_death: Optional[int] = Field(None, description="Hijri year")


class LeafCoverage(BaseModel):
    """Per-leaf coverage record (SPEC §3.3)."""
    leaf_path: str
    total_excerpts: int = 0
    verified_excerpts: int = 0
    flagged_excerpts: int = 0
    source_count: int = 0
    school_coverage: dict[str, int] = Field(default_factory=dict)
    evidence_type_coverage: dict[str, int] = Field(default_factory=dict)
    author_diversity: int = 0
    temporal_span: TemporalSpan = Field(
        default_factory=lambda: TemporalSpan(
            earliest_author_death=None, latest_author_death=None,
        ),
    )
    content_type_distribution: dict[str, int] = Field(default_factory=dict)
    gaps: list[CoverageGap] = Field(default_factory=list)
    significance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    difficulty_estimate: Optional[float] = Field(None, ge=0.0, le=1.0)
    duplicate_clusters: list[list[str]] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# §3.4 — Evolution Artifacts
# ──────────────────────────────────────────────────────────────────


class ExcerptRedistribution(BaseModel):
    """How one excerpt would be moved during evolution (SPEC §3.4)."""
    excerpt_id: str
    current_leaf: str
    proposed_leaf: str
    redistribution_confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class EvolutionInvariantChecks(BaseModel):
    """Results of the four §4.4 invariant checks (SPEC §3.4)."""
    zero_orphans: bool
    sibling_coherence: bool
    excerpt_non_interference: bool
    entry_lifecycle_propagation: bool


class EvolutionProposal(BaseModel):
    """A structured tree evolution proposal (SPEC §3.4)."""
    proposal_id: str = Field(description="Format: evo_{science_id}_{timestamp}")
    science_id: str
    current_tree_version: str
    proposed_tree_version: str
    change_type: EvolutionChangeType
    affected_node: str = Field(description="Node path in current tree")
    proposed_structure: dict = Field(description="New subtree structure")
    excerpt_redistribution: list[ExcerptRedistribution] = Field(default_factory=list)
    trigger_signal: dict = Field(description="What triggered this proposal")
    invariant_checks: EvolutionInvariantChecks


# ──────────────────────────────────────────────────────────────────
# §4.B.4 — Scholarly Disagreement Topology
# ──────────────────────────────────────────────────────────────────


class DisagreementPosition(BaseModel):
    """A distinct scholarly position within a disagreement (SPEC §4.B.4)."""
    schools: list[str] = Field(description="School names that hold this position")
    position_summary: str = Field(description="LLM-generated one-sentence summary")
    evidence_types: list[str] = Field(default_factory=list)
    earliest_scholar_date: Optional[int] = Field(None, description="Hijri year")
    latest_scholar_date: Optional[int] = Field(None, description="Hijri year")


class IntraSchoolDisagreement(BaseModel):
    """Internal disagreement within a single school (SPEC §4.B.4 Category 4)."""
    school: str
    internal_positions: list[str] = Field(
        description="Array of position summaries with scholar attributions"
    )


class LeafDisagreementClassification(BaseModel):
    """Disagreement classification for a single leaf (SPEC §4.B.4)."""
    leaf_path: str
    category: DisagreementCategory
    ijma_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    positions: list[DisagreementPosition] = Field(default_factory=list)
    intra_school: list[IntraSchoolDisagreement] = Field(default_factory=list)
    robustness: str = Field(
        default="normal",
        description="'low_robustness' if only one source per school"
    )
    intra_author_shifts: list[str] = Field(
        default_factory=list,
        description="Authors who changed position between works"
    )


class DominantDisagreementAxis(BaseModel):
    """A recurring school-pair disagreement pattern (SPEC §4.B.4)."""
    school_pair: list[str] = Field(min_length=2, max_length=2)
    leaf_count: int
    axis_root_cause_hypothesis: str = Field(
        description="LLM hypothesis of common methodological root cause"
    )


class DisagreementTopology(BaseModel):
    """Full disagreement topology for a science (SPEC §4.B.4)."""
    science_id: str
    computed_utc: str
    tree_version: str
    per_leaf_classifications: list[LeafDisagreementClassification]
    science_summary: dict = Field(
        description="Category percentages: {ijma_pct, khilaf_pct, apparent_pct, insufficient_pct}"
    )
    khilaf_hotspots: list[str] = Field(
        description="Top 10 branch paths by proportion of active khilaf leaves"
    )
    dominant_disagreement_axes: list[DominantDisagreementAxis] = Field(
        default_factory=list
    )


# ──────────────────────────────────────────────────────────────────
# §4.B.5 — Proactive Tree Evolution Prediction
# ──────────────────────────────────────────────────────────────────


class SplitPrediction(BaseModel):
    """Prediction that a leaf needs splitting (SPEC §4.B.5)."""
    leaf_path: str
    source_id: str
    mapped_section_count: int = Field(ge=3)
    section_titles: list[str]
    predicted_sub_topics: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class GapPrediction(BaseModel):
    """Prediction that a leaf is missing from the tree (SPEC §4.B.5)."""
    source_id: str
    unmapped_section_title: str
    unmapped_section_content_preview: str = Field(max_length=200)
    nearest_leaf: str
    nearest_leaf_score: float = Field(ge=0.0, le=1.0)
    predicted_topic: str


class SourceEvolutionPredictions(BaseModel):
    """All predictions for a single source (SPEC §4.B.5)."""
    science_id: str
    source_id: str
    computed_utc: str
    tree_version: str
    split_predictions: list[SplitPrediction] = Field(default_factory=list)
    gap_predictions: list[GapPrediction] = Field(default_factory=list)
    non_topical_organization: bool = False


# ──────────────────────────────────────────────────────────────────
# §4.B.6 — Scholarly Landscape Reconstruction
# ──────────────────────────────────────────────────────────────────


class ScholarNode(BaseModel):
    """A scholar in the influence graph (SPEC §4.B.6)."""
    scholar_id: Optional[str] = Field(None, description="From scholar authority registry, null if unresolved")
    name: str
    death_date_hijri: Optional[int] = None
    school: Optional[str] = None


class InfluenceEdge(BaseModel):
    """A directed influence relationship between scholars (SPEC §4.B.6)."""
    from_scholar_id: Optional[str]
    to_scholar_id: Optional[str]
    influence_type: InfluenceType
    confidence: float = Field(ge=0.0, le=1.0)
    excerpt_ids: list[str] = Field(default_factory=list)
    inferred: bool = False


class ChronologicalPosition(BaseModel):
    """A distinct scholarly position in the timeline (SPEC §4.B.6)."""
    position_id: str = Field(description="Format: pos_{leaf_id}_{sequence}")
    position_summary: str
    first_known_proponent: str = Field(description="Scholar name")
    first_known_date_hijri: Optional[int] = None
    subsequent_proponents: list[dict] = Field(
        default_factory=list,
        description="Array of {author, date, excerpt_id}"
    )
    school_affiliations: list[str] = Field(default_factory=list)
    evidence_basis: list[str] = Field(default_factory=list)
    convergent_evidence: bool = Field(
        default=False,
        description="True when different schools reach same conclusion via different evidence"
    )


class DiscourseTransition(BaseModel):
    """A moment when the scholarly conversation shifted (SPEC §4.B.6)."""
    transition_type: DiscourseTransitionType
    from_scholar: str
    to_scholar: str
    description: str = Field(description="LLM-generated explanation of what changed")
    excerpt_ids: list[str] = Field(default_factory=list)


class EvidenceEvolutionPeriod(BaseModel):
    """How evidence changed during a historical period (SPEC §4.B.6)."""
    position_id: str
    period_start_hijri: int
    period_end_hijri: int
    dominant_evidence_types: list[str]
    example_excerpt_id: str


class SchoolPositioningSummary(BaseModel):
    """A school's stance on the topic (SPEC §4.B.6)."""
    school: str
    position_id: str
    earliest_proponent: dict = Field(description="{name, date_hijri}")
    latest_proponent: dict = Field(description="{name, date_hijri}")
    internal_unity: bool = Field(description="False if intra-school disagreement exists")
    strength_of_evidence: int = Field(description="Count of distinct evidence types used")


class ScholarlyLandscape(BaseModel):
    """Full scholarly landscape for a leaf (SPEC §4.B.6)."""
    leaf_path: str
    computed_utc: str
    tree_version: str
    excerpt_count: int
    source_count: int
    chronological_timeline: list[ChronologicalPosition] = Field(default_factory=list)
    influence_graph_nodes: list[ScholarNode] = Field(default_factory=list)
    influence_graph_edges: list[InfluenceEdge] = Field(default_factory=list)
    discourse_transitions: list[DiscourseTransition] = Field(default_factory=list)
    evidence_evolution: list[EvidenceEvolutionPeriod] = Field(default_factory=list)
    school_positioning: list[SchoolPositioningSummary] = Field(default_factory=list)
    landscape_confidence: float = Field(ge=0.0, le=1.0)
    preliminary: bool = Field(
        default=False,
        description="True when confidence < 0.4"
    )


# ──────────────────────────────────────────────────────────────────
# Forward reference resolution
# ──────────────────────────────────────────────────────────────────

TreeNode.model_rebuild()
