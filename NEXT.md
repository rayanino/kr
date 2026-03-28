# NEXT — Pre-Overnight Preparation (CC Task)

## Context

The architect has completed a deep audit of the excerpting engine before the 280-chunk overnight integration run. See `reference/archive/sessions/cross_provider_audit/architect_audit_findings.md` for full findings.

Key facts:
- HEAD is at `7cf348d5` (timeout fix already landed)
- 815+ tests expected passing
- The overnight run uses `--backend cli` (subprocess calls to claude/codex/gemini CLIs)
- Codex verify path is broken (F-1 in audit) — accepted for first run
- No code changes needed — this is preparation and validation only

## What to Do (in order)

### Task 1: Run Full Test Suite

```bash
python -m pytest --tb=short -q 2>&1 | tail -20
```

Report: total passed, failed, skipped, errors. If any FAILURES exist, stop and report immediately.

### Task 2: Phase 1 Discovery — Exact Chunk Counts

Run Phase 1 (deterministic only, no LLM calls) on all 5 packages to get exact chunk counts. This tells us exactly how many LLM calls the overnight run will make.

Write and run this script (save as `scripts/phase1_discovery.py`):

```python
"""Phase 1 discovery — get exact chunk counts for overnight run planning."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engines.excerpting.contracts import ExcerptingConfig
from engines.excerpting.src.phase1_assembly import run_phase1
from scripts.run_integration_test import load_package

PACKAGES_DIR = Path("experiments/format_diversity_test/packages")
PACKAGES = [
    "ibn_aqil_v1",
    "ibn_aqil_v3",
    "taysir",
    "ext_39_masala",
    "ext_46_qa",
]

config = ExcerptingConfig()
total_chunks = 0
large_chunks = 0

results = []

for name in PACKAGES:
    pkg_path = PACKAGES_DIR / name
    try:
        package = load_package(pkg_path)
        chunks, validation = run_phase1(package, config)
        
        chunk_words = [c.word_count for c in chunks]
        large = sum(1 for w in chunk_words if w > 2500)
        max_words = max(chunk_words) if chunk_words else 0
        
        results.append({
            "package": name,
            "content_units": len(package.content_units),
            "chunks": len(chunks),
            "large_chunks_gt2500": large,
            "max_words": max_words,
            "mean_words": round(sum(chunk_words) / len(chunk_words)) if chunk_words else 0,
        })
        
        total_chunks += len(chunks)
        large_chunks += large
        
        print(f"  {name}: {len(chunks)} chunks "
              f"(large: {large}, max: {max_words} words)")
        
    except Exception as exc:
        print(f"  {name}: FAILED — {exc}")
        results.append({"package": name, "error": str(exc)})

print(f"\nTotal: {total_chunks} chunks, {large_chunks} large (>2500 words)")
print(f"Estimated LLM calls: ~{total_chunks * 3} (classify + group + enrich)")
print(f"Estimated time at 131s/chunk: {total_chunks * 131 / 3600:.1f} hours")

output = Path("reference/archive/sessions/cross_provider_audit/phase1_discovery.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"\nSaved to {output}")
```

Run it. Report the exact numbers.

### Task 3: Write Overnight Analysis Script

Create `scripts/analyze_overnight_run.py` that the owner runs after the overnight completes. It should:

1. Accept `--output-dir` argument pointing to the overnight run's output directory
2. Read SUMMARY.json from the output directory
3. For each package:
   - Count excerpts, errors, gate entries
   - Count `verification_skipped` and `llm_enrichment_failed` flags in excerpts.jsonl
   - Report timing per phase from timing.json
   - Count retry attempts (look for duplicate call_ids or attempt patterns in raw_llm_requests/)
4. For the full run:
   - Total excerpts, errors, gate entries
   - Flag distribution table
   - Any timeout errors
   - Largest/smallest chunks by word count (from phase1_chunks.json)
   - Output a clean summary table

### Task 4: Commit and Report

Commit all new files with message:
```
audit: pre-overnight preparation — phase1 discovery + analysis script
```

Report:
- Test suite results (pass/fail/skip counts)
- Phase 1 chunk counts per package
- Total chunks for overnight run
- Any issues encountered

## Do NOT Do

- Do NOT modify any existing source files
- Do NOT implement code changes for the audit findings
- Do NOT run any LLM calls (no --backend cli, no API calls)
- Do NOT proceed beyond these 4 tasks
- After completing all tasks, commit, push, and stop
