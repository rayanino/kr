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
- Rule: The production collection is the existing Shamela HTML library, and no other format is in production scope for source intake.

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
- Source: Derived from OF-SRC-0002 and OF-SRC-0005; amended per contract-architect-review.yaml
- Rule: Hint comparison may inspect only inferred_metadata.author_name, inferred_metadata.genre, and inferred_metadata.science_scope after base inference finishes.

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
- Source: Derived from OF-SRC-0002; amended per contract-architect-review.yaml
- Trigger: Owner submits a single filesystem path for source intake.
- Postconditions:
  - source_metadata.source_sha256 is computed from the submitted file bytes.
  - source_metadata.frozen_blob_path points to the immutable frozen copy of the submitted bytes.
  - source_metadata.registry_entry_id is written and linked to source_metadata.source_sha256.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When source engine intake executes; Then source_metadata.source_sha256 is a 64-character SHA-256 hex digest, source_metadata.frozen_blob_path is non-empty, and source_metadata.registry_entry_id is non-empty..
  - AC-2 [deterministic] Given Missing path tests/fixtures/shamela_real/does_not_exist/book.htm; When source engine intake executes; Then Intake aborts with error_code=SRC-E-PATH-NOT-FOUND..
  - AC-3 [deterministic] Given Directory path tests/fixtures/shamela_real/11_multi_small; When source engine intake executes; Then Intake aborts with error_code=SRC-E-DIRECTORY-INPUT..
  - AC-4 [deterministic] Given A 0-byte HTML file at a valid temporary intake path; When source engine intake executes; Then Intake aborts with error_code=SRC-E-EMPTY-FILE..
  - AC-5 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after the same file has already been frozen once; When source engine intake executes again; Then Intake aborts with error_code=SRC-E-DUPLICATE-INGEST..

### REQ-SRC-0002 — Optional owner hints as cross-validation
- Type: requirement
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0002; amended per contract-architect-review.yaml
- Trigger: The owner submits optional intake hints together with a source path.
- Postconditions:
  - owner_hint_payload values are stored separately from inferred_metadata values.
  - Matching author_name hints may increase author_identification_confidence without changing inferred_metadata.author_name.
  - Matching genre hints may increase genre_confidence without changing inferred_metadata.genre.
  - Matching science_scope hints may increase science_scope_confidence without changing inferred_metadata.science_scope.
  - Hint contradictions write hint_investigation with fields field, hint_value, inferred_value, status, and opened_reason.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/03_fiqh/book.htm with owner_hint_payload.author_name="عبد الله بن إبراهيم الزاحم"; When post-inference hint comparison executes; Then inferred_metadata.author_name remains "عبد الله بن إبراهيم الزاحم" and author_identification_confidence increases..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with owner_hint_payload.genre="matn"; When post-inference hint comparison executes; Then hint_investigation.field="genre", hint_investigation.hint_value="matn", and inferred_metadata.genre remains "risalah"..
  - AC-3 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with owner_hint_payload.publisher="دار الفكر"; When hint payload validation executes; Then The invalid hint key is rejected with error_code=SRC-E-HINT-FIELD and base inference still runs..
