# Atomization Engine — محرك التذرير

**Responsibility:** Breaking passages into typed atoms (§2.4) — the smallest indivisible units of text — and classifying each atom by structural type and scholarly function.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md (the authoritative document)
2. VISION.md §2.4 (atom definition, content type)
3. Input boundary: passage stream from passaging engine (passaging SPEC §3)
4. Output boundary: atom stream → excerpting engine

## What This Engine Does
- Receives passage records from the passaging engine
- Segments each passage's text into non-overlapping, exhaustive atoms
- Classifies each atom on TWO dimensions: structural type (shape) + scholarly function (role in discourse)
- Detects embedded content (Quran quotations, hadith, poetry) via rule-based and LLM detection
- Preserves text layer attribution (matn/sharh/hashiyah) from normalization
- Produces an atom stream consumed by the excerpting engine

## Architecture: Five-Phase Per-Passage Processing
1. **Pre-screen** (deterministic): Select strategy, calibrate thresholds
2. **Rule-based pre-detection** (deterministic): Quran, hadith, evidence markers, poetry, footnotes
3. **LLM atomization** (LLM-driven): Boundary detection + type classification via Instructor/Pydantic
4. **Post-processing** (deterministic): Offset correction, coverage enforcement, layer attribution
5. **Self-validation** (deterministic): 7 automated checks (V-1 through V-7)

## Key Design Decisions
- **Two-tier type system:** 7 structural types × 16 scholarly function types. Independent dimensions.
- **Rule-based + LLM hybrid:** Quran detection uses canonical text matching; scholarly function uses LLM with few-shot examples.
- **No multi-model consensus** for atomization (conscious decision — see SPEC §6). Consensus operates at the excerpting level.
- **Offset integrity invariant:** atom_text == passage_text[start:end] — verified deterministically on every atom.
- **Exhaustive coverage:** Every character in passage_text covered by exactly one atom. No gaps, no overlaps.

## Transformative Capabilities (§4.B)
1. **Rhetorical structure analysis** — Detect argumentative flow patterns (issue→opinion→evidence→refutation)
2. **Implicit layer transition detection** — Flag potential misattribution where commentary shifts to matn without markers
3. **Atom type distribution analytics** — Statistical profile of source content structure for book briefings and excerpting hints

## Current State
No dedicated code. ABD embedded atomization logic inside engines/excerpting/src/extract_passages.py — to be separated and redesigned. ABD design decisions have zero authority (D-019).

Code: 0L dedicated (logic embedded in excerpting).
Tests: 0 dedicated.
Reference: 2 ABD-era docs in engines/atomization/reference/.

## External Dependencies
- **Instructor** (Python): Structured LLM output with Pydantic schema enforcement
- **Quran_Detector** (GitHub): Quranic verse fragment identification (≥3 words)
- **CAMeL Tools** (NYU): Arabic text processing utilities
- **DSPy** (Stanford): Prompt optimization against gold baselines

## Key Constraints
1. **Source-agnostic**: operates on passages only, no source-format awareness
2. **Offset integrity is absolute**: every atom's text must exactly match passage_text at its offsets
3. **Two-tier typing is mandatory**: every non-heading atom gets both structural_type AND scholarly_function
4. **Metadata pass-through (D-023)**: atom types ARE the new metadata flowing to synthesis
5. **Fail-loud (D-033)**: low-confidence classifications get review flags, not silent defaults
6. **Layer attribution from normalization**: atoms inherit and may refine text_layers from passages
