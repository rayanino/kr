"""KR Overnight Autonomous Work Orchestrator v2.

Runs quality improvement tasks using Claude Code CLI/SDK and Codex CLI
for independent verification. Each task gets a fresh context window.
State persists across tasks via JSON + progress.md (Anthropic harness pattern).

Usage:
  python scripts/overnight_orchestrator.py --hours 7.5
  python scripts/overnight_orchestrator.py --manifest overnight/manifest.json
  python scripts/overnight_orchestrator.py --dry-run
  python scripts/overnight_orchestrator.py --task val-001
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
OVERNIGHT_DIR = PROJECT_DIR / "overnight"
STATE_FILE = OVERNIGHT_DIR / "state.json"
PROGRESS_FILE = OVERNIGHT_DIR / "progress.md"
DECISIONS_LOG = OVERNIGHT_DIR / "decisions.log"
MORNING_REPORT = OVERNIGHT_DIR / "MORNING_REPORT.md"
LOCK_FILE = OVERNIGHT_DIR / ".overnight.lock"
HEARTBEAT_FILE = OVERNIGHT_DIR / ".heartbeat"

MAX_CONSECUTIVE_FAILURES = 3   # legacy — kept for backwards compat in state.json
MAX_CONSECUTIVE_CRASHES = 3    # hard stop: subprocess died unexpectedly
MAX_CONSECUTIVE_TIMEOUTS = 5   # soft stop: tasks running out of time
MAX_TIMEOUT_MINUTES = 45       # absolute cap for adaptive timeout scaling

OVERNIGHT_SAFETY_PROMPT = """OVERNIGHT AUTONOMOUS MODE — KR Pipeline Project.
You are executing a single task in the overnight autonomous system.

ABSOLUTE RULES — SAFETY:
- NEVER modify files in library/sources/*/frozen/
- NEVER modify primary_text content in any pipeline output
- NEVER delete any file or directory
- NEVER run git push
- NEVER modify .claude/settings.json
- There is no human present — do not ask questions
- Commit your work with message prefix "overnight: "
- Write a summary to overnight/results/{TASK_ID}/summary.md
- ALL LLM calls within the pipeline go through OpenRouter ONLY
- Use OPENROUTER_API_KEY — never direct Anthropic or OpenAI endpoints

ABSOLUTE RULES — HARDENING ONLY:
- NEVER implement new features, new modules, or new capabilities
- NEVER create new source files under engines/*/src/
- Only MODIFY existing source files to fix confirmed bugs found during THIS session
- Your job is to FIND problems and WRITE TESTS, not to build new functionality
- Allowed work: code review, edge case tests, bug fixes, spec audits, validation, documentation
- Forbidden work: new engine phases, new pipeline stages, feature implementation

CORE QUALITY RULES:
1. Every bug you find MUST be fixed AND regression-tested in the same session.
   Finding without fixing is half the value. Write a test that fails without the
   fix and passes with it.
2. Every test must test exactly ONE behavior. Name it precisely:
   test_{{what}}_{{condition}}_{{expected}}. No multi-assertion catch-all tests.
3. Reference the EXACT SPEC section for every test: read the SPEC text, quote
   the rule, then write the test. Don't paraphrase SPEC rules from memory.
4. Test QUALITY over QUANTITY. 10 precise boundary tests > 100 shallow smoke tests.
   Every test must catch a real bug or prove a real invariant.
5. When done, self-review your work: re-read every test you wrote and ask
   "Would this test catch the bug if someone introduced it tomorrow?"
6. Count tests BEFORE and AFTER. Report the delta in findings.json.

FINDINGS PROTOCOL (MANDATORY for every modifying/test task):
After completing your work, write a structured findings file to:
  overnight/results/{{TASK_ID}}/findings.json
with this exact JSON structure:
{{
  "task_status": "success|truncated|failed",
  "session_id": "{TASK_ID}",
  "bugs_found": [{{"severity": "CRITICAL|HIGH|MEDIUM", "file": "...", "line": 0, "description": "...", "fixed": true}}],
  "tests_added": [{{"name": "test_...", "file": "...", "edge_case": "..."}}],
  "spec_issues": [{{"section": "§...", "issue": "...", "recommendation": "..."}}],
  "dead_code": [{{"file": "...", "line": 0, "description": "..."}}],
  "learnings": ["..."],
  "test_count_before": 0,
  "test_count_after": 0
}}
Count tests BEFORE starting work: python -m pytest engines/excerpting/tests/ --co -q 2>/dev/null | tail -1
Count tests AFTER finishing: same command.
This data is aggregated into the morning report and cumulative findings log.
Every overnight session's findings must be preserved — they represent paid knowledge.

Read overnight/progress.md for context on what has been done tonight.
Read the active engine's CLAUDE.md for current state.
Follow all rules in CLAUDE.md and .claude/rules/*.
"""

OVERNIGHT_RESEARCH_PROMPT = """OVERNIGHT AUTONOMOUS MODE — KR Pipeline Project — RESEARCH TASK.
You are executing a research task in the overnight autonomous system.

ABSOLUTE RULES — SAFETY:
- NEVER modify any source code files (engines/*/src/, shared/*/src/)
- NEVER create new files under engines/*/src/
- NEVER modify .claude/settings.json
- NEVER run git push or git commit
- NEVER delete any file or directory
- There is no human present — do not ask questions
- Write ALL output to overnight/results/{TASK_ID}/

RESEARCH RULES:
- Your job is to RESEARCH AND DOCUMENT, not to implement or modify code
- Use web search extensively — minimum 8 searches per major research question
- Cite specific URLs, version numbers, benchmark scores for every claim
- If you cannot find evidence, say so explicitly — never guess or hallucinate
- All recommendations must include exact implementation steps for the next session
- Write a structured findings document to overnight/results/{TASK_ID}/findings.md

Read overnight/progress.md for context on what has been done tonight.
Read NEXT.md for the research questions to answer.
Follow all rules in CLAUDE.md and .claude/rules/*.
"""

# --- Weekend Sprint prompts (broader than hardening, still safe) ---

SPRINT_ANALYSIS_PROMPT = """WEEKEND SPRINT — READONLY ANALYSIS MODE — KR Pipeline Project.
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

QUALITY RULES:
1. Every claim in your analysis must reference specific file paths and line numbers.
2. When auditing SPECs, quote the exact text of each defect.
3. When comparing contracts, list exact field names from each side.
4. Write a structured findings document to overnight/results/{TASK_ID}/findings.md
5. Write a machine-readable summary to overnight/results/{TASK_ID}/findings.json

Read CLAUDE.md and the relevant engine's CLAUDE.md for context.
Follow all rules in .claude/rules/*.
"""

SPRINT_TEST_PROMPT = """WEEKEND SPRINT — TEST WRITING MODE — KR Pipeline Project.
You are executing a test writing task in the weekend sprint system.

ABSOLUTE RULES — SAFETY:
- NEVER modify files in library/sources/*/frozen/
- NEVER modify primary_text content in any pipeline output
- NEVER delete any file or directory
- NEVER run git push
- NEVER modify .claude/settings.json
- There is no human present — do not ask questions
- Commit your work with message prefix "weekend: "
- Write a summary to overnight/results/{TASK_ID}/summary.md

SCOPE RULES — WHAT YOU MAY DO:
- You MAY create NEW test files under engines/*/tests/ and shared/*/tests/
- You MAY add new fixtures to existing conftest.py files (append-only)
- You MAY read any file in the repository for context

SCOPE RULES — WHAT YOU MUST NOT DO:
- NEVER modify files under engines/*/src/ or shared/*/src/
- NEVER modify EXISTING test files — only create NEW test files
- NEVER touch engines/excerpting/src/ (CLI backend reformation in progress)

QUALITY RULES:
1. Every test must use real Arabic text from tests/fixtures/ — never transliteration.
2. Every test must test exactly ONE behavior. Name: test_{{what}}_{{condition}}_{{expected}}.
3. Reference the EXACT SPEC section for every test.
4. Test QUALITY over QUANTITY. 10 precise tests > 50 shallow ones.
5. Count tests BEFORE and AFTER. Report the delta in findings.json.
6. Run pytest -x -q on the affected test directory after writing tests.

Read CLAUDE.md and the relevant engine's CLAUDE.md for context.
Follow all rules in .claude/rules/*.
"""

SPRINT_SCRIPT_PROMPT = """WEEKEND SPRINT — QUALITY SCRIPT BUILDING MODE — KR Pipeline Project.
You are executing a quality tooling task in the weekend sprint system.

ABSOLUTE RULES — SAFETY:
- NEVER modify files in library/sources/*/frozen/
- NEVER modify primary_text content in any pipeline output
- NEVER delete any file or directory
- NEVER run git push
- NEVER modify .claude/settings.json
- There is no human present — do not ask questions
- Commit your work with message prefix "weekend: "
- Write a summary to overnight/results/{TASK_ID}/summary.md

SCOPE RULES — WHAT YOU MAY DO:
- You MAY create NEW files under scripts/ and tools/
- You MAY create NEW directories under tests/adversarial/
- You MAY read any file in the repository for context

SCOPE RULES — WHAT YOU MUST NOT DO:
- NEVER modify existing files — only create NEW files
- NEVER modify any file under engines/*/src/ or shared/*/src/
- NEVER modify any file under engines/*/tests/ or shared/*/tests/
- NEVER touch engines/excerpting/src/ (CLI backend reformation in progress)

QUALITY RULES:
1. All scripts must have type hints on all function signatures.
2. All scripts must have a docstring and --help via argparse.
3. All scripts must handle errors gracefully with clear error messages.
4. All scripts must produce structured output (JSON or Markdown).
5. Test your script by running it before committing.
6. Report what the script does and its output in findings.json.

Read CLAUDE.md for project context.
Follow all rules in .claude/rules/*.
"""

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class TaskDef:
    """A single overnight task definition."""

    task_id: str
    name: str
    category: str  # validation|test|spec|doc|code_quality|research|integration|verification
    prompt: str
    safety_level: str  # readonly|additive|modifying
    execution_mode: str  # cli|codex|sdk
    agent: str | None = None  # KR agent name for cli mode
    model: str = "sonnet"
    max_budget_usd: float = 2.0
    timeout_minutes: int = 30
    allowed_tools: list[str] = field(default_factory=list)
    permission_mode: str = "bypassPermissions"  # bypassPermissions|plan
    depends_on: list[str] = field(default_factory=list)
    priority: int = 5
    max_turns: int = 30
    codex_flags: list[str] = field(default_factory=list)
    bookend: bool = False  # Always-run task: skips dependency propagation, runs last
    estimated_complexity: str = "medium"  # low|medium|high — controls sort order + timeout scaling


# Complexity sort order: low tasks run before medium, medium before high
_COMPLEXITY_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass
class TaskResult:
    """Result from executing a task."""

    task_id: str
    status: str  # success|failed|timeout|rolled_back|skipped
    start_time: str = ""
    end_time: str = ""
    duration_s: float = 0.0
    output_summary: str = ""
    commit_hash: str | None = None
    gate_result: dict[str, Any] | None = None
    error: str | None = None
    model_used: str = ""
    cost_usd: float = 0.0


@dataclass
class OvernightState:
    """Persistent state for an overnight run."""

    run_id: str
    started_at: str
    deadline: str
    status: str = "running"  # running|completed|stopped|crashed
    git_start_hash: str = ""
    consecutive_failures: int = 0   # legacy — sum of all failure types
    consecutive_crashes: int = 0    # subprocess crashes (hard breaker)
    consecutive_timeouts: int = 0   # task timeouts (soft breaker)
    total_cost_usd: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_skipped: int = 0
    tasks_rolled_back: int = 0
    results: dict[str, dict[str, Any]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Codex CLI detection
# ---------------------------------------------------------------------------


def _find_codex() -> str | None:
    """Find Codex CLI, checking common Windows npm global locations."""
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


def _find_gemini() -> str | None:
    """Find Gemini CLI, checking common Windows npm global locations."""
    found = shutil.which("gemini")
    if found:
        return found
    if sys.platform == "win32":
        for candidate in [
            Path(os.environ.get("APPDATA", "")) / "npm" / "gemini.cmd",
            Path(os.environ.get("LOCALAPPDATA", "")) / "npm" / "gemini.cmd",
            Path.home() / "AppData" / "Roaming" / "npm" / "gemini.cmd",
        ]:
            if candidate.exists():
                return str(candidate)
    return None


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def git_head() -> str:
    """Return current HEAD commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=str(PROJECT_DIR),
    )
    return result.stdout.strip()


def git_is_clean() -> bool:
    """Check if working directory is clean (ignoring overnight/transient files)."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=str(PROJECT_DIR),
    )
    # Filter out overnight state files and transient paths regardless of status
    IGNORED_PREFIXES = (
        "overnight/", "results/", ".claude/scheduled_tasks",
        ".claude/session_state", ".claude/plans/",
    )
    lines = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        # Extract the file path (status chars are first 2 chars + space)
        path_part = line[3:] if len(line) > 3 else line.strip()
        # Normalize Windows backslashes for consistent prefix matching
        path_part = path_part.replace("\\", "/")
        if not any(path_part.startswith(p) for p in IGNORED_PREFIXES):
            lines.append(line)
    return len(lines) == 0


def git_rollback(commit_hash: str) -> None:
    """Roll back to a specific commit and clean untracked files."""
    result = subprocess.run(
        ["git", "reset", "--hard", commit_hash],
        capture_output=True, text=True, cwd=str(PROJECT_DIR),
    )
    if result.returncode != 0:
        log_decision(f"ROLLBACK FAILED: {result.stderr[:500]}")
        raise RuntimeError(f"Git rollback failed: {result.stderr[:200]}")
    # Clean untracked files created by the failed task (preserve overnight/)
    subprocess.run(
        ["git", "clean", "-fd", "--exclude=overnight/"],
        capture_output=True, text=True, cwd=str(PROJECT_DIR),
    )
    log_decision(f"ROLLBACK to {commit_hash[:8]}")


def git_commit(message: str, files: list[str] | None = None) -> str | None:
    """Create a git commit. Returns commit hash or None if nothing to commit."""
    if files:
        for f in files:
            subprocess.run(
                ["git", "add", f],
                capture_output=True, text=True, cwd=str(PROJECT_DIR),
            )
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True, cwd=str(PROJECT_DIR),
    )
    if result.returncode == 0:
        # Nothing staged
        return None
    subprocess.run(
        ["git", "commit", "-m", message,
         "--author", "KR Overnight <overnight@kr.local>"],
        capture_output=True, text=True, cwd=str(PROJECT_DIR),
    )
    return git_head()


def git_changed_files_since(commit_hash: str) -> list[str]:
    """List files changed since a commit."""
    result = subprocess.run(
        ["git", "diff", "--name-only", commit_hash, "HEAD"],
        capture_output=True, text=True, cwd=str(PROJECT_DIR),
    )
    return [f for f in result.stdout.strip().split("\n") if f.strip()]


# ---------------------------------------------------------------------------
# Safe subprocess execution (avoids Windows pipe deadlock)
# ---------------------------------------------------------------------------


def _run_subprocess_safe(
    cmd: list[str],
    timeout: int = 300,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run subprocess safely on Windows (avoids pipe buffer deadlock).

    subprocess.run(capture_output=True) can deadlock on Windows when
    stdout/stderr exceed ~64KB pipe buffer. Uses Popen + communicate()
    which handles large outputs correctly.
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd or str(PROJECT_DIR),
        env=env,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate(timeout=10)
        raise subprocess.TimeoutExpired(cmd, timeout, output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(
        args=cmd, returncode=proc.returncode, stdout=stdout, stderr=stderr,
    )


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------


def _atomic_write(path: Path, content: str) -> None:
    """Write content to file atomically (write-to-temp-then-rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def save_state(state: OvernightState) -> None:
    """Save state to JSON file (atomic write)."""
    _atomic_write(STATE_FILE, json.dumps(asdict(state), indent=2, ensure_ascii=False))


def load_state() -> OvernightState | None:
    """Load state from JSON file, or None if not present."""
    if not STATE_FILE.exists():
        return None
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    results = data.pop("results", {})
    state = OvernightState(**data)
    state.results = results
    return state


def write_progress_file(state: OvernightState, manifest: list[TaskDef]) -> None:
    """Write human-readable progress file (Anthropic harness pattern)."""
    lines = [f"# Overnight Progress — {state.run_id}\n"]

    completed = []
    in_progress = []
    remaining = []

    for task in manifest:
        result = state.results.get(task.task_id)
        if result and result.get("status") in ("success", "rolled_back", "skipped"):
            status_mark = "x" if result["status"] == "success" else "~"
            dur = result.get("duration_s", 0)
            completed.append(
                f"- [{status_mark}] {task.task_id}: {task.name} "
                f"({result['status']}, {dur:.0f}s)"
            )
        elif result and result.get("status") == "in_progress":
            in_progress.append(f"- [ ] {task.task_id}: {task.name} (in progress)")
        else:
            remaining.append(f"- [ ] {task.task_id}: {task.name}")

    if completed:
        lines.append("\n## Completed")
        lines.extend(completed)
    if in_progress:
        lines.append("\n## In Progress")
        lines.extend(in_progress)
    if remaining:
        lines.append("\n## Remaining")
        lines.extend(remaining)

    _atomic_write(PROGRESS_FILE, "\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Decision logging
# ---------------------------------------------------------------------------


def log_decision(message: str, details: Any = None) -> None:
    """Append a decision to the decisions log."""
    DECISIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"[{timestamp}] {message}"
    if details:
        entry += f"\n  Details: {json.dumps(details, ensure_ascii=False, default=str)[:500]}"
    with DECISIONS_LOG.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")


# ---------------------------------------------------------------------------
# Lock file (prevent concurrent instances)
# ---------------------------------------------------------------------------


def _acquire_lock() -> None:
    """Prevent multiple overnight instances from running simultaneously."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text(encoding="utf-8").strip())
            try:
                os.kill(old_pid, 0)  # Check if process exists (doesn't kill)
                raise RuntimeError(
                    f"Another overnight session (PID {old_pid}) is already running. "
                    f"If stale, delete {LOCK_FILE}"
                )
            except OSError:
                log_decision(f"Stale lock file from PID {old_pid} — removing")
        except (ValueError, OSError):
            pass  # Invalid PID or check failed — assume stale
    LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8")


def _release_lock() -> None:
    """Release the lock file."""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except OSError:
        pass


def _write_heartbeat(
    task_id: str, status: str, state: OvernightState,
    manifest_len: int, start_monotonic: float,
) -> None:
    """Write heartbeat file after each task (detect hangs)."""
    _atomic_write(HEARTBEAT_FILE, json.dumps({
        "source": "write_orchestrator",
        "pid": os.getpid(),
        "last_task": task_id,
        "last_task_status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tasks_completed": state.tasks_completed,
        "tasks_remaining": manifest_len - len(state.results),
        "elapsed_minutes": round((time.monotonic() - start_monotonic) / 60, 1),
    }, indent=2))


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------


def preflight_checks() -> None:
    """Verify system is ready for overnight work."""
    errors: list[str] = []

    # Clean git state (allow overnight/ and results/ untracked)
    if not git_is_clean():
        errors.append("Git working directory is not clean. Commit or stash changes first.")

    # Claude CLI available
    try:
        result = subprocess.run(
            ["claude", "--version"], capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            errors.append("Claude CLI not responding")
    except FileNotFoundError:
        errors.append("Claude CLI not found in PATH")

    # Test suite passes (run each engine separately to avoid conftest collisions)
    for test_dir in [
        "engines/source/tests/", "engines/normalization/tests/",
        "engines/excerpting/tests/",
    ]:
        test_result = _run_subprocess_safe(
            ["python", "-m", "pytest", test_dir, "-x", "-q", "--tb=no"],
            timeout=300,
        )
        if test_result.returncode != 0:
            errors.append(f"Test suite failing ({test_dir}):\n{test_result.stdout[-500:]}")
            break

    # Codex CLI availability (L5 quality gate)
    codex_path = _find_codex()
    if not codex_path:
        os.environ["KR_SKIP_CODEX"] = "1"
        print("  [info] Codex CLI not found — L5 verification disabled for this run")
    else:
        os.environ.pop("KR_SKIP_CODEX", None)
        os.environ["KR_CODEX_PATH"] = codex_path
        print(f"  [info] Codex CLI found at {codex_path}")

    gemini_path = _find_gemini()
    if not gemini_path:
        os.environ["KR_SKIP_GEMINI"] = "1"
        print("  [info] Gemini CLI not found — L6 adversarial challenge disabled for this run")
    else:
        os.environ.pop("KR_SKIP_GEMINI", None)
        os.environ["KR_GEMINI_PATH"] = gemini_path
        print(f"  [info] Gemini CLI found at {gemini_path}")

    # Disk space (need at least 500MB free)
    # Simple check via df on Windows/bash
    try:
        df_result = subprocess.run(
            ["df", "-h", str(PROJECT_DIR)],
            capture_output=True, text=True, timeout=10,
        )
        # Just log it, don't block
        if df_result.returncode == 0:
            log_decision(f"Disk space check:\n{df_result.stdout.strip()}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # df might not be available on all Windows setups

    if errors:
        print("PRE-FLIGHT CHECKS FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("Pre-flight checks passed.")


# ---------------------------------------------------------------------------
# Task execution — 4 backends (CLI, Codex, Gemini, SDK)
# ---------------------------------------------------------------------------


def execute_task(task: TaskDef) -> TaskResult:
    """Route task to the appropriate execution backend."""
    start = time.time()
    start_ts = datetime.now(timezone.utc).isoformat()

    # Create results directory for this task
    task_results_dir = OVERNIGHT_DIR / "results" / task.task_id
    task_results_dir.mkdir(parents=True, exist_ok=True)

    # Select safety prompt based on task category
    if task.category == "research":
        safety_prompt = OVERNIGHT_RESEARCH_PROMPT.replace("{TASK_ID}", task.task_id)
    elif task.category == "sprint_analysis":
        safety_prompt = SPRINT_ANALYSIS_PROMPT.replace("{TASK_ID}", task.task_id)
    elif task.category == "sprint_test":
        safety_prompt = SPRINT_TEST_PROMPT.replace("{TASK_ID}", task.task_id)
    elif task.category == "sprint_script":
        safety_prompt = SPRINT_SCRIPT_PROMPT.replace("{TASK_ID}", task.task_id)
    else:
        safety_prompt = OVERNIGHT_SAFETY_PROMPT.replace("{TASK_ID}", task.task_id)

    try:
        if task.execution_mode == "codex":
            result = _execute_codex(task, task_results_dir)
        elif task.execution_mode == "gemini":
            result = _execute_gemini(task, task_results_dir)
        elif task.execution_mode == "sdk":
            result = _execute_sdk(task, safety_prompt)
        else:
            result = _execute_cli(task, safety_prompt)
    except subprocess.TimeoutExpired:
        result = TaskResult(
            task_id=task.task_id, status="timeout",
            error=f"Task exceeded {task.timeout_minutes} minute timeout",
            model_used=task.model,
        )
        # Check for partial output before marking as total failure
        if _check_partial_success(task.task_id):
            result.status = "partial_success"
            result.error += " (partial output preserved)"
    except Exception as e:
        result = TaskResult(
            task_id=task.task_id, status="failed",
            error=str(e), model_used=task.model,
        )

    end = time.time()
    result.start_time = start_ts
    result.end_time = datetime.now(timezone.utc).isoformat()
    result.duration_s = round(end - start, 1)

    # Save task result to disk (atomic write)
    result_file = task_results_dir / "result.json"
    _atomic_write(result_file, json.dumps(asdict(result), indent=2, ensure_ascii=False))

    return result


def _check_partial_success(task_id: str) -> bool:
    """Check if a timed-out task produced meaningful output (> 1KB)."""
    task_dir = OVERNIGHT_DIR / "results" / task_id
    if not task_dir.exists():
        return False
    for filename in ("findings.json", "findings.md", "summary.md"):
        f = task_dir / filename
        if f.exists() and f.stat().st_size > 1024:
            return True
    return False


def _execute_cli(task: TaskDef, safety_prompt: str) -> TaskResult:
    """Execute via Claude Code CLI — agent dispatch, inherits hooks."""
    cmd = [
        "claude", "-p", task.prompt,
        "--output-format", "json",
        "--model", task.model,
        "--dangerously-skip-permissions",
        "--no-session-persistence",
        "--append-system-prompt", safety_prompt,
    ]
    # Maximum thinking effort for opus tasks + fallback for rate limits
    if task.model == "opus":
        cmd += ["--effort", "max", "--fallback-model", "sonnet"]
    if task.agent:
        cmd += ["--agent", task.agent]
    if task.allowed_tools:
        cmd += ["--allowedTools", ",".join(task.allowed_tools)]
    # Always pass budget cap — defense-in-depth: $5 minimum even if manifest says 0
    effective_budget = task.max_budget_usd if task.max_budget_usd > 0 else 5.0
    cmd += ["--max-budget-usd", str(effective_budget)]
    if task.max_turns > 0:
        cmd += ["--max-turns", str(task.max_turns)]

    env = {
        **os.environ,
        "KR_OVERNIGHT": "1",
        "PYTHONIOENCODING": "utf-8",
        "KR_BUDGET_LIMIT": os.environ.get("KR_BUDGET_LIMIT", "20"),
    }
    # Remove API key so CLI uses Max subscription auth (OAuth), not API billing
    env.pop("ANTHROPIC_API_KEY", None)

    result = _run_subprocess_safe(
        cmd, timeout=task.timeout_minutes * 60, env=env,
    )

    # Parse JSON output
    output_text = result.stdout
    try:
        output_json = json.loads(output_text)
        summary = output_json.get("result", output_text[:2000])
        cost = output_json.get("total_cost_usd", 0.0)  # Claude Code uses total_cost_usd
        # Detect max_turns truncation — task completed but was cut short
        subtype = output_json.get("subtype", "")
        if subtype == "error_max_turns":
            log_decision(
                f"WARNING: {task.task_id} hit max_turns limit ({task.max_turns}) "
                f"— output may be incomplete"
            )
    except (json.JSONDecodeError, TypeError):
        summary = output_text[:2000] if output_text else result.stderr[:2000]
        cost = 0.0
        # Fallback: extract cost from raw output via regex
        if output_text:
            match = re.search(r'"total_cost_usd":\s*([0-9.]+)', output_text)
            if match:
                cost = float(match.group(1))

    status = "success" if result.returncode == 0 else "failed"
    error = result.stderr[:1000] if result.returncode != 0 else None

    return TaskResult(
        task_id=task.task_id, status=status,
        output_summary=str(summary)[:2000],
        error=error, model_used=task.model,
        cost_usd=cost,
    )


def _execute_codex(task: TaskDef, results_dir: Path) -> TaskResult:
    """Execute via Codex CLI — independent verification. NEVER for Arabic content."""
    output_file = results_dir / "codex_output.md"
    codex_bin = os.environ.get("KR_CODEX_PATH", "codex")
    cmd = [
        codex_bin, "exec", "--full-auto",
        "--output-last-message", str(output_file),
        *task.codex_flags,
        task.prompt,
    ]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    result = subprocess.run(
        cmd, capture_output=True, text=True,
        timeout=task.timeout_minutes * 60,
        cwd=str(PROJECT_DIR), env=env,
    )

    summary = ""
    if output_file.exists():
        summary = output_file.read_text(encoding="utf-8")[:2000]
    elif result.stdout:
        summary = result.stdout[:2000]

    status = "success" if result.returncode == 0 else "failed"
    error = result.stderr[:1000] if result.returncode != 0 else None

    return TaskResult(
        task_id=task.task_id, status=status,
        output_summary=summary,
        error=error, model_used=task.model,
    )


def _execute_gemini(task: TaskDef, results_dir: Path) -> TaskResult:
    """Execute via Gemini CLI — adversarial review. Uses -y for auto-approval."""
    gemini_bin = os.environ.get("KR_GEMINI_PATH", "gemini")
    output_file = results_dir / "gemini_output.md"

    # Write prompt to file to avoid CLI arg length issues on Windows
    prompt_file = results_dir / "gemini_prompt.txt"
    prompt_file.write_text(task.prompt, encoding="utf-8")

    cmd = [
        gemini_bin, "-p", task.prompt[:8000],  # Gemini -p has arg limits
        "-o", "text",
        "-y",  # auto-approve tool calls
    ]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=task.timeout_minutes * 60,
            cwd=str(PROJECT_DIR), env=env,
        )
    except subprocess.TimeoutExpired:
        return TaskResult(
            task_id=task.task_id, status="timeout",
            error=f"Gemini timed out after {task.timeout_minutes}m",
            model_used="gemini",
        )

    summary = result.stdout[:2000] if result.stdout else ""
    if summary:
        output_file.write_text(summary, encoding="utf-8")

    status = "success" if result.returncode == 0 else "failed"
    error = result.stderr[:1000] if result.returncode != 0 else None

    return TaskResult(
        task_id=task.task_id, status=status,
        output_summary=summary,
        error=error, model_used="gemini",
    )


def _execute_sdk(task: TaskDef, safety_prompt: str) -> TaskResult:
    """Execute via Claude Code SDK — full programmatic control."""
    try:
        from claude_code_sdk import ClaudeCodeOptions, query
    except ImportError:
        # Fall back to CLI if SDK not available
        return _execute_cli(task, safety_prompt)

    options = ClaudeCodeOptions(
        allowed_tools=task.allowed_tools or ["Read", "Bash", "Glob", "Grep"],
        permission_mode=task.permission_mode or "bypassPermissions",
        model=task.model,
        append_system_prompt=safety_prompt,
        max_turns=task.max_turns,
        cwd=str(PROJECT_DIR),
        env={"KR_OVERNIGHT": "1", "PYTHONIOENCODING": "utf-8"},
    )

    # Run async query synchronously
    messages = asyncio.run(_collect_sdk_messages(task.prompt, options))

    # Extract text from messages
    text_parts: list[str] = []
    for msg in messages:
        if hasattr(msg, "content"):
            if isinstance(msg.content, str):
                text_parts.append(msg.content)
            elif isinstance(msg.content, list):
                for block in msg.content:
                    if hasattr(block, "text"):
                        text_parts.append(block.text)

    summary = "\n".join(text_parts)[:2000]

    return TaskResult(
        task_id=task.task_id, status="success",
        output_summary=summary, model_used=task.model,
    )


async def _collect_sdk_messages(prompt: str, options: Any) -> list[Any]:
    """Collect all messages from the async SDK query."""
    from claude_code_sdk import query

    messages = []
    async for msg in query(prompt=prompt, options=options):
        messages.append(msg)
    return messages


# ---------------------------------------------------------------------------
# Quality gate
# ---------------------------------------------------------------------------


def run_quality_gate(task: TaskDef, pre_snapshot: str) -> dict[str, Any]:
    """Run post-task quality checks. Returns {"passed": bool, "failures": [...]}."""
    failures: list[str] = []

    # Determine which engines were modified (engine-specific testing)
    changed = git_changed_files_since(pre_snapshot)
    affected_engines: set[str] = set()
    for f in changed:
        parts = f.replace("\\", "/").split("/")
        if len(parts) >= 2 and parts[0] == "engines":
            affected_engines.add(parts[1])

    # L1: Test suite — only affected engines (or all if shared code changed)
    if not affected_engines:
        affected_engines = {"source", "normalization", "excerpting"}
    for engine in sorted(affected_engines):
        test_dir = f"engines/{engine}/tests/"
        if not (PROJECT_DIR / test_dir).exists():
            continue
        test_result = _run_subprocess_safe(
            ["python", "-m", "pytest", test_dir, "-x", "-q", "--tb=short"],
            timeout=300,
        )
        if test_result.returncode != 0:
            failures.append(f"L1 TEST FAILURE ({test_dir}):\n{test_result.stdout[-500:]}")
            break

    # L2: Git state — check no frozen source modifications or deletions
    for f in changed:
        if "frozen/" in f:
            failures.append(f"L2 FROZEN SOURCE MODIFIED: {f}")
        # Protect ALL excerpting files during CLI transformation (Codex review #6)
        normalized = f.replace("\\", "/")
        if normalized.startswith("engines/excerpting/") and not normalized.startswith("engines/excerpting/tests/"):
            failures.append(f"L2 EXCERPTING PROTECTION: {f}")
    diff_result = _run_subprocess_safe(
        ["git", "diff", "--diff-filter=D", "--name-only", pre_snapshot, "HEAD"],
        timeout=30,
    )
    deleted = [f for f in diff_result.stdout.strip().split("\n") if f.strip()]
    if deleted:
        failures.append(f"L2 FILES DELETED: {deleted}")

    # L3: Compliance — pre_review_checks on modified Python files
    py_changed = [f for f in changed if f.endswith(".py") and "engines/" in f]
    if py_changed:
        check_script = PROJECT_DIR / "scripts" / "pre_review_checks.py"
        if check_script.exists():
            check_result = _run_subprocess_safe(
                ["python", str(check_script), *py_changed],
                timeout=60,
            )
            if check_result.returncode != 0 and check_result.stdout and "ERROR" in check_result.stdout:
                failures.append(f"L3 COMPLIANCE ERROR:\n{check_result.stdout[-500:]}")

    # L4: Pyright (log only, don't fail)
    if py_changed:
        pyright_result = _run_subprocess_safe(
            ["python", "-m", "pyright", *py_changed],
            timeout=60,
        )
        if pyright_result.returncode != 0:
            log_decision(f"L4 PYRIGHT warnings for {task.task_id}",
                         pyright_result.stdout[-500:])

    passed = len(failures) == 0
    if not passed:
        log_decision(f"QUALITY GATE FAILED for {task.task_id}", failures)

    return {"passed": passed, "failures": failures}


# ---------------------------------------------------------------------------
# Codex cross-verification (L5)
# ---------------------------------------------------------------------------


def run_codex_verification(task: TaskDef) -> dict[str, Any]:
    """L5: Independent Codex review of Claude's changes (D-041)."""
    results_dir = OVERNIGHT_DIR / "results" / f"{task.task_id}-codex-review"
    results_dir.mkdir(parents=True, exist_ok=True)

    review_prompt = (
        f"Review the git diff HEAD~1 for code changes made by another AI agent. "
        f"Task was: '{task.name}'. "
        f"Focus on: code structure, type safety, Pydantic patterns, test completeness, "
        f"error handling. Do NOT evaluate Arabic text content or domain-specific decisions. "
        f"Report any structural issues found."
    )
    output_file = results_dir / "codex_review.md"

    try:
        result = subprocess.run(
            [os.environ.get("KR_CODEX_PATH", "codex"), "exec", "--full-auto",
             "--output-last-message", str(output_file),
             review_prompt],
            capture_output=True, text=True, timeout=600,
            cwd=str(PROJECT_DIR),
        )
        review_text = ""
        if output_file.exists():
            review_text = output_file.read_text(encoding="utf-8")

        # Simple heuristic: check if Codex found issues
        has_issues = any(
            kw in review_text.lower()
            for kw in ["issue", "error", "bug", "concern", "problem", "missing"]
        )
        return {
            "review": review_text[:2000],
            "discrepancies": has_issues,
            "review_file": str(output_file),
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log_decision(f"Codex verification skipped for {task.task_id}: {e}")
        return {"review": "", "discrepancies": False, "skipped": True}


def run_gemini_adversarial_challenge(task: TaskDef, code_diff: str) -> dict[str, Any]:
    """L6: Gemini adversarial challenge of overnight changes (D-H002)."""
    results_dir = OVERNIGHT_DIR / "results" / f"{task.task_id}-gemini-review"
    results_dir.mkdir(parents=True, exist_ok=True)

    challenge_prompt = (
        f"You are an adversarial reviewer. A code change was made by an autonomous "
        f"overnight system for task: '{task.name}'.\n\n"
        f"Code diff:\n{code_diff[:6000]}\n\n"
        f"Challenge this change:\n"
        f"1. What edge cases could still break this code after the change?\n"
        f"2. What assumptions is the implementation making that could be wrong?\n"
        f"3. Is the fix/test addressing the root cause or papering over the symptom?\n"
        f"4. Are the new tests actually testing what they claim to test?\n"
        f"Report ONLY genuine concerns — not style or cosmetic issues."
    )
    output_file = results_dir / "gemini_challenge.md"
    gemini_bin = os.environ.get("KR_GEMINI_PATH", "gemini")

    try:
        result = subprocess.run(
            [gemini_bin, "-p", challenge_prompt[:8000], "-o", "text", "-y"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=600, cwd=str(PROJECT_DIR),
        )
        challenge_text = result.stdout[:3000] if result.stdout else ""
        if challenge_text:
            output_file.write_text(challenge_text, encoding="utf-8")

        has_concerns = any(
            kw in challenge_text.lower()
            for kw in ["break", "assumption", "root cause", "symptom", "miss", "fail"]
        )
        return {
            "challenge": challenge_text[:2000],
            "concerns_raised": has_concerns,
            "challenge_file": str(output_file),
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log_decision(f"Gemini adversarial challenge skipped for {task.task_id}: {e}")
        return {"challenge": "", "concerns_raised": False, "skipped": True}


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------


def load_manifest(path: Path) -> list[TaskDef]:
    """Load task manifest from JSON file with validation."""
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("tasks", data if isinstance(data, list) else [])
    known_fields = set(TaskDef.__dataclass_fields__)

    tasks: list[TaskDef] = []
    for item in items:
        # Warn on unknown fields (typo detection)
        unknown = set(item.keys()) - known_fields
        if unknown:
            raise ValueError(
                f"Unknown fields in task '{item.get('task_id', '?')}': {unknown}. "
                f"Valid fields: {sorted(known_fields)}"
            )
        tasks.append(TaskDef(**item))

    # Check for duplicate task IDs
    ids = [t.task_id for t in tasks]
    dupes = {x for x in ids if ids.count(x) > 1}
    if dupes:
        raise ValueError(f"Duplicate task IDs in manifest: {dupes}")

    return tasks


def pick_next_ready(manifest: list[TaskDef], state: OvernightState) -> TaskDef | None:
    """Pick next task: dependencies met, not yet executed, highest priority.

    Propagates skips transitively: if A fails and B depends on A, B is skipped.
    If C depends on B, C is also skipped (not stuck in limbo).
    """
    # Propagate dependency-failed skips transitively until stable.
    # Include "skipped" in the propagation set so A→B→C chains fully propagate:
    # if A fails, B is skipped; then C (which depends on B) is also skipped.
    # Bookend tasks are exempt from dependency propagation — they always run.
    changed = True
    while changed:
        changed = False
        blocked_ids = {
            tid for tid, r in state.results.items()
            if r.get("status") in ("failed", "timeout", "partial_success", "rolled_back", "skipped")
        }
        bookend_ids = {t.task_id for t in manifest if t.bookend}
        for task in manifest:
            if task.task_id in state.results or task.task_id in bookend_ids:
                continue
            if any(dep in blocked_ids for dep in task.depends_on):
                state.results[task.task_id] = {
                    "status": "skipped",
                    "error": "dependency failed",
                }
                state.tasks_skipped += 1
                changed = True

    # Now find candidates with all deps met (only truly successful deps count)
    completed_ids = {
        tid for tid, r in state.results.items()
        if r.get("status") == "success"
    }
    blocked_ids = {
        tid for tid, r in state.results.items()
        if r.get("status") in ("failed", "timeout", "partial_success", "rolled_back", "skipped")
    }
    # Regular tasks: deps must be successful
    regular_candidates = []
    # Bookend tasks: run after all non-bookend tasks are resolved
    bookend_candidates = []
    all_resolved = {tid for tid in state.results}
    non_bookend_tasks = [t for t in manifest if not t.bookend]
    all_non_bookend_resolved = all(t.task_id in all_resolved for t in non_bookend_tasks)

    for task in manifest:
        if task.task_id in completed_ids or task.task_id in blocked_ids:
            continue
        if task.task_id in all_resolved:
            continue
        if task.bookend:
            if all_non_bookend_resolved:
                bookend_candidates.append(task)
        else:
            if all(dep in completed_ids for dep in task.depends_on):
                regular_candidates.append(task)

    candidates = regular_candidates or bookend_candidates
    if not candidates:
        return None
    candidates.sort(key=lambda t: (t.priority, _COMPLEXITY_ORDER.get(t.estimated_complexity, 1), t.task_id))
    return candidates[0]


# ---------------------------------------------------------------------------
# Morning report
# ---------------------------------------------------------------------------


def _extract_task_cost(result_data: dict[str, Any]) -> float:
    """Extract actual cost from a task's output_summary JSON."""
    summary = result_data.get("output_summary", "")
    if not summary:
        return result_data.get("cost_usd", 0.0)
    try:
        parsed = json.loads(summary)
        return parsed.get("total_cost_usd", 0.0)
    except (json.JSONDecodeError, TypeError):
        match = re.search(r'"total_cost_usd":\s*([0-9.]+)', summary)
        return float(match.group(1)) if match else result_data.get("cost_usd", 0.0)


def generate_morning_report(state: OvernightState, manifest: list[TaskDef]) -> None:
    """Generate the morning report markdown file."""
    lines = [f"# Overnight Report — {state.run_id}\n"]

    # Compute actual costs from output summaries
    total_actual_cost = 0.0
    task_costs: dict[str, float] = {}
    for task in manifest:
        result = state.results.get(task.task_id, {})
        cost = _extract_task_cost(result)
        task_costs[task.task_id] = cost
        total_actual_cost += cost

    # Summary
    total = len(manifest)
    lines.append("## Summary")
    lines.append(f"- Duration: {_format_duration(state)}")
    lines.append(f"- Tasks: {state.tasks_completed}/{total} completed, "
                 f"{state.tasks_failed} failed, {state.tasks_skipped} skipped, "
                 f"{state.tasks_rolled_back} rolled back")
    lines.append(f"- Status: **{state.status.upper()}**")
    lines.append(f"- Cost: **${total_actual_cost:.2f}**"
                 + (f" (tracked: ${state.total_cost_usd:.2f})" if state.total_cost_usd != total_actual_cost else ""))
    lines.append(f"- Git: {state.git_start_hash[:8]}..{git_head()[:8]}")
    lines.append("")

    # Completed tasks by category (with costs)
    by_category: dict[str, list[str]] = {}
    for task in manifest:
        result = state.results.get(task.task_id, {})
        if result.get("status") == "success":
            cat = task.category
            if cat not in by_category:
                by_category[cat] = []
            dur = result.get("duration_s", 0)
            cost = task_costs.get(task.task_id, 0.0)
            cost_str = f", ${cost:.2f}" if cost > 0 else ""
            by_category[cat].append(
                f"- [x] {task.name} ({dur:.0f}s, {task.model}{cost_str})"
            )

    if by_category:
        lines.append("## Completed Tasks")
        for cat, items in sorted(by_category.items()):
            lines.append(f"\n### {cat.replace('_', ' ').title()}")
            lines.extend(items)
        lines.append("")

    # Failed / rolled back
    problems = []
    for task in manifest:
        result = state.results.get(task.task_id, {})
        if result.get("status") in ("failed", "timeout", "rolled_back"):
            error = result.get("error", "unknown")
            problems.append(f"- **{task.task_id}** ({result['status']}): {error[:200]}")

    if problems:
        lines.append("## Issues (YOUR ATTENTION NEEDED)")
        lines.extend(problems)
        lines.append("")

    # Review first — prioritized list for the architect
    review_items: list[str] = []
    for task in manifest:
        result = state.results.get(task.task_id, {})
        if result.get("status") == "success" and task.category == "review":
            results_dir = OVERNIGHT_DIR / "results" / task.task_id
            review_file = results_dir / "review.md"
            if review_file.exists():
                review_items.append(f"- `{review_file.relative_to(PROJECT_DIR)}` — {task.name}")
    if review_items:
        lines.append("## Review First")
        lines.append("These review outputs need architect attention:")
        lines.extend(review_items)
        lines.append("")

    # Aggregate findings from findings.json files
    all_bugs: list[dict] = []
    all_tests: list[dict] = []
    all_spec_issues: list[dict] = []
    all_learnings: list[str] = []
    test_delta = 0
    for task in manifest:
        findings_file = OVERNIGHT_DIR / "results" / task.task_id / "findings.json"
        if findings_file.exists():
            try:
                findings = json.loads(findings_file.read_text(encoding="utf-8"))
                all_bugs.extend(findings.get("bugs_found", []))
                all_tests.extend(findings.get("tests_added", []))
                all_spec_issues.extend(findings.get("spec_issues", []))
                all_learnings.extend(findings.get("learnings", []))
                before = findings.get("test_count_before", 0)
                after = findings.get("test_count_after", 0)
                if before > 0 and after > 0:
                    test_delta += after - before
            except (json.JSONDecodeError, TypeError):
                pass

    if all_bugs or all_tests or all_spec_issues or all_learnings:
        lines.append("## Findings Summary")
        if all_bugs:
            critical = [b for b in all_bugs if b.get("severity") == "CRITICAL"]
            high = [b for b in all_bugs if b.get("severity") == "HIGH"]
            medium = [b for b in all_bugs if b.get("severity") == "MEDIUM"]
            lines.append(f"- **Bugs found:** {len(all_bugs)} "
                         f"({len(critical)} CRITICAL, {len(high)} HIGH, {len(medium)} MEDIUM)")
            for bug in critical + high:
                fixed = "FIXED" if bug.get("fixed") else "UNFIXED"
                lines.append(f"  - [{bug.get('severity')}] {bug.get('description', '?')} "
                             f"({bug.get('file', '?')}:{bug.get('line', '?')}) — {fixed}")
        if all_tests:
            lines.append(f"- **Tests added:** {len(all_tests)} (net delta: +{test_delta})")
        if all_spec_issues:
            lines.append(f"- **SPEC issues:** {len(all_spec_issues)}")
            for issue in all_spec_issues:
                lines.append(f"  - {issue.get('section', '?')}: {issue.get('issue', '?')}")
        if all_learnings:
            lines.append(f"- **Learnings:** {len(all_learnings)}")
            for learning in all_learnings[:10]:
                lines.append(f"  - {learning}")
        lines.append("")

    # Decisions
    if DECISIONS_LOG.exists():
        decisions_text = DECISIONS_LOG.read_text(encoding="utf-8")
        if decisions_text.strip():
            lines.append("## Autonomous Decisions Made")
            for line in decisions_text.strip().split("\n"):
                if line.startswith("["):
                    lines.append(f"- {line}")
            lines.append("")

    _atomic_write(MORNING_REPORT, "\n".join(lines) + "\n")
    print(f"Morning report written to {MORNING_REPORT}")


def _format_duration(state: OvernightState) -> str:
    """Format run duration as human-readable string."""
    try:
        start = datetime.fromisoformat(state.started_at)
        end = datetime.now(timezone.utc)
        delta = end - start
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
    except (ValueError, TypeError):
        return "unknown"


# ---------------------------------------------------------------------------
# Main orchestration loop
# ---------------------------------------------------------------------------


def run_overnight(
    hours: float = 7.5,
    max_cost_usd: float = 25.0,
    manifest_path: Path | None = None,
    single_task: str | None = None,
    dry_run: bool = False,
    resume: bool = False,
) -> None:
    """Main entry point for overnight orchestration."""
    print(f"=== KR Overnight Orchestrator v2 ===")
    print(f"Project: {PROJECT_DIR}")
    print(f"Duration: {hours} hours")
    print(f"Max cost: ${max_cost_usd}")
    print()

    # Pre-flight (skip for dry-run)
    if not dry_run:
        preflight_checks()
        _acquire_lock()

    # Load or generate manifest
    if manifest_path and manifest_path.exists():
        manifest = load_manifest(manifest_path)
        print(f"Loaded {len(manifest)} tasks from {manifest_path}")
    else:
        # Try to generate
        generator = PROJECT_DIR / "scripts" / "overnight_task_generator.py"
        if generator.exists():
            gen_result = subprocess.run(
                ["python", str(generator), "--output",
                 str(OVERNIGHT_DIR / "manifest.json")],
                capture_output=True, text=True, cwd=str(PROJECT_DIR),
            )
            if gen_result.returncode == 0:
                manifest = load_manifest(OVERNIGHT_DIR / "manifest.json")
                print(f"Generated {len(manifest)} tasks")
            else:
                print(f"Task generator failed: {gen_result.stderr[:500]}")
                sys.exit(1)
        else:
            print("No manifest and no task generator found.")
            print("Create overnight/manifest.json or scripts/overnight_task_generator.py")
            sys.exit(1)

    # Filter to single task if requested
    if single_task:
        manifest = [t for t in manifest if t.task_id == single_task]
        if not manifest:
            print(f"Task '{single_task}' not found in manifest")
            sys.exit(1)

    # Dry run — just print the plan
    if dry_run:
        print("\n=== DRY RUN — Execution Plan ===\n")
        for i, task in enumerate(sorted(manifest, key=lambda t: (t.priority, _COMPLEXITY_ORDER.get(t.estimated_complexity, 1), t.task_id)), 1):
            deps = f" (depends: {', '.join(task.depends_on)})" if task.depends_on else ""
            print(f"  {i:2d}. [{task.priority}] {task.task_id}: {task.name}")
            print(f"      Mode: {task.execution_mode} | Agent: {task.agent or '-'} "
                  f"| Model: {task.model} | Safety: {task.safety_level}{deps}")
            print(f"      Timeout: {task.timeout_minutes}m | Budget: ${task.max_budget_usd} "
                  f"| Complexity: {task.estimated_complexity}")
            print()
        print(f"Total tasks: {len(manifest)}")
        return

    # Resume or fresh start (FIX-4)
    now = datetime.now(timezone.utc)
    deadline = now + __import__("datetime").timedelta(hours=hours)
    start_monotonic = time.monotonic()
    max_seconds = hours * 3600
    resumed = False

    if resume:
        old_state = load_state()
        if old_state and old_state.status in ("stopped", "crashed", "failed"):
            state = old_state
            state.status = "running"
            state.consecutive_failures = 0
            state.consecutive_crashes = 0
            state.consecutive_timeouts = 0
            state.deadline = deadline.isoformat()
            resumed = True
            log_decision(f"RESUMED from previous run. {len(state.results)} tasks already resolved.")
            print(f"RESUME: {len(state.results)} tasks already resolved, continuing...")

    if not resumed:
        # Clear stale state from any previous run (BEFORE initializing new state)
        for stale in [STATE_FILE, PROGRESS_FILE, DECISIONS_LOG, HEARTBEAT_FILE]:
            if stale.exists():
                stale.unlink()

        state = OvernightState(
            run_id=now.strftime("%Y-%m-%d"),
            started_at=now.isoformat(),
            deadline=deadline.isoformat(),
            git_start_hash=git_head(),
        )
        log_decision(f"Overnight session started. {len(manifest)} tasks. Deadline: {deadline.isoformat()}")
    save_state(state)
    write_progress_file(state, manifest)

    # Initial commit
    git_commit(
        "overnight: initialize overnight session",
        [str(STATE_FILE), str(PROGRESS_FILE)],
    )

    # Graceful shutdown handler
    shutdown_requested = False

    def handle_signal(signum: int, frame: Any) -> None:
        nonlocal shutdown_requested
        shutdown_requested = True
        print("\nGraceful shutdown requested. Finishing current task...")

    signal.signal(signal.SIGINT, handle_signal)
    if sys.platform == "win32":
        try:
            signal.signal(signal.SIGBREAK, handle_signal)  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            pass  # SIGBREAK not available on all Windows configurations

    # Adaptive timeout tracking — learn from category timeouts (FIX-7)
    timeout_overrides: dict[str, float] = {}   # category -> multiplier
    category_timeouts: dict[str, int] = {}     # category -> consecutive timeout count

    # === Main loop ===
    print(f"\nStarting execution. Deadline: {deadline.strftime('%H:%M UTC')}")
    print("=" * 60)

    while not shutdown_requested:
        # Time check (monotonic — immune to sleep/NTP drift)
        elapsed = time.monotonic() - start_monotonic
        remaining = max_seconds - elapsed
        if remaining <= 0:
            log_decision("TIME LIMIT reached. Stopping.")
            break

        # Budget check
        if state.total_cost_usd >= max_cost_usd:
            log_decision(f"BUDGET LIMIT reached: ${state.total_cost_usd:.2f} >= ${max_cost_usd:.2f}")
            break

        # Circuit breaker — per-category thresholds
        if state.consecutive_crashes >= MAX_CONSECUTIVE_CRASHES:
            log_decision(f"CIRCUIT BREAKER (crash): {state.consecutive_crashes} consecutive crashes. Stopping.")
            state.status = "stopped"
            break
        if state.consecutive_timeouts >= MAX_CONSECUTIVE_TIMEOUTS:
            log_decision(f"CIRCUIT BREAKER (timeout): {state.consecutive_timeouts} consecutive timeouts. Pausing.")
            state.status = "stopped"
            break

        # Pick next task
        task = pick_next_ready(manifest, state)
        if task is None:
            # Recycling: if time remains, generate more hardening tasks
            min_recycle_seconds = 30 * 60  # Need at least 30 min for recycling
            if remaining > min_recycle_seconds:
                generator = PROJECT_DIR / "scripts" / "overnight_task_generator.py"
                if generator.exists():
                    log_decision(f"All manifest tasks resolved. {remaining / 60:.0f}m remaining — recycling.")
                    gen_result = subprocess.run(
                        ["python", str(generator), "--output",
                         str(OVERNIGHT_DIR / "manifest_recycled.json")],
                        capture_output=True, text=True, cwd=str(PROJECT_DIR),
                    )
                    if gen_result.returncode == 0:
                        recycled_path = OVERNIGHT_DIR / "manifest_recycled.json"
                        try:
                            new_tasks = load_manifest(recycled_path)
                            # Only add tasks not already in manifest
                            existing_ids = {t.task_id for t in manifest}
                            added = 0
                            for nt in new_tasks:
                                if nt.task_id not in existing_ids and nt.task_id not in state.results:
                                    manifest.append(nt)
                                    existing_ids.add(nt.task_id)
                                    added += 1
                            if added > 0:
                                log_decision(f"Recycled: {added} new tasks added from task generator.")
                                write_progress_file(state, manifest)
                                continue  # Re-enter loop to pick from new tasks
                        except (ValueError, json.JSONDecodeError) as e:
                            log_decision(f"Recycled manifest invalid: {e}")
            log_decision("All tasks completed or blocked.")
            break

        # Adaptive timeout: scale up based on complexity + category history (FIX-7)
        original_timeout = task.timeout_minutes
        effective_timeout = task.timeout_minutes
        multiplier = timeout_overrides.get(task.category, 1.0)
        if multiplier > 1.0:
            effective_timeout = int(effective_timeout * multiplier)
        if task.estimated_complexity == "high":
            effective_timeout = int(effective_timeout * 1.5)
        effective_timeout = min(effective_timeout, MAX_TIMEOUT_MINUTES)
        task.timeout_minutes = effective_timeout

        # Time guard: skip if task can't finish before deadline
        if remaining < task.timeout_minutes * 60:
            task.timeout_minutes = original_timeout  # restore before skip
            log_decision(f"SKIP {task.task_id}: {task.timeout_minutes}m timeout > "
                         f"{remaining / 60:.0f}m remaining")
            state.results[task.task_id] = {"status": "skipped", "error": "insufficient time"}
            state.tasks_skipped += 1
            save_state(state)
            continue

        # Execute
        timeout_note = f" (scaled {original_timeout}m→{effective_timeout}m)" if effective_timeout != original_timeout else ""
        print(f"\n>>> [{task.priority}] {task.task_id}: {task.name}")
        print(f"    Mode: {task.execution_mode} | Model: {task.model} | "
              f"Safety: {task.safety_level} | Timeout: {effective_timeout}m{timeout_note}")

        pre_snapshot = git_head()
        result = execute_task(task)
        task.timeout_minutes = original_timeout  # restore after execution

        # Quality gate for modification tasks
        if result.status == "success" and task.safety_level != "readonly":
            print(f"    Running quality gate (L1-L4)...")
            gate = run_quality_gate(task, pre_snapshot)
            if not gate["passed"]:
                print(f"    QUALITY GATE FAILED — rolling back")
                git_rollback(pre_snapshot)
                result.status = "rolled_back"
                result.gate_result = gate
                state.tasks_rolled_back += 1
            else:
                # Auto-commit guard: if CLI didn't commit, commit for it
                current_head = git_head()
                if current_head == pre_snapshot:
                    uncommitted = subprocess.run(
                        ["git", "status", "--porcelain", "--", "engines/", "shared/",
                         "tests/", "overnight/results/"],
                        capture_output=True, text=True, cwd=str(PROJECT_DIR),
                    ).stdout.strip()
                    if uncommitted:
                        log_decision(
                            f"AUTO-COMMIT: {task.task_id} left uncommitted changes — committing",
                        )
                        git_commit(
                            f"overnight: {task.task_id} — auto-commit (CLI missed commit step)",
                        )
                        print(f"    Auto-committed (CLI missed commit step)")

        # L5: Optional Codex cross-verification (skip if Codex unavailable)
        if (result.status == "success"
                and task.execution_mode not in ("codex", "gemini")
                and task.safety_level != "readonly"
                and not os.environ.get("KR_SKIP_CODEX")):
            print(f"    Running Codex cross-verification (L5)...")
            try:
                codex_review = run_codex_verification(task)
                if codex_review.get("discrepancies"):
                    log_decision(
                        f"CODEX DISCREPANCY for {task.task_id}: see {codex_review.get('review_file', 'N/A')}",
                        codex_review.get("review", "")[:300],
                    )
                    print(f"    Codex flagged discrepancies — logged for morning review")
                else:
                    print(f"    Codex verification: CLEAN")
            except Exception as e:
                log_decision(f"Codex verification failed for {task.task_id}: {e}")

        # L6: Optional Gemini adversarial challenge (skip if unavailable)
        if (result.status == "success"
                and task.execution_mode not in ("codex", "gemini")
                and task.safety_level != "readonly"
                and not os.environ.get("KR_SKIP_GEMINI")):
            print(f"    Running Gemini adversarial challenge (L6)...")
            try:
                diff_result = subprocess.run(
                    ["git", "diff", pre_snapshot, "HEAD"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    cwd=str(PROJECT_DIR),
                )
                code_diff = diff_result.stdout[:6000] if diff_result.stdout else "No diff available"
                gemini_result = run_gemini_adversarial_challenge(task, code_diff)
                if gemini_result.get("concerns_raised"):
                    log_decision(
                        f"GEMINI CONCERN for {task.task_id}: see {gemini_result.get('challenge_file', 'N/A')}",
                        gemini_result.get("challenge", "")[:300],
                    )
                    print(f"    Gemini raised concerns — logged for morning review")
                else:
                    print(f"    Gemini adversarial challenge: CLEAN")
            except Exception as e:
                log_decision(f"Gemini adversarial challenge failed for {task.task_id}: {e}")

        # Track cost
        state.total_cost_usd += result.cost_usd

        # Record result
        state.results[task.task_id] = asdict(result)
        if result.status == "success":
            state.tasks_completed += 1
            state.consecutive_failures = 0
            state.consecutive_crashes = 0
            state.consecutive_timeouts = 0
            print(f"    SUCCESS ({result.duration_s:.0f}s)")
        elif result.status == "partial_success":
            state.tasks_completed += 1
            state.consecutive_failures = 0
            state.consecutive_crashes = 0
            state.consecutive_timeouts = 0
            print(f"    PARTIAL SUCCESS ({result.duration_s:.0f}s) — output preserved")
        elif result.status == "timeout":
            state.tasks_failed += 1
            state.consecutive_failures += 1
            state.consecutive_timeouts += 1
            state.consecutive_crashes = 0  # timeout is not a crash
            print(f"    TIMEOUT: {result.error or 'unknown'}")
        elif result.status == "failed":
            state.tasks_failed += 1
            state.consecutive_failures += 1
            state.consecutive_crashes += 1
            state.consecutive_timeouts = 0  # crash is not a timeout
            print(f"    FAILED: {result.error or 'unknown'}")
        elif result.status == "rolled_back":
            state.tasks_rolled_back += 1
            # Quality issue, not system failure — don't trigger circuit breaker
            print(f"    ROLLED BACK (quality gate)")

        # Adaptive timeout learning (FIX-7): bump timeout for category after timeouts
        if result.status in ("timeout", "partial_success"):
            cat = task.category
            category_timeouts[cat] = category_timeouts.get(cat, 0) + 1
            # +50% per consecutive timeout in this category, capped at 2.5x
            timeout_overrides[cat] = 1.0 + 0.5 * min(category_timeouts[cat], 3)
        elif result.status == "success":
            category_timeouts.pop(task.category, None)
            timeout_overrides.pop(task.category, None)

        write_progress_file(state, manifest)
        save_state(state)
        _write_heartbeat(
            task.task_id, result.status, state,
            len(manifest), start_monotonic,
        )

    # === Shutdown ===
    if state.status == "running":
        if state.tasks_completed == 0 and (state.tasks_failed > 0 or state.tasks_skipped > 0):
            state.status = "failed"
        else:
            state.status = "completed"
    save_state(state)
    generate_morning_report(state, manifest)
    _release_lock()

    print("\n" + "=" * 60)
    print(f"Overnight session {state.status}.")
    print(f"Tasks: {state.tasks_completed} completed, {state.tasks_failed} failed, "
          f"{state.tasks_skipped} skipped, {state.tasks_rolled_back} rolled back")
    print(f"Report: {MORNING_REPORT}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KR Overnight Autonomous Work Orchestrator v2",
    )
    parser.add_argument(
        "--hours", type=float, default=7.5,
        help="Maximum hours to run (default: 7.5)",
    )
    parser.add_argument(
        "--max-cost-usd", type=float, default=25.0,
        help="Maximum Claude API cost in USD (default: 25.0)",
    )
    parser.add_argument(
        "--manifest", type=str, default=None,
        help="Path to task manifest JSON file",
    )
    parser.add_argument(
        "--task", type=str, default=None,
        help="Run a single task by ID",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print execution plan without running tasks",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from last state.json instead of starting fresh",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest) if args.manifest else None

    run_overnight(
        hours=args.hours,
        max_cost_usd=args.max_cost_usd,
        manifest_path=manifest_path,
        single_task=args.task,
        dry_run=args.dry_run,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
