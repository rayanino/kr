# Pre-Batch Verification Plan: Source Engine Final Hardening

## Rationale

Every verification layer in the source engine's history found bugs the previous
layer missed. Code audit caught what tests missed. LLM runs caught what audit
missed. Scale testing caught what small runs missed. Adversarial review caught
what evaluation missed. The cheapest, most productive bug-finding happens
*before* any books are processed — not during.

This plan exhausts every zero-cost verification method before spending a single
euro on LLM calls.

---

## Already-Discovered Issues (from this session's analysis)

### mypy: 37 type errors across 9 files

Run: `mypy engines/source/src/ --ignore-missing-imports --explicit-package-bases`

**Crash risks (must fix):**
- `consensus.py:110,113` — accesses `.base_work_title` / `.base_work_author` on
  a potentially-None `genre_chain_output` without null check. Would crash on any
  book without a genre chain.
- `engine.py:611,612` — `gate_error.field` is `Optional[str]` but passed to
  `gate_low_confidence()` which expects `str`. The new Fix 2 handler at line 626
  uses `data_for_validation.get("genre", "hashiyah")` which is safe, but the
  existing `confidence_threshold` handler at line 611 passes `gate_error.field`
  directly — could pass None.

**Contract mismatches (should fix):**
- `scholar_registry.py:99,147` — Missing required fields when constructing
  `ScholarAuthorityRecord`. Runtime Pydantic fills defaults, but the type
  contract is violated.
- `scholar_registry.py:109` — assigns arbitrary string to a `Literal[...]` field.
- `engine.py:458` — Missing required fields for `SourceMetadata` construction.
- `engine.py:183` — Missing `base_work_id` for `GenreChain` construction.
- `work_registry_store.py:46,69` — Missing `citation_count` for `WorkRegistryEntry`.

**Type narrowing (low risk but messy):**
- `metadata_inference.py:297,301` — Dict values typed as `float | None` where
  `float` expected. Runtime-safe but imprecise.
- `metadata_inference.py:475` — `agreement_fn` type mismatch (InferenceOutput vs
  BaseModel). Works via duck typing.

### SPEC quality: 34 HIGH defects

Run: `python3 scripts/check_spec_quality.py engines/source/SPEC_CORE.md`

Mostly vague quantifiers ("some", "multiple"), unbounded lists ("etc."), and
missing thresholds ("low confidence"). These are documentation quality issues
that predate the 4 fixes. They don't affect runtime behavior but indicate
ambiguity the implementation may have interpreted differently from intent.

**Action:** Triage — which defects affect correctness vs. which are stylistic.
Fix correctness-relevant ones. Note the rest in reference/OPEN_PROBLEMS.md for future
cleanup.

### Metadata flow: 22 fields at source→normalization boundary

Run: `python3 scripts/verify_metadata_flow.py`

The normalization engine expects 25 input fields; the source engine produces 6
(per the static analysis script). Most are likely false positives from the
script matching enum value names as field names (e.g., "shamela_html",
"commentary", "prose" are SourceFormat/StructuralFormat enum values, not
separate fields). But this needs manual verification.

**Action:** For each flagged field, determine: is this a real gap or a false
positive? Pay special attention to: `genre`, `source_format`,
`structural_format`, `multi_layer`, `volume_count`, `layers` — these sound like
real contract fields the normalization engine would need.

### Data mining of 204-book Phase D results

**Genre distribution:** 15 genre=other books. Only 1 (ملء العيبة) caused by
missing enum. 14 are genuine "other" or were classified by the non-canonical
model. After Fix 1, only ملء العيبة changes on a re-run.

**Fix 2 target confirmed:** النكت على شرح النووي — hashiyah, is_multi_layer=False,
0 layers. This is the exact book Fix 2 targets. 3 other hashiyah books all have
proper layers.

**Fix 3 scope:** 7 books have single-model death dates. 2 show the CA precision
fabrication pattern (century → specific year). Fix 3 would flag all 7 for
review.

**Cross-book consistency:** 15 authors appear in multiple books. All have
consistent death dates (all None — death dates stored in scholar registry, not
result.json).

**Flag rate:** 68/204 (33%) flagged. All solely for trust score < 0.65.

---

## Five Verification Layers

### Layer 1 — Fix mypy type errors (€0, Claude Code)

**Priority:** HIGH — the consensus.py None-access bug is a latent crash.

Fix the crash risks first (consensus.py, engine.py gate handler). Then fix the
contract mismatches (missing required fields at construction). Low-risk type
narrowing issues can be deferred.

**Exit criteria:** `mypy engines/source/src/ --ignore-missing-imports
--explicit-package-bases` produces 0 errors on the crash-risk and
contract-mismatch categories. Remaining type narrowing issues documented.

**Test suite must still pass after fixes:** `pytest engines/source/tests/ -v`

### Layer 2 — Contract boundary verification (€0, Claude Chat + Claude Code)

**Priority:** HIGH — determines whether the batch output is actually consumable.

Verify the source engine's actual output schema against normalization engine
expectations:

1. Does the normalization engine import `Genre` from source contracts? → YES
   (confirmed: `from engines.source.contracts import SourceFormat, SourceMetadata`
   in dispatcher.py). No genre-conditional logic found in normalization code.
   New `rihlah` and `usul_al_fiqh` values should pass through without issue.

2. Where does the normalization engine read death dates? → From scholar registry
   or from SourceMetadata? Need to check normalization SPEC.

3. Do any of the 4 new fields (death_date_single_model, needs_review_fields
   additions) need to be consumed downstream? → Probably not — they're
   review-assistance metadata, not content metadata. But verify.

4. Resolve the 22 false-positive-suspected metadata flow warnings. For each:
   is it an enum value being matched as a field name, or a real missing field?

**Exit criteria:** A written list of confirmed real gaps (if any) with resolution
plan. All false positives documented.

### Layer 3 — SPEC consistency audit after fixes (€0, Claude Chat)

**Priority:** MEDIUM — prevents SPEC drift that causes future misimplementation.

The 4 fixes modified SPEC_CORE.md in several places. Verify:

1. **Genre enum list in SPEC matches code.** Fix 1 added rihlah and usul_al_fiqh
   to the prompt and contracts. Does the SPEC's genre list (if any) match?

2. **Check 5e description matches the split code.** Fix 2 split check 5e into
   5e (sharh warning) and a new hashiyah-specific gate. Does the SPEC describe
   this split correctly?

3. **Death date warning described in SPEC.** Fix 3 added check 5g. Verify the
   SPEC has a section for it and the description matches the implementation.

4. **No stale references.** The BUG-05 fix downgraded check 5c from gate to
   warning, but SPEC had stale references. Check if any new stale references
   were introduced by the 4 fixes.

5. **34 HIGH SPEC defects triage.** Which affect correctness? Which are style?

**Exit criteria:** SPEC_CORE.md is consistent with the codebase. Stale references
fixed. Correctness-relevant SPEC defects addressed.

### Layer 4 — Targeted end-to-end fix validation (~€1.50-2.00, 4-5 books)

**Priority:** HIGH — fixes have unit tests but zero end-to-end validation.

Run these specific books through the fixed pipeline:

| Book | Tests Fix | Expected Change |
|------|-----------|----------------|
| ملء العيبة (vol 5) | Fix 1 | genre: other → rihlah |
| النكت على شرح النووي | Fix 2 | warning → human gate (abort with checkpoint) |
| أساليب بلاغية | Fix 3 | death_date_hijri appears in needs_review_fields |
| صحيح البخاري (control) | None | Identical to Phase D result |
| One usul_al_fiqh book (إعلام الموقعين ط العلمية) | Fix 1 | If CA returns usul_al_fiqh, it maps correctly |

**Cost:** ~€0.30-0.40 per book × 5 = ~€1.50-2.00

**Exit criteria:** Each fix produces the expected behavioral change. Control book
matches Phase D. No unexpected regressions.

### Layer 5 — Batch design decisions (€0, Claude Chat + owner)

**Priority:** Must resolve before batch.

**Book selection:**
- How many? ~50 is the current plan.
- Which? New unseen books that exercise normalization engine challenges:
  multi-volume, multi-layer, versified, different genres.
- Should the selection cover genres/formats underrepresented in Phase D?
  (Only 1 sirah, 2 tarikh, 2 mujam, 0 rihlah post-fix, 0 usul_al_fiqh post-fix)

**Downstream consumption:**
- Does the normalization engine use only the batch results, or also Phase D?
- If both: the 204 Phase D books were processed with the OLD code. Fix 1 would
  change ملء العيبة's genre. Fix 3 would add needs_review flags to 7 books.
  Do we re-run affected books or accept Phase D results as-is?

**Flag rate at scale:**
- 33% at 204 → projected ~830 flagged at 2,519.
- Is trust score thresholding working correctly, or is 0.65 too aggressive?
- Should we investigate before the batch?

**Re-run scope:**
- The 3-4 books affected by the fixes (ملء العيبة, النكت, usul_al_fiqh books):
  re-run through fixed pipeline or accept Phase D results?

---

## Execution Order

```
Layers 1-3 (parallel, €0):
  ├── Claude Code: fix mypy crash risks + contract mismatches (Layer 1)
  ├── Claude Chat: contract boundary verification (Layer 2)
  └── Claude Chat: SPEC consistency audit (Layer 3)
         │
         ▼
Layer 4 (~€1.50-2.00):
  Run 4-5 targeted books through fixed pipeline
         │
         ▼
Layer 5 (€0):
  Finalize batch design decisions
         │
         ▼
Final batch (~€5-10):
  Run ~50 new books per ENGINE TRANSITION rule
```

Total pre-batch cost: ~€1.50-2.00
Batch cost: ~€5-10
Combined: ~€7-12 (well within ~€70 remaining)

---

## Layer 1 — COMPLETE (commit 56dbe61)

**mypy result:** `Success: no issues found in 39 source files`
**pytest result:** `511 passed in 10.69s`

### Fixes applied (9 files, 22 insertions, 19 deletions):
- Fix 1: config.py `_load_json → Any` return type (4 errors)
- Fix 2: validation.py `current: Any` variable type (1 error)
- Fix 3: scholar_authority.py `if→elif` + rename `merged→merged_dict` (2 errors)
- Fix 4: shared consensus.py `Exception→BaseException` (1 error)
- Fix 5: source consensus.py None-narrowing assert (2 errors)
- Fix 6: scholar_registry.py:109 `type: ignore[assignment]` (1 error)
- Fix 7: metadata_inference.py `dict[str, float|None]` return + downstream `build_needs_review` (3 errors)
- Fix 8: metadata_inference.py:475 `type: ignore[arg-type]` (1 error)
- Fix 9: engine.py `field_name = gate_error.field or "unknown"` (2 errors)
- Pydantic suppressions: 6 sites across 4 files (21 errors)

### Handoff gap found:
My handoff missed that `build_needs_review` (line 356) also needed `dict[str, float|None]`
to match the widened return type of `apply_confidence_caps`. Claude Code caught this
independently. Lesson: trace ALL consumers of a function whose signature changes.
