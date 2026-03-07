# Passaging Engine — محرك التقطيع

**Responsibility:** Segmenting normalized content into passages for downstream processing.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md (1038 lines — the authoritative document)
2. IMPLEMENTATION_ORDER.md (build plan — follow this sequence)
3. TEST_PLAN.md (test cases mapped to fixtures)
4. contracts.py (556 lines — Pydantic models for all inputs/outputs/errors/config)

## What This Engine Does
- Receives normalized packages (manifest.json + content.jsonl) and segments content into passages
- Selects strategy based on `structural_format`: prose, verse, Q&A, masala-block, dictionary, commentary
- Prose targets: 200–800 Arabic words (50 min, 2000 hard max)
- Produces passage stream (passages.jsonl) consumed by the atomization engine
- Runs 11 self-validation checks on every output (6 fatal, 5 warning)

## Current State
**Code: 0 lines of engine logic.** Module stubs exist with SPEC-referencing docstrings.
**Tests: 0 dedicated.** Test plan written, fixtures partially available.
**ABD legacy:** `scaffold_passage.py` (279L) and `schemas/passage.json` are irrelevant — ignore entirely.

## Module Architecture
```
src/
  engine.py              — Main orchestrator (§4.A.1 six-phase pipeline)
  loader.py              — Input loading + 6 validation checks (§2)
  assembly.py            — Cross-page text assembly (§4.A.2) ← hardest module
  strategy.py            — Strategy selection router (§4.A.3)
  strategies/
    prose.py             — Default: division-guided + semantic splitting (§4.A.4)
    verse.py             — Versified texts (§4.A.5)
    qa.py                — Q&A pairs (§4.A.6)
    masala.py            — Comparative fiqh مسألة blocks (§4.A.7)
    dictionary.py        — Lexical/biographical entries (§4.A.8)
    commentary.py        — Multi-layer sharh/hashiyah (§4.A.9)
  emitter.py             — Passage emission + linking (§4.A.10)
  validator.py           — 11 self-validation checks (§4.A.10)
  errors.py              — Error classes using PassagingErrorCode enum
  config.py              — PassagingConfig loading with per-science overrides
  arguments.py           — §4.B.6 Argument boundary detection
  discourse_optimization.py — §4.B.7 Discourse-aware boundary optimization
  completeness_forecast.py  — §4.B.8 Completeness forecast
  adaptive_passaging.py     — §4.B.5 Content census adaptation
  quality_prediction.py     — §4.B.1 [NOT YET IMPLEMENTED — deferred]
  implicit_structure.py     — §4.B.2 [NOT YET IMPLEMENTED — deferred]
  commentary_alignment.py   — §4.B.3 [NOT YET IMPLEMENTED — deferred]
  cross_edition.py          — §4.B.4 [NOT YET IMPLEMENTED — deferred]
```

## Build Order
Follow IMPLEMENTATION_ORDER.md strictly. Summary:
1. **Phase 0:** errors.py → config.py → loader.py (foundation)
2. **Phase 1:** assembly.py (cross-page joining — Arabic text care required)
3. **Phase 2:** strategies/prose.py + strategy.py (default strategy)
4. **Phase 3:** emitter.py + validator.py (output + validation)
5. **Phase 4:** engine.py (orchestrator wiring)
6. **Phase 5:** remaining strategies (verse, masala, qa, commentary, dictionary)
7. **Phase 6:** §4.B capabilities (adaptive, arguments, discourse, completeness)

## Key Constraints
1. **Source-agnostic:** operates on normalized packages only. No format-specific logic.
2. **Passage containment (D-011):** excerpts cannot span passages. Bad boundaries = bad excerpts.
3. **Sentence integrity:** no boundary falls mid-sentence in Arabic text.
4. **Complete coverage:** every substantive content unit in exactly one passage.
5. **Metadata pass-through (D-023):** passages carry all upstream metadata.
6. **Fail-loud:** uncertain boundaries get review flags, not silent defaults.
7. **Arabic text is fragile:** read .claude/skills/arabic-text/SKILL.md before touching assembly.py.

## Contracts (contracts.py)
All types are in `engines/passaging/contracts.py` (556 lines):
- **Output:** PassageRecord, PassageStream, all sub-models
- **Enums:** ReviewFlag (15 values), HeadingSource, PassageStructuralFormat, SizingAction, ArgumentCompleteness, CompletenessLevel, etc.
- **Error handling:** PassagingErrorCode (38 codes), ErrorSeverity, ERROR_SEVERITY map
- **Configuration:** PassagingConfig (17 parameters with defaults and valid ranges)
- **§4.B models:** QualityPrediction, ArgumentStructure, CompletenessForecast, CommentaryAlignmentRecord, AdaptiveParams, CrossEditionMap

## Input (from normalization engine)
- `library/sources/{source_id}/normalized/manifest.json` — NormalizedManifest
- `library/sources/{source_id}/normalized/content.jsonl` — list[ContentUnit]
- Source metadata via `source_id` reference

## Output
- `library/sources/{source_id}/passages/passages.jsonl` — one PassageRecord per line

## External Dependencies
- **LiteLLM + Instructor** — LLM calls for semantic splitting (Phase 2+)
- **PyArabic** — Arabic character analysis for assembly
- **Sentence embeddings** — quality prediction, implicit structure (Phase 6, deferred)
- **CAMeL Tools** — technical term identification (Phase 6)

## Commands
```bash
cd engines/passaging && python -m pytest tests/ -q
python3 scripts/check_spec_quality.py engines/passaging/SPEC.md
```

## Test Fixtures Available
- `ibn_aqil_alfiyyah/` — Multi-layer sharh (prose + verse commentary)
- `alfiyyah_versified/` — Pure verse text (1000 lines)
- `mughni_comparative/` — Large comparative fiqh (69 .doc files)
- `waraqat_usul/` — Single-layer prose
- `owner_note/` — Manual input
- `photo_scan_ilm/` — Scanned pages

## SPEC Refinement Status
- Creative session: ✅ (2 new §4.B capabilities: boundary optimization, completeness forecast)
- Precision session: ✅ (18 defects fixed, Arabic examples added)
- Hardening session: ✅ (12 adversarial scenarios, 18 defects fixed)
- Implementation prep: ✅ (contracts, stubs, build plan, test plan)
- **Implementation-ready: YES**
