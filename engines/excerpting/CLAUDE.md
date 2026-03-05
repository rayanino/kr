# Excerpting Engine — محرك الاقتطاف

**Responsibility:** Grouping atoms into self-contained excerpts (§5), enriching with metadata for synthesis.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md (the authoritative document)
2. VISION.md §5 (excerpt definition, self-containment, architectural rules)
3. VISION.md §2.4 (excerpt vocabulary, lifecycle stages)
4. Input boundary: atom stream from atomization engine (atomization SPEC §3)
5. Output boundary: draft excerpts → taxonomy engine

## What This Engine Does
- Groups atoms into candidate excerpts using LLM boundary detection
- Evaluates self-containment against §5.1 standard (with multi-model consensus)
- Enriches each excerpt with metadata: author, school, topic, evidence, takhrij, quoted scholars
- Prevents decontextualized quotation (§4.A.2) — the most dangerous excerpt error

## Architecture: Three-Phase Pipeline (D-037)
1. **Boundary Detection** — group atoms into teaching units. Bonded atoms are hard constraints.
2. **Self-Containment Evaluation** — score ≥0.7 accept, 0.5–0.7 enrich, <0.5 merge.
3. **Metadata Enrichment** — populate attribution, classification, and reference fields.

## Current State
ABD code: extract_passages.py (2288L combined atomization+excerpting), assemble_excerpts.py (1021L).
Must be separated from atomization and redesigned per SPEC. 10 ABD-era reference docs — historical only (D-019).

## Commands
```
cd engines/excerpting && python -m pytest tests/ -q
```

## External Dependencies
- **Instructor**: structured LLM output. **OpenRouter**: LLM routing.
- **DSPy**: prompt optimization. **CAMeL Tools**: Arabic normalization.
- **Sentence-transformers**: embeddings for duplicate detection.

## Key Constraints
1. **Self-containment existential (§5.1):** every excerpt independently understandable
2. **Taxonomy-independent (§5.2):** group by content, place by taxonomy — never mix
3. **Multi-model consensus (D-036):** self-containment + school attribution use 2 independent models
4. **Decontextualization prevented (§4.A.2):** reported positions include response/refutation
5. **Metadata is synthesis fuel (D-023):** every field serves the synthesizer
6. **Text integrity absolute (D-004):** primary_text never modified
7. **Fail-loud (D-033):** low-confidence decisions get flags, not silent defaults
