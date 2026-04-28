# Source Spec Atoms by Topic: identity

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0019 | requirement | Source-work identification and collection matching | confirmed | critical |
| REQ-SRC-0026 | requirement | Authoritative work identity and collection linkage output | confirmed | critical |
| REQ-SRC-0036 | requirement | Completeness analysis of frozen source candidate | confirmed | critical |
| REQ-SRC-0037 | requirement | Integrity analysis of frozen source candidate | confirmed | critical |
| REQ-SRC-0038 | requirement | Composite work (majmu‘) detection and decomposition | confirmed | critical |

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
