# Independent CC Review — Excerpting Engine: contracts.py Rewrite

> **Commit reviewed:** `94aa487f` (rewrite excerpting contracts.py) — same commit as prior review
> **Reviewer:** Claude Chat (Architect) — independent session, fresh context
> **Date:** 2026-03-23
> **Protocol:** reference/protocols/REVIEW_PROTOCOL.md — 3-round mandatory review
> **Context:** Prior autonomous review (d167abc6) claimed 48 probes, zero findings. This independent review found and fixed 1 finding the prior review missed.

## Pre-review
- [x] Repo cloned, commit diff read (`94aa487f`)
- [x] NEXT.md re-read — 891-line handoff specifying complete rewrite
- [x] QUALITY_AXIOM.md re-read — architect is sole quality gate
- [x] REVIEW_PROTOCOL.md re-read — 3-round mandatory structure
- [x] Skills invoked: kr-reviewing-cc-output, critical-review, thinking-frameworks

## Pass 1: Structural
- [x] `engines/excerpting/contracts.py` read in 6 chunks (1-200, 200-400, 400-600, 600-800, 800-1000, 1000-1102). No truncation.
  - 27 classes (ast.parse verified)
  - 7 top-level functions (ast.parse verified)
  - 6 model_validators (ast.parse verified)
  - 1101 lines (wc -l verified)
- [x] `engines/excerpting/tests/conftest.py` read in full — 184 lines, 4 factory functions
- [x] Normalization test suite: 503 passed, 14 skipped, 0 failed (zero regressions)
- [x] Cross-engine boundary: only conftest.py imports from excerpting (grep verified)
- [x] Normalization contracts: 0 bytes changed (git diff verified)
- [x] All 15 NEXT.md verification checks: PASS
- [x] SPEC field-by-field cross-reference:
  - ExcerptRecord: 33/33 fields, names match, DD8 patterns verified
  - AssembledChunk: 16/16 fields, all sub-types correct
  - ClassifiedSegment: 6/6 fields
  - TeachingUnit: 10/10 fields
  - LLM schemas: 7/7 types, field counts match
  - Error codes: 28/28 match
  - Config: 18/18 parameters match SPEC §8.3
  - Enums: ScholarlyFunction 16 values, SelfContainmentLevel 3 values
- [x] 12/12 critical audit artifacts present and verified
- [x] JSON round-trip: ExcerptRecord and AssembledChunk serialize/deserialize correctly
- [x] DD8 Pattern 1 serialization: school present as null in JSON
- [x] Arabic diacritics round-trip preserved
- [x] Factory consistency: all 4 factories produce valid instances, full pipeline chain passes
- [x] Normalization type imports: all 7 resolve with expected field shapes

**Pass 1 finding count: 0**

## Pass 2: Adversarial
- [x] 12 probing scripts, 67+ individual assertions:
  - Probe 1a: AC invariant boundaries (I-AC-1/5/6/7) — 6 cases
  - Probe 1b: CS invariant boundaries (I-CS-1/2/3/4/5/overlap/empty) — 8 cases
  - Probe 1c: TU invariant boundaries (I-TU-1/2/3/4/5/9) — 9 cases, **1 finding (F-1)**
  - Probe 2: Error path robustness (OOB/empty/negative/duplicates/ordering) — 6 cases
  - Probe 3: I-TU-8 warning boundary precision (4/5/35/36 words) — 4 cases
  - Probe 4: LLM response schema (instructor-compatible JSON) — 6 cases incl. DD8
  - Probe 5: Arabic word count edge cases (diacritics/numbers/mixed/Quran brackets) — 9 cases
  - Probe 6: I-ER-4 all self-containment branches — 11 cases
  - Probe 7: Full pipeline data flow (AC→CS→TU→ER) — realistic Arabic, text integrity, ID format
  - Probe 8: Layer coverage validator edge cases — 8 cases
  - Probe 9: Collection ordering (string/numeric sort, equal keys) — 5 cases
  - Probe 10: ExtractionResult.notes optionality — 3 variants
  - Probe 11: Field constraints (ge/le boundaries) — 7 cases
  - Probe 12: model_construct bypass + defense in depth — 2 cases

- [x] SPEC concrete example trace: full pipeline (Phase 1→2a→2b→3) with realistic Arabic text from Surat Al-Fatiha. All invariants validated at each phase boundary. Text extraction integrity verified. ID format verified.
- [x] Cross-engine data flow: normalization types verified compatible
- [x] Fixture spot-check: Arabic diacritics, Quran brackets, footnote markers, mixed script — all preserved correctly

**Pass 2 finding count: 1 (F-1)**

### F-1: `validate_tu_invariants` IndexError on OOB segment_indices

- **Location:** contracts.py line 956 (pre-fix)
- **Root cause:** I-TU-5 accesses `segments[si[0]]` before I-TU-3 validates index range
- **Impact:** LOW (engineering quality — unhelpful error message, not knowledge corruption)
- **Fix:** Added bounds check between I-TU-2 and I-TU-5 (10 lines)
- **Verification:** OOB/negative indices now produce clean ValueError; valid cases unaffected; 503 tests pass

## Pass 3: Self-verification
- [x] Structural counts re-verified: 27 classes, 7 functions, 6 validators (ast.parse)
- [x] Line counts re-verified: 1111 (post-fix), 184 conftest
- [x] Test count re-verified: 503 passed, 14 skipped
- [x] Cross-engine boundary re-verified: only conftest imports
- [x] F-1 fix verified: 5 test cases (OOB, negative, valid single, valid multi, contiguous OOB)
- [x] All 15 NEXT.md checks re-run after fix: all PASS
- [x] Invariant completeness: 29 in SPEC, 27 in code, 2 documented exclusions (I-ER-2 runtime, I-ER-6 structural)
- [x] Rationalization check:
  - UnitEnrichment optionality: verified against SPEC §7.2.4 table + empirical probes. Not a finding.
  - Arabic-Indic digits in word count: SPEC explicitly says U+0600-U+06FF. Not a finding.
  - String sort for div_id: SPEC §2.2.1 explicitly says "string sort." Not a finding.
- [x] Unconstrained adversarial (Standing Order 7):
  - Mutable default trap: all list fields use default_factory=list. No bugs.
  - JSON Schema compatibility: all 4 LLM schemas produce valid schemas, DD8 patterns in schema correct.
  - Instructor compatibility: schemas work for structured output extraction.

**Pass 3 finding count: 0 (F-1 already fixed)**

## Findings

| # | File | Finding | Severity | Fix | Fixed? |
|---|------|---------|----------|-----|--------|
| F-1 | contracts.py:956 | validate_tu_invariants crashes with IndexError on OOB segment_indices instead of clean ValueError | LOW | Added bounds check before segment list access | ✅ Fixed and verified |

## Verdict

**Verdict: ACCEPT**

One finding (F-1), fixed and verified in this session. The code matches the SPEC field-by-field across all 8 referenced sections. 67+ adversarial probes confirm behavioral correctness. DD8 optionality patterns work correctly in construction, serialization, and JSON Schema. Defense in depth (model_validators + standalone functions) both functional. Arabic diacritics preserved through round-trip. All invariants accounted for (27 enforced + 2 documented runtime exclusions = 29 SPEC total). Zero regressions.

## Build metrics (cumulative)

```
Excerpting contracts: 1111 impl lines (1101 original + 10 fix)
Excerpting test infrastructure: 184 lines (conftest.py)
Normalization engine: 503 tests passing (0 regressions)
Types defined: 2 enums, 12 sub-types, 4 main types, 7 LLM schemas
Invariant checks: 29 total (6 model_validators + 7 standalone functions)
Error codes: 28 (EX-A/C/M/V/G)
Config params: 18 static
```
