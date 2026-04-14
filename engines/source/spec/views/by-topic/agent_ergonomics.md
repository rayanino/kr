# Source Spec Atoms by Topic: agent_ergonomics

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0008 | decision | Agent infrastructure is built within source-engine scope first | proposed | medium |
| DEC-SRC-0009 | decision | Research strategy uses specialized sources | proposed | high |
| OF-SRC-0016 | feedback | Research must use specialized source channels | confirmed | high |
| OQ-SRC-0003 | question | Agent-team architecture design | draft | critical |
| OQ-SRC-0005 | question | Agent monitoring scope | draft | medium |
| OQ-SRC-0007 | question | Specialized research source inventory | draft | medium |
| REQ-SRC-0013 | requirement | Specialized research agents | proposed | high |

### DEC-SRC-0008 — Agent infrastructure is built within source-engine scope first
- Type: decision
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0015
- Chosen option: OPT-A — Build within source engine scope first
- Decision rationale: The owner explicitly prioritized building the best possible source-engine scope first.

### DEC-SRC-0009 — Research strategy uses specialized sources
- Type: decision
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0016
- Chosen option: OPT-B — Dedicated agents per source type
- Decision rationale: This matches the owner's request for specialized research capability and better evidence quality.

### OF-SRC-0016 — Research must use specialized source channels
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 4 question 4
- Interview question: What kind of research capability does the source engine need?
- Owner answer: Research should be much more accurate than generic web search. Dedicated agents should cover general web, specific scholarly sources, and well-defined reference databases.

### OQ-SRC-0003 — Agent-team architecture design
- Type: question
- Status: draft
- Priority: critical
- Confidence: medium
- Source: Derived from OF-SRC-0009
- Candidates:
  - OPT-A: Fixed roles (likely)
  - OPT-B: Dynamic composition (possible)
  - OPT-C: Hierarchical escalation (possible)

### OQ-SRC-0005 — Agent monitoring scope
- Type: question
- Status: draft
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0009
- Candidates:
  - OPT-A: Source-engine monitors (possible)
  - OPT-B: Pipeline-wide monitors (likely)
  - OPT-C: Per-book monitors (unlikely)

### OQ-SRC-0007 — Specialized research source inventory
- Type: question
- Status: draft
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0016
- Candidates:
  - OPT-A: Web plus Usul.ai (possible)
  - OPT-B: Curated scholarly inventory (likely)
  - OPT-C: Dynamic discovery (unlikely)

### REQ-SRC-0013 — Specialized research agents
- Type: requirement
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0016
- Trigger: The engine dispatches research work for metadata verification.
- Postconditions:
  - Research is routed through dedicated source channels such as general web, scholarly databases, manuscript catalogs, and Islamic reference sites.
  - At least two distinct source types contribute to high-impact verification tasks.
- Acceptance criteria:
  - AC-1 [integration] Given An author-verification task.; When Research dispatch runs.; Then The task uses at least two different research source types..
