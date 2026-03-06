# Scholar Interface — واجهة العالم — Specification

## 1. Purpose and Scope

**What this component does.** The scholar interface is the primary product of KR. Every engine and shared component exists to feed it. KR IS Rayane's knowledge (D-018), and the scholar interface is the surface through which he interacts with, grows, questions, produces, and navigates that knowledge. It is not a search bar over a database. It is a living scholarly partner — a system that teaches, challenges, discovers, assists, and adapts, grounded entirely in the library's verified knowledge.

The scholar interface is a conversational and structured intelligence layer that sits on top of all engine outputs and shared component state. It reads: placed excerpts (from taxonomy engine), synthesized entries (from synthesis engine), taxonomy trees with prerequisites and coverage analytics (from taxonomy engine), scholar authority records and intellectual genealogy graphs (from scholar_authority component), and user model state — engagement history, knowledge estimates, curricula, gaps, alerts (from user_model component). It reads source metadata through placed excerpts' provenance chains. It writes to the user model: engagement events, assessment results, curriculum actions, bookmarks, annotations, focus declarations, and scholarly production events.

The scholar interface has six capability domains, corresponding to six distinct but overlapping responsibilities:

1. **Guiding** — curriculum design and structured learning from zero to mastery.
2. **Answering** — conversational Q&A grounded in the library's verified knowledge.
3. **Teaching** — active Socratic assessment and spaced repetition orchestration.
4. **Discovering** — proactive intelligence that surfaces what the user doesn't know to look for.
5. **Assisting** — scholarly production support: writing, footnoting, evidence compilation, tarjih scaffolding.
6. **Navigating** — knowledge exploration: taxonomy browsing, scholar networks, temporal evolution, science maps, coverage analytics.

These six domains map to three user modes that reflect the owner's "complete scholar" goal (DOMAIN.md): **Learning mode** (Guiding + Teaching + Answering — absorb and understand), **Research mode** (Answering + Assisting + Discovering — compare, analyze, produce), and **Teaching mode** (Answering + Teaching + Navigating — practice explaining, generate lesson plans). Mode selection is explicit (the owner declares which mode they're in) but the interface may operate across modes within a single session when context requires it — a learning session may spawn a research tangent, and that is natural.

**What is NOT this component's responsibility.** The scholar interface does not process sources (source engine), normalize text (normalization engine), create passages (passaging engine), produce atoms (atomization engine), generate excerpts (excerpting engine), manage taxonomy trees (taxonomy engine), or synthesize entries (synthesis engine). It consumes these engines' outputs but does not produce them. It does not manage human gate checkpoints (human gate component), though it may present gate decisions to the owner when relevant. It does not persist user state directly — it writes events to the user model component, which handles persistence. It does not manage scholar authority records — it reads them from the scholar_authority component.

**Phase classification.** The scholar interface requires at minimum: one source processed through the complete pipeline (so that placed excerpts and at least one entry exist), a taxonomy tree for at least one science, and the user model initialized. The interface cannot function with an empty library — it is the surface of the library, not a standalone system. However, it degrades gracefully: if only partial pipeline output exists (excerpts placed but entries not yet synthesized), the interface can present raw excerpts with source citations. If taxonomy coverage is sparse, the interface can navigate what exists and explicitly flag gaps.

**User scenarios served.** All eight scenarios in USER_SCENARIOS.md are scholar interface interactions:
- Scenario 1 (Day 1): Guiding domain — curriculum initialization, first topic presentation, first Socratic check. §4.A.1.
- Scenario 2 (Active Study): Guiding + Teaching + Discovering — spaced repetition, source alerts, comparative queries. §4.A.1, §4.A.3, §4.A.4, §4.A.2.
- Scenario 3 (Cross-Science): Discovering + Answering — proactive cross-science connection surfacing, cross-science analysis generation. §4.A.4, §4.A.2.
- Scenario 4 (Scholarly Production): Assisting + Answering + Discovering — research mode, gap detection, writing assistance, footnote generation, claim verification, tarjih absorption. §4.A.5, §4.A.2.
- Scenario 5 (Teaching Mode): Teaching + Navigating — lesson plan generation, anticipated question preparation, depth verification. §4.A.3, §4.A.5.
- Scenario 6 (Book Briefing): Answering + Navigating — source metadata presentation, prerequisite contextualizing, edition comparison. §4.A.2, §4.A.6.
- Scenario 7 (Science Map): Navigating — taxonomy visualization with engagement overlay, prerequisite graph display, coverage analytics. §4.A.6.
- Scenario 8 (Correction): feedback integration — error identification, correction propagation, pattern detection. §4.A.7.

## 2. Input Contract

The scholar interface receives input from two categories: user input (from Rayane) and system state (from engines and components).

### 2.1 User Input

**Conversational messages.** Natural language messages in any of the owner's languages (Arabic, Dutch, French, English). The interface detects the language and responds in the same language, except for scholarly content which is always in Arabic (D-032). Messages may contain: questions about the library's content ("ما هو تعريف المبتدأ عند البصريين؟"), commands ("start a curriculum in Nahw"), references to past interactions ("that position we discussed yesterday"), requests for specific capability domains ("generate a lesson plan for باب الحال"), or scholarly production input ("here is my tarjih on this topic").

**Structured actions.** The owner may perform explicit actions through the interface: starting/pausing/resuming a curriculum, marking content as studied, triggering a Socratic assessment, bookmarking or annotating content, declaring a focus area, switching modes (learning/research/teaching), requesting a book briefing for a source, navigating the taxonomy tree, requesting a science map visualization, or submitting a correction.

**File input.** The owner may provide files for manual source acquisition: iPhone photographs of book pages, downloaded PDFs, text files. These are passed through to the source engine for processing — the scholar interface validates that the file type is recognized and routes it appropriately. The interface does not process files itself.

**Validation on user input.** Empty messages are ignored. Messages longer than 10,000 characters are truncated with a warning (scholarly questions are rarely this long — excessive length usually indicates pasted text that should go through manual source input). Structured actions are validated against the action schema: unrecognized actions return `SI_UNKNOWN_ACTION`. File inputs are validated for supported types (image/jpeg, image/png, application/pdf, text/plain, text/html) — unsupported types are rejected with `SI_UNSUPPORTED_FILE_TYPE` and the owner is informed which types are accepted.

### 2.2 System State (Read)

The scholar interface reads from multiple system components. All reads are through defined APIs — the interface never reads files directly from engine output directories.

**From taxonomy engine output:**
- Science trees: the complete taxonomy tree for each science, including node hierarchy, narrative ordering, prerequisite edges, cross-science links, and terminology synonyms.
- Placed excerpts: all placed excerpts at any given leaf, with full upstream metadata (source_id, passage_id, primary_author_id, quoted_scholars, evidence_refs, takhrij_data, content_types, school, self_containment_score, physical pages, layer attribution, confidence scores).
- Coverage analytics: per-leaf coverage records (total excerpts, school coverage, temporal span, gaps, significance score, difficulty estimate, duplicate clusters).

**From synthesis engine output:**
- Entries: the synthesized entries at any given leaf, with content structure (prerequisites, topic_situation, core_treatment, scholarly_positions, edge_cases, khilaf_analysis, temporal_narrative, what_next, analytical_layer, critical_analysis), citations with grounding_type, generation metadata, owner constraints, version history, and change summaries.

**From scholar_authority component:**
- Scholar records: canonical identities, biographical data, school affiliations, work lists.
- Graph queries: teacher-student chains, intellectual genealogy subgraphs, scholarly connection paths.
- Name resolution: candidate matching for ambiguous scholar references in user queries.

**From user_model component:**
- Knowledge state: per-leaf mastery levels and confidence scores.
- Engagement history: what Rayane has interacted with, when, how deeply.
- Gap analysis: topic gaps, school gaps, temporal gaps, science gaps, with severity and actionability.
- Curriculum state: active curricula, current positions, completion stats, review backlogs.
- Scholarly profile: per-science expertise levels, study preferences, study patterns.
- Alerts: unread alerts from processing engines and system events.
- Bookmarks and annotations: Rayane's personal markers and notes.
- Spaced repetition state: due reviews, upcoming reviews, review statistics.

**From source engine output (via placed excerpt provenance):**
- Source metadata: source title, author profile, edition details, work classification, text fidelity signal, source authority level, work relationships.
- Source registry: available sources per work, preferred editions, acquisition status.

**From feedback component:**
- Active corrections: owner corrections that affect current entries.
- Pattern rules: learned patterns from past corrections that constrain future synthesis.
- Correction history: what was corrected, when, how the system adapted.

### 2.3 System State (Write)

The scholar interface writes exclusively to the user_model component through its event API:

- **Engagement events:** `viewed`, `read`, `studied` transitions with duration and interaction signals.
- **Assessment results:** per-question Socratic assessment outcomes with comprehension scores.
- **Curriculum actions:** `start_curriculum`, `complete_topic`, `skip_topic`, `pause_curriculum`, `resume_curriculum`, `abandon_curriculum`.
- **Review results:** FSRS ratings (Again/Hard/Good/Easy) for spaced repetition items.
- **Bookmarks:** target, label, context.
- **Annotations:** target, anchor, content, annotation_type (note/question/disagreement/connection/tarjih).
- **Focus declarations:** science, branch, or topic that Rayane is currently focusing on.
- **Scholarly production events:** tarjih submitted, research note created, lesson plan generated.
- **Alert actions:** alert read, alert dismissed, alert acted upon.

The scholar interface also writes to the feedback component when the owner submits a correction (§4.A.7).

## 3. Output Contract

The scholar interface produces output in two categories: responses to the user and engagement data to the user model.

### 3.1 Response Format

Every response from the scholar interface follows a structured format, even if the presentation is conversational:

```
{
  response_id: string,
  timestamp: ISO datetime,
  mode: "learning" | "research" | "teaching",
  capability_domain: string,  // which domain(s) generated this response
  content: {
    text: string,             // the natural language response (Arabic for scholarly content, user's language for interface)
    structured_data: object,  // optional — citations, positions, visualizations, etc.
    citations: [citation],    // every factual claim traced to source
    suggested_actions: [action],  // what the user might want to do next
    assessment_question: object | null,  // Socratic follow-up if applicable
  },
  grounding: {
    library_grounded_claims: integer,
    llm_contributed_claims: integer,
    ungrounded_claims: integer   // should be 0 for factual responses
  },
  user_model_events: [event]  // engagement events generated by this interaction
}
```

**Guarantees about responses:**

- **Grounding.** Every factual claim about Islamic scholarship in the response is either (a) traced to a specific excerpt from a specific source in the library (`library_grounded`), or (b) explicitly marked as LLM-contributed context (`llm_contributed`) with lower certainty. The interface never presents LLM-contributed claims as library-verified facts. If the library has no relevant excerpts for a query, the interface says so: "The library does not have content on this topic yet. Based on my training knowledge: [LLM response, clearly marked as unverified]. To add verified content, consider acquiring [suggested source]."

- **Citation traceability.** Every `library_grounded` claim includes a citation: source title, author, edition, volume, page. The owner can verify any claim against the physical book. This is non-negotiable — it is the scholarly integrity baseline (DOMAIN.md §1: "Every attribution must be verified. Every claim must be sourced.").

- **No fabricated citations.** The interface never invents a citation. If it cannot locate the specific excerpt backing a claim, it either omits the claim or clearly marks it as LLM-contributed. A wrong citation (wrong page, wrong author, wrong source) is a critical integrity violation — worse than admitting ignorance.

- **Scholarly tone without pretension.** Responses are clear and precise without being unnecessarily formal or using jargon the owner hasn't encountered. The interface adapts to the owner's current expertise level (from user model): beginner-level responses define terms and explain context; advanced-level responses assume familiarity and focus on nuance.

- **Arabic scholarly content integrity.** When presenting Arabic text from excerpts or entries, the interface preserves the original text exactly — no paraphrasing of primary source quotes. Diacritics, when present in the source, are preserved. The interface may add its own explanatory text around the original, clearly distinguished.

### 3.2 Response Types

The interface produces several distinct response types, each with specific structural requirements:

**Factual answer.** A direct answer to a knowledge question. Contains: the answer text, supporting citations, confidence level (based on how well the library covers this topic), and a suggested action (e.g., "study this topic in depth" or "compare with another school's position").

**Entry presentation.** Presents a synthesized entry to the owner. Contains: the full entry content (from synthesis engine output), rendered with the appropriate depth for the owner's expertise level, with engagement tracking signals (the interface reports the presentation as a `viewed` event). If the entry has been updated since the owner last studied it, the change summary is highlighted.

**Comparative analysis.** Presents positions from multiple schools or scholars side by side. Contains: each position with its holders, evidence, and citations, organized by the user's preference (chronological, by school, by evidence type). May include cross-school links and the interface's analytical notes (marked as LLM-contributed).

**Curriculum proposal.** A structured learning path. Contains: the sequence of topics with estimated study times, the rationale for the ordering (prerequisites, classical progression), the sources that will be used, and the assessment strategy at each checkpoint.

**Book briefing.** A comprehensive pre-reading intelligence report (D-022). Contains: author profile, work classification, genre chain, scope and coverage, edition quality assessment, prerequisites, study context, comparative edition analysis. See §4.A.2.6 for full specification.

**Science map.** A visualization-ready data structure representing the topology of a science. Contains: all nodes with engagement overlay (green/yellow/gray), prerequisite edges, significance scores, coverage metrics, and gap highlights. The rendering is a frontend concern — the interface provides the data.

**Assessment result.** The outcome of a Socratic assessment. Contains: the questions asked, the owner's responses, the evaluation of each response (correct/partial/incorrect with explanation), the new comprehension score, and the updated mastery level.

**Correction acknowledgment.** Response to an owner correction. Contains: what was wrong, what was corrected, which downstream artifacts are affected, and whether a pattern was detected. See §4.A.7.

### 3.3 Metadata Pass-Through (D-023)

The scholar interface is the terminal consumer of the metadata chain in the user-facing direction. It does not produce output consumed by downstream engines. However, it preserves the full provenance chain in its responses: every citation traces through entry → excerpt → passage → normalized package → frozen source. When the owner asks "where does this claim come from?", the interface can trace the complete chain from the displayed text back to the original book, page, and author.

The interface also generates new metadata: engagement events, assessment results, annotations, and scholarly production records. These flow to the user model, which makes them available to all components — including processing engines that use the user model's expertise levels for confidence calibration (D-042) and the synthesis engine that may adjust analytical depth based on what Rayane has mastered.

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Guiding: Curriculum Design and Structured Learning

The guiding domain is the first capability the owner needs. Before Q&A, before research, before anything else — Rayane needs structure: what to study, in what order, starting from which level. KR must fill the role of both the library and the guide (DOMAIN.md: "KR must fill the role of both the library and the guide").

**§4.A.1.1 — Curriculum generation.**

A curriculum is a structured learning path through a portion of the taxonomy tree. The scholar interface generates curricula; the user model stores state within them (user_model SPEC §4.A.5).

Curriculum generation takes three inputs: (a) the target science or branch, (b) the owner's current expertise level in that science (from user model), and (c) the available content in the library (from taxonomy coverage analytics). Generation follows three principles:

*Principle 1: Classical pedagogical progression.* Islamic sciences have established learning progressions refined over centuries. In Nahw: foundational mutun (الآجرومية, ملحة الإعراب) → intermediate texts (قطر الندى, شذور الذهب) → advanced reference works (ألفية ابن مالك with شرح ابن عقيل). In Hanafi fiqh: القدوري → الاختيار or الكنز → الهداية → حاشية ابن عابدين. These progressions are encoded in a curriculum knowledge base — a structured data file per science that records the classical text sequence with levels, prerequisites, and estimated scope. The curriculum knowledge base is initially populated from domain research (the islamclass.wordpress.com progressions, SeekersGuidance curricula, and classical madrasa syllabi), and grows as the owner provides domain input or as the library's content suggests adjustments.

*Principle 2: Taxonomy-guided topic sequencing.* Within each text, topics follow the taxonomy tree's narrative ordering (taxonomy SPEC §3.2). The narrative ordering is the pedagogical sequence: topics are ordered so that prerequisites come before dependents, foundational concepts before derived ones. The curriculum respects this ordering. When the taxonomy tree's narrative ordering conflicts with the classical text's chapter ordering, the curriculum follows the taxonomy's ordering with a note explaining the deviation (the taxonomy may reorder topics for better learning, while the text's ordering may reflect historical convention rather than pedagogical logic).

*Principle 3: Content-driven adaptation.* A curriculum can only cover topics for which the library has content. If the library has a full set of excerpts and entries for الآجرومية but only sparse coverage for قطر الندى, the curriculum prioritizes الآجرومية and flags the gap: "After completing الآجرومية, the next text in the classical progression is قطر الندى. The library's coverage is currently thin (12 excerpts, 4 entries). Consider acquiring a source for this text before proceeding." The curriculum never skips a classical progression level silently — it either covers it or explicitly flags the gap with an acquisition suggestion.

**Curriculum structure.** Each generated curriculum contains:
- `curriculum_id`: assigned at creation.
- `science`: the target science.
- `source_texts`: the ordered list of texts in the classical progression, with per-text metadata (genre, level, author, approximate topic count).
- `topic_sequence`: the flattened sequence of taxonomy leaf_ids that the curriculum covers, respecting both text ordering and prerequisite dependencies.
- `assessment_checkpoints`: positions in the sequence where Socratic assessment is required before proceeding. Checkpoints are placed at: (a) the end of each major chapter (باب), (b) before any topic that has a `hard` prerequisite dependency, and (c) at configurable intervals (default: every 10 topics).
- `estimated_duration`: per-topic and total, based on content length and the owner's observed pace (from user model study patterns, if available; otherwise from configurable defaults per science).
- `review_strategy`: how spaced repetition items are integrated. Default: after each assessment checkpoint, the interface creates review items for the assessed topics.

**First curriculum special case.** The very first curriculum (Scenario 1) has additional requirements. The owner has no prior engagement, no expertise, and no study history. The interface must: (a) present the curriculum as a welcome message with clear structure and expectations (see Scenario 1 in USER_SCENARIOS.md), (b) begin with the simplest text in the science (for Nahw: الآجرومية), (c) set assessment checkpoints conservatively (every 5 topics initially, widening as confidence grows), and (d) offer to adjust pacing based on early assessment results: "You scored 0.95 on the first 5 topics — would you like to accelerate the pace?"

**Multi-science curricula.** Rayane may study multiple sciences simultaneously. The interface supports multiple active curricula (user_model SPEC §4.A.5). When presenting daily study recommendations, the interface considers all active curricula and their review backlogs, prioritizing: (a) overdue spaced repetition reviews from any curriculum, (b) the curriculum the owner most recently engaged with, (c) cross-science connections that would reinforce multiple curricula simultaneously.

**§4.A.1.2 — Daily study session orchestration.**

When the owner begins a study session, the interface generates a session plan based on current state:

1. **Review backlog check.** Query the user model for overdue spaced repetition items across all active curricula. If overdue items exist, present them first: "You have 5 review items due — 3 from باب المبتدأ والخبر, 2 from باب الفاعل. Starting with reviews." Reviews are conducted before new material.

2. **Curriculum position check.** For the active curriculum(s), identify the next topic(s). Present the topic with its entry, contextualized for the owner's level: "Next topic: تعريف الخبر. This is the second part of the subject-predicate pair you studied yesterday. Here's the entry: [entry content, presented at the owner's expertise level]."

3. **Source alerts check.** Query the user model for unread processing alerts relevant to active curricula. If a new source was recently processed that adds excerpts to upcoming topics, mention it: "A new source was acquired: شرح الكفراوي على الآجرومية. It adds 23 new excerpts to topics in your current curriculum."

4. **Cross-science connection check.** If the owner has multiple active curricula, check for cross-science links between the current topic and topics in other curricula: "Today's Nahw topic (الاستثناء) connects to a topic you'll encounter in your Usul al-Fiqh curriculum — remember this connection."

The session plan is a suggestion, not a constraint. The owner can redirect at any point: "Skip reviews, take me to the next topic" or "I want to explore a completely different topic today."

#### §4.A.2 — Answering: Library-Grounded Conversational Q&A

The answering domain handles all knowledge queries. Every answer is grounded in the library's verified content — the interface never generates unverified claims as if they were library knowledge.

**§4.A.2.1 — Query classification.**

When the owner asks a question, the interface classifies it to determine the appropriate response strategy. Classification uses the query's content, the owner's current mode, active curricula, and recent conversation context.

Query types:

- **Single-topic factual.** "What is the definition of المبتدأ?" → Retrieve the entry at the relevant leaf. Present core_treatment and scholarly_positions. Cite sources.

- **Single-school factual.** "What is the Hanafi position on [topic]?" → Retrieve the school-group entry at the relevant leaf for the specified school. If no school-specific entry exists, retrieve excerpts with that school attribution and synthesize an on-the-fly response. Cite sources.

- **Comparative.** "How do the schools differ on [topic]?" or "Compare the Basran and Kufan definitions of [term]." → Retrieve entries for all schools (or specified schools) at the relevant leaf. Present side by side with chronological ordering, evidence types, and the interface's comparative analysis (marked as LLM-contributed). Cite all sources.

- **Evidence-chain.** "What evidence supports the Shafi'i position on [topic]?" → Extract from the entry's scholarly_positions the specified school's evidence_types and evidence_refs. Trace each evidence reference back to its excerpt and source. Present the complete evidence chain with citations.

- **Historical evolution.** "How did the definition of [term] change over time?" → Retrieve the entry's temporal_narrative if available. If not available (or if the entry doesn't cover temporal evolution), extract author death dates from all excerpts at the leaf, sort chronologically, and present positions in temporal order with the interface's narrative framing (marked as LLM-contributed where it adds context beyond what the entry states).

- **Scholar-specific.** "What are Sibawayhi's positions in my library?" → Query the scholar_authority component for the scholar's canonical_id, then query all placed excerpts attributed to that scholar across all sciences. Group by topic, present with citations.

- **Cross-science.** "How does الاستثناء in Nahw relate to الاستثناء in Usul?" → Read cross-science links from the taxonomy engine output. Retrieve entries at both leaves. Generate a cross-science analysis that connects the two treatments, drawing on excerpts from both sciences. Mark the synthesis as LLM-contributed where it goes beyond what the entries explicitly state.

- **Meta-library.** "How many sources do I have on Nahw?" or "Which topics have no Maliki coverage?" → Query coverage analytics and user model gap analysis. Present statistics and actionable recommendations.

- **Ungrounded.** The query asks about something the library doesn't cover. The interface detects this (no relevant excerpts or entries found) and responds honestly: "The library does not have verified content on this topic. Based on my training knowledge: [response, clearly marked]. To add verified content, consider acquiring: [source suggestion based on source registry knowledge or LLM research]."

**§4.A.2.2 — Retrieval strategy.**

For each query, the interface retrieves relevant content using a multi-stage strategy:

*Stage 1: Topic identification.* Map the query to taxonomy leaf_ids. This uses: keyword matching against leaf titles and terminology synonyms, semantic similarity between the query and leaf titles (using an Arabic-capable embedding model), and conversation context (if the query references "this topic" or "the previous position," resolve from the current session's context). If the mapping is ambiguous (multiple candidate leaves), the interface either asks for clarification ("Do you mean الاستثناء in Nahw or in Usul?") or retrieves from all candidates if the query is broad enough to warrant it.

*Stage 2: Content retrieval.* At each identified leaf, retrieve: the synthesized entry (if it exists and is not stale), the placed excerpts (always — even when an entry exists, because the interface may need specific excerpts for citations), and coverage analytics (for context: how well-covered is this topic?).

*Stage 3: Scholar context enrichment.* For each scholar mentioned in the retrieved content, query the scholar_authority component for biographical data, school affiliations, and teacher-student relationships. This enrichment enables the interface to contextualize positions with scholarly metadata: "سيبويه (d. 180 AH), founder of systematic Basran grammar, student of الخليل بن أحمد..."

*Stage 4: User context overlay.* Query the user model for the owner's engagement with the retrieved content: has he seen this entry before? What is his mastery level on this topic? What are his prerequisites' confidence scores? This overlay determines response depth: a first-time viewer gets the full entry with context; someone revisiting gets a focused response addressing their specific question.

**§4.A.2.3 — Response generation.**

The interface generates responses using an LLM call with the retrieved content as context. The prompt includes:

- The user's query.
- The retrieved entry content (if exists).
- Relevant placed excerpts with full metadata.
- Scholar authority data for mentioned scholars.
- The user's expertise level in the relevant science(s).
- The user's specific question history on this topic (from engagement records).
- The grounding requirement: every factual claim must be traceable to a specific excerpt, or explicitly marked as LLM-contributed.

The LLM is instructed to: answer the query using ONLY the provided library content for factual claims, add contextual framing and connections as LLM-contributed content (clearly distinguished), adapt explanation depth to the owner's expertise level, include citations in a structured format that the interface can render, and suggest a natural follow-up (next topic, deeper question, or assessment prompt).

**Response verification.** Before presenting the response to the owner, the interface performs a citation check: every claimed citation must reference an excerpt_id that exists in the retrieved content. Citations that reference non-existent excerpts are stripped with a warning log (this indicates hallucination in the citation generation). This verification catches the most dangerous error — fabricated citations that appear legitimate.

**§4.A.2.4 — Handling stale entries.**

An entry may be stale (its `is_stale` flag is true, meaning new excerpts have been placed at its leaf since generation). The interface handles stale entries as follows:

- If the entry is stale and the new excerpts are minor (fewer than 3 new excerpts from the same schools already represented): present the existing entry with a note: "This entry is being updated — 2 new excerpts have been added. The core positions are unchanged."
- If the entry is stale and the new excerpts are significant (new school representation, new evidence types, or more than 5 new excerpts): present the existing entry with a prominent warning: "This entry needs regeneration — significant new content has been added. The following positions may not be fully represented: [list based on new excerpt metadata]." Queue a regeneration request.
- If no entry exists at a leaf (the leaf has placed excerpts but synthesis hasn't run yet): generate an on-the-fly response directly from the placed excerpts, clearly marked as "from raw excerpts, not yet synthesized into a formal entry."

**§4.A.2.5 — Multi-turn conversation management.**

The interface maintains session context across multiple exchanges within a single session. Context includes: the topics discussed, the entries and excerpts retrieved, the mode, the active curriculum position, and the owner's expressed interests and questions. This context enables natural multi-turn conversation:

- "Tell me about المبتدأ." → Full entry presentation.
- "What about the Kufan view?" → Context: we're discussing المبتدأ. Retrieve Kufan-specific excerpts.
- "Compare that with what we discussed yesterday about الفاعل." → Context: compare Kufan position on المبتدأ with yesterday's discussion of الفاعل (retrieved from user model engagement history).

Session context is maintained in memory for the duration of the session. Cross-session context (referencing past conversations) is resolved through the user model's engagement records and annotation history — the interface does not maintain a full conversation transcript across sessions, but it can reconstruct the owner's interaction history from the user model.

**§4.A.2.6 — Book briefing generation.**

The book briefing (D-022) is a comprehensive pre-reading intelligence report generated when the owner encounters a new source. The briefing is generated from source metadata (from the source engine's registry), the scholar authority component, the taxonomy coverage analytics, and LLM research for context not in the library.

Briefing structure (see Scenario 6 for an example):

1. **Source identification.** Title, author (full name, known_as, death dates), work type/genre.
2. **Author profile.** From scholar_authority: biography, scholarly standing, school, teachers, students, other major works, methodology. Enriched with LLM-contributed context (historical setting, reputation) marked as such.
3. **Genre chain.** If this is a sharh/hashiyah/mukhtasar: the full derivative chain. "This is a hashiyah on [sharh] on [matn]." Each work in the chain identified with author and date.
4. **Classification.** Science(s), level (beginner/intermediate/advanced/specialist), source authority (primary/reference/modern compilation).
5. **Scope and coverage.** What topics this source covers (estimated from table of contents if available, or from LLM knowledge). What it does NOT cover. Theory vs. practice proportion.
6. **This edition.** Tahqiq quality, publisher, text fidelity signal. Comparison with other editions of the same work in the library or in source registries.
7. **Prerequisites.** What knowledge is needed before reading this source. Two levels: (a) prerequisite topics (mapped to taxonomy leaves — the interface checks the owner's mastery of each and reports: "You've mastered 8/12 prerequisites"), (b) prerequisite texts (from the classical progression — "Read القدوري before this").
8. **Study context.** Where this source fits in the classical learning progression for its science. What to read after finishing it.
9. **Recommended approach.** Based on the owner's expertise level and the source's level: sequential reading, chapter-by-chapter reference, or selective study. If the source is above the owner's level, warn and suggest prerequisites.

The book briefing is written to the user model as a scholarly production event (type: `briefing_consulted`) so the interface can later reference it: "Remember from your briefing on حاشية ابن عابدين — the prerequisites included intermediate Hanafi fiqh."

#### §4.A.3 — Teaching: Socratic Assessment and Knowledge Verification

The teaching domain ensures that reading translates into understanding. It is the mechanism that distinguishes "has seen" from "has understood" in the user model (D-018: a gap in the library IS a gap in Rayane's scholarship — and "scholarship" means comprehension, not just exposure).

**§4.A.3.1 — Socratic assessment design.**

Socratic assessment tests the owner's comprehension of a topic through guided questioning, not multiple-choice quizzes. The interface asks questions that require the owner to articulate understanding in his own words. Assessment is triggered by: (a) a curriculum checkpoint (§4.A.1.1), (b) the owner's explicit request ("test me on المبتدأ"), (c) the interface's judgment that the owner has studied enough to benefit from assessment (e.g., the owner has read an entry and spent significant time — the interface may suggest: "Would you like me to test your understanding of this topic?").

Assessment questions are generated by an LLM call with the following inputs: the entry content for the topic being assessed, the placed excerpts (for specific quotes the owner should be able to reference), the owner's expertise level, the topic's prerequisite chain (to test whether prerequisites are solid), and the assessment question type (recall, recognition, application, comparison — see user_model SPEC §4.A.3 for definitions).

**Question generation rules:**

- **Recall questions** test raw comprehension: "In your own words, define المبتدأ." "What are the conditions for a noun to be a مبتدأ?" Generated from the entry's core_treatment.
- **Recognition questions** test the ability to identify: "Which of these statements reflects the Basran definition vs. the Kufan definition?" Generated from scholarly_positions in the entry.
- **Application questions** test the ability to apply rules: "In the sentence 'في الدار رجلٌ', identify the مبتدأ and explain why." Generated from the entry's edge_cases.
- **Comparison questions** test the ability to distinguish: "How does سيبويه's definition differ from ابن السراج's? What did ابن السراج add?" Generated from the entry's temporal_narrative and scholarly_positions.

**Assessment progression.** For a given topic, the assessment proceeds through escalating question types: recall → recognition → application → comparison. The interface asks 2-4 questions per assessment session (enough to evaluate comprehension without being exhausting). If the owner struggles with recall, the assessment does not proceed to application — it identifies the gap and suggests re-study.

**§4.A.3.2 — Assessment evaluation.**

The owner's responses are evaluated by an LLM call with: the question, the expected answer (derived from the entry content), the owner's actual response, and evaluation criteria specific to the question type.

Evaluation produces:
- Per-question score: 0.0 (incorrect), 0.5 (partial — correct concept but missing nuance or containing an imprecision), 1.0 (correct and well-articulated).
- Per-question feedback: what was correct, what was missing, what was incorrect. Feedback references specific entry content: "You correctly identified that المبتدأ is a nominative noun. However, you didn't mention the key Basran insight — that it's defined by its semantic role (what's being talked about), not its position. See: [excerpt citation]."
- Overall comprehension score: the average of per-question scores, weighted by question type (comparison questions weighted higher than recall — they test deeper understanding).

**Assessment integrity.** The interface uses multi-model consensus (via the consensus component, D-041) for evaluation of ambiguous responses. If the owner's response is nuanced and the primary model's evaluation is uncertain (confidence < 0.70), a second model evaluates independently. If both agree, the evaluation stands. If they disagree, the more generous evaluation is presented to the owner with a note: "Your answer is on the right track — let me refine the question to check more precisely."

The interface never gives false positive assessments. Telling the owner he understands something when he doesn't is worse than being strict — it creates a false knowledge state in the user model (DOMAIN.md: "An error in the library is an error in Rayane's mind"). Assessment evaluation errs on the side of caution: if uncertain, score 0.5 (partial) with specific feedback, not 1.0 (correct).

**§4.A.3.3 — Spaced repetition orchestration.**

After each successful assessment, the interface creates spaced repetition review items in the user model (user_model SPEC §4.A.3). Review items are created at the entry level (not at the excerpt level — the entry is the knowledge unit Rayane should retain). Each review item has a question_type that matches the highest question type the owner successfully answered during assessment.

When reviews are due, the interface presents them as part of the daily study session (§4.A.1.2). Review presentation: the interface asks a question about the topic (generated fresh — not the exact same question from the original assessment), evaluates the response, and reports the FSRS rating to the user model. If the owner fails a review (rating: Again), the interface suggests re-study: "Your answer on باب المبتدأ wasn't as strong as last time. Would you like to revisit the entry before continuing?"

**§4.A.3.4 — Knowledge gap detection from assessments.**

Assessment results reveal specific gaps. The interface tracks patterns:

- If the owner consistently scores low on comparison questions but high on recall, the gap is in analytical depth: "You know the individual positions well, but struggle to compare them. Try focusing on the entries' khilaf_analysis sections."
- If the owner scores low on application questions, the gap is in practical understanding: "You can define المبتدأ but struggle to identify it in complex sentences. Let me generate more practice examples."
- If assessment on a topic reveals that a prerequisite was not understood (the owner's answer reveals confusion about a prerequisite concept), the interface flags the prerequisite gap: "Your answer suggests you're unclear about العامل (grammatical operator) — this is a prerequisite for understanding المبتدأ. Let me take you back to that topic before we continue."

These patterns are stored as annotations (type: `gap_pattern`) and inform future curriculum pacing and assessment scheduling.

#### §4.A.4 — Discovering: Proactive Intelligence

The discovering domain surfaces knowledge the owner doesn't know to look for. This is what transforms KR from a passive reference into an active scholarly partner.

**§4.A.4.1 — New content alerts.**

When processing engines add new content to the library (new sources acquired, new excerpts placed, new entries generated), the user model receives alert events (user_model SPEC §4.A.7). The scholar interface consumes these alerts and presents them to the owner with contextual relevance:

- **Alert relevance scoring.** Not all alerts are equally important. The interface scores each alert based on: overlap with active curricula (alerts about topics in the current curriculum are highest priority), overlap with recent study focus (topics the owner studied in the last 7 days), school coverage improvement (a new Maliki source for a topic where only Hanafi and Shafi'i were represented is highly valuable), and temporal coverage improvement (a new early-period source for a topic only covered by late-period scholars).

- **Alert presentation.** High-priority alerts are presented at the start of study sessions (§4.A.1.2). Lower-priority alerts are batched into periodic briefings (see §4.A.4.4). The interface never interrupts active study for an alert — alerts are queued and presented at natural transition points.

**§4.A.4.2 — Cross-science connection discovery.**

When the owner studies a topic that has cross-science links in the taxonomy (taxonomy SPEC §3.2 cross_science_links.json), the interface surfaces the connection at an appropriate moment:

- **During learning mode:** After the owner completes a topic, if a cross-science link exists and the linked topic is in a science the owner has studied: "This Nahw concept (الاستثناء) has implications in Usul al-Fiqh — a topic you've seen in your Usul curriculum. Would you like to see the connection?"
- **During research mode:** Cross-science links are always surfaced as part of comparative analysis, without waiting for the owner to ask.

The interface does not surface cross-science connections for sciences the owner has not started studying — this would be confusing without context. It waits until the owner has at least `beginner` expertise in both sciences before presenting the connection.

**§4.A.4.3 — Coverage gap alerting.**

The user model's gap analysis (user_model SPEC §4.A.4b) computes what's missing. The scholar interface transforms these gaps into actionable intelligence:

- **School gaps:** "In your study of المبتدأ, you've seen the Basran position from 3 sources but no Kufan source. The library has 2 Kufan excerpts at this leaf — would you like to study them?"
- **Temporal gaps:** "All your sources on this topic are from after 900 AH. The library has an excerpt from الكتاب (Sibawayhi, d. 180 AH) that gives the foundational treatment. Worth reading for historical context."
- **Source gaps:** "The library has no Maliki source for this topic. The Muwatta of Imam Malik likely addresses this — shall I check if it's available for acquisition?"

Gaps are presented as opportunities, not deficiencies. The tone is: "here's something valuable you haven't explored yet" — not "your knowledge is incomplete."

**§4.A.4.4 — Scholarly briefing generation.**

The interface generates periodic scholarly briefings — concise, personalized summaries of what's new and relevant. Briefing frequency is configurable (daily, weekly, or on-demand). Each briefing contains:

- **Study progress summary.** Topics completed this period, assessment results, curriculum position, milestones reached (from user model's growth trajectory, §4.B.1).
- **New content relevant to current study.** Sources acquired, excerpts placed at curriculum topics, entries regenerated.
- **Gap discoveries.** New gaps detected based on current study progress.
- **Cross-science connections.** Connections between recently studied topics and other sciences.
- **Suggested focus.** Based on the user model's analysis of where the owner's study would have the most impact: "Strengthening your understanding of العامل theory would improve your scores on 3 upcoming topics."

**§4.A.4.5 — Contradiction detection surfacing.**

The synthesis engine may detect contradictions between sources or within a single author's corpus (synthesis SPEC §4.B). The scholar interface presents detected contradictions as research opportunities:

- **Intra-author contradiction:** "Ibn Qudamah's position in المغني (vol. 3 p. 245) appears to differ from his statement in الكافي (vol. 2 p. 112). This may reflect a change in position, or a difference in context. Would you like to investigate?"
- **Cross-source contradiction on reported facts:** "Two sources in the library disagree on whether Ibn al-Sarraj was a student of al-Mubarrad or studied independently. Source A (الأصول, editor's note) says he was a direct student. Source B (طبقات النحويين) says he studied only through al-Mubarrad's writings. This is a domain question — what do you think?"

The interface presents contradictions with their sources cited so the owner can evaluate independently. It does not resolve contradictions on its own — this is a scholarly judgment that belongs to the owner (or to the synthesizer with lower confidence). Contradictions are flagged as high-value learning opportunities because they force deep engagement with sources.

#### §4.A.5 — Assisting: Scholarly Production Support

The assisting domain supports the owner in producing original scholarship — the third leg of the "complete scholar" goal (learning + research + teaching). This transforms KR from a study aid into a research partner.

**§4.A.5.1 — Evidence compilation.**

When the owner declares a research topic ("I want to write about how different grammatical interpretations of Quran 2:228 led to different fiqh rulings on the iddah period"), the interface compiles all relevant evidence from the library:

1. **Topic identification.** Map the research topic to taxonomy leaves across all relevant sciences (this example spans Nahw + Fiqh + Tafsir).
2. **Excerpt retrieval.** Retrieve all placed excerpts at the identified leaves, grouped by school, author, and time period.
3. **Evidence chain construction.** For each school's position, construct the complete evidence chain: the position statement, the Quranic evidence, the hadith evidence (with takhrij data), the analogical reasoning, and the scholarly consensus claims.
4. **Gap detection.** Identify what's missing: "You have 14 excerpts from 9 sources. Gap detected: no Zahiri school source. Ibn Hazm likely addresses this in المحلى."
5. **Presentation.** Present the compiled evidence as a structured research dossier: positions by school, evidence by type, sources with full citations, identified gaps.

**§4.A.5.2 — Writing assistance.**

When the owner is writing (a tarjih, a research note, a paper), the interface assists with:

- **Footnote generation.** When the owner writes a claim, the interface matches it against library excerpts and generates academic footnotes: "You wrote 'the majority position is X' — citing: [source 1, vol. page], [source 2, vol. page], [source 3, vol. page]."
- **Claim verification.** The interface checks every claim in the owner's text against the library: "You wrote 'Ibn Malik considers المصدر and المفعول المطلق to be the same.' My analysis of the library excerpts suggests this is a subset relationship, not equivalence (see Alfiyyah line 199). Please verify."
- **Citation completeness check.** The interface identifies unsourced claims: "This sentence makes a factual claim that I cannot trace to any excerpt in the library. Would you like to add a source?"
- **Scholarly precision check.** The interface flags imprecise language: "You wrote 'the majority hold X.' More precisely: 6 sources support X and 4 support Y. Three of the six for X are from a single school. The claim 'majority' depends on whether you mean across all schools or within a specific school."

**§4.A.5.3 — Tarjih scaffolding.**

When the owner wants to form a scholarly opinion (tarjih) on a topic, the interface provides a structured framework:

1. **تحرير المسألة (formulating the question).** The interface presents the precise scholarly question at stake, distinguishing it from related but different questions. "The question is: does [specific issue]? This is distinct from [related question] which is addressed at [other leaf]."
2. **Position inventory.** All known positions with their holders, evidence, and reasoning — drawn from the entry's scholarly_positions and supplemented by placed excerpts.
3. **Evidence strength analysis.** For each position: what evidence type supports it, what hadith grading is relevant, whether consensus claims are contested.
4. **Comparative framework.** Which positions are stronger by which criteria: evidence quantity, evidence quality, scholarly consensus, methodological soundness.
5. **Precedent analysis.** How earlier scholars weighed these same positions — from the entry's temporal_narrative and from the owner's previously recorded tarjih on related topics.

The owner then writes their tarjih. The interface stores it as an annotation (type: `tarjih`) at the relevant leaf, linked to the entry and the evidence inventory. The tarjih becomes part of the library — future queries on this topic will surface: "You previously concluded that [position X] is stronger because [reasoning]."

**§4.A.5.4 — Lesson plan generation.**

When the owner enters teaching mode and requests a lesson plan (Scenario 5), the interface generates a structured teaching plan:

1. **Topic analysis.** Retrieve the entry content and identify: core concepts, common misconceptions, edge cases, prerequisite knowledge required of the audience.
2. **Lesson structure.** Based on the topic's complexity and the specified time: introduction (definition/context), core content (positions, evidence), practice (examples, edge cases), assessment (anticipated student questions with answers).
3. **Source references.** Which excerpts to cite during the lesson, with page references for the owner to have the physical books ready.
4. **Depth verification.** Before generating the plan, the interface checks the owner's mastery of the topic: "Before you teach this, can you explain [specific nuance]?" If the owner's response shows a gap, the interface suggests: "Your explanation of [concept] could be stronger — review [specific entry section] before teaching."

The lesson plan is stored as a scholarly production event and can be retrieved and modified later.

#### §4.A.6 — Navigating: Knowledge Exploration and Visualization

The navigating domain enables the owner to explore the library's structure visually and interactively, answering the frustration: "There's no way to see an entire science drawn out" (DOMAIN.md).

**§4.A.6.1 — Science map generation.**

When the owner requests a science map (Scenario 7), the interface generates a visualization-ready data structure:

For each node in the requested science's taxonomy tree:
- `node_id`, `title` (Arabic), `level` (branch or leaf), `children` (ordered by narrative sequence).
- `engagement_state`: `mastered` (green — confidence ≥ mastery_threshold), `studied` (yellow — confidence ≥ 0.30), `unseen` (gray — no engagement). Computed from user model knowledge state.
- `significance_score`: from coverage analytics. Determines visual weight (node size).
- `difficulty_estimate`: from coverage analytics. May affect color saturation or visual cue.
- `coverage_summary`: total excerpts, school count, temporal span. Displayed on hover/tap.
- `gap_highlights`: which school or temporal gaps exist. Displayed as red markers.

For prerequisite edges: `from_node_id`, `to_node_id`, `strength` (hard/soft). Rendered as directed arrows.
For cross-science links: `source_node`, `target_node` (in another science), `relationship_type`. Rendered as dashed cross-links.

The data structure is frontend-agnostic — it describes the content and relationships, not the rendering. The frontend (outside the scope of this SPEC) renders it as an interactive graph/tree. The interface's responsibility is to generate correct, complete, up-to-date data.

**§4.A.6.2 — Taxonomy browsing.**

The interface supports interactive taxonomy browsing: the owner navigates the tree, and at each node the interface presents:

- **At a branch node:** child topics with their engagement states, total excerpt count across all children, coverage statistics, and the narrative thread connecting this branch's topics: "This branch covers [description]. Its topics proceed from [first topic] through [last topic], following [pedagogical logic]."
- **At a leaf node:** the entry (or entry preview if stale/missing), coverage statistics per school, placed excerpt count, temporal span, gap analysis, and the prerequisite chain: "This topic depends on [prerequisites, with your mastery level for each]."

**§4.A.6.3 — Scholar network exploration.**

The interface enables browsing the scholar authority graph: the owner selects a scholar and sees their teacher-student network, their works in the library, their positions across topics, and their school affiliations. This uses the scholar_authority component's graph queries (§4.A.8 of scholar_authority SPEC).

- **Chain query:** "Show me the teaching chain from Sibawayhi to al-Mubarrad." → Returns the path with each scholar's dates, school, and major works.
- **Subgraph query:** "Show me all scholars related to [scholar] within 2 degrees." → Returns the neighborhood graph centered on the selected scholar.
- **Influence query:** "Which scholars in my library were influenced by [scholar]?" → Returns all scholars with a teacher-student connection (direct or transitive) to the selected scholar, with the excerpts in the library attributed to each.

**§4.A.6.4 — Temporal exploration.**

The interface enables exploring knowledge evolution over time: the owner selects a topic and a time range, and sees how positions evolved:

- **Timeline view.** For a given leaf: all scholarly positions sorted by holder's death date, showing when each position appeared, who refined it, and when the consensus settled (if it did). Uses the entry's temporal_narrative supplemented by excerpt metadata (author death dates).
- **Century view.** For a given science: what was the state of scholarship in each century? How many topics were settled? How many were actively debated? Uses aggregate coverage analytics across all leaves in the science.

#### §4.A.7 — Correction and Feedback Integration

When the owner identifies an error (Scenario 8), the interface handles correction at the appropriate level and propagates it through the system.

**§4.A.7.1 — Error identification.**

The owner may flag an error in: an entry (wrong attribution, misrepresented position, logical error), an excerpt (wrong school, wrong author, wrong topic), a taxonomy placement (excerpt at the wrong leaf), or metadata (wrong date, wrong work relationship). The interface captures: what is wrong (the specific claim or datum), what is correct (the owner's correction), and the evidence for the correction (excerpt reference, external knowledge, or the owner's scholarly judgment).

**§4.A.7.2 — Correction routing.**

Based on the error level, the interface routes the correction:

- **Entry-level error.** The correction is stored as an owner constraint at the relevant leaf. The entry is marked stale and queued for regeneration. The owner constraint survives regeneration — it is passed to the synthesis engine as a permanent note (synthesis SPEC §4 owner_constraints). Example: "The entry says Ibn Malik equates المصدر and المفعول المطلق. Correction: this is a subset relationship. Constraint: the synthesis engine must not present this as equivalence."

- **Excerpt-level error.** The correction is routed to the feedback component, which updates the excerpt metadata (school, author, content type). The entry at the excerpt's leaf is marked stale. If the correction changes the excerpt's leaf placement, two leaves are affected (old and new). The feedback component records the correction for pattern analysis.

- **Taxonomy-level error.** The correction is routed as an excerpt relocation request to the taxonomy engine (via the human gate). Coverage metrics update at both the source and destination leaves. Entries at both leaves are marked stale.

- **Metadata error.** The correction is routed to the appropriate component: source metadata corrections go to the source engine, scholar authority corrections go to the scholar_authority component. Downstream artifacts that depend on the corrected metadata are identified and marked stale.

**§4.A.7.3 — Pattern detection.**

After each correction, the interface queries the feedback component for patterns: "Does this correction suggest a systematic error?" The feedback component's pattern detection (feedback SPEC §4) identifies recurring error types. If a pattern is found, the interface informs the owner: "This correction reveals a pattern — the synthesizer consistently confuses subset and equivalence relationships. I've created a rule that will apply to all future synthesis, not just this entry."

Pattern corrections are the highest-value corrections — they improve all future outputs. The interface highlights this: "Your single correction improved 47 entries across 3 sciences."

[CONTINUES NEXT SESSION — §4.B (Transformative Capabilities) through §10 remaining]
