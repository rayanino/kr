---
name: consensus-pattern
description: Implementation pattern for D-041 multi-model consensus via LiteLLM + Instructor. Use when implementing any LLM inference call that makes content decisions (genre, author, science scope, etc.). Never use single-LLM calls for content classification.
---

# Multi-Model Consensus Pattern (D-041)

**Rule:** Every content decision (genre classification, author identification, science scope assignment, multi-layer detection) MUST use multi-model consensus. Single-LLM calls are only acceptable for format validation, not content judgment.

## Selected Consensus Pair

Based on Step 2 Phase 3 testing (2026-03-09):

| Model | Provider | Role |
|-------|----------|------|
| **Command A** | Cohere (via OpenRouter) | Model A — fast, 100% parse, strong Arabic |
| **Opus 4.6** | Anthropic (direct API) | Model B — highest accuracy, 100% parse |

**Metrics:** 92.3% "at least one right", 15.4% complementarity, 76.9% both right.

## Implementation Pattern

### Dependencies
```python
# requirements.txt
litellm>=1.40.0
instructor>=1.0.0
pydantic>=2.0
```

### Core Pattern
```python
from __future__ import annotations

from typing import TypeVar

import instructor
import litellm
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# Model configuration
CONSENSUS_MODELS = [
    {
        "model": "cohere/command-a",
        "api_base": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "model": "claude-opus-4-6",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
]


async def consensus_infer(
    prompt: str,
    response_model: type[T],
    system_prompt: str = "",
    max_tokens: int = 4000,
) -> tuple[T, T, bool]:
    """Run inference through both consensus models.

    Returns:
        (response_a, response_b, agreed) where agreed is True if
        the critical fields match between the two responses.
    """
    responses: list[T] = []

    for model_config in CONSENSUS_MODELS:
        client = instructor.from_litellm(litellm.acompletion)
        response = await client.chat.completions.create(
            model=model_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_model=response_model,
            max_tokens=max_tokens,
        )
        responses.append(response)

    response_a, response_b = responses
    agreed = check_agreement(response_a, response_b)

    return response_a, response_b, agreed
```

### Agreement Checking
```python
from engines.source.contracts import Genre, StructuralFormat, AuthorityLevel


def check_agreement(a: BaseModel, b: BaseModel) -> bool:
    """Check field-by-field agreement between two model responses.

    Agreement means: all critical fields match exactly, or are
    within acceptable tolerance for fuzzy fields.
    """
    a_dict = a.model_dump()
    b_dict = b.model_dump()

    # Exact-match fields (must agree perfectly)
    exact_fields = ["genre", "is_multi_layer", "authority_level"]
    for field in exact_fields:
        if a_dict.get(field) != b_dict.get(field):
            return False

    # Set-overlap fields (must share at least one element)
    if set(a_dict.get("science_scope", [])) != set(b_dict.get("science_scope", [])):
        return False

    # Fuzzy fields (name, death date) — checked separately
    # Author names: at least one shared significant token
    # Death dates: must match exactly if both provided

    return True
```

### Human Gate Integration
```python
from shared.human_gate.src.checkpoint import HumanGateCheckpoint


async def infer_with_consensus(
    source_id: str,
    prompt: str,
    response_model: type[T],
) -> T:
    """Full consensus flow with human gate fallback.

    1. Run both models
    2. If they agree → use the agreed result
    3. If they disagree → trigger human gate
    """
    response_a, response_b, agreed = await consensus_infer(
        prompt=prompt,
        response_model=response_model,
    )

    if agreed:
        # Use Model A (Command A) as the canonical response when agreed
        return response_a

    # Disagreement → human gate
    checkpoint = HumanGateCheckpoint(
        source_id=source_id,
        gate_type="consensus_disagreement",
        model_a_response=response_a.model_dump(),
        model_b_response=response_b.model_dump(),
        fields_disagreed=find_disagreements(response_a, response_b),
    )
    # This blocks until the owner resolves
    resolved = await checkpoint.await_resolution()
    return resolved
```

## When to Use

| Scenario | Use Consensus? | Why |
|----------|---------------|-----|
| Genre classification | YES | Content decision, models can disagree |
| Author identification | YES | Critical metadata, error propagates |
| Science scope | YES | Content decision |
| Multi-layer detection | YES | Affects downstream processing |
| JSON format validation | NO | Structural check, not content |
| SHA-256 hash computation | NO | Deterministic, no LLM involved |
| Trust score calculation | NO | Deterministic formula |

## Environment Setup

```bash
# .env file (gitignored)
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENROUTER_API_KEY=sk-or-v1-...
```

## Cost Estimate

Per source: ~3500 input tokens x 2 models = ~7000 tokens. At production pricing: ~$0.10-0.20 per source. For a 1000-source library: ~$100-200 total, one-time.
