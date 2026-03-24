# NEXT — Excerpting Session 4 Fixes (Complete Architect Review)

## Current Position

- **Excerpting Phase 3.2 (LLM enrichment):** COMPLETE. 27 tests. 442 impl lines.
- **Excerpting Phase 3.3 (consensus verification):** COMPLETE. 33 tests. 767 impl lines.
- **Test baseline:** 437 passed, 2 skipped, 0 failed (excerpting)
- **Review status:** Round 1 BLOCKED — 8 findings, fixes specified below

## What to Do

Fix 8 bugs found during architect review of Session 4 (commit `4a7f71e9`). Fixes are in `phase3_consensus.py` and `phase3_enrichment.py`. No changes to `contracts.py`.

After fixing: **≥ 467 passed tests** (437 + ≥30 new).

**IMPORTANT ordering note for Fix 1:** In `resolve_consensus()`, `_repair_context_hint` is called at line 227, but `consensus_metadata` is added to `updates` at line 230–231. This means `_repair_context_hint` can NEVER read consensus decisions from `updates`. Fix 1 accounts for this by moving the `consensus_metadata` assignment BEFORE the `_repair_context_hint` call.

---

## Fix 1: FULL→PARTIAL/DEPENDENT downgrade produces invalid ExcerptRecord [CRASH]

**Severity:** HIGH — crash on JSONL round-trip, blocks Session 5 writer

**Root cause:** `_repair_context_hint()` sets `context_hint` but not `self_containment_notes` when downgrading from FULL. Violates I-ER-4. Pydantic v2 `model_copy` bypasses validators → silent invalid record → crash on re-validation.

**Combined with F-8 (ordering):** `_repair_context_hint` tries to read `consensus_metadata` from `updates`, but `consensus_metadata` isn't set until 3 lines later. The reading code always sees `None`.

**File:** `engines/excerpting/src/phase3_consensus.py`

### Fix 1a: In `resolve_consensus()`, move consensus_metadata BEFORE _repair_context_hint

Change lines 226–231 from:
```python
    # Apply context_hint repair after all consensus decisions
    updates = _repair_context_hint(excerpt, updates)

    updates["review_flags"] = review_flags
    if decisions:
        updates["consensus_metadata"] = ConsensusRecord(decisions=decisions)
```
To:
```python
    # Set consensus_metadata FIRST — _repair_context_hint reads it
    if decisions:
        updates["consensus_metadata"] = ConsensusRecord(decisions=decisions)

    # Apply context_hint repair after all consensus decisions
    updates = _repair_context_hint(excerpt, updates)

    updates["review_flags"] = review_flags
```

### Fix 1b: In `_repair_context_hint()`, set self_containment_notes on downgrade

Replace lines 513–534 with:
```python
    if new_level == SelfContainmentLevel.DEPENDENT:
        updates["context_hint"] = None
        # I-ER-4: DEPENDENT requires self_containment_notes.
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
        # FULL→PARTIAL: I-ER-4 requires self_containment_notes AND context_hint.
        notes = "تم تعديل التقييم بعد التحقق: يحتاج سياقاً جزئياً"
        consensus = updates.get("consensus_metadata")
        if isinstance(consensus, ConsensusRecord):
            for d in consensus.decisions:
                if d.decision_type == "self_containment" and not d.verifier_agrees:
                    notes = f"تم تعديل التقييم من مكتفٍ ذاتياً إلى جزئي — المحقق: {d.verifier_value}"
                    break
        updates["self_containment_notes"] = notes
        updates["context_hint"] = notes
```

**Tests (5 new, in `test_phase3_consensus.py`):**

1. `test_full_to_partial_sets_self_containment_notes`: FULL → `_repair_context_hint` with PARTIAL update → assert `"self_containment_notes"` in updates, non-empty.
2. `test_full_to_dependent_sets_self_containment_notes`: FULL → DEPENDENT → assert `"self_containment_notes"` in updates AND `"context_hint"` is None.
3. `test_full_to_partial_roundtrip_valid`: FULL excerpt → full resolve_consensus flow downgrading to PARTIAL → `ExcerptRecord.model_validate(updated.model_dump())` MUST NOT raise.
4. `test_full_to_dependent_roundtrip_valid`: Same for DEPENDENT.
5. `test_partial_to_dependent_keeps_existing_notes`: PARTIAL → DEPENDENT → assert existing notes preserved, `context_hint` is None.

---

## Fix 2: EX-G-003 over-triggers when verifier agrees with source metadata

**Severity:** MEDIUM — human gate queue pollution

**Root cause:** SPEC §7.3.4 says "source_school conflicts with **both** models." Code checks `vi.alternative != excerpt.school` (verifier ≠ enrichment) instead of `vi.alternative != source_school` (verifier ≠ source).

### Fix 2a: `_resolve_school()` line 290

Change `vi.alternative != excerpt.school` to `vi.alternative != source_school`.

### Fix 2b: `check_gate_triggers()` lines 575–585

Replace with:
```python
    source_school = manifest_metadata.get("source_school")
    if (
        config.GATE_ON_SCHOOL_CONFLICT
        and source_school
        and excerpt.school is not None
        and excerpt.school != source_school
        and "school_consensus_disagreement" in excerpt.review_flags
    ):
        verifier_also_conflicts = True  # Conservative default
        if excerpt.consensus_metadata:
            for d in excerpt.consensus_metadata.decisions:
                if d.decision_type == "school_attribution" and d.verifier_value is not None:
                    verifier_also_conflicts = (d.verifier_value != source_school)
                    break
        if verifier_also_conflicts:
            if ExcerptingErrorCodes.EX_G_003 not in excerpt.gate_flags:
                gates.append(ExcerptingErrorCodes.EX_G_003)
```

**Tests (4 new):**

1. `test_ex_g_003_not_triggered_when_verifier_agrees_with_source`: source=حنبلي, enrichment=شافعي, verifier=حنبلي → NOT in gates.
2. `test_ex_g_003_triggered_when_source_conflicts_with_both`: source=حنبلي, enrichment=شافعي, verifier=مالكي → IS in gates.
3. `test_check_gate_triggers_ex_g_003_respects_verifier`: consensus_metadata with verifier_value=حنبلي, source=حنبلي → NOT triggered.
4. `test_check_gate_triggers_ex_g_003_triggers_when_both_conflict`: verifier=مالكي, source=حنبلي → triggered.

---

## Fix 3: Chunk matching via `startswith` false-matches similar div_ids

**Severity:** MEDIUM — latent bug for split chunks

**Files:** `phase3_enrichment.py` lines 370–380 and `phase3_consensus.py` lines 640–648

**Fix (in BOTH files):** Replace startswith loop:
```python
    chunk_map: dict[str, AssembledChunk] = {c.chunk_id: c for c in chunks}
    excerpts_by_chunk: dict[str, list[ExcerptRecord]] = defaultdict(list)
    for exc in excerpts:
        chunk_id = exc.div_id
        if chunk_id not in chunk_map:
            split_id = f"{exc.div_id}_chunk_{exc.chunk_index}"
            if split_id in chunk_map:
                chunk_id = split_id
        excerpts_by_chunk[chunk_id].append(exc)
```

**Tests (2 new):**

1. `test_split_chunk_matched_correctly` (enrichment): Two chunks, two excerpts with matching chunk_index.
2. `test_split_chunk_consensus_matched_correctly` (consensus): Same.

---

## Fix 4: Attribution majority winner NOT applied to excerpt [CRITICAL — T-2]

**Severity:** CRITICAL — silent wrong author attribution

**Root cause:** `_resolve_attribution()` records majority in `ConsensusDecision.final_value` but does NOT update `primary_author_layer`. Excerpt keeps outvoted enrichment attribution.

**Existing test `test_2_of_3_majority_wins` is tautological:** uses enrichment=sch_a, escalation=sch_a → majority=enrichment, hides the bug.

**File:** `phase3_consensus.py`, `_resolve_attribution()` lines 332–347

**Fix:** When majority ≠ enrichment_val, apply it:
```python
            if majority is not None:
                updates["attribution_confidence"] = 0.67
                if majority != enrichment_val:
                    updates["primary_author_layer"] = excerpt.primary_author_layer.model_copy(
                        update={
                            "author_id": majority,
                            "rule_applied": "LA-3_consensus",
                        }
                    )
                decision = ConsensusDecision(
                    decision_type="author_attribution",
                    enrichment_value=enrichment_val,
                    verifier_value=verifier_val,
                    verifier_agrees=False,
                    escalation_value=escalation_value,
                    final_value=majority,
                    resolution_method="majority_2_of_3",
                )
```

**Tests (4 new):**

1. `test_majority_different_from_enrichment_applied`: enrichment=sch_a, verifier=sch_b, escalation=sch_b → `result.primary_author_layer.author_id == "sch_b"`. **ACID TEST.**
2. `test_majority_same_as_enrichment_no_change`: enrichment=sch_a, verifier=sch_b, escalation=sch_a → author_id stays "sch_a", rule_applied stays "LA-3".
3. `test_all_3_disagree_keeps_enrichment_with_zero_confidence`: enrichment=sch_a, verifier=sch_b, escalation=sch_c → author_id="sch_a", confidence=0.0.
4. `test_majority_applied_sets_consensus_rule`: majority ≠ enrichment → rule_applied == "LA-3_consensus".

---

## Fix 5: Verification item mapping ignores item_index (positional fragility)

**Severity:** MEDIUM — silent wrong consensus if LLM returns items out of order

**File:** `phase3_consensus.py` lines 714–726

**Fix:** Replace positional iterator with index-based lookup:
```python
        vr_result, excerpts_with_items = verification_result

        vi_by_index: dict[int, VerificationItem] = {
            vi.item_index: vi for vi in vr_result.items
        }

        excerpt_to_vi: dict[int, list[tuple[VerificationItem, str]]] = {}
        item_index = 0
        for exc, items in excerpts_with_items:
            vis: list[tuple[VerificationItem, str]] = []
            for item in items:
                vi = vi_by_index.get(item_index)
                if vi is not None:
                    vis.append((vi, item["verification_type"]))
                else:
                    logger.warning(
                        "Missing verification item %d for excerpt %s",
                        item_index, exc.excerpt_id,
                    )
                item_index += 1
            excerpt_to_vi[exc.unit_index] = vis
```

**Tests (2 new):**

1. `test_verification_items_matched_by_index_not_position`: Mock LLM returns items in reverse order. Verify correct pairing.
2. `test_missing_verification_item_logged`: Mock returns 1 of 2 items. Verify warning + remaining item correctly matched.

---

## Fix 6: _parse_self_containment matches substring in wrong order

**Severity:** LOW-MEDIUM — "DEPENDENT (partially)" returns PARTIAL

**File:** `phase3_consensus.py`, `_parse_self_containment()` lines 490–498

**Fix:** Exact match first, then pick most conservative on substring conflict:
```python
def _parse_self_containment(text: Optional[str]) -> Optional[SelfContainmentLevel]:
    if text is None:
        return None
    text_upper = text.strip().upper()
    for level in SelfContainmentLevel:
        if text_upper == level.value:
            return level
    _LEVEL_ORDER = {
        SelfContainmentLevel.FULL: 2,
        SelfContainmentLevel.PARTIAL: 1,
        SelfContainmentLevel.DEPENDENT: 0,
    }
    matches = [level for level in SelfContainmentLevel if level.value in text_upper]
    if matches:
        return min(matches, key=lambda l: _LEVEL_ORDER.get(l, 1))
    return None
```

**Tests (3 new):**

1. `test_parse_ambiguous_picks_most_conservative`: "DEPENDENT (partially)" → DEPENDENT.
2. `test_parse_exact_match_preferred`: "FULL", "PARTIAL", "DEPENDENT" → exact.
3. `test_parse_both_in_text`: "This is PARTIAL, not FULL" → PARTIAL.

---

## Fix 7: Gate entry missing assessments (SPEC deviation)

**Severity:** MEDIUM — owner cannot properly resolve human gates

**Root cause:** SPEC §7.3.4 says gate entries include `context.assessments` (list of all model assessments with reasoning). Code's `_build_gate_entry()` only stores a single `context.attribution` dict with the enrichment model's values. For EX-G-001 (3 models disagree), the owner needs all 3 opinions to choose. For EX-G-003 (school conflict), the owner needs both models' school values.

**File:** `phase3_consensus.py`, `_build_gate_entry()` lines 595–619

**Fix:** Accept an optional `assessments` parameter and include it:
```python
def _build_gate_entry(
    excerpt: ExcerptRecord,
    gate_code: str,
    source_metadata: dict[str, str],
) -> dict[str, object]:
    import datetime

    # Build assessments from consensus_metadata if available
    assessments: list[dict[str, str]] = []
    if excerpt.consensus_metadata:
        for d in excerpt.consensus_metadata.decisions:
            assessments.append({
                "decision_type": d.decision_type,
                "enrichment_value": d.enrichment_value,
                "verifier_value": d.verifier_value or "",
                "escalation_value": d.escalation_value or "",
                "final_value": d.final_value,
                "resolution_method": d.resolution_method,
            })

    return {
        "excerpt_id": excerpt.excerpt_id,
        "gate_code": gate_code,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "context": {
            "primary_text_snippet": excerpt.primary_text[:200],
            "assessments": assessments,
            "source_metadata": source_metadata,
            "self_containment": excerpt.self_containment.value,
            "school": excerpt.school,
            "attribution": {
                "layer_id": excerpt.primary_author_layer.layer_id,
                "author_id": excerpt.primary_author_layer.author_id,
                "rule_applied": excerpt.primary_author_layer.rule_applied,
            },
        },
        "status": "pending",
    }
```

**Tests (2 new):**

1. `test_gate_entry_contains_assessments`: Excerpt with consensus_metadata → gate entry has non-empty `assessments` list.
2. `test_gate_entry_assessments_contain_all_models`: EX-G-001 gate → assessments contain enrichment_value, verifier_value, and escalation_value.

---

## Fix 8: (Absorbed into Fix 1a — ordering of consensus_metadata vs _repair_context_hint)

See Fix 1a above. No separate tests needed — Fix 1's roundtrip tests cover this.

---

## Read First

| File | Lines | What |
|------|-------|------|
| `phase3_consensus.py` | 226–231 | `resolve_consensus` ordering — Fix 1a |
| `phase3_consensus.py` | 501–536 | `_repair_context_hint` — Fix 1b |
| `phase3_consensus.py` | 284–293 | `_resolve_school` — Fix 2a |
| `phase3_consensus.py` | 575–587 | `check_gate_triggers` — Fix 2b |
| `phase3_enrichment.py` | 370–380 | Chunk matching — Fix 3 |
| `phase3_consensus.py` | 640–648 | Chunk matching — Fix 3 |
| `phase3_consensus.py` | 332–347 | `_resolve_attribution` — Fix 4 |
| `phase3_consensus.py` | 714–726 | Verification item mapping — Fix 5 |
| `phase3_consensus.py` | 490–498 | `_parse_self_containment` — Fix 6 |
| `phase3_consensus.py` | 595–619 | `_build_gate_entry` — Fix 7 |
| `contracts.py` | 534–566 | I-ER-4 validator |
| `contracts.py` | 435–530 | ExcerptRecord + AuthorAttribution |
| `tests/conftest.py` | all | Test factories |

## Do NOT Do

1. **Do NOT modify `contracts.py`.** All fixes in implementation files.
2. **Do NOT modify existing tests.** Only ADD new tests.
3. **Do NOT change consensus resolution logic** — fix APPLICATION of decisions.
4. **Do NOT run self-review.** Architect reviews after you push. Just run pytest.

## Verification

1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → **≥ 467 passed** (437 + 30 new), 0 failed
2. `grep -c "def test_" engines/excerpting/tests/test_phase3_consensus.py` → ≥ 59 (was 33, +26)
3. `grep -c "def test_" engines/excerpting/tests/test_phase3_enrichment.py` → ≥ 29 (was 27, +2)
4. **Fix 1 acid:** `test_full_to_partial_roundtrip_valid` → `ExcerptRecord.model_validate(updated.model_dump())` MUST NOT raise.
5. **Fix 4 acid:** `test_majority_different_from_enrichment_applied` → `result.primary_author_layer.author_id == "sch_b"`.
6. `grep -n "startswith" phase3_enrichment.py phase3_consensus.py` → 0 in chunk matching.
7. All 437 existing tests still pass.

## After This

Architect reviews fixes in a new chat (Round 2 + Round 3). Session 5 NEXT.md backed up at `reference/archive/sessions/NEXT_session5_original.md`.
