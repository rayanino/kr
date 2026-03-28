# NEXT — CLI Adapter Fix (4 Review Findings)

## Current Position

- **Baseline:** 796 tests passing, 2 skipped (766 excerpting + 30 adapter)
- **Commit:** `2a8560b4` (CC implementation) + `9d83bb14` (review checklist)
- **Review verdict:** BLOCKED — 4 findings (1 CRITICAL, 2 HIGH, 1 MEDIUM)
- **Root cause:** All 4 findings are SPEC-code divergences caused by building from the pre-amendment SPEC (commit `1f0ee83c`). The SPEC was amended in commit `550d74a2` after the implementation.

## What Just Happened

The 3-pass architect review + CC concurrent audit found 4 issues. CC's empirical test on the owner's machine confirmed the CRITICAL finding: `claude -p --bare --output-format json` wraps output in a JSON envelope `{"type":"result","result":"...model text...","usage":{...},...}`. The current adapter returns the full envelope as the model's output, causing 100% failure rate on real Claude CLI calls.

## What to Do

Fix all 4 findings. Each fix is surgical (< 15 lines). Then add 4 new tests covering the fixes.

**Read the SPEC amendments first:** `shared/llm/CLI_ADAPTER_SPEC.md` §2.4, §3.1, §3.2, §4.5, §5.1 — these sections were updated after your implementation.

---

### Fix 1 (F-3 — CRITICAL): Claude CLI envelope extraction

**File:** `shared/llm/cli_adapter.py`
**Function:** `_invoke_claude()` (currently line ~530)

**Current code (BROKEN):**
```python
        logger.debug("Claude stdout: %s", result.stdout[:200])
        return result.stdout
```

**Replace with:**
```python
        raw_stdout = result.stdout
        logger.debug("Claude raw stdout: %s", raw_stdout[:200])

        # Extract model text from CLI JSON envelope (SPEC §3.2)
        # The claude CLI with --output-format json wraps the model's
        # response in: {"type":"result","result":"...model text...","usage":{...}}
        try:
            envelope = json.loads(raw_stdout)
            if isinstance(envelope, dict) and "result" in envelope:
                if envelope.get("is_error"):
                    raise CLIBackendError(
                        f"Claude CLI returned error: {envelope.get('result', 'unknown')}",
                        backend="claude",
                    )
                logger.debug("Extracted model text from Claude CLI envelope")
                return str(envelope["result"])
        except json.JSONDecodeError:
            pass  # Not an envelope — return raw stdout

        return raw_stdout
```

**Why:** The Claude CLI wraps model output in a JSON envelope. Without extraction, `extract_json()` parses the envelope (valid JSON) instead of the model's output, then `model_validate()` fails on the envelope schema. The retry loop augments the prompt but the model responds correctly again, the CLI wraps it again, and all retries are wasted on the same structural problem. 100% failure rate.

---

### Fix 2 (F-1 — HIGH): `extract_json()` return type

**File:** `shared/llm/cli_adapter.py`

**Change 1 — Replace the entire `extract_json` function (currently lines ~146-192) with:**

```python
def extract_json(raw_output: str) -> dict | list:
    """Extract and parse JSON from raw CLI output (SPEC §4.5).

    Returns the parsed Python object (dict or list), NOT a string.

    Tries in order:
    1. Direct parse of stripped output.
    2. Find first { and last } (or [ and ]).
    3. Strip markdown code fences and retry.
    4. Raise JSONDecodeError.
    """
    stripped = raw_output.strip()

    # Step 1: direct parse
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Step 2: brace extraction
    for open_char, close_char in [("{", "}"), ("[", "]")]:
        first = stripped.find(open_char)
        last = stripped.rfind(close_char)
        if first != -1 and last > first:
            candidate = stripped[first : last + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

    # Step 3: strip markdown fences
    fence_pattern = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)
    match = fence_pattern.search(stripped)
    if match:
        fenced = match.group(1).strip()
        try:
            return json.loads(fenced)
        except json.JSONDecodeError:
            pass

    # Step 4: give up
    raise json.JSONDecodeError(
        "No valid JSON found in CLI output",
        stripped[:200],
        0,
    )
```

**Change 2 — In the `create()` method, replace (currently lines ~323-324):**
```python
                json_str = extract_json(raw_output)
                json_data = json.loads(json_str)
```
**With:**
```python
                json_data = extract_json(raw_output)
```

**Change 3 — Update the two test functions that call `extract_json` directly:**

Replace `test_json_extraction_strips_markdown`:
```python
def test_json_extraction_strips_markdown() -> None:
    """Raw output wrapped in markdown fences extracted correctly."""
    raw = '```json\n{"answer": "test", "confidence": 0.9}\n```'
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert result["answer"] == "test"
```

Replace `test_json_extraction_finds_object`:
```python
def test_json_extraction_finds_object() -> None:
    """Raw output with surrounding text extracts JSON object."""
    raw = 'Here is the result: {"answer": "test", "confidence": 0.5} done.'
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert result["confidence"] == 0.5
```

---

### Fix 3 (F-2 — HIGH): `_resolve_backend()` WARNING on unknown prefix

**File:** `shared/llm/cli_adapter.py`
**Function:** `_resolve_backend()` (currently lines ~206-211)

**Replace the entire function with:**
```python
def _resolve_backend(model: str, default_backend: str) -> str:
    """Map model string prefix to CLI backend name."""
    for prefix, backend in _PROVIDER_MAP.items():
        if model.startswith(prefix):
            return backend
    # Extract the prefix for the warning message
    prefix = model.split("/")[0] + "/" if "/" in model else model
    logger.warning(
        "Unknown model prefix '%s' for model '%s', "
        "falling back to %s backend",
        prefix,
        model,
        default_backend,
    )
    return default_backend
```

---

### Fix 4 (F-4 — MEDIUM): Empty system message leading `\n\n`

**File:** `shared/llm/cli_adapter.py`
**In the `create()` method (currently lines ~278-285)**

**Replace:**
```python
        # Augment system prompt with schema directive (SPEC §5.1)
        schema_directive = (
            "\n\nOUTPUT FORMAT: You are a JSON API. You MUST output ONLY "
            "valid JSON matching this exact schema. No markdown, no "
            "explanation, no code fences — just the raw JSON object."
            f"\n\nJSON SCHEMA:\n{schema_str}"
        )
        system_with_schema = original_system + schema_directive
```

**With:**
```python
        # Augment system prompt with schema directive (SPEC §5.1)
        schema_directive = (
            "OUTPUT FORMAT: You are a JSON API. You MUST output ONLY "
            "valid JSON matching this exact schema. No markdown, no "
            "explanation, no code fences — just the raw JSON object."
            f"\n\nJSON SCHEMA:\n{schema_str}"
        )
        if original_system:
            system_with_schema = original_system + "\n\n" + schema_directive
        else:
            system_with_schema = schema_directive
```

---

### New Tests (4 tests)

Add these to `shared/llm/tests/test_cli_adapter.py`:

**Test 31: `test_claude_envelope_extraction`**
```python
@patch("shared.llm.cli_adapter.subprocess.run")
def test_claude_envelope_extraction(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, mock_oauth: Any, mock_which: Any,
) -> None:
    """Claude CLI JSON envelope is correctly unwrapped to extract model text."""
    model_json = json.dumps({"answer": "test", "confidence": 0.9})
    envelope = json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": model_json,
        "usage": {"input_tokens": 100, "output_tokens": 50},
        "total_cost_usd": 0.01,
    })
    mock_run.return_value = _make_completed_process(stdout=envelope)
    result = adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )
    assert result.answer == "test"
    assert result.confidence == 0.9
```

**Test 32: `test_claude_envelope_error_raises`**
```python
@patch("shared.llm.cli_adapter.subprocess.run")
def test_claude_envelope_error_raises(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, mock_oauth: Any, mock_which: Any,
) -> None:
    """Claude CLI envelope with is_error=True raises CLIBackendError."""
    envelope = json.dumps({
        "type": "result",
        "subtype": "error",
        "is_error": True,
        "result": "Something went wrong",
    })
    mock_run.return_value = _make_completed_process(stdout=envelope)
    with pytest.raises(CLIBackendError, match="error"):
        adapter.chat.completions.create(
            model="anthropic/claude-opus-4.6",
            response_model=SimpleResponse,
            messages=MESSAGES,
        )
```

**Test 33: `test_unknown_prefix_logs_warning`**
```python
@patch("shared.llm.cli_adapter.subprocess.run")
def test_unknown_prefix_logs_warning(
    mock_run: MagicMock, valid_json: str, mock_oauth: Any, mock_which: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Unknown model prefix logs WARNING with prefix and model name."""
    import logging
    adapter = CLIInstructorAdapter(default_backend="claude")
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    with caplog.at_level(logging.WARNING, logger="kr.shared.llm.cli_adapter"):
        adapter.chat.completions.create(
            model="mistralai/mistral-large",
            response_model=SimpleResponse,
            messages=MESSAGES,
        )
    assert "Unknown model prefix" in caplog.text
    assert "mistralai/" in caplog.text
```

**Test 34: `test_no_system_message_clean_prompt`**
```python
@patch("shared.llm.cli_adapter.subprocess.run")
def test_no_system_message_clean_prompt(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """When messages have no system role, system prompt starts clean (no leading newlines)."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=[{"role": "user", "content": "Just a user message"}],
    )
    cmd = mock_run.call_args[0][0]
    sp_idx = cmd.index("--system-prompt")
    system_prompt = cmd[sp_idx + 1]
    assert system_prompt.startswith("OUTPUT FORMAT:"), (
        f"System prompt should start with 'OUTPUT FORMAT:', got: {system_prompt[:30]!r}"
    )
```

---

## Do NOT Do

- **Do NOT modify any files in `engines/excerpting/`** — not source, not tests, not contracts.
- **Do NOT change the fix logic beyond what is specified above.** These are surgical fixes.
- **Do NOT extract envelope metadata into CLIResponse fields.** That is a separate enhancement for a future session. The fix only extracts `envelope["result"]` and returns it as a string.
- **Do NOT refactor other parts of the adapter.** Only touch the specific lines called out in the 4 fixes.
- **Do NOT implement anything beyond what is specified here. After completing the fixes, run the full test suite, commit and push. Do NOT proceed to the next session.**

## Verification

After applying all 4 fixes and adding the 4 new tests:

```bash
# 1. Existing excerpting tests (must match baseline exactly)
PYTHONPATH=. python -m pytest engines/excerpting/tests/ -q --tb=short
# Expected: 766 passed, 2 skipped

# 2. Adapter tests (30 original + 4 new)
PYTHONPATH=. python -m pytest shared/llm/tests/ -v --tb=short
# Expected: 34 passed

# 3. Combined count
PYTHONPATH=. python -m pytest engines/excerpting/tests/ shared/llm/tests/ -q --tb=short
# Expected: 800 passed, 2 skipped

# 4. Verify extract_json return type
PYTHONPATH=. python -c "
from shared.llm.cli_adapter import extract_json
result = extract_json('{\"a\": 1}')
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
print('extract_json returns dict: OK')
"

# 5. Verify envelope extraction
PYTHONPATH=. python -c "
import json
from unittest.mock import patch, MagicMock
from shared.llm.cli_adapter import CLIInstructorAdapter
from pydantic import BaseModel

class T(BaseModel):
    answer: str

adapter = CLIInstructorAdapter()
model_json = json.dumps({'answer': 'hello'})
envelope = json.dumps({'type':'result','result':model_json,'is_error':False})

with patch('shared.llm.cli_adapter.subprocess.run') as m, \
     patch('shared.llm.cli_adapter._get_oauth_token', return_value='x'), \
     patch('shared.llm.cli_adapter.shutil.which', return_value='/x'):
    m.return_value = MagicMock(stdout=envelope, stderr='', returncode=0)
    r = adapter.chat.completions.create(
        model='anthropic/claude-opus-4.6',
        response_model=T,
        messages=[{'role':'user','content':'test'}],
    )
    assert r.answer == 'hello', f'Got {r.answer}'
    print('Envelope extraction: OK')
"
```

ALL 5 checks must pass. If any fails, fix before committing.

## After This

Architect re-verifies the fixes (targeted re-review, not full 3-pass). Then: first real CLI integration test on 1 package.
