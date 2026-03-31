---
name: codex-verify
description: Independent code review via Codex MCP for D-041 multi-model verification. Use after writing or modifying engine source code, contracts.py, or test files to get a cross-model structural review.
---

# Codex Cross-Verification Skill

Use this skill after completing a code modification task to get an independent
structural review from OpenAI Codex via MCP.

## When to Use

- After writing or modifying Python code (engines/*/src/, shared/*/src/)
- After creating new test files
- After modifying contracts.py
- When D-041 multi-model consensus is required for a code decision

## How to Use

1. Complete your code changes and commit
2. Call the Codex MCP `review` tool (if available) or `codex` tool with:
   - `prompt`: "Review git diff HEAD~1 for structural issues"
   - `fullAuto`: true
3. Compare Codex findings with your own assessment
4. Log discrepancies to `overnight/decisions.log`

## CRITICAL: Arabic Domain Boundary

Codex has NO Arabic text understanding. Only ask Codex to review:

- Python code structure and design patterns
- Pydantic model definitions and validation logic
- Type safety and error handling patterns
- Test completeness and assertion coverage
- Import organization and dependency management

NEVER ask Codex about:

- Arabic text content, diacritics, or encoding
- Scholarly domain logic (genre, attribution, taxonomy)
- SPEC interpretation involving Arabic examples
- Any decision that requires understanding Arabic NLP
