"""Process a DR response file into structured findings (v2).

Paragraph-level extraction with role classification, provider auto-detection,
and auto-populated spec_sections/affected_files.

Reference: docs/autonomous-system/DESIGN.md §4.5 (Response Processing)

Usage:
    python scripts/process_dr_response.py <response_file> --dr-id DR40
    python scripts/process_dr_response.py <response_file> --dr-id DR40 --prompt-id RQ-B2-001 --source gemini_dr
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
    DR_RESPONSES_JSONL,
    FINDINGS_JSONL,
    KB_DIR,
    DRResponse,
    DRTarget,
    Finding,
    FindingSeverity,
    ResearchCategory,
    append_jsonl,
)
from scripts.dr_format_detectors import (
    Section,
    classify_paragraphs,
    detect_provider,
    extract_affected_files,
    extract_sections,
    extract_spec_sections,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Severity / category classification (improved from v1)
# ═══════════════════════════════════════════════════════════════════


def classify_severity(text: str) -> FindingSeverity:
    """Heuristic severity classification from text content."""
    lower = text.lower()
    if any(w in lower for w in [
        "critical", "blocks", "broken", "corrupt", "invalid",
        "existential", "must not", "never",
    ]):
        return FindingSeverity.CRITICAL
    if any(w in lower for w in [
        "must", "required", "high", "important", "missing",
        "the engine must", "mandatory",
    ]):
        return FindingSeverity.HIGH
    if any(w in lower for w in [
        "should", "recommend", "medium", "consider", "improve",
    ]):
        return FindingSeverity.MEDIUM
    return FindingSeverity.LOW


def classify_category(text: str) -> ResearchCategory:
    """Heuristic category classification from text content."""
    lower = text.lower()
    scholarly = sum(
        1 for w in [
            "arabic", "islamic", "fiqh", "scholarly", "quran", "hadith",
            "tree", "taxonomy", "madhab", "nahw", "sarf", "balagha",
            "aqidah", "usul", "isnad",
        ] if w in lower
    )
    engine = sum(
        1 for w in [
            "engine", "pipeline", "phase", "test", "spec", "code", "prompt",
            "excerpting", "passaging", "atomization", "normalization",
        ] if w in lower
    )
    arch = sum(
        1 for w in [
            "architecture", "schema", "design", "system", "data model",
            "dashboard", "knowledge base",
        ] if w in lower
    )

    if scholarly > engine and scholarly > arch:
        return ResearchCategory.SCHOLARLY_DOMAIN
    if arch > engine:
        return ResearchCategory.ARCHITECTURE
    return ResearchCategory.ENGINE_SPECIFIC


# ═══════════════════════════════════════════════════════════════════
# Main processor (v2 — paragraph-level extraction)
# ═══════════════════════════════════════════════════════════════════


def process_response(
    response_file: Path,
    dr_id: str,
    prompt_id: str = "unknown",
    source: DRTarget | None = None,
) -> tuple[DRResponse, list[Finding]]:
    """Process a DR response file into structured data.

    Auto-detects provider if not specified. Uses paragraph-level extraction
    with role classification instead of sentence-level keyword matching.
    """
    text = response_file.read_text(encoding="utf-8")
    line_count = text.count("\n") + 1

    # Auto-detect provider if not specified
    if source is None:
        detection = detect_provider(text)
        source = detection.provider
        logger.info(
            "Auto-detected provider: %s (confidence: %.2f, signals: %s)",
            source.value, detection.confidence, detection.signals,
        )

    # Extract sections using provider-aware strategy
    sections = extract_sections(text, source)
    logger.info("Found %d sections in %s", len(sections), response_file.name)

    # Extract findings — paragraph-level with role classification
    all_findings: list[Finding] = []
    finding_counter = 0

    for section in sections:
        paragraphs = classify_paragraphs(section.body)
        # Collect context from analysis/evidence paragraphs
        context_paras = [
            p.text for p in paragraphs if p.role in ("analysis", "evidence")
        ]
        context_text = "\n\n".join(context_paras[:3]) if context_paras else ""

        for para in paragraphs:
            # Only recommendation and question paragraphs become findings
            if para.role not in ("recommendation", "question"):
                continue

            finding_counter += 1
            full_text = para.text
            para_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()[:12]

            # Build title from first sentence or first 100 chars
            first_sentence_end = re.search(r"[.!?\u061F]\s", full_text)
            if first_sentence_end and first_sentence_end.start() < 120:
                title = full_text[:first_sentence_end.start() + 1]
            else:
                title = full_text[:100] + ("..." if len(full_text) > 100 else "")

            # Build description with context
            description = full_text
            if context_text and len(context_text) < 2000:
                description = f"{full_text}\n\n---\nContext from same section:\n{context_text}"

            finding = Finding(
                finding_id=f"F-{dr_id}-{para_hash}",
                source_type="dr_response",
                source_id=dr_id,
                severity=classify_severity(full_text),
                category=classify_category(full_text),
                title=title,
                description=description,
                spec_sections=extract_spec_sections(full_text),
                affected_files=extract_affected_files(full_text),
                action_required=_infer_action(para.role, full_text),
                prompt_id=prompt_id if prompt_id != "unknown" else None,
                confidence=para.confidence,
                raw_text_hash=para_hash,
                section_heading=section.heading,
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
        summary=_generate_summary(sections, all_findings, line_count),
    )

    return response, all_findings


def _infer_action(role: str, text: str) -> str:
    """Infer action_required from paragraph role and content."""
    if role == "question":
        return "Research needed — generate follow-up DR prompt"
    lower = text.lower()
    if "the engine must" in lower or "implement" in lower:
        return "Implementation change required"
    if "spec" in lower or "§" in text:
        return "SPEC amendment needed"
    if "test" in lower:
        return "Test case needed"
    return "Review and determine action"


def _generate_summary(
    sections: list[Section], findings: list[Finding], line_count: int,
) -> str:
    """Generate a 1-2 sentence summary."""
    section_count = len(sections)
    finding_count = len(findings)
    critical = sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL)
    high = sum(1 for f in findings if f.severity == FindingSeverity.HIGH)

    parts = [f"{line_count} lines, {section_count} sections, {finding_count} findings"]
    if critical:
        parts.append(f"{critical} CRITICAL")
    if high:
        parts.append(f"{high} HIGH")
    return ". ".join(parts) + "."


def persist_results(
    response: DRResponse, findings: list[Finding],
) -> None:
    """Write response and findings to JSONL knowledge base."""
    KB_DIR.mkdir(parents=True, exist_ok=True)
    append_jsonl(DR_RESPONSES_JSONL, response)
    for finding in findings:
        append_jsonl(FINDINGS_JSONL, finding)

    logger.info(
        "Persisted: response %s → %s, %d findings → %s",
        response.response_id, DR_RESPONSES_JSONL,
        len(findings), FINDINGS_JSONL,
    )


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process a DR response into structured findings (v2)"
    )
    parser.add_argument("response_file", type=Path, help="Path to DR response .md file")
    parser.add_argument("--dr-id", required=True, help="DR identifier (e.g. DR40)")
    parser.add_argument("--prompt-id", default="unknown", help="Which prompt this responds to")
    parser.add_argument(
        "--source",
        choices=["chatgpt_dr", "claude_dr", "gemini_dr"],
        default=None,
        help="DR source (auto-detected if omitted)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.response_file.exists():
        logger.error("File not found: %s", args.response_file)
        sys.exit(1)

    source = DRTarget(args.source) if args.source else None
    response, findings = process_response(
        args.response_file, args.dr_id, args.prompt_id, source,
    )

    persist_results(response, findings)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"DR RESPONSE PROCESSED: {args.dr_id}")
    print(f"{'=' * 60}")
    print(f"  Source:     {response.source.value}")
    print(f"  Prompt:     {args.prompt_id}")
    print(f"  Sections:   {len(findings)}")
    print(f"  Findings:   {len(findings)}")

    severity_counts: dict[str, int] = {}
    for f in findings:
        severity_counts[f.severity.value] = severity_counts.get(f.severity.value, 0) + 1
    for sev, count in sorted(severity_counts.items()):
        print(f"    {sev}: {count}")

    spec_refs = set()
    for f in findings:
        spec_refs.update(f.spec_sections)
    if spec_refs:
        print(f"  SPEC refs:  {', '.join(sorted(spec_refs))}")

    print(f"\nPersisted to: {KB_DIR}")


if __name__ == "__main__":
    main()
