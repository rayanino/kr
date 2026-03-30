"""Test factories and fixtures for the taxonomy engine.

All defaults use real Arabic text from the KR test corpus.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pytest

from engines.taxonomy.contracts_core import (
    ExcerptType,
    LeafScore,
    LifecycleStage,
    LoadedTree,
    PlacementAdditions,
    PlacementRanking,
    PlacementRoute,
    RunConfig,
    TreeNode,
    BranchSelection,
)
from engines.taxonomy.src.tree_loader import load_tree

# ── Paths ─────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _PROJECT_ROOT / "library" / "sciences" / "taxonomy_registry.yaml"
_INTEGRATION_EXCERPTS = (
    _PROJECT_ROOT
    / "integration_tests"
    / "smoke_fix_20260329"
    / "ibn_aqil_v3"
    / "excerpts.jsonl"
)

# ── Default Arabic text (from ibn_aqil excerpt 0) ─────────────────

_DEFAULT_PRIMARY_TEXT = (
    "بسم الله الرحمن الرحيم\n"
    "\u200c\u200cحروف الجر\n"
    "هاك حروف الجر وهي من إلى\n"
    "… حتى خلا حاشا عدا في عن على\n"
    "مذ منذ رب اللام كي واو وتا … والكاف والباء ولعل ومتى\n"
    "هذه الحروف العشرون كلها مختصة بالأسماء وهي تعمل فيها الجر"
)


# ── Factory functions ─────────────────────────────────────────────


def make_excerpt(**overrides: Any) -> dict:
    """Create a valid excerpt dict with real Arabic defaults."""
    base = {
        "excerpt_id": "exc_src_test0001_div_src_test0001_3_000_0_0",
        "source_id": "src_test0001",
        "div_id": "div_src_test0001_3_000",
        "chunk_index": 0,
        "unit_index": 0,
        "div_path": ["حروف الجر"],
        "primary_text": _DEFAULT_PRIMARY_TEXT,
        "text_snippet": "بسم الله الرحمن الرحيم",
        "start_word": 0,
        "end_word": 58,
        "segment_indices": [0, 1, 2, 3],
        "physical_pages": {"volume": 1, "start_page": 3, "end_page": 3},
        "primary_function": "rule_statement",
        "secondary_functions": ["structural_transition"],
        "content_types": ["structural_transition", "rule_statement"],
        "description_arabic": (
            "تعداد حروف الجر العشرين وبيان اختصاصها بالأسماء وعملها الجر فيها"
        ),
        "self_containment": "FULL",
        "self_containment_notes": None,
        "context_hint": None,
        "primary_author_layer": {
            "layer_id": "sharh",
            "author_id": "unknown",
            "coverage_pct": 1.0,
            "rule_applied": "LA-4",
        },
        "attribution_confidence": None,
        "quoted_scholars": [],
        "school": None,
        "school_confidence": None,
        "excerpt_topic": ["حروف الجر", "تعداد حروف الجر"],
        "terminology_variants": [],
        "evidence_refs": [],
        "takhrij_data": None,
        "cross_references": [],
        "footnotes_relevant": [],
        "consensus_metadata": None,
        "gate_flags": [],
        "review_flags": [],
    }
    base.update(overrides)
    return base


def make_run_config(**overrides: Any) -> RunConfig:
    """Create a valid RunConfig with sensible defaults."""
    defaults = {
        "science_id": "nahw",
        "input_path": str(_INTEGRATION_EXCERPTS),
        "batch_id": "test_batch_001",
    }
    defaults.update(overrides)
    return RunConfig(**defaults)


def make_placement_additions(**overrides: Any) -> PlacementAdditions:
    """Create a fully populated PlacementAdditions for placed excerpts."""
    defaults: dict[str, Any] = {
        "lifecycle_stage": LifecycleStage.PLACED,
        "placement_route": PlacementRoute.LIVE,
        "confirmed_leaf": "almajrurat/huruf_aljar/ma3ani_huruf_aljar",
        "placement_confidence": 0.92,
        "placed_utc": "2026-03-30T12:00:00+00:00",
        "taxonomy_version_at_placement": "nahw_v1_0",
        "placement_reasoning": "Excerpt discusses حروف الجر and their meanings",
        "primary_topic_used": "حروف الجر",
        "review_metadata": {"review_outcome": "auto_approved"},
        "tie_detected": False,
    }
    defaults.update(overrides)
    return PlacementAdditions(**defaults)


def make_ranking(
    scores: list[tuple[str, float]],
    primary_topic: str = "حروف الجر",
) -> PlacementRanking:
    """Create a PlacementRanking from (leaf_path, score) pairs."""
    return PlacementRanking(
        rankings=[
            LeafScore(leaf_path=path, score=score, reasoning=f"Score {score}")
            for path, score in scores
        ],
        primary_topic_used=primary_topic,
    )


# ── Mock Adapter ──────────────────────────────────────────────────


class MockPlacementAdapter:
    """Configurable mock for testing routing and engine without LLM.

    Accepts either a fixed PlacementRanking or a callable that receives
    (excerpt, candidates) and returns a PlacementRanking.
    """

    def __init__(
        self,
        stage2_result: PlacementRanking | Callable[..., PlacementRanking],
        stage1_result: BranchSelection | None = None,
    ) -> None:
        self._stage2_result = stage2_result
        self._stage1_result = stage1_result
        self.stage1_calls: list[tuple[dict, LoadedTree]] = []
        self.stage2_calls: list[tuple[dict, list[TreeNode]]] = []

    def run_stage1(
        self, excerpt: dict, tree: LoadedTree
    ) -> BranchSelection:
        self.stage1_calls.append((excerpt, tree))
        if self._stage1_result is not None:
            return self._stage1_result
        # Default: select first 3 root branches
        branch_ids = [n.id for n in tree.root_nodes[:3]]
        return BranchSelection(selected_branches=branch_ids)

    def run_stage2(
        self, excerpt: dict, candidates: list[TreeNode]
    ) -> PlacementRanking:
        self.stage2_calls.append((excerpt, candidates))
        if callable(self._stage2_result):
            return self._stage2_result(excerpt, candidates)
        return self._stage2_result


# ── Pytest Fixtures ───────────────────────────────────────────────


@pytest.fixture
def nahw_tree() -> LoadedTree:
    """Load the real nahw science tree (v1 format, 226 leaves)."""
    return load_tree("nahw", _REGISTRY_PATH)


@pytest.fixture
def aqidah_tree() -> LoadedTree:
    """Load the real aqidah science tree (v0 format, 30 leaves)."""
    return load_tree("aqidah", _REGISTRY_PATH)


@pytest.fixture
def all_trees() -> dict[str, LoadedTree]:
    """Load all 5 science trees."""
    trees = {}
    for sid in ["nahw", "sarf", "balagha", "imlaa", "aqidah"]:
        trees[sid] = load_tree(sid, _REGISTRY_PATH)
    return trees


@pytest.fixture
def real_excerpts() -> list[dict]:
    """Load first 5 real excerpts from the integration test JSONL."""
    excerpts = []
    if _INTEGRATION_EXCERPTS.exists():
        with _INTEGRATION_EXCERPTS.open(encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 5:
                    break
                excerpts.append(json.loads(line.strip()))
    return excerpts


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Temporary output directory for writer tests."""
    return tmp_path / "taxonomy_output"
