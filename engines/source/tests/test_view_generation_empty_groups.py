from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = PROJECT_ROOT / "engines" / "source"
GENERATE_SCRIPT = ENGINE_ROOT / "scripts" / "generate_views.py"
VIEWS_ROOT = ENGINE_ROOT / "spec" / "views"


def test_generate_views_writes_empty_status_and_topic_pages() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATE_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    proposed = VIEWS_ROOT / "by-status" / "proposed.md"

    assert result.returncode == 0, result.stdout + result.stderr
    assert proposed.exists()
    assert "Source Spec Atoms by Status: proposed" in proposed.read_text(encoding="utf-8")
