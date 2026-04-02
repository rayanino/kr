#!/usr/bin/env python3
"""Build browser-DR upload bundles for the questionnaire lane."""

from __future__ import annotations

import argparse
from pathlib import Path


PROFILES: dict[str, list[str]] = {
    "gemini-core": [
        "integration_tests/questionnaire/OWNER_FEEDBACK_GUARDRAIL.md",
        "integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md",
        "integration_tests/questionnaire/START_HERE.md",
        "integration_tests/questionnaire/RESPONSE_FORMAT.md",
        "integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md",
        "integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md",
        "integration_tests/questionnaire/QUESTIONNAIRE_EXAMPLES.md",
        "integration_tests/questionnaire/SUPPLEMENTAL_OWNER_QUESTIONS.md",
        "integration_tests/questionnaire/interactions.json",
        "docs/codex/survey_completeness_audit_2026_04_02.md",
    ],
    "gemini-post": [
        "integration_tests/questionnaire/OWNER_FEEDBACK_GUARDRAIL.md",
        "integration_tests/questionnaire/OWNER_QUESTIONNAIRE.md",
        "integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md",
        "integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md",
        "integration_tests/questionnaire/SUPPLEMENTAL_OWNER_QUESTIONS.md",
        "integration_tests/questionnaire/SUPPLEMENTAL_TRANSLATION_GUIDE.md",
        "integration_tests/questionnaire/AFTER_COMPLETION_CHECKLIST.md",
        "integration_tests/questionnaire/evaluation_reports/README.md",
        "integration_tests/questionnaire/evaluation_reports/SYNTHESIS_TEMPLATE.md",
        "docs/codex/weekend_dr_prompts.md",
    ],
}


def write_readme(output_dir: Path, profile: str, files: list[str]) -> None:
    readme = output_dir / "README.md"
    lines = [
        f"# Questionnaire DR Bundle: {profile}",
        "",
        "Built from the current local checkout.",
        "",
        "Included files:",
        "",
    ]
    lines.extend(f"- `{path}`" for path in files)
    lines.append("")
    readme.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        required=True,
        help="Which bundle profile to build",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Destination directory for copied bundle files",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    files = PROFILES[args.profile]
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    for rel_path in files:
        source = repo_root / rel_path
        if not source.exists():
            raise FileNotFoundError(f"Missing bundle input: {source}")
        destination = output_dir / Path(rel_path).name
        destination.write_bytes(source.read_bytes())

    write_readme(output_dir, args.profile, files)
    print(f"Built {args.profile} bundle at {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
