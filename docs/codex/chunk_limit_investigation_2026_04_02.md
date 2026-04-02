# Chunk-Limit Investigation — 2026-04-02

Question:

Did the weekend `smoke_api_v2` overrun happen because the code ignored
`--max-chunks`, or because the run was launched without that flag?

## Evidence Collected

1. `scripts/run_full_integration.py` visibly forwards `--max-chunks` to
   `scripts/run_integration_test.py` when the argument is present.

2. A real mock probe against the `taysir` package using the repo virtualenv:

```bash
.venv/bin/python scripts/run_integration_test.py \
  --package-path experiments/format_diversity_test/packages/taysir \
  --output-dir integration_tests/chunk_limit_probe_taysir \
  --mock \
  --max-chunks 2
```

Observed behavior:

- Phase 1 still produced `184` chunks
- the runner then logged `--max-chunks=2: processing 2 of 184 chunks in Phases 2-3`
- Phase 2a classified `2` chunks
- Phase 2b grouped `2` chunks
- Phase 3 produced `2` excerpts

## Strongest Interpretation

The child runner honors `--max-chunks` correctly.

Given that `run_full_integration.py` also visibly forwards the flag when set,
the strongest current interpretation is:

- the expensive weekend overrun was launched **without** `--max-chunks`
- or without a wrapper that actually passed it through

not that the child runner silently ignored the limit.

## Practical Consequence

The next future smoke command should still be verified explicitly before use,
but this investigation does **not** support the claim that the child runner’s
current Phase 2/3 truncation logic is broken.

## Follow-Up

1. If a future wrapper or script is used to launch smoke runs, inspect that
   wrapper’s CLI construction, not just `run_integration_test.py`.
2. Keep the mock chunk-limit probe as the cheap verification path before any
   future paid smoke run.
