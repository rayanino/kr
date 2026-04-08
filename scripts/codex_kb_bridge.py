"""Bridge: Convert Codex overnight results into KB findings.

Reads final_response.json from each task result, converts action_items
and findings strings into Finding records, persists to the KB JSONL files,
then runs cross-referencing and follow-up prompt generation.

Also bridges three additional data flows:
- Creative task results → Idea Quarry (ideas.jsonl)
- SPEC [OPEN:] markers + KNOWN_LIMITATIONS.md → Research Gaps (research_gaps.jsonl)
- CONFIRMED HIGH/CRITICAL findings → Codex backlog (backlog.json)

Usage:
    python scripts/codex_kb_bridge.py              # ingest all un-ingested results
    python scripts/codex_kb_bridge.py --dry-run     # report without writing
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.autonomous_schemas import (
    DIGESTION_LOG_JSONL,
    DR_RESPONSES_JSONL,
    FINDINGS_JSONL,
    IDEAS_JSONL,
    PROJECT_DIR,
    PROMPTS_DIR,
    RESEARCH_GAPS_JSONL,
    DigestionRecord,
    DRResponse,
    DRTarget,
    Finding,
    FindingSeverity,
    GapSource,
    Idea,
    Priority,
    ResearchCategory,
    ResearchGap,
    VerificationStatus,
    append_jsonl,
    read_jsonl,
    rewrite_jsonl,
)

try:
    from scripts.overnight_codex_common import RESULTS_DIR, repo_rel
except ImportError:
    from overnight_codex_common import RESULTS_DIR, repo_rel

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# Mapping tables
# ═══════════════════════════════════════════════════════════════════

_PRIORITY_TO_SEVERITY: dict[str, FindingSeverity] = {
    "CRITICAL": FindingSeverity.CRITICAL,
    "HIGH": FindingSeverity.HIGH,
    "MEDIUM": FindingSeverity.MEDIUM,
    "LOW": FindingSeverity.LOW,
}

_CATEGORY_TO_RESEARCH: dict[str, ResearchCategory] = {
    "REVIEW": ResearchCategory.ENGINE_SPECIFIC,
    "TEST": ResearchCategory.ENGINE_SPECIFIC,
    "VALIDATION": ResearchCategory.ENGINE_SPECIFIC,
    "SPEC": ResearchCategory.ARCHITECTURE,
    "CODE_QUALITY": ResearchCategory.ARCHITECTURE,
    "DOC": ResearchCategory.CROSS_CUTTING,
    "CREATIVE": ResearchCategory.CREATIVE_VISIONARY,
}


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════


def _already_ingested() -> set[str]:
    """Return set of dr_ids already in digestion_log.jsonl."""
    records = read_jsonl(DIGESTION_LOG_JSONL, DigestionRecord)
    return {r.dr_id for r in records if isinstance(r, DigestionRecord)}


def _dedup_hash(task_id: str, item_id: str) -> str:
    """Stable hash for idempotent dedup."""
    return hashlib.sha256(f"{task_id}:{item_id}".encode("utf-8")).hexdigest()[:16]


def _extract_paths(payload: dict[str, Any]) -> list[str]:
    """Extract file paths from evidence and files_changed."""
    paths: list[str] = []
    for evidence in payload.get("evidence", []):
        if isinstance(evidence, dict):
            path = str(evidence.get("path", "")).replace("\\", "/").strip()
            if path and path not in paths:
                paths.append(path)
    for item in payload.get("files_changed", []):
        path = str(item).replace("\\", "/").strip()
        if path and path not in paths:
            paths.append(path)
    return paths


def _map_severity(priority: str) -> FindingSeverity:
    return _PRIORITY_TO_SEVERITY.get(priority.upper(), FindingSeverity.MEDIUM)


def _map_category(codex_category: str) -> ResearchCategory:
    return _CATEGORY_TO_RESEARCH.get(codex_category.upper(), ResearchCategory.CROSS_CUTTING)


# ═══════════════════════════════════════════════════════════════════
# Core conversion
# ═══════════════════════════════════════════════════════════════════


def convert_task_to_findings(
    task_id: str,
    payload: dict[str, Any],
) -> list[Finding]:
    """Convert a Codex final_response.json payload into Finding records."""
    findings: list[Finding] = []
    seen_hashes: set[str] = set()
    affected_files = _extract_paths(payload)
    task_category = task_id.split("-")[0] if "-" in task_id else "review"

    # Build evidence context string (preserves detail per rule 13: all data is training data)
    evidence_details = []
    for ev in payload.get("evidence", []):
        if isinstance(ev, dict):
            detail = str(ev.get("detail", "")).strip()
            if detail:
                evidence_details.append(detail)
    evidence_context = (" | Evidence: " + "; ".join(evidence_details)) if evidence_details else ""

    # 1. Convert action_items (structured, higher quality)
    for raw_item in payload.get("action_items", []):
        if not isinstance(raw_item, dict):
            continue
        item_id = str(raw_item.get("id", "")).strip()
        summary = str(raw_item.get("summary", "")).strip()
        if not summary:
            continue
        if not item_id:
            item_id = hashlib.sha256(summary.encode("utf-8")).hexdigest()[:8]

        raw_hash = _dedup_hash(task_id, item_id)
        if raw_hash in seen_hashes:
            continue
        seen_hashes.add(raw_hash)

        priority = str(raw_item.get("priority", "MEDIUM")).strip()
        category = str(raw_item.get("category", task_category)).strip()

        findings.append(Finding(
            finding_id=f"F-codex-{task_id}-{item_id}"[:80],
            source_type="codex_task",
            source_id=f"codex-{task_id}",
            severity=_map_severity(priority),
            category=_map_category(category),
            title=summary[:200],
            description=(summary + evidence_context)[:2000],
            affected_files=affected_files[:10],
            spec_sections=[],
            action_required=summary,
            confidence=0.7,
            raw_text_hash=raw_hash,
            prompt_id=None,
            section_heading="",
            verification_status=VerificationStatus.PRELIMINARY,
            verified_by=None,
            verified_at=None,
            verification_response="",
        ))

    # 2. Convert findings strings (unstructured, informational)
    for raw_finding in payload.get("findings", []):
        if not isinstance(raw_finding, str) or not raw_finding.strip():
            continue
        text = raw_finding.strip()
        str_id = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
        raw_hash = _dedup_hash(task_id, f"str-{str_id}")
        if raw_hash in seen_hashes:
            continue
        seen_hashes.add(raw_hash)

        findings.append(Finding(
            finding_id=f"F-codex-{task_id}-s{str_id}"[:80],
            source_type="codex_task",
            source_id=f"codex-{task_id}",
            severity=FindingSeverity.INFORMATIONAL,
            category=_map_category(task_category),
            title=text[:200],
            description=text,
            affected_files=affected_files[:10],
            spec_sections=[],
            action_required="",
            confidence=0.6,
            raw_text_hash=raw_hash,
            prompt_id=None,
            verification_status=VerificationStatus.PRELIMINARY,
            verified_by=None,
            verified_at=None,
            verification_response="",
            section_heading="",
        ))

    return findings


# ═══════════════════════════════════════════════════════════════════
# Cross-model verification (D-041)
# ═══════════════════════════════════════════════════════════════════

_VERIFY_SEVERITIES = {FindingSeverity.CRITICAL, FindingSeverity.HIGH}

_VERIFY_PROMPT = """\
You are reviewing a finding from an automated code analysis (Codex CLI) of the KR \
Islamic scholarly library pipeline. Assess whether this finding is accurate.

FINDING:
  Title: {title}
  Severity: {severity}
  Category: {category}
  Affected files: {files}
  Description: {description}

INSTRUCTIONS:
1. Read the affected files if they exist in this repository.
2. Assess whether the finding accurately describes a real issue.
3. Respond with EXACTLY one of these verdicts on the FIRST LINE:
   AGREE — the finding is accurate and actionable
   DISAGREE — the finding is inaccurate, outdated, or not a real issue
4. Then provide a brief explanation (2-3 sentences max).
"""

# Verifier priority: CC first (most important), Gemini second
# Each entry: (cli_name, label, extra_args)
_VERIFIERS: list[tuple[str, str, list[str]]] = [
    ("claude", "claude_code", ["--bare", "--model", "sonnet", "--max-budget-usd", "0.05"]),
    ("gemini", "gemini_cli", []),
]


def _find_verifier() -> tuple[str, str, list[str]] | None:
    """Find the best available CLI verifier. CC first, Gemini second."""
    for cli_name, label, extra_args in _VERIFIERS:
        path = shutil.which(cli_name)
        if path:
            return path, label, extra_args
    return None


def _run_cli_verify(
    finding: Finding, cli_path: str, cli_label: str,
    extra_args: list[str] | None = None,
) -> tuple[VerificationStatus, str]:
    """Dispatch a single finding to a CLI verifier (CC or Gemini).

    Returns (status, response_text).
    """
    prompt = _VERIFY_PROMPT.format(
        title=finding.title,
        severity=finding.severity.value,
        category=finding.category.value,
        files=", ".join(finding.affected_files[:5]) or "(none)",
        description=finding.description[:1500],
    )

    cmd = [cli_path, "-p", prompt] + (extra_args or [])
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180,
            cwd=str(Path(__file__).resolve().parent.parent),
        )
    except subprocess.TimeoutExpired:
        logger.warning("%s timed out verifying %s", cli_label, finding.finding_id)
        return VerificationStatus.PRELIMINARY, f"{cli_label} timeout"
    except OSError as exc:
        logger.error("%s failed for %s: %s", cli_label, finding.finding_id, exc)
        return VerificationStatus.PRELIMINARY, f"{cli_label} error: {exc}"

    # Check return code and stderr before parsing stdout
    if result.returncode != 0:
        stderr_msg = (result.stderr or "").strip()[:500]
        logger.error(
            "%s exited with code %d for %s. stderr: %s",
            cli_label, result.returncode, finding.finding_id, stderr_msg,
        )
        return VerificationStatus.PRELIMINARY, f"{cli_label} exit code {result.returncode}: {stderr_msg}"

    output = result.stdout.strip()
    if not output:
        stderr_hint = (result.stderr or "").strip()[:200]
        logger.warning(
            "%s returned empty stdout for %s (stderr=%s)",
            cli_label, finding.finding_id, stderr_hint,
        )
        return VerificationStatus.PRELIMINARY, f"{cli_label} returned empty output"

    # Parse verdict — exact match preferred, prefix match with warning
    first_line = output.split("\n")[0].strip().upper()
    if first_line == "AGREE":
        return VerificationStatus.CONFIRMED, output
    elif first_line == "DISAGREE":
        return VerificationStatus.DISPUTED, output
    elif first_line.startswith("AGREE"):
        logger.warning(
            "%s verdict for %s is not exact AGREE: '%s' — treating as CONFIRMED",
            cli_label, finding.finding_id, first_line[:80],
        )
        return VerificationStatus.CONFIRMED, output
    elif first_line.startswith("DISAGREE"):
        logger.warning(
            "%s verdict for %s is not exact DISAGREE: '%s' — treating as DISPUTED",
            cli_label, finding.finding_id, first_line[:80],
        )
        return VerificationStatus.DISPUTED, output
    else:
        logger.warning(
            "%s returned unparseable verdict for %s: '%s'",
            cli_label, finding.finding_id, first_line[:80],
        )
        return VerificationStatus.PRELIMINARY, output


def verify_findings(
    findings: list[Finding],
) -> dict[str, int]:
    """Verify HIGH/CRITICAL findings with CC (primary) or Gemini (fallback).

    Mutates findings in-place and rewrites findings.jsonl.
    Returns stats: verified, confirmed, disputed, skipped.

    INVARIANT: Single-writer discipline on FINDINGS_JSONL. This function
    reads, modifies in memory, then rewrites. Concurrent callers will cause
    data loss. The launcher and orchestrator serialize through ingest_codex_results().
    """
    to_verify = [
        f for f in findings
        if f.severity in _VERIFY_SEVERITIES
        and f.verification_status == VerificationStatus.PRELIMINARY
    ]

    if not to_verify:
        logger.info("No HIGH/CRITICAL PRELIMINARY findings to verify")
        return {"verified": 0, "confirmed": 0, "disputed": 0, "skipped": 0}

    verifier = _find_verifier()
    if not verifier:
        logger.warning(
            "No CLI verifier found (tried: %s) — skipping verification for %d findings",
            ", ".join(name for name, _, _ in _VERIFIERS), len(to_verify),
        )
        return {"verified": 0, "confirmed": 0, "disputed": 0, "skipped": len(to_verify)}

    cli_path, cli_label, extra_args = verifier
    logger.info("Using %s (%s) as verifier for %d findings", cli_label, cli_path, len(to_verify))

    confirmed = 0
    disputed = 0
    skipped = 0
    now = datetime.now(timezone.utc).isoformat()
    dirty = False  # tracks whether we have unsaved changes

    def _save_progress() -> None:
        """Persist verified findings to disk (incremental save)."""
        all_raw = read_jsonl(FINDINGS_JSONL, Finding)
        all_f = [f for f in all_raw if isinstance(f, Finding)]
        vmap = {f.finding_id: f for f in to_verify if f.verification_status != VerificationStatus.PRELIMINARY}
        for i, f in enumerate(all_f):
            if f.finding_id in vmap:
                all_f[i] = vmap[f.finding_id]
        rewrite_jsonl(FINDINGS_JSONL, all_f)

    try:
        for idx, finding in enumerate(to_verify):
            logger.info("Verifying [%d/%d] %s: %s", idx + 1, len(to_verify), finding.finding_id, finding.title[:60])
            status, response = _run_cli_verify(finding, cli_path, cli_label, extra_args)

            if status == VerificationStatus.PRELIMINARY:
                skipped += 1
                continue

            finding.verification_status = status
            finding.verified_by = cli_label
            finding.verified_at = now
            finding.verification_response = response[:2000]
            dirty = True

            if status == VerificationStatus.CONFIRMED:
                confirmed += 1
                logger.info("  → CONFIRMED by %s", cli_label)
            else:
                disputed += 1
                logger.info("  → DISPUTED by %s: %s", cli_label, response[:120])

            # Save every 5 findings to avoid losing work on interrupt
            if dirty and (idx + 1) % 5 == 0:
                logger.info("  Saving progress (%d verified so far)...", confirmed + disputed)
                _save_progress()
                dirty = False

    except KeyboardInterrupt:
        logger.warning("Verification interrupted — saving %d partial results", confirmed + disputed)

    # Final save of any remaining unsaved results
    if dirty:
        _save_progress()

    total = confirmed + disputed
    logger.info(
        "Verification complete (%s): %d verified (%d confirmed, %d disputed, %d skipped)",
        cli_label, total, confirmed, disputed, skipped,
    )
    return {"verified": total, "confirmed": confirmed, "disputed": disputed, "skipped": skipped}


# ═══════════════════════════════════════════════════════════════════
# Bridge 1: Creative tasks → Idea Quarry
# ═══════════════════════════════════════════════════════════════════


def _load_existing_idea_ids() -> set[str]:
    """Return set of idea_ids already in ideas.jsonl."""
    records = read_jsonl(IDEAS_JSONL, Idea)
    return {r.idea_id for r in records if isinstance(r, Idea)}


def _extract_ideas_from_payload(
    task_id: str,
    payload: dict[str, Any],
    existing_ids: set[str],
) -> tuple[int, int]:
    """Extract Idea records from a creative task payload.

    Returns (created, skipped).
    """
    created = 0
    skipped = 0

    for raw_item in payload.get("action_items", []):
        if not isinstance(raw_item, dict):
            continue
        summary = str(raw_item.get("summary", "")).strip()
        if not summary:
            continue
        item_id = str(raw_item.get("id", "")).strip()
        if not item_id:
            item_id = hashlib.sha256(summary.encode("utf-8")).hexdigest()[:8]

        idea_id = f"IDEA-{task_id}-{item_id}"[:60]
        if idea_id in existing_ids:
            skipped += 1
            continue

        idea = Idea(
            idea_id=idea_id,
            title=summary[:200],
            description=summary,
            source="codex_creative",
            implementation_sketch=str(raw_item.get("detail", ""))[:2000],
            estimated_effort=str(raw_item.get("effort", "")).strip(),
        )
        append_jsonl(IDEAS_JSONL, idea)
        existing_ids.add(idea_id)
        created += 1

    for raw_finding in payload.get("findings", []):
        if not isinstance(raw_finding, str) or not raw_finding.strip():
            continue
        text = raw_finding.strip()
        str_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
        idea_id = f"IDEA-{task_id}-s{str_hash}"[:60]
        if idea_id in existing_ids:
            skipped += 1
            continue

        idea = Idea(
            idea_id=idea_id,
            title=text[:200],
            description=text,
            source="codex_creative",
        )
        append_jsonl(IDEAS_JSONL, idea)
        existing_ids.add(idea_id)
        created += 1

    return created, skipped


def bridge_creative_to_ideas() -> dict[str, int]:
    """Scan creative-* result dirs for creative.json and create Idea records.

    Falls back to final_response.json if creative.json is absent.
    Returns stats: ideas_created, ideas_skipped.
    """
    existing_ids = _load_existing_idea_ids()
    created = 0
    skipped = 0

    creative_dirs = sorted(RESULTS_DIR.glob("creative-*"))
    if not creative_dirs:
        logger.info("No creative-* result dirs found in %s", RESULTS_DIR)
        return {"ideas_created": 0, "ideas_skipped": 0}

    for task_dir in creative_dirs:
        task_id = task_dir.name
        creative_file = task_dir / "creative.json"
        if not creative_file.exists():
            creative_file = task_dir / "final_response.json"
        if not creative_file.exists():
            logger.warning("No creative.json or final_response.json in %s", task_dir)
            skipped += 1
            continue

        try:
            payload = json.loads(creative_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skipping %s: %s", creative_file, exc)
            skipped += 1
            continue

        if not isinstance(payload, dict):
            logger.warning("Skipping %s: not a dict", task_id)
            skipped += 1
            continue

        task_created, task_skipped = _extract_ideas_from_payload(
            task_id, payload, existing_ids,
        )
        created += task_created
        skipped += task_skipped

    logger.info("Creative → Ideas: %d created, %d skipped", created, skipped)
    return {"ideas_created": created, "ideas_skipped": skipped}


# ═══════════════════════════════════════════════════════════════════
# Bridge 2: Gap scanner → Research Gaps
# ═══════════════════════════════════════════════════════════════════

# Pattern for [OPEN: description] markers in SPEC files
_OPEN_MARKER_RE = re.compile(r"\[OPEN:\s*(.+?)\]")

# Pattern for L-NNN limitation entries in KNOWN_LIMITATIONS.md
_LIMITATION_RE = re.compile(r"^##\s+(L-[0-9]+):\s*(.+)$", re.MULTILINE)

# Engines directory for scanning
_ENGINES_DIR = PROJECT_DIR / "engines"


def _load_existing_gap_ids() -> set[str]:
    """Return set of gap_ids already in research_gaps.jsonl."""
    records = read_jsonl(RESEARCH_GAPS_JSONL, ResearchGap)
    return {r.gap_id for r in records if isinstance(r, ResearchGap)}


def _scan_spec_open_markers(existing_ids: set[str]) -> list[ResearchGap]:
    """Grep SPEC.md files for [OPEN: ...] markers."""
    gaps: list[ResearchGap] = []
    for spec_file in sorted(_ENGINES_DIR.glob("*/SPEC.md")):
        engine_name = spec_file.parent.name
        try:
            content = spec_file.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Cannot read %s: %s", spec_file, exc)
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            match = _OPEN_MARKER_RE.search(line)
            if not match:
                continue
            description = match.group(1).strip()
            desc_hash = hashlib.sha256(description.encode("utf-8")).hexdigest()[:8]
            gap_id = f"GAP-OPEN-{engine_name}-{desc_hash}"
            if gap_id in existing_ids:
                continue

            gaps.append(ResearchGap(
                gap_id=gap_id,
                source=GapSource.SPEC_OPEN,
                source_file=str(spec_file.relative_to(PROJECT_DIR)).replace("\\", "/"),
                source_line=line_num,
                description=f"[{engine_name}] {description}",
                priority=Priority.MEDIUM,
            ))
            existing_ids.add(gap_id)

    return gaps


def _scan_known_limitations(existing_ids: set[str]) -> list[ResearchGap]:
    """Parse KNOWN_LIMITATIONS.md files for L-NNN entries."""
    gaps: list[ResearchGap] = []

    for lim_file in sorted(PROJECT_DIR.glob("engines/*/KNOWN_LIMITATIONS.md")):
        engine_name = lim_file.parent.name
        try:
            content = lim_file.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Cannot read %s: %s", lim_file, exc)
            continue

        for match in _LIMITATION_RE.finditer(content):
            lim_id = match.group(1)  # e.g. "L-001"
            lim_title = match.group(2).strip()
            gap_id = f"GAP-LIM-{engine_name}-{lim_id}"
            if gap_id in existing_ids:
                continue

            gaps.append(ResearchGap(
                gap_id=gap_id,
                source=GapSource.KNOWN_LIMITATION,
                source_file=str(lim_file.relative_to(PROJECT_DIR)).replace("\\", "/"),
                source_line=None,
                description=f"[{engine_name}] {lim_id}: {lim_title}",
                priority=Priority.LOW,
            ))
            existing_ids.add(gap_id)

    # Also scan scripts/excerpting_eval/ for KNOWN_LIMITATIONS.md
    for lim_file in sorted(PROJECT_DIR.glob("scripts/*/KNOWN_LIMITATIONS.md")):
        module_name = lim_file.parent.name
        try:
            content = lim_file.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Cannot read %s: %s", lim_file, exc)
            continue

        for match in _LIMITATION_RE.finditer(content):
            lim_id = match.group(1)
            lim_title = match.group(2).strip()
            gap_id = f"GAP-LIM-{module_name}-{lim_id}"
            if gap_id in existing_ids:
                continue

            gaps.append(ResearchGap(
                gap_id=gap_id,
                source=GapSource.KNOWN_LIMITATION,
                source_file=str(lim_file.relative_to(PROJECT_DIR)).replace("\\", "/"),
                source_line=None,
                description=f"[{module_name}] {lim_id}: {lim_title}",
                priority=Priority.LOW,
            ))
            existing_ids.add(gap_id)

    return gaps


def bridge_gaps_to_research_gaps() -> dict[str, int]:
    """Scan SPEC [OPEN:] markers and KNOWN_LIMITATIONS.md for research gaps.

    Returns stats: gaps_created (open + limitations), gaps_skipped.
    """
    existing_ids = _load_existing_gap_ids()
    initial_count = len(existing_ids)

    open_gaps = _scan_spec_open_markers(existing_ids)
    lim_gaps = _scan_known_limitations(existing_ids)

    all_new = open_gaps + lim_gaps
    for gap in all_new:
        append_jsonl(RESEARCH_GAPS_JSONL, gap)

    created = len(all_new)
    logger.info(
        "Gap scanner → Research Gaps: %d created (%d from [OPEN:], %d from KNOWN_LIMITATIONS)",
        created, len(open_gaps), len(lim_gaps),
    )
    return {
        "gaps_created": created,
        "gaps_from_open": len(open_gaps),
        "gaps_from_limitations": len(lim_gaps),
        "gaps_skipped": initial_count,
    }


# ═══════════════════════════════════════════════════════════════════
# Bridge 3: Findings → Backlog promotion
# ═══════════════════════════════════════════════════════════════════

_PROMOTABLE_SEVERITIES = {FindingSeverity.CRITICAL, FindingSeverity.HIGH}


def _import_backlog_helpers() -> tuple[Any, ...]:
    """Lazy-import backlog helpers to avoid circular deps."""
    try:
        from scripts.overnight_codex_backlog import (
            dedupe_key, infer_frontier_tag, infer_subsystem,
            infer_allowed_write_prefixes, load_backlog, save_backlog,
        )
        from scripts.overnight_codex_common import utc_now_iso
    except ImportError:
        from overnight_codex_backlog import (  # type: ignore[no-redef]
            dedupe_key, infer_frontier_tag, infer_subsystem,
            infer_allowed_write_prefixes, load_backlog, save_backlog,
        )
        from overnight_codex_common import utc_now_iso  # type: ignore[no-redef]
    return dedupe_key, infer_frontier_tag, infer_subsystem, infer_allowed_write_prefixes, load_backlog, save_backlog, utc_now_iso


def _build_backlog_item(
    finding: Finding,
    item_key: str,
    subsystem: str,
    frontier_tag: str,
    write_prefixes: list[str],
    run_id: str,
    utc_now_iso: Any,
) -> dict[str, Any]:
    """Build a backlog item dict from a confirmed finding."""
    return {
        "item_id": item_key,
        "dedupe_key": item_key,
        "summary": finding.action_required.strip()[:500],
        "proposed_action": finding.action_required.strip()[:500],
        "category": finding.category.value.upper(),
        "priority": finding.severity.value.upper(),
        "effort": "M",
        "status": "proposed",
        "frontier_tag": frontier_tag,
        "subsystem": subsystem,
        "allowed_write_prefixes": write_prefixes,
        "gate_mode": "all",
        "evidence_paths": finding.affected_files[:12],
        "source_task_ids": [finding.source_id],
        "source_kind": "kb_finding_promotion",
        "source_finding_id": finding.finding_id,
        "legacy_input": False,
        "latest_result_path": "",
        "latest_source_signature": f"{finding.finding_id}:{finding.verified_at or ''}",
        "created_at": utc_now_iso(),
        "created_by_run": run_id,
        "last_seen": utc_now_iso(),
        "last_touched_run": run_id,
        "status_updated_at": utc_now_iso(),
        "status_updated_by_run": run_id,
        "occurrences": 1,
    }


def bridge_findings_to_backlog() -> dict[str, int]:
    """Promote CONFIRMED HIGH/CRITICAL findings to the Codex backlog."""
    (dedupe_key, infer_frontier_tag, infer_subsystem,
     infer_allowed_write_prefixes, load_backlog, save_backlog,
     utc_now_iso) = _import_backlog_helpers()

    if not FINDINGS_JSONL.exists():
        logger.info("No findings.jsonl — skipping backlog promotion")
        return {"promoted": 0, "already_in_backlog": 0, "skipped": 0}

    all_findings_raw = read_jsonl(FINDINGS_JSONL, Finding)
    candidates = [
        f for f in all_findings_raw
        if isinstance(f, Finding)
        and f.verification_status == VerificationStatus.CONFIRMED
        and f.severity in _PROMOTABLE_SEVERITIES
        and f.action_required.strip()
    ]

    if not candidates:
        logger.info("No CONFIRMED HIGH/CRITICAL findings with action_required to promote")
        return {"promoted": 0, "already_in_backlog": 0, "skipped": 0}

    backlog = load_backlog()
    promoted = 0
    already = 0
    run_id = f"bridge-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"

    for finding in candidates:
        paths = finding.affected_files[:10]
        subsystem = infer_subsystem(finding.finding_id, paths)
        summary = finding.action_required.strip()[:500]
        category = finding.category.value.upper()
        item_key = dedupe_key(subsystem=subsystem, category=category, summary=summary)

        if item_key in backlog["items"]:
            already += 1
            continue

        backlog["items"][item_key] = _build_backlog_item(
            finding, item_key, subsystem,
            infer_frontier_tag(subsystem),
            infer_allowed_write_prefixes(subsystem),
            run_id, utc_now_iso,
        )
        promoted += 1

    if promoted > 0:
        backlog["meta"]["last_synced_at"] = utc_now_iso()
        backlog["meta"]["last_sync_run"] = run_id
        save_backlog(backlog)

    logger.info(
        "Findings → Backlog: %d promoted, %d already present",
        promoted, already,
    )
    return {
        "promoted": promoted,
        "already_in_backlog": already,
        "skipped": len(candidates) - promoted - already,
    }


# ═══════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════


def ingest_codex_results(run_id: str | None = None) -> dict[str, Any]:
    """Scan results/ and ingest all un-ingested Codex results into the KB.

    Returns stats: tasks_processed, findings_created, skipped,
    contradictions, followup_prompts.
    """
    ingested = _already_ingested()
    tasks_processed = 0
    findings_created = 0
    skipped = 0
    all_new_findings: list[Finding] = []

    result_files = sorted(RESULTS_DIR.glob("*/final_response.json"))
    if not result_files:
        logger.info("No Codex results found in %s", RESULTS_DIR)
        return {"tasks_processed": 0, "findings_created": 0, "skipped": 0,
                "contradictions": 0, "followup_prompts": 0}

    # Load existing finding IDs for dedup (guards against partial prior writes)
    existing_finding_ids: set[str] = set()
    if FINDINGS_JSONL.exists():
        for f in read_jsonl(FINDINGS_JSONL, Finding):
            if isinstance(f, Finding):
                existing_finding_ids.add(f.finding_id)

    for result_file in result_files:
        task_id = result_file.parent.name
        dr_id = f"codex-{task_id}"

        if dr_id in ingested:
            skipped += 1
            continue

        try:
            payload = json.loads(result_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skipping %s: %s", result_file, exc)
            skipped += 1
            continue

        if not isinstance(payload, dict):
            logger.warning("Skipping %s: payload is %s, expected dict", task_id, type(payload).__name__)
            skipped += 1
            continue

        # Convert to findings
        findings = convert_task_to_findings(task_id, payload)
        has_input = payload.get("action_items") or payload.get("findings")
        if not findings and has_input:
            logger.warning("Task %s had input data but produced 0 findings", task_id)

        # Persist findings (skip duplicates from crashed prior runs)
        new_in_task: list[Finding] = []
        for f in findings:
            if f.finding_id not in existing_finding_ids:
                append_jsonl(FINDINGS_JSONL, f)
                existing_finding_ids.add(f.finding_id)
                new_in_task.append(f)
        all_new_findings.extend(new_in_task)

        # Create DRResponse record (DigestionRecord written LAST as commit marker)
        dr_response = DRResponse(
            response_id=dr_id,
            prompt_id=task_id,
            source=DRTarget.CODEX,
            response_file=str(repo_rel(result_file)),
            finding_count=len(new_in_task),
            finding_ids=[f.finding_id for f in new_in_task],
            summary=str(payload.get("summary", ""))[:500],
        )
        append_jsonl(DR_RESPONSES_JSONL, dr_response)

        # Create DigestionRecord
        action_items = payload.get("action_items", [])
        findings_strs = payload.get("findings", [])
        record = DigestionRecord(
            dr_id=dr_id,
            response_file=str(repo_rel(result_file)),
            provider=DRTarget.CODEX,
            section_count=len(action_items) + len(findings_strs),
            finding_count=len(findings),
            status="pass",
            digestion_version="2.0",
        )
        append_jsonl(DIGESTION_LOG_JSONL, record)

        tasks_processed += 1
        findings_created += len(new_in_task)
        logger.info("Ingested %s: %d findings", task_id, len(new_in_task))

    # Verify HIGH/CRITICAL findings with Gemini CLI (D-041 cross-model)
    # Covers both newly ingested AND existing PRELIMINARY findings
    verify_stats = {"verified": 0, "confirmed": 0, "disputed": 0, "skipped": 0}
    try:
        all_existing = read_jsonl(FINDINGS_JSONL, Finding)
        verify_candidates = [f for f in all_existing if isinstance(f, Finding)]
        if verify_candidates:
            verify_stats = verify_findings(verify_candidates)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        logger.exception("Gemini verification failed (findings remain PRELIMINARY): %s", exc)

    # Cross-reference ALL findings (existing + new).
    # Isolated try/except: cross-ref failure must not block stats or follow-ups.
    contradiction_count = 0
    if all_new_findings:
        try:
            try:
                from scripts.cross_reference_findings import (
                    cross_reference,
                    persist_cross_references,
                )
            except ImportError:
                from cross_reference_findings import (
                    cross_reference,
                    persist_cross_references,
                )

            all_findings_raw = read_jsonl(FINDINGS_JSONL, Finding)
            all_findings = [f for f in all_findings_raw if isinstance(f, Finding)]
            related_map, contradictions = cross_reference(all_findings)
            persist_cross_references(all_findings, related_map, contradictions)
            contradiction_count = len(contradictions)
            logger.info("Cross-referenced %d findings, %d contradictions", len(all_findings), contradiction_count)
        except (OSError, ValueError) as exc:
            logger.error("Cross-referencing failed (I/O or data error): %s", exc)
        except Exception as exc:
            logger.exception("Cross-referencing failed (likely code bug): %s", exc)

    # Generate follow-up prompts from new contradictions/gaps.
    # Isolated: prompt generation failure must not block stats.
    followup_count = 0
    if all_new_findings:
        try:
            try:
                from scripts.generate_followup_prompts import generate_followups
            except ImportError:
                from generate_followup_prompts import generate_followups

            new_prompts = generate_followups(batch="codex-auto")
            if new_prompts:
                batch_file = PROMPTS_DIR / "codex-auto.jsonl"
                PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
                for p in new_prompts:
                    append_jsonl(batch_file, p)
                followup_count = len(new_prompts)
                logger.info("Generated %d follow-up prompts", followup_count)
        except (OSError, ValueError) as exc:
            logger.error("Follow-up prompt generation failed (I/O or data error): %s", exc)
        except Exception as exc:
            logger.exception("Follow-up prompt generation failed (likely code bug): %s", exc)

    # ── Bridges: each isolated, errors tracked for caller visibility ──
    bridge_errors: list[str] = []

    creative_stats = {"ideas_created": 0, "ideas_skipped": 0}
    try:
        creative_stats = bridge_creative_to_ideas()
    except (OSError, ValueError) as exc:
        logger.error("Creative → Ideas bridge failed (I/O or data error): %s", exc)
        bridge_errors.append(f"creative: {exc}")
    except Exception as exc:
        logger.exception("Creative → Ideas bridge failed (likely code bug): %s", exc)
        bridge_errors.append(f"creative: {exc}")

    gap_stats = {"gaps_created": 0, "gaps_from_open": 0, "gaps_from_limitations": 0, "gaps_skipped": 0}
    try:
        gap_stats = bridge_gaps_to_research_gaps()
    except (OSError, ValueError) as exc:
        logger.error("Gap scanner → Research Gaps bridge failed: %s", exc)
        bridge_errors.append(f"gaps: {exc}")
    except Exception as exc:
        logger.exception("Gap scanner → Research Gaps bridge failed: %s", exc)
        bridge_errors.append(f"gaps: {exc}")

    backlog_stats = {"promoted": 0, "already_in_backlog": 0, "skipped": 0}
    try:
        backlog_stats = bridge_findings_to_backlog()
    except (OSError, ValueError) as exc:
        logger.error("Findings → Backlog promotion failed: %s", exc)
        bridge_errors.append(f"backlog: {exc}")
    except Exception as exc:
        logger.exception("Findings → Backlog promotion failed: %s", exc)
        bridge_errors.append(f"backlog: {exc}")

    # Warn if PRELIMINARY findings are blocking follow-ups (chicken-and-egg)
    if FINDINGS_JSONL.exists():
        all_for_check = read_jsonl(FINDINGS_JSONL, Finding)
        preliminary_needing_action = [
            f for f in all_for_check
            if isinstance(f, Finding)
            and f.verification_status == VerificationStatus.PRELIMINARY
            and f.severity in _VERIFY_SEVERITIES
        ]
        if preliminary_needing_action:
            logger.warning(
                "⚠ %d HIGH/CRITICAL findings stuck at PRELIMINARY — "
                "follow-up prompts blocked until Gemini CLI verifies them. "
                "Run 'python scripts/codex_kb_bridge.py' when Gemini is available.",
                len(preliminary_needing_action),
            )

    # Compute KB totals for summary display (avoids 0-stat problem when
    # orchestrator hook already ingested everything before the launcher's
    # bridge call)
    total_findings = 0
    total_confirmed = 0
    total_disputed = 0
    if FINDINGS_JSONL.exists():
        all_f = read_jsonl(FINDINGS_JSONL, Finding)
        total_findings = len(all_f)
        for f in all_f:
            if isinstance(f, Finding):
                if f.verification_status == VerificationStatus.CONFIRMED:
                    total_confirmed += 1
                elif f.verification_status == VerificationStatus.DISPUTED:
                    total_disputed += 1

    total_tasks = 0
    if DIGESTION_LOG_JSONL.exists():
        total_tasks = len(read_jsonl(DIGESTION_LOG_JSONL, DigestionRecord))

    return {
        "tasks_processed": tasks_processed,
        "findings_created": findings_created,
        "skipped": skipped,
        "contradictions": contradiction_count,
        "followup_prompts": followup_count,
        "verified": verify_stats.get("verified", 0),
        "confirmed": verify_stats.get("confirmed", 0),
        "disputed": verify_stats.get("disputed", 0),
        # Bridge stats
        "ideas_created": creative_stats.get("ideas_created", 0),
        "gaps_created": gap_stats.get("gaps_created", 0),
        "backlog_promoted": backlog_stats.get("promoted", 0),
        "bridge_errors": bridge_errors,
        # KB totals (cumulative across all runs)
        "kb_total_tasks": total_tasks,
        "kb_total_findings": total_findings,
        "kb_total_confirmed": total_confirmed,
        "kb_total_disputed": total_disputed,
    }


def main() -> None:
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Bridge Codex results into KB")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    parser.add_argument("--run-id", default=None, help="Optional run ID for tracing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.dry_run:
        # Just report what would be ingested
        ingested = _already_ingested()
        result_files = sorted(RESULTS_DIR.glob("*/final_response.json"))
        pending = [f for f in result_files if f"codex-{f.parent.name}" not in ingested]
        print(f"Results found: {len(result_files)}")
        print(f"Already ingested: {len(result_files) - len(pending)}")
        print(f"Pending ingestion: {len(pending)}")
        for f in pending:
            print(f"  - {f.parent.name}")
        return

    stats = ingest_codex_results(run_id=args.run_id)
    print(f"\nCodex → KB Bridge Results:")
    print(f"  Tasks processed:   {stats['tasks_processed']}")
    print(f"  Findings created:  {stats['findings_created']}")
    print(f"  Skipped:           {stats['skipped']}")
    print(f"  Verified:          {stats['verified']} ({stats['confirmed']} confirmed, {stats['disputed']} disputed)")
    print(f"  Contradictions:    {stats['contradictions']}")
    print(f"  Follow-up prompts: {stats['followup_prompts']}")
    print(f"  Ideas created:     {stats['ideas_created']}")
    print(f"  Gaps created:      {stats['gaps_created']}")
    print(f"  Backlog promoted:  {stats['backlog_promoted']}")
    errors = stats.get("bridge_errors", [])
    if errors:
        print(f"\n  BRIDGE ERRORS ({len(errors)}):")
        for err in errors:
            print(f"    - {err}")


if __name__ == "__main__":
    main()
