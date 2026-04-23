# Source Spec Atoms by Layer: pipeline

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0001 | requirement | Upload receipt and raw submission registration | confirmed | critical |
| REQ-SRC-0002 | requirement | Optional owner hints as cross-validation | confirmed | high |
| REQ-SRC-0003 | requirement | Metadata deliberation stays owner-light | confirmed | critical |
| REQ-SRC-0004 | requirement | Multi-model consensus for author attribution | confirmed | critical |
| REQ-SRC-0005 | requirement | Optional science hint | confirmed | medium |
| REQ-SRC-0006 | requirement | Growable science registry without owner gate | confirmed | high |
| REQ-SRC-0007 | requirement | Level field preservation across source-engine handoff | confirmed | medium |
| REQ-SRC-0008 | requirement | Agent-team trust evaluation | confirmed | critical |
| REQ-SRC-0009 | requirement | Agent self-resolution of disagreements | confirmed | critical |
| REQ-SRC-0010 | requirement | Graduated muhaqiq standing | confirmed | medium |
| REQ-SRC-0011 | requirement | Fine-grained hadith classification | confirmed | high |
| REQ-SRC-0012 | requirement | Multi-position metadata for disputed fields | confirmed | high |
| REQ-SRC-0013 | requirement | Specialized research agents | confirmed | high |
| REQ-SRC-0014 | requirement | Copyist and author disambiguation | confirmed | critical |
| REQ-SRC-0015 | requirement | Scholar identity matching and name resolution | confirmed | critical |
| REQ-SRC-0016 | requirement | Multi-science assignment | confirmed | high |
| REQ-SRC-0017 | requirement | Multipart Shamela container classification | confirmed | critical |
| REQ-SRC-0018 | requirement | Freeze and manifest verification | confirmed | critical |
| REQ-SRC-0019 | requirement | Source-work identification and collection matching | confirmed | critical |
| REQ-SRC-0020 | requirement | Plain text container classification | confirmed | medium |
| REQ-SRC-0021 | requirement | PDF intake analysis and text-layer quality classification | confirmed | critical |
| REQ-SRC-0022 | requirement | PDF handoff preserves intake verdicts | confirmed | critical |
| REQ-SRC-0023 | requirement | PDF text-layer evidence is diagnostic only | confirmed | critical |
| REQ-SRC-0024 | requirement | PDF page-geometry hints for normalization | confirmed | high |
| REQ-SRC-0025 | requirement | Two-stage source admission and normalization handoff packaging | confirmed | critical |
| REQ-SRC-0026 | requirement | Authoritative work identity and collection linkage output | confirmed | critical |
| REQ-SRC-0027 | requirement | Owner-submission risk gate for study-quality threats | confirmed | critical |
| REQ-SRC-0028 | requirement | Case complexity assessment and deliberation routing | confirmed | critical |
| REQ-SRC-0029 | requirement | Monitor feedback with non-recursive constraint | confirmed | high |
| REQ-SRC-0030 | requirement | Genre classification | confirmed | critical |
| REQ-SRC-0031 | requirement | Multi-layer hint detection | confirmed | critical |
| REQ-SRC-0032 | requirement | Structural format classification | confirmed | critical |
| REQ-SRC-0033 | requirement | Volume count and intake timestamp derivation | confirmed | high |
| REQ-SRC-0034 | requirement | Compiler-as-muhaqiq detection | confirmed | critical |
| REQ-SRC-0035 | requirement | Display metadata for teaching units (source card) | confirmed | high |
| REQ-SRC-0036 | requirement | Completeness analysis of frozen source candidate | confirmed | critical |
| REQ-SRC-0037 | requirement | Integrity analysis of frozen source candidate | confirmed | critical |
| REQ-SRC-0038 | requirement | Composite work (majmu‘) detection and decomposition | confirmed | critical |
| REQ-SRC-0039 | requirement | Work-to-work relationship modeling | confirmed | high |
| REQ-SRC-0040 | requirement | Attribution confidence levels with scholarly terminology | confirmed | high |
| REQ-SRC-0041 | requirement | Format-agnostic multi-volume folder classification | confirmed | critical |
| REQ-SRC-0042 | requirement | Scholar profile lookup for display card | confirmed | high |
| REQ-SRC-0043 | requirement | New scholar registration in authority registry | confirmed | high |
| REQ-SRC-0044 | requirement | Edition-group and holding reconciliation on source admission | confirmed | critical |
| REQ-SRC-0045 | requirement | Supersession signal emission on source admission | confirmed | high |
| REQ-SRC-0046 | requirement | Evidence preservation for downstream level inference | confirmed | critical |
| REQ-SRC-0047 | requirement | Owner override pathway for level at intake | confirmed | medium |
| REQ-SRC-0048 | requirement | Deferred validation surface for owner_level_override | confirmed | medium |

### REQ-SRC-0001 — Upload receipt and raw submission registration
- Type: requirement
- Layer: pipeline
- Step: upload_receipt
- Status: confirmed
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
- Status: confirmed
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
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0003 and tightened on 2026-04-14 to align with the owner rule that metadata should resolve autonomously without human gates.
- Trigger: Metadata deliberation reaches a case that cannot be finalized as one definitive metadata value.
- Postconditions:
  - Metadata cases with evidence-backed automatic resolution do not create owner_review_case records.
  - Zero-author-evidence cases emit author_output.status="insufficient_evidence" rather than opening owner review.
  - Genuine metadata disputes emit the multi-position or insufficient-evidence output required by the relevant metadata contract rather than opening owner review.
  - owner_review_case is not used for metadata finalization inside the source engine.
  - This rule does not prohibit the later owner_submission_risk_gate, because that gate addresses mistaken or materially risky submissions rather than metadata disagreement.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/06_usul/book.htm; When source metadata resolution completes; Then No owner_review_case is written..
  - AC-2 [deterministic] Given A Shamela HTML source whose metadata card, title, and colophon contain no author signal; When source metadata resolution completes; Then author_output.status="insufficient_evidence" and no owner_review_case is written..
  - AC-3 [deterministic] Given A source with two evidence-backed science positions that remain genuinely disputed after internal resolution; When science classification completes; Then the output preserves the dispute and no owner_review_case is written..

### REQ-SRC-0004 — Multi-model consensus for author attribution
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0004; amended per coworker reviews, adversary-review ADV-009, and author-attribution review (ADV-ATT-005/007/011/012). Status values renamed to avoid collision with REQ-SRC-0040 scholarly terminology. Death date verification enum completed. Co-authorship status added. Correlated hallucination guard for modern scholars.
- Trigger: The source engine must assign or preserve author attribution for a source.
- Postconditions:
  - author_output.status is one of: agent_consensus (agents agree on one author), agent_disagreement (agents disagree — multiple positions preserved), agent_no_evidence (no evidence-backed position from any agent), or co_authored (multiple authors genuinely co-wrote the work, indicated by conjunctive markers like و between names or تأليف X و Y).
  - Each author_output.positions item contains position, display_name, death_hijri, death_hijri_verification, nisba_tokens, evidence, confidence, source_agent, and entity_type (person or institution).
  - An agent_consensus case stores one chosen position. An agent_disagreement case preserves all evidence-backed positions. A co_authored case lists all co-authors as non-competing positions.
  - death_hijri_verification enum: single_model_unverified (one agent only), multi_agent_agreed (two+ agents agree), database_verified (confirmed from structured database like Dorar.net or OpenITI), colophon_extracted (directly from source colophon text).
  - Correlated hallucination guard: for scholars with death_hijri > 1300, two-LLM agreement alone is insufficient. Death dates for modern scholars MUST be verified against at least one structured database (Dorar.net API, OpenITI, Shamela metadata). When no database confirms, death_hijri_verification is set to consensus_unverified (a level between single_model_unverified and database_verified).
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm and two independent attribution agents; When author attribution executes; Then author_output.status="agent_consensus" and author_output.positions[0].position="عبد الله بن إبراهيم الزاحم"..
  - AC-2 [integration] Given A disputed authorship case with two evidence-backed candidates for the same source; When author attribution executes; Then author_output.status="agent_disagreement" and len(author_output.positions) is at least 2..
  - AC-3 [deterministic] Given Candidate authors "أحمد بن عبد الحليم بن تيمية الحراني" (death_hijri=728) and "عبد السلام بن عبد الله بن تيمية" (death_hijri=652) with evidence mentioning الحراني and post-700H content; When author attribution executes; Then The selected position matches death_hijri=728 and nisba_tokens contains "الحراني"..
  - AC-4 [integration] Given A source whose metadata card, title, and colophon provide no author evidence; When author attribution executes with two independent agents; Then author_output.status="agent_no_evidence" and study_quality_risk_flags includes "zero_author_evidence"..
  - AC-5 [deterministic] Given An author position whose death_hijri=676 is inferred by exactly one independent attribution agent; When author attribution executes; Then author_output.positions[0].death_hijri=676, author_output.positions[0].death_hijri_verification="single_model_unverified", and the death date remains pending confirmation from a second independent agent..

### REQ-SRC-0005 — Optional science hint
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
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
- Status: confirmed
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
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0007; moved to step 60 on 2026-04-14 because the rule governs handoff packaging rather than metadata deliberation itself. Amended on 2026-04-16 per dr-chatgpt-level-detection-20260416.yaml (SEC-5). Further amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) explicit precondition that owner_level_override passed the CON-SRC-0011 enum-value whitelist before reaching handoff packaging; (b) new level_status (CON-SRC-0004 middle-path) must serialize alongside level — preservation contract extends to both fields. Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-1 (intermediate → mutawassiṭ), AC-3 (advanced → muntahī), and AC-5 (beginner → mubtadiʾ) in the CON-SRC-0011 classical WorkLevel vocabulary. Behaviour, preconditions, postconditions, and error conditions unchanged; the Phase-5a reviewer wave identified the English placeholders as structurally untestable because REQ-SRC-0047 now rejects them at intake against the enum whitelist. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the synchronized `pending_taxonomy` → `pending_synthesis` rename across the level_status enum (four verbatim occurrences in preconditions, AC-2, AC-5). Behaviour unchanged; rename follows the 3-of-3 UNANIMOUS_OWN_SYNTHESIS verdict on CON-SRC-0004.
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - The handoff payload always includes the level key.
  - The handoff payload always includes the level_status key with a non-null enum value.
  - A populated level value is passed through unchanged.
  - An unknown level is serialized as null rather than omitted, paired with a non-null level_status.
  - A level value populated via owner_level_override is passed through unchanged with the same string value received at intake, paired with level_status="assigned".
  - The level_status value is passed through unchanged — handoff packaging never rewrites, defaults, or reinterprets it.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with SourceMetadata.level="mutawassiṭ" and level_status="assigned" (populated via valid owner_level_override, the classical pedagogical CON-SRC-0011 WorkLevel value equivalent to intermediate); When source-to-normalization handoff packaging executes; Then The serialized payload contains level="mutawassiṭ" and level_status="assigned", both unchanged from the upstream emission. The level value serializes as the exact CON-SRC-0011 enum string — no coercion, no translation, no case folding..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/12_multi_muq/001.htm with SourceMetadata.level=null and level_status="pending_synthesis"; When source-to-normalization handoff packaging executes; Then The serialized payload contains the key level with value null AND the key level_status with value "pending_synthesis", both present and neither omitted..
  - AC-3 [deterministic] Given A source whose SourceMetadata.level was populated via owner_level_override="muntahī" at intake (validated against CON-SRC-0011 WorkLevel whitelist per REQ-SRC-0047 AC-1 — the classical pedagogical WorkLevel value for the terminal / curriculum-completing student, the enum position that the earlier English placeholder "advanced" mapped to), with level_status="assigned"; When source-to-normalization handoff packaging executes; Then The serialized payload contains level="muntahī" with the override value unchanged and level_status="assigned" unchanged..
  - AC-4 [deterministic] Given A source with genre="mushaf" (non-applicable per INV-SRC-0012), SourceMetadata.level=null, level_status="non_applicable_reference"; When source-to-normalization handoff packaging executes; Then The serialized payload contains level=null and level_status="non_applicable_reference"..
  - AC-5 [deterministic] Given A handoff packaging path that would have emitted level="mubtadiʾ" (a valid CON-SRC-0011 WorkLevel string — the classical pedagogical label for pre-malakah beginner) with level_status="pending_synthesis" — a cross-field invariant violation per CON-SRC-0004 because a populated level requires level_status="assigned"; When handoff packaging executes; Then Packaging is rejected with SRC-E-LEVEL-STATUS-INVARIANT-VIOLATION and no partial bundle is emitted. The error surfaces the cross- field rule (populated level requires assigned status), not a validation error on the WorkLevel string itself — the level value is a valid CON-SRC-0011 enum member..

### REQ-SRC-0008 — Agent-team trust evaluation
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009; amended per both coworker reviews, adversary-review.yaml ADV-003, and ChatGPT DR on agent-team architecture (2026-04-14) which recommends extending trust_decision to support disputed status with positions array.
- Trigger: The engine must emit a trust_decision for a source or metadata claim.
- Postconditions:
  - trust_decision contains decision, trust_path, supporting_agents, and evidence_summary fields.
  - trust_decision.decision is one of verified, needs_review, or disputed.
  - trust_decision.decision=disputed is set when independent trust verifiers produce evidence-backed competing trust assessments that do not converge after the disagreement protocol. In this case trust_decision.positions preserves both assessments with evidence and confidence, ordered by confidence descending.
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
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011; amended per contract-architect-review.yaml, adversary-review.yaml ADV-005/ADV-012, and ChatGPT DR on agent-team architecture (2026-04-14) which specifies the structured round protocol.
- Trigger: Independent agents disagree about a metadata field.
- Postconditions:
  - disagreement_case.resolution_state is set to resolved_error or genuine_scholarly_dispute.
  - resolved_error writes one corrected value and structured failure_analysis for the losing agent.
  - genuine_scholarly_dispute delegates the field to the REQ-SRC-0012 multi-position schema.
  - When disagreement_case.round_count reaches 3 without convergence on resolved_error, disagreement_case.resolution_state defaults to genuine_scholarly_dispute and emits REQ-SRC-0012 output.
  - Each round follows a structured protocol where each verification agent receives the other agent's position and evidence traces, then emits a steelman of the other position, a list of attack points with evidence, at most 2 targeted research requests, and a revised position.
  - Convergence is detected mechanically by the orchestrator when both agents emit the same canonicalized output and the winning position's evidence list is non-empty.
  - When one agent's evidence becomes empty while the other remains evidence-backed, the case resolves as resolved_error rather than genuine_scholarly_dispute.
  - failure_analysis for resolved_error must include error_type, what_missed, corrective_evidence, and guardrail_suggestion fields.
- Acceptance criteria:
  - AC-1 [integration] Given A disagreement where one agent treats "إعداد" as author evidence and another agent corrects it to compiler evidence; When disagreement resolution executes; Then disagreement_case.resolution_state="resolved_error" and the corrected metadata field is stored as a single resolved value..
  - AC-2 [integration] Given A disputed authorship case with two evidence-backed positions from independent agents; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..
  - AC-3 [deterministic] Given A resolved_error case with one losing agent; When disagreement resolution finalizes; Then failure_analysis.agent_id is recorded and linked to disagreement_case.case_id..
  - AC-4 [deterministic] Given A disagreement that remains unresolved after disagreement_case.round_count=3; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..

### REQ-SRC-0010 — Graduated muhaqiq standing
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
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
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012; amended per both coworker reviews and domain-validator-review-2 (DV-001, DV-016) which found 6 missing hadith subgenres and clarified genre/subgenre orthogonality.
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
- Status: confirmed
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
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0016; amended per contract-architect-review.yaml and Gemini DR on Islamic scholarly metadata verification sources (2026-04-14) which provides a concrete curated inventory per source_type category.
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
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from domain-validator-review.yaml; amended per adversary-review.yaml ADV-006 and Claude DR spec audit 2026-04-15 which identified إعداد as a distinct role (neither author nor editor).
- Trigger: Attribution parsing reads a metadata card or colophon with or without role-bearing name signals.
- Postconditions:
  - author_name is populated only from author markers.
  - compiler_name is populated only from compiler markers.
  - preparer_name is populated only from preparer markers.
  - copyist_name is populated only from copyist markers.
  - editor_name is populated only from editor markers.
  - When no explicit role markers appear in metadata or colophon, metadata_card.author is assigned to author_name by default.
  - confirmed_dual_role mechanical criteria: the same name in both author and editor roles is set to confirmed_dual_role (not attribution_role_conflict) when at least one of: (a) title page explicitly states تأليف وتحقيق or a combined formula, (b) temporal impossibility of being different people (same death_hijri for both roles), (c) research agent confirms the scholar is known to self-edit their own works.
- Acceptance criteria:
  - AC-1 [deterministic] Given Colophon text "كتبه الفقير العبد عبد الله بن محمد"; When attribution parsing executes; Then copyist_name="عبد الله بن محمد" and author_name remains null..
  - AC-2 [deterministic] Given Metadata card text "ألفه محمد بن عبد الوهاب"; When attribution parsing executes; Then author_name="محمد بن عبد الوهاب"..
  - AC-3 [deterministic] Given Metadata card author field "ابن قدامة" with no colophon role markers; When attribution parsing executes; Then author_name="ابن قدامة"..

### REQ-SRC-0015 — Scholar identity matching and name resolution
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from domain-validator-review.yaml; amended per adversary-review.yaml ADV-010, adversary-attribution review (ADV-ATT-001/002/006/012), domain-attribution review (laqab-as-primary, nisba, sahib convention, death date tolerance, female scholars), and contract-attribution review (display_name precedence).
- Trigger: Attribution matching compares two Arabic scholar names or resolves a scholar identity.
- Postconditions:
  - canonical_match_name excludes stripped honorific tokens and any stripped leading kunya segment.
  - display_name preserves the original honorific-bearing form from the source record.
  - display_name selection rule: when multiple sources provide different valid forms, display_name defaults to the shortest commonly recognized form (الشهرة). full_name_lineage always stores the longest unabridged form. Disagreement on display_name form (not identity) is NOT a substantive disagreement and must not trigger disagreement resolution.
  - Structured name decomposition: agents output ism, nasab, kunya, laqab, nisba, death_hijri, and laqab_is_primary_identifier (boolean). When laqab_is_primary_identifier=true (e.g., سيبويه, الجاحظ, المبرد, البخاري, النووي), matching treats the laqab as the primary match key.
  - Name-equivalence with death dates: two names refer to the same scholar when death_hijri values match within a tolerance of ±5 Hijri years AND the shorter name's tokens are a strict subset of the longer name's tokens after stripping.
  - Name-equivalence without death dates: when death_hijri is null for BOTH names, strict token-subset matching alone is sufficient to declare equivalence, provided the shorter name's tokens are a strict subset of the longer name's tokens. This prevents cosmetic name-form differences from triggering disagreement resolution.
  - Disambiguation when canonical_match_name is identical and death_hijri is absent for both: the system MUST use secondary signals — science_scope of the work, specialized nisba tokens (المفسر vs المقرئ), and content-derived evidence. When no signal disambiguates, emit SRC-W-AMBIGUOUS-SCHOLAR-IDENTITY and set author_output.status=agent_disagreement with both candidates as positions.
  - The صاحب convention: 'صاحب [work_title]' (e.g., صاحب فتح الباري = Ibn Hajar, صاحب المغني = Ibn Qudama) is resolved via work-to-author lookup using REQ-SRC-0039 work_relationships, not name decomposition. This is a downstream citation resolution pattern; at the source-engine level it applies only when the صاحب formula appears in the metadata card or colophon attribution.
- Acceptance criteria:
  - AC-1 [deterministic] Given Name forms "الإمام النووي" and "النووي" with death_hijri=676 for both; When author-name matching executes; Then Both resolve to the same scholar. display_name preserves original form..
  - AC-2 [deterministic] Given Name forms "أبو محمد ابن قدامة" and "ابن قدامة" with death_hijri=620 for both; When author-name matching executes; Then Both resolve to the same scholar via token-subset + death_hijri match..
  - AC-3 [deterministic] Given Name forms "يحيى بن شرف النووي" (death_hijri=null) and "النووي" (death_hijri=null); When author-name matching executes; Then Both resolve to the same scholar via strict token-subset matching without death_hijri (null-null case)..
  - AC-4 [deterministic] Given Name forms "ابن كثير" (death_hijri=null) from a tafsir source and "ابن كثير" (death_hijri=null) from a qira'at source; When author-name matching executes; Then The system uses science_scope to disambiguate. SRC-W-AMBIGUOUS-SCHOLAR-IDENTITY is emitted if science_scope is unavailable..
  - AC-5 [deterministic] Given Name "سيبويه" with laqab_is_primary_identifier=true and name "عمرو بن عثمان بن قنبر" with death_hijri=180 for both; When author-name matching executes; Then Both resolve to the same scholar because laqab_is_primary_identifier allows laqab-to-ism matching..
  - AC-6 [deterministic] Given Name "أبو هريرة" (recognized kunya-only scholar); When kunya stripping executes; Then canonical_match_name="أبو هريرة" preserved as atomic unit. Kunya is NOT stripped..
  - AC-7 [deterministic] Given Name "لجنة الإفتاء الدائمة" with entity_type=institution; When name matching executes; Then entity_type=institution, canonical_match_name="لجنة الإفتاء الدائمة", no structured decomposition attempted..
  - AC-8 [deterministic] Given Name "كريمة بنت أحمد المروزية"; When name decomposition executes; Then بنت is recognized as patronymic connector, nasab correctly parsed..
  - AC-9 [deterministic] Given Death dates 256 and 252 for the same scholar البخاري from different databases; When death date comparison executes; Then Dates match within ±5 year tolerance. Scholar is NOT split into two records..

### REQ-SRC-0016 — Multi-science assignment
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
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
- Status: confirmed
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
- Status: confirmed
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

### REQ-SRC-0019 — Source-work identification and collection matching
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner correction on 2026-04-14. Narrowed to source-work identification and collection matching after contract-architect review found 4 sub-analyses in one atom is untestable. Completeness analysis moved to REQ-SRC-0036, integrity analysis moved to REQ-SRC-0037.
- Trigger: Intake analysis receives a frozen, container-classified source candidate.
- Postconditions:
  - An intake_dossier is written with non-null dossier_id, title_evidence, work_identity_proposal, and collection_match_candidates.
  - work_identity_proposal.candidates preserves one or more evidence-backed candidate work identities without declaring them authoritative yet.
  - collection_match_candidates records whether the work matches an existing admitted source, an edition group, or has no match.
  - title_evidence preserves all title signals (metadata card title, title page text, colophon title, filename-derived title) with provenance per INV-SRC-0009.
  - Completeness analysis is handled by REQ-SRC-0036. Integrity analysis is handled by REQ-SRC-0037. Metadata deliberation consumes the combined intake_dossier from all three sub-analyses.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When source-work identification executes; Then intake_dossier.dossier_id is non-empty, len(intake_dossier.title_evidence) >= 1, len(intake_dossier.work_identity_proposal.candidates) >= 1..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small; When source-work identification executes; Then len(intake_dossier.work_identity_proposal.candidates) >= 1 and collection_match_candidates is present..

### REQ-SRC-0020 — Plain text container classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: confirmed
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
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OWNER_SANITY_CHECK_ANSWERS.md Q10, reference/pdf_fixture_observations_2026-04-14.md, owner correction on text quality, and pdf_collection_characterization_2026-04-14.md which found 10/10 sampled PDFs use Unicode Presentation Forms (not scans), recoverable via NFKC normalization.
- Trigger: Intake analysis runs on a frozen source candidate whose container_type is pdf.
- Postconditions:
  - intake_dossier.source_format is set to pdf.
  - intake_dossier.declared_vs_observed_counts.physical_page_count is set from the PDF page count.
  - intake_dossier.pdf_text_layer_status is set to absent when sampled content pages yield no extractable visible text.
  - intake_dossier.pdf_text_layer_status is set to corrupt when sampled pages yield extractable text but the text-layer assessment rejects that text as unusable even after NFKC normalization.
  - intake_dossier.pdf_text_layer_status is set to presentation_forms when sampled pages yield text in Unicode Presentation Forms (U+FB50-FDFF, U+FE70-FEFF) that becomes intelligible standard Arabic after NFKC normalization.
  - intake_dossier.pdf_text_layer_status is set to clean when sampled pages yield extractable text already in standard Arabic (U+0600-06FF) that is intelligible without normalization.
  - intake_dossier.normalization_route is set to pdf_ocr_primary when pdf_text_layer_status in {absent, corrupt}. intake_dossier.normalization_route is set to pdf_text_primary when pdf_text_layer_status in {presentation_forms, clean}.
  - intake_dossier.pdf_text_encoding records the detected Unicode block profile: standard_arabic, presentation_forms, or mixed. This signals normalization whether NFKC is needed at the extraction boundary.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="absent", intake_dossier.normalization_route="pdf_ocr_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=398..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="corrupt", intake_dossier.normalization_route="pdf_ocr_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=13..
  - AC-3 [deterministic] Given A temporary PDF generated during the test run with one Arabic page containing the literal string "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ" as embedded text; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="clean", intake_dossier.normalization_route="pdf_text_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=1..
  - AC-4 [deterministic] Given A corrupted or password-protected PDF at a valid temporary intake path; When intake analysis executes; Then Intake analysis aborts with error_code=SRC-E-PDF-CORRUPT..

### REQ-SRC-0022 — PDF handoff preserves intake verdicts
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
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
- Status: confirmed
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
- Status: confirmed
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
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that raw uploads must not pollute the official source collection and that structurally valid but partial sources may still proceed with explicit flags.
- Trigger: Source-engine finalization runs after metadata deliberation completes for a source candidate.
- Postconditions:
  - raw_upload_record.status is set to awaiting_owner_ack, source_engine_accepted, or rejected_at_source based on the source-engine result and any live owner_submission_risk_case.
  - The official source_collection is written only when the source engine completes successfully and no live owner_submission_risk_case remains unacknowledged.
  - Structurally valid sources with completeness_status in {partial, mixed, indeterminate} may still enter the source_collection with explicit admission_reason and preserved flags.
  - Structurally invalid uploads do not create source_collection records.
  - normalization_handoff_bundle is written only for source_engine_accepted sources whose owner_submission_risk_case is absent or acknowledged, and contains SourceMetadata, NormalizationInput, FrozenMemberManifest, and preserved intake_dossier completeness and integrity verdicts.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after successful metadata deliberation; When source admission and normalization handoff packaging execute; Then raw_upload_record.status="source_engine_accepted", exactly one source_collection record is written, and normalization_handoff_bundle.SourceMetadata.registry_entry_id is non-empty..
  - AC-2 [deterministic] Given A structurally valid upload whose intake_dossier.completeness_status="partial"; When source admission and normalization handoff packaging execute; Then one source_collection record is written with admission_reason="accepted_with_flags" and the handoff preserves completeness_status="partial"..
  - AC-3 [deterministic] Given A raw upload rejected earlier with error_code=SRC-E-EMPTY-FILE; When source admission and normalization handoff packaging would otherwise execute; Then no source_collection record is written for that submission..
  - AC-4 [deterministic] Given A source candidate with a live owner_submission_risk_case awaiting acknowledgment; When source admission and normalization handoff packaging execute; Then raw_upload_record.status="awaiting_owner_ack", no source_collection record is written, and no normalization_handoff_bundle is emitted..

### REQ-SRC-0026 — Authoritative work identity and collection linkage output
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that the source engine must determine exactly which book/source was uploaded and preserve collection linkage explicitly.
- Trigger: Metadata deliberation finalizes source-engine metadata for a source candidate.
- Postconditions:
  - work_output is written with non-null status and at least one evidence-backed position.
  - work_output.status is one of definitive, disputed, or insufficient_evidence.
  - A definitive case stores one chosen work position, while a disputed case preserves multiple work positions instead of forcing one bibliographic identity.
  - collection_match_output records whether the source matches an existing admitted work, an existing edition group, or no current collection match.
  - collection_match_output.match_status is one of: same_work_same_edition, same_work_new_edition, duplicate_same_edition_volume, conflict_mixed_edition, new_work, unknown. This disambiguates the kind of collection match, not just its presence.
  - collection_match_output.candidate_match_ids are structured as evidence-backed candidates with confidence (aligned with INV-SRC-0009 zero knowledge loss).
  - collection_match_output.matched_edition_group_id is the resolved best-match edition group identifier derived from candidate_match_ids when a single candidate has high confidence, or null when no high-confidence match exists. This field is consumed by reconciliation (REQ-SRC-0044).
  - When the source appears to be one present part of a larger work, collection_match_output records parent_work_id plus present_volumes and missing_volumes when that can be inferred.
  - present_volumes and missing_volumes are tied to the edition holding view (DEC-SRC-0018), not only the single source view. This enables holding-level completeness computation (INV-SRC-0010).
  - title_arabic in SourceMetadata is derived from the chosen or preserved work identity evidence rather than from raw upload naming alone.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with one evidence-backed work candidate; When metadata deliberation executes; Then work_output.status="definitive", len(work_output.positions)=1, and title_arabic is non-empty..
  - AC-2 [deterministic] Given A source candidate whose intake dossier contains two evidence-backed work candidates for the same uploaded source; When metadata deliberation executes; Then work_output.status="disputed" and len(work_output.positions) is at least 2..
  - AC-3 [deterministic] Given A source candidate whose intake dossier contains no evidence-backed work candidate; When metadata deliberation executes; Then work_output.status="insufficient_evidence"..
  - AC-4 [deterministic] Given A source candidate identified as volume 2 of a larger work with only volume 2 currently present; When metadata deliberation executes; Then collection_match_output.parent_work_id is non-null, collection_match_output.present_volumes includes "2", and collection_match_output.missing_volumes is non-empty..
  - AC-5 [deterministic] Given A source candidate that matches an existing admitted work but from a different muhaqqiq (different edition); When metadata deliberation executes; Then collection_match_output.match_status="same_work_new_edition" and collection_match_output.matched_edition_group_id either differs from the existing edition or is null..
  - AC-6 [deterministic] Given A source candidate that is volume 5 of an already-complete work from the same edition; When metadata deliberation executes; Then collection_match_output.match_status="duplicate_same_edition_volume" and collection_match_output.candidate_match_ids includes the existing edition holding with confidence..

### REQ-SRC-0027 — Owner-submission risk gate for study-quality threats
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that any uncertainty materially affecting study quality should trigger a human gate before official admission or downstream work proceeds.
- Trigger: Source-engine finalization evaluates whether the candidate carries any uncertainty that could materially affect study quality.
- Postconditions:
  - When study_quality_risk_flags is empty, no owner_submission_risk_case is written and normal source admission may continue.
  - When study_quality_risk_flags is non-empty, owner_submission_risk_case is written with owner_ack_required=true.
  - A live owner_submission_risk_case blocks official source_collection admission and blocks normalization_handoff_bundle emission until the owner acknowledges or annotates the case.
  - The source engine may still preserve provisional analysis outputs for review while the gate remains open.
- Acceptance criteria:
  - AC-1 [deterministic] Given A source candidate whose intake_dossier.study_quality_risk_flags is empty; When the owner-submission risk gate executes; Then no owner_submission_risk_case is written..
  - AC-2 [deterministic] Given A source candidate identified as one volume of a larger work with material dependency on missing volumes; When the owner-submission risk gate executes; Then owner_submission_risk_case.owner_ack_required=true, source_collection admission is blocked, and normalization handoff is blocked..
  - AC-3 [deterministic] Given A readable but suspicious source whose trust or integrity uncertainty could materially mislead study; When the owner-submission risk gate executes; Then owner_submission_risk_case.risk_flags is non-empty and owner_submission_risk_case.gate_status="awaiting_owner_ack"..

### REQ-SRC-0028 — Case complexity assessment and deliberation routing
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR report on agent-team architecture (2026-04-14). Defines three routing paths based on case complexity signals. The source engine classifies PDF text quality but does NOT perform OCR — degraded-evidence path means limited internal evidence requiring heavier external research, not OCR processing.
- Trigger: The orchestrator begins metadata deliberation for a source candidate.
- Postconditions:
  - case_complexity is set to one of fast_track, standard, or degraded_evidence.
  - fast_track requires all of: scholar_authority[author_canonical_id].authority_level >= primary, genre in {matn, sharh, hadith_collection, tafsir}, author_death_hijri is not null.
  - degraded_evidence is set when intake_dossier.source_format=pdf and intake_dossier.pdf_text_layer_status in {absent, corrupt}, or when intake_dossier.integrity_status=suspicious.
  - standard is the default when neither fast_track nor degraded_evidence applies.
  - fast_track path uses 2 independent verification reasoners, optional minimal research, and monitor. Research depth is reduced but verification independence is not.
  - standard path uses 2+ specialized research agents with distinct source_type values, 2 independent verification reasoners, disagreement resolver, and monitor.
  - degraded_evidence path expands research dispatch to 3+ source types to compensate for weak internal evidence. Verification reasoner count remains exactly 2.
  - case_complexity_record preserves the routing decision and the signals that determined it.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/05_tafsir/book.htm with definitive author attribution and author_death_hijri=774; When case complexity assessment runs; Then case_complexity="fast_track"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre="risalah" and a modern author; When case complexity assessment runs; Then case_complexity="standard"..
  - AC-3 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf with pdf_text_layer_status="corrupt"; When case complexity assessment runs; Then case_complexity="degraded_evidence"..
  - AC-4 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf with pdf_text_layer_status="absent"; When case complexity assessment runs; Then case_complexity="degraded_evidence"..

### REQ-SRC-0029 — Monitor feedback with non-recursive constraint
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: ChatGPT DR report on agent-team architecture (2026-04-14). Defines monitor feedback as a structured non-recursive observation record. The monitor audits and scores but never triggers in-run reruns.
- Trigger: A deliberation cell completes processing for any metadata field or trust evaluation.
- Postconditions:
  - A monitor_feedback record is written with non-null case_id, source_id, field, trust_path, and completed_at.
  - monitor_feedback.evidence_coverage records whether high-impact fields used at least 2 distinct source_type values.
  - monitor_feedback.independence_check records whether verification reasoners had distinct agent_id values and did not read each other's outputs before emitting.
  - monitor_feedback.uncertainty_flags records whether multi-position output was emitted, whether OCR-unreliable sources contributed, and whether confidence ordering was applied.
  - monitor_feedback.spec_violations records any blocking or fatal violations detected during the run.
  - monitor_feedback.suggested_policy_updates records non-blocking improvement suggestions as structured entries.
  - The monitor CANNOT trigger a rerun of the same case. Reruns happen only when a requirement's error condition mandates it.
  - monitor_feedback is written even for fast_track cases.
- Acceptance criteria:
  - AC-1 [integration] Given A fast_track trust evaluation that completes successfully; When monitor feedback runs; Then monitor_feedback.trust_path="fast_track" and monitor_feedback.case_id is non-null..
  - AC-2 [deterministic] Given A standard author attribution where one research source_type was used for a high-impact field; When monitor feedback runs; Then monitor_feedback.evidence_coverage.meets_minimum=false and monitor_feedback.spec_violations includes SRC-E-INCOMPLETE-RESEARCH..
  - AC-3 [deterministic] Given A completed deliberation cell where the monitor emits a suggested_policy_update; When the same case is checked for reruns; Then No rerun is triggered by the monitor's suggestion. The suggestion is stored as a future policy ticket only..

### REQ-SRC-0030 — Genre classification
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added after contract-architect review found genre is mandatory in CON-SRC-0004 but no requirement atom produces it. Genre is referenced as a precondition by REQ-SRC-0002 and REQ-SRC-0008 but was never formally specified. Amended 2026-04-23 (Phase 5b item 4, Option E-prime-final) to expand the postcondition-enumerated genre list with the four archival/documentary genres that are now pinned to the INV-SRC-0012 Axis 1 non-applicable set (mushaf, mashyakhah, thabat, barnamaj) per Codex E-prime DIM3 AMEND. The classifier does not currently emit these genres; the expansion keeps the postcondition list aligned with the Genre enum members that are normatively non-applicable for level. See follow-ups 21-26.
- Trigger: Metadata deliberation processes a source candidate whose intake dossier is available.
- Postconditions:
  - source_metadata.genre is set to one of matn, sharh, hashiyah, risalah, hadith_collection, tafsir, fatawa, tabaqat, mujam, nazm, mukhtasar, mushaf, mashyakhah, thabat, barnamaj, fahrasah, or other.
  - When genre classification is disputed between agents and both positions are evidence-backed, genre is set to the majority or higher-confidence position as a scalar and a genre_dispute record preserves the competing positions with evidence.
  - genre_dispute is optional and only written when genuine disagreement exists.
  - Genre classification uses title keywords, structural signals from the intake dossier, and content sampling when title evidence is ambiguous.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with title containing "أحكام"; When genre classification runs; Then source_metadata.genre="risalah"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small with title "همع الهوامع في شرح جمع الجوامع"; When genre classification runs; Then source_metadata.genre="sharh"..
  - AC-3 [deterministic] Given A source where one agent classifies genre=sharh and another classifies genre=hashiyah, both with evidence; When genre classification runs; Then source_metadata.genre is set to the higher-confidence position and genre_dispute preserves both positions..

### REQ-SRC-0031 — Multi-layer hint detection
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added after contract-architect review found is_multi_layer is mandatory in CON-SRC-0004 but no requirement atom produces it. Implements DEC-SRC-0010 OPT-C (source hints, normalization confirms). Domain-validator review added genre-based auto-hint for tafsir and hadith.
- Trigger: Metadata deliberation processes a source whose intake dossier and genre classification are available.
- Postconditions:
  - source_metadata.is_multi_layer is set to true or false and is never null.
  - is_multi_layer=true when title contains any keyword in the multi-layer keyword set or when genre implies structural multi-layer content.
  - The multi-layer keyword set includes: شرح, حاشية, تعليق, تقريرات, نكت.
  - Genre-based auto-hint: genre in {tafsir, hadith_collection, sharh, hashiyah} sets is_multi_layer=true regardless of title keywords, because these genres are structurally multi-layer by definition.
  - source_metadata.multi_layer_evidence records which signals drove the hint (keyword matches, genre-based auto-hint, or format-specific signals).
  - is_multi_layer is a source-engine hint, not an authoritative verdict. Normalization confirms or overrides from actual text structure per DEC-SRC-0010.
  - When no title keywords match and genre does not imply multi-layer, is_multi_layer is set to false.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small with title "همع الهوامع في شرح جمع الجوامع"; When multi-layer detection runs; Then source_metadata.is_multi_layer=true and multi_layer_evidence includes keyword "شرح"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre=risalah and no multi-layer keywords in title; When multi-layer detection runs; Then source_metadata.is_multi_layer=false..
  - AC-3 [deterministic] Given A source with genre=tafsir and no multi-layer keywords in title; When multi-layer detection runs; Then source_metadata.is_multi_layer=true and multi_layer_evidence includes "genre_auto_hint"..

### REQ-SRC-0032 — Structural format classification
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added after contract-architect review found structural_format is mandatory in CON-SRC-0004 but no requirement atom produces it.
- Trigger: Metadata deliberation processes a source whose genre classification and intake dossier are available.
- Postconditions:
  - source_metadata.structural_format is set to one of prose, commentary, verse, reference_entries, qa_format, tabular, or mixed.
  - prose is the default for genres: risalah, fatawa, matn, mukhtasar.
  - commentary is set when genre in {sharh, hashiyah} or when is_multi_layer=true with interleaved base text and authorial explanation.
  - verse is set when genre=nazm or when the text structure is predominantly metered poetry.
  - reference_entries is set when genre in {mujam, tabaqat} or when the text is organized as alphabetical or biographical entries.
  - qa_format is set when the text follows a question-and-answer structure.
  - structural_format may be overridden by content-level signals from the intake dossier when title and genre signals are insufficient.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small with genre=sharh; When structural format classification runs; Then source_metadata.structural_format="commentary"..
  - AC-2 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt with genre=nazm; When structural format classification runs; Then source_metadata.structural_format="verse"..
  - AC-3 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre=risalah; When structural format classification runs; Then source_metadata.structural_format="prose"..

### REQ-SRC-0033 — Volume count and intake timestamp derivation
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added after contract-architect review found volume_count and intake_timestamp are mandatory in CON-SRC-0004 but no requirement atom produces them.
- Trigger: Source admission finalizes the SourceMetadata record for an accepted source.
- Postconditions:
  - source_metadata.volume_count is set to the observed volume count from intake_dossier.declared_vs_observed_counts.observed_volume_count for multi-volume sources, or 1 for single-file sources.
  - source_metadata.intake_timestamp is set to the UTC ISO 8601 timestamp at the moment SourceMetadata finalization completes.
  - source_metadata.registry_entry_id is assigned as a unique identifier linking this SourceMetadata to its entry in the official source_collection registry.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after source-engine acceptance; When SourceMetadata finalization runs; Then source_metadata.volume_count=1 and source_metadata.intake_timestamp is a valid ISO 8601 UTC timestamp..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small after source-engine acceptance; When SourceMetadata finalization runs; Then source_metadata.volume_count=3 and source_metadata.registry_entry_id is non-empty..

### REQ-SRC-0034 — Compiler-as-muhaqiq detection
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: adversary-review-2 ADV2-002 (compiler/muhaqiq role inversion gap); v1 LESSONS.md ERR-02 (Shamela lists source authors in author field while actual compiler is in muhaqiq field)
- Trigger: Attribution parsing identifies both author and muhaqiq from metadata card or colophon.
- Postconditions:
  - When muhaqiq death_hijri > 1300 (or no death date available) AND all listed authors have death_hijri < 1000, the source is flagged as compiler_muhaqiq_inversion_candidate.
  - When temporal distance between the earliest listed author death_hijri and the muhaqiq death_hijri exceeds 300 Hijri years, the source is flagged as compiler_muhaqiq_inversion_candidate.
  - Flagged cases add compiler_muhaqiq_inversion to study_quality_risk_flags array on the source dossier.
  - The flag routes to the disagreement resolver for evidence-based role correction, where the resolver determines whether the muhaqiq is actually the compiler and the listed authors are the sources being compiled.
- Acceptance criteria:
  - AC-1 [integration] Given A Shamela source like السراج المنير with classical source authors (death_hijri < 1000) and a contemporary muhaqiq (death_hijri > 1300 or no death date); When metadata deliberation runs attribution parsing; Then compiler_muhaqiq_inversion is present in study_quality_risk_flags and the source is routed to the disagreement resolver..
  - AC-2 [integration] Given A normal sharh with a single classical author (death_hijri=676) and a contemporary tahqiq editor (death_hijri=1420) where the metadata card correctly identifies the author as author and the editor as muhaqiq; When metadata deliberation runs attribution parsing; Then compiler_muhaqiq_inversion is flagged (temporal gap exceeds 300 years), routing to the disagreement resolver. The resolver examines evidence and confirms the roles are correct (genuine tahqiq, not compilation), removing the flag..

### REQ-SRC-0035 — Display metadata for teaching units (source card)
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview 2026-04-14 + Gemini DR on display metadata design (2026-04-14). The DR grounds the source card (بطاقة المصدر) in the Islamic scholarly tradition: the Eight Heads (الرؤوس الثمانية) of classical muqaddimat and the Ten Principles (المبادئ العشرة) of foundational sciences.
- Trigger: Metadata deliberation completes for a source candidate with confirmed or disputed author attribution and genre classification.
- Postconditions:
  - source_metadata.display_card is written with 13 structured fields organized in two progressive disclosure tiers.
  - Quick-Glance tier (always visible): display_name (الاسم الشائع — the name the scholar is best known by), scholarly_title (اللقب العلمي — highest consensus-agreed honorific as a visual badge), death_date_display (سنة الوفاة — Hijri primary with Gregorian secondary), madhab (المذهب — methodological school tag), book_title (عنوان الكتاب), science_and_genre (التصنيف العلمي — with educational tooltips on technical terms), author_blurb_short (نبذة مختصرة — 1-2 sentence truncated blurb), and layer_tree_short (شجرة الكتاب — visual nesting for multi-layer works showing where the reader is).
  - Deep-Dive tier (expanded on interaction): full_name_lineage (البطاقة الشخصية الكاملة — ism, nasab, kunya, laqab, nisba unabridged), author_blurb_full (نبذة عن المؤلف — dynamically tailored to scholar type per Gemini DR), book_significance (أهمية الكتاب / الثمرة — why the author wrote it, what gap it fills, its rank), edition_metadata (بيانات الطبعة — muhaqqiq, publisher, year, city), dispute_panel (مؤشر التوثيق — visible only when authorship or attribution is disputed, showing all positions with evidence), and verification_sources (مصادر التوثيق — which databases and catalogs verified the metadata).
  - Deterministic extraction fields (from databases, never LLM-generated): display_name, full_name_lineage, death_date_display, book_title, science_and_genre, edition_metadata, layer_tree, verification_sources. Note: madhab and scholarly_title are registry-first fields — populated from scholar_authority registry when available, from agent research evidence when no registry entry exists, or null with reason in partial_reasons when neither source provides data.
  - LLM agent synthesis fields (generated by agent teams from research evidence): author_blurb, book_significance, dispute_panel summary. These must cite their evidence sources and are subject to multi-model review.
  - author_blurb is dynamically tailored to scholar type: hadith scholars emphasize rihlah and hifz; fiqh scholars emphasize rank within madhab; polymaths emphasize breadth and synthesis; modern scholars emphasize institutional role and contemporary impact; unknown authors state what is known with transparent uncertainty.
  - All display_card content is in Arabic and preserves full evidence chains per INV-SRC-0009.
- Acceptance criteria:
  - AC-1 [integration] Given A source identified as صحيح البخاري with author الإمام البخاري (death_hijri=256); When display metadata generation executes; Then display_card.display_name contains البخاري, display_card.scholarly_title contains أمير المؤمنين في الحديث or الإمام, display_card.death_date_display contains both 256 and 870, display_card.author_blurb mentions rihlah and hifz..
  - AC-2 [integration] Given A multi-layer source فتح الباري شرح صحيح البخاري by ابن حجر العسقلاني; When display metadata generation executes; Then display_card.layer_tree_short shows nested structure with صحيح البخاري as matn and فتح الباري as sharh, with a reading position indicator..
  - AC-3 [integration] Given A modern risalah الدروس المهمة لعامة الأمة by الشيخ ابن باز; When display metadata generation executes; Then display_card.author_blurb mentions institutional role (المفتي العام or equivalent) and display_card.book_significance describes it as an introductory text for beginners..
  - AC-4 [deterministic] Given A source with author_output.status=insufficient_evidence; When display metadata generation executes; Then display_card.status=partial, deterministic fields are populated, author_blurb is null with reason in partial_reasons..

### REQ-SRC-0036 — Completeness analysis of frozen source candidate
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Decomposed from REQ-SRC-0019 per contract-architect review finding that 4 sub-analyses in one atom is untestable.
- Trigger: Intake analysis assesses completeness of a frozen, container-classified source candidate.
- Postconditions:
  - completeness_status is written as one of: complete, partial, mixed, indeterminate.
  - self_containment_assessment is written as one of: self_contained, partially_self_contained, context_dependent.
  - cross_volume_dependency_assessment records whether missing volumes are: non_material, material, unknown.
  - parent_work_presence_model records whether the uploaded material appears to be part of a larger work, and which volumes are present or missing when that can be inferred.
  - declared_vs_observed_counts preserves any count comparison evidence (e.g. declared_volume_count vs observed_volume_count) used by completeness analysis.
  - holding_completeness_delta is an optional SourceMetadata field (CON-SRC-0004) that records what new volume coverage this source would add to a matching EditionHolding, if any. This is computed from comparing the source's volume_coverage against the existing holding's VolumeHolding states. If no matching holding exists, holding_completeness_delta is null. This field enables INV-SRC-0010 (computed holding completeness) by providing the incremental contribution signal.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small (3-volume directory); When completeness analysis executes; Then declared_vs_observed_counts.observed_volume_count=3 and completeness_status is one of {complete, indeterminate}..
  - AC-2 [deterministic] Given A frozen source candidate whose title page and file naming indicate 'الجزء الثاني' with no companion parts present; When completeness analysis executes; Then completeness_status=partial, self_containment_assessment is not self_contained, partiality_reasons includes single_part_without_companion_parts..
  - AC-3 [integration] Given A single-file Shamela book with no volume indicators (e.g. tests/fixtures/shamela_real/03_fiqh/book.htm); When completeness analysis executes; Then completeness_status=complete, self_containment_assessment=self_contained, cross_volume_dependency_assessment=non_material..

### REQ-SRC-0037 — Integrity analysis of frozen source candidate
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Decomposed from REQ-SRC-0019 per contract-architect review finding that 4 sub-analyses in one atom is untestable.
- Trigger: Intake analysis assesses structural integrity of a frozen, container-classified source candidate.
- Postconditions:
  - integrity_status is written as one of: sound, suspicious, corrupt.
  - study_quality_risk_flags is a list preserving every uncertainty that could materially affect study quality (e.g. encoding_anomaly, truncated_content, missing_basmala, garbled_diacritics).
  - contains_isnad_chains is a boolean set to true when transmission formulas (per INV-SRC-0006) are detected in the source text.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm (well-formed Shamela HTML); When integrity analysis executes; Then integrity_status=sound, study_quality_risk_flags is empty..
  - AC-2 [deterministic] Given A frozen PDF source with embedded null bytes and invalid UTF-8 sequences in text layer; When integrity analysis executes; Then integrity_status=corrupt, SRC-E-INTEGRITY-CORRUPT error is raised..
  - AC-3 [deterministic] Given A hadith fixture containing transmission formulas (حدثنا، أخبرنا، سمعت); When integrity analysis executes; Then contains_isnad_chains=true..

### REQ-SRC-0038 — Composite work (majmu‘) detection and decomposition
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Claude DR spec audit 2026-04-15 finding that majmu' collections (e.g. 37-volume compilations containing hundreds of independent risalahs) demand whole-part decomposition. Both Shamela and OpenITI treat the entire majmu' as a single entry. The source engine must detect and decompose.
- Trigger: Intake analysis examines a source candidate whose title, structure, or volume count suggests it is a composite collection (majmu').
- Postconditions:
  - intake_dossier.composite_work_type is set to one of: majmu, possible, or null.
  - When title evidence contains keywords indicating a composite collection (e.g. مجموع, فتاوى as collection title, رسائل as collection title) or structural signals indicate a composite work (high volume count with heterogeneous internal titles), composite_work_type is set to majmu.
  - For detected majmu' works, intake_dossier.sub_work_inventory is a list where each entry contains: sub_title (string), volume_number (int or null), page_start (int or null), page_end (int or null), and detection_method (one of toc_entry, volume_boundary, structural_signal).
  - The source engine creates a parent work record for the collection AND preserves sub_work_inventory for downstream engines to use during passaging and atomization.
  - Sub-work detection is best-effort from structural signals (table of contents, volume boundaries, internal bismillah/hamdala patterns). Complete decomposition may require normalization engine assistance.
  - Non-composite works have composite_work_type set to null and sub_work_inventory as an empty list.
- Acceptance criteria:
  - AC-1 [integration] Given A source with title "مجموع فتاوى ابن تيمية" spanning 37 volumes; When intake analysis runs composite detection; Then composite_work_type="majmu", sub_work_inventory is non-empty, each entry has sub_title and detection_method..
  - AC-2 [deterministic] Given A standard single-author monograph ("أحكام الاضطباع والرمل في الطواف") with 1 volume; When intake analysis runs composite detection; Then composite_work_type=null, sub_work_inventory is an empty list..
  - AC-3 [integration] Given A source titled "رسائل ابن رجب" with 1 volume but internal structural boundaries between distinct treatises; When intake analysis runs composite detection; Then composite_work_type="majmu" (detected via structural_signal), sub_work_inventory contains entries with detection_method="structural_signal"..
  - AC-4 [deterministic] Given A source titled "رسائل" with 1 volume and no detectable internal sub-work boundaries; When intake analysis runs composite detection; Then composite_work_type="possible", study_quality_risk_flags includes "ambiguous_composite_detection"..

### REQ-SRC-0039 — Work-to-work relationship modeling
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Claude DR spec audit 2026-04-15 finding that Islamic texts are fundamentally relational with mukhtasar-sharh-hashiyah chains up to 5 levels deep. Neither Shamela nor WorldCat models chain relationships. The source engine must capture typed links between derivative works and their base texts.
- Trigger: Metadata deliberation identifies a source whose genre implies a derivative relationship (sharh, hashiyah, mukhtasar, nazm, taliqa, taqrirat).
- Postconditions:
  - work_relationships is a list of typed links where each entry contains: relationship_type (one of is_commentary_on, is_supercommentary_on, is_abridgement_of, is_versification_of, has_part, is_part_of), target_work_title (string), target_work_author (string or null), and confidence (one of high, medium, low).
  - For genre=sharh: at least one entry with relationship_type=is_commentary_on identifying the matn it comments on.
  - For genre=hashiyah: at least one entry with relationship_type=is_supercommentary_on identifying the sharh it glosses.
  - For genre=mukhtasar: at least one entry with relationship_type=is_abridgement_of identifying the original work.
  - For genre=nazm: at least one entry with relationship_type=is_versification_of identifying the prose original.
  - When the target work cannot be identified from title, content, or metadata evidence, target_work_title is set to the best available partial evidence (e.g. extracted from the source's own title) and confidence=low.
  - For works where the matn is embedded in the commentary text, matn_embedding_style is recorded as one of: interlinear (matn lines alternate with sharh paragraphs), separated (matn in one block, sharh in another), marginal (matn in margin, sharh in body), or mazj (matn words woven into sharh sentences).
  - work_relationships is an empty list for standalone works (genre=matn, genre=risalah, genre=hadith_collection, genre=fatawa, or any genre with no derivative relationship).
- Acceptance criteria:
  - AC-1 [integration] Given A source titled "فتح الباري شرح صحيح البخاري" with genre=sharh; When work-to-work relationship modeling runs; Then work_relationships contains an entry with relationship_type="is_commentary_on", target_work_title contains "صحيح البخاري", confidence is high or medium..
  - AC-2 [integration] Given A source titled "حاشية ابن القيم على سنن أبي داود" with genre=hashiyah; When work-to-work relationship modeling runs; Then work_relationships contains an entry with relationship_type="is_supercommentary_on", target_work_title contains "سنن أبي داود"..
  - AC-3 [deterministic] Given A standalone risalah ("أحكام الاضطباع والرمل في الطواف") with genre=risalah; When work-to-work relationship modeling runs; Then work_relationships is an empty list..
  - AC-4 [integration] Given A source titled "شرح ابن عقيل على ألفية ابن مالك" with genre=sharh and interlinear matn embedding; When work-to-work relationship modeling runs; Then work_relationships contains is_commentary_on with target_work_title containing "ألفية ابن مالك" AND matn_embedding_style="interlinear"..

### REQ-SRC-0040 — Attribution confidence levels with scholarly terminology
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Claude DR spec audit 2026-04-15 finding that anonymous and pseudepigraphic works need confidence-level attribution beyond REQ-SRC-0004's three statuses (definitive/disputed/insufficient_evidence). The Islamic scholarly tradition has precise terminology for attribution confidence that the spec must model.
- Trigger: Author attribution finalizes (REQ-SRC-0004 completes) and the output must express the confidence level using Islamic scholarly terminology.
- Postconditions:
  - author_output.attribution_confidence is set to one of: confirmed (مؤكد — authorship established beyond reasonable doubt), disputed (مختلف في نسبته — scholarly disagreement on attribution; secondary display term منسوب إلى meaning "attributed to" may be used in display_card when the dispute involves only the attribution target), anonymous (مجهول المؤلف — truly unknown author), pseudepigraphic (منحول — falsely attributed, evidence the named author did not write it), or collective (جماعي — institutional or committee works with no named primary author; genuine co-authorship by named individuals using تأليف X و Y is handled by REQ-SRC-0004 co_authored status, not by collective).
  - For anonymous works, author_output preserves whatever temporal or geographic evidence exists (e.g. era, region, school affiliation) in author_output.anonymous_evidence as a free-text string.
  - For pseudepigraphic works, author_output preserves both the attributed_author (the false claimant) and false_attribution_evidence (the evidence against authenticity) per INV-SRC-0009.
  - For collective works, author_output.positions lists all identifiable contributors with their roles.
  - author_output.attribution_confidence_ar stores the Arabic scholarly term corresponding to the classification for display purposes.
  - attribution_confidence feeds into display_card dispute_panel generation (REQ-SRC-0035).
- Acceptance criteria:
  - AC-1 [deterministic] Given صحيح البخاري with author_output.status=definitive and unambiguous authorship; When attribution confidence classification runs; Then attribution_confidence="confirmed", attribution_confidence_ar="مؤكد"..
  - AC-2 [integration] Given A work attributed to al-Ghazali with scholarly evidence that the real author is a later imitator; When attribution confidence classification runs; Then attribution_confidence="pseudepigraphic", attribution_confidence_ar="منحول", attributed_author field preserved, false_attribution_evidence is non-empty..
  - AC-3 [integration] Given A truly anonymous work with only temporal evidence "مجهول - من أهل القرن السابع الهجري"; When attribution confidence classification runs; Then attribution_confidence="anonymous", attribution_confidence_ar="مجهول المؤلف", anonymous_evidence contains temporal era reference..
  - AC-4 [integration] Given الموسوعة الفقهية الكويتية with multiple contributing scholars, no single primary author, and institutional sponsorship; When attribution confidence classification runs; Then attribution_confidence="collective", attribution_confidence_ar="جماعي", author_output.positions lists identifiable contributors. Note that a work like "تأليف أحمد بن علي و محمد بن خالد" would NOT be collective but rather co_authored per REQ-SRC-0004..

### REQ-SRC-0041 — Format-agnostic multi-volume folder classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner correction 2026-04-15 that multi-volume handling should be format-agnostic. Single file = single volume, folder with files = multi-volume, regardless of format. PDF and plain text multi-volume folders were not covered by REQ-SRC-0017 (Shamela-only) or REQ-SRC-0020/0021 (single-file only).
- Trigger: Container classification receives a frozen directory candidate whose members are not .htm files.
- Postconditions:
  - A folder containing multiple .pdf files is classified as container_type=pdf_multi_volume. volume_manifest preserves the PDF files in filename order. normalization_route=pdf_ocr_primary or pdf_text_primary based on per-file text-layer assessment in REQ-SRC-0021.
  - A folder containing multiple .txt files is classified as container_type=plain_text_multi_volume. volume_manifest preserves the text files in filename order. normalization_route=plain_text_parse.
  - A folder containing mixed file formats is classified as container_type=mixed_format_directory with a warning. Each member's format is recorded individually.
  - The format-agnostic principle: single file submission = single-volume source. Folder submission = multi-volume source. The format of the files inside determines the processing route, but the folder-as-multi-volume pattern is universal across all formats.
  - Concatenated multi-volume PDFs (single PDF with internal volume boundaries marked by ToC entries) are detected at intake analysis (REQ-SRC-0019/REQ-SRC-0038), not at container classification. Container classification sees them as a single PDF file.
- Acceptance criteria:
  - AC-1 [deterministic] Given A frozen directory containing 3 PDF files named vol1.pdf, vol2.pdf, vol3.pdf; When container classification executes; Then container_type="pdf_multi_volume" and len(volume_manifest)=3 and volume_manifest is ordered by filename..
  - AC-2 [deterministic] Given A frozen directory containing 2 .txt files; When container classification executes; Then container_type="plain_text_multi_volume" and normalization_route="plain_text_parse"..
  - AC-3 [deterministic] Given A single PDF file submitted (not a folder); When container classification executes; Then container_type="pdf" (single-volume, not pdf_multi_volume)..

### REQ-SRC-0042 — Scholar profile lookup for display card
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Contract-attribution review finding that REQ-SRC-0035 display card depends on madhab, scholarly_title, and full_name_lineage as deterministic fields, but no atom produces them. This atom fills that gap.
- Trigger: Author attribution has produced an agent_consensus or agent_disagreement result with at least one evidence-backed position.
- Postconditions:
  - For each author position, a scholar_profile record is retrieved or synthesized containing: full_name_lineage (ism, nasab, kunya, laqab, nisba in the longest unabridged form available), scholarly_title (highest consensus-agreed honorific), madhab (legal or theological school), primary_science (main field of scholarship), era_description (century or generation label).
  - Deterministic lookup order: (1) scholar_authority registry match by canonical_id or name+death_hijri, (2) structured databases (OpenITI metadata, Shamela author records, Dorar.net API), (3) agent synthesis from textual evidence in the source itself.
  - When scholar_authority has a matching entry, all available fields are extracted deterministically without LLM involvement.
  - When no registry match exists and no structured database match is found, agent synthesis produces the profile from available evidence in author_output.positions and source text. Agent-synthesized profiles are tagged with profile_source=agent_synthesis.
  - death_gregorian is computed from death_hijri using standard Hijri-Gregorian conversion at display-card generation time (REQ-SRC-0035), not stored as a separate authoritative field in scholar_profile.
  - scholar_profile is attached to the corresponding author_output.positions entry and consumed by REQ-SRC-0035 for display_card generation.
- Acceptance criteria:
  - AC-1 [deterministic] Given Author attribution returns agent_consensus for البخاري (death_hijri=256) and scholar_authority registry contains a matching entry; When scholar profile lookup executes; Then scholar_profile.scholarly_title contains one of [امير المؤمنين في الحديث, الامام], scholar_profile.madhab is populated, scholar_profile.primary_science=hadith, scholar_profile.profile_source=scholar_authority.
  - AC-2 [integration] Given Author attribution returns agent_consensus for a minor modern scholar not present in scholar_authority or any structured database; When scholar profile lookup executes; Then scholar_profile is produced via agent synthesis, scholar_profile.profile_source=agent_synthesis, and fields are populated from source text evidence where available.
  - AC-3 [deterministic] Given Author attribution returns agent_consensus with death_hijri=256 for a scholar in scholar_authority; When display card generation (REQ-SRC-0035) consumes the scholar_profile; Then display_card.death_date_display contains both 256 (Hijri) and approximately 870 (Gregorian), computed at display time from death_hijri.

### REQ-SRC-0043 — New scholar registration in authority registry
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Adversary-attribution review ADV-ATT-008 finding that no atom specifies how a newly discovered author enters the scholar_authority registry.
- Trigger: Attribution identifies an author not present in scholar_authority.
- Postconditions:
  - A provisional scholar_authority entry is created with status=provisional, containing: canonical_id (auto-assigned), display_name, full_name_lineage (best available from source evidence), death_hijri (if known, otherwise null), primary_science (inferred from source science_scope), authority_level=unknown, and source_book_ids listing the book that triggered creation.
  - Provisional entries are usable by downstream processing (REQ-SRC-0042 scholar profile lookup returns them) but are flagged in trust evaluation: trust fast-track (REQ-SRC-0015) is NOT eligible for sources attributed to provisional scholars.
  - When a second distinct book by the same provisional scholar enters the pipeline and its evidence is consistent with the existing entry (display_name overlap and death_hijri match or both null), the entry is promoted to status=confirmed and authority_level is re-evaluated from unknown.
  - The entry records evidence_sources as an array of objects each containing book_id, evidence_type (metadata_card, title_page, colophon, agent_inference), and the raw evidence string.
- Acceptance criteria:
  - AC-1 [deterministic] Given A book attributed to a minor modern scholar not in scholar_authority with display_name and death_hijri available; When new scholar registration executes; Then scholar_authority gains a new entry with status=provisional, authority_level=unknown, source_book_ids containing the current book_id, and trust fast-track is blocked for this source.
  - AC-2 [integration] Given A second book by the same provisional scholar arrives with consistent evidence (same display_name, same death_hijri); When attribution completes and matches the provisional entry; Then The existing provisional entry is promoted to status=confirmed, source_book_ids contains both book_ids, and authority_level is re-evaluated.
  - AC-3 [deterministic] Given A new scholar with display_name matching existing entry ابن تيمية (death_hijri=728) but new evidence shows death_hijri=652; When new scholar registration executes; Then A separate scholar_authority entry is created with its own canonical_id, both entries have disambiguation_note referencing the other.

### REQ-SRC-0044 — Edition-group and holding reconciliation on source admission
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15). The DR identifies that the spec needs a reconciliation mechanism in step 60 (admission) that runs whenever a new source is accepted. This mechanism creates or updates EditionGroup and EditionHolding entities based on work_output and collection_match_output from metadata deliberation, enabling progressive completeness, duplicate handling, and supersession without mutating sources.
- Trigger: A source is admitted into the source_collection (REQ-SRC-0025 completes successfully with status=source_engine_accepted).
- Postconditions:
  - If collection_match_output.matched_edition_group_id exists with high confidence, attach the new source's volume slice(s) to the matching EditionHolding's VolumeHolding(s). Update VolumeHolding presence_state accordingly.
  - If no matching edition group exists or confidence is insufficient, create a new EditionGroup and EditionHolding from the source's work_output and completeness signals.
  - If the new source's edition fingerprint conflicts with the existing holding's edition fingerprint on a shared volume, do NOT silently merge. Either create a separate EditionHolding (DEC-SRC-0019) or set the conflicted VolumeHolding to presence_state=conflict.
  - EditionHolding completeness_state is recomputed after every attachment (INV-SRC-0010).
  - When a volume slot already has a present_primary source and a new source claims the same volume of the same edition, attach the new source as present_alternate, not as a replacement.
  - All reconciliation decisions (attach, create, conflict) are logged with evidence and confidence for auditability (INV-SRC-0009).
- Acceptance criteria:
  - AC-1 [deterministic] Given Volume 1 of a 3-volume work is already admitted with an EditionHolding (completeness_state=active_partial, expected_volume_count=3). A new source is admitted containing volumes 2 and 3 with matching edition fingerprint.; When Reconciliation executes after source admission.; Then The existing EditionHolding gains VolumeHolding entries for volumes 2 and 3 with presence_state=present_primary, and completeness_state transitions from active_partial to active_complete..
  - AC-2 [deterministic] Given A complete EditionHolding exists for a work. A new source is admitted containing volume 5 of the same work but from a different edition (different muhaqqiq, different publisher).; When Reconciliation executes after source admission.; Then A new EditionGroup and EditionHolding are created for the second edition, with only volume 5 present (completeness_state=active_partial). The original EditionHolding is unchanged..
  - AC-3 [deterministic] Given An EditionHolding exists with volume 1 present_primary. A new source is admitted claiming the same volume 1 of the same edition with matching fingerprint.; When Reconciliation executes after source admission.; Then The new source is attached as present_alternate for volume 1. The existing present_primary source remains primary. No data is overwritten..
  - AC-4 [deterministic] Given No existing work or edition matches exist in the collection. A new source is admitted with work_output.status=definitive.; When Reconciliation executes after source admission.; Then A new EditionGroup and EditionHolding are created from the work_output and completeness signals. The source's volume slices are attached as present_primary..
  - AC-5 [deterministic] Given A source admitted with work_output.status=insufficient_evidence (no evidence-backed work identity could be determined).; When Reconciliation executes after source admission.; Then A standalone EditionGroup and EditionHolding are created with completeness_state=indeterminate. Log entry includes unresolved_work_identity..
  - AC-6 [deterministic] Given A source with two files both labeled 'volume 1' containing different content, admitted to an existing EditionHolding.; When Reconciliation executes after source admission.; Then Both files are attached as present_alternate for volume 1. A study_quality_risk_flag with risk_type=ambiguous_volume_numbering is emitted..

### REQ-SRC-0045 — Supersession signal emission on source admission
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: high
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15), Edge Case 4. When a better edition of an already-held work arrives, the source engine must emit supersession signals so downstream engines know which holding is preferred. This implements the pointer-based supersession model from DEC-SRC-0020.
- Trigger: Reconciliation (REQ-SRC-0044) determines that a newly admitted source represents a potentially superior edition of an already-held work.
- Postconditions:
  - If the new edition is judged superior by the deliberation agents, new_holding.preferred_rank is set to primary and old_holding.superseded_by is set to new_holding.holding_id.
  - old_holding.holding_state transitions to superseded.
  - old_holding's sources and downstream artifacts remain addressable by ID. Nothing is deleted or overwritten.
  - new_holding.supersession_policy is set based on the nature of the quality difference. For works where text quality materially affects atomization (e.g. hadith corpora where OCR errors destroy isnad parsing), supersession_policy=regen_required. For works where differences are mostly footnotes and the core matn is stable, supersession_policy=regen_optional.
  - If agents cannot determine which edition is superior, no supersession is applied. Both holdings remain active. A study_quality_risk_flag is emitted with risk_type=unresolved_edition_preference.
- Acceptance criteria:
  - AC-1 [deterministic] Given A complete EditionHolding for a hadith work exists with text_fidelity=low_ocr. A new source is admitted as a different edition of the same work with text_fidelity=high_verified, also complete.; When Supersession signal emission executes.; Then old_holding.superseded_by=new_holding_id, old_holding.holding_state=superseded, new_holding.preferred_rank=primary, new_holding.supersession_policy=regen_required..
  - AC-2 [deterministic] Given A complete EditionHolding exists. A new source is admitted as a partial holding of a potentially better edition (only 1 of 5 volumes).; When Supersession signal emission evaluates.; Then No supersession is applied. The new EditionHolding is created with completeness_state=active_partial and no preferred_rank. Advisory flag supersession_blocked_by_completeness is emitted..
  - AC-3 [deterministic] Given Two editions of the same work exist. No quality comparison evidence is available (text_fidelity signals are identical, no owner hints exist, no edition reputation signals differ).; When Supersession signal emission evaluates.; Then Neither holding is superseded. Both remain active. A study_quality_risk_flag with risk_type=unresolved_edition_preference is emitted..

### REQ-SRC-0046 — Evidence preservation for downstream level inference
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-3. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR) and the R1/R2 reviewer wave: (a) nested Optional serialization rule added — when a preserved signal carries a nested structured field (e.g. muhaqiq_output, work_relationships, display_card), the nested object MUST itself honor D-023 and serialize absent sub-fields as explicit nulls rather than omitting keys; (b) genre_dispute signal added as required-preserved per R1 finding that disputed-genre payloads currently drop the secondary positions; (c) dedicated acceptance criteria now exercise the two signals most historically dropped at handoff (contains_isnad_chains and genre_dispute); (d) depends_on corrected to include DEC-SRC-0003 and INV-SRC-0011 because the evidence-preservation contract is the mechanism that makes the downstream content-only level classification (OPT-B) possible. Amended on 2026-04-21 per Phase 5b item 14 closing the Phase 5a Adversary ADV-011 finding ("positions[0].death_date unexercised"): AC-7 added to exercise depth-2 nested Optional serialization where the Optional sub-field is nested inside a list item. AC-6 already covers depth-1 direct-child omission; AC-7 closes the structurally distinct list-item sub-field omission case that Pydantic default serialization can silently drop when exclude_unset traverses list elements. Same-day retroactive reviewer wave on commit bf4354399 (Codex CLI structural + Gemini CLI 2 independent scholarly runs) reached 3-way AMEND consensus that the originally-committed path muhaqiq_output.positions[0].death_date was both structurally aspirational (MuhaqiqAssessment in contracts.py has no positions field) and scholarly-incorrect (muhaqqiqs unify on the title page of a critical edition and do not carry multi-position attributions in classical tahqiq practice; authorship disputes across نُسَخ produce the multi-position structure, not editorial attribution). AC-7 realigned to author_output.positions[0].death_hijri — structurally grounded (AuthorOutputPosition at contracts.py:676-712 declares death_hijri as Optional[int]) and scholarly-grounded (multi-position attribution is the canonical disputed-authorship shape in Dar Ibn Hazm / Muʾassasat al-Risāla critical-edition practice). The required-preserved signal set is correspondingly expanded from 16 signals to 17 by adding author_output; its inclusion is justified by the fact that author_output is already a mandatory SourceMetadata field per CON-SRC-0004, so preservation at handoff was always implicit — this amendment makes it explicit and subjects it to the recursive D-023 rule. Also amended on 2026-04-21 per Phase 5b item 16 closing a paper-reconciliation gap between the atom and contracts.py ErrorCode enum. Yesterday's retroactive Codex S6-DIM6A BLOCKER flagged that SRC-E-EVIDENCE-DROPPED and SRC-E-EVIDENCE-DROPPED- NESTED were cited in error_conditions and AC-3/AC-6/AC-7 but absent from contracts.py::ErrorCode. Item 16 pre-commit dispatch (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all optimized through /prompt-architect) reached 3-way unanimous PREFER_B verdict: rename to SRC-E-HANDOFF-EVIDENCE-DROPPED and SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED per the standing 2026-04-16 ChatGPT Deep Research advisory (dr-chatgpt-level-detection- 20260416.yaml:950) disambiguating step-60 handoff packaging omission from the step-40 intake code SRC-E-PDF-TEXT-EVIDENCE- DROPPED (PyMuPDF text-layer eviction). Scholarly rationale from both Gemini runs: step 60 omission maps to T-2 Attribution Error and T-6 Metadata Poisoning in reference/KNOWLEDGE_INTEGRITY.md, distinct from step 40's T-1 Silent Text Corruption; the HANDOFF_ prefix prevents Arabic-localization conflation of the error with hadith-science proof rejection (دليل شرعي / شاهد / قرينة) when surfaced to the owner as إسقاط دليل التسليم rather than the ambiguous إسقاط الدليل. Both enum entries added to engines/source/contracts.py ErrorCode step-60 block. All five normative reference sites (behavior.error_conditions @113/@116, AC-3 then-clause, AC-6 then-clause, AC-7 then-clause) updated in lock-step. Reviewer outputs at .kr/runtime/structural_audit_codex_cli_item16_precommit_ 20260421.md and .kr/runtime/domain_validation_gemini_cli_item16_ run_A_20260421.md and .kr/runtime/domain_validation_gemini_cli_ item16_run_B_20260421.md (gitignored). A follow-up Phase 5b item tracks severity reclassification (both Gemini runs flagged as AMEND that CON-SRC-0012 places "missing required-preserved evidence that upstream can re-emit" in the blocking tier, not fatal) and raise-site wiring in engines/source/src/admission.py _build_handoff_bundle (Codex DIM4 AMEND). Amended on 2026-04-23 (Phase 5b item 9 bundled with follow-up 19) to land the severity reclassification fatal → blocking on both SRC-E-HANDOFF-EVIDENCE-DROPPED and SRC-E-HANDOFF-EVIDENCE-DROPPED- NESTED error conditions. Per CON-SRC-0012 operational taxonomy, "fatal" is reserved for unrecoverable data corruption whereas "blocking" covers recoverable rejection with a correction path. Handoff-layer evidence omissions fit the blocking tier — upstream can re-emit the absent signals by re-running intake analysis (REQ-SRC-0037) on the already-frozen source, so the condition is recoverable. Gemini Run B DIM2 rationale verbatim: "Option B's HANDOFF_ prefix makes it clear this is a recoverable boundary transmission failure rather than source corruption, making it easier to correctly reason about and downgrade the severity to blocking." The HANDOFF_ prefix established in item 16 already isolated the failure mode from step-40 primary-text corruption; this amendment completes that isolation by aligning severity with CON-SRC-0012. Also amended 2026-04-23 (Phase 5b item 9) to close the ADV-010 Shamela happy-path concern: the atom's existing postconditions (when not populated the key is present with value null, recursive D-023 preservation) already protect the Shamela mushaf case where edition_info, muhaqiq_output, publisher, and matn_embedding_style are legitimately absent — Pydantic v2's default model_dump(mode="json") without exclude_none=True serializes Optional=None fields as null-valued JSON keys, not omissions. AC-8 added to provide the missing spec-linked proof that the Shamela happy-path actually satisfies the null-key contract today: a deterministic test constructs a SourceMetadata with all Shamela-legitimately-absent signals set to None, calls the admission flow, and asserts the JSON surface contains every one of the 17 required-preserved signal keys with null values for the absent ones. Without AC-8, a future exclude_none=True added to a model_dump call would silently break the contract and no spec-linked test would catch it. The raise-site wiring in admission.py _build_handoff_bundle for the positive error-raise path remains tracked as follow-up item 20 — this amendment lands the severity change and the Shamela happy-path assertion only.
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - D-023 metadata preservation — the governing rule — applies to every signal listed below AND recursively to every nested structured field within those signals. Absent top-level signals serialize as null-valued keys; absent sub-fields inside nested structures (e.g., muhaqiq_output.death_date, work_relationships[i].target_work_author) likewise serialize as null-valued keys, never omitted.
  - The required-preserved signal set is {title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_group_id, edition_info, publisher, muhaqiq_output, page_layout_hint, matn_embedding_style, pdf_text_layer_status, volume_count, holding_id, genre_dispute, author_output} on SourceMetadata and {contains_isnad_chains} on the intake_dossier surface — 17 signals total. Any change to this set must amend this atom's postconditions and acceptance_criteria in lock-step. author_output was added on 2026-04-21 per 3-way AMEND consensus (Codex CLI + Gemini CLI 2 runs) after the retroactive review of commit bf4354399 — author_output.positions is the canonical depth-2 list-item Optional structure in the classical tahqiq domain, so AC-7's list-item D-023 recursion test targets it rather than muhaqiq_output.positions (aspirational, see source field).
  - SourceMetadata.title_arabic is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.genre is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.science_scope is serialized in the handoff payload with the exact list populated upstream.
  - SourceMetadata.is_multi_layer is serialized in the handoff payload with the exact boolean populated upstream.
  - SourceMetadata.structural_format is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.edition_group_id is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.edition_info is serialized in the handoff payload with recursive D-023 preservation; when not populated the key is present with value null; when populated, each of its nested sub-fields (edition_label, edition_year, imprint_city, tahqiq_version) honors the same rule.
  - SourceMetadata.publisher is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.muhaqiq_output is serialized in the handoff payload with recursive D-023 preservation; when not populated the key is present with value null; when populated, each of its nested sub-fields (name, status, positions, death_date, attribution_confidence) honors the same rule.
  - SourceMetadata.page_layout_hint is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.matn_embedding_style is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.pdf_text_layer_status is serialized in the handoff payload; when not populated (non-PDF source) the key is present with value null.
  - SourceMetadata.volume_count is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.holding_id is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.genre_dispute is serialized in the handoff payload with recursive D-023 preservation; when not populated (no disputed secondary genre) the key is present with value null; when populated, each alternate-genre position (genre_candidate, supporting_evidence, confidence) honors the same rule.
  - SourceMetadata.author_output is serialized in the handoff payload with recursive D-023 preservation; author_output is a mandatory SourceMetadata field per CON-SRC-0004 so the top-level key is always present with a populated object; each entry in author_output.positions (AuthorOutputPosition per contracts.py:676-712) is a structured object whose Optional sub-fields (canonical_id, canonical_match_name, full_name_lineage, ism, kunya, death_hijri, death_hijri_verification, among others) honor the same recursive rule — absent sub-fields serialize as null-valued keys at the list-item level, never omitted. This is the depth-2 list-item D-023 recursion case exercised by AC-7.
  - intake_dossier.contains_isnad_chains is propagated into the normalization handoff bundle unchanged; when not populated the key is present with value null.
  - No evidence signal listed above is omitted from the payload — absent values serialize as null per D-023 metadata preservation, at every structural depth.
- Acceptance criteria:
  - AC-1 [integration] Given A fully populated intake for tests/fixtures/shamela_real/06_usul/book.htm with title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_group_id, edition_info, publisher, muhaqiq_output, page_layout_hint, matn_embedding_style, pdf_text_layer_status, volume_count, holding_id, genre_dispute, and intake_dossier.contains_isnad_chains all populated; When source admission and normalization handoff packaging executes; Then The serialized payload contains every signal from the 17-signal required-preserved set with the exact values populated upstream, no signal is omitted, and every nested sub-field is either populated with its exact value or serialized as null..
  - AC-2 [deterministic] Given A source whose muhaqiq_output is legitimately absent (for example a Shamela source without a critical-edition muhaqqiq); When source admission and normalization handoff packaging executes; Then The serialized payload contains the key muhaqiq_output with value null (not omitted)..
  - AC-3 [deterministic] Given A handoff packaging path that would have dropped the edition_info key entirely from the serialized payload; When handoff packaging executes; Then The packaging is aborted with SRC-E-HANDOFF-EVIDENCE-DROPPED and no partial bundle is emitted..
  - AC-4 [integration] Given A source whose metadata deliberation produced genre_dispute populated with two alternate-genre positions (genre_candidate_1 + supporting_evidence_1 + confidence_1; genre_candidate_2 + supporting_evidence_2 + confidence_2); When source admission and normalization handoff packaging executes; Then The serialized payload contains the key genre_dispute with both alternate positions preserved intact — neither the top-level genre_dispute key nor any nested sub-field (genre_candidate, supporting_evidence, confidence) is omitted..
  - AC-5 [integration] Given A source whose intake_dossier.contains_isnad_chains was populated true during intake analysis (for example, a hadith collection processed through REQ-SRC-0019); When source admission and normalization handoff packaging executes; Then The serialized handoff bundle contains intake_dossier.contains_isnad_chains=true, propagated unchanged from the intake_dossier surface..
  - AC-6 [deterministic] Given A handoff packaging path that would have serialized muhaqiq_output as a nested object with its `death_date` sub-field KEY absent (rather than set to null) because the upstream deliberation did not populate it; When handoff packaging executes; Then The packaging is aborted with SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED identifying muhaqiq_output.death_date as the omitted sub-field and no partial bundle is emitted..
  - AC-7 [deterministic] Given A handoff packaging path where author_output.positions is a non- empty list of AuthorOutputPosition entries (the canonical multi- position attribution shape established at contracts.py:676-712 for disputed authorship across نُسَخ / manuscript witnesses) and the first position element has its `death_hijri` sub-field KEY absent (rather than set to null) because the upstream multi-model consensus did not populate a death-date for that candidate-author position — the depth-2 case where the Optional sub-field is nested inside a list item rather than nested directly as a scalar child of a top-level signal (AC-6 covers the direct-child scalar case; AC-7 covers the list-item field that Pydantic exclude_unset can silently drop when iterating list elements). Path choice rationale: all three retroactive-review evaluators (Codex CLI structural + Gemini CLI 2 independent scholarly runs) reached 3-way consensus that author_output.positions[].death_ hijri is the scholarly- and structurally-correct depth-2 list- item path — authorship disputes across manuscripts produce competing multi-position attributions with per-position death dates in classical tahqiq practice, whereas muhaqqiqs act as a unified entity on the title page of a critical edition and do not carry multi-position attributions.; When handoff packaging executes; Then The packaging is aborted with SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED identifying author_output.positions[0].death_hijri as the omitted sub-field and no partial bundle is emitted..
  - AC-8 [deterministic] Given A Shamela mushaf-style SourceMetadata where the four signals Shamela legitimately lacks — edition_info, muhaqiq_output, publisher, matn_embedding_style — are all set to None, along with the other Optional signals page_layout_hint, pdf_text_layer_status (non-PDF source), holding_id, and genre_dispute that may also be legitimately absent for a Shamela intake. Every mandatory signal on SourceMetadata is populated normally (title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_group_id, volume_count, author_output, and the intake_dossier contains_isnad_chains surface); When source admission and normalization handoff packaging executes and the resulting bundle is serialized via Pydantic model_dump(mode="json") — the default serialization mode used by admission.py _build_handoff_bundle without exclude_none or exclude_unset overrides; Then The serialized JSON payload contains every key from the 17-signal required-preserved set. Legitimately-absent signals (edition_info, muhaqiq_output, publisher, matn_embedding_style, page_layout_hint, pdf_text_layer_status, holding_id, genre_dispute) appear as keys with value null — the null-key contract from REQ-SRC-0046 postconditions is satisfied by Pydantic v2 default serialization of Optional=None fields as JSON null. No SRC-E-HANDOFF-EVIDENCE-DROPPED or SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED error is raised. This AC closes the ADV-010 Shamela happy-path concern by providing the spec-linked proof that the null-key contract is operational on Shamela mushaf intakes — and it guards against a future exclude_none=True argument silently breaking the contract in a model_dump call..

### REQ-SRC-0047 — Owner override pathway for level at intake
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-4. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) error severity downgraded fatal → blocking per reviewer finding that an invalid override should reject the override but not terminate intake (intake proceeds with level=null, level_status=pending_synthesis); (b) three distinct error conditions now distinguish absent vs empty vs invalid override values (previously conflated); (c) audit-trail entry structure enriched to include the raw override token, the validation verdict, and the enum-value whitelist that was applied; (d) integrates with the CON-SRC-0004 middle-path level_status field. Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) after the 3-cycle pre-commit dispatch (A/B/C/D → E → E-prime; 2-run Gemini CLI unanimous findings + Codex CLI per cycle): the non-applicable rejection path now cites the INV-SRC-0012 3-axis gate. Axis 1 lists the six-value genre set {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah}; Axis 2 fires on composite_work_type == "majmu" (REQ-SRC-0038); Axis 3 is deferred to Phase 5b item 23. See follow-ups 21-26. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the synchronized `pending_taxonomy` → `pending_synthesis` rename across six verbatim occurrences (rationale, postcondition, AC-2, AC-4, AC-5, behavior.preconditions). The rename follows the 3-of-3 UNANIMOUS_OWN_SYNTHESIS verdict (Codex CLI gpt-5.4 architectural-fit + Gemini CLI 2-run gemini-3.1-pro-preview + gemini-2.5-pro classical-scholarly) on CON-SRC-0004 enum. Error codes, severity, behaviour, and acceptance criteria shape unchanged. Amended on 2026-04-23 (Phase 5b item 10) to add the ADV-012 stickiness postcondition and AC-6. ADV-012's proposed_fix had two halves: (1) add mandatory level_provenance enum — LANDED in Phase 5b item 1 (commit `62647cb2b`) via the LevelProvenance enum and the SourceMetadata.enforce_level_invariants Pydantic model_validator; (2) add stickiness postcondition to REQ-SRC-0047 — LANDED here as a cross-engine contract declaration: owner override produces level_provenance="owner_override", and any downstream actor with level-writing authority (synthesis per DEC-SRC-0003 synthesis-owns-level) MUST honor this provenance signal as the "do not silently overwrite" beacon. Silent overwrite of an owner-asserted level is a T-2 knowledge- integrity corruption vector — the owner's direct library assertion would be contradicted without audit, producing a level value that appears content-derived while it actually overrides an owner assertion, or vice versa. See Adversary ADV-012 verbatim at `.kr/runtime/adversary_phase5a_20260417 .md`:296-307.
- Trigger: The owner supplies an optional level override on a RawUploadRecord or equivalent intake surface when admitting a new source.
- Postconditions:
  - When owner_level_override is absent (the field is not present on the intake payload), SourceMetadata.level remains null and level_status is set per standard source-engine rules — pending_synthesis when no INV-SRC-0012 non-applicability axis fires, non_applicable_reference when at least one axis fires (Axis 1 genre ∈ {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah} OR Axis 2 composite_work_type == "majmu").
  - When owner_level_override is present AND the value passes the CON-SRC-0011 enum whitelist AND NO INV-SRC-0012 non-applicability axis fires (Axis 1 genre not in the six-value set AND Axis 2 composite_work_type != "majmu"), SourceMetadata.level is populated with the exact enum value and level_status is set to "assigned".
  - An audit-trail entry is written with provenance="owner_override", the raw override token received at intake, the validation verdict (accepted | rejected_invalid | rejected_nonapplicable | rejected_empty), the CON-SRC-0011 whitelist that was applied (enumerated snapshot), and an ISO 8601 timestamp of when the override was evaluated.
  - The override value, when accepted, survives through source admission and normalization handoff packaging unchanged (per REQ-SRC-0007 AC-3).
  - The (SourceMetadata.level, SourceMetadata.level_provenance) pair produced by an accepted owner override is ADV-012-STICKY. At the data-model level, contracts.py SourceMetadata.enforce_level_invariants (a Pydantic model_validator running under validate_assignment=True) enforces the IFF-style pair-consistency invariant — level non-null ↔ level_provenance non-null — so any single-field reassignment of either element trips a ValidationError. This blocks the "replace level, keep provenance untouched as owner_override but with a stale value" mutation path at the single-field layer. At the cross-engine contract level, any downstream actor with level-writing authority (the synthesis engine per DEC-SRC-0003 synthesis-owns-level) MUST inspect level_provenance on the received SourceMetadata record and, if level_provenance equals "owner_override", MUST NOT replace the level value without producing a structured level-override-disagreement entry — a non-silent escalation path whose specific shape is defined in the owning-engine spec. Silent overwriting of an owner-asserted level is a T-2 knowledge-integrity corruption vector — the owner's direct library assertion ("I, the student, declare this text mutawassiṭ") would be contradicted by a downstream content-derived classification without audit, producing a level value that masquerades as an owner assertion when it has been silently replaced (if provenance is left at "owner_override"), or as content-derived when it reflects the owner's override (if provenance is reassigned). The source engine's handoff packaging preserves the (level, level_provenance) pair byte-exactly through REQ-SRC-0007 AC-3, surfacing the provenance signal intact to every downstream consumer.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm (genre="matn" or "sharh") submitted with owner_level_override="mutawassiṭ"; When intake analysis processes the raw upload; Then SourceMetadata.level="mutawassiṭ", SourceMetadata.level_status= "assigned", an audit-trail entry is recorded with provenance="owner_override", raw_token="mutawassiṭ", verdict="accepted", whitelist_applied=["mubtadiʾ", "mutawassiṭ", "muntahī"], and a non-null ISO 8601 timestamp, and the override survives normalization handoff unchanged..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm submitted with owner_level_override="expert" (not a CON-SRC-0011 WorkLevel enum value); When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-INVALID, SourceMetadata.level remains null, SourceMetadata.level_status= "pending_synthesis", intake_analysis continues, and an audit-trail entry records raw_token="expert" and verdict="rejected_invalid"..
  - AC-3 [deterministic] Given A source with SourceMetadata.genre="mushaf" submitted with owner_level_override="mubtadiʾ"; When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE, SourceMetadata.level remains null, SourceMetadata.level_status= "non_applicable_reference", intake_analysis continues, and an audit-trail entry records verdict="rejected_nonapplicable"..
  - AC-4 [deterministic] Given A source submitted with owner_level_override="" (empty string) or owner_level_override="   " (whitespace only); When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-EMPTY, SourceMetadata.level remains null, SourceMetadata.level_status= "pending_synthesis" (or "non_applicable_reference" per genre), and an audit-trail entry records verdict="rejected_empty"..
  - AC-5 [deterministic] Given A source submitted with no owner_level_override field present at all on the intake payload; When intake analysis processes the raw upload; Then No audit-trail entry is written for override evaluation, SourceMetadata.level remains null, SourceMetadata.level_status is set per standard source-engine rules (pending_synthesis for leveled genres, non_applicable_reference for non-applicable genres), and intake_analysis completes without error..
  - AC-6 [deterministic] Given A SourceMetadata record produced by an accepted owner override through the REQ-SRC-0047 AC-1 happy path — (level="mutawassiṭ", level_provenance="owner_override", level_status="assigned"); When a subsequent actor attempts either of the two silent-overwrite attack paths — (a) reassigning SourceMetadata.level alone to "muntahī" without updating level_provenance, or (b) reassigning SourceMetadata.level_provenance alone to "synthesis_engine" without updating level; Then Layered defense in contracts.py SourceMetadata.enforce_level_invariants (Pydantic model_validator under validate_assignment=True) raises a ValidationError at the single-field assignment attempt. For attack path (a), CON-SRC-0004 invariant 1 (level_status=assigned IFF level non-null) fires first because it is ordered before the ADV-012 stickiness branch in the validator; ADV-012 stickiness is the backstop if the caller also mutates level_status. For attack path (b), CON-SRC-0004 invariants 1 and 2 both pass (level non-null + status=assigned is consistent), so ADV-012 stickiness is the sole defender. The test asserts that EITHER invariant citation is acceptable, because the outcome (single-field clear rejected, record unmutated) is identical under either layer. At the cross-engine contract level, the level_provenance="owner_override" field remains a readable signal to downstream engines that any paired reassignment of the pair (the structurally-valid mutation path which the IFF invariants cannot catch) requires a structured level-override-disagreement entry rather than a silent rewrite. The test also observes that the (level, level_provenance) pair is preserved byte-exactly through the REQ-SRC-0007 handoff JSON surface so downstream engines receive the provenance signal intact..

### REQ-SRC-0048 — Deferred validation surface for owner_level_override
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: medium
- Confidence: medium
- Source: Initial formulation on 2026-04-23 (Phase 5b item 6), closing the adversary finding ADV-005 from the Phase 5a 4-of-4 reviewer wave which flagged that the deferred-validation surface was cited in prior atoms but did not actually exist. The host spec (source engine, not synthesis or a cross-engine contract) is determined by the `REQ-SRC-*` atom-naming convention and by the item 7 3-of-3 UNANIMOUS_OWN_SYNTHESIS dispatch (Codex CLI + Gemini CLI 2-run) `req_src_0048_scope_guidance` outputs: Gemini Run A argued source-engine spec because "the source engine receives owner_level_override at intake (REQ-SRC-0047) and asserts level_status provenance at admission (CON-SRC-0004), so it logically owns the queueing and validation state of that override"; Codex argued cross-engine contract; Gemini Run B argued synthesis spec. Source-engine spec wins on naming- convention precedence and on the source-engine-owns-intake single-writer principle. Content derives from the item 7 dispatch scope guidance rather than a separate atom-design dispatch; future Phase 5b follow-up may harden with a focused 3-evaluator pre-commit review if the atom surface expands beyond the initial intake-stage-only scope. Reviewer outputs informing scope: .kr/runtime/structural_audit_codex_cli_item7_retry_20260423.md lines 126-127, .kr/runtime/domain_validation_gemini_cli_item7_run_A_20260423.md lines 24-25, .kr/runtime/domain_validation_gemini_cli_item7_run_B_20260423.md lines 143-144.
- Trigger: An owner_level_override is accepted at intake per REQ-SRC-0047 AC-1 (value is a valid CON-SRC-0011 WorkLevel enum member) but the source's genre is not yet resolved — either because metadata deliberation has not completed, or because agents returned genre_dispute without consensus.
- Postconditions:
  - The override is queued in an intake-stage pending-override record keyed by source_id, carrying raw_token, CON-SRC-0011-validated value, an ISO 8601 queued_at timestamp, and the genre-resolution state observed at queueing.
  - Interim SourceMetadata emits level=null and level_status="pending_synthesis" (the level is not populated from the queued override until axis validation resolves).
  - When metadata deliberation subsequently resolves genre to a single classification AND no INV-SRC-0012 non-applicability axis fires (Axis 1 genre ∉ {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah} AND Axis 2 composite_work_type != "majmu"), the queued override is applied as if it had been validated at intake per REQ-SRC-0047 AC-1, SourceMetadata.level is populated with the override value, and SourceMetadata.level_status is updated to "assigned".
  - When metadata deliberation resolves genre to a value where at least one INV-SRC-0012 axis fires, the queued override is rejected via the REQ-SRC-0047 AC-3 path (SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE), SourceMetadata.level remains null, and SourceMetadata.level_status is set to "non_applicable_reference".
  - When metadata deliberation resolves with genre_dispute (agents disagree and consensus-pattern does not yield a single classification per D-041), the queued override remains queued, SourceMetadata.level_status stays "pending_synthesis", and an audit-trail entry records the dispute with each agent's proposed genre and confidence. Synthesis engine consumes the queued override and the dispute record during its authoritative level determination pass.
  - An audit-trail entry is written at every state transition (queued, applied, rejected_nonapplicable, deferred_to_synthesis_on_dispute) with provenance="owner_override_deferred", the source_id, the genre-resolution state, and the ISO 8601 timestamp.
- Acceptance criteria:
  - AC-1 [integration] Given A source submitted with owner_level_override="mutawassiṭ" (a valid CON-SRC-0011 value) where metadata deliberation has not yet emitted a genre classification at the moment of intake.; When intake_analysis processes the raw upload; Then The override is queued with provenance="owner_override_deferred", the interim SourceMetadata emits level=null and level_status="pending_synthesis", an audit-trail entry records the queuing event, and intake_analysis completes without blocking on genre resolution..
  - AC-2 [integration] Given A source whose owner_level_override was queued per AC-1, when metadata deliberation subsequently resolves genre="sharh" (a leveled genre NOT in the Axis 1 non-applicable set) and composite_work_type=null (Axis 2 does not fire).; When genre resolution is received by the intake-stage override-queue handler; Then The queued override is applied, SourceMetadata.level is updated to "mutawassiṭ", SourceMetadata.level_status is updated to "assigned", and an audit-trail entry records the applied-on- resolution event with both the queued_at and resolved_at timestamps..
  - AC-3 [integration] Given A source whose owner_level_override was queued per AC-1, when metadata deliberation subsequently resolves genre="mushaf" (a genre in the Axis 1 non-applicable set).; When genre resolution is received by the intake-stage override-queue handler; Then The queued override is rejected with SRC-E-LEVEL-OVERRIDE- NONAPPLICABLE per REQ-SRC-0047 AC-3 path, SourceMetadata.level remains null, SourceMetadata.level_status is updated to "non_applicable_reference" with Axis 1 cited, and an audit-trail entry records the rejected-on-resolution event..
  - AC-4 [integration] Given A source whose owner_level_override was queued per AC-1, when metadata deliberation resolves with genre_dispute — two agents propose "risalah" (leveled) and a third proposes "mushaf" (non-applicable) with no consensus reached per D-041.; When genre resolution is received by the intake-stage override-queue handler; Then The queued override remains queued (not applied, not rejected), SourceMetadata.level_status stays "pending_synthesis", the audit-trail entry captures the genre_dispute with per-agent proposed-genre and confidence, and the handoff payload to normalization carries the queued-override record so the synthesis engine can consume it during authoritative level determination..
  - AC-5 [integration] Given A source submitted with owner_level_override="mubtadiʾ" where metadata deliberation has ALREADY completed (genre="sharh", composite_work_type=null) at the moment of intake — the standard REQ-SRC-0047 path, not a deferred-validation case.; When intake_analysis processes the raw upload; Then The override flows through the REQ-SRC-0047 synchronous validation path and the REQ-SRC-0048 deferred-queue surface is bypassed — no pending-override record is created, no "pending_synthesis" transition is emitted for this source, and SourceMetadata emits level="mubtadiʾ" with level_status="assigned" directly..
  - AC-6 [deterministic] Given A source whose owner_level_override was queued per AC-1, where the intake-stage override-staleness window (48 hours default) has elapsed before genre resolution is received.; When genre resolution finally arrives after the staleness window; Then The override is still applied/rejected per the resolved genre following the standard AC-2/AC-3 paths, but SRC-W-OVERRIDE- QUEUE-STALE is emitted as a warning and the audit-trail entry marks the override as applied-after-stale-window..
