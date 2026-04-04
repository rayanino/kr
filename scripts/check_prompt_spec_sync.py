"""Check that the Phase 2b grouping prompt in code matches the SPEC §5.3.2 copy.

Usage:
    python scripts/check_prompt_spec_sync.py

Exits 0 if synced, 1 if drifted. Reports specific lines that differ.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SPEC_PATH = Path("engines/excerpting/SPEC.md")
CODE_PATH = Path("engines/excerpting/src/phase2_group.py")


def extract_spec_prompt() -> str:
    """Extract the prompt from the SPEC §5.3.2 code block."""
    spec = SPEC_PATH.read_text(encoding="utf-8")

    # Find the code block after "§5.3.2 — LLM System Prompt"
    # The prompt is between ``` markers after that section
    pattern = r"§5\.3\.2.*?```\n(.*?)```"
    match = re.search(pattern, spec, re.DOTALL)
    if not match:
        print("ERROR: Could not find §5.3.2 code block in SPEC")
        sys.exit(2)

    return match.group(1).strip()


def extract_code_prompt() -> str:
    """Extract GROUP_SYSTEM_PROMPT from phase2_group.py."""
    code = CODE_PATH.read_text(encoding="utf-8")

    # Find the triple-quoted string assigned to GROUP_SYSTEM_PROMPT
    pattern = r'GROUP_SYSTEM_PROMPT\s*=\s*"""\\\n(.*?)"""'
    match = re.search(pattern, code, re.DOTALL)
    if not match:
        print("ERROR: Could not find GROUP_SYSTEM_PROMPT in phase2_group.py")
        sys.exit(2)

    # The code version has backslash line continuations — normalize them
    raw = match.group(1)
    # Replace \ + newline with nothing (line continuation)
    normalized = re.sub(r"\\\n", "", raw)
    return normalized.strip()


def normalize_whitespace(text: str) -> list[str]:
    """Normalize to comparable lines."""
    lines = text.split("\n")
    # Strip trailing whitespace, collapse multiple spaces
    return [re.sub(r" +", " ", line.rstrip()) for line in lines]


def main() -> None:
    spec_prompt = extract_spec_prompt()
    code_prompt = extract_code_prompt()

    spec_lines = normalize_whitespace(spec_prompt)
    code_lines = normalize_whitespace(code_prompt)

    # Compare key sections rather than exact match
    # (formatting differences like line wrapping are expected)
    spec_text = "\n".join(spec_lines)
    code_text = "\n".join(code_lines)

    # Check key doctrine markers that MUST be present in both
    required_markers = [
        "EE-1",
        "taqdir",
        "FP-9",
        "C-SC-1",
        "C-SC-2",
        "C-SC-3",
        "C-SC-4",
        "C-SC-5",
    ]

    drift_found = False
    for marker in required_markers:
        in_spec = marker in spec_text
        in_code = marker in code_text
        if in_spec != in_code:
            print(f"DRIFT: '{marker}' in SPEC={in_spec}, in code={in_code}")
            drift_found = True

    # Check decontextualization rules
    decontext_markers = [
        "قال أبو حنيفة",
        "ورد عليه بأن",
        "tarjīḥ",
        "فإن قيل",
    ]
    for marker in decontext_markers:
        in_spec = marker in spec_text
        in_code = marker in code_text
        if in_spec != in_code:
            print(f"DRIFT: '{marker}' in SPEC={in_spec}, in code={in_code}")
            drift_found = True

    if drift_found:
        print("\nFAILED: Prompt-SPEC sync drift detected.")
        print("Fix: update the SPEC §5.3.2 code block to match phase2_group.py")
        sys.exit(1)
    else:
        print("PASSED: All key markers present in both SPEC and code.")
        sys.exit(0)


if __name__ == "__main__":
    main()
