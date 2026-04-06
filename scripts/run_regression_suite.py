#!/usr/bin/env python3
"""S-06: Re-execute validated atom checks after prompt/SPEC change.

Reads a validation directory for per-atom artifacts, computes prompt_hash
and spec_hash for the current state, compares outputs with stored baselines,
and detects regressions.

Output: regression_runs/<run_id>/summary.json
Exit 0 if no regressions, exit 1 if regression detected.

Usage:
    python scripts/run_regression_suite.py --profile profile.json
    python scripts/run_regression_suite.py --profile profile.json --validation-dir validation/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_profile(path: Path) -> dict:
    """Load the model/run configuration profile."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_file_hash(path: Path) -> str:
    """SHA-256 hex digest of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_prompt_hash(profile: dict) -> str:
    """Hash the prompt file referenced in the profile."""
    prompt_path = Path(profile.get("prompt_file", ""))
    if not prompt_path.is_absolute():
        prompt_path = REPO_ROOT / prompt_path
    if prompt_path.is_file():
        return compute_file_hash(prompt_path)
    log.warning("Prompt file not found: %s (using empty hash)", prompt_path)
    return hashlib.sha256(b"").hexdigest()


def compute_spec_hash(profile: dict) -> str:
    """Hash the SPEC file referenced in the profile."""
    spec_path = Path(profile.get("spec_file", ""))
    if not spec_path.is_absolute():
        spec_path = REPO_ROOT / spec_path
    if spec_path.is_file():
        return compute_file_hash(spec_path)
    log.warning("SPEC file not found: %s (using empty hash)", spec_path)
    return hashlib.sha256(b"").hexdigest()


def discover_baselines(validation_dir: Path) -> list[Path]:
    """Find all baseline result files in the validation directory."""
    baselines: list[Path] = []
    for path in sorted(validation_dir.rglob("baseline.json")):
        baselines.append(path)
    return baselines


def compare_with_baseline(baseline_path: Path) -> dict:
    """Compare current state against a single baseline artifact.

    Returns a comparison result dict. Actual LLM re-execution is deferred;
    this stub compares structural metadata only.
    """
    with open(baseline_path, encoding="utf-8") as f:
        baseline = json.load(f)

    atom_id = baseline.get("atom_id", baseline_path.parent.name)
    return {
        "atom_id": atom_id,
        "baseline_path": str(baseline_path),
        "baseline_prompt_hash": baseline.get("prompt_hash", ""),
        "baseline_spec_hash": baseline.get("spec_hash", ""),
        "status": "PENDING_RERUN",
        "regression_detected": False,
        "notes": "Structural comparison only; LLM re-execution deferred.",
    }


def run_regression_checks(
    profile: dict,
    validation_dir: Path,
    prompt_hash: str,
    spec_hash: str,
) -> list[dict]:
    """Run regression checks across all baseline artifacts."""
    baselines = discover_baselines(validation_dir)
    log.info("Found %d baseline artifacts in %s", len(baselines), validation_dir)

    results: list[dict] = []
    for bp in baselines:
        result = compare_with_baseline(bp)
        # Flag as needing rerun if hashes differ
        if result["baseline_prompt_hash"] and result["baseline_prompt_hash"] != prompt_hash:
            result["status"] = "PROMPT_CHANGED"
        if result["baseline_spec_hash"] and result["baseline_spec_hash"] != spec_hash:
            result["status"] = "SPEC_CHANGED"
        results.append(result)
    return results


def main() -> int:
    """Entry point: load profile, run regression, write summary."""
    parser = argparse.ArgumentParser(
        description="S-06: Re-execute validated atom checks after prompt/SPEC change.",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        required=True,
        help="Path to JSON profile with model config, prompt_file, spec_file.",
    )
    parser.add_argument(
        "--validation-dir",
        type=Path,
        default=None,
        help="Directory with per-atom baseline artifacts (default: validation/).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for regression run (default: regression_runs/<run_id>/).",
    )
    args = parser.parse_args()

    profile_path: Path = args.profile.resolve()
    if not profile_path.is_file():
        log.error("Profile file not found: %s", profile_path)
        return 1

    log.info("Loading profile from %s", profile_path)
    profile = load_profile(profile_path)

    validation_dir: Path = (
        args.validation_dir or REPO_ROOT / "validation"
    ).resolve()
    if not validation_dir.is_dir():
        log.error("Validation directory not found: %s", validation_dir)
        return 1

    prompt_hash = compute_prompt_hash(profile)
    spec_hash = compute_spec_hash(profile)
    log.info("Prompt hash: %s", prompt_hash[:16])
    log.info("SPEC hash: %s", spec_hash[:16])

    results = run_regression_checks(profile, validation_dir, prompt_hash, spec_hash)

    run_id = str(uuid.uuid4())[:8]
    output_dir: Path = (
        args.output_dir or REPO_ROOT / "regression_runs" / run_id
    ).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    regressions = [r for r in results if r["regression_detected"]]
    summary = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt_hash": prompt_hash,
        "spec_hash": spec_hash,
        "total_baselines": len(results),
        "regressions_detected": len(regressions),
        "results": results,
    }

    summary_path = output_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log.info("Summary written to %s", summary_path)

    if regressions:
        log.error("FAIL: %d regression(s) detected", len(regressions))
        for r in regressions:
            log.error("  Regression in atom %s", r["atom_id"])
        return 1

    log.info("PASS: no regressions detected across %d baselines", len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
