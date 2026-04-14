# Source Spec Atoms by Topic: agent_ergonomics

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0008 | decision | Agent infrastructure is built within source-engine scope first | proposed | medium |
| DEC-SRC-0009 | decision | Research strategy uses specialized sources | proposed | high |
| OF-SRC-0016 | feedback | Research must use specialized source channels | confirmed | high |
| OQ-SRC-0003 | question | Agent-team architecture design | draft | critical |
| OQ-SRC-0005 | question | Agent monitoring scope | deferred | medium |
| OQ-SRC-0007 | question | Specialized research source inventory | draft | medium |
| REQ-SRC-0013 | requirement | Specialized research agents | proposed | high |

### DEC-SRC-0008 — Agent infrastructure is built within source-engine scope first
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0015
- Chosen option: OPT-A — Build within source engine scope first
- Decision rationale: The owner explicitly prioritized building the best possible source-engine scope first.

### DEC-SRC-0009 — Research strategy uses specialized sources
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0016; amended per both coworker reviews
- Chosen option: OPT-B — Canonical specialized source categories
- Decision rationale: This gives REQ-SRC-0013 a stable source-type taxonomy without overcommitting the exact inventory list.

### OF-SRC-0016 — Research must use specialized source channels
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 4 question 4
- Interview question: What kind of research capability does the source engine need?
- Owner answer: Research should be much more accurate than generic web search. Dedicated agents should cover general web, specific scholarly sources, and well-defined reference databases.

### OQ-SRC-0003 — Agent-team architecture design
- Type: question
- Layer: questions
- Step: n/a
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
- Layer: questions
- Step: n/a
- Status: deferred
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0009; narrowed per contract-architect-review.yaml
- Candidates:
  - OPT-A: Source-engine monitors (possible)
  - OPT-B: Pipeline-wide monitors (likely)
  - OPT-C: Per-book monitors (unlikely)

### OQ-SRC-0007 — Specialized research source inventory
- Type: question
- Layer: questions
- Step: n/a
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
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0016; amended per contract-architect-review.yaml
- Trigger: The engine dispatches research work for metadata verification.
- Postconditions:
  - High-impact fields author, genre, science_scope, and death_date use at least two distinct research_task.source_type values.
  - Every dispatch writes verification_log with field, source_types, source_count, and completed_at.
  - Non-high-impact fields may use fewer than two source types.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/08_death_date/book.htm with research_task.field="death_date"; When research dispatch executes; Then verification_log.field="death_date" and len(verification_log.source_types) is at least 2..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/04_hadith/book.htm with research_task.field="author"; When research dispatch executes; Then verification_log.source_types is a subset of {general_web, scholarly_database, manuscript_catalog, islamic_reference, library_catalog}..
  - AC-3 [deterministic] Given A research task with field="author" and only source_type=general_web available; When research dispatch executes; Then verification_log.status="incomplete_specialized_sources"..
