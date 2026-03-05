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
- Receives atom records from the atomization engine
- Groups atoms into candidate excerpts using LLM boundary detection
- Evaluates self-containment against §5.1 standard (with multi-model consensus)
- Enriches each excerpt with metadata: author, school, topic, evidence refs, takhrij, quoted scholars
- Prevents decontextualized quotation (§4.A.2) — the most dangerous excerpt error
- Produces draft excerpts consumed by the taxonomy engine

## Architecture: Three-Phase Per-Passage Processing
1. **Boundary Detection** (LLM-driven): group atoms into coherent teaching units. Bonded atoms are hard constraints. Division structure and atom relations provide hints.
2. **Self-Containment Evaluation** (LLM + consensus): evaluate each candidate against §5.1 standard. Score ≥ 0.7 → accept. 0.5–0.7 → enrich with context atoms. < 0.5 → merge with adjacent.
3. **Metadata Enrichment** (deterministic + LLM): populate all attribution, classification, and reference fields.

## Key Design Decisions
- **Multi-model consensus (D-036)** for self-containment and school attribution. Two independent models, conservative scoring on disagreement.
- **Decontextualization prevention** (§4.A.2): explicit detection of reported positions. Reported + response must stay in same excerpt.
- **Three excerpt kinds:** teaching (scholarly content), exercise (practice material), apparatus (editorial).
- **Passage containment rule (D-011):** all atoms in an excerpt must share the same passage_id.
- **Taxonomy-independence rule (§5.2):** excerpts are grouped by content coherence, NEVER by taxonomy fit.

## Transformative Capabilities (§4.B)
1. **Cross-excerpt scholarly dialogue detection** — detect intellectual engagement between excerpts from different sources at the same leaf
2. **Self-containment repair suggestions** — actionable fix recommendations for incomplete excerpts
3. **Scholarly argument completeness analysis** — detect when evidence is missing from an argument

## Current State
ABD code: extract_passages.py (2288L combined atomization+excerpting), assemble_excerpts.py (1021L).
Must be separated from atomization and redesigned per SPEC.
10 ABD-era reference docs — historical reference only (D-019).

## External Dependencies
- **Instructor** (Python): structured LLM output for all phases
- **OpenRouter** (API): LLM routing for primary + consensus models
- **DSPy** (Python): prompt optimization against gold baselines
- **CAMeL Tools** (Python): Arabic text normalization
- **Sentence-transformers** (Python): embedding models for duplicate detection

## Key Constraints
1. **Self-containment is existential** (§5.1): every excerpt must be independently understandable
2. **Taxonomy-independent creation** (§5.2): group by content, place by taxonomy — never mix
3. **Content integrity > taxonomic precision** (§5.3 Rule 3): never break self-containment for taxonomy fit
4. **Metadata is synthesis fuel (D-023):** every field serves the synthesizer's ability to produce scholarly narratives
5. **Fail-loud (D-033):** low-confidence decisions get flags, not silent defaults
6. **Text integrity absolute (D-004):** primary_text is never modified
7. **Multi-layer attribution (§4.A.3):** excerpts attributed to correct layer author
8. **Evidence grading captured (§4.A.4):** hadith evidence carries authenticity status
9. **Decontextualization prevented (§4.A.2):** reported positions include the response/refutation
