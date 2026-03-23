"""Phase 3: Consensus Verification and Human Gates (SPEC §7.3).

Cross-provider verification for high-epistemic-impact decisions
(attribution, school). Triggers human gates for unresolvable uncertainty.

Uses a different-provider model (openai/gpt-4.1 by default) for
structural independence from the enrichment model (Opus 4.6).
"""

from __future__ import annotations

import logging
from typing import Optional

import instructor

from engines.excerpting.contracts import (
    AssembledChunk,
    ConsensusRecord,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    VerificationResult,
)

logger = logging.getLogger(__name__)


def verify_chunk(
    chunk: AssembledChunk,
    excerpts: list[ExcerptRecord],
    client: instructor.Instructor,
    config: ExcerptingConfig,
) -> VerificationResult:
    """Call verification model for attribution + school checks (§7.3.2).

    Uses VERIFY_MODEL (different provider family from ENRICH_MODEL).
    Returns VerificationResult with per-unit attribution and school verdicts.
    """
    raise NotImplementedError


def resolve_consensus(
    enrichment_result: ExcerptRecord,
    verification_result: dict,
    escalation_client: Optional[instructor.Instructor],
    config: ExcerptingConfig,
) -> tuple[ExcerptRecord, Optional[ConsensusRecord]]:
    """Resolve disagreements between enrichment and verification (§7.3.3).

    2-of-3 majority wins. If all 3 disagree (enrichment, verification,
    escalation), trigger EX-G-001 human gate.

    Returns updated ExcerptRecord and optional ConsensusRecord metadata.
    """
    raise NotImplementedError


def check_gate_triggers(
    excerpt: ExcerptRecord,
    manifest_metadata: dict,
    config: ExcerptingConfig,
) -> list[str]:
    """Check human gate trigger conditions (§7.3.4).

    EX-G-001: All 3 models disagree on attribution.
    EX-G-002: DEPENDENT self-containment after consensus.
    EX-G-003: School attribution conflicts with source metadata.

    Returns list of triggered gate codes (empty if none triggered).
    """
    raise NotImplementedError


def run_consensus(
    excerpts: list[ExcerptRecord],
    chunks: list[AssembledChunk],
    enrich_client: instructor.Instructor,
    verify_client: instructor.Instructor,
    escalation_client: Optional[instructor.Instructor],
    config: ExcerptingConfig,
) -> tuple[list[ExcerptRecord], list[dict]]:
    """Execute consensus verification for all excerpts (§7.3).

    Returns:
        excerpts: Updated ExcerptRecords with consensus metadata.
        gate_entries: Human gate entries to write (EX-G-001/002/003).
    """
    raise NotImplementedError
