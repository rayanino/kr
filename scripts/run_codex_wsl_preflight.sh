#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

STRICT_PARITY=0
if [ "${1:-}" = "--strict-parity" ]; then
  STRICT_PARITY=1
  shift
fi

if [ ! -x ".venv/bin/python" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv --seed .venv
  else
    python -m venv .venv
  fi
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
fi

PYTHON_BIN=".venv/bin/python"

echo "=== KR Codex WSL Preflight ==="
echo "Project: $(pwd)"
echo "Python:  $PYTHON_BIN"
echo ""

if [ "$STRICT_PARITY" -eq 1 ]; then
  "$PYTHON_BIN" scripts/check_codex_kr_setup.py --require-windows-parity
else
  "$PYTHON_BIN" scripts/check_codex_kr_setup.py
fi
echo ""
"$PYTHON_BIN" scripts/check_runtime_cli_auth.py --json
