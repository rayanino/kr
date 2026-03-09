# NEXT — Source Engine Core SPEC (Step 1)

**Session type:** SPEC
**Goal:** Produce a core-only source engine SPEC at architecture-decision depth. Claude Code must be able to build the source engine from this SPEC with zero clarifying questions.

---

## What to read first

1. `skills/shared/ENGINE_PROTOCOL.md` — Step 1 section (SPEC requirements)
2. `engines/source/SPEC.md` — Current full SPEC (~1,140 lines). Read §4.A only.
3. `reference/CORE_CONTRACT_CLASSIFICATION.md` — Source engine section (27 core classes, 18 deferred)
4. `reference/TRACER_FINDINGS.md` — Source→normalization boundary issues
5. `engines/source/contracts.py` — The actual Pydantic models (825 lines)

## What NOT to read

- VISION.md — not needed
- kr_decisions.md — not needed
- Other engine SPECs — not needed
- §4.B of the source SPEC — these are deferred

---

## The work

### 1. Core vs. Deferred classification
Draw the line in the existing source SPEC:
- **Core:** Format detection (shamela_html + plain_text only), metadata extraction, metadata inference (LLM), freezing, deduplication, registration, trust evaluation
- **Deferred:** Citation network discovery, cross-validated scholar bootstrapping, source difficulty prediction, tahqiq apparatus fingerprinting, edition comparison, all formats except shamela_html and plain_text

Move all deferred content to a single "Deferred to Stage 2" section. Add extension hooks per ENGINE_PROTOCOL.

### 2. Assess SPEC maturity
The source SPEC has been through CREATIVE and partial PRECISION sessions. §4.A likely has vague language and missing concrete examples. The tracer bullet revealed 15 field-level mismatches between what the SPEC implies and what the contracts require — verify these are addressed.

### 3. Write core §4.A to architecture-decision depth
For each processing rule, verify you can write a function signature + 5-15 lines of pseudocode. Key areas:
- **Shamela HTML extraction:** Exact extraction rules for info.html fields (the tracer stub has working code)
- **Plain text handling:** What metadata can be inferred from plain text with no structural markup
- **LLM metadata inference:** What model, what prompt, what structured output schema, what fallback
- **Freezing:** Exact file operations, hash computation, immutability guarantees
- **Deduplication:** Composite key definition, what triggers human review vs. auto-reject
- **Trust evaluation:** Factor weights, scoring formula, tier thresholds

### 4. Verify contract alignment
The tracer bullet fixed contract mismatches. Verify the SPEC describes the ACTUAL contract fields:
- ScholarReference: `canonical_id`, `name_arabic`, `confidence`, `source_of_identification`
- TextLayer: `layer_type`, `author` (ScholarReference)
- TrustworthinessFactor: `name`, `weight`, `score`, `reason`
- InferredFieldConfidence: `genre`, `science_scope`, `structural_format`, `authority_level`
- MetadataHistoryEntry: `field`, `old_value`, `new_value`, `changed_by`, `timestamp`

---

## Done when

- [ ] Core SPEC passes the depth test: every §4.A rule → function signature + pseudocode
- [ ] All §4.B content deferred with extension hooks
- [ ] Contract field names in SPEC match contracts.py exactly
- [ ] SPEC addresses all source→normalization boundary findings from TRACER_FINDINGS.md
- [ ] Owner sanity check questions prepared (experiential review)
