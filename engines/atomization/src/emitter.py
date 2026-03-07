"""Atomization Engine — Output Emission.

Writes the atom stream to library/sources/{source_id}/atoms/atoms.jsonl.
Updates the source's processing status from 'passaged' to 'atomized'.

Also produces secondary artifacts:
  - distribution_report.json (§4.B.3)
  - fingerprint_manifest.json (§4.B.5, when enabled)
  - term_index.json (§4.B.7, when enabled)
  - atomization_log.jsonl (always — error/warning log)

Guarantees: atom_id sequence numbers are globally monotonic within a source.
Atoms are ordered by reading order within each passage.
"""

from __future__ import annotations


def emit_atom_stream(source_id: str, atoms_by_passage: dict[str, list[dict]],
                     config: "AtomizationConfig") -> str:
    """Write the atom stream JSONL and secondary artifacts.

    Returns the path to the written atoms.jsonl file.
    Updates source processing status to 'atomized'.
    """
    raise NotImplementedError


def emit_distribution_report(source_id: str,
                             atoms_by_passage: dict[str, list[dict]]) -> str:
    """Produce the per-source type distribution report (§4.B.3).

    Returns path to distribution_report.json.
    """
    raise NotImplementedError
