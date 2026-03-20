"""Validate that code constants match SPEC-defined numeric ranges and thresholds.

Extracts numeric constraints from SPEC.md (confidence ranges, thresholds, ratios)
and checks corresponding source files for mismatches.

Usage:
    python scripts/validate_spec_values.py <engine_dir>
    python scripts/validate_spec_values.py engines/normalization/
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SpecConstraint:
    section: str
    description: str
    value_type: str  # range, threshold_lower, threshold_upper, level
    low: float | None
    high: float | None
    context: str
    line_number: int
    keywords: set[str] = field(default_factory=set)


@dataclass
class CodeValue:
    file: Path
    line_number: int
    value: float
    context: str
    keywords: set[str] = field(default_factory=set)


_STOP_WORDS = frozenset({
    "the", "and", "for", "with", "from", "this", "that", "are", "was",
    "not", "none", "true", "false", "def", "class", "self", "return",
    "import", "str", "int", "float", "list", "dict", "set", "tuple",
})


def _extract_keywords(text: str) -> set[str]:
    """Extract meaningful identifier-like words from text."""
    words = re.findall(r"[a-zA-Z_]{3,}", text.lower())
    return {w for w in words if w not in _STOP_WORDS}


def extract_spec_constraints(spec_path: Path) -> list[SpecConstraint]:
    """Parse SPEC.md for numeric constraints."""
    text = spec_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    constraints: list[SpecConstraint] = []
    current_section = ""

    for i, line in enumerate(lines, 1):
        sec = re.match(r"^#{1,4}\s+(.+)", line)
        if sec:
            current_section = sec.group(1).strip()

        kw = _extract_keywords(line)

        # Range: 0.60-0.80 or 0.60--0.80
        for m in re.finditer(r"([0-9]+\.[0-9]+)\s*[-\u2013]+\s*([0-9]+\.[0-9]+)", line):
            lo, hi = float(m.group(1)), float(m.group(2))
            constraints.append(SpecConstraint(
                section=current_section, description=f"Range {lo}-{hi}",
                value_type="range", low=lo, high=hi,
                context=line.strip(), line_number=i, keywords=kw,
            ))

        # Lower threshold: >= 0.90, > 0.50
        for m in re.finditer(r"[>\u2265]=?\s*([0-9]+\.[0-9]+)", line):
            val = float(m.group(1))
            constraints.append(SpecConstraint(
                section=current_section, description=f">= {val}",
                value_type="threshold_lower", low=val, high=None,
                context=line.strip(), line_number=i, keywords=kw,
            ))

        # Upper threshold: <= 0.30, < 0.60
        for m in re.finditer(r"[<\u2264]=?\s*([0-9]+\.[0-9]+)", line):
            val = float(m.group(1))
            constraints.append(SpecConstraint(
                section=current_section, description=f"<= {val}",
                value_type="threshold_upper", low=None, high=val,
                context=line.strip(), line_number=i, keywords=kw,
            ))

    return constraints


def find_code_values(src_dir: Path) -> list[CodeValue]:
    """Find confidence-like floating-point literals in source files."""
    values: list[CodeValue] = []
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            lines = py_file.read_text(encoding="utf-8", errors="ignore").split("\n")
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            code = line.split("#")[0]
            for m in re.finditer(r"\b([0-9]+\.[0-9]{2,})\b", code):
                val = float(m.group(1))
                if 0.0 < val < 1.0:
                    values.append(CodeValue(
                        file=py_file, line_number=i, value=val,
                        context=line.strip(), keywords=_extract_keywords(line),
                    ))
    return values


def check_violations(
    constraints: list[SpecConstraint], code_values: list[CodeValue],
) -> list[str]:
    """Check code values against SPEC range constraints using keyword overlap."""
    violations: list[str] = []

    range_constraints = [c for c in constraints if c.value_type == "range"]
    for constraint in range_constraints:
        if constraint.low is None or constraint.high is None:
            continue
        if not constraint.keywords:
            continue

        for cv in code_values:
            overlap = constraint.keywords & cv.keywords
            if len(overlap) < 2:
                continue
            if cv.value < constraint.low - 0.001 or cv.value > constraint.high + 0.001:
                violations.append(
                    f"MISMATCH: SPEC '{constraint.section}' L{constraint.line_number} "
                    f"says {constraint.low}-{constraint.high}, "
                    f"but {cv.file.name}:{cv.line_number} uses {cv.value}\n"
                    f"  SPEC: {constraint.context[:120]}\n"
                    f"  Code: {cv.context[:120]}"
                )

    return violations


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

    if len(sys.argv) < 2:
        print("Usage: validate_spec_values.py <engine_dir>")
        return 1

    engine_dir = Path(sys.argv[1])
    spec_path = engine_dir / "SPEC.md"
    src_dir = engine_dir / "src"

    if not spec_path.exists():
        print(f"SPEC not found: {spec_path}", file=sys.stderr)
        return 1
    if not src_dir.exists():
        print(f"Source dir not found: {src_dir}", file=sys.stderr)
        return 1

    constraints = extract_spec_constraints(spec_path)
    code_values = find_code_values(src_dir)
    violations = check_violations(constraints, code_values)

    if violations:
        print(f"SPEC VALUE VIOLATIONS -- {engine_dir}")
        for v in violations:
            print(f"\n  {v}")
        print(f"\n{len(violations)} violation(s) found.")
        return 1

    print(
        f"SPEC value check passed -- "
        f"{len(constraints)} constraints, {len(code_values)} code values checked."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
