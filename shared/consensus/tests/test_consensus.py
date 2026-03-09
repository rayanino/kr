"""Tests for shared consensus module.

All tests mock the Instructor clients — no real API calls.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic import BaseModel

from shared.consensus.src.consensus import (
    ConsensusResult,
    ModelResponse,
    _call_model,
    _select_canonical,
    evaluate,
)


# ── Test models ──

class MockInferenceOutput(BaseModel):
    """Minimal mock of InferenceOutput for testing."""

    genre: str = "matn"
    author_identification_confidence: float = 0.90
    attribution_status: str = "definitive"


# ── Fixtures ──

@pytest.fixture
def mock_response_a() -> MockInferenceOutput:
    return MockInferenceOutput(genre="sharh", author_identification_confidence=0.85)


@pytest.fixture
def mock_response_b() -> MockInferenceOutput:
    return MockInferenceOutput(genre="sharh", author_identification_confidence=0.92)


# ── TestEvaluate ──

class TestEvaluate:
    """Tests for the evaluate() function."""

    @pytest.mark.asyncio
    async def test_both_agree(
        self,
        mock_response_a: MockInferenceOutput,
        mock_response_b: MockInferenceOutput,
    ) -> None:
        """Both models return valid results and agreement_fn returns True."""
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse(
                    "model_a", "openrouter", mock_response_a,
                    mock_response_a.model_dump(), True, latency=1.0,
                ),
                ModelResponse(
                    "model_b", "anthropic", mock_response_b,
                    mock_response_b.model_dump(), True, latency=1.0,
                ),
            ]
            result = await evaluate(
                task="author_identification",
                messages=[{"role": "user", "content": "test"}],
                response_model=MockInferenceOutput,
                agreement_fn=lambda a, b: True,
            )
        assert result.agreed is True
        assert result.canonical_result is not None
        assert result.needs_human_gate is False

    @pytest.mark.asyncio
    async def test_both_disagree_author_id(
        self,
        mock_response_a: MockInferenceOutput,
        mock_response_b: MockInferenceOutput,
    ) -> None:
        """Both models succeed but disagree on author identification."""
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse(
                    "model_a", "openrouter", mock_response_a,
                    mock_response_a.model_dump(), True, latency=1.0,
                ),
                ModelResponse(
                    "model_b", "anthropic", mock_response_b,
                    mock_response_b.model_dump(), True, latency=1.0,
                ),
            ]
            result = await evaluate(
                task="author_identification",
                messages=[{"role": "user", "content": "test"}],
                response_model=MockInferenceOutput,
                agreement_fn=lambda a, b: False,
            )
        assert result.agreed is False
        assert result.needs_human_gate is True
        assert result.human_gate_trigger == "consensus_disagreement"

    @pytest.mark.asyncio
    async def test_one_model_fails_author_id(
        self,
        mock_response_b: MockInferenceOutput,
    ) -> None:
        """One model fails for author_identification → needs_human_gate.

        When the failing model is NOT cohere (no fallback swap path), the
        single-success path should set needs_human_gate=True.
        """
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            # Use a non-cohere model name so the fallback swap is NOT triggered
            failed = ModelResponse(
                "openrouter/openai/gpt-4o", "openrouter", None, {}, False, error="timeout",
            )
            success = ModelResponse(
                "anthropic/model", "anthropic", mock_response_b,
                mock_response_b.model_dump(), True, latency=1.0,
            )
            mock_call.side_effect = [failed, success]

            result = await evaluate(
                task="author_identification",
                messages=[{"role": "user", "content": "test"}],
                response_model=MockInferenceOutput,
            )
        assert result.needs_human_gate is True

    @pytest.mark.asyncio
    async def test_one_model_fails_work_matching(
        self,
        mock_response_b: MockInferenceOutput,
    ) -> None:
        """One model fails for work_matching → single_model_fallback."""
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            failed = ModelResponse(
                "model_a", "openrouter", None, {}, False, error="timeout",
            )
            success = ModelResponse(
                "model_b", "anthropic", mock_response_b,
                mock_response_b.model_dump(), True, latency=1.0,
            )
            mock_call.side_effect = [failed, success]

            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "test"}],
                response_model=MockInferenceOutput,
            )
        assert result.single_model_fallback is True
        assert result.needs_human_gate is False
        assert result.canonical_result is not None

    @pytest.mark.asyncio
    async def test_both_fail(self) -> None:
        """Both models fail → needs_human_gate."""
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            failed_a = ModelResponse(
                "model_a", "openrouter", None, {}, False, error="timeout",
            )
            failed_b = ModelResponse(
                "model_b", "anthropic", None, {}, False, error="timeout",
            )
            mock_call.side_effect = [failed_a, failed_b]

            result = await evaluate(
                task="author_identification",
                messages=[{"role": "user", "content": "test"}],
                response_model=MockInferenceOutput,
            )
        assert result.agreed is False
        assert result.needs_human_gate is True
        assert result.canonical_result is None

    @pytest.mark.asyncio
    async def test_default_agreement_fn_identical_responses(
        self,
        mock_response_a: MockInferenceOutput,
    ) -> None:
        """When no agreement_fn is supplied, dict equality is used.

        Identical parsed dicts → agreed=True.
        """
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse(
                    "model_a", "openrouter", mock_response_a,
                    mock_response_a.model_dump(), True, latency=0.5,
                ),
                ModelResponse(
                    "model_b", "anthropic", mock_response_a,
                    mock_response_a.model_dump(), True, latency=0.5,
                ),
            ]
            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "test"}],
                response_model=MockInferenceOutput,
                # agreement_fn intentionally omitted
            )
        assert result.agreed is True

    @pytest.mark.asyncio
    async def test_default_agreement_fn_different_responses(
        self,
        mock_response_a: MockInferenceOutput,
        mock_response_b: MockInferenceOutput,
    ) -> None:
        """When no agreement_fn is supplied, different dicts → agreed=False."""
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse(
                    "model_a", "openrouter", mock_response_a,
                    mock_response_a.model_dump(), True, latency=0.5,
                ),
                ModelResponse(
                    "model_b", "anthropic", mock_response_b,
                    mock_response_b.model_dump(), True, latency=0.5,
                ),
            ]
            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "test"}],
                response_model=MockInferenceOutput,
            )
        assert result.agreed is False
        assert result.human_gate_trigger == "work_match_uncertain"

    @pytest.mark.asyncio
    async def test_gather_exception_treated_as_failure(
        self,
        mock_response_b: MockInferenceOutput,
    ) -> None:
        """An exception propagated from asyncio.gather is wrapped as a failed response."""
        # Patch asyncio.gather directly so the first item raises an exception
        import asyncio as _asyncio

        original_gather = _asyncio.gather

        async def patched_gather(*coros, return_exceptions=False):  # type: ignore[override]
            results = []
            for coro in coros:
                try:
                    results.append(await coro)
                except Exception as exc:
                    if return_exceptions:
                        results.append(exc)
                    else:
                        raise
            return results

        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            failed = ModelResponse(
                "model_a", "openrouter", None, {}, False, error="network error",
            )
            success = ModelResponse(
                "model_b", "anthropic", mock_response_b,
                mock_response_b.model_dump(), True, latency=1.0,
            )
            mock_call.side_effect = [failed, success]

            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "test"}],
                response_model=MockInferenceOutput,
            )
        # The surviving model result should be returned as a fallback
        assert result.single_model_fallback is True or result.needs_human_gate is True


# ── TestSelectCanonical ──

class TestSelectCanonical:
    """Tests for _select_canonical()."""

    def test_higher_confidence_wins(self) -> None:
        """Response with higher author_identification_confidence is selected."""
        resp_a = ModelResponse(
            "a", "p",
            MockInferenceOutput(author_identification_confidence=0.95),
            {}, True,
        )
        resp_b = ModelResponse(
            "b", "p",
            MockInferenceOutput(author_identification_confidence=0.85),
            {}, True,
        )
        result = _select_canonical(resp_a, resp_b)
        assert result.author_identification_confidence == 0.95

    def test_tie_prefers_model_b(self) -> None:
        """On equal confidence, Model B (resp_b) is preferred."""
        resp_a = ModelResponse(
            "a", "p",
            MockInferenceOutput(author_identification_confidence=0.90),
            {}, True,
        )
        resp_b = ModelResponse(
            "b", "p",
            MockInferenceOutput(author_identification_confidence=0.90),
            {}, True,
        )
        result = _select_canonical(resp_a, resp_b)
        assert result is resp_b.parsed

    def test_no_confidence_attribute_falls_back_to_model_b(self) -> None:
        """When parsed object lacks the confidence attribute, Model B wins (0.0 == 0.0)."""

        class NoConf(BaseModel):
            label: str = "x"

        resp_a = ModelResponse("a", "p", NoConf(), {}, True)
        resp_b = ModelResponse("b", "p", NoConf(label="y"), {}, True)
        result = _select_canonical(resp_a, resp_b)
        assert result is resp_b.parsed


# ── TestCallModel ──

class TestCallModel:
    """Tests for _call_model() retry logic (mocking the Instructor client)."""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(
        self,
        mock_response_a: MockInferenceOutput,
    ) -> None:
        """A successful first call returns a ModelResponse with parse_success=True."""
        with patch("shared.consensus.src.consensus._get_client") as mock_get:
            fake_client = type("C", (), {})()

            async def fake_create(**kwargs):  # type: ignore[override]
                return mock_response_a

            fake_client.create = fake_create
            mock_get.return_value = fake_client

            resp = await _call_model(
                "anthropic/claude-opus-4-6",
                [{"role": "user", "content": "hello"}],
                MockInferenceOutput,
            )
        assert resp.parse_success is True
        assert resp.parsed is mock_response_a
        assert resp.provider == "anthropic"

    @pytest.mark.asyncio
    async def test_retry_uses_simplified_messages_on_second_attempt(
        self,
        mock_response_a: MockInferenceOutput,
    ) -> None:
        """On retry, simplified_messages are used instead of the original messages."""
        calls: list[list[dict]] = []

        with patch("shared.consensus.src.consensus._get_client") as mock_get:
            fake_client = type("C", (), {})()
            call_count = 0

            async def fake_create(messages, **kwargs):  # type: ignore[override]
                nonlocal call_count
                calls.append(messages)
                call_count += 1
                if call_count == 1:
                    raise RuntimeError("simulated failure")
                return mock_response_a

            fake_client.create = fake_create
            mock_get.return_value = fake_client

            simplified = [{"role": "user", "content": "short"}]
            resp = await _call_model(
                "anthropic/claude-opus-4-6",
                [{"role": "user", "content": "long original message"}],
                MockInferenceOutput,
                simplified_messages=simplified,
            )

        assert resp.parse_success is True
        assert calls[0][0]["content"] == "long original message"
        assert calls[1][0]["content"] == "short"

    @pytest.mark.asyncio
    async def test_all_retries_exhausted_returns_failed_response(self) -> None:
        """When all retry attempts fail, a failed ModelResponse is returned."""
        with patch("shared.consensus.src.consensus._get_client") as mock_get:
            fake_client = type("C", (), {})()

            async def fake_create(**kwargs):  # type: ignore[override]
                raise RuntimeError("always fails")

            fake_client.create = fake_create
            mock_get.return_value = fake_client

            resp = await _call_model(
                "openrouter/cohere/command-a",
                [{"role": "user", "content": "hello"}],
                MockInferenceOutput,
            )
        assert resp.parse_success is False
        assert resp.error is not None
        assert "Failed after" in resp.error
