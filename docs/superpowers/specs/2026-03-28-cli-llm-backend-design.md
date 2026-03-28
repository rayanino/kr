# CLI-Based LLM Backend for Excerpting Pipeline

**Date:** 2026-03-28
**Status:** Phase 1 — CLI Adapter (replace API calls with subscription CLIs)
**Motivation:** Full integration run costs ~$292 via OpenRouter API. The user has Claude Max 20x, ChatGPT (Codex), and Gemini subscriptions — the same models are available at $0 via CLI tools.

---

## Problem

The excerpting pipeline makes ~4,480 LLM calls across 280 chunks (16 calls/chunk). 99.7% of the cost ($291 of $292) is Claude Opus output tokens via OpenRouter. The user already pays for Opus via Claude Max 20x.

## Solution

Replace the Instructor/OpenRouter client with a **CLI adapter** that routes calls to `claude -p`, `codex exec`, and `gemini -p` based on model name. Pipeline code is unchanged.

## Model Mapping

| Role | Calls | Current | New CLI | Schema support |
|------|-------|---------|---------|----------------|
| Classify (Phase 2a) | anthropic/claude-opus-4.6 | OpenRouter | `claude -p --json-schema` | Native |
| Group (Phase 2b) | anthropic/claude-opus-4.6 | OpenRouter | `claude -p --json-schema` | Native |
| Enrich (Phase 3) | anthropic/claude-opus-4.6 | OpenRouter | `claude -p --json-schema` | Native |
| Verify (Phase 3) | openai/gpt-5.4 | OpenRouter | `codex exec --output-schema` | Native |
| Escalation (Phase 3) | mistralai/mistral-large-2411 | OpenRouter | `gemini -p --output-format json` | Pydantic post-validation |

**Total cost: $0** (was $292). Three-provider diversity preserved (Anthropic/OpenAI/Google).

## Architecture

```
Pipeline code (5 call sites, UNCHANGED)
        │
        ▼
  client.chat.completions.create(model=..., response_model=..., messages=...)
        │
        ▼
┌─────────────────────────────────┐
│  CLIInstructorAdapter           │  ← ONLY NEW CODE
│  .chat.completions.create()     │
│                                 │
│  1. Route by model prefix       │
│  2. Extract JSON schema         │
│  3. Build CLI command           │
│  4. Run subprocess              │
│  5. Parse JSON response         │
│  6. Validate with Pydantic      │
│  7. Retry on validation failure │
│  8. Log request/response        │
└──────────┬──────────┬──────────┘
           │          │          │
     claude -p   codex exec  gemini -p
```

### File: `shared/llm/cli_adapter.py`

Single new file containing:

1. **`CLIInstructorAdapter`** — drop-in replacement for `instructor.Instructor`
   - Has `.chat.completions.create()` method matching Instructor's signature
   - Routes calls based on model string prefix
   - Manages retry logic (same `max_retries` parameter)

2. **`_call_claude()`** — subprocess wrapper for `claude -p`
   - Writes JSON schema to temp file
   - Passes system + user messages
   - `--output-format json --model opus --no-session-persistence`
   - Timeout: `config.TIMEOUT_SECONDS` (default 120s)

3. **`_call_codex()`** — subprocess wrapper for `codex exec`
   - Writes JSON schema to temp file (codex uses `--output-schema <file>`)
   - `--json -m gpt-5.4 -s read-only`
   - Codex `--json` emits JSONL events; extract the final message event containing the model's response
   - Alternatively: use `-o /tmp/codex_out.json` (`--output-last-message`) to capture just the final response

4. **`_call_gemini()`** — subprocess wrapper for `gemini -p`
   - `--output-format json -y` (auto-accept, no tools needed)
   - Post-validates with Pydantic (no native schema enforcement)

5. **`_log_request()` / `_log_response()`** — matching current raw_llm_requests/responses format

### Integration point: `scripts/run_integration_test.py`

Only change: `create_client()` function.

```python
# Before:
def create_client(timeout=120):
    return instructor.from_openai(
        openai.OpenAI(base_url="...", api_key=KEY),
        mode=instructor.Mode.JSON,
    )

# After:
def create_client(timeout=120, backend="cli"):
    if backend == "api":
        return instructor.from_openai(...)  # existing code
    return CLIInstructorAdapter(timeout=timeout)
```

New CLI flag: `--backend cli|api` (default: `cli`).

## Response Models (JSON Schemas)

6 Pydantic models need schema extraction:

1. `ClassificationResult` — segments with scholarly_function enum, word offsets
2. `ExtractionResult` — teaching units with self_containment enum
3. `EnrichmentResult` — 7 enrichment fields per unit (topic, school, scholars, takhrij, terms, refs, context_hint)
4. `VerificationResult` — agree/disagree with confidence and reasoning
5. `EscalationResponse` — author_id + reasoning (inline model)

All use `model.model_json_schema()` for schema extraction. Enum values serialize as strings.

## Error Handling

| Error | Current behavior | CLI adapter behavior |
|-------|---|---|
| Schema validation failure | Instructor retries with feedback | Adapter retries with feedback (same) |
| API timeout | OpenAI client raises | subprocess.TimeoutExpired → same exception type |
| Rate limit | HTTP 429, backoff | CLI exits non-zero → backoff |
| Model unavailable | HTTP error | CLI exits non-zero → fallback or raise |
| Incomplete output | IncompleteOutputException | JSON parse fails → retry |

## Retry Logic

Same as current Instructor pattern:
- `max_retries` parameter (default 2, total 3 attempts)
- On Pydantic validation failure: retry with error context appended to prompt
- On subprocess error: exponential backoff (2^attempt seconds)
- On timeout: log and raise (same as current)

## Logging

Request/response logs maintain identical format:
```json
// raw_llm_requests/enrich_0003.json
{
  "call_id": "enrich_0003",
  "model": "anthropic/claude-opus-4.6",
  "backend": "cli:claude",  // NEW field
  "temperature": 0.0,
  "max_tokens": 32768,
  "messages": [...]
}

// raw_llm_responses/enrich_0003.json
{
  "call_id": "enrich_0003",
  "model": "anthropic/claude-opus-4.6",
  "backend": "cli:claude",  // NEW field
  "content": "...",
  "raw_content": "...",
  "usage": {"prompt_tokens": 0, "completion_tokens": 0}  // unavailable from CLI
}
```

**Note:** CLI tools don't report token usage. The `usage` field will be `null` or estimated. This is acceptable since cost is $0.

## Testing

1. Unit tests for `CLIInstructorAdapter` with mocked subprocess calls
2. Integration test: run `--max-chunks 1` on taysir with `--backend cli` and verify identical output structure
3. Comparison: same chunk with `--backend api` vs `--backend cli` — outputs should be structurally identical (content may vary due to LLM non-determinism)

## Fallback

`--backend api` flag preserves the current OpenRouter path. No code is deleted. If a CLI tool is unavailable (not installed, auth expired), the adapter raises a clear error rather than silently falling back.

## Future: Agent Team Verification (Phase 2)

This adapter is the foundation for a more powerful architecture:

After enrichment of each chunk, spawn a Claude agent team via `claude -p`:
- **Scholar Verifier**: cross-checks quoted_scholars against known databases (full 1M context)
- **School Attribution Auditor**: verifies school assignment against text signals
- **Self-Containment Reviewer**: checks if excerpts actually stand alone
- **Consensus Synthesizer**: aggregates agent verdicts into final decision

This replaces the current 2-model verify with a multi-agent deep review — leveraging Claude's 1M context window to see entire pages, not truncated snippets. Design as separate spec.

## Constraints

- Pipeline code (5 call sites across 4 engine files) must NOT change
- Request/response log format must be backwards-compatible
- Error codes (EX-*) must be emitted identically
- `--backend api` must continue to work as before
- No new dependencies (uses subprocess, json, tempfile from stdlib)
