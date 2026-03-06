#!/usr/bin/env python3
"""Project orientation — automated status for any Claude session.

Run this at the start of any session to understand the full project state
without depending on NEXT.md being correct or current.

Usage:
    python3 scripts/orient.py          # Full orientation
    python3 scripts/orient.py --brief  # One-screen summary
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def git_log(n=5):
    """Get recent git log."""
    try:
        result = subprocess.run(
            ["git", "log", f"--oneline", f"-{n}"],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip()
    except Exception:
        return "ERROR: git not available"


def count_files(directory, pattern="*.py"):
    """Count files matching pattern in directory."""
    path = Path(directory)
    if not path.exists():
        return 0
    return len(list(path.rglob(pattern)))


def read_next_md():
    """Parse NEXT.md for task info."""
    path = Path(__file__).parent.parent / "NEXT.md"
    if not path.exists():
        return {"error": "NEXT.md not found"}

    text = path.read_text(encoding="utf-8")

    info = {}
    # Session type
    m = re.search(r"## Session Type\n(\w+)", text)
    info["session_type"] = m.group(1) if m else "UNKNOWN"

    # Immediate task
    m = re.search(r"## Immediate Task\n\n(.+?)(?=\n\n##|\Z)", text, re.DOTALL)
    info["task"] = m.group(1).strip()[:200] if m else "UNKNOWN"

    # Pending owner questions
    m = re.search(r"## Pending Owner Questions\n\n(.+?)(?=\n\n##|\Z)", text, re.DOTALL)
    info["owner_questions"] = m.group(1).strip() if m else "None"

    return info


def spec_refinement_status():
    """Check refinement status across all engines."""
    targets = [
        "engines/source", "engines/normalization", "engines/passaging",
        "engines/atomization", "engines/excerpting", "engines/taxonomy",
        "engines/synthesis", "shared/consensus", "shared/validation",
        "shared/human_gate", "shared/feedback", "shared/user_model",
        "shared/scholar_authority", "interface/scholar",
    ]

    ready = 0
    total = 0
    status = []

    for target in targets:
        claude_md = Path(target) / "CLAUDE.md"
        total += 1
        if claude_md.exists():
            text = claude_md.read_text(encoding="utf-8")
            if "Implementation-ready: YES" in text:
                ready += 1
                status.append(f"  ✓ {Path(target).name}")
            else:
                cycles = len(re.findall(r"Cycle \d+(?!\s*\(not yet)", text))
                status.append(f"  · {Path(target).name} (cycle {cycles})")
        else:
            status.append(f"  ? {Path(target).name} (no CLAUDE.md)")

    return ready, total, status


def code_status():
    """Check code files across engines."""
    engines = {}
    for engine_dir in sorted(Path("engines").iterdir()):
        if engine_dir.is_dir():
            src_files = count_files(engine_dir / "src", "*.py")
            test_files = count_files(engine_dir / "tests", "*.py")
            has_contracts = (engine_dir / "contracts.py").exists()
            engines[engine_dir.name] = {
                "src": src_files,
                "tests": test_files,
                "contracts": has_contracts,
            }
    return engines


def check_test_data():
    """Check what test fixtures exist."""
    fixtures = Path("tests/fixtures")
    if not fixtures.exists():
        return []
    return [str(p.relative_to(fixtures)) for p in fixtures.iterdir() if p.is_dir()]


def check_env():
    """Check if .env exists with API keys."""
    env_path = Path(".env")
    if not env_path.exists():
        return "MISSING — no .env file"
    text = env_path.read_text()
    if "ANTHROPIC_API_KEY" in text or "OPENAI_API_KEY" in text or "OPENROUTER_API_KEY" in text:
        return "EXISTS — API keys configured"
    return "EXISTS — but no API keys found"


def main():
    brief = "--brief" in sys.argv
    root = Path(__file__).parent.parent
    os.chdir(root)

    print("=" * 60)
    print("  KR PROJECT ORIENTATION")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # NEXT.md task
    next_info = read_next_md()
    print(f"\n📋 CURRENT TASK")
    print(f"  Type: {next_info.get('session_type', 'UNKNOWN')}")
    print(f"  Task: {next_info.get('task', 'UNKNOWN')[:120]}")
    if next_info.get("owner_questions", "None") != "None":
        print(f"  ⚠ OWNER QUESTIONS PENDING: {next_info['owner_questions'][:100]}")

    # Recent git
    print(f"\n📝 RECENT COMMITS")
    for line in git_log(5).split("\n"):
        print(f"  {line}")

    # SPEC refinement
    ready, total, statuses = spec_refinement_status()
    print(f"\n📊 SPEC REFINEMENT: {ready}/{total} implementation-ready")
    if not brief:
        for s in statuses:
            print(s)

    # Code status
    engines = code_status()
    code_engines = {k: v for k, v in engines.items() if v["src"] > 1 or v["tests"] > 0}
    contracts = {k: v for k, v in engines.items() if v["contracts"]}
    print(f"\n💻 CODE: {sum(v['src'] for v in engines.values())} src files, "
          f"{sum(v['tests'] for v in engines.values())} test files")
    print(f"  Contracts (Pydantic models): {', '.join(contracts.keys()) or 'none'}")
    if not brief and code_engines:
        for name, info in code_engines.items():
            print(f"  {name}: {info['src']} src, {info['tests']} tests")

    # Test data
    fixtures = check_test_data()
    print(f"\n🧪 TEST DATA: {len(fixtures)} fixture sets")
    for f in fixtures:
        print(f"  {f}")

    # Environment
    env_status = check_env()
    print(f"\n🔑 API KEYS: {env_status}")

    # Governance docs
    gov_docs = list(root.glob("*.md"))
    print(f"\n📄 GOVERNANCE: {len(gov_docs)} root docs, "
          f"{len(list(Path('.claude/agents').glob('*.md')))} agents, "
          f"{len(list(Path('.claude/commands').glob('*.md')))} commands, "
          f"{len(list(Path('.claude/skills').iterdir()))} skills")

    # GUI
    gui_app = Path("interface/scholar/src/app.py").exists()
    gui_template = Path("interface/scholar/src/templates/base.html").exists()
    gui_spec = Path("interface/GUI.md").exists()
    print(f"\n🖥️  GUI: spec={'✓' if gui_spec else '✗'} app={'✓' if gui_app else '✗'} templates={'✓' if gui_template else '✗'}")

    # What's needed
    print(f"\n⚡ WHAT'S NEEDED NEXT")
    if ready == 0:
        print("  → SPEC refinement (no SPECs are implementation-ready)")
    if not contracts:
        print("  → Machine-readable contracts (no contracts.py files)")
    elif len(contracts) < len(engines):
        missing = set(engines.keys()) - set(contracts.keys())
        print(f"  → Contracts for: {', '.join(sorted(missing))}")
    if not fixtures:
        print("  → Test fixtures (no test data)")
    if "MISSING" in env_status:
        print("  → API keys (.env file)")
    if not gui_app:
        print("  → GUI skeleton (FastAPI app.py, see interface/GUI.md)")
    if ready == total:
        print("  → Implementation can begin! Follow ORCHESTRATOR.md")

    print()


if __name__ == "__main__":
    main()
