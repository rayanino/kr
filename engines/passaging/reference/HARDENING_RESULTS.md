# Passaging Engine — Hardening Results

**Date:** 2026-03-07
**SPEC version at start:** 1004 lines, 0 non-VAGUE_QUANTIFIER HIGH defects

---

## 1. Adversarial Scenarios (12)

### AS-1: Poisoned boundary_continuity Signal

**Attack vector:** Normalization engine emits `boundary_continuity.type = "mid_sentence"` with confidence 0.95, but the actual text ends with a complete sentence (period + space). §4.A.2 says to skip character-level heuristics when confidence ≥0.7.

**Target:** §4.A.2 (continuity-informed joining)

**Expected defense:** The engine trusts the normalization engine's high-confidence signal and joins without separator.

**Defense adequate?** PARTIALLY. The join produces `...الصلاة. وأما` → `...الصلاة.وأما` (missing space between sentences). Self-validation check #4b catches gross text loss/duplication but NOT bad joins that preserve character count. Self-validation check #8 only checks PASSAGE boundaries, not internal assembly joins.

**Fix:** The normalization engine is the appropriate place to catch this (its output is its contract). However, the passaging engine should not be defenseless. **Added:** a note in §4.A.2 that when `boundary_continuity` overrides a character-level heuristic that would have produced a DIFFERENT join type (e.g., boundary_continuity says mid_sentence but heuristic would have detected sentence-end punctuation), log `PSG_ASSEMBLY_CONTINUITY_OVERRIDE` (info) so that systematic normalization bugs can be detected via log analysis.

### AS-2: Division Tree Off-by-One Overlap

**Attack vector:** Two sibling divisions have ranges [0,5] and [5,10] with inclusive `end_unit_index`. Both claim unit 5. Validation check #6 says "without overlap" but doesn't define overlap for inclusive ranges.

**Target:** §2 validation check #6

**Expected defense:** `PSG_DIVISION_INCONSISTENT` should fire.

**Defense adequate?** NO. The overlap condition is ambiguous for inclusive ranges.

**Fix:** Added explicit overlap definition: for sibling divisions A and B where A precedes B, the constraint is `B.start_unit_index > A.end_unit_index` (strictly greater, since both indices are inclusive).

### AS-3: Argument Nesting Depth Cap Forced Closure

**Attack vector:** Legitimate scholarly text has 4 levels: `مسألة → فرع → فرع → تنبيه`. The depth-3 cap (§4.B.6) forcibly closes all nested arguments at depth 4, treating the 4th-level opening as a new top-level argument.

**Target:** §4.B.6 nested argument handling

**Expected defense:** Depth cap prevents unbounded nesting from pathological input.

**Defense adequate?** YES for safety, NO for correctness. The forced closure may break legitimate 4-deep arguments.

**Fix:** Added `PSG_ARGUMENT_DEPTH_CAP_HIT` (info) error code — logged when the cap fires, so systematic depth violations can be detected. Also added `review_flag: "argument_depth_exceeded"` on affected passages.

### AS-4: Content Census with Corrupt Values

**Attack vector:** Content census has `technical_term_density: -0.3` or `mean_footnotes_per_page: NaN`. §4.B.5 clamps ADAPTED parameters but doesn't validate INPUT census values.

**Target:** §4.B.5 (content census-driven adaptation)

**Expected defense:** The out-of-range guard clamps adapted parameters. But garbage-in → garbage-adapted → clamped garbage.

**Defense adequate?** NO. Negative density values would invert the adaptation formula: `800 × (1.0 - (-0.3) × 0.3) = 800 × 1.09 = 872`, which is within range and wouldn't trigger the guard. The adaptation silently produces a wrong-direction adjustment.

**Fix:** Added input validation on census values before adaptation: all density/ratio values must be ≥0.0, structural depth values must be positive integers. Invalid values → log `PSG_ADAPTATION_FAILED` with reason "invalid census input", use defaults.

### AS-5: Footnote Collision Marker Format Ambiguity

**Attack vector:** `PSG_ASSEMBLY_FOOTNOTE_COLLISION` resolves duplicates by appending suffix (e.g., `1a`, `1b`). But the `ref_marker` format `⌜N⌝` uses integers. Downstream engines parsing `ref_marker` as integer will crash on `1a`.

**Target:** §4.A.2 cross-page footnote renumbering, §7 error handling

**Expected defense:** The collision error is logged and passage is flagged.

**Defense adequate?** PARTIALLY. The flag warns humans but doesn't protect downstream engines from the non-integer marker.

**Fix:** Changed the collision resolution strategy: instead of suffixed markers, renumber ALL footnotes in the passage starting from 1 with no gaps. Since renumbering is deterministic (order of appearance in assembled text), collisions should not occur in correct implementations. Changed the error from "resolve by appending suffix" to "re-run sequential renumbering from 1; if collision persists after sequential renumbering, this indicates a code bug — abort with PSG_ASSEMBLY_FOOTNOTE_COLLISION (fatal)."

### AS-6: Quran Citation Bracket Nesting

**Attack vector:** Malformed brackets: `﴿وَأَقِيمُوا ﴿الصَّلَاةَ﴾﴾` or unbalanced brackets in OCR-corrupted text.

**Target:** §4.A.2 Quran citation integrity at page boundaries

**Expected defense:** The engine tracks open brackets, but nesting behavior is undefined.

**Defense adequate?** NO. Nested `﴿` without defined behavior creates ambiguity.

**Fix:** Added: "Quran citation brackets are treated as non-nesting. Each `﴿` opens a citation region. Each `﴾` closes the most recently opened region. If a `﴾` appears with no open region, it is treated as regular text. If multiple `﴿` appear before a `﴾`, only the FIRST opened region is tracked; subsequent `﴿` within an open region are treated as regular characters."

### AS-7: Layer Segment Overflow in Content Unit

**Attack vector:** A content unit has `primary_text` of 480 characters, but its `text_layers` segment claims `end: 520`. The segment extends 40 characters past the text.

**Target:** §4.A.2 text layer rebasing

**Expected defense:** Self-validation check #5 catches gaps and overlaps in the ASSEMBLED passage, but doesn't catch malformed INPUT segments.

**Defense adequate?** NO. The rebasing computation would produce incorrect offsets.

**Fix:** Added input validation during layer rebasing: if any segment's `end` exceeds its content unit's `primary_text` length, clamp the segment to text length and log `PSG_ASSEMBLY_LAYER_MISMATCH` (already exists — clarified that it covers this input case as well).

### AS-8: Below-Minimum Division with No Siblings

**Attack vector:** A division has 30 Arabic words and is the only child of its parent (no siblings to merge with).

**Target:** §4.A.4 Step 2 (size evaluation)

**Expected defense:** Merge with sibling. But no sibling exists.

**Defense adequate?** NO. The SPEC defines merge only with siblings.

**Fix:** Added: "If a below-minimum passage has no siblings (it is the only child of its parent division), the engine attempts to merge with the PARENT division's nearest sibling's last/first passage. If no parent siblings exist either (the division is the sole descendant of the root), emit the passage as-is with `review_flag: "very_short"`. An undersized passage is better than lost content."

### AS-9: All Discourse Flow Segments Are `unknown` Type

**Attack vector:** Normalization engine produces `discourse_flow` for all content units, but every segment has type `unknown`. The discourse flow is present (non-null) so the keyword state machine fallback doesn't trigger. But the discourse flow provides zero useful signal.

**Target:** §4.B.6 (argument detection signal hierarchy), §4.B.7 (discourse cost table)

**Expected defense:** The keyword state machine is "secondary (fallback)" triggered when `discourse_flow` is absent (null).

**Defense adequate?** NO. Discourse flow that is present but useless (all unknown) is treated as authoritative.

**Fix:** Added quality gate: if >80% of discourse segments in a division have type `unknown`, treat the discourse flow as absent for that division. Log `PSG_DISCOURSE_FLOW_ABSENT` with reason "low quality (>80% unknown segments)."

### AS-10: LLM Splitting on Massive Text Block

**Attack vector:** A single content unit has 50,000 characters (~12,000 words). The prose strategy attempts LLM-assisted splitting (§4.A.4 Step 3), but the LLM context window cannot fit 50,000 characters.

**Target:** §4.A.4 Step 3 (LLM-assisted splitting)

**Expected defense:** The SPEC says "the engine sends the text to an LLM" without size limits.

**Defense adequate?** NO. LLM calls on oversized input will fail or truncate.

**Fix:** Added: "When the text exceeds 8000 Arabic words (~32000 characters), the engine sends overlapping windows of 4000 words each (with 200-word overlap) to the LLM. Boundary candidates from each window are collected and merged, deduplicating candidates within 50 characters of each other."

### AS-11: Single-Unit Passage Text Identity

**Attack vector:** A passage consists of one content unit. The text integrity check #4b has ±0 tolerance (num_joins = 0). If the assembly process trims trailing whitespace from `primary_text`, the character count won't match and the check fails as `PSG_VALIDATION_TEXT_LOSS` (fatal).

**Target:** §4.A.10 check #4b, §4.A.2 assembly process

**Expected defense:** Character count invariant.

**Defense adequate?** PARTIALLY. The invariant is correct but the assembly behavior for leading/trailing whitespace is unspecified.

**Fix:** Added: "For single-unit passages, `passage_text` is identical to the content unit's `primary_text` — no trimming, no modification. For multi-unit passages, the assembled text begins with the first unit's `primary_text` (untrimmed) and ends with the last unit's `primary_text` (untrimmed). Joining rules (Rules 1–4) apply only at the BOUNDARIES between adjacent units."

### AS-12: Self-Validation Check #8 Ambiguity at Division Boundaries

**Attack vector:** A passage ends mid-sentence, but the passage and the next passage belong to different divisions. Check #8 says "division boundaries are always valid passage boundaries regardless of sentence position." The attacker exploits this: normalization engine assigns every page to its own division (1-page divisions), making ALL boundaries division boundaries. Every mid-sentence split passes check #8.

**Target:** §4.A.10 check #8 (boundary integrity check)

**Expected defense:** The division tree is validated in §2 check #6 for consistency, but there's no check against pathologically fine-grained division trees.

**Defense adequate?** PARTIALLY. If the normalization engine produces pathological divisions, every boundary is "valid" per check #8 but the passages are garbage.

**Fix:** Added to §5 (Layer 2 automated checks): "Division granularity check: if the average content units per leaf division is <1.5, the division tree is pathologically fine-grained and likely incorrect. Log `PSG_DIVISION_PATHOLOGICAL` (warning) and flag all passages from this source."

---

## 2. Error Cascade Analyses (2)

### Cascade 1: PSG_DIVISION_INCONSISTENT → Flat Passaging → Oversized Implicit Division → PSG_ARGUMENT_NO_SUBBOUNDARY

**Trigger:** Division tree has inconsistent ranges for a 5000-word region.

**Step 1:** §2 validation fires `PSG_DIVISION_INCONSISTENT` (warning). The affected region falls back to flat passaging.

**Step 2:** Flat passaging treats the 5000-word region as a single implicit division (§4.A.4 "Empty division tree" rules).

**Step 3:** The implicit division exceeds the hard max (2000 words). Step 3 (semantic splitting) attempts to find split points. If §4.B.6 is enabled, argument detection runs on the 5000-word block.

**Step 4:** Argument detection (using keyword fallback, since flat passaging means no fine-grained discourse flow correlation to divisions) detects one giant argument spanning 4500 words. The argument is >150% of hard max (>3000), so §4.B.6 says split at internal sub-argument boundaries.

**Step 5:** But the argument is a monolithic block with no position/evidence/response subdivision (it's a long narration or historical account). No sub-argument boundary found. §4.B.6 falls back to paragraph splitting and logs `PSG_ARGUMENT_NO_SUBBOUNDARY` (warning). Passages flagged with `argument_preserved` + `low_confidence_boundary`.

**Result:** The cascade produces passages with:
- `division_path` = synthetic `[no structure]` entry
- `review_flags` = `[low_confidence_boundary, argument_preserved, split_from_large]`
- No argument structure metadata (the argument was split, so `argument_structure.protected_from_split: false`)

**Is this handled?** YES, but the output quality is poor. Every passage in the affected region has multiple warning flags. The human gate at excerpting will surface these.

**Improvement opportunity:** When flat passaging produces >5 passages that all have `argument_preserved` + `low_confidence_boundary`, add a source-level flag `PSG_REGION_NEEDS_RESTRUCTURING` suggesting re-normalization or manual structure annotation.

### Cascade 2: PSG_CONTENT_GAP → Missing Units → Coverage Check Bypass → Silent Data Loss

**Trigger:** Content stream has a gap: unit_indices [0,1,2, 5,6,7,...]. Units 3 and 4 are missing.

**Step 1:** §2 validation fires `PSG_CONTENT_GAP` (warning). Processing continues with actual units.

**Step 2:** Assembly skips missing indices. A passage that should span units [0-5] now spans [0-2, 5]. The text from units 3-4 is lost.

**Step 3:** Self-validation check #1 (coverage) requires "every content unit that is not flagged" is covered. But units 3 and 4 are not in the content stream at all — they can't be flagged because they don't exist. The coverage check passes because it checks against EXISTING substantive units, not against the expected range [0, total_content_units-1].

**Step 4:** The passage stream is written. Units 3-4's text is silently lost.

**Is this handled?** NO. The coverage check doesn't catch this because it only verifies that EXISTING units are covered, not that the EXPECTED range is complete.

**Fix applied:** Self-validation check #1 now has two sub-checks:
- Check #1a: Every existing substantive unit is in exactly one passage (existing check).
- Check #1b (NEW): The expected range [0, total_content_units-1] is compared against existing unit indices. Any unit index in the expected range but missing from the content stream was ALREADY flagged by `PSG_CONTENT_GAP` in §2. Check #1b verifies that the gap flag was raised — if missing units exist but no gap was logged, this is a logic error: `PSG_VALIDATION_COVERAGE_GAP` (fatal).

---

## 3. Invariant Verifications (6)

### INV-1: Coverage Invariant

**Statement:** Every content unit with `is_toc_page == false AND is_index_page == false AND is_blank == false` appears in exactly one passage's `unit_range`.

**Verification under normal processing:** Self-validation check #1 explicitly tests this.

**Verification under error recovery:**
- `PSG_DIVISION_INCONSISTENT`: Flat passaging creates an implicit division spanning the affected units. The implicit division is processed through normal passaging. ✅ Coverage maintained.
- `PSG_CONTENT_GAP`: Missing units are not in the content stream, so coverage check passes for existing units. Gap units are logged. ✅ Coverage maintained for existing units (gap is a normalization problem).
- `PSG_FORMAT_DETECTION_FAILED`: Falls back to prose strategy, which processes all units in the division. ✅ Coverage maintained.
- `PSG_LLM_UNAVAILABLE`: Falls back to non-LLM splitting, which still processes all units. ✅ Coverage maintained.
- Argument preservation (§4.B.6): Keeps oversized passages rather than dropping content. ✅ Coverage maintained.
- Corrective merge (§4.B.8): Merges passages but doesn't drop any. ✅ Coverage maintained.

**Verified:** Coverage invariant holds under all processing paths.

### INV-2: Ordering Invariant

**Statement:** Passages are strictly ordered by `sequence_index` (zero-based, monotonically increasing, gapless), and `unit_range.start` values are monotonically increasing.

**Verification under normal processing:** Self-validation check #3 explicitly tests this.

**Verification under error recovery:**
- Merge operations (§4.A.4 Step 2, §4.B.8 corrective merge): Merging two adjacent passages removes one and adjusts the other's range. Sequence indices are reassigned after all merges. ✅
- Split operations (§4.A.4 Step 3): Splitting produces sequential passages in document order. ✅
- Flat passaging: Processes units in index order. ✅
- Argument preservation: May reorder boundary candidates but produces passages in document order. ✅

**Verified:** Ordering invariant holds under all processing paths.

### INV-3: Non-Overlap Invariant

**Statement:** No content unit contributes to more than one passage.

**Verification under normal processing:** Self-validation check #2 explicitly tests this.

**Verification under error recovery:**
- Split operations: Each split piece covers a disjoint subset of the original range. ✅
- Merge operations: Merged passages' ranges are combined (union of adjacent ranges, which are disjoint by construction). ✅
- Division-guided passaging: Leaf divisions have non-overlapping ranges (validated in §2 check #6). ✅ *(With AS-2 fix: sibling divisions have strictly non-overlapping inclusive ranges.)*

**Verified:** Non-overlap invariant holds under all processing paths.

### INV-4: Text Preservation Invariant

**Statement:** `passage_text` is a deterministic function of constituent content units' `primary_text` fields and joining rules. No text is lost or fabricated during assembly.

**Verification under normal processing:** Self-validation check #4 (hash comparison + character count invariant) explicitly tests this.

**Verification under error recovery:**
- Cross-page assembly with `boundary_continuity`: Joining rules insert/remove at most 1 character per join. Character count invariant bounds this. ✅
- Footnote renumbering: Changes marker text but preserves footnote content. New markers are sequential integers — no text loss. ✅ *(With AS-5 fix: collision-free by construction.)*
- Single-unit passages: `passage_text == primary_text` exactly (AS-11 fix). ✅
- Layer rebasing: Operates on offsets, not text content. Does not modify `passage_text`. ✅

**Verified:** Text preservation invariant holds under all processing paths.

### INV-5: Author Preservation Invariant

**Statement:** For multi-layer sources, every `(layer_type, author_canonical_id)` pair present in the constituent content units' `text_layers` appears in the passage's `text_layers`.

**Verification under normal processing:** Self-validation check #10 explicitly tests this.

**Verification under error recovery:**
- Layer rebasing: Rebasing adjusts offsets but preserves layer attribution. Adjacent same-author segments are merged (reducing segment count but not losing attribution). ✅
- Commentary strategy fallback (§4.A.9 → prose): When commentary layers can't be detected, the engine falls back to prose strategy with `commentary_layers_undetected` flag. The layer data from content units is still passed through (rebased to assembled text). ✅
- Layer segment overflow (AS-7 fix): Clamping a segment to text length preserves its `(layer_type, author_canonical_id)`. ✅

**Verified:** Author preservation invariant holds under all processing paths.

### INV-6: Link Consistency Invariant

**Statement:** The predecessor/successor chain forms a valid doubly-linked list: first passage has `predecessor_id == null`, last has `successor_id == null`, and for all middle passages, `predecessor_id` points to the passage with `sequence_index - 1` and `successor_id` points to `sequence_index + 1`.

**Verification under normal processing:** Self-validation check #9 explicitly tests this.

**Verification under error recovery:**
- §4.A.10 says "After all passages are emitted, the engine sets predecessor_id and successor_id fields by iterating through the passage list." This runs AFTER all merges, splits, and adjustments. ✅
- Corrective merge (§4.B.8): Merges happen BEFORE link assignment (§4.A.1 processing order: create passages → forecast/adjust → emit and validate). ✅

**Potential risk:** If a future code change adds post-emission modifications that don't re-run linking, the invariant could break. The self-validation check catches this, but only at runtime.

**Verified:** Link consistency invariant holds under all current processing paths.

---

## 4. Signal Disagreement Attack (Definition of Done #4)

### Constructed Scenario

A 1500-word division from المغني discusses traveler's prayer (صلاة المسافر).

**Discourse flow signal:** Normalization engine detected one argument cycle spanning the entire 1500 words. The cycle has segments: `[position (200 words), evidence_hadith (300 words), evidence_qiyas (200 words), objection (250 words), response (300 words), preferred (250 words)]`. `argument_cycle_complete: true`. Coverage: 1500/1500 = 100%.

**Keyword state machine signal:** The passaging engine's keyword scan finds:
- `مسألة:` at word 1 (opening)
- `القول الأول:` at word 250 (sub-position within the مسألة? Or new argument?)
- `القول الثاني:` at word 650 (second position)
- `والراجح:` at word 1300 (conclusion)

The state machine interprets `القول الأول:` and `القول الثاني:` as two separate argument openings (position markers from the opening marker list). Result: 2 arguments (one from word 1 to word 650, one from word 650 to word 1500). Coverage: ~1400/1500 = 93%.

**Resolution per current SPEC:** Coverage comparison: 100% (discourse flow) vs 93% (keywords). Discourse flow wins. The entire 1500-word division is one argument span. Since 1500 < 150% of hard max (3000), the argument is preserved as one passage. Result: one 1500-word passage.

**Is this correct?** YES in this case. The discourse flow correctly identified a single مسألة with multiple positions, evidence, objection, response, and conclusion as one argument cycle. The keyword state machine incorrectly split it into two because `القول الأول/الثاني` are position markers that can either open new arguments or mark positions within an existing argument.

**Adversarial variant:** What if the discourse flow INCORRECTLY detected one cycle (it missed that `القول الثاني` actually starts a completely different مسألة — the normalization engine conflated two topics)? Then the keyword signal (2 arguments) would be correct, but the coverage comparison still picks discourse flow (100% > 93%).

**Current defense:** The 5% tie threshold only applies when coverage is WITHIN 5%. Since 100% vs 93% exceeds 5%, discourse flow wins unconditionally.

**Is this adequate?** MOSTLY. The scenario where discourse flow is wrong about argument count is rare because the normalization engine uses per-page context (format-specific markers, heading proximity) that the keyword scan lacks. However, when coverage difference is small (<10%) and argument COUNT differs by >1, the more granular signal is more likely correct.

**Fix applied:** Added secondary granularity tiebreaker: "When coverage difference is ≤10% AND argument count differs by >1 (e.g., discourse flow detects 1 argument, keywords detect 3), use the signal with MORE argument spans and log `PSG_ARGUMENT_SIGNAL_DISAGREEMENT` with reason 'granularity disagreement — preferring more specific signal.' When coverage difference is ≤5% and argument count differs by ≤1, use discourse flow (existing rule). When coverage difference >10%, use the higher-coverage signal (existing rule)."

---

## 5. Corrective Merge Cascade Attack (Definition of Done #5)

### Constructed Scenario

Three consecutive passages from a prose division:
- P1 (300 words): discourse types `{position}` → forecast: `"fragment"` (position without evidence)
- P2 (280 words): discourse types `{evidence_hadith, evidence_athar}` → forecast: `"fragment"` (evidence without position or conclusion)
- P3 (320 words): discourse types `{objection, response, preferred}` → forecast: `"complete"` (has objection-response-conclusion cycle)

The three passages together form one complete مسألة: P1=claim, P2=evidence, P3=counter+response+conclusion.

**Current SPEC behavior (max 1 merge per boundary):**
- Step 1: P1 is fragment. Corrective merge: P1+P2 = 580 words (< hard max). Re-forecast P1+P2: types `{position, evidence_hadith, evidence_athar}`. Still no conclusion. Forecast: `"partial_closing"` (has position+evidence but no conclusion).
- Step 2: Cap reached. No further merge. P1+P2 stays as 580-word partial-closing. P3 stays as 320-word complete.
- Result: The full argument is split between two passages. P1+P2 has claim+evidence but no conclusion. P3 has counter+response+conclusion. The excerpting engine receives two passages that together form one complete argument, but individually are incomplete.

**Is this problematic?** YES. The three fragments form a natural scholarly unit. The corrective merge cap prevents full reassembly.

**Fix applied:** Changed the corrective merge rule from "at most ONCE per boundary" to "at most TWO corrective merges per initial fragment passage (merging at most 3 original passages into one)." The chain: P1 fragment → merge with P2 → still incomplete → merge with P3 → 900 words, types `{position, evidence_hadith, evidence_athar, objection, response, preferred}`, forecast: `"complete"`.

**Guard:** Total merged passage must not exceed hard max (2000 words). The chain limit (max 2 merges, max 3 original passages) prevents runaway cascade.

**Alternative scenario: 5 fragments in sequence.** Even with the 2-merge cap, fragments P4 and P5 would not be merged into the P1+P2+P3 cluster. This is acceptable: 3-passage merges cover the common case (a مسألة split into claim/evidence/conclusion). Longer fragment sequences (5+) indicate either pathological splitting or genuinely disconnected content. These are flagged with `incomplete_scholarly_content` for human review.

---

## 6. Discourse Cost Table Completeness (Definition of Done #6)

### Taxonomy Enumeration

The SPEC references a "15-type scholarly discourse taxonomy" and also mentions "narration" in the §4.B.7 type list.

**Canonical 15 types:** definition, ruling, position, evidence_quran, evidence_hadith, evidence_athar, evidence_qiyas, evidence_ijma, objection, response, preferred, example, condition, exception, elaboration.

**Issue:** §4.B.7 lists "narration" as a 16th type. This contradicts "15-type taxonomy."

**Resolution:** narration IS a legitimate discourse type in Islamic scholarly texts (isnad + matn narration chains). The taxonomy should be 16 types, or narration should be classified as a subtype of evidence (evidence_narration ≈ evidence_hadith/evidence_athar). Since §4.B.6 already has isnad-specific handling (§4.A.4 isnad chain integrity), and narration appears in the discourse flow taxonomy from normalization, narration should be the 16th type. **Fix:** Changed "15-type" to "16-type" throughout the SPEC.

### 256 Possible Pairs (16×16)

With 16 types, there are 256 pairs. The cost table covers 31 explicitly. The remaining 225 use the default 0.4.

### Pairs Where Default 0.4 Is Clearly Wrong

| Transition | Default Cost | Should Be | Rationale |
|---|---|---|---|
| definition → ruling | 0.4 | 0.15 | Definition of a concept followed by its ruling is natural scholarly flow |
| example → example | 0.4 | 0.1 | Consecutive examples illustrating the same rule |
| condition → condition | 0.4 | 0.15 | Sequential listing of conditions |
| exception → exception | 0.4 | 0.15 | Sequential listing of exceptions |
| elaboration → elaboration | 0.4 | 0.1 | Continued elaboration on the same point |
| preferred → ruling | 0.4 | 0.1 | Conclusion followed by formal ruling — natural close |
| ruling → position | 0.4 | 0.2 | Ruling stated, then scholarly positions presented |
| narration → position | 0.4 | 0.15 | Hadith narration followed by scholarly analysis |
| narration → narration | 0.4 | 0.1 | Consecutive narrations on the same topic |
| position → narration | 0.4 | 0.3 | Position followed by supporting narration evidence |
| exception → ruling | 0.4 | 0.2 | Exception to a rule followed by ruling summary |
| condition → position | 0.4 | 0.6 | Condition orphaned from its exception, then new position |
| example → ruling | 0.4 | 0.2 | Example followed by its ruling — natural |
| objection → objection | 0.4 | 0.3 | Multiple objections in sequence before response |

**Fix:** Added 14 explicit entries to the discourse cost table. Default 0.4 remains for truly unpredictable transitions.

---

## 7. SPEC Defects Found and Fixed (Summary)

| # | Location | Defect | Fix |
|---|---|---|---|
| 1 | §4.A.2 | No logging when boundary_continuity overrides character heuristic | Added `PSG_ASSEMBLY_CONTINUITY_OVERRIDE` (info) |
| 2 | §2 check #6 | Overlap definition ambiguous for inclusive ranges | Added explicit `B.start > A.end` for siblings |
| 3 | §4.B.6 | Depth cap forced closure has no review flag | Added `argument_depth_exceeded` review flag + `PSG_ARGUMENT_DEPTH_CAP_HIT` error |
| 4 | §4.B.5 | No validation on census INPUT values | Added non-negative validation with default fallback |
| 5 | §4.A.2/§7 | Footnote collision suffix format breaks downstream | Changed to re-run sequential renumbering; persistent collision is fatal |
| 6 | §4.A.2 | Nested Quran brackets undefined | Defined non-nesting semantics |
| 7 | §4.A.2 | Layer segment overflow on input not caught | Clarified clamping applies to input segments |
| 8 | §4.A.4 | Below-minimum division with no siblings undefined | Added parent-sibling merge, then very_short fallback |
| 9 | §4.B.6 | All-unknown discourse flow treated as authoritative | Added >80% unknown quality gate |
| 10 | §4.A.4 | LLM splitting has no input size limit | Added 8000-word windowing with 200-word overlap |
| 11 | §4.A.2 | Single-unit passage text identity unspecified | Added explicit identity rule |
| 12 | §5 | No check for pathologically fine-grained division tree | Added division granularity check |
| 13 | §4.B.6 | Signal disagreement uses only coverage, not granularity | Added granularity tiebreaker for ≤10% coverage difference |
| 14 | §4.B.8 | Corrective merge cap too restrictive (1 merge) | Changed to max 2 merges (max 3 passages merged) |
| 15 | §4.B.7 | 14 discourse transitions use wrong default cost | Added 14 explicit cost entries |
| 16 | Throughout | "15-type" taxonomy but 16 types exist (narration) | Changed to "16-type" |
| 17 | §4.A.10 | Coverage check doesn't verify expected range vs actual | Added check #1b for gap correlation |
| 18 | §7 | Missing error codes for new scenarios | Added 3 new error codes |
