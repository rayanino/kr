---
name: recursive-improve
description: >
  Trace capture and analysis for KR pipeline LLM calls.  Use when running
  pipeline with LLM calls, reviewing improvement proposals, or benchmarking
  agent performance.  NEVER use for autonomous content prompt changes.
---

# recursive-improve for KR

Captures LLM call traces, analyzes failure patterns, proposes improvements,
and benchmarks results.  Integrated via trace bridge for CLI adapter calls
and ri.patch() for SDK calls.

## When to Use

1. **After any pipeline run with LLM calls** — pass `--traces eval/traces/`
2. **After accumulating traces** — run `recursive-improve eval eval/traces/`
3. **After ri generates proposals** — run `python scripts/ri_review.py`
4. **For benchmarking** — run `recursive-improve benchmark --label "description"`

## KR Safety Constraints

**NEVER use ri for:**
- Content classification prompt changes (genre, author, science, school)
- Arabic text handling modifications
- Code changes without code review
- Autonomous `/ratchet` on content prompts

**ONLY use ri for:**
- JSON schema directive improvements
- Error recovery instruction tuning
- Output format specification optimization
- Retry augmentation text improvements

## Quick Reference

```bash
# Run pipeline with traces
python scripts/run_pipeline.py --traces eval/traces/pipeline
python scripts/run_integration_test.py --package-path PKG --traces eval/traces/excerpting

# Analyze traces
recursive-improve eval eval/traces/

# Review proposals (auto-rejects content changes)
python scripts/ri_review.py

# Benchmark
recursive-improve benchmark --label "v1-baseline"
recursive-improve benchmark list

# Dashboard
recursive-improve dashboard -p 8080

# KR-specific metrics
python -c "from eval.compute_baselines import run_all_on_directory; ..."
```

## Architecture

- `shared/llm/ri_trace_bridge.py` — hooks into CLI adapter events
- `eval/compute_baselines.py` — 7 KR-specific detectors
- `eval/program.md` — ratchet configuration
- `scripts/ri_review.py` — proposal review with content safety gate
