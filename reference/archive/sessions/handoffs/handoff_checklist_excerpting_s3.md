# Handoff Checklist — Excerpting Session 3: Phase 3 Deterministic

**Date:** 2026-03-23
**Commit:** `8a58a5ac`
**Architect:** Claude Chat

---

## Step 2: Test Baseline
- [x] pytest run: `147 passed, 2 skipped`
- [x] Count matches NEXT.md header: yes

## Step 3: File References
| File | Exists | Lines Verified |
|------|--------|---------------|
| `engines/excerpting/SPEC.md` §7.1 (1397–1518) | ✅ | ✅ (grep confirms §7.1 at 1397) |
| `engines/excerpting/SPEC.md` §6.2 (1260–1340) | ✅ | ✅ (grep confirms §6.2 at 1261) |
| `engines/excerpting/SPEC.md` §2.2 (365–520) | ✅ | ✅ |
| `engines/excerpting/contracts.py` 87–200 | ✅ | ✅ (PageRange at 87, AuthorAttribution at 99) |
| `engines/excerpting/contracts.py` 440–530 | ✅ | ✅ (ExcerptRecord fields) |
| `engines/excerpting/contracts.py` 1036–1100 | ✅ | ✅ (validate_er_invariants at 1036) |
| `engines/excerpting/contracts.py` 675–740 | ✅ | ✅ (ExcerptingErrorCodes at 675) |
| `engines/excerpting/src/phase3_deterministic.py` | ✅ | ✅ (stubs present) |
| `engines/excerpting/src/phase2_classify.py` 105–123 | ✅ | ✅ (_build_token_char_map at 105) |
| `engines/excerpting/tests/conftest.py` | ✅ | ✅ |

## Step 5: SPEC Example Traces
| SPEC Section | Example | Trace Result | Match |
|---|---|---|---|
| §7.1 F-DET-1 | `exc_12345_div_3_2_0_7` | Algorithm produces correct format | ✅ |
| §7.1 F-DET-1 | `exc_12345_div_3_2_1_3` | Algorithm produces correct format | ✅ |
| §7.1 F-DET-2 | Substring extraction preserving `\n\n` | Off-by-one detail correct: `_build_token_char_map` returns exclusive end, no +1 needed | ✅ |
| §6.2 LA-1 through LA-4 | Constructed inputs for all 4 rules | All 4 rules trace correctly with overlap formula | ✅ |

Done in previous chat session (Part 1). Not redone — verified results documented.

## Step 6: Fixture Testing
| Detection Logic | Total Fixtures | Total Chars | Key Finding | Action |
|---|---|---|---|---|
| Evidence markers (all) | 66 | 16.7M | Word-boundary checks catastrophically wrong (76% FN on إجماع) | DD-S3-8: drop boundary checks |
| Quran ﴿﴾ delimiters | 66 | 16.7M | Zero hits — Shamela doesn't use ornate parentheses | Note added, not blocking |
| `رواه` without boundary | 66 | 16.7M | 511 matches, ~2 FPs (0.13%) | Acceptable |
| `أخرجه` without boundary | 66 | 16.7M | 503 matches, 0 genuine FPs | Acceptable |
| `إجماع` without boundary | 66 | 16.7M | 163 matches, ~1 FP (0.6%) | Acceptable |

Done in previous chat session (Part 1). Not redone — empirical data settled.

## Step 7: Prerequisites
- [x] Test baseline verified (Step 2)
- [x] All Read First files exist
- [x] All line numbers verified (grep-confirmed in this session)
- [x] SPEC sections referenced specifically (§7.1, §6.2, §2.2)
- [x] Do NOT Do covers scope creep (8 items: no §7.2/7.3/7.4, no contracts mod, no Phase 1/2 mod, no Quran lookup, no LLM, no invented codes)
- [x] Verification has concrete pass/fail (8 items with grep commands and counts)
- [x] AGENT_ARCHITECTURE.md checked (previous session)
- [x] ENGINE_BUILD_BLUEPRINT.md checked (previous session)
- [x] Fixture claims verified by running code (66 fixtures, 16.7M chars)
- [x] SPEC thresholds copy-pasted with line numbers (80% at LA-1, 60% at LA-3, from §6.2)
- [x] All SPEC examples traced (Step 5)
- [x] New detection logic tested on fixtures (Step 6)
- [x] Cross-engine contracts verified (PhysicalPage, TextLayerSegment imports from normalization)

## Step 8: Adversarial Questions
1. **Judgment calls not covered?** Function 6 volume extraction was underspecified — FIXED: added explicit "first overlapping page" rule and None fallback. All other decisions covered by DD-S3-1 through DD-S3-9.
2. **Missing files?** ExcerptingErrorCodes was not in Read First — FIXED: added contracts.py 675–740. All stubs already import it.
3. **Ambiguous "done"?** No — Verification section has 8 concrete pass/fail checks.
4. **Wrong output passing verification?** Evidence detection tests now require detecting prefixed forms (الإجماع, وأخرجه) — CC can't accidentally add boundary checks and pass. Orchestrator tests verify school=None explicit.
5. **Unverified claims?** HEAD updated to 8459deac. All line numbers grep-verified.
6. **Missing test helpers?** conftest has _make_assembled_chunk, _make_teaching_unit, _make_classified_segment. NEXT.md specifies two new helpers: _make_multi_layer_chunk, _make_chunk_with_footnotes.
7. **Platform assumptions?** (S6 addition) No file I/O in Phase 3 deterministic — pure in-memory string/list operations. No CRLF risk.
8. **Do NOT Do vs Verification contradictions?** (S7 addition) Checked — no contradictions.
9. **Tautological tests?** (S7 addition) F-DET-5 tests check against known input strings with known markers — not internal consistency. F-DET-3 tests construct layers with known offsets and verify rule selection — independent of implementation.

## validate_handoff.py
Two known false positives:
1. `test_phase3_deterministic.py` flagged as missing — it's the file CC will create (validator doesn't distinguish input vs output files)
2. Test count 147 vs 503 — validator hardcoded to `engines/normalization/tests/` (tool bug, never updated for excerpting)

Both are validator bugs, not handoff issues. Real check: `python -m pytest engines/excerpting/tests/ -q --tb=no` → 147 passed, 2 skipped ✅

## Verdict
- [x] ALL boxes checked → READY
- Commit: `8a58a5ac`
