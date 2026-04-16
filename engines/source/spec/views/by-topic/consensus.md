# Source Spec Atoms by Topic: consensus

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0006 | decision | Agents resolve disagreements autonomously | confirmed | critical |
| DEC-SRC-0011 | decision | Agent self-resolution replaces human_gate | confirmed | high |
| INV-SRC-0004 | invariant | Truth-seeking over consensus-forcing | confirmed | high |
| OF-SRC-0011 | feedback | Agents resolve disagreements without human gate | confirmed | critical |
| OF-SRC-0013 | feedback | Disagreement may itself be the true answer | confirmed | high |
| OQ-SRC-0004 | question | Formal replacement for human_gate | superseded | high |
| REQ-SRC-0009 | requirement | Agent self-resolution of disagreements | confirmed | critical |

### DEC-SRC-0006 — Agents resolve disagreements autonomously
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011
- Chosen option: OPT-B — Agent self-resolution with failure analysis
- Decision rationale: This matches the owner's desire for autonomous resolution plus system learning.

### DEC-SRC-0011 — Agent self-resolution replaces human_gate
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Resolves OQ-SRC-0004; derived from OF-SRC-0011 and REQ-SRC-0009
- Chosen option: OPT-B — REQ-SRC-0009 pipeline with multi-position fallback
- Decision rationale: Owner said agents resolve everything. REQ-SRC-0009 already specifies the resolution flow, terminal states, failure analysis, and fallback. Adding a separate module creates unnecessary indirection.

### INV-SRC-0004 — Truth-seeking over consensus-forcing
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Rule: A metadata field qualifies as genuine scholarly dispute only when at least two independent agents provide evidence-backed positions for that field.

### OF-SRC-0011 — Agents resolve disagreements without human gate
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 3 question 3
- Interview question: What should happen when agents disagree on metadata?
- Owner answer: Human gate checkpoints for metadata disagreements should be removed. Agents resolve disagreements autonomously, and the agent that erred should analyze its own failure so the system improves.

### OF-SRC-0013 — Disagreement may itself be the true answer
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 4 question 1
- Interview question: What counts as successful resolution when scholars disagree?
- Owner answer: Resolution does not mean forcing one entity. If scholars genuinely disagree, the engine should record every supported position with evidence because the goal is truth-seeking, not consensus-forcing.

### OQ-SRC-0004 — Formal replacement for human_gate
- Type: question
- Layer: questions
- Step: n/a
- Status: superseded
- Priority: high
- Confidence: medium
- Source: Derived from OF-SRC-0011
- Candidates:
  - OPT-A: Agent-gate module (likely)
  - OPT-B: Confidence threshold resolver (possible)
  - OPT-C: Supervisor veto (possible)

### REQ-SRC-0009 — Agent self-resolution of disagreements
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011; amended per contract-architect-review.yaml, adversary-review.yaml ADV-005/ADV-012, and ChatGPT DR on agent-team architecture (2026-04-14) which specifies the structured round protocol.
- Trigger: Independent agents disagree about a metadata field.
- Postconditions:
  - disagreement_case.resolution_state is set to resolved_error or genuine_scholarly_dispute.
  - resolved_error writes one corrected value and structured failure_analysis for the losing agent.
  - genuine_scholarly_dispute delegates the field to the REQ-SRC-0012 multi-position schema.
  - When disagreement_case.round_count reaches 3 without convergence on resolved_error, disagreement_case.resolution_state defaults to genuine_scholarly_dispute and emits REQ-SRC-0012 output.
  - Each round follows a structured protocol where each verification agent receives the other agent's position and evidence traces, then emits a steelman of the other position, a list of attack points with evidence, at most 2 targeted research requests, and a revised position.
  - Convergence is detected mechanically by the orchestrator when both agents emit the same canonicalized output and the winning position's evidence list is non-empty.
  - When one agent's evidence becomes empty while the other remains evidence-backed, the case resolves as resolved_error rather than genuine_scholarly_dispute.
  - failure_analysis for resolved_error must include error_type, what_missed, corrective_evidence, and guardrail_suggestion fields.
- Acceptance criteria:
  - AC-1 [integration] Given A disagreement where one agent treats "إعداد" as author evidence and another agent corrects it to compiler evidence; When disagreement resolution executes; Then disagreement_case.resolution_state="resolved_error" and the corrected metadata field is stored as a single resolved value..
  - AC-2 [integration] Given A disputed authorship case with two evidence-backed positions from independent agents; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..
  - AC-3 [deterministic] Given A resolved_error case with one losing agent; When disagreement resolution finalizes; Then failure_analysis.agent_id is recorded and linked to disagreement_case.case_id..
  - AC-4 [deterministic] Given A disagreement that remains unresolved after disagreement_case.round_count=3; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..
