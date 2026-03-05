# Passaging Engine — محرك التقطيع

**Responsibility:** Segmenting normalized content into passages (§2.2).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md (502 lines, all 10 sections)
2. VISION.md §2.2 (passaging definition), §2.5 (passage definition)
3. Input boundary: normalized package from normalization engine (see normalization SPEC §3)
4. Output boundary: passages → atomization engine

## Current State
No automated passaging logic exists. ABD-era `scaffold_passage.py` (279L) creates manual baselines — has zero relevance to KR's automated pipeline and should be replaced entirely. ABD-era `schemas/passage.json` must be rewritten to match SPEC §3.

## Architecture Summary

**Input:** Normalized package (manifest.json + content.jsonl) at `library/sources/{source_id}/normalized/`.

**Output:** Passage stream (passages.jsonl) at `library/sources/{source_id}/passages/`.

**Processing flow:**
1. Load + validate input (§2)
2. Cross-page text assembly — join per-page content units into continuous text (§4.A.2)
3. Strategy selection based on `structural_format` (§4.A.3)
4. Create passages using format-specific strategy (§4.A.4–§4.A.9)
5. Emit + self-validate (§4.A.10)

**Six format-specific strategies:**
- Prose: division-guided with semantic splitting (§4.A.4) — default, most common
- Verse: verse-group passaging for منظومات (§4.A.5) — never splits a بيت
- Q&A: question-answer pair passaging for فتاوى/مسائل (§4.A.6)
- Tabular khilaf: مسألة-block passaging for disagreement catalogs (§4.A.7)
- Dictionary: root/entry-boundary passaging for معاجم (§4.A.8)
- Commentary: commentary-unit passaging keeping matn+sharh together (§4.A.9)

**Size targets (prose):** 200–800 Arabic words target, 50 min (merge below), 2000 hard max (force split above).

## Key Constraints
1. **Source-agnostic** (§7.6): operates on normalized packages only. No format-specific logic.
2. **Passage containment rule (D-011):** Excerpts cannot span passage boundaries. Bad passage boundaries = bad excerpts.
3. **Sentence integrity:** No passage boundary falls mid-sentence.
4. **Verse integrity:** A بيت is never split across passage boundaries.
5. **Metadata pass-through (D-023):** Passages carry all upstream metadata via `source_id` reference + add division path, physical pages, assembled text, text layers, content flags, fidelity.
6. **Complete coverage:** Every digestible content unit appears in exactly one passage. No text lost, no overlaps.

## Transformative Capabilities (§4.B)
1. **Passage quality prediction** — scores coherence, boundary quality, extractability per passage [NOT YET IMPLEMENTED]
2. **Implicit structure discovery** — detects topic boundaries in headingless texts [NOT YET IMPLEMENTED]
3. **Commentary-matn precision alignment** — maps matn segments to their commentary spans [NOT YET IMPLEMENTED]
4. **Cross-edition passage correspondence** — aligns passages between editions of the same work [NOT YET IMPLEMENTED]

## External Dependencies
- Sentence embedding model (multilingual-e5-large or similar) — for quality prediction + implicit structure
- LLM API via OpenRouter — for semantic splitting + implicit structure
- CAMeL Tools — for Arabic word tokenization
