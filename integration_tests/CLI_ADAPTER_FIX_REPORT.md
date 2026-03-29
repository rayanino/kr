# CLI Adapter Fix Report — 2026-03-29

## Summary

The CLI adapter (`shared/llm/cli_adapter.py`) had **three cascading bugs** that prevented
`--backend cli` integration tests from producing any excerpts. All three are now fixed and
verified on real Arabic scholarly text.

**OAuth IS working.** The credentials.json token is valid and the adapter reads it correctly.
The failures were caused by a UTF-16 encoded file, missing exception handling, and a CLI
tool-use turn limit — NOT by Anthropic disabling OAuth or the token being expired.

## The Three Bugs

### Bug 1: UnicodeDecodeError from UTF-16 setup-token file

**Root cause:** Windows PowerShell wrote `~/.claude/kr_setup_token.txt` in UTF-16LE encoding
(BOM `0xFFFE`). The adapter's `_get_setup_token()` called `read_text(encoding="utf-8")` which
crashed with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff`.

**Impact:** This exception was NOT caught by the adapter's retry loop (only catches
`CalledProcessError`, `TimeoutExpired`, `json.JSONDecodeError`, `ValidationError`). It
propagated directly into `phase2_classify.py`'s catch-all `except Exception`, which silently
excluded the chunk. Result: 0 excerpts, 0 errors, status "success".

**Fix:** `_get_setup_token()` now catches `UnicodeDecodeError` and `OSError`, returning `None`
to fall through to credentials.json.

**Evidence:** Phase 2a timing was 0.009s per package — impossibly fast for any subprocess call.
The UnicodeDecodeError was instant (file read, no network). Three request hook files existed
per package (adapter fired `completion:kwargs` 3x) but zero response/error hook files (the
exception bypassed both hooks).

### Bug 2: CLIBackendError not caught in retry loop

**Root cause:** The adapter's `create()` retry loop catches 4 specific exception types but NOT
`CLIBackendError`. When `_extract_claude_result()` raises `CLIBackendError` (e.g., envelope
with `is_error=true`), it bypasses all retries and propagates immediately.

**Fix:** Added `except CLIBackendError` handler in the retry loop with backoff + error hook.

### Bug 3: Tool-use turn exhaustion with --output-format json

**Root cause:** Claude CLI `--bare` mode with `--output-format json` triggers internal tool-use
for structured output. Each tool call counts as a "turn". For complex Arabic texts (7791 chars),
the model needs 4-10 turns. With `--max-turns 2`, the model exhausted turns, producing an
envelope with `subtype: "error_max_turns"` and `result: null` (no model text). The adapter
passed this envelope dict to Pydantic validation, which failed with "segments Field required".

**Diagnosis sequence:**
1. Short texts (3000 chars) → model completes in 1 turn → works
2. Full texts (7791 chars) → model needs 4-10 turns → `error_max_turns`
3. With `--max-turns 5` → model used 6 turns → still failed
4. With `--max-turns 10` + `--output-format text` → model completes → **works**

**Fix:** Changed from `--output-format json` + `--max-turns 2` to `--output-format text` +
`--max-turns 10`. Raw model text is returned directly (no envelope), parsed by `extract_json()`.
Also added `error_max_turns` detection in `_extract_claude_result()` to raise `CLIBackendError`
with a clear message instead of silently passing the envelope dict through.

## Verification

### Unit tests: 45/45 pass
```
python -m pytest shared/llm/tests/test_cli_adapter.py -v
# 45 passed in 0.23s
```

### Full-chunk classification: PASS
```
Full chunk: 7791 chars (Arabic scholarly text from ext_39_masala)
Result: 41 segments classified
Time: 357 seconds
Cost: $0.00 (Max subscription)
```

### Token status at time of fix
```
accessToken prefix: sk-ant-oat01-qQFgN6T...
expiresAt: 7.7 hours remaining
refreshToken: present
```

## Performance Comparison

| Backend | Time per chunk | Cost per chunk | JSON compliance |
|---------|---------------|---------------|-----------------|
| API (OpenRouter) | ~45s | EUR 0.42 | Enforced by Instructor JSON mode |
| CLI (--bare) | ~357s (6 min) | $0.00 | System prompt + extract_json |

CLI is ~8x slower due to multi-turn tool-use overhead, but $0 cost.

## Files Changed

| File | Changes |
|------|---------|
| `shared/llm/cli_adapter.py` | `_get_setup_token` encoding resilience, `CLIBackendError` retry handler, `--output-format text`, `--max-turns 10`, `error_max_turns` detection |
| `shared/llm/tests/test_cli_adapter.py` | 10 new tests (encoding, retry, envelope formats, token priority) → 45 total |

## Commits

1. `129ceeea` — Initial fix: envelope extraction + setup-token auth (before diagnosis)
2. `50f633f9` — Final fix: text output + max-turns 10 + encoding resilience
3. `e8e001a8` — Debug test results

## Remaining Issue (out of scope)

4 of 5 integration test packages fail with a **pre-existing** `UnicodeEncodeError` at
`run_integration_test.py:1016` — Windows cp1252 encoding can't print Arabic source metadata.
This is in the test runner, not the CLI adapter. The `ext_39_masala` package (null metadata)
runs successfully.

## Result Directories

| Directory | What | Status |
|-----------|------|--------|
| `integration_tests/smoke_cli_20260329/` | First CLI run (before any fixes) | 0 excerpts — Bug 1 |
| `integration_tests/smoke_cli_fix_20260329/` | After Bug 1 fix | 0 excerpts — Bug 3 |
| `integration_tests/cli_final_test/` | Debug run during Bug 3 investigation | 0 excerpts — Bug 3 |
| `integration_tests/debug_cli_v3/` | Timeout investigation | Timeout — Bug 3 |
| (standalone test) | Full chunk with final fix | **41 segments** — SUCCESS |
