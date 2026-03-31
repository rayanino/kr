"""Shared Codex and Claude quality gate for KR changes.

This script centralizes the post-change checks that were previously encoded
mainly in Claude hooks and overnight runtime logic.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


PROJECT_DIR = Path(__file__).resolve().parent.parent
PIPELINE_ORDER = ["source", "normalization", "passaging", "atomization", "excerpting", "taxonomy", "synthesis"]
INTEGRATION_TRIGGER_PREFIXES = (
    "scripts/run_integration_test.py",
    "scripts/run_full_integration.py",
    "shared/llm/",
    "tools/check_cross_engine_contracts.py",
)


def repo_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_DIR.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def normalize_paths(raw_paths: Sequence[str]) -> list[str]:
    paths: list[str] = []
    for raw in raw_paths:
        if not raw:
            continue
        path = Path(raw)
        if not path.is_absolute():
            path = PROJECT_DIR / path
        normalized = repo_rel(path)
        if normalized not in paths:
            paths.append(normalized)
    return paths


def infer_engines(paths: Sequence[str], explicit: Sequence[str]) -> list[str]:
    engines: set[str] = {engine for engine in explicit if (PROJECT_DIR / "engines" / engine).exists()}
    for path in paths:
        parts = path.split("/")
        if len(parts) >= 3 and parts[0] == "engines":
            engines.add(parts[1])
        elif parts and parts[0] == "shared":
            for engine in PIPELINE_ORDER:
                if (PROJECT_DIR / "engines" / engine / "tests").exists():
                    engines.add(engine)
    return sorted(engines)


def infer_python_paths(paths: Sequence[str]) -> list[str]:
    return [path for path in paths if path.endswith(".py")]


def infer_spec_paths(paths: Sequence[str]) -> list[str]:
    return [path for path in paths if path.endswith("SPEC.md")]


def should_run_arabic(paths: Sequence[str]) -> bool:
    return any(
        path.endswith(".py")
        and any(path.startswith(prefix) for prefix in ("engines/", "shared/"))
        and "/src/" in path
        for path in paths
    )


def should_run_contracts(paths: Sequence[str]) -> bool:
    return any(path.endswith("contracts.py") for path in paths)


def should_run_integration(paths: Sequence[str]) -> bool:
    return any(path.startswith(prefix) for prefix in INTEGRATION_TRIGGER_PREFIXES for path in paths)


def find_bash() -> str | None:
    found = shutil.which("bash")
    if found:
        return found
    candidates = [
        Path("C:/Program Files/Git/bin/bash.exe"),
        Path("C:/Program Files/Git/usr/bin/bash.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def find_pyright() -> list[str] | None:
    module_check = subprocess.run(
        [sys.executable, "-m", "pyright", "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJECT_DIR),
        check=False,
    )
    if module_check.returncode == 0:
        return [sys.executable, "-m", "pyright"]
    binary = shutil.which("pyright")
    if binary:
        return [binary]
    return None


def run_command(
    label: str,
    cmd: list[str],
    *,
    timeout: int = 600,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> tuple[bool, str]:
    print(f"[quality-gate] {label}")
    print("  $ " + " ".join(cmd))
    merged_env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if env:
        merged_env.update(env)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd or PROJECT_DIR),
        env=merged_env,
        timeout=timeout,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip()[-1200:])
    if result.stderr.strip():
        print(result.stderr.strip()[-1200:])
    return result.returncode == 0, (result.stderr or result.stdout).strip()[-1200:]


def run_hook_script(script_name: str, file_path: str) -> tuple[bool, str]:
    bash = find_bash()
    script_path = PROJECT_DIR / ".claude" / "hooks" / script_name
    if not bash:
        return False, "bash not found for hook execution"
    env = {
        "CLAUDE_PROJECT_DIR": str(PROJECT_DIR),
        "CLAUDE_TOOL_FILE_PATH": str((PROJECT_DIR / file_path).resolve()),
    }
    return run_command(
        f"{script_name} -> {file_path}",
        [bash, str(script_path)],
        timeout=120,
        env=env,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run KR quality gates")
    parser.add_argument(
        "--mode",
        choices=["python", "contracts", "arabic", "spec", "integration", "all"],
        default="all",
        help="Which gate family to run",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=[],
        help="Changed repo-relative paths used to infer required checks",
    )
    parser.add_argument(
        "--engine",
        action="append",
        default=[],
        help="Explicitly include an engine when inferring test scope",
    )
    parser.add_argument(
        "--excerpting-cli-smoke",
        action="store_true",
        help="Run a bounded excerpting CLI smoke after integration checks",
    )
    args = parser.parse_args()

    paths = normalize_paths(args.paths)
    engines = infer_engines(paths, args.engine)
    py_paths = infer_python_paths(paths)
    spec_paths = infer_spec_paths(paths)

    failures: list[str] = []

    run_python = args.mode in {"python", "all"} and bool(py_paths)
    run_contracts = args.mode in {"contracts", "all"} and (
        args.mode == "contracts" or should_run_contracts(paths)
    )
    run_arabic = args.mode in {"arabic", "all"} and (
        args.mode == "arabic" or should_run_arabic(paths)
    )
    run_spec = args.mode in {"spec", "all"} and bool(spec_paths)
    run_integration = args.mode in {"integration", "all"} and (
        args.mode == "integration" or should_run_integration(paths)
    )

    if run_python:
        pre_review = PROJECT_DIR / "scripts" / "pre_review_checks.py"
        if pre_review.exists():
            cmd = [sys.executable, str(pre_review), *py_paths]
            if len(engines) == 1:
                cmd.extend(["--engine", engines[0]])
            ok, output = run_command("pre_review_checks", cmd, timeout=300)
            if not ok:
                failures.append(f"pre_review_checks failed: {output}")

        pyright_cmd = find_pyright()
        if pyright_cmd is None:
            failures.append("pyright not available")
        else:
            ok, output = run_command("pyright", [*pyright_cmd, *py_paths], timeout=300)
            if not ok:
                failures.append(f"pyright failed: {output}")

        for engine in engines:
            test_dir = PROJECT_DIR / "engines" / engine / "tests"
            if not test_dir.exists():
                continue
            ok, output = run_command(
                f"pytest {engine}",
                [sys.executable, "-m", "pytest", f"engines/{engine}/tests/", "-x", "-q", "--tb=short"],
                timeout=1800,
            )
            if not ok:
                failures.append(f"pytest failed for {engine}: {output}")
                break

    if run_contracts:
        metadata_script = PROJECT_DIR / "scripts" / "verify_metadata_flow.py"
        contracts_script = PROJECT_DIR / "tools" / "check_cross_engine_contracts.py"
        if metadata_script.exists():
            ok, output = run_command(
                "verify_metadata_flow",
                [sys.executable, str(metadata_script)],
                timeout=600,
            )
            if not ok:
                failures.append(f"verify_metadata_flow failed: {output}")
        if contracts_script.exists():
            ok, output = run_command(
                "check_cross_engine_contracts",
                [sys.executable, str(contracts_script)],
                timeout=600,
            )
            if not ok:
                failures.append(f"check_cross_engine_contracts failed: {output}")

    if run_arabic:
        for file_path in paths:
            if not (
                file_path.endswith(".py")
                and any(file_path.startswith(prefix) for prefix in ("engines/", "shared/"))
                and "/src/" in file_path
            ):
                continue
            ok, output = run_hook_script("arabic-safety-check.sh", file_path)
            if not ok:
                failures.append(f"arabic safety check failed for {file_path}: {output}")
                break
            ok, output = run_hook_script("diacritic-preservation.sh", file_path)
            if not ok:
                failures.append(f"diacritic preservation check failed for {file_path}: {output}")
                break

    if run_spec:
        checker = PROJECT_DIR / "scripts" / "check_spec_quality.py"
        for spec_path in spec_paths:
            ok, output = run_command(
                f"check_spec_quality {spec_path}",
                [sys.executable, str(checker), spec_path],
                timeout=600,
            )
            if not ok:
                failures.append(f"check_spec_quality failed for {spec_path}: {output}")
                break

    if run_integration:
        contracts_script = PROJECT_DIR / "tools" / "check_cross_engine_contracts.py"
        if contracts_script.exists():
            ok, output = run_command(
                "integration boundary smoke",
                [sys.executable, str(contracts_script)],
                timeout=600,
            )
            if not ok:
                failures.append(f"integration boundary smoke failed: {output}")
        if args.excerpting_cli_smoke:
            ok, output = run_command(
                "excerpting CLI smoke",
                [
                    sys.executable,
                    "scripts/run_full_integration.py",
                    "--backend",
                    "cli",
                    "--max-chunks",
                    "1",
                    "--output-dir",
                    "integration_tests/quality_gate_smoke",
                ],
                timeout=7200,
            )
            if not ok:
                failures.append(f"excerpting CLI smoke failed: {output}")

    if not any((run_python, run_contracts, run_arabic, run_spec, run_integration)):
        print("[quality-gate] Nothing to run for the given mode and paths.")

    if failures:
        print("\nQUALITY GATE FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nQUALITY GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
