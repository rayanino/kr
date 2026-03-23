# CC Review Checklist — Excerpting Session 2: Phase 2 LLM Classification + Grouping

> **This file is the review artifact.** Fill every checkbox, commit this file, THEN deliver the verdict.  
> An unfilled checklist = an incomplete review. Do NOT deliver a verdict without committing this file.  
> **REVIEW_PROTOCOL.md is the authority — NOT the kr-reviewing-cc-output skill's verdict template.**

## Pre-review
- [x] Repo pulled, commit diff read
- [x] NEXT.md re-read — what was requested?
- [x] REVIEW_PROTOCOL.md read fresh
- [x] QUALITY_AXIOM.md read fresh

## Pass 1: Structural
- [x] Every CC-modified file opened and read **in full** (not truncated) — list files:
  - [x] `phase2_classify.py` — 9 functions (5 public, 4 internal) verified by `grep -n "^def " phase2_classify.py` (9 lines)
  - [x] `phase2_group.py` — 4 functions (3 public, 1 internal) verified by `grep -n "^def " phase2_group.py` (4 lines)
  - [x] `tests/conftest.py` — new factories: `_make_mock_instructor_client`, `_make_classification_result` (verified)
  - [x] `tests/test_phase2_normalize.py` — 27 test functions (verified: `grep -c "def test_"` = 27)
  - [x] `tests/test_phase2_classify.py` — 18 test functions (verified: `grep -c "def test_"` = 18)
  - [x] `tests/test_phase2_group.py` — 21 test functions (verified: `grep -c "def test_"` = 21)
  - [x] `tests/test_phase2_integration.py` — 2 test functions (verified: `grep -c "def test_"` = 2)
  - **RULE 7 check:** `phase2_classify.py` was truncated at line 229; truncated range [229-260] was requested and read.
  - **RULE 7 check:** `test_phase2_group.py` was truncated at line 217; truncated range [217-230] was requested and read.
- [x] All tests run: `147 passed, 2 skipped, 0 failed`
- [x] Normalization regression: `503 passed, 14 skipped, 0 failed`
- [x] SPEC cross-reference: every function traces to a § rule
  - `_compute_classify_max_tokens` → §5.5.1 ✅
  - `_build_token_char_map` → §5.4.1 Step 1 ✅
  - `_char_to_token_index` → §5.4.1 Step 2c ✅
  - `_strip_text` → §5.4.1 Step 2d/d2 ✅
  - `_find_snippet_position` → §5.4.1 Step 2a-e ✅
  - `normalize_offsets` → §5.4.1 Steps 1-3 ✅
  - `verify_segments` → §5.4.2 (delegates to contracts.py) ✅
  - `classify_chunk` → §5.2 ✅
  - `run_phase2a` → §5.1 Steps 1-3, §5.5.2 ✅
  - `_build_segment_summary` → §5.3.3 ✅
  - `group_chunk` → §5.3 ✅
  - `verify_units` → §5.4.3, V-P2-14, V-P2-15 ✅
  - `run_phase2b` → §5.1 Steps 4-5, §5.5.2 ✅
- [x] Prompts match SPEC: CLASSIFY_SYSTEM_PROMPT = §5.2.2 (programmatic comparison: EXACT MATCH)
- [x] Prompts match SPEC: GROUP_SYSTEM_PROMPT = §5.3.2 (programmatic comparison: EXACT MATCH)
- [x] Error codes all exist in contracts: EX_A_012, EX_C_001–005 ✅
- [x] DD-S2-1 (prompts verbatim) ✅
- [x] DD-S2-2 (client from caller) ✅
- [x] DD-S2-3 (new objects, no mutation) ✅
- [x] DD-S2-5 (error feedback in user message) ✅
- [x] DD-S2-6 (standard logging) ✅
- [x] DD-S2-7 (mock testing) ✅
- [x] DD-S2-8 (max_retries=0) ✅ but **F-1: ValidationError feedback violates DD-S2-8**
- [x] No direct API imports: `grep -r "import anthropic" engines/excerpting/src/` → empty ✅
- [x] **Cross-engine boundary check:**
  - [x] contracts.py NOT modified → no cross-engine impact
  - Modified types: `None`
  - Consumers checked: `N/A — no contract changes`

## Pass 2: Adversarial
- [x] 14 probing scripts run with constructed inputs — findings:
  - Probe A: Whitespace fallback with search_start > 0 → PASS
  - Probe A2: Diacritic fallback with search_start > 0 → PASS (EX-A-012 warning emitted)
  - Probe C: Full SPEC §5.4.1 algorithm step-by-step trace → PASS (all 4 steps match)
  - Probe D: Duplicate word disambiguation → PASS (left-to-right correct)
  - Probe E: verify_units V-P2-14 derivation → PASS
  - Probe E2: Out-of-range segment_indices → **F-2 FOUND** (IndexError caught by wrong handler)
  - Probe F: User message format vs SPEC §5.3.3 → EXACT MATCH
  - Probe G: ValidationError inheritance chain → CORRECT (except ordering valid)
  - Probe H: Retry count → PASS (exactly 3 attempts)
  - Probe I: _char_to_token_index boundary behavior → CORRECT
  - Probe J: 5-segment realistic Arabic text → PASS
  - Probe K: ExcerptingConfig defaults vs SPEC §5.5.3 → ALL MATCH
  - Probe L: ZWNJ character handling → PASS
  - Probe M: total_tokens vs word_count distinction → CORRECT
- [x] Fixture spot-checks: N/A — Phase 2 requires LLM calls, not deterministic fixture processing. The offset normalization algorithm (the testable part) was probed with constructed Arabic texts in Probes A/A2/C/D/J.
- [x] Cross-engine data flow: N/A — no contract changes
- [x] **SPEC concrete example trace (RULE 5):** §5.4.1 has no single worked example but has a detailed algorithm. Traced all 4 steps through implementation in Probe C. No divergences.
  - §5.5.1 MAX_TOKENS thresholds: verified programmatically ✅
  - §5.5.3 API config defaults: verified programmatically ✅

## Pass 3: Self-verification (RULES 6-7)
- [x] Every factual claim in Passes 1-2 verified against code with tool calls:
  - [x] "147 passed, 2 skipped" — re-run pytest: confirmed
  - [x] "27 test functions in normalize" — re-run grep: confirmed
  - [x] "contracts.py not modified" — re-run git diff: confirmed
  - [x] "DD-S2-8 says NOT to append" — re-read handoff text: confirmed
  - [x] "F-1 code appends error_feedback" — re-read lines 421-422 and 324-326: confirmed
  - [x] "F-2 IndexError caught by wrong handler" — re-read line 206: confirmed
  - [x] "No direct API imports" — re-run grep: confirmed
- [x] Check for rationalization patterns:
  - F-1 and F-2: not rationalized — both are clear violations with trivial fixes
  - Telemetry token counts: noted as informational gap (DD-S2-6 handoff omitted them, zero epistemic impact). Not elevated to finding — would be blocking manufacture.
- [x] Review Notes drafted — each Note verified against code before writing

## Notes

**N-1 (Informational):** SPEC §5.5.4 requires logging input/output token counts. Code omits these. The handoff DD-S2-6 also omitted them. Zero epistemic impact (telemetry only). Not a finding — document as enhancement for a future session if instructor client exposes usage metadata.

**N-2 (Positive):** The offset normalization algorithm is well-implemented. The `_strip_text` function with position mapping is clean and correct. The three-level matching cascade (exact → whitespace → diacritic) with position back-mapping is the core innovation, and it handles the search_start translation correctly in both fallback paths. 14 adversarial probes found zero bugs in the normalization algorithm.

**N-3 (Positive):** V-P2-15 auto-repair correctly uses `model_construct()` in tests to bypass Pydantic validators, addressing the architect's concern about reachability. CC's comment at line 229-231 shows awareness of the defense-in-depth rationale.

## Findings

| # | File | Finding | Fix | Fixed? |
|---|------|---------|-----|--------|
| F-1 | `phase2_classify.py:421` + `phase2_group.py:324` | DD-S2-8 violation: ValidationError handlers set `error_feedback` to include the error message. DD-S2-8 explicitly says "NOT appended to the next attempt's prompt." | Set `error_feedback = None` in both `except ValidationError` blocks. | [ ] |
| F-2 | `phase2_group.py:206` | `verify_units` accesses `segments[unit.segment_indices[0]]` without bounds checking. Out-of-range indices from LLM raise `IndexError` caught by generic `except Exception` handler → wrong error code (EX_C_002 vs EX_C_005), unnecessary backoff, no LLM feedback. | Wrap V-P2-14 derivation in `try: ... except IndexError: raise ValueError(f"V-P2-14: segment index {unit.segment_indices[0]} out of range for {len(segments)} segments")`. | [ ] |

## Fixes committed
- [ ] ALL findings above have `Fixed? [x]`
- [ ] Fix commits pushed to repo
- [ ] Tests re-run after fixes: `[N] passed`

## Verdict

**Verdict: BLOCKED**

Two findings (F-1, F-2) require fixes before ACCEPT.

## Build metrics (cumulative)

```
Implementation: ~1620 lines (+766 this session: 476 classify + 375 group - 37 stubs removed)
Tests: 147 passing (+70 this session), 2 skipped (integration, gated)
SPEC sections implemented: §5.2, §5.3, §5.4.1, §5.4.2, §5.4.3, §5.5.1, §5.5.2
SPEC sections remaining: §5.6 (Phase 3 enrichment), §5.7 (Phase 3 consensus)
Known limitations: N/A (no new limitations identified)
```
