# Backend Proof Status

Date: 2026-03-31
Lane: Codex control-plane only
Runtime host: WSL clone at `~/kr-codex`

## Scope

This document records the first bounded CLI-backend proof run for the post-Claude takeover path.

The goal was not engine implementation. The goal was to answer one control-plane question: can the current WSL runtime execute the CLI-backed excerpting path end-to-end on bounded fixtures without depending on the interactive Windows environment?

## Artifacts

WSL artifact root from the first proof run:

- `~/kr-codex/overnight_codex/results/backend_proof_cli_20260331_194513`

Fixtures exercised:

- `taysir`
- `ibn_aqil_v3`

Both runs used:

- `--backend cli`
- `--max-chunks 1`

## What Passed

- `shared/llm/tests/test_cli_adapter.py` passed in the WSL venv (`49 passed`).
- Deterministic Phase 1 completed on both fixtures.
- LLM-backed Phase 2a classification completed on both fixtures.
- LLM-backed Phase 2b grouping completed on both fixtures.
- LLM-backed Phase 3 enrichment completed on both fixtures.
- Output writing completed on both fixtures:
  - `excerpts.jsonl`
  - `processing_log.jsonl`
  - `timing.json`
  - `run_metadata.json`

Observed bounded outputs:

- `taysir`: 13 excerpts
- `ibn_aqil_v3`: 26 excerpts

## What Failed

Consensus / verification is still the blocker, but the failure class changed during this session.

Evidence:

- each run ended with `gate_count = 0`
- each run recorded `errors = ["llm_call_errors:3"]`
- the raw verify error artifacts show `CLIBackendError` with Claude authentication failure

Initial failure surface:

- `Failed to authenticate. API Error: 401 ... Invalid authentication credentials`

## Fast Auth Preflight

A direct adapter-level auth preflight was also run against the WSL venv after the smoke implementation landed.

Observed result before the setup-token fix:

- `codex`: OK
- `gemini`: OK
- `claude`: FAILED

That proved the failure was not "the WSL runtime cannot use subscription CLIs." The failure was narrower:

- the current WSL Claude auth path is invalid for adapter-backed verification calls

## Setup-Token Follow-Up

After placing a long-lived Claude setup token in `~/.claude/kr_setup_token.txt` on Windows and re-running WSL bootstrap, the fast auth preflight changed to:

- `codex`: OK
- `claude`: OK
- `gemini`: rate-limited

That means the WSL Claude auth path is no longer the active blocker.

## Latest Bounded Proof Result

After the setup-token fix, a new bounded `taysir` proof run completed with:

- Phase 1 deterministic: PASS
- Phase 2a classification: PASS
- Phase 2b grouping: PASS
- Phase 3 enrichment: PASS
- excerpt writing: PASS
- consensus / verification: FAIL

Observed bounded output:

- `taysir`: 14 excerpts
- `gate_count`: 0

Latest failure surface:

- Claude verification calls no longer return `401`
- they now fail with a rate-limit reset notice (`resets 12am`)

## Current Interpretation

The runtime host is now good enough to prove real CLI-backed engine execution in WSL.

The remaining blocker is not generic WSL setup, Python, Codex, or basic Claude auth. The blocker is the Claude-backed verification path inside the current excerpting CLI configuration under real provider quota conditions.

Current config observed in both run metadata files:

- `CLASSIFY_MODEL = openai/gpt-5.4`
- `GROUP_MODEL = openai/gpt-5.4`
- `ENRICH_MODEL = openai/gpt-5.4`
- `VERIFY_MODEL = anthropic/claude-opus-4.6`
- `ESCALATION_MODEL = google/gemini-2.5-pro`

So the current blocker after WSL hardening is specifically:

- WSL Claude verification auth is not valid for the excerpting CLI path

## Control-Plane Consequence

Codex can now operate the runtime host continuously in shadow mode on this machine.

But the statement in [ACTIVE_AUTHORITY.md](/C:/Users/Rayane/Desktop/kr/ACTIVE_AUTHORITY.md) remains materially true:

- `blocked_after_claude_expiry: Primary Claude-backed excerpting calls remain blocked unless an alternative backend is proven.`

This proof sequence narrows that blocker:

- the host and adapter path are mechanically viable
- the setup-token path fixes the original WSL auth failure
- the remaining live failure is Claude verification quota / rate limit, not the entire CLI architecture

## Next Useful Actions

1. Run the new runtime auth preflight before future backend-proof runs.
2. Re-run the bounded backend proof after the Claude quota window resets.
3. If repeated bounded runs still hit the same verify-model quota wall, treat verify-model remapping as an explicit post-Claude engine/back-end decision, not an implicit runtime assumption.
4. Keep using the fast auth preflight before long proof runs so provider issues are detected before expensive engine execution starts.
