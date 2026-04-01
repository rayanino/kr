"""Audit the KR Codex setup across repo, home config, and runtime surfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_MCP_SERVERS = {"context7", "memory", "tavily"}
SUPPRESSED_MCP_SERVERS = {
    "stripe": "https://mcp.stripe.com",
    "supabase": "https://mcp.supabase.com/mcp",
    "vercel": "https://mcp.vercel.com",
}
EXPECTED_PROFILES = {"kr_interactive", "kr_peer_review", "kr_research", "kr_shadow"}
EXPECTED_AGENT_FILES = [
    ".codex/agents/kr_arabic_reviewer.toml",
    ".codex/agents/kr_boundary_validator.toml",
    ".codex/agents/kr_build_prober.toml",
    ".codex/agents/kr_code_reviewer.toml",
    ".codex/agents/kr_coworker_brief_writer.toml",
    ".codex/agents/kr_quick_check.toml",
    ".codex/agents/kr_repo_mapper.toml",
    ".codex/agents/kr_runtime_prober.toml",
]
EXPECTED_HOOK_FILES = [
    ".codex/hooks.json",
    ".codex/hooks/hook_utils.py",
    ".codex/hooks/session_start.py",
    ".codex/hooks/pre_tool_use_policy.py",
    ".codex/hooks/stop_quality_gate.py",
]
EXPECTED_SCRIPT_FILES = [
    "scripts/check_codex_kr_setup.py",
    "scripts/check_runtime_cli_auth.py",
    "scripts/overnight_codex_wsl_bootstrap.sh",
    "scripts/overnight_codex_wsl_resume.ps1",
    "scripts/run_codex_backend_proof_smoke.sh",
    "scripts/run_codex_wsl_preflight.sh",
    "scripts/run_overnight_codex_shadow_loop.ps1",
    "scripts/start_overnight_codex.sh",
]
EXPECTED_SKILL_FILES = [
    ".agents/skills/kr-codex-arabic-integrity/SKILL.md",
    ".agents/skills/kr-codex-bootstrap/SKILL.md",
    ".agents/skills/kr-codex-coworker-orchestration/SKILL.md",
    ".agents/skills/kr-codex-environment-audit/SKILL.md",
    ".agents/skills/kr-codex-quality-gate/SKILL.md",
    ".agents/skills/kr-codex-review-dispatch/SKILL.md",
    ".agents/skills/kr-codex-runtime/SKILL.md",
    ".agents/skills/kr-codex-session-start/SKILL.md",
    ".agents/skills/kr-codex-shadow-setup/SKILL.md",
]
PARITY_FILES = [
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/hooks/dispatch.py",
    ".codex/agents/kr_runtime_prober.toml",
    ".agents/skills/kr-codex-runtime/SKILL.md",
    "scripts/check_codex_kr_setup.py",
    "scripts/check_runtime_cli_auth.py",
]


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def normalized_path(value: str) -> str:
    path = value.replace("\\", "/")
    if len(path) >= 2 and path[1] == ":":
        path = path[0].lower() + path[1:]
    return path.rstrip("/")


def trusted_project(config: dict, target: str) -> bool:
    projects = config.get("projects") or {}
    target_norm = normalized_path(target)
    for raw_path, data in projects.items():
        if not isinstance(data, dict) or data.get("trust_level") != "trusted":
            continue
        candidate = normalized_path(str(raw_path))
        if target_norm == candidate or target_norm.startswith(candidate + "/"):
            return True
    return False


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=str(cwd or ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(cmd, 1, "", str(exc))


def check_repo_files() -> CheckResult:
    required = [
        ".codex/config.toml",
        *EXPECTED_HOOK_FILES,
        *EXPECTED_AGENT_FILES,
        *EXPECTED_SCRIPT_FILES,
        *EXPECTED_SKILL_FILES,
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        return CheckResult("repo_files", False, f"missing: {', '.join(missing)}")
    return CheckResult(
        "repo_files",
        True,
        "repo-local Codex config, hooks, agents, skills, and preflight scripts are present",
    )


def check_repo_config() -> CheckResult:
    path = ROOT / ".codex" / "config.toml"
    if not path.exists():
        return CheckResult("repo_config", False, "missing .codex/config.toml")

    config = load_toml(path)
    features = config.get("features") or {}
    agents = config.get("agents") or {}
    profiles = set((config.get("profiles") or {}).keys())
    mcp_servers = config.get("mcp_servers") or {}

    problems: list[str] = []
    if features.get("codex_hooks") is not True:
        problems.append("features.codex_hooks != true")
    if features.get("multi_agent") is not True:
        problems.append("features.multi_agent != true")
    if agents.get("max_threads") != 6:
        problems.append("agents.max_threads != 6")
    if agents.get("max_depth") != 1:
        problems.append("agents.max_depth != 1")
    if agents.get("job_max_runtime_seconds") != 1800:
        problems.append("agents.job_max_runtime_seconds != 1800")

    missing_profiles = sorted(EXPECTED_PROFILES - profiles)
    if missing_profiles:
        problems.append(f"missing profiles: {', '.join(missing_profiles)}")

    missing_servers = sorted(EXPECTED_MCP_SERVERS - set(mcp_servers.keys()))
    if missing_servers:
        problems.append(f"missing repo mcp servers: {', '.join(missing_servers)}")

    for name, expected_url in SUPPRESSED_MCP_SERVERS.items():
        server = mcp_servers.get(name)
        if not isinstance(server, dict):
            problems.append(f"missing suppressed mcp override: {name}")
            continue
        if server.get("url") != expected_url:
            problems.append(f"{name} url mismatch")
        if server.get("enabled") is not False:
            problems.append(f"{name} is not disabled repo-locally")

    if problems:
        return CheckResult("repo_config", False, "; ".join(problems))
    return CheckResult(
        "repo_config",
        True,
        "repo config exposes KR profiles, hooks, multi-agent settings, and scoped MCP policy",
    )


def check_hook_commands() -> CheckResult:
    path = ROOT / ".codex" / "hooks.json"
    if not path.exists():
        return CheckResult("hook_commands", False, "missing .codex/hooks.json")

    text = path.read_text(encoding="utf-8")
    if "git rev-parse --show-toplevel" in text:
        return CheckResult(
            "hook_commands",
            False,
            "hooks.json still shells out through git rev-parse to locate repo-local hook scripts",
        )
    if "dispatch.py" not in text:
        return CheckResult("hook_commands", False, "hooks.json is not using the repo-local dispatch hook launcher")
    return CheckResult("hook_commands", True, "hook launchers resolve repo-local scripts without git-dependent path shells")


def check_home_config() -> CheckResult:
    path = Path.home() / ".codex" / "config.toml"
    if not path.exists():
        return CheckResult("home_config", False, f"missing {path}")

    config = load_toml(path)
    expected = [str(ROOT)]
    if os.name == "nt":
        expected.extend([r"\\?\{}".format(ROOT), "/home/rayane/kr-codex"])
    elif str(ROOT).startswith("/home/"):
        expected.append(str(ROOT))

    missing = [target for target in expected if not trusted_project(config, target)]
    if missing:
        return CheckResult("home_config", False, f"trusted project entry missing for: {', '.join(missing)}")
    return CheckResult("home_config", True, f"trusted project coverage is present in {path}")


def check_home_agents() -> CheckResult:
    path = Path.home() / ".codex" / "AGENTS.md"
    if not path.exists():
        return CheckResult("home_agents", False, f"missing {path}")
    text = path.read_text(encoding="utf-8")
    if "Prefer repo-local" not in text or "WSL clone" not in text:
        return CheckResult("home_agents", False, "global AGENTS.md does not contain the expected Codex defaults")
    return CheckResult("home_agents", True, "global AGENTS.md contains the expected Codex defaults")


def parse_mcp_rows(output: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("Name"):
            continue
        parts = line.split()
        if not parts:
            continue
        name = parts[0]
        match = re.search(r"\b(enabled|disabled)\b", line)
        rows[name] = match.group(1) if match else "unknown"
    return rows


def check_codex_mcp() -> CheckResult:
    cmd = ["codex", "mcp", "list"]
    if os.name == "nt":
        cmd = ["cmd", "/c", "codex", "mcp", "list"]
    proc = run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        return CheckResult("codex_mcp", False, proc.stderr.strip() or proc.stdout.strip() or "codex mcp list failed")

    rows = parse_mcp_rows(proc.stdout)
    missing = sorted(name for name in EXPECTED_MCP_SERVERS if rows.get(name) != "enabled")
    if missing:
        return CheckResult("codex_mcp", False, f"repo-scoped MCP servers not enabled: {', '.join(missing)}")

    noisy = sorted(name for name in SUPPRESSED_MCP_SERVERS if rows.get(name) == "enabled")
    if noisy:
        return CheckResult("codex_mcp", False, f"unexpected enabled MCP auth noise: {', '.join(noisy)}")

    detail = f"visible repo servers: {', '.join(sorted(EXPECTED_MCP_SERVERS))}; noisy remotes disabled"
    return CheckResult("codex_mcp", True, detail)


def peer_repo_root() -> Path | None:
    if os.name == "nt":
        candidate = Path(r"\\wsl.localhost\Ubuntu\home\rayane\kr-codex")
    else:
        candidate = Path("/mnt/c/Users/Rayane/Desktop/kr")
    return candidate if candidate.exists() else None


def check_runtime_parity(require_windows_parity: bool = False) -> CheckResult:
    peer = peer_repo_root()
    if peer is None:
        detail = "peer Windows/WSL checkout not found"
        return CheckResult("runtime_parity", not require_windows_parity, detail)

    local_head = run(["git", "rev-parse", "HEAD"], cwd=ROOT)
    if os.name == "nt":
        peer_head = run(["wsl.exe", "-e", "bash", "-lc", "cd ~/kr-codex && git rev-parse HEAD"])
    else:
        peer_head = run(["git", "rev-parse", "HEAD"], cwd=peer)
    if local_head.returncode != 0 or peer_head.returncode != 0:
        detail = "unable to read git HEAD from both checkouts"
        return CheckResult("runtime_parity", not require_windows_parity, detail)

    drift: list[str] = []
    if local_head.stdout.strip() != peer_head.stdout.strip():
        drift.append(f"HEAD mismatch: local={local_head.stdout.strip()} peer={peer_head.stdout.strip()}")

    for rel_path in PARITY_FILES:
        local_path = ROOT / rel_path
        peer_path = peer / rel_path
        if not local_path.exists() or not peer_path.exists():
            drift.append(f"missing parity file: {rel_path}")
            continue
        if sha256_file(local_path) != sha256_file(peer_path):
            drift.append(f"content drift: {rel_path}")

    if not drift:
        return CheckResult("runtime_parity", True, f"peer checkout in sync at {peer}")

    detail = "; ".join(drift)
    if require_windows_parity:
        return CheckResult("runtime_parity", False, detail)
    return CheckResult(
        "runtime_parity",
        True,
        detail + " (allowed in WSL-first mode; resync the Windows checkout before Windows-launched bootstrap or resume)",
    )


def check_auth_preflight(enabled: bool) -> CheckResult:
    if not enabled:
        return CheckResult("auth_preflight", True, "skipped (use --auth-preflight to run runtime backend auth checks)")

    proc = run(
        [
            sys.executable,
            "scripts/check_runtime_cli_auth.py",
            "--backends",
            "codex",
            "claude",
            "gemini",
            "--json",
        ],
        cwd=ROOT,
    )
    if proc.returncode != 0:
        return CheckResult("auth_preflight", False, proc.stdout.strip() or proc.stderr.strip() or "runtime auth preflight failed")
    return CheckResult("auth_preflight", True, "runtime backend auth preflight succeeded")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--auth-preflight",
        action="store_true",
        help="Run the runtime backend auth probe in addition to static setup checks.",
    )
    parser.add_argument(
        "--require-windows-parity",
        action="store_true",
        help="Fail when the Windows checkout drifts from the WSL checkout. Use this for Windows-launched bootstrap validation.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text output.",
    )
    args = parser.parse_args()

    results = [
        check_repo_files(),
        check_repo_config(),
        check_hook_commands(),
        check_home_config(),
        check_home_agents(),
        check_codex_mcp(),
        check_runtime_parity(args.require_windows_parity),
        check_auth_preflight(args.auth_preflight),
    ]

    status = "PASS" if all(result.ok for result in results) else "FAIL"
    if args.json:
        payload = {"status": status, "results": [asdict(result) for result in results]}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if status == "PASS" else 1

    print(f"KR Codex setup audit: {status}")
    for result in results:
        label = "OK" if result.ok else "FAIL"
        print(f"- [{label}] {result.name}: {result.detail}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
