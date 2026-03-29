"""Run readonly Codex tasks in parallel while guarded-write tasks use the orchestrator."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

try:
    from scripts.overnight_codex_common import (
        OVERNIGHT_CODEX_DIR,
        PROJECT_DIR,
        RESULTS_DIR,
        CodexTaskDef,
        OvernightCodexState,
        git_head,
        load_manifest,
        repo_rel,
        utc_now_iso,
        write_json,
    )
    from scripts.overnight_codex_orchestrator import _find_codex, execute_task, preflight
except ImportError:
    from overnight_codex_common import (
        OVERNIGHT_CODEX_DIR,
        PROJECT_DIR,
        RESULTS_DIR,
        CodexTaskDef,
        OvernightCodexState,
        git_head,
        load_manifest,
        repo_rel,
        utc_now_iso,
        write_json,
    )
    from overnight_codex_orchestrator import _find_codex, execute_task, preflight


STATE_FILE = OVERNIGHT_CODEX_DIR / "weekend_state.json"


def _load_tasks(path: Path) -> list[CodexTaskDef]:
    return load_manifest(path)


def _split_tasks(tasks: list[CodexTaskDef]) -> tuple[list[CodexTaskDef], list[CodexTaskDef]]:
    readonly = [task for task in tasks if task.write_policy == "readonly"]
    write = [task for task in tasks if task.write_policy == "guarded_write"]
    return readonly, write


def _run_write_orchestrator(manifest_path: Path, hours: float) -> subprocess.Popen[str]:
    cmd = [
        "python",
        str(PROJECT_DIR / "scripts" / "overnight_codex_orchestrator.py"),
        "--manifest",
        str(manifest_path),
        "--hours",
        str(hours),
        "--skip-lock",
        "--skip-preflight",
    ]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(PROJECT_DIR),
        env=env,
        encoding="utf-8",
        errors="replace",
    )


def run_parallel(manifest_path: Path, *, hours: float, workers: int, dry_run: bool) -> None:
    if not manifest_path.exists():
        generator = PROJECT_DIR / "scripts" / "overnight_codex_task_generator.py"
        subprocess.run(
            ["python", str(generator), "--output", str(manifest_path)],
            cwd=str(PROJECT_DIR),
            check=True,
        )
    tasks = _load_tasks(manifest_path)
    readonly, write = _split_tasks(tasks)
    print("=== KR Weekend Parallel Codex ===")
    print(f"Tasks: {len(tasks)} ({len(readonly)} readonly, {len(write)} guarded_write)")
    print(f"Workers: {workers}")
    print(f"Duration target: {hours} hours")
    print()

    if dry_run:
        for task in readonly:
            print(f"  [R] P{task.priority} {task.task_id}: {task.name}")
        for task in write:
            print(f"  [W] P{task.priority} {task.task_id}: {task.name}")
        return

    codex_bin = _find_codex()
    if not codex_bin:
        raise RuntimeError("Codex CLI not found in PATH.")
    preflight(skip_tests=False)

    readonly_state = OvernightCodexState(
        run_id=utc_now_iso(),
        started_at=utc_now_iso(),
        deadline=utc_now_iso(),
        launch_head=git_head(),
        apply_mode="queue_only",
        baseline_clean=False,
        baseline_tests_passed=False,
        notes=["Parallel readonly lane uses queue_only policy."],
    )

    write_manifest = OVERNIGHT_CODEX_DIR / "manifest_write.json"
    write_json(write_manifest, {"tasks": [asdict(task) for task in write]})
    write_proc = _run_write_orchestrator(write_manifest, hours) if write else None

    start = time.time()
    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(execute_task, task, state=readonly_state, codex_bin=codex_bin): task
            for task in readonly
        }
        for future in as_completed(futures):
            task = futures[future]
            result = future.result()
            results.append(asdict(result))
            print(f"  [{result.status.upper()}] {task.task_id}: {result.summary[:100]}")

    if write_proc is not None:
        remaining = max(0.0, hours * 3600 - (time.time() - start))
        try:
            write_stdout, _ = write_proc.communicate(timeout=remaining)
            (OVERNIGHT_CODEX_DIR / "write_orchestrator_output.log").write_text(
                write_stdout or "",
                encoding="utf-8",
            )
        except subprocess.TimeoutExpired:
            write_proc.kill()
            write_proc.communicate()

    write_json(
        STATE_FILE,
        {
            "finished_at": utc_now_iso(),
            "readonly_results": results,
            "readonly_count": len(readonly),
            "guarded_write_count": len(write),
        },
    )
    print()
    print(f"Parallel Codex results saved to {repo_rel(STATE_FILE)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parallel Codex weekend runner")
    parser.add_argument("--manifest", required=True, help="Path to a Codex manifest")
    parser.add_argument("--hours", type=float, default=12.0, help="Duration limit in hours")
    parser.add_argument("--workers", type=int, default=3, help="Readonly worker count")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan and exit")
    args = parser.parse_args()

    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = PROJECT_DIR / manifest
    run_parallel(manifest, hours=args.hours, workers=args.workers, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
