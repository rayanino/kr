"""Auto-update build metrics in an engine's CLAUDE.md.

Counts implementation lines, test lines, test count, and ADV coverage,
then updates the build metrics line in CLAUDE.md in-place.

Usage:
    python scripts/update_build_metrics.py <engine_name>
    python scripts/update_build_metrics.py normalization
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def count_lines(directory: Path) -> int:
    """Count total lines in .py files under directory."""
    total = 0
    for py_file in directory.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            total += len(
                py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except OSError:
            pass
    return total


def count_tests(test_dir: Path, project_dir: Path) -> int:
    """Count collected tests using pytest --co."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", str(test_dir), "--co", "-q"],
            capture_output=True, text=True, cwd=project_dir, timeout=30,
        )
        if result.returncode == 0:
            match = re.search(r"([0-9]+) tests?\s", result.stdout)
            if match:
                return int(match.group(1))
            # Fallback: count :: lines
            return sum(
                1 for l in result.stdout.splitlines()
                if "::" in l and not l.startswith("=")
            )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return 0


def count_adv_coverage(test_dir: Path) -> tuple[int, int]:
    """Count ADV-NNN references in test files. Returns (covered, max_id)."""
    adv_ids: set[str] = set()
    for py_file in test_dir.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            adv_ids.update(re.findall(r"ADV-([0-9]{3})", source))
        except OSError:
            pass
    if adv_ids:
        return len(adv_ids), max(int(a) for a in adv_ids)
    return 0, 0


def count_known_limitations(engine_dir: Path) -> int:
    """Count L-NNN entries in KNOWN_LIMITATIONS.md."""
    kl = engine_dir / "KNOWN_LIMITATIONS.md"
    if not kl.exists():
        return 0
    try:
        text = kl.read_text(encoding="utf-8", errors="ignore")
        return len(set(re.findall(r"L-[0-9]{3}", text)))
    except OSError:
        return 0


def update_claude_md(
    claude_md: Path,
    impl_lines: int,
    test_lines: int,
    test_count: int,
    adv_covered: int,
    adv_total: int,
    limitation_count: int,
) -> bool:
    """Update build metrics line in CLAUDE.md. Returns True if updated."""
    try:
        content = claude_md.read_text(encoding="utf-8")
    except OSError:
        return False

    new_metrics = (
        f"**Build metrics:** {impl_lines:,} impl lines, {test_lines:,} test lines, "
        f"{test_count} tests passing, {adv_covered}/{adv_total} ADV covered"
    )
    if limitation_count:
        new_metrics += f", {limitation_count} known limitations"
    new_metrics += "."

    # Match existing build metrics line (various phrasings)
    pattern = r"\*\*Build metrics.*?\*\*:?.*"
    updated, count = re.subn(pattern, new_metrics, content, count=1)
    if count == 0:
        print(f"  No build metrics line found in {claude_md}")
        return False

    claude_md.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: update_build_metrics.py <engine_name>")
        return 1

    engine_name = sys.argv[1]
    project_dir = Path.cwd()
    engine_dir = project_dir / "engines" / engine_name

    if not engine_dir.exists():
        print(f"Engine not found: {engine_dir}", file=sys.stderr)
        return 1

    src_dir = engine_dir / "src"
    test_dir = engine_dir / "tests"
    claude_md = engine_dir / "CLAUDE.md"

    impl_lines = count_lines(src_dir) if src_dir.exists() else 0
    test_lines = count_lines(test_dir) if test_dir.exists() else 0
    test_count = count_tests(test_dir, project_dir) if test_dir.exists() else 0
    adv_covered, adv_total = (
        count_adv_coverage(test_dir) if test_dir.exists() else (0, 0)
    )
    limitation_count = count_known_limitations(engine_dir)

    print(f"Build metrics for {engine_name}:")
    print(f"  Impl lines:    {impl_lines:,}")
    print(f"  Test lines:    {test_lines:,}")
    print(f"  Tests:         {test_count}")
    print(f"  ADV coverage:  {adv_covered}/{adv_total}")
    print(f"  Limitations:   {limitation_count}")

    if claude_md.exists():
        if update_claude_md(
            claude_md, impl_lines, test_lines, test_count,
            adv_covered, adv_total, limitation_count,
        ):
            print(f"\nUpdated {claude_md}")
        else:
            print(f"\nCould not update {claude_md}")
    else:
        print(f"\n{claude_md} not found -- metrics printed but not saved")

    return 0


if __name__ == "__main__":
    sys.exit(main())
