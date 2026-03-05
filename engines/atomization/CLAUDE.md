# Atomization Engine — محرك التذرير

**Responsibility:** Breaking passages into typed atoms — the smallest indivisible text units — classified by structural type and scholarly function (§2.4).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md (the authoritative document)
2. VISION.md §2.4 (atom definition, content type)
3. Input boundary: passage stream from passaging engine (passaging SPEC §3)
4. Output boundary: atom stream → excerpting engine

## What This Engine Does
- Segments each passage into non-overlapping, exhaustive atoms
- Classifies each atom on TWO dimensions: structural type (7 types) + scholarly function (16 types)
- Detects embedded content (Quran, hadith, poetry) via rule-based + LLM hybrid
- Preserves text layer attribution (matn/sharh/hashiyah) from normalization

## Current State
No dedicated code. ABD embedded atomization inside `engines/excerpting/src/extract_passages.py`. Must be separated and redesigned per SPEC. ABD decisions have zero authority (D-019).

Code: 0L dedicated.
Tests: 0 dedicated.

## Commands
```
cd engines/atomization && python -m pytest tests/ -q
```

## Transformative Capabilities (§4.B)
1. **Rhetorical structure analysis** — detect argumentative flow patterns [NOT YET IMPLEMENTED]
2. **Implicit layer transition detection** — flag potential misattribution at unmarked layer shifts [NOT YET IMPLEMENTED]
3. **Atom type distribution analytics** — statistical profile for book briefings [NOT YET IMPLEMENTED]

## External Dependencies
- **Instructor** (Python): structured LLM output with Pydantic
- **Quran_Detector** (GitHub): Quranic verse fragment identification
- **CAMeL Tools** (NYU): Arabic text processing
- **DSPy** (Stanford): prompt optimization against gold baselines

## Key Constraints
1. **Source-agnostic:** operates on passages only, no source-format awareness
2. **Offset integrity absolute:** `atom_text == passage_text[start:end]` — verified on every atom
3. **Exhaustive coverage:** every character covered by exactly one atom, no gaps or overlaps
4. **Two-tier typing mandatory:** every non-heading atom gets both structural_type AND scholarly_function
5. **Metadata pass-through (D-023):** atom types ARE the new metadata flowing to synthesis
6. **Fail-loud (D-033):** low-confidence classifications get review flags, not silent defaults
