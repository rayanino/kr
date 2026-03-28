# NEXT — CLI Adapter Implementation

## Current Position

- **Baseline:** 766 tests passing, 2 skipped, 0 failed
- **Commit:** `d69f8f52` (master HEAD — CLI backend decision record)
- **Engine:** Excerpting (shared infrastructure)
- **Milestone:** CLI backend architecture APPROVED by 4-reviewer process. Adapter SPEC written. Ready for implementation.

## What Just Happened

A 4-reviewer architecture review (Claude Chat, ChatGPT 5.4, Gemini CLI, Claude Code) validated the CLI backend transition. 8 blocking findings were identified and resolved. The approved architecture is documented in the decision record. The formal adapter SPEC has been written.

## What to Do

Implement `CLIInstructorAdapter` — a drop-in replacement for `instructor.Instructor` that routes LLM calls to CLI backends (`claude -p`, `codex exec`, `gemini -p`). Then update integration test scripts to support `--backend cli`.

## Read First

Read these files IN FULL before writing any code:

1. **`shared/llm/CLI_ADAPTER_SPEC.md`** — The formal specification. This is your implementation guide. Every section must be implemented as described. Do not deviate.
2. **`docs/superpowers/specs/2026-03-28-cli-backend-review-decisions.md`** — The decision record. Background on why things are designed this way. Read §"The Working Recipe" and §"Critical constraints" carefully.
3. **`engines/excerpting/contracts.py` lines 582-678** — The 6 LLM response schemas the adapter must parse and validate.
4. **`engines/excerpting/tests/conftest.py` lines 205-222** — The `_make_mock_instructor_client` pattern. Your adapter must be mockable in this same way.
5. **`scripts/run_integration_test.py` lines 48-63** — Current `create_client()`. Your adapter replaces this when `--backend cli`.
6. **`scripts/run_integration_test.py` lines 70-160** — Hook-based logging. Your `CLIResponse` dataclass must satisfy every `hasattr` / attribute access in `on_response` (lines 112-146).
7. **`scripts/run_integration_test.py` lines 460-484** — Client creation + hook registration. Your adapter must support `.on()` with the same event names.

## What to Build

### File 1: `shared/llm/__init__.py`
Empty file (package marker).

### File 2: `shared/llm/cli_adapter.py`
The full adapter implementation per the SPEC. Contains:

- `CLIBackendError(Exception)` — Custom exception (SPEC §6.1)
- `CLIInstructorAdapter` — Main class (SPEC §2)
  - `__init__(default_backend="claude")` — Constructor
  - `chat.completions.create(...)` — Via `_ChatNamespace` and `_CompletionsNamespace` (SPEC §2.2)
  - `on(event, callback)` — Hook registration (SPEC §2.4)
- `_CLIUsage`, `_CLIMessage`, `_CLIChoice`, `CLIResponse` — Response dataclasses (SPEC §7.1). Note: `_CLIUsage` MUST have a `model_dump()` method returning a dict — the integration test's `on_response` calls `response.usage.model_dump()`.
- `_get_oauth_token()` — Token extraction (SPEC §6.3)
- `_check_tool_available(tool_name)` — PATH check (SPEC §6.4)
- `patch_additional_properties(schema)` — Recursive schema patching for Codex (SPEC §5.3)
- `extract_json(raw_output)` — JSON extraction from raw CLI output (SPEC §4.5)

### File 3: `shared/llm/tests/__init__.py`
Empty file (package marker).

### File 4: `shared/llm/tests/test_cli_adapter.py`
30 unit tests as specified in SPEC §10.2. All tests mock `subprocess.run` — no real CLI calls.

For tests needing a simple Pydantic response model, define a local test model:
```python
class SimpleResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
```

For test 28 (`test_response_model_with_model_validators`), define a model with a `@model_validator`:
```python
class ValidatedResponse(BaseModel):
    value: int
    label: str

    @model_validator(mode="after")
    def check_label(self) -> "ValidatedResponse":
        if self.value > 10 and self.label != "high":
            raise ValueError("value > 10 requires label='high'")
        return self
```

### File 5: Changes to `scripts/run_integration_test.py`
- Add `--backend` argument (SPEC §8.2): `choices=["cli", "api"], default="api"`
- Add `create_cli_client()` function (SPEC §9.1)
- Modify client creation block (SPEC §9.2) to branch on `mock` / `cli` / `api`
- Add config override for CLI escalation model (SPEC §9.3)
- Pass `backend` variable from args through to the client creation block

### File 6: Changes to `scripts/run_full_integration.py`
- Add `--backend` argument (SPEC §8.3)
- Pass `--backend {value}` to the subprocess call that invokes `run_integration_test.py`

## Design Decisions (reference — do not re-derive)

All design decisions are in the SPEC and decision record. Key ones:

- **DD-1:** `max_retries=N` means N retries after initial = N+1 total attempts.
- **DD-2:** Schema enforcement is prompt-based + Pydantic post-validation. NOT constrained decoding.
- **DD-3:** Retry feedback includes full validation error with field paths and valid enum values.
- **DD-4:** `--bare` flag mandatory for Claude (avoids Stop hook infinite loop).
- **DD-5:** `--max-turns 2` mandatory for Claude (max-turns 1 can be empty).
- **DD-6:** `additionalProperties: false` must be injected recursively into Codex schemas.
- **DD-7:** OAuth token refresh: on auth error, re-read credentials and retry once within same attempt.
- **DD-8:** JSON extraction must handle: raw JSON, markdown fences, JSON with surrounding text.
- **DD-9:** `temperature` accepted but NOT passed to any CLI tool. IS included in hook payloads.

## Do NOT Do

- **Do NOT modify any files in `engines/excerpting/`** — not source, not tests, not contracts. The adapter is a new file in `shared/llm/`. Only the two integration test scripts are modified.
- **Do NOT run real CLI calls in tests.** All 30 tests mock `subprocess.run`.
- **Do NOT add `instructor` as a dependency of the adapter.** The adapter replaces Instructor — it must not import it.
- **Do NOT use `MagicMock` to implement the namespace chain.** Use real classes (`_ChatNamespace`, `_CompletionsNamespace`).
- **Do NOT add `--backend` to `run_pipeline.py`.** Only the two integration test scripts.
- **Do NOT implement anything beyond what is specified here. After completing all files, run the full test suite, commit and push. Do NOT proceed to the next session.**

## Verification

After implementation, run:

```bash
# 1. All existing tests still pass (MUST match baseline exactly)
PYTHONPATH=. python -m pytest engines/excerpting/tests/ -q --tb=short
# Expected: 766 passed, 2 skipped

# 2. New adapter tests pass
PYTHONPATH=. python -m pytest shared/llm/tests/ -v --tb=short
# Expected: 30 passed

# 3. Combined count
PYTHONPATH=. python -m pytest engines/excerpting/tests/ shared/llm/tests/ -q --tb=short
# Expected: 796 passed, 2 skipped

# 4. Import check — adapter is importable
PYTHONPATH=. python -c "from shared.llm.cli_adapter import CLIInstructorAdapter, CLIBackendError, CLIResponse; print('OK')"

# 5. Interface check — namespace chain works
PYTHONPATH=. python -c "
from shared.llm.cli_adapter import CLIInstructorAdapter
a = CLIInstructorAdapter()
assert hasattr(a, 'chat')
assert hasattr(a.chat, 'completions')
assert callable(a.chat.completions.create)
assert callable(a.on)
print('Interface OK')
"
```

ALL 5 checks must pass. If any fails, fix before committing.

## After This

The architect reviews CC's implementation using the 3-pass review protocol. Then: a real CLI integration test on 1 package to verify end-to-end.
