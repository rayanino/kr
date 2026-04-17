# Source Spec Atoms by Layer: quality

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| INV-SRC-0001 | invariant | Owner hints never bias inference | confirmed | critical |
| INV-SRC-0002 | invariant | Author attribution role separation is mandatory | confirmed | critical |
| INV-SRC-0003 | invariant | Library never refuses knowledge | confirmed | critical |
| INV-SRC-0004 | invariant | Truth-seeking over consensus-forcing | confirmed | high |
| INV-SRC-0005 | invariant | Muhaqiq never gates trust decisions | confirmed | high |
| INV-SRC-0006 | invariant | Isnad atomic preservation | confirmed | high |
| INV-SRC-0007 | invariant | Scholar registry minimum population | confirmed | critical |
| INV-SRC-0008 | invariant | PDF-derived text is never silently trusted at source handoff | confirmed | critical |
| INV-SRC-0009 | invariant | Zero knowledge loss in all source-engine output | confirmed | critical |
| INV-SRC-0010 | invariant | Holding-level completeness is computed, not asserted | confirmed | critical |
| INV-SRC-0011 | invariant | Source engine must not infer level from shallow metadata | confirmed | critical |
| INV-SRC-0012 | invariant | Non-applicable genres require level null | confirmed | high |

### INV-SRC-0001 — Owner hints never bias inference
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002 and OF-SRC-0005; amended per contract-architect-review.yaml
- Rule: Hint comparison may inspect only inferred_metadata.author_name, inferred_metadata.genre, and inferred_metadata.science_scope after base inference finishes.

### INV-SRC-0002 — Author attribution role separation is mandatory
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0004; amended per domain-validator-review.yaml
- Rule: No marker from one role set may populate a field belonging to another role set. The 7 role sets defined by REQ-SRC-0014 are author, compiler, preparer, copyist, editor, annotator, and supervisor.

### INV-SRC-0003 — Library never refuses knowledge
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0006 and broadened on 2026-04-14 after owner clarification that only structurally invalid uploads should be blocked from the official source flow.
- Rule: No structurally valid source is rejected solely because its science label is absent from science_registry, because its metadata remains disputed, or because its completeness or integrity verdict carries non-fatal flags.

### INV-SRC-0004 — Truth-seeking over consensus-forcing
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Rule: A metadata field qualifies as genuine scholarly dispute only when at least two independent agents provide evidence-backed positions for that field.

### INV-SRC-0005 — Muhaqiq never gates trust decisions
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0010
- Rule: Muhaqiq standing may annotate parsing confidence, but it may never reject a source or block trust_decision finalization.

### INV-SRC-0006 — Isnad atomic preservation
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added from domain-validator-review.yaml
- Rule: Transmission formulas حدثنا, ثنا, نا, أخبرنا, أنبأنا, سمعت, قرأت على, أجاز لي, and ناولني mark isnad chains that must remain in one atomic unit across processing boundaries.

### INV-SRC-0007 — Scholar registry minimum population
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-004
- Rule: scholar_authority.count must be at least 50 before the first pipeline run begins.

### INV-SRC-0008 — PDF-derived text is never silently trusted at source handoff
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md and the 2026-04-14 architecture decision that normalization owns PDF-to-text conversion
- Rule: No PDF-derived text may be treated as normalized source text by the source engine; every PDF handoff must carry source_metadata.pdf_text_layer_status and source_metadata.normalization_route=pdf_ocr_primary.

### INV-SRC-0009 — Zero knowledge loss in all source-engine output
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner directive 2026-04-14. The library NEVER hides, compresses, or simplifies knowledge. Full exhaustiveness and extensiveness in all output. This is a project-wide core rule that applies to every engine and every agent.
- Rule: Every source-engine output preserves the full evidence chain, all considered positions, all reasoning, and all uncertainty. No metadata field, dispute, risk, or finding is hidden, compressed, or simplified in the output. When multiple positions exist, all positions are preserved with their evidence and confidence. When a most-likely resolution exists, it is highlighted but the alternatives are never removed.

### INV-SRC-0010 — Holding-level completeness is computed, not asserted
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15). The DR identifies that source-level completeness_status (per uploaded artifact) and holding-level completeness (what the library holds for an edition group) are distinct signals. Source-level completeness is immutable history about each source. Holding-level completeness must be recomputed whenever a volume is added or removed from a holding. Stamping 'complete' on a source and treating it as library-wide truth produces stale data as the collection evolves.
- Rule: EditionHolding completeness_state is always derived from the current set of attached VolumeHoldings, never stored as a static assertion. When a volume is attached, detached, superseded, or has its presence_state changed, the holding's completeness_state is recomputed. Source-level completeness_status (from REQ-SRC-0036) remains immutable and records what was true about each individual source at intake time. The two completeness signals are never conflated.

### INV-SRC-0011 — Source engine must not infer level from shallow metadata
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-1. Hardened on 2026-04-17 by the 3-of-3 unanimous adjudication (Codex CLI architectural-fit, Gemini CLI runs 1 and 2 classical- defensibility at 6-0 branch win counts, Gemini DR T-2 threat model) that closed DEC-SRC-0003 on OPT-B. Acceptance criterion AC-4 (positive assertion that level_status is still populated when level is null) is added to complement the null-assertion clauses in AC-1 and AC-2. Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-3 in the CON-SRC-0011 classical WorkLevel vocabulary (mutawassiṭ), replacing the earlier English placeholder "intermediate" which would fail the enum whitelist at REQ-SRC-0047 intake validation. Rule statement and implication are unchanged; the amendment is confined to the acceptance criterion surface.
- Rule: The source engine MUST NOT compute or infer the level field of SourceMetadata from title tokens, series cues, publisher metadata, or any shallow bibliographic signal. The level field remains null unless an explicit owner_level_override is provided at intake. This invariant does NOT restrict the `level_status` field (CON-SRC-0004), which is a processing-state enum — not a pedagogical-level inference — and whose emission is governed by CON-SRC-0004 alone.

### INV-SRC-0012 — Non-applicable genres require level null
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-reports/dr-chatgpt-level-detection-20260416.yaml (SEC-2). Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-1 through AC-4 in the CON-SRC-0011 classical WorkLevel vocabulary (mubtadiʾ, muntahī, mutawassiṭ, muntahī respectively). AC-4's "specialist" placeholder has no fourth-tier equivalent in the three-tier CON-SRC-0011 enum; "muntahī" is the semantic replacement preserving the topmost-tier-override rejection intent. Rule statement, rationale, implication, and violation_severity are unchanged. The non-applicable genre set listed in the rule statement still lags behind CON-SRC-0004's seven-value frozenset (four of seven values are not yet in the Genre enum — see NON_APPLICABLE_GENRE_VALUES in contracts.py); reconciliation is tracked as Phase 5b item 4.
- Rule: For genres where the reading-level concept does not apply — mushaf, hadith_collection, rijal_dictionary, and majmu — the source engine MUST serialize SourceMetadata.level as null regardless of any owner override attempt. Forcing a reading-level label onto these genres creates false scholarly authority because their organizing principle is transmission, reference, or compilation, not graduated pedagogical exposition.
