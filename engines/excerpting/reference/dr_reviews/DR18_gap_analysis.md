# DR18 Gap Analysis: 11 Missed Owner-Dependent Decisions

**Source:** CC explore agent cross-referencing DR18 against shared/ components and engine contracts
**Date:** 2026-04-07

DR18 mapped 31 decision points across 5 engines. It missed 11 decisions concentrated in shared components (human_gate, consensus, user_model, feedback) and engine configuration.

## Gaps Found

### Shared: Human Gate

**HG-D-001: Pre-Approval Policies**
- **Component:** `shared/human_gate/SPEC.md:25, 170-180`
- **Description:** Owner defines policies that auto-approve certain gate categories. Each policy: gate_type, scope (science, source_id, engine_id), conditions (min_confidence), active status.
- **Classification:** PERMANENTLY OWNER-DEPENDENT
- **Capture:** Policy creation sessions — "which gate types should auto-approve?"
- **Impact:** ALL engines — reduces gate queue volume

**HG-D-002: Per-Science Expertise Calibration**
- **Component:** `shared/human_gate/SPEC.md:157-164`
- **Description:** Owner's expertise level per science (expert/intermediate/beginner/none) adjusts gate thresholds. Beginner: +0.10 confidence required. None: all pre-approvals suspended.
- **Classification:** PERMANENTLY OWNER-DEPENDENT (evolves over time)
- **Capture:** Monthly declaration per science
- **Related:** UM-D-001 (user_model expertise)

**HG-D-003: Queue Alert Thresholds**
- **Component:** `shared/human_gate/SPEC.md:348-353`
- **Description:** Configurable: queue_alert_threshold (default 20), stale_checkpoint_threshold (default 7 days), policy_suggestion_threshold (default 30 approvals).
- **Classification:** OWNER configuration (sensible defaults exist)
- **Capture:** THRESHOLD_SETTING — 3 numbers

### Shared: Consensus

**CON-D-001: Decision-Type Model Affinities**
- **Component:** `shared/consensus/SPEC.md:74-78, 323`
- **Description:** Preferred model pairs for specific decision types. E.g., author_identification prefers models with strong Arabic NLP.
- **Classification:** AUTOMATABLE WITH TRAINING DATA (initial assessment needed)
- **Capture:** Model performance evaluation per decision type
- **Config:** `config/consensus.yaml` (global) + `config/sciences/{id}/consensus.yaml` (per-science)

### Shared: Feedback

**FB-D-001: Regression Tolerance**
- **Component:** `shared/feedback/SPEC.md:218, 373-376`
- **Description:** When regression tests show quality degradation after update, what degradation is acceptable? FEEDBACK_REGRESSION_TOLERANCE threshold.
- **Classification:** PERMANENTLY OWNER-DEPENDENT (risk tolerance)
- **Capture:** THRESHOLD_SETTING — one percentage

### Shared: User Model

**UM-D-001: Expertise Level Declaration**
- **Component:** `shared/user_model/SPEC.md:127-135`
- **Description:** Per-science expertise: none/beginner/intermediate/advanced/researcher. Owner can override upward. PRIMARY data source for all expertise-dependent components.
- **Classification:** PERMANENTLY OWNER-DEPENDENT
- **Capture:** Initial declaration + monthly refresh
- **Note:** DR18 mentions PP-003 (study focus) but NOT the formal user_model expertise system

**UM-D-002: Study Preferences**
- **Component:** `shared/user_model/SPEC.md:133-135`
- **Description:** preferred_depth (survey/standard/deep/exhaustive), preferred_interaction_style (guided/exploratory/challenge), preferred_languages, study_schedule, notification_preferences.
- **Classification:** PERMANENTLY OWNER-DEPENDENT
- **Capture:** Configuration interview

### Engine-Specific Gaps

**SRC-D-011: Source Gate Pre-Approval Config**
- **Component:** Source engine gate types + `shared/human_gate/`
- **Description:** Which source engine gate types auto-approve vs always escalate.
- **Classification:** PERMANENTLY OWNER-DEPENDENT
- **Capture:** Policy creation per gate type

**EXC-D-011: Excerpting Gate Trigger Toggles**
- **Component:** `engines/excerpting/contracts.py:827-829`
- **Description:** ExcerptingConfig has 3 booleans: GATE_ON_DEPENDENT (True), GATE_ON_ATTRIBUTION_DISAGREEMENT (True), GATE_ON_SCHOOL_CONFLICT (True).
- **Classification:** OWNER configuration
- **Capture:** BINARY_CHOICE per toggle

**EXC-D-012: LLM Model Selection per Phase**
- **Component:** `engines/excerpting/contracts.py:807-824`
- **Description:** ExcerptingConfig model choices: CLASSIFY_MODEL, GROUP_MODEL, ENRICH_MODEL, VERIFY_MODEL, ESCALATION_MODEL.
- **Classification:** AUTOMATABLE WITH TRAINING DATA
- **Capture:** Model performance evaluation on real excerpts

**SYN-D-007: Permanent Constraint Policy**
- **Component:** `engines/synthesis/SPEC.md §2.3`
- **Description:** Which correction types should be "permanent" (surviving regeneration)? DR18 mentions SYN-D-004 but doesn't frame it as a policy to define upfront.
- **Classification:** PERMANENTLY OWNER-DEPENDENT
- **Capture:** Policy definition + operational decisions

## Summary: Revised Decision Count

| Engine/Component | DR18 | Gaps | Total |
|-----------------|------|------|-------|
| Source | 10 | 1 | 11 |
| Normalization | 5 | 0 | 5 |
| Excerpting | 10 | 2 | 12 |
| Taxonomy | 7 | 0 | 7 |
| Synthesis | 6 | 1 | 7 |
| Shared (human_gate) | 0 | 3 | 3 |
| Shared (consensus) | 0 | 1 | 1 |
| Shared (feedback) | 0 | 1 | 1 |
| Shared (user_model) | 0 | 2 | 2 |
| **TOTAL** | **31** | **11** | **42** |

## Impact on Collection Plan

Most gaps add to Session A (Science & Scope) and Session D (Thresholds & Policies):
- UM-D-001 expertise levels → Session A (+5 min)
- UM-D-002 study preferences → Session A (+10 min)
- HG-D-001 pre-approval policies → Session D (+15 min)
- FB-D-001 regression tolerance → Session D (+5 min)
- EXC-D-011 gate toggles → Session D (+5 min)
- HG-D-003 queue thresholds → Session D (+5 min, defaults exist)

Total addition to tedious collection: ~45 min across sessions A and D.
