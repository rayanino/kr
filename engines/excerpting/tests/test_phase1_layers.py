"""Tests for §4.6 — Text layer rebasing."""

from __future__ import annotations

import pytest

from engines.excerpting.contracts import JoinPoint
from engines.excerpting.src.phase1_assembly import rebase_text_layers
from engines.excerpting.tests.conftest import _make_content_unit
from engines.normalization.contracts import (
    BoundaryContinuityType,
    LayerType,
    TextLayerSegment,
)


# ═══════════════════════════════════════════════════════════════════
# rebase_text_layers
# ═══════════════════════════════════════════════════════════════════


class TestRebaseTextLayers:
    """Tests for rebase_text_layers (§4.6)."""

    def test_rebase_single_unit(self) -> None:
        """Single unit: no offset change needed."""
        text = "بسم الله الرحمن الرحيم"
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=len(text),
                        confidence=1.0,
                    )
                ],
            )
        ]
        result = rebase_text_layers(units, [0], [], len(text))
        assert len(result) == 1
        assert result[0].start == 0
        assert result[0].end == len(text)

    def test_rebase_multi_unit(self) -> None:
        """Two units with separator: cumulative offset includes separator length."""
        text_0 = "الحمد لله"
        text_1 = "رب العالمين"
        sep = "\n"  # mid_paragraph separator

        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text_0,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=len(text_0),
                        confidence=1.0,
                    )
                ],
            ),
            _make_content_unit(
                unit_index=1,
                primary_text=text_1,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=len(text_1),
                        confidence=1.0,
                    )
                ],
            ),
        ]
        assembled_len = len(text_0) + len(sep) + len(text_1)
        jps = [
            JoinPoint(
                after_unit_index=0,
                before_unit_index=1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used=sep,
                char_offset_in_assembled=len(text_0),
            )
        ]
        result = rebase_text_layers(units, [0, 1], jps, assembled_len)
        # Should produce segments covering [0, assembled_len)
        # First unit: [0, len(text_0))
        # Second unit: [len(text_0)+1, assembled_len)
        assert result[-1].end == assembled_len

    def test_merge_adjacent_segments(self) -> None:
        """Same layer_type + author → merged after rebasing."""
        text_0 = "أولاً"
        text_1 = "ثانياً"
        sep = "\n"
        assembled_len = len(text_0) + len(sep) + len(text_1)

        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text_0,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id="sch_001",
                        start=0,
                        end=len(text_0),
                        confidence=1.0,
                    )
                ],
            ),
            _make_content_unit(
                unit_index=1,
                primary_text=text_1,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id="sch_001",
                        start=0,
                        end=len(text_1),
                        confidence=1.0,
                    )
                ],
            ),
        ]
        jps = [
            JoinPoint(
                after_unit_index=0,
                before_unit_index=1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used=sep,
                char_offset_in_assembled=len(text_0),
            )
        ]
        result = rebase_text_layers(units, [0, 1], jps, assembled_len)
        # Adjacent same-type segments should merge into one
        assert len(result) == 1
        assert result[0].start == 0
        assert result[0].end == assembled_len

    def test_coverage_invariant(self) -> None:
        """I-AC-2: exact coverage [0, len) after rebasing."""
        text = "كتاب الله"
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=len(text),
                        confidence=1.0,
                    )
                ],
            )
        ]
        result = rebase_text_layers(units, [0], [], len(text))
        # Verify continuous coverage
        total_covered = sum(s.end - s.start for s in result)
        assert total_covered == len(text)
        assert result[0].start == 0
        assert result[-1].end == len(text)

    def test_clamping(self) -> None:
        """Segment overflow → clamped + EX-A-004."""
        text = "قصير"  # 4 chars
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=100,  # Way too big — will be clamped
                        confidence=1.0,
                    )
                ],
            )
        ]
        result = rebase_text_layers(units, [0], [], len(text))
        assert result[0].end == len(text)  # Clamped to text length

    def test_gap_detection(self) -> None:
        """Missing coverage within a unit → EX-A-003 raises ValueError."""
        text = "كتاب الله"
        # Two non-contiguous layers with a gap between them
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=3,
                        confidence=1.0,
                    ),
                    TextLayerSegment(
                        layer_type=LayerType.SHARH,
                        author_canonical_id=None,
                        start=5,  # Gap at [3, 5)
                        end=len(text),
                        confidence=1.0,
                    ),
                ],
            )
        ]
        with pytest.raises(ValueError, match="I-AC-2"):
            rebase_text_layers(units, [0], [], len(text))
