# NEXT — Phase D Evaluation

## Status: Pipeline run COMPLETE. Programmatic analysis COMPLETE. Per-book evaluation NEXT.

## What happened

204 books processed (73 reruns + 131 new), 100% success rate. Programmatic validation found 2 errors, 6 warnings, and verified trust math + SPEC compliance across all 204 books. Complete triage assigned every book to a review tier.

## Current task: 7 evaluation sessions

The evaluation follows 4 layers, governed by `PHASE_D_EVALUATION_PROTOCOL.md`:

| Session | What | Books | Status |
|---------|------|-------|--------|
| Layer 1 | Programmatic validation | 204 | ✅ COMPLETE |
| Layer 2 | Pattern analysis | 62 (as cohorts) | PENDING |
| Session A | Consensus disagreements | 14 | PENDING |
| Session B | Author uncertainty | 19 | PENDING |
| Session C | Structural flags | 15 | PENDING |
| Session D | Random calibration | 12 | PENDING |
| Layer 4 | Aggregation + GO/NO-GO | all | PENDING |

## How to run each session

Each session is an independent Claude Chat conversation in the KR project. Paste the session-specific prompt.

### Session startup sequence (every session)

1. Clone repo
2. Read `NEXT.md` (this file)
3. Read `PHASE_D_EVALUATION_PROTOCOL.md`
4. Read `EVALUATION_QUICK_REFERENCE.md`
5. Load triage: `tests/results/source_engine/phase_d/PHASE_D_TRIAGE.json`
6. Process assigned books per protocol

### Session-specific instructions

**Layer 2 (Pattern Analysis):** Read PHASE_D_TRIAGE.json for the 62 pattern_analysis books. Analyze as cohorts (genre disagreement patterns, attribution patterns). Also investigate: ERR-01 (النكت hashiyah/ML bug), WARN-01 (ML disagreements), WARN-02 (edition inconsistencies), WARN-04 (canonical_model recording bug), WARN-05 (trust flagging rate), WARN-06 (Opus canonical concentration). Output: `PHASE_D_PATTERN_ANALYSIS.md`, committed to repo.

**Session A:** Read PHASE_D_TRIAGE.json → sessions.A.books (14 books). Full per-book web search evaluation per protocol. Output: `PHASE_D_SESSION_A_REPORT.md`.

**Session B:** Read PHASE_D_TRIAGE.json → sessions.B.books (19 books). Full per-book web search evaluation per protocol. Output: `PHASE_D_SESSION_B_REPORT.md`.

**Session C:** Read PHASE_D_TRIAGE.json → sessions.C.books (25 books). Full per-book web search evaluation per protocol. Output: `PHASE_D_SESSION_C_REPORT.md`.

**Session D:** Read PHASE_D_TRIAGE.json → sessions.D.books (12 books). Full per-book web search evaluation per protocol. If ANY error found, note that sample should be expanded. Output: `PHASE_D_SESSION_D_REPORT.md`.

**Layer 4 (Aggregation):** Read all session reports + pattern analysis + PHASE_D_TRIAGE.json. Compute error rates. Compare with Phase C baseline. Write GO/NO-GO verdict. Output: `PHASE_D_AGGREGATION_REPORT.md`.

## Key files

- `PHASE_D_EVALUATION_PROTOCOL.md` — evaluation methodology and per-book procedure
- `PHASE_D_PROGRAMMATIC_ANALYSIS.md` — deep analysis from Layer 1 (genre patterns, attribution compliance, ML bias, trust root causes, edition consistency, specific errors)
- `EVALUATION_QUICK_REFERENCE.md` — compact checklist, re-read before each book
- `tests/results/source_engine/phase_d/PHASE_D_TRIAGE.json` — all 204 books triaged with assignments
- `tests/results/source_engine/phase_d/PHASE_D_AUTO_SCREENING.md` — auto-screening report
- `phase_c_collection/PHASE_C_ALL_VERDICTS.json` — Phase C verdicts for comparison
- `reference/archive/sessions/phase_c/PHASE_C_EVALUATION_FRAMEWORK.md` — full Phase C framework (reference)

## Key state

- Pipeline version: b81d5cb (post-bug-fix, smoke-tested)
- Budget spent: €30.10 (€9.70 pre-Phase D + €20.40 Phase D)
- Budget remaining: ~€70
- Books processed: 204 (73 reruns + 131 new)
- Success rate: 100% (0 gate_abort)
- Programmatic errors found: 2 (hashiyah/ML inconsistency, author disagreement)
- Phase C VERIFIED verdicts carried: 55 (41 gate_abort→success, 14 success→success)

## PREREQUISITE: Push per-book Phase D results

The per-book result files (result.json, extraction.json, consensus.json, llm_responses/) are on the owner's machine but NOT in git. Review sessions need these files.

**Owner action:** Run in the kr directory:
```
git add -f tests/results/source_engine/phase_d/*/
git commit -m "Add Phase D per-book results for evaluation"
git push
```

This adds ~204 book directories with ~6 files each (~1,200 files). Without this, evaluation sessions cannot read per-book pipeline data.
