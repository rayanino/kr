"""File output for the taxonomy engine.

Writes placed, staged, unplaced, and pending excerpts to their correct
output directories. All writers preserve upstream fields (D-023) and
use UTF-8 encoding with ensure_ascii=False for Arabic text.

See SPEC §3.1–3.4 for output paths and §3.6 for serialization rules.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from engines.taxonomy.contracts_core import PlacementAdditions

logger = logging.getLogger(__name__)


def _merge_and_write(
    excerpt: dict,
    additions: PlacementAdditions,
    output_path: Path,
) -> Path:
    """Merge excerpt with placement additions and write to disk.

    D-023: Output = {**original_excerpt, **placement_additions}.
    Collision policy: taxonomy fields overwrite upstream fields with same key.
    Serialization: ensure_ascii=False, indent=2, encoding=utf-8.
    """
    additions_dict = additions.model_dump(mode="json")
    output = {**excerpt, **additions_dict}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.debug("Wrote %s", output_path)
    return output_path


def write_placed_excerpt(
    excerpt: dict,
    additions: PlacementAdditions,
    science_id: str,
    base_path: Path,
) -> Path:
    """Write a live-placed excerpt to the content tree.

    Path: {base}/{science}/content/{leaf}/excerpts/{excerpt_id}.json

    Precondition: additions.confirmed_leaf is non-None (caller validates).
    """
    assert additions.confirmed_leaf is not None, "confirmed_leaf required for placed excerpt"
    excerpt_id = excerpt["excerpt_id"]
    output_path = (
        base_path / science_id / "content" / additions.confirmed_leaf / "excerpts" / f"{excerpt_id}.json"
    )
    return _merge_and_write(excerpt, additions, output_path)


def write_staged_excerpt(
    excerpt: dict,
    additions: PlacementAdditions,
    science_id: str,
    base_path: Path,
) -> Path:
    """Write a staged excerpt (low confidence or front matter).

    Path: {base}/{science}/staged/{leaf}/excerpts/{excerpt_id}.json

    Precondition: additions.confirmed_leaf is non-None (caller validates).
    """
    assert additions.confirmed_leaf is not None, "confirmed_leaf required for staged excerpt"
    excerpt_id = excerpt["excerpt_id"]
    output_path = (
        base_path / science_id / "staged" / additions.confirmed_leaf / "excerpts" / f"{excerpt_id}.json"
    )
    return _merge_and_write(excerpt, additions, output_path)


def write_unplaced_excerpt(
    excerpt: dict,
    additions: PlacementAdditions,
    science_id: str,
    base_path: Path,
) -> Path:
    """Write an unplaced excerpt.

    Path: {base}/{science}/unplaced/{excerpt_id}.json
    """
    excerpt_id = excerpt["excerpt_id"]
    output_path = base_path / science_id / "unplaced" / f"{excerpt_id}.json"
    return _merge_and_write(excerpt, additions, output_path)


def write_pending_excerpt(
    excerpt: dict,
    additions: PlacementAdditions,
    science_id: str,
    base_path: Path,
) -> Path:
    """Write a pending-no-tree excerpt.

    Path: {base}/pending_no_tree/{science}/{excerpt_id}.json
    """
    excerpt_id = excerpt["excerpt_id"]
    output_path = (
        base_path / "pending_no_tree" / science_id / f"{excerpt_id}.json"
    )
    return _merge_and_write(excerpt, additions, output_path)
