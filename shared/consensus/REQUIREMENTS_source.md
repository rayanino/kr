# Consensus — Source Engine Requirements

**Component:** `shared/consensus/`
**Consumer:** Source engine (Session 3), Normalization engine (future)
**SPEC authority:** `engines/source/SPEC_CORE.md` §6 (Consensus Integration)

---

## Purpose

The consensus module runs the same structured prompt through two LLMs from different providers, compares their results, and returns whether they agree. The source engine uses it for three decisions during Step 4 (metadata inference):

1. **Author identification** — highest cascade risk. Disagreement → human gate.
2. **Work matching** — lower cascade risk. Single-model fallback accepted provisionally.
3. **Attribution status** — directed safety comparison piggybacking on author identification.

---

## Interface

### Primary function: `evaluate()`

```python
from dataclasses import dataclass, field
from typing import Any, Optional
from pydantic import BaseModel


@dataclass
class ModelResponse:
    """Response from a single model."""
    model_id: str           # e.g. "claude-opus-4-6" or "cohere/command-a"
    provider: str           # e.g. "anthropic" or "openrouter"
    raw_response: dict      # Full parsed JSON from the model
    parse_success: bool     # Whether the response parsed as valid JSON
    error: Optional[str] = None  # Error message if parse_success is False


@dataclass
class ConsensusResult:
    """Result of a consensus evaluation."""
    agreed: bool                           # Whether models agreed per the task-specific rules
    canonical_result: Optional[dict]       # The accepted result (agreed value, or None if disagreed)
    model_responses: list[ModelResponse]   # Per-model results (always 2 for normal operation)
    agreement_detail: str                  # Human-readable explanation of the agreement/disagreement
    single_model_fallback: bool = False    # True when one model failed and the other's result was accepted provisionally
    needs_human_gate: bool = False         # True when disagreement or failure requires human gate
    human_gate_trigger: Optional[str] = None  # HumanGateTrigger enum value if needs_human_gate


async def evaluate(
    task: str,
    prompt: str,
    response_model: type[BaseModel],
    models: Optional[list[dict]] = None,
    agreement_fn: Optional[callable] = None,
) -> ConsensusResult:
    """Run a prompt through multiple models and compare results.

    Parameters
    ----------
    task : str
        Task identifier. One of: "author_identification", "work_matching".
        Determines failure handling behavior (§6 asymmetric rules).
    prompt : str
        The complete prompt to send to each model (same prompt for all models).
    response_model : type[BaseModel]
        Pydantic model for Instructor to parse the response into.
        Must match the inference output schema (§4.A.4).
    models : list[dict], optional
        List of model configurations. Each dict has keys:
        - "model": str (model identifier, e.g. "claude-opus-4-6")
        - "provider": str ("anthropic" or "openrouter")
        Defaults to the configured consensus pair (§8).
    agreement_fn : callable, optional
        Custom agreement function: (response_a, response_b) -> bool.
        If None, uses the task-specific default agreement function.

    Returns
    -------
    ConsensusResult
        Contains agreement status, canonical result, per-model details,
        and human gate trigger if applicable.

    Raises
    ------
    Does NOT raise on model failure. Failures are captured in ModelResponse.error
    and handled per the asymmetric failure rules below.
    """
```

### Configuration

```python
# Default consensus pair (from SPEC §8, validated in Step 2 Phase 3)
DEFAULT_CONSENSUS_MODELS = [
    {
        "model": "cohere/command-a",
        "provider": "openrouter",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "model": "claude-opus-4-6",
        "provider": "anthropic",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
]

# Fallback: if Command A fails after retries, swap it for GPT-5.4
FALLBACK_MODEL = {
    "model": "openai/gpt-5.4",
    "provider": "openrouter",
    "api_key_env": "OPENROUTER_API_KEY",
}
```

---

## Agreement Rules

### Author identification (SPEC §6.1)

Two models agree on author identification when ALL of the following hold:

**Case A — Existing scholar match:** Both models return the same `canonical_id` from the scholar registry in their `author_identification` output.

**Case B — New scholar (neither finds a match):** Both models agree that no existing record matches, AND:
- Normalized name similarity ≥ 0.90 between the two models' `canonical_name_ar` values (using `normalized_name_similarity()` from `shared/scholar_authority/src/name_matching.py` — the token-based approach, NOT SequenceMatcher).
- Death date within ±10 years (comparing `death_date_hijri` values), OR both return null for death date.

**Disagreement triggers** (any of these → `needs_human_gate = True`, `human_gate_trigger = "CONSENSUS_DISAGREEMENT"`):
- One model matches an existing record, the other says "new."
- Both match existing records but different `canonical_id` values.
- Both say "new" but name similarity < 0.90.
- Both say "new" but death dates differ by > 10 years (and neither is null).

**When models agree on a new scholar:** Create a new record using merged metadata. For any disagreeing biographical field (e.g., school affiliations), prefer the model with higher stated `author_identification_confidence`.

**Canonical result selection when agreed:** Use the response from the model with higher `author_identification_confidence`. If tied, use Model B (Opus 4.6, the higher-accuracy model per Step 2).

### Work matching (SPEC §6.2)

Two models agree when both assign the same `work_id` (existing work) or both agree the source is a new work (no match). Agreement/disagreement follows the same logic as author identification but applied to work title and author identity.

### Attribution status — directed comparison (SPEC §6.3)

**This is NOT a symmetric agreement check.** It runs alongside author identification (same LLM calls, no additional cost). The rule is asymmetric and conservative:

```python
def compare_attribution_status(status_a: str, status_b: str) -> tuple[str, bool]:
    """Directed comparison of attribution_status values.
    
    Returns (accepted_status, needs_human_gate).
    
    Rules:
    - Both agree → accept the agreed value, no gate.
    - One says disputed/unknown, other says definitive/traditional
      → use the MORE CONSERVATIVE value (disputed/unknown wins)
      → trigger human gate (CONSENSUS_DISAGREEMENT).
    - One says traditional, other says definitive
      → use traditional (more conservative), NO human gate.
      This is a degree-of-certainty disagreement, not alarming.
    """
    CONSERVATIVE_ORDER = ["unknown", "disputed", "traditional", "definitive"]
    
    if status_a == status_b:
        return status_a, False
    
    idx_a = CONSERVATIVE_ORDER.index(status_a)
    idx_b = CONSERVATIVE_ORDER.index(status_b)
    conservative = status_a if idx_a < idx_b else status_b
    
    # Check if one is disputed/unknown and the other is definitive/traditional
    conservative_set = {"unknown", "disputed"}
    permissive_set = {"definitive", "traditional"}
    if (status_a in conservative_set and status_b in permissive_set) or \
       (status_b in conservative_set and status_a in permissive_set):
        return conservative, True  # Gate: real safety disagreement
    
    # traditional vs definitive: conservative, no gate
    return conservative, False
```

**Critical:** This runs on the SAME per-model results from the author identification consensus call. It does NOT require a third `evaluate()` call. The source engine extracts `attribution_status` from each model's response after the author identification evaluate() returns.

---

## Failure Handling (Asymmetric by Cascade Risk — SPEC §6)

### Per-model retry logic

When a single model call fails (timeout, API error, unparseable response):
1. First retry: same model, fresh request.
2. Second retry: same model, simplified prompt (remove library context to reduce tokens).
3. Both retries failed → model is marked as "failed."

### Task-specific handling after model failure

**Author identification (highest cascade risk):**
- If one model fails after retries → single-model result is NOT accepted.
- `needs_human_gate = True`, `human_gate_trigger = "CONSENSUS_DISAGREEMENT"`.
- `canonical_result` contains the single model's suggestion as context for the human gate, NOT as an accepted result.
- The single model's `attribution_status` is accepted at face value with `needs_review` on `attribution_status` — the human gate review will cover it.

**Work matching (lower cascade risk):**
- If one model fails after retries → the surviving model's result IS accepted provisionally.
- `single_model_fallback = True`.
- `needs_review` flag set on `work_id` in the source metadata.
- `needs_human_gate = False` (provisionally accepted, not blocking).

### Fallback model swap

If Command A (Cohere) fails after all retries for author identification:
1. Swap Command A for GPT-5.4 (OpenAI via OpenRouter).
2. Retry the consensus with GPT-5.4 + Opus 4.6.
3. If GPT-5.4 also fails → human gate with Opus 4.6's single-model result as context.

This fallback does NOT apply to work matching (single-model provisional acceptance is sufficient for lower-cascade-risk tasks).

---

## Cross-Engine Reuse

The normalization engine will need consensus for layer attribution decisions. The `evaluate()` interface is designed for reuse:
- `task` parameter allows different agreement functions per engine.
- `agreement_fn` parameter allows custom comparison logic without modifying the consensus module.
- The normalization engine can define its own agreement functions and pass them to `evaluate()`.

The consensus module does NOT import from `engines/source/`. All source-engine-specific logic (name similarity thresholds, death date comparison) is passed via `agreement_fn` or implemented in the source engine's consensus integration code.

---

## MVP Implementation Notes

- Use Instructor's `from_provider()` for each model (see technology-inventory.md RQ-1).
- Both model calls should be dispatched concurrently (`asyncio.gather()`) to minimize latency.
- Timeout per model call: 60 seconds (inference prompt is ~3500 tokens input).
- Log every consensus call to `library/logs/consensus.jsonl` with: task, models, agreed, per-model parse_success, latency, and the `agreement_detail`.
- Do NOT log full model responses (may contain PII from source text). Log only the structured output fields relevant to the agreement decision.
