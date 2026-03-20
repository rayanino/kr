"""Normalization self-validation — SPEC §5 Layer 1.

Ten automated checks run on every normalized package before writing to disk.
Any fatal check failure aborts the write — no corrupt packages reach disk.

Check list (SPEC §5):
  1. Schema compliance
  2. Coverage check (page count match, loose ±10%)
  3. Text extraction verification (Arabic %, no garbage, no mojibake)
  4. Layer consistency (full coverage, plausible proportions, transition count)
  5. Division tree validity (ordering, no overlap, full coverage)
  6. Footnote integrity (non-empty text, orphan reference detection)
  7. Unit index integrity (contiguous zero-based sequence)
  8. Diacritics preservation — standalone utility (runs inside each normalizer per D6-1)
  9. Format-specific input validation (delegated to each normalizer)
  10. Boundary continuity consistency

validate_package() runs checks 1-7 and 10. Check 8 runs inside normalizers.
Check 9 runs inside each normalizer's validate_input().
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from pydantic import ValidationError as PydanticValidationError

from engines.normalization.contracts import (
    BoundaryContinuityType,
    ContentUnit,
    DivisionNode,
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
)
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.source.contracts import SourceMetadata

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────
# §5 Check 8 — Diacritics preservation utility (D6-1, D6-3)
# ──────────────────────────────────────────────────────────────────

# SPEC §5 line 1501: exactly U+064B–U+0652, U+0670, U+0640.
# Total: 10 codepoints. Do NOT reuse _ARABIC_DIACRITICS from shamela.py (20 codepoints).
DIACRITICS_CHECK8: set[int] = set(range(0x064B, 0x0653)) | {0x0670, 0x0640}


def check_diacritics_page(source_text: str, output_text: str) -> bool:
    """Return True if diacritics counts match. False means drift detected.

    Per D6-3 and D6-4: compares primary text only (not footnotes).
    """
    source_d = [c for c in source_text if ord(c) in DIACRITICS_CHECK8]
    output_d = [c for c in output_text if ord(c) in DIACRITICS_CHECK8]
    return len(source_d) == len(output_d)


# ──────────────────────────────────────────────────────────────────
# Validation result
# ──────────────────────────────────────────────────────────────────


class ValidationResult:
    """Result of running all §5 checks on a normalized package."""

    def __init__(self) -> None:
        self.passed: bool = True
        self.warnings: list[str] = []
        self.fatal_errors: list[NormalizationError] = []

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_fatal(self, error: NormalizationError) -> None:
        self.fatal_errors.append(error)
        self.passed = False


# ──────────────────────────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────────────────────────


def validate_package(
    package: NormalizedPackage,
    metadata: SourceMetadata,
) -> ValidationResult:
    """Run all §5 Layer 1 checks on a normalized package.

    Calls checks 1-7 and 10 sequentially. Any fatal error stops
    processing (no point running further checks). Warnings accumulate.

    Check 8 (diacritics) runs inside each normalizer per D6-1.
    Check 9 (format-specific input) runs inside each normalizer's validate_input().

    Args:
        package: The assembled normalized package (before writing to disk).
        metadata: Source metadata for coverage check.

    Returns:
        ValidationResult with pass/fail and all warnings/errors.
    """
    result = ValidationResult()

    # Fatal checks stop on first failure
    _check_schema_compliance(package, result)
    if not result.passed:
        return result

    _check_unit_index_integrity(package, result)
    if not result.passed:
        return result

    # Non-fatal checks accumulate warnings
    _check_coverage(package, metadata, result)
    _check_text_extraction(package, result)
    _check_layer_consistency(package, metadata, result)
    _check_division_tree(package, result)
    _check_footnote_integrity(package, result)
    _check_boundary_continuity(package, result)

    return result


# ──────────────────────────────────────────────────────────────────
# Check 1 — Schema compliance (SPEC line 1472)
# ──────────────────────────────────────────────────────────────────


def _check_schema_compliance(
    package: NormalizedPackage,
    result: ValidationResult,
) -> None:
    """Re-validate manifest and each content unit via Pydantic.

    Also verifies manifest.total_content_units == len(content_units) (ADV-033).
    """
    # Re-validate manifest
    try:
        NormalizedManifest.model_validate(package.manifest.model_dump())
    except PydanticValidationError as e:
        result.add_fatal(NormalizationError(
            code=NormErrorCode.SCHEMA_VIOLATION,
            message=f"Manifest schema violation: {e}",
            source_id=package.manifest.source_id,
            recovery="Fix the manifest fields that violate the schema.",
        ))
        return

    # Re-validate each content unit
    for cu in package.content_units:
        try:
            ContentUnit.model_validate(cu.model_dump())
        except PydanticValidationError as e:
            result.add_fatal(NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message=f"Content unit {cu.unit_index} schema violation: {e}",
                source_id=cu.source_id,
                unit_index=cu.unit_index,
                recovery="Fix the content unit fields that violate the schema.",
            ))
            return

    # ADV-033: total_content_units must match actual count
    if package.manifest.total_content_units != len(package.content_units):
        result.add_fatal(NormalizationError(
            code=NormErrorCode.SCHEMA_VIOLATION,
            message=(
                f"total_content_units={package.manifest.total_content_units} "
                f"but actual content unit count={len(package.content_units)}"
            ),
            source_id=package.manifest.source_id,
            recovery="Ensure total_content_units matches the actual number of content units.",
        ))


# ──────────────────────────────────────────────────────────────────
# Check 2 — Coverage check (SPEC line 1474)
# ──────────────────────────────────────────────────────────────────

# Unicode ranges for Arabic characters
_ARABIC_RANGES = (
    range(0x0600, 0x0700),   # Arabic block
    range(0x0750, 0x0780),   # Arabic Supplement
    range(0xFB50, 0xFE00),   # Arabic Presentation Forms-A
    range(0xFE70, 0xFF00),   # Arabic Presentation Forms-B
)


def _check_coverage(
    package: NormalizedPackage,
    metadata: SourceMetadata,
    result: ValidationResult,
) -> None:
    """Loose check: |content_units - page_count| / page_count > 0.10 → warning.

    Skip if metadata.page_count is None or 0. D6-8: only loose check here.
    """
    page_count = getattr(metadata, "page_count", None)
    if page_count is None or page_count == 0:
        return

    actual = len(package.content_units)
    deviation = abs(actual - page_count) / page_count
    # ADV-028: > 0.10, NOT >= 0.10
    if deviation > 0.10:
        result.add_warning(
            f"NORM_PAGE_COUNT_MISMATCH: expected ~{page_count} content units, "
            f"got {actual} ({deviation:.1%} deviation)"
        )


# ──────────────────────────────────────────────────────────────────
# Check 3 — Text extraction verification (SPEC lines 1476-1480)
# ──────────────────────────────────────────────────────────────────

# Regex for identical character runs (>20). Use . to match any char.
_IDENTICAL_RUN_RE = re.compile(r"(.)\1{20,}")

# Regex for mojibake: 3+ consecutive Latin Extended chars in Arabic text (D6-9)
_MOJIBAKE_RE = re.compile(r"[\u00c0-\u00ff]{3,}")

# Punctuation chars to exclude from Arabic ratio denominator
_PUNCTUATION = set(".,;:!?()[]{}\"'`~@#$%^&*-_=+/\\|<>؟،؛" + "⌜⌝")


def _is_arabic_char(c: str) -> bool:
    """Check if a character is in any Arabic Unicode range."""
    cp = ord(c)
    return any(cp in r for r in _ARABIC_RANGES)


def _check_text_extraction(
    package: NormalizedPackage,
    result: ValidationResult,
) -> None:
    """Per-page checks: non-empty text, Arabic ratio, garbage runs, mojibake."""
    for cu in package.content_units:
        # Skip blank pages
        if cu.content_flags.is_blank:
            continue

        # Non-empty primary_text on non-blank page → fatal
        if not cu.primary_text.strip():
            result.add_fatal(NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message=f"Empty primary_text on non-blank page unit_index={cu.unit_index}",
                source_id=cu.source_id,
                unit_index=cu.unit_index,
                recovery="Investigate why a non-blank page has empty text.",
            ))
            return

        # Arabic character ratio (exclude whitespace and punctuation)
        non_ws_non_punct = [
            c for c in cu.primary_text
            if not c.isspace() and c not in _PUNCTUATION
        ]
        if non_ws_non_punct:
            arabic_count = sum(1 for c in non_ws_non_punct if _is_arabic_char(c))
            ratio = arabic_count / len(non_ws_non_punct)
            # ADV-025: >= 0.70 passes, < 0.70 flags
            if ratio < 0.70:
                result.add_warning(
                    f"Low Arabic ratio on unit_index={cu.unit_index}: "
                    f"{ratio:.2%} ({arabic_count}/{len(non_ws_non_punct)})"
                )

        # Identical character runs (>20) — ADV-029: exactly 20 = no flag, 21 = flag
        if _IDENTICAL_RUN_RE.search(cu.primary_text):
            result.add_warning(
                f"Identical character run >20 on unit_index={cu.unit_index}"
            )

        # Mojibake detection (D6-9)
        if _MOJIBAKE_RE.search(cu.primary_text):
            result.add_warning(
                f"Possible mojibake on unit_index={cu.unit_index}: "
                f"3+ consecutive Latin Extended characters"
            )


# ──────────────────────────────────────────────────────────────────
# Check 4 — Layer consistency (SPEC lines 1482-1486)
# ──────────────────────────────────────────────────────────────────


def _check_layer_consistency(
    package: NormalizedPackage,
    metadata: SourceMetadata,
    result: ValidationResult,
) -> None:
    """Multi-layer sources only: full coverage, plausible proportions, transition count."""
    if not metadata.is_multi_layer:
        return

    # Build set of known author_canonical_ids from layer_map
    layer_map_ids: set[Optional[str]] = {
        entry.author_canonical_id for entry in package.manifest.layer_map
    }

    total_matn_chars = 0
    total_chars = 0

    for cu in package.content_units:
        text_len = len(cu.primary_text)
        if text_len == 0:
            continue

        segments = cu.text_layers

        # Full character coverage: first starts at 0, last ends at len, no gaps
        if not segments:
            result.add_fatal(NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message=f"No text_layers on unit_index={cu.unit_index} in multi-layer source",
                source_id=cu.source_id,
                unit_index=cu.unit_index,
                recovery="Every character must be covered by a text_layers segment.",
            ))
            return

        if segments[0].start != 0:
            result.add_fatal(NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message=(
                    f"text_layers gap on unit_index={cu.unit_index}: "
                    f"first segment starts at {segments[0].start}, not 0"
                ),
                source_id=cu.source_id,
                unit_index=cu.unit_index,
                recovery="Fix layer detection to cover from position 0.",
            ))
            return

        if segments[-1].end != text_len:
            result.add_fatal(NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message=(
                    f"text_layers gap on unit_index={cu.unit_index}: "
                    f"last segment ends at {segments[-1].end}, not {text_len}"
                ),
                source_id=cu.source_id,
                unit_index=cu.unit_index,
                recovery="Fix layer detection to cover through end of text.",
            ))
            return

        for j in range(len(segments) - 1):
            if segments[j].end != segments[j + 1].start:
                result.add_fatal(NormalizationError(
                    code=NormErrorCode.SCHEMA_VIOLATION,
                    message=(
                        f"text_layers gap on unit_index={cu.unit_index}: "
                        f"segment {j} ends at {segments[j].end}, "
                        f"segment {j+1} starts at {segments[j+1].start}"
                    ),
                    source_id=cu.source_id,
                    unit_index=cu.unit_index,
                    recovery="Fix layer detection gap between consecutive segments.",
                ))
                return

        # Matn ratio accumulation
        for seg in segments:
            seg_len = seg.end - seg.start
            total_chars += seg_len
            if seg.layer_type == LayerType.MATN:
                total_matn_chars += seg_len

        # Layer transitions per page (>20 → warning)
        transitions = 0
        for j in range(1, len(segments)):
            if segments[j].layer_type != segments[j - 1].layer_type:
                transitions += 1
        if transitions > 20:
            result.add_warning(
                f"Excessive layer transitions ({transitions}) on unit_index={cu.unit_index}"
            )

        # author_canonical_id validation against layer_map
        for seg in segments:
            if seg.author_canonical_id is not None:
                if seg.author_canonical_id not in layer_map_ids:
                    result.add_warning(
                        f"author_canonical_id '{seg.author_canonical_id}' on "
                        f"unit_index={cu.unit_index} not found in layer_map"
                    )

    # Matn ratio check: >= 0.40 in sharh/hashiyah → warning
    if total_chars > 0:
        matn_ratio = total_matn_chars / total_chars
        genre = getattr(metadata, "genre", None)
        if matn_ratio >= 0.40 and genre in ("sharh", "hashiyah"):
            result.add_warning(
                f"High matn ratio ({matn_ratio:.2%}) for genre '{genre}' — "
                f"expected <40% matn in a commentary"
            )


# ──────────────────────────────────────────────────────────────────
# Check 5 — Division tree validity (SPEC lines 1488-1492)
# ──────────────────────────────────────────────────────────────────


def _validate_division_node(
    node: DivisionNode,
    parent: DivisionNode | None,
    result: ValidationResult,
    source_id: str,
) -> None:
    """Recursive validation of a single division node."""
    # start <= end
    if node.start_unit_index > node.end_unit_index:
        result.add_fatal(NormalizationError(
            code=NormErrorCode.SCHEMA_VIOLATION,
            message=(
                f"Division '{node.div_id}': start_unit_index={node.start_unit_index} "
                f"> end_unit_index={node.end_unit_index}"
            ),
            source_id=source_id,
            recovery="Fix division tree node ordering.",
        ))
        return

    # Child within parent bounds
    if parent is not None:
        if node.start_unit_index < parent.start_unit_index:
            result.add_fatal(NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message=(
                    f"Division '{node.div_id}' starts at {node.start_unit_index} "
                    f"before parent '{parent.div_id}' start at {parent.start_unit_index}"
                ),
                source_id=source_id,
                recovery="Fix child division to be within parent bounds.",
            ))
            return
        if node.end_unit_index > parent.end_unit_index:
            result.add_fatal(NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message=(
                    f"Division '{node.div_id}' ends at {node.end_unit_index} "
                    f"after parent '{parent.div_id}' end at {parent.end_unit_index}"
                ),
                source_id=source_id,
                recovery="Fix child division to be within parent bounds.",
            ))
            return

    # Sibling no-overlap: end_unit_index is INCLUSIVE, so overlap is
    # sibling[i].end_unit_index >= sibling[i+1].start_unit_index
    # Warning (not fatal) — structure_discovery may produce overlaps in
    # edge cases; the content units are valid regardless.
    children_sorted = sorted(node.children, key=lambda c: c.start_unit_index)
    for i in range(len(children_sorted) - 1):
        if children_sorted[i].end_unit_index >= children_sorted[i + 1].start_unit_index:
            result.add_warning(
                f"Division overlap: '{children_sorted[i].div_id}' "
                f"[{children_sorted[i].start_unit_index},{children_sorted[i].end_unit_index}] "
                f"overlaps with '{children_sorted[i+1].div_id}' "
                f"[{children_sorted[i+1].start_unit_index},{children_sorted[i+1].end_unit_index}]"
            )
            return

    # Recurse into children
    for child in node.children:
        _validate_division_node(child, node, result, source_id)
        if not result.passed:
            return


def _check_division_tree(
    package: NormalizedPackage,
    result: ValidationResult,
) -> None:
    """Validate division tree: ordering, no overlap, coverage."""
    source_id = package.manifest.source_id
    total_units = len(package.content_units)

    if not package.manifest.division_tree:
        return

    # Validate each top-level node recursively
    for node in package.manifest.division_tree:
        _validate_division_node(node, None, result, source_id)
        if not result.passed:
            return

    # Top-level sibling overlap check (warning — structure_discovery edge cases)
    top_sorted = sorted(
        package.manifest.division_tree, key=lambda n: n.start_unit_index
    )
    for i in range(len(top_sorted) - 1):
        if top_sorted[i].end_unit_index >= top_sorted[i + 1].start_unit_index:
            result.add_warning(
                f"Top-level division overlap: '{top_sorted[i].div_id}' "
                f"[{top_sorted[i].start_unit_index},{top_sorted[i].end_unit_index}] "
                f"overlaps with '{top_sorted[i+1].div_id}' "
                f"[{top_sorted[i+1].start_unit_index},{top_sorted[i+1].end_unit_index}]"
            )
            return

    # Full coverage: union of top-level divisions should cover [0, total_units - 1]
    # Warning (not fatal) if gaps — sparse structure valid per L-003
    if total_units > 0:
        covered: set[int] = set()
        for node in package.manifest.division_tree:
            for idx in range(node.start_unit_index, node.end_unit_index + 1):
                covered.add(idx)
        expected = set(range(total_units))
        gaps = expected - covered
        if gaps:
            result.add_warning(
                f"Division tree does not cover {len(gaps)} content unit(s): "
                f"gaps at indices {sorted(gaps)[:10]}{'...' if len(gaps) > 10 else ''}"
            )


# ──────────────────────────────────────────────────────────────────
# Check 6 — Footnote integrity (SPEC lines 1494-1497)
# ──────────────────────────────────────────────────────────────────

# Footnote ref pattern: ⌜N⌝ where N is ASCII digits. Use [0-9] not \d.
_FOOTNOTE_REF_RE = re.compile(r"\u231c([0-9]+)\u231d")


def _check_footnote_integrity(
    package: NormalizedPackage,
    result: ValidationResult,
) -> None:
    """Non-empty footnote text, orphan reference marker detection."""
    for cu in package.content_units:
        # Empty footnote text → warning
        for fn in cu.footnotes:
            if not fn.text.strip():
                result.add_warning(
                    f"Empty footnote text for ref_marker='{fn.ref_marker}' "
                    f"on unit_index={cu.unit_index}"
                )

        # Orphan footnote references: markers in text with no matching footnote
        ref_markers_in_text = _FOOTNOTE_REF_RE.findall(cu.primary_text)
        footnote_markers = {fn.ref_marker for fn in cu.footnotes}
        for marker in ref_markers_in_text:
            if marker not in footnote_markers:
                result.add_warning(
                    f"NORM_ORPHAN_FOOTNOTE_REF: marker ⌜{marker}⌝ in text "
                    f"on unit_index={cu.unit_index} has no matching footnote"
                )


# ──────────────────────────────────────────────────────────────────
# Check 7 — Unit index integrity (SPEC line 1499)
# ──────────────────────────────────────────────────────────────────


def _check_unit_index_integrity(
    package: NormalizedPackage,
    result: ValidationResult,
) -> None:
    """Contiguous zero-based sequence: 0, 1, 2, ..., N-1."""
    indices = sorted(cu.unit_index for cu in package.content_units)
    expected = list(range(len(package.content_units)))
    if indices != expected:
        result.add_fatal(NormalizationError(
            code=NormErrorCode.UNIT_INDEX_VIOLATION,
            message=f"Unit indices not contiguous: got {indices[:20]}{'...' if len(indices) > 20 else ''}, expected {expected[:20]}{'...' if len(expected) > 20 else ''}",
            source_id=package.manifest.source_id,
            recovery="Fix unit_index assignment to produce contiguous 0-based sequence.",
        ))


# ──────────────────────────────────────────────────────────────────
# Check 10 — Boundary continuity consistency (SPEC line 1505)
# ──────────────────────────────────────────────────────────────────

# Terminal punctuation that contradicts mid_sentence (D6-10)
_TERMINAL_PUNCT: set[str] = {".", "\u061f", "!"}  # period, Arabic ?, exclamation


def _check_boundary_continuity(
    package: NormalizedPackage,
    result: ValidationResult,
) -> None:
    """Validate boundary continuity fields for consistency."""
    if not package.content_units:
        return

    for i, cu in enumerate(package.content_units):
        is_last = i == len(package.content_units) - 1

        # (d) Last content unit must have boundary_continuity = None
        if is_last:
            if cu.boundary_continuity is not None:
                result.add_warning(
                    f"NORM_CONTINUITY_INCONSISTENT: last content unit "
                    f"(unit_index={cu.unit_index}) has boundary_continuity set"
                )
            continue

        if cu.boundary_continuity is None:
            continue

        # (a) Verify type is valid BoundaryContinuityType (Pydantic enforces,
        # but verify for packages constructed outside Pydantic)
        try:
            BoundaryContinuityType(cu.boundary_continuity.type)
        except ValueError:
            result.add_warning(
                f"NORM_CONTINUITY_INCONSISTENT: invalid boundary type "
                f"'{cu.boundary_continuity.type}' on unit_index={cu.unit_index}"
            )

        # (b) Confidence in range 0.0–1.0 (Pydantic enforces, verify explicitly)
        if not (0.0 <= cu.boundary_continuity.confidence <= 1.0):
            result.add_warning(
                f"NORM_CONTINUITY_INCONSISTENT: confidence "
                f"{cu.boundary_continuity.confidence} out of range on "
                f"unit_index={cu.unit_index}"
            )

        # (c) ADV-026: mid_sentence + terminal punctuation → contradiction
        if cu.boundary_continuity.type == BoundaryContinuityType.MID_SENTENCE:
            stripped = cu.primary_text.rstrip()
            if stripped and stripped[-1] in _TERMINAL_PUNCT:
                result.add_warning(
                    f"NORM_CONTINUITY_INCONSISTENT: mid_sentence but text ends "
                    f"with terminal punctuation '{stripped[-1]}' on "
                    f"unit_index={cu.unit_index}"
                )
                # Mutate: set confidence to 0.0
                cu.boundary_continuity.confidence = 0.0
