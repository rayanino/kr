# Session Log — خزانة ريان

## Session 13: Atomization Engine PRECISION
**Date:** 2026-03-06
**Type:** PRECISION
**Focus:** Atomization SPEC audit — machine-readability, defect fixing, contracts synchronization

**Defects Found and Fixed (15):**
1. (CRITICAL) Footnote offset invariant contradiction — §4.A.9 said footnote atom spans are relative to footnote text, but V-2 and §4.A.8 required `atom_text == passage_text[start:end]` for ALL atoms. Fixed: added footnote variant of invariant, new `footnote_source_index` field, updated V-1, V-2, V-4, §3 guarantees, and coverage enforcement.
2. Layer type mapping used "layer_1/layer_2/layer_3/editor" but upstream LayerType enum uses "matn/sharh/hashiyah/tahqiq_note/uncertain". Fixed mapping and added handling for "uncertain" layer type.
3. Rule AB-6 said whitespace doesn't become atoms, but whitespace_separator structural type exists. Resolved contradiction: ordinary whitespace absorbed into preceding atom; explicit dividers ("***") become whitespace_separator atoms.
4. V-1 (exhaustive coverage), V-2 (offset integrity), V-4 (ordering) all updated for footnote atom handling.
5. §4.A.1 pre-screen "Select the appropriate atomization strategy" → specified: select by structural_format match per §4.A.7, calibrate confidence for low-fidelity passages.
6. Coverage enforcement "nearest atom" → deterministic: always the preceding atom.
7. §4.B.1 and §4.B.4 "appropriate relation types" → explicit enum reference.
8. §5 "appropriate review point" → removed vague phrasing.
9. §4.B.3 "deviates significantly" → ">2 standard deviations" (matching contracts.py).
10. §4.A.5 "generic gold examples" → "prose-format gold examples".
11. §4.B.5 Tier 1 word sorting → "Unicode codepoint order" (deterministic, locale-independent).
12. §4.A.9 empty footnote text handling added.
13. Missing error codes added for §4.B.4 (ATOM_ATTRIBUTION_PARSE_FAILURE, ATOM_ATTRIBUTION_LOW_CONFIDENCE) and §4.B.5 (ATOM_FINGERPRINT_HASH_FAILURE, ATOM_FINGERPRINT_EMBEDDING_FAILURE, ATOM_FINGERPRINT_KEY_TERMS_EMPTY) + ATOM_UNKNOWN_LAYER_TYPE.
14. Test cases 11-14 added for attribution detection, fingerprint determinism, fingerprint relevance, and footnote atom integrity.
15. Test cases 1-2 updated to account for footnote atom invariant variant.

**Contracts.py Changes:** Added `footnote_source_index` field to AtomRecord.

**Quality Script:** 41→35 defects (27 high). Remaining are false-positive VAGUE_QUANTIFIER on descriptive text and MISSING_EXAMPLE for worked examples (deferred to implementation prep).

**Decisions:** None requiring owner input.
**Next:** Atomization HARDENING session.

## Session 7 — Normalization Engine HARDENING
**Date:** 2026-03-06
**Type:** HARDENING
**Engine:** Normalization

### What Was Done

Systematic threat enumeration against KNOWLEDGE_INTEGRITY.md for every §4.A processing step. Identified 8 coverage gaps where corruption paths had no detection mechanism. Patched all 8:

1. **Atomic write guarantee (Pass 6).** Added temp-directory + atomic-rename procedure to prevent partial packages on disk. New error code `NORM_WRITE_FAILED`.
2. **Unit index integrity (§5 check #7).** Added validation that unit_index forms contiguous 0-based sequence. New error code `NORM_UNIT_INDEX_VIOLATION`.
3. **Diacritics preservation verification (§5 check #8).** Added character-class comparison between source and output Arabic diacritics for digital-text sources. New error code `NORM_DIACRITICS_DRIFT`.
4. **Format-specific input validation (§5 check #9).** Each normalizer validates input matches expected format before processing. New error code `NORM_NO_TEXT_LAYER`.
5. **Footnote separator absence handling (§4.A.2 Pass 2).** Explicit rule: absent separator → treat entire page as primary text, log info. New error code `NORM_FOOTNOTE_SEPARATOR_ABSENT`.
6. **Image page ordering conflict resolution (§4.A.4).** Defined precedence: filename sort authoritative, OCR page numbers for cross-reference. New error code `NORM_PAGE_ORDER_CONFLICT`.
7. **Tighter coverage check for deterministic sources (§5 check #2).** Shamela/text PDF: exact page count match (minus explicitly skipped pages), not ±10%.
8. **Contracts updated.** FootnoteType enum expanded for §4.B.4 fine-grained types. Added VariantReadingData, TakhrijData, BiographicalNoteData, CorrectionNoteData models.

Added 2 Arabic text examples: §4.B.1 (content-based layer inference in شرح الورقات), §4.B.4 (4-footnote classification from المغني tahqiq edition).

### Quality Metrics
- HIGH defects: 6 → 4 (target: ≤6) ✓
- Creative score: 90/100 maintained ✓
- Arabic examples added: 2 (target: ≥2) ✓
- New error codes: 6
- New §5 validation checks: 3
- SPEC lines: 1013 → 1073

### Decisions
- Atomic write uses temp directory + rename (not file-level locking) — simpler, portable, sufficient for single-writer.
- Diacritics drift check is fatal (not warning) — any diacritic loss is a code bug, not a data quality issue.
- Filename sort is authoritative for image sets over OCR page numbers — captures owner's physical sequencing intent.

### No Domain Questions This Session

## Session 8 — Normalization Engine IMPL_PREP
**Date:** 2026-03-06
**Type:** IMPLEMENTATION_PREP
**Engine:** Normalization

### What Was Done

Prepared the normalization engine directory for Claude Code implementation. This is the last Claude Chat session for the normalization engine.

**Phase 1 — Contract alignment verification:**
- Verified all 16 fields the normalization engine reads from SourceMetadata exist in source contracts.py.
- Verified StructuralFormat enum values match exactly between source and normalization contracts.
- Identified one mapping note: source TextLayer uses string "tahqiq" → normalization LayerType uses "tahqiq_note". Documented in IMPL_BRIEF.

**Phase 2 — Test fixture gap analysis:**
- Existing html_export_minimal fixture uses NON-STANDARD format (div.page) not actual Shamela format (div.PageText). Cannot be used with ABD normalizer code.
- Created new fixture `engines/normalization/tests/fixtures/shamela_ibn_aqil.htm` in REAL Shamela export format: PageText divs, PageHead headers, PageNumber spans, hr footnote separators.
- Fixture covers: multi-page, footnotes (numbered_parens), bold matn signal, HTML-tagged headings, ZWNJ heading, verse detection, Quran citation, diacritics, no-separator page.
- Gold baseline directory created with README documenting what baselines are needed.
- ABD tests (204 test functions) are in archive; equivalent tests needed in new structure.

**Phase 3 — Directory skeleton:**
- Created module stubs with SPEC-referencing docstrings:
  - `src/errors.py` (complete — all 20 error codes, severity mapping, NormalizationError class)
  - `src/normalizers/base.py` (complete — BaseNormalizer interface)
  - `src/dispatcher.py` (stub — normalizer registry + dispatch logic)
  - `src/normalizers/shamela.py` (stub — 6-pass pipeline)
  - `src/validation.py` (stub — 8 validation check functions)
  - `src/writer.py` (stub — atomic write procedure)
  - `src/layer_detector.py` (stub — multi-layer detection)
  - `src/content_flagger.py` (stub — content type flagging)
  - `src/content_census.py` (stub — statistical profiling)
- Created test stubs: `tests/test_kr_output.py` with 30 test methods organized by SPEC §10 categories.

**Phase 4 — Implementation brief:**
- Wrote `engines/normalization/IMPL_BRIEF.md` — 6-step build plan for Claude Code.
- Steps: (1) output schema upgrade + atomic writer, (2) validation framework, (3) footnote classification, (4) multi-layer detection, (5) content flagging, (6) content census.
- Each step specifies: what to do, field mappings, thresholds, test criteria.
- Documents ABD→KR field mapping table, constraints, dependencies, final file layout.

### Quality Metrics
- Contract alignment: ✓ All fields verified
- Test fixture: ✓ Created in real Shamela format (6 pages, covers key scenarios)
- Module stubs: 9 files created (2 complete, 7 stubs with SPEC references)
- Test stubs: 30 test methods across 10 test classes
- IMPL_BRIEF: 6 implementation steps with concrete build criteria

### Decisions
- errors.py and base.py implemented fully (not stubs) since they're pure definitions with no behavioral complexity — saves Claude Code a step.
- New Shamela fixture created rather than fixing html_export_minimal — the existing fixture may be useful for other purposes and shouldn't be changed.
- IMPL_BRIEF uses 6-step incremental build rather than big-bang — each step is independently testable.

### No Domain Questions This Session

---

## Session 9: Passaging Engine CREATIVE
**Date:** 2026-03-06
**Type:** CREATIVE
**Engine:** Passaging (محرك التقطيع)

### What Was Done

**Research phase:**
- Surveyed Arabic NLP text segmentation landscape (ArabicNLP 2024-2025, KITAB project, OpenITI mARkdown)
- Studied KITAB's passim algorithm: 300-word milestones, Smith-Waterman alignment for text reuse detection
- Researched RAG chunking strategies (2024-2025): semantic chunking, adaptive chunking (87% vs 13% accuracy over fixed-size), late chunking, proposition-based chunking
- Examined OpenITI mARkdown structural tagging: `### |` for chapters, `### ||` for sections, paragraph tags, milestone markers

**Key research insight:** Adaptive chunking that respects document structure dramatically outperforms fixed-size and even semantic-only approaches. This validates KR's division-guided approach AND motivates the new content census-driven adaptation capability.

**Creative output — SPEC rewrite (502 → 643 lines):**

1. **§2 input contract updated:** Added content_census and tahqiq_topology from normalization manifest, quality_report for boundary confidence adjustment
2. **§4.A.2 Arabic cross-page joining examples:** Two concrete Arabic examples (mid-word break on المبتدأ, sentence-boundary break), taa marbuta/hamza page boundary handling
3. **§4.A.4 scholarly keyword scan expansion:** Organized 25+ Arabic keywords into 5 categories (ordinal, new-topic, contrastive, evidence, position), with concrete مغني example showing splitting at position boundaries
4. **§4.A.4 Arabic sentence detection specification:** Four-tier priority system (terminal punctuation, paragraph breaks, Quran citation boundaries, long comma-span heuristic), explicit rule that Arabic comma is NOT sentence-terminal
5. **§4.A.4 isnad chain integrity rule:** Pattern-based detection of حدثنا/أخبرنا/أنبأنا chains, never split isnad+matn across passages
6. **§4.A.6 Q&A markers expanded:** Added فأجاب, الجواب:, قيل له:, وسأله; concrete example from مجموع الفتاوى
7. **Arabic word count method specified:** Whitespace tokenization (matching KITAB convention), not morphological tokenization
8. **NEW §4.B.5 — Content Census-Driven Adaptive Passaging:** Uses normalization content census to adapt passage size, splitting thresholds, commentary sensitivity, and footnote adjustment per-source. Concrete formulas with worked examples (شرح ابن عقيل → 643 effective target)
9. **NEW §4.B.6 — Scholarly Argument Boundary Detection:** Pattern-based state machine detecting مسألة → evidence → counter → refutation → conclusion structure. Boundary protection rule (arguments up to 150% hard max preserved intact). Concrete example from المغني
10. **New error codes:** PSG_ARGUMENT_OVERSIZED, PSG_ADAPTATION_FAILED, PSG_ISNAD_SPLIT
11. **New test requirements:** Isnad chain preservation (4 tests), adaptation formulas (4 tests), argument detection (5 tests)
12. **New gold baseline:** Masala-block source for argument boundary verification

### Quality Metrics
- Creative verification score: 90/100 (6 capabilities, 3 named technologies, examples, 0 vague phrases)
- Invention ratio: 89% (32 invention signals, 4 correction signals)
- Assessment: CREATIVE

### Decisions
- Arabic word counting uses whitespace tokenization (not morphological) — matches KITAB/OpenITI convention and how scholars estimate text length
- Isnad chains treated as atomic units — splitting a narration chain is worse than an oversized passage
- Argument preservation can expand passages up to 150% of hard max — a complete argument in one passage is more valuable than two broken halves
- Content census adaptation formulas use conservative multipliers (0.3, 15-20-30%) — aggressive adaptation risks unexpected behavior on edge cases

### No Domain Questions This Session


## Session 10: Passaging Engine PRECISION
**Date:** 2026-03-06
**Type:** PRECISION
**Duration:** ~1 session

### What Was Done
Systematic self-audit of the passaging SPEC against the Perfection Standard. Found and fixed 16 defects:

**Contract alignment (3 fixes):**
- §2 `division_tree` field names mismatched contracts.py (`title`→`heading_text`, `level`→`heading_level`, flat `parent_div_id/child_div_ids`→nested `children`). Added synthetic `div_id` generation rule.
- `digestible` field (not in contracts) replaced with content_flags-based digestibility test throughout.
- §9 CAMeL Tools described as "word counting" but §4.A.4 explicitly uses whitespace tokenization. Fixed §9 to match.

**Ambiguity fixes (5 fixes):**
- LLM boundary confidence: vague "0.6–0.8 range" → fixed 0.7.
- Mixed-format classification: vague "matches Q&A patterns" → explicit priority cascade with thresholds (≥80% verse pages, ≥2 marker detections).
- `quality_report.overall_confidence`: vague "lowers expectations" → concrete per-level behavior (confirmed/high = trust, medium = flag, low = cross-validate with LLM).
- Keyword split selection: no criteria for choosing among multiple candidates → balance + type priority + argument exclusion rules.
- Empty division tree: undefined behavior → flat passaging with synthetic division, §4.B.2 integration.

**Formula verification (3 fixes):**
- §4.B.5 structural depth boundaries: made inclusivity explicit ([2.0, 10.0]).
- §4.B.5 footnote formula: specified which targets affected (`target_high` only), stacking order (multiplicative: term density → footnote), out-of-range clamping.
- §4.B.5 example: footnote density 4.3 was below 5.0 threshold → fixed to 6.2.

**State machine formalization (1 fix):**
- §4.B.6 argument detection: prose description → formal state transition table with 4 states, 14 transitions, nested argument handling (depth tracking, cap at 3).

**Schema completeness (3 fixes):**
- §3 missing fields: added `quality_prediction`, `commentary_alignment`, `adaptive_params`, `argument_structure`, `heading_source`.
- §3 `division_path` referenced undefined `type` field → fixed to `heading_text`/`heading_level`.
- §4.A.8 dictionary entry detection: vague signals → priority cascade with fallback.

**Cross-page joining (1 fix):**
- Rule 1 false positives: word-final forms (`ة`, `ى`, `ا` after letter, `ء`) prevent mid-word join.

### Artifacts Created
- `engines/passaging/contracts.py` — 25 Pydantic models, 285 lines. Validated with Python import + instantiation test.

### Decisions Made
- Passaging engine generates synthetic `div_id` values (not stored in normalization output).
- Whitespace tokenization confirmed as sole word counting method (not CAMeL Tools).
- Argument nesting capped at depth 3.
- Commentary sensitivity now has concrete behavioral definitions (fine/normal/coarse).
- Adaptation stacking order: technical_term_density first, then footnote_factor (multiplicative).

### Quality Metrics
- check_spec_quality.py: 50 flagged items (35 HIGH), mostly false-positive "multiple/many" quantifiers in descriptive context.
- creative_verification.py: 80/100 (6 §4.B capabilities, 3 named technologies). "SECRETARY" flag expected for PRECISION session.
- contracts.py validates successfully with Pydantic.

### Next
Passaging HARDENING session: threat model failure modes, validate error handling completeness, verify state machine has no deadlock states.

## Session 11: Passaging Engine HARDENING
**Date:** 2026-03-06
**Type:** HARDENING
**Focus:** Threat analysis and gap closure for passaging SPEC

### What Was Done
- Analyzed 8 threat vectors against the passaging engine (silent text loss, bad boundary corruption, metadata loss, footnote corruption, argument false positive, adaptation edge case, state machine deadlock, false join)
- Added 4 new self-validation checks (#8 boundary integrity, #9 predecessor/successor linking, #10 author preservation, #11 bidirectional footnote integrity)
- Added 10 new error codes (PSG_ASSEMBLY_QURAN_UNCLOSED, PSG_ASSEMBLY_FOOTNOTE_COLLISION, PSG_ASSEMBLY_LAYER_MISMATCH, PSG_ARGUMENT_NO_SUBBOUNDARY, PSG_VALIDATION_BOUNDARY_MIDSENTENCE, PSG_VALIDATION_LINK_BROKEN, PSG_VALIDATION_AUTHOR_LOST, PSG_VALIDATION_FOOTNOTE_ORPHAN, PSG_VALIDATION_TEXT_LOSS, plus updated severity descriptions)
- Hardened cross-page joining: added tanwin diacritics to word-final forms, added Quran citation bracket tracking at page boundaries
- Completed §4.B.6 state machine: added 2 missing transitions (OPEN+counter-evidence/response → BODY), added explicit "any other text" rows for all states, proved deadlock impossibility, clarified nesting cap behavior
- Added fallback for §4.B.6 oversized arguments with no internal sub-boundaries
- Bounded adaptation formula (clamp technical_term_density to [0.0, 0.5])
- Strengthened text integrity check #4 with character count invariant
- Added §3 guarantee → validation check mapping in §5
- Updated test requirements (12 cross-page tests, 9 self-validation tests, 6 sentence integrity tests)

### Decisions Made
- Author preservation check is FATAL (not warning) — losing an author is an attribution error (threat T-2), too serious for a warning
- Predecessor/successor link check is FATAL — broken links indicate logic errors, not content issues
- Text loss check is FATAL — any character loss during assembly is data corruption
- Boundary mid-sentence check is WARNING — mid-sentence boundaries degrade quality but don't corrupt data

### SPEC Stats
- Before: 704 lines, 7 self-validation checks, ~16 error codes
- After: 731 lines, 11 self-validation checks, ~26 error codes

### Next
Atomization engine CREATIVE session.

## Session 12: Atomization Engine CREATIVE
**Date:** 2026-03-06
**Type:** CREATIVE
**Focus:** Atomization engine SPEC enhancement with 2 new §4.B capabilities

### What Was Done
1. Read all required files: DOMAIN.md, ENTRY_EXAMPLE.md, USER_SCENARIOS.md, passaging SPEC §3, passaging contracts.py, RESOURCES.md
2. Research phase: Arabic discourse segmentation, hadith isnad/matn segmentation (92.5% accuracy with bi-grams), IslamicLegalBench 2026 (67% LLM accuracy on Islamic legal reasoning), KITAB text reuse detection, computational approaches to fiqh classification
3. Designed and fully specified **§4.B.4 — Scholarly Attribution Chain Resolution**: Detects and structures nested attribution patterns within atoms (direct, via_work, school_collective, isnad, anonymous, self, refutation_target). Enables the synthesizer to reconstruct complete scholarly dialogue structure across the corpus.
4. Designed and fully specified **§4.B.5 — Atom-Level Semantic Fingerprinting**: Three-tier fingerprinting (normalized text hash, key term extraction, semantic embedding) enabling downstream cross-source deduplication detection at the finest meaningful granularity. No existing tool does this for Arabic scholarly texts.
5. Created `engines/atomization/contracts.py` with full Pydantic models for: AtomRecord, all sub-models (AnchorSpan, EmbeddedRef, ScholarlyAttribution, etc.), distribution report models, fingerprint manifest models
6. Updated §3 output contract with attribution and fingerprint fields
7. Updated §8 configuration with 8 new parameters for the new capabilities
8. Updated §9 implementation state with new NOT YET IMPLEMENTED entries
9. Updated RESOURCES.md with new research findings

### Decisions Made
- Attribution detection runs as sub-task within existing LLM atomization call (not a separate pass) — marginal cost
- Fingerprinting uses three tiers with increasing cost: Tier 1 (text hash, deterministic), Tier 2 (key terms, part of LLM call), Tier 3 (embeddings, optional/deferred)
- Tier 3 embeddings default to OFF — requires GPU infrastructure
- Attribution produces raw scholar names, NOT canonical IDs — resolution is excerpting engine's responsibility

### Domain Questions for Owner
None this session.
