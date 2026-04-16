from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from _pytest.monkeypatch import MonkeyPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUALITY_GATE_PATH = PROJECT_ROOT / "scripts" / "quality_gate.py"


def _load_quality_gate_module():
    spec = importlib.util.spec_from_file_location("quality_gate_module", QUALITY_GATE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_run_hook_script_uses_bash_safe_posix_paths(monkeypatch: MonkeyPatch) -> None:
    quality_gate = _load_quality_gate_module()
    captured: dict[str, object] = {}

    def fake_run_command(
        label: str,
        cmd: list[str],
        **kwargs: Any,
    ) -> tuple[bool, str]:
        captured["label"] = label
        captured["cmd"] = cmd
        captured["env"] = kwargs.get("env", {})
        return True, "ok"

    monkeypatch.setattr(quality_gate, "find_bash", lambda: "C:\\Program Files\\Git\\bin\\bash.exe")
    monkeypatch.setattr(quality_gate, "run_command", fake_run_command)
    monkeypatch.setattr(
        quality_gate,
        "PROJECT_DIR",
        Path(r"C:\Users\Rayane\.config\superpowers\worktrees\kr\source-engine-build-20260415"),
    )

    ok, _ = quality_gate.run_hook_script("arabic-safety-check.sh", "engines/source/src/errors.py")

    assert ok is True
    cmd = captured["cmd"]
    env = captured["env"]
    assert isinstance(cmd, list)
    assert isinstance(env, dict)
    assert cmd[1] == "C:/Users/Rayane/.config/superpowers/worktrees/kr/source-engine-build-20260415/.claude/hooks/arabic-safety-check.sh"
    assert env["CLAUDE_PROJECT_DIR"] == "C:/Users/Rayane/.config/superpowers/worktrees/kr/source-engine-build-20260415"
    assert env["CLAUDE_TOOL_FILE_PATH"] == "C:/Users/Rayane/.config/superpowers/worktrees/kr/source-engine-build-20260415/engines/source/src/errors.py"
