"""Atomization Engine — Cross-Atom Terminological Concordance.

Implements SPEC §4.B.7: Extracting term-concept mappings from definition atoms.

For each atom with scholarly_function: definition, extracts:
  - defined_term: the Arabic term being defined
  - definition_genus: broader category (genus in genus-differentia)
  - definition_differentia: distinguishing features
  - alternate_terms: synonyms mentioned in the text
  - science_scope: science this term belongs to (from source metadata)

Produces a per-source term_index.json for downstream cross-source
terminology mapping.
"""

from __future__ import annotations


def extract_concordance_entry(atom_text: str, source_metadata: dict,
                              config: "AtomizationConfig") -> "ConcordanceEntry | None":
    """Extract concordance entry from a definition atom.

    Returns ConcordanceEntry or None on extraction failure.
    """
    raise NotImplementedError


def build_term_index(source_id: str,
                     definition_atoms: list[dict]) -> "TermIndex":
    """Build the per-source terminological index from all definition atoms."""
    raise NotImplementedError
