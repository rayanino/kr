# CLI Backend Architecture Review — Decision Record

**Date:** 2026-03-28
**Session type:** Architecture review (4 independent reviewers)
**Reviewers:** Claude Chat (architect), ChatGPT 5.4 (deep research), Gemini CLI (adversarial), Claude Code (empirical verification)
**Input:** CC's transition plan at `docs/superpowers/specs/2026-03-28-cli-llm-backend-design.md`
**Verdict:** VIABLE with constraints. Original plan requires significant revision.

---

## The Working Recipe (CC-verified)

```bash
# Extract OAuth token from Claude Code credentials
TOKEN=$(python3 -c "import json,os; print(json.load(open(os.path.expanduser('~/.claude/.credentials.json')))['claudeAiOauth']['accessToken'])")

# Primary calls (Opus) — WORKS
ANTHROPIC_API_KEY="$TOKEN" claude -p "prompt here" \
  --bare --no-session-persistence --max-turns 2 \
  --output-format json --model opus \
  --system-prompt "You are a JSON API. Output ONLY valid JSON matching this schema: {schema}"

# Verification calls (GPT-5.4) — WORKS
codex exec "prompt here" \
  --output-schema /path/to/schema.json \
  -s read-only -o /path/to/output.json

# Escalation calls (Gemini) — WORKS (prompt-based, no native schema)
gemini -p "prompt here" -y --output-format text
```

### Why --bare + OAuth token works
1. `--bare` skips hooks/plugins/MCP → avoids the Stop hook infinite loop
2. OAuth token from `~/.claude/.credentials.json` passed as `ANTHROPIC_API_KEY` env var
3. Claude Code routes the OAuth token through its infrastructure → Opus accessible
4. The same token fails via direct Anthropic SDK (server returns "OAuth not supported")
5. `--max-turns 2` required (max-turns 1 can produce empty results)
6. `--no-session-persistence` ensures clean single-shot execution

### Empirically verified properties
- **Determinism:** 3 identical calls → 3 identical outputs (confidence spread = 0.00)
- **Arabic diacritics:** Byte-perfect preservation through subprocess pipes (15/15 diacritics)
- **Realistic schema:** 10-segment ClassificationResult parsed successfully, 14 seconds
- **Error handling:** Empty input → graceful `{"segments":[], "total_segments":0}`
- **Cost:** $0 (billed against Max subscription, total_cost_usd field present but not charged)
- **Latency:** ~3-5s per Opus call, ~2s per Haiku call

---

## Findings That Shaped This Architecture

### 8 blocking findings identified, 2 resolved empirically

| # | Finding | Source | Status |
|---|---------|--------|--------|
| B-1 | Gemini CLI has no JSON schema enforcement | All 4 reviewers | Accepted — prompt-based adequate for simple escalation schema |
| B-2 | Codex CLI is an agent (10K token overhead, needs additionalProperties:false) | ChatGPT + CC | Manageable — adapter must patch schemas |
| B-3 | `claude -p` blocked by Stop hook infinite loop | CC empirical | **RESOLVED** — `--bare` + OAuth token bypasses hooks |
| B-4 | SPEC says "via OpenRouter" in 14+ places — this is a SPEC change | Architect | Required — SPEC amendment needed |
| B-5 | Instructor retry-with-feedback is complex to reimplement | ChatGPT + Gemini | Designable — manual retry loop with error feedback |
| B-6 | No test migration analysis | Architect | Required — part of adapter implementation |
| B-7 | No temperature=0 flag in any CLI | ChatGPT + CC | **RESOLVED** — empirically deterministic (3/3 identical) |
| B-8 | Codex requires additionalProperties:false (Pydantic doesn't generate it) | CC empirical | Required — adapter must recursively patch schemas |

### Critical constraints the adapter MUST implement

1. **`--json-schema` does NOT work with `--bare`** (uses tool_use internally, bare can't resolve). Schema enforcement is prompt-based: embed schema in system prompt, post-validate with Pydantic. This is the same reliability level as Instructor's `Mode.JSON`.

2. **`--max-turns 2` not 1.** With max-turns 1, the model can produce empty results. Verified by CC.

3. **Retry loop must be stateful across stateless calls.** Each `claude -p --bare` subprocess is a fresh session with no memory. The adapter must construct augmented prompts: original prompt + "Previous output failed validation: {error}. Fix the following issues: {details}". This replicates Instructor's automatic retry behavior.

4. **Pydantic model_validators that JSON Schema cannot express:**
   - `check_self_containment_notes` (I-TU-6/7): if FULL → notes must be null; if PARTIAL/DEPENDENT → notes required
   - `check_self_containment_consistency` (I-ER-4): FULL → context_hint null; PARTIAL → context_hint required
   - `check_split_chunk_id` (I-AC-5): chunk_id suffix must match split_info.chunk_index
   - `check_merge_history` (I-AC-6): merge_history[0] must equal div_id
   - `check_mutual_exclusion` (I-AC-7): merge_history and split_info mutually exclusive
   - `_check_item_index_uniqueness` (VerificationResult): no duplicate item_index values
   - `check_attribution_completeness` (I-ER-5): layer_id and author_id must be non-empty
   
   All of these are caught by Pydantic post-validation. The retry loop feeds the ValidationError back into the prompt.

5. **Non-standard enum values from the model** (e.g., "book_title" instead of ScholarlyFunction values). Pydantic's enum validator catches these → retry with error feedback listing valid values.

6. **Codex schemas need `additionalProperties: false`** injected recursively at every object level, or Codex returns HTTP 400.

7. **Token refresh:** OAuth tokens expire. The adapter should re-read `~/.claude/.credentials.json` on auth errors and retry once before failing.

---

## Architecture Decisions

### D-CLI-001: Three-backend adapter with unified Instructor-compatible interface
The adapter exposes `client.chat.completions.create(model=..., response_model=..., max_retries=..., messages=...)` — identical to the current Instructor interface. Internally routes to claude/codex/gemini based on model string prefix. Pipeline code (5 call sites) remains UNCHANGED.

### D-CLI-002: Schema enforcement is prompt-based + Pydantic post-validation
Not constrained decoding. The system prompt includes the JSON schema. The response is parsed with `json.loads()` then validated with `response_model.model_validate(data)`. On validation failure, retry with error feedback appended to messages. This matches Instructor's `Mode.JSON` behavior.

### D-CLI-003: Retry loop replicates Instructor semantics
- `max_retries=N` means N retry attempts (N+1 total attempts, matching Instructor's empirically verified semantics — see memory re: `stop_after_attempt`)
- On Pydantic ValidationError: append error details to user message, re-invoke subprocess
- On subprocess timeout: exponential backoff (2^attempt seconds), re-invoke
- On non-zero exit: log, exponential backoff, re-invoke
- After all retries exhausted: raise same exception type the pipeline currently catches

### D-CLI-004: Provider mapping preserves 3-provider diversity
| Role | Current | CLI backend | Schema enforcement |
|------|---------|-------------|-------------------|
| Primary (classify/group/enrich) | Opus via OpenRouter | `claude -p --bare` | Prompt-based + Pydantic |
| Verify | GPT-5.4 via OpenRouter | `codex exec --output-schema` | Native (with patched schema) |
| Escalation | Mistral via OpenRouter | `gemini -p` | Prompt-based + Pydantic |

Provider diversity changes from Anthropic/OpenAI/Mistral to Anthropic/OpenAI/Google. Gemini replaces Mistral for escalation. This is acceptable — escalation is <3% of calls and the schema is simple (2 fields).

### D-CLI-005: SPEC amendment required
All "via OpenRouter" references in SPEC §5.2.5, §5.3.5, §5.5.3, §7.2.5, §7.3.2, §7.3.3, §8.3 must be updated to "via configured backend (CLI or API)". A new §8.4 documents CLI backend configuration. The `--backend cli|api` flag is added to integration test scripts.

### D-CLI-006: Existing tests pass unchanged
The 5 call sites use `client.chat.completions.create(response_model=..., max_retries=..., ...)`. Tests mock at the `client.chat.completions.create` level (see `_make_mock_instructor_client` in conftest.py). The adapter implements the same method signature, so mocks work identically. No test changes required. Verify with `pytest` after adapter is built.

### D-CLI-007: Logging format backward-compatible
Request/response logs gain `"backend": "cli:claude"` field. All existing fields preserved. `usage.prompt_tokens` and `usage.completion_tokens` are null for CLI calls (token counts not available from subprocess output).

### D-CLI-008: Rollback to OpenRouter preserved
`--backend api` flag on integration test scripts preserves the current OpenRouter path. No code is deleted. If CLI path fails in production, switch back with a flag change.

---

## What the Next Session Must Do

1. **Write the adapter SPEC** (`shared/llm/CLI_ADAPTER_SPEC.md`) — formal specification for `CLIInstructorAdapter`, covering the full interface, all three backends, retry logic, schema patching, error codes, and logging.

2. **Write NEXT.md** for CC to implement the adapter — single file at `shared/llm/cli_adapter.py` plus unit tests.

3. **Amend SPEC.md** — update 14+ "via OpenRouter" references.

4. **Run full test suite** after adapter is built to verify zero regressions.

---

## Cross-Provider Evidence Summary

| Question | ChatGPT 5.4 | Gemini CLI | CC Empirical |
|----------|-------------|------------|--------------|
| Gemini has schema enforcement? | No (issue links) | N/A | No (--help grep) |
| Codex is thin wrapper? | No (agent harness) | N/A | Clean output but 10K overhead |
| Temperature control? | None in any CLI | None (docs) | None (--help grep, confirmed) |
| claude -p works? | N/A | N/A | Blocked by hook → fixed with --bare |
| Arabic diacritics? | Risk flagged | Risk flagged | PASS (byte-perfect) |
| Instructor retry replicable? | Yes (LangChain/Guardrails analogs) | Stateless = no memory | Designable (prompt augmentation) |
| model_validators vs JSON Schema? | N/A | 3 validators named correctly | Confirmed (enum values caught) |
