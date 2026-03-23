# Excerpting SPEC — kr-integrity Audit Handoff

**Date:** 2026-03-23
**Task:** 8-lens integrity audit on complete SPEC (2381 lines, 12 sections)
**Skills used:** kr-integrity, critical-review, thinking-frameworks
**Commits:** integrity audit fixes (this commit)
**Status:** All findings fixed. SPEC is implementation-ready.

---

## Audit Structure

Audited in 2 chunks across 5 responses (2 audit chunks + 3 fix responses):

| Chunk | Sections | Lines | Findings |
|-------|----------|-------|----------|
| 1 | §1–§5 (Purpose, Data Model, Contracts, Self-Containment, Phase 1, Phase 2) | 16–1204 | 5 HIGH, 5 MEDIUM |
| 2 | §6–§10 (Domain Rules, Phase 3, Error Handling, Deferred, Tests) | 1205–2342 | 5 HIGH, 7 MEDIUM, 2 LOW |
| **Total** | | | **10 HIGH, 12 MEDIUM, 2 LOW** |

## All Findings (Fixed)

### HIGH (10) — would cause wrong implementation or knowledge corruption

| # | Lens | Section | Description | Fix |
|---|------|---------|-------------|-----|
| 10.1 | Knowledge Corruption T-7 | §7.1 F-DET-1 | **excerpt_id collision for split divisions** — format `exc_{source_id}_{div_id}_{unit_index}` produces duplicate IDs when a division is split into multiple chunks (each chunk starts unit_index at 0) | Added `chunk_index` to ID format: `exc_{source_id}_{div_id}_{chunk_index}_{unit_index}`. Updated 4 locations. |
| 10.2 | Knowledge Corruption T-4 | §7.2/§7.3 | **enrichment→consensus ordering breaks context_hint** — LLM enrichment produces context_hint before consensus may change self_containment level, creating I-ER-4 violations | Added post-consensus context_hint repair step in §7.3.3 |
| 2.1 | Knowledge Corruption T-2 | §4.5 | **Layer splitting creates artificial attribution boundaries** — splitting a division at a character offset divides a layer segment, creating a false author transition | Added `layer_split_points` field to AssemblyMetadata; F-DET-3 merges split-induced boundaries |
| 2.2 | Knowledge Corruption T-1/T-2 | §4.7 | **Footnote renumbering ordering unspecified** — renumbering modifies assembled_text but ordering vs layer rebasing was undefined | Swapped §4.1 steps 5/6; footnote aggregation now precedes layer rebasing; added CRITICAL ORDERING note |
| 1.1 | Zero Ambiguity | §4.3 | **"Word-initial character" undefined** in mid_sentence join refinement | Replaced with precise word-final indicator list (ة, ى, tanwin) |
| 9.1 | Zero Ambiguity | §7.3.3 | **school_confidence has no producer** — enrichment/verification schemas didn't produce confidence values | Added school_confidence to enrichment prompt, schema, and verification schema |
| 3.1 | Silent Failure | §2.2.2 | **chunk_index on ExcerptRecord underfined for unsplit chunks** | Defined derivation: 0 for unsplit, split_info.chunk_index for split |
| 11.1 | Silent Failure | §7.1 F-DET-6 | **phantom `page_ranges` field** — AssemblyMetadata doesn't have this field | Rewrote F-DET-6 to use actual physical_pages + join_points |
| 12.2 | Error Path | ADV-E-10 | **Contradictory recovery** — ADV-E-10 said "produce fallback segment", §5.5.2/§8.2 said "skip chunk" | Aligned ADV-E-10 with §5.5.2/§8.2 (skip, flag for reprocessing) |
| 13.2 | Contract Consistency | §2.2.2 | **PageRange type used but never defined** | Added type definition: `{volume: int|null, start_page: int, end_page: int}` |

### MEDIUM (12) — missing detail, unnecessary harshness, or untested assumption

| # | Section | Fix |
|---|---------|-----|
| 1.2 | §4.8 | Specified exact Unicode codepoints for Arabic noise stripping; clarified non-contradiction with §4.3 |
| 1.3 | §4.2 | Removed "case-insensitive" (irrelevant for Arabic); changed to word-boundary matching for exclusion keywords |
| 1.4 | §5.4.1 | Added diacritic-stripped matching fallback (step d2) + new EX-A-012 warning code |
| 3.2 | §5.3.4/§5.4.3 | Changed V-P2-14 from fatal to warning; clarified engine always derives word offsets from segments |
| 9.2 | §2.2.2 | Defined attribution_confidence values: null (deterministic), 0.67 (2-of-3 consensus), 0.0 (all disagree) |
| 11.3 | §7.1 F-DET-8 | Rewrote footnote relevance to use `⌜{ref_marker}⌝` text search instead of phantom character offset |
| 11.4 | §10.3 | Replaced phantom `verse_statement` with valid ScholarlyFunction values |
| 12.1 | §8.1 | Distinguished EX-A-003 gap repair (extend ≤5 chars) from EX-A-004 overflow clamp |
| 12.3 | §8.2 | Clarified repair→re-validate→retry→skip sequence for coverage violations |
| 13.1 | §2.2.2 | Added `decontextualization_risk` and `verification_skipped` to known review_flags |
| 15.1 | §7.1 F-DET-3 | Added explicit word-to-character offset conversion algorithm |
| 16.1 | §9.1/§9.2 | Moved DC-09 extension hook from TeachingUnit to ExcerptRecord |

### LOW (2)

| # | Section | Fix |
|---|---------|-----|
| 11.2 | §7.1 F-DET-7 | Fixed field path from `assembly_metadata.heading_path` to `div_path` |
| 15.2 | §7.3.4 | Added note about gate resolution re-processing mechanism (cross-engine) |

## Assumptions Needing Build Testing (5)

| # | Section | What to Test |
|---|---------|-------------|
| 6.1 | §5.4.1 | Snippet matching failure rate on 50 extended fixtures |
| 6.2 | §5.5.1 | MAX_TOKENS sufficiency for 4000–5000 word chunks (already flagged in SPEC) |
| 6.3 | §4.4 | Merged tiny divisions producing coherent teaching units (30-book probe) |
| 14.1 | §7.2 | Enrichment call scalability at 5000 words / 40+ units |
| 14.2 | §6.4 | Scholar epithet resolution accuracy with source school context |

## New Artifacts

- Error code `EX-A-012` (diacritic-mismatched snippet in offset normalization)
- AssemblyMetadata fields: `layer_split_points`, `footnote_renumber_map`
- `PageRange` type definition in §2.2.2
- Review flags: `decontextualization_risk`, `verification_skipped`
- `school_confidence` field in enrichment and verification LLM schemas
- `confidence` field in verification response schema

## SPEC Metrics After Audit

- Lines: 2381 (was 2343)
- Error codes: 28 (was 27, +EX-A-012)
- Invariants: 29 (unchanged)
- Verification checks: 34 (unchanged)
- Domain rules: 22 (unchanged)

## What's Next

1. **Step 3b: Rewrite contracts.py** — CC task. Prepare handoff via kr-preparing-cc-handoffs. The contracts must reflect all audit fixes (chunk_index in excerpt_id, PageRange type, layer_split_points, footnote_renumber_map, school_confidence in enrichment schema, confidence in verification schema, new review flags).

2. **Step 3c: Build prep** — Technology survey, architecture stubs, test skeleton.

## Session End Retrospective

**What went well:** The 8-lens framework caught real defects that a general review would miss. The most dangerous finding (excerpt_id collision, Defect 10.1) would have caused silent data loss in every split division — roughly 0.9% of all Shamela divisions. The enrichment→consensus ordering issue (Defect 10.2) was subtle: it only manifests when the verifier disagrees with Phase 2b's self-containment assessment AND the consensus changes the level. Both findings survived the session 4 coherence review because they involve cross-section interactions that single-section reading doesn't expose.

**What went wrong:** My first edit pass accidentally created duplicate blocks (duplicate context_hint repair section, duplicate EX-A-012 in catalog). These were caught in the final consistency sweep, not by the edit process itself. Root cause: when applying multiple fixes to the same file region, the str_replace tool can match broader patterns than intended if the old_str isn't precise enough. Fix: after each batch of edits, run a duplicate-detection check before committing.

**Stale memory entries:** Update "KR EXCERPTING ENGINE STATE" — SPEC is now 2387 lines with 28 error codes. Integrity audit + deep review complete.

**Protocol changes:** Add to audit protocol: "After all edits, run a duplicate-detection sweep: grep for repeated section headers, repeated error codes, and repeated block-level phrases before committing."

---

## Post-Audit Deep Review (same session, owner-requested)

Owner requested a deep critical review after the audit fixes were pushed. Despite context degradation risk (same-chat review per standing order 8), the review used tool-grounded verification (fresh clone, grep-based tracing, end-to-end data flow analysis) and found 4 additional issues the 8-lens audit missed:

### Additional Findings (Fixed)

| # | Severity | Section | Description | Fix |
|---|----------|---------|-------------|-----|
| R-1 | HIGH | §7.1 F-DET-2, V-P3-2 | F-DET-2 split+rejoin destroys paragraph breaks in primary_text, violating I-ER-2 and causing false V-P3-2 failures | Changed to substring extraction; made V-P3-2 whitespace-robust |
| R-2 | MEDIUM | §4.4 | Merge of tiny (45w) + large sibling (4960w) = 5005w triggers split, violating I-AC-7 mutual exclusivity | Added merge size guard |
| R-3 | MEDIUM | §7.1 F-DET-9 | ScholarAttribution field mapping unspecified (3 missing fields, no dedup rule with §7.2) | Added full field conversion and deduplication |
| R-4 | MEDIUM | §2.2.2, §7.1 F-DET-5, §6.3 | evidence_refs source claimed "Deterministic + LLM" but §7.2 never produces evidence_refs | Changed to "Deterministic"; clarified scope in F-DET-5 and §6.3 |

### Why The Audit Missed These

- **R-1:** The 8-lens audit reads each section independently. F-DET-2's split+rejoin looks correct in isolation. The bug only appears when tracing the *exact bytes* from assembled_text (which has \n\n) through F-DET-2 (which collapses whitespace) to V-P3-2 (which compares against a snippet preserving \n\n). This is a cross-section data flow bug that requires end-to-end tracing.
- **R-2:** The merge and split sections are read separately. The interaction only surfaces when you construct a concrete scenario with specific word counts that bridge both thresholds.
- **R-3/R-4:** Both involve checking whether the output schema fields have actual producers — this is Lens 5 (Contract Consistency) but at a more granular level than the audit applied. The audit checked that fields exist; the review checked that field *values* are actually computed.

### Observation: layer_split_points may be dead infrastructure

After splitting, each chunk's text_layers cover [0, len(chunk.assembled_text)). The split point is the *boundary* between chunks, not a position within any chunk. D-011 prevents teaching units from crossing chunk boundaries. Therefore, no teaching unit can ever encounter a split-induced layer boundary. The `layer_split_points` field and the F-DET-3 merge logic are likely dead code. Flagged for CC awareness during build — tests should verify this reasoning.

### Updated SPEC Metrics

- Lines: 2387 (was 2381 after audit, was 2343 original)
- Total findings fixed: 10 HIGH + 12 MEDIUM + 2 LOW (audit) + 1 HIGH + 3 MEDIUM (review) = **11 HIGH, 15 MEDIUM, 2 LOW**
