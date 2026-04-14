from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = PROJECT_ROOT / "engines" / "source"
VALIDATE_SCRIPT = ENGINE_ROOT / "scripts" / "validate_spec.py"


def test_validate_spec_succeeds_for_source_spec_tree() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert "Total atoms: 53" in output
    assert "Validation errors: 0" in output

