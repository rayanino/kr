# NEXT — Excerpting Session 4 Fixes (Architect Review Findings)

## Current Position

- **Excerpting Phase 3.2 (LLM enrichment):** COMPLETE. 27 tests. 442 impl lines.
- **Excerpting Phase 3.3 (consensus verification):** COMPLETE. 33 tests. 767 impl lines.
- **Test baseline:** 437 passed, 2 skipped, 0 failed (excerpting)
- **Review status:** Round 1 BLOCKED — 3 findings require fixes before acceptance

## What to Do

Fix 3 bugs found during architect review of Session 4 (commit `4a7f71e9`). All fixes are in `engines/excerpting/src/phase3_consensus.py` and `engines/excerpting/src/phase3_enrichment.py`. No changes to `contracts.py`.

After fixing, the test count must be ≥ 437 + (new tests for each fix) = **≥ 448 passed**.

---

## Fix 1: FULL→PARTIAL/DEPENDENT downgrade produces invalid ExcerptRecord [CRASH]

**Severity:** HIGH — crash on JSONL round-trip, blocks Session 5 writer

**Root cause:** When consensus downgrades `self_containment` from FULL to PARTIAL or DEPENDENT, `_repair_context_hint()` updates `context_hint` but does NOT set `self_containment_notes`. FULL excerpts have `self_containment_notes=None` (required by I-ER-4). After model_copy, the ExcerptRecord has PARTIAL (or DEPENDENT) + `self_containment_notes=None`, which violates I-ER-4. Pydantic v2 `model_copy` does NOT re-run validators, so no immediate crash — but any `model_validate()`, `ExcerptRecord(**data)`, or JSONL round-trip crashes with `ValueError: I-ER-4: PARTIAL -> self_containment_notes required`.

**File:** `engines/excerpting/src/phase3_consensus.py`

**Fix location:** `_repair_context_hint()` function (lines 501–536)

**Exact fix:** When `excerpt.self_containment == FULL` and the new level is PARTIAL or DEPENDENT, also set `updates["self_containment_notes"]`. The notes should describe the consensus downgrade.

Replace lines 513–534 with:

```python
    if new_level == SelfContainmentLevel.DEPENDENT:
        updates["context_hint"] = None
        # I-ER-4: DEPENDENT requires self_containment_notes.
        # If original was FULL, it has no notes. Generate from consensus.
        if excerpt.self_containment == SelfContainmentLevel.FULL:
            notes = "تم تعديل التقييم بعد التحقق: يعتمد كلياً على السياق"
            consensus = updates.get("consensus_metadata")
            if isinstance(consensus, ConsensusRecord):
                for d in consensus.decisions:
                    if d.decision_type == "self_containment" and not d.verifier_agrees:
                        notes = f"تم تعديل التقييم من مكتفٍ ذاتياً إلى معتمد — المحقق: {d.verifier_value}"
                        break
            updates["self_containment_notes"] = notes
    elif (
        new_level == SelfContainmentLevel.PARTIAL
        and excerpt.self_containment == SelfContainmentLevel.FULL
    ):
        # FULL→PARTIAL: original has no notes or hint. Generate both.
        # I-ER-4: PARTIAL requires self_containment_notes AND context_hint.
        notes = "تم تعديل التقييم بعد التحقق: يحتاج سياقاً جزئياً"
        consensus = updates.get("consensus_metadata")
        if isinstance(consensus, ConsensusRecord):
            for d in consensus.decisions:
                if d.decision_type == "self_containment" and not d.verifier_agrees:
                    notes = f"تم تعديل التقييم من مكتفٍ ذاتياً إلى جزئي — المحقق: {d.verifier_value}"
                    break
        updates["self_containment_notes"] = notes
        # context_hint: use the generated notes as the hint
        updates["context_hint"] = notes
```

**Tests to add (in `test_phase3_consensus.py`):**

1. `test_full_to_partial_sets_self_containment_notes`: Create a FULL excerpt (self_containment_notes=None, context_hint=None). Run `_repair_context_hint` with `updates={"self_containment": SelfContainmentLevel.PARTIAL}`. Assert `"self_containment_notes"` key is in the returned updates dict and its value is a non-empty string.

2. `test_full_to_dependent_sets_self_containment_notes`: Create a FULL excerpt. Run `_repair_context_hint` with `updates={"self_containment": SelfContainmentLevel.DEPENDENT}`. Assert `"self_containment_notes"` is in updates AND `"context_hint"` is None.

3. `test_full_to_partial_roundtrip_valid`: Acid test. Create a FULL excerpt. Simulate the full downgrade: build updates dict with `{"self_containment": SelfContainmentLevel.PARTIAL}`, run `_repair_context_hint`, then apply via `excerpt.model_copy(update=updates)`. Then: `ExcerptRecord.model_validate(updated.model_dump())` — this MUST NOT raise. It proves the record survives serialization.

4. `test_full_to_dependent_roundtrip_valid`: Same acid test for FULL→DEPENDENT. Create FULL excerpt, build updates dict with `{"self_containment": SelfContainmentLevel.DEPENDENT}`, run `_repair_context_hint`, model_copy, then `ExcerptRecord.model_validate(updated.model_dump())` MUST NOT raise.

5. `test_partial_to_dependent_keeps_existing_notes`: PARTIAL excerpt (already has `self_containment_notes="يحتاج سياقاً"`). Run `_repair_context_hint` with `updates={"self_containment": SelfContainmentLevel.DEPENDENT}`. Assert `"self_containment_notes"` is NOT in updates (original notes are preserved through model_copy since _repair_context_hint doesn't overwrite them when notes already exist). Assert `"context_hint"` is None.

**Expected: 5 new tests.**

---

## Fix 2: EX-G-003 over-triggers when verifier agrees with source metadata

**Severity:** MEDIUM — human gate queue pollution (false positives)

**Root cause:** SPEC §7.3.4 says EX-G-003 fires when "source_school conflicts with **both** models." The code in `_resolve_school()` (line 290) checks `vi.alternative != excerpt.school` (verifier ≠ enrichment) instead of `vi.alternative != source_school` (verifier ≠ source). This means EX-G-003 fires even when the verifier AGREES with the source metadata — the scenario where the correct answer is clearest.

Truth table:
- source=حنبلي, enrichment=شافعي, verifier=مالكي → should trigger (source conflicts with BOTH) ✓
- source=حنبلي, enrichment=شافعي, verifier=حنبلي → should NOT trigger (verifier agrees with source) ← BUG: triggers

**File:** `engines/excerpting/src/phase3_consensus.py`

### Fix 2a: `_resolve_school()` (line 290)

Change line 290 from:
```python
            and vi.alternative != excerpt.school
```
to:
```python
            and vi.alternative != source_school
```

### Fix 2b: `check_gate_triggers()` (lines 575–585)

This function also checks EX-G-003 but doesn't have direct access to the verifier's alternative. It needs to read the verifier's school from `consensus_metadata`.

Replace lines 575–585 with:
```python
    # EX-G-003: School conflicts with source metadata AND both models
    source_school = manifest_metadata.get("source_school")
    if (
        config.GATE_ON_SCHOOL_CONFLICT
        and source_school
        and excerpt.school is not None
        and excerpt.school != source_school
        and "school_consensus_disagreement" in excerpt.review_flags
    ):
        # SPEC §7.3.4: source must conflict with BOTH models.
        # Check verifier's school from consensus_metadata.
        verifier_also_conflicts = True  # Conservative default if no metadata
        if excerpt.consensus_metadata:
            for d in excerpt.consensus_metadata.decisions:
                if d.decision_type == "school_attribution" and d.verifier_value is not None:
                    verifier_also_conflicts = (d.verifier_value != source_school)
                    break
        if verifier_also_conflicts:
            if ExcerptingErrorCodes.EX_G_003 not in excerpt.gate_flags:
                gates.append(ExcerptingErrorCodes.EX_G_003)
```

**Tests to add (in `test_phase3_consensus.py`):**

1. `test_ex_g_003_not_triggered_when_verifier_agrees_with_source`: source_school=حنبلي, enrichment school=شافعي, verifier alternative=حنبلي. Run `_resolve_school`. Assert EX-G-003 NOT in gates.

2. `test_ex_g_003_triggered_when_source_conflicts_with_both`: source_school=حنبلي, enrichment school=شافعي, verifier alternative=مالكي. Run `_resolve_school`. Assert EX-G-003 IS in gates.

3. `test_check_gate_triggers_ex_g_003_respects_verifier`: Create excerpt with `school="شافعي"`, `review_flags=["school_consensus_disagreement"]`, and `consensus_metadata` containing a school_attribution decision with `verifier_value="حنبلي"`. Call `check_gate_triggers` with `manifest_metadata={"source_school": "حنبلي"}`. Assert EX-G-003 NOT in gates.

4. `test_check_gate_triggers_ex_g_003_triggers_when_both_conflict`: Same setup but `verifier_value="مالكي"`. Assert EX-G-003 IS in gates.

**Expected: 4 new tests.**

---

## Fix 3: Chunk matching via `startswith` is fragile

**Severity:** MEDIUM — latent bug for split chunks

**Root cause:** Both `run_phase3_enrichment` (lines 375–379) and `run_consensus` (lines 643–648) match excerpts to chunks using `cid.startswith(exc.div_id)`. This false-matches: `div_1` matches `div_10_chunk_0`. And for split chunks, all excerpts get assigned to the first matching chunk regardless of `chunk_index`.

**Files:** 
- `engines/excerpting/src/phase3_enrichment.py` (lines 370–380)
- `engines/excerpting/src/phase3_consensus.py` (lines 640–648)

**Fix:** Replace the startswith loop in BOTH files. The new logic:

```python
    # Group excerpts by chunk_id
    chunk_map: dict[str, AssembledChunk] = {c.chunk_id: c for c in chunks}
    excerpts_by_chunk: dict[str, list[ExcerptRecord]] = defaultdict(list)
    for exc in excerpts:
        # Exact match: non-split chunks have chunk_id == div_id
        chunk_id = exc.div_id
        if chunk_id not in chunk_map:
            # Try split chunk format: {div_id}_chunk_{chunk_index}
            split_id = f"{exc.div_id}_chunk_{exc.chunk_index}"
            if split_id in chunk_map:
                chunk_id = split_id
        excerpts_by_chunk[chunk_id].append(exc)
```

**Tests to add:**

1. `test_split_chunk_matched_correctly` (in `test_phase3_enrichment.py`): Create 2 chunks: `chunk_id="div_a_chunk_0"` (div_id="div_a") and `chunk_id="div_a_chunk_1"` (div_id="div_a"). Create 2 excerpts: `div_id="div_a", chunk_index=0` and `div_id="div_a", chunk_index=1`. Mock client returns different enrichment for each call. Run `run_phase3_enrichment`. Assert each call gets the correct chunk (verify via mock call_args: first call gets chunk_0's text, second call gets chunk_1's text).

2. `test_split_chunk_consensus_matched_correctly` (in `test_phase3_consensus.py`): Same pattern for `run_consensus`.

**Expected: 2 new tests (1 per module).**

---

## Read First

| File | Lines | What |
|------|-------|------|
| `engines/excerpting/src/phase3_consensus.py` | 501–536 | `_repair_context_hint` — Fix 1 |
| `engines/excerpting/src/phase3_consensus.py` | 284–293 | `_resolve_school` EX-G-003 — Fix 2a |
| `engines/excerpting/src/phase3_consensus.py` | 575–587 | `check_gate_triggers` EX-G-003 — Fix 2b |
| `engines/excerpting/src/phase3_enrichment.py` | 370–380 | Chunk matching — Fix 3 |
| `engines/excerpting/src/phase3_consensus.py` | 640–648 | Chunk matching — Fix 3 |
| `engines/excerpting/contracts.py` | 534–566 | I-ER-4 validator — the rule Fix 1 must satisfy |
| `engines/excerpting/tests/conftest.py` | all | Test factories |
| `engines/excerpting/tests/test_phase3_consensus.py` | all | Existing tests — add new tests at end |
| `engines/excerpting/tests/test_phase3_enrichment.py` | all | Existing tests — add new tests at end |

## Do NOT Do

1. **Do NOT modify `contracts.py`.** All fixes are in implementation files.
2. **Do NOT modify existing tests.** Only ADD new tests.
3. **Do NOT change consensus resolution logic** (majority voting, conservatism rule, etc.) — only the downstream repair and gate trigger checks.
4. **Do NOT run self-review.** The architect will review after you push. Just run pytest.
5. **Do NOT modify `NEXT.md`** after fixing — the architect will restore the Session 5 directive.

## Verification

1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → **≥ 448 passed** (437 + 11 new), 0 failed
2. `grep -c "def test_" engines/excerpting/tests/test_phase3_consensus.py` → ≥ 42 (was 33, adding 9)
3. `grep -c "def test_" engines/excerpting/tests/test_phase3_enrichment.py` → ≥ 28 (was 27, adding 1)
4. Fix 1 acid test: `test_full_to_partial_roundtrip_valid` and `test_full_to_dependent_roundtrip_valid` call `ExcerptRecord.model_validate(updated.model_dump())` and do NOT raise
5. Fix 2 acid test: `test_ex_g_003_not_triggered_when_verifier_agrees_with_source` asserts EX-G-003 NOT in gates
6. `grep -n "startswith" engines/excerpting/src/phase3_enrichment.py engines/excerpting/src/phase3_consensus.py` → 0 hits in chunk matching blocks
7. All 437 existing tests still pass (zero regressions)

## After This

The architect will review the fixes in a new chat session (Round 2 adversarial + Round 3 verdict). If accepted, the Session 5 NEXT.md (§7.4 validation + writer) will be restored. The backed-up Session 5 NEXT.md is at `reference/archive/sessions/NEXT_session5_original.md`.
