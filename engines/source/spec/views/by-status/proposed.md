# Source Spec Atoms by Status: proposed

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0001 | decision | Owner hints are cross-validation, not primary data | proposed | critical |
| DEC-SRC-0002 | decision | Science scope uses dynamic registry | proposed | high |
| DEC-SRC-0004 | decision | Replace trust algorithm with agent teams | proposed | critical |
| DEC-SRC-0005 | decision | Muhaqiq standing is metadata only | proposed | high |
| DEC-SRC-0006 | decision | Agents resolve disagreements autonomously | proposed | critical |
| DEC-SRC-0007 | decision | Disputed metadata as multi-position evidence | proposed | high |
| DEC-SRC-0008 | decision | Agent infrastructure is built within source-engine scope first | proposed | medium |
| DEC-SRC-0009 | decision | Research strategy uses specialized sources | proposed | high |
| INV-SRC-0001 | invariant | Owner hints never bias inference | proposed | critical |
| INV-SRC-0002 | invariant | Author attribution is the number one quality metric | proposed | critical |
| INV-SRC-0003 | invariant | Library never refuses knowledge | proposed | critical |
| INV-SRC-0004 | invariant | Truth-seeking over consensus-forcing | proposed | high |
| INV-SRC-0005 | invariant | Muhaqiq never gates trust decisions | proposed | high |
| REQ-SRC-0001 | requirement | Autonomous source acquisition | proposed | critical |
| REQ-SRC-0002 | requirement | Optional owner hints as cross-validation | proposed | high |
| REQ-SRC-0003 | requirement | Minimal owner review load | proposed | critical |
| REQ-SRC-0004 | requirement | Multi-model consensus for author attribution | proposed | critical |
| REQ-SRC-0005 | requirement | Optional science hint | proposed | medium |
| REQ-SRC-0006 | requirement | Growable science registry | proposed | high |
| REQ-SRC-0008 | requirement | Agent-team trust evaluation | proposed | critical |
| REQ-SRC-0009 | requirement | Agent self-resolution of disagreements | proposed | critical |
| REQ-SRC-0010 | requirement | Graduated muhaqiq standing | proposed | medium |
| REQ-SRC-0011 | requirement | Fine-grained hadith classification | proposed | high |
| REQ-SRC-0012 | requirement | Multi-position metadata for disputed fields | proposed | high |
| REQ-SRC-0013 | requirement | Specialized research agents | proposed | high |

### DEC-SRC-0001 — Owner hints are cross-validation, not primary data
- Type: decision
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002
- Chosen option: OPT-B — Hints as cross-validation signals
- Decision rationale: This matches the owner's drop-and-go workflow and preserves inference independence.

### DEC-SRC-0002 — Science scope uses dynamic registry
- Type: decision
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006
- Chosen option: OPT-B — Growable registry with owner confirmation
- Decision rationale: This preserves intake breadth while keeping science-tree expansion human-approved.

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

### DEC-SRC-0006 — Agents resolve disagreements autonomously
- Type: decision
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011
- Chosen option: OPT-B — Agent self-resolution with failure analysis
- Decision rationale: This matches the owner's desire for autonomous resolution plus system learning.

### DEC-SRC-0007 — Disputed metadata as multi-position evidence
- Type: decision
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013
- Chosen option: OPT-B — Record all positions with evidence
- Decision rationale: This preserves the truth structure the owner asked for and avoids fake certainty.

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

### INV-SRC-0001 — Owner hints never bias inference
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002 and OF-SRC-0005
- Rule: Agent inference must complete before any owner hint is compared against the result.

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

### INV-SRC-0004 — Truth-seeking over consensus-forcing
- Type: invariant
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013
- Rule: When the real answer is that scholars disagree, the engine must record disagreement as the result.

### INV-SRC-0005 — Muhaqiq never gates trust decisions
- Type: invariant
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010
- Rule: Muhaqiq standing is informational metadata and never a trust gate for keeping or rejecting a text.

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

### REQ-SRC-0009 — Agent self-resolution of disagreements
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011
- Trigger: Independent agents disagree about a metadata field.
- Postconditions:
  - Agents resolve the disagreement autonomously without owner intervention.
  - The failing or losing agent emits structured failure analysis for system improvement.
- Acceptance criteria:
  - AC-1 [integration] Given A simulated metadata disagreement.; When The disagreement workflow runs.; Then The agents resolve the case without owner intervention..
  - AC-2 [deterministic] Given An agent loses or retracts its position in disagreement review.; When Resolution completes.; Then That agent produces structured failure analysis linked to the case..

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
