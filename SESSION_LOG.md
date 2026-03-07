# Session Log — خزانة ريان

## Session: Normalization Engine HARDENING — 2026-03-07
**Type:** HARDENING
**Engine:** Normalization (محرك التطبيع)

**Work completed:**
- 12 adversarial scenarios tested with attack vectors, defenses evaluated, and SPEC fixes applied
- 2 error cascade traces (footnote separator → false scholarly claims; page order → broken passages)
- 6 KNOWLEDGE_INTEGRITY.md invariants verified (all PASS, 1 after fix)
- 3 multi-layer misattribution attack vectors (gradual signal degradation, cross-source fingerprint poisoning, hashiyah triple-layer confusion)
- 2 OCR corruption scenarios (diacritic hallucination, table structure destruction)
- §4.B.8/§4.B.10 interaction verified under 3 test cases (all PASS after fixes)
- Pass 6 processing order verified: no circular dependencies
- All 24 error codes verified with concrete trigger scenarios
- 5 new error codes added: NORM_SUSPICIOUS_PAGEHEAD, NORM_ORDERING_UNCERTAIN, NORM_OCR_DIACRITICS_HALLUCINATION, NORM_TABLE_STRUCTURE_LOST, NORM_OCR_COHERENCE_FAILURE
- 6 self-audit defects found and fixed

**Contract changes (contracts.py):**
- Added `ELABORATION` to `DiscourseSegmentType` (was missing vs SPEC)
- Created `DiscourseDetectionMethod` enum (was untyped string)
- Created `FingerprintReliability` enum (was untyped string)
- Added `model_validator` to `DiscourseFlow` (cycle_complete ↔ missing_elements, segments non-overlapping)
- Added `model_validator` to `DiscourseSegment` (start_char < end_char)
- Added `model_validator` to `LayerFingerprint` (insufficient_data threshold)
- Added `cycle_truncated_by_structure` field to `DiscourseFlow`
- Added `SecondaryFootnoteType` model and `secondary_types` field to `Footnote`

**SPEC changes:**
- §4.A.2: Added interrupted write recovery rule
- §4.A.4: Added semantic confusion hazard rule, OCR diacritics hallucination check
- §4.A.4d: Added embedded scholarly quotation detection for owner content
- §4.A.5: Added numeric threshold (0.50) for conservative default; added bold-for-emphasis disambiguation; added hashiyah quotation detection (step 7)
- §4.B.4: Added mixed-type footnote rule with secondary_types
- §4.B.8: Added signal priority rule (headings > argument flow > punctuation)
- §4.B.8/§4.B.10: Added reverse interaction rule with cycle_truncated_by_structure
- §4.B.9: Added inversion detection thresholds, per-segment fingerprint option, minimum-sources rule for cross-source comparison
- §5: Added checks 13 (OCR coherence) and 14 (OCR diacritics hallucination)
- §7: Added 5 new error codes; upgraded NORM_FOOTNOTE_SEPARATOR_ABSENT severity for tahqiq editions
- Appendix A: Full hardening analysis (adversarial scenarios, cascades, invariants, attack vectors)

**Decisions made:**
- Continuity signal priority: heading detection always overrides punctuation analysis, even for low-confidence headings
- Cross-source fingerprint comparison requires ≥2 independent sources before baselines become authoritative
- Mixed-type footnotes classified by primary content type with secondary types recorded separately
- Per-segment fingerprinting enabled by default for sources with >50 pages (configurable)
- OCR semantic confusion flagged but never auto-corrected

**Quality metrics:**
- check_spec_quality.py: 0 HIGH defects in SPEC proper (§1-§10); 6 HIGH in appendix (narrative prose, not binding rules)
- All Pydantic validators tested and passing
- 24 error codes with concrete trigger scenarios verified

## Session: Normalization Engine PRECISION — 2026-03-07
**Type:** PRECISION
**Engine:** Normalization (محرك التطبيع)
**SPEC:** engines/normalization/SPEC.md (1418L → 1690L)
**Contracts:** engines/normalization/contracts.py updated

### What Was Done
1. **Resolved all 4 HIGH defects** (MISSING_EXAMPLE): Added worked examples with Arabic text to §4.A.3 (PDF text normalizer), §4.A.4 (scanned PDF/iPhone OCR), §4.A.7 (page boundary preservation with non-sequential numbering), §4.B.2 (Q&A format auto-detection in مجموع الفتاوى), §4.B.3 (dual-OCR character-level fidelity mapping).
2. **Added 4 normalizer behavioral outlines:** §4.A.4a (EPUB), §4.A.4b (Word doc), §4.A.4c (plain text), §4.A.4d (owner content). Each defines key behavioral rules, input/output expectations, and [NOT YET IMPLEMENTED] status.
3. **Added `layout_detected` to HeadingDetectionMethod enum** — PDF and EPUB headings detected by layout analysis had no applicable enum value.
4. **Added heading inclusion rule to §4.A.6** — explicit distinction: Shamela PageHead excluded from primary_text (navigation metadata), PDF/EPUB/other headings included (part of author's text).
5. **Added §5 validation checks 10-12** for §4.B.8 (boundary continuity consistency), §4.B.10 (discourse flow consistency), §4.B.9 (layer fingerprint plausibility).
6. **Added 4 new error codes** to §7: `NORM_CONTINUITY_INCONSISTENT`, `NORM_DISCOURSE_INCONSISTENT`, `NORM_FINGERPRINT_INVALID`, `NORM_ORPHAN_FOOTNOTE_REF`.
7. **Clarified orphan footnote reference handling** in §5 check 6: orphan markers preserved as literal text, not converted to universal format.
8. **Added explicit §4.B processing order to Pass 6** with 11 dependency-ordered steps + cross-validation rule for §4.B.8/§4.B.10 consistency.
9. **Updated contracts.py** with 7 new Pydantic models: `BoundaryContinuity`, `DiscourseFlow`, `DiscourseSegment`, `LayerFingerprint`, `SentenceLengthStats`, plus enums. Added `boundary_continuity` and `discourse_flow` to `ContentUnit`, `layer_fingerprints` and `discourse_flow_summary` to `NormalizedManifest`.

### Self-Audit (5 defects found and fixed)
1. **§3 heading_detection_method enum** (Criterion #1 Ambiguity): No value for PDF/Docling layout-based heading detection → added `layout_detected`.
2. **§5 validation gaps** (Criterion #10 Completeness): No validation for §4.B.8-10 output fields → added checks 10-12.
3. **Orphan footnote markers** (Criterion #10 Completeness): Undefined behavior for markers without matching footnotes → defined explicit handling and error code.
4. **§4.B.8/§4.B.10 interaction** (Criterion #14 Both-sides integration): No cross-validation rule for consistency → added step 9 in Pass 6.
5. **§4.A.3 example error** (Criterion #8 Accurate state): Example incorrectly used `html_tagged` for PDF heading → fixed to `layout_detected`.

### Quality Metrics
- `check_spec_quality.py`: 0 HIGH defects (was 4), 1 medium, 1 low
- `creative_verification.py`: §4.B score 90/100
- Contracts syntax: valid Python

### No Domain Questions

## Session: Source Engine HARDENING — 2026-03-07
**Type:** HARDENING
**Engine:** Source (محرك المصادر)

**What was done:**
- Verified all 6 KNOWLEDGE_INTEGRITY.md invariants against every §4.A and §4.B rule (full matrix in Appendix A.3)
- Tested 12 adversarial scenarios with concrete corruption paths, evaluated existing defenses, and applied fixes for gaps found
- Traced 2 error cascades end-to-end (wrong author → corrupted synthesis; corrupt external data → poisoned genealogy)
- All 4 external data integration points (OpenITI, KITAB, Usul-Data, Wikidata) verified with corruption defenses

**Fixes applied (SPEC inline + Appendix A):**
1. Registry file locking for concurrent intake atomicity (§4.A.2 Step 7)
2. Freeze cleanup failure handling — SRC_FREEZE_CLEANUP_FAILED + CORRUPT_FREEZE marker (§4.A.2 Step 6)
3. Orphaned staging lock cleanup on startup (§4.A.2)
4. Enrichment invariant #8: re-processing depth limit to prevent write-back loops (§2)
5. Enrichment invariant #9: verification_context for critical field updates (§2)
6. LLM-only genealogy confidence cap at 0.70 + link_provenance tracking (§4.B.7)
7. Wikidata known-works zero-overlap detection (§4.B.8)
8. Edition comparison alignment sufficiency threshold at 20% (§4.B.6)
9. OpenITI metadata integrity verification (spot-checks, SHA-256) (§4.B.1)
10. Author-science mismatch detection in consistency cross-check (§5)
11. Trust re-evaluation trigger on enrichment of trust-relevant fields (§4.A.8)
12. Scholar data_provenance_score field for provenance quality tracking (§4.A.5)

**Contracts.py changes:**
- Added 3 error codes: FREEZE_CLEANUP_FAILED, OPENITI_CACHE_CORRUPT, COMPARISON_INCONCLUSIVE
- Added data_provenance_score to ScholarAuthorityRecord
- Added verification_context to EnrichmentRequest
- Made EditionComparisonSummary.preferred_edition_recommendation Optional
- Added link_provenance to GenealogyMetadata

**Quality metrics:**
- check_spec_quality.py: 0 HIGH in SPEC proper (3 false positives in appendix narrative)
- 12 adversarial scenarios documented (requirement: ≥10)
- 2 error cascades traced (requirement: ≥2)
- All 6 invariants verified (requirement: all)

**No domain questions for owner.**

## Session: Source Engine PRECISION — 2026-03-07
**Type:** PRECISION
**Engine:** Source (محرك المصادر)

**What was done:**
- Fixed all 14 HIGH-severity defects from `check_spec_quality.py` (12 VAGUE_QUANTIFIER, 4 UNVALIDATED_WRITE — final count 0 HIGH)
- Added 6 missing error codes to §7 error taxonomy (SRC_KITAB_CACHE_MISSING, SRC_KITAB_CACHE_CORRUPT, SRC_USUL_DATA_MISSING, SRC_WIKIDATA_TIMEOUT, SRC_COMPARISON_DEFERRED, and aligned naming)
- Added 7 new §9 implementation gaps for §4.B capabilities (items 13-18 + KITAB/genealogy)
- Updated contracts.py: added 5 new ErrorCode enum values, added difficulty_prediction and tahqiq_fingerprint fields to SourceMetadata, added cross_validation field to ScholarAuthorityRecord, fixed DeathDateAgreement confidence_boost cap (0.20→0.15 to match SPEC)

**Self-audit defects found and fixed (4):**
1. §4.B.9 Signal 6 overlap: page count and volume count rules could both apply — added max() precedence rule
2. §4.B.9 Signal 2 incomplete: only 8 of 18 Genre values had difficulty scores — added all 18
3. §4.B.10 footnote entropy normalization unspecified — added log2(vocabulary_size) normalization method
4. contracts.py DeathDateAgreement.confidence_boost cap (0.20) contradicted SPEC (0.15) — aligned to 0.15

**Decisions made:** None requiring owner input.
**Domain questions:** None.

---


## Session: Synthesis Engine HARDENING — 2026-03-06
**Type:** HARDENING
**Engine:** Synthesis (محرك التوليف)

### What Was Done
- **Contract verification (§2 vs taxonomy §3):** Field-by-field match. Found `school_confidence` missing from synthesis input contract — fixed. Documented `primary_text` implicit preservation. Verified all 7 required and 8 expected fields match.
- **Adversarial test scenarios designed (10 total):**
  - 3 attribution-first pipeline scenarios: low self-containment (vacuous entailment attack), metadata-vs-text contradiction (multi-layer misattribution), self-reinforcing hallucination (same-provider parametric knowledge bias)
  - 7 per-threat scenarios (T-1 through T-7): diacritic corruption, multi-layer misattribution, closely related topic misplacement, forward-reference excerpt, plausible wrong death date, misclassified source type, near-identical editions
- **Error cascade analysis (2 chains):**
  - Cascade 1: Metadata resolution failure → unattributed excerpt → lost unique position. Found residual gap: no alert when unattributed excerpt holds a unique position. Fixed with escalation rule.
  - Cascade 2: Wrong duplicate cluster → merged distinct positions → silently lost position. Found residual gap: no defense against incorrect upstream clustering for different-author excerpts. Fixed with duplicate cluster verification.
- **Self-audit (5 defects found and fixed):**
  1. `school_confidence` missing from §2.1 → added with handling rule (< 0.5 routes to inference path)
  2. Khilaf classification failure unhandled → added Instructor failure recovery and low-confidence handling
  3. Same-provider entailment verification → mandated cross-provider model for Step 4 to prevent self-reinforcing hallucination. Added `entailment_model` config parameter.
  4. `consensus_strength` missing from §3.2 schema → added to content structure definition
  5. Vacuous entailment undefended → added semantic similarity check (< 0.3 triggers rewrite)
- **Error code reachability:** All 22 error codes verified reachable from §4 processing rules. No unreachable codes found. No processing paths without error coverage.
- **Quality script:** 14 defects reported, all 6 HIGH are confirmed false positives (same patterns as PRECISION session: "how many" question phrase, "topic-appropriate" compound adjective, UNVALIDATED_WRITE false positives on reads/validations/test descriptions).
- **T-5 threat mapping updated** to reflect cross-provider entailment and vacuous entailment defense.

### Decisions Made
- Entailment verification MUST use a different provider from the generator (prevents self-reinforcing hallucination)
- School_confidence < 0.5 triggers inference path rather than direct partitioning
- Duplicate clusters are verified for position agreement before acceptance
- Unattributed excerpts with unique positions escalate to human gate

### Owner Questions
- None new (API keys still pending, not blocking)

---

## Session: Synthesis Engine PRECISION — 2026-03-06
**Type:** PRECISION
**Engine:** Synthesis (محرك التوليف)
**SPEC:** `engines/synthesis/SPEC.md` (659 → 859 lines, +200)
**Contracts:** `engines/synthesis/contracts.py` (539 → 565 lines, +26)

### What Was Done
1. **Fixed all genuine high-severity defects (20 → 0).** Replaced 10 vague quantifiers ("multiple" → specific counts, "many" → bounded ranges). Fixed 3 unvalidated write warnings by adding pre-write validation to §4.A.6, consensus output in §4.B.1, and gap note references in §4.B.3.
2. **Added 9 worked examples with Arabic text.** §4.A.1 (pipeline overview with nahw leaf), §4.A.5 (integrity verification with fiqh leaf), §4.A.6 (finalization with version diff), §4.A.8 (diagnostic entry for riba topic), §4.A.9 (per-science hooks: fiqh vs tajwid), §4.A.10 (cross-science nahw↔fiqh), §4.A.11 (ellipsis expansion at 3 levels), §4.B.5 (khilaf disambiguation for المبتدأ definitions), §4.B.6 (Socratic self-verification catching coherence defect).
3. **Added 3 exact prompt templates in Arabic.** Position identification (§4.A.3 Step 1), source span selection (§4.A.4.1 Step 2), entailment verification (§4.A.4.1 Step 4). All include system prompt, user prompt, and examples.
4. **Added §5.4 threat mapping.** All 7 KNOWLEDGE_INTEGRITY.md threats (T-1 through T-7) mapped to synthesis-specific vectors with prevention strategies and residual risk assessments.
5. **Added 8 new error codes to §7.** SYNTH_PREWRITE_VALIDATION_FAILED, SYNTH_CONSENSUS_VALIDATION_FAILED, SYNTH_INVALID_WORK_REFERENCE, SYNTH_ENTAILMENT_FAILED, SYNTH_NO_GROUNDED_CLAIMS, SYNTH_LANDSCAPE_MISMATCH, SYNTH_INSTRUCTOR_PARSE_FAILED, SYNTH_POSITION_COUNT_ZERO.
6. **Aligned contracts.py with SPEC.** Added `analytical_layer`, `critical_analysis`, `khilaf_analysis` fields to `EntryContent`. Added `ChangeSummary` Pydantic model matching §3.4 structured change summary schema. Updated `EntryVersionRecord` to use structured `ChangeSummary`.
7. **Updated §9** with accurate contracts alignment notes.

### Self-Audit (4 defects found and fixed)

**Defect 1 (Structural — Criterion #3 No Contradictions).** §3.2 schema listed 10 content fields but `EntryContent` in contracts.py had only 8 — missing `analytical_layer`, `critical_analysis`, `khilaf_analysis`. These fields are referenced extensively in §4.A.4.2 and §4.A.5. **Fix:** Added all 3 fields to contracts.py with descriptions matching SPEC usage.

**Defect 2 (Completeness — Criterion #11 Exhaustive Error Handling).** §4.A.4.1 Step 4 describes entailment failure but no error code existed for it. §4.B.1 consensus validation failure had no error code. §4.A.6 pre-write validation failure had no error code. **Fix:** Added SYNTH_ENTAILMENT_FAILED, SYNTH_CONSENSUS_VALIDATION_FAILED, SYNTH_PREWRITE_VALIDATION_FAILED, and 5 more error codes.

**Defect 3 (Design — Criterion #21 Scholarly Integrity).** §5 had no systematic mapping of KNOWLEDGE_INTEGRITY.md threats to synthesis-specific vectors. The taxonomy SPEC had a thorough §5.4 threat mapping; the synthesis SPEC — as the pipeline's terminal consumer where all upstream errors surface — needed one even more. **Fix:** Added §5.4 with all 7 threats mapped, including prevention strategies and residual risk.

**Defect 4 (Communication — Criterion #8 Accurate State).** §9 said "All four §4.B transformative capabilities" but there are 6. §3.4 defines a structured change summary schema but contracts.py had only a string field. **Fix:** Updated §9 to say "All 6 §4.B transformative capabilities." Added `ChangeSummary` Pydantic model to contracts.py.

### False Positives in Quality Script (5)
- L 491: "how many" in "how many sources hold each position" — question phrase, not vague quantifier
- L 625: "appropriate" in "topic-appropriate" — compound adjective, specific in context
- L 384: UNVALIDATED_WRITE — validation text is on the same line; script only checks subsequent lines
- L 495: UNVALIDATED_WRITE — describes content generation, not a library write
- L 535: UNVALIDATED_WRITE — describes a registry read, not a write

### Decisions Made
- **Prompt templates in Arabic:** The 3 prompt templates use Arabic system prompts because the LLM processes Arabic text and Arabic scholarly terminology. English system prompts would require unnecessary translation overhead and risk terminology mismatches.
- **`ChangeSummary` as structured model:** Changed from a free-text `change_summary: str` to a Pydantic model with `positions_added`, `positions_removed`, `positions_modified` fields. This enables the scholar interface to present structured diffs without parsing prose.

### No Domain Questions for Owner

## Session: Taxonomy Engine HARDENING — 2026-03-06
**Type:** HARDENING
**Engine:** Taxonomy (محرك التصنيف)

**What was done:**
- Mapped all 7 KNOWLEDGE_INTEGRITY.md threats (T-1 through T-7) to taxonomy-specific vectors and prevention mechanisms (new §5.4)
- Wrote error cascade analysis for 5 failure propagation paths: wrong science_id, corrupted tree semantics, mid-evolution crash, systematic LLM bias, embedding model degradation (new §5.5)
- Added 6 adversarial test cases to §10.5: systematic placement bias, evolution orphan attack, mid-migration crash recovery, rollback with post-evolution excerpts, duplicate human gate decision, Arabic text fidelity
- Self-audit found and fixed 6 structural/semantic defects:
  1. Leaf embedding cache lifecycle unspecified → added compute/update/staleness rules
  2. Post-write text fidelity check missing from §5.1 → added byte-for-byte primary_text verification
  3. Rollback failure scenario missing → added TAX_ROLLBACK_FAILURE with diagnostic report + manual recovery path
  4. Human gate decision idempotency missing → added duplicate detection via gate_log.jsonl
  5. Pre-approval "consecutive" scope ambiguous → clarified as per source-science pair
  6. "reviewed" status referenced in 3 places (doesn't exist in taxonomy contract) → fixed to "draft" + re-placement queue
- Added WAL (write-ahead log) mechanism for crash-safe evolution application
- Added 4 new error codes: TAX_METADATA_INCONSISTENCY, TAX_LOW_SELF_CONTAINMENT, TAX_EMBEDDING_DEGRADED, TAX_ROLLBACK_FAILURE

**Quality metrics:**
- `check_spec_quality.py`: 0 high (maintained), 6 medium (false-positive concept terms), 2 low
- `creative_verification.py`: 90/100 (maintained). SECRETARY flag expected — this is a HARDENING session.
- SPEC grew from 868 to 946 lines

**Decisions made:**
- WAL for evolution: write-ahead log records all intended file operations before execution, enabling recovery from any mid-point failure
- Rollback failure halts the science entirely rather than attempting automated recovery — file system may be inconsistent, manual intervention is safer
- Post-write fidelity check compares primary_text byte-for-byte (not Unicode-normalized) to catch any serialization corruption
- TAX_METADATA_INCONSISTENCY is a warning (not fatal) because the taxonomy engine cannot independently verify attribution — it flags for human review

**No domain questions for owner.**

## Session: Taxonomy Engine CREATIVE — 2026-03-06
**Type:** CREATIVE
**Engine:** Taxonomy (محرك التصنيف)

**What was done:**
- Read full taxonomy SPEC (562 lines), ENTRY_EXAMPLE.md, USER_SCENARIOS.md
- Researched: Arabic NLP text classification, Islamic knowledge ontologies, scholarly knowledge graphs, ikhtilaf mapping, GRAPHYP dispute detection
- Designed and wrote 3 new transformative capabilities (§4.B.4–§4.B.6):
  - §4.B.4: Scholarly Disagreement Topology — maps consensus/disagreement patterns per leaf, branch, science; detects recurring axes with root cause hypotheses
  - §4.B.5: Proactive Tree Evolution Prediction — predicts tree changes from source TOC alignment before excerpting begins
  - §4.B.6: Scholarly Landscape Reconstruction — pre-computes chronological timeline, influence graphs, discourse transitions, evidence evolution per leaf
- Created `engines/taxonomy/contracts.py` with Pydantic models for §2/§3 input/output + all §4.B outputs
- Updated §9 implementation state table
- Recorded 8 defects for PRECISION session

**Quality metrics:**
- `creative_verification.py`: 90/100 (up from 75)
- `check_spec_quality.py`: 47 defects (39 pre-existing + 8 new — all deferred to PRECISION session)
- SPEC grew from 562 to 691 lines

**Decisions made:**
- §4.B.4 disagreement analysis classifies into 5 categories (ijma, khilaf, apparent consensus, intra-school, insufficient) — not binary agree/disagree
- §4.B.5 proactive prediction threshold: 3+ source sections mapping to same leaf (not 2, because 2 may be definition + examples of same sub-topic)
- §4.B.6 landscape confidence formula: min(source_diversity, temporal_span, school_coverage) — conservative, because the weakest dimension limits narrative quality

**No domain questions for owner.**

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

---

## Session: Atomization HARDENING
**Date:** 2026-03-06
**Type:** HARDENING
**Engine:** Atomization

### What Was Done
1. Systematic threat analysis against KNOWLEDGE_INTEGRITY.md — all 7 threats (T-1 through T-7) checked against atomization
2. **9 hardening defects found and fixed:**
   - H-1: V-2 hard failure vs "best available" contradiction — clarified: V-2 failure excludes the passage entirely (no corrupt atoms written); V-1 failure produces synthetic gap-marker atoms
   - H-2: Coverage enforcement creating invalid atoms — fixed: coverage gap repair now updates BOTH anchor_span AND atom_text together to maintain offset integrity invariant
   - H-3: Heading atom offset ambiguity — heading_text is separate from passage_text; defined heading-specific offset invariant (atom_text == heading_text[start:end]), excluded heading atoms from V-1 coverage and V-2 passage_text checks
   - H-4: No word-boundary check — added V-8 word boundary integrity validation (soft failure with mid_word_boundary review flag)
   - H-5: Unicode normalization form unspecified — added NFC precondition to input validation with safety-net normalization
   - H-6: Quran hard constraint vs scholarly_function override tension — clarified two-level constraint system: embedded_ref is hard (text IS Quran), scholarly_function is soft (LLM may override evidence_quran)
   - H-7: attributions null vs empty semantics — clarified: null = feature disabled, [] = enabled but nothing found
   - H-8: Bonded cluster spanning layer boundary — special handling: attribute to FIRST layer segment (not majority), double review flags (ambiguous_layer + possible_misattribution)
   - H-9: text_layers partial gap — explicit handling: treated identically to full gap with conservative matn default
3. 11 new test cases added to §10 (tests 15-25) covering all hardening defects plus NEXT.md edge cases
4. 2 new review flag values added: mid_word_boundary, coverage_gap_unresolved
5. contracts.py updated: attribution null/empty semantics, review_flags documentation
6. All 7 NEXT.md threat scenarios traced through the complete path (input → processing → validation → error handling → output)

### Decisions Made
- V-2 (offset integrity) failure is truly blocking: passage excluded entirely rather than writing corrupt atoms. Rationale: corrupt offsets → corrupt excerpts → T-1 silent text corruption. An excluded passage with a visible error is infinitely better than a silently corrupt one.
- V-1 (coverage) failure produces synthetic whitespace_separator atoms to mark gaps, rather than excluding the passage. Rationale: partial atomization with visible gaps preserves the LLM's work on atoms it DID produce correctly.
- Bonded clusters spanning layer boundaries are attributed to the FIRST layer segment (not majority). Rationale: in Arabic scholarly convention, the introducing voice determines attribution ("قال المصنف" + quoted text = the quoted text belongs to the introduced author, regardless of which layer occupies more characters).

### Domain Questions for Owner
None this session.

## Session: Excerpting CREATIVE — 2026-03-06

**Type:** CREATIVE
**Engine:** Excerpting (محرك الاقتطاف)
**Duration:** Single session

### What Was Done

1. **Deep web research** (8 searches across 5 topic areas):
   - Islamic text extraction tools: Shamela, Turath, Usul.ai, OpenITI/KITAB passim text reuse detection
   - LLM accuracy: IslamicLegalBench (Feb 2026) — best model 68% correct, 21% hallucination
   - Cross-tradition tools: Sefaria (Talmud cross-reference mapping), ChavrutAI
   - Argument mining: Legal argument mining (ECHR 15K spans), ArgMining 2024-2025 workshops
   - Arabic NLP: FiqhQA school-specific evaluation, Aftina RAG system

2. **Enhanced §4.B with 5 transformative capabilities** (replacing 3 earlier capabilities):
   - §4.B.1 — **Argumentative Discourse Mapping**: Detects the مسألة→أقوال→أدلة→ترجيح pattern. No existing tool does this for Islamic texts. Informed by legal argument mining research.
   - §4.B.2 — **Cross-Source Semantic Deduplication**: Excerpt-level dedup using atomization fingerprints + embeddings. Inspired by KITAB's passim but semantic, not just verbatim.
   - §4.B.3 — **Scholarly Argument Completeness Analysis**: Detects incomplete arguments via Arabic enumeration/continuation markers. Enhanced with passaging error feedback.
   - §4.B.4 — **Cross-Excerpt Scholarly Dialogue Detection**: Detects dialogue across sources using evidence comparison + chronological ordering + explicit citation check.
   - §4.B.5 — **Self-Containment Repair Suggestions**: Generates actionable repair paths including generated context notes (marked analytical).

3. **Created `contracts.py`** (389 lines): Complete Pydantic models for the excerpt stream, including all §4.B output types.

4. **Added 3 new review flags** for §4.B capabilities: `cross_source_duplicate`, `argument_incomplete`, `passaging_boundary_suspect`.

### Self-Audit Results

**Defect 1 (Completeness — Criterion #10):** §3 review_flags list did not include flags for new §4.B capabilities. An implementer would not know to add these flags when implementing §4.B.2, §4.B.3. **Fixed:** Added `cross_source_duplicate`, `argument_incomplete`, `passaging_boundary_suspect` to the review_flags enumeration.

**Defect 2 (Structural — Criterion #1):** §4.B.1 lists 9 argument roles but does not specify what happens when the LLM classifies as `mixed`. The implementer needs to know: does `mixed` trigger splitting? Is `mixed` acceptable? **Fix needed in PRECISION:** Add explicit handling rule for `mixed` argument_role.

**Defect 3 (Design — Criterion #16):** §4.B.2 defines a 3-stage deduplication pipeline (hash pre-filter → embedding → LLM judgment) but does not specify the embedding model. The atomization SPEC references sentence-transformers but doesn't specify which model or dimension. **Fix needed in PRECISION:** Coordinate embedding model choice with atomization §4.B.5.

**Defect 4 (Completeness — Criterion #11):** §4.B.4 says "Only active during incremental processing, not during initial bulk loading" but does not specify what happens to the `dialogue_links` field during bulk loading — is it null? Empty array? This matters for downstream consumers. **Fix needed in PRECISION:** Specify explicitly.

### Decisions Made

- **D-041: Argumentative discourse roles are per-science.** The argument role vocabulary is the same across all sciences but the expected distribution differs (fiqh uses full mas'ala sequence; tajwid uses almost exclusively definition+example). Per-science calibration is a configuration hook, not a separate code path.
- **D-042: Cross-source deduplication runs post-excerpt, not inline.** During bulk loading, dedup runs as batch after all sources are excerpted. During incremental processing, dedup runs per-excerpt at placement time.
- **D-043: Argument completeness feeds back to passaging engine.** When §4.B.3 detects an argument continuation across a passage boundary, it produces a feedback record for the passaging engine. This is a new inter-engine communication channel.

### Metrics

- SPEC: 559 → 660 lines (+101 lines, all in §4.B)
- contracts.py: 0 → 389 lines (new file)
- §4.B capabilities: 3 → 5
- check_spec_quality.py: ~25 VAGUE_QUANTIFIER warnings (expected, to be fixed in PRECISION)
- creative_verification.py: §4.B score 90/100

### Domain Questions for Owner

None this session.

## Session: Excerpting Engine CREATIVE
**Date:** 2026-03-06
**Type:** CREATIVE
**Engine:** Excerpting (محرك الاقتطاف)

### What Was Done
- Deep domain research: Talmud tools (DICTA, ChavrutAI), argumentation mining (RST, GNN), KITAB/OpenITI/passim, Arabic NLP 2025-2026, Islamic DH landscape
- Added §4.B.4: Mas'ala Boundary Detection and Issue Formulation
- Added §4.B.5: Evidence Chain Reconstruction
- Added §4.B.6: Cross-Source Textual Resonance Detection
- Added §4.A.7: Verse-Format (نظم) Excerpt Handling
- Wrote contracts.py (459 lines, 30+ Pydantic models)
- Updated §3 output contract and D-023 metadata pass-through

### Decisions Made
- §4.B.4 uses two-stage process: mas'ala detection then issue formulation with masala_id for cross-source grouping
- §4.B.5 models Islamic argument types explicitly (textual, analogical, consensus_based, rational, presumptive)
- §4.B.6 uses three tiers applied sequentially for cost management
- Verse-format excerpts allow single-verse self-containment

### Owner Questions
- None new

---

## Session 2026-03-06 (B)

**Type:** PRECISION
**Engine:** Excerpting (محرك الاقتطاف)

### What Was Done
- Resolved all 28 check_spec_quality.py defects → 0 remaining
  - 21 vague quantifiers: "multiple" → "two or more", "some" → specific language, "etc." → explicit enumeration
  - 6 missing examples: added worked examples with Arabic text to §4.A.2–§4.A.7
  - 1 unbounded: "sufficient" → explicit field list
- Fixed duplicate §4.B numbering (CREATIVE session created two §4.B.4 and two §4.B.5):
  - Dialogue Detection: §4.B.4 → §4.B.6
  - Repair Suggestions: §4.B.5 → §4.B.7
  - Resonance Detection: §4.B.6 → §4.B.8
  - All cross-references updated in both SPEC.md and contracts.py
- Synced contracts.py with §3:
  - Added 4 missing fields: verse_numbers, masala_analysis, evidence_chain, resonance_links
  - Added 8 new enums: MasalaExcerptType, MasalaScope, EvidenceLinkType, LogicalStructure, IslamicArgumentType, ResonanceTier, ResonanceType, ChronologicalDirection
  - Added 6 new sub-models: VerseNumbers, MasalaAnalysis, EvidenceChainClaim, EvidenceLink, EvidenceChain, ResonanceLink
  - Field count: 43 in both SPEC and contracts (exact match)
- Self-audit: 4 structural defects found and fixed:
  1. "Optionally" in derived_normalized_text → always strip diacritics
  2. Consensus "for verified sources" contradicted §6 → removed qualifier
  3. Single-atom/heading-only passages unhandled → added explicit edge case rules + EXCERPT_HEADING_ONLY_PASSAGE error code
  4. Dialogue links not bidirectional → added reciprocal update rule

### Decisions Made
- §4.B numbering is now §4.B.1–§4.B.8 (non-contiguous in file, but unique)
- Diacritics are ALWAYS stripped in derived_normalized_text (not optional)
- Consensus is used for ALL self-containment evaluations (no source quality restriction)
- Heading-only passages produce 0 excerpts (not an error)

### Owner Questions
- None new

---

## Session: Excerpting Engine HARDENING
**Date:** 2026-03-06
**Type:** HARDENING
**Engine:** Excerpting

### What Was Done
- Mapped all 7 KNOWLEDGE_INTEGRITY.md threats (T-1 through T-7) to excerpting SPEC prevention mechanisms
- Found and fixed 6 defects:
  1. §3/§4.B.3 mismatch: `argument_completeness` field description in §3 omitted `continuation_detected` and `continuation_passage_id` fields that §4.B.3 defines
  2. Whitespace_separator atom coverage ambiguity: §3 guarantee and V-3 said "every non-heading atom" — now explicitly excludes whitespace_separator atoms
  3. Source metadata cross-validation gap: no mechanism detected when source-level metadata (school tag) contradicted textual evidence — added Layer 2 checks for school mismatch (≥30% threshold) and layer distribution plausibility
  4. Bidirectional update error handling (§4.B.6): no error handling for failure during reciprocal dialogue link updates — added atomic rollback, retry queue with schema validation
  5. Batch post-processing partial failure (§4.B.2): no behavior defined for partial failure of batch deduplication — added checkpoint/resume, null vs. empty list semantics
  6. Upstream layer error cascade: if all atoms have WRONG source_layer (atomization error), excerpting produced incorrect primary_author_id with no detection — added EXCERPT_LAYER_DISTRIBUTION_UNIFORM warning
- Added 6 adversarial test cases to §10:
  - ADV-DECONTEXT-1: Nested quotation chain (Scholar A reports B's report of C's position)
  - ADV-DECONTEXT-2: Refutation split across passage boundary
  - ADV-DECONTEXT-3: Conditional agreement ("وهذا القول حسن لولا...")
  - ADV-LAYER-1: Editor footnote corrects author
  - ADV-LAYER-2: Three-layer hashiyah attribution chain
  - ADV-EVIDENCE-1: Hadith grading silent drop path verification
- Added 4 new error codes to §7
- check_spec_quality.py: 0 defects (maintained from PRECISION session)

### Decisions Made
- Whitespace_separator atoms are excluded from excerpt assignment and V-3 coverage checks (they carry no scholarly content)
- Source metadata cross-validation uses 30% threshold for school mismatch detection (below this, legitimate presentation of other schools' views is common)
- Bidirectional dialogue link updates require atomic rollback on partial failure (unidirectional links are worse than no links)
- Batch deduplication uses checkpoint/resume and distinguishes null (not yet run) from empty list (run, no duplicates)

### Owner Questions
- None new

---

## Session: 2026-03-06

**Type:** PRECISION
**Engine:** Taxonomy

### What Was Done
- Fixed 47→0 high-severity defects from `check_spec_quality.py`:
  - 28 VAGUE_QUANTIFIER fixes: replaced every "multiple", "many", "some" with specific counts (2+, 3+, 5+, ≥50%, etc.)
  - 1 VAGUE_APPROPRIATE fix: "appropriately granular" → "finer granularity than the source's chapter divisions"
  - 1 HANDWAVE_LLM fix: §4.B.4 Category 2 now specifies model (claude-sonnet + gpt-4o consensus), Instructor, structured output schema
  - 1 MISSING_THRESHOLD fix: "low score" → "scored < 0.4"
  - 1 UNBOUNDED_ETC fix: enumerated all 8 dependent leaves instead of "etc."
  - 6 additional medium terms fixed: "sufficient" → "meets the quality bar", "some sciences" → specific with configurable multiplier
- Added 12 concrete examples with real Arabic content:
  - §4.A.1: 2 placement decision flow examples (normal + override with escalation)
  - §4.A.2: one-excerpt-per-source diagnostic example
  - §4.A.4: primary topic determination example (multi-topic excerpt)
  - §4.A.5: evolution signal accumulation example
  - §4.A.6: coverage gap detection example (school + temporal + evidence gaps)
  - §4.A.7: evolution application example
  - §4.A.8: semantic deduplication example (same hadith from different sources)
  - §4.A.9: cross-science link example (istithna in Nahw vs Usul)
  - §4.A.10: terminology synonym detection example (الفاعل المعنوي / نائب الفاعل)
  - §4.B.1: significance scoring example with computed weights
  - §4.B.2: difficulty estimation example
  - §4.B.3: corpus-driven tree construction example for Sarf
  - §4.B.4: disagreement topology example for fiqh leaf
  - §4.B.6: scholarly landscape example for nahw/mubtada
- Specified LLM calls fully:
  - §4.A.1 Stage 1b: claude-sonnet via Instructor, structured output schema, prompt template
  - §4.A.1 Stage 2: single call for all candidates, structured ranking schema
  - §4.A.4: claude-sonnet via consensus interface, structured output
  - §4.B.4: claude-sonnet primary + gpt-4o consensus, Instructor structured output
- Fixed contracts.py: added missing `entry_lifecycle_propagation` field to EvolutionInvariantChecks
- Fixed SPEC §3.4: added `entry_lifecycle_propagation` to invariant_checks description
- Self-audit found and fixed 4 defects:
  1. §4.A.1 Stage 1b LLM underspecified → added model, prompt, output schema
  2. §4.A.1 Stage 2 ranking call structure unclear → specified single call, all candidates
  3. Pre-approval policy undefined → added definition, creation trigger (10+ approvals), revocation
  4. §6 consensus provider fallback missing → added degraded mode with confidence cap at 0.75
- Added small-tree fast path: trees < 10 leaves skip Stage 1b
- Made evolution_sensitivity configurable per SCIENCE.md (multiplier 0.5–2.0)
- SPEC grew from 691→868 lines (177 lines added, mostly examples)

### Decisions Made
- Pre-approval policies trigger after 10+ consecutive unmodified approvals per source+science
- Consensus provider fallback caps confidence at 0.75 (forces human gate review)
- Small trees (< 10 leaves) skip LLM topic search, use all leaves as candidates
- Evolution sensitivity is a per-science multiplier on the global signal threshold

### Owner Questions
- None new

---

## Session: Synthesis Engine CREATIVE
**Date:** 2026-03-06
**Type:** CREATIVE
**Engine:** Synthesis (محرك التوليف)

### What Was Done
- **Web research (8 searches):** LLM multi-document synthesis, attribution-first generation (Slobodkin et al. 2024), OpenScholar (Nature 2025), contradiction detection in RAG, long-form structured generation techniques, Islamic scholarly comparison tools, hallucination rates in MDS (Belem et al. 2025), NEXUSSUM hierarchical summarization
- **§4.A improvements:**
  - §4.A.2: Added scholarly landscape loading as a key Phase 1 input — the synthesis engine validates and enriches the taxonomy engine's pre-computed landscape rather than rebuilding it
  - §4.A.3 (Phase 2): Rewrote all 7 steps with precise Pydantic schemas, exact prompt structures, LLM output formats, and specific formulas (Herfindahl index defined, mu'tamad keyword lists, etc.)
  - §4.A.4.1 (Phase 3 — Factual Layer): Complete redesign as "Attribution-First" generation — plan claims → select source spans → generate conditioned on spans → verify entailment. Based on Slobodkin et al. 2024 and Belem et al. 2025 findings on hallucination rates
  - Added no-grounded-claims edge case handling
- **§4.B new capabilities (architect-originated):**
  - §4.B.5 — Khilaf Disambiguation Engine (تحرير مسألة الخلاف): Automatic tahrir al-mas'ala through atomic sub-claim decomposition, agreement-disagreement matrix construction, and four-category classification (lafzi, ishtiraki, haqiqi, su'al_mukhtalif). Novel contribution: no existing tool automates this fundamental scholarly methodology.
  - §4.B.6 — Socratic Self-Verification and Assessment Generation: Dual-purpose system that generates comprehension questions at 4 cognitive levels to both (1) detect entry coherence defects and (2) fuel the user model's assessment system
- **contracts.py created:** Full Pydantic models for all input/output schemas, Phase 2/3 intermediates, and all 6 §4.B capability outputs
- **RESOURCES.md updated:** 7 new research entries (Attr-First, OpenScholar, NEXUSSUM, DiverseSumm, Belem et al., LAQuer, contradiction detection)
- **Self-audit:** 4 defects found and fixed:
  1. ExcerptSpan "approximate" offsets ambiguous → clarified as ±50 chars for highlighting, not extraction
  2. No-grounded-claims edge case missing → added diagnostic entry generation
  3. Agreement matrix storage format unspecified → specified flat triple representation
  4. Herfindahl index formula undefined → added explicit formula

### Decisions Made
- Attribution-first generation over generate-then-cite: research shows 75% hallucination in standard MDS
- Khilaf disambiguation uses four categories (not traditional two) — `ishtiraki` and `su'al_mukhtalif` are novel
- Socratic self-verification is a quality mechanism AND an assessment generator — dual-purpose by design
- Scholarly landscape is the PRIMARY analysis source when available (confidence ≥ 0.6)
- Entry citation format: standard academic Arabic format (Author, Work (ed. Tahqiq, Publisher), vol:page)

### Owner Questions
- None new (API keys still pending, not blocking)

---

## Session 12 — Source Engine CREATIVE
**Date:** 2026-03-06
**Type:** CREATIVE
**Focus:** Source engine §4.B transformative capabilities

### What Was Done
1. **Research phase** (7 web searches): Investigated digital Islamic library management, usul-data structured scholar dataset, CBDB prosopographical database model, Wikidata SPARQL for Islamic scholars, tahqiq quality assessment challenges.
2. **Three new §4.B capabilities invented:**
   - **§4.B.8 — Cross-Validated Scholar Authority Bootstrapping:** Uses Usul-Data (MIT) + Wikidata SPARQL + OpenITI to cross-validate scholar records across three independent sources. Disagreements surfaced as research signals. Death date triangulation, known works union, novel teacher-student links from Wikidata.
   - **§4.B.9 — Source Difficulty Prediction:** Seven-signal weighted model predicts processing difficulty BEFORE normalization. Enables strategic queue prioritization — easy/high-yield sources first, matching curricular study order. No LLM call needed.
   - **§4.B.10 — Tahqiq Apparatus Fingerprinting:** Automated detection of genuine vs. commercial tahqiq through analysis of footnote manuscript references, variant readings, hadith takhrij, and editorial entropy. Addresses documented problem of fake tahqiq editions.
3. **contracts.py updated:** Added 8 new Pydantic models (CrossValidationResult, DifficultyPrediction, TahqiqFingerprint, and supporting models).
4. **Self-audit:** 4 defects found and fixed (Wikidata rate limit retry, expected_human_gates formula, unbounded library names list, Usul-Data name normalization specification).
5. **RESOURCES.md updated:** Usul-Data entry cross-referenced to §4.B.8.

### Decisions
- Usul-Data (seemorg/usul-data, MIT license) adopted as a scholar authority enrichment source alongside OpenITI
- Wikidata SPARQL adopted as a third enrichment source for teacher-student links and cross-validation
- Difficulty prediction does NOT use LLM — pure metadata computation for speed
- Tahqiq fingerprinting uses single-model LLM (not consensus) because it's non-destructive (adjusts trust factor only)

### Quality Metrics
- SPEC: 933 → 1140+ lines (+200 lines of new capabilities)
- §4.B capabilities: 7 → 10
- check_spec_quality.py: 26 defects (15 HIGH) — to be resolved in PRECISION session
- creative_verification.py: §4.B score 90/100, 15 named technologies

### Owner Questions
- None new (API keys still pending, not blocking)

---

## Session: Normalization Engine CREATIVE
**Date:** 2026-03-07
**Type:** CREATIVE
**Duration:** ~1 session

### What Was Done
1. **3 new §4.B transformative capabilities designed** for the normalization engine SPEC:
   - **§4.B.8 — Cross-Page Continuity Intelligence:** Annotates every page boundary with a continuity signal (mid_sentence/mid_paragraph/mid_argument/section_break/division_break). Uses format-specific cues (Shamela HTML page boundaries, PDF reading order, OCR line geometry) and Arabic scholarly argument flow markers to detect whether content at a page boundary is fracturable. Feeds passaging engine with zero-fracture signals. No existing Islamic text tool provides this.
   - **§4.B.9 — Authorial Voice Fingerprint for Multi-Layer Validation:** Builds per-layer stylometric fingerprints (sentence length, vocabulary richness, connective frequency, information density, pronoun patterns) across the entire source, then validates individual page layer attributions against the aggregate fingerprint using Mahalanobis distance outlier detection. Catches systematic layer detection failures (bold formatting disappearing mid-source) and enables cross-source author voice verification as the library grows.
   - **§4.B.10 — Scholarly Discourse Flow Annotation:** Annotates each content unit with a discourse flow map identifying 15 scholarly discourse segment types (definition, ruling, evidence_quran, evidence_hadith, evidence_ijma, evidence_qiyas, position, objection, response, preferred, example, condition, exception, elaboration, narration). Detects complete argument cycles (position → evidence → objection → response → conclusion) and signals argument completeness to the passaging and excerpting engines. Per-science calibration hooks included.
2. **Output schema updated:** Content unit schema in §3 now includes `boundary_continuity` and `discourse_flow` fields. Manifest schema includes `layer_fingerprints` and `discourse_flow_summary`.
3. **Metadata-adds list updated** to include all §4.B-generated metadata (census, tahqiq topology, continuity, fingerprints, discourse flow).
4. **Stale marker removed:** `[CONTINUES NEXT SESSION]` between §4.A.9 and §4.B.
5. **4 vague language defects fixed** in new text (flagged by check_spec_quality.py).

### Decisions
- Cross-page continuity uses argument flow markers (15 opening/closing pattern pairs from Islamic scholarly discourse conventions) rather than general NLP discourse parsing — domain-specific markers are more reliable for classical Arabic
- Authorial voice fingerprint uses 8 statistical features (sentence length, type-token ratio, connective frequency, technical term density, pronoun reference patterns, self-reference patterns, citation density, information density) — chosen because these features have proven discriminative for Arabic authorship attribution in computational stylometry literature
- Discourse flow annotation uses a 15-type taxonomy specific to Islamic scholarly reasoning patterns, not a general rhetorical structure theory framework — the patterns are consistent across 14 centuries of Arabic scholarly production
- Fingerprint validation threshold: 2.5 standard deviations Mahalanobis distance for page-level outlier detection, minimum 50 words per layer per page, minimum 2000 words total for fingerprint reliability

### Quality Metrics
- SPEC: 1072 → 1419 lines (+347 lines of new capabilities)
- §4.B capabilities: 7 → 10
- check_spec_quality.py: 4 HIGH defects remaining (all pre-existing MISSING_EXAMPLE in §4.A.3, §4.A.7, §4.B.2, §4.B.3 — to be resolved in PRECISION session)
- creative_verification.py: §4.B score 90/100, invention ratio 91%, assessment CREATIVE

### Owner Questions
- None new (API keys still pending, not blocking)
