"""Passaging Engine — Input Loading and Validation.

Implements SPEC §2: Input Contract.

Reads the normalized package (manifest.json + content.jsonl) from
library/sources/{source_id}/normalized/ and validates the six input checks:

  1. Manifest exists and is valid JSON → PSG_MANIFEST_INVALID (fatal)
  2. schema_version recognized → PSG_SCHEMA_UNSUPPORTED (fatal)
  3. Content stream file exists → PSG_CONTENT_MISSING (fatal)
  4. total_content_units matches actual count → PSG_CONTENT_COUNT_MISMATCH (warning)
  5. Content units ordered by unit_index, no gaps → PSG_CONTENT_UNORDERED (fatal),
     PSG_CONTENT_GAP (warning)
  6. Division tree ranges consistent → PSG_DIVISION_INCONSISTENT (warning)

Returns: validated NormalizedManifest + list[ContentUnit], or raises on fatal error.
"""

from __future__ import annotations


def load_and_validate(source_id: str):
    """Load normalized package and run all six input validation checks.

    Returns (manifest, content_units) on success.
    Raises PassagingFatalError on any fatal validation failure.
    Logs warnings for non-fatal issues.
    """
    raise NotImplementedError
