"""Tests for the recursive-improve trace bridge.

Verifies that CLIInstructorAdapter hook events are correctly
translated into ri Session messages.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from shared.llm.ri_trace_bridge import TraceBridge, attach


# ═══════════════════════════════════════════════════════════════════
# Minimal stubs — avoid importing real CLIResponse/Session in unit tests
# ═══════════════════════════════════════════════════════════════════


@dataclass
class _StubUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass
class _StubMessage:
    content: str | None = None


@dataclass
class _StubChoice:
    finish_reason: str = "stop"
    message: _StubMessage = field(default_factory=_StubMessage)


@dataclass
class _StubCLIResponse:
    model: str = ""
    usage: _StubUsage = field(default_factory=_StubUsage)
    choices: list[_StubChoice] = field(default_factory=lambda: [_StubChoice()])
    backend: str = ""
    latency_seconds: float = 0.0


class _StubSession:
    """Minimal ri.Session stub that collects messages."""

    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []

    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        msg = {"role": role, "content": content, **kwargs}
        self.messages.append(msg)


class _StubAdapter:
    """Minimal CLIInstructorAdapter stub with hook system."""

    def __init__(self) -> None:
        self._hooks: dict[str, list[Any]] = {}

    def on(self, event: str, callback: Any) -> None:
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    def fire(self, event: str, *args: Any, **kwargs: Any) -> None:
        for cb in self._hooks.get(event, []):
            if args:
                cb(args[0])
            else:
                cb(**kwargs)


# ═══════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════


class TestTraceBridgeAttach:
    """Test that attach() wires all three hooks."""

    def test_attach_registers_three_hooks(self) -> None:
        adapter = _StubAdapter()
        session = _StubSession()
        bridge = attach(adapter, session)  # type: ignore[arg-type]

        assert len(adapter._hooks.get("completion:kwargs", [])) == 1
        assert len(adapter._hooks.get("completion:response", [])) == 1
        assert len(adapter._hooks.get("completion:error", [])) == 1
        assert isinstance(bridge, TraceBridge)


class TestOnKwargs:
    """Test completion:kwargs handler."""

    def test_records_system_and_user_messages(self) -> None:
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        bridge.on_kwargs(
            model="anthropic/claude-opus-4-6",
            temperature=0.0,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": "You are a JSON API."},
                {"role": "user", "content": "Classify this text."},
            ],
            backend="cli:claude",
        )

        assert len(session.messages) == 2
        assert session.messages[0]["role"] == "system"
        assert session.messages[0]["content"] == "You are a JSON API."
        assert session.messages[1]["role"] == "user"
        assert session.messages[1]["content"] == "Classify this text."

    def test_deduplicates_system_messages_across_retries(self) -> None:
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        system = "You are a JSON API. OUTPUT FORMAT: ..."
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": "Attempt 1"},
        ]
        bridge.on_kwargs(
            model="m", temperature=0, max_tokens=4096,
            messages=messages, backend="cli:claude",
        )

        # Retry with augmented user prompt but same system
        messages_retry = [
            {"role": "system", "content": system},
            {"role": "user", "content": "Attempt 2 (with error feedback)"},
        ]
        bridge.on_kwargs(
            model="m", temperature=0, max_tokens=4096,
            messages=messages_retry, backend="cli:claude",
        )

        # System recorded once, user recorded twice
        system_msgs = [m for m in session.messages if m["role"] == "system"]
        user_msgs = [m for m in session.messages if m["role"] == "user"]
        assert len(system_msgs) == 1
        assert len(user_msgs) == 2

    def test_arabic_content_preserved(self) -> None:
        """Arabic scholarly text must pass through without corruption."""
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        arabic_text = (
            "بسم الله الرحمن الرحيم\n"
            "قال الإمام ابن قدامة رحمه الله في المغني:\n"
            "كتاب الطهارة — باب المياه"
        )
        bridge.on_kwargs(
            model="m", temperature=0, max_tokens=4096,
            messages=[{"role": "user", "content": arabic_text}],
            backend="cli:claude",
        )

        assert session.messages[0]["content"] == arabic_text

    def test_arabic_with_diacritics_preserved(self) -> None:
        """Diacritics (tashkeel) must survive trace recording."""
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        diacritized = "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"
        bridge.on_kwargs(
            model="m", temperature=0, max_tokens=4096,
            messages=[{"role": "user", "content": diacritized}],
            backend="cli:claude",
        )

        assert session.messages[0]["content"] == diacritized


class TestOnResponse:
    """Test completion:response handler."""

    def test_records_assistant_message_with_metadata(self) -> None:
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        response = _StubCLIResponse(
            model="anthropic/claude-opus-4-6",
            usage=_StubUsage(
                prompt_tokens=1200,
                completion_tokens=350,
                total_tokens=1550,
            ),
            choices=[_StubChoice(message=_StubMessage(content='{"genre": "sharh"}'))],
            backend="cli:claude",
            latency_seconds=4.5,
        )
        bridge.on_response(response)  # type: ignore[arg-type]

        assert len(session.messages) == 1
        msg = session.messages[0]
        assert msg["role"] == "assistant"
        assert msg["content"] == '{"genre": "sharh"}'
        assert msg["model"] == "anthropic/claude-opus-4-6"
        assert msg["provider"] == "cli:claude"
        assert msg["latency_s"] == 4.5
        assert msg["usage"]["prompt_tokens"] == 1200
        assert msg["usage"]["completion_tokens"] == 350
        assert msg["usage"]["total_tokens"] == 1550

    def test_omits_usage_when_tokens_are_none(self) -> None:
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        response = _StubCLIResponse(
            model="gemini",
            choices=[_StubChoice(message=_StubMessage(content="{}"))],
            backend="cli:gemini",
            latency_seconds=2.0,
        )
        bridge.on_response(response)  # type: ignore[arg-type]

        msg = session.messages[0]
        assert "usage" not in msg

    def test_handles_empty_choices(self) -> None:
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        response = _StubCLIResponse(choices=[], backend="cli:claude")
        bridge.on_response(response)  # type: ignore[arg-type]

        assert session.messages[0]["content"] == ""

    def test_arabic_response_preserved(self) -> None:
        """Arabic JSON response content must not be corrupted."""
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        arabic_json = json.dumps(
            {"author": "ابن قدامة المقدسي", "death_hijri": 620},
            ensure_ascii=False,
        )
        response = _StubCLIResponse(
            model="m",
            choices=[_StubChoice(message=_StubMessage(content=arabic_json))],
            backend="cli:claude",
        )
        bridge.on_response(response)  # type: ignore[arg-type]

        parsed = json.loads(session.messages[0]["content"])
        assert parsed["author"] == "ابن قدامة المقدسي"
        assert parsed["death_hijri"] == 620


class TestOnError:
    """Test completion:error handler."""

    def test_records_error_as_system_message(self) -> None:
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        error = json.JSONDecodeError("Expecting value", "doc", 0)
        bridge.on_error(error)

        assert len(session.messages) == 1
        msg = session.messages[0]
        assert msg["role"] == "system"
        assert "JSONDecodeError" in msg["content"]
        assert msg["error"] is True
        assert msg["error_type"] == "JSONDecodeError"

    def test_records_timeout_error(self) -> None:
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        import subprocess
        error = subprocess.TimeoutExpired(cmd="claude", timeout=120)
        bridge.on_error(error)

        msg = session.messages[0]
        assert "TimeoutExpired" in msg["content"]
        assert msg["error_type"] == "TimeoutExpired"


class TestEndToEndFlow:
    """Test full kwargs→response flow via adapter hooks."""

    def test_full_call_produces_input_and_output_messages(self) -> None:
        adapter = _StubAdapter()
        session = _StubSession()
        attach(adapter, session)  # type: ignore[arg-type]

        # Simulate: adapter fires kwargs, then response
        adapter.fire(
            "completion:kwargs",
            model="anthropic/claude-opus-4-6",
            temperature=0.0,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": "You are a JSON API."},
                {"role": "user", "content": "What is the genre?"},
            ],
            backend="cli:claude",
        )
        adapter.fire(
            "completion:response",
            _StubCLIResponse(
                model="anthropic/claude-opus-4-6",
                choices=[_StubChoice(message=_StubMessage(content='{"genre": "matn"}'))],
                backend="cli:claude",
                latency_seconds=3.2,
            ),
        )

        assert len(session.messages) == 3
        assert session.messages[0]["role"] == "system"
        assert session.messages[1]["role"] == "user"
        assert session.messages[2]["role"] == "assistant"
        assert session.messages[2]["model"] == "anthropic/claude-opus-4-6"

    def test_retry_flow_with_error_then_success(self) -> None:
        """Simulates a retry: kwargs→error→kwargs(augmented)→response."""
        adapter = _StubAdapter()
        session = _StubSession()
        attach(adapter, session)  # type: ignore[arg-type]

        system = "You are a JSON API."

        # Attempt 1
        adapter.fire(
            "completion:kwargs",
            model="m", temperature=0, max_tokens=4096,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": "Classify."},
            ],
            backend="cli:claude",
        )
        adapter.fire(
            "completion:error",
            json.JSONDecodeError("bad", "doc", 0),
        )

        # Attempt 2 (augmented user prompt)
        adapter.fire(
            "completion:kwargs",
            model="m", temperature=0, max_tokens=4096,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": "Classify. PREVIOUS ATTEMPT PRODUCED INVALID JSON..."},
            ],
            backend="cli:claude",
        )
        adapter.fire(
            "completion:response",
            _StubCLIResponse(
                model="m",
                choices=[_StubChoice(message=_StubMessage(content='{"ok": true}'))],
                backend="cli:claude",
            ),
        )

        # system(1) + user(1) + error(1) + user(2) + assistant(1) = 5
        # system is deduplicated so only 1
        assert len(session.messages) == 5
        roles = [m["role"] for m in session.messages]
        assert roles == ["system", "user", "system", "user", "assistant"]
        # The second "system" is the error message
        assert session.messages[2]["error"] is True

    def test_trace_json_serializable(self) -> None:
        """All messages must be JSON-serializable (ri writes JSON traces)."""
        session = _StubSession()
        bridge = TraceBridge(session)  # type: ignore[arg-type]

        bridge.on_kwargs(
            model="m", temperature=0, max_tokens=4096,
            messages=[{"role": "user", "content": "الحمد لله"}],
            backend="cli:claude",
        )
        bridge.on_response(
            _StubCLIResponse(  # type: ignore[arg-type]
                model="m",
                usage=_StubUsage(100, 50, 150),
                choices=[_StubChoice(message=_StubMessage(content='{"x": 1}'))],
                backend="cli:claude",
                latency_seconds=1.5,
            ),
        )

        serialized = json.dumps(session.messages, ensure_ascii=False)
        roundtripped = json.loads(serialized)
        assert roundtripped[0]["content"] == "الحمد لله"
        assert roundtripped[1]["usage"]["total_tokens"] == 150
