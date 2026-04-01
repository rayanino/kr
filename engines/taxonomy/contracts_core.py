"""Taxonomy Engine Core v1 Contracts — Pydantic models for placement.

Derived from SPEC.md §2, §3, §4. Stripped to core-only (24 capabilities).
For the full original contracts with evolution, coverage, landscape models,
see reference/SPEC_FULL_ORIGINAL.md.

When SPEC.md and these models disagree, update the models — they must match the SPEC.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────


class PlacementRoute(str, Enum):
    """Where an excerpt ends up after placement (SPEC §4.A.3)."""
    LIVE = "live"
    STAGED_LOW_CONFIDENCE = "staged_low_confidence"
    STAGED_FRONT_MATTER = "staged_front_matter"
    UNPLACED = "unplaced"
    PENDING_NO_TREE = "pending_no_tree"


class LifecycleStage(str, Enum):
    """Excerpt lifecycle stage after taxonomy processing."""
    PLACED = "placed"
    STAGED = "staged"
    UNPLACED = "unplaced"
    PENDING_NO_TREE = "pending_no_tree"


class ExcerptType(str, Enum):
    """Classification for type-based routing (SPEC §4.A.3).

    TEACHING: rule_statement, opinion_statement, definition, etc.
    EDITORIAL: editorial_note — eligible for live at ≥0.85.
    ALWAYS_STAGED: structural_transition, cross_reference — never live.
    """
    TEACHING = "teaching"
    EDITORIAL = "editorial"
    ALWAYS_STAGED = "always_staged"


class TaxonomyWarning(str, Enum):
    """Batch-level diagnostic warnings (SPEC §4.A.6)."""
    POSSIBLE_SCIENCE_MISMATCH = "TAX_POSSIBLE_SCIENCE_MISMATCH"
    HIGH_UNPLACEMENT_RATE = "TAX_HIGH_UNPLACEMENT_RATE"
    LEAF_CONCENTRATION = "TAX_LEAF_CONCENTRATION"
    HIGH_EDITORIAL_PLACEMENT = "TAX_HIGH_EDITORIAL_PLACEMENT"


# ──────────────────────────────────────────────────────────────────
# §2.2 — Run Configuration
# ──────────────────────────────────────────────────────────────────


class RunConfig(BaseModel):
    """Configuration for a single taxonomy run (SPEC §2.2)."""
    science_id: str = Field(description="Which science tree to place against")
    input_path: str = Field(description="Path to excerpts JSONL file")
    batch_id: str = Field(description="Unique batch identifier")
    tree_override_path: Optional[str] = Field(
        default=None,
        description="Override registry's active tree. For testing.",
    )


# ──────────────────────────────────────────────────────────────────
# §4.A.1 — Tree Loading (internal representation)
# ──────────────────────────────────────────────────────────────────


@dataclass
class TreeNode:
    """A node in the internal tree representation.

    Both v0 (nested dict / aqidah) and v1 (nodes list / nahw etc.)
    YAML formats are normalized into this structure at load time.
    """
    id: str
    title: str
    children: list[TreeNode] = field(default_factory=list)
    is_leaf: bool = False
    path: str = ""           # Full path from root, e.g. "almajrurat/huruf_aljar/..."
    parent_title: str = ""   # Parent node's Arabic title


@dataclass
class LoadedTree:
    """Complete loaded and normalized tree (SPEC §4.A.1)."""
    tree_version: str
    science_id: str
    display_name_ar: str
    root_nodes: list[TreeNode]
    all_leaves: list[TreeNode]
    leaf_by_path: dict[str, TreeNode]
    leaf_count: int


# ──────────────────────────────────────────────────────────────────
# §4.A.2 — LLM Response Models (Stage 1 and Stage 2)
# ──────────────────────────────────────────────────────────────────


class BranchSelection(BaseModel):
    """Stage 1 response: which branches to search (SPEC §4.A.2).

    Used only for trees with > 200 leaves (hierarchical search).
    """
    selected_branches: list[str] = Field(
        description="1-3 branch IDs, ranked by likelihood",
        min_length=0,
        max_length=3,
    )
    no_match: bool = Field(
        default=False,
        description="True if no branch fits the excerpt at all",
    )


class LeafScore(BaseModel):
    """A single candidate leaf with its score and reasoning."""
    leaf_path: str = Field(
        description="Full path from root (e.g., 'almajrurat/huruf_aljar/ma3ani_huruf_aljar')",
    )
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str


class PlacementRanking(BaseModel):
    """Stage 2 response: scored candidate leaves (SPEC §4.A.2)."""
    rankings: list[LeafScore] = Field(min_length=1)
    primary_topic_used: str = Field(
        description="Which of the excerpt's topics drove the placement decision",
    )


# ──────────────────────────────────────────────────────────────────
# §3.1–3.4 — Placement Output Fields
# ──────────────────────────────────────────────────────────────────


class PlacementAdditions(BaseModel):
    """Fields the taxonomy engine ADDS to an excerpt at placement (SPEC §3.1).

    AUTHORITATIVE runtime contract. All upstream fields are preserved
    verbatim (D-023). These are the taxonomy-specific additions merged
    onto the original excerpt.

    See also:
    - contracts.py:PlacedExcerptAdditions (DEPRECATED full-SPEC version
      with deferred fields like verified_flagged_status)
    - synthesis/contracts.py:TaxonomyPlacedExcerpt (synthesis input model
      matching this output shape)
    """
    lifecycle_stage: LifecycleStage
    placement_route: PlacementRoute

    # Present for placed and staged excerpts
    confirmed_leaf: Optional[str] = Field(
        default=None,
        description="Leaf path in tree. None for unplaced/pending.",
    )
    placement_confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
    )
    placed_utc: Optional[str] = None
    taxonomy_version_at_placement: Optional[str] = None
    placement_reasoning: Optional[str] = None
    primary_topic_used: Optional[str] = None
    review_metadata: Optional[dict] = None
    tie_detected: bool = False

    # Present for unplaced excerpts
    unplaced_reason: Optional[str] = None
    best_candidates: Optional[list[dict]] = None

    # Present for pending-no-tree
    declared_science_id: Optional[str] = None
    pending_since_utc: Optional[str] = None


# ──────────────────────────────────────────────────────────────────
# §3.5 — Batch Report
# ──────────────────────────────────────────────────────────────────


class BatchReport(BaseModel):
    """Batch-level diagnostics (SPEC §3.5 / §4.A.6)."""
    batch_id: str
    science_id: str
    tree_version: str
    timestamp_utc: str
    total_excerpts: int
    placed_count: int = 0
    staged_count: int = 0
    unplaced_count: int = 0
    pending_no_tree_count: int = 0
    confidence_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Histogram buckets: '0.0-0.1', '0.1-0.2', ... '0.9-1.0'",
    )
    median_confidence: Optional[float] = None
    leaf_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Leaf path → excerpt count (live + staged)",
    )
    editorial_placement_rate: Optional[float] = Field(
        default=None,
        description="Fraction of editorial excerpts that reached live tree",
    )
    warnings: list[str] = Field(default_factory=list)
