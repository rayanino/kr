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
    AuthorAttribution,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    PageRange,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
)
from engines.normalization.contracts import (
    LayerMapEntry,
    NormalizedManifest,
    TextLayerSegment,
)

logger = logging.getLogger(__name__)

# §7.1 F-DET-5: Quran verse delimiters (ornate parentheses)
_QURAN_VERSE_RE = re.compile(r"\uFD3F[^\uFD3E]+\uFD3E")


def compute_excerpt_id(
    source_id: str,
    div_id: str,
    chunk_index: int,
    unit_index: int,
) -> str:
    """F-DET-1: Globally unique excerpt identifier (§7.1).

    Format: exc_{source_id}_{div_id}_{chunk_index}_{unit_index}.
    """
    raise NotImplementedError


def extract_primary_text(
    assembled_text: str,
    start_word: int,
    end_word: int,
) -> str:
    """F-DET-2: Extract teaching unit text as a substring (§7.1).

    Uses word-to-character offset conversion. Preserves all original
    whitespace (newlines, paragraph breaks). This is a substring, not
    a split-and-rejoin — the difference matters for I-ER-2.
    """
    raise NotImplementedError


def compute_layer_attribution(
    assembled_text: str,
    text_layers: list[TextLayerSegment],
    start_word: int,
    end_word: int,
    layer_map: list[LayerMapEntry],
    layer_split_points: list[int],
) -> AuthorAttribution:
    """F-DET-3: Primary author layer attribution (§7.1, §6.2 LA-1–LA-4).

    LA-1: Dominant layer (>=80% of unit's character range) → primary.
    LA-2: Layer transition markers within unit → split attribution.
    LA-3: Ambiguous (no layer >=80%) → emit EX-M-001, consensus verification.
    LA-4: Editor footnotes → treat as scholarly commentary.

    layer_split_points: split-induced boundaries treated as non-meaningful
    (consecutive segments with same type/author across split point = one span).
    """
    raise NotImplementedError


def compute_content_types(
    segments: list[tuple[int, ScholarlyFunction]],
) -> list[ScholarlyFunction]:
    """F-DET-4: Deduplicated list of scholarly functions in this unit (§7.1)."""
    raise NotImplementedError


def detect_quran_verses(primary_text: str) -> bool:
    """F-DET-5: Detect Quran verse citations using ﴿...﴾ delimiters (§7.1)."""
    raise NotImplementedError


def compute_page_range(
    physical_pages: list,
    start_word: int,
    end_word: int,
) -> Optional[PageRange]:
    """F-DET-6: Physical page range for this excerpt (§7.1)."""
    raise NotImplementedError


def compute_word_offsets(
    start_word: int, end_word: int
) -> tuple[int, int]:
    """F-DET-7: Word offsets in assembled_text coordinate space (§7.1)."""
    raise NotImplementedError


def filter_relevant_footnotes(
    primary_text: str,
    all_footnotes: list,
) -> list:
    """F-DET-8: Footnotes whose ⌜N⌝ markers appear in this unit's text (§7.1)."""
    raise NotImplementedError


def compute_segment_indices(unit: TeachingUnit) -> list[int]:
    """F-DET-9: Segment indices composing this unit (§7.1)."""
    raise NotImplementedError


def build_deterministic_excerpts(
    chunks: list[AssembledChunk],
    grouped: dict[str, list[TeachingUnit]],
    classified: dict[str, list],
    manifest: NormalizedManifest,
    config: ExcerptingConfig,
) -> list[ExcerptRecord]:
    """Assemble ExcerptRecords with all deterministic fields populated (§7.1).

    LLM-enriched fields (excerpt_topic, school, takhrij, etc.) are set to
    None/empty — filled by phase3_enrichment.py.

    Returns one ExcerptRecord per TeachingUnit across all chunks.
    """
    raise NotImplementedError
