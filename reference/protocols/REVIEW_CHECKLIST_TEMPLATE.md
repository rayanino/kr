# CC Review Checklist — Session [N]: [Title]

> **This file is the review artifact.** Fill every checkbox, commit this file, THEN deliver the verdict.  
> An unfilled checklist = an incomplete review. Do NOT deliver a verdict without committing this file.  
> **REVIEW_PROTOCOL.md is the authority — NOT the kr-reviewing-cc-output skill's verdict template.**

## Pre-review
- [ ] Repo pulled, commit diff read
- [ ] NEXT.md re-read — what was requested?

## Pass 1: Structural
- [ ] Every CC-modified file opened and read (not skimmed) — list files:
  - [ ] `[file1]`
  - [ ] `[file2]`
- [ ] All tests run: `[N] passed, [N] skipped, [N] failed`
- [ ] SPEC cross-reference: every function traces to a § rule
- [ ] **Cross-engine boundary check:**
  - [ ] `grep -rn` for every modified contract type across ALL engines
  - [ ] `python tools/check_cross_engine_contracts.py` → result: `[PASS/FAIL]`
  - [ ] Each downstream consumer verified to accept the new shape
  - Modified types: `[list them]`
  - Consumers checked: `[list engines/files]`

## Pass 2: Adversarial
- [ ] 3+ probing scripts run with constructed inputs — findings:
  - Probe 1: `[description]` → `[result]`
  - Probe 2: `[description]` → `[result]`
  - Probe 3: `[description]` → `[result]`
- [ ] 2+ fixture semantic spot-checks — printed actual Arabic text:
  - Fixture 1: `[name]` — `[observation]`
  - Fixture 2: `[name]` — `[observation]`
- [ ] Cross-engine data flow: constructed realistic output, verified deserialization into downstream contracts
- [ ] Edge case probes with constructed inputs: `[N]` run, `[findings]`

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
> Fill this line ONLY after every checkbox above is checked and every finding is fixed.  
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
