# Scholar Interface — واجهة العالم

**Responsibility:** The primary product of KR. Everything else exists to feed this. The scholar interface is a conversational and structured intelligence layer that sits on top of all engine outputs and shared component state. KR IS Rayane's knowledge (D-018), and the scholar interface is how he interacts with, grows, questions, produces, and navigates that knowledge.

## Six Capability Domains

1. **Guiding (§4.A.1)** — Curriculum design and structured learning from zero to mastery. Generates curricula based on classical pedagogical progressions (mutun → shuruh → hawashi), taxonomy narrative ordering, and available library content. Orchestrates daily study sessions: review backlog → new material → source alerts → cross-science connections.

2. **Answering (§4.A.2)** — Library-grounded conversational Q&A. Classifies queries (single-topic, comparative, evidence-chain, historical evolution, scholar-specific, cross-science, meta-library, ungrounded). Multi-stage retrieval: topic identification → content retrieval → scholar context enrichment → user context overlay. Every factual claim cited to source. LLM-contributed context explicitly marked. Includes book briefing generation (D-022).

3. **Teaching (§4.A.3)** — Socratic assessment with four question types: recall, recognition, application, comparison. Assessment evaluation uses multi-model consensus for ambiguous responses. Spaced repetition orchestration via FSRS (user_model §4.A.3). Knowledge gap detection from assessment patterns.

4. **Discovering (§4.A.4)** — Proactive intelligence. New content alerts with relevance scoring. Cross-science connection surfacing. Coverage gap alerting (school, temporal, source gaps). Periodic scholarly briefings. Contradiction detection surfacing.

5. **Assisting (§4.A.5)** — Scholarly production support. Evidence compilation, writing assistance (footnote generation, claim verification, citation completeness), tarjih scaffolding, lesson plan generation.

6. **Navigating (§4.A.6)** — Knowledge exploration. Science map visualization data, taxonomy browsing, scholar network exploration (teacher-student chains, influence graphs), temporal exploration (position evolution, century views).

## Three Modes

1. **Learning mode** — Guiding + Teaching + Answering. Absorb and understand.
2. **Research mode** — Answering + Assisting + Discovering. Compare, analyze, produce.
3. **Teaching mode** — Answering + Teaching + Navigating. Practice explaining, generate lessons.

## Data Flow

**Reads from:** placed excerpts (taxonomy engine), entries (synthesis engine), taxonomy trees + coverage analytics (taxonomy engine), scholar records + graph data (scholar_authority), user model state (user_model), source metadata (via provenance chains), feedback state (feedback component).

**Writes to:** user_model (engagement events, assessment results, curriculum actions, review results, bookmarks, annotations, focus declarations, scholarly production events, alert actions), feedback component (corrections).

## Correction Handling (§4.A.7)

Entry-level → owner constraint at leaf, entry marked stale.
Excerpt-level → metadata correction via feedback component.
Taxonomy-level → relocation request via human gate.
Metadata-level → routed to source engine or scholar_authority.
Pattern detection after each correction.

## Key Design Principles

- **Grounding non-negotiable.** Every factual claim traced to source or explicitly marked as LLM-contributed. No fabricated citations — worse than admitting ignorance.
- **Assessment integrity.** Never false positive assessments. Uncertainty scores 0.5 (partial), not 1.0.
- **Gaps as opportunities.** Coverage gaps presented constructively, not as deficiencies.
- **Progressive adaptation.** Response depth adapts to owner's expertise level from user model.
- **Session context.** Multi-turn conversation maintained within sessions. Cross-session via user model history.

## SPEC Status

§1–§4.A complete. §4.B (Transformative Capabilities) through §10 pending next session.
