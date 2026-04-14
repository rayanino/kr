from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = PROJECT_ROOT / "engines" / "source"
GENERATE_SCRIPT = ENGINE_ROOT / "scripts" / "generate_views.py"
VIEWS_ROOT = ENGINE_ROOT / "spec" / "views"


def test_generate_views_populates_markdown_outputs() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATE_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert (VIEWS_ROOT / "README.md").exists()
    assert (VIEWS_ROOT / "by-topic" / "acquisition.md").exists()
    assert (VIEWS_ROOT / "by-status" / "proposed.md").exists()
    assert (VIEWS_ROOT / "by-layer" / "pipeline.md").exists()
    assert (VIEWS_ROOT / "by-step" / "upload_receipt.md").exists()

    overview = (VIEWS_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Source Spec Atom Overview" in overview
    assert "REQ-SRC-0001" in overview
    assert "Layer" in overview
