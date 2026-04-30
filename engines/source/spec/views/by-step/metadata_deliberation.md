# Source Spec Atoms by Step: metadata_deliberation

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0002 | requirement | Optional owner hints as cross-validation | confirmed | high |
| REQ-SRC-0003 | requirement | Metadata deliberation stays owner-light | confirmed | critical |
| REQ-SRC-0004 | requirement | Multi-model consensus for author attribution | confirmed | critical |
| REQ-SRC-0005 | requirement | Optional science hint | confirmed | medium |
| REQ-SRC-0006 | requirement | Growable science registry without owner gate | confirmed | high |
| REQ-SRC-0008 | requirement | Agent-team trust evaluation | confirmed | critical |
| REQ-SRC-0009 | requirement | Agent self-resolution of disagreements | confirmed | critical |
| REQ-SRC-0010 | requirement | Graduated muhaqiq standing | confirmed | medium |
| REQ-SRC-0011 | requirement | Fine-grained hadith classification | confirmed | high |
| REQ-SRC-0012 | requirement | Multi-position metadata for disputed fields | confirmed | high |
| REQ-SRC-0013 | requirement | Specialized research agents | confirmed | high |
| REQ-SRC-0014 | requirement | Copyist and author disambiguation | confirmed | critical |
| REQ-SRC-0015 | requirement | Scholar identity matching and name resolution | confirmed | critical |
| REQ-SRC-0016 | requirement | Multi-science assignment | confirmed | high |
| REQ-SRC-0026 | requirement | Authoritative work identity and collection linkage output | confirmed | critical |
| REQ-SRC-0028 | requirement | Case complexity assessment and deliberation routing | confirmed | critical |
| REQ-SRC-0029 | requirement | Monitor feedback with non-recursive constraint | confirmed | high |
| REQ-SRC-0030 | requirement | Genre classification | confirmed | critical |
| REQ-SRC-0031 | requirement | Multi-layer hint detection | confirmed | critical |
| REQ-SRC-0032 | requirement | Structural format classification | confirmed | critical |
| REQ-SRC-0034 | requirement | Compiler-as-muhaqiq detection | confirmed | critical |
| REQ-SRC-0035 | requirement | Display metadata for teaching units (source card) | confirmed | high |
| REQ-SRC-0039 | requirement | Work-to-work relationship modeling | confirmed | high |
| REQ-SRC-0040 | requirement | Attribution confidence levels with scholarly terminology | confirmed | high |
| REQ-SRC-0042 | requirement | Scholar profile lookup for display card | confirmed | high |
| REQ-SRC-0043 | requirement | New scholar registration in authority registry | confirmed | high |
| REQ-SRC-0049 | requirement | Scholar registry snapshot locking for match-call duration | confirmed | critical |
| REQ-SRC-0050 | requirement | Scholar fragment normalization and 5-component parsing | confirmed | critical |
| REQ-SRC-0051 | requirement | Deterministic scholar candidate generation with work-title channel | confirmed | critical |
| REQ-SRC-0052 | requirement | Scholar match verification cell with hybrid round-0 / round-1 protocol | confirmed | critical |
| REQ-SRC-0053 | requirement | Scholar disagreement routing with compound 4-condition threshold | confirmed | critical |

### REQ-SRC-0002 — Optional owner hints as cross-validation
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0002; amended per contract-architect-review.yaml and adversary-review.yaml ADV-007
- Trigger: The owner submits optional intake hints together with a source path.
- Postconditions:
  - owner_hint_payload values are stored separately from inferred_metadata values.
  - Matching author_name hints may increase author_identification_confidence without changing inferred_metadata.author_name.
  - Matching genre hints may increase genre_confidence without changing inferred_metadata.genre.
  - Matching science_scope hints may increase science_scope_confidence without changing inferred_metadata.science_scope.
  - source_metadata.hint_comparison_results appends one record per compared hint with fields hint_field, hint_value, inferred_value, match, and confidence_delta.
  - Hint contradictions write hint_investigation with fields field, hint_value, inferred_value, status, and opened_reason.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/03_fiqh/book.htm with owner_hint_payload.author_name="عبد الله بن إبراهيم الزاحم"; When post-inference hint comparison executes; Then inferred_metadata.author_name remains "عبد الله بن إبراهيم الزاحم", author_identification_confidence increases, and source_metadata.hint_comparison_results contains a record with hint_field="author_name", hint_value="عبد الله بن إبراهيم الزاحم", inferred_value="عبد الله بن إبراهيم الزاحم", and match=true..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with owner_hint_payload.genre="matn"; When post-inference hint comparison executes; Then hint_investigation.field="genre", hint_investigation.hint_value="matn", inferred_metadata.genre remains "risalah", and source_metadata.hint_comparison_results contains a record with hint_field="genre", hint_value="matn", inferred_value="risalah", and match=false..
  - AC-3 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with owner_hint_payload.publisher="دار الفكر"; When hint payload validation executes; Then The invalid hint key is rejected with error_code=SRC-E-HINT-FIELD and base inference still runs..

### REQ-SRC-0003 — Metadata deliberation stays owner-light
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
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

### REQ-SRC-0004 — Multi-model consensus for author attribution
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0004; amended per coworker reviews, adversary-review ADV-009, and author-attribution review (ADV-ATT-005/007/011/012). Status values renamed to avoid collision with REQ-SRC-0040 scholarly terminology. Death date verification enum completed. Co-authorship status added. Correlated hallucination guard for modern scholars.
- Trigger: The source engine must assign or preserve author attribution for a source.
- Postconditions:
  - author_output.status is one of: agent_consensus (agents agree on one author), agent_disagreement (agents disagree — multiple positions preserved), agent_no_evidence (no evidence-backed position from any agent), or co_authored (multiple authors genuinely co-wrote the work, indicated by conjunctive markers like و between names or تأليف X و Y).
  - Each author_output.positions item contains position, display_name, death_hijri, death_hijri_verification, nisba_tokens, evidence, confidence, source_agent, and entity_type (person or institution).
  - An agent_consensus case stores one chosen position. An agent_disagreement case preserves all evidence-backed positions. A co_authored case lists all co-authors as non-competing positions.
  - death_hijri_verification enum: single_model_unverified (one agent only), multi_agent_agreed (two+ agents agree), database_verified (confirmed from structured database like Dorar.net or OpenITI), colophon_extracted (directly from source colophon text).
  - Correlated hallucination guard: for scholars with death_hijri > 1300, two-LLM agreement alone is insufficient. Death dates for modern scholars MUST be verified against at least one structured database (Dorar.net API, OpenITI, Shamela metadata). When no database confirms, death_hijri_verification is set to consensus_unverified (a level between single_model_unverified and database_verified).
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm and two independent attribution agents; When author attribution executes; Then author_output.status="agent_consensus" and author_output.positions[0].position="عبد الله بن إبراهيم الزاحم"..
  - AC-2 [integration] Given A disputed authorship case with two evidence-backed candidates for the same source; When author attribution executes; Then author_output.status="agent_disagreement" and len(author_output.positions) is at least 2..
  - AC-3 [deterministic] Given Candidate authors "أحمد بن عبد الحليم بن تيمية الحراني" (death_hijri=728) and "عبد السلام بن عبد الله بن تيمية" (death_hijri=652) with evidence mentioning الحراني and post-700H content; When author attribution executes; Then The selected position matches death_hijri=728 and nisba_tokens contains "الحراني"..
  - AC-4 [integration] Given A source whose metadata card, title, and colophon provide no author evidence; When author attribution executes with two independent agents; Then author_output.status="agent_no_evidence" and study_quality_risk_flags includes "zero_author_evidence"..
  - AC-5 [deterministic] Given An author position whose death_hijri=676 is inferred by exactly one independent attribution agent; When author attribution executes; Then author_output.positions[0].death_hijri=676, author_output.positions[0].death_hijri_verification="single_model_unverified", and the death date remains pending confirmation from a second independent agent..

### REQ-SRC-0005 — Optional science hint
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0005; amended per contract-architect-review.yaml
- Trigger: The owner supplies science_scope as an optional intake hint.
- Postconditions:
  - Exact science_scope matches may increase science_scope_confidence without changing inferred_metadata.science_scope.
  - Contradictions write hint_investigation with field=science_scope and preserve both hint and inference values.
  - Science hints never replace the inferred science_scope list.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/04_hadith/book.htm with owner_hint_payload.science_scope=["hadith"]; When science-hint comparison executes; Then inferred_metadata.science_scope remains ["hadith"] and science_scope_confidence increases..
  - AC-2 [integration] Given tests/fixtures/shamela_real/10_no_author/book.htm with owner_hint_payload.science_scope=["tafsir"]; When science-hint comparison executes; Then hint_investigation.field="science_scope", hint_investigation.hint_value=["tafsir"], and inferred_metadata.science_scope remains ["hadith", "fiqh"]..

### REQ-SRC-0006 — Growable science registry without owner gate
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006; amended on 2026-04-14 to align with the owner rule that metadata should not depend on human gates.
- Trigger: Science classification yields a science label not present in science_registry.
- Postconditions:
  - Existing science labels classify normally without registry expansion.
  - New science labels write registry_expansion_request with candidate_science and status=autonomous_review_pending.
  - Autonomous verification may resolve the candidate science as accepted_new_label, merged_into_existing_label, or insufficient_evidence.
  - Source admission remains accepted while the science expansion workflow is pending or disputed.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When science classification executes; Then inferred_metadata.science_scope=["fiqh"] and no registry_expansion_request is written..
  - AC-2 [integration] Given A source whose inferred_metadata.science_scope=["mustalah_al_hadith"] while science_registry lacks that label; When science classification executes; Then registry_expansion_request.candidate_science="mustalah_al_hadith" and registry_expansion_request.status="autonomous_review_pending"..
  - AC-3 [deterministic] Given A pending registry_expansion_request for mustalah_al_hadith that autonomous review cannot yet settle; When registry expansion handling executes; Then registry_expansion_request.status="insufficient_evidence" and source admission remains accepted_with_flags..

### REQ-SRC-0008 — Agent-team trust evaluation
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0009; amended per both coworker reviews, adversary-review.yaml ADV-003, and ChatGPT DR on agent-team architecture (2026-04-14) which recommends extending trust_decision to support disputed status with positions array. Phase 5 amendment 2026-04-30 (scholar-matching DR synthesis §5.4 + §2.3 Pivot (c) HYBRID adjudication): specialize verifier-cell rules for scholar-matching cell — round-cap = 2; round-0 no-peeking + different prompts; round-1 adversarial scaffold ONLY if round-0 diverges; no new candidates in round-1 (per CON-SRC-0009 immutability + INV-SRC-0016 chosen_id closure). Tighten: trust_decision.positions per-position carries cited_evidence (list[CitationRef]) for scholar-matching deliberations.
- Trigger: The engine must emit a trust_decision for a source or metadata claim.
- Postconditions:
  - trust_decision contains decision, trust_path, supporting_agents, and evidence_summary fields.
  - trust_decision.decision is one of verified, needs_review, or disputed.
  - trust_decision.decision=disputed is set when independent trust verifiers produce evidence-backed competing trust assessments that do not converge after the disagreement protocol. In this case trust_decision.positions preserves both assessments with evidence and confidence, ordered by confidence descending.
  - Every run writes monitor_feedback records even when the case follows the fast_track path.
  - Books meeting all fast_track predicates may use trust_path=fast_track instead of full_deliberation.
  - Scholar-matching cell specialization (Phase 5 amendment 2026-04-30): when this trust evaluation operates as the scholar_match_cell pattern (per DEC-SRC-0013 amendment), the verifier independence rules are specialized: (a) round-cap = 2 (no rounds beyond round-1); (b) round-0 uses no-peeking + different reasoning prompts (functional independence); (c) round-1 uses adversarial scaffold (one verifier defends round-0 leader, the other attacks) ONLY if round-0 diverges; (d) round-1 cannot introduce new candidates — chosen_id MUST remain in CON-SRC-0009.candidate_set per INV-SRC-0016 closure invariant; (e) trust_decision.positions per-position MUST carry cited_evidence (list[CitationRef]) bound to the source_book_ids referenced in scholar_authority.evidence_sources.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/05_tafsir/book.htm with definitive author attribution, scholar_authority[author_canonical_id].authority_level="primary", and author_death_hijri=774; When trust evaluation executes; Then trust_decision.trust_path="fast_track" and trust_decision.decision="verified"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When trust evaluation executes; Then trust_decision includes decision, trust_path, supporting_agents, and evidence_summary, and at least one monitor_feedback record is written..
  - AC-3 [deterministic] Given A trust evaluation run with only one verification agent available; When trust evaluation executes; Then Finalization aborts with error_code=SRC-E-TRUST-AGENT-COUNT..
  - AC-4 [deterministic] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre="risalah" or author_death_hijri=null; When trust evaluation executes; Then trust_decision.trust_path="full_deliberation"..

### REQ-SRC-0009 — Agent self-resolution of disagreements
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0011; amended per contract-architect-review.yaml, adversary-review.yaml ADV-005/ADV-012, and ChatGPT DR on agent-team architecture (2026-04-14) which specifies the structured round protocol.
- Trigger: Independent agents disagree about a metadata field.
- Postconditions:
  - disagreement_case.resolution_state is set to resolved_error or genuine_scholarly_dispute.
  - resolved_error writes one corrected value and structured failure_analysis for the losing agent.
  - genuine_scholarly_dispute delegates the field to the REQ-SRC-0012 multi-position schema.
  - When disagreement_case.round_count reaches 3 without convergence on resolved_error, disagreement_case.resolution_state defaults to genuine_scholarly_dispute and emits REQ-SRC-0012 output.
  - Each round follows a structured protocol where each verification agent receives the other agent's position and evidence traces, then emits a steelman of the other position, a list of attack points with evidence, at most 2 targeted research requests, and a revised position.
  - Convergence is detected mechanically by the orchestrator when both agents emit the same canonicalized output and the winning position's evidence list is non-empty.
  - When one agent's evidence becomes empty while the other remains evidence-backed, the case resolves as resolved_error rather than genuine_scholarly_dispute.
  - failure_analysis for resolved_error must include error_type, what_missed, corrective_evidence, and guardrail_suggestion fields.
- Acceptance criteria:
  - AC-1 [integration] Given A disagreement where one agent treats "إعداد" as author evidence and another agent corrects it to compiler evidence; When disagreement resolution executes; Then disagreement_case.resolution_state="resolved_error" and the corrected metadata field is stored as a single resolved value..
  - AC-2 [integration] Given A disputed authorship case with two evidence-backed positions from independent agents; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..
  - AC-3 [deterministic] Given A resolved_error case with one losing agent; When disagreement resolution finalizes; Then failure_analysis.agent_id is recorded and linked to disagreement_case.case_id..
  - AC-4 [deterministic] Given A disagreement that remains unresolved after disagreement_case.round_count=3; When disagreement resolution executes; Then disagreement_case.resolution_state="genuine_scholarly_dispute" and the output field uses the REQ-SRC-0012 positions array..

### REQ-SRC-0010 — Graduated muhaqiq standing
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0010; amended per both coworker reviews
- Trigger: The engine researches the muhaqiq for an edition.
- Postconditions:
  - muhaqiq_assessment stores standing_level, evidence_sources, and last_verified.
  - standing_level is one of unknown, barely_known, known, well_known, or elite.
  - Unknown or low standing never blocks source intake.
- Acceptance criteria:
  - AC-1 [deterministic] Given A muhaqiq research result with zero verified evidence sources; When muhaqiq standing assessment executes; Then muhaqiq_assessment.standing_level="unknown", muhaqiq_assessment.evidence_sources=[], and muhaqiq_assessment.last_verified is populated..
  - AC-2 [deterministic] Given A muhaqiq research result with one verified library_catalog source; When muhaqiq standing assessment executes; Then muhaqiq_assessment.standing_level="barely_known"..
  - AC-3 [deterministic] Given A muhaqiq research result with verified sources from scholarly_database, library_catalog, islamic_reference, and general_web; When muhaqiq standing assessment executes; Then muhaqiq_assessment.standing_level="elite" and len(muhaqiq_assessment.evidence_sources)=4..

### REQ-SRC-0011 — Fine-grained hadith classification
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012; amended per both coworker reviews and domain-validator-review-2 (DV-001, DV-016) which found 6 missing hadith subgenres and clarified genre/subgenre orthogonality.
- Trigger: A source is identified as hadith literature or adjacent hadith scholarship.
- Postconditions:
  - hadith_subgenre is written for every hadith or hadith-adjacent source.
  - Ambiguous cases preserve candidate_subgenres instead of collapsing to generic hadith_collection.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/04_hadith/book.htm; When hadith classification executes; Then hadith_subgenre="juz"..
  - AC-2 [deterministic] Given A tabaqat/rijal work about hadith narrators; When hadith classification executes; Then hadith_subgenre="tabaqat_rijal" and not "hadith_commentary"..
  - AC-3 [deterministic] Given One collection organized by companion narrator names and one collection organized by fiqh chapters; When hadith classification executes; Then The first source receives hadith_subgenre="musnad" and the second receives hadith_subgenre="sunan"..

### REQ-SRC-0012 — Multi-position metadata for disputed fields
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Trigger: The engine encounters a metadata field with genuine scholarly disagreement.
- Postconditions:
  - disputed_field.positions is an array of objects with keys position, evidence, confidence, and source_agents.
  - Every positions item has confidence between 0.0 and 1.0 and a non-empty evidence list.
  - The engine never forces one canonical value when disputed_field.positions contains two or more evidence-backed items.
- Acceptance criteria:
  - AC-1 [integration] Given A disputed authorship case with supported positions "ابن القيم" and "ابن تيمية"; When metadata finalization executes; Then disputed_field.positions contains two objects and each object includes position, evidence, confidence, and source_agents..
  - AC-2 [deterministic] Given A disputed metadata field with two evidence-backed positions; When metadata finalization executes; Then Every disputed_field.positions[*].confidence is between 0.0 and 1.0 and every disputed_field.positions[*].evidence list is non-empty..

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

### REQ-SRC-0014 — Copyist and author disambiguation
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from domain-validator-review.yaml; amended per adversary-review.yaml ADV-006 and Claude DR spec audit 2026-04-15 which identified إعداد as a distinct role (neither author nor editor).
- Trigger: Attribution parsing reads a metadata card or colophon with or without role-bearing name signals.
- Postconditions:
  - author_name is populated only from author markers.
  - compiler_name is populated only from compiler markers.
  - preparer_name is populated only from preparer markers.
  - copyist_name is populated only from copyist markers.
  - editor_name is populated only from editor markers.
  - When no explicit role markers appear in metadata or colophon, metadata_card.author is assigned to author_name by default.
  - confirmed_dual_role mechanical criteria: the same name in both author and editor roles is set to confirmed_dual_role (not attribution_role_conflict) when at least one of: (a) title page explicitly states تأليف وتحقيق or a combined formula, (b) temporal impossibility of being different people (same death_hijri for both roles), (c) research agent confirms the scholar is known to self-edit their own works.
- Acceptance criteria:
  - AC-1 [deterministic] Given Colophon text "كتبه الفقير العبد عبد الله بن محمد"; When attribution parsing executes; Then copyist_name="عبد الله بن محمد" and author_name remains null..
  - AC-2 [deterministic] Given Metadata card text "ألفه محمد بن عبد الوهاب"; When attribution parsing executes; Then author_name="محمد بن عبد الوهاب"..
  - AC-3 [deterministic] Given Metadata card author field "ابن قدامة" with no colophon role markers; When attribution parsing executes; Then author_name="ابن قدامة"..

### REQ-SRC-0015 — Scholar identity matching and name resolution
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from domain-validator-review.yaml; amended per adversary-review.yaml ADV-010, adversary-attribution review (ADV-ATT-001/002/006/012), domain-attribution review (laqab-as-primary, nisba, sahib convention, death date tolerance, female scholars), and contract-attribution review (display_name precedence).
- Trigger: Attribution matching compares two Arabic scholar names or resolves a scholar identity.
- Postconditions:
  - canonical_match_name excludes stripped honorific tokens and any stripped leading kunya segment.
  - display_name preserves the original honorific-bearing form from the source record.
  - display_name selection rule: when multiple sources provide different valid forms, display_name defaults to the shortest commonly recognized form (الشهرة). full_name_lineage always stores the longest unabridged form. Disagreement on display_name form (not identity) is NOT a substantive disagreement and must not trigger disagreement resolution.
  - Structured name decomposition: agents output ism, nasab, kunya, laqab, nisba, death_hijri, and laqab_is_primary_identifier (boolean). When laqab_is_primary_identifier=true (e.g., سيبويه, الجاحظ, المبرد, البخاري, النووي), matching treats the laqab as the primary match key.
  - Name-equivalence with death dates: two names refer to the same scholar when death_hijri values match within a tolerance of ±5 Hijri years AND the shorter name's tokens are a strict subset of the longer name's tokens after stripping.
  - Name-equivalence without death dates: when death_hijri is null for BOTH names, strict token-subset matching alone is sufficient to declare equivalence, provided the shorter name's tokens are a strict subset of the longer name's tokens. This prevents cosmetic name-form differences from triggering disagreement resolution.
  - Disambiguation when canonical_match_name is identical and death_hijri is absent for both: the system MUST use secondary signals — science_scope of the work, specialized nisba tokens (المفسر vs المقرئ), and content-derived evidence. When no signal disambiguates, emit SRC-W-AMBIGUOUS-SCHOLAR-IDENTITY and set author_output.status=agent_disagreement with both candidates as positions.
  - The صاحب convention: 'صاحب [work_title]' (e.g., صاحب فتح الباري = Ibn Hajar, صاحب المغني = Ibn Qudama) is resolved via work-to-author lookup using REQ-SRC-0039 work_relationships, not name decomposition. This is a downstream citation resolution pattern; at the source-engine level it applies only when the صاحب formula appears in the metadata card or colophon attribution.
- Acceptance criteria:
  - AC-1 [deterministic] Given Name forms "الإمام النووي" and "النووي" with death_hijri=676 for both; When author-name matching executes; Then Both resolve to the same scholar. display_name preserves original form..
  - AC-2 [deterministic] Given Name forms "أبو محمد ابن قدامة" and "ابن قدامة" with death_hijri=620 for both; When author-name matching executes; Then Both resolve to the same scholar via token-subset + death_hijri match..
  - AC-3 [deterministic] Given Name forms "يحيى بن شرف النووي" (death_hijri=null) and "النووي" (death_hijri=null); When author-name matching executes; Then Both resolve to the same scholar via strict token-subset matching without death_hijri (null-null case)..
  - AC-4 [deterministic] Given Name forms "ابن كثير" (death_hijri=null) from a tafsir source and "ابن كثير" (death_hijri=null) from a qira'at source; When author-name matching executes; Then The system uses science_scope to disambiguate. SRC-W-AMBIGUOUS-SCHOLAR-IDENTITY is emitted if science_scope is unavailable..
  - AC-5 [deterministic] Given Name "سيبويه" with laqab_is_primary_identifier=true and name "عمرو بن عثمان بن قنبر" with death_hijri=180 for both; When author-name matching executes; Then Both resolve to the same scholar because laqab_is_primary_identifier allows laqab-to-ism matching..
  - AC-6 [deterministic] Given Name "أبو هريرة" (recognized kunya-only scholar); When kunya stripping executes; Then canonical_match_name="أبو هريرة" preserved as atomic unit. Kunya is NOT stripped..
  - AC-7 [deterministic] Given Name "لجنة الإفتاء الدائمة" with entity_type=institution; When name matching executes; Then entity_type=institution, canonical_match_name="لجنة الإفتاء الدائمة", no structured decomposition attempted..
  - AC-8 [deterministic] Given Name "كريمة بنت أحمد المروزية"; When name decomposition executes; Then بنت is recognized as patronymic connector, nasab correctly parsed..
  - AC-9 [deterministic] Given Death dates 256 and 252 for the same scholar البخاري from different databases; When death date comparison executes; Then Dates match within ±5 year tolerance. Scholar is NOT split into two records..

### REQ-SRC-0016 — Multi-science assignment
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added from domain-validator-review.yaml; amended per adversary-review.yaml ADV-008
- Trigger: Science classification detects evidence for more than one science.
- Postconditions:
  - science_scope preserves all supported sciences in dominance order.
  - The dominant science remains science_scope[0].
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/10_no_author/book.htm; When science classification executes; Then science_scope=["hadith", "fiqh"] and science_scope[0]="hadith"..

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

### REQ-SRC-0030 — Genre classification
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added after contract-architect review found genre is mandatory in CON-SRC-0004 but no requirement atom produces it. Genre is referenced as a precondition by REQ-SRC-0002 and REQ-SRC-0008 but was never formally specified. Amended 2026-04-23 (Phase 5b item 4, Option E-prime-final) to expand the postcondition-enumerated genre list with the four archival/documentary genres that are now pinned to the INV-SRC-0012 Axis 1 non-applicable set (mushaf, mashyakhah, thabat, barnamaj) per Codex E-prime DIM3 AMEND. The classifier does not currently emit these genres; the expansion keeps the postcondition list aligned with the Genre enum members that are normatively non-applicable for level. See follow-ups 21-26. Follow-up 32 amendment on 2026-04-24 aligns genre_dispute with the live contract shape: evidence-bearing GenreDisputePosition entries with genre_candidate, supporting_evidence, confidence, and source_agents, ordered by descending confidence; the scalar genre remains the primary / highest-confidence position.
- Trigger: Metadata deliberation processes a source candidate whose intake dossier is available.
- Postconditions:
  - source_metadata.genre is set to one of matn, sharh, hashiyah, risalah, hadith_collection, tafsir, fatawa, tabaqat, mujam, nazm, mukhtasar, mushaf, mashyakhah, thabat, barnamaj, fahrasah, or other.
  - When genre classification is disputed between agents and both positions are evidence-backed, genre is set to the majority or higher-confidence position as a scalar and a genre_dispute record preserves the competing positions with genre_candidate, supporting_evidence, confidence, and source_agents.
  - genre_dispute is optional, only written when genuine disagreement exists, and is ordered by descending confidence so the first position matches the scalar genre winner.
  - Genre classification uses title keywords, structural signals from the intake dossier, and content sampling when title evidence is ambiguous.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with title containing "أحكام"; When genre classification runs; Then source_metadata.genre="risalah"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small with title "همع الهوامع في شرح جمع الجوامع"; When genre classification runs; Then source_metadata.genre="sharh"..
  - AC-3 [deterministic] Given A source where one agent classifies genre=sharh and another classifies genre=hashiyah, both with evidence; When genre classification runs; Then source_metadata.genre is set to the higher-confidence position and genre_dispute preserves both positions with genre_candidate, supporting_evidence, confidence, and source_agents in descending-confidence order..

### REQ-SRC-0031 — Multi-layer hint detection
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added after contract-architect review found is_multi_layer is mandatory in CON-SRC-0004 but no requirement atom produces it. Implements DEC-SRC-0010 OPT-C (source hints, normalization confirms). Domain-validator review added genre-based auto-hint for tafsir and hadith.
- Trigger: Metadata deliberation processes a source whose intake dossier and genre classification are available.
- Postconditions:
  - source_metadata.is_multi_layer is set to true or false and is never null.
  - is_multi_layer=true when title contains any keyword in the multi-layer keyword set or when genre implies structural multi-layer content.
  - The multi-layer keyword set includes: شرح, حاشية, تعليق, تقريرات, نكت.
  - Genre-based auto-hint: genre in {tafsir, hadith_collection, sharh, hashiyah} sets is_multi_layer=true regardless of title keywords, because these genres are structurally multi-layer by definition.
  - source_metadata.multi_layer_evidence records which signals drove the hint (keyword matches, genre-based auto-hint, or format-specific signals).
  - is_multi_layer is a source-engine hint, not an authoritative verdict. Normalization confirms or overrides from actual text structure per DEC-SRC-0010.
  - When no title keywords match and genre does not imply multi-layer, is_multi_layer is set to false.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small with title "همع الهوامع في شرح جمع الجوامع"; When multi-layer detection runs; Then source_metadata.is_multi_layer=true and multi_layer_evidence includes keyword "شرح"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre=risalah and no multi-layer keywords in title; When multi-layer detection runs; Then source_metadata.is_multi_layer=false..
  - AC-3 [deterministic] Given A source with genre=tafsir and no multi-layer keywords in title; When multi-layer detection runs; Then source_metadata.is_multi_layer=true and multi_layer_evidence includes "genre_auto_hint"..

### REQ-SRC-0032 — Structural format classification
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added after contract-architect review found structural_format is mandatory in CON-SRC-0004 but no requirement atom produces it.
- Trigger: Metadata deliberation processes a source whose genre classification and intake dossier are available.
- Postconditions:
  - source_metadata.structural_format is set to one of prose, commentary, verse, reference_entries, qa_format, tabular, or mixed.
  - prose is the default for genres: risalah, fatawa, matn, mukhtasar.
  - commentary is set when genre in {sharh, hashiyah} or when is_multi_layer=true with interleaved base text and authorial explanation.
  - verse is set when genre=nazm or when the text structure is predominantly metered poetry.
  - reference_entries is set when genre in {mujam, tabaqat} or when the text is organized as alphabetical or biographical entries.
  - qa_format is set when the text follows a question-and-answer structure.
  - structural_format may be overridden by content-level signals from the intake dossier when title and genre signals are insufficient.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small with genre=sharh; When structural format classification runs; Then source_metadata.structural_format="commentary"..
  - AC-2 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt with genre=nazm; When structural format classification runs; Then source_metadata.structural_format="verse"..
  - AC-3 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with genre=risalah; When structural format classification runs; Then source_metadata.structural_format="prose"..

### REQ-SRC-0034 — Compiler-as-muhaqiq detection
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: adversary-review-2 ADV2-002 (compiler/muhaqiq role inversion gap); v1 LESSONS.md ERR-02 (Shamela lists source authors in author field while actual compiler is in muhaqiq field)
- Trigger: Attribution parsing identifies both author and muhaqiq from metadata card or colophon.
- Postconditions:
  - When muhaqiq death_hijri > 1300 (or no death date available) AND all listed authors have death_hijri < 1000, the source is flagged as compiler_muhaqiq_inversion_candidate.
  - When temporal distance between the earliest listed author death_hijri and the muhaqiq death_hijri exceeds 300 Hijri years, the source is flagged as compiler_muhaqiq_inversion_candidate.
  - Flagged cases add compiler_muhaqiq_inversion to study_quality_risk_flags array on the source dossier.
  - The flag routes to the disagreement resolver for evidence-based role correction, where the resolver determines whether the muhaqiq is actually the compiler and the listed authors are the sources being compiled.
- Acceptance criteria:
  - AC-1 [integration] Given A Shamela source like السراج المنير with classical source authors (death_hijri < 1000) and a contemporary muhaqiq (death_hijri > 1300 or no death date); When metadata deliberation runs attribution parsing; Then compiler_muhaqiq_inversion is present in study_quality_risk_flags and the source is routed to the disagreement resolver..
  - AC-2 [integration] Given A normal sharh with a single classical author (death_hijri=676) and a contemporary tahqiq editor (death_hijri=1420) where the metadata card correctly identifies the author as author and the editor as muhaqiq; When metadata deliberation runs attribution parsing; Then compiler_muhaqiq_inversion is flagged (temporal gap exceeds 300 years), routing to the disagreement resolver. The resolver examines evidence and confirms the roles are correct (genuine tahqiq, not compilation), removing the flag..

### REQ-SRC-0035 — Display metadata for teaching units (source card)
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview 2026-04-14 + Gemini DR on display metadata design (2026-04-14). The DR grounds the source card (بطاقة المصدر) in the Islamic scholarly tradition: the Eight Heads (الرؤوس الثمانية) of classical muqaddimat and the Ten Principles (المبادئ العشرة) of foundational sciences. Phase 5 amendment 2026-04-30 (scholar-matching DR synthesis §5.4): TIGHTEN dispute_panel semantics — scholar-dependent display fields (display_name, full_name_ lineage, scholarly_title, madhab, attributed_works, era_description, scholarly_standing) MUST be bound to CON-SRC-0008.scholar_match_result evidence (not free- floating LLM synthesis). When CON-SRC-0008 .disambiguation_state = disputed, display ALL positions side-by-side with score_breakdown (9 sub-scores from CON-SRC-0008.positions) + cited_evidence; the display layer MUST NOT silently pick a single id from positions[] to populate scalar fields like scholarly_title. When disambiguation_state = insufficient_evidence, the scholar- dependent fields are null with explicit reason in display_card.partial_reasons.
- Trigger: Metadata deliberation completes for a source candidate with confirmed or disputed author attribution and genre classification.
- Postconditions:
  - Phase 5 amendment 2026-04-30: scholar-dependent display fields (display_name, full_name_lineage, scholarly_title, madhab, attributed_works, era_description, scholarly_standing) are bound to CON-SRC-0008.scholar_match_result evidence. If CON-SRC-0008.disambiguation_state=definitive: scalar fields (display_name, scholarly_title, madhab) are populated from the registry record at canonical_scholar_id (display_card.scholar_match_state='definitive'). If disambiguation_state=disputed: dispute_panel is REQUIRED, lists ALL positions[] side-by-side with each position's display_name, scholarly_title, madhab, score_breakdown (9 sub-scores), and cited_evidence; scalar scholar-dependent fields display the leading position with explicit '(disputed — see panel)' annotation; the display MUST NOT silently pick a single id from positions[]. If disambiguation_state=insufficient_evidence: scholar-dependent fields are null with display_card.partial_reasons explicitly recording 'scholar match insufficient evidence' (display_card.scholar_match_state='insufficient_evidence').
  - source_metadata.display_card is written with 13 structured fields organized in two progressive disclosure tiers.
  - Quick-Glance tier (always visible): display_name (الاسم الشائع — the name the scholar is best known by), scholarly_title (اللقب العلمي — highest consensus-agreed honorific as a visual badge), death_date_display (سنة الوفاة — Hijri primary with Gregorian secondary), madhab (المذهب — methodological school tag), book_title (عنوان الكتاب), science_and_genre (التصنيف العلمي — with educational tooltips on technical terms), author_blurb_short (نبذة مختصرة — 1-2 sentence truncated blurb), and layer_tree_short (شجرة الكتاب — visual nesting for multi-layer works showing where the reader is).
  - Deep-Dive tier (expanded on interaction): full_name_lineage (البطاقة الشخصية الكاملة — ism, nasab, kunya, laqab, nisba unabridged), author_blurb_full (نبذة عن المؤلف — dynamically tailored to scholar type per Gemini DR), book_significance (أهمية الكتاب / الثمرة — why the author wrote it, what gap it fills, its rank), edition_metadata (بيانات الطبعة — muhaqqiq, publisher, year, city), dispute_panel (مؤشر التوثيق — visible only when authorship or attribution is disputed, showing all positions with evidence), and verification_sources (مصادر التوثيق — which databases and catalogs verified the metadata).
  - Deterministic extraction fields (from databases, never LLM-generated): display_name, full_name_lineage, death_date_display, book_title, science_and_genre, edition_metadata, layer_tree, verification_sources. Note: madhab and scholarly_title are registry-first fields — populated from scholar_authority registry when available, from agent research evidence when no registry entry exists, or null with reason in partial_reasons when neither source provides data.
  - LLM agent synthesis fields (generated by agent teams from research evidence): author_blurb, book_significance, dispute_panel summary. These must cite their evidence sources and are subject to multi-model review.
  - author_blurb is dynamically tailored to scholar type: hadith scholars emphasize rihlah and hifz; fiqh scholars emphasize rank within madhab; polymaths emphasize breadth and synthesis; modern scholars emphasize institutional role and contemporary impact; unknown authors state what is known with transparent uncertainty.
  - All display_card content is in Arabic and preserves full evidence chains per INV-SRC-0009.
- Acceptance criteria:
  - AC-1 [integration] Given A source identified as صحيح البخاري with author الإمام البخاري (death_hijri=256); When display metadata generation executes; Then display_card.display_name contains البخاري, display_card.scholarly_title contains أمير المؤمنين في الحديث or الإمام, display_card.death_date_display contains both 256 and 870, display_card.author_blurb mentions rihlah and hifz..
  - AC-2 [integration] Given A multi-layer source فتح الباري شرح صحيح البخاري by ابن حجر العسقلاني; When display metadata generation executes; Then display_card.layer_tree_short shows nested structure with صحيح البخاري as matn and فتح الباري as sharh, with a reading position indicator..
  - AC-3 [integration] Given A modern risalah الدروس المهمة لعامة الأمة by الشيخ ابن باز; When display metadata generation executes; Then display_card.author_blurb mentions institutional role (المفتي العام or equivalent) and display_card.book_significance describes it as an introductory text for beginners..
  - AC-4 [deterministic] Given A source with author_output.status=insufficient_evidence; When display metadata generation executes; Then display_card.status=partial, deterministic fields are populated, author_blurb is null with reason in partial_reasons..

### REQ-SRC-0039 — Work-to-work relationship modeling
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Claude DR spec audit 2026-04-15 finding that Islamic texts are fundamentally relational with mukhtasar-sharh-hashiyah chains up to 5 levels deep. Neither Shamela nor WorldCat models chain relationships. The source engine must capture typed links between derivative works and their base texts.
- Trigger: Metadata deliberation identifies a source whose genre implies a derivative relationship (sharh, hashiyah, mukhtasar, nazm, taliqa, taqrirat).
- Postconditions:
  - work_relationships is a list of typed links where each entry contains: relationship_type (one of is_commentary_on, is_supercommentary_on, is_abridgement_of, is_versification_of, has_part, is_part_of), target_work_title (string), target_work_author (string or null), and confidence (one of high, medium, low).
  - For genre=sharh: at least one entry with relationship_type=is_commentary_on identifying the matn it comments on.
  - For genre=hashiyah: at least one entry with relationship_type=is_supercommentary_on identifying the sharh it glosses.
  - For genre=mukhtasar: at least one entry with relationship_type=is_abridgement_of identifying the original work.
  - For genre=nazm: at least one entry with relationship_type=is_versification_of identifying the prose original.
  - When the target work cannot be identified from title, content, or metadata evidence, target_work_title is set to the best available partial evidence (e.g. extracted from the source's own title) and confidence=low.
  - For works where the matn is embedded in the commentary text, matn_embedding_style is recorded as one of: interlinear (matn lines alternate with sharh paragraphs), separated (matn in one block, sharh in another), marginal (matn in margin, sharh in body), or mazj (matn words woven into sharh sentences).
  - work_relationships is an empty list for standalone works (genre=matn, genre=risalah, genre=hadith_collection, genre=fatawa, or any genre with no derivative relationship).
- Acceptance criteria:
  - AC-1 [integration] Given A source titled "فتح الباري شرح صحيح البخاري" with genre=sharh; When work-to-work relationship modeling runs; Then work_relationships contains an entry with relationship_type="is_commentary_on", target_work_title contains "صحيح البخاري", confidence is high or medium..
  - AC-2 [integration] Given A source titled "حاشية ابن القيم على سنن أبي داود" with genre=hashiyah; When work-to-work relationship modeling runs; Then work_relationships contains an entry with relationship_type="is_supercommentary_on", target_work_title contains "سنن أبي داود"..
  - AC-3 [deterministic] Given A standalone risalah ("أحكام الاضطباع والرمل في الطواف") with genre=risalah; When work-to-work relationship modeling runs; Then work_relationships is an empty list..
  - AC-4 [integration] Given A source titled "شرح ابن عقيل على ألفية ابن مالك" with genre=sharh and interlinear matn embedding; When work-to-work relationship modeling runs; Then work_relationships contains is_commentary_on with target_work_title containing "ألفية ابن مالك" AND matn_embedding_style="interlinear"..

### REQ-SRC-0040 — Attribution confidence levels with scholarly terminology
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Claude DR spec audit 2026-04-15 finding that anonymous and pseudepigraphic works need confidence-level attribution beyond REQ-SRC-0004's three statuses (definitive/disputed/insufficient_evidence). The Islamic scholarly tradition has precise terminology for attribution confidence that the spec must model.
- Trigger: Author attribution finalizes (REQ-SRC-0004 completes) and the output must express the confidence level using Islamic scholarly terminology.
- Postconditions:
  - author_output.attribution_confidence is set to one of: confirmed (مؤكد — authorship established beyond reasonable doubt), disputed (مختلف في نسبته — scholarly disagreement on attribution; secondary display term منسوب إلى meaning "attributed to" may be used in display_card when the dispute involves only the attribution target), anonymous (مجهول المؤلف — truly unknown author), pseudepigraphic (منحول — falsely attributed, evidence the named author did not write it), or collective (جماعي — institutional or committee works with no named primary author; genuine co-authorship by named individuals using تأليف X و Y is handled by REQ-SRC-0004 co_authored status, not by collective).
  - For anonymous works, author_output preserves whatever temporal or geographic evidence exists (e.g. era, region, school affiliation) in author_output.anonymous_evidence as a free-text string.
  - For pseudepigraphic works, author_output preserves both the attributed_author (the false claimant) and false_attribution_evidence (the evidence against authenticity) per INV-SRC-0009.
  - For collective works, author_output.positions lists all identifiable contributors with their roles.
  - author_output.attribution_confidence_ar stores the Arabic scholarly term corresponding to the classification for display purposes.
  - attribution_confidence feeds into display_card dispute_panel generation (REQ-SRC-0035).
- Acceptance criteria:
  - AC-1 [deterministic] Given صحيح البخاري with author_output.status=definitive and unambiguous authorship; When attribution confidence classification runs; Then attribution_confidence="confirmed", attribution_confidence_ar="مؤكد"..
  - AC-2 [integration] Given A work attributed to al-Ghazali with scholarly evidence that the real author is a later imitator; When attribution confidence classification runs; Then attribution_confidence="pseudepigraphic", attribution_confidence_ar="منحول", attributed_author field preserved, false_attribution_evidence is non-empty..
  - AC-3 [integration] Given A truly anonymous work with only temporal evidence "مجهول - من أهل القرن السابع الهجري"; When attribution confidence classification runs; Then attribution_confidence="anonymous", attribution_confidence_ar="مجهول المؤلف", anonymous_evidence contains temporal era reference..
  - AC-4 [integration] Given الموسوعة الفقهية الكويتية with multiple contributing scholars, no single primary author, and institutional sponsorship; When attribution confidence classification runs; Then attribution_confidence="collective", attribution_confidence_ar="جماعي", author_output.positions lists identifiable contributors. Note that a work like "تأليف أحمد بن علي و محمد بن خالد" would NOT be collective but rather co_authored per REQ-SRC-0004..

### REQ-SRC-0042 — Scholar profile lookup for display card
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Contract-attribution review finding that REQ-SRC-0035 display card depends on madhab, scholarly_title, and full_name_lineage as deterministic fields, but no atom produces them. This atom fills that gap. Phase 5 amendment 2026-04-30 (scholar-matching DR synthesis §1.2 hot-path-forbids-runtime-external + §5.4 LOAD-BEARING amendment): tier-2 RUNTIME lookup of "structured databases (OpenITI metadata, Shamela author records, Dorar.net API)" is REMOVED — runtime external sources are forbidden in the scholar-matching hot path. Replacement: build-time-only enrichment lane explicitly authorizing OpenITI (offline metadata, evidence-only future-training-restricted), Wikidata SPARQL (opportunistic), LLM inference (sparse- record bootstrapping with provenance flag). All build-time external use produces records with data_provenance carrying source, enrichment_phase=build_time, license, and training_use_permitted (bool). Cross-provider 2-of-2 ratification: Claude DR §7 + ChatGPT DR §7. F-3 (external source unavailable build-time) closure surface per synthesis §1.4. This amendment is LOAD-BEARING because it changes the runtime architecture of REQ-SRC-0042's third lookup tier.
- Trigger: Author attribution has produced an agent_consensus or agent_disagreement result with at least one evidence-backed position.
- Postconditions:
  - For each author position, a scholar_profile record is retrieved or synthesized containing: full_name_lineage (ism, nasab, kunya, laqab, nisba in the longest unabridged form available), scholarly_title (highest consensus-agreed honorific), madhab (legal or theological school), primary_science (main field of scholarship), era_description (century or generation label).
  - Deterministic lookup order (Phase 5 amendment 2026-04-30): (1) scholar_authority registry match by canonical_id or name+death_hijri (operates against the locked registry snapshot per REQ-SRC-0049, registry_release_version pinned per case); (2) [REMOVED — runtime external lookup is FORBIDDEN per synthesis §1.2 hot-path-forbids-runtime-external; OpenITI / Shamela / Dorar.net data is now sourced ONLY at registry-build time per the build-time enrichment lane below]; (3) agent synthesis from textual evidence in the source itself, operating on the locked snapshot — verifiers reason over a CON-SRC-0009 evidence packet per REQ-SRC-0052.
  - Build-time enrichment lane (Phase 5 amendment 2026-04-30): the registry build phase MAY use OpenITI metadata (offline TSV, evidence-only future-training-restricted per Critical Rule 13 OpenITI license review), Wikidata SPARQL (opportunistic enrichment for cross-language identifiers + corroborating dates), LLM inference (sparse-record bootstrapping for under-populated scholar entries). All build-time external use produces records carrying data_provenance with source (string), enrichment_phase='build_time' (constant), license (string per source), and training_use_permitted (bool — owner-decision per Critical Rule 13). Build-time enrichment is performed BEFORE registry release; the resulting snapshot is what REQ-SRC-0049 locks for runtime cases.
  - When scholar_authority has a matching entry, all available fields are extracted deterministically without LLM involvement (operating against the locked snapshot).
  - When no registry match exists, agent synthesis produces the profile from available evidence in author_output.positions and source text via the REQ-SRC-0052 verifier cell (NOT from runtime external calls). Agent-synthesized profiles are tagged with profile_source=agent_synthesis. The registry MAY register a provisional entry per REQ-SRC-0043 (subject to the provisional-only-after-no-match rule from the REQ-SRC-0043 Phase 5 amendment) if the synthesis converges on 'new scholar' rather than 'unresolved ambiguity'.
  - death_gregorian is computed from death_hijri using standard Hijri-Gregorian conversion at display-card generation time (REQ-SRC-0035), not stored as a separate authoritative field in scholar_profile.
  - scholar_profile is attached to the corresponding author_output.positions entry and consumed by REQ-SRC-0035 for display_card generation.
- Acceptance criteria:
  - AC-1 [deterministic] Given Author attribution returns agent_consensus for البخاري (death_hijri=256) and scholar_authority registry contains a matching entry; When scholar profile lookup executes; Then scholar_profile.scholarly_title contains one of [امير المؤمنين في الحديث, الامام], scholar_profile.madhab is populated, scholar_profile.primary_science=hadith, scholar_profile.profile_source=scholar_authority.
  - AC-2 [integration] Given Author attribution returns agent_consensus for a minor modern scholar not present in scholar_authority or any structured database; When scholar profile lookup executes; Then scholar_profile is produced via agent synthesis, scholar_profile.profile_source=agent_synthesis, and fields are populated from source text evidence where available.
  - AC-3 [deterministic] Given Author attribution returns agent_consensus with death_hijri=256 for a scholar in scholar_authority; When display card generation (REQ-SRC-0035) consumes the scholar_profile; Then display_card.death_date_display contains both 256 (Hijri) and approximately 870 (Gregorian), computed at display time from death_hijri.

### REQ-SRC-0043 — New scholar registration in authority registry
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Adversary-attribution review ADV-ATT-008 finding that no atom specifies how a newly discovered author enters the scholar_authority registry. Phase 5 amendment 2026-04-30 (scholar-matching DR synthesis §5.4): CLARIFY provisional registration is permitted ONLY after the match cell concludes "new scholar" (CON-SRC-0008.disambiguation_state = insufficient_evidence with no candidate clearing the floor AND the synthesis verifiers converged that this is a new identity), NOT during unresolved ambiguity. A disputed match-call result (disambiguation_state=disputed) DOES NOT trigger provisional creation — the case is preserved for re-attribution against a richer registry release per INV-SRC-0017 explicit-replay rule. Provisional → confirmed promotion: when a second distinct book by the same provisional scholar enters the pipeline AND independent corroborating evidence accumulates (≥2-non-name floor met per INV-SRC-0013 across the two sources combined). Aligns with knowledge-integrity primacy and Owner Principle 3 (zero-tolerance for attribution errors).
- Trigger: Attribution identifies an author not present in scholar_authority AND the match cell (REQ-SRC-0049 through REQ-SRC-0053) has finalized the case as new-scholar (insufficient_evidence with no candidate clearing the floor + verifier convergence on "new identity" interpretation).
- Postconditions:
  - A provisional scholar_authority entry is created with status=provisional, containing: canonical_id (auto-assigned), display_name, full_name_lineage (best available from source evidence), death_hijri (if known, otherwise null), primary_science (inferred from source science_scope), authority_level=unknown, and source_book_ids listing the book that triggered creation.
  - Provisional entries are usable by downstream processing (REQ-SRC-0042 scholar profile lookup returns them) but are flagged in trust evaluation: trust fast-track (REQ-SRC-0015) is NOT eligible for sources attributed to provisional scholars (per REQ-SRC-0028 Phase 5 amendment partial_fragment_author_identity routing).
  - When a second distinct book by the same provisional scholar enters the pipeline and its evidence is consistent with the existing entry (display_name overlap and death_hijri match or both null) AND the combined evidence across the two sources satisfies INV-SRC-0013 ≥2-non-name floor, the entry is promoted to status=confirmed and authority_level is re-evaluated from unknown. Promotion without ≥2-non-name floor satisfaction is NOT permitted (Phase 5 amendment 2026-04-30).
  - The entry records evidence_sources as an array of objects each containing book_id, evidence_type (metadata_card, title_page, colophon, agent_inference), and the raw evidence string.
  - Phase 5 amendment 2026-04-30: a disputed match-call result (CON-SRC-0008.disambiguation_state=disputed) does NOT trigger provisional creation. The disputed case is preserved with positions[] populated for future re-attribution per INV-SRC-0017 explicit-replay rule; if a later registry release resolves the ambiguity, the disputed result is replayed.
- Acceptance criteria:
  - AC-1 [deterministic] Given A book attributed to a minor modern scholar not in scholar_authority with display_name and death_hijri available; When new scholar registration executes; Then scholar_authority gains a new entry with status=provisional, authority_level=unknown, source_book_ids containing the current book_id, and trust fast-track is blocked for this source.
  - AC-2 [integration] Given A second book by the same provisional scholar arrives with consistent evidence (same display_name, same death_hijri); When attribution completes and matches the provisional entry; Then The existing provisional entry is promoted to status=confirmed, source_book_ids contains both book_ids, and authority_level is re-evaluated.
  - AC-3 [deterministic] Given A new scholar with display_name matching existing entry ابن تيمية (death_hijri=728) but new evidence shows death_hijri=652; When new scholar registration executes; Then A separate scholar_authority entry is created with its own canonical_id, both entries have disambiguation_note referencing the other.

### REQ-SRC-0049 — Scholar registry snapshot locking for match-call duration
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §1.2 (hot-path-forbids-runtime-external) + §5.1 immediately-usable atom. Cross-provider 2-of-2 ratified: Claude DR §7 ("External sources are USED ONLY at registry-build time. This isolates Critical Rule 13 compliance to a one-time vetted ingestion stage.") + ChatGPT DR §7 ("the chosen runtime architecture should use no live external source in the attribution hot path. The hot path should run on a locked internal registry snapshot plus locally materialized side indexes."). 4-evaluator wave: 4-of-4 cross-provider HIGH on hot-path isolation. F-7 (cross-time inconsistency — registry mid-pipeline drift) closure surface per synthesis §1.4 failure-mode catalog. Codex Stage-3 Defect 2 (provenance naming): registry_release_version is the canonical name applied uniformly; snapshot_version is FORBIDDEN as a field name (case_packet_lock_id is reserved for the orthogonal per-call lock concept if needed).
- Trigger: The match-call orchestrator initiates a scholar identification case (triggered by REQ-SRC-0042 scholar profile lookup, REQ-SRC-0014 copyist-vs-author disambiguation, or excerpting-engine quoted-scholar resolution).
- Postconditions:
  - A versioned snapshot of the internal scholar registry plus all locally-materialized side indexes is loaded and pinned for the case duration. The pinned identifier is registry_release_version.
  - No write or merge operation against the registry is permitted to mutate the snapshot during the case. Concurrent registry updates are routed to the next release version, not the locked snapshot.
  - No external network call (Brill EI, Usul.ai API, Dorar.net API, Wikidata SPARQL endpoint, OpenITI GitHub, LLM enrichment endpoints) is permitted during the case — all enrichment data must already be present in the locked snapshot from build-time enrichment per REQ-SRC-0042 amendment.
  - The locked snapshot's registry_release_version is written to provenance.registry_release_version on every CON-SRC-0008 ScholarMatchResult emitted by the case (per INV-SRC-0017 snapshot-pin invariant).
  - Any snapshot drift detected mid-pipeline (e.g., orchestrator restart with a different release loaded) aborts finalization, discards verifier outputs from the case, and restarts from candidate generation against the new snapshot. This is EXPLICIT REPLAY, not silent re-resolution.
- Acceptance criteria:
  - AC-1 [deterministic] Given The internal scholar registry has registry_release_version "2026-04-15.r1" and a match-call is initiated for a fragment "البخاري" with deep dossier context.; When the orchestrator locks the snapshot and runs the case; Then The case operates against registry_release_version "2026-04-15.r1" exclusively. All CON-SRC-0008 ScholarMatchResult outputs from this case carry provenance.registry_release_version = "2026-04-15.r1"..
  - AC-2 [deterministic] Given A match-call is in flight against registry_release_version "2026-04-15.r1" and a concurrent registry update produces release "2026-04-15.r2" before the case finalizes.; When the orchestrator detects the available release change at finalization time; Then The in-flight case continues to operate against "2026-04-15.r1"; no mid-case drift occurs (the case is properly isolated). The new release "2026-04-15.r2" is available to the NEXT case..
  - AC-3 [integration] Given A match-call has loaded registry_release_version "2026-04-15.r1" and the orchestrator restarts (process crash, container restart) before finalization. On resume, only "2026-04-15.r2" is available.; When the orchestrator attempts to finalize the case on the new snapshot; Then Snapshot drift is detected (loaded version "2026-04-15.r2" ≠ pinned version "2026-04-15.r1"). Finalization aborts with SRC-E-REGISTRY-SNAPSHOT-DRIFT. Verifier outputs from the original case are retained as audit evidence but not used. Candidate generation restarts against "2026-04-15.r2" — EXPLICIT REPLAY. Provenance. registry_release_version on the restarted case is "2026-04-15.r2"..
  - AC-4 [integration] Given A match-call is locked against registry_release_version "2026-04-15.r1" and a verifier prompt template attempts a runtime external fetch (e.g., "fetch the latest Wikidata QID for this scholar").; When the orchestrator intercepts the external call; Then The external call is rejected with SRC-E-RUNTIME-EXTERNAL. The verifier is aborted. The case routes to disputed terminal with positions[] populated from local evidence only. The attempted external call is logged for audit..

### REQ-SRC-0050 — Scholar fragment normalization and 5-component parsing
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §5.2 (renumbered from ChatGPT DR's stale REQ-SRC-0045 to REQ-SRC-0050 per repo verification — slot 0045 already taken by "Supersession signal emission on source admission"). 5- component name parsing per .claude/rules/arabic-scholarly-conventions.md (ism / kunyah / nasab_chain / laqab / nisba_list). Honorific strip-from-match- key per existing shared/scholar_authority/src/name_matching.py honorific list (referenced by INV-SRC-0014 strict-ordering invariant). Compound-name preservation (عبد + divine attribute = single semantic unit) per arabic-scholarly-conventions.md compound-name rule. Cross-provider 2-of-2 ratified: F-5 (compound name split) closure surface per synthesis §1.4. Primary text immutability per Critical Rule 2 — match keys are derived; primary display strings are byte-identical to the source.
- Trigger: The match-call orchestrator receives a scholar fragment from author attribution (REQ-SRC-0004 / REQ-SRC-0014), excerpting-engine quoted-scholar resolution, or REQ-SRC-0042 scholar profile lookup.
- Postconditions:
  - The fragment is decomposed into the 5 classical name components: ism (given name), kunyah (teknonym such as أبو X / أم X), nasab_chain (patronymic chain such as ابن X بن Y), laqab (epithet such as قطب الدين), and nisba_list (relational adjectives such as البصري, الدمشقي, الأشعري). Each component may be null or empty; any-null-result is permitted.
  - Compound-name units are preserved as single tokens — عبد + divine attribute (عبد الله, عبد الرحمن, عبد الرحيم, عبد الرزاق, عبد العزيز, عبد الكريم, عبد المجيد, عبد الجبار, عبد القادر, عبد الستار, etc.) MUST NOT be split at whitespace into separate tokens. The compound is a single semantic unit per arabic-scholarly-conventions.md.
  - The display_fragment (the original fragment with honorifics PRESERVED for display) is stored byte-identical to the input per Critical Rule 2.
  - The match_key (derived for candidate-generation lookup) is constructed per INV-SRC-0014 three-stage ordering: (1) invisible-Unicode strip, (2) honorific normalization, (3) match-key construction. The match_key is a derived field; primary text is never modified.
  - parsed_components, display_fragment, and match_key are emitted as a structured packet feeding into REQ-SRC-0051 deterministic candidate generation and CON-SRC-0009 evidence packet construction.
- Acceptance criteria:
  - AC-1 [deterministic] Given Fragment "الإمام البخاري" (full honorific + nisba).; When REQ-SRC-0050 normalization runs; Then parsed_components.nisba_list = ["البخاري"]; parsed_components.ism = null; parsed_components.kunyah = null. display_fragment = "الإمام البخاري" (byte-identical preserved). match_key = "البخاري" (honorific stripped per INV-SRC-0014). No error..
  - AC-2 [deterministic] Given Fragment "عبد الله بن المبارك" (compound name + nasab).; When REQ-SRC-0050 normalization runs; Then parsed_components.ism = "عبد الله" (compound preserved as single semantic unit, NOT split into "عبد" and "الله"); parsed_components.nasab_chain = ["ابن المبارك"]. The compound rule is enforced. No SRC-E-COMPOUND-NAME-SPLIT error..
  - AC-3 [deterministic] Given Fragment "أبو حنيفة النعمان بن ثابت الكوفي" (kunyah + ism + nasab + nisba).; When REQ-SRC-0050 normalization runs; Then parsed_components.kunyah = "أبو حنيفة"; parsed_components.ism = "النعمان"; parsed_components.nasab_chain = ["بن ثابت"]; parsed_components.nisba_list = ["الكوفي"]. All four components populated; laqab = null. match_key contains all four (no honorifics to strip)..
  - AC-4 [deterministic] Given Fragment "الشيخ" only (honorific-shell input from a miscalled lookup).; When REQ-SRC-0050 normalization runs; Then Stage-1 bidi-strip (no marks) → Stage-2 honorific-strip removes الشيخ → match_key is empty. Match call aborts with SRC-E-HONORIFIC-ONLY-NAME per F-6 closure surface..
  - AC-5 [deterministic] Given Fragment "Sibawayh" (Latin transliteration provided to a match-call boundary that requires Arabic).; When REQ-SRC-0050 normalization runs; Then The fragment is rejected with SRC-E-FRAGMENT-NOT-ARABIC. Caller receives the error and the match call does not proceed..

### REQ-SRC-0051 — Deterministic scholar candidate generation with work-title channel
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §2.1 (Pivot (a) work-title-as-deterministic-index ADOPT WITH GUARDS) + §5.2 (renumbered from ChatGPT DR's stale REQ-SRC-0046 to REQ-SRC-0051 per repo verification — slot 0046 already taken by "Evidence preservation for downstream level inference"). 4-evaluator wave: 3-of-4 cross-provider HIGH on Pivot (a) + arabic-reviewer AMEND with operationalization fix (list-size guard N=3). Stage-4 absorbs all 4 substantive arabic-reviewer inputs landing on this atom: (1) Defect 5 list-size guard, (2) Novel Finding 2 work-title normalization function spec (allowed/forbidden), (3) Novel Finding 3 compound-title decomposition (شرح + base / حاشية + base), and (4) reference to INV-SRC-0014 strict-ordering for the match-key honorific exclusion. Cross-provider 2-of-2 on K cap (8 standard / 12 degraded). Compound-name preservation per REQ-SRC-0050 + F-5 closure surface per synthesis §1.4.
- Trigger: The match-call orchestrator enters Stage-1 candidate generation for a normalized fragment from REQ-SRC-0050.
- Postconditions:
  - EXACT (deterministic) channels are queried first against the locked snapshot: canonical_id direct lookup, canonical_name_ar normalized exact, known_as[] exact, kunya exact, death_date_hijri exact, nisba[] exact, AND the work-title channel below.
  - Work-title channel — known_work_title_normalized → list[canonical_id]. The channel applies normalization ONLY to the match-key index (never to stored titles per Critical Rule 2): ALLOWED diacritic strip + alef-variant normalization (ا → آ / إ / أ unified for matching key only); FORBIDDEN taa-marbuta normalization (preserves الهداية vs الهدايه distinction critical to Hanafi sources), FORBIDDEN Persian / Urdu / Kurdish character normalization (پ U+067E, چ U+0686, گ U+06AF, ژ U+0698 are PRESERVED for non-Arab work titles such as گيلاني works), FORBIDDEN ALL forms of Unicode NFC / NFD / NFKC / NFKD normalization on the stored title.
  - Work-title list-size guard — if known_work_title_normalized resolves to a list of size > N (default N = 3, calibrated at implementation time per the implementation-phase calibration corpus), the channel reverts to Stage-2 scoring signal only and DOES NOT contribute to Stage-1 deterministic narrowing. Sizes 1 - 3 promote to Stage-1 deterministic narrowing per the synthesis-ratified channel design. Empty lists (size 0) make no contribution.
  - Compound-title decomposition — work titles matching "شرح + [base title]" or "حاشية + [base title]" or "تهذيب + [base title]" or "مختصر + [base title]" decompose: extract base title as a SEPARATE Stage-1 narrowing channel for the base-work author, in addition to the channel for the compound-work author. Example: "شرح صحيح مسلم" → narrows on {al-Nawawi as sharh author} ∪ {Muslim ibn al-Hajjaj as base-work author}. Both channels feed into candidate_set; round-2 verifier selection (REQ-SRC-0052 + REQ-SRC-0053) decides which is the correct attribution for the dossier in question.
  - FUZZY channels run if exact channels surface fewer than K candidates: full-name trigram similarity over name_variants, component-wise approximate (Jaro-Winkler on ism / nasab / nisba), work-title fuzzy via trigram on normalized title.
  - K cap — candidate_set is capped at K = 8 for standard cases and K = 12 for degraded cases (per the case complexity assessment from REQ-SRC-0028). The cap is applied AFTER all channel contributions are merged and de-duplicated.
  - Compound-name preservation per REQ-SRC-0050 — the pre-retrieval tokenization MUST preserve compound names (عبد + divine attribute = single semantic unit). This closes F-5 (compound name split) per synthesis §1.4.
  - Honorifics MUST NOT appear in match keys per INV-SRC-0014 (the match-key construction has already applied this exclusion in REQ-SRC-0050; this atom does not re-apply, but consumes the exclusion-applied match_key).
  - The output candidate_set feeds CON-SRC-0009 evidence packet construction; each candidate carries canonical_id, canonical_name_ar, score_breakdown (per-channel contributions), and provenance_for_inclusion (which Stage-1 channel surfaced the candidate).
- Acceptance criteria:
  - AC-1 [integration] Given Fragment "الكاساني" with dossier_context indicating primary_science=fiqh, school_affiliations[fiqh]=hanafi, attributed_works=["بدائع الصنائع"], century_active_hijri≈6. Registry contains al-Kāsānī al-Ḥanafī (death 587 H) with canonical_name_ar="علاء الدين الكاساني" and known_works including "بدائع الصنائع".; When REQ-SRC-0051 Stage-1 candidate generation runs; Then Work-title channel resolves "بدائع الصنائع" to the single canonical_id of al-Kāsānī (list size = 1, ≤ N=3, promoted to Stage-1 deterministic narrowing). nisba channel matches الكاساني. candidate_set top-1 is al-Kāsānī with score_breakdown showing both work-title-channel + nisba-channel contributions, provenance_for_inclusion listing both channels..
  - AC-2 [integration] Given Fragment "الحنفي" with dossier_context indicating attributed_works=["مختصر"]. Registry contains 7 distinct Ḥanafī scholars whose known_works include the title "مختصر" (a polysemic work-title token).; When REQ-SRC-0051 Stage-1 candidate generation runs; Then Work-title channel resolves "مختصر" to a list of size 7 > N=3. The channel REVERTS to Stage-2 scoring signal only and does NOT contribute to Stage-1 deterministic narrowing. nisba channel matches الحنفي broadly (returns many candidates). The K cap (= 8) applies after channel merge. The work-title is preserved in the dossier_context for Stage-2 verifier reasoning but is not in the deterministic narrowing path..
  - AC-3 [integration] Given Fragment "الإمام النووي" with dossier_context attributed_works=["شرح صحيح مسلم"], primary_science=hadith. Registry contains both al-Nawawī (death 676 H, sharh author) and Muslim ibn al-Hajjāj (death 261 H, base-work author).; When REQ-SRC-0051 Stage-1 candidate generation runs with compound-title decomposition; Then Compound-title decomposition extracts "شرح + صحيح مسلم" → both channels fire. Sharh-author channel surfaces al-Nawawī (matched by both nisba=النووي and sharh- author-of-صحيح-مسلم). Base-work-author channel surfaces Muslim ibn al-Hajjāj. Both candidates appear in candidate_set. Stage-2 verifiers (REQ-SRC-0052) will resolve which is the correct attribution given other dossier signals (e.g., primary_science=hadith matches both; century_active_hijri ≈ 7 matches al-Nawawī, ≈ 3 matches Muslim)..
  - AC-4 [integration] Given Fragment "الكيلاني" with stored title "الفتوحات الغيبية" by Persian Hanafi scholar Gīlānī (the Persian چ in title). Registry has the title with U+06AF گ preserved in canonical title.; When REQ-SRC-0051 Stage-1 work-title normalization runs; Then The match-key normalization preserves the Persian گ U+06AF — does NOT collapse it to ك U+0643. The work-title channel correctly matches the registry's Persian-character-preserved title. taa-marbuta is also preserved (الفتوحات stays الفتوحات, not الفتوحاه). The candidate_set surfaces Gīlānī. The FORBIDDEN normalizations are not applied..
  - AC-5 [integration] Given Fragment "أبو حنيفة" with no work-title context (just a kunyah). Registry has 12 distinct scholars carrying the kunyah أبو حنيفة across history.; When REQ-SRC-0051 Stage-1 candidate generation runs; Then Kunyah-channel surfaces all 12. K cap = 8 applies (standard case complexity); top 8 by name-trigram similarity to fragment are kept. Stage-1 produces candidate_set of size 8. None of the 8 has been deterministically narrowed by work-title (no work- title in dossier); ≥2-non-name floor (per INV-SRC-0013) will be the binding constraint at Stage-2. The K cap is auditable in provenance_for_inclusion (which 8 of the 12 made it through, ranked by similarity)..
  - AC-6 [integration] Given Fragment "محمد" with NO dossier_context (single ism, no other signals). Registry has thousands of canonical_ids whose canonical_name_ar starts with محمد.; When REQ-SRC-0051 Stage-1 candidate generation runs; Then No exact channel surfaces a deterministic narrow (single-token ism is not a deterministic key). Fuzzy channels would return thousands; the K cap truncates to 8 standard. INV-SRC-0013 ≥2-non-name floor will reject definitive at REQ-SRC-0053 routing — none of the 8 will satisfy ≥2 non-name intersections without a richer dossier. Result routes to insufficient_evidence terminal. This AC documents the correctness of K-cap-then-floor routing for under-spec fragments..

### REQ-SRC-0052 — Scholar match verification cell with hybrid round-0 / round-1 protocol
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §2.3 (Pivot (c) verifier-independence mechanism HYBRID adjudication) + §5.2 (renumbered from ChatGPT DR's stale REQ-SRC-0047 to REQ-SRC-0052 per repo verification — slot 0047 already taken by "Owner override pathway for level at intake"). Cross-provider 2-of-2 contributing pivots: Claude DR §6 (adversarial scaffold) + ChatGPT DR §6 (functional independence with no-peeking + different prompts). Synthesis adopts HYBRID — ChatGPT DR's no-peeking as round-0 baseline; Claude DR's adversarial scaffold ONLY in round-1 disagreement-resolution. 4-evaluator wave: 4-of-4 UNANIMOUS HIGH on Pivot (c). Round cap = 2; both DRs converge. NO new candidates introduced in round-1 (Claude DR § + ChatGPT DR §5 Stage 10 both, ChatGPT DR's more conservative framing adopted: "no new candidate may be introduced unless it already existed in the frozen packet"). This atom specializes DEC-SRC-0013's deliberation-cell pattern as scholar_match_cell.
- Trigger: A locked CON-SRC-0009 evidence packet has been emitted by Stage-1 (REQ-SRC-0051 deterministic candidate generation); the orchestrator initiates Stage-2 verifier consensus.
- Postconditions:
  - Round-0 — Two verifiers receive the SAME CON-SRC-0009 packet (byte-identical input). Each verifier executes its own round-0 prompt template (different reasoning instructions but identical evidence). NO-PEEKING: neither verifier sees the other's output before forming its own round-0 verdict. Each verifier returns a ranked positions list with chosen_id, confidence, score_breakdown (9 sub-scores per ChatGPT DR §3b), and cited_evidence per position.
  - INV-SRC-0016 chosen_id-closure check runs on EVERY round-0 verifier output BEFORE any routing or convergence check reads the output. F-4 hallucinations are rejected up-front per the closure invariant.
  - Convergence check at round-0 (deterministic, no LLM involvement) — convergence requires: (a) both verifiers' top-ranked chosen_id is the same, (b) mean confidence ≥ 0.92, (c) each verifier's confidence ≥ 0.90, (d) no rival candidate within 0.07 of leader confidence (per REQ-SRC-0053 compound threshold), and (e) ≥2 non-name attributes intersect per INV-SRC-0013 floor. If ALL conditions met → DEFINITIVE terminal (REQ-SRC-0053 routing reads this as definitive). If any condition fails AND verifiers' top chosen_id is the same → fall through to round-1 (treated as disagreement on confidence shape rather than identity); if verifiers' top chosen_id differs → round-1 triggered.
  - Round-1 (only on round-0 non-convergence; otherwise skipped) — adversarial scaffold: verifier A receives a prompt template where it DEFENDS its round-0 leader against the round-0 alternative; verifier B receives a prompt template where it ATTACKS A's round-0 leader AND DEFENDS B's round-0 leader. The CON-SRC-0009 evidence packet is UNCHANGED (immutable per the contract). NO new candidates may be introduced — chosen_id MUST remain in candidate_set per INV-SRC-0016. Each verifier returns updated ranked positions.
  - INV-SRC-0016 chosen_id-closure check runs on EVERY round-1 verifier output (same closure as round-0).
  - Final convergence check at round-1 (deterministic, same compound threshold as round-0). If converged → DEFINITIVE per REQ-SRC-0053; if competing within 0.07 of leader → DISPUTED per REQ-SRC-0053; if neither candidate clears 0.70 → INSUFFICIENT_EVIDENCE per REQ-SRC-0053.
  - Round cap = 2 (no rounds beyond round-1; case finalizes with whatever terminal applies after round-1).
  - The provenance trail per CON-SRC-0008 records: verifier_a_id, verifier_b_id, round_count (1 if round-0 converged; 2 if round-1 ran), prompt template hashes for each round each verifier, all score_breakdowns, all cited_evidence references.
- Acceptance criteria:
  - AC-1 [integration] Given A locked CON-SRC-0009 packet for fragment "البخاري" with K=4 candidates. Both verifiers run round-0 and independently return chosen_id=sch_00042 with confidence 0.96 (verifier A) and 0.94 (verifier B); no rival within 0.07 of leader; ≥2-non-name floor satisfied (primary_science=hadith + attributed_works intersect).; When round-0 convergence check runs; Then All 5 conditions met (same chosen_id, mean 0.95 ≥ 0.92, each ≥ 0.90, no rival within 0.07, ≥2 non-name). Round-0 converges to DEFINITIVE. Round-1 is NOT triggered. provenance.round_count=1. CON-SRC-0008 emits with disambiguation_state=definitive..
  - AC-2 [integration] Given A locked CON-SRC-0009 packet where round-0 verifiers return DIFFERENT chosen_ids (verifier A: sch_00042 with 0.88; verifier B: sch_00115 with 0.85).; When round-0 convergence check runs; Then Conditions fail (different chosen_id). Round-1 is triggered. Verifier A receives "defend sch_00042" prompt; verifier B receives "attack sch_00042 + defend sch_00115" prompt. Both reason on the UNCHANGED CON-SRC-0009 packet. INV-SRC-0016 closure runs on both round-1 outputs..
  - AC-3 [integration] Given Round-1 verifiers return: verifier A reaffirms sch_00042 at 0.93 (defended successfully); verifier B revises to sch_00042 at 0.91 (attacker conceded). Mean = 0.92 ≥ 0.92, each ≥ 0.90, no rival within 0.07, ≥2-non-name satisfied.; When final convergence check at round-1 runs; Then All compound-threshold conditions met. Definitive terminal at REQ-SRC-0053. provenance.round_count=2. The audit trail shows the round-1 adversarial resolution with full prompt template hashes for both rounds, both verifiers..
  - AC-4 [integration] Given Round-1 verifiers continue to disagree: verifier A defends sch_00042 at 0.85; verifier B defends sch_00115 at 0.83. Competing within 0.07 (gap = 0.02).; When final convergence check at round-1 runs; Then Disputed routing per REQ-SRC-0053 (competing within 0.07). CON-SRC-0008 emits with disambiguation_state= disputed; positions[] populated with both candidates' score_breakdowns and cited_evidence; canonical_scholar_id is the leading id (top of positions). provenance .round_count=2. Round cap = 2 holds; no round-2..
  - AC-5 [integration] Given Verifier A returns chosen_id="sch_99999" (NOT in candidate_set — F-4 hallucination at round-0).; When orchestrator runs INV-SRC-0016 closure check; Then Verifier A output is REJECTED (per INV-SRC-0016). Logged as F-4. The case proceeds with verifier B's output only; if verifier B legitimately converged on an in-packet candidate, the case is treated as structural disagreement (one valid + one rejected) → disputed terminal with positions populated from legitimate candidates only..
  - AC-6 [deterministic] Given Only 1 verifier is available (the second model is rate-limited; both retries fail).; When REQ-SRC-0052 attempts to run; Then Match call aborts with SRC-E-TRUST-AGENT-COUNT (existing code, contracts.py:572). The case routes to disputed (with the single verifier's positions if any) or insufficient_evidence (if no verifier returned). Reuses the existing error code per ChatGPT DR existing-error-citation discipline..

### REQ-SRC-0053 — Scholar disagreement routing with compound 4-condition threshold
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §2.4 (Pivot (d) compound 4-condition threshold adjudication) + §5.2 (renumbered from ChatGPT DR's stale REQ-SRC-0048 to REQ-SRC-0053 per repo verification — slot 0048 already taken by "Deferred validation surface for owner_level_override"). Cross-provider DR sources: Claude DR §6 (single threshold 0.95) + ChatGPT DR §6 (compound 4-condition: mean ≥ 0.92 AND each ≥ 0.90 AND no rival within 0.07 AND ≥2 corroborating attributes beyond fragment). Synthesis adopts ChatGPT DR's compound rule per knowledge-integrity primacy: strictly more conservative in adversarial cases; rival-margin guard closes a class of false-definitive errors that the flat threshold would miss. 4-evaluator wave: 3-of-4 cross- provider HIGH on Pivot (d) + 1 AMEND with partition fix (Codex Stage-3 Defect 1 — threshold partition gap [0.05, 0.07)). Codex Defect 1 reconciliation applied: the disputed routing margin is widened to 0.07 so the definitive / disputed / insufficient_evidence predicates partition cleanly without the [0.05, 0.07) gap — Codex's recommended fix path (cleaner: extend disputed routing to "competing within 0.07 OR mean ∈ [0.75, 0.92)" per closure §3.1 Defect 1).
- Trigger: Stage-2 verifier consensus (REQ-SRC-0052) has emitted final round outputs (round-0 if converged at round-0; round-1 otherwise); the orchestrator runs terminal routing.
- Postconditions:
  - DEFINITIVE predicate (compound 4-condition AND) — all 4 conditions MUST be true: (a) both verifiers' final-round chosen_id is the same (convergent identity); (b) mean confidence ≥ 0.92; (c) each verifier's confidence ≥ 0.90; (d) no rival candidate within 0.07 of leader confidence; AND (e) the ≥2-non-name floor from INV-SRC-0013 is satisfied (corroboration_count ≥ 2 on eligible attributes). If ALL 5 conditions met → terminal = DEFINITIVE, canonical_scholar_id = chosen_id, confidence = mean, positions = empty.
  - DISPUTED predicate — ANY ONE of the following: (a) convergent identity but mean ∈ [0.75, 0.92); OR (b) verifiers diverge after round-1 (different chosen_ids at round-1 final); OR (c) competing candidates within 0.07 of leader (per Codex Defect 1 reconciliation: widened from 0.05 to 0.07 so the [0.05, 0.07) partition gap closes; this matches definitive's no-rival guard at exactly the same threshold for clean partitioning); OR (d) ≥2-non- name floor not met for any candidate even if confidence numbers would otherwise pass; OR (e) convergent identity at round-1 (same chosen_id) but at least one verifier's confidence < 0.90 (both_pass=false) — even when mean ≥ 0.92, no rival within 0.07, and ≥2-non-name floor met (Stage-4 Codex re-review closure: previously the partition left this case in a routing gap because (a) excludes mean ≥ 0.92, (b) excludes convergence, (c) requires close rival, and (d) requires floor unmet — none covered the convergent-but-both_pass=false case that AC-2 below exercises). If any condition true → terminal = DISPUTED, positions[] populated with all candidates that cleared the disputed floor (ranked by mean confidence descending).
  - INSUFFICIENT_EVIDENCE predicate — ANY ONE of the following: (a) no candidate scores ≥ 0.70 across both verifiers; OR (b) ambiguity remains after round cap (round-1 finalized as disputed but no candidate cleared the disputed-floor of mean 0.75). If any condition true → terminal = INSUFFICIENT_EVIDENCE, canonical_scholar_id = null, positions = empty.
  - The 3 predicates are MUTUALLY EXCLUSIVE and JOINTLY EXHAUSTIVE — every match-cell run terminates in exactly one of the 3 states (per Codex Defect 1 reconciliation: the partition is exhaustive after widening disputed to 0.07 AND adding the convergent-identity-but-both_pass=false branch (e) to disputed at Stage-4 closure).
  - provenance.threshold_audit records all 4 compound- threshold predicates' results (mean_passes, both_pass, no_rival_close, corroboration_count_ge_2) plus the numeric backing values (mean_confidence, leader_confidence, rival_confidence, corroboration_count) per INV-SRC-0015.
- Acceptance criteria:
  - AC-1 [deterministic] Given Round-1 final: both verifiers converge on chosen_id=sch_00042, confidences (0.95, 0.93). Mean = 0.94 ≥ 0.92, both ≥ 0.90, no rival within 0.07, ≥2 non-name attributes intersect.; When REQ-SRC-0053 routing runs; Then Terminal = DEFINITIVE. canonical_scholar_id=sch_00042. confidence=0.94. positions=empty. threshold_audit records all 4 predicates true with backing values..
  - AC-2 [deterministic] Given Round-1 final: both verifiers converge on chosen_id=sch_00042, confidences (0.99, 0.89). Mean = 0.94 ≥ 0.92, but each ≥ 0.90 FAILS (0.89 < 0.90).; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. The "each ≥ 0.90" guard prevents one strong verifier from carrying a weak one. positions[] populated. threshold_audit records both_pass=false (the binding failure) along with the other 3 predicate values..
  - AC-3 [deterministic] Given Round-1 final: both verifiers converge on sch_00042 with confidences (0.95, 0.95) but a rival candidate sch_00115 has aggregated confidence 0.91. Rival gap = 0.04 < 0.07.; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. The "no rival within 0.07" guard fires (gap 0.04 < 0.07). positions[] populated with both sch_00042 (leader) and sch_00115 (rival). threshold_audit records no_rival_close=false with rival gap 0.04 numeric backing. This AC documents the textbook ambiguous case classical methodology flags as disputed..
  - AC-4 [deterministic] Given Round-1 final: confidences satisfy all numeric predicates (mean 0.95, each ≥ 0.94, no rival within 0.07) but only 1 non-name attribute intersects between dossier and registry (INV-SRC-0013 floor unmet).; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. INV-SRC-0013 ≥2-non-name floor is the binding constraint regardless of confidence values. positions[] populated. threshold_audit records corroboration_count_ge_2= false with corroboration_count=1 numeric backing..
  - AC-5 [deterministic] Given Round-1 final with rival gap exactly = 0.06 (in the previously-under-specified [0.05, 0.07) range identified by Codex Stage-3 Defect 1).; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. The widened disputed-routing margin (0.07 per Codex Defect 1 reconciliation) captures this case cleanly. The previously under-specified gap [0.05, 0.07) is now closed: rival gaps in this range route to disputed (as the synthesis intended). threshold_audit records no_rival_close=false with rival gap 0.06 backing..
  - AC-6 [deterministic] Given Round-1 final: no candidate has confidence ≥ 0.70 across both verifiers (max individual confidence is 0.65).; When REQ-SRC-0053 routing runs; Then Terminal = INSUFFICIENT_EVIDENCE. canonical_scholar_id= null. positions=empty. threshold_audit records which predicate failed (no candidate ≥ 0.70 floor) with full backing values. The case is preserved for future re-attribution against a richer registry release..
  - AC-7 [deterministic] Given Round-1 final: verifiers diverge — verifier A chose sch_00042 at 0.88; verifier B chose sch_00115 at 0.86. Adversarial round-1 did not collapse the disagreement.; When REQ-SRC-0053 routing runs; Then Terminal = DISPUTED. The "verifiers diverge after round-1" condition fires. positions[] populated with both candidates. canonical_scholar_id is the leading id (sch_00042 by 0.88 vs 0.86 + aggregated rival score). threshold_audit records the specific failure (verifier_disagreement=true)..
