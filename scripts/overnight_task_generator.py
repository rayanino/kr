"""KR Overnight Task Generator.

Scans repo state to discover beneficial autonomous work. Produces a
prioritized manifest with dependency DAG for the overnight orchestrator.

Usage:
  python scripts/overnight_task_generator.py --output overnight/manifest.json
  python scripts/overnight_task_generator.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Task definition (matches orchestrator)
# ---------------------------------------------------------------------------


@dataclass
class TaskDef:
    task_id: str
    name: str
    category: str
    prompt: str
    safety_level: str = "readonly"
    execution_mode: str = "cli"
    agent: str | None = None
    model: str = "sonnet"
    max_budget_usd: float = 2.0
    timeout_minutes: int = 30
    allowed_tools: list[str] = field(default_factory=list)
    permission_mode: str = "bypassPermissions"
    depends_on: list[str] = field(default_factory=list)
    priority: int = 5
    max_turns: int = 30
    codex_flags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Scanner helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """Run a command and return result."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(PROJECT_DIR), timeout=timeout, env=env,
    )


def _file_age_hours(path: Path) -> float | None:
    """Return hours since file was last modified, or None if missing."""
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    delta = datetime.now(timezone.utc) - mtime
    return delta.total_seconds() / 3600


# ---------------------------------------------------------------------------
# Scanner 1: Test Health
# ---------------------------------------------------------------------------


def scan_test_health() -> list[TaskDef]:
    """Check test suite health and discover coverage gaps."""
    tasks: list[TaskDef] = []

    # Count tests per engine
    for engine_dir in sorted(PROJECT_DIR.glob("engines/*/tests")):
        engine = engine_dir.parent.name
        result = _run(
            ["python", "-m", "pytest", str(engine_dir), "--co", "-q", "--no-header"],
            timeout=30,
        )
        if result.returncode != 0:
            continue
        stdout = result.stdout or ""
        # Count test items
        lines = [l for l in stdout.strip().split("\n") if l.strip() and "::" in l]
        test_count = len(lines)

        # Generate tasks for any engine with tests
        if test_count > 0:
            tasks.append(TaskDef(
                task_id=f"test-coverage-{engine}",
                name=f"Analyze test coverage gaps in {engine} engine",
                category="test",
                prompt=(
                    f"Read engines/{engine}/SPEC.md section 4 and extract every "
                    f"behavioral rule (numbered items, MUST/SHALL statements). "
                    f"Then read all test files in engines/{engine}/tests/ and match "
                    f"each SPEC rule to its test(s). "
                    f"Write a coverage matrix to overnight/results/test-coverage-{engine}/coverage.md "
                    f"showing which rules have tests and which lack tests. "
                    f"Current test count: {test_count}."
                ),
                safety_level="readonly",
                execution_mode="cli",
                model="sonnet",
                timeout_minutes=20,
                priority=4,
                allowed_tools=["Read", "Glob", "Grep", "Bash"],
                depends_on=["val-test-regression"],
            ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 2: SPEC Quality
# ---------------------------------------------------------------------------


def scan_spec_quality() -> list[TaskDef]:
    """Run SPEC quality checks and generate audit tasks."""
    tasks: list[TaskDef] = []

    spec_checker = PROJECT_DIR / "scripts" / "check_spec_quality.py"
    if not spec_checker.exists():
        return tasks

    for spec_path in sorted(PROJECT_DIR.glob("engines/*/SPEC.md")):
        engine = spec_path.parent.name
        result = _run(["python", str(spec_checker), str(spec_path)], timeout=30)

        # Count defects by severity
        high_count = result.stdout.lower().count("high")
        medium_count = result.stdout.lower().count("medium")

        if high_count + medium_count > 3:
            tasks.append(TaskDef(
                task_id=f"spec-audit-{engine}",
                name=f"SPEC quality audit: {engine} engine ({high_count} high, {medium_count} medium)",
                category="spec",
                prompt=(
                    f"Run a thorough quality audit on engines/{engine}/SPEC.md. "
                    f"The automated checker found {high_count} HIGH and {medium_count} MEDIUM "
                    f"defects. Read the SPEC and identify: "
                    f"1. Rules that lack concrete examples with real Arabic text "
                    f"2. Ambiguous language ('appropriate', 'reasonable', 'as needed') "
                    f"3. Cross-references that may be broken "
                    f"4. Untestable behavioral rules "
                    f"Write findings to overnight/results/spec-audit-{engine}/audit.md"
                ),
                safety_level="readonly",
                execution_mode="cli",
                agent="spec-auditor-a",
                model="sonnet",
                timeout_minutes=20,
                priority=5,
                allowed_tools=["Read", "Glob", "Grep"],
                depends_on=["val-test-regression"],
            ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 3: Code Quality
# ---------------------------------------------------------------------------


def scan_code_quality() -> list[TaskDef]:
    """Scan for Arabic-unsafe patterns, missing type hints, etc."""
    tasks: list[TaskDef] = []

    issues_found: list[str] = []

    # Check for \\d in regex (Arabic-Indic digit trap)
    result = _run(["python", "-m", "grep", "-r", r"\\d", "engines/", "--include=*.py"],
                  timeout=10)
    # Fallback: use our Grep-like approach
    try:
        grep_result = subprocess.run(
            ["grep", "-rn", r"\\d", "engines/"],
            capture_output=True, text=True, cwd=str(PROJECT_DIR), timeout=10,
        )
        digit_matches = [
            l for l in grep_result.stdout.strip().split("\n")
            if l.strip() and "# safe: intentional" not in l and "test" not in l.lower()
        ]
        if digit_matches:
            issues_found.append(f"Arabic-Indic digit trap (\\d): {len(digit_matches)} instances")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check for bare except
    try:
        bare_result = subprocess.run(
            ["grep", "-rn", "except:", "engines/"],
            capture_output=True, text=True, cwd=str(PROJECT_DIR), timeout=10,
        )
        bare_matches = [
            l for l in bare_result.stdout.strip().split("\n")
            if l.strip() and "except:" in l and "except:" == l.strip().rstrip("{").strip()
        ]
        if bare_matches:
            issues_found.append(f"Bare except handlers: {len(bare_matches)} instances")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if issues_found:
        tasks.append(TaskDef(
            task_id="cq-scan",
            name=f"Code quality scan ({', '.join(issues_found)})",
            category="code_quality",
            prompt=(
                "Scan all Python files in engines/*/src/ for:\n"
                "1. Regex using \\d instead of [0-9] (Arabic-Indic digit safety)\n"
                "2. .lower()/.upper()/.strip() called on variables that might contain Arabic\n"
                "3. Bare except: handlers\n"
                "4. Missing type hints on function signatures\n"
                "5. Pydantic Field(None) pattern compliance\n"
                "Write findings to overnight/results/cq-scan/scan.md with file:line for each issue."
            ),
            safety_level="readonly",
            execution_mode="cli",
            model="sonnet",
            timeout_minutes=15,
            priority=6,
            allowed_tools=["Read", "Glob", "Grep"],
            depends_on=["val-test-regression"],
        ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 4: Corpus Integrity
# ---------------------------------------------------------------------------


def scan_corpus_integrity() -> list[TaskDef]:
    """Check if corpus sweep is stale or integrity checks are needed."""
    tasks: list[TaskDef] = []

    # Check age of last corpus sweep
    latest_sweep = None
    for sweep_dir in sorted(PROJECT_DIR.glob("results/normalization_sweep_v*")):
        sweep_file = sweep_dir / "corpus_sweep.jsonl"
        if sweep_file.exists():
            latest_sweep = sweep_file

    if latest_sweep:
        age = _file_age_hours(latest_sweep)
        if age and age > 168:  # > 1 week
            tasks.append(TaskDef(
                task_id="val-corpus-integrity",
                name=f"Corpus integrity revalidation (last sweep {age:.0f}h ago)",
                category="validation",
                prompt=(
                    "Run the normalized corpus integrity check:\n"
                    "PYTHONIOENCODING=utf-8 python scripts/verify_normalized_integrity.py "
                    f"--sweep {latest_sweep}\n"
                    "Report findings to overnight/results/val-corpus-integrity/integrity.md"
                ),
                safety_level="readonly",
                execution_mode="cli",
                agent="library-integrity-checker",
                model="sonnet",
                timeout_minutes=60,
                priority=2,
                allowed_tools=["Read", "Bash", "Glob", "Grep"],
                depends_on=["val-test-regression"],
            ))
    else:
        # No sweep found at all
        tasks.append(TaskDef(
            task_id="val-corpus-integrity",
            name="Corpus integrity check (no previous sweep found)",
            category="validation",
            prompt=(
                "Check if any normalization sweep results exist in results/. "
                "If results/normalization_sweep_v3/ exists, run integrity check. "
                "Otherwise report that no sweep data is available."
            ),
            safety_level="readonly",
            execution_mode="cli",
            model="sonnet",
            timeout_minutes=15,
            priority=2,
            allowed_tools=["Read", "Bash", "Glob", "Grep"],
            depends_on=["val-test-regression"],
        ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 5: Contract Boundaries
# ---------------------------------------------------------------------------


def scan_contract_boundaries() -> list[TaskDef]:
    """Check cross-engine contract alignment."""
    tasks: list[TaskDef] = []

    metadata_script = PROJECT_DIR / "scripts" / "verify_metadata_flow.py"
    if metadata_script.exists():
        tasks.append(TaskDef(
            task_id="val-contracts",
            name="Cross-engine contract and D-023 metadata flow verification",
            category="validation",
            prompt=(
                "Run the metadata flow verification:\n"
                "  python3 scripts/verify_metadata_flow.py\n"
                "Also check cross-engine contracts:\n"
                "  PYTHONIOENCODING=utf-8 python tools/check_cross_engine_contracts.py\n"
                "Report findings to overnight/results/val-contracts/boundaries.md"
            ),
            safety_level="readonly",
            execution_mode="cli",
            agent="boundary-validator",
            model="sonnet",
            timeout_minutes=10,
            priority=3,
            allowed_tools=["Read", "Bash", "Glob", "Grep"],
            depends_on=["val-test-regression"],
        ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 6: Known Limitations
# ---------------------------------------------------------------------------


def scan_known_limitations() -> list[TaskDef]:
    """Check if KNOWN_LIMITATIONS.md calibration data is stale."""
    tasks: list[TaskDef] = []

    for kl_path in sorted(PROJECT_DIR.glob("engines/*/KNOWN_LIMITATIONS.md")):
        engine = kl_path.parent.name
        age = _file_age_hours(kl_path)
        if age and age > 168:  # > 1 week since last update
            tasks.append(TaskDef(
                task_id=f"cal-{engine}",
                name=f"Re-calibrate known limitations for {engine} ({age:.0f}h since update)",
                category="doc",
                prompt=(
                    f"Read engines/{engine}/KNOWN_LIMITATIONS.md. "
                    f"For each L-NNN entry that has calibration data (e.g., 'affects N% of corpus'): "
                    f"verify the data is still accurate by checking against the latest "
                    f"corpus sweep results in results/normalization_sweep_v3/. "
                    f"If calibration has drifted >5% from documented value, flag it. "
                    f"Write findings to overnight/results/cal-{engine}/calibration.md"
                ),
                safety_level="readonly",
                execution_mode="cli",
                model="sonnet",
                timeout_minutes=20,
                priority=7,
                allowed_tools=["Read", "Bash", "Glob", "Grep"],
                depends_on=["val-test-regression"],
            ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 7: Documentation
# ---------------------------------------------------------------------------


def scan_documentation() -> list[TaskDef]:
    """Check documentation freshness against recent code changes."""
    tasks: list[TaskDef] = []

    # Check if NEXT.md was updated recently (it should always be current)
    next_md = PROJECT_DIR / "NEXT.md"
    if next_md.exists():
        age = _file_age_hours(next_md)
        # If NEXT.md is more than 48h old, suggest a review
        if age and age > 48:
            tasks.append(TaskDef(
                task_id="doc-freshness",
                name="Documentation freshness check",
                category="doc",
                prompt=(
                    "Check documentation freshness:\n"
                    "1. Read NEXT.md and verify the Progress Tracker matches git history\n"
                    "2. Read each engine's CLAUDE.md and check if it matches the engine's actual state\n"
                    "3. Check if engines/*/KNOWN_LIMITATIONS.md references correct line numbers\n"
                    "Write findings to overnight/results/doc-freshness/report.md"
                ),
                safety_level="readonly",
                execution_mode="cli",
                model="sonnet",
                timeout_minutes=15,
                priority=7,
                allowed_tools=["Read", "Bash", "Glob", "Grep"],
                depends_on=["val-test-regression"],
            ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 8: Research Needs
# ---------------------------------------------------------------------------


def scan_research_needs() -> list[TaskDef]:
    """Check NEXT.md for upcoming engine work that needs research."""
    tasks: list[TaskDef] = []

    next_md = PROJECT_DIR / "NEXT.md"
    if not next_md.exists():
        return tasks

    content = next_md.read_text(encoding="utf-8")

    # Look for references to technology surveys or research
    if "technology survey" in content.lower() or "research" in content.lower():
        # Check which engine is next
        if "excerpting" in content.lower() and "build prep" in content.lower():
            tasks.append(TaskDef(
                task_id="res-tech-survey",
                name="Technology survey for excerpting engine capabilities",
                category="research",
                prompt=(
                    "Research technology options for the excerpting engine. "
                    "Read NEXT.md for context. The excerpting engine needs: "
                    "1. Arabic word/character offset handling libraries "
                    "2. Self-containment assessment approaches "
                    "3. Arabic sentence boundary detection "
                    "Search the web for options. For each library found, check "
                    "if it supports Arabic text (Unicode ranges, diacritics, RTL). "
                    "Write the survey to overnight/results/res-tech-survey/survey.md"
                ),
                safety_level="readonly",
                execution_mode="cli",
                agent="deep-researcher",
                model="sonnet",
                timeout_minutes=20,
                priority=8,
                allowed_tools=["Read", "Bash", "Glob", "Grep", "WebSearch", "WebFetch"],
                depends_on=["val-test-regression"],
            ))

    return tasks


# ---------------------------------------------------------------------------
# Always-present tasks
# ---------------------------------------------------------------------------


def generate_core_tasks() -> list[TaskDef]:
    """Tasks that always run in every overnight session."""
    return [
        TaskDef(
            task_id="val-test-regression",
            name="Test suite regression check",
            category="validation",
            prompt=(
                "Run the full test suite for all completed engines:\n"
                "  python -m pytest engines/source/tests/ engines/normalization/tests/ engines/excerpting/tests/ -v --tb=short\n"
                "Report: total tests, passed, failed, skipped, any error details.\n"
                "Do NOT modify any files."
            ),
            safety_level="readonly",
            execution_mode="cli",
            model="sonnet",
            max_budget_usd=0.50,
            timeout_minutes=10,
            priority=1,
            allowed_tools=["Bash", "Read", "Glob", "Grep"],
            permission_mode="bypassPermissions",
        ),
    ]


# ---------------------------------------------------------------------------
# Codex verification task auto-generation
# ---------------------------------------------------------------------------


def add_codex_verifications(tasks: list[TaskDef]) -> list[TaskDef]:
    """Auto-append Codex verification tasks for additive/modifying Claude tasks."""
    extra: list[TaskDef] = []
    for task in tasks:
        if task.safety_level in ("additive", "modifying") and task.execution_mode != "codex":
            extra.append(TaskDef(
                task_id=f"{task.task_id}-verify",
                name=f"Codex review: {task.name}",
                category="verification",
                prompt=(
                    f"Review the code changes from task '{task.name}'. "
                    f"Check: type safety, Pydantic patterns, test completeness, "
                    f"error handling. Do NOT evaluate Arabic text or domain logic. "
                    f"Run: git diff HEAD~1"
                ),
                safety_level="readonly",
                execution_mode="codex",
                model="gpt-5-codex-mini",
                max_budget_usd=0.50,
                timeout_minutes=10,
                priority=task.priority,
                depends_on=[task.task_id],
                codex_flags=["--full-auto"],
                allowed_tools=[],
            ))
    return tasks + extra


# ---------------------------------------------------------------------------
# Manifest generation
# ---------------------------------------------------------------------------


def generate_manifest(output_path: Path | None = None, dry_run: bool = False) -> list[dict[str, Any]]:
    """Run all scanners and produce a manifest."""
    print("Scanning repo state...")

    all_tasks: list[TaskDef] = []

    # Core tasks (always present)
    core = generate_core_tasks()
    all_tasks.extend(core)
    print(f"  Core tasks: {len(core)}")

    # Scanner tasks
    scanners = [
        ("Test Health", scan_test_health),
        ("SPEC Quality", scan_spec_quality),
        ("Code Quality", scan_code_quality),
        ("Corpus Integrity", scan_corpus_integrity),
        ("Contract Boundaries", scan_contract_boundaries),
        ("Known Limitations", scan_known_limitations),
        ("Documentation", scan_documentation),
        ("Research", scan_research_needs),
    ]

    for name, scanner_fn in scanners:
        try:
            found = scanner_fn()
            all_tasks.extend(found)
            if found:
                print(f"  {name}: {len(found)} tasks")
        except Exception as e:
            print(f"  {name}: FAILED ({e})")

    # Auto-append Codex verifications
    all_tasks = add_codex_verifications(all_tasks)
    verification_count = sum(1 for t in all_tasks if t.category == "verification")
    if verification_count:
        print(f"  Codex verifications: {verification_count}")

    # Sort by priority
    all_tasks.sort(key=lambda t: (t.priority, t.task_id))

    print(f"\nTotal tasks: {len(all_tasks)}")

    # Convert to dicts for JSON
    manifest_data = [asdict(t) for t in all_tasks]

    if dry_run:
        print("\n=== DRY RUN — Generated Manifest ===\n")
        for t in all_tasks:
            deps = f" → depends: {', '.join(t.depends_on)}" if t.depends_on else ""
            print(f"  P{t.priority} [{t.execution_mode:5s}] {t.task_id}: {t.name}{deps}")
        return manifest_data

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps({"tasks": manifest_data}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nManifest written to {output_path}")

    return manifest_data


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="KR Overnight Task Generator")
    parser.add_argument(
        "--output", type=str, default="overnight/manifest.json",
        help="Output path for manifest JSON (default: overnight/manifest.json)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print generated tasks without writing manifest",
    )
    args = parser.parse_args()

    output_path = Path(args.output) if not args.dry_run else None
    generate_manifest(output_path=output_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
