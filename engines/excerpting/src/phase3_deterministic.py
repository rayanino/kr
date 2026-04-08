"""Phase 3: Deterministic Metadata Assembly (SPEC §7.1, §6.2).

Computes 9 deterministic fields (F-DET-1 through F-DET-9) and layer
attribution rules (LA-1 through LA-4) without any LLM call.

These fields survive even if LLM enrichment fails — they are the
minimum viable ExcerptRecord.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from engines.excerpting.contracts import TakhrijEntry

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
    UnitRelationship,
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
# Expanded per DR29 improvement #11 — high-precision transmission/citation verbs
# from arabic-scholarly-conventions.md and HARDENING_SESSION_PROTOCOL indivisible units.
_HADITH_MARKERS: list[str] = [
    "رواه",
    "أخرجه",
    "في الصحيحين",
    "متفق عليه",
    "في صحيح",
    "في سنن",
    # Transmission formulas (arabic-scholarly-conventions.md)
    "حدثنا",
    "أخبرنا",
    "أنبأنا",
    "سمعت",
    "عن النبي",
    "قال رسول الله",
    # Collection references
    "في المسند",
    "في الموطأ",
]

_IJMA_MARKERS: list[str] = [
    "أجمعوا",
    "إجماع",
    "لا خلاف",
    "اتفق العلماء",
    "بالاتفاق",
    # Additional consensus/agreement formulas
    "بلا خلاف",
    "من غير خلاف",
    "لا نعلم فيه خلافا",
    "اتفقوا على",
]


# ═══════════════════════════════════════════════════════════════════
# Micro-unit merge (DR29 #4 + Gemini CLI scholarly validation)
# ═══════════════════════════════════════════════════════════════════

# Bare opener patterns — forward-merge into following unit.
# Gemini CLI: "indexing devices for the point that follows"
_OPENER_PATTERNS: list[str] = [
    "المسألة",
    "الفرع",
    "فائدة",
    "تنبيه",
    "تتمة",
    "خاتمة",
    "فرع",
    # Ordinals (bare Arabic ordinals without substantive content)
    "الأولى",
    "الثانية",
    "الثالثة",
    "الرابعة",
    "الخامسة",
    "السادسة",
    "السابعة",
    "الثامنة",
    "التاسعة",
    "العاشرة",
    # Discourse ordinals
    "أحدها",
    "والثاني",
    "والثالث",
    "الوجه الأول",
    "الوجه الثاني",
    "الوجه الثالث",
]

# Bare closer patterns — backward-merge into preceding unit.
# Gemini CLI: "closing formulas merge backward, not forward"
_CLOSER_PATTERNS: list[str] = [
    "والله أعلم",
    "انتهى",
    "تم",
    "هذا آخره",
    "انتهى كلامه",
]

# Maximum character length for a unit to be considered "bare micro"
_MICRO_UNIT_MAX_CHARS = 40


def _is_bare_micro_unit(text: str) -> str | None:
    """Classify a short text as opener, closer, or not a micro-unit.

    Returns "opener", "closer", or None.
    A unit is bare if it matches a known pattern AND does not contain
    substantive content after the marker (i.e., no colon-then-content).
    """
    stripped = text.strip()
    if len(stripped) > _MICRO_UNIT_MAX_CHARS:
        return None
    # Semantically-complete heading exemption: if the text contains a colon
    # followed by substantive content (>10 chars), it's not bare.
    # e.g. "قاعدة: اليقين لا يزول بالشك" is a complete heading.
    colon_pos = stripped.find(":")
    if colon_pos == -1:
        colon_pos = stripped.find(":")  # Arabic colon (rare but possible)
    if colon_pos >= 0 and len(stripped) - colon_pos - 1 > 10:
        return None

    # Closers: pattern must be at or near the END of the text
    for pattern in _CLOSER_PATTERNS:
        if stripped.endswith(pattern) or stripped.endswith(pattern + "."):
            return "closer"
    # Openers: pattern must be at the START of the text (not embedded in a sentence)
    for pattern in _OPENER_PATTERNS:
        if stripped.startswith(pattern):
            return "opener"
    return None


def _reindex_related_units(
    units: list[TeachingUnit],
    old_to_new: dict[int, int],
) -> list[TeachingUnit]:
    """Remap target_unit_index in related_units after merge reindexing.

    Fixes stale indices (DR40 codex-verify finding):
    - Remaps target_unit_index using old_to_new mapping
    - Drops self-referential links (target == self after remap)
    - Deduplicates by (target_unit_index, relationship)
    """
    result: list[TeachingUnit] = []
    for unit in units:
        if not unit.related_units:
            result.append(unit)
            continue
        seen: set[tuple[int, str]] = set()
        remapped: list[UnitRelationship] = []
        for rel in unit.related_units:
            new_target = old_to_new.get(rel.target_unit_index)
            if new_target is None:
                # Target was absorbed — drop the link. This is a data loss
                # event for scholarly structure; warn so operators can detect it.
                logger.warning(
                    "Dropped related_unit link: unit %d → old target %d "
                    "(absorbed during merge, relationship=%s).",
                    unit.unit_index,
                    rel.target_unit_index,
                    rel.relationship.value,
                )
                continue
            if new_target == unit.unit_index:
                # Self-referential after remap — drop
                logger.debug(
                    "Dropped self-referential link: unit %d → %d.",
                    unit.unit_index,
                    new_target,
                )
                continue
            dedup_key = (new_target, rel.relationship.value)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            remapped.append(
                rel.model_copy(update={"target_unit_index": new_target})
            )
        result.append(unit.model_copy(update={"related_units": remapped}))
    return result


def merge_micro_units(
    units: list[TeachingUnit],
    assembled_text: str,
) -> list[TeachingUnit]:
    """Merge bare structural micro-units into adjacent substantive units.

    DR29 #4 + Gemini CLI scholarly validation (USUALLY_MERGE).
    Openers (ordinals, مسألة, فائدة, تنبيه) → forward-merge into NEXT unit.
    Closers (والله أعلم, انتهى) → backward-merge into PREVIOUS unit.

    Returns a new list with merged units and reindexed unit_index values.
    """
    if len(units) <= 1:
        return units

    # Build a char map for extracting text from word offsets
    tokens = assembled_text.split()

    def unit_text(u: TeachingUnit) -> str:
        """Extract the actual text of a unit from assembled_text."""
        start_char = sum(len(tokens[i]) + 1 for i in range(u.start_word)) if u.start_word > 0 else 0
        end_char = sum(len(tokens[i]) + 1 for i in range(u.end_word + 1))
        return assembled_text[start_char:end_char].strip()

    # Phase 1: classify each unit
    classifications: list[str | None] = []
    for u in units:
        text = unit_text(u)
        classifications.append(_is_bare_micro_unit(text))

    # Phase 2: build merge plan (which units absorb which)
    # absorb_into[i] = j means unit i is absorbed into unit j
    absorb_into: dict[int, int] = {}

    for i, cls in enumerate(classifications):
        if cls == "opener" and i + 1 < len(units) and classifications[i + 1] is None:
            absorb_into[i] = i + 1
        elif cls == "closer" and i - 1 >= 0 and classifications[i - 1] is None:
            absorb_into[i] = i - 1

    if not absorb_into:
        return units

    # Phase 3: execute merges
    merged: dict[int, TeachingUnit] = {}
    for i, u in enumerate(units):
        if i in absorb_into:
            continue  # this unit will be absorbed
        merged[i] = u

    for micro_idx, target_idx in absorb_into.items():
        micro = units[micro_idx]
        if target_idx not in merged:
            # Target was itself absorbed — skip (don't chain merges)
            logger.warning(
                "Micro-unit %d target %d also absorbed — keeping micro standalone.",
                micro_idx,
                target_idx,
            )
            merged[micro_idx] = micro
            continue

        target = merged[target_idx]
        # Merge: expand word range and segment indices
        new_start = min(micro.start_word, target.start_word)
        new_end = max(micro.end_word, target.end_word)
        new_segments = sorted(set(micro.segment_indices + target.segment_indices))

        # Recompute text_snippet from merged range
        start_char = sum(len(tokens[j]) + 1 for j in range(new_start)) if new_start > 0 else 0
        end_char = sum(len(tokens[j]) + 1 for j in range(new_end + 1))
        merged_text = assembled_text[start_char:end_char].strip()

        merged[target_idx] = TeachingUnit(
            unit_index=target.unit_index,  # reindexed below
            segment_indices=new_segments,
            start_word=new_start,
            end_word=new_end,
            text_snippet=merged_text[:80],
            primary_function=target.primary_function,
            secondary_functions=list(
                set(target.secondary_functions) | set(micro.secondary_functions)
            ),
            description_arabic=target.description_arabic,
            self_containment=target.self_containment,
            self_containment_notes=target.self_containment_notes,
            related_units=target.related_units + micro.related_units,
        )

    # Phase 4: reindex, remap related_units, and sort
    result = sorted(merged.values(), key=lambda u: u.start_word)
    old_to_new: dict[int, int] = {
        u.unit_index: idx for idx, u in enumerate(result)
    }
    reindexed = [
        u.model_copy(update={"unit_index": idx})
        for idx, u in enumerate(result)
    ]
    reindexed = _reindex_related_units(reindexed, old_to_new)

    logger.info(
        "Micro-unit merge: %d units → %d units (%d merged).",
        len(units),
        len(reindexed),
        len(absorb_into),
    )
    return reindexed


# ═══════════════════════════════════════════════════════════════════
# MV-1 sub-viable merge (SPEC §5.5.5, Session 17 campaign finding)
# ═══════════════════════════════════════════════════════════════════

_MV1_WORD_FLOOR = 25

# Transmission formulas that mark isnad chains — units containing these
# MUST NOT be merged even if sub-viable. Isnads are atomic scholarly units
# per arabic-scholarly-conventions.md. Arabic-auditor review finding.
_ISNAD_MARKERS: list[str] = [
    "حدثنا",
    "أخبرنا",
    "أنبأنا",
    "سمعت",
    "قرأت على",
]


def merge_subviable_units(
    units: list[TeachingUnit],
    assembled_text: str,
) -> list[TeachingUnit]:
    """Merge sub-viable units (<25 words) per SPEC §5.5.5.

    Runs AFTER merge_micro_units (which handles structural openers/closers).
    Catches remaining fragments — typically numbered-list items that are
    content but too short to stand alone as teaching units.

    Merge strategy (§5.5.5 rules 1–5):
    1. Scan in reading order for units below 25 words.
    2. Backward-merge preferred (into preceding unit).
    3. If preceding is also sub-viable, merge entire run forward.
    4. If sub-viable unit is first in chunk, merge forward.
    5. Log every merge.
    """
    if len(units) <= 1:
        return units

    def word_count(u: TeachingUnit) -> int:
        return u.end_word - u.start_word + 1

    def _unit_has_isnad(u: TeachingUnit) -> bool:
        """Check if unit text contains transmission formulas (isnad).

        Arabic-auditor finding: isnad chains (7-12 words) are sub-viable
        by word count but MUST NOT be merged — they are atomic scholarly
        units per arabic-scholarly-conventions.md.
        """
        char_s, char_e = _word_to_char_range(assembled_text, u.start_word, u.end_word)
        text = assembled_text[char_s:char_e]
        return any(marker in text for marker in _ISNAD_MARKERS)

    # DR40: protect both ends of relationship links from merge.
    # A unit is protected if it HAS links OR if another unit TARGETS it.
    linked_targets = {
        rel.target_unit_index
        for u in units
        for rel in u.related_units
    }
    subviable = [
        word_count(u) < _MV1_WORD_FLOOR
        and not _unit_has_isnad(u)
        and not u.related_units  # DR40: units with outgoing links
        and u.unit_index not in linked_targets  # DR40: units targeted by links
        for u in units
    ]

    if not any(subviable):
        return units

    # ── Group consecutive sub-viable units into runs ──────────────
    runs: list[tuple[int, int]] = []  # (start_idx, end_idx_exclusive)
    i = 0
    while i < len(units):
        if subviable[i]:
            run_start = i
            while i < len(units) and subviable[i]:
                i += 1
            runs.append((run_start, i))
        else:
            i += 1

    # ── Build merge plan ──────────────────────────────────────────
    absorb_into: dict[int, int] = {}

    for run_start, run_end in runs:
        if run_start == 0:
            # Rule 4: run at chunk start → forward into first viable
            if run_end < len(units):
                target = run_end
            else:
                # ALL units sub-viable → collapse into index 0
                for idx in range(1, len(units)):
                    absorb_into[idx] = 0
                continue
        else:
            # Rule 2: backward into preceding viable unit
            target = run_start - 1

        for idx in range(run_start, run_end):
            absorb_into[idx] = target

    if not absorb_into:
        return units

    # ── Execute merges ────────────────────────────────────────────
    merged: dict[int, TeachingUnit] = {}
    for idx, u in enumerate(units):
        if idx not in absorb_into:
            merged[idx] = u

    for src_idx, tgt_idx in sorted(absorb_into.items()):
        src = units[src_idx]
        if tgt_idx not in merged:
            logger.warning(
                "MV-1 merge: unit %d target %d missing — keeping standalone.",
                src_idx,
                tgt_idx,
            )
            merged[src_idx] = src
            continue

        target = merged[tgt_idx]
        new_start = min(src.start_word, target.start_word)
        new_end = max(src.end_word, target.end_word)
        new_segments = sorted(set(src.segment_indices + target.segment_indices))

        # Use _word_to_char_range (DD-S3-2) — handles multi-space, leading
        # whitespace, and ZWNJ correctly. Do NOT duplicate char arithmetic.
        char_s, char_e = _word_to_char_range(assembled_text, new_start, new_end)
        merged_text = assembled_text[char_s:char_e].strip()

        merged[tgt_idx] = TeachingUnit(
            unit_index=target.unit_index,
            segment_indices=new_segments,
            start_word=new_start,
            end_word=new_end,
            text_snippet=merged_text[:80],
            primary_function=target.primary_function,
            secondary_functions=list(
                set(target.secondary_functions) | set(src.secondary_functions)
            ),
            description_arabic=target.description_arabic,
            self_containment=target.self_containment,
            self_containment_notes=target.self_containment_notes,
            related_units=target.related_units + src.related_units,
        )

        logger.info(
            "MV-1 merge: unit %d (%d words) → unit %d. Result: %d words.",
            src_idx,
            word_count(src),
            tgt_idx,
            new_end - new_start + 1,
        )

    # ── Reindex + remap related_units ────────────────────────────
    result = sorted(merged.values(), key=lambda u: u.start_word)
    old_to_new: dict[int, int] = {
        u.unit_index: idx for idx, u in enumerate(result)
    }
    reindexed = [
        u.model_copy(update={"unit_index": idx})
        for idx, u in enumerate(result)
    ]
    reindexed = _reindex_related_units(reindexed, old_to_new)

    total_merged = len(absorb_into)
    logger.info(
        "MV-1 sub-viable merge: %d units → %d units (%d absorbed).",
        len(units),
        len(reindexed),
        total_merged,
    )
    return reindexed


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

    # LA-2: Exactly 2 layers, neither >=80%, dominant >=60% -> outermost wins
    # §6.2: if dominant <60%, route to LA-3 (EX-M-001) for consensus review
    if len(coverages) == 2 and top_coverage >= 0.6:
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
        # Search ALL occurrences — a marker may appear multiple times
        # (e.g. repeated ref in different chunks). Include the footnote
        # if ANY occurrence falls within [char_start, char_end).
        found_any = False
        matched = False
        search_start = 0
        while True:
            pos = assembled_text.find(pattern, search_start)
            if pos == -1:
                break
            found_any = True
            if char_start <= pos < char_end:
                matched = True
                break
            search_start = pos + 1
        if not found_any:
            logger.warning(
                "Orphaned footnote marker '%s' — not found in assembled_text",
                footnote.ref_marker,
            )
            continue
        if matched:
            result.append(footnote)
    return result


def derive_takhrij_from_footnotes(
    footnotes_relevant: list[Footnote],
) -> Optional[list["TakhrijEntry"]]:
    """Derive takhrij_data from HADITH_TAKHRIJ footnotes (DR29 #8).

    Gemini CLI minimum-viable spec: only populate when the footnote contains
    at least a source collection name + retrievable locator (hadith number
    or volume/page). Footnotes without locators are below minimum and are
    not included (e.g. "رواه البخاري ومسلم" without a number).

    Distinguishes author vs muhaqqiq provenance via footnote_type context.
    """
    from engines.excerpting.contracts import TakhrijEntry
    from engines.normalization.contracts import FootnoteType

    entries: list[TakhrijEntry] = []

    for fn in footnotes_relevant:
        # Only process HADITH_TAKHRIJ footnotes
        if fn.footnote_type != FootnoteType.HADITH_TAKHRIJ:
            continue

        # Check if structured takhrij_data exists from normalization
        if fn.takhrij_data is None:
            continue

        collections_raw = fn.takhrij_data.collections
        if not collections_raw:
            continue

        # Extract collection names and locators
        collection_names: list[str] = []
        hadith_numbers: list[str] = []
        has_locator = False

        for coll in collections_raw:
            name = coll.get("name", "")
            if name:
                collection_names.append(name)
            number = coll.get("number")
            if number:
                hadith_numbers.append(str(number))
                has_locator = True
            book = coll.get("book")
            if book:
                has_locator = True  # book/bab reference counts as locator

        # Gemini minimum-viable: must have source + locator
        if not collection_names or not has_locator:
            logger.debug(
                "Footnote '%s' has takhrij but no locator — below minimum.",
                fn.ref_marker,
            )
            continue

        # Extract grade if present
        grade: Optional[str] = None
        grade_source: Optional[str] = None
        if fn.takhrij_data.grading:
            grade = fn.takhrij_data.grading.get("grade")
            grade_source = fn.takhrij_data.grading.get("grader")

        # hadith_text_snippet: first 80 chars of the footnote text as anchor
        anchor = fn.text[:80].strip()

        entries.append(
            TakhrijEntry(
                hadith_text_snippet=anchor,
                collections=collection_names,
                hadith_numbers=hadith_numbers,
                grade=grade,
                grade_source=grade_source,
            )
        )

    return entries if entries else None


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
    primary_skipped = False
    for layer, _coverage in coverages:
        layer_author = layer.author_canonical_id or "unknown"
        # Skip the primary layer (match on type AND author, not type alone)
        if (layer.layer_type.value == primary_layer.layer_id
                and layer_author == primary_layer.author_id):
            if layer_author != "unknown":
                # Known author: all same-(type, author) entries are the
                # same person — safe to exclude all.
                continue
            # Unknown author: only skip one entry (the primary itself).
            # Other same-(type, unknown) entries may represent different
            # scholars — silently excluding them is T-1 attribution
            # corruption (scholar voice lost from the record).
            if not primary_skipped:
                primary_skipped = True
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

        # IC-1 exemption (Session 17 Fix #3): when 3+ distinct content_types
        # exist in one unit, the content is intertwined (e.g. definition +
        # proof + attribution in one paragraph). FR-1's 33% audit does not
        # apply — the secondary content is constitutive, not supplementary.
        if len(content_types) >= 3:
            review_flags.append("content_intertwined")

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
            # Deterministic snippet: derive from primary_text, not LLM-supplied
            # unit.text_snippet. LLMs cannot count Unicode codepoints precisely
            # in Arabic (diacritics are separate codepoints). DR29 improvement #1.
            text_snippet=primary_text[:80],
            start_word=sw,
            end_word=ew,
            segment_indices=unit.segment_indices,
            physical_pages=physical_pages,
            # ── Classification (5) ──
            primary_function=unit.primary_function,
            secondary_functions=unit.secondary_functions,
            content_types=content_types,
            description_arabic=unit.description_arabic,
            structural_section=None,  # Populated by Phase 3 LLM enrichment
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
            takhrij_data=derive_takhrij_from_footnotes(footnotes_relevant),
            cross_references=[],
            footnotes_relevant=footnotes_relevant,
            # ── Relationship links (1) ──
            related_units=unit.related_units,
            # ── Metadata/flags (3) ──
            consensus_metadata=None,
            gate_flags=[],
            review_flags=review_flags,
        )
        results.append(record)

    return results
