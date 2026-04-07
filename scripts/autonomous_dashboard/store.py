"""Data access layer for the autonomous dashboard.

Reads JSONL/JSON files from overnight_codex/autonomous/knowledge_base/
using Pydantic models from scripts/autonomous_schemas.py.

Hardened after 3-reviewer audit (code, architecture, silent-failure-hunter).
"""
from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from pydantic import ValidationError

from scripts.autonomous_schemas import (
    Contradiction,
    DigestionRecord,
    DRPrompt,
    DRPromptStatus,
    DRResponse,
    Finding,
    FindingSeverity,
    Idea,
    Priority,
    ResearchGap,
    append_jsonl,
)

logger = logging.getLogger(__name__)

# Resolve paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
KB = PROJECT_ROOT / "overnight_codex" / "autonomous" / "knowledge_base"

# Startup validation — fail loud if knowledge base is missing
if not KB.exists():
    logger.warning("Knowledge base not found at %s — dashboard will show empty data", KB)


def _safe_read_jsonl(path: Path, model_class: type) -> tuple[list, list[str]]:
    """Read JSONL with graceful degradation on corrupt lines.

    Returns (valid_records, error_messages) instead of raising on
    individual parse errors. A completely missing file returns ([], []).
    """
    if not path.exists():
        return [], []
    errors: list[str] = []
    records: list = []
    with open(path, encoding="utf-8-sig") as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(model_class.model_validate_json(stripped))
            except (ValidationError, json.JSONDecodeError, ValueError) as e:
                msg = f"{path.name}:{line_num}: {e}"
                logger.warning("JSONL parse error: %s", msg)
                errors.append(msg)
    return records, errors


# ═══════════════════════════════════════════════════════════════════
# Relay Queue
# ═══════════════════════════════════════════════════════════════════

_PRIORITY_ORDER = {
    Priority.CRITICAL: 0,
    Priority.HIGH: 1,
    Priority.MEDIUM: 2,
    Priority.LOW: 3,
}


def load_all_prompts() -> tuple[list[DRPrompt], list[str]]:
    """Load all DR prompts from all batch JSONL files, sorted by priority.

    Returns (prompts, errors) for graceful degradation.
    """
    prompts_dir = KB / "dr_prompts"
    if not prompts_dir.exists():
        logger.warning("DR prompts directory not found: %s", prompts_dir)
        return [], []

    all_prompts: list[DRPrompt] = []
    all_errors: list[str] = []
    for jsonl_file in sorted(prompts_dir.glob("*.jsonl")):
        records, errors = _safe_read_jsonl(jsonl_file, DRPrompt)
        all_prompts.extend(records)
        all_errors.extend(errors)

    # Deduplicate by prompt_id (last-write-wins)
    seen: dict[str, DRPrompt] = {}
    for p in all_prompts:
        seen[p.prompt_id] = p

    # Sort: pending first, then by priority
    result = list(seen.values())
    result.sort(key=lambda p: (
        0 if p.status == DRPromptStatus.PENDING else 1,
        _PRIORITY_ORDER.get(p.priority, 99),
    ))
    return result, all_errors


def get_pending_prompts() -> list[DRPrompt]:
    """Return only pending (not-yet-relayed) prompts."""
    prompts, _ = load_all_prompts()
    return [p for p in prompts if p.status == DRPromptStatus.PENDING]


def get_relay_stats() -> dict[str, int]:
    """Quick stats for the relay queue, counting all status values."""
    all_p, _ = load_all_prompts()
    stats: dict[str, int] = {"total": len(all_p)}
    for status in DRPromptStatus:
        stats[status.value] = sum(1 for p in all_p if p.status == status)
    return stats


# ═══════════════════════════════════════════════════════════════════
# Findings
# ═══════════════════════════════════════════════════════════════════

_SEVERITY_ORDER = {
    FindingSeverity.CRITICAL: 0,
    FindingSeverity.HIGH: 1,
    FindingSeverity.MEDIUM: 2,
    FindingSeverity.LOW: 3,
    FindingSeverity.INFORMATIONAL: 4,
}


def load_findings() -> tuple[list[Finding], list[str]]:
    """Load all findings sorted by severity. Returns (findings, errors)."""
    path = KB / "findings.jsonl"
    records, errors = _safe_read_jsonl(path, Finding)
    records.sort(key=lambda f: _SEVERITY_ORDER.get(f.severity, 99))
    return records, errors


def get_findings_by_severity() -> tuple[dict[str, list[Finding]], list[str]]:
    """Group findings by severity level. Returns (grouped, errors)."""
    findings, errors = load_findings()
    grouped: dict[str, list[Finding]] = {}
    for f in findings:
        key = f.severity.value
        grouped.setdefault(key, []).append(f)
    return grouped, errors


def get_findings_stats() -> dict[str, int]:
    """Quick stats for findings."""
    findings, _ = load_findings()
    stats: dict[str, int] = {"total": len(findings), "unresolved": 0}
    for sev in FindingSeverity:
        stats[sev.value] = sum(1 for f in findings if f.severity == sev)
    stats["unresolved"] = sum(1 for f in findings if not f.resolved)
    return stats


# ═══════════════════════════════════════════════════════════════════
# Research Gaps (Status page)
# ═══════════════════════════════════════════════════════════════════

def load_research_gaps() -> list[ResearchGap]:
    """Load all research gaps."""
    path = KB / "research_gaps.jsonl"
    records, _ = _safe_read_jsonl(path, ResearchGap)
    return records


def get_gaps_stats() -> dict[str, int]:
    """Quick stats for research gaps."""
    gaps = load_research_gaps()
    return {
        "total": len(gaps),
        "open": sum(1 for g in gaps if not g.prompt_generated),
        "prompted": sum(1 for g in gaps if g.prompt_generated),
        "critical": sum(1 for g in gaps if g.priority == Priority.CRITICAL),
        "high": sum(1 for g in gaps if g.priority == Priority.HIGH),
    }


# ═══════════════════════════════════════════════════════════════════
# Ideas
# ═══════════════════════════════════════════════════════════════════

IDEAS_FILE = KB / "ideas.jsonl"


def load_ideas() -> list[Idea]:
    """Load all ideas."""
    records, _ = _safe_read_jsonl(IDEAS_FILE, Idea)
    return records


def submit_idea(title: str, description: str) -> Idea:
    """Submit a new owner idea and persist it.

    Uses UUID for idea_id to avoid race conditions (reviewer finding #4).
    """
    short_id = uuid.uuid4().hex[:8]
    idea = Idea(
        idea_id=f"IDEA-{short_id}",
        title=title,
        description=description,
        source="owner",
    )
    append_jsonl(IDEAS_FILE, idea)
    return idea


# ═══════════════════════════════════════════════════════════════════
# DR Responses
# ═══════════════════════════════════════════════════════════════════

def get_dr_response_stats() -> dict[str, int]:
    """Stats on processed DR responses."""
    path = KB / "dr_responses.jsonl"
    records, _ = _safe_read_jsonl(path, DRResponse)
    return {
        "total": len(records),
        "total_findings": sum(r.finding_count for r in records),
    }


# ═════════════════════════════════════════════════════════════��═════
# Contradictions
# ═══════════════════════════════════════════════════════════════════

def load_contradictions() -> tuple[list[Contradiction], list[str]]:
    """Load all contradictions. Returns (contradictions, errors)."""
    path = KB / "contradictions.jsonl"
    return _safe_read_jsonl(path, Contradiction)


def get_contradiction_stats() -> dict[str, int]:
    """Quick stats for contradictions."""
    contras, _ = load_contradictions()
    return {
        "total": len(contras),
        "unresolved": sum(1 for c in contras if c.resolution_status == "unresolved"),
        "resolved": sum(1 for c in contras if c.resolution_status != "unresolved"),
    }


# ═════════════════════════════════════════════════════��═════════════
# Digestion Log
# ═══════════════════════════════════════════════════════════════════

def load_digestion_records() -> tuple[list[DigestionRecord], list[str]]:
    """Load all digestion records. Returns (records, errors)."""
    path = KB / "digestion_log.jsonl"
    return _safe_read_jsonl(path, DigestionRecord)


def get_digestion_stats() -> dict[str, int]:
    """Quick stats for digestion log."""
    records, _ = load_digestion_records()
    return {
        "total": len(records),
        "pass": sum(1 for r in records if r.status == "pass"),
        "warn": sum(1 for r in records if r.status == "warn"),
        "fail": sum(1 for r in records if r.status == "fail"),
    }
