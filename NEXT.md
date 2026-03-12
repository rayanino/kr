# NEXT — Step 3 Bug Review (Owner)

## Status: Step 3 Aggregation COMPLETE → Owner Review of Findings

Phase C ran 73 books, evaluated across 7 sessions, aggregated into a single report. The aggregation report (`PHASE_C_AGGREGATION_REPORT.md`) identified bugs and findings. **The owner has NOT yet reviewed these findings.**

---

## CRITICAL FRAMING

**We are building a 7-engine pipeline, NOT populating a library.** The 2,519 Shamela books are a local test sample. Library population happens only after all 7 engines are proven.

**We are still in Step 3.** Step 3 is not done until:
1. Owner reviews all findings from the aggregation report
2. Owner confirms (or expands) the complete bug list using domain expertise
3. Claude Code fixes every confirmed bug
4. Fixes are verified

Only then does Step 4 planning begin.

---

## Current Task: Owner Reviews Aggregation Findings

### What the aggregation report found

**PHASE_C_AGGREGATION_REPORT.md** contains 13 findings and 7 recommendations:

**3 Must-Fix Bugs:**
1. Tahqiq-note ML auto-correction — 3 books have wrong is_multi_layer=true (§4.1.1)
2. Author confidence not surfaced — result.json always shows 1.0 (§4.1.2)
3. 71% gate-abort rate from empty scholar registry (§4.1.3)

**2 Should-Fix Bugs:**
4. Death date false-positive classification — 7 books mislabeled (§4.2.1)
5. Genre/ML auto-correction creates impossible state (§4.2.2)

**2 Nice-to-Have:**
6. Genre taxonomy expansion — nukat, jarh_wa_tadil (§4.3.1)
7. Consensus expansion to check ML and authority_level (§4.3.2)

### What the owner must do

Read the aggregation report (especially Sections 3 and 4) with your domain expertise and ask:
- Are there domain-level issues the report missed?
- Are the priority assignments correct? (Should any should-fix be must-fix? Any must-fix actually not critical?)
- Are there books in the 73 where you know the pipeline output is wrong but the evaluator couldn't tell?
- Are the genre taxonomy recommendations correct from an Islamic studies perspective?

### What happens after owner review

Owner confirms the final bug list → Claude Code gets a single task with ALL bugs to fix → fixes are verified → Step 3 is CLOSED → Step 4 planning begins.

---

## Governing Documents

1. **This file** (NEXT.md)
2. **PHASE_C_AGGREGATION_REPORT.md** — the report to review
3. **PHASE_C_ERRATA.md** — corrections to the evaluation framework
4. **RESULT_PRESERVATION.md** — how results are saved
