"""Tests using real excerpt data from integration test fixtures (F-3).

Uses the real_excerpts fixture from conftest.py (previously orphaned).
Validates that real-world data shapes are compatible with taxonomy engine logic.
"""

from __future__ import annotations

import re

import pytest

from engines.taxonomy.src.placer import classify_excerpt_type

# Arabic Unicode range (basic Arabic block)
_ARABIC_CHAR_RE = re.compile(r"[\u0600-\u06FF]")

_REQUIRED_FIELDS = ("excerpt_id", "source_id", "primary_text", "excerpt_topic")


def _skip_if_no_excerpts(excerpts: list[dict]) -> None:
    if not excerpts:
        pytest.skip("Integration test excerpts file not available")


class TestRealData:
    def test_all_excerpts_have_required_fields(
        self, real_excerpts: list[dict]
    ) -> None:
        """Every real excerpt must have the 4 required fields."""
        _skip_if_no_excerpts(real_excerpts)
        for exc in real_excerpts:
            for field in _REQUIRED_FIELDS:
                assert field in exc, f"Missing {field} in {exc.get('excerpt_id', '?')}"
                assert exc[field], f"Empty {field} in {exc.get('excerpt_id', '?')}"

    def test_excerpt_topic_is_nonempty_list(
        self, real_excerpts: list[dict]
    ) -> None:
        """excerpt_topic must be a non-empty list in all real excerpts."""
        _skip_if_no_excerpts(real_excerpts)
        for exc in real_excerpts:
            topics = exc.get("excerpt_topic")
            assert isinstance(topics, list), (
                f"excerpt_topic not a list in {exc.get('excerpt_id', '?')}"
            )
            assert len(topics) > 0, (
                f"excerpt_topic empty in {exc.get('excerpt_id', '?')}"
            )

    def test_classify_excerpt_type_no_crash(
        self, real_excerpts: list[dict]
    ) -> None:
        """classify_excerpt_type must not crash on any real data shape."""
        _skip_if_no_excerpts(real_excerpts)
        for exc in real_excerpts:
            result = classify_excerpt_type(exc)
            assert result is not None

    def test_primary_text_contains_arabic(
        self, real_excerpts: list[dict]
    ) -> None:
        """Sanity check: primary_text should contain Arabic characters."""
        _skip_if_no_excerpts(real_excerpts)
        for exc in real_excerpts:
            text = exc.get("primary_text", "")
            assert _ARABIC_CHAR_RE.search(text), (
                f"No Arabic in primary_text of {exc.get('excerpt_id', '?')}"
            )
