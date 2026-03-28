# Handoff Checklist — CLI Adapter Review

**Date:** 2026-03-28
**Commit:** (CC's commit hash — fill after CC pushes)
**Architect:** Claude Chat
**Baseline:** 766 passed, 2 skipped (pre-CC)
**Expected after CC:** 796 passed, 2 skipped (766 existing + 30 new)

---

## Step 2: Test Baseline
- [ ] pytest run on `engines/excerpting/tests/`: `766 passed, 2 skipped`
- [ ] pytest run on `shared/llm/tests/`: `30 passed`
- [ ] Combined: `796 passed, 2 skipped`
- [ ] Count matches NEXT.md expectation: yes/no

## Step 3: File References Verified
| File | Exists | Content Verified |
|------|--------|-----------------|
| `shared/llm/__init__.py` | ☐ | ☐ (empty) |
| `shared/llm/cli_adapter.py` | ☐ | ☐ |
| `shared/llm/tests/__init__.py` | ☐ | ☐ (empty) |
| `shared/llm/tests/test_cli_adapter.py` | ☐ | ☐ |
| `scripts/run_integration_test.py` (modified) | ☐ | ☐ |
| `scripts/run_full_integration.py` (modified) | ☐ | ☐ |

## SPEC Compliance (§-by-§ trace)
| SPEC Section | Implementation | Verified |
|---|---|---|
| §2.1 Constructor | `__init__(default_backend)` | ☐ |
| §2.2 Namespace chain | `_ChatNamespace` / `_CompletionsNamespace` | ☐ |
| §2.3 `create()` signature | All 6 named params + `**kwargs` | ☐ |
| §2.4 Hook registration | `.on()` with 3 event names | ☐ |
| §3.1 Provider routing | Model prefix → backend mapping | ☐ |
| §3.2 Claude backend | `--bare --no-session-persistence --max-turns 2 --output-format json --model opus` | ☐ |
| §3.3 Codex backend | `codex exec --output-schema ... -s read-only -o ...` | ☐ |
| §3.4 Gemini backend | `gemini -p ... -y --output-format text` | ☐ |
| §4.1 Retry semantics | max_retries=N → N+1 total attempts | ☐ |
| §4.2 Attempt loop | Catches JSONDecodeError, ValidationError, TimeoutExpired, CalledProcessError | ☐ |
| §4.3 Validation error feedback | Includes field paths + enum values | ☐ |
| §4.4 JSON parse error feedback | Includes first 500 chars + error msg | ☐ |
| §4.5 JSON extraction | 3-step: direct parse → find braces → strip fences | ☐ |
| §5.1 Schema in system prompt (claude/gemini) | JSON schema appended to system message | ☐ |
| §5.2 Schema temp file (codex) | Written to tempfile, cleaned in finally | ☐ |
| §5.3 additionalProperties patching | Recursive, all object levels + $defs | ☐ |
| §6.1 CLIBackendError | Exception with backend + exit_code attrs | ☐ |
| §6.2 Subprocess invocation | capture_output, text=True, timeout, check=True | ☐ |
| §6.3 OAuth token | Reads ~/.claude/.credentials.json | ☐ |
| §6.4 CLI tool check | shutil.which, cached per backend | ☐ |
| §7.1 Hook payloads | CLIResponse with model_dump() on usage | ☐ |
| §7.2 Structured logging | Logger name kr.shared.llm.cli_adapter | ☐ |
| §8.2 --backend flag (single) | run_integration_test.py | ☐ |
| §8.3 --backend flag (batch) | run_full_integration.py | ☐ |
| §9.1-9.3 Client creation branch | mock / cli / api branching | ☐ |

## Invariant Verification
| Invariant | How Verified | Verified |
|---|---|---|
| INV-1: messages list not mutated | Code read: augmented prompt is new string | ☐ |
| INV-2: No pipeline code touched | `git diff --name-only` — no files in `engines/` | ☐ |
| INV-3: Existing tests unchanged | `git diff engines/excerpting/tests/` — empty | ☐ |
| INV-4: `--backend api` path untouched | Code read: else branch is original code | ☐ |
| INV-5: Arabic diacritics | `text=True` in subprocess, no normalize calls | ☐ |
| INV-6: Temp file cleanup | `try/finally` around temp file usage | ☐ |
| INV-7: OAuth token not logged | grep for token variable in log/hook payloads | ☐ |

## Pass 2: Adversarial Probes
| Probe | Result | Finding? |
|---|---|---|
| P-1: JSON extraction — raw JSON | | ☐ |
| P-2: JSON extraction — markdown fenced | | ☐ |
| P-3: JSON extraction — text around JSON | | ☐ |
| P-4: JSON extraction — nested braces | | ☐ |
| P-5: Retry with ValidationError — enum mismatch | | ☐ |
| P-6: Retry with ValidationError — model_validator | | ☐ |
| P-7: Retry exhausted → correct exception type | | ☐ |
| P-8: OAuth token refresh on auth error | | ☐ |
| P-9: Codex schema patching — deeply nested model | | ☐ |
| P-10: Provider routing — unknown prefix fallback | | ☐ |
| P-11: Hook payload shape — matches on_response attribute access | | ☐ |
| P-12: max_retries=0 → exactly 1 call | | ☐ |

## Pass 3: Self-Verification
- [ ] Every factual claim from Passes 1-2 re-verified with tool call
- [ ] Checked for rationalization patterns
- [ ] Notes drafted with code citations
- [ ] CC concurrent review completed (Rule 9)

## Verdict
- [ ] ALL boxes checked → ACCEPT / BLOCKED
- Commit: (hash)
