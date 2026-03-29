# NEXT — Fix Two CLI Adapter Bugs Before Overnight Run

## Situation

The 280-chunk overnight integration run **failed**. The smoke test (1 chunk per
package) succeeded at 23:18 on March 28. The overnight run launched at 02:02 on
March 29. Within the first hour, ALL calls started failing. No packages completed.

Two distinct bugs were observed:

### Bug 1: OAuth Token Expires Mid-Run (BLOCKING)

**Symptom:** After ~3 hours of successful calls, every `claude -p` subprocess
starts returning exit code 1 within 1-2 seconds. Logs show:
```
[WARNING] Attempt 1/3: subprocess error (exit 1)
[INFO] Auth error detected — refreshing token
[WARNING] Attempt 2/3: subprocess error (exit 1)
[WARNING] Attempt 3/3: subprocess error (exit 1)
[ERROR] Phase 2a FAILED for chunk ... after 3 attempts. Error code: EX-C-001
```

**Root cause:** `_get_oauth_token()` (cli_adapter.py line 96) reads the OAuth
access token from `~/.claude/.credentials.json`. This token expires after a few
hours. The "refresh" at line 440-442 just re-reads the SAME stale file — it
doesn't actually request a new token. So "refreshing" produces the same expired
token, and all 3 retry attempts fail identically.

**Why the smoke test didn't catch it:** The smoke test ran immediately after a
fresh `claude` interactive session, which writes a new token. It completed in
28 minutes — well before token expiry.

**Why CC being open didn't help:** CC keeps its own in-memory token alive. It
doesn't write refreshed tokens back to `~/.claude/.credentials.json`. So the
file on disk goes stale while CC is fine.

**Fix options to investigate:**
1. Call `claude` interactively before each package to force a token refresh
2. Detect the specific auth error and run a token refresh command
3. Use `claude auth refresh` or similar CLI command if it exists (research needed)
4. Write a wrapper that periodically refreshes the credentials file
5. Use the Anthropic API key directly instead of OAuth (the adapter already has
   a fallback path via `--backend api` with OpenRouter, but we want $0 via Max)

### Bug 2: Envelope Extraction Failing (BLOCKING)

**Symptom:** Even when auth works, some calls produce this validation error:
```
[WARNING] Attempt 1/3: validation error: 2 validation errors for ClassificationResult
segments
  Field required [type=missing, input_value={'type': 'result', 'subty...
  a602eb73', 'errors': []}, input_type=dict]
```

**Root cause:** The Claude CLI JSON envelope (the wrapper around the model's
actual response) is being passed directly to Pydantic validation instead of
being unwrapped first. The `input_value` shown IS the envelope — it has
`type`, `subtype`, `errors` fields, not `segments`.

**Where this fails in code:** `_invoke_claude()` at line 543-557 tries to
extract the model text from the envelope:
```python
envelope = json.loads(raw_stdout)
if isinstance(envelope, dict) and "result" in envelope:
    return str(envelope["result"])
```
If this extraction fails (JSONDecodeError, or no "result" key), line 559
returns `raw_stdout` unchanged. Then `extract_json()` parses the raw stdout
as JSON — getting the envelope dict — and passes it to `model_validate()`,
which fails because the envelope isn't a ClassificationResult.

**Possible causes:**
- The Claude CLI output format may have changed (new `subtype` field suggests
  an update)
- `--output-format json` and `--bare` flag interaction may have changed
- The envelope might have a different structure than expected
- Multi-line output or BOM might prevent `json.loads` from parsing

**Investigation needed:** Run a real `claude -p "say hello" --bare --output-format json`
and inspect the EXACT raw output byte-by-byte. Compare to the expected format
documented in CLI_ADAPTER_SPEC.md section 3.2.

## Files to Read

| File | Why |
|------|-----|
| `shared/llm/cli_adapter.py` | The adapter with both bugs (699 lines) |
| `shared/llm/CLI_ADAPTER_SPEC.md` | Governing SPEC — section 3.2 for Claude backend, section 6.3 for OAuth |
| `integration_tests/smoke_20260329_v2/SUMMARY.json` | Successful smoke test (proves pipeline works when auth is fresh) |
| `reference/archive/sessions/cross_provider_audit/architect_audit_findings.md` | Full audit context |

## Constraints

- The fix must ensure the overnight run (15-20 hours, 280 chunks) completes
  without manual intervention. The owner will be sleeping.
- Do NOT switch to --backend api (OpenRouter costs money). The owner has
  Claude Max — all CLI calls must be $0.
- The pipeline itself works — 69 real excerpts were produced in the smoke test.
  Only the token management and envelope parsing need fixing.
- After fixing, run a smoke test (--max-chunks 1) on all 5 packages to verify.
- Use the cross-provider review team if the fix involves architectural changes.
  For a targeted bug fix with clear root cause, CC alone is sufficient.

## What to Do

1. **Clone repo, read this NEXT.md and the audit findings.**

2. **Investigate Bug 2 first** (envelope parsing). Have CC run a real
   `claude -p "Respond with only: {\"test\": true}" --bare --output-format json`
   and capture the EXACT raw output. Compare to what `_invoke_claude()` expects.
   Fix the extraction logic.

3. **Investigate Bug 1** (token expiry). Research whether `claude` CLI has a
   token refresh command. Have CC check what `claude auth` or `claude login`
   subcommands exist. Design a solution that automatically refreshes the token
   before it expires during a long run.

4. **Have CC implement fixes.** Write a targeted NEXT.md for CC with exact
   changes needed. The changes should be ONLY in `cli_adapter.py` and possibly
   `run_integration_test.py` / `run_full_integration.py`.

5. **Run smoke test** (--max-chunks 1) on all 5 packages after the fix.

6. **Wait 4+ hours, then run another single CLI call** to verify token
   longevity. If it fails, the token fix isn't working.

7. **Then re-launch the overnight run.**

## Do NOT Do

- Do NOT change the excerpting engine, contracts, or phase logic.
- Do NOT switch to API backend. The owner's Max plan makes CLI calls free.
- Do NOT skip the 4-hour token longevity test. The smoke test didn't catch
  Bug 1 because it completed too quickly.
- Do NOT rush. The pipeline works. Only the CLI infrastructure needs fixing.

## Critical Numbers

- 280 total chunks across 5 packages
- ~840 LLM calls (3 per chunk: classify + group + enrich)
- Estimated 15-20 hours runtime
- Per-call timeout: 600s
- Per-package timeout: 43200s (12h)
- 1991 tests passing, 0 failures (as of commit 3cefa8c8)
