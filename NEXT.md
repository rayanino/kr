# NEXT — Fix Two CLI Adapter Bugs (OAuth + Envelope)

## Current Position

- **Test baseline:** 35 adapter tests + 1991 total project tests, 0 failures (as of commit 3cefa8c8)
- **Smoke test:** PASSED (5/5 packages, 69 excerpts, $0.00, 28min)
- **Overnight run:** FAILED (280 chunks) — two distinct bugs

## Read First

| File | What to look for |
|------|------------------|
| `shared/llm/cli_adapter.py` | Lines 96-113 (`_get_oauth_token`), lines 502-559 (`_invoke_claude`), lines 430-453 (auth error retry) |
| `shared/llm/CLI_ADAPTER_SPEC.md` | §3.2 (Claude backend), §6.3 (OAuth) |
| `shared/llm/tests/test_cli_adapter.py` | `test_claude_envelope_extraction`, `test_claude_envelope_error_raises` |

## What to Do

### Phase 0: Investigate (before writing any code)

**0a. Capture Claude CLI raw output format:**

Run these exact commands and save the FULL raw output:

```bash
# Test 1: with --bare (current approach)
claude -p "Respond with only: {\"test\": true}" --bare --no-session-persistence --output-format json --model opus 2>/dev/null

# Test 2: without --bare
claude -p "Respond with only: {\"test\": true}" --no-session-persistence --output-format json --model opus 2>/dev/null

# Test 3: hex dump to see any hidden chars
claude -p "Respond with only: {\"test\": true}" --bare --no-session-persistence --output-format json --model opus 2>/dev/null | xxd | head -30
```

Record: Is the output a JSON array `[...]` or a JSON object `{...}`? What fields exist?

**0b. Check credentials file:**
```bash
python3 -c "
import json
from pathlib import Path
data = json.loads(Path.home().joinpath('.claude/.credentials.json').read_text())
oauth = data.get('claudeAiOauth', {})
print('accessToken prefix:', (oauth.get('accessToken','') or '')[:25])
print('has refreshToken:', bool(oauth.get('refreshToken')))
print('expiresAt:', oauth.get('expiresAt'))
"
```

**0c. Generate a long-lived setup-token:**
```bash
claude setup-token
```
This opens a browser for authentication. Complete the flow. It outputs a long-lived token
(format: `sk-ant-oat01-...`). Save this token — it is valid for ~1 year and tied to the
Max subscription ($0 cost).

If `claude setup-token` is not available or fails, note this and fall back to the
`KR_ANTHROPIC_TOKEN` env var approach (see fallback in Phase 2).

**0d. Verify the setup-token works with --bare:**
```bash
ANTHROPIC_API_KEY="<setup-token-from-0c>" claude -p "Say hello" --bare --no-session-persistence --output-format json --model opus
```

If this succeeds with `--bare`, the setup-token is our solution for Bug 1.

### Phase 1: Fix Bug 2 — Envelope Extraction

**Root cause:** The Claude CLI with `--output-format json` can return output in multiple
formats depending on `--bare` and CLI version:
- **Single dict:** `{"type": "result", "subtype": "success", "result": "...model text...", ...}`
- **Array:** `[{"type": "system", ...}, ..., {"type": "result", "result": "...model text...", ...}]`
- **Raw text:** Just the model's text output (not wrapped in an envelope)

The current code at lines 546-557 only handles the single-dict case. If the output is an
array, extraction fails and the entire envelope dict gets passed to Pydantic validation,
which fails with "Field required" errors because the envelope has `type`, `subtype`,
`errors` fields instead of `segments`.

**Fix:** Add a new standalone function `_extract_claude_result()` and call it from
`_invoke_claude()`. Replace the inline extraction block (lines 543-559).

```python
def _extract_claude_result(raw_stdout: str) -> str:
    """Extract model text from Claude CLI JSON output.

    Handles three output formats:
    1. Single dict envelope: {"type": "result", "result": "...model text..."}
    2. Array of messages: [..., {"type": "result", "result": "...model text..."}]
    3. Raw text (not an envelope): returned as-is

    Raises CLIBackendError if the envelope reports is_error=True.
    """
    try:
        parsed = json.loads(raw_stdout)
    except json.JSONDecodeError:
        # Not valid JSON — return as-is for extract_json() to handle
        return raw_stdout

    # Case 1: Array format — find the result element
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict) and item.get("type") == "result":
                if item.get("is_error"):
                    raise CLIBackendError(
                        f"Claude CLI returned error: {item.get('result', 'unknown')}",
                        backend="claude",
                    )
                result_text = item.get("result")
                if result_text is not None:
                    logger.debug("Extracted model text from Claude CLI array envelope")
                    return str(result_text)
        # No result element found — return raw for downstream handling
        logger.warning("Claude CLI array output had no 'result' element")
        return raw_stdout

    # Case 2: Single dict format
    if isinstance(parsed, dict):
        if parsed.get("type") == "result" or "result" in parsed:
            if parsed.get("is_error"):
                raise CLIBackendError(
                    f"Claude CLI returned error: {parsed.get('result', 'unknown')}",
                    backend="claude",
                )
            if "result" in parsed:
                logger.debug("Extracted model text from Claude CLI dict envelope")
                return str(parsed["result"])

    # Case 3: Not an envelope — return as-is
    return raw_stdout
```

Then in `_invoke_claude()`, replace lines 543-559 with:
```python
raw_stdout = result.stdout
logger.debug("Claude raw stdout: %s", raw_stdout[:200])
return _extract_claude_result(raw_stdout)
```

### Phase 2: Fix Bug 1 — OAuth Token Expiry

**Root cause:** `--bare` mode skips OAuth auto-refresh. The token in
`~/.claude/.credentials.json` expires after a few hours. The adapter's "refresh" at
line 440-442 just re-reads the same expired file. During the 15-hour overnight run,
the token expires and every call fails.

**Fix (depends on Phase 0 results):**

**If `claude setup-token` succeeded (preferred):**

1. Add a constant and reader function:
```python
_SETUP_TOKEN_PATH = Path.home() / ".claude" / "kr_setup_token.txt"


def _get_setup_token() -> str | None:
    """Read long-lived setup-token if available."""
    if _SETUP_TOKEN_PATH.exists():
        token = _SETUP_TOKEN_PATH.read_text(encoding="utf-8").strip()
        if token:
            return token
    return None
```

2. Update `_get_oauth_token()` to try setup-token first:
```python
def _get_oauth_token() -> str:
    """Read auth token for Claude CLI (SPEC §6.3).

    Priority:
    1. KR_ANTHROPIC_TOKEN env var (explicit override)
    2. Long-lived setup-token from ~/.claude/kr_setup_token.txt
    3. OAuth access token from ~/.claude/.credentials.json (original)
    """
    # Priority 1: explicit env var override
    env_token = os.environ.get("KR_ANTHROPIC_TOKEN")
    if env_token:
        logger.debug("Using KR_ANTHROPIC_TOKEN from environment")
        return env_token

    # Priority 2: long-lived setup-token
    setup_token = _get_setup_token()
    if setup_token:
        logger.debug("Using long-lived setup-token")
        return setup_token

    # Priority 3: OAuth credentials file (original behavior)
    cred_path = Path.home() / ".claude" / ".credentials.json"
    if not cred_path.exists():
        raise CLIBackendError(
            f"Claude credentials not found at {cred_path}. "
            "Run 'claude' once to authenticate, or set KR_ANTHROPIC_TOKEN.",
            backend="claude",
        )
    data = json.loads(cred_path.read_text(encoding="utf-8"))
    try:
        return data["claudeAiOauth"]["accessToken"]
    except KeyError:
        raise CLIBackendError(
            "OAuth token not found in credentials file. "
            "Expected data['claudeAiOauth']['accessToken'].",
            backend="claude",
        )
```

3. Save the setup-token:
```bash
echo "<the-token-from-phase-0c>" > ~/.claude/kr_setup_token.txt
chmod 600 ~/.claude/kr_setup_token.txt
```

**If `claude setup-token` is NOT available (fallback):**

Just implement the `KR_ANTHROPIC_TOKEN` env var override (Priority 1 above).
The owner will set this env var manually before launching the overnight run.

### Phase 3: Add Tests

Add these tests to `shared/llm/tests/test_cli_adapter.py`:

**For Bug 2 (envelope):**

1. `test_extract_claude_result_array_format` — input is a JSON array containing
   `[{"type":"system",...},{"type":"result","result":"{\"answer\":\"test\"}","is_error":false}]`
   → returns the `result` field text.

2. `test_extract_claude_result_array_error` — input is a JSON array where the result
   element has `"is_error": true` → raises `CLIBackendError`.

3. `test_extract_claude_result_array_no_result` — input is a JSON array with no
   element having `"type": "result"` → returns raw stdout unchanged.

4. `test_extract_claude_result_raw_text` — input is plain text (not JSON) → returns
   unchanged.

5. `test_extract_claude_result_dict_format` — input is a single dict envelope →
   works the same as existing `test_claude_envelope_extraction` (keep existing test).

**For Bug 1 (token priority):**

6. `test_token_priority_env_var` — when `KR_ANTHROPIC_TOKEN` env var is set, it takes
   precedence over setup-token and credentials.json.

7. `test_token_priority_setup_token` — when setup-token file exists but env var is not
   set, setup-token is used.

8. `test_token_priority_credentials_fallback` — when neither env var nor setup-token
   exists, falls back to credentials.json.

**Also:** Update the existing `test_claude_envelope_extraction` to call
`_extract_claude_result` directly (in addition to the end-to-end test via adapter).

### Phase 4: Run Tests and Smoke Test

```bash
# Unit tests
cd /home/claude/kr
python -m pytest shared/llm/tests/test_cli_adapter.py -v --tb=short
# Should be ~43 tests, 0 failures

# Full project tests
python -m pytest --tb=short -q
# Should be ~1991+ tests, 0 failures

# Integration smoke test (all 5 packages, 1 chunk each)
python scripts/run_full_integration.py --output-dir integration_tests/smoke_fix_$(date +%Y%m%d) --max-chunks 1
# All 5 packages must succeed
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep `--bare` | YES | Owner has hooks/MCP configured. Without --bare they load and may interfere. |
| Token source | Setup-token (1yr) → env var → credentials.json | Setup-token is long-lived ($0 Max), never expires during runs. Env var is explicit override. Credentials.json is last resort. |
| Setup-token path | `~/.claude/kr_setup_token.txt` | Separate from credentials.json to avoid conflicts with CC's OAuth management. |
| Envelope extraction | Standalone function | Testable in isolation, handles array + dict + raw text robustly. |
| `_extract_claude_result` location | Module-level function in cli_adapter.py | Same pattern as `extract_json()` — helper function before the class definitions. |

## Do NOT Do

- Do NOT remove `--bare` — the owner has hooks and MCP servers configured globally.
- Do NOT change the excerpting engine, contracts, or phase logic.
- Do NOT switch to `--backend api` or OpenRouter.
- Do NOT modify the Codex or Gemini backend code.
- Do NOT change any files outside `shared/llm/cli_adapter.py` and `shared/llm/tests/test_cli_adapter.py`.
- Do NOT implement anything beyond what is specified here. After completing the fixes and tests, commit, push, and STOP.

## Verification Criteria

1. `python -m pytest shared/llm/tests/test_cli_adapter.py -v` — all tests pass (~43)
2. `python -m pytest --tb=short -q` — full project tests pass (~1991+)
3. Integration smoke test — all 5 packages succeed, $0.00 cost
4. Setup-token works with `--bare` mode (verified in Phase 0d)
5. Commit message: `fix(cli-adapter): robust envelope extraction + setup-token auth`
