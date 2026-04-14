# Source Spec Atoms by Step: intake_analysis

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0019 | requirement | Intake dossier and source-work identification | proposed | critical |
| REQ-SRC-0021 | requirement | PDF intake analysis and text-layer quality classification | proposed | critical |
| REQ-SRC-0023 | requirement | PDF text-layer evidence is diagnostic only | proposed | critical |
| REQ-SRC-0024 | requirement | PDF page-geometry hints for normalization | proposed | high |

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
  - self_containment_assessment is one of self_contained, partially_self_contained, or context_dependent.
  - cross_volume_dependency_assessment records whether missing volumes are non_material, material, or unknown to study quality.
  - integrity_status is one of sound, suspicious, or corrupt.
  - study_quality_risk_flags preserves every uncertainty that could materially affect study quality.
  - parent_work_presence_model preserves whether the uploaded material appears to be part of a larger work and which volumes are currently present or missing when that can be inferred.
  - declared_vs_observed_counts preserves any count comparison evidence used by completeness analysis.
  - Metadata deliberation consumes the intake_dossier rather than re-reading raw upload state directly.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When intake analysis executes; Then intake_dossier.dossier_id is non-empty, len(intake_dossier.title_evidence) is at least 1, len(intake_dossier.work_identity_proposal.candidates) is at least 1, and intake_dossier.integrity_status is one of {sound, suspicious, corrupt}..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small; When intake analysis executes; Then intake_dossier.declared_vs_observed_counts.observed_volume_count=3 and intake_dossier.completeness_status is one of {complete, indeterminate}..
  - AC-3 [deterministic] Given A frozen source candidate whose title page and file naming indicate "الجزء الثاني" with no companion parts present; When intake analysis executes; Then intake_dossier.completeness_status="partial", intake_dossier.self_containment_assessment is not "self_contained", and intake_dossier.partiality_reasons includes "single_part_without_companion_parts"..
  - AC-4 [deterministic] Given A frozen source candidate that begins mid-commentary, ends mid-chapter, or contains references whose resolution depends materially on missing volumes; When intake analysis executes; Then intake_dossier.study_quality_risk_flags is non-empty and intake_dossier.cross_volume_dependency_assessment is one of {material, unknown}..

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
