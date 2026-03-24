# NEXT — Excerpting Session 4 Fixes (Corrected After CC Adversarial Audit)

## Current Position

- **Excerpting Phase 3.2 (LLM enrichment):** COMPLETE. 27 tests. 442 impl lines.
- **Excerpting Phase 3.3 (consensus verification):** COMPLETE. 33 tests. 767 impl lines.
- **Test baseline:** 437 passed, 2 skipped, 0 failed (excerpting)
- **Review status:** Round 1 BLOCKED — findings from architect review + CC adversarial audit

## What to Do

Fix bugs found during architect review (commit `4a7f71e9`) and independently confirmed by CC adversarial audit. Fixes are in `phase3_consensus.py` and `phase3_enrichment.py`. No changes to `contracts.py`.

After fixing: **≥ 465 passed tests** (437 + ≥28 new).

---

## Fix 1: Attribution majority winner NOT applied to excerpt [CRITICAL — T-2]

**Severity:** CRITICAL — silent wrong author attribution (T-2 epistemic corruption)
**Found by:** Architect (F-4) + CC audit (CC-F1). Independently confirmed with identical trace.

**Root cause:** In `_resolve_attribution()` (lines 332–347), when the 2-of-3 majority differs from the enrichment model's attribution, the code records the majority in `ConsensusDecision.final_value` but does NOT update `primary_author_layer`. The excerpt keeps the enrichment model's (outvoted) attribution.

SPEC §7.3.3 line 1844: "If 2 of 3 models agree → **use** the majority attribution."

**Empirically confirmed:** enrichment=sch_a, verifier=sch_b, escalation=sch_b → majority=sch_b. Output: `primary_author_layer.author_id` = "sch_a" (WRONG).

**Existing test `test_2_of_3_majority_wins` is tautological:** enrichment=sch_a, escalation=sch_a → majority=enrichment. Bug invisible.

**File:** `engines/excerpting/src/phase3_consensus.py`, `_resolve_attribution()` lines 332–347

**Fix:** When majority ≠ enrichment_val, update `primary_author_layer`:

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
2. `test_majority_same_as_enrichment_unchanged`: enrichment=sch_a, verifier=sch_b, escalation=sch_a → `author_id` stays "sch_a", `rule_applied` stays "LA-3".
3. `test_all_3_disagree_keeps_enrichment`: enrichment=sch_a, verifier=sch_b, escalation=sch_c → `author_id="sch_a"`, `confidence=0.0`.
4. `test_majority_sets_consensus_rule`: majority ≠ enrichment → `rule_applied == "LA-3_consensus"`.

---

## Fix 2: apply_enrichment produces I-ER-4 violation for PARTIAL units [HIGH — CRASH]

**Severity:** HIGH — crash on JSONL round-trip. REACHABLE code path.
**Found by:** CC audit (CC-F3). Confirmed by architect.

**Root cause:** `apply_enrichment()` (lines 279–302) sets `context_hint` from the LLM's `ue.context_hint` for PARTIAL units, then removes the `llm_enrichment_failed` exemption flag. If the LLM returns `context_hint=None` for a PARTIAL unit (omitting the field), the result is PARTIAL + `context_hint=None` + no exemption flag → I-ER-4 violation → crash on any `model_validate()` or JSONL round-trip.

**File:** `engines/excerpting/src/phase3_enrichment.py`, `apply_enrichment()` lines 279–302

**Fix:** Add a fallback when LLM returns None context_hint for PARTIAL:

```python
        # Determine context_hint: only for PARTIAL (I-ER-4)
        context_hint: Optional[str] = None
        if exc.self_containment == SelfContainmentLevel.PARTIAL:
            context_hint = ue.context_hint
            # Fallback: if LLM omitted context_hint, generate from notes
            if context_hint is None and exc.self_containment_notes:
                context_hint = exc.self_containment_notes
            # Last resort: generic hint (better than I-ER-4 crash)
            if context_hint is None:
                context_hint = "يحتاج سياقاً إضافياً لفهم المحتوى"
```

**Tests (3 new, in `test_phase3_enrichment.py`):**

1. `test_apply_partial_with_none_hint_uses_notes_fallback`: PARTIAL excerpt with `self_containment_notes="يعتمد على ما سبق"`. LLM returns `context_hint=None`. Assert result.context_hint == "يعتمد على ما سبق".
2. `test_apply_partial_with_none_hint_no_notes_uses_generic`: PARTIAL excerpt with `self_containment_notes="needed"` (exists but LLM hint is None and notes are present). Assert result.context_hint is not None. Then roundtrip: `ExcerptRecord.model_validate(result.model_dump())` MUST NOT raise.
3. `test_apply_partial_roundtrip_after_enrichment`: PARTIAL excerpt → apply_enrichment with LLM context_hint=None → roundtrip validation MUST NOT raise.

---

## Fix 3: EX-G-003 over-triggers when verifier agrees with source metadata

**Severity:** MEDIUM — human gate queue pollution
**Found by:** Architect (F-2)

**Root cause:** SPEC §7.3.4: "source_school conflicts with **both** models." Code checks `vi.alternative != excerpt.school` (verifier ≠ enrichment) instead of `vi.alternative != source_school` (verifier ≠ source).

### Fix 3a: `_resolve_school()` line 290

Change `vi.alternative != excerpt.school` to `vi.alternative != source_school`.

### Fix 3b: `check_gate_triggers()` lines 575–585

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
3. `test_check_gate_triggers_ex_g_003_respects_verifier`: consensus_metadata verifier_value=حنبلي, source=حنبلي → NOT triggered.
4. `test_check_gate_triggers_ex_g_003_both_conflict`: verifier=مالكي, source=حنبلي → triggered.

---

## Fix 4: Chunk matching via `startswith` false-matches similar div_ids

**Severity:** MEDIUM — latent bug for split chunks
**Found by:** Architect (F-3)

**Files:** `phase3_enrichment.py` lines 370–380 and `phase3_consensus.py` lines 640–648

**Fix (in BOTH files):**
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

1. `test_split_chunk_matched_correctly` (enrichment)
2. `test_split_chunk_consensus_matched_correctly` (consensus)

---

## Fix 5: Verification item mapping ignores item_index (positional fragility)

**Severity:** MEDIUM-HIGH — silent wrong consensus if LLM reorders
**Found by:** Architect (F-5) + CC audit (CC-F2). Independently confirmed.

**File:** `phase3_consensus.py` lines 714–726

**Fix:**
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

1. `test_verification_items_matched_by_index_not_position`: Reverse-ordered items → correct pairing.
2. `test_missing_verification_item_logged`: Partial response → warning logged.

---

## Fix 6: _parse_self_containment matches substring in wrong order

**Severity:** LOW-MEDIUM — "DEPENDENT (partially)" returns PARTIAL
**Found by:** Architect (F-6)

**File:** `phase3_consensus.py`, lines 490–498

**Fix:** Exact match first, then pick most conservative:
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
2. `test_parse_exact_match_preferred`: exact strings → exact matches.
3. `test_parse_both_in_text`: "This is PARTIAL, not FULL" → PARTIAL.

---

## Fix 7: Gate entry missing assessments list per SPEC §7.3.4

**Severity:** MEDIUM — owner cannot properly resolve human gates
**Found by:** Architect (F-7)

**File:** `phase3_consensus.py`, `_build_gate_entry()` lines 595–619

**Fix:** Include consensus assessments:
```python
def _build_gate_entry(
    excerpt: ExcerptRecord,
    gate_code: str,
    source_metadata: dict[str, str],
) -> dict[str, object]:
    import datetime

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

1. `test_gate_entry_contains_assessments`: consensus_metadata → assessments list non-empty.
2. `test_gate_entry_assessments_contain_all_models`: EX-G-001 → enrichment, verifier, escalation values present.

---

## Fix 8: consensus_metadata set AFTER _repair_context_hint reads it

**Severity:** MEDIUM — _repair_context_hint always sees None for consensus
**Found by:** Architect (F-8)

**File:** `phase3_consensus.py`, `resolve_consensus()` lines 226–231

**Fix:** Move consensus_metadata before _repair_context_hint:
```python
    # Set consensus_metadata FIRST — _repair_context_hint reads it
    if decisions:
        updates["consensus_metadata"] = ConsensusRecord(decisions=decisions)

    # Apply context_hint repair after all consensus decisions
    updates = _repair_context_hint(excerpt, updates)

    updates["review_flags"] = review_flags
```

Also remove the duplicate ConsensusRecord creation at line 234 (dead code):
```python
    updated = excerpt.model_copy(update=updates)
    # consensus_record already in updates; return None for backward compat
    return updated, None, gate_codes
```

**Tests (1 new):**

1. `test_repair_context_hint_reads_consensus_metadata`: Build updates dict with `consensus_metadata` containing a self_containment decision with `verifier_agrees=False`. Run `_repair_context_hint`. Verify the output references verifier reasoning (not just the generic fallback string).

---

## Fix 9: Phantom "unknown" voter in attribution escalation

**Severity:** LOW-MEDIUM — unnecessary EX-G-001 gates
**Found by:** CC audit (CC-F6). Confirmed by architect.

**File:** `phase3_consensus.py`, `_resolve_attribution()` line 330

**Root cause:** `verifier_val = vi.alternative or "unknown"` injects a phantom voter. When verifier disagrees but provides no alternative, "unknown" enters the 3-way vote, preventing legitimate 2-of-3 majorities and creating false 3-way disagreements.

**Fix:** Use `None` for missing alternative, and handle it in majority logic:
```python
        verifier_val = vi.alternative  # None if no alternative provided

        if escalation_value is not None:
            # Filter out None votes for majority calculation
            real_votes = [v for v in [enrichment_val, verifier_val, escalation_value] if v is not None]
            if len(real_votes) >= 2:
                majority = _find_majority_flexible(real_votes)
            else:
                majority = None
```

And add a flexible majority function:
```python
def _find_majority_flexible(votes: list[str]) -> Optional[str]:
    """Find majority among 2 or 3 real votes. Returns None if no majority."""
    from collections import Counter
    counts = Counter(votes)
    for val, count in counts.most_common():
        if count >= 2:
            return val
    return None
```

Also update `ConsensusDecision` to use `verifier_val or "abstained"` for the `verifier_value` field (for human-readable gate entries, not for vote logic).

**Tests (2 new):**

1. `test_verifier_no_alternative_does_not_block_majority`: enrichment=sch_a, verifier alternative=None, escalation=sch_a → majority=sch_a (not blocked by phantom).
2. `test_verifier_no_alternative_with_different_escalation`: enrichment=sch_a, verifier alternative=None, escalation=sch_b → no majority (2 real votes disagree) → EX-G-001 gate.

---

## Findings Downgraded / Noted

### Former F-1: FULL→PARTIAL/DEPENDENT repair is dead code
**Original severity:** HIGH (crash). **Revised:** NOT A BUG — unreachable path.
**Reason:** CC audit (CC-F5) proved `_needs_consensus` never triggers SELF_CONTAINMENT for FULL excerpts. No code path can downgrade a FULL excerpt's self_containment. The FULL→PARTIAL and FULL→DEPENDENT branches in `_repair_context_hint` are dead code.
**Action:** Leave the dead code branches as defensive code (they don't hurt). Remove tests that were designed for the dead path. The real crash is Fix 2 (CC-F3), not this.

### CC-F4: takhrij_data empty list→None coercion
**Severity:** LOW — semantic distinction lost ([] vs None), no crash.
**Action:** Not fixing now — downstream code handles None correctly.

### CC-F7: No school↔school_confidence cross-validation
**Severity:** LOW — semantically odd (school=None with confidence=0.85), no crash.
**Action:** Not fixing now — would require contracts.py modification.

---

## Read First

| File | Lines | What |
|------|-------|------|
| `phase3_consensus.py` | 332–347 | `_resolve_attribution` — Fix 1 |
| `phase3_enrichment.py` | 279–302 | `apply_enrichment` context_hint — Fix 2 |
| `phase3_consensus.py` | 284–293 | `_resolve_school` — Fix 3a |
| `phase3_consensus.py` | 575–587 | `check_gate_triggers` — Fix 3b |
| `phase3_enrichment.py` | 370–380 | Chunk matching — Fix 4 |
| `phase3_consensus.py` | 640–648 | Chunk matching — Fix 4 |
| `phase3_consensus.py` | 714–726 | Verification item mapping — Fix 5 |
| `phase3_consensus.py` | 490–498 | `_parse_self_containment` — Fix 6 |
| `phase3_consensus.py` | 595–619 | `_build_gate_entry` — Fix 7 |
| `phase3_consensus.py` | 226–234 | `resolve_consensus` ordering — Fix 8 |
| `phase3_consensus.py` | 330 | phantom voter — Fix 9 |
| `phase3_consensus.py` | 422–430 | `_find_majority` — Fix 9 |
| `contracts.py` | 534–566 | I-ER-4 validator |
| `contracts.py` | 435–530 | ExcerptRecord + AuthorAttribution |
| `tests/conftest.py` | all | Test factories |

## Do NOT Do

1. **Do NOT modify `contracts.py`.**
2. **Do NOT modify existing tests.** Only ADD new tests.
3. **Do NOT change consensus resolution logic** — fix APPLICATION of decisions.
4. **Do NOT run self-review.** Architect reviews after you push. Just run pytest.

## Verification

1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → **≥ 465 passed** (437 + 28 new), 0 failed
2. `grep -c "def test_" tests/test_phase3_consensus.py` → ≥ 49 (was 33, +16)
3. `grep -c "def test_" tests/test_phase3_enrichment.py` → ≥ 32 (was 27, +5)
4. **Fix 1 acid:** `test_majority_different_from_enrichment_applied` → `author_id == "sch_b"`.
5. **Fix 2 acid:** `test_apply_partial_roundtrip_after_enrichment` → `model_validate` MUST NOT raise.
6. `grep -n "startswith" phase3_enrichment.py phase3_consensus.py` → 0 in chunk matching.
7. All 437 existing tests still pass.

## After This

Architect reviews in a new chat (Round 2 adversarial + Round 3 verdict). Session 5 NEXT.md at `reference/archive/sessions/NEXT_session5_original.md`.
