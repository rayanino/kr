# CLI Adapter SPEC — `CLIInstructorAdapter`

**Status:** APPROVED for implementation
**Governing decision record:** `docs/superpowers/specs/2026-03-28-cli-backend-review-decisions.md`
**Implementation target:** `shared/llm/cli_adapter.py`

---

## §1 Purpose

`CLIInstructorAdapter` is a drop-in replacement for `instructor.Instructor` that routes LLM calls to CLI backends (`claude`, `codex`, `gemini`) instead of the OpenRouter API. The 5 call sites in the excerpting engine and all 768+ existing tests work without modification.

The adapter exists because the owner's existing Max/Pro subscriptions make CLI calls free ($0), whereas OpenRouter charges per-token. The architecture was validated by a 4-reviewer process (D-CLI-001 through D-CLI-008).

---

## §2 Public Interface

### §2.1 Constructor

```python
class CLIInstructorAdapter:
    def __init__(self, default_backend: str = "claude") -> None:
        """
        Args:
            default_backend: The CLI backend to use when model string prefix
                doesn't match any known provider. One of: "claude", "codex", "gemini".
        """
```

The constructor initializes:
- An empty hook registry (`dict[str, list[Callable]]`)
- The `chat.completions` namespace (see §2.2)
- The default backend

### §2.2 Attribute Chain: `adapter.chat.completions.create(...)`

The adapter exposes the same attribute chain as `instructor.Instructor`. This is implemented via two nested namespace objects:

```python
adapter = CLIInstructorAdapter()
adapter.chat                    # → _ChatNamespace instance
adapter.chat.completions        # → _CompletionsNamespace instance
adapter.chat.completions.create # → the callable that dispatches LLM calls
```

Implementation: `_ChatNamespace` holds a `completions` attribute of type `_CompletionsNamespace`. `_CompletionsNamespace` holds a `create` method. Both are plain classes (not mocks, not `MagicMock`). The adapter's `__init__` wires them together.

### §2.3 The `create` Method — Signature

```python
def create(
    self,
    *,
    model: str,
    response_model: type[T],
    messages: list[dict[str, str]],
    max_retries: int = 0,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    **kwargs: Any,
) -> T:
```

**Parameter semantics:**
| Parameter | Type | Used by adapter | Notes |
|-----------|------|----------------|-------|
| `model` | `str` | Yes — routes to backend | Provider prefix determines CLI tool |
| `response_model` | `type[BaseModel]` | Yes — schema extraction + validation | The Pydantic model class |
| `messages` | `list[dict]` | Yes — prompt construction | System + user messages |
| `max_retries` | `int` | Yes — retry loop | N retries = N+1 total attempts (§4) |
| `temperature` | `float` | No — CLI has no temperature flag | Logged but not passed to CLI |
| `max_tokens` | `int` | Partial — codex only (via prompt budget) | Claude/Gemini ignore it |
| `**kwargs` | `Any` | No — silently ignored | Forward-compat with future Instructor args |

**Return type:** An instance of `response_model` (the Pydantic model class passed in), identical to Instructor's behavior.

**Exceptions raised:** On exhausted retries, raises the last `pydantic.ValidationError` (for schema failures) or `CLIBackendError` (for subprocess failures). These are the same exception types the pipeline currently catches.

### §2.4 Hook Registration: `adapter.on(event, callback)`

```python
def on(self, event: str, callback: Callable) -> None:
    """Register a callback for a lifecycle event.

    Supported events (matching Instructor's hook API):
        "completion:kwargs"    — fired before subprocess invocation
        "completion:response"  — fired after successful parse
        "completion:error"     — fired on any error
    """
```

Hooks fire with **different calling conventions per event type** — this matches Instructor's internal behavior (verified from `instructor.core.hooks.Hooks` source):

- `"completion:kwargs"` → `callback(**kwargs_dict)` — the dict is **expanded as keyword arguments**. The integration test's `on_request(**kwargs: Any)` handler depends on this.
- `"completion:response"` → `callback(response)` — single **positional** argument (the `CLIResponse` object).
- `"completion:error"` → `callback(error)` — single **positional** argument (the exception object).

**CRITICAL:** If `completion:kwargs` passes the dict as a positional arg instead of expanding it, the integration test's `on_request` handler crashes with `TypeError`. This is the most likely hook-related implementation bug.

---

## §3 Provider Routing

### §3.1 Model String → Backend Mapping

The `model` string passed to `create()` determines which CLI backend handles the call:

| Model prefix | Backend | CLI tool | Example model strings |
|-------------|---------|----------|----------------------|
| `anthropic/` | claude | `claude` | `anthropic/claude-opus-4.6` |
| `openai/` | codex | `codex` | `openai/gpt-5.4` |
| `google/` | gemini | `gemini` | `google/gemini-2.5-pro` |

If the prefix matches none of the above, use `self.default_backend` and log a WARNING: `"Unknown model prefix '{prefix}' for model '{model}', falling back to {default_backend} backend"`. This prevents silent misconfiguration — especially if the escalation model override (§9.3) is accidentally omitted.

### §3.2 Backend: Claude (`claude -p --bare`)

**Command template:**
```bash
ANTHROPIC_API_KEY="{oauth_token}" claude -p "{user_prompt}" \
    --bare \
    --no-session-persistence \
    --max-turns 2 \
    --output-format json \
    --model opus \
    --system-prompt "{system_prompt_with_schema}"
```

**Flag semantics (empirically verified):**
- `--bare`: Skips hooks/plugins/MCP. Required to avoid Stop hook infinite loop.
- `--no-session-persistence`: Clean single-shot execution, no session state leaks.
- `--max-turns 2`: Required — max-turns 1 can produce empty results.
- `--output-format json`: Requests JSON output from the CLI wrapper. **IMPLEMENTATION NOTE:** The `claude` CLI with `--output-format json` may wrap the model's text response in a JSON envelope (e.g., `{"type": "result", "result": "...model text..."}`). If so, the adapter must extract the model's text from the envelope before passing it to `extract_json()`. CC must test the actual output format of `claude -p --bare --output-format json` and implement extraction accordingly. If the output format turns out to be raw model text (not wrapped), no envelope extraction is needed — `extract_json()` handles it directly.
- `--model opus`: Routes to Claude Opus via the Claude Code infrastructure.

**OAuth token:** Extracted from `~/.claude/.credentials.json` (see §6.3).

**System prompt construction:** The system message from `messages` is augmented with a JSON schema directive. See §5.1.

**User prompt construction:** The user message(s) from `messages` are concatenated with `\n\n` separators.

**Model string mapping:** The adapter strips the `anthropic/` prefix but does NOT pass the full model string to `--model`. Mapping:
- Any model string starting with `anthropic/` → `--model opus`

This is because `claude -p` does not accept OpenRouter-style model strings. If future models need different `--model` values, add entries to a mapping dict.

### §3.3 Backend: Codex (`codex exec`)

**Command template:**
```bash
codex exec "{combined_prompt}" \
    --output-schema {schema_temp_file} \
    -s read-only \
    -o {output_temp_file}
```

**Key differences from Claude/Gemini:**
- Schema is written to a temp file (JSON Schema format), not embedded in prompt.
- Output is written to a temp file, not captured from stdout.
- The schema MUST have `additionalProperties: false` at every object level (§5.3).
- Codex is an agent harness with ~10K token overhead per call. The prompt should be concise.

**Combined prompt construction:** System and user messages are merged into a single prompt string (Codex has no system prompt flag). Format:

```
SYSTEM INSTRUCTIONS:
{system_message}

USER INPUT:
{user_message}
```

**Output reading:** After subprocess completes, read the output temp file. Parse as JSON.

### §3.4 Backend: Gemini (`gemini -p`)

**Command template:**
```bash
gemini -p "{combined_prompt_with_schema}" -y --output-format text
```

**Flag semantics:**
- `-y`: Auto-confirm prompts (non-interactive mode).
- `--output-format text`: Plain text output (no markdown wrapping).

**No native schema enforcement.** Schema is embedded in the prompt (same as Claude §5.1). Gemini is used only for escalation calls — simple 2-field schemas (EscalationResponse: `author_id` + `reasoning`).

**Combined prompt construction:** System and user messages merged (Gemini has no system prompt flag). Same format as Codex §3.3, with schema appended to the system section.

---

## §4 Retry Loop

The retry loop replicates Instructor's automatic retry-with-feedback behavior. This is the core complexity of the adapter.

### §4.1 Semantics

`max_retries=N` means N retry attempts after the initial attempt. Total attempts = N + 1.

This matches Instructor's empirically verified behavior: `max_retries=0` → 1 attempt (no retries), `max_retries=2` → 3 attempts (1 initial + 2 retries). All 5 call sites use `max_retries=2`.

### §4.2 Attempt Loop (Pseudocode)

```
for attempt in range(max_retries + 1):
    try:
        fire_hook("completion:kwargs", kwargs_dict)

        raw_output = invoke_subprocess(backend, prompt, system_prompt)

        json_data = extract_json(raw_output)  # Returns parsed dict/list (see §4.5)

        result = response_model.model_validate(json_data)

        fire_hook("completion:response", build_cli_response(raw_output, model))

        return result

    except json.JSONDecodeError as e:
        error = e
        if attempt < max_retries:
            prompt = augment_prompt_json_error(original_prompt, raw_output, e)
        else:
            fire_hook("completion:error", e)
            raise CLIBackendError(f"JSON parse failed after {max_retries+1} attempts: {e}")

    except pydantic.ValidationError as e:
        error = e
        if attempt < max_retries:
            prompt = augment_prompt_validation_error(original_prompt, raw_output, e)
        else:
            fire_hook("completion:error", e)
            raise e  # Raise the ValidationError directly — pipeline catches this type

    except subprocess.TimeoutExpired as e:
        error = e
        if attempt < max_retries:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            fire_hook("completion:error", e)
            raise CLIBackendError(f"Subprocess timeout after {max_retries+1} attempts")

    except subprocess.CalledProcessError as e:
        error = e
        if attempt < max_retries:
            if is_auth_error(e):
                refresh_oauth_token()  # §6.3 — retry once with fresh token
            time.sleep(2 ** attempt)
        else:
            fire_hook("completion:error", e)
            raise CLIBackendError(f"Subprocess failed (exit {e.returncode}) after {max_retries+1} attempts: {e.stderr}")
```

### §4.3 Prompt Augmentation for Validation Errors

When Pydantic validation fails, the retry prompt includes the error feedback so the model can self-correct. This is how Instructor works internally.

**Augmented user prompt format:**
```
{original_user_message}

PREVIOUS ATTEMPT FAILED VALIDATION. Your previous output was:
{raw_json_output}

The following validation errors occurred:
{formatted_validation_errors}

Fix ALL of the above issues and output valid JSON matching the schema.
```

**Formatting validation errors:** Each `pydantic.ValidationError` error is formatted as:
```
- Field '{loc}': {msg} (type={type})
```

Example:
```
- Field 'segments.0.confidence': Input should be greater than or equal to 0 (type=greater_than_equal)
- Field 'segments.0.scholarly_function': Input should be 'definition', 'rule_statement', ... (type=enum)
```

This format explicitly lists valid enum values when the error is an enum mismatch — critical for catching the "book_title instead of ScholarlyFunction" failure mode identified in the review.

### §4.4 Prompt Augmentation for JSON Parse Errors

**Augmented user prompt format:**
```
{original_user_message}

PREVIOUS ATTEMPT PRODUCED INVALID JSON. Your previous output was:
{raw_output_first_500_chars}

Error: {json_error_message}

Output ONLY valid JSON. No markdown, no explanation, no code fences.
```

### §4.5 JSON Extraction from Raw Output

```python
def extract_json(raw_output: str) -> dict | list:
    """Extract and parse JSON from CLI output. Returns parsed Python object."""
```

CLI tools may produce output with surrounding text (especially Gemini and Codex). The adapter must extract and parse the JSON:

1. Try `json.loads(raw_output.strip())` directly. If it succeeds, return the parsed result.
2. If that fails, find the first `{` and last `}` in the raw output, extract that substring, and try `json.loads()`. If it fails, try the same with `[` and `]`. Return the parsed result on success.
3. If that fails, strip markdown code fences (```` ```json ... ``` ```` or ```` ``` ... ``` ````) and try `json.loads()` on the stripped content. Return on success.
4. If all steps fail, raise `json.JSONDecodeError`.

Note: Step 2's brace-matching is a heuristic — it finds the outermost `{`/`}` pair. This works correctly even when string values contain braces, because `json.loads()` handles the actual parsing. The heuristic only determines the substring boundaries; if the substring isn't valid JSON, the step fails and falls through to step 3.

---

## §5 Schema Handling

### §5.1 Prompt-Based Schema Embedding (Claude, Gemini)

For Claude and Gemini backends, the JSON schema is embedded in the system prompt.

**Message extraction:** The adapter extracts system and user content from `messages`:
```python
system_parts = [m["content"] for m in messages if m["role"] == "system"]
user_parts = [m["content"] for m in messages if m["role"] == "user"]
original_system = "\n\n".join(system_parts)  # May be empty string
original_user = "\n\n".join(user_parts)
```

**System prompt template (when system message exists):**
```
{original_system_message}

OUTPUT FORMAT: You are a JSON API. You MUST output ONLY valid JSON matching this exact schema. No markdown, no explanation, no code fences — just the raw JSON object.

JSON SCHEMA:
{json_schema}
```

**System prompt template (when NO system message exists — e.g., escalation calls):**
```
OUTPUT FORMAT: You are a JSON API. You MUST output ONLY valid JSON matching this exact schema. No markdown, no explanation, no code fences — just the raw JSON object.

JSON SCHEMA:
{json_schema}
```

The adapter MUST handle the no-system-message case because the escalation call site (`phase3_consensus.py` line 468) passes only a user message. For Claude, this means `--system-prompt` contains only the schema directive. For Gemini/Codex, the schema directive is prepended to the combined prompt.

The JSON schema is extracted from the Pydantic `response_model`:
```python
schema = response_model.model_json_schema()
schema_str = json.dumps(schema, indent=2)
```

### §5.2 File-Based Schema (Codex)

For Codex, the schema is written to a temporary file and passed via `--output-schema`:

```python
import tempfile
schema = response_model.model_json_schema()
schema = patch_additional_properties(schema)  # §5.3
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(schema, f, indent=2)
    schema_path = f.name
```

The schema temp file is cleaned up after the call (in a `finally` block).

### §5.3 Codex Schema Patching: `additionalProperties: false`

Codex requires `additionalProperties: false` at every object level in the JSON schema, or it returns HTTP 400. Pydantic v2 does NOT generate this by default.

**Patching algorithm (recursive):**
```python
def patch_additional_properties(schema: dict) -> dict:
    """Recursively add additionalProperties: false to all object schemas."""
    if isinstance(schema, dict):
        if schema.get("type") == "object" or "properties" in schema:
            schema["additionalProperties"] = False
        # Recurse into all dict values
        for key, value in schema.items():
            if isinstance(value, dict):
                patch_additional_properties(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        patch_additional_properties(item)
        # Handle $defs / definitions
        for defs_key in ("$defs", "definitions"):
            if defs_key in schema:
                for def_schema in schema[defs_key].values():
                    patch_additional_properties(def_schema)
    return schema
```

This patching applies to the Codex schema file ONLY. Claude and Gemini use the unpatched Pydantic schema in the prompt.

---

## §6 Error Handling

### §6.1 Exception Types

The adapter defines one new exception:

```python
class CLIBackendError(Exception):
    """Raised when a CLI backend fails in a non-recoverable way.

    Wraps subprocess errors, timeouts, and persistent JSON parse failures.
    Preserves the original exception in __cause__.
    """
    def __init__(self, message: str, backend: str = "", exit_code: int | None = None):
        super().__init__(message)
        self.backend = backend
        self.exit_code = exit_code
```

**Exception routing for the pipeline:**
- `pydantic.ValidationError` → raised directly (the pipeline's error handlers already catch this type)
- All subprocess/timeout/JSON failures → wrapped in `CLIBackendError`
- The pipeline currently catches `Exception` broadly in consensus escalation, so `CLIBackendError` is caught automatically

### §6.2 Subprocess Invocation

All subprocess calls use:
```python
subprocess.run(
    command,
    capture_output=True,
    text=True,
    encoding="utf-8",
    timeout=timeout_seconds,
    env={**os.environ, **extra_env},  # e.g., ANTHROPIC_API_KEY for claude
    check=True,  # raises CalledProcessError on non-zero exit
)
```

**Encoding (§14.5):** `encoding="utf-8"` is **mandatory** on all subprocess calls. On Windows, `text=True` without an explicit encoding defaults to the system code page (typically cp1252/Western European), which cannot decode Arabic text. This causes `UnicodeDecodeError` in the subprocess reader thread before the adapter ever sees the output. Discovered during the first real CLI integration test (2026-03-28).

**Timeout:** Default 120 seconds (from `ExcerptingConfig.TIMEOUT_SECONDS`). Passed through from the `create()` call if the caller provides a custom timeout via kwargs. If not provided, use 120s.

Note: The `create()` signature does not include `timeout` as a named parameter because the current call sites don't pass it. However, the adapter accepts it via `**kwargs` and uses it if present, defaulting to 120s.

### §6.3 OAuth Token Management

Claude CLI requires an OAuth token from `~/.claude/.credentials.json`:

```python
def _get_oauth_token() -> str:
    """Read the OAuth access token from Claude Code credentials."""
    cred_path = Path.home() / ".claude" / ".credentials.json"
    if not cred_path.exists():
        raise CLIBackendError(
            f"Claude credentials not found at {cred_path}. "
            "Run 'claude' once to authenticate.",
            backend="claude",
        )
    data = json.loads(cred_path.read_text())
    try:
        return data["claudeAiOauth"]["accessToken"]
    except KeyError:
        raise CLIBackendError(
            "OAuth token not found in credentials file. "
            "Expected data['claudeAiOauth']['accessToken'].",
            backend="claude",
        )
```

**Token refresh on auth error:** If a Claude subprocess call fails with an error message containing "unauthorized", "401", "auth", or "token expired" (case-insensitive), the adapter:
1. Re-reads the credentials file (token may have been refreshed by another process)
2. Retries the call once with the new token
3. If still fails, propagates the error

This single-retry-on-auth-error happens WITHIN a single attempt of the retry loop (§4), not as an additional retry.

### §6.4 CLI Tool Availability Check

On first use of each backend, verify the CLI tool exists:

```python
def _check_tool_available(tool_name: str) -> None:
    """Verify a CLI tool is on PATH."""
    result = shutil.which(tool_name)
    if result is None:
        raise CLIBackendError(
            f"CLI tool '{tool_name}' not found on PATH. "
            f"Install it or use --backend api to fall back to OpenRouter.",
            backend=tool_name,
        )
```

Cache the result per-backend (check once per adapter lifetime, not per call).

---

## §7 Logging

### §7.1 Hook-Based Logging (Backward-Compatible)

The adapter fires hooks at the same lifecycle points as Instructor, using the same event names. The integration test's `make_hook_logger` function works unchanged.

**`completion:kwargs` — fired before subprocess invocation:**
```python
hook_payload = {
    "model": model,
    "temperature": temperature,
    "max_tokens": max_tokens,
    "messages": messages,
    "backend": f"cli:{backend_name}",  # NEW field (D-CLI-007)
}
```

**`completion:response` — fired after successful parse:**

The hook receives a `CLIResponse` object that mimics the OpenAI `ChatCompletion` structure the integration test expects:

```python
@dataclass
class _CLIUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    def model_dump(self) -> dict:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }

@dataclass
class _CLIMessage:
    content: str | None = None

@dataclass
class _CLIChoice:
    finish_reason: str = "stop"
    message: _CLIMessage = field(default_factory=_CLIMessage)

@dataclass
class CLIResponse:
    model: str = ""
    usage: _CLIUsage = field(default_factory=_CLIUsage)
    choices: list[_CLIChoice] = field(default_factory=lambda: [_CLIChoice()])
    backend: str = ""  # NEW field: "cli:claude", "cli:codex", "cli:gemini"
    latency_seconds: float = 0.0
```

The `on_response` handler in the integration test accesses:
- `response.usage` → `_CLIUsage(None, None, None)` — token counts unavailable from CLI
- `response.usage.model_dump()` → dict with null values
- `response.choices[0].finish_reason` → `"stop"`
- `response.choices[0].message.content` → raw JSON string from subprocess
- `response.model` → the model string passed to `create()`

**`completion:error` — fired on error:**
```python
# The hook receives the exception object directly, same as Instructor
fire_hook("completion:error", error)
```

### §7.2 Structured Logging

In addition to hooks, the adapter logs via Python's `logging` module at key points:

- `INFO`: Backend selected, subprocess command (with token redacted), attempt number
- `WARNING`: Retry triggered (with error summary), auth token refresh
- `ERROR`: All retries exhausted, CLI tool not found
- `DEBUG`: Raw subprocess stdout/stderr, full prompt text

Logger name: `"kr.shared.llm.cli_adapter"`

---

## §8 Configuration Changes

### §8.1 Model String Updates for CLI Mode

When using CLI backend, the `ExcerptingConfig` model strings should be:

| Config field | Current (OpenRouter) | CLI backend |
|-------------|---------------------|-------------|
| `CLASSIFY_MODEL` | `anthropic/claude-opus-4.6` | `anthropic/claude-opus-4.6` (unchanged) |
| `GROUP_MODEL` | `anthropic/claude-opus-4.6` | `anthropic/claude-opus-4.6` (unchanged) |
| `ENRICH_MODEL` | `anthropic/claude-opus-4.6` | `anthropic/claude-opus-4.6` (unchanged) |
| `VERIFY_MODEL` | `openai/gpt-5.4` | `openai/gpt-5.4` (unchanged) |
| `ESCALATION_MODEL` | `mistralai/mistral-large-2411` | `google/gemini-2.5-pro` |

Only `ESCALATION_MODEL` changes — Gemini replaces Mistral for escalation (D-CLI-004). This change is made in the integration test script's `--backend cli` path, NOT in `contracts.py` defaults (which remain the OpenRouter values for backward compatibility).

### §8.2 The `--backend` Flag

The `run_integration_test.py` script gains a `--backend` argument:

```python
parser.add_argument(
    "--backend",
    choices=["cli", "api"],
    default="api",
    help="LLM backend: 'cli' for CLI tools, 'api' for OpenRouter (default: api)",
)
```

When `--backend cli`:
- `create_client()` returns a `CLIInstructorAdapter()` instead of an Instructor client
- `ESCALATION_MODEL` is overridden to `google/gemini-2.5-pro`
- No `OPENROUTER_API_KEY` is required

When `--backend api`:
- Current behavior preserved exactly (OpenRouter + Instructor)
- This is the default, so existing scripts/workflows are unaffected

### §8.3 `run_full_integration.py` Changes

The batch script passes `--backend` through to `run_integration_test.py`:

```python
parser.add_argument(
    "--backend",
    choices=["cli", "api"],
    default="api",
    help="LLM backend passed to run_integration_test.py",
)
```

And includes it in the subprocess command that invokes the single-package runner.

---

## §9 Integration Test Script Changes

### §9.1 New `create_cli_client()` Function

```python
def create_cli_client() -> CLIInstructorAdapter:
    """Create a CLI adapter client."""
    from shared.llm.cli_adapter import CLIInstructorAdapter
    return CLIInstructorAdapter()
```

### §9.2 Client Creation Branch

In the main function, the client creation block becomes:

```python
if mock:
    enrich_client, verify_client, escalation_client = create_mock_clients()
elif backend == "cli":
    enrich_client = create_cli_client()
    verify_client = create_cli_client()
    escalation_client = create_cli_client()
else:  # backend == "api"
    enrich_client = create_client(timeout=config.TIMEOUT_SECONDS)
    verify_client = create_client(timeout=config.TIMEOUT_SECONDS)
    escalation_client = create_client(timeout=config.TIMEOUT_SECONDS)
```

Hook registration works identically for both client types (both support `.on()`).

### §9.3 Config Override for CLI

When `--backend cli`, override the escalation model:
```python
if backend == "cli":
    config = config.model_copy(update={"ESCALATION_MODEL": "google/gemini-2.5-pro"})
```

---

## §10 Test Compatibility

### §10.1 Existing Tests Pass Unchanged

All 768+ existing tests mock at `client.chat.completions.create` (via `_make_mock_instructor_client` in conftest.py). The adapter's `create` method is at the same attribute path. Mocks replace it identically. No test changes needed.

Verify by running:
```bash
PYTHONPATH=. python -m pytest engines/excerpting/tests/ -v --tb=short
```
Result must be: same count, same pass/skip/fail as baseline (766 passed, 2 skipped).

### §10.2 New Unit Tests for the Adapter

New tests go in `shared/llm/tests/test_cli_adapter.py`. These test the adapter in isolation (mocking `subprocess.run`):

**Required test cases:**

1. **`test_create_interface_exists`** — Verify `adapter.chat.completions.create` is callable.

2. **`test_provider_routing_anthropic`** — Model `anthropic/claude-opus-4.6` → claude backend invoked.

3. **`test_provider_routing_openai`** — Model `openai/gpt-5.4` → codex backend invoked.

4. **`test_provider_routing_google`** — Model `google/gemini-2.5-pro` → gemini backend invoked.

5. **`test_provider_routing_unknown_fallback`** — Unknown prefix → default backend.

6. **`test_claude_command_flags`** — Verify `--bare`, `--no-session-persistence`, `--max-turns 2`, `--output-format json`, `--model opus` are all present in the subprocess command.

7. **`test_codex_schema_file_created`** — Verify schema is written to temp file with `additionalProperties: false`.

8. **`test_codex_schema_patching_recursive`** — Verify `additionalProperties: false` is added at every nested object level.

9. **`test_gemini_command_flags`** — Verify `-y`, `--output-format text` in command.

10. **`test_schema_in_system_prompt_claude`** — Verify JSON schema appears in the `--system-prompt` argument.

11. **`test_schema_in_prompt_gemini`** — Verify JSON schema appears in the prompt.

12. **`test_retry_on_validation_error`** — Return invalid JSON on attempt 1, valid on attempt 2. Verify 2 subprocess calls, second includes error feedback.

13. **`test_retry_exhausted_raises_validation_error`** — Return invalid JSON on all attempts. Verify `pydantic.ValidationError` raised (not `CLIBackendError`).

14. **`test_retry_on_json_parse_error`** — Return non-JSON on attempt 1, valid JSON on attempt 2. Verify retry with feedback.

15. **`test_retry_on_subprocess_timeout`** — First call raises `TimeoutExpired`, second succeeds. Verify backoff sleep.

16. **`test_retry_on_subprocess_error`** — First call exits non-zero, second succeeds.

17. **`test_hook_completion_kwargs_fired`** — Register hook, make call, verify hook called with expected dict.

18. **`test_hook_completion_response_fired`** — Verify `CLIResponse` shape matches integration test expectations.

19. **`test_hook_completion_error_fired`** — Verify error hook fires on failure.

20. **`test_oauth_token_read`** — Mock credentials file, verify token extracted correctly.

21. **`test_oauth_token_missing_raises`** — No credentials file → `CLIBackendError`.

22. **`test_oauth_token_refresh_on_auth_error`** — First call fails auth, token refreshed, second call succeeds.

23. **`test_json_extraction_strips_markdown`** — Raw output wrapped in ` ```json ... ``` ` → extracted correctly.

24. **`test_json_extraction_finds_object`** — Raw output with surrounding text → JSON object extracted.

25. **`test_cli_tool_not_found_raises`** — `shutil.which` returns None → `CLIBackendError`.

26. **`test_max_retries_zero_means_one_attempt`** — `max_retries=0` → exactly 1 subprocess call.

27. **`test_max_retries_two_means_three_attempts`** — `max_retries=2` → up to 3 subprocess calls.

28. **`test_response_model_with_model_validators`** — Use a Pydantic model with `@model_validator` constraints. Verify the adapter catches validation errors and retries with feedback that includes the validator's error message.

29. **`test_temperature_logged_not_passed`** — Verify `temperature` appears in hook kwargs but NOT in subprocess command args.

30. **`test_cli_response_usage_is_null`** — Verify `CLIResponse.usage.prompt_tokens` is None.

---

## §11 Error Codes

The adapter does not define new error codes for the excerpting engine. It raises exceptions that the existing error-handling code catches:

| Scenario | Exception | Pipeline handling |
|----------|-----------|-------------------|
| Schema validation fails (all retries) | `pydantic.ValidationError` | Caught by Phase 2/3 error handlers → EX-C-001/EX-C-002/EX-M-002 |
| Subprocess timeout | `CLIBackendError` | Caught by broad `except Exception` → same error code as LLM timeout |
| Non-zero exit | `CLIBackendError` | Caught by broad `except Exception` |
| CLI tool not found | `CLIBackendError` | Fatal — script exits |
| OAuth token missing | `CLIBackendError` | Fatal — script exits |

---

## §12 File Layout

```
shared/
  llm/
    __init__.py            # Empty
    cli_adapter.py         # CLIInstructorAdapter + CLIBackendError + CLIResponse
    CLI_ADAPTER_SPEC.md    # This file
    tests/
      __init__.py          # Empty
      test_cli_adapter.py  # 30 unit tests (§10.2)
```

No other files are created or modified by the adapter implementation itself. The integration test script changes (§9) are a separate task in the same NEXT.md.

---

## §13 Invariants

**INV-1:** The adapter NEVER modifies the `messages` list passed by the caller. Augmented prompts for retries are constructed as new strings.

**INV-2:** The adapter NEVER touches pipeline code. It is imported only by integration test scripts.

**INV-3:** All existing tests pass with zero changes after the adapter is added.

**INV-4:** The `--backend api` path preserves current behavior byte-for-byte. No code is deleted.

**INV-5:** Arabic diacritics pass through subprocess pipes byte-perfectly. The adapter uses `text=True` (UTF-8) for all subprocess calls and never applies Unicode normalization.

**INV-6:** Temp files (Codex schema, Codex output) are always cleaned up, even on error (use `try/finally`).

**INV-7:** The OAuth token is never logged, printed, or included in hook payloads. It appears only in the subprocess environment variable.

---

## §14 Implementation Notes

### §14.1 Prompt Length and Command-Line Limits

The `claude -p "{prompt}"` and `gemini -p "{prompt}"` patterns pass the full prompt as a command-line argument. For the largest chunks (5000+ Arabic words ≈ 30KB text, doubled on retry with error feedback ≈ 60KB), this is well within Linux's ARG_MAX (~2MB). However, if prompts ever approach 500KB, switch to stdin-based passing (`echo "{prompt}" | claude --bare ...`). For the current excerpting engine workload, command-line passing is safe.

### §14.2 Codex Output File May Contain Envelope

Codex writes output to the file specified by `-o`. The output may be raw JSON matching the schema, or it may be wrapped in an envelope. CC must test the actual format and extract accordingly.

### §14.3 `shared/` Is a Namespace Package

The `shared/` directory has no `__init__.py` — it is a PEP 420 implicit namespace package. The `shared/llm/__init__.py` file is needed, but `shared/__init__.py` must NOT be created (other subdirectories rely on namespace package behavior). Verified: `PYTHONPATH=. python -c "from shared.llm.cli_adapter import CLIInstructorAdapter"` works without `shared/__init__.py`.

### §14.4 Post-Review Amendments

This SPEC was amended after adversarial self-review (commit after initial). Changes:
- §5.2: `json.dumps` → `json.dump` (TypeError crash fix)
- §2.4: Added exact hook firing conventions per event type (kwargs expansion vs positional arg)
- §4.2/§4.5: `extract_json` returns `dict | list`, not `str` (removed redundant `json.loads`)
- §5.1: Added message extraction logic and no-system-message case (escalation call site compatibility)
- §3.1: Added WARNING log on unknown model prefix fallback
- §3.2: Documented `--output-format json` envelope risk

### §14.5 Windows Subprocess Encoding

On Windows, `subprocess.run(text=True)` decodes stdout/stderr using the system code page (typically cp1252 for Western European locales). Arabic text from the Claude/Gemini/Codex CLI tools contains bytes that cp1252 cannot decode, causing `UnicodeDecodeError` in the subprocess reader thread before the adapter ever sees the output.

**Fix:** All three `subprocess.run()` calls MUST include `encoding="utf-8"` alongside `text=True`. This is explicit in §6.2. On Linux, `encoding="utf-8"` is redundant (the default locale is usually UTF-8) but harmless. On Windows, it is mandatory.

**Discovered:** First real CLI integration test (2026-03-28). All 34 unit tests passed because they mock `subprocess.run` and return Python strings directly, bypassing the real byte-decoding path. This is a class of bug that mocked tests structurally cannot catch.
