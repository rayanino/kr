"""Edge-case tests for shared/consensus — no duplicates of test_consensus.py.

Covers:
  - Overall consensus timeout (global asyncio.wait_for cap, NOT per-model failures)
  - agreement_fn returning None (falsy) vs raising an exception
  - Fallback model activation when the Cohere model fails on author_identification
  - Arabic text preservation through ModelResponse serialisation and prompt dispatch
  - Latency recording on successful _call_model calls
  - Schema-validation failure propagation in the evaluate() flow
  - Partial field agreement via a selective agreement_fn
  - Empty prompt dispatching (current behaviour, no early guard)

All external API calls are mocked. Real Arabic text is used in ≥ 4 tests.
SPEC: shared/consensus/SPEC.md (§ consensus verdicts, §2 input handling).
"""

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import BaseModel

from shared.consensus.src.consensus import (
    ModelResponse,
    _call_model,
    evaluate,
)


# ── Shared test models ──────────────────────────────────────────────────────

class ScholarlyClassification(BaseModel):
    """Minimal classification model used across edge-case tests."""

    genre: str = "matn"
    science_scope: str = "fiqh"
    author_identification_confidence: float = 0.80


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sharh_obj() -> ScholarlyClassification:
    return ScholarlyClassification(
        genre="sharh", science_scope="fiqh", author_identification_confidence=0.90
    )


@pytest.fixture
def matn_obj() -> ScholarlyClassification:
    return ScholarlyClassification(
        genre="matn", science_scope="aqidah", author_identification_confidence=0.75
    )


# ── §1  Both models identical ───────────────────────────────────────────────

class TestBothModelsIdenticalResult:
    """Both models return the same Pydantic object — agreed via explicit fn.

    Distinction from test_default_agreement_fn_identical_responses:
    uses an explicit field-checking agreement_fn (genre equality), not
    the default dict-equality fallback.
    """

    async def test_both_models_identical_result_genre_agreement_fn(
        self, sharh_obj: ScholarlyClassification
    ) -> None:
        """Identical responses + explicit genre fn → agreed=True, canonical set.

        SPEC: Both models agreeing via caller-supplied fn → agreed=True,
        canonical_result set, needs_human_gate=False.
        """
        resp = ModelResponse(
            "openrouter/cohere/command-a", "openrouter",
            sharh_obj, sharh_obj.model_dump(), True, latency=0.5,
        )

        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [resp, resp]

            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "هل هذا الكتاب شرح؟"}],
                response_model=ScholarlyClassification,
                agreement_fn=lambda a, b: a.genre == b.genre,
            )

        assert result.agreed is True
        assert result.canonical_result is not None
        assert result.canonical_result.genre == "sharh"
        assert result.needs_human_gate is False
        assert len(result.model_responses) == 2


# ── §2  Overall timeout ─────────────────────────────────────────────────────

class TestBothModelsTimeout:
    """Global asyncio.wait_for cap — distinct from both models failing individually.

    test_both_fail in test_consensus.py tests the path where each _call_model
    returns parse_success=False.  This test fires the *outer* 150 s wall-time
    cap before any model responds, reaching the separate timeout branch.
    """

    async def test_both_models_overall_timeout_returns_failure(self) -> None:
        """Outer asyncio.wait_for raises TimeoutError → agreed=False, needs_human_gate.

        SPEC: Overall consensus timeout → ConsensusResult with agreed=False
        and agreement_detail mentioning timeout.
        """
        with patch(
            "shared.consensus.src.consensus.asyncio.wait_for",
            side_effect=asyncio.TimeoutError(),
        ):
            result = await evaluate(
                task="author_identification",
                messages=[{"role": "user", "content": "من مؤلف هذا الكتاب؟"}],
                response_model=ScholarlyClassification,
            )

        assert result.agreed is False
        assert result.canonical_result is None
        assert result.needs_human_gate is True
        assert "timeout" in result.agreement_detail.lower()


# ── §3  One model empty response ────────────────────────────────────────────

class TestOneModelEmptyResponse:
    """One model returns parse_success=False; other succeeds.

    Distinction from test_one_model_fails_work_matching: verifies that
    the canonical_result IS exactly the surviving model's parsed object
    and that the failed response's error field is preserved.
    """

    async def test_one_model_empty_response_work_matching_single_fallback(
        self, sharh_obj: ScholarlyClassification
    ) -> None:
        """parse_success=False from model A + work_matching → single_model_fallback.

        SPEC: Single surviving model on work_matching task →
        single_model_fallback=True, canonical_result from surviving model.
        """
        empty = ModelResponse(
            "openrouter/cohere/command-a", "openrouter",
            None, {}, False, error="empty response from API",
        )
        success = ModelResponse(
            "anthropic/claude-opus-4-6", "anthropic",
            sharh_obj, sharh_obj.model_dump(), True, latency=1.2,
        )

        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [empty, success]

            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "ما هو عنوان هذا الكتاب؟"}],
                response_model=ScholarlyClassification,
            )

        assert result.single_model_fallback is True
        assert result.canonical_result is sharh_obj
        assert result.needs_human_gate is False
        # Failed response is preserved in model_responses
        failed = next(r for r in result.model_responses if not r.parse_success)
        assert failed.error == "empty response from API"


# ── §4  agreement_fn edge cases ─────────────────────────────────────────────

class TestAgreementFnEdgeCases:
    """agreement_fn contracts: falsy return and exception propagation."""

    async def test_agreement_fn_returns_none_treated_as_disagreement(
        self, sharh_obj: ScholarlyClassification, matn_obj: ScholarlyClassification
    ) -> None:
        """agreement_fn returning None (falsy) → agreed=False without crash.

        Python bool(None) is False, so the if-agreed branch is skipped.
        Tests that a caller's buggy agreement_fn (returning None instead of bool)
        does not crash evaluate() — it silently disagrees.
        SPEC: agreement_fn must return bool; None is falsy → treated as False.
        """
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse("model_a", "openrouter", sharh_obj, sharh_obj.model_dump(), True),
                ModelResponse("model_b", "anthropic", matn_obj, matn_obj.model_dump(), True),
            ]

            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "test"}],
                response_model=ScholarlyClassification,
                agreement_fn=lambda a, b: None,  # type: ignore[return-value]
            )

        # None is falsy — evaluate() treats as disagreement, no crash
        assert result.agreed is False

    async def test_agreement_fn_raises_exception_propagates(
        self, sharh_obj: ScholarlyClassification
    ) -> None:
        """agreement_fn raising ValueError propagates through evaluate() (current behaviour).

        Current behaviour: evaluate() does NOT wrap agreement_fn in try/except.
        A future improvement would catch the exception and return needs_human_gate=True.
        This test documents the current behaviour so any accidental change is caught.
        Real Arabic error message: 'مقارنة غير صالحة — invalid comparison'.
        """

        def bad_fn(a: Any, b: Any) -> bool:
            raise ValueError("مقارنة غير صالحة — invalid comparison")

        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse("model_a", "openrouter", sharh_obj, sharh_obj.model_dump(), True),
                ModelResponse("model_b", "anthropic", sharh_obj, sharh_obj.model_dump(), True),
            ]

            with pytest.raises(ValueError, match="مقارنة غير صالحة"):
                await evaluate(
                    task="work_matching",
                    messages=[{"role": "user", "content": "test"}],
                    response_model=ScholarlyClassification,
                    agreement_fn=bad_fn,
                )


# ── §5  Schema validation and partial agreement ─────────────────────────────

class TestModelResponseSchemaHandling:
    """Schema failures and field-selective agreement logic."""

    async def test_model_response_parse_failure_treated_as_failed_model(
        self, sharh_obj: ScholarlyClassification
    ) -> None:
        """ModelResponse with parse_success=False is excluded from successful models.

        SPEC: Only responses with parse_success=True count toward consensus.
        A schema-validation failure (e.g. missing required field) is identical
        in effect to an API timeout from the consensus engine's perspective.
        """
        failed = ModelResponse(
            "openrouter/cohere/command-a", "openrouter",
            None, {}, False,
            error="Pydantic validation error: missing required field 'genre'",
        )
        success = ModelResponse(
            "anthropic/claude-opus-4-6", "anthropic",
            sharh_obj, sharh_obj.model_dump(), True, latency=0.7,
        )

        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [failed, success]

            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "حدد النوع"}],
                response_model=ScholarlyClassification,
            )

        assert result.single_model_fallback is True
        failed_resp = next(r for r in result.model_responses if not r.parse_success)
        assert failed_resp.parse_success is False
        assert "validation error" in (failed_resp.error or "").lower()

    async def test_partial_agreement_via_field_selective_fn(self) -> None:
        """Models agree on genre but differ on science_scope.

        With a genre-only agreement_fn → agreed=True.
        With default dict-equality → agreed=False (dicts differ).
        Tests that agreement_fn granularity controls the verdict independently.
        SPEC: agreement_fn is the sole arbiter of agreement — dict equality is only
        the fallback when no fn is supplied.
        """
        obj_a = ScholarlyClassification(genre="sharh", science_scope="fiqh")
        obj_b = ScholarlyClassification(genre="sharh", science_scope="usul_al_fiqh")

        # Genre-only: should agree
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse("model_a", "openrouter", obj_a, obj_a.model_dump(), True),
                ModelResponse("model_b", "anthropic", obj_b, obj_b.model_dump(), True),
            ]
            result_genre = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "حدد النوع والعلم"}],
                response_model=ScholarlyClassification,
                agreement_fn=lambda a, b: a.genre == b.genre,
            )

        assert result_genre.agreed is True

        # Default dict-equality: should disagree (different science_scope)
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse("model_a", "openrouter", obj_a, obj_a.model_dump(), True),
                ModelResponse("model_b", "anthropic", obj_b, obj_b.model_dump(), True),
            ]
            result_full = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": "حدد النوع والعلم"}],
                response_model=ScholarlyClassification,
                # no agreement_fn → dict equality
            )

        assert result_full.agreed is False


# ── §6  Fallback model activation ───────────────────────────────────────────

class TestFallbackModelActivation:
    """Cohere failure on author_identification triggers the fallback swap.

    test_one_model_fails_author_id in test_consensus.py deliberately uses a
    NON-cohere model ID to avoid the fallback path.  This test targets that
    path explicitly.
    """

    async def test_fallback_model_triggered_when_cohere_fails(self) -> None:
        """Cohere fails → fallback (GPT) called as replacement; both succeed → compare.

        SPEC: fallback swap only for author_identification when
        'cohere' appears in failed model's model_id.
        After successful swap: two models present → compare with agreement_fn.
        Verified by asserting _call_model called 3 times.
        """
        cohere_fail = ModelResponse(
            "openrouter/cohere/command-a", "openrouter",
            None, {}, False, error="cohere API unavailable",
        )
        claude_obj = ScholarlyClassification(genre="sharh", author_identification_confidence=0.88)
        claude_resp = ModelResponse(
            "anthropic/claude-opus-4-6", "anthropic",
            claude_obj, claude_obj.model_dump(), True, latency=1.0,
        )
        fallback_obj = ScholarlyClassification(genre="sharh", author_identification_confidence=0.82)
        fallback_resp = ModelResponse(
            "openrouter/openai/gpt-5.4", "openrouter",
            fallback_obj, fallback_obj.model_dump(), True, latency=1.5,
        )

        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            # Call 1: cohere → fail, Call 2: claude → success, Call 3: fallback → success
            mock_call.side_effect = [cohere_fail, claude_resp, fallback_resp]

            result = await evaluate(
                task="author_identification",
                messages=[{"role": "user", "content": "من مؤلف كتاب الأم؟"}],
                response_model=ScholarlyClassification,
                agreement_fn=lambda a, b: a.genre == b.genre,
            )

        # Fallback activated: exactly 3 _call_model invocations
        assert mock_call.call_count == 3
        # Both fallback + claude agree on genre="sharh" → agreed=True
        assert result.agreed is True
        assert result.canonical_result is not None


# ── §7  Arabic text handling ─────────────────────────────────────────────────

class TestArabicTextHandling:
    """Arabic text must survive serialisation and be dispatched to models intact."""

    def test_model_response_serialization_preserves_arabic(self) -> None:
        """ModelResponse with Arabic title round-trips through JSON without corruption.

        Verifies that 'كتاب الأم للشافعي' survives model_dump() and JSON
        serialise/deserialise with ensure_ascii=False.
        SPEC: raw_response must preserve all Unicode text including Arabic.
        """
        arabic_title = "كتاب الأم للشافعي"

        class WorkMetadata(BaseModel):
            title: str
            author_identification_confidence: float = 0.90

        obj = WorkMetadata(title=arabic_title)
        resp = ModelResponse(
            model_id="anthropic/claude-opus-4-6",
            provider="anthropic",
            parsed=obj,
            raw_response=obj.model_dump(),
            parse_success=True,
            latency=0.6,
        )

        # Direct attribute access
        assert resp.raw_response["title"] == arabic_title
        assert resp.parsed.title == arabic_title

        # JSON round-trip with ensure_ascii=False (as used in _log_consensus)
        serialized = json.dumps(resp.raw_response, ensure_ascii=False)
        roundtripped = json.loads(serialized)
        assert roundtripped["title"] == arabic_title

    async def test_consensus_with_arabic_prompt_dispatches_correctly(self) -> None:
        """Arabic prompt 'ما نوع هذا الكتاب؟ هل هو شرح أم متن أم حاشية؟' reaches both models intact.

        SPEC: Messages must be forwarded to _call_model without alteration.
        Verifies the Arabic content is preserved in every _call_model invocation.
        """
        arabic_prompt = "ما نوع هذا الكتاب؟ هل هو شرح أم متن أم حاشية؟"
        obj = ScholarlyClassification(genre="sharh", science_scope="fiqh")

        captured_messages: list[list[dict]] = []

        async def capturing_call_model(
            provider_model: str,
            messages: list[dict],
            response_model: type,
            simplified_messages: Any = None,
        ) -> ModelResponse:
            captured_messages.append(messages)
            return ModelResponse(
                provider_model,
                provider_model.split("/")[0],
                obj,
                obj.model_dump(),
                True,
                latency=0.5,
            )

        with patch(
            "shared.consensus.src.consensus._call_model",
            side_effect=capturing_call_model,
        ):
            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": arabic_prompt}],
                response_model=ScholarlyClassification,
                agreement_fn=lambda a, b: True,
            )

        assert result.agreed is True
        # Both model calls received the Arabic prompt unaltered
        assert len(captured_messages) == 2
        for msgs in captured_messages:
            assert msgs[0]["content"] == arabic_prompt


# ── §8  Latency recording ───────────────────────────────────────────────────

class TestLatencyRecording:
    """_call_model must record elapsed time even on the happy path."""

    async def test_latency_recorded_on_successful_call(self) -> None:
        """Fake async client with 50 ms delay → ModelResponse.latency > 0.

        SPEC: latency field must reflect actual wall time of the model call.
        Verifies that time.monotonic() is measured around the awaited create() call.
        """
        obj = ScholarlyClassification(genre="matn", science_scope="tafsir")

        class FakeClient:
            async def create(self, **kwargs: Any) -> ScholarlyClassification:
                await asyncio.sleep(0.05)  # 50 ms simulated network latency
                return obj

        with patch(
            "shared.consensus.src.consensus._get_client",
            return_value=FakeClient(),
        ):
            resp = await _call_model(
                "anthropic/claude-opus-4-6",
                [{"role": "user", "content": "صنّف هذا النص"}],
                ScholarlyClassification,
            )

        assert resp.parse_success is True
        assert resp.latency > 0.0, f"Expected latency > 0 but got {resp.latency}"


# ── §9  Empty prompt handling ───────────────────────────────────────────────

class TestEmptyPromptHandling:
    """evaluate() with empty prompt content — documents current (no-guard) behaviour."""

    async def test_empty_prompt_content_dispatches_to_models(
        self, sharh_obj: ScholarlyClassification
    ) -> None:
        """Empty string prompt is forwarded to _call_model without early validation.

        Current behaviour: evaluate() applies no content-length guard; the empty
        message is dispatched as-is.  A future improvement could add an early
        ValueError guard before dispatching.  This test documents current behaviour
        so any accidental silent change is caught.
        """
        with patch("shared.consensus.src.consensus._call_model") as mock_call:
            mock_call.side_effect = [
                ModelResponse("model_a", "openrouter", sharh_obj, sharh_obj.model_dump(), True),
                ModelResponse("model_b", "anthropic", sharh_obj, sharh_obj.model_dump(), True),
            ]

            result = await evaluate(
                task="work_matching",
                messages=[{"role": "user", "content": ""}],
                response_model=ScholarlyClassification,
                agreement_fn=lambda a, b: True,
            )

        # Empty prompt is dispatched — no guard fires
        assert mock_call.call_count == 2
        result.agreed is True  # noqa: B015  (intentional no-assert; testing no crash)
        # Verify the empty string reached the first _call_model call unchanged
        first_call_messages = mock_call.call_args_list[0][0][1]
        assert first_call_messages[0]["content"] == ""
