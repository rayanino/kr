# Source Spec Atoms by Layer: contracts

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0001 | constraint | Shamela HTML and PDF are production formats | confirmed | high |
| CON-SRC-0002 | constraint | Hadith literature dominates source-engine benchmark quality | confirmed | high |
| CON-SRC-0003 | constraint | No existing pipeline contract is binding on the rebuild | confirmed | critical |
| CON-SRC-0004 | constraint | Complete SourceMetadata output schema | confirmed | critical |
| CON-SRC-0005 | constraint | Normalization handoff bundle includes a bridge input contract | confirmed | high |
| CON-SRC-0006 | constraint | Per-book processing cost and time ceiling | confirmed | high |
| CON-SRC-0007 | constraint | Source type extensibility | confirmed | high |

### CON-SRC-0001 — Shamela HTML and PDF are production formats
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0001; amended per OWNER_SANITY_CHECK_ANSWERS.md Q10, reference/pdf_fixture_observations_2026-04-14.md, and owner cross-validation on 2026-04-14 that normalization owns PDF-to-text conversion
- Rule: Production source intake must support Shamela HTML and PDF inputs, while plain text remains a minimal-metadata test format rather than a production collection format.

### CON-SRC-0002 — Hadith literature dominates source-engine benchmark quality
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012; amended per contract-architect-review.yaml
- Rule: At least 40 percent of source-engine benchmark fixtures must be hadith literature or hadith-adjacent works.

### CON-SRC-0003 — No existing pipeline contract is binding on the rebuild
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0014
- Rule: Archived and legacy source-engine contracts are reference material only and cannot overrule the current atom set.

### CON-SRC-0004 — Complete SourceMetadata output schema
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-002; amended per reference/pdf_fixture_observations_2026-04-14.md, owner guidance on 2026-04-14 about exact source/work identification and staged source admission, and the architecture decision that normalization owns text extraction.
- Rule: Every source-engine accepted source emits one SourceMetadata record with non-null mandatory fields source_id, source_sha256, frozen_blob_path, registry_entry_id, title_arabic, author_output, work_output, genre, science_scope, is_multi_layer, structural_format, trust_decision, completeness_status, integrity_status, volume_count, and intake_timestamp; author_output must always contain status (one of agent_consensus, agent_disagreement, agent_no_evidence, co_authored) and positions.

### CON-SRC-0005 — Normalization handoff bundle includes a bridge input contract
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added on 2026-04-14 after contract review found that SourceMetadata alone no longer defines a runnable source→normalization boundary in the live repo.
- Rule: Every source-engine accepted source must emit a NormalizationHandoffBundle containing non-null SourceMetadata, NormalizationInput, FrozenMemberManifest, completeness_status, and integrity_status.

### CON-SRC-0006 — Per-book processing cost and time ceiling
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: medium
- Source: adversary-review-2 ADV2-010 (no atom specifies timeout or cost ceiling for agent operations)
- Rule: Every source candidate has a maximum wall-clock processing time of 300 seconds and a maximum per-book API cost ceiling (initial default EUR 0.50). When either ceiling is reached, processing halts gracefully, the book is flagged with processing_timeout or processing_budget_exceeded in study_quality_risk_flags, and it is routed through the risk gate rather than consuming unbounded resources. Partial results obtained before the ceiling are preserved, not discarded.

### CON-SRC-0007 — Source type extensibility
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview 2026-04-14 identifying YouTube transcripts as the third most valuable source type after Shamela and PDF, requiring the architecture to accommodate new formats without restructuring
- Rule: The container classification step (step 30) must be designed so that adding a new source format requires only registering a new classifier and normalization route, without modifying existing classifiers or restructuring the pipeline. Current formats are shamela_html, pdf, and plain_text. Future formats include but are not limited to lecture_transcript. Container classification routes each format to normalization via a configurable normalization_route field on the classification output, not via hardcoded format-specific branching.
