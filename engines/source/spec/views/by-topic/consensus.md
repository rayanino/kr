# Source Spec Atoms by Topic: consensus

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0006 | decision | Agents resolve disagreements autonomously | proposed | critical |
| INV-SRC-0004 | invariant | Truth-seeking over consensus-forcing | proposed | high |
| OF-SRC-0011 | feedback | Agents resolve disagreements without human gate | confirmed | critical |
| OF-SRC-0013 | feedback | Disagreement may itself be the true answer | confirmed | high |
| OQ-SRC-0004 | question | Formal replacement for human_gate | draft | high |
| REQ-SRC-0009 | requirement | Agent self-resolution of disagreements | proposed | critical |

### DEC-SRC-0006 — Agents resolve disagreements autonomously
- Type: decision
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011
- Chosen option: OPT-B — Agent self-resolution with failure analysis
- Decision rationale: This matches the owner's desire for autonomous resolution plus system learning.

### INV-SRC-0004 — Truth-seeking over consensus-forcing
- Type: invariant
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013
- Rule: When the real answer is that scholars disagree, the engine must record disagreement as the result.

### OF-SRC-0011 — Agents resolve disagreements without human gate
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 3 question 3
- Interview question: What should happen when agents disagree on metadata?
- Owner answer: Human gate checkpoints for metadata disagreements should be removed. Agents resolve disagreements autonomously, and the agent that erred should analyze its own failure so the system improves.

### OF-SRC-0013 — Disagreement may itself be the true answer
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 4 question 1
- Interview question: What counts as successful resolution when scholars disagree?
- Owner answer: Resolution does not mean forcing one entity. If scholars genuinely disagree, the engine should record every supported position with evidence because the goal is truth-seeking, not consensus-forcing.

### OQ-SRC-0004 — Formal replacement for human_gate
- Type: question
- Status: draft
- Priority: high
- Confidence: medium
- Source: Derived from OF-SRC-0011
- Candidates:
  - OPT-A: Agent-gate module (likely)
  - OPT-B: Confidence threshold resolver (possible)
  - OPT-C: Supervisor veto (possible)

### REQ-SRC-0009 — Agent self-resolution of disagreements
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011
- Trigger: Independent agents disagree about a metadata field.
- Postconditions:
  - Agents resolve the disagreement autonomously without owner intervention.
  - The failing or losing agent emits structured failure analysis for system improvement.
- Acceptance criteria:
  - AC-1 [integration] Given A simulated metadata disagreement.; When The disagreement workflow runs.; Then The agents resolve the case without owner intervention..
  - AC-2 [deterministic] Given An agent loses or retracts its position in disagreement review.; When Resolution completes.; Then That agent produces structured failure analysis linked to the case..
