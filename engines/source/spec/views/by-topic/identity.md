# Source Spec Atoms by Topic: identity

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0019 | requirement | Intake dossier and source-work identification | proposed | critical |
| REQ-SRC-0026 | requirement | Authoritative work identity and collection linkage output | proposed | critical |

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
  - When the source appears to be one present part of a larger work, collection_match_output records parent_work_id plus present_volumes and missing_volumes when that can be inferred.
  - title_arabic in SourceMetadata is derived from the chosen or preserved work identity evidence rather than from raw upload naming alone.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with one evidence-backed work candidate; When metadata deliberation executes; Then work_output.status="definitive", len(work_output.positions)=1, and title_arabic is non-empty..
  - AC-2 [deterministic] Given A source candidate whose intake dossier contains two evidence-backed work candidates for the same uploaded source; When metadata deliberation executes; Then work_output.status="disputed" and len(work_output.positions) is at least 2..
  - AC-3 [deterministic] Given A source candidate whose intake dossier contains no evidence-backed work candidate; When metadata deliberation executes; Then work_output.status="insufficient_evidence"..
  - AC-4 [deterministic] Given A source candidate identified as volume 2 of a larger work with only volume 2 currently present; When metadata deliberation executes; Then collection_match_output.parent_work_id is non-null, collection_match_output.present_volumes includes "2", and collection_match_output.missing_volumes is non-empty..
