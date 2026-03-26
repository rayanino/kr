"""CLI tool for reviewing excerpting engine integration test results.

Loads excerpts.jsonl and phase1_chunks.json from a run directory,
maps word offsets back to character offsets, and prints formatted
review blocks with pre/post context for decontextualization spot-check.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from engines.excerpting.contracts import (
    AssembledChunk,
    ExcerptRecord,
    SelfContainmentLevel,
)
from engines.excerpting.src.phase2_classify import _build_token_char_map

# ═══════════════════════════════════════════════════════════════════
# Data Loading
# ═══════════════════════════════════════════════════════════════════


def load_excerpts(run_dir: Path) -> list[ExcerptRecord]:
    """Load all ExcerptRecords from excerpts.jsonl."""
    excerpts_path = run_dir / "excerpts.jsonl"
    if not excerpts_path.exists():
        raise FileNotFoundError(f"excerpts.jsonl not found in {run_dir}")
    records: list[ExcerptRecord] = []
    for line_num, line in enumerate(
        excerpts_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            records.append(ExcerptRecord.model_validate_json(stripped))
        except (json.JSONDecodeError, ValueError) as exc:
            print(
                f"WARNING: Skipping invalid line {line_num} in "
                f"excerpts.jsonl: {exc}",
                file=sys.stderr,
            )
    return records


def load_chunks(run_dir: Path) -> dict[str, AssembledChunk]:
    """Load AssembledChunks from phase1_chunks.json, keyed by chunk_id."""
    chunks_path = run_dir / "phase1_chunks.json"
    if not chunks_path.exists():
        raise FileNotFoundError(f"phase1_chunks.json not found in {run_dir}")
    raw = json.loads(chunks_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(
            f"phase1_chunks.json must be a JSON array, got {type(raw).__name__}"
        )
    chunks: dict[str, AssembledChunk] = {}
    for i, item in enumerate(raw):
        try:
            chunk = AssembledChunk.model_validate(item)
            chunks[chunk.chunk_id] = chunk
        except (ValueError, TypeError) as exc:
            print(
                f"WARNING: Skipping invalid chunk at index {i}: {exc}",
                file=sys.stderr,
            )
    return chunks


# ═══════════════════════════════════════════════════════════════════
# Chunk Matching
# ═══════════════════════════════════════════════════════════════════


def find_chunk_for_excerpt(
    excerpt: ExcerptRecord,
    chunks: dict[str, AssembledChunk],
) -> Optional[AssembledChunk]:
    """Find the chunk matching an excerpt using div_id and DD-PE-4 fallbacks.

    Tries in order:
    1. Exact match: chunk_id == div_id
    2. DD-PE-4 split format: {div_id}_chunk_{chunk_index}
    3. Legacy split format: {div_id}_{chunk_index}
    """
    # Direct match: chunk_id == div_id (unsplit chunks)
    if excerpt.div_id in chunks:
        return chunks[excerpt.div_id]

    # DD-PE-4 split fallback: {div_id}_chunk_{chunk_index}
    split_id = f"{excerpt.div_id}_chunk_{excerpt.chunk_index}"
    if split_id in chunks:
        return chunks[split_id]

    # Legacy split fallback: {div_id}_{chunk_index}
    legacy_id = f"{excerpt.div_id}_{excerpt.chunk_index}"
    if legacy_id in chunks:
        return chunks[legacy_id]

    return None


# ═══════════════════════════════════════════════════════════════════
# Context Extraction
# ═══════════════════════════════════════════════════════════════════

CONTEXT_CHARS = 200


def extract_context(
    excerpt: ExcerptRecord,
    chunk: AssembledChunk,
) -> tuple[str, str]:
    """Extract pre-context and post-context from assembled_text.

    Maps word offsets to character offsets using _build_token_char_map,
    then extracts CONTEXT_CHARS chars before and after the excerpt span.

    Returns:
        (pre_context, post_context) strings.
    """
    token_spans = _build_token_char_map(chunk.assembled_text)

    if not token_spans:
        return ("", "")

    # Clamp word indices to valid range
    start_idx = max(0, min(excerpt.start_word, len(token_spans) - 1))
    end_idx = max(0, min(excerpt.end_word, len(token_spans) - 1))

    char_start = token_spans[start_idx][0]
    char_end = token_spans[end_idx][1]

    # Extract pre-context: up to CONTEXT_CHARS before char_start
    pre_start = max(0, char_start - CONTEXT_CHARS)
    pre_context = chunk.assembled_text[pre_start:char_start]

    # Extract post-context: up to CONTEXT_CHARS after char_end
    post_end = min(len(chunk.assembled_text), char_end + CONTEXT_CHARS)
    post_context = chunk.assembled_text[char_end:post_end]

    return (pre_context, post_context)


# ═══════════════════════════════════════════════════════════════════
# Filtering
# ═══════════════════════════════════════════════════════════════════

_SELF_CONTAINMENT_FILTER_NAMES = {
    "FULL": SelfContainmentLevel.FULL,
    "PARTIAL": SelfContainmentLevel.PARTIAL,
    "DEPENDENT": SelfContainmentLevel.DEPENDENT,
}


def filter_excerpts(
    excerpts: list[ExcerptRecord],
    *,
    filter_value: Optional[str] = None,
    excerpt_id: Optional[str] = None,
) -> list[ExcerptRecord]:
    """Apply CLI filters to the excerpt list."""
    result = excerpts

    if excerpt_id is not None:
        result = [e for e in result if e.excerpt_id == excerpt_id]
        return result

    if filter_value is not None:
        upper_filter = filter_value.upper()
        # Check if it's a self-containment level
        if upper_filter in _SELF_CONTAINMENT_FILTER_NAMES:
            level = _SELF_CONTAINMENT_FILTER_NAMES[upper_filter]
            result = [e for e in result if e.self_containment == level]
        else:
            # Filter by review_flag or gate_flag
            result = [
                e
                for e in result
                if filter_value in e.review_flags or filter_value in e.gate_flags
            ]

    return result


# ═══════════════════════════════════════════════════════════════════
# Display
# ═══════════════════════════════════════════════════════════════════

_SEPARATOR = "\u2550" * 51  # ═ repeated
_DASH_LINE = "\u2500" * 3  # ─ repeated


def format_excerpt_block(
    excerpt: ExcerptRecord,
    pre_context: str,
    post_context: str,
    chunk_found: bool,
) -> str:
    """Format a single excerpt into a display block."""
    # Takhrij status
    if excerpt.takhrij_data is None:
        takhrij_status = "none"
    elif len(excerpt.takhrij_data) == 0:
        takhrij_status = "empty"
    else:
        takhrij_status = f"{len(excerpt.takhrij_data)} entries"

    # School display
    school_display = excerpt.school if excerpt.school else "null"
    school_conf = (
        f"{excerpt.school_confidence:.2f}"
        if excerpt.school_confidence is not None
        else "null"
    )

    # Topics display
    topics_display = (
        ", ".join(excerpt.excerpt_topic) if excerpt.excerpt_topic else "(none)"
    )

    # Review/gate flags display
    review_flags_display = (
        ", ".join(excerpt.review_flags) if excerpt.review_flags else "(none)"
    )
    gate_flags_display = (
        ", ".join(excerpt.gate_flags) if excerpt.gate_flags else "(none)"
    )

    # Div path display
    div_path_display = " > ".join(excerpt.div_path)

    lines = [
        _SEPARATOR,
        f"EXCERPT: {excerpt.excerpt_id}",
        f"  div_path: {div_path_display}",
        f"  unit_index: {excerpt.unit_index}",
        f"  function: {excerpt.primary_function.value}",
        f"  self_containment: {excerpt.self_containment.value}",
        f"  school: {school_display} (confidence: {school_conf})",
        f"  attribution: {excerpt.primary_author_layer.author_id} "
        f"(rule: {excerpt.primary_author_layer.rule_applied})",
        f"  topics: {topics_display}",
        f"  review_flags: {review_flags_display}",
        f"  gate_flags: {gate_flags_display}",
        f"  scholars: {len(excerpt.quoted_scholars)} "
        f"| evidence: {len(excerpt.evidence_refs)} "
        f"| takhrij: {takhrij_status}",
        "",
    ]

    if not chunk_found:
        lines.append(
            f"{_DASH_LINE} WARNING: chunk not found, "
            f"cannot show context {_DASH_LINE}"
        )
        lines.append("")
        lines.append(f"{_DASH_LINE} PRIMARY TEXT {_DASH_LINE}")
        lines.append(excerpt.primary_text)
    else:
        lines.append(f"{_DASH_LINE} PRE-CONTEXT ({CONTEXT_CHARS} chars) {_DASH_LINE}")
        lines.append(pre_context if pre_context else "(start of chunk)")
        lines.append("")
        lines.append(f"{_DASH_LINE} PRIMARY TEXT {_DASH_LINE}")
        lines.append(excerpt.primary_text)
        lines.append("")
        lines.append(f"{_DASH_LINE} POST-CONTEXT ({CONTEXT_CHARS} chars) {_DASH_LINE}")
        lines.append(post_context if post_context else "(end of chunk)")

    lines.append(_SEPARATOR)
    return "\n".join(lines)


def print_summary(excerpts: list[ExcerptRecord]) -> None:
    """Print aggregate summary counts."""
    total = len(excerpts)
    print(f"Total excerpts: {total}")
    print()

    # Self-containment counts
    print("Self-containment:")
    for level in SelfContainmentLevel:
        count = sum(1 for e in excerpts if e.self_containment == level)
        print(f"  {level.value}: {count}")
    print()

    # Primary function counts
    print("Primary function:")
    func_counts: dict[str, int] = {}
    for e in excerpts:
        key = e.primary_function.value
        func_counts[key] = func_counts.get(key, 0) + 1
    for func_name, count in sorted(func_counts.items(), key=lambda x: -x[1]):
        print(f"  {func_name}: {count}")
    print()

    # Gate flag counts
    print("Gate flags:")
    gate_counts: dict[str, int] = {}
    for e in excerpts:
        for flag in e.gate_flags:
            gate_counts[flag] = gate_counts.get(flag, 0) + 1
    if gate_counts:
        for flag, count in sorted(gate_counts.items(), key=lambda x: -x[1]):
            print(f"  {flag}: {count}")
    else:
        print("  (none)")
    print()

    # Review flag counts
    print("Review flags:")
    review_counts: dict[str, int] = {}
    for e in excerpts:
        for flag in e.review_flags:
            review_counts[flag] = review_counts.get(flag, 0) + 1
    if review_counts:
        for flag, count in sorted(review_counts.items(), key=lambda x: -x[1]):
            print(f"  {flag}: {count}")
    else:
        print("  (none)")


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Review excerpting engine integration test results. "
            "Displays excerpt blocks with surrounding context for "
            "decontextualization spot-check."
        ),
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Integration test run directory containing "
        "excerpts.jsonl and phase1_chunks.json",
    )
    parser.add_argument(
        "--filter",
        dest="filter_value",
        type=str,
        default=None,
        help="Filter by review_flag, gate_flag, or "
        "self_containment level (FULL/PARTIAL/DEPENDENT)",
    )
    parser.add_argument(
        "--excerpt-id",
        type=str,
        default=None,
        help="Show a single excerpt by its excerpt_id",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print aggregate counts instead of individual blocks",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for the review helper CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    run_dir: Path = args.run_dir.resolve()
    if not run_dir.is_dir():
        print(
            f"ERROR: Run directory does not exist: {run_dir}",
            file=sys.stderr,
        )
        return 1

    # Load data
    try:
        excerpts = load_excerpts(run_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not excerpts:
        print("No excerpts found in excerpts.jsonl.", file=sys.stderr)
        return 1

    # Apply filters
    filtered = filter_excerpts(
        excerpts,
        filter_value=args.filter_value,
        excerpt_id=args.excerpt_id,
    )

    if not filtered:
        print("No excerpts match the given filter.", file=sys.stderr)
        return 1

    # Summary mode
    if args.summary:
        print_summary(filtered)
        return 0

    # Load chunks for context display
    try:
        chunks = load_chunks(run_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Display each excerpt
    for excerpt in filtered:
        chunk = find_chunk_for_excerpt(excerpt, chunks)
        if chunk is not None:
            pre_context, post_context = extract_context(excerpt, chunk)
            block = format_excerpt_block(
                excerpt, pre_context, post_context, chunk_found=True
            )
        else:
            print(
                f"WARNING: No chunk found for excerpt "
                f"{excerpt.excerpt_id} (div_id={excerpt.div_id}, "
                f"chunk_index={excerpt.chunk_index})",
                file=sys.stderr,
            )
            block = format_excerpt_block(excerpt, "", "", chunk_found=False)
        print(block)
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
