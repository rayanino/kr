"""Taxonomy engine orchestrator.

Entry point for taxonomy placement runs. Loads trees, iterates excerpts,
delegates placement to the placer, validates and writes results, then
produces a batch report.

See SPEC §2 (input), §3 (output), §4.A (behavioral rules), §6 (errors).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from engines.taxonomy.contracts_core import (
    BatchReport,
    LifecycleStage,
    LoadedTree,
    PlacementAdditions,
    PlacementRoute,
    RunConfig,
)
from engines.taxonomy.src.diagnostics import compute_batch_report
from engines.taxonomy.src.placer import (
    PlacementAdapter,
    StubPlacementAdapter,
    place_excerpt,
)
from engines.taxonomy.src.tree_loader import (
    TreeLoadError,
    load_tree,
)
from engines.taxonomy.src.validator import validate_placement, verify_written_file
from engines.taxonomy.src.writer import (
    write_pending_excerpt,
    write_placed_excerpt,
    write_staged_excerpt,
    write_unplaced_excerpt,
)

logger = logging.getLogger(__name__)

# SPEC §2.1 — Required fields (rejection on absence)
_REQUIRED_FIELDS = ("excerpt_id", "source_id", "primary_text", "excerpt_topic")

# SPEC §2.1 — Expected fields (warning on absence)
_EXPECTED_FIELDS = (
    "description_arabic",
    "primary_function",
    "content_types",
    "div_path",
)

# Default registry location
_DEFAULT_REGISTRY = Path("library/sciences/taxonomy_registry.yaml")


class TaxonomyEngineError(Exception):
    """Fatal batch-level error."""

    def __init__(self, message: str, error_code: str) -> None:
        super().__init__(message)
        self.error_code = error_code


def run(
    config: RunConfig,
    adapter: PlacementAdapter | None = None,
    base_path: Path | None = None,
    registry_path: Path | None = None,
) -> BatchReport:
    """Run a taxonomy placement batch.

    Args:
        config: Run configuration (science_id, input_path, batch_id).
        adapter: Placement adapter (None → StubPlacementAdapter).
        base_path: Output base directory (None → library/sciences/).
        registry_path: Path to taxonomy_registry.yaml.

    Returns:
        BatchReport with placement statistics and warnings.

    Raises:
        TaxonomyEngineError: On batch-fatal conditions (tree load failure).
    """
    if adapter is None:
        adapter = StubPlacementAdapter()

    if base_path is None:
        base_path = Path("library/sciences")

    if registry_path is None:
        registry_path = _DEFAULT_REGISTRY

    now_utc = datetime.now(timezone.utc).isoformat()

    # Validate config
    _validate_config(config)

    # Load tree (or route everything to pending_no_tree)
    tree = None
    try:
        override = Path(config.tree_override_path) if config.tree_override_path else None
        tree = load_tree(config.science_id, registry_path, override)
    except TreeLoadError as e:
        if e.error_code == "TAX_INVALID_SCIENCE":
            logger.warning(
                "TAX_INVALID_SCIENCE: %s — routing all to pending_no_tree",
                e,
            )
        else:
            raise TaxonomyEngineError(str(e), e.error_code) from e

    # Read excerpts from JSONL
    input_path = Path(config.input_path)
    excerpts = _read_excerpts(input_path)

    results: list[dict] = []

    for excerpt in excerpts:
        result = _process_excerpt(
            excerpt=excerpt,
            tree=tree,
            adapter=adapter,
            config=config,
            base_path=base_path,
            now_utc=now_utc,
        )
        if result is not None:
            results.append(result)

    # Compute and write batch report
    report = compute_batch_report(results, config, tree, now_utc)
    _write_batch_report(report, config.science_id, base_path)

    logger.info(
        "Batch %s complete: %d placed, %d staged, %d unplaced, %d pending",
        config.batch_id,
        report.placed_count,
        report.staged_count,
        report.unplaced_count,
        report.pending_no_tree_count,
    )

    return report


def _validate_config(config: RunConfig) -> None:
    """Validate run configuration."""
    if not config.science_id:
        raise TaxonomyEngineError(
            "science_id is empty", "TAX_MISSING_REQUIRED_FIELD"
        )
    if not config.batch_id:
        raise TaxonomyEngineError(
            "batch_id is empty", "TAX_MISSING_REQUIRED_FIELD"
        )
    input_path = Path(config.input_path)
    if not input_path.exists():
        raise TaxonomyEngineError(
            f"input_path does not exist: {input_path}",
            "TAX_MISSING_REQUIRED_FIELD",
        )


def _read_excerpts(input_path: Path) -> list[dict]:
    """Read excerpts from a JSONL file."""
    excerpts: list[dict] = []
    with input_path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                excerpts.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.error(
                    "TAX_MISSING_REQUIRED_FIELD: JSONL parse error at line %d: %s",
                    line_num,
                    e,
                )
    return excerpts


def _process_excerpt(
    excerpt: dict,
    tree: LoadedTree | None,
    adapter: PlacementAdapter,
    config: RunConfig,
    base_path: Path,
    now_utc: str,
) -> dict | None:
    """Process a single excerpt through validation, placement, and writing.

    Returns the merged result dict, or None if the excerpt was rejected.
    """
    excerpt_id = excerpt.get("excerpt_id", "<unknown>")

    # Validate required fields
    missing = [f for f in _REQUIRED_FIELDS if not excerpt.get(f)]
    if missing:
        logger.error(
            "TAX_MISSING_REQUIRED_FIELD: excerpt %s missing %s — skipped",
            excerpt_id,
            missing,
        )
        return None

    # Check excerpt_topic is a non-empty list
    topics = excerpt.get("excerpt_topic")
    if not isinstance(topics, list) or len(topics) == 0:
        logger.error(
            "TAX_MISSING_REQUIRED_FIELD: excerpt %s has empty/invalid excerpt_topic — skipped",
            excerpt_id,
        )
        return None

    # Warn on missing expected fields
    for field in _EXPECTED_FIELDS:
        if excerpt.get(field) is None:
            logger.warning(
                "TAX_MISSING_EXPECTED_FIELD: excerpt %s missing %s",
                excerpt_id,
                field,
            )

    # No tree → pending_no_tree
    if tree is None:
        additions = PlacementAdditions(
            lifecycle_stage=LifecycleStage.PENDING_NO_TREE,
            placement_route=PlacementRoute.PENDING_NO_TREE,
            declared_science_id=config.science_id,
            pending_since_utc=now_utc,
        )
        merged = {**excerpt, **additions.model_dump(mode="json")}
        write_pending_excerpt(excerpt, additions, config.science_id, base_path)
        return merged

    # Attempt placement
    try:
        additions = place_excerpt(excerpt, tree, adapter)
    except NotImplementedError:
        # Stub adapter — route to unplaced
        additions = PlacementAdditions(
            lifecycle_stage=LifecycleStage.UNPLACED,
            placement_route=PlacementRoute.UNPLACED,
            unplaced_reason="LLM placement not available (Session 2)",
            placed_utc=now_utc,
            taxonomy_version_at_placement=tree.tree_version,
        )
    except Exception as e:
        logger.error(
            "TAX_LLM_FAILURE: excerpt %s placement failed: %s",
            excerpt_id,
            e,
        )
        additions = PlacementAdditions(
            lifecycle_stage=LifecycleStage.UNPLACED,
            placement_route=PlacementRoute.UNPLACED,
            unplaced_reason=f"Placement error: {e}",
            placed_utc=now_utc,
            taxonomy_version_at_placement=tree.tree_version,
        )

    # Validate and write
    merged = {**excerpt, **additions.model_dump(mode="json")}
    route = additions.placement_route

    if route == PlacementRoute.LIVE:
        # Validate leaf exists (confirmed_leaf must be non-None for LIVE)
        confirmed = additions.confirmed_leaf
        if confirmed is None or not validate_placement(confirmed, tree):
            logger.error(
                "TAX_PLACEMENT_INTEGRITY_ERROR: excerpt %s — leaf '%s' not in tree",
                excerpt_id,
                additions.confirmed_leaf,
            )
            return _reroute_to_unplaced(
                excerpt, tree, now_utc, "Leaf not found in tree"
            )
        path = write_placed_excerpt(
            excerpt, additions, config.science_id, base_path
        )
        if not verify_written_file(path, excerpt["primary_text"]):
            logger.error(
                "TAX_PLACEMENT_INTEGRITY_ERROR: excerpt %s — byte mismatch after write",
                excerpt_id,
            )
            path.unlink(missing_ok=True)
            return _reroute_to_unplaced(
                excerpt, tree, now_utc, "Post-write byte mismatch"
            )

    elif route in (
        PlacementRoute.STAGED_LOW_CONFIDENCE,
        PlacementRoute.STAGED_FRONT_MATTER,
    ):
        confirmed = additions.confirmed_leaf
        if confirmed is None or not validate_placement(confirmed, tree):
            logger.error(
                "TAX_PLACEMENT_INTEGRITY_ERROR: excerpt %s — leaf '%s' not in tree",
                excerpt_id,
                additions.confirmed_leaf,
            )
            return _reroute_to_unplaced(
                excerpt, tree, now_utc, "Leaf not found in tree"
            )
        path = write_staged_excerpt(
            excerpt, additions, config.science_id, base_path
        )
        if not verify_written_file(path, excerpt["primary_text"]):
            logger.error(
                "TAX_PLACEMENT_INTEGRITY_ERROR: excerpt %s — byte mismatch after write",
                excerpt_id,
            )
            path.unlink(missing_ok=True)
            return _reroute_to_unplaced(
                excerpt, tree, now_utc, "Post-write byte mismatch"
            )

    elif route == PlacementRoute.UNPLACED:
        write_unplaced_excerpt(
            excerpt, additions, config.science_id, base_path
        )

    elif route == PlacementRoute.PENDING_NO_TREE:
        write_pending_excerpt(
            excerpt, additions, config.science_id, base_path
        )

    return merged


def _reroute_to_unplaced(
    excerpt: dict,
    tree: LoadedTree,
    now_utc: str,
    reason: str,
) -> dict:
    """Create an unplaced result for an excerpt that failed validation."""
    additions = PlacementAdditions(
        lifecycle_stage=LifecycleStage.UNPLACED,
        placement_route=PlacementRoute.UNPLACED,
        unplaced_reason=reason,
        placed_utc=now_utc,
        taxonomy_version_at_placement=tree.tree_version,
    )
    return {**excerpt, **additions.model_dump(mode="json")}


def _write_batch_report(
    report: BatchReport,
    science_id: str,
    base_path: Path,
) -> Path:
    """Write the batch report JSON to the output directory."""
    report_path = (
        base_path / science_id / "batch_reports" / f"{report.batch_id}.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Batch report written to %s", report_path)
    return report_path
