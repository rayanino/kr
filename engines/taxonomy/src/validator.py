"""Placement validation for the taxonomy engine.

Verifies that placements target real leaves and that written files
preserve Arabic text byte-identical (T-1 threat defense).
See SPEC §4.A.4 for the three-step validation protocol.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from engines.taxonomy.contracts_core import LoadedTree

logger = logging.getLogger(__name__)


def validate_placement(leaf_path: str, tree: LoadedTree) -> bool:
    """Verify that a leaf path resolves to a real leaf in the tree.

    Step 1 of SPEC §4.A.4: Leaf existence check.
    """
    return leaf_path in tree.leaf_by_path


def verify_written_file(file_path: Path, original_primary_text: str) -> bool:
    """Re-read a written file and verify primary_text is byte-identical.

    Step 3 of SPEC §4.A.4: Post-write fidelity check.
    This is the T-1 (Arabic text corruption) defense. Catches encoding
    mismatches (e.g., cp1252 on Windows) and serialization corruption.

    Returns:
        True if the file's primary_text matches the original exactly.
        False on any mismatch, parse error, or missing field.
    """
    try:
        raw = file_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError, OSError) as e:
        logger.error(
            "Post-write verification failed for %s: %s", file_path, e
        )
        return False

    written_text = data.get("primary_text")
    if written_text is None:
        logger.error(
            "Post-write verification: primary_text missing in %s", file_path
        )
        return False

    if written_text != original_primary_text:
        logger.error(
            "Post-write verification: primary_text mismatch in %s "
            "(original=%d chars, written=%d chars)",
            file_path,
            len(original_primary_text),
            len(written_text),
        )
        return False

    return True
