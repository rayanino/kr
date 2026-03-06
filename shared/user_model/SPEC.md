# User Model — نموذج المستخدم — Specification

## 1. Purpose and Scope

**What this component does.** The user model is the persistent representation of Rayane's scholarly state. Since KR IS Rayane's knowledge (D-018), the user model tracks the STATE of that knowledge: what has been studied, what has been understood, what has been forgotten, what is being actively pursued, and what remains unknown. It provides this state to every component that needs it — primarily the scholar interface for personalization, but also processing engines for relevance alerts and the human gate for confidence calibration.

The user model is a shared component, not an engine. It does not process sources or produce knowledge products. It is a stateful data layer that multiple components read from and write to. It owns four responsibilities: (1) maintaining engagement records — what Rayane has interacted with and how deeply, (2) maintaining knowledge state estimates — what Rayane understands at each topic, (3) maintaining curriculum state — active learning paths and position within each, and (4) maintaining scholarly profile — per-science expertise level, preferences, bookmarks, annotations, and study patterns.

**What is NOT this component's responsibility.** The user model does not generate entries (synthesizing engine), does not present content to the user (scholar interface), does not design curricula (scholar interface), does not conduct Socratic assessments (scholar interface), and does not manage human gate checkpoints (human gate component). It stores the DATA that these components produce and consume. The user model does not decide what to study next — it provides the state from which the scholar interface makes that decision. The user model does not evaluate comprehension — it stores the results of evaluations that the scholar interface conducts.

**Phase classification.** The user model is operational from the moment the scholar interface is available. It has no dependency on the processing pipeline — it begins empty and grows as Rayane interacts with the library. However, it benefits from library content: knowledge gap computation requires taxonomy trees, spaced repetition requires entries and excerpts, and relevance alerts require placed excerpts.

**User scenarios served.** All eight scenarios in USER_SCENARIOS.md depend on user model state:
- Scenario 1 (Day 1): curriculum state initialization, scholarly level recording, first engagement tracking.
- Scenario 2 (Active Study): spaced repetition scheduling, engagement history, source relevance alerts against current focus.
- Scenario 3 (Cross-Science): cross-science knowledge state enables the scholar interface to detect meaningful connections between topics Rayane has studied.
- Scenario 4 (Scholarly Production): knowledge state identifies what Rayane knows well enough to write about; gap detection reveals where research is needed.
- Scenario 5 (Teaching): demonstrated knowledge at advanced levels triggers teaching mode availability; lesson plan generation uses knowledge state to identify what Rayane can teach confidently.
- Scenario 6 (Book Briefing): scholarly level per science enables the scholar interface to contextualize the briefing ("this book is above your current level in Fiqh").
- Scenario 7 (Science Map): engagement state provides the green/yellow/gray coloring; knowledge gaps provide the red highlights.
- Scenario 8 (Correction): correction history is stored in the feedback component, but the user model tracks that Rayane has expertise on the corrected topic (corrections demonstrate deep understanding).

## 2. Input Contract

The user model receives input from four categories of writers. All writes are through a defined API — no component modifies user model files directly.

**Scholar interface writes.** The scholar interface is the primary writer. It writes: engagement events (Rayane opened an entry, read an excerpt, spent N seconds on a page), assessment results (Socratic dialogue outcomes with per-topic scores), curriculum actions (started a curriculum, completed a topic, skipped a topic, paused a curriculum), preference changes (interaction style, depth preference, language preference, study schedule), bookmarks and annotations (user-created markers on excerpts or entries), focus declarations (Rayane explicitly states "I'm studying Nahw now"), and scholarly production events (Rayane wrote a tarjih, completed a research note).

Each scholar interface write is a structured event with: `event_type` (string from the registered event type enum), `timestamp` (ISO 8601 UTC), `target` (what the event is about — a leaf_id, excerpt_id, entry_id, science_id, or curriculum_id), `payload` (event-type-specific structured data), and `source` (always `"scholar_interface"`).

**Processing engine writes.** Processing engines write relevance alerts: when a new excerpt is placed at a leaf that overlaps with Rayane's current focus or active curriculum, the engine writes an alert event. The alert contains: `alert_type` (one of `new_excerpt_in_focus`, `new_source_in_science`, `coverage_change`), `target` (the affected leaf, science, or source), `details` (what changed — new excerpt ID, new source ID, coverage delta), and `source` (the engine ID that generated the alert). Processing engines never modify knowledge state, engagement records, or curriculum state — they only ADD alerts.

**Human gate writes.** When the owner resolves a human gate checkpoint, the human gate component writes an event recording that Rayane made a domain decision. This is evidence of domain expertise — a resolved checkpoint on a Nahw topic is a signal that Rayane can evaluate Nahw content. The event contains: `event_type` (`"gate_resolution"`), `target` (the science and leaf if applicable), `payload` (the gate type and the owner's confidence assessment recorded at resolution time), and `source` (`"human_gate"`).

**Administrative writes.** The owner may directly update profile fields (scholarly level per science, study preferences) through the scholar interface's settings. These are preference writes, not engagement events.

**Validation on input.** Every write is validated before acceptance: `event_type` must be in the registered enum (rejection: `UM_UNKNOWN_EVENT_TYPE`), `timestamp` must be valid UTC and not in the future by more than 60 seconds (rejection: `UM_INVALID_TIMESTAMP`), `target` must reference an entity that exists in the library — a valid leaf_id, excerpt_id, entry_id, science_id, or curriculum_id (rejection: `UM_INVALID_TARGET`), `payload` must conform to the schema for its event type (rejection: `UM_INVALID_PAYLOAD`). Validation failures are logged and rejected — the user model never stores malformed events.

## 3. Output Contract

The user model provides read access through a query API. No component reads user model files directly — all reads go through the API, which ensures consistent data views.

**Knowledge state queries.** Given a leaf_id or a set of leaf_ids, returns the current knowledge state for each: mastery level (one of `unseen`, `viewed`, `studied`, `assessed`, `mastered`, `retained`), confidence score (0.0–1.0 — the model's estimate of how well Rayane knows this topic), last engagement timestamp, engagement depth (a summary of all interactions), and spaced repetition state (if active: next review date, current FSRS card state, retrievability estimate).

**Gap analysis queries.** Given a scope (a science, a branch, or the entire library), returns a structured gap report: topics with no engagement, topics below a mastery threshold, schools not represented in study history at topics where schools exist, time periods not covered (e.g., "no early-period sources studied for this topic"), and sciences not yet started. Gap reports include severity (how important the gap is, based on prerequisite dependencies and curriculum position) and actionability (what the owner can do — "acquire a Maliki source" vs. "study the existing entry").

**Curriculum state queries.** Returns active curricula with: curriculum ID, science, current position (which topic is next), completion percentage, pace statistics (topics per week, estimated completion date), and review backlog (how many spaced repetition items are due).

**Profile queries.** Returns the scholarly profile: per-science expertise level, declared confidence levels, study preferences, active focus areas, and study pattern statistics (average daily study time, most productive hours, preferred study depth).

**Alert queries.** Returns unread alerts sorted by relevance to current focus, with read/dismiss capability.

**Metadata pass-through (D-023).** The user model does not process source metadata — it operates at a higher level (topics, entries, excerpts as referenced by ID). However, it preserves all metadata it receives in events: if an engagement event includes excerpt metadata references, those references are stored verbatim. The user model adds: mastery estimates, engagement summaries, gap classifications, spaced repetition states, and curriculum positions. All of these are available to the scholar interface and, through it, to the synthesizing engine (which may use "Rayane has studied this topic deeply" to adjust analytical layer depth).

**Output guarantees.** Knowledge state queries always return a result for every requested leaf — if no engagement exists, the state is `unseen` with confidence 0.0. Gap analysis queries are computed fresh from current engagement data and current taxonomy trees — they are never stale (though they may be cached with a short TTL for performance). Curriculum state reflects the latest committed writes — there is no eventual consistency delay for curriculum operations.

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Engagement Tracking

Every interaction between Rayane and library content is recorded as an engagement event. The user model distinguishes six engagement types, ordered by depth:

1. **Viewed** (`viewed`): The content was displayed to Rayane. Minimum threshold: the entry or excerpt was on screen for at least 3 seconds (to filter accidental navigation). The scholar interface reports view events with duration.

2. **Read** (`read`): Rayane read the content meaningfully. Determined by: duration exceeds a reading-time threshold computed from content length (Arabic reading speed baseline: ~150 words per minute for scholarly text, configurable), OR the scholar interface reports explicit read-completion (Rayane scrolled to the end and the content was on screen long enough). The reading-time threshold is a lower bound, not a hard cutoff — the scholar interface may report read-completion based on interaction signals even if the time is below the threshold.

3. **Studied** (`studied`): Rayane engaged deeply. Determined by: Rayane took notes (annotation event on the content), Rayane asked the scholar interface a question about the content, Rayane spent more than 2x the reading-time threshold, OR the scholar interface reports explicit study-completion (e.g., Rayane used a "mark as studied" action).

4. **Assessed** (`assessed`): Rayane's comprehension was tested. Determined by: the scholar interface conducted a Socratic assessment on the topic and Rayane responded. The assessment result (per-question scores, overall comprehension estimate) is stored in the engagement record. An assessment that was started but abandoned (no responses recorded) is not counted.

5. **Mastered** (`mastered`): Rayane demonstrated strong comprehension. Determined by: an assessment result where the comprehension score exceeds the mastery threshold (default: 0.80, configurable per science via the scholarly profile). Mastery is topic-specific: Rayane can master the definition of المبتدأ without mastering all of باب المبتدأ والخبر.

6. **Retained** (`retained`): Rayane still knows the material after time has passed. Determined by: a spaced repetition review where Rayane's response is rated `Good` or `Easy` (FSRS ratings 3 or 4) after the scheduled review interval has elapsed. Retention is re-evaluated at every review — a failed review (`Again` or `Hard`) drops the state back to `studied` and resets the FSRS card.

**Engagement aggregation.** Each leaf in the taxonomy has an engagement record that aggregates all engagement events for that leaf's content (entries and excerpts). The leaf's mastery level is the HIGHEST engagement level achieved, subject to decay: mastery and retention can degrade over time if spaced repetition reviews are missed (see §4.A.3). The engagement record also stores the full event history for that leaf — individual events are never aggregated away, because the scholar interface may need fine-grained history (e.g., "show me everything I studied last Tuesday").

**Per-entry vs. per-leaf tracking.** Engagement is tracked at both granularities. Each entry has its own engagement events. Each leaf aggregates across all its entries. The leaf-level mastery is the MINIMUM mastery across all school-group entries at that leaf where schools exist — Rayane has mastered a topic only when all relevant school perspectives have been studied. For leaves without schools, the leaf-level mastery equals the single entry's mastery.

**Engagement across entry regeneration.** When an entry is regenerated (§6.3 of VISION.md), the old entry's engagement history is preserved and linked to the new entry. The new entry starts at engagement level `viewed` (it is displayed to Rayane with a "this entry has been updated" marker), but the TOPIC-level mastery is not reset — Rayane's understanding of the topic does not disappear because the entry was regenerated. If the regeneration was triggered by significant new content (new excerpts that change the scholarly landscape), the scholar interface may recommend re-assessment, but this is an interface decision, not a user model decision.

#### §4.A.2 — Knowledge State Estimation

The engagement tracking in §4.A.1 provides the raw data. The knowledge state estimator transforms this into a per-topic confidence score (0.0–1.0) that represents the user model's best estimate of how well Rayane knows each topic.

**Confidence score computation.** The confidence score for a leaf combines four signals:

1. **Engagement depth** (weight: 0.30). Mapped from the mastery level: `unseen`=0.0, `viewed`=0.10, `read`=0.25, `studied`=0.50, `assessed`=0.70, `mastered`=0.90, `retained`=1.0.

2. **Assessment performance** (weight: 0.35). If assessed: the most recent assessment's comprehension score (0.0–1.0). If not assessed: 0.0. This is the strongest signal — Socratic assessment directly measures comprehension.

3. **Recency decay** (weight: 0.20). How recently Rayane engaged with this topic. Uses an exponential decay function: `recency = exp(-days_since_last_engagement / half_life)`. The half-life is configurable per science (default: 30 days). A topic studied yesterday has high recency; a topic studied 90 days ago has low recency. This captures the forgetting curve at a coarse level — FSRS handles fine-grained forgetting for spaced repetition items.

4. **Prerequisite strength** (weight: 0.15). The average confidence score of this topic's prerequisite topics (as defined in the taxonomy's prerequisite graph). A topic whose prerequisites are poorly understood cannot be confidently known, even if the topic itself was studied — understanding without prerequisites is superficial. If the topic has no prerequisites, this signal defaults to 1.0.

**Score computation.** `confidence = Σ(weight_i × signal_i)` for the four signals. The score is clamped to [0.0, 1.0]. The weights are configurable via the scholarly profile (§8) but the defaults above reflect the priority: assessment is the strongest signal, engagement depth is next, recency captures forgetting, and prerequisite strength captures foundation quality.

**Staleness.** Confidence scores are recomputed on read (not precomputed) from current engagement data, current assessment results, and current taxonomy prerequisite graph. This means scores automatically reflect taxonomy evolution (new prerequisites added) and time passage (recency decay) without explicit recomputation triggers.

#### §4.A.3 — Spaced Repetition

The user model manages spaced repetition scheduling using the FSRS algorithm (Free Spaced Repetition Scheduler, version 6). FSRS is the state-of-the-art open-source spaced repetition algorithm, backed by academic research (KDD 2022), and available as the py-fsrs Python package with full JSON serialization support.

**What is a review item?** A review item is a knowledge unit that Rayane should periodically recall. Review items are created by the scholar interface — the user model does not decide what should be reviewed, only when. The scholar interface creates review items at the entry level (review the core definition of المبتدأ), at the excerpt level (recall this specific quote from Sibawayhi), or at a custom granularity (review this specific distinction between two scholarly positions). Each review item has: a `review_item_id`, a `target` (the leaf, entry, or excerpt it tests), a `question_type` (one of `recall`, `recognition`, `application`, `comparison` — see below), and an FSRS `Card` object tracking the item's scheduling state.

**Question types.** The review item's question type determines what the scholar interface asks during review:
- `recall`: "Define المبتدأ in your own words." Tests raw recall of a concept.
- `recognition`: "Which of these definitions is from the Basran school?" Tests ability to identify correct information.
- `application`: "Is 'رجل' the مبتدأ in 'في الدار رجلٌ'? Why?" Tests ability to apply the concept.
- `comparison`: "How does Ibn al-Sarraj's definition differ from Sibawayhi's?" Tests ability to distinguish related concepts.

The user model stores the question type because it affects FSRS scheduling: `recall` items are harder (shorter initial intervals) than `recognition` items. The difficulty modifier per question type is configurable (§8).

**FSRS integration.** The user model maintains an FSRS `Scheduler` instance configured with: `desired_retention=0.90` (default — Rayane retains 90% of reviewed material), `learning_steps=(timedelta(minutes=1), timedelta(minutes=10))` (standard initial steps), and default FSRS v6 parameters (21 weights). When the scholar interface reports a review result, it provides a `Rating` (Again=1, Hard=2, Good=3, Easy=4). The user model calls `scheduler.review_card(card, rating)` to update the card's state and next due date.

**FSRS parameter optimization.** After Rayane has accumulated sufficient review history (threshold: 200 reviews, configurable), the user model can optimize FSRS parameters using the fsrs-optimizer to personalize the scheduling to Rayane's actual memory patterns. This optimization is triggered manually by the scholar interface or automatically at configurable intervals (default: every 500 reviews). Optimization uses Rayane's complete review log as training data. The optimized parameters replace the defaults but are stored separately — the defaults can be restored if optimization produces poor results.

**Spaced repetition and mastery decay.** When a spaced repetition review is due and Rayane does not complete it within a grace period (default: 3 days past the due date), the review item's FSRS card state reflects the growing probability of forgetting. The user model does NOT automatically downgrade the topic's mastery level — this would be punitive and inaccurate (Rayane may still know the material; he just hasn't reviewed it). Instead, the confidence score's recency decay signal (§4.A.2) naturally decreases over time, and the scholar interface can see that reviews are overdue and adjust its recommendations accordingly.

**Review item lifecycle.** Review items can be: `active` (scheduled for periodic review), `suspended` (temporarily paused — Rayane is focusing on other topics), `retired` (mastery is so high that review is no longer needed — FSRS stability exceeds a threshold, default: 365 days), or `archived` (the underlying entry was regenerated with substantially different content — the review item is no longer valid and a new one should be created). The scholar interface manages lifecycle transitions; the user model stores and enforces the state.

#### §4.A.4 — Scholarly Profile and Expertise Level

The scholarly profile is the user model's representation of Rayane AS a scholar — his expertise, preferences, and study patterns. This replaces and subsumes the human gate's confidence calibration (previously in `library/gates/confidence.json` — see §4.A.4.1 for the migration).

**Per-science expertise level.** For each science in the library, the user model tracks an expertise level: `none` (has not started studying this science), `beginner` (early stages — studying foundational texts), `intermediate` (solid foundation — can evaluate content with guidance), `advanced` (deep knowledge — can evaluate content independently), `researcher` (producing original scholarship in this science). The expertise level is the MAXIMUM of two values: (a) the owner's self-declared level (set via the scholar interface's settings), and (b) the model's estimated level based on engagement data (see below). The owner can always override upward (declaring themselves more expert than the model estimates) but cannot override downward below the model's estimate — this prevents false modesty from weakening the human gate's calibration.

**Expertise estimation from engagement data.** The model estimates expertise level from: the percentage of the science's taxonomy tree that has been studied (viewed ≥ 50% of leaves → `beginner`, studied ≥ 30% → `intermediate`, mastered ≥ 30% → `advanced`), assessment performance across the science's topics (average comprehension score ≥ 0.7 across assessed topics, with ≥ 20% of topics assessed → +1 level), and scholarly production (any owner-originated tarjih or research note in this science → `researcher` candidate, subject to assessment coverage). These thresholds are configurable per science (§8).

**§4.A.4.1 — Confidence calibration migration.** The human gate SPEC §4.A.4 currently defines owner confidence levels (`expert`, `intermediate`, `beginner`, `none`) stored in `library/gates/confidence.json`. This is architecturally the same data as the per-science expertise level. The user model subsumes this: the human gate reads the owner's expertise level from the user model instead of maintaining its own file. The mapping is: `expert` → `advanced` or `researcher`, `intermediate` → `intermediate`, `beginner` → `beginner`, `none` → `none`. The human gate's behavioral rules (raising auto-approval thresholds for low-expertise sciences) remain unchanged — only the data source moves.

**Study preferences.** The user model stores: `preferred_depth` (one of `survey`, `standard`, `deep`, `exhaustive` — affects how much detail the scholar interface provides), `preferred_interaction_style` (one of `guided`, `exploratory`, `challenge` — guided: step-by-step curriculum; exploratory: follow interests; challenge: Socratic-heavy), `preferred_languages` (ordered list — for interface language, not scholarly content which is always Arabic per D-032), `study_schedule` (preferred study times — used for spaced repetition scheduling and daily briefings), `notification_preferences` (which alerts to surface proactively vs. batch).

**Study patterns.** The user model computes and stores study pattern statistics from engagement history: average daily study time (rolling 30-day window), most productive hours (which times of day have the most engagement events), study consistency (how many of the last 30 days had at least one engagement event), preferred session length (median engagement session duration), and topic switching frequency (how often Rayane moves between sciences or topics within a session). These statistics are informational — they help the scholar interface adapt its recommendations but do not constrain the owner's behavior.

#### §4.A.4b — Gap Analysis Computation

Gap analysis (§3) is computed on demand from three data sources: the user model's engagement records, the current taxonomy tree (read from the taxonomy engine's output), and excerpt metadata at each leaf (read from the library's placed excerpt records).

**Topic gaps.** For each leaf in the requested scope: if no engagement record exists, the leaf is a topic gap with severity based on its position in the prerequisite graph (a gap in a foundational topic is more severe than a gap in an advanced topic). If engagement exists but mastery level is below `studied`, it is a shallow gap (seen but not understood).

**School gaps.** For each leaf where schools exist: the user model checks which school-group entries have engagement records. If any school-group at the leaf has no engagement, it is a school gap. Severity is based on: whether the unstudied school represents a major madhhab (Hanafi, Maliki, Shafi'i, Hanbali — these are always high severity) and whether Rayane has studied the topic in other schools (if yes, the gap is "comparative" — he knows the topic but is missing one perspective).

**Temporal gaps.** For each leaf in the requested scope: the user model reads the placed excerpts' author metadata (author death dates from the scholar authority registry) and groups them by time period (early: before 400 AH, classical: 400–900 AH, late: after 900 AH — configurable). If Rayane has engaged only with excerpts from one or two periods and excerpts from all three periods exist at the leaf, the unengaged periods are temporal gaps. This computation requires cross-referencing engagement records (which excerpts were studied) with excerpt metadata (which authors wrote them and when) — the user model performs this cross-reference at query time.

**Science gaps.** Sciences that exist in the taxonomy but have zero engagement are science gaps. Severity is based on the owner's declared study goals in the scholarly profile.

**Actionability.** Each gap includes an actionability classification: `study_existing` (content exists at the leaf — just study it), `acquire_source` (no content exists for the missing school/period — a source needs to be acquired), `build_tree` (the science has no taxonomy tree yet — tree construction is needed before gaps can be filled), or `prerequisite_first` (the gap is in an advanced topic whose prerequisites are also gaps — study prerequisites first).

#### §4.A.5 — Curriculum State

A curriculum is a structured learning path through a portion of the taxonomy tree. The scholar interface creates curricula; the user model tracks state within them.

**Curriculum record.** Each curriculum contains: `curriculum_id` (format: `cur_{science}_{timestamp_hash}`), `science` (the science this curriculum covers), `scope` (which portion of the tree — could be an entire science, a specific branch, or a cross-science path), `sequence` (an ordered list of leaf_ids representing the study order — respecting prerequisite dependencies from the taxonomy's prerequisite graph), `current_position` (index into the sequence — which leaf is next), `status` (one of `active`, `paused`, `completed`, `abandoned`), `created_at` and `updated_at` timestamps, `pace_target` (optional — topics per week), and `completion_stats` (topics completed, topics skipped, average time per topic, estimated completion date).

**Multiple active curricula.** Rayane may have multiple active curricula simultaneously (e.g., one for Nahw and one for Usul al-Fiqh). The user model tracks all of them independently. The scholar interface may recommend focusing on one at a time, but the user model does not enforce this.

**Curriculum progression.** When the scholar interface reports that Rayane has completed a topic in the curriculum (engagement level `studied` or higher, optionally with assessment), the curriculum's `current_position` advances. If Rayane skips a topic (explicit skip action), the skip is recorded (the topic is marked as skipped, not completed) and the position advances. The scholar interface may later recommend revisiting skipped topics.

**Curriculum and taxonomy evolution.** If the taxonomy tree evolves (new leaves added, leaves split, leaves merged) while a curriculum is active, the curriculum's sequence may become invalid. The user model detects this: when a curriculum is queried, it validates that all leaf_ids in the sequence still exist in the current taxonomy tree. Invalid entries are flagged (not silently removed) and the scholar interface is notified that the curriculum needs updating. The scholar interface — not the user model — decides how to adapt the curriculum (insert new topics, skip removed topics, reorder).

#### §4.A.6 — Bookmarks and Annotations

Rayane can bookmark and annotate any content in the library. These are personal markers — they are not part of the library's knowledge products.

**Bookmarks.** A bookmark records: `bookmark_id`, `target` (entry_id, excerpt_id, or leaf_id), `created_at`, `label` (optional user-provided text, e.g., "review later", "important for paper"), and `context` (what Rayane was doing when he bookmarked — study session, research, browsing).

**Annotations.** An annotation records: `annotation_id`, `target` (entry_id or excerpt_id), `anchor` (the specific text range within the target — start/end character offsets), `content` (the annotation text — Rayane's notes, questions, disagreements), `annotation_type` (one of `note`, `question`, `disagreement`, `connection`, `tarjih`), and `created_at`.

Annotations of type `tarjih` are special: they represent Rayane's own scholarly opinion on a topic. The user model stores them and flags them as scholarly production events, which contributes to expertise estimation (§4.A.4) and is visible to the synthesizing engine as owner-originated knowledge (D-018, point 6: "Rayane's own voice belongs in the library").

**Annotation search.** The user model supports searching annotations by: target (all annotations on a specific entry), type (all tarjih annotations across the library), text content (free-text search within annotation content), and date range.

#### §4.A.7 — Alert Management

Processing engines and the scholar interface generate alerts about events relevant to Rayane's study. The user model stores and manages these alerts.

**Alert record.** Each alert contains: `alert_id`, `alert_type` (from a registered enum — see §2 for processing engine alert types; the scholar interface adds types like `review_due`, `curriculum_milestone`, `gap_detected`, `assessment_recommended`), `target` (the affected entity), `priority` (one of `critical`, `high`, `normal`, `low` — `critical` for things like "an entry you mastered was regenerated with contradicting content"), `created_at`, `read_at` (null if unread), `dismissed_at` (null if not dismissed), and `payload` (alert-type-specific details).

**Alert relevance scoring.** When alerts are queried, the user model scores each alert's relevance to Rayane's current focus: alerts about topics in active curricula score higher, alerts about sciences at higher expertise levels score higher (Rayane cares more about alerts in sciences he's actively studying), alerts from recent processing (newer sources) score higher. The relevance score is computed on read and used for ordering.

**Alert lifecycle.** Alerts transition: `unread` → `read` (displayed to Rayane) → `dismissed` (Rayane acknowledged it) or `acted_upon` (Rayane took the suggested action — e.g., acquired a suggested source, started a review session). Alerts older than a configurable retention period (default: 90 days) that are dismissed or acted upon are archived (moved to a compressed archive file, not deleted — the history may be useful for pattern analysis).

### §4.B — Transformative Capabilities

#### §4.B.1 — Scholarly Growth Trajectory Analysis

The user model accumulates a rich longitudinal dataset of Rayane's scholarly development — every engagement, every assessment, every curriculum progression, every correction, every annotation. This data enables analysis that no traditional learning system provides: a quantitative model of scholarly growth over time.

**Growth trajectory.** The user model computes, for each science and for the library as a whole: a knowledge breadth curve (percentage of taxonomy covered over time), a knowledge depth curve (average confidence score over time), a mastery velocity (rate of new topics mastered per week, with trend analysis), an assessment accuracy trajectory (comprehension scores over time — is Rayane getting better?), and a forgetting curve profile (personalized from FSRS review data — how quickly does Rayane forget material in each science? Does forgetting rate improve as expertise grows?).

These trajectories enable the scholar interface to make statements like: "In the last 3 months, your Nahw mastery velocity has doubled — you're now covering 8 topics per week versus 4. Your assessment accuracy has plateaued at 0.82 — this might indicate you need to revisit prerequisites before pushing forward." This kind of feedback transforms KR from a passive repository into an active scholarly development partner.

**Milestone detection.** The user model detects and records milestones: first topic mastered in a science, first assessment above 0.90, first cross-science connection studied, first tarjih annotation (scholarly production), curriculum completion, and custom milestones (the scholar interface can define science-specific milestones based on the classical pedagogical progression — e.g., "completed متن الآجرومية").

**Growth comparison.** Over time, as FSRS parameters are optimized and assessment data accumulates, the user model can identify which sciences Rayane learns fastest in, which types of content he retains best (definitions vs. evidence chains vs. scholarly positions), and which study patterns correlate with better retention (morning study vs. evening, long sessions vs. short bursts). This is self-knowledge about learning — transformative because no manual study method can provide it.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: sufficient engagement data (minimum 30 days of active study for meaningful trajectories), FSRS optimization (for personalized forgetting curves), and scholar interface milestone definitions.

#### §4.B.2 — Prerequisite Readiness Prediction

The taxonomy engine's prerequisite graph defines which topics depend on which other topics. The user model's knowledge state estimation (§4.A.2) already uses prerequisites as a signal. This capability goes further: it predicts whether Rayane is READY for a specific topic based on his current knowledge state across all prerequisites, and identifies the optimal study order to reach readiness.

**Readiness score.** For any leaf in the taxonomy, the user model computes a readiness score (0.0–1.0) that estimates how prepared Rayane is to study that topic. The score considers: the confidence scores of all direct prerequisites (weighted by prerequisite strength — some prerequisites are more critical than others, as defined in the taxonomy), the confidence scores of transitive prerequisites (prerequisites of prerequisites, with diminishing weight), and the overlap with Rayane's current study context (if he's actively studying the same branch, readiness is higher because context is fresh).

**Readiness gap identification.** When the readiness score is below a threshold (default: 0.60), the user model identifies the specific prerequisites that are lacking and ranks them by impact: "To be ready for الحال, you need to strengthen your understanding of المفعول به (confidence: 0.45) and النعت (confidence: 0.38). المفعول به is more critical because 8 other topics in your curriculum also depend on it."

**Optimal study path computation.** Given a target topic (or set of topics), the user model computes the shortest study path that brings all prerequisites to the readiness threshold. This uses a topological sort of the prerequisite graph filtered to only unready topics, ordered by: dependency depth (deepest prerequisites first — you can't build on an unstable foundation), cross-topic impact (prerequisites that serve multiple targets are prioritized), and estimated study time (based on content length and Rayane's pace in this science). The study path is returned to the scholar interface, which may present it as a curriculum.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: taxonomy engine's prerequisite graph (§4.B.2 of taxonomy SPEC), sufficient knowledge state data, and content length estimates from entries.

#### §4.B.3 — Knowledge Decay Prediction and Proactive Review

Beyond standard spaced repetition (which schedules reviews for items Rayane has explicitly studied), this capability predicts knowledge decay for topics that are NOT in the spaced repetition system — topics Rayane studied but never created review items for, or topics where understanding may have degraded due to lack of use.

**Decay prediction model.** Using the FSRS forgetting curve parameters (optimized from Rayane's actual review data per §4.A.3) and the engagement history, the user model estimates the current retrievability of every topic Rayane has studied — even those without active FSRS review items. The estimate uses: time since last engagement, depth of original engagement (a topic mastered after 3 assessment rounds decays slower than one that was only read), science-specific decay rates (from FSRS optimization — Rayane may forget Nahw rules slower than Fiqh details), and prerequisite reinforcement (engaging with a topic that depends on another topic partially reinforces the prerequisite — studying الحال reinforces understanding of المفعول به).

**Proactive review recommendations.** When the predicted retrievability of a studied topic drops below a threshold (default: 0.70), the user model generates a `decay_alert` that the scholar interface can present as a review recommendation. Unlike standard spaced repetition (which reviews individual items), decay alerts are topic-level: "Your understanding of باب الاستثناء is likely fading (estimated retrievability: 0.58). You studied it 47 days ago and haven't engaged with related topics since. A quick review session would take approximately 15 minutes." This turns the user model from a passive recorder into an active guardian of Rayane's knowledge.

**Prerequisite decay cascading.** When a prerequisite topic's predicted retrievability drops below a critical threshold (default: 0.50), the user model flags all dependent topics as potentially weakened — even if the dependent topics were recently reviewed. The scholar interface can then recommend a prerequisite refresh before continuing with advanced topics. This prevents the common problem of "I passed the review but I don't actually understand it anymore because I forgot the foundation."

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: FSRS parameter optimization (§4.A.3), sufficient engagement history (minimum 60 days for meaningful decay estimates), taxonomy prerequisite graph.

## 5. Validation and Quality

The user model's data directly affects every interaction Rayane has with KR. A wrong mastery level means the scholar interface gives wrong recommendations. A lost engagement event means Rayane's study history has a gap. A corrupted FSRS card means spaced repetition fails. Validation is therefore critical.

**§8 Layer 1 — Self-validation on writes.** Every write to the user model is validated before persistence:
- Schema validation: every event, record, and state update conforms to its JSON schema.
- Referential integrity: every target ID references an entity that exists in the library. If the entity has been deleted (e.g., a leaf was removed during taxonomy evolution), the write is rejected with `UM_STALE_TARGET` and the caller is notified.
- Temporal consistency: engagement events must be in chronological order per target. An event with a timestamp earlier than the most recent event for the same target is rejected with `UM_TEMPORAL_VIOLATION` (prevents replayed or out-of-order events from corrupting state).
- State machine consistency: mastery level transitions must follow the valid progression (`unseen` → `viewed` → `read` → `studied` → `assessed` → `mastered` → `retained`). A transition from `unseen` directly to `mastered` is rejected with `UM_INVALID_TRANSITION` — it indicates a missing intermediate event.

**§8 Layer 1 — Self-validation on reads.** Confidence score computation (§4.A.2) validates its inputs: if the taxonomy prerequisite graph references leaves that don't exist in the engagement data, the prerequisite signal defaults to 1.0 (no penalty for missing data) and a warning is logged. If FSRS card states are corrupted (invalid JSON, impossible dates), the card is reset to a new card state and a warning is logged.

**§8 Layer 2 — Automated periodic checks.**
- Engagement coverage check: compares the set of leaves Rayane has engaged with against the current taxonomy tree. If leaves exist in engagement data but not in the tree (taxonomy evolution removed them), the engagement data is flagged for review — not deleted, because the historical record is still valuable.
- FSRS health check: for all active review items, verifies that FSRS card states are valid and next due dates are in a reasonable range (not more than 365 days in the future for any card, not in the past by more than the grace period).
- Curriculum validity check: for all active curricula, verifies that the sequence references valid leaves (§4.A.5 taxonomy evolution detection).

**What prevents data loss.** The user model writes to disk after every successful write operation (not batched — a crash should lose at most one event). Engagement events are append-only: they are never deleted or modified after creation. State changes (mastery level, FSRS card state) are logged as events, not overwrites — the complete history is preserved. Periodic backups of the entire user model directory are the responsibility of the application's infrastructure layer, not the user model itself — but the user model's file format is designed for easy backup (JSON files, no binary blobs, no database).

## 6. Consensus Integration

The user model does NOT use multi-model consensus. This is an explicit, conscious decision.

**Rationale.** The user model does not make high-stakes content decisions that benefit from independent verification. It records engagement events (factual — either Rayane interacted with something or he didn't), computes derived scores (mathematical — the formula is deterministic given the inputs), and manages FSRS scheduling (algorithmic — the FSRS library handles scheduling deterministically). None of these operations involve the kind of ambiguous judgment calls where a second model's opinion would add value.

The closest thing to a judgment call is the engagement depth classification (did this engagement count as "read" vs. "studied"?), but this classification is based on objective signals (time, actions, explicit markers) with defined thresholds — not LLM interpretation. If a future requirement introduces LLM-based assessment scoring that feeds into the user model, consensus should be reconsidered for that specific pathway.

## 7. Error Handling

**UM_UNKNOWN_EVENT_TYPE** (severity: warning). An event with an unrecognized event_type was submitted. Recovery: reject the event, log the full payload, return error to caller. The caller (scholar interface or engine) may have a bug or be using a newer event type that the user model hasn't been updated to recognize.

**UM_INVALID_TIMESTAMP** (severity: warning). An event timestamp is invalid or more than 60 seconds in the future. Recovery: reject the event, return error to caller. This likely indicates a clock synchronization issue.

**UM_INVALID_TARGET** (severity: warning). An event references a target entity (leaf, entry, excerpt, science, curriculum) that does not exist in the library. Recovery: reject the event, return error to caller. This may indicate that taxonomy evolution removed the target between when the scholar interface displayed it and when the engagement event was recorded. The caller should refresh its state.

**UM_INVALID_PAYLOAD** (severity: warning). An event's payload does not conform to its event_type's schema. Recovery: reject the event, return error to caller.

**UM_TEMPORAL_VIOLATION** (severity: warning). An engagement event's timestamp is earlier than the most recent event for the same target. Recovery: reject the event, return error to caller. This may indicate a replayed event or a race condition in the scholar interface.

**UM_INVALID_TRANSITION** (severity: warning). A mastery level transition does not follow the valid progression. Recovery: reject the event, return error to caller. This may indicate the scholar interface skipped an intermediate event (e.g., reported "mastered" without a preceding "assessed" event).

**UM_STALE_TARGET** (severity: info). An event references a target that existed previously but has been removed by taxonomy evolution. Recovery: reject the event, return error to caller with the ID of the entity that replaced the removed one (if known from the taxonomy evolution record).

**UM_FSRS_CORRUPTION** (severity: warning). An FSRS card state is invalid (malformed JSON, impossible dates, out-of-range parameters). Recovery: reset the card to a new card state, log the corruption details, generate a `fsrs_reset` alert for the scholar interface. The review item continues with a fresh schedule — some review history is lost for this item, but no data is silently corrupted.

**UM_CURRICULUM_INVALID** (severity: info). A curriculum's sequence references leaves that no longer exist. Recovery: flag the affected sequence entries, return the curriculum with flags to the caller. The scholar interface handles curriculum adaptation — the user model does not modify curricula autonomously.

**UM_DISK_WRITE_FAILURE** (severity: fatal). The user model cannot write to disk. Recovery: the current operation fails and returns an error. The caller must retry. If disk writes fail repeatedly, the user model enters a read-only mode where it serves existing data but rejects all writes, and generates a `critical_storage_failure` alert. No data is lost (the data that failed to write was never committed), but new events are lost until the storage issue is resolved.

**Principle: fail-loud over fail-silent (D-033).** Every error is logged with: the error code, the full event that triggered it, the timestamp, and the component that submitted the event. No error is silently swallowed. If an engagement event is rejected, the scholar interface knows and can inform Rayane or retry.

## 8. Configuration

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| `reading_speed_wpm` | 150 | 50–500 | Arabic scholarly text reading speed for view→read threshold |
| `study_time_multiplier` | 2.0 | 1.5–5.0 | Multiplier over reading time for read→studied threshold |
| `mastery_threshold` | 0.80 | 0.50–1.00 | Assessment comprehension score for assessed→mastered transition |
| `recency_half_life_days` | 30 | 7–180 | Half-life for recency decay in confidence score computation |
| `fsrs_desired_retention` | 0.90 | 0.70–0.99 | FSRS target retention rate |
| `fsrs_optimization_threshold` | 200 | 50–1000 | Minimum reviews before FSRS parameter optimization |
| `fsrs_optimization_interval` | 500 | 100–5000 | Reviews between automatic FSRS re-optimizations |
| `review_grace_period_days` | 3 | 1–14 | Days past due date before review is flagged as overdue |
| `fsrs_retirement_stability_days` | 365 | 90–730 | FSRS stability threshold for review item retirement |
| `decay_alert_threshold` | 0.70 | 0.40–0.90 | Predicted retrievability below which a decay alert is generated |
| `prerequisite_decay_critical` | 0.50 | 0.30–0.70 | Prerequisite retrievability below which dependent topics are flagged |
| `readiness_threshold` | 0.60 | 0.30–0.80 | Minimum readiness score for a topic to be considered "ready" |
| `alert_retention_days` | 90 | 30–365 | Days before dismissed/acted alerts are archived |
| `view_minimum_seconds` | 3 | 1–10 | Minimum on-screen time for an engagement to count as "viewed" |
| `confidence_weight_engagement` | 0.30 | 0.10–0.50 | Weight of engagement depth in confidence score |
| `confidence_weight_assessment` | 0.35 | 0.10–0.50 | Weight of assessment performance in confidence score |
| `confidence_weight_recency` | 0.20 | 0.05–0.40 | Weight of recency in confidence score |
| `confidence_weight_prerequisites` | 0.15 | 0.05–0.30 | Weight of prerequisite strength in confidence score |

**Per-science configuration.** The following parameters can be overridden per science via the scholarly profile: `mastery_threshold` (some sciences may require higher assessment scores), `recency_half_life_days` (Nahw rules may be retained longer than Fiqh details), `fsrs_desired_retention` (critical sciences may warrant higher retention targets), and the expertise level thresholds (what percentage of the tree must be covered for each expertise level).

**What is configurable vs. hardcoded.** The engagement level progression (`unseen` → `viewed` → `read` → `studied` → `assessed` → `mastered` → `retained`) is hardcoded — the levels are definitional, not tunable. The confidence score formula structure (weighted sum of four signals) is hardcoded — the weights are tunable but the signals themselves are fixed. The FSRS algorithm is hardcoded to FSRS v6 — the parameters are tunable but the algorithm is not swappable (FSRS is demonstrably the best open-source spaced repetition scheduler; see RESOURCES.md). Event validation rules are hardcoded — the validation schema is not configurable per deployment.

## 9. Current Implementation State

**Existing files.** `shared/user_model/CLAUDE.md` (21 lines) — orientation file listing data tracked and integration points. No implementation code exists.

**Known gaps between this SPEC and current code.** Everything in this SPEC is unbuilt. There is no user model implementation. The closest existing code is the human gate's `confidence.json` management, which this SPEC subsumes.

**External tools and libraries.**
- **py-fsrs** (Python package `fsrs`, v5.1+): FSRS v6 spaced repetition scheduling. Handles card state management, review scheduling, retrievability computation, and JSON serialization. Used for: all spaced repetition logic in §4.A.3.
- **fsrs-optimizer** (Python package `fsrs-optimizer`): Optional — used for personalizing FSRS parameters from Rayane's review history. Requires PyTorch. Used for: §4.A.3 FSRS parameter optimization.

**What each external tool handles vs. custom code.**
- py-fsrs handles: card state management, review scheduling (next due date computation), retrievability estimation, parameter management, JSON serialization/deserialization. The user model wraps this — it does not reimplement scheduling logic.
- Custom code handles: engagement tracking (§4.A.1), knowledge state estimation (§4.A.2 — the confidence score computation), scholarly profile management (§4.A.4), curriculum state management (§4.A.5), bookmarks and annotations (§4.A.6), alert management (§4.A.7), all validation (§5), all error handling (§7), and all transformative capabilities (§4.B).

**Storage layout.**
```
library/user_model/
├── engagement/
│   ├── {science_id}/
│   │   └── {leaf_id}.json       # Per-leaf engagement records
│   └── _index.json              # Leaf→science mapping for fast lookup
├── reviews/
│   ├── items/
│   │   └── {review_item_id}.json # FSRS card state per review item
│   ├── log.jsonl                 # Append-only review log (all review events)
│   └── optimizer_state.json      # FSRS optimized parameters
├── curricula/
│   └── {curriculum_id}.json      # Per-curriculum state
├── bookmarks/
│   └── bookmarks.json            # All bookmarks (single file — manageable size for one user)
├── annotations/
│   └── {target_type}/
│       └── {target_id}.json      # Annotations grouped by target
├── alerts/
│   ├── active.json               # Current unread and read alerts
│   └── archive/
│       └── {year}-{month}.json   # Archived alerts by month
├── profile.json                  # Scholarly profile: expertise levels, preferences, study patterns
└── _schema_version.json          # Schema version for migration support
```

All files are JSON. The user model is designed for a single user (Rayane) — there is no multi-user consideration. File sizes are manageable: even with years of engagement data, individual leaf engagement files will be small (hundreds of events at most per leaf), and the review log will be the largest file (potentially tens of thousands of lines, but JSONL format handles this efficiently).

**[NOT YET IMPLEMENTED]** — Everything. The entire component needs to be built from scratch.

## 10. Test Requirements

**What MUST be tested.**

**Engagement tracking tests.** Verify: all six engagement levels are correctly classified from input signals, engagement aggregation correctly computes leaf-level mastery from entry-level events, per-leaf mastery is the minimum across school-group entries, engagement events are correctly preserved across entry regeneration, the view minimum time threshold correctly filters accidental navigation, and temporal ordering is enforced.

**Knowledge state estimation tests.** Verify: confidence score computation produces correct results for known inputs (manually computed expected values for each signal and the weighted sum), recency decay correctly decreases over time, prerequisite strength correctly aggregates across the prerequisite graph, scores are correctly recomputed when the taxonomy prerequisite graph changes, and edge cases — a leaf with no engagement returns `unseen`/0.0, a leaf with all prerequisites at 0.0 correctly penalizes the confidence score.

**FSRS integration tests.** Verify: review items are correctly created with appropriate FSRS card states, review results correctly update card states and schedule next reviews, FSRS JSON serialization round-trips correctly (serialize → deserialize → same state), the retirement threshold correctly retires high-stability items, and card corruption detection and reset works.

**Curriculum state tests.** Verify: curriculum progression correctly advances position, skipped topics are recorded but position advances, taxonomy evolution detection correctly flags invalid curricula, and multiple simultaneous curricula are tracked independently.

**Validation tests.** Every error code in §7 must have at least one test that triggers it and verifies the correct error response.

**Gold baselines.** A gold baseline user model state — engagement records, FSRS card states, curriculum state, and scholarly profile for a simulated 30-day study period — should be created and used for regression testing. The baseline includes: known engagement events with expected mastery levels, known FSRS review sequences with expected scheduling, and known confidence scores with expected values.

**Integration test requirements.**
- With human gate: verify that the user model correctly serves expertise level data that the human gate uses for confidence calibration (§4.A.4.1 migration).
- With scholar interface: verify that engagement events from the interface are correctly stored and that knowledge state queries return consistent results.
- With processing engines: verify that alert events from engines are correctly stored and queryable.
- With taxonomy engine: verify that taxonomy evolution correctly triggers curriculum validity checks and that engagement data for removed leaves is flagged but not lost.
