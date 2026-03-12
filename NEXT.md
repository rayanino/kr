# NEXT — Step 3 Bug Identification (Claude Chat)

## Status: Step 3 Aggregation COMPLETE → Exhaustive Bug Identification

Phase C ran 73 books, evaluated across 7 sessions, aggregated into `PHASE_C_AGGREGATION_REPORT.md`. The aggregation found 13 findings and 7 recommendations. **These findings have NOT been exhaustively verified. More bugs may exist.**

---

## CRITICAL FRAMING

**We are building a 7-engine pipeline, NOT populating a library.** The 2,519 Shamela books are a local test sample. Library population happens only after all 7 engines are proven.

**We are still in Step 3.** Step 3 is not done until:
1. Claude Chat exhaustively reviews findings and the actual engine code/results to identify EVERY bug
2. Owner confirms domain-level questions if they arise
3. Claude Code fixes every confirmed bug
4. Fixes are verified

Only then does Step 4 planning begin.

---

## Current Task: Exhaustive Bug Identification

### What exists already

The aggregation report identified these issues:

**3 flagged as Must-Fix:**
1. Tahqiq-note ML auto-correction — 3 books wrong (§4.1.1)
2. Author confidence not surfaced — always 1.0 in result.json (§4.1.2)
3. 71% gate-abort rate from empty scholar registry (§4.1.3)

**2 flagged as Should-Fix:**
4. Death date false-positive classification (§4.2.1)
5. Genre/ML auto-correction creates impossible state (§4.2.2)

**2 flagged as Nice-to-Have:**
6. Genre taxonomy expansion (§4.3.1)
7. Consensus expansion to ML/authority_level (§4.3.2)

### What this session must do

The aggregation report was produced by a context-heavy session. It may have missed bugs. This session must:

1. Read the aggregation report (Sections 3 and 4 especially)
2. Read the actual Phase C results — dig into the per-book JSON files in `tests/results/source_engine/phase_c/` for patterns the aggregation missed
3. Read the engine source code for any bugs that correct test output might be hiding (e.g., a bug that happens to produce the right answer on these 73 books but would fail on others)
4. Cross-reference findings against the SPEC to find any SPEC violations not caught by evaluation
5. Produce a COMPLETE, FINAL bug list — every bug, prioritized, with evidence
6. Escalate domain questions to the owner if needed

### What happens after this session

Complete bug list → Claude Code fixes ALL bugs in one session → fixes verified → Step 3 CLOSED → Step 4 planning begins.

---

## Governing Documents (read in this order)

1. **This file** (NEXT.md)
2. **PHASE_C_AGGREGATION_REPORT.md** — aggregation analysis
3. **PHASE_C_ERRATA.md** — framework corrections
4. **phase_c_collection/PHASE_C_ALL_VERDICTS.json** — raw verdict data
5. **RESULT_PRESERVATION.md** — result preservation protocol
6. **SPEC_CORE.md** — the behavioral authority for the source engine
7. **engines/source/src/** — the actual engine code
