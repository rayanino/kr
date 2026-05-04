"""Phase 5 Session 4 — REQ-SRC-0042 build-time enrichment lane.

Defines the **lane contract** for build-time-only scholar registry enrichment
per REQ-SRC-0042 Phase 5 amendment + INV-SRC-0017 F-7 closure:

  - External sources (OpenITI metadata TSV, Wikidata SPARQL, LLM inference)
    are AUTHORIZED at registry-build time only.
  - Runtime external calls are FORBIDDEN per INV-SRC-0017; the enforcement
    surface is ``shared.scholar_authority.src.snapshot_lock.RuntimeExternalCallError``.
  - Every build-time-enriched scholar record carries a structured
    ``BuildTimeProvenance`` with source / phase=build_time / license /
    training_use_permitted (owner-decision per Critical Rule 13: all data is
    future training material).

This module ships the **contract + discipline**, not the enrichment dispatch:
the actual OpenITI/Wikidata/LLM clients are scope for a separate
build-time tooling layer. The lane defined here is the PROVENANCE GATE that
every enriched record passes through before being persisted into the
scholar registry snapshot that REQ-SRC-0049 then locks for runtime cases.

Architecture overview::

    [build-time only]
    OpenITI TSV ─┐
    Wikidata    ─┼── enrich_record() ──> EnrichedScholarRecord (with BuildTimeProvenance)
    LLM         ─┘                                   │
                                                     ▼
                              registry release snapshot (REQ-SRC-0049)
                                                     │
    [runtime — external FORBIDDEN]                   │
    scholar_match_cell ──── reads from snapshot ─────┘
                          (NO external calls; ever)

Critical Rule 13 alignment: ``training_use_permitted`` is recorded per
source per record so a future training pipeline can filter out evidence-
only material (e.g., OpenITI metadata under restrictive license) while
still using the record for scholar disambiguation at runtime.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from engines.source.contracts import ScholarAuthorityRecord
from shared.scholar_authority.src.snapshot_lock import (
    RuntimeExternalCallError,
)


# ---------------------------------------------------------------------------
# Source taxonomy — REQ-SRC-0042 amendment authorizes exactly these sources
# at build time. Adding a new source requires a SPEC amendment + license review.
# ---------------------------------------------------------------------------

EnrichmentSource = Literal["openiti", "wikidata", "llm_inference"]
"""Authorized build-time enrichment sources per REQ-SRC-0042 amendment.

  - ``openiti`` — local OpenITI metadata TSV (offline; evidence-only by
    license; ``training_use_permitted`` defaults to False — owner decision).
  - ``wikidata`` — Wikidata SPARQL (opportunistic enrichment for cross-
    language identifiers + corroborating dates).
  - ``llm_inference`` — LLM-generated biographical inference (sparse-record
    bootstrapping; provenance flag tracks the model + prompt hash so future
    re-attribution can replay the inference).
"""


EnrichmentPhase = Literal["build_time"]
"""The only authorized enrichment phase per REQ-SRC-0042 amendment.

Reserved as a Literal to prevent silent expansion of the enrichment-phase
surface; any future addition (e.g., runtime enrichment) requires a SPEC
amendment + INV-SRC-0017 F-7 closure review. The literal type makes the
forbidden runtime expansion fail at type-check time, not just at runtime.
"""


# ---------------------------------------------------------------------------
# BuildTimeProvenance — REQ-SRC-0042 amendment §"build-time enrichment lane"
# ---------------------------------------------------------------------------


class BuildTimeProvenance(BaseModel):
    """Structured provenance attached to every build-time-enriched record.

    Per REQ-SRC-0042 Phase 5 amendment line "All build-time external use
    produces records carrying data_provenance with source (string),
    enrichment_phase='build_time' (constant), license (string per source),
    and training_use_permitted (bool — owner-decision per Critical Rule 13)".

    Field semantics:

      - ``source`` — REQ-SRC-0042 ``EnrichmentSource`` value naming which
        external source produced this enrichment record. NOT the upstream
        scholar (which is the ``record_subject_canonical_id``).
      - ``enrichment_phase`` — pinned to ``"build_time"``. The Literal type
        prevents accidental runtime use; no helper accepts a runtime
        value here.
      - ``license`` — free-form license identifier per the source's
        terms (e.g., "openiti-cc-by-sa-4.0", "wikidata-cc0-1.0",
        "llm-inference-anthropic-tos"). The string is recorded so a
        downstream training pipeline can filter records under
        license-restrictive umbrellas.
      - ``training_use_permitted`` — Critical Rule 13 alignment: every
        enrichment record declares whether its content may be used as
        training material. The default is ``False`` (conservative) —
        owner explicitly opts in per source per content category. The
        bool is owner-driven, not source-driven; an owner may grant
        training use for OpenITI even when OpenITI's license technically
        permits redistribution.
      - ``record_subject_canonical_id`` — which scholar this enrichment
        record describes. Optional because OpenITI/Wikidata/LLM records
        sometimes pre-date the scholar registry's ID assignment (the
        provenance is still recorded for audit even before the canonical
        id is minted).
      - ``upstream_external_id`` — the source-side identifier (OpenITI
        URI / Wikidata QID / LLM model-id+prompt-hash). Optional because
        not all sources surface a stable id (LLM inference may not have
        one beyond the prompt hash).

    Frozen + ``extra='forbid'`` per Phase 5 contract discipline (Codex
    Stage-3 Defect 2 pattern: forbid silent field additions).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: EnrichmentSource
    enrichment_phase: EnrichmentPhase = "build_time"
    license: str = Field(min_length=1)
    training_use_permitted: bool
    record_subject_canonical_id: Optional[str] = None
    upstream_external_id: Optional[str] = None


# ---------------------------------------------------------------------------
# EnrichedScholarRecord — the lane's output shape
# ---------------------------------------------------------------------------


class EnrichedScholarRecord(BaseModel):
    """One scholar record + its build-time provenance.

    Pairs a ``ScholarAuthorityRecord`` (the scholar identity content) with
    a ``BuildTimeProvenance`` (the audit trail for how this record reached
    the registry snapshot). Per Critical Rule 6 (D-023 metadata flow)
    + Critical Rule 13 (training data preservation), the pair is recorded
    in full when the registry build pipeline persists enriched records.

    The lane wraps the record so that downstream consumers (registry build
    persister; future training pipeline filter) can route records by
    provenance without opening the underlying ``ScholarAuthorityRecord``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    record: ScholarAuthorityRecord
    provenance: BuildTimeProvenance


# ---------------------------------------------------------------------------
# Lane entry point — enrich_record
# ---------------------------------------------------------------------------


def enrich_record(
    record: ScholarAuthorityRecord,
    source: EnrichmentSource,
    license: str,
    training_use_permitted: bool,
    *,
    upstream_external_id: Optional[str] = None,
) -> EnrichedScholarRecord:
    """REQ-SRC-0042 — wrap a record with build-time provenance.

    The lane's only entry point. Build-time enrichment dispatchers (OpenITI
    TSV ingest / Wikidata SPARQL bridge / LLM inference) call this wrapper
    after producing or augmenting a ``ScholarAuthorityRecord``; the
    wrapper attaches the structured provenance before persistence.

    The function does NOT make any external calls itself — it only
    constructs the provenance Pydantic. Callers are responsible for the
    actual data fetch + record construction; the lane is the
    audit-discipline gate, not the network boundary.

    The ``record_subject_canonical_id`` defaults to ``record.canonical_id``
    when present (it is a 5-digit-padded string per ScholarAuthorityRecord;
    when missing the registry has not yet assigned an ID and the
    provenance still records the enrichment event for audit).
    """
    subject_id = record.canonical_id or None
    provenance = BuildTimeProvenance(
        source=source,
        enrichment_phase="build_time",
        license=license,
        training_use_permitted=training_use_permitted,
        record_subject_canonical_id=subject_id,
        upstream_external_id=upstream_external_id,
    )
    return EnrichedScholarRecord(record=record, provenance=provenance)


# ---------------------------------------------------------------------------
# Runtime-external guard — re-export for callers wiring the lane discipline
# ---------------------------------------------------------------------------


def reject_runtime_external_call(attempted_endpoint: str) -> None:
    """Raise ``RuntimeExternalCallError`` to fail-loud on runtime external attempts.

    Per INV-SRC-0017 F-7 + REQ-SRC-0042 amendment: external sources are
    forbidden in the runtime hot path. Any code path that detects an
    attempted runtime call (e.g., HTTP client wrapper, OpenITI loader)
    must raise ``RuntimeExternalCallError`` to abort the case rather than
    silently degrading to runtime fetch.

    This thin wrapper is provided so callers don't need to import
    ``snapshot_lock`` directly when the only reason is runtime-external
    enforcement; the actual error type is unchanged.
    """
    raise RuntimeExternalCallError(attempted_endpoint=attempted_endpoint)


__all__ = [
    "BuildTimeProvenance",
    "EnrichedScholarRecord",
    "EnrichmentPhase",
    "EnrichmentSource",
    "enrich_record",
    "reject_runtime_external_call",
]
