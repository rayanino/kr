"""Tests for §4.9 — Phase 1 self-validation (V-P1-1 through V-P1-6)."""

from __future__ import annotations

import pytest

from engines.excerpting.contracts import (
    AssemblyMetadata,
    ExcerptingConfig,
)
from engines.excerpting.src.phase1_assembly import run_phase1, validate_phase1
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_normalized_package,
)


class TestValidatePhase1:
    """Tests for validate_phase1 (§4.9)."""

    def _simple_manifest(self, num_units: int = 2):
        """Build a simple manifest for validation testing."""
        pkg = _make_normalized_package(num_units=num_units)
        return pkg.manifest

    def test_v_p1_1_coverage(self) -> None:
        """Every leaf → chunk or skip. Missing = fatal."""
        manifest = self._simple_manifest(2)
        config = ExcerptingConfig()
        # No chunks AND no skipped divisions → division not covered
        with pytest.raises(ValueError, match="EX-V-001"):
            validate_phase1([], manifest, {}, config)

    def test_v_p1_1_with_skip(self) -> None:
        """Skipped divisions satisfy V-P1-1."""
        manifest = self._simple_manifest(2)
        config = ExcerptingConfig()
        # The leaf div_id is "div_src_test_0_0", mark it as skipped
        skipped = {"div_src_test_0_0": "all_toc"}
        results = validate_phase1([], manifest, skipped, config)
        v1 = next(r for r in results if r["check"] == "V-P1-1")
        assert v1["status"] == "pass"

    def test_v_p1_3_no_empty(self) -> None:
        """word_count > 0 for all chunks. Empty = warning (not fatal)."""
        manifest = self._simple_manifest(2)
        config = ExcerptingConfig()

        # Build a chunk with word_count=0 but matching the manifest's div_id
        chunk = _make_assembled_chunk(
            chunk_id="div_src_test_0_0",
            div_id="div_src_test_0_0",
            assembled_text="",
            word_count=0,
            total_tokens=0,
            text_layers=[],
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=[0, 1],
                join_points=[],
                footnote_renumber_map=None,
            ),
        )
        # V-P1-3 is warning only, but V-P1-5 (layer coverage on empty) should pass
        # and V-P1-6 should pass (0==0).
        # V-P1-1 and V-P1-2 should pass since the chunk covers the division.
        results = validate_phase1([chunk], manifest, {}, config)
        v3 = next(r for r in results if r["check"] == "V-P1-3")
        assert v3["status"] == "warning"

    def test_v_p1_4_no_oversized(self) -> None:
        """word_count ≤ OVERSIZED. Over-limit = warning."""
        manifest = self._simple_manifest(2)
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=5)

        # Default chunk has ~7 words, exceeding threshold of 5
        chunk = _make_assembled_chunk(
            chunk_id="div_src_test_0_0",
            div_id="div_src_test_0_0",
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=[0, 1],
                join_points=[],
                footnote_renumber_map=None,
            ),
        )
        results = validate_phase1([chunk], manifest, {}, config)
        v4 = next(r for r in results if r["check"] == "V-P1-4")
        assert v4["status"] == "warning"

    def test_v_p1_6_word_count(self) -> None:
        """I-AC-1: word_count mismatch = fatal."""
        manifest = self._simple_manifest(2)
        config = ExcerptingConfig()

        # Build chunk with deliberately wrong word_count
        text = "بسم الله الرحمن الرحيم"
        chunk = _make_assembled_chunk(
            assembled_text=text,
            word_count=999,  # Wrong!
            total_tokens=len(text.split()),
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=[0, 1],
                join_points=[],
                footnote_renumber_map=None,
            ),
        )
        with pytest.raises(ValueError, match="EX-V-001"):
            validate_phase1([chunk], manifest, {}, config)


class TestRunPhase1EndToEnd:
    """Integration tests for run_phase1 orchestrator."""

    def test_simple_package(self) -> None:
        """Minimal package: 1 division, 2 units → 1 chunk."""
        pkg = _make_normalized_package(num_units=2)
        config = ExcerptingConfig()
        chunks, results = run_phase1(pkg, config)
        assert len(chunks) == 1
        assert chunks[0].assembled_text  # Non-empty text
        assert chunks[0].word_count > 0
        # All validation checks pass
        assert all(r["status"] in ("pass", "warning") for r in results)

    def test_empty_tree(self) -> None:
        """Empty division tree → EX-A-010, empty chunks."""
        pkg = _make_normalized_package(division_tree=[])
        config = ExcerptingConfig()
        chunks, results = run_phase1(pkg, config)
        assert len(chunks) == 0
