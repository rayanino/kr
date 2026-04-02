#!/usr/bin/env python3
from __future__ import annotations

from hook_utils import changed_paths, emit_json, infer_quality_gate_mode, load_event, needs_setup_audit, repo_root


def main() -> int:
    event = load_event()
    root = repo_root(event)
    paths = changed_paths(root)
    if not paths:
        return 0

    messages: list[str] = []
    mode = infer_quality_gate_mode(paths)
    if mode:
        joined = " ".join(paths)
        messages.append(f'Run before finishing: make quality-gate MODE={mode} PATHS="{joined}"')

    if needs_setup_audit(paths):
        messages.append("Codex setup changes detected. Run: python scripts/check_codex_kr_setup.py")

    if messages:
        emit_json({"systemMessage": " ".join(messages)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
