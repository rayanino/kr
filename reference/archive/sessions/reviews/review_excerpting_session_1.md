# CC Review Checklist — Excerpting Engine Session 1: Phase 1 Deterministic Preprocessing

> Reviewed by: Claude Chat (Architect)
> CC commit: 1ae4a991
> Previous commit: 69ec1faa
> Date: March 2026

## Pre-review
- [x] Repo pulled, commit diff read
- [x] NEXT.md re-read — what was requested?

## Pass 1: Structural
- [x] Every CC-modified file opened and read **in full** (not truncated) — list files:
  - [x] `engines/excerpting/src/phase1_assembly.py` — 22 functions (verified by `grep -c "^def \|^    def "`)
  - [x] `engines/excerpting/tests/conftest.py` — 8 factories total (4 original + 4 new)
  - [x] `engines/excerpting/tests/test_phase1_tree_walk.py` — 19 tests
  - [x] `engines/excerpting/tests/test_phase1_assembly.py` — 17 tests
  - [x] `engines/excerpting/tests/test_phase1_merge.py` — 8 tests
  - [x] `engines/excerpting/tests/test_phase1_split.py` — 9 tests
  - [x] `engines/excerpting/tests/test_phase1_metadata.py` — 11 tests
  - [x] `engines/excerpting/tests/test_phase1_layers.py` — 6 tests
  - [x] `engines/excerpting/tests/test_phase1_alignment.py` — 5 tests
  - [x] `engines/excerpting/tests/test_phase1_validation.py` — 6 tests (4 validation + 2 end-to-end)
  - **RULE 7 check:** phase1_assembly.py was truncated at line 236. Truncated range [236-1280] and [1100-1280] were requested and read before proceeding.
- [x] All tests run: 81 passed, 0 skipped, 0 failed (excerpting); 503 passed, 14 skipped (normalization regression)
- [x] SPEC cross-reference: every function traces to a § rule (§4.2–§4.9)
- [x] **Cross-engine boundary check:**
  - [x] `grep -rn` for StructuralMarkers, ContentUnit, DivisionNode, TextLayerSegment across all engines
  - [x] `python tools/check_cross_engine_contracts.py` → result: PASS
  - [x] Each downstream consumer verified to accept the new shape
  - Modified types: none (contracts.py untouched as required)
  - Consumers checked: normalization contracts StructuralMarkers.heading_detected (line 192), ContentUnit.structural_markers (line 449)

## Pass 2: Adversarial
- [x] 3+ probing scripts run with constructed inputs — findings:
  - Probe 1: F-1 real fixture trace — 03_fiqh 19-marker division → 10-char text growth, 9 stale join points, all validation passes silently
  - Probe 2: Word-merge rate across all 5 packages — 270/294 (92%) mid_sentence joins produce word-merging (SPEC design flaw, not CC bug)
  - Probe 3: Tanwin fathah + alif (ـًا) form — not detected as word-final (1/294 occurrences, SPEC limitation)
  - Probe 4: Regex edge cases — all 3 patterns correct at boundaries
  - Probe 5: Keyword matching against 322 headings — 2 true positives, 0 false positives
  - Probe 6: Empty primary_text and overlapping divisions — handled correctly
  - Probe 7: Step ordering analysis (aggregate→split vs SPEC split→aggregate) — cosmetic difference only
- [x] 2+ fixture semantic spot-checks — printed actual Arabic text:
  - Fixture 1: 02_nahw_muhaqiq — 23 chunks, all 7 invariants pass, text reads naturally except at mid_sentence joins
  - Fixture 2: 06_usul — 9 chunks, 60/65 mid_sentence joins produce word-merging, verified 15 samples: all between-word corruptions
- [x] Cross-engine data flow: Pydantic round-trip on all 23 chunks, Arabic text preserved byte-for-byte
- [x] **SPEC concrete example trace (RULE 5):**
  - [x] BC_SEPARATOR_MAP compared with reference BC_JOIN_MAP — exact match on all 7 entries
  - [x] Split behavior on div_src_test0001_2_013 — 6056-word division, 3-way split, all invariants pass
  - [x] Divergences: none (no worked numerical examples in SPEC §4 to trace against)
- [x] Edge case probes with constructed inputs: 7 run, 2 findings (F-1, SPEC-ERRATA-3)

## Pass 3: Self-verification (RULES 6-7)
- [x] Every factual claim in Passes 1-2 verified against code with tool calls:
  - [x] "22 functions" — verified by `grep -c`
  - [x] "81 tests pass" — verified by re-running pytest
  - [x] "503 normalization tests" — verified by re-running pytest
  - [x] "contracts.py untouched" — verified by `git diff --name-only`
  - [x] "17 F401 lint errors" — verified by `ruff check` + `grep -c F401`
  - [x] "19 markers all colliding" — verified by fixture scan
  - [x] "10-char growth, 9 stale JPs" — verified by re-running renumber trace
  - [x] "270/294 word-merge rate" — **CORRECTED from "219/294" in Round 2** (broken script checked only 3 packages)
  - [x] "CC's heuristic matches SPEC" — verified by `inspect.getsource`
  - [x] "All validation passes silently" — verified by isolated run_phase1
- [x] Check for rationalization patterns: SPEC-ERRATA-1 classification verified not rationalization (CC code matches SPEC exactly)
- [x] Review Notes drafted — each Note verified against code before writing

## Findings

| # | File | Finding | Fix | Fixed? |
|---|------|---------|-----|--------|
| F-1 | phase1_assembly.py (run_phase1, lines 1390–1429) | Stale join_point char_offset_in_assembled after footnote renumbering. Renumbering can change text length (⌜1⌝→⌜10⌝), shifting character offsets. Join_points are never updated. Rebase uses stale offsets → silent T-2 layer misattribution. Confirmed on 03_fiqh: 10-char growth, 9 stale JPs, all validation passes. | CC fix: add `_adjust_join_points_after_renumber()` helper. Apply in run_phase1 step 4 after renumbering. Update both chunk join_points and original_join_points. Add regression test. | [ ] |
| F-2 | conftest.py, test_phase1_assembly.py, test_phase1_tree_walk.py, test_phase1_validation.py | 17 unused imports (F401). NEXT.md verification step 4 requires lint clean. | CC fix: `ruff check --fix engines/excerpting/tests/` | [ ] |

## SPEC Errata documented (architect-owned, not CC findings)

- SPEC-NOTE-4: mid_sentence word-final heuristic produces 92% word-merge corruption (T-1). SPEC design flaw, not CC bug. 270/294 mid_sentence boundaries merge separate words.
- SPEC-NOTE-5: tanwin fathah + alif form not detected as word-final. 1/294 boundaries. Subsumable into NOTE-4's fix.
- SPEC-NOTE-6: EXCLUDE_KEYWORDS expanded from SPEC's 5 to CC's 13. Zero false positives. Should be added to SPEC §4.2.
- SPEC-NOTE-7: SPEC §4.2 says "word-boundary-aware" but implementation uses exact match. Exact match is correct (prevents "مصادر الأحكام" false positive). SPEC wording should say "exact match after noise stripping."

## Fixes committed
- [ ] ALL findings above have `Fixed? [x]`
- [ ] Fix commits pushed to repo
- [ ] Tests re-run after fixes: `[N] passed`
- [ ] `python tools/check_cross_engine_contracts.py` re-run after fixes → `[PASS/FAIL]`

## Verdict

**Verdict: BLOCKED — 2 findings (F-1, F-2). Fix directive prepared in NEXT.md.**

## Build metrics (cumulative)
```
Excerpting engine:
  Implementation: ~1505 lines (+1182 this session)
  Tests: 81 passing (+81 this session, baseline was 0)
  Test-to-code ratio: 5.4 tests per 100 impl lines
  conftest factories: 8 (4 original + 4 new)
  SPEC sections implemented: §4.2, §4.3, §4.4, §4.5, §4.6, §4.7, §4.8, §4.9
  SPEC sections remaining: §5 (Phase 2), §6 (Phase 3), §7, §8, §9
  Known limitations: SPEC-NOTE-4 (mid_sentence 92% word-merge, blocks Phase 2 deployment)
```
