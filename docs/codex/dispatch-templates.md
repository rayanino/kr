# Codex Dispatch Templates

**See also:** `.claude/skills/coworker-dispatch/SKILL.md` for the master coworker dispatch protocol and Codex's role in multi-coworker milestones.

Use these templates as starting points for `explorer` and `worker` agents.

## Read-Only Code Reviewer

Use when a bounded review is needed on changed code.

```text
Review these files for structural correctness only:
- <paths>

Focus on:
1. wrong behavior against local contracts or tests
2. missing regression coverage
3. silent failure paths
4. Unicode or serialization risks that do not require Arabic semantic judgment

Do not edit files. Cite exact paths and symbols.
```

## Regression Hunter

Use when a bug class is suspected elsewhere in the same subsystem.

```text
Search the local codebase for more instances of this bug pattern:
- <pattern>
- <known file>

Return only concrete matches, risk notes, and the smallest safe follow-up actions.
Do not edit files.
```

## Contract Auditor

Use when changes may have broken upstream or downstream boundaries.

```text
Inspect these contracts and the code that consumes them:
- <contracts>
- <boundary scripts>

Find mismatches, dropped metadata, or broken assumptions with exact file references.
Do not edit files.
```

## Arabic-Risk Structural Reviewer

Use when code touches Arabic text handling but the task should stay structural.

```text
Review these files for Arabic-risk structural issues only:
- byte preservation
- unsafe normalization
- regex traps
- invisible Unicode hazards
- dropped or rewritten text

Do not make semantic claims about the Arabic content itself.
Do not edit files.
```

## Backend Prober

Use when a CLI or integration path needs bounded validation.

```text
Inspect this backend path and tell me:
1. exact command surface
2. config assumptions
3. likely failure points
4. the smallest safe smoke test to run next

Stay local to the repo and named scripts only.
Do not edit files.
```
