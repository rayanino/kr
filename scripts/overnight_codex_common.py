"""Shared types and helpers for the isolated Codex overnight runtime."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parent.parent
OVERNIGHT_CODEX_DIR = PROJECT_DIR / "overnight_codex"
RESULTS_DIR = OVERNIGHT_CODEX_DIR / "results"
QUEUE_DIR = OVERNIGHT_CODEX_DIR / "queue"
WORKTREES_DIR = OVERNIGHT_CODEX_DIR / "worktrees"
STATE_FILE = OVERNIGHT_CODEX_DIR / "state.json"
PROGRESS_FILE = OVERNIGHT_CODEX_DIR / "progress.md"
DECISIONS_LOG = OVERNIGHT_CODEX_DIR / "decisions.log"
MORNING_REPORT = OVERNIGHT_CODEX_DIR / "MORNING_REPORT.md"
HEARTBEAT_FILE = OVERNIGHT_CODEX_DIR / ".heartbeat"
LOCK_FILE = OVERNIGHT_CODEX_DIR / ".overnight_codex.lock"
FINDINGS_TRACKER = OVERNIGHT_CODEX_DIR / "FINDINGS_TRACKER.md"
CUMULATIVE_FINDINGS = OVERNIGHT_CODEX_DIR / "CUMULATIVE_FINDINGS.md"
CREATIVE_RUN_LOG = OVERNIGHT_CODEX_DIR / "creative_run_log.json"

ALLOWED_CATEGORIES = {
    "review",
    "test",
    "validation",
    "spec",
    "doc",
    "code_quality",
    "creative",
}
ALLOWED_RUNNER_MODES = {"exec", "review"}
ALLOWED_SANDBOX_MODES = {"read-only", "workspace-write"}
ALLOWED_WRITE_POLICIES = {"readonly", "guarded_write"}
ALLOWED_OUTPUT_MODES = {"json"}
ALLOWED_COMPLEXITIES = {"low", "medium", "high"}
ALLOWED_PRIORITIES = {"HIGH", "MEDIUM", "LOW"}
ALLOWED_EFFORTS = {"S", "M", "L"}
FORBIDDEN_CAPABILITY_FLAGS = {
    "requires_web",
    "requires_arabic_judgment",
    "generates_arabic_content",
}
FORBIDDEN_EDIT_PREFIXES = (
    ".claude/",
    "overnight/",
    "overnight_codex/",
    "docs/superpowers/",
)
FORBIDDEN_EDIT_EXACT = {
    "CLAUDE.md",
    "NEXT.md",
    "scripts/overnight_orchestrator.py",
    "scripts/overnight_task_generator.py",
    "scripts/weekend_parallel.py",
    "scripts/start_overnight.sh",
    "scripts/start_sprint.sh",
}
PIPELINE_ORDER = ["source", "normalization", "excerpting", "taxonomy", "synthesis"]
COMPLEXITY_ORDER = {"low": 0, "medium": 1, "high": 2}


ACTION_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["id", "category", "summary", "effort", "priority"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "category": {"type": "string", "pattern": r"^[A-Z_]+$"},
        "summary": {"type": "string", "minLength": 1},
        "effort": {"type": "string", "enum": sorted(ALLOWED_EFFORTS)},
        "priority": {"type": "string", "enum": sorted(ALLOWED_PRIORITIES)},
    },
}

FINAL_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "task_status",
        "summary",
        "commands_run",
        "evidence",
        "findings",
        "action_items",
        "files_changed",
        "tests_run",
    ],
    "properties": {
        "task_status": {
            "type": "string",
            "enum": ["success", "truncated", "failed"],
        },
        "summary": {"type": "string", "minLength": 1},
        "commands_run": {
            "type": "array",
            "items": {"type": "string"},
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["path", "detail"],
                "properties": {
                    "path": {"type": "string", "minLength": 1},
                    "detail": {"type": "string", "minLength": 1},
                },
            },
        },
        "findings": {
            "type": "array",
            "items": {"type": "string"},
        },
        "action_items": {
            "type": "array",
            "items": ACTION_ITEM_SCHEMA,
        },
        "files_changed": {
            "type": "array",
            "items": {"type": "string"},
        },
        "tests_run": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
}


@dataclass
class CodexTaskDef:
    """Task definition for the isolated Codex overnight runtime."""

    task_id: str
    name: str
    category: str
    prompt: str
    runner_mode: str = "exec"
    sandbox_mode: str = "read-only"
    write_policy: str = "readonly"
    model: str = "gpt-5.4"
    timeout_minutes: int = 25
    depends_on: list[str] = field(default_factory=list)
    priority: int = 5
    bookend: bool = False
    estimated_complexity: str = "medium"
    output_mode: str = "json"
    expected_artifact: str = "final_response.json"
    capability_flags: list[str] = field(default_factory=list)
    authority_level: str = "low"

    def validate(self) -> None:
        if self.category not in ALLOWED_CATEGORIES:
            raise ValueError(f"Unsupported category for {self.task_id}: {self.category}")
        if self.runner_mode not in ALLOWED_RUNNER_MODES:
            raise ValueError(f"Unsupported runner_mode for {self.task_id}: {self.runner_mode}")
        if self.sandbox_mode not in ALLOWED_SANDBOX_MODES:
            raise ValueError(f"Unsupported sandbox_mode for {self.task_id}: {self.sandbox_mode}")
        if self.write_policy not in ALLOWED_WRITE_POLICIES:
            raise ValueError(f"Unsupported write_policy for {self.task_id}: {self.write_policy}")
        if self.output_mode not in ALLOWED_OUTPUT_MODES:
            raise ValueError(f"Unsupported output_mode for {self.task_id}: {self.output_mode}")
        if self.estimated_complexity not in ALLOWED_COMPLEXITIES:
            raise ValueError(
                f"Unsupported estimated_complexity for {self.task_id}: "
                f"{self.estimated_complexity}"
            )
        if self.timeout_minutes <= 0:
            raise ValueError(f"timeout_minutes must be > 0 for {self.task_id}")
        forbidden = set(self.capability_flags) & FORBIDDEN_CAPABILITY_FLAGS
        if forbidden:
            joined = ", ".join(sorted(forbidden))
            raise ValueError(f"Forbidden capability flags for {self.task_id}: {joined}")
        if self.write_policy == "readonly" and self.sandbox_mode != "read-only":
            raise ValueError(
                f"Readonly task {self.task_id} must use sandbox_mode='read-only'"
            )
        if self.write_policy == "guarded_write" and self.sandbox_mode != "workspace-write":
            raise ValueError(
                f"Guarded write task {self.task_id} must use sandbox_mode='workspace-write'"
            )


@dataclass
class TaskResult:
    """Execution result for a Codex overnight task."""

    task_id: str
    status: str
    start_time: str = ""
    end_time: str = ""
    duration_s: float = 0.0
    summary: str = ""
    error: str | None = None
    artifact_path: str = ""
    branch_name: str | None = None
    patch_path: str | None = None
    commit_hash: str | None = None
    review_path: str | None = None
    auto_applied: bool = False
    files_changed: list[str] = field(default_factory=list)
    tests_run: list[str] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    queued_only: bool = False
    queue_reason: str | None = None


@dataclass
class OvernightCodexState:
    """Persistent state for unattended Codex runs."""

    run_id: str
    started_at: str
    deadline: str
    launch_head: str
    apply_mode: str
    baseline_clean: bool
    baseline_tests_passed: bool
    status: str = "running"
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_skipped: int = 0
    tasks_queued: int = 0
    consecutive_failures: int = 0
    consecutive_timeouts: int = 0
    results: dict[str, dict[str, Any]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return utc_now().isoformat()


def atomic_write(path: Path, content: str) -> None:
    """Write a file atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def write_json(path: Path, payload: Any) -> None:
    """Write JSON atomically."""
    atomic_write(path, json.dumps(payload, indent=2, ensure_ascii=False))


def load_manifest(path: Path) -> list[CodexTaskDef]:
    """Load and validate a manifest."""
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data["tasks"] if isinstance(data, dict) else data
    tasks: list[CodexTaskDef] = []
    seen: set[str] = set()
    for item in items:
        task = CodexTaskDef(**item)
        task.validate()
        if task.task_id in seen:
            raise ValueError(f"Duplicate task_id in manifest: {task.task_id}")
        seen.add(task.task_id)
        tasks.append(task)
    return tasks


def manifest_to_json(tasks: list[CodexTaskDef]) -> dict[str, Any]:
    """Serialize a manifest."""
    return {"tasks": [asdict(task) for task in tasks]}


def ensure_runtime_dirs() -> None:
    """Ensure the isolated runtime directories exist."""
    for path in (
        OVERNIGHT_CODEX_DIR,
        RESULTS_DIR,
        QUEUE_DIR,
        WORKTREES_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def repo_rel(path: str | Path) -> str:
    """Return a repo-relative path using forward slashes."""
    as_path = Path(path)
    try:
        rel = as_path.resolve().relative_to(PROJECT_DIR.resolve())
    except ValueError:
        rel = as_path
    return str(rel).replace("\\", "/")


def safe_slug(value: str) -> str:
    """Create a conservative slug for branch names and task-derived paths."""
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9._-]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-.")
    return lowered or "task"


def git_head(cwd: Path | None = None) -> str:
    """Return HEAD for the given repository."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=str(cwd or PROJECT_DIR),
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout.strip()


def git_status_porcelain(
    cwd: Path | None = None,
    ignore_prefixes: tuple[str, ...] = (
        "overnight_codex/",
        ".claude/session_state",
        ".claude/session_state.json",
    ),
) -> list[str]:
    """Return non-ignored porcelain lines."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=str(cwd or PROJECT_DIR),
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    lines: list[str] = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        candidate = raw[3:] if len(raw) > 3 else raw.strip()
        candidate = candidate.replace("\\", "/")
        if any(candidate.startswith(prefix) for prefix in ignore_prefixes):
            continue
        lines.append(raw)
    return lines


def worktree_changed_files(worktree_path: Path) -> list[str]:
    """List changed files in a worktree."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=str(worktree_path),
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    files: list[str] = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        candidate = raw[3:] if len(raw) > 3 else raw.strip()
        files.append(candidate.replace("\\", "/"))
    return files


def has_forbidden_edits(changed_files: list[str]) -> list[str]:
    """Return forbidden changed files."""
    violations: list[str] = []
    for file_path in changed_files:
        normalized = file_path.replace("\\", "/")
        if normalized in FORBIDDEN_EDIT_EXACT:
            violations.append(normalized)
            continue
        if any(normalized.startswith(prefix) for prefix in FORBIDDEN_EDIT_PREFIXES):
            violations.append(normalized)
    return violations


def write_progress_file(state: OvernightCodexState, manifest: list[CodexTaskDef]) -> None:
    """Write a compact progress file."""
    lines = [f"# Overnight Codex Progress — {state.run_id}", ""]
    completed: list[str] = []
    queued: list[str] = []
    remaining: list[str] = []

    for task in manifest:
        result = state.results.get(task.task_id, {})
        status = result.get("status")
        if status == "success":
            marker = "x"
            suffix = " (auto-applied)" if result.get("auto_applied") else ""
            completed.append(f"- [{marker}] {task.task_id}: {task.name}{suffix}")
        elif status == "queued":
            queued.append(f"- [~] {task.task_id}: {task.name} (queued patch)")
        elif status in {"failed", "timeout", "partial_success", "skipped"}:
            completed.append(f"- [~] {task.task_id}: {task.name} ({status})")
        else:
            remaining.append(f"- [ ] {task.task_id}: {task.name}")

    if completed:
        lines.append("## Completed")
        lines.extend(completed)
        lines.append("")
    if queued:
        lines.append("## Queued")
        lines.extend(queued)
        lines.append("")
    if remaining:
        lines.append("## Remaining")
        lines.extend(remaining)
        lines.append("")

    atomic_write(PROGRESS_FILE, "\n".join(lines).rstrip() + "\n")


def validate_action_items(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Validate creative action items before tracker ingestion."""
    validated: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        action_id = str(item.get("id", "")).strip()
        category = str(item.get("category", "")).strip()
        summary = str(item.get("summary", "")).strip()
        effort = str(item.get("effort", "")).strip()
        priority = str(item.get("priority", "")).strip()
        if not all((action_id, category, summary, effort, priority)):
            continue
        if effort not in ALLOWED_EFFORTS or priority not in ALLOWED_PRIORITIES:
            continue
        if not re.fullmatch(r"[A-Z_]+", category):
            continue
        validated.append(
            {
                "id": action_id,
                "category": category,
                "summary": summary.replace("\r", " ").replace("\n", " ").strip(),
                "effort": effort,
                "priority": priority,
            }
        )
    return validated
