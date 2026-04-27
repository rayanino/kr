# Source Spec Atoms by Topic: metadata

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0002 | constraint | Hadith literature dominates source-engine benchmark quality | confirmed | high |
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

### CON-SRC-0002 — Hadith literature dominates source-engine benchmark quality
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012; amended per contract-architect-review.yaml
- Rule: At least 40 percent of source-engine benchmark fixtures must be hadith literature or hadith-adjacent works.

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
- Decision rationale: Reversible, non-destructive, D-023-compatible, and safe under the empty-library state. The migration logic is concrete and testable: (i) missing level_status + level null + genre not in NON_APPLICABLE_GENRE_VALUES + composite_work_type != "majmu" ⇒ default level_status=pending_synthesis; (ii) missing level_status + level null + genre in NON_APPLICABLE_GENRE_VALUES (Axis 1) OR composite_work_type=="majmu" (Axis 2) ⇒ default level_status=non_applicable_reference; (iii) missing level_status + level non-null ⇒ ambiguous, raise SRC-E-LEGACY-RECORD-AMBIGUOUS-STATUS and route to human_gate (cannot safely default between assigned and non_applicable_reference without rerunning deliberation); (iv) missing level_provenance + level null ⇒ default level_provenance=null (IFF-consistent with ADV-012 stickiness); (v) missing level_provenance + level non-null ⇒ ambiguous, raise SRC-E-LEGACY-RECORD-AMBIGUOUS-PROVENANCE and route to human_gate (cannot distinguish owner_override from synthesis_engine without additional evidence — OPT-A's rejection-ground 2 at the record level). (vi) missing composite_work_type ⇒ default to None (the field was not present pre-Phase-5a; Axis 2 of INV-SRC-0012 cannot fire for a legacy record lacking the field, so default None is safe and preserves the 3-axis gate invariants). Every migration decision is audited; nothing is silently corrected. Aligns with Critical Rule 4 (errors fail loudly) because ambiguous cases become blocking load-boundary errors rather than silent defaults. Aligns with D-023 (persisted records unchanged) and with INV-SRC-0011 (source engine never infers level from shallow signals — the migration layer defaults level_status from level and genre, which are already-present fields, not inferred content). Closure-wave 2026-04-23 localization constraints (Run A DVF-3, Run B DVF-2, 2-of-2 Gemini convergent on DIM3/DIM6): (vii) Arabic localization of "provenance" in error surfaces MUST use maṣdar al-taqyīm (مصدر التقييم) — the metadata-origin sense — and MUST NOT use sanad (سند), bayyina (بينة), or shahāda (شهادة), which carry hadith-science and uṣūl al-fiqh evidentiary semantics whose conflation with pipeline-provenance is a T-2 corruption vector (cf. al-Khaṭīb al-Baghdādī al-Kifāyah fī ʿIlm al- Riwāyah on transmission-term precision). (viii) the human_gate routing for SRC-E-LEGACY-RECORD-AMBIGUOUS-STATUS and SRC-E-LEGACY-RECORD-AMBIGUOUS-PROVENANCE MUST NOT expose technical enum values or architecture strings (e.g. the literal strings "owner_override" or "synthesis_engine") to the non- technical owner. The owner-facing prompt MUST be framed as a plain-language pedagogical question about the book itself — a canonical example prompt: "هل سبق أن حدّدتَ درجةَ هذا الكتاب بنفسك؟ (Did you previously assign this book's reading level yourself, or was it categorized automatically?)" — referencing the book title in context. The owner knows his own learning history with the text (he placed it, or did not); he does not know the provenance enum universe. Implementation of the human_gate surface is scheduled under follow-up item 30.

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
- Source: Initial formulation on 2026-04-16 from dr-reports/dr-chatgpt-level-detection-20260416.yaml (SEC-2). Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-1 through AC-4 in the CON-SRC-0011 classical WorkLevel vocabulary (mubtadiʾ, muntahī, mutawassiṭ, muntahī respectively). Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) to introduce the 3-axis non-applicability gate after a 3-cycle pre-commit dispatch with 3 evaluators per cycle (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through /prompt-architect): the prior A/B/C/D cycle blocked unanimously on classical-taxonomy category errors (majmu is a structural composite not a fann; biographical_dictionary is an English alias for tarajim / parent of Genre.TABAQAT; rijal_dictionary is a nawʿ of tabaqat/tarikh/hadith); the Option E cycle blocked unanimously on DIM4 archival-genre regression (the reduced 2-value {mushaf, hadith_collection} set left existing archival Genres MASHYAKHAH / THABAT / BARNAMAJ silently level-applicable); the Option E-prime cycle returned unanimous AMEND_REQUIRED adding FAHRASAH as convergent scholarly guidance (same archival-reference class as mashyakhah / thabat / barnamaj) with Codex PROCEED_WITH_AMENDMENTS confirming structural soundness of the 6-value expansion. Axis 1 now enumerates six Genre members; Axis 2 adds the composite_work_type == "majmu" signal from IntakeDossier (REQ-SRC-0038); Axis 3 was deferred to Phase 5b item 23 (HadithSubgenre ARBAIN pedagogical carve-out) and is activated below. Amended on 2026-04-26 (Phase 5b item 23) to ACTIVATE Axis 3 with the conservative single-value carve-back set LEVELED_HADITH_SUBGENRES = {arbain}, with Path A semantics (default None subgenre fires Axis 3 — transmission-by-default per the *iḥtiyāṭ* / *tawaqquf* principle, Ibn Ḥajar *Nuzhat al-Naẓar* Bāb al-Khabar al-Maqbūl, al-Suyūṭī *Tadrīb al-Rāwī* Nawʿ 23). 3-evaluator wave (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through /prompt-architect): 3-of-3 BLOCKED the original draft's plan to overload HadithSubgenre.ARBAIN as a generic pedagogical proxy for Bulūgh al-Marām and Riyāḍ al-Ṣāliḥīn (Codex CRITICAL DIM4 BLOCK + 2-of-2 Gemini CRITICAL DIM4 amend); 3-of-3 PROCEEDED on Path A default (al-Kattānī *al-Risālah al- Mustaṭrafah* p. 69-72 *Kutub al-Arbaʿīniyyāt* + iḥtiyāṭ); 2-of-2 Gemini AMEND on Arabic-anchor injection (كُتُب الرِّوَايَة into rejection error strings); Codex AMEND on queue-path regression tests + named-test strengthening (Axis 3 substring + hadith_subgenre pin). The Geminis' constructive proposal to introduce HadithSubgenre.AHKAM and MUKHTARAT enum values for famous pedagogical anthologies (Bulūgh al-Marām → AHKAM; Riyāḍ al-Ṣāliḥīn → MUKHTARAT, per al-Kattānī *al-Risālah al-Mustaṭrafah* p. 41/44 *Kutub al-Aḥkām*) is deferred to NEW follow-up 34 — substantive contract-change scope beyond ARBAIN-only carve-back. New AC-5 (ARBAIN positive — al-Arbaʿīn al-Nawawī accepts owner override) and AC-6 (MUSNAD negative — Musnad Aḥmad rejects with explicit Axis 3 citation) added. The "مصنف" → MUSANNAF inference extension bundled (Codex CRITICAL DIM4 fix). See follow-up items 21 (FATAWA/MUJAM naming resolution), 22 (mawsūʿa/muʿjam/fihris non-applicable expansion), 24 (majmuʿ constituent-rasāʾil leveling architecture), and 34 (HadithSubgenre.AHKAM + MUKHTARAT enum addition for selected-hadith pedagogical anthologies). Amended on 2026-04-27 (Phase 5b follow-ups 25 + 26 paired closure) to EXTEND NON_APPLICABLE_GENRE_VALUES from six values to eight by adding ``mujam`` and ``tabaqat``, after a paired-PRELIMINARY- confirmation dispatch wave (Gemini CLI Run B scholarly + Codex CLI structural, both through /prompt-architect). Run B scholarly verdicts: FU-25 AMEND HIGH (Option A genre-level — disagreed with Run-A item4e's Option B sub-genre-only carve-out, on the basis that BOTH linguistic lexicons AND hadith muʿjam works share the same non-linear alphabetical-index reference architecture); FU-26 CONFIRM HIGH (Option α genre-level — full convergence with Run-A item4eprime). Run B governing principle (own-words): a genre belongs in NON_APPLICABLE_GENRE_VALUES when its organizing architecture operates as a static repository of attestation, indexing, or archival documentation rather than a graduated didactic curriculum. Codex CLI structural reasoning (executable Python probes of ``_infer_genre`` outputs, ripgrep across all source-engine tests and fixtures, direct read of GenreDisputePosition contract): zero existing test ripple (no fixtures or override tests assert Genre.MUJAM or Genre.TABAQAT behavior); double-classification of hadith-muʿjam and hadith-ṭabaqāt titles is real but harmless because Axis 1 fires before Axis 3 for non-hadith_collection genres in ``_non_applicability_axis``; **Option B/β subgenre-only carve-out is structurally inadequate on the dispute path** because GenreDisputePosition (contracts.py:770) carries only ``genre_candidate``, not a hadith-subgenre candidate, so the override-queue's unanimous-nonapplicable branch can only adjudicate via ``genre_candidate ∈ NON_APPLICABLE_GENRE_VALUES``. The genre- level fix (Option A + Option α) was therefore the only architecturally complete path. Classical anchors: al-Kattānī, *al-Risālah al-Mustaṭrafah*, "Kutub al-Maʿājim" section (~p. 110+ in Dār al-Bashāʾir ed.); al-Suyūṭī, *Tadrīb al-Rāwī*, Nawʿ 61 (*Maʿrifat al-Ṭabaqāt*); Ibn Khallikān, *Wafayāt al-Aʿyān*, author's introduction; Ibn al-Nadīm, *al-Fihrist*. New AC-7 (MUJAM positive — al-Muʿjam al-Kabīr li-l-Ṭabarānī rejects owner override on Genre.MUJAM Axis 1) and AC-8 (TABAQAT positive — al- Ṭabaqāt al-Kubrā li-Ibn Saʿd rejects owner override on Genre.TABAQAT Axis 1) added. Documented limitation: hadith-muʿjam and hadith-ṭabaqāt titles double-classify (Genre.MUJAM/TABAQAT + HadithSubgenre.MUJAM/TABAQAT_RIJAL fire simultaneously); under the Axis 1 firing on the genre, the redundant subgenre is harmless metadata. Documented latent gap: GenreDisputePosition carries no hadith-subgenre candidate; future need for subgenre-level dispute adjudication would require widening that contract — captured for potential future follow-up if/when the need surfaces. Open follow- ups remaining: 18, 21, 22, 24, 27, 28, 34.
- Rule: For works where the reading-level concept does not apply, the source engine MUST serialize SourceMetadata.level as null regardless of any owner override attempt. Non-applicability fires along three axes, any of which is sufficient: Axis 1 (fann-level) — the work's Genre is one of the six non-applicable members {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah}; Axis 2 (structural) — the work's composite_work_type == "majmu" (a structural composite whose container-level pedagogy does not apply even when the declared Genre is otherwise leveled); Axis 3 (hadith-subgenre) — when Axis 1 fires for Genre.HADITH_COLLECTION, attribution is refined by hadith_subgenre. Subgenres in the carve-back set LEVELED_HADITH_SUBGENRES (currently {arbain}) reverse the Axis 1 firing — the work is treated as a pedagogical 40-hadith collection (al-Arbaʿīn al-Nawawī of al-Nawawī d. 676 AH; al-Kattānī, al-Risālah al-Mustaṭrafah p. 69-72 Kutub al-Arbaʿīniyyāt) and the level applies. All other hadith subgenres — including null subgenre per Path A (transmission-by-default, iḥtiyāṭ / tawaqquf principle, Ibn Ḥajar Nuzhat al-Naẓar Bāb al-Khabar al-Maqbūl) — confirm Axis 1 firing under Axis 3 (the work is kutub al-riwāyah, transmission collection). Forcing a reading- level label onto an Axis-1 (post-carve-back), Axis-2, or Axis-3 firing work creates false scholarly authority because its organizing principle is transmission, archival reference, or structural compilation, not graduated pedagogical exposition.

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
- Source: Derived from OF-SRC-0007; moved to step 60 on 2026-04-14 because the rule governs handoff packaging rather than metadata deliberation itself. Amended on 2026-04-16 per dr-chatgpt-level-detection-20260416.yaml (SEC-5). Further amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) explicit precondition that owner_level_override passed the CON-SRC-0011 enum-value whitelist before reaching handoff packaging; (b) new level_status (CON-SRC-0004 middle-path) must serialize alongside level — preservation contract extends to both fields. Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-1 (intermediate → mutawassiṭ), AC-3 (advanced → muntahī), and AC-5 (beginner → mubtadiʾ) in the CON-SRC-0011 classical WorkLevel vocabulary. Behaviour, preconditions, postconditions, and error conditions unchanged; the Phase-5a reviewer wave identified the English placeholders as structurally untestable because REQ-SRC-0047 now rejects them at intake against the enum whitelist. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the synchronized `pending_taxonomy` → `pending_synthesis` rename across the level_status enum (four verbatim occurrences in preconditions, AC-2, AC-5). Behaviour unchanged; rename follows the 3-of-3 UNANIMOUS_OWN_SYNTHESIS verdict on CON-SRC-0004.
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

### REQ-SRC-0047 — Owner override pathway for level at intake
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-4. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) error severity downgraded fatal → blocking per reviewer finding that an invalid override should reject the override but not terminate intake (intake proceeds with level=null, level_status=pending_synthesis); (b) three distinct error conditions now distinguish absent vs empty vs invalid override values (previously conflated); (c) audit-trail entry structure enriched to include the raw override token, the validation verdict, and the enum-value whitelist that was applied; (d) integrates with the CON-SRC-0004 middle-path level_status field. Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) after the 3-cycle pre-commit dispatch (A/B/C/D → E → E-prime; 2-run Gemini CLI unanimous findings + Codex CLI per cycle): the non-applicable rejection path now cites the INV-SRC-0012 3-axis gate. Axis 1 lists the six-value genre set {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah}; Axis 2 fires on composite_work_type == "majmu" (REQ-SRC-0038); Axis 3 is deferred to Phase 5b item 23. See follow-ups 21-26. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the synchronized `pending_taxonomy` → `pending_synthesis` rename across six verbatim occurrences (rationale, postcondition, AC-2, AC-4, AC-5, behavior.preconditions). The rename follows the 3-of-3 UNANIMOUS_OWN_SYNTHESIS verdict (Codex CLI gpt-5.4 architectural-fit + Gemini CLI 2-run gemini-3.1-pro-preview + gemini-2.5-pro classical-scholarly) on CON-SRC-0004 enum. Error codes, severity, behaviour, and acceptance criteria shape unchanged. Amended on 2026-04-23 (Phase 5b item 10) to add the ADV-012 stickiness postcondition and AC-6. ADV-012's proposed_fix had two halves: (1) add mandatory level_provenance enum — LANDED in Phase 5b item 1 (commit `62647cb2b`) via the LevelProvenance enum and the SourceMetadata.enforce_level_invariants Pydantic model_validator; (2) add stickiness postcondition to REQ-SRC-0047 — LANDED here as a cross-engine contract declaration: owner override produces level_provenance="owner_override", and any downstream actor with level-writing authority (synthesis per DEC-SRC-0003 synthesis-owns-level) MUST honor this provenance signal as the "do not silently overwrite" beacon. Silent overwrite of an owner-asserted level is a T-2 knowledge- integrity corruption vector — the owner's direct library assertion would be contradicted without audit, producing a level value that appears content-derived while it actually overrides an owner assertion, or vice versa. See Adversary ADV-012 verbatim at `.kr/runtime/adversary_phase5a_20260417 .md`:296-307. Closure-wave amendment 2026-04-23 (Codex CAF-4 HIGH): narrowed the stickiness postcondition and AC-6 scope to match what `enforce_level_invariants` in contracts.py actually blocks — PAIR-CLEARING attacks (level-alone-null or provenance-alone-null), NOT value-swap attacks where both fields stay non-null. An earlier draft overstated the guarantee by claiming the IFF invariant blocks value-swap (e.g. mubtadiʾ→muntahī with provenance untouched); it does not, because (muntahī, OWNER_OVERRIDE) is a structurally valid pair under pair-consistency rules. Value-swap protection is a cross-engine contract: the synthesis engine per DEC-SRC-0003 synthesis-owns-level is required to refuse silent overwrite on records with level_provenance= OWNER_OVERRIDE, producing a structured disagreement entry instead. Source engine's contribution is the IFF invariant at the data-model layer plus byte-exact provenance preservation through REQ-SRC-0007 handoff — the signal the synthesis engine consumes. Reviewer output at `.kr/runtime/closure_wave_codex_cli_20260423.md`.
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

### REQ-SRC-0048 — Deferred validation surface for owner_level_override
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: medium
- Confidence: medium
- Source: Initial formulation on 2026-04-23 (Phase 5b item 6), closing the adversary finding ADV-005 from the Phase 5a 4-of-4 reviewer wave which flagged that the deferred-validation surface was cited in prior atoms but did not actually exist. The host spec (source engine, not synthesis or a cross-engine contract) is determined by the `REQ-SRC-*` atom-naming convention and by the item 7 3-of-3 UNANIMOUS_OWN_SYNTHESIS dispatch (Codex CLI + Gemini CLI 2-run) `req_src_0048_scope_guidance` outputs: Gemini Run A argued source-engine spec because "the source engine receives owner_level_override at intake (REQ-SRC-0047) and asserts level_status provenance at admission (CON-SRC-0004), so it logically owns the queueing and validation state of that override"; Codex argued cross-engine contract; Gemini Run B argued synthesis spec. Source-engine spec wins on naming- convention precedence and on the source-engine-owns-intake single-writer principle. Content derives from the item 7 dispatch scope guidance rather than a separate atom-design dispatch; future Phase 5b follow-up may harden with a focused 3-evaluator pre-commit review if the atom surface expands beyond the initial intake-stage-only scope. Reviewer outputs informing scope: .kr/runtime/structural_audit_codex_cli_item7_retry_20260423.md lines 126-127, .kr/runtime/domain_validation_gemini_cli_item7_run_A_20260423.md lines 24-25, .kr/runtime/domain_validation_gemini_cli_item7_run_B_20260423.md lines 143-144.
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
