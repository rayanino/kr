from __future__ import annotations

from pathlib import Path

import pytest

from engines.source.src.pipeline import SourcePipeline


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_ROOT = PROJECT_ROOT / "tests" / "fixtures"


@pytest.fixture
def source_pipeline(tmp_path: Path) -> SourcePipeline:
    return SourcePipeline(workspace_root=tmp_path / "source_workspace")
