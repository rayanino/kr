"""Multi-layer text detection — SPEC §4.A.5 Pass 5.

Detects which portions of each page belong to which author layer
(matn/sharh/hashiyah/tahqiq_note) using typographic signals from
Shamela HTML: bold spans, transition markers, and bracket regions.

Architecture:
  1. Leaf functions extract raw signals (bold → primary_text offsets,
     transition markers, bracket regions)
  2. _classify_bold_signal applies the SPEC two-factor test
  3. _build_segments merges all signals via an event-based state machine
     with marker_state tracking for open-ended marker persistence
  4. detect_layers orchestrates per-page detection
  5. _build_layer_map aggregates across all pages

SPEC reference: §4.A.5 (multi-layer detection), §4.A.2 Pass 5
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

from engines.normalization.contracts import LayerMapEntry, LayerType, TextLayerSegment
from engines.normalization.src.errors import NormErrorCode
from engines.normalization.src.normalizers.shamela import (
    CleanedPage,
    decode_entities,
    normalize_whitespace,
    strip_tags,
)
from engines.source.contracts import SourceMetadata

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════


@dataclass
class _MarkerPattern:
    """A transition marker pattern for layer detection.

    Used by both _detect_transition_markers (regex scanning) and
    _classify_bold_signal (plain-text marker-in-bold check).
    """

    regex: re.Pattern[str]
    target_layer: Optional[LayerType]  # None → resolved to default_commentary_layer
    confidence: float
    plain_texts: list[str]  # for marker-in-bold text search


# Shared constant: transition marker patterns (§4.A.5).
# Both _detect_transition_markers and _classify_bold_signal use this list.
# "أقول:" is intentionally NOT included — it confirms current layer's
# author speaking, not a layer transition (SPEC §4.A.5).
#
# L-004 fix: Arabic conjunction prefixes (و, ف) are optionally matched
# before markers. These attach directly without whitespace, e.g.:
# "وقال المصنف:" → same as "قال المصنف:"
# "فقوله:" → same as "قوله:"
# The prefix itself is NOT captured in the match group — only the core marker.
_CONJUNCTION_PREFIX = r"[وف]?"  # Optional waw or fa prefix (L-004)

TRANSITION_MARKER_PATTERNS: list[_MarkerPattern] = [
    _MarkerPattern(
        regex=re.compile(r"(?:^|\s)" + _CONJUNCTION_PREFIX + r"(قال\s+المصنف\s*:)"),
        target_layer=LayerType.MATN,
        confidence=0.90,
        plain_texts=["قال المصنف:", "وقال المصنف:", "فقال المصنف:"],
    ),
    _MarkerPattern(
        regex=re.compile(r"(?:^|\s)" + _CONJUNCTION_PREFIX + r"(قال\s+الشارح\s*:)"),
        target_layer=LayerType.SHARH,
        confidence=0.90,
        plain_texts=["قال الشارح:", "وقال الشارح:", "فقال الشارح:"],
    ),
    _MarkerPattern(
        regex=re.compile(r"(?:^|\s)" + _CONJUNCTION_PREFIX + r"(قوله\s*:)"),
        target_layer=LayerType.MATN,
        confidence=0.90,
        plain_texts=["قوله:", "وقوله:", "فقوله:"],
    ),
    _MarkerPattern(
        regex=re.compile(r"(?:^|\s)" + _CONJUNCTION_PREFIX + r"(أي\s*:)"),
        target_layer=None,  # → default_commentary_layer at runtime
        confidence=0.80,
        plain_texts=["أي:", "وأي:", "فأي:"],
    ),
]

# Hierarchy for resolving default commentary layer (D11).
# tahqiq_note excluded (rank 0). matn excluded from default (rank 1).
_LAYER_HIERARCHY: dict[str, int] = {
    "matn": 1,
    "sharh": 2,
    "hashiyah": 3,
    "tahqiq_note": 0,
}


# ══════════════════════════════════════════════════════════════════════
# Internal data structures
# ══════════════════════════════════════════════════════════════════════


@dataclass
class LayerBoundary:
    """A detected transition marker boundary."""

    char_offset: int  # first char AFTER marker text (start of new layer)
    to_layer: LayerType
    confidence: float
    marker_text: str


@dataclass
class _LayerEvent:
    """Event in the state machine event stream."""

    offset: int
    event_type: str  # bold_enter, bold_exit, marker, bracket_enter, bracket_exit
    to_layer: LayerType
    confidence: float
    sort_key: int  # exit=0, bracket_enter=1, bold_enter=2, marker=3


@dataclass
class PageDetectionResult:
    """Result from per-page layer detection."""

    segments: list[TextLayerSegment]
    markers_used: dict[str, set[str]]  # layer_type.value → marker descriptions


# ══════════════════════════════════════════════════════════════════════
# Leaf functions (no inter-function dependencies)
# ══════════════════════════════════════════════════════════════════════


def _map_bold_to_primary(page: CleanedPage) -> list[tuple[int, int]]:
    """Map bold_spans (HTML coordinates) to primary_text character ranges.

    For each bold_span, cleans the inner HTML using the same pipeline
    as Pass 3 (strip_tags → decode_entities → normalize_whitespace),
    then uses sequential find() to locate the text in primary_text.

    Returns list of (start, end) tuples in primary_text coordinates.
    """
    regions: list[tuple[int, int]] = []
    search_start = 0

    for _, _, inner_html in page.bold_spans:
        cleaned = strip_tags(inner_html)
        cleaned = decode_entities(cleaned)
        cleaned = normalize_whitespace(cleaned).strip()

        if not cleaned:
            continue

        pos = page.primary_text.find(cleaned, search_start)
        if pos == -1:
            logger.warning(
                "%s: bold text not found in primary_text (unit_index=%d, "
                "search_start=%d): %.40s...",
                NormErrorCode.LAYER_UNCERTAIN.value,
                page.unit_index,
                search_start,
                cleaned,
            )
            continue

        end = pos + len(cleaned)
        regions.append((pos, end))
        search_start = end

    return regions


def _detect_transition_markers(
    primary_text: str,
    default_commentary_layer: LayerType,
) -> list[LayerBoundary]:
    """Detect standalone transition markers in primary text.

    Markers must be preceded by whitespace or line start (standalone).
    Embedded markers ("بقوله «...»") are NOT matched because
    the Arabic prefix ب prevents the word-boundary check.

    char_offset points to the first character AFTER the marker text
    and any trailing space — the marker text belongs to the preceding layer.

    Returns boundaries sorted by char_offset.
    """
    boundaries: list[LayerBoundary] = []

    for pattern in TRANSITION_MARKER_PATTERNS:
        for m in pattern.regex.finditer(primary_text):
            end_pos = m.end(1)
            # Skip trailing whitespace after the colon
            while end_pos < len(primary_text) and primary_text[end_pos] == " ":
                end_pos += 1

            target = (
                pattern.target_layer
                if pattern.target_layer is not None
                else default_commentary_layer
            )

            boundaries.append(
                LayerBoundary(
                    char_offset=end_pos,
                    to_layer=target,
                    confidence=pattern.confidence,
                    marker_text=m.group(1),
                )
            )

    boundaries.sort(key=lambda b: b.char_offset)
    return boundaries


def _detect_bracket_regions(primary_text: str) -> list[tuple[int, int]]:
    """Detect bracket regions with >=15 char content as potential matn markers.

    Looks for square brackets [text] where the content is >=15 characters.
    Short brackets (<15 chars) are excluded — these are typically Quran
    verse references or cross-references, not matn markers.

    Returns (start, end) tuples for qualifying bracket regions.
    """
    regions: list[tuple[int, int]] = []
    i = 0

    while i < len(primary_text):
        if primary_text[i] == "[":
            close_pos = primary_text.find("]", i + 1)
            if close_pos != -1:
                content_len = close_pos - i - 1
                if content_len >= 15:
                    regions.append((i, close_pos + 1))
                i = close_pos + 1
                continue
        i += 1

    return regions


# ══════════════════════════════════════════════════════════════════════
# Classification
# ══════════════════════════════════════════════════════════════════════


def _classify_bold_signal(
    page: CleanedPage,
    bold_regions: list[tuple[int, int]],
    is_multi_layer: bool,
) -> tuple[str, list[tuple[int, int]]]:
    """Classify bold as 'layer_indicator' or 'emphasis' per SPEC §4.A.5.

    Two-level check:
    1. Page-level: bold percentage must be in [5%, 60%] range.
       <5% = too little (emphasis), >60% = too much (entire page is bold).
    2. Per-span two-factor test: each bold region must be >=50 chars
       AND contain no transition marker pattern in the bold text.

    Returns (classification, filtered_bold_regions).
    When classification is "emphasis", filtered_bold_regions is empty.
    """
    if not bold_regions or not is_multi_layer:
        return ("emphasis", [])

    text_len = len(page.primary_text)
    if text_len == 0:
        return ("emphasis", [])

    # Page-level percentage check
    total_bold_chars = sum(end - start for start, end in bold_regions)
    bold_percentage = total_bold_chars / text_len

    # <5% or >60% → emphasis
    if bold_percentage < 0.05 or bold_percentage > 0.60:
        return ("emphasis", [])

    # Per-span two-factor test
    filtered: list[tuple[int, int]] = []
    for start, end in bold_regions:
        span_len = end - start

        # Factor 1: >=50 chars (calibrated from ibn_aqil: 79 and 71 char verses)
        if span_len < 50:
            continue

        # Factor 2: no transition marker pattern in the bold text
        bold_text = page.primary_text[start:end]
        has_marker = any(
            plain_text in bold_text
            for pattern in TRANSITION_MARKER_PATTERNS
            for plain_text in pattern.plain_texts
        )
        if has_marker:
            continue

        filtered.append((start, end))

    if not filtered:
        return ("emphasis", [])

    return ("layer_indicator", filtered)


# ══════════════════════════════════════════════════════════════════════
# Core segmentation (event-based state machine)
# ══════════════════════════════════════════════════════════════════════


def _build_segments(
    primary_text: str,
    bold_regions: list[tuple[int, int]],
    markers: list[LayerBoundary],
    bracket_regions: list[tuple[int, int]],
    default_commentary_layer: LayerType,
    default_confidence: float = 0.60,
) -> list[TextLayerSegment]:
    """Build segments using event-based state machine with marker_state.

    Event generation:
      Bold region [s, e)   → bold_enter(s, MATN, 0.75) + bold_exit(e)
      Marker at char_offset → marker(char_offset, to_layer, confidence)
      Bracket [s, e)       → bracket_enter(s, MATN, 0.65) + bracket_exit(e)

    Sort order at same offset: exit(0) < bracket_enter(1) < bold_enter(2) < marker(3).
    Exits first prevent zero-length segments; markers last so highest priority wins.

    Walk algorithm tracks marker_state — the most recent open-ended marker.
    When a bounded region (bold/bracket) exits, the state machine restores
    to marker_state rather than a hardcoded default. This prevents bold_exit
    from destroying an active marker's MATN transition (R1 resolution).

    Post-processing: merge adjacent same-type, remove zero-length, fill gaps
    with UNCERTAIN, apply conservative default (low-confidence MATN → commentary).
    """
    text_len = len(primary_text)
    if text_len == 0:
        return []

    # ── Generate events ──
    events: list[_LayerEvent] = []

    for start, end in bold_regions:
        events.append(_LayerEvent(start, "bold_enter", LayerType.MATN, 0.75, 2))
        events.append(_LayerEvent(end, "bold_exit", LayerType.MATN, 0.0, 0))

    for boundary in markers:
        events.append(
            _LayerEvent(
                boundary.char_offset,
                "marker",
                boundary.to_layer,
                boundary.confidence,
                3,
            )
        )

    for start, end in bracket_regions:
        events.append(_LayerEvent(start, "bracket_enter", LayerType.MATN, 0.65, 1))
        events.append(_LayerEvent(end, "bracket_exit", LayerType.MATN, 0.0, 0))

    # Sort: by offset, then by sort_key
    events.sort(key=lambda e: (e.offset, e.sort_key))

    # ── Walk with marker_state tracking ──
    current_layer = default_commentary_layer
    current_confidence = default_confidence
    marker_state = (default_commentary_layer, default_confidence)
    last_offset = 0
    raw_segments: list[TextLayerSegment] = []

    for event in events:
        offset = min(event.offset, text_len)

        if offset > last_offset:
            raw_segments.append(
                TextLayerSegment(
                    layer_type=current_layer,
                    author_canonical_id=None,
                    start=last_offset,
                    end=offset,
                    confidence=current_confidence,
                )
            )
            last_offset = offset

        if event.event_type == "marker":
            marker_state = (event.to_layer, event.confidence)
            current_layer = event.to_layer
            current_confidence = event.confidence
        elif event.event_type in ("bold_enter", "bracket_enter"):
            current_layer = event.to_layer
            current_confidence = event.confidence
        elif event.event_type in ("bold_exit", "bracket_exit"):
            current_layer, current_confidence = marker_state

    # Final segment
    if last_offset < text_len:
        raw_segments.append(
            TextLayerSegment(
                layer_type=current_layer,
                author_canonical_id=None,
                start=last_offset,
                end=text_len,
                confidence=current_confidence,
            )
        )

    # ── Post-processing ──
    segments = _merge_adjacent(raw_segments)
    segments = [s for s in segments if s.end > s.start]
    segments = _fill_gaps(segments, text_len)
    segments = _apply_conservative_default(segments, default_commentary_layer)

    return segments


def _merge_adjacent(segments: list[TextLayerSegment]) -> list[TextLayerSegment]:
    """Merge adjacent segments with same layer_type. Confidence = min."""
    if not segments:
        return []

    merged: list[TextLayerSegment] = [segments[0].model_copy()]
    for seg in segments[1:]:
        prev = merged[-1]
        if seg.layer_type == prev.layer_type:
            merged[-1] = TextLayerSegment(
                layer_type=prev.layer_type,
                author_canonical_id=prev.author_canonical_id,
                start=prev.start,
                end=seg.end,
                confidence=min(prev.confidence, seg.confidence),
            )
        else:
            merged.append(seg.model_copy())

    return merged


def _fill_gaps(
    segments: list[TextLayerSegment],
    text_len: int,
) -> list[TextLayerSegment]:
    """Fill gaps with UNCERTAIN segments at confidence 0.30."""
    if not segments:
        if text_len > 0:
            return [
                TextLayerSegment(
                    layer_type=LayerType.UNCERTAIN,
                    author_canonical_id=None,
                    start=0,
                    end=text_len,
                    confidence=0.30,
                )
            ]
        return []

    filled: list[TextLayerSegment] = []

    # Gap before first segment
    if segments[0].start > 0:
        filled.append(
            TextLayerSegment(
                layer_type=LayerType.UNCERTAIN,
                author_canonical_id=None,
                start=0,
                end=segments[0].start,
                confidence=0.30,
            )
        )

    for i, seg in enumerate(segments):
        filled.append(seg)
        if i + 1 < len(segments) and seg.end < segments[i + 1].start:
            filled.append(
                TextLayerSegment(
                    layer_type=LayerType.UNCERTAIN,
                    author_canonical_id=None,
                    start=seg.end,
                    end=segments[i + 1].start,
                    confidence=0.30,
                )
            )

    # Gap after last segment
    if segments[-1].end < text_len:
        filled.append(
            TextLayerSegment(
                layer_type=LayerType.UNCERTAIN,
                author_canonical_id=None,
                start=segments[-1].end,
                end=text_len,
                confidence=0.30,
            )
        )

    return filled


def _apply_conservative_default(
    segments: list[TextLayerSegment],
    default_commentary_layer: LayerType,
) -> list[TextLayerSegment]:
    """MATN segments with confidence < 0.50 → reclassify to commentary.

    SPEC §4.A.5: misattributing commentary to the commentator is less
    harmful than attributing explanation text to the matn author (T-2).
    Re-merges after reclassification to consolidate adjacent same-type.
    """
    result: list[TextLayerSegment] = []
    for seg in segments:
        if seg.layer_type == LayerType.MATN and seg.confidence < 0.50:
            result.append(
                TextLayerSegment(
                    layer_type=default_commentary_layer,
                    author_canonical_id=seg.author_canonical_id,
                    start=seg.start,
                    end=seg.end,
                    confidence=seg.confidence,
                )
            )
        else:
            result.append(seg)

    return _merge_adjacent(result)


# ══════════════════════════════════════════════════════════════════════
# Layer map construction
# ══════════════════════════════════════════════════════════════════════


def _build_layer_map(
    all_page_segments: list[list[TextLayerSegment]],
    metadata: SourceMetadata,
    markers_by_layer: dict[str, set[str]],
) -> list[LayerMapEntry]:
    """Build source-level layer map from per-page segments (D12).

    One LayerMapEntry per unique LayerType. Average confidence across
    all segments of that type. Union of markers. Author info from metadata.
    UNCERTAIN segments are excluded from the layer map.
    """
    layer_confidences: dict[LayerType, list[float]] = {}

    for page_segs in all_page_segments:
        for seg in page_segs:
            if seg.layer_type == LayerType.UNCERTAIN:
                continue
            if seg.layer_type not in layer_confidences:
                layer_confidences[seg.layer_type] = []
            layer_confidences[seg.layer_type].append(seg.confidence)

    entries: list[LayerMapEntry] = []
    for layer_type, confidences in layer_confidences.items():
        # Find author info from metadata.text_layers
        author_id: Optional[str] = None
        author_name: Optional[str] = None
        for tl in metadata.text_layers:
            if tl.layer_type == layer_type.value:
                author_id = tl.author.canonical_id
                author_name = tl.author.name_arabic
                break

        markers = sorted(markers_by_layer.get(layer_type.value, set()))
        avg_conf = sum(confidences) / len(confidences)

        entries.append(
            LayerMapEntry(
                layer_type=layer_type,
                author_canonical_id=author_id,
                author_name_arabic=author_name,
                confidence=round(avg_conf, 2),
                markers=markers,
            )
        )

    return entries


# ══════════════════════════════════════════════════════════════════════
# Orchestration
# ══════════════════════════════════════════════════════════════════════


def _resolve_default_commentary_layer(metadata: SourceMetadata) -> LayerType:
    """D11: Find the default commentary layer.

    Returns the highest-hierarchy non-matn, non-tahqiq layer in
    metadata.text_layers. Hierarchy: sharh=2, hashiyah=3.
    Fallback: SHARH if no qualifying layer found or text_layers empty.
    """
    best_type: Optional[str] = None
    best_rank = 1  # must be >1 to exclude matn (rank 1) and tahqiq_note (rank 0)

    for tl in metadata.text_layers:
        rank = _LAYER_HIERARCHY.get(tl.layer_type, -1)
        if rank > best_rank:
            best_rank = rank
            best_type = tl.layer_type

    if best_type is not None:
        return LayerType(best_type)

    return LayerType.SHARH


def _assign_author_ids(
    segments: list[TextLayerSegment],
    metadata: SourceMetadata,
) -> list[TextLayerSegment]:
    """Assign author_canonical_id to segments from metadata.text_layers."""
    author_map: dict[str, str] = {}
    for tl in metadata.text_layers:
        author_map[tl.layer_type] = tl.author.canonical_id

    if not author_map:
        return segments

    result: list[TextLayerSegment] = []
    for seg in segments:
        author_id = author_map.get(seg.layer_type.value)
        if author_id is not None:
            result.append(
                TextLayerSegment(
                    layer_type=seg.layer_type,
                    author_canonical_id=author_id,
                    start=seg.start,
                    end=seg.end,
                    confidence=seg.confidence,
                )
            )
        else:
            result.append(seg)

    return result


def detect_layers(
    page: CleanedPage,
    metadata: SourceMetadata,
    is_multi_layer: bool,
    default_commentary_layer: LayerType,
) -> PageDetectionResult:
    """Detect text layers in a single page.

    Single-layer fast path: one MATN segment [0, len), confidence 1.0.
    Multi-layer: bold mapping → transition markers → brackets →
    bold classification → state machine segmentation → author IDs.
    """
    text_len = len(page.primary_text)
    markers_used: dict[str, set[str]] = {}

    if text_len == 0:
        return PageDetectionResult(segments=[], markers_used={})

    if not is_multi_layer:
        # Single-layer fast path
        author_id: Optional[str] = None
        if metadata.text_layers:
            author_id = metadata.text_layers[0].author.canonical_id
        return PageDetectionResult(
            segments=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=author_id,
                    start=0,
                    end=text_len,
                    confidence=1.0,
                )
            ],
            markers_used={},
        )

    # ── Multi-layer detection ──

    # Step 1: Map bold spans to primary_text coordinates
    bold_regions = _map_bold_to_primary(page)

    # Step 2: Detect transition markers
    marker_boundaries = _detect_transition_markers(
        page.primary_text, default_commentary_layer
    )

    # Step 3: Detect bracket regions
    bracket_regions = _detect_bracket_regions(page.primary_text)

    # Step 4: Classify bold signal
    bold_class, filtered_bold = _classify_bold_signal(page, bold_regions, True)

    # Collect markers used
    if bold_class == "layer_indicator":
        markers_used.setdefault("matn", set()).add("bold")
    for boundary in marker_boundaries:
        markers_used.setdefault(boundary.to_layer.value, set()).add(
            boundary.marker_text
        )
    if bracket_regions:
        markers_used.setdefault("matn", set()).add("brackets")

    # Step 5: Build segments
    segments = _build_segments(
        page.primary_text,
        filtered_bold,
        marker_boundaries,
        bracket_regions,
        default_commentary_layer,
    )

    # Step 6: Assign author canonical_ids
    segments = _assign_author_ids(segments, metadata)

    return PageDetectionResult(segments=segments, markers_used=markers_used)


def pre_scan_multi_layer(
    pages: list[CleanedPage],
    max_pages: int = 10,
) -> bool:
    """Quick scan for multi-layer signals in first N pages.

    Checks for bold coverage >10% or transition markers present.
    Returns True if >=3 pages show multi-layer signals.
    Used by shamela.py for D7/ADV-015 metadata override.
    """
    scan_pages = [p for p in pages if not p.is_blank and not p.is_image_only][
        :max_pages
    ]
    signal_count = 0

    for page in scan_pages:
        text_len = len(page.primary_text)
        if text_len == 0:
            continue

        has_signal = False

        # Check bold coverage > 10% (fast proxy using raw inner_html length)
        if page.bold_spans:
            total_bold = sum(len(inner) for _, _, inner in page.bold_spans)
            if total_bold / text_len > 0.10:
                has_signal = True

        # Check for transition markers
        if not has_signal:
            for pattern in TRANSITION_MARKER_PATTERNS:
                if pattern.regex.search(page.primary_text):
                    has_signal = True
                    break

        if has_signal:
            signal_count += 1

    return signal_count >= 3
