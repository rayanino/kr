# Foundations Hardening Ledger

> Living record of atom-by-atom doctrine hardening from owner Q&A F1-F8.
> Authority: this session. Updated after each atom completes.

## Agent Teams Decision

**Decision: USE agent teams for research breadth in the per-atom loop.**

Roles:
- **Repo-research agent**: searches codebase for all prior art, SPEC rules, prompts, tests related to current atom
- **Contract-consequence agent**: traces implications through adjacent engines (normalization -> excerpting -> taxonomy -> synthesis)
- **Counterexample agent**: searches for cases that pressure the atom's proposed doctrine

Agent teams do NOT replace:
- Codex shadow challenge (external coworker — repo-state + contract pressure)
- Gemini deep research (external coworker — blind spots + methodology diversity)
- Owner interrogation (human signal)
- Closure discipline (orchestrator judgment)

Agent team outputs are reviewed before closure. They feed the pressure-testing phase.

## Atom Register

| # | Atom Name | Status | Disposition |
|---|-----------|--------|-------------|
| 1 | explained + explanation default unity (EE-1) | **FINALIZED + EMPIRICALLY VALIDATED** | SPEC §6.4b + prompt + tests. Codex: 3 fixed. Gemini: universal. Empirical: taysir PASS, ibn_aqil PASS. Origin: F1 line 222 (first stated), F5 (expanded). |
| 2 | note-compensation vs source-preserving context (NC-1) | **FINALIZED** | NC-1 hierarchy in SPEC §3. Source surroundings vision saved to memory. FP-2, FP-10. |
| 3 | linking-word preservation | **FINALIZED** | C-SC-2 expanded in prompt + SPEC with specific Arabic patterns + "don't flag blindly" instruction. FP-3. |
| 4 | rule/proof split without scholar linkage loss | **DOCUMENTED — deferred to K-1/K-2/K-3** | Owner signal captured in §6.1 design note. FP-8. Current DP rules preserved pending DR-3 resolution. |
| 5 | disagreement mention vs tarjih separation | **DOCUMENTED — deferred to K-1/K-2/K-3** | Owner signal captured in §6.1 design note. FP-8. Tension with current tarjih rule noted. |
| 6 | overgranulation vs undergranulation | **FINALIZED** | FP-9 in SPEC §1.1b. Overgranulated is worse than undergranulated. |
| 7 | forgiving rule / percentage threshold | **DOCUMENTED** | Owner F3 signal captured. No SPEC change — threshold is empirical, calibrated during 30-book probe. |
| 8 | taxonomy must not bias excerpting | **FINALIZED** | FP-4 in SPEC §1.1b. Excerpting is source-driven, not tree-driven. |
| 9 | omission honesty | **DOCUMENTED** | PR-012 in canon. No SPEC change needed — already covered by C-SC-4, C-SC-5 decontextualization rules. |
| 10 | fetched proof vs book-preserved proof | **FINALIZED** | FP-7 in SPEC §1.1b. Two-layer system. Implementation deferred to cross-engine design. |
| 11 | uncertainty gates for unseen methodologies | **FINALIZED** | FP-6 in SPEC §1.1b. Rules + intelligence + uncertainty gates. |
| 12 | global trust poisoning from one local error | **FINALIZED** | FP-5 in SPEC §1.1b. Silent corruption is the worst failure. Always assume wrong until proven. |
| 13 | sanad-matn awareness | **FINALIZED** | FP-11 in SPEC §1.1b. Gemini review gap #3. Sanad = context in fiqh, study object in hadith sciences. |
| 14 | implied dependency detection (taqdir) | **FINALIZED** | FP-12 in SPEC §1.1b + C-SC-2 expanded in prompt + SPEC. Gemini review gap #4. Invisible syntactic anchors. |
| 15 | post-grouping viability check (MV-1) | **FINALIZED** | MV-1 in SPEC §5.3. 25-word minimum floor. DR-backed: ChatGPT 1=2/5, Claude 1=1/5 on TU-5. Cross-ref demotion for <30w. |
| 16 | principle conflict precedence | **FINALIZED** | FP-13 in SPEC §1.1b. 5-level stack: attribution > dialogue > grammar > self-containment > granularity. |
| 17 | speaker-role inversion protection | **FINALIZED** | FP-14 in SPEC §1.1b. فإن قيل / قلنا must stay together. #1 blind spot per ChatGPT DR adversarial review. |
| 18-24 | (remaining F1-F8 atoms: sub-excerpting, source-scope, completeness, variants, quantitative, quote-methodology, separation-aspiration) | QUEUED | To be processed in next session batch |
| B1 | **BATCH 1: Safety & Integrity (17 MAQ atoms)** | **CONFIRMED (4/4 coworkers)** | Codex + Gemini + ChatGPT DR + Claude DR. 10 refinements across 2 DR rounds. |
| B1-FP5 | FP-5 strengthen: cascading trust collapse | **IMPLEMENTED** | Added cascade chain + blast-radius assessment language. No numeric threshold (Codex: breaks salvage). |
| B1-FP2 | FP-2 strengthen: anti-rescue prohibition | **IMPLEMENTED** | Added: context must not silently fix verdicts. Help layers beside source, never overwrite. |
| B1-FP19 | **NEW FP-19: Omission honesty** | **IMPLEMENTED** | Deceptive cleanliness = named failure. Al-Ghazali adversarial example (Gemini). Contract field deferred (Codex). |
| B1-FP20 | **NEW FP-20: Validation rigor** | **IMPLEMENTED** | 5 hardest patterns from Gemini. Hard cases over polished paths. |
| B1-FP21 | **NEW FP-21: Severity class distinction** | **IMPLEMENTED** | Silent corruption (existential) vs visible flagged failure (recoverable). 4 per-science examples. Rephrased per Codex (no taxonomy-external language). |
| B1-FP22 | **NEW FP-22: Anti-covert-excerpter** | **IMPLEMENTED** | Validator must not reshape text/span/boundaries. V-P3-8 exempt (Codex). |
| B2 | **BATCH 2: Self-Containment (5 actionable MAQ atoms)** | **CONFIRMED (2/2: Gemini+Codex, Session 8)** | All 5 atoms confirmed with amendments. SPEC sync + prompt changes → Session 9. |
| B2-P1 | Anti-surface-classification | **CONFIRMED + SPEC SYNC PENDING** | Gemini: CONFIRM (scholarly sound). Codex: NEEDS-REVISION (not in SPEC §5.2.2). T2-1: copy to SPEC. |
| B2-P2 | Forgiving retention (≤15%, لأن/فإن) | **CONFIRMED WITH AMENDMENTS** | Gemini: CHALLENGE (add إذ, لكونه). Codex: NEEDS-REVISION (threshold should be heuristic). T1-1: expand particles + soften threshold → Session 9. |
| B2-P3 | Title-retention asymmetry (MODIFIED) | **CONFIRMED (2/2)** | Gemini: CONFIRM. Codex: CONFIRM. No changes needed. |
| B2-P4 | Dependency-first splits | **CONFIRMED WITH AMENDMENTS** | Gemini: CHALLENGE (fails for Rijal). Codex: CHALLENGE (not formalized). T2-2: add to SPEC. T3-1: Rijal exception deferred. |
| B2-SP | Two-layer model (theory + context) | **CONFIRMED (1/2 Codex)** | Codex: CONFIRM (FP-18 captures it). Gemini: not reviewed (gap). |
| B3 | **BATCH 3: Boundary & Grouping (10 MAQ atoms)** | **CONFIRMED (2/2: Gemini+Codex, Session 8)** | All atoms confirmed with amendments. SPEC sync + prompt changes → Session 9. |
| B3-P1 | Multi-function split (>20% per function) | **CONFIRMED WITH AMENDMENTS** | Gemini: CHALLENGE (exempt تخصيص/شرط/استثناء). Codex: NEEDS-REVISION (20% is weak heuristic). T1-2: soften threshold + semantic exemption → Session 9. |
| B3-P2 | Introduction scope classification | **CONFIRMED + SPEC SYNC PENDING** | Gemini: CONFIRM (distinction sound). Codex: NEEDS-REVISION (not in SPEC §5.3.2). T2-3: add to SPEC. |
| B3-P3 | Three-part proof structure (1+2 together, 3 conditional) | **CONFIRMED WITH AMENDMENTS** | Gemini: CHALLENGE (dialectical exception). Codex: NEEDS-REVISION (no SPEC section + FP-14 cross-ref). T1-3 + T2-4 → Session 9. |
| B3-SP1 | Scholar-quoting-scholar protocol | **CONFIRMED + NEEDS SPEC PROTOCOL** | Gemini: CONFIRM (essential). Codex: NEEDS-REVISION (no SQ-1, LA-2 can flip authorship on nested quotes). T2-5 → Session 9. |
| B3-SP2 | Boundary consistency audit | **CONFIRMED + NEEDS SPEC RULE** | Gemini: CONFIRM. Codex: CHALLENGE (no BC-1 audit rule). T2-6 → Session 9. |
| B3-SP3 | Malformation-first diagnosis | **CONFIRMED + NEEDS SPEC RULE** | Gemini: CONFIRM (universal). Codex: NEEDS-REVISION (no MF-1 rule). T2-7 → Session 9. |
| B3-SP4 | Boundary mustn't distort meaning | **CONFIRMED (2/2)** | Gemini: CONFIRM. Codex: CONFIRM. FP-1+3+9+13 collectively cover this. |
| B4 | **BATCH 4: Granularity (17 MAQ atoms)** | **IMPLEMENTED** | 1 prompt rule (mention≠excerpt, +51w). 16 SPEC-only. Prompt: 1474/1500 (FULL). |
| B4-P1 | Mention is NOT excerpt | **IN PROMPT** | MAQ-047. Owner ALL-CAPS: "a mention IS NOT A REASON TO EXCERPT." Anti-false-positive. |
| B4-SP1 | Forgiving rule ~33% quantitative limit | **SPEC-ONLY** | MAQ-036. Dual-gate: percentage + character count. 10000/500 worked example. Calibration deferred to 30-book probe. |
| B4-SP2 | Anti-duplication via sub-excerpting | **SPEC-ONLY** | MAQ-037. Don't copy whole passage to multiple leaves; sub-excerpt instead. |
| B4-SP3 | Hukm-return visibility | **SPEC-ONLY** | MAQ-038. Short hukm-return in refutation OK, but hukm must also appear at hukm home. |
| B4-SP4 | Intra-khilaf clustering | **SPEC-ONLY** | MAQ-039. Disagreement marker + opinion listing = one excerpt when answering same question. |
| B4-SP5 | Question-cluster methodology | **SPEC-ONLY** | MAQ-040. Already partially captured in DEPENDENCY-FIRST SPLITS prompt rule. Full methodology in SPEC. |
| B4-SP6 | Frozen excerpt immutability | **SPEC-ONLY** | MAQ-041. Tree revision must not rewrite frozen excerpts. Explicit in FP-4. |
| B4-SP7 | Config-sensitivity audit trigger | **SPEC-ONLY** | MAQ-042. If excerpting changes with config, trigger audit. |
| B4-SP8 | False contradiction mechanism | **SPEC-ONLY** | MAQ-043. Overgranulation creates false contradictions in sibling leaves. Added to FP-9 explanation. |
| B4-SP9 | Granulation cascade example | **REFERENCE** | MAQ-044. Owner's al-sarf progressive example preserved as canonical reference. |
| B4-SP10 | No hard character caps + no layout mutation | **SPEC-ONLY** | MAQ-045. Two principles: no caps, no mutation. |
| B4-SP11 | Wrong location = nonexistent | **SPEC-ONLY** | MAQ-046. Example in wrong place = not existing. |
| B4-SP12 | Theory-example vs practice-example | **SPEC-ONLY** | MAQ-048. Distinction + one-example-per-excerpt + archive concept. |
| B4-SP13 | Solved-solver unity (EE-1 extension) | **SPEC-ONLY** | MAQ-049. Solutions NEVER separate from what they solve. |
| B4-SP14 | A×B intertwined protocol | **SPEC-ONLY** | MAQ-050. If both short: duplicate. If A long B short: B stays in A. |
| B4-SP15 | Readability ≠ correctness | **SPEC-ONLY** | MAQ-052. Readable output is not proven correct. |
| B5 | **BATCH 5: Tarjih/Khilaf/Proof (21 MAQ atoms)** | **SPEC-ONLY** | Prompt FULL (1474/1500). All atoms go to SPEC or deferred. |
| B5-SP1 | Attribution-critical tarjih | **SPEC-ONLY** | MAQ-053. Strengthen FP-8 with attribution-loss framing. |
| B5-SP2 | Clipped tarjih prohibition | **SPEC-ONLY** | MAQ-054. Tarjih must include completion of preferred view. |
| B5-SP3 | Hadith variant-mismatch risk | **SPEC-ONLY** | MAQ-056. Scholars may explain different wordings of same proof. |
| B5-SP4 | Proof-as-witness not-memorization-source | **VERIFIED** | MAQ-058. FP-7 covers this. |
| B5-SP5 | Parallel-layer principle (help beside source) | **SPEC-ONLY** | MAQ-059. Help never overwrites source. Extends FP-2. |
| B5-SP6 | Provenance-auditability | **SPEC-ONLY** | MAQ-063. Every unit traceable to source+version+lineage. Extends D-023. |
| B5-SP7 | Proof-stack cross-reference | **DEFERRED** | MAQ-067. Which proofs a scholar used together. Cross-engine. |
| B5-SP8 | Interleaved methodology awareness | **SPEC-ONLY** | MAQ-069. topic→proof→explanation-with-rules→proof pattern. |
| B5-SP9 | Footnote handling protocol | **SPEC-ONLY** | MAQ-071. Directly related footnotes never separated. Default: keep glued. |
| B5-DEF | 7 atoms deferred (cross-engine) | **DEFERRED** | MAQ-057/060/061/062 (proof alignment, variant classification, analytics, layer chunking). |
| B6 | **BATCH 6: Other (9 MAQ atoms)** | **SPEC-ONLY** | Mixed: 3 SPEC, 2 deferred, 1 prompt (FP-15 enforcement), 3 documented. |
| B6-P1 | FP-15 rhetorical posture → prompt | **DEFERRED** | MAQ-I09. FP-15 is SPEC-only. Prompt enforcement deferred to corpus expansion per FP-15 text. |
| B6-SP1 | No-layout-mutation principle | **SPEC-ONLY** | MAQ-I06. Don't change determined excerpt layout. |
| B6-SP2 | Source completeness | **VERIFIED** | MAQ-I07. Covered by frozen source rules. |

---

## ATOM 1: explained + explanation default unity

### Raw owner artifacts used
- `engines/excerpting/chatgpt_f1_collection/source_artifacts/f1_owner_original_notes_2026_04_03.txt` (lines 222-224: first statement of EE-1 principle, chronological origin)
- `engines/excerpting/chatgpt_f5_collection/source_artifacts/f5_owner_raw_reaction_2026_04_04.txt` (expanded articulation of EE-1)
- `engines/excerpting/chatgpt_f5_collection/source_artifacts/f5_full_user_input_2026_04_04.txt`
- `engines/excerpting/chatgpt_f3_collection/source_artifacts/f3_owner_raw_reaction_2026_04_04.txt`

### Cleaned owner-answer layers used
- `engines/excerpting/chatgpt_f5_collection/01_questionnaire_answer.md`
- `engines/excerpting/chatgpt_f5_collection/02_case_dossier.md`
- `engines/excerpting/reference/excerpt_definition_canon/01_dossier.md` (PR-007)

### Owner signal reconstruction
- F5 raw: "The explained is separated from the explanation. This does not make sense."
- Owner WANTS separation but FEARS integrity tradeoffs (hadith versions, wording, grading)
- F5 cleaned: "The deeper failure happened earlier: the explanation was separated from the explained text."
- F3 raw: "why invest in a note and add risks and difficulties, instead of just leaving in the context?"
- Live Q&A (2026-04-04): Excerpts opened for "HOW THE SPECIFIC SCHOLAR HANDLED IT" — hadith is context, not primary study object. Memorization uses fetched authoritative sources.

### Owner tensions
1. WANTS separation of concerns (ideal taxonomy) vs FEARS integrity loss (practical reality)
2. Acknowledges he may be wrong — asks for deep research on feasibility
3. Explicitly separates study workflows: library = understanding/analysis, memorization = separate apps + fetched sources

### Coworker outputs used
- **CC repo-search agent**: SPEC VC-1, DP-5, grouping rules (definition+examples, hadith+chain+commentary), LA-1/LA-2 attribution, PR-007 canon evidence
- **CC contract-consequence agent**: Architecture already supports doctrine. No breaking changes. Recommended additive CompoundUnitComposition marker (~200 lines total surface).
- **Codex**: 3 findings — HIGH: chunk-split limitation (fixed: SPEC corrected to document honestly), MEDIUM: hadith sequence inconsistency (fixed: SPEC §6.3 aligned with prompt), MEDIUM: soft over-merge scope (accepted: existing topic-split rules are the hard guard), LOW: tests are prompt-presence only (accepted: behavioral tests require LLM calls)
- **Gemini**: Confirmed EE-1 holds universally across nahw, tafsir, usul, aqidah. No science-specific exceptions. "No classical Islamic science where separating the explained from the explanation is standard practice within a single teaching unit of a single book."

### Research findings
- SPEC already has specific instances (VC-1, DP-2, grouping rules) but no GENERAL principle
- Phase 2 grouping prompt already instructs "hadith + chain + commentary = one unit" but not the general case
- Canon PR-007: "operationally usable but not frozen" — enough evidence to harden a default
- Hard-judgment warns against "mistaking repeated pressure for completed doctrine" — doctrine has explicit exceptions
- Contract analysis: zero breaking changes, all additive

### Counterexample analysis
- Tafsir (ayah+commentary): ayah repeated at each section. BUT owner uses library for scholar's analysis, not raw ayah. Unity still holds within excerpts.
- Hadith collections (separate sharh books): Different SOURCES in library, not splitting within one source. Not a counterexample.
- Very long explanations: Handled by Phase 1 chunk splitting with context preservation.
- Multi-explanation (5 scholars explain same hadith): Duplication is CORRECT — each scholar's handling is unique per owner signal.
- Over-merging (whole chapter = one unit): Controlled by Phase 2 classification boundaries. EE-1 applies to IMMEDIATELY adjacent pairs, not everything "related."

### Doctrine adopted

**EE-1 (Default unity):** An explained object and its immediately following explanation form one teaching unit by default. The explained text is context for the explanation — separating them orphans the explanation.

**Scope:** Immediately adjacent within same division. Does NOT apply across sources, across scholarly function boundaries, or when chunk limits force a split.

**Exceptions:** (1) Different sources/books, (2) Phase 2 classifies a different function boundary, (3) Chunk size limits with context preservation.

### Implementation consequence
- **SPEC**: Added EE-1 to §5.3.2 grouping rules (general principle, first rule). Added §6.4b formal domain rule with scope, exceptions, and rationale. (+42 lines)
- **Prompt**: Updated `phase2_group.py` GROUP_SYSTEM_PROMPT with EE-1 as first grouping rule.
- **Tests**: Added `test_ee1_explained_explanation_unity` to TestGroupSystemPrompt class.
- **Contracts**: CompoundUnitComposition marker DEFERRED — additive, no urgency, can be added when Phase 3 needs it.

### Tests added/run
- `test_ee1_explained_explanation_unity`: PASSED (verifies EE-1 present in prompt with correct content)
- Full deterministic suite: 898 passed, 0 failed (8 LLM integration tests deselected)
- pyright: 0 errors on modified file
- SPEC quality: 57 defects (all pre-existing, 0 new)

### Unresolved risks
1. **Coworker challenge not yet received.** Codex and Gemini dispatch prompts prepared but not executed. Atom cannot be FINALIZED until at least one external challenge confirms the doctrine.
2. **Tafsir exception not fully researched.** The tafsir pattern (ayah repeated at each section) might justify an exception for tafsir sources. Needs Gemini deep research on whether tafsir excerpts need the ayah included or can safely reference it.
3. **Phase 1 chunk splitting at explained/explanation boundary.** If a chunk split falls between a hadith and its المعنى الإجمالي, they end up in different chunks, and D-011 prevents cross-chunk grouping. Need to verify Phase 1 split logic prefers boundaries AFTER explanation, not between explained/explanation.
4. **No empirical validation yet.** The doctrine is encoded in the prompt but not tested against a live smoke run. Will be validated when the full smoke run happens after all atoms.

### Final disposition
**FINALIZED.** Codex challenged (3 findings, all addressed). Gemini confirmed (universal across 5 sciences, no exceptions). All hardening criteria met.

---

## ATOM 2: note-compensation vs source-preserving context

### Raw owner artifacts used
- `engines/excerpting/chatgpt_f5_collection/source_artifacts/f5_owner_raw_reaction_2026_04_04.txt` (lines 44-51)
- `engines/excerpting/chatgpt_f3_collection/source_artifacts/f3_owner_raw_reaction_2026_04_04.txt` (lines 48-52)
- Live Q&A answer (2026-04-04): owner prefers original source text, proposed "source surroundings" hoverable box

### Owner signal reconstruction
- "why invest in a note and add risks and difficulties, instead of just leaving in the context?"
- "KNOWLEDGE INTEGRITY instead of CONTEXT PRESERVATION, the first one (knowledge integrity) prevails"
- "ALWAYS TRY TO KEEP THINGS AS CLOSE TO THE ORIGINAL AUTHORS WORDINGS / WORK / SOURCE AS POSSIBLE"
- "the note is not extensive enough for the extreme detail the library aims to provide"
- Live Q&A: "Nothing beats the peace of mind and assurance received from seeing the hard facts: the original text from the book"
- NEW IDEA: every excerpt should have hoverable access to surrounding pages from the source

### Owner tensions
- None identified — the hierarchy is clear and consistent across F5, F3, and live Q&A

### Research findings
- ExcerptRecord already carries source_id, div_id, physical_pages, chunk_index — sufficient metadata for source surroundings
- context_hint field exists as LLM-generated brief note for PARTIAL excerpts
- The source surroundings display is a synthesis/UI feature — excerpting engine already produces all needed metadata
- No contract changes required in excerpting — the metadata is already there

### Doctrine adopted

**NC-1 (Context resolution hierarchy):** Three-tier hierarchy for context resolution:
1. Structural unity (EE-1) — prevent the gap
2. Source surroundings — let the reader see the actual source pages (no AI generation)
3. Generated context_hint — supplementary guidance pointing into the surroundings (downgraded from primary mechanism)

### Implementation consequence
- **SPEC §3**: Added NC-1 hierarchy documentation between PARTIAL definition and Phase 3 action (+18 lines)
- **Contracts**: NO changes needed — ExcerptRecord already carries all required metadata
- **Source surroundings display**: Documented as synthesis/UI feature — deferred but saved to memory
- **context_hint role**: Downgraded from "primary rescue mechanism" to "supplementary navigation guidance"

### Tests added/run
- Full deterministic suite: 907 passed, 0 failed
- No new tests needed — no contract or code changes, only SPEC doctrine

### Unresolved risks
1. **Coworker challenge not yet received.** Should be included in the Atom 1 dispatch batch.
2. **Source surroundings display is deferred.** Until the synthesis/UI layer implements the hoverable box, PARTIAL excerpts still rely on context_hint as the primary visible mechanism. The hierarchy is documented but tier 2 is not yet operational.
3. **Token cost of source surroundings** not yet analyzed. Showing 3 pages of context per excerpt could be significant at scale.

### Final disposition
**IMPLEMENTED + TESTED — AWAITING COWORKER CHALLENGE.**

---

## BATCH 1: Safety & Integrity (Session 2, 2026-04-04)

### Scope
17 atoms from MERGED_ATOM_QUEUE.md Section D (MAQ-001 through MAQ-017). Covers trust poisoning, silent failures, deceptive cleanliness, corruption prevention, severity classification, validation rigor.

### Raw owner artifacts used
- `engines/excerpting/f1-owner-original-notes.txt` (F1 raw, 430 lines — foundational vision, threat detection, NO DECEPTION principle)
- `engines/excerpting/chatgpt_f2_collection/source_artifacts/f2_owner_raw_draft_and_followups_2026_04_03.txt` (F2 raw — study methodology, personal stakes)
- F3-F8 raw reactions and structured collections (nonnegotiables, red-team tests)
- Queue audit: 124 gaps cross-referenced

### Coworker reports

**Codex CLI (Contract Guardian):**
- FP-5 strengthen: MODIFY — no numeric stop threshold (breaks salvage behavior in phase3_validation.py:246). Cascade language acceptable.
- FP-19 (omission honesty): MODIFY — SPEC already says study-ready = "no deceptive omission" (FP-18 line 69), but contracts.py has no visible-cut field. Add principle now, defer contract field.
- FP-20 (validation rigor): ACCEPT — closes real validation-policy gap. Regression: LOW.
- FP-21 (severity class): MODIFY — rephrase as "silent corruption vs visible flagged failure" (not "misplacement" which is excerpting-external per FP-4). contracts.py already has gate_flags/review_flags for visible failures.
- FP-22 (anti-covert-excerpter): MODIFY — narrow to text/span/boundary reshaping. Absolute ban breaks V-P3-8 (orphan-footnote removal).
- Red-team automation: YES — parametrized pytest mutation cases (diacritic inject/swap + split-point mutation).

**Gemini CLI (Scholarly Auditor):**
- All 5 FPs: ACCEPT STRONGLY. "Without FP-19 and FP-21, the engine is not a scholarly tool; it is a high-speed heresy generator."
- FP-19 adversarial: cutting al-Ghazali's condemnation of philosophers' views ("وهذا كفر صريح") leaves a sentence attributing kufr to al-Ghazali himself. Syntactically flawless, semantically catastrophic.
- FP-21 per-science examples: fiqh (dropped condition), hadith (mudraj insertion), tafsir (dropped invalidation), nahw (dropped grammatical judgment).
- FP-20: 5 hardest patterns — dialectical trap, pronoun disconnects, extended digressions, deferred exceptions, nested quotations.
- System impact: mapped blast radius across all 6 components (contracts, P1, P2, P3, taxonomy, synthesis).

**DR (Adversarial):** PENDING — owner relay prompt prepared, awaiting dispatch.

### Synthesis and CC decisions
| FP | Codex | Gemini | CC Decision |
|----|-------|--------|-------------|
| FP-5 strengthen | MODIFY (no numeric threshold) | Accept | **MODIFY**: cascade language added, no threshold |
| FP-19 (omission) | MODIFY (need contract field) | Accept strongly | **MODIFY**: principle now, field deferred |
| FP-20 (rigor) | ACCEPT | Accept | **ACCEPT** |
| FP-21 (severity) | MODIFY (rephrase) | Accept | **MODIFY**: rephrased per Codex |
| FP-22 (validator) | MODIFY (narrow scope) | Accept | **MODIFY**: narrowed, V-P3-8 exempt |

### Implementation
- **SPEC §1.1b FP-5**: Strengthened with cascading trust collapse language + blast-radius assessment requirement (+3 sentences)
- **SPEC §1.1b FP-2**: Strengthened with anti-rescue prohibition + help-layer-beside-source rule (+4 sentences)
- **SPEC §1.1b FP-19**: New principle — omission honesty, deceptive cleanliness named failure, al-Ghazali example, contract field deferred
- **SPEC §1.1b FP-20**: New principle — validation rigor, 5 hardest patterns, adversarial test requirement
- **SPEC §1.1b FP-21**: New principle — severity class distinction, 4 per-science examples, rephrased per Codex
- **SPEC §1.1b FP-22**: New principle — anti-covert-excerpter, narrowed scope, V-P3-8 exempt
- **No prompt changes** (these are meta-principles, not Phase 2 instructions)
- **No contract changes** (contract field for FP-19 deferred)

### Tests
- 907 passed, 0 failures, 0 regressions
- Prompt-SPEC sync: PASSED
- Red-team test automation: PENDING (2 pytest cases to create: diacritic injection + split/merge mutation)

### Unresolved risks
1. **DR coworker has not reviewed.** Batch status is PRELIMINARY until DR confirms. DR prompt prepared and presented to owner.
2. **FP-19 contract field deferred.** Omission honesty is a principle without runtime enforcement until a visible-cut field is added to ExcerptRecord.
3. **Red-team tests not yet automated.** F7-RT-001 (diacritic injection) and F7-RT-002 (split/merge mutation) need to become actual pytest cases.
4. **FP-20 test gap.** The 5 hardest patterns from Gemini need corresponding test fixtures with real Arabic text.

### Final disposition
**PRELIMINARY — 2/3 coworkers confirmed. Awaiting DR review.**
