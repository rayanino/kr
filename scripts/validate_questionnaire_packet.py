#!/usr/bin/env python3
"""Validate the owner questionnaire packet against current hardening rules."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONNAIRE_DIR = REPO_ROOT / "integration_tests" / "questionnaire"
DOCS_DIR = REPO_ROOT / "docs" / "codex"
TOOLS_DIR = REPO_ROOT / "tools"


@dataclass(frozen=True)
class CheckFailure:
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_interactions() -> tuple[list[dict], list[CheckFailure]]:
    failures: list[CheckFailure] = []
    path = QUESTIONNAIRE_DIR / "interactions.json"
    interactions = json.loads(read_text(path))
    ids = [item["id"] for item in interactions]
    if len(interactions) != 40:
        failures.append(CheckFailure(f"{path}: expected 40 interactions, found {len(interactions)}"))
    if len(ids) != len(set(ids)):
        failures.append(CheckFailure(f"{path}: duplicate interaction ids found"))

    blocked = [item["id"] for item in interactions if item.get("availability") == "blocked_pending_source"]
    if blocked != ["CJ-2", "CJ-3"]:
        failures.append(CheckFailure(f"{path}: expected blocked ids ['CJ-2', 'CJ-3'], found {blocked}"))

    id_map = {item["id"]: item for item in interactions}
    if id_map.get("F-8", {}).get("title") != "A Risk Preference Question":
        failures.append(CheckFailure(f"{path}: F-8 title drifted from hardened wording"))
    if "If grammar is not a science you actively study" not in (id_map.get("GN-2", {}).get("context_note") or ""):
        failures.append(CheckFailure(f"{path}: GN-2 context note lost novice-reader fallback"))
    return interactions, failures


def normalize_questionnaire_title(title: str) -> str:
    normalized = re.sub(r"\s+\[EDGE CASE\]$", "", title)
    normalized = re.sub(r"\s+\(Blocked For Now\)$", "", normalized)
    return normalized.strip()


def parse_owner_questionnaire_headings(path: Path) -> list[tuple[str, str]]:
    text = read_text(path)
    pattern = re.compile(r"^#{2,3}\s+([A-Z]+(?:-[0-9A-Za-z]+)?)\s+---\s+(.+)$", re.MULTILINE)
    return [(match.group(1), normalize_questionnaire_title(match.group(2))) for match in pattern.finditer(text)]


def assert_contains(text: str, path: Path, needle: str, failures: list[CheckFailure]) -> None:
    if needle not in text:
        failures.append(CheckFailure(f"{path}: missing required text: {needle!r}"))


def assert_not_contains(text: str, path: Path, pattern: str, failures: list[CheckFailure]) -> None:
    if re.search(pattern, text):
        failures.append(CheckFailure(f"{path}: forbidden pattern matched: {pattern!r}"))


def check_owner_facing_docs(active_count: int) -> list[CheckFailure]:
    failures: list[CheckFailure] = []
    start_here = QUESTIONNAIRE_DIR / "START_HERE.md"
    owner_q = QUESTIONNAIRE_DIR / "OWNER_QUESTIONNAIRE.md"
    response_format = QUESTIONNAIRE_DIR / "RESPONSE_FORMAT.md"

    start_text = read_text(start_here)
    owner_text = read_text(owner_q)
    response_text = read_text(response_format)
    owner_headings = parse_owner_questionnaire_headings(owner_q)

    assert_contains(start_text, start_here, "40 core questionnaire slots", failures)
    assert_contains(start_text, start_here, f"**{active_count} are answerable**", failures)
    assert_contains(start_text, start_here, "Use Works / Needs Work / Doesn't Work", failures)
    assert_contains(start_text, start_here, "Short Path If You Are Time-Limited", failures)
    assert_contains(start_text, start_here, "OWNER_FEEDBACK_GUARDRAIL.md", failures)
    assert_contains(start_text, start_here, "AFTER_COMPLETION_CHECKLIST.md", failures)

    assert_contains(owner_text, owner_q, "A Risk Preference Question", failures)
    assert_contains(owner_text, owner_q, "Blocked For Now", failures)
    assert_contains(owner_text, owner_q, "important starting input", failures)
    assert_contains(owner_text, owner_q, "OWNER_FEEDBACK_GUARDRAIL.md", failures)

    interaction_items = json.loads(read_text(QUESTIONNAIRE_DIR / "interactions.json"))
    interaction_pairs = [(item["id"], normalize_questionnaire_title(item["title"])) for item in interaction_items]
    if owner_headings != interaction_pairs:
        failures.append(
            CheckFailure(
                f"{owner_q}: interaction heading sequence/title sync drifted from interactions.json"
            )
        )

    assert_contains(response_text, response_format, "Works for me", failures)
    assert_contains(response_text, response_format, "Partly works", failures)
    assert_contains(response_text, response_format, "Doesn't work for me", failures)
    assert_contains(response_text, response_format, "your answer is evidence in the chain, not the whole chain", failures)

    forbidden_patterns = [
        r"directly shape how the library breaks books",
        r"shape how the pipeline works",
        r"nothing is invented without your input",
        r"become rules that govern how the library works",
        r"become SPEC rules",
        r"Accept as-is",
        r"\bReject\b",
    ]
    for pattern in forbidden_patterns:
        assert_not_contains(start_text, start_here, pattern, failures)
        assert_not_contains(owner_text, owner_q, pattern, failures)
        assert_not_contains(response_text, response_format, pattern, failures)

    return failures


def check_team_docs() -> list[CheckFailure]:
    failures: list[CheckFailure] = []
    translation = QUESTIONNAIRE_DIR / "TEAM_TRANSLATION_GUIDE.md"
    evaluation = QUESTIONNAIRE_DIR / "CRITICAL_EVALUATION_GUIDE.md"
    guardrail = QUESTIONNAIRE_DIR / "OWNER_FEEDBACK_GUARDRAIL.md"
    synthesis = QUESTIONNAIRE_DIR / "evaluation_reports" / "SYNTHESIS_TEMPLATE.md"
    eval_readme = QUESTIONNAIRE_DIR / "evaluation_reports" / "README.md"

    translation_text = read_text(translation)
    evaluation_text = read_text(evaluation)
    guardrail_text = read_text(guardrail)
    synthesis_text = read_text(synthesis)
    eval_readme_text = read_text(eval_readme)

    for needle in [
        "## Layer Triage",
        "Boundary",
        "Display",
        "Workflow",
        "consult `F-2` first",
        "consult `SUP-WF-1` when available",
    ]:
        assert_contains(translation_text, translation, needle, failures)

    for needle in [
        "stakeholder expectations are not validated requirements",
        "scholarly invariants outrank user preference",
        "owner confidence is metadata, not evidence",
        "OVERRIDDEN",
        "Owner clarification can refine interpretation, but it does not override invariants.",
    ]:
        assert_contains(evaluation_text, evaluation, needle, failures)

    for needle in [
        "stakeholder expectations, not validated requirements",
        "Accepted owner signal must become a **bounded rule**",
        "## Scholarly Invariants Outrank Preference",
        "## Evidence Beats Confidence",
        "## Separation Of Duties",
    ]:
        assert_contains(guardrail_text, guardrail, needle, failures)

    for needle in [
        "### LOCAL_PREFERENCE",
        "### DEEPER_NEED",
        "Resolution layer: boundary / display / workflow",
        "Did the rewritten need survive independent challenge: yes/no",
        "Owner confidence was treated as metadata, not proof.",
    ]:
        assert_contains(synthesis_text, synthesis, needle, failures)

    for needle in [
        "External Report Adjudication Rule",
        "remote-only repo review",
        "uploaded-file review",
        "the local commit(s) that implemented any accepted changes",
    ]:
        assert_contains(eval_readme_text, eval_readme, needle, failures)

    return failures


def check_runtime_surfaces() -> list[CheckFailure]:
    failures: list[CheckFailure] = []
    review_py = TOOLS_DIR / "review.py"
    viewer_html = TOOLS_DIR / "excerpt_viewer.html"
    review_text = read_text(review_py)
    viewer_text = read_text(viewer_html)

    for needle in [
        'availability") == "blocked_pending_source"',
        '"Interaction is blocked pending source material"',
    ]:
        assert_contains(review_text, review_py, needle, failures)

    for needle in [
        'qIsBlocked(item)',
        'Blocked Pending Source Material',
        "0 of 0 active",
        "Works",
        "Doesn't Work",
    ]:
        assert_contains(viewer_text, viewer_html, needle, failures)

    return failures


def main() -> int:
    interactions, failures = check_interactions()
    active_count = len([item for item in interactions if item.get("availability") != "blocked_pending_source"])
    failures.extend(check_owner_facing_docs(active_count))
    failures.extend(check_team_docs())
    failures.extend(check_runtime_surfaces())

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure.message}")
        return 1

    print("Questionnaire packet validation passed.")
    print(f"- total interactions: {len(interactions)}")
    print(f"- active interactions: {active_count}")
    print("- blocked interactions: CJ-2, CJ-3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
