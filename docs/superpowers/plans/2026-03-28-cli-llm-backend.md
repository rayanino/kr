# CLI LLM Backend Implementation Plan

> **For agentic workers:** Each chunk below is designed for a **fresh CC session**. Read the Context section, implement all steps, run the pass criteria. Do NOT proceed to the next chunk — a separate session handles it.

**Goal:** Replace OpenRouter API calls ($292/run) with subscription CLI tools ($0/run) while keeping all pipeline code unchanged.

**Architecture:** A single `CLIInstructorAdapter` class provides the same `.chat.completions.create(response_model=...)` interface as Instructor. It routes calls to `claude -p`, `codex exec`, or `gemini -p` based on model name prefix. Pipeline code (5 call sites across 4 files) is untouched.

**Tech Stack:** Python stdlib (subprocess, json, tempfile, pathlib), Pydantic (existing)

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `shared/llm/__init__.py` | CREATE | Package init |
| `shared/llm/cli_adapter.py` | CREATE | The adapter — all CLI wrappers + routing + retry + logging |
| `shared/llm/tests/__init__.py` | CREATE | Test package init |
| `shared/llm/tests/test_cli_adapter.py` | CREATE | Unit tests with mocked subprocess |
| `scripts/run_integration_test.py` | MODIFY | Add `--backend cli\|api` flag, route client creation |
| `scripts/run_full_integration.py` | MODIFY | Pass `--backend` flag to runner script |

---

## Chunk 1: Core Adapter + Claude Wrapper

**Session objective:** Create `shared/llm/cli_adapter.py` with the `CLIInstructorAdapter` class, the Claude CLI wrapper, schema extraction, retry logic, and request/response logging. Write unit tests with mocked subprocess.

**Estimated effort:** 45–60 min

**Context to read first:**
- This plan (Chunk 1 section)
- `docs/superpowers/specs/2026-03-28-cli-llm-backend-design.md` — full design spec
- `scripts/run_integration_test.py:48-63` — current `create_client()` to understand what we're replacing
- `scripts/run_integration_test.py:71-161` — current logging hooks (our adapter must produce identical file format)
- `engines/excerpting/src/phase3_enrichment.py:270-280` — example call site (how the client is used)
- `engines/excerpting/contracts.py` — `EnrichmentResult`, `ClassificationResult`, etc. (the response_model types)

**Files to create:**
- `shared/llm/__init__.py`
- `shared/llm/cli_adapter.py`
- `shared/llm/tests/__init__.py`
- `shared/llm/tests/test_cli_adapter.py`

### Step 1: Create package structure

Create `shared/llm/__init__.py`:
```python
"""LLM backend abstraction for the KR pipeline."""
```

Create `shared/llm/tests/__init__.py`:
```python
"""Tests for shared.llm."""
```

### Step 2: Write the core adapter class

Create `shared/llm/cli_adapter.py` with this exact content:

```python
"""CLI-based LLM backend adapter.

Replaces Instructor/OpenRouter API calls with subscription CLI tools:
- anthropic/* models → claude -p (Claude Max subscription)
- openai/* models → codex exec (ChatGPT subscription)
- Other models → gemini -p (Gemini subscription)

The adapter provides the same .chat.completions.create(response_model=...)
interface that Instructor uses, so pipeline code is unchanged.
"""
from __future__ import annotations

import json
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Response envelope — mirrors what claude -p --output-format json returns
# ---------------------------------------------------------------------------

class CLIResponse:
    """Minimal response object matching the fields that logging hooks read."""

    def __init__(
        self,
        content: str,
        model: str,
        finish_reason: str = "stop",
    ) -> None:
        self.content = content
        self.model = model
        self.finish_reason = finish_reason
        # CLI tools don't report token usage
        self.usage = None

    class _Choice:
        def __init__(self, content: str, finish_reason: str) -> None:
            self.message = type("Msg", (), {"content": content})()
            self.finish_reason = finish_reason

    @property
    def choices(self) -> list[Any]:
        return [self._Choice(self.content, self.finish_reason)]


# ---------------------------------------------------------------------------
# Namespace shim so client.chat.completions.create(...) works
# ---------------------------------------------------------------------------

class _Completions:
    """Namespace so adapter.chat.completions.create() matches Instructor."""

    def __init__(self, adapter: CLIInstructorAdapter) -> None:
        self._adapter = adapter

    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        response_model: Type[T],
        temperature: float = 0.0,
        max_tokens: int = 8192,
        max_retries: int = 2,
        **kwargs: Any,
    ) -> T:
        return self._adapter._dispatch(
            model=model,
            messages=messages,
            response_model=response_model,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
        )


class _Chat:
    """Namespace so adapter.chat.completions.create() works."""

    def __init__(self, adapter: CLIInstructorAdapter) -> None:
        self.completions = _Completions(adapter)


# ---------------------------------------------------------------------------
# Main adapter
# ---------------------------------------------------------------------------

class CLIInstructorAdapter:
    """Drop-in replacement for instructor.Instructor using CLI tools.

    Usage:
        adapter = CLIInstructorAdapter(timeout=120)
        result = adapter.chat.completions.create(
            model="anthropic/claude-opus-4.6",
            response_model=ClassificationResult,
            messages=[{"role": "system", "content": "..."}, ...],
        )
    """

    def __init__(
        self,
        timeout: int = 120,
        log_dir: Optional[Path] = None,
        client_name: str = "cli",
    ) -> None:
        self.timeout = timeout
        self.log_dir = log_dir
        self.client_name = client_name
        self.chat = _Chat(self)
        self._call_counter = 0
        # Hook-compatibility: no-op .on() method
        self._hooks: dict[str, list[Any]] = {}

    def on(self, event: str, callback: Any) -> None:
        """Accept hook registration (for compatibility) but use internal logging."""
        self._hooks.setdefault(event, []).append(callback)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def _dispatch(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        response_model: Type[T],
        temperature: float,
        max_tokens: int,
        max_retries: int,
    ) -> T:
        """Route call to the right CLI tool based on model prefix."""
        schema = response_model.model_json_schema()
        system_prompt, user_message = self._extract_messages(messages)

        self._call_counter += 1
        call_id = f"{self.client_name}_{self._call_counter:04d}"

        # Log request
        self._log_request(call_id, model, temperature, max_tokens, messages)

        # Determine backend
        if model.startswith("anthropic/"):
            call_fn = self._call_claude
        elif model.startswith("openai/"):
            call_fn = self._call_codex
        else:
            call_fn = self._call_gemini

        # Retry loop (same semantics as Instructor's max_retries)
        last_error: Optional[Exception] = None
        for attempt in range(1 + max_retries):
            try:
                start = time.monotonic()
                raw_json = call_fn(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    schema=schema,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency = time.monotonic() - start

                # Parse and validate with Pydantic
                parsed = response_model.model_validate_json(raw_json)

                # Log success
                self._log_response(call_id, model, raw_json, latency)

                logger.info(
                    "CLI call %s: model=%s backend=%s latency=%.1fs attempt=%d",
                    call_id, model, call_fn.__name__, latency, attempt + 1,
                )
                return parsed

            except ValidationError as e:
                last_error = e
                logger.warning(
                    "CLI call %s attempt %d/%d validation error: %s",
                    call_id, attempt + 1, 1 + max_retries, str(e)[:200],
                )
                # Append validation error to user message for retry
                user_message = (
                    user_message
                    + f"\n\n[Previous attempt failed validation: {str(e)[:300]}. "
                    f"Please fix and try again.]"
                )

            except subprocess.TimeoutExpired:
                last_error = TimeoutError(
                    f"CLI call {call_id} timed out after {self.timeout}s"
                )
                logger.warning("CLI call %s timed out", call_id)

            except Exception as e:
                last_error = e
                wait = 2 ** attempt
                logger.warning(
                    "CLI call %s attempt %d/%d error: %s. Backing off %ds.",
                    call_id, attempt + 1, 1 + max_retries, str(e)[:200], wait,
                )
                time.sleep(wait)

        # All retries exhausted
        self._log_error(call_id, last_error)
        raise last_error  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Message extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_messages(
        messages: list[dict[str, str]],
    ) -> tuple[str, str]:
        """Split messages into system prompt and user message."""
        system = ""
        user = ""
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            elif m["role"] == "user":
                user = m["content"]
        return system, user

    # ------------------------------------------------------------------
    # Claude CLI wrapper
    # ------------------------------------------------------------------

    def _call_claude(
        self,
        *,
        system_prompt: str,
        user_message: str,
        schema: dict[str, Any],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Claude via `claude -p` with --json-schema.

        Returns the raw JSON string conforming to the schema.
        """
        # Build command
        cmd: list[str] = [
            "claude",
            "-p", user_message,
            "--output-format", "json",
            "--json-schema", json.dumps(schema),
            "--model", self._claude_model_alias(model),
            "--no-session-persistence",
            "--tools", "",
        ]
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout + 30,  # extra buffer for CLI startup
            encoding="utf-8",
        )

        if result.returncode != 0:
            stderr = result.stderr[:500] if result.stderr else ""
            raise RuntimeError(
                f"claude -p exited {result.returncode}: {stderr}"
            )

        # Parse the JSON envelope
        envelope = json.loads(result.stdout)
        if envelope.get("is_error"):
            raise RuntimeError(
                f"claude -p error: {envelope.get('result', 'unknown')}"
            )

        # The model's response is in the 'result' field
        raw_result = envelope.get("result", "")

        # If result is already a dict/list (parsed by envelope), re-serialize
        if isinstance(raw_result, (dict, list)):
            return json.dumps(raw_result, ensure_ascii=False)

        return raw_result

    @staticmethod
    def _claude_model_alias(model: str) -> str:
        """Convert OpenRouter model string to claude CLI alias."""
        m = model.lower()
        if "opus" in m:
            return "opus"
        if "sonnet" in m:
            return "sonnet"
        if "haiku" in m:
            return "haiku"
        # Fallback: return the model string as-is
        return model.split("/")[-1]

    # ------------------------------------------------------------------
    # Codex CLI wrapper (Chunk 2 will implement)
    # ------------------------------------------------------------------

    def _call_codex(
        self,
        *,
        system_prompt: str,
        user_message: str,
        schema: dict[str, Any],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Codex via `codex exec`. Implemented in Chunk 2."""
        raise NotImplementedError("Codex wrapper — implement in Chunk 2")

    # ------------------------------------------------------------------
    # Gemini CLI wrapper (Chunk 2 will implement)
    # ------------------------------------------------------------------

    def _call_gemini(
        self,
        *,
        system_prompt: str,
        user_message: str,
        schema: dict[str, Any],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Gemini via `gemini -p`. Implemented in Chunk 2."""
        raise NotImplementedError("Gemini wrapper — implement in Chunk 2")

    # ------------------------------------------------------------------
    # Logging (same file format as run_integration_test.py hooks)
    # ------------------------------------------------------------------

    def _log_request(
        self,
        call_id: str,
        model: str,
        temperature: float,
        max_tokens: int,
        messages: list[dict[str, str]],
    ) -> None:
        if self.log_dir is None:
            return
        req_dir = self.log_dir / "raw_llm_requests"
        req_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "call_id": call_id,
            "model": model,
            "backend": "cli",
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": m.get("role", ""), "content": m.get("content", "")[:2000]}
                for m in messages
            ],
        }
        path = req_dir / f"{call_id}.json"
        path.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _log_response(
        self,
        call_id: str,
        model: str,
        raw_content: str,
        latency: float,
    ) -> None:
        if self.log_dir is None:
            return
        resp_dir = self.log_dir / "raw_llm_responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "call_id": call_id,
            "latency_seconds": round(latency, 2),
            "model": model,
            "backend": "cli",
            "usage": None,  # CLI tools don't report token usage
            "finish_reason": "stop",
            "raw_content": raw_content[:50000],
        }
        path = resp_dir / f"{call_id}.json"
        path.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _log_error(
        self, call_id: str, error: Optional[Exception]
    ) -> None:
        if self.log_dir is None:
            return
        resp_dir = self.log_dir / "raw_llm_responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "call_id": call_id,
            "error_type": type(error).__name__ if error else "Unknown",
            "error": str(error)[:500] if error else "Unknown error",
        }
        path = resp_dir / f"{call_id}_error.json"
        path.write_text(
            json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )
```

### Step 3: Write unit tests

Create `shared/llm/tests/test_cli_adapter.py`:

```python
"""Tests for CLIInstructorAdapter — Claude wrapper + core routing."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from shared.llm.cli_adapter import CLIInstructorAdapter


# ---------------------------------------------------------------------------
# Test response models (simple Pydantic schemas)
# ---------------------------------------------------------------------------

class SimpleResponse(BaseModel):
    status: str
    count: int


class ScholarResponse(BaseModel):
    name: str
    school: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_claude_envelope(result_json: dict) -> str:
    """Build a claude -p --output-format json envelope."""
    return json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": json.dumps(result_json, ensure_ascii=False),
        "session_id": "test-session",
        "total_cost_usd": 0,
    })


def _make_failed_envelope(error_msg: str) -> str:
    return json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": True,
        "result": error_msg,
    })


# ---------------------------------------------------------------------------
# Tests: message extraction
# ---------------------------------------------------------------------------

class TestMessageExtraction:
    def test_extracts_system_and_user(self) -> None:
        messages = [
            {"role": "system", "content": "You are an expert."},
            {"role": "user", "content": "Classify this text."},
        ]
        sys, user = CLIInstructorAdapter._extract_messages(messages)
        assert sys == "You are an expert."
        assert user == "Classify this text."

    def test_user_only_messages(self) -> None:
        messages = [{"role": "user", "content": "Just a question."}]
        sys, user = CLIInstructorAdapter._extract_messages(messages)
        assert sys == ""
        assert user == "Just a question."


# ---------------------------------------------------------------------------
# Tests: model alias mapping
# ---------------------------------------------------------------------------

class TestModelAlias:
    def test_opus(self) -> None:
        assert CLIInstructorAdapter._claude_model_alias("anthropic/claude-opus-4.6") == "opus"

    def test_sonnet(self) -> None:
        assert CLIInstructorAdapter._claude_model_alias("anthropic/claude-sonnet-4") == "sonnet"

    def test_haiku(self) -> None:
        assert CLIInstructorAdapter._claude_model_alias("anthropic/claude-haiku-4.5") == "haiku"


# ---------------------------------------------------------------------------
# Tests: routing
# ---------------------------------------------------------------------------

class TestRouting:
    def test_routes_anthropic_to_claude(self) -> None:
        adapter = CLIInstructorAdapter()
        with patch.object(adapter, "_call_claude") as mock_claude:
            mock_claude.return_value = '{"status":"ok","count":1}'
            result = adapter.chat.completions.create(
                model="anthropic/claude-opus-4.6",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "test"}],
            )
            mock_claude.assert_called_once()
            assert result.status == "ok"
            assert result.count == 1

    def test_routes_openai_to_codex(self) -> None:
        adapter = CLIInstructorAdapter()
        with pytest.raises(NotImplementedError, match="Codex"):
            adapter.chat.completions.create(
                model="openai/gpt-5.4",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "test"}],
            )

    def test_routes_unknown_to_gemini(self) -> None:
        adapter = CLIInstructorAdapter()
        with pytest.raises(NotImplementedError, match="Gemini"):
            adapter.chat.completions.create(
                model="mistralai/mistral-large-2411",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "test"}],
            )


# ---------------------------------------------------------------------------
# Tests: Claude wrapper with mocked subprocess
# ---------------------------------------------------------------------------

class TestClaudeWrapper:
    def test_successful_call(self) -> None:
        adapter = CLIInstructorAdapter()
        envelope = _make_claude_envelope({"status": "ok", "count": 42})

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=envelope, stderr=""
            )
            result = adapter.chat.completions.create(
                model="anthropic/claude-opus-4.6",
                response_model=SimpleResponse,
                messages=[
                    {"role": "system", "content": "Be precise."},
                    {"role": "user", "content": "Count items."},
                ],
            )

        assert result.status == "ok"
        assert result.count == 42

        # Verify command structure
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "claude"
        assert "-p" in cmd
        assert "--json-schema" in cmd
        assert "--system-prompt" in cmd
        assert "Be precise." in cmd

    def test_validation_retry(self) -> None:
        """On Pydantic validation failure, adapter retries with error feedback."""
        adapter = CLIInstructorAdapter()
        bad = _make_claude_envelope({"status": "ok"})  # missing 'count'
        good = _make_claude_envelope({"status": "ok", "count": 1})

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=bad, stderr=""),
                MagicMock(returncode=0, stdout=good, stderr=""),
            ]
            result = adapter.chat.completions.create(
                model="anthropic/claude-opus-4.6",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "test"}],
                max_retries=2,
            )

        assert result.count == 1
        assert mock_run.call_count == 2

    def test_cli_error_raises(self) -> None:
        adapter = CLIInstructorAdapter()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="auth failed"
            )
            with pytest.raises(RuntimeError, match="claude -p exited 1"):
                adapter.chat.completions.create(
                    model="anthropic/claude-opus-4.6",
                    response_model=SimpleResponse,
                    messages=[{"role": "user", "content": "test"}],
                )

    def test_is_error_envelope_raises(self) -> None:
        adapter = CLIInstructorAdapter()
        envelope = _make_failed_envelope("Not logged in")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=envelope, stderr=""
            )
            with pytest.raises(RuntimeError, match="Not logged in"):
                adapter.chat.completions.create(
                    model="anthropic/claude-opus-4.6",
                    response_model=SimpleResponse,
                    messages=[{"role": "user", "content": "test"}],
                )


# ---------------------------------------------------------------------------
# Tests: logging
# ---------------------------------------------------------------------------

class TestLogging:
    def test_logs_request_and_response(self, tmp_path: Path) -> None:
        adapter = CLIInstructorAdapter(log_dir=tmp_path, client_name="enrich")
        envelope = _make_claude_envelope({"status": "ok", "count": 1})

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=envelope, stderr=""
            )
            adapter.chat.completions.create(
                model="anthropic/claude-opus-4.6",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "test"}],
            )

        # Check request log
        req_file = tmp_path / "raw_llm_requests" / "enrich_0001.json"
        assert req_file.exists()
        req_data = json.loads(req_file.read_text(encoding="utf-8"))
        assert req_data["call_id"] == "enrich_0001"
        assert req_data["model"] == "anthropic/claude-opus-4.6"
        assert req_data["backend"] == "cli"

        # Check response log
        resp_file = tmp_path / "raw_llm_responses" / "enrich_0001.json"
        assert resp_file.exists()
        resp_data = json.loads(resp_file.read_text(encoding="utf-8"))
        assert resp_data["call_id"] == "enrich_0001"
        assert resp_data["raw_content"] is not None

    def test_logs_error(self, tmp_path: Path) -> None:
        adapter = CLIInstructorAdapter(log_dir=tmp_path, client_name="enrich")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="fail"
            )
            with pytest.raises(RuntimeError):
                adapter.chat.completions.create(
                    model="anthropic/claude-opus-4.6",
                    response_model=SimpleResponse,
                    messages=[{"role": "user", "content": "test"}],
                    max_retries=0,
                )

        err_file = tmp_path / "raw_llm_responses" / "enrich_0001_error.json"
        assert err_file.exists()


# ---------------------------------------------------------------------------
# Tests: Arabic content handling
# ---------------------------------------------------------------------------

class TestArabicContent:
    def test_arabic_in_prompt_preserved(self) -> None:
        adapter = CLIInstructorAdapter()
        envelope = _make_claude_envelope({"name": "ابن تيمية", "confidence": 0.95})

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=envelope, stderr=""
            )
            result = adapter.chat.completions.create(
                model="anthropic/claude-opus-4.6",
                response_model=ScholarResponse,
                messages=[
                    {"role": "system", "content": "تحليل النصوص العلمية"},
                    {"role": "user", "content": "من هو شيخ الإسلام؟"},
                ],
            )

        assert result.name == "ابن تيمية"
        # Verify Arabic was passed to subprocess
        cmd = mock_run.call_args[0][0]
        user_idx = cmd.index("-p") + 1
        assert "شيخ الإسلام" in cmd[user_idx]
```

### Step 4: Run tests

```bash
cd C:/Users/Rayane/Desktop/kr
python -m pytest shared/llm/tests/test_cli_adapter.py -v --tb=short
```

**Expected:** All tests pass. The Claude wrapper, routing, retry, logging, and Arabic handling all work with mocked subprocess.

### Step 5: Commit

```bash
git add shared/llm/
git commit -m "feat(shared/llm): CLI adapter core — Claude wrapper + routing + retry + logging

Phase 1 of CLI LLM backend: replaces OpenRouter API with subscription CLIs.
CLIInstructorAdapter provides identical interface to Instructor.
Claude wrapper calls claude -p with --json-schema for structured output.
Codex and Gemini wrappers are NotImplementedError stubs (Chunk 2)."
```

### Pass criteria
- [ ] `python -m pytest shared/llm/tests/test_cli_adapter.py -v` — all pass
- [ ] `python -c "from shared.llm.cli_adapter import CLIInstructorAdapter"` — imports clean
- [ ] Routing sends anthropic/* to _call_claude, openai/* to _call_codex, others to _call_gemini
- [ ] Retry works: on ValidationError, retries with error feedback appended
- [ ] Logging produces identical file format to current raw_llm_requests/responses
- [ ] Arabic text passes through subprocess correctly (encoding="utf-8")

---

## Chunk 2: Codex + Gemini Wrappers

**Session objective:** Implement `_call_codex()` and `_call_gemini()` in the existing `shared/llm/cli_adapter.py`. Both use structured output via prompt-based schema injection + Pydantic post-validation.

**Estimated effort:** 30–45 min

**Context to read first:**
- This plan (Chunk 2 section)
- `shared/llm/cli_adapter.py` — the file created in Chunk 1 (read the full file)
- `shared/llm/tests/test_cli_adapter.py` — existing tests (understand the pattern)
- `codex exec --help` output (key flags: `-o` for output file, `-s read-only`, `-m` for model)
- `gemini --help` output (key flags: `-p` for non-interactive, `--output-format json`, `-y` for auto-accept)

**Files to modify:**
- `shared/llm/cli_adapter.py` — replace NotImplementedError stubs
- `shared/llm/tests/test_cli_adapter.py` — add tests for codex + gemini

### Step 1: Implement `_call_codex()`

Replace the `_call_codex` stub in `shared/llm/cli_adapter.py` with:

```python
    def _call_codex(
        self,
        *,
        system_prompt: str,
        user_message: str,
        schema: dict[str, Any],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Codex via `codex exec` with output schema.

        Codex supports --output-schema for structured output.
        Falls back to prompt-based schema if --output-schema fails.
        Returns the raw JSON string.
        """
        # Write schema to temp file (codex needs file path, not inline JSON)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(schema, f, ensure_ascii=False)
            schema_path = f.name

        # Build the full prompt (system + user combined for codex)
        full_prompt = ""
        if system_prompt:
            full_prompt += f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
        full_prompt += f"USER REQUEST:\n{user_message}\n\n"
        full_prompt += (
            "Respond ONLY with a valid JSON object matching the provided schema. "
            "No markdown, no explanation, just the JSON."
        )

        # Write prompt to temp file (codex reads from stdin or arg)
        # Also prepare output file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as out_f:
            output_path = out_f.name

        try:
            codex_model = model.split("/")[-1] if "/" in model else model
            cmd: list[str] = [
                "codex", "exec",
                full_prompt,
                "--output-schema", schema_path,
                "-o", output_path,
                "-m", codex_model,
                "-s", "read-only",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 60,  # codex startup is slow
                encoding="utf-8",
            )

            # Read the output file
            output_text = Path(output_path).read_text(encoding="utf-8").strip()

            if not output_text:
                # Fallback: try without --output-schema
                # (some codex versions may not support it)
                logger.warning(
                    "Codex --output-schema produced empty output. "
                    "Retrying with prompt-based schema."
                )
                return self._call_codex_fallback(
                    full_prompt=full_prompt,
                    schema=schema,
                    codex_model=codex_model,
                )

            # The output might be the raw JSON or wrapped
            # Try to parse as JSON directly
            json.loads(output_text)  # validate it's JSON
            return output_text

        finally:
            Path(schema_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def _call_codex_fallback(
        self,
        full_prompt: str,
        schema: dict[str, Any],
        codex_model: str,
    ) -> str:
        """Fallback: embed schema in prompt, parse response as JSON."""
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False)
        prompt_with_schema = (
            f"{full_prompt}\n\n"
            f"Your response MUST conform to this JSON Schema:\n"
            f"```json\n{schema_str}\n```\n\n"
            f"Respond with ONLY the JSON object. No other text."
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as out_f:
            output_path = out_f.name

        try:
            cmd = [
                "codex", "exec",
                prompt_with_schema,
                "-o", output_path,
                "-m", codex_model,
                "-s", "read-only",
            ]
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 60,
                encoding="utf-8",
            )
            output_text = Path(output_path).read_text(encoding="utf-8").strip()

            # Extract JSON from potential markdown fences
            return self._extract_json(output_text)
        finally:
            Path(output_path).unlink(missing_ok=True)
```

### Step 2: Implement `_call_gemini()`

Replace the `_call_gemini` stub with:

```python
    def _call_gemini(
        self,
        *,
        system_prompt: str,
        user_message: str,
        schema: dict[str, Any],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Gemini via `gemini -p`.

        Gemini CLI has --output-format json but no --json-schema.
        We embed the schema in the prompt and post-validate with Pydantic.
        """
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False)
        full_prompt = ""
        if system_prompt:
            full_prompt += f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
        full_prompt += f"USER REQUEST:\n{user_message}\n\n"
        full_prompt += (
            f"Your response MUST be a valid JSON object conforming to this schema:\n"
            f"```json\n{schema_str}\n```\n\n"
            f"Respond with ONLY the JSON object. No markdown fences, no explanation."
        )

        cmd: list[str] = [
            "gemini",
            "-p", full_prompt,
            "-y",  # auto-accept all actions
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout + 60,
            encoding="utf-8",
        )

        if result.returncode != 0:
            stderr = result.stderr[:500] if result.stderr else ""
            raise RuntimeError(
                f"gemini -p exited {result.returncode}: {stderr}"
            )

        # Gemini outputs text to stdout
        output = result.stdout.strip()
        return self._extract_json(output)
```

### Step 3: Add the shared `_extract_json` helper

Add this method to the `CLIInstructorAdapter` class:

```python
    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from text that might contain markdown fences or preamble."""
        # Try direct parse first
        text = text.strip()
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown JSON fence
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            candidate = text[start:end].strip()
            json.loads(candidate)  # validate
            return candidate

        # Try extracting from plain fence
        if "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            candidate = text[start:end].strip()
            json.loads(candidate)
            return candidate

        # Try finding first { to last }
        if "{" in text and "}" in text:
            start = text.index("{")
            end = text.rindex("}") + 1
            candidate = text[start:end]
            json.loads(candidate)
            return candidate

        raise ValueError(f"Could not extract JSON from CLI output: {text[:200]}")
```

### Step 4: Add tests for codex, gemini, and JSON extraction

Append to `shared/llm/tests/test_cli_adapter.py`:

```python
# ---------------------------------------------------------------------------
# Tests: JSON extraction
# ---------------------------------------------------------------------------

class TestExtractJson:
    def test_plain_json(self) -> None:
        result = CLIInstructorAdapter._extract_json('{"status":"ok","count":1}')
        assert json.loads(result) == {"status": "ok", "count": 1}

    def test_markdown_fenced(self) -> None:
        text = 'Here is the result:\n```json\n{"status":"ok","count":1}\n```\n'
        result = CLIInstructorAdapter._extract_json(text)
        assert json.loads(result) == {"status": "ok", "count": 1}

    def test_brace_extraction(self) -> None:
        text = 'The response is {"status":"ok","count":1} as requested.'
        result = CLIInstructorAdapter._extract_json(text)
        assert json.loads(result) == {"status": "ok", "count": 1}

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Could not extract JSON"):
            CLIInstructorAdapter._extract_json("no json here")


# ---------------------------------------------------------------------------
# Tests: Codex wrapper
# ---------------------------------------------------------------------------

class TestCodexWrapper:
    def test_successful_call(self, tmp_path: Path) -> None:
        adapter = CLIInstructorAdapter()
        response_json = '{"status":"ok","count":1}'

        with patch("subprocess.run") as mock_run, \
             patch("pathlib.Path.read_text", return_value=response_json), \
             patch("pathlib.Path.unlink"):
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = adapter.chat.completions.create(
                model="openai/gpt-5.4",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "test"}],
            )

        assert result.status == "ok"
        assert result.count == 1


# ---------------------------------------------------------------------------
# Tests: Gemini wrapper
# ---------------------------------------------------------------------------

class TestGeminiWrapper:
    def test_successful_call(self) -> None:
        adapter = CLIInstructorAdapter()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"status":"ok","count":5}',
                stderr="",
            )
            result = adapter.chat.completions.create(
                model="mistralai/mistral-large-2411",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "test"}],
            )

        assert result.status == "ok"
        assert result.count == 5

    def test_markdown_fenced_output(self) -> None:
        adapter = CLIInstructorAdapter()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='```json\n{"status":"ok","count":3}\n```',
                stderr="",
            )
            result = adapter.chat.completions.create(
                model="mistralai/mistral-large-2411",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "test"}],
            )

        assert result.count == 3
```

### Step 5: Run all tests

```bash
cd C:/Users/Rayane/Desktop/kr
python -m pytest shared/llm/tests/test_cli_adapter.py -v --tb=short
```

**Expected:** All tests pass (Chunk 1 tests + new Chunk 2 tests).

### Step 6: Commit

```bash
git add shared/llm/
git commit -m "feat(shared/llm): Codex + Gemini CLI wrappers + JSON extraction

Complete CLI adapter with all 3 backends:
- Claude: claude -p with --json-schema (native schema enforcement)
- Codex: codex exec with --output-schema (fallback: prompt-based)
- Gemini: gemini -p with prompt-based schema + Pydantic post-validation
JSON extraction handles markdown fences and preamble text."
```

### Pass criteria
- [ ] All tests pass (Chunk 1 + Chunk 2)
- [ ] `_call_codex()` and `_call_gemini()` no longer raise NotImplementedError
- [ ] `_extract_json()` handles: plain JSON, markdown-fenced, brace-extraction, and error case
- [ ] Codex fallback path works when `--output-schema` produces empty output

---

## Chunk 3: Integration Wiring

**Session objective:** Wire the CLI adapter into `run_integration_test.py` and `run_full_integration.py`. Add `--backend cli|api` flag. The pipeline code (engine files) is NOT touched.

**Estimated effort:** 20–30 min

**Context to read first:**
- This plan (Chunk 3 section)
- `shared/llm/cli_adapter.py` — the adapter (read it fully)
- `scripts/run_integration_test.py:42-63` — current `create_client()` function
- `scripts/run_integration_test.py:465-484` — client creation + hook installation
- `scripts/run_integration_test.py:843-910` — argument parser
- `scripts/run_full_integration.py:174-184` — how it calls the runner script

**Files to modify:**
- `scripts/run_integration_test.py`
- `scripts/run_full_integration.py`

### Step 1: Modify `create_client()` in `run_integration_test.py`

Find the `create_client` function (line 48) and replace it with:

```python
def create_client(
    timeout: int = 120,
    backend: str = "cli",
    log_dir: Optional[Path] = None,
    client_name: str = "cli",
) -> Any:
    """Create an LLM client — CLI adapter or OpenRouter API.

    Args:
        timeout: Seconds before call times out.
        backend: "cli" for subscription CLIs, "api" for OpenRouter.
        log_dir: Directory for request/response logs (CLI adapter only).
        client_name: Prefix for log filenames (e.g. "enrich", "verify").
    """
    if backend == "api":
        import instructor
        import openai

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        return instructor.from_openai(
            openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                timeout=timeout,
            ),
            mode=instructor.Mode.JSON,
        )

    # CLI backend
    from shared.llm.cli_adapter import CLIInstructorAdapter

    return CLIInstructorAdapter(
        timeout=timeout,
        log_dir=log_dir,
        client_name=client_name,
    )
```

### Step 2: Modify client creation section (line ~465)

Find the client creation block and replace:

```python
    # ── Create clients ────────────────────────────────────────────
    if mock:
        logger.info("Mock mode: using MagicMock clients")
        enrich_client, verify_client, escalation_client = create_mock_clients()
    else:
        backend = args.backend if hasattr(args, "backend") else "api"
        logger.info("Creating %s LLM clients", backend.upper())

        enrich_client = create_client(
            timeout=config.TIMEOUT_SECONDS,
            backend=backend,
            log_dir=output_dir,
            client_name="enrich",
        )
        verify_client = create_client(
            timeout=config.TIMEOUT_SECONDS,
            backend=backend,
            log_dir=output_dir,
            client_name="verify",
        )
        escalation_client = create_client(
            timeout=config.TIMEOUT_SECONDS,
            backend=backend,
            log_dir=output_dir,
            client_name="escalation",
        )

        # Register logging hooks (API backend only — CLI adapter logs internally)
        if backend == "api":
            for client, name in [
                (enrich_client, "enrich"),
                (verify_client, "verify"),
                (escalation_client, "escalation"),
            ]:
                req_hook, resp_hook, err_hook = make_hook_logger(output_dir, name)
                client.on("completion:kwargs", req_hook)
                client.on("completion:response", resp_hook)
                client.on("completion:error", err_hook)
```

### Step 3: Add `--backend` argument to the parser

Find the argument parser section (around line 895) and add after the `--source-metadata` argument:

```python
    parser.add_argument(
        "--backend",
        choices=["cli", "api"],
        default="cli",
        help="LLM backend: 'cli' uses subscription CLIs ($0), "
             "'api' uses OpenRouter API (requires OPENROUTER_API_KEY). "
             "Default: cli.",
    )
```

### Step 4: Modify `run_full_integration.py` to pass backend

In `scripts/run_full_integration.py`, find the command construction (line ~174):

```python
        cmd = [
            sys.executable,
            str(RUNNER_SCRIPT),
            "--package-path", str(pkg_path),
            "--output-dir", str(pkg_output),
            "--source-metadata", json.dumps(pkg["metadata"], ensure_ascii=False),
        ]
```

Add the backend flag:

```python
        cmd = [
            sys.executable,
            str(RUNNER_SCRIPT),
            "--package-path", str(pkg_path),
            "--output-dir", str(pkg_output),
            "--source-metadata", json.dumps(pkg["metadata"], ensure_ascii=False),
            "--backend", args.backend,
        ]
```

And add `--backend` to the full integration script's own argument parser (find it and add):

```python
    parser.add_argument(
        "--backend",
        choices=["cli", "api"],
        default="cli",
        help="LLM backend: 'cli' or 'api'. Default: cli.",
    )
```

### Step 5: Test with --mock

```bash
cd C:/Users/Rayane/Desktop/kr
PYTHONPATH=. python scripts/run_integration_test.py \
  --package-path experiments/format_diversity_test/packages/ibn_aqil_v1 \
  --output-dir /tmp/test_cli_wiring \
  --mock \
  --backend cli
```

**Expected:** Mock mode works regardless of backend (mock bypasses client creation). This verifies the argument parsing and wiring are correct without making any LLM calls.

### Step 6: Commit

```bash
git add scripts/run_integration_test.py scripts/run_full_integration.py
git commit -m "feat(scripts): wire CLI adapter into integration test runner

--backend cli|api flag (default: cli) routes LLM calls to subscription
CLIs instead of OpenRouter API. Pipeline code unchanged. API mode preserved
for fallback. CLI adapter handles its own request/response logging."
```

### Pass criteria
- [ ] `--help` shows `--backend` flag on both scripts
- [ ] `--mock` mode works with `--backend cli`
- [ ] `--backend api` still works (requires OPENROUTER_API_KEY)
- [ ] CLI adapter creates log files in output dir (raw_llm_requests/, raw_llm_responses/)
- [ ] No changes to any file under `engines/`

---

## Chunk 4: End-to-End Validation

**Session objective:** Run the integration test with `--backend cli` on real packages and verify outputs. Compare with API-backend results from the pre-flight smoke test. This is a validation chunk — no code changes.

**Estimated effort:** 30–60 min (mostly waiting for LLM calls)

**Context to read first:**
- This plan (Chunk 4 section)
- `integration_tests/pre_flight_smoke/` — API-backend results from today's smoke test (baseline)
- `docs/superpowers/specs/2026-03-28-cli-llm-backend-design.md` — the spec

**Pre-requisite:** Chunks 1-3 all committed and tests passing.

### Step 1: Verify unit tests still pass

```bash
cd C:/Users/Rayane/Desktop/kr
python -m pytest shared/llm/tests/test_cli_adapter.py -v --tb=short
python -m pytest engines/excerpting/tests/ -x -q
```

**Expected:** All pass. No regressions.

### Step 2: Run single-chunk smoke test with CLI backend

Run on each of the 5 packages with `--backend cli --max-chunks 1`:

```bash
PYTHONIOENCODING=utf-8 PYTHONPATH=. python scripts/run_integration_test.py \
  --package-path experiments/format_diversity_test/packages/taysir \
  --output-dir integration_tests/cli_smoke/taysir \
  --max-chunks 1 \
  --backend cli \
  --source-metadata '{"author_name":"عبد الله البسام","work_title":"تيسير العلام شرح عمدة الأحكام","science":"فقه","source_school":"حنبلي"}'
```

(Repeat for all 5 packages, substituting paths and metadata from `scripts/run_full_integration.py` PACKAGES config.)

**Start with taysir** — it's the fastest (67s on API) and tests the source_school fix.

### Step 3: Compare CLI vs API results

For each package, compare:

| Check | API result (pre_flight_smoke/) | CLI result (cli_smoke/) |
|-------|------|------|
| Exit code | 0 | Should be 0 |
| Excerpt count | N | Similar (LLM non-determinism expected) |
| Error count | 0 or 1 | Same or fewer |
| Error files | 0 | 0 |
| Request log format | Standard | Standard + "backend":"cli" |
| Response log format | Standard | Standard + "backend":"cli", usage:null |

### Step 4: Verify fix-specific checks on CLI results

Same checks as the pre-flight sweep Phase 3B, but on `integration_tests/cli_smoke/`:
1. **source_school**: taysir enrich request contains "School: حنبلي"
2. **MAX_TOKENS**: ibn_aqil_v3 enrich request has max_tokens=32768
3. **Verifier prompt**: verify request (if triggered) has C-SC-1

### Step 5: Document results

Create `integration_tests/cli_smoke/VALIDATION_REPORT.md` with:
- Per-package results table
- Fix verification results
- Timing comparison (CLI vs API)
- Any issues found
- READY / NOT READY verdict for full CLI run

### Pass criteria
- [ ] All 5 packages exit 0 with excerpts produced
- [ ] No new error types vs API baseline
- [ ] Request/response log files created in correct format
- [ ] source_school shows "حنبلي" for taysir
- [ ] ibn_aqil_v3 produces >0 excerpts (the critical fix 4 check)
- [ ] Timing is acceptable (CLI may be 20-50% slower due to process spawn overhead)

---

## Execution Order

```
Chunk 1 (serial) → Chunk 2 (serial) → Chunk 3 (serial) → Chunk 4 (serial)
```

All chunks are serial — each depends on the previous. Total estimated time: 2-3 hours across 4 sessions.

After Chunk 4 validates, the full 280-chunk run can proceed with `--backend cli` at **$0 cost**.

---

## Known Risks & Mitigations

1. **Nested `claude -p` from within CC session**: The integration test runs `claude -p` as subprocess. If launched from a CC session, this spawns a nested Claude instance. Each `claude -p` call starts a fresh process (no session state shared). Monitor for auth conflicts or rate limit issues during Chunk 4 validation.

2. **CLI startup overhead**: Each `claude -p` invocation has ~3-5s startup overhead (loading config, auth). For 280 chunks × 3 Claude calls = 840 invocations, this adds ~42-70 minutes. Acceptable given the $291 savings.

3. **Codex `--output-schema` may not work**: The fallback path (prompt-based schema) is implemented. If codex structured output is unreliable, consider keeping GPT verify calls on OpenRouter (~$0.67 total).

4. **Gemini model quality for escalation**: Gemini replaces Mistral Large for 3-model escalation. If quality is insufficient, switch to codex for escalation or keep Mistral on OpenRouter (~$0.24 total).

5. **Max plan rate limits**: Claude Max 20x has usage caps. 840 Opus calls in one run may approach limits. If rate-limited, the adapter's retry with backoff handles it. Monitor and report if it occurs.
