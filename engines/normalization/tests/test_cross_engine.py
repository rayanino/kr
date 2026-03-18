"""Cross-engine contract consistency — runs automatically with pytest.

SESSION 3 FAILURE: normalization changed heading_level from ge=1 to ge=0,
passaging's DivisionPathEntry still had ge=1 → runtime crash on multi-volume
books. This test catches that class of bug automatically. No human needs to
remember to run a separate tool.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "tools" / "check_cross_engine_contracts.py"


@pytest.mark.skipif(
    not CHECKER.exists(),
    reason="tools/check_cross_engine_contracts.py not found",
)
def test_cross_engine_contract_consistency():
    """All shared field constraints must be consistent across engines.

    This catches the Session 3 bug class: one engine changes a field constraint
    but downstream engines still have the old constraint → runtime Pydantic crash.
    """
    result = subprocess.run(
        [sys.executable, str(CHECKER)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"Cross-engine contract mismatch:\n{result.stdout}\n{result.stderr}"
    )
