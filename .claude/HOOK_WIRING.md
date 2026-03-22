# Hook Wiring Guide — Paste into settings.json

Created 2026-03-23 by overnight hardening session.
These hook scripts are ready but need to be wired into `.claude/settings.json`.

**Why deferred:** Editing settings.json triggers a user approval prompt,
which would block an autonomous overnight session.

## Instructions

Add these entries to the `"PreToolUse"` array in `.claude/settings.json`:

### 1. Circuit Breaker (prevents infinite retry loops)

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/circuit-breaker.sh\"",
      "timeout": 5
    }
  ]
}
```

### 2. Cost Overspend Guard (blocks API calls when budget exceeded)

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/cost-guard.sh\"",
      "timeout": 10
    }
  ]
}
```

### 3. No-Ask-Human (blocks questions during overnight sessions)

```json
{
  "matcher": "AskUserQuestion",
  "hooks": [
    {
      "type": "command",
      "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/no-ask-human.sh\"",
      "timeout": 5
    }
  ]
}
```

## Activation

- Circuit breaker and cost guard are always active.
- No-ask-human requires: `export KR_OVERNIGHT=1` before starting the session.
  Set this in `.claude/settings.json` under `"env"` for overnight sessions:
  ```json
  "env": {
    "KR_OVERNIGHT": "1"
  }
  ```
  Remove or set to "0" for interactive sessions.

## Verification

After wiring, test each hook:
1. **Circuit breaker:** Run `echo "test" | bash .claude/hooks/circuit-breaker.sh` — should exit 0
2. **Cost guard:** Run `echo '{"tool_input":{"command":"python openrouter"}}' | bash .claude/hooks/cost-guard.sh` — should exit 0 (under budget)
3. **No-ask-human:** Set `KR_OVERNIGHT=1`, run `echo '{"tool_input":{"question":"test?"}}' | bash .claude/hooks/no-ask-human.sh` — should output block decision
