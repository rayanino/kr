# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Verify no knowledge corruption paths exist in the normalization engine SPEC.** The PRECISION session reduced defects from 46 HIGH to 6 HIGH (all MISSING_EXAMPLE), fixed all vague quantifiers, added 4 Arabic text examples, updated contracts.py with §4.B.5 and §4.B.7 models. Now verify that no processing rule can silently corrupt the library.

## What to Read

1. `engines/normalization/SPEC.md` — **Focus on §4.A (core processing), §5 (validation), §7 (error handling).** Look for paths where data is modified without validation.
2. `engines/normalization/contracts.py` — verify models match SPEC §2/§3 exactly.
3. `KNOWLEDGE_INTEGRITY.md` — the threat model. Apply it to normalization.

**Do NOT read:** VISION.md, source engine SPEC, CREATIVE_MANDATE.md, CHALLENGE_PROTOCOL.md.

## The Hardening Work (follow this sequence)

### Phase 1: Threat enumeration
For each §4.A processing step, ask: "What happens if this step produces wrong output?" Enumerate every path where:
- Text could be silently lost (characters dropped, pages skipped)
- Text could be silently modified (diacritics altered, whitespace mangled)
- Attribution could be wrong (layer misattribution, footnote misclassification)
- Structure could be wrong (heading missed, hierarchy inverted)
- Metadata could be lost (D-023 pass-through failure)

### Phase 2: Validate error coverage
For each threat from Phase 1, verify:
- Is there a validation check in §5 that catches it?
- Is there an error code in §7 that reports it?
- Is there a human gate trigger that flags it?
If any threat has no detection mechanism, add one.

### Phase 3: Add remaining examples
The SPEC still needs examples for: §4.A.3, §4.A.7, §4.B.1, §4.B.2, §4.B.3, §4.B.4.
Add at least 2 more (targeting §4.B.1 and §4.B.4 — highest corruption risk).

### Phase 4: Final quality checks
```
python3 scripts/check_spec_quality.py engines/normalization/SPEC.md --verbose
python3 scripts/creative_verification.py engines/normalization/SPEC.md
```

## Definition of Done

1. Every §4.A processing step has an identified failure mode with detection mechanism
2. `check_spec_quality.py` reports ≤6 HIGH defects (maintained)
3. `creative_verification.py` maintains ≥85/100 (currently 90)
4. ≥2 additional Arabic text examples added
5. NEXT.md written for IMPL_PREP session (normalization engine)
6. SESSION_LOG.md updated
7. Committed and pushed

## What the Previous Sessions Did

Source engine complete (4 sessions): CREATIVE → PRECISION → HARDENING → IMPL_PREP.
Normalization engine session 1 (CREATIVE): 3 new §4.B capabilities (§4.B.5–§4.B.7).
Normalization engine session 2 (PRECISION, this session):
- HIGH defects: 46 → 6. All vague quantifiers, "etc.", missing thresholds fixed.
- 4 Arabic text examples added (Shamela normalizer, multi-layer detection, structure discovery, content flagging).
- contracts.py updated with ContentCensus and TahqiqTopology models.
- SPEC: 902 → 1013 lines.

## Pending Owner Questions

- **API keys:** Not needed for preparatory work. Will be needed when Claude Code starts implementation.
