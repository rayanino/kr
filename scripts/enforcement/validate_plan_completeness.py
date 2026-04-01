"""F4 enforcement: Validate NEXT.md plan completeness.

Checks that NEXT.md has required structural elements for every phase:
- Exit conditions for each phase
- Step ownership (who does what)
- Error/failure handling
- No undefined placeholders (TBD, TODO, ???)

Exit codes:
  0 = plan passes all checks
  1 = plan has gaps (advisory warnings)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def check_plan(content: str) -> list[str]:
    """Check NEXT.md content for completeness gaps. Returns list of warnings."""
    warnings: list[str] = []

    # Check 1: Undefined placeholders
    placeholders = re.findall(r'\b(TBD|TODO|FIXME|XXX|\?\?\?)\b', content, re.IGNORECASE)
    if placeholders:
        warnings.append(
            f"PLACEHOLDER: {len(placeholders)} undefined placeholder(s) found: "
            f"{', '.join(set(p.upper() for p in placeholders))}"
        )

    # Check 2: Phase sections should have exit conditions
    # Find phase headers (## Phase N or ### Phase N)
    phase_headers = re.findall(r'^#{2,3}\s+Phase\s+[0-9]+', content, re.MULTILINE)
    if phase_headers:
        # Check if exit condition language exists
        exit_patterns = [
            r'exit\s+condition', r'EXIT\s+CONDITION', r'exit\s+criteria',
            r'completion\s+criteria', r'done\s+when', r'complete\s+when',
        ]
        has_exit = any(re.search(p, content, re.IGNORECASE) for p in exit_patterns)
        if not has_exit:
            warnings.append(
                f"EXIT CONDITIONS: {len(phase_headers)} phase(s) found but no exit "
                f"condition language detected. Add explicit exit criteria per phase."
            )

    # Check 3: Checklist items (- [ ]) should exist for transition gates
    checklist_items = re.findall(r'- \[ \]', content)
    if not checklist_items and phase_headers:
        warnings.append(
            "CHECKLISTS: No transition checklists found (- [ ] items). "
            "Add checklists for phase transitions."
        )

    # Check 4: Error handling / failure modes
    error_patterns = [
        r'error', r'fail', r'fallback', r'recovery', r'rollback',
        r'if\s+.*\s+fails', r'when\s+.*\s+fails',
    ]
    has_error_handling = any(re.search(p, content, re.IGNORECASE) for p in error_patterns)
    if not has_error_handling and len(content) > 1000:
        warnings.append(
            "ERROR HANDLING: No error/failure handling language found in a plan "
            f"of {len(content)} characters. Add failure modes and recovery steps."
        )

    # Check 5: Ownership (who does what)
    ownership_patterns = [
        r'CC\s+(does|will|must|should)', r'owner\s+(does|will|must|reviews)',
        r'coworker', r'Codex', r'Gemini', r'dispatch',
    ]
    has_ownership = any(re.search(p, content, re.IGNORECASE) for p in ownership_patterns)
    if not has_ownership and len(content) > 1000:
        warnings.append(
            "OWNERSHIP: No ownership language found. Each step should specify "
            "who does it (CC, owner, coworker)."
        )

    # Check 6: Budget awareness (for plans with API calls)
    if re.search(r'API|LLM|model|run|smoke|campaign', content, re.IGNORECASE):
        budget_patterns = [r'EUR|€|\$|budget|cost', r'Budget']
        has_budget = any(re.search(p, content) for p in budget_patterns)
        if not has_budget:
            warnings.append(
                "BUDGET: Plan mentions API/LLM work but no budget estimate. "
                "Add cost estimates per phase."
            )

    return warnings


def main() -> int:
    next_path = Path.cwd() / "NEXT.md"
    if len(sys.argv) > 1:
        next_path = Path(sys.argv[1])

    if not next_path.exists():
        print(f"File not found: {next_path}", file=sys.stderr)
        return 1

    content = next_path.read_text(encoding="utf-8")
    warnings = check_plan(content)

    if not warnings:
        print(f"NEXT.md plan completeness: ALL CHECKS PASS")
        return 0

    print(f"NEXT.md plan completeness: {len(warnings)} gap(s) found:\n")
    for i, w in enumerate(warnings, 1):
        print(f"  {i}. {w}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
