"""Check invariant consistency across KR governance documents.

Detects contradictions in key project invariants (engine count, pipeline
stages, D-rules) across CLAUDE.md, AGENTS.md, principles.md, and MEMORY.md.

Would have caught the 5-vs-7 engine contradiction found by DR26.

Usage:
    python scripts/check_invariant_consistency.py

Exit 0 if consistent, exit 1 if contradictions found.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = Path.home() / ".claude" / "projects" / "C--Users-Rayane-Desktop-kr" / "memory"

# Files to check for invariant consistency
GOVERNANCE_FILES = [
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "AGENTS.md",
    MEMORY_DIR / "principles.md",
    MEMORY_DIR / "MEMORY.md",
]


def extract_engine_counts(text: str) -> list[str]:
    """Find all N-engine references in text."""
    return re.findall(r"(\d+)-engine", text)


def extract_pipeline_stages(text: str) -> list[str]:
    """Find pipeline stage sequences like 'Source → Normalization → ...'."""
    patterns = re.findall(
        r"((?:Source|Normalization|Passaging|Atomization|Excerpting|Taxonomy|Synthesis)"
        r"(?:\s*[→→>─]+\s*(?:Source|Normalization|Passaging|Atomization|Excerpting|Taxonomy|Synthesis))+)",
        text,
    )
    return patterns


def check_engine_count_consistency() -> list[str]:
    """Check that all files agree on engine count."""
    issues = []
    counts_by_file: dict[str, set[str]] = {}

    for path in GOVERNANCE_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        counts = extract_engine_counts(text)
        if counts:
            counts_by_file[path.name] = set(counts)

    all_counts: set[str] = set()
    for counts in counts_by_file.values():
        all_counts.update(counts)

    if len(all_counts) > 1:
        detail = ", ".join(f"{name}: {sorted(cs)}" for name, cs in counts_by_file.items())
        issues.append(
            f"INVARIANT CONTRADICTION — engine count: found {sorted(all_counts)} across files. {detail}"
        )

    return issues


def check_pipeline_stage_consistency() -> list[str]:
    """Check that pipeline stage sequences are consistent."""
    issues = []
    canonical_stages = [
        "Source", "Normalization", "Passaging", "Atomization",
        "Excerpting", "Taxonomy", "Synthesis",
    ]

    for path in GOVERNANCE_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        sequences = extract_pipeline_stages(text)
        for seq in sequences:
            stages = re.split(r"\s*[→→>─]+\s*", seq)
            stages = [s.strip() for s in stages if s.strip()]
            for stage in stages:
                if stage not in canonical_stages:
                    issues.append(
                        f"UNKNOWN STAGE '{stage}' in {path.name} — not in canonical list"
                    )

    return issues


def check_d_rule_references() -> list[str]:
    """Check that D-rule references (D-023, D-041, etc.) are consistent."""
    issues = []
    d_rules_by_file: dict[str, set[str]] = {}

    for path in GOVERNANCE_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        rules = set(re.findall(r"D-0[0-9]{2}", text))
        if rules:
            d_rules_by_file[path.name] = rules

    # No contradiction check needed here — just report what's referenced where
    # Future: check that D-rule descriptions match across files
    all_rules = set()
    for rules in d_rules_by_file.values():
        all_rules.update(rules)

    if all_rules:
        logger.info("D-rules referenced: %s", sorted(all_rules))

    return issues


def check_arabic_invariants() -> list[str]:
    """Check Arabic text handling invariants across governance files.

    Verifies that anti-normalization stance, diacritics preservation,
    and Taa Marbuta prohibition are consistent.
    """
    issues = []

    # Key Arabic invariants that must appear in AGENTS.md
    agents_path = REPO_ROOT / "AGENTS.md"
    if agents_path.exists():
        agents_text = agents_path.read_text(encoding="utf-8")

        required_arabic_rules = [
            ("normalization prohibition", r"(?i)never.*normali[sz]"),
            ("Taa Marbuta warning", r"[ةه]"),
            ("regex digit rule", r"\\d.*Arabic-Indic|\\[0-9\\]"),
            ("diacritics preservation", r"(?i)(?:diacritics?.*preserv|preserv.*diacritics?)"),
            ("isnad atomicity", r"(?i)isnad.*atomic"),
        ]

        for rule_name, pattern in required_arabic_rules:
            if not re.search(pattern, agents_text):
                issues.append(
                    f"AGENTS.md missing Arabic invariant: {rule_name} "
                    f"(pattern '{pattern}' not found)"
                )

    # Check that CLAUDE.md and AGENTS.md don't contradict on normalization
    claude_path = REPO_ROOT / "CLAUDE.md"
    if claude_path.exists() and agents_path.exists():
        claude_text = claude_path.read_text(encoding="utf-8")
        agents_text = agents_path.read_text(encoding="utf-8")

        # Both should prohibit normalization
        claude_prohibits = bool(re.search(r"(?i)never.*normali[sz]|no.*normali[sz]", claude_text))
        agents_prohibits = bool(re.search(r"(?i)never.*normali[sz]|no.*normali[sz]", agents_text))

        if claude_prohibits != agents_prohibits:
            issues.append(
                "NORMALIZATION CONTRADICTION — CLAUDE.md and AGENTS.md disagree on "
                "Unicode normalization prohibition"
            )

    return issues


def main() -> int:
    """Run all invariant consistency checks."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    all_issues: list[str] = []

    logger.info("Checking engine count consistency...")
    all_issues.extend(check_engine_count_consistency())

    logger.info("Checking pipeline stage consistency...")
    all_issues.extend(check_pipeline_stage_consistency())

    logger.info("Checking D-rule references...")
    all_issues.extend(check_d_rule_references())

    logger.info("Checking Arabic text handling invariants...")
    all_issues.extend(check_arabic_invariants())

    if all_issues:
        for issue in all_issues:
            logger.error(issue)
        logger.error("%d invariant issues found", len(all_issues))
        return 1

    logger.info("All invariant checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
