# Source Spec Atoms by Layer: quality

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| INV-SRC-0001 | invariant | Owner hints never bias inference | proposed | critical |
| INV-SRC-0002 | invariant | Author attribution role separation is mandatory | proposed | critical |
| INV-SRC-0003 | invariant | Library never refuses knowledge | proposed | critical |
| INV-SRC-0004 | invariant | Truth-seeking over consensus-forcing | proposed | high |
| INV-SRC-0005 | invariant | Muhaqiq never gates trust decisions | proposed | high |
| INV-SRC-0006 | invariant | Isnad atomic preservation | proposed | high |
| INV-SRC-0007 | invariant | Scholar registry minimum population | proposed | critical |
| INV-SRC-0008 | invariant | PDF-derived text is never silently trusted at source handoff | proposed | critical |

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
