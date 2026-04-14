from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = PROJECT_ROOT / "engines" / "source"
VALIDATE_SCRIPT = ENGINE_ROOT / "scripts" / "validate_spec.py"
INDEX_PATH = ENGINE_ROOT / "spec" / "INDEX.yaml"


def test_validate_spec_succeeds_for_source_spec_tree() -> None:
    index_data = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8"))
    expected_atom_count = len(index_data["atoms"])

    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert f"Total atoms: {expected_atom_count}" in output
    assert "Validation errors: 0" in output
