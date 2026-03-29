#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

HOURS_VAL="${HOURS_VAL:-12}"
WORKERS_VAL="${WORKERS_VAL:-3}"
DRY_RUN=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN="--dry-run"; shift ;;
        --hours) HOURS_VAL="$2"; shift 2 ;;
        --workers) WORKERS_VAL="$2"; shift 2 ;;
        *) shift ;;
    esac
done

python scripts/overnight_codex_task_generator.py --output overnight_codex/manifest.json
python scripts/weekend_parallel_codex.py \
    --manifest overnight_codex/manifest.json \
    --hours "$HOURS_VAL" \
    --workers "$WORKERS_VAL" \
    $DRY_RUN
