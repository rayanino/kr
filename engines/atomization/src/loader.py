"""Atomization Engine — Input Loading and Validation.

Implements SPEC §2: Input Contract.

Reads the passage stream from library/sources/{source_id}/passages/passages.jsonl.
Each record conforms to the passaging engine's output schema (PassageRecord).

Validation checks (§2):
  1. passage_text is non-empty
  2. passage_id matches expected format (psg_{source_id}_{zero_padded_sequence})
  3. text_layers is non-empty and covers full span of passage_text
  4. structural_format is a recognized value
  5. passage_text is Unicode NFC (safety net — normalizes in-memory if not)

On validation failure: passage skipped with ATOM_INVALID_INPUT, processing
continues with remaining passages.
"""

from __future__ import annotations


def load_passage_stream(source_id: str):
    """Load and validate the passage stream for a source.

    Yields validated passage records. Skips invalid passages with
    ATOM_INVALID_INPUT logged per passage.

    NFC normalization (§2 step 5): if passage_text is not NFC, normalize
    the in-memory copy and recompute text_layers offsets. Never modifies
    the on-disk file. Sets nfc_normalization_applied review flag.
    """
    raise NotImplementedError
