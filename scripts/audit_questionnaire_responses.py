#!/usr/bin/env python3
"""Audit completed questionnaire responses before multi-coworker synthesis."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Interaction:
    id: str
    title: str
    phase_label: str
    availability: str | None
    multiple_choice: list[str] | None
    is_edge_case: bool


def load_interactions(path: Path) -> dict[str, Interaction]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        item["id"]: Interaction(
            id=item["id"],
            title=item["title"],
            phase_label=item["phase_label"],
            availability=item.get("availability"),
            multiple_choice=item.get("multiple_choice"),
            is_edge_case=bool(item.get("is_edge_case")),
        )
        for item in raw
    }


def load_responses(path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if not path.exists():
        return {}, []
    responses: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            interaction_id = payload.get("interaction_id")
            if not interaction_id:
                raise ValueError(f"{path}: line {line_no} missing interaction_id")
            if interaction_id in responses:
                duplicates.append(str(interaction_id))
            responses[interaction_id] = payload
    return responses, sorted(set(duplicates))


def load_external_responses(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw.get("responses", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise ValueError(f"{path}: expected a list or dict with 'responses'")
    responses: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(items, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: entry {index} is not an object")
        interaction_id = entry.get("interaction_id")
        if not interaction_id:
            raise ValueError(f"{path}: entry {index} missing interaction_id")
        responses[str(interaction_id)] = entry
    return responses


def parse_translation_dimensions(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    mappings: dict[str, dict[str, str]] = {}
    row_re = re.compile(
        r"^\|\s*([A-Z]+(?:-[0-9A-Za-z]+)?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$",
        re.MULTILINE,
    )
    for match in row_re.finditer(text):
        interaction_id = match.group(1)
        if interaction_id == "Interaction":
            continue
        mappings[interaction_id] = {
            "dimension": match.group(2),
            "maps_to": match.group(3),
            "spec_section": match.group(4),
            "prompt_parameter": match.group(5),
            "current_default": match.group(6),
            "dr_decision": match.group(7),
        }
    return mappings


def is_answered(entry: dict[str, Any] | None) -> bool:
    if not entry:
        return False
    if entry.get("source_mode") == "external_bundle" and entry.get("answered_external") is True:
        return True
    value = entry.get("immediate_reaction")
    return bool(isinstance(value, str) and value.strip())


def find_keyword_sentiment_mismatches(
    interactions: dict[str, Interaction], responses: dict[str, dict[str, Any]]
) -> list[dict[str, str]]:
    negative_words = ("missing", "unclear", "confusing", "incomplete", "fragment", "wrong", "bad")
    mismatches: list[dict[str, str]] = []
    for interaction_id, response in responses.items():
        choice = response.get("mc_choice")
        reaction = (response.get("immediate_reaction") or "").lower()
        if not isinstance(choice, str) or not reaction:
            continue
        if choice.startswith("A:") and any(word in reaction for word in negative_words):
            mismatches.append(
                {
                    "interaction_id": interaction_id,
                    "mc_choice": choice,
                    "reason": "positive multiple-choice paired with negative reaction language",
                }
            )
    return mismatches


def build_audit(
    interactions: dict[str, Interaction],
    responses: dict[str, dict[str, Any]],
    duplicates: list[str],
    translation_map: dict[str, dict[str, str]],
) -> dict[str, Any]:
    active_ids = [iid for iid, item in interactions.items() if item.availability != "blocked_pending_source"]
    blocked_ids = [iid for iid, item in interactions.items() if item.availability == "blocked_pending_source"]
    answered_ids = [iid for iid in active_ids if is_answered(responses.get(iid))]
    missing_ids = [iid for iid in active_ids if not is_answered(responses.get(iid))]
    orphan_ids = sorted(iid for iid in responses if iid not in interactions)
    blocked_answer_ids = sorted(iid for iid in blocked_ids if iid in responses)

    missing_choices: list[str] = []
    short_reactions: list[dict[str, Any]] = []
    missing_edge_fields: list[str] = []
    low_confidence_ids: list[str] = []
    dimension_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"answered": 0, "total": 0})
    low_confidence_dimensions: dict[str, list[str]] = defaultdict(list)
    external_response_ids: list[str] = []

    for iid in active_ids:
        item = interactions[iid]
        mapping = translation_map.get(iid)
        if mapping:
            dimension_counts[mapping["dimension"]]["total"] += 1

        response = responses.get(iid)
        if not is_answered(response):
            continue
        assert response is not None
        if response.get("source_mode") == "external_bundle":
            external_response_ids.append(iid)

        if mapping:
            dimension_counts[mapping["dimension"]]["answered"] += 1

        if item.multiple_choice and not response.get("mc_choice") and response.get("source_mode") != "external_bundle":
            missing_choices.append(iid)

        reaction = str(response.get("immediate_reaction", "")).strip()
        if len(reaction) < 10 and response.get("source_mode") != "external_bundle":
            short_reactions.append({"interaction_id": iid, "length": len(reaction)})

        if item.is_edge_case:
            if not (response.get("what_would_change_mind") or response.get("principles_revealed")):
                missing_edge_fields.append(iid)

        confidence = (response.get("confidence") or "").lower()
        if confidence in {"", "low"} and not (
            response.get("source_mode") == "external_bundle" and confidence == ""
        ):
            low_confidence_ids.append(iid)
            if mapping:
                low_confidence_dimensions[mapping["dimension"]].append(iid)

    missing_dimensions = sorted(
        dimension for dimension, counts in dimension_counts.items() if counts["answered"] == 0
    )
    translation_unmapped_response_ids = sorted(iid for iid in answered_ids if iid not in translation_map)
    translation_missing_interaction_ids = sorted(iid for iid in interactions if iid not in translation_map)

    readiness_score = 0.0
    if active_ids:
        readiness_score = round(len(answered_ids) / len(active_ids), 3)

    return {
        "audit_summary": {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_interactions": len(interactions),
            "active_interactions": len(active_ids),
            "blocked_interactions": len(blocked_ids),
            "answered_active_interactions": len(answered_ids),
            "readiness_score": readiness_score,
        },
        "structural_alerts": {
            "missing": missing_ids,
            "orphans": orphan_ids,
            "duplicates": duplicates,
            "blocked_answer_ids": blocked_answer_ids,
        },
        "content_alerts": {
            "missing_choices": missing_choices,
            "short_reactions": short_reactions,
            "missing_edge_fields": missing_edge_fields,
            "low_confidence_ids": low_confidence_ids,
            "keyword_sentiment_mismatches": find_keyword_sentiment_mismatches(interactions, responses),
        },
        "dimension_audit": {
            "missing_coverage": missing_dimensions,
            "low_confidence_dimensions": dict(low_confidence_dimensions),
            "dimension_counts": dict(dimension_counts),
        },
        "translation_readiness": {
            "unmapped_response_ids": translation_unmapped_response_ids,
            "unmapped_interaction_ids": translation_missing_interaction_ids,
        },
        "external_response_ids": sorted(external_response_ids),
    }


def render_markdown(audit: dict[str, Any]) -> str:
    summary = audit["audit_summary"]
    lines = [
        "# Questionnaire Response Audit",
        "",
        f"- Generated: `{summary['timestamp']}`",
        f"- Total interactions: `{summary['total_interactions']}`",
        f"- Active interactions: `{summary['active_interactions']}`",
        f"- Answered active interactions: `{summary['answered_active_interactions']}`",
        f"- Readiness score: `{summary['readiness_score']}`",
        "",
        "## Structural Alerts",
        "",
    ]
    for key, items in audit["structural_alerts"].items():
        lines.append(f"### {key}")
        if items:
            if isinstance(items, list):
                for item in items:
                    lines.append(f"- `{item}`")
        else:
            lines.append("_None_")
        lines.append("")

    lines.append("## Content Alerts")
    lines.append("")
    for key, items in audit["content_alerts"].items():
        lines.append(f"### {key}")
        if items:
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        lines.append(f"- `{item.get('interaction_id', '?')}` — {json.dumps(item, ensure_ascii=False)}")
                    else:
                        lines.append(f"- `{item}`")
        else:
            lines.append("_None_")
        lines.append("")

    lines.append("## Dimension Audit")
    lines.append("")
    lines.append(f"- Missing coverage: {', '.join(f'`{x}`' for x in audit['dimension_audit']['missing_coverage']) or '_None_'}")
    lines.append("")
    lines.append("### Low Confidence Dimensions")
    low_dims = audit["dimension_audit"]["low_confidence_dimensions"]
    if low_dims:
        for dimension, ids in low_dims.items():
            lines.append(f"- `{dimension}`: {', '.join(f'`{x}`' for x in ids)}")
    else:
        lines.append("_None_")
    lines.append("")

    lines.append("## External Responses")
    lines.append("")
    if audit["external_response_ids"]:
        for iid in audit["external_response_ids"]:
            lines.append(f"- `{iid}`")
    else:
        lines.append("_None_")
    lines.append("")

    lines.append("## Translation Readiness")
    lines.append("")
    for key, items in audit["translation_readiness"].items():
        lines.append(f"### {key}")
        if items:
            for item in items:
                lines.append(f"- `{item}`")
        else:
            lines.append("_None_")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--questionnaire-dir",
        type=Path,
        default=Path("integration_tests/questionnaire"),
        help="Questionnaire directory",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.md"),
        help="Markdown output path",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.json"),
        help="JSON output path",
    )
    args = parser.parse_args()

    interactions = load_interactions(args.questionnaire_dir / "interactions.json")
    responses_jsonl, duplicates = load_responses(args.questionnaire_dir / "questionnaire_responses.jsonl")
    external_responses = load_external_responses(
        args.questionnaire_dir / "external_questionnaire_responses.json"
    )
    responses = {**external_responses, **responses_jsonl}
    translation_map = parse_translation_dimensions(args.questionnaire_dir / "TEAM_TRANSLATION_GUIDE.md")
    audit = build_audit(interactions, responses, duplicates, translation_map)

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(audit), encoding="utf-8")
    args.output_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
