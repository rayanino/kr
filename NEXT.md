# NEXT — Step 3 Bug Fixes (Claude Code)

## Status: Bug List COMPLETE → Claude Code Fixes All Bugs

The exhaustive bug identification is done. `STEP3_FINAL_BUG_LIST.md` contains 7 bugs (3 must-fix, 2 should-fix, 2 nice-to-have deferred). All decisions are made. No ambiguity remains.

---

## Your Task

Fix BUG-01 through BUG-05 in the order specified below. BUG-06 and BUG-07 are deferred to post-Step-4.

**Read `STEP3_FINAL_BUG_LIST.md` first.** Every bug has: root cause with file + line numbers, data evidence, and a specific proposed fix. Follow the proposed fixes — they have been verified against the code and data.

---

## Implementation Order

### 1. BUG-01 Part 1 — Fix school_affiliations key names

**Files:** `engines/source/src/engine.py`, `engines/source/src/registries/scholar_registry.py`

- `engine.py` lines 340–346: pass the full LLM `school_affiliations` dict to registration instead of extracting one school name value.
- `scholar_registry.py` `lookup_or_register_author`: change parameter from `school: Optional[str]` to `school_affiliations: Optional[dict]`. Store the dict directly on new records. For the `lookup()` call, extract one school value from the dict values (maintains interface compatibility).
- Update all callers of `lookup_or_register_author` to pass the new parameter.

### 2. BUG-01 Part 2 — Downgrade check 5c to warning

**File:** `engines/source/src/validation.py` line 197

- Change `severity="gate"` to `severity="warning"` for the `consistency_author_science` check.
- That is it. One word change. The check still fires, still populates `needs_review_fields`, just does not abort the pipeline.

### 3. BUG-05 — Fix genre/ML impossible state

**File:** `engines/source/src/validation.py` lines 232–244

- Make check 5e conditional: only auto-correct `is_multi_layer=True` when `text_layers` is non-empty.
- When genre is sharh/hashiyah but layers are empty, emit a warning and add both `genre` and `is_multi_layer` to `needs_review_fields`, but do NOT auto-correct.

### 4. BUG-03 — Add tahqiq-note override

**File:** `engines/source/src/validation.py` (new check, after existing checks)

- Add a post-validation rule:
  ```
  IF is_multi_layer == true
     AND all layer types in text_layers are in {matn, tahqiq_note}
  THEN auto-correct is_multi_layer to false
       AND clear text_layers
       AND log correction as "tahqiq_note_override"
  ```
- Do NOT require muhaqiq presence (1/4 known false positives has no muhaqiq in extraction).
- The layer-type pattern alone is sufficient — all real sharh/hashiyah books have sharh/hashiyah layer types.

### 5. BUG-02 — Verify author confidence end-to-end

**Files:** `engines/source/src/engine.py`, `engines/source/contracts.py`

- FIX-C04 (commit `2760f62`) already added `confidence_scores.author` to `InferredFieldConfidence`. Verify this field is populated correctly by running 2–3 test books.
- `result.author.confidence` (from `ScholarReference`) remains the registry match score. Document this distinction clearly in the ScholarReference docstring: `confidence` = registry match score (1.0 for new records), NOT LLM identification confidence. Downstream engines must use `confidence_scores.author` for identification confidence.

### 6. BUG-04 — Add death_date_source tracking

**Files:** `engines/source/contracts.py`, `engines/source/src/metadata_inference.py`, `engines/source/src/registries/scholar_registry.py`

- Add `death_date_source` field to `ScholarAuthorityRecord` with values: `extraction`, `author_raw_text`, `inference`, `absent`.
- In `metadata_inference.py`: after mapping author fields, determine death_date_source by checking whether the death date value appears in any extraction field (`author_name_raw`, etc.).
- Pass through to scholar registration.

---

## After Fixing

1. Run the full test suite. All existing tests must pass.
2. Run 5–10 books end-to-end via `scripts/run_phase_c.py` (or a similar script) as a smoke test:
   - Verify BUG-01 fix: books that previously gate_abort now succeed
   - Verify BUG-03 fix: tahqiq-note books get ML auto-corrected to false
   - Verify BUG-05 fix: genre=hashiyah with empty layers emits warning, not gate error
3. Update `CLAUDE.md` with the new validation state.
4. Commit with a descriptive message listing all bug IDs fixed.

---

## What NOT To Do

- Do NOT fix BUG-06 (genre taxonomy) or BUG-07 (consensus ML check) — deferred to post-Step-4.
- Do NOT plan Step 4. This session is scoped to bug fixes only.
- Do NOT modify SPEC_CORE.md (the check 5c severity change is an implementation-level decision that does not require a SPEC rewrite — the SPEC can be updated after Step 4 validates the decision).
- Do NOT re-run the full 73-book Phase C. A 5–10 book smoke test is sufficient.

---

## Governing Documents (read in this order)

1. **This file** (NEXT.md) — task directive
2. **STEP3_FINAL_BUG_LIST.md** — the complete bug list with evidence and fixes
3. **PHASE_C_ERRATA.md** — corrections discovered during evaluation
4. **SPEC_CORE.md** — behavioral authority
5. **engines/source/src/** — the code you are modifying
