"""Lightweight pre-review checks to run BEFORE dispatching the code-reviewer agent.

Catches common issues (Pydantic Field(None), re.DOTALL, SPEC ranges, logging)
that would otherwise consume reviewer time.

Usage:
    python scripts/pre_review_checks.py <file1.py> [file2.py ...] [--engine <name>]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def check_redotall(file_path: Path) -> list[str]:
    """Check for regex patterns with . quantifiers but no DOTALL."""
    issues: list[str] = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").split("\n")
    except OSError:
        return []

    for i, line in enumerate(lines, 1):
        code = line.split("#")[0]
        if "re.compile" in code and re.search(r"\.\{[0-9]|\.[\*\+]", code):
            context = "\n".join(lines[max(0, i - 2):min(len(lines), i + 2)])
            if "DOTALL" not in context and "# safe:" not in line:
                issues.append(
                    f"  {file_path}:{i}: regex with . quantifier may need "
                    f"re.DOTALL if text contains newlines"
                )
    return issues


def check_logging(file_path: Path) -> list[str]:
    """Check that files using error codes have a logger."""
    issues: list[str] = []
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    error_codes = set(re.findall(r"ErrorCode\.(\w+)", source))
    if not error_codes:
        return []

    has_logger = "logger" in source or "logging" in source
    if not has_logger:
        issues.append(
            f"  {file_path}: uses {len(error_codes)} error codes but no logger. "
            f"Add: logger = logging.getLogger(__name__)"
        )
    return issues


def check_debug_prints(file_path: Path) -> list[str]:
    """Check for print() statements in engine source files."""
    issues: list[str] = []
    # Only check source files, not tests or scripts
    path_str = str(file_path)
    if "tests/" in path_str or "scripts/" in path_str:
        return []

    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").split("\n")
    except OSError:
        return []

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#") or "# safe:" in line:
            continue
        if re.match(r"print\s*\(", stripped):
            issues.append(
                f"  {file_path}:{i}: print() statement found "
                f"-- use logging.getLogger(__name__) instead"
            )

    return issues


def check_confidence_values(file_path: Path) -> list[str]:
    """Flag unusual confidence values as potential SPEC violations."""
    issues: list[str] = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").split("\n")
    except OSError:
        return []

    for i, line in enumerate(lines, 1):
        code = line.split("#")[0]
        if "confidence" not in code.lower():
            continue
        for m in re.finditer(
            r"confidence\s*[=:]\s*([0-9]+\.[0-9]+)", code, re.IGNORECASE
        ):
            val = float(m.group(1))
            if val > 0.95:
                issues.append(
                    f"  {file_path}:{i}: confidence={val} is very high "
                    f"-- verify against SPEC range"
                )
            elif val < 0.10:
                issues.append(
                    f"  {file_path}:{i}: confidence={val} is very low "
                    f"-- verify against SPEC range"
                )
    return issues


def run_delegated_check(
    script: Path, args: list[str], timeout: int = 15,
) -> str | None:
    """Run a delegated check script and return output if issues found."""
    if not script.exists():
        return None
    try:
        result = subprocess.run(
            ["python", str(script)] + args,
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: pre_review_checks.py <file1.py> [file2.py ...] [--engine <name>]")
        return 1

    engine_name = None
    if "--engine" in sys.argv:
        idx = sys.argv.index("--engine")
        if idx + 1 < len(sys.argv):
            engine_name = sys.argv[idx + 1]

    files = [
        Path(f) for f in sys.argv[1:]
        if f.endswith(".py") and not f.startswith("--") and Path(f).exists()
    ]
    if not files:
        print("No valid Python files provided.")
        return 1

    project_dir = Path.cwd()
    all_issues: list[str] = []
    checks_run = 0

    print("=== Pre-Review Checks ===\n")

    for fp in files:
        for check_fn in (
            check_redotall,
            check_logging,
            check_confidence_values,
            check_debug_prints,
        ):
            issues = check_fn(fp)
            checks_run += 1
            all_issues.extend(issues)

    # Delegated: Pydantic Field(None) check
    pydantic_script = project_dir / "scripts" / "check_pydantic_fields.py"
    for fp in files:
        output = run_delegated_check(
            pydantic_script,
            [str(fp), "--project-dir", str(project_dir)],
        )
        if output:
            all_issues.append(output)
        checks_run += 1

    # Delegated: SPEC value validation (once per engine)
    if engine_name:
        spec_script = project_dir / "scripts" / "validate_spec_values.py"
        engine_dir = project_dir / "engines" / engine_name
        if engine_dir.exists():
            output = run_delegated_check(
                spec_script, [str(engine_dir)], timeout=30
            )
            if output:
                all_issues.append(output)
            checks_run += 1

    if all_issues:
        print(f"Found {len(all_issues)} issue(s) across {checks_run} checks:\n")
        for issue in all_issues:
            print(issue)
        print("\nFix these BEFORE dispatching the code-reviewer agent.")
        return 1

    print(f"All clear -- {checks_run} checks passed on {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
