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
| CON-SRC-0011 | constraint | WorkLevel enum — classical pedagogical-level vocabulary | confirmed | high |
| CON-SRC-0012 | constraint | Error severity taxonomy | confirmed | high |

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
- Source: Added from adversary-review.yaml ADV-002; amended per reference/ pdf_fixture_observations_2026-04-14.md, owner guidance on 2026-04-14 about exact source/work identification and staged source admission, and the architecture decision that normalization owns text extraction. Further amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication on DEC-SRC-0003: (a) added the mandatory `level_status` enum field per Gemini DR's middle- path proposal, which closes the null-conflation gap that Claude DR correctly identified without adopting OPT-C's shallow-signal level emission; (b) level_status provenance is the source engine at admission time, with values pending_taxonomy or non_applicable_reference, extended by downstream engines to assigned or unprocessable_error. See .kr/runtime/ adjudication_gemini_dr_20260417.md sections q5 and final_recommendation.
- Rule: Every source-engine accepted source emits one SourceMetadata record with non-null mandatory fields source_id, source_sha256, frozen_blob_path, registry_entry_id, title_arabic, author_output, work_output, genre, science_scope, is_multi_layer, structural_format, trust_decision, completeness_status, integrity_status, volume_count, intake_timestamp, AND level_status. The author_output field must always contain status (one of agent_consensus, agent_disagreement, agent_no_evidence, co_authored) and positions. The level_status field must always contain one of the four enum values defined below.

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

### CON-SRC-0011 — WorkLevel enum — classical pedagogical-level vocabulary
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Established on 2026-04-17 following the 3-of-3 unanimous OPT-B adjudication on DEC-SRC-0003. The enum values derive from Gemini CLI run 2 classical-defensibility review (R2 finding) which identified that the ChatGPT DR amendment set used `mutaqaddim` as the "advanced" level value — incorrect classical usage. Mutaqaddim (متقدم) denotes chronological priority (an earlier-generation scholar relative to a later one), NOT pedagogical advancement. The correct classical pedagogical ladder is mubtadiʾ (beginner) → mutawassiṭ (intermediate) → muntahī (terminal / advanced), documented in al-Zarnūjī's Taʿlīm al-Mutaʿallim, Ibn Khaldūn's Muqaddima Book VI (faṣl fī wajh al-ṣawāb fī taʿlīm al-ʿulūm), and the standard curriculum language of Dār al-Muṣṭafā and al- Qarawiyyīn ḥadīth tracks. See .kr/runtime/ adjudication_gemini_cli_run1_20260417.md (R2 terminology finding) and run2_20260417.md (independent confirmation).
- Rule: The WorkLevel enum is the canonical vocabulary for the SourceMetadata.level field and any downstream field that stores an authoritative pedagogical-level assignment. It has exactly three permitted values: "mubtadiʾ" (beginner / pre-malakah student), "mutawassiṭ" (intermediate / foundational-malakah student), and "muntahī" (terminal / curriculum-completing student). No other string values are valid for a SourceMetadata .level assignment. The historiographic term "mutaqaddim" and its counterpart "mutaʾakhkhirūn" are REJECTED as WorkLevel values — they denote chronological / generational priority among scholars, not pedagogical level.

### CON-SRC-0012 — Error severity taxonomy
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Established on 2026-04-21 per Phase 5b item 13 closing Codex CLI's Phase 5a reviewer-wave finding S7 ("schema enum {fatal, blocking, warning} has no operational definition anywhere"). The JSON Schema at engines/source/spec/schema.json $defs/severity pins the three permitted values but provides no semantic guidance. With 75+ behavior.error_conditions severity assignments across the atom corpus (24 fatal, 21 blocking, 30 warning as of this atom's creation date), the absence of operational semantics means each atom author has been free to interpret the values differently, silently corrupting the pipeline's error-recovery contract. This atom fixes the semantics once and authoritatively.
- Rule: Every behavior.error_conditions[].severity value in any source- engine spec atom carries a defined operational semantic. "fatal" means unrecoverable data corruption — the condition indicates that scholarly metadata or primary text has been damaged in a way that cannot be reconstructed from the inputs available to the pipeline, and no downstream engine may proceed with the affected record. "blocking" means recoverable rejection — the condition prevents the current operation from completing but a specific correction path exists (owner resubmits with a valid override, upstream re-emits missing evidence, transient dependency recovers). "warning" means advisory — the condition is logged and the operation continues; suitable for observability signals that must not halt the pipeline. These three values are mutually exclusive and collectively exhaustive for the severity enum.
