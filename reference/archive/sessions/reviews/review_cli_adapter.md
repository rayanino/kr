# Handoff Checklist — CLI Adapter Review

**Date:** 2026-03-28
**Commit:** 2a8560b4
**Architect:** Claude Chat (Opus 4.6)
**CC Concurrent Reviewer:** Claude Code (Opus 4.6, 1M)
**Baseline:** 766 passed, 2 skipped (pre-CC)
**Expected after CC:** 796 passed, 2 skipped (766 existing + 30 new)
**Actual after CC:** 796 passed, 2 skipped ✓

---

## Step 2: Test Baseline
- [x] pytest run on `engines/excerpting/tests/`: `766 passed, 2 skipped`
- [x] pytest run on `shared/llm/tests/`: `30 passed`
- [x] Combined: `796 passed, 2 skipped`
- [x] Count matches NEXT.md expectation: **yes**

NOTE: CC reported "768 passed, 0 failed" for excerpting — incorrect. Actual: 766 passed + 2 skipped = 768 collected. CC conflated collected with passed. Architect's independent count is authoritative.

## Step 3: File References Verified
| File | Exists | Content Verified |
|------|--------|-----------------|
| `shared/llm/__init__.py` | ✅ | ✅ (empty) |
| `shared/llm/cli_adapter.py` | ✅ | ✅ (669 lines, read in full) |
| `shared/llm/tests/__init__.py` | ✅ | ✅ (empty) |
| `shared/llm/tests/test_cli_adapter.py` | ✅ | ✅ (772 lines, read in full) |
| `scripts/run_integration_test.py` (modified) | ✅ | ✅ (diff reviewed) |
| `scripts/run_full_integration.py` (modified) | ✅ | ✅ (diff reviewed) |

## SPEC Compliance (§-by-§ trace)
| SPEC Section | Implementation | Verified |
|---|---|---|
| §2.1 Constructor | `__init__(default_backend)` | ✅ line 645-648 |
| §2.2 Namespace chain | `_ChatNamespace` / `_CompletionsNamespace` | ✅ lines 234, 630-634, 650-651 |
| §2.3 `create()` signature | All 6 named params + `**kwargs` | ✅ lines 240-249 |
| §2.4 Hook registration | `.on()` with 3 event names | ✅ lines 653-657 |
| §2.4 Hook firing conventions | kwargs→`**kwargs_dict`, response→positional, error→positional | ✅ lines 659-668, empirical probe |
| §3.1 Provider routing | Model prefix → backend mapping | ✅ lines 199-211 |
| §3.2 Claude backend | All 6 flags present | ✅ lines 505-514, test_claude_command_flags |
| §3.3 Codex backend | `codex exec --output-schema -s read-only -o` | ✅ lines 565-571, test_codex_schema_file_created |
| §3.4 Gemini backend | `gemini -p -y --output-format text` | ✅ lines 609-614, test_gemini_command_flags |
| §4.1 Retry semantics | max_retries=N → N+1 total attempts | ✅ line 295, empirical: max_retries=2 → 3 calls |
| §4.2 Attempt loop | All 4 exception types caught | ✅ lines 347, 374, 403, 420 |
| §4.3 Validation error feedback | Field paths + error types | ✅ lines 384-398, empirical: model_validator msg included |
| §4.4 JSON parse error feedback | First 500 chars + error msg | ✅ lines 357-365 |
| §4.5 JSON extraction | 3-step cascade | ✅ lines 155-192, 4 empirical probes |
| §4.5 Return type | **⛔ FINDING F-1:** returns `str` (line 146), SPEC says `dict\|list` | |
| §5.1 Schema in system prompt | Schema appended to system message | ✅ lines 278-284 |
| §5.1 No system message case | **⛔ FINDING F-4:** leading `\n\n` when `original_system=""` | |
| §5.2 Schema temp file (codex) | Written to tempfile, cleaned in finally | ✅ lines 554-558, 584-594 |
| §5.2 json.dump (not json.dumps) | `json.dump(patched_schema, schema_file, indent=2)` | ✅ line 557 |
| §5.3 additionalProperties patching | Recursive, $defs handled | ✅ lines 127-143, empirical: ClassificationResult |
| §6.1 CLIBackendError | backend + exit_code attrs | ✅ lines 35-49 |
| §6.2 Subprocess invocation | capture_output, text=True, timeout, check=True | ✅ lines 520-527, 575-581, 618-624 |
| §6.3 OAuth token | Reads ~/.claude/.credentials.json | ✅ lines 96-113 |
| §6.4 CLI tool check | shutil.which, cached in _tool_checked set | ✅ lines 116-124, 257-259, 648 |
| §7.1 Hook payloads | CLIResponse with model_dump() | ✅ lines 57-88, empirical probe |
| §7.2 Structured logging | Logger: `kr.shared.llm.cli_adapter` | ✅ line 26 |
| §8.2 --backend flag (single) | run_integration_test.py lines 925-929 | ✅ |
| §8.3 --backend flag (batch) | run_full_integration.py diff reviewed | ✅ |
| §9.1-9.3 Client creation branch | mock/cli/api 3-way branch | ✅ lines 483-517 |
| §3.1 WARNING on unknown prefix | **⛔ FINDING F-2:** no WARNING log | |
| §3.2 Envelope extraction | **⛔ FINDING F-3:** no defensive extraction | |

## Invariant Verification
| Invariant | How Verified | Verified |
|---|---|---|
| INV-1: messages list not mutated | Empirical probe: deepcopy comparison after retry | ✅ |
| INV-2: No pipeline code touched | `git diff 2a8560b4^..2a8560b4 -- engines/` → empty | ✅ |
| INV-2b: No shared/__init__.py | `ls shared/__init__.py` → "No such file" | ✅ |
| INV-3: Existing tests pass | 766 passed, 2 skipped (identical to baseline) | ✅ |
| INV-4: `--backend api` unchanged | diff shows only additive branches, else = original | ✅ |
| INV-5: Arabic diacritics | `text=True` in all subprocess.run + empirical Arabic probe | ✅ |
| INV-6: Temp file cleanup | `try/finally` at lines 584-594, both files | ✅ |
| INV-7: OAuth token not logged | token only in env dict (line 519), not in cmd or hooks | ✅ empirical |

## Pass 2: Adversarial Probes
| Probe | Result | Finding? |
|---|---|---|
| P-1: JSON extraction — raw JSON | PASS | ✅ No |
| P-2: JSON extraction — markdown fenced | PASS | ✅ No |
| P-3: JSON extraction — text around JSON | PASS | ✅ No |
| P-4: JSON extraction — nested braces | PASS (nested `{}` works, two separate objects fails — acceptable) | ✅ No |
| P-5: Retry with ValidationError — Field constraint | PASS — error details included in retry prompt | ✅ No |
| P-6: Retry with ValidationError — model_validator | PASS — "value > 50 requires label=high" in retry prompt | ✅ No |
| P-7: Retry exhausted → correct exception type | PASS — raises `ValidationError` not `CLIBackendError` | ✅ No |
| P-8: OAuth token refresh on auth error | Covered by test_oauth_token_refresh_on_auth_error | ✅ No |
| P-9: Codex schema patching — real ClassificationResult | PASS — top-level + $defs entries all patched | ✅ No |
| P-10: Provider routing — unknown prefix | Routes to default backend correctly (no WARNING — F-2) | ✅ F-2 |
| P-11: Hook payload shape — integration test attrs | PASS — usage.model_dump(), choices[0].finish_reason, choices[0].message.content all work | ✅ No |
| P-12: max_retries=0 → exactly 1 call | PASS — mock_run.call_count == 1 | ✅ No |
| P-13: Hook fires with **kwargs expansion | PASS — on_request(**kwargs) receives expanded dict | ✅ No |
| P-14: No system message → schema-only prompt | Produces prompt with leading \n\n — F-4 | ✅ F-4 |
| P-15: extract_json returns str (not dict/list) | Confirmed returns str — F-1 | ✅ F-1 |
| P-16: Empty codex output file | PASS — raises CLIBackendError via extract_json | ✅ No |
| P-17: Arabic text through adapter | PASS — byte-perfect preservation | ✅ No |
| P-18: INV-1 messages not mutated after retry | PASS — deepcopy comparison identical | ✅ No |
| P-19: Claude envelope scenario | extract_json returns envelope, not model output — F-3 | ✅ F-3 |
| P-20: Subprocess env inherits os.environ | PASS — all env keys present + ANTHROPIC_API_KEY added | ✅ No |

## Pass 3: Self-Verification
- [x] Every factual claim from Passes 1-2 re-verified with tool call (grep line numbers, re-run tests, re-read functions)
- [x] Checked for rationalization: F-3 upgraded from CONDITIONAL to BLOCKING
- [x] Notes drafted with code citations (all line numbers verified)
- [x] CC concurrent review completed (Rule 9): 4 findings aligned, CC test count corrected
- [x] Standing Order 7 (unconstrained adversarial pass): Arabic probe, empty codex output, INV-1 mutation probe — no new findings

## Findings Ledger

| # | Finding | Severity | Line(s) | Root Cause |
|---|---------|----------|---------|------------|
| F-1 | `extract_json()` returns `str`, SPEC §4.5 says `dict\|list` | BLOCKING (HIGH) | 146, 324 | Pre-fix SPEC |
| F-2 | `_resolve_backend()` missing WARNING on unknown prefix | BLOCKING (HIGH) | 206-211 | Pre-fix SPEC |
| F-3 | No Claude `--output-format json` envelope extraction | **BLOCKING (CRITICAL)** | 530 | Pre-fix SPEC + no empirical test |
| F-4 | Empty system message → leading `\n\n` in prompt | BLOCKING (MEDIUM) | 278-284 | Pre-fix SPEC |

CC independently found all 4 findings (labeled 1-4 in CC's audit). Zero discrepancy between reviewers on finding identification.

### F-3 Severity Upgrade — Empirical Confirmation (CC Pass 2)

CC ran `claude -p "Say hello" --bare --no-session-persistence --max-turns 2 --output-format json --model opus` on the owner's Windows machine. The actual stdout is a JSON envelope:
```json
{"type":"result","subtype":"success","is_error":false,"duration_ms":2543,
 "result":"hello","stop_reason":"end_turn","total_cost_usd":0.02924625,
 "usage":{"input_tokens":3,"output_tokens":4,...},...}
```
The model's text is at `envelope["result"]`. Without extraction, every Claude CLI call fails permanently (validation error on envelope schema → retry → same envelope → all retries exhausted).

**Bonus:** The envelope provides free metadata we currently hardcode as `None`:
- `usage.input_tokens` / `usage.output_tokens` → real token counts
- `total_cost_usd` → per-call cost tracking
- `duration_api_ms` → precise API latency
- `stop_reason` → model stop reason

## Build Metrics
- Implementation lines: 668 (cli_adapter.py) + 73 (script changes) = 741 total
- Test lines: 772 (test_cli_adapter.py)
- New tests: 30
- Test-to-code ratio: 4.1 tests per 100 impl lines (healthy)
- SPEC sections: 14/14 addressed, 4 with findings

## Verdict

**BLOCKED** — 4 findings (1 CRITICAL, 2 HIGH, 1 MEDIUM). The CRITICAL finding (F-3) means the Claude backend is completely non-functional in production — every real call fails. All findings are SPEC-code divergences caused by CC building from the pre-amendment SPEC. No logic bugs in what CC built; the code faithfully implements the pre-fix SPEC. Fixes are surgical. Fix directive in NEXT.md.

- Review checklist commit: 9d83bb14
- Updated checklist commit: (this commit)
