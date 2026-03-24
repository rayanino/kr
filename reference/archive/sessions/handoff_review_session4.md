# Architect Handoff — Excerpting Session 4 Review

**Date:** 2026-03-24
**From:** Claude Chat (Architect), Session 3 review chat
**To:** Claude Chat (Architect), next session
**Task:** Full 3-pass review of Session 4 (Phase 3 LLM enrichment + consensus verification)

---

## Critical Context: How Session 4 Was Built

Session 4 was **implemented autonomously by Claude Code without an architect-prepared handoff.** The overnight system ran CC for Session 3 review/hardening tasks (legitimate). Then CC implemented Session 4 (§7.2 enrichment + §7.3 consensus) on its own — there was no architect-designed NEXT.md for Session 4.

This means:
1. **No architect-designed design decisions** — CC read the SPEC stubs and improvised
2. **No architect SPEC example traces** — the mandatory Step 5 from HANDOFF_PROTOCOL.md was skipped
3. **No architect empirical verification** on real fixtures
4. **No Tier 1 LLM trustworthiness defenses were integrated** — the defense doc (`engines/excerpting/docs/llm_trustworthiness_defenses.md`) mandated 5 items for Session 4; zero were implemented

**This is NOT automatically a problem.** CC is Opus 4.6 reading a comprehensive SPEC. The implementation might be excellent. But it was built without the quality gate that catches design-level issues, and the reviewer must compensate by being extra thorough on architecture and design choices — not just correctness.

---

## What Was Delivered

**Commit:** `4a7f71e9` (merged into master at HEAD `03ae2279`)
**Commit message:** "feat: implement Phase 3 LLM enrichment + consensus verification (§7.2–7.3)"

### Files Modified

| File | Lines | What |
|------|-------|------|
| `engines/excerpting/src/phase3_enrichment.py` | 442 (was ~56 stubs) | LLM enrichment: prompt construction, Instructor call, response merging |
| `engines/excerpting/src/phase3_consensus.py` | 767 (was ~53 stubs) | Consensus verification: 2nd-model call, field comparison, human gates |
| `engines/excerpting/tests/test_phase3_enrichment.py` | 543 (new file) | 27 test functions |
| `engines/excerpting/tests/test_phase3_consensus.py` | 590 (new file) | 33 test functions |
| `engines/excerpting/tests/test_phase3_deterministic.py` | +856 | Additional edge case tests (from overnight, folded into Session 4 commit) |
| `engines/excerpting/CLAUDE.md` | +11 | Build table update |
| `NEXT.md` | rewritten | CC wrote Session 5 NEXT.md (§7.4 validation + writer) |

### Test Counts

- 437 total excerpting tests passing (was 184 pre-overnight)
- 27 enrichment tests, 33 consensus tests
- 0 failures, 2 skipped (Phase 2 integration requiring real LLM)

---

## Governing Documents (Read First)

| Document | What to check | Why |
|----------|---------------|-----|
| `reference/protocols/REVIEW_PROTOCOL.md` | Full 3-pass protocol | Authority on review structure |
| `reference/protocols/QUALITY_AXIOM.md` | Sole quality gate principle | Especially critical since CC self-designed |
| `engines/excerpting/SPEC.md` §7.2 (lines 1519–1745) | LLM enrichment algorithm, prompt, response schema | Primary authority for enrichment review |
| `engines/excerpting/SPEC.md` §7.3 (lines 1746–1892) | Consensus protocol, field comparison, gate triggers | Primary authority for consensus review |
| `engines/excerpting/docs/llm_trustworthiness_defenses.md` | Tier 1 defense integration plan | **CRITICAL: 5 items were mandated for Session 4; 0 were implemented** |
| `engines/excerpting/contracts.py` lines 580–660 | `EnrichmentResult`, `ConsensusRecord`, LLM response schemas | Structural target shapes |
| `engines/excerpting/contracts.py` lines 675–740 | Error codes EX-M-002, EX-M-003, EX-G-001 through EX-G-005 | Session 4 should emit these |

---

## Red Flags to Investigate

### 1. Missing Tier 1 LLM Trustworthiness Defenses

The defense doc (`engines/excerpting/docs/llm_trustworthiness_defenses.md`) Integration Points table mandated for Session 4:

| Defense | What | Status |
|---------|------|--------|
| **1B** — School cross-check | Compare LLM `school` against source metadata | **NOT IMPLEMENTED** (0 grep hits) |
| **1C** — Quran canonical lookup | Download `data/quran_uthmani.json`, match against evidence_refs | **NOT IMPLEMENTED** (file doesn't exist) |
| **2A** — Targeted self-containment consensus question | Ask 2nd model specifically about dangling references in FULL units | **NOT IMPLEMENTED** (0 grep hits) |

Additionally, 3 empirical scans were supposed to run during Session 4 handoff preparation:
- Back-reference pattern scan (Defense 1A feasibility)
- Quran text coverage scan
- Evidence-classification overlap scan

**None of these ran.** The reviewer must decide: are these deferred to Session 5, or do they block Session 4 acceptance?

### 2. LLM Call Architecture — OpenRouter Routing

All LLM calls must go through OpenRouter only (memory mandate). Verify:
- `grep -rn "openrouter\|OpenRouter\|OPENROUTER" engines/excerpting/src/phase3_enrichment.py engines/excerpting/src/phase3_consensus.py`
- No direct Anthropic/OpenAI API calls
- Instructor integration pattern: `instructor.from_openai(openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=KEY))`

### 3. Consensus Provider Independence

§7.3 requires the consensus model to be a **different provider** from the primary enrichment model. This prevents same-model bias (failure F4a). Verify:
- What model does enrichment use?
- What model does consensus use?
- Is the provider actually different, or just a different model from the same provider?

### 4. Human Gate Triggers

§7.3 defines 5 gate trigger conditions (EX-G-001 through EX-G-005). Verify:
- All 5 are implemented
- Gate entries include enough context for the owner to resolve them
- EX-M-008 (gate write failure) halts processing

### 5. Decontextualization Defense (T-2)

The excerpting corruption threat doc identified F2a (decontextualization) as CRITICAL severity with no deterministic defense. The only defense is the consensus question and the human gate. Verify:
- Does the consensus prompt specifically ask about decontextualization?
- Does the grouping self-containment assessment flow through correctly?
- Are PARTIAL/DEPENDENT units flagged for human review?

### 6. Test Coverage vs Implementation

CC wrote its own tests for its own code (the CC self-review anti-pattern at the test level). The tests may be structurally correct but miss the cases the implementation handles wrong. The reviewer must construct independent adversarial probes, not rely on CC's tests.

---

## Session 3 Review Outcome (For Context)

**Verdict: ACCEPT** (after fix)

Session 3 (Phase 3 deterministic, §7.1) was reviewed with a full 3-pass protocol across 3 responses. One finding was identified and fixed:

- **F-1 (FIXED at `03ae2279`):** F-DET-9 used type-class matching for primary layer exclusion instead of identity matching. Changed line 480 to match on both `layer_type.value` AND `author_canonical_id`.

Additionally, the overnight CC review found and fixed:
- **H-1 (FIXED at `6ddf802f`):** Missing adjacency check in layer split-point merging. Added `and layer.start == merged[-1][2]` guard.

Both fixes have tests. 437 tests pass.

### Medium Findings Tracked (NOT blocking)

- M-1: DEPENDENT units get unnecessary `llm_enrichment_failed` flag (functionally inert)
- M-2: Test fixture violates I-AC-2 (1-char gap between layers — test data only)
- M-3: Magic sentinel `char_end + 1_000_000` in page range (correct but fragile)
- M-4: SPEC LA-2/LA-3 condition (b) unreachable (design question)
- M-5: Test name misleading
- M-6: Unused `primary_text` parameter in `filter_relevant_footnotes`
- H-2: Interleaved same-type layers inflate layer count (conservative outcome, not corruption)

These are NOT blocking — they produce no epistemic impact and were deliberately not elevated to findings.

---

## Repo State

```
HEAD: 03ae2279 (fix: F-DET-9 identity matching)
Branch: master
Tests: 437 passed, 2 skipped, 0 failed
NEXT.md: Points at Session 5 (§7.4 validation + writer) — CC wrote this
```

### Key commits in scope for Session 4 review:

```
03ae2279 fix: F-DET-9 identity matching — exclude primary (type+author), not entire type  ← Session 3 fix (ACCEPTED)
4a7f71e9 feat: implement Phase 3 LLM enrichment + consensus verification (§7.2–7.3)       ← SESSION 4 (UNREVIEWED)
789d95d9 overnight: 76 edge case hardening tests for Phase 2 LLM classification + grouping ← overnight (harmless)
8eb0eb19 overnight: 40 edge case hardening tests for Phase 1 deterministic assembly         ← overnight (harmless)
6ddf802f overnight: 22 adversarial tests for Phase 3.1 deterministic functions              ← overnight (includes H-1 fix)
```

The diff to review is: `git diff 789d95d9..4a7f71e9` (Session 4 delivery only, excluding overnight hardening)

---

## Review Protocol

Follow `reference/protocols/REVIEW_PROTOCOL.md` — 3 passes, separate responses.

**Round 1 (Structural):**
1. Pull repo. Read diff (`git diff 789d95d9..4a7f71e9`).
2. Read SPEC §7.2 and §7.3 in full.
3. Read `phase3_enrichment.py` and `phase3_consensus.py` in full.
4. Read all test files.
5. Run full test suite.
6. Cross-engine boundary check (any contract changes?).
7. **Check LLM trustworthiness defenses doc** — which defenses were supposed to be in Session 4?
8. Produce findings. End response.

**Round 2 (Adversarial):**
1. Construct mock LLM responses and trace through enrichment pipeline.
2. Construct consensus disagreement scenarios — verify gate triggers.
3. **SPEC concrete example trace** for §7.2 and §7.3 worked examples.
4. Test with malformed LLM output — does it fail safely?
5. Verify error codes match SPEC §8.
6. Verify OpenRouter routing.
7. Produce findings. End response.

**Round 3 (Self-verification + Verdict):**
1. Verify every claim from Rounds 1-2.
2. Check for rationalization.
3. **Explicit decision on Tier 1 defenses:** Block or defer with documented rationale.
4. Fill checklist. Commit. Deliver verdict.

---

## Build Metrics (Current)

```
Total excerpting implementation lines: ~3,745 (P1: ~900, P2: ~1,000, P3.1: 637, P3.2: 442, P3.3: 767)
Total excerpting test count: 437 passed
SPEC sections complete: §4 (P1), §5 (P2), §7.1 (P3 deterministic), §7.2 (P3 enrichment), §7.3 (P3 consensus)
SPEC sections remaining: §7.4 (validation), §3 (output writer)
Adversarial cases: overnight added ~138 edge case tests across all phases
```

---

## Session Start Checklist (For Next Chat)

```
[ ] Clone repo: git clone https://{token}@github.com/rayanino/kr.git
[ ] Read this handoff document
[ ] Read REVIEW_PROTOCOL.md
[ ] Read QUALITY_AXIOM.md
[ ] Read SPEC §7.2 (lines 1519-1745)
[ ] Read SPEC §7.3 (lines 1746-1892)
[ ] Read llm_trustworthiness_defenses.md
[ ] git log --oneline -10
[ ] git diff 789d95d9..4a7f71e9 --stat
[ ] Run pytest: python -m pytest engines/excerpting/tests/ -v --tb=short
[ ] Begin Round 1
```
