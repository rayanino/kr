from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from scripts import append_codex_findings
from scripts import overnight_codex_backlog as backlog
from scripts import overnight_codex_common as common
from scripts import overnight_codex_orchestrator as orchestrator
from scripts import overnight_codex_task_generator as task_generator
from scripts.overnight_codex_common import CodexTaskDef, OvernightCodexState


def test_classify_quality_gate_failures_distinguishes_policy_and_validation() -> None:
    assert orchestrator._classify_quality_gate_failures(
        ["Guarded task touched files outside allowlist: ['engines/excerpting/contracts.py']"]
    ) == "policy_blocked"
    assert orchestrator._classify_quality_gate_failures(
        ["pytest failed for excerpting: 1 failed, 698 passed"]
    ) == "validation_failed"


def test_creative_run_log_key_matches_generator_cooldown_shape() -> None:
    key = orchestrator._creative_run_log_key(
        "creative-innovation-local_failure_mode_review-excerpting"
    )
    assert key == "innovation/local_failure_mode_review:excerpting"


def test_extract_environment_notes_detects_runtime_blockers() -> None:
    payload = {
        "summary": "Test execution was blocked because no usable Python runtime was available in the sandbox.",
        "commands_run": [],
        "tests_run": [
            "Blocked: no `python` executable in the sandbox, and uv could not provision a runtime."
        ],
        "evidence": [],
    }
    notes = orchestrator._extract_environment_notes(payload)
    assert "No usable Python runtime was available in the task sandbox." in notes
    assert "uv could not provision a runtime inside the task sandbox." in notes


def test_update_creative_run_log_writes_generator_key(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    log_path = tmp_path / "creative_run_log.json"
    monkeypatch.setattr(orchestrator, "CREATIVE_RUN_LOG", log_path)

    orchestrator._update_creative_run_log("creative-innovation-local_cost_efficiency-excerpting")

    payload = json.loads(log_path.read_text(encoding="utf-8"))
    assert payload["runs"]["innovation/local_cost_efficiency:excerpting"]


def test_execute_task_readonly_uses_disposable_workspace(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(orchestrator, "RESULTS_DIR", tmp_path / "results")
    workspace = tmp_path / "readonly-workspace"
    workspace.mkdir()
    observed: dict[str, Path] = {}

    def fake_prepare_worktree(*args: object, **kwargs: object) -> None:  # pragma: no cover
        raise AssertionError("readonly task should not create a write worktree")

    def fake_prepare_readonly_workspace(
        task: CodexTaskDef, launch_head: str
    ) -> Path:
        assert task.task_id == "readonly-review"
        assert launch_head == "abc123"
        return workspace

    def fake_codex_exec(
        codex_bin: str,
        *,
        prompt: str,
        workdir: Path,
        sandbox_mode: str,
        output_path: Path,
        schema_path: Path,
        timeout_minutes: int,
    ) -> subprocess.CompletedProcess[str]:
        output_path.write_text(
            json.dumps(
                {
                    "task_status": "success",
                    "summary": "Readonly review completed with concrete evidence.",
                    "commands_run": ["Get-Content engines/excerpting/src/writer.py"],
                    "evidence": [
                        {
                            "path": "engines/excerpting/src/writer.py",
                            "detail": "Inspected writer serialization logic.",
                        }
                    ],
                    "findings": [],
                    "action_items": [],
                    "files_changed": [],
                    "tests_run": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        observed["workdir"] = workdir
        observed["output_path"] = output_path
        return subprocess.CompletedProcess(["codex"], 0, "", "")

    monkeypatch.setattr(orchestrator, "prepare_worktree", fake_prepare_worktree)
    monkeypatch.setattr(orchestrator, "prepare_readonly_workspace", fake_prepare_readonly_workspace)
    monkeypatch.setattr(orchestrator, "cleanup_readonly_workspace", lambda worktree_path: None)
    monkeypatch.setattr(orchestrator, "_snapshot_readonly_guard", lambda: {})
    monkeypatch.setattr(orchestrator, "_readonly_guard_failures", lambda snapshot: [])
    monkeypatch.setattr(orchestrator, "_codex_exec", fake_codex_exec)

    task = CodexTaskDef(
        task_id="readonly-review",
        name="Readonly review",
        category="review",
        prompt="Inspect the repo only.",
        sandbox_mode="read-only",
        write_policy="readonly",
        expected_artifact="review.json",
    )
    state = OvernightCodexState(
        run_id="2026-03-30",
        started_at="2026-03-30T00:00:00+00:00",
        deadline="2026-03-30T08:00:00+00:00",
        launch_head="abc123",
        apply_mode="queue_only",
        baseline_clean=False,
        baseline_tests_passed=False,
    )

    result = orchestrator.execute_task(task, state=state, codex_bin="codex")

    assert result.status == "success"
    assert result.failure_class is None
    assert observed["workdir"] == workspace
    assert observed["output_path"].parent != tmp_path / "results" / "readonly-review"
    assert (tmp_path / "results" / "readonly-review" / "packet.json").exists()
    assert (tmp_path / "results" / "readonly-review" / "review.json").exists()


def test_append_findings_updates_registry_recurrence(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    results_dir = tmp_path / "results"
    actionable_dir = results_dir / "creative-signal"
    actionable_dir.mkdir(parents=True)
    actionable_path = actionable_dir / "actionable.json"
    actionable_path.write_text(
        json.dumps(
            [
                {
                    "id": "CREATIVE-1",
                    "category": "ARCH",
                    "summary": "Recurring architectural signal",
                    "effort": "M",
                    "priority": "HIGH",
                }
            ]
        ),
        encoding="utf-8",
    )

    tracker = tmp_path / "FINDINGS_TRACKER.md"
    registry = tmp_path / "findings_registry.json"
    monkeypatch.setattr(append_codex_findings, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(append_codex_findings, "FINDINGS_TRACKER", tracker)
    monkeypatch.setattr(append_codex_findings, "FINDINGS_REGISTRY_FILE", registry)

    assert append_codex_findings.append_findings() == 1
    assert append_codex_findings.append_findings() == 0

    payload = json.loads(registry.read_text(encoding="utf-8"))
    assert payload["items"]["CREATIVE-1"]["occurrences"] == 1


def test_validate_task_payload_rejects_legacy_overnight_root() -> None:
    payload = {
        "task_status": "success",
        "summary": "Wrote findings to overnight/results/review-recent-excerpting/review.md.",
        "commands_run": ["Get-Content engines/excerpting/src/writer.py"],
        "evidence": [
            {
                "path": "overnight/results/review-recent-excerpting/review.md",
                "detail": "Legacy path should be rejected.",
            }
        ],
        "findings": [],
        "action_items": [],
        "files_changed": [],
        "tests_run": [],
    }
    task = CodexTaskDef(
        task_id="legacy-root-check",
        name="Legacy root check",
        category="review",
        prompt="Review only.",
        sandbox_mode="read-only",
        write_policy="readonly",
    )

    with pytest.raises(ValueError, match="legacy overnight root"):
        orchestrator._validate_task_payload(task, payload)


def test_payload_from_markdown_marks_truncated(tmp_path: Path) -> None:
    markdown = tmp_path / "fallback.md"
    markdown.write_text(
        "\n".join(
            [
                "# Fallback",
                "",
                "Summary paragraph.",
                "",
                "## Findings",
                "- First finding",
            ]
        ),
        encoding="utf-8",
    )
    task = CodexTaskDef(
        task_id="markdown-fallback",
        name="Markdown fallback",
        category="review",
        prompt="Fallback only.",
        sandbox_mode="read-only",
        write_policy="readonly",
    )

    payload = orchestrator._payload_from_markdown(task, markdown)

    assert payload["task_status"] == "truncated"


def test_sync_backlog_from_artifacts_creates_proposed_item(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    results_dir = tmp_path / "results"
    task_dir = results_dir / "review-recent-excerpting"
    task_dir.mkdir(parents=True)
    (task_dir / "final_response.json").write_text(
        json.dumps(
            {
                "task_status": "success",
                "summary": "Review completed.",
                "commands_run": ["Get-Content engines/excerpting/src/phase2_classify.py"],
                "evidence": [
                    {
                        "path": "engines/excerpting/src/phase2_classify.py",
                        "detail": "Inspected repair path.",
                    }
                ],
                "findings": ["Gap found."],
                "action_items": [
                    {
                        "id": "A1",
                        "category": "SPEC_COMPLIANCE",
                        "summary": "Restore spec-compliant schema retry behavior.",
                        "effort": "S",
                        "priority": "HIGH",
                    }
                ],
                "files_changed": [],
                "tests_run": [],
            }
        ),
        encoding="utf-8",
    )

    backlog_file = tmp_path / "backlog.json"
    monkeypatch.setattr(backlog, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(backlog, "QUEUE_DIR", tmp_path / "queue")
    monkeypatch.setattr(backlog, "BACKLOG_FILE", backlog_file)
    monkeypatch.setattr(backlog, "FINDINGS_REGISTRY_FILE", tmp_path / "findings_registry.json")

    summary = backlog.sync_backlog_from_artifacts("2026-03-30")
    summary_repeat = backlog.sync_backlog_from_artifacts("2026-03-30")

    assert summary["created"] == 1
    assert summary_repeat["created"] == 0
    assert summary_repeat["updated"] == 0
    payload = json.loads(backlog_file.read_text(encoding="utf-8"))
    items = list(payload["items"].values())
    assert len(items) == 1
    item = items[0]
    assert item["status"] == "proposed"
    assert item["subsystem"] == "excerpting"
    assert item["allowed_write_prefixes"] == [
        "engines/excerpting/src/",
        "engines/excerpting/tests/",
    ]
    assert item["occurrences"] == 1


def test_build_backlog_write_tasks_uses_only_approved_items(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        task_generator,
        "load_active_authority",
        lambda: {"active_authority": "codex", "runtime_mode": "autonomous_codex"},
    )
    monkeypatch.setattr(
        task_generator,
        "approved_backlog_items",
        lambda frontier_tag: [
            {
                "item_id": "excerpting-retry-fix",
                "summary": "Restore spec-compliant schema retry behavior.",
                "frontier_tag": frontier_tag,
                "allowed_write_prefixes": [
                    "engines/excerpting/src/",
                    "engines/excerpting/tests/",
                ],
                "source_task_ids": ["review-recent-excerpting"],
                "evidence_paths": ["engines/excerpting/src/phase2_classify.py"],
                "gate_mode": "python",
            }
        ],
    )

    tasks = task_generator.build_backlog_write_tasks("excerpting")

    assert len(tasks) == 1
    task = tasks[0]
    assert task.write_policy == "guarded_write"
    assert task.backlog_item_id == "excerpting-retry-fix"
    assert task.gate_mode == "python"
    assert task.allowed_write_prefixes == [
        "engines/excerpting/src/",
        "engines/excerpting/tests/",
    ]


def test_has_forbidden_edits_allows_docs_codex() -> None:
    violations = common.has_forbidden_edits(
        [
            "docs/codex/runtime-policy.md",
            "docs/superpowers/secret.md",
            "overnight_codex/README.md",
        ]
    )

    assert "docs/codex/runtime-policy.md" not in violations
    assert "docs/superpowers/secret.md" in violations
    assert "overnight_codex/README.md" in violations


def test_load_active_authority_ignores_unknown_keys(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    authority_file = tmp_path / "ACTIVE_AUTHORITY.md"
    authority_file.write_text(
        "\n".join(
            [
                "# Active Authority",
                "active_authority: codex",
                "runtime_mode: autonomous_codex",
                "note: should be ignored",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(common, "ACTIVE_AUTHORITY_FILE", authority_file)

    parsed = common.load_active_authority()

    assert parsed["active_authority"] == "codex"
    assert parsed["runtime_mode"] == "autonomous_codex"
    assert "note" not in parsed


def test_project_python_prefers_repo_venv(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("", encoding="utf-8")
    monkeypatch.setattr(common, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(common.sys, "executable", "/usr/bin/python3")
    monkeypatch.delenv("KR_RUNTIME_PYTHON", raising=False)
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)

    assert common.project_python() == str(venv_python)


def test_rewrite_python_command_uses_project_python(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(common, "project_python", lambda: "/tmp/kr/.venv/bin/python")

    assert common.rewrite_python_command(["python", "-m", "pytest"]) == [
        "/tmp/kr/.venv/bin/python",
        "-m",
        "pytest",
    ]
    assert common.rewrite_python_command(["git", "status"]) == ["git", "status"]


def test_requires_shadow_setup_restrictions_uses_runtime_mode() -> None:
    shadow_state = OvernightCodexState(
        run_id="2026-03-30",
        started_at="2026-03-30T00:00:00+00:00",
        deadline="2026-03-30T08:00:00+00:00",
        launch_head="abc123",
        apply_mode="queue_only",
        baseline_clean=False,
        baseline_tests_passed=False,
        active_authority="codex",
        runtime_mode="shadow_setup",
    )
    auto_state = OvernightCodexState(
        run_id="2026-03-30",
        started_at="2026-03-30T00:00:00+00:00",
        deadline="2026-03-30T08:00:00+00:00",
        launch_head="abc123",
        apply_mode="auto_apply",
        baseline_clean=True,
        baseline_tests_passed=True,
        active_authority="codex",
        runtime_mode="autonomous_codex",
    )

    assert orchestrator._requires_shadow_setup_restrictions(shadow_state) is True
    assert orchestrator._requires_shadow_setup_restrictions(auto_state) is False


def test_affected_engines_includes_taxonomy_and_synthesis_for_shared_changes() -> None:
    engines = orchestrator._affected_engines(["shared/llm/cli_adapter.py"])

    assert engines == {"source", "normalization", "excerpting", "taxonomy", "synthesis"}


def test_detect_active_claude_session_checks_windows_processes_in_wsl(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(orchestrator, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(orchestrator.sys, "platform", "linux")
    monkeypatch.setattr(
        orchestrator.Path,
        "read_text",
        lambda self, encoding="utf-8": "6.6.87.2-microsoft-standard-WSL2",
    )

    def fake_run(cmd: list[str], timeout: int, **_: object) -> subprocess.CompletedProcess[str]:
        assert cmd[:2] == ["tasklist.exe", "/FI"]
        return subprocess.CompletedProcess(cmd, 0, "claude.exe                    1234 Console                    1    10,000 K", "")

    monkeypatch.setattr(orchestrator, "_run_subprocess_safe", fake_run)

    active, notes = orchestrator.detect_active_claude_session()

    assert active is True
    assert any("claude.exe" in note for note in notes)


def test_detect_active_claude_session_ignores_wsl_clone_session_state_without_windows_home(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    session_state = tmp_path / ".claude" / "session_state.json"
    session_state.parent.mkdir(parents=True)
    session_state.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(orchestrator, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(orchestrator.sys, "platform", "linux")
    monkeypatch.setattr(
        orchestrator.Path,
        "read_text",
        lambda self, encoding="utf-8": "6.6.87.2-microsoft-standard-WSL2",
    )
    monkeypatch.delenv("KR_WINDOWS_HOME", raising=False)
    monkeypatch.setattr(
        orchestrator,
        "_run_subprocess_safe",
        lambda cmd, timeout, **_: subprocess.CompletedProcess(cmd, 0, "", ""),
    )

    active, notes = orchestrator.detect_active_claude_session()

    assert active is False
    assert notes == []


def test_find_codex_uses_linux_local_bin_fallback(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    codex_path = tmp_path / ".local" / "bin" / "codex"
    codex_path.parent.mkdir(parents=True)
    codex_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(orchestrator.shutil, "which", lambda name: None)
    monkeypatch.setattr(orchestrator.sys, "platform", "linux")
    monkeypatch.setattr(orchestrator.Path, "home", lambda: tmp_path)

    assert orchestrator._find_codex() == str(codex_path)


def test_find_codex_ignores_windows_interop_path_in_wsl(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    codex_path = tmp_path / ".local" / "bin" / "codex"
    codex_path.parent.mkdir(parents=True)
    codex_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        orchestrator.shutil,
        "which",
        lambda name: "/mnt/c/Users/Rayane/AppData/Roaming/npm/codex.cmd",
    )
    monkeypatch.setattr(orchestrator.sys, "platform", "linux")
    monkeypatch.setattr(orchestrator.Path, "home", lambda: tmp_path)

    assert orchestrator._find_codex() == str(codex_path)


def test_failure_breaker_trips_on_alternating_infra_and_timeout() -> None:
    state = OvernightCodexState(
        run_id="2026-03-30",
        started_at="2026-03-30T00:00:00+00:00",
        deadline="2026-03-30T08:00:00+00:00",
        launch_head="abc123",
        apply_mode="queue_only",
        baseline_clean=False,
        baseline_tests_passed=False,
    )
    state.consecutive_failures = 3
    state.consecutive_breaker_failures = 1
    state.consecutive_timeouts = 0

    assert orchestrator._failure_breaker_tripped(state) is True


def test_run_overnight_resume_refreshes_apply_mode(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    captured_states: list[OvernightCodexState] = []
    previous = OvernightCodexState(
        run_id="2026-03-30",
        started_at="2026-03-30T00:00:00+00:00",
        deadline="2026-03-30T08:00:00+00:00",
        launch_head="abc123",
        apply_mode="conditional_auto_apply",
        baseline_clean=True,
        baseline_tests_passed=True,
        active_authority="codex",
        runtime_mode="autonomous_codex",
    )
    previous.results = {"done-task": {"status": "success"}}

    monkeypatch.setattr(orchestrator, "ensure_runtime_dirs", lambda: None)
    monkeypatch.setattr(orchestrator, "sync_backlog", lambda run_id: None)
    monkeypatch.setattr(
        orchestrator,
        "load_manifest",
        lambda path: [
            CodexTaskDef(
                task_id="done-task",
                name="Done task",
                category="review",
                prompt="No-op",
                sandbox_mode="read-only",
                write_policy="readonly",
            )
        ],
    )
    monkeypatch.setattr(orchestrator, "load_state", lambda: previous)
    monkeypatch.setattr(
        orchestrator,
        "preflight",
        lambda: (
            "queue_only",
            False,
            False,
            ["fresh preflight note"],
            "codex",
            {"active_authority": "claude", "runtime_mode": "shadow_setup"},
        ),
    )
    monkeypatch.setattr(orchestrator, "_acquire_lock", lambda: None)
    monkeypatch.setattr(orchestrator, "_release_lock", lambda: None)
    monkeypatch.setattr(orchestrator, "write_progress_file", lambda state, manifest: None)
    monkeypatch.setattr(orchestrator, "log_decision", lambda *args, **kwargs: None)
    monkeypatch.setattr(orchestrator, "_append_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(orchestrator, "_load_previous_snapshot", lambda started_at: None)
    monkeypatch.setattr(orchestrator, "generate_morning_report", lambda state, manifest, snapshot=None: None)
    monkeypatch.setattr(orchestrator, "_write_run_snapshot", lambda state, manifest: tmp_path / "snapshot.json")
    monkeypatch.setattr(orchestrator, "maybe_append_findings", lambda: None)
    monkeypatch.setattr(orchestrator, "pick_next_ready", lambda manifest, state: None)
    monkeypatch.setattr(orchestrator, "save_state", lambda state: captured_states.append(state))

    orchestrator.run_overnight(
        hours=0.1,
        manifest_path=tmp_path / "manifest.json",
        single_task=None,
        dry_run=False,
        resume=True,
        skip_lock=True,
        skip_preflight=False,
    )

    assert captured_states
    resumed = captured_states[0]
    assert resumed.apply_mode == "queue_only"
    assert resumed.baseline_clean is False
    assert resumed.baseline_tests_passed is False
    assert resumed.active_authority == "claude"
    assert resumed.runtime_mode == "shadow_setup"


def test_execute_task_write_path_fails_when_no_durable_commit(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(orchestrator, "RESULTS_DIR", tmp_path / "results")
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    monkeypatch.setattr(
        orchestrator,
        "prepare_worktree",
        lambda task, launch_head: (worktree, "overnight-codex-write-check"),
    )
    monkeypatch.setattr(orchestrator, "_snapshot_readonly_guard", lambda: {})
    monkeypatch.setattr(orchestrator, "_readonly_guard_failures", lambda snapshot: [])
    monkeypatch.setattr(orchestrator, "_preserve_staged_artifacts", lambda io_dir, result_dir: [])
    monkeypatch.setattr(orchestrator, "_write_result_artifacts", lambda task, result_dir, payload: None)
    def fake_codex_exec(
        codex_bin: str,
        *,
        prompt: str,
        workdir: Path,
        sandbox_mode: str,
        output_path: Path,
        schema_path: Path,
        timeout_minutes: int,
    ) -> subprocess.CompletedProcess[str]:
        output_path.write_text(
            json.dumps(
                {
                    "task_status": "success",
                    "summary": "Write attempted.",
                    "commands_run": [],
                    "evidence": [
                        {
                            "path": "scripts/overnight_codex_orchestrator.py",
                            "detail": "changed",
                        }
                    ],
                    "findings": [],
                    "action_items": [],
                    "files_changed": [],
                    "tests_run": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(["codex"], 0, "", "")

    monkeypatch.setattr(orchestrator, "_codex_exec", fake_codex_exec)
    monkeypatch.setattr(
        orchestrator,
        "worktree_changed_files",
        lambda worktree_path: ["scripts/overnight_codex_orchestrator.py"],
    )
    monkeypatch.setattr(
        orchestrator,
        "run_quality_gate",
        lambda *args, **kwargs: (True, [], tmp_path / "review.md"),
    )
    monkeypatch.setattr(orchestrator, "_commit_worktree", lambda task, worktree_path: "")

    task = CodexTaskDef(
        task_id="write-check",
        name="Write check",
        category="test",
        prompt="Make a bounded write.",
        sandbox_mode="workspace-write",
        write_policy="guarded_write",
        expected_artifact="findings.json",
        allowed_write_prefixes=["scripts/"],
    )
    state = OvernightCodexState(
        run_id="2026-03-30",
        started_at="2026-03-30T00:00:00+00:00",
        deadline="2026-03-30T08:00:00+00:00",
        launch_head="abc123",
        apply_mode="queue_only",
        baseline_clean=False,
        baseline_tests_passed=False,
    )

    result = orchestrator.execute_task(task, state=state, codex_bin="codex")

    assert result.status == "failed"
    assert result.failure_class == "validation_failed"
    assert "No durable staged diff" in (result.error or "")


def test_run_subprocess_safe_rewrites_python_to_project_venv(
    monkeypatch: MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}

    class FakePopen:
        def __init__(self, cmd: list[str], **kwargs: object) -> None:
            observed["cmd"] = cmd
            observed["cwd"] = kwargs.get("cwd")
            self.returncode = 0

        def communicate(self, timeout: int | None = None) -> tuple[str, str]:
            return ("ok", "")

        def kill(self) -> None:
            return None

    monkeypatch.setattr(orchestrator, "rewrite_python_command", lambda cmd: ["/tmp/kr/.venv/bin/python", *cmd[1:]])
    monkeypatch.setattr(orchestrator.subprocess, "Popen", FakePopen)

    result = orchestrator._run_subprocess_safe(["python", "-m", "pytest", "engines/source/tests/"], timeout=5)

    assert observed["cmd"] == ["/tmp/kr/.venv/bin/python", "-m", "pytest", "engines/source/tests/"]
    assert result.args == ["/tmp/kr/.venv/bin/python", "-m", "pytest", "engines/source/tests/"]


def test_task_generator_run_rewrites_python_to_project_venv(
    monkeypatch: MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(task_generator, "rewrite_python_command", lambda cmd: ["/tmp/kr/.venv/bin/python", *cmd[1:]])
    monkeypatch.setattr(task_generator.subprocess, "run", fake_run)

    task_generator._run(["python", "-m", "pytest", "engines/excerpting/tests/", "--co"])

    assert observed["cmd"] == ["/tmp/kr/.venv/bin/python", "-m", "pytest", "engines/excerpting/tests/", "--co"]


def test_wsl_resume_shadow_rehearsal_preserves_bash_runtime_vars() -> None:
    if os.name != "nt":
        pytest.skip("WSL bootstrap wrapper is Windows-only")

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        pytest.skip("PowerShell is not available")

    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "overnight_codex_wsl_resume.ps1"
    command = textwrap.dedent(
        f"""
        $ErrorActionPreference = 'Stop'
        $global:WslCalls = @()

        function global:wsl.exe {{
            $joined = [string]::Join(' ', $args)
            if ($joined -eq '--status') {{
                return 'Default Version: 2'
            }}
            if ($joined -eq '--list --quiet') {{
                return 'Ubuntu-24.04'
            }}
            $global:WslCalls += ,@($args)
            $global:LastWslArgs = $args
            return '/home/test/kr-codex'
        }}

        function global:ubuntu2404.exe {{
            throw 'ubuntu2404.exe should not be called in this test'
        }}

        & '{script_path}' -RunShadowRehearsal

        $bashCommand = $global:LastWslArgs[-1]
        if ($bashCommand -notmatch '/home/test/kr-codex') {{
            throw 'Expected the bash command to use the resolved absolute WSL runtime dir.'
        }}
        foreach ($call in $global:WslCalls) {{
            if ($call -contains '~') {{
                throw 'Expected WSL invocations to avoid --cd ~ so runtime setup stays out of a literal ~/ directory.'
            }}
        }}

        Write-Output $bashCommand
        """
    ).strip()

    completed = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert 'RUNTIME_DIR=' in completed.stdout


def test_wsl_resume_strips_carriage_returns_and_bootstraps_via_tr() -> None:
    if os.name != "nt":
        pytest.skip("WSL bootstrap wrapper is Windows-only")

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        pytest.skip("PowerShell is not available")

    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "overnight_codex_wsl_resume.ps1"
    command = textwrap.dedent(
        f"""
        $ErrorActionPreference = 'Stop'
        $global:WslCalls = @()

        function global:wsl.exe {{
            $joined = [string]::Join(' ', $args)
            if ($joined -eq '--status') {{
                return 'Default Version: 2'
            }}
            if ($joined -eq '--list --quiet') {{
                return 'Ubuntu'
            }}
            $global:WslCalls += ,@($args)
            return '/home/test/kr-codex'
        }}

        function global:ubuntu2404.exe {{
            throw 'ubuntu2404.exe should not be called in this test'
        }}

        & '{script_path}' -RunShadowRehearsal

        foreach ($call in $global:WslCalls) {{
            $bashCommand = $call[-1]
            if ($bashCommand.Contains("`r")) {{
                throw 'Expected WSL bash commands to be sanitized before execution.'
            }}
        }}

        $bootstrapCall = $global:WslCalls[1][-1]
        if ($bootstrapCall -notmatch "tr -d '\\\\r'") {{
            throw 'Expected bootstrap command to strip CR before piping into bash.'
        }}

        Write-Output 'WSL_COMMANDS_OK'
        """
    ).strip()

    completed = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert "WSL_COMMANDS_OK" in completed.stdout


def test_wsl_resume_run_cycle_uses_runtime_venv_and_task_filter() -> None:
    if os.name != "nt":
        pytest.skip("WSL bootstrap wrapper is Windows-only")

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        pytest.skip("PowerShell is not available")

    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "overnight_codex_wsl_resume.ps1"
    command = textwrap.dedent(
        f"""
        $ErrorActionPreference = 'Stop'
        $global:WslCalls = @()

        function global:wsl.exe {{
            $joined = [string]::Join(' ', $args)
            if ($joined -eq '--status') {{
                return 'Default Version: 2'
            }}
            if ($joined -eq '--list --quiet') {{
                return 'Ubuntu'
            }}
            $global:WslCalls += ,@($args)
            return '/home/test/kr-codex'
        }}

        function global:ubuntu2404.exe {{
            throw 'ubuntu2404.exe should not be called in this test'
        }}

        & '{script_path}' -RunCycle -Hours 2.5 -SingleTask val-contracts

        $bashCommand = $global:WslCalls[-1][-1]
        if ($bashCommand -notmatch '\\.venv/bin/python') {{
            throw 'Expected cycle command to prefer the runtime venv python.'
        }}
        if ($bashCommand -notmatch '--task ''val-contracts''') {{
            throw 'Expected cycle command to include the requested single task.'
        }}
        if ($bashCommand -notmatch '--hours 2.5') {{
            throw 'Expected cycle command to carry the requested hours value.'
        }}

        Write-Output 'RUN_CYCLE_OK'
        """
    ).strip()

    completed = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert "RUN_CYCLE_OK" in completed.stdout


def test_wsl_resume_does_not_require_get_windows_optional_feature() -> None:
    if os.name != "nt":
        pytest.skip("WSL bootstrap wrapper is Windows-only")

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        pytest.skip("PowerShell is not available")

    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "overnight_codex_wsl_resume.ps1"
    command = textwrap.dedent(
        f"""
        $ErrorActionPreference = 'Stop'

        function global:Get-WindowsOptionalFeature {{
            throw 'Get-WindowsOptionalFeature should not be called by the WSL resume wrapper.'
        }}

        function global:wsl.exe {{
            $joined = [string]::Join(' ', $args)
            if ($joined -eq '--status') {{
                return 'Default Version: 2'
            }}
            if ($joined -eq '--list --quiet') {{
                return 'Ubuntu'
            }}
            return '/home/test/kr-codex'
        }}

        function global:ubuntu2404.exe {{
            throw 'ubuntu2404.exe should not be called in this test'
        }}

        & '{script_path}' -DryRun
        Write-Output 'DRY_RUN_OK'
        """
    ).strip()

    completed = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert "DRY_RUN_OK" in completed.stdout
