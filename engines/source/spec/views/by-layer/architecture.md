# Source Spec Atoms by Layer: architecture

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0001 | decision | Owner hints are cross-validation, not primary data | proposed | critical |
| DEC-SRC-0002 | decision | Science scope uses dynamic registry | proposed | high |
| DEC-SRC-0003 | decision | Level detection strategy | deferred | medium |
| DEC-SRC-0004 | decision | Replace trust algorithm with agent teams | proposed | critical |
| DEC-SRC-0005 | decision | Muhaqiq standing is metadata only | proposed | high |
| DEC-SRC-0006 | decision | Agents resolve disagreements autonomously | proposed | critical |
| DEC-SRC-0007 | decision | Disputed metadata as multi-position evidence | proposed | high |
| DEC-SRC-0008 | decision | Agent infrastructure is built within source-engine scope first | proposed | medium |
| DEC-SRC-0009 | decision | Research strategy uses specialized sources | proposed | high |
| DEC-SRC-0010 | decision | Source hints multi-layer routing and normalization confirms it | proposed | medium |
| DEC-SRC-0011 | decision | Agent self-resolution replaces human_gate | proposed | high |
| DEC-SRC-0012 | decision | Multi-position metadata ordered by confidence | proposed | high |
| DEC-SRC-0014 | decision | Separate raw-upload tracking from official source admission | proposed | critical |
| DEC-SRC-0015 | decision | Normalization consumes a bridge input model, not raw SourceMetadata | proposed | high |

### DEC-SRC-0001 — Owner hints are cross-validation, not primary data
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002
- Chosen option: OPT-B — Hints as cross-validation signals
- Decision rationale: This matches the owner's drop-and-go workflow and preserves inference independence.

### DEC-SRC-0002 — Science scope uses dynamic registry
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006; amended per domain-validator-review.yaml
- Chosen option: OPT-B — Growable ordered science list
- Decision rationale: This preserves intake breadth, supports cross-science books such as ahadith al-ahkam, and keeps expansion approval at the registry layer.

### DEC-SRC-0003 — Level detection strategy
- Type: decision
- Layer: architecture
- Step: n/a
- Status: deferred
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007; amended per contract-architect-review.yaml
- Chosen option: Decision deferred

### DEC-SRC-0004 — Replace trust algorithm with agent teams
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009; amended per both coworker reviews
- Chosen option: OPT-B — Minimum two-verifier trust workflow
- Decision rationale: This matches the owner's trust direction while keeping unresolved team architecture out of the runtime contract.

### DEC-SRC-0005 — Muhaqiq standing is metadata only
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010; amended per domain-validator-review.yaml
- Chosen option: OPT-B — Metadata plus parsing-confidence signal
- Decision rationale: This keeps the owner's non-rejection rule intact while preserving the structural risk signal Gemini flagged for normalization.

### DEC-SRC-0006 — Agents resolve disagreements autonomously
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011
- Chosen option: OPT-B — Agent self-resolution with failure analysis
- Decision rationale: This matches the owner's desire for autonomous resolution plus system learning.

### DEC-SRC-0007 — Disputed metadata as multi-position evidence
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Chosen option: OPT-B — Record all positions in a positions array
- Decision rationale: This keeps disputed metadata truthful and gives REQ-SRC-0012 a stable contract to implement.

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

### DEC-SRC-0010 — Source hints multi-layer routing and normalization confirms it
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Resolved from OQ-SRC-0002 per domain-validator-review.yaml; amended per 2026-04-14 PDF format directive
- Chosen option: OPT-C — Source hints, normalization confirms
- Decision rationale: This gives source enough responsibility to route early across both Shamela and PDF without pretending format-specific hint evidence is authoritative on its own.

### DEC-SRC-0011 — Agent self-resolution replaces human_gate
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Resolves OQ-SRC-0004; derived from OF-SRC-0011 and REQ-SRC-0009
- Chosen option: OPT-B — REQ-SRC-0009 pipeline with multi-position fallback
- Decision rationale: Owner said agents resolve everything. REQ-SRC-0009 already specifies the resolution flow, terminal states, failure analysis, and fallback. Adding a separate module creates unnecessary indirection.

### DEC-SRC-0012 — Multi-position metadata ordered by confidence
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Resolves OQ-SRC-0006; builds on DEC-SRC-0007 and REQ-SRC-0012
- Chosen option: OPT-B — Sort by confidence descending with primary marker
- Decision rationale: Confidence ordering gives downstream engines a natural default (positions[0]) while preserving all scholarly positions. The owner's principle is truth-seeking — all positions stay, but the most-evidenced one is first.

### DEC-SRC-0014 — Separate raw-upload tracking from official source admission
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that uploaded artifacts must not pollute the official source collection before source-engine acceptance.
- Chosen option: OPT-B — Two registries with staged admission
- Decision rationale: This preserves full upload traceability without polluting the official source collection before the source engine genuinely accepts the source.

### DEC-SRC-0015 — Normalization consumes a bridge input model, not raw SourceMetadata
- Type: decision
- Layer: architecture
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Added on 2026-04-14 after contract-auditor review found that the redesigned SourceMetadata surface no longer matches the live normalization boundary.
- Chosen option: OPT-B — Emit a NormalizationInput bridge inside the handoff bundle
- Decision rationale: This preserves source-engine clarity while giving normalization a concrete boundary contract that can evolve independently later.
