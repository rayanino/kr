"""Placement algorithm for the taxonomy engine.

Handles excerpt type classification, placement routing, and orchestration
of the two-stage LLM placement process. The LLM interaction is abstracted
behind a PlacementAdapter protocol — Session 1 uses a stub, Session 2
provides the real LLM-backed implementation.

See SPEC §4.A.2 (placement algorithm) and §4.A.3 (routing thresholds).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from engines.taxonomy.contracts_core import (
    BranchSelection,
    ExcerptType,
    LifecycleStage,
    LoadedTree,
    PlacementAdditions,
    PlacementRanking,
    PlacementRoute,
    TreeNode,
)

logger = logging.getLogger(__name__)

# SPEC §7.1 — Global configuration parameters
LIVE_THRESHOLD_TEACHING = 0.80
LIVE_THRESHOLD_EDITORIAL = 0.85
STAGING_THRESHOLD = 0.50
TIE_THRESHOLD = 0.10
HIERARCHICAL_SEARCH_LEAF_LIMIT = 200
STAGE1_BRANCH_COUNT = 3


# ── Adapter Protocol ──────────────────────────────────────────────


@runtime_checkable
class PlacementAdapter(Protocol):
    """Interface for LLM-backed placement operations.

    Session 1: StubPlacementAdapter raises NotImplementedError.
    Session 2: LLMPlacementAdapter uses CLIInstructorAdapter.
    """

    def run_stage1(
        self, excerpt: dict, tree: LoadedTree
    ) -> BranchSelection: ...

    def run_stage2(
        self, excerpt: dict, candidates: list[TreeNode]
    ) -> PlacementRanking: ...


class StubPlacementAdapter:
    """Session 1 stub — raises NotImplementedError for all LLM calls."""

    def run_stage1(
        self, excerpt: dict, tree: LoadedTree
    ) -> BranchSelection:
        raise NotImplementedError("LLM placement deferred to Session 2")

    def run_stage2(
        self, excerpt: dict, candidates: list[TreeNode]
    ) -> PlacementRanking:
        raise NotImplementedError("LLM placement deferred to Session 2")


# ── Excerpt Type Classification ───────────────────────────────────

# SPEC §4.A.3: Types that are ALWAYS staged (never live)
_ALWAYS_STAGED_FUNCTIONS = frozenset({"structural_transition", "cross_reference"})

# SPEC §4.A.3: Editorial type
_EDITORIAL_FUNCTIONS = frozenset({"editorial_note"})


def classify_excerpt_type(excerpt: dict) -> ExcerptType:
    """Classify an excerpt's type for routing purposes (SPEC §4.A.3).

    Returns:
        ALWAYS_STAGED for structural_transition, cross_reference.
        EDITORIAL for editorial_note.
        TEACHING for all other known primary_function values.
        EDITORIAL for missing/null/unknown (safe default — stricter threshold).
    """
    primary_function = excerpt.get("primary_function")

    if primary_function is None or primary_function == "":
        return ExcerptType.EDITORIAL  # Safe default per SPEC

    if primary_function in _ALWAYS_STAGED_FUNCTIONS:
        return ExcerptType.ALWAYS_STAGED

    if primary_function in _EDITORIAL_FUNCTIONS:
        return ExcerptType.EDITORIAL

    return ExcerptType.TEACHING


# ── Placement Routing ─────────────────────────────────────────────


def route_excerpt(
    ranking: PlacementRanking,
    excerpt_type: ExcerptType,
) -> tuple[PlacementRoute, str | None, float | None, bool]:
    """Apply type-based threshold routing to a placement ranking (SPEC §4.A.3).

    Args:
        ranking: The Stage 2 ranking result with scored leaves.
        excerpt_type: Classification of the excerpt.

    Returns:
        (route, leaf_path, confidence, tie_detected)
        - route: Where the excerpt goes (live/staged/unplaced)
        - leaf_path: Best leaf path, or None if unplaced
        - confidence: Top score, or None if no candidates
        - tie_detected: True if top 2 within TIE_THRESHOLD and both ≥ STAGING_THRESHOLD
    """
    sorted_rankings = sorted(ranking.rankings, key=lambda r: r.score, reverse=True)
    top = sorted_rankings[0]
    top_score = top.score
    top_path = top.leaf_path

    # Tie detection: top 2 within TIE_THRESHOLD and both ≥ STAGING_THRESHOLD
    tie_detected = False
    if len(sorted_rankings) >= 2:
        second_score = sorted_rankings[1].score
        if (
            top_score - second_score <= TIE_THRESHOLD
            and top_score >= STAGING_THRESHOLD
            and second_score >= STAGING_THRESHOLD
        ):
            tie_detected = True

    # Route based on excerpt type and score
    route = _compute_route(top_score, excerpt_type)

    # Tie override: if would be LIVE but tie detected, force to staged
    if tie_detected and route == PlacementRoute.LIVE:
        if excerpt_type == ExcerptType.EDITORIAL:
            route = PlacementRoute.STAGED_FRONT_MATTER
        else:
            route = PlacementRoute.STAGED_LOW_CONFIDENCE

    # Unplaced excerpts have no confirmed leaf
    if route == PlacementRoute.UNPLACED:
        return route, None, top_score, tie_detected

    return route, top_path, top_score, tie_detected


def _compute_route(score: float, excerpt_type: ExcerptType) -> PlacementRoute:
    """Compute the base route before tie override."""
    if excerpt_type == ExcerptType.ALWAYS_STAGED:
        if score >= STAGING_THRESHOLD:
            return PlacementRoute.STAGED_FRONT_MATTER
        return PlacementRoute.UNPLACED

    if excerpt_type == ExcerptType.EDITORIAL:
        if score >= LIVE_THRESHOLD_EDITORIAL:
            return PlacementRoute.LIVE
        if score >= STAGING_THRESHOLD:
            return PlacementRoute.STAGED_FRONT_MATTER
        return PlacementRoute.UNPLACED

    # TEACHING (default)
    if score >= LIVE_THRESHOLD_TEACHING:
        return PlacementRoute.LIVE
    if score >= STAGING_THRESHOLD:
        return PlacementRoute.STAGED_LOW_CONFIDENCE
    return PlacementRoute.UNPLACED


# ── Placement Orchestration ───────────────────────────────────────


def _should_skip_stage1(tree: LoadedTree) -> bool:
    """Trees with ≤ HIERARCHICAL_SEARCH_LEAF_LIMIT leaves skip Stage 1."""
    return tree.leaf_count <= HIERARCHICAL_SEARCH_LEAF_LIMIT


def _collect_branch_leaves(
    tree: LoadedTree, branch_ids: list[str]
) -> list[TreeNode]:
    """Collect all leaves within the selected branches."""
    from engines.taxonomy.src.tree_loader import collect_leaves

    branch_set = set(branch_ids)
    leaves: list[TreeNode] = []
    for root in tree.root_nodes:
        if root.id in branch_set:
            leaves.extend(collect_leaves([root]))
    return leaves


def place_excerpt(
    excerpt: dict,
    tree: LoadedTree,
    adapter: PlacementAdapter,
) -> PlacementAdditions:
    """Orchestrate placement for one excerpt (SPEC §4.A.2).

    Runs Stage 1 (branch selection for large trees), Stage 2 (leaf ranking),
    then applies type-based routing.
    """
    now_utc = datetime.now(timezone.utc).isoformat()
    excerpt_type = classify_excerpt_type(excerpt)

    # Stage 1: Candidate generation
    if _should_skip_stage1(tree):
        candidates = tree.all_leaves
    else:
        stage1_result = adapter.run_stage1(excerpt, tree)
        if stage1_result.no_match:
            return PlacementAdditions(
                lifecycle_stage=LifecycleStage.UNPLACED,
                placement_route=PlacementRoute.UNPLACED,
                unplaced_reason="Stage 1: no matching branch",
                best_candidates=[],
                placed_utc=now_utc,
                taxonomy_version_at_placement=tree.tree_version,
            )
        candidates = _collect_branch_leaves(tree, stage1_result.selected_branches)
        # If proposed_leaf exists and is valid, add to candidates
        proposed = excerpt.get("proposed_leaf")
        if proposed and proposed in tree.leaf_by_path:
            candidate_paths = {c.path for c in candidates}
            if proposed not in candidate_paths:
                candidates.append(tree.leaf_by_path[proposed])

        if not candidates:
            return PlacementAdditions(
                lifecycle_stage=LifecycleStage.UNPLACED,
                placement_route=PlacementRoute.UNPLACED,
                unplaced_reason="Stage 1: selected branches contain no leaves",
                best_candidates=[],
                placed_utc=now_utc,
                taxonomy_version_at_placement=tree.tree_version,
            )

    # Stage 2: Leaf ranking
    ranking = adapter.run_stage2(excerpt, candidates)

    # Route based on type and score
    route, leaf_path, confidence, tie_detected = route_excerpt(ranking, excerpt_type)

    # Build placement additions
    lifecycle = _route_to_lifecycle(route)

    if route == PlacementRoute.UNPLACED:
        # Include top 3 candidates for diagnostics
        sorted_rankings = sorted(
            ranking.rankings, key=lambda r: r.score, reverse=True
        )
        best_3 = [
            {"leaf_path": r.leaf_path, "score": r.score, "reasoning": r.reasoning}
            for r in sorted_rankings[:3]
        ]
        return PlacementAdditions(
            lifecycle_stage=lifecycle,
            placement_route=route,
            unplaced_reason=f"No candidate scored ≥{STAGING_THRESHOLD}",
            best_candidates=best_3,
            placement_confidence=confidence,
            placed_utc=now_utc,
            taxonomy_version_at_placement=tree.tree_version,
            primary_topic_used=ranking.primary_topic_used,
            tie_detected=tie_detected,
        )

    # Match reasoning to the selected leaf (rankings may be unsorted)
    reasoning = next(
        (r.reasoning for r in ranking.rankings if r.leaf_path == leaf_path),
        ranking.rankings[0].reasoning if ranking.rankings else None,
    )

    return PlacementAdditions(
        lifecycle_stage=lifecycle,
        placement_route=route,
        confirmed_leaf=leaf_path,
        placement_confidence=confidence,
        placed_utc=now_utc,
        taxonomy_version_at_placement=tree.tree_version,
        placement_reasoning=reasoning,
        primary_topic_used=ranking.primary_topic_used,
        review_metadata={"review_outcome": "auto_approved"},
        tie_detected=tie_detected,
    )


def _route_to_lifecycle(route: PlacementRoute) -> LifecycleStage:
    """Map PlacementRoute to LifecycleStage."""
    if route == PlacementRoute.LIVE:
        return LifecycleStage.PLACED
    if route in (
        PlacementRoute.STAGED_LOW_CONFIDENCE,
        PlacementRoute.STAGED_FRONT_MATTER,
    ):
        return LifecycleStage.STAGED
    if route == PlacementRoute.PENDING_NO_TREE:
        return LifecycleStage.PENDING_NO_TREE
    return LifecycleStage.UNPLACED
