# Handoff Checklist — Session {N}: {Title}

**Date:** {date}
**Commit:** {hash}
**Architect:** Claude Chat

---

## Step 2: Test Baseline
- [ ] pytest run: `{N} passed, {M} skipped`
- [ ] Count matches NEXT.md header: {yes/no}

## Step 3: File References
| File | Exists | Lines Verified |
|------|--------|---------------|
| {path1} | ☐ | ☐ |
| {path2} | ☐ | ☐ |

## Step 5: SPEC Example Traces
| SPEC Section | Example Lines | Algorithm Output | SPEC Expected | Match |
|---|---|---|---|---|
| §{X} | {N}-{M} | {actual} | {expected} | ☐ |

## Step 6: Fixture Testing
| Detection Logic | Total Pages | Matches | Rate | Acceptable |
|---|---|---|---|---|
| {pattern} | {N} | {M} | {%} | ☐ |

## Step 7: Prerequisites
- [ ] Test baseline verified (Step 2)
- [ ] All Read First files exist
- [ ] All line numbers verified
- [ ] SPEC sections referenced specifically
- [ ] Do NOT Do covers scope creep
- [ ] Verification has concrete pass/fail
- [ ] AGENT_ARCHITECTURE.md checked
- [ ] ENGINE_BUILD_BLUEPRINT.md checked
- [ ] Fixture claims verified by running code
- [ ] SPEC thresholds copy-pasted with line numbers
- [ ] All SPEC examples traced (Step 5)
- [ ] New detection logic tested on fixtures (Step 6)
- [ ] Cross-engine contracts verified

## Step 8: Adversarial Questions
1. Judgment calls not covered? {answer}
2. Missing files? {answer}
3. Ambiguous "done"? {answer}
4. Wrong output that passes verification? {answer}
5. Unverified claims? {answer}
6. Missing test helpers? {answer}

## Verdict
- [ ] ALL boxes checked → READY
- Commit: {hash}
