# Codex Relay Prompts

Use these when repo-native coworkers are blocked or when you want a relay-ready prompt for a deep-research channel.

## ChatGPT Deep Research

```text
You are reviewing the KR Codex control plane.

Authority constraints:
- active_authority=claude
- runtime_mode=shadow_setup
- do not suggest engine implementation

Review only these files:
- <paths>

Return:
1. concrete risks or regressions
2. why they matter operationally
3. smallest safe fixes
4. any missing verification
```

## Claude Deep Research

```text
Review this KR Codex setup/runtime task under claude authority.

Constraints:
- setup/runtime/shadow lanes only
- preserve Claude Code and Gemini workflow surfaces
- no engine implementation

Files:
- <paths>

Return only concrete findings, exact paths, and smallest safe follow-ups.
```

## Gemini Deep Research

```text
Audit this KR Codex control-plane change.

Constraints:
- active_authority remains claude
- the active Windows checkout is the canonical Codex lane unless a concrete blocker is documented
- focus on setup, runtime, hooks, scripts, docs, and verification only

Files:
- <paths>

Return:
1. bugs or weak assumptions
2. operational risk
3. smallest safe fix
4. any blocker you could not verify
```
