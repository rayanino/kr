"""Passaging Engine — Passage Emission.

Implements SPEC §4.A.10 (emission process).

After all passage boundaries are determined, this module:
  1. Assigns passage_id and sequence_index sequentially.
  2. Assembles the complete PassageRecord for each passage.
  3. Sets predecessor_id / successor_id links.
  4. Writes passages.jsonl to library/sources/{source_id}/passages/.
  5. Updates source processing status from 'normalized' to 'passaged'.

Emission occurs AFTER self-validation passes. If validation fails on
fatal checks, no passage stream is written.
"""

from __future__ import annotations


def emit_passage_stream(passages: list, source_id: str, output_dir: str) -> None:
    """Write the passage stream to disk as passages.jsonl.

    Each passage is serialized as one JSON line using PassageRecord schema.
    Predecessor/successor links are set after all passages are assembled.
    """
    raise NotImplementedError
