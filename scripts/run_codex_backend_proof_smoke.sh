#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

PYTHON_BIN="python"
if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
fi

OUTPUT_ROOT="${1:-overnight_codex/results/backend_proof_cli_$(date -u '+%Y%m%d_%H%M%S')}"
shift || true

PACKAGES=("$@")
if [ ${#PACKAGES[@]} -eq 0 ]; then
  PACKAGES=("taysir" "ibn_aqil_v3")
fi

metadata_for() {
  case "$1" in
    taysir)
      printf '%s' '{"author_name":"عبد الله البسام","work_title":"تيسير العلام شرح عمدة الأحكام","science":"فقه","source_school":"حنبلي"}'
      ;;
    ibn_aqil_v3)
      printf '%s' '{"author_name":"ابن عقيل","work_title":"شرح ابن عقيل على ألفية ابن مالك","science":"نحو","source_school":null}'
      ;;
    *)
      printf '%s' '{"author_name":null,"work_title":null,"science":null,"source_school":null}'
      ;;
  esac
}

echo "=== KR Codex Backend Proof Smoke ==="
echo "Project: $(pwd)"
echo "Python:  $PYTHON_BIN"
echo "Output:  $OUTPUT_ROOT"
echo ""

mkdir -p "$OUTPUT_ROOT"

echo "== Runtime CLI auth preflight =="
set +e
"$PYTHON_BIN" scripts/check_runtime_cli_auth.py --backends codex claude gemini --json > "$OUTPUT_ROOT/cli_auth_preflight.json"
AUTH_STATUS=$?
set -e

if [ ! -s "$OUTPUT_ROOT/cli_auth_preflight.json" ]; then
  echo "Runtime CLI auth preflight did not produce JSON output." | tee "$OUTPUT_ROOT/smoke_skip_reason.txt"
  exit 1
fi

cat "$OUTPUT_ROOT/cli_auth_preflight.json"

backend_status() {
  local backend_name="$1"
  "$PYTHON_BIN" - <<PY
import json
from pathlib import Path
payload = json.loads(Path("$OUTPUT_ROOT/cli_auth_preflight.json").read_text(encoding="utf-8"))
for item in payload.get("results", []):
    if item.get("backend") == "$backend_name":
        print(item.get("status", "missing"))
        break
else:
    print("missing")
PY
}

CODEX_STATUS="$(backend_status codex)"
CLAUDE_STATUS="$(backend_status claude)"
GEMINI_STATUS="$(backend_status gemini)"

echo "== CLI adapter unit tests =="
"$PYTHON_BIN" -m pytest shared/llm/tests/test_cli_adapter.py -q | tee "$OUTPUT_ROOT/cli_adapter_pytest.txt"

if [ "$CODEX_STATUS" != "ok" ]; then
  echo ""
  echo "Skipping excerpting CLI smokes: codex backend preflight status = $CODEX_STATUS" | tee "$OUTPUT_ROOT/smoke_skip_reason.txt"
  exit 1
fi

if [ "$CLAUDE_STATUS" != "ok" ]; then
  echo ""
  echo "Skipping excerpting CLI smokes: claude backend preflight status = $CLAUDE_STATUS" | tee "$OUTPUT_ROOT/smoke_skip_reason.txt"
  exit 1
fi

if [ "$GEMINI_STATUS" != "ok" ]; then
  echo ""
  echo "Gemini preflight status = $GEMINI_STATUS; continuing because escalation may not trigger in bounded smokes." | tee "$OUTPUT_ROOT/smoke_warning.txt"
fi

for package_name in "${PACKAGES[@]}"; do
  package_path="experiments/format_diversity_test/packages/$package_name"
  package_output="$OUTPUT_ROOT/$package_name"
  if [ ! -d "$package_path" ]; then
    echo "Skipping unknown package: $package_name" | tee "$OUTPUT_ROOT/${package_name}_skipped.txt"
    continue
  fi

  echo ""
  echo "== CLI smoke: $package_name =="
  "$PYTHON_BIN" scripts/run_integration_test.py \
    --package-path "$package_path" \
    --output-dir "$package_output" \
    --backend cli \
    --max-chunks 1 \
    --source-metadata "$(metadata_for "$package_name")"
done

echo ""
echo "Backend proof smoke complete."
echo "Artifacts: $OUTPUT_ROOT"
