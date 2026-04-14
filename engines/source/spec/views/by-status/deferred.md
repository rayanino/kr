# Source Spec Atoms by Status: deferred

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0003 | decision | Level detection strategy | deferred | medium |
| REQ-SRC-0007 | requirement | Level detection from content | deferred | medium |

### DEC-SRC-0003 — Level detection strategy
- Type: decision
- Status: deferred
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007
- Chosen option: Decision deferred

### REQ-SRC-0007 — Level detection from content
- Type: requirement
- Status: deferred
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007
- Trigger: The source engine needs to preserve or infer a difficulty level for a book.
- Postconditions:
  - The level field is preserved in the source contract.
  - The final detection owner is decided through OQ-SRC-0001 rather than silently guessed in code.
- Acceptance criteria:
  - AC-1 [deterministic] Given A level value is supplied by a later analysis stage.; When Source metadata is handed forward.; Then The level field survives handoff unchanged..
  - AC-2 [deterministic] Given The architecture still has not resolved who computes level.; When The spec is reviewed for implementation readiness.; Then The blocker is recorded against OQ-SRC-0001 instead of being silently implemented..
