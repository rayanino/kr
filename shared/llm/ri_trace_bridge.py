"""Trace bridge between KR CLI adapter and recursive-improve.

Hooks into CLIInstructorAdapter's lifecycle events to capture LLM call
traces in ri's expected format.  Since ri.patch() only intercepts Python
SDK calls (openai/anthropic), it cannot see KR's subprocess-based CLI
calls.  This bridge fills that gap by translating CLIResponse objects
into ri session messages.

Usage:
    import recursive_improve as ri
    from shared.llm.ri_trace_bridge import attach

    with ri.session("eval/traces/excerpting") as run:
        bridge = attach(adapter, run)
        # ... pipeline code using adapter ...
        run.finish(output=summary, success=True)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from recursive_improve.capture.session import Session

    from shared.llm.cli_adapter import CLIInstructorAdapter, CLIResponse

logger = logging.getLogger("kr.shared.llm.ri_trace_bridge")


class TraceBridge:
    """Translates CLI adapter hook events into ri session messages.

    Registers as a listener on CLIInstructorAdapter's three lifecycle
    events (completion:kwargs, completion:response, completion:error)
    and writes normalized messages into the active ri Session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session
        self._seen_system_hashes: set[int] = set()

    def on_kwargs(
        self,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        messages: list[dict[str, str]],
        backend: str,
    ) -> None:
        """Handle completion:kwargs — record input messages.

        System messages are deduplicated across retries (same system
        prompt repeated).  User messages are always recorded since
        they may change on retry (augmented with error feedback).
        """
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                h = hash(content[:500])
                if h in self._seen_system_hashes:
                    continue
                self._seen_system_hashes.add(h)

            self._session.add_message(role=role, content=content)

    def on_response(self, cli_response: CLIResponse) -> None:
        """Handle completion:response — record assistant output with metadata."""
        content = ""
        if cli_response.choices:
            content = cli_response.choices[0].message.content or ""

        usage: dict[str, Any] = {}
        if cli_response.usage.prompt_tokens is not None:
            usage["prompt_tokens"] = cli_response.usage.prompt_tokens
        if cli_response.usage.completion_tokens is not None:
            usage["completion_tokens"] = cli_response.usage.completion_tokens
        if cli_response.usage.total_tokens is not None:
            usage["total_tokens"] = cli_response.usage.total_tokens

        self._session.add_message(
            role="assistant",
            content=content,
            model=cli_response.model,
            provider=cli_response.backend,
            latency_s=cli_response.latency_seconds,
            **({"usage": usage} if usage else {}),
        )

    def on_error(self, error: Exception) -> None:
        """Handle completion:error — record error in trace."""
        self._session.add_message(
            role="system",
            content=f"ERROR: {type(error).__name__}: {error}",
            error=True,
            error_type=type(error).__name__,
        )


def attach(adapter: CLIInstructorAdapter, session: Session) -> TraceBridge:
    """Wire a TraceBridge into a CLI adapter, capturing all LLM calls.

    Returns the bridge instance for inspection in tests.
    """
    bridge = TraceBridge(session)
    adapter.on("completion:kwargs", bridge.on_kwargs)
    adapter.on("completion:response", bridge.on_response)
    adapter.on("completion:error", bridge.on_error)
    return bridge
