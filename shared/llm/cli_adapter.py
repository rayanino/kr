"""CLI Instructor Adapter — drop-in replacement for instructor.Instructor.

Routes LLM calls to CLI backends (claude, codex, gemini) instead of
OpenRouter API. Implements the same ``client.chat.completions.create()``
interface so existing pipeline code and tests work unchanged.

Governing SPEC: shared/llm/CLI_ADAPTER_SPEC.md
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger("kr.shared.llm.cli_adapter")

T = TypeVar("T", bound=BaseModel)

# ═══════════════════════════════════════════════════════════════════
# Exception (SPEC §6.1)
# ═══════════════════════════════════════════════════════════════════


class CLIBackendError(Exception):
    """Raised when a CLI backend fails in a non-recoverable way.

    Wraps subprocess errors, timeouts, and persistent JSON parse failures.
    """

    def __init__(
        self,
        message: str,
        backend: str = "",
        exit_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.backend = backend
        self.exit_code = exit_code


# ═══════════════════════════════════════════════════════════════════
# Response dataclasses (SPEC §7.1)
# ═══════════════════════════════════════════════════════════════════


@dataclass
class _CLIUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    def model_dump(self) -> dict[str, int | None]:
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
    backend: str = ""
    latency_seconds: float = 0.0


# ═══════════════════════════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════════════════════════


_SETUP_TOKEN_PATH = Path.home() / ".claude" / "kr_setup_token.txt"


def _get_setup_token() -> str | None:
    """Read long-lived setup-token if available."""
    if _SETUP_TOKEN_PATH.exists():
        try:
            token = _SETUP_TOKEN_PATH.read_text(encoding="utf-8").strip()
        except (UnicodeDecodeError, OSError) as e:
            logger.warning("Cannot read setup-token at %s: %s", _SETUP_TOKEN_PATH, e)
            return None
        if token:
            return token
    return None


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


def _check_tool_available(tool_name: str) -> None:
    """Verify a CLI tool is on PATH (SPEC §6.4)."""
    result = shutil.which(tool_name)
    if result is None:
        raise CLIBackendError(
            f"CLI tool '{tool_name}' not found on PATH. "
            f"Install it or use --backend api to fall back to OpenRouter.",
            backend=tool_name,
        )


def patch_additional_properties(schema: dict[str, Any]) -> dict[str, Any]:
    """Recursively add additionalProperties: false to all object schemas (SPEC §5.3)."""
    if isinstance(schema, dict):
        if schema.get("type") == "object" or "properties" in schema:
            schema["additionalProperties"] = False
        for _, value in schema.items():
            if isinstance(value, dict):
                patch_additional_properties(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        patch_additional_properties(item)
        for defs_key in ("$defs", "definitions"):
            if defs_key in schema:
                for def_schema in schema[defs_key].values():
                    patch_additional_properties(def_schema)
    return schema


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
            # Handle max-turns exceeded (result field missing or None)
            if parsed.get("subtype") == "error_max_turns":
                raise CLIBackendError(
                    f"Claude CLI hit max-turns limit (num_turns={parsed.get('num_turns')}). "
                    "Model needed more turns to complete.",
                    backend="claude",
                )
            result_text = parsed.get("result")
            if result_text is not None:
                logger.debug("Extracted model text from Claude CLI dict envelope")
                return str(result_text)

    # Case 3: Not an envelope — return as-is
    return raw_stdout


# ═══════════════════════════════════════════════════════════════════
# Provider routing (SPEC §3.1)
# ═══════════════════════════════════════════════════════════════════

_PROVIDER_MAP: dict[str, str] = {
    "anthropic/": "claude",
    "openai/": "codex",
    "google/": "gemini",
}


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


# ═══════════════════════════════════════════════════════════════════
# Auth error detection (SPEC §6.3)
# ═══════════════════════════════════════════════════════════════════

_AUTH_ERROR_PATTERNS = ("unauthorized", "401", "auth", "token expired")


def _is_auth_error(exc: subprocess.CalledProcessError) -> bool:
    """Check if a subprocess error looks like an auth failure."""
    stderr = (exc.stderr or "").lower()
    stdout = (exc.stdout or "").lower()
    combined = stderr + stdout
    return any(pattern in combined for pattern in _AUTH_ERROR_PATTERNS)


# ═══════════════════════════════════════════════════════════════════
# Namespace classes (SPEC §2.2)
# ═══════════════════════════════════════════════════════════════════


class _CompletionsNamespace:
    """Implements ``adapter.chat.completions.create(...)``."""

    def __init__(self, adapter: CLIInstructorAdapter) -> None:
        self._adapter = adapter

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
        """Dispatch an LLM call to a CLI backend (SPEC §2.3, §3, §4)."""
        adapter = self._adapter
        backend = _resolve_backend(model, adapter._default_backend)
        timeout_seconds: int = kwargs.get("timeout", 600)

        # Ensure CLI tool is available (cached per backend)
        if backend not in adapter._tool_checked:
            _check_tool_available(backend)
            adapter._tool_checked.add(backend)

        # Extract schema
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)

        # Build system and user prompts from messages
        system_parts: list[str] = []
        user_parts: list[str] = []
        for msg in messages:
            if msg.get("role") == "system":
                system_parts.append(msg.get("content", ""))
            else:
                user_parts.append(msg.get("content", ""))

        original_system = "\n\n".join(system_parts)
        original_user = "\n\n".join(user_parts)

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

        # Current user prompt (may be augmented on retry)
        current_user = original_user

        # OAuth token (for claude backend, loaded lazily)
        oauth_token: str | None = None

        last_raw: str = ""

        for attempt in range(max_retries + 1):
            # ── Fire pre-hook ──────────────────────────────────
            hook_payload = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "messages": messages,
                "backend": f"cli:{backend}",
            }
            adapter._fire_hooks("completion:kwargs", **hook_payload)

            t0 = time.monotonic()
            raw_output = ""

            try:
                # ── Invoke subprocess per backend ──────────────
                raw_output = self._invoke_backend(
                    backend=backend,
                    system_prompt=system_with_schema,
                    user_prompt=current_user,
                    schema=schema,
                    response_model=response_model,
                    model=model,
                    timeout_seconds=timeout_seconds,
                    oauth_token=oauth_token,
                )

                # ── Extract and parse JSON ─────────────────────
                json_data = extract_json(raw_output)

                # ── Validate with Pydantic ─────────────────────
                result = response_model.model_validate(json_data)

                # ── Fire response hook ─────────────────────────
                latency = time.monotonic() - t0
                cli_response = CLIResponse(
                    model=model,
                    usage=_CLIUsage(),
                    choices=[
                        _CLIChoice(
                            finish_reason="stop",
                            message=_CLIMessage(content=raw_output),
                        )
                    ],
                    backend=f"cli:{backend}",
                    latency_seconds=round(latency, 3),
                )
                adapter._fire_hooks("completion:response", cli_response)

                return result

            except json.JSONDecodeError as e:
                last_raw = raw_output
                logger.warning(
                    "Attempt %d/%d: JSON parse error: %s",
                    attempt + 1,
                    max_retries + 1,
                    e,
                )
                if attempt < max_retries:
                    current_user = (
                        f"{original_user}\n\n"
                        "PREVIOUS ATTEMPT PRODUCED INVALID JSON. "
                        "Your previous output was:\n"
                        f"{raw_output[:500]}\n\n"
                        f"Error: {e}\n\n"
                        "Output ONLY valid JSON. No markdown, no "
                        "explanation, no code fences."
                    )
                else:
                    adapter._fire_hooks("completion:error", e)
                    raise CLIBackendError(
                        f"JSON parse failed after {max_retries + 1} "
                        f"attempts: {e}",
                        backend=backend,
                    ) from e

            except ValidationError as e:
                last_raw = raw_output
                logger.warning(
                    "Attempt %d/%d: validation error: %s",
                    attempt + 1,
                    max_retries + 1,
                    str(e)[:200],
                )
                if attempt < max_retries:
                    error_details = "\n".join(
                        f"- Field '{'.'.join(str(loc) for loc in err['loc'])}': "
                        f"{err['msg']} (type={err['type']})"
                        for err in e.errors()
                    )
                    current_user = (
                        f"{original_user}\n\n"
                        "PREVIOUS ATTEMPT FAILED VALIDATION. "
                        "Your previous output was:\n"
                        f"{last_raw}\n\n"
                        "The following validation errors occurred:\n"
                        f"{error_details}\n\n"
                        "Fix ALL of the above issues and output valid "
                        "JSON matching the schema."
                    )
                else:
                    adapter._fire_hooks("completion:error", e)
                    raise

            except subprocess.TimeoutExpired as e:
                logger.warning(
                    "Attempt %d/%d: subprocess timeout",
                    attempt + 1,
                    max_retries + 1,
                )
                if attempt < max_retries:
                    time.sleep(2**attempt)
                else:
                    adapter._fire_hooks("completion:error", e)
                    raise CLIBackendError(
                        f"Subprocess timeout after {max_retries + 1} "
                        "attempts",
                        backend=backend,
                    ) from e

            except subprocess.CalledProcessError as e:
                logger.warning(
                    "Attempt %d/%d: subprocess error (exit %d)",
                    attempt + 1,
                    max_retries + 1,
                    e.returncode,
                )
                if attempt < max_retries:
                    if _is_auth_error(e) and backend == "claude":
                        logger.info("Auth error detected — refreshing token")
                        try:
                            oauth_token = _get_oauth_token()
                        except CLIBackendError:
                            pass
                    time.sleep(2**attempt)
                else:
                    adapter._fire_hooks("completion:error", e)
                    raise CLIBackendError(
                        f"Subprocess failed (exit {e.returncode}) after "
                        f"{max_retries + 1} attempts: {e.stderr}",
                        backend=backend,
                        exit_code=e.returncode,
                    ) from e

            except CLIBackendError as e:
                logger.warning(
                    "Attempt %d/%d: CLI backend error: %s",
                    attempt + 1,
                    max_retries + 1,
                    e,
                )
                if attempt < max_retries:
                    time.sleep(2**attempt)
                else:
                    adapter._fire_hooks("completion:error", e)
                    raise

        # Should not reach here, but satisfy type checker
        raise CLIBackendError(  # pragma: no cover
            "Retry loop exited unexpectedly",
            backend=backend,
        )

    def _invoke_backend(
        self,
        *,
        backend: str,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        response_model: type[BaseModel],
        model: str,
        timeout_seconds: int,
        oauth_token: str | None,
    ) -> str:
        """Run the appropriate CLI subprocess and return raw output."""
        if backend == "claude":
            return self._invoke_claude(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model,
                timeout_seconds=timeout_seconds,
                oauth_token=oauth_token,
            )
        elif backend == "codex":
            return self._invoke_codex(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
                response_model=response_model,
                timeout_seconds=timeout_seconds,
            )
        elif backend == "gemini":
            return self._invoke_gemini(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                timeout_seconds=timeout_seconds,
            )
        else:
            raise CLIBackendError(
                f"Unknown backend: {backend}",
                backend=backend,
            )

    def _invoke_claude(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        timeout_seconds: int,
        oauth_token: str | None,
    ) -> str:
        """Invoke claude CLI (SPEC §3.2)."""
        if oauth_token is None:
            oauth_token = _get_oauth_token()

        cmd = [
            "claude",
            "-p", "-",
            "--bare",
            "--no-session-persistence",
            "--max-turns", "10",
            "--output-format", "text",
            "--model", "opus",
            "--system-prompt", system_prompt,
        ]

        logger.info("Claude CLI: model=%s", model)

        env = {**os.environ, "ANTHROPIC_API_KEY": oauth_token}
        result = subprocess.run(
            cmd,
            input=user_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_seconds,
            env=env,
            check=True,
        )

        raw_stdout = result.stdout
        logger.debug("Claude raw stdout: %s", raw_stdout[:200])

        # With --output-format text, raw stdout IS the model text.
        # Try envelope extraction for backwards compat with json format,
        # but raw text is the expected case.
        return _extract_claude_result(raw_stdout)

    def _invoke_codex(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        response_model: type[BaseModel],
        timeout_seconds: int,
    ) -> str:
        """Invoke codex CLI (SPEC §3.3).

        Schema is embedded in the prompt (same as Claude/Gemini) rather than
        using --output-schema, which triggers a fatal MCP transport error
        on Windows when Codex has third-party MCP servers configured.
        """
        combined_prompt = (
            f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            f"USER INPUT:\n{user_prompt}"
        )

        codex_bin = shutil.which("codex") or "codex"
        cmd = [
            codex_bin,
            "exec", "-",
            "-s", "read-only",
        ]

        logger.info("Codex CLI: prompt via stdin")

        result = subprocess.run(
            cmd,
            input=combined_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_seconds,
            check=True,
        )

        logger.debug("Codex raw stdout: %s", result.stdout[:200])
        return result.stdout

    def _invoke_gemini(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        timeout_seconds: int,
    ) -> str:
        """Invoke gemini CLI (SPEC §3.4)."""
        combined_prompt = (
            f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            f"USER INPUT:\n{user_prompt}"
        )

        gemini_bin = shutil.which("gemini") or "gemini"
        cmd = [
            gemini_bin,
            "-p", "",
            "-y",
            "--output-format", "text",
        ]

        logger.info("Gemini CLI")

        result = subprocess.run(
            cmd,
            input=combined_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_seconds,
            check=True,
        )

        logger.debug("Gemini stdout: %s", result.stdout[:200])
        return result.stdout


class _ChatNamespace:
    """Implements ``adapter.chat.completions``."""

    def __init__(self, completions: _CompletionsNamespace) -> None:
        self.completions = completions


# ═══════════════════════════════════════════════════════════════════
# Main adapter class (SPEC §2.1)
# ═══════════════════════════════════════════════════════════════════


class CLIInstructorAdapter:
    """Drop-in replacement for instructor.Instructor using CLI backends."""

    def __init__(self, default_backend: str = "claude") -> None:
        self._default_backend = default_backend
        self._hooks: dict[str, list[Callable[..., Any]]] = {}
        self._tool_checked: set[str] = set()

        completions = _CompletionsNamespace(self)
        self.chat = _ChatNamespace(completions)

    def on(self, event: str, callback: Callable[..., Any]) -> None:
        """Register a callback for a lifecycle event (SPEC §2.4)."""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    def _fire_hooks(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Call all registered callbacks for an event."""
        for callback in self._hooks.get(event, []):
            try:
                if args:
                    callback(args[0])
                else:
                    callback(**kwargs)
            except Exception:
                logger.exception("Hook %s raised an exception", event)
