"""Tests for validate_enrichment_passthrough — D-023 pass-through enforcement.

SPEC §5 Layer 1 / D-023: No upstream non-null field may become null or missing
after enrichment. Error code: SRC_INVALID_ENRICHMENT, severity: fatal.

Each test exercises exactly ONE behavioral rule.
Real Arabic text is used in tests 9, 10, 12, and 13.
"""

from __future__ import annotations

import pytest

from shared.validation.src.validation import (
    ValidationError,
    validate_enrichment_passthrough,
)


# ---------------------------------------------------------------------------
# 1. Identical dicts — no changes at all
# ---------------------------------------------------------------------------

def test_identical_dicts_pass() -> None:
    """SPEC §5 D-023: When before == after, no fields were lost → no errors."""
    # Arrange
    before = {"genre": "sharh", "title": "المقدمة", "confidence": 0.9}
    after = {"genre": "sharh", "title": "المقدمة", "confidence": 0.9}

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert errors == []


# ---------------------------------------------------------------------------
# 2. Extra field in after — additions are always OK
# ---------------------------------------------------------------------------

def test_field_added_ok() -> None:
    """SPEC §5 D-023: after may contain new keys not in before → no error."""
    # Arrange
    before = {"genre": "sharh"}
    after = {"genre": "sharh", "death_year": 852, "madhab": "shafii"}

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert errors == []


# ---------------------------------------------------------------------------
# 3. Field value changed — value changes are explicitly allowed
# ---------------------------------------------------------------------------

def test_field_value_changed_ok() -> None:
    """SPEC §5 D-023: Only null/missing matters; value changes are permitted."""
    # Arrange
    before = {"title": "أ"}
    after = {"title": "ب"}

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert errors == []


# ---------------------------------------------------------------------------
# 4. Non-null field deleted → SRC_INVALID_ENRICHMENT
# ---------------------------------------------------------------------------

def test_field_deleted_fails() -> None:
    """SPEC §5 D-023: Deleting a non-null field is a fatal D-023 violation."""
    # Arrange
    before = {"genre": "sharh", "title": "المقدمة"}
    after = {"title": "المقدمة"}  # 'genre' removed

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert len(errors) == 1
    err = errors[0]
    assert isinstance(err, ValidationError)
    assert err.error_code == "SRC_INVALID_ENRICHMENT"
    assert err.severity == "fatal"
    assert err.field == "genre"
    assert err.recovery == "abort"


# ---------------------------------------------------------------------------
# 5. Non-null field explicitly set to None → SRC_INVALID_ENRICHMENT
# ---------------------------------------------------------------------------

def test_field_nulled_fails() -> None:
    """SPEC §5 D-023: Setting a non-null field to None is a D-023 violation."""
    # Arrange
    before = {"genre": "sharh"}
    after = {"genre": None}  # key present but value is None

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert len(errors) == 1
    err = errors[0]
    assert err.error_code == "SRC_INVALID_ENRICHMENT"
    assert err.field == "genre"


# ---------------------------------------------------------------------------
# 6. Null field in before can be deleted in after
# ---------------------------------------------------------------------------

def test_null_field_can_be_deleted() -> None:
    """SPEC §5 D-023: before[k]=None then after lacks k → no error (was already null)."""
    # Arrange
    before = {"title": "المقدمة", "muhaqiq": None}
    after = {"title": "المقدمة"}  # 'muhaqiq' omitted — was None, so allowed

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert errors == []


# ---------------------------------------------------------------------------
# 7. Null field in before stays null in after
# ---------------------------------------------------------------------------

def test_null_field_can_stay_null() -> None:
    """SPEC §5 D-023: before[k]=None, after[k]=None → no error."""
    # Arrange
    before = {"title": "المقدمة", "muhaqiq": None}
    after = {"title": "المقدمة", "muhaqiq": None}

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert errors == []


# ---------------------------------------------------------------------------
# 8. Multiple deletions — all reported as separate errors
# ---------------------------------------------------------------------------

def test_multiple_deletions_all_reported() -> None:
    """SPEC §5 D-023: Each deleted non-null field produces its own error."""
    # Arrange
    before = {"genre": "sharh", "madhab": "shafii", "death_year": 852}
    after = {}  # all three fields dropped

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert len(errors) == 3
    missing_fields = {e.field for e in errors}
    assert missing_fields == {"genre", "madhab", "death_year"}
    for err in errors:
        assert err.error_code == "SRC_INVALID_ENRICHMENT"
        assert err.severity == "fatal"


# ---------------------------------------------------------------------------
# 9. Arabic field preserved — real Quran opener text
# ---------------------------------------------------------------------------

def test_arabic_field_preserved() -> None:
    """SPEC §5 D-023: Preserving Arabic text verbatim satisfies D-023."""
    # Arrange
    arabic_text = "الحمد لله رب العالمين"
    before = {"title": arabic_text, "genre": "sharh"}
    after = {"title": arabic_text, "genre": "sharh"}

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert errors == []


# ---------------------------------------------------------------------------
# 10. Arabic field deleted → error with correct field name
# ---------------------------------------------------------------------------

def test_arabic_field_deleted() -> None:
    """SPEC §5 D-023: Deleting an Arabic-content field raises error naming that field."""
    # Arrange
    bismillah = "بسم الله الرحمن الرحيم"
    before = {"title": bismillah, "genre": "matn"}
    after = {"genre": "matn"}  # 'title' dropped

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert len(errors) == 1
    err = errors[0]
    assert err.error_code == "SRC_INVALID_ENRICHMENT"
    assert err.field == "title"
    # The original Arabic value should appear in the diagnostic message
    assert bismillah in err.message


# ---------------------------------------------------------------------------
# 11. Empty before — any after is valid
# ---------------------------------------------------------------------------

def test_empty_before_always_passes() -> None:
    """SPEC §5 D-023: No upstream fields means nothing can be lost → no errors."""
    # Arrange
    before: dict = {}
    after = {"genre": "sharh", "title": "المقدمة", "death_year": 911}

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert errors == []


# ---------------------------------------------------------------------------
# 12. Mixed changes — added, changed, and one deleted field
# ---------------------------------------------------------------------------

def test_mixed_changes_exactly_one_error() -> None:
    """SPEC §5 D-023: Among multiple changes, only the deleted non-null field errors."""
    # Arrange
    before = {
        "title": "كتاب التوحيد",          # Arabic: will be preserved
        "genre": "sharh",                 # will be deleted → should error
        "confidence": 0.7,                # will be changed → OK
    }
    after = {
        "title": "كتاب التوحيد",          # preserved
        # "genre" is gone → violation
        "confidence": 0.95,               # value changed → allowed
        "madhab": "hanbali",              # new field → allowed
    }

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert
    assert len(errors) == 1
    assert errors[0].field == "genre"
    assert errors[0].error_code == "SRC_INVALID_ENRICHMENT"


# ---------------------------------------------------------------------------
# 13. Nested dict — top-level key present; inner changes are not checked
# ---------------------------------------------------------------------------

def test_nested_dict_not_recursed() -> None:
    """SPEC §5 D-023: Function checks top-level keys only; nested changes are allowed."""
    # Arrange — 'metadata' key is present in both; inner dict contents differ
    before = {
        "title": "شرح ابن عقيل",    # Arabic: Ibn Aqil commentary
        "metadata": {"a": 1, "b": 2},
    }
    after = {
        "title": "شرح ابن عقيل",
        "metadata": {"b": 99, "c": 3},   # inner key 'a' gone, 'c' added
    }

    # Act
    errors = validate_enrichment_passthrough(before, after)

    # Assert — 'metadata' key still present in after, so no D-023 violation
    assert errors == []
