# Handoff — Excerpting Engine Review Continuation

**Date:** 2026-03-24
**From:** Claude Chat (Architect), Session 4 review chat (Round 1 deep analysis)
**To:** Claude Chat (Architect), next chat session(s)
**Repo state:** commit `721de52f`, 540 tests passing

---

## What Happened in This Chat

### Round 1 Deep Analysis (20 analysis angles)
Architect performed structural review of Session 4 (commit `4a7f71e9` — Phase 3 LLM enrichment + consensus verification). Found 8 bugs across `phase3_enrichment.py` and `phase3_consensus.py`.

### CC Adversarial Audit (independent)
A separate CC session ran an adversarial bug-hunting audit on the same code. CC independently confirmed 2 of the architect's findings and found 2 additional bugs the architect missed:
- **CC-F3 (HIGH):** `apply_enrichment` PARTIAL + None context_hint → I-ER-4 crash. Architect missed this — it's a reachable crash path.
- **CC-F5 (corrected architect):** Architect's F-1 (FULL→PARTIAL repair crash) is DEAD CODE — unreachable because `_needs_consensus` never triggers SELF_CONTAINMENT for FULL excerpts.

### Corrected Finding List (9 total)
After cross-referencing, the final corrected finding list:

| # | Severity | Finding | Fix |
|---|----------|---------|-----|
| 1 | CRITICAL | Attribution majority not applied to excerpt (T-2) | Apply majority to primary_author_layer |
| 2 | HIGH | PARTIAL + None hint from LLM → I-ER-4 crash | Fallback chain in apply_enrichment |
| 3 | MEDIUM | EX-G-003 over-triggers (wrong condition) | Check verifier vs source, not verifier vs enrichment |
| 4 | MEDIUM | startswith chunk matching false-matches | Exact match + split_id fallback |
| 5 | MED-HIGH | Verification items matched by position not index | Index-based dict lookup |
| 6 | LOW-MED | _parse_self_containment substring order | Exact match first, conservative substring |
| 7 | MEDIUM | Gate entry missing assessments | Include consensus decisions |
| 8 | MEDIUM | consensus_metadata set after _repair reads it | Move assignment before repair call |
| 9 | LOW-MED | Phantom "unknown" voter | Use None, flexible majority function |

### CC Fix Execution
CC implemented all 9 fixes + 23 new tests. All acid tests pass. 83 Session 4 tests total (was 60).

### CC Scope Creep
**CC also implemented Session 5 (validation + writer + orchestrator) and Session 6 (integration tests) in the same push — ~3,000 lines, 75 tests, without architect authorization.** This work exists in the repo but has NOT been reviewed.

Files from unauthorized work:
- `engines/excerpting/src/phase3_orchestrator.py` (188 lines — NEW)
- `engines/excerpting/src/phase3_validation.py` (251 lines expanded)
- `engines/excerpting/src/pipeline.py` (161 lines expanded)
- `engines/excerpting/src/writer.py` (172 lines expanded)
- `engines/excerpting/tests/test_phase3_validation.py` (33 tests — NEW)
- `engines/excerpting/tests/test_writer.py` (17 tests — NEW)
- `engines/excerpting/tests/test_integration.py` (25 tests — NEW)
- `engines/excerpting/tests/test_phase3_deterministic.py` (286 lines added — overnight hardening)
- Various `overnight/` files

---

## Current Repo State

```
HEAD: 721de52f
Branch: master
Tests: 540 passed, 2 skipped, 0 failed
```

### What is reviewed and accepted:
- Phase 1 (assembly): ✅ all prior sessions
- Phase 2 (classification + grouping): ✅ all prior sessions
- Phase 3.1 (deterministic): ✅ Session 3 ACCEPTED
- Phase 3.2 (enrichment): Session 4 — FIXES APPLIED, awaiting Round 2+3
- Phase 3.3 (consensus): Session 4 — FIXES APPLIED, awaiting Round 2+3

### What exists but is NOT reviewed:
- Phase 3.4 (validation): CC-implemented, no architect handoff
- Phase 3 orchestrator: CC-implemented, no architect handoff
- Output writer: CC-implemented, no architect handoff
- Integration tests: CC-implemented, no architect handoff

---

## Task Queue (execute in order)

### Task 1: Session 4 Review — Round 2 (Adversarial Probing on Fixed Code)

**What:** Run adversarial probes on the 9 fixed functions in `phase3_enrichment.py` and `phase3_consensus.py`. This is Round 2 of the 3-pass review protocol.

**Scope:** ONLY `phase3_enrichment.py` and `phase3_consensus.py` changes. Do NOT review the unauthorized Session 5/6 work.

**Protocol:** Follow `reference/protocols/REVIEW_PROTOCOL.md` Pass 2 requirements:
- 3+ probing scripts with constructed inputs
- 2+ fixture semantic spot-checks with printed Arabic
- SPEC concrete example traces for §7.2 and §7.3
- Cross-engine data flow verification
- Verify each of the 9 fixes individually with adversarial inputs

**CC Parallel Audit Prompt:**
```
Read engines/excerpting/src/phase3_enrichment.py and engines/excerpting/src/phase3_consensus.py in full. For each of the 9 fixes (see NEXT.md "Corrected After CC Adversarial Audit"), construct an adversarial input that would expose a regression or incomplete fix:

1. Fix 1 (attribution majority): Construct a case where majority=verifier but the verifier's author_id contains Arabic characters. Does primary_author_layer.author_id preserve them exactly?
2. Fix 2 (PARTIAL hint fallback): Construct a PARTIAL unit where self_containment_notes is also None (should this be possible? If so, does the generic fallback fire?). Verify roundtrip.
3. Fix 3 (EX-G-003): Construct the case where source_school=None. Does the fix crash or skip gracefully?
4. Fix 4 (chunk matching): Construct chunks where div_id contains underscores that look like split suffixes (e.g., div_id="book_1_chapter_2"). Does the split_id fallback false-match?
5. Fix 5 (item_index): Construct a case with duplicate item_index values in the LLM response. What happens?
6. Fix 6 (parse): What happens with empty string input? What about "PARTIALLY FULL"?
7. Fix 7 (gate assessments): Construct a gate entry where consensus_metadata is None (enrichment-failed excerpt). Does it crash or produce empty assessments?
8. Fix 8 (ordering): Verify that the consensus_metadata is readable in _repair_context_hint by constructing a FULL→PARTIAL downgrade scenario (even though it's currently dead code — defensive check).
9. Fix 9 (phantom voter): What if escalation_client is None AND verifier has no alternative? Trace through the code path.

Write findings. Do NOT fix anything.
```

**Deliverable:** Round 2 findings list. End the response.

---

### Task 2: Session 4 Review — Round 3 (Self-Verification + Verdict)

**What:** Verify every claim from Rounds 1-2, check for rationalization, fill checklist, deliver verdict.

**Protocol:** Follow `reference/protocols/REVIEW_PROTOCOL.md` Pass 3:
- Verify every factual claim from Rounds 1-2 with tool calls (RULE 6)
- Check for rationalization patterns
- Fill `reference/archive/sessions/reviews/review_excerpting_session4.md`
- Commit checklist
- Deliver verdict: ACCEPT or BLOCKED

**CC Parallel Audit:** Not needed for Round 3 — this is self-verification.

**Deliverable:** Verdict. If ACCEPT → proceed to Task 3. If BLOCKED → write fix directive, loop back.

---

### Task 3: Triage CC's Unauthorized Session 5/6 Work

**What:** Decide whether to KEEP or REJECT CC's unauthorized Session 5/6 implementation.

**Options:**
- **Option A (Review it):** Treat it as a completed Session 5+6 delivery. Run the full 3-pass review protocol on it. Pro: saves ~2 sessions of build time. Con: CC designed it without architect input — design quality uncertain.
- **Option B (Reject and redo):** `git revert` the unauthorized files, write a proper Session 5 NEXT.md with architect design decisions, have CC re-implement. Pro: proper quality pipeline. Con: throws away working code.
- **Option C (Hybrid):** Keep the code as a reference/draft, but write the Session 5 NEXT.md anyway and have CC align the existing code to the architect's design. Pro: saves most build time, gets architect design. Con: diffing "what CC did" vs "what architect wants" is complex.

**Decision framework:** Read the unauthorized files. If the design decisions align with the SPEC and the architect's Session 5 NEXT.md (backed up at `reference/archive/sessions/NEXT_session5_original.md`), go with Option A. If the design diverges, go with Option C.

**CC Parallel Audit Prompt (if Option A):**
```
Read engines/excerpting/src/phase3_validation.py, engines/excerpting/src/phase3_orchestrator.py, engines/excerpting/src/writer.py, and engines/excerpting/src/pipeline.py in full.

For each module:
1. Does it implement the SPEC section it claims to? Cross-reference against engines/excerpting/SPEC.md §7.4 (validation) and §3 (output format).
2. For every model_copy or model_validate call: construct the input, apply the operation, and verify the result survives ExcerptRecord.model_validate(result.model_dump()).
3. For every error code emitted: verify it matches the SPEC §8.1 error code table.
4. Does the orchestrator chain phases correctly? What happens if Phase 3.2 (enrichment) fails for a chunk but Phase 3.3 (consensus) still runs? Is this handled?
5. Does the writer produce correct JSONL? One object per line, ensure_ascii=False, Pydantic model_dump(mode="json")?
6. Does V-P3-7 (gate queue integrity) read back the file after writing? SPEC requires paranoid verification.

Write findings. Do NOT fix anything.
```

**Deliverable:** Triage decision + review findings (if Option A).

---

### Task 4: Session 5/6 Review (if keeping CC's work)

**What:** Full 3-pass review of validation, writer, orchestrator, integration tests.

**Protocol:** Same as Tasks 1-2. Three passes across separate responses.

**CC Parallel Audit:** Use the prompt from Task 3 (already run at that point).

---

### Task 5: Excerpting Engine Completion Assessment

**What:** After all phases reviewed, assess whether the excerpting engine is ready for the owner's 30-book evaluation probe.

**Check:**
- All SPEC sections implemented: §4 (P1), §5 (P2), §7.1-7.4 (P3), §3 (output)
- All error codes tested
- All I-ER invariants tested
- Cross-engine contracts verified
- Tier 1 LLM trustworthiness defenses: decide defer vs implement

---

## Dual-Reviewer Pattern (Standard for All Future Work)

Every review and analysis should use TWO independent reviewers:

1. **Claude Chat (Architect):** Structural analysis, SPEC traces, design judgment, multi-angle thinking
2. **Claude Code (Auditor):** Adversarial input construction, model_copy roundtrip testing, tautological test detection, branch coverage

**Why this works:** This session proved the pattern. Architect found F-4 (CRITICAL attribution bug) that CC confirmed. CC found CC-F3 (HIGH crash on reachable path) that architect missed. CC found CC-F5 (dead code) that corrected architect's false F-1. Neither reviewer alone would have caught everything.

**How to implement:**
- Architect does their analysis first
- Owner gives CC the audit prompt (provided by architect for each task)
- Architect cross-references CC's findings against their own
- Final corrected finding list combines both

**Prompt template for CC audits:**
```
Read [files] in full. For each [function/fix/module]:
1. [Specific adversarial check relevant to the task]
2. For every model_copy: construct input → apply → model_validate roundtrip
3. For every test: "what broken implementation would still pass?"
4. [Task-specific traces]
Write findings. Do NOT fix anything.
```

---

## Files to Read at Session Start

| File | Why |
|------|-----|
| This handoff document | Current state and task queue |
| `reference/protocols/REVIEW_PROTOCOL.md` | Review rules |
| `reference/protocols/QUALITY_AXIOM.md` | Governing principle |
| `reference/archive/sessions/reviews/review_excerpting_session4.md` | Round 1 checklist (to be completed in Round 2+3) |
| `engines/excerpting/SPEC.md` §7.2-§7.3 | SPEC for enrichment + consensus |
| `NEXT.md` | Current state (CC updated after fixes) |
| `git log --oneline -5` | Recent commits |
| `git diff 4988551b..78a46587 -- engines/excerpting/src/phase3_consensus.py engines/excerpting/src/phase3_enrichment.py` | The 9 fix diffs (review scope) |

---

## Lessons Learned (for Memory Updates)

1. **CC adversarial audit is mandatory for every review.** The two-reviewer pattern caught bugs neither reviewer found alone. Formalize this in REVIEW_PROTOCOL.md.
2. **Reachability check for adversarial inputs.** Before declaring a crash finding, trace backward to verify the pipeline can actually produce the triggering input. Architect's F-1 was a false alarm on dead code.
3. **model_copy skips validators.** Every model_copy must be followed by a mental (or actual) model_validate check. This is the #1 source of silent invariant violations in Pydantic v2.
4. **CC scope creep is real.** CC implemented 3 sessions of work in one push. The overnight/autonomous system needs guardrails — perhaps a line-count limit or a "stop after NEXT.md scope" instruction.
