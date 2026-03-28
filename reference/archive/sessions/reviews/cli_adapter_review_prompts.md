# CLI Adapter Review — Session Handoff

Everything you need to run the review session. Three prompts, used in order.

---

## PROMPT 1: New Claude Chat Review Session

Paste this as the first message in a new Claude Chat (the same project):

```
This is a KR review session. CC implemented the CLI adapter (`shared/llm/cli_adapter.py`) from the SPEC I wrote last session. Review it using the 3-pass protocol.

**What CC was asked to do:**
- Implement `CLIInstructorAdapter` — drop-in replacement for `instructor.Instructor` routing LLM calls to CLI backends (claude/codex/gemini)
- 30 unit tests in `shared/llm/tests/test_cli_adapter.py`
- Add `--backend cli|api` flag to `scripts/run_integration_test.py` and `scripts/run_full_integration.py`
- Zero changes to `engines/excerpting/` (source or tests)
- Baseline: 766 passed, 2 skipped. Expected after: 796 passed, 2 skipped.

**Governing documents (read IN FULL before reviewing):**
1. `shared/llm/CLI_ADAPTER_SPEC.md` — the SPEC CC built from (14 sections, 7 invariants, 30 test cases — AMENDED after adversarial self-review)
2. `docs/superpowers/specs/2026-03-28-cli-backend-review-decisions.md` — the 4-reviewer decision record
3. `reference/protocols/REVIEW_PROTOCOL.md` — the 3-pass review protocol (9 rules)
4. `reference/archive/sessions/reviews/review_cli_adapter.md` — pre-populated checklist (fill as you go)

**Session start protocol:**
1. Clone/pull repo
2. `git log --oneline -5` — identify CC's commit(s)
3. `git diff HEAD~1 --stat` (or however many commits CC made) — inventory what changed
4. Read the SPEC, decision record, and review protocol
5. `ls /mnt/skills/user/` — use `kr-reviewing-cc-output` + `critical-review`
6. Begin Pass 1

**Critical review targets (from SPEC authoring session):**
- The `create()` method signature must accept ALL kwargs from all 5 call sites: `model`, `response_model`, `messages`, `max_retries`, `temperature`, `max_tokens`
- `CLIResponse` must satisfy the integration test's `on_response` handler attribute accesses: `response.usage.model_dump()`, `response.choices[0].finish_reason`, `response.choices[0].message.content`, `response.model`
- `additionalProperties: false` patching must recurse into `$defs`/`definitions` (Codex rejects unpatch schemas)
- OAuth token must NEVER appear in hook payloads or logs
- `max_retries=N` → N+1 total attempts (not N attempts)
- JSON extraction must handle: raw, markdown-fenced, text-surrounded
- No files in `engines/excerpting/` were touched
- Existing 766 tests still pass with zero changes

**Known risks to probe in Pass 2:**
- Does the retry loop actually augment the prompt with validation error details, or just retry blindly?
- Does `_CLIUsage.model_dump()` return a dict (not raise AttributeError)?
- Does the codex schema patching handle `$defs` references correctly?
- Does JSON extraction handle nested `{` correctly (e.g., JSON with string values containing braces)?
- Is the subprocess `env` constructed correctly (inherits os.environ + adds ANTHROPIC_API_KEY)?
- Does `--backend api` path remain byte-for-byte identical to pre-CC code?
- **[POST-AMENDMENT]** Are hooks fired with correct calling conventions? `completion:kwargs` must use `callback(**kwargs_dict)` (keyword expansion), NOT `callback(kwargs_dict)` (positional). If wrong, the integration test's `on_request(**kwargs)` handler crashes.
- **[POST-AMENDMENT]** Does the adapter handle messages with NO system role? The escalation call has only a user message — the adapter must create a schema-only system prompt.
- **[POST-AMENDMENT]** Does `extract_json()` return parsed `dict|list`, not a string? There must be no outer `json.loads()` call.
- **[POST-AMENDMENT]** Is `json.dump` used (not `json.dumps`) for writing Codex schemas to temp files?
- **[POST-AMENDMENT]** Is `shared/__init__.py` absent? (It must NOT be created — namespace package.)

Start with Pass 1. End the response after Pass 1 findings. I'll say "continue" for Pass 2.
```

---

## PROMPT 2: CC Adversarial Audit (Rule 9 — Mandatory)

After Pass 1, paste this to CC in a separate session. CC reviews the SAME commit independently:

```
You are performing an adversarial code review of the CLI adapter implementation.

Read these files:
1. shared/llm/CLI_ADAPTER_SPEC.md — the specification
2. shared/llm/cli_adapter.py — the implementation
3. shared/llm/tests/test_cli_adapter.py — the tests
4. scripts/run_integration_test.py — the modified integration script
5. scripts/run_full_integration.py — the modified batch script

Then run ALL tests:
PYTHONPATH=. python -m pytest shared/llm/tests/ engines/excerpting/tests/ -v --tb=short 2>&1 | tail -20

Review checklist — answer each with evidence:

1. Does `create()` accept all 6 named kwargs from the SPEC §2.3? List them.
2. Does `CLIResponse.usage` have a `model_dump()` method that returns a dict? Show the code.
3. Does `patch_additional_properties` recurse into `$defs` and `definitions`? Show the code.
4. Does the retry loop augment the prompt with validation error details (field paths, enum values)? Show the augmentation code.
5. Is `max_retries=0` handled as 1 total attempt? Trace the loop.
6. Does JSON extraction handle: (a) raw JSON, (b) markdown fences, (c) text-surrounded JSON? List the steps.
7. Does the OAuth token appear anywhere in hook payloads or log statements? grep for it.
8. Are temp files (codex schema, codex output) cleaned up in a finally block?
9. Does `--backend api` in run_integration_test.py preserve the exact original code path?
10. Run: git diff HEAD~N -- engines/excerpting/ (where N = number of commits). Confirm ZERO changes to engine code.
11. How are hooks fired for `completion:kwargs`? Is it `callback(**kwargs_dict)` or `callback(kwargs_dict)`? Show the code. It MUST be keyword expansion.
12. What happens when `messages` contains no system role message? Show how the adapter constructs the system prompt for Claude backend in this case.
13. Does `extract_json()` return a parsed `dict|list` or a `str`? Show the return type.
14. Is `json.dump` (not `json.dumps`) used for writing Codex schema to temp file? Show the code.
15. Does `shared/__init__.py` exist? It must NOT. Run: ls shared/__init__.py

Then run these adversarial probes:

Probe A — Schema patching depth test:
```python
from shared.llm.cli_adapter import patch_additional_properties
import json

# Deeply nested schema simulating ClassificationResult
schema = {
    "type": "object",
    "properties": {
        "segments": {
            "type": "array",
            "items": {"$ref": "#/$defs/Segment"}
        }
    },
    "$defs": {
        "Segment": {
            "type": "object",
            "properties": {
                "nested": {
                    "type": "object",
                    "properties": {"val": {"type": "string"}}
                }
            }
        }
    }
}
result = patch_additional_properties(schema)
# Verify: additionalProperties:false at root, in Segment, and in nested
print(json.dumps(result, indent=2))
assert result.get("additionalProperties") == False
assert result["$defs"]["Segment"].get("additionalProperties") == False
assert result["$defs"]["Segment"]["properties"]["nested"].get("additionalProperties") == False
print("PASS: all levels patched")
```

Probe B — JSON extraction edge cases:
```python
from shared.llm.cli_adapter import extract_json

# Case 1: Clean JSON
assert extract_json('{"answer": "test", "confidence": 0.9}') is not None

# Case 2: Markdown fences
assert extract_json('```json\n{"answer": "test", "confidence": 0.9}\n```') is not None

# Case 3: Text around JSON
assert extract_json('Here is the result:\n{"answer": "test", "confidence": 0.9}\nDone.') is not None

# Case 4: Nested braces in string values
result = extract_json('{"answer": "x = {y: z}", "confidence": 0.9}')
assert result is not None

print("PASS: all extraction cases")
```

Probe C — Retry count verification:
```python
from unittest.mock import patch, MagicMock
from shared.llm.cli_adapter import CLIInstructorAdapter
from pydantic import BaseModel, Field
import subprocess

class Simple(BaseModel):
    answer: str

adapter = CLIInstructorAdapter()
call_count = 0

def mock_run(*args, **kwargs):
    global call_count
    call_count += 1
    result = MagicMock()
    result.stdout = 'not json'  # Always fail
    result.stderr = ''
    result.returncode = 0
    return result

with patch('subprocess.run', side_effect=mock_run):
    with patch('shutil.which', return_value='/usr/bin/claude'):
        with patch('shared.llm.cli_adapter._get_oauth_token', return_value='fake'):
            try:
                adapter.chat.completions.create(
                    model="anthropic/claude-opus-4.6",
                    response_model=Simple,
                    messages=[{"role": "user", "content": "test"}],
                    max_retries=2,
                )
            except:
                pass

print(f"Calls made: {call_count}")
assert call_count == 3, f"Expected 3 attempts for max_retries=2, got {call_count}"
print("PASS: retry count correct")
```

Probe D — Hook firing convention (most dangerous subtle bug):
```python
from unittest.mock import patch, MagicMock
from shared.llm.cli_adapter import CLIInstructorAdapter
from pydantic import BaseModel

class Simple(BaseModel):
    answer: str

adapter = CLIInstructorAdapter()

# Register a hook that expects **kwargs (like the integration test does)
received_kwargs = {}
def on_request(**kwargs):
    received_kwargs.update(kwargs)

adapter.on("completion:kwargs", on_request)

# Mock a successful call
mock_result = MagicMock()
mock_result.stdout = '{"answer": "test"}'
mock_result.stderr = ''
mock_result.returncode = 0

with patch('subprocess.run', return_value=mock_result):
    with patch('shutil.which', return_value='/usr/bin/claude'):
        with patch('shared.llm.cli_adapter._get_oauth_token', return_value='fake'):
            adapter.chat.completions.create(
                model="anthropic/claude-opus-4.6",
                response_model=Simple,
                messages=[{"role": "user", "content": "test"}],
                max_retries=0,
            )

assert "model" in received_kwargs, f"Hook not called with kwargs expansion. Got: {received_kwargs}"
assert received_kwargs["model"] == "anthropic/claude-opus-4.6"
print("PASS: hook fires with **kwargs expansion")
```

Probe E — No system message handling:
```python
from unittest.mock import patch, MagicMock
from shared.llm.cli_adapter import CLIInstructorAdapter
from pydantic import BaseModel, Field

class EscalationResponse(BaseModel):
    author_id: str
    reasoning: str

adapter = CLIInstructorAdapter()

mock_result = MagicMock()
mock_result.stdout = '{"author_id": "ibn_qudama", "reasoning": "test"}'
mock_result.stderr = ''
mock_result.returncode = 0

captured_cmds = []
def capture_run(*args, **kwargs):
    captured_cmds.append(args[0] if args else kwargs.get('args'))
    return mock_result

with patch('subprocess.run', side_effect=capture_run):
    with patch('shutil.which', return_value='/usr/bin/gemini'):
        # Only user message, no system message (like escalation call)
        adapter.chat.completions.create(
            model="google/gemini-2.5-pro",
            response_model=EscalationResponse,
            messages=[{"role": "user", "content": "Who is the author?"}],
            max_retries=0,
        )

# Verify call didn't crash and schema was still included in prompt
cmd = captured_cmds[0]
prompt_text = ' '.join(str(c) for c in cmd)
assert "JSON SCHEMA" in prompt_text or "json" in prompt_text.lower(), f"Schema missing from prompt: {cmd}"
print("PASS: no system message handled correctly")
```

Report findings. Stop after this task. Do not continue to the next session.
```

---

## PROMPT 3: Continue to Pass 2

After receiving Pass 1 results from the review chat, say:

```
continue
```

(Then after Pass 2, say "continue" again for Pass 3.)

---

## After CC's Adversarial Audit Returns

Paste CC's full output into the review chat with:

```
CC independent audit results (Rule 9). Cross-reference against your Pass 1/2 findings:

[paste CC output here]
```

Do this AFTER Pass 2, BEFORE Pass 3 verdict.
