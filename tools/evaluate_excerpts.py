#!/usr/bin/env python3
"""Evaluate smoke_api excerpt outputs against structural rules.

Usage:
    python tools/evaluate_excerpts.py
    python tools/evaluate_excerpts.py --root integration_tests/smoke_api --strict
"""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any


if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace",
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace",
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from engines.excerpting.contracts import ConsensusRecord, ExcerptRecord, ScholarlyFunction


TOKEN_RE = re.compile(r"\S+")
WHITESPACE_RE = re.compile(r"\s+")
ZWNJ = "\u200c"
CHECK_ORDER = [
    "required_fields",
    "word_offset_consistency",
    "text_snippet_prefix_match",
    "segment_indices_validity",
    "excerpt_id_format",
    "empty_field_detection",
    "consensus_structure",
    "zwnj_scan",
    "duplicate_detection",
    "gate_cross_reference",
    "short_long_outliers",
    "author_id_audit",
    "consensus_coverage",
    "physical_pages",
    "function_taxonomy_validation",
]
CHECK_TITLES = {
    "required_fields": "Required Fields",
    "word_offset_consistency": "Word Offset Consistency",
    "text_snippet_prefix_match": "text_snippet Prefix Match",
    "segment_indices_validity": "segment_indices Validity",
    "excerpt_id_format": "excerpt_id Format",
    "empty_field_detection": "Empty Field Detection",
    "consensus_structure": "Consensus Structure",
    "zwnj_scan": "ZWNJ Scan",
    "duplicate_detection": "Duplicate Detection",
    "gate_cross_reference": "Gate Cross-Reference",
    "short_long_outliers": "Short/Long Outliers",
    "author_id_audit": "author_id Audit",
    "consensus_coverage": "Consensus Coverage",
    "physical_pages": "Physical Pages",
    "function_taxonomy_validation": "Function Taxonomy Validation",
}
CHECK_DESCRIPTIONS = {
    "required_fields": "Top-level required ExcerptRecord fields are present and each record validates against the Pydantic contract.",
    "word_offset_consistency": "start_word/end_word resolve to the exact primary_text substring and agree with the Phase 2 grouping boundaries.",
    "text_snippet_prefix_match": "Whitespace-normalized first 80 characters of primary_text match text_snippet per SPEC V-P3-2.",
    "segment_indices_validity": "segment_indices are non-empty, contiguous, ascending, and match Phase 2 unit/segment provenance.",
    "excerpt_id_format": "excerpt_id exactly matches exc_{source_id}_{div_id}_{chunk_index}_{unit_index}.",
    "empty_field_detection": "Required structural strings are non-blank and required collections are not empty when the SPEC expects content.",
    "consensus_structure": "consensus_metadata is structurally valid and internally coherent when present.",
    "zwnj_scan": "Invisible U+200C characters are inventoried across excerpt fields for follow-up review.",
    "duplicate_detection": "Duplicate excerpt IDs, duplicate coordinate keys, and duplicate normalized primary_text bodies are detected across the corpus.",
    "gate_cross_reference": "gate_flags and gate_queue.jsonl entries agree in both directions within each package.",
    "short_long_outliers": "Word-count outliers are reported using a hybrid short-threshold plus Tukey upper-fence audit.",
    "author_id_audit": "primary_author_layer.author_id values are inventoried, including sentinel values such as unknown.",
    "consensus_coverage": "Records with consensus-only signals always carry consensus_metadata, and decision types are summarized.",
    "physical_pages": "physical_pages matches the page span implied by Phase 1 join points and token-derived character ranges.",
    "function_taxonomy_validation": "All function fields are valid ScholarlyFunction values and agree with Phase 2 provenance.",
}
CONSENSUS_REVIEW_FLAGS = {
    "school_consensus_disagreement",
    "verification_skipped",
    "attribution_consensus_escalated",
}
GATE_CODES = {"EX-G-001", "EX-G-002", "EX-G-003"}
UNKNOWN_AUTHOR_IDS = {"unknown", "UNKNOWN", "sch_unknown"}
VALID_FUNCTIONS = {member.value for member in ScholarlyFunction}
REQUIRED_FIELDS = sorted(
    name for name, model_field in ExcerptRecord.model_fields.items()
    if model_field.is_required()
)
NON_BLANK_STRING_FIELDS = (
    "excerpt_id",
    "source_id",
    "div_id",
    "primary_text",
    "text_snippet",
    "description_arabic",
    "primary_function",
    "self_containment",
)
REQUIRED_NON_EMPTY_LISTS = ("div_path", "segment_indices", "content_types")


def to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): to_jsonable(child) for key, child in value.items()}
    if isinstance(value, list):
        return [to_jsonable(child) for child in value]
    if isinstance(value, tuple):
        return [to_jsonable(child) for child in value]
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "model_dump"):
        return to_jsonable(value.model_dump())
    return value


@dataclass
class Finding:
    package: str | None
    excerpt_id: str | None
    message: str
    severity: str = "error"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "severity": self.severity,
            "message": self.message,
        }
        if self.package is not None:
            data["package"] = self.package
        if self.excerpt_id is not None:
            data["excerpt_id"] = self.excerpt_id
        if self.details:
            data["details"] = to_jsonable(self.details)
        return data


@dataclass
class CheckBucket:
    check_id: str
    metrics: dict[str, Any] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def build(self) -> dict[str, Any]:
        severity_order = {"info": 0, "warning": 1, "error": 2}
        max_severity = max(
            (severity_order[finding.severity] for finding in self.findings),
            default=0,
        )
        status = "pass"
        if max_severity >= severity_order["error"]:
            status = "fail"
        elif max_severity >= severity_order["warning"]:
            status = "warn"

        return {
            "title": CHECK_TITLES[self.check_id],
            "description": CHECK_DESCRIPTIONS[self.check_id],
            "status": status,
            "finding_count": len(self.findings),
            "metrics": self.metrics,
            "sample_findings": [finding.to_dict() for finding in self.findings[:20]],
        }


@dataclass
class RecordContext:
    package: str
    package_dir: Path
    raw: dict[str, Any]
    model: ExcerptRecord

    @property
    def excerpt_id(self) -> str:
        return self.raw["excerpt_id"]


@dataclass
class PackageArtifacts:
    name: str
    root: Path
    excerpts: list[dict[str, Any]]
    phase1_chunks: dict[str, dict[str, Any]]
    phase2a_segments: dict[str, dict[int, dict[str, Any]]]
    phase2b_units: dict[str, dict[int, dict[str, Any]]]
    gate_entries: dict[str, list[dict[str, Any]]]
    validation_drops: list[dict[str, Any]]


def normalize_ws(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text).strip()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def find_string_paths(
    value: Any,
    path: tuple[str, ...] = (),
) -> list[tuple[tuple[str, ...], str]]:
    found: list[tuple[tuple[str, ...], str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(find_string_paths(child, path + (str(key),)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_string_paths(child, path + (str(index),)))
    elif isinstance(value, str):
        found.append((path, value))
    return found


def compute_token_spans(text: str) -> list[tuple[int, int]]:
    return [match.span() for match in TOKEN_RE.finditer(text)]


def compute_page_segments(chunk: dict[str, Any]) -> list[dict[str, int | None]]:
    assembled_text = chunk["assembled_text"]
    join_offsets = [
        join_point["char_offset_in_assembled"]
        for join_point in chunk["assembly_metadata"]["join_points"]
    ]
    segments: list[dict[str, int | None]] = []
    previous_offset = 0
    for index, page in enumerate(chunk["physical_pages"]):
        next_offset = join_offsets[index] if index < len(join_offsets) else len(assembled_text)
        segments.append(
            {
                "start_char": previous_offset,
                "end_char": next_offset,
                "volume": page["volume"],
                "page_number": page["page_number_int"],
            }
        )
        previous_offset = next_offset
    return segments


def expected_page_range(
    chunk: dict[str, Any],
    start_char: int,
    end_char: int,
) -> dict[str, int | None] | None:
    page_segments = compute_page_segments(chunk)
    overlaps = [
        segment for segment in page_segments
        if not (end_char <= segment["start_char"] or start_char >= segment["end_char"])
    ]
    if not overlaps:
        return None
    volumes = {segment["volume"] for segment in overlaps}
    volume: int | None = None
    if len(volumes) == 1:
        volume = next(iter(volumes))
    return {
        "volume": volume,
        "start_page": overlaps[0]["page_number"],
        "end_page": overlaps[-1]["page_number"],
    }


def quantile(sorted_values: list[int], p: float) -> float:
    if not sorted_values:
        raise ValueError("cannot compute quantile of empty sequence")
    position = (len(sorted_values) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def load_package(package_dir: Path) -> PackageArtifacts:
    excerpts = read_jsonl(package_dir / "excerpts.jsonl")
    phase1_chunks = {
        chunk["chunk_id"]: chunk
        for chunk in read_json(package_dir / "phase1_chunks.json")
    }
    phase2a_segments = {
        path.stem.removeprefix("chunk_"): {
            segment["segment_index"]: segment
            for segment in read_json(path)
        }
        for path in sorted((package_dir / "phase2a_classifications").glob("*.json"))
    }
    phase2b_units = {
        path.stem.removeprefix("chunk_"): {
            unit["unit_index"]: unit
            for unit in read_json(path)
        }
        for path in sorted((package_dir / "phase2b_groupings").glob("*.json"))
    }
    gate_entries = defaultdict(list)
    for entry in read_jsonl(package_dir / "gate_queue.jsonl"):
        gate_entries[entry["excerpt_id"]].append(entry)
    return PackageArtifacts(
        name=package_dir.name,
        root=package_dir,
        excerpts=excerpts,
        phase1_chunks=phase1_chunks,
        phase2a_segments=phase2a_segments,
        phase2b_units=phase2b_units,
        gate_entries=dict(gate_entries),
        validation_drops=read_jsonl(package_dir / "validation_drops.jsonl"),
    )


def build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    overall = report["overall"]
    lines.append("# Structural Excerpt Report")
    lines.append("")
    lines.append(
        f"Generated: `{report['generated_at']}`  "
        f"Packages: `{overall['package_count']}`  "
        f"Excerpts: `{overall['excerpt_count']}`"
    )
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | ---: |")
    lines.append(f"| Packages | {overall['package_count']} |")
    lines.append(f"| Excerpts | {overall['excerpt_count']} |")
    lines.append(f"| Phase 2 teaching units | {overall['phase2_unit_count']} |")
    lines.append(f"| Validation drops | {overall['validation_drop_count']} |")
    lines.append(f"| Gate queue entries | {overall['gate_entry_count']} |")
    lines.append(f"| Consensus records | {overall['consensus_record_count']} |")
    lines.append("")
    lines.append("## Check Summary")
    lines.append("")
    lines.append("| Check | Status | Findings |")
    lines.append("| --- | --- | ---: |")
    for check_id in CHECK_ORDER:
        check = report["checks"][check_id]
        lines.append(
            f"| {check['title']} | `{check['status']}` | {check['finding_count']} |"
        )
    lines.append("")
    lines.append("## Key Findings")
    lines.append("")
    duplicate_metrics = report["checks"]["duplicate_detection"]["metrics"]
    lines.append(
        f"- Duplicate excerpt IDs: `{duplicate_metrics['duplicate_excerpt_id_count']}` "
        f"keys across `{duplicate_metrics['duplicate_excerpt_instances']}` records."
    )
    author_metrics = report["checks"]["author_id_audit"]["metrics"]
    lines.append(
        f"- `author_id` sentinel `unknown`: `{author_metrics['unknown_author_id_count']}` "
        f"of `{overall['excerpt_count']}` excerpts."
    )
    zwnj_metrics = report["checks"]["zwnj_scan"]["metrics"]
    lines.append(
        f"- ZWNJ-bearing excerpts: `{zwnj_metrics['excerpt_count_with_zwnj']}` "
        f"with `{zwnj_metrics['total_zwnj_occurrences']}` total U+200C occurrences."
    )
    outlier_metrics = report["checks"]["short_long_outliers"]["metrics"]
    lines.append(
        f"- Word-count outliers: `{outlier_metrics['short_outlier_count']}` short "
        f"and `{outlier_metrics['long_outlier_count']}` long."
    )
    lines.append("")
    lines.append("## Per-Check Details")
    lines.append("")
    for check_id in CHECK_ORDER:
        check = report["checks"][check_id]
        lines.append(f"### {check['title']}")
        lines.append("")
        lines.append(f"Status: `{check['status']}`")
        lines.append("")
        lines.append(check["description"])
        lines.append("")
        if check["metrics"]:
            lines.append("| Metric | Value |")
            lines.append("| --- | --- |")
            for key, value in check["metrics"].items():
                rendered = json.dumps(value, ensure_ascii=False)
                lines.append(f"| `{key}` | `{rendered}` |")
            lines.append("")
        if check["sample_findings"]:
            lines.append("Sample findings:")
            for finding in check["sample_findings"]:
                package = finding.get("package", "n/a")
                excerpt_id = finding.get("excerpt_id", "n/a")
                lines.append(
                    f"- `{finding['severity']}` {package} / {excerpt_id}: "
                    f"{finding['message']}"
                )
            lines.append("")
        else:
            lines.append("No findings.")
            lines.append("")
    lines.append("## Package Summary")
    lines.append("")
    lines.append("| Package | Excerpts | Gate Entries | Validation Drops |")
    lines.append("| --- | ---: | ---: | ---: |")
    for package_name, summary in report["packages"].items():
        lines.append(
            f"| {package_name} | {summary['excerpt_count']} | "
            f"{summary['gate_entry_count']} | {summary['validation_drop_count']} |"
        )
    lines.append("")
    return "\n".join(lines)


def evaluate(root: Path) -> dict[str, Any]:
    package_dirs = sorted(
        path.parent
        for path in root.glob("*/excerpts.jsonl")
    )
    if not package_dirs:
        raise FileNotFoundError(f"No excerpts.jsonl files found under {root}")

    buckets = {check_id: CheckBucket(check_id) for check_id in CHECK_ORDER}
    packages = {package_dir.name: load_package(package_dir) for package_dir in package_dirs}
    package_summaries: dict[str, dict[str, Any]] = {}
    all_records: list[RecordContext] = []
    word_counts: list[int] = []
    duplicate_excerpt_ids = defaultdict(list)
    duplicate_coordinate_keys = defaultdict(list)
    duplicate_primary_texts = defaultdict(list)
    decision_type_counts: Counter[str] = Counter()
    zwnj_field_counts: Counter[str] = Counter()
    zwnj_excerpt_count = 0
    total_zwnj_occurrences = 0
    author_id_counts: Counter[str] = Counter()

    for package_name, artifacts in packages.items():
        package_summaries[package_name] = {
            "excerpt_count": len(artifacts.excerpts),
            "phase2_unit_count": sum(len(units) for units in artifacts.phase2b_units.values()),
            "validation_drop_count": len(artifacts.validation_drops),
            "gate_entry_count": sum(len(entries) for entries in artifacts.gate_entries.values()),
        }

        for raw in artifacts.excerpts:
            excerpt_id = raw.get("excerpt_id")
            missing_required = sorted(
                field_name for field_name in REQUIRED_FIELDS if field_name not in raw
            )
            if missing_required:
                buckets["required_fields"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=excerpt_id,
                        message="Missing required top-level fields.",
                        details={"missing_fields": missing_required},
                    )
                )
                continue

            try:
                model = ExcerptRecord.model_validate(raw)
            except Exception as exc:
                buckets["required_fields"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=excerpt_id,
                        message="ExcerptRecord contract validation failed.",
                        details={"error": str(exc)},
                    )
                )
                continue

            context = RecordContext(
                package=package_name,
                package_dir=artifacts.root,
                raw=raw,
                model=model,
            )
            all_records.append(context)

            expected_id = (
                f"exc_{model.source_id}_{model.div_id}_{model.chunk_index}_{model.unit_index}"
            )
            if model.excerpt_id != expected_id:
                buckets["excerpt_id_format"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message="excerpt_id does not match the deterministic format.",
                        details={"expected": expected_id, "actual": model.excerpt_id},
                    )
                )

            for field_name in NON_BLANK_STRING_FIELDS:
                value = raw.get(field_name)
                if isinstance(value, str) and not value.strip():
                    buckets["empty_field_detection"].add(
                        Finding(
                            package=package_name,
                            excerpt_id=model.excerpt_id,
                            message=f"{field_name} is blank.",
                        )
                    )
            for field_name in REQUIRED_NON_EMPTY_LISTS:
                value = raw.get(field_name)
                if isinstance(value, list) and not value:
                    buckets["empty_field_detection"].add(
                        Finding(
                            package=package_name,
                            excerpt_id=model.excerpt_id,
                            message=f"{field_name} is empty.",
                        )
                    )
            if not model.excerpt_topic and "llm_enrichment_failed" not in model.review_flags:
                buckets["empty_field_detection"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message="excerpt_topic is empty without llm_enrichment_failed.",
                    )
                )

            blank_paths = [
                ".".join(path)
                for path, value in find_string_paths(raw)
                if not value.strip()
            ]
            for blank_path in blank_paths:
                buckets["empty_field_detection"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message=f"Blank string detected at {blank_path}.",
                    )
                )

            if model.consensus_metadata is not None:
                try:
                    consensus = ConsensusRecord.model_validate(raw["consensus_metadata"])
                except Exception as exc:
                    buckets["consensus_structure"].add(
                        Finding(
                            package=package_name,
                            excerpt_id=model.excerpt_id,
                            message="consensus_metadata failed contract validation.",
                            details={"error": str(exc)},
                        )
                    )
                else:
                    if not consensus.decisions:
                        buckets["consensus_structure"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="consensus_metadata.decisions is empty.",
                            )
                        )
                    for decision in consensus.decisions:
                        decision_type_counts[decision.decision_type] += 1
                        if not decision.decision_type.strip():
                            buckets["consensus_structure"].add(
                                Finding(
                                    package=package_name,
                                    excerpt_id=model.excerpt_id,
                                    message="Consensus decision_type is blank.",
                                )
                            )
                        if not decision.final_value.strip():
                            buckets["consensus_structure"].add(
                                Finding(
                                    package=package_name,
                                    excerpt_id=model.excerpt_id,
                                    message="Consensus final_value is blank.",
                                )
                            )
                        if decision.verifier_agrees is True and decision.verifier_value is None:
                            buckets["consensus_structure"].add(
                                Finding(
                                    package=package_name,
                                    excerpt_id=model.excerpt_id,
                                    message="verifier_agrees=true but verifier_value is null.",
                                )
                            )
                        if (
                            decision.resolution_method == "no_majority_gate"
                            and decision.escalation_value is None
                        ):
                            buckets["consensus_structure"].add(
                                Finding(
                                    package=package_name,
                                    excerpt_id=model.excerpt_id,
                                    message="no_majority_gate decision is missing escalation_value.",
                                )
                            )

            strings_with_zwnj = []
            zwnj_occurrences = 0
            for path, value in find_string_paths(raw):
                count = value.count(ZWNJ)
                if count:
                    zwnj_occurrences += count
                    rendered_path = ".".join(path)
                    strings_with_zwnj.append(rendered_path)
                    zwnj_field_counts[rendered_path] += count
            if zwnj_occurrences:
                zwnj_excerpt_count += 1
                total_zwnj_occurrences += zwnj_occurrences
                buckets["zwnj_scan"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        severity="warning",
                        message="U+200C detected in excerpt payload.",
                        details={
                            "zwnj_occurrences": zwnj_occurrences,
                            "fields": strings_with_zwnj,
                        },
                    )
                )

            author_id_counts[model.primary_author_layer.author_id] += 1
            if model.primary_author_layer.author_id in UNKNOWN_AUTHOR_IDS:
                buckets["author_id_audit"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        severity="warning",
                        message="primary_author_layer.author_id uses the sentinel value unknown.",
                    )
                )

            chunk = artifacts.phase1_chunks.get(model.div_id)
            if chunk is None:
                buckets["word_offset_consistency"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message="No matching Phase 1 chunk found for div_id.",
                        details={"div_id": model.div_id},
                    )
                )
                buckets["physical_pages"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message="No matching Phase 1 chunk found for physical page validation.",
                        details={"div_id": model.div_id},
                    )
                )
            else:
                token_spans = compute_token_spans(chunk["assembled_text"])
                if not token_spans:
                    buckets["word_offset_consistency"].add(
                        Finding(
                            package=package_name,
                            excerpt_id=model.excerpt_id,
                            message="Phase 1 chunk tokenization produced no tokens.",
                        )
                    )
                elif (
                    model.start_word < 0
                    or model.end_word < model.start_word
                    or model.end_word >= len(token_spans)
                ):
                    buckets["word_offset_consistency"].add(
                        Finding(
                            package=package_name,
                            excerpt_id=model.excerpt_id,
                            message="start_word/end_word is outside the assembled_text token span.",
                            details={
                                "start_word": model.start_word,
                                "end_word": model.end_word,
                                "token_count": len(token_spans),
                            },
                        )
                    )
                else:
                    start_char = token_spans[model.start_word][0]
                    end_char = token_spans[model.end_word][1]
                    expected_primary_text = chunk["assembled_text"][start_char:end_char]
                    if expected_primary_text != model.primary_text:
                        buckets["word_offset_consistency"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="Word offsets do not resolve to the stored primary_text.",
                                details={
                                    "expected_preview": expected_primary_text[:120],
                                    "actual_preview": model.primary_text[:120],
                                },
                            )
                        )

                    expected_pages = expected_page_range(chunk, start_char, end_char)
                    actual_pages = (
                        model.physical_pages.model_dump()
                        if model.physical_pages is not None
                        else None
                    )
                    if expected_pages != actual_pages:
                        buckets["physical_pages"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="physical_pages does not match the Phase 1 page span.",
                                details={
                                    "expected": expected_pages,
                                    "actual": actual_pages,
                                },
                            )
                        )

            expected_snippet = normalize_ws(model.primary_text[:80])
            actual_snippet = normalize_ws(model.text_snippet)
            if not expected_snippet.startswith(actual_snippet):
                buckets["text_snippet_prefix_match"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message="text_snippet is not a normalized prefix of the first 80 characters of primary_text.",
                        details={
                            "expected": expected_snippet,
                            "actual": actual_snippet,
                        },
                    )
                )

            segment_indices = model.segment_indices
            if not segment_indices:
                buckets["segment_indices_validity"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message="segment_indices is empty.",
                    )
                )
            else:
                expected_contiguous = list(range(segment_indices[0], segment_indices[-1] + 1))
                if segment_indices != expected_contiguous:
                    buckets["segment_indices_validity"].add(
                        Finding(
                            package=package_name,
                            excerpt_id=model.excerpt_id,
                            message="segment_indices is not a contiguous ascending sequence.",
                            details={"segment_indices": segment_indices},
                        )
                    )

            units_for_chunk = artifacts.phase2b_units.get(model.div_id)
            segments_for_chunk = artifacts.phase2a_segments.get(model.div_id)
            if units_for_chunk is None:
                buckets["segment_indices_validity"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message="No matching Phase 2 grouping file found for div_id.",
                        details={"div_id": model.div_id},
                    )
                )
            else:
                unit = units_for_chunk.get(model.unit_index)
                if unit is None:
                    buckets["segment_indices_validity"].add(
                        Finding(
                            package=package_name,
                            excerpt_id=model.excerpt_id,
                            message="unit_index not found in the matching Phase 2 grouping file.",
                            details={"unit_index": model.unit_index},
                        )
                    )
                else:
                    if unit["segment_indices"] != segment_indices:
                        buckets["segment_indices_validity"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="segment_indices does not match the Phase 2 grouping record.",
                                details={
                                    "expected": unit["segment_indices"],
                                    "actual": segment_indices,
                                },
                            )
                        )
                    if unit["start_word"] != model.start_word or unit["end_word"] != model.end_word:
                        buckets["word_offset_consistency"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="Word offsets do not match the Phase 2 grouping record.",
                                details={
                                    "expected": {
                                        "start_word": unit["start_word"],
                                        "end_word": unit["end_word"],
                                    },
                                    "actual": {
                                        "start_word": model.start_word,
                                        "end_word": model.end_word,
                                    },
                                },
                            )
                        )

            if segments_for_chunk is None:
                buckets["segment_indices_validity"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=model.excerpt_id,
                        message="No matching Phase 2 classification file found for div_id.",
                        details={"div_id": model.div_id},
                    )
                )
            elif segment_indices:
                missing_segments = [
                    index for index in segment_indices if index not in segments_for_chunk
                ]
                if missing_segments:
                    buckets["segment_indices_validity"].add(
                        Finding(
                            package=package_name,
                            excerpt_id=model.excerpt_id,
                            message="segment_indices references missing Phase 2 segments.",
                            details={"missing_segment_indices": missing_segments},
                        )
                    )
                else:
                    first_segment = segments_for_chunk[segment_indices[0]]
                    last_segment = segments_for_chunk[segment_indices[-1]]
                    if (
                        first_segment["start_word"] != model.start_word
                        or last_segment["end_word"] != model.end_word
                    ):
                        buckets["segment_indices_validity"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="Excerpt word offsets do not align to the first/last segment boundaries.",
                                details={
                                    "expected": {
                                        "start_word": first_segment["start_word"],
                                        "end_word": last_segment["end_word"],
                                    },
                                    "actual": {
                                        "start_word": model.start_word,
                                        "end_word": model.end_word,
                                    },
                                },
                            )
                        )

                    segment_functions = {
                        segments_for_chunk[index]["scholarly_function"]
                        for index in segment_indices
                    }
                    invalid_values = [
                        value
                        for value in [
                            model.primary_function,
                            *model.secondary_functions,
                            *model.content_types,
                        ]
                        if value not in VALID_FUNCTIONS
                    ]
                    if invalid_values:
                        buckets["function_taxonomy_validation"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="Encountered function values outside the ScholarlyFunction taxonomy.",
                                details={"invalid_values": invalid_values},
                            )
                        )
                    if model.primary_function not in model.content_types:
                        buckets["function_taxonomy_validation"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="primary_function is missing from content_types.",
                            )
                        )
                    missing_secondary = [
                        value for value in model.secondary_functions
                        if value not in model.content_types
                    ]
                    if missing_secondary:
                        buckets["function_taxonomy_validation"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="secondary_functions is not a subset of content_types.",
                                details={"missing_secondary": missing_secondary},
                            )
                        )
                    if len(set(model.content_types)) != len(model.content_types):
                        buckets["function_taxonomy_validation"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="content_types contains duplicate entries.",
                            )
                        )
                    if set(model.content_types) != segment_functions:
                        buckets["function_taxonomy_validation"].add(
                            Finding(
                                package=package_name,
                                excerpt_id=model.excerpt_id,
                                message="content_types does not match the set of Phase 2 segment functions.",
                                details={
                                    "expected": sorted(segment_functions),
                                    "actual": model.content_types,
                                },
                            )
                        )

            duplicate_excerpt_ids[model.excerpt_id].append(context)
            coord_key = (model.source_id, model.div_id, model.chunk_index, model.unit_index)
            duplicate_coordinate_keys[coord_key].append(context)
            duplicate_primary_texts[normalize_ws(model.primary_text)].append(context)
            word_counts.append(len(model.primary_text.split()))

        flagged_excerpt_ids = {
            excerpt["excerpt_id"]
            for excerpt in artifacts.excerpts
            if excerpt.get("gate_flags")
        }
        gate_excerpt_ids = set(artifacts.gate_entries)
        for excerpt in artifacts.excerpts:
            gate_flags = excerpt.get("gate_flags", [])
            if not gate_flags:
                continue
            entries = artifacts.gate_entries.get(excerpt["excerpt_id"], [])
            entry_codes = {entry["gate_code"] for entry in entries}
            missing_codes = sorted(set(gate_flags) - entry_codes)
            if missing_codes:
                buckets["gate_cross_reference"].add(
                    Finding(
                        package=package_name,
                        excerpt_id=excerpt["excerpt_id"],
                        message="gate_flags contains codes missing from gate_queue.jsonl.",
                        details={"missing_gate_codes": missing_codes},
                    )
                )
        orphan_gate_ids = sorted(gate_excerpt_ids - flagged_excerpt_ids)
        for orphan_excerpt_id in orphan_gate_ids:
            buckets["gate_cross_reference"].add(
                Finding(
                    package=package_name,
                    excerpt_id=orphan_excerpt_id,
                    message="gate_queue.jsonl contains an entry with no matching gate_flags in excerpts.jsonl.",
                )
            )

    for excerpt_id, contexts in sorted(duplicate_excerpt_ids.items()):
        if len(contexts) <= 1:
            continue
        packages_for_id = sorted(context.package for context in contexts)
        buckets["duplicate_detection"].add(
            Finding(
                package=None,
                excerpt_id=excerpt_id,
                message="Duplicate excerpt_id detected across the smoke corpus.",
                details={"packages": packages_for_id},
            )
        )
    for coord_key, contexts in sorted(duplicate_coordinate_keys.items()):
        if len(contexts) <= 1:
            continue
        unique_ids = {context.excerpt_id for context in contexts}
        if len(unique_ids) == 1:
            continue
        buckets["duplicate_detection"].add(
            Finding(
                package=None,
                excerpt_id=None,
                message="Duplicate coordinate key detected with different excerpt IDs.",
                details={
                    "coordinate_key": list(coord_key),
                    "excerpt_ids": sorted(unique_ids),
                },
            )
        )
    for normalized_text, contexts in duplicate_primary_texts.items():
        if len(contexts) <= 1:
            continue
        unique_ids = {context.excerpt_id for context in contexts}
        if len(unique_ids) <= 1:
            continue
        buckets["duplicate_detection"].add(
            Finding(
                package=None,
                excerpt_id=None,
                severity="warning",
                message="Duplicate normalized primary_text detected across different excerpt IDs.",
                details={
                    "excerpt_ids": sorted(unique_ids),
                    "packages": sorted({context.package for context in contexts}),
                    "text_preview": normalized_text[:120],
                },
            )
        )

    for context in all_records:
        expects_consensus = False
        reasons: list[str] = []
        if context.model.primary_author_layer.rule_applied == "LA-3":
            expects_consensus = True
            reasons.append("LA-3")
        if context.model.attribution_confidence is not None:
            expects_consensus = True
            reasons.append("attribution_confidence")
        if GATE_CODES.intersection(context.model.gate_flags):
            expects_consensus = True
            reasons.append("gate_flags")
        if CONSENSUS_REVIEW_FLAGS.intersection(context.model.review_flags):
            expects_consensus = True
            reasons.append("review_flags")
        if expects_consensus and context.model.consensus_metadata is None:
            buckets["consensus_coverage"].add(
                Finding(
                    package=context.package,
                    excerpt_id=context.excerpt_id,
                    message="Consensus-signaled record is missing consensus_metadata.",
                    details={"reasons": reasons},
                )
            )

    sorted_word_counts = sorted(word_counts)
    q1 = quantile(sorted_word_counts, 0.25)
    q3 = quantile(sorted_word_counts, 0.75)
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    short_threshold = 10
    for context in all_records:
        word_count = len(context.model.primary_text.split())
        if word_count <= short_threshold:
            buckets["short_long_outliers"].add(
                Finding(
                    package=context.package,
                    excerpt_id=context.excerpt_id,
                    severity="warning",
                    message="Short word-count outlier.",
                    details={"word_count": word_count, "threshold": short_threshold},
                )
            )
        elif word_count > upper_fence:
            buckets["short_long_outliers"].add(
                Finding(
                    package=context.package,
                    excerpt_id=context.excerpt_id,
                    severity="warning",
                    message="Long word-count outlier.",
                    details={"word_count": word_count, "upper_fence": upper_fence},
                )
            )

    buckets["required_fields"].metrics = {
        "required_field_count": len(REQUIRED_FIELDS),
        "required_fields": REQUIRED_FIELDS,
        "records_evaluated": len(all_records),
    }
    buckets["word_offset_consistency"].metrics = {
        "records_evaluated": len(all_records),
    }
    buckets["text_snippet_prefix_match"].metrics = {
        "records_evaluated": len(all_records),
    }
    buckets["segment_indices_validity"].metrics = {
        "records_evaluated": len(all_records),
    }
    buckets["excerpt_id_format"].metrics = {
        "records_evaluated": len(all_records),
    }
    buckets["empty_field_detection"].metrics = {
        "records_evaluated": len(all_records),
    }
    buckets["consensus_structure"].metrics = {
        "records_with_consensus_metadata": sum(
            1 for context in all_records if context.model.consensus_metadata is not None
        ),
        "decision_type_counts": dict(sorted(decision_type_counts.items())),
    }
    buckets["zwnj_scan"].metrics = {
        "excerpt_count_with_zwnj": zwnj_excerpt_count,
        "total_zwnj_occurrences": total_zwnj_occurrences,
        "field_occurrence_counts": dict(zwnj_field_counts.most_common()),
    }
    buckets["duplicate_detection"].metrics = {
        "duplicate_excerpt_id_count": sum(
            1 for contexts in duplicate_excerpt_ids.values() if len(contexts) > 1
        ),
        "duplicate_excerpt_instances": sum(
            len(contexts)
            for contexts in duplicate_excerpt_ids.values()
            if len(contexts) > 1
        ),
        "duplicate_coordinate_key_count": sum(
            1 for contexts in duplicate_coordinate_keys.values()
            if len(contexts) > 1
        ),
        "duplicate_primary_text_count": sum(
            1 for contexts in duplicate_primary_texts.values()
            if len({context.excerpt_id for context in contexts}) > 1
        ),
    }
    buckets["gate_cross_reference"].metrics = {
        "records_with_gate_flags": sum(
            1 for context in all_records if context.model.gate_flags
        ),
        "gate_queue_entry_count": sum(
            sum(len(entries) for entries in artifacts.gate_entries.values())
            for artifacts in packages.values()
        ),
    }
    buckets["short_long_outliers"].metrics = {
        "min_word_count": min(sorted_word_counts),
        "median_word_count": median(sorted_word_counts),
        "max_word_count": max(sorted_word_counts),
        "q1_word_count": q1,
        "q3_word_count": q3,
        "iqr_word_count": iqr,
        "upper_fence": upper_fence,
        "short_threshold_words": short_threshold,
        "short_outlier_count": sum(
            1 for context in all_records
            if len(context.model.primary_text.split()) <= short_threshold
        ),
        "long_outlier_count": sum(
            1 for context in all_records
            if len(context.model.primary_text.split()) > upper_fence
        ),
    }
    buckets["author_id_audit"].metrics = {
        "unique_author_id_count": len(author_id_counts),
        "author_id_counts": dict(author_id_counts.most_common()),
        "unknown_author_id_count": sum(
            count for author_id, count in author_id_counts.items()
            if author_id in UNKNOWN_AUTHOR_IDS
        ),
    }
    buckets["consensus_coverage"].metrics = {
        "records_with_consensus_metadata": sum(
            1 for context in all_records if context.model.consensus_metadata is not None
        ),
        "records_with_consensus_signals": sum(
            1 for context in all_records
            if (
                context.model.primary_author_layer.rule_applied == "LA-3"
                or context.model.attribution_confidence is not None
                or bool(GATE_CODES.intersection(context.model.gate_flags))
                or bool(CONSENSUS_REVIEW_FLAGS.intersection(context.model.review_flags))
            )
        ),
        "decision_type_counts": dict(sorted(decision_type_counts.items())),
    }
    buckets["physical_pages"].metrics = {
        "records_evaluated": len(all_records),
    }
    buckets["function_taxonomy_validation"].metrics = {
        "records_evaluated": len(all_records),
        "valid_function_count": len(VALID_FUNCTIONS),
        "valid_functions": sorted(VALID_FUNCTIONS),
    }

    phase2_unit_count = sum(
        summary["phase2_unit_count"] for summary in package_summaries.values()
    )
    validation_drop_count = sum(
        summary["validation_drop_count"] for summary in package_summaries.values()
    )
    gate_entry_count = sum(
        summary["gate_entry_count"] for summary in package_summaries.values()
    )
    overall = {
        "package_count": len(packages),
        "excerpt_count": len(all_records),
        "phase2_unit_count": phase2_unit_count,
        "validation_drop_count": validation_drop_count,
        "gate_entry_count": gate_entry_count,
        "consensus_record_count": sum(
            1 for context in all_records if context.model.consensus_metadata is not None
        ),
        "package_names": sorted(packages),
        "phase2_units_minus_drops": phase2_unit_count - validation_drop_count,
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "overall": overall,
        "packages": package_summaries,
        "checks": {
            check_id: buckets[check_id].build()
            for check_id in CHECK_ORDER
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT / "integration_tests" / "smoke_api",
        help="Root directory containing package subdirectories with excerpts.jsonl files.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any check fails.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    report = evaluate(root)
    json_out = root / "structural_report.json"
    md_out = root / "structural_report.md"

    json_out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md_out.write_text(build_markdown(report), encoding="utf-8")

    failed_checks = [
        check["title"]
        for check in report["checks"].values()
        if check["status"] == "fail"
    ]
    warned_checks = [
        check["title"]
        for check in report["checks"].values()
        if check["status"] == "warn"
    ]

    print("Structural excerpt evaluation complete.")
    print(f"  Root:       {root}")
    print(f"  JSON report:{json_out}")
    print(f"  MD report:  {md_out}")
    print(f"  Excerpts:   {report['overall']['excerpt_count']}")
    print(f"  Failed:     {len(failed_checks)} checks")
    print(f"  Warned:     {len(warned_checks)} checks")
    if failed_checks:
        print(f"  Fail checks:{', '.join(failed_checks)}")
    if warned_checks:
        print(f"  Warn checks:{', '.join(warned_checks)}")

    if args.strict and failed_checks:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
