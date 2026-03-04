# Scholar Interface — واجهة العالم

**Responsibility:** The user-facing intelligence layer. Consumes all knowledge products (excerpts, entries, knowledge graph) and provides Rayane with interactive scholarly capabilities: conversational Q&A, active teaching, proactive discovery, scholarly production assistance, and knowledge navigation.

This is not a processing engine. The 7 engines build the library; the scholar interface IS the librarian. It is the reason the library exists.

## Capability Domains

**Answering** — Conversational Q&A grounded in the library's verified knowledge. Every claim cites specific excerpts from specific sources. Handles: single-school queries, comparative queries, evidence-chain queries, historical evolution queries.

**Teaching** — Active learning support. Socratic dialogue that tests and deepens understanding. Study path generation based on the user model. Spaced repetition of scholarly positions. Knowledge gap detection: "You have engaged with 3 schools on topic X but not the Hanafi position."

**Discovering** — Proactive intelligence that surfaces what the user doesn't know to look for. New source alerts relevant to current study focus. Contradiction detection between sources. Coverage gap alerts. Daily/weekly personalized scholarly briefings. Research question generation.

**Assisting** — Scholarly production support. Writing assistance with full source citation. Footnote generation from library knowledge. Tahqiq comparison across editions. Evidence compilation for research topics.

**Navigating** — Knowledge exploration. Taxonomy browsing. Scholar network visualization. Temporal evolution of positions. Coverage maps across sciences, schools, and centuries.

## Dependencies

Reads from: placed excerpts, entries, source registry, taxonomy trees, knowledge graph.
Reads and writes: user model (shared/user_model).
Uses: consensus engine (for complex queries requiring multi-model verification).

## Architectural Notes

The scholar interface reads the user model to personalize every interaction. The user model tracks: study history, demonstrated knowledge (from Socratic dialogue), identified gaps, current focus areas, preferences.

The interface may use multiple LLM calls per interaction — e.g., a comparative query might retrieve excerpts from 4 schools, synthesize them, then generate a follow-up question. This is by design; quality of scholarly interaction outweighs latency.
