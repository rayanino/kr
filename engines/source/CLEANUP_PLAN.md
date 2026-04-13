# Source Engine Cleanup Plan

## Summary

This plan covers the `97` tracked files currently under `engines/source/`.

Target end state:

```text
engines/source/
  README.md
```

with `README.md` containing exactly:

```text
Source Engine — spec in progress
```

Everything else currently under `engines/source/` is either:

- deleted as obsolete legacy material, or
- archived to `reference/archive/v1/source_engine/` because it contains reusable domain knowledge, lessons learned, or durable reference material.

### External dependencies that would break if `engines/source/` is removed without follow-up changes

Direct Python imports from `engines.source.contracts` currently exist in:

- `engines/normalization/src/dispatcher.py`
- `engines/normalization/src/layer_detector.py`
- `engines/normalization/src/normalizers/base.py`
- `engines/normalization/src/normalizers/plain_text.py`
- `engines/normalization/src/normalizers/shamela.py`
- `engines/normalization/src/structure_discovery.py`
- `engines/normalization/src/validation.py`
- `engines/normalization/tests/conftest.py`
- `engines/normalization/tests/test_kr_output.py`
- `engines/normalization/tests/test_layer_detection.py`
- `shared/human_gate/src/human_gate.py`
- `shared/human_gate/tests/test_human_gate.py`
- `shared/scholar_authority/src/scholar_authority.py`
- `shared/scholar_authority/tests/test_name_matching.py`
- `shared/scholar_authority/tests/test_scholar_authority.py`
- `tools/smoke_test_validation.py`
- `scripts/normalization_corpus_sweep.py`
- `scripts/run_pipeline.py`
- `scripts/phases/run_phase_a.py`
- `scripts/phases/run_phase_c.py`
- `scripts/phases/run_session6_integration.py`
- `scripts/phases/stress_test_collection.py`

Direct Python imports from `engines.source.src.*` currently exist in:

- `scripts/phases/run_phase_a.py`
- `scripts/phases/run_phase_c.py`
- `scripts/phases/run_session6_integration.py`
- `scripts/phases/stress_test_collection.py`
- `scripts/run_pipeline.py`

Direct Python import from `engines.source.prompts.inference_v1` currently exists in:

- `scripts/phases/run_phase_c.py`

Literal path references to `engines/source/tests/`, `engines/source/contracts.py`, `engines/source/SPEC.md`, and `engines/source/src/*` currently exist in:

- `tests/test_overnight_codex_runtime.py`
- `scripts/check_compliance.py`
- `scripts/check_spec_quality.py`
- `scripts/creative_verification.py`
- `scripts/decompose_spec.py`
- `scripts/generate_sprint_tasks.py`
- `scripts/overnight_codex_evaluator.py`
- `scripts/overnight_codex_orchestrator.py`
- `scripts/overnight_codex_task_generator.py`
- `scripts/overnight_orchestrator.py`
- `scripts/overnight_task_generator.py`
- `scripts/session_quality_gate.py`

This means the cleanup itself is simple, but the repo will need a separate follow-up change outside `engines/source/` before the source engine can actually be reduced to a one-file skeleton.

## Section A — DELETE (no value)

### DEAD_SESSION

- `engines/source/STRATEGIC_PLAN.md`
- `engines/source/docs/session5-architecture.md`
- `engines/source/docs/session5-technology-inventory.md`
- `engines/source/docs/session5-test-plan.md`
- `engines/source/review/OWNER_SANITY_CHECK.md`
- `engines/source/review/PHASE_A_FIXES.md`
- `engines/source/session-3-plan.md`
- `engines/source/session-4-plan.md`
- `engines/source/session-5-plan.md`
- `engines/source/session-6-plan.md`
- `engines/source/src/.gitkeep`
- `engines/source/src/_deferred/__init__.py`
- `engines/source/src/tracer.py`
- `engines/source/tests/.gitkeep`
- `engines/source/tests/__init__.py`

### OLD_REVIEW

- `engines/source/TESTING_PROTOCOL.md`
- `engines/source/VALIDATION_PLAN.md`
- `engines/source/review/BUILD_PREP_AUDIT.md`
- `engines/source/review/CODE_AUDIT_SESSION6.md`
- `engines/source/review/INTEGRITY_AUDIT.md`
- `engines/source/review/SANITY_CHECK_ANSWERS.md`
- `engines/source/review/STEP1_HARDENING.md`
- `engines/source/review/STEP1_QUALITY_REVIEW.md`

### OLD_SPEC

- `engines/source/SPEC.md`
- `engines/source/SPEC_CORE.md`
- `engines/source/reference/TEST_PLAN.md`
- `engines/source/src/citation_discovery.py`
- `engines/source/src/enrichment.py`
- `engines/source/src/extractors/image.py`
- `engines/source/src/extractors/owner_authored.py`
- `engines/source/src/extractors/pdf.py`
- `engines/source/src/extractors/plaintext.py`
- `engines/source/src/extractors/shamela.py`
- `engines/source/src/extractors/word.py`
- `engines/source/src/gap_analysis.py`
- `engines/source/src/llm_client.py`
- `engines/source/src/openiti_enrichment.py`
- `engines/source/src/scholar_authority.py`
- `engines/source/src/work_registry.py`

### OLD_DOCS

- `engines/source/CLAUDE.md`
- `engines/source/docs/architecture.md`
- `engines/source/prompts/README.md`
- `engines/source/reference/DEPENDENCIES.md`
- `engines/source/src/__init__.py`

### OLD_CODE

- `engines/source/contracts.py`
- `engines/source/reference/IMPLEMENTATION_ORDER.md`
- `engines/source/src/config.py`
- `engines/source/src/deduplication.py`
- `engines/source/src/engine.py`
- `engines/source/src/exceptions.py`
- `engines/source/src/extractors/__init__.py`
- `engines/source/src/extractors/plain_text.py`
- `engines/source/src/format_detection.py`
- `engines/source/src/freezer.py`
- `engines/source/src/human_gate.py`
- `engines/source/src/inference_models.py`
- `engines/source/src/logger.py`
- `engines/source/src/registries/scholar_registry.py`
- `engines/source/src/registries/source_registry.py`
- `engines/source/src/registries/work_registry_store.py`
- `engines/source/src/staging.py`
- `engines/source/src/text_utils.py`
- `engines/source/tests/test_boundary_values.py`
- `engines/source/tests/test_config.py`
- `engines/source/tests/test_consensus_integration.py`
- `engines/source/tests/test_contract_boundaries.py`
- `engines/source/tests/test_deduplication.py`
- `engines/source/tests/test_edge_cases.py`
- `engines/source/tests/test_engine.py`
- `engines/source/tests/test_error_paths.py`
- `engines/source/tests/test_freezer.py`
- `engines/source/tests/test_logger.py`
- `engines/source/tests/test_metadata_inference.py`
- `engines/source/tests/test_text_utils.py`
- `engines/source/tests/test_trust_evaluator.py`

## Section B — ARCHIVE (move to `reference/archive/v1/source_engine/`)

Only files in `DOMAIN_KNOWLEDGE`, `LESSONS_LEARNED`, or `USEFUL_REFERENCE` are archived.

### DOMAIN_KNOWLEDGE

#### `engines/source/reference/ABD_INTAKE_SPEC.md`

Reason: obsolete as an intake spec, but it preserves the best single description of real Shamela HTML structure and one durable pipeline principle.

Keep these passages:

- `"Important: Count \`PageNumber\` spans, NOT \`PageText\` divs."`
- `"2. **القسم is special.** It's the only field where the colon is a plain \`:\` character baked into the span text. All other fields use \`<font color=#be0000>:</font>\` (red-colored colon) as the separator."`
- `"the book's declared science is an informational prior, not a routing constraint"`

Everything else in this file is old intake-tool choreography and output layout noise.

#### `engines/source/reference/edge_cases.md`

Reason: durable parser behavior and Shamela-specific failure modes that would be expensive to rediscover.

Keep these passages:

- `"The full \`label: value\` text is appended to \`unrecognized_metadata_lines\`. Zero data loss — everything the parser can't classify is captured verbatim."`
- `"Both values are recorded separately (\`shamela_page_count\` vs \`actual_page_count\` / \`total_actual_pages\`). No correction is attempted. A 69% mismatch rate was observed across the original 7-book corpus — this is a known Shamela data quality issue."`
- `"Keep-first semantics. The first muhaqiq match is kept; subsequent matches are logged with a warning and routed to \`unrecognized_metadata_lines\`. Additionally, \`أصل التحقيق\` is in an explicit exclusion list (\`MUHAQIQ_EXCLUSIONS\`) so it never matches in the first place."`

Everything else is local Stage 0/1 intake-wrapper detail.

#### `engines/source/review/OWNER_SANITY_CHECK_ANSWERS.md`

Reason: this is the richest reusable file for scholarly trust heuristics, publisher caveats, and deferred relationship types.

Keep these passages:

- `"The line should be: \"editors whose name alone increases trust in ANY edition they touch, across all sciences.\" The 8 names on the list meet this bar."`
- `"\"دار الرسالة\" is listed but the actual publisher name is \"مؤسسة الرسالة\" ... \"دار الرسالة\" and \"مؤسسة الرسالة\" are the same entity."`
- `"\"دار الكتب العلمية\" is correctly included but needs a quality caveat. This publisher ... is known in the scholarly community for mass-producing editions of variable quality."`
- `"takmila_of (تكملة — continuation)"`
- `"dhayl_of (ذيل — supplement/appendix)"`

Everything else is question-by-question review scaffolding.

#### `engines/source/src/extractors/shamela_html.py`

Reason: the implementation itself is disposable, but the embedded field map, Arabic label semantics, and corpus-derived parser rules are durable domain knowledge.

Keep these passages:

- `"حقق ∉ تحقيق, خرج ∉ تخريج, علق ∉ تعليق. Both forms must be listed."`
- `"The non-greedy (.*?)</div> regex works because the metadata card has NO nested <div> elements (verified across all 2,519 exports)."`
- `"\\"رواية\\": \\"riwayah\\",  # Hadith transmission/recension (26 books)"`
- `if "القسم" in label:`

Everything else is old implementation scaffolding around those rules.

#### `engines/source/tests/test_deterministic.py`

Reason: the pytest harness is disposable, but this file contains the strongest fixture-backed Arabic integrity and Shamela-format truths.

Keep these passages:

- `"This exact byte sequence must be preserved — no normalization allowed."`
- `"Muhaqiq and author are NEVER the same person in fixture 04."`
- `"Fixture 13: Format B layout extracts title from value inside span."`
- `"Fixture 13: Format B layout extracts author from value inside span."`
- `"Fixture 13: Format B layout extracts muhaqiq from value inside span."`

Everything else is old test harness and direct assertions against the discarded implementation.

### LESSONS_LEARNED

#### `engines/source/LESSONS.md`

Reason: best cross-phase empirical summary of what actually failed and what fixed it.

Keep these passages:

- `"Tests written by the same agent as the code tend to test what the code does, not what the SPEC says. A fresh code audit against the SPEC catches different bugs."`
- `"Scholar registry sparseness caused 70% gate_abort rate in Phase C. Populating science_scope for major scholars before Phase D dropped the rate to 0%."`
- `"Consensus module was oversensitive to cosmetic differences in Phase C/D. 13 of 14 Phase D \"disagreements\" were the same person described differently — not substantive factual disagreements."`
- `"Death dates from single-model inference are unreliable. Check 5g flags these. Downstream engines should not treat flagged death dates as ground truth."`

Everything else is phase-by-phase narrative around those durable findings.

#### `engines/source/docs/session5-contracts-audit.md`

Reason: preserves two high-value lessons that were costly to discover in implementation.

Keep these passages:

- `"The \`unsure\` → \`elevated\` workflow (Layer 3.5: 3+ model consensus when owner says \"unsure\") cannot be represented with a boolean \`resolved\`."`
- `"Validated formula: death_date ≤ 1000 → 0.90; death_date > 1000 → 0.70; no death date → 0.30. Re-verified: 13/13 correct."`

Everything else is session-specific contract surgery.

#### `engines/source/docs/technology-inventory.md`

Reason: preserves the clearest rationale for the custom Arabic scholar-name matcher and the rejection of heavyweight alternatives.

Keep these passages:

- `"This directly addresses the A3-1 problem: \"النووي\" (1 token: {نووي}) vs \"أبو زكريا يحيى بن شرف النووي\" (5 tokens: {ابو, زكريا, يحيى, شرف, نووي}). The shorter name's token set {نووي} is a subset of the longer name's tokens → score ≥ 0.85 → auto-link. SequenceMatcher would score this at 0.267 (character-level overlap), creating a false duplicate."`
- `"Keep the custom approach. The eval_harness implementation is correct for the domain. Neither PyArabic nor CAMeL Tools solves the actual problem (scholarly name identity matching)."`

Everything else is dated package-selection context.

#### `engines/source/review/PHASE_A_LESSONS.md`

Reason: strongest extractor-specific bug history from the 2,519-book sweep.

Keep these passages:

- `"Fix: Guard at top of field loop: \`if \"القسم\" in label: continue\`"`
- `"Two HTML card formats exist:"`
- `"- Format A (standard): \`<span class='title'>LABEL<font>:</font></span> VALUE\`"`
- `"- Format B (variant): \`<span class='title'>LABEL <font>:</font> VALUE ... <font>:</font></span> CONTINUATION\`"`
- ``"`رواية` label (26 books) — architect decision needed on mapping"``

Everything else is metric reporting for a completed sweep.

#### `engines/source/review/STEP0_RESULTS.md`

Reason: retains one owner preference and one name-matching regression worth preserving.

Keep these passages:

- `"\`normalize_arabic_name\` strips diacritics and definite articles but not Arabic commas (،) or other punctuation. LLM-generated full nasab names often include commas ..."`
- `"Full nasab names: Owner confirmed he wants extensive, detailed full nasab forms (not shortened names)."`

Everything else is ephemeral first-integration run reporting.

#### `engines/source/src/metadata_inference.py`

Reason: the file is old code, but it contains durable lessons about confidence provenance and death-date hallucination risk.

Keep these passages:

- `"When one model provides a death_date and the other says None, the date is higher-risk for hallucination."`
- `"Single model = treat death date as unverified if inferred"`
- `"text_fidelity is NOT inferred by LLM — it is a deterministic property of the source format."`

Everything else is implementation-specific orchestration that will be rewritten.

#### `engines/source/src/trust_evaluator.py`

Reason: keeps the validated trust formula and the key lesson about initial evaluation vs re-evaluation.

Keep these passages:

- `"The validated formula (Phase 0, 13/13 correct) uses ONLY the death date:"`
- `"- death_date_hijri ≤ 1000 → 0.90 (classical)"`
- `"- death_date_hijri > 1000 → 0.70 (post-classical with known date)"`
- `"- death_date_hijri is None → 0.30 (unknown)"`
- `"The \"prior sources\" check belongs in trust RE-EVALUATION (§4.A.8 last paragraph), not in initial evaluation."`

Everything else is old implementation detail around a formula that should be re-expressed cleanly in the rewrite.

#### `engines/source/tests/test_registries.py`

Reason: keeps concrete regression lessons about scholar-linking and fail-loud rollback.

Keep these passages:

- `"Regression: أحمد محمد شاكر was auto-linked to أحمد بن محمد بن حنبل"`
- `"Corrupt registry + corrupt .bak → RuntimeError (not silent pass)."`

Everything else is old registry test scaffolding.

#### `engines/source/tests/test_validation.py`

Reason: keeps subtle validation lessons that are easy to accidentally regress.

Keep these passages:

- `"sharh + is_multi_layer=false + empty layers → warning, NO auto-correct (BUG-05 fix)."`
- `"is_multi_layer=True + only matn/tahqiq_note → corrected to False, layers cleared."`

Everything else is direct testing against the discarded implementation.

### USEFUL_REFERENCE

#### `engines/source/review/CORE_VS_DEFERRED.md`

Reason: compact map of what belonged in core vs what was intentionally deferred, plus useful extension-hook language.

Keep these passages:

- `"**Core formats:** \`shamela_html\`, \`plain_text\` only"`
- `"Muhaqiq records as scholars | CORE | Trust evaluation needs muhaqiq identity"`
- `"Layer 1: Self-validation (schema, referential integrity, confidence, dedup re-check, consistency) | CORE | Prevents every write of corrupt data"`
- `"Format detection and metadata extraction must use pluggable extractor modules — not hardcode Shamela/plain-text logic into the main flow"`

Everything else is old scope tabulation around a discarded implementation plan.

#### `engines/source/review/DOWNSTREAM_CONTRACT_AUDIT.md`

Reason: best concise statement of the metadata-chain rule and registry discipline.

Keep these passages:

- `"Correct both downstream SPECs to read from \`library/sources/{source_id}/metadata.json\` for these fields."`
- `"Do NOT expand the registry — that creates redundancy and staleness risk."`

Everything else is detailed downstream audit history.

#### `engines/source/review/STEP2_EVALUATION.md`

Reason: preserves the architectural decisions that were actually validated, plus their cautionary caveat.

Keep these passages:

- `"Decision: KEEP SINGLE-CALL."`
- `"Decision: COMMAND A (Cohere) + OPUS 4.6 (Anthropic)."`
- `"Decision: KEEP CURRENT THRESHOLDS (0.70 / 0.50), PROVISIONALLY."`
- `"Decision: RAISE TO 1000 AH."`
- `"Mandatory build-phase check: before committing to this pair in implementation, compute \"at least one right\" on \`author_identification\` alone."`

Everything else is historical evaluation framing.

#### `engines/source/session-6-next.md`

Reason: mostly dead session choreography, but it contains two real orchestration constraints and one explicit reminder about stale spec text.

Keep these passages:

- `"The SPEC numbers trust as Step 8 and registration as Step 7, but \`SourceRegistryEntry.trust_tier\` is required at write time. Compute trust BEFORE calling register_source."`
- `"work_id must be set BEFORE calling register_source."`
- `"Trust evaluator uses validated formula, not SPEC text."`

Everything else is one-time session execution detail.

#### `engines/source/prompts/inference_v1.py`

Reason: strong prompt-level rules worth preserving even if the entire prompt is rewritten later.

Keep these passages:

- `"Compiler vs. author distinction: a compiler (جامع/مرتب) organized existing material but is not the original author. When both Author and Compiler are present in the metadata, author_identification should identify the ORIGINAL author, not the compiler."`
- `"Set confidence to 0.50 for any field you are genuinely uncertain about. Do NOT guess — low confidence triggers human review, which is the correct outcome for uncertain cases."`
- `"For multi-layer detection: a sharh always contains its matn (multi-layer). ... A تعقبات ... is NOT multi-layer — it is a standalone work referencing another."`
- `"- sectarian_tradition: default \"sunni\" for the vast majority of the collection. Only set otherwise when there is positive evidence"`

Everything else is old prompt packaging.

#### `engines/source/src/consensus.py`

Reason: preserves exact agreement semantics and the conservative attribution ordering.

Keep these passages:

- `"Case B: Both say \"new\" → name_sim >= 0.90 AND death dates agree (±10 years or both None) → True"`
- `CONSERVATIVE_ORDER = ["unknown", "disputed", "traditional", "definitive"]`

Everything else is tied to the old consensus implementation wrapper.

#### `engines/source/src/registries/__init__.py`

Reason: preserve only the atomic-write pattern, not the registry implementation.

Keep this passage:

- `"Atomic writes via write-ahead log pattern:"`

Everything else is disposable implementation machinery.

#### `engines/source/src/validation.py`

Reason: preserves the sharpest formulation of the layer-consistency rules.

Keep these passages:

- `"Genre 'hashiyah' requires 3 layers (matn→sharh→hashiyah)"`
- `"All layer types {layer_types} are tahqiq editorial apparatus (not scholarly commentary) — auto-corrected is_multi_layer to false"`
- `"Death date from single-model inference only (other model abstained). High risk for hallucination — needs manual verification."`

Everything else is old validation implementation.

## Section C — FRESH SKELETON

After cleanup, `engines/source/` should contain only:

```text
engines/source/
  README.md
```

with:

```text
Source Engine — spec in progress
```

No other files remain in `engines/source/`. Every current file is either deleted or archived.

