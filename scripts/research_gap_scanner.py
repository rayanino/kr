"""Research gap scanner for the KR autonomous system.

Scans the codebase for unresolved research questions from multiple sources:
- SPEC [OPEN] and [CALIBRATED] markers
- KNOWN_LIMITATIONS.md L-XXX entries
- Test coverage gaps (SPEC rules without matching tests)
- Coworker disagreements
- Owner feedback

Reference: docs/autonomous-system/DESIGN.md §4.2 (Research Gap Scanner)

Usage:
    python scripts/research_gap_scanner.py [--output PATH]
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.autonomous_schemas import (
    DRTarget,
    GapSource,
    Priority,
    ResearchGap,
)

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent
ENGINES_DIR = PROJECT_DIR / "engines"
DEFAULT_OUTPUT = (
    PROJECT_DIR / "overnight_codex" / "autonomous" / "knowledge_base" / "research_gaps.jsonl"
)

# ═══════════════════════════════════════════════════════════════════
# Scanners
# ═══════════════════════════════════════════════════════════════════


def scan_spec_open_markers() -> list[ResearchGap]:
    """Find [OPEN ...] markers in all SPEC.md files.

    Handles: [OPEN: desc], [OPEN — desc], bare [OPEN].
    """
    gaps: list[ResearchGap] = []
    # Match [OPEN] with optional separator (colon, space, em-dash) and description
    pattern = re.compile(r"\[OPEN(?:[:\s\u2014]([^\]]*))?\]")
    gap_counter = 0

    for spec_file in ENGINES_DIR.glob("*/SPEC.md"):
        engine = spec_file.parent.name
        with open(spec_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                for match in pattern.finditer(line):
                    gap_counter += 1
                    raw_desc = match.group(1)
                    description = raw_desc.strip() if raw_desc else "(bare marker)"
                    gaps.append(
                        ResearchGap(
                            gap_id=f"GAP-OPEN-{gap_counter:03d}",
                            source=GapSource.SPEC_OPEN,
                            source_file=str(spec_file.relative_to(PROJECT_DIR)),
                            source_line=line_num,
                            description=f"[{engine}] {description}",
                            recommended_target=_classify_target(description),
                            priority=Priority.HIGH,
                        )
                    )
    return gaps


def scan_known_limitations() -> list[ResearchGap]:
    """Find L-XXX entries in KNOWN_LIMITATIONS.md files.

    Handles: ## L-001: desc, ### L-001, bare L-001 at line start.
    """
    gaps: list[ResearchGap] = []
    # Match L-XXX after optional markdown heading prefix; reject L-0001
    pattern = re.compile(r"^(?:#{1,4}\s+)?(L-[0-9]{3})(?![0-9])")
    gap_counter = 0

    for lim_file in ENGINES_DIR.glob("*/KNOWN_LIMITATIONS.md"):
        engine = lim_file.parent.name
        with open(lim_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                match = pattern.match(line.strip())
                if match:
                    gap_counter += 1
                    gaps.append(
                        ResearchGap(
                            gap_id=f"GAP-LIM-{gap_counter:03d}",
                            source=GapSource.KNOWN_LIMITATION,
                            source_file=str(lim_file.relative_to(PROJECT_DIR)),
                            source_line=line_num,
                            description=f"[{engine}] {line.strip()[:200]}",
                            priority=Priority.MEDIUM,
                        )
                    )
    return gaps


def scan_taxonomy_gaps() -> list[ResearchGap]:
    """Find taxonomy trees with unvalidated or missing nodes."""
    gaps: list[ResearchGap] = []
    sciences_dir = PROJECT_DIR / "library" / "sciences"

    if not sciences_dir.exists():
        return gaps

    gap_counter = 0
    for tree_file in sciences_dir.glob("*/tree_history/*.yaml"):
        science = tree_file.stem.split("_")[0]
        # Match _v0_ or _v1_ but not _v10_ (require non-digit after version)
        if re.search(r"_v[01]_", tree_file.name):
            gap_counter += 1
            gaps.append(
                ResearchGap(
                    gap_id=f"GAP-TAX-{gap_counter:03d}",
                    source=GapSource.TAXONOMY_GAP,
                    source_file=str(tree_file.relative_to(PROJECT_DIR)),
                    description=(
                        f"[taxonomy] {science} tree at version "
                        f"{tree_file.stem} — needs validation through "
                        f"TAXONOMY_TREE_PROTOCOL quality gates"
                    ),
                    recommended_target=DRTarget.GEMINI,
                    priority=Priority.HIGH if "_v0_" in tree_file.name else Priority.MEDIUM,
                )
            )
    return gaps


def scan_spec_calibrated_markers() -> list[ResearchGap]:
    """Find [CALIBRATED: ...] markers — these are RESOLVED gaps (informational)."""
    gaps: list[ResearchGap] = []
    pattern = re.compile(r"\[CALIBRATED[:\s\u2014]([^\]]+)\]")
    gap_counter = 0

    for spec_file in ENGINES_DIR.glob("*/SPEC.md"):
        engine = spec_file.parent.name
        with open(spec_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                match = pattern.search(line)
                if match:
                    gap_counter += 1
                    description = match.group(1).strip()
                    gaps.append(
                        ResearchGap(
                            gap_id=f"GAP-RESOLVED-{gap_counter:03d}",
                            source=GapSource.SPEC_CALIBRATED,
                            source_file=str(spec_file.relative_to(PROJECT_DIR)),
                            source_line=line_num,
                            description=f"[{engine}] RESOLVED: {description}",
                            priority=Priority.LOW,
                            prompt_generated=True,
                        )
                    )
    return gaps


# ═══════════════════════════════════════════════════════════════════
# Classification
# ═══════════════════════════════════════════════════════════════════


def _classify_target(description: str) -> DRTarget:
    """Heuristic: route a gap to the best DR target."""
    scholarly_keywords = [
        "scholarly", "arabic", "islamic", "fiqh", "hadith", "quran",
        "madhab", "taxonomy", "tree", "science", "nahw", "sarf",
        "balagha", "aqidah", "school", "definition",
    ]
    arch_keywords = [
        "architecture", "pipeline", "performance", "schema", "model",
        "orchestr", "deploy", "infra", "pattern",
    ]

    lower = description.lower()
    scholarly_score = sum(1 for kw in scholarly_keywords if kw in lower)
    arch_score = sum(1 for kw in arch_keywords if kw in lower)

    if scholarly_score > arch_score:
        return DRTarget.GEMINI
    if arch_score > scholarly_score:
        return DRTarget.CHATGPT
    return DRTarget.CLAUDE


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════


def run_scan(output_path: Path | None = None) -> dict[str, int]:
    """Run all scanners and write results to JSONL."""
    if not ENGINES_DIR.exists():
        raise FileNotFoundError(
            f"ENGINES_DIR not found: {ENGINES_DIR}. "
            f"Run from the repo root."
        )
    output = output_path or DEFAULT_OUTPUT

    open_gaps = scan_spec_open_markers()
    lim_gaps = scan_known_limitations()
    tax_gaps = scan_taxonomy_gaps()
    resolved_gaps = scan_spec_calibrated_markers()

    all_gaps = open_gaps + lim_gaps + tax_gaps + resolved_gaps

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        for gap in all_gaps:
            f.write(gap.model_dump_json() + "\n")

    return {
        "spec_open": len(open_gaps),
        "known_limitations": len(lim_gaps),
        "taxonomy_gaps": len(tax_gaps),
        "resolved": len(resolved_gaps),
        "total": len(all_gaps),
    }


def _print_scan_summary(
    counts: dict[str, int],
    all_gaps: list[ResearchGap],
    output: Path,
) -> None:
    """Display scan results to stdout (CLI only)."""
    print(f"\n{'=' * 60}")
    print("RESEARCH GAP SCAN RESULTS")
    print(f"{'=' * 60}")
    print(f"  SPEC [OPEN] markers:     {counts['spec_open']}")
    print(f"  Known limitations:       {counts['known_limitations']}")
    print(f"  Taxonomy tree gaps:      {counts['taxonomy_gaps']}")
    print(f"  RESOLVED (informational):{counts['resolved']}")
    print(f"  {'─' * 40}")
    print(f"  TOTAL:                   {counts['total']}")
    print(f"\nOutput: {output}")

    unresolved = [g for g in all_gaps if not g.prompt_generated]
    if unresolved:
        print("\nUnresolved gaps by recommended target:")
        by_target: dict[str, int] = {}
        for g in unresolved:
            t = g.recommended_target.value if g.recommended_target else "unclassified"
            by_target[t] = by_target.get(t, 0) + 1
        for target, count in sorted(by_target.items()):
            print(f"  {target}: {count}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scan for research gaps in the KR codebase"
    )
    parser.add_argument(
        "--output", type=Path, default=None, help="Output JSONL file path",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    output = args.output or DEFAULT_OUTPUT
    counts = run_scan(args.output)

    # Re-read for summary display (run_scan already wrote the file)
    all_gaps: list[ResearchGap] = []
    if output.exists():
        from scripts.autonomous_schemas import read_jsonl
        all_gaps = read_jsonl(output, ResearchGap)  # type: ignore[assignment]

    _print_scan_summary(counts, all_gaps, output)


if __name__ == "__main__":
    main()
