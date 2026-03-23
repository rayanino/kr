"""Tests for §4.8 — Heading alignment filter."""

from __future__ import annotations

from engines.excerpting.src.phase1_assembly import check_heading_alignment


class TestHeadingAlignment:
    """Tests for check_heading_alignment (§4.8)."""

    def test_aligned_heading(self) -> None:
        """Heading found in first 200 stripped chars → True."""
        heading = "باب الطهارة"
        text = "باب الطهارة وهي النظافة الشرعية " + "والطهارة " * 50
        assert check_heading_alignment(heading, text) is True

    def test_misaligned_heading(self) -> None:
        """Heading NOT found in assembled text → False + EX-A-006."""
        heading = "باب الصلاة"
        text = "وقال المؤلف رحمه الله في كتابه " + "عن الطهارة " * 50
        assert check_heading_alignment(heading, text) is False

    def test_noise_stripped(self) -> None:
        """Diacritics/tatweel ignored in comparison."""
        # Heading with diacritics
        heading = "بَابُ الطَّهَارَةِ"
        # Text without diacritics
        text = "باب الطهارة وهي النظافة الشرعية " + "والطهارة " * 50
        assert check_heading_alignment(heading, text) is True

    def test_not_gate(self) -> None:
        """Misaligned heading is quality flag only — chunk still processed.

        This test verifies the return value is False (not an exception).
        The calling code in run_phase1 still includes the chunk regardless.
        """
        heading = "باب الصلاة"
        text = "كتاب الطهارة " * 100
        result = check_heading_alignment(heading, text)
        assert result is False  # Flag, not gate

    def test_empty_heading(self) -> None:
        """Empty heading after stripping → vacuously aligned."""
        assert check_heading_alignment("", "some text") is True
        # Heading that's all noise characters
        assert check_heading_alignment("\u0640\u200C", "some text") is True
