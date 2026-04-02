#!/usr/bin/env python3
"""Summarize questionnaire completion state for post-owner evaluation."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
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


def load_interactions(path: Path) -> list[Interaction]:
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    interactions: list[Interaction] = []
    for item in raw:
        interactions.append(
            Interaction(
                id=item["id"],
                title=item["title"],
                phase_label=item["phase_label"],
                availability=item.get("availability"),
            )
        )
    return interactions


def load_responses(path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if not path.exists():
        return {}, []
    responses: dict[str, dict[str, Any]] = {}
    duplicate_ids: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            entry = json.loads(stripped)
            interaction_id = entry.get("interaction_id")
            if not interaction_id:
                raise ValueError(
                    f"{path}: line {line_no} missing interaction_id"
                )
            if interaction_id in responses:
                duplicate_ids.append(str(interaction_id))
            responses[interaction_id] = entry
    return responses, sorted(set(duplicate_ids))


def answered(entry: dict[str, Any] | None) -> bool:
    if not entry:
        return False
    reaction = entry.get("immediate_reaction")
    return bool(isinstance(reaction, str) and reaction.strip())


def build_summary(
    interactions: list[Interaction],
    responses: dict[str, dict[str, Any]],
    duplicate_response_ids: list[str],
) -> dict[str, Any]:
    active = [item for item in interactions if item.availability != "blocked_pending_source"]
    blocked = [item for item in interactions if item.availability == "blocked_pending_source"]
    answered_active = [item for item in active if answered(responses.get(item.id))]
    unanswered_active = [item for item in active if not answered(responses.get(item.id))]
    orphan_responses = sorted(
        interaction_id for interaction_id in responses if interaction_id not in {item.id for item in interactions}
    )

    phase_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"answered": 0, "total": 0})
    for item in active:
        phase_counts[item.phase_label]["total"] += 1
        if answered(responses.get(item.id)):
            phase_counts[item.phase_label]["answered"] += 1

    confidence_counts = Counter()
    for item in answered_active:
        confidence = responses[item.id].get("confidence") or "unset"
        confidence_counts[str(confidence)] += 1

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "total_slots": len(interactions),
        "active_slots": len(active),
        "blocked_slots": len(blocked),
        "answered_active_slots": len(answered_active),
        "unanswered_active_slots": len(unanswered_active),
        "completion_pct": (
            round((len(answered_active) / len(active)) * 100, 1) if active else 0.0
        ),
        "blocked_ids": [item.id for item in blocked],
        "unanswered_ids": [item.id for item in unanswered_active],
        "orphan_response_ids": orphan_responses,
        "duplicate_response_ids": duplicate_response_ids,
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "phase_counts": dict(phase_counts),
        "supplemental_answers_included": False,
    }


def render_markdown(summary: dict[str, Any], interactions: list[Interaction]) -> str:
    interaction_map = {item.id: item for item in interactions}
    lines = [
        "# Owner Response Summary",
        "",
        f"- Generated: `{summary['generated_at']}`",
        f"- Total slots: `{summary['total_slots']}`",
        f"- Active slots: `{summary['active_slots']}`",
        f"- Blocked slots: `{summary['blocked_slots']}`",
        f"- Answered active slots: `{summary['answered_active_slots']}`",
        f"- Unanswered active slots: `{summary['unanswered_active_slots']}`",
        f"- Completion: `{summary['completion_pct']}%`",
        "- Supplemental answers included: `no` (track optional supplementals separately if the owner answered them outside the UI)",
        "",
        "## Phase Progress",
        "",
        "| Phase | Answered | Total |",
        "|---|---:|---:|",
    ]
    for phase_label, counts in summary["phase_counts"].items():
        lines.append(f"| {phase_label} | {counts['answered']} | {counts['total']} |")

    lines.extend(
        [
            "",
            "## Blocked Slots",
            "",
            ", ".join(f"`{item_id}`" for item_id in summary["blocked_ids"]) or "_None_",
            "",
            "## Unanswered Active Slots",
            "",
        ]
    )
    if summary["unanswered_ids"]:
        for item_id in summary["unanswered_ids"]:
            item = interaction_map[item_id]
            lines.append(f"- `{item.id}` — {item.title}")
    else:
        lines.append("_None_")

    lines.extend(
        [
            "",
            "## Confidence Counts",
            "",
        ]
    )
    if summary["confidence_counts"]:
        for confidence, count in summary["confidence_counts"].items():
            lines.append(f"- `{confidence}`: {count}")
    else:
        lines.append("_No answered responses yet_")

    lines.extend(
        [
            "",
            "## Orphan Response IDs",
            "",
        ]
    )
    if summary["orphan_response_ids"]:
        for item_id in summary["orphan_response_ids"]:
            lines.append(f"- `{item_id}`")
    else:
        lines.append("_None_")

    lines.extend(
        [
            "",
            "## Duplicate Response IDs",
            "",
        ]
    )
    if summary["duplicate_response_ids"]:
        for item_id in summary["duplicate_response_ids"]:
            lines.append(f"- `{item_id}` (latest entry currently wins)")
    else:
        lines.append("_None_")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--questionnaire-dir",
        type=Path,
        default=Path("integration_tests/questionnaire"),
        help="Directory containing interactions.json and questionnaire_responses.jsonl",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.md"),
        help="Markdown output path",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.json"),
        help="JSON output path",
    )
    args = parser.parse_args()

    questionnaire_dir = args.questionnaire_dir
    interactions = load_interactions(questionnaire_dir / "interactions.json")
    responses, duplicate_response_ids = load_responses(
        questionnaire_dir / "questionnaire_responses.jsonl"
    )
    summary = build_summary(interactions, responses, duplicate_response_ids)

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)

    args.output_md.write_text(render_markdown(summary, interactions), encoding="utf-8")
    args.output_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
