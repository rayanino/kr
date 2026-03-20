"""Check test text strings for unintended matches against source pattern matchers.

When writing tests for Arabic pattern matchers, test text may accidentally contain
patterns from OTHER matchers, causing cross-contamination in test results.

Usage:
    python scripts/check_test_text_contamination.py <test_file.py> <src_file.py>
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


def extract_arabic_strings(source: str) -> list[tuple[int, str]]:
    """Extract string literals containing Arabic text from a Python file."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    strings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any("\u0600" <= c <= "\u06FF" for c in node.value):
                strings.append((node.lineno, node.value))
    return strings


def extract_regex_patterns(source: str) -> list[tuple[int, str, str]]:
    """Extract compiled regex patterns from a source file."""
    patterns: list[tuple[int, str, str]] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        attr = ""
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
        if attr not in ("compile", "search", "match", "findall", "finditer"):
            continue
        if (
            node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            patterns.append((node.lineno, node.args[0].value, f"re.{attr}"))
    return patterns


def check_contamination(
    test_strings: list[tuple[int, str]],
    src_patterns: list[tuple[int, str, str]],
    test_file: str,
    src_file: str,
) -> list[str]:
    """Check if test strings match any source regex patterns."""
    issues: list[str] = []
    for t_line, t_str in test_strings:
        for s_line, s_pat, s_func in src_patterns:
            try:
                if re.search(s_pat, t_str):
                    short_text = (t_str[:60] + "...") if len(t_str) > 60 else t_str
                    short_pat = (s_pat[:60] + "...") if len(s_pat) > 60 else s_pat
                    issues.append(
                        f"  {test_file}:{t_line} test text matches "
                        f"pattern from {src_file}:{s_line}\n"
                        f"    Text: {short_text!r}\n"
                        f"    Pattern: {short_pat!r} ({s_func})"
                    )
            except re.error:
                continue
    return issues


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

    if len(sys.argv) < 3:
        print(
            "Usage: check_test_text_contamination.py <test_file.py> <src_file.py>"
        )
        return 1

    test_path = Path(sys.argv[1])
    src_path = Path(sys.argv[2])

    if not test_path.exists() or not src_path.exists():
        return 0

    test_source = test_path.read_text(encoding="utf-8", errors="ignore")
    src_source = src_path.read_text(encoding="utf-8", errors="ignore")

    test_strings = extract_arabic_strings(test_source)
    src_patterns = extract_regex_patterns(src_source)

    if not test_strings or not src_patterns:
        return 0

    issues = check_contamination(
        test_strings, src_patterns, str(test_path), str(src_path)
    )
    if issues:
        print(
            f"TEST TEXT CONTAMINATION -- {test_path.name} vs {src_path.name}"
        )
        for issue in issues:
            print(issue)
        print(f"\n{len(issues)} contamination(s) found.")
        print(
            "Use text that does NOT trigger these patterns, "
            "or mark with '# safe: intentional'"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
