# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Make the normalization engine SPEC machine-implementable.** The CREATIVE session added 3 new transformative capabilities (§4.B.5–§4.B.7) and the SPEC now has 7 §4.B capabilities total (score: 90/100). However, the SPEC has 51 defects (46 HIGH) — mostly vague language, missing thresholds, and unbounded quantifiers from both old and new content.

## What to Read

1. `engines/normalization/SPEC.md` — **ALL sections.** You are polishing this.
2. `engines/normalization/contracts.py` — machine-readable truth. Update to match any §2/§3 changes.
3. `reference/DOMAIN.md` — for Arabic terminology verification (use `python3 scripts/extract_vision_sections.py 2` for glossary).

**Do NOT read:** VISION.md, source engine SPEC, CREATIVE_MANDATE.md, ENTRY_EXAMPLE.md, CHALLENGE_PROTOCOL.md.

**Budget:** ~10K tokens on reading. ~60K tokens on precision work. ~10K tokens on handoff.

## The Precision Work (follow this sequence)

### Phase 1: Run quality baseline
```
python3 scripts/check_spec_quality.py engines/normalization/SPEC.md --verbose
```
Record: "Baseline: X HIGH defects." Categorize defects by section.

### Phase 2: Fix §4.A defects first (core processing must be pristine)

The 46 HIGH defects include vague quantifiers ("many", "some", "few", "multiple"), missing thresholds ("high confidence"), unbounded etc., and handwave analysis. Fix each by:
- Replace "many" with specific counts or "≥N" thresholds
- Replace "high confidence" with numeric thresholds (e.g., ≥0.85)
- Replace "etc." with complete lists
- Replace "using content analysis" with specific algorithm names

### Phase 3: Add Arabic text examples to §4.A

Each normalizer (at minimum the Shamela normalizer §4.A.2) should have at least one concrete example showing:
- Input: actual HTML snippet from a Shamela export
- Output: the corresponding normalized content unit fields

### Phase 4: Verify §4.B new capabilities (§4.B.5–§4.B.7)

The three new capabilities already have concrete examples. Check:
- Are all field names consistent with contracts.py?
- Are all thresholds explicit?
- Could Claude Code implement each algorithm without questions?
- Do error cases have defined handling?

### Phase 5: Update contracts.py

Add any new fields from §4.B.5 (content_census manifest fields) and §4.B.7 (tahqiq_topology manifest fields) to the Pydantic models.

### Phase 6: Run final quality check
```
python3 scripts/check_spec_quality.py engines/normalization/SPEC.md --verbose
python3 scripts/creative_verification.py engines/normalization/SPEC.md
```

## Definition of Done

1. `check_spec_quality.py` reports ≤6 HIGH defects (down from 46)
2. `creative_verification.py` maintains ≥85/100 (currently 90)
3. ≥3 Arabic text examples added (input → output pairs)
4. Every threshold in §4.A has an explicit numeric value
5. Every "etc." replaced with complete list
6. contracts.py updated with new §4.B.5 and §4.B.7 fields
7. NEXT.md written for HARDENING session
8. SESSION_LOG.md updated
9. Committed and pushed

## What the Previous Sessions Did

Source engine complete (4 sessions): CREATIVE → PRECISION → HARDENING → IMPL_PREP.
Normalization engine session 1 (CREATIVE, this session):
- 3 new §4.B capabilities: Content Census (§4.B.5), Adaptive OCR Orchestration (§4.B.6), Tahqiq Apparatus Topology (§4.B.7)
- §4.B score: 75 → 90/100. Capabilities: 4 → 7.
- 8+ web searches on Arabic OCR landscape (Baseer, PaddleOCR-VL 1.5, QARI-OCR, KITAB-Bench, Granite-Docling)
- RESOURCES.md updated with 6 new technology entries
- Total SPEC: 665 → 902 lines

## Pending Owner Questions

- **API keys:** Not needed for preparatory work. Will be needed when Claude Code starts implementation.
