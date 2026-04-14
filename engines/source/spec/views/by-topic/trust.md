# Source Spec Atoms by Topic: trust

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0004 | decision | Replace trust algorithm with agent teams | proposed | critical |
| DEC-SRC-0005 | decision | Muhaqiq standing is metadata only | proposed | high |
| INV-SRC-0005 | invariant | Muhaqiq never gates trust decisions | proposed | high |
| INV-SRC-0008 | invariant | PDF-derived text is never silently trusted at source handoff | proposed | critical |
| OF-SRC-0003 | feedback | Minimize owner review load | confirmed | critical |
| OF-SRC-0009 | feedback | Replace numeric trust scoring with agent teams | confirmed | critical |
| OF-SRC-0010 | feedback | Muhaqiq standing is informational only | confirmed | high |
| REQ-SRC-0003 | requirement | Metadata deliberation stays owner-light | proposed | critical |
| REQ-SRC-0008 | requirement | Agent-team trust evaluation | proposed | critical |
| REQ-SRC-0022 | requirement | PDF handoff preserves intake verdicts | proposed | critical |

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

### INV-SRC-0005 — Muhaqiq never gates trust decisions
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010
- Rule: Muhaqiq standing may annotate parsing confidence, but it may never reject a source or block trust_decision finalization.

### INV-SRC-0008 — PDF-derived text is never silently trusted at source handoff
- Type: invariant
- Layer: quality
- Step: n/a
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md and the 2026-04-14 architecture decision that normalization owns PDF-to-text conversion
- Rule: No PDF-derived text may be treated as normalized source text by the source engine; every PDF handoff must carry source_metadata.pdf_text_layer_status and source_metadata.normalization_route=pdf_ocr_primary.

### OF-SRC-0003 — Minimize owner review load
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 3
- Interview question: How often should the owner review metadata decisions?
- Owner answer: The owner wants as few reviews as possible. The system should auto-decide aggressively and only send genuinely unresolvable cases to the owner.

### OF-SRC-0009 — Replace numeric trust scoring with agent teams
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 3 question 1
- Interview question: How should trust evaluation work?
- Owner answer: Trust evaluation should be rebuilt around agent teams rather than numeric factors. Two web researchers and two reasoners work under supervisors, supervisors deliberate, and monitor agents provide process-improvement feedback.

### OF-SRC-0010 — Muhaqiq standing is informational only
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 3 question 2
- Interview question: How should muhaqiq reputation affect source evaluation?
- Owner answer: Muhaqiq standing is metadata only. Unknown muhaqiqs should be flagged, and standing can be graduated from unknown to elite, but it must never cause the text to be discarded.

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
  - This rule does not prohibit the later owner_submission_risk_gate, because that gate addresses mistaken or materially risky submissions rather than metadata disagreement.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/06_usul/book.htm; When source metadata resolution completes; Then No owner_review_case is written..
  - AC-2 [deterministic] Given A Shamela HTML source whose metadata card, title, and colophon contain no author signal; When source metadata resolution completes; Then author_output.status="insufficient_evidence" and no owner_review_case is written..
  - AC-3 [deterministic] Given A source with two evidence-backed science positions that remain genuinely disputed after internal resolution; When science classification completes; Then the output preserves the dispute and no owner_review_case is written..

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
