# Source Spec Atoms by Status: draft

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| OQ-SRC-0001 | question | Level detection ownership | draft | medium |
| OQ-SRC-0003 | question | Agent-team architecture design | draft | critical |
| OQ-SRC-0004 | question | Formal replacement for human_gate | draft | high |
| OQ-SRC-0005 | question | Agent monitoring scope | draft | medium |
| OQ-SRC-0006 | question | Ordering and display semantics for multi-position metadata | draft | high |
| OQ-SRC-0007 | question | Specialized research source inventory | draft | medium |

### OQ-SRC-0001 — Level detection ownership
- Type: question
- Status: draft
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007
- Candidates:
  - OPT-A: Source metadata only (unlikely)
  - OPT-B: Downstream content analysis (likely)
  - OPT-C: Dual inference with reconciliation (possible)

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

### OQ-SRC-0005 — Agent monitoring scope
- Type: question
- Status: draft
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0009; narrowed per contract-architect-review.yaml
- Candidates:
  - OPT-A: Source-engine monitors (possible)
  - OPT-B: Pipeline-wide monitors (likely)
  - OPT-C: Per-book monitors (unlikely)

### OQ-SRC-0006 — Ordering and display semantics for multi-position metadata
- Type: question
- Status: draft
- Priority: high
- Confidence: medium
- Source: Derived from OF-SRC-0013; narrowed per contract-architect-review.yaml
- Candidates:
  - OPT-A: Preserve input order (possible)
  - OPT-B: Sort by confidence (likely)
  - OPT-C: Weighted display without reordering (possible)

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
