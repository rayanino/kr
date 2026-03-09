"""Taxonomy engine — tracer bullet entry point.

Places excerpts into a science tree.
Simple strategy: create a minimal tree and place all excerpts at a single leaf.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def process(input_path: Path, output_path: Path, config: dict) -> None:
    """Place excerpts into taxonomy tree.

    Args:
        input_path: Path to ExcerptStream JSON.
        output_path: Path to write taxonomy output JSON (tree + placements).
        config: Engine configuration.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    excerpt_stream = json.loads(input_path.read_text(encoding="utf-8"))
    source_id = excerpt_stream["source_id"]
    excerpts = excerpt_stream["excerpts"]

    now_utc = datetime.now(timezone.utc).isoformat()

    # Build a minimal science tree for nahw
    tree = {
        "id": "nahw",
        "title": "النحو",
        "children": [
            {
                "id": "nahw/kalaam",
                "title": "باب الكلام وما يتألف منه",
                "children": [
                    {
                        "id": "nahw/kalaam/definition",
                        "title": "تعريف الكلام",
                        "children": [],
                        "leaf": True,
                    },
                    {
                        "id": "nahw/kalaam/parts",
                        "title": "أقسام الكلمة",
                        "children": [],
                        "leaf": True,
                    },
                ],
                "leaf": False,
            },
        ],
        "leaf": False,
    }

    # Place all excerpts at the first leaf
    placements = []
    for excerpt in excerpts:
        placement = {
            "excerpt_id": excerpt["excerpt_id"],
            "source_id": source_id,
            "confirmed_leaf": "nahw/kalaam/definition",
            "placement_confidence": 0.6,
            "placed_utc": now_utc,
            "review_metadata": {
                "review_outcome": "auto_approved",
                "evolution_proposal_id": None,
                "reviewer_notes": "Tracer bullet: all excerpts placed at default leaf",
            },
            "verified_flagged_status": "verified",
            "taxonomy_version_at_placement": "tracer_v0",
            "placement_reasoning": "Tracer bullet stub — all excerpts placed at nahw/kalaam/definition",
            "proposed_leaf_override": False,
            "proposed_leaf_original": excerpt.get("proposed_leaf"),
            "override_reason": None,
        }
        placements.append(placement)

    # Coverage analysis
    leaf_ids = _collect_leaf_ids(tree)
    coverage = []
    for lid in leaf_ids:
        placed_here = [p for p in placements if p["confirmed_leaf"] == lid]
        coverage.append({
            "leaf_id": lid,
            "excerpt_count": len(placed_here),
            "gap_type": None if placed_here else "empty_leaf",
        })

    taxonomy_output = {
        "source_id": source_id,
        "tree": tree,
        "placements": placements,
        "coverage": coverage,
        "taxonomy_version": "tracer_v0",
    }

    output_path.write_text(
        json.dumps(taxonomy_output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _collect_leaf_ids(node: dict) -> list[str]:
    """Recursively collect all leaf IDs from a tree node."""
    if node.get("leaf"):
        return [node["id"]]
    result = []
    for child in node.get("children", []):
        result.extend(_collect_leaf_ids(child))
    return result
