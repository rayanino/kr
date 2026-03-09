# NEXT — Source Engine Step 1 (Continued) or Step 2

**Session type:** Owner review → then RESEARCH
**Goal:** Owner reviews SPEC_CORE.md experientially, then Claude researches the 7 marked assumptions.

---

## What happened last session

Step 1 Parts 1, 4, 5 completed:

1. **Core extraction** (CORE_VS_DEFERRED.md): 68 core / 32 deferred capabilities classified. Core formats: shamela_html + plain_text. All §4.B deferred with extension hooks.

2. **Core SPEC written** (SPEC_CORE.md): ~700 lines at architecture-decision depth. Includes pseudocode for: format detection, Shamela HTML extraction, plain text extraction, scholar matching score formula, slug generation, trust evaluation (deterministic factor scores), consensus agreement (including "new record" case), LLM output schema with required prompt elements.

3. **Integrity audit** (INTEGRITY_AUDIT.md): 11 defects found. 3 HIGH + 5 MEDIUM fixed in the SPEC. 7 assumptions marked for Step 2 testing.

4. **Owner sanity check** (OWNER_SANITY_CHECK.md): 10 experiential questions prepared.

---

## What to do now

### If the owner has reviewed OWNER_SANITY_CHECK.md:

1. Read the owner's answers.
2. For any ✗ answers: use `kr-spec-review` to investigate and resolve.
3. Update SPEC_CORE.md with any fixes.
4. Move to Step 2 (RESEARCH) — test the 7 marked assumptions.

### If the owner has NOT yet reviewed:

Per ENGINE_PROTOCOL: after 3 days with no comments, proceed to Step 2. Mark domain-dependent decisions as `[OWNER REVIEW PENDING]`.

---

## Step 2 Plan (when ready)

Test these 7 assumptions on the `html_export_minimal` and `alfiyyah_versified` fixtures:

| ID | What to Test | Method |
|----|-------------|--------|
| A1 | LLM genre inference ≥ 85% | Run inference prompt on both fixtures + manual test cases |
| A2 | LLM genre_chain inference ≥ 80% | Test with commentary titles |
| A3 | LLM multi-layer detection ≥ 90% | Test on multi-layer and single-layer fixtures |
| A4 | Two-model consensus effectiveness | Run same prompt through Claude + GPT, compare |
| A5 | Scholar matching score formula accuracy | Test with variant spellings |
| A6 | Trust evaluation weights/threshold correctness | Run on 5+ source scenarios |
| A7 | Name normalization sufficiency | Test with real Shamela name variants |

**Skills to use:** `kr-research` for the assumption testing.

---

## What to read

1. `engines/source/SPEC_CORE.md` — The core SPEC (primary document)
2. `engines/source/INTEGRITY_AUDIT.md` — Defects found and fixes applied
3. `engines/source/CORE_VS_DEFERRED.md` — Classification decisions
4. `engines/source/OWNER_SANITY_CHECK.md` — Questions for the owner
