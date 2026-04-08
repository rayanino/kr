from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


HOOK_CONFIG_REL_PATH = Path(".codex/hooks/config/hooks-config.json")
DEFAULT_HOOK_CONFIG: dict[str, bool] = {
    "disableSessionStartContext": False,
    "disableProtectedAreaWarnings": False,
    "disableDestructiveCommandWarnings": False,
    "disableAuthorityMutationWarnings": False,
    "disableCoworkerDispatchWarnings": False,
    "disableStopQualityGateReminder": False,
    "disableStopSetupAuditReminder": False,
    "disableStopDispatchReminder": False,
    "disableStopPlanReminder": False,
    "disableDriftDetection": False,
}

SETUP_SAFE_PREFIXES = (
    ".codex/",
    ".agents/skills/",
    "docs/codex/",
    "overnight_codex/",
    "scripts/append_codex_findings.py",
    "scripts/check_codex_kr_setup.py",
    "scripts/check_runtime_cli_auth.py",
    "scripts/export_codex_windows_setup.ps1",
    "scripts/overnight_codex_",
    "scripts/run_codex_backend_proof_smoke.sh",
    "scripts/run_codex_wsl_preflight.sh",
    "scripts/run_overnight_codex_shadow_loop.ps1",
    "scripts/start_codex_kr.ps1",
    "scripts/start_overnight_codex.sh",
)

PROTECTED_PATH_PATTERNS = (
    r"\.claude/",
    r"(^|[\\/])overnight/",
    r"(^|[\\/])CLAUDE\.md$",
    r"(^|[\\/])NEXT\.md$",
    r"docs/superpowers/",
)

DESTRUCTIVE_COMMAND_PATTERNS = (
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+checkout\s+--\b",
    r"\bgit\s+clean\s+-f",
    r"\brm\s+-rf\b",
    r"\brmdir\b",
    r"\bdel\s+/f\b",
    r"\bformat\b",
)

MUTATING_COMMAND_PATTERNS = (
    r"\bsed\s+-i\b",
    r"\bperl\s+-i\b",
    r"\btee\b",
    r"\btouch\b",
    r"\btruncate\b",
    r"\bmv\b",
    r"\bcp\b",
    r"\brm\b",
    r"\bmkdir\b",
    r">\s*[^&]",
)

KNOWN_ENGINES = frozenset({
    "source", "normalization", "passaging", "atomization",
    "excerpting", "taxonomy", "synthesis",
})

ENGINE_PATH_HINTS = (
    "engines/",
    "shared/",
    "library/",
    "integration_tests/",
    "tools/",
)

INTEGRATION_TRIGGER_PREFIXES = (
    "scripts/run_integration_test.py",
    "scripts/run_full_integration.py",
    "scripts/overnight_codex_",
    "scripts/run_codex_wsl_preflight.sh",
    "shared/llm/",
    "tools/check_cross_engine_contracts.py",
)

REVIEW_PACKET_HINTS = (
    "docs/codex/reviews/",
    "docs/codex/dispatch-templates.md",
    "docs/codex/relay-prompts.md",
    "docs/codex/weekend_dr_prompts.md",
)

ANALYSIS_PATH_HINTS = (
    "analysis",
    "assessment",
    "findings",
    "handoff",
    "report",
    "review",
)

PLAN_PATH_HINTS = (
    "NEXT.md",
    ".kr/ACTIVE.md",
    ".kr/HANDOFF.md",
    "docs/plans/",
    "reference/handoffs/",
)


def emit_json(payload: dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False)


def load_event() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def _looks_like_repo_root(path: Path) -> bool:
    return (path / "ACTIVE_AUTHORITY.md").exists() and (path / ".codex").exists()


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for base in [current, *current.parents]:
        if _looks_like_repo_root(base):
            return base
    return current


def repo_root(event: dict[str, Any]) -> Path:
    raw_cwd = event.get("cwd")
    if isinstance(raw_cwd, str) and raw_cwd.strip():
        candidate = find_repo_root(Path(raw_cwd))
        if _looks_like_repo_root(candidate):
            return candidate
    cwd = Path(".").resolve()
    candidate = find_repo_root(cwd)
    if _looks_like_repo_root(candidate):
        return candidate
    try:
        proc = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return Path(proc.stdout.strip()).resolve()
    except OSError:
        pass
    return cwd


def parse_simple_kv(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def active_authority_state(root: Path) -> dict[str, str]:
    return parse_simple_kv(root / "ACTIVE_AUTHORITY.md")


def load_hook_config(root: Path) -> dict[str, bool]:
    path = root / HOOK_CONFIG_REL_PATH
    if not path.exists():
        return dict(DEFAULT_HOOK_CONFIG)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return dict(DEFAULT_HOOK_CONFIG)

    config = dict(DEFAULT_HOOK_CONFIG)
    for key, default in DEFAULT_HOOK_CONFIG.items():
        value = payload.get(key)
        if isinstance(value, bool):
            config[key] = value
        else:
            config[key] = default
    return config


def hook_enabled(root: Path, flag: str) -> bool:
    config = load_hook_config(root)
    return not config.get(flag, False)


def changed_paths(root: Path) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return []
    if proc.returncode != 0:
        return []

    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        normalized = path.strip().replace("\\", "/")
        if normalized:
            paths.append(normalized)
    return paths


def infer_quality_gate_mode(paths: list[str]) -> str | None:
    if not paths:
        return None
    if any(path.endswith("contracts.py") for path in paths):
        return "contracts"
    if any(path.endswith("SPEC.md") for path in paths):
        return "spec"
    if any(path.startswith(prefix) for prefix in INTEGRATION_TRIGGER_PREFIXES for path in paths):
        return "integration"
    if any(path.endswith(".py") and path.startswith(("engines/", "shared/")) and "/src/" in path for path in paths):
        return "all"
    return None


def needs_setup_audit(paths: list[str]) -> bool:
    setup_prefixes = (
        ".codex/",
        ".agents/skills/",
        "docs/codex/",
        "overnight_codex/README.md",
        "docs/codex/windows-workflow.md",
        "scripts/check_codex_kr_setup.py",
        "scripts/check_runtime_cli_auth.py",
        "scripts/export_codex_windows_setup.ps1",
        "scripts/run_codex_wsl_preflight.sh",
        "scripts/run_overnight_codex_shadow_loop.ps1",
        "scripts/start_codex_kr.ps1",
    )
    return any(path.startswith(setup_prefixes) for path in paths)


def command_text(event: dict[str, Any]) -> str:
    tool_input = event.get("tool_input") or {}
    command = tool_input.get("command")
    if isinstance(command, str):
        return command
    return ""


def command_matches(patterns: tuple[str, ...], command: str) -> bool:
    return any(re.search(pattern, command) for pattern in patterns)


def command_references_protected_area(command: str) -> bool:
    normalized = command.replace("\\", "/")
    return any(re.search(pattern, normalized) for pattern in PROTECTED_PATH_PATTERNS)


def command_references_engine_paths(command: str) -> bool:
    normalized = command.replace("\\", "/")
    return any(hint in normalized for hint in ENGINE_PATH_HINTS)


def _command_path_tokens(command: str) -> list[str]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.replace("&&", " ").replace("||", " ").split()

    candidates: list[str] = []
    for token in tokens:
        normalized = token.strip().strip("'\"").replace("\\", "/")
        if not normalized or normalized.startswith("-") or normalized in {"|", "&&", "||"}:
            continue
        if "/" in normalized or normalized in {
            "ACTIVE_AUTHORITY.md",
            "AGENTS.md",
            "CLAUDE.md",
            "Makefile",
            "NEXT.md",
            "pyproject.toml",
            "requirements.txt",
        }:
            candidates.append(normalized)
            continue
        if normalized.endswith((".json", ".md", ".ps1", ".py", ".sh", ".toml")):
            candidates.append(normalized)
    return candidates


def command_references_only_safe_setup_paths(command: str) -> bool:
    referenced = _command_path_tokens(command)
    if not referenced:
        return False
    for path in referenced:
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in SETUP_SAFE_PREFIXES):
            continue
        return False
    return True


def command_targets_external_coworker_cli(command: str) -> bool:
    normalized = command.lower()
    return bool(re.search(r"(^|[\s(])claude(\.cmd|\.exe)?\b", normalized)) or bool(
        re.search(r"(^|[\s(])gemini(\.cmd|\.exe)?\b", normalized)
    )


def command_uses_review_packet_path(command: str) -> bool:
    normalized = command.replace("\\", "/")
    return any(hint in normalized for hint in REVIEW_PACKET_HINTS)


def paths_look_like_major_conclusions(paths: list[str]) -> bool:
    lowered = [path.lower() for path in paths]
    return any(any(hint in path for hint in ANALYSIS_PATH_HINTS) and path.endswith(".md") for path in lowered)


def paths_touch_planning_surface(paths: list[str]) -> bool:
    normalized = [path.replace("\\", "/") for path in paths]
    return any(any(hint == path or hint in path for hint in PLAN_PATH_HINTS) for path in normalized)


def extract_next_scope(root: Path) -> set[str]:
    """Extract expected engine scope from NEXT.md header lines."""
    next_file = root / "NEXT.md"
    if not next_file.exists():
        return set()
    try:
        text = next_file.read_text(encoding="utf-8")
    except OSError:
        return set()
    header = "\n".join(text.splitlines()[:30]).lower()
    # Match engine names only in KR-specific contexts to avoid false positives
    # ("source" in "open source", "normalization" in "Unicode normalization").
    # Accepted patterns: "engines/<name>", "<name> engine", "engine: <name>"
    found: set[str] = set()
    for engine in KNOWN_ENGINES:
        if re.search(rf"engines/{engine}\b", header):
            found.add(engine)
        elif re.search(rf"\b{engine}\s+engine\b", header):
            found.add(engine)
        elif re.search(rf"engine[:\s]+.*\b{engine}\b", header):
            found.add(engine)
    return found


def detect_drift(root: Path, paths: list[str]) -> str | None:
    """Return a drift warning if changed paths diverge from NEXT.md scope."""
    scope = extract_next_scope(root)
    if not scope:
        return None
    engine_paths = [p for p in paths if p.startswith("engines/")]
    if not engine_paths:
        return None
    out_of_scope: list[str] = []
    for p in engine_paths:
        parts = p.split("/")
        if len(parts) >= 2 and parts[1] not in scope:
            out_of_scope.append(p)
    if not out_of_scope or len(out_of_scope) <= len(engine_paths) // 2:
        return None
    engines_touched = {p.split("/")[1] for p in out_of_scope if len(p.split("/")) >= 2}
    return (
        f"DRIFT WARNING: NEXT.md scope is {', '.join(sorted(scope))} "
        f"but {len(out_of_scope)}/{len(engine_paths)} engine changes touch "
        f"{', '.join(sorted(engines_touched))}. "
        "Verify this is intentional."
    )


def git_branch(root: Path) -> str:
    proc = run_git(root, ["branch", "--show-current"])
    if proc.returncode != 0:
        return "unknown"
    branch = proc.stdout.strip()
    return branch or "detached"


def dirty_summary(root: Path) -> str:
    paths = changed_paths(root)
    if not paths:
        return "clean"
    return f"dirty ({len(paths)} path(s))"


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return subprocess.CompletedProcess(args, 1, "", "git unavailable")
