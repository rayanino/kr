# Atomization Engine — محرك التذرير

**Responsibility:** Breaking passages into typed atoms — the smallest indivisible text units — classified by structural type (7 types) and scholarly function (16 types).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md (1206 lines — the authoritative document)
2. IMPLEMENTATION_ORDER.md (build plan — follow this sequence)
3. TEST_PLAN.md (38 test cases mapped to fixtures and priorities)
4. contracts.py (676 lines — Pydantic models for all inputs/outputs/errors/config)

## What This Engine Does
- Receives passage records from the passaging engine (passages.jsonl)
- Segments each passage into non-overlapping, exhaustive atoms via a 5-phase pipeline
- Classifies each atom on TWO dimensions: structural type + scholarly function
- Detects embedded content (Quran, hadith, poetry) via rule-based + LLM hybrid
- Preserves and propagates text layer attribution from normalization
- Produces an atom stream (atoms.jsonl) consumed by the excerpting engine
- Runs 9 self-validation checks on every passage's output

## Current State
**Code: 0 lines of engine logic.** Module stubs exist with SPEC-referencing docstrings.
**Tests: 0 dedicated.** Test plan written, gold fixtures need creation.
**ABD legacy:** `engines/excerpting/src/extract_passages.py` combined atomization + excerpting. Must be decomposed per SPEC. ABD decisions have zero authority (D-019).

## Module Architecture
```
src/
  engine.py                — Main orchestrator (§4.A.1 five-phase pipeline)
  loader.py                — Input loading + 5 validation checks (§2)
  prescreen.py             — Phase 1: strategy selection, model selection (§4.A.1)
  predetection.py          — Phase 2: rule-based pattern scanning (§4.A.4)
  llm_atomizer.py          — Phase 3: LLM-driven classification (§4.A.5)
  postprocessor.py         — Phase 4: offset correction, coverage, linkage (§4.A.8)
  validator.py             — Phase 5: 9 self-validation checks (§4.A.10)
  emitter.py               — Output emission + status update
  errors.py                — Error classes using AtomizationErrorCode enum
  config.py                — AtomizationConfig loading with per-science overrides
  layer_attribution.py     — Multi-layer attribution (§4.A.6)
  footnote_atomizer.py     — Footnote atomization (§4.A.9)
  format_strategies/
    prose.py               — Default prose strategy (§4.A.7)
    verse.py               — Versified texts (§4.A.7)
    commentary.py          — Multi-layer sharh/hashiyah (§4.A.7)
    qa.py                  — Q&A pairs (§4.A.7)
    masala.py              — Comparative fiqh مسألة blocks (§4.A.7)
    dictionary.py          — Lexical/biographical entries (§4.A.7)
  attribution_detection.py — §4.B.4 Scholarly attribution chains
  fingerprinting.py        — §4.B.5 Semantic fingerprinting (Tier 1-3)
  distribution_analytics.py — §4.B.3 Type distribution statistics
  concordance.py           — §4.B.7 Terminological concordance
  evidence_quality.py      — §4.B.8 Evidence quality signals
  rhetorical_analysis.py   — §4.B.1 Rhetorical structure patterns
  completeness_scoring.py  — §4.B.6 Argument completeness scoring
  implicit_layers.py       — §4.B.2 Implicit layer transitions [deferred]
```

## Build Order
Follow IMPLEMENTATION_ORDER.md strictly. Summary:
1. **Phase 0:** errors.py → config.py → loader.py (foundation)
2. **Phase 1:** prescreen.py → predetection.py (pre-processing)
3. **Phase 2:** llm_atomizer.py + format_strategies/prose.py (LLM atomization)
4. **Phase 3:** postprocessor.py + layer_attribution.py + footnote_atomizer.py (post-processing)
5. **Phase 4:** validator.py + emitter.py (validation + output)
6. **Phase 5:** engine.py (orchestrator wiring)
7. **Phase 6:** remaining format strategies (verse, commentary, masala, qa, dictionary)
8. **Phase 7:** §4.B capabilities (fingerprinting, distribution, attribution, concordance, evidence quality, rhetorical, completeness)

## Key Constraints
1. **Source-agnostic:** operates on passages only, no source-format awareness.
2. **Offset integrity absolute:** `atom_text == passage_text[start:end]` — verified on every atom.
3. **Exhaustive coverage:** every character covered by exactly one atom, no gaps or overlaps.
4. **Two-tier typing mandatory:** every non-heading atom gets both structural_type AND scholarly_function.
5. **Metadata pass-through (D-023):** atom types ARE the new metadata flowing to synthesis.
6. **Fail-loud (D-033):** low-confidence classifications get review flags, not silent defaults.
7. **Arabic text is fragile:** read .claude/skills/arabic-text/SKILL.md before touching predetection.py or postprocessor.py.

## Contracts (contracts.py)
All types are in `engines/atomization/contracts.py` (676 lines):
- **Output:** AtomRecord, AtomStream, all sub-models (AnchorSpan, EmbeddedRef, etc.)
- **Enums:** StructuralType (7), ScholarlyFunction (16), SourceLayer (5), ReviewFlag (15), AttributionType (7), EvidenceQualitySignalType (7)
- **Error handling:** AtomizationErrorCode (22 codes), ErrorSeverity, ERROR_SEVERITY map
- **Configuration:** AtomizationConfig (23 parameters with defaults and valid ranges)
- **§4.B models:** ScholarlyAttribution, ConcordanceEntry, EvidenceQualitySignal, ArgumentCompletenessScore, PassageTypeDistribution, SourceTypeDistribution, FingerprintManifest, TermIndex

## Input (from passaging engine)
- `library/sources/{source_id}/passages/passages.jsonl` — one PassageRecord per line

## Output
- `library/sources/{source_id}/atoms/atoms.jsonl` — one AtomRecord per line
- `library/sources/{source_id}/atoms/distribution_report.json` — type statistics
- `library/sources/{source_id}/atoms/fingerprint_manifest.json` — (when enabled)
- `library/sources/{source_id}/atoms/term_index.json` — (when enabled)
- `library/sources/{source_id}/atoms/atomization_log.jsonl` — error/warning log

## External Dependencies
- **Instructor** (Python, MIT): Structured LLM output with Pydantic
- **Quran_Detector** (GitHub): Quranic verse fragment identification
- **CAMeL Tools** (NYU, MIT): Arabic text processing
- **DSPy** (Stanford, MIT): Optional prompt optimization
- **LiteLLM / OpenRouter / Anthropic API**: LLM providers
- **Arabic-STS-Matryoshka or Swan-Large**: Embedding models (§4.B.5 Tier 3 only)

## Commands
```bash
cd engines/atomization && python -m pytest tests/ -q
python3 scripts/check_spec_quality.py engines/atomization/SPEC.md
```

## Test Fixtures Available
- `ibn_aqil_alfiyyah/` — Multi-layer sharh (commentary strategy, footnotes)
- `alfiyyah_versified/` — Pure verse text (verse strategy)
- `mughni_comparative/` — Comparative fiqh (masala strategy)
- Gold passages — Need creation for core invariant testing

## SPEC Refinement Status
- Creative session: ✅ (8 §4.B capabilities)
- Precision session: ✅ (vague quantifiers fixed, Arabic examples added)
- Hardening session: ✅ (12 adversarial scenarios, 6 invariants verified)
- Implementation prep: ✅ (contracts, 28 stubs, build plan, test plan)
- **Implementation-ready: YES**
