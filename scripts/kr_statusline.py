#!/usr/bin/env python3
"""KR status line for Claude Code."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys


def main() -> None:
    """Output a single status line for the KR project."""
    # Read stdin JSON from Claude Code
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    ctx_pct = data.get("context_window", {}).get("used_percentage", "?")
    if isinstance(ctx_pct, (int, float)):
        ctx_str = f"{ctx_pct:.0f}% ctx"
    else:
        ctx_str = "? ctx"

    # Active engine from NEXT.md
    engine = "?"
    try:
        first_line = pathlib.Path("NEXT.md").read_text(encoding="utf-8").split("\n")[0]
        # Extract engine name from patterns like "Taxonomy Session" or "# NEXT — Taxonomy"
        for name in [
            "source",
            "normalization",
            "passaging",
            "atomization",
            "excerpting",
            "taxonomy",
            "synthesis",
        ]:
            if name.lower() in first_line.lower():
                engine = name
                break
    except Exception:
        pass

    # Budget from COST_LOG.json
    budget_str = "€?/€100"
    try:
        cost_log = pathlib.Path("tests/results/source_engine/COST_LOG.json")
        if cost_log.exists():
            d = json.loads(cost_log.read_text(encoding="utf-8"))
            total = sum(
                v.get("cost_eur", 0) for v in d.values() if isinstance(v, dict)
            )
            limit = float(os.environ.get("KR_BUDGET_LIMIT", "100"))
            budget_str = f"€{total:.2f}/€{limit:.0f}"
    except Exception:
        pass

    # Git branch
    branch = "?"
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            branch = result.stdout.strip() or "detached"
    except Exception:
        pass

    print(f"[{engine}] {budget_str} | {ctx_str} | {branch}")


if __name__ == "__main__":
    main()
