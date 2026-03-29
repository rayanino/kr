"""Isolated Codex-first overnight orchestrator with guarded worktree writes."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path
from typing import Any

try:
    from scripts.overnight_codex_common import (
        COMPLEXITY_ORDER,
        DECISIONS_LOG,
        FINAL_RESPONSE_SCHEMA,
        HEARTBEAT_FILE,
        LOCK_FILE,
        MORNING_REPORT,
        OVERNIGHT_CODEX_DIR,
        PROJECT_DIR,
        PROGRESS_FILE,
        QUEUE_DIR,
        RESULTS_DIR,
        STATE_FILE,
        WORKTREES_DIR,
        CodexTaskDef,
        OvernightCodexState,
        TaskResult,
        atomic_write,
        ensure_runtime_dirs,
        git_head,
        git_status_porcelain,
        has_forbidden_edits,
        load_manifest,
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
    from overnight_codex_common import (
        COMPLEXITY_ORDER,
        DECISIONS_LOG,
        FINAL_RESPONSE_SCHEMA,
        HEARTBEAT_FILE,
        LOCK_FILE,
        MORNING_REPORT,
        OVERNIGHT_CODEX_DIR,
        PROJECT_DIR,
        PROGRESS_FILE,
        QUEUE_DIR,
        RESULTS_DIR,
        STATE_FILE,
        WORKTREES_DIR,
        CodexTaskDef,
        OvernightCodexState,
        TaskResult,
        atomic_write,
        ensure_runtime_dirs,
        git_head,
        git_status_porcelain,
        has_forbidden_edits,
        load_manifest,
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


def _find_codex() -> str | None:
    """Find the Codex CLI."""
    found = shutil.which("codex")
    if found:
        return found
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
    proc = subprocess.Popen(
        cmd,
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
        raise subprocess.TimeoutExpired(cmd, timeout, output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(cmd, proc.returncode, stdout, stderr)


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
    }
    write_json(HEARTBEAT_FILE, payload)


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
        "Read CLAUDE.md and return {'ok': 'yes'} only.",
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
    return payload.get("ok") == "yes"


def determine_apply_mode() -> tuple[str, bool, bool, list[str]]:
    """Determine whether the main worktree can be auto-applied into safely."""
    notes: list[str] = []
    baseline_clean = not git_status_porcelain()
    if not baseline_clean:
        notes.append("Main repo was dirty at launch; auto-apply disabled.")
    baseline_tests_passed = run_baseline_tests()
    if not baseline_tests_passed:
        notes.append("Baseline tests failed at launch; auto-apply disabled.")
    apply_mode = "conditional_auto_apply" if baseline_clean and baseline_tests_passed else "queue_only"
    return apply_mode, baseline_clean, baseline_tests_passed, notes


def preflight(skip_tests: bool = False) -> tuple[str, bool, bool, list[str], str]:
    """Run preflight checks and return launch policy."""
    codex_bin = _find_codex()
    if not codex_bin:
        raise RuntimeError("Codex CLI not found in PATH.")
    version = _run_subprocess_safe([codex_bin, "--version"], timeout=30)
    if version.returncode != 0:
        raise RuntimeError("Codex CLI did not respond to --version.")
    if not run_codex_smoke(codex_bin):
        raise RuntimeError("Codex unattended smoke test failed.")
    if skip_tests:
        apply_mode = "queue_only"
        notes = ["Baseline tests skipped explicitly; auto-apply disabled."]
        return apply_mode, False, False, notes, codex_bin
    apply_mode, baseline_clean, baseline_tests_passed, notes = determine_apply_mode()
    return apply_mode, baseline_clean, baseline_tests_passed, notes, codex_bin


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
        "task_status": "success",
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
        command = ["python", "-m", "pytest", test_dir, "-v", "--tb=short"]
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
    return TaskResult(
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
    )


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
    branch_name = f"overnight-codex-{safe_slug(task.task_id)}-{int(time.time())}"
    worktree_path = WORKTREES_DIR / safe_slug(task.task_id)
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
        raise RuntimeError(f"Failed to create worktree for {task.task_id}: {result.stderr[:400]}")
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
            return {"source", "normalization", "excerpting"}
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
    deleted = _run_subprocess_safe(
        ["git", "diff", "--diff-filter=D", "--name-only"],
        cwd=worktree_path,
        timeout=30,
    )
    deleted_files = [line.strip() for line in deleted.stdout.splitlines() if line.strip()]
    if deleted_files:
        failures.append(f"Deleted files are not allowed: {deleted_files}")

    engines = _affected_engines(changed_files)
    for engine in sorted(engines):
        test_dir = worktree_path / "engines" / engine / "tests"
        if not test_dir.exists():
            continue
        test_result = _run_subprocess_safe(
            ["python", "-m", "pytest", f"engines/{engine}/tests/", "-x", "-q", "--tb=short"],
            cwd=worktree_path,
            timeout=900,
        )
        if test_result.returncode != 0:
            failures.append(f"pytest failed for {engine}: {test_result.stdout[-800:]}")
            break

    py_changed = [path for path in changed_files if path.endswith(".py")]
    if py_changed:
        check_script = worktree_path / "scripts" / "pre_review_checks.py"
        if check_script.exists():
            check_result = _run_subprocess_safe(
                ["python", str(check_script), *py_changed],
                cwd=worktree_path,
                timeout=180,
            )
            if check_result.returncode != 0 and "ERROR" in check_result.stdout:
                failures.append(f"pre_review_checks failed: {check_result.stdout[-800:]}")

        pyright = _run_subprocess_safe(
            ["python", "-m", "pyright", *py_changed],
            cwd=worktree_path,
            timeout=180,
        )
        if pyright.returncode != 0:
            log_decision("Pyright warnings in guarded worktree", pyright.stdout[-800:])

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
    schema_path = result_dir / "output_schema.json"
    output_path = result_dir / task.expected_artifact
    write_json(schema_path, FINAL_RESPONSE_SCHEMA)

    prompt = build_prompt(task)
    workdir = PROJECT_DIR
    branch_name: str | None = None
    worktree_path: Path | None = None

    try:
        worktree_path, branch_name = prepare_worktree(task, state.launch_head)
        workdir = worktree_path
    except Exception as exc:
        return TaskResult(
            task_id=task.task_id,
            status="failed",
            start_time=start_time,
            end_time=utc_now_iso(),
            duration_s=round(time.time() - start, 1),
            error=str(exc),
            artifact_path=repo_rel(output_path),
            branch_name=branch_name,
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
                sandbox_mode="workspace-write",
                output_path=output_path,
                schema_path=schema_path,
                timeout_minutes=task.timeout_minutes,
            )
        except subprocess.TimeoutExpired:
            return TaskResult(
                task_id=task.task_id,
                status="timeout",
                start_time=start_time,
                end_time=utc_now_iso(),
                duration_s=round(time.time() - start, 1),
                error=f"Task exceeded {task.timeout_minutes} minute timeout",
                artifact_path=repo_rel(output_path),
                branch_name=branch_name,
            )
        except Exception as exc:
            return TaskResult(
                task_id=task.task_id,
                status="failed",
                start_time=start_time,
                end_time=utc_now_iso(),
                duration_s=round(time.time() - start, 1),
                error=str(exc),
                artifact_path=repo_rel(output_path),
                branch_name=branch_name,
            )

        if exec_result.returncode != 0:
            return TaskResult(
                task_id=task.task_id,
                status="failed",
                start_time=start_time,
                end_time=utc_now_iso(),
                duration_s=round(time.time() - start, 1),
                error=exec_result.stderr[-1000:],
                artifact_path=repo_rel(output_path),
                branch_name=branch_name,
            )

        try:
            payload = _parse_structured_output(output_path)
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
                fallback_path = result_dir / "fallback.md"
                fallback_prompt = (
                    build_prompt(task)
                    + "\n\nStructured JSON retries failed. Do the work and return markdown with sections: "
                    "Summary, Evidence, Findings, Action Items, Commands."
                )
                fallback_result = _codex_exec_freeform(
                    codex_bin,
                    prompt=fallback_prompt,
                    workdir=workdir,
                    sandbox_mode="workspace-write",
                    output_path=fallback_path,
                    timeout_minutes=task.timeout_minutes,
                )
                if fallback_result.returncode != 0:
                    return TaskResult(
                        task_id=task.task_id,
                        status="failed",
                        start_time=start_time,
                        end_time=utc_now_iso(),
                        duration_s=round(time.time() - start, 1),
                        error=f"Invalid structured output: {last_validation_error}",
                        artifact_path=repo_rel(output_path),
                        branch_name=branch_name,
                    )
                payload = _payload_from_markdown(task, fallback_path)
                break

    assert payload is not None

    _write_result_artifacts(task, result_dir, payload)
    summary = str(payload.get("summary", ""))[:2000]
    assert worktree_path is not None
    assert branch_name is not None
    changed_files = worktree_changed_files(worktree_path)

    if task.write_policy == "readonly":
        if changed_files:
            log_decision(
                f"Readonly task attempted repo edits: {task.task_id}",
                {"files": changed_files},
            )
            return TaskResult(
                task_id=task.task_id,
                status="failed",
                start_time=start_time,
                end_time=utc_now_iso(),
                duration_s=round(time.time() - start, 1),
                summary=summary,
                error=f"Readonly task modified files: {changed_files}",
                artifact_path=repo_rel(output_path),
                branch_name=branch_name,
                files_changed=changed_files,
                tests_run=list(payload.get("tests_run", [])),
                commands_run=list(payload.get("commands_run", [])),
            )
        return TaskResult(
            task_id=task.task_id,
            status="success",
            start_time=start_time,
            end_time=utc_now_iso(),
            duration_s=round(time.time() - start, 1),
            summary=summary,
            artifact_path=repo_rel(output_path),
            branch_name=branch_name,
            files_changed=[],
            tests_run=list(payload.get("tests_run", [])),
            commands_run=list(payload.get("commands_run", [])),
        )
    if not changed_files:
        return TaskResult(
            task_id=task.task_id,
            status="success",
            start_time=start_time,
            end_time=utc_now_iso(),
            duration_s=round(time.time() - start, 1),
            summary=summary,
            artifact_path=repo_rel(output_path),
            branch_name=branch_name,
            tests_run=list(payload.get("tests_run", [])),
            commands_run=list(payload.get("commands_run", [])),
        )

    gate_passed, gate_failures, review_path = run_quality_gate(
        codex_bin, task, worktree_path, changed_files, result_dir
    )
    if not gate_passed:
        log_decision(f"Quality gate failed for {task.task_id}", gate_failures)
        return TaskResult(
            task_id=task.task_id,
            status="failed",
            start_time=start_time,
            end_time=utc_now_iso(),
            duration_s=round(time.time() - start, 1),
            summary=summary,
            error="; ".join(gate_failures)[:1800],
            artifact_path=repo_rel(output_path),
            branch_name=branch_name,
            review_path=repo_rel(review_path),
            files_changed=changed_files,
            tests_run=list(payload.get("tests_run", [])),
            commands_run=list(payload.get("commands_run", [])),
        )

    commit_hash = _commit_worktree(task, worktree_path)
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
    return TaskResult(
        task_id=task.task_id,
        status=status,
        start_time=start_time,
        end_time=utc_now_iso(),
        duration_s=round(time.time() - start, 1),
        summary=summary,
        artifact_path=repo_rel(output_path),
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
    )


def generate_morning_report(state: OvernightCodexState, manifest: list[CodexTaskDef]) -> None:
    """Generate a compact morning report."""
    lines = [f"# Overnight Codex Report — {state.run_id}", ""]
    lines.append(f"- Status: **{state.status.upper()}**")
    lines.append(f"- Apply mode: `{state.apply_mode}`")
    lines.append(f"- Launch head: `{state.launch_head[:8]}`")
    lines.append(
        f"- Tasks: {state.tasks_completed} completed, {state.tasks_failed} failed, "
        f"{state.tasks_queued} queued, {state.tasks_skipped} skipped"
    )
    if state.notes:
        lines.append("")
        lines.append("## Launch Notes")
        lines.extend(f"- {note}" for note in state.notes)

    completed: list[str] = []
    queued: list[str] = []
    issues: list[str] = []
    for task in manifest:
        result = state.results.get(task.task_id, {})
        status = result.get("status", "pending")
        if status == "success":
            suffix = " (auto-applied)" if result.get("auto_applied") else ""
            completed.append(f"- `{task.task_id}`: {task.name}{suffix}")
        elif status == "queued":
            queued.append(
                f"- `{task.task_id}`: {task.name} -> `{result.get('patch_path', 'n/a')}` "
                f"({result.get('queue_reason', 'queued')})"
            )
        elif status in {"failed", "timeout", "partial_success"}:
            issues.append(f"- `{task.task_id}` ({status}): {result.get('error', 'unknown')}")

    if completed:
        lines.append("")
        lines.append("## Completed")
        lines.extend(completed)
    if queued:
        lines.append("")
        lines.append("## Queued Patches")
        lines.extend(queued)
    if issues:
        lines.append("")
        lines.append("## Issues")
        lines.extend(issues)

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
            notes = ["Preflight skipped explicitly; auto-apply disabled."]
        else:
            apply_mode, baseline_clean, baseline_tests_passed, notes, codex_bin = preflight()

        deadline = utc_now() + timedelta(hours=hours)
        previous = load_state() if resume else None
        if previous:
            state = previous
            state.status = "running"
            state.deadline = deadline.isoformat()
            state.notes.extend(note for note in notes if note not in state.notes)
            log_decision("Resuming previous overnight_codex state")
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
                notes=notes,
            )
            log_decision(
                "overnight_codex session started",
                {
                    "tasks": len(manifest),
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
            if state.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                log_decision("Circuit breaker tripped on failures")
                state.status = "stopped"
                break
            if state.consecutive_timeouts >= MAX_CONSECUTIVE_TIMEOUTS:
                log_decision("Circuit breaker tripped on timeouts")
                state.status = "stopped"
                break

            task = pick_next_ready(manifest, state)
            if task is None:
                log_decision("All tasks resolved or blocked")
                break

            original_timeout = task.timeout_minutes
            scale = timeout_overrides.get(task.category, 1.0)
            if task.estimated_complexity == "high":
                scale *= 1.4
            task.timeout_minutes = min(MAX_TIMEOUT_MINUTES, max(1, int(task.timeout_minutes * scale)))
            if remaining < task.timeout_minutes * 60:
                state.results[task.task_id] = {"status": "skipped", "error": "insufficient time"}
                state.tasks_skipped += 1
                save_state(state)
                write_progress_file(state, manifest)
                continue

            print(
                f">>> [{task.priority}] {task.task_id}: {task.name} "
                f"({task.write_policy}, {task.timeout_minutes}m)"
            )
            result = execute_task(task, state=state, codex_bin=codex_bin)
            task.timeout_minutes = original_timeout

            state.results[task.task_id] = asdict(result)
            if result.status == "success":
                state.tasks_completed += 1
                state.consecutive_failures = 0
                state.consecutive_timeouts = 0
            elif result.status == "queued":
                state.tasks_queued += 1
                state.consecutive_failures = 0
                state.consecutive_timeouts = 0
            elif result.status == "timeout":
                state.tasks_failed += 1
                state.consecutive_failures += 1
                state.consecutive_timeouts += 1
                timeout_overrides[task.category] = timeout_overrides.get(task.category, 1.0) + 0.5
            else:
                state.tasks_failed += 1
                state.consecutive_failures += 1

            save_state(state)
            write_progress_file(state, manifest)
            _write_heartbeat(state, task.task_id, result.status, len(manifest))
            print(f"    {result.status.upper()}: {result.summary[:140]}")

        if state.status == "running":
            state.status = "completed"
        save_state(state)
        write_progress_file(state, manifest)
        generate_morning_report(state, manifest)
        maybe_append_findings()
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
