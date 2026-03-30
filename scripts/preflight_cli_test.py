"""Pre-flight CLI backend test — run BEFORE any integration test.

Tests each backend (claude, codex, gemini) with a tiny prompt to catch
infrastructure issues instantly instead of discovering them after hours.

Usage:
    python scripts/preflight_cli_test.py
    python scripts/preflight_cli_test.py --backend claude
    python scripts/preflight_cli_test.py --backend codex
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Ensure stdout/stderr can handle Arabic on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SIMPLE_PROMPT = 'Respond with exactly this JSON: {"answer": "hello", "confidence": 0.99}'
ARABIC_PROMPT = 'Respond with exactly this JSON: {"answer": "بسم الله", "confidence": 0.95}'

SIMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["answer", "confidence"],
    "additionalProperties": False,
}


def test_claude() -> tuple[bool, str]:
    """Test Claude CLI backend."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        return False, "claude CLI not found on PATH"

    # Load OAuth token (same as CLI adapter)
    creds_path = Path.home() / ".claude" / ".credentials.json"
    if not creds_path.exists():
        return False, f"Credentials not found: {creds_path}"
    try:
        creds = json.loads(creds_path.read_text(encoding="utf-8"))
        oauth_token = creds.get("claudeAiOauth", {}).get("accessToken", "")
        if not oauth_token:
            return False, "No accessToken in credentials"
    except (json.JSONDecodeError, KeyError) as e:
        return False, f"Failed to read credentials: {e}"

    cmd = [
        "claude", "-p", "-",
        "--bare", "--no-session-persistence",
        "--max-turns", "10",
        "--output-format", "text",
        "--model", "opus",
    ]

    try:
        t0 = time.monotonic()
        env = {**os.environ, "ANTHROPIC_API_KEY": oauth_token}
        result = subprocess.run(
            cmd,
            input=ARABIC_PROMPT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            env=env,
        )
        elapsed = time.monotonic() - t0

        if result.returncode != 0:
            return False, (
                f"Exit code {result.returncode} ({elapsed:.1f}s)\n"
                f"stderr: {result.stderr[:500]}"
            )

        output = result.stdout.strip()
        if not output:
            return False, f"Empty output ({elapsed:.1f}s)"

        # Try to parse JSON from output
        try:
            # Find JSON in output
            start = output.find("{")
            end = output.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(output[start:end])
                return True, (
                    f"OK ({elapsed:.1f}s) — "
                    f"answer={data.get('answer', '?')!r}"
                )
        except json.JSONDecodeError:
            pass

        return True, f"OK ({elapsed:.1f}s) — raw response (no JSON, but CLI works)"

    except subprocess.TimeoutExpired:
        return False, "Timeout (120s) — Claude CLI is unresponsive"
    except FileNotFoundError:
        return False, "claude executable not found"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def test_codex() -> tuple[bool, str]:
    """Test Codex CLI backend."""
    codex_bin = shutil.which("codex")
    if not codex_bin:
        return False, "codex CLI not found on PATH"

    schema_file = None
    output_file = None
    try:
        schema_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(SIMPLE_SCHEMA, schema_file, indent=2)
        schema_file.close()

        output_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        output_file.close()

        cmd = [
            codex_bin,
            "exec", "-",
            "--output-schema", schema_file.name,
            "-s", "read-only",
            "-o", output_file.name,
        ]

        t0 = time.monotonic()
        result = subprocess.run(
            cmd,
            input=SIMPLE_PROMPT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        elapsed = time.monotonic() - t0

        if result.returncode != 0:
            return False, (
                f"Exit code {result.returncode} ({elapsed:.1f}s)\n"
                f"stderr: {result.stderr[:500]}"
            )

        output = Path(output_file.name).read_text(encoding="utf-8").strip()
        if not output:
            return False, f"Empty output file ({elapsed:.1f}s)"

        try:
            data = json.loads(output)
            return True, (
                f"OK ({elapsed:.1f}s) — "
                f"answer={data.get('answer', '?')!r}"
            )
        except json.JSONDecodeError:
            return True, f"OK ({elapsed:.1f}s) — response not JSON but CLI works"

    except subprocess.TimeoutExpired:
        return False, "Timeout (120s) — Codex CLI is unresponsive"
    except FileNotFoundError:
        return False, f"codex executable not found at {codex_bin}"
    except Exception as e:
        return False, f"Unexpected error: {e}"
    finally:
        for f in [schema_file, output_file]:
            if f is not None:
                try:
                    os.unlink(f.name)
                except OSError:
                    pass


def test_gemini() -> tuple[bool, str]:
    """Test Gemini CLI backend."""
    gemini_bin = shutil.which("gemini")
    if not gemini_bin:
        return False, "gemini CLI not found on PATH"

    cmd = [
        gemini_bin,
        "-p", "",
        "-y",
        "--output-format", "text",
    ]

    try:
        t0 = time.monotonic()
        result = subprocess.run(
            cmd,
            input=SIMPLE_PROMPT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        elapsed = time.monotonic() - t0

        if result.returncode != 0:
            return False, (
                f"Exit code {result.returncode} ({elapsed:.1f}s)\n"
                f"stderr: {result.stderr[:500]}"
            )

        output = result.stdout.strip()
        if not output:
            return False, f"Empty output ({elapsed:.1f}s)"

        return True, f"OK ({elapsed:.1f}s) — got {len(output)} chars"

    except subprocess.TimeoutExpired:
        return False, "Timeout (120s) — Gemini CLI is unresponsive"
    except FileNotFoundError:
        return False, f"gemini executable not found at {gemini_bin}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-flight CLI backend test")
    parser.add_argument(
        "--backend",
        choices=["claude", "codex", "gemini", "all"],
        default="all",
        help="Which backend to test (default: all)",
    )
    args = parser.parse_args()

    tests = {
        "claude": test_claude,
        "codex": test_codex,
        "gemini": test_gemini,
    }

    if args.backend != "all":
        tests = {args.backend: tests[args.backend]}

    print("=" * 60)
    print("PRE-FLIGHT CLI BACKEND TEST")
    print("=" * 60)
    print()

    all_pass = True
    for name, test_fn in tests.items():
        print(f"  [{name}] Testing...", end=" ", flush=True)
        ok, msg = test_fn()
        status = "PASS" if ok else "FAIL"
        print(f"{status}")
        print(f"    {msg}")
        print()
        if not ok:
            all_pass = False

    print("=" * 60)
    if all_pass:
        print("ALL BACKENDS READY")
    else:
        print("SOME BACKENDS FAILED — fix before running integration tests")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
