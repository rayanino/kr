"""Test factory helpers for excerpting engine.

Each factory returns a valid instance with all required fields populated
with sensible defaults. Tests pass only the fields they care about via
**overrides. Follows the exact pattern from engines/normalization/tests/conftest.py.
"""

from __future__ import annotations

from typing import Any

from engines.excerpting.contracts import (
    AssembledChunk,
    AssemblyMetadata,
    AuthorAttribution,
    ClassifiedSegment,
    ExcerptRecord,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
)
from engines.normalization.contracts import (
    ContentFlags,
    ContentUnit,
    DivisionNode,
    Footnote,
    FootnoteType,
    HeadingConfidence,
    HeadingDetectionMethod,
    LayerMapEntry,
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
    PhysicalPage,
    QualityReport,
    StructuralFormat,
    TextFidelity,
    TextFidelityLevel,
    TextFidelitySummary,
    TextLayerSegment,
)


# ═══════════════════════════════════════════════════════════════════
# Default values computed once at import time
# ═══════════════════════════════════════════════════════════════════

_DEFAULT_AC_TEXT = "بسم الله الرحمن الرحيم الحمد لله رب العالمين"
_DEFAULT_AC_TOKENS = _DEFAULT_AC_TEXT.split()
_DEFAULT_AC_TOTAL_TOKENS = len(_DEFAULT_AC_TOKENS)
_DEFAULT_AC_WORD_COUNT = sum(
    1
    for t in _DEFAULT_AC_TOKENS
    if any("\u0600" <= c <= "\u06FF" for c in t)
)


# ═══════════════════════════════════════════════════════════════════
# Factory functions
# ═══════════════════════════════════════════════════════════════════


def _make_assembled_chunk(**overrides: Any) -> AssembledChunk:
    """Factory for AssembledChunk with valid defaults.

    Default text: "بسم الله الرحمن الرحيم الحمد لله رب العالمين"
    Satisfies I-AC-1 (word/token counts), I-AC-2 (layer coverage),
    I-AC-7 (merge/split mutual exclusion).
    """
    defaults: dict[str, Any] = {
        "chunk_id": "div_test_1_0",
        "source_id": "src_test",
        "div_id": "div_test_1_0",
        "div_path": ["باب الاختبار"],
        "assembled_text": _DEFAULT_AC_TEXT,
        "word_count": _DEFAULT_AC_WORD_COUNT,
        "total_tokens": _DEFAULT_AC_TOTAL_TOKENS,
        "text_layers": [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(_DEFAULT_AC_TEXT),
                confidence=1.0,
            )
        ],
        "footnotes": [],
        "content_flags": ContentFlags(),
        "physical_pages": [
            PhysicalPage(volume=1, page_number_display="١", page_number_int=1)
        ],
        "structural_format": StructuralFormat.PROSE,
        "heading_alignment_ok": True,
        "assembly_metadata": AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        ),
        "merge_history": None,
        "split_info": None,
    }
    defaults.update(overrides)
    return AssembledChunk(**defaults)


def _make_classified_segment(**overrides: Any) -> ClassifiedSegment:
    """Factory for ClassifiedSegment with valid defaults."""
    defaults: dict[str, Any] = {
        "segment_index": 0,
        "start_word": 0,
        "end_word": 4,
        "text_snippet": "بسم الله الرحمن الرحيم الحمد"[:50],
        "scholarly_function": ScholarlyFunction.DEFINITION,
        "confidence": 0.9,
    }
    defaults.update(overrides)
    return ClassifiedSegment(**defaults)


def _make_teaching_unit(**overrides: Any) -> TeachingUnit:
    """Factory for TeachingUnit with valid defaults.

    Satisfies I-TU-6 (FULL -> no notes) and I-TU-8 (>=5 Arabic words).
    """
    defaults: dict[str, Any] = {
        "unit_index": 0,
        "segment_indices": [0],
        "start_word": 0,
        "end_word": 4,
        "text_snippet": _DEFAULT_AC_TEXT[:80],
        "primary_function": ScholarlyFunction.DEFINITION,
        "secondary_functions": [],
        "description_arabic": "وصف عربي قصير للاختبار يتضمن عدة كلمات",
        "self_containment": SelfContainmentLevel.FULL,
        "self_containment_notes": None,
    }
    defaults.update(overrides)
    return TeachingUnit(**defaults)


def _make_excerpt_record(**overrides: Any) -> ExcerptRecord:
    """Factory for ExcerptRecord with valid defaults.

    Satisfies I-ER-4 (FULL -> no notes/hint), I-ER-5 (non-null layer_id/author_id),
    and DD8 (school explicitly passed as None — Pattern 1, no default on model).
    """
    defaults: dict[str, Any] = {
        # Identification
        "excerpt_id": "exc_src_test_div_test_0_0",
        "source_id": "src_test",
        "div_id": "div_test",
        "chunk_index": 0,
        "unit_index": 0,
        "div_path": ["باب الاختبار"],
        # Text
        "primary_text": "بسم الله الرحمن الرحيم",
        "text_snippet": "بسم الله الرحمن الرحيم"[:80],
        "start_word": 0,
        "end_word": 3,
        "segment_indices": [0],
        "physical_pages": None,
        # Classification
        "primary_function": ScholarlyFunction.DEFINITION,
        "secondary_functions": [],
        "content_types": [ScholarlyFunction.DEFINITION],
        "description_arabic": "وصف عربي قصير للاختبار يتضمن عدة كلمات",
        "structural_section": None,
        # Self-containment (I-ER-4: FULL -> no notes, no hint)
        "self_containment": SelfContainmentLevel.FULL,
        "self_containment_notes": None,
        "context_hint": None,
        # Attribution (I-ER-5: non-null layer_id/author_id)
        "primary_author_layer": AuthorAttribution(
            layer_id="layer_matn",
            author_id="sch_test",
            coverage_pct=1.0,
            rule_applied="LA-1",
        ),
        "attribution_confidence": None,
        "quoted_scholars": [],
        "school": None,  # DD8 Pattern 1 — must be explicitly passed
        "school_confidence": None,
        # Topic
        "excerpt_topic": ["اختبار"],
        "terminology_variants": [],
        # Evidence
        "evidence_refs": [],
        "takhrij_data": None,
        "cross_references": [],
        "footnotes_relevant": [],
        # Metadata
        "consensus_metadata": None,
        "gate_flags": [],
        "review_flags": [],
    }
    defaults.update(overrides)
    return ExcerptRecord(**defaults)


# ═══════════════════════════════════════════════════════════════════
# Phase 2 test helpers (Session 2)
# ═══════════════════════════════════════════════════════════════════


def _make_mock_instructor_client(
    return_value: Any = None,
    side_effect: Any = None,
) -> Any:
    """Return a MagicMock configured as an instructor client.

    Mocks ``client.chat.completions.create()`` to return *return_value*
    or raise via *side_effect*.
    """
    from unittest.mock import MagicMock

    client = MagicMock()
    create_mock = client.chat.completions.create
    if side_effect is not None:
        create_mock.side_effect = side_effect
    elif return_value is not None:
        create_mock.return_value = return_value
    return client


def _make_classification_result(
    assembled_text: str,
    n_segments: int = 3,
) -> "ClassificationResult":
    """Build a valid ClassificationResult with *n_segments* segments.

    Each segment's ``text_snippet`` is extracted from *assembled_text*
    at evenly spaced positions so that ``normalize_offsets`` can anchor them.
    """
    from engines.excerpting.contracts import ClassificationResult

    tokens = assembled_text.split()
    total = len(tokens)
    segments: list[ClassifiedSegment] = []

    for i in range(n_segments):
        # Compute approximate start token for each segment
        tok_start = (total * i) // n_segments
        # Find character position for this token
        char_pos = 0
        for t_idx, tok in enumerate(tokens):
            if t_idx == tok_start:
                break
            char_pos = assembled_text.index(tok, char_pos) + len(tok)
        char_pos = assembled_text.index(tokens[tok_start], char_pos)
        snippet = assembled_text[char_pos : char_pos + 50]

        segments.append(
            ClassifiedSegment(
                segment_index=i,
                start_word=tok_start * 2,  # deliberately wrong (LLM offsets)
                end_word=tok_start * 2 + 10,
                text_snippet=snippet,
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        )

    return ClassificationResult(
        segments=segments,
        total_segments=n_segments,
    )


# ═══════════════════════════════════════════════════════════════════
# Phase 1 factory helpers (Session 1)
# ═══════════════════════════════════════════════════════════════════

_DEFAULT_CU_TEXT = "بسم الله الرحمن الرحيم وبعد فهذا كتاب في النحو"


def _make_content_unit(**overrides: Any) -> ContentUnit:
    """ContentUnit factory with valid defaults. One per physical page.

    Auto-generates a single MATN text_layer covering [0, len(primary_text)).
    Default: no boundary_continuity, no footnotes, no flags.
    """
    primary_text = overrides.pop("primary_text", _DEFAULT_CU_TEXT)
    fields: dict[str, Any] = {
        "source_id": "src_test",
        "unit_index": 0,
        "physical_page": PhysicalPage(
            volume=1, page_number_display=None, page_number_int=None
        ),
        "primary_text": primary_text,
        "text_layers": [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(primary_text),
                confidence=1.0,
            )
        ],
        "footnotes": [],
        "content_flags": ContentFlags(),
        "text_fidelity": TextFidelity(
            score=TextFidelityLevel.HIGH, ocr_confidence=None
        ),
        "boundary_continuity": None,
        "verse_info": None,
        "discourse_flow": None,
    }
    fields.update(overrides)
    return ContentUnit(**fields)


def _make_division_node(**overrides: Any) -> DivisionNode:
    """DivisionNode factory with valid defaults."""
    defaults: dict[str, Any] = {
        "div_id": "div_test_1_0",
        "division_type": None,
        "heading_text": "باب الاختبار",
        "heading_level": 1,
        "start_unit_index": 0,
        "end_unit_index": 0,
        "detection_method": HeadingDetectionMethod.KEYWORD_HEURISTIC,
        "confidence": HeadingConfidence.HIGH,
        "children": [],
    }
    defaults.update(overrides)
    return DivisionNode(**defaults)


def _make_normalized_package(**overrides: Any) -> NormalizedPackage:
    """Minimal valid NormalizedPackage: 1 division, 2 content units.

    Builds content_units and manifest unless overridden.
    Root division covering all units.
    """
    source_id = overrides.pop("source_id", "src_test")
    num_units = overrides.pop("num_units", 2)
    primary_text = overrides.pop("primary_text", _DEFAULT_CU_TEXT)

    # Build content units unless overridden
    content_units = overrides.pop("content_units", None)
    if content_units is None:
        content_units = [
            _make_content_unit(
                primary_text=primary_text,
                unit_index=i,
                source_id=source_id,
            )
            for i in range(num_units)
        ]

    # Build manifest unless overridden
    manifest = overrides.pop("manifest", None)
    if manifest is None:
        division_tree = overrides.pop(
            "division_tree",
            [
                DivisionNode(
                    div_id=f"div_{source_id}_0_0",
                    division_type=None,
                    heading_text="باب الاختبار",
                    heading_level=0,
                    start_unit_index=0,
                    end_unit_index=max(0, len(content_units) - 1),
                    detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                    confidence=HeadingConfidence.HIGH,
                ),
            ],
        )
        manifest_fields: dict[str, Any] = {
            "source_id": source_id,
            "normalizer_id": "kr.normalization.test_v1",
            "normalization_utc": "2026-01-01T00:00:00+00:00",
            "division_tree": division_tree,
            "layer_map": [
                LayerMapEntry(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    confidence=1.0,
                ),
            ],
            "structural_format": StructuralFormat.PROSE,
            "text_fidelity_summary": TextFidelitySummary(
                mean_ocr_confidence=None,
                character_level_fidelity_estimate=None,
                pages_with_warnings=0,
                total_pages=len(content_units),
            ),
            "total_content_units": len(content_units),
            "quality_report": QualityReport(),
        }
        manifest_fields.update(overrides)
        manifest = NormalizedManifest(**manifest_fields)

    return NormalizedPackage(
        manifest=manifest,
        content_units=content_units,
    )


def _make_division_tree(
    leaf_count: int,
    source_id: str = "src_test",
    total_units: int = 10,
) -> list[DivisionNode]:
    """Generate a division tree with one root and leaf_count child leaves.

    Each leaf covers a proportional range of unit_indices.
    """
    if leaf_count <= 0:
        return []

    if leaf_count == 1:
        return [
            DivisionNode(
                div_id=f"div_{source_id}_0_0",
                division_type=None,
                heading_text="باب الاختبار",
                heading_level=0,
                start_unit_index=0,
                end_unit_index=max(0, total_units - 1),
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
            )
        ]

    # Multiple leaves under one root
    units_per_leaf = max(1, total_units // leaf_count)
    children: list[DivisionNode] = []
    for i in range(leaf_count):
        start = i * units_per_leaf
        end = min(start + units_per_leaf - 1, total_units - 1)
        if i == leaf_count - 1:
            end = total_units - 1  # Last leaf gets remainder
        children.append(
            DivisionNode(
                div_id=f"div_{source_id}_1_{i}",
                division_type=None,
                heading_text=f"فصل {i + 1}",
                heading_level=1,
                start_unit_index=start,
                end_unit_index=end,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
            )
        )

    root = DivisionNode(
        div_id=f"div_{source_id}_0_0",
        division_type=None,
        heading_text="كتاب الاختبار",
        heading_level=0,
        start_unit_index=0,
        end_unit_index=total_units - 1,
        detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
        confidence=HeadingConfidence.HIGH,
        children=children,
    )
    return [root]


# ═══════════════════════════════════════════════════════════════════
# Phase 3 test helpers (Session 3)
# ═══════════════════════════════════════════════════════════════════

# Real Arabic text for multi-layer testing: matn + sharh
_MATN_TEXT = "قال ابن مالك كلامنا لفظ مفيد كاستقم"
_SHARH_TEXT = "يريد أن الكلام في اصطلاح النحويين هو اللفظ المفيد فائدة يحسن السكوت عليها"
_MULTI_LAYER_TEXT = _MATN_TEXT + " " + _SHARH_TEXT
_MATN_END = len(_MATN_TEXT)
_SHARH_START = _MATN_END + 1  # +1 for the space between


def _make_multi_layer_chunk(**overrides: Any) -> AssembledChunk:
    """AssembledChunk with MATN + SHARH layers for attribution testing.

    Default text: matn (40%) + sharh (60%), two layer segments,
    both with author_canonical_id set.
    """
    text = overrides.pop("assembled_text", _MULTI_LAYER_TEXT)
    tokens = text.split()
    total = len(tokens)
    word_count = sum(
        1 for t in tokens if any("\u0600" <= c <= "\u06FF" for c in t)
    )

    matn_end = overrides.pop("matn_end", _MATN_END)
    sharh_start = overrides.pop("sharh_start", _SHARH_START)

    defaults: dict[str, Any] = {
        "chunk_id": "div_ml_test_0",
        "source_id": "src_ml_test",
        "div_id": "div_ml_test_0",
        "div_path": ["كتاب الألفية", "باب الكلام"],
        "assembled_text": text,
        "word_count": word_count,
        "total_tokens": total,
        "text_layers": [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_ibn_malik",
                start=0,
                end=matn_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_ibn_aqeel",
                start=sharh_start,
                end=len(text),
                confidence=1.0,
            ),
        ],
        "footnotes": [],
        "content_flags": ContentFlags(),
        "physical_pages": [
            PhysicalPage(volume=1, page_number_display="١", page_number_int=1)
        ],
        "structural_format": StructuralFormat.PROSE,
        "heading_alignment_ok": True,
        "assembly_metadata": AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        ),
        "merge_history": None,
        "split_info": None,
    }
    defaults.update(overrides)
    return AssembledChunk(**defaults)


# Text with embedded footnote markers for F-DET-8 testing
_FN_TEXT = "وقال النبي صلى الله عليه وسلم ⌜1⌝ من توضأ فأحسن الوضوء ⌜2⌝ خرجت خطاياه"
_FN_TOKENS = _FN_TEXT.split()


def _make_chunk_with_footnotes(**overrides: Any) -> AssembledChunk:
    """AssembledChunk with ⌜1⌝ and ⌜2⌝ footnote markers in the text.

    Default: two footnotes with ref_marker="1" and "2" matching
    markers embedded in assembled_text.
    """
    text = overrides.pop("assembled_text", _FN_TEXT)
    tokens = text.split()
    total = len(tokens)
    word_count = sum(
        1 for t in tokens if any("\u0600" <= c <= "\u06FF" for c in t)
    )

    defaults: dict[str, Any] = {
        "chunk_id": "div_fn_test_0",
        "source_id": "src_fn_test",
        "div_id": "div_fn_test_0",
        "div_path": ["باب الطهارة"],
        "assembled_text": text,
        "word_count": word_count,
        "total_tokens": total,
        "text_layers": [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ],
        "footnotes": [
            Footnote(
                ref_marker="1",
                text="متفق عليه من حديث عثمان رضي الله عنه",
                footnote_type=FootnoteType.HADITH_TAKHRIJ,
                confidence=0.95,
            ),
            Footnote(
                ref_marker="2",
                text="أي أتم أركانه وشروطه",
                footnote_type=FootnoteType.LINGUISTIC_NOTE,
                confidence=0.90,
            ),
        ],
        "content_flags": ContentFlags(),
        "physical_pages": [
            PhysicalPage(volume=1, page_number_display="٥", page_number_int=5)
        ],
        "structural_format": StructuralFormat.PROSE,
        "heading_alignment_ok": True,
        "assembly_metadata": AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        ),
        "merge_history": None,
        "split_info": None,
    }
    defaults.update(overrides)
    return AssembledChunk(**defaults)
