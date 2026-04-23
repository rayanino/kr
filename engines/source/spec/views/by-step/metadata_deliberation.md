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
- Source: Derived from OF-SRC-0009; amended per both coworker reviews, adversary-review.yaml ADV-003, and ChatGPT DR on agent-team architecture (2026-04-14) which recommends extending trust_decision to support disputed status with positions array.
- Trigger: The engine must emit a trust_decision for a source or metadata claim.
- Postconditions:
  - trust_decision contains decision, trust_path, supporting_agents, and evidence_summary fields.
  - trust_decision.decision is one of verified, needs_review, or disputed.
  - trust_decision.decision=disputed is set when independent trust verifiers produce evidence-backed competing trust assessments that do not converge after the disagreement protocol. In this case trust_decision.positions preserves both assessments with evidence and confidence, ordered by confidence descending.
  - Every run writes monitor_feedback records even when the case follows the fast_track path.
  - Books meeting all fast_track predicates may use trust_path=fast_track instead of full_deliberation.
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
- Source: ChatGPT DR report on agent-team architecture (2026-04-14). Defines three routing paths based on case complexity signals. The source engine classifies PDF text quality but does NOT perform OCR — degraded-evidence path means limited internal evidence requiring heavier external research, not OCR processing.
- Trigger: The orchestrator begins metadata deliberation for a source candidate.
- Postconditions:
  - case_complexity is set to one of fast_track, standard, or degraded_evidence.
  - fast_track requires all of: scholar_authority[author_canonical_id].authority_level >= primary, genre in {matn, sharh, hadith_collection, tafsir}, author_death_hijri is not null.
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
- Source: Added after contract-architect review found genre is mandatory in CON-SRC-0004 but no requirement atom produces it. Genre is referenced as a precondition by REQ-SRC-0002 and REQ-SRC-0008 but was never formally specified. Amended 2026-04-23 (Phase 5b item 4, Option E-prime-final) to expand the postcondition-enumerated genre list with the four archival/documentary genres that are now pinned to the INV-SRC-0012 Axis 1 non-applicable set (mushaf, mashyakhah, thabat, barnamaj) per Codex E-prime DIM3 AMEND. The classifier does not currently emit these genres; the expansion keeps the postcondition list aligned with the Genre enum members that are normatively non-applicable for level. See follow-ups 21-26.
- Trigger: Metadata deliberation processes a source candidate whose intake dossier is available.
- Postconditions:
  - source_metadata.genre is set to one of matn, sharh, hashiyah, risalah, hadith_collection, tafsir, fatawa, tabaqat, mujam, nazm, mukhtasar, mushaf, mashyakhah, thabat, barnamaj, fahrasah, or other.
  - When genre classification is disputed between agents and both positions are evidence-backed, genre is set to the majority or higher-confidence position as a scalar and a genre_dispute record preserves the competing positions with evidence.
  - genre_dispute is optional and only written when genuine disagreement exists.
  - Genre classification uses title keywords, structural signals from the intake dossier, and content sampling when title evidence is ambiguous.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with title containing "أحكام"; When genre classification runs; Then source_metadata.genre="risalah"..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small with title "همع الهوامع في شرح جمع الجوامع"; When genre classification runs; Then source_metadata.genre="sharh"..
  - AC-3 [deterministic] Given A source where one agent classifies genre=sharh and another classifies genre=hashiyah, both with evidence; When genre classification runs; Then source_metadata.genre is set to the higher-confidence position and genre_dispute preserves both positions..

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
- Source: Owner interview 2026-04-14 + Gemini DR on display metadata design (2026-04-14). The DR grounds the source card (بطاقة المصدر) in the Islamic scholarly tradition: the Eight Heads (الرؤوس الثمانية) of classical muqaddimat and the Ten Principles (المبادئ العشرة) of foundational sciences.
- Trigger: Metadata deliberation completes for a source candidate with confirmed or disputed author attribution and genre classification.
- Postconditions:
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
- Source: Contract-attribution review finding that REQ-SRC-0035 display card depends on madhab, scholarly_title, and full_name_lineage as deterministic fields, but no atom produces them. This atom fills that gap.
- Trigger: Author attribution has produced an agent_consensus or agent_disagreement result with at least one evidence-backed position.
- Postconditions:
  - For each author position, a scholar_profile record is retrieved or synthesized containing: full_name_lineage (ism, nasab, kunya, laqab, nisba in the longest unabridged form available), scholarly_title (highest consensus-agreed honorific), madhab (legal or theological school), primary_science (main field of scholarship), era_description (century or generation label).
  - Deterministic lookup order: (1) scholar_authority registry match by canonical_id or name+death_hijri, (2) structured databases (OpenITI metadata, Shamela author records, Dorar.net API), (3) agent synthesis from textual evidence in the source itself.
  - When scholar_authority has a matching entry, all available fields are extracted deterministically without LLM involvement.
  - When no registry match exists and no structured database match is found, agent synthesis produces the profile from available evidence in author_output.positions and source text. Agent-synthesized profiles are tagged with profile_source=agent_synthesis.
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
- Source: Adversary-attribution review ADV-ATT-008 finding that no atom specifies how a newly discovered author enters the scholar_authority registry.
- Trigger: Attribution identifies an author not present in scholar_authority.
- Postconditions:
  - A provisional scholar_authority entry is created with status=provisional, containing: canonical_id (auto-assigned), display_name, full_name_lineage (best available from source evidence), death_hijri (if known, otherwise null), primary_science (inferred from source science_scope), authority_level=unknown, and source_book_ids listing the book that triggered creation.
  - Provisional entries are usable by downstream processing (REQ-SRC-0042 scholar profile lookup returns them) but are flagged in trust evaluation: trust fast-track (REQ-SRC-0015) is NOT eligible for sources attributed to provisional scholars.
  - When a second distinct book by the same provisional scholar enters the pipeline and its evidence is consistent with the existing entry (display_name overlap and death_hijri match or both null), the entry is promoted to status=confirmed and authority_level is re-evaluated from unknown.
  - The entry records evidence_sources as an array of objects each containing book_id, evidence_type (metadata_card, title_page, colophon, agent_inference), and the raw evidence string.
- Acceptance criteria:
  - AC-1 [deterministic] Given A book attributed to a minor modern scholar not in scholar_authority with display_name and death_hijri available; When new scholar registration executes; Then scholar_authority gains a new entry with status=provisional, authority_level=unknown, source_book_ids containing the current book_id, and trust fast-track is blocked for this source.
  - AC-2 [integration] Given A second book by the same provisional scholar arrives with consistent evidence (same display_name, same death_hijri); When attribution completes and matches the provisional entry; Then The existing provisional entry is promoted to status=confirmed, source_book_ids contains both book_ids, and authority_level is re-evaluated.
  - AC-3 [deterministic] Given A new scholar with display_name matching existing entry ابن تيمية (death_hijri=728) but new evidence shows death_hijri=652; When new scholar registration executes; Then A separate scholar_authority entry is created with its own canonical_id, both entries have disambiguation_note referencing the other.
