#!/usr/bin/env python3
from __future__ import annotations

from hook_utils import (
    active_authority_state,
    dirty_summary,
    emit_json,
    git_branch,
    hook_enabled,
    load_event,
    repo_root,
)


def main() -> int:
    event = load_event()
    root = repo_root(event)
    if not hook_enabled(root, "disableSessionStartContext"):
        return 0
    authority = active_authority_state(root)
    active = authority.get("active_authority", "unknown")
    runtime_mode = authority.get("runtime_mode", "unknown")
    branch = git_branch(root)
    dirty = dirty_summary(root)

    context = (
        "KR session start on the Windows checkout. Read in order: ACTIVE_AUTHORITY.md, CLAUDE.md, "
        "docs/codex/operating-model.md, .kr/ACTIVE.md, .kr/HANDOFF.md, relevant engine CLAUDE.md. "
        f"Current lane: active_authority={active}, runtime_mode={runtime_mode}, branch={branch}, state={dirty}. "
        "When authority stays claude, Codex is limited to setup, runtime, and read-only shadow work. "
        "Protected areas remain off-limits: .claude/, CLAUDE.md, NEXT.md, docs/superpowers/. "
        "Use `powershell -ExecutionPolicy Bypass -File scripts/start_codex_kr.ps1` as the canonical Windows launcher. "
        "Treat WSL as legacy fallback only if a concrete Windows blocker is proven."
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
