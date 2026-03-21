"""Multi-Model Consensus Evaluation — shared infrastructure.

Dispatches the same structured prompt to two LLMs from different providers
via Instructor's from_provider(), compares their typed Pydantic responses
using a caller-supplied agreement function, and returns a ConsensusResult.

This module does NOT import from engines/source/. All engine-specific
logic (name similarity thresholds, death date comparison) comes via
the agreement_fn parameter.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import instructor
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ── Configuration ──

DEFAULT_CONSENSUS_MODELS = [
    {
        "provider_model": "openrouter/cohere/command-a",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "provider_model": "anthropic/claude-opus-4-6",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
]

FALLBACK_MODEL = {
    "provider_model": "openrouter/openai/gpt-5.4",
    "api_key_env": "OPENROUTER_API_KEY",
}

MODEL_TIMEOUT = 60.0
MAX_RETRIES_PER_MODEL = 2  # original + 1 retry with simplified


@dataclass
class ModelResponse:
    """Response from a single model."""

    model_id: str
    provider: str
    parsed: Any  # Typed Pydantic object (or None on failure)
    raw_response: dict  # .model_dump() for serialization
    parse_success: bool
    error: Optional[str] = None
    latency: float = 0.0


@dataclass
class ConsensusResult:
    """Result of a consensus evaluation."""

    agreed: bool
    canonical_result: Any  # Typed Pydantic object when agreed, None when disagreed
    model_responses: list[ModelResponse] = field(default_factory=list)
    agreement_detail: str = ""
    single_model_fallback: bool = False
    needs_human_gate: bool = False
    human_gate_trigger: Optional[str] = None


# ── Client cache (lazy, module-level) ──

_clients: dict[str, Any] = {}


def _get_client(provider_model: str) -> Any:
    """Get or create an async Instructor client for the given model.

    OpenRouter models require JSON mode (tool use not supported via OpenRouter).
    Anthropic models use the default tool mode.
    """
    if provider_model not in _clients:
        if provider_model.startswith("openrouter/"):
            _clients[provider_model] = instructor.from_provider(
                provider_model,
                async_client=True,
                mode=instructor.Mode.JSON,
            )
        else:
            _clients[provider_model] = instructor.from_provider(
                provider_model,
                async_client=True,
            )
    return _clients[provider_model]


# ── Single-model call with retry ──

async def _call_model(
    provider_model: str,
    messages: list[dict[str, str]],
    response_model: type[BaseModel],
    simplified_messages: Optional[list[dict[str, str]]] = None,
) -> ModelResponse:
    """Call a single model with retry logic.

    Attempt 1: original messages.
    Attempt 2: simplified_messages if provided, else original messages again.

    Args:
        provider_model: Provider/model string, e.g. ``"openrouter/cohere/command-a"``.
        messages: Chat messages to send on the first attempt.
        response_model: Pydantic model class for Instructor to parse into.
        simplified_messages: Shorter fallback messages used on retry. Optional.

    Returns:
        ModelResponse with parse_success=True on success, False after all retries.
    """
    client = _get_client(provider_model)
    provider = provider_model.split("/")[0]  # "openrouter" or "anthropic"

    for attempt in range(MAX_RETRIES_PER_MODEL):
        start = time.monotonic()
        msgs = messages if attempt == 0 or simplified_messages is None else simplified_messages
        try:
            result = await asyncio.wait_for(
                client.create(
                    messages=msgs,
                    response_model=response_model,
                    max_tokens=4000,
                    temperature=0,
                ),
                timeout=MODEL_TIMEOUT,
            )
            latency = time.monotonic() - start
            return ModelResponse(
                model_id=provider_model,
                provider=provider,
                parsed=result,
                raw_response=result.model_dump(),
                parse_success=True,
                latency=latency,
            )
        except Exception as e:
            latency = time.monotonic() - start
            logger.warning(
                "Model %s attempt %d failed (%.1fs): %s",
                provider_model,
                attempt + 1,
                latency,
                e,
            )

    # All retries exhausted
    return ModelResponse(
        model_id=provider_model,
        provider=provider,
        parsed=None,
        raw_response={},
        parse_success=False,
        error=f"Failed after {MAX_RETRIES_PER_MODEL} attempts",
        latency=0.0,
    )


# ── Main evaluate function ──

async def evaluate(
    task: str,
    messages: list[dict[str, str]],
    response_model: type[BaseModel],
    models: Optional[list[dict]] = None,
    agreement_fn: Optional[Callable[[BaseModel, BaseModel], bool]] = None,
    simplified_messages: Optional[list[dict[str, str]]] = None,
) -> ConsensusResult:
    """Run the same messages through multiple models and compare results.

    Dispatches both models concurrently via ``asyncio.gather``. Agreement is
    determined by ``agreement_fn`` when provided; otherwise falls back to
    dict equality of the serialised responses.

    Args:
        task: Task identifier — ``"author_identification"`` or ``"work_matching"``.
            Determines failure-handling behaviour and fallback model activation.
        messages: Chat messages sent to each model.
        response_model: Pydantic model class for Instructor to parse into.
        models: List of model configuration dicts. Each dict must have
            ``"provider_model"`` and ``"api_key_env"`` keys.
            Defaults to ``DEFAULT_CONSENSUS_MODELS``.
        agreement_fn: Callable receiving two parsed Pydantic instances and
            returning ``True`` when they agree. Defaults to dict equality.
        simplified_messages: Shorter messages used on retry attempts.

    Returns:
        ConsensusResult with ``agreed``, ``canonical_result``,
        ``model_responses``, and gate/fallback flags.
    """
    model_configs = models or DEFAULT_CONSENSUS_MODELS

    # Dispatch both models concurrently with overall timeout guard.
    # Individual models have MODEL_TIMEOUT each; this caps total wall time
    # (e.g. if both hit timeout simultaneously: 2×60s → capped at 150s).
    try:
        raw_responses = await asyncio.wait_for(
            asyncio.gather(
                _call_model(
                    model_configs[0]["provider_model"],
                    messages,
                    response_model,
                    simplified_messages,
                ),
                _call_model(
                    model_configs[1]["provider_model"],
                    messages,
                    response_model,
                    simplified_messages,
                ),
                return_exceptions=True,
            ),
            timeout=MODEL_TIMEOUT * 2 + 30,  # 150s total
        )
    except asyncio.TimeoutError:
        logger.error("Consensus overall timeout exceeded (%.0fs)", MODEL_TIMEOUT * 2 + 30)
        _log_consensus(task, [], False, "overall_timeout")
        return ConsensusResult(
            agreed=False,
            canonical_result=None,
            model_responses=[],
            agreement_detail="Overall consensus timeout exceeded",
            needs_human_gate=True,
            human_gate_trigger="consensus_disagreement",
        )

    # Normalise gather exceptions into failed ModelResponse objects
    model_responses: list[ModelResponse] = []
    for i, resp in enumerate(raw_responses):
        if isinstance(resp, BaseException):
            model_responses.append(
                ModelResponse(
                    model_id=model_configs[i]["provider_model"],
                    provider=model_configs[i]["provider_model"].split("/")[0],
                    parsed=None,
                    raw_response={},
                    parse_success=False,
                    error=str(resp),
                )
            )
        else:
            model_responses.append(resp)

    successful = [r for r in model_responses if r.parse_success]
    failed = [r for r in model_responses if not r.parse_success]

    # ── Both failed ──
    if len(successful) == 0:
        _log_consensus(task, model_responses, False, "both_models_failed")
        return ConsensusResult(
            agreed=False,
            canonical_result=None,
            model_responses=model_responses,
            agreement_detail="Both models failed after retries",
            needs_human_gate=True,
            human_gate_trigger="consensus_disagreement",
        )

    # ── One failed ──
    if len(successful) == 1:
        surviving = successful[0]
        failed_model = failed[0]

        # For author_identification: attempt fallback swap when Command A (cohere) failed
        if task == "author_identification" and "cohere" in failed_model.model_id:
            logger.info(
                "Attempting fallback swap: %s -> %s",
                failed_model.model_id,
                FALLBACK_MODEL["provider_model"],
            )
            fallback_response = await _call_model(
                FALLBACK_MODEL["provider_model"],
                messages,
                response_model,
                simplified_messages,
            )
            if fallback_response.parse_success:
                # Replace failed response with fallback response
                model_responses = [
                    r if r.parse_success else fallback_response
                    for r in model_responses
                ]
                successful = [r for r in model_responses if r.parse_success]
                # Fall through to "both succeeded" logic below
            else:
                # Fallback also failed
                _log_consensus(task, model_responses, False, "fallback_also_failed")
                return ConsensusResult(
                    agreed=False,
                    canonical_result=surviving.parsed,
                    model_responses=model_responses,
                    agreement_detail=(
                        f"Model {failed_model.model_id} failed, fallback also failed. "
                        "Single-model result as context only."
                    ),
                    needs_human_gate=True,
                    human_gate_trigger="consensus_disagreement",
                )

        if len(successful) == 1:
            # Still only one success (no fallback attempted, or non-author task)
            if task == "author_identification":
                _log_consensus(task, model_responses, False, "single_model_author_id")
                return ConsensusResult(
                    agreed=False,
                    canonical_result=surviving.parsed,
                    model_responses=model_responses,
                    agreement_detail=(
                        f"Model {failed_model.model_id} failed. Single-model result as "
                        "context only (author_identification requires consensus)."
                    ),
                    needs_human_gate=True,
                    human_gate_trigger="consensus_disagreement",
                )
            else:  # work_matching or other tasks
                _log_consensus(task, model_responses, False, "single_model_fallback")
                return ConsensusResult(
                    agreed=False,
                    canonical_result=surviving.parsed,
                    model_responses=model_responses,
                    agreement_detail=(
                        f"Model {failed_model.model_id} failed. "
                        "Surviving model accepted provisionally."
                    ),
                    single_model_fallback=True,
                )

    # ── Both succeeded: compare ──
    resp_a, resp_b = successful[0], successful[1]

    if agreement_fn is not None:
        agreed = agreement_fn(resp_a.parsed, resp_b.parsed)
    else:
        # Default: dict equality of serialised responses
        agreed = resp_a.raw_response == resp_b.raw_response

    if agreed:
        canonical = _select_canonical(resp_a, resp_b)
        detail = "Models agreed"
        _log_consensus(task, model_responses, True, detail)
        return ConsensusResult(
            agreed=True,
            canonical_result=canonical,
            model_responses=model_responses,
            agreement_detail=detail,
        )
    else:
        if task == "author_identification":
            _log_consensus(task, model_responses, False, "disagreement_author_id")
            return ConsensusResult(
                agreed=False,
                canonical_result=None,
                model_responses=model_responses,
                agreement_detail="Models disagreed on author identification",
                needs_human_gate=True,
                human_gate_trigger="consensus_disagreement",
            )
        else:
            _log_consensus(task, model_responses, False, "disagreement_work_matching")
            return ConsensusResult(
                agreed=False,
                canonical_result=None,
                model_responses=model_responses,
                agreement_detail="Models disagreed on work matching",
                needs_human_gate=True,
                human_gate_trigger="work_match_uncertain",
            )


# ── Helpers ──

def _select_canonical(resp_a: ModelResponse, resp_b: ModelResponse) -> Any:
    """Select the canonical result from two successful responses.

    The response with the higher ``author_identification_confidence`` attribute
    wins. On a tie, Model B (index 1, Opus 4.6) is preferred.

    Args:
        resp_a: First successful ModelResponse.
        resp_b: Second successful ModelResponse.

    Returns:
        The parsed Pydantic object from the winning response.
    """
    conf_a = getattr(resp_a.parsed, "author_identification_confidence", 0.0)
    conf_b = getattr(resp_b.parsed, "author_identification_confidence", 0.0)
    if conf_a > conf_b:
        return resp_a.parsed
    return resp_b.parsed  # Tie → Model B (Opus 4.6)


def _log_consensus(
    task: str,
    responses: list[ModelResponse],
    agreed: bool,
    detail: str,
) -> None:
    """Append a consensus log entry to ``library/logs/consensus.jsonl``.

    Only task/models/agreed/latencies are written — no full response content.

    Args:
        task: Task identifier string.
        responses: All ModelResponse objects from this round.
        agreed: Whether models reached agreement.
        detail: Human-readable description of the outcome.
    """
    log_dir = Path("library/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task": task,
        "models": [r.model_id for r in responses],
        "agreed": agreed,
        "agreement_detail": detail,
        "per_model": [
            {
                "model_id": r.model_id,
                "parse_success": r.parse_success,
                "latency": round(r.latency, 2),
                "error": r.error,
            }
            for r in responses
        ],
    }

    try:
        with open(log_dir / "consensus.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        logger.warning("Failed to write consensus log")
