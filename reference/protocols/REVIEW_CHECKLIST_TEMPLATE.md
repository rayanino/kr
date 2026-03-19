# CC Review Checklist — Session [N]: [Title]

> **This file is the review artifact.** Fill every checkbox, commit this file, THEN deliver the verdict.  
> An unfilled checklist = an incomplete review. Do NOT deliver a verdict without committing this file.  
> **REVIEW_PROTOCOL.md is the authority — NOT the kr-reviewing-cc-output skill's verdict template.**

## Pre-review
- [ ] Repo pulled, commit diff read
- [ ] NEXT.md re-read — what was requested?

## Pass 1: Structural
- [ ] Every CC-modified file opened and read **in full** (not truncated) — list files:
  - [ ] `[file1]` — `[N] functions/patterns/classes` (verified by grep)
  - [ ] `[file2]` — `[N] functions/patterns/classes` (verified by grep)
  - **RULE 7 check:** If any file was truncated by the view tool, the truncated range was requested and read before proceeding.
- [ ] All tests run: `[N] passed, [N] skipped, [N] failed`
- [ ] SPEC cross-reference: every function traces to a § rule
- [ ] **Cross-engine boundary check:**
  - [ ] `grep -rn` for every modified contract type across ALL engines
  - [ ] `python tools/check_cross_engine_contracts.py` → result: `[PASS/FAIL]`
  - [ ] Each downstream consumer verified to accept the new shape
  - Modified types: `[list them]`
  - Consumers checked: `[list engines/files]`

**→ End response after Pass 1. Context switch forces fresh eyes for Pass 2. (RULE 8)**

## Pass 2: Adversarial
- [ ] 3+ probing scripts run with constructed inputs — findings:
  - Probe 1: `[description]` → `[result]`
  - Probe 2: `[description]` → `[result]`
  - Probe 3: `[description]` → `[result]`
- [ ] 2+ fixture semantic spot-checks — printed actual Arabic text:
  - Fixture 1: `[name]` — `[observation]`
  - Fixture 2: `[name]` — `[observation]`
- [ ] Cross-engine data flow: constructed realistic output, verified deserialization into downstream contracts
- [ ] **SPEC concrete example trace (RULE 5):** For each SPEC section with a worked example:
  - [ ] SPEC §[N] example traced — implementation output: `[summary]`
  - [ ] Divergences: `[list or "none"]`
  - [ ] Each divergence classified as: finding / documented deferred capability
- [ ] Edge case probes with constructed inputs: `[N]` run, `[findings]`

**→ End response after Pass 2. Verdict is NEVER in the same response as probes. (RULE 8)**

## Pass 3: Self-verification (RULES 6-7)
- [ ] Every factual claim in Passes 1-2 verified against code with tool calls:
  - [ ] "N patterns/functions" claims — verified by grep count
  - [ ] "Not implemented" claims — verified by grep (must show zero matches)
  - [ ] "Correctly handles X" claims — verified by running probe
- [ ] Check for rationalization patterns: any finding I downplayed or explained away?
- [ ] Review Notes drafted — each Note verified against code before writing

## Findings
> List ALL findings. There are no "non-blocking" findings. Every finding listed here must be FIXED before the verdict line below is filled.

| # | File | Finding | Fix | Fixed? |
|---|------|---------|-----|--------|
| 1 | | | | [ ] |

## Fixes committed
- [ ] ALL findings above have `Fixed? [x]`
- [ ] Fix commits pushed to repo
- [ ] Tests re-run after fixes: `[N] passed`
- [ ] `python tools/check_cross_engine_contracts.py` re-run after fixes → `[PASS/FAIL]`

## Verdict
> Fill this line ONLY after Passes 1, 2, AND 3 are complete, every checkbox is checked, and every finding is fixed.
> The verdict is NEVER delivered in the same response as Pass 2 probes (RULE 8).
> **ACCEPT** = zero unfixed findings, repo clean.  
> **BLOCKED** = findings exist that couldn't be fixed in this review.  
> "ACCEPT WITH FIXES" does not exist. "Non-blocking" does not exist.

**Verdict: ___________**

## Build metrics (cumulative)
```
Implementation: [N] lines (+[M] this session)
Tests: [N] passing (+[M] this session)
ADV covered: [N]/51
Known limitations: [list]
```
