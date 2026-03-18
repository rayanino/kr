# NEXT — Pre-build hardening: 2 findings from Architect deep review

## Current position: Probe 1 → Probe 2 transition APPROVED. 15 original findings fixed and verified. Architect deep review found 2 additional issues that must be resolved before build begins.
## What to do: Apply 2 targeted fixes (adversarial catalog annotations + consolidator confidence rules), then commit.
## Context: The Architect's self-review (using thinking-frameworks, critical-review, and adversarial probing) found that §4.B ADV cases outside ADV-035-042 lack deferred annotations (causing test engineer confusion during core build), and the consolidator's Step 2 is missing confidence handling for 4 of 5 agreement types (reducing reproducibility).
## Owner action needed: YES — after CC commits, start a new Claude Chat session for Probe 2 build prep (technology survey, module architecture, core-extraction classification).

---

## Read First (in this order)

1. `reference/SPEC_ADVERSARY_NORMALIZATION.md` (857L) — You will add deferred annotations at 2 locations.
2. `.claude/agents/consolidator.md` (197L) — You will add confidence handling rules to Step 2.

## Fixes

### FIX P — Deferred annotations for §4.B ADV cases outside ADV-035-042

**Problem:** Three ADV cases reference deferred §4.B capabilities but have no deferred annotation. The test engineer agent says "Every ADV-NNN case with a 'Detection' assertion should have a corresponding pytest test." During core build, the test engineer will encounter these cases, attempt to write tests for unimplemented capabilities, and either waste time or produce confusion.

**P1. Add deferred annotation to ADV-046 (§4.B.9, line 302).**

Before `### ADV-046`, insert:

```
> **NOTE:** ADV-046 targets §4.B.9 (Authorial Voice Fingerprint), a deferred capability. Implement this test when §4.B.9 is built. It is placed here (in the §4.A.5 section) because the fingerprint validates layer detection results from §4.A.5.

```

**P2. Add deferred annotation to §4.B.2 section (line 707).**

After the section header `## §4.B.2 — Structural Format Auto-Detection (T-3 defense)` and before `### ADV-043`, insert:

```
> **NOTE:** ADV-043 and ADV-044 target §4.B.2 (Structural Format Auto-Detection), which may be classified as core or deferred during build prep (core-extraction classification). If deferred, implement these tests when §4.B.2 is built. If core, implement during the build session that implements §4.B.2.

```

### FIX Q — Consolidator confidence handling for all agreement types

**Problem:** The consolidator's Step 2 specifies confidence for AGREEMENT_VERIFIED (`min(A_confidence, B_confidence)`) but not for AGREEMENT_PLAUSIBLE, AGREEMENT_FLAG, AGREEMENT_UNVERIFIABLE, or AGREEMENT_UNCERTAIN. The consolidator will need to improvise confidence for these cases, reducing reproducibility.

**Q1. Add confidence rules to all agreement types in Step 2.**

In `.claude/agents/consolidator.md`, replace the current Step 2 content (lines 49-53):

```
**AGREEMENT_VERIFIED:** Final verdict = VERIFIED. Confidence = min(A_confidence, B_confidence).
**AGREEMENT_PLAUSIBLE:** Final verdict = PLAUSIBLE. Both verifiers lacked strong evidence.
**AGREEMENT_FLAG:** Final verdict = FLAG. High priority for remediation.
**AGREEMENT_UNVERIFIABLE:** Final verdict = UNVERIFIABLE. Neither verifier found evidence. Not an error — it means the item cannot be independently confirmed.
**AGREEMENT_UNCERTAIN:** Final verdict = PLAUSIBLE. When one says PLAUSIBLE and the other says UNVERIFIABLE, upgrade to PLAUSIBLE (some evidence > no evidence).
```

with:

```
**AGREEMENT_VERIFIED:** Final verdict = VERIFIED. Confidence = min(A_confidence, B_confidence). Conservative — uses the weaker evidence assessment.
**AGREEMENT_PLAUSIBLE:** Final verdict = PLAUSIBLE. Confidence = min(A_confidence, B_confidence). Both verifiers lacked strong evidence — use the more cautious assessment.
**AGREEMENT_FLAG:** Final verdict = FLAG. Confidence = max(A_confidence, B_confidence). Both found problems — the stronger evidence drives the confidence in the flag. High priority for remediation.
**AGREEMENT_UNVERIFIABLE:** Final verdict = UNVERIFIABLE. Confidence = 0.5 (neutral baseline). Neither verifier found evidence for or against — confidence has no evidential grounding, so it defaults to neutral. Not an error — it means the item cannot be independently confirmed.
**AGREEMENT_UNCERTAIN:** Final verdict = PLAUSIBLE. Confidence = the PLAUSIBLE verifier's confidence. When one says PLAUSIBLE and the other says UNVERIFIABLE, upgrade to PLAUSIBLE (some evidence > no evidence). The evidence-holder's confidence is the only one with grounding.
```

## Do NOT Do

- Do NOT modify any other agent files. Only consolidator.md changes.
- Do NOT modify the SPEC. No engine source code changes.
- Do NOT renumber, reorder, or restructure existing ADV cases. Only add annotations.
- Do NOT modify the adversarial catalog's Summary by Threat table or header counts (they are still correct — annotations don't change case counts).
- Do NOT start building the normalization engine.

## Verification

After applying both fixes, run these 5 checks:

```bash
# 1. ADV-046 has deferred annotation
grep -B2 "^### ADV-046" reference/SPEC_ADVERSARY_NORMALIZATION.md | grep "NOTE"
# Expected: 1 line containing "NOTE" about §4.B.9

# 2. §4.B.2 section has deferred annotation
grep -A2 "^## §4.B.2" reference/SPEC_ADVERSARY_NORMALIZATION.md | grep "NOTE"
# Expected: 1 line containing "NOTE" about core or deferred

# 3. Case count unchanged
grep -c "^### ADV-" reference/SPEC_ADVERSARY_NORMALIZATION.md
# Expected: 51 (unchanged)

# 4. Consolidator has confidence rules for all 5 agreement types
grep "Confidence =" .claude/agents/consolidator.md | wc -l
# Expected: 5

# 5. Consolidator AGREEMENT_UNCERTAIN references PLAUSIBLE verifier's confidence
grep "AGREEMENT_UNCERTAIN" .claude/agents/consolidator.md | grep "evidence-holder"
# Expected: 1 line
```

## Commit Message

```
fix: 2 pre-build findings from Architect deep review

Adversarial catalog: added deferred annotations for ADV-043/044 (§4.B.2)
  and ADV-046 (§4.B.9) — prevents test engineer confusion during core build
  when these §4.B capabilities may not yet be implemented.
Consolidator: added explicit confidence handling rules for all 5 agreement
  types (was only specified for AGREEMENT_VERIFIED, leaving 4 types to
  improvisation).
```

## After This

Update NEXT.md to:

```
# NEXT — Probe 2 build prep (Architect session)

## Current position: Probe 1 COMPLETE. All 17 findings resolved (15 original + 2 from deep review). Transition gate APPROVED. Ready for Probe 2.
## What to do: Architect begins Probe 2 build preparation — technology survey, core-extraction classification, module architecture, MUST-FIX resolution, and first build session handoff.
## Owner action needed: YES — start a new Claude Chat session for Architect build prep.

Architect reads:
- reference/ENGINE_BUILD_BLUEPRINT.md §2a (Build Preparation)
- engines/normalization/SPEC.md (full — for core extraction classification)
- reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md (3 MUST-FIX items to resolve)
- engines/normalization/contracts.py (current state)
- engines/source/contracts.py (upstream boundary)

The Architect will:
1. Run kr-core-extract on the normalization SPEC (classify §4.A/§4.B as core vs deferred)
2. Resolve the 3 MUST-FIX items from the integrity audit (M-14, M-13, M-09)
3. Do the technology survey for core capabilities
4. Design module architecture and write stubs
5. Write CLAUDE.md for the normalization engine
6. Write Build Session 1 NEXT.md for Claude Code
```
