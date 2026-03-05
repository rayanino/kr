# Passaging Engine — محرك التقطيع

**Responsibility:** Segmenting normalized content into passages (§2.2).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md (the authoritative document)
2. VISION.md §2.2 (passaging definition), §2.5 (passage definition)
3. Input boundary: normalized package from normalization engine (normalization SPEC §3)
4. Output boundary: passages → atomization engine

## What This Engine Does
- Receives normalized packages and segments their content into passages
- Selects strategy based on `structural_format`: prose, verse, Q&A, tabular khilaf, dictionary, commentary
- Prose targets: 200–800 Arabic words (50 min, 2000 hard max)
- Produces passage stream consumed by the atomization engine

## Current State
No automated passaging logic exists. ABD-era `scaffold_passage.py` (279L) creates manual baselines — irrelevant to KR's automated pipeline. ABD-era `schemas/passage.json` must be rewritten to match SPEC §3.

Code: 0L dedicated (only ABD scaffolding).
Tests: 0 dedicated.

## Commands
```
cd engines/passaging && python -m pytest tests/ -q
```

## Transformative Capabilities (§4.B)
1. **Passage quality prediction** — scores coherence, boundary quality, extractability [NOT YET IMPLEMENTED]
2. **Implicit structure discovery** — detects topic boundaries in headingless texts [NOT YET IMPLEMENTED]
3. **Commentary-matn precision alignment** — maps matn segments to commentary spans [NOT YET IMPLEMENTED]
4. **Cross-edition passage correspondence** — aligns passages between editions [NOT YET IMPLEMENTED]

## External Dependencies
- Sentence embedding model (multilingual-e5-large) for quality prediction + implicit structure
- LLM API via OpenRouter for semantic splitting
- CAMeL Tools for Arabic word tokenization

## Key Constraints
1. **Source-agnostic (§7.6):** operates on normalized packages only, no format-specific logic
2. **Passage containment rule (D-011):** excerpts cannot span passage boundaries — bad boundaries = bad excerpts
3. **Sentence integrity:** no boundary falls mid-sentence
4. **Complete coverage:** every content unit in exactly one passage, no gaps, no overlaps
5. **Metadata pass-through (D-023):** passages carry all upstream metadata for synthesis
6. **Fail-loud (D-033):** uncertain boundaries get review flags, not silent defaults
