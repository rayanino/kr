from __future__ import annotations

import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import cast

from spec_common import LoadedAtom, load_atoms, relative_spec_path, spec_root

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stdout,
    )


def as_mapping(value: object) -> dict[str, object]:
    return cast(dict[str, object], value) if isinstance(value, dict) else {}


def as_string(value: object) -> str:
    return value if isinstance(value, str) else ""


def as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def as_mapping_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [cast(dict[str, object], item) for item in value if isinstance(item, dict)]


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    divider = ["---"] * len(headers)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(divider) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def summarize_atom(atom: LoadedAtom) -> list[str]:
    data = atom.data
    lines = [
        f"### {atom.atom_id} — {as_string(data.get('title'))}",
        f"- Type: {as_string(data.get('type'))}",
        f"- Layer: {as_string(data.get('layer'))}",
        f"- Step: {as_string(data.get('step')) or 'n/a'}",
        f"- Status: {as_string(data.get('status'))}",
        f"- Priority: {as_string(data.get('priority'))}",
        f"- Confidence: {as_string(data.get('confidence'))}",
        f"- Source: {as_string(data.get('source'))}",
    ]

    atom_type = as_string(data.get("type"))
    if atom_type == "requirement":
        behavior = as_mapping(data.get("behavior"))
        lines.append(f"- Trigger: {as_string(behavior.get('trigger'))}")
        lines.append("- Postconditions:")
        lines.extend(f"  - {item}" for item in as_string_list(behavior.get("postconditions")))
        lines.append("- Acceptance criteria:")
        lines.extend(format_acceptance_criteria(data))
    elif atom_type == "decision":
        lines.extend(format_decision(atom))
    elif atom_type in {"invariant", "constraint"}:
        rule = as_mapping(data.get("rule"))
        lines.append(f"- Rule: {as_string(rule.get('statement'))}")
    elif atom_type == "feedback":
        lines.append(f"- Interview question: {as_string(data.get('question'))}")
        lines.append(f"- Owner answer: {as_string(data.get('answer'))}")
    elif atom_type == "question":
        lines.append("- Candidates:")
        for candidate in as_mapping_list(data.get("candidates")):
            lines.append(
                "  - "
                f"{as_string(candidate.get('id'))}: "
                f"{as_string(candidate.get('label'))} "
                f"({as_string(candidate.get('likelihood'))})"
            )
    return lines


def format_acceptance_criteria(data: dict[str, object]) -> list[str]:
    lines: list[str] = []
    for criterion in as_mapping_list(data.get("acceptance_criteria")):
        lines.append(
            "  - "
            f"{as_string(criterion.get('id'))} "
            f"[{as_string(criterion.get('test_type'))}] "
            f"Given {as_string(criterion.get('given'))}; "
            f"When {as_string(criterion.get('when'))}; "
            f"Then {as_string(criterion.get('then'))}."
        )
    return lines


def format_decision(atom: LoadedAtom) -> list[str]:
    chosen_option = next(
        (
            option
            for option in as_mapping_list(atom.data.get("options"))
            if as_string(option.get("status")) == "chosen"
        ),
        None,
    )
    if chosen_option is None:
        return ["- Chosen option: Decision deferred"]
    return [
        "- Chosen option: "
        f"{as_string(chosen_option.get('id'))} — "
        f"{as_string(chosen_option.get('label'))}",
        f"- Decision rationale: {as_string(chosen_option.get('chosen_reason'))}",
    ]


def build_readme(root: Path, atoms: list[LoadedAtom]) -> str:
    type_counts = Counter(as_string(atom.data.get("type")) for atom in atoms)
    status_counts = Counter(as_string(atom.data.get("status")) for atom in atoms)
    topic_counts = Counter(as_string(atom.data.get("topic")) for atom in atoms)

    summary_rows = [["Total atoms", str(len(atoms))]]
    type_rows = [[key, str(type_counts[key])] for key in sorted(type_counts)]
    status_rows = [[key, str(status_counts[key])] for key in sorted(status_counts)]
    topic_rows = [[key, str(topic_counts[key])] for key in sorted(topic_counts)]
    atom_rows = [
        [
            atom.atom_id,
            as_string(atom.data.get("type")),
            as_string(atom.data.get("layer")),
            as_string(atom.data.get("step")) or "—",
            as_string(atom.data.get("title")),
            as_string(atom.data.get("status")),
            as_string(atom.data.get("priority")),
            as_string(atom.data.get("topic")),
            relative_spec_path(atom.path, root),
        ]
        for atom in atoms
    ]

    sections = [
        "# Source Spec Atom Overview",
        "",
        "## Summary",
        markdown_table(["Metric", "Value"], summary_rows),
        "",
        "## By Type",
        markdown_table(["Type", "Count"], type_rows),
        "",
        "## By Status",
        markdown_table(["Status", "Count"], status_rows),
        "",
        "## By Topic",
        markdown_table(["Topic", "Count"], topic_rows),
        "",
        "## Atom Index",
        markdown_table(
            ["ID", "Type", "Layer", "Step", "Title", "Status", "Priority", "Topic", "File"],
            atom_rows,
        ),
    ]
    return "\n".join(sections) + "\n"


def build_group_view(
    group_name: str,
    heading: str,
    atoms: list[LoadedAtom],
) -> str:
    table_rows = [
        [
            atom.atom_id,
            as_string(atom.data.get("type")),
            as_string(atom.data.get("title")),
            as_string(atom.data.get("status")),
            as_string(atom.data.get("priority")),
        ]
        for atom in atoms
    ]
    sections = [
        f"# {heading}: {group_name}",
        "",
        markdown_table(["ID", "Type", "Title", "Status", "Priority"], table_rows),
        "",
    ]
    for atom in atoms:
        sections.extend(summarize_atom(atom))
        sections.append("")
    return "\n".join(sections).rstrip() + "\n"


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def clear_markdown_files(path: Path) -> None:
    if not path.exists():
        return
    for markdown_file in path.glob("*.md"):
        markdown_file.unlink()


def generate_views(root: Path | None = None) -> None:
    base_root = root or Path(__file__).resolve().parents[1]
    atoms = sorted(load_atoms(base_root), key=lambda atom: atom.atom_id)
    views_root = spec_root(base_root) / "views"
    by_topic_root = views_root / "by-topic"
    by_status_root = views_root / "by-status"
    by_layer_root = views_root / "by-layer"
    by_step_root = views_root / "by-step"

    clear_markdown_files(by_topic_root)
    clear_markdown_files(by_status_root)
    clear_markdown_files(by_layer_root)
    clear_markdown_files(by_step_root)

    by_topic: dict[str, list[LoadedAtom]] = defaultdict(list)
    by_status: dict[str, list[LoadedAtom]] = defaultdict(list)
    by_layer: dict[str, list[LoadedAtom]] = defaultdict(list)
    by_step: dict[str, list[LoadedAtom]] = defaultdict(list)
    for atom in atoms:
        by_topic[as_string(atom.data.get("topic"))].append(atom)
        by_status[as_string(atom.data.get("status"))].append(atom)
        by_layer[as_string(atom.data.get("layer"))].append(atom)
        step = as_string(atom.data.get("step"))
        if step:
            by_step[step].append(atom)

    for expected_status in ("confirmed", "deferred", "proposed", "superseded"):
        by_status.setdefault(expected_status, [])

    write_markdown(views_root / "README.md", build_readme(base_root, atoms))
    for topic, topic_atoms in sorted(by_topic.items()):
        write_markdown(
            by_topic_root / f"{topic}.md",
            build_group_view(topic, "Source Spec Atoms by Topic", topic_atoms),
        )
    for status, status_atoms in sorted(by_status.items()):
        write_markdown(
            by_status_root / f"{status}.md",
            build_group_view(status, "Source Spec Atoms by Status", status_atoms),
        )
    for layer, layer_atoms in sorted(by_layer.items()):
        write_markdown(
            by_layer_root / f"{layer}.md",
            build_group_view(layer, "Source Spec Atoms by Layer", layer_atoms),
        )
    for step, step_atoms in sorted(by_step.items()):
        write_markdown(
            by_step_root / f"{step}.md",
            build_group_view(step, "Source Spec Atoms by Step", step_atoms),
        )


def main() -> int:
    configure_logging()
    try:
        generate_views()
    except Exception as exc:  # noqa: BLE001
        logger.error("View generation failed: %s", exc)
        return 1
    logger.info("Generated source spec views.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
