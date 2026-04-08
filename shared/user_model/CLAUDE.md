# User Model — نموذج المستخدم

**Responsibility:** Persistent representation of Rayane's scholarly state. The canonical store for all user state in KR. Tracks engagement, knowledge state estimates, curriculum position, scholarly profile, spaced repetition, bookmarks, annotations, and alerts. Read by the scholar interface for every interaction. Written to by: scholar interface (engagement, assessments, curriculum), processing engines (alerts), human gate (gate resolution evidence).

## Core Capabilities (SPEC §4.A)

- **Engagement tracking** (§4.A.1): Six-level progression — unseen → viewed → read → studied → assessed → mastered → retained. Tracked per-entry AND per-leaf (leaf mastery = minimum across school-group entries).
- **Knowledge state estimation** (§4.A.2): Per-topic confidence score (0.0–1.0) from four weighted signals: engagement depth (0.30), assessment performance (0.35), recency decay (0.20), prerequisite strength (0.15). Computed on read, never stale.
- **Spaced repetition** (§4.A.3): FSRS v6 via py-fsrs. Review items created by scholar interface, scheduled by user model. FSRS parameter optimization after 200+ reviews.
- **Scholarly profile** (§4.A.4): Per-science expertise level (none/beginner/intermediate/advanced/researcher). **Subsumes human gate's confidence calibration** (D-042). Study preferences and patterns.
- **Gap analysis** (§4.A.4b): Multi-dimensional gaps — topic, school, temporal, science. Computed on demand from engagement + taxonomy + excerpt metadata.
- **Curriculum state** (§4.A.5): Structured learning paths with position tracking, pace statistics, taxonomy evolution detection.
- **Bookmarks and annotations** (§4.A.6): Personal markers. Tarjih annotations are scholarly production.
- **Alert management** (§4.A.7): Alerts from engines and interface, relevance-scored, lifecycle-managed.

## Transformative Capabilities (SPEC §4.B) [NOT YET IMPLEMENTED]

- **Scholarly growth trajectory** (§4.B.1): Longitudinal analysis of knowledge breadth, depth, velocity, forgetting curves.
- **Prerequisite readiness prediction** (§4.B.2): Predicts topic readiness from prerequisite knowledge state. Computes optimal study paths.
- **Knowledge decay prediction** (§4.B.3): Predicts decay for topics not in spaced repetition. Proactive review recommendations. Prerequisite decay cascading.

## External Dependencies

- **py-fsrs** (v5.1+): FSRS v6 spaced repetition scheduling. All scheduling logic delegated to this library.
- **fsrs-optimizer**: Optional. Personalizes FSRS parameters from review history. Requires PyTorch.

## Storage

`library/user_model/` — JSON files. Engagement per-leaf, FSRS cards per-item, review log (JSONL), curricula, bookmarks, annotations, alerts, profile.

## Integration Points

- Human gate READS expertise level from user model (replaces confidence.json)
- Scholar interface is primary reader AND writer
- Processing engines write ONLY alerts
- Taxonomy engine changes trigger curriculum validity checks
- Synthesizing engine may use study depth to adjust analytical layer

## SPEC Refinement Status
- Cycle 0 (not yet started)
- Implementation-ready: NO — refinement required before implementation

## Claude Code Behaviour Guidelines

- **Ownership, not deflection:** When you encounter an issue, take responsibility and work towards a solution. Don't say "not caused by my changes" or "pre-existing issue." Don't give up with "known limitation" or defer to "future work." Fix it now.
- **Persistence through obstacles:** Don't stop at the first problem. Don't declare "good stopping point" or "natural checkpoint." Keep pushing until you have a complete, verified solution.
- **Initiative over permission-seeking:** If you have the knowledge and capability to solve a problem, act. Don't ask "should I continue?" or "want me to keep going?" Take initiative and drive towards the solution.
- **Plan before acting:** For multi-step work, plan which files to read, in what order, which tools to use, and what the expected outcome is — before touching anything.
- **Convention recall:** Always re-read and apply project-specific conventions from CLAUDE.md files. Don't rely on memory of what they say.
- **Self-correction loops:** Catch your own mistakes by applying reasoning loops and self-checks. Fix errors before committing or asking for help.
- **Verify, don't assume:** After reaching a conclusion or making a change, verify it against the actual state of the codebase. A conclusion you haven't verified is a guess. Run the test, read the output, check the file.
- **Trace root causes:** When something fails, trace the full causal chain. Don't patch symptoms — find and fix the underlying cause. A surface fix hides the real bug for later.

### Tool Use

- **Research-first, never edit-first:** Before using any tool, research the context and requirements. Read the relevant code, SPEC, and contracts before making changes. Understand before you act.
- **Surgical edits over rewrites:** Make targeted, minimal changes. Never rewrite whole files or make large sweeping changes when a focused edit achieves the goal.
- **Reasoning loops are mandatory:** Apply reasoning loops frequently. Don't skip them to save tokens. The cost of a wrong action far exceeds the cost of thinking.

### Thinking Depth

- Always apply the **highest level of thinking depth**. Shallow thinking leads to the cheapest available action, which is rarely the correct one. Spending more tokens on reasoning produces dramatically better outcomes.
- **Never reason from assumptions.** Always reason from actual data — read and understand the actual code, SPEC, or documentation before making decisions. Assumptions compound into errors.
