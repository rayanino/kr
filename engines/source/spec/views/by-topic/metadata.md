# Source Spec Atoms by Topic: metadata

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0002 | constraint | Hadith literature dominates source-engine benchmark quality | confirmed | high |
| CON-SRC-0008 | constraint | ScholarMatchResult contract — match-call output with dual state surface | confirmed | critical |
| CON-SRC-0009 | constraint | Scholar evidence packet contract — immutable case bundle | confirmed | critical |
| CON-SRC-0011 | constraint | WorkLevel enum — classical pedagogical-level vocabulary | confirmed | high |
| DEC-SRC-0002 | decision | Science scope uses dynamic registry | confirmed | high |
| DEC-SRC-0003 | decision | Level detection strategy | confirmed | medium |
| DEC-SRC-0007 | decision | Disputed metadata as multi-position evidence | confirmed | high |
| DEC-SRC-0010 | decision | Source hints multi-layer routing and normalization confirms it | confirmed | medium |
| DEC-SRC-0012 | decision | Multi-position metadata ordered by confidence | confirmed | high |
| DEC-SRC-0021 | decision | Pre-Phase-5a SourceMetadata migration — default-on-read at load boundary | confirmed | high |
| INV-SRC-0002 | invariant | Author attribution role separation is mandatory | confirmed | critical |
| INV-SRC-0003 | invariant | Library never refuses knowledge | confirmed | critical |
| INV-SRC-0006 | invariant | Isnad atomic preservation | confirmed | high |
| INV-SRC-0007 | invariant | Scholar registry minimum population | confirmed | critical |
| INV-SRC-0009 | invariant | Zero knowledge loss in all source-engine output | confirmed | critical |
| INV-SRC-0011 | invariant | Source engine must not infer level from shallow metadata | confirmed | critical |
| INV-SRC-0012 | invariant | Non-applicable works require level null | confirmed | high |
| INV-SRC-0013 | invariant | No definitive scholar match from under-specified fragment (≥2 non-name floor) | confirmed | critical |
| INV-SRC-0014 | invariant | Matching-key honorific exclusion with bidi-strip ordering | confirmed | critical |
| INV-SRC-0016 | invariant | Verifier chosen_id closure — F-4 hallucination prevention | confirmed | critical |
| INV-SRC-0017 | invariant | Registry snapshot version pin — F-7 cross-time-inconsistency closure | confirmed | critical |
| OF-SRC-0004 | feedback | Author attribution errors are catastrophic | confirmed | critical |
| OF-SRC-0005 | feedback | Science hints follow the same cross-validation rule | confirmed | high |
| OF-SRC-0006 | feedback | Science registry must keep growing | confirmed | high |
| OF-SRC-0007 | feedback | Preserve and infer level metadata from content | confirmed | medium |
| OF-SRC-0008 | feedback | Multi-layer detection ownership is unresolved | confirmed | medium |
| OF-SRC-0012 | feedback | Hadith classification is the primary benchmark surface | confirmed | high |
| OQ-SRC-0001 | question | Level detection ownership | superseded | medium |
| OQ-SRC-0006 | question | Ordering and display semantics for multi-position metadata | superseded | high |
| REQ-SRC-0004 | requirement | Multi-model consensus for author attribution | confirmed | critical |
| REQ-SRC-0005 | requirement | Optional science hint | confirmed | medium |
| REQ-SRC-0006 | requirement | Growable science registry without owner gate | confirmed | high |
| REQ-SRC-0007 | requirement | Level field preservation across source-engine handoff | confirmed | medium |
| REQ-SRC-0010 | requirement | Graduated muhaqiq standing | confirmed | medium |
| REQ-SRC-0011 | requirement | Fine-grained hadith classification | confirmed | high |
| REQ-SRC-0012 | requirement | Multi-position metadata for disputed fields | confirmed | high |
| REQ-SRC-0014 | requirement | Copyist and author disambiguation | confirmed | critical |
| REQ-SRC-0015 | requirement | Scholar identity matching and name resolution | confirmed | critical |
| REQ-SRC-0016 | requirement | Multi-science assignment | confirmed | high |
| REQ-SRC-0023 | requirement | PDF text-layer evidence is diagnostic only | confirmed | critical |
| REQ-SRC-0024 | requirement | PDF page-geometry hints for normalization | confirmed | high |
| REQ-SRC-0030 | requirement | Genre classification | confirmed | critical |
| REQ-SRC-0031 | requirement | Multi-layer hint detection | confirmed | critical |
| REQ-SRC-0032 | requirement | Structural format classification | confirmed | critical |
| REQ-SRC-0034 | requirement | Compiler-as-muhaqiq detection | confirmed | critical |
| REQ-SRC-0035 | requirement | Display metadata for teaching units (source card) | confirmed | high |
| REQ-SRC-0039 | requirement | Work-to-work relationship modeling | confirmed | high |
| REQ-SRC-0040 | requirement | Attribution confidence levels with scholarly terminology | confirmed | high |
| REQ-SRC-0042 | requirement | Scholar profile lookup for display card | confirmed | high |
| REQ-SRC-0043 | requirement | New scholar registration in authority registry | confirmed | high |
| REQ-SRC-0047 | requirement | Owner override pathway for level at intake | confirmed | medium |
| REQ-SRC-0048 | requirement | Deferred validation surface for owner_level_override | confirmed | medium |
| REQ-SRC-0049 | requirement | Scholar registry snapshot locking for match-call duration | confirmed | critical |
| REQ-SRC-0050 | requirement | Scholar fragment normalization and 5-component parsing | confirmed | critical |
| REQ-SRC-0051 | requirement | Deterministic scholar candidate generation with work-title channel | confirmed | critical |

### CON-SRC-0002 — Hadith literature dominates source-engine benchmark quality
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012; amended per contract-architect-review.yaml
- Rule: At least 40 percent of source-engine benchmark fixtures must be hadith literature or hadith-adjacent works.

### CON-SRC-0008 — ScholarMatchResult contract — match-call output with dual state surface
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §5.1 immediately-usable atom (CON-SRC-0008 verified clean against engines/source/spec/INDEX.yaml — slot not previously taken). ChatGPT DR §3d originated the result shape; cross-provider 2-of-2 ratification on the 3-state output. Synthesis §3.1 ChatGPT DR analytical advantage absorbed: 5-state ScholarAuthorityRecord.status preservation (engines/source/contracts.py:688-694 retains its existing lifecycle unchanged). Codex Stage-3 Defect 3 (3-state vs 5-state surface contradiction) fix: this contract carries BOTH state surfaces — disambiguation_state (3-state, this match call) and record_status (5-state, lifecycle of the referenced record). Codex Stage-3 Defect 2 (provenance naming): registry_release_version is the canonical name (snapshot_version is FORBIDDEN as a field name). Synthesis §3.2 ChatGPT DR analytical advantage absorbed: teacher- student fields and teacher_student_network_match scoring signal preserved. Synthesis §4.1 common-gap preserved: career_phases interaction via matched_phase.
- Rule: The ScholarMatchResult contract has the following required fields: (1) canonical_scholar_id — Optional[str]; populated when disambiguation_state=definitive, populated with the leading-confidence chosen_id when disambiguation_state= disputed (the lower-confidence positions are in positions[]), null when disambiguation_state= insufficient_evidence. (2) confidence — float in [0.0, 1.0]; the mean confidence across the two Stage-2 verifiers for the chosen_id (or null if insufficient_evidence). (3) disambiguation_state — Literal["definitive", "disputed", "insufficient_evidence"]; the 3-state output of THIS match call. (4) record_status — Optional[Literal["provisional", "confirmed", "merged_into", "split_disputed", "deprecated"]]; the 5-state lifecycle status of the canonical_scholar_id record at the time the match call ran (sourced from ScholarAuthorityRecord.status at engines/source/contracts.py:688-694). Null when canonical_scholar_id is null. NOT a required match-call decision; this is the orthogonal record-lifecycle surface. (5) evidence_sources — list[CitationRef]; non-empty when disambiguation_state ∈ {definitive, disputed} per INV-SRC-0015 provenance-completeness invariant. Each CitationRef carries source_book_id, evidence_type (metadata_card / title_page / colophon / agent_inference / work_title_match / teacher_student_link / external_anchor), and the raw evidence string. (6) positions — list[Position]; populated iff disambiguation_state=disputed. Each Position carries canonical_id, confidence (per-verifier and aggregated), score_breakdown (the 9 sub-scores per ChatGPT DR §3b: name_match, death_date_proximity, school_affiliation_overlap, work_title_match, teacher_student_network_match, geographic_origin_match, century_active_match, primary_science_match, secondary_sciences_overlap), why_not_other_candidate (qualitative), cited_evidence (list[CitationRef]). (7) provenance — ScholarMatchProvenance object containing: stage_1_score_breakdown (Stage-1 channel contributions per candidate from REQ-SRC-0051), stage_2_verifier_record ( verifier_a_id, verifier_b_id, verifier_a_seed, verifier_b_seed, verifier_a_prompt_template_hash, verifier_b_prompt_template_hash, round_count [1 or 2]), threshold_audit (4 predicate values from REQ-SRC-0053 compound threshold: mean_passes [bool], both_pass [bool], no_rival_close [bool], corroboration_count_ge_2 [bool] — plus the actual mean confidence, leader confidence, rival confidence, and corroboration_count integer for full auditability), registry_release_version (str; the pinned snapshot from REQ-SRC-0049 — the canonical field name; snapshot_version is FORBIDDEN per Codex Stage-3 Defect 2), matched_phase (Optional[CareerPhaseRef]; populated when the dossier signals a specific career phase per shared/scholar_authority/SPEC.md §4.A.7). The contract is immutable post-emission.

### CON-SRC-0009 — Scholar evidence packet contract — immutable case bundle
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §5.1 (third immediately-usable atom; numbering CON-SRC-0009 verified clean against engines/source/spec/INDEX.yaml — slot not previously taken). ChatGPT DR §3d originated the evidence-packet shape; cross-provider 2-of-2 ratification on packet-locked verifier reasoning per synthesis §1.1 OPT-4 architecture. F-4 (LLM hallucinates non-existent scholar) closure surface per synthesis §1.4: verifiers MUST reason over a frozen candidate set; INV-SRC-0016 enforces the chosen_id-closure invariant against this contract. Round-1 cannot mutate the packet (no new candidates introduced) — synthesis §2.3 Pivot (c) adjudication.
- Rule: The ScholarEvidencePacket contract defines an immutable bundle locked at the end of Stage-1 deterministic candidate generation (REQ-SRC-0051). Required fields: (1) normalized_fragment — the 5-component parse from REQ-SRC-0050 (ism, kunyah, nasab_chain, laqab, nisba_list); (2) display_fragment — byte-identical-to-source preserved string per Critical Rule 2; (3) match_key — derived match string per INV-SRC-0014 strict-ordering; (4) parsed_components — the structured 5-tuple from REQ-SRC-0050; (5) dossier_context — the upstream context bundle (genre, primary_science, century_active_hijri estimates, school_affiliations[science] hints, attributed_works referenced in the source, geographic signals, work-title extracts from the source); (6) candidate_set — list[ScholarCandidate], the Stage-1 narrowed candidate universe (K cap = 8 standard / 12 degraded per REQ-SRC-0051); each ScholarCandidate carries canonical_id, canonical_name_ar, score_breakdown (per-channel contributions), and provenance_for_inclusion (which Stage-1 channel surfaced this candidate); (7) source_snippets — relevant excerpt strings from the source providing the fragment context (max 2 KB per snippet, max 5 snippets); (8) registry_release_version — the pinned snapshot identifier per REQ-SRC-0049 (named registry_release_version canonically; snapshot_version is FORBIDDEN as a field name per Codex Stage-3 Defect 2). The packet is IMMUTABLE for the case duration: round-0 verifiers and round-1 verifiers receive the SAME packet; round-1 cannot introduce new candidates (any chosen_id must already be in candidate_set per INV-SRC-0016).

### CON-SRC-0011 — WorkLevel enum — classical pedagogical-level vocabulary
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Established on 2026-04-17 following the 3-of-3 unanimous OPT-B adjudication on DEC-SRC-0003. The enum values derive from Gemini CLI run 2 classical-defensibility review (R2 finding) which identified that the ChatGPT DR amendment set used `mutaqaddim` as the "advanced" level value — incorrect classical usage. Mutaqaddim (متقدم) denotes chronological priority (an earlier-generation scholar relative to a later one), NOT pedagogical advancement. The correct classical pedagogical ladder is mubtadiʾ (beginner) → mutawassiṭ (intermediate) → muntahī (terminal / advanced), documented in al-Zarnūjī's Taʿlīm al-Mutaʿallim, Ibn Khaldūn's Muqaddima Book VI (faṣl fī wajh al-ṣawāb fī taʿlīm al-ʿulūm), and the standard curriculum language of Dār al-Muṣṭafā and al- Qarawiyyīn ḥadīth tracks. See .kr/runtime/ adjudication_gemini_cli_run1_20260417.md (R2 terminology finding) and run2_20260417.md (independent confirmation). Amended 2026-04-23 (Phase 5b item 5) to break 3 producer-consumer cycles: the original depends_on list named INV-SRC-0011, CON-SRC-0004, and REQ-SRC-0047 — all of which CONSUME this enum and themselves declare CON-SRC-0011 as a producer, creating cycles that break scoped atom injection per Codex CAF-1. The corrected ordering is strictly producer-before- consumer: CON-SRC-0011 defines the WorkLevel vocabulary, so it depends only on the architectural decision (DEC-SRC-0003) that authorized having a level vocabulary at all; every atom that uses the enum (INV-SRC-0011, INV-SRC-0012, CON-SRC-0004, REQ-SRC-0047, REQ-SRC-0007) declares CON-SRC-0011 as an upstream producer. Further amended 2026-04-23 (Phase 5b item 11) to add the C7 multi-layer scope clause: the single scalar SourceMetadata.level, when populated for a multi-layer work (matn + sharḥ, sharḥ + ḥāshiya, or deeper nestings), refers to the TARGET READERSHIP of the composite work as a whole — the pedagogical state of the student for whom the work is intended — NOT the level of any contained layer, the author's own scholarly stature, or the matn's intrinsic density. Per Gemini CLI Run B C7 verdict CONFIRM (interpretation_measured: target_readership, `.kr/runtime/domain_validation_gemini_cli_run_B_20260417.md`:95-102) and Adversary finding ADV-007 (severity: HIGH; affected_atoms: REQ-SRC-0046, CON-SRC-0011, CON-SRC-0004; `.kr/runtime/ adversary_phase5a_20260417.md`:242-252). Classical-defensibility reasoning: all four madhāhib use the mubtadiʾ/mutawassiṭ/muntahī terminology to describe the student-state at which the work is pitched, not the author's own rank (al-Zarnūjī Taʿlīm al-Mutaʿallim IV; Ibn Khaldūn Muqaddima VI, faṣl fī wajh al-ṣawāb fī taʿlīm al- ʿulūm). The scope is the owner's own question — "what student can read this?" — so the library ladder matches his actual progression. A sharḥ authored by a muntahī but composed to teach mubtadiʾ students is assigned level="mubtadiʾ"; a ḥāshiya composed for muntahī-level Ḥanafī specialists is assigned level="muntahī" regardless of the underlying matn's native level. This interpretation is strictly stronger than the Adversary's proposed "outer author's work only" alternative fix — it refuses the author-rank proxy in favor of the pedagogical-fit question the owner actually asks of the library. Closure-wave amendment 2026-04-23 (Codex CAF-5 + 2-of-2 Gemini DIM1/DIM2 convergent): (a) replaced residual "taxonomy engine" wording in rationale with "synthesis engine" per DEC-SRC-0003 synthesis-owns-level (closes Codex CAF-5); (b) anchored the multi-layer scope clause in rule.statement to the classical Arabic istiʿdād al-mutaʿallim (استعداد المتعلم) per Ibn Khaldūn Muqaddima VI, with al-qāriʾ al-maqṣūd (القارئ المقصود) as equivalent gloss (closes 2-of-2 Gemini DIM1 — Run A proposed istiʿdād, Run B proposed al-qāriʾ al-maqṣūd; both kept, classical primacy to Ibn Khaldūn's exact phrasing); (c) augmented AC-7 from a single Hanbali exemplar (Ibn ʿUthaymīn) to a four-madhhab exemplar set (Maḥallī Sharḥ al-Waraqāt for Shafiʿi, al-Shurunbulālī Nūr al- Īḍāḥ for Hanafi, Zarrūq Sharḥ al-Risālah for Maliki, original Ibn ʿUthaymīn retained for Hanbali), avoiding perceived madhhab bias and demonstrating that the istiʿdād al-mutaʿallim scope rule is universally institutionalized across the Sunni schools (closes 2-of-2 Gemini DIM2 convergent finding). Reviewer outputs at `.kr/runtime/closure_wave_codex_cli_20260423.md` and `.kr/runtime/closure_wave_gemini_cli_run_{A,B}_20260423.md`.
- Rule: The WorkLevel enum is the canonical vocabulary for the SourceMetadata.level field and any downstream field that stores an authoritative pedagogical-level assignment. It has exactly three permitted values: "mubtadiʾ" (beginner / pre-malakah student), "mutawassiṭ" (intermediate / foundational-malakah student), and "muntahī" (terminal / curriculum-completing student). No other string values are valid for a SourceMetadata .level assignment. The historiographic term "mutaqaddim" and its counterpart "mutaʾakhkhirūn" are REJECTED as WorkLevel values — they denote chronological / generational priority among scholars, not pedagogical level. For a multi-layer work (matn + sharḥ, sharḥ + ḥāshiya, or deeper nestings), the single scalar SourceMetadata.level refers to the TARGET READERSHIP of the composite work as a whole — the pedagogical state of the student for whom the work is intended — NOT the level of any contained layer, the author's own scholarly stature, or the matn's intrinsic density. The classical Arabic anchor for this scope is istiʿdād al-mutaʿallim (استعداد المتعلم) per Ibn Khaldūn Muqaddima VI, faṣl fī wajh al-ṣawāb fī taʿlīm al-ʿulūm — "wa-muraʿāt istiʿdād al-mutaʿallim wa-qabūlihi" — the readiness and receptivity of the learner for whom the work is pitched; al-qāriʾ al-maqṣūd (القارئ المقصود) is an acceptable equivalent gloss. A sharḥ composed by a muntahī to teach mubtadiʾ students is assigned level="mubtadiʾ"; a ḥāshiya composed for muntahī-level Ḥanafī specialists is assigned level="muntahī" regardless of the underlying matn's native level.

### DEC-SRC-0002 — Science scope uses dynamic registry
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0006; amended per domain-validator-review.yaml
- Chosen option: OPT-B — Growable ordered science list
- Decision rationale: This preserves intake breadth, supports cross-science books such as ahadith al-ahkam, and keeps expansion approval at the registry layer.

### DEC-SRC-0003 — Level detection strategy
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Initial closure on 2026-04-16 by ChatGPT Deep Research (dr-chatgpt-level-detection-20260416.yaml SEC-6). Hardened on 2026-04-17 by a 3-of-3 unanimous adjudication after Claude DR (dr-claude-level-detection-20260416.yaml) recommended OPT-C-asymmetric: Codex CLI (architectural fit, .kr/runtime/adjudication_codex_20260417.md), Gemini CLI runs 1 and 2 (classical scholarly defensibility, 6-0 branch win counts, .kr/runtime/adjudication_gemini_cli_run1_20260417.md and run2_20260417.md), and Gemini DR (T-2 threat model tie-breaker, .kr/runtime/adjudication_gemini_dr_20260417.md) all voted OPT-B with high confidence. Gemini DR additionally proposed a middle-path `level_status` enumerator amendment to CON-SRC-0004 to close the null-conflation gap Claude DR correctly identified — that amendment is adopted on 2026-04-17 and is orthogonal to this decision. Amended 2026-04-23 (Phase 5b item 5) to remove REQ-SRC-0007 from depends_on — the original listing caused a producer-consumer cycle (DEC authorizes the downstream-owns-level architecture, REQ-SRC-0007 implements handoff preservation within that architecture, so REQ-SRC-0007 consumes DEC, not the reverse). Cycle broken per Codex CAF-1 audit finding. Re-confirmed 2026-04-23 (Phase 5b item 7, ownership story closure) by a 3-of-3 UNANIMOUS_OWN_SYNTHESIS HIGH-confidence verdict (Codex CLI gpt-5.4 architectural-fit axis; Gemini CLI Run A gemini-3.1-pro-preview classical-scholarly-defensibility; Gemini CLI Run B gemini-2.5-pro classical-scholarly-defensibility) closing the synthesis-vs-taxonomy sub-question that the 2026-04-17 OPT-B adjudication had inherited silently from ChatGPT DR p19 without re-adjudication against Claude DR's p9_taxonomy_authoritative_owner counter-argument. Phase 5a reviewer wave (Codex CAF-2 + CC-adversary ADV-003) had flagged this as ownership paper-reconciliation 2-of-4. Verdict rationale: martaba is a synthetic/pedagogical act (Ibn Khaldūn Muqaddima Book VI; al-Zarnūjī Taʿlīm al-Mutaʿallim IV) not a bibliographic/taxonomic act (al-Fihrist, Kashf al-Ẓunūn deliberately omit martaba despite cataloging fann and nawʿ); the synthesis engine's mandate to see works as distributed pedagogical units is the architectural home for work-level martaba. Existing rationale wording "Authoritative ownership sits in the synthesis engine." (line 44) and OPT-B.chosen_reason synthesis references are now RATIFIED, not drifted. Zero functional changes to this atom. Synchronized rename in CON-SRC-0004 enum value `pending_taxonomy` → `pending_synthesis` + tightening of generic "a downstream engine" wording to "the synthesis engine" applied in Phase 5b item 7. Reviewer outputs at .kr/runtime/structural_audit_codex_cli_item7_retry_20260423.md and .kr/runtime/domain_validation_gemini_cli_item7_run_{A,B}_20260423.md.
- Chosen option: OPT-B — Downstream content analysis
- Decision rationale: OPT-B is the only architecture that structurally aligns with the rigor of the turāth. ChatGPT DR p16 headline: level inference is downstream and content-based, authoritative ownership sits in the synthesis engine, source engine preserves evidence but does NOT populate level except via rare owner override. ChatGPT DR p17: the book's own discourse — definitions, audience markers, gloss rate, commentary layer — is the most authoritative signal. ChatGPT DR p18: the nullable SourceMetadata.level already models "unknown" cleanly, so OPT-B creates no schema mismatch. ChatGPT DR p19: synthesis is the first place a book can be seen as distributed pedagogical units — the least distortive place to attach a late-bound owner-facing judgment. ChatGPT DR p20: in a personal scholarly library, wrong visible level is more harmful than a temporarily unknown level. ChatGPT DR p21: the three-stage cascade fann → nawʿ/layer → martaba (science → genre/layer → level) is mandatory. Gemini CLI classical analyses (runs 1 and 2) reinforce: Ibn Khaldūn's tadarruj requires level to emerge from internal structural density, al-Zarnūjī's tawaqquf forbids premature commitment, al-Fihrist and Kashf al-Ẓunūn systematically refuse provisional pedagogical tags. Gemini DR T-2 threat model verdict: OPT-B residual T-2 risk (3/10) stems only from the null-conflation ambiguity, which the middle-path `level_status` enum on CON-SRC-0004 entirely mitigates. The source engine remains a pure preserver of raw structural and bibliographic evidence, leaving the authoritative pedagogical ḥukm to the downstream engines capable of examining the matn itself.

### DEC-SRC-0007 — Disputed metadata as multi-position evidence
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0013; amended per contract-architect-review.yaml
- Chosen option: OPT-B — Record all positions in a positions array
- Decision rationale: This keeps disputed metadata truthful and gives REQ-SRC-0012 a stable contract to implement.

### DEC-SRC-0010 — Source hints multi-layer routing and normalization confirms it
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Resolved from OQ-SRC-0002 per domain-validator-review.yaml; amended per 2026-04-14 PDF format directive
- Chosen option: OPT-C — Source hints, normalization confirms
- Decision rationale: This gives source enough responsibility to route early across both Shamela and PDF without pretending format-specific hint evidence is authoritative on its own.

### DEC-SRC-0012 — Multi-position metadata ordered by confidence
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Resolves OQ-SRC-0006; builds on DEC-SRC-0007 and REQ-SRC-0012
- Chosen option: OPT-B — Sort by confidence descending with primary marker
- Decision rationale: Confidence ordering gives downstream engines a natural default (positions[0]) while preserving all scholarly positions. The owner's principle is truth-seeking — all positions stay, but the most-evidenced one is first.

### DEC-SRC-0021 — Pre-Phase-5a SourceMetadata migration — default-on-read at load boundary
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Landed on 2026-04-23 (Phase 5b item 8) and amended same day by the closure wave to add localization and owner-experience constraints. Initial landing resolved Phase 5a adversary finding ADV-013 (severity: HIGH; attack_vector: V5 T-2 corruption; affected_atoms: CON-SRC-0004, REQ-SRC-0007). ADV-013 verbatim description: "Pre-Phase-5a migration corruption. CON-SRC-0004 requires non-null level_status; REQ-SRC-0007 rejects serialization if missing. Legacy sources have no level_status. No atom specifies default-on-read, one-shot migration, or re-admission flow." See `.kr/runtime/adversary_phase5a_20260417.md`:309-316. This decision closes that gap by binding the migration strategy BEFORE any production sources enter the library, so the first admission event after Phase 5b closure operates against a defined policy rather than discovering one ad-hoc. The library is currently empty (no frozen sources admitted as of 2026-04-23); this decision is forward-looking and applies at the moment any SourceMetadata record is loaded whose persisted JSON lacks fields that Phase 5a introduced (level_status mandatory; level_provenance IFF-paired with level; composite_work_type; the 6-value Axis 1 genre set used by CON-SRC-0004 invariant 3).
- Chosen option: OPT-B — Default-on-read at the load boundary with conservative defaults + human_gate routing for ambiguous cases
- Decision rationale: Reversible, non-destructive, D-023-compatible, and safe under the empty-library state. The migration logic is concrete and testable: (i) missing level_status + level null + genre not in NON_APPLICABLE_GENRE_VALUES + composite_work_type != "majmu" ⇒ default level_status=pending_synthesis; (ii) missing level_status + level null + genre in NON_APPLICABLE_GENRE_VALUES (Axis 1) OR composite_work_type=="majmu" (Axis 2) ⇒ default level_status=non_applicable_reference; (iii) missing level_status + level non-null ⇒ ambiguous, raise SRC-E-LEGACY-RECORD-AMBIGUOUS-STATUS and route to human_gate (cannot safely default between assigned and non_applicable_reference without rerunning deliberation); (iv) missing level_provenance + level null ⇒ default level_provenance=null (IFF-consistent with ADV-012 stickiness); (v) missing level_provenance + level non-null ⇒ ambiguous, raise SRC-E-LEGACY-RECORD-AMBIGUOUS-PROVENANCE and route to human_gate (cannot distinguish owner_override from synthesis_engine without additional evidence — OPT-A's rejection-ground 2 at the record level). (vi) missing composite_work_type ⇒ default to None (the field was not present pre-Phase-5a; Axis 2 of INV-SRC-0012 cannot fire for a legacy record lacking the field, so default None is safe and preserves the 3-axis gate invariants). Every migration decision is audited; nothing is silently corrected. Aligns with Critical Rule 4 (errors fail loudly) because ambiguous cases become blocking load-boundary errors rather than silent defaults. Aligns with D-023 (persisted records unchanged) and with INV-SRC-0011 (source engine never infers level from shallow signals — the migration layer defaults level_status from level and genre, which are already-present fields, not inferred content). Closure-wave 2026-04-23 localization constraints (Run A DVF-3, Run B DVF-2, 2-of-2 Gemini convergent on DIM3/DIM6): (vii) Arabic localization of "provenance" in error surfaces MUST use maṣdar al-taqyīm (مصدر التقييم) — the metadata-origin sense — and MUST NOT use sanad (سند), bayyina (بينة), or shahāda (شهادة), which carry hadith-science and uṣūl al-fiqh evidentiary semantics whose conflation with pipeline-provenance is a T-2 corruption vector (cf. al-Khaṭīb al-Baghdādī al-Kifāyah fī ʿIlm al- Riwāyah on transmission-term precision). (viii) the human_gate routing for SRC-E-LEGACY-RECORD-AMBIGUOUS-STATUS and SRC-E-LEGACY-RECORD-AMBIGUOUS-PROVENANCE MUST NOT expose technical enum values or architecture strings (e.g. the literal strings "owner_override" or "synthesis_engine") to the non- technical owner. The owner-facing prompt MUST be framed as a plain-language pedagogical question about the book itself — a canonical example prompt: "هل سبق أن حدّدتَ درجةَ هذا الكتاب بنفسك؟ (Did you previously assign this book's reading level yourself, or was it categorized automatically?)" — referencing the book title in context. The owner knows his own learning history with the text (he placed it, or did not); he does not know the provenance enum universe. Implementation of the human_gate surface is scheduled under follow-up item 30. Phase 5b follow-up 24 (a-lite) closure 2026-04-28 adds constituent-level migration rules: (vii.a) missing ``sub_work_inventory`` ⇒ default to empty list ``[]`` and log ``legacy_migration_event`` with ``fields_defaulted=["sub_work_inventory"]``. The empty default is the natural state for non-composite legacy records (which have no constituent inventory by design). (vii.b) within an existing ``sub_work_inventory`` list, any entry lacking the new placeholder fields (``level``, ``level_status``, ``level_provenance``) inherits the Pydantic defaults (``None``, ``PENDING_SYNTHESIS``, ``None``) via Pydantic field-default semantics — no migration logic required because the new fields are optional with safe defaults. The per-constituent IFF pair-consistency invariant (level non- null IFF level_status == "assigned" IFF level_provenance non- null) enforces that the placeholder triple is structurally sound at construction time. (vii.c) when a legacy record carries ``composite_work_type == "majmu"`` AND the sub_work_inventory default fires (i.e., sub_work_inventory was missing in the persisted JSON), append "sub_work_inventory" to the migration event's ``ambiguous_fields`` list. The default IS LOSSY for majmuʿ records — pre-FU-24 SourceMetadata schema had no sub_work_inventory field, so legacy majmu records lack the carrier; the original IntakeDossier inventory is gone if not independently persisted. The empty default audit-flagged as ambiguous is the documented record so re-intake can surface the constituent inventory if/when needed. NO human_gate routing for vii.c — the system functions without the inventory; re-intake recovers it; the lossy default is documented in the audit trail, not silent. Constituent-level owner override at intake is tracked as Phase 5b item 37 (NOT in scope for legacy migration here). Phase 5b follow-up 37 closure 2026-04-28 adds two further rules for per-constituent override-entrance widening: (vii.d) legacy ``PendingLevelOverride`` payloads pre-FU-37 have no ``constituent_idx`` field. Pydantic field-default semantics handle this transparently — no explicit migration logic required because the new field is optional with a safe default (``None`` = container-level intent, the legacy semantics). Loading a legacy JSON record into the new Pydantic model yields ``constituent_idx=None`` automatically; no audit-trail entry is needed because the default is unambiguous and matches the pre-FU-37 contract (every persisted record was implicitly source-level / container- level keyed). Same Pydantic-default treatment applies to every nested PendingLevelOverride carried on ``MetadataDeliberationResult.pending_level_override`` and ``NormalizationHandoffBundle.pending_level_override``. (vii.e) legacy ``GenreDisputePosition`` payloads pre-FU-37 similarly have no ``constituent_idx`` field. The same Pydantic field-default semantics apply: loading yields ``constituent_idx=None`` (container-level dispute, the legacy semantics). Applies to dispute_snapshot entries on every nested PendingLevelOverride record. arabic-reviewer Agent CRIT-AR-1 and CRIT-AR-2 structural findings closed by these contract widenings are forward-compatible with all legacy records — no rewrites, no human_gate routing, no ambiguous_fields flagging. The widening is purely additive.

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

### INV-SRC-0009 — Zero knowledge loss in all source-engine output
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner directive 2026-04-14. The library NEVER hides, compresses, or simplifies knowledge. Full exhaustiveness and extensiveness in all output. This is a project-wide core rule that applies to every engine and every agent.
- Rule: Every source-engine output preserves the full evidence chain, all considered positions, all reasoning, and all uncertainty. No metadata field, dispute, risk, or finding is hidden, compressed, or simplified in the output. When multiple positions exist, all positions are preserved with their evidence and confidence. When a most-likely resolution exists, it is highlighted but the alternatives are never removed.

### INV-SRC-0011 — Source engine must not infer level from shallow metadata
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-1. Hardened on 2026-04-17 by the 3-of-3 unanimous adjudication (Codex CLI architectural-fit, Gemini CLI runs 1 and 2 classical- defensibility at 6-0 branch win counts, Gemini DR T-2 threat model) that closed DEC-SRC-0003 on OPT-B. Acceptance criterion AC-4 (positive assertion that level_status is still populated when level is null) is added to complement the null-assertion clauses in AC-1 and AC-2. Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-3 in the CON-SRC-0011 classical WorkLevel vocabulary (mutawassiṭ), replacing the earlier English placeholder "intermediate" which would fail the enum whitelist at REQ-SRC-0047 intake validation. Rule statement and implication are unchanged; the amendment is confined to the acceptance criterion surface. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) after the 3-of-3 UNANIMOUS_OWN_ SYNTHESIS verdict (Codex CLI gpt-5.4 architectural-fit + Gemini CLI 2-run gemini-3.1-pro-preview + gemini-2.5-pro classical- scholarly) confirmed the rule.implication's existing naming of "the synthesis engine's ownership of level classification" as correct. The amendment is confined to AC-4's reference to the level_status enum value `pending_taxonomy`, renamed to `pending_synthesis` consistent with CON-SRC-0004's synchronized rename. Rule statement, rule.implication, and AC-1 through AC-3 are semantically unchanged.
- Rule: The source engine MUST NOT compute or infer the level field of SourceMetadata from title tokens, series cues, publisher metadata, or any shallow bibliographic signal. The level field remains null unless an explicit owner_level_override is provided at intake. This invariant does NOT restrict the `level_status` field (CON-SRC-0004), which is a processing-state enum — not a pedagogical-level inference — and whose emission is governed by CON-SRC-0004 alone.

### INV-SRC-0012 — Non-applicable works require level null
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-reports/dr-chatgpt-level-detection-20260416.yaml (SEC-2). Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-1 through AC-4 in the CON-SRC-0011 classical WorkLevel vocabulary (mubtadiʾ, muntahī, mutawassiṭ, muntahī respectively). Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) to introduce the 3-axis non-applicability gate after a 3-cycle pre-commit dispatch with 3 evaluators per cycle (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through /prompt-architect): the prior A/B/C/D cycle blocked unanimously on classical-taxonomy category errors (majmu is a structural composite not a fann; biographical_dictionary is an English alias for tarajim / parent of Genre.TABAQAT; rijal_dictionary is a nawʿ of tabaqat/tarikh/hadith); the Option E cycle blocked unanimously on DIM4 archival-genre regression (the reduced 2-value {mushaf, hadith_collection} set left existing archival Genres MASHYAKHAH / THABAT / BARNAMAJ silently level-applicable); the Option E-prime cycle returned unanimous AMEND_REQUIRED adding FAHRASAH as convergent scholarly guidance (same archival-reference class as mashyakhah / thabat / barnamaj) with Codex PROCEED_WITH_AMENDMENTS confirming structural soundness of the 6-value expansion. Axis 1 now enumerates six Genre members; Axis 2 adds the composite_work_type == "majmu" signal from IntakeDossier (REQ-SRC-0038); Axis 3 was deferred to Phase 5b item 23 (HadithSubgenre ARBAIN pedagogical carve-out) and is activated below. Amended on 2026-04-26 (Phase 5b item 23) to ACTIVATE Axis 3 with the conservative single-value carve-back set LEVELED_HADITH_SUBGENRES = {arbain}, with Path A semantics (default None subgenre fires Axis 3 — transmission-by-default per the *iḥtiyāṭ* / *tawaqquf* principle, Ibn Ḥajar *Nuzhat al-Naẓar* Bāb al-Khabar al-Maqbūl, al-Suyūṭī *Tadrīb al-Rāwī* Nawʿ 23). 3-evaluator wave (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through /prompt-architect): 3-of-3 BLOCKED the original draft's plan to overload HadithSubgenre.ARBAIN as a generic pedagogical proxy for Bulūgh al-Marām and Riyāḍ al-Ṣāliḥīn (Codex CRITICAL DIM4 BLOCK + 2-of-2 Gemini CRITICAL DIM4 amend); 3-of-3 PROCEEDED on Path A default (al-Kattānī *al-Risālah al- Mustaṭrafah* p. 69-72 *Kutub al-Arbaʿīniyyāt* + iḥtiyāṭ); 2-of-2 Gemini AMEND on Arabic-anchor injection (كُتُب الرِّوَايَة into rejection error strings); Codex AMEND on queue-path regression tests + named-test strengthening (Axis 3 substring + hadith_subgenre pin). The Geminis' constructive proposal to introduce HadithSubgenre.AHKAM and MUKHTARAT enum values for famous pedagogical anthologies (Bulūgh al-Marām → AHKAM; Riyāḍ al-Ṣāliḥīn → MUKHTARAT, per al-Kattānī *al-Risālah al-Mustaṭrafah* p. 41/44 *Kutub al-Aḥkām*) is deferred to NEW follow-up 34 — substantive contract-change scope beyond ARBAIN-only carve-back. New AC-5 (ARBAIN positive — al-Arbaʿīn al-Nawawī accepts owner override) and AC-6 (MUSNAD negative — Musnad Aḥmad rejects with explicit Axis 3 citation) added. The "مصنف" → MUSANNAF inference extension bundled (Codex CRITICAL DIM4 fix). See follow-up items 21 (FATAWA/MUJAM naming resolution), 22 (mawsūʿa/muʿjam/fihris non-applicable expansion), 24 (majmuʿ constituent-rasāʾil leveling architecture), and 34 (HadithSubgenre.AHKAM + MUKHTARAT enum addition for selected-hadith pedagogical anthologies). Amended on 2026-04-27 (Phase 5b follow-ups 25 + 26 paired closure) to EXTEND NON_APPLICABLE_GENRE_VALUES from six values to eight by adding ``mujam`` and ``tabaqat``, after a paired-PRELIMINARY- confirmation dispatch wave (Gemini CLI Run B scholarly + Codex CLI structural, both through /prompt-architect). Run B scholarly verdicts: FU-25 AMEND HIGH (Option A genre-level — disagreed with Run-A item4e's Option B sub-genre-only carve-out, on the basis that BOTH linguistic lexicons AND hadith muʿjam works share the same non-linear alphabetical-index reference architecture); FU-26 CONFIRM HIGH (Option α genre-level — full convergence with Run-A item4eprime). Run B governing principle (own-words): a genre belongs in NON_APPLICABLE_GENRE_VALUES when its organizing architecture operates as a static repository of attestation, indexing, or archival documentation rather than a graduated didactic curriculum. Codex CLI structural reasoning (executable Python probes of ``_infer_genre`` outputs, ripgrep across all source-engine tests and fixtures, direct read of GenreDisputePosition contract): zero existing test ripple (no fixtures or override tests assert Genre.MUJAM or Genre.TABAQAT behavior); double-classification of hadith-muʿjam and hadith-ṭabaqāt titles is real but harmless because Axis 1 fires before Axis 3 for non-hadith_collection genres in ``_non_applicability_axis``; **Option B/β subgenre-only carve-out is structurally inadequate on the dispute path** because GenreDisputePosition (contracts.py:770) carries only ``genre_candidate``, not a hadith-subgenre candidate, so the override-queue's unanimous-nonapplicable branch can only adjudicate via ``genre_candidate ∈ NON_APPLICABLE_GENRE_VALUES``. The genre- level fix (Option A + Option α) was therefore the only architecturally complete path. Classical anchors: al-Kattānī, *al-Risālah al-Mustaṭrafah*, "Kutub al-Maʿājim" section (~p. 110+ in Dār al-Bashāʾir ed.); al-Suyūṭī, *Tadrīb al-Rāwī*, Nawʿ 61 (*Maʿrifat al-Ṭabaqāt*); Ibn Khallikān, *Wafayāt al-Aʿyān*, author's introduction; Ibn al-Nadīm, *al-Fihrist*. New AC-7 (MUJAM positive — al-Muʿjam al-Kabīr li-l-Ṭabarānī rejects owner override on Genre.MUJAM Axis 1) and AC-8 (TABAQAT positive — al- Ṭabaqāt al-Kubrā li-Ibn Saʿd rejects owner override on Genre.TABAQAT Axis 1) added. Documented limitation: hadith-muʿjam and hadith-ṭabaqāt titles double-classify (Genre.MUJAM/TABAQAT + HadithSubgenre.MUJAM/TABAQAT_RIJAL fire simultaneously); under the Axis 1 firing on the genre, the redundant subgenre is harmless metadata. Documented latent gap: GenreDisputePosition carries no hadith-subgenre candidate; future need for subgenre-level dispute adjudication would require widening that contract — captured for potential future follow-up if/when the need surfaces. Amended on 2026-04-27 (Phase 5b follow-up 22 closure) to EXTEND NON_APPLICABLE_GENRE_VALUES from eight values to nine by adding ``mawsuah``, after a focused single-evaluator dispatch wave (Gemini CLI Run-B-style scholarly with anti-priming protocol — Step-1 first- principles commitment locked before Step-2 confrontation with prior runs — through /prompt-architect). 2-of-2 cross-time independent Gemini scholarly convergence: original Run-A item-4 DIM4 (2026-04-21) verdict CONFIRM = ADD, plus FU-22 paired-confirmation Run B (2026-04-27) verdict ADD high. Original Run-B AMEND (2026-04-21, raising classical-vs-modern anachronism risk on retroactive application of the modern term to classical works) explicitly reconciled: the structural fact that ``_infer_genre`` (deliberation.py :496-504) has no keyword trigger for "موسوعة" — the deterministic classifier never assigns Genre.MAWSUAH from a title; it can only enter the system through deliberate owner_metadata override or a future agent-layer classifier, where the assignment is deliberate precisely because the work *functions* as an encyclopedia. The modern Arabic loan موسوعة (mawsūʿa, 19th–20th-century calque of European *encyclopedia*) names comprehensive reference works arranged alphabetically or thematically for lookup, not sequential reading; classical functional analogues (Ibn al-Athīr's al-Nihāyah fī Gharīb al-Ḥadīth d. 606 AH; Ḥājī Khalīfa's Kashf al-Ẓunūn d. 1067 AH; Ibn al-Nadīm's al-Fihrist d. ~385 AH) share the same static-repository architecture. Governing inclusion principle (distilled from FU-25/26 Run-B verdicts): "a genre belongs in NON_APPLICABLE_GENRE_VALUES when its organizing architecture operates as a static repository of attestation, indexing, or archival documentation rather than a graduated didactic curriculum." Mawsūʿa satisfies all three branches — attestation (jāmiʿ-scale comprehensive compilation: al-Ṭabarī's Jāmiʿ al-Bayān, Ibn Rajab's Jāmiʿ al-ʿUlūm wa-l-Ḥikam), indexing (alphabetical organization), archival documentation (al-Khaṭīb al-Baghdādī's Tārīkh Baghdād). New AC-9 (MAWSUAH positive — al-Mawsūʿa al-Fiqhiyya al-Kuwaytiyya rejects owner override on Genre.MAWSUAH Axis 1) added. Documented limitation: hybrid works titled "موسوعة الناشئة" (youth encyclopedia) with internal pedagogical sequence are rare exceptions; the invariant correctly prioritizes the dominant architectural function. Open follow-ups remaining: 18, 21, 24, 27, 28, 34. Amended on 2026-04-27 (Phase 5b follow-up 34 closure) to ACTIVATE HadithSubgenre.AHKAM in the carve-back set, expanding LEVELED_HADITH_ SUBGENRES from {arbain} to {arbain, ahkam}. 3-evaluator wave (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through /prompt-architect with RISEN + Step-Back + CAI Critique-Revise hybrid): 2-of-2 Gemini scholarly convergence at HIGH confidence on ADD AHKAM (Run A AMEND_REQUIRED + Run B PROCEED, both demanding compound- keyword discipline) and on BLOCK MUKHTARAT (al-Ḍiyāʾ al-Maqdisī's *al-Aḥādīth al-Mukhtārah* d. 643 AH is primary transmission with full isnāds despite the name; *Mukhtārāt* is a cross-cutting descriptor not a standalone subgenre per al-Kattānī's bibliographic taxonomy). Codex CLI returned CRITICAL DIM5 BLOCK on the dispute-path latent gap (GenreDisputePosition carried only genre_candidate, so disputed hadith_collection works with leveled subgenres would auto-reject on Axis 1 alone), resolved by widening GenreDisputePosition with hadith_subgenre_candidate (contracts.py:820-826) and updating _resolve_disputed (override_queue.py:295-345) to consult the carve- back. DIM6 AMEND aligned migration._default_level_status with Axis 3 membership (legacy hadith_collection payloads with leveled subgenres now default to pending_synthesis, not non_applicable_reference). AHKAM inference is restricted to compound-keyword patterns per Run A's S1.Q3 keyword-reliability ceiling and Run B's Q4a recommendation: 6 ordered compound rules (بلوغ + المرام / عمدة + الأحكام / الإلمام + الأحكام / المنتقى + الأحكام / أدلة + الأحكام / أحاديث + الأحكام); bare أحكام is FORBIDDEN due to false-positive collisions with Aḥkām al-Qurʾān (al-Jaṣṣāṣ d. 370 AH — fiqh-tafsīr), al-Aḥkām al-Sulṭāniyyah (al-Māwardī d. 450 AH — siyāsah), al-Iḥkām fī Uṣūl al-Aḥkām (al-Āmidī d. 631 AH — Uṣūl al-Fiqh), and Iḥkām al-Aḥkām Sharḥ ʿUmdat al-Aḥkām (Ibn Daqīq al-ʿĪd d. 702 AH — sharḥ, not primary aḥkām collection). المحرر alone is also forbidden because it collides with al-Muḥarrar fī al-Fiqh (Majd al-Dīn Ibn Taymiyyah). The AHKAM compound rules are inserted AFTER the HADITH_COMMENTARY branch in _infer_hadith_subgenre so that a sharḥ on an aḥkām collection (e.g., Iḥkām al-Aḥkām Sharḥ ʿUmdat al-Aḥkām) is correctly tagged HADITH_COMMENTARY rather than AHKAM. Constructive Gemini Run-B proposals to also add HadithSubgenre. TARGHIB (Kutub al-Targhīb wa-l-Tarhīb per al-Kattānī p. 45), HadithSubgenre.MUKHTASAR (Kutub al-Mukhtaṣarāt), and HadithSubgenre. SHAMAIL (al-Shamāʾil al-Muḥammadiyyah of al-Tirmidhī d. 279 AH) were deferred to NEW follow-up 35 — substantive contract-change scope beyond FU-34's AHKAM + MUKHTARAT charter. New AC-10 (AHKAM positive — Bulūgh al-Marām accepts owner override), AC-11 (AHKAM scope-disambiguation negative — al-Muntaqā of Ibn al-Jārūd is transmission-style despite aḥkām theme, no compound rule fires), and AC-12 (AHKAM false-positive guard — al-Iḥkām fī Uṣūl al-Aḥkām of al-Āmidī inferred as None subgenre because no compound matches "Uṣūl al-Aḥkām" pattern) added. Open follow-ups remaining after FU-34 closure: 18, 24, 27, 28, 35 (NEW). Amended on 2026-04-28 (Phase 5b follow-up 24 (a-lite) closure) to CLOSE the AC-3 / AC-4 deferred-promise ("Constituent-rasāʾil leveling is tracked as Phase 5b item 24" / "Individual-fatwa-level pedagogy remains tracked as Phase 5b item 24") via the hybrid-resolution path: the SubWorkInventoryEntry contract is widened with a per-constituent placeholder triple (level: Optional[WorkLevel] = None, level_status: LevelStatus = PENDING_SYNTHESIS, level_provenance: Optional[ LevelProvenance] = None) plus a pair-consistency model_validator mirroring SourceMetadata invariants 1-2; ``IntakeDossier.sub_work_ inventory`` propagates onto ``SourceMetadata.sub_work_inventory`` via ``_populate_deterministic_metadata`` so the constituent placeholder surface flows through the source→normalization handoff via the existing dispatcher ``model_copy(deep=True)`` (D-023). Container Axis 2 firing on ``composite_work_type=="majmu"`` REMAINS UNCHANGED; the placeholder surface is independent of the container's non- applicability gate. Source engine never WRITES per-constituent level (DEC-SRC-0003 — synthesis owns level writes). 4-evaluator dispatch wave was launched for FU-24 (Codex CLI structural + Gemini Run A scholarly + Gemini Run B scholarly + arabic-reviewer Anthropic Agent, all through /prompt-architect with RISEN + Step-Back + CAI Critique- Revise hybrid framework). Codex (a-lite) ISOMORPHIC at source-model level + NEW at first cross-engine boundary. Gemini Run A and Run B both recommended (a+b) HIGH at 2-of-2 cross-time independent scholarly convergence (classical anchors: al-Kattānī al-Risālah al-Mustaṭrafah on majmūʿāt + rasāʾil; Ibn Khaldūn Muqaddima Book VI on tadarruj / pedagogical progression; al-Zarnūjī Taʿlīm al-Mutaʿallim Ch. IV on tawaqquf in text selection). The arabic-reviewer Agent dispatch FAILED twice (Anthropic billing extra-usage cap + 600s stream watchdog stall); CC main-thread substituted with the structural cross-provider DIM-AR2 check (codebase fact-finding, objectively verifiable) and a non-independent scholarly framework alignment (with full disclosure of prior Gemini exposure). The substantive scholarly verdict (a+b) is converged 3-of-4 at HIGH but the cross- provider Anthropic-side check is methodologically incomplete. Hybrid-resolution chosen: implement (a-lite) NOW (boundary widening + placeholder surface; minimum scope; CRIT-1 cross-engine ripple MOOT because ``sub_work_inventory`` rides ``SourceMetadata`` through the dispatcher's existing ``model_copy(deep=True)``; CRIT-2 keyspace explosion MOOT because intake override stays single-keyed at source level; CRIT-3 legacy migration addressed via DEC-SRC-0021 rule (vii.a/b/c)) and OPEN NEW follow-up 37 to track the constituent- level owner-override-entrance widening (REQ-SRC-0047 entrance signature widened to per-constituent keying + PendingLevelOverride keyspace from source_id to (source_id, constituent_idx)) plus the arabic-reviewer Agent retroactive validation that failed this session. The Geminis' BLOCK on (a-lite) ("decisively incomplete") is honored by FU-37 carrying the obligation forward, NOT by silent denial. Owner UX gap is documented as known limitation pending FU-37. New AC-FU24-A added below capturing the constituent placeholder semantics. Open follow-ups remaining after FU-24 closure: 18, 27, 28, 36, 37 (NEW). Amended on 2026-04-28 (Phase 5b follow-up 37 closure) to CLOSE the FU-24 deferred owner-override-entrance promise via the (a+b) hybrid-resolution path validated by 4-of-4 cross-provider scholarly+structural convergence at HIGH confidence (Codex CLI structural + Gemini Run A/B + arabic-reviewer Anthropic Agent). arabic-reviewer's NOVEL classical anchor al-Suyūṭī *Tadrīb al-Rāwī* Muqaddimah on *iʿtibār* discipline (preserve raw evidence at finest granularity to enable sound *ḥukm*) — independent of either Gemini and not in the sealed prior-evaluator block — closed the cross-provider Anthropic-side scholarly check that FU-24 had to defer due to Anthropic billing cap + 600s stream stall. arabic-reviewer's structural cross-provider check surfaced TWO new CRITICAL findings: CRIT-AR-1 (PendingLevelOverride was per-source-keyed and could not persist per-constituent intent without ambiguity) and CRIT-AR-2 (GenreDisputePosition lacked constituent identifier for per-constituent dispute snapshots). Both addressed by contract widening: ``PendingLevelOverride.constituent_idx: Optional[int] = Field(default=None, ge=0)`` and ``GenreDisputePosition.constituent_idx: Optional[int] = Field(default=None, ge=0)``. Plus the entrance widening: ``MetadataDeliberationInput.owner_constituent_level_overrides: dict[int, WorkLevel]`` accepts per-constituent owner intent for *majmūʿ* sources; ``deliberation._queue_constituent_overrides`` validates ``constituent_idx`` is non-negative and in range of ``sub_work_inventory`` and the source is composite_work_type == "majmu" (raises SRC-E-LEVEL-OVERRIDE-CONSTITUENT-INVALID otherwise). Per-constituent overrides at intake are ALWAYS QUEUED (deferred to synthesis) because constituent-level genre is unknown at the source-engine stage; synthesis applies/rejects via the standard INV-SRC-0012 3-axis gate per DEC-SRC-0003. Container Axis 2 firing on ``composite_work_type=="majmu"`` REMAINS UNCHANGED — per- constituent intent does NOT override container non-applicability; both states coexist via the new ``MetadataDeliberationResult.pending_constituent_level_overrides: list[PendingLevelOverride]`` field. Methodology gap disclosure: the arabic-reviewer wrapper at ``.kr/runtime/_followup_37_arabic_reviewer_wrapper_optimized.md`` contained the sealed prior-evaluator block in-file, so file-read sequence independence is technically compromised; analytical independence is supported by novel anchor + novel structural findings + novel framing. New ACs AC-FU37-1 through AC-FU37-9 added below. Open follow-ups remaining after FU-37 closure: 18, 27, 28, 36. Amended on 2026-04-29 (Phase 5b follow-up 36 closure) after a 4-evaluator cross-provider dispatch (Codex CLI gpt-5.4 + Gemini Run A/B gemini-2.5-pro + arabic-reviewer Anthropic Agent, all through /prompt-architect with CAI Critique-Revise + Step-Back + TIDD-EC hybrid framework — same framework vindicated by FU-37). The FU-37 sealed-block-in-separate-file rectification was applied for the first time and SUCCEEDED for Codex and arabic-reviewer (full Read-tool-call file-read sequence verified); Geminis used cat-via-shell because .kr/ is gitignored, producing a slightly weaker but still observable file-read sequence in their tool-call log. Q-B (HadithSubgenre.ADHKAR) and Q-C (HadithSubgenre.ADAB) PROCEED at 3-of-4 cross-provider convergence — both values added to the enum and EXCLUDED from LEVELED_HADITH_SUBGENRES per the SHAMAIL precedent (chain-preservation in canonical anchors: Ibn al-Sunnī's *ʿAmal al-Yawm wa-l-Laylah* d. 364 AH for ADHKAR; al-Bukhārī's *al-Adab al-Mufrad* d. 256 AH for ADAB). Q-A (is_abridgement orthogonal property) BLOCKED at 2-of-4 cross- provider convergence (Codex + arabic-reviewer): all enumerated PROCEED paths failed to wire into the level gate (_non_applicability_axis / enforce_level_invariants) or the dispute path (_resolve_disputed) — architecturally incomplete; Geminis recommended PROCEED but DIVERGED between path-2 (per-constituent) and path-3 (genre migration), weakening the cross-time independent signal. Per .claude/rules/no-single- model-conclusion.md no path achieved 4-of-4 HIGH; the 2-of-4 BLOCK position prevails on Q-A. Documented limitations added below (L-FU36-1, L-FU36-2). Novel anchors surfaced this dispatch: Ibn al-Nadīm's *al-Fihrist* d. ~385 AH (organizes mukhtaṣarāt under source works — earliest Islamic bibliography to make this choice); al-Khaṭīb al-Baghdādī's *al-Jāmiʿ li-Akhlāq al-Rāwī wa-Ādāb al-Sāmiʿ* d. 463 AH (riwāyah-class vs taʿlīm-class distinction explaining ADHKAR's non-uniform chain treatment); al-Suyūṭī's *Tadrīb al-Rāwī* Muqaddimah on *aqsām al-kutub al-muṣannafah* (al-Adab al-Mufrad classified in *aʿmāl wa-l-ādāb* sub-category of *muṣannaf*, NOT *jāmiʿ* — definitively refuting Q-C path-2 KEEP-AS-JAMI-VIA-NEW-KEYWORD which all 4 evaluators unanimously rejected). CRITICAL naming- collision finding (CRIT-FU36-1, surfaced independently by both Codex and arabic-reviewer): HadithSubgenre.ADAB has the same string value "adab" as Genre.ADAB at contracts.py:158; display layers MUST disambiguate by enum-class context — JSON serialization outputs "adab" for both and deserialization without type context is ambiguous (T-1 risk). New ACs AC-FU36-1 through AC-FU36-5 added below covering ADHKAR positive (al-Nawawī's *al-Adhkār*) + ADHKAR exclusion (Ibn al-Sunnī's *ʿAmal al-Yawm wa-l-Laylah* tagged correctly but Axis-1 rejection) + ADAB positive (al-Bukhārī's *al-Adab al-Mufrad* tagged correctly but Axis-1 rejection) + Q-C path-2 unanimously- rejected JAMI-via-keyword regression guard + ADHKAR/ADAB false- positive guards via science-scope pre-condition + compound- keyword discipline. Documented limitations: L-FU36-1 (_extract_target narrowness — `_infer_work_relationships` at deliberation.py:817 uses ("مختصر",) as the sole target-extraction marker, so works classified as Genre.MUKHTASAR via خلاصة/تهذيب/تقريب/ملخص/وجيز keywords get Genre.MUKHTASAR but NOT the is_abridgement_of WorkRelationship — surfaced by arabic-reviewer DIM-AR2 AR2-QA-1); L-FU36-2 (gate-semantics gap for hadith abridgement owner-override rejection — would require future architectural path-5 with dual-surface metadata + explicit INV-SRC-0012 wiring + GenreDisputePosition abridgement_candidate field analogous to FU-34's hadith_subgenre_candidate; surfaced by Codex DIM-CDX3 + arabic-reviewer DIM-AR2 convergent finding). Open follow-ups remaining after FU-36 closure: 18, 27, 28.
- Rule: For works where the reading-level concept does not apply, the source engine MUST serialize SourceMetadata.level as null regardless of any owner override attempt. Non-applicability fires along three axes, any of which is sufficient: Axis 1 (fann-level) — the work's Genre is one of the nine non-applicable members {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah, mujam, tabaqat, mawsuah}; Axis 2 (structural) — the work's composite_work_type == "majmu" (a structural composite whose container-level pedagogy does not apply even when the declared Genre is otherwise leveled); Axis 3 (hadith-subgenre) — when Axis 1 fires for Genre.HADITH_COLLECTION, attribution is refined by hadith_subgenre. Subgenres in the carve-back set LEVELED_HADITH_SUBGENRES (currently {arbain, ahkam, targhib}) reverse the Axis 1 firing — the work is treated as a pedagogical hadith curriculum: ARBAIN covers al-Arbaʿīn al-Nawawī of al-Nawawī (d. 676 AH) and the broader arbaʿūniyyāt genre per al-Kattānī, al-Risālah al-Mustaṭrafah p. 69-72 Kutub al-Arbaʿīniyyāt; AHKAM covers selected-hadith pedagogical anthologies of legal evidences per al-Kattānī, al-Risālah al-Mustaṭrafah p. 41 Kutub al-Aḥkām (Bulūgh al-Marām min Adillat al-Aḥkām of Ibn Ḥajar d. 852 AH; ʿUmdat al-Aḥkām of ʿAbd al-Ghanī al-Maqdisī d. 600 AH; al-Muntaqā fī al-Aḥkām of Majd al-Dīn Ibn Taymiyyah d. 652 AH; al-Ilmām bi-Aḥādīth al-Aḥkām of Ibn Daqīq al-ʿĪd d. 702 AH); TARGHIB covers Kutub al-Targhīb wa-l-Tarhīb per al-Kattānī, al-Risālah al-Mustaṭrafah p. 45 (canonical anchor al-Targhīb wa-l-Tarhīb of al-Mundhirī d. 656 AH) plus Riyāḍ al-Ṣāliḥīn of al-Nawawī d. 676 AH classified under TARGHIB via the dedicated compound rule "رياض" + "الصالحين" closing the FU-34 documented limitation. AHKAM was activated by Phase 5b follow-up 34 (2026-04-27) after 2-of-2 cross-time independent Gemini scholarly convergence at HIGH confidence and Codex CRITICAL DIM5 BLOCK resolution that widened GenreDisputePosition with hadith_subgenre_candidate to enable correct dispute-path adjudication. TARGHIB was activated by Phase 5b follow-up 35 (2026-04-28) after 4-of-4 cross-provider evaluator convergence (Codex CLI structural ISOMORPHIC + Gemini Run A scholarly + Gemini Run B scholarly + arabic-reviewer Anthropic scholarly cross- provider, all through /prompt-architect with anti-priming Step-1/ Step-2 protocol; 3-of-3 cross-provider scholarly verdict at HIGH confidence on every cell). The level applies to AHKAM and TARGHIB works. SHAMAIL is enum-recognized (Ḥājī Khalīfa, Kashf al-Ẓunūn 2/1043 lists shamāʾil as a distinct fann; al-Kattānī recognizes Kutub al-Shamāʾil) but EXCLUDED from LEVELED_HADITH_SUBGENRES because its canonical anchor al-Shamāʾil al-Muḥammadiyyah of al-Tirmidhī (d. 279 AH) PRESERVES full transmission chains (cited isnād from "Bāb Mā Jāʾa fī Khātam al-Nubuwwah": حدثنا قتيبة بن سعيد، قال: حدثنا حاتم بن إسماعيل، عن الجعد بن عبد الرحمن، قال: سمعت السائب بن يزيد يقول...). Per the iḥtiyāṭ precautionary framework plus arabic-reviewer's compound BLOCK criterion (chain-preservation + absence of pedagogical muqaddimah + comprehensive-not-graduated organization), SHAMAIL hadith_ collection works are correctly tagged but Axis 3 carve-back does NOT fire — owner override is REJECTED under Axis 1. MUKHTASAR was BLOCKED entirely (NOT added to enum) per 3-of-3 cross-provider scholarly verdict at HIGH: cross-cutting structural descriptor not a standalone hadith subgenre (Ḥājī Khalīfa lists mukhtaṣarāt under source works as derivatives, not in a dedicated chapter); the arabic-reviewer's structural cross-provider check additionally surfaced that KR already encodes mukhtaṣar at the Genre level (Genre.MUKHTASAR at contracts.py:145, mapped from keywords مختصر/خلاصة/تهذيب/تقريب/ملخص/وجيز in deliberation.py:55) — adding HadithSubgenre.MUKHTASAR would create semantic redundancy and the pre-condition early-exit at deliberation.py:537 would render any HadithSubgenre.MUKHTASAR rule unreachable for Genre.MUKHTASAR works. All other hadith subgenres — including null subgenre per Path A (transmission-by-default, iḥtiyāṭ / tawaqquf principle, Ibn Ḥajar Nuzhat al-Naẓar Bāb al-Khabar al-Maqbūl) — confirm Axis 1 firing under Axis 3 (the work is kutub al-riwāyah, transmission collection). Forcing a reading- level label onto an Axis-1 (post-carve-back), Axis-2, or Axis-3 firing work creates false scholarly authority because its organizing principle is transmission, archival reference, or structural compilation, not graduated pedagogical exposition.

### INV-SRC-0013 — No definitive scholar match from under-specified fragment (≥2 non-name floor)
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §2.2 — Pivot (b) operationalization adjudication. Cross-provider 2-of-2 concept convergence on ≥2-corroborating-attribute floor (Claude DR §6 + ChatGPT DR §6). Synthesis adopts Claude DR's STRICTER ≥2-NON-NAME formulation per knowledge-integrity primacy and Owner Principle 3 (zero-tolerance for attribution errors). 4-evaluator wave (Codex CLI / arabic-reviewer / Gemini Run A / Gemini Run B): 4-of-4 UNANIMOUS HIGH on Pivot (b). Classical anchor: al-Khaṭīb al-Baghdādī, al-Mukmil fī Bayān al-Mahmal — "external markers needed" maps directly to non-name corroboration; al-Khaṭīb's external markers (city of audition, dating of samāʿ, immediate teacher) are EXPLICITLY non-name signals. Name expansion (longer nasab chain, additional nisba) is the SAME KIND of signal as the fragment, not an external marker.
- Rule: A scholar match-call result with disambiguation_state = "definitive" is permitted only when ≥2 non-name attributes intersect between dossier-side context and registry-side record. Eligible non-name attributes are exactly: century_active_hijri, school_affiliations[science], primary_science, secondary_sciences, attributed_works, region_origin, region_active, teacher_student_link. Name expansion (nasab, nisba, kunyah, laqab) is NOT corroboration for the ≥2 floor; name expansion remains eligible as Stage-2 scoring evidence but does not unlock the definitive terminal. The check is binary and auditable: "did the matched record share ≥2 non-name attributes with the dossier? yes/no" — recorded in provenance.threshold_audit.corroboration_count_ge_2.

### INV-SRC-0014 — Matching-key honorific exclusion with bidi-strip ordering
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §5.3 (renumbered from ChatGPT DR's stale INV-SRC-0011 to INV-SRC-0014 per repo verification — slot 0011 already taken by "Source engine must not infer level from shallow metadata"). arabic-reviewer Stage-3 wave Novel Finding 1 (bidi-mark contamination ordering, T-1 → T-2 risk path): existing name_matching.py honorific list (28 single + 8 multi at shared/scholar_authority/src/name_matching.py:33-99) does NOT address invisible Unicode bidi marks (U+200E, U+200F, U+202A-202E) in honorifics extracted from Shamela HTML; when an honorific like "الشيخ" carries an embedded bidi mark, the stripping regex may fail to match, leaving the honorific in the match key. 4-evaluator wave: PARTIAL_ALIGN on Pivot (a) but SURFACED finding accepted as Stage-4 input. Existing error code SRC-E-HONORIFIC-ONLY-NAME (contracts.py:579) cited in F-6 closure surface (synthesis §1.4).
- Rule: Match-key construction MUST apply normalization in this exact order: (1) invisible-Unicode strip per .claude/rules/input-sanitization.md targeting U+200E, U+200F, U+202A through U+202E, U+200B, U+200C, U+200D (with the carve-outs noted in input-sanitization.md for Persian/Urdu/Kurdish source markers), U+FEFF, U+2060, U+00AD; THEN (2) honorific normalization using the existing name_matching.py honorific list (28 single tokens at _SINGLE_HONORIFICS plus 8 multi-token honorifics at _MULTI_HONORIFICS); THEN (3) match-key construction. The ordering is non-commutative — applying (2) before (1) leaks bidi-contaminated honorifics into the match key. Honorifics are EXCLUDED from match keys but PRESERVED in display fields. If stripping leaves an empty match key (the fragment was honorific-shell only), the match call aborts with existing error code SRC-E-HONORIFIC-ONLY-NAME (contracts.py:579) — this is the F-6 closure surface from synthesis §1.4.

### INV-SRC-0016 — Verifier chosen_id closure — F-4 hallucination prevention
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §5.3 (Claude DR INV-SRC-NEW-1 renumbered to INV-SRC-0016 per repo verification — slot 0016 verified clean against engines/source/spec/INDEX.yaml). F-4 (LLM hallucinates non- existent scholar) closure surface per synthesis §1.4 failure- mode catalog. Cross-provider 2-of-2 ratification: Claude DR §10 + ChatGPT DR §10 both identify F-4 as a critical failure mode requiring verifier-output validation. The invariant is the structural barrier preventing a hallucinated scholar identity from finalizing a case.
- Rule: Every verifier output (round-0 or round-1) MUST select chosen_id from CON-SRC-0009.candidate_set. The orchestrator validates this closure on every verifier output before any routing decision (REQ-SRC-0053) reads the verdict. An output whose chosen_id is not present in candidate_set is REJECTED, marked as F-4 hallucination in the audit log, and the verifier's output is treated as a STRUCTURAL DISAGREEMENT — escalates the case to disputed terminal with positions[] populated from the LEGITIMATE (in-packet) candidates only. The hallucinated identity is logged for audit (Critical Rule 13 — all data is future training material) but is NEVER finalized as canonical_scholar_id. The closure rule applies to BOTH round-0 and round-1 outputs; round-1 cannot introduce a new candidate (the packet is immutable per CON-SRC-0009).

### INV-SRC-0017 — Registry snapshot version pin — F-7 cross-time-inconsistency closure
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Phase 5 scholar-matching DR synthesis (2026-04-30) §5.3 (Claude DR INV-SRC-NEW-3 renumbered to INV-SRC-0017 per repo verification — slot 0017 verified clean against engines/source/spec/INDEX.yaml). F-7 (cross-time inconsistency — registry mid-pipeline drift) closure surface per synthesis §1.4 failure-mode catalog. Cross-provider 2-of-2 ratification: Claude DR §10 + ChatGPT DR §10 both identify F-7 as a critical failure mode requiring snapshot pin discipline. Codex Stage-3 Defect 2 fix applied: registry_release_version is the canonical name applied uniformly across REQ-SRC-0049 + CON-SRC-0008 + INV-SRC-0015 + this invariant.
- Rule: The pipeline MUST be pinned to provenance.registry_release_version at intake. Every CON-SRC-0008 ScholarMatchResult MUST record the pinned registry_release_version (per INV-SRC-0015). Re-attribution after a registry release bump is EXPLICIT REPLAY, not silent re-resolution: a match call that re-runs against a newer release MUST emit a NEW CON-SRC-0008 with the newer registry_release_version, and MUST log the prior result-id + the prior registry_release_version pair in revision_history (per Critical Rule 13: all data is future training material; provenance of the prior verdict is preserved). Any case where the registry snapshot drifts mid-pipeline (e.g., orchestrator restart loads a different release; concurrent registry update mutates the snapshot) aborts finalization, discards verifier outputs from the in-flight case, and restarts candidate generation against the new snapshot per REQ-SRC-0049 error path. The pinned name is registry_release_version canonically (snapshot_version is FORBIDDEN per Codex Stage-3 Defect 2).

### OF-SRC-0004 — Author attribution errors are catastrophic
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 4
- Interview question: Which metadata failure matters most to the owner?
- Owner answer: Author attribution errors are devastating. If attribution fails, the owner would doubt the whole library. This is the number one quality metric.

### OF-SRC-0005 — Science hints follow the same cross-validation rule
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 2 question 1
- Interview question: Should a science hint influence source inference?
- Owner answer: Science hints are optional and follow the same pattern as author hints. They never bias inference and are used only as post-inference cross-validation.

### OF-SRC-0006 — Science registry must keep growing
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 2 question 2
- Interview question: What happens when a book belongs to a science outside the current registry?
- Owner answer: The library never refuses knowledge. Sciences are a growable registry. New sciences may be added with owner confirmation, and no book is rejected only because its science is absent today.

### OF-SRC-0007 — Preserve and infer level metadata from content
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: medium
- Source: Owner interview batch 2 question 3
- Interview question: Is level metadata useful, and how should it be inferred?
- Owner answer: The level field is valuable. The owner recommends detecting it from content analysis rather than relying only on book-level metadata, but the final engine ownership is still unresolved.

### OF-SRC-0008 — Multi-layer detection ownership is unresolved
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: low
- Source: Owner interview batch 2 question 4
- Interview question: Should multi-layer detection happen in source or normalization?
- Owner answer: The owner is unsure. He thinks source-level hints that route normalization may be better, but explicitly said he is not confident about the final boundary.

### OF-SRC-0012 — Hadith classification is the primary benchmark surface
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 3 question 4
- Interview question: Which part of the collection should dominate source-engine quality evaluation?
- Owner answer: Hadith is the owner's main focus and represents 48.7% of the collection. Fine-grained classification within hadith literature is therefore very important.

### OQ-SRC-0001 — Level detection ownership
- Type: question
- Layer: questions
- Step: n/a
- Status: superseded
- Priority: medium
- Confidence: high
- Source: dr-reports/dr-chatgpt-level-detection-20260416.yaml (SEC-7)
- Candidates:
  - OPT-A: Source metadata only (unlikely)
  - OPT-B: Downstream content analysis (likely)
  - OPT-C: Dual inference with reconciliation (possible)

### OQ-SRC-0006 — Ordering and display semantics for multi-position metadata
- Type: question
- Layer: questions
- Step: n/a
- Status: superseded
- Priority: high
- Confidence: medium
- Source: Derived from OF-SRC-0013; narrowed per contract-architect-review.yaml
- Candidates:
  - OPT-A: Preserve input order (possible)
  - OPT-B: Sort by confidence (likely)
  - OPT-C: Weighted display without reordering (possible)

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

### REQ-SRC-0007 — Level field preservation across source-engine handoff
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0007; moved to step 60 on 2026-04-14 because the rule governs handoff packaging rather than metadata deliberation itself. Amended on 2026-04-16 per dr-chatgpt-level-detection-20260416.yaml (SEC-5). Further amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) explicit precondition that owner_level_override passed the CON-SRC-0011 enum-value whitelist before reaching handoff packaging; (b) new level_status (CON-SRC-0004 middle-path) must serialize alongside level — preservation contract extends to both fields. Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-1 (intermediate → mutawassiṭ), AC-3 (advanced → muntahī), and AC-5 (beginner → mubtadiʾ) in the CON-SRC-0011 classical WorkLevel vocabulary. Behaviour, preconditions, postconditions, and error conditions unchanged; the Phase-5a reviewer wave identified the English placeholders as structurally untestable because REQ-SRC-0047 now rejects them at intake against the enum whitelist. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the synchronized `pending_taxonomy` → `pending_synthesis` rename across the level_status enum (four verbatim occurrences in preconditions, AC-2, AC-5). Behaviour unchanged; rename follows the 3-of-3 UNANIMOUS_OWN_SYNTHESIS verdict on CON-SRC-0004. Amended on 2026-04-28 (Phase 5b follow-up 24 (a-lite) closure) to EXTEND the handoff preservation contract to include the per-constituent placeholder surface ``SourceMetadata.sub_work_inventory`` added by FU-24. Each ``SubWorkInventoryEntry`` carries its own ``(level, level_status, level_provenance)`` placeholder triple (defaults: ``(None, PENDING_SYNTHESIS, None)``); the handoff preservation contract extends pair-wise to each entry — the per-constituent IFF pair-consistency invariant (level non-null IFF level_status == "assigned" IFF level_provenance non-null) is enforced at the contract level via SubWorkInventoryEntry's model_validator. The constituent surface flows through the source→normalization handoff via the dispatcher's existing ``model_copy(deep=True)`` of ``bundle.source_metadata`` (engines/normalization/src/dispatcher.py:74) without requiring cross-engine widening (Codex CRIT-1 MOOT under this architectural choice). Constituent-level owner override at intake is OUT OF SCOPE for FU-24 — tracked as Phase 5b item 37.
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - The handoff payload always includes the level key.
  - The handoff payload always includes the level_status key with a non-null enum value.
  - A populated level value is passed through unchanged.
  - An unknown level is serialized as null rather than omitted, paired with a non-null level_status.
  - A level value populated via owner_level_override is passed through unchanged with the same string value received at intake, paired with level_status="assigned".
  - The level_status value is passed through unchanged — handoff packaging never rewrites, defaults, or reinterprets it.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with SourceMetadata.level="mutawassiṭ" and level_status="assigned" (populated via valid owner_level_override, the classical pedagogical CON-SRC-0011 WorkLevel value equivalent to intermediate); When source-to-normalization handoff packaging executes; Then The serialized payload contains level="mutawassiṭ" and level_status="assigned", both unchanged from the upstream emission. The level value serializes as the exact CON-SRC-0011 enum string — no coercion, no translation, no case folding..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/12_multi_muq/001.htm with SourceMetadata.level=null and level_status="pending_synthesis"; When source-to-normalization handoff packaging executes; Then The serialized payload contains the key level with value null AND the key level_status with value "pending_synthesis", both present and neither omitted..
  - AC-3 [deterministic] Given A source whose SourceMetadata.level was populated via owner_level_override="muntahī" at intake (validated against CON-SRC-0011 WorkLevel whitelist per REQ-SRC-0047 AC-1 — the classical pedagogical WorkLevel value for the terminal / curriculum-completing student, the enum position that the earlier English placeholder "advanced" mapped to), with level_status="assigned"; When source-to-normalization handoff packaging executes; Then The serialized payload contains level="muntahī" with the override value unchanged and level_status="assigned" unchanged..
  - AC-4 [deterministic] Given A source with genre="mushaf" (non-applicable per INV-SRC-0012), SourceMetadata.level=null, level_status="non_applicable_reference"; When source-to-normalization handoff packaging executes; Then The serialized payload contains level=null and level_status="non_applicable_reference"..
  - AC-5 [deterministic] Given A handoff packaging path that would have emitted level="mubtadiʾ" (a valid CON-SRC-0011 WorkLevel string — the classical pedagogical label for pre-malakah beginner) with level_status="pending_synthesis" — a cross-field invariant violation per CON-SRC-0004 because a populated level requires level_status="assigned"; When handoff packaging executes; Then Packaging is rejected with SRC-E-LEVEL-STATUS-INVARIANT-VIOLATION and no partial bundle is emitted. The error surfaces the cross- field rule (populated level requires assigned status), not a validation error on the WorkLevel string itself — the level value is a valid CON-SRC-0011 enum member..

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

### REQ-SRC-0023 — PDF text-layer evidence is diagnostic only
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md, .claude/skills/arabic-text/SKILL.md, and owner cross-validation on 2026-04-14 that normalization owns PDF-to-text conversion
- Trigger: The source engine records sampled direct-extraction evidence from a PDF for text-layer classification.
- Postconditions:
  - intake_dossier.pdf_text_evidence preserves the literal extracted string and its physical page number.
  - No Unicode normalization in {NFC, NFD, NFKC, NFKD} is applied to sampled direct-extraction evidence.
  - Sampled direct-extraction evidence is diagnostic only and is never emitted as normalized handoff text by the source engine.
  - The presence of diacritics inside sampled direct-extraction evidence does not override intake_dossier.pdf_text_layer_status="corrupt" when the text-layer assessment rejects the text as unusable.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/waraqat_usul/waraqat.pdf; When sampled direct-extraction evidence is recorded; Then One preserved sampled string equals "منت الورقات إلماـ احلرمني أيب ادلعايل اجلويين" with its physical page number and intake_dossier.pdf_text_layer_status="corrupt"..
  - AC-2 [deterministic] Given A temporary PDF generated during the test run with one Arabic page containing the literal string "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ" as embedded text; When sampled direct-extraction evidence is recorded; Then One preserved sampled string equals "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", intake_dossier.pdf_text_layer_status="clean", and the handoff contains no normalized_text field..

### REQ-SRC-0024 — PDF page-geometry hints for normalization
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md and revised on 2026-04-14 after confirming that source-engine PDF handling must stay metadata-first and normalization-owned for text extraction
- Trigger: A PDF source is being processed.
- Postconditions:
  - intake_dossier.page_layout_hint is set to single_column, dual_column, marginal_notes, or mixed when the intake-time geometry is sufficient.
  - layout_analysis.main_text_stream_hint and layout_analysis.marginal_text_stream_hint are identified separately when intake_dossier.page_layout_hint=marginal_notes.
  - layout_analysis.reading_order_hint is set to rtl_columns when intake_dossier.page_layout_hint=dual_column.
  - intake_dossier.page_layout_hint remains optional and non-authoritative until normalization confirms page layout on extracted text.
- Acceptance criteria:
  - AC-1 [deterministic] Given A PDF page with visible حاشية blocks in the outer margin alongside the main sharh text; When layout detection runs; Then intake_dossier.page_layout_hint="marginal_notes"..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When layout detection runs; Then intake_dossier.page_layout_hint="single_column"..

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

### REQ-SRC-0047 — Owner override pathway for level at intake
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-4. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) error severity downgraded fatal → blocking per reviewer finding that an invalid override should reject the override but not terminate intake (intake proceeds with level=null, level_status=pending_synthesis); (b) three distinct error conditions now distinguish absent vs empty vs invalid override values (previously conflated); (c) audit-trail entry structure enriched to include the raw override token, the validation verdict, and the enum-value whitelist that was applied; (d) integrates with the CON-SRC-0004 middle-path level_status field. Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) after the 3-cycle pre-commit dispatch (A/B/C/D → E → E-prime; 2-run Gemini CLI unanimous findings + Codex CLI per cycle): the non-applicable rejection path now cites the INV-SRC-0012 3-axis gate. Axis 1 lists the six-value genre set {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah}; Axis 2 fires on composite_work_type == "majmu" (REQ-SRC-0038); Axis 3 is deferred to Phase 5b item 23. See follow-ups 21-26. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the synchronized `pending_taxonomy` → `pending_synthesis` rename across six verbatim occurrences (rationale, postcondition, AC-2, AC-4, AC-5, behavior.preconditions). The rename follows the 3-of-3 UNANIMOUS_OWN_SYNTHESIS verdict (Codex CLI gpt-5.4 architectural-fit + Gemini CLI 2-run gemini-3.1-pro-preview + gemini-2.5-pro classical-scholarly) on CON-SRC-0004 enum. Error codes, severity, behaviour, and acceptance criteria shape unchanged. Amended on 2026-04-23 (Phase 5b item 10) to add the ADV-012 stickiness postcondition and AC-6. ADV-012's proposed_fix had two halves: (1) add mandatory level_provenance enum — LANDED in Phase 5b item 1 (commit `62647cb2b`) via the LevelProvenance enum and the SourceMetadata.enforce_level_invariants Pydantic model_validator; (2) add stickiness postcondition to REQ-SRC-0047 — LANDED here as a cross-engine contract declaration: owner override produces level_provenance="owner_override", and any downstream actor with level-writing authority (synthesis per DEC-SRC-0003 synthesis-owns-level) MUST honor this provenance signal as the "do not silently overwrite" beacon. Silent overwrite of an owner-asserted level is a T-2 knowledge- integrity corruption vector — the owner's direct library assertion would be contradicted without audit, producing a level value that appears content-derived while it actually overrides an owner assertion, or vice versa. See Adversary ADV-012 verbatim at `.kr/runtime/adversary_phase5a_20260417 .md`:296-307. Closure-wave amendment 2026-04-23 (Codex CAF-4 HIGH): narrowed the stickiness postcondition and AC-6 scope to match what `enforce_level_invariants` in contracts.py actually blocks — PAIR-CLEARING attacks (level-alone-null or provenance-alone-null), NOT value-swap attacks where both fields stay non-null. An earlier draft overstated the guarantee by claiming the IFF invariant blocks value-swap (e.g. mubtadiʾ→muntahī with provenance untouched); it does not, because (muntahī, OWNER_OVERRIDE) is a structurally valid pair under pair-consistency rules. Value-swap protection is a cross-engine contract: the synthesis engine per DEC-SRC-0003 synthesis-owns-level is required to refuse silent overwrite on records with level_provenance= OWNER_OVERRIDE, producing a structured disagreement entry instead. Source engine's contribution is the IFF invariant at the data-model layer plus byte-exact provenance preservation through REQ-SRC-0007 handoff — the signal the synthesis engine consumes. Reviewer output at `.kr/runtime/closure_wave_codex_cli_20260423.md`. Amended on 2026-04-28 (Phase 5b follow-up 37 closure) to WIDEN the owner-override entrance from per-source ``owner_level_override`` (a single ``Optional[WorkLevel]``) to ALSO accept per-constituent keying via ``MetadataDeliberationInput.owner_constituent_level_overrides: dict[int, WorkLevel]`` for *majmūʿ* sources whose constituents span the pedagogical spectrum (e.g. *Majmūʿ Fatāwā Ibn Taymiyyah* binding *al-ʿUbūdiyyah* mubtadiʾ-accessible with *Maʿārij al-Wuṣūl* muntahī). 4-of-4 cross-provider scholarly+structural convergence at HIGH confidence: Codex CLI structural (a-lite) ISOMORPHIC + Gemini Run A scholarly (a+b) HIGH + Gemini Run B scholarly INDEPENDENT (a+b) HIGH + arabic-reviewer Anthropic Agent (a+b) HIGH with NOVEL classical anchor al-Suyūṭī *Tadrīb al-Rāwī* Muqaddimah on *iʿtibār* discipline (genuinely independent — not in either Gemini's verdict or the sealed prior-evaluator block). Classical justification (al-Zarnūjī *Taʿlīm al-Mutaʿallim* Ch. IV pp. 58-66): *tawaqquf* is applied per-text, so an owner-override system that only accepts container-level overrides cannot express "I have read *al-ʿUbūdiyyah* (accessible) but *Maʿārij al-Wuṣūl* (advanced) is beyond me, both being in *Majmūʿ Fatāwā Ibn Taymiyyah*". Per-constituent overrides at intake are ALWAYS QUEUED (deferred to synthesis) because constituent-level genre is not classified at the source-engine intake stage; synthesis acquires constituent metadata later and applies/rejects via the standard INV-SRC-0012 3-axis gate per DEC-SRC-0003. Source engine NEVER WRITES per-constituent level (DEC-SRC-0003 — synthesis owns level writes); the entrance only RECORDS the per-constituent intent and PROPAGATES the queued record forward via ``MetadataDeliberationResult.pending_constituent_level_overrides: list[PendingLevelOverride]``. Two new structural CRITICAL findings from arabic-reviewer closed in this widening: CRIT-AR-1 (PendingLevelOverride was per-source-keyed; now carries optional ``constituent_idx: Optional[int] = Field(default=None, ge=0)``); CRIT-AR-2 (GenreDisputePosition lacked constituent identifier; now carries optional ``constituent_idx`` for per-constituent dispute snapshots in PendingLevelOverride.dispute_snapshot). Methodology gap disclosure: the arabic-reviewer wrapper at ``.kr/runtime/_followup_37_arabic_reviewer_wrapper_optimized.md`` contained the sealed prior-evaluator block in-file, so file-read sequence independence is technically compromised; analytical independence is supported by the novel al-Suyūṭī anchor + novel structural findings + novel framing ("rasm al-wirāqah vs pedagogical fact"). New error code SRC-E-LEVEL-OVERRIDE-CONSTITUENT-INVALID added at contracts.py for intake-boundary rejection of per-constituent keying on non-composite sources or out-of-range ``constituent_idx``. New AC-7 added below. Open follow-ups remaining after FU-37 closure: 18, 27, 28, 36.
- Trigger: The owner supplies an optional level override on a RawUploadRecord or equivalent intake surface when admitting a new source.
- Postconditions:
  - When owner_level_override is absent (the field is not present on the intake payload), SourceMetadata.level remains null and level_status is set per standard source-engine rules — pending_synthesis when no INV-SRC-0012 non-applicability axis fires, non_applicable_reference when at least one axis fires (Axis 1 genre ∈ {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah} OR Axis 2 composite_work_type == "majmu").
  - When owner_level_override is present AND the value passes the CON-SRC-0011 enum whitelist AND NO INV-SRC-0012 non-applicability axis fires (Axis 1 genre not in the six-value set AND Axis 2 composite_work_type != "majmu"), SourceMetadata.level is populated with the exact enum value and level_status is set to "assigned".
  - An audit-trail entry is written with provenance="owner_override", the raw override token received at intake, the validation verdict (accepted | rejected_invalid | rejected_nonapplicable | rejected_empty), the CON-SRC-0011 whitelist that was applied (enumerated snapshot), and an ISO 8601 timestamp of when the override was evaluated.
  - The override value, when accepted, survives through source admission and normalization handoff packaging unchanged (per REQ-SRC-0007 AC-3).
  - The (SourceMetadata.level, SourceMetadata.level_provenance) pair produced by an accepted owner override is ADV-012-STICKY. At the data-model level, contracts.py SourceMetadata.enforce_level_invariants (a Pydantic model_validator running under validate_assignment=True) enforces the IFF-style pair-consistency invariant — level non-null ↔ level_provenance non-null — so any single-field reassignment that BREAKS the pair (clearing level alone, clearing level_provenance alone) trips a ValidationError. The invariant does NOT block value-swap mutations where both elements stay non-null (e.g. replacing level=mutawassiṭ with level=muntahī while provenance remains OWNER_OVERRIDE) — that scenario satisfies the IFF pair-consistency rule at the Pydantic layer, so value-swap protection is not a single-engine invariant. The Codex closure-wave finding (CAF-4, 2026-04-23) surfaced this correctly: an earlier draft of this postcondition claimed the invariant blocked value-swap, which overstated what the code enforces. The accurate statement is that the invariant is a pair-clearing defense only; value-swap is governed by the cross-engine contract below. At the cross-engine contract level, any downstream actor with level-writing authority (the synthesis engine per DEC-SRC-0003 synthesis-owns-level) MUST inspect level_provenance on the received SourceMetadata record and, if level_provenance equals "owner_override", MUST NOT replace the level value without producing a structured level-override-disagreement entry — a non-silent escalation path whose specific shape is defined in the owning-engine spec. Silent overwriting of an owner-asserted level is a T-2 knowledge-integrity corruption vector — the owner's direct library assertion ("I, the student, declare this text mutawassiṭ") would be contradicted by a downstream content-derived classification without audit, producing a level value that masquerades as an owner assertion when it has been silently replaced (if provenance is left at "owner_override"), or as content-derived when it reflects the owner's override (if provenance is reassigned). The source engine's handoff packaging preserves the (level, level_provenance) pair byte-exactly through REQ-SRC-0007 AC-3, surfacing the provenance signal intact to every downstream consumer.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm (genre="matn" or "sharh") submitted with owner_level_override="mutawassiṭ"; When intake analysis processes the raw upload; Then SourceMetadata.level="mutawassiṭ", SourceMetadata.level_status= "assigned", an audit-trail entry is recorded with provenance="owner_override", raw_token="mutawassiṭ", verdict="accepted", whitelist_applied=["mubtadiʾ", "mutawassiṭ", "muntahī"], and a non-null ISO 8601 timestamp, and the override survives normalization handoff unchanged..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm submitted with owner_level_override="expert" (not a CON-SRC-0011 WorkLevel enum value); When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-INVALID, SourceMetadata.level remains null, SourceMetadata.level_status= "pending_synthesis", intake_analysis continues, and an audit-trail entry records raw_token="expert" and verdict="rejected_invalid"..
  - AC-3 [deterministic] Given A source with SourceMetadata.genre="mushaf" submitted with owner_level_override="mubtadiʾ"; When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE, SourceMetadata.level remains null, SourceMetadata.level_status= "non_applicable_reference", intake_analysis continues, and an audit-trail entry records verdict="rejected_nonapplicable"..
  - AC-4 [deterministic] Given A source submitted with owner_level_override="" (empty string) or owner_level_override="   " (whitespace only); When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-EMPTY, SourceMetadata.level remains null, SourceMetadata.level_status= "pending_synthesis" (or "non_applicable_reference" per genre), and an audit-trail entry records verdict="rejected_empty"..
  - AC-5 [deterministic] Given A source submitted with no owner_level_override field present at all on the intake payload; When intake analysis processes the raw upload; Then No audit-trail entry is written for override evaluation, SourceMetadata.level remains null, SourceMetadata.level_status is set per standard source-engine rules (pending_synthesis for leveled genres, non_applicable_reference for non-applicable genres), and intake_analysis completes without error..
  - AC-6 [deterministic] Given A SourceMetadata record produced by an accepted owner override through the REQ-SRC-0047 AC-1 happy path — (level="mutawassiṭ", level_provenance="owner_override", level_status="assigned"); When a subsequent actor attempts either of the two PAIR-CLEARING attack paths that the IFF invariant catches — (a) clearing SourceMetadata.level to null while leaving level_provenance set, or (b) clearing SourceMetadata.level_provenance to null while leaving level set. Pair-clearing breaks the level↔provenance IFF invariant, so the validator rejects. (Value-swap attacks that keep both fields non-null — e.g. level=mutawassiṭ→muntahī while provenance stays OWNER_OVERRIDE — are NOT caught by this validator because they preserve pair consistency; those are governed by the cross-engine contract in behavior.postconditions and are the synthesis engine's responsibility to refuse silently per DEC-SRC-0003 synthesis-owns-level authority. The Codex closure-wave finding CAF-4 surfaced this scope distinction — AC-6 now faithfully describes what enforce_level_invariants blocks, not what the cross-engine contract separately prescribes.); Then Layered defense in contracts.py SourceMetadata.enforce_level_invariants (Pydantic model_validator under validate_assignment=True) raises a ValidationError at the single-field assignment attempt. For attack path (a), CON-SRC-0004 invariant 1 (level_status=assigned IFF level non-null) fires first because it is ordered before the ADV-012 stickiness branch in the validator; ADV-012 stickiness is the backstop if the caller also mutates level_status. For attack path (b), CON-SRC-0004 invariants 1 and 2 both pass (level non-null + status=assigned is consistent), so ADV-012 stickiness is the sole defender. The test asserts that EITHER invariant citation is acceptable, because the outcome (single-field clear rejected, record unmutated) is identical under either layer. At the cross-engine contract level, the level_provenance="owner_override" field remains a readable signal to downstream engines that any paired reassignment of the pair (the structurally-valid mutation path which the IFF invariants cannot catch) requires a structured level-override-disagreement entry rather than a silent rewrite. The test also observes that the (level, level_provenance) pair is preserved byte-exactly through the REQ-SRC-0007 handoff JSON surface so downstream engines receive the provenance signal intact..
  - AC-7 [deterministic] Given A composite *majmūʿ* source (composite_work_type == "majmu") with ``IntakeDossier.sub_work_inventory`` of length N detected at intake (e.g. مجموع رسائل ابن رجب with N constituent rasāʾil) submitted with per-constituent owner overrides via ``MetadataDeliberationInput.owner_constituent_level_overrides == {0: WorkLevel.MUBTADI, 2: WorkLevel.MUNTAHI}`` (the owner asserts constituent idx 0 is mubtadiʾ and constituent idx 2 is muntahī; constituent idx 1 receives no override). Per Phase 5b follow-up 37 closure 2026-04-28, the owner-override entrance is widened to per- constituent keying for majmūʿ sources whose constituents span the pedagogical spectrum. Per-constituent overrides at intake are ALWAYS QUEUED (deferred to synthesis) because constituent-level genre is not classified at the source-engine stage; source engine NEVER writes per-constituent level (DEC-SRC-0003). The orchestrator helper ``_queue_constituent_overrides`` validates that ``constituent_idx`` is non-negative and in range of ``sub_work_inventory``, and that the source is composite_work_type == "majmu" (per-constituent keying on non-composite sources raises SRC-E-LEVEL-OVERRIDE-CONSTITUENT-INVALID).; When metadata deliberation processes the composite source; Then ``MetadataDeliberationResult.pending_constituent_level_overrides`` contains exactly 2 PendingLevelOverride records, sorted by ``constituent_idx`` ascending: idx=0 with validated_value=MUBTADI, state=QUEUED, raw_token="mubtadiʾ"; idx=2 with validated_value= MUNTAHI, state=QUEUED, raw_token="muntahī". Container-level SourceMetadata.level remains null and SourceMetadata.level_status == "non_applicable_reference" (Axis 2 fires unchanged on the container — per-constituent intent does NOT override container non-applicability). Each queued record carries genre_resolution_state_at_queueing=UNRESOLVED because constituent genre is unknown at intake; synthesis acquires constituent metadata later and applies/rejects per the standard INV-SRC-0012 3-axis gate via ``resolve_pending_level_override``..

### REQ-SRC-0048 — Deferred validation surface for owner_level_override
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: medium
- Confidence: medium
- Source: Initial formulation on 2026-04-23 (Phase 5b item 6), closing the adversary finding ADV-005 from the Phase 5a 4-of-4 reviewer wave which flagged that the deferred-validation surface was cited in prior atoms but did not actually exist. The host spec (source engine, not synthesis or a cross-engine contract) is determined by the `REQ-SRC-*` atom-naming convention and by the item 7 3-of-3 UNANIMOUS_OWN_SYNTHESIS dispatch (Codex CLI + Gemini CLI 2-run) `req_src_0048_scope_guidance` outputs: Gemini Run A argued source-engine spec because "the source engine receives owner_level_override at intake (REQ-SRC-0047) and asserts level_status provenance at admission (CON-SRC-0004), so it logically owns the queueing and validation state of that override"; Codex argued cross-engine contract; Gemini Run B argued synthesis spec. Source-engine spec wins on naming- convention precedence and on the source-engine-owns-intake single-writer principle. Content derives from the item 7 dispatch scope guidance rather than a separate atom-design dispatch; future Phase 5b follow-up may harden with a focused 3-evaluator pre-commit review if the atom surface expands beyond the initial intake-stage-only scope. Reviewer outputs informing scope: .kr/runtime/structural_audit_codex_cli_item7_retry_20260423.md lines 126-127, .kr/runtime/domain_validation_gemini_cli_item7_run_A_20260423.md lines 24-25, .kr/runtime/domain_validation_gemini_cli_item7_run_B_20260423.md lines 143-144. Amended on 2026-04-28 (Phase 5b follow-up 37 closure) to WIDEN the queue keyspace from ``source_id`` alone to the composite ``(source_id, constituent_idx)`` tuple via the new optional ``PendingLevelOverride.constituent_idx: Optional[int] = Field(default=None, ge=0)`` field. ``constituent_idx == None`` preserves source-level (container) override semantics for backward compatibility and for non-composite sources; an integer keys the override against ``SourceMetadata.sub_work_inventory[constituent_idx]`` for *majmūʿ* sources. Per-constituent overrides accepted at intake via REQ-SRC-0047 AC-7 (FU-37 entrance widening) are persisted as zero-or-more queued records on the new ``MetadataDeliberationResult.pending_constituent_level_overrides: list[PendingLevelOverride]`` field — distinct from the singular ``pending_level_override`` (per-source) so container-level and per-constituent overrides never conflate during synthesis-engine consumption. Per the 4-of-4 cross-provider scholarly+structural convergence on (a+b) HIGH (Codex CLI structural + Gemini Run A/B scholarly + arabic-reviewer Anthropic Agent), per-constituent overrides at intake are ALWAYS QUEUED (deferred to synthesis) because constituent-level genre is unknown at the source-engine stage; synthesis acquires constituent metadata later and applies/rejects per the standard INV-SRC-0012 3-axis gate via ``resolve_pending_level_override``. Source engine NEVER WRITES per-constituent level (DEC-SRC-0003). The arabic-reviewer Agent (this closure) surfaced the structural CRITICAL gap CRIT-AR-1 — PendingLevelOverride was per-source-keyed and could not persist per-constituent intent without ambiguity. New AC-7 below covers the per-constituent queue persistence path.
- Trigger: An owner_level_override is accepted at intake per REQ-SRC-0047 AC-1 (value is a valid CON-SRC-0011 WorkLevel enum member) but the source's genre is not yet resolved — either because metadata deliberation has not completed, or because agents returned genre_dispute without consensus.
- Postconditions:
  - The override is queued in an intake-stage pending-override record keyed by source_id, carrying raw_token, CON-SRC-0011-validated value, an ISO 8601 queued_at timestamp, and the genre-resolution state observed at queueing.
  - Interim SourceMetadata emits level=null and level_status="pending_synthesis" (the level is not populated from the queued override until axis validation resolves).
  - When metadata deliberation subsequently resolves genre to a single classification AND no INV-SRC-0012 non-applicability axis fires (Axis 1 genre ∉ {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah} AND Axis 2 composite_work_type != "majmu"), the queued override is applied as if it had been validated at intake per REQ-SRC-0047 AC-1, SourceMetadata.level is populated with the override value, and SourceMetadata.level_status is updated to "assigned".
  - When metadata deliberation resolves genre to a value where at least one INV-SRC-0012 axis fires, the queued override is rejected via the REQ-SRC-0047 AC-3 path (SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE), SourceMetadata.level remains null, and SourceMetadata.level_status is set to "non_applicable_reference".
  - When metadata deliberation resolves with genre_dispute (agents disagree and consensus-pattern does not yield a single classification per D-041), the queued override remains queued, SourceMetadata.level_status stays "pending_synthesis", and an audit-trail entry records the dispute with each agent's proposed genre and confidence. Synthesis engine consumes the queued override and the dispute record during its authoritative level determination pass.
  - An audit-trail entry is written at every state transition (queued, applied, rejected_nonapplicable, deferred_to_synthesis_on_dispute) with provenance="owner_override_deferred", the source_id, the genre-resolution state, and the ISO 8601 timestamp.
- Acceptance criteria:
  - AC-1 [integration] Given A source submitted with owner_level_override="mutawassiṭ" (a valid CON-SRC-0011 value) where metadata deliberation has not yet emitted a genre classification at the moment of intake.; When intake_analysis processes the raw upload; Then The override is queued with provenance="owner_override_deferred", the interim SourceMetadata emits level=null and level_status="pending_synthesis", an audit-trail entry records the queuing event, and intake_analysis completes without blocking on genre resolution..
  - AC-2 [integration] Given A source whose owner_level_override was queued per AC-1, when metadata deliberation subsequently resolves genre="sharh" (a leveled genre NOT in the Axis 1 non-applicable set) and composite_work_type=null (Axis 2 does not fire).; When genre resolution is received by the intake-stage override-queue handler; Then The queued override is applied, SourceMetadata.level is updated to "mutawassiṭ", SourceMetadata.level_status is updated to "assigned", and an audit-trail entry records the applied-on- resolution event with both the queued_at and resolved_at timestamps..
  - AC-3 [integration] Given A source whose owner_level_override was queued per AC-1, when metadata deliberation subsequently resolves genre="mushaf" (a genre in the Axis 1 non-applicable set).; When genre resolution is received by the intake-stage override-queue handler; Then The queued override is rejected with SRC-E-LEVEL-OVERRIDE- NONAPPLICABLE per REQ-SRC-0047 AC-3 path, SourceMetadata.level remains null, SourceMetadata.level_status is updated to "non_applicable_reference" with Axis 1 cited, and an audit-trail entry records the rejected-on-resolution event..
  - AC-4 [integration] Given A source whose owner_level_override was queued per AC-1, when metadata deliberation resolves with genre_dispute — two agents propose "risalah" (leveled) and a third proposes "mushaf" (non-applicable) with no consensus reached per D-041.; When genre resolution is received by the intake-stage override-queue handler; Then The queued override remains queued (not applied, not rejected), SourceMetadata.level_status stays "pending_synthesis", the audit-trail entry captures the genre_dispute with per-agent proposed-genre and confidence, and the handoff payload to normalization carries the queued-override record so the synthesis engine can consume it during authoritative level determination..
  - AC-5 [integration] Given A source submitted with owner_level_override="mubtadiʾ" where metadata deliberation has ALREADY completed (genre="sharh", composite_work_type=null) at the moment of intake — the standard REQ-SRC-0047 path, not a deferred-validation case.; When intake_analysis processes the raw upload; Then The override flows through the REQ-SRC-0047 synchronous validation path and the REQ-SRC-0048 deferred-queue surface is bypassed — no pending-override record is created, no "pending_synthesis" transition is emitted for this source, and SourceMetadata emits level="mubtadiʾ" with level_status="assigned" directly..
  - AC-6 [deterministic] Given A source whose owner_level_override was queued per AC-1, where the intake-stage override-staleness window (48 hours default) has elapsed before genre resolution is received.; When genre resolution finally arrives after the staleness window; Then The override is still applied/rejected per the resolved genre following the standard AC-2/AC-3 paths, but SRC-W-OVERRIDE- QUEUE-STALE is emitted as a warning and the audit-trail entry marks the override as applied-after-stale-window..
  - AC-7 [integration] Given A composite *majmūʿ* source (composite_work_type == "majmu") with ``IntakeDossier.sub_work_inventory`` of length N submitted with per-constituent owner overrides via ``MetadataDeliberationInput.owner_constituent_level_overrides == {0: WorkLevel.MUBTADI, 2: WorkLevel.MUNTAHI}``. Per Phase 5b follow-up 37 closure 2026-04-28, the queue keyspace widens from ``source_id`` alone to the composite ``(source_id, constituent_idx)`` tuple via the new optional ``PendingLevelOverride.constituent_idx: Optional[int] = Field(default=None, ge=0)`` field.; When metadata deliberation processes the composite source; Then ``MetadataDeliberationResult.pending_constituent_level_overrides`` contains exactly 2 PendingLevelOverride records — one per non-empty key in the entrance dict — sorted ascending by ``constituent_idx``. Each record carries ``state=QUEUED``, ``genre_resolution_state_at_queueing=UNRESOLVED`` (constituent genre unknown at intake), and ``constituent_idx`` matching the entrance key (0 and 2 respectively). The singular per-source ``MetadataDeliberationResult.pending_level_override`` is None (no source-level override was supplied). Container-level SourceMetadata.level remains null and SourceMetadata.level_status == "non_applicable_reference" (Axis 2 fires unchanged on the container). The first audit-trail entry on each queued record records the QUEUED transition with provenance= "owner_override_deferred", matching the per-source AC-1 audit contract. arabic-reviewer Agent CRIT-AR-1 (PendingLevelOverride keyspace expansion) is closed by this AC..

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
