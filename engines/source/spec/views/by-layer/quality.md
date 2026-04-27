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
| INV-SRC-0012 | invariant | Non-applicable works require level null | confirmed | high |

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
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-1. Hardened on 2026-04-17 by the 3-of-3 unanimous adjudication (Codex CLI architectural-fit, Gemini CLI runs 1 and 2 classical- defensibility at 6-0 branch win counts, Gemini DR T-2 threat model) that closed DEC-SRC-0003 on OPT-B. Acceptance criterion AC-4 (positive assertion that level_status is still populated when level is null) is added to complement the null-assertion clauses in AC-1 and AC-2. Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-3 in the CON-SRC-0011 classical WorkLevel vocabulary (mutawassiṭ), replacing the earlier English placeholder "intermediate" which would fail the enum whitelist at REQ-SRC-0047 intake validation. Rule statement and implication are unchanged; the amendment is confined to the acceptance criterion surface. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) after the 3-of-3 UNANIMOUS_OWN_ SYNTHESIS verdict (Codex CLI gpt-5.4 architectural-fit + Gemini CLI 2-run gemini-3.1-pro-preview + gemini-2.5-pro classical- scholarly) confirmed the rule.implication's existing naming of "the synthesis engine's ownership of level classification" as correct. The amendment is confined to AC-4's reference to the level_status enum value `pending_taxonomy`, renamed to `pending_synthesis` consistent with CON-SRC-0004's synchronized rename. Rule statement, rule.implication, and AC-1 through AC-3 are semantically unchanged.
- Rule: The source engine MUST NOT compute or infer the level field of SourceMetadata from title tokens, series cues, publisher metadata, or any shallow bibliographic signal. The level field remains null unless an explicit owner_level_override is provided at intake. This invariant does NOT restrict the `level_status` field (CON-SRC-0004), which is a processing-state enum — not a pedagogical-level inference — and whose emission is governed by CON-SRC-0004 alone.

### INV-SRC-0012 — Non-applicable works require level null
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-reports/dr-chatgpt-level-detection-20260416.yaml (SEC-2). Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-1 through AC-4 in the CON-SRC-0011 classical WorkLevel vocabulary (mubtadiʾ, muntahī, mutawassiṭ, muntahī respectively). Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) to introduce the 3-axis non-applicability gate after a 3-cycle pre-commit dispatch with 3 evaluators per cycle (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through /prompt-architect): the prior A/B/C/D cycle blocked unanimously on classical-taxonomy category errors (majmu is a structural composite not a fann; biographical_dictionary is an English alias for tarajim / parent of Genre.TABAQAT; rijal_dictionary is a nawʿ of tabaqat/tarikh/hadith); the Option E cycle blocked unanimously on DIM4 archival-genre regression (the reduced 2-value {mushaf, hadith_collection} set left existing archival Genres MASHYAKHAH / THABAT / BARNAMAJ silently level-applicable); the Option E-prime cycle returned unanimous AMEND_REQUIRED adding FAHRASAH as convergent scholarly guidance (same archival-reference class as mashyakhah / thabat / barnamaj) with Codex PROCEED_WITH_AMENDMENTS confirming structural soundness of the 6-value expansion. Axis 1 now enumerates six Genre members; Axis 2 adds the composite_work_type == "majmu" signal from IntakeDossier (REQ-SRC-0038); Axis 3 was deferred to Phase 5b item 23 (HadithSubgenre ARBAIN pedagogical carve-out) and is activated below. Amended on 2026-04-26 (Phase 5b item 23) to ACTIVATE Axis 3 with the conservative single-value carve-back set LEVELED_HADITH_SUBGENRES = {arbain}, with Path A semantics (default None subgenre fires Axis 3 — transmission-by-default per the *iḥtiyāṭ* / *tawaqquf* principle, Ibn Ḥajar *Nuzhat al-Naẓar* Bāb al-Khabar al-Maqbūl, al-Suyūṭī *Tadrīb al-Rāwī* Nawʿ 23). 3-evaluator wave (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all through /prompt-architect): 3-of-3 BLOCKED the original draft's plan to overload HadithSubgenre.ARBAIN as a generic pedagogical proxy for Bulūgh al-Marām and Riyāḍ al-Ṣāliḥīn (Codex CRITICAL DIM4 BLOCK + 2-of-2 Gemini CRITICAL DIM4 amend); 3-of-3 PROCEEDED on Path A default (al-Kattānī *al-Risālah al- Mustaṭrafah* p. 69-72 *Kutub al-Arbaʿīniyyāt* + iḥtiyāṭ); 2-of-2 Gemini AMEND on Arabic-anchor injection (كُتُب الرِّوَايَة into rejection error strings); Codex AMEND on queue-path regression tests + named-test strengthening (Axis 3 substring + hadith_subgenre pin). The Geminis' constructive proposal to introduce HadithSubgenre.AHKAM and MUKHTARAT enum values for famous pedagogical anthologies (Bulūgh al-Marām → AHKAM; Riyāḍ al-Ṣāliḥīn → MUKHTARAT, per al-Kattānī *al-Risālah al-Mustaṭrafah* p. 41/44 *Kutub al-Aḥkām*) is deferred to NEW follow-up 34 — substantive contract-change scope beyond ARBAIN-only carve-back. New AC-5 (ARBAIN positive — al-Arbaʿīn al-Nawawī accepts owner override) and AC-6 (MUSNAD negative — Musnad Aḥmad rejects with explicit Axis 3 citation) added. The "مصنف" → MUSANNAF inference extension bundled (Codex CRITICAL DIM4 fix). See follow-up items 21 (FATAWA/MUJAM naming resolution), 22 (mawsūʿa/muʿjam/fihris non-applicable expansion), 24 (majmuʿ constituent-rasāʾil leveling architecture), and 34 (HadithSubgenre.AHKAM + MUKHTARAT enum addition for selected-hadith pedagogical anthologies). Amended on 2026-04-27 (Phase 5b follow-ups 25 + 26 paired closure) to EXTEND NON_APPLICABLE_GENRE_VALUES from six values to eight by adding ``mujam`` and ``tabaqat``, after a paired-PRELIMINARY- confirmation dispatch wave (Gemini CLI Run B scholarly + Codex CLI structural, both through /prompt-architect). Run B scholarly verdicts: FU-25 AMEND HIGH (Option A genre-level — disagreed with Run-A item4e's Option B sub-genre-only carve-out, on the basis that BOTH linguistic lexicons AND hadith muʿjam works share the same non-linear alphabetical-index reference architecture); FU-26 CONFIRM HIGH (Option α genre-level — full convergence with Run-A item4eprime). Run B governing principle (own-words): a genre belongs in NON_APPLICABLE_GENRE_VALUES when its organizing architecture operates as a static repository of attestation, indexing, or archival documentation rather than a graduated didactic curriculum. Codex CLI structural reasoning (executable Python probes of ``_infer_genre`` outputs, ripgrep across all source-engine tests and fixtures, direct read of GenreDisputePosition contract): zero existing test ripple (no fixtures or override tests assert Genre.MUJAM or Genre.TABAQAT behavior); double-classification of hadith-muʿjam and hadith-ṭabaqāt titles is real but harmless because Axis 1 fires before Axis 3 for non-hadith_collection genres in ``_non_applicability_axis``; **Option B/β subgenre-only carve-out is structurally inadequate on the dispute path** because GenreDisputePosition (contracts.py:770) carries only ``genre_candidate``, not a hadith-subgenre candidate, so the override-queue's unanimous-nonapplicable branch can only adjudicate via ``genre_candidate ∈ NON_APPLICABLE_GENRE_VALUES``. The genre- level fix (Option A + Option α) was therefore the only architecturally complete path. Classical anchors: al-Kattānī, *al-Risālah al-Mustaṭrafah*, "Kutub al-Maʿājim" section (~p. 110+ in Dār al-Bashāʾir ed.); al-Suyūṭī, *Tadrīb al-Rāwī*, Nawʿ 61 (*Maʿrifat al-Ṭabaqāt*); Ibn Khallikān, *Wafayāt al-Aʿyān*, author's introduction; Ibn al-Nadīm, *al-Fihrist*. New AC-7 (MUJAM positive — al-Muʿjam al-Kabīr li-l-Ṭabarānī rejects owner override on Genre.MUJAM Axis 1) and AC-8 (TABAQAT positive — al- Ṭabaqāt al-Kubrā li-Ibn Saʿd rejects owner override on Genre.TABAQAT Axis 1) added. Documented limitation: hadith-muʿjam and hadith-ṭabaqāt titles double-classify (Genre.MUJAM/TABAQAT + HadithSubgenre.MUJAM/TABAQAT_RIJAL fire simultaneously); under the Axis 1 firing on the genre, the redundant subgenre is harmless metadata. Documented latent gap: GenreDisputePosition carries no hadith-subgenre candidate; future need for subgenre-level dispute adjudication would require widening that contract — captured for potential future follow-up if/when the need surfaces. Amended on 2026-04-27 (Phase 5b follow-up 22 closure) to EXTEND NON_APPLICABLE_GENRE_VALUES from eight values to nine by adding ``mawsuah``, after a focused single-evaluator dispatch wave (Gemini CLI Run-B-style scholarly with anti-priming protocol — Step-1 first- principles commitment locked before Step-2 confrontation with prior runs — through /prompt-architect). 2-of-2 cross-time independent Gemini scholarly convergence: original Run-A item-4 DIM4 (2026-04-21) verdict CONFIRM = ADD, plus FU-22 paired-confirmation Run B (2026-04-27) verdict ADD high. Original Run-B AMEND (2026-04-21, raising classical-vs-modern anachronism risk on retroactive application of the modern term to classical works) explicitly reconciled: the structural fact that ``_infer_genre`` (deliberation.py :496-504) has no keyword trigger for "موسوعة" — the deterministic classifier never assigns Genre.MAWSUAH from a title; it can only enter the system through deliberate owner_metadata override or a future agent-layer classifier, where the assignment is deliberate precisely because the work *functions* as an encyclopedia. The modern Arabic loan موسوعة (mawsūʿa, 19th–20th-century calque of European *encyclopedia*) names comprehensive reference works arranged alphabetically or thematically for lookup, not sequential reading; classical functional analogues (Ibn al-Athīr's al-Nihāyah fī Gharīb al-Ḥadīth d. 606 AH; Ḥājī Khalīfa's Kashf al-Ẓunūn d. 1067 AH; Ibn al-Nadīm's al-Fihrist d. ~385 AH) share the same static-repository architecture. Governing inclusion principle (distilled from FU-25/26 Run-B verdicts): "a genre belongs in NON_APPLICABLE_GENRE_VALUES when its organizing architecture operates as a static repository of attestation, indexing, or archival documentation rather than a graduated didactic curriculum." Mawsūʿa satisfies all three branches — attestation (jāmiʿ-scale comprehensive compilation: al-Ṭabarī's Jāmiʿ al-Bayān, Ibn Rajab's Jāmiʿ al-ʿUlūm wa-l-Ḥikam), indexing (alphabetical organization), archival documentation (al-Khaṭīb al-Baghdādī's Tārīkh Baghdād). New AC-9 (MAWSUAH positive — al-Mawsūʿa al-Fiqhiyya al-Kuwaytiyya rejects owner override on Genre.MAWSUAH Axis 1) added. Documented limitation: hybrid works titled "موسوعة الناشئة" (youth encyclopedia) with internal pedagogical sequence are rare exceptions; the invariant correctly prioritizes the dominant architectural function. Open follow-ups remaining: 18, 21, 24, 27, 28, 34.
- Rule: For works where the reading-level concept does not apply, the source engine MUST serialize SourceMetadata.level as null regardless of any owner override attempt. Non-applicability fires along three axes, any of which is sufficient: Axis 1 (fann-level) — the work's Genre is one of the nine non-applicable members {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah, mujam, tabaqat, mawsuah}; Axis 2 (structural) — the work's composite_work_type == "majmu" (a structural composite whose container-level pedagogy does not apply even when the declared Genre is otherwise leveled); Axis 3 (hadith-subgenre) — when Axis 1 fires for Genre.HADITH_COLLECTION, attribution is refined by hadith_subgenre. Subgenres in the carve-back set LEVELED_HADITH_SUBGENRES (currently {arbain}) reverse the Axis 1 firing — the work is treated as a pedagogical 40-hadith collection (al-Arbaʿīn al-Nawawī of al-Nawawī d. 676 AH; al-Kattānī, al-Risālah al-Mustaṭrafah p. 69-72 Kutub al-Arbaʿīniyyāt) and the level applies. All other hadith subgenres — including null subgenre per Path A (transmission-by-default, iḥtiyāṭ / tawaqquf principle, Ibn Ḥajar Nuzhat al-Naẓar Bāb al-Khabar al-Maqbūl) — confirm Axis 1 firing under Axis 3 (the work is kutub al-riwāyah, transmission collection). Forcing a reading- level label onto an Axis-1 (post-carve-back), Axis-2, or Axis-3 firing work creates false scholarly authority because its organizing principle is transmission, archival reference, or structural compilation, not graduated pedagogical exposition.
