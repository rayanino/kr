# Hook Wiring Status — Reference

Updated 2026-03-31. All hooks are LIVE in `.claude/settings.json`.

## Active PreToolUse Hooks

| Hook | Matcher | Script | Status |
|------|---------|--------|--------|
| Destructive command blocker | `Bash` | Inline (settings.json) | LIVE |
| Config protection | `Write\|Edit\|MultiEdit` | `config-protection.sh` | LIVE |
| Pre-push test gate | `Bash(git push*)` | Inline (settings.json) | LIVE |
| Pre-commit check | `Bash(git commit*)` | `pre-commit-check.sh` | LIVE |
| Circuit breaker | `Bash` | `circuit-breaker.sh` | LIVE |
| Cost overspend guard | `Bash` | `cost-guard.sh` | LIVE |
| No-ask-human (overnight) | `AskUserQuestion` | `no-ask-human.sh` | LIVE (requires `KR_OVERNIGHT=1`) |

## Active PostToolUse Hooks

| Hook | Matcher | Script | Status |
|------|---------|--------|--------|
| Ruff format | `Write\|Edit\|MultiEdit` | `ruff-format.sh` | LIVE |
| SPEC/code change reminder | `Write\|Edit\|MultiEdit` | Inline (settings.json) | LIVE |
| Arabic safety check | `Write\|Edit\|MultiEdit` | `arabic-safety-check.sh` | LIVE |
| Auto-staging | `Write\|Edit\|MultiEdit` | Inline (settings.json) | LIVE |
| Pyright type check | `Write\|Edit\|MultiEdit` | `pyright-check.sh` | LIVE |
| Auto-test | `Write\|Edit\|MultiEdit` | `auto-test.sh` | LIVE |
| Boundary check (D-023) | `Write\|Edit\|MultiEdit` | `boundary-check.sh` | LIVE |
| Diacritic preservation | `Write\|Edit\|MultiEdit` | `diacritic-preservation.sh` | LIVE |
| SPEC coverage check | `Write\|Edit\|MultiEdit` | `spec-coverage-check.sh` | LIVE |

## Other Lifecycle Hooks

| Hook | Event | Script | Status |
|------|-------|--------|--------|
| Session state save | Stop | `session_stop.py` | LIVE |
| Quality gate | Stop | `stop-quality-gate.sh` | LIVE |
| Prompt context | UserPromptSubmit | `prompt-context.sh` | LIVE |
| Pre-compact checkpoint | PreCompact | `pre-compact-checkpoint.sh` | LIVE |
| Post-compact recovery | PostCompact | `post-compact-recovery.sh` | LIVE |
| Settings change monitor | FileChanged(settings.json) | Inline | LIVE |
| Compaction recovery | SessionStart(compact) | Inline | LIVE |
| Startup context | SessionStart(startup\|resume) | Inline | LIVE |

## Toggle Control

All hooks can be individually disabled via `.claude/hooks/config/hooks-config.json`.
Personal overrides go in `.claude/hooks/config/hooks-config.local.json` (git-ignored).

## Environment Variables

- `KR_OVERNIGHT=1` — Enables no-ask-human hook, adjusts cost-guard and stop-quality-gate behavior
- `KR_BUDGET_LIMIT` — EUR budget cap for cost-guard (default: 100)
- `CLAUDE_RAPID_MODE=1` — Skips auto-test and pyright hooks for fast iteration

## Verification

Test individual hooks:
1. **Circuit breaker:** `echo '{"tool_input":{"command":"echo test"}}' | bash .claude/hooks/circuit-breaker.sh` — exits 0
2. **Cost guard:** `echo '{"tool_input":{"command":"python openrouter"}}' | bash .claude/hooks/cost-guard.sh` — exits 0 (under budget)
3. **No-ask-human:** Set `KR_OVERNIGHT=1`, run `echo '{"tool_input":{"question":"test?"}}' | bash .claude/hooks/no-ask-human.sh` — outputs block decision

## Related

- MCP cleanup plan: `.claude/MCP_ACTION_PLAN.md` (manual action, requires Claude Desktop restart)
- Hook scripts: `.claude/hooks/` (19 scripts)
