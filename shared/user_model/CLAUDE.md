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
