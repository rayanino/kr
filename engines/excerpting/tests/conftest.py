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
    LayerType,
    PhysicalPage,
    StructuralFormat,
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
