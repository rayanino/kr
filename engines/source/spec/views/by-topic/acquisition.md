# Source Spec Atoms by Topic: acquisition

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0001 | constraint | Shamela HTML is the only production format | confirmed | high |
| DEC-SRC-0001 | decision | Owner hints are cross-validation, not primary data | proposed | critical |
| INV-SRC-0001 | invariant | Owner hints never bias inference | proposed | critical |
| OF-SRC-0001 | feedback | Collection unchanged for source intake | confirmed | high |
| OF-SRC-0002 | feedback | Drop-and-go intake with optional hints | confirmed | critical |
| REQ-SRC-0001 | requirement | Autonomous source acquisition | proposed | critical |
| REQ-SRC-0002 | requirement | Optional owner hints as cross-validation | proposed | high |

### CON-SRC-0001 — Shamela HTML is the only production format
- Type: constraint
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0001
- Rule: The production collection is the existing ~2,519 Shamela HTML books, and no other format is currently in production scope.

### DEC-SRC-0001 — Owner hints are cross-validation, not primary data
- Type: decision
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002
- Chosen option: OPT-B — Hints as cross-validation signals
- Decision rationale: This matches the owner's drop-and-go workflow and preserves inference independence.

### INV-SRC-0001 — Owner hints never bias inference
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002 and OF-SRC-0005
- Rule: Agent inference must complete before any owner hint is compared against the result.

### OF-SRC-0001 — Collection unchanged for source intake
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 1 question 1
- Interview question: What changed about the source collection and intake formats?
- Owner answer: Collection unchanged. The source engine still targets the same ~2,519 Shamela HTML books, with no new production sources added.

### OF-SRC-0002 — Drop-and-go intake with optional hints
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 2
- Interview question: How much manual structure should the owner provide at intake time?
- Owner answer: The owner wants drop-and-go intake. Optional fields such as author or science are allowed as hints only, never as primary data. Matching hints boost confidence; diverging hints trigger investigation.

### REQ-SRC-0001 — Autonomous source acquisition
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002
- Trigger: Owner provides a single file path for source intake.
- Postconditions:
  - SourceMetadata is created for the book.
  - The source bytes are frozen with a SHA-256 digest.
  - The book is registered for downstream handoff.
- Acceptance criteria:
  - AC-1 [integration] Given A valid Shamela HTML file is provided.; When The source engine runs intake.; Then SourceMetadata, freezing, and source registration complete without owner intervention..
  - AC-2 [deterministic] Given A file that is not valid for production intake is provided.; When The source engine validates the input.; Then Intake aborts with the specific error code for the detected failure mode..

### REQ-SRC-0002 — Optional owner hints as cross-validation
- Type: requirement
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0002
- Trigger: The owner provides optional hints such as author or science at intake time.
- Postconditions:
  - Every provided hint is compared against the agent output after inference.
  - Matching hints increase recorded confidence.
  - Mismatching hints trigger an automated investigation record.
- Acceptance criteria:
  - AC-1 [deterministic] Given A hint matches the inferred field.; When Cross-validation runs after inference.; Then The confidence boost is recorded without changing the inferred value..
  - AC-2 [integration] Given A hint contradicts the inferred field.; When Cross-validation runs after inference.; Then Investigation is triggered and both the hint and inference are preserved..
