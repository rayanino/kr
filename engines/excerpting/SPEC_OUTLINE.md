# Excerpting Engine SPEC — Outline

**Date:** 2026-03-22
**Author:** Claude Chat (Architect)
**Status:** DRAFT — awaiting owner review before section writing begins
**Governs:** `engines/excerpting/SPEC.md` (to be rewritten section-by-section)

---

## Design Rationale

This SPEC synthesizes three sources into one coherent document:

1. **Old passaging SPEC** (`engines/passaging/SPEC.md`, 1037 lines) — provides Phase 1 (deterministic preprocessing): cross-page assembly, format strategies, Arabic joining rules, validation checks
2. **Old atomization SPEC** (`engines/atomization/SPEC.md`, 1205 lines) — provides Phase 2 foundation: classification taxonomy, boundary rules, multi-layer attribution, format-specific classification
3. **Old excerpting SPEC** (`engines/excerpting/SPEC.md`, 1038 lines) — provides domain design: decontextualization prevention, evidence handling, implicit references, verse handling, adversarial cases; and Phase 3: metadata enrichment

Plus empirical evidence from two validated experiments (23 divisions, 7 formats).

The old excerpting SPEC was BLOCKED (16 findings, 3 CRITICAL) because its structural framework assumed separate passaging and atomization engines that no longer exist. The domain knowledge is excellent; the architecture is wrong. This outline defines the correct architecture and maps every piece of preserved domain knowledge to its new location.

---

## Key Design Decision: Internal Intermediate Representation

**Decision: Option C (Hybrid) — simple segments for Phase 2, enriched during Phase 3.**

Rationale:
- The experiment validated `ClassifiedSegment` (word offsets + scholarly function + confidence) as sufficient for Phase 2a classification
- The experiment validated `TeachingUnit` (grouped segments + self-containment flag) as sufficient for Phase 2b grouping
- Neither required pre-computed relations, bonds, or embedded references (the old atom model's complexity)
- Phase 3 enriches teaching units with attribution, evidence, cross-references — the metadata that was previously baked into atoms
- This preserves the old excerpting SPEC's domain rules (decontextualization via relation awareness) while grounding the implementation in validated evidence

The data flow:

```
NormalizedPackage
  → Phase 1 → AssembledChunk[]
    → Phase 2a → ClassifiedSegment[]
      → Phase 2b → TeachingUnit[]
        → Phase 3 → ExcerptRecord[]
          → taxonomy engine
```

Each intermediate is simpler than its successor. Phase 1 is fully deterministic. Phase 2 is LLM-driven with structural constraints. Phase 3 adds semantic richness.

---

## Section Structure

### §1 — Purpose and Scope

**What it covers:** What this engine does, what it absorbs (passaging + atomization), what it does NOT do (taxonomy, synthesis, source ingestion). The three-phase architecture at a glance. D-011 as division containment. Position in the pipeline.

**Source material:** Architecture decision (`ARCHITECTURE_DECISION.md`), corrected `CLAUDE.md`.

**Key content:**
- Pipeline position: Source ✅ → Normalization ✅ → **Excerpting** → Taxonomy → Synthesis
- Absorbs passaging (deterministic preprocessing) and atomization (LLM classification) as internal phases
- Produces self-contained, attributed excerpts — the building blocks of the knowledge library
- D-011 constraint: no excerpt spans a division or chunk boundary
- Defines "teaching unit" as the engine's core concept: the smallest segment a student can study and learn something complete from
- Explicit scope exclusions: no cross-source operations, no taxonomy placement, no synthesis

**Dependencies:** None (this section is foundational).

**Estimated length:** ~80 lines.

---

### §2 — Contracts and Data Model

#### §2.1 — Input Contract

**What it covers:** What the excerpting engine receives from normalization. References `engines/normalization/contracts.py` as the authoritative schema. Lists every field the engine uses and how.

**Source material:** `engines/normalization/contracts.py` (726 lines), especially `NormalizedManifest`, `ContentUnit`, `DivisionNode`, `BoundaryContinuity`, `TextLayerSegment`, `DiscourseFlow`.

**Key content:**
- Input files: `library/sources/{source_id}/normalized/manifest.json` + `content.jsonl`
- Manifest fields used: `division_tree`, `layer_map`, `structural_format`, `total_content_units`, `content_census` (when present), `verse_detection`
- ContentUnit fields used: `primary_text`, `text_layers`, `footnotes`, `structural_markers`, `boundary_continuity`, `content_flags`, `discourse_flow` (when present), `physical_page`, `unit_index`
- Fields passed through untouched (D-023): `source_id`, all metadata from manifest
- Pre-conditions: normalized package must pass schema validation; engine does NOT re-validate normalization output

**Dependencies:** Normalization engine must be complete.

**Estimated length:** ~100 lines.

#### §2.2 — Output Contract

**What it covers:** What the excerpting engine produces for the taxonomy engine. Defines `ExcerptRecord` with every field, types, and guarantees.

**Source material:** Old excerpting SPEC §3 (adapted: replace passage_id with div_id, atoms with segments).

**Key content:**
- Output file: `library/sources/{source_id}/excerpts/excerpts.jsonl`
- ExcerptRecord fields: excerpt_id, source_id, div_id, chunk_id (if split), word_range, assembled_text, teaching_unit_segments (classified segments composing this excerpt), primary_scholarly_function, self_contained flag, self_containment_notes, text_layers (rebased to excerpt offsets), footnotes (relevant subset), physical_pages, content_type, attribution metadata (Phase 3), topic_proposal (Phase 3), evidence_refs (Phase 3)
- Guarantees: full coverage (union of all excerpts covers all text in every processed division), no overlap, every excerpt attributed to at least one author layer, D-011 enforced
- Per-source summary: `excerpts_summary.json` with counts, gate statistics, quality flags

**Dependencies:** §2.3 (references internal data model types).

**Estimated length:** ~120 lines.

#### §2.3 — Internal Data Model

**What it covers:** The four intermediate representations flowing between phases. This is where the "atom replacement" decision is specified.

**Source material:** Experiment schemas (`run_tests.py`), architecture decision.

**Key content:**

**AssembledChunk** (Phase 1 output):
- chunk_id, source_id, div_id, div_path (heading hierarchy)
- assembled_text (cross-page joined, continuous)
- word_count
- text_layers (rebased to assembled-text offsets)
- footnotes (collected from constituent content units)
- content_flags (aggregated OR across constituent units)
- physical_pages (list of PhysicalPage from constituent units)
- structural_format (inherited or per-division classified)
- assembly_metadata: constituent unit_indices, join points, boundary_continuity types used
- merge_history (if tiny divisions were merged): list of original div_ids
- split_info (if oversized division was split): original div_id, split point, chunk index

**ClassifiedSegment** (Phase 2a output):
- segment_index (0-based within chunk)
- start_word, end_word (word offsets in assembled_text)
- text_snippet (first 50 chars)
- scholarly_function (from 16-type taxonomy)
- confidence (0.0–1.0)

**TeachingUnit** (Phase 2b output):
- unit_index (0-based within chunk)
- segment_indices (which ClassifiedSegments compose this unit)
- start_word, end_word (word offsets in assembled_text)
- text_snippet (first 80 chars)
- primary_function (dominant scholarly function)
- secondary_functions (additional functions present)
- description_arabic (10-30 word Arabic summary)
- self_contained (boolean, per §3 standard)
- self_containment_notes (when self_contained=false: what context is missing)

**ExcerptRecord** (Phase 3 output — same as §2.2):
- All TeachingUnit fields, plus Phase 3 enrichment

**Dependencies:** None (this section defines what other sections reference).

**Estimated length:** ~150 lines.

---

### §3 — Self-Containment Standard

**What it covers:** The formal definition of self-containment — the engine's primary quality criterion. This addresses review finding F2 (cross-referenced §5.1/§5.2/§5.3 that didn't exist).

**Source material:** Old excerpting SPEC §5 (reworked), experiment self-containment evaluations, `KNOWLEDGE_INTEGRITY.md` T-4 (Context Loss).

**Key content:**

**Definition:** An excerpt is self-contained if a student with general familiarity of the Islamic science (علم) can understand what is being taught without reading the surrounding text from the same division.

**Formal criteria (each must hold):**
- C-SC-1: Every technical term used is either (a) defined within the excerpt, (b) a standard term of the science that any student would know, or (c) flagged in self_containment_notes
- C-SC-2: Every pronoun/demonstrative reference resolves within the excerpt (no dangling "هذا" referring to a prior excerpt)
- C-SC-3: Every evidence citation (Quran, hadith, athar) either includes its text or is a well-known citation identifiable by its opening words
- C-SC-4: The excerpt's argument or rule is complete — not a fragment of a larger argument whose conclusion is elsewhere
- C-SC-5: If the excerpt quotes or responds to another scholar's position, enough of that position is included to understand the response

**Self-containment levels:**
- FULL: All criteria met. Excerpt stands alone.
- PARTIAL: Most criteria met, but some context would help. Phase 3 adds context_hint.
- DEPENDENT: Excerpt cannot be understood alone. Requires connection to adjacent excerpt. Flagged for human review.

**Design decision note:** The experiment used a binary self_contained boolean. The 3-level system is a design extension — PARTIAL captures cases where the experiment's self_containment_notes field was populated but the excerpt was still marked self_contained=true. This provides more actionable information for Phase 3 repair and human gates. Must be validated during build evaluation.

**Threat defended:** T-4 (Context Loss). A DEPENDENT excerpt reaching the taxonomy engine without its dependency is a knowledge integrity violation — the owner would study an incomplete argument.

**Dependencies:** Referenced by §5 (Phase 2b evaluates this), §6 (domain rules defend this), §7 (Phase 3 repairs PARTIAL cases), §10 (tests verify this).

**Estimated length:** ~100 lines.

---

### §4 — Phase 1: Deterministic Preprocessing

**What it covers:** Everything that happens before the LLM is called. This absorbs the old passaging engine's core processing. Fully deterministic, independently unit-testable, ~800 lines estimated implementation.

**Source material:** Old passaging SPEC §4.A.1–§4.A.10, `extract_divisions.py` (validated prototype), `ARCHITECTURE_DECISION.md` §Phase 1.

#### §4.1 — Processing Overview

The Phase 1 pipeline: walk division tree → assemble text → merge/split → rebase layers → aggregate flags → validate. One AssembledChunk per processable division (or chunk).

#### §4.2 — Division Tree Walking

- Start from manifest.division_tree
- Identify leaf divisions (no children)
- Handle multi-volume sources (division_type == "volume" nodes)
- Skip excluded divisions: is_toc_page, is_index_page, bibliography (EXCLUDE_KEYWORDS from prototype)
- Handle empty divisions (0 content units in range): emit warning, skip
- **Minimal division trees** (evaluation C-8): books with <5 headings produce very few leaf divisions, each potentially very large. These are handled by §4.5 (oversized splitting). Sources with a single root division and no children: the entire source text becomes one chunk, then split per §4.5 rules. No special-casing needed — the standard merge/split pipeline handles this naturally.

#### §4.3 — Cross-Page Text Assembly

- For each leaf division, collect content units by unit_index range [start_unit_index, end_unit_index]
- Join primary_text across pages using boundary_continuity separator mapping:
  - mid_sentence → "" (no separator)
  - mid_paragraph → "\n"
  - mid_argument → "\n"
  - section_break → "\n\n"
  - division_break → "\n\n"
  - unknown/absent → "\n"
- Preserve footnote reference markers (⌜N⌝) inline
- Preserve all diacritics exactly (no Unicode normalization)
- Record assembly_metadata: which units, join points, BC types

From old passaging SPEC §4.A.2: Arabic-specific joining rules — when BC=mid_sentence, check if the last character of page N and first character of page N+1 form a valid Arabic word boundary. If not (word split across pages), join without space.

#### §4.4 — Tiny Division Merging

- Threshold: <50 Arabic words (from division size analysis: 29.1% of raw Shamela divisions)
- Merge with next sibling under same parent, recursively
- If no next sibling, merge with previous sibling
- If no siblings at all (only child), process as-is regardless of size
- Record merge_history on resulting AssembledChunk
- Word count uses Arabic word counter (words containing ≥1 Arabic character)

#### §4.5 — Oversized Division Splitting

- Threshold: >5000 Arabic words (from division size analysis: 0.9% at raw Shamela level)
- Split at structural markers within the division text:
  - First preference: heading-level structural markers (detected by normalization)
  - Second preference: discourse_flow section_break boundaries within the text
  - Third preference: paragraph breaks (\n\n) near the midpoint
  - Last resort: sentence boundary nearest the midpoint
- Each resulting chunk gets a chunk_id: {div_id}_chunk_{N}
- Record split_info on each chunk
- Chunks inherit parent division's metadata

Design question for section writing: Should marker-free divisions >5000w get a lower threshold? The evaluation noted this as C-6. Research needed.

#### §4.6 — Text Layer Rebasing

- Normalization provides text_layers per content unit (character offsets within that unit's primary_text)
- After cross-page assembly, rebase all layer segment offsets to assembled-text coordinates
- Verify: every character in assembled_text is covered by exactly one layer segment (normalization invariant, re-verified after assembly)
- Handle layer transitions at page boundaries: if two adjacent pages end/start with the same layer, merge the segments

#### §4.7 — Content Flag and Footnote Aggregation

- Content flags: OR-aggregate across all constituent content units (if any unit has_verse, the chunk has_verse)
- Footnotes: collect all footnotes from constituent units, deduplicate by ref_marker, preserve order
- Physical pages: collect all PhysicalPage records in order

#### §4.8 — Heading Alignment Filter (L-003)

- From experiment: heading alignment (first N stripped chars of heading appear in first M stripped chars of assembled text) rejects misaligned divisions that would produce garbage LLM results
- Strict mode: first 15 stripped chars in first 100 stripped chars
- Relaxed mode: first 30 stripped chars in first 200 stripped chars
- Misaligned divisions: emit warning with error code, process anyway but flag for human review
- This is a quality filter, not a hard gate — CC's evaluation found 40-60% rejection rates with strict mode on some fixtures

#### §4.9 — Phase 1 Self-Validation

- V-P1-1: Every leaf division maps to ≥1 AssembledChunk (or is explicitly skipped with reason)
- V-P1-2: Union of all chunks covers all content units in the source (no silent data loss)
- V-P1-3: No chunk has 0 words
- V-P1-4: No chunk exceeds 5000 words (splitting worked)
- V-P1-5: Text layer rebasing produces full coverage (every char attributed)
- V-P1-6: Word count of each chunk matches Arabic word counter on assembled_text

**Dependencies:** §2.1 (input contract), §2.3 (AssembledChunk definition).

**Estimated length:** ~250 lines.

---

### §5 — Phase 2: LLM Teaching Unit Extraction

**What it covers:** The LLM-driven classification and grouping. This absorbs the old atomization engine's core classification and the experiment's validated approach.

**Source material:** Validated experiment (`run_tests.py` prompts + schemas), old atomization SPEC §4.A.1–§4.A.10, evaluation constraints C-1 through C-4.

#### §5.1 — Processing Overview

Two-step approach (Approach B, validated in 23/23 divisions):
1. Phase 2a (classify): LLM classifies text into segments by scholarly function
2. Phase 2b (group): LLM groups segments into self-contained teaching units

Both steps operate on one AssembledChunk at a time. D-011 is structurally enforced: the LLM only sees text within one chunk, so it cannot create cross-chunk units.

#### §5.2 — Phase 2a: Segment Classification

- Input: AssembledChunk.assembled_text
- Output: ClassifiedSegment[] covering the full text
- LLM prompt: APPROACH_B_CLASSIFY_SYSTEM (specified in full — from experiment, adapted for production)
- Response schema: ClassificationResult (Pydantic model, specified in full)
- Model: anthropic/claude-opus-4.6 via OpenRouter
- Temperature: 0
- MAX_TOKENS: ≥32768 for chunks >2000 words (empirically validated: classify produces 125-166 segments for 2500-3100w text)

**Scholarly function taxonomy (16 types):**

| Function | Description | Arabic marker examples |
|----------|-------------|----------------------|
| definition | Term definition with explanation | تعريف، معنى، هو |
| rule_statement | Legal ruling or grammatical rule | يجب، يحرم، لا يجوز |
| evidence_quran | Quranic citation with introduction | قال تعالى، لقوله تعالى |
| evidence_hadith | Hadith with chain or reference | روى، عن النبي صلى الله عليه وسلم |
| evidence_ijma | Consensus citation | أجمع العلماء، بالإجماع |
| evidence_qiyas | Analogical reasoning | قياسا على، بالقياس |
| evidence_rational | Rational/logical argument | لأن، والعلة |
| opinion_statement | Scholar's position | قال أبو حنيفة، ذهب الشافعي |
| refutation | Counter-argument | ورد عليه بأن، واعترض |
| example | Illustrative example | نحو، مثال، كقولك |
| condition_exception | Conditional or exception to a rule | إلا، ما لم، بشرط |
| cross_reference | Reference to another section/work | كما تقدم، انظر |
| narration | Historical narration or isnad | روي أن، عن فلان |
| editorial_note | Editor's or commentator's insertion | قال المحقق، في بعض النسخ |
| structural_transition | Chapter heading, basmala, transition | باب، فصل، بسم الله |
| unclassified | Cannot determine function | — |

This taxonomy is from the experiment and covers all segment types observed in 23 divisions. It replaces the old atomization SPEC's 7 structural types + 16 scholarly functions with a single flat classification.

**Segment boundary rules** (from old atomization SPEC §4.A.2, adapted):
- An isnad chain + its matn = one segment
- A position marker (قال X) + the stated position = one segment
- Each Quran citation with its introduction = one segment
- Consecutive related sentences may form one segment if they serve the same function

**Coverage requirement:** Union of all segment word ranges must cover the full assembled text. No gaps, no overlaps.

#### §5.3 — Phase 2b: Teaching Unit Grouping

- Input: AssembledChunk.assembled_text + ClassifiedSegment[]
- Output: TeachingUnit[] covering all segments
- LLM prompt: APPROACH_B_GROUP_SYSTEM (specified in full — from experiment, adapted for production)
- Response schema: ExtractionResult (Pydantic model, specified in full)
- Model: anthropic/claude-opus-4.6 via OpenRouter
- Temperature: 0
- MAX_TOKENS: 16384

**Grouping rules:**
- A position (opinion_statement) + its evidence + counter-evidence + conclusion = one unit
- A definition + its examples = one unit
- A hadith + its chain + commentary = one unit (fiqh sharh pattern)
- Never group unrelated content (two different مسائل) into one unit
- Each unit evaluated for self-containment per §3

**Over-segmentation management** (addresses evaluation finding C-3 and review finding F14):
- Minimum teaching unit size: [TO BE CALIBRATED — design question, not pre-decided]
- B's over-segmentation correlates with structural repetition (e.g., hadith-benefits pattern produces 1.71x at 3111w) not just length
- The SPEC defines the concern and the measurement; the threshold is calibrated during build evaluation

#### §5.4 — Coverage Verification

- V-P2-1: Union of all TeachingUnit word ranges covers all segments
- V-P2-2: No TeachingUnit spans more than one AssembledChunk (D-011)
- V-P2-3: Every segment is assigned to exactly one TeachingUnit
- V-P2-4: Every TeachingUnit has at least one segment
- V-P2-5: TeachingUnit word ranges are monotonically increasing (no out-of-order grouping)

#### §5.5 — Operational Constraints

- All LLM calls through OpenRouter (api_key from env, model string: anthropic/claude-opus-4.6)
- MAX_TOKENS scaling: 8192 default, 32768 for chunks >2000 words (empirically validated). Chunks >4000 words: scaling TBD during build — 32768 may suffice given segment-count growth is sub-linear, but must be tested
- Retry policy: 2 retries with exponential backoff
- Rate limiting: respect OpenRouter rate limits
- Cost tracking: log input/output tokens per call for monitoring (not a constraint, just telemetry)
- Timeout: 120 seconds per call

**Dependencies:** §2.3 (ClassifiedSegment, TeachingUnit definitions), §3 (self-containment standard), §4 (AssembledChunk input).

**Estimated length:** ~300 lines.

---

### §6 — Domain-Specific Processing Rules

**What it covers:** Cross-cutting rules that modify behavior across phases for specific scholarly text patterns. This preserves the old excerpting SPEC's excellent domain design (§4.A.2–§4.A.7) in a new architectural context.

**Source material:** Old excerpting SPEC §4.A.2–§4.A.7, old passaging SPEC §4.A.4–§4.A.9, old atomization SPEC §4.A.6–§4.A.7.

#### §6.1 — Decontextualization Prevention

From old excerpting SPEC §4.A.2. The highest-risk failure mode in the engine: extracting a fragment that looks complete but is actually responding to or dependent on something outside the excerpt.

Rules that Phase 2b must enforce:
- A reported position (قال أبو حنيفة...) and its refutation (ورد عليه بأن...) belong in the same teaching unit
- A question and its answer belong together
- A condition and its exception (rule + إلا clause) belong together
- Evidence cited for a ruling must stay with the ruling
- A counter-argument must include enough of the original argument to be understood

Phase 3 responsibility: when Phase 2b marks self_contained=false, Phase 3 adds context_hint explaining what's missing.

#### §6.2 — Multi-Layer Text Handling

From old excerpting SPEC §4.A.3 and old atomization SPEC §4.A.6. How to handle sources where matn and sharh (or hashiyah) are interleaved.

Phase 1 responsibility: text_layers are rebased to assembled-text offsets (§4.6).
Phase 2 responsibility: LLM sees the interleaved text and classifies segments. The text_layers metadata is NOT passed to the LLM — the LLM classifies based on content, not markup.
Phase 3 responsibility: for each teaching unit, determine which author(s) are being excerpted based on text_layer overlap. Attribution rules:
- If >80% of the unit's character range falls within one layer, attribute to that layer's author
- If mixed, attribute to the sharh/hashiyah author (they are the one doing the teaching; the matn is being quoted)
- If uncertain, flag for human review

T-2 (Attribution Error) defense: wrong author attribution is a knowledge integrity violation. Multi-model consensus on attribution decisions where layers are mixed.

#### §6.3 — Evidence and Hadith Handling

From old excerpting SPEC §4.A.4. Fiqh and hadith texts have specific patterns that affect segmentation and self-containment.

Phase 2a recognizes: evidence_quran, evidence_hadith, evidence_ijma, evidence_qiyas, evidence_rational as segment types.
Phase 2b groups evidence with the ruling it supports.
Phase 3 extracts: for evidence_hadith segments, attempt to identify collection and number (using structured patterns). For evidence_quran, identify surah and ayah.

Pattern (from Taysir experiment): hadith commentary often follows الحديث → الغريب → المعنى الإجمالي → ما يستفاد pattern. Phase 2b should group these as one teaching unit when they concern the same hadith. The experiment showed both A and B correctly handle this.

#### §6.4 — Implicit Reference Resolution

From old excerpting SPEC §4.A.5. When text refers to something not present (كما تقدم, المذكور آنفا), the reference must be flagged.

Phase 2b: mark self_contained=false if a teaching unit depends on an implicit reference that is not resolved within the unit.
Phase 3: attempt to resolve the reference:
- If the reference points to another division in the same source, add a cross_reference field
- If the reference cannot be resolved, add to self_containment_notes

This is a PARTIAL self-containment case (§3): the excerpt teaches something, but full understanding requires following the reference.

#### §6.5 — Verse-Commentary (نظم) Handling

From old excerpting SPEC §4.A.7, old passaging SPEC §4.A.5 and §4.A.9. How verse-commentary texts (like Ibn Aqil on Alfiyyah) are processed.

Experiment finding: the LLM correctly keeps verse + commentary together as teaching units without explicit verse identification. The ألفية verses function as natural topic delimiters.

Phase 1 responsibility: no special handling needed (text assembly works the same for verse-commentary). Verse_info from content units is passed through for reference but not used for splitting.
Phase 2 responsibility: the verse-commentary pattern is handled naturally by the LLM's topical coherence detection. No special prompting needed (validated in 6/6 verse-commentary divisions).
DEFERRED: explicit verse-commentary alignment (Phase 1 preprocessor that identifies verse lines and ensures they're grouped with their commentary). This is a quality optimization, not mandatory (evaluation C-5).

#### §6.6 — Q&A and Masala-Format Handling

From old passaging SPEC §4.A.6 and §4.A.7.

Phase 1 responsibility: assembled text preserves structural markers (مسألة numbers, سؤال/فأجاب markers, أولا/ثانيا ordinals).
Phase 2 responsibility: the LLM correctly identifies Q&A pairs and masala blocks as self-contained units (validated in 3/3 experiment divisions — ext_39, ext_46).

No special handling needed beyond preserving structural markers in Phase 1 assembly.

**Dependencies:** §3 (self-containment standard), §4 (Phase 1), §5 (Phase 2), §7 (Phase 3 enrichment).

**Estimated length:** ~200 lines.

---

### §7 — Phase 3: Metadata Enrichment

**What it covers:** Adding semantic metadata to teaching units to produce ExcerptRecords. Mix of deterministic extraction and LLM inference.

**Source material:** Old excerpting SPEC §4.A.1 Phase 3, old excerpting SPEC metadata fields, `KNOWLEDGE_INTEGRITY.md`.

#### §7.1 — Deterministic Metadata Assembly

No LLM needed:
- Author attribution from text_layers (§6.2 rules)
- Content type aggregation from content_flags
- Physical page range from assembly_metadata
- Evidence reference collection (Quran ayah numbers, hadith markers — pattern-matched)
- Division path (heading hierarchy from manifest)
- Footnote subsetting (only footnotes whose ref_markers appear in the excerpt's text)

#### §7.2 — LLM-Driven Metadata

Requires LLM inference:
- Topic classification: 1-3 topic keywords for taxonomy placement
- School attribution: which madhhab or scholarly school the excerpt represents (when identifiable)
- Quoted scholar resolution: when the excerpt quotes another scholar (قال X), identify X
- Implicit reference resolution (§6.4)
- Terminology variant detection: alternative Arabic terms for the same concept

Model: anthropic/claude-opus-4.6 via OpenRouter. Temperature: 0.

#### §7.3 — Consensus and Human Gates

From `KNOWLEDGE_INTEGRITY.md`:
- Multi-model consensus on: self-containment evaluation (Phase 2b), school attribution, author attribution for mixed-layer excerpts
- Human gate triggers: DEPENDENT self-containment, attribution confidence <0.7, school attribution disagrees between models
- Gate queue: flagged excerpts written to `library/sources/{source_id}/excerpts/gate_queue.jsonl` for owner review

**Dependencies:** §2.2 (output contract), §3 (self-containment standard), §5 (TeachingUnit input), §6 (domain rules).

**Estimated length:** ~150 lines.

---

### §8 — Error Handling and Configuration

**What it covers:** Error codes, recovery strategies, configuration parameters.

**Source material:** Old passaging SPEC §7-§8, old excerpting SPEC §7-§8, normalization engine error code patterns.

#### §8.1 — Error Codes

Following the KR error code convention (engine prefix + category + number):
- EX-A-xxx: Phase 1 errors (assembly failures, merge conflicts)
- EX-C-xxx: Phase 2 errors (LLM call failures, schema validation errors, coverage violations)
- EX-M-xxx: Phase 3 errors (metadata extraction failures, consensus disagreements)
- EX-V-xxx: Validation errors (invariant violations)
- EX-G-xxx: Gate triggers (human review required)

Every error loud. No silent data loss. No silent defaults.

#### §8.2 — Recovery Strategies

- LLM call failure: retry 2x, then emit EX-C-001 and skip chunk (flag for re-processing)
- Schema validation failure: retry with simplified prompt, then emit EX-C-002 and flag
- Coverage violation: emit EX-V-001, attempt repair (merge uncovered ranges into nearest unit), flag if repair fails
- Phase 1 assembly failure: emit EX-A-001, skip division, continue with remaining divisions

#### §8.3 — Configuration

- Phase 1 thresholds: TINY_DIVISION_WORDS (default 50), OVERSIZED_DIVISION_WORDS (default 5000)
- Phase 2 parameters: MODEL, TEMPERATURE, MAX_TOKENS scaling table, RETRY_COUNT, TIMEOUT_SECONDS
- Phase 3 parameters: CONSENSUS_MODEL_COUNT (default 2), ATTRIBUTION_CONFIDENCE_THRESHOLD (default 0.7)
- Human gate parameters: GATE_ON_DEPENDENT (default true), GATE_ON_LOW_ATTRIBUTION (default true)

**Dependencies:** All processing sections (§4-§7).

**Estimated length:** ~120 lines.

---

### §9 — Deferred Capabilities

**What it covers:** All §4.B content from all three old SPECs, clearly separated from core. Extension hooks defined but not implemented.

**Source material:** Old passaging SPEC §4.B, old atomization SPEC §4.B, old excerpting SPEC §4.B.

**Key deferred capabilities (with source):**

| Capability | Source | Extension Hook |
|-----------|--------|---------------|
| Argumentative discourse mapping | excerpting §4.B.1 | discourse_flow field on ContentUnit |
| Cross-source semantic deduplication | excerpting §4.B.2 | excerpt fingerprint field |
| Scholarly argument completeness analysis | excerpting §4.B.3 | argument_completeness field |
| Mas'ala boundary detection | excerpting §4.B.4 | structural_markers in ContentUnit |
| Evidence chain reconstruction | excerpting §4.B.5 | evidence_refs in ExcerptRecord |
| Cross-excerpt dialogue detection | excerpting §4.B.6 | dialogue_links field |
| Self-containment repair suggestions | excerpting §4.B.7 | repair_suggestion field |
| Cross-source textual resonance | excerpting §4.B.8 | resonance_links field |
| Verse-commentary explicit alignment | evaluation C-5 | verse_info in ContentUnit |
| Rhetorical structure analysis | atomization §4.B.1 | discourse_flow segments |
| Atom-level semantic fingerprinting | atomization §4.B.5 | fingerprint field |
| Scholarly attribution chain | atomization §4.B.4 | attribution_chain field |
| Format-specific passaging strategies | passaging §4.A.5–§4.A.9 (advanced) | structural_format field |
| Completeness forecast | passaging §4.B.8 | forecast field |

Each deferred capability has an extension hook in the data model (nullable field, empty list, or config flag) so it can be added without schema migration.

**Estimated length:** ~100 lines (table + hook descriptions, not full specifications).

---

### §10 — Test Requirements

**What it covers:** What must be tested, with what data, at what granularity. Grounded in real fixtures, not theoretical cases.

**Source material:** Old excerpting SPEC §10, old atomization SPEC §5, normalization engine test patterns, experiment fixtures.

#### §10.1 — Phase 1 Unit Tests

- Assembly: verify cross-page joining with known BC types
- Merging: verify tiny divisions are merged correctly
- Splitting: verify oversized divisions are split at structural markers
- Rebasing: verify text_layer offsets after assembly
- Validation: verify all V-P1 checks

Test data: existing normalization test fixtures + experiment packages.

#### §10.2 — Phase 2 Integration Tests

- Classification: verify segment coverage on known divisions
- Grouping: verify teaching unit boundaries against experiment baseline
- Self-containment: verify FULL/PARTIAL/DEPENDENT assignment

Test data: experiment divisions (13 from format diversity + 10 from original) with known-good outputs as regression baselines.

#### §10.3 — Adversarial Test Cases

From old excerpting SPEC §10, adapted to new architecture:
- ADV-E-01: Dangling refutation (ورد عليه بأن without the position being refuted)
- ADV-E-02: Implicit reference chain (كما تقدم → another كما تقدم → eventually resolves)
- ADV-E-03: Multi-layer boundary (matn verse ends mid-sharh paragraph)
- ADV-E-04: Decontextualized evidence (hadith cited without its ruling)
- ADV-E-05: Mixed-attribution unit (both matn and sharh in one teaching unit)
- ADV-E-06: Empty division (0 content units)
- ADV-E-07: Single-sentence division (<10 words)
- ADV-E-08: Massive division (>10000 words, needs splitting)
- ADV-E-09: Overlapping LLM segment ranges
- ADV-E-10: LLM produces 0 segments (empty classification)

More adversarial cases to be added from old SPEC §10 during section writing.

#### §10.4 — Cross-Engine Contract Tests

- Verify ExcerptRecord validates against output schema
- Verify every excerpt's source_id exists in normalization output
- Verify div_id references match manifest division_tree
- Verify text_layers in excerpt are a valid subset of normalization text_layers
- Verify no field from normalization is silently dropped (D-023)

#### §10.5 — Evaluation Methodology (C-7 Mitigation)

- Same-model evaluation bias: Opus 4.6 both produces and evaluates excerpts. The SPEC should define structural mitigations:
  - Mechanical verification: coverage checks, schema validation, word-count verification (model-independent)
  - Known-boundary test set: divisions with architect-determined correct boundaries, checked automatically
  - Cross-model spot checks: use a different model for 10% of self-containment evaluations during the 30-book probe
  - Owner spot-checks: domain-level quality checks that are model-independent

**Dependencies:** All processing sections.

**Estimated length:** ~150 lines.

---

## Source Material Mapping

Every section of every old SPEC mapped to its new location or marked as excluded.

### Old Passaging SPEC → New Location

| Old Section | Content | New Location | Notes |
|------------|---------|-------------|-------|
| §1 Purpose | Passaging engine scope | §1 (absorbed into purpose) | Rewritten for new scope |
| §2 Input | PassageInput schema | §2.1 (replaced by normalization contracts) | Old schema discarded |
| §3 Output | PassageRecord schema | §2.3 AssembledChunk | Replaces passages with chunks |
| §4.A.1 Processing overview | Pipeline steps | §4.1 | Adapted |
| §4.A.2 Cross-page assembly | BC-based joining | §4.3 | Directly absorbed |
| §4.A.3 Strategy selection | Format → strategy map | §4.1 + §6.5/§6.6 | Format strategies in domain rules |
| §4.A.4 Prose passaging | Division-guided splitting | §4.4 + §4.5 | Merge/split logic |
| §4.A.5 Verse passaging | Verse-group logic | §6.5 (deferred) | Evaluation C-5: not mandatory |
| §4.A.6 Q&A passaging | Q&A pair logic | §6.6 | Simplified: LLM handles it |
| §4.A.7 Masala passaging | Masala block logic | §6.6 | Simplified: LLM handles it |
| §4.A.8 Dictionary passaging | Entry-boundary logic | §9 (deferred) | Rare format, defer |
| §4.A.9 Commentary passaging | Commentary-unit logic | §6.5 | Absorbed into verse-commentary |
| §4.A.10 Validation | Self-validation checks | §4.9 | Adapted for chunks |
| §4.B all | Transformative capabilities | §9 (deferred) | All deferred |
| §5 Validation | Quality standards | §3 + §10 | Split: standard + tests |
| §6 Consensus | Multi-model consensus | §7.3 | Moved to Phase 3 |
| §7 Error handling | Error codes | §8 | Adapted |
| §8 Configuration | Config params | §8.3 | Adapted |
| §10 Test requirements | Test cases | §10.1 | Phase 1 tests |

### Old Atomization SPEC → New Location

| Old Section | Content | New Location | Notes |
|------------|---------|-------------|-------|
| §1 Purpose | Atomization scope | §1 (absorbed) | Rewritten |
| §2 Input | Passage stream schema | Discarded | Passages don't exist |
| §3 Output | Atom schema | §2.3 ClassifiedSegment | Simplified from atoms |
| §4.A.1 Processing model | Atom detection pipeline | §5.1 | Adapted for segments |
| §4.A.2 Atom boundary rules | Boundary logic | §5.2 segment boundary rules | Adapted |
| §4.A.3 Atom type taxonomy | 7 structural + 16 function | §5.2 function taxonomy | Unified 16-type flat taxonomy |
| §4.A.4 Rule-based pre-detection | Marker-based detection | §5.2 (LLM does it all) | Replaced by LLM classification |
| §4.A.5 LLM-driven classification | LLM classification spec | §5.2 | Core of Phase 2a |
| §4.A.6 Multi-layer attribution | Layer-aware classification | §6.2 | Domain rule |
| §4.A.7 Format-specific atomization | Per-format rules | §6.5 + §6.6 | Domain rules |
| §4.A.8 Character offset integrity | Offset validation | §5.4 coverage verification | Adapted for word offsets |
| §4.A.9 Footnote atomization | Footnote handling | §4.7 + §7.1 | Split: aggregation + metadata |
| §4.A.10 Self-validation | Validation checks | §5.4 | Phase 2 validation |
| §4.B all | Transformative capabilities | §9 (deferred) | All deferred |
| §5 Validation | Adversarial scenarios | §10.3 | Test cases |
| §6 Consensus | Multi-model consensus | §7.3 | Moved to Phase 3 |
| §7 Error handling | Error codes | §8 | Adapted |

### Old Excerpting SPEC → New Location

| Old Section | Content | New Location | Notes |
|------------|---------|-------------|-------|
| §1 Purpose | Excerpting scope | §1 | Rewritten for absorbed architecture |
| §2 Input | Atom stream schema | Discarded | Atoms don't exist as input |
| §3 Output | ExcerptRecord schema | §2.2 | Updated: div_id replaces passage_id |
| §4.A.1 Three-phase pipeline | Processing model | §4/§5/§7 overview | Split across three phases |
| §4.A.2 Decontextualization | Prevention rules | §6.1 | Domain rule, cross-cutting |
| §4.A.3 Multi-layer handling | Layer attribution | §6.2 | Domain rule |
| §4.A.4 Evidence/hadith | Evidence handling | §6.3 | Domain rule |
| §4.A.5 Implicit references | Reference resolution | §6.4 | Domain rule |
| §4.A.6 Cross-topic handling | §5.3 rules | §3 (self-containment) | Formalized as quality standard |
| §4.A.7 Verse format | نظم handling | §6.5 | Domain rule |
| §4.B.1–§4.B.8 | All deferred capabilities | §9 | All deferred |
| §5 Validation | Layer 1/2/3 quality | §3 + §7.3 | Split: standard + gates |
| §6 Consensus | Multi-model consensus | §7.3 | Moved |
| §7 Error handling | Error codes | §8 | Adapted |
| §8 Configuration | Config params | §8.3 | Adapted |
| §9 Implementation state | ABD-era code refs | Discarded | Finding F5: misleading |
| §10 Test requirements | Adversarial cases | §10.3 | Adapted for new architecture |

---

## Review Findings Resolution Map

How each of the 16 review findings is addressed:

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1: Input contract describes nonexistent data | CRITICAL | §2.1 defines real input from normalization contracts.py |
| F2: Self-containment subsections don't exist | CRITICAL | §3 is the formal self-containment standard |
| F10: Atom concept unspecified | CRITICAL | §2.3 defines ClassifiedSegment + TeachingUnit (not atoms) |
| F3: §4.B references nonexistent atomization | HIGH | §9 collects all deferred capabilities with correct hooks |
| F4: D-011 uses old passage definition | HIGH | §1 defines D-011 as division/chunk containment |
| F5: ABD-era code references | HIGH | All ABD references removed; no §9 "implementation state" |
| F11: Experiment approach doesn't match SPEC phases | HIGH | §5 specifies the experiment's validated approach directly |
| F12: MAX_TOKENS constraint not captured | HIGH | §5.5 specifies MAX_TOKENS scaling table |
| F13: Passaging phase unspecified | HIGH | §4 specifies full Phase 1 deterministic preprocessing |
| F6: contracts.py has 8 unimplemented models | MEDIUM | §9 lists deferred capabilities; contracts.py updated in Step 3 |
| F7: No formal LLM prompt specification | MEDIUM | §5.2 and §5.3 include full prompt text and response schemas |
| F8: 5 previously flagged concerns | MEDIUM | Addressed via new architecture (atom_ids gone, contracts updated) |
| F14: Over-segmentation on longer texts | MEDIUM | §5.3 defines the concern and measurement; threshold calibrated in build |
| F15: D-023 wrong references | MEDIUM | §2.1 and §2.2 use correct field names (div_id, unit_index) |
| F9: CLAUDE.md stale | LOW | Already fixed (commit 5b71749) |
| F16: passage_id required field | LOW | Replaced by div_id in §2.2 |

---

## Section Writing Order (Dependency-Driven)

1. **§2.3** Internal Data Model — everything else references these types
2. **§2.1** Input Contract — what we receive
3. **§3** Self-Containment Standard — the quality criterion
4. **§4** Phase 1 — deterministic preprocessing (read old passaging SPEC §4.A.2–§4.A.10)
5. **§5** Phase 2 — LLM extraction (read old atomization SPEC §4.A.1–§4.A.5, experiment run_tests.py)
6. **§6** Domain rules — cross-cutting (read old excerpting SPEC §4.A.2–§4.A.7)
7. **§7** Phase 3 — metadata enrichment (read old excerpting SPEC §4.A.1 Phase 3)
8. **§2.2** Output Contract — now fully specified by what Phase 3 produces
9. **§8** Error handling and configuration
10. **§1** Purpose and Scope — written last, after all content is known
11. **§9** Deferred capabilities
12. **§10** Test requirements

**Context management:** Read old SPEC sections on-demand per the writing order above. Do NOT front-load all 400KB. Start a new chat after prompt 6-7.

---

## Estimated Total Length

| Section | Est. Lines |
|---------|-----------|
| §1 Purpose | 80 |
| §2 Contracts + Data Model | 370 |
| §3 Self-Containment | 100 |
| §4 Phase 1 | 250 |
| §5 Phase 2 | 300 |
| §6 Domain Rules | 200 |
| §7 Phase 3 | 150 |
| §8 Error + Config | 120 |
| §9 Deferred | 100 |
| §10 Tests | 150 |
| **Total** | **~1820** |

This is larger than the old 1038-line SPEC because it absorbs two additional engines. The increase is proportional to the absorbed content.
