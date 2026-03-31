#!/usr/bin/env python3
"""Context drift detection — validates KR context document health.

Checks that paths, commands, and references in governance documents
(CLAUDE.md, MEMORY.md, NEXT.md, rules, skills, agents) still point
to real files and are internally consistent.

Inspired by mex's drift detection concept, but built natively for KR's
domain-specific architecture (engines, SPECs, Arabic skills, memory system).

Usage:
    python scripts/context_drift_check.py           # full check with score
    python scripts/context_drift_check.py --json     # machine-readable output
    python scripts/context_drift_check.py --quiet    # score only (for hooks)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Severity + Issue model
# ---------------------------------------------------------------------------

class Severity:
    CRITICAL = "CRITICAL"  # -5 points — broken governance docs
    HIGH = "HIGH"          # -3 points — desync between index and files
    MEDIUM = "MEDIUM"      # -2 points — stale or missing secondary refs
    LOW = "LOW"            # -1 point  — informational

SEVERITY_PENALTY = {
    Severity.CRITICAL: 5,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}


@dataclass
class Issue:
    checker: str
    severity: str
    message: str
    file: str = ""
    line: int = 0


@dataclass
class CheckResult:
    name: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.issues) == 0


# ---------------------------------------------------------------------------
# Path extraction helpers
# ---------------------------------------------------------------------------

# Matches backtick-quoted paths that look like file/dir references
_BACKTICK_PATH_RE = re.compile(
    r'`([a-zA-Z0-9_.][a-zA-Z0-9_./\-*<>{}]*\.[a-zA-Z]{1,10})`'
    r'|'
    r'`([a-zA-Z0-9_.][a-zA-Z0-9_./\-*<>{}]*/)`'
)

# Matches markdown links: [text](file.md)
_MD_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')

# Template placeholders that should not be resolved literally
_TEMPLATE_MARKERS = {"<n>", "<name>", "<engine>", "<file>", "<path>", "*"}

# Curly-brace template variables like {phase}, {model}, {book_id}
_CURLY_VAR_RE = re.compile(r'\{[a-zA-Z_]+\}')

# Placeholder patterns in filenames like PHASE_X_MANIFEST
_PLACEHOLDER_RE = re.compile(r'_X_')

# Known non-path backtick content (Python modules, class names, etc.)
_NON_PATH_STRINGS = {
    "pathlib.Path", "os.path", "model_validator", "text-overflow",
}


def _has_template_marker(path: str) -> bool:
    """Check if a path contains template placeholders."""
    if any(m in path for m in _TEMPLATE_MARKERS):
        return True
    if _CURLY_VAR_RE.search(path):
        return True
    if _PLACEHOLDER_RE.search(path):
        return True
    return False


def _is_likely_path(text: str) -> bool:
    """Heuristic: does this backtick string look like a file path?"""
    if text in _NON_PATH_STRINGS:
        return False
    if text.startswith("http") or text.startswith("$"):
        return False
    if " " in text and "/" not in text:
        return False
    # Must contain a slash or a dot-extension
    return "/" in text or re.search(r'\.\w{1,6}$', text) is not None


def extract_paths_from_md(filepath: Path) -> list[tuple[str, int]]:
    """Extract file/directory path references from a markdown file.

    Returns list of (path_string, line_number).
    Skips template paths and non-path backtick content.
    """
    paths: list[tuple[str, int]] = []
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    in_code_block = False
    for i, line in enumerate(lines, 1):
        # Track fenced code blocks — skip command examples
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Backtick-quoted paths
        for m in _BACKTICK_PATH_RE.finditer(line):
            path = m.group(1) or m.group(2)
            if path and _is_likely_path(path) and not _has_template_marker(path):
                paths.append((path, i))

    return paths


def extract_md_links(filepath: Path) -> list[tuple[str, str, int]]:
    """Extract markdown links from a file.

    Returns list of (link_text, link_target, line_number).
    """
    links: list[tuple[str, str, int]] = []
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    for i, line in enumerate(lines, 1):
        for m in _MD_LINK_RE.finditer(line):
            target = m.group(2)
            # Skip URLs
            if target.startswith("http") or target.startswith("#"):
                continue
            links.append((m.group(1), target, i))

    return links


# ---------------------------------------------------------------------------
# Individual checkers
# ---------------------------------------------------------------------------

def check_claude_md_paths(project_dir: Path) -> CheckResult:
    """Validate that paths referenced in CLAUDE.md exist."""
    result = CheckResult(name="CLAUDE.md path references")
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        result.issues.append(Issue(
            checker=result.name,
            severity=Severity.CRITICAL,
            message="CLAUDE.md not found at project root",
        ))
        return result

    paths = extract_paths_from_md(claude_md)
    for path_str, line_num in paths:
        resolved = project_dir / path_str
        if not resolved.exists():
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.CRITICAL,
                message=f"referenced path does not exist: {path_str}",
                file="CLAUDE.md",
                line=line_num,
            ))

    return result


def check_memory_index_sync(memory_dir: Path) -> CheckResult:
    """Validate MEMORY.md index is in sync with actual memory files."""
    result = CheckResult(name="MEMORY.md index sync")
    memory_md = memory_dir / "MEMORY.md"
    if not memory_md.exists():
        result.issues.append(Issue(
            checker=result.name,
            severity=Severity.HIGH,
            message="MEMORY.md not found in memory directory",
        ))
        return result

    # Extract links from MEMORY.md
    links = extract_md_links(memory_md)
    indexed_files = set()
    for _text, target, line_num in links:
        indexed_files.add(target)
        resolved = memory_dir / target
        if not resolved.exists():
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.HIGH,
                message=f"indexed memory file missing: {target}",
                file="MEMORY.md",
                line=line_num,
            ))

    # Check for orphan memory files (exist but not indexed)
    for md_file in sorted(memory_dir.glob("*.md")):
        if md_file.name == "MEMORY.md":
            continue
        if md_file.name not in indexed_files:
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.MEDIUM,
                message=f"orphan memory file (not in MEMORY.md index): {md_file.name}",
                file=md_file.name,
            ))

    return result


def check_engine_structure(project_dir: Path) -> CheckResult:
    """Validate that each engine directory has required files."""
    result = CheckResult(name="Engine directory structure")
    engines_dir = project_dir / "engines"
    if not engines_dir.exists():
        result.issues.append(Issue(
            checker=result.name,
            severity=Severity.CRITICAL,
            message="engines/ directory not found",
        ))
        return result

    for engine_dir in sorted(engines_dir.iterdir()):
        if not engine_dir.is_dir() or engine_dir.name.startswith("."):
            continue

        name = engine_dir.name

        # CLAUDE.md required
        if not (engine_dir / "CLAUDE.md").exists():
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.HIGH,
                message=f"engine '{name}' missing CLAUDE.md",
                file=f"engines/{name}/",
            ))

        # SPEC.md or SPEC_CORE.md expected
        has_spec = (
            (engine_dir / "SPEC.md").exists()
            or (engine_dir / "SPEC_CORE.md").exists()
        )
        if not has_spec:
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.MEDIUM,
                message=f"engine '{name}' has no SPEC.md or SPEC_CORE.md",
                file=f"engines/{name}/",
            ))

        # tests/ directory expected
        if not (engine_dir / "tests").exists():
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.MEDIUM,
                message=f"engine '{name}' has no tests/ directory",
                file=f"engines/{name}/",
            ))

    return result


def check_rule_references(project_dir: Path) -> CheckResult:
    """Validate that paths referenced in .claude/rules/*.md exist."""
    result = CheckResult(name="Rule file references")
    rules_dir = project_dir / ".claude" / "rules"
    if not rules_dir.exists():
        return result

    for rule_file in sorted(rules_dir.glob("*.md")):
        paths = extract_paths_from_md(rule_file)
        for path_str, line_num in paths:
            # Skip bare filenames — rules reference patterns like
            # "contracts.py" or "SPEC.md" generically, not as root-relative paths
            if "/" not in path_str:
                continue
            resolved = project_dir / path_str
            if not resolved.exists():
                result.issues.append(Issue(
                    checker=result.name,
                    severity=Severity.MEDIUM,
                    message=f"broken path reference: {path_str}",
                    file=f".claude/rules/{rule_file.name}",
                    line=line_num,
                ))

    return result


def check_skill_integrity(project_dir: Path) -> CheckResult:
    """Validate that each skill directory has a SKILL.md."""
    result = CheckResult(name="Skill file integrity")
    skills_dir = project_dir / ".claude" / "skills"
    if not skills_dir.exists():
        return result

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        if not (skill_dir / "SKILL.md").exists():
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.MEDIUM,
                message=f"skill '{skill_dir.name}' missing SKILL.md",
                file=f".claude/skills/{skill_dir.name}/",
            ))

    return result


def check_agent_definitions(project_dir: Path) -> CheckResult:
    """Validate agent definition files are well-formed."""
    result = CheckResult(name="Agent definitions")
    agents_dir = project_dir / ".claude" / "agents"
    if not agents_dir.exists():
        return result

    for agent_file in sorted(agents_dir.glob("*.md")):
        if agent_file.name == "archived":
            continue
        try:
            content = agent_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # Check for required frontmatter fields
        if not content.startswith("---"):
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.LOW,
                message=f"agent '{agent_file.stem}' missing YAML frontmatter",
                file=f".claude/agents/{agent_file.name}",
            ))

    return result


def check_next_md(project_dir: Path) -> CheckResult:
    """Validate NEXT.md references and freshness."""
    result = CheckResult(name="NEXT.md references")
    next_md = project_dir / "NEXT.md"
    if not next_md.exists():
        result.issues.append(Issue(
            checker=result.name,
            severity=Severity.HIGH,
            message="NEXT.md not found — no session handoff instructions",
        ))
        return result

    # Check paths referenced in NEXT.md (only directory-qualified paths)
    paths = extract_paths_from_md(next_md)
    for path_str, line_num in paths:
        # Skip bare filenames — NEXT.md mentions scripts by name in prose
        if "/" not in path_str:
            continue
        resolved = project_dir / path_str
        if not resolved.exists():
            result.issues.append(Issue(
                checker=result.name,
                severity=Severity.MEDIUM,
                message=f"NEXT.md references missing file: {path_str}",
                file="NEXT.md",
                line=line_num,
            ))

    # Check staleness via git log
    try:
        git_result = subprocess.run(
            ["git", "log", "-1", "--format=%H %ar", "--", "NEXT.md"],
            capture_output=True, text=True, cwd=project_dir, timeout=10,
        )
        if git_result.returncode == 0 and git_result.stdout.strip():
            relative_time = git_result.stdout.strip().split(" ", 1)[1]
            # Flag if NEXT.md hasn't been updated in many commits
            commits_since = subprocess.run(
                ["git", "rev-list", "--count", "HEAD", "--not",
                 "HEAD~50", "--", "NEXT.md"],
                capture_output=True, text=True, cwd=project_dir, timeout=10,
            )
            # If NEXT.md was last touched more than 30 commits ago
            log_count = subprocess.run(
                ["git", "log", "--oneline", "--", "NEXT.md"],
                capture_output=True, text=True, cwd=project_dir, timeout=10,
            )
            total_next_commits = len(
                log_count.stdout.strip().splitlines()
            ) if log_count.returncode == 0 else 0

            head_count = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True, text=True, cwd=project_dir, timeout=10,
            )
            total_commits = int(
                head_count.stdout.strip()
            ) if head_count.returncode == 0 else 0

            if total_commits > 0 and total_next_commits > 0:
                # Get the commit hash of last NEXT.md change
                last_next_hash = git_result.stdout.strip().split()[0]
                distance = subprocess.run(
                    ["git", "rev-list", "--count",
                     f"{last_next_hash}..HEAD"],
                    capture_output=True, text=True,
                    cwd=project_dir, timeout=10,
                )
                if distance.returncode == 0:
                    commits_behind = int(distance.stdout.strip())
                    if commits_behind > 30:
                        result.issues.append(Issue(
                            checker=result.name,
                            severity=Severity.LOW,
                            message=(
                                f"NEXT.md is {commits_behind} commits stale "
                                f"(last updated {relative_time})"
                            ),
                            file="NEXT.md",
                        ))
    except (subprocess.TimeoutExpired, ValueError, OSError):
        pass  # git not available or parse error — skip staleness check

    return result


def check_script_references(project_dir: Path) -> CheckResult:
    """Validate that scripts referenced in CLAUDE.md exist."""
    result = CheckResult(name="Script references")
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        return result

    try:
        content = claude_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return result

    # Extract script paths from code blocks
    in_code_block = False
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            continue

        # Match python/python3 script invocations
        m = re.match(
            r'(?:python3?|PYTHONIOENCODING=\S+\s+python)\s+'
            r'(?:-m\s+)?(\S+)',
            stripped,
        )
        if m:
            script_ref = m.group(1)
            # Skip module invocations like "pytest"
            if "/" in script_ref or script_ref.endswith(".py"):
                resolved = project_dir / script_ref
                if not resolved.exists():
                    result.issues.append(Issue(
                        checker=result.name,
                        severity=Severity.HIGH,
                        message=f"referenced script missing: {script_ref}",
                        file="CLAUDE.md",
                        line=i,
                    ))

    return result


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_score(all_issues: list[Issue]) -> int:
    """Compute health score from 0-100 based on issue severity."""
    score = 100
    for issue in all_issues:
        score -= SEVERITY_PENALTY.get(issue.severity, 1)
    return max(0, score)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_results(
    results: list[CheckResult],
    all_issues: list[Issue],
    score: int,
    quiet: bool = False,
) -> None:
    """Print human-readable results."""
    if quiet:
        print(f"context-health: {score}/100")
        return

    print("=" * 62)
    print("  CONTEXT DRIFT CHECK")
    print("=" * 62)

    for r in results:
        if r.passed:
            print(f"  [OK] {r.name}")
        else:
            crit = sum(1 for i in r.issues if i.severity == Severity.CRITICAL)
            high = sum(1 for i in r.issues if i.severity == Severity.HIGH)
            med = sum(1 for i in r.issues if i.severity == Severity.MEDIUM)
            low = sum(1 for i in r.issues if i.severity == Severity.LOW)
            parts = []
            if crit:
                parts.append(f"{crit} critical")
            if high:
                parts.append(f"{high} high")
            if med:
                parts.append(f"{med} medium")
            if low:
                parts.append(f"{low} low")
            print(f"  [!!] {r.name} ({', '.join(parts)})")
            for issue in r.issues:
                loc = ""
                if issue.file and issue.line:
                    loc = f" [{issue.file}:{issue.line}]"
                elif issue.file:
                    loc = f" [{issue.file}]"
                print(f"    {issue.severity}: {issue.message}{loc}")

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print(f"\n{'=' * 62}")
    print(f"  Score: {score}/100  ({passed} passed, {failed} failed)")

    if score == 100:
        print("  All context documents are consistent and healthy.")
    elif score >= 80:
        print("  Minor drift detected -- context is mostly healthy.")
    elif score >= 50:
        print("  Significant drift -- review and fix before next session.")
    else:
        print("  Severe drift -- context documents are unreliable.")
    print("=" * 62)


def json_output(
    results: list[CheckResult],
    all_issues: list[Issue],
    score: int,
) -> None:
    """Print machine-readable JSON output."""
    data = {
        "score": score,
        "total_issues": len(all_issues),
        "by_severity": {
            Severity.CRITICAL: sum(
                1 for i in all_issues if i.severity == Severity.CRITICAL
            ),
            Severity.HIGH: sum(
                1 for i in all_issues if i.severity == Severity.HIGH
            ),
            Severity.MEDIUM: sum(
                1 for i in all_issues if i.severity == Severity.MEDIUM
            ),
            Severity.LOW: sum(
                1 for i in all_issues if i.severity == Severity.LOW
            ),
        },
        "checks": [
            {
                "name": r.name,
                "passed": r.passed,
                "issues": [
                    {
                        "severity": i.severity,
                        "message": i.message,
                        "file": i.file,
                        "line": i.line,
                    }
                    for i in r.issues
                ],
            }
            for r in results
        ],
    }
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="KR context drift detection — validate governance doc health",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="output machine-readable JSON",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="output score only (for hooks)",
    )
    parser.add_argument(
        "--project-dir", type=Path, default=Path.cwd(),
        help="project root (default: cwd)",
    )
    parser.add_argument(
        "--memory-dir", type=Path, default=None,
        help="memory directory (default: auto-detect from Claude projects)",
    )
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()

    # Auto-detect memory directory
    memory_dir = args.memory_dir
    if memory_dir is None:
        home = Path.home()
        # Claude Code memory path convention
        project_slug = str(project_dir).replace("\\", "-").replace("/", "-").replace(":", "-")
        # Try common slug patterns
        for candidate_slug in [
            project_slug,
            project_slug.lstrip("-"),
            # Windows: C--Users-Name-path
            f"C--{str(project_dir)[3:].replace(chr(92), '-').replace('/', '-')}",
        ]:
            candidate = home / ".claude" / "projects" / candidate_slug / "memory"
            if candidate.exists():
                memory_dir = candidate
                break

    # Run all checks
    results: list[CheckResult] = [
        check_claude_md_paths(project_dir),
        check_script_references(project_dir),
        check_engine_structure(project_dir),
        check_rule_references(project_dir),
        check_skill_integrity(project_dir),
        check_agent_definitions(project_dir),
        check_next_md(project_dir),
    ]

    if memory_dir and memory_dir.exists():
        results.append(check_memory_index_sync(memory_dir))
    elif not args.quiet:
        results.append(CheckResult(
            name="MEMORY.md index sync",
            issues=[Issue(
                checker="MEMORY.md index sync",
                severity=Severity.LOW,
                message="memory directory not found — skipping index sync check",
            )],
        ))

    # Collect all issues and compute score
    all_issues: list[Issue] = []
    for r in results:
        all_issues.extend(r.issues)

    score = compute_score(all_issues)

    # Output
    if args.json:
        json_output(results, all_issues, score)
    else:
        print_results(results, all_issues, score, quiet=args.quiet)

    # Exit code: 0 if score >= 50, 1 if severe drift
    return 0 if score >= 50 else 1


if __name__ == "__main__":
    sys.exit(main())
