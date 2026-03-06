# NEXT SESSION

**Written by:** Session 2026-03-06 (Scholar Interface SPEC enhancements + research)
**Date:** 2026-03-06

## Immediate Task

Continue the scholar interface SPEC from §4.B (Transformative Capabilities). Complete §4.B through §10. Also integrate the retrieval pipeline architecture into §4.A.2 (see "Architecture Additions" below).

**Definition of done — this session is complete when:**
1. Scholar interface SPEC completed (all 10 sections)
2. Retrieval pipeline architecture integrated into §4.A.2 (Qdrant vector store, embedding model, cross-encoder re-ranking, grounding enforcement thresholds)
3. VISION.md corrections for scholar interface
4. Any new decisions recorded in kr_decisions.md
5. Changes committed and pushed

## Context

§1–§4.A are complete (520 lines). All six capability domains are specified. The SPEC uses a simpler retrieval approach (keyword + semantic similarity against leaf titles) that needs to be upgraded with the full hybrid retrieval pipeline researched this session.

## Architecture Additions to Integrate

The current §4.A.2.2 describes a basic retrieval strategy (topic identification → content retrieval → scholar enrichment → user context). This should be enhanced with:

**1. Qdrant vector store (self-hosted).** Two collections:
- **Excerpt embeddings:** One vector per placed excerpt (embedded from `primary_text`). Payload: excerpt_id, leaf_path, science_id, school, primary_author_id, evidence_types, content_types, death_hijri, source_id, placement_confidence, self_containment_score. Enables filtered vector search without joins.
- **Entry-section embeddings:** One vector per entry section (core_treatment, each scholarly_position, each edge_case). Payload: entry_id, leaf_path, science_id, school_group, section_type. Section-level embedding for precise retrieval.

**2. Embedding model.** Arabic Matryoshka model — evaluate AraGemma-Embedding-300m vs Swan-Large on KR's corpus. See RESOURCES.md for details.

**3. Cross-encoder re-ranking.** After initial retrieval (top-K=20), re-rank with cross-encoder for precision. Adds ~100-200ms, acceptable for personal use.

**4. Grounding enforcement thresholds.**
- Every citation carries `grounding_type`: `library_excerpt`, `library_metadata`, or `llm_research`.
- >30% LLM-contributed claims → `confidence_assessment: "low"` + visible notice to Rayane.
- >50% LLM-contributed → recommend acquiring additional sources.

**5. Four retrieval strategies:**
- **Targeted:** Exact match → leaf titles + synonyms. For specific topic queries.
- **Semantic:** Qdrant ANN search. For broad/exploratory queries.
- **Filtered:** Metadata constraints (school, period, evidence type, author). Combinable with targeted/semantic.
- **Cross-science:** From cross_science_links.json for multi-science queries.

## Files to Read — IN THIS ORDER

1. `interface/scholar/SPEC.md` — the partial SPEC. Read FIRST.
2. `reference/RESOURCES.md` — Scholar Interface Resources section for tool references.
3. `reference/DOMAIN.md` §"What Doesn't Exist Yet" — for §4.B inspiration.
4. `reference/ENTRY_EXAMPLE.md` — to calibrate what §4.B should enable.

**Do NOT re-read:** USER_SCENARIOS.md, upstream SPEC output contracts, or DOMAIN.md in full.

## Decisions Needed

- **§4.B transformative capabilities.** Directions to explore:
  - **Debate simulation:** Simulate scholarly debates between historical figures based on documented positions.
  - **Optimal source prediction:** Which SOURCE would most accelerate Rayane's learning given current state?
  - **Full lesson generation:** Not just sequencing but content: "Generate a 30-minute lesson on X."
  - **Knowledge graph Q&A:** Scholar network queries: "Who disagreed with Sibawayhi on any topic?"
  - **Scholarly fingerprinting:** What makes each scholar's approach distinctive? Can the interface characterize a scholar's methodology from their positions across topics?

- **§6 Consensus.** Should the interface use multi-model consensus? The current SPEC uses it for assessment evaluation of ambiguous responses. Consider whether grounding verification also needs it.

## Pending Owner Questions

None.

## What This Session Did

Updated RESOURCES.md with detailed research: Qdrant vector database (with comparison to pgvector, ChromaDB, Pinecone), Arabic embedding models (AraGemma-Embedding, Swan-Large, Arabic-Matryoshka-V2, E5-ML-Large), and cross-encoder re-ranking options. The previous session wrote §1-§4.A (520L). This session's key addition is the retrieval pipeline architecture specification (documented above) that needs integration.

## New Decisions

None.
