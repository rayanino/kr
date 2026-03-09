"""Source Engine Consensus Integration — SPEC §6

Engine-specific agreement functions and comparison logic for the shared
consensus module. These functions implement the §6.1 (author identification),
§6.2 (work matching), and §6.3 (attribution status) rules.

The shared consensus module dispatches models and handles retries.
This module provides the domain-specific agreement semantics.
"""

from __future__ import annotations

from typing import Callable, Optional

from engines.source.contracts import AttributionStatus, HumanGateTrigger
from engines.source.src.inference_models import InferenceOutput
from shared.consensus.src.consensus import ModelResponse
from shared.scholar_authority.src.name_matching import normalized_name_similarity


def make_author_agreement_fn(
    scholar_lookup_fn: Callable[[str], Optional[dict]],
) -> Callable[[InferenceOutput, InferenceOutput], bool]:
    """Create an author agreement function closed over a scholar lookup.

    The returned function implements SPEC §6.1:
    - Case A: Both match same existing record (same canonical_id) → True
    - Case B: Both say "new" → name_sim >= 0.90 AND death dates agree (±10 years or both None) → True
    - All other cases → False

    Args:
        scholar_lookup_fn: Function that looks up a scholar by name,
            returns a dict with 'canonical_id' key or None.
    """

    def author_agreement(response_a: InferenceOutput, response_b: InferenceOutput) -> bool:
        """Compare two InferenceOutput author identifications for agreement.

        Args:
            response_a: InferenceOutput from first model.
            response_b: InferenceOutput from second model.

        Returns:
            True when both models agree on the author identity, False otherwise.
        """
        name_a = response_a.author_identification.canonical_name_ar
        name_b = response_b.author_identification.canonical_name_ar

        # Look up both names in scholar registry
        record_a = scholar_lookup_fn(name_a)
        record_b = scholar_lookup_fn(name_b)

        # Case A: Both match existing records
        if record_a is not None and record_b is not None:
            id_a = record_a.get("canonical_id", record_a.get("canonical_name"))
            id_b = record_b.get("canonical_id", record_b.get("canonical_name"))
            return id_a == id_b

        # One matches, one doesn't → disagreement
        if (record_a is None) != (record_b is None):
            return False

        # Case B: Both say "new" (neither found in registry)
        name_sim = normalized_name_similarity(name_a, name_b)
        if name_sim < 0.90:
            return False

        # Death date check: ±10 years or both None
        death_a = response_a.author_identification.death_date_hijri
        death_b = response_b.author_identification.death_date_hijri
        if death_a is not None and death_b is not None:
            if abs(death_a - death_b) > 10:
                return False
        # If one is None and the other isn't, still okay (one may not know)

        return True

    return author_agreement


def check_work_agreement(
    response_a: InferenceOutput, response_b: InferenceOutput
) -> tuple[bool, Optional[str]]:
    """Compare work matching between two model responses (SPEC §6.2).

    Compares genre_chain's base_work_title and base_work_author.

    Args:
        response_a: InferenceOutput from first model.
        response_b: InferenceOutput from second model.

    Returns:
        Tuple of (agreed, human_gate_trigger_or_none):
        - agreed=True when both have no genre_chain, or both have matching chains.
        - agreed=False with trigger when both respond but differ.
    """
    chain_a = response_a.genre_chain
    chain_b = response_b.genre_chain

    # Both None → agree (both say this is an independent work)
    if chain_a is None and chain_b is None:
        return True, None

    # One None, one not → disagree
    if (chain_a is None) != (chain_b is None):
        return False, HumanGateTrigger.WORK_MATCH_UNCERTAIN.value

    # Both have genre chains — compare title and author
    title_sim = normalized_name_similarity(
        chain_a.base_work_title, chain_b.base_work_title
    )
    author_sim = normalized_name_similarity(
        chain_a.base_work_author, chain_b.base_work_author
    )

    if title_sim >= 0.85 and author_sim >= 0.85:
        return True, None

    return False, HumanGateTrigger.WORK_MATCH_UNCERTAIN.value


def compare_attribution_status(
    status_a: str, status_b: str
) -> tuple[str, bool]:
    """Directed comparison of attribution_status values (SPEC §6.3).

    This is NOT symmetric in outcome logic — conservative value always wins —
    but the result IS symmetric: argument order does not affect output.

    Rules:
    - Both agree → accept the agreed value, no gate.
    - One says disputed/unknown, other says definitive/traditional
      → use the MORE CONSERVATIVE value (disputed/unknown wins)
      → trigger human gate.
    - One says traditional, other says definitive
      → use traditional (more conservative), NO human gate.
      This is a degree-of-certainty disagreement, not alarming.

    Args:
        status_a: First model's attribution_status string.
        status_b: Second model's attribution_status string.

    Returns:
        Tuple of (accepted_status, needs_human_gate).
    """
    CONSERVATIVE_ORDER = ["unknown", "disputed", "traditional", "definitive"]

    if status_a == status_b:
        return status_a, False

    idx_a = CONSERVATIVE_ORDER.index(status_a)
    idx_b = CONSERVATIVE_ORDER.index(status_b)
    conservative = status_a if idx_a < idx_b else status_b

    # Check if one is conservative (unknown/disputed) and the other is permissive
    # (definitive/traditional) — this is a real safety disagreement
    conservative_set = {"unknown", "disputed"}
    permissive_set = {"definitive", "traditional"}
    if (status_a in conservative_set and status_b in permissive_set) or (
        status_b in conservative_set and status_a in permissive_set
    ):
        return conservative, True

    # traditional vs definitive: use conservative, but no gate needed
    return conservative, False


def select_canonical_result(
    model_responses: list[ModelResponse],
) -> InferenceOutput:
    """Select the canonical InferenceOutput from model responses (SPEC §6).

    Higher author_identification_confidence wins. Tie → Model B (index 1, Opus 4.6).

    Args:
        model_responses: List of successful ModelResponse objects.

    Returns:
        The InferenceOutput from the winning model.
    """
    successful = [r for r in model_responses if r.parse_success and r.parsed is not None]
    if len(successful) == 1:
        return successful[0].parsed

    # Compare confidence
    resp_a, resp_b = successful[0], successful[1]
    conf_a = resp_a.parsed.author_identification_confidence
    conf_b = resp_b.parsed.author_identification_confidence

    if conf_a > conf_b:
        return resp_a.parsed
    return resp_b.parsed  # Tie → Model B (Opus 4.6)
