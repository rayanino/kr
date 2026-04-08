"""Data models for the KR autonomous system knowledge base.

All persistent data structures for DR prompts, responses, findings, ideas,
and insights. JSONL-first: each model serializes to one JSON line.

Reference: docs/autonomous-system/DESIGN.md §3.4 (Persistence Model)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, model_validator

logger = logging.getLogger(__name__)

# Centralized KB paths — all modules import from here (Architect finding: was duplicated in 6 files)
PROJECT_DIR = Path(__file__).resolve().parent.parent
KB_DIR = PROJECT_DIR / "overnight_codex" / "autonomous" / "knowledge_base"
FINDINGS_JSONL = KB_DIR / "findings.jsonl"
DR_RESPONSES_JSONL = KB_DIR / "dr_responses.jsonl"
CONTRADICTIONS_JSONL = KB_DIR / "contradictions.jsonl"
DIGESTION_LOG_JSONL = KB_DIR / "digestion_log.jsonl"
PROMPTS_DIR = KB_DIR / "dr_prompts"

# ═══════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════


class DRTarget(str, Enum):
    """Which Deep Research provider or autonomous source to target."""

    CHATGPT = "chatgpt_dr"
    CLAUDE = "claude_dr"
    GEMINI = "gemini_dr"
    CODEX = "codex"


class DRPromptStatus(str, Enum):
    """Lifecycle of a DR prompt in the relay queue."""

    PENDING = "pending"
    RELAYED = "relayed"
    RECEIVED = "received"
    PROCESSED = "processed"
    SUPERSEDED = "superseded"


class ResearchCategory(str, Enum):
    """DR33-derived research categories."""

    ENGINE_SPECIFIC = "engine_specific"
    CROSS_CUTTING = "cross_cutting"
    SCHOLARLY_DOMAIN = "scholarly_domain"
    ARCHITECTURE = "architecture"
    CREATIVE_VISIONARY = "creative_visionary"


class GapSource(str, Enum):
    """Where a research gap was detected."""

    SPEC_OPEN = "spec_open"
    SPEC_CALIBRATED = "spec_calibrated"  # Resolved [CALIBRATED] markers
    SPEC_NO_EXAMPLE = "spec_no_example"
    KNOWN_LIMITATION = "known_limitation"
    TEST_COVERAGE = "test_coverage"
    COWORKER_DISAGREEMENT = "coworker_disagreement"
    OWNER_FEEDBACK = "owner_feedback"
    CROSS_ENGINE = "cross_engine"
    CONSENSUS_FAILURE = "consensus_failure"
    ARABIC_EDGE_CASE = "arabic_edge_case"
    TAXONOMY_GAP = "taxonomy_gap"
    DR_FOLLOWUP = "dr_followup"


class Priority(str, Enum):
    """Priority levels for prompts and gaps."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingSeverity(str, Enum):
    """How impactful a finding is (extends Priority with INFORMATIONAL)."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class IdeaStatus(str, Enum):
    """Lifecycle of a creative idea."""

    GENERATED = "generated"
    DR_RESEARCHED = "dr_researched"
    COWORKER_VALIDATED = "coworker_validated"
    SCORED = "scored"
    QUEUED_FOR_SUMMER = "queued_for_summer"
    REJECTED = "rejected"


class TopicState(str, Enum):
    """DR33-derived research topic state machine."""

    IDENTIFIED = "identified"
    ACTIVE = "active"
    DEEP = "deep"
    BLOCKED = "blocked"
    SATURATED = "saturated"


# ═══════════════════════════════════════════════════════════════════
# Core Models
# ═══════════════════════════════════════════════════════════════════


class DRPrompt(BaseModel):
    """A DR prompt ready for the relay queue."""

    prompt_id: str = Field(..., pattern=r"^[A-Za-z0-9_\-]+$", description="Unique ID, e.g. RQ-B2-001")
    target: DRTarget
    category: ResearchCategory
    priority: Priority
    topic: str = Field(..., description="Short topic description")
    prompt_text: str = Field(..., min_length=1, description="Full prompt text for copy-paste")
    unblocks: str = Field(..., description="What this DR answer unblocks")
    file_bundle: Optional[str] = Field(
        None, description="Files to upload for Gemini DR"
    )
    estimated_minutes: int = Field(20, description="Estimated DR session time")
    dedup_hash: str = Field("", description="SHA-256 of target+prompt for dedup")
    status: DRPromptStatus = DRPromptStatus.PENDING
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    relayed_at: Optional[str] = None
    response_file: Optional[str] = None
    batch: str = Field("", description="Which batch this prompt belongs to")

    @model_validator(mode="after")
    def compute_dedup_hash(self) -> DRPrompt:
        """Auto-compute dedup hash from target + prompt text."""
        if not self.dedup_hash:
            key = f"{self.target.value}:{self.prompt_text}"
            self.dedup_hash = hashlib.sha256(
                key.encode("utf-8")
            ).hexdigest()[:16]
        return self


class DRResponse(BaseModel):
    """A processed DR response with extracted findings."""

    response_id: str = Field(..., description="Unique ID, e.g. DR40")
    prompt_id: str = Field(..., description="Which prompt this responds to")
    source: DRTarget
    response_file: str = Field(..., description="Path to the raw response file")
    processed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finding_count: int = 0
    finding_ids: list[str] = Field(default_factory=list)
    followup_prompt_ids: list[str] = Field(default_factory=list)
    summary: str = Field("", description="1-2 sentence summary of findings")


class Finding(BaseModel):
    """An actionable finding extracted from a DR response or system analysis."""

    finding_id: str = Field(..., description="Unique ID, e.g. F-001")
    source_type: str = Field(
        ..., description="dr_response / gap_scanner / coworker / system"
    )
    source_id: str = Field(..., description="DR response ID or scan run ID")
    severity: FindingSeverity
    category: ResearchCategory
    title: str
    description: str
    affected_files: list[str] = Field(default_factory=list)
    spec_sections: list[str] = Field(default_factory=list)
    action_required: str = Field("", description="What should be done")
    resolved: bool = False
    resolved_by: Optional[str] = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    # KB digestion fields (all optional — backward compatible with existing records)
    gap_ids: list[str] = Field(
        default_factory=list, description="ResearchGap IDs this finding resolves"
    )
    prompt_id: Optional[str] = Field(
        None, description="DR prompt that produced this finding"
    )
    related_finding_ids: list[str] = Field(
        default_factory=list, description="Findings in same contradiction/agreement cluster"
    )
    confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="Parser confidence in extraction quality"
    )
    raw_text_hash: str = Field(
        "", description="SHA-256 prefix of source text span for dedup"
    )
    section_heading: str = Field(
        "", description="Heading in the DR response this was extracted from"
    )


class ResearchGap(BaseModel):
    """An identified research gap that needs a DR prompt."""

    gap_id: str = Field(..., description="Unique ID, e.g. GAP-001")
    source: GapSource
    source_file: str = Field(..., description="File where gap was detected")
    source_line: Optional[int] = None
    description: str
    recommended_target: Optional[DRTarget] = None
    priority: Priority = Priority.MEDIUM
    prompt_generated: bool = False
    prompt_id: Optional[str] = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Idea(BaseModel):
    """A creative idea in the Idea Quarry pipeline."""

    idea_id: str = Field(..., description="Unique ID, e.g. IDEA-001")
    title: str
    description: str
    source: str = Field(
        ..., description="owner / system / dr_response / coworker"
    )
    status: IdeaStatus = IdeaStatus.GENERATED
    dr_prompt_ids: list[str] = Field(default_factory=list)
    coworker_reviews: list[str] = Field(default_factory=list)
    score: Optional[float] = None
    implementation_sketch: str = ""
    dependencies: list[str] = Field(default_factory=list)
    estimated_effort: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ResearchTopic(BaseModel):
    """A research topic tracked by the state machine (DR33 framework)."""

    topic_id: str = Field(..., description="e.g. RT-01")
    name: str
    category: ResearchCategory
    state: TopicState = TopicState.IDENTIFIED
    dr_count: int = 0
    hard_dependencies: list[str] = Field(default_factory=list)
    tsi: float = Field(0.0, description="Topic Saturation Index 0.0-1.0")
    last_dr_date: Optional[str] = None


class Contradiction(BaseModel):
    """A conflict between findings from different DR responses."""

    contradiction_id: str = Field(..., description="e.g. CONTRA-001")
    finding_id_a: str
    finding_id_b: str
    dr_id_a: str
    dr_id_b: str
    topic: str = Field(..., description="What the contradiction is about")
    description: str
    resolution_status: str = Field(
        "unresolved",
        description="unresolved / a_preferred / b_preferred / synthesized / deferred",
    )
    resolution_notes: str = Field("")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DigestionRecord(BaseModel):
    """Tracks the processing state of a DR response file."""

    dr_id: str
    response_file: str
    provider: DRTarget
    line_count: int = 0
    section_count: int = 0
    finding_count: int = 0
    contradiction_count: int = 0
    followup_prompt_count: int = 0
    digested_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    digestion_version: str = Field("2.0", description="Parser version for reprocessing")
    status: str = Field("complete")


# ═══════════════════════════════════════════════════════════════════
# JSONL I/O helpers
# ═══════════════════════════════════════════════════════════════════


def append_jsonl(path: Path, record: BaseModel) -> None:
    """Append a single Pydantic model as one JSONL line.

    Single-writer discipline: this function is NOT concurrency-safe.
    All writes to a given JSONL file must come from a single process.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path: Path, model_class: type[BaseModel]) -> list[BaseModel]:
    """Read all records from a JSONL file.

    Raises on parse errors to fail loud per project rules.
    Skips blank lines only.
    """
    if not path.exists():
        return []
    records: list[BaseModel] = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(model_class.model_validate_json(line))
            except (ValidationError, json.JSONDecodeError) as e:
                raise ValueError(
                    f"JSONL parse error at {path}:{line_num}: {e}"
                ) from e
    return records


def load_dr_index(path: Path) -> dict[str, DRPrompt]:
    """Load the DR prompt index as a dict keyed by prompt_id.

    Last-write-wins semantics: if a prompt_id appears multiple times
    (from append-only updates), the latest entry is kept.
    """
    raw = read_jsonl(path, DRPrompt)
    prompts: list[DRPrompt] = [p for p in raw if isinstance(p, DRPrompt)]
    seen: dict[str, DRPrompt] = {}
    for p in prompts:
        if p.prompt_id in seen:
            logger.debug("Duplicate prompt_id %s — using later entry", p.prompt_id)
        seen[p.prompt_id] = p
    return seen
