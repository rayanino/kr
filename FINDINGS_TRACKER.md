# Findings Tracker — Research Sprint 2026-03-28

Source: `overnight/results/` (commit 07ed999b). 19 tasks across Claude/Codex/Gemini.

---

## BUGS (fix immediately)

- [x] BUG-001: empty string similarity returns 1.0 — `shared/scholar_authority/src/name_matching.py:60` — FIXED (swapped emptiness check before equality)
- [x] BUG-002: PageRange allows inverted ranges — `engines/excerpting/contracts.py` — FIXED (added model_validator)
- [ ] BUG-003: TermVariant model incompatible — `engines/excerpting/contracts.py` has `variants: list[str]`, `engines/taxonomy/contracts.py` has `context: str`. Will break at runtime. Source: `spec-audit/contract_chain_verification.md`
- [ ] BUG-004: GapType enum mismatch — taxonomy has 6 values, synthesis only 3. Source: `spec-audit/contract_chain_verification.md`
- [ ] BUG-005: consensus failure silently absorbed — per-chunk `run_consensus` failures set `verification_skipped` flag but do NOT emit EX-M-011 to error list. Invisible in `Phase3Result.errors`. Source: `edge-tests/test_state_machine.py` test 13
- [ ] BUG-006: word_count not enforced at construction — `AssembledChunk` has no `model_validator` for I-AC-1. Mismatch only caught by standalone `validate_ac_invariants()`. Source: `edge-tests/test_state_machine.py` test 10

## READY TO IMPLEMENT (next 1-2 sessions)

- [ ] IMP-001: **Parallel execution (ThreadPool)** — 4-8x speedup wrapping per-phase chunk loops in `ThreadPoolExecutor(max_workers=4)`. Zero accuracy risk. Source: `innovation/cost_efficiency.md`
- [ ] IMP-002: **Concurrency precautions** — BoundedSemaphore(5) on subprocess calls, per-worker adapter isolation, collect-then-merge for Phase 3 results. Required before IMP-001. Source: `edge-tests/concurrency_analysis.md`
- [ ] IMP-003: **Confidence-threshold consensus skip** — Already partially at `phase3_consensus.py:748`. Extend with enrichment-confidence thresholds. Source: `innovation/cost_efficiency.md`
- [ ] IMP-004: **Rule-based cross-reference detection** — Detect كما تقدم, سيأتي etc. as F-DET-10 deterministic field. Reduces LLM dependency. Source: `innovation/cost_efficiency.md`

## INTEGRATE BEFORE TAXONOMY BUILD (blocks next engine)

- [ ] TAX-001: Fix immutability vs migration paradox — SPEC says placed is immutable AND tree evolves. Physically impossible. Source: `cross-provider/taxonomy_spec_challenge.md`
- [ ] TAX-002: Allow branch-level placement — قواعد فقهية belong at branch, not forced into leaves. Source: `cross-provider/taxonomy_spec_challenge.md`
- [ ] TAX-003: Replace ASCII slugs with UUID — Arabic concepts in ASCII creates mapping hell. Source: `cross-provider/taxonomy_spec_challenge.md`
- [ ] TAX-004: Define Arabic normalization contract for terminology matching — صلاة vs الصلاة undefined. Source: `cross-provider/taxonomy_spec_challenge.md`
- [ ] TAX-005: Fix pending queue — no TTL/escalation for excerpts waiting on tree creation. Source: `cross-provider/taxonomy_spec_challenge.md`
- [ ] TAX-006: LLM reasoning only for low-confidence placements — 100K excerpts x "brief explanation" = 90% repetitive. Source: `cross-provider/taxonomy_spec_challenge.md`

## EXTERNAL INTEGRATIONS (high value, low effort)

- [ ] EXT-001: **Tanzil Quran text** — download, build n-gram index for deterministic citation detection. Zero LLM cost. Source: `innovation/arabic_nlp_survey.md`
- [ ] EXT-002: **usul-data authors.json** — MIT licensed, 6,236 scholar records. Import into scholar_authority registry. Source: `innovation/cross_pollination.md`
- [ ] EXT-003: **OpenITI URI naming** — adopt `{HijriDeathYear}{Shuhra}.{BookTitle}` for interoperability with 40K+ corpus. Source: `innovation/cross_pollination.md`
- [ ] EXT-004: **GATE Arabic embeddings** — prototype for taxonomy pre-filtering. 80-90% fewer LLM calls. Source: `innovation/arabic_nlp_survey.md`
- [ ] EXT-005: **CAMeL Tools NER** — secondary signal for scholar name extraction. Classical Arabic BERT variant. Source: `innovation/arabic_nlp_survey.md`

## ARCHITECTURE (design sessions needed)

- [ ] ARCH-001: Delete ghost engines (passaging + atomization) — 1,232 lines dead contracts, 54 source files, 0 tests. Source: `innovation/architecture_challenge.md`
- [ ] ARCH-002: Prune deferred contracts in normalization — 17 always-null classes, 30+ unused enum values. Source: `innovation/architecture_challenge.md`
- [ ] ARCH-003: Calibrate consensus per classification type — 100% agreement on some types means single model sufficient. 40-50% cost savings. Source: `innovation/architecture_challenge.md`
- [ ] ARCH-004: Design search/retrieval subsystem — library is currently unsearchable. Source: `innovation/architecture_challenge.md`
- [ ] ARCH-005: Vector-first taxonomy — embed science trees, semantic nearest-neighbor, LLM verifies top-3. 10x cheaper. Source: `cross-provider/architecture_challenge.md`
- [ ] ARCH-006: Tiered LLM approach — fast local model for simple classifications, consensus only for uncertain. Source: `cross-provider/architecture_challenge.md`

## DOMAIN KNOWLEDGE (expert review needed)

- [ ] DOM-001: Multi-opinion khilaf chain handling — 3-5 opinion chains with tarjih, not just binary. Source: `innovation/domain_knowledge_gaps.md`
- [ ] DOM-002: Hadith collection-specific patterns — Bukhari tarajim, Tirmidhi commentary, mu'allaq citations. Source: `innovation/domain_knowledge_gaps.md`
- [ ] DOM-003: Aqeedah sect-attribution sensitivity — author presenting heterodox position to refute it. Source: `innovation/domain_knowledge_gaps.md`
- [ ] DOM-004: 3+ text layer detection — hashiyah and ta'liqat may collapse into sharh. Source: `innovation/domain_knowledge_gaps.md`
- [ ] DOM-005: Science-specific processing differences — fiqh vs hadith vs tafsir vs nahw. Source: `innovation/domain_knowledge_gaps.md`

## VALIDATED DECISIONS (no action needed, keep for reference)

- IslamicLegalBench: Best LLM 68% correct, 21% hallucination on Islamic legal content — validates multi-model consensus (D-041)
- Current pipeline architecture validated as sound — alternatives (RAG, fine-tuning, agents) sacrifice properties KR values
- Incremental processing rated highest alternative (4/5) but is a FUTURE enhancement, not replacement
- Excerpting engine: 106 rules verified, 93 implemented+tested, 0 unimplemented — ready for integration run

## FUTURE (post-excerpting validation)

- [ ] FUT-001: Incremental pipeline processing — each book enriches context for next. Source: `innovation/radical_alternatives.md`
- [ ] FUT-002: CTS-like passage citation scheme — human-readable excerpt IDs. Source: `innovation/cross_pollination.md`
- [ ] FUT-003: Evaluate Taxonomy+Synthesis merge — intermediate PlacedExcerpt is just excerpt + one field. Source: `innovation/architecture_challenge.md`
