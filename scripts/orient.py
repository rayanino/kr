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


def engine_protocol_status():
    """Check per-engine status against ENGINE_PROTOCOL.md steps."""
    engines = [
        "source", "normalization", "passaging",
        "atomization", "excerpting", "taxonomy", "synthesis",
    ]

    statuses = []
    for eng in engines:
        eng_dir = Path(f"engines/{eng}")
        has_spec = (eng_dir / "SPEC.md").exists()
        has_contracts = (eng_dir / "contracts.py").exists()
        has_src = len(list((eng_dir / "src").glob("*.py"))) > 1 if (eng_dir / "src").exists() else False
        has_tests = len(list((eng_dir / "tests").glob("test_*.py"))) > 0 if (eng_dir / "tests").exists() else False
        has_lessons = (eng_dir / "LESSONS.md").exists()

        if has_lessons:
            status = "COMPLETE"
        elif has_tests:
            status = "Step 4 (TEST)"
        elif has_src:
            status = "Step 3 (BUILD) or pre-protocol stubs"
        elif has_spec and has_contracts:
            status = "Step 1 (SPEC) pending"
        else:
            status = "NOT STARTED"

        statuses.append(f"    {eng}: {status}")

    tracer = Path("reference/TRACER_FINDINGS.md").exists()
    pipeline = Path("scripts/run_pipeline.py").exists()

    return tracer, pipeline, statuses


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

    # Engine protocol status
    tracer, pipeline, statuses = engine_protocol_status()
    print(f"\n📊 PROTOCOL STATUS:")
    print(f"  Tracer bullet: {'✓ DONE' if tracer else '✗ NOT DONE (Step 0)'}")
    print(f"  Pipeline runner: {'✓ exists' if pipeline else '✗ not built yet'}")
    if not brief:
        print("  Per-engine:")
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

    # What's needed
    print(f"\n⚡ WHAT'S NEEDED NEXT")
    if not tracer:
        print("  → Step 0: Run the tracer bullet (see ENGINE_PROTOCOL.md)")
    elif not pipeline:
        print("  → Tracer bullet incomplete: scripts/run_pipeline.py needed")
    else:
        print("  → Per-engine work: Steps 1-4 per ENGINE_PROTOCOL.md")
    if not contracts:
        print("  → Machine-readable contracts (no contracts.py files)")
    if not fixtures:
        print("  → Test fixtures (no test data)")
    if "MISSING" in env_status:
        print("  → API keys (.env file)")

    print()


if __name__ == "__main__":
    main()
