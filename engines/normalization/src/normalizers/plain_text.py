"""Plain text normalizer — SPEC §4.A.4c.

Transforms raw .txt files into the universal normalized format.
Handles paragraph splitting, encoding detection, and structure discovery
via keyword heuristics (Tier 2).

Key constraints:
  - No HTML or formatting signals available
  - Single-layer only (cannot detect layers from formatting)
  - Structure confidence typically low or minimal
  - Physical page numbers: null for all fields
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from engines.normalization.contracts import (
    BoundaryContinuity,
    ContentUnit,
    LayerMapEntry,
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
    PhysicalPage,
    QualityReport,
    StructuralFormat,
    StructuralMarkers,
    TextFidelity,
    TextFidelityLevel,
    TextFidelitySummary,
    TextLayerSegment,
)
from engines.normalization.src.boundary_continuity import classify_boundary
from engines.normalization.src.content_flagger import compute_content_flags
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.normalization.src.normalizers.base import BaseNormalizer
from engines.normalization.src.normalizers.shamela import CleanedPage
from engines.normalization.src.structure_discovery import StructureResult, discover_structure
from engines.normalization.src.validation import check_diacritics_page
from engines.source.contracts import Genre, SourceMetadata

logger = logging.getLogger(__name__)


class PlainTextNormalizer(BaseNormalizer):
    """Normalizer for raw .txt files (SPEC §4.A.4c)."""

    def validate_input(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> None:
        """Verify frozen_path contains readable .txt file(s)."""
        if frozen_path.is_file():
            if not frozen_path.suffix.lower() == ".txt":
                raise NormalizationError(
                    code=NormErrorCode.MISSING_FROZEN,
                    message=f"Expected .txt file, got '{frozen_path.suffix}'",
                    source_id=metadata.source_id,
                    recovery="Provide a .txt file or directory containing .txt files.",
                )
            if frozen_path.stat().st_size == 0:
                raise NormalizationError(
                    code=NormErrorCode.MISSING_FROZEN,
                    message=f"File is empty: {frozen_path}",
                    source_id=metadata.source_id,
                    recovery="Provide a non-empty .txt file.",
                )
        elif frozen_path.is_dir():
            txt_files = sorted(frozen_path.glob("*.txt"))
            if not txt_files:
                raise NormalizationError(
                    code=NormErrorCode.MISSING_FROZEN,
                    message=f"No .txt files found in directory: {frozen_path}",
                    source_id=metadata.source_id,
                    recovery="Provide a directory with at least one .txt file.",
                )
            # Check at least one has content
            if all(f.stat().st_size == 0 for f in txt_files):
                raise NormalizationError(
                    code=NormErrorCode.MISSING_FROZEN,
                    message=f"All .txt files in {frozen_path} are empty",
                    source_id=metadata.source_id,
                    recovery="Provide non-empty .txt files.",
                )
        else:
            raise NormalizationError(
                code=NormErrorCode.MISSING_FROZEN,
                message=f"Path does not exist: {frozen_path}",
                source_id=metadata.source_id,
                recovery="Provide a valid path to a .txt file or directory.",
            )

    def normalize(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> NormalizedPackage:
        """Transform plain text into a NormalizedPackage."""
        # 1. Read source file(s)
        raw_text, fidelity_level = self._read_source(frozen_path, metadata)

        # 2. Split into content unit segments (D6-6)
        segments = self._split_into_segments(raw_text)

        if not segments:
            raise NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message="No content segments produced from plain text input",
                source_id=metadata.source_id,
                recovery="Ensure the input file contains text content.",
            )

        # 3-4. Build CleanedPage objects for downstream processing + diacritics check
        cleaned_pages = self._build_cleaned_pages(
            segments, raw_text, metadata.source_id,
        )

        # 5. Structure discovery
        genre: Optional[Genre] = None
        genre_str = getattr(metadata, "genre", None)
        if genre_str:
            try:
                genre = Genre(genre_str)
            except ValueError as exc:
                raise NormalizationError(
                    code=NormErrorCode.SCHEMA_VIOLATION,
                    message=f"Invalid source genre value: {genre_str!r}",
                    source_id=metadata.source_id,
                    recovery="Repair SourceMetadata.genre before normalization.",
                ) from exc

        structure = discover_structure(
            cleaned_pages, metadata.source_id, genre,
        )

        # 6. Determine layer type
        layer_type = LayerType.MATN
        if metadata.is_multi_layer:
            layer_type = LayerType.SHARH  # conservative default per SPEC

        # 7-9. Assemble package
        return self._assemble_package(
            cleaned_pages=cleaned_pages,
            metadata=metadata,
            structure=structure,
            fidelity_level=fidelity_level,
            layer_type=layer_type,
        )

    # ──────────────────────────────────────────────────────────────
    # Internal methods
    # ──────────────────────────────────────────────────────────────

    def _read_source(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> tuple[str, TextFidelityLevel]:
        """Read source file(s) with encoding detection."""
        fidelity = TextFidelityLevel.HIGH

        if frozen_path.is_file():
            files = [frozen_path]
        else:
            files = sorted(frozen_path.glob("*.txt"))

        parts: list[str] = []
        for f in files:
            text, file_fidelity = self._read_single_file(f, metadata.source_id)
            parts.append(text)
            if file_fidelity == TextFidelityLevel.LOW:
                fidelity = TextFidelityLevel.LOW

        return "\n\n".join(parts), fidelity

    def _read_single_file(
        self,
        file_path: Path,
        source_id: str,
    ) -> tuple[str, TextFidelityLevel]:
        """Read a single file with encoding fallback chain."""
        # Try UTF-8 strict first
        try:
            return file_path.read_text(encoding="utf-8", errors="strict"), TextFidelityLevel.HIGH
        except UnicodeDecodeError:
            pass

        # Fallback: charset_normalizer detection
        try:
            import charset_normalizer
            raw_bytes = file_path.read_bytes()
            detected = charset_normalizer.detect(raw_bytes)
            enc_name = detected.get("encoding") if detected else None
            if enc_name is not None:
                encoding: str = enc_name
                text = raw_bytes.decode(encoding, errors="strict")
                logger.warning(
                    "[%s] NORM_ENCODING_ERROR: UTF-8 failed, detected encoding '%s'",
                    source_id, encoding,
                )
                return text, TextFidelityLevel.HIGH
        except (ImportError, UnicodeDecodeError, LookupError):
            pass

        # Last resort: UTF-8 with replacement characters
        logger.warning(
            "[%s] NORM_ENCODING_ERROR: all encoding detection failed, "
            "using UTF-8 with replacement",
            source_id,
        )
        return file_path.read_text(encoding="utf-8", errors="replace"), TextFidelityLevel.LOW

    def _split_into_segments(self, raw_text: str) -> list[str]:
        """Split text into content unit segments (D6-6).

        0. Normalize CRLF first
        1. Split at double newlines
        2. Split long segments (>3000 chars) at ~2000 char whitespace boundary
        3. Merge consecutive short segments (<1000 chars)
        4. Discard empty segments
        """
        # Step 0: CRLF normalization (critical for Windows — D6-6)
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

        # Step 1: Split at double newlines
        raw_segments = text.split("\n\n")

        # Remove empty/whitespace-only segments
        raw_segments = [s.strip() for s in raw_segments if s.strip()]

        if not raw_segments:
            return []

        # Step 2: Split long segments at ~2000 char whitespace boundary
        split_segments: list[str] = []
        for seg in raw_segments:
            if len(seg) > 3000:
                split_segments.extend(self._split_long_segment(seg))
            else:
                split_segments.append(seg)

        # Step 3: Merge consecutive short segments
        merged: list[str] = []
        for seg in split_segments:
            if merged and len(merged[-1]) < 1000 and len(seg) < 1000:
                merged[-1] = merged[-1] + "\n\n" + seg
            else:
                merged.append(seg)

        return merged

    @staticmethod
    def _split_long_segment(text: str) -> list[str]:
        """Split a segment >3000 chars at whitespace nearest to 2000."""
        result: list[str] = []
        remaining = text
        while len(remaining) > 3000:
            # Find whitespace nearest to position 2000
            split_pos = 2000
            # Search backward for whitespace
            while split_pos > 0 and not remaining[split_pos].isspace():
                split_pos -= 1
            if split_pos == 0:
                # No whitespace found — split at 2000 anyway
                split_pos = 2000
            result.append(remaining[:split_pos].strip())
            remaining = remaining[split_pos:].strip()
        if remaining.strip():
            result.append(remaining.strip())
        return result

    def _build_cleaned_pages(
        self,
        segments: list[str],
        raw_text: str,
        source_id: str,
    ) -> list[CleanedPage]:
        """Build CleanedPage objects from text segments.

        Also runs §5 check 8 (diacritics) since plain text has minimal
        processing that could cause drift.
        """
        pages: list[CleanedPage] = []
        for i, seg in enumerate(segments):
            # Diacritics check 8: for plain text, drift can only come from
            # encoding conversion. Compare segment to itself (after any
            # encoding transformations that already happened).
            if not check_diacritics_page(seg, seg):
                raise NormalizationError(
                    code=NormErrorCode.DIACRITICS_DRIFT,
                    message=f"Diacritics drift on plain text segment {i}",
                    source_id=source_id,
                    unit_index=i,
                    recovery="Investigate encoding conversion that modified diacritics.",
                )

            pages.append(CleanedPage(
                unit_index=i,
                volume=1,
                primary_text=seg,
                bold_spans=[],
                font_size_spans=[],
                title_spans=[],
            ))

        return pages

    def _assemble_package(
        self,
        cleaned_pages: list[CleanedPage],
        metadata: SourceMetadata,
        structure: StructureResult,
        fidelity_level: TextFidelityLevel,
        layer_type: LayerType,
    ) -> NormalizedPackage:
        """Build the final NormalizedPackage from processed data."""
        toc_set = set(structure.toc_page_indices)

        content_units: list[ContentUnit] = []
        pages_with_warnings = 0

        for i, page in enumerate(cleaned_pages):
            # Content flags
            flags = compute_content_flags(page, page.unit_index in toc_set)

            # Boundary continuity — None for last page
            boundary: Optional[BoundaryContinuity] = None
            if i < len(cleaned_pages) - 1:
                next_page = cleaned_pages[i + 1]
                cur_markers = structure.page_markers.get(page.unit_index)
                nxt_markers = structure.page_markers.get(next_page.unit_index)
                boundary = classify_boundary(
                    page, next_page, cur_markers, nxt_markers, False,
                )

            # Single text layer segment covering entire text
            text_layers = []
            if page.primary_text:
                text_layers = [
                    TextLayerSegment(
                        layer_type=layer_type,
                        author_canonical_id=None,
                        start=0,
                        end=len(page.primary_text),
                        confidence=1.0,
                    ),
                ]

            # Structural markers
            markers = structure.page_markers.get(
                page.unit_index,
                StructuralMarkers(
                    heading_detected=False,
                    heading_text=None,
                    heading_level=None,
                    heading_detection_method=None,
                    heading_confidence=None,
                ),
            )

            # Text fidelity
            text_fidelity = TextFidelity(
                score=fidelity_level,
                ocr_confidence=None,
            )

            if page.warnings:
                pages_with_warnings += 1

            content_units.append(ContentUnit(
                source_id=metadata.source_id,
                unit_index=page.unit_index,
                physical_page=PhysicalPage(
                    volume=None,
                    page_number_display=None,
                    page_number_int=None,
                ),
                primary_text=page.primary_text,
                text_layers=text_layers,
                footnotes=[],
                structural_markers=markers,
                content_flags=flags,
                text_fidelity=text_fidelity,
                boundary_continuity=boundary,
                verse_info=None,
                discourse_flow=None,
            ))

        # Layer map
        layer_map = [
            LayerMapEntry(
                layer_type=layer_type,
                author_canonical_id=None,
                confidence=1.0,
            ),
        ]

        # Structural format
        try:
            structural_format = StructuralFormat(metadata.structural_format)
        except ValueError as exc:
            raise NormalizationError(
                code=NormErrorCode.SCHEMA_VIOLATION,
                message=f"Invalid source structural_format value: {metadata.structural_format!r}",
                source_id=metadata.source_id,
                recovery="Repair SourceMetadata.structural_format before normalization.",
            ) from exc

        # Quality report
        quality_report = QualityReport(
            division_count_by_tier=dict(structure.quality_counts),
            layer_transition_count=0,
            pages_with_warnings=pages_with_warnings,
            high_fidelity_pct=1.0 if fidelity_level == TextFidelityLevel.HIGH else 0.0,
            unclassified_footnote_count=0,
            overall_confidence=structure.overall_confidence,
        )

        # Text fidelity summary
        fidelity_summary = TextFidelitySummary(
            mean_ocr_confidence=None,
            character_level_fidelity_estimate=None,
            pages_with_warnings=pages_with_warnings,
            total_pages=len(content_units),
        )

        # Manifest
        manifest = NormalizedManifest(
            source_id=metadata.source_id,
            normalizer_id="kr.normalization.plain_text_v1",
            normalization_utc=datetime.now(timezone.utc).isoformat(),
            division_tree=structure.division_tree,
            layer_map=layer_map,
            structural_format=structural_format,
            structural_format_proposed=None,
            text_fidelity_summary=fidelity_summary,
            verse_detection=False,
            verse_numbering_scheme=None,
            total_content_units=len(content_units),
            quality_report=quality_report,
            # Deferred §4.B fields
            content_census=None,
            tahqiq_topology=None,
            layer_fingerprints=None,
            discourse_flow_summary=None,
        )

        return NormalizedPackage(
            manifest=manifest,
            content_units=content_units,
        )
