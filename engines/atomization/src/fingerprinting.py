"""Atomization Engine — Atom-Level Semantic Fingerprinting.

Implements SPEC §4.B.5: Three-tier fingerprinting for cross-source
duplicate and near-duplicate detection.

Tier 1 (text hash): SHA-256 of normalized atom text. Normalization:
  diacritics stripped, alef/hamza/taa marbuta normalized, particles
  stripped, words sorted. Uses CAMeL Tools for Arabic normalization.
  Deterministic — same text always produces same hash.

Tier 2 (key terms): 2-5 key Arabic terms extracted by the LLM.
  Represents the atom's conceptual core. Normalized (diacritics stripped).

Tier 3 (embedding): Semantic embedding vector from Arabic-STS-Matryoshka
  or Swan-Large. Only when enable_semantic_fingerprinting is true.
  Requires GPU-resident model.

Produces a per-source fingerprint_manifest.json for downstream
cross-source deduplication.
"""

from __future__ import annotations


def compute_text_hash(atom_text: str) -> str | None:
    """Tier 1: Compute SHA-256 of normalized atom text.

    Returns 64-char hex string, or None on normalization failure.
    """
    raise NotImplementedError


def extract_key_terms(atom_text: str, scholarly_function: str,
                      config: "AtomizationConfig") -> list[str]:
    """Tier 2: Extract key Arabic terms from atom text via LLM.

    Returns list of 2-5 normalized terms.
    """
    raise NotImplementedError


def compute_embedding(atom_text: str,
                      config: "AtomizationConfig") -> list[float] | None:
    """Tier 3: Compute semantic embedding vector.

    Returns float array of configured dimensions, or None on failure.
    Requires enable_semantic_fingerprinting = true.
    """
    raise NotImplementedError


def build_fingerprint_manifest(source_id: str,
                               atoms: list[dict]) -> "FingerprintManifest":
    """Build the per-source fingerprint manifest for downstream use."""
    raise NotImplementedError
