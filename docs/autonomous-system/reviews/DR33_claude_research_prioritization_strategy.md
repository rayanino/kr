# Research prioritization framework for KR's 83-day deep research campaign

The KR project (خزانة ريان) faces a clear bottleneck: **three of seven engines have only first-draft SPECs, and all must be build-ready by July 1**. The critical path runs through an 8-topic dependency chain from metadata schema design through synthesis architecture. This framework transforms 830 daily DR sessions into a precision instrument that eliminates every "research first" blocker before the summer build begins—by front-loading high-dependency architectural decisions in Phase 1, accelerating engine SPECs in Phase 2, and closing the long tail in Phase 3.

The framework is grounded in the project's actual repository state: excerpting's 942 tests proving the hardening methodology works, nahw v2.0's 183-leaf tree demonstrating taxonomy granularity expectations, and the original project context document's taxonomy trees for الإملاء, الصرف, النحو, and البلاغة—each containing hundreds of atomic leaf nodes. The taxonomy trees in the project context document reveal the extraordinary granularity expected: the الإملاء tree alone has **~250+ leaf nodes** spanning hamza rules, alif types, tā' marbūṭa/maftūḥa disambiguation, wāw/yā' handling, punctuation, and Unicode normalization. This granularity directly informs how many DR sessions the taxonomy category needs.

---

## QUESTION 1: Research topic distribution across five categories

The allocation below reflects two realities: three engines with first-draft SPECs need the most work, and the scholarly domain research must run in parallel because it cannot be retroactively bolted onto engine designs.

| Category | Allocation % | Sessions (of 830) | Top 3 questions (research first) | Saturation signal | Primary DR target |
|---|---|---|---|---|---|
| **a) Engine-specific** | **35%** | **290** | 1. What defines passage boundaries in classical Arabic texts across genres—فقه masā'il vs. حديث isnād-matn vs. نحو qawā'id? (Passaging SPEC, §1-2 gaps) 2. What is the precise atomic unit definition per science—a fiqh ḥukm with dalīl, a hadith with full isnād, a nahw rule with examples? (Atomization SPEC, §1 gap identified in V.02 doc: "no precise definition of excerpt") 3. What RAG architecture ensures synthesis entries cite 5+ scholars accurately while preserving ikhtilāf structure? (Synthesis SPEC, §1-2) | Three consecutive DRs produce **<2 new SPEC section additions** and **>70% semantic overlap** (cosine similarity on sentence embeddings) with prior reports on the same engine. The 942-test excerpting benchmark: when a new DR triggers **0 new test cases** across 3 consecutive sessions. | **Claude DR** (60% of engine sessions): best for careful edge-case reasoning about Arabic text boundaries, code analysis of existing 942 tests, and nuanced atom/excerpt definition work. **ChatGPT DR** (40%): architectural feasibility for synthesis RAG pipeline. |
| **b) Cross-cutting** | **18%** | **150** | 1. What is the complete inter-engine metadata schema—what fields flow from Source→Normalization→Passaging→Atomization→Excerpting→Taxonomy→Synthesis? (D-023 metadata flow, blocking ALL engines) 2. What multi-model consensus protocol works for Arabic Islamic text verification—ICE ensemble, debate pattern, or triangulation? (D-041, affects all engines' accuracy guarantees) 3. What error taxonomy covers the full pipeline—what happens when passaging fails, atomization is ambiguous, classification confidence is low? (Referenced in V.02 doc: "feedback enveloppe" philosophy) | When the metadata schema document has **no open fields marked "TBD"** and the error taxonomy covers all 7 engines with **0 uncategorized error types**. Quantitatively: when DRs on cross-cutting topics generate **<1 new cross-engine interface question** per session for 4+ consecutive sessions. | **ChatGPT DR** (50%): excels at broad integration pattern surveys and schema design comparison. **Claude DR** (30%): deep analysis of error handling edge cases. **Gemini DR** (20%): Arabic-specific cross-cutting concerns. |
| **c) Scholarly domain** | **22%** | **183** | 1. What are the complete kutub/abwāb skeletons for the 4 remaining science trees—and at what leaf granularity, given nahw's 183-leaf benchmark? (Taxonomy SPEC, the V.02 document's "gap nodes" problem confirms under-granularity is a real risk) 2. How should cross-science excerpts be routed—when an أصول الفقه text contains a نحوي grammatical analysis, which tree gets the excerpt? (Original project doc identifies this as a critical gap: "one book about one science might contain excerpts relevant to another science's taxonomy") 3. How do the four madhāhib structure their arguments differently, and what does this mean for atomization boundaries in فقه texts? | When each of the 5 science trees has a **complete skeleton approved by owner** with **0 branches marked "needs research"**, and when cross-science routing rules cover **>90% of observed multi-science excerpts** in a test corpus. Discovery rate of **new science sub-topics drops below 1 per day** across all scholarly DRs. | **Gemini DR** (50%): UAE government testing confirmed Gemini as most culturally accurate for Arabic content; Google's knowledge graph provides the broadest index of Arabic Islamic web content. **Claude DR** (40%): deeper scholarly reasoning about classification decisions and madhab-specific nuances. **ChatGPT** (10%): supplementary web breadth. |
| **d) Architecture/design** | **15%** | **125** | 1. What is the optimal pipeline orchestration—sequential with checkpointing, or parallel with merge? (Original doc: "Speed is absolutely not a necessity"; project doc establishes Claude Code CLI as build tool with Max x20 plan) 2. What data model (relational, document store, graph DB) best serves a taxonomy tree with 183+ leaves per science and many-to-many excerpt mappings? (V.02 document gap #2: "there is no data model") 3. What test strategy ensures the "exhaustive feedback system" philosophy works at scale across 7 engines? (Project doc's core principle: app wrapped in feedback layers) | When all architectural decisions have been made and **0 engine SPECs reference an unresolved architectural question**. The architecture decision record (ADR) list has **no items in "proposed" status**—all are "accepted" or "rejected." | **ChatGPT DR** (60%): strongest at system design comparisons, technology feasibility analysis, and broad architectural pattern surveys. **Claude DR** (30%): architectural code review and edge-case analysis. **Gemini** (10%): Google ecosystem integration patterns. |
| **e) Creative/visionary** | **10%** | **83** | 1. What local LLM fine-tuning strategy would improve Arabic Islamic text processing—AraBERT, AraT5, or Qwen-Arabic as base models on the KR corpus? 2. How should the "scholar agent" interface work—the project doc envisions an entity "living inside the library" with "mastery over the topic" that the owner can study with? 3. What cross-engine innovations could eliminate the excerpting↔taxonomy co-dependency loop through iterative prototyping? | When **>80% of creative DRs** produce ideas that are flagged as "future roadmap" rather than "summer build relevant." When the creative backlog has **>30 documented ideas** and the rate of genuinely novel ideas drops below **1 per 5 DRs**. | **ChatGPT DR** (40%): broadest web research for emerging techniques. **Gemini DR** (40%): educational content design and Arabic NLP innovations. **Claude DR** (20%): careful reasoning about feasibility of visionary concepts. |

### Implementation as Python data structure

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

class DRTarget(Enum):
    CHATGPT = "chatgpt_dr"
    CLAUDE = "claude_dr"
    GEMINI = "gemini_dr"

class Category(Enum):
    ENGINE_SPECIFIC = "engine_specific"
    CROSS_CUTTING = "cross_cutting"
    SCHOLARLY_DOMAIN = "scholarly_domain"
    ARCHITECTURE = "architecture"
    CREATIVE_VISIONARY = "creative_visionary"

@dataclass
class CategoryAllocation:
    category: Category
    pct: float
    sessions_830: int
    top_3_questions: List[str]
    saturation_threshold_drs: int  # after this many DRs, diminishing returns
    saturation_signal: str
    primary_target: List[Tuple[DRTarget, float]]  # target, pct of category

ALLOCATIONS = {
    Category.ENGINE_SPECIFIC: CategoryAllocation(
        category=Category.ENGINE_SPECIFIC,
        pct=0.35, sessions_830=290,
        top_3_questions=[
            "passage_boundary_definition_by_genre",
            "atomic_unit_definition_per_science",
            "synthesis_rag_architecture_with_5_scholar_citation",
        ],
        saturation_threshold_drs=60,  # per engine (~15 each for 4 engines)
        saturation_signal="3_consecutive_drs_with_lt_2_new_spec_sections_and_gt_70pct_overlap",
        primary_target=[(DRTarget.CLAUDE, 0.60), (DRTarget.CHATGPT, 0.40)],
    ),
    Category.CROSS_CUTTING: CategoryAllocation(
        category=Category.CROSS_CUTTING,
        pct=0.18, sessions_830=150,
        top_3_questions=[
            "inter_engine_metadata_schema_d023",
            "multi_model_consensus_protocol_d041",
            "pipeline_error_taxonomy_and_recovery",
        ],
        saturation_threshold_drs=40,
        saturation_signal="0_tbd_fields_in_schema_and_lt_1_new_interface_question_per_session_for_4_sessions",
        primary_target=[(DRTarget.CHATGPT, 0.50), (DRTarget.CLAUDE, 0.30), (DRTarget.GEMINI, 0.20)],
    ),
    Category.SCHOLARLY_DOMAIN: CategoryAllocation(
        category=Category.SCHOLARLY_DOMAIN,
        pct=0.22, sessions_830=183,
        top_3_questions=[
            "complete_kutub_abwab_skeletons_for_4_remaining_trees",
            "cross_science_routing_rules",
            "madhab_specific_argumentation_patterns_for_atomization",
        ],
        saturation_threshold_drs=45,
        saturation_signal="all_5_trees_have_complete_skeleton_and_new_subtopic_discovery_lt_1_per_day",
        primary_target=[(DRTarget.GEMINI, 0.50), (DRTarget.CLAUDE, 0.40), (DRTarget.CHATGPT, 0.10)],
    ),
    Category.ARCHITECTURE: CategoryAllocation(
        category=Category.ARCHITECTURE,
        pct=0.15, sessions_830=125,
        top_3_questions=[
            "pipeline_orchestration_sequential_vs_parallel",
            "data_model_relational_vs_graph_for_taxonomy",
            "test_strategy_for_feedback_enveloppe_at_scale",
        ],
        saturation_threshold_drs=30,
        saturation_signal="0_engine_specs_reference_unresolved_architectural_question",
        primary_target=[(DRTarget.CHATGPT, 0.60), (DRTarget.CLAUDE, 0.30), (DRTarget.GEMINI, 0.10)],
    ),
    Category.CREATIVE_VISIONARY: CategoryAllocation(
        category=Category.CREATIVE_VISIONARY,
        pct=0.10, sessions_830=83,
        top_3_questions=[
            "local_llm_finetuning_strategy_arabert_vs_arat5",
            "scholar_agent_interface_design",
            "cross_engine_innovations_to_break_excerpt_taxonomy_codependency",
        ],
        saturation_threshold_drs=25,
        saturation_signal="gt_80pct_creative_drs_flagged_future_roadmap_not_summer_build",
        primary_target=[(DRTarget.CHATGPT, 0.40), (DRTarget.GEMINI, 0.40), (DRTarget.CLAUDE, 0.20)],
    ),
}
```

---

## QUESTION 2: Research completeness state machine

The state machine tracks each research topic through five states. Every transition is triggered by **code-measurable signals**, never human judgment. The design draws on theoretical saturation from grounded theory (Glaser & Strauss) and novelty detection via running-centroid sentence embeddings.

### State definitions

**IDENTIFIED**: A research gap exists but no DR has been dispatched. Created when a SPEC gap is detected, a DR generates a follow-up question, or a dependency analysis reveals an unresearched prerequisite.

**ACTIVE**: At least one DR dispatched and one response received. The topic is actively producing new information. This is the default state for all topics once research begins.

**DEEP**: Multiple DRs dispatched; findings are refining existing knowledge rather than discovering new territory. The topic has been explored from multiple angles; remaining questions are narrower.

**BLOCKED**: Research depends on another topic that has not yet reached DEEP or SATURATED. The topic cannot make further progress without upstream resolution.

**SATURATED**: Additional DRs produce no new actionable information. The topic is fully researched for summer build purposes.

### State transition table

```python
TRANSITIONS = [
    {
        "from_state": "IDENTIFIED",
        "to_state": "ACTIVE",
        "trigger": "first_dr_dispatched",
        "measurement": "count(dr_prompts_sent[topic]) >= 1",
    },
    {
        "from_state": "ACTIVE",
        "to_state": "DEEP",
        "trigger": "theme_stability_reached",
        "measurement": (
            "count(dr_responses[topic]) >= 3 AND "
            "rolling_3_report_unique_theme_variance < 0.10 AND "
            "avg_semantic_novelty_last_3 < 0.30"
        ),
        # Semantic novelty = 1 - cosine_similarity(new_embedding, centroid_of_prior_embeddings)
        # Theme variance = std(unique_theme_count) / mean(unique_theme_count) over last 3 reports
    },
    {
        "from_state": "ACTIVE",
        "to_state": "BLOCKED",
        "trigger": "unsatisfied_hard_dependency",
        "measurement": (
            "any(dep.state in ['IDENTIFIED', 'ACTIVE'] "
            "for dep in topic.hard_dependencies) AND "
            "count(dr_responses[topic]) >= 2 AND "
            "last_dr_contains_unresolvable_reference_to_dependency"
        ),
        # Detected when NER extraction of the DR report finds >3 references to
        # concepts owned by a dependency topic that is not yet DEEP
    },
    {
        "from_state": "DEEP",
        "to_state": "BLOCKED",
        "trigger": "dependency_regression",
        "measurement": (
            "any(dep.state in ['IDENTIFIED', 'ACTIVE'] "
            "for dep in topic.hard_dependencies) AND "
            "novelty_plateau_but_tsi < 0.80"
        ),
        # Topic can't reach saturation because upstream knowledge is missing
    },
    {
        "from_state": "BLOCKED",
        "to_state": "ACTIVE",
        "trigger": "dependency_resolved",
        "measurement": (
            "all(dep.state in ['DEEP', 'SATURATED'] "
            "for dep in topic.hard_dependencies)"
        ),
    },
    {
        "from_state": "DEEP",
        "to_state": "SATURATED",
        "trigger": "saturation_criteria_met",
        "measurement": (
            "count(dr_responses[topic]) >= 5 AND "
            "avg_semantic_novelty_last_3 < 0.10 AND "
            "action_ratio_last_3 < 0.15 AND "
            "spec_changes_triggered_last_3 == 0 AND "
            "new_followup_questions_last_3 <= 1"
        ),
        # action_ratio = count(actionable_findings) / count(total_findings)
        # Actionable detected via keywords: "should", "must", "implement", "change", "new"
        # Confirmatory detected via: "confirms", "consistent with", "as expected"
    },
    {
        "from_state": "SATURATED",
        "to_state": "ACTIVE",
        "trigger": "reopen_on_external_change",
        "measurement": (
            "external_spec_change_detected_touching_topic OR "
            "dependency_topic_produced_contradicting_finding OR "
            "owner_manual_reopen"
        ),
    },
]
```

### Composite Topic Saturation Index (TSI) computation — ⚠️ AMD-6: Use simplified proxy (keyword-overlap) until embedding infra justified

```python
def compute_tsi(topic) -> float:
    """Returns 0.0 (fully novel) to 1.0 (fully saturated)."""
    ns = compute_novelty_score(topic)  # 0=redundant, 1=novel
    ar = compute_action_ratio(topic)   # actionable / total findings
    qv = compute_question_velocity(topic)  # new_questions(n) / new_questions(1)
    sv = compute_spec_change_velocity(topic)  # spec_changes / dr_count
    ol = compute_avg_overlap(topic)    # avg pairwise cosine sim between reports

    tsi = 1.0 - (
        0.30 * ns +          # novelty score (inverted: low novelty = high saturation)
        0.20 * (1.0 - ol) +  # overlap (high overlap = high saturation)
        0.20 * ar +           # action ratio (low actions = high saturation)
        0.15 * qv +           # question velocity (fewer questions = higher saturation)
        0.15 * sv             # spec change velocity (no changes = high saturation)
    )
    return max(0.0, min(1.0, tsi))

# Thresholds:
# TSI > 0.80 → topic is SATURATED
# TSI 0.50–0.80 → topic is in DEEP (confirmation phase)
# TSI < 0.50 → topic is ACTIVE (still yielding new information)
```

---

## QUESTION 3: Temporal phasing strategy across 83 days

### Phase 1: Foundation sprint (Days 1–28, April 9 – May 6)

```python
PHASE_1 = {
    "name": "FOUNDATION_SPRINT",
    "date_range": ("2026-04-09", "2026-05-06"),
    "days": 28,
    "distribution": {
        Category.ENGINE_SPECIFIC: 0.30,     # 84 sessions → focus on excerpting hardening + passaging SPEC
        Category.CROSS_CUTTING: 0.25,       # 70 sessions → lock metadata schema (D-023), consensus protocol (D-041)
        Category.SCHOLARLY_DOMAIN: 0.10,    # 28 sessions → begin tree skeleton research for 4 remaining sciences
        Category.ARCHITECTURE: 0.30,        # 84 sessions → ALL architectural decisions must be locked by Day 28
        Category.CREATIVE_VISIONARY: 0.05,  # 14 sessions → light exploration only
    },
    "daily_target": 15,  # front-loaded: 15/day avg, up to 20 on weekdays
    "total_sessions": 280,  # 28 * 10 baseline; realistically ~350-420 at 12.5-15/day
    "queue_strategy": (
        "MORNING_BATCH_DOMINANT: Generate 12 prompts each morning (70% of daily). "
        "Reserve 3 afternoon slots for discoveries from morning results. "
        "Batch by DR target: 5 ChatGPT (architecture), 5 Claude (engine code + edge cases), "
        "2 Gemini (Arabic/scholarly). Send all morning batch by 9 AM. "
        "Review completed sessions at 2 PM; generate adaptive follow-ups by 3 PM."
    ),
    "strategic_priority": (
        "Lock ALL architectural decisions and cross-engine contracts. "
        "⚠️ SUPERSEDED BY AMD-1: Critical path starts at RT-03, not RT-01/RT-02 (Source+Norm complete). "
        "RT-03 (book structure) is the gateway. By Day 28, no engine SPEC should reference an unresolved "
        "architectural question. Passaging SPEC should be elevated from first-draft to detailed-draft. "
        "Excerpting hardening should be nearing completion (targeting 1000+ tests)."
    ),
    "transition_criteria": (
        "ALL of: (1) Metadata schema D-023 has 0 TBD fields. "
        "(2) Architecture ADR list has 0 items in 'proposed' status. "
        "(3) Passaging SPEC sections 1-4 are complete (not first-draft). "
        "(4) >= 3 of the 4 remaining taxonomy tree skeletons have initial drafts."
    ),
}
```

**Rationale for Phase 1 distribution**: The V.02 document identified **8 critical gaps** in the original project spec—no data model, no input format spec, no excerpt definition, no cross-science routing. Source and Normalization engines are complete, proving the pipeline's early stages work. But the metadata flowing from them to Passaging has never been formally specified. Phase 1's **30% architecture allocation** (vs. 15% overall) front-loads these blocking decisions. The original project document's core philosophy—"assume infinite time and budget, focus on building an application that utilises that infinite time and budget to incorporate as many tools"—means architecture decisions must be deliberate, not rushed, and Phase 1 is where that deliberation happens.

### Phase 2: SPEC acceleration (Days 29–56, May 7 – June 3)

```python
PHASE_2 = {
    "name": "SPEC_ACCELERATION",
    "date_range": ("2026-05-07", "2026-06-03"),
    "days": 28,
    "distribution": {
        Category.ENGINE_SPECIFIC: 0.40,     # 112 sessions → Atomization + Synthesis SPECs are the focus
        Category.CROSS_CUTTING: 0.15,       # 42 sessions → integration testing patterns, error handling
        Category.SCHOLARLY_DOMAIN: 0.25,    # 70 sessions → complete all 5 taxonomy tree skeletons
        Category.ARCHITECTURE: 0.10,        # 28 sessions → validation and refinement only
        Category.CREATIVE_VISIONARY: 0.10,  # 28 sessions → scholar agent concepts, LLM training strategy
    },
    "daily_target": 12,  # steady state: 10-15/day
    "total_sessions": 280,
    "queue_strategy": (
        "HYBRID_ADAPTIVE: Morning batch of 8 prompts (65% of daily). "
        "Afternoon adaptive slots of 4 prompts driven by UCB1 priority algorithm. "
        "Cross-target consensus: send 1 high-stakes question to all 3 targets daily "
        "for triangulation (especially taxonomy tree decisions). "
        "Weekly synthesis: every Friday, spend 2 DR slots on 'what are we missing?' meta-prompts."
    ),
    "strategic_priority": (
        "Elevate all 3 first-draft SPECs (Passaging, Atomization, Synthesis) to build-ready. "
        "Complete all 5 taxonomy tree skeletons with owner approval. "
        "Resolve the excerpting↔taxonomy co-dependency through iterative prototyping: "
        "define minimal excerpt schema → map to minimal nahw tree → validate → iterate both. "
        "The V.02 document's 'gap nodes' and 'granulation' processes must be fully specified. "
        "scholarly domain research peaks here because taxonomy trees must be locked before "
        "synthesis architecture can be finalized."
    ),
    "transition_criteria": (
        "ALL of: (1) >= 5 of 7 engine SPECs rated 'build-ready' (sections 1-5 complete). "
        "(2) All 5 taxonomy tree skeletons have owner-approved initial versions. "
        "(3) New-topic discovery rate < 3/day for 5 consecutive days. "
        "(4) Critical path topics RT-01 through RT-06 are all in DEEP or SATURATED state."
    ),
}
```

**Rationale for Phase 2 distribution**: Engine-specific research jumps to **40%** because this is where SPECs must be written. The scholarly domain allocation rises to **25%** because the taxonomy tree design (the V.02 document confirms "gap nodes" are a real problem when trees are under-granular) directly feeds into the Excerpting and Synthesis engine designs. The nahw tree's 183 leaves set the precedent; building the الإملاء tree (⚠️ AMD-4: ~80-120 leaves, not 250+), الصرف tree (~300+ leaves), and البلاغة tree (~200+ leaves) requires sustained scholarly research. Architecture drops to 10% because decisions should be locked. ⚠️ AMD-3: Overall scholarly allocation raised to 28% (from 22%).

### Phase 3: Long-tail closure + validation (Days 57–83, June 4 – July 1)

```python
PHASE_3 = {
    "name": "LONGTAIL_CLOSURE_AND_VALIDATION",
    "date_range": ("2026-06-04", "2026-07-01"),
    "days": 27,
    "distribution": {
        Category.ENGINE_SPECIFIC: 0.30,     # 81 sessions → edge cases, hardening, final gaps
        Category.CROSS_CUTTING: 0.15,       # 40 sessions → integration validation
        Category.SCHOLARLY_DOMAIN: 0.20,    # 54 sessions → tree refinement, cross-science routing
        Category.ARCHITECTURE: 0.15,        # 40 sessions → performance, deployment, final validation
        Category.CREATIVE_VISIONARY: 0.20,  # 54 sessions → rises as foundations complete; future roadmap
    },
    "daily_target": 10,  # wind-down in final week to 5-8/day
    "total_sessions": 270,
    "queue_strategy": (
        "BLOCKER_AUDIT_DRIVEN: Every morning, run blocker audit: enumerate ALL remaining "
        "topics not in SATURATED state. Prioritize exclusively by blocker impact score. "
        "Days 57-72: 10-12 prompts/day filling gaps identified by audit. "
        "Days 73-78: 8-10 prompts/day, use triangulation pattern (all 3 targets) for "
        "any remaining high-stakes open questions. "
        "Days 79-83: 5-8 prompts/day, devil's advocate prompts challenging key decisions, "
        "plus final documentation generation."
    ),
    "strategic_priority": (
        "Zero blockers remaining by July 1. Three sub-phases: "
        "(A) Gap-filling (Days 57-72): driven entirely by open-questions register. "
        "Research topics stuck in ACTIVE or DEEP state get priority. "
        "(B) Validation (Days 73-78): send devil's advocate prompts to each DR target "
        "challenging the project's key decisions. Cross-validate critical findings. "
        "(C) Documentation (Days 79-83): generate research summary for each engine SPEC. "
        "Produce the 'Research Complete' certification document. "
        "Creative/visionary rises to 20% because foundational research is done and "
        "forward-looking ideas for the build phase become valuable."
    ),
    "transition_criteria": (
        "EXIT (research campaign complete) when ALL of: "
        "(1) Zero items tagged 'research-first blocker' remain unresolved. "
        "(2) All 7 engine SPECs rated 'build-ready'. "
        "(3) All 20 critical research topics are in SATURATED state. "
        "(4) Owner has approved all 5 taxonomy tree skeletons. "
        "(5) Blocker audit produces 0 items for 3 consecutive days."
    ),
}
```

---

## QUESTION 4: Research dependency graph with 20 topics, critical path, and parallel clusters

### The 20 most important research topics

Each topic is grounded in specific project artifacts. The original project context document, V.02 passage extraction document, and the user's description of engine states provide the primary evidence.

```python
RESEARCH_TOPICS = {
    # TIER 1: FOUNDATION (blocks everything)
    "RT-01": {
        "name": "Inter-engine metadata schema (D-023)",
        "category": Category.CROSS_CUTTING,
        "urgency": "CRITICAL",
        "evidence": "V.02 doc gap #2: 'there is no data model'. Project doc: no specification of what fields each excerpt carries. Metadata must flow from Source through Synthesis.",
        "estimated_drs": 20,
    },
    "RT-02": {
        "name": "Arabic text representation standards",
        "category": Category.CROSS_CUTTING,
        "urgency": "CRITICAL",
        "evidence": "Project context doc section 14 (الكتابة الحاسوبية ومعايير الترميز) defines Unicode normalization policy nodes. Normalization engine is complete but its output format cascades to ALL downstream. Alif unification (أ/إ/آ→ا), hamza handling, tā' marbūṭa policy decisions propagate everywhere.",
        "estimated_drs": 15,
    },
    "RT-03": {
        "name": "Classical Arabic book structure patterns across genres",
        "category": Category.SCHOLARLY_DOMAIN,
        "urgency": "CRITICAL",
        "evidence": "Project doc step A3: 'identify the different excerpts within that book.' OpenITI explicitly notes paragraphs are 'not particularly reliable' in premodern Arabic texts. Shamela exports of 2,519 books span multiple genres with different structural conventions.",
        "estimated_drs": 20,
    },

    # TIER 2: CORE PIPELINE
    "RT-04": {
        "name": "Passaging rules and topic boundary detection",
        "category": Category.ENGINE_SPECIFIC,
        "urgency": "HIGH",
        "evidence": "engines/passaging/SPEC.md is first-draft only. Must define genre-specific passage boundaries: باب/فصل/مسألة for fiqh, per-hadith for hadith collections, verse-by-verse for tafsir. V.02 doc mentions 'Passage 2 extraction' with specific gap-node handling.",
        "estimated_drs": 25,
    },
    "RT-05": {
        "name": "Atomization granularity and edge cases",
        "category": Category.ENGINE_SPECIFIC,
        "urgency": "HIGH",
        "evidence": "engines/atomization/SPEC.md is first-draft only. V.02 doc identified the #1 gap: 'no precise definition of excerpt.' Project doc lists edge cases: 'what if a topic is explained in location X and further explained in location Y? What if a further explanation is within an excerpt about another topic?'",
        "estimated_drs": 25,
    },
    "RT-06": {
        "name": "Excerpt definition hardening and edge cases",
        "category": Category.ENGINE_SPECIFIC,
        "urgency": "HIGH",
        "evidence": "engines/excerpting/SPEC.md sections 1-4 for scope, section 6 for hardening. 942 tests exist. V.02 doc: 'Please be extremely accurate... nothing needs to raise future regrets.' Remaining edge cases: cross-topic side-explanations, half-sentences spanning topics, scholarly attribution metadata.",
        "estimated_drs": 20,
    },
    "RT-07": {
        "name": "Taxonomy tree architecture for 5 sciences",
        "category": Category.SCHOLARLY_DOMAIN,
        "urgency": "HIGH",
        "evidence": "engines/taxonomy/SPEC.md sections 1-2. Nahw v2.0 has 183 leaves. 4 remaining trees needed. Project context document contains full preliminary trees for الإملاء, الصرف, النحو, البلاغة (original 4 Arabic language sciences). ⚠️ AMD-4: الإملاء revised to ~80-120 leaves (not 250+). D3 process for tree evolution (granulate leaf → parent with children, migrate excerpts) referenced in V.02 doc.",
        "estimated_drs": 30,
    },
    "RT-08": {
        "name": "Synthesis engine architecture",
        "category": Category.ENGINE_SPECIFIC,
        "urgency": "HIGH",
        "evidence": "engines/synthesis/SPEC.md is first-draft only. Project doc 'About the Synthetization Engine': entries are 'the soul of the library'—encyclopedic, exhaustive, storyline-like, strictly Arabic. Must cite 5+ scholars per claim. Must go beyond excerpts with deep research. Entries should satisfy: 'there is no other knowledge available in the universe other than what is present in the entry.'",
        "estimated_drs": 25,
    },

    # TIER 3: CROSS-CUTTING
    "RT-09": {
        "name": "Multi-model consensus protocol (D-041)",
        "category": Category.CROSS_CUTTING,
        "urgency": "MEDIUM",
        "evidence": "Referenced in task as D-041. Project doc: 'multi consensus, many deep researches... to ensure that the knowledge present within is absolutely correct and complete.' ICE ensemble approach improves accuracy 7-15% over single model.",
        "estimated_drs": 15,
    },
    "RT-10": {
        "name": "Error handling and recovery patterns",
        "category": Category.CROSS_CUTTING,
        "urgency": "MEDIUM",
        "evidence": "Project doc: 'feedback enveloppe' philosophy. V.02 doc: taxonomy changes logged in taxonomy_changes.jsonl. Pipeline needs defined behavior for every failure mode across 7 engines.",
        "estimated_drs": 12,
    },
    "RT-11": {
        "name": "Test strategy and QA framework",
        "category": Category.ARCHITECTURE,
        "urgency": "MEDIUM",
        "evidence": "Project doc: 'every single thing... needs to be aimed towards what would be best understood by this coding agent [Claude Code].' Excerpting has 942 tests as benchmark. Each engine needs golden test sets + integration tests between engines.",
        "estimated_drs": 15,
    },
    "RT-12": {
        "name": "Pipeline orchestration and data persistence",
        "category": Category.ARCHITECTURE,
        "urgency": "MEDIUM",
        "evidence": "Project doc: 'Speed is absolutely not a necessity.' 2,519 books need processing. Each engine's output must be persisted before the next engine runs (checkpointing). Sequential with rollback capability.",
        "estimated_drs": 10,
    },

    # TIER 4: DOMAIN-SPECIFIC
    "RT-13": {  # ⚠️ SUPERSEDED BY AMD-2: Split into RT-13a (Quranic) + RT-13b (hadith)
        "name": "Quranic citation and hadith isnād detection",
        "category": Category.SCHOLARLY_DOMAIN,
        "urgency": "MEDIUM",
        "evidence": "Project context doc section 12 (الرسم العثماني وملحقات التراث): 'سياسة المشروع عند ورود اقتباس قراني في كتاب'. Quranic verses embedded in scholarly text need identification for taxonomy and synthesis. Hadith isnād chains have distinctive formulaic structure.",
        "estimated_drs": 15,
    },
    "RT-14": {
        "name": "Madhab-specific text handling patterns",
        "category": Category.SCHOLARLY_DOMAIN,
        "urgency": "MEDIUM",
        "evidence": "Relevant when fiqh texts are processed. Each madhab structures arguments differently. Affects atomization boundaries and taxonomy branching. Project doc mentions cross-science routing for multi-science books.",
        "estimated_drs": 12,
    },
    "RT-15": {
        "name": "Cross-science routing rules",
        "category": Category.CROSS_CUTTING,
        "urgency": "MEDIUM",
        "evidence": "Project doc: 'one book about one science might contain excerpts relevant to another science's taxonomy.' V.02 doc gap #6: 'no cross-science routing specification.' Requires all taxonomy trees to be at least partially defined first.",
        "estimated_drs": 12,
    },
    "RT-16": {
        "name": "Scholar attribution and reference extraction",
        "category": Category.SCHOLARLY_DOMAIN,
        "urgency": "MEDIUM",
        "evidence": "Synthesis engine requires 5+ scholars per claim. Project doc: 'References: every claim needs to be backed up by clear examples and quotings of scholars. This needs to be exhaustive (5 or more).' Scholars referenced by kunya, laqab, and nisba require entity resolution.",
        "estimated_drs": 12,
    },

    # TIER 5: VISIONARY
    "RT-17": {
        "name": "Taxonomy tree evolution and version control",
        "category": Category.ENGINE_SPECIFIC,
        "urgency": "LOW",
        "evidence": "V.02 doc: 'granulate leaf → parent with new child leaves, migrate any prior excerpts, log in taxonomy_changes.jsonl.' Trees evolve as more books are processed. Needs formal versioning strategy. Schema evolution best practice: expand-and-contract pattern.",
        "estimated_drs": 10,
    },
    "RT-18": {
        "name": "Local LLM fine-tuning strategy",
        "category": Category.CREATIVE_VISIONARY,
        "urgency": "LOW",
        "evidence": "Project doc mentions OpenAI and Claude API keys with 'infinite credits.' AraBERT, AraT5 as potential base models. The KR corpus itself could become training data.",
        "estimated_drs": 8,
    },
    "RT-19": {
        "name": "Scholar agent interface design",
        "category": Category.CREATIVE_VISIONARY,
        "urgency": "LOW",
        "evidence": "Project doc: 'there needs to be a scholar I can communicate with; I'm the student, they are the scholar. It has mastery over the topic in question, the excerpts, the content of the entries, can answer my questions, validate my ideas.'",
        "estimated_drs": 10,
    },
    "RT-20": {
        "name": "Claude Code agent architecture and optimal setup",
        "category": Category.ARCHITECTURE,
        "urgency": "MEDIUM",
        "evidence": "Project doc: 'the actual application will not be built by humans. Rather, it will be built by coding agents, specifically: claude code cli with the max x20 plan.' Mentions mem0.ai for permanent memory, need for optimal agent teams, documentation optimized for AI agents.",
        "estimated_drs": 10,
    },
}
```

### Dependency list with reasons

```python
DEPENDENCIES = [
    # Format: (predecessor, successor, reason)
    ("RT-01", "RT-04", "Passaging input/output schema cannot be defined without the inter-engine metadata contract"),
    ("RT-01", "RT-05", "Atomization input format depends on the metadata schema flowing from upstream engines"),
    ("RT-01", "RT-06", "Excerpt metadata fields (source, page, confidence, taxonomy path) must align with the schema"),
    ("RT-02", "RT-04", "Passaging topic detection depends on normalization decisions (diacritics, Alif unification)"),
    ("RT-02", "RT-05", "Atomization boundary detection depends on how Arabic text is represented after normalization"),
    ("RT-02", "RT-06", "Excerpt formatting and scholar name extraction depend on Arabic text standards"),
    ("RT-02", "RT-13", "Quranic citation detection depends on how Quranic text is normalized vs. surrounding text"),
    ("RT-03", "RT-04", "Passaging rules are genre-specific; must know book structure patterns first"),
    ("RT-04", "RT-05", "Atomization scope is bounded by passage output—cannot atomize what has not been passaged"),
    ("RT-05", "RT-06", "Excerpt definition depends on what an 'atom' looks like—the V.02 doc's #1 gap"),
    ("RT-06", "RT-07", "Cannot design taxonomy leaf-to-excerpt mapping without knowing the excerpt schema"),
    ("RT-07", "RT-08", "Synthesis generates entries AT leaf nodes—without tree structure, nothing to synthesize"),
    ("RT-07", "RT-15", "Cross-science routing requires all individual taxonomy trees to be at least partially defined"),
    ("RT-06", "RT-08", "Synthesis references excerpts directly; entry format depends on excerpt richness"),
    ("RT-07", "RT-17", "Tree evolution rules require the base tree architecture to be defined first"),
    ("RT-13", "RT-04", "Quranic and hadith markers serve as passage boundary signals in some genres"),
    ("RT-13", "RT-06", "Excerpt metadata should include Quranic verse references and hadith identifiers"),
    ("RT-16", "RT-08", "Synthesis 5+ scholar requirement needs entity resolution to work"),
    ("RT-14", "RT-05", "Madhab-specific argumentation patterns affect how fiqh atoms are bounded"),
    ("RT-11", "RT-06", "Test strategy framework needed to extend excerpting's 942-test methodology to other engines"),
    ("RT-09", "RT-08", "Synthesis accuracy verification depends on multi-model consensus protocol design"),
    ("RT-20", "RT-12", "Pipeline orchestration design should be optimized for Claude Code's execution model"),
]
```

### Critical path: the longest dependency chain

```
⚠️ SUPERSEDED BY AMD-1 — corrected critical path below:
RT-03 → RT-04 → RT-05 → RT-06 → RT-07 → RT-08
Book      Passage   Atom      Excerpt   Taxonomy  Synthesis
Structure Rules     Granular  Hardening Trees     Architecture
~20 DRs   ~25 DRs   ~25 DRs   ~20 DRs   ~30 DRs   ~25 DRs
```

**Total critical path: ~180 DRs across 8 sequential topics.** At 10 DRs/day, this chain requires **18 working days minimum** if each topic reaches DEEP state before the next begins. In practice, topics overlap (RT-01 and RT-02 can start simultaneously; RT-06 is already in hardening). The realistic critical path duration is **35-45 days**, which fits within Phase 1 + Phase 2 (56 days). The bottleneck is the **RT-06↔RT-07 co-dependency**: excerpting and taxonomy design form a loop that must be resolved through iterative prototyping.

The co-dependency between RT-06 and RT-07 is the single most dangerous point in the project's research timeline. The V.02 document's description of "gap nodes" where the taxonomy tree is under-granular proves this is already a live problem: during passage extraction, the system discovers taxonomy deficiencies that force tree evolution. This means excerpting cannot be fully hardened until taxonomy trees are at least partially complete, but taxonomy design depends on understanding the excerpt schema. **The resolution**: run RT-06 and RT-07 in parallel iterative cycles, not sequentially. Define a minimal excerpt schema, build a minimal taxonomy skeleton, test the mapping, then iterate both simultaneously.

### Parallel clusters (no dependencies between clusters)

```python
PARALLEL_CLUSTERS = {
    "CLUSTER_A": {
        "name": "Infrastructure and tooling",
        "topics": ["RT-20", "RT-12"],
        "rationale": "Claude Code setup and pipeline orchestration are about HOW to build, not WHAT to build. Can proceed while domain research happens. RT-20 references project doc's explicit request to optimize for Claude Code CLI.",
        "can_start": "Day 1",
    },
    "CLUSTER_B": {
        "name": "Cross-cutting quality systems",
        "topics": ["RT-09", "RT-10", "RT-11"],
        "rationale": "Multi-model consensus, error handling, and test strategy affect ALL engines but can be designed as reusable frameworks independently. The consensus protocol from D-041, the error taxonomy, and the test harness architecture don't depend on passaging rules or taxonomy design.",
        "can_start": "Day 1",
    },
    "CLUSTER_C": {
        "name": "Arabic NLP detection capabilities",
        "topics": ["RT-13", "RT-16"],
        "rationale": "Quranic citation detection, hadith isnād detection, and scholar attribution extraction are standalone NLP problems. They FEED INTO the main pipeline but can be researched using existing tools (CAMeL Tools, MADAMIRA, Quranic Arabic Corpus) before the pipeline design is finalized.",
        "can_start": "Day 1",
    },
    "CLUSTER_D": {
        "name": "Long-term vision",
        "topics": ["RT-18", "RT-19"],
        "rationale": "Local LLM training and scholar agent interface are important but not blocking the summer build. Research them asynchronously during creative/visionary allocation slots.",
        "can_start": "Day 29 (Phase 2)",
    },
    "CLUSTER_E": {
        "name": "Domain knowledge deep dives",
        "topics": ["RT-03", "RT-07", "RT-14"],
        "rationale": "Book structure patterns, taxonomy architecture, and madhab-specific handling require deep Islamic scholarly domain knowledge. They can be researched together as a scholarly investigation thread, with Gemini DR as the primary target leveraging Google's Arabic knowledge base.",
        "can_start": "Day 1 for RT-03; Day 15+ for RT-07 and RT-14 (once RT-01/RT-02 provide baseline standards)",
    },
}
```

### Optimal first-week execution plan

⚠️ SUPERSEDED BY AMD-1/AMD-2: On Day 1, launch research on **all three parallel clusters A, B, and C** simultaneously alongside the critical path starting at **RT-03** (book structure patterns, not RT-01/RT-02 which are already DEEP). Day 1's 15 prompts: 5 on RT-03 (book structure), 3 on RT-09/RT-10/RT-11 (quality systems), 3 on RT-13a/RT-13b/RT-16 (Quran+hadith+scholar detection — split per AMD-2), 2 on RT-20 (Claude Code setup), 2 on RT-07 (taxonomy trees). By Day 7, book structure should be in ACTIVE approaching DEEP, and all parallel clusters should have first findings in.

The project's own philosophy provides the closing principle: "assume infinite time and budget, focus on building an application that utilises that infinite time and budget to incorporate as many tools and design very intricate systems that deliver top notch quality." The 830 DR sessions are that infinite budget applied to research. This framework ensures not a single session is wasted.

---

## AMENDMENTS (Post-DR Coworker Review Corrections — 2026-04-07)

**Sources:** CC Structural Agent (coworker_dr32_36_structural_review.md) + CC Scholarly Agent (coworker_dr33_34_scholarly_review.md). Applied Session 14.

### AMD-1: Critical Path Starts at RT-03, Not RT-01

**Finding (Q5):** The Source and Normalization engines are COMPLETE — 2 engines with full test suites, proven contracts, and verified metadata flow. RT-01 (metadata schema D-023) and RT-02 (Arabic text standards) are therefore already **largely resolved** by existing implementation. The critical path should start at RT-03 (book structure patterns).

**Correction:** The critical path chain is:

```
RT-03 → RT-04 → RT-05 → RT-06 → RT-07 → RT-08
Book      Passage   Atom      Excerpt   Taxonomy  Synthesis
Structure Rules     Granular  Hardening Trees     Architecture
~20 DRs   ~25 DRs   ~25 DRs   ~20 DRs   ~30 DRs   ~25 DRs
```

Total critical path: **~145 DRs across 6 sequential topics** (reduced from ~180 across 8). RT-01 and RT-02 move to Cluster B (quality systems) as validation/refinement topics, not blocking prerequisites. Realistic critical path duration: **30-38 days** (reduced from 35-45).

**Impact on Phase 1:** The `strategic_priority` no longer says "RT-01 and RT-02 block EVERYTHING downstream." Instead: "RT-03 (book structure) is the gateway — understanding how classical Arabic texts are structured across genres is prerequisite for all downstream engine SPECs."

### AMD-2: RT-13 Must Split — Quranic and Hadith Are Distinct Sciences

**Finding (Q3):** RT-13 "Quranic citation and hadith isnād detection" conflates two entirely distinct Islamic sciences: علوم القرآن (ulum al-Quran) and علوم الحديث (ulum al-hadith). These have different:
- Detection patterns (Quranic: ﴿﴾ brackets, citation formulas like قال تعالى; hadith: isnad chains with حدثنا/أخبرنا)
- Scholarly methodologies (Quranic: tajwid, qira'at, asbab al-nuzul; hadith: jarh wa ta'dil, takhrij)
- Downstream pipeline impacts (Quranic: verse alignment, rasm uthmani; hadith: isnad-matn boundary, narrator chains)

**Correction:** Split into:

```python
RT13_SPLIT = {
"RT-13a": {
    "name": "Quranic citation detection and handling (ulum al-Quran)",
    "category": Category.SCHOLARLY_DOMAIN,
    "urgency": "MEDIUM",
    "evidence": "Project context doc section 12 (الرسم العثماني). Detection patterns: ﴿﴾ brackets, قال تعالى formula, verse numbering. Handling: preserve rasm uthmani, cross-reference to surah/ayah, detect tajwid markers.",
    "estimated_drs": 10,
},
"RT-13b": {
    "name": "Hadith isnād-matn detection and handling (ulum al-hadith)",
    "category": Category.SCHOLARLY_DOMAIN,
    "urgency": "MEDIUM",
    "evidence": "DR34 identified 7 new transmission patterns beyond existing AGENTS.md rules. Detection: isnad chain formulas, matn boundary, narrator entity extraction. Handling: keep isnad atomic, extract hadith grade signals.",
    "estimated_drs": 10,
},
}
```

**Impact on dependencies:** The existing dependency `("RT-02", "RT-13", ...)` splits into two. `("RT-02", "RT-13a", "Quranic text handling depends on Arabic normalization policy for rasm uthmani")` and `("RT-02", "RT-13b", "Hadith narrator name extraction depends on Arabic text representation standards")`.

### AMD-3: Scholarly Domain Allocation Raised to 28-30%

**Finding (Q1):** 22% (183 sessions) is too low. The 5 taxonomy trees alone require extensive research, plus cross-science routing, plus madhab-specific patterns. Scholarly domain research cannot be retroactively bolted onto engine designs.

**Correction:** Raise scholarly allocation from 22% to **28%** (232 sessions). Redistribute from architecture (15%→12%) and creative (10%→7%), since architecture decisions are fewer than DR33 estimated (Source+Norm being complete eliminates many).

```python
# CORRECTED ALLOCATION
ALLOCATIONS_CORRECTED = {
    Category.ENGINE_SPECIFIC:    0.35,   # 290 sessions — unchanged
    Category.CROSS_CUTTING:      0.18,   # 150 sessions — unchanged
    Category.SCHOLARLY_DOMAIN:   0.28,   # 232 sessions — raised from 0.22
    Category.ARCHITECTURE:       0.12,   # 100 sessions — reduced from 0.15
    Category.CREATIVE_VISIONARY: 0.07,   #  58 sessions — reduced from 0.10
}
```

### AMD-4: Imla' Leaf Estimate Corrected (250+ → 80-120)

**Finding (Q2):** DR33 estimated الإملاء tree at ~250+ leaves based on the project context document's preliminary tree. The scholarly agent found this unrealistic — the installed imlaa v1.0 has 105 leaves and the cold-read audit draft has 51 leaves. A well-structured imla' tree should have **80-120 leaves**. The 250+ figure was inflated by counting every sub-variant as a separate leaf.

**Correction:** In the RT-07 entry and Phase 2 rationale, replace "الإملاء tree (~250+ leaves)" with "الإملاء tree (~80-120 leaves)". The sarf estimate (~300+ leaves) is plausible per the scholarly agent and remains unchanged.

### AMD-5: 6/20 Topics Partially Answered

**Finding (Q4, structural review):** RT-01, RT-02, RT-06, RT-09, RT-11, and RT-13 are partially answered by existing work (completed engines, 942 excerpting tests, D-041 implementation). Their initial state should be ACTIVE or DEEP, not IDENTIFIED.

**Correction:** When the research state machine is initialized, these 6 topics start at:
- RT-01: **DEEP** (D-023 metadata flow verified by `verify_metadata_flow.py`)
- RT-02: **DEEP** (Arabic text rules in AGENTS.md, normalization engine complete)
- RT-06: **DEEP** (942 tests, 22 FPs, 23 domain rules, active hardening)
- RT-09: **ACTIVE** (D-041 consensus implemented for excerpting, not yet generalized)
- RT-11: **ACTIVE** (test framework exists for excerpting, not yet formalized cross-engine)
- RT-13: **ACTIVE** (basic patterns in AGENTS.md, DR34 extended with 7 new patterns)

### AMD-6: TSI Requires Embedding Infrastructure

**Finding (Q6, structural review):** The TSI (Topic Saturation Index) computation references semantic novelty via sentence embeddings, but no embedding infrastructure exists in the project. Implementing TSI as specified requires sentence-transformers + PyTorch.

**Correction:** For Phase 0 implementation, use a **simplified TSI proxy** that does not require embeddings:
- Replace semantic novelty with keyword-overlap ratio (Jaccard similarity on extracted key phrases)
- Replace cosine similarity with TF-IDF overlap score
- Add a TODO marker for full embedding-based TSI when torch is justified by the research volume

The simplified proxy is sufficient for the first 50-100 DRs. Upgrade to embedding-based TSI only if keyword overlap proves insufficient for detecting saturation.