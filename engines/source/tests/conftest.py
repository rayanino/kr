"""Pytest fixtures for source engine tests."""

import shutil
import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"


@pytest.fixture
def tmp_library(tmp_path):
    """Create a temporary library directory structure."""
    lib = tmp_path / "library"
    (lib / "registries").mkdir(parents=True)
    (lib / "staging").mkdir(parents=True)
    (lib / "sources").mkdir(parents=True)
    return lib


@pytest.fixture
def waraqat_pdf():
    """Path to the Waraqat PDF fixture."""
    path = FIXTURES_DIR / "waraqat_usul" / "waraqat.pdf"
    assert path.exists(), f"Fixture not found: {path}"
    return path


@pytest.fixture
def alfiyyah_txt():
    """Path to the Alfiyyah plain text fixture."""
    path = FIXTURES_DIR / "alfiyyah_versified" / "alfiyyah.txt"
    assert path.exists(), f"Fixture not found: {path}"
    return path


@pytest.fixture
def photo_scan_dir():
    """Path to the photo scan fixture directory."""
    path = FIXTURES_DIR / "photo_scan_ilm"
    assert path.exists(), f"Fixture not found: {path}"
    return path


@pytest.fixture
def owner_note_txt():
    """Path to the owner note fixture."""
    path = FIXTURES_DIR / "owner_note" / "study_note.txt"
    assert path.exists(), f"Fixture not found: {path}"
    return path
