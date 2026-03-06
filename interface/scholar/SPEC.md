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

**§4.A.2.2 — Retrieval architecture.**

The scholar interface retrieves library content through a hybrid retrieval pipeline backed by a Qdrant vector store, Arabic-optimized embeddings, and cross-encoder re-ranking. The pipeline has four stages.

**Vector store design.** Qdrant (self-hosted via Docker, disk-persisted) maintains two collections:

*Excerpt embeddings collection.* One vector per placed excerpt, embedded from the excerpt's `primary_text` field using the selected Arabic embedding model. Each vector carries a structured payload: `excerpt_id`, `leaf_path`, `science_id`, `school`, `primary_author_id`, `evidence_types` (list), `content_types` (list), `death_hijri` (integer, author death date for temporal filtering), `source_id`, `placement_confidence`, `self_containment_score`. This payload enables filtered vector search — queries like "find similar content in the Hanafi school from before 400 AH" execute as a single Qdrant request combining ANN search with payload filters, with negligible filtering overhead (~1.1x).

*Entry-section embeddings collection.* One vector per entry section (one each for `core_treatment`, each `scholarly_position`, each `edge_case`, and the `analytical_layer`). Payload: `entry_id`, `leaf_path`, `science_id`, `school_group` (for school-specific positions), `section_type`. Section-level granularity enables precise retrieval — a query about edge cases retrieves edge-case sections directly rather than whole entries.

**Embedding model.** The system uses an Arabic Matryoshka embedding model — either AraGemma-Embedding-300m or Swan-Large, selected after benchmarking on KR's own corpus during initial deployment (see §8 for evaluation configuration). Matryoshka dimensionality allows trading precision for speed: full-dimension embeddings for high-stakes queries, truncated embeddings for exploratory browsing. Embeddings are generated at excerpt placement time (for placed excerpts) and at entry generation time (for entry sections). Re-embedding is triggered when an excerpt's metadata changes significantly (school attribution corrected, author reattributed) or when an entry is regenerated.

**Four retrieval strategies.** The interface selects a retrieval strategy based on query classification (§4.A.2.1):

*Targeted retrieval.* For single-topic factual queries where the topic can be identified with high confidence. Matches the query against leaf titles and terminology synonyms from the taxonomy tree's synonym index. If a leaf match confidence exceeds 0.9, retrieval proceeds directly to that leaf's content without vector search. This is the fastest path — a known topic needs no approximation.

*Semantic retrieval.* For broad, exploratory, or ambiguous queries where the topic mapping is uncertain. Executes an ANN search against the excerpt embeddings collection (top-K=20), then re-ranks with a cross-encoder. The cross-encoder receives the query and each candidate excerpt's `primary_text`, producing a relevance score. After re-ranking, the top-5 results (or all results above a relevance threshold of 0.65) are used. Cross-encoder re-ranking adds ~100-200ms latency, acceptable for personal use. Arabic cross-encoder options: multilingual models from the BGE or Cohere families initially, with potential fine-tuning on KR relevance judgments as the library grows.

*Filtered retrieval.* For queries with explicit metadata constraints: school, time period, evidence type, author, source. Combines Qdrant's payload filtering with either targeted or semantic retrieval. Example: "What do Hanafi scholars before 500 AH say about المبتدأ?" → targeted retrieval on المبتدأ leaf + payload filter `school == "hanafi" AND death_hijri < 500`. Filters are combinable — multiple constraints are ANDed.

*Cross-science retrieval.* For queries that span multiple sciences. Reads the taxonomy engine's `cross_science_links.json` to identify linked leaves across sciences, then retrieves content from all linked leaves. This strategy is triggered when the query mentions multiple sciences, or when the identified leaf has cross-science links and the query is broad enough to warrant cross-science exploration.

**Stage 1: Topic identification and strategy selection.** The query is analyzed to determine: the most likely taxonomy leaf_ids (using keyword matching against leaf titles + synonyms, semantic similarity between the query embedding and precomputed leaf title embeddings, and conversation context for anaphoric references like "this topic"). If the leaf match is high-confidence (≥0.9), targeted retrieval is used. If the query contains metadata constraints, filtered retrieval is added. If the query mentions multiple sciences or cross-science terms, cross-science retrieval is activated. Otherwise, semantic retrieval is the default. If the mapping is genuinely ambiguous (multiple candidate leaves with confidence 0.5-0.9), the interface either asks for clarification ("Do you mean الاستثناء in Nahw or in Usul?") or retrieves from all candidates if the query warrants breadth.

**Stage 2: Content retrieval.** Using the selected strategy, retrieve: the synthesized entry at each identified leaf (if it exists and is not stale), the placed excerpts (always — the interface needs specific excerpts for citations even when an entry exists), and coverage analytics (for context on how well-covered this topic is). For semantic retrieval, the retrieval pulls from both the excerpt and entry-section collections, merging results by leaf_path.

**Stage 3: Scholar context enrichment.** For each scholar mentioned in the retrieved content, query the scholar_authority component for biographical data, school affiliations, and teacher-student relationships. This enrichment enables the interface to contextualize positions with scholarly metadata: "سيبويه (d. 180 AH), founder of systematic Basran grammar, student of الخليل بن أحمد..." Enrichment queries are batched — all scholar IDs are collected from retrieved content and resolved in a single batch query rather than per-excerpt.

**Stage 4: User context overlay.** Query the user model for the owner's engagement with the retrieved content: has he seen this entry before? What is his mastery level on this topic? What are his prerequisites' confidence scores? This overlay determines response depth: a first-time viewer gets the full entry with context; someone revisiting gets a focused response addressing their specific question.

**Grounding enforcement.** Every claim in the generated response carries a `grounding_type`: `library_excerpt` (traced to a specific excerpt_id), `library_metadata` (derived from source/scholar metadata in the system), or `llm_research` (from the LLM's training knowledge, not verifiable against the library). The interface enforces two thresholds: if more than 30% of factual claims in a response are `llm_research`, the response receives `confidence_assessment: "low"` and the owner sees a visible notice: "This answer draws significantly on unverified knowledge — the library's coverage of this topic is limited." If more than 50% are `llm_research`, the response additionally recommends source acquisition: "Consider acquiring [suggested source] to strengthen the library's coverage here." These thresholds ensure the owner always knows how much of what he reads is library-verified versus LLM-contributed.

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

### §4.B — Transformative Capabilities

The capabilities in this section are architect-originated — none appear in VISION.md or in the owner's requests. Each is fully specified with inputs, outputs, triggers, and behavioral rules. These are not aspirations; they are features that make previously impossible scholarship possible through the scholar interface.

#### §4.B.1 — Scholarly Debate Simulation

**What this enables.** A scholar studying a disputed topic today reads each school's position in isolation, then mentally reconstructs the argument. No tool lets you witness the argument itself — hearing each side's response to the other's evidence, each scholar's counter to the other's reasoning, in a structured back-and-forth grounded entirely in documented positions. Debate simulation makes this possible: the interface generates a structured scholarly debate between historical figures on any topic where the library holds multiple positions, using only their documented arguments and methodological commitments.

**Trigger.** The owner requests a debate explicitly ("Simulate a debate between Sibawayhi and al-Kisa'i on المبتدأ") or the interface suggests one when presenting a topic with rich khilaf (disagreement involving ≥3 distinct positions from ≥2 schools with documented evidence chains). The interface only offers debate simulation when sufficient grounding exists — it never simulates debates on topics where the library has fewer than 4 relevant excerpts across at least 2 positions.

**Inputs to the simulation LLM call:**
- All placed excerpts at the relevant leaf, grouped by school and scholar.
- Each scholar's documented methodology (from scholar_authority records: school affiliation, known methodological commitments, evidence hierarchy preferences).
- Each scholar's documented positions on the specific topic, with their stated evidence and reasoning (from excerpts' content and metadata).
- The historical context: when each scholar lived, what scholarly debates were active in their period, what intellectual tradition they inherited (from scholar_authority biographical data + entry temporal_narrative).
- A strict grounding constraint: every argument attributed to a scholar must be traceable to a specific excerpt or to documented methodological commitments in the scholar_authority record. No fabricated arguments.

**Simulation structure.** The debate proceeds in rounds:
1. **Opening statements.** Each participant states their position in their own documented words (direct excerpt quotation where available, paraphrase from excerpt content otherwise). Each statement carries a citation.
2. **Evidence presentation.** Each participant presents their evidence chain: Quranic evidence, hadith evidence (with grading), analogical reasoning, consensus claims. All evidence is from excerpts.
3. **Rebuttals.** Each participant responds to the other's evidence using their documented counter-arguments. Where a direct rebuttal exists in the library (an excerpt where Scholar A explicitly responds to Scholar B), it is quoted. Where no direct rebuttal exists but the scholar's methodology implies a response (e.g., a Basran scholar would reject a Kufan argument from analogy because Basrans privileged سماع over قياس), the response is generated and marked as `llm_research` with the reasoning: "This response is inferred from [scholar]'s documented methodology (evidence: [excerpt_id]), not from a direct rebuttal in the library."
4. **Moderator analysis.** The interface provides a post-debate analysis: what were the strongest arguments, where did each side concede ground (explicitly or implicitly), what evidence was left unanswered, and where the later scholarly tradition settled.

**Grounding enforcement in debates.** Every statement in the simulation carries an inline grounding marker: `[library: excerpt_id]` for directly sourced statements, `[methodology: scholar_authority_id + methodological_principle]` for methodology-inferred responses, `[llm: reasoning]` for synthesized connections. The overall grounding ratio is computed and displayed. If more than 40% of the debate content is `llm`-grounded (meaning the library doesn't have enough documented positions to sustain a rich debate), the interface warns: "This debate is largely reconstructed from general scholarly knowledge rather than your library's specific excerpts. Acquiring [suggested sources] would strengthen it."

**What makes this transformative.** No Islamic studies tool, digital or physical, lets a student witness a structured scholarly debate between figures from different centuries, grounded in their actual documented positions. This makes the intellectual dynamics of khilaf tangible in a way that reading positions in isolation never can.

#### §4.B.2 — Scholarly Fingerprinting

**What this enables.** Every scholar has a distinctive intellectual signature — a pattern of methodological commitments, evidence preferences, reasoning styles, and topic priorities that makes their approach recognizable across their corpus. Today, perceiving this signature requires reading dozens of books by the same author. KR can compute it from the library's metadata.

**Trigger.** The owner asks about a scholar's methodology ("What characterizes Ibn Qudamah's approach?"), or the interface surfaces a fingerprint comparison when presenting positions from multiple scholars ("Note: al-Nawawi and Ibn Qudamah reach the same conclusion here but through characteristically different reasoning — see their fingerprints").

**Computation.** A scholar's fingerprint is computed from all excerpts in the library attributed to that scholar (primary_author_id match). The fingerprint has five dimensions:

*Evidence preference profile.* Distribution of evidence types across the scholar's excerpts: what percentage cite Quranic evidence, hadith evidence, qiyas (analogy), ijma' (consensus), aql (rational argument), linguistic analysis. Computed from excerpts' `evidence_types` metadata. A scholar who cites hadith in 80% of positions and qiyas in 15% has a different fingerprint from one who cites qiyas in 60% and hadith in 30%.

*Agreement profile.* Across all topics where this scholar has a documented position, what percentage align with the majority position of their own school, what percentage deviate from their school, and what percentage create novel positions not held by any prior scholar. Computed by comparing the scholar's positions (from excerpts' `school` and content) against the leaf's coverage analytics.

*Scope profile.* Which sciences and branches the scholar addresses, weighted by depth. A scholar with 200 excerpts across 3 sciences has a different scope signature from one with 200 excerpts concentrated in a single branch of a single science.

*Temporal positioning.* Whether the scholar typically follows established consensus, revises earlier positions, or originates new analysis. Computed by comparing the scholar's positions against earlier positions at the same leaves (using death_hijri ordering).

*Methodological markers.* Characteristic reasoning patterns detected across the scholar's excerpts: does the scholar typically define terms before ruling? Cite counter-evidence before refuting? Build from edge cases? These patterns are extracted by an LLM analysis of the scholar's excerpts, scored by frequency, and reported with confidence levels. This dimension uses `llm_research` grounding and is clearly marked as analytical rather than factual.

**Output.** A scholar fingerprint document: a structured, human-readable profile that characterizes the scholar's intellectual signature with concrete statistics and examples. Each dimension includes: the computed score with confidence interval, the excerpts that most strongly exemplify the pattern, and comparison to other scholars in the library from the same science and period.

**Comparison mode.** When two or more scholars are being compared (either by owner request or because they hold opposing positions on a topic), the interface presents a side-by-side fingerprint comparison highlighting where their approaches diverge most. This reveals not just WHAT they disagree on, but WHY — their underlying methodological differences that predict future disagreements.

**What makes this transformative.** Understanding a scholar's methodology traditionally requires years of reading their works. KR computes a quantitative methodological profile from metadata that accumulates naturally as the library grows. This enables a student to understand WHY a scholar holds a position before even reading their argument — and to predict what position they would likely hold on a topic where they haven't been consulted.

#### §4.B.3 — Unanswered Question Discovery

**What this enables.** Every science has questions that no scholar has addressed, or questions where the scholarly record has gaps that represent original research opportunities. These are invisible in traditional study — you have to already know the entire field to notice what's missing. KR can detect these gaps computationally.

**Computation.** Unanswered question discovery operates at three levels:

*Level 1: Coverage-based gaps.* From taxonomy coverage analytics, identify leaves where: (a) no excerpts exist from any school (unexplored topic — the tree says this topic should exist but no source in the library addresses it), (b) excerpts exist from some schools but not others (partial coverage — a position gap, not an unexplored topic), (c) no excerpts exist from before a certain century (temporal blind spot — the topic may have been addressed but the library lacks early sources). These are factual gaps in the library, not necessarily gaps in the scholarly record — the distinction is presented clearly.

*Level 2: Structural inference gaps.* From the taxonomy tree's prerequisite graph and cross-science links, identify topic combinations that SHOULD interact but DON'T have any linking content in the library. Example: if leaf A in Nahw and leaf B in Usul share a cross-science link, but no excerpt at either leaf references the other science, this is a potential gap in cross-science analysis that could be an original research opportunity. Structural gaps are ranked by: the significance scores of both topics (high-significance topics with missing connections are more valuable), the number of schools represented at both topics (more schools = richer potential analysis), and the owner's expertise in both sciences (gaps in sciences the owner has studied are more actionable).

*Level 3: Contradiction-implied gaps.* When the synthesis engine detects a contradiction (§4.A.4.5), this may imply an unresolved scholarly question. If two sources disagree and no third source in the library resolves the disagreement, the question of which position is stronger — and whether a synthesis is possible — is an unanswered research question. The interface presents these as: "This contradiction between [Source A] and [Source B] on [topic] has not been resolved by any scholar in your library. This could be an original research opportunity."

**Trigger.** The interface computes unanswered questions periodically (whenever taxonomy coverage analytics are updated) and presents them through three channels: (a) the scholarly briefing (§4.A.4.4) includes a "research opportunities" section, (b) when the owner enters research mode, the interface proactively suggests relevant unanswered questions based on the owner's current focus, (c) when the owner requests evidence compilation for a research topic (§4.A.5.1), the interface checks whether the topic intersects with any discovered unanswered questions.

**Output.** Each unanswered question is presented as a structured research seed: the question formulation, the gap type (coverage, structural, contradiction-implied), the existing evidence on each side (if any), the suggested sources that might address it, and an assessment of the question's significance (based on topic significance, school impact, and novelty). Research seeds are stored in the user model as bookmarkable items — the owner can save them for later investigation.

**What makes this transformative.** Original research in Islamic sciences today requires a scholar to have internalized the entire field well enough to notice what's missing. KR can detect structural gaps in the scholarly record computationally — turning gap detection from a lifetime of reading into a systematic process. A student using KR could identify original research opportunities in their first year of study.

#### §4.B.4 — Optimal Source Prediction

**What this enables.** The question "what should I read next?" is one of the most consequential in a student's career. The wrong choice wastes months. The right choice fills the exact gaps that accelerate understanding. Today, this question is answered by teachers who know both the student and the field. KR can answer it computationally by combining library state, user model, and the work relationship graph.

**Computation.** Given the current library state (what sources exist, what coverage they provide) and the user model state (what the owner has studied, what gaps exist, what curricula are active), the interface computes a ranked list of source acquisition recommendations. The ranking function considers:

*Coverage impact.* For each candidate source (from the work registry's `referenced_not_acquired` records and from LLM-suggested sources for detected gaps): how many taxonomy leaves would gain new excerpts if this source were acquired? How many school gaps would be filled? How many temporal gaps would be narrowed? Coverage impact is estimated from the source's known scope (from its work record metadata, if available) or from LLM knowledge of the work's contents (marked as `llm_research`).

*Curriculum alignment.* Does the candidate source cover topics in the owner's active curricula? Sources aligned with current study are prioritized — they provide immediate benefit rather than deferred value.

*Classical progression fit.* Where does the candidate source sit in the classical learning progression for its science (from the curriculum knowledge base, §4.A.1.1)? A source that is the logical next text in the owner's progression is more valuable than a reference work he won't consult for years.

*Citation density.* How many times is the candidate source cited by sources already in the library? (From the work relationship graph's citation counts.) A heavily-cited work that the library doesn't yet contain represents a systematic blind spot — every time the library cites it without having its content, the synthesizer must rely on `llm_research` grounding.

*Scholarly authority.* What is the candidate source's scholarly standing? (From its work record's authority_level, if known, or from LLM assessment.) Primary sources by foundational scholars (e.g., الكتاب by Sibawayhi, المغني by Ibn Qudamah) are prioritized over modern compilations.

**Trigger.** The interface proactively computes acquisition recommendations: (a) when gap analysis detects significant coverage deficiencies (§4.A.4.3), (b) when the owner completes a curriculum level and needs the next text, (c) when the owner explicitly asks "what should I read next?" or "what source should I acquire?", (d) in the periodic scholarly briefing's "library growth" section.

**Output.** A ranked list of recommended acquisitions, each with: source identification (title, author, known editions), the predicted coverage impact (how many leaves, schools, and temporal gaps it addresses), the reasoning for the recommendation, the acquisition difficulty (is it available in known repositories? does it require manual acquisition?), and the estimated processing effort (page count, format complexity). The top recommendation includes a one-sentence summary: "Acquiring المغني by Ibn Qudamah would fill Hanbali coverage gaps across 34 fiqh leaves and provide the most-cited reference for 12 topics currently relying on LLM-contributed knowledge."

**What makes this transformative.** Source selection in traditional scholarship is guided by teachers who know a student's level and by scholarly consensus about what texts are important. Both are valuable but neither accounts for the SPECIFIC gaps in a SPECIFIC student's knowledge. KR makes source selection a personalized, data-driven recommendation that considers the entire state of the library and the student's learning trajectory simultaneously.

#### §4.B.5 — Knowledge Decay Prediction and Proactive Reinforcement

**What this enables.** Spaced repetition systems react to forgotten knowledge — they schedule a review AFTER you've failed to recall something. KR can predict decay BEFORE it happens by analyzing the owner's engagement patterns, assessment history, and the structural relationships between topics. If topic A is decaying and topic B depends on it, the owner should reinforce A before B becomes incomprehensible.

**Computation.** The decay prediction model operates on two signals:

*Individual topic decay.* From the user model's FSRS scheduling data (§4.A.3 of user_model SPEC), each reviewed topic has a predicted retention probability at any given time. Standard FSRS computes this already. The enhancement is: instead of waiting for the retention probability to drop below the review threshold (default: 0.85), the interface identifies topics approaching the threshold (retention 0.85-0.90) that are prerequisites for topics the owner is about to study in their curriculum. These "strategically fragile" topics are promoted to immediate review even though they haven't technically crossed the threshold.

*Cascade vulnerability.* From the taxonomy tree's prerequisite graph, identify clusters of topics where decay in one topic threatens comprehension of many others. A foundational topic like "العامل" (grammatical operator theory) that is a prerequisite for 15 other topics is a cascade vulnerability — if it decays, the owner's understanding of all 15 dependents degrades silently. The interface assigns a cascade vulnerability score to each topic: the number of downstream topics in the prerequisite graph weighted by their significance scores. High-cascade-vulnerability topics receive tighter retention thresholds (0.90 instead of 0.85).

**Trigger.** The decay prediction runs at the start of each study session (§4.A.1.2). If strategically fragile or cascade-vulnerable topics are detected, they are inserted into the session plan ahead of new material: "Before proceeding with today's topic, let's reinforce العامل theory — it's foundational to the next 3 topics in your curriculum and your retention is at 87%."

**Output.** The daily session plan is augmented with: a "strategic reinforcement" section listing topics recommended for proactive review (with the reason: cascade vulnerability, curriculum alignment, or approaching threshold), and a "knowledge health" summary showing the owner's overall retention trajectory: "Your Nahw retention is strong (94% average) but Usul al-Fiqh is declining (82% average, 3 topics below threshold). Consider shifting study time to Usul this week."

**What makes this transformative.** Traditional spaced repetition is topic-level and reactive. KR's decay prediction is structurally aware — it understands that forgetting a foundational topic silently undermines everything built on it. This transforms review from a mechanical chore into a strategic reinforcement that preserves the integrity of the owner's knowledge network.

## 5. Validation and Quality

The scholar interface is the final presentation layer — errors here are errors the owner sees and absorbs. Validation operates at three layers.

### §5.1 — Self-Validation (Layer 1)

The interface performs automated checks on every response before presenting it to the owner.

**Citation verification.** Every `library_grounded` claim must reference an excerpt_id or entry_id that exists in the retrieved content for this response. The interface verifies: (a) the cited excerpt_id exists in the current retrieval set, (b) the cited excerpt's content supports the claim being made (a lightweight semantic similarity check between the claim text and the excerpt's `primary_text` — threshold: 0.50 cosine similarity with the Arabic embedding model). Citations that fail check (a) are stripped entirely (this catches hallucinated excerpt_ids). Citations that fail check (b) are flagged with a warning log but presented with reduced confidence — the claim may still be correct but the citation link is weak.

**Grounding ratio enforcement.** The grounding thresholds (§4.A.2.2) are verified: >30% `llm_research` → low confidence notice added; >50% `llm_research` → acquisition recommendation added. These thresholds are checked programmatically on every response.

**Factual consistency check.** When the response contains a claim that references a previously presented claim in the same session (multi-turn consistency), the interface verifies the two claims are consistent. If the current response contradicts something stated earlier in the session, the interface flags the contradiction to the owner rather than silently presenting inconsistent information.

**Arabic text integrity.** When the response includes quoted Arabic text from excerpts, the interface verifies the quoted text matches the excerpt's `primary_text` field exactly (byte-level comparison). Any mismatch — even a single diacritical mark — triggers a warning log and the quote is replaced with the canonical excerpt text. The LLM may attempt to "correct" or paraphrase primary text during response generation; this check prevents that.

**Assessment evaluation safeguard.** For Socratic assessment evaluations (§4.A.3.2), the interface checks that the evaluation's grading is internally consistent: a response scored 1.0 (correct) must not contain feedback saying "you missed X" — that would be a partial (0.5) score. Inconsistent evaluations are re-evaluated with a second LLM call.

### §5.2 — Automated Checks (Layer 2)

**Response quality monitoring.** Aggregate statistics computed over rolling windows: average grounding ratio (what percentage of responses are well-grounded), citation accuracy (what percentage of citations pass verification), assessment strictness distribution (the distribution of 0.0/0.5/1.0 scores — too many 1.0 scores suggest the evaluation is too lenient, too many 0.0 scores suggest questions are too hard). These statistics are logged and available for owner review.

**Retrieval quality monitoring.** Per-query: the number of relevant results returned (out of top-K), the re-ranking delta (how much cross-encoder re-ranking changed the initial ranking — large deltas suggest the embedding model is poorly calibrated), and retrieval latency. Persistent low retrieval quality triggers a recommendation to fine-tune the embedding model or re-evaluate the embedding choice.

**User model consistency audit.** Periodically (daily), verify that the user model's knowledge estimates are consistent with assessment results: if the user model says mastery ≥ 0.8 on a topic but the most recent assessment scored 0.3, the knowledge estimate is stale or wrong. Inconsistencies are flagged for recalibration.

### §5.3 — Human Gate Integration (Layer 3)

The scholar interface does not have its own human gate checkpoints — it is the human-facing surface, so every response IS human-reviewed by virtue of the owner reading it. However, the interface integrates with the human gate in two ways:

**Presenting gate decisions.** When the human gate queues a decision for owner review (a taxonomy placement question, a source ambiguity, a low-confidence excerpt), the interface presents it contextually — not as an abstract queue, but as a natural part of the owner's current activity. If the owner is studying a topic and a related gate decision exists, the interface surfaces it: "While you're on this topic — the system placed an excerpt here with moderate confidence (0.62). Does this excerpt belong at this leaf? [excerpt preview + placement rationale]."

**Triggering escalation.** If the interface's self-validation (§5.1) detects a systematic issue — citation accuracy drops below 90% over 20 responses, or assessment evaluations show persistent inconsistency — it creates an alert for the owner: "I'm detecting potential quality issues in my responses about [science/branch]. My citation accuracy has dropped to [X%]. This may indicate a problem with the underlying entries or with my retrieval. Would you like to investigate?"

## 6. Consensus Integration

The scholar interface uses multi-model consensus for one specific decision: evaluation of ambiguous assessment responses (§4.A.3.2). When the primary model's confidence in evaluating an owner's Socratic assessment answer is below 0.70, a second model evaluates independently. Agreement accepts the evaluation; disagreement triggers the more generous score with a refined follow-up question.

**Why only assessment evaluation uses consensus.** Response generation does not use consensus because: (a) response quality is governed by grounding enforcement, which is a deterministic check, not a judgment call, (b) the owner reads every response, making it a human-reviewed output, and (c) generating two full responses and merging them would double latency without improving grounding quality. Retrieval does not use consensus because it is a mechanical process (embedding similarity + re-ranking) with no judgment component. Curriculum generation does not use consensus because curricula are reviewed by the owner before use, and the generation logic is primarily rule-based (classical progression + prerequisite ordering) rather than open-ended.

Assessment evaluation is the exception because: a wrong evaluation directly corrupts the user model's knowledge estimates (DOMAIN.md: the library IS Rayane's knowledge — a false positive assessment means the system thinks he knows something he doesn't). The stakes are high enough to justify the cost of a second model, and the input is small enough (one question + one answer) that the latency impact is minimal.

**Consensus configuration.** Two models from different providers (provider diversity ensures independent failure modes). Primary: the main KR inference model. Secondary: a model from a different provider family. Agreement threshold: both models assign the same score category (0.0 vs 0.5 vs 1.0). If they disagree on category (e.g., one says 0.5 and the other says 1.0), the more generous score is presented but the confidence in the evaluation is lowered: the owner sees "Your answer was evaluated as correct, though my confidence in this evaluation is moderate. Let me ask a follow-up to verify."

## 7. Error Handling

### §7.1 — Input Errors

| Error | Code | Severity | Recovery |
|-------|------|----------|----------|
| Empty message | SI_EMPTY_INPUT | info | Ignored, no response generated |
| Message exceeds 10,000 chars | SI_INPUT_TRUNCATED | warning | Truncated with notice to owner |
| Unrecognized structured action | SI_UNKNOWN_ACTION | warning | Owner informed of valid actions |
| Unsupported file type | SI_UNSUPPORTED_FILE_TYPE | warning | Owner informed of supported types |
| File exceeds size limit (100MB) | SI_FILE_TOO_LARGE | warning | Owner informed of limit |

### §7.2 — Retrieval Errors

| Error | Code | Severity | Recovery |
|-------|------|----------|----------|
| Qdrant unavailable | SI_VECTOR_STORE_DOWN | fatal | Fallback to targeted-only retrieval (leaf title matching without vector search). If targeted also fails, inform owner: "Knowledge retrieval is temporarily unavailable." Log for system alert. |
| No results for query | SI_NO_RESULTS | info | Inform owner: "The library has no content matching this query." Offer LLM-only response clearly marked. |
| Embedding model unavailable | SI_EMBEDDING_DOWN | fatal | Fallback to keyword-based retrieval against leaf titles. Degraded quality but functional. Log for system alert. |
| Cross-encoder timeout | SI_RERANKER_TIMEOUT | warning | Skip re-ranking, use initial embedding-based ranking. Degraded precision but functional. |
| Scholar authority query fails | SI_AUTHORITY_DOWN | warning | Proceed without scholar enrichment. Responses lack biographical context but core content is unaffected. |

### §7.3 — Generation Errors

| Error | Code | Severity | Recovery |
|-------|------|----------|----------|
| LLM call fails (timeout/error) | SI_GENERATION_FAILED | fatal | Retry once with same input. If retry fails, inform owner: "I couldn't generate a response. Please try again." Log full error for debugging. |
| Citation verification fails (>50% citations invalid) | SI_CITATION_INTEGRITY | warning | Strip invalid citations. If remaining grounded claims < 30%, downgrade to "low confidence" response with notice. Log for quality monitoring. |
| Response contradicts session context | SI_CONSISTENCY_VIOLATION | warning | Present the response with a notice: "Note: this may differ from what I said earlier about [topic]. Let me clarify the distinction." Log for investigation. |
| Assessment evaluation inconsistency | SI_EVALUATION_INCONSISTENT | warning | Re-evaluate with second LLM call. If still inconsistent, present partial score (0.5) with explanation that evaluation was uncertain. |

### §7.4 — System State Errors

| Error | Code | Severity | Recovery |
|-------|------|----------|----------|
| User model unavailable | SI_USER_MODEL_DOWN | fatal | Operate in "anonymous" mode: no personalization, no engagement tracking, no spaced repetition. Inform owner: "Personalization is temporarily unavailable — responses won't reflect your study history." |
| Taxonomy tree unavailable | SI_TAXONOMY_DOWN | fatal | Cannot perform topic identification or navigation. Inform owner. Offer direct excerpt search as fallback. |
| Synthesis engine output missing for leaf | SI_NO_ENTRY | info | Generate response directly from placed excerpts (§4.A.2.4). Normal operation for leaves without entries. |
| Feedback component unavailable | SI_FEEDBACK_DOWN | warning | Accept corrections but queue them locally until the component recovers. Inform owner: "Your correction has been recorded and will be processed when the system is fully available." |

### §7.5 — Error Principles

Every error follows three principles from D-033 (secure by design):

**Fail-loud.** No error is silently swallowed. Every error produces either a user-visible notice (for errors that affect the owner's experience) or a system log entry (for errors that are transparent to the owner but need investigation).

**Degrade gracefully.** The interface always attempts to provide some value even when components fail. Full retrieval pipeline down → fall back to keyword matching. User model down → operate without personalization. Entry missing → generate from raw excerpts. Total LLM failure → inform the owner and suggest retrying.

**Never present uncertain content as certain.** When degraded operation produces lower-quality responses (e.g., missing scholar enrichment, no re-ranking, keyword-only retrieval), the response's confidence signals reflect this. The owner always knows when they're getting a degraded response.

## 8. Configuration

### §8.1 — Retrieval Configuration

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| `embedding_model` | `AraGemma-Embedding-300m` | Any HuggingFace model | Arabic embedding model for vector search. Evaluate against Swan-Large on KR corpus before deployment. |
| `embedding_dimensions` | 768 | 64–768 | Matryoshka dimension for retrieval. Full (768) for answering, reduced (256) for exploratory browsing. |
| `retrieval_top_k` | 20 | 5–50 | Number of candidates from initial vector search before re-ranking. |
| `reranker_top_n` | 5 | 1–10 | Number of results after cross-encoder re-ranking. |
| `reranker_relevance_threshold` | 0.65 | 0.0–1.0 | Minimum cross-encoder relevance score for a result to be included. |
| `targeted_confidence_threshold` | 0.90 | 0.5–1.0 | Minimum leaf-match confidence for targeted retrieval (skipping vector search). |
| `llm_research_warning_threshold` | 0.30 | 0.0–1.0 | Proportion of LLM-contributed claims that triggers low-confidence notice. |
| `llm_research_acquisition_threshold` | 0.50 | 0.0–1.0 | Proportion of LLM-contributed claims that triggers acquisition recommendation. |

### §8.2 — Assessment Configuration

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| `assessment_questions_per_session` | 3 | 2–6 | Number of Socratic questions per assessment session. |
| `consensus_confidence_threshold` | 0.70 | 0.5–0.9 | Below this confidence, assessment evaluation triggers multi-model consensus. |
| `review_retention_threshold` | 0.85 | 0.7–0.95 | FSRS retention probability below which a review is scheduled. |
| `cascade_retention_threshold` | 0.90 | 0.8–0.95 | Elevated retention threshold for cascade-vulnerable topics. |
| `cascade_vulnerability_weight` | 1.0 | 0.0–5.0 | Weight of downstream topic count in cascade vulnerability score. |

### §8.3 — Presentation Configuration

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| `response_language` | `auto` | `auto`, `ar`, `nl`, `fr`, `en` | Language for interface text. `auto` matches the owner's input language. Scholarly content always Arabic (D-032). |
| `scholarly_briefing_frequency` | `weekly` | `daily`, `weekly`, `on_demand` | How often periodic scholarly briefings are generated. |
| `debate_simulation_grounding_threshold` | 0.60 | 0.3–0.9 | Minimum library-grounded proportion for debate simulation. Below this, simulation is warned as heavily reconstructed. |
| `expert_level_threshold` | `advanced` | user_model expertise levels | Owner expertise level at which responses omit basic definitions and assume familiarity. |

### §8.4 — Per-Science Configuration

Some parameters may be overridden per science to reflect different scholarly characteristics:

- `curriculum_knowledge_base`: the structured data file defining classical text progressions for each science. Separate files per science.
- `assessment_question_distribution`: the proportion of recall/recognition/application/comparison questions may vary by science (e.g., Fiqh may weight application higher than Nahw).
- `debate_simulation_availability`: some sciences may have insufficient khilaf tradition for meaningful debate simulation (e.g., Tajwid has minimal scholarly disagreement). This flag disables the suggestion for those sciences.

### §8.5 — Hardcoded Decisions

The following are NOT configurable:

- **Grounding is mandatory.** Every factual response must carry grounding markers. This cannot be disabled — it is the scholarly integrity baseline.
- **Citation verification runs on every response.** This cannot be skipped for performance. An unverified citation is worse than no citation.
- **Arabic text from excerpts is presented exactly.** No option to allow paraphrasing of primary source text.
- **Assessment evaluation errs on the side of caution.** No option to make evaluation more lenient — false positives in knowledge assessment are more harmful than false negatives.

## 9. Current Implementation State

**No code exists.** The scholar interface is entirely [NOT YET IMPLEMENTED]. No files, no code, no prototypes.

**Dependencies on upstream components:**

| Component | Status | Impact on Scholar Interface |
|-----------|--------|---------------------------|
| Source engine | SPEC complete, code partially exists (ABD-era Shamela intake) | Scholar interface needs source metadata API — not yet available |
| Normalization engine | SPEC complete, code partially exists (ABD-era Shamela normalizer) | Scholar interface has no direct dependency |
| Passaging engine | SPEC complete, no code | Scholar interface has no direct dependency |
| Atomization engine | SPEC complete, no code | Scholar interface has no direct dependency |
| Excerpting engine | SPEC complete, code partially exists (ABD-era excerpting) | Scholar interface needs placed excerpts — available only after taxonomy engine runs |
| Taxonomy engine | SPEC complete, no code | Scholar interface needs taxonomy trees, placed excerpts, coverage analytics — none available |
| Synthesis engine | SPEC complete, no code | Scholar interface needs synthesized entries — none available |
| Consensus component | SPEC complete, no code | Scholar interface needs consensus for assessment evaluation |
| Human gate | SPEC complete, no code | Scholar interface presents gate decisions |
| Validation component | SPEC complete, no code | Scholar interface uses validation for citation checks |
| Feedback component | SPEC complete, no code | Scholar interface routes corrections to feedback |
| User model | SPEC complete, no code | Scholar interface depends heavily on user model for all personalization |
| Scholar authority | SPEC complete, no code | Scholar interface needs scholar records for enrichment |

**External tools and libraries:**

| Tool | Purpose | Status |
|------|---------|--------|
| Qdrant | Vector store for excerpt and entry-section embeddings | Not yet deployed. Docker image available. |
| Arabic embedding model (AraGemma or Swan-Large) | Embedding generation for semantic retrieval | Not yet evaluated on KR corpus. Models available on HuggingFace. |
| Cross-encoder (BGE/Cohere multilingual) | Re-ranking after initial retrieval | Not yet selected. Candidates identified in RESOURCES.md. |
| LiteLLM | LLM provider abstraction for response generation and assessment | Available (shared with consensus component). |
| Instructor | Structured output extraction from LLM responses | Available (shared with consensus component). |
| FSRS algorithm | Spaced repetition scheduling | Open-source Python library available (py-fsrs). |

**Known gaps between this SPEC and buildability:**

1. The curriculum knowledge base (§4.A.1.1) — the structured data files defining classical text progressions per science — does not exist. These must be created from domain research before curriculum generation can work. This is a data creation task, not a code task.
2. The scholar fingerprinting computation (§4.B.2) depends on having a significant number of excerpts attributed to individual scholars. With the current library (minimal ABD-era processed content), fingerprints would be meaningless. This feature becomes valuable as the library grows.
3. The debate simulation (§4.B.1) similarly requires rich multi-school coverage at disputed leaves. Early library state will limit debate quality.
4. Frontend rendering is entirely out of scope for this SPEC. The interface produces structured data (science maps, debate transcripts, comparative analyses); a frontend must render them. No frontend exists.

## 10. Test Requirements

### §10.1 — Critical Test Coverage

**Grounding enforcement tests.** Verify that: (a) every response carries grounding markers, (b) the >30% LLM threshold triggers a low-confidence notice, (c) the >50% threshold triggers an acquisition recommendation, (d) a response with 0% `llm_research` carries no warnings, (e) a response generated when the library has no relevant content is entirely marked as `llm_research` with the appropriate notice.

**Citation verification tests.** Verify that: (a) a response with a valid excerpt_id citation passes verification, (b) a response with a fabricated excerpt_id has the citation stripped, (c) a response with a valid excerpt_id but semantically unrelated claim text triggers a weak-citation warning, (d) Arabic text quoted from an excerpt matches the source exactly (byte-level).

**Assessment evaluation tests.** Verify that: (a) a clearly correct answer scores 1.0, (b) a clearly incorrect answer scores 0.0, (c) a partial answer scores 0.5, (d) multi-model consensus is triggered when primary model confidence < 0.70, (e) consensus disagreement produces the more generous score with a follow-up question, (f) an evaluation marked 1.0 with "you missed X" feedback is caught by the inconsistency check.

**Retrieval tests.** Verify that: (a) targeted retrieval correctly maps a known topic query to the right leaf, (b) semantic retrieval returns relevant excerpts for a broad query, (c) filtered retrieval correctly applies school and temporal constraints, (d) cross-science retrieval activates when appropriate, (e) the system degrades gracefully when Qdrant is unavailable (falls back to keyword matching).

### §10.2 — Gold Baseline Usage

**Response quality baselines.** Create a set of 20 test queries spanning all query types (§4.A.2.1) with known expected responses. After each significant change to retrieval or generation logic, run all 20 queries and verify that response quality (grounding ratio, citation accuracy, relevance) does not regress.

**Assessment evaluation baselines.** Create a set of 15 test answer-pairs (question + owner answer) with known correct evaluations. Include: 5 clearly correct, 5 clearly incorrect, 5 ambiguous (the hard cases where consensus matters). Use these to verify assessment evaluation consistency.

**Curriculum generation baselines.** For at least one science (Nahw), create a reference curriculum based on domain research. Verify that the system's generated curriculum matches the expected topic sequence and assessment checkpoint placement.

### §10.3 — Regression Testing

**No-regression rules:**
- Grounding enforcement must never be weaker than the configured thresholds. A code change that allows an ungrounded factual claim to pass without a marker is a critical regression.
- Citation verification must never be disabled or weakened. A code change that allows a fabricated citation to reach the owner is a critical regression.
- Assessment evaluation must never produce false positives that go undetected. A code change that loosens evaluation criteria without updating the consistency check is a regression.
- Arabic text integrity must never allow modification of primary source quotes. A code change that permits LLM paraphrasing of excerpt text is a critical regression.

### §10.4 — Integration Tests

**With taxonomy engine.** Verify that: the interface can read a taxonomy tree and navigate it, placed excerpts at a leaf are retrievable with full metadata, coverage analytics are correctly consumed and presented.

**With synthesis engine.** Verify that: entries are retrievable by leaf_path, entry staleness is correctly detected, entry sections are individually retrievable for the entry-section embeddings collection.

**With user model.** Verify that: engagement events are written correctly, knowledge state is readable and consistent with assessment results, curriculum state is readable and writable, spaced repetition scheduling integrates with FSRS correctly.

**With scholar_authority.** Verify that: scholar records are retrievable by canonical_id, graph queries (teacher-student chains, subgraphs) return correct results, name resolution returns appropriate candidates for ambiguous queries.

**With feedback component.** Verify that: corrections are routed correctly (entry-level vs. excerpt-level vs. taxonomy-level vs. metadata), pattern detection results are consumable, correction acknowledgments are generated correctly.

**End-to-end scenario tests.** Implement at least one automated test per user scenario (USER_SCENARIOS.md). These tests verify the complete flow from user input to response, crossing all component boundaries. Start with Scenario 1 (Day 1) and Scenario 2 (Active Study) as the highest-priority integration tests.
