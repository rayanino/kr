"""Bridge: Convert Codex overnight results into KB findings.

Reads final_response.json from each task result, converts action_items
and findings strings into Finding records, persists to the KB JSONL files,
then runs cross-referencing and follow-up prompt generation.

Usage:
    python scripts/codex_kb_bridge.py              # ingest all un-ingested results
    python scripts/codex_kb_bridge.py --dry-run     # report without writing
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.autonomous_schemas import (
    DIGESTION_LOG_JSONL,
    DR_RESPONSES_JSONL,
    FINDINGS_JSONL,
    PROMPTS_DIR,
    DigestionRecord,
    DRResponse,
    DRTarget,
    Finding,
    FindingSeverity,
    ResearchCategory,
    append_jsonl,
    read_jsonl,
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
            section_heading="",
        ))

    return findings


# ═══════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════


def ingest_codex_results(run_id: str | None = None) -> dict[str, int]:
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
        except Exception as exc:
            logger.error("Cross-referencing failed (findings persisted without cross-refs): %s", exc)

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
        except Exception as exc:
            logger.error("Follow-up prompt generation failed: %s", exc)

    return {
        "tasks_processed": tasks_processed,
        "findings_created": findings_created,
        "skipped": skipped,
        "contradictions": contradiction_count,
        "followup_prompts": followup_count,
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
    print(f"  Tasks processed:  {stats['tasks_processed']}")
    print(f"  Findings created: {stats['findings_created']}")
    print(f"  Skipped:          {stats['skipped']}")
    print(f"  Contradictions:   {stats['contradictions']}")
    print(f"  Follow-up prompts: {stats['followup_prompts']}")


if __name__ == "__main__":
    main()
