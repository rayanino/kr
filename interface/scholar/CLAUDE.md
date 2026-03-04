# Scholar Interface — واجهة العالم

**Responsibility:** The primary product of KR. Everything else exists to feed this. KR IS Rayane's knowledge — the library represents what he knows, and the scholar interface is how he interacts with, grows, and expresses that knowledge. It provides the complete scholarly experience: structured curriculum, conversational Q&A, active teaching, proactive discovery, scholarly production assistance, and knowledge navigation.

This is not an add-on. The owner has no teacher, no existing study practice, no curriculum. KR IS the study infrastructure. If the engines work perfectly but this interface doesn't guide study from zero to mastery, the application has failed.

Because the library IS his knowledge, quality is existential: every answer must be verifiable, every citation traceable, every claim sourced. An error in an interface response is an error planted in Rayane's understanding.

## Capability Domains

**Guiding** — Curriculum design and structured learning. Generate complete study sequences for any science: which books to read, in what order, starting from which level. Follow classical Islamic pedagogical progressions (mutun → shuruh → hawashi). Track progress through the curriculum. Adapt pacing based on demonstrated understanding. This is the first capability the user will need — before Q&A, before research, before anything else.

**Answering** — Conversational Q&A grounded in the library's verified knowledge. Every claim cites specific excerpts from specific sources. Handles: single-school queries, comparative queries, evidence-chain queries, historical evolution queries. Never generates unverified claims — if the library doesn't have the answer, says so and suggests which sources to acquire.

**Teaching** — Active learning support. Socratic dialogue that tests and deepens understanding. Spaced repetition of scholarly positions. Knowledge gap detection: "You have engaged with 3 schools on topic X but not the Hanafi position." Adapts teaching style based on user model: beginner gets simplified explanations, advanced gets nuanced comparative analysis.

**Discovering** — Proactive intelligence that surfaces what the user doesn't know to look for. New source alerts relevant to current study focus. Contradiction detection between sources. Coverage gap alerts. Daily/weekly personalized scholarly briefings. Research question generation.

**Assisting** — Scholarly production support. Writing assistance with full source citation. Footnote generation from library knowledge. Tahqiq comparison across editions. Evidence compilation for research topics. Tarjih scaffolding: "Here are all positions on X with their evidence — here's the framework for weighing them."

**Navigating** — Knowledge exploration. Taxonomy browsing. Scholar network visualization. Temporal evolution of positions. Coverage maps across sciences, schools, and centuries. Personal progress visualization.

## Three Modes (maps to user's "complete scholar" goal)

1. **Learning mode** — absorb and understand positions (encyclopedic knowledge). Curriculum-guided reading, Socratic testing, spaced repetition.
2. **Research mode** — compare, analyze, produce original work (scholarly production). Evidence compilation, contradiction detection, tarjih scaffolding, writing assistance.
3. **Teaching mode** — practice explaining positions (teaching mastery). Generate lesson outlines, simulate student questions, assess explanation clarity.

## The Feedback Loop

Rayane's own scholarly output feeds back into the library. When he writes a tarjih (comparative analysis), a research paper, personal notes, or conclusions — these become part of KR alongside the classical sources. His voice grows alongside the classical voices. This means:
- The library has two classes of content: **source-derived** (from processed books) and **owner-originated** (from Rayane's own scholarship)
- Owner-originated content is clearly marked but treated as first-class knowledge
- Over time, the library becomes not just "what scholars said" but "what scholars said AND what Rayane concluded"
- The interface can cite Rayane's own previous conclusions: "You wrote in your analysis of topic X that..."

## Dependencies

Reads from: placed excerpts, entries, source registry, taxonomy trees, knowledge graph.
Reads and writes: user model (shared/user_model).
Uses: consensus engine (for complex queries requiring multi-model verification).

## Architectural Notes

The scholar interface reads the user model to personalize every interaction. The user model tracks: study history, demonstrated knowledge (from Socratic dialogue), identified gaps, current focus areas, preferences, curriculum progress.

The interface may use multiple LLM calls per interaction — e.g., a comparative query might retrieve excerpts from 4 schools, synthesize them, then generate a follow-up question. This is by design; quality of scholarly interaction outweighs latency.

Since the user starts from zero with Arabic language sciences, the interface must support a complete beginner in its first deployment while scaling to support advanced scholarly research as the user progresses. The user model's assessment of current level drives this adaptation.
