# Source Spec Atoms by Topic: trust

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0004 | decision | Replace trust algorithm with agent teams | proposed | critical |
| DEC-SRC-0005 | decision | Muhaqiq standing is metadata only | proposed | high |
| INV-SRC-0005 | invariant | Muhaqiq never gates trust decisions | proposed | high |
| OF-SRC-0003 | feedback | Minimize owner review load | confirmed | critical |
| OF-SRC-0009 | feedback | Replace numeric trust scoring with agent teams | confirmed | critical |
| OF-SRC-0010 | feedback | Muhaqiq standing is informational only | confirmed | high |
| REQ-SRC-0003 | requirement | Minimal owner review load | proposed | critical |
| REQ-SRC-0008 | requirement | Agent-team trust evaluation | proposed | critical |

### DEC-SRC-0004 — Replace trust algorithm with agent teams
- Type: decision
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009
- Chosen option: OPT-B — Agent-team deliberation with supervisors
- Decision rationale: This matches the owner's desired architecture for ambiguity reduction and process supervision.

### DEC-SRC-0005 — Muhaqiq standing is metadata only
- Type: decision
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010
- Chosen option: OPT-B — Informational metadata with graduated levels
- Decision rationale: This preserves useful editorial context while keeping trust decisions focused on the text and evidence.

### INV-SRC-0005 — Muhaqiq never gates trust decisions
- Type: invariant
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010
- Rule: Muhaqiq standing is informational metadata and never a trust gate for keeping or rejecting a text.

### OF-SRC-0003 — Minimize owner review load
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 3
- Interview question: How often should the owner review metadata decisions?
- Owner answer: The owner wants as few reviews as possible. The system should auto-decide aggressively and only send genuinely unresolvable cases to the owner.

### OF-SRC-0009 — Replace numeric trust scoring with agent teams
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 3 question 1
- Interview question: How should trust evaluation work?
- Owner answer: Trust evaluation should be rebuilt around agent teams rather than numeric factors. Two web researchers and two reasoners work under supervisors, supervisors deliberate, and monitor agents provide process-improvement feedback.

### OF-SRC-0010 — Muhaqiq standing is informational only
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 3 question 2
- Interview question: How should muhaqiq reputation affect source evaluation?
- Owner answer: Muhaqiq standing is metadata only. Unknown muhaqiqs should be flagged, and standing can be graduated from unknown to elite, but it must never cause the text to be discarded.

### REQ-SRC-0003 — Minimal owner review load
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0003
- Trigger: The source engine completes metadata inference for a book.
- Postconditions:
  - The system auto-decides clear metadata cases aggressively.
  - Only genuinely unresolvable cases are routed to the owner.
- Acceptance criteria:
  - AC-1 [integration] Given The 13 source fixtures have clear ground truth.; When The source engine runs full metadata inference.; Then Zero owner reviews are triggered for those fixtures..

### REQ-SRC-0008 — Agent-team trust evaluation
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009
- Trigger: The engine needs a trust evaluation for a source or metadata claim.
- Postconditions:
  - Trust is determined by agent-team deliberation rather than a weighted numeric algorithm.
  - Monitor agents emit process-improvement feedback for the run.
- Acceptance criteria:
  - AC-1 [integration] Given The 13 source fixtures require trust evaluation.; When The trust workflow runs.; Then The agent team reaches a trust decision for every fixture..
