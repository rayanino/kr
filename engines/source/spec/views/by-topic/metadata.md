# Source Spec Atoms by Topic: metadata

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0002 | constraint | Hadith literature dominates source-engine benchmark quality | confirmed | high |
| DEC-SRC-0002 | decision | Science scope uses dynamic registry | proposed | high |
| DEC-SRC-0003 | decision | Level detection strategy | deferred | medium |
| DEC-SRC-0007 | decision | Disputed metadata as multi-position evidence | proposed | high |
| INV-SRC-0002 | invariant | Author attribution is the number one quality metric | proposed | critical |
| INV-SRC-0003 | invariant | Library never refuses knowledge | proposed | critical |
| OF-SRC-0004 | feedback | Author attribution errors are catastrophic | confirmed | critical |
| OF-SRC-0005 | feedback | Science hints follow the same cross-validation rule | confirmed | high |
| OF-SRC-0006 | feedback | Science registry must keep growing | confirmed | high |
| OF-SRC-0007 | feedback | Preserve and infer level metadata from content | confirmed | medium |
| OF-SRC-0008 | feedback | Multi-layer detection ownership is unresolved | confirmed | medium |
| OF-SRC-0012 | feedback | Hadith classification is the primary benchmark surface | confirmed | high |
| OQ-SRC-0001 | question | Level detection ownership | draft | medium |
| OQ-SRC-0002 | question | Multi-layer detection responsibility | draft | medium |
| OQ-SRC-0006 | question | Multi-position metadata representation | draft | high |
| REQ-SRC-0004 | requirement | Multi-model consensus for author attribution | proposed | critical |
| REQ-SRC-0005 | requirement | Optional science hint | proposed | medium |
| REQ-SRC-0006 | requirement | Growable science registry | proposed | high |
| REQ-SRC-0007 | requirement | Level detection from content | deferred | medium |
| REQ-SRC-0010 | requirement | Graduated muhaqiq standing | proposed | medium |
| REQ-SRC-0011 | requirement | Fine-grained hadith classification | proposed | high |
| REQ-SRC-0012 | requirement | Multi-position metadata for disputed fields | proposed | high |

### CON-SRC-0002 — Hadith literature dominates source-engine benchmark quality
- Type: constraint
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012
- Rule: Because 48.7 percent of the collection is hadith literature, hadith classification accuracy is a primary benchmark domain.

### DEC-SRC-0002 — Science scope uses dynamic registry
- Type: decision
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006
- Chosen option: OPT-B — Growable registry with owner confirmation
- Decision rationale: This preserves intake breadth while keeping science-tree expansion human-approved.

### DEC-SRC-0003 — Level detection strategy
- Type: decision
- Status: deferred
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007
- Chosen option: Decision deferred

### DEC-SRC-0007 — Disputed metadata as multi-position evidence
- Type: decision
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013
- Chosen option: OPT-B — Record all positions with evidence
- Decision rationale: This preserves the truth structure the owner asked for and avoids fake certainty.

### INV-SRC-0002 — Author attribution is the number one quality metric
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0004
- Rule: Attribution accuracy outranks every other source-engine quality trade-off.

### INV-SRC-0003 — Library never refuses knowledge
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0006
- Rule: No book is rejected solely because its science is absent from the current registry.

### OF-SRC-0004 — Author attribution errors are catastrophic
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 4
- Interview question: Which metadata failure matters most to the owner?
- Owner answer: Author attribution errors are devastating. If attribution fails, the owner would doubt the whole library. This is the number one quality metric.

### OF-SRC-0005 — Science hints follow the same cross-validation rule
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 2 question 1
- Interview question: Should a science hint influence source inference?
- Owner answer: Science hints are optional and follow the same pattern as author hints. They never bias inference and are used only as post-inference cross-validation.

### OF-SRC-0006 — Science registry must keep growing
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 2 question 2
- Interview question: What happens when a book belongs to a science outside the current registry?
- Owner answer: The library never refuses knowledge. Sciences are a growable registry. New sciences may be added with owner confirmation, and no book is rejected only because its science is absent today.

### OF-SRC-0007 — Preserve and infer level metadata from content
- Type: feedback
- Status: confirmed
- Priority: medium
- Confidence: medium
- Source: Owner interview batch 2 question 3
- Interview question: Is level metadata useful, and how should it be inferred?
- Owner answer: The level field is valuable. The owner recommends detecting it from content analysis rather than relying only on book-level metadata, but the final engine ownership is still unresolved.

### OF-SRC-0008 — Multi-layer detection ownership is unresolved
- Type: feedback
- Status: confirmed
- Priority: medium
- Confidence: low
- Source: Owner interview batch 2 question 4
- Interview question: Should multi-layer detection happen in source or normalization?
- Owner answer: The owner is unsure. He thinks source-level hints that route normalization may be better, but explicitly said he is not confident about the final boundary.

### OF-SRC-0012 — Hadith classification is the primary benchmark surface
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 3 question 4
- Interview question: Which part of the collection should dominate source-engine quality evaluation?
- Owner answer: Hadith is the owner's main focus and represents 48.7% of the collection. Fine-grained classification within hadith literature is therefore very important.

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

### OQ-SRC-0002 — Multi-layer detection responsibility
- Type: question
- Status: draft
- Priority: medium
- Confidence: low
- Source: Derived from OF-SRC-0008
- Candidates:
  - OPT-A: Source detects and routes (possible)
  - OPT-B: Normalization detects from text (possible)
  - OPT-C: Source hints, normalization confirms (likely)

### OQ-SRC-0006 — Multi-position metadata representation
- Type: question
- Status: draft
- Priority: high
- Confidence: medium
- Source: Derived from OF-SRC-0013
- Candidates:
  - OPT-A: Position array (likely)
  - OPT-B: Primary plus alternatives (unlikely)
  - OPT-C: Weighted positions (possible)

### REQ-SRC-0004 — Multi-model consensus for author attribution
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0004
- Trigger: The source engine needs to assign an author to a book.
- Postconditions:
  - Every author claim is verified by two or more independent agents.
  - Disputed authorship yields evidence-backed multiple positions rather than a single forced value.
- Acceptance criteria:
  - AC-1 [integration] Given The 13 source fixtures with known authors.; When Multi-agent attribution runs.; Then The correct author is identified for every fixture..
  - AC-2 [integration] Given A book with a genuinely disputed author.; When Attribution evidence conflicts.; Then The result stores multiple supported author positions with evidence..

### REQ-SRC-0005 — Optional science hint
- Type: requirement
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0005
- Trigger: The owner provides an optional science hint during intake.
- Postconditions:
  - The science hint is used only for post-inference cross-validation.
  - A matching hint increases confidence.
  - A conflicting hint opens investigation without overriding inference.
- Acceptance criteria:
  - AC-1 [deterministic] Given A science hint matches the inferred science.; When Cross-validation runs.; Then Confidence increases and the inferred value remains unchanged..
  - AC-2 [integration] Given A science hint contradicts the inferred science.; When Cross-validation runs.; Then Investigation starts and the hint never overrides the inference..

### REQ-SRC-0006 — Growable science registry
- Type: requirement
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006
- Trigger: A source maps to a science that is not yet in the registry.
- Postconditions:
  - The owner is asked only to confirm the registry expansion.
  - The new science is added with a base tree if confirmed.
  - The source remains eligible for intake regardless of the expansion decision.
- Acceptance criteria:
  - AC-1 [integration] Given A book maps to an existing science.; When Science classification runs.; Then The book is classified normally without a registry-expansion prompt..
  - AC-2 [integration] Given A book maps to a new science.; When Science classification runs.; Then The owner is prompted to confirm registry expansion and the science is added on confirmation..

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

### REQ-SRC-0010 — Graduated muhaqiq standing
- Type: requirement
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0010
- Trigger: The engine researches the muhaqiq for an edition.
- Postconditions:
  - Muhaqiq standing is recorded as informational metadata using graduated levels.
  - Unknown muhaqiqs are explicitly flagged.
  - Muhaqiq standing never rejects or downgrades the source text itself.
- Acceptance criteria:
  - AC-1 [deterministic] Given A muhaqiq with no reliable external footprint.; When Muhaqiq standing is assessed.; Then The standing is recorded as unknown..
  - AC-2 [integration] Given A muhaqiq with some verified scholarly footprint.; When Muhaqiq standing is assessed.; Then The standing is recorded as barely_known or higher..

### REQ-SRC-0011 — Fine-grained hadith classification
- Type: requirement
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012
- Trigger: A source is identified as hadith literature or closely adjacent hadith scholarship.
- Postconditions:
  - Hadith works are classified into fine-grained sub-genres rather than a single bucket.
  - The resulting sub-genre is preserved for downstream taxonomy and evaluation.
- Acceptance criteria:
  - AC-1 [integration] Given A hadith collection and a hadith commentary.; When Hadith classification runs.; Then The two books are assigned different sub-genres..
  - AC-2 [integration] Given A narrator-biography work.; When Hadith classification runs.; Then The work is classified distinctly from a hadith collection..

### REQ-SRC-0012 — Multi-position metadata for disputed fields
- Type: requirement
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013
- Trigger: The engine encounters a metadata field with genuine scholarly disagreement.
- Postconditions:
  - The field stores an array of supported positions with evidence and confidence.
  - The engine does not force a single canonical value when disagreement is real.
- Acceptance criteria:
  - AC-1 [integration] Given A book with disputed authorship.; When Metadata finalization runs.; Then Both supported author positions are recorded with evidence..
