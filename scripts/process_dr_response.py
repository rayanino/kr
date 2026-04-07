"""Process a DR response file into structured findings.

Takes a markdown file containing a Deep Research response, parses it,
extracts actionable findings, and updates the knowledge base.

Reference: docs/autonomous-system/DESIGN.md §4.5 (Response Processing)

Usage:
    python scripts/process_dr_response.py <response_file> --prompt-id RQ-B2-001 --source gemini_dr --dr-id DR40
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.autonomous_schemas import (
    DRResponse,
    DRTarget,
    Finding,
    FindingSeverity,
    ResearchCategory,
    append_jsonl,
)

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent
KB_DIR = PROJECT_DIR / "overnight_codex" / "autonomous" / "knowledge_base"
RESPONSES_JSONL = KB_DIR / "dr_responses.jsonl"
FINDINGS_JSONL = KB_DIR / "findings.jsonl"


# ═══════════════════════════════════════════════════════════════════
# Parsing
# ═══════════════════════════════════════════════════════════════════


def extract_sections(text: str) -> list[dict[str, str]]:
    """Split markdown into sections by ## headings."""
    sections: list[dict[str, str]] = []
    current_heading = ""
    current_body: list[str] = []

    for line in text.split("\n"):
        heading_match = re.match(r"^##\s+(.+)", line)
        if heading_match:
            if current_heading or current_body:
                sections.append({
                    "heading": current_heading,
                    "body": "\n".join(current_body).strip(),
                })
            current_heading = heading_match.group(1).strip()
            current_body = []
        else:
            current_body.append(line)

    if current_heading or current_body:
        sections.append({
            "heading": current_heading,
            "body": "\n".join(current_body).strip(),
        })

    return sections


def detect_actionable_findings(text: str) -> list[str]:
    """Extract sentences that contain actionable recommendations."""
    actionable_keywords = [
        "should", "must", "recommend", "implement", "change",
        "add", "remove", "fix", "update", "create", "replace",
        "needs", "required", "critical", "important", "warning",
    ]
    # Include Arabic question mark; require whitespace after punctuation
    sentences = re.split(r"[.!?\u061F]\s+", text)
    findings = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(kw in lower for kw in actionable_keywords):
            cleaned = sentence.strip()
            if len(cleaned) > 20:  # Skip very short fragments
                findings.append(cleaned)
    return findings


def classify_severity(text: str) -> FindingSeverity:
    """Heuristic severity classification from text content."""
    lower = text.lower()
    if any(w in lower for w in ["critical", "blocks", "broken", "corrupt", "invalid"]):
        return FindingSeverity.CRITICAL
    if any(w in lower for w in ["must", "required", "high", "important", "missing"]):
        return FindingSeverity.HIGH
    if any(w in lower for w in ["should", "recommend", "medium", "consider"]):
        return FindingSeverity.MEDIUM
    return FindingSeverity.LOW


def classify_category(text: str) -> ResearchCategory:
    """Heuristic category classification from text content."""
    lower = text.lower()
    scholarly = sum(1 for w in ["arabic", "islamic", "fiqh", "scholarly", "quran", "hadith", "tree", "taxonomy"] if w in lower)
    engine = sum(1 for w in ["engine", "pipeline", "phase", "test", "spec", "code", "prompt"] if w in lower)
    arch = sum(1 for w in ["architecture", "schema", "design", "system", "data model"] if w in lower)

    if scholarly > engine and scholarly > arch:
        return ResearchCategory.SCHOLARLY_DOMAIN
    if arch > engine:
        return ResearchCategory.ARCHITECTURE
    return ResearchCategory.ENGINE_SPECIFIC


# ═══════════════════════════════════════════════════════════════════
# Main processor
# ═══════════════════════════════════════════════════════════════════


def process_response(
    response_file: Path,
    prompt_id: str,
    source: DRTarget,
    dr_id: str,
) -> tuple[DRResponse, list[Finding]]:
    """Process a DR response file into structured data."""
    text = response_file.read_text(encoding="utf-8")

    # Extract sections
    sections = extract_sections(text)
    logger.info("Found %d sections in response", len(sections))

    # Extract actionable findings from each section
    all_findings: list[Finding] = []
    finding_counter = 0

    # Content hash for finding_id uniqueness across re-runs
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]

    for section in sections:
        actionable = detect_actionable_findings(section["body"])
        for sentence in actionable:
            finding_counter += 1
            finding = Finding(
                finding_id=f"F-{dr_id}-{content_hash}-{finding_counter:03d}",
                source_type="dr_response",
                source_id=dr_id,
                severity=classify_severity(sentence),
                category=classify_category(sentence),
                title=sentence[:100] + ("..." if len(sentence) > 100 else ""),
                description=sentence,
                spec_sections=[],
                action_required="Review and determine action",
            )
            all_findings.append(finding)

    # Build response record
    response = DRResponse(
        response_id=dr_id,
        prompt_id=prompt_id,
        source=source,
        response_file=str(response_file),
        finding_count=len(all_findings),
        finding_ids=[f.finding_id for f in all_findings],
        summary=_generate_summary(sections, all_findings),
    )

    return response, all_findings


def _generate_summary(
    sections: list[dict[str, str]], findings: list[Finding]
) -> str:
    """Generate a 1-2 sentence summary."""
    section_count = len(sections)
    finding_count = len(findings)
    critical = sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL)
    high = sum(1 for f in findings if f.severity == FindingSeverity.HIGH)

    parts = [f"{section_count} sections, {finding_count} actionable findings"]
    if critical:
        parts.append(f"{critical} CRITICAL")
    if high:
        parts.append(f"{high} HIGH")
    return ". ".join(parts) + "."


def persist_results(
    response: DRResponse, findings: list[Finding]
) -> None:
    """Write response and findings to JSONL knowledge base."""
    KB_DIR.mkdir(parents=True, exist_ok=True)
    append_jsonl(RESPONSES_JSONL, response)
    for finding in findings:
        append_jsonl(FINDINGS_JSONL, finding)

    logger.info(
        "Persisted: response %s → %s, %d findings → %s",
        response.response_id,
        RESPONSES_JSONL,
        len(findings),
        FINDINGS_JSONL,
    )


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process a DR response into structured findings"
    )
    parser.add_argument("response_file", type=Path, help="Path to DR response .md file")
    parser.add_argument("--prompt-id", required=True, help="Which prompt this responds to")
    parser.add_argument(
        "--source",
        required=True,
        choices=["chatgpt_dr", "claude_dr", "gemini_dr"],
        help="DR source",
    )
    parser.add_argument("--dr-id", required=True, help="DR identifier (e.g. DR40)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.response_file.exists():
        logger.error("File not found: %s", args.response_file)
        sys.exit(1)

    source = DRTarget(args.source)
    response, findings = process_response(
        args.response_file, args.prompt_id, source, args.dr_id
    )

    persist_results(response, findings)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"DR RESPONSE PROCESSED: {args.dr_id}")
    print(f"{'=' * 60}")
    print(f"  Source:   {source.value}")
    print(f"  Prompt:   {args.prompt_id}")
    print(f"  Findings: {len(findings)}")

    severity_counts: dict[str, int] = {}
    for f in findings:
        severity_counts[f.severity.value] = severity_counts.get(f.severity.value, 0) + 1
    for sev, count in sorted(severity_counts.items()):
        print(f"    {sev}: {count}")

    print(f"\nPersisted to: {KB_DIR}")


if __name__ == "__main__":
    main()
