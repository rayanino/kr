# Source Spec Atoms by Topic: handoff

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0003 | constraint | No existing pipeline contract is binding on the rebuild | confirmed | critical |
| OF-SRC-0014 | feedback | Legacy contracts do not cap the rebuild | confirmed | critical |
| OF-SRC-0015 | feedback | Build source-engine teams inside the source-engine scope first | confirmed | medium |

### CON-SRC-0003 — No existing pipeline contract is binding on the rebuild
- Type: constraint
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0014
- Rule: The rebuilt source engine designs from first principles and is not capped by archived or legacy cross-engine contracts.

### OF-SRC-0014 — Legacy contracts do not cap the rebuild
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 4 question 2
- Interview question: How much authority do existing pipeline contracts keep during the rebuild?
- Owner answer: All engines will be rebuilt. No existing contract is binding, and the source engine should be engineered to the best possible quality without being capped by old infrastructure.

### OF-SRC-0015 — Build source-engine teams inside the source-engine scope first
- Type: feedback
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Owner interview batch 4 question 3
- Interview question: Where should the first agent infrastructure land?
- Owner answer: The immediate focus is the source engine. The best spec, build, and agent-team design should be created inside source-engine scope first, while reusable questions can be lifted later when downstream engines are built.
