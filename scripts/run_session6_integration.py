"""Session 6 Integration Script — Real LLM calls on all fixtures.

Runs acquire_source on each fixture with live inference, compares
against GROUND_TRUTH.json, saves per-fixture results and summary.

Usage:
    python scripts/run_session6_integration.py [--fixture 03_fiqh] [--dry-run]

Requires: ANTHROPIC_API_KEY, OPENROUTER_API_KEY environment variables.
Hard cost ceiling: $5.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engines.source.contracts import SourceMetadata
from engines.source.src.config import SourceEngineConfig
from engines.source.src.engine import acquire_source
from engines.source.src.exceptions import SourceEngineError


FIXTURES_DIR = Path("tests/fixtures")
RESULTS_DIR = Path("tests/results/source_engine/session6")
GROUND_TRUTH_PATH = FIXTURES_DIR / "GROUND_TRUTH.json"

SHAMELA_FIXTURES = [
    "01_nahw_simple", "02_nahw_muhaqiq", "03_fiqh", "04_hadith",
    "05_tafsir", "06_usul", "07_balagha", "08_death_date",
    "09_alt_title", "10_no_author", "11_multi_small", "12_multi_muq",
]
PLAINTEXT_FIXTURES = ["alfiyyah_versified"]


def check_env() -> None:
    """Verify API keys are set."""
    missing = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not os.environ.get("OPENROUTER_API_KEY"):
        missing.append("OPENROUTER_API_KEY")
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)


def load_ground_truth() -> dict:
    """Load ground truth from GROUND_TRUTH.json."""
    return json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))


def create_temp_library(base_dir: Path) -> SourceEngineConfig:
    """Create an isolated temp library for a single fixture."""
    library_root = base_dir / "library"
    staging = library_root / "staging"
    for d in [staging, library_root / "registries", library_root / "logs",
              library_root / "config", library_root / "gates" / "pending",
              library_root / "gates" / "resolved", library_root / "sources"]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy config files from the real library so trust evaluation,
    # genre synonyms, slug generation, and muhaqiq recognition work correctly
    real_config = Path("library/config")
    if real_config.exists():
        for cfg_file in real_config.iterdir():
            if cfg_file.is_file():
                shutil.copy2(cfg_file, library_root / "config" / cfg_file.name)

    from shared.human_gate.src.human_gate import configure
    configure(gates_dir=library_root / "gates", auto_approve=True)

    from engines.source.src.config import load_config
    return load_config(library_root)


def compare_ground_truth(metadata: SourceMetadata, truth: dict) -> dict:
    """Compare metadata against ground truth."""
    results = {}
    if "genre" in truth:
        results["genre_match"] = metadata.genre.value == truth["genre"]
    if "expected_trust" in truth:
        results["trust_match"] = metadata.trust_tier.value == truth["expected_trust"]
    if "author_name" in truth:
        results["author_match"] = truth["author_name"] in metadata.author.name_arabic
    if "is_multi_layer" in truth:
        results["multi_layer_match"] = metadata.is_multi_layer == truth["is_multi_layer"]
    if "science_scope" in truth:
        results["science_match"] = set(metadata.science_scope) == set(truth["science_scope"])
    return results


async def run_fixture(
    fixture_name: str,
    ground_truth: dict,
    is_shamela: bool = True,
) -> dict:
    """Run a single fixture through acquire_source."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        config = create_temp_library(tmp_path)

        # Copy fixture to staging
        if is_shamela:
            src = FIXTURES_DIR / "shamela_real" / fixture_name
            dst = config.staging_path / fixture_name
            shutil.copytree(src, dst)
        else:
            src = FIXTURES_DIR / fixture_name / next(
                (FIXTURES_DIR / fixture_name).iterdir()
            ).name
            dst = config.staging_path / src.name
            shutil.copy2(src, dst)

        start = time.time()
        result: dict = {"fixture": fixture_name, "success": False}

        try:
            metadata = await acquire_source(dst, config)
            elapsed = time.time() - start
            result["success"] = True
            result["elapsed_seconds"] = round(elapsed, 2)
            result["source_id"] = metadata.source_id
            result["genre"] = metadata.genre.value
            result["trust_tier"] = metadata.trust_tier.value
            result["trust_score"] = round(metadata.trust_score, 3)
            result["author_name"] = metadata.author.name_arabic
            result["author_id"] = metadata.author.canonical_id
            result["is_multi_layer"] = metadata.is_multi_layer
            result["science_scope"] = metadata.science_scope
            result["structural_format"] = metadata.structural_format.value
            result["authority_level"] = metadata.authority_level.value
            result["confidence_scores"] = metadata.confidence_scores.model_dump(mode="json")

            # Compare ground truth
            truth = ground_truth.get(fixture_name, {})
            result["ground_truth"] = compare_ground_truth(metadata, truth)

        except SourceEngineError as exc:
            elapsed = time.time() - start
            result["elapsed_seconds"] = round(elapsed, 2)
            result["error_code"] = exc.error.error_code.value
            result["error_message"] = exc.error.message

        return result


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Session 6 integration test")
    parser.add_argument("--fixture", help="Run only this fixture")
    parser.add_argument("--dry-run", action="store_true", help="Check setup only")
    args = parser.parse_args()

    check_env()
    ground_truth = load_ground_truth()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("Dry run: environment OK, ground truth loaded.")
        print(f"Fixtures: {len(SHAMELA_FIXTURES)} shamela + {len(PLAINTEXT_FIXTURES)} plaintext")
        return

    fixtures_to_run: list[tuple[str, bool]] = []
    if args.fixture:
        is_shamela = args.fixture in SHAMELA_FIXTURES
        fixtures_to_run.append((args.fixture, is_shamela))
    else:
        for f in SHAMELA_FIXTURES:
            fixtures_to_run.append((f, True))
        for f in PLAINTEXT_FIXTURES:
            fixtures_to_run.append((f, False))

    all_results: list[dict] = []
    for fixture_name, is_shamela in fixtures_to_run:
        print(f"\n{'='*60}")
        print(f"Running: {fixture_name}")
        result = await run_fixture(fixture_name, ground_truth, is_shamela)
        all_results.append(result)

        # Save per-fixture result
        out_path = RESULTS_DIR / f"{fixture_name}.json"
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        status = "OK" if result["success"] else f"FAIL: {result.get('error_code', 'unknown')}"
        print(f"  Result: {status} ({result.get('elapsed_seconds', 0)}s)")
        if result["success"] and result.get("ground_truth"):
            for check, passed in result["ground_truth"].items():
                print(f"    {check}: {'PASS' if passed else 'FAIL'}")

    # Summary
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_fixtures": len(all_results),
        "successes": sum(1 for r in all_results if r["success"]),
        "failures": sum(1 for r in all_results if not r["success"]),
        "ground_truth_checks": {},
    }

    for r in all_results:
        for check, passed in r.get("ground_truth", {}).items():
            summary["ground_truth_checks"].setdefault(check, {"pass": 0, "fail": 0})
            summary["ground_truth_checks"][check]["pass" if passed else "fail"] += 1

    summary_path = RESULTS_DIR / "SESSION6_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"SUMMARY: {summary['successes']}/{summary['total_fixtures']} succeeded")
    for check, counts in summary["ground_truth_checks"].items():
        print(f"  {check}: {counts['pass']} pass, {counts['fail']} fail")
    print(f"\nResults saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
