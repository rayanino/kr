"""Fast adapter-level auth check for runtime CLI backends."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    from pydantic import BaseModel
except ModuleNotFoundError:
    REPO_ROOT = Path(__file__).resolve().parent.parent
    VENV_ROOT = REPO_ROOT / ".venv"
    VENV_PYTHON = VENV_ROOT / "bin" / "python"
    if VENV_PYTHON.exists() and Path(sys.prefix).resolve() != VENV_ROOT.resolve():
        raise SystemExit(
            subprocess.run([str(VENV_PYTHON), __file__, *sys.argv[1:]], check=False).returncode
        )
    raise

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.llm.cli_adapter import CLIInstructorAdapter


BACKEND_MODELS = {
    "claude": "anthropic/claude-opus-4.6",
    "codex": "openai/gpt-5.4",
    "gemini": "google/gemini-3.1-pro-preview",
}


class HealthCheckResponse(BaseModel):
    ok: str


def _messages_for(backend: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "Return a tiny JSON object matching the schema. "
                f"This is a runtime auth smoke for the {backend} backend."
            ),
        },
        {
            "role": "user",
            "content": 'Reply with {"ok":"yes"} only.',
        },
    ]


def check_backend(name: str, timeout_seconds: int) -> dict[str, Any]:
    model = BACKEND_MODELS[name]
    adapter = CLIInstructorAdapter(default_backend=name)
    start = time.monotonic()
    try:
        response = adapter.chat.completions.create(
            model=model,
            response_model=HealthCheckResponse,
            messages=_messages_for(name),
            timeout=timeout_seconds,
            max_retries=0,
        )
        duration = round(time.monotonic() - start, 1)
        ok = response.ok.strip().lower() == "yes"
        return {
            "backend": name,
            "model": model,
            "status": "ok" if ok else "bad_response",
            "duration_s": duration,
            "detail": f"ok={response.ok!r}",
        }
    except Exception as exc:
        duration = round(time.monotonic() - start, 1)
        return {
            "backend": name,
            "model": model,
            "status": "failed",
            "duration_s": duration,
            "detail": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Runtime CLI auth preflight")
    parser.add_argument(
        "--backends",
        nargs="*",
        choices=sorted(BACKEND_MODELS),
        default=["claude", "codex", "gemini"],
        help="Backends to check",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=30,
        help="Per-backend timeout in seconds",
    )
    args = parser.parse_args()

    results = [check_backend(name, args.timeout_seconds) for name in args.backends]
    failed = [item for item in results if item["status"] != "ok"]

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        print("=== Runtime CLI Auth Check ===")
        for item in results:
            print(f"{item['backend']}: {item['status']} ({item['duration_s']}s) - {item['detail']}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
