# Source Spec Atoms by Status: deferred

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0003 | decision | Level detection strategy | deferred | medium |
| OQ-SRC-0001 | question | Level detection ownership | deferred | medium |
| OQ-SRC-0005 | question | Agent monitoring scope | deferred | medium |

### DEC-SRC-0003 — Level detection strategy
- Type: decision
- Status: deferred
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007; amended per contract-architect-review.yaml
- Chosen option: Decision deferred

### OQ-SRC-0001 — Level detection ownership
- Type: question
- Status: deferred
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007
- Candidates:
  - OPT-A: Source metadata only (unlikely)
  - OPT-B: Downstream content analysis (likely)
  - OPT-C: Dual inference with reconciliation (possible)

### OQ-SRC-0005 — Agent monitoring scope
- Type: question
- Status: deferred
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0009; narrowed per contract-architect-review.yaml
- Candidates:
  - OPT-A: Source-engine monitors (possible)
  - OPT-B: Pipeline-wide monitors (likely)
  - OPT-C: Per-book monitors (unlikely)
