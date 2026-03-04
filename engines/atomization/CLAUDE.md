# Atomization Engine — محرك التذرير

**Responsibility:** Breaking passages into typed atoms (§2.4).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §2.4 (atom definition, content type)
3. Input boundary: passages from passaging engine
4. Output boundary: atoms → excerpting engine

## Current State
No dedicated code. ABD embedded atomization logic inside `engines/excerpting/src/extract_passages.py` — to be separated. ABD design decisions have zero authority in KR (D-019).

Code: 0L dedicated (logic embedded in excerpting).
Tests: 0 dedicated.
Reference: 2 ABD-era docs in `engines/atomization/reference/`.

## Key Constraints
1. **Source-agnostic** (§7.6): operates on passages only.
2. **Atoms have types** (§2.4): type determination rules in SPEC.
3. **Character offsets are precise** (§2.4): every atom must be locatable within its passage by exact character offsets. Offset errors corrupt downstream excerpt construction.
4. **Islamic scholarly text patterns.** Arabic scholarly texts have distinctive structural patterns that inform atom typing: isnad chains (حدثنا فلان عن فلان) are transmission metadata — NOT the author's own words. Evidence markers (لقوله تعالى، لقول النبي ﷺ) indicate a shift from opinion to evidence. Refutation patterns (ورُدّ بأن، والجواب عن هذا) indicate the author is responding to an opposing view. Opinion markers (وذهب الحنفية إلى، والراجح عندي) indicate position statements. Recognizing these patterns at the atom level is what enables the excerpting engine to build contextually correct excerpts.
5. **Metadata pass-through (D-023):** Atom output must carry all upstream metadata. The atom type itself IS new metadata that flows downstream to the synthesizer.
