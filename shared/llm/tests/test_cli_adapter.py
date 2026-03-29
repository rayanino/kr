"""Unit tests for CLIInstructorAdapter (SPEC §10.2).

All 30 tests mock subprocess.run — no real CLI calls.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest
from pydantic import BaseModel, Field, model_validator

from shared.llm.cli_adapter import (
    CLIBackendError,
    CLIInstructorAdapter,
    CLIResponse,
    _CLIUsage,
    _SETUP_TOKEN_PATH,
    _extract_claude_result,
    _get_oauth_token,
    extract_json,
    patch_additional_properties,
)

# ═══════════════════════════════════════════════════════════════════
# Test models
# ═══════════════════════════════════════════════════════════════════


class SimpleResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)


class ValidatedResponse(BaseModel):
    value: int
    label: str

    @model_validator(mode="after")
    def check_label(self) -> "ValidatedResponse":
        if self.value > 10 and self.label != "high":
            raise ValueError("value > 10 requires label='high'")
        return self


class NestedModel(BaseModel):
    inner: SimpleResponse
    tag: str


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture()
def adapter() -> CLIInstructorAdapter:
    return CLIInstructorAdapter()


@pytest.fixture()
def valid_json() -> str:
    return json.dumps({"answer": "test", "confidence": 0.9})


@pytest.fixture()
def mock_oauth() -> Any:
    with patch(
        "shared.llm.cli_adapter._get_oauth_token",
        return_value="fake-token",
    ) as m:
        yield m


@pytest.fixture()
def mock_which() -> Any:
    with patch("shared.llm.cli_adapter.shutil.which", return_value="/usr/bin/claude") as m:
        yield m


def _make_completed_process(
    stdout: str = "", stderr: str = "", returncode: int = 0
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["mock"], returncode=returncode, stdout=stdout, stderr=stderr
    )


MESSAGES = [
    {"role": "system", "content": "You are a JSON API."},
    {"role": "user", "content": "What is 2+2?"},
]


# ═══════════════════════════════════════════════════════════════════
# Test 1: Interface
# ═══════════════════════════════════════════════════════════════════


def test_create_interface_exists(adapter: CLIInstructorAdapter) -> None:
    """Verify adapter.chat.completions.create is callable."""
    assert hasattr(adapter, "chat")
    assert hasattr(adapter.chat, "completions")
    assert callable(adapter.chat.completions.create)
    assert callable(adapter.on)


# ═══════════════════════════════════════════════════════════════════
# Tests 2-5: Provider routing
# ═══════════════════════════════════════════════════════════════════


@patch("shared.llm.cli_adapter.subprocess.run")
def test_provider_routing_anthropic(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Model anthropic/claude-opus-4.6 routes to claude backend."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "claude"


@patch("shared.llm.cli_adapter.subprocess.run")
def test_provider_routing_openai(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_which: Any,
) -> None:
    """Model openai/gpt-5.4 routes to codex backend."""
    mock_run.return_value = _make_completed_process(stdout="")
    # Codex reads from output file — mock Path.read_text
    with patch.object(Path, "read_text", return_value=valid_json):
        adapter.chat.completions.create(
            model="openai/gpt-5.4",
            response_model=SimpleResponse,
            messages=MESSAGES,
        )
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "codex"


@patch("shared.llm.cli_adapter.subprocess.run")
def test_provider_routing_google(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_which: Any,
) -> None:
    """Model google/gemini-2.5-pro routes to gemini backend."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="google/gemini-2.5-pro",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "gemini"


@patch("shared.llm.cli_adapter.subprocess.run")
def test_provider_routing_unknown_fallback(
    mock_run: MagicMock, valid_json: str, mock_oauth: Any, mock_which: Any,
) -> None:
    """Unknown prefix falls back to default backend."""
    adapter = CLIInstructorAdapter(default_backend="claude")
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="mistralai/mistral-large",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "claude"


# ═══════════════════════════════════════════════════════════════════
# Tests 6, 9, 10, 11: Command flags
# ═══════════════════════════════════════════════════════════════════


@patch("shared.llm.cli_adapter.subprocess.run")
def test_claude_command_flags(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Verify --bare, --no-session-persistence, --max-turns 2, etc."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )
    cmd = mock_run.call_args[0][0]
    assert "--bare" in cmd
    assert "--no-session-persistence" in cmd
    assert "--max-turns" in cmd
    mt_idx = cmd.index("--max-turns")
    assert cmd[mt_idx + 1] == "2"
    assert "--output-format" in cmd
    of_idx = cmd.index("--output-format")
    assert cmd[of_idx + 1] == "json"
    assert "--model" in cmd
    m_idx = cmd.index("--model")
    assert cmd[m_idx + 1] == "opus"


@patch("shared.llm.cli_adapter.subprocess.run")
def test_gemini_command_flags(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_which: Any,
) -> None:
    """Verify -y, --output-format text in gemini command."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="google/gemini-2.5-pro",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )
    cmd = mock_run.call_args[0][0]
    assert "-y" in cmd
    assert "--output-format" in cmd
    of_idx = cmd.index("--output-format")
    assert cmd[of_idx + 1] == "text"


@patch("shared.llm.cli_adapter.subprocess.run")
def test_schema_in_system_prompt_claude(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Verify JSON schema appears in the --system-prompt argument."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )
    cmd = mock_run.call_args[0][0]
    sp_idx = cmd.index("--system-prompt")
    system_prompt = cmd[sp_idx + 1]
    assert "JSON SCHEMA:" in system_prompt
    assert '"confidence"' in system_prompt


@patch("shared.llm.cli_adapter.subprocess.run")
def test_schema_in_prompt_gemini(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_which: Any,
) -> None:
    """Verify JSON schema appears in gemini prompt."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="google/gemini-2.5-pro",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )
    cmd = mock_run.call_args[0][0]
    # Gemini combined prompt is at index 2 (after "gemini" "-p")
    prompt = cmd[2]
    assert "JSON SCHEMA:" in prompt
    assert '"confidence"' in prompt


# ═══════════════════════════════════════════════════════════════════
# Tests 7-8: Codex schema
# ═══════════════════════════════════════════════════════════════════


@patch("shared.llm.cli_adapter.subprocess.run")
def test_codex_schema_file_created(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_which: Any,
) -> None:
    """Verify schema temp file is created and --output-schema is in command."""
    mock_run.return_value = _make_completed_process(stdout="")

    # Mock Path.read_text to return valid JSON for the codex output file
    with patch.object(Path, "read_text", return_value=valid_json):
        adapter.chat.completions.create(
            model="openai/gpt-5.4",
            response_model=SimpleResponse,
            messages=MESSAGES,
        )

    cmd = mock_run.call_args[0][0]
    assert "--output-schema" in cmd
    # Verify the schema file path is a .json temp file
    schema_idx = cmd.index("--output-schema")
    schema_path = cmd[schema_idx + 1]
    assert schema_path.endswith(".json")


def test_codex_schema_patching_recursive() -> None:
    """Verify additionalProperties: false at every nested object level."""
    schema = NestedModel.model_json_schema()
    patched = patch_additional_properties(schema)

    # Top level
    assert patched.get("additionalProperties") is False

    # Check $defs
    defs = patched.get("$defs", {})
    for _name, def_schema in defs.items():
        if def_schema.get("type") == "object" or "properties" in def_schema:
            assert def_schema.get("additionalProperties") is False, (
                f"$defs entry missing additionalProperties: false"
            )


# ═══════════════════════════════════════════════════════════════════
# Tests 12-16: Retry behavior
# ═══════════════════════════════════════════════════════════════════


@patch("shared.llm.cli_adapter.subprocess.run")
def test_retry_on_validation_error(
    mock_run: MagicMock, adapter: CLIInstructorAdapter,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Return invalid then valid JSON. Verify 2 calls, second has feedback."""
    invalid = json.dumps({"answer": "test", "confidence": 1.5})  # > 1.0
    valid = json.dumps({"answer": "test", "confidence": 0.9})

    mock_run.side_effect = [
        _make_completed_process(stdout=invalid),
        _make_completed_process(stdout=valid),
    ]

    result = adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
        max_retries=1,
    )

    assert result.confidence == 0.9
    assert mock_run.call_count == 2
    # Second call should have augmented prompt with error feedback
    second_cmd = mock_run.call_args_list[1][0][0]
    second_prompt = second_cmd[2]  # -p argument
    assert "PREVIOUS ATTEMPT FAILED VALIDATION" in second_prompt


@patch("shared.llm.cli_adapter.subprocess.run")
def test_retry_exhausted_raises_validation_error(
    mock_run: MagicMock, adapter: CLIInstructorAdapter,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Invalid JSON on all attempts raises pydantic.ValidationError."""
    from pydantic import ValidationError

    invalid = json.dumps({"answer": "test", "confidence": 1.5})
    mock_run.return_value = _make_completed_process(stdout=invalid)

    with pytest.raises(ValidationError):
        adapter.chat.completions.create(
            model="anthropic/claude-opus-4.6",
            response_model=SimpleResponse,
            messages=MESSAGES,
            max_retries=1,
        )


@patch("shared.llm.cli_adapter.subprocess.run")
def test_retry_on_json_parse_error(
    mock_run: MagicMock, adapter: CLIInstructorAdapter,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Return non-JSON then valid JSON. Verify retry with feedback."""
    valid = json.dumps({"answer": "test", "confidence": 0.9})

    mock_run.side_effect = [
        _make_completed_process(stdout="This is not JSON at all"),
        _make_completed_process(stdout=valid),
    ]

    result = adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
        max_retries=1,
    )

    assert result.answer == "test"
    assert mock_run.call_count == 2
    second_cmd = mock_run.call_args_list[1][0][0]
    second_prompt = second_cmd[2]
    assert "PREVIOUS ATTEMPT PRODUCED INVALID JSON" in second_prompt


@patch("shared.llm.cli_adapter.time.sleep")
@patch("shared.llm.cli_adapter.subprocess.run")
def test_retry_on_subprocess_timeout(
    mock_run: MagicMock, mock_sleep: MagicMock,
    adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """First call raises TimeoutExpired, second succeeds. Verify backoff."""
    mock_run.side_effect = [
        subprocess.TimeoutExpired(cmd="claude", timeout=120),
        _make_completed_process(stdout=valid_json),
    ]

    result = adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
        max_retries=1,
    )

    assert result.answer == "test"
    mock_sleep.assert_called_once_with(1)  # 2^0 = 1


@patch("shared.llm.cli_adapter.time.sleep")
@patch("shared.llm.cli_adapter.subprocess.run")
def test_retry_on_subprocess_error(
    mock_run: MagicMock, mock_sleep: MagicMock,
    adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """First call exits non-zero, second succeeds."""
    mock_run.side_effect = [
        subprocess.CalledProcessError(
            returncode=1, cmd="claude", stderr="error"
        ),
        _make_completed_process(stdout=valid_json),
    ]

    result = adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
        max_retries=1,
    )

    assert result.confidence == 0.9
    mock_sleep.assert_called_once_with(1)


@patch("shared.llm.cli_adapter.subprocess.run")
def test_timeout_kwarg_forwarded_to_subprocess(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Verify that kwargs['timeout'] is forwarded to subprocess.run(timeout=...)."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)

    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
        timeout=999,
    )

    # subprocess.run should have been called with timeout=999
    call_kwargs = mock_run.call_args
    assert call_kwargs.kwargs.get("timeout") == 999 or call_kwargs[1].get("timeout") == 999


# ═══════════════════════════════════════════════════════════════════
# Tests 17-19: Hook firing
# ═══════════════════════════════════════════════════════════════════


@patch("shared.llm.cli_adapter.subprocess.run")
def test_hook_completion_kwargs_fired(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Register hook, make call, verify hook called with expected dict."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    captured: list[dict[str, Any]] = []

    def on_request(**kwargs: Any) -> None:
        captured.append(kwargs)

    adapter.on("completion:kwargs", on_request)
    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
        temperature=0.5,
    )

    assert len(captured) == 1
    payload = captured[0]
    assert payload["model"] == "anthropic/claude-opus-4.6"
    assert payload["temperature"] == 0.5
    assert payload["backend"] == "cli:claude"
    assert "messages" in payload


@patch("shared.llm.cli_adapter.subprocess.run")
def test_hook_completion_response_fired(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Verify CLIResponse shape matches integration test expectations."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    captured: list[Any] = []

    def on_response(response: Any) -> None:
        captured.append(response)

    adapter.on("completion:response", on_response)
    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
    )

    assert len(captured) == 1
    response = captured[0]
    assert isinstance(response, CLIResponse)
    assert response.model == "anthropic/claude-opus-4.6"
    assert response.backend == "cli:claude"
    # Integration test accesses these attributes:
    assert response.usage.model_dump() == {
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
    }
    assert response.choices[0].finish_reason == "stop"
    assert response.choices[0].message.content is not None


@patch("shared.llm.cli_adapter.subprocess.run")
def test_hook_completion_error_fired(
    mock_run: MagicMock, adapter: CLIInstructorAdapter,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Verify error hook fires on failure."""
    mock_run.return_value = _make_completed_process(stdout="not json")
    captured: list[Any] = []

    def on_error(error: Any) -> None:
        captured.append(error)

    adapter.on("completion:error", on_error)

    with pytest.raises(CLIBackendError):
        adapter.chat.completions.create(
            model="anthropic/claude-opus-4.6",
            response_model=SimpleResponse,
            messages=MESSAGES,
            max_retries=0,
        )

    assert len(captured) == 1
    assert isinstance(captured[0], json.JSONDecodeError)


# ═══════════════════════════════════════════════════════════════════
# Tests 20-22: OAuth token management
# ═══════════════════════════════════════════════════════════════════


def test_oauth_token_read(tmp_path: Path) -> None:
    """Mock credentials file, verify token extracted correctly."""
    creds = {"claudeAiOauth": {"accessToken": "test-token-123"}}
    cred_file = tmp_path / ".credentials.json"
    cred_file.write_text(json.dumps(creds))

    with patch(
        "shared.llm.cli_adapter.Path.home", return_value=tmp_path / "fake"
    ):
        # Need to place the file where _get_oauth_token looks
        claude_dir = tmp_path / "fake" / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / ".credentials.json").write_text(json.dumps(creds))

        from shared.llm.cli_adapter import _get_oauth_token

        token = _get_oauth_token()
        assert token == "test-token-123"


def test_oauth_token_missing_raises(tmp_path: Path) -> None:
    """No credentials file raises CLIBackendError."""
    with patch(
        "shared.llm.cli_adapter.Path.home",
        return_value=tmp_path / "nonexistent",
    ):
        from shared.llm.cli_adapter import _get_oauth_token

        with pytest.raises(CLIBackendError, match="credentials not found"):
            _get_oauth_token()


@patch("shared.llm.cli_adapter.time.sleep")
@patch("shared.llm.cli_adapter.subprocess.run")
def test_oauth_token_refresh_on_auth_error(
    mock_run: MagicMock, mock_sleep: MagicMock,
    adapter: CLIInstructorAdapter, valid_json: str, mock_which: Any,
) -> None:
    """First call fails auth, token refreshed, second call succeeds."""
    mock_run.side_effect = [
        subprocess.CalledProcessError(
            returncode=1, cmd="claude", stderr="401 Unauthorized"
        ),
        _make_completed_process(stdout=valid_json),
    ]

    with patch(
        "shared.llm.cli_adapter._get_oauth_token",
        return_value="refreshed-token",
    ) as mock_get:
        result = adapter.chat.completions.create(
            model="anthropic/claude-opus-4.6",
            response_model=SimpleResponse,
            messages=MESSAGES,
            max_retries=1,
        )

    assert result.answer == "test"
    # Token should have been fetched multiple times (initial + refresh)
    assert mock_get.call_count >= 2


# ═══════════════════════════════════════════════════════════════════
# Tests 23-24: JSON extraction
# ═══════════════════════════════════════════════════════════════════


def test_json_extraction_strips_markdown() -> None:
    """Raw output wrapped in markdown fences extracted correctly."""
    raw = '```json\n{"answer": "test", "confidence": 0.9}\n```'
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert result["answer"] == "test"


def test_json_extraction_finds_object() -> None:
    """Raw output with surrounding text extracts JSON object."""
    raw = 'Here is the result: {"answer": "test", "confidence": 0.5} done.'
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert result["confidence"] == 0.5


# ═══════════════════════════════════════════════════════════════════
# Test 25: CLI tool not found
# ═══════════════════════════════════════════════════════════════════


def test_cli_tool_not_found_raises() -> None:
    """shutil.which returns None raises CLIBackendError."""
    adapter = CLIInstructorAdapter()

    with patch("shared.llm.cli_adapter.shutil.which", return_value=None):
        with pytest.raises(CLIBackendError, match="not found on PATH"):
            adapter.chat.completions.create(
                model="anthropic/claude-opus-4.6",
                response_model=SimpleResponse,
                messages=MESSAGES,
            )


# ═══════════════════════════════════════════════════════════════════
# Tests 26-27: Retry count semantics
# ═══════════════════════════════════════════════════════════════════


@patch("shared.llm.cli_adapter.subprocess.run")
def test_max_retries_zero_means_one_attempt(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """max_retries=0 means exactly 1 subprocess call."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
        max_retries=0,
    )
    assert mock_run.call_count == 1


@patch("shared.llm.cli_adapter.subprocess.run")
def test_max_retries_two_means_three_attempts(
    mock_run: MagicMock, adapter: CLIInstructorAdapter,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """max_retries=2 with persistent failure → up to 3 subprocess calls."""
    invalid = json.dumps({"answer": "test", "confidence": 1.5})
    mock_run.return_value = _make_completed_process(stdout=invalid)

    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        adapter.chat.completions.create(
            model="anthropic/claude-opus-4.6",
            response_model=SimpleResponse,
            messages=MESSAGES,
            max_retries=2,
        )

    assert mock_run.call_count == 3


# ═══════════════════════════════════════════════════════════════════
# Test 28: model_validator feedback
# ═══════════════════════════════════════════════════════════════════


@patch("shared.llm.cli_adapter.subprocess.run")
def test_response_model_with_model_validators(
    mock_run: MagicMock, adapter: CLIInstructorAdapter,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Pydantic model_validator errors are caught and fed back."""
    # value > 10 but label != "high" triggers validator
    invalid = json.dumps({"value": 15, "label": "low"})
    valid = json.dumps({"value": 15, "label": "high"})

    mock_run.side_effect = [
        _make_completed_process(stdout=invalid),
        _make_completed_process(stdout=valid),
    ]

    result = adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=ValidatedResponse,
        messages=MESSAGES,
        max_retries=1,
    )

    assert result.value == 15
    assert result.label == "high"
    assert mock_run.call_count == 2
    # Second prompt should include the validator error message
    second_cmd = mock_run.call_args_list[1][0][0]
    second_prompt = second_cmd[2]
    assert "PREVIOUS ATTEMPT FAILED VALIDATION" in second_prompt
    assert "value > 10 requires label='high'" in second_prompt


# ═══════════════════════════════════════════════════════════════════
# Test 29: Temperature logged not passed
# ═══════════════════════════════════════════════════════════════════


@patch("shared.llm.cli_adapter.subprocess.run")
def test_temperature_logged_not_passed(
    mock_run: MagicMock, adapter: CLIInstructorAdapter, valid_json: str,
    mock_oauth: Any, mock_which: Any,
) -> None:
    """Temperature appears in hook kwargs but NOT in subprocess command."""
    mock_run.return_value = _make_completed_process(stdout=valid_json)
    captured_kwargs: list[dict[str, Any]] = []

    def on_request(**kwargs: Any) -> None:
        captured_kwargs.append(kwargs)

    adapter.on("completion:kwargs", on_request)
    adapter.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        response_model=SimpleResponse,
        messages=MESSAGES,
        temperature=0.7,
    )

    # Temperature in hook
    assert captured_kwargs[0]["temperature"] == 0.7

    # Temperature NOT in subprocess command
    cmd = mock_run.call_args[0][0]
    cmd_str = " ".join(str(c) for c in cmd)
    assert "temperature" not in cmd_str.lower()
    assert "0.7" not in cmd_str


# ═══════════════════════════════════════════════════════════════════
# Test 30: CLIResponse usage is null
# ═══════════════════════════════════════════════════════════════════


def test_cli_response_usage_is_null() -> None:
    """CLIResponse.usage.prompt_tokens is None."""
    response = CLIResponse()
    assert response.usage.prompt_tokens is None
    assert response.usage.completion_tokens is None
    assert response.usage.total_tokens is None
    dump = response.usage.model_dump()
    assert dump["prompt_tokens"] is None


# ═══════════════════════════════════════════════════════════════════
# Tests 31-34: Review finding fixes
# ═══════════════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════════════
# Tests 35-39: _extract_claude_result (Bug 2 — envelope extraction)
# ═══════════════════════════════════════════════════════════════════


def test_extract_claude_result_array_format() -> None:
    """Array envelope: extracts 'result' from the result-type element."""
    model_text = '{"answer": "test", "confidence": 0.9}'
    array_envelope = json.dumps([
        {"type": "system", "subtype": "init", "message": "starting"},
        {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "result": model_text,
        },
    ])
    extracted = _extract_claude_result(array_envelope)
    assert extracted == model_text


def test_extract_claude_result_array_error() -> None:
    """Array envelope with is_error=True raises CLIBackendError."""
    array_envelope = json.dumps([
        {"type": "system", "subtype": "init"},
        {
            "type": "result",
            "subtype": "error",
            "is_error": True,
            "result": "Token expired",
        },
    ])
    with pytest.raises(CLIBackendError, match="Token expired"):
        _extract_claude_result(array_envelope)


def test_extract_claude_result_array_no_result() -> None:
    """Array with no result-type element returns raw stdout."""
    raw = json.dumps([
        {"type": "system", "subtype": "init"},
        {"type": "progress", "message": "working"},
    ])
    assert _extract_claude_result(raw) == raw


def test_extract_claude_result_raw_text() -> None:
    """Non-JSON input returned unchanged."""
    raw = "This is plain text, not JSON"
    assert _extract_claude_result(raw) == raw


def test_extract_claude_result_dict_format() -> None:
    """Single dict envelope: extracts 'result' field (same as existing behavior)."""
    model_text = '{"answer": "hello", "confidence": 0.7}'
    envelope = json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": model_text,
        "usage": {"input_tokens": 100, "output_tokens": 50},
    })
    extracted = _extract_claude_result(envelope)
    assert extracted == model_text


# ═══════════════════════════════════════════════════════════════════
# Tests 40-42: Token priority (Bug 1 — OAuth token expiry)
# ═══════════════════════════════════════════════════════════════════


def test_token_priority_env_var(tmp_path: Path) -> None:
    """KR_ANTHROPIC_TOKEN env var takes precedence over all other sources."""
    # Create setup-token and credentials so we know env var wins
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    (claude_dir / "kr_setup_token.txt").write_text("setup-token-val")
    creds = {"claudeAiOauth": {"accessToken": "creds-token-val"}}
    (claude_dir / ".credentials.json").write_text(json.dumps(creds))

    with (
        patch.dict(os.environ, {"KR_ANTHROPIC_TOKEN": "env-token-val"}),
        patch("shared.llm.cli_adapter.Path.home", return_value=tmp_path),
        patch("shared.llm.cli_adapter._SETUP_TOKEN_PATH", claude_dir / "kr_setup_token.txt"),
    ):
        token = _get_oauth_token()
    assert token == "env-token-val"


def test_token_priority_setup_token(tmp_path: Path) -> None:
    """Setup-token used when env var is absent."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    (claude_dir / "kr_setup_token.txt").write_text("setup-token-val")
    creds = {"claudeAiOauth": {"accessToken": "creds-token-val"}}
    (claude_dir / ".credentials.json").write_text(json.dumps(creds))

    env = {k: v for k, v in os.environ.items() if k != "KR_ANTHROPIC_TOKEN"}
    with (
        patch.dict(os.environ, env, clear=True),
        patch("shared.llm.cli_adapter.Path.home", return_value=tmp_path),
        patch("shared.llm.cli_adapter._SETUP_TOKEN_PATH", claude_dir / "kr_setup_token.txt"),
    ):
        token = _get_oauth_token()
    assert token == "setup-token-val"


def test_token_priority_credentials_fallback(tmp_path: Path) -> None:
    """Falls back to credentials.json when no env var or setup-token."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    creds = {"claudeAiOauth": {"accessToken": "creds-token-val"}}
    (claude_dir / ".credentials.json").write_text(json.dumps(creds))

    # Point setup-token to a non-existent file
    fake_token_path = tmp_path / "nonexistent" / "kr_setup_token.txt"
    env = {k: v for k, v in os.environ.items() if k != "KR_ANTHROPIC_TOKEN"}
    with (
        patch.dict(os.environ, env, clear=True),
        patch("shared.llm.cli_adapter.Path.home", return_value=tmp_path),
        patch("shared.llm.cli_adapter._SETUP_TOKEN_PATH", fake_token_path),
    ):
        token = _get_oauth_token()
    assert token == "creds-token-val"
