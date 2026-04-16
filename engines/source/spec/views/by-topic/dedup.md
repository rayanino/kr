# Source Spec Atoms by Topic: dedup

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0018 | decision | Sources are immutable; collection entries evolve | confirmed | critical |
| DEC-SRC-0019 | decision | Mixed-edition volumes never silently produce a coherent edition holding | confirmed | critical |
| DEC-SRC-0020 | decision | Supersession is pointer-based, not deletion-based | confirmed | critical |
| INV-SRC-0010 | invariant | Holding-level completeness is computed, not asserted | confirmed | critical |
| REQ-SRC-0044 | requirement | Edition-group and holding reconciliation on source admission | confirmed | critical |
| REQ-SRC-0045 | requirement | Supersession signal emission on source admission | confirmed | high |

### DEC-SRC-0018 — Sources are immutable; collection entries evolve
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15). FRBR/IFLA LRM separates abstract content from concrete carriers. Fedora/DSpace repositories keep immutable versions and expose 'latest' pointers without deleting history. KR's existing invariant (frozen sources are immutable) and INV-SRC-0003 (library never refuses knowledge) together require that collection membership evolves without mutating the carrier layer. The DR identifies this as the structural resolution to incremental volumes, supersession, and mixed-edition handling.
- Chosen option: OPT-B — Attach immutable sources to evolving collection entries (holdings)
- Decision rationale: Satisfies immutability (sources untouched), INV-SRC-0003 (nothing refused), INV-SRC-0009 (all evidence preserved), and enables progressive completeness tracking. The 'attach not merge' principle is the minimum mechanism that handles all six DR edge cases (incremental volumes, duplicate editions, mixed editions, supersession, partial-of-complete, composite evolution).

### DEC-SRC-0019 — Mixed-edition volumes never silently produce a coherent edition holding
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15), Edge Case 3. Silent mixing of editions is dangerous in Islamic scholarly study because citations, page numbers, and tahqiq notes differ by edition. Mixing breaks scholarly reliability. The DR recommends either two separate holdings or one holding explicitly marked as ActiveMixed with a study-quality warning.
- Chosen option: OPT-B — Separate mixed editions into distinct holdings with explicit warning
- Decision rationale: Preserves scholarly reliability by keeping edition-coherent holdings separate. INV-SRC-0003 (never refuse knowledge) is respected because both editions are admitted. INV-SRC-0009 (zero knowledge loss) is respected because the mixing evidence is preserved, not hidden. The ActiveMixed state provides usability without false coherence claims.

### DEC-SRC-0020 — Supersession is pointer-based, not deletion-based
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15), Edge Case 4. Fedora API specification requires resource versioning via the Memento protocol where an Original Resource can have multiple immutable Mementos listed in a TimeMap. DSpace's item-level versioning treats each version as a separate item with a base identifier pointing to the most recent version while older versions remain accessible and citable. Both models align with KR's immutability and zero-knowledge-loss invariants.
- Chosen option: OPT-B — Pointer-based supersession with configurable regeneration policy
- Decision rationale: Preserves full history (Fedora/Memento model), enables DSpace-style 'only most recent in search, older still accessible', and avoids compute explosion by making regeneration conditional on actual text-quality impact. Satisfies all three governing invariants (immutability, never-refuse, zero-loss) simultaneously.

### INV-SRC-0010 — Holding-level completeness is computed, not asserted
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15). The DR identifies that source-level completeness_status (per uploaded artifact) and holding-level completeness (what the library holds for an edition group) are distinct signals. Source-level completeness is immutable history about each source. Holding-level completeness must be recomputed whenever a volume is added or removed from a holding. Stamping 'complete' on a source and treating it as library-wide truth produces stale data as the collection evolves.
- Rule: EditionHolding completeness_state is always derived from the current set of attached VolumeHoldings, never stored as a static assertion. When a volume is attached, detached, superseded, or has its presence_state changed, the holding's completeness_state is recomputed. Source-level completeness_status (from REQ-SRC-0036) remains immutable and records what was true about each individual source at intake time. The two completeness signals are never conflated.

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
