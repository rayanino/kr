from __future__ import annotations

import subprocess
import sys
import types
from pathlib import Path

from pytest import MonkeyPatch


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    module = types.ModuleType(module_name)
    module.__file__ = str(path)
    sys.modules[module_name] = module
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    exec(code, module.__dict__)
    return module


setup_check = load_module("scripts/check_codex_kr_setup.py", "setup_check")
try:  # Allow loading the auth preflight script under the system interpreter used by some local test runs.
    import pydantic  # noqa: F401
except ModuleNotFoundError:
    pydantic_stub = types.ModuleType("pydantic")

    class _BaseModel:
        pass

    class _ValidationError(Exception):
        pass

    pydantic_stub.BaseModel = _BaseModel
    pydantic_stub.ValidationError = _ValidationError
    sys.modules["pydantic"] = pydantic_stub
auth_check = load_module("scripts/check_runtime_cli_auth.py", "auth_check")
contract_check = load_module("tools/check_cross_engine_contracts.py", "contract_check")
hook_utils = load_module(".codex/hooks/hook_utils.py", "hook_utils")
dispatch = load_module(".codex/hooks/dispatch.py", "dispatch")


def test_parse_mcp_rows_tracks_enabled_and_disabled_servers() -> None:
    output = """
Name      Command  Args                                    Env                     Cwd  Status   Auth
context7  npx      -y @upstash/context7-mcp@latest         -                       -    enabled  Unsupported
memory    npx      -y @modelcontextprotocol/server-memory  MEMORY_FILE_PATH=*****  -    enabled  Unsupported

Name      Url                           Bearer Token Env Var  Status    Auth
stripe    https://mcp.stripe.com        -                     disabled  Not logged in
vercel    https://mcp.vercel.com        -                     enabled   Not logged in
"""
    rows = setup_check.parse_mcp_rows(output)
    assert rows["context7"] == "enabled"
    assert rows["memory"] == "enabled"
    assert rows["stripe"] == "disabled"
    assert rows["vercel"] == "enabled"


def test_changed_paths_includes_untracked_and_renamed_files(monkeypatch: MonkeyPatch) -> None:
    proc = subprocess.CompletedProcess(
        ["git"],
        0,
        stdout=(
            " M docs/codex/runtime-policy.md\n"
            "?? .codex/config.toml\n"
            "R  old/name.py -> new/name.py\n"
        ),
        stderr="",
    )
    monkeypatch.setattr(hook_utils.subprocess, "run", lambda *args, **kwargs: proc)

    paths = hook_utils.changed_paths(Path("/tmp/kr"))
    assert paths == [
        "docs/codex/runtime-policy.md",
        ".codex/config.toml",
        "new/name.py",
    ]


def test_safe_setup_path_detection_rejects_mixed_mutation_targets() -> None:
    assert hook_utils.command_references_only_safe_setup_paths(
        "mv .codex/config.toml tests/test_codex_control_plane.py"
    ) is False
    assert hook_utils.command_references_only_safe_setup_paths(
        "cp .codex/config.toml .agents/skills/kr-codex-runtime/SKILL.md"
    ) is True


def test_find_repo_root_walks_up_from_nested_cwd(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    (repo_root / ".codex" / "hooks").mkdir(parents=True)
    (repo_root / ".codex" / "hooks" / "hook_utils.py").write_text("# marker\n", encoding="utf-8")
    nested = repo_root / "a" / "b" / "c"
    nested.mkdir(parents=True)

    assert dispatch.find_repo_root(str(nested)) == repo_root


def test_runtime_parity_allows_head_drift_when_control_plane_matches(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    local_root = tmp_path / "local"
    peer_root = tmp_path / "peer"
    for root in (local_root, peer_root):
        for rel_path in setup_check.PARITY_FILES:
            path = root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("same\n", encoding="utf-8")

    monkeypatch.setattr(setup_check, "ROOT", local_root)
    monkeypatch.setattr(setup_check, "peer_repo_root", lambda: peer_root)

    def fake_run(cmd: list[str], cwd: Path | None = None):
        head = "aaaa\n" if cwd == local_root else "bbbb\n"
        return subprocess.CompletedProcess(cmd, 0, stdout=head, stderr="")

    monkeypatch.setattr(setup_check, "run", fake_run)

    result = setup_check.check_runtime_parity(False)
    assert result.ok is True
    assert "allowed in WSL-first mode" in result.detail


def test_runtime_parity_fails_when_control_plane_files_differ(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    local_root = tmp_path / "local"
    peer_root = tmp_path / "peer"
    for rel_path in setup_check.PARITY_FILES:
        local_path = local_root / rel_path
        peer_path = peer_root / rel_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        peer_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text("local\n", encoding="utf-8")
        peer_path.write_text("peer\n", encoding="utf-8")

    monkeypatch.setattr(setup_check, "ROOT", local_root)
    monkeypatch.setattr(setup_check, "peer_repo_root", lambda: peer_root)

    def fake_run(cmd: list[str], cwd: Path | None = None):
        head = "aaaa\n" if cwd == local_root else "bbbb\n"
        return subprocess.CompletedProcess(cmd, 0, stdout=head, stderr="")

    monkeypatch.setattr(setup_check, "run", fake_run)

    result = setup_check.check_runtime_parity(True)
    assert result.ok is False
    assert "HEAD mismatch" in result.detail


def test_runtime_docs_reference_namespaced_profiles() -> None:
    for relative_path in [
        "docs/codex/wsl-bootstrap.md",
        "docs/codex/runtime-policy.md",
    ]:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "kr_interactive" in text
        assert "kr_shadow" in text
        assert "kr_peer_review" in text
        assert "kr_research" in text


def test_check_runtime_cli_auth_forwards_timeout_kwarg(monkeypatch: MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return types.SimpleNamespace(ok="yes")

    class FakeChat:
        completions = FakeCompletions()

    class FakeAdapter:
        def __init__(self, default_backend: str) -> None:
            captured["backend"] = default_backend
            self.chat = FakeChat()

    monkeypatch.setattr(auth_check, "CLIInstructorAdapter", FakeAdapter)

    result = auth_check.check_backend("codex", timeout_seconds=17)

    assert result["status"] == "ok"
    assert captured["backend"] == "codex"
    assert captured["timeout"] == 17


def test_start_overnight_codex_prefers_repo_venv() -> None:
    text = (ROOT / "scripts" / "start_overnight_codex.sh").read_text(encoding="utf-8")
    assert 'PYTHON_BIN="python"' in text
    assert 'if [ -x ".venv/bin/python" ]; then' in text
    assert '"$PYTHON_BIN" scripts/overnight_codex_orchestrator.py' in text


def test_find_cross_references_detects_contracts_core_imports(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    engines_dir = tmp_path / "engines"
    (engines_dir / "taxonomy").mkdir(parents=True)
    (engines_dir / "synthesis").mkdir(parents=True)
    (engines_dir / "taxonomy" / "contracts_core.py").write_text(
        "class PlacementAdditions:\n    pass\n",
        encoding="utf-8",
    )
    (engines_dir / "synthesis" / "consumer.py").write_text(
        "from engines.taxonomy.contracts_core import PlacementAdditions\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(contract_check, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(contract_check, "ENGINES_DIR", engines_dir)

    refs = contract_check.find_cross_references()
    assert refs["taxonomy -> synthesis"] == [
        "PlacementAdditions (in engines/synthesis/consumer.py)"
    ]


def test_extract_field_constraints_reads_multiline_field_and_type(tmp_path: Path) -> None:
    contracts_path = tmp_path / "contracts.py"
    contracts_path.write_text(
        """
from pydantic import BaseModel, Field


class Example(BaseModel):
    count: int = Field(
        default=0,
        ge=1,
        le=10,
    )
""".strip()
        + "\n",
        encoding="utf-8",
    )

    original_root = contract_check.REPO_ROOT
    contract_check.REPO_ROOT = tmp_path
    try:
        fields = contract_check.extract_field_constraints(contracts_path)
    finally:
        contract_check.REPO_ROOT = original_root
    assert fields["Example.count"]["type"] == "int"
    assert fields["Example.count"]["constraints"] == {"ge": "1", "le": "10"}


def test_check_enum_consistency_flags_mismatched_values(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    engines_dir = tmp_path / "engines"
    (engines_dir / "alpha").mkdir(parents=True)
    (engines_dir / "beta").mkdir(parents=True)
    (engines_dir / "gamma").mkdir(parents=True)
    (engines_dir / "alpha" / "contracts.py").write_text(
        """
from enum import Enum


class SharedMode(str, Enum):
    FIRST = "first"
    SECOND = "second"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (engines_dir / "beta" / "contracts.py").write_text(
        """
from enum import Enum


class SharedMode(str, Enum):
    FIRST = "first"
    THIRD = "third"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (engines_dir / "gamma" / "consumer.py").write_text(
        "from engines.alpha.contracts import SharedMode\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(contract_check, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(contract_check, "ENGINES_DIR", engines_dir)

    issues = contract_check.check_enum_consistency()
    assert len(issues) == 1
    assert "SharedMode" in issues[0]
