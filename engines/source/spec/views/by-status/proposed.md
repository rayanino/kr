# Source Spec Atoms by Status: proposed

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0004 | constraint | Complete SourceMetadata output schema | proposed | critical |
| DEC-SRC-0001 | decision | Owner hints are cross-validation, not primary data | proposed | critical |
| DEC-SRC-0002 | decision | Science scope uses dynamic registry | proposed | high |
| DEC-SRC-0004 | decision | Replace trust algorithm with agent teams | proposed | critical |
| DEC-SRC-0005 | decision | Muhaqiq standing is metadata only | proposed | high |
| DEC-SRC-0006 | decision | Agents resolve disagreements autonomously | proposed | critical |
| DEC-SRC-0007 | decision | Disputed metadata as multi-position evidence | proposed | high |
| DEC-SRC-0008 | decision | Agent infrastructure is built within source-engine scope first | proposed | medium |
| DEC-SRC-0009 | decision | Research strategy uses specialized sources | proposed | high |
| DEC-SRC-0010 | decision | Source hints multi-layer routing and normalization confirms it | proposed | medium |
| INV-SRC-0001 | invariant | Owner hints never bias inference | proposed | critical |
| INV-SRC-0002 | invariant | Author attribution role separation is mandatory | proposed | critical |
| INV-SRC-0003 | invariant | Library never refuses knowledge | proposed | critical |
| INV-SRC-0004 | invariant | Truth-seeking over consensus-forcing | proposed | high |
| INV-SRC-0005 | invariant | Muhaqiq never gates trust decisions | proposed | high |
| INV-SRC-0006 | invariant | Isnad atomic preservation | proposed | high |
| INV-SRC-0007 | invariant | Scholar registry minimum population | proposed | critical |
| INV-SRC-0008 | invariant | OCR output is never silently trusted | proposed | critical |
| REQ-SRC-0001 | requirement | Autonomous source acquisition | proposed | critical |
| REQ-SRC-0002 | requirement | Optional owner hints as cross-validation | proposed | high |
| REQ-SRC-0003 | requirement | Minimal owner review load | proposed | critical |
| REQ-SRC-0004 | requirement | Multi-model consensus for author attribution | proposed | critical |
| REQ-SRC-0005 | requirement | Optional science hint | proposed | medium |
| REQ-SRC-0006 | requirement | Growable science registry | proposed | high |
| REQ-SRC-0007 | requirement | Level field preservation across handoff | proposed | medium |
| REQ-SRC-0008 | requirement | Agent-team trust evaluation | proposed | critical |
| REQ-SRC-0009 | requirement | Agent self-resolution of disagreements | proposed | critical |
| REQ-SRC-0010 | requirement | Graduated muhaqiq standing | proposed | medium |
| REQ-SRC-0011 | requirement | Fine-grained hadith classification | proposed | high |
| REQ-SRC-0012 | requirement | Multi-position metadata for disputed fields | proposed | high |
| REQ-SRC-0013 | requirement | Specialized research agents | proposed | high |
| REQ-SRC-0014 | requirement | Copyist and author disambiguation | proposed | critical |
| REQ-SRC-0015 | requirement | Honorific-aware name matching | proposed | high |
| REQ-SRC-0016 | requirement | Multi-science assignment | proposed | high |
| REQ-SRC-0017 | requirement | Multi-volume directory intake | proposed | critical |
| REQ-SRC-0020 | requirement | Plain text source intake | proposed | medium |
| REQ-SRC-0021 | requirement | PDF format detection and routing | proposed | critical |
| REQ-SRC-0022 | requirement | Arabic OCR quality assessment | proposed | critical |
| REQ-SRC-0023 | requirement | Diacritics preservation from OCR | proposed | critical |
| REQ-SRC-0024 | requirement | PDF page layout detection | proposed | high |

### CON-SRC-0004 — Complete SourceMetadata output schema
- Type: constraint
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-002; amended per 2026-04-14 PDF format directive
- Rule: Every successful intake emits one SourceMetadata record with non-null mandatory fields source_id, source_sha256, frozen_blob_path, registry_entry_id, title_arabic, author_output, genre, science_scope, is_multi_layer, structural_format, trust_decision, volume_count, and intake_timestamp; author_output must always contain status and positions.

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
- Source: Derived from OF-SRC-0006; amended per domain-validator-review.yaml
- Chosen option: OPT-B — Growable ordered science list
- Decision rationale: This preserves intake breadth, supports cross-science books such as ahadith al-ahkam, and keeps expansion approval at the registry layer.

### DEC-SRC-0004 — Replace trust algorithm with agent teams
- Type: decision
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009; amended per both coworker reviews
- Chosen option: OPT-B — Minimum two-verifier trust workflow
- Decision rationale: This matches the owner's trust direction while keeping unresolved team architecture out of the runtime contract.

### DEC-SRC-0005 — Muhaqiq standing is metadata only
- Type: decision
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010; amended per domain-validator-review.yaml
- Chosen option: OPT-B — Metadata plus parsing-confidence signal
- Decision rationale: This keeps the owner's non-rejection rule intact while preserving the structural risk signal Gemini flagged for normalization.

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
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Chosen option: OPT-B — Record all positions in a positions array
- Decision rationale: This keeps disputed metadata truthful and gives REQ-SRC-0012 a stable contract to implement.

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
- Source: Derived from OF-SRC-0016; amended per both coworker reviews
- Chosen option: OPT-B — Canonical specialized source categories
- Decision rationale: This gives REQ-SRC-0013 a stable source-type taxonomy without overcommitting the exact inventory list.

### DEC-SRC-0010 — Source hints multi-layer routing and normalization confirms it
- Type: decision
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Resolved from OQ-SRC-0002 per domain-validator-review.yaml; amended per 2026-04-14 PDF format directive
- Chosen option: OPT-C — Source hints, normalization confirms
- Decision rationale: This gives source enough responsibility to route early across both Shamela and PDF without pretending format-specific hint evidence is authoritative on its own.

### INV-SRC-0001 — Owner hints never bias inference
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002 and OF-SRC-0005; amended per contract-architect-review.yaml
- Rule: Hint comparison may inspect only inferred_metadata.author_name, inferred_metadata.genre, and inferred_metadata.science_scope after base inference finishes.

### INV-SRC-0002 — Author attribution role separation is mandatory
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0004; amended per domain-validator-review.yaml
- Rule: Author attribution must map author markers to author_name, copyist markers to copyist_name, and editor markers to editor_name without cross-populating those fields.

### INV-SRC-0003 — Library never refuses knowledge
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0006
- Rule: No source is rejected solely because its science label is absent from science_registry.

### INV-SRC-0004 — Truth-seeking over consensus-forcing
- Type: invariant
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Rule: A metadata field qualifies as genuine scholarly dispute only when at least two independent agents provide evidence-backed positions for that field.

### INV-SRC-0005 — Muhaqiq never gates trust decisions
- Type: invariant
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010
- Rule: Muhaqiq standing may annotate parsing confidence, but it may never reject a source or block trust_decision finalization.

### INV-SRC-0006 — Isnad atomic preservation
- Type: invariant
- Status: proposed
- Priority: high
- Confidence: high
- Source: Added from domain-validator-review.yaml
- Rule: Transmission formulas حدثنا, أخبرنا, سمعت, and أجاز لي mark isnad chains that must remain in one atomic unit across processing boundaries.

### INV-SRC-0007 — Scholar registry minimum population
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-004
- Rule: scholar_authority.count must be at least 50 before the first pipeline run begins.

### INV-SRC-0008 — OCR output is never silently trusted
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from the 2026-04-14 PDF format directive
- Rule: OCR-extracted text must always carry its source_metadata.ocr_confidence score, and downstream text_fidelity for OCR-derived sources must be bounded by that score.

### REQ-SRC-0001 — Autonomous source acquisition
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002; amended per contract-architect-review.yaml, adversary-review.yaml ADV-001, and 2026-04-14 PDF format directive
- Trigger: Owner submits a single filesystem path for source intake.
- Postconditions:
  - File input writes source_metadata.source_id, source_metadata.source_sha256, source_metadata.frozen_blob_path, source_metadata.registry_entry_id, and source_metadata.source_format.
  - .htm or .html file input sets source_metadata.source_format=shamela_html.
  - .pdf file input sets source_metadata.source_format=pdf_scanned when extracted_text_area_ratio < 0.10 and sets source_metadata.source_format=pdf_text_embedded when extracted_text_area_ratio >= 0.10.
  - .txt file input sets source_metadata.source_format=plain_text.
  - Directory input routes to REQ-SRC-0017 and never emits SRC-E-DIRECTORY-INPUT.
  - The written source_metadata.source_sha256 is linked to source_metadata.registry_entry_id for duplicate detection.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When source engine intake executes; Then source_metadata.source_id is non-empty, source_metadata.source_sha256 is a 64-character SHA-256 hex digest, source_metadata.frozen_blob_path is non-empty, source_metadata.registry_entry_id is non-empty, and source_metadata.source_format="shamela_html"..
  - AC-2 [deterministic] Given Missing path tests/fixtures/shamela_real/does_not_exist/book.htm; When source engine intake executes; Then Intake aborts with error_code=SRC-E-PATH-NOT-FOUND..
  - AC-3 [deterministic] Given Directory path tests/fixtures/shamela_real/11_multi_small; When source engine intake executes; Then The request routes to REQ-SRC-0017 and does not emit error_code=SRC-E-DIRECTORY-INPUT..
  - AC-4 [deterministic] Given A 0-byte HTML file at a valid temporary intake path; When source engine intake executes; Then Intake aborts with error_code=SRC-E-EMPTY-FILE..
  - AC-5 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after the same file has already been frozen once; When source engine intake executes again; Then Intake aborts with error_code=SRC-E-DUPLICATE-INGEST..
  - AC-6 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When source engine intake executes; Then The request routes to REQ-SRC-0021 and source_metadata.source_format="pdf_text_embedded"..
  - AC-7 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt; When source engine intake executes; Then The request routes to REQ-SRC-0020 and source_metadata.source_format="plain_text"..

### REQ-SRC-0002 — Optional owner hints as cross-validation
- Type: requirement
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

### REQ-SRC-0003 — Minimal owner review load
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0003; amended per contract-architect-review.yaml
- Trigger: Metadata inference reaches a case that cannot be finalized automatically.
- Postconditions:
  - Cases with evidence-backed automatic resolution do not create owner_review_case records.
  - Routed cases write owner_review_case with fields route_reason, target_field, evidence_summary, and candidate_positions.
  - Owner review is never requested for reasons outside the approved route_reason taxonomy.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/06_usul/book.htm; When source metadata resolution completes; Then No owner_review_case is written..
  - AC-2 [deterministic] Given A Shamela HTML source whose metadata card, title, and colophon contain no author signal; When source metadata resolution completes; Then owner_review_case.route_reason="zero_author_evidence" and owner_review_case.target_field="author_name"..
  - AC-3 [integration] Given A source classified as mustalah_al_hadith while science_registry lacks that entry; When science classification completes; Then owner_review_case.route_reason="new_science_not_in_registry" and owner_review_case.target_field="science_scope"..

### REQ-SRC-0004 — Multi-model consensus for author attribution
- Type: requirement
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

### REQ-SRC-0006 — Growable science registry
- Type: requirement
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006; amended per both coworker reviews
- Trigger: Science classification yields a science label not present in science_registry.
- Postconditions:
  - Existing science labels classify normally without registry expansion.
  - New science labels write registry_expansion_request with candidate_science and status=pending_owner_confirmation.
  - Owner confirmation adds the new science and updates registry_expansion_request.status=confirmed.
  - Owner decline or defer keeps intake accepted and stores source_metadata.pending_science_label with registry_expansion_request.status set to declined or deferred.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When science classification executes; Then inferred_metadata.science_scope=["fiqh"] and no registry_expansion_request is written..
  - AC-2 [integration] Given A source whose inferred_metadata.science_scope=["mustalah_al_hadith"] while science_registry lacks that label; When science classification executes; Then registry_expansion_request.candidate_science="mustalah_al_hadith" and registry_expansion_request.status="pending_owner_confirmation"..
  - AC-3 [deterministic] Given A pending registry_expansion_request for mustalah_al_hadith that the owner declines; When registry expansion handling executes; Then registry_expansion_request.status="declined", source_metadata.pending_science_label="mustalah_al_hadith", and source admission remains accepted..

### REQ-SRC-0007 — Level field preservation across handoff
- Type: requirement
- Status: proposed
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007; narrowed per contract-architect-review.yaml
- Trigger: The source engine serializes source metadata for downstream handoff.
- Postconditions:
  - The handoff payload always includes the level key.
  - A populated level value is passed through unchanged.
  - An unknown level is serialized as null rather than omitted.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with source_metadata.level="intermediate"; When source-to-normalization handoff serialization executes; Then The serialized payload contains level="intermediate"..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/12_multi_muq/001.htm with source_metadata.level=null; When source-to-normalization handoff serialization executes; Then The serialized payload contains the key level with value null..

### REQ-SRC-0008 — Agent-team trust evaluation
- Type: requirement
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

### REQ-SRC-0017 — Multi-volume directory intake
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-001
- Trigger: Owner submits a directory path containing numbered .htm volume files for intake.
- Postconditions:
  - All numbered volume files are frozen under one source_metadata.source_id and one source_metadata.registry_entry_id.
  - source_metadata.volume_count equals the number of frozen numbered volume files and is at least 2.
  - source_metadata.source_sha256 stores the composite hash of the numbered volume files.
  - source_metadata.frozen_blob_path points to the immutable frozen directory for the shared source_id.
  - When non-numbered .htm files are present, interactive intake prompts for supplementary inclusion and non-interactive intake auto-skips those files while recording supplementary_file_decision.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small; When intake executes; Then All .htm volumes are frozen under one source_metadata.source_id, source_metadata.volume_count=3, and exactly one source_metadata.registry_entry_id is written..
  - AC-2 [deterministic] Given A directory containing only non-numbered .htm files; When intake executes; Then Intake aborts with error_code=SRC-E-EMPTY-DIRECTORY..
  - AC-3 [deterministic] Given A directory containing 001.htm, 002.htm, and appendix.htm while interaction is unavailable; When intake executes; Then source_metadata.volume_count=2 and supplementary_file_decision.mode="auto_skip"..

### REQ-SRC-0020 — Plain text source intake
- Type: requirement
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Added from adversary-review.yaml ADV-011
- Trigger: Owner submits a .txt file path.
- Postconditions:
  - source_metadata.source_id, source_metadata.source_sha256, source_metadata.frozen_blob_path, and source_metadata.registry_entry_id are written from the submitted file bytes.
  - source_metadata.title_arabic equals the first non-empty line of the file.
  - The full file content, including the title line, is passed to metadata inference as plain_text_content.
  - source_metadata.source_sha256 is computed from the submitted .txt file bytes.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt; When intake executes; Then source_metadata.title_arabic="متن الفية ابن مالك فى علم النحو والصرف"..

### REQ-SRC-0021 — PDF format detection and routing
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OWNER_SANITY_CHECK_ANSWERS.md Q10 and the 2026-04-14 PDF format directive
- Trigger: A .pdf file is submitted for intake.
- Postconditions:
  - source_metadata.source_format is set to pdf_scanned when extracted_text_area_ratio < 0.10.
  - source_metadata.source_format is set to pdf_text_embedded when extracted_text_area_ratio >= 0.10.
  - source_metadata.text_extraction_method is set to direct_text_extraction when source_metadata.source_format=pdf_text_embedded.
  - OCR routing is triggered when source_metadata.source_format=pdf_scanned.
  - source_metadata.page_count_physical is set from the PDF page count.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf; When PDF format detection runs; Then source_metadata.source_format="pdf_scanned" and source_metadata.page_count_physical=398..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When PDF format detection runs; Then source_metadata.source_format="pdf_text_embedded", source_metadata.text_extraction_method="direct_text_extraction", and source_metadata.page_count_physical=13..
  - AC-3 [deterministic] Given A corrupted or password-protected PDF at a valid temporary intake path; When PDF format detection runs; Then Intake aborts with error_code=SRC-E-PDF-CORRUPT..

### REQ-SRC-0022 — Arabic OCR quality assessment
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: medium
- Source: Added from the 2026-04-14 PDF format directive and OCR-quality constraints in the task context
- Trigger: A pdf_scanned source has been OCR-processed.
- Postconditions:
  - source_metadata.ocr_confidence is set to a 0.0-1.0 aggregate across counted pages.
  - source_metadata.scan_quality is set to high, medium, or low.
  - ocr_assessment.page_scores preserves one ocr_confidence value per physical page for downstream use.
  - ocr_assessment.low_fidelity_pages lists pages whose page-level ocr_confidence is below 0.5.
- Acceptance criteria:
  - AC-1 [deterministic] Given A 300+ DPI Arabic scholarly scan with clear print on every counted page; When OCR quality assessment runs; Then source_metadata.ocr_confidence > 0.8 and source_metadata.scan_quality="high"..
  - AC-2 [deterministic] Given A blurry low-resolution Arabic scholarly scan with median_page_dpi below 200; When OCR quality assessment runs; Then source_metadata.ocr_confidence < 0.5 and source_metadata.scan_quality="low"..
  - AC-3 [deterministic] Given A decorative title page with no Arabic text in a pdf_scanned source; When OCR quality assessment runs; Then The page is flagged with warning_code=SRC-W-OCR-LOW-ARABIC and excluded from the counted-page aggregate..

### REQ-SRC-0023 — Diacritics preservation from OCR
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: medium
- Source: Added from the 2026-04-14 PDF format directive and .claude/rules/arabic-scholarly-conventions.md
- Trigger: OCR produces Arabic text from a scanned source.
- Postconditions:
  - OCR output preserves diacritical code points in the ranges U+064B-U+0653, U+0656-U+065F, and U+0670 whenever they are detected in the source scan.
  - No Unicode normalization in {NFC, NFD, NFKC, NFKD} is applied to OCR output.
  - source_metadata.diacritic_fidelity is recorded as preserved_diacritic_count divided by expected_diacritic_count when expected_diacritic_count > 0, else 1.0.
- Acceptance criteria:
  - AC-1 [deterministic] Given A scanned OCR test page containing the text "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"; When OCR extracts Arabic text; Then The OCR output preserves the detected diacritics and applies no Unicode normalization..
  - AC-2 [deterministic] Given OCR output compared against a scanned source page with known diacritics; When diacritic assessment runs; Then source_metadata.diacritic_fidelity equals preserved_diacritic_count divided by expected_diacritic_count..

### REQ-SRC-0024 — PDF page layout detection
- Type: requirement
- Status: proposed
- Priority: high
- Confidence: medium
- Source: Added from the 2026-04-14 PDF format directive and PDF layout constraints in the task context
- Trigger: A PDF source is being processed.
- Postconditions:
  - source_metadata.page_layout is set to single_column, dual_column, marginal_notes, or mixed.
  - layout_analysis.main_text_stream and layout_analysis.marginal_text_stream are identified separately when source_metadata.page_layout=marginal_notes.
  - layout_analysis.reading_order is set to rtl_columns when source_metadata.page_layout=dual_column.
- Acceptance criteria:
  - AC-1 [deterministic] Given A PDF page with visible حاشية blocks in the outer margin alongside the main sharh text; When layout detection runs; Then source_metadata.page_layout="marginal_notes"..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When layout detection runs; Then source_metadata.page_layout="single_column"..
