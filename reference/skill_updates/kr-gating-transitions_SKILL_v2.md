---
name: kr-gating-transitions
description: Verifies all prerequisites before KR phase transitions. ALWAYS invoke before saying proceed, next step, or approving any transition. Do not approve transitions without this check first.
---

# KR Transition Gate

A phase transition (SPEC→Build, Build→Evaluate, Probe N→Probe N+1, Engine N→Engine N+1) is the highest-risk moment in the project. A premature transition propagates errors into all downstream work. This skill exists because the Architect once approved a transition without verifying prerequisites, and again approved with 12 findings rationalized as "non-blocking."

**QUALITY AXIOM:** The architect is the sole quality gate. The owner says "continue." If the architect approves a premature transition, everything downstream builds on a broken foundation. There is no safety net. See `reference/protocols/QUALITY_AXIOM.md`.

## When this skill activates

Any moment where the Architect would say "proceed," "next step," "ready for," "move on," or approve any transition. The transition may feel obvious — that feeling is the danger signal.

## Protocol — Two Rounds (QUALITY AXIOM: multi-round)

### ROUND 1: Evidence gathering

#### Step 1: Pull and read governing documents
Execute `git pull`. Read `reference/AGENT_ARCHITECTURE.md` and `reference/ENGINE_BUILD_BLUEPRINT.md` using tools. Not from memory. Not "I just read that" — read it again NOW.

#### Step 2: Name the transition
State explicitly: FROM → TO, governing doc section, Blueprint step.

#### Step 3: List and verify every prerequisite with TOOL-BASED EVIDENCE
For each prerequisite from the architecture and Blueprint:
```
- Prerequisite: [description] (source: [doc] §[section])
  Status: VERIFIED / NOT MET
  Evidence: [tool call: file path, commit hash, test output, grep result]
```

**Every status must have a tool call citation.** "VERIFIED (I remember reading this)" is NOT acceptable. "VERIFIED (view tool showed file X at line Y contains Z)" IS acceptable. Introspective verification ("I believe this is met") is banned.

#### Step 4: Check for outstanding findings
```bash
grep -rn 'BLOCKED\|finding\|must.fix\|TODO.*fix' reference/archive/sessions/reviews/ engines/*/KNOWN_LIMITATIONS.md
```
Any unresolved finding from prior sessions blocks until explicitly addressed.

**→ End Round 1. Deliver prerequisite report. End the response.**

### ROUND 2: Adversarial verification (separate response)

#### Step 5: Worst-case analysis
Not introspection ("am I feeling momentum pressure?") — that doesn't work. Instead, concrete analysis:
1. List every output the outgoing phase was supposed to produce.
2. For each output, verify it exists AND passes its quality criteria with a tool call.
3. For each output, ask: what happens to the NEXT engine if this output is wrong? Trace the specific failure path.

#### Step 6: Missing test check
Ask: "What's the most obvious test of the outgoing phase that hasn't been run?" Run it. If it passes, good. If it fails, the transition is BLOCKED.

This is the Rule 5 principle generalized: the most obvious test is the one most likely to be skipped.

#### Step 7: Verdict
```
## Transition verdict: APPROVED / BLOCKED

Prerequisites: [N/N verified with tool evidence]
Outstanding findings: [none / list]
Worst-case analysis: [done — no failure paths found / found: ...]
Missing test: [ran X, result: ...]
```

APPROVED requires: every prerequisite VERIFIED with tool evidence, zero outstanding findings, worst-case analysis completed, missing test passed.

BLOCKED requires: state exactly what must be fixed. Do not proceed.

There is no DEFERRED verdict. There is no "APPROVED with conditions." Fix it or block it.
