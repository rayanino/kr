# NEXT — Excerpting Engine Session 5: Phase 3 Validation + Output Writer

## Current Position

- **Excerpting Phase 1:** COMPLETE. 117 tests (incl. hardening).
- **Excerpting Phase 2:** COMPLETE. 141 tests (incl. hardening).
- **Excerpting Phase 3.1:** COMPLETE. 86 tests, 637 lines. Deterministic metadata assembly.
- **Excerpting Phase 3.2:** COMPLETE. 27 tests, ~300 lines. LLM enrichment (enrich_chunk, apply_enrichment, run_phase3_enrichment).
- **Excerpting Phase 3.3:** COMPLETE. 33 tests, ~450 lines. Consensus verification + human gates (verify_chunk, resolve_consensus, check_gate_triggers, run_consensus).
- **Test baseline:** 438 tests passing, 0 failures (excerpting)
- **Open SPEC errata:** None

## What to Do

Implement Phase 3 Stage 4 (§7.4 Self-Validation) and the output writer (`writer.py`). This completes Phase 3 and produces the final output files.

**Processing flow:**
1. After consensus resolution, run 9 validation checks (V-P3-1 through V-P3-9) on each excerpt
2. Write validated excerpts to `excerpts.jsonl` (one line per ExcerptRecord)
3. Write gate entries to `gate_queue.jsonl` (one line per gate trigger)
4. Produce processing summary/manifest

## Context

This is the final build session for Phase 3. After this, all three phases are complete and Session 6 does integration + cross-engine testing.

Key patterns:
- **Validation is not correction.** V-P3 checks detect problems and emit error codes. They do NOT auto-correct (exception: V-P3-8 removes orphan footnotes). Mismatches signal bugs.
- **Gate queue integrity (V-P3-7) is CRITICAL.** Missing gate entry = invisible uncertainty → halt processing (EX-M-008).
- **Writer produces JSONL.** One JSON object per line, no pretty-printing. ExcerptRecord serialized via Pydantic `.model_dump(mode="json")`.

## Read First

| File | Lines | What |
|------|-------|------|
| `engines/excerpting/SPEC.md` | §7.4 (1893–1913) | **Validation checks V-P3-1 through V-P3-9.** |
| `engines/excerpting/SPEC.md` | §3 (367–395) | **Output format.** excerpts.jsonl + gate_queue.jsonl paths and structure. |
| `engines/excerpting/SPEC.md` | §8.1 (1957–1970) | **Error codes EX-M-004 through EX-M-010.** Triggered by validation checks. |
| `engines/excerpting/SPEC.md` | §10.6 (2274–2279) | **Test examples for V-P3 checks.** |
| `engines/excerpting/contracts.py` | 440–530 | `ExcerptRecord` — the type being validated and serialized |
| `engines/excerpting/contracts.py` | 675–740 | `ExcerptingErrorCodes` — EX-M-004 through EX-M-010, EX-V-002 |
| `engines/excerpting/src/phase3_enrichment.py` | all | Upstream: enrichment output to validate |
| `engines/excerpting/src/phase3_consensus.py` | all | Upstream: consensus output + gate entries to validate and write |
| `engines/excerpting/tests/conftest.py` | all | Existing factory helpers |

## What to Build

### Module 1: `phase3_validation.py` (§7.4)

**Function 1: `validate_excerpt(excerpt) → tuple[ExcerptRecord, list[str]]`**
Run V-P3-1 through V-P3-9 on a single excerpt. Return the (possibly modified) excerpt and a list of emitted error codes.

Validation checks:
- **V-P3-1 (ID uniqueness):** Checked at batch level, not per-excerpt.
- **V-P3-2 (Primary text integrity):** First 80 chars of `primary_text` match `text_snippet` after whitespace normalization.
- **V-P3-3 (Author attribution completeness):** `primary_author_layer` is not null. Emit EX-M-004 if null.
- **V-P3-4 (Topic keyword validity):** 1–3 `excerpt_topic` keywords when LLM enrichment succeeded (no `llm_enrichment_failed` flag). Emit EX-M-005 if violated.
- **V-P3-5 (Self-containment consistency):** PARTIAL → context_hint non-null (unless llm_enrichment_failed). FULL/DEPENDENT → context_hint null. Emit EX-M-006 if mismatched.
- **V-P3-6 (Evidence reference integrity):** Quran refs have valid surah (1–114) and ayah in range. Emit EX-M-007 if invalid.
- **V-P3-7 (Gate queue integrity):** Checked at writer level after writing.
- **V-P3-8 (Footnote relevance):** Remove footnotes with ref_marker offset outside excerpt range. Emit EX-M-009.
- **V-P3-9 (Content type consistency):** All content_types are valid ScholarlyFunction values. Emit EX-M-010 if unknown.

**Function 2: `validate_batch(excerpts) → tuple[list[ExcerptRecord], list[str]]`**
Run validate_excerpt on each excerpt. Also check V-P3-1 (ID uniqueness) at batch level. Return validated excerpts and all error codes.

### Module 2: `writer.py` (§3)

**Function 1: `write_excerpts(excerpts, output_dir) → Path`**
Write validated ExcerptRecords to `excerpts.jsonl`. One JSON line per record.

**Function 2: `write_gate_queue(gate_entries, output_dir) → Path`**
Write gate entries to `gate_queue.jsonl`. One JSON line per entry.

**Function 3: `verify_gate_queue(gate_entries, gate_path) → list[str]`**
V-P3-7: Read back `gate_queue.jsonl` and verify each expected gate entry exists. Emit EX-M-008 if any missing.

### Module: Tests

**File: `engines/excerpting/tests/test_phase3_validation.py`**

Test each V-P3 check individually:
1. V-P3-1: Duplicate IDs detected
2. V-P3-2: Text integrity pass and fail (EX-V-002)
3. V-P3-3: Null attribution → EX-M-004
4. V-P3-4: Topic count violations → EX-M-005
5. V-P3-5: Self-containment/hint mismatches → EX-M-006
6. V-P3-6: Invalid Quran refs → EX-M-007
7. V-P3-8: Orphan footnotes removed → EX-M-009
8. V-P3-9: Unknown content types → EX-M-010

**File: `engines/excerpting/tests/test_writer.py`**

1. JSONL format correctness (parseable, one object per line)
2. Round-trip: write → read → compare
3. Gate queue write + V-P3-7 verification
4. Empty inputs handled
5. EX-M-008 on missing gate entry

**Expected total: 438 + ≥25 = ≥463 passed tests.**

## Design Decisions (Pre-Resolved)

**DD-S5-1: Validation does not auto-correct (except V-P3-8).**
V-P3 checks emit error codes and log. They do NOT change data — with the sole exception of V-P3-8, which removes orphan footnotes (because keeping them is more wrong than removing them).

**DD-S5-2: JSONL output via Pydantic.**
Use `exc.model_dump(mode="json")` + `json.dumps(ensure_ascii=False)` for each line. `ensure_ascii=False` preserves Arabic characters without escaping.

**DD-S5-3: Gate queue verification reads back the file.**
V-P3-7 is paranoid by design: it writes the gate queue, then reads it back and checks. This catches filesystem failures, encoding issues, etc.

**DD-S5-4: EX-M-008 halts processing.**
If gate verification fails (missing entry), the writer MUST raise an exception. Invisible uncertainty > visible stop. This is CRITICAL severity in §8.1.

## Do NOT Do

1. **Do NOT implement the Phase 3 orchestrator** that chains all stages — that's Session 6.
2. **Do NOT modify Phase 1, Phase 2, or Phase 3.1–3.3 code.**
3. **Do NOT modify `contracts.py`** unless you find a bug.
4. **Do NOT make real LLM calls.** All tests are deterministic.
5. **Do NOT invent error codes.** Use only codes from `ExcerptingErrorCodes`.
6. **Do NOT pretty-print JSONL.** One compact JSON object per line.

## Verification

1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → **≥463 passed**, 0 failed
2. `grep -r "raise NotImplementedError" engines/excerpting/src/phase3_validation.py` → empty
3. `grep -r "raise NotImplementedError" engines/excerpting/src/writer.py` → empty
4. `grep -c "def test_" engines/excerpting/tests/test_phase3_validation.py` → ≥15
5. `grep -c "def test_" engines/excerpting/tests/test_writer.py` → ≥10
6. All 9 V-P3 checks have at least one test
7. Gate queue round-trip tested
8. EX-M-008 halt behavior tested

## After This

Session 6 will implement the Phase 3 orchestrator that chains all stages (deterministic → enrichment → consensus → validation → writer) and run cross-engine integration tests.
