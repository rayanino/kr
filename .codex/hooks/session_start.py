#!/usr/bin/env python3
from __future__ import annotations

from hook_utils import active_authority_state, emit_json, load_event, repo_root


def main() -> int:
    event = load_event()
    root = repo_root(event)
    authority = active_authority_state(root)
    active = authority.get("active_authority", "unknown")
    runtime_mode = authority.get("runtime_mode", "unknown")

    context = (
        "KR session start. Read in order: ACTIVE_AUTHORITY.md, CLAUDE.md, "
        "docs/codex/operating-model.md, .kr/ACTIVE.md, .kr/HANDOFF.md, relevant engine CLAUDE.md. "
        f"Current lane: active_authority={active}, runtime_mode={runtime_mode}. "
        "When authority stays claude, Codex is limited to setup, runtime, and read-only shadow work. "
        "Protected areas remain off-limits: .claude/, CLAUDE.md, NEXT.md, docs/superpowers/. "
        "Prefer the WSL clone at /home/rayane/kr-codex for hooks, MCP, quality-gate runs, and unattended execution; "
        "treat the Windows checkout as the secondary interactive lane."
    )

    emit_json(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
