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
| 1 | explained + explanation default unity (EE-1) | **FINALIZED + EMPIRICALLY VALIDATED** | SPEC §6.4b + prompt + tests. Codex: 3 fixed. Gemini: universal. Empirical: taysir PASS, ibn_aqil PASS. |
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

---

## ATOM 1: explained + explanation default unity

### Raw owner artifacts used
- `engines/excerpting/chatgpt_f5_collection/source_artifacts/f5_owner_raw_reaction_2026_04_04.txt`
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
