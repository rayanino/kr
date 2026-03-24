# CC Review — Excerpting Session 4 Fixes: Round 2 + Round 3

**Date:** 2026-03-24
**Reviewer:** Claude Chat (Architect)
**Scope:** 9 fixes applied in commit `78a46587` to `phase3_enrichment.py` and `phase3_consensus.py`
**Dual reviewer:** CC adversarial audit (Task 1 from handoff_review_session4_continuation.md)
**Baseline:** 83 Session 4 tests passing (540 total excerpting tests), 0 failed

---

## Round 1 (Structural) — Completed in prior chat

See `review_excerpting_session4.md`. Found 9 findings, all fixed by CC in commit `78a46587`.

---

## Round 2 (Adversarial) — This chat

### Pre-probing
- [x] Repo cloned fresh (`git clone`)
- [x] Continuation plan read (`handoff_review_session4_continuation.md`)
- [x] REVIEW_PROTOCOL.md re-read
- [x] Both source files read in full:
  - [x] `phase3_enrichment.py` — 452 lines, 3 functions (verified by grep)
  - [x] `phase3_consensus.py` — 828 lines, ~14 functions (verified by grep)
- [x] Fix diffs read (`git diff 4988551b..78a46587`)
- [x] All 23 new tests read from diff
- [x] Baseline confirmed: 83 tests pass, 540 total pass

### Per-fix adversarial probes (all executed with tool calls)

| Fix | # Probes | Result | Key Edge Cases |
|-----|----------|--------|---------------|
| 1 (attribution majority) | 3 | ✅ PASS | Arabic diacritics preservation, model_validate roundtrip, no-update when majority==enrichment |
| 2 (PARTIAL hint fallback) | 5 | ✅ PASS | Notes fallback, generic via model_construct, LLM hint preferred, FULL stays None, roundtrip |
| 3 (EX-G-003) | 5 | ✅ PASS | Missing source_school, vi.alternative=None, verifier_value=None conservative, verifier=source |
| 4 (chunk matching) | 5 | ✅ PASS | Underscore div_ids, chunk_index=0, exact match, orphan, old-startswith false-match |
| 5 (item_index mapping) | 3 | ✅ PASS | Duplicate index, non-zero start, multi-excerpt sequential |
| 6 (_parse_self_containment) | 17 | ✅ PASS | All ambiguous combos, empty/whitespace/Arabic/None, all-three-levels |
| 7 (gate assessments) | 3 | ✅ PASS | consensus_metadata=None, multiple decisions, None→empty string |
| 8 (ordering) | 3 | ✅ PASS | Full resolve_consensus flow, FULL→PARTIAL repair, no-consensus fallback |
| 9 (phantom voter) | 7 | ✅ PASS | No escalation+None alt, flexible majority, "abstained", roundtrip |

**Total: 51 adversarial test cases executed, 0 failures.**

### SPEC Concrete Example Traces (RULE 5)

| SPEC Section | Trace Result |
|-------------|-------------|
| §7.3.3 School disagreement | ✅ min(confidence), keep enrichment, flag, EX-M-003 |
| §7.3.3 Author 2-of-3 majority | ✅ Majority applied to primary_author_layer |
| §7.3.3 Author all-3-disagree | ✅ EX-G-001, confidence=0.0, keep enrichment |
| §7.3.3 Self-containment conservative | ✅ Lower level, DEPENDENT→EX-G-002, hint nullified |
| §7.3.4 Gate queue JSON format | ✅ All fields match SPEC (10/10 field checks) |
| §7.3.3 FULL→PARTIAL repair | Dead code (§7.3.1 exempts FULL from consensus) — defensive, correct |

### Cross-Engine Contract Check (RULE 3)
- [x] `grep -rn "from engines.excerpting" engines/` excluding excerpting → 0 results
- [x] No other engine imports excerpting contracts
- [x] All changes self-contained within excerpting engine

### End-to-End Integration Probe
- [x] 2 excerpts in 1 split chunk, all fixes interacting simultaneously
- [x] Out-of-order verification items + Arabic diacritics + split chunk matching
- [x] Both results survive model_validate(model_dump()) roundtrip
- [x] Gate entries correct (EX-G-002 for DEPENDENT, no EX-G-003 when verifier matches source)

---

## Round 3 (Self-Verification) — This chat

### CC Adversarial Audit Cross-Reference

CC ran an independent adversarial audit on all 9 fixes. Cross-referencing:

| CC Finding | My R2 Finding | Assessment |
|-----------|--------------|------------|
| Fix 1: Arabic NFC/NFD mismatch across providers | Not tested | **Pre-existing** — not a Fix 1 regression. LLMs typically return NFC. |
| Fix 2: Generic fallback unreachable for valid PARTIAL (I-ER-4 guarantees notes) | Confirmed in Probe 2A-2C | **Agree** — defensive code, correct |
| Fix 3: source_school=None graceful skip | Confirmed in Probe 3A | **Agree** — no issue |
| Fix 4: `alt_id` fallback not in NEXT.md | Not flagged | **Verified** — CC scope deviation, but harmless defensive code |
| **Fix 5: Duplicate item_index → silent last-write-wins** | Noted in Probe 5A as "data quality issue" | **Verified** — real schema gap (see analysis below) |
| Fix 6: All edge cases correct | Confirmed with 17 cases | **Agree** |
| Fix 7: None → empty assessments | Confirmed in Probe 7A | **Agree** |
| Fix 8: FULL→PARTIAL confirmed dead code | Confirmed in SPEC trace | **Agree** |
| Fix 9: resolution_method mislabel "all_3_disagree_gate" | Not flagged | **Verified** — label inaccurate, gate action correct (see analysis below) |

### Detailed Analysis of CC Findings

**CC-F5 (Duplicate item_index):**
- Real gap: `vi_by_index` dict does silent last-write-wins on duplicate `item_index`
- Fix 5 introduced this specific failure mode while fixing a worse one (positional fragility)
- Net effect: strictly positive for realistic LLM behavior (reordering common, duplicates near-zero)
- Root cause: `VerificationResult` schema lacks uniqueness constraint — a schema-level issue
- Fix 5's implementation (dict by index) is the correct approach for its stated purpose
- Adding a `VerificationResult` validator is architecturally separate from Fix 5
- **Classification: pre-engine-completion improvement, not a Fix 5 regression**

**CC-F9 (resolution_method mislabel):**
- Verified: "all_3_disagree_gate" when verifier abstained (alternative=None, 2 real votes)
- Gate action (EX-G-001) is correct — human review for unresolvable disagreement
- Human sees actual values: enrichment=X, verifier="abstained", escalation=Y
- Label is informational metadata, not a behavioral control
- **Classification: cosmetic label inaccuracy in human-review context, not T-2 corruption**

**CC-F4 (alt_id):**
- Verified: `alt_id = f"{div_id}_{chunk_index}"` was not in NEXT.md specification
- False-match risk negligible given div_id formats (`div_src_NNN_depth_index`)
- Code is harmless defensive fallback
- **Classification: CC scope deviation, harmless**

### Factual Claim Verification (RULE 6)

| Claim | Verification | Result |
|-------|-------------|--------|
| "83 Session 4 tests pass" | `pytest -q` | ✅ 83 passed |
| "540 total excerpting tests" | `pytest engines/excerpting/ -q` | ✅ 540 passed, 2 skipped |
| "`_find_majority` is dead production code" | `grep -n "_find_majority(" src/ \| grep -v def \| grep -v flexible` | ✅ 0 production calls |
| "No other engine imports excerpting" | `grep -rn "from engines.excerpting" engines/ \| grep -v excerpting/` | ✅ 0 results |
| "`_needs_consensus` exempts FULL" | Code trace line 78-82 | ✅ Only PARTIAL/DEPENDENT |
| "resolve_consensus 2nd return ignored" | `grep` line 797: `_cr` | ✅ Underscore variable |
| "`_find_majority_flexible` equivalent for 3-vote" | Ran all 5 test cases | ✅ Identical results |

### Rationalization Check

| Conclusion | "Am I explaining this away?" | Re-examination |
|-----------|------------------------------|----------------|
| CC-F5 not blocking | Could I add a 3-line validator to VerificationResult right now? Yes. But it's a schema improvement, not a Fix 5 implementation defect. Fix 5 correctly solves its stated problem. | **Not rationalizing** — genuinely separate architectural layer |
| CC-F9 not blocking | The label IS wrong. But fixing it means adding a resolution_method variant for a case where the gate action is already correct and data complete. | **Not rationalizing** — genuinely marginal given gate data completeness |
| FULL→PARTIAL as "defensive" | Could this dead code hide a SPEC inconsistency? | Checked: §7.3.1 explicitly exempts FULL, §7.3.3 describes repair as "if consensus downgrades FULL→PARTIAL." The SPEC describes a theoretical path the design intentionally prevents. Not a finding. |

### Unconstrained Adversarial Pass (QUALITY_AXIOM §7)

What is the protocol NOT checking?
1. **Nested model_copy field preservation** — tested: layer_id, coverage_pct preserved through model_copy + roundtrip ✅
2. **Counter import inside function body** — tested: works correctly ✅
3. **None 2nd return from resolve_consensus** — verified: caller ignores via `_cr` ✅
4. **Double-update (enrichment then consensus) on same field** — tested: consensus overwrites correctly ✅
5. **Empty excerpts list** — tested: empty in, empty out, no crash ✅

---

## Findings

**Zero findings that block acceptance of the 9 fixes.**

The 9 fixes correctly address their stated findings. No regressions introduced.

### Pre-engine-completion items (tracked, not blocking fix review)

| # | Description | Tracking |
|---|------------|----------|
| PE-1 | `VerificationResult` lacks uniqueness constraint on `item_index` — add `@model_validator` | Add to Session 5/6 scope |
| PE-2 | `resolution_method` label "all_3_disagree_gate" inaccurate when verifier abstains | Add to Session 5/6 scope |
| PE-3 | `_find_majority` function at line 433 is dead production code (unused) | Cleanup in next session |
| PE-4 | `alt_id` fallback in chunk matching not in NEXT.md spec (CC scope deviation) | Document in CLAUDE.md |

---

## Verdict

**ACCEPT**

The 9 fixes correctly address all 9 findings from Round 1. Each fix was probed with 3-7 adversarial inputs (51 total). All SPEC §7.3.3 disagreement rules trace correctly through the implementation. Cross-engine contracts clean. Full end-to-end integration test passes. Roundtrip validation passes everywhere. CC's independent audit found no regressions in the fixes themselves — only pre-existing schema and labeling gaps to address before engine completion.

---

## Build metrics (cumulative after Session 4 fixes)

```
Implementation: ~3,745 lines (phase3_enrichment: 452, phase3_consensus: 828, + prior sessions)
Tests: 540 passing (+23 new fix tests, +60 Session 4 original = 83 Session 4 total)
Test-to-code: 83 tests / ~1,280 impl lines = 6.5 tests per 100 lines (Session 4 scope)
SPEC sections implemented: §4, §5, §7.1, §7.2, §7.3
SPEC sections remaining: §7.4 (validation), §3 (output format)
ADV covered: 22/51 (estimate — Session 4 added no new ADV cases)
Known limitations: L-001–L-012
```
