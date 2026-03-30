"""Tree loading and normalization for the taxonomy engine.

Loads science trees from YAML files, normalizing both v0 (nested dict)
and v1 (nodes list) formats into a uniform TreeNode representation.
See SPEC §4.A.1 for format rules and normalization semantics.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from engines.taxonomy.contracts_core import LoadedTree, TreeNode

logger = logging.getLogger(__name__)

# SPEC §6 error codes
TAX_TREE_LOAD_ERROR = "TAX_TREE_LOAD_ERROR"
TAX_INVALID_SCIENCE = "TAX_INVALID_SCIENCE"


class TreeLoadError(Exception):
    """Raised when a tree cannot be loaded or normalized."""

    def __init__(self, message: str, error_code: str = TAX_TREE_LOAD_ERROR) -> None:
        super().__init__(message)
        self.error_code = error_code


def load_tree(
    science_id: str,
    registry_path: Path,
    override_path: Path | None = None,
) -> LoadedTree:
    """Load and normalize a science tree from the registry.

    Args:
        science_id: Which science tree to load (e.g., "nahw", "aqidah").
        registry_path: Path to taxonomy_registry.yaml.
        override_path: If provided, use this YAML file instead of the registry's.

    Returns:
        A fully normalized LoadedTree ready for placement.

    Raises:
        TreeLoadError: On YAML parse failure, zero leaves, duplicate paths,
            or missing science_id in registry.
    """
    if override_path is not None:
        tree_path = override_path
        # Still need registry for display_name_ar; fall back to science_id
        display_name_ar = science_id
        registry_version = "override"
        try:
            registry_data = _load_registry(registry_path)
            for sci in registry_data.get("sciences", []):
                if sci["science_id"] == science_id:
                    display_name_ar = sci.get("display_name_ar", science_id)
                    break
        except Exception:
            pass  # Override path takes priority; registry is optional context
    else:
        registry_data = _load_registry(registry_path)
        science_entry = _find_science(registry_data, science_id)
        active_version = _find_active_version(science_entry, science_id)
        display_name_ar = science_entry.get("display_name_ar", science_id)
        registry_version = active_version["taxonomy_version"]
        relpath = active_version["relpath"]
        tree_path = registry_path.parent / relpath

    if not tree_path.exists():
        raise TreeLoadError(
            f"Tree file not found: {tree_path} for science_id={science_id}"
        )

    try:
        raw = tree_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise TreeLoadError(f"YAML parse error for {tree_path}: {e}") from e
    except UnicodeDecodeError as e:
        raise TreeLoadError(f"Encoding error for {tree_path}: {e}") from e

    if not isinstance(data, dict) or not data:
        raise TreeLoadError(f"Tree YAML is empty or not a dict: {tree_path}")

    fmt = detect_yaml_format(data)

    if fmt == "v1":
        root_nodes, tree_version, parsed_display = normalize_v1(data)
        if not override_path:
            tree_version = registry_version
        display_name_ar = parsed_display or display_name_ar
    else:
        root_nodes = normalize_v0(data)
        tree_version = registry_version if not override_path else "override"

    all_leaves = collect_leaves(root_nodes)

    if len(all_leaves) == 0:
        raise TreeLoadError(
            f"Tree has zero leaves after normalization: {tree_path}"
        )

    leaf_by_path: dict[str, TreeNode] = {}
    for leaf in all_leaves:
        if leaf.path in leaf_by_path:
            raise TreeLoadError(
                f"Duplicate leaf path '{leaf.path}' in tree {tree_path}"
            )
        leaf_by_path[leaf.path] = leaf

    loaded = LoadedTree(
        tree_version=tree_version,
        science_id=science_id,
        display_name_ar=display_name_ar,
        root_nodes=root_nodes,
        all_leaves=all_leaves,
        leaf_by_path=leaf_by_path,
        leaf_count=len(all_leaves),
    )

    logger.info(
        "Loaded tree %s: %d leaves, version=%s",
        science_id,
        loaded.leaf_count,
        loaded.tree_version,
    )
    return loaded


def detect_yaml_format(data: dict[str, Any]) -> str:
    """Detect whether YAML data is v0 (nested dict) or v1 (nodes list).

    v1: Top-level key "taxonomy" with a "nodes" array.
    v0: Everything else (nested dicts with _label/_leaf).
    """
    if "taxonomy" in data:
        taxonomy_block = data["taxonomy"]
        if isinstance(taxonomy_block, dict) and "nodes" in taxonomy_block:
            return "v1"
    return "v0"


def normalize_v1(data: dict[str, Any]) -> tuple[list[TreeNode], str, str]:
    """Normalize v1 format (nahw, sarf, balagha, imlaa) to TreeNode list.

    Returns:
        (root_nodes, tree_version, display_name_ar)
    """
    taxonomy = data["taxonomy"]
    tree_version = taxonomy.get("id", "unknown")
    display_name_ar = taxonomy.get("title", "")
    nodes_data = taxonomy.get("nodes", [])

    root_nodes = [
        _normalize_v1_node(node_data, parent_path="", parent_title="")
        for node_data in nodes_data
    ]
    return root_nodes, tree_version, display_name_ar


def _normalize_v1_node(
    node_data: dict[str, Any],
    parent_path: str,
    parent_title: str,
) -> TreeNode:
    """Recursively normalize a single v1 node."""
    node_id = node_data["id"]
    title = node_data.get("title", node_id)
    is_leaf = node_data.get("leaf", False)
    path = f"{parent_path}/{node_id}" if parent_path else node_id

    children: list[TreeNode] = []
    for child_data in node_data.get("children", []):
        children.append(
            _normalize_v1_node(child_data, parent_path=path, parent_title=title)
        )

    return TreeNode(
        id=node_id,
        title=title,
        children=children,
        is_leaf=is_leaf,
        path=path,
        parent_title=parent_title,
    )


def normalize_v0(data: dict[str, Any]) -> list[TreeNode]:
    """Normalize v0 format (aqidah) to TreeNode list.

    v0 rules (SPEC §4.A.1):
    - Top-level key is an envelope, NOT a tree node (excluded from paths).
    - _label → node title.
    - _leaf: true → marks leaf.
    - Single underscore keys (except _label, _leaf) → metadata, skip.
    - Double underscore keys (__overview) → ARE child nodes.
    - All other keys → child nodes.
    """
    # The top-level key is the envelope (e.g., "aqidah")
    envelope_keys = [k for k in data if not k.startswith("#")]
    if not envelope_keys:
        raise TreeLoadError("v0 tree has no envelope key")

    envelope_key = envelope_keys[0]
    envelope_data = data[envelope_key]

    if not isinstance(envelope_data, dict):
        raise TreeLoadError(f"v0 envelope '{envelope_key}' is not a dict")

    root_nodes: list[TreeNode] = []
    for key, value in envelope_data.items():
        if _is_v0_child_key(key) and isinstance(value, dict):
            root_nodes.append(
                _normalize_v0_node(key, value, parent_path="", parent_title="")
            )

    return root_nodes


def _normalize_v0_node(
    key: str,
    node_data: dict[str, Any],
    parent_path: str,
    parent_title: str,
) -> TreeNode:
    """Recursively normalize a single v0 node."""
    title = node_data.get("_label", key)
    is_leaf = bool(node_data.get("_leaf", False))
    path = f"{parent_path}/{key}" if parent_path else key

    children: list[TreeNode] = []
    for child_key, child_value in node_data.items():
        if _is_v0_child_key(child_key) and isinstance(child_value, dict):
            children.append(
                _normalize_v0_node(
                    child_key, child_value, parent_path=path, parent_title=title
                )
            )

    return TreeNode(
        id=key,
        title=title,
        children=children,
        is_leaf=is_leaf,
        path=path,
        parent_title=parent_title,
    )


def _is_v0_child_key(key: str) -> bool:
    """Determine if a v0 dict key represents a child node.

    Rules:
    - _label, _leaf → metadata, not children
    - Other single-underscore keys → metadata, not children
    - Double-underscore keys (__overview) → ARE children
    - All other keys → children
    """
    if key.startswith("__"):
        return True  # Double underscore = real node (naming convention)
    if key.startswith("_"):
        return False  # Single underscore = metadata
    return True


def collect_leaves(nodes: list[TreeNode]) -> list[TreeNode]:
    """Recursively collect all leaf nodes from a tree."""
    leaves: list[TreeNode] = []
    for node in nodes:
        if node.is_leaf:
            leaves.append(node)
        if node.children:
            leaves.extend(collect_leaves(node.children))
    return leaves


def build_branch_view(nodes: list[TreeNode]) -> str:
    """Format top-level branches with first-level children for Stage 1 prompt.

    Produces a human-readable list of branches and their immediate children
    so the LLM can select which branches to search.
    """
    lines: list[str] = []
    for node in nodes:
        lines.append(f"Branch: {node.id} ({node.title})")
        for child in node.children:
            leaf_marker = " [LEAF]" if child.is_leaf else ""
            child_count = f" [{len(child.children)} children]" if child.children else ""
            lines.append(f"  - {child.id} ({child.title}){leaf_marker}{child_count}")
    return "\n".join(lines)


def build_leaf_view(leaves: list[TreeNode]) -> str:
    """Format candidate leaves for Stage 2 prompt.

    Each leaf shows: path, title, parent_title — the context the LLM needs
    to score how well an excerpt matches each leaf.
    """
    lines: list[str] = []
    for leaf in leaves:
        parent_info = f" (under: {leaf.parent_title})" if leaf.parent_title else ""
        lines.append(f"- {leaf.path}: {leaf.title}{parent_info}")
    return "\n".join(lines)


# ── Internal helpers ──────────────────────────────────────────────


def _load_registry(registry_path: Path) -> dict[str, Any]:
    """Load and parse the taxonomy registry YAML."""
    if not registry_path.exists():
        raise TreeLoadError(
            f"Registry not found: {registry_path}",
            error_code=TAX_INVALID_SCIENCE,
        )
    try:
        raw = registry_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise TreeLoadError(f"Registry YAML error: {e}") from e

    if not isinstance(data, dict) or "sciences" not in data:
        raise TreeLoadError("Registry missing 'sciences' key")
    return data


def _find_science(
    registry_data: dict[str, Any], science_id: str
) -> dict[str, Any]:
    """Find a science entry in the registry by science_id."""
    for sci in registry_data.get("sciences", []):
        if sci.get("science_id") == science_id:
            return sci
    raise TreeLoadError(
        f"science_id '{science_id}' not found in registry",
        error_code=TAX_INVALID_SCIENCE,
    )


def _find_active_version(
    science_entry: dict[str, Any], science_id: str
) -> dict[str, Any]:
    """Find the active version for a science entry."""
    for ver in science_entry.get("versions", []):
        if ver.get("status") == "active":
            return ver
    raise TreeLoadError(
        f"No active version for science_id '{science_id}'",
        error_code=TAX_INVALID_SCIENCE,
    )
