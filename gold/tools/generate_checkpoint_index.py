#!/usr/bin/env python3
"""CLI for generating deterministic checkpoint_outputs/index.txt.

Usage:
  python tools/generate_checkpoint_index.py --baseline-dir <baseline_dir>
"""

from __future__ import annotations

import sys
from pathlib import Path
_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
import _paths  # noqa: F401 — registers all engine/shared src dirs

import argparse
import os
import sys

from checkpoint_index_lib import write_index_file, INDEX_REL_PATH


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-dir", required=True, help="Path to a baseline package directory")
    args = ap.parse_args()
    bd = os.path.abspath(args.baseline_dir)
    st = os.path.join(bd, "checkpoint_state.json")
    if not os.path.exists(st):
        print(f"ERROR: Missing checkpoint_state.json in baseline_dir: {bd}")
        sys.exit(2)
    txt = write_index_file(bd)
    print(f"WROTE: {os.path.join(bd, INDEX_REL_PATH)} ({len(txt.splitlines())} lines)")
    sys.exit(0)


if __name__ == "__main__":
    main()
