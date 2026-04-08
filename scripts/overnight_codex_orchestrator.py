"""Isolated Codex-first overnight orchestrator with guarded worktree writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict
from datetime import date, datetime, timezone
from datetime import timedelta
from pathlib import Path
from typing import Any

try:
    from scripts.overnight_codex_backlog import (
        summarize_backlog,
        sync_backlog_from_artifacts,
        update_backlog_status,
    )
    from scripts.overnight_codex_common import (
        ACTIVE_AUTHORITY_FILE,
        COMPLEXITY_ORDER,
        CREATIVE_RUN_LOG,
        DECISIONS_LOG,
        EVENTS_FILE,
        FINAL_RESPONSE_SCHEMA,
        FINDINGS_REGISTRY_FILE,
        HEARTBEAT_FILE,
        LOCK_FILE,
        MORNING_REPORT,
        OVERNIGHT_CODEX_DIR,
        PIPELINE_ORDER,
        PROJECT_DIR,
        PROGRESS_FILE,
        QUEUE_DIR,
        RESULTS_DIR,
        RUN_SNAPSHOTS_DIR,
        SHADOW_SETUP_WRITE_TARGETS,
        STATE_FILE,
        WORKTREES_DIR,
        CodexTaskDef,
        OvernightCodexState,
        TaskResult,
        append_jsonl,
        atomic_write,
        ensure_runtime_dirs,
        git_head,
        git_status_porcelain,
        has_forbidden_edits,
        load_active_authority,
        load_manifest,
        rewrite_python_command,
        repo_rel,
        safe_slug,
        utc_now,
        utc_now_iso,
        validate_action_items,
        worktree_changed_files,
        write_json,
        write_progress_file,
    )
except ImportError:
    from overnight_codex_backlog import (
        summarize_backlog,
        sync_backlog_from_artifacts,
        update_backlog_status,
    )
    from overnight_codex_common import (
        ACTIVE_AUTHORITY_FILE,
        COMPLEXITY_ORDER,
        CREATIVE_RUN_LOG,
        DECISIONS_LOG,
        EVENTS_FILE,
        FINAL_RESPONSE_SCHEMA,
        FINDINGS_REGISTRY_FILE,
        HEARTBEAT_FILE,
        LOCK_FILE,
        MORNING_REPORT,
        OVERNIGHT_CODEX_DIR,
        PIPELINE_ORDER,
        PROJECT_DIR,
        PROGRESS_FILE,
        QUEUE_DIR,
        RESULTS_DIR,
        RUN_SNAPSHOTS_DIR,
        SHADOW_SETUP_WRITE_TARGETS,
        STATE_FILE,
        WORKTREES_DIR,
        CodexTaskDef,
        OvernightCodexState,
        TaskResult,
        append_jsonl,
        atomic_write,
        ensure_runtime_dirs,
        git_head,
        git_status_porcelain,
        has_forbidden_edits,
        load_active_authority,
        load_manifest,
        rewrite_python_command,
        repo_rel,
        safe_slug,
        utc_now,
        utc_now_iso,
        validate_action_items,
        worktree_changed_files,
        write_json,
        write_progress_file,
    )


MAX_CONSECUTIVE_FAILURES = 3
MAX_CONSECUTIVE_TIMEOUTS = 4
MAX_TIMEOUT_MINUTES = 50
ENABLE_STRICT_CODEX_REVIEW = False

READONLY_SAFETY_PROMPT = """OVERNIGHT_CODEX — LOW-AUTHORITY READONLY EMPLOYEE.

You are not the boss and not the repo architect. You are a bounded overnight employee.

Absolute rules:
- Never edit any file in the repository.
- Never edit .claude/, overnight/, overnight_codex/, docs/superpowers/, CLAUDE.md, NEXT.md, or any launcher/orchestrator.
- Never run git commit, git push, git rebase, git reset, or git checkout.
- Never invent roadmap work or architecture ownership.
- Use only local repo evidence and local commands. No web work.
- Ignore NEXT.md, AGENT_TEAM_HANDOFF.md, integration handoff docs, and unrelated planning files unless the task explicitly names them.
- Prefer reading only the files named by the task and their directly adjacent tests or helpers.
- Final response must be valid JSON matching the provided schema.
"""

WRITE_SAFETY_PROMPT = """OVERNIGHT_CODEX — LOW-AUTHORITY GUARDED-WRITE EMPLOYEE.

You are not the boss and not the repo architect. You are a bounded overnight employee.

Absolute rules:
- You may only make the minimum local code/test changes needed for this task.
- Never edit .claude/, overnight/, overnight_codex/, docs/superpowers/, CLAUDE.md, NEXT.md, or any launcher/orchestrator.
- Never implement new product features or new autonomous systems.
- Never run git commit, git push, git rebase, git reset, or git checkout.
- Never edit engine SPEC.md files or planning documents.
- Prefer regression tests and local bug fixes over broader refactors.
- Ignore NEXT.md, AGENT_TEAM_HANDOFF.md, integration handoff docs, and unrelated planning files unless the task explicitly names them.
- Prefer reading only the files named by the task and their directly adjacent tests or helpers.
- Do not attempt to launch long integration runs; the orchestrator will perform post-change validation outside your sandbox.
- Final response must be valid JSON matching the provided schema.
"""


def _shadow_setup_allows_task(task: CodexTaskDef) -> tuple[bool, str]:
    """Restrict pre-cutover writes to Codex setup files only."""
    if task.write_policy == "readonly":
        return True, ""
    unexpected = [
        prefix
        for prefix in task.allowed_write_prefixes
        if not any(prefix == target or prefix.startswith(target) for target in SHADOW_SETUP_WRITE_TARGETS)
    ]
    if unexpected:
        return False, f"shadow setup blocks write prefixes: {unexpected}"
    return True, ""


def _requires_shadow_setup_restrictions(state: OvernightCodexState) -> bool:
    """Apply shadow restrictions unless autonomous Codex mode is active."""
    return state.runtime_mode != "autonomous_codex"


def _task_checkout_token(task_id: str) -> str:
    """Return a short, stable token for worktree and branch naming."""
    slug = safe_slug(task_id)
    prefix = slug[:12].strip("-.")
    digest = hashlib.sha1(task_id.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}" if prefix else digest


def _tail_process_output(result: subprocess.CompletedProcess[str], limit: int = 1200) -> str:
    """Return the most useful tail of a subprocess failure."""
    text = (result.stderr or "").strip() or (result.stdout or "").strip()
    if not text:
        return f"exit code {result.returncode}"
    return text[-limit:]


BREAKER_FAILURE_CLASSES = {"infra_failure"}
SIGNAL_STATUSES = {"queued", "partial_success", "failed", "timeout", "usage_limited"}
PARTIAL_ARTIFACT_NAMES = (
    "final_response.json",
    "review.json",
    "findings.json",
    "creative.json",
    "boundaries.json",
    "coverage.json",
    "audit.json",
    "report.json",
    "summary.md",
    "fallback.md",
)
ENVIRONMENT_PATTERNS = (
    ("no usable python runtime", "No usable Python runtime was available in the task sandbox."),
    ("no accessible python runtime", "No accessible Python runtime was available in the task sandbox."),
    ("no `python` executable", "Python was unavailable in the task sandbox."),
    ("python --version (not available)", "Python was unavailable in the task sandbox."),
    ("uv could not provision", "uv could not provision a runtime inside the task sandbox."),
    ("network downloads are blocked", "Sandbox network downloads were blocked for runtime provisioning."),
    ("filesystem access restrictions", "Sandbox filesystem restrictions blocked runtime provisioning."),
    ("sandbox/network", "Sandbox constraints blocked requested runtime checks."),
)


def _failure_breaker_tripped(state: OvernightCodexState) -> bool:
    """Return whether repeated unhealthy results should stop the run."""
    if state.consecutive_breaker_failures >= MAX_CONSECUTIVE_FAILURES:
        return True
    if state.consecutive_timeouts >= MAX_CONSECUTIVE_TIMEOUTS:
        return True
    return (
        state.consecutive_failures >= MAX_CONSECUTIVE_FAILURES
        and (state.consecutive_breaker_failures > 0 or state.consecutive_timeouts > 0)
    )
LANE_ORDER = {"analysis_lane": 0, "synthesis_lane": 1, "write_lane": 2}
LEGACY_RESULT_PREFIX = "overnight/results/"
READONLY_GUARD_ROOTS = (
    PROJECT_DIR / "engines",
    PROJECT_DIR / "shared",
    PROJECT_DIR / "scripts",
    PROJECT_DIR / "docs",
    PROJECT_DIR / "tests",
    PROJECT_DIR / "overnight",
)


def _append_event(event_type: str, payload: dict[str, Any]) -> None:
    """Append one structured runtime event."""
    append_jsonl(
        EVENTS_FILE,
        {
            "timestamp": utc_now_iso(),
            "event_type": event_type,
            **payload,
        },
    )


def _creative_run_log_key(task_id: str) -> str:
    """Convert a creative task id back into the generator cooldown key."""
    body = task_id.removeprefix("creative-")
    template_slug, sep, focus_engine = body.rpartition("-")
    if not sep or not template_slug or not focus_engine:
        return body
    template_id = template_slug.replace("-", "/", 1)
    return f"{template_id}:{focus_engine}"


def _update_creative_run_log(task_id: str) -> None:
    """Record a successful creative run for cooldown tracking."""
    log_data: dict[str, Any] = {"runs": {}}
    if CREATIVE_RUN_LOG.exists():
        try:
            log_data = json.loads(CREATIVE_RUN_LOG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    log_data.setdefault("runs", {})[_creative_run_log_key(task_id)] = date.today().isoformat()
    write_json(CREATIVE_RUN_LOG, log_data)


def _collect_partial_artifacts(result_dir: Path, min_bytes: int = 1024) -> list[str]:
    """List meaningful artifacts preserved by a partial task."""
    artifacts: list[str] = []
    for name in PARTIAL_ARTIFACT_NAMES:
        path = result_dir / name
        if path.exists() and path.stat().st_size >= min_bytes:
            artifacts.append(repo_rel(path))
    return artifacts


def _snapshot_tree(root: Path) -> dict[str, tuple[int, int]]:
    """Capture file size and mtime for one protected tree."""
    if not root.exists():
        return {}
    snapshot: dict[str, tuple[int, int]] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        stat = path.stat()
        snapshot[repo_rel(path)] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def _diff_tree_snapshot(
    before: dict[str, tuple[int, int]],
    after: dict[str, tuple[int, int]],
) -> list[str]:
    """Return protected-tree files that were added, removed, or modified."""
    changed: list[str] = []
    for path, state in after.items():
        if before.get(path) != state:
            changed.append(path)
    for path in before:
        if path not in after:
            changed.append(path)
    return sorted(set(changed))


def _snapshot_readonly_guard() -> dict[str, Any]:
    """Capture main-repo state before a readonly task runs."""
    return {
        "git_status": set(git_status_porcelain()),
        "protected_roots": {
            repo_rel(root): _snapshot_tree(root)
            for root in READONLY_GUARD_ROOTS
        },
    }


def _readonly_guard_failures(before: dict[str, Any]) -> list[str]:
    """Detect main-repo mutations performed by a readonly task."""
    failures: list[str] = []
    current_status = set(git_status_porcelain())
    added_status = sorted(current_status - set(before.get("git_status", set())))
    if added_status:
        failures.append(f"Readonly task mutated tracked repo state: {added_status}")
    protected_roots = before.get("protected_roots", {})
    if isinstance(protected_roots, dict):
        for root_label, snapshot in protected_roots.items():
            root_path = PROJECT_DIR / root_label
            after_snapshot = _snapshot_tree(root_path)
            changed = _diff_tree_snapshot(snapshot, after_snapshot)
            if changed:
                failures.append(f"Readonly task wrote protected root `{root_label}`: {changed}")
    return failures


def _environment_notes_from_texts(texts: list[str]) -> list[str]:
    """Extract structured environment notes from free-form task output."""
    notes: list[str] = []
    lowered_texts = [text.lower() for text in texts if text]
    for pattern, note in ENVIRONMENT_PATTERNS:
        if any(pattern in text for text in lowered_texts) and note not in notes:
            notes.append(note)
    return notes


def _extract_environment_notes(payload: dict[str, Any]) -> list[str]:
    """Pull environment blockers out of a structured task payload."""
    texts: list[str] = [str(payload.get("summary", ""))]
    texts.extend(str(item) for item in payload.get("tests_run", []))
    texts.extend(str(item) for item in payload.get("commands_run", []))
    for evidence in payload.get("evidence", []):
        if isinstance(evidence, dict):
            texts.append(str(evidence.get("detail", "")))
    return _environment_notes_from_texts(texts)


def _classify_quality_gate_failures(failures: list[str]) -> str:
    """Classify quality-gate failures into a stable failure class."""
    joined = " ".join(failures).lower()
    if any(
        token in joined
        for token in (
            "forbidden files changed",
            "touched files outside allowlist",
            "deleted files are not allowed",
        )
    ):
        return "policy_blocked"
    if "pytest failed" in joined or "pre_review_checks failed" in joined:
        return "validation_failed"
    return "task_failed"


def _recommend_next_actions(
    *,
    task: CodexTaskDef,
    status: str,
    failure_class: str | None,
    environment_notes: list[str],
    patch_path: str | None = None,
) -> list[str]:
    """Return compact next actions for reports and packets."""
    actions: list[str] = []
    if patch_path:
        actions.append(f"Review and apply queued patch `{patch_path}` if the change is still wanted.")
    if failure_class == "infra_failure":
        actions.append("Fix the runtime/orchestrator issue before re-running similar tasks.")
    elif failure_class == "policy_blocked":
        actions.append("Tighten task scope or allowlists before retrying this task.")
    elif failure_class == "validation_failed":
        actions.append("Inspect the failing validation/test surface before allowing this task to retry.")
    elif failure_class == "usage_limited":
        actions.append("Wait for provider quota reset or lower the nightly load before resuming.")
    elif status == "partial_success":
        actions.append("Review preserved partial artifacts and convert them into a follow-up task if valuable.")
    if environment_notes:
        actions.append("Treat sandbox/runtime blockers as environment issues, not product-code failures.")
    if not actions and task.write_policy == "guarded_write":
        actions.append("Review the bounded write result and decide whether to retry or leave it queued.")
    return actions[:3]


def _snapshot_filename(started_at: str) -> str:
    """Return a stable filename for a run snapshot."""
    safe = started_at.replace(":", "-").replace("+", "_")
    return f"{safe}.json"


def _load_previous_snapshot(current_started_at: str) -> dict[str, Any] | None:
    """Load the most recent snapshot before the current run."""
    candidates = sorted(RUN_SNAPSHOTS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime)
    for path in reversed(candidates):
        try:
            snapshot = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if snapshot.get("started_at") != current_started_at:
            return snapshot
    return None


def _build_run_snapshot(state: OvernightCodexState, manifest: list[CodexTaskDef]) -> dict[str, Any]:
    """Build a machine-readable snapshot of the current run."""
    tasks: dict[str, Any] = {}
    status_counts: dict[str, int] = {}
    backlog_summary = summarize_backlog(run_id=state.run_id)
    for task in manifest:
        result = state.results.get(task.task_id, {})
        status = str(result.get("status", "pending"))
        status_counts[status] = status_counts.get(status, 0) + 1
        tasks[task.task_id] = {
            "name": task.name,
            "backlog_item_id": task.backlog_item_id or None,
            "category": task.category,
            "lane": task.lane,
            "priority": task.priority,
            "status": status,
            "failure_class": result.get("failure_class"),
            "queued_only": result.get("queued_only", False),
            "patch_path": result.get("patch_path"),
            "partial_artifacts": list(result.get("partial_artifacts", [])),
            "environment_notes": list(result.get("environment_notes", [])),
            "recommended_next_actions": list(result.get("recommended_next_actions", [])),
        }
    return {
        "run_id": state.run_id,
        "started_at": state.started_at,
        "deadline": state.deadline,
        "status": state.status,
        "active_authority": state.active_authority,
        "runtime_mode": state.runtime_mode,
        "apply_mode": state.apply_mode,
        "launch_head": state.launch_head,
        "backlog": backlog_summary,
        "summary": {
            "completed": state.tasks_completed,
            "failed": state.tasks_failed,
            "queued": state.tasks_queued,
            "skipped": state.tasks_skipped,
            "status_counts": status_counts,
            "failure_class_counts": dict(state.failure_class_counts),
        },
        "tasks": tasks,
    }


def _write_run_snapshot(state: OvernightCodexState, manifest: list[CodexTaskDef]) -> Path:
    """Persist the current run snapshot."""
    snapshot_path = RUN_SNAPSHOTS_DIR / _snapshot_filename(state.started_at)
    write_json(snapshot_path, _build_run_snapshot(state, manifest))
    return snapshot_path


def _write_task_packet(
    result_dir: Path,
    task: CodexTaskDef,
    result: TaskResult,
    payload: dict[str, Any] | None = None,
) -> None:
    """Write a compact research packet for the task outcome."""
    packet = {
        "task_id": task.task_id,
        "backlog_item_id": task.backlog_item_id or None,
        "name": task.name,
        "category": task.category,
        "lane": task.lane,
        "learning_value": task.learning_value,
        "status": result.status,
        "failure_class": result.failure_class,
        "summary": result.summary,
        "artifact_path": result.artifact_path,
        "partial_artifacts": list(result.partial_artifacts),
        "environment_notes": list(result.environment_notes),
        "recommended_next_actions": list(result.recommended_next_actions),
        "payload": payload or {},
    }
    write_json(result_dir / "packet.json", packet)


def _finalize_task_result(
    *,
    task: CodexTaskDef,
    result_dir: Path,
    result: TaskResult,
    payload: dict[str, Any] | None = None,
) -> TaskResult:
    """Persist final packet state and update creative cooldown memory."""
    _write_task_packet(result_dir, task, result, payload)
    if task.category == "creative" and result.status in {"success", "partial_success"}:
        _update_creative_run_log(task.task_id)
    return result


def _sync_backlog_after_task(
    task: CodexTaskDef,
    state: OvernightCodexState,
    result: TaskResult,
) -> None:
    """Update approved backlog item state after task completion."""
    if not task.backlog_item_id:
        return
    if result.status == "success":
        backlog_status = "implemented"
    elif result.status == "queued":
        backlog_status = "scheduled"
    elif result.status in {"failed", "timeout", "usage_limited"}:
        backlog_status = "blocked"
    else:
        return
    note = result.error or result.summary
    update_backlog_status(
        task.backlog_item_id,
        status=backlog_status,
        run_id=state.run_id,
        note=note[:400] if note else "",
        patch_path=result.patch_path or "",
    )


def _should_trip_breaker(result: TaskResult) -> bool:
    """Return whether a result should count toward the hard failure breaker."""
    return result.failure_class in BREAKER_FAILURE_CLASSES


def _find_codex() -> str | None:
    """Find the Codex CLI."""
    found = shutil.which("codex")
    if found:
        normalized = found.replace("\\", "/")
        if sys.platform == "win32" or not normalized.startswith("/mnt/"):
            return found
    if sys.platform != "win32":
        for candidate in [
            Path.home() / ".local" / "bin" / "codex",
            Path("/usr/local/bin/codex"),
            Path("/usr/bin/codex"),
        ]:
            if candidate.exists():
                return str(candidate)
    if sys.platform == "win32":
        for candidate in [
            Path(os.environ.get("APPDATA", "")) / "npm" / "codex.cmd",
            Path(os.environ.get("LOCALAPPDATA", "")) / "npm" / "codex.cmd",
            Path.home() / "AppData" / "Roaming" / "npm" / "codex.cmd",
        ]:
            if candidate.exists():
                return str(candidate)
    return None


def _run_subprocess_safe(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 300,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess without risking Windows pipe deadlocks."""
    resolved_cmd = rewrite_python_command(cmd)
    proc = subprocess.Popen(
        resolved_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd or PROJECT_DIR),
        env=env,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate(timeout=10)
        raise subprocess.TimeoutExpired(resolved_cmd, timeout, output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(resolved_cmd, proc.returncode, stdout, stderr)


def log_decision(message: str, details: Any | None = None) -> None:
    """Append to the Codex decisions log."""
    entry = f"[{utc_now_iso()}] {message}"
    if details is not None:
        detail_text = json.dumps(details, ensure_ascii=False, default=str)
        entry += f"\n  Details: {detail_text[:1200]}"
    with DECISIONS_LOG.open("a", encoding="utf-8") as handle:
        handle.write(entry + "\n")


def _acquire_lock() -> None:
    """Prevent concurrent Codex overnight runs."""
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text(encoding="utf-8").strip())
            os.kill(old_pid, 0)
            raise RuntimeError(
                f"Another overnight_codex process is running with PID {old_pid}. "
                f"Delete {repo_rel(LOCK_FILE)} only if it is stale."
            )
        except OSError:
            log_decision("Removing stale Codex lock file", {"path": repo_rel(LOCK_FILE)})
        except ValueError:
            log_decision("Removing invalid Codex lock file", {"path": repo_rel(LOCK_FILE)})
    LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8")


def _release_lock() -> None:
    """Release the run lock."""
    if LOCK_FILE.exists():
        try:
            LOCK_FILE.unlink()
        except OSError:
            pass


def _write_heartbeat(state: OvernightCodexState, task_id: str, status: str, total: int) -> None:
    """Write a progress heartbeat."""
    payload = {
        "source": "overnight_codex",
        "pid": os.getpid(),
        "timestamp": utc_now_iso(),
        "last_task": task_id,
        "last_status": status,
        "completed": state.tasks_completed,
        "failed": state.tasks_failed,
        "queued": state.tasks_queued,
        "skipped": state.tasks_skipped,
        "remaining": total - len(state.results),
        "apply_mode": state.apply_mode,
        "consecutive_breaker_failures": state.consecutive_breaker_failures,
        "consecutive_timeouts": state.consecutive_timeouts,
        "failure_class_counts": dict(state.failure_class_counts),
    }
    write_json(HEARTBEAT_FILE, payload)


def _is_usage_limit_error(text: str | None) -> bool:
    """Return True when Codex reports a provider usage cap."""
    if not text:
        return False
    lowered = text.lower()
    return "usage limit" in lowered or "purchase more credits" in lowered


def run_baseline_tests() -> bool:
    """Run the baseline engine tests. Failure disables auto-apply."""
    for test_dir in (
        "engines/source/tests/",
        "engines/normalization/tests/",
        "engines/excerpting/tests/",
    ):
        result = _run_subprocess_safe(
            ["python", "-m", "pytest", test_dir, "-x", "-q", "--tb=no"],
            timeout=600,
        )
        if result.returncode != 0:
            log_decision(
                "Baseline tests failed; auto-apply disabled",
                {"test_dir": test_dir, "stdout": result.stdout[-800:]},
            )
            return False
    return True


def run_codex_smoke(codex_bin: str) -> bool:
    """Verify unattended Codex execution works before a long run starts."""
    smoke_dir = RESULTS_DIR / "_smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    schema_path = smoke_dir / "schema.json"
    output_path = smoke_dir / "output.json"
    write_json(
        schema_path,
        {
            "type": "object",
            "additionalProperties": False,
            "required": ["ok"],
            "properties": {"ok": {"type": "string"}},
        },
    )
    cmd = [
        codex_bin,
        "exec",
        "--ephemeral",
        "--full-auto",
        "-m",
        "gpt-5.4",
        "-s",
        "workspace-write",
        "--output-schema",
        str(schema_path),
        "-o",
        str(output_path),
        'Read CLAUDE.md and return a JSON object with {"ok":"yes"} only.',
    ]
    result = _run_subprocess_safe(cmd, timeout=120)
    if result.returncode != 0:
        log_decision("Codex smoke failed", {"stderr": result.stderr[-800:]})
        return False
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        log_decision("Codex smoke returned invalid JSON")
        return False
    value = str(payload.get("ok", "")).strip().lower()
    return value == "yes" or "yes" in value


def detect_active_claude_session() -> tuple[bool, list[str]]:
    """Detect live Claude activity and force queue-only when present."""
    notes: list[str] = []
    active = False

    def _is_wsl_runtime() -> bool:
        if sys.platform != "linux":
            return False
        try:
            return "microsoft" in Path("/proc/sys/kernel/osrelease").read_text(encoding="utf-8").lower()
        except OSError:
            return False

    def _check_recent_session_state(session_state: Path, note: str) -> None:
        nonlocal active
        if not session_state.exists():
            return
        try:
            modified = datetime.fromtimestamp(session_state.stat().st_mtime, tz=timezone.utc)
            age_s = (utc_now() - modified).total_seconds()
            if age_s < 30 * 60:
                active = True
                notes.append(note)
        except OSError:
            return

    windows_home = os.environ.get("KR_WINDOWS_HOME", "").strip()
    is_wsl = _is_wsl_runtime()

    if sys.platform == "win32":
        _check_recent_session_state(
            PROJECT_DIR / ".claude" / "session_state.json",
            ".claude/session_state.json was updated recently; assuming Claude session is active.",
        )
    elif is_wsl and windows_home:
        _check_recent_session_state(
            Path(windows_home) / ".claude" / "session_state.json",
            "Windows Claude session_state.json was updated recently; assuming Claude session is active.",
        )

    try:
        if sys.platform == "win32" or is_wsl:
            proc_result = _run_subprocess_safe(
                ["tasklist.exe", "/FI", "IMAGENAME eq claude.exe"],
                timeout=10,
            )
            lines = [line for line in proc_result.stdout.splitlines() if "claude.exe" in line.lower()]
            if lines:
                active = True
                notes.append("Detected running claude.exe processes; forcing queue-only mode.")
        else:
            proc_result = _run_subprocess_safe(["pgrep", "-x", "claude"], timeout=10)
            if proc_result.returncode == 0 and proc_result.stdout.strip():
                active = True
                notes.append("Detected running Claude processes; forcing queue-only mode.")
    except Exception:
        pass

    return active, notes


def determine_apply_mode() -> tuple[str, bool, bool, list[str], dict[str, str]]:
    """Determine whether the main worktree can be auto-applied into safely."""
    notes: list[str] = []
    authority = load_active_authority()
    baseline_clean = not git_status_porcelain()
    if not baseline_clean:
        notes.append("Main repo was dirty at launch; auto-apply disabled.")
    baseline_tests_passed = run_baseline_tests()
    if not baseline_tests_passed:
        notes.append("Baseline tests failed at launch; auto-apply disabled.")
    claude_active, claude_notes = detect_active_claude_session()
    notes.extend(claude_notes)
    apply_mode = "conditional_auto_apply" if baseline_clean and baseline_tests_passed else "queue_only"
    if claude_active:
        apply_mode = "queue_only"
    active_authority = authority.get("active_authority", "claude")
    runtime_mode = authority.get("runtime_mode", "shadow_setup")
    if active_authority != "codex":
        apply_mode = "queue_only"
        notes.append(f"Active authority is {active_authority}; forcing queue-only mode.")
    elif runtime_mode != "autonomous_codex":
        apply_mode = "queue_only"
        notes.append(f"Runtime mode is {runtime_mode}; forcing queue-only mode.")
    return apply_mode, baseline_clean, baseline_tests_passed, notes, authority


def preflight(skip_tests: bool = False) -> tuple[str, bool, bool, list[str], str, dict[str, str]]:
    """Run preflight checks and return launch policy."""
    codex_bin = _find_codex()
    if not codex_bin:
        raise RuntimeError("Codex CLI not found in PATH.")
    version = _run_subprocess_safe([codex_bin, "--version"], timeout=30)
    if version.returncode != 0:
        raise RuntimeError("Codex CLI did not respond to --version.")
    if not run_codex_smoke(codex_bin):
        raise RuntimeError("Codex unattended smoke test failed.")
    authority = load_active_authority()
    if skip_tests:
        apply_mode = "queue_only"
        notes = ["Baseline tests skipped explicitly; auto-apply disabled."]
        return apply_mode, False, False, notes, codex_bin, authority
    apply_mode, baseline_clean, baseline_tests_passed, notes, authority = determine_apply_mode()
    return apply_mode, baseline_clean, baseline_tests_passed, notes, codex_bin, authority


def save_state(state: OvernightCodexState) -> None:
    """Persist the orchestrator state."""
    write_json(STATE_FILE, asdict(state))


def load_state() -> OvernightCodexState | None:
    """Load a previous orchestrator state."""
    if not STATE_FILE.exists():
        return None
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    results = data.pop("results", {})
    notes = data.pop("notes", [])
    state = OvernightCodexState(**data)
    state.results = results
    state.notes = notes
    return state


def pick_next_ready(manifest: list[CodexTaskDef], state: OvernightCodexState) -> CodexTaskDef | None:
    """Pick the next executable task."""
    changed = True
    while changed:
        changed = False
        blocked_ids = {
            task_id
            for task_id, result in state.results.items()
            if result.get("status") in {"failed", "timeout", "partial_success", "skipped"}
        }
        bookend_ids = {task.task_id for task in manifest if task.bookend}
        for task in manifest:
            if task.task_id in state.results or task.task_id in bookend_ids:
                continue
            if any(dep in blocked_ids for dep in task.depends_on):
                state.results[task.task_id] = {"status": "skipped", "error": "dependency failed"}
                state.tasks_skipped += 1
                changed = True

    completed_ids = {
        task_id for task_id, result in state.results.items() if result.get("status") == "success"
    }
    resolved = set(state.results)
    regular: list[CodexTaskDef] = []
    bookend: list[CodexTaskDef] = []
    all_non_bookend_resolved = all(task.task_id in resolved for task in manifest if not task.bookend)
    for task in manifest:
        if task.task_id in resolved:
            continue
        if task.bookend:
            if all_non_bookend_resolved:
                bookend.append(task)
            continue
        if all(dep in completed_ids for dep in task.depends_on):
            regular.append(task)
    candidates = regular or bookend
    if not candidates:
        return None
    candidates.sort(
        key=lambda task: (
            task.priority,
            LANE_ORDER.get(task.lane, 9),
            -task.learning_value,
            COMPLEXITY_ORDER.get(task.estimated_complexity, 1),
            task.task_id,
        )
    )
    return candidates[0]


def build_prompt(task: CodexTaskDef) -> str:
    """Compose the final prompt passed to Codex."""
    return (
        f"TASK ID: {task.task_id}\n"
        f"TASK NAME: {task.name}\n"
        f"TASK CATEGORY: {task.category}\n\n"
        "Do the repository work below now.\n\n"
        f"{task.prompt}\n\n"
        "Boundaries:\n"
        f"- {'Read-only inspection only.' if task.write_policy == 'readonly' else 'Only bounded local code/test changes needed for this task.'}\n"
        "- You are a low-authority employee, not the architect or roadmap owner.\n"
        "- Ignore NEXT.md, AGENT_TEAM_HANDOFF.md, docs/superpowers/, overnight/, overnight_codex/, and .claude unless the task explicitly names them.\n"
        "- Never use this prompt or the orchestrator itself as evidence unless the task explicitly targets it.\n"
        "- Never run git commit/push/rebase/reset/checkout.\n"
        "- Do not spend time trying to bootstrap Python or launch long integration runs inside your sandbox; inspect code/tests locally and let the orchestrator perform host-side validation.\n\n"
        "Final response rules:\n"
        "- Do not acknowledge the mode or repeat the safety rules.\n"
        "- `summary` must contain repo-specific substance, not a generic acknowledgement.\n"
        "- `commands_run` and/or `evidence` must show what you actually inspected.\n"
        "- If you found no issues, say that explicitly and still include concrete evidence.\n"
        "- Return only the final JSON response that matches the provided schema."
    )


def _parse_structured_output(path: Path) -> dict[str, Any]:
    """Parse the structured final response."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Structured output must be a JSON object.")
    required = set(FINAL_RESPONSE_SCHEMA["required"])
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"Structured output missing fields: {missing}")
    if not payload.get("commands_run") and not payload.get("evidence"):
        raise ValueError("Structured output must include concrete commands_run or evidence.")
    summary = str(payload.get("summary", "")).strip().lower()
    if summary.startswith("mode noted") or summary.startswith("operating in"):
        raise ValueError("Summary is generic and non-substantive.")
    return payload


def _payload_contains_legacy_results(payload: dict[str, Any]) -> bool:
    """Return True when the task points at the legacy overnight results root."""
    serialized = json.dumps(payload, ensure_ascii=False)
    return LEGACY_RESULT_PREFIX in serialized.replace("\\", "/")


def _validate_task_payload(
    task: CodexTaskDef,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Reject structurally valid payloads that violate runtime policy."""
    if _payload_contains_legacy_results(payload):
        raise ValueError(
            "Payload referenced `overnight/results/`; overnight_codex tasks must not use the legacy overnight root."
        )
    if task.write_policy == "readonly" and payload.get("files_changed"):
        raise ValueError("Readonly tasks must return an empty `files_changed` list.")
    return payload


def _extract_markdown_section(text: str, title: str) -> str:
    """Extract a markdown section by title."""
    patterns = [
        rf"^\*\*{title}\*\*\s*$",
        rf"^##\s+{title}\s*$",
        rf"^###\s+{title}\s*$",
    ]
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if any(re.match(pattern, stripped, re.IGNORECASE) for pattern in patterns):
            start = index + 1
            break
    if start is None:
        return ""
    collected: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if re.match(r"^\*\*[A-Za-z ].*\*\*$", stripped) or re.match(r"^##\s+", stripped) or re.match(r"^###\s+", stripped):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def _parse_bullets(section_text: str) -> list[str]:
    """Parse bullet lines from markdown text."""
    items: list[str] = []
    for raw in section_text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped:
            items.append(stripped)
    return items


def _payload_from_markdown(task: CodexTaskDef, markdown_path: Path) -> dict[str, Any]:
    """Convert markdown fallback output into the structured payload shape."""
    text = markdown_path.read_text(encoding="utf-8")
    summary = _extract_markdown_section(text, "Summary").strip()
    if not summary:
        summary = text.strip()[:1200]
    evidence_section = _extract_markdown_section(text, "Evidence")
    findings_section = _extract_markdown_section(text, "Findings")
    actions_section = _extract_markdown_section(text, "Action Items")
    commands_section = _extract_markdown_section(text, "Commands")

    evidence = [{"path": "markdown_fallback", "detail": item} for item in _parse_bullets(evidence_section)] or [
        {"path": "markdown_fallback", "detail": "Markdown fallback used due structured-output failure."}
    ]
    findings = _parse_bullets(findings_section)
    commands_run = _parse_bullets(commands_section)
    action_items = [
        {
            "id": f"{safe_slug(task.task_id).upper()}-{index + 1}",
            "category": "FOLLOW_UP",
            "summary": item,
            "effort": "M",
            "priority": "MEDIUM",
        }
        for index, item in enumerate(_parse_bullets(actions_section))
    ]
    return {
        "task_status": "truncated",
        "summary": summary,
        "commands_run": commands_run,
        "evidence": evidence,
        "findings": findings,
        "action_items": action_items,
        "files_changed": [],
        "tests_run": [],
    }


def _write_result_artifacts(task: CodexTaskDef, result_dir: Path, payload: dict[str, Any]) -> None:
    """Persist the structured response into stable artifacts."""
    write_json(result_dir / "final_response.json", payload)
    write_json(result_dir / task.expected_artifact, payload)
    action_items = validate_action_items(payload.get("action_items", []))
    if task.category == "creative" and action_items:
        write_json(result_dir / "actionable.json", action_items)

    lines = [f"# {task.name}", "", payload.get("summary", ""), ""]
    if payload.get("findings"):
        lines.append("## Findings")
        lines.extend(f"- {item}" for item in payload["findings"])
        lines.append("")
    if payload.get("evidence"):
        lines.append("## Evidence")
        for evidence in payload["evidence"]:
            lines.append(f"- {evidence['path']}: {evidence['detail']}")
        lines.append("")
    if payload.get("files_changed"):
        lines.append("## Files Changed")
        lines.extend(f"- {item}" for item in payload["files_changed"])
        lines.append("")
    if payload.get("tests_run"):
        lines.append("## Tests Run")
        lines.extend(f"- {item}" for item in payload["tests_run"])
        lines.append("")
    if action_items:
        lines.append("## Action Items")
        for item in action_items:
            lines.append(
                f"- {item['id']} [{item['category']}] {item['summary']} "
                f"({item['effort']}, {item['priority']})"
            )
        lines.append("")
    atomic_write(result_dir / "summary.md", "\n".join(lines).rstrip() + "\n")


def _preserve_staged_artifacts(source_dir: Path, result_dir: Path) -> list[str]:
    """Copy partial task IO artifacts into the stable result directory."""
    preserved: list[str] = []
    for name in PARTIAL_ARTIFACT_NAMES:
        source = source_dir / name
        if not source.exists() or not source.is_file():
            continue
        target = result_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        preserved.append(repo_rel(target))
    return preserved


def _run_external_regression_task(task: CodexTaskDef, result_dir: Path) -> TaskResult:
    """Run the deterministic regression snapshot outside Codex."""
    start_time = utc_now_iso()
    started = time.time()
    payload: dict[str, Any] = {
        "task_status": "success",
        "summary": "Deterministic regression snapshot completed.",
        "commands_run": [],
        "evidence": [],
        "findings": [],
        "action_items": [],
        "files_changed": [],
        "tests_run": [],
    }
    failures: list[str] = []
    test_dirs = [
        "engines/source/tests/",
        "engines/normalization/tests/",
        "engines/excerpting/tests/",
    ]
    for test_dir in test_dirs:
        command = rewrite_python_command(["python", "-m", "pytest", test_dir, "-v", "--tb=short"])
        payload["commands_run"].append(" ".join(command))
        result = _run_subprocess_safe(command, timeout=1800)
        payload["tests_run"].append(f"{test_dir}: returncode={result.returncode}")
        if result.returncode == 0:
            payload["evidence"].append(
                {
                    "path": test_dir,
                    "detail": "Full engine test suite passed under host validation.",
                }
            )
        else:
            failures.append(f"{test_dir} failed")
            payload["findings"].append(f"{test_dir} failed regression validation.")
            payload["evidence"].append(
                {
                    "path": test_dir,
                    "detail": result.stdout[-1200:] or result.stderr[-1200:],
                }
            )
    if failures:
        payload["task_status"] = "failed"
        payload["summary"] = "Deterministic regression snapshot found failing engine tests."
    _write_result_artifacts(task, result_dir, payload)
    result = TaskResult(
        task_id=task.task_id,
        status="success" if not failures else "failed",
        start_time=start_time,
        end_time=utc_now_iso(),
        duration_s=round(time.time() - started, 1),
        summary=payload["summary"],
        artifact_path=repo_rel(result_dir / "final_response.json"),
        tests_run=list(payload["tests_run"]),
        commands_run=list(payload["commands_run"]),
        error="; ".join(failures) if failures else None,
        failure_class="validation_failed" if failures else None,
        recommended_next_actions=_recommend_next_actions(
            task=task,
            status="success" if not failures else "failed",
            failure_class="validation_failed" if failures else None,
            environment_notes=[],
        ),
    )
    return _finalize_task_result(task=task, result_dir=result_dir, result=result, payload=payload)


def _codex_exec(
    codex_bin: str,
    *,
    prompt: str,
    workdir: Path,
    sandbox_mode: str,
    output_path: Path,
    schema_path: Path,
    timeout_minutes: int,
) -> subprocess.CompletedProcess[str]:
    """Run codex exec in a fully unattended mode."""
    cmd = [
        codex_bin,
        "exec",
        "--ephemeral",
        "--full-auto",
        "-m",
        "gpt-5.4",
        "-s",
        sandbox_mode,
        "--output-schema",
        str(schema_path),
        "-o",
        str(output_path),
        prompt,
    ]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return _run_subprocess_safe(cmd, cwd=workdir, timeout=timeout_minutes * 60, env=env)


def _codex_review(codex_bin: str, worktree_path: Path, review_path: Path) -> subprocess.CompletedProcess[str]:
    """Run codex exec review on uncommitted worktree changes."""
    cmd = [
        codex_bin,
        "exec",
        "review",
        "--uncommitted",
        "--ephemeral",
        "--full-auto",
        "-m",
        "gpt-5.4",
        "-o",
        str(review_path),
    ]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return _run_subprocess_safe(cmd, cwd=worktree_path, timeout=600, env=env)


def _codex_exec_freeform(
    codex_bin: str,
    *,
    prompt: str,
    workdir: Path,
    sandbox_mode: str,
    output_path: Path,
    timeout_minutes: int,
) -> subprocess.CompletedProcess[str]:
    """Run codex exec without an output schema as a markdown fallback."""
    cmd = [
        codex_bin,
        "exec",
        "--ephemeral",
        "--full-auto",
        "-m",
        "gpt-5.4",
        "-s",
        sandbox_mode,
        "-o",
        str(output_path),
        prompt,
    ]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return _run_subprocess_safe(cmd, cwd=workdir, timeout=timeout_minutes * 60, env=env)


def prepare_worktree(task: CodexTaskDef, launch_head: str) -> tuple[Path, str]:
    """Create a clean per-task worktree."""
    checkout_token = _task_checkout_token(task.task_id)
    branch_name = f"overnight-codex-{checkout_token}-{int(time.time())}"
    worktree_path = WORKTREES_DIR / checkout_token
    if worktree_path.exists():
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)
    result = _run_subprocess_safe(
        ["git", "worktree", "add", "-f", "-b", branch_name, str(worktree_path), launch_head],
        timeout=120,
    )
    if result.returncode != 0:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)
        subprocess.run(
            ["git", "branch", "-D", branch_name],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        raise RuntimeError(
            f"Failed to create worktree for {task.task_id}: {_tail_process_output(result)}"
        )
    _run_subprocess_safe(
        ["git", "config", "user.name", "KR Overnight Codex"],
        cwd=worktree_path,
        timeout=30,
    )
    _run_subprocess_safe(
        ["git", "config", "user.email", "overnight-codex@kr.local"],
        cwd=worktree_path,
        timeout=30,
    )
    return worktree_path, branch_name


def prepare_readonly_workspace(task: CodexTaskDef, launch_head: str) -> Path:
    """Create a disposable detached worktree for a readonly task."""
    checkout_token = f"ro-{_task_checkout_token(task.task_id)}"
    worktree_path = WORKTREES_DIR / checkout_token
    if worktree_path.exists():
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)
    result = _run_subprocess_safe(
        ["git", "worktree", "add", "--detach", str(worktree_path), launch_head],
        timeout=120,
    )
    if result.returncode != 0:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)
        raise RuntimeError(
            f"Failed to create readonly workspace for {task.task_id}: {_tail_process_output(result)}"
        )
    return worktree_path


def cleanup_readonly_workspace(worktree_path: Path | None) -> None:
    """Remove the disposable readonly worktree after task completion."""
    if worktree_path is None:
        return
    subprocess.run(
        ["git", "worktree", "remove", "--force", str(worktree_path)],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    if worktree_path.exists():
        shutil.rmtree(worktree_path, ignore_errors=True)


def queue_patch(
    task: CodexTaskDef,
    worktree_path: Path,
    branch_name: str,
    base_head: str,
    commit_hash: str,
    reason: str,
) -> tuple[Path, Path]:
    """Create a queued patch and metadata file."""
    patch_path = QUEUE_DIR / f"{safe_slug(task.task_id)}.patch"
    metadata_path = QUEUE_DIR / f"{safe_slug(task.task_id)}.json"
    patch_result = _run_subprocess_safe(
        ["git", "format-patch", "-1", commit_hash, "--stdout"],
        cwd=worktree_path,
        timeout=60,
    )
    atomic_write(patch_path, patch_result.stdout)
    write_json(
        metadata_path,
        {
            "task_id": task.task_id,
            "branch_name": branch_name,
            "base_head": base_head,
            "commit_hash": commit_hash,
            "worktree_path": str(worktree_path),
            "patch_path": str(patch_path),
            "reason": reason,
            "created_at": utc_now_iso(),
        },
    )
    return patch_path, metadata_path


def _affected_engines(changed_files: list[str]) -> set[str]:
    """Infer affected engines from changed files."""
    engines: set[str] = set()
    for file_path in changed_files:
        parts = file_path.split("/")
        if len(parts) >= 3 and parts[0] == "engines":
            engines.add(parts[1])
        if parts and parts[0] == "shared":
            return set(PIPELINE_ORDER)
    return engines


def run_quality_gate(
    codex_bin: str,
    task: CodexTaskDef,
    worktree_path: Path,
    changed_files: list[str],
    result_dir: Path,
) -> tuple[bool, list[str], Path]:
    """Run post-task checks before any main-repo integration."""
    failures: list[str] = []
    review_path = result_dir / "codex_review.md"
    violations = has_forbidden_edits(changed_files)
    if violations:
        failures.append(f"Forbidden files changed: {violations}")
    if task.allowed_write_prefixes:
        unexpected = [
            path for path in changed_files
            if not any(path.replace("\\", "/").startswith(prefix) for prefix in task.allowed_write_prefixes)
        ]
        if unexpected:
            failures.append(f"Guarded task touched files outside allowlist: {unexpected}")
    deleted = _run_subprocess_safe(
        ["git", "diff", "--diff-filter=D", "--name-only"],
        cwd=worktree_path,
        timeout=30,
    )
    deleted_files = [line.strip() for line in deleted.stdout.splitlines() if line.strip()]
    if deleted_files:
        failures.append(f"Deleted files are not allowed: {deleted_files}")

    quality_gate_script = worktree_path / "scripts" / "quality_gate.py"
    if quality_gate_script.exists():
        engines = _affected_engines(changed_files)
        gate_cmd = [
            sys.executable,
            str(quality_gate_script),
            "--mode",
            task.gate_mode,
        ]
        if changed_files:
            gate_cmd.append("--paths")
            gate_cmd.extend(changed_files)
        for engine in sorted(engines):
            gate_cmd.extend(["--engine", engine])
        gate_result = _run_subprocess_safe(
            gate_cmd,
            cwd=worktree_path,
            timeout=2400,
        )
        if gate_result.returncode != 0:
            failures.append(f"quality gate failed: {_tail_process_output(gate_result)}")

    if ENABLE_STRICT_CODEX_REVIEW:
        review_result = _codex_review(codex_bin, worktree_path, review_path)
        if review_result.returncode != 0:
            failures.append(f"codex review failed: {review_result.stderr[-800:]}")

    return (len(failures) == 0, failures, review_path)


def _repo_still_safe_for_auto_apply(launch_head: str) -> tuple[bool, str]:
    """Decide whether the main repo can still accept automatic cherry-picks."""
    current_head = git_head()
    if current_head != launch_head:
        return False, "main HEAD changed during run"
    if git_status_porcelain():
        return False, "main repo became dirty during run"
    return True, ""


def _commit_worktree(task: CodexTaskDef, worktree_path: Path) -> str:
    """Commit guarded-write changes from a worktree."""
    _run_subprocess_safe(["git", "add", "--all"], cwd=worktree_path, timeout=60)
    diff_check = _run_subprocess_safe(
        ["git", "diff", "--cached", "--quiet"],
        cwd=worktree_path,
        timeout=30,
    )
    if diff_check.returncode == 0:
        return ""
    commit = _run_subprocess_safe(
        [
            "git",
            "commit",
            "-m",
            f"overnight_codex: {task.task_id}",
            "--author",
            "KR Overnight Codex <overnight-codex@kr.local>",
        ],
        cwd=worktree_path,
        timeout=60,
    )
    if commit.returncode != 0:
        raise RuntimeError(f"git commit failed in worktree for {task.task_id}: {commit.stderr[:400]}")
    return git_head(worktree_path)


def _auto_apply_commit(commit_hash: str) -> tuple[bool, str]:
    """Cherry-pick a verified worktree commit into the main repo."""
    result = _run_subprocess_safe(
        ["git", "cherry-pick", "--ff", commit_hash],
        cwd=PROJECT_DIR,
        timeout=120,
    )
    if result.returncode == 0:
        return True, ""
    _run_subprocess_safe(["git", "cherry-pick", "--abort"], cwd=PROJECT_DIR, timeout=30)
    return False, result.stderr[-800:]


def execute_task(
    task: CodexTaskDef,
    *,
    state: OvernightCodexState,
    codex_bin: str,
) -> TaskResult:
    """Execute a single task."""
    result_dir = RESULTS_DIR / task.task_id
    result_dir.mkdir(parents=True, exist_ok=True)
    if task.task_id == "val-test-regression":
        return _run_external_regression_task(task, result_dir)

    start = time.time()
    start_time = utc_now_iso()
    prompt = build_prompt(task)
    workdir = PROJECT_DIR
    branch_name: str | None = None
    worktree_path: Path | None = None
    readonly_guard: dict[str, Any] | None = None
    uses_worktree = task.write_policy == "guarded_write"
    sandbox_mode = task.sandbox_mode
    io_tempdir = tempfile.TemporaryDirectory(prefix=f"overnight_codex_{safe_slug(task.task_id)}_")
    io_dir = Path(io_tempdir.name)
    schema_path = io_dir / "output_schema.json"
    output_path = io_dir / task.expected_artifact
    write_json(schema_path, FINAL_RESPONSE_SCHEMA)
    finalized_once = False

    def finalize_result(result: TaskResult, payload: dict[str, Any] | None = None) -> TaskResult:
        nonlocal finalized_once
        finalized = _finalize_task_result(task=task, result_dir=result_dir, result=result, payload=payload)
        _sync_backlog_after_task(task, state, finalized)
        if not finalized_once:
            io_tempdir.cleanup()
            if not uses_worktree:
                cleanup_readonly_workspace(worktree_path)
            finalized_once = True
        return finalized

    if uses_worktree:
        try:
            worktree_path, branch_name = prepare_worktree(task, state.launch_head)
            workdir = worktree_path
        except Exception as exc:
            return finalize_result(
                TaskResult(
                    task_id=task.task_id,
                    status="failed",
                    start_time=start_time,
                    end_time=utc_now_iso(),
                    duration_s=round(time.time() - start, 1),
                    error=str(exc),
                    artifact_path=repo_rel(result_dir / task.expected_artifact),
                    branch_name=branch_name,
                    failure_class="infra_failure",
                    recommended_next_actions=_recommend_next_actions(
                        task=task,
                        status="failed",
                        failure_class="infra_failure",
                        environment_notes=[],
                    ),
                )
            )
    else:
        try:
            worktree_path = prepare_readonly_workspace(task, state.launch_head)
            workdir = worktree_path
            readonly_guard = _snapshot_readonly_guard()
        except Exception as exc:
            return finalize_result(
                TaskResult(
                    task_id=task.task_id,
                    status="failed",
                    start_time=start_time,
                    end_time=utc_now_iso(),
                    duration_s=round(time.time() - start, 1),
                    error=str(exc),
                    artifact_path=repo_rel(result_dir / task.expected_artifact),
                    failure_class="infra_failure",
                    recommended_next_actions=_recommend_next_actions(
                        task=task,
                        status="failed",
                        failure_class="infra_failure",
                        environment_notes=[],
                    ),
                )
            )

    payload: dict[str, Any] | None = None
    exec_result: subprocess.CompletedProcess[str] | None = None
    corrective_feedback = ""
    last_validation_error = ""
    for attempt in range(1, 4):
        attempt_prompt = prompt
        if corrective_feedback:
            attempt_prompt += f"\n\nCORRECTION FOR RETRY {attempt}:\n{corrective_feedback}"
        try:
            exec_result = _codex_exec(
                codex_bin,
                prompt=attempt_prompt,
                workdir=workdir,
                sandbox_mode=sandbox_mode,
                output_path=output_path,
                schema_path=schema_path,
                timeout_minutes=task.timeout_minutes,
            )
        except subprocess.TimeoutExpired:
            partial_artifacts = _preserve_staged_artifacts(io_dir, result_dir)
            status = "partial_success" if partial_artifacts else "timeout"
            return finalize_result(
                TaskResult(
                    task_id=task.task_id,
                    status=status,
                    start_time=start_time,
                    end_time=utc_now_iso(),
                    duration_s=round(time.time() - start, 1),
                    summary=(
                        "Timed out after preserving partial task output."
                        if partial_artifacts
                        else ""
                    ),
                    error=(
                        f"Task exceeded {task.timeout_minutes} minute timeout"
                        + (" (partial output preserved)" if partial_artifacts else "")
                    ),
                    artifact_path=repo_rel(result_dir / task.expected_artifact),
                    branch_name=branch_name,
                    failure_class="timeout",
                    partial_artifacts=partial_artifacts,
                    recommended_next_actions=_recommend_next_actions(
                        task=task,
                        status=status,
                        failure_class="timeout",
                        environment_notes=[],
                    ),
                )
            )
        except Exception as exc:
            return finalize_result(
                TaskResult(
                    task_id=task.task_id,
                    status="failed",
                    start_time=start_time,
                    end_time=utc_now_iso(),
                    duration_s=round(time.time() - start, 1),
                    error=str(exc),
                    artifact_path=repo_rel(result_dir / task.expected_artifact),
                    branch_name=branch_name,
                    failure_class="infra_failure",
                    recommended_next_actions=_recommend_next_actions(
                        task=task,
                        status="failed",
                        failure_class="infra_failure",
                        environment_notes=[],
                    ),
                )
            )

        if readonly_guard is not None:
            readonly_failures = _readonly_guard_failures(readonly_guard)
            if readonly_failures:
                return finalize_result(
                    TaskResult(
                        task_id=task.task_id,
                        status="failed",
                        start_time=start_time,
                        end_time=utc_now_iso(),
                        duration_s=round(time.time() - start, 1),
                        error="; ".join(readonly_failures)[:1800],
                        artifact_path=repo_rel(result_dir / task.expected_artifact),
                        failure_class="policy_blocked",
                        recommended_next_actions=_recommend_next_actions(
                            task=task,
                            status="failed",
                            failure_class="policy_blocked",
                            environment_notes=[],
                        ),
                    )
                )

        if exec_result.returncode != 0:
            error_text = _tail_process_output(exec_result)
            environment_notes = _environment_notes_from_texts([error_text])
            if _is_usage_limit_error(exec_result.stderr):
                status = "usage_limited"
                failure_class = "usage_limited"
            elif environment_notes:
                status = "failed"
                failure_class = "environment_blocked"
            else:
                status = "failed"
                failure_class = "task_failed"
            return finalize_result(
                TaskResult(
                    task_id=task.task_id,
                    status=status,
                    start_time=start_time,
                    end_time=utc_now_iso(),
                    duration_s=round(time.time() - start, 1),
                    error=error_text,
                    artifact_path=repo_rel(result_dir / task.expected_artifact),
                    branch_name=branch_name,
                    failure_class=failure_class,
                    environment_notes=environment_notes,
                    recommended_next_actions=_recommend_next_actions(
                        task=task,
                        status=status,
                        failure_class=failure_class,
                        environment_notes=environment_notes,
                    ),
                )
            )

        try:
            payload = _validate_task_payload(task, _parse_structured_output(output_path))
            break
        except Exception as exc:
            last_validation_error = str(exc)
            corrective_feedback = (
                f"Your previous response was rejected: {exc}. "
                "Inspect the repository with actual file reads or shell commands, then return "
                "repo-specific evidence and a substantive summary. Empty `commands_run` and "
                "empty `evidence` are invalid."
            )
            if attempt == 3:
                fallback_path = io_dir / "fallback.md"
                fallback_prompt = (
                    build_prompt(task)
                    + "\n\nStructured JSON retries failed. Do the work and return markdown with sections: "
                    "Summary, Evidence, Findings, Action Items, Commands."
                )
                try:
                    fallback_result = _codex_exec_freeform(
                        codex_bin,
                        prompt=fallback_prompt,
                        workdir=workdir,
                        sandbox_mode=sandbox_mode,
                        output_path=fallback_path,
                        timeout_minutes=task.timeout_minutes,
                    )
                except subprocess.TimeoutExpired:
                    partial_artifacts = _preserve_staged_artifacts(io_dir, result_dir)
                    status = "partial_success" if partial_artifacts else "timeout"
                    return finalize_result(
                        TaskResult(
                            task_id=task.task_id,
                            status=status,
                            start_time=start_time,
                            end_time=utc_now_iso(),
                            duration_s=round(time.time() - start, 1),
                            summary=(
                                "Timed out after preserving partial task output."
                                if partial_artifacts
                                else ""
                            ),
                            error=(
                                f"Task exceeded {task.timeout_minutes} minute timeout"
                                + (" (partial output preserved)" if partial_artifacts else "")
                            ),
                            artifact_path=repo_rel(result_dir / task.expected_artifact),
                            branch_name=branch_name,
                            failure_class="timeout",
                            partial_artifacts=partial_artifacts,
                            recommended_next_actions=_recommend_next_actions(
                                task=task,
                                status=status,
                                failure_class="timeout",
                                environment_notes=[],
                            ),
                        )
                    )
                if fallback_result.returncode != 0:
                    environment_notes = _environment_notes_from_texts([_tail_process_output(fallback_result)])
                    if _is_usage_limit_error(fallback_result.stderr):
                        status = "usage_limited"
                        failure_class = "usage_limited"
                    elif environment_notes:
                        status = "failed"
                        failure_class = "environment_blocked"
                    else:
                        status = "failed"
                        failure_class = "validation_failed"
                    return finalize_result(
                        TaskResult(
                            task_id=task.task_id,
                            status=status,
                            start_time=start_time,
                            end_time=utc_now_iso(),
                            duration_s=round(time.time() - start, 1),
                            error=f"Invalid structured output: {last_validation_error}",
                            artifact_path=repo_rel(result_dir / task.expected_artifact),
                            branch_name=branch_name,
                            failure_class=failure_class,
                            environment_notes=environment_notes,
                            recommended_next_actions=_recommend_next_actions(
                                task=task,
                                status=status,
                                failure_class=failure_class,
                                environment_notes=environment_notes,
                            ),
                        )
                    )
                try:
                    payload = _validate_task_payload(task, _payload_from_markdown(task, fallback_path))
                except ValueError as exc:
                    environment_notes = _environment_notes_from_texts([str(exc)])
                    return finalize_result(
                        TaskResult(
                            task_id=task.task_id,
                            status="failed",
                            start_time=start_time,
                            end_time=utc_now_iso(),
                            duration_s=round(time.time() - start, 1),
                            error=f"Invalid markdown fallback output: {exc}",
                            artifact_path=repo_rel(result_dir / task.expected_artifact),
                            branch_name=branch_name,
                            failure_class="validation_failed",
                            environment_notes=environment_notes,
                            recommended_next_actions=_recommend_next_actions(
                                task=task,
                                status="failed",
                                failure_class="validation_failed",
                                environment_notes=environment_notes,
                            ),
                        )
                    )
                break

    assert payload is not None

    _write_result_artifacts(task, result_dir, payload)
    summary = str(payload.get("summary", ""))[:2000]
    environment_notes = _extract_environment_notes(payload)
    recommended_next_actions = _recommend_next_actions(
        task=task,
        status="success",
        failure_class=None,
        environment_notes=environment_notes,
    )
    novelty_score = None
    if task.category == "creative":
        novelty_score = round(
            min(1.0, (len(payload.get("findings", [])) + len(payload.get("action_items", []))) / 6.0),
            2,
        )

    if not uses_worktree:
        return finalize_result(
            TaskResult(
                task_id=task.task_id,
                status="success",
                start_time=start_time,
                end_time=utc_now_iso(),
                duration_s=round(time.time() - start, 1),
                summary=summary,
                artifact_path=repo_rel(result_dir / task.expected_artifact),
                tests_run=list(payload.get("tests_run", [])),
                commands_run=list(payload.get("commands_run", [])),
                environment_notes=environment_notes,
                recommended_next_actions=recommended_next_actions,
                confidence="medium" if task.category == "creative" else None,
                novelty_score=novelty_score,
            ),
            payload=payload,
        )

    assert worktree_path is not None
    assert branch_name is not None
    changed_files = worktree_changed_files(worktree_path)
    if not changed_files:
        return finalize_result(
            TaskResult(
                task_id=task.task_id,
                status="success",
                start_time=start_time,
                end_time=utc_now_iso(),
                duration_s=round(time.time() - start, 1),
                summary=summary,
                artifact_path=repo_rel(result_dir / task.expected_artifact),
                branch_name=branch_name,
                tests_run=list(payload.get("tests_run", [])),
                commands_run=list(payload.get("commands_run", [])),
                environment_notes=environment_notes,
                recommended_next_actions=recommended_next_actions,
            ),
            payload=payload,
        )

    gate_passed, gate_failures, review_path = run_quality_gate(
        codex_bin, task, worktree_path, changed_files, result_dir
    )
    if not gate_passed:
        log_decision(f"Quality gate failed for {task.task_id}", gate_failures)
        failure_class = _classify_quality_gate_failures(gate_failures)
        return finalize_result(
            TaskResult(
                task_id=task.task_id,
                status="failed",
                start_time=start_time,
                end_time=utc_now_iso(),
                duration_s=round(time.time() - start, 1),
                summary=summary,
                error="; ".join(gate_failures)[:1800],
                artifact_path=repo_rel(result_dir / task.expected_artifact),
                branch_name=branch_name,
                review_path=repo_rel(review_path),
                files_changed=changed_files,
                tests_run=list(payload.get("tests_run", [])),
                commands_run=list(payload.get("commands_run", [])),
                failure_class=failure_class,
                environment_notes=environment_notes,
                recommended_next_actions=_recommend_next_actions(
                    task=task,
                    status="failed",
                    failure_class=failure_class,
                    environment_notes=environment_notes,
                ),
            ),
            payload=payload,
        )

    commit_hash = _commit_worktree(task, worktree_path)
    if not commit_hash:
        return finalize_result(
            TaskResult(
                task_id=task.task_id,
                status="failed",
                start_time=start_time,
                end_time=utc_now_iso(),
                duration_s=round(time.time() - start, 1),
                summary=summary,
                error=(
                    "No durable staged diff remained after git add; "
                    "the write path produced only non-persisting changes."
                ),
                artifact_path=repo_rel(result_dir / task.expected_artifact),
                branch_name=branch_name,
                files_changed=changed_files,
                tests_run=list(payload.get("tests_run", [])),
                commands_run=list(payload.get("commands_run", [])),
                failure_class="validation_failed",
                environment_notes=environment_notes,
                recommended_next_actions=_recommend_next_actions(
                    task=task,
                    status="failed",
                    failure_class="validation_failed",
                    environment_notes=environment_notes,
                ),
            ),
            payload=payload,
        )
    auto_apply = False
    patch_path: Path | None = None
    queue_reason = ""
    queued_only = False

    if state.apply_mode == "conditional_auto_apply":
        repo_safe, queue_reason = _repo_still_safe_for_auto_apply(state.launch_head)
        if repo_safe and commit_hash:
            auto_apply, cherry_pick_error = _auto_apply_commit(commit_hash)
            if not auto_apply:
                queue_reason = f"auto-apply failed: {cherry_pick_error[:400]}"
        else:
            queue_reason = queue_reason or "main repo not safe for auto-apply"
    else:
        queue_reason = "launch policy is queue_only"

    if commit_hash and not auto_apply:
        patch_path, _ = queue_patch(
            task,
            worktree_path,
            branch_name,
            state.launch_head,
            commit_hash,
            queue_reason,
        )
        queued_only = True

    status = "queued" if queued_only else "success"
    return finalize_result(
        TaskResult(
            task_id=task.task_id,
            status=status,
            start_time=start_time,
            end_time=utc_now_iso(),
            duration_s=round(time.time() - start, 1),
            summary=summary,
            artifact_path=repo_rel(result_dir / task.expected_artifact),
            branch_name=branch_name,
            patch_path=repo_rel(patch_path) if patch_path else None,
            commit_hash=commit_hash or None,
            review_path=repo_rel(review_path),
            auto_applied=auto_apply,
            files_changed=changed_files,
            tests_run=list(payload.get("tests_run", [])),
            commands_run=list(payload.get("commands_run", [])),
            queued_only=queued_only,
            queue_reason=queue_reason or None,
            environment_notes=environment_notes,
            recommended_next_actions=_recommend_next_actions(
                task=task,
                status=status,
                failure_class=None,
                environment_notes=environment_notes,
                patch_path=repo_rel(patch_path) if patch_path else None,
            ),
        ),
        payload=payload,
    )
    


def _load_findings_registry_summary() -> tuple[int, list[dict[str, Any]]]:
    """Load a compact summary of the findings registry."""
    if not FINDINGS_REGISTRY_FILE.exists():
        return 0, []
    try:
        data = json.loads(FINDINGS_REGISTRY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0, []
    items = data.get("items", {})
    if not isinstance(items, dict):
        return 0, []
    records = [record for record in items.values() if isinstance(record, dict)]
    records.sort(key=lambda record: (record.get("last_seen", ""), record.get("id", "")), reverse=True)
    return len(records), records[:5]


def _current_signal_records(
    state: OvernightCodexState,
    manifest: list[CodexTaskDef],
) -> list[dict[str, Any]]:
    """Build issue-like records for morning reporting."""
    by_id = {task.task_id: task for task in manifest}
    signals: list[dict[str, Any]] = []
    for task_id, result in state.results.items():
        task = by_id.get(task_id)
        if not task:
            continue
        status = str(result.get("status", "pending"))
        if status not in SIGNAL_STATUSES and status != "skipped":
            continue
        signals.append(
            {
                "task_id": task_id,
                "name": task.name,
                "category": task.category,
                "lane": task.lane,
                "priority": task.priority,
                "learning_value": task.learning_value,
                "status": status,
                "failure_class": result.get("failure_class"),
                "error": result.get("error"),
                "summary": result.get("summary", ""),
                "patch_path": result.get("patch_path"),
                "queue_reason": result.get("queue_reason"),
                "environment_notes": list(result.get("environment_notes", [])),
                "recommended_next_actions": list(result.get("recommended_next_actions", [])),
            }
        )
    return signals


def _split_new_vs_recurring(
    signals: list[dict[str, Any]],
    previous_snapshot: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Partition current signals by whether they existed in the prior snapshot."""
    if not previous_snapshot:
        return signals, []
    previous_tasks = previous_snapshot.get("tasks", {})
    if not isinstance(previous_tasks, dict):
        return signals, []
    new_signals: list[dict[str, Any]] = []
    recurring: list[dict[str, Any]] = []
    for signal in signals:
        previous = previous_tasks.get(signal["task_id"])
        if (
            isinstance(previous, dict)
            and previous.get("status") == signal["status"]
            and previous.get("failure_class") == signal["failure_class"]
        ):
            recurring.append(signal)
        else:
            new_signals.append(signal)
    return new_signals, recurring


def generate_morning_report(
    state: OvernightCodexState,
    manifest: list[CodexTaskDef],
    previous_snapshot: dict[str, Any] | None = None,
) -> None:
    """Generate an action-first morning report."""
    snapshot = _build_run_snapshot(state, manifest)
    backlog_summary = snapshot.get("backlog", {})
    current_signals = _current_signal_records(state, manifest)
    new_signals, recurring_signals = _split_new_vs_recurring(current_signals, previous_snapshot)
    findings_count, recent_finding_items = _load_findings_registry_summary()

    def signal_rank(signal: dict[str, Any]) -> tuple[int, int, int]:
        status_rank = {
            "usage_limited": 0,
            "failed": 1,
            "timeout": 2,
            "partial_success": 3,
            "queued": 4,
            "skipped": 5,
        }
        failure_rank = {
            "infra_failure": 0,
            "policy_blocked": 1,
            "validation_failed": 2,
            "environment_blocked": 3,
            "usage_limited": 4,
            "task_failed": 5,
            None: 6,
        }
        return (
            status_rank.get(signal["status"], 9),
            failure_rank.get(signal.get("failure_class"), 9),
            signal["priority"],
        )

    top_signals = sorted(current_signals, key=signal_rank)[:5]
    blocked_work = [
        signal
        for signal in current_signals
        if signal["status"] == "skipped"
        or signal.get("failure_class") in {"infra_failure", "policy_blocked", "environment_blocked", "validation_failed"}
    ]
    patch_queue = [signal for signal in current_signals if signal["status"] == "queued"]
    movement = [
        task
        for task in manifest
        if task.category in {"review", "validation", "test", "spec"}
        and state.results.get(task.task_id, {}).get("status") in {"success", "partial_success"}
    ]
    environment_issues: list[str] = []
    for signal in current_signals:
        if signal.get("failure_class") == "infra_failure":
            environment_issues.append(
                f"`{signal['task_id']}` hit an infrastructure failure: {signal.get('error', 'unknown')}"
            )
        for note in signal.get("environment_notes", []):
            message = f"`{signal['task_id']}`: {note}"
            if message not in environment_issues:
                environment_issues.append(message)

    next_actions: list[str] = []
    for signal in top_signals + patch_queue + blocked_work:
        for action in signal.get("recommended_next_actions", []):
            if action not in next_actions:
                next_actions.append(action)
    next_actions = next_actions[:3]

    previous_summary = previous_snapshot.get("summary", {}) if previous_snapshot else {}
    prev_completed = int(previous_summary.get("completed", 0)) if isinstance(previous_summary, dict) else 0
    prev_failed = int(previous_summary.get("failed", 0)) if isinstance(previous_summary, dict) else 0
    prev_queued = int(previous_summary.get("queued", 0)) if isinstance(previous_summary, dict) else 0

    lines = [f"# Overnight Codex Report — {state.run_id}", ""]
    lines.append(f"- Active authority: `{state.active_authority}`")
    lines.append(f"- Runtime mode: `{state.runtime_mode}`")
    lines.append(f"- Status: **{state.status.upper()}**")
    lines.append(f"- Apply mode: `{state.apply_mode}`")
    lines.append(f"- Launch head: `{state.launch_head[:8]}`")
    lines.append(
        f"- Tasks: {state.tasks_completed} completed, {state.tasks_failed} failed, "
        f"{state.tasks_queued} queued, {state.tasks_skipped} skipped"
    )
    lines.append(
        f"- Delta vs previous run: completed {state.tasks_completed - prev_completed:+d}, "
        f"failed {state.tasks_failed - prev_failed:+d}, queued {state.tasks_queued - prev_queued:+d}"
    )
    if isinstance(backlog_summary, dict):
        lines.append(
            f"- Backlog movement: +{backlog_summary.get('created_this_run', 0)} proposed, "
            f"+{backlog_summary.get('approved_this_run', 0)} approved, "
            f"+{backlog_summary.get('implemented_this_run', 0)} implemented"
        )
    if state.notes:
        lines.append("")
        lines.append("## Launch Notes")
        lines.extend(f"- {note}" for note in state.notes)

    if top_signals:
        lines.append("")
        lines.append("## Tonight's Top Signals")
        for signal in top_signals:
            detail = signal.get("error") or signal.get("summary") or "No detail recorded."
            lines.append(
                f"- `{signal['task_id']}` [{signal['status']}/{signal.get('failure_class') or 'none'}]: {detail}"
            )

    lines.append("")
    lines.append("## New vs Recurring")
    lines.append(f"- New signals this run: {len(new_signals)}")
    lines.append(f"- Recurring signals from the previous snapshot: {len(recurring_signals)}")
    if new_signals[:3]:
        lines.extend(f"- New: `{signal['task_id']}` ({signal['status']})" for signal in new_signals[:3])
    if recurring_signals[:3]:
        lines.extend(f"- Recurring: `{signal['task_id']}` ({signal['status']})" for signal in recurring_signals[:3])

    if blocked_work:
        lines.append("")
        lines.append("## Blocked Work")
        for signal in blocked_work[:5]:
            detail = signal.get("error") or signal.get("summary") or "No detail recorded."
            lines.append(
                f"- `{signal['task_id']}` [{signal.get('failure_class') or signal['status']}]: {detail}"
            )

    if patch_queue:
        lines.append("")
        lines.append("## Patch Queue")
        for signal in patch_queue:
            lines.append(
                f"- `{signal['task_id']}` -> `{signal.get('patch_path', 'n/a')}` "
                f"({signal.get('queue_reason', 'queued')})"
            )

    if movement:
        lines.append("")
        lines.append("## Coverage And Validation Movement")
        for task in movement[:8]:
            result = state.results.get(task.task_id, {})
            lines.append(f"- `{task.task_id}` [{task.category}/{task.lane}]: {result.get('summary', task.name)}")

    if isinstance(backlog_summary, dict):
        counts = backlog_summary.get("counts", {})
        lines.append("")
        lines.append("## Backlog State")
        lines.append(f"- Total items: {backlog_summary.get('total', 0)}")
        lines.append(f"- Proposed: {counts.get('proposed', 0)}")
        lines.append(f"- Approved: {counts.get('approved', 0)}")
        lines.append(f"- Scheduled: {counts.get('scheduled', 0)}")
        lines.append(f"- Implemented: {counts.get('implemented', 0)}")
        lines.append(f"- Blocked: {counts.get('blocked', 0)}")
        lines.append(f"- Superseded: {counts.get('superseded', 0)}")

    if next_actions:
        lines.append("")
        lines.append("## Recommended Next 3 Actions")
        lines.extend(f"- {action}" for action in next_actions)

    if environment_issues:
        lines.append("")
        lines.append("## Environment And Infra Issues")
        lines.extend(f"- {issue}" for issue in environment_issues[:6])

    lines.append("")
    lines.append("## Findings Registry")
    lines.append(f"- Known tracked findings: {findings_count}")
    if recent_finding_items:
        for item in recent_finding_items[:3]:
            lines.append(
                f"- `{item.get('id', 'unknown')}`: {item.get('summary', 'No summary')} "
                f"(seen {item.get('occurrences', 1)} times)"
            )

    lines.append("")
    lines.append("## Snapshot")
    lines.append(
        f"- Snapshot file: `overnight_codex/run_snapshots/{_snapshot_filename(state.started_at)}`"
    )
    lines.append(
        f"- Failure classes this run: {snapshot['summary']['failure_class_counts'] or 'none'}"
    )

    atomic_write(MORNING_REPORT, "\n".join(lines).rstrip() + "\n")


def maybe_append_findings() -> None:
    """Append validated creative findings into the Codex tracker."""
    try:
        try:
            from scripts.append_codex_findings import append_findings
        except ImportError:
            from append_codex_findings import append_findings
        appended = append_findings()
        if appended:
            log_decision("Appended Codex creative findings", {"count": appended})
    except Exception as exc:
        log_decision("Failed to append Codex findings", {"error": str(exc)})


def ingest_to_kb(run_id: str) -> None:
    """Ingest Codex results into the autonomous KB for dashboard visibility."""
    try:
        try:
            from scripts.codex_kb_bridge import ingest_codex_results
        except ImportError:
            from codex_kb_bridge import ingest_codex_results
        stats = ingest_codex_results(run_id)
        log_decision("Ingested Codex results into KB", stats)
    except Exception as exc:
        log_decision("Failed to ingest into KB", {"error": str(exc)})


def sync_backlog(run_id: str) -> None:
    """Refresh the canonical backlog from results and legacy queues."""
    try:
        summary = sync_backlog_from_artifacts(run_id)
        log_decision("Synchronized overnight_codex backlog", summary)
    except Exception as exc:
        log_decision("Failed to synchronize overnight_codex backlog", {"error": str(exc)})


def run_overnight(
    *,
    hours: float,
    manifest_path: Path | None,
    single_task: str | None,
    dry_run: bool,
    resume: bool,
    skip_lock: bool,
    skip_preflight: bool,
) -> None:
    """Run the isolated Codex overnight session."""
    ensure_runtime_dirs()
    print("=== KR Overnight Codex ===")
    print(f"Project: {PROJECT_DIR}")
    print(f"Duration target: {hours} hours")
    print()

    sync_backlog(utc_now().strftime("%Y-%m-%d"))

    if manifest_path and manifest_path.exists():
        manifest = load_manifest(manifest_path)
        print(f"Loaded {len(manifest)} tasks from {repo_rel(manifest_path)}")
    else:
        generator = PROJECT_DIR / "scripts" / "overnight_codex_task_generator.py"
        gen = _run_subprocess_safe(
            ["python", str(generator), "--output", str(OVERNIGHT_CODEX_DIR / "manifest.json")],
            timeout=180,
        )
        if gen.returncode != 0:
            raise RuntimeError(f"Manifest generation failed: {gen.stderr[:400]}")
        manifest = load_manifest(OVERNIGHT_CODEX_DIR / "manifest.json")
        print(f"Generated {len(manifest)} tasks")

    if single_task:
        manifest = [task for task in manifest if task.task_id == single_task]
        if not manifest:
            raise RuntimeError(f"Task {single_task!r} was not found in the manifest.")

    if dry_run:
        print("=== DRY RUN ===")
        for task in sorted(
            manifest,
            key=lambda item: (item.priority, COMPLEXITY_ORDER.get(item.estimated_complexity, 1), item.task_id),
        ):
            deps = f" | depends: {', '.join(task.depends_on)}" if task.depends_on else ""
            print(
                f"  P{task.priority} [{task.write_policy}/{task.sandbox_mode}] "
                f"{task.task_id}: {task.name}{deps}"
            )
        return

    if not skip_lock:
        _acquire_lock()
    try:
        if skip_preflight:
            codex_bin = _find_codex()
            if not codex_bin:
                raise RuntimeError("Codex CLI not found in PATH.")
            apply_mode = "queue_only"
            baseline_clean = False
            baseline_tests_passed = False
            authority = load_active_authority()
            notes = ["Preflight skipped explicitly; auto-apply disabled."]
        else:
            apply_mode, baseline_clean, baseline_tests_passed, notes, codex_bin, authority = preflight()

        deadline = utc_now() + timedelta(hours=hours)
        previous = load_state() if resume else None
        if previous:
            state = previous
            state.status = "running"
            state.deadline = deadline.isoformat()
            state.apply_mode = apply_mode
            state.baseline_clean = baseline_clean
            state.baseline_tests_passed = baseline_tests_passed
            state.active_authority = authority.get("active_authority", state.active_authority)
            state.runtime_mode = authority.get("runtime_mode", state.runtime_mode)
            state.notes.extend(note for note in notes if note not in state.notes)
            log_decision("Resuming previous overnight_codex state")
            _append_event(
                "run_resumed",
                {
                    "run_id": state.run_id,
                    "started_at": state.started_at,
                    "resolved_tasks": len(state.results),
                },
            )
        else:
            for path in (STATE_FILE, PROGRESS_FILE, DECISIONS_LOG, HEARTBEAT_FILE):
                if path.exists():
                    path.unlink()
            state = OvernightCodexState(
                run_id=utc_now().strftime("%Y-%m-%d"),
                started_at=utc_now_iso(),
                deadline=deadline.isoformat(),
                launch_head=git_head(),
                apply_mode=apply_mode,
                baseline_clean=baseline_clean,
                baseline_tests_passed=baseline_tests_passed,
                active_authority=authority.get("active_authority", "claude"),
                runtime_mode=authority.get("runtime_mode", "shadow_setup"),
                notes=notes,
            )
            log_decision(
                "overnight_codex session started",
                {
                    "tasks": len(manifest),
                    "apply_mode": apply_mode,
                    "active_authority": state.active_authority,
                    "runtime_mode": state.runtime_mode,
                    "authority_file": repo_rel(ACTIVE_AUTHORITY_FILE),
                    "baseline_clean": baseline_clean,
                    "baseline_tests_passed": baseline_tests_passed,
                },
            )
            _append_event(
                "run_started",
                {
                    "run_id": state.run_id,
                    "started_at": state.started_at,
                    "manifest_task_count": len(manifest),
                    "apply_mode": apply_mode,
                    "baseline_clean": baseline_clean,
                    "baseline_tests_passed": baseline_tests_passed,
                },
            )

        save_state(state)
        write_progress_file(state, manifest)

        shutdown_requested = False

        def handle_signal(signum: int, frame: Any) -> None:
            nonlocal shutdown_requested
            shutdown_requested = True
            log_decision("Shutdown requested", {"signal": signum})

        signal.signal(signal.SIGINT, handle_signal)
        if hasattr(signal, "SIGTERM"):
            try:
                signal.signal(signal.SIGTERM, handle_signal)
            except (AttributeError, OSError, ValueError):
                pass
        if sys.platform == "win32":
            try:
                signal.signal(signal.SIGBREAK, handle_signal)  # type: ignore[attr-defined]
            except (AttributeError, OSError):
                pass

        start_monotonic = time.monotonic()
        max_seconds = hours * 3600
        timeout_overrides: dict[str, float] = {}

        while not shutdown_requested:
            remaining = max_seconds - (time.monotonic() - start_monotonic)
            if remaining <= 0:
                log_decision("Time limit reached")
                break
            if _failure_breaker_tripped(state):
                log_decision(
                    "Circuit breaker tripped on repeated unhealthy runtime failures",
                    {
                        "consecutive_failures": state.consecutive_failures,
                        "consecutive_breaker_failures": state.consecutive_breaker_failures,
                        "consecutive_timeouts": state.consecutive_timeouts,
                    },
                )
                state.status = "stopped"
                break

            task = pick_next_ready(manifest, state)
            if task is None:
                log_decision("All tasks resolved or blocked")
                break

            if _requires_shadow_setup_restrictions(state):
                allowed, reason = _shadow_setup_allows_task(task)
                if not allowed:
                    state.results[task.task_id] = {"status": "skipped", "error": reason}
                    state.tasks_skipped += 1
                    save_state(state)
                    write_progress_file(state, manifest)
                    continue

            original_timeout = task.timeout_minutes
            scale = timeout_overrides.get(task.category, 1.0)
            if task.estimated_complexity == "high":
                scale *= 1.4
            task.timeout_minutes = min(MAX_TIMEOUT_MINUTES, max(1, int(task.timeout_minutes * scale)))
            if remaining < task.timeout_minutes * 60:
                state.results[task.task_id] = {"status": "skipped", "error": "insufficient time"}
                state.tasks_skipped += 1
                _append_event(
                    "task_skipped",
                    {
                        "run_id": state.run_id,
                        "task_id": task.task_id,
                        "status": "skipped",
                        "reason": "insufficient_time",
                        "remaining_seconds": round(remaining, 1),
                    },
                )
                save_state(state)
                write_progress_file(state, manifest)
                continue

            print(
                f">>> [{task.priority}] {task.task_id}: {task.name} "
                f"({task.write_policy}, {task.timeout_minutes}m)"
            )
            _append_event(
                "task_started",
                {
                    "run_id": state.run_id,
                    "task_id": task.task_id,
                    "lane": task.lane,
                    "category": task.category,
                    "write_policy": task.write_policy,
                    "timeout_minutes": task.timeout_minutes,
                    "learning_value": task.learning_value,
                },
            )
            result = execute_task(task, state=state, codex_bin=codex_bin)
            task.timeout_minutes = original_timeout

            state.results[task.task_id] = asdict(result)
            if result.failure_class:
                state.failure_class_counts[result.failure_class] = (
                    state.failure_class_counts.get(result.failure_class, 0) + 1
                )
            if result.status == "success":
                state.tasks_completed += 1
                state.consecutive_failures = 0
                state.consecutive_timeouts = 0
                state.consecutive_breaker_failures = 0
            elif result.status == "queued":
                state.tasks_queued += 1
                state.consecutive_failures = 0
                state.consecutive_timeouts = 0
                state.consecutive_breaker_failures = 0
            elif result.status == "partial_success":
                state.tasks_completed += 1
                state.consecutive_failures = 0
                state.consecutive_timeouts = 0
                state.consecutive_breaker_failures = 0
            elif result.status == "usage_limited":
                state.tasks_failed += 1
                state.consecutive_failures += 1
                state.consecutive_breaker_failures += 1
                state.status = "stopped"
                log_decision("Codex usage limit reached; stopping run", {"task_id": task.task_id})
            elif result.status == "timeout":
                state.tasks_failed += 1
                state.consecutive_failures += 1
                state.consecutive_timeouts += 1
                state.consecutive_breaker_failures = 0
            else:
                state.tasks_failed += 1
                state.consecutive_failures += 1
                if _should_trip_breaker(result):
                    state.consecutive_breaker_failures += 1
                else:
                    state.consecutive_breaker_failures = 0
                state.consecutive_timeouts = 0

            if result.failure_class == "timeout" and result.status in {"timeout", "partial_success"}:
                timeout_overrides[task.category] = timeout_overrides.get(task.category, 1.0) + 0.5
            elif result.status == "success":
                timeout_overrides.pop(task.category, None)

            save_state(state)
            write_progress_file(state, manifest)
            _write_heartbeat(state, task.task_id, result.status, len(manifest))
            _append_event(
                "task_finished",
                {
                    "run_id": state.run_id,
                    "task_id": task.task_id,
                    "status": result.status,
                    "failure_class": result.failure_class,
                    "duration_s": result.duration_s,
                    "queued_only": result.queued_only,
                    "partial_artifacts": list(result.partial_artifacts),
                    "environment_notes": list(result.environment_notes),
                },
            )
            print(f"    {result.status.upper()}: {result.summary[:140]}")
            if result.status == "usage_limited":
                break

        if state.status == "running":
            state.status = "completed"
        save_state(state)
        write_progress_file(state, manifest)
        sync_backlog(state.run_id)
        maybe_append_findings()
        ingest_to_kb(state.run_id)
        previous_snapshot = _load_previous_snapshot(state.started_at)
        generate_morning_report(state, manifest, previous_snapshot)
        snapshot_path = _write_run_snapshot(state, manifest)
        _append_event(
            "run_finished",
            {
                "run_id": state.run_id,
                "status": state.status,
                "snapshot_path": repo_rel(snapshot_path),
                "completed": state.tasks_completed,
                "failed": state.tasks_failed,
                "queued": state.tasks_queued,
                "skipped": state.tasks_skipped,
            },
        )
        print()
        print(f"Run status: {state.status}")
        print(f"Morning report: {repo_rel(MORNING_REPORT)}")
    finally:
        if not skip_lock:
            _release_lock()


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Run the isolated Codex overnight runtime")
    parser.add_argument("--hours", type=float, default=8.0, help="Maximum runtime in hours")
    parser.add_argument("--manifest", type=str, help="Optional path to manifest JSON")
    parser.add_argument("--task", type=str, help="Run a single task by id")
    parser.add_argument("--dry-run", action="store_true", help="Print the task plan and exit")
    parser.add_argument("--resume", action="store_true", help="Resume from overnight_codex/state.json")
    parser.add_argument("--skip-lock", action="store_true", help="Skip the Codex run lock")
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip preflight and force queue-only mode",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest) if args.manifest else None
    if manifest_path and not manifest_path.is_absolute():
        manifest_path = PROJECT_DIR / manifest_path

    run_overnight(
        hours=args.hours,
        manifest_path=manifest_path,
        single_task=args.task,
        dry_run=args.dry_run,
        resume=args.resume,
        skip_lock=args.skip_lock,
        skip_preflight=args.skip_preflight,
    )


if __name__ == "__main__":
    main()
