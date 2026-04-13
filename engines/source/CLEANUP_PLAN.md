# Source Engine Archive-First Reset Plan

## Summary

This replaces the earlier delete-heavy cleanup approach.

The goal is:

1. remove the old source engine from the active authority surface
2. preserve historical memory inside `engines/source/` as quarantined reference
3. make archive trust explicit so future agents do not treat old material as live authority

### Target active tree

```text
engines/source/
  README.md
  reference/
    archive/
      v1/
        source_engine/
          ARCHIVE_INDEX.md
          FILE_MANIFEST.md
          conftest.py
          docs/
          prompts/
          reference/
          review/
          src/
          tests/
```

### Rules

- Active authority stays tiny.
- Nearly all non-trivial tracked files are archived, not deleted.
- Original relative paths are preserved under `engines/source/reference/archive/v1/source_engine/`.
- Archived material is reference-only and non-authoritative.
- Only trivial markers and confirmed near-empty files are deleted.
- This cleanup plan does not touch files outside `engines/source/`.

### Clarification on Arabic name research

There is no tracked file named `engines/source/reference/ARABIC_NAME_RESEARCH.md`.

The archived source for the Arabic scholar-name matching rationale is:

- `engines/source/docs/technology-inventory.md`

### External breakage note

Reducing the active `engines/source/` tree to only `README.md` plus the in-engine archive will still break imports and literal path references elsewhere in the repo. Those follow-up fixes are intentionally out of scope here because this task is restricted to `engines/source/`.

Known external breakage surfaces below are representative, not exhaustive. They include direct imports, contract references, skill examples, requirements docs, testing docs, and manifest/config references that currently assume the active `engines/source/` tree still exists.

Known external breakage surfaces include:

- imports from `engines.source.contracts` in `engines/normalization/*`, `shared/human_gate/*`, `shared/scholar_authority/*`, `tools/smoke_test_validation.py`, `scripts/normalization_corpus_sweep.py`, `scripts/run_pipeline.py`, and multiple `scripts/phases/*`
- imports from `engines.source.src.*` in `scripts/phases/run_phase_a.py`, `scripts/phases/run_phase_c.py`, `scripts/phases/run_session6_integration.py`, `scripts/phases/stress_test_collection.py`, and `scripts/run_pipeline.py`
- import from `engines.source.prompts.inference_v1` in `scripts/phases/run_phase_c.py`
- literal path references to `engines/source/tests/`, `engines/source/contracts.py`, `engines/source/SPEC.md`, and `engines/source/src/*` in overnight/task-generation scripts and some repo tests
- additional doc/config/reference surfaces such as:
  - `shared/scholar_authority/REQUIREMENTS_source.md`
  - `shared/human_gate/REQUIREMENTS_source.md`
  - `shared/validation/REQUIREMENTS_source.md`
  - `shared/consensus/REQUIREMENTS_source.md`
  - `.claude/skills/consensus-pattern/SKILL.md`
  - `reference/TESTING_FRAMEWORK.md`
  - `reference/PRE_BATCH_VERIFICATION_PLAN.md`
  - `reference/PRE_BATCH_EXECUTION_PROTOCOL.md`
  - `overnight/tonight_manifest.json`
  - `overnight/sprint_manifest.json`
  - `overnight/sprint_write_manifest.json`
  - `overnight/parallel_manifest.json`

## Active Surface

After execution, the only active file at the root of `engines/source/` should be:

- `engines/source/README.md`

with this content:

```md
# Source Engine

Fresh restart in progress.

The previous source-engine implementation has been removed from the active surface.
Historical material from the previous iteration is preserved under
`reference/archive/v1/source_engine/`.

Archived files are reference-only and are not authoritative for the new build.
Do not implement against the archive without explicit approval from the new source-engine spec.
```

## Delete Only

Delete only the trivial files below:

- `engines/source/prompts/README.md` — near-empty placeholder
- `engines/source/src/.gitkeep` — marker only
- `engines/source/src/__init__.py` — trivial package marker/docstring only
- `engines/source/src/_deferred/__init__.py` — trivial package marker/docstring only
- `engines/source/tests/.gitkeep` — marker only
- `engines/source/tests/__init__.py` — empty package marker

## Archive Manifest

Every remaining tracked file is archived exactly once.

Trust tiers:

- `Tier A` — corpus-verified or owner-validated knowledge
- `Tier B` — lessons learned or failure memory
- `Tier C` — architectural reference
- `Tier D` — obsolete implementation snapshot

### Tier A — Corpus-Verified / Owner-Validated Knowledge

- `engines/source/reference/ABD_INTAKE_SPEC.md` — real Shamela structure facts and durable pipeline principles
- `engines/source/reference/edge_cases.md` — verified parser edge cases and preservation rules
- `engines/source/review/OWNER_SANITY_CHECK_ANSWERS.md` — owner-confirmed editor, publisher, and relationship heuristics
- `engines/source/review/PHASE_A_LESSONS.md` — extractor lessons from 2,519 real Shamela exports
- `engines/source/review/STEP0_RESULTS.md` — owner-confirmed full-nasab preference and early integration realities
- `engines/source/src/extractors/shamela_html.py` — corpus-derived Shamela label map and parser rules
- `engines/source/tests/test_deterministic.py` — fixture-backed Arabic and Shamela truths

### Tier B — Lessons Learned / Failure Memory

- `engines/source/LESSONS.md` — cross-phase empirical lessons
- `engines/source/docs/session5-contracts-audit.md` — contract mistakes and validated trust-rule correction
- `engines/source/review/BUILD_PREP_AUDIT.md` — pre-build gap memory
- `engines/source/review/CODE_AUDIT_SESSION6.md` — code-audit failure memory
- `engines/source/review/INTEGRITY_AUDIT.md` — spec-defect audit history
- `engines/source/review/PHASE_A_FIXES.md` — extractor bug-fix memory
- `engines/source/review/SANITY_CHECK_ANSWERS.md` — smaller but still useful answer-memory artifact
- `engines/source/review/STEP1_HARDENING.md` — hardening-session memory
- `engines/source/review/STEP1_QUALITY_REVIEW.md` — quality-review memory
- `engines/source/review/STEP2_EVALUATION.md` — evaluated architectural decisions and caveats
- `engines/source/src/metadata_inference.py` — implementation-embedded lessons on confidence provenance and death-date risk
- `engines/source/src/trust_evaluator.py` — implementation-embedded validated trust formula and re-evaluation lesson
- `engines/source/tests/test_registries.py` — regression memory for scholar-linking and rollback behavior
- `engines/source/tests/test_validation.py` — regression memory for layer and death-date validation

### Tier C — Architectural Reference

- `engines/source/CLEANUP_PLAN.md` — reset-planning record for the archive itself
- `engines/source/CLAUDE.md` — old engine orientation and canonical examples
- `engines/source/SPEC.md` — superseded but still useful historical spec
- `engines/source/SPEC_CORE.md` — prior behavioral authority snapshot
- `engines/source/STRATEGIC_PLAN.md` — historical strategy and handoff framing
- `engines/source/TESTING_PROTOCOL.md` — validation process design
- `engines/source/VALIDATION_PLAN.md` — validation governance snapshot
- `engines/source/contracts.py` — old schema authority snapshot
- `engines/source/docs/architecture.md` — old pipeline/module map
- `engines/source/docs/session5-architecture.md` — registration/trust/validation architecture snapshot
- `engines/source/docs/session5-technology-inventory.md` — session-local tech decisions
- `engines/source/docs/session5-test-plan.md` — session-local testing design
- `engines/source/docs/technology-inventory.md` — strongest archived rationale for name matching and tool choices
- `engines/source/prompts/inference_v1.py` — archived prompt reference with durable anti-hallucination rules
- `engines/source/reference/DEPENDENCIES.md` — dependency snapshot
- `engines/source/reference/IMPLEMENTATION_ORDER.md` — build-order reference
- `engines/source/reference/TEST_PLAN.md` — old test planning snapshot
- `engines/source/review/CORE_VS_DEFERRED.md` — core-vs-deferred scope and extension hooks
- `engines/source/review/DOWNSTREAM_CONTRACT_AUDIT.md` — cross-engine metadata-chain audit
- `engines/source/session-6-next.md` — orchestration constraints and integration hazards
- `engines/source/src/consensus.py` — author/work agreement semantics
- `engines/source/src/format_detection.py` — format-detection marker logic
- `engines/source/src/inference_models.py` — archived intermediate inference contract
- `engines/source/src/registries/__init__.py` — atomic-registration reference
- `engines/source/src/text_utils.py` — archived transliteration and text-utility reference
- `engines/source/src/validation.py` — archived validation-rule reference
- `engines/source/tests/test_boundary_values.py` — boundary and scoring reference
- `engines/source/tests/test_contract_boundaries.py` — source-to-downstream contract boundary reference
- `engines/source/tests/test_freezer.py` — frozen-source invariant reference
- `engines/source/tests/test_metadata_inference.py` — prompt/inference behavior reference
- `engines/source/tests/test_trust_evaluator.py` — trust-rule reference

### Tier D — Obsolete Implementation Snapshot

- `engines/source/docs/architecture.md` is already classified above as Tier C
- `engines/source/review/OWNER_SANITY_CHECK.md` — one-off questionnaire template
- `engines/source/session-3-plan.md` — session logistics
- `engines/source/session-4-plan.md` — session logistics
- `engines/source/session-5-plan.md` — session logistics
- `engines/source/session-6-plan.md` — session logistics
- `engines/source/src/citation_discovery.py` — deferred stub
- `engines/source/src/config.py` — old implementation
- `engines/source/src/deduplication.py` — old implementation
- `engines/source/src/engine.py` — old implementation
- `engines/source/src/enrichment.py` — deferred stub
- `engines/source/src/exceptions.py` — old implementation
- `engines/source/src/extractors/__init__.py` — old implementation wrapper
- `engines/source/src/extractors/image.py` — deferred stub
- `engines/source/src/extractors/owner_authored.py` — deferred stub
- `engines/source/src/extractors/pdf.py` — deferred stub
- `engines/source/src/extractors/plain_text.py` — old implementation
- `engines/source/src/extractors/plaintext.py` — deferred stub
- `engines/source/src/extractors/shamela.py` — old extractor surface superseded by `shamela_html.py`
- `engines/source/src/extractors/word.py` — deferred stub
- `engines/source/src/freezer.py` — old implementation
- `engines/source/src/gap_analysis.py` — deferred stub
- `engines/source/src/human_gate.py` — old implementation
- `engines/source/src/llm_client.py` — deferred/unused surface
- `engines/source/src/logger.py` — old implementation
- `engines/source/src/openiti_enrichment.py` — deferred stub
- `engines/source/src/registries/scholar_registry.py` — old implementation
- `engines/source/src/registries/source_registry.py` — old implementation
- `engines/source/src/registries/work_registry_store.py` — old implementation
- `engines/source/src/scholar_authority.py` — deferred stub
- `engines/source/src/staging.py` — old implementation
- `engines/source/src/tracer.py` — tracer-bullet artifact
- `engines/source/src/work_registry.py` — deferred stub
- `engines/source/tests/test_config.py` — old implementation test
- `engines/source/tests/test_consensus_integration.py` — old implementation test
- `engines/source/tests/test_deduplication.py` — old implementation test
- `engines/source/tests/test_edge_cases.py` — old implementation test
- `engines/source/tests/test_engine.py` — old implementation test
- `engines/source/tests/test_error_paths.py` — old implementation test
- `engines/source/tests/test_logger.py` — old implementation test
- `engines/source/tests/test_text_utils.py` — old implementation test

## Archive Support Files To Create

Create these new files during execution:

- `engines/source/reference/archive/v1/source_engine/ARCHIVE_INDEX.md`
- `engines/source/reference/archive/v1/source_engine/FILE_MANIFEST.md`
- `engines/source/reference/archive/v1/source_engine/conftest.py`

### `ARCHIVE_INDEX.md`

Purpose:

- explain that everything in the archive is reference-only and non-authoritative
- explain Tier A / B / C / D
- point readers to the new active `README.md`
- warn that archived specs, code, prompts, and tests must not be implemented against without explicit approval

Minimum sections:

1. archive purpose
2. authority warning
3. trust tier definitions
4. top Tier A files worth reading first
5. note about archived tests being blocked from collection

### `FILE_MANIFEST.md`

Purpose:

- list every archived file exactly once
- make file accounting auditable after the move

Columns:

- original path
- archived path
- trust tier
- reason preserved
- tags from this set:
  - `corpus_facts`
  - `owner_confirmed_heuristics`
  - `lessons_learned`
  - `architectural_reference`
  - `obsolete_implementation`

### `conftest.py`

Purpose:

- prevent archived tests from being collected accidentally by pytest

Required behavior:

- ignore all archived `test_*.py` files under `engines/source/reference/archive/v1/source_engine/`

Implementation expectation:

```python
collect_ignore_glob = ["**/test_*.py"]
```

If that glob is too broad for pytest in this repo, use archive-local explicit patterns that ignore all archived files under `tests/`.

## Anchor Passages Worth Preserving

These are the highest-signal passages that justify the archive-first plan.

These anchors are not a whitelist. The full archived files remain preserved under the archive tree. The anchor section exists to surface the most valuable starting points for future readers, not to limit what survives.

### Tier A anchors

- `engines/source/reference/ABD_INTAKE_SPEC.md`
  - `"Important: Count \`PageNumber\` spans, NOT \`PageText\` divs."`
  - `"2. **القسم is special.** It's the only field where the colon is a plain \`:\` character baked into the span text."`
  - `"the book's declared science is an informational prior, not a routing constraint"`

- `engines/source/reference/edge_cases.md`
  - `"Zero data loss — everything the parser can't classify is captured verbatim."`
  - `"A 69% mismatch rate was observed across the original 7-book corpus"`
  - `"Keep-first semantics ... \`أصل التحقيق\` is in an explicit exclusion list"`

- `engines/source/review/OWNER_SANITY_CHECK_ANSWERS.md`
  - `"editors whose name alone increases trust in ANY edition they touch, across all sciences."`
  - `"دار الرسالة and مؤسسة الرسالة are the same entity."`
  - `"دار الكتب العلمية ... mass-producing editions of variable quality."`
  - `"takmila_of"`
  - `"dhayl_of"`

- `engines/source/src/extractors/shamela_html.py`
  - `"حقق ∉ تحقيق, خرج ∉ تخريج, علق ∉ تعليق. Both forms must be listed."`
  - `"The non-greedy (.*?)</div> regex works because the metadata card has NO nested <div> elements (verified across all 2,519 exports)."`
  - `"\\"رواية\\": \\"riwayah\\",  # Hadith transmission/recension (26 books)"`
  - `if "القسم" in label:`

- `engines/source/tests/test_deterministic.py`
  - `"This exact byte sequence must be preserved — no normalization allowed."`
  - `"Muhaqiq and author are NEVER the same person in fixture 04."`
  - `"Fixture 13: Format B layout extracts title from value inside span."`

### Tier B anchors

- `engines/source/LESSONS.md`
  - `"Tests written by the same agent as the code tend to test what the code does, not what the SPEC says."`
  - `"Scholar registry sparseness caused 70% gate_abort rate in Phase C."`
  - `"Consensus module was oversensitive to cosmetic differences"`
  - `"Death dates from single-model inference are unreliable."`

- `engines/source/docs/session5-contracts-audit.md`
  - `"The \`unsure\` → \`elevated\` workflow ... cannot be represented with a boolean \`resolved\`."`
  - `"Validated formula: death_date ≤ 1000 → 0.90; death_date > 1000 → 0.70; no death date → 0.30. Re-verified: 13/13 correct."`

- `engines/source/review/PHASE_A_LESSONS.md`
  - `"if \"القسم\" in label: continue"`
  - `"Two HTML card formats exist:"`
  - ``"`رواية` label (26 books) — architect decision needed on mapping"```

- `engines/source/review/STEP0_RESULTS.md`
  - `"\`normalize_arabic_name\` ... not Arabic commas (،) or other punctuation"`
  - `"Full nasab names: Owner confirmed he wants extensive, detailed full nasab forms (not shortened names)."`

- `engines/source/src/metadata_inference.py`
  - `"When one model provides a death_date and the other says None, the date is higher-risk for hallucination."`

- `engines/source/src/trust_evaluator.py`
  - `"The validated formula ... uses ONLY the death date"`
  - `"The \"prior sources\" check belongs in trust RE-EVALUATION ... not in initial evaluation."`

- `engines/source/tests/test_registries.py`
  - `"Regression: أحمد محمد شاكر was auto-linked to أحمد بن محمد بن حنبل"`
  - `"Corrupt registry + corrupt .bak → RuntimeError (not silent pass)."`

- `engines/source/tests/test_validation.py`
  - `"sharh + is_multi_layer=false + empty layers → warning, NO auto-correct (BUG-05 fix)."`
  - `"is_multi_layer=True + only matn/tahqiq_note → corrected to False, layers cleared."`

### Tier C anchors

- `engines/source/contracts.py`
  - `"This is NOT the LLM identification confidence. Downstream engines must use SourceMetadata.confidence_scores.author"`
  - `"Fields with confidence < 0.70 → needs_review. Fields with confidence < 0.50 → block metadata write"`
  - `"This is the ORIGIN of the metadata chain that flows through the entire pipeline."`

- `engines/source/SPEC.md`
  - `"Muhaqiq (editor) records. Tahqiq editors are scholars in their own right."`
  - `"Disambiguation handling. The most critical disambiguation case is when two different scholars share a commonly used name."`
  - `"The recognized muhaqiqs list: شعيب الأرناؤوط، أحمد شاكر، عبد السلام هارون، عبد الله التركي، محمد فؤاد عبد الباقي، عبد القادر الأرناؤوط، محمد ناصر الدين الألباني."`

- `engines/source/SPEC_CORE.md`
  - `"The source metadata record flows downstream through the entire pipeline — no engine may strip metadata fields (D-023)."`
  - `"There is NO separate \`info.html\` metadata file — metadata is embedded in the first \`PageText\` div of each \`.htm\` file."`
  - `"Frozen file immutability. No enrichment may modify \`frozen_hash\`, \`frozen_path\`, \`frozen_file_hashes\`, or any frozen file content."`

- `engines/source/docs/technology-inventory.md`
  - `"This directly addresses the A3-1 problem: \"النووي\" (1 token: {نووي}) vs \"أبو زكريا يحيى بن شرف النووي\" (5 tokens: {ابو, زكريا, يحيى, شرف, نووي})."`
  - `"Keep the custom approach. The eval_harness implementation is correct for the domain. Neither PyArabic nor CAMeL Tools solves the actual problem (scholarly name identity matching)."`

- `engines/source/review/DOWNSTREAM_CONTRACT_AUDIT.md`
  - `"Correct both downstream SPECs to read from \`library/sources/{source_id}/metadata.json\`"`
  - `"Do NOT expand the registry — that creates redundancy and staleness risk."`

- `engines/source/review/STEP2_EVALUATION.md`
  - `"Decision: KEEP SINGLE-CALL."`
  - `"Decision: COMMAND A (Cohere) + OPUS 4.6 (Anthropic)."`
  - `"Decision: KEEP CURRENT THRESHOLDS (0.70 / 0.50), PROVISIONALLY."`
  - `"Decision: RAISE TO 1000 AH."`
  - `"Mandatory build-phase check ... compute \"at least one right\" on \`author_identification\` alone."`

- `engines/source/review/CORE_VS_DEFERRED.md`
  - `"Core formats: \`shamela_html\`, \`plain_text\` only"`
  - `"Muhaqiq records as scholars | CORE"`
  - `"Format detection and metadata extraction must use pluggable extractor modules"`

- `engines/source/prompts/inference_v1.py`
  - `"Compiler vs. author distinction ... identify the ORIGINAL author, not the compiler."`
  - `"Set confidence to 0.50 for any field you are genuinely uncertain about. Do NOT guess"`
  - `"A تعقبات ... is NOT multi-layer"`
  - `"The output schema section of this file is preserved in full by archiving the entire prompt file, not by the anchor excerpts alone."`

- `engines/source/src/consensus.py`
  - `"Case B: Both say \"new\" → name_sim >= 0.90 AND death dates agree (±10 years or both None) → True"`
  - `CONSERVATIVE_ORDER = ["unknown", "disputed", "traditional", "definitive"]`

- `engines/source/src/validation.py`
  - `"Genre 'hashiyah' requires 3 layers (matn→sharh→hashiyah)"`
  - `"All layer types {layer_types} are tahqiq editorial apparatus (not scholarly commentary)"`
  - `"Death date from single-model inference only ... High risk for hallucination"`

## Execution Notes

- Move files, do not copy them, so the active surface is truly cleared.
- Preserve relative paths under the archive root.
- Write `ARCHIVE_INDEX.md` and `FILE_MANIFEST.md` after the move, using the tier assignments above.
- Do not touch files outside `engines/source/`.
- Stop after the archive-first reset plan is reflected in the tree.
