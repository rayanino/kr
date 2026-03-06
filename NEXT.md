# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Make the source engine SPEC implementation-ready.**

This is NOT a creative session. Do NOT invent new capabilities. This session exists for ONE purpose: eliminate every defect that would cause Claude Code to ask a clarifying question.

## What to Read

1. `engines/source/SPEC.md` — **ALL sections.** You are cleaning this.
2. `engines/source/contracts.py` — verify contracts match SPEC after your edits
3. `reference/ENTRY_EXAMPLE.md` — the quality target (refresh your understanding of what metadata the synthesizer needs)

**Do NOT read:** CREATIVE_MANDATE.md, other engine SPECs, VISION.md sections unrelated to source engine. Stay focused.

**Budget:** ~10K tokens on reading. ~60K tokens on precision edits. ~20K tokens on validation. ~10K tokens on handoff.

## The Precision Work (follow this sequence)

### Step 1: Run quality baseline
```
python3 scripts/check_spec_quality.py engines/source/SPEC.md --verbose
```
Record: "Baseline: X high-severity defects."

### Step 2: Fix all HIGH severity defects

The creative session (2026-03-06) left 41 high-severity defects. Most are in §4.A (the creative session did not touch §4.A). Categories:

- **MISSING_EXAMPLE (14 instances):** Every §4 subsection needs a worked example with real Arabic text. This is the biggest gap. Write concrete input→output examples for: §4.A.1 (identity model), §4.A.2 (acquisition workflow), §4.A.3 (metadata extraction), §4.A.6 (relevance evaluation), §4.A.7 (deduplication), §4.A.8 (trustworthiness), §4.A.9 (work relationships), §4.A.10 (status tracking).
- **VAGUE_QUANTIFIER (7 instances):** Replace "multiple", "many", "some" with specific numbers or bounded ranges.
- **UNBOUNDED_ETC (6 instances):** Replace "etc." with exhaustive lists or explicit scope.
- **UNVALIDATED (8 instances):** Ensure every write to disk has validation specified.
- **VAGUE_APPROPRIATE (2 instances):** Replace "appropriate" with specific criteria.

### Step 3: Verify contracts.py alignment

After editing the SPEC, check that `contracts.py` still matches:
- Any new fields added to §3 or §4.A must appear in the Pydantic models
- Any new enums must be defined
- The `compositional_profile` from §4.B.5 needs a Pydantic model
- The `edition_comparison` from §4.B.6 needs a Pydantic model
- The `genealogy_metadata` from §4.B.7 needs a Pydantic model

### Step 4: Run quality verification
```
python3 scripts/check_spec_quality.py engines/source/SPEC.md --verbose
python3 scripts/creative_verification.py engines/source/SPEC.md
```
Target: ≤10 high-severity defects (down from 41). §4.B score remains ≥85.

## Definition of Done

1. All MISSING_EXAMPLE defects resolved — every §4 subsection has a worked example
2. All VAGUE_QUANTIFIER defects resolved — no unbounded "many", "some", "multiple"
3. All UNBOUNDED_ETC defects resolved — no "etc." remains
4. `contracts.py` updated with new models for §4.B.5, §4.B.6, §4.B.7 output schemas
5. `check_spec_quality.py` reports ≤10 high-severity defects
6. `creative_verification.py` score remains ≥85
7. NEXT.md written for the next session (HARDENING for source engine)
8. SESSION_LOG.md updated
9. Committed and pushed

## What the Previous Session Did

CREATIVE session (2026-03-06): Added 3 new transformative §4.B capabilities to the source engine SPEC:
- §4.B.5: KITAB Text Reuse Integration for Source Compositional Profiling (uses KITAB passim dataset to show a source's place in the classical Arabic intertextual network)
- §4.B.6: Edition Comparison Intelligence (automated comparison of multiple editions of the same work, classifying divergences)
- §4.B.7: Scholarly Genealogy Auto-Construction (builds teacher-student chains using OpenITI + LLM inference + NetworkX graph analysis)

Updated RESOURCES.md with: KITAB text reuse statistics, passim algorithm, eScriptorium/Kraken, NetworkX.

§4.B score went from 75/100 → 90/100. 4 → 7 capabilities. 2 → 7 named technologies. Examples added (was none).

## Pending Owner Questions

- **API keys:** Will be needed for the IMPLEMENTATION_PREP session (after PRECISION + HARDENING). Not needed yet.
