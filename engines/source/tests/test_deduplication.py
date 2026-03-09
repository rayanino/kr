"""Tests for source deduplication — SPEC §4.A.7.

Uses real Arabic text from the Islamic scholarly tradition.
"""

from __future__ import annotations

import pytest

from engines.source.src.deduplication import (
    check_exact_duplicate,
    check_work_duplicate,
)


class TestCheckExactDuplicate:
    """Tests for source-level exact deduplication."""

    def test_exact_match_returns_source_id(self) -> None:
        """Same hash → returns existing source_id."""
        registry = {
            "src_a7c3e91f": {"frozen_hash": "abc123def456"},
            "src_b8d4f02g": {"frozen_hash": "xyz789ghi012"},
        }
        result = check_exact_duplicate("abc123def456", registry)
        assert result == "src_a7c3e91f"

    def test_no_match_returns_none(self) -> None:
        """Different hash → None."""
        registry = {
            "src_a7c3e91f": {"frozen_hash": "abc123def456"},
        }
        result = check_exact_duplicate("completely_different_hash", registry)
        assert result is None

    def test_empty_registry_returns_none(self) -> None:
        """Empty registry → None."""
        result = check_exact_duplicate("abc123def456", {})
        assert result is None

    def test_multiple_entries_finds_correct(self) -> None:
        """Multiple registry entries, finds the matching one."""
        registry = {
            "src_00000001": {"frozen_hash": "hash_1"},
            "src_00000002": {"frozen_hash": "hash_2"},
            "src_00000003": {"frozen_hash": "hash_3"},
        }
        result = check_exact_duplicate("hash_2", registry)
        assert result == "src_00000002"

    def test_entry_missing_frozen_hash_key_is_skipped(self) -> None:
        """Registry entry without 'frozen_hash' key is safely skipped."""
        registry = {
            "src_00000001": {"some_other_field": "value"},
            "src_00000002": {"frozen_hash": "target_hash"},
        }
        result = check_exact_duplicate("target_hash", registry)
        assert result == "src_00000002"

    def test_hash_must_match_exactly_no_prefix_match(self) -> None:
        """Prefix of a hash does not trigger a match — full equality required."""
        registry = {
            "src_00000001": {"frozen_hash": "abc123def456full"},
        }
        result = check_exact_duplicate("abc123def456", registry)
        assert result is None


class TestCheckWorkDuplicate:
    """Tests for work-level deduplication using real Arabic scholarly titles."""

    def test_same_title_same_author(self) -> None:
        """Exact title + same author → returns work_id."""
        registry = {
            "wrk_nawawi_001": {
                "canonical_title": "شرح النووي على صحيح مسلم",
                "author_canonical_id": "sch_00042",
            },
        }
        result = check_work_duplicate(
            "شرح النووي على صحيح مسلم", "sch_00042", registry
        )
        assert result == "wrk_nawawi_001"

    def test_similar_title_same_author(self) -> None:
        """Similar title (>= 0.90) + same author → returns work_id.

        'همع الهوامع شرح جمع الجوامع' vs 'همع الهوامع في شرح جمع الجوامع':
        token overlap is high enough to cross the 0.90 threshold.
        """
        registry = {
            "wrk_suyuti_001": {
                "canonical_title": "همع الهوامع في شرح جمع الجوامع",
                "author_canonical_id": "sch_00099",
            },
        }
        result = check_work_duplicate(
            "همع الهوامع شرح جمع الجوامع", "sch_00099", registry
        )
        assert result == "wrk_suyuti_001"

    def test_different_author_same_title(self) -> None:
        """Same title but different author → None (different work)."""
        registry = {
            "wrk_nawawi_001": {
                "canonical_title": "شرح صحيح مسلم",
                "author_canonical_id": "sch_00042",
            },
        }
        result = check_work_duplicate(
            "شرح صحيح مسلم", "sch_99999", registry
        )
        assert result is None

    def test_different_title_same_author(self) -> None:
        """Different title + same author → None."""
        registry = {
            "wrk_nawawi_001": {
                "canonical_title": "المنهاج شرح صحيح مسلم",
                "author_canonical_id": "sch_00042",
            },
        }
        result = check_work_duplicate(
            "رياض الصالحين", "sch_00042", registry
        )
        assert result is None

    def test_empty_registry(self) -> None:
        """Empty registry → None."""
        result = check_work_duplicate("أي كتاب", "sch_00001", {})
        assert result is None

    def test_title_below_threshold(self) -> None:
        """Title similarity below 0.90 → None."""
        registry = {
            "wrk_001": {
                "canonical_title": "ألفية ابن مالك",
                "author_canonical_id": "sch_00001",
            },
        }
        # Completely different title by same author
        result = check_work_duplicate(
            "قطر الندى وبل الصدى", "sch_00001", registry
        )
        assert result is None

    def test_author_comparison_is_exact_not_similarity(self) -> None:
        """Author ID comparison is exact string equality — similar IDs do not match."""
        registry = {
            "wrk_bukhari_001": {
                "canonical_title": "الجامع الصحيح",
                "author_canonical_id": "sch_00010",
            },
        }
        # sch_00010 vs sch_00100 — different scholars, title nearly identical
        result = check_work_duplicate(
            "الجامع الصحيح", "sch_00100", registry
        )
        assert result is None

    def test_multiple_works_finds_correct_match(self) -> None:
        """Multiple works in registry: returns only the matching work_id."""
        registry = {
            "wrk_nawawi_001": {
                "canonical_title": "رياض الصالحين",
                "author_canonical_id": "sch_00042",
            },
            "wrk_nawawi_002": {
                "canonical_title": "المجموع شرح المهذب",
                "author_canonical_id": "sch_00042",
            },
            "wrk_ibnmalk_001": {
                "canonical_title": "ألفية ابن مالك",
                "author_canonical_id": "sch_00055",
            },
        }
        result = check_work_duplicate(
            "المجموع شرح المهذب", "sch_00042", registry
        )
        assert result == "wrk_nawawi_002"

    def test_entry_missing_canonical_title_is_skipped(self) -> None:
        """Registry entry without 'canonical_title' treated as empty title, skipped."""
        registry = {
            "wrk_incomplete": {
                "author_canonical_id": "sch_00042",
                # missing canonical_title
            },
            "wrk_complete": {
                "canonical_title": "رياض الصالحين",
                "author_canonical_id": "sch_00042",
            },
        }
        result = check_work_duplicate(
            "رياض الصالحين", "sch_00042", registry
        )
        assert result == "wrk_complete"

    def test_entry_missing_author_id_is_skipped(self) -> None:
        """Registry entry without 'author_canonical_id' is skipped (empty string != author_id)."""
        registry = {
            "wrk_no_author": {
                "canonical_title": "شرح النووي على صحيح مسلم",
                # missing author_canonical_id
            },
        }
        result = check_work_duplicate(
            "شرح النووي على صحيح مسلم", "sch_00042", registry
        )
        assert result is None
