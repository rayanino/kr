"""Data models for the excerpting evaluation layer.

No I/O. No imports from engines/ or shared/.
All structures are pure data containers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EvidenceBasis(str, Enum):
    OBSERVED = "observed"
    INFERRED_HIGH_CONFIDENCE = "inferred_high_confidence"
    INFERRED_MODERATE_CONFIDENCE = "inferred_moderate_confidence"


class StructuralStatus(str, Enum):
    STRUCTURAL_FAIL = "STRUCTURAL_FAIL"
    STRUCTURAL_CONCERN = "STRUCTURAL_CONCERN"
    STRUCTURALLY_CLEAN = "STRUCTURALLY_CLEAN"


class MetricTier(str, Enum):
    DECISION_GRADE = "decision_grade_structural"
    OPERATIONAL = "operational"
    REVIEW_RISK = "review_risk_triage"
    DESCRIPTIVE = "descriptive"


class SemanticPhase(str, Enum):
    CLASSIFICATION = "classification"
    GROUPING = "grouping"
    ENRICHMENT = "enrichment"
    VERIFICATION = "verification"
    ESCALATION = "escalation"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Canonical unit key
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CanonicalUnitKey:
    """Primary join key for the unit ledger.

    chunk_id is deliberately excluded — it is auxiliary metadata only.
    """
    source_id: str
    div_id: str
    chunk_index: int
    unit_index: int

    def to_tuple(self) -> tuple[str, str, int, int]:
        return (self.source_id, self.div_id, self.chunk_index, self.unit_index)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "div_id": self.div_id,
            "chunk_index": self.chunk_index,
            "unit_index": self.unit_index,
        }

    def __str__(self) -> str:
        return f"({self.source_id}, {self.div_id}, ci={self.chunk_index}, ui={self.unit_index})"


# ---------------------------------------------------------------------------
# Ledger entries
# ---------------------------------------------------------------------------

@dataclass
class UnitLedgerEntry:
    """One row in the canonical unit ledger."""
    key: CanonicalUnitKey
    chunk_id: str  # auxiliary, not the join key
    has_phase2b: bool = False
    phase2b_data: dict[str, Any] | None = None
    has_excerpt: bool = False
    excerpt_data: dict[str, Any] | None = None

    @property
    def stage_state(self) -> str:
        if self.has_excerpt:
            return "final_excerpt"
        if self.has_phase2b:
            return "grouped_only"
        return "absent"


@dataclass
class ChunkRecord:
    """Processing status for one Phase 1 chunk."""
    chunk_id: str
    source_id: str
    div_id: str
    chunk_index: int
    word_count: int = 0
    total_tokens: int = 0
    phase1_present: bool = True
    phase2a_present: bool = False
    phase2b_present: bool = False
    phase2b_unit_count: int = 0
    excerpt_count: int = 0


# ---------------------------------------------------------------------------
# LLM trace entry
# ---------------------------------------------------------------------------

@dataclass
class LLMTraceEntry:
    """One raw LLM request/response pair."""
    file_stem: str
    client_label: str
    inferred_phase: SemanticPhase
    label_matches_content: bool  # metadata only — NOT an anomaly trigger
    finish_reason: str | None = None
    model: str | None = None
    latency_seconds: float | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost: float | None = None
    has_error: bool = False
    error_type: str | None = None
    chunk_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_stem": self.file_stem,
            "client_label": self.client_label,
            "inferred_phase": self.inferred_phase.value,
            "label_matches_content": self.label_matches_content,
            "finish_reason": self.finish_reason,
            "model": self.model,
            "latency_seconds": self.latency_seconds,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost": self.cost,
            "has_error": self.has_error,
            "error_type": self.error_type,
            "chunk_id": self.chunk_id,
        }


# ---------------------------------------------------------------------------
# Anomaly
# ---------------------------------------------------------------------------

@dataclass
class Anomaly:
    """One detected structural or operational anomaly."""
    anomaly_id: str
    category: str
    severity: str  # "structural_fail" | "structural_concern" | "info"
    evidence_basis: EvidenceBasis
    summary: str
    observed_facts: list[str] = field(default_factory=list)
    inferred_interpretation: str | None = None
    affected_keys: list[CanonicalUnitKey] = field(default_factory=list)
    evidence_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "anomaly_id": self.anomaly_id,
            "category": self.category,
            "severity": self.severity,
            "evidence_basis": self.evidence_basis.value,
            "summary": self.summary,
            "observed_facts": self.observed_facts,
            "inferred_interpretation": self.inferred_interpretation,
            "affected_keys": [k.to_dict() for k in self.affected_keys],
            "evidence_paths": self.evidence_paths,
        }


# ---------------------------------------------------------------------------
# Tiered metric
# ---------------------------------------------------------------------------

@dataclass
class TieredMetric:
    """One metric with explicit authority tier and provenance."""
    name: str
    value: Any
    tier: MetricTier
    provenance: str  # "artifact_accounting" | "deterministic_structural" | ...

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "tier": self.tier.value,
            "provenance": self.provenance,
        }


# ---------------------------------------------------------------------------
# Review candidate
# ---------------------------------------------------------------------------

@dataclass
class ReviewCandidate:
    """One unit selected for inclusion in a review packet."""
    key: CanonicalUnitKey
    bucket_tags: list[str] = field(default_factory=list)
    stage_state: str = ""
    evidence_basis: EvidenceBasis = EvidenceBasis.OBSERVED
    primary_text: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    observed_facts: list[str] = field(default_factory=list)
    inferred_interpretation: str | None = None
    artifact_pointers: list[str] = field(default_factory=list)
    review_questions: list[str] = field(default_factory=list)
    anomaly_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_unit_key": self.key.to_dict(),
            "bucket_tags": self.bucket_tags,
            "stage_state": self.stage_state,
            "evidence_basis": self.evidence_basis.value,
            "primary_text": self.primary_text,
            "context": self.context,
            "observed_facts": self.observed_facts,
            "inferred_interpretation": self.inferred_interpretation,
            "artifact_pointers": self.artifact_pointers,
            "review_questions": self.review_questions,
            "anomaly_ids": self.anomaly_ids,
        }


# ---------------------------------------------------------------------------
# Book analysis result
# ---------------------------------------------------------------------------

@dataclass
class BookAnalysisResult:
    """Complete analysis output for one book run."""
    book_name: str
    source_id: str
    structural_status: StructuralStatus
    metrics: list[TieredMetric] = field(default_factory=list)
    anomalies: list[Anomaly] = field(default_factory=list)
    review_candidates: list[ReviewCandidate] = field(default_factory=list)
    traces: list[LLMTraceEntry] = field(default_factory=list)
    chunk_records: list[ChunkRecord] = field(default_factory=list)
    observability_limitations: list[str] = field(default_factory=list)
    # Raw counts for summary
    phase1_chunk_count: int = 0
    phase2b_unit_count: int = 0
    excerpt_count: int = 0
    error_count: int = 0
    total_time_seconds: float = 0.0
    total_cost: float = 0.0
