"""Phase 3: Deterministic Metadata Assembly (SPEC §7.1, §6.2).

Computes 9 deterministic fields (F-DET-1 through F-DET-9) and layer
attribution rules (LA-1 through LA-4) without any LLM call.

These fields survive even if LLM enrichment fails — they are the
minimum viable ExcerptRecord.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from engines.excerpting.contracts import (
    AssembledChunk,
    AssemblyMetadata,
    AuthorAttribution,
    ClassifiedSegment,
    EvidenceRef,
    ExcerptRecord,
    ExcerptingErrorCodes,
    JoinPoint,
    PageRange,
    ScholarAttribution,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
)
from engines.excerpting.src.phase2_classify import _build_token_char_map
from engines.normalization.contracts import (
    Footnote,
    LayerType,
    PhysicalPage,
    TextLayerSegment,
)

logger = logging.getLogger(__name__)

# §7.1 F-DET-5: Quran verse delimiters (ornate parentheses)
# ﴿ = U+FD3F opening, ﴾ = U+FD3E closing
# Capturing group extracts text between delimiters (strips ﴿﴾)
_QURAN_VERSE_RE = re.compile(r"\uFD3F([^\uFD3E]+)\uFD3E")

# §6.2 LA-2: Layer type ordering (highest = outermost)
# TAHQIQ_NOTE > HASHIYAH > SHARH > MATN > UNCERTAIN
_LAYER_LEVEL: dict[LayerType, int] = {
    LayerType.UNCERTAIN: 0,
    LayerType.MATN: 1,
    LayerType.SHARH: 2,
    LayerType.HASHIYAH: 3,
    LayerType.TAHQIQ_NOTE: 4,
}

# §7.1 F-DET-5: Evidence marker lists (DD-S3-8: plain substring, NO word boundaries)
_HADITH_MARKERS: list[str] = [
    "رواه",
    "أخرجه",
    "في الصحيحين",
    "متفق عليه",
    "في صحيح",
    "في سنن",
]

_IJMA_MARKERS: list[str] = [
    "أجمعوا",
    "إجماع",
    "لا خلاف",
    "اتفق العلماء",
    "بالاتفاق",
]


# ═══════════════════════════════════════════════════════════════════
# Shared Helpers
# ═══════════════════════════════════════════════════════════════════


def _word_to_char_range(
    assembled_text: str, start_word: int, end_word: int
) -> tuple[int, int]:
    """Convert word offsets to character range in assembled_text.

    Uses _build_token_char_map from phase2_classify.py (DD-S3-2: do NOT
    duplicate). Returns (char_start, char_end) where char_end is exclusive —
    ``assembled_text[char_start:char_end]`` gives the substring.
    """
    spans = _build_token_char_map(assembled_text)
    char_start = spans[start_word][0]
    char_end = spans[end_word][1]  # Already exclusive — do NOT add +1
    return char_start, char_end


def _compute_layer_coverages(
    text_layers: list[TextLayerSegment],
    char_start: int,
    char_end: int,
    layer_split_points: list[int],
) -> list[tuple[TextLayerSegment, float]]:
    """Merge layers at split points (DD-S3-7) and compute coverage percentages.

    Shared by F-DET-3 (compute_layer_attribution) and F-DET-9
    (compute_quoted_scholars). Avoids duplicating ~15 lines of logic.

    Returns list of (representative_layer, coverage_pct) for layers with
    >0 coverage. The representative_layer is the first segment in each
    merge chain (carries layer_type, author_canonical_id).
    """
    if not text_layers:
        return []

    unit_length = char_end - char_start
    if unit_length <= 0:
        return []

    # Step 1: Merge consecutive segments at split points (DD-S3-7)
    # Two segments merge if same (layer_type, author_canonical_id) AND
    # first.end is in layer_split_points. Handles chains (A-B-C).
    split_set = set(layer_split_points)
    # Each entry: (representative_layer, merged_start, merged_end)
    merged: list[tuple[TextLayerSegment, int, int]] = []

    for layer in text_layers:
        if (
            merged
            and merged[-1][0].layer_type == layer.layer_type
            and merged[-1][0].author_canonical_id == layer.author_canonical_id
            and merged[-1][2] in split_set
            and layer.start == merged[-1][2]  # H-1: adjacency check (DD-S3-7)
        ):
            # Merge: extend previous segment's end
            prev_rep, prev_start, _prev_end = merged[-1]
            merged[-1] = (prev_rep, prev_start, layer.end)
        else:
            merged.append((layer, layer.start, layer.end))

    # Step 2: Compute overlap with unit range
    coverages: list[tuple[TextLayerSegment, float]] = []
    for representative, layer_start, layer_end in merged:
        overlap = max(0, min(layer_end, char_end) - max(layer_start, char_start))
        if overlap > 0:
            coverage = overlap / unit_length
            coverages.append((representative, coverage))

    return coverages


# ═══════════════════════════════════════════════════════════════════
# F-DET-1 through F-DET-9: Deterministic Field Computation
# ═══════════════════════════════════════════════════════════════════


def compute_excerpt_id(
    source_id: str,
    div_id: str,
    chunk_index: int,
    unit_index: int,
) -> str:
    """F-DET-1: Globally unique excerpt identifier (§7.1).

    Format: ``exc_{source_id}_{div_id}_{chunk_index}_{unit_index}``.
    """
    return f"exc_{source_id}_{div_id}_{chunk_index}_{unit_index}"


def extract_primary_text(
    assembled_text: str,
    start_word: int,
    end_word: int,
) -> str:
    """F-DET-2: Extract teaching unit text as a substring (§7.1).

    Uses character-offset substring extraction via _word_to_char_range.
    Preserves all original whitespace (newlines, paragraph breaks).
    This is a substring, NOT a split-and-rejoin — the difference
    matters for I-ER-2.
    """
    char_start, char_end = _word_to_char_range(assembled_text, start_word, end_word)
    return assembled_text[char_start:char_end]


def compute_layer_attribution(
    assembled_text: str,
    text_layers: list[TextLayerSegment],
    start_word: int,
    end_word: int,
    assembly_metadata: AssemblyMetadata,
) -> AuthorAttribution:
    """F-DET-3: Primary author layer attribution (§7.1, §6.2 LA-1-LA-4).

    Rules applied in order: LA-4 -> LA-1 -> LA-2 -> LA-3.
    LA-3 emits EX-M-001 warning for ambiguous attribution.

    assembly_metadata.layer_split_points: split-induced boundaries treated
    as non-meaningful — consecutive segments with same type/author across
    a split point are merged before computing coverage (DD-S3-7).
    """
    char_start, char_end = _word_to_char_range(assembled_text, start_word, end_word)
    coverages = _compute_layer_coverages(
        text_layers, char_start, char_end, assembly_metadata.layer_split_points
    )

    if not coverages:
        # Should not happen given I-AC-2 full coverage guarantee
        raise ValueError(
            "F-DET-3: No layer coverage found for unit range "
            f"[{char_start}, {char_end}). "
            "This violates I-AC-2 (every character attributed to a layer)."
        )

    # Sort by coverage descending
    coverages.sort(key=lambda x: x[1], reverse=True)
    top_layer, top_coverage = coverages[0]

    # LA-4: Any layer has 100% coverage (most specific case, checked first)
    if top_coverage >= 1.0:
        return AuthorAttribution(
            layer_id=top_layer.layer_type.value,
            author_id=top_layer.author_canonical_id or "unknown",
            coverage_pct=top_coverage,
            rule_applied="LA-4",
        )

    # LA-1: Any layer has >=80% coverage
    if top_coverage >= 0.8:
        return AuthorAttribution(
            layer_id=top_layer.layer_type.value,
            author_id=top_layer.author_canonical_id or "unknown",
            coverage_pct=top_coverage,
            rule_applied="LA-1",
        )

    # LA-2: Exactly 2 layers, neither >=80% -> outermost (highest level) wins
    if len(coverages) == 2:
        outermost = max(
            coverages, key=lambda x: _LAYER_LEVEL.get(x[0].layer_type, 0)
        )
        return AuthorAttribution(
            layer_id=outermost[0].layer_type.value,
            author_id=outermost[0].author_canonical_id or "unknown",
            coverage_pct=outermost[1],
            rule_applied="LA-2",
        )

    # LA-3: 3+ layers, none >=80% -> ambiguous, emit EX-M-001
    logger.warning(
        "%s: Attribution ambiguous — %d layers, dominant coverage %.1f%% "
        "(unit chars [%d, %d))",
        ExcerptingErrorCodes.EX_M_001,
        len(coverages),
        top_coverage * 100,
        char_start,
        char_end,
    )
    return AuthorAttribution(
        layer_id=top_layer.layer_type.value,
        author_id=top_layer.author_canonical_id or "unknown",
        coverage_pct=top_coverage,
        rule_applied="LA-3",
    )


def compute_content_types(
    segments: list[ClassifiedSegment],
    unit_segment_indices: list[int],
) -> list[ScholarlyFunction]:
    """F-DET-4: Deduplicated list of scholarly functions in this unit (§7.1).

    Collects scholarly_function from segments whose segment_index is in
    unit_segment_indices. Deduplicates while preserving insertion order.
    """
    seen: set[ScholarlyFunction] = set()
    result: list[ScholarlyFunction] = []
    indices_set = set(unit_segment_indices)
    for seg in segments:
        if seg.segment_index in indices_set and seg.scholarly_function not in seen:
            seen.add(seg.scholarly_function)
            result.append(seg.scholarly_function)
    return result


def detect_evidence_refs(primary_text: str) -> list[EvidenceRef]:
    """F-DET-5: Detect evidence references by pattern matching (§7.1).

    DD-S3-8: All markers use plain substring matching — NO word-boundary
    checks. Arabic proclitic prefixes attach directly to evidence markers,
    making boundary checks catastrophically wrong (up to 76% false negatives).

    Three evidence types: Quran (﴿...﴾), hadith markers, ijma markers.
    See SPEC-NOTE-8 for why this overrides SPEC line 1469.
    """
    results: list[EvidenceRef] = []
    seen_positions: set[tuple[int, str]] = set()  # (position, marker) dedup

    # EV-1: Quran verse delimiters ﴿...﴾
    for match in _QURAN_VERSE_RE.finditer(primary_text):
        extracted = match.group(1)  # Text between delimiters (stripped)
        results.append(
            EvidenceRef(
                type="quran",
                surah=None,  # DD-S3-3: canonical lookup deferred
                ayah_start=None,
                ayah_end=None,
                text_snippet=extracted,
            )
        )

    # EV-2: Hadith markers — plain substring (DD-S3-8)
    for marker in _HADITH_MARKERS:
        pos = 0
        while True:
            pos = primary_text.find(marker, pos)
            if pos == -1:
                break
            key = (pos, marker)
            if key not in seen_positions:
                seen_positions.add(key)
                snippet_start = max(0, pos - 25)
                snippet_end = min(len(primary_text), pos + len(marker) + 25)
                results.append(
                    EvidenceRef(
                        type="hadith",
                        text_snippet=primary_text[snippet_start:snippet_end],
                        marker_text=marker,
                    )
                )
            pos += 1

    # EV-3: Ijma markers — plain substring (DD-S3-8)
    for marker in _IJMA_MARKERS:
        pos = 0
        while True:
            pos = primary_text.find(marker, pos)
            if pos == -1:
                break
            key = (pos, marker)
            if key not in seen_positions:
                seen_positions.add(key)
                snippet_start = max(0, pos - 25)
                snippet_end = min(len(primary_text), pos + len(marker) + 25)
                results.append(
                    EvidenceRef(
                        type="ijma",
                        text_snippet=primary_text[snippet_start:snippet_end],
                        marker_text=marker,
                    )
                )
            pos += 1

    return results


def compute_page_range(
    physical_pages: list[PhysicalPage],
    join_points: list[JoinPoint],
    char_start: int,
    char_end: int,
) -> Optional[PageRange]:
    """F-DET-6: Physical page range for this excerpt (§7.1).

    Maps character range to physical pages using join_points.
    Returns None when physical_pages is empty or all overlapping
    pages have page_number_int=None.
    """
    if not physical_pages:
        return None

    # Single-page fast path (96.8% of cases — no join points)
    if not join_points:
        page = physical_pages[0]
        if page.page_number_int is None:
            return None
        return PageRange(
            volume=page.volume,
            start_page=page.page_number_int,
            end_page=page.page_number_int,
        )

    # Multi-page: build page char ranges from join points
    # N physical pages -> N-1 join points
    offsets = [jp.char_offset_in_assembled for jp in join_points]

    # Find overlapping pages
    # Defensive: clamp to pages addressable by join_points.
    # After the split fix, len(physical_pages) == len(offsets) + 1 always holds.
    # This guard prevents IndexError if a future code path breaks that invariant.
    n_pages = min(len(physical_pages), len(offsets) + 1)
    overlapping_indices: list[int] = []
    for i in range(n_pages):
        # Compute this page's char range
        page_start = offsets[i - 1] if i > 0 else 0
        page_end = offsets[i] if i < len(offsets) else char_end + 1_000_000

        if page_start < char_end and page_end > char_start:
            overlapping_indices.append(i)

    if not overlapping_indices:
        return None

    # Collect page numbers (skip None)
    page_nums: list[int] = []
    first_volume: Optional[int] = None
    for idx in overlapping_indices:
        page = physical_pages[idx]
        if first_volume is None:
            first_volume = page.volume
        if page.page_number_int is not None:
            page_nums.append(page.page_number_int)

    if not page_nums:
        return None

    return PageRange(
        volume=first_volume,
        start_page=min(page_nums),
        end_page=max(page_nums),
    )


def compute_word_offsets(
    start_word: int, end_word: int
) -> tuple[int, int]:
    """Word offsets passthrough (§7.1).

    Exists to make the field-computation pattern uniform.
    This is NOT SPEC F-DET-7 (div_path, handled as chunk passthrough).
    """
    return start_word, end_word


def filter_relevant_footnotes(
    primary_text: str,
    assembled_text: str,
    all_footnotes: list[Footnote],
    char_start: int,
    char_end: int,
) -> list[Footnote]:
    """F-DET-8: Footnotes whose ref markers appear in this unit's range (§7.1).

    Searches assembled_text for ``⌜{ref_marker}⌝`` patterns (U+231C, U+231D).
    Orphaned markers (not found anywhere in assembled_text) are logged as
    warnings but not included.
    """
    result: list[Footnote] = []
    for footnote in all_footnotes:
        pattern = f"\u231C{footnote.ref_marker}\u231D"
        pos = assembled_text.find(pattern)
        if pos == -1:
            logger.warning(
                "Orphaned footnote marker '%s' — not found in assembled_text",
                footnote.ref_marker,
            )
            continue
        if char_start <= pos < char_end:
            result.append(footnote)
    return result


def compute_quoted_scholars(
    text_layers: list[TextLayerSegment],
    unit_char_start: int,
    unit_char_end: int,
    primary_layer: AuthorAttribution,
    assembly_metadata: AssemblyMetadata,
) -> list[ScholarAttribution]:
    """F-DET-9: Non-primary layer authors in this unit's range (§7.1).

    Identifies layers with >0% coverage that are NOT the primary_layer.
    Uses the same layer merging as F-DET-3 via _compute_layer_coverages.

    DD-S3-9: resolved_name uses author_canonical_id as placeholder
    (author_name_arabic field does not exist — see SPEC-NOTE-9).
    """
    coverages = _compute_layer_coverages(
        text_layers,
        unit_char_start,
        unit_char_end,
        assembly_metadata.layer_split_points,
    )

    result: list[ScholarAttribution] = []
    for layer, _coverage in coverages:
        # Skip the primary layer (match on type AND author, not type alone)
        if (layer.layer_type.value == primary_layer.layer_id
                and (layer.author_canonical_id or "unknown") == primary_layer.author_id):
            continue

        # Determine role: MATN in a non-MATN primary unit = classification_frame
        if layer.layer_type == LayerType.MATN and primary_layer.layer_id != "matn":
            role = "classification_frame"
        else:
            role = "quoted_opinion"

        result.append(
            ScholarAttribution(
                mention_text=f"[structural: {layer.layer_type.value}]",
                resolved_name=layer.author_canonical_id,
                role=role,
                confidence=1.0,
                source="layer_overlap",
            )
        )

    return result


# ═══════════════════════════════════════════════════════════════════
# F10: Orchestrator
# ═══════════════════════════════════════════════════════════════════


def build_deterministic_excerpts(
    chunk: AssembledChunk,
    units: list[TeachingUnit],
    segments: list[ClassifiedSegment],
) -> list[ExcerptRecord]:
    """Assemble ExcerptRecords with all deterministic fields populated (§7.1).

    Per-chunk function: processes one AssembledChunk and its TeachingUnits.
    LLM-enriched fields (excerpt_topic, school, takhrij, etc.) are set to
    None/empty — filled by phase3_enrichment.py in Session 4.

    Returns one ExcerptRecord per TeachingUnit.
    """
    chunk_index = chunk.split_info.chunk_index if chunk.split_info else 0
    results: list[ExcerptRecord] = []

    for unit in units:
        # F-DET-1: excerpt_id
        excerpt_id = compute_excerpt_id(
            chunk.source_id, chunk.div_id, chunk_index, unit.unit_index
        )

        # Word -> char conversion (reused by multiple functions below)
        char_start, char_end = _word_to_char_range(
            chunk.assembled_text, unit.start_word, unit.end_word
        )

        # F-DET-2: primary_text (substring, not split-rejoin)
        primary_text = chunk.assembled_text[char_start:char_end]

        # F-DET-3: primary_author_layer
        primary_author_layer = compute_layer_attribution(
            chunk.assembled_text,
            chunk.text_layers,
            unit.start_word,
            unit.end_word,
            chunk.assembly_metadata,
        )

        # F-DET-4: content_types
        content_types = compute_content_types(segments, unit.segment_indices)

        # F-DET-5: evidence_refs
        evidence_refs = detect_evidence_refs(primary_text)

        # F-DET-6: physical_pages
        physical_pages = compute_page_range(
            chunk.physical_pages,
            chunk.assembly_metadata.join_points,
            char_start,
            char_end,
        )

        # F-DET-7: word_offsets (passthrough)
        sw, ew = compute_word_offsets(unit.start_word, unit.end_word)

        # F-DET-8: footnotes_relevant
        footnotes_relevant = filter_relevant_footnotes(
            primary_text,
            chunk.assembled_text,
            chunk.footnotes,
            char_start,
            char_end,
        )

        # F-DET-9: quoted_scholars
        quoted_scholars = compute_quoted_scholars(
            chunk.text_layers,
            char_start,
            char_end,
            primary_author_layer,
            chunk.assembly_metadata,
        )

        # Review flags: PARTIAL/DEPENDENT need "llm_enrichment_failed"
        # to satisfy I-ER-4 model_validator (context_hint=None until Session 4)
        review_flags: list[str] = []
        if unit.self_containment in (
            SelfContainmentLevel.PARTIAL,
            SelfContainmentLevel.DEPENDENT,
        ):
            review_flags = ["llm_enrichment_failed"]

        # Assemble ExcerptRecord with all 33 fields
        record = ExcerptRecord(
            # ── Identification (6) ──
            excerpt_id=excerpt_id,
            source_id=chunk.source_id,
            div_id=chunk.div_id,
            chunk_index=chunk_index,
            unit_index=unit.unit_index,
            div_path=chunk.div_path,
            # ── Text (6) ──
            primary_text=primary_text,
            text_snippet=unit.text_snippet,
            start_word=sw,
            end_word=ew,
            segment_indices=unit.segment_indices,
            physical_pages=physical_pages,
            # ── Classification (4) ──
            primary_function=unit.primary_function,
            secondary_functions=unit.secondary_functions,
            content_types=content_types,
            description_arabic=unit.description_arabic,
            # ── Self-containment (3) ──
            self_containment=unit.self_containment,
            self_containment_notes=unit.self_containment_notes,
            context_hint=None,
            # ── Attribution (5) ──
            primary_author_layer=primary_author_layer,
            attribution_confidence=None,  # DD-S3-6
            quoted_scholars=quoted_scholars,
            school=None,  # DD-S3-1: explicit None (DD8 Pattern 1)
            school_confidence=None,
            # ── Topic/taxonomy (2) ──
            excerpt_topic=[],
            terminology_variants=[],
            # ── Evidence/references (4) ──
            evidence_refs=evidence_refs,
            takhrij_data=None,
            cross_references=[],
            footnotes_relevant=footnotes_relevant,
            # ── Metadata/flags (3) ──
            consensus_metadata=None,
            gate_flags=[],
            review_flags=review_flags,
        )
        results.append(record)

    return results
