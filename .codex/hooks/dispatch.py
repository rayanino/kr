#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import logging
import runpy
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def find_repo_root(cwd_value: str | None) -> Path | None:
    start = Path(cwd_value or ".").resolve()
    for candidate in (start, *start.parents):
        hook_utils = candidate / ".codex" / "hooks" / "hook_utils.py"
        if hook_utils.exists():
            return candidate
    return None


def main() -> int:
    if len(sys.argv) != 2:
        LOGGER.error("usage: dispatch.py <hook-script>")
        return 2

    raw = sys.stdin.read()
    try:
        event = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        LOGGER.error("invalid hook event payload: %s", exc)
        return 2

    root = find_repo_root(event.get("cwd"))
    if root is None:
        return 0

    target = root / ".codex" / "hooks" / sys.argv[1]
    if not target.exists():
        LOGGER.error("missing hook target: %s", target)
        return 2

    sys.path.insert(0, str(target.parent))
    sys.stdin = io.StringIO(raw)
    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
