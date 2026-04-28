# Source Spec Atoms by Step: intake_analysis

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0019 | requirement | Source-work identification and collection matching | confirmed | critical |
| REQ-SRC-0021 | requirement | PDF intake analysis and text-layer quality classification | confirmed | critical |
| REQ-SRC-0023 | requirement | PDF text-layer evidence is diagnostic only | confirmed | critical |
| REQ-SRC-0024 | requirement | PDF page-geometry hints for normalization | confirmed | high |
| REQ-SRC-0036 | requirement | Completeness analysis of frozen source candidate | confirmed | critical |
| REQ-SRC-0037 | requirement | Integrity analysis of frozen source candidate | confirmed | critical |
| REQ-SRC-0038 | requirement | Composite work (majmu‘) detection and decomposition | confirmed | critical |
| REQ-SRC-0047 | requirement | Owner override pathway for level at intake | confirmed | medium |
| REQ-SRC-0048 | requirement | Deferred validation surface for owner_level_override | confirmed | medium |

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
  - For detected majmu' works, intake_dossier.sub_work_inventory is a list where each entry contains: sub_title (string), volume_number (int or null), page_start (int or null), page_end (int or null), detection_method (one of toc_entry, volume_boundary, structural_signal), and the per-constituent placeholder level triple (level: Optional[WorkLevel] = null, level_status: LevelStatus = "pending_synthesis", level_provenance: Optional[LevelProvenance] = null) added by Phase 5b follow-up 24 (a-lite) closure 2026-04-28. The entry enforces an IFF pair-consistency invariant via model_validator: level non-null IFF level_status == "assigned" IFF level_provenance non-null. Source engine NEVER writes per-constituent level (DEC-SRC-0003); each entry arrives with the placeholder triple (None, PENDING_SYNTHESIS, None) at intake and synthesis writes authoritative level later. Owner-override-entrance widening to per-constituent keying is OUT OF SCOPE for FU-24 (tracked as Phase 5b item 37).
  - The source engine creates a parent work record for the collection AND preserves sub_work_inventory for downstream engines to use during passaging and atomization. Phase 5b follow-up 24 (a-lite) closure 2026-04-28 propagates ``intake_dossier .sub_work_inventory`` onto ``SourceMetadata.sub_work_inventory`` via ``_populate_deterministic_metadata`` (deliberation.py) so the constituent placeholder surface flows through the source→normalization handoff via the dispatcher's existing ``model_copy(deep=True)`` of ``bundle.source_metadata`` (engines/normalization/src/dispatcher.py:74) without requiring cross-engine widening (Codex CRIT-1 MOOT under this architectural choice). D-023 metadata-flow is preserved.
  - Sub-work detection is best-effort from structural signals (table of contents, volume boundaries, internal bismillah/hamdala patterns). Complete decomposition may require normalization engine assistance.
  - Non-composite works have composite_work_type set to null and sub_work_inventory as an empty list.
- Acceptance criteria:
  - AC-1 [integration] Given A source with title "مجموع فتاوى ابن تيمية" spanning 37 volumes; When intake analysis runs composite detection; Then composite_work_type="majmu", sub_work_inventory is non-empty, each entry has sub_title and detection_method..
  - AC-2 [deterministic] Given A standard single-author monograph ("أحكام الاضطباع والرمل في الطواف") with 1 volume; When intake analysis runs composite detection; Then composite_work_type=null, sub_work_inventory is an empty list..
  - AC-3 [integration] Given A source titled "رسائل ابن رجب" with 1 volume but internal structural boundaries between distinct treatises; When intake analysis runs composite detection; Then composite_work_type="majmu" (detected via structural_signal), sub_work_inventory contains entries with detection_method="structural_signal"..
  - AC-4 [deterministic] Given A source titled "رسائل" with 1 volume and no detectable internal sub-work boundaries; When intake analysis runs composite detection; Then composite_work_type="possible", study_quality_risk_flags includes "ambiguous_composite_detection"..

### REQ-SRC-0047 — Owner override pathway for level at intake
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-4. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) error severity downgraded fatal → blocking per reviewer finding that an invalid override should reject the override but not terminate intake (intake proceeds with level=null, level_status=pending_synthesis); (b) three distinct error conditions now distinguish absent vs empty vs invalid override values (previously conflated); (c) audit-trail entry structure enriched to include the raw override token, the validation verdict, and the enum-value whitelist that was applied; (d) integrates with the CON-SRC-0004 middle-path level_status field. Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) after the 3-cycle pre-commit dispatch (A/B/C/D → E → E-prime; 2-run Gemini CLI unanimous findings + Codex CLI per cycle): the non-applicable rejection path now cites the INV-SRC-0012 3-axis gate. Axis 1 lists the six-value genre set {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah}; Axis 2 fires on composite_work_type == "majmu" (REQ-SRC-0038); Axis 3 is deferred to Phase 5b item 23. See follow-ups 21-26. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the synchronized `pending_taxonomy` → `pending_synthesis` rename across six verbatim occurrences (rationale, postcondition, AC-2, AC-4, AC-5, behavior.preconditions). The rename follows the 3-of-3 UNANIMOUS_OWN_SYNTHESIS verdict (Codex CLI gpt-5.4 architectural-fit + Gemini CLI 2-run gemini-3.1-pro-preview + gemini-2.5-pro classical-scholarly) on CON-SRC-0004 enum. Error codes, severity, behaviour, and acceptance criteria shape unchanged. Amended on 2026-04-23 (Phase 5b item 10) to add the ADV-012 stickiness postcondition and AC-6. ADV-012's proposed_fix had two halves: (1) add mandatory level_provenance enum — LANDED in Phase 5b item 1 (commit `62647cb2b`) via the LevelProvenance enum and the SourceMetadata.enforce_level_invariants Pydantic model_validator; (2) add stickiness postcondition to REQ-SRC-0047 — LANDED here as a cross-engine contract declaration: owner override produces level_provenance="owner_override", and any downstream actor with level-writing authority (synthesis per DEC-SRC-0003 synthesis-owns-level) MUST honor this provenance signal as the "do not silently overwrite" beacon. Silent overwrite of an owner-asserted level is a T-2 knowledge- integrity corruption vector — the owner's direct library assertion would be contradicted without audit, producing a level value that appears content-derived while it actually overrides an owner assertion, or vice versa. See Adversary ADV-012 verbatim at `.kr/runtime/adversary_phase5a_20260417 .md`:296-307. Closure-wave amendment 2026-04-23 (Codex CAF-4 HIGH): narrowed the stickiness postcondition and AC-6 scope to match what `enforce_level_invariants` in contracts.py actually blocks — PAIR-CLEARING attacks (level-alone-null or provenance-alone-null), NOT value-swap attacks where both fields stay non-null. An earlier draft overstated the guarantee by claiming the IFF invariant blocks value-swap (e.g. mubtadiʾ→muntahī with provenance untouched); it does not, because (muntahī, OWNER_OVERRIDE) is a structurally valid pair under pair-consistency rules. Value-swap protection is a cross-engine contract: the synthesis engine per DEC-SRC-0003 synthesis-owns-level is required to refuse silent overwrite on records with level_provenance= OWNER_OVERRIDE, producing a structured disagreement entry instead. Source engine's contribution is the IFF invariant at the data-model layer plus byte-exact provenance preservation through REQ-SRC-0007 handoff — the signal the synthesis engine consumes. Reviewer output at `.kr/runtime/closure_wave_codex_cli_20260423.md`.
- Trigger: The owner supplies an optional level override on a RawUploadRecord or equivalent intake surface when admitting a new source.
- Postconditions:
  - When owner_level_override is absent (the field is not present on the intake payload), SourceMetadata.level remains null and level_status is set per standard source-engine rules — pending_synthesis when no INV-SRC-0012 non-applicability axis fires, non_applicable_reference when at least one axis fires (Axis 1 genre ∈ {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah} OR Axis 2 composite_work_type == "majmu").
  - When owner_level_override is present AND the value passes the CON-SRC-0011 enum whitelist AND NO INV-SRC-0012 non-applicability axis fires (Axis 1 genre not in the six-value set AND Axis 2 composite_work_type != "majmu"), SourceMetadata.level is populated with the exact enum value and level_status is set to "assigned".
  - An audit-trail entry is written with provenance="owner_override", the raw override token received at intake, the validation verdict (accepted | rejected_invalid | rejected_nonapplicable | rejected_empty), the CON-SRC-0011 whitelist that was applied (enumerated snapshot), and an ISO 8601 timestamp of when the override was evaluated.
  - The override value, when accepted, survives through source admission and normalization handoff packaging unchanged (per REQ-SRC-0007 AC-3).
  - The (SourceMetadata.level, SourceMetadata.level_provenance) pair produced by an accepted owner override is ADV-012-STICKY. At the data-model level, contracts.py SourceMetadata.enforce_level_invariants (a Pydantic model_validator running under validate_assignment=True) enforces the IFF-style pair-consistency invariant — level non-null ↔ level_provenance non-null — so any single-field reassignment that BREAKS the pair (clearing level alone, clearing level_provenance alone) trips a ValidationError. The invariant does NOT block value-swap mutations where both elements stay non-null (e.g. replacing level=mutawassiṭ with level=muntahī while provenance remains OWNER_OVERRIDE) — that scenario satisfies the IFF pair-consistency rule at the Pydantic layer, so value-swap protection is not a single-engine invariant. The Codex closure-wave finding (CAF-4, 2026-04-23) surfaced this correctly: an earlier draft of this postcondition claimed the invariant blocked value-swap, which overstated what the code enforces. The accurate statement is that the invariant is a pair-clearing defense only; value-swap is governed by the cross-engine contract below. At the cross-engine contract level, any downstream actor with level-writing authority (the synthesis engine per DEC-SRC-0003 synthesis-owns-level) MUST inspect level_provenance on the received SourceMetadata record and, if level_provenance equals "owner_override", MUST NOT replace the level value without producing a structured level-override-disagreement entry — a non-silent escalation path whose specific shape is defined in the owning-engine spec. Silent overwriting of an owner-asserted level is a T-2 knowledge-integrity corruption vector — the owner's direct library assertion ("I, the student, declare this text mutawassiṭ") would be contradicted by a downstream content-derived classification without audit, producing a level value that masquerades as an owner assertion when it has been silently replaced (if provenance is left at "owner_override"), or as content-derived when it reflects the owner's override (if provenance is reassigned). The source engine's handoff packaging preserves the (level, level_provenance) pair byte-exactly through REQ-SRC-0007 AC-3, surfacing the provenance signal intact to every downstream consumer.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm (genre="matn" or "sharh") submitted with owner_level_override="mutawassiṭ"; When intake analysis processes the raw upload; Then SourceMetadata.level="mutawassiṭ", SourceMetadata.level_status= "assigned", an audit-trail entry is recorded with provenance="owner_override", raw_token="mutawassiṭ", verdict="accepted", whitelist_applied=["mubtadiʾ", "mutawassiṭ", "muntahī"], and a non-null ISO 8601 timestamp, and the override survives normalization handoff unchanged..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm submitted with owner_level_override="expert" (not a CON-SRC-0011 WorkLevel enum value); When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-INVALID, SourceMetadata.level remains null, SourceMetadata.level_status= "pending_synthesis", intake_analysis continues, and an audit-trail entry records raw_token="expert" and verdict="rejected_invalid"..
  - AC-3 [deterministic] Given A source with SourceMetadata.genre="mushaf" submitted with owner_level_override="mubtadiʾ"; When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE, SourceMetadata.level remains null, SourceMetadata.level_status= "non_applicable_reference", intake_analysis continues, and an audit-trail entry records verdict="rejected_nonapplicable"..
  - AC-4 [deterministic] Given A source submitted with owner_level_override="" (empty string) or owner_level_override="   " (whitespace only); When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-EMPTY, SourceMetadata.level remains null, SourceMetadata.level_status= "pending_synthesis" (or "non_applicable_reference" per genre), and an audit-trail entry records verdict="rejected_empty"..
  - AC-5 [deterministic] Given A source submitted with no owner_level_override field present at all on the intake payload; When intake analysis processes the raw upload; Then No audit-trail entry is written for override evaluation, SourceMetadata.level remains null, SourceMetadata.level_status is set per standard source-engine rules (pending_synthesis for leveled genres, non_applicable_reference for non-applicable genres), and intake_analysis completes without error..
  - AC-6 [deterministic] Given A SourceMetadata record produced by an accepted owner override through the REQ-SRC-0047 AC-1 happy path — (level="mutawassiṭ", level_provenance="owner_override", level_status="assigned"); When a subsequent actor attempts either of the two PAIR-CLEARING attack paths that the IFF invariant catches — (a) clearing SourceMetadata.level to null while leaving level_provenance set, or (b) clearing SourceMetadata.level_provenance to null while leaving level set. Pair-clearing breaks the level↔provenance IFF invariant, so the validator rejects. (Value-swap attacks that keep both fields non-null — e.g. level=mutawassiṭ→muntahī while provenance stays OWNER_OVERRIDE — are NOT caught by this validator because they preserve pair consistency; those are governed by the cross-engine contract in behavior.postconditions and are the synthesis engine's responsibility to refuse silently per DEC-SRC-0003 synthesis-owns-level authority. The Codex closure-wave finding CAF-4 surfaced this scope distinction — AC-6 now faithfully describes what enforce_level_invariants blocks, not what the cross-engine contract separately prescribes.); Then Layered defense in contracts.py SourceMetadata.enforce_level_invariants (Pydantic model_validator under validate_assignment=True) raises a ValidationError at the single-field assignment attempt. For attack path (a), CON-SRC-0004 invariant 1 (level_status=assigned IFF level non-null) fires first because it is ordered before the ADV-012 stickiness branch in the validator; ADV-012 stickiness is the backstop if the caller also mutates level_status. For attack path (b), CON-SRC-0004 invariants 1 and 2 both pass (level non-null + status=assigned is consistent), so ADV-012 stickiness is the sole defender. The test asserts that EITHER invariant citation is acceptable, because the outcome (single-field clear rejected, record unmutated) is identical under either layer. At the cross-engine contract level, the level_provenance="owner_override" field remains a readable signal to downstream engines that any paired reassignment of the pair (the structurally-valid mutation path which the IFF invariants cannot catch) requires a structured level-override-disagreement entry rather than a silent rewrite. The test also observes that the (level, level_provenance) pair is preserved byte-exactly through the REQ-SRC-0007 handoff JSON surface so downstream engines receive the provenance signal intact..

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
