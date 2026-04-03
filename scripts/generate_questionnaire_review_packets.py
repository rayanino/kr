#!/usr/bin/env python3
"""Generate post-questionnaire reviewer dispatch packets."""

from __future__ import annotations

import argparse
from pathlib import Path


REVIEWERS = {
    "codex_internal_consistency": {
        "title": "Codex Internal Consistency Packet",
        "access_mode": "local checkout",
        "goal": "find internal contradictions, vague answers, and low-confidence hotspots before deeper review",
    },
    "claude_code_spec_alignment": {
        "title": "Claude Code Spec Alignment Packet",
        "access_mode": "local checkout",
        "goal": "check which answers create SPEC conflicts, cross-engine implications, or implementation-heavy consequences",
    },
    "gemini_cli_accuracy": {
        "title": "Gemini CLI Scholarly Accuracy Packet",
        "access_mode": "local checkout",
        "goal": "challenge owner answers against Arabic scholarly text behavior without treating Gemini as final authority",
    },
    "chatgpt_dr_feasibility": {
        "title": "ChatGPT DR Feasibility Packet",
        "access_mode": "remote-only unless files are pasted/uploaded",
        "goal": "evaluate technical feasibility and cost implications of owner preferences",
    },
    "claude_dr_scholarly": {
        "title": "Claude DR Scholarly Soundness Packet",
        "access_mode": "remote-only unless files are pasted/uploaded",
        "goal": "evaluate whether the owner's principles produce a coherent scholarly library",
    },
    "gemini_dr_pedagogical": {
        "title": "Gemini DR Pedagogical Packet",
        "access_mode": "uploaded files",
        "goal": "evaluate pedagogical usefulness and workflow alignment of owner answers",
    },
}


def build_packet(name: str, meta: dict[str, str], output_dir: Path) -> None:
    body = f"""# {meta['title']}

- Reviewer lane: `{name}`
- Access mode: {meta['access_mode']}
- Goal: {meta['goal']}

## Fill This In Before Finalizing The Review

- Reviewer:
- Date:
- Review target:
- Known limitations:

## Use These Inputs

- `integration_tests/questionnaire/questionnaire_responses.jsonl`
- `integration_tests/questionnaire/external_questionnaire_responses.json`
- `integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.md`
- `integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.md`
- `integration_tests/questionnaire/OWNER_FEEDBACK_GUARDRAIL.md`
- `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md`
- `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md`
- `integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md`

## Required Stance

- owner answers are signal, not authority
- owner confidence is metadata, not proof
- scholarly invariants outrank preference
- if access is remote-only, do not pretend unpushed local files are visible

## Expected Output

Place the final report in:

- `integration_tests/questionnaire/evaluation_reports/`

Use a filename matching this lane, for example:

- `{name}_YYYY_MM_DD.md`

## Minimum Questions To Answer

1. What are the highest-risk answers in this response set?
2. Which answers are safe to translate, and which must be challenged?
3. Which answers are only local preference or only point to a deeper need?
4. Which follow-up questions are truly necessary, if any?

## Reminder

Do not translate owner answers directly into implementation.
"""
    (output_dir / f"{name}.md").write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("integration_tests/questionnaire/evaluation_reports/dispatch_packets"),
        help="Directory to write packet markdown files into",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, meta in REVIEWERS.items():
        build_packet(name, meta, output_dir)

    index = output_dir / "README.md"
    index.write_text(
        "# Questionnaire Review Dispatch Packets\n\n"
        "Generated helper packets for the post-questionnaire multi-reviewer phase.\n",
        encoding="utf-8",
    )
    print(f"Wrote dispatch packets to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
