# Source Spec Atoms by Status: proposed

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0004 | constraint | Complete SourceMetadata output schema | proposed | critical |
| CON-SRC-0005 | constraint | Normalization handoff bundle includes a bridge input contract | proposed | high |
| DEC-SRC-0001 | decision | Owner hints are cross-validation, not primary data | proposed | critical |
| DEC-SRC-0002 | decision | Science scope uses dynamic registry | proposed | high |
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
| INV-SRC-0001 | invariant | Owner hints never bias inference | proposed | critical |
| INV-SRC-0002 | invariant | Author attribution role separation is mandatory | proposed | critical |
| INV-SRC-0003 | invariant | Library never refuses knowledge | proposed | critical |
| INV-SRC-0004 | invariant | Truth-seeking over consensus-forcing | proposed | high |
| INV-SRC-0005 | invariant | Muhaqiq never gates trust decisions | proposed | high |
| INV-SRC-0006 | invariant | Isnad atomic preservation | proposed | high |
| INV-SRC-0007 | invariant | Scholar registry minimum population | proposed | critical |
| INV-SRC-0008 | invariant | PDF-derived text is never silently trusted at source handoff | proposed | critical |
| REQ-SRC-0001 | requirement | Upload receipt and raw submission registration | proposed | critical |
| REQ-SRC-0002 | requirement | Optional owner hints as cross-validation | proposed | high |
| REQ-SRC-0003 | requirement | Metadata deliberation stays owner-light | proposed | critical |
| REQ-SRC-0004 | requirement | Multi-model consensus for author attribution | proposed | critical |
| REQ-SRC-0005 | requirement | Optional science hint | proposed | medium |
| REQ-SRC-0006 | requirement | Growable science registry without owner gate | proposed | high |
| REQ-SRC-0007 | requirement | Level field preservation across source-engine handoff | proposed | medium |
| REQ-SRC-0008 | requirement | Agent-team trust evaluation | proposed | critical |
| REQ-SRC-0009 | requirement | Agent self-resolution of disagreements | proposed | critical |
| REQ-SRC-0010 | requirement | Graduated muhaqiq standing | proposed | medium |
| REQ-SRC-0011 | requirement | Fine-grained hadith classification | proposed | high |
| REQ-SRC-0012 | requirement | Multi-position metadata for disputed fields | proposed | high |
| REQ-SRC-0013 | requirement | Specialized research agents | proposed | high |
| REQ-SRC-0014 | requirement | Copyist and author disambiguation | proposed | critical |
| REQ-SRC-0015 | requirement | Honorific-aware name matching | proposed | high |
| REQ-SRC-0016 | requirement | Multi-science assignment | proposed | high |
| REQ-SRC-0017 | requirement | Multipart Shamela container classification | proposed | critical |
| REQ-SRC-0018 | requirement | Freeze and manifest verification | proposed | critical |
| REQ-SRC-0019 | requirement | Intake dossier and source-work identification | proposed | critical |
| REQ-SRC-0020 | requirement | Plain text container classification | proposed | medium |
| REQ-SRC-0021 | requirement | PDF intake analysis and text-layer quality classification | proposed | critical |
| REQ-SRC-0022 | requirement | PDF handoff preserves intake verdicts | proposed | critical |
| REQ-SRC-0023 | requirement | PDF text-layer evidence is diagnostic only | proposed | critical |
| REQ-SRC-0024 | requirement | PDF page-geometry hints for normalization | proposed | high |
| REQ-SRC-0025 | requirement | Two-stage source admission and normalization handoff packaging | proposed | critical |
| REQ-SRC-0026 | requirement | Authoritative work identity and collection linkage output | proposed | critical |

### CON-SRC-0004 — Complete SourceMetadata output schema
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-002; amended per reference/pdf_fixture_observations_2026-04-14.md, owner guidance on 2026-04-14 about exact source/work identification and staged source admission, and the architecture decision that normalization owns text extraction.
- Rule: Every source-engine accepted source emits one SourceMetadata record with non-null mandatory fields source_id, source_sha256, frozen_blob_path, registry_entry_id, title_arabic, author_output, work_output, genre, science_scope, is_multi_layer, structural_format, trust_decision, completeness_status, integrity_status, volume_count, and intake_timestamp; author_output must always contain status and positions.

### CON-SRC-0005 — Normalization handoff bundle includes a bridge input contract
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Added on 2026-04-14 after contract review found that SourceMetadata alone no longer defines a runnable source→normalization boundary in the live repo.
- Rule: Every source-engine accepted source must emit a NormalizationHandoffBundle containing non-null SourceMetadata, NormalizationInput, FrozenMemberManifest, completeness_status, and integrity_status.

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

### INV-SRC-0001 — Owner hints never bias inference
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002 and OF-SRC-0005; amended per contract-architect-review.yaml
- Rule: Hint comparison may inspect only inferred_metadata.author_name, inferred_metadata.genre, and inferred_metadata.science_scope after base inference finishes.

### INV-SRC-0002 — Author attribution role separation is mandatory
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0004; amended per domain-validator-review.yaml
- Rule: Author attribution must map author markers to author_name, copyist markers to copyist_name, and editor markers to editor_name without cross-populating those fields.

### INV-SRC-0003 — Library never refuses knowledge
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0006 and broadened on 2026-04-14 after owner clarification that only structurally invalid uploads should be blocked from the official source flow.
- Rule: No structurally valid source is rejected solely because its science label is absent from science_registry, because its metadata remains disputed, or because its completeness or integrity verdict carries non-fatal flags.

### INV-SRC-0004 — Truth-seeking over consensus-forcing
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Rule: A metadata field qualifies as genuine scholarly dispute only when at least two independent agents provide evidence-backed positions for that field.

### INV-SRC-0005 — Muhaqiq never gates trust decisions
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010
- Rule: Muhaqiq standing may annotate parsing confidence, but it may never reject a source or block trust_decision finalization.

### INV-SRC-0006 — Isnad atomic preservation
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Added from domain-validator-review.yaml
- Rule: Transmission formulas حدثنا, أخبرنا, سمعت, and أجاز لي mark isnad chains that must remain in one atomic unit across processing boundaries.

### INV-SRC-0007 — Scholar registry minimum population
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-004
- Rule: scholar_authority.count must be at least 50 before the first pipeline run begins.

### INV-SRC-0008 — PDF-derived text is never silently trusted at source handoff
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md and the 2026-04-14 architecture decision that normalization owns PDF-to-text conversion
- Rule: No PDF-derived text may be treated as normalized source text by the source engine; every PDF handoff must carry source_metadata.pdf_text_layer_status and source_metadata.normalization_route=pdf_ocr_primary.

### REQ-SRC-0001 — Upload receipt and raw submission registration
- Type: requirement
- Layer: pipeline
- Step: upload_receipt
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002; re-scoped on 2026-04-14 after owner correction that upload, intake analysis, and later source acceptance must be distinct stages.
- Trigger: The owner submits one filesystem path for source-engine processing.
- Postconditions:
  - A raw_upload_record is written with non-null submission_id, submitted_path, submitted_path_kind, intake_mode, and receipt_timestamp.
  - raw_upload_record.status is set to received.
  - Owner hints are preserved as raw_upload_record.owner_hint_payload without being used as primary inference at this step.
  - No source_id, source_sha256, frozen_blob_path, source_metadata, or normalization_handoff_bundle is emitted at this step.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When upload receipt executes; Then raw_upload_record.submission_id is non-empty, raw_upload_record.submitted_path_kind="file", raw_upload_record.status="received", and no source_id field exists in the upload-receipt output..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small; When upload receipt executes; Then raw_upload_record.submitted_path_kind="directory" and raw_upload_record.status="received"..
  - AC-3 [deterministic] Given Missing path tests/fixtures/shamela_real/does_not_exist/book.htm; When upload receipt executes; Then Upload receipt aborts with error_code=SRC-E-PATH-NOT-FOUND..
  - AC-4 [deterministic] Given A 0-byte HTML file at a valid temporary intake path; When upload receipt executes; Then Upload receipt aborts with error_code=SRC-E-EMPTY-FILE..

### REQ-SRC-0002 — Optional owner hints as cross-validation
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0002; amended per contract-architect-review.yaml and adversary-review.yaml ADV-007
- Trigger: The owner submits optional intake hints together with a source path.
- Postconditions:
  - owner_hint_payload values are stored separately from inferred_metadata values.
  - Matching author_name hints may increase author_identification_confidence without changing inferred_metadata.author_name.
  - Matching genre hints may increase genre_confidence without changing inferred_metadata.genre.
  - Matching science_scope hints may increase science_scope_confidence without changing inferred_metadata.science_scope.
  - source_metadata.hint_comparison_results appends one record per compared hint with fields hint_field, hint_value, inferred_value, match, and confidence_delta.
  - Hint contradictions write hint_investigation with fields field, hint_value, inferred_value, status, and opened_reason.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/03_fiqh/book.htm with owner_hint_payload.author_name="عبد الله بن إبراهيم الزاحم"; When post-inference hint comparison executes; Then inferred_metadata.author_name remains "عبد الله بن إبراهيم الزاحم", author_identification_confidence increases, and source_metadata.hint_comparison_results contains a record with hint_field="author_name", hint_value="عبد الله بن إبراهيم الزاحم", inferred_value="عبد الله بن إبراهيم الزاحم", and match=true..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with owner_hint_payload.genre="matn"; When post-inference hint comparison executes; Then hint_investigation.field="genre", hint_investigation.hint_value="matn", inferred_metadata.genre remains "risalah", and source_metadata.hint_comparison_results contains a record with hint_field="genre", hint_value="matn", inferred_value="risalah", and match=false..
  - AC-3 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with owner_hint_payload.publisher="دار الفكر"; When hint payload validation executes; Then The invalid hint key is rejected with error_code=SRC-E-HINT-FIELD and base inference still runs..

### REQ-SRC-0003 — Metadata deliberation stays owner-light
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0003 and tightened on 2026-04-14 to align with the owner rule that metadata should resolve autonomously without human gates.
- Trigger: Metadata deliberation reaches a case that cannot be finalized as one definitive metadata value.
- Postconditions:
  - Metadata cases with evidence-backed automatic resolution do not create owner_review_case records.
  - Zero-author-evidence cases emit author_output.status="insufficient_evidence" rather than opening owner review.
  - Genuine metadata disputes emit the multi-position or insufficient-evidence output required by the relevant metadata contract rather than opening owner review.
  - owner_review_case is not used for metadata finalization inside the source engine.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/06_usul/book.htm; When source metadata resolution completes; Then No owner_review_case is written..
  - AC-2 [deterministic] Given A Shamela HTML source whose metadata card, title, and colophon contain no author signal; When source metadata resolution completes; Then author_output.status="insufficient_evidence" and no owner_review_case is written..
  - AC-3 [deterministic] Given A source with two evidence-backed science positions that remain genuinely disputed after internal resolution; When science classification completes; Then the output preserves the dispute and no owner_review_case is written..

### REQ-SRC-0004 — Multi-model consensus for author attribution
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0004; amended per both coworker reviews and adversary-review.yaml ADV-009
- Trigger: The source engine must assign or preserve author attribution for a source.
- Postconditions:
  - author_output.status is one of definitive, disputed, or insufficient_evidence.
  - Each author_output.positions item contains position, display_name, death_hijri, death_hijri_verification, nisba_tokens, evidence, confidence, and source_agent.
  - A definitive case stores one chosen position, while a disputed case preserves multiple positions instead of forcing a single author.
  - Any death_hijri value supported by only one independent agent is stored with death_hijri_verification=single_model_unverified until a second independent agent confirms the same year.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm and two independent attribution agents; When author attribution executes; Then author_output.status="definitive" and author_output.positions[0].position="عبد الله بن إبراهيم الزاحم"..
  - AC-2 [integration] Given A disputed authorship case with two evidence-backed candidates for the same source; When author attribution executes; Then author_output.status="disputed" and len(author_output.positions) is at least 2..
  - AC-3 [deterministic] Given Candidate authors "أحمد بن تيمية الحراني" (death_hijri=728) and "أحمد بن تيمية" (death_hijri=652) with evidence mentioning الحراني; When author attribution executes; Then The selected position matches death_hijri=728 and nisba_tokens contains "الحراني"..
  - AC-4 [integration] Given A source whose metadata card, title, and colophon provide no author evidence; When author attribution executes with two independent agents; Then author_output.status="insufficient_evidence" and owner_review_case.route_reason="zero_author_evidence"..
  - AC-5 [deterministic] Given An author position whose death_hijri=676 is inferred by exactly one independent attribution agent; When author attribution executes; Then author_output.positions[0].death_hijri=676, author_output.positions[0].death_hijri_verification="single_model_unverified", and the death date remains pending confirmation from a second independent agent..

### REQ-SRC-0005 — Optional science hint
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0005; amended per contract-architect-review.yaml
- Trigger: The owner supplies science_scope as an optional intake hint.
- Postconditions:
  - Exact science_scope matches may increase science_scope_confidence without changing inferred_metadata.science_scope.
  - Contradictions write hint_investigation with field=science_scope and preserve both hint and inference values.
  - Science hints never replace the inferred science_scope list.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/04_hadith/book.htm with owner_hint_payload.science_scope=["hadith"]; When science-hint comparison executes; Then inferred_metadata.science_scope remains ["hadith"] and science_scope_confidence increases..
  - AC-2 [integration] Given tests/fixtures/shamela_real/10_no_author/book.htm with owner_hint_payload.science_scope=["tafsir"]; When science-hint comparison executes; Then hint_investigation.field="science_scope", hint_investigation.hint_value=["tafsir"], and inferred_metadata.science_scope remains ["hadith", "fiqh"]..

### REQ-SRC-0006 — Growable science registry without owner gate
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006; amended on 2026-04-14 to align with the owner rule that metadata should not depend on human gates.
- Trigger: Science classification yields a science label not present in science_registry.
- Postconditions:
  - Existing science labels classify normally without registry expansion.
  - New science labels write registry_expansion_request with candidate_science and status=autonomous_review_pending.
  - Autonomous verification may resolve the candidate science as accepted_new_label, merged_into_existing_label, or insufficient_evidence.
  - Source admission remains accepted while the science expansion workflow is pending or disputed.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When science classification executes; Then inferred_metadata.science_scope=["fiqh"] and no registry_expansion_request is written..
  - AC-2 [integration] Given A source whose inferred_metadata.science_scope=["mustalah_al_hadith"] while science_registry lacks that label; When science classification executes; Then registry_expansion_request.candidate_science="mustalah_al_hadith" and registry_expansion_request.status="autonomous_review_pending"..
  - AC-3 [deterministic] Given A pending registry_expansion_request for mustalah_al_hadith that autonomous review cannot yet settle; When registry expansion handling executes; Then registry_expansion_request.status="insufficient_evidence" and source admission remains accepted_with_flags..

### REQ-SRC-0007 — Level field preservation across source-engine handoff
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: proposed
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007; moved to step 60 on 2026-04-14 because the rule governs handoff packaging rather than metadata deliberation itself.
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - The handoff payload always includes the level key.
  - A populated level value is passed through unchanged.
  - An unknown level is serialized as null rather than omitted.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with SourceMetadata.level="intermediate"; When source-to-normalization handoff packaging executes; Then The serialized payload contains level="intermediate"..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/12_multi_muq/001.htm with SourceMetadata.level=null; When source-to-normalization handoff packaging executes; Then The serialized payload contains the key level with value null..

### REQ-SRC-0008 — Agent-team trust evaluation
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009; amended per both coworker reviews and adversary-review.yaml ADV-003
- Trigger: The engine must emit a trust_decision for a source or metadata claim.
- Postconditions:
  - trust_decision contains decision, trust_path, supporting_agents, and evidence_summary fields.
  - Every run writes monitor_feedback records even when the case follows the fast_track path.
  - Books meeting all fast_track predicates may use trust_path=fast_track instead of full_deliberation.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/05_tafsir/book.htm with definitive author attribution, scholar_authority[author_canonical_id].authority_level="primary", and author_death_hijri=774; When trust evaluation executes; Then trust_decision.trust_path="fast_track" and trust_decision.decision="verified"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When trust evaluation executes; Then trust_decision includes decision, trust_path, supporting_agents, and evidence_summary, and at least one monitor_feedback record is written..
  - AC-3 [deterministic] Given A trust evaluation run with only one verification agent available; When trust evaluation executes; Then Finalization aborts with error_code=SRC-E-TRUST-AGENT-COUNT..
  - AC-4 [deterministic] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre="risalah" or author_death_hijri=null; When trust evaluation executes; Then trust_decision.trust_path="full_deliberation"..

### REQ-SRC-0009 — Agent self-resolution of disagreements
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011; amended per contract-architect-review.yaml and adversary-review.yaml ADV-005, ADV-012
- Trigger: Independent agents disagree about a metadata field.
- Postconditions:
  - disagreement_case.resolution_state is set to resolved_error or genuine_scholarly_dispute.
  - resolved_error writes one corrected value and structured failure_analysis for the losing agent.
  - genuine_scholarly_dispute delegates the field to the REQ-SRC-0012 multi-position schema.
  - When disagreement_case.round_count reaches 3 without convergence on resolved_error, disagreement_case.resolution_state defaults to genuine_scholarly_dispute and emits REQ-SRC-0012 output.
- Acceptance criteria:
  - AC-1 [integration] Given A disagreement where one agent treats "إعداد" as author evidence and another agent corrects it to compiler evidence; When disagreement resolution executes; Then disagreement_case.resolution_state="resolved_error" and the corrected metadata field is stored as a single resolved value..
  - AC-2 [integration] Given A disputed authorship case with two evidence-backed positions from independent agents; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..
  - AC-3 [deterministic] Given A resolved_error case with one losing agent; When disagreement resolution finalizes; Then failure_analysis.agent_id is recorded and linked to disagreement_case.case_id..
  - AC-4 [deterministic] Given A disagreement that remains unresolved after disagreement_case.round_count=3; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..

### REQ-SRC-0010 — Graduated muhaqiq standing
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0010; amended per both coworker reviews
- Trigger: The engine researches the muhaqiq for an edition.
- Postconditions:
  - muhaqiq_assessment stores standing_level, evidence_sources, and last_verified.
  - standing_level is one of unknown, barely_known, known, well_known, or elite.
  - Unknown or low standing never blocks source intake.
- Acceptance criteria:
  - AC-1 [deterministic] Given A muhaqiq research result with zero verified evidence sources; When muhaqiq standing assessment executes; Then muhaqiq_assessment.standing_level="unknown", muhaqiq_assessment.evidence_sources=[], and muhaqiq_assessment.last_verified is populated..
  - AC-2 [deterministic] Given A muhaqiq research result with one verified library_catalog source; When muhaqiq standing assessment executes; Then muhaqiq_assessment.standing_level="barely_known"..
  - AC-3 [deterministic] Given A muhaqiq research result with verified sources from scholarly_database, library_catalog, islamic_reference, and general_web; When muhaqiq standing assessment executes; Then muhaqiq_assessment.standing_level="elite" and len(muhaqiq_assessment.evidence_sources)=4..

### REQ-SRC-0011 — Fine-grained hadith classification
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012; amended per both coworker reviews
- Trigger: A source is identified as hadith literature or adjacent hadith scholarship.
- Postconditions:
  - hadith_subgenre is written for every hadith or hadith-adjacent source.
  - Ambiguous cases preserve candidate_subgenres instead of collapsing to generic hadith_collection.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/04_hadith/book.htm; When hadith classification executes; Then hadith_subgenre="juz"..
  - AC-2 [deterministic] Given A tabaqat/rijal work about hadith narrators; When hadith classification executes; Then hadith_subgenre="tabaqat_rijal" and not "hadith_commentary"..
  - AC-3 [deterministic] Given One collection organized by companion narrator names and one collection organized by fiqh chapters; When hadith classification executes; Then The first source receives hadith_subgenre="musnad" and the second receives hadith_subgenre="sunan"..

### REQ-SRC-0012 — Multi-position metadata for disputed fields
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Trigger: The engine encounters a metadata field with genuine scholarly disagreement.
- Postconditions:
  - disputed_field.positions is an array of objects with keys position, evidence, confidence, and source_agents.
  - Every positions item has confidence between 0.0 and 1.0 and a non-empty evidence list.
  - The engine never forces one canonical value when disputed_field.positions contains two or more evidence-backed items.
- Acceptance criteria:
  - AC-1 [integration] Given A disputed authorship case with supported positions "ابن القيم" and "ابن تيمية"; When metadata finalization executes; Then disputed_field.positions contains two objects and each object includes position, evidence, confidence, and source_agents..
  - AC-2 [deterministic] Given A disputed metadata field with two evidence-backed positions; When metadata finalization executes; Then Every disputed_field.positions[*].confidence is between 0.0 and 1.0 and every disputed_field.positions[*].evidence list is non-empty..

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

### REQ-SRC-0014 — Copyist and author disambiguation
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from domain-validator-review.yaml; amended per adversary-review.yaml ADV-006
- Trigger: Attribution parsing reads a metadata card or colophon with or without role-bearing name signals.
- Postconditions:
  - author_name is populated only from author markers.
  - copyist_name is populated only from copyist markers.
  - editor_name is populated only from editor markers.
  - When no explicit role markers appear in metadata or colophon, metadata_card.author is assigned to author_name by default.
- Acceptance criteria:
  - AC-1 [deterministic] Given Colophon text "كتبه الفقير العبد عبد الله بن محمد"; When attribution parsing executes; Then copyist_name="عبد الله بن محمد" and author_name remains null..
  - AC-2 [deterministic] Given Metadata card text "ألفه محمد بن عبد الوهاب"; When attribution parsing executes; Then author_name="محمد بن عبد الوهاب"..
  - AC-3 [deterministic] Given Metadata card author field "ابن قدامة" with no colophon role markers; When attribution parsing executes; Then author_name="ابن قدامة"..

### REQ-SRC-0015 — Honorific-aware name matching
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: high
- Confidence: high
- Source: Added from domain-validator-review.yaml; amended per adversary-review.yaml ADV-010
- Trigger: Attribution matching compares two Arabic scholar names.
- Postconditions:
  - canonical_match_name excludes stripped honorific tokens and any stripped leading kunya segment.
  - display_name preserves the original honorific-bearing form from the source record.
- Acceptance criteria:
  - AC-1 [deterministic] Given Name forms "الإمام النووي" and "النووي"; When author-name matching executes; Then Both names resolve to the same canonical_match_name="النووي" while display_name preserves the original source form..
  - AC-2 [deterministic] Given Name forms "القاضي عياض" and "عياض"; When author-name matching executes; Then Both names resolve to the same canonical_match_name="عياض" while display_name preserves the original source form..
  - AC-3 [deterministic] Given Name forms "أبو محمد ابن قدامة" and "ابن قدامة"; When author-name matching executes; Then Both names resolve to the same canonical_match_name="ابن قدامة" while display_name preserves the original source form..

### REQ-SRC-0016 — Multi-science assignment
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: high
- Confidence: high
- Source: Added from domain-validator-review.yaml; amended per adversary-review.yaml ADV-008
- Trigger: Science classification detects evidence for more than one science.
- Postconditions:
  - science_scope preserves all supported sciences in dominance order.
  - The dominant science remains science_scope[0].
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/10_no_author/book.htm; When science classification executes; Then science_scope=["hadith", "fiqh"] and science_scope[0]="hadith"..

### REQ-SRC-0017 — Multipart Shamela container classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-001 and tightened on 2026-04-14 to distinguish container classification from freezing and later metadata deliberation.
- Trigger: Container classification receives a frozen directory candidate whose members include .htm files.
- Postconditions:
  - container_classification.container_type is set to shamela_multi_volume_html when the manifest contains at least two numbered .htm members.
  - container_classification.container_type is set to multipart_with_supplementary when the manifest contains one or more numbered .htm members plus supplementary non-numbered .htm members.
  - container_classification.volume_manifest preserves numbered HTML members in integer-stem order.
  - container_classification.supplementary_members preserves non-numbered HTML members separately from numbered volumes.
  - container_classification.normalization_route is set to html_parse_primary.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small; When container classification executes; Then container_classification.container_type="shamela_multi_volume_html", len(container_classification.volume_manifest)=3, and container_classification.normalization_route="html_parse_primary"..
  - AC-2 [deterministic] Given A frozen directory manifest containing only appendix.htm and introduction.htm; When container classification executes; Then Classification aborts with error_code=SRC-E-EMPTY-DIRECTORY..
  - AC-3 [deterministic] Given A frozen directory manifest containing 001.htm and المقدمة.htm; When container classification executes; Then container_classification.container_type="multipart_with_supplementary", container_classification.volume_manifest[0].member_name="001.htm", and container_classification.supplementary_members[0].member_name="المقدمة.htm"..

### REQ-SRC-0018 — Freeze and manifest verification
- Type: requirement
- Layer: pipeline
- Step: freeze_and_manifest
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from reference/archive/v1/source_engine/reference/ABD_INTAKE_SPEC.md and archive freezer/integrity behavior, then adapted to the new raw-upload registry boundary on 2026-04-14.
- Trigger: A raw_upload_record with status=received is promoted into freeze processing.
- Postconditions:
  - A frozen_source record is written with non-null source_id, source_sha256, frozen_blob_path, and freeze_verification_status.
  - frozen_source.frozen_member_manifest records every frozen member with member_name, member_sha256, member_size_bytes, and member_kind.
  - raw_upload_record.status is set to frozen when freeze_verification_status="verified".
  - Exact duplicate detection is evaluated against frozen_source.source_sha256 before later container classification begins.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When freeze and manifest executes; Then frozen_source.source_id is non-empty, frozen_source.source_sha256 is a 64-character SHA-256 hex digest, frozen_source.freeze_verification_status="verified", and len(frozen_source.frozen_member_manifest)=1..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small; When freeze and manifest executes; Then frozen_source.freeze_verification_status="verified" and len(frozen_source.frozen_member_manifest)=3..
  - AC-3 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after the same file has already been frozen once; When freeze and manifest executes again; Then Freezing aborts with error_code=SRC-E-DUPLICATE-INGEST..

### REQ-SRC-0019 — Intake dossier and source-work identification
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from owner correction on 2026-04-14 that source intake must thoroughly analyze what was uploaded, determine exact source/work identity, inspect completeness, and avoid leaving these gaps to later implementation.
- Trigger: Intake analysis receives a frozen, container-classified source candidate.
- Postconditions:
  - An intake_dossier is written with non-null dossier_id, title_evidence, work_identity_proposal, completeness_status, integrity_status, and collection_match_candidates.
  - work_identity_proposal.candidates preserves one or more evidence-backed candidate work identities without declaring them authoritative yet.
  - completeness_status is one of complete, partial, mixed, or indeterminate.
  - integrity_status is one of sound, suspicious, or corrupt.
  - declared_vs_observed_counts preserves any count comparison evidence used by completeness analysis.
  - Metadata deliberation consumes the intake_dossier rather than re-reading raw upload state directly.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When intake analysis executes; Then intake_dossier.dossier_id is non-empty, len(intake_dossier.title_evidence) is at least 1, len(intake_dossier.work_identity_proposal.candidates) is at least 1, and intake_dossier.integrity_status is one of {sound, suspicious, corrupt}..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small; When intake analysis executes; Then intake_dossier.declared_vs_observed_counts.observed_volume_count=3 and intake_dossier.completeness_status is one of {complete, indeterminate}..
  - AC-3 [deterministic] Given A frozen source candidate whose title page and file naming indicate "الجزء الثاني" with no companion parts present; When intake analysis executes; Then intake_dossier.completeness_status="partial" and intake_dossier.partiality_reasons includes "single_part_without_companion_parts"..

### REQ-SRC-0020 — Plain text container classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Added from adversary-review.yaml ADV-011 and narrowed on 2026-04-14 so plain-text handling is classified and routed here, while later text interpretation belongs to later steps.
- Trigger: Container classification receives a frozen single-file candidate whose suffix is .txt.
- Postconditions:
  - container_classification.container_type is set to plain_text.
  - container_classification.normalization_route is set to plain_text_parse.
  - container_classification.text_encoding is set to utf-8.
  - intake analysis may later use the first non-empty line as title evidence, but that evidence is not finalized at this step.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt; When container classification executes; Then container_classification.container_type="plain_text", container_classification.normalization_route="plain_text_parse", and container_classification.text_encoding="utf-8"..

### REQ-SRC-0021 — PDF intake analysis and text-layer quality classification
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OWNER_SANITY_CHECK_ANSWERS.md Q10, reference/pdf_fixture_observations_2026-04-14.md, and owner correction that PDF text-layer judgment belongs to intake analysis and must use text quality, not text presence alone.
- Trigger: Intake analysis runs on a frozen source candidate whose container_type is pdf.
- Postconditions:
  - intake_dossier.source_format is set to pdf.
  - intake_dossier.declared_vs_observed_counts.physical_page_count is set from the PDF page count.
  - intake_dossier.normalization_route is set to pdf_ocr_primary.
  - intake_dossier.pdf_text_layer_status is set to absent when sampled content pages yield no extractable visible text.
  - intake_dossier.pdf_text_layer_status is set to corrupt when sampled pages yield extractable text but the text-layer assessment rejects that text as unusable.
  - intake_dossier.pdf_text_layer_status is set to clean when sampled pages yield extractable text and the text-layer assessment accepts that text as intelligible.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="absent", intake_dossier.normalization_route="pdf_ocr_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=398..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="corrupt", intake_dossier.normalization_route="pdf_ocr_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=13..
  - AC-3 [deterministic] Given A temporary PDF generated during the test run with one Arabic page containing the literal string "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ" as embedded text; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="clean", intake_dossier.normalization_route="pdf_ocr_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=1..
  - AC-4 [deterministic] Given A corrupted or password-protected PDF at a valid temporary intake path; When intake analysis executes; Then Intake analysis aborts with error_code=SRC-E-PDF-CORRUPT..

### REQ-SRC-0022 — PDF handoff preserves intake verdicts
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md and revised on 2026-04-14 so the handoff step propagates intake-analysis verdicts without performing normalization itself.
- Trigger: Source admission and normalization handoff finalize a source whose intake dossier source_format is pdf.
- Postconditions:
  - SourceMetadata.normalization_route is set to pdf_ocr_primary.
  - SourceMetadata.pdf_text_layer_status and SourceMetadata.page_count_physical are copied from the intake dossier.
  - NormalizationInput.source_format_legacy is set from SourceMetadata.source_format and SourceMetadata.pdf_text_layer_status according to the bridge contract.
  - The normalization_handoff_bundle preserves the intake dossier evidence needed to explain the PDF verdict downstream.
  - The source engine emits no normalized_text field for a PDF handoff.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf; When normalization handoff packaging executes; Then SourceMetadata.normalization_route="pdf_ocr_primary", SourceMetadata.pdf_text_layer_status="absent", SourceMetadata.page_count_physical=398, NormalizationInput.source_format_legacy="pdf_scanned", and normalization_handoff_bundle contains no normalized_text field..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When normalization handoff packaging executes; Then SourceMetadata.normalization_route="pdf_ocr_primary", SourceMetadata.pdf_text_layer_status="corrupt", SourceMetadata.page_count_physical=13, NormalizationInput.source_format_legacy="pdf_scanned", and normalization_handoff_bundle contains no normalized_text field..
  - AC-3 [deterministic] Given A temporary PDF generated during the test run with one Arabic page containing clean embedded text; When normalization handoff packaging executes; Then SourceMetadata.normalization_route="pdf_ocr_primary", SourceMetadata.pdf_text_layer_status="clean", NormalizationInput.source_format_legacy="pdf_text", and normalization_handoff_bundle contains no normalized_text field..

### REQ-SRC-0023 — PDF text-layer evidence is diagnostic only
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md, .claude/skills/arabic-text/SKILL.md, and owner cross-validation on 2026-04-14 that normalization owns PDF-to-text conversion
- Trigger: The source engine records sampled direct-extraction evidence from a PDF for text-layer classification.
- Postconditions:
  - intake_dossier.pdf_text_evidence preserves the literal extracted string and its physical page number.
  - No Unicode normalization in {NFC, NFD, NFKC, NFKD} is applied to sampled direct-extraction evidence.
  - Sampled direct-extraction evidence is diagnostic only and is never emitted as normalized handoff text by the source engine.
  - The presence of diacritics inside sampled direct-extraction evidence does not override intake_dossier.pdf_text_layer_status="corrupt" when the text-layer assessment rejects the text as unusable.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/waraqat_usul/waraqat.pdf; When sampled direct-extraction evidence is recorded; Then One preserved sampled string equals "منت الورقات إلماـ احلرمني أيب ادلعايل اجلويين" with its physical page number and intake_dossier.pdf_text_layer_status="corrupt"..
  - AC-2 [deterministic] Given A temporary PDF generated during the test run with one Arabic page containing the literal string "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ" as embedded text; When sampled direct-extraction evidence is recorded; Then One preserved sampled string equals "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", intake_dossier.pdf_text_layer_status="clean", and the handoff contains no normalized_text field..

### REQ-SRC-0024 — PDF page-geometry hints for normalization
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: proposed
- Priority: high
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md and revised on 2026-04-14 after confirming that source-engine PDF handling must stay metadata-first and normalization-owned for text extraction
- Trigger: A PDF source is being processed.
- Postconditions:
  - intake_dossier.page_layout_hint is set to single_column, dual_column, marginal_notes, or mixed when the intake-time geometry is sufficient.
  - layout_analysis.main_text_stream_hint and layout_analysis.marginal_text_stream_hint are identified separately when intake_dossier.page_layout_hint=marginal_notes.
  - layout_analysis.reading_order_hint is set to rtl_columns when intake_dossier.page_layout_hint=dual_column.
  - intake_dossier.page_layout_hint remains optional and non-authoritative until normalization confirms page layout on extracted text.
- Acceptance criteria:
  - AC-1 [deterministic] Given A PDF page with visible حاشية blocks in the outer margin alongside the main sharh text; When layout detection runs; Then intake_dossier.page_layout_hint="marginal_notes"..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When layout detection runs; Then intake_dossier.page_layout_hint="single_column"..

### REQ-SRC-0025 — Two-stage source admission and normalization handoff packaging
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that raw uploads must not pollute the official source collection and that structurally valid but partial sources may still proceed with explicit flags.
- Trigger: Source-engine finalization runs after metadata deliberation completes for a source candidate.
- Postconditions:
  - raw_upload_record.status is set to source_engine_accepted or rejected_at_source based on the source-engine result.
  - The official source_collection is written only when the source engine completes successfully.
  - Structurally valid sources with completeness_status in {partial, mixed, indeterminate} may still enter the source_collection with explicit admission_reason and preserved flags.
  - Structurally invalid uploads do not create source_collection records.
  - normalization_handoff_bundle is written for every source_engine_accepted source and contains SourceMetadata, NormalizationInput, FrozenMemberManifest, and preserved intake_dossier completeness and integrity verdicts.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after successful metadata deliberation; When source admission and normalization handoff packaging execute; Then raw_upload_record.status="source_engine_accepted", exactly one source_collection record is written, and normalization_handoff_bundle.SourceMetadata.registry_entry_id is non-empty..
  - AC-2 [deterministic] Given A structurally valid upload whose intake_dossier.completeness_status="partial"; When source admission and normalization handoff packaging execute; Then one source_collection record is written with admission_reason="accepted_with_flags" and the handoff preserves completeness_status="partial"..
  - AC-3 [deterministic] Given A raw upload rejected earlier with error_code=SRC-E-EMPTY-FILE; When source admission and normalization handoff packaging would otherwise execute; Then no source_collection record is written for that submission..

### REQ-SRC-0026 — Authoritative work identity and collection linkage output
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that the source engine must determine exactly which book/source was uploaded and preserve collection linkage explicitly.
- Trigger: Metadata deliberation finalizes source-engine metadata for a source candidate.
- Postconditions:
  - work_output is written with non-null status and at least one evidence-backed position.
  - work_output.status is one of definitive, disputed, or insufficient_evidence.
  - A definitive case stores one chosen work position, while a disputed case preserves multiple work positions instead of forcing one bibliographic identity.
  - collection_match_output records whether the source matches an existing admitted work, an existing edition group, or no current collection match.
  - title_arabic in SourceMetadata is derived from the chosen or preserved work identity evidence rather than from raw upload naming alone.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with one evidence-backed work candidate; When metadata deliberation executes; Then work_output.status="definitive", len(work_output.positions)=1, and title_arabic is non-empty..
  - AC-2 [deterministic] Given A source candidate whose intake dossier contains two evidence-backed work candidates for the same uploaded source; When metadata deliberation executes; Then work_output.status="disputed" and len(work_output.positions) is at least 2..
  - AC-3 [deterministic] Given A source candidate whose intake dossier contains no evidence-backed work candidate; When metadata deliberation executes; Then work_output.status="insufficient_evidence"..
