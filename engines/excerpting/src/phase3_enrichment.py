"""Phase 3: LLM-Driven Metadata Enrichment (SPEC §7.2).

Adds topic classification, school attribution, scholar resolution,
takhrij extraction, terminology variants, cross-references, and
context hints via one LLM enrichment call per chunk.

All LLM calls go through OpenRouter via Instructor.
"""

from __future__ import annotations

import logging

import instructor

from engines.excerpting.contracts import (
    AssembledChunk,
    EnrichmentResult,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    UnitEnrichment,
)

logger = logging.getLogger(__name__)


def enrich_chunk(
    chunk: AssembledChunk,
    excerpts: list[ExcerptRecord],
    client: instructor.Instructor,
    config: ExcerptingConfig,
) -> EnrichmentResult:
    """Send chunk + its teaching units to LLM for enrichment (§7.2).

    One LLM call per chunk (not per-unit). Inter-unit context improves
    quality — references like "as mentioned above" can be resolved.

    Uses system prompt from §7.2.2 and user message from §7.2.3.
    Returns EnrichmentResult with per-unit enrichments.
    """
    raise NotImplementedError


def apply_enrichment(
    excerpts: list[ExcerptRecord],
    enrichment: EnrichmentResult,
) -> list[ExcerptRecord]:
    """Merge LLM enrichment results into ExcerptRecords (§7.2).

    Updates: excerpt_topic, school, school_confidence, quoted_scholars,
    evidence_refs, takhrij_data, terminology_variants, cross_references,
    context_hint, self_containment (may upgrade PARTIAL → FULL or downgrade).
    """
    raise NotImplementedError


def run_phase3_enrichment(
    excerpts: list[ExcerptRecord],
    chunks: list[AssembledChunk],
    client: instructor.Instructor,
    config: ExcerptingConfig,
) -> list[ExcerptRecord]:
    """Execute LLM enrichment for all chunks (§7.2).

    Groups excerpts by chunk_id, calls enrich_chunk once per group.
    On LLM failure: deterministic fields survive. LLM fields stay None.
    Emits EX-M-002 on failure. Retries per §5.5.2.
    """
    raise NotImplementedError
