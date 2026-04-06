#!/usr/bin/env python3
"""S-07: Static analysis for prompt internal coherence.

Analyzes a prompt file for internal contradictions and structural issues:
  - Duplicate clause detection (exact and fuzzy via normalized comparison)
  - Conflicting modal/quantifier pairs ("always" vs "never" on same noun)
  - Unreachable conditions (if-else chains that can never fire)
  - Token budget accounting by section

Output: coherence_report.md
Exit 0 if clean, exit 1 if contradictions found.

Usage:
    python scripts/prompt_coherence_lint.py path/to/prompt.md
    python scripts/prompt_coherence_lint.py path/to/prompt.md --output report.md
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

# Approximate tokens-per-character ratio for English/mixed text
CHARS_PER_TOKEN = 4


def read_prompt(path: Path) -> str:
    """Read the prompt file content."""
    return path.read_text(encoding="utf-8")


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split text into (heading, body) tuples by markdown headings."""
    parts = re.split(r"^(#{1,4}\s+.+)$", text, flags=re.MULTILINE)
    sections: list[tuple[str, str]] = []
    if parts[0].strip():
        sections.append(("(preamble)", parts[0]))
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append((heading, body))
    return sections


def normalize_clause(clause: str) -> str:
    """Normalize a clause for fuzzy dedup: lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", clause.strip().lower())


def detect_duplicate_clauses(text: str) -> list[dict[str, str]]:
    """Find exact and fuzzy duplicate sentences/clauses."""
    sentences = re.split(r"[.!?\n]", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    seen: dict[str, int] = {}
    duplicates: list[dict[str, str]] = []

    for i, sentence in enumerate(sentences):
        normalized = normalize_clause(sentence)
        if normalized in seen:
            duplicates.append({
                "type": "duplicate_clause",
                "severity": "HIGH",
                "first_occurrence_line": str(seen[normalized]),
                "duplicate_at_index": str(i),
                "text_preview": sentence[:80],
            })
        else:
            seen[normalized] = i
    return duplicates


def detect_modal_conflicts(text: str) -> list[dict[str, str]]:
    """Find conflicting modal/quantifier pairs on the same noun."""
    always_pattern = re.compile(r"\b(always|must|shall)\s+(\w+)", re.IGNORECASE)
    never_pattern = re.compile(r"\b(never|must not|shall not)\s+(\w+)", re.IGNORECASE)

    always_targets: dict[str, str] = {}
    for match in always_pattern.finditer(text):
        modal = match.group(1)
        target = match.group(2).lower()
        always_targets[target] = f"{modal} {match.group(2)}"

    conflicts: list[dict[str, str]] = []
    for match in never_pattern.finditer(text):
        modal = match.group(1)
        target = match.group(2).lower()
        if target in always_targets:
            conflicts.append({
                "type": "modal_conflict",
                "severity": "CRITICAL",
                "positive": always_targets[target],
                "negative": f"{modal} {match.group(2)}",
                "target_word": target,
            })
    return conflicts


def detect_unreachable_conditions(text: str) -> list[dict[str, str]]:
    """Detect if-else patterns where conditions may be unreachable."""
    issues: list[dict[str, str]] = []
    # Look for patterns like "If X, ... If not X, ... Otherwise, ..."
    if_blocks = re.findall(
        r"(?:^|\n)\s*[-*]?\s*[Ii]f\s+(.+?)(?:,|:|\n)",
        text,
    )
    normalized_conditions: dict[str, int] = defaultdict(int)
    for cond in if_blocks:
        key = normalize_clause(cond)
        normalized_conditions[key] += 1

    for cond, count in normalized_conditions.items():
        if count > 1:
            issues.append({
                "type": "repeated_condition",
                "severity": "MEDIUM",
                "condition": cond[:80],
                "occurrences": str(count),
            })
    return issues


def compute_section_tokens(sections: list[tuple[str, str]]) -> list[dict[str, str | int]]:
    """Estimate token count per section."""
    result: list[dict[str, str | int]] = []
    for heading, body in sections:
        char_count = len(body)
        token_est = max(1, char_count // CHARS_PER_TOKEN)
        result.append({
            "section": heading,
            "chars": char_count,
            "estimated_tokens": token_est,
        })
    return result


def format_report(
    findings: list[dict[str, str]],
    token_budget: list[dict[str, str | int]],
    prompt_path: str,
) -> str:
    """Format the coherence report as markdown."""
    lines = [
        "# Prompt Coherence Report",
        "",
        f"Prompt: `{prompt_path}`",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("_No coherence issues found._")
    else:
        for f in findings:
            severity = f.get("severity", "UNKNOWN")
            ftype = f.get("type", "unknown")
            detail_parts = [f"**[{severity}]** {ftype}"]
            for k, v in f.items():
                if k not in ("type", "severity"):
                    detail_parts.append(f"  - {k}: {v}")
            lines.append("\n".join(detail_parts))
            lines.append("")

    lines.append("## Token Budget by Section")
    lines.append("")
    lines.append("| Section | Chars | Est. Tokens |")
    lines.append("|---|---|---|")
    total_tokens = 0
    for entry in token_budget:
        tokens = entry["estimated_tokens"]
        total_tokens += int(tokens)
        lines.append(f"| {entry['section']} | {entry['chars']} | {tokens} |")
    lines.append(f"| **Total** | | **{total_tokens}** |")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    """Entry point: lint prompt file, write report."""
    parser = argparse.ArgumentParser(
        description="S-07: Static analysis for prompt internal coherence.",
    )
    parser.add_argument(
        "prompt_file",
        type=Path,
        help="Path to the prompt file to analyze.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for coherence_report.md (default: alongside prompt file).",
    )
    args = parser.parse_args()

    prompt_path: Path = args.prompt_file.resolve()
    if not prompt_path.is_file():
        log.error("Prompt file not found: %s", prompt_path)
        return 1

    log.info("Analyzing prompt: %s", prompt_path)
    text = read_prompt(prompt_path)

    sections = split_sections(text)
    log.info("Found %d sections", len(sections))

    findings: list[dict[str, str]] = []
    findings.extend(detect_duplicate_clauses(text))
    findings.extend(detect_modal_conflicts(text))
    findings.extend(detect_unreachable_conditions(text))

    token_budget = compute_section_tokens(sections)

    # Sort by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    findings.sort(key=lambda f: severity_order.get(f.get("severity", "LOW"), 99))

    output_path: Path = (
        args.output or prompt_path.parent / "coherence_report.md"
    ).resolve()

    report = format_report(findings, token_budget, str(prompt_path.name))
    output_path.write_text(report, encoding="utf-8")
    log.info("Report written to %s", output_path)

    contradictions = [
        f for f in findings if f.get("severity") in ("CRITICAL", "HIGH")
    ]
    if contradictions:
        log.error(
            "FAIL: %d contradiction(s) found (%d critical, %d high)",
            len(contradictions),
            sum(1 for c in contradictions if c["severity"] == "CRITICAL"),
            sum(1 for c in contradictions if c["severity"] == "HIGH"),
        )
        return 1

    log.info("PASS: no contradictions found (%d advisory findings)", len(findings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
