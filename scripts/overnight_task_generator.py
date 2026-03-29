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
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import date as date_type
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
    model: str = "opus"
    max_budget_usd: float = 5.0
    timeout_minutes: int = 35
    allowed_tools: list[str] = field(default_factory=list)
    permission_mode: str = "bypassPermissions"
    depends_on: list[str] = field(default_factory=list)
    priority: int = 5
    max_turns: int = 40
    codex_flags: list[str] = field(default_factory=list)
    bookend: bool = False  # Always-run task: skips dependency propagation, runs last


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
                depends_on=[],
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
                depends_on=[],
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
            depends_on=[],
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
                depends_on=[],
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
            depends_on=[],
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
            depends_on=[],
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
                depends_on=[],
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
                depends_on=[],
            ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 8: Research Needs
# ---------------------------------------------------------------------------


def scan_recent_changes() -> list[TaskDef]:
    """Generate code review and hardening tasks for recently modified code."""
    tasks: list[TaskDef] = []

    # Find recently modified engine source files (last 24h)
    recent_files: list[str] = []
    for src_dir in sorted(PROJECT_DIR.glob("engines/*/src")):
        engine = src_dir.parent.name
        for py_file in src_dir.glob("*.py"):
            age = _file_age_hours(py_file)
            if age is not None and age < 24:
                recent_files.append(f"engines/{engine}/src/{py_file.name}")

    if not recent_files:
        return tasks

    # Group by engine
    by_engine: dict[str, list[str]] = {}
    for f in recent_files:
        engine = f.split("/")[1]
        by_engine.setdefault(engine, []).append(f)

    for engine, files in by_engine.items():
        file_list = "\n".join(f"  - {f}" for f in files)

        # Task 1: Code review (readonly)
        tasks.append(TaskDef(
            task_id=f"review-recent-{engine}",
            name=f"Review recently modified {engine} code ({len(files)} files)",
            category="review",
            prompt=(
                f"TASK: Code review of recently modified {engine} engine source files.\n\n"
                f"Read engines/{engine}/CLAUDE.md for context.\n"
                f"Read the SPEC section governing these files.\n\n"
                f"Files modified in the last 24 hours:\n{file_list}\n\n"
                f"Review for:\n"
                f"1. SPEC compliance — does the code match the behavioral rules?\n"
                f"2. Arabic text safety — no .lower()/.upper()/.strip() on Arabic, no \\d in regex\n"
                f"3. D-023 metadata pass-through — all upstream fields preserved\n"
                f"4. Error handling — fails loudly with SPEC error codes?\n"
                f"5. Edge cases that lack test coverage\n\n"
                f"Write detailed findings to overnight/results/review-recent-{engine}/review.md\n"
                f"Do NOT modify any source files. This is a READ-ONLY review."
            ),
            safety_level="readonly",
            execution_mode="cli",
            model="opus",
            timeout_minutes=45,
            priority=1,
            max_turns=30,
            allowed_tools=["Read", "Glob", "Grep", "Bash"],
        ))

        # Task 2: Edge case hardening tests (modifying, depends on review)
        tasks.append(TaskDef(
            task_id=f"harden-recent-{engine}",
            name=f"Edge case hardening for recent {engine} changes",
            category="test",
            prompt=(
                f"TASK: Write edge case and hardening tests for recently modified {engine} code.\n\n"
                f"Read engines/{engine}/CLAUDE.md for context.\n"
                f"Read the review at overnight/results/review-recent-{engine}/review.md for findings.\n"
                f"Read existing tests in engines/{engine}/tests/.\n\n"
                f"Recently modified files:\n{file_list}\n\n"
                f"For each finding in the review (especially HIGH and MEDIUM):\n"
                f"1. Write a targeted test that exercises the edge case\n"
                f"2. Use real Arabic text from tests/fixtures/ wherever possible\n"
                f"3. Follow conftest factory patterns\n\n"
                f"Rules: use [0-9] not \\d. Never .lower()/.upper()/.strip() on Arabic.\n"
                f"Run: python -m pytest engines/{engine}/tests/ -x -v --tb=short\n"
                f"All existing + new tests must pass."
            ),
            safety_level="modifying",
            execution_mode="cli",
            model="opus",
            timeout_minutes=45,
            priority=2,
            max_turns=40,
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
            depends_on=[f"review-recent-{engine}"],
        ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 9: Empirical Validations (Defense 1A data collection)
# ---------------------------------------------------------------------------


def scan_empirical_validations() -> list[TaskDef]:
    """Check if empirical validation scans need to run."""
    tasks: list[TaskDef] = []

    script = PROJECT_DIR / "scripts" / "empirical_backrefs.py"
    if not script.exists():
        return tasks

    result_file = PROJECT_DIR / "overnight" / "results" / "empirical-backrefs" / "scan.json"
    age = _file_age_hours(result_file)

    # Run if result doesn't exist or is > 24h old
    if age is None or age > 24:
        tasks.append(TaskDef(
            task_id="empirical-backrefs",
            name="Empirical scan: Arabic back-reference patterns in fixtures (Defense 1A)",
            category="validation",
            prompt=(
                "Run the empirical back-reference scanner:\n"
                "  python scripts/empirical_backrefs.py "
                "--output overnight/results/empirical-backrefs/scan.json\n\n"
                "Read the output and write a brief interpretation to "
                "overnight/results/empirical-backrefs/summary.md:\n"
                "- Which patterns had the most hits?\n"
                "- Is the hit rate sufficient to justify building Defense 1A?\n"
                "- What is the recommended decision (PROCEED or SKIP)?"
            ),
            safety_level="readonly",
            execution_mode="cli",
            model="sonnet",
            max_budget_usd=2.0,
            timeout_minutes=15,
            priority=1,
            max_turns=15,
            allowed_tools=["Bash", "Read"],
        ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 10: Model Research (NEXT.md research tasks)
# ---------------------------------------------------------------------------


def scan_model_research() -> list[TaskDef]:
    """Detect if model role assignment research is needed."""
    tasks: list[TaskDef] = []

    next_md = PROJECT_DIR / "NEXT.md"
    if not next_md.exists():
        return tasks

    next_content = next_md.read_text(encoding="utf-8", errors="replace")
    if "Model Role Assignment Research" not in next_content:
        return tasks

    # Check if contracts.py still has stale model strings
    contracts = PROJECT_DIR / "engines" / "excerpting" / "contracts.py"
    if contracts.exists():
        contracts_content = contracts.read_text(encoding="utf-8", errors="replace")
        has_stale = "gpt-4.1" in contracts_content or "command-a" in contracts_content
        if not has_stale:
            return tasks  # Already updated

    # Check if research was already done recently
    findings = PROJECT_DIR / "overnight" / "results" / "model-research" / "findings.md"
    age = _file_age_hours(findings)
    if age is not None and age < 24:
        return tasks  # Recent findings exist

    tasks.append(TaskDef(
        task_id="model-research",
        name="Model role assignment research: compare Opus 4.6 / GPT-5.4 / Gemini 3.1 Pro",
        category="research",
        prompt=(
            "Execute the model role assignment research defined in NEXT.md Task 1.\n\n"
            "You are the model-researcher agent. Follow your research protocol:\n"
            "1. Load context: NEXT.md, contracts.py:749-761, SPEC.md §7.3\n"
            "2. Run 8-10+ web searches for Arabic capability benchmarks per model\n"
            "3. Evaluate each model for Primary, Verifier, and Escalation roles\n"
            "4. Design an empirical probe with 3 specific chunks\n"
            "5. Write structured findings to overnight/results/model-research/findings.md\n\n"
            "The different-provider requirement means Primary and Verifier MUST be "
            "from different providers (SPEC §7.3).\n"
            "All models must be available on OpenRouter.\n"
            "Cite specific URLs and benchmark data for every claim."
        ),
        safety_level="readonly",
        execution_mode="cli",
        agent="model-researcher",
        model="opus",
        max_budget_usd=15.0,
        timeout_minutes=45,
        priority=3,
        max_turns=40,
        allowed_tools=["Read", "Grep", "Glob", "WebSearch", "WebFetch", "Bash"],
    ))

    return tasks


# ---------------------------------------------------------------------------
# Scanner 11: Knowledge Integrity Probes (T-1 through T-7)
# ---------------------------------------------------------------------------


def scan_knowledge_integrity() -> list[TaskDef]:
    """Generate knowledge corruption probes for active engines.

    Targets the 7 threat categories from KNOWLEDGE_INTEGRITY.md:
    T-1: Attribution corruption (wrong scholar)
    T-2: Evidence corruption (wrong references)
    T-3: Text corruption (altered primary text)
    T-4: Boundary corruption (wrong excerpt range)
    T-5: Metadata loss (D-023 violations)
    T-6: Consensus bypass (single-model decisions)
    T-7: Gate corruption (wrong human gate entries)
    """
    tasks: list[TaskDef] = []

    # Only probe engines that have implementation (src/ directory with .py files)
    for engine_dir in sorted(PROJECT_DIR.glob("engines/*/src")):
        engine = engine_dir.parent.name
        py_files = list(engine_dir.glob("*.py"))
        if not py_files:
            continue

        # Check which Phase 3 files exist (knowledge-sensitive code)
        phase3_files = [f.name for f in py_files if "phase3" in f.name]
        has_writer = any(f.name == "writer.py" for f in py_files)

        if not phase3_files:
            continue  # Only excerpting has Phase 3

        # Probe 1: Attribution corruption (T-1)
        tasks.append(TaskDef(
            task_id=f"ki-attribution-{engine}",
            name=f"Knowledge integrity: attribution corruption probe ({engine})",
            category="test",
            prompt=(
                f"KNOWLEDGE CORRUPTION PROBE — T-1: Attribution Corruption\n\n"
                f"Read engines/{engine}/src/phase3_deterministic.py, focusing on "
                f"_compute_layer_coverages() and compute_layer_attribution().\n\n"
                f"Hunt for scenarios where layer attribution produces WRONG RESULTS:\n"
                f"1. All layers have author_canonical_id=None — does merging collapse distinct layers?\n"
                f"2. Two layers with same (type, author) but different scholarly functions\n"
                f"3. LA rule cascade with exact boundary values (80.0%, 100.0%)\n"
                f"4. compute_quoted_scholars excluding correct layers or including wrong ones\n\n"
                f"For EACH scenario found, write a targeted test with real Arabic text.\n"
                f"If you find a bug, FIX IT and explain why it corrupts knowledge.\n"
                f"Run: python -m pytest engines/{engine}/tests/ -x -v --tb=short"
            ),
            safety_level="modifying",
            execution_mode="cli",
            model="opus",
            timeout_minutes=40,
            priority=1,
            max_turns=30,
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        ))

        # Probe 2: Text integrity (T-3)
        if has_writer:
            tasks.append(TaskDef(
                task_id=f"ki-text-integrity-{engine}",
                name=f"Knowledge integrity: Arabic text round-trip probe ({engine})",
                category="test",
                prompt=(
                    f"KNOWLEDGE CORRUPTION PROBE — T-3: Text Corruption\n\n"
                    f"Read engines/{engine}/src/writer.py.\n\n"
                    f"Verify Arabic text survives serialization BYTE-FOR-BYTE:\n"
                    f"1. Text with full tashkeel (diacritics) — fathah, dammah, kasrah, shadda, sukun\n"
                    f"2. ZWNJ (U+200C) between Arabic letters\n"
                    f"3. Tatweel (U+0640) inside words\n"
                    f"4. Superscript alef (U+0670)\n"
                    f"5. Paragraph breaks (\\n\\n) in primary_text\n\n"
                    f"Write to JSONL, read back, verify byte-identical.\n"
                    f"If Pydantic or JSON serialization alters any byte, this is CRITICAL.\n"
                    f"Run: python -m pytest engines/{engine}/tests/ -x -v --tb=short"
                ),
                safety_level="modifying",
                execution_mode="cli",
                model="opus",
                timeout_minutes=35,
                priority=1,
                max_turns=25,
                allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
            ))

    return tasks


# ---------------------------------------------------------------------------
# Always-present tasks
# ---------------------------------------------------------------------------


def generate_core_tasks() -> list[TaskDef]:
    """Tasks that always run in every overnight session."""
    return [
        # Regression test is a bookend — always runs last regardless of other failures
        TaskDef(
            task_id="val-test-regression",
            name="Test suite regression check",
            category="validation",
            prompt=(
                "Run the full test suite for all completed engines SEPARATELY:\n"
                "  python -m pytest engines/source/tests/ -v --tb=short\n"
                "  python -m pytest engines/normalization/tests/ -v --tb=short\n"
                "  python -m pytest engines/excerpting/tests/ -v --tb=short\n"
                "Report: total tests, passed, failed, skipped, any error details.\n"
                "Write report to overnight/results/val-test-regression/summary.md\n"
                "Do NOT modify any files."
            ),
            safety_level="readonly",
            execution_mode="cli",
            model="sonnet",
            max_budget_usd=0.50,
            timeout_minutes=10,
            priority=99,  # Runs last
            max_turns=15,
            allowed_tools=["Bash", "Read", "Glob", "Grep"],
            permission_mode="bypassPermissions",
            bookend=True,  # Always runs regardless of other task failures
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
                codex_flags=[],  # orchestrator already adds --full-auto
                allowed_tools=[],
            ))
    return tasks + extra


# ---------------------------------------------------------------------------
# Creative task scanner
# ---------------------------------------------------------------------------

CREATIVE_TEMPLATES_DIR = PROJECT_DIR / "overnight" / "creative_templates"
CREATIVE_RUN_LOG = PROJECT_DIR / "overnight" / "creative_run_log.json"
PIPELINE_ORDER = ["source", "normalization", "excerpting", "taxonomy", "synthesis"]
GEMINI_MAX_PER_RUN = 10


def _load_creative_run_log() -> dict[str, str]:
    """Load the creative run log (template_id:target -> last_run_date)."""
    if CREATIVE_RUN_LOG.exists():
        try:
            data = json.loads(CREATIVE_RUN_LOG.read_text(encoding="utf-8"))
            return data.get("runs", {})
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def creative_log_key(template_id: str, engine: str) -> str:
    """Canonical key for creative run log. Used by both scanner and updater.

    Format: template_id with / replaced by - , then - , then engine name.
    Must stay in sync with _update_creative_run_log() in overnight_orchestrator.py.
    """
    return f"{template_id.replace('/', '-')}-{engine}"


def _detect_active_engine() -> str:
    """Parse NEXT.md for the active engine name."""
    next_md = PROJECT_DIR / "NEXT.md"
    if next_md.exists():
        text = next_md.read_text(encoding="utf-8")[:500]
        # Reverse order: check longer/more-specific names first
        # to avoid "source" matching inside "resource"
        for engine in reversed(PIPELINE_ORDER):
            if re.search(rf"\b{engine}\b", text, re.IGNORECASE):
                return engine
    return "excerpting"


def _load_creative_templates() -> list[dict]:
    """Load all JSON templates from overnight/creative_templates/."""
    templates = []
    if not CREATIVE_TEMPLATES_DIR.exists():
        return templates
    for f in sorted(CREATIVE_TEMPLATES_DIR.rglob("*.json")):
        try:
            tmpl = json.loads(f.read_text(encoding="utf-8"))
            templates.append(tmpl)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  WARNING: Failed to load template {f}: {e}")
    return templates


def _days_since(date_str: str) -> int:
    """Days since a YYYY-MM-DD date string."""
    last = date_type.fromisoformat(date_str)
    return (date_type.today() - last).days


def _resolve_variable(var_def: dict, active_engine: str) -> str:
    """Resolve a single template variable."""
    source = var_def.get("source", "literal")
    if source == "active_engine":
        return active_engine
    if source == "literal":
        return var_def.get("value", "")
    if source == "run_date":
        return date_type.today().isoformat()
    return var_def.get("fallback", "unknown")


def _instantiate_prompt(prompt_template: str, variables: dict[str, str]) -> str:
    """Fill template variables in prompt."""
    result = prompt_template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", value)
    result = result.replace("{run_date}", date_type.today().isoformat())
    # Warn on unreplaced template variables (skip JSON-like patterns with quotes)
    unreplaced = re.findall(r"(?<!\"){([a-z_]+)}(?!\")", result)
    if unreplaced:
        print(f"  WARNING: Unreplaced template variables: {unreplaced}")
    return result


def scan_creative() -> list[TaskDef]:
    """Scanner: Generate creative research tasks from templates."""
    templates = _load_creative_templates()
    if not templates:
        return []

    run_log = _load_creative_run_log()
    active_engine = _detect_active_engine()
    today = date_type.today().isoformat()
    tasks: list[TaskDef] = []
    gemini_count = 0

    for tmpl in templates:
        template_id = tmpl["template_id"]
        cooldown = tmpl.get("cooldown_days", 14)

        # Check cooldown
        log_key = creative_log_key(template_id, active_engine)
        last_run = run_log.get(log_key)
        if last_run and _days_since(last_run) < cooldown:
            continue

        # Gemini quota guard
        exec_mode = tmpl.get("execution_mode", "cli")
        if exec_mode == "gemini":
            if gemini_count >= GEMINI_MAX_PER_RUN:
                continue
            gemini_count += 1

        # Resolve variables
        var_defs = tmpl.get("variables", {})
        resolved = {k: _resolve_variable(v, active_engine) for k, v in var_defs.items()}
        resolved["run_date"] = today
        resolved["task_id"] = template_id.replace("/", "-") + "-" + active_engine

        # Instantiate prompt
        prompt = _instantiate_prompt(tmpl["prompt_template"], resolved)

        # Build task
        task_id = f"creative-{resolved['task_id']}"

        # Enforce tool restrictions based on safety level
        safety = tmpl.get("safety_level", "readonly")
        if safety == "readonly":
            tools = ["Read", "Glob", "Grep", "Bash"]
        else:
            tools = ["Read", "Glob", "Grep", "Bash", "Write", "Edit"]

        tasks.append(TaskDef(
            task_id=task_id,
            name=tmpl["name"].replace("{target}", active_engine),
            category="creative",
            prompt=prompt,
            safety_level=safety,
            execution_mode=exec_mode,
            model=tmpl.get("model", "opus"),
            max_budget_usd=tmpl.get("max_budget_usd", 5.0),
            timeout_minutes=tmpl.get("timeout_minutes", 30),
            max_turns=tmpl.get("max_turns", 50),
            priority=2,  # Between critical hardening (1) and nice-to-have (3)
            allowed_tools=tools,
        ))

    return tasks


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
        ("Knowledge Integrity", scan_knowledge_integrity),
        ("Recent Changes", scan_recent_changes),
        ("Test Health", scan_test_health),
        ("SPEC Quality", scan_spec_quality),
        ("Code Quality", scan_code_quality),
        ("Corpus Integrity", scan_corpus_integrity),
        ("Contract Boundaries", scan_contract_boundaries),
        ("Known Limitations", scan_known_limitations),
        ("Documentation", scan_documentation),
        ("Empirical Validations", scan_empirical_validations),
        ("Model Research", scan_model_research),
        ("Creative Research", scan_creative),
    ]

    for name, scanner_fn in scanners:
        try:
            found = scanner_fn()
            all_tasks.extend(found)
            if found:
                print(f"  {name}: {len(found)} tasks")
        except Exception as e:
            print(f"  {name}: FAILED ({e})")

    # Category enforcement — hardening + readonly research, no implementation
    ALLOWED_CATEGORIES = {"review", "test", "validation", "spec", "doc", "code_quality", "verification", "research", "creative"}
    rejected = [t for t in all_tasks if t.category not in ALLOWED_CATEGORIES]
    if rejected:
        for t in rejected:
            print(f"  REJECTED (category '{t.category}'): {t.task_id}")
        all_tasks = [t for t in all_tasks if t.category in ALLOWED_CATEGORIES]

    # Safety net: ensure all tasks have a non-zero budget cap
    for t in all_tasks:
        if t.max_budget_usd <= 0:
            print(f"  WARNING: {t.task_id} has max_budget_usd={t.max_budget_usd}, defaulting to 5.0")
            t.max_budget_usd = 5.0

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
