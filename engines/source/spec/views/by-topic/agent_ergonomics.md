# Source Spec Atoms by Topic: agent_ergonomics

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| DEC-SRC-0008 | decision | Agent infrastructure is built within source-engine scope first | confirmed | medium |
| DEC-SRC-0009 | decision | Research strategy uses specialized sources | confirmed | high |
| DEC-SRC-0013 | decision | Deliberation cell architecture with deterministic orchestrator | confirmed | critical |
| OF-SRC-0016 | feedback | Research must use specialized source channels | confirmed | high |
| OQ-SRC-0003 | question | Agent-team architecture design | superseded | critical |
| OQ-SRC-0005 | question | Agent monitoring scope | superseded | medium |
| OQ-SRC-0007 | question | Specialized research source inventory | superseded | medium |
| REQ-SRC-0013 | requirement | Specialized research agents | confirmed | high |
| REQ-SRC-0028 | requirement | Case complexity assessment and deliberation routing | confirmed | critical |
| REQ-SRC-0029 | requirement | Monitor feedback with non-recursive constraint | confirmed | high |

### DEC-SRC-0008 — Agent infrastructure is built within source-engine scope first
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0015
- Chosen option: OPT-A — Build within source engine scope first
- Decision rationale: The owner explicitly prioritized building the best possible source-engine scope first.

### DEC-SRC-0009 — Research strategy uses specialized sources
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0016; amended per both coworker reviews and Gemini DR on Islamic scholarly metadata verification sources (2026-04-14) which resolved OQ-SRC-0007 with a concrete curated inventory.
- Chosen option: OPT-B — Canonical specialized source categories
- Decision rationale: This gives REQ-SRC-0013 a stable source-type taxonomy. The concrete inventory was resolved by Gemini DR (OQ-SRC-0007 superseded). Key sources per category are now curated in REQ-SRC-0013 preconditions with access modalities documented.

### DEC-SRC-0013 — Deliberation cell architecture with deterministic orchestrator
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR report on agent-team architecture (2026-04-14). Resolves OQ-SRC-0003. The DR evaluated fixed roles, dynamic composition, and hierarchical escalation, recommending dynamic composition with fixed minimums under a deterministic orchestrator. Phase 5 amendment 2026-04-30 (scholar-matching DR synthesis §5.4): add scholar_match_cell as a NAMED deliberation-cell pattern. Stage-1 (deterministic narrowing per REQ-SRC-0051) is the orchestrator role; Stage-2 (≥2 verifier consensus per REQ-SRC-0052) is the verifier-cell role. Round-cap and disagreement protocol per REQ-SRC-0008 Phase 5 amendment + REQ-SRC-0053. Cross- references: CON-SRC-0008 (output contract), CON-SRC-0009 (evidence packet contract), REQ-SRC-0049 (snapshot locking), INV-SRC-0013 (≥2-non-name floor), INV-SRC-0014 (matching-key honorific exclusion), INV-SRC-0015 (provenance completeness), INV-SRC-0016 (chosen_id closure), INV-SRC-0017 (snapshot version pin). The scholar_match_cell is the second NAMED instance of the generic deliberation-cell pattern (the first is the trust evaluation cell from REQ-SRC-0008).
- Chosen option: OPT-B — Deterministic orchestrator with deliberation cells
- Decision rationale: Smallest system that enforces independence, produces evidence-traceable outputs, guarantees bounded disagreement loops, supports fast-track without bypassing logging, and produces always-valid output shapes. Deterministic orchestration avoids the LLM supervisor single-point-of-failure problem while maintaining the agent team's deliberative power. Phase 5 amendment 2026-04-30: the cell pattern is now explicitly EXTENSIBLE — scholar_match_cell is the second named instance, demonstrating that the pattern accommodates domain specialization (compound 4-condition threshold per REQ-SRC-0053; hybrid round-0 / round-1 protocol per REQ-SRC-0052; F-4 hallucination closure per INV-SRC-0016) without architectural changes to DEC-SRC-0013's orchestrator core.

### OF-SRC-0016 — Research must use specialized source channels
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 4 question 4
- Interview question: What kind of research capability does the source engine need?
- Owner answer: Research should be much more accurate than generic web search. Dedicated agents should cover general web, specific scholarly sources, and well-defined reference databases.

### OQ-SRC-0003 — Agent-team architecture design
- Type: question
- Layer: questions
- Step: n/a
- Status: superseded
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009. Resolved by ChatGPT DR on agent-team architecture (2026-04-14). Answer formalized in DEC-SRC-0013, REQ-SRC-0028, REQ-SRC-0029.
- Candidates:
  - OPT-A: Fixed roles (likely)
  - OPT-B: Dynamic composition (possible)
  - OPT-C: Hierarchical escalation (possible)

### OQ-SRC-0005 — Agent monitoring scope
- Type: question
- Layer: questions
- Step: n/a
- Status: superseded
- Priority: medium
- Confidence: high
- Source: Resolved 2026-04-29 by Codex CLI structural adjudication against confirmed source-engine-local monitor atoms DEC-SRC-0004, DEC-SRC-0013, REQ-SRC-0008, REQ-SRC-0028, and REQ-SRC-0029; original question derived from OF-SRC-0009 and previously narrowed per contract-architect-review.yaml.
- Candidates:
  - OPT-A: Source-engine monitors (possible)
  - OPT-B: Pipeline-wide monitors (likely)
  - OPT-C: Per-book monitors (unlikely)

### OQ-SRC-0007 — Specialized research source inventory
- Type: question
- Layer: questions
- Step: n/a
- Status: superseded
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0016. Resolved by Gemini DR on Islamic scholarly metadata verification sources (2026-04-14). OPT-B (curated scholarly inventory) chosen. Concrete inventory formalized in amendments to REQ-SRC-0013 and DEC-SRC-0009.
- Candidates:
  - OPT-A: Web plus Usul.ai (possible)
  - OPT-B: Curated scholarly inventory (likely)
  - OPT-C: Dynamic discovery (unlikely)

### REQ-SRC-0013 — Specialized research agents
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0016; amended per contract-architect-review.yaml and Gemini DR on Islamic scholarly metadata verification sources (2026-04-14) which provides a concrete curated inventory per source_type category.
- Trigger: The engine dispatches research work for metadata verification.
- Postconditions:
  - High-impact fields author, genre, science_scope, and death_date use at least two distinct research_task.source_type values.
  - Every dispatch writes verification_log with field, source_types, source_count, and completed_at.
  - Non-high-impact fields may use fewer than two source types.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/08_death_date/book.htm with research_task.field="death_date"; When research dispatch executes; Then verification_log.field="death_date" and len(verification_log.source_types) is at least 2..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/04_hadith/book.htm with research_task.field="author"; When research dispatch executes; Then verification_log.source_types is a subset of {general_web, scholarly_database, manuscript_catalog, islamic_reference, library_catalog}..
  - AC-3 [deterministic] Given A research task with field="author" and only source_type=general_web available; When research dispatch executes; Then verification_log.status="incomplete_specialized_sources"..

### REQ-SRC-0028 — Case complexity assessment and deliberation routing
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR report on agent-team architecture (2026-04-14). Defines three routing paths based on case complexity signals. The source engine classifies PDF text quality but does NOT perform OCR — degraded-evidence path means limited internal evidence requiring heavier external research, not OCR processing. Phase 5 amendment 2026-04-30 (scholar- matching DR synthesis §5.4): add partial_fragment_author_ identity as a routing signal that FORCES standard path (not fast_track) even when a provisional scholar exists in scholar_authority. Provisional scholars under unresolved ambiguity MUST run the full match cell (REQ-SRC-0049 through REQ-SRC-0053) regardless of other fast_track predicates. This aligns with INV-SRC-0013 ≥2-non-name floor and the no-definitive-from-under-spec rule.
- Trigger: The orchestrator begins metadata deliberation for a source candidate.
- Postconditions:
  - case_complexity is set to one of fast_track, standard, or degraded_evidence.
  - fast_track requires all of: scholar_authority[author_canonical_id].authority_level >= primary, genre in {matn, sharh, hadith_collection, tafsir}, author_death_hijri is not null, AND partial_fragment_author_identity is false (Phase 5 amendment 2026-04-30 — fast_track is BLOCKED when the dossier signals an under-specified scholar fragment whose match cell has not yet finalized).
  - partial_fragment_author_identity is true when the dossier carries an author fragment that REQ-SRC-0050 normalizes into ≤1 non-name attribute, or when scholar_authority lookup returns a provisional record (status=provisional per ScholarAuthorityRecord.status) for the canonical_id, or when the dossier-level INV-SRC-0013 ≥2-non-name floor is unmet. Such cases MUST use trust_path=full_deliberation regardless of other fast_track predicates.
  - degraded_evidence is set when intake_dossier.source_format=pdf and intake_dossier.pdf_text_layer_status in {absent, corrupt}, or when intake_dossier.integrity_status=suspicious.
  - standard is the default when neither fast_track nor degraded_evidence applies.
  - fast_track path uses 2 independent verification reasoners, optional minimal research, and monitor. Research depth is reduced but verification independence is not.
  - standard path uses 2+ specialized research agents with distinct source_type values, 2 independent verification reasoners, disagreement resolver, and monitor.
  - degraded_evidence path expands research dispatch to 3+ source types to compensate for weak internal evidence. Verification reasoner count remains exactly 2.
  - case_complexity_record preserves the routing decision and the signals that determined it.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/05_tafsir/book.htm with definitive author attribution and author_death_hijri=774; When case complexity assessment runs; Then case_complexity="fast_track"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre="risalah" and a modern author; When case complexity assessment runs; Then case_complexity="standard"..
  - AC-3 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf with pdf_text_layer_status="corrupt"; When case complexity assessment runs; Then case_complexity="degraded_evidence"..
  - AC-4 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf with pdf_text_layer_status="absent"; When case complexity assessment runs; Then case_complexity="degraded_evidence"..

### REQ-SRC-0029 — Monitor feedback with non-recursive constraint
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: ChatGPT DR report on agent-team architecture (2026-04-14). Defines monitor feedback as a structured non-recursive observation record. The monitor audits and scores but never triggers in-run reruns.
- Trigger: A deliberation cell completes processing for any metadata field or trust evaluation.
- Postconditions:
  - A monitor_feedback record is written with non-null case_id, source_id, field, trust_path, and completed_at.
  - monitor_feedback.evidence_coverage records whether high-impact fields used at least 2 distinct source_type values.
  - monitor_feedback.independence_check records whether verification reasoners had distinct agent_id values and did not read each other's outputs before emitting.
  - monitor_feedback.uncertainty_flags records whether multi-position output was emitted, whether OCR-unreliable sources contributed, and whether confidence ordering was applied.
  - monitor_feedback.spec_violations records any blocking or fatal violations detected during the run.
  - monitor_feedback.suggested_policy_updates records non-blocking improvement suggestions as structured entries.
  - The monitor CANNOT trigger a rerun of the same case. Reruns happen only when a requirement's error condition mandates it.
  - monitor_feedback is written even for fast_track cases.
- Acceptance criteria:
  - AC-1 [integration] Given A fast_track trust evaluation that completes successfully; When monitor feedback runs; Then monitor_feedback.trust_path="fast_track" and monitor_feedback.case_id is non-null..
  - AC-2 [deterministic] Given A standard author attribution where one research source_type was used for a high-impact field; When monitor feedback runs; Then monitor_feedback.evidence_coverage.meets_minimum=false and monitor_feedback.spec_violations includes SRC-E-INCOMPLETE-RESEARCH..
  - AC-3 [deterministic] Given A completed deliberation cell where the monitor emits a suggested_policy_update; When the same case is checked for reruns; Then No rerun is triggered by the monitor's suggestion. The suggestion is stored as a future policy ticket only..
