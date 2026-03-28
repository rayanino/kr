"""KR Weekend Sprint — Parallel Coordinator.

Runs readonly analysis/bughunt tasks in parallel (3 workers) while a
sequential write orchestrator handles test/script creation tasks.

Usage:
  python scripts/weekend_parallel.py --manifest overnight/sprint_manifest.json --hours 20
  python scripts/weekend_parallel.py --manifest overnight/sprint_manifest.json --dry-run
  python scripts/weekend_parallel.py --manifest overnight/sprint_manifest.json --task bughunt-source-trust
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent
OVERNIGHT_DIR = PROJECT_DIR / "overnight"
RESULTS_DIR = OVERNIGHT_DIR / "results"
STATE_FILE = OVERNIGHT_DIR / "weekend_state.json"
PROGRESS_FILE = OVERNIGHT_DIR / "weekend_progress.md"
HEARTBEAT_FILE = OVERNIGHT_DIR / ".heartbeat"

# Safety prompts (same as in orchestrator, but standalone for readonly workers)
READONLY_SAFETY = """WEEKEND SPRINT — READONLY ANALYSIS MODE — KR Pipeline Project.
You are executing a readonly analysis task in the weekend sprint system.

ABSOLUTE RULES — SAFETY:
- NEVER modify any file in the repository
- NEVER run git commit or git push
- NEVER delete any file or directory
- NEVER modify .claude/settings.json
- NEVER modify files in library/sources/*/frozen/
- There is no human present — do not ask questions
- Write ALL output to overnight/results/{TASK_ID}/
- You MAY read any file for analysis

CRITICAL PROTECTION:
- engines/excerpting/src/ is under active CLI backend reformation
- Analyze but do NOT suggest code modifications to excerpting source files
- The pipeline has 5 engines: Source, Normalization, Excerpting, Taxonomy, Synthesis
- Passaging and Atomization directories are STALE ARTIFACTS from an old plan — ignore them

QUALITY RULES:
1. Every claim must reference specific file paths and line numbers.
2. Write structured findings to overnight/results/{TASK_ID}/findings.md
3. Write machine-readable summary to overnight/results/{TASK_ID}/findings.json

Read CLAUDE.md for project context. Follow all rules in .claude/rules/*.
"""

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class TaskDef:
    """Task definition from manifest."""

    task_id: str
    name: str
    category: str
    prompt: str
    safety_level: str = "readonly"
    execution_mode: str = "cli"
    model: str = "opus"
    max_budget_usd: float = 0
    timeout_minutes: int = 30
    allowed_tools: list[str] = field(default_factory=list)
    permission_mode: str = "bypassPermissions"
    depends_on: list[str] = field(default_factory=list)
    priority: int = 5
    max_turns: int = 25
    bookend: bool = False
    estimated_complexity: str = "medium"  # low|medium|high — controls sort order


# Complexity sort order: low tasks run before medium, medium before high
_COMPLEXITY_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass
class TaskResult:
    """Result from executing a task."""

    task_id: str
    status: str  # success|failed|timeout|skipped
    duration_s: float = 0.0
    error: str = ""
    worker: str = ""
    start_time: str = ""
    end_time: str = ""


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------


class SprintState:
    """Thread-safe state tracking for parallel execution."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.started_at: str = datetime.now(timezone.utc).isoformat()
        self.readonly_completed: int = 0
        self.readonly_failed: int = 0
        self.write_completed: int = 0
        self.write_failed: int = 0
        self.results: list[dict] = []
        self.active_workers: dict[str, str] = {}  # worker_id -> task_id
        self.write_orchestrator_status: str = "not_started"

    def record_result(self, result: TaskResult) -> None:
        with self._lock:
            self.results.append(asdict(result))
            if result.status in ("success", "partial_success"):
                if result.worker.startswith("readonly"):
                    self.readonly_completed += 1
                else:
                    self.write_completed += 1
            else:
                if result.worker.startswith("readonly"):
                    self.readonly_failed += 1
                else:
                    self.write_failed += 1

    def set_active(self, worker_id: str, task_id: str) -> None:
        with self._lock:
            self.active_workers[worker_id] = task_id

    def clear_active(self, worker_id: str) -> None:
        with self._lock:
            self.active_workers.pop(worker_id, None)

    @property
    def total_completed(self) -> int:
        return self.readonly_completed + self.write_completed

    @property
    def total_failed(self) -> int:
        return self.readonly_failed + self.write_failed

    def save(self) -> None:
        with self._lock:
            data = {
                "started_at": self.started_at,
                "readonly_completed": self.readonly_completed,
                "readonly_failed": self.readonly_failed,
                "write_completed": self.write_completed,
                "write_failed": self.write_failed,
                "active_workers": dict(self.active_workers),
                "results": list(self.results),
                "write_orchestrator_status": self.write_orchestrator_status,
            }
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(STATE_FILE)


# ---------------------------------------------------------------------------
# Unified heartbeat (FIX-6)
# ---------------------------------------------------------------------------


def _write_unified_heartbeat(
    state: SprintState, total_readonly: int, total_write: int,
) -> None:
    """Write unified heartbeat file for external monitoring."""
    with state._lock:
        data = {
            "source": "parallel_coordinator",
            "pid": os.getpid(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "readonly_completed": state.readonly_completed,
            "readonly_failed": state.readonly_failed,
            "readonly_active": list(state.active_workers.values()),
            "write_completed": state.write_completed,
            "write_failed": state.write_failed,
            "total_readonly": total_readonly,
            "total_write": total_write,
        }
    tmp = HEARTBEAT_FILE.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(HEARTBEAT_FILE)
    except OSError:
        pass  # Ignore file access conflicts on Windows


# ---------------------------------------------------------------------------
# Write orchestrator health monitoring (FIX-2)
# ---------------------------------------------------------------------------


def _monitor_write_orchestrator(
    proc: subprocess.Popen,
    state: SprintState,
    shutdown: threading.Event,
    poll_interval_s: int = 60,
) -> None:
    """Monitor write orchestrator subprocess health (runs as daemon thread)."""
    last_heartbeat_task: str | None = None
    last_progress_time = time.time()
    stall_threshold_s = 50 * 60  # 50 min (2x typical 25m task timeout)

    while not shutdown.is_set():
        shutdown.wait(timeout=poll_interval_s)
        if shutdown.is_set():
            break

        # Check process liveness
        retcode = proc.poll()
        if retcode is not None:
            status = "completed" if retcode == 0 else f"dead (exit {retcode})"
            print(f"\n  [monitor] Write orchestrator: {status}")
            state.write_orchestrator_status = status
            return

        # Check heartbeat for progress
        try:
            hb_text = HEARTBEAT_FILE.read_text(encoding="utf-8")
            hb = json.loads(hb_text)
            if hb.get("source") == "write_orchestrator":
                current_task = hb.get("last_task")
                if current_task != last_heartbeat_task:
                    last_heartbeat_task = current_task
                    last_progress_time = time.time()
                elif time.time() - last_progress_time > stall_threshold_s:
                    print(f"\n  [monitor] Write orchestrator STALLED on {current_task}")
                    state.write_orchestrator_status = f"stalled on {current_task}"
        except (OSError, PermissionError, json.JSONDecodeError):
            pass  # Heartbeat file may not exist yet or be mid-write


# ---------------------------------------------------------------------------
# Readonly worker — runs claude -p directly
# ---------------------------------------------------------------------------


def execute_readonly_task(
    task: TaskDef, worker_id: str, state: SprintState,
) -> TaskResult:
    """Execute a single readonly task via claude -p."""
    state.set_active(worker_id, task.task_id)
    start = time.time()
    start_ts = datetime.now(timezone.utc).isoformat()

    # Create results directory
    task_dir = RESULTS_DIR / task.task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    safety = READONLY_SAFETY.replace("{TASK_ID}", task.task_id)

    # Readonly tasks: restrict to Read, Glob, Grep only (no Bash — Codex review #2)
    readonly_tools = ["Read", "Glob", "Grep"]

    cmd = [
        "claude", "-p", task.prompt,
        "--output-format", "json",
        "--model", task.model,
        "--dangerously-skip-permissions",
        "--no-session-persistence",
        "--append-system-prompt", safety,
        "--effort", "max" if task.model == "opus" else "high",
        "--allowedTools", ",".join(readonly_tools),
    ]
    if task.model == "opus":
        cmd += ["--fallback-model", "sonnet"]
    # Always cap budget — defense-in-depth (CC review B-2, Gemini recommendation)
    effective_budget = max(task.max_budget_usd, 5.0)
    cmd += ["--max-budget-usd", str(effective_budget)]
    if task.max_turns > 0:
        cmd += ["--max-turns", str(task.max_turns)]

    env = {
        **os.environ,
        "KR_OVERNIGHT": "1",
        "PYTHONIOENCODING": "utf-8",
    }
    env.pop("ANTHROPIC_API_KEY", None)

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(PROJECT_DIR), env=env,
            encoding="utf-8", errors="replace",
        )
        timeout_s = task.timeout_minutes * 60
        stdout, stderr = proc.communicate(timeout=timeout_s)

        # Save raw output
        (task_dir / "raw_output.json").write_text(
            stdout or "{}", encoding="utf-8",
        )
        if stderr:
            (task_dir / "stderr.log").write_text(stderr, encoding="utf-8")

        status = "success" if proc.returncode == 0 else "failed"
        error = stderr[-500:] if proc.returncode != 0 and stderr else ""

    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        # Check for partial output before marking as total failure
        partial = False
        for fname in ("findings.json", "findings.md", "summary.md"):
            f = task_dir / fname
            if f.exists() and f.stat().st_size > 1024:
                partial = True
                break
        status = "partial_success" if partial else "timeout"
        error = f"Exceeded {task.timeout_minutes}m timeout" + (" (partial output preserved)" if partial else "")
    except Exception as e:
        status = "failed"
        error = str(e)

    end = time.time()
    result = TaskResult(
        task_id=task.task_id, status=status,
        duration_s=round(end - start, 1), error=error,
        worker=worker_id, start_time=start_ts,
        end_time=datetime.now(timezone.utc).isoformat(),
    )

    # Save result
    (task_dir / "result.json").write_text(
        json.dumps(asdict(result), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    state.clear_active(worker_id)
    state.record_result(result)
    return result


# ---------------------------------------------------------------------------
# Progress dashboard
# ---------------------------------------------------------------------------


def print_dashboard(
    state: SprintState,
    total_readonly: int,
    total_write: int,
    start_time: float,
) -> None:
    """Print a compact progress dashboard."""
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    mins = int((elapsed % 3600) // 60)

    r_done = state.readonly_completed + state.readonly_failed
    w_done = state.write_completed + state.write_failed
    total_done = r_done + w_done
    total_tasks = total_readonly + total_write

    active = list(state.active_workers.values())
    active_str = ", ".join(active[:4]) if active else "(idle)"

    print(
        f"\r[{hours:02d}:{mins:02d}] "
        f"Done: {total_done}/{total_tasks} "
        f"(R:{state.readonly_completed}/{total_readonly} "
        f"W:{state.write_completed}/{total_write}) "
        f"Fail:{state.total_failed} "
        f"Active: {active_str}",
        end="", flush=True,
    )


# ---------------------------------------------------------------------------
# Main coordinator
# ---------------------------------------------------------------------------


def load_manifest(path: Path) -> list[TaskDef]:
    """Load tasks from manifest JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    tasks = []
    for t in data["tasks"]:
        tasks.append(TaskDef(**{k: v for k, v in t.items() if k in TaskDef.__dataclass_fields__}))
    return tasks


def split_tasks(tasks: list[TaskDef]) -> tuple[list[TaskDef], list[TaskDef]]:
    """Split tasks into readonly and write queues."""
    readonly = [t for t in tasks if t.category == "sprint_analysis"]
    write = [t for t in tasks if t.category in ("sprint_test", "sprint_script")]
    return readonly, write


def run_write_orchestrator(write_manifest: Path, hours: float) -> subprocess.Popen:
    """Launch the existing orchestrator for write tasks."""
    cmd = [
        "python", str(PROJECT_DIR / "scripts" / "overnight_orchestrator.py"),
        "--manifest", str(write_manifest),
        "--hours", str(hours),
    ]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=str(PROJECT_DIR), env=env,
        encoding="utf-8", errors="replace",
    )


def run_parallel(
    manifest_path: Path,
    hours: float = 20.0,
    max_readonly_workers: int = 3,
    single_task: str | None = None,
    dry_run: bool = False,
    resume: bool = False,
) -> None:
    """Run the parallel sprint system."""
    tasks = load_manifest(manifest_path)
    readonly_tasks, write_tasks = split_tasks(tasks)

    print(f"=== KR Weekend Sprint — Parallel Mode ===")
    print(f"Total tasks: {len(tasks)} ({len(readonly_tasks)} readonly, {len(write_tasks)} write)")
    print(f"Readonly workers: {max_readonly_workers}")
    print(f"Duration target: {hours} hours")
    print()

    # Resume: skip already-completed tasks from previous run (FIX-4)
    completed_task_ids: set[str] = set()
    if resume and STATE_FILE.exists():
        try:
            old_state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            for r in old_state.get("results", []):
                if r.get("status") in ("success", "partial_success"):
                    completed_task_ids.add(r["task_id"])
            print(f"RESUME: {len(completed_task_ids)} tasks already completed, will skip")
        except Exception as e:
            print(f"Resume failed to load state: {e}, starting fresh")
            completed_task_ids.clear()

    if completed_task_ids:
        readonly_tasks = [t for t in readonly_tasks if t.task_id not in completed_task_ids]
        write_tasks = [t for t in write_tasks if t.task_id not in completed_task_ids]
        print(f"After resume filter: {len(readonly_tasks)} readonly, {len(write_tasks)} write remaining")

    if dry_run:
        print("=== DRY RUN ===")
        print(f"\nReadonly tasks ({len(readonly_tasks)}):")
        for i, t in enumerate(readonly_tasks, 1):
            print(f"  {i:3d}. [{t.priority}] {t.task_id}: {t.name[:70]} ({t.estimated_complexity})")
        print(f"\nWrite tasks ({len(write_tasks)}):")
        for i, t in enumerate(write_tasks, 1):
            print(f"  {i:3d}. [{t.priority}] {t.task_id}: {t.name[:70]} ({t.estimated_complexity})")
        return

    # Single task mode
    if single_task:
        task = next((t for t in tasks if t.task_id == single_task), None)
        if not task:
            print(f"ERROR: Task '{single_task}' not found")
            sys.exit(1)
        state = SprintState()
        print(f"Running single task: {task.task_id}")
        result = execute_readonly_task(task, "readonly-0", state)
        print(f"\nResult: {result.status} ({result.duration_s}s)")
        if result.error:
            print(f"Error: {result.error}")
        return

    # Full parallel run
    state = SprintState()
    start_time = time.time()
    deadline = start_time + (hours * 3600)
    shutdown = threading.Event()

    def handle_signal(sig: int, frame: Any) -> None:
        print("\n\nShutdown requested. Finishing active tasks...")
        shutdown.set()

    signal.signal(signal.SIGINT, handle_signal)

    # Sort by priority, then complexity (easy wins first), then task_id
    readonly_tasks.sort(key=lambda t: (t.priority, _COMPLEXITY_ORDER.get(t.estimated_complexity, 1), t.task_id))
    write_tasks.sort(key=lambda t: (t.priority, _COMPLEXITY_ORDER.get(t.estimated_complexity, 1), t.task_id))

    # Separate bookend tasks — run after pool completes (CC review B-3)
    regular_readonly = [t for t in readonly_tasks if not t.bookend]
    bookend_readonly = [t for t in readonly_tasks if t.bookend]
    print(f"  Regular readonly: {len(regular_readonly)}, Bookend: {len(bookend_readonly)}")

    # Create write manifest for the orchestrator
    write_manifest = OVERNIGHT_DIR / "sprint_write_manifest.json"
    with open(write_manifest, "w", encoding="utf-8") as f:
        json.dump(
            {"tasks": [asdict(t) for t in write_tasks]},
            f, indent=2, ensure_ascii=False,
        )

    # Launch write orchestrator as background process
    print(f"Launching write orchestrator with {len(write_tasks)} tasks...")
    write_proc = run_write_orchestrator(write_manifest, hours)
    state.write_orchestrator_status = "running"

    # Start health monitor for write orchestrator (FIX-2)
    monitor_thread = threading.Thread(
        target=_monitor_write_orchestrator,
        args=(write_proc, state, shutdown),
        daemon=True,
    )
    monitor_thread.start()

    # Launch readonly pool
    print(f"Launching readonly pool with {max_readonly_workers} workers...")
    print()

    # Incremental scheduling: submit tasks in batches, check deadline between batches
    # (Codex review #3: don't submit all tasks at once)
    completed_readonly = 0
    skipped_readonly = 0
    task_idx = 0

    # Run regular (non-bookend) readonly tasks in pool
    with ThreadPoolExecutor(max_workers=max_readonly_workers, thread_name_prefix="readonly") as pool:
        while task_idx < len(regular_readonly):
            if shutdown.is_set():
                skipped_readonly = len(regular_readonly) - task_idx
                print(f"\n  Shutdown: skipping {skipped_readonly} remaining readonly tasks")
                break
            if time.time() > deadline:
                skipped_readonly = len(regular_readonly) - task_idx
                print(f"\n  Deadline reached: skipping {skipped_readonly} remaining readonly tasks")
                break

            batch_end = min(task_idx + max_readonly_workers, len(regular_readonly))
            futures: dict[Future, TaskDef] = {}

            for i in range(task_idx, batch_end):
                task = regular_readonly[i]
                worker_id = f"readonly-{i % max_readonly_workers}"
                future = pool.submit(execute_readonly_task, task, worker_id, state)
                futures[future] = task

            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    icon = "+" if result.status in ("success", "partial_success") else "X"
                    print(f"\n  [{icon}] {task.task_id}: {result.status} ({result.duration_s:.0f}s)")
                except Exception as e:
                    print(f"\n  [!] {task.task_id}: exception: {e}")

                completed_readonly += 1
                state.save()
                _write_unified_heartbeat(state, len(readonly_tasks), len(write_tasks))
                print_dashboard(state, len(readonly_tasks), len(write_tasks), start_time)

            task_idx = batch_end

    # Run bookend readonly tasks sequentially AFTER pool completes (CC review B-3)
    if bookend_readonly and not shutdown.is_set() and time.time() < deadline:
        print(f"\n\nRunning {len(bookend_readonly)} bookend readonly tasks sequentially...")
        for task in bookend_readonly:
            if shutdown.is_set() or time.time() > deadline:
                break
            result = execute_readonly_task(task, "bookend-0", state)
            icon = "+" if result.status in ("success", "partial_success") else "X"
            print(f"  [{icon}] {task.task_id}: {result.status} ({result.duration_s:.0f}s)")
            state.save()
            _write_unified_heartbeat(state, len(readonly_tasks), len(write_tasks))

    # Wait for write orchestrator
    print("\n\nReadonly pool complete. Waiting for write orchestrator...")
    try:
        write_stdout, _ = write_proc.communicate(timeout=max(0, deadline - time.time()))
        # Save write orchestrator output
        (OVERNIGHT_DIR / "write_orchestrator_output.log").write_text(
            write_stdout or "(empty)", encoding="utf-8",
        )
        # Update final write orchestrator status (FIX-2)
        if write_proc.returncode == 0:
            state.write_orchestrator_status = "completed"
        elif write_proc.returncode is not None:
            state.write_orchestrator_status = f"exited ({write_proc.returncode})"
    except subprocess.TimeoutExpired:
        write_proc.kill()
        write_proc.communicate()
        state.write_orchestrator_status = "killed (deadline)"
        print("Write orchestrator killed (deadline reached)")

    # Final state save
    state.save()
    _write_unified_heartbeat(state, len(readonly_tasks), len(write_tasks))

    # Print summary
    elapsed = time.time() - start_time
    hours_elapsed = elapsed / 3600
    print(f"\n\n{'='*60}")
    print(f"WEEKEND SPRINT COMPLETE")
    print(f"{'='*60}")
    print(f"Duration: {hours_elapsed:.1f} hours")
    print(f"Readonly: {state.readonly_completed} done, {state.readonly_failed} failed")
    print(f"Write:    {state.write_completed} done, {state.write_failed} failed")
    print(f"Total:    {state.total_completed} done, {state.total_failed} failed")
    print(f"\nResults in: {RESULTS_DIR}")
    print(f"State in:   {STATE_FILE}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="KR Weekend Sprint — Parallel Coordinator")
    parser.add_argument("--manifest", required=True, help="Path to sprint manifest JSON")
    parser.add_argument("--hours", type=float, default=20.0, help="Maximum runtime in hours")
    parser.add_argument("--workers", type=int, default=3, help="Number of readonly workers")
    parser.add_argument("--task", help="Run a single task by ID")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--resume", action="store_true", help="Resume from last weekend_state.json")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = PROJECT_DIR / manifest_path

    run_parallel(
        manifest_path=manifest_path,
        hours=args.hours,
        max_readonly_workers=args.workers,
        single_task=args.task,
        dry_run=args.dry_run,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
