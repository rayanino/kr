"""Phase 1: Deterministic Preprocessing (SPEC §4).

Transforms a NormalizedPackage into a list of AssembledChunk objects.
Fully deterministic — no LLM calls, no randomness. Every behavior
is independently unit-testable.

Seven sequential steps:
1. Walk division tree (§4.2)
2. Assemble text (§4.3)
3. Merge tiny divisions (§4.4)
4. Split oversized divisions (§4.5)
5. Aggregate metadata + renumber footnotes (§4.7) — before rebasing
6. Rebase text layers (§4.6) — after footnote renumbering
7. Validate (§4.9)

The heading alignment filter (§4.8) runs during step 2 as a quality flag.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Optional

from engines.excerpting.contracts import (
    AssembledChunk,
    AssemblyMetadata,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    JoinPoint,
    SplitInfo,
    _count_arabic_words,
    validate_ac_invariants,
    validate_layer_coverage,
)
from engines.normalization.contracts import (
    BoundaryContinuity,
    BoundaryContinuityType,
    ContentFlags,
    ContentUnit,
    DivisionNode,
    DivisionType,
    Footnote,
    HeadingConfidence,
    HeadingDetectionMethod,
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
    PhysicalPage,
    TextLayerSegment,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════

# §4.3: Boundary continuity → separator mapping
# mid_sentence uses space (not empty): Shamela page breaks always fall between
# complete words (Arabic print does not split words across pages). Empirically
# verified: 0/294 genuine mid-word splits across all fixture packages.
# See SPEC-NOTE-4 in reference/SPEC_ERRATA.md.
BC_SEPARATOR_MAP: dict[Optional[str], str] = {
    "mid_sentence": " ",
    "mid_paragraph": "\n",
    "mid_argument": "\n",
    "section_break": "\n\n",
    "division_break": "\n\n",
    "unknown": "\n",
    None: "\n",
}

# §4.2: Bibliography/index exclusion keywords (exact-match after noise stripping).
# Expanded list covers compound bibliography headings found in real Shamela exports.
EXCLUDE_KEYWORDS: list[str] = [
    "مصادر", "مراجع", "فهرس", "ثبت المصادر", "المراجع",
    "المصادر", "مصادر ومراجع", "المصادر والمراجع",
    "فهرس المصادر", "فهرس المراجع",
    "قائمة المراجع", "قائمة المصادر", "قائمة المصادر والمراجع",
]

# §4.8: Arabic noise characters for comparison stripping
_ARABIC_NOISE_RE = re.compile(r"[\u064B-\u0652\u0670\u0640\u200C\u200D]")

# §4.7: Footnote marker pattern in primary_text
_FOOTNOTE_MARKER_RE = re.compile(r"⌜([^⌝]+)⌝")

# §4.5: Sentence boundary for last-resort splitting
_SENTENCE_BOUNDARY_RE = re.compile(r"[.؟!]\s")


# ═══════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════


def strip_arabic_noise(text: str) -> str:
    """Strip ZWNJ, ZWJ, diacritics U+064B-0652, superscript alef U+0670,
    and tatweel U+0640 for comparison purposes (§4.8).

    Returns a temporary copy — never modifies the original text.
    """
    result = _ARABIC_NOISE_RE.sub("", text)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def _get_bc_separator(boundary: Optional[BoundaryContinuity]) -> str:
    """Get join separator from a content unit's boundary_continuity (§4.3).

    Returns the separator string based on the boundary type.
    When boundary is None (absent), returns '\\n' (conservative default).
    """
    if boundary is None:
        return BC_SEPARATOR_MAP[None]
    return BC_SEPARATOR_MAP.get(boundary.type.value, "\n")


def _adjust_join_points_after_renumber(
    old_text: str,
    new_text: str,
    join_points: list[JoinPoint],
) -> list[JoinPoint]:
    """Adjust join_point char_offset_in_assembled after footnote renumbering.

    When renumbering changes marker lengths (e.g., ⌜1⌝→⌜10⌝), character
    offsets downstream of the change shift. This recomputes offsets to match
    the renumbered text.

    Returns join_points unchanged if text length didn't change.
    """
    if len(old_text) == len(new_text) or not join_points:
        return join_points

    # Find all marker positions in old and new text
    old_markers = list(_FOOTNOTE_MARKER_RE.finditer(old_text))
    new_markers = list(_FOOTNOTE_MARKER_RE.finditer(new_text))

    # Build cumulative delta table
    # Each entry: (position_in_old_text after this marker, cumulative_shift)
    deltas: list[tuple[int, int]] = []
    cumulative = 0
    for om, nm in zip(old_markers, new_markers):
        delta = (nm.end() - nm.start()) - (om.end() - om.start())
        if delta != 0:
            cumulative += delta
            deltas.append((om.end(), cumulative))

    if not deltas:
        return join_points

    # Adjust each join_point's char_offset_in_assembled
    adjusted: list[JoinPoint] = []
    for jp in join_points:
        shift = 0
        for pos, cum_delta in deltas:
            if jp.char_offset_in_assembled >= pos:
                shift = cum_delta
        if shift != 0:
            adjusted.append(
                JoinPoint(
                    after_unit_index=jp.after_unit_index,
                    before_unit_index=jp.before_unit_index,
                    boundary_type=jp.boundary_type,
                    separator_used=jp.separator_used,
                    char_offset_in_assembled=jp.char_offset_in_assembled + shift,
                )
            )
        else:
            adjusted.append(jp)

    return adjusted


# ═══════════════════════════════════════════════════════════════════
# §4.2 — Division Tree Walking
# ═══════════════════════════════════════════════════════════════════


def find_leaf_divisions(
    division_tree: list[DivisionNode],
) -> list[tuple[DivisionNode, list[str]]]:
    """Walk division tree and return leaf divisions with heading paths (§4.2).

    Returns list of (leaf_node, heading_path) tuples where heading_path
    is the list of heading_text values from root to leaf.

    Volume-type nodes are structural containers — the walk descends into
    their children to reach actual leaf divisions.
    """

    def _walk(
        nodes: list[DivisionNode], path: list[str]
    ) -> list[tuple[DivisionNode, list[str]]]:
        results: list[tuple[DivisionNode, list[str]]] = []
        for node in nodes:
            current_path = path + [node.heading_text]
            if not node.children:
                # Leaf node
                results.append((node, current_path))
            else:
                # Internal node — recurse into children
                results.extend(_walk(node.children, current_path))
        return results

    return _walk(division_tree, [])


def _complete_division_tree(
    nodes: list[DivisionNode],
) -> list[DivisionNode]:
    """Insert synthetic leaf nodes for parent content not covered by children.

    When a parent DivisionNode has children, the children may not cover the
    parent's full [start_unit_index, end_unit_index] range. This is normal
    in Arabic scholarly texts — a chapter (باب) often starts with introductory
    text before its sub-sections (فصول). These uncovered units would cause
    EX-V-001 (uncovered unit indices) in validation.

    This function recursively walks the tree and inserts synthetic leaf nodes
    to fill three types of gap:
    - Preamble: units in [parent.start, first_child.start - 1]
    - Inter-child: units in [child_n.end + 1, child_n+1.start - 1]
    - Trailing: units in [last_child.end + 1, parent.end]

    Empirically, all 5 test packages have ONLY preamble gaps (zero inter-child,
    zero trailing), but inter-child and trailing are handled defensively.

    Synthetic nodes use div_id suffixes (_pre, _gap_N, _post) that cannot
    collide with normalization-generated IDs (format: div_{source_id}_{depth}_{index}).

    Returns a NEW tree. Input nodes are not mutated.
    """
    result: list[DivisionNode] = []
    for node in nodes:
        if not node.children:
            result.append(node)
            continue

        # Recursively complete children first
        completed_children = _complete_division_tree(node.children)

        # Sort children by start_unit_index (defensive — should already be sorted)
        sorted_children = sorted(completed_children, key=lambda c: c.start_unit_index)

        # Determine heading_level for synthetic leaves (same as first child)
        child_level = sorted_children[0].heading_level

        new_children: list[DivisionNode] = []

        # 1. Preamble gap: [parent.start, first_child.start - 1]
        first_child_start = sorted_children[0].start_unit_index
        if node.start_unit_index < first_child_start:
            synthetic = DivisionNode(
                div_id=f"{node.div_id}_pre",
                division_type=DivisionType.MUQADDIMAH,
                heading_text="مقدمة",
                heading_level=child_level,
                start_unit_index=node.start_unit_index,
                end_unit_index=first_child_start - 1,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
                children=[],
            )
            new_children.append(synthetic)

        # 2. Walk through children, inserting inter-child gap synthetics
        for i, child in enumerate(sorted_children):
            new_children.append(child)
            if i < len(sorted_children) - 1:
                next_child = sorted_children[i + 1]
                gap_start = child.end_unit_index + 1
                gap_end = next_child.start_unit_index - 1
                if gap_start <= gap_end:
                    synthetic = DivisionNode(
                        div_id=f"{node.div_id}_gap_{i}",
                        division_type=None,
                        heading_text=node.heading_text,
                        heading_level=child_level,
                        start_unit_index=gap_start,
                        end_unit_index=gap_end,
                        detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                        confidence=HeadingConfidence.HIGH,
                        children=[],
                    )
                    new_children.append(synthetic)

        # 3. Trailing gap: [last_child.end + 1, parent.end]
        last_child_end = sorted_children[-1].end_unit_index
        if last_child_end < node.end_unit_index:
            synthetic = DivisionNode(
                div_id=f"{node.div_id}_post",
                division_type=None,
                heading_text=node.heading_text,
                heading_level=child_level,
                start_unit_index=last_child_end + 1,
                end_unit_index=node.end_unit_index,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
                children=[],
            )
            new_children.append(synthetic)

        # Create new node with updated children (do NOT mutate original)
        result.append(node.model_copy(update={"children": new_children}))

    return result


def should_skip_division(
    node: DivisionNode,
    content_units: list[ContentUnit],
) -> Optional[str]:
    """Check if a leaf division should be skipped (§4.2 skip criteria).

    Returns None if the division should be processed, or a reason string
    if it should be skipped (TOC, index, blank, bibliography, empty range).
    """
    # Empty range check
    if node.start_unit_index > node.end_unit_index:
        logger.warning(
            "%s: empty division range [%d, %d] for %s",
            ExcerptingErrorCodes.EX_A_002,
            node.start_unit_index,
            node.end_unit_index,
            node.div_id,
        )
        return f"{ExcerptingErrorCodes.EX_A_002}: empty range"

    # Get units in range
    units_in_range = [
        cu
        for cu in content_units
        if node.start_unit_index <= cu.unit_index <= node.end_unit_index
    ]

    if not units_in_range:
        logger.warning(
            "%s: no content units in range [%d, %d] for %s",
            ExcerptingErrorCodes.EX_A_002,
            node.start_unit_index,
            node.end_unit_index,
            node.div_id,
        )
        return f"{ExcerptingErrorCodes.EX_A_002}: no content units in range"

    # All-TOC
    if all(cu.content_flags.is_toc_page for cu in units_in_range):
        return "all_toc"

    # All-index
    if all(cu.content_flags.is_index_page for cu in units_in_range):
        return "all_index"

    # All-blank
    if all(cu.content_flags.is_blank for cu in units_in_range):
        return "all_blank"

    # Bibliography keyword
    if _matches_exclude_keyword(node.heading_text):
        return "bibliography_keyword"

    return None


def _matches_exclude_keyword(heading_text: str) -> bool:
    """Check if heading matches bibliography/index exclusion keywords (§4.2).

    Uses exact match after Arabic noise stripping to prevent false positives
    on content chapters like 'مصادر الأحكام' (sources of rulings).
    """
    stripped = strip_arabic_noise(heading_text).strip()
    if not stripped:
        return False
    for keyword in EXCLUDE_KEYWORDS:
        if stripped == strip_arabic_noise(keyword).strip():
            return True
    return False


# ═══════════════════════════════════════════════════════════════════
# §4.3 — Cross-Page Text Assembly
# ═══════════════════════════════════════════════════════════════════


def assemble_text(
    content_units: list[ContentUnit],
    start_unit_index: int,
    end_unit_index: int,
) -> tuple[str, list[JoinPoint], list[int]]:
    """Assemble text from content units in [start, end] inclusive (§4.3).

    Skips content units with is_toc_page, is_index_page, or is_blank.
    Joins using boundary_continuity separator mapping.
    mid_sentence boundaries always use space (SPEC-NOTE-4).
    Preserves all Arabic diacritics exactly.

    Returns:
        assembled_text: The joined text string.
        join_points: One JoinPoint per page boundary within this assembly.
        constituent_unit_indices: All unit_index values in the assembly
            (including skipped units, per I-AC-4).
    """
    cu_map: dict[int, ContentUnit] = {cu.unit_index: cu for cu in content_units}

    # All unit indices in range, including skipped (I-AC-4)
    constituent_unit_indices: list[int] = list(
        range(start_unit_index, end_unit_index + 1)
    )

    parts: list[str] = []
    join_points: list[JoinPoint] = []
    cumulative_offset = 0
    prev_unit: Optional[ContentUnit] = None

    for idx in constituent_unit_indices:
        cu = cu_map.get(idx)
        if cu is None:
            # EX-A-011: content unit not found
            logger.warning(
                "%s: content unit %d not found in content_units list",
                ExcerptingErrorCodes.EX_A_011,
                idx,
            )
            continue

        # Skip TOC/index/blank pages (index already recorded in constituent_unit_indices)
        if (
            cu.content_flags.is_toc_page
            or cu.content_flags.is_index_page
            or cu.content_flags.is_blank
        ):
            continue

        text = cu.primary_text

        if prev_unit is not None:
            # Determine separator from PREVIOUS unit's boundary_continuity
            separator = _get_bc_separator(prev_unit.boundary_continuity)

            # Determine boundary type for the JoinPoint
            bc_type = BoundaryContinuityType.UNKNOWN
            if prev_unit.boundary_continuity is not None:
                bc_type = prev_unit.boundary_continuity.type

            join_points.append(
                JoinPoint(
                    after_unit_index=prev_unit.unit_index,
                    before_unit_index=cu.unit_index,
                    boundary_type=bc_type,
                    separator_used=separator,
                    char_offset_in_assembled=cumulative_offset,
                )
            )

            parts.append(separator)
            cumulative_offset += len(separator)

        parts.append(text)
        cumulative_offset += len(text)
        prev_unit = cu

    assembled_text = "".join(parts)
    return assembled_text, join_points, constituent_unit_indices


# ═══════════════════════════════════════════════════════════════════
# §4.4 — Tiny Division Merging
# ═══════════════════════════════════════════════════════════════════


def _merge_two_chunks(first: AssembledChunk, second: AssembledChunk) -> AssembledChunk:
    """Merge two adjacent sibling chunks into one (§4.4 helper)."""
    separator = "\n\n"
    new_text = first.assembled_text + separator + second.assembled_text
    wc = _count_arabic_words(new_text)
    tt = len(new_text.split())

    # Build merge_history: accumulate all div_ids from both sides
    history: list[str] = []
    if first.merge_history:
        history.extend(first.merge_history)
    else:
        history.append(first.div_id)
    if second.merge_history:
        history.extend(second.merge_history)
    else:
        history.append(second.div_id)

    # Union constituent_unit_indices (sorted, deduplicated)
    indices = sorted(
        set(
            first.assembly_metadata.constituent_unit_indices
            + second.assembly_metadata.constituent_unit_indices
        )
    )

    # Combine join_points: first's + merge boundary + offset-shifted second's
    offset = len(first.assembled_text) + len(separator)
    second_jps = [
        JoinPoint(
            after_unit_index=jp.after_unit_index,
            before_unit_index=jp.before_unit_index,
            boundary_type=jp.boundary_type,
            separator_used=jp.separator_used,
            char_offset_in_assembled=jp.char_offset_in_assembled + offset,
        )
        for jp in second.assembly_metadata.join_points
    ]
    # Add a join point for the merge boundary itself
    first_indices = first.assembly_metadata.constituent_unit_indices
    second_indices = second.assembly_metadata.constituent_unit_indices
    merge_jp = JoinPoint(
        after_unit_index=first_indices[-1] if first_indices else 0,
        before_unit_index=second_indices[0] if second_indices else 0,
        boundary_type=BoundaryContinuityType.SECTION_BREAK,
        separator_used=separator,
        char_offset_in_assembled=len(first.assembled_text),
    )
    jps = list(first.assembly_metadata.join_points) + [merge_jp] + second_jps

    # Placeholder text_layers (will be replaced in steps 5-6)
    placeholder_layers = [
        TextLayerSegment(
            layer_type=LayerType.MATN,
            author_canonical_id=None,
            start=0,
            end=len(new_text),
            confidence=1.0,
        )
    ]

    heading_ok = check_heading_alignment(
        first.div_path[-1] if first.div_path else "",
        new_text,
    )

    return AssembledChunk(
        chunk_id=first.div_id,
        source_id=first.source_id,
        div_id=first.div_id,
        div_path=first.div_path,
        assembled_text=new_text,
        word_count=wc,
        total_tokens=tt,
        text_layers=placeholder_layers,
        footnotes=[],
        content_flags=ContentFlags(),
        physical_pages=[],
        structural_format=first.structural_format,
        heading_alignment_ok=heading_ok,
        assembly_metadata=AssemblyMetadata(
            constituent_unit_indices=indices,
            join_points=jps,
            footnote_renumber_map=None,
        ),
        merge_history=history,
        split_info=None,
    )


def merge_tiny_divisions(
    chunks: list[AssembledChunk],
    parent_div_id: str,
    config: ExcerptingConfig,
) -> list[AssembledChunk]:
    """Merge adjacent sibling chunks below TINY_DIVISION_WORDS (§4.4).

    Operates on chunks that share the same parent in the division tree.
    Merge size guard: combined word count must not exceed OVERSIZED_DIVISION_WORDS.
    I-AC-7: merge_history and split_info are mutually exclusive.

    Returns new list of chunks (merged where applicable).
    """
    if len(chunks) <= 1:
        return list(chunks)

    result = list(chunks)
    changed = True

    while changed:
        changed = False
        i = 0
        while i < len(result):
            chunk = result[i]
            if chunk.word_count >= config.TINY_DIVISION_WORDS:
                i += 1
                continue

            # Try merge with next sibling
            if i + 1 < len(result):
                next_chunk = result[i + 1]
                combined_wc = chunk.word_count + next_chunk.word_count
                if combined_wc <= config.OVERSIZED_DIVISION_WORDS:
                    merged = _merge_two_chunks(chunk, next_chunk)
                    result[i] = merged
                    result.pop(i + 1)
                    changed = True
                    continue  # Re-check merged chunk (might still be tiny)

            # Try merge with previous sibling
            if i > 0:
                prev_chunk = result[i - 1]
                combined_wc = prev_chunk.word_count + chunk.word_count
                if combined_wc <= config.OVERSIZED_DIVISION_WORDS:
                    merged = _merge_two_chunks(prev_chunk, chunk)
                    result[i - 1] = merged
                    result.pop(i)
                    changed = True
                    continue

            # Can't merge (only child or size guard prevents it)
            i += 1

    return result


# ═══════════════════════════════════════════════════════════════════
# §4.5 — Oversized Division Splitting
# ═══════════════════════════════════════════════════════════════════


def _find_split_point(
    chunk: AssembledChunk,
    content_units: list[ContentUnit],
) -> tuple[int, str]:
    """Find best split point for an oversized chunk (§4.5 priority).

    Returns (char_offset, method) where method is one of:
    heading_marker, section_break, paragraph_break, sentence_boundary.
    """
    text = chunk.assembled_text
    midpoint = len(text) // 2

    # Priority 1: Heading markers within the chunk
    cu_map = {cu.unit_index: cu for cu in content_units}
    unit_starts: dict[int, int] = {}
    for jp in chunk.assembly_metadata.join_points:
        unit_starts[jp.before_unit_index] = (
            jp.char_offset_in_assembled + len(jp.separator_used)
        )
    for idx in sorted(chunk.assembly_metadata.constituent_unit_indices):
        cu = cu_map.get(idx)
        if cu is None:
            continue
        if cu.structural_markers.heading_detected and idx in unit_starts:
            offset = unit_starts[idx]
            if 0 < offset < len(text):
                return offset, "heading_marker"

    # Priority 2/3: Section/paragraph breaks ("\n\n") nearest midpoint
    positions: list[int] = []
    search_pos = 0
    while True:
        pos = text.find("\n\n", search_pos)
        if pos == -1:
            break
        positions.append(pos)
        search_pos = pos + 1
    if positions:
        # Split AFTER the "\n\n" — the new chunk starts on fresh content
        best = min(positions, key=lambda p: abs(p - midpoint))
        split_at = best + 2  # after the double newline
        if 0 < split_at < len(text):
            return split_at, "paragraph_break"

    # Priority 4: Sentence boundary nearest midpoint
    matches = list(_SENTENCE_BOUNDARY_RE.finditer(text))
    if matches:
        # Split after the whitespace following terminal punctuation
        sentence_positions = [m.end() for m in matches]
        best_pos = min(sentence_positions, key=lambda p: abs(p - midpoint))
        if 0 < best_pos < len(text):
            return best_pos, "sentence_boundary"

    # Absolute fallback: split at midpoint (should be extremely rare)
    return midpoint, "paragraph_break"


def split_oversized_division(
    chunk: AssembledChunk,
    content_units: list[ContentUnit],
    config: ExcerptingConfig,
) -> list[AssembledChunk]:
    """Split a chunk exceeding OVERSIZED_DIVISION_WORDS at structural boundaries (§4.5).

    Split point priority: heading markers > section breaks > paragraph breaks > sentence boundary.
    Recursive: if a split result still exceeds threshold, split again.

    All chunks from the same split share constituent_unit_indices (I-AC-4).
    Chunk IDs: {div_id}_chunk_0, {div_id}_chunk_1, etc.

    Returns list of chunks (1 if no split needed, >1 if split).
    """
    if chunk.word_count <= config.OVERSIZED_DIVISION_WORDS:
        return [chunk]

    split_offset, method = _find_split_point(chunk, content_units)
    text = chunk.assembled_text

    text_0 = text[:split_offset]
    text_1 = text[split_offset:]

    if not text_0.strip() or not text_1.strip():
        # Degenerate split — can't meaningfully divide
        return [chunk]

    # Split join_points between the two chunks
    jp_0 = [
        jp
        for jp in chunk.assembly_metadata.join_points
        if jp.char_offset_in_assembled < split_offset
    ]
    jp_1 = [
        JoinPoint(
            after_unit_index=jp.after_unit_index,
            before_unit_index=jp.before_unit_index,
            boundary_type=jp.boundary_type,
            separator_used=jp.separator_used,
            char_offset_in_assembled=jp.char_offset_in_assembled - split_offset,
        )
        for jp in chunk.assembly_metadata.join_points
        if jp.char_offset_in_assembled >= split_offset
    ]

    # Determine the base div_id (strip any existing _chunk_N suffix)
    base_div_id = chunk.div_id
    if chunk.split_info is not None:
        base_div_id = chunk.split_info.original_div_id

    shared_indices = chunk.assembly_metadata.constituent_unit_indices

    # Partition physical_pages to match join_point partitioning.
    # jp_0 covers the first N page boundaries → first N+1 pages.
    # The boundary page (index len(jp_0)) is shared between both halves
    # so that teaching units near the split boundary get correct page refs.
    pages_0 = chunk.physical_pages[:len(jp_0) + 1]
    pages_1 = chunk.physical_pages[len(jp_0):]

    # Placeholder layers (replaced during step 6)
    placeholder_0 = [
        TextLayerSegment(
            layer_type=LayerType.MATN,
            author_canonical_id=None,
            start=0,
            end=len(text_0),
            confidence=1.0,
        )
    ]
    placeholder_1 = [
        TextLayerSegment(
            layer_type=LayerType.MATN,
            author_canonical_id=None,
            start=0,
            end=len(text_1),
            confidence=1.0,
        )
    ]

    chunk_0 = AssembledChunk(
        chunk_id=f"{base_div_id}_chunk_0",
        source_id=chunk.source_id,
        div_id=chunk.div_id,
        div_path=chunk.div_path,
        assembled_text=text_0,
        word_count=_count_arabic_words(text_0),
        total_tokens=len(text_0.split()),
        text_layers=placeholder_0,
        footnotes=[],
        content_flags=chunk.content_flags,
        physical_pages=pages_0,
        structural_format=chunk.structural_format,
        heading_alignment_ok=chunk.heading_alignment_ok,
        assembly_metadata=AssemblyMetadata(
            constituent_unit_indices=shared_indices,
            join_points=jp_0,
            layer_split_points=[split_offset],
            footnote_renumber_map=None,
        ),
        merge_history=None,
        split_info=SplitInfo(
            original_div_id=base_div_id,
            chunk_index=0,
            total_chunks=2,
            split_method=method,
        ),
    )
    chunk_1 = AssembledChunk(
        chunk_id=f"{base_div_id}_chunk_1",
        source_id=chunk.source_id,
        div_id=chunk.div_id,
        div_path=chunk.div_path,
        assembled_text=text_1,
        word_count=_count_arabic_words(text_1),
        total_tokens=len(text_1.split()),
        text_layers=placeholder_1,
        footnotes=[],
        content_flags=chunk.content_flags,
        physical_pages=pages_1,
        structural_format=chunk.structural_format,
        heading_alignment_ok=chunk.heading_alignment_ok,
        assembly_metadata=AssemblyMetadata(
            constituent_unit_indices=shared_indices,
            join_points=jp_1,
            layer_split_points=[],
            footnote_renumber_map=None,
        ),
        merge_history=None,
        split_info=SplitInfo(
            original_div_id=base_div_id,
            chunk_index=1,
            total_chunks=2,
            split_method=method,
        ),
    )

    # Recursive split if either half is still oversized
    results: list[AssembledChunk] = []
    for c in [chunk_0, chunk_1]:
        if c.word_count > config.OVERSIZED_DIVISION_WORDS:
            results.extend(split_oversized_division(c, content_units, config))
        else:
            results.append(c)

    # Renumber chunk_ids and update split_info sequentially
    total = len(results)
    renumbered: list[AssembledChunk] = []
    for i, c in enumerate(results):
        assert c.split_info is not None
        renumbered.append(
            c.model_copy(
                update={
                    "chunk_id": f"{base_div_id}_chunk_{i}",
                    "split_info": SplitInfo(
                        original_div_id=base_div_id,
                        chunk_index=i,
                        total_chunks=total,
                        split_method=c.split_info.split_method,
                    ),
                }
            )
        )

    return renumbered


# ═══════════════════════════════════════════════════════════════════
# §4.7 — Content Flag and Footnote Aggregation
# ═══════════════════════════════════════════════════════════════════


def aggregate_content_flags(
    content_units: list[ContentUnit],
    unit_indices: list[int],
) -> ContentFlags:
    """OR-aggregate content_flags across constituent content units (§4.7).

    If any unit has has_verse=True, the result has has_verse=True. Same for all boolean flags.
    """
    cu_map: dict[int, ContentUnit] = {cu.unit_index: cu for cu in content_units}

    has_verse = False
    has_table = False
    has_quran = False
    has_hadith = False
    is_toc = False
    is_index = False
    is_blank = False

    for idx in unit_indices:
        cu = cu_map.get(idx)
        if cu is None:
            continue
        flags = cu.content_flags
        has_verse = has_verse or flags.has_verse
        has_table = has_table or flags.has_table
        has_quran = has_quran or flags.has_quran_citation
        has_hadith = has_hadith or flags.has_hadith_citation
        is_toc = is_toc or flags.is_toc_page
        is_index = is_index or flags.is_index_page
        is_blank = is_blank or flags.is_blank

    return ContentFlags(
        has_verse=has_verse,
        has_table=has_table,
        has_quran_citation=has_quran,
        has_hadith_citation=has_hadith,
        is_toc_page=is_toc,
        is_index_page=is_index,
        is_blank=is_blank,
    )


def aggregate_footnotes(
    content_units: list[ContentUnit],
    unit_indices: list[int],
) -> list[Footnote]:
    """Collect ALL footnotes from constituent content units in order (§4.7).

    Collects every footnote without deduplication — collision resolution
    (renumbering + dedup) is handled by renumber_footnotes().
    """
    cu_map: dict[int, ContentUnit] = {cu.unit_index: cu for cu in content_units}
    result: list[Footnote] = []
    for idx in sorted(unit_indices):
        cu = cu_map.get(idx)
        if cu is None:
            continue
        result.extend(cu.footnotes)
    return result


def renumber_footnotes(
    assembled_text: str,
    footnotes: list[Footnote],
) -> tuple[str, list[Footnote], Optional[dict[str, str]]]:
    """Renumber footnote markers if collisions exist (§4.7).

    When footnote ref_markers collide across pages (two pages both have ⌜1⌝),
    renumbers sequentially by order of first appearance in the assembled text.
    Updates both ⌜N⌝ markers in assembled_text and ref_marker in footnotes.

    CRITICAL: This modifies assembled_text (changing character offsets).
    Must run BEFORE text layer rebasing (§4.1 step ordering).

    Returns:
        new_text: The text with renumbered markers (or original if no collisions).
        new_footnotes: Footnotes with updated ref_markers.
        renumber_map: old→new mapping, or None if no renumbering needed.
    """
    if not footnotes:
        return assembled_text, footnotes, None

    matches = list(_FOOTNOTE_MARKER_RE.finditer(assembled_text))
    if not matches:
        return assembled_text, footnotes, None

    # Check for collisions (any marker appearing more than once in text)
    text_markers = [m.group(1) for m in matches]
    if len(text_markers) == len(set(text_markers)):
        # All unique — no renumbering needed. Dedup footnotes by ref_marker.
        seen: set[str] = set()
        deduped: list[Footnote] = []
        for fn in footnotes:
            if fn.ref_marker in seen:
                logger.warning(
                    "%s: duplicate footnote ref_marker '%s' (keeping first)",
                    ExcerptingErrorCodes.EX_A_005,
                    fn.ref_marker,
                )
                continue
            seen.add(fn.ref_marker)
            deduped.append(fn)
        return assembled_text, deduped, None

    # Build footnote queues by ref_marker (preserving order for each marker)
    fn_queues: dict[str, list[Footnote]] = {}
    for fn in footnotes:
        fn_queues.setdefault(fn.ref_marker, []).append(fn)

    # Sequential renumbering by order of appearance in text
    renumber_map: dict[str, str] = {}
    replacements: list[tuple[int, int, str]] = []
    new_footnotes: list[Footnote] = []
    seen_new: set[str] = set()

    for i, match in enumerate(matches):
        old_marker = match.group(1)
        new_marker = str(i + 1)

        replacements.append((match.start(), match.end(), f"⌜{new_marker}⌝"))

        # Record mapping for traceability (first change per old marker)
        if old_marker != new_marker and old_marker not in renumber_map:
            renumber_map[old_marker] = new_marker

        # Pop corresponding footnote from queue
        queue = fn_queues.get(old_marker, [])
        if queue:
            fn = queue.pop(0)
            if new_marker not in seen_new:
                new_footnotes.append(fn.model_copy(update={"ref_marker": new_marker}))
                seen_new.add(new_marker)
            else:
                logger.warning(
                    "%s: duplicate ref_marker '%s' after renumbering",
                    ExcerptingErrorCodes.EX_A_005,
                    new_marker,
                )

    # Replace markers from end to start (preserves character offsets)
    new_text = assembled_text
    for start, end, replacement in reversed(replacements):
        new_text = new_text[:start] + replacement + new_text[end:]

    return new_text, new_footnotes, renumber_map if renumber_map else None


def collect_physical_pages(
    content_units: list[ContentUnit],
    unit_indices: list[int],
) -> list[PhysicalPage]:
    """Collect PhysicalPage records from constituent content units in order (§4.7)."""
    cu_map: dict[int, ContentUnit] = {cu.unit_index: cu for cu in content_units}
    result: list[PhysicalPage] = []
    for idx in sorted(unit_indices):
        cu = cu_map.get(idx)
        if cu is None:
            continue
        result.append(cu.physical_page)
    return result


# ═══════════════════════════════════════════════════════════════════
# §4.6 — Text Layer Rebasing
# ═══════════════════════════════════════════════════════════════════


def rebase_text_layers(
    content_units: list[ContentUnit],
    unit_indices: list[int],
    join_points: list[JoinPoint],
    assembled_text_len: int,
) -> list[TextLayerSegment]:
    """Translate per-page text_layers to assembled-text coordinates (§4.6).

    For each content unit, adds the cumulative character offset (including
    separators) to each layer segment's start and end values.

    After rebasing, merges adjacent segments with same layer_type and
    author_canonical_id.

    Clamps segments exceeding their content unit's text length (EX-A-004).

    Validates I-AC-2: union of segments covers [0, assembled_text_len) exactly.
    Emits EX-A-003 on failure.
    """
    if assembled_text_len == 0:
        return []

    cu_map: dict[int, ContentUnit] = {cu.unit_index: cu for cu in content_units}

    # Build offset map from join_points: unit_index → base_char_offset
    offset_map: dict[int, int] = {}

    # Derive offsets from join_points
    if join_points:
        for jp in sorted(join_points, key=lambda j: j.char_offset_in_assembled):
            offset_map[jp.before_unit_index] = (
                jp.char_offset_in_assembled + len(jp.separator_used)
            )

    # First non-skipped unit starts at offset 0
    for idx in sorted(unit_indices):
        cu = cu_map.get(idx)
        if cu is None:
            continue
        if (
            cu.content_flags.is_toc_page
            or cu.content_flags.is_index_page
            or cu.content_flags.is_blank
        ):
            continue
        if idx not in offset_map:
            offset_map[idx] = 0
        break

    # Build ordered list of (unit_index, base_offset) for non-skipped units
    unit_offsets: list[tuple[int, int]] = []
    for idx in sorted(unit_indices):
        if idx in offset_map:
            cu = cu_map.get(idx)
            if cu is None:
                continue
            if (
                cu.content_flags.is_toc_page
                or cu.content_flags.is_index_page
                or cu.content_flags.is_blank
            ):
                continue
            unit_offsets.append((idx, offset_map[idx]))

    # Compute the "coverage end" for each unit: extends to the next unit's start
    # (covers the separator gap). Last unit extends to assembled_text_len.
    coverage_end_map: dict[int, int] = {}
    for i, (idx, base) in enumerate(unit_offsets):
        if i + 1 < len(unit_offsets):
            coverage_end_map[idx] = unit_offsets[i + 1][1]
        else:
            coverage_end_map[idx] = assembled_text_len

    # Rebase each unit's layers
    rebased: list[TextLayerSegment] = []
    for idx, base in unit_offsets:
        cu = cu_map[idx]
        text_len = len(cu.primary_text)
        unit_coverage_end = coverage_end_map[idx]

        for j, seg in enumerate(cu.text_layers):
            # Clamp overflow (EX-A-004)
            clamped_end = seg.end
            if seg.end > text_len:
                logger.warning(
                    "%s: layer segment end %d > text length %d for unit %d, clamping",
                    ExcerptingErrorCodes.EX_A_004,
                    seg.end,
                    text_len,
                    idx,
                )
                clamped_end = text_len

            new_start = seg.start + base
            new_end = clamped_end + base

            # Last segment of the unit: extend to cover separator gap
            is_last_seg = j == len(cu.text_layers) - 1
            if is_last_seg and new_end < unit_coverage_end:
                new_end = unit_coverage_end

            # Clip to assembled_text bounds
            if new_start >= assembled_text_len:
                continue
            new_end = min(new_end, assembled_text_len)

            rebased.append(
                TextLayerSegment(
                    layer_type=seg.layer_type,
                    author_canonical_id=seg.author_canonical_id,
                    start=new_start,
                    end=new_end,
                    confidence=seg.confidence,
                )
            )

    # Merge adjacent segments with same layer_type + author_canonical_id
    rebased.sort(key=lambda s: s.start)
    merged: list[TextLayerSegment] = []
    for seg in rebased:
        if (
            merged
            and merged[-1].end == seg.start
            and merged[-1].layer_type == seg.layer_type
            and merged[-1].author_canonical_id == seg.author_canonical_id
        ):
            merged[-1] = TextLayerSegment(
                layer_type=merged[-1].layer_type,
                author_canonical_id=merged[-1].author_canonical_id,
                start=merged[-1].start,
                end=seg.end,
                confidence=min(merged[-1].confidence, seg.confidence),
            )
        else:
            merged.append(seg)

    # EX-A-003: Detect and repair small gaps in layer coverage
    # SPEC §4.6 + §8.1: gaps ≤5 chars → repair (extend previous end), WARNING
    # gaps >5 chars → leave for validate_layer_coverage to Fatal
    if merged:
        repaired: list[TextLayerSegment] = [merged[0]]
        for i in range(1, len(merged)):
            gap = merged[i].start - repaired[-1].end
            if gap > 0 and gap <= 5:
                # Small gap — repair by extending previous segment
                logger.warning(
                    "%s: small gap of %d chars at position %d-%d between segments "
                    "(repaired by extending previous segment). This may indicate "
                    "rounding in normalization layer offsets.",
                    ExcerptingErrorCodes.EX_A_003,
                    gap,
                    repaired[-1].end,
                    merged[i].start,
                )
                repaired[-1] = TextLayerSegment(
                    layer_type=repaired[-1].layer_type,
                    author_canonical_id=repaired[-1].author_canonical_id,
                    start=repaired[-1].start,
                    end=merged[i].start,  # extend to close gap
                    confidence=repaired[-1].confidence,
                )
                repaired.append(merged[i])
            elif gap > 5:
                # Large gap — log but leave for validate_layer_coverage to catch
                logger.error(
                    "%s: large gap of %d chars at position %d-%d between segments "
                    "(too large to repair, will fail I-AC-2 validation).",
                    ExcerptingErrorCodes.EX_A_003,
                    gap,
                    repaired[-1].end,
                    merged[i].start,
                )
                repaired.append(merged[i])
            else:
                repaired.append(merged[i])
        merged = repaired

    # Validate I-AC-2 coverage
    validate_layer_coverage(merged, assembled_text_len)

    return merged


# ═══════════════════════════════════════════════════════════════════
# §4.8 — Heading Alignment Filter
# ═══════════════════════════════════════════════════════════════════


def check_heading_alignment(
    heading_text: str,
    assembled_text: str,
) -> bool:
    """Check if division heading aligns with assembled text (§4.8).

    Strips Arabic noise from both, then checks if first 30 stripped chars
    of heading appear within first 200 stripped chars of assembled text.

    Returns True if aligned, False otherwise (emits EX-A-006 warning).
    """
    stripped_heading = strip_arabic_noise(heading_text)[:30]
    stripped_text = strip_arabic_noise(assembled_text)[:200]

    if not stripped_heading:
        return True  # Nothing to check — vacuously aligned

    if stripped_heading in stripped_text:
        return True

    logger.warning(
        "%s: heading '%s' does not align with assembled text start",
        ExcerptingErrorCodes.EX_A_006,
        heading_text[:50],
    )
    return False


# ═══════════════════════════════════════════════════════════════════
# §4.9 — Phase 1 Self-Validation
# ═══════════════════════════════════════════════════════════════════


def validate_phase1(
    chunks: list[AssembledChunk],
    manifest: NormalizedManifest,
    skipped_divisions: dict[str, str],
    config: ExcerptingConfig,
    completed_tree: list[DivisionNode] | None = None,
) -> list[dict]:
    """Run V-P1-1 through V-P1-6 validation checks (§4.9).

    V-P1-1: Division coverage (every leaf → chunk or explicit skip). Fatal.
    V-P1-2: Content unit coverage (all units accounted for). Fatal.
    V-P1-3: No empty chunks (word_count > 0). Warning.
    V-P1-4: No oversized chunks. Warning.
    V-P1-5: Layer coverage (I-AC-2 for each chunk). Fatal.
    V-P1-6: Word count consistency (I-AC-1 for each chunk). Fatal.

    Returns list of validation result dicts with 'check', 'status', 'detail'.
    Raises on fatal failures if any.
    """
    results: list[dict] = []
    fatal_failures: list[str] = []

    # V-P1-1: Division coverage
    tree = completed_tree if completed_tree is not None else _complete_division_tree(manifest.division_tree)
    all_leaves = find_leaf_divisions(tree)
    all_leaf_ids = {node.div_id for node, _ in all_leaves}

    # Collect div_ids covered by chunks (including merge_history and split_info)
    covered_div_ids: set[str] = set()
    for chunk in chunks:
        covered_div_ids.add(chunk.div_id)
        if chunk.merge_history:
            covered_div_ids.update(chunk.merge_history)
        if chunk.split_info:
            covered_div_ids.add(chunk.split_info.original_div_id)

    skipped_ids = set(skipped_divisions.keys())
    missing_divs = all_leaf_ids - covered_div_ids - skipped_ids
    if missing_divs:
        detail = f"Missing divisions: {missing_divs}"
        results.append({"check": "V-P1-1", "status": "fail", "detail": detail})
        fatal_failures.append(detail)
    else:
        results.append(
            {"check": "V-P1-1", "status": "pass", "detail": "All divisions covered"}
        )

    # V-P1-2: Content unit coverage
    all_unit_indices: set[int] = set()
    for chunk in chunks:
        all_unit_indices.update(chunk.assembly_metadata.constituent_unit_indices)

    # Units belonging to skipped divisions
    skipped_unit_indices: set[int] = set()
    for node, _ in all_leaves:
        if node.div_id in skipped_ids:
            for idx in range(node.start_unit_index, node.end_unit_index + 1):
                skipped_unit_indices.add(idx)

    expected = set(range(manifest.total_content_units))
    uncovered = expected - all_unit_indices - skipped_unit_indices
    if uncovered:
        detail = f"Uncovered unit indices: {sorted(uncovered)[:10]}..."
        results.append({"check": "V-P1-2", "status": "fail", "detail": detail})
        fatal_failures.append(detail)
    else:
        results.append(
            {"check": "V-P1-2", "status": "pass", "detail": "All units covered"}
        )

    # V-P1-3: No empty chunks (warning)
    empty_chunks = [c.chunk_id for c in chunks if c.word_count == 0]
    if empty_chunks:
        results.append(
            {
                "check": "V-P1-3",
                "status": "warning",
                "detail": f"Empty chunks: {empty_chunks}",
            }
        )
    else:
        results.append(
            {"check": "V-P1-3", "status": "pass", "detail": "No empty chunks"}
        )

    # V-P1-4: No oversized chunks (warning)
    oversized = [
        c.chunk_id
        for c in chunks
        if c.word_count > config.OVERSIZED_DIVISION_WORDS
    ]
    if oversized:
        results.append(
            {
                "check": "V-P1-4",
                "status": "warning",
                "detail": f"Oversized chunks: {oversized}",
            }
        )
    else:
        results.append(
            {"check": "V-P1-4", "status": "pass", "detail": "No oversized chunks"}
        )

    # V-P1-5: Layer coverage (fatal)
    layer_failures: list[str] = []
    for chunk in chunks:
        try:
            validate_layer_coverage(chunk.text_layers, len(chunk.assembled_text))
        except ValueError as e:
            layer_failures.append(f"{chunk.chunk_id}: {e}")
    if layer_failures:
        detail = f"Layer coverage failures: {layer_failures}"
        results.append({"check": "V-P1-5", "status": "fail", "detail": detail})
        fatal_failures.append(detail)
    else:
        results.append(
            {"check": "V-P1-5", "status": "pass", "detail": "All layers valid"}
        )

    # V-P1-6: Word count consistency (fatal)
    wc_failures: list[str] = []
    for chunk in chunks:
        try:
            validate_ac_invariants(chunk)
        except ValueError as e:
            wc_failures.append(f"{chunk.chunk_id}: {e}")
    if wc_failures:
        detail = f"Word count failures: {wc_failures}"
        results.append({"check": "V-P1-6", "status": "fail", "detail": detail})
        fatal_failures.append(detail)
    else:
        results.append(
            {"check": "V-P1-6", "status": "pass", "detail": "All counts consistent"}
        )

    # Raise on fatal
    if fatal_failures:
        raise ValueError(
            f"{ExcerptingErrorCodes.EX_V_001}: Phase 1 validation failed: "
            + "; ".join(fatal_failures)
        )

    return results


# ═══════════════════════════════════════════════════════════════════
# Private Helpers
# ═══════════════════════════════════════════════════════════════════


def _build_parent_map(
    nodes: list[DivisionNode], parent_id: str = "root"
) -> dict[str, str]:
    """Map each leaf div_id to its parent node's div_id."""
    result: dict[str, str] = {}
    for node in nodes:
        if not node.children:
            result[node.div_id] = parent_id
        else:
            result.update(_build_parent_map(node.children, node.div_id))
    return result


def _slice_layers_for_split(
    full_layers: list[TextLayerSegment],
    chunk_start: int,
    chunk_end: int,
) -> tuple[list[TextLayerSegment], list[int]]:
    """Slice full-text rebased layers for a split chunk's text range.

    Returns (sliced_layers, layer_split_points) where layer_split_points
    records offsets (in chunk coordinates) where segments were artificially divided.
    """
    sliced: list[TextLayerSegment] = []
    split_points: list[int] = []

    for seg in full_layers:
        if seg.end <= chunk_start or seg.start >= chunk_end:
            continue  # Fully outside this chunk

        new_start = max(seg.start, chunk_start) - chunk_start
        new_end = min(seg.end, chunk_end) - chunk_start

        # Detect if segment was split at chunk boundary
        if seg.start < chunk_start:
            split_points.append(0)
        if seg.end > chunk_end:
            split_points.append(new_end)

        sliced.append(
            TextLayerSegment(
                layer_type=seg.layer_type,
                author_canonical_id=seg.author_canonical_id,
                start=new_start,
                end=new_end,
                confidence=seg.confidence,
            )
        )

    return sliced, split_points


# ═══════════════════════════════════════════════════════════════════
# Top-Level Orchestrator
# ═══════════════════════════════════════════════════════════════════


def run_phase1(
    package: NormalizedPackage,
    config: ExcerptingConfig,
) -> tuple[list[AssembledChunk], list[dict]]:
    """Execute Phase 1: deterministic preprocessing (§4.1).

    Steps (in order):
    1. Walk division tree → identify leaves
    2. For each leaf: assemble text, check heading alignment
    3. Merge tiny divisions (per parent group)
    4. Aggregate metadata + renumber footnotes (modifies assembled_text)
    5. Split oversized divisions (on final text)
    6. Rebase text layers (on final assembled_text)
    7. Validate (V-P1-1 through V-P1-6)

    Returns:
        chunks: list of AssembledChunk objects ready for Phase 2.
        validation_results: list of validation check results.

    Raises ValueError on fatal validation failure.
    """
    manifest = package.manifest
    content_units = package.content_units

    # ── Step 0: Complete division tree (handle preamble gaps) ─────
    completed_tree = _complete_division_tree(manifest.division_tree)

    # ── Step 1: Walk division tree ────────────────────────────────
    leaves = find_leaf_divisions(completed_tree)

    if not leaves:
        logger.warning(
            "%s: no leaf divisions found in division tree", ExcerptingErrorCodes.EX_A_010
        )
        return [], [
            {
                "check": "V-P1-1",
                "status": "skip",
                "detail": f"{ExcerptingErrorCodes.EX_A_010}: empty division tree",
            }
        ]

    # ── Step 2: Assemble text per leaf ────────────────────────────
    skipped_divisions: dict[str, str] = {}
    proto_chunks: list[AssembledChunk] = []

    for node, heading_path in leaves:
        skip_reason = should_skip_division(node, content_units)
        if skip_reason is not None:
            skipped_divisions[node.div_id] = skip_reason
            logger.info("Skipping division %s: %s", node.div_id, skip_reason)
            continue

        text, join_points, unit_indices = assemble_text(
            content_units, node.start_unit_index, node.end_unit_index
        )

        if not text.strip():
            skipped_divisions[node.div_id] = "empty_assembled_text"
            continue

        # F-1: Synthetic preamble/gap/post nodes have assigned headings that
        # won't appear in assembled text — skip alignment check (not a real mismatch)
        if node.div_id.endswith("_pre") or "_gap_" in node.div_id or node.div_id.endswith("_post"):
            heading_ok = True
        else:
            heading_ok = check_heading_alignment(node.heading_text, text)
        wc = _count_arabic_words(text)
        tt = len(text.split())

        # Proto-chunk with placeholder layers (replaced in steps 4-6)
        chunk = AssembledChunk(
            chunk_id=node.div_id,
            source_id=manifest.source_id,
            div_id=node.div_id,
            div_path=heading_path,
            assembled_text=text,
            word_count=wc,
            total_tokens=tt,
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(text),
                    confidence=1.0,
                )
            ],
            footnotes=[],
            content_flags=ContentFlags(),
            physical_pages=[],
            structural_format=manifest.structural_format,
            heading_alignment_ok=heading_ok,
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=unit_indices,
                join_points=join_points,
                footnote_renumber_map=None,
            ),
            merge_history=None,
            split_info=None,
        )
        proto_chunks.append(chunk)

    if not proto_chunks:
        # All divisions skipped
        return [], validate_phase1([], manifest, skipped_divisions, config, completed_tree=completed_tree)

    # ── Step 3: Merge tiny divisions (grouped by parent) ──────────
    parent_map = _build_parent_map(completed_tree)
    groups: dict[str, list[AssembledChunk]] = defaultdict(list)
    for chunk in proto_chunks:
        pid = parent_map.get(chunk.div_id, "root")
        groups[pid].append(chunk)

    merged_chunks: list[AssembledChunk] = []
    for pid, group in groups.items():
        merged_chunks.extend(merge_tiny_divisions(group, pid, config))

    # ── Step 4: Aggregate metadata + renumber footnotes ───────────
    # (BEFORE split — renumbering changes text offsets)
    # Save original join_points for split chunk layer rebasing
    original_join_points: dict[str, list[JoinPoint]] = {}
    finalized: list[AssembledChunk] = []

    for chunk in merged_chunks:
        indices = chunk.assembly_metadata.constituent_unit_indices
        flags = aggregate_content_flags(content_units, indices)
        all_fn = aggregate_footnotes(content_units, indices)

        # Filter footnotes to only those whose markers appear in this chunk's text
        chunk_fn = [
            fn for fn in all_fn if f"⌜{fn.ref_marker}⌝" in chunk.assembled_text
        ]

        new_text, new_fn, rmap = renumber_footnotes(chunk.assembled_text, chunk_fn)

        # F-1 fix: adjust join_points for renumbering-induced offset shifts
        adjusted_jps = _adjust_join_points_after_renumber(
            chunk.assembled_text, new_text,
            chunk.assembly_metadata.join_points,
        )

        # Save ADJUSTED join_points for split chunk layer rebasing (step 6)
        original_join_points[chunk.div_id] = adjusted_jps

        pages = collect_physical_pages(content_units, indices)
        wc = _count_arabic_words(new_text)
        tt = len(new_text.split())

        finalized.append(
            chunk.model_copy(
                update={
                    "assembled_text": new_text,
                    "word_count": wc,
                    "total_tokens": tt,
                    "footnotes": new_fn,
                    "content_flags": flags,
                    "physical_pages": pages,
                    "assembly_metadata": chunk.assembly_metadata.model_copy(
                        update={
                            "footnote_renumber_map": rmap,
                            "join_points": adjusted_jps,  # F-1 fix
                        }
                    ),
                }
            )
        )

    # ── Step 5: Split oversized divisions ─────────────────────────
    split_results: list[AssembledChunk] = []
    for chunk in finalized:
        split_results.extend(
            split_oversized_division(chunk, content_units, config)
        )

    # ── Step 6: Rebase text layers ────────────────────────────────
    # Group split chunks by original_div_id for coordinated rebasing
    split_groups: dict[str, list[tuple[int, AssembledChunk]]] = defaultdict(list)
    unsplit_indices: list[int] = []
    for i, chunk in enumerate(split_results):
        if chunk.split_info is not None:
            split_groups[chunk.split_info.original_div_id].append((i, chunk))
        else:
            unsplit_indices.append(i)

    # Unsplit chunks: normal rebasing
    for i in unsplit_indices:
        chunk = split_results[i]
        layers = rebase_text_layers(
            content_units,
            chunk.assembly_metadata.constituent_unit_indices,
            chunk.assembly_metadata.join_points,
            len(chunk.assembled_text),
        )
        split_results[i] = chunk.model_copy(update={"text_layers": layers})

    # Split chunks: rebase full original text, then slice per chunk
    for orig_div_id, group in split_groups.items():
        group.sort(key=lambda x: x[1].split_info.chunk_index)  # type: ignore[union-attr]
        first_chunk = group[0][1]
        full_indices = first_chunk.assembly_metadata.constituent_unit_indices

        # Use original (pre-split) join_points for full-text rebasing
        full_jp = original_join_points.get(orig_div_id, [])
        full_text_len = sum(len(c.assembled_text) for _, c in group)

        # Rebase layers for the FULL original text
        full_layers = rebase_text_layers(
            content_units, full_indices, full_jp, full_text_len
        )

        # Slice per chunk
        offset = 0
        for idx, chunk in group:
            chunk_len = len(chunk.assembled_text)
            sliced, split_pts = _slice_layers_for_split(
                full_layers, offset, offset + chunk_len
            )

            # Filter footnotes for this split chunk's text
            chunk_fn = [
                fn
                for fn in chunk.footnotes
                if f"⌜{fn.ref_marker}⌝" in chunk.assembled_text
            ]

            split_results[idx] = chunk.model_copy(
                update={
                    "text_layers": sliced,
                    "footnotes": chunk_fn,
                    "assembly_metadata": chunk.assembly_metadata.model_copy(
                        update={"layer_split_points": split_pts}
                    ),
                }
            )
            offset += chunk_len

    # ── Step 7: Validate ──────────────────────────────────────────
    validation_results = validate_phase1(
        split_results, manifest, skipped_divisions, config,
        completed_tree=completed_tree,
    )

    return split_results, validation_results
