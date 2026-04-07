"""Quality gate for DR response digestion (Component E).

Validates digestion completeness and quality before findings are trusted:
- Section count vs line count ratio
- Finding count and confidence distribution
- Cross-reference population
- Severity distribution sanity check

Produces a DigestionRecord with quality score for each processed DR response.

Usage:
    python scripts/digestion_quality_gate.py --dr-id DR40
    python scripts/digestion_quality_gate.py --all
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.autonomous_schemas import (
    Contradiction,
    DRResponse,
    DRTarget,
    DigestionRecord,
    Finding,
    FindingSeverity,
    append_jsonl,
    read_jsonl,
)

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent
KB_DIR = PROJECT_DIR / "overnight_codex" / "autonomous" / "knowledge_base"
RESPONSES_JSONL = KB_DIR / "dr_responses.jsonl"
FINDINGS_JSONL = KB_DIR / "findings.jsonl"
CONTRADICTIONS_JSONL = KB_DIR / "contradictions.jsonl"
DIGESTION_LOG = KB_DIR / "digestion_log.jsonl"


# ═══════════════════════════════════════════════════════════════════
# Quality checks
# ═══════════════════════════════════════════════════════════════════


class QualityCheck:
    """A single quality check result."""

    def __init__(self, name: str, passed: bool, detail: str, weight: float = 1.0) -> None:
        self.name = name
        self.passed = passed
        self.detail = detail
        self.weight = weight


def check_section_ratio(response: DRResponse, findings: list[Finding]) -> QualityCheck:
    """Verify reasonable section-to-finding ratio."""
    # Parse line count from summary (format: "N lines, M sections, K findings.")
    line_count = 0
    if response.summary:
        parts = response.summary.split(",")
        for part in parts:
            part = part.strip()
            if "lines" in part:
                try:
                    line_count = int(part.split()[0])
                except (ValueError, IndexError):
                    pass

    if line_count == 0:
        return QualityCheck(
            "section_ratio", False,
            "Could not determine line count from summary",
            weight=0.5,
        )

    findings_per_100_lines = (len(findings) / line_count) * 100 if line_count > 0 else 0

    if findings_per_100_lines < 0.5:
        return QualityCheck(
            "section_ratio", False,
            f"Too few findings: {len(findings)} from {line_count} lines "
            f"({findings_per_100_lines:.1f} per 100 lines, expected >= 0.5)",
        )

    if findings_per_100_lines > 20:
        return QualityCheck(
            "section_ratio", False,
            f"Too many findings: {len(findings)} from {line_count} lines "
            f"({findings_per_100_lines:.1f} per 100 lines, expected <= 20). "
            f"Parser may be over-fragmenting.",
        )

    return QualityCheck(
        "section_ratio", True,
        f"{len(findings)} findings from {line_count} lines "
        f"({findings_per_100_lines:.1f} per 100 lines)",
    )


def check_confidence_distribution(findings: list[Finding]) -> QualityCheck:
    """Verify confidence scores are reasonable (not all low)."""
    if not findings:
        return QualityCheck("confidence", True, "No findings to check", weight=0.5)

    avg_confidence = sum(f.confidence for f in findings) / len(findings)
    low_confidence_count = sum(1 for f in findings if f.confidence < 0.4)
    low_ratio = low_confidence_count / len(findings)

    if avg_confidence < 0.3:
        return QualityCheck(
            "confidence", False,
            f"Average confidence too low: {avg_confidence:.2f} "
            f"({low_confidence_count}/{len(findings)} below 0.4)",
        )

    if low_ratio > 0.7:
        return QualityCheck(
            "confidence", False,
            f"{low_ratio:.0%} of findings have low confidence (<0.4). "
            f"Parser may not be classifying paragraphs well.",
        )

    return QualityCheck(
        "confidence", True,
        f"Average confidence: {avg_confidence:.2f}, "
        f"{low_confidence_count}/{len(findings)} low-confidence",
    )


def check_severity_distribution(findings: list[Finding]) -> QualityCheck:
    """Verify severity distribution is not degenerate (all same level)."""
    if len(findings) < 3:
        return QualityCheck("severity_dist", True, "Too few findings to check distribution", weight=0.3)

    severities = {f.severity for f in findings}
    if len(severities) == 1:
        return QualityCheck(
            "severity_dist", False,
            f"All {len(findings)} findings have the same severity ({findings[0].severity.value}). "
            f"Heuristic classifier may be stuck.",
            weight=0.8,
        )

    return QualityCheck(
        "severity_dist", True,
        f"{len(severities)} distinct severity levels across {len(findings)} findings",
    )


def check_spec_coverage(findings: list[Finding]) -> QualityCheck:
    """Verify that at least some findings have spec_sections populated."""
    if not findings:
        return QualityCheck("spec_coverage", True, "No findings", weight=0.3)

    with_specs = sum(1 for f in findings if f.spec_sections)
    ratio = with_specs / len(findings)

    if ratio < 0.1 and len(findings) >= 5:
        return QualityCheck(
            "spec_coverage", False,
            f"Only {with_specs}/{len(findings)} findings have SPEC references. "
            f"extract_spec_sections may be failing.",
            weight=0.7,
        )

    return QualityCheck(
        "spec_coverage", True,
        f"{with_specs}/{len(findings)} findings have SPEC references ({ratio:.0%})",
    )


def check_cross_references(findings: list[Finding]) -> QualityCheck:
    """Verify cross-references are populated (post cross_reference_findings.py)."""
    if not findings:
        return QualityCheck("cross_refs", True, "No findings", weight=0.3)

    with_refs = sum(1 for f in findings if f.related_finding_ids)

    if not with_refs:
        return QualityCheck(
            "cross_refs", False,
            "No findings have cross-references. Run cross_reference_findings.py first.",
            weight=0.5,
        )

    return QualityCheck(
        "cross_refs", True,
        f"{with_refs}/{len(findings)} findings have cross-references",
    )


def check_minimum_findings(response: DRResponse, findings: list[Finding]) -> QualityCheck:
    """A DR response should produce at least 1 finding."""
    if not findings:
        return QualityCheck(
            "min_findings", False,
            f"DR {response.response_id} produced 0 findings. "
            f"Parser may have failed to extract any content.",
            weight=2.0,
        )
    return QualityCheck("min_findings", True, f"{len(findings)} findings extracted")


# ═══════════════════════════════════════════════════════════════════
# Gate decision
# ═══════════════════════════════════════════════════════════════════


def run_quality_gate(
    response: DRResponse, findings: list[Finding],
) -> tuple[list[QualityCheck], float, str]:
    """Run all quality checks. Returns (checks, score, verdict).

    Score: 0.0-1.0 (weighted pass ratio).
    Verdict: PASS / WARN / FAIL.
    """
    checks = [
        check_minimum_findings(response, findings),
        check_section_ratio(response, findings),
        check_confidence_distribution(findings),
        check_severity_distribution(findings),
        check_spec_coverage(findings),
        check_cross_references(findings),
    ]

    total_weight = sum(c.weight for c in checks)
    passed_weight = sum(c.weight for c in checks if c.passed)
    score = passed_weight / total_weight if total_weight > 0 else 0.0

    if score >= 0.8:
        verdict = "PASS"
    elif score >= 0.5:
        verdict = "WARN"
    else:
        verdict = "FAIL"

    return checks, score, verdict


# ═══════════════════════════════════════════════════════════════════
# Persistence
# ═══════════════════════════════════════════════════════════════════


def build_digestion_record(
    response: DRResponse,
    findings: list[Finding],
    contradictions: list[Contradiction],
    score: float,
    verdict: str,
) -> DigestionRecord:
    """Build a DigestionRecord from gate results."""
    # Count sections from response summary
    section_count = 0
    if response.summary:
        for part in response.summary.split(","):
            if "sections" in part:
                try:
                    section_count = int(part.strip().split()[0])
                except (ValueError, IndexError):
                    pass

    # Parse line count
    line_count = 0
    if response.summary:
        for part in response.summary.split(","):
            if "lines" in part:
                try:
                    line_count = int(part.strip().split()[0])
                except (ValueError, IndexError):
                    pass

    return DigestionRecord(
        dr_id=response.response_id,
        response_file=response.response_file,
        provider=response.source,
        line_count=line_count,
        section_count=section_count,
        finding_count=len(findings),
        contradiction_count=len(contradictions),
        status=verdict.lower(),
    )


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Quality gate for DR digestion")
    parser.add_argument("--dr-id", help="Check a specific DR response")
    parser.add_argument("--all", action="store_true", help="Check all DR responses")
    parser.add_argument("--persist", action="store_true", help="Write DigestionRecord to log")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.dr_id and not args.all:
        parser.error("Specify --dr-id DR40 or --all")

    # Load all data
    responses_raw = read_jsonl(RESPONSES_JSONL, DRResponse)
    responses: list[DRResponse] = [r for r in responses_raw if isinstance(r, DRResponse)]

    findings_raw = read_jsonl(FINDINGS_JSONL, Finding)
    all_findings: list[Finding] = [f for f in findings_raw if isinstance(f, Finding)]

    contras_raw = read_jsonl(CONTRADICTIONS_JSONL, Contradiction) if CONTRADICTIONS_JSONL.exists() else []
    all_contradictions: list[Contradiction] = [c for c in contras_raw if isinstance(c, Contradiction)]

    # Filter to requested DR(s)
    if args.dr_id:
        responses = [r for r in responses if r.response_id == args.dr_id]
        if not responses:
            logger.error("DR response %s not found in %s", args.dr_id, RESPONSES_JSONL)
            sys.exit(1)

    for response in responses:
        # Filter findings for this DR
        dr_findings = [f for f in all_findings if f.source_id == response.response_id]
        dr_contradictions = [
            c for c in all_contradictions
            if c.dr_id_a == response.response_id or c.dr_id_b == response.response_id
        ]

        checks, score, verdict = run_quality_gate(response, dr_findings)

        print(f"\n{'=' * 60}")
        print(f"QUALITY GATE: {response.response_id}  [{verdict}]  score={score:.2f}")
        print(f"{'=' * 60}")
        print(f"  Source: {response.source.value}")
        print(f"  Findings: {len(dr_findings)}")
        print(f"  Contradictions: {len(dr_contradictions)}")

        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"  [{status}] {check.name}: {check.detail}")

        if args.persist:
            record = build_digestion_record(
                response, dr_findings, dr_contradictions, score, verdict,
            )
            append_jsonl(DIGESTION_LOG, record)
            logger.info("Persisted DigestionRecord for %s", response.response_id)


if __name__ == "__main__":
    main()
