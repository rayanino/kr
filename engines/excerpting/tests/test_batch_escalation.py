"""Tests for batch escalation of author attribution disagreements.

Covers: BatchEscalationItem/Result models, _call_batch_escalation
prompt construction, empty/failure paths, and resolve_attribution
integration with batch results.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from engines.excerpting.contracts import (
    AuthorAttribution,
    BatchEscalationItem,
    BatchEscalationResult,
    ExcerptingConfig,
    VerificationItem,
)
from engines.excerpting.src.phase3_consensus import (
    _call_batch_escalation,
    _resolve_attribution,
)
from engines.excerpting.tests.conftest import _make_excerpt_record


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════

_SOURCE_META: dict[str, str] = {
    "author_name": "ابن قدامة",
    "work_title": "المغني",
    "science": "فقه",
    "source_school": "حنبلي",
}

_DEFAULT_CONFIG = ExcerptingConfig()


def _make_mock_client(
    return_value: Any = None,
    side_effect: Any = None,
) -> MagicMock:
    """Return a MagicMock configured as an instructor client."""
    client = MagicMock()
    create_mock = client.chat.completions.create
    if side_effect is not None:
        create_mock.side_effect = side_effect
    elif return_value is not None:
        create_mock.return_value = return_value
    return client


def _make_disagreements(count: int = 3) -> list[dict[str, object]]:
    """Build a list of disagreement dicts for batch escalation."""
    items: list[dict[str, object]] = []
    for i in range(count):
        items.append({
            "item_index": i,
            "excerpt_id": f"exc_test_{i}",
            "primary_text": f"نص عربي للاختبار رقم {i} " * 10,
            "enrichment_author": f"sch_enrichment_{i}",
            "verifier_author": f"sch_verifier_{i}",
            "verifier_reasoning": f"Reasoning for item {i}",
        })
    return items


# ═══════════════════════════════════════════════════════════════════
# 1. Model validation
# ═══════════════════════════════════════════════════════════════════


class TestBatchEscalationModels:
    """BatchEscalationItem and BatchEscalationResult validation."""

    def test_item_validates_correctly(self) -> None:
        item = BatchEscalationItem(
            item_index=0,
            author_id="sch_ibn_malik",
            reasoning="Text matches matn style",
        )
        assert item.item_index == 0
        assert item.author_id == "sch_ibn_malik"
        assert item.reasoning == "Text matches matn style"

    def test_result_with_unique_indices(self) -> None:
        result = BatchEscalationResult(
            items=[
                BatchEscalationItem(
                    item_index=0, author_id="sch_a", reasoning="r1"
                ),
                BatchEscalationItem(
                    item_index=1, author_id="sch_b", reasoning="r2"
                ),
                BatchEscalationItem(
                    item_index=2, author_id="sch_c", reasoning="r3"
                ),
            ]
        )
        assert len(result.items) == 3

    def test_result_rejects_duplicate_indices(self) -> None:
        with pytest.raises(ValueError, match="Duplicate item_index"):
            BatchEscalationResult(
                items=[
                    BatchEscalationItem(
                        item_index=0, author_id="sch_a", reasoning="r1"
                    ),
                    BatchEscalationItem(
                        item_index=0, author_id="sch_b", reasoning="r2"
                    ),
                ]
            )

    def test_result_empty_items_valid(self) -> None:
        result = BatchEscalationResult(items=[])
        assert len(result.items) == 0


# ═══════════════════════════════════════════════════════════════════
# 2. _call_batch_escalation
# ═══════════════════════════════════════════════════════════════════


class TestCallBatchEscalation:
    """Test _call_batch_escalation function."""

    def test_empty_disagreements_returns_none(self) -> None:
        client = _make_mock_client()
        result = _call_batch_escalation(
            [], client, _DEFAULT_CONFIG, _SOURCE_META
        )
        assert result is None
        client.chat.completions.create.assert_not_called()

    def test_success_returns_batch_result(self) -> None:
        expected = BatchEscalationResult(
            items=[
                BatchEscalationItem(
                    item_index=0, author_id="sch_a", reasoning="r1"
                ),
                BatchEscalationItem(
                    item_index=1, author_id="sch_b", reasoning="r2"
                ),
            ]
        )
        client = _make_mock_client(return_value=expected)
        disagreements = _make_disagreements(count=2)

        result = _call_batch_escalation(
            disagreements, client, _DEFAULT_CONFIG, _SOURCE_META
        )

        assert result is not None
        assert len(result.items) == 2
        assert result.items[0].author_id == "sch_a"
        assert result.items[1].author_id == "sch_b"

    def test_client_failure_returns_none(self) -> None:
        client = _make_mock_client(side_effect=RuntimeError("API down"))
        disagreements = _make_disagreements(count=2)

        result = _call_batch_escalation(
            disagreements, client, _DEFAULT_CONFIG, _SOURCE_META
        )

        assert result is None

    def test_prompt_contains_all_items(self) -> None:
        expected = BatchEscalationResult(items=[])
        client = _make_mock_client(return_value=expected)
        disagreements = _make_disagreements(count=4)

        _call_batch_escalation(
            disagreements, client, _DEFAULT_CONFIG, _SOURCE_META
        )

        call_kwargs = client.chat.completions.create.call_args
        messages = call_kwargs.kwargs.get(
            "messages", call_kwargs[1].get("messages", [])
        )
        prompt_text = messages[0]["content"]

        # All 4 items present
        for i in range(4):
            assert f"ITEM {i}:" in prompt_text
            assert f"sch_enrichment_{i}" in prompt_text
            assert f"sch_verifier_{i}" in prompt_text

    def test_prompt_contains_source_metadata(self) -> None:
        expected = BatchEscalationResult(items=[])
        client = _make_mock_client(return_value=expected)
        disagreements = _make_disagreements(count=1)

        _call_batch_escalation(
            disagreements, client, _DEFAULT_CONFIG, _SOURCE_META
        )

        call_kwargs = client.chat.completions.create.call_args
        messages = call_kwargs.kwargs.get(
            "messages", call_kwargs[1].get("messages", [])
        )
        prompt_text = messages[0]["content"]

        assert "ابن قدامة" in prompt_text
        assert "المغني" in prompt_text

    def test_no_source_metadata_uses_unknown(self) -> None:
        expected = BatchEscalationResult(items=[])
        client = _make_mock_client(return_value=expected)
        disagreements = _make_disagreements(count=1)

        _call_batch_escalation(
            disagreements, client, _DEFAULT_CONFIG, source_metadata=None
        )

        call_kwargs = client.chat.completions.create.call_args
        messages = call_kwargs.kwargs.get(
            "messages", call_kwargs[1].get("messages", [])
        )
        prompt_text = messages[0]["content"]

        assert "Unknown" in prompt_text

    def test_uses_correct_model_and_timeout(self) -> None:
        expected = BatchEscalationResult(items=[])
        client = _make_mock_client(return_value=expected)
        disagreements = _make_disagreements(count=1)

        config = ExcerptingConfig(
            ESCALATION_MODEL="test/model-v1",
            ESCALATION_TIMEOUT=42,
        )

        _call_batch_escalation(
            disagreements, client, config, _SOURCE_META
        )

        call_kwargs = client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "test/model-v1"
        assert call_kwargs.kwargs["timeout"] == 42
        assert call_kwargs.kwargs["max_tokens"] == 2048

    def test_primary_text_truncated_to_500(self) -> None:
        """Long primary_text is truncated at 500 chars in prompt."""
        expected = BatchEscalationResult(items=[])
        client = _make_mock_client(return_value=expected)

        long_text = "ا" * 1000
        disagreements: list[dict[str, object]] = [{
            "item_index": 0,
            "excerpt_id": "exc_long",
            "primary_text": long_text,
            "enrichment_author": "sch_a",
            "verifier_author": "sch_b",
            "verifier_reasoning": "reason",
        }]

        _call_batch_escalation(
            disagreements, client, _DEFAULT_CONFIG, _SOURCE_META
        )

        call_kwargs = client.chat.completions.create.call_args
        messages = call_kwargs.kwargs.get(
            "messages", call_kwargs[1].get("messages", [])
        )
        prompt_text = messages[0]["content"]

        # The full 1000-char text should NOT appear; only 500 chars
        assert long_text not in prompt_text
        assert "ا" * 500 in prompt_text


# ═══════════════════════════════════════════════════════════════════
# 3. Integration: _resolve_attribution with batch results
# ═══════════════════════════════════════════════════════════════════


class TestResolveAttributionBatch:
    """_resolve_attribution uses batch_escalation_result when provided."""

    def _la3_excerpt(self, author_id: str = "sch_enrichment") -> Any:
        """Excerpt with LA-3 rule for attribution testing."""
        return _make_excerpt_record(
            primary_author_layer=AuthorAttribution(
                layer_id="sharh",
                author_id=author_id,
                coverage_pct=0.55,
                rule_applied="LA-3",
            ),
        )

    def test_batch_result_used_instead_of_escalation_call(self) -> None:
        """When batch_escalation_result has the item, no LLM call needed."""
        exc = self._la3_excerpt("sch_enrichment")
        vi = VerificationItem(
            item_index=5,
            agrees=False,
            alternative_value="sch_verifier",
            confidence=0.8,
            reasoning="Different author",
        )
        # Should NOT be called
        mock_client = _make_mock_client(side_effect=RuntimeError("should not call"))
        batch_result = {5: "sch_enrichment"}  # agrees with enrichment

        decision, _updates, _flags, _gates = _resolve_attribution(
            exc, vi, mock_client, _DEFAULT_CONFIG, _SOURCE_META,
            batch_escalation_result=batch_result,
        )

        # Escalation client was NOT called
        mock_client.chat.completions.create.assert_not_called()
        # Majority: enrichment + batch = 2 votes for sch_enrichment
        assert decision.resolution_method == "majority_2_of_3"
        assert decision.final_value == "sch_enrichment"

    def test_batch_result_missing_index_falls_back(self) -> None:
        """When batch result lacks item_index, falls back to per-item call."""
        exc = self._la3_excerpt("sch_enrichment")
        vi = VerificationItem(
            item_index=99,  # Not in batch result
            agrees=False,
            alternative_value="sch_verifier",
            confidence=0.8,
            reasoning="Different author",
        )

        from pydantic import BaseModel, Field

        class _EscResp(BaseModel):
            author_id: str = Field(description="The correct author attribution")
            reasoning: str = Field(description="Brief explanation")

        mock_client = _make_mock_client(
            return_value=_EscResp(author_id="sch_enrichment", reasoning="ok")
        )
        batch_result = {5: "sch_other"}  # Index 5 only

        _decision, _updates, _flags, _gates = _resolve_attribution(
            exc, vi, mock_client, _DEFAULT_CONFIG, _SOURCE_META,
            batch_escalation_result=batch_result,
        )

        # Per-item escalation was called as fallback
        mock_client.chat.completions.create.assert_called_once()

    def test_batch_result_none_uses_per_item(self) -> None:
        """batch_escalation_result=None uses the per-item path."""
        exc = self._la3_excerpt("sch_enrichment")
        vi = VerificationItem(
            item_index=0,
            agrees=False,
            alternative_value="sch_verifier",
            confidence=0.8,
            reasoning="Different author",
        )

        from pydantic import BaseModel, Field

        class _EscResp(BaseModel):
            author_id: str = Field(description="The correct author attribution")
            reasoning: str = Field(description="Brief explanation")

        mock_client = _make_mock_client(
            return_value=_EscResp(author_id="sch_enrichment", reasoning="ok")
        )

        _decision, _updates, _flags, _gates = _resolve_attribution(
            exc, vi, mock_client, _DEFAULT_CONFIG, _SOURCE_META,
            batch_escalation_result=None,
        )

        # Per-item escalation was called
        mock_client.chat.completions.create.assert_called_once()
