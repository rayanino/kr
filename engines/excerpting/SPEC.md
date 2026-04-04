# Excerpting Engine — SPEC

**Engine:** Excerpting (محرك الاقتباس)
**Version:** 2.0.0
**Date:** 2026-03-23
**Author:** Claude Chat (Architect)
**Status:** COMPLETE — 12 sections, 2343 lines. Ready for kr-integrity audit and contracts.py update.

**Supersedes:** `reference/archive/abd_code/excerpting/SPEC_old_original.md` (1038 lines, 7-engine architecture — BLOCKED)
and `reference/archive/abd_code/excerpting/SPEC_old_blocked.md` (868 lines, rewrite attempt — BLOCKED, 16 findings)

**Governing documents:** `KNOWLEDGE_INTEGRITY.md`, `SPEC_OUTLINE.md`, `ARCHITECTURE_DECISION.md`

---

## §1 — Purpose and Scope

### §1.1 — What This Engine Does

The excerpting engine transforms normalized scholarly text into self-contained, attributed teaching units — the building blocks of the knowledge library. A teaching unit is the smallest segment of text from which a student can learn a complete scholarly thought: a definition, a ruling with its evidence, a position with its refutation, a grammatical rule with its example.

**Pipeline position:**

```
Source ✅ → Normalization ✅ → Excerpting → Taxonomy → Synthesis
```

The excerpting engine receives a `NormalizedPackage` (frozen source text with structure, metadata, and text layers) and produces a stream of `ExcerptRecord` objects (self-contained excerpts with full attribution, topic keywords, evidence references, and self-containment evaluation). The taxonomy engine consumes these records to place excerpts in the knowledge tree. The synthesis engine consumes placed excerpts to produce encyclopedic entries.

### §1.1b — Foundational Principles (Owner Hardening, 2026-04-04)

These principles were extracted, challenged, and hardened from owner Q&A responses F1–F8 during the foundations hardening session. Each principle has been pressure-tested against the codebase, challenged by Codex and Gemini coworkers, and empirically validated where possible. They constrain all implementation decisions across all three phases.

**FP-1 (Explained-explanation unity, EE-1):** An explained object and its immediately following explanation form one teaching unit by default. See §6.4b for the full rule, scope, and exceptions.

**FP-2 (Context resolution hierarchy, NC-1):** When an excerpt needs context, the hierarchy is: (1) keep original context via structural unity (EE-1), (2) source surroundings — the reader accesses the actual frozen source pages, (3) generated context_hint — supplementary guidance pointing into the surroundings. See §3 PARTIAL definition for the full hierarchy. **Anti-rescue prohibition:** surrounding context and generated notes are diagnostic tools for ENGINEERING analysis — they must never silently "rescue" the owner-facing verdict on a defective excerpt. If an excerpt requires surrounding context to be understood, it is PARTIAL or DEPENDENT, not FULL — regardless of how readable it appears when context is available to the evaluator. Generated summary notes must never replace source-preserving context where source integrity matters: the note is a secondary aid, not a primary context mechanism. Help layers (comparisons, summaries, study-friendly structuring) sit BESIDE the preserved source as parallel layers — they never overwrite it (owner F4, F5, F6; Batch 1 hardening session 2).

**FP-3 (Linking-word intelligence):** Linking words (pronouns, demonstratives, opening conjunctions) must be evaluated intelligently, not flagged blindly. See the expanded C-SC-2 for specific patterns. Opening و does not automatically indicate a dangling reference.

**FP-4 (Taxonomy independence):** The excerpting engine's output must be identical regardless of the taxonomy tree's state. Excerpting is source-driven, not tree-driven. An overgranulated, undergranulated, or perfectly granulated taxonomy tree must all receive the same excerpts. Excerpting-bias — where boundary decisions are influenced by downstream placement — is a top failure mode (owner F8, 2026-04-04).

**FP-5 (Knowledge corruption is the worst failure):** One corrupted excerpt poisons the reader's trust in the entire library. Silent corruption is worse than visible failure. Always assume an excerpt is wrongfully excerpted until proven otherwise. The engine must fail loud — never silently produce an excerpt that looks correct but misrepresents the source. **Cascading trust collapse:** a wrong excerpt invalidates the entire book it came from (other excerpts from the same source cannot be trusted) → the excerpting engine itself becomes suspect → the owner's entire knowledge base requires re-evaluation. This cascade means the blast radius of one silent error is not one excerpt but the full corpus processed by the same prompt/model/configuration. When a content error is confirmed, the engine must immediately assess blast radius: which other excerpts from the same source were processed in the same batch, with the same prompt, and are therefore at risk (owner F7, F8, 2026-04-04; Batch 1 hardening session 2).

**FP-6 (Rules + intelligence):** The more rules, examples, and edge cases we define, the more accurate the engine gets. But rules alone are not enough — the LLM must also apply intelligent reasoning for cases not covered by explicit rules. New scholar methodologies will appear that no predefined rule anticipates. The engine must have uncertainty gates for cases where the system is not confident (owner F5, 2026-04-04).

**FP-7 (Fetched proof vs book-preserved proof):** Book-preserved proofs (as scholars cite them) and authoritatively fetched proofs (from primary sources like Sahih al-Bukhari) are two distinct layers that both belong in the library. The book-preserved proof is for analyzing how the scholar handled it. The fetched proof is for memorization and direct study. Neither replaces the other (owner F5, F6, 2026-04-04). Implementation of the fetched-proof layer is deferred to a cross-engine design phase.

**FP-8 (Khilaf-tarjih distinction):** The unbiased mapping of scholarly disagreement (تحرير الخلاف) and the scholar's biased conclusion (ترجيح) are distinct scholarly functions. Full resolution is deferred to questionnaire items K-1 through K-3. See §6.1 design note.

**FP-9 (Overgranulation is worse than undergranulation):** An overgranulated taxonomy tree is more dangerous than an undergranulated one because reassembling fragments is harder than splitting a coarse unit. This constrains both excerpting granularity and taxonomy placement (owner F8, 2026-04-04).

**FP-10 (Source surroundings vision):** Every excerpt should be accompanied by access to its surrounding pages from the original source — a "window into the source" rather than a detached fragment. The excerpting engine produces location metadata (source_id, div_id, physical_pages) for this purpose. When `physical_pages` is null (some sources lack page metadata), the surrounding-text display falls back to division-based navigation (same div_id, adjacent chunk_index values). The display mechanism is a synthesis/UI responsibility (owner live Q&A, 2026-04-04).

**FP-11 (Sanad-matn awareness):** In hadith-containing texts, the chain of narration (isnad/sanad) and the narrated text (matn) have different scholarly functions. In fiqh and sharh texts, the sanad is contextual metadata for the matn — it establishes the hadith's route but is not the primary study object. In hadith sciences (mustalah al-hadith / 'ilm al-rijal), the sanad IS the study object. The engine must not treat sanad chains as noise to be stripped — they are preserved in the excerpt and classified appropriately. Long sanad chains in fiqh texts do not disqualify an excerpt; they are part of the source's scholarly apparatus (Gemini review, 2026-04-04).

**FP-12 (Implied dependency detection — taqdir):** Arabic text frequently operates on taqdir (implied/omitted words). An excerpt may appear syntactically complete while depending on an implied subject, object, or referent from a previous paragraph. C-SC-2 (Reference Resolution) must account for INVISIBLE syntactic anchors, not only visible linking words. Example: "قال: يجوز" — the subject of "قال" is implied from prior context; if the reader cannot determine who "said" it, the excerpt is not self-contained even though there is no visible pronoun or demonstrative. The LLM must reason about implied dependencies during self-containment evaluation (Gemini review, 2026-04-04).

**FP-13 (Principle conflict precedence, from DR adversarial review 2026-04-04):** When foundational principles conflict in a real text (e.g., EE-1 unity vs FP-9 anti-overgranulation), apply this precedence stack:
1. **Speaker-role correctness** — who is endorsing what. Misattribution is the most dangerous silent failure.
2. **Dialogue completeness** — objection + response, position + refutation. Omission flips meaning.
3. **Textual/grammatical integrity** — avoid "bleeding" Arabic fragments that break mid-sentence.
4. **Self-containment for the target reader** — the unit teaches a complete thought.
5. **Granularity for leaf-level comparison** — lowest priority; optimize via post-grouping merge, not boundary splitting.

This precedence stack resolves the FP-1 (unity) vs FP-9 (anti-overgranulation) tension: unity wins when splitting would break attribution or dialogue, but granularity can be optimized post-grouping through MV-1 (minimum viability merge).

**FP-14 (Speaker-role inversion is the #1 blind spot, from DR adversarial review 2026-04-04):** Excerpts containing objection/response patterns (فإن قيل / قلنا, سؤال / الجواب, اعترض / وأجيب) MUST include both the objection AND the answer. An excerpt that teaches the opponent's view as the author's view is the most dangerous silent failure because it is confident, self-contained, and exactly wrong. The existing DP-1 (position + refutation) covers named-scholar reports but does NOT fully cover anonymous dialectical structures (فإن قيل without a named scholar). The Phase 2b prompt already includes Q&A coupling (DP-2), but the adversarial risk of anonymous objection structures warrants this explicit principle.

**FP-18 (Three-level excerpt quality distinction, from F1 canon PR-001):** Independent understandability and direct study-readiness are distinct levels. A teaching unit can carry usable theory while still failing direct study-readiness. The canon defines three quality levels for excerpts: (1) *excerpt candidate* — bounded unit with one primary study object or tightly bound cluster; (2) *acceptable excerpt* — no essential backward hunting for frame, function, or referent; (3) *directly study-ready excerpt* — acceptable + clean entry frame + no deceptive omission + no avoidable overload. The current self-containment system (FULL/PARTIAL/DEPENDENT) maps approximately: FULL ≈ acceptable or study-ready (conflated), PARTIAL ≈ below acceptable but still coherent, DEPENDENT ≈ not an excerpt. Splitting FULL into ACCEPTABLE and STUDY_READY is a **deferred contract enhancement** — the distinction is real (confirmed by Gemini CLI with concrete Arabic examples: unresolved «وهو» and ordinal «الشرط الثالث» both produce FULL units that are NOT study-ready) but the operational threshold is not yet calibrated. When implemented, this should be a separate `study_readiness_grade` field on UnitEnrichment/ExcerptRecord, not a change to the SelfContainmentLevel enum, to preserve backward compatibility. The 30-book probe should calibrate the acceptable/study-ready boundary empirically.

**FP-15 (Rhetorical posture detection, from Gemini DR stress test 2026-04-04):** Classical scholars frequently quote opponents' views to refute them (ilzam method), construct hypothetical interlocutors (فإن قيل), or employ sarcasm. The engine must not attribute quoted-to-refute content to the quoting author. This extends FP-14 (speaker-role inversion) to cover non-dialogue rhetorical structures. Critical for: Al-Muhalla (Ibn Hazm), kalam texts, advanced usul. Implementation: Phase 2a classification should tag segments with rhetorical posture (endorsed / quoted-to-refute / hypothetical / ilzam). Deferred to corpus expansion.

**FP-16 (Chunk-split nesting prohibition, from Gemini DR stress test 2026-04-04):** When the dialectical nesting depth is ≥3 levels (e.g., author quoting opponent quoting evidence within a refutation), the Phase 1 chunk-split algorithm MUST NOT cut inside the nested structure. The algorithm must wait until the rhetorical stack unwinds to level 1 (author's own voice) before executing a split. If this requires slightly exceeding the chunk token limit, the forgiving rule applies. Cutting mid-nesting risks the catastrophic failure described in FP-5: a quote from an opponent is attributed to the author. Critical for: Al-Muhalla, dense kalam/usul texts. Implementation: Phase 1 split logic enhancement, deferred to corpus expansion.

**FP-17 (Hub-and-spoke for serial narrations, from Gemini DR stress test 2026-04-04):** When a single explained object (e.g., a Quranic verse) has many independent explanations (e.g., 20 tafsir narrations with full isnads), the engine must NOT force all narrations into one teaching unit. Instead, treat the verse as a hub node. Each chunk of narrations gets the verse text duplicated at its start via NC-1 Tier 3 (context_hint). This satisfies EE-1 (no orphaned explanation) without creating a monstrous over-merged unit. Critical for: Tafsir al-Tabari, hadith collections with multiple asanid per hadith. Implementation: Phase 1 + Phase 2b enhancement, deferred to corpus expansion.

**FP-19 (Omission honesty — anti-deceptive cleanliness, from Batch 1 hardening session 2):** When the engine omits material between two text spans within an excerpt, the omission MUST be visible — the result must never look like uninterrupted source flow. "Deceptive cleanliness" is a named failure mode: a hidden cut that produces syntactically perfect Arabic but semantically inverted meaning. Canonical catastrophe (Gemini adversarial review): cutting al-Ghazali's condemnation of philosophers' views ("وهذا كفر صريح") leaves a sentence that attributes kufr to al-Ghazali himself. Omission markers (e.g., `[...]`) are non-negotiable for any non-contiguous text assembly. This principle applies to Phase 1 (chunk assembly from non-contiguous divisions), Phase 2 (grouping that skips segments), and Phase 3 (any text assembly in enrichment). Contract enforcement of a visible-cut field is **deferred** — the principle constrains behavior now; the contract field will be added when Phase 3 enrichment is hardened (Codex review: adding the field retroactively risks making existing FULL excerpts noncompliant).

**FP-20 (Validation rigor — hard cases over polished paths, from Batch 1 hardening session 2):** Testing and validation must target the HARDEST cases, not merely pass polished easy-path examples. Hollow evaluation that only validates clean inputs is itself a failure (owner F7 NG-009). The five hardest Arabic scholarly text patterns that break naive implementations: (1) the dialectical trap (فإن قيل / قلنا) where opponent views are quoted at length before refutation, (2) pronoun disconnects where referents are pages away, (3) extended digressions (استطراد) spanning unrelated sciences, (4) deferred exceptions (الاستثناء المنفصل) where a critical qualifier appears at the end of a long chapter, (5) nested quotations within quotations (تداخل النقولات) with unclear speaker boundaries. Every validation suite must include adversarial cases from at least categories (1) and (4) (Gemini scholarly review, session 2).

**FP-21 (Severity class distinction — silent corruption vs visible flagged failure, from Batch 1 hardening session 2):** Silent excerpt corruption (wrong meaning, lost attribution, inverted speaker role) and visible flagged failures (gate triggers, review flags, PARTIAL/DEPENDENT self-containment) are fundamentally different severity classes and must be tracked separately. Silent corruption is existential — the owner memorizes wrong knowledge without knowing it. Visible flagged failure is serious but recoverable — the owner or the system sees the flag and can investigate. The engine's error-handling, human-gate triggers, and post-run analysis must distinguish these classes. Conflating them masks the most dangerous errors behind the volume of flagged-but-harmless issues. Concrete per-science examples: in fiqh, dropping a condition (إن لم يجد غيرها) turns a concession into an absolute rule; in hadith, failing to capture a mudraj insertion attributes human commentary to the Prophet ﷺ; in tafsir, dropping an invalidation (وهذا باطل لا يصح) asserts a falsehood as the mufassir's view; in nahw, dropping a grammatical judgment (ولا يجوز القياس عليه) turns a rejected anomaly into a standard rule (Gemini scholarly review, session 2; Codex: rephrase from "misplacement" to "visible flagged failure" since taxonomy placement is excerpting-external per FP-4).

**FP-22 (Anti-covert-excerpter — Phase 3 validator integrity, from Batch 1 hardening session 2):** Phase 3 validation must not reshape excerpt text, span boundaries, or segment grouping to improve taxonomy fit or resolve placement difficulties. A validator that silently adjusts excerpts to fit the tree is a covert second excerpting engine — it reintroduces the taxonomy-bias that FP-4 prohibits. If an excerpt does not fit the current tree, the tree is wrong, not the excerpt. Scope: this prohibition covers `primary_text`, `start_word`/`end_word`, `segment_indices`, and teaching unit composition. Exemption: Phase 3 orphan-footnote handling (V-P3-8) is a completeness fix, not a reshaping — it adds omitted footnote content that the LLM missed, it does not alter boundaries to improve fit (Codex review: absolute "never reshape" breaks V-P3-8; narrowed to text/span/boundary reshaping for taxonomy fit).

### §1.2 — Three-Phase Architecture

The engine operates in three sequential phases:

**Phase 1 — Deterministic Preprocessing (§4):** Assembles content units into processable chunks. Handles cross-page text joining, tiny division merging, oversized division splitting, text layer rebasing, and content flag aggregation. Fully deterministic — no LLM calls. Absorbs the functionality of the former passaging engine.

**Phase 2 — LLM Teaching Unit Extraction (§5):** Classifies text segments by scholarly function (Phase 2a) and groups segments into teaching units with self-containment evaluation (Phase 2b). This is the engine's core intellectual operation — identifying where one scholarly thought ends and another begins. Absorbs the functionality of the former atomization engine.

**Phase 3 — Metadata Enrichment (§7):** Adds attribution, topic keywords, evidence references, school classification, and cross-references to each teaching unit, producing the final `ExcerptRecord`. Uses LLM enrichment with multi-model consensus verification for high-stakes fields (attribution, school).

### §1.3 — Architecture Absorption

This engine absorbs two former engines from the original 7-engine architecture:

**Passaging** (deterministic text chunking) is absorbed as Phase 1. Rationale: 96.8% of Shamela divisions need no splitting; the remaining 3.2% require ~500 lines of deterministic code — not engine-worthy. Full analysis: `experiments/architecture_test/ARCHITECTURE_DECISION.md`.

**Atomization** (LLM segment classification) is absorbed as Phase 2. Rationale: the Architecture C experiment validated that an LLM can identify teaching units directly from division-level text without a separate atom-level intermediate representation. Two-phase (classify-then-group) outperformed single-phase in 10/10 experiment divisions across 5 genres. Full results: `experiments/format_diversity_test/EVALUATION_WORKBOOK.md`.

### §1.4 — D-011: Division Containment

**D-011 constraint:** No excerpt spans a division or chunk boundary. This is the fundamental structural invariant. The LLM sees one chunk at a time and produces teaching units only from that chunk's text. This constraint is STRONGER than the original D-011 (which was passage containment): divisions are the author's own organizational structure, while passages were artificial boundaries.

D-011 is enforced structurally (§5.5.1): the LLM prompt receives one chunk's text, and the grouping response's word offsets are validated against that chunk's boundaries. There is no mechanism by which a teaching unit could span chunks — the constraint is not checked after the fact but made impossible by construction.

### §1.5 — Scope Exclusions

The excerpting engine does NOT:

- **Cross source boundaries.** Each source is excerpted independently. Cross-source operations (deduplication, dialogue detection, resonance) are deferred capabilities (§9).
- **Place excerpts in the taxonomy tree.** The engine produces `excerpt_topic` keywords; the taxonomy engine maps topics to tree positions. Clean engine boundary: excerpting knows content, taxonomy knows structure.
- **Synthesize entries.** The engine produces individual excerpts; the synthesis engine combines excerpts into encyclopedic entries.
- **Modify source text.** The engine reads frozen normalized text. It never writes back to normalization output.
- **Perform cross-division operations.** Each division/chunk is processed independently. Context from adjacent divisions is available for self-containment evaluation (§3) but not for content modification.

### §1.6 — Knowledge Integrity

Every excerpt this engine produces becomes a belief in the owner's mind. A wrong attribution means the owner studies a text believing it was written by the wrong person. A decontextualized refutation means the owner believes a scholar endorses a position he actually rejects. A lost hadith grading means the owner cannot assess the strength of evidence.

The engine defends against the 7 corruption threats defined in `KNOWLEDGE_INTEGRITY.md`:
- T-1 (Silent text corruption): Offset validation (V-P2-1–5), primary text integrity (V-P3-2)
- T-2 (Attribution error): Multi-model consensus (§7.3), human gates (EX-G-001, EX-G-003)
- T-3 (Taxonomic misplacement): Deferred to taxonomy engine; excerpting provides topic keywords only
- T-4 (Context loss): Self-containment standard (§3), decontextualization prevention (§6.1)
- T-5 (Synthesis hallucination): Deferred to synthesis engine
- T-6 (Metadata poisoning): Schema validation (I-ER-1–7), evidence reference integrity (V-P3-6)
- T-7 (Duplication): Excerpt ID uniqueness (V-P3-1), deferred deduplication (DC-02)

---

## §2.3 — Internal Data Model

The excerpting engine transforms a `NormalizedPackage` (from `engines/normalization/contracts.py`) into a stream of `ExcerptRecord` objects. Three intermediate representations flow between the engine's internal phases:

```
NormalizedPackage (input — normalization contracts)
  → Phase 1 (deterministic) → AssembledChunk[]
    → Phase 2a (LLM classify) → ClassifiedSegment[]
      → Phase 2b (LLM group) → TeachingUnit[]
        → Phase 3 (enrich) → ExcerptRecord[] (output — §2.2)
```

Each intermediate is simpler than its successor. Phase 1 output is fully deterministic and independently unit-testable. Phase 2 output is LLM-driven with structural constraints. Phase 3 adds semantic richness. This separation means Phase 1 bugs are caught without any LLM cost, and Phase 2 bugs are isolated from metadata enrichment logic.

**Design decision (Option C — Hybrid):** The experiment (`experiments/architecture_test/run_tests.py`) validated `ClassifiedSegment` and `TeachingUnit` as sufficient intermediate types for LLM extraction. Phase 3 enrichment (attribution, topics, evidence references) is added after extraction, not embedded in the LLM call. This avoids the complexity of the old atomization SPEC's pre-computed relations and bonds, which were never empirically validated.

### §2.3.1 — Enumerations

#### ScholarlyFunction

The 16-type flat taxonomy for segment classification. Validated across 23 divisions in 7 formats (experiments `run_tests.py` and `format_diversity_test`). Replaces the old atomization SPEC's separate 7 structural types + 16 scholarly functions with a single classification.

| Value | Description | Arabic marker examples |
|-------|-------------|----------------------|
| `definition` | Term definition with explanation | تعريف، معنى، حقيقة |
| `rule_statement` | Legal ruling or grammatical rule | يجب، يحرم، لا يجوز، حكمه |
| `evidence_quran` | Quranic citation with introduction | قال تعالى، لقوله تعالى |
| `evidence_hadith` | Hadith with chain or reference | روى، عن النبي ﷺ، أخرجه |
| `evidence_ijma` | Consensus citation | أجمع العلماء، بالإجماع |
| `evidence_qiyas` | Analogical reasoning | قياساً على، بالقياس، والعلة |
| `evidence_rational` | Rational/logical argument | لأن، ولأنه، والدليل العقلي |
| `opinion_statement` | Scholar's named position | قال أبو حنيفة، ذهب الشافعي، وعند مالك |
| `refutation` | Counter-argument or objection | ورد عليه بأن، واعترض، ونوقش |
| `example` | Illustrative example | نحو، مثال ذلك، كقولك، كأن يقول |
| `condition_exception` | Conditional or exception to a rule | إلا، ما لم، بشرط، إن كان |
| `cross_reference` | Reference to another section or work | كما تقدم، انظر، سيأتي |
| `narration` | Historical narration or isnad | روي أن، أخبرنا، حدثنا |
| `editorial_note` | Editor's or commentator's insertion | قال المحقق، في بعض النسخ، كذا في الأصل |
| `structural_transition` | Chapter heading, basmala, transition | باب، فصل، بسم الله الرحمن الرحيم |
| `unclassified` | Cannot determine scholarly function | — |

The Arabic markers listed are non-exhaustive examples to aid human understanding. The LLM classifies based on semantic analysis of the text, not marker matching. Marker-based pre-classification was considered (old atomization SPEC §4.A.4) and rejected: the experiment showed the LLM handles classification reliably without it, and marker-based approaches produce false positives on conjugated Arabic verb forms (normalization engine lesson: `وذهب` matches `وذهبت`/`وذهبوا`).

#### SelfContainmentLevel

The self-containment assessment for a teaching unit. Defined formally in §3; used in the data model here.

| Value | Meaning | Phase 3 action |
|-------|---------|---------------|
| `FULL` | All §3 criteria met. Excerpt stands alone. | No repair needed. |
| `PARTIAL` | Most criteria met, but some context would help. | Phase 3 adds `context_hint`. |
| `DEPENDENT` | Cannot be understood alone. Requires connection to adjacent content. | Flagged for human gate review. |

**Design extension note:** The experiment used a binary `self_contained` boolean. The 3-level system extends this: `PARTIAL` captures cases where the experiment's `self_containment_notes` field was populated but the excerpt was still marked `self_contained=true`. This provides actionable information for Phase 3 repair and human gates. The mapping is: experiment `true` with no notes → `FULL`; experiment `true` with notes → `PARTIAL`; experiment `false` → `DEPENDENT`. Must be validated during build evaluation.

**T-4 defense:** A `DEPENDENT` excerpt reaching the taxonomy engine without its dependency resolved is a knowledge integrity violation — the owner would study an incomplete argument.

### §2.3.2 — AssembledChunk (Phase 1 Output)

One `AssembledChunk` represents a processable unit of text: one leaf division (or a merged/split portion thereof) with all cross-page text assembled into a single continuous string. Phase 1 is fully deterministic — no LLM calls.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `chunk_id` | `str` | yes | Unique identifier. Format: `{div_id}` for unsplit divisions; `{div_id}_chunk_{N}` for split divisions (N is 0-based). |
| `source_id` | `str` | yes | Inherited from manifest. |
| `div_id` | `str` | yes | The leaf division this chunk derives from. Format per normalization: `div_{source_id}_{depth}_{index}`. |
| `div_path` | `list[str]` | yes | Heading hierarchy from root to this division. Each element is the `heading_text` of an ancestor `DivisionNode`, ordered root-first. Example: `["كتاب الصلاة", "باب صفة الصلاة", "فصل في الركوع"]`. |
| `assembled_text` | `str` | yes | The full text of this chunk, assembled from constituent `ContentUnit.primary_text` values joined per boundary continuity rules (§4.3). All diacritics preserved exactly — no Unicode normalization. Footnote reference markers (`⌜N⌝`) preserved inline. |
| `word_count` | `int` | yes | Arabic word count of `assembled_text`. Counts whitespace-delimited tokens containing ≥1 Arabic character (U+0600–U+06FF). Used for merge/split threshold decisions (§4.4, §4.5). |
| `total_tokens` | `int` | yes | Total whitespace-delimited token count: `len(assembled_text.split())`. Includes all tokens (Arabic, numbers, markers). Used as the coordinate space for word offsets in Phase 2. |
| `text_layers` | `list[TextLayerSegment]` | yes | Layer attribution segments rebased to `assembled_text` character offsets (§4.6). Every character in `assembled_text` is covered by exactly one segment. Types from `engines/normalization/contracts.py::TextLayerSegment`. |
| `footnotes` | `list[Footnote]` | yes | All footnotes from constituent content units, deduplicated by `ref_marker`, order preserved. Types from `engines/normalization/contracts.py::Footnote`. |
| `content_flags` | `ContentFlags` | yes | OR-aggregate across all constituent content units. If any unit has `has_verse=true`, the chunk has `has_verse=true`. Type from `engines/normalization/contracts.py::ContentFlags`. |
| `physical_pages` | `list[PhysicalPage]` | yes | Physical page records from all constituent content units, in order. Type from `engines/normalization/contracts.py::PhysicalPage`. |
| `structural_format` | `StructuralFormat` | yes | Inherited from manifest `structural_format`. Type from `engines/normalization/contracts.py::StructuralFormat`. |
| `heading_alignment_ok` | `bool` | yes | Whether the division heading aligns with the assembled text per §4.8 heading alignment filter. `false` flags a potential misalignment for human review. |
| `assembly_metadata` | `AssemblyMetadata` | yes | Provenance record for how this chunk was assembled. See below. |
| `merge_history` | `list[str]` | no | Present only when tiny divisions were merged (§4.4). List of original `div_id` values that were merged to form this chunk. Absent (null) for unmerged chunks. |
| `split_info` | `SplitInfo` | no | Present only when an oversized division was split (§4.5). Absent (null) for unsplit chunks. See below. |

**AssemblyMetadata** (sub-type):

| Field | Type | Description |
|-------|------|-------------|
| `constituent_unit_indices` | `list[int]` | The `unit_index` values of all `ContentUnit` objects that were assembled into this chunk, in order. |
| `join_points` | `list[JoinPoint]` | One entry per page boundary within this chunk. |
| `layer_split_points` | `list[int]` | Character offsets in `assembled_text` where text layer segments were artificially divided by §4.5 splitting. Empty for unsplit chunks. Phase 3 attribution (§7.1 F-DET-3) treats split-induced layer boundaries as non-meaningful — consecutive segments with the same `layer_type` and `author_canonical_id` separated only by a split point are treated as a single attribution span. |
| `footnote_renumber_map` | `dict[str, str] \| null` | When footnote renumbering occurred (§4.7), maps old `ref_marker` → new `ref_marker`. Null when no renumbering was needed. |

**JoinPoint** (sub-type):

| Field | Type | Description |
|-------|------|-------------|
| `after_unit_index` | `int` | The `unit_index` of the page before this join. |
| `before_unit_index` | `int` | The `unit_index` of the page after this join. |
| `boundary_type` | `BoundaryContinuityType` | The boundary continuity type used for joining. Type from normalization contracts. |
| `separator_used` | `str` | The actual separator string inserted: `""` for mid_sentence, `"\n"` for mid_paragraph/mid_argument/unknown, `"\n\n"` for section_break/division_break. |
| `char_offset_in_assembled` | `int` | Character offset in `assembled_text` where this join occurs. |

**SplitInfo** (sub-type):

| Field | Type | Description |
|-------|------|-------------|
| `original_div_id` | `str` | The `div_id` of the division before splitting. |
| `chunk_index` | `int` | 0-based index of this chunk within the split result. |
| `total_chunks` | `int` | Total number of chunks the division was split into. |
| `split_method` | `str` | One of: `"heading_marker"`, `"section_break"`, `"paragraph_break"`, `"sentence_boundary"`. |

**Invariants:**
- I-AC-1: `word_count` equals the count of whitespace-delimited tokens in `assembled_text` that contain ≥1 Arabic character. `total_tokens` equals `len(assembled_text.split())`. Both are computed from `assembled_text` — never set independently.
- I-AC-2: The union of character ranges in `text_layers` exactly covers `[0, len(assembled_text))`. No gaps, no overlaps.
- I-AC-3: Every `ref_marker` in `footnotes` appears in `assembled_text` as `⌜{ref_marker}⌝`.
- I-AC-4: `constituent_unit_indices` is a contiguous ascending sequence. For unmerged, unsplit chunks: it matches the `DivisionNode`'s `[start_unit_index, end_unit_index]` range (inclusive). For merged chunks: it spans the union of all merged divisions' content unit ranges. For split chunks: all chunks from the same split share the same `constituent_unit_indices` (the original division's full range), because splitting occurs on the assembled text, not on content units.
- I-AC-5: If `split_info` is present, `chunk_id` ends with `_chunk_{split_info.chunk_index}`.
- I-AC-6: If `merge_history` is present, it contains ≥2 `div_id` values, and the first element equals `div_id`.
- I-AC-7: `merge_history` and `split_info` are mutually exclusive. A chunk is either merged, split, or neither — never both.

### §2.3.3 — ClassifiedSegment (Phase 2a Output)

One `ClassifiedSegment` represents a contiguous span of text within an `AssembledChunk` that serves a single scholarly function. Produced by the Phase 2a LLM classification call (§5.2).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `segment_index` | `int` | yes | 0-based index within this chunk's classification result. |
| `start_word` | `int` | yes | Start word offset in `assembled_text` (0-based, inclusive). |
| `end_word` | `int` | yes | End word offset in `assembled_text` (0-based, inclusive). |
| `text_snippet` | `str` | yes | First 50 characters of this segment's text, copied exactly from `assembled_text`. |
| `scholarly_function` | `ScholarlyFunction` | yes | The segment's classified scholarly function from the 16-type taxonomy. |
| `confidence` | `float` | yes | Classification confidence, range [0.0, 1.0]. |

**Word offset convention and normalization:** The canonical tokenization is `assembled_text.split()` (Python whitespace split). Both `start_word` and `end_word` are **inclusive** indices into this token list. The text of segment `s` is: `" ".join(assembled_text.split()[s.start_word : s.end_word + 1])`.

**LLM offset alignment (critical implementation detail):** The experiment revealed that the LLM produces internally consistent word offsets (perfectly contiguous — 0 gaps across 162 boundaries in the Taysir div_661 test) but uses its own tokenization that does not match Python `text.split()`. Example: a 3643-token text produced segments ending at word 4172. The LLM's offsets are self-consistent but not directly usable for text extraction.

Therefore, §5.4 (coverage verification) includes a mandatory **offset normalization step** that maps LLM-produced offsets to canonical token positions. The normalization uses the `text_snippet` fields as alignment anchors — each segment's `text_snippet` (copied from the actual text by the LLM) is located in the token stream, and the segment's boundaries are adjusted to match. The invariants below describe the **post-normalization** state — what downstream phases can rely on.

**Invariants (post-normalization):**
- I-CS-1: Segments are ordered by `segment_index` which equals their position in the list (0, 1, 2, ...).
- I-CS-2: Segments are contiguous: for consecutive segments `s[i]` and `s[i+1]`, `s[i+1].start_word == s[i].end_word + 1`.
- I-CS-3: First segment starts at word 0: `segments[0].start_word == 0`.
- I-CS-4: Last segment ends at the last token: `segments[-1].end_word == chunk.total_tokens - 1`.
- I-CS-5: Full coverage: the union of all segment word ranges equals `[0, chunk.total_tokens - 1]`. No gaps, no overlaps.
- I-CS-6: `confidence` is in range `[0.0, 1.0]`.

These invariants are enforced by §5.4 (coverage verification). If the LLM output cannot be normalized to satisfy these invariants (e.g., `text_snippet` cannot be located in the token stream), the result is rejected and retried per §8.2.

### §2.3.4 — TeachingUnit (Phase 2b Output)

One `TeachingUnit` represents the smallest segment of text a student can study and learn something complete from. It groups one or more `ClassifiedSegment` objects into a pedagogically coherent unit. Produced by the Phase 2b LLM grouping call (§5.3).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `unit_index` | `int` | yes | 0-based index within this chunk's grouping result. |
| `segment_indices` | `list[int]` | yes | The `segment_index` values of the `ClassifiedSegment` objects composing this unit. Must be a contiguous ascending sequence (no interleaving). |
| `start_word` | `int` | yes | Start word offset in `assembled_text` (0-based, inclusive). Equals the `start_word` of the first constituent segment. |
| `end_word` | `int` | yes | End word offset in `assembled_text` (0-based, inclusive). Equals the `end_word` of the last constituent segment. |
| `text_snippet` | `str` | yes | First 80 characters of this unit's text, copied exactly from `assembled_text`. |
| `primary_function` | `ScholarlyFunction` | yes | The dominant scholarly function of this unit, determined by the LLM from the constituent segments' functions. |
| `secondary_functions` | `list[ScholarlyFunction]` | yes | Additional scholarly functions present in this unit (may be empty). |
| `description_arabic` | `str` | yes | Brief Arabic description of what this unit teaches. Target range: 5–35 Arabic words. Written by the LLM. |
| `self_containment` | `SelfContainmentLevel` | yes | The unit's self-containment assessment per §3. |
| `self_containment_notes` | `str` | no | Present when `self_containment` is `PARTIAL` or `DEPENDENT`. Describes what context is missing. Written by the LLM. Must be null/absent when `self_containment` is `FULL`. |

**Invariants:**
- I-TU-1: Units are ordered by `unit_index` which equals their position in the list (0, 1, 2, ...).
- I-TU-2: `segment_indices` is a contiguous ascending sequence (e.g., `[3, 4, 5]`, never `[3, 5]` or `[5, 3]`).
- I-TU-3: Every `ClassifiedSegment` is assigned to exactly one `TeachingUnit`. The union of all `segment_indices` across all units equals `{0, 1, ..., total_segments - 1}`.
- I-TU-4: Units are contiguous in word space: for consecutive units `u[i]` and `u[i+1]`, `u[i+1].start_word == u[i].end_word + 1`.
- I-TU-5: `start_word` equals `segments[segment_indices[0]].start_word` and `end_word` equals `segments[segment_indices[-1]].end_word`.
- I-TU-6: If `self_containment` is `FULL`, then `self_containment_notes` must be null/absent.
- I-TU-7: If `self_containment` is `PARTIAL` or `DEPENDENT`, then `self_containment_notes` must be present and non-empty.
- I-TU-8: `description_arabic` contains between 5 and 35 Arabic words (same word-counting rule as `word_count`). Descriptions outside this range trigger a warning but do not reject the unit — the field is informational, not structural.
- I-TU-9: `primary_function` is one of the functions present in the constituent segments (not invented).

### §2.3.5 — ExcerptRecord (Phase 3 Output)

One `ExcerptRecord` is the engine's final output: a `TeachingUnit` enriched with attribution, topic classification, evidence references, and cross-reference metadata. Fully specified in §2.2 (Output Contract). Defined here in summary to complete the data flow.

An `ExcerptRecord` contains all `TeachingUnit` fields plus Phase 3 enrichment:

- `excerpt_id`: globally unique identifier (`exc_{source_id}_{div_id}_{chunk_index}_{unit_index}`)
- Attribution metadata: author layer(s), school, confidence
- Topic classification: 1–3 topic keywords for taxonomy placement
- Evidence references: structured Quran/hadith citations extracted from the text
- Cross-references: resolved implicit references (كما تقدم → target div_id)
- Context hint: added text for `PARTIAL` self-containment cases
- Human gate flags: which decisions need owner review

The full field specification is in §2.2 (Output Contract) — 33 fields across 7 categories, with complete type definitions, sub-object schemas, and 7 output invariants (I-ER-1 through I-ER-7).

### §2.3.6 — Design Constraints

**D-011 (Division/Chunk Containment):** No intermediate type spans a chunk boundary. `AssembledChunk` is the unit of LLM processing — the LLM receives one chunk's `assembled_text` and cannot reference text from another chunk. This is structurally enforced: the Phase 2 prompt receives only one chunk at a time. Cross-chunk teaching units are impossible by construction, not by validation.

**D-023 (Metadata Passthrough):** No normalization metadata field is dropped. `source_id` flows through every intermediate. `text_layers` are rebased but never discarded. `footnotes` are aggregated but never filtered (filtering to relevant footnotes happens in Phase 3 per-excerpt). `content_flags` are aggregated, never reduced. The `AssembledChunk` carries everything downstream phases might need.

**Word offset coordinate system:** All word offsets across all intermediate types use the same coordinate system — words of `assembled_text` split on whitespace, 0-based, inclusive on both ends. This means a `TeachingUnit`'s `start_word`/`end_word` can be directly used to extract text from the `AssembledChunk`'s `assembled_text` without any offset translation. This guarantee holds because §5.4 normalizes LLM-produced offsets to this canonical tokenization before any downstream use.

**Immutability:** `assembled_text` is write-once at Phase 1 and never modified by subsequent phases. Phase 2 and Phase 3 add metadata — they never alter the text. This defends against T-1 (Silent Text Corruption): the text the owner reads in a final excerpt is exactly the text that was assembled from the normalized content units.

---

## §2.1 — Input Contract

The excerpting engine consumes one `NormalizedPackage` at a time — the output of the normalization engine for a single source. The authoritative schema is `engines/normalization/contracts.py`. This section specifies which fields the excerpting engine reads, which it passes through, and what pre-conditions must hold.

### §2.1.1 — Input Files

For each source with `source_id`:

| File | Schema | Description |
|------|--------|-------------|
| `library/sources/{source_id}/normalized/manifest.json` | `NormalizedManifest` | Source-level metadata, division tree, layer map, quality report. |
| `library/sources/{source_id}/normalized/content.jsonl` | `ContentUnit` (one per line) | Page-level content. One record per physical page, ordered by `unit_index`. |

The engine reads both files at startup for the source being processed. The manifest is loaded fully into memory. Content units are loaded on demand per division (by `unit_index` range).

### §2.1.2 — Manifest Fields Used

| Field | Type | Used By | How |
|-------|------|---------|-----|
| `source_id` | `str` | All phases | Propagated to every intermediate and output type. |
| `division_tree` | `list[DivisionNode]` | Phase 1 (§4.2) | Walked to identify leaf divisions. Each `DivisionNode` provides `div_id`, `heading_text`, `heading_level`, `start_unit_index`, `end_unit_index` (inclusive), `children`, `division_type`, `confidence`. |
| `layer_map` | `list[LayerMapEntry]` | Phase 3 (§7.1) | Maps layer types to authors. Used for attribution: `layer_type` → `author_canonical_id` / `author_name_arabic`. Single-layer sources have one entry. |
| `structural_format` | `StructuralFormat` | Phase 1 (§4.1) | Inherited by every `AssembledChunk`. Informs domain-specific handling in §6. The confirmed format, not `structural_format_proposed`. |
| `total_content_units` | `int` | Phase 1 validation (§4.9) | Used by V-P1-2 to verify full coverage: union of all chunks' content units must equal `{0, ..., total_content_units - 1}`. |
| `verse_detection` | `bool` | Phase 1 (§4) | Informational flag. When `true`, the source contains versified text. Does not change Phase 1 behavior (verse-commentary handling is LLM-driven in Phase 2, not structural in Phase 1). |
| `quality_report` | `QualityReport` | Logging | `overall_confidence` logged at start. Sources with `MINIMAL` heading confidence are flagged for potential quality issues (few divisions → large chunks). Not a processing gate. |
| `text_fidelity_summary` | `TextFidelitySummary` | Logging | `high_fidelity_pct` logged. Not a processing gate — the excerpting engine processes all sources regardless of fidelity. |

**Manifest fields consulted when present (optional):**

| Field | Type | Used By | How |
|-------|------|---------|-----|
| `content_census` | `ContentCensus` (nullable) | Phase 1 (§4.5) | When present, `structural_depth.division_count` informs splitting threshold adjustment for books with minimal division trees. Absent for sources where §4.B.5 was not run. |
| `discourse_flow_summary` | `dict` (nullable) | Phase 3 (§7.2) | When present, `dominant_discourse_type` provides a hint for topic classification. Absent for sources where §4.B.10 was not run. |

**Manifest fields passed through (D-023):**

Every manifest field not listed above is passed through to the output untouched. The excerpting engine never modifies or drops manifest-level metadata. Specifically: `schema_version`, `normalizer_id`, `normalization_utc`, `structural_format_proposed`, `verse_numbering_scheme`, `normalization_warnings`, `tahqiq_topology`, `layer_fingerprints` — all preserved in the per-source output summary for downstream engines.

### §2.1.3 — ContentUnit Fields Used

Each `ContentUnit` corresponds to one physical page. The excerpting engine reads these fields during Phase 1 assembly:

| Field | Type | Used By | How |
|-------|------|---------|-----|
| `unit_index` | `int` | Phase 1 (§4.3) | Identifies which units belong to a division. Units are selected by `[start_unit_index, end_unit_index]` range from the `DivisionNode`. |
| `primary_text` | `str` | Phase 1 (§4.3) | Concatenated across pages to form `assembled_text`. All diacritics preserved exactly. No Unicode normalization applied. |
| `text_layers` | `list[TextLayerSegment]` | Phase 1 (§4.6) | Rebased from per-page character offsets to assembled-text character offsets. Each segment's `layer_type`, `author_canonical_id`, `start`, `end`, `confidence` are preserved. |
| `footnotes` | `list[Footnote]` | Phase 1 (§4.7) | Collected from all constituent pages, deduplicated by `ref_marker`. All fields preserved: `ref_marker`, `text`, `footnote_type`, `confidence`, plus type-specific data when present. |
| `structural_markers` | `StructuralMarkers` | Phase 1 (§4.5, §4.8) | `heading_detected`, `heading_text` used for split-point detection in oversized divisions. `heading_text` used for heading alignment verification. |
| `boundary_continuity` | `BoundaryContinuity` (nullable) | Phase 1 (§4.3) | Determines separator between consecutive pages during assembly. `type` field maps to separator string. Null on last unit and non-paginated sources — treated as `"\n"` separator. |
| `content_flags` | `ContentFlags` | Phase 1 (§4.7) | OR-aggregated across pages into chunk-level flags. `is_toc_page` and `is_index_page` used by §4.2 to skip non-content divisions. |
| `physical_page` | `PhysicalPage` | Phase 1 (§4.7) | Collected into chunk's `physical_pages` list for citation support. |
| `verse_info` | `VerseInfo` (nullable) | Accessible | Not carried on `AssembledChunk` directly. Accessible by re-reading the constituent `ContentUnit` records via `assembly_metadata.constituent_unit_indices`. Reserved for deferred §6.5 verse-commentary alignment. |
| `text_fidelity` | `TextFidelity` | Logging | Per-page fidelity logged. Not a processing gate. |

**ContentUnit fields consulted when present (optional):**

| Field | Type | Used By | How |
|-------|------|---------|-----|
| `discourse_flow` | `DiscourseFlow` (nullable) | Phase 1 (§4.5) | When present, `section_break` boundaries in discourse segments provide split-point candidates for oversized divisions (second preference after heading markers). Absent for pages with <100 characters. |

### §2.1.4 — Pre-conditions

The excerpting engine does **not** re-validate the normalization output against its schema. The normalization engine is responsible for producing valid output (Layer 1 self-validation per `KNOWLEDGE_INTEGRITY.md`). The excerpting engine trusts that:

1. `manifest.json` conforms to the `NormalizedManifest` schema.
2. Every line in `content.jsonl` conforms to the `ContentUnit` schema.
3. `unit_index` values are contiguous from 0 to `total_content_units - 1`.
4. `text_layers` on every `ContentUnit` cover `[0, len(primary_text))` with no gaps and no overlaps.
5. `DivisionNode.start_unit_index` and `end_unit_index` refer to valid `unit_index` values.
6. `DivisionNode` ranges do not overlap at the same tree level.

If any of these pre-conditions is violated, the excerpting engine will produce incorrect output or crash. This is by design — the normalization boundary guarantees validity, and re-validating 725 lines of schema on every excerpting run would be wasteful. Boundary violations are caught by `tools/check_cross_engine_contracts.py` during integration testing, not at runtime.

**Exception:** The excerpting engine does perform lightweight defensive checks at the point of use:
- Empty `division_tree` → emit `EX-A-010` (no divisions to process), skip source.
- `ContentUnit` not found for a `unit_index` in the declared range → emit `EX-A-011`, skip division.
- `boundary_continuity` is null on a non-terminal unit → treat as `unknown` type, emit warning.

These are defensive checks against data corruption, not schema re-validation.

---

## §2.2 — Output Contract

The excerpting engine produces one `ExcerptRecord` per teaching unit. The output is a JSONL file per source: `library/sources/{source_id}/excerpts/excerpts.jsonl`. Each line is a complete JSON object representing one `ExcerptRecord`.

The taxonomy engine (downstream consumer) reads these files. Every field documented here is part of the cross-engine contract — removing or renaming a field is a breaking change.

### §2.2.1 — Output File Structure

**Primary output:** `library/sources/{source_id}/excerpts/excerpts.jsonl`
- One JSON line per `ExcerptRecord`.
- Records are ordered by `div_id` (string sort), then by `chunk_index` (numeric), then by `unit_index` (numeric). This ordering preserves the text's reading order within the source.
- Encoding: UTF-8. No BOM. Line separator: `\n`.

**Gate queue (side output):** `library/sources/{source_id}/excerpts/gate_queue.jsonl`
- One JSON line per human gate entry (§7.3.4). Present only if at least one gate was triggered.

**Processing log (side output):** `library/sources/{source_id}/excerpts/processing_log.jsonl`
- Structured log of all warnings, errors, and telemetry for this source's excerpting run.

### §2.2.2 — ExcerptRecord Fields

Every field is listed with its type, whether it is required, its source (which processing step produces it), and traceability to the SPEC section that defines its computation.

**Identification and context:**

| Field | Type | Required | Source | SPEC Reference |
|-------|------|----------|--------|----------------|
| `excerpt_id` | `str` | yes | Deterministic | §7.1 F-DET-1 |
| `source_id` | `str` | yes | Passthrough | §2.1 (from AssembledChunk) |
| `div_id` | `str` | yes | Passthrough | §2.1 (from AssembledChunk) |
| `chunk_index` | `int` | yes | Deterministic | §7.1 F-DET-1. For unsplit chunks (no `split_info`), `chunk_index = 0`. For split chunks, `chunk_index = split_info.chunk_index`. |
| `unit_index` | `int` | yes | Inherited | §2.3.4 (from TeachingUnit) |
| `div_path` | `list[str]` | yes | Deterministic | §7.1 F-DET-7 |

**Text content:**

| Field | Type | Required | Source | SPEC Reference |
|-------|------|----------|--------|----------------|
| `primary_text` | `str` | yes | Deterministic | §7.1 F-DET-2 |
| `text_snippet` | `str` | yes | Inherited | §2.3.4 (from TeachingUnit) |
| `start_word` | `int` | yes | Inherited | §2.3.4 (from TeachingUnit) |
| `end_word` | `int` | yes | Inherited | §2.3.4 (from TeachingUnit) |
| `segment_indices` | `list[int]` | yes | Inherited | §2.3.4 (from TeachingUnit) |
| `physical_pages` | `PageRange \| null` | no | Deterministic | §7.1 F-DET-6 |

`PageRange` structure: `{volume: int | null, start_page: int, end_page: int}`. Null when physical page information is unavailable (some Shamela exports lack it). Derived from the `AssembledChunk.physical_pages` list in §7.1 F-DET-6.

**Classification:**

| Field | Type | Required | Source | SPEC Reference |
|-------|------|----------|--------|----------------|
| `primary_function` | `ScholarlyFunction` | yes | Inherited | §2.3.4 (from TeachingUnit) |
| `secondary_functions` | `list[ScholarlyFunction]` | yes | Inherited | §2.3.4 (from TeachingUnit) |
| `content_types` | `list[ScholarlyFunction]` | yes | Deterministic | §7.1 F-DET-4 |
| `description_arabic` | `str` | yes | Inherited | §2.3.4 (from TeachingUnit) |

**Self-containment:**

| Field | Type | Required | Source | SPEC Reference |
|-------|------|----------|--------|----------------|
| `self_containment` | `SelfContainmentLevel` | yes | Inherited + consensus | §2.3.4 + §7.3 |
| `self_containment_notes` | `str \| null` | conditional | Inherited | §2.3.4 (from TeachingUnit) |
| `context_hint` | `str \| null` | conditional | LLM enrichment | §7.2 |

Conditional rules: `self_containment_notes` is required (non-null, non-empty) when `self_containment` is PARTIAL or DEPENDENT, and must be null when FULL (I-TU-6, I-TU-7). `context_hint` is non-null only when `self_containment` is PARTIAL.

**Attribution:**

| Field | Type | Required | Source | SPEC Reference |
|-------|------|----------|--------|----------------|
| `primary_author_layer` | `AuthorAttribution` | yes | Deterministic | §7.1 F-DET-3 |
| `attribution_confidence` | `float \| null` | no | Consensus | §7.3 |
| `quoted_scholars` | `list[ScholarAttribution]` | yes | Deterministic + LLM | §7.1 F-DET-9 + §7.2 |
| `school` | `str \| null` | yes | LLM enrichment | §7.2 |
| `school_confidence` | `float \| null` | no | LLM enrichment + Consensus | §7.2 + §7.3 |

`attribution_confidence` values: For non-LA-3 cases (deterministic attribution via LA-1, LA-2, or LA-4), `attribution_confidence` is `null` — the attribution is deterministic and confidence is not applicable. For LA-3 cases resolved by 2-of-3 consensus, `attribution_confidence` is `0.67`. For LA-3 cases where all 3 disagree (EX-G-001), `attribution_confidence` is `0.0`.

`school_confidence` values: The enrichment LLM produces a `school_confidence` value (0.0–1.0) alongside `school` in the §7.2 response. When consensus is not triggered (school is null, or verifier agrees), this value passes through. When the verifier disagrees (§7.3.3), `school_confidence` is set to the lower of the enrichment and verifier confidence values. When school is null, `school_confidence` is null.

`AuthorAttribution` structure: `{layer_id: str, author_id: str, coverage_pct: float, rule_applied: str}`. The `rule_applied` field is one of LA-1, LA-2, LA-3, LA-4 (§6.2).

`ScholarAttribution` structure: `{mention_text: str, resolved_name: str | null, role: str, confidence: float, source: str}`. The `source` field distinguishes structural detection (`"layer_overlap"` from F-DET-9) from LLM resolution (`"llm_enrichment"` from §7.2). The `role` field is one of: `quoted_opinion`, `classification_frame`, `refuted_position`.

**Topic and taxonomy:**

| Field | Type | Required | Source | SPEC Reference |
|-------|------|----------|--------|----------------|
| `excerpt_topic` | `list[str]` | yes | LLM enrichment | §7.2 |
| `terminology_variants` | `list[TermVariant]` | yes | LLM enrichment | §7.2 |

`TermVariant` structure: `{term: str, variants: list[str]}`.

`excerpt_topic` may be empty (zero keywords) only when LLM enrichment failed (review flag `llm_enrichment_failed` is set). Otherwise it must have 1–3 entries.

**Evidence and references:**

| Field | Type | Required | Source | SPEC Reference |
|-------|------|----------|--------|----------------|
| `evidence_refs` | `list[EvidenceRef]` | yes | Deterministic | §7.1 F-DET-5. Note: F-DET-5 performs structural pattern matching only (﴿...﴾ delimiters for Quran, hadith citation markers, consensus patterns). Unresolved references (e.g., partial Quran quotes with `surah: null`) remain null in core. LLM-assisted resolution of partial evidence references is a deferred capability — the §7.2 enrichment call does not update `evidence_refs`. The `takhrij_data` field (§7.2) provides LLM-extracted hadith detail separately. |
| `takhrij_data` | `list[TakhrijEntry] \| null` | no | LLM enrichment | §7.2 |
| `cross_references` | `list[CrossReference]` | yes | LLM enrichment | §7.2 |
| `footnotes_relevant` | `list[Footnote]` | yes | Deterministic | §7.1 F-DET-8 |

`EvidenceRef` structure: `{type: str, surah: int | null, ayah_start: int | null, ayah_end: int | null, text_snippet: str, marker_text: str | null, scope: str | null}`. The `type` is one of: `quran`, `hadith`, `ijma`. Fields not applicable to the type are null.

`TakhrijEntry` structure: `{hadith_text_snippet: str, collections: list[str], hadith_numbers: list[str], grade: str | null, grade_source: str | null}`.

`CrossReference` structure: `{reference_text: str, target_description: str | null, target_div_id: str | null, resolved: bool}`.

`Footnote` structure: inherited from the normalization engine's footnote schema. Includes `ref_marker`, `text`, and `footnote_type`.

**Metadata and flags:**

| Field | Type | Required | Source | SPEC Reference |
|-------|------|----------|--------|----------------|
| `consensus_metadata` | `ConsensusRecord \| null` | no | Consensus | §7.3 |
| `gate_flags` | `list[str]` | yes | Consensus/gates | §7.3.4 |
| `review_flags` | `list[str]` | yes | Various | §7.2, §7.3, §7.4 |

`ConsensusRecord` structure: `{decisions: list[ConsensusDecision]}`. Each `ConsensusDecision`: `{decision_type: str, enrichment_value: str, verifier_value: str | null, verifier_agrees: bool | null, escalation_value: str | null, final_value: str, resolution_method: str}`.

`gate_flags` is a list of EX-G-* codes that triggered. Empty list if no gates triggered.

`review_flags` is a list of string flags for operational issues. Known flags: `llm_enrichment_failed`, `school_consensus_disagreement`, `attribution_consensus_escalated`, `decontextualization_risk` (set when Phase 2b assigns DEPENDENT due to C-SC-4 or C-SC-5 failure from DP-1–DP-6 patterns), `verification_skipped` (set when consensus verification model fails on all retries and enrichment model's assessment is used without verification). Empty list if no flags.

### §2.2.3 — Output Invariants

**I-ER-1 (Excerpt ID uniqueness):** No two `ExcerptRecord` objects in the entire library share an `excerpt_id`. Within a source, uniqueness is guaranteed by the ID format (`exc_{source_id}_{div_id}_{chunk_index}_{unit_index}`). For split divisions, different chunks have different `chunk_index` values, preventing ID collisions.

**I-ER-2 (Primary text immutability):** `primary_text` is exactly the text extracted from `assembled_text` using word offsets. It is never modified after extraction — no "cleanup," no Unicode normalization, no diacritics alteration. The owner reads exactly what the source contains.

**I-ER-3 (Reading order):** Records within a source's JSONL file appear in reading order: sorted by `div_id`, then `chunk_index`, then `unit_index`. This allows sequential reading of the source's excerpts.

**I-ER-4 (Self-containment consistency):** The self-containment level, notes, and context_hint are mutually consistent per I-TU-6 and I-TU-7. FULL → no notes, no context_hint. PARTIAL → notes present, context_hint present (if LLM enrichment succeeded). DEPENDENT → notes present, no context_hint (context hints cannot save DEPENDENT units).

**I-ER-5 (Attribution completeness):** Every excerpt has `primary_author_layer` with a non-null `layer_id` and `author_id`. Even ambiguous cases (LA-3) produce an attribution — the ambiguity is expressed in `attribution_confidence` and `gate_flags`, not in missing data.

**I-ER-6 (No orphan fields):** Every field in the ExcerptRecord is produced by a defined processing step (column "Source" in §2.2.2 tables). No field exists without a producer. No processing step produces a field not listed in §2.2.2.

**I-ER-7 (D-023 compliance):** Source metadata fields (`source_id`, `div_id`) are passed through without modification. No upstream metadata is dropped.

### §2.2.4 — Downstream Consumer Contract

The taxonomy engine consumes `ExcerptRecord` objects with these expectations:

**Required for taxonomy placement:** `excerpt_id`, `excerpt_topic`, `primary_function`, `content_types`, `school`, `source_id`.

**Required for display:** `primary_text`, `description_arabic`, `div_path`, `physical_pages`, `primary_author_layer`, `footnotes_relevant`.

**Required for quality gates:** `self_containment`, `gate_flags`, `review_flags`.

**Informational (used if present):** `evidence_refs`, `takhrij_data`, `cross_references`, `terminology_variants`, `context_hint`, `quoted_scholars`, `consensus_metadata`.

The taxonomy engine MUST handle null/empty values gracefully for all optional/conditional fields. When `llm_enrichment_failed` is in `review_flags`, LLM-derived fields (`excerpt_topic`, `school`, `takhrij_data`, `terminology_variants`, `cross_references`, `context_hint`) may be empty/null.

---

## §3 — Self-Containment Standard

Self-containment is the excerpting engine's primary quality criterion. An excerpt that fails self-containment delivers an incomplete piece of knowledge to the owner — a fragment that looks like a complete teaching but is actually missing its premise, its evidence, or its conclusion. This is T-4 (Context Loss) from `KNOWLEDGE_INTEGRITY.md`: the owner reads something that appears self-sufficient but silently depends on context that was stripped during extraction.

This section defines the standard formally. It is referenced by Phase 2b (§5.3, which evaluates it), Phase 3 (§7, which repairs `PARTIAL` cases), §6 (domain rules that defend it), and §10 (tests that verify it).

### §3.1 — Definition

An excerpt is **self-contained** if a student with general familiarity of the Islamic science (عِلم) covered by the source — but no familiarity with this specific source or its surrounding text — can understand:

1. **What** is being taught (the concept, ruling, argument, or narration).
2. **Whose** position this represents (which scholar, school, or the author themselves).
3. **Why** this position is held (what evidence or reasoning supports it, if the excerpt presents a justified claim).

"General familiarity" means the student knows the basic terminology and structure of the science. For example: a student of fiqh knows what a حكم (ruling) is, what the مذاهب (schools) are, and what constitutes دليل (evidence). The student does NOT know the specific topic being discussed, the arguments made earlier in the book, or the scholarly debates surrounding this particular issue — those must be contained within the excerpt or explicitly flagged as missing.

### §3.2 — Formal Criteria

Five criteria must all hold for an excerpt to be `FULL` self-contained. These are evaluated by the LLM during Phase 2b (§5.3) and re-checked during Phase 3 (§7.3).

**C-SC-1 (Term Resolution):** Every technical term used in the excerpt is either:
  - (a) defined within the excerpt,
  - (b) a standard term of the science that any student of that science would know (e.g., واجب in fiqh, مبتدأ in nahw), or
  - (c) flagged in `self_containment_notes` as requiring external knowledge.

**C-SC-2 (Reference Resolution):** Every pronoun, demonstrative, anaphoric reference, or implied dependency (taqdir) resolves within the excerpt. No dangling references pointing to text outside the excerpt. The LLM must watch for both visible and invisible dependencies:
- **Visible:** هذا/هذه/هؤلاء (demonstratives), المذكور/ما تقدم/ما سبق (backward references), pronoun suffixes like ـه/ـها/ـهم/ـهما (e.g., عليهما referring to الخفين), opening conjunctions like لأن/فإن that depend on a preceding clause.
- **Invisible (taqdir):** Implied subjects in قال/ذهب/رأى where the speaker is determined from prior context, not stated in the excerpt. Example: "قال: يجوز" — if the reader cannot determine who "said" it from within the excerpt, the reference is unresolved (FP-12, Gemini review 2026-04-04).
Note: opening و does NOT always indicate a dangling reference — it may simply continue within the same topic. The LLM must reason about whether each referent (visible or implied) resolves inside or outside the unit rather than flagging blindly (owner F4, 2026-04-04). If the LLM detects an unresolvable reference, the excerpt cannot be `FULL`.

**C-SC-3 (Evidence Completeness):** Every evidence citation (Quran, hadith, athar, scholarly precedent) either:
  - (a) includes its text within the excerpt, or
  - (b) is a well-known citation identifiable by its opening words alone (e.g., حديث "إنما الأعمال بالنيات" — any student would recognize it), or
  - (c) is flagged in `self_containment_notes`.

**C-SC-4 (Argument Completeness):** The excerpt's argument, ruling, or teaching is complete — not a fragment of a larger argument whose premise or conclusion is elsewhere. An excerpt that states "ورد عليه بأن..." (and it was countered with...) without the original position being countered cannot be `FULL`. An excerpt that presents evidence without stating what it is evidence for cannot be `FULL`.

**C-SC-5 (Dialogue Completeness):** If the excerpt quotes or responds to another scholar's position, enough of that position is included to understand the response. An excerpt that says "وأما قول الشافعي فليس بصحيح لأن..." must include enough of al-Shafi'i's stated position to understand why it is being rejected. The position need not be quoted in full — a sufficient summary within the excerpt satisfies this criterion.

### §3.3 — Self-Containment Levels

Each `TeachingUnit` (§2.3.4) receives one of three self-containment levels:

**FULL** — All five criteria (C-SC-1 through C-SC-5) are met. The excerpt stands alone. No repair, no flagging, no human gate. This is the target state for every excerpt.

**PARTIAL** — Most criteria are met, but the excerpt would benefit from additional context. Specifically: the excerpt teaches something coherent, but a reference, term, or piece of evidence is not fully resolved. This corresponds to the experiment's `self_contained=true` with `self_containment_notes` populated — the excerpt is usable but not perfect.

**Context resolution hierarchy (NC-1, from owner Q&A F5, 2026-04-04):**

The context resolution hierarchy for PARTIAL excerpts, in order of preference:

1. **Structural unity (EE-1):** Prevent the context gap by keeping explained+explanation together. This is the best outcome — no repair needed because the content was never split.

2. **Source surroundings:** Every excerpt carries `source_id`, `div_id`, and `physical_pages`, which point back to the frozen source bytes. The reader can access the actual surrounding pages from the original book to verify context. This mechanism applies to ALL excerpts (FULL, PARTIAL, and DEPENDENT) and requires no AI generation — it uses the immutable source text preserved by the normalization engine. Implementation of the source-surroundings display is a synthesis/UI responsibility; the excerpting engine's responsibility is ensuring the location metadata is always present and correct.

3. **Generated context_hint:** A brief LLM-generated note explaining what context is missing and where to find it in the surrounding text (e.g., "References a position stated in the باب preceding this one"). This is supplementary guidance that helps the reader navigate the source surroundings — it is NOT a replacement for the source text itself. The hint points into the surroundings; it does not substitute for them.

**Rationale:** The owner's principle is: "ALWAYS TRY TO KEEP THINGS AS CLOSE TO THE ORIGINAL AUTHORS WORDINGS / WORK / SOURCE AS POSSIBLE." Generated notes are lossy summaries — they introduce interpretation risk and can never match the specificity of the actual source text. The source surroundings mechanism provides the original text with zero interpretation, while the context_hint provides navigation guidance.

Phase 3 action: Add `context_hint` — a brief note explaining what context is missing and where to find it in the source surroundings. The taxonomy engine receives the excerpt with the hint attached; the synthesis engine can incorporate the hint and source-surroundings reference when building entries.

Phase 3 also attempts to resolve the gap:
- If C-SC-2 fails (dangling reference) and the reference points to a known division, add a `cross_reference` linking to that division.
- If C-SC-3 fails (evidence not included) and the evidence is identifiable (e.g., a known hadith), add the reference in `evidence_refs`.

After Phase 3 repair, the level could in principle be upgraded from `PARTIAL` to `FULL` if all criteria are now satisfied. However, **the core engine does not implement automatic re-evaluation** — re-evaluating C-SC-1 through C-SC-5 after repair would require an additional LLM call per unit. In core, the level stays `PARTIAL` and the context_hint provides value even when the underlying gap has been resolved by a cross-reference or evidence addition. Automatic self-containment re-evaluation after Phase 3 repair is a quality optimization (candidate for DC-07, Self-containment repair suggestions). If repair fails, the level stays `PARTIAL`.

**DEPENDENT** — The excerpt cannot be understood alone. It depends on adjacent content in a way that no context hint can repair. This typically means C-SC-4 fails (argument is a fragment) or C-SC-5 fails (response to an unknown position).

Phase 3 action: Flag for human gate review. Write to `gate_queue.jsonl` with the full context (the excerpt, its adjacent teaching units in the same chunk, and the specific criteria that failed). The owner decides: accept with a note, merge with an adjacent excerpt, or reject.

**Gate design:** Per `KNOWLEDGE_INTEGRITY.md` Layer 4, the owner may respond "yes" (accept), "no" (reject), or "I'm not sure" (triggers elevated Layer 3.5 cross-provider verification with 3+ models). A `DEPENDENT` excerpt never auto-promotes to `FULL` — it either stays `DEPENDENT` with an owner-accepted note, gets merged into an adjacent unit, or is rejected.

### §3.4 — Relationship to Domain Rules

The domain rules in §6 are enforcement mechanisms for self-containment:

- §6.1 (Decontextualization Prevention) defends C-SC-4 and C-SC-5: a position and its refutation must stay together, a question and its answer must stay together.
- §6.2 (Multi-Layer Handling) defends the "whose position" requirement: correct attribution prevents the owner from studying a sharh author's opinion thinking it is the matn author's.
- §6.3 (Evidence Handling) defends C-SC-3: hadith and evidence grouped with their rulings.
- §6.4 (Implicit Reference Resolution) defends C-SC-2: كما تقدم references are flagged or resolved.

Self-containment is not a separate evaluation pass — it is embedded in the Phase 2b grouping decision. When the LLM groups segments into teaching units, it evaluates self-containment simultaneously. The domain rules (§6) are encoded in the Phase 2b prompt as explicit grouping constraints.

### §3.5 — Measurement and Calibration

The old excerpting SPEC used a continuous 0.0–1.0 `self_containment_score`. The new design uses a 3-level enum. The rationale:

- A continuous score creates false precision. The LLM cannot reliably distinguish 0.65 from 0.72 — both mean "probably fine but something might be missing."
- The 3-level system maps directly to actions: no action (`FULL`), automated repair (`PARTIAL`), human gate (`DEPENDENT`). Every level has a defined response.
- The experiment's binary flag plus notes naturally maps to this 3-level system (see §2.3 `SelfContainmentLevel` design extension note).

**Calibration during build:** The boundary between `PARTIAL` and `DEPENDENT` is the critical calibration point. Too strict (many `DEPENDENT`) overwhelms the human gate queue. Too lenient (many `PARTIAL` that should be `DEPENDENT`) lets incomplete arguments through. The 30-book probe (source engine roadmap Step 3) calibrates this boundary empirically. The SPEC defines the criteria; the build determines the prompt calibration that maps criteria to levels.

**Same-model evaluation bias (C-7 mitigation):** Opus 4.6 both extracts teaching units and evaluates self-containment. Structural mitigations:
- Mechanical checks (C-SC-2 can be partially verified by searching for unresolved demonstratives; C-SC-3 can be partially verified by checking evidence segment presence).
- Cross-model spot checks: during the 30-book probe, a different model evaluates 10% of self-containment assessments.
- Owner spot-checks: the owner reviews 5 excerpts per session during the probe, with specific attention to "does this make sense on its own?"

---

## §4 — Phase 1: Deterministic Preprocessing

Phase 1 transforms a `NormalizedPackage` into a list of `AssembledChunk` objects (§2.3.2). It is fully deterministic — no LLM calls, no randomness, no external dependencies beyond the input files. Every behavior is independently unit-testable. This phase absorbs the core of the old passaging engine (cross-page assembly, text joining, validation) but eliminates format-specific passaging strategies — those are handled by the LLM in Phase 2.

### §4.1 — Processing Overview

Phase 1 proceeds in seven sequential steps:

1. **Walk division tree** (§4.2): Identify leaf divisions from `manifest.division_tree`. Skip non-content divisions.
2. **Assemble text** (§4.3): For each leaf division, join `primary_text` across content units using `boundary_continuity` separator mapping.
3. **Merge tiny divisions** (§4.4): Merge adjacent leaf divisions with <50 Arabic words.
4. **Split oversized divisions** (§4.5): Split divisions with >5000 Arabic words at structural boundaries.
5. **Aggregate metadata and renumber footnotes** (§4.7): OR-aggregate content flags, collect footnotes (including renumbering if `ref_marker` collisions exist — this modifies `assembled_text`), collect physical pages. Footnote renumbering MUST complete before step 6 because it changes character offsets.
6. **Rebase text layers** (§4.6): Translate per-page `text_layers` character offsets to assembled-text coordinates. Runs on the final `assembled_text` (after any footnote renumbering from step 5).
7. **Validate** (§4.9): Run self-validation checks (V-P1-1 through V-P1-6).

The heading alignment filter (§4.8) runs during step 2 as a quality flag but does not gate processing.

The engine processes one source at a time. Each leaf division (or merged/split result) produces one `AssembledChunk`. The output is a list of chunks ready for Phase 2.

**No format-specific strategies.** Unlike the old passaging SPEC, Phase 1 does not apply different strategies for prose, verse, Q&A, or masala formats. The `structural_format` field is inherited by each chunk for Phase 2's reference, but Phase 1 treats all text identically: assemble, merge/split, validate. Format-aware processing happens in Phase 2 (the LLM understands format natively) and §6 (domain-specific rules).

### §4.2 — Division Tree Walking

**Input:** `manifest.division_tree` — a list of `DivisionNode` objects forming a tree.

**Leaf identification:** A leaf division is a `DivisionNode` with an empty `children` list. The engine recursively walks the tree and collects all leaves with their heading path (the list of `heading_text` values from root to leaf). Validated implementation: `find_leaf_divisions()` in `experiments/architecture_test/extract_divisions.py`.

**Parent preamble content (tree completion):** The normalization engine produces division trees where parent nodes may have content units not covered by any child. This is the standard Arabic scholarly text pattern: a chapter (باب) starts with introductory text before its sub-sections (فصول). Before walking the tree, the engine calls `_complete_division_tree()` which inserts synthetic leaf nodes for uncovered ranges. Three gap types are handled: preamble (content before the first child), inter-child (content between consecutive children), and trailing (content after the last child). Synthetic preamble leaves use `DivisionType.MUQADDIMAH` with `heading_text="مقدمة"`. Synthetic div_ids use `{parent_div_id}_pre`, `_gap_{N}`, or `_post` suffixes. Empirically, all 5 test packages exhibit only preamble gaps (zero inter-child, zero trailing). Without tree completion, 2–29% of content units per source would be silently lost.

**Skip criteria:** A leaf division is skipped (produces no chunk) if ANY of the following hold:
- All content units in its range have `content_flags.is_toc_page == true`.
- All content units in its range have `content_flags.is_index_page == true`.
- All content units in its range have `content_flags.is_blank == true`.
- Its `heading_text` matches any of the bibliography/index exclusion keywords. Match is **exact match after Arabic noise stripping** (same stripping as §4.8): the full stripped heading must equal the full stripped keyword. This prevents false positives on content chapters like "مصادر الأحكام" (sources of rulings) — word-boundary matching would incorrectly match "مصادر" within such headings. Note: Arabic has no case distinction; "case-insensitive" does not apply. The complete keyword list (validated on 322 headings across 5 fixture packages with zero false positives):
  - Base forms: مصادر, مراجع, فهرس
  - With definite article: المصادر, المراجع
  - Construct phrases: ثبت المصادر
  - Compound forms: مصادر ومراجع, المصادر والمراجع
  - Index compounds: فهرس المصادر, فهرس المراجع
  - List compounds: قائمة المراجع, قائمة المصادر, قائمة المصادر والمراجع
- Its content unit range is empty: `start_unit_index > end_unit_index` or no content units exist in the range. Emit `EX-A-002` (empty division), log, and skip.

Skipped divisions are logged with reason codes. They are NOT errors — TOC and index pages are expected.

**Multi-volume sources:** Division nodes with `division_type == "volume"` are structural containers, not content divisions. The engine walks through them to reach leaf divisions. Volume nodes never produce chunks themselves.

**Minimal division trees (C-8):** Sources with <5 leaf divisions after filtering produce very large chunks. This is handled naturally by §4.5 (oversized splitting). Sources with zero leaf divisions after filtering: emit `EX-A-010`, skip entire source.

**Single-root sources:** Sources where `division_tree` contains a single root node with no children: the entire source text is one leaf division. It becomes one chunk (or multiple chunks if oversized per §4.5).

### §4.3 — Cross-Page Text Assembly

For each leaf division, assemble the full text by joining `ContentUnit.primary_text` across pages.

**Content unit selection:** Select all content units with `unit_index` in the range `[division.start_unit_index, division.end_unit_index]` (both inclusive). Content units with `is_toc_page`, `is_index_page`, or `is_blank` true within this range are skipped during assembly — their `unit_index` is still recorded in `assembly_metadata.constituent_unit_indices` for coverage tracking, but their text is not included.

**Separator mapping:** Between consecutive content units N and N+1, the separator is determined by unit N's `boundary_continuity.type`:

| `boundary_continuity.type` | Separator | Rationale |
|---------------------------|-----------|-----------|
| `mid_sentence` | `" "` (space) | Text continues across page boundary; always between complete words (see below). |
| `mid_paragraph` | `"\n"` | New sentence within same paragraph. |
| `mid_argument` | `"\n"` | Argument continues but new logical segment. |
| `section_break` | `"\n\n"` | Major topic transition. |
| `division_break` | `"\n\n"` | Division-level break (should not occur within a leaf division's range, but handled defensively). |
| `unknown` | `"\n"` | Conservative default. |
| null (absent) | `"\n"` | Boundary continuity not computed. |

This mapping is validated in the prototype (`BC_JOIN_MAP` in `extract_divisions.py`).

**Boundary continuity is on unit N:** The `boundary_continuity` field on unit N describes the boundary AFTER unit N (between N and N+1). When joining unit N and unit N+1, read `boundary_continuity` from unit N.

**Arabic word joining at mid_sentence:** When `boundary_continuity.type == "mid_sentence"`, the separator is a single space `" "`. Shamela digitizes printed Arabic books page-by-page, and Arabic typography does not split words across page boundaries (there is no Arabic hyphenation convention). Every Shamela page break inherently falls between complete words. Empirically verified: 0 of 294 mid_sentence boundaries across all 5 fixture packages contained a genuine mid-word split; 100% were between complete words.

The previous heuristic (empty separator with word-final character detection for ة, ى, tanwin) was removed because it produced 92% word-merge corruption — 270 of 294 boundaries merged two separate Arabic words into unreadable text (e.g., "للخطأوَلِهَذَا" instead of "للخطأ وَلِهَذَا"). See SPEC-NOTE-4 in reference/SPEC_ERRATA.md.

**Future mid-word boundaries:** The normalization SPEC §4.B.8 documents that OCR sources or corrupt Shamela exports may produce genuine mid-word `mid_sentence` boundaries (logged as `NORM_MIDWORD_BREAK`). When such sources are implemented, the `continuation_hint` field on `BoundaryContinuity` can signal the excerpting engine to use empty separator for those cases. Until then, the always-space rule applies — an unwanted space in a word is visible and correctable, while 92% silent word-merging is not.

**Diacritics preservation:** All Arabic diacritics (U+064B–U+0652, U+0670) are preserved exactly. No Unicode normalization (NFC/NFD/NFKC/NFKD) is applied at any point. This is an absolute rule — violating it risks T-1 (Silent Text Corruption), since a single diacritic change can reverse meaning (حَرَّمَ "forbade" vs حَرَمَ "deprived").

**Footnote reference markers:** The `⌜N⌝` markers in `primary_text` are preserved inline during assembly. Footnote renumbering (if `ref_marker` values collide across pages) is handled in §4.7.

**Assembly output:** The assembled text, plus an `AssemblyMetadata` record containing `constituent_unit_indices` and `join_points` (one `JoinPoint` per page boundary, recording the units, separator, and character offset).

### §4.4 — Tiny Division Merging

Divisions with very few words produce low-quality LLM inputs — the model lacks sufficient context for meaningful classification. These are merged with adjacent siblings.

**Threshold:** `TINY_DIVISION_WORDS = 50` Arabic words (configurable, §8.3). This captures 29.1% of raw Shamela divisions per the division size analysis.

**Merge algorithm:**
1. After assembling all leaf divisions under the same parent node, identify those with `word_count < TINY_DIVISION_WORDS`.
2. For each tiny division, merge with the **next sibling** under the same parent. If no next sibling exists, merge with the **previous sibling**. **Merge size guard:** before merging, check whether the combined word count would exceed `OVERSIZED_DIVISION_WORDS`. If so, do NOT merge — leave the tiny division as a standalone chunk (same behavior as the only-child case in step 3). This prevents a merge→split sequence that would produce a chunk with both `merge_history` and `split_info`, violating I-AC-7.
3. If the division is an only child (no siblings), or if all eligible siblings would exceed the size guard, process as-is regardless of size — there is nothing safe to merge with.
4. Merging combines the assembled texts with a `"\n\n"` separator between them (they are separate divisions, so a section break is appropriate).
5. The merged chunk's `div_id` is the first division's `div_id`. The merged chunk's `merge_history` records all merged `div_id` values.
6. The merged chunk's `div_path` is the first division's path (the heading hierarchy).
7. Repeat merging: if the result of a merge is still below threshold, merge again with the next sibling (subject to the size guard). This is recursive but bounded by the finite number of siblings.

**Invariant preserved:** I-AC-6 requires `merge_history` to contain ≥2 entries with the first being `div_id`. The merge algorithm guarantees this.

### §4.5 — Oversized Division Splitting

Divisions with too many words produce LLM inputs that exceed token limits or degrade classification quality. These are split at structural boundaries.

**Threshold:** `OVERSIZED_DIVISION_WORDS = 5000` Arabic words (configurable, §8.3). This affects ~0.9% of Shamela divisions per division size analysis.

**Split point selection (priority order):**
1. **Heading markers within the division:** If any content unit in the range has `structural_markers.heading_detected == true`, split at that unit. The heading starts a new chunk. This is the highest-quality split because the heading indicates a natural topic boundary.
2. **Discourse section breaks:** If `discourse_flow` data is available on content units and contains segments with type boundaries corresponding to `section_break`, split at those boundaries. Second preference because discourse flow is a normalization §4.B feature that may not be present.
3. **Paragraph breaks:** Find the `"\n\n"` nearest the midpoint of the assembled text. Split there. This is reliable because paragraph breaks exist in almost all texts.
4. **Sentence boundary:** Find the sentence boundary (terminal punctuation `.` `؟` `!` followed by whitespace) nearest the midpoint. Last resort.

**Splitting produces:** Multiple chunks from one division, each with `split_info` populated (§2.3.2 `SplitInfo`). Chunk IDs: `{div_id}_chunk_0`, `{div_id}_chunk_1`, etc.

**Recursive splitting:** If a split result still exceeds the threshold, split again. Bounded by text length — eventually each chunk will be below threshold.

**Text layer and footnote handling for split chunks:** Each chunk gets the text layers and footnotes corresponding to its text range only. Text layers are sliced at the split point character offset — a layer segment that spans the split point is divided into two segments, one per chunk. Both halves inherit the original segment's `layer_type`, `author_canonical_id`, and `confidence`. The split point character offset is recorded in `assembly_metadata.layer_split_points` (see §2.3.2 AssemblyMetadata). Phase 3 attribution logic (§7.1 F-DET-3) MUST treat split-point layer boundaries as non-meaningful — consecutive layer segments with the same `layer_type` and `author_canonical_id` separated only by a recorded split point are treated as a single attribution span, preventing artificial attribution transitions at split boundaries. Footnotes are assigned to the chunk that contains their `⌜N⌝` marker.

**Content unit assignment for split chunks:** All chunks from the same split share the same `constituent_unit_indices` (the original division's full range) because splitting operates on the assembled text, not on content units. The `assembled_text` of each chunk is a substring of the original assembly. Per I-AC-4, this is the correct behavior.

### §4.6 — Text Layer Rebasing

Normalization provides `text_layers` per content unit with character offsets relative to that unit's `primary_text`. After cross-page assembly, these offsets must be translated to the assembled-text coordinate system.

**Rebasing algorithm:** For each content unit in the assembly order, add the cumulative character offset (including separators) to each layer segment's `start` and `end` values. Validated implementation: `rebase_text_layers()` in `extract_divisions.py`.

**Layer segment merging:** After rebasing, if two adjacent segments (from consecutive content units) have the same `layer_type` and `author_canonical_id`, merge them into a single segment spanning both ranges. This reduces segment count and simplifies downstream processing.

**Validation (I-AC-2):** After rebasing, verify that the union of all segment character ranges exactly covers `[0, len(assembled_text))`. No gaps, no overlaps. If this invariant fails, emit `EX-A-003` (layer coverage failure) — this indicates a bug in rebasing or a malformed normalization output.

**Clamping:** If a layer segment's `end` exceeds its content unit's `primary_text` length, clamp to the text length and emit `EX-A-004` (layer segment overflow, warning). This handles edge cases where normalization produced slightly off offsets.

### §4.7 — Content Flag and Footnote Aggregation

**Content flags:** OR-aggregate across all constituent content units. If any unit in the chunk has `has_verse == true`, the chunk has `has_verse == true`. Same for all boolean flags. Validated implementation: `aggregate_content_flags()` in `extract_divisions.py`.

**Footnotes:** Collect all `Footnote` objects from constituent content units in order. Deduplicate by `ref_marker` — if two units have a footnote with the same `ref_marker`, keep the first occurrence and emit `EX-A-005` (duplicate footnote marker, warning).

**Footnote renumbering:** When assembling text across pages, footnote reference markers may collide (two pages both have `⌜1⌝`). If collisions exist, renumber footnotes sequentially by order of first appearance in the assembled text. Update both the `⌜N⌝` markers in `assembled_text` and the `ref_marker` fields in the `footnotes` list. Record the old→new mapping in `assembly_metadata.footnote_renumber_map` for traceability.

**CRITICAL ORDERING:** Footnote renumbering modifies `assembled_text` (changing character offsets when marker lengths change, e.g., `⌜1⌝` → `⌜12⌝`). This step runs as part of step 5 (§4.1), BEFORE text layer rebasing (step 6). Layer rebasing operates on the final `assembled_text` — the version after footnote renumbering. If renumbering changes any character offsets, the `word_count` and `total_tokens` are also recomputed from the final text. The `assembled_text` is write-once after this step — no subsequent phase may modify it (§2.3.6 Immutability).

**Physical pages:** Collect `PhysicalPage` records from all constituent content units in `unit_index` order. No deduplication — each page contributes one record.

### §4.8 — Heading Alignment Filter

From the experiment: heading-content misalignment (where a division's heading does not match its actual content) produces garbage LLM results. The heading alignment filter detects this.

**Algorithm:** Strip Arabic noise characters from both the division's `heading_text` and the first 200 characters of `assembled_text` for comparison purposes only. The stripped characters are: U+200C (ZWNJ), U+200D (ZWJ), U+0640 (tatweel/kashida), and Arabic diacritics U+064B–U+0652 (fathatan through sukun) and U+0670 (superscript alef). This stripping is applied to temporary copies — the actual `assembled_text` and `heading_text` are never modified (this does not conflict with §4.3's diacritics preservation rule, which governs the stored text). The canonical stripping function is `strip_arabic_noise()` in `extract_divisions.py`. Check if the first 30 stripped characters of the heading appear within the first 200 stripped characters of the assembled text.

**Result:** Sets `heading_alignment_ok` on the `AssembledChunk`:
- `true`: heading aligns with content.
- `false`: heading does not align. Emit `EX-A-006` (heading misalignment, warning). The chunk is still processed — this is a quality flag, not a gate. Phase 2 may produce lower-quality results for misaligned chunks, but skipping them would mean data loss.

**Threshold note:** The experiment found 40–60% rejection rates with strict alignment (15 chars in first 100 chars). The relaxed check (30 chars in first 200 chars) is used here to avoid excessive flagging. The threshold may be calibrated during build evaluation.

### §4.9 — Phase 1 Self-Validation

After all chunks are produced, run these validation checks before passing to Phase 2. Validation failures are categorized as fatal (processing stops) or warning (processing continues with flags).

**V-P1-1 (Division coverage):** Every leaf division in the division tree maps to ≥1 `AssembledChunk`, or is explicitly listed as skipped with a reason code. Fatal if a division is neither processed nor skipped — indicates a bug in tree walking.

**V-P1-2 (Content unit coverage):** The union of all chunks' `constituent_unit_indices` covers all non-skipped content units. Specifically: for every `unit_index` from 0 to `total_content_units - 1`, the unit is either (a) in at least one chunk's `constituent_unit_indices`, or (b) belongs to a skipped division, or (c) its content flags indicate it should be skipped (`is_toc_page`, `is_index_page`, `is_blank`). Fatal if any content unit is silently lost — this is data loss.

**V-P1-3 (No empty chunks):** Every `AssembledChunk` has `word_count > 0`. Warning if violated (indicates a merge/split edge case).

**V-P1-4 (No oversized chunks):** Every `AssembledChunk` has `word_count <= OVERSIZED_DIVISION_WORDS`. Warning if violated (indicates a splitting failure).

**V-P1-5 (Layer coverage):** For every `AssembledChunk`, the text layer invariant I-AC-2 holds: every character in `assembled_text` is covered by exactly one `text_layers` segment. Fatal if violated — downstream phases depend on layer attribution.

**V-P1-6 (Word count consistency):** For every `AssembledChunk`, `word_count` equals the Arabic word counter applied to `assembled_text`, and `total_tokens` equals `len(assembled_text.split())`. Fatal if violated — indicates a computation bug.

**Validation output:** A list of validation results (pass/fail/warning per check) written to the source's processing log. If any fatal check fails, Phase 1 output is not passed to Phase 2. The source is flagged with `EX-V-001` for investigation.

---

## §5 — Phase 2: LLM Teaching Unit Extraction

Phase 2 transforms each `AssembledChunk` (§2.3.2) into a list of `TeachingUnit` objects (§2.3.4) via two sequential LLM calls. This is the engine's inference core — the only phase that calls an LLM. Every other phase is fully deterministic.

The approach is **Approach B (classify-then-group)**, validated across 23 divisions in 7 formats (experiments `run_tests.py` and `format_diversity_test`). Approach A (single-call extraction) was also validated but rejected because Approach B provides more architectural control points: classification results can be validated independently before grouping, and the two-step design enables targeted retries (retry classification without re-doing grouping, or vice versa).

**D-011 enforcement (structural):** Phase 2 processes one `AssembledChunk` at a time. The LLM receives only that chunk's `assembled_text` — it has no access to text from other chunks. Cross-chunk teaching units are therefore impossible by construction, not by validation. This is the primary defense against T-4 (Context Loss) at the structural level.

### §5.1 — Processing Overview

For each `AssembledChunk` produced by Phase 1, Phase 2 executes:

1. **Phase 2a — Segment Classification (§5.2):** The LLM classifies the chunk's text into `ClassifiedSegment` objects, each spanning a contiguous run of words serving a single scholarly function.

2. **Offset Normalization (§5.4.1):** The raw LLM-produced word offsets are remapped to the canonical tokenization (`assembled_text.split()`), using `text_snippet` fields as alignment anchors.

3. **Coverage Verification — Segments (§5.4.2):** Verify that the normalized segments satisfy invariants I-CS-1 through I-CS-6.

4. **Phase 2b — Teaching Unit Grouping (§5.3):** The LLM groups the classified segments into `TeachingUnit` objects — self-contained pedagogical units that each teach one distinct concept, ruling, or argument.

5. **Coverage Verification — Units (§5.4.3):** Verify that the teaching units satisfy invariants I-TU-1 through I-TU-9.

Steps 1–3 must succeed before step 4 begins. If classification fails after retries, the chunk is flagged with `EX-C-001` and excluded from further processing. If grouping fails after retries, the chunk is flagged with `EX-C-002`.

**Per-source ordering:** Chunks from the same source are processed sequentially (by `div_id` order). Chunks from different sources may be processed in parallel.

### §5.2 — Phase 2a: Segment Classification

Phase 2a sends the chunk's assembled text to the LLM and receives back a list of classified segments covering the full text.

#### §5.2.1 — Input

The LLM receives:
- The full `assembled_text` of the `AssembledChunk`
- The chunk's `structural_format` (for contextual awareness — the LLM adapts its segmentation granularity to the format)

#### §5.2.2 — LLM System Prompt

The classification prompt is adapted from the experiment's `APPROACH_B_CLASSIFY_SYSTEM`, with production additions marked. The full prompt text:

```
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

Classify each sentence or closely bonded group of sentences in this Arabic text
by scholarly function. The scholarly function types are:

  definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
  evidence_qiyas, evidence_rational, opinion_statement, refutation, example,
  condition_exception, cross_reference, narration, editorial_note,
  structural_transition, unclassified

Segment boundary rules:
- An isnad chain + its matn = one segment (narration or evidence_hadith)
- A position marker ("قال X") + the stated position = one segment
- Each Quran citation with its introduction = one segment
- A condition + its result ("إذا ... فـ") = one segment
- Each distinct sentence or bonded group gets exactly one classification
- Consecutive sentences serving the same function may form one segment
  if they are tightly bonded (e.g., a two-sentence definition)

For each segment, provide:
- segment_index: 0-based position in the sequence
- start_word: approximate start word offset in the text
- end_word: approximate end word offset in the text (inclusive)
- text_snippet: the FIRST 50 CHARACTERS of this segment's text, copied EXACTLY
  from the input — preserve all diacritics, punctuation, and whitespace precisely.
  This field is used for alignment; exact copying is critical.
- scholarly_function: one of the 16 types listed above
- confidence: your classification confidence from 0.0 to 1.0

The text format is: {structural_format}
```

**Adaptation notes (differences from experiment prompt):**
- Added: `confidence` field instruction (experiment schema had it but prompt didn't explicitly request it)
- Added: condition + result bonded rule (from atomization SPEC §4.A.2 AB-2; experiment relied on implicit LLM understanding)
- Added: consecutive-sentences-same-function rule (clarifies that segments can span multiple sentences)
- Added: structural_format context (the experiment tested per-division; production includes format as context)
- Preserved: all original experiment boundary rules exactly
- Removed: nothing from experiment prompt

**Implementation note:** The word "approximate" in the prompt (for `start_word` and `end_word`) is deliberate — it reduces LLM effort on offset precision, which the normalization algorithm (§5.4.1) handles post-hoc using `text_snippet` as the alignment anchor. CC should not attempt to improve offset accuracy in the prompt. The `text_snippet` field is the critical alignment input, not the offset numbers.

#### §5.2.3 — User Message

The user message contains only the assembled text, wrapped for clarity:

```
<text>
{assembled_text}
</text>
```

No additional context is provided. The system prompt carries all instructions. The text is the sole input.

#### §5.2.4 — Response Schema

The LLM returns structured output enforced via a Pydantic model (using the Instructor library or equivalent structured output enforcement). The schema:

**ClassificationResult:**

| Field | Type | Description |
|-------|------|-------------|
| `segments` | `list[ClassifiedSegment]` | The classified segments, ordered by position. |
| `total_segments` | `int` | Count of segments (must equal `len(segments)`). |

**ClassifiedSegment** fields match §2.3.3. The LLM produces raw offsets in its own tokenization; these become canonical after offset normalization (§5.4.1).

On schema validation failure (missing fields, wrong types, values outside enum), the structured output library retries automatically with the validation error message appended. Up to 2 retries per chunk (§5.5).

#### §5.2.5 — Model and Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `anthropic/claude-opus-4.6` via OpenRouter | Highest classification accuracy. Validated in experiment. |
| Temperature | `0` | Deterministic classification. |
| MAX_TOKENS | Dynamic — see §5.5.1 | Classification output scales with input length. |

### §5.3 — Phase 2b: Teaching Unit Grouping

Phase 2b receives the classified segments (post-normalization) and the original text, then groups segments into self-contained teaching units.

#### §5.3.1 — Input

The LLM receives:
- The full `assembled_text` of the `AssembledChunk`
- The classification result: a summary of each segment (index, word range, function, snippet)
- The chunk's `structural_format`

The classification summary is formatted as a structured list in the user message (§5.3.3), not embedded in the system prompt. This keeps the system prompt stable across chunks.

#### §5.3.2 — LLM System Prompt

The grouping prompt is adapted from the experiment's `APPROACH_B_GROUP_SYSTEM`, with production additions for self-containment evaluation, segment index tracking, and decontextualization prevention. The full prompt text:

```
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

You previously classified segments of this Arabic text by scholarly function.
Now group these classified segments into TEACHING UNITS — self-contained
scholarly segments that each teach one distinct concept, ruling, or argument.
A teaching unit is the smallest segment a student could study and learn
something complete from.

GROUPING RULES:
- **EE-1 (Explained-explanation unity):** An explained object and its
  immediately following explanation form one teaching unit by default.
  The explained text is context for the explanation — separating them
  orphans the explanation. This applies to: hadith + sharh, verse (matn)
  + commentary, definition + examples, principle + reasoning, ruling +
  evidence. Split only when a different scholarly function boundary begins
  (e.g., transition from explanation to scholarly_disagreement).
- A position (opinion_statement) + its evidence + any counter-evidence
  + conclusion = one unit
- A definition + its examples = one unit
- A hadith + its chain + commentary = one unit (for hadith citations
  within broader discussions — NOT for derived benefits sections).
- **Derived Benefits Rule:** Sections opening with "ما يؤخذ من الحديث:"
  or "فوائد:" split per numbered item. Each numbered benefit is a
  separate teaching unit. Exception: consecutive items that are fragments
  of one immediate ruling cluster AND are individually under 20 words may
  be grouped. If uncertain whether items are same-topic or different-topic,
  SPLIT. (This split-on-uncertainty rule is specific to derived benefits
  and numbered items. For general grouping, prefer keeping related content
  together per EE-1 — overgranulation is more harmful than
  undergranulation, FP-9.)
- The hadith text + gharib + المعنى الإجمالي form the inseparable core
  of a hadith commentary unit. Fawa'id/ما يؤخذ points may be separate.
- **Numbered Item Boundaries:** Numbered items (1-, 2-, 3-... or
  فائدة/مسألة + numbering) are strong unit boundary markers. Each is a
  separate unit unless explicitly continuing the same argument. Two items
  covering different topics MUST NOT be merged (e.g., items about void
  bequests and burial are separate units). Exception: consecutive sub-20-word
  items in the same ruling cluster may be grouped. If uncertain, split.
- A question and its answer belong in the same unit
- A rule_statement + its condition_exception(s) = one unit
- Never group unrelated content (e.g., two different مسائل) into one unit
- structural_transition segments may be grouped with the content they introduce,
  or stand alone if they serve as section markers

DECONTEXTUALIZATION PREVENTION (critical):
- A reported position ("قال أبو حنيفة...") and its refutation
  ("ورد عليه بأن...") MUST be in the same unit
- A counter-argument MUST include enough of the original argument to be
  understood on its own
- Evidence cited for a ruling MUST stay with the ruling
- A condition and its exception (rule + إلا clause) belong together
- A verdict/tarjīḥ phrase (والصواب، الراجح، الأصح، المعتمد، الأقوى) that
  selects among competing positions MUST remain with the alternatives it
  judges. Without the alternatives, the verdict reads as a standalone
  ruling and the reader cannot evaluate the reasoning.
- Qualifications and disclaimers (لكن، غير أن، إلا أن، على خلاف) MUST
  remain with the statement they qualify. A rule without its qualification
  is actively misleading.
- A question (فإن قيل، سؤال، اعترض) and its answer (قلنا، الجواب، وأجيب)
  MUST be in the same unit — even when multiple question-answer cycles
  appear in sequence

SELF-CONTAINMENT EVALUATION:
For each teaching unit, evaluate self-containment against these criteria:

C-SC-1 (Term Resolution): Every technical term is either defined within the
  unit, is standard terminology any student of the science would know, or is
  flagged as requiring external knowledge.

C-SC-2 (Reference Resolution): Every pronoun, demonstrative, anaphoric
  reference, or IMPLIED dependency resolves within the unit. No dangling
  references to text outside the unit. Watch for:
  - Visible: هذا/هذه/هؤلاء, المذكور/ما تقدم/ما سبق, pronoun suffixes
    (ـه/ـها/ـهم/ـهما), opening conjunctions (لأن/فإن)
  - Invisible (taqdir): implied subjects in قال/ذهب/رأى where the speaker
    is determined from prior context, not stated in this unit
  Note: opening و does NOT always indicate a dangling reference — it may
  simply continue within the same topic. Reason about whether each referent
  (visible or implied) resolves inside the unit. Do not flag blindly.

C-SC-3 (Evidence Completeness): Every evidence citation either includes its
  text, is a universally known citation identifiable by its opening words
  (e.g., حديث "إنما الأعمال بالنيات"), or is flagged.

C-SC-4 (Argument Completeness): The unit's argument, ruling, or teaching is
  complete — not a fragment whose premise or conclusion is elsewhere.

C-SC-5 (Dialogue Completeness): If the unit responds to another scholar's
  position, enough of that position is included to understand the response.

Assign self_containment as:
- FULL: All five criteria met. The unit stands alone.
- PARTIAL: Most criteria met, but some context would help. Populate
  self_containment_notes describing what's missing.
- DEPENDENT: Cannot be understood alone. Populate self_containment_notes
  explaining the dependency.

For each teaching unit, provide:
- unit_index: 0-based position in the sequence
- segment_indices: list of segment_index values composing this unit
  (must be a contiguous ascending sequence, e.g. [3, 4, 5])
- start_word: the start_word of the first constituent segment
- end_word: the end_word of the last constituent segment
- text_snippet: the FIRST 80 CHARACTERS of this unit's text, copied EXACTLY
  from the input — preserve all diacritics, punctuation, and whitespace.
- primary_function: the dominant scholarly function (must be a function present
  in the constituent segments)
- secondary_functions: other functions present in the unit (may be empty)
- description_arabic: a brief Arabic description of what this unit teaches,
  5 to 35 Arabic words. Write it as a student-facing summary.
- self_containment: FULL, PARTIAL, or DEPENDENT
- self_containment_notes: present and non-empty for PARTIAL/DEPENDENT;
  absent or null for FULL

The text format is: {structural_format}
```

**Adaptation notes (differences from experiment prompt):**
- Added: `segment_indices` field instruction (new field — experiment had only word ranges)
- Added: full self-containment criteria C-SC-1–5 (experiment had one-sentence instruction; production embeds the formal criteria)
- Added: `self_containment` 3-level enum (experiment used binary `self_contained`)
- Added: `description_arabic` target range 5–35 words (experiment said "10-30"; relaxed per §2.3 Finding 2)
- Added: decontextualization prevention rules (from §6.1, embedded here because the LLM needs them during grouping)
- Added: structural_transition grouping guidance
- Added: structural_format context
- Changed: self_containment_notes requirement aligned with I-TU-6/I-TU-7 (must be absent for FULL)
- Preserved: all original experiment grouping rules

#### §5.3.3 — User Message

The user message contains the text and the classification summary:

```
<text>
{assembled_text}
</text>

<classified_segments>
{for each segment:}
Segment {segment_index}: words {start_word}–{end_word}, function={scholarly_function}, snippet="{text_snippet}"
{end for}
</classified_segments>
```

The segment summary uses the **post-normalization** word offsets (canonical tokenization). The LLM sees the segments anchored to the actual text via both word ranges and snippets.

#### §5.3.4 — Response Schema

**ExtractionResult:**

| Field | Type | Description |
|-------|------|-------------|
| `teaching_units` | `list[TeachingUnit]` | The grouped teaching units, ordered by position. |
| `total_units` | `int` | Count of units (must equal `len(teaching_units)`). |
| `notes` | `str` (optional) | LLM notes on grouping decisions, if any. |

**TeachingUnit** fields match §2.3.4. The engine always computes `start_word` and `end_word` from the constituent segments' normalized offsets — it does not use the LLM's values for these fields. The LLM references segments by index; the engine derives `start_word = segments[segment_indices[0]].start_word` and `end_word = segments[segment_indices[-1]].end_word`. V-P2-14 compares the LLM's values against the derived values as a sanity check (warning, not fatal — see §5.4.3).

On schema validation failure, same retry policy as §5.2.4.

#### §5.3.5 — Model and Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `anthropic/claude-opus-4.6` via OpenRouter | Consistent with classification. Grouping requires understanding scholarly argument structure. |
| Temperature | `0` | Deterministic grouping. |
| MAX_TOKENS | `16384` | Grouping output is smaller than classification (fewer objects, each with more fields). 16384 is sufficient for the largest validated case (41 units at 3111 words). |

### §5.4 — Coverage Verification and Offset Normalization

This section specifies how the raw LLM output is validated and transformed into the canonical representation that downstream phases depend on. It has three parts: offset normalization (§5.4.1), segment verification (§5.4.2), and unit verification (§5.4.3).

#### §5.4.1 — Offset Normalization

**The problem:** The experiment revealed that the LLM produces word offsets using its own internal tokenization, which does not match Python's `text.split()`. The offsets are internally consistent — across 162 segment boundaries in the Taysir div_661 test (3111 words), there were 0 gaps between consecutive segment boundaries. But the LLM's final offset (4172) exceeded the Python token count (3643) by 14.5%. The LLM's offsets are self-consistent but not directly usable for text extraction.

**The solution:** Use `text_snippet` fields as alignment anchors to remap LLM offsets to the canonical tokenization.

**Canonical tokenization:** `assembled_text.split()` — Python whitespace split. This produces a list of tokens indexed 0 through `total_tokens - 1`. All word offsets in `ClassifiedSegment` and `TeachingUnit` (§2.3.3, §2.3.4) use this coordinate system after normalization.

**Algorithm:**

The normalization processes the segments in order (by `segment_index`) and maps each segment's start position to a canonical token index using its `text_snippet` as an anchor.

**Step 1 — Build token-to-character mapping.** Split `assembled_text` by whitespace. For each token, record its character start and end offset in the original string. This creates a lookup from character position to token index.

**Step 2 — Anchor each segment.** For each segment `s` in order (0, 1, 2, ...):

(a) Take `s.text_snippet` (the first 50 characters of the segment's text, as copied by the LLM from the input).

(b) Search for `s.text_snippet` in `assembled_text` starting from `search_start_char` (initially 0, updated after each successful match). The search must find the snippet at or after the previous segment's matched position. This left-to-right constraint prevents misalignment from duplicate snippets.

(c) If the snippet is found at character position `match_char`:
   - Find the token whose character range contains `match_char`. That token's index is the segment's canonical `start_word`.
   - Update `search_start_char` to `match_char + 1` for the next segment.

(d) If the snippet is not found with exact matching, attempt **whitespace-normalized matching**: collapse runs of whitespace in both the snippet and the search region to single spaces, then retry. Arabic text may have inconsistent whitespace around diacritics or punctuation.

(d2) If the whitespace-normalized match also fails, attempt **diacritic-stripped matching**: strip Arabic diacritics (U+064B–U+0652, U+0670) from both the snippet and the search region, then retry. The LLM may occasionally drop or add a diacritic in the copied snippet despite being instructed to copy exactly. If this match succeeds, use the match position but emit a warning `EX-A-012` (diacritic-mismatched snippet) for quality monitoring. This warning does not affect processing — the match position is correct.

(e) If the snippet is still not found after all three matching attempts, the normalization has failed for this segment. See failure handling below.

**Step 3 — Infer boundaries from contiguity.** After all segments are anchored:
- `segment[0].start_word` is set from its anchor (must be 0 — validated in §5.4.2).
- For each pair of consecutive segments `s[i]` and `s[i+1]`: `s[i].end_word = s[i+1].start_word - 1`.
- `segment[-1].end_word = total_tokens - 1`.

This leverages the LLM's internal contiguity (verified empirically) to infer exact boundaries from anchor positions. The anchor locates the start; contiguity determines the end.

**Step 4 — Validate invariants.** Run the checks in §5.4.2. If any invariant is violated, the normalization result is rejected.

**Failure handling:**
- If any segment's snippet cannot be located (step 2e), the entire classification result is rejected. The chunk is retried with the classification prompt (up to 2 retries total per §5.5). The retry includes an error feedback message: "The previous classification produced a text_snippet that could not be located in the source text. Ensure each text_snippet is copied exactly from the input."
- If step 3 produces a negative word range (a segment's end_word < start_word), the result is rejected and retried.
- If all retries are exhausted, the chunk is flagged with `EX-C-003` (offset normalization failure) and excluded from Phase 2b.

**Design rationale:** This algorithm assumes the LLM's segment ordering matches the text's reading order (left-to-right, top-to-bottom). The experiment confirmed this: across all 23 validated divisions, the LLM always produced segments in text order with monotonically increasing offsets. The left-to-right search constraint (step 2b) is both a correctness guarantee and a disambiguation mechanism for duplicate snippets.

#### §5.4.2 — Segment Coverage Verification

After offset normalization, verify the invariants from §2.3.3:

**V-P2-1 (Segment ordering):** `segment_index` values form the sequence 0, 1, 2, ..., N-1 (I-CS-1). Fatal if violated.

**V-P2-2 (Segment contiguity):** For every consecutive pair `s[i]`, `s[i+1]`: `s[i+1].start_word == s[i].end_word + 1` (I-CS-2). Fatal if violated. (Note: this is guaranteed by the step 3 boundary inference, but verified explicitly as a consistency check.)

**V-P2-3 (First segment starts at 0):** `segments[0].start_word == 0` (I-CS-3). If the first segment's anchor resolves to a token other than 0, the text before the anchor is unclassified — this is a classification gap. Fatal.

**V-P2-4 (Last segment covers end):** `segments[-1].end_word == total_tokens - 1` (I-CS-4). Guaranteed by step 3 but verified explicitly. Fatal if violated.

**V-P2-5 (Full coverage):** The union of all segment word ranges covers `[0, total_tokens - 1]` (I-CS-5). This is a logical consequence of V-P2-2 + V-P2-3 + V-P2-4 but verified explicitly as the master check. Fatal if violated.

**V-P2-6 (Confidence range):** Every segment's `confidence` is in `[0.0, 1.0]` (I-CS-6). Enforced by schema validation. Warning if violated (clamp to range).

**V-P2-7 (Non-empty segments):** Every segment's `end_word >= start_word` (at least one token). Fatal if violated.

**V-P2-8 (Scholarly function validity):** Every segment's `scholarly_function` is a valid `ScholarlyFunction` enum value. Enforced by schema validation. Fatal if violated.

**V-P2-9 (Total segments consistency):** `total_segments == len(segments)`. Warning if mismatched (use actual list length).

On any fatal violation: reject the classification result, retry per §5.5.

#### §5.4.3 — Teaching Unit Coverage Verification

After Phase 2b produces teaching units, verify the invariants from §2.3.4:

**V-P2-10 (Unit ordering):** `unit_index` values form the sequence 0, 1, 2, ..., M-1 (I-TU-1). Fatal if violated.

**V-P2-11 (Segment indices contiguous):** Each unit's `segment_indices` is a contiguous ascending sequence (I-TU-2). No gaps (e.g., `[3, 5]` is invalid) and no reversals. Fatal if violated.

**V-P2-12 (Complete segment assignment):** The union of all `segment_indices` across all units equals `{0, 1, ..., total_segments - 1}` (I-TU-3). Every segment is assigned to exactly one unit. Fatal if violated.

**V-P2-13 (Unit contiguity):** For consecutive units `u[i]`, `u[i+1]`: `u[i+1].start_word == u[i].end_word + 1` (I-TU-4). Fatal if violated.

**V-P2-14 (Word range consistency):** Each unit's `start_word` equals the `start_word` of its first constituent segment, and its `end_word` equals the `end_word` of its last constituent segment (I-TU-5). Warning if the LLM's values differ from the derived values (log the discrepancy for monitoring LLM reliability, but always use the derived values). The implementation derives these from the segment data rather than trusting the LLM's values.

**V-P2-15 (Self-containment notes consistency):** If `self_containment` is `FULL`, then `self_containment_notes` must be null/absent (I-TU-6). If `self_containment` is `PARTIAL` or `DEPENDENT`, then `self_containment_notes` must be present and non-empty (I-TU-7). Warning if violated (auto-repair: set notes to null for FULL; set to "No notes provided" for PARTIAL/DEPENDENT — but flag for review).

**V-P2-16 (Description range):** `description_arabic` contains 5–35 Arabic words (I-TU-8). Warning if outside range (do not reject — the field is informational).

**V-P2-17 (Primary function grounding):** The unit's `primary_function` is one of the `scholarly_function` values present in its constituent segments (I-TU-9). Warning if violated (the LLM may have synthesized a higher-level function; log but do not reject).

**V-P2-18 (Total units consistency):** `total_units == len(teaching_units)`. Warning if mismatched (use actual list length).

**V-P2-19 (Non-empty units):** Every unit has at least one segment in `segment_indices`. Fatal if violated.

On any fatal violation: reject the grouping result, retry Phase 2b per §5.5. Classification results are reused — only the grouping call is retried.

### §5.5 — Operational Constraints

#### §5.5.1 — MAX_TOKENS Scaling

The classification call's output size scales with input length (more text → more segments). The experiment validated:

| Input words | Classify segments | Teaching units (group) | MAX_TOKENS needed |
|-------------|-------------------|----------------------|-------------------|
| 451–1270 | Not measured (< classify for 2500w range) | 8–21 | < 8192 (classify fits in default) |
| 2513–3111 | 125–166 | 19–41 | ≥ 32768 (classify output requires it) |

The classify call produces significantly more objects than the group call (125–166 segments vs. 19–41 units for the 2500–3100w range). The MAX_TOKENS constraint is driven by the classify call, not the group call.

**Scaling rule:**
- Chunks with `word_count <= 1500`: MAX_TOKENS = `8192`
- Chunks with `word_count > 1500`: MAX_TOKENS = `32768`
- Chunks with `word_count > 4000`: MAX_TOKENS = `32768` (provisionally — must be tested during build; if classify output truncates at this size, escalate to `65536`)

> **Empirical calibration (2026-03-28):** Threshold lowered from 2000 to 1500. ibn_aqil_v3 حروف الجر chunk (1987 words, 15 layers) exceeded 8192 tokens on classification output at the 2000-word threshold.

The grouping call uses a fixed MAX_TOKENS of `16384`. The largest validated grouping output was 41 units (Taysir div_661 at 3111 words), well within this limit.

**Design extension note:** The `word_count > 4000` threshold is untested — no experiment division exceeded 3111 words. Phase 1 splits divisions at 5000 Arabic words (§4.5), so chunks of 4000–5000 words are possible. Build evaluation must test MAX_TOKENS sufficiency for these cases.

#### §5.5.2 — Retry Policy

Each LLM call (classify and group, independently) is retried up to **2 times** on failure, for a maximum of 3 attempts per call per chunk.

**Retry triggers:**
- Schema validation failure (structured output library handles automatically)
- Offset normalization failure (§5.4.1 step 2e — snippet not found)
- Coverage verification failure (§5.4.2 or §5.4.3 fatal checks)
- API error (timeout, rate limit, server error)

**Retry behavior:**
- Schema failure: the structured output library appends the validation error to the next attempt's prompt automatically.
- Offset normalization failure: append the error feedback message specified in §5.4.1.
- Coverage failure: append a message describing which invariant was violated (e.g., "Previous output had a gap between segments 4 and 5 — ensure all text is covered").
- API error: exponential backoff — wait 2^attempt seconds (2s, 4s) before retrying.

**After all retries exhausted:**
- Classification failure: flag chunk with `EX-C-001` (classification failed). No Phase 2b attempted.
- Offset normalization failure: flag chunk with `EX-C-003` (normalization failed). No Phase 2b attempted.
- Segment coverage failure: flag chunk with `EX-C-004` (segment coverage invariant violated after retries).
- Grouping failure: flag chunk with `EX-C-002` (grouping failed). Classification result is preserved (it may be useful for diagnostics).
- Unit coverage failure: flag chunk with `EX-C-005` (unit coverage invariant violated after retries).

Flagged chunks are logged with full diagnostic information (the raw LLM responses, the specific invariant that failed, the chunk's assembled_text length) and excluded from Phase 3.

#### §5.5.3 — API Configuration

| Parameter | Value |
|-----------|-------|
| Provider | OpenRouter |
| API key | From environment variable (`OPENROUTER_API_KEY`) |
| Model string | `anthropic/claude-opus-4.6` |
| Temperature | `0` (both calls) |
| Timeout | `120` seconds per call |
| Rate limiting | Respect OpenRouter rate limits; back off on 429 responses |

#### §5.5.4 — Telemetry

Each LLM call logs (for monitoring, not for behavioral decisions):
- `source_id`, `chunk_id`
- Call type (`classify` or `group`)
- Input token count, output token count
- Latency (seconds)
- Retry count (0 if first attempt succeeded)
- Success/failure status

This data enables cost tracking and performance monitoring but does not affect processing logic. No behavioral decisions are made based on telemetry.

#### §5.5.5 — Over-Segmentation Awareness

The experiment revealed that Approach B's two-step design can over-segment compared to Approach A, particularly for longer texts with structural repetition. The most extreme case: Taysir div_661 (3111 words) produced 41 B-units vs. 24 A-units (ratio 1.71x), driven by a repeated hadith-benefits pattern.

The average teaching unit size across all 13 validated divisions ranged from 45 words (Q&A format, 451w input) to 126 words (fiqh prose, 2513w input). The median was approximately 80–90 words per unit.

**Minimum teaching unit viability (MV-1, from DR review 2026-04-04):** Teaching units below **25 Arabic words** are flagged as sub-viable. Sub-viable units are merged with their nearest adjacent unit in reading order as a **post-grouping merge** step. This threshold is based on empirical evidence: DR coworkers independently graded a 5-word unit (TU-5: "استحباب خدمة العلماء والفضلاء") as 1/5 and 2/5 for study-readiness — it functions as a heading, not a teaching unit (ChatGPT DR, Claude DR, 2026-04-04). The ~25 word floor aligns with the minimum context needed for a standalone scholarly note in the mukhtasar tradition.

**Additionally:** Units with `primary_function = cross_reference` that are below 30 words should be considered for demotion to metadata (attached as a cross-reference note to the preceding unit) rather than standalone teaching units. TU-6 (14-word cross-reference about غزوة تبوك) was graded 1/5 by ChatGPT DR and 2/5 by Claude DR — it functions as a pointer, not a study object.

**Implementation:** The viability check runs AFTER Phase 2b grouping and BEFORE Phase 3 enrichment. It does NOT modify the Phase 2b prompt — the LLM groups by scholarly structure, and viability optimization is a separate concern. The merge strategy is:
1. Scan teaching units in reading order for units below 25 words.
2. For each sub-viable unit, merge with the immediately preceding unit (prefer backward merge to maintain reading flow).
3. If the preceding unit is also sub-viable, merge both with the next viable unit forward.
4. If a sub-viable unit is the first unit in the chunk, merge forward.
5. Log every merge with: original unit indices, word counts, merge reason, resulting unit size.
6. Re-evaluate self-containment for the merged unit.

**What the SPEC does NOT commit:** A hard numeric cap as a rejection threshold. The 25-word floor is a merge trigger, not a hard contract invariant. Edge cases (e.g., a 20-word unit that is genuinely a complete ruling) are handled by the LLM's scholarly judgment during the merge re-evaluation — if the merged result is worse than the original, the merge is reverted.

---

## §6 — Domain-Specific Processing Rules

This section defines cross-cutting rules that govern how the engine handles specific patterns in Islamic scholarly texts. These rules apply across multiple phases — Phase 2a (classification), Phase 2b (grouping), and Phase 3 (enrichment) each implement the subset relevant to their scope.

The rules here preserve the domain design from the original excerpting SPEC (§4.A.2–§4.A.7), translated into the new architecture. The old SPEC operated on atoms produced by a separate atomization engine; the new design operates on segments and teaching units produced by the LLM in Phase 2. The domain knowledge is the same; the enforcement mechanism changes from deterministic post-processing to LLM prompt constraints plus deterministic verification.

**Relationship to §5:** Several rules from this section are embedded in the Phase 2b grouping prompt (§5.3.2) as behavioral constraints. §6 is the formal specification — the prompt implements it. If the prompt and §6 ever conflict, §6 governs.

### §6.1 — Decontextualization Prevention

Decontextualized quotation is the highest-risk failure in the excerpting engine. It occurs when a fragment that looks complete actually depends on or responds to content outside the excerpt. The owner reads "Scholar A says X" when the original text says "Scholar A reports Scholar B's view X, but Scholar A disagrees." The excerpt misattributes X to Scholar A — a T-2 (Attribution Error) with epistemic consequences.

**Phase enforcement:**

Phase 2b (grouping) is the primary defense. The following patterns MUST be grouped into a single teaching unit:

**DP-1 (Position + Refutation):** A reported position ("قال أبو حنيفة: لا يجب الترتيب في الوضوء") and its refutation ("ولنا قوله تعالى..." or "ورد عليه بأن...") belong in the same teaching unit. Splitting them means either: (a) the reported position is excerpted without the refutation, making it appear to be the source author's view, or (b) the refutation is excerpted without the position, making "ورد عليه" an unintelligible fragment.

**DP-2 (Question + Answer):** A question ("سؤال: هل يجب الترتيب؟") and its answer ("الجواب: نعم يجب") belong in the same teaching unit. This includes formal Q&A format (فإن قيل / قلنا) and informal dialogue.

**DP-3 (Rule + Exception):** A rule statement and its exception ("يجب الوضوء ... إلا إذا ...") belong in the same teaching unit. An exception without its rule is meaningless; a rule without its exception is misleading.

**DP-4 (Evidence + Ruling):** Evidence cited for a ruling must stay with the ruling. An evidence citation ("لقوله تعالى...") without the ruling it supports is decontextualized — the owner sees a Quranic verse cited but doesn't know what it's evidence for.

**DP-5 (Counter-argument + Original):** A counter-argument must include enough of the original argument to be understood. An excerpt that opens with "وأما قول الشافعي فليس بصحيح لأن..." must include al-Shafi'i's position (or a sufficient summary of it) to make the refutation intelligible. This is C-SC-5 (Dialogue Completeness) from §3.

**DP-6 (Condition + Result):** A conditional statement ("إذا نوى المتوضئ رفع الحدث واستباحة الصلاة أجزأه") is one unit. The condition and its result are semantically bonded — splitting them produces two meaningless fragments.

**Phase 3 responsibility:** When Phase 2b assigns `self_containment: PARTIAL` or `DEPENDENT` due to a decontextualization concern, Phase 3 adds a `context_hint` explaining the dependency (e.g., "This excerpt responds to a position stated in the preceding teaching unit").

**Design note — Khilaf mention vs tarjih (owner F4, 2026-04-04):** The owner identifies a distinction between the unbiased *mapping* of scholarly disagreement (تحرير الخلاف — "scholars disagreed into these opinions") and the scholar's biased *weighting* (ترجيح — "the strongest is X"). These serve different scholarly functions: the خلاف mapping is a neutral fact; the ترجيح is the author's personal attribution. The owner prefers these as separate teaching units when the text structure supports it. The current tarjih decontextualization rule in the prompt ("verdict MUST remain with alternatives") applies when alternatives are only briefly mentioned within the tarjih itself. Full resolution of this tension depends on questionnaire items K-1 through K-3 (scholarly disagreement deep dive) and is DEFERRED to that phase. For now: when a long dispute section (listing multiple opinions with evidence) is followed by a tarjih conclusion, the LLM should consider whether the tarjih is a distinct scholarly function worthy of its own teaching unit.

**Verification:** The DP rules are not independently verifiable by deterministic checks — they depend on Arabic semantic understanding. However, the unit coverage checks (§5.4.3) ensure structural consistency. The 30-book probe (source engine roadmap Step 3) will include adversarial spot-checks where the owner reads excerpts containing reported positions and verifies that the context is preserved.

### §6.2 — Multi-Layer Text Handling

Multi-layer sources (sharh, hashiyah, muhashshah) contain interleaved text from different authors. Correct layer attribution is critical — a wrong author attribution is T-2 (Attribution Error): the owner studies a sharh author's analysis believing it was the matn author's original statement.

**Phase 1 responsibility:** Text layers are rebased to `assembled_text` character offsets (§4.6). Every character in the assembled text is attributed to exactly one layer (I-AC-2). The layer information is available on the `AssembledChunk` but is NOT passed to the Phase 2 LLM. The LLM classifies based on content, not on markup metadata.

**Design rationale for not passing layers to the LLM:** The LLM already understands scholarly text structure — it recognizes "قال ابن مالك" as a matn quotation and "يريد أن الكلام..." as commentary without being told which layer is which. Passing layer metadata would risk the LLM deferring to the metadata rather than analyzing the text, which would mask cases where the layer boundaries are incorrect (the normalization engine's layer detection has known limitations, L-001 through L-012).

**Phase 3 responsibility — Attribution rules:**

For each teaching unit, Phase 3 determines author attribution by overlapping the unit's character range with the `text_layers` segments:

**LA-1 (Single-layer dominance):** If ≥80% of the unit's character range falls within a single layer, attribute the unit to that layer's author. The 80% threshold allows for brief inline quotations (a matn fragment cited within a sharh explanation) without flipping the attribution.

**LA-2 (Mixed-layer default):** If no layer covers ≥80% of the unit, attribute to the sharh/hashiyah author — the commentary author is the one doing the teaching. The matn text is being quoted as context. Specifically: attribute to the outermost (highest-layer) author present in the unit.

**LA-3 (Attribution uncertainty):** If the unit spans text from three or more layers, or if the dominant layer has <60% coverage (neither sharh nor matn clearly dominates), flag the unit with `EX-M-001` (attribution ambiguous) for multi-model consensus verification. The human gate triggers if models disagree.

**LA-4 (Pure matn units):** If 100% of the unit falls within the matn layer (no sharh commentary), the unit is attributed to the matn author. This is correct and expected — some teaching units are pure matn text (e.g., a definition in the Alfiyya that stands alone). These are less common in sharh texts but valid.

**Phase 3 output fields:** The attribution produces `primary_author_layer` (which text layer the unit is attributed to) and `quoted_scholars` (other authors whose text appears within the unit). The `quoted_scholars` field distinguishes:
- `quoted_opinion`: the unit quotes another scholar's view as content
- `classification_frame`: the unit quotes another author's text as the frame being commented on (matn verse in a sharh excerpt)
- `refuted_position`: the unit quotes another scholar's view in order to refute it

**T-2 defense:** Attribution errors are the most dangerous silent failure in multi-layer texts. Structural mitigations:
- The layer attribution is deterministic (character overlap computation), not LLM-inferred — reducing the attack surface to the normalization engine's layer detection accuracy.
- The 80% threshold (LA-1) is conservative — it requires clear dominance.
- Ambiguous cases (LA-3) trigger multi-model consensus and human gate rather than silent default.

### §6.3 — Evidence and Hadith Handling

Fiqh, hadith, and usul al-fiqh texts have specific evidence citation patterns that affect both segmentation (Phase 2a) and metadata enrichment (Phase 3).

**Phase 2a responsibility:** The classify prompt recognizes five evidence types as scholarly functions: `evidence_quran`, `evidence_hadith`, `evidence_ijma`, `evidence_qiyas`, `evidence_rational`. The LLM classifies each evidence citation as a segment with the appropriate function type.

**Phase 2b responsibility:** Evidence segments are grouped with their associated rulings (DP-4). The experiment validated this grouping across all fiqh divisions — the LLM correctly keeps evidence with its ruling without special prompting.

**Phase 2b — Hadith commentary pattern:** In hadith sharh texts (e.g., Taysir al-Allam), hadith discussion often follows a stereotyped sequence: الحديث (the hadith text) → الغريب (unusual vocabulary) → المعنى الإجمالي (overall meaning) → ما يُستفاد (lessons derived). The inseparable core is الحديث + الغريب + المعنى الإجمالي — these form one teaching unit per EE-1 (the hadith is the explained object; gharib and ma'na are its explanation). The ما يُستفاد (derived benefits / فوائد) section splits per numbered item: each numbered benefit is a separate teaching unit, unless consecutive items are fragments of one immediate ruling cluster AND individually under 20 words (see the Derived Benefits Rule in §5.3.2).

**Phase 3 responsibility — Evidence extraction:**

For each teaching unit containing evidence segments:

**EV-1 (Quran references):** When a segment has function `evidence_quran`, Phase 3 attempts to identify the surah and ayah. The identification method is pattern-based:
- Look for ﴿...﴾ delimiters in the segment text
- Match the contained text against a canonical Quran text lookup (pre-loaded reference data)
- If matched, record `{surah, ayah_start, ayah_end}` in `evidence_refs`
- If no match (partial quotation, paraphrase, or allusion), record the segment as Quran evidence with `{type: "quran", surah: null, ayah_start: null, ayah_end: null, text_snippet: <the quoted text>}` for potential future resolution

**EV-2 (Hadith references):** When a segment has function `evidence_hadith`, Phase 3 extracts:
- Narrator name(s) from isnad patterns ("عن X عن Y عن Z")
- Collection name if mentioned ("رواه البخاري", "في الصحيحين", "أخرجه مسلم")
- Hadith number if mentioned
- Grade if stated in the text or in associated footnotes ("صحيح", "حسن", "ضعيف")
- The grade source (who stated the grade: the author, the editor, a cited scholar)

The engine does NOT independently assess hadith authenticity. It records the grades stated in the source text and editor apparatus, with attribution to who stated the grade. Fabricating or inferring grades would be scholarly overreach — a T-1 (Fabrication) violation.

**EV-3 (Consensus references):** When a segment has function `evidence_ijma`, Phase 3 records the scope of the claimed consensus (who is said to agree: all scholars? a specific school? the companions?) from the text.

**Evidence extraction scope:** Surah/ayah identification for well-known Quranic verses is deterministic (pattern match against ﴿...﴾ delimiters + canonical text lookup in F-DET-5). For less common verses, partial quotations, or detailed hadith identification (collection, number, grade), the §7.2 enrichment call produces `takhrij_data` entries. However, the §7.2 call does not update the `evidence_refs` list itself — unresolved references in `evidence_refs` (with `surah: null` or `scope: null`) remain in their partial state. Full LLM-assisted evidence resolution is a deferred capability.

### §6.4 — Implicit Reference Resolution

Islamic scholarly texts use implicit references extensively: "كما تقدم" (as previously mentioned), "المذكور آنفاً" (the aforementioned), "الإمام" (the Imam — context-dependent), "صاحب الكتاب" (the author of the book). These create self-containment gaps (C-SC-2 violations) that must be detected and, where possible, resolved.

**Phase 2b responsibility:** When the LLM detects an unresolvable reference within a teaching unit, it should mark the unit as `PARTIAL` self-containment (not `FULL`) with the reference noted in `self_containment_notes`. The grouping prompt (§5.3.2) instructs the LLM to evaluate C-SC-2 (Reference Resolution) for this purpose.

**Phase 3 responsibility — Resolution attempts:**

**IR-1 (Intra-source cross-reference):** If an implicit reference points to another division in the same source (e.g., "كما تقدم في باب الطهارة"), Phase 3 attempts to resolve it by searching the division tree headings. If a matching division is found, a `cross_reference` is added to the excerpt's metadata: `{target_div_id, reference_text, confidence}`. The self-containment level may be upgraded from `PARTIAL` to `FULL` if the cross-reference makes the unit independently navigable (the owner can follow the link).

**IR-2 (Scholar epithet resolution):** Common scholarly epithets are context-dependent:
- "الإمام" → Ahmad ibn Hanbal in Hanbali texts, al-Shafi'i in Shafi'i texts, Abu Hanifa in Hanafi texts, Malik in Maliki texts
- "الشيخ" → varies by author and context
- "صاحب الكتاب" → the matn author (in sharh texts)
- "المصنف" → the author of the current work

Phase 3 resolves these using source metadata (school affiliation from the source engine's metadata, work relationships from the manifest). When resolution succeeds, the resolved scholar is added to `quoted_scholars`. When resolution fails, the epithet is preserved as-is with a `confidence: null` entry — never silently dropped (D-033, fail-loud).

**IR-3 (Unresolvable references):** When a reference cannot be resolved (e.g., "كما ذكره بعض أصحابنا" — "as some of our companions mentioned" — with no specific source identifiable), Phase 3 records the reference in the excerpt's metadata as an unresolved implicit reference. The self-containment level stays at `PARTIAL`.

**Design extension note:** A scholar authority registry mapping epithets to canonical IDs per school/context is described in the old excerpting SPEC (§4.A.5). This registry is a build-time artifact — populated during the source engine's scholar disambiguation phase and loaded by the excerpting engine. The SPEC defines the lookup behavior; the registry data is populated incrementally as the library grows. For the initial build, the registry contains only the well-known epithet mappings (الإمام per school, المصنف/صاحب الكتاب per work relationship). Must be validated during build evaluation.

### §6.4b — Explained-Explanation Unity

**EE-1 (Default unity):** An explained object and its immediately following explanation form one teaching unit by default. This is the general principle underlying VC-1 (verse + commentary), DP-2 (question + answer), and the grouping rules for hadith + commentary, definition + examples, and rule_statement + condition_exception.

The explained object provides the reference frame; the explanation provides the scholarly analysis. Separating them produces an orphaned explanation (the reader cannot identify what is being explained) and an unexplained object (the reader receives the text without the scholar's analysis).

**Scope:** "Immediately following" means the explanation is structurally adjacent to the explained text within the same division. If the explanation is in a different chapter, section, or structural unit, it is a separate source and does not trigger EE-1.

**EE-1 does not apply when:**
1. The explained text and explanation are in different sources (different books in the library).
2. Phase 2 classification identifies a different scholarly function boundary between them (e.g., the text transitions from EXPLANATION to SCHOLARLY_DISAGREEMENT — the disagreement section is a new teaching unit, not part of the explanation).
3. The combined unit exceeds the chunk size limit and Phase 1 must split them into separate chunks. D-011 prevents cross-chunk grouping by construction — if explained and explanation end up in different chunks, they cannot be reunited in Phase 2. This is a **known limitation**: Phase 1's split logic does not currently carry the explained text forward as context into subsequent chunks. The resulting excerpt in the later chunk will be evaluated as PARTIAL or DEPENDENT by Phase 2b's self-containment assessment, and Phase 3 will add a `context_hint` pointing to the preceding chunk. The source-surroundings mechanism (NC-1) provides the reader access to the full surrounding text. Future improvement: Phase 1 split logic should prefer boundaries AFTER explanation blocks, not between explained/explanation pairs.

**Rationale (owner Q&A F5, 2026-04-04):** In Islamic scholarly texts, an explanation is tightly bound to the specific version, wording, route, and grading of the explained text. A scholar may explain one wording of a hadith, one grading assumption, or one route. Separating the explanation from the explained text forces the reader to hunt for which version the scholar was explaining. The owner opens excerpts to see "how the specific scholar handled it" — the explained text is context, not the primary study object. For hadith memorization, the owner uses authoritative fetched sources, not book-preserved versions.

**Relation to existing rules:** EE-1 generalizes what VC-1 (verse + commentary unity), DP-2 (question + answer), and the hadith + chain + commentary grouping rule already express for specific cases. EE-1 ensures that any new explained/explanation pattern not covered by a specific rule still defaults to unity.

### §6.5 — Verse-Commentary (نظم) Handling

Versified texts (المنظومات) and their commentaries (e.g., Ibn Aqil on the Alfiyya) have specific patterns. A بيت (verse line) is a self-contained unit in the scholarly tradition — scholars cite by line number, and each verse typically encodes one grammatical or legal rule.

**Experiment validation:** The LLM correctly handles verse-commentary text without explicit verse identification. Across 6 verse-commentary divisions in the experiment (ibn_aqil_v1 and ibn_aqil_v3 fixtures), both Approach A and Approach B correctly grouped verses with their commentary as coherent teaching units. The Alfiyya verses function as natural topic delimiters that the LLM recognizes from content.

**Phase 1 responsibility:** No special handling. Text assembly works identically for verse-commentary. The `content_flags.has_verse` field and any `verse_info` from content units are passed through on the `AssembledChunk` but are not used for splitting or merging decisions.

**Phase 2 responsibility:** The LLM naturally groups verse + commentary as one teaching unit. The `structural_format` field provides context (if the source is identified as verse-commentary format), but no special prompting is needed.

**VC-1 (Verse + commentary unity):** A verse (matn) and its immediately following commentary (sharh) form one teaching unit. The verse provides the rule; the commentary provides the explanation. Splitting them produces an unexplained verse and an orphaned commentary.

**VC-2 (Standalone verse validity):** In pure verse texts (no commentary layer), a single verse may constitute a valid self-contained teaching unit if it encodes a complete rule. The self-containment standard (§3) applies: the verse is `FULL` if a student of the science can understand what it teaches; `PARTIAL` if it references another verse or concept not included.

**VC-3 (Multi-verse grouping):** When consecutive verses address the same topic, they may form a single teaching unit. The LLM determines the boundary — a topic shift to a new grammatical or legal concept signals a new unit. The experiment showed the LLM makes reasonable boundary decisions: the Ibn Aqil العلم division (865 words, Approach A: 8 units, Approach B: 13 units) was correctly split at topic boundaries.

**DEFERRED:** Explicit verse-commentary alignment (a Phase 1 preprocessor that identifies verse lines by `verse_info` and ensures each is grouped with its commentary). This is evaluation constraint C-5 — not architecturally required because the LLM handles it, but a quality optimization that could be added if the 30-book probe reveals edge cases where the LLM misgroups verse and commentary.

### §6.6 — Q&A and Masala-Format Handling

Q&A format (سؤال وجواب) and masala format (مسألة enumerated legal issues) have predictable structures that the LLM handles naturally.

**Experiment validation:** The experiment tested 3 divisions with these formats (ext_39_masala and ext_46_qa fixtures). Both approaches correctly identified Q&A pairs and masala blocks as self-contained units.

**Phase 1 responsibility:** Text assembly preserves structural markers — مسألة numbers, سؤال/فأجاب markers, أولا/ثانيا ordinals. These markers appear in the `assembled_text` and help the Phase 2 LLM identify unit boundaries.

**Phase 2 responsibility:**

**QM-1 (Q&A pairs):** A question and its answer form one teaching unit (this is also DP-2 from §6.1). The LLM classifies the question as one segment and the answer as one or more segments, then groups them.

**QM-2 (Masala blocks):** Each مسألة (legal issue) forms one teaching unit if it is self-contained. A masala typically contains: the issue statement, the ruling(s), and supporting evidence. The مسألة marker signals the unit boundary.

**QM-3 (Cross-masala references):** If a masala references a previous masala ("كما في المسألة السابقة"), the reference creates a self-containment gap (C-SC-2). Phase 2b marks the unit as `PARTIAL` and notes the dependency. Phase 3 attempts to resolve the reference to a specific masala (IR-1 from §6.4).

**No special handling beyond marker preservation.** The Q&A and masala formats are well-structured enough that the LLM's general segment classification and grouping produce correct results without format-specific prompting.

---

## §7 — Phase 3: Metadata Enrichment

Phase 3 transforms `TeachingUnit` objects (§2.3.4) into `ExcerptRecord` objects (§2.2) by adding attribution, topic classification, evidence references, and cross-reference metadata. Phase 3 operates on one `AssembledChunk` at a time, enriching all teaching units within that chunk.

Phase 3 has three stages, executed in order:
1. **Deterministic assembly** (§7.1): fields computable from the data model without any LLM call.
2. **LLM enrichment** (§7.2): fields requiring inference — topic classification, school attribution, scholar resolution, takhrij extraction, terminology variants, cross-references, and context hints.
3. **Consensus verification** (§7.3): cross-provider verification for high-epistemic-impact decisions, plus human gate triggers for unresolvable uncertainty.

**Design decision — LLM call granularity:** Phase 3 issues **one LLM enrichment call per chunk** (not per-unit). Rationale: inter-unit context improves quality — when unit 5 references "as mentioned above," the LLM can see unit 3 and resolve the reference. School attribution is more consistent when the LLM sees all units from the same textual context. Topic keywords benefit from seeing the chunk's thematic scope. The per-chunk failure risk is mitigated by deterministic fallback (§7.1 fields survive LLM failure).

**Design decision — no `proposed_leaf`:** The old excerpting SPEC included a `proposed_leaf` field where the LLM proposed a taxonomy tree path. This field is **removed** in the new architecture. The excerpting engine produces `excerpt_topic` (1–3 Arabic topic keywords). The taxonomy engine is responsible for mapping topics to tree positions. Rationale: the taxonomy engine owns the classification tree and may restructure it — pre-proposed paths would be invalidated. Topic keywords are stable, content-descriptive, and useful regardless of tree structure. This maintains a clean engine boundary: excerpting knows content, taxonomy knows structure.

### §7.1 — Deterministic Metadata Assembly

For each `TeachingUnit` in the chunk, Phase 3 computes the following fields without any LLM call. Each field is defined with its computation algorithm and source data.

**F-DET-1: `excerpt_id` and `chunk_index`**

Globally unique identifier for the excerpt. Format: `exc_{source_id}_{div_id}_{chunk_index}_{unit_index}`.

- `source_id`: from the `AssembledChunk.source_id` field.
- `div_id`: from the `AssembledChunk.div_id` field (the division that produced this chunk).
- `chunk_index`: for unsplit chunks (no `split_info`), `chunk_index = 0`. For split chunks, `chunk_index = split_info.chunk_index`. This field is also written to the ExcerptRecord as a top-level field.
- `unit_index`: from the `TeachingUnit.unit_index` field.

Example: `exc_12345_div_3_2_0_7` for unit 7, chunk 0 of division 3.2 in source 12345. For a split division: `exc_12345_div_3_2_1_3` for unit 3 of chunk 1.

Uniqueness invariant: no two excerpts in the library share an `excerpt_id`. This is guaranteed by the combination of unique source_id (from the source engine), unique div_id within a source (from the normalization manifest), unique chunk_index within a division (from Phase 1 splitting), and unique unit_index within a chunk (from Phase 2). The chunk_index component is critical for split divisions — without it, chunks 0 and 1 of the same division would produce identical IDs for matching unit_index values.

**F-DET-2: `primary_text`**

The teaching unit's full Arabic text, extracted from `assembled_text` as a substring preserving all original whitespace.

Algorithm: use the same word-to-character offset conversion defined in F-DET-3 step 1 (split `assembled_text` by whitespace, record each token's character start and end positions). Extract `primary_text = assembled_text[char_start : char_end + 1]` where `char_start` is the character position of the first character of token `start_word` and `char_end` is the character position of the last character of token `end_word`. This preserves all original whitespace (newlines, paragraph breaks, multiple spaces) within the unit's text range.

**Note:** The extraction is a substring, not a split-and-rejoin. The difference matters: `assembled_text` may contain `\n\n` between paragraphs. Substring extraction preserves this structure. Split-and-rejoin would collapse it to a single space, violating I-ER-2 and losing structural information the owner needs for reading.

This text is **immutable** — it is written once and never modified by subsequent processing or engines. It is the text the owner reads in the final library. Correctness depends on the offset normalization guarantee from §5.4.

**F-DET-3: `primary_author_layer`**

The text layer (and therefore author) to which this teaching unit is attributed. Computed by applying the layer attribution rules from §6.2 (LA-1 through LA-4) to the unit's character range within `assembled_text`.

Algorithm:
1. Convert the unit's word offsets (`start_word`, `end_word`) to character offsets in `assembled_text`. **Character offset conversion:** split `assembled_text` by whitespace, recording each token's start and end character positions in the original string. Word offset `w` corresponds to character range `[token_char_start[w], token_char_end[w]]`. The unit's character range is `[token_char_start[start_word], token_char_end[end_word]]`. This same conversion is used by F-DET-6 and F-DET-8.
2. For each `text_layer` segment in `AssembledChunk.text_layers`, compute the character overlap with the unit's character range. **Layer split point handling:** before computing coverage, merge consecutive layer segments that have identical `layer_type` and `author_canonical_id` AND are separated by a character offset listed in `assembly_metadata.layer_split_points`. These segments were artificially divided by §4.5 splitting and represent a single continuous attribution span. Failure to merge them would create false attribution transitions at split boundaries (T-2 risk).
3. Compute each layer's coverage percentage: `overlap_chars / unit_total_chars`.
4. Apply rules in order:
   - **LA-4:** If one layer has 100% coverage, attribute to that layer's author. (Checked first because it's the most specific case.)
   - **LA-1:** If one layer has ≥80% coverage, attribute to that layer's author.
   - **LA-2:** If no layer has ≥80% but the unit spans exactly two layers, attribute to the outermost (highest-layer) author.
   - **LA-3:** If no layer has ≥80% and either (a) three or more layers are present, or (b) the dominant layer has <60% coverage, emit `EX-M-001` (attribution ambiguous). Mark for consensus verification (§7.3).

Output: `{layer_id, author_id, coverage_pct, rule_applied}`. The `rule_applied` field records which rule (LA-1/LA-2/LA-3/LA-4) determined the attribution — this supports auditability and debugging.

For single-layer sources (no sharh/hashiyah), this step is trivial: 100% coverage of the single layer, LA-4 applies. The rule still runs to maintain uniform processing.

**F-DET-4: `content_types`**

Aggregated scholarly function types present in the teaching unit's constituent segments.

Algorithm: collect `scholarly_function` from each `ClassifiedSegment` whose `segment_index` is in the `TeachingUnit.segment_indices`. Deduplicate. The result is a set of `ScholarlyFunction` values (e.g., `{rule_statement, evidence_quran, evidence_rational}`).

This field supports downstream filtering (e.g., "show me all teaching units that contain hadith evidence").

**F-DET-5: `evidence_refs` (structural)**

Structured evidence references detected by pattern matching in the unit's `primary_text`. This is purely deterministic — no LLM involvement. Unresolved references (partial Quran quotes with `surah: null`, hadith markers with only `marker_text` populated) remain in their partial state. The §7.2 enrichment call produces separate `takhrij_data` entries for hadith details but does not update `evidence_refs` entries. Full LLM-assisted evidence resolution (completing partial Quran references, identifying hadith collections from partial quotes) is a deferred capability.

Quran references (EV-1 partial):
1. Scan `primary_text` for ﴿...﴾ delimiters.
2. Extract the text between delimiters.
3. Attempt canonical lookup against a pre-loaded Quran text reference (surah/ayah mapping). The reference data is a build-time artifact.
4. If matched: `{type: "quran", surah: int, ayah_start: int, ayah_end: int, text_snippet: str}`.
5. If no match (partial quote, paraphrase, or allusion): `{type: "quran", surah: null, ayah_start: null, ayah_end: null, text_snippet: str}` — the snippet is preserved for LLM resolution in §7.2.

Hadith markers (EV-2 partial):
1. Scan `primary_text` for hadith citation patterns: رواه, أخرجه, في الصحيحين, متفق عليه, في صحيح, في سنن.
2. If found: `{type: "hadith", surah: null, ayah_start: null, ayah_end: null, text_snippet: <matching text region>, marker_text: <the matched pattern>, scope: null}`. The Quran-specific fields are null for hadith evidence. Detailed hadith information (collection, number, grade) is extracted by the §7.2 enrichment call into `takhrij_data`, not into `evidence_refs`.

Consensus markers (EV-3 partial):
1. Scan `primary_text` for consensus patterns: أجمعوا, إجماع, لا خلاف, اتفق العلماء, بالاتفاق.
2. If found: `{type: "ijma", marker_text: str, scope: null}` — the `scope` field is populated by LLM enrichment.

Pattern matching uses word-boundary-aware search (the lesson from normalization engine S4/S5 — short Arabic stems produce false positives without boundary checks). Each pattern requires the marker to appear at a word boundary (preceded by whitespace/start-of-text and followed by whitespace/punctuation/end-of-text).

**F-DET-6: `physical_pages`**

The physical page range this teaching unit spans in the original printed edition.

Algorithm:
1. Convert the unit's word offsets to character offsets (same conversion as F-DET-3 step 1).
2. The `AssembledChunk.physical_pages` list contains one `PhysicalPage` record per constituent content unit, in order. The `assembly_metadata.join_points` list records the `char_offset_in_assembled` for each page boundary.
3. Identify which physical pages overlap with the unit's character range by comparing the unit's character range against the join point offsets. The physical page before the first join point covers characters 0 to `join_points[0].char_offset_in_assembled - 1`; the page between join points covers the range between consecutive offsets; and so on.
4. From the overlapping physical pages, extract the minimum and maximum page numbers and volume.

Output: `PageRange: {volume: int | null, start_page: int, end_page: int}` (type defined in §2.2.2). If physical page information is unavailable (some Shamela exports lack it, or the `physical_pages` list is empty), this field is `null`.

**F-DET-7: `div_path`**

The heading hierarchy path from the source's table of contents to the division containing this chunk.

Source: `AssembledChunk.div_path` — a list of heading strings from the manifest's division tree, root to leaf (defined in §2.3.2).

Output: `list[str]` — e.g., `["كتاب الطهارة", "باب الوضوء", "فصل في فرائض الوضوء"]`.

**F-DET-8: `footnotes_relevant`**

The subset of the chunk's footnotes that have reference markers appearing within this teaching unit's text range.

Algorithm:
1. The `AssembledChunk.footnotes` contains all footnotes for the chunk, each with a `ref_marker` field. The `Footnote` object does not carry a pre-computed character offset in `assembled_text`. Instead, locate each footnote's position by searching `assembled_text` for the pattern `⌜{ref_marker}⌝`.
2. Convert the unit's word offsets to character offsets (same conversion as F-DET-3 step 1).
3. For each footnote, if the pattern `⌜{ref_marker}⌝` is found in `assembled_text` and the match's character position falls within the unit's character range, the footnote is relevant to this unit.
4. If a footnote's marker pattern is not found anywhere in `assembled_text`, this indicates a data integrity issue (the footnote was collected but its marker is missing from the text) — log a warning but do not include the orphaned footnote.
5. Return the selected footnotes with their full text.

Footnotes outside the unit's range are excluded — they belong to other teaching units from the same chunk. No footnote is dropped from the chunk-level data (D-023 metadata passthrough); the filtering is per-excerpt for relevance.

**F-DET-9: `quoted_scholars` (structural)**

Other text layer authors whose text appears within this teaching unit but who are NOT the `primary_author_layer`.

Algorithm: from the layer overlap computation in F-DET-3, identify all layers with >0% coverage that are not the primary layer. For each, determine `role` by the layer relationship:
- If the non-primary layer is the matn layer in a sharh unit → `role: "classification_frame"` (the matn text is the frame being commented on).
- If the non-primary layer is a higher layer (hashiyah quoting sharh) → `role: "quoted_opinion"`.
- Default → `role: "quoted_opinion"`.

**Convert to `ScholarAttribution` format:** Each structural detection produces `{mention_text: "[structural: {layer_type}]", resolved_name: layer_map[layer_id].author_name_arabic, role: <as above>, confidence: 1.0, source: "layer_overlap"}`. The `mention_text` uses a synthetic marker (not Arabic text) to distinguish structural detections from LLM-detected text mentions. The `confidence` is 1.0 because attribution is deterministic from layer data. The `resolved_name` comes from the manifest's `layer_map` entry for that layer.

**Deduplication with §7.2 LLM detections:** After §7.2 enrichment adds LLM-detected `resolved_scholars`, merge the two lists. If both F-DET-9 and §7.2 identify the same scholar (matching on `resolved_name`), keep the LLM entry (it has a real `mention_text` from the text and potentially a more specific `role`) and discard the structural entry. If F-DET-9 finds a layer author that §7.2 did not detect, the structural entry is preserved. This ensures every layer author with text in the unit appears in `quoted_scholars`, while avoiding duplicates.

This is structural quoted-scholar detection (from layer metadata). §7.2 adds LLM-detected quoted scholars from the text content (e.g., "قال أبو حنيفة" when Abu Hanifa is not a layer author).

### §7.2 — LLM-Driven Metadata Enrichment

For each chunk, a single LLM call enriches all teaching units with fields that require inference. The call receives the full assembled text, all unit boundaries with their deterministic metadata, and source-level context.

#### §7.2.1 — Input

The LLM receives:
- The full `assembled_text` of the `AssembledChunk`
- Source metadata: author name, work title, science/discipline, school affiliation (from the normalization engine's manifest)
- For each teaching unit: unit_index, word range, text_snippet, primary_function, self_containment level, self_containment_notes, and the deterministic `evidence_refs` (so the LLM can resolve partial references rather than re-detecting them)

#### §7.2.2 — LLM System Prompt

The enrichment prompt specifies each output field with instructions and constraints. Full prompt text:

```
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

You are enriching teaching units extracted from this Arabic text with semantic
metadata. Each teaching unit has already been identified, classified, and
partially annotated. Your task is to add inferred metadata that requires
scholarly understanding of the text.

For EACH teaching unit listed in the input, provide these fields:

1. TOPIC KEYWORDS (excerpt_topic): 1 to 3 Arabic keywords or short phrases
   identifying the specific topic taught in this unit. Use standard Arabic
   terminology from the science of this text.
   Examples: "شروط الوضوء", "حكم الربا", "إعراب المبتدأ والخبر"
   Choose keywords that distinguish this unit's topic from other units in the
   same chapter. Avoid overly broad terms (e.g., "فقه" alone is too broad).

2. SCHOOL ATTRIBUTION (school, school_confidence): If this unit presents a
   position from a specific madhhab or school, identify it. Values:
   - A school name: "حنفي", "مالكي", "شافعي", "حنبلي", "ظاهري"
   - "cross_school" if the unit compares multiple schools' positions
   - null if no school attribution is identifiable (grammar, tafsir, etc.)
   Also provide school_confidence (0.0 to 1.0) for your attribution. Set to
   null when school is null.
   CRITICAL DISTINCTION: The author's own school (provided in source metadata)
   is not necessarily the school of the position being presented. An author from
   the Hanbali school may present the Shafi'i position for comparison. Attribute
   the POSITION, not the AUTHOR, unless the author is presenting their own
   school's view.

3. QUOTED SCHOLAR RESOLUTION (resolved_scholars): For each scholar mentioned
   by name or epithet in the unit's text, provide:
   - mention_text: the exact Arabic text used to refer to the scholar
   - resolved_name: the scholar's full conventional name (الاسم المشهور)
     if you can identify them. Use standard scholarly naming (e.g.,
     "أحمد بن حنبل" not just "أحمد").
   - role: one of:
     * "quoted_opinion" — the unit quotes this scholar's view as content
     * "classification_frame" — the unit quotes this scholar's text as the
       frame being commented on (matn author in a sharh excerpt)
     * "refuted_position" — the unit quotes this scholar to refute their view
   - confidence: 0.0 to 1.0

   EPITHET RESOLUTION: Common epithets are context-dependent:
   - "الإمام" → in Hanbali texts usually Ahmad ibn Hanbal; in Shafi'i texts
     usually al-Shafi'i; in Hanafi texts usually Abu Hanifa; in Maliki texts
     usually Malik
   - "الشيخ" → varies by author and era; use source metadata for context
   - "صاحب الكتاب" / "المصنف" → the author of the current work
   Use the source school metadata provided to resolve ambiguous epithets.
   If resolution is uncertain, set confidence < 0.5 and provide your best guess.
   Never silently drop an unresolvable mention — include it with low confidence.

4. TAKHRIJ DATA (takhrij_data): For teaching units containing hadith citations,
   extract from the text AND from the footnotes provided:
   - hadith_text_snippet: first 30 characters of the hadith matn
   - collections: list of hadith collection names mentioned (e.g., "صحيح البخاري",
     "سنن أبي داود")
   - hadith_numbers: list of hadith numbers if mentioned (may be empty)
   - grade: the stated authenticity grade ("صحيح", "حسن", "ضعيف", etc.) or null
   - grade_source: who stated the grade ("المؤلف", "المحقق", "الألباني", etc.)
     or null
   Do NOT invent or infer grades. Record ONLY what the text or footnotes
   explicitly state. If no grade is mentioned, set grade and grade_source to null.
   Omit this field entirely for units with no hadith content.

5. TERMINOLOGY VARIANTS (terminology_variants): Arabic technical terms in this
   unit that are known to have alternative names in other scholarly traditions.
   - term: the term as used in this text
   - variants: list of known alternative Arabic terms for the same concept
   Example: {"term": "القراض", "variants": ["المضاربة"]}
   Example: {"term": "الحدث", "variants": ["النجاسة الحكمية"]}
   Only include genuine terminology equivalences. Empty list is acceptable
   for units with no notable term variants.

6. CROSS-REFERENCES (cross_references): If the unit contains references to
   other parts of the same work ("كما تقدم", "المذكور آنفاً", "ما سيأتي في باب"),
   provide:
   - reference_text: the exact reference phrase in the unit
   - target_description: what the reference points to, if determinable
   - resolved: true if you can identify the target from the division path
     and text context, false otherwise
   When the reference cannot be resolved (IR-3 from §6.4), set resolved to false.
   Unresolved references support self-containment assessment (the unit stays at
   PARTIAL) and downstream linking.

7. CONTEXT HINT (context_hint): For units with self_containment = PARTIAL,
   provide a brief Arabic phrase (10 to 30 Arabic words) that supplies the
   missing context identified in self_containment_notes. This hint will be
   displayed alongside the excerpt to help the reader.
   Provide ONLY for units where self_containment is PARTIAL.
   Set to null for FULL and DEPENDENT units.

Respond with a JSON array containing one enrichment object per teaching unit,
in the same order as the input units.
```

**Adaptation notes:**
- Adapted from: old excerpting SPEC §4.A.1 Phase 3 metadata enrichment, plus domain rules from §6.2–§6.4 of this SPEC.
- Added: explicit school-vs-position distinction (from §6.2 Layer Attribution design, where author school ≠ position school).
- Added: epithet resolution instructions with per-school defaults (from §6.4 IR-2).
- Added: hadith grade fabrication prohibition (from §6.3 EV-2 — "do NOT independently assess hadith authenticity").
- Added: cross-reference field (from §6.4 IR-1 intra-source cross-reference).
- Added: context_hint tied to self_containment level (from §3.3 PARTIAL definition).
- Added: terminology_variants (from old excerpting SPEC enrichment list).
- Removed: `proposed_leaf` — taxonomy placement is the taxonomy engine's responsibility (design decision documented above).
- Removed: `atom_ids`, `core_atom_ids`, `context_atom_ids` — the atom-based data model is eliminated in this architecture.

#### §7.2.3 — User Message

The user message contains the text, source metadata, and unit summaries with their deterministic annotations:

```
<source_metadata>
Author: {author_name}
Work: {work_title}
Science: {science}
School: {source_school}
</source_metadata>

<text>
{assembled_text}
</text>

<teaching_units>
{for each unit:}
Unit {unit_index}: words {start_word}–{end_word}
  snippet: "{text_snippet}"
  function: {primary_function}
  self_containment: {self_containment}
  self_containment_notes: {self_containment_notes | "none"}
  evidence_detected: {summary of F-DET-5 evidence_refs for this unit, or "none"}
  footnotes: {footnotes_relevant text, or "none"}
{end for}
</teaching_units>
```

The `evidence_detected` summary includes the pattern-matched evidence references from §7.1 (F-DET-5), so the LLM can refine and complete them (e.g., resolving a partial Quran quote to surah/ayah) rather than re-detecting from scratch.

The `footnotes` field includes the full text of relevant footnotes (F-DET-8), because the LLM needs footnote content for takhrij extraction (EV-2) and evidence grading.

#### §7.2.4 — Response Schema

The LLM returns structured output enforced via a Pydantic model. The schema:

**EnrichmentResult:**

| Field | Type | Description |
|-------|------|-------------|
| `enrichments` | `list[UnitEnrichment]` | One enrichment per teaching unit, same order as input. |
| `total_units` | `int` | Count of enrichments (must equal input unit count). |

**UnitEnrichment:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `unit_index` | `int` | yes | Must match the input `unit_index`. |
| `excerpt_topic` | `list[str]` | yes | 1–3 Arabic topic keywords. |
| `school` | `str \| null` | yes | School attribution or null. |
| `school_confidence` | `float \| null` | yes | Confidence for school attribution (0.0–1.0). Null when `school` is null. |
| `resolved_scholars` | `list[ResolvedScholar]` | yes | May be empty if no scholars mentioned. |
| `takhrij_data` | `list[TakhrijEntry]` | no | Present only for units with hadith content. |
| `terminology_variants` | `list[TermVariant]` | yes | May be empty. |
| `cross_references` | `list[CrossReference]` | yes | May be empty. |
| `context_hint` | `str \| null` | yes | Non-null only when self_containment is PARTIAL. |

**ResolvedScholar:**

| Field | Type | Description |
|-------|------|-------------|
| `mention_text` | `str` | Exact Arabic text referring to the scholar. |
| `resolved_name` | `str \| null` | Full conventional name, or null if unresolvable. |
| `role` | `str` | One of: `quoted_opinion`, `classification_frame`, `refuted_position`. |
| `confidence` | `float` | 0.0–1.0. |

**TakhrijEntry:**

| Field | Type | Description |
|-------|------|-------------|
| `hadith_text_snippet` | `str` | First 30 characters of the hadith matn. |
| `collections` | `list[str]` | Hadith collection names. |
| `hadith_numbers` | `list[str]` | Hadith numbers if mentioned (may be empty). |
| `grade` | `str \| null` | Stated grade or null. |
| `grade_source` | `str \| null` | Who stated the grade, or null. |

**TermVariant:**

| Field | Type | Description |
|-------|------|-------------|
| `term` | `str` | The term as used in this text. |
| `variants` | `list[str]` | Known alternative Arabic terms. |

**CrossReference:**

| Field | Type | Description |
|-------|------|-------------|
| `reference_text` | `str` | The exact reference phrase. |
| `target_description` | `str \| null` | What the reference points to. |
| `resolved` | `bool` | Whether the target was identified. |

On schema validation failure (missing fields, wrong types, invalid enum values), the structured output library retries automatically with the validation error appended. Up to 2 retries per chunk (same retry policy as Phase 2 — §5.5.2).

#### §7.2.5 — Model and Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `anthropic/claude-opus-4.6` via OpenRouter | Highest enrichment quality. School attribution and scholar resolution require deep domain knowledge. |
| Temperature | `0` | Deterministic enrichment. |
| MAX_TOKENS | `16384` | Enrichment output is structured metadata, not full text. 16384 is sufficient for the largest validated case (41 units, each with ~7 enrichment fields). |

**LLM enrichment failure handling:** If the enrichment call fails after retries (timeout, validation failure, API error), emit `EX-M-002` (enrichment failed). The excerpt is produced with deterministic metadata only (§7.1 fields) plus a review flag `llm_enrichment_failed: true`. Enrichment can be retried later without re-running Phases 1–2. The `ExcerptRecord` is structurally valid with only deterministic fields — the LLM-enriched fields have defaults (empty lists, null values) that downstream engines handle gracefully.

### §7.3 — Consensus Verification and Human Gates

Not every Phase 3 decision requires cross-provider verification. Consensus is reserved for high-epistemic-impact decisions where a wrong answer is silent and dangerous — the owner learns something false without any visible error signal.

#### §7.3.1 — What Requires Consensus

**Consensus required:**

| Decision | Trigger | Rationale |
|----------|---------|-----------|
| School attribution | `school` is non-null in §7.2 output | T-2 defense: wrong school attribution silently corrupts the owner's understanding of which tradition a position belongs to. |
| Author attribution (LA-3) | `EX-M-001` emitted in §7.1 (F-DET-3) | T-2 defense: ambiguous layer coverage means the deterministic rule cannot confidently attribute. A second model provides an independent assessment. |
| Self-containment (PARTIAL/DEPENDENT) | `self_containment` is not FULL | T-4 defense: a false FULL rating is caught by the Phase 2b evaluation. But PARTIAL/DEPENDENT ratings determine what context is shown to the owner — verifying these with a second model catches cases where Phase 2b was too conservative or too lenient. |

**Consensus NOT required:**

| Decision | Rationale |
|----------|-----------|
| Topic classification (`excerpt_topic`) | Validated by the taxonomy engine downstream — an independent structural check. |
| Evidence extraction (`evidence_refs`, `takhrij_data`) | Validated by structured reference matching (Quran verse lookup, hadith collection verification). Pattern-based, not subjective. |
| Author attribution (LA-1, LA-2, LA-4) | Deterministic — computed from character overlap with text layers, not inferred. |
| Self-containment FULL | Phase 2b's FULL assessment is accepted. FULL is the common case; verifying every FULL unit would be prohibitively expensive with minimal benefit. |
| Quoted scholar resolution | Low epistemic risk — a wrong scholar resolution is visible to the owner (the name appears in the text) and correctable. |
| Terminology variants | Informational — variants are suggestions, not authoritative claims. |

#### §7.3.2 — Verification Call

When a chunk contains units requiring consensus, Phase 3 issues a **single verification call per chunk** to a different model provider. The call includes only the units needing verification, not all units.

**Verification model:** Configurable. Default: `openai/gpt-5.4` via OpenRouter. The verification model MUST be from a different provider family than the enrichment model (Layer 3.5 of KNOWLEDGE_INTEGRITY.md). Since the enrichment model is Anthropic (Opus), the verifier must be from OpenAI, Cohere, Mistral, or another non-Anthropic provider.

**Verification prompt:**

```
You are verifying metadata decisions made by another model on Arabic Islamic
scholarly text. For each item below, independently assess whether the decision
is correct.

Source context:
- Author: {author_name}
- Work: {work_title}
- Science: {science}
- School: {source_school}

{for each item needing verification:}

ITEM {n}: {verification_type}
Text: "{unit primary_text, truncated to 500 chars}"
Decision: {the claim being verified}
Your assessment: agree or disagree, with brief reasoning in Arabic or English.
If you disagree, put ONLY the corrected value in alternative_value (bare string, no explanation).
Provide your confidence (0.0 to 1.0) in your own assessment.

{end for}
```

The verification types are:
- `SCHOOL_ATTRIBUTION`: "School attributed as {school}. Is this correct given the text content?"
- `AUTHOR_ATTRIBUTION`: "Unit attributed to {author} (layer {layer_id}, {coverage_pct}% coverage, rule LA-3). Is this attribution correct, or should it be attributed differently?"
- `SELF_CONTAINMENT`: "Unit assessed as {level}. Notes: {notes}. Is this assessment correct?"

**Verification response schema:**

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[VerificationItem]` | One per verification item. |

**VerificationItem:**

| Field | Type | Description |
|-------|------|-------------|
| `item_index` | `int` | Matches the item number from the prompt. |
| `agrees` | `bool` | Whether the verifier agrees with the decision. |
| `alternative_value` | `str \| null` | Bare corrected value if disagrees (author name, school, or self-containment level). No prose. |
| `confidence` | `float` | The verifier's confidence in its own assessment (0.0–1.0). Used for school_confidence computation in §7.3.3. |
| `reasoning` | `str` | Brief explanation. |

**Verification model parameters:**

| Parameter | Value |
|-----------|-------|
| Model | Configurable — default `openai/gpt-5.4` via OpenRouter |
| Temperature | `0` |
| MAX_TOKENS | `8192` |

#### §7.3.3 — Disagreement Resolution

When the enrichment model and verification model disagree:

**School attribution disagreement:**
1. Record both assessments: `{enrichment_school, verifier_school, verifier_reasoning}`.
2. If the verifier proposes a specific alternative school → use the **conservative** choice: set `school_confidence` to the lower of the enrichment model's `school_confidence` and the verifier's `confidence`, and add review flag `school_consensus_disagreement`.
3. Emit `EX-M-003` (school attribution disagreement).
4. The excerpt is produced with the enrichment model's `school` value but flagged for human review.

**Author attribution disagreement (LA-3 cases):**
1. Record both assessments.
2. Escalate: issue a **third verification call** using a second alternative provider (configurable, default `mistralai/mistral-large-2411` via OpenRouter). The third model sees the text and both prior assessments.
3. If 2 of 3 models agree → use the majority attribution.
4. If all 3 disagree → emit `EX-G-001` (attribution requires human review). Set `primary_author_layer` to the enrichment model's assessment with `attribution_confidence: 0.0`. The human gate triggers.

**Self-containment disagreement:**
1. Use the **more conservative** (lower) assessment. If the enrichment model said PARTIAL but the verifier says DEPENDENT, use DEPENDENT. If the verifier says FULL but Phase 2b said PARTIAL, keep PARTIAL.
2. Record the disagreement in the excerpt's metadata: `{phase2_assessment, verifier_assessment}`.
3. If downgraded to DEPENDENT → the human gate triggers (§7.3.4).

**Post-consensus context_hint repair (critical):** Because §7.2 (enrichment) runs BEFORE §7.3 (consensus), the `context_hint` produced by the LLM may be inconsistent with the consensus-resolved self-containment level. This repair step runs immediately after §7.3 consensus resolution, before V-P3-5 (self-containment consistency) validation.
- If consensus **downgrades** FULL → PARTIAL: the enrichment LLM did not produce a `context_hint` (it saw FULL). Repair: generate a `context_hint` from `self_containment_notes` — use the notes text directly as the hint. If `self_containment_notes` is also absent (Phase 2b said FULL), set `context_hint` to the verifier's reasoning text from the disagreement record. This ensures I-ER-4 is satisfied (PARTIAL → context_hint present).
- If consensus **downgrades** FULL → DEPENDENT or PARTIAL → DEPENDENT: set `context_hint` to null (DEPENDENT units do not receive context hints per §3.3). The human gate handles DEPENDENT units.
- If consensus **upgrades** PARTIAL → FULL: this case cannot occur. The conservative rule (§7.3.3) means consensus never upgrades — it only keeps or downgrades. This eliminates the PARTIAL→FULL case by design.
- If consensus **keeps** the same level: no repair needed — the enrichment LLM's context_hint (or lack thereof) is consistent.

Rationale for conservatism: underestimating self-containment (marking as PARTIAL when it's really FULL) costs the owner a context hint they don't need. Overestimating self-containment (marking as FULL when it's really PARTIAL) means the owner studies an excerpt without needed context and potentially misunderstands the teaching. The asymmetry of harm favors conservatism.

#### §7.3.4 — Human Gate Triggers

The following conditions trigger human gate entries. A gate entry is a record in the gate queue that requires the owner's review before the excerpt is considered fully validated.

| Gate Code | Trigger | What the Owner Sees |
|-----------|---------|---------------------|
| `EX-G-001` | Author attribution: 3 models all disagree (§7.3.3) | The excerpt text, the 3 proposed attributions with reasoning, and a prompt: "Which author wrote this passage?" |
| `EX-G-002` | Self-containment DEPENDENT after consensus (§7.3.3) | The excerpt text, the dependency notes, and a prompt: "This excerpt cannot stand alone. Should it be: (a) kept with a context note, (b) merged with adjacent content, or (c) excluded?" |
| `EX-G-003` | School attribution disagreement AND source_school conflicts with both models (§7.3.3) | The excerpt text, the proposed schools, and a prompt: "Which school does this position belong to?" |

**Gate queue format:** Each gate entry is a JSON line in `library/sources/{source_id}/excerpts/gate_queue.jsonl`:

```json
{
  "excerpt_id": "exc_12345_div_3_2_7",
  "gate_code": "EX-G-001",
  "timestamp": "2026-03-22T14:30:00Z",
  "context": {
    "primary_text_snippet": "...",
    "assessments": [...],
    "source_metadata": {...}
  },
  "status": "pending"
}
```

Gate entries with `status: "pending"` block the excerpt from appearing in the owner's study view but do NOT block downstream processing. The taxonomy engine can process gated excerpts (using the enrichment model's assessment as provisional) and update when the gate is resolved. This prevents the human gate queue from becoming a pipeline bottleneck.

**Gate entry does NOT trigger for:**
- LLM enrichment failure (`EX-M-002`) — this is an operational error, not an epistemic uncertainty. The excerpt is produced with deterministic metadata and can be re-enriched later.
- Low-confidence quoted scholar resolution — visible to the owner in the text and self-correcting.
- Unresolved cross-references — informational, not dangerous.

### §7.4 — Phase 3 Self-Validation

After Phase 3 completes for a chunk, the following checks are run before the `ExcerptRecord` objects are written.

**V-P3-1 (Excerpt ID uniqueness):** Every `excerpt_id` produced in this chunk is unique. No duplicate IDs within the chunk. Cross-chunk uniqueness is guaranteed by the ID format (includes div_id and unit_index).

**V-P3-2 (Primary text integrity):** For each excerpt, verify that the first 80 characters of `primary_text` match `text_snippet`. The comparison is whitespace-normalized: collapse runs of whitespace to a single space in both strings before comparing, because the LLM may normalize whitespace when copying the snippet. If they differ even after whitespace normalization, something went wrong in offset handling. Emit `EX-V-002`.

**V-P3-3 (Author attribution completeness):** Every excerpt has a `primary_author_layer` value. No excerpt has `null` attribution — even LA-3 (ambiguous) cases produce an attribution (with the ambiguity flagged). If any excerpt lacks attribution, emit `EX-M-004`.

**V-P3-4 (Topic keyword validity):** Every excerpt has 1–3 `excerpt_topic` keywords (from LLM enrichment) or an empty list (if LLM enrichment failed). Keywords with 0 or >3 entries when LLM enrichment succeeded → emit `EX-M-005` (topic extraction anomaly). The excerpt is still produced; the anomaly is logged.

**V-P3-5 (Self-containment consistency):** The `self_containment` level on the `ExcerptRecord` matches the consensus-resolved level from §7.3. If the `context_hint` field is non-null but `self_containment` is not PARTIAL, or if `self_containment` is PARTIAL but `context_hint` is null (and LLM enrichment succeeded), emit `EX-M-006` (self-containment metadata inconsistency).

**V-P3-6 (Evidence reference integrity):** For each `evidence_refs` entry with `type: "quran"` and a resolved surah/ayah, verify that the surah number is 1–114 and the ayah number is within the surah's ayah count (from the canonical reference). Invalid references → emit `EX-M-007` (invalid Quran reference). The reference is kept but flagged.

**V-P3-7 (Gate queue integrity):** Every gate trigger (EX-G-001, EX-G-002, EX-G-003) resulted in a gate queue entry being written. Read back the gate queue file and verify the entry exists. Missing entry → emit `EX-M-008` (gate entry not written — critical, because the uncertainty becomes invisible).

**V-P3-8 (Footnote relevance):** For each excerpt with `footnotes_relevant`, verify that every footnote's `ref_marker` offset falls within the excerpt's character range. Orphan footnotes (ref_marker outside the excerpt) → emit `EX-M-009` (footnote misattribution). The footnote is removed from this excerpt's `footnotes_relevant` (it belongs to a different excerpt).

**V-P3-9 (Content type consistency):** The `content_types` set (F-DET-4) must be a subset of the `ScholarlyFunction` enum values. Unknown function types → emit `EX-M-010` (unknown content type).

---

## §8 — Error Handling and Configuration

Every error is loud. No silent data loss. No silent defaults. When the engine cannot process an input correctly, it emits a structured error code, logs the context, and either recovers with a degraded output or skips the unit and flags it for reprocessing. The owner never encounters a silently wrong result — only a visibly flagged one.

### §8.1 — Error Code Catalog

All error codes follow the KR convention: `EX-{category}-{number}`.

**Categories:**
- `EX-A-*`: Phase 1 assembly errors
- `EX-C-*`: Phase 2 classification/grouping errors
- `EX-M-*`: Phase 3 metadata enrichment errors
- `EX-V-*`: Cross-phase validation errors
- `EX-G-*`: Human gate triggers (not errors — epistemic uncertainty requiring owner review)

Each code is defined exactly once in the section where its triggering condition is specified. This catalog lists every code with its definition location, severity, and recovery strategy. Codes are NOT redefined here — only cataloged.

**Phase 1 — Assembly (EX-A-*):**

| Code | Trigger | Severity | Recovery | Defined In |
|------|---------|----------|----------|------------|
| `EX-A-002` | Division's content unit range is empty | ERROR | Skip division | §4.2 |
| `EX-A-003` | Text layer rebasing produces non-contiguous coverage (gap between segments) | WARNING | Attempt repair: extend the preceding segment's `end` to cover gaps ≤5 characters (likely rounding errors). If gap >5 characters, escalate to Fatal via V-P1-5. Log gap size and location. | §4.6 |
| `EX-A-004` | Layer segment end exceeds content unit text length | WARNING | Clamp to text length | §4.6 |
| `EX-A-005` | Duplicate footnote `ref_marker` in assembled footnotes | WARNING | Deduplicate, keep first | §4.7 |
| `EX-A-006` | Heading text does not align with first content unit | WARNING | Process chunk anyway | §4.8 |
| `EX-A-010` | Empty `division_tree` — no divisions to process | ERROR | Skip source | §4.9 |
| `EX-A-011` | Content unit not found for declared unit index | ERROR | Skip division | §4.9 |
| `EX-A-012` | Offset normalization snippet matched only after diacritic stripping (§5.4.1 step d2) | WARNING | Use match position; log for quality monitoring | §5.4.1 |

**Phase 2 — Classification and Grouping (EX-C-*):**

| Code | Trigger | Severity | Recovery | Defined In |
|------|---------|----------|----------|------------|
| `EX-C-001` | Classification LLM call failed after all retries | ERROR | Skip chunk, flag for reprocessing | §5.1 |
| `EX-C-002` | Grouping LLM call failed after all retries | ERROR | Skip chunk, flag for reprocessing | §5.1 |
| `EX-C-003` | Offset normalization failed — cannot align LLM offsets to canonical tokenization | ERROR | Skip chunk, flag for reprocessing | §5.4.1 |
| `EX-C-004` | Segment coverage invariant violated after repair attempts | ERROR | Skip chunk, flag for reprocessing | §5.4.2 |
| `EX-C-005` | Unit coverage invariant violated after repair attempts | ERROR | Skip chunk, flag for reprocessing | §5.4.3 |

**Phase 3 — Metadata Enrichment (EX-M-*):**

| Code | Trigger | Severity | Recovery | Defined In |
|------|---------|----------|----------|------------|
| `EX-M-001` | Attribution ambiguous — LA-3 triggered (no layer ≥80%, ambiguous overlap) | WARNING | Escalate to consensus verification (§7.3) | §6.2 |
| `EX-M-002` | LLM enrichment call failed after all retries | WARNING | Produce excerpt with deterministic metadata only; set `llm_enrichment_failed` flag | §7.2.5 |
| `EX-M-003` | School attribution disagreement between enrichment and verification models | WARNING | Use enrichment model's value with low confidence; set `school_consensus_disagreement` flag | §7.3.3 |
| `EX-M-004` | Excerpt has null `primary_author_layer` after Phase 3 | ERROR | Should not occur — indicates a bug. Log full excerpt context. | §7.4 (V-P3-3) |
| `EX-M-005` | Topic keyword count outside 1–3 range when LLM enrichment succeeded | WARNING | Log; excerpt still produced | §7.4 (V-P3-4) |
| `EX-M-006` | Self-containment metadata inconsistency (level vs. context_hint mismatch) | WARNING | Log; do not auto-correct — the mismatch signals a bug | §7.4 (V-P3-5) |
| `EX-M-007` | Invalid Quran reference (surah or ayah out of range) | WARNING | Keep reference but flag as invalid | §7.4 (V-P3-6) |
| `EX-M-008` | Gate entry not written despite gate trigger | CRITICAL | Retry write. If retry fails, halt source processing — the uncertainty is now invisible. | §7.4 (V-P3-7) |
| `EX-M-009` | Footnote `ref_marker` offset outside excerpt's character range | WARNING | Remove footnote from this excerpt's `footnotes_relevant` | §7.4 (V-P3-8) |
| `EX-M-010` | Unknown content type in `content_types` set | WARNING | Log; likely indicates a new scholarly function type not in the enum | §7.4 (V-P3-9) |

**Validation (EX-V-*):**

| Code | Trigger | Severity | Recovery | Defined In |
|------|---------|----------|----------|------------|
| `EX-V-001` | Phase 1 self-validation check failed | Varies per check | Per check (§4.9) | §4.9 |
| `EX-V-002` | Primary text integrity check failed — extracted text doesn't match snippet | ERROR | Do not produce excerpt. Log full context for debugging. | §7.4 (V-P3-2) |

**Human Gate Triggers (EX-G-*):**

| Code | Trigger | Severity | Recovery | Defined In |
|------|---------|----------|----------|------------|
| `EX-G-001` | Author attribution: 3 models all disagree | GATE | Write to gate queue; excerpt produced with provisional attribution | §7.3.3 |
| `EX-G-002` | Self-containment DEPENDENT after consensus verification | GATE | Write to gate queue; owner decides: keep with note, merge, or exclude | §7.3.4 |
| `EX-G-003` | School attribution disagreement AND source school conflicts with both models | GATE | Write to gate queue; owner decides school | §7.3.4 |

**Severity definitions:**
- **CRITICAL**: Processing must halt for this source. Continuing would produce invisible errors.
- **ERROR**: The affected unit (division, chunk, or excerpt) cannot be produced. Skip and flag.
- **WARNING**: The affected unit is produced with degraded quality. Logged and flagged.
- **GATE**: Not an error. An epistemic uncertainty requiring human judgment.

### §8.2 — Recovery Strategies

Recovery follows a consistent pattern: retry → degrade → skip → flag.

**LLM call failures (EX-C-001, EX-C-002, EX-M-002):**
1. Retry up to `RETRY_COUNT` times (default 2) with exponential backoff (1s, 4s).
2. On schema validation failure, the structured output library (Instructor) automatically retries with the validation error appended to the prompt.
3. If all retries exhausted:
   - Phase 2 failures (EX-C-001, EX-C-002): skip the entire chunk. No teaching units are produced for this chunk. The chunk is flagged for reprocessing in the processing log.
   - Phase 3 enrichment failure (EX-M-002): produce the excerpt with deterministic metadata only (§7.1). LLM-enriched fields default to empty/null. The excerpt is structurally valid but informationally incomplete.

**Offset normalization failures (EX-C-003):**
1. The normalization algorithm (§5.4.1) attempts snippet-based alignment as fallback.
2. If alignment fails, skip the chunk. Flag for reprocessing with diagnostic data (the LLM's raw offsets and the canonical tokenization).

**Coverage violations (EX-C-004, EX-C-005):**
1. On coverage invariant violation (§5.4.2 or §5.4.3), first attempt **repair**: merge uncovered word ranges into the nearest adjacent segment or unit. Re-validate after repair.
2. If repair restores coverage → proceed with repaired data and log the repair. No retry needed.
3. If repair fails (violation persists) → reject the LLM result and **retry** the LLM call per §5.5.2 (up to RETRY_COUNT retries). The retry includes an error feedback message describing which invariant was violated.
4. If all retries are exhausted and coverage is still violated → skip the chunk. Flag with EX-C-004 (segments) or EX-C-005 (units) for reprocessing.

**Phase 1 assembly failures (EX-A-002, EX-A-010, EX-A-011):**
1. Skip the affected division (or source for EX-A-010).
2. Continue with remaining divisions. Phase 1 failures are per-division independent — one bad division does not affect others.

**Gate trigger failures (EX-M-008):**
1. Retry the gate queue file write once.
2. If retry fails → halt processing for this source. Rationale: a missing gate entry means an uncertainty becomes invisible, violating the core guarantee that every low-confidence decision creates a checkpoint. This is the only non-LLM error that halts source processing.

**Reprocessing:** Chunks flagged for reprocessing are recorded in the processing log with their error codes and diagnostic context. Reprocessing is triggered manually or by a scheduled retry job. Reprocessed chunks go through the full pipeline from Phase 1 — there is no partial re-entry (this is simpler and defends against stale intermediate state).

### §8.3 — Configuration

All configuration parameters are collected here with their defaults, valid ranges, and the SPEC section that defines their behavioral impact.

**Phase 1 parameters:**

| Parameter | Type | Default | Range | Description | SPEC Reference |
|-----------|------|---------|-------|-------------|----------------|
| `TINY_DIVISION_WORDS` | int | 50 | 10–200 | Minimum word count for a standalone division. Below this → merge with sibling. | §4.4 |
| `OVERSIZED_DIVISION_WORDS` | int | 5000 | 2000–10000 | Maximum word count for a single chunk. Above this → split into multiple chunks. | §4.5 |

**Phase 2 parameters:**

| Parameter | Type | Default | Range | Description | SPEC Reference |
|-----------|------|---------|-------|-------------|----------------|
| `CLASSIFY_MODEL` | str | `anthropic/claude-opus-4.6` | — | LLM model for segment classification. Via OpenRouter. | §5.2.5 |
| `GROUP_MODEL` | str | `anthropic/claude-opus-4.6` | — | LLM model for teaching unit grouping. Via OpenRouter. | §5.3.5 |
| `LLM_TEMPERATURE` | float | 0 | 0.0–0.3 | Temperature for all LLM calls (classification, grouping, enrichment). | §5.2.5, §5.3.5, §7.2.5 |
| `CLASSIFY_MAX_TOKENS` | dynamic | See §5.5.1 | — | MAX_TOKENS for classify call. Scales with input word count. | §5.5.1 |
| `GROUP_MAX_TOKENS` | int | 16384 | 8192–32768 | MAX_TOKENS for group call. | §5.3.5 |
| `RETRY_COUNT` | int | 2 | 1–5 | Maximum retries for LLM calls (excluding schema validation retries). | §5.5.2 |
| `TIMEOUT_SECONDS` | int | 300 | 30–600 | Per-call timeout for LLM API requests. | §5.5.3 |

**Phase 3 parameters:**

| Parameter | Type | Default | Range | Description | SPEC Reference |
|-----------|------|---------|-------|-------------|----------------|
| `ENRICH_MODEL` | str | `anthropic/claude-opus-4.6` | — | LLM model for metadata enrichment. Via OpenRouter. | §7.2.5 |
| `ENRICH_MAX_TOKENS` | int | dynamic | 16384–32768 | ≤1500 words → 16384, >1500 words → 32768. Mirrors §5.5.1 classify scaling. Empirically calibrated from ibn_aqil_v3 (1987 words, 28 TUs, 14863 completion tokens). | §7.2.5 |
| `VERIFY_MODEL` | str | `openai/gpt-5.4` | — | LLM model for consensus verification. Via OpenRouter. Must be from a different provider family than ENRICH_MODEL. | §7.3.2 |
| `VERIFY_MAX_TOKENS` | int | 8192 | 4096–16384 | MAX_TOKENS for verification call. | §7.3.2 |
| `ESCALATION_MODEL` | str | `mistralai/mistral-large-2411` | — | Third model for 3-way escalation when enrichment and verification disagree on attribution. Via OpenRouter. | §7.3.3 |

**Human gate parameters:**

| Parameter | Type | Default | Description | SPEC Reference |
|-----------|------|---------|-------------|----------------|
| `GATE_ON_DEPENDENT` | bool | true | Trigger human gate for DEPENDENT self-containment after consensus. | §7.3.4 (EX-G-002) |
| `GATE_ON_ATTRIBUTION_DISAGREEMENT` | bool | true | Trigger human gate when all 3 attribution models disagree. | §7.3.4 (EX-G-001) |
| `GATE_ON_SCHOOL_CONFLICT` | bool | true | Trigger human gate when school attribution conflicts with source metadata and models disagree. | §7.3.4 (EX-G-003) |

**Telemetry parameters:**

| Parameter | Type | Default | Description | SPEC Reference |
|-----------|------|---------|-------------|----------------|
| `LOG_LEVEL` | str | `INFO` | Minimum log level: DEBUG, INFO, WARNING, ERROR. | §5.5.4 |
| `TELEMETRY_ENABLED` | bool | true | Collect per-chunk timing, token usage, error counts. | §5.5.4 |

**Configuration loading order:**
1. Built-in defaults (the values in the tables above).
2. Engine configuration file: `engines/excerpting/config.yaml` (overrides defaults).
3. Per-source overrides: `library/sources/{source_id}/excerpting_config.yaml` (overrides engine config for this source — useful for sources requiring different thresholds).

Per-source overrides are designed for edge cases. For example, a very short source (under 10 divisions) might lower `TINY_DIVISION_WORDS` to avoid over-merging. A source with known poor layer detection might lower the LA-1 threshold from 80% to 70%. Per-source overrides are logged in the processing log.

**All LLM calls go through OpenRouter.** Model strings in this configuration are OpenRouter model identifiers. Direct API calls to Anthropic, OpenAI, Cohere, or Mistral are not permitted (KR routing rule).

---

## §9 — Deferred Capabilities

This section catalogs capabilities that are **not part of the core excerpting engine** but are designed to plug into its architecture. Each capability is listed with: what it does, which processing phase it extends, and what ExcerptRecord fields or processing steps it would add. The core engine preserves extension hooks for each — nullable fields, empty arrays, or config flags — so these capabilities can be added without schema migration.

**Principle:** Every deferred capability was specified in the old 7-engine SPECs (passaging §4.B, atomization §4.B, excerpting §4.B). The 5-engine architecture absorbed passaging and atomization into excerpting as internal phases, but it did NOT absorb their transformative capabilities. These remain deferred until the core engine is proven and the pipeline is flowing.

**Extension hook contract:** A deferred capability may add nullable fields to `ExcerptRecord` (§2.2), add optional processing steps within an existing phase, or add new configuration parameters (§8.3). It must NOT change the type or semantics of any existing core field. It must NOT change the ordering or skip conditions of existing processing steps. It must NOT require a different LLM model for core operations. Violations of these rules require a SPEC revision, not just a capability activation.

### §9.1 — Deferred Capabilities Catalog

| ID | Capability | Source | Phase | Extension Hook | Depends On |
|----|-----------|--------|-------|----------------|------------|
| DC-01 | Argumentative discourse mapping | excerpting §4.B.1 | Phase 3 | `argument_role: str \| null`, `argument_map: list \| null` on ExcerptRecord | Core: `content_types`, `primary_function` |
| DC-02 | Cross-source semantic deduplication | excerpting §4.B.2 | Post-Phase 3 (batch) | `semantic_duplicates: list \| null` on ExcerptRecord | DC-08 (fingerprints), taxonomy placement |
| DC-03 | Scholarly argument completeness | excerpting §4.B.3 | Post-Phase 3 | `argument_completeness: object \| null` on ExcerptRecord | DC-01 (argument roles) |
| DC-04 | Mas'ala boundary detection | excerpting §4.B.4 | Phase 3 | `masala_analysis: object \| null` on ExcerptRecord | Core: `excerpt_topic`, source science |
| DC-05 | Evidence chain reconstruction | excerpting §4.B.5 | Phase 3 | `evidence_chain: object \| null` on ExcerptRecord | Core: `evidence_refs`, `content_types` |
| DC-06 | Cross-excerpt dialogue detection | excerpting §4.B.6 | Post-Phase 3 (incremental) | `dialogue_links: list \| null` on ExcerptRecord | DC-01, DC-05, taxonomy placement |
| DC-07 | Self-containment repair suggestions | excerpting §4.B.7 | Post-Phase 3 | `repair_suggestions: list \| null` on ExcerptRecord | Core: `self_containment`, adjacent chunk context |
| DC-08 | Cross-source textual resonance | excerpting §4.B.8 | Post-Phase 3 (incremental) | `resonance_links: list \| null` on ExcerptRecord | DC-05, DC-08 (fingerprints), taxonomy placement |
| DC-09 | Rhetorical structure analysis | atomization §4.B.1 | Phase 2b (post-grouping) → Phase 3 (passthrough) | `rhetorical_pattern: str \| null` on ExcerptRecord (computed after grouping, carried through Phase 3) | Core: `scholarly_function` sequence |
| DC-10 | Scholarly attribution chain resolution | atomization §4.B.4 | Phase 3 | `attribution_chain: list \| null` on ExcerptRecord | Core: `quoted_scholars`, `primary_author_layer` |
| DC-11 | Semantic fingerprinting | atomization §4.B.5 | Post-Phase 2 | `fingerprint: object \| null` on ExcerptRecord | Core: `primary_text` |
| DC-12 | Passage quality prediction | passaging §4.B.1 | Post-Phase 1 | `quality_prediction: object \| null` on AssembledChunk | Core: `assembled_text`, embeddings |
| DC-13 | Implicit structure discovery | passaging §4.B.2 | Phase 1 (pre-splitting) | Supplementary division tree for sources with `structure_confidence: "minimal"` | Normalization: `structure_confidence` |
| DC-14 | Discourse-aware boundary optimization | passaging §4.B.7 | Phase 1 (splitting) | `discourse_transition_cost: float \| null` on split boundaries | Core: `assembled_text`, embeddings |
| DC-15 | Completeness forecast | passaging §4.B.8 | Post-Phase 1 | `completeness_forecast: object \| null` on AssembledChunk | Normalization: `discourse_flow` (if available) |
| DC-16 | Verse-commentary explicit alignment | evaluation finding C-5 | Phase 1 | `verse_alignment: list \| null` on AssembledChunk for verse-commentary sources | Core: `text_layers`, VC domain rules (§6.5) |

### §9.2 — Extension Hook Descriptions

**DC-01 through DC-08 (old excerpting §4.B):** These capabilities extend Phase 3 metadata enrichment or run as post-Phase 3 batch operations. Their full specifications are preserved in `reference/archive/abd_code/excerpting/SPEC_old_original.md` §4.B.1–§4.B.8. The core engine's `ExcerptRecord` fields (`content_types`, `evidence_refs`, `quoted_scholars`, `excerpt_topic`, `self_containment`, `primary_author_layer`) provide the foundation each capability builds upon.

Post-Phase 3 capabilities (DC-02, DC-03, DC-06, DC-07, DC-08) run AFTER Phase 3 produces complete `ExcerptRecord` objects. They add fields to already-valid records. If a post-Phase 3 capability fails, the core ExcerptRecord remains valid — the deferred field stays null.

Cross-source capabilities (DC-02, DC-06, DC-08) require taxonomy placement to determine which excerpts share a leaf. These are inherently incremental — they run when a new source is added to an existing library, comparing new excerpts against previously placed excerpts. During initial bulk loading, they run as a batch job after all sources are excerpted and placed.

**DC-09 (rhetorical structure):** Extends Phase 2b by adding a post-grouping pattern matching step. After teaching units are grouped, a pattern matcher examines the sequence of `scholarly_function` values across a chunk's units and annotates recognized rhetorical patterns. The field `rhetorical_pattern` on `ExcerptRecord` records the matched pattern name (e.g., `"masala_tarjih"`, `"definition_example"`) or null. The value is computed after Phase 2b grouping and carried through Phase 3 deterministic assembly. This is purely informational — it does not change unit boundaries.

**DC-10 (attribution chain):** Extends Phase 3 LLM enrichment to resolve multi-layer scholarly attribution chains. Where the core engine identifies `primary_author_layer` and `quoted_scholars`, this capability reconstructs the full chain: who quotes whom, in what capacity, across how many layers of commentary. The `attribution_chain` field is a list of `{scholar_id, role, layer, quotes}` objects tracing the scholarly lineage of each teaching unit's content.

**DC-11 (semantic fingerprinting):** Adds a post-Phase 2 step that computes a semantic fingerprint for each teaching unit's `primary_text`. The fingerprint includes: a text hash (for exact duplicate detection), key terms (for terminological matching), and an embedding vector (for semantic similarity). This fingerprint is the foundation for DC-02 (deduplication) and DC-08 (resonance detection).

**DC-12 through DC-16 (old passaging/atomization §4.B):** These capabilities extend Phase 1 (deterministic preprocessing) or run as post-Phase 1 analysis. Their full specifications are preserved in `engines/passaging/SPEC.md` §4.B and `engines/atomization/SPEC.md` §4.B. The core engine's Phase 1 output (`AssembledChunk` with `assembled_text`, `text_layers`, `word_count`) provides the foundation.

DC-13 (implicit structure discovery) is the most architecturally significant: it provides an alternative division tree for sources where the normalization engine reported `structure_confidence: "minimal"`. This supplementary tree guides Phase 1 splitting without modifying the normalization engine's output. It would be activated by a configuration flag (`ENABLE_IMPLICIT_STRUCTURE: bool, default false`).

### §9.3 — Activation Model

Deferred capabilities are activated per-engine-run via configuration flags in `engines/excerpting/config.yaml`. Each capability has a boolean flag (`ENABLE_DC_01: bool`, etc.) defaulting to `false`. When a capability is activated:

1. Its nullable fields are populated on applicable records (instead of remaining null).
2. Its processing steps execute within the designated phase.
3. Its error codes (defined in the capability's full specification) are added to the error catalog.
4. Its configuration parameters (model strings, thresholds) are added to §8.3.

Capabilities with dependencies (the `Depends On` column in §9.1) cannot be activated unless their dependencies are also active. The engine validates capability dependencies at startup and emits a configuration error if an unsatisfied dependency is detected.

### §9.4 — What Is NOT Deferred

The following capabilities from the old SPECs are **absorbed into the core engine** (not deferred):

| Old Capability | Absorbed Into | Rationale |
|---------------|---------------|-----------|
| Atomization §4.A (classification) | Phase 2a (§5.2) | Core: segment classification is the engine's primary function |
| Atomization §4.B.2 (implicit layer transition) | §6.2 (LA rules) | Partially absorbed: LA-2 and LA-3 handle explicit and ambiguous layer transitions; implicit detection remains deferred (DC-09 pattern matching covers the remaining cases) |
| Atomization §4.B.6 (argument completeness) | Subsumed by DC-03 | Old atomization version operated at atom level; DC-03 operates at excerpt level (more useful) |
| Passaging §4.A (all core steps) | Phase 1 (§4) | Core: cross-page assembly, merging, splitting are the preprocessor |
| Passaging §4.B.3 (commentary alignment) | DC-16 + §6.5 (VC rules) | VC rules handle core verse-commentary detection; precision alignment is deferred |
| Passaging §4.B.5 (adaptive passaging) | Not needed | Content census adaptation was for a separate passaging engine; Phase 1 operates within the excerpting engine's context and uses simpler thresholds |
| Passaging §4.B.6 (argument boundary detection) | Phase 2b (§5.3) | Core: teaching unit grouping inherently detects argument boundaries through self-containment evaluation |
| Atomization §4.B.3 (distribution analytics) | Not deferred — dropped | Analytics capability, not a processing capability; can be implemented as a post-hoc analysis script outside the engine |
| Atomization §4.B.7 (terminological concordance) | Not deferred — dropped | Cross-source concordance is better handled at the taxonomy/synthesis layer |
| Atomization §4.B.8 (evidence quality signals) | §6.3 (EV rules) | EV-1 through EV-3 handle evidence detection and reference extraction; quality signal detection is covered |

---

## §10 — Test Requirements

This section specifies **what must be tested**, not how. The builder (Claude Code) writes the actual test code; this section defines the coverage targets, fixture requirements, and adversarial cases that the test suite must satisfy.

**Coverage rule:** Every verification check (34 total: V-P1-1–6, V-P2-1–19, V-P3-1–9), every invariant (29 total: I-AC-1–7, I-CS-1–6, I-TU-1–9, I-ER-1–7), every error code (28 total: EX-A/C/M/V/G), and every domain rule (22 total: DP-1–6, LA-1–4, EV-1–3, IR-1–3, VC-1–3, QM-1–3) requires at least one test that exercises it. A test that only checks the happy path does not count — each test must verify the specific behavior described by the ID it claims to cover.

### §10.1 — Test Fixtures

**Existing fixtures (from experiments — regression baselines):**

The architecture experiments produced validated outputs for real Shamela divisions. These become regression baselines: future engine runs on the same inputs must produce equivalent or better outputs (measured by teaching unit boundary quality and self-containment accuracy). Fixture locations:

- `experiments/format_diversity_test/fixtures/ibn_aqil/` — verse-commentary (نظم) format, multi-layer (matn/sharh/hashiyah)
- `experiments/format_diversity_test/fixtures/taysir_al_ilam/` — prose format, single-layer
- `experiments/architecture_test/` — 10 divisions from 5 genres (nahw, fiqh, usul, balagha, hadith)

**Required new fixtures (builder must create):**

The following fixture types are needed for unit testing and are NOT covered by experiment fixtures:

| Fixture Type | Purpose | Minimum Count |
|-------------|---------|---------------|
| Tiny division (<50 words) | Test merging logic (§4.4) | 3 (single, consecutive pair, triple) |
| Oversized division (>5000 words) | Test splitting logic (§4.5) | 2 (with structural markers, without) |
| Multi-page division | Test cross-page assembly (§4.3) | 2 (2-page, 5-page) |
| Empty division (0 content units) | Test skip logic (§4.2) | 1 |
| Single-sentence division (<10 words) | Test minimal-content handling | 1 |
| Multi-layer source (matn/sharh) | Test LA-1 through LA-4, text layer rebasing (§4.6) | 2 (clean layers, ambiguous layers) |
| Source with footnotes | Test footnote aggregation (§4.7) | 1 (with ref_markers spanning multiple units) |
| Hadith-heavy text | Test EV-1 through EV-3 | 1 |
| Verse-commentary (نظم) | Test VC-1 through VC-3 | 1 (from existing ibn_aqil fixtures) |
| Q&A / masala format | Test QM-1 through QM-3 | 1 |
| Source with reported positions | Test DP-1, DP-2 (decontextualization prevention) | 2 |

All fixtures must use real Arabic text from Shamela exports. Synthetic Arabic text is not acceptable for domain rule testing — the markers and patterns must be authentic.

**Fixture construction pattern:** Follow normalization engine conventions (`engines/normalization/tests/conftest.py`). Use factory helpers: `_make_source_metadata(**overrides)` for SourceMetadata, `_make_normalized_package(**overrides)` for NormalizedPackage. Each fixture includes the NormalizedPackage input and (where applicable) the expected output for regression comparison.

### §10.2 — Phase 1 Unit Tests

Phase 1 is fully deterministic — every behavior is testable without LLM calls.

**Verification check coverage:**

| Check | What the test must verify |
|-------|--------------------------|
| V-P1-1 (Division coverage) | Every leaf division produces ≥1 chunk or is explicitly skipped. Test: create a division tree with 5 leaves; verify 5 chunks (or documented skips). |
| V-P1-2 (Content unit coverage) | All content units appear in some chunk. Test: 10 content units across 3 divisions; verify union of `constituent_unit_indices` covers 0–9. |
| V-P1-3 (No empty chunks) | Every chunk has `word_count > 0`. Test: merge two tiny divisions (one with 10 words, one with 5); verify merged chunk has word_count=15. |
| V-P1-4 (No oversized chunks) | Every chunk has `word_count <= OVERSIZED_DIVISION_WORDS`. Test: input a 7000-word division; verify it splits into chunks ≤5000 words each. |
| V-P1-5 (Layer coverage) | Every character in `assembled_text` is covered by exactly one `text_layers` segment. Test: multi-page division with 3 layers; verify continuous coverage after assembly. |
| V-P1-6 (Word count consistency) | `word_count` matches actual Arabic word count. Test: known text with 47 Arabic words; verify `word_count == 47`. |

**Invariant coverage:**

I-AC-1 through I-AC-7 define `AssembledChunk` structural constraints. Each invariant must have a dedicated test that constructs an AssembledChunk violating exactly that invariant and verifies the validation code detects it.

**Error code coverage (Phase 1):**

| Error Code | Trigger Condition for Test |
|-----------|---------------------------|
| EX-A-002 | Division's content unit range is empty (start_unit_index > end_unit_index or no content units in range) |
| EX-A-003 | Text layer rebasing produces non-contiguous coverage (gap between layer segments after assembly) |
| EX-A-004 | Layer segment end exceeds content unit primary_text length (requires clamping) |
| EX-A-005 | Assembled footnotes contain duplicate ref_marker values across constituent content units |
| EX-A-006 | Heading text from division tree does not align with first content unit text (heading mismatch) |
| EX-A-010 | Empty division_tree — source has 0 leaf divisions to process |
| EX-A-011 | Content unit not found for a unit_index in the declared range (missing content unit) |
| EX-A-012 | Offset normalization snippet matched only after diacritic stripping (§5.4.1 step d2) |

Each error code test must verify: (a) the error is emitted with the correct code, (b) the error message contains actionable context, and (c) the appropriate recovery strategy from §8.2 is followed.

### §10.3 — Phase 2 Integration Tests

Phase 2 requires LLM calls. Tests at this level use either (a) recorded LLM responses (golden fixtures) or (b) mock LLM responses with known outputs for deterministic testing.

**Verification check coverage:**

Phase 2a (classification, V-P2-1 through V-P2-9) and Phase 2b (grouping, V-P2-10 through V-P2-19) checks are tested together because grouping depends on classification output.

For each V-P2 check, the test must:
1. Construct an `AssembledChunk` with known text.
2. Provide a mock or recorded LLM response that produces known `ClassifiedSegment[]` and `TeachingUnit[]`.
3. Verify the specific V-P2 check passes on valid input.
4. Verify the specific V-P2 check detects a violation on deliberately invalid input.

**Key integration tests (using experiment regression baselines):**

| Test | Input | Expected Behavior |
|------|-------|-------------------|
| Prose classification | Architecture experiment prose division (~500 words) | Segments with valid scholarly functions, full coverage (V-P2-5) |
| Verse-commentary classification | Ibn Aqil fixture division | VC-1 through VC-3 rules applied; verse segments classified with appropriate scholarly functions from §2.3.1 (typically `rule_statement` for Alfiyya verses encoding grammar rules, or `definition`); verse + commentary grouped as single teaching unit per VC-1 |
| Multi-topic grouping | Division with 2 distinct topics | ≥2 teaching units; no unit spans both topics |
| Self-containment evaluation | Division with a dependent excerpt (references prior context) | At least one unit with `self_containment: DEPENDENT` |
| Offset normalization | LLM response with approximate word boundaries | §5.4 normalization produces exact token-aligned boundaries |

**Error code coverage (Phase 2):**

| Error Code | Trigger Condition for Test |
|-----------|---------------------------|
| EX-C-001 | Classification LLM call fails after all retries (timeout, schema validation failure, API error) |
| EX-C-002 | Grouping LLM call fails after all retries |
| EX-C-003 | Offset normalization fails — cannot align LLM word boundaries to actual token boundaries |
| EX-C-004 | Segment coverage invariant violated after offset repair (gap in coverage persists) |
| EX-C-005 | Unit coverage invariant violated after repair (unassigned segments persist) |

**Invariant coverage:** I-CS-1 through I-CS-6 and I-TU-1 through I-TU-9 must each have a test that verifies violation detection. The test constructs a mock LLM response that produces output violating exactly one invariant and verifies the validation code catches it.

### §10.4 — Phase 3 and Output Tests

**Verification check coverage:**

| Check | What the test must verify |
|-------|--------------------------|
| V-P3-1 (Excerpt ID uniqueness) | Two units in the same chunk produce different `excerpt_id` values. |
| V-P3-2 (Primary text integrity) | `primary_text` first 80 characters match `text_snippet` after whitespace normalization (collapse runs of whitespace to single space in both). Test with known text containing `\n\n` paragraph breaks and known offsets; verify the comparison passes despite whitespace differences. Also test a genuine mismatch (wrong offsets) → EX-V-002. |
| V-P3-3 (Author attribution completeness) | Every excerpt has a non-null `primary_author_layer`. Test: construct a chunk from a multi-layer source; verify all excerpts are attributed. |
| V-P3-4 (Topic keyword validity) | Excerpts have 1–3 topic keywords after successful LLM enrichment. Test with mock LLM returning 0 keywords → EX-M-005 emitted. |
| V-P3-5 (Self-containment consistency) | PARTIAL excerpt has non-null `context_hint`; FULL excerpt has null `context_hint`. Test both valid and invalid combinations. |
| V-P3-6 (Evidence reference integrity) | Quran references have valid surah (1–114) and ayah numbers. Test with surah 115 → EX-M-007. |
| V-P3-7 (Gate queue integrity) | Every gate trigger writes a gate queue entry. Test: trigger EX-G-001; verify gate file contains the entry. |
| V-P3-8 (Footnote relevance) | Footnote `ref_marker` offsets fall within the excerpt's character range. Test with orphan footnote → EX-M-009. |
| V-P3-9 (Content type consistency) | `content_types` set contains only valid `ScholarlyFunction` values. Test with an unknown type → EX-M-010. |

**Error code coverage (Phase 3):**

| Error Code | Trigger Condition for Test |
|-----------|---------------------------|
| EX-M-001 | Attribution ambiguous — LA-3 triggered (no layer has ≥80% coverage, or 3+ layers present with <60% dominant) |
| EX-M-002 | LLM enrichment call fails after all retries (timeout, validation failure, API error) |
| EX-M-003 | School attribution disagreement between enrichment model and verification model |
| EX-M-004 | Excerpt has null `primary_author_layer` after full Phase 3 |
| EX-M-005 | Topic keyword count outside 1–3 range |
| EX-M-006 | Self-containment level vs. `context_hint` mismatch |
| EX-M-007 | Invalid Quran reference |
| EX-M-008 | Gate entry write fails — **critical**: verify retry and halt behavior |
| EX-M-009 | Footnote ref_marker offset falls outside excerpt's character range (orphan footnote) |
| EX-M-010 | Unknown content type |
| EX-V-001 | Phase 1 self-validation check failed (any V-P1 fatal check) |
| EX-V-002 | Primary text integrity check fails |
| EX-G-001 | Attribution disagreement (3 models disagree) → gate queue entry |
| EX-G-002 | DEPENDENT self-containment after consensus → gate queue entry |
| EX-G-003 | School conflict unresolved → gate queue entry |

**Output invariant coverage:** I-ER-1 through I-ER-7 must each have a dedicated test.

### §10.5 — Domain Rule Tests

Each domain rule (§6) requires a test with authentic Arabic text demonstrating the rule's activation. These tests verify that the LLM prompt + post-processing correctly applies the domain rule.

**Decontextualization prevention (DP-1 through DP-6):**

- DP-1 (Reported position inclusion): Input text with وقال الشافعي + author response. Verify excerpt contains both.
- DP-2 (Refutation context): Input text with ورد عليه بأن. Verify the refuted position is included.
- DP-3 (Conditional endorsement): Input text with وهذا القول حسن لولا... Verify both the praise and qualification are in one unit.
- DP-4 (Evidence-ruling binding): Hadith + its ruling. Verify they are in the same unit.
- DP-5 (Definition-example binding): Definition + immediately following example. Verify they are grouped.
- DP-6 (Prerequisite inclusion): Term used without definition, but definition is in a prior segment. Verify context is preserved.

**Multi-layer handling (LA-1 through LA-4):**

- LA-1 (Layer attribution): Multi-layer text with 80%+ from one layer → `primary_author_layer` is that layer.
- LA-2 (Layer transition markers): Text containing قال المصنف. Verify layer boundary is detected.
- LA-3 (Ambiguous layers): Text where no layer reaches 80%. Verify consensus verification is triggered.
- LA-4 (Editor footnotes): Substantive editor footnote. Verify it is treated as scholarly commentary, not silently merged.

**Evidence handling (EV-1 through EV-3), implicit references (IR-1 through IR-3), verse-commentary (VC-1 through VC-3), Q&A format (QM-1 through QM-3):** Each rule requires at least one test with authentic Arabic text exercising the specific behavior the rule describes.

### §10.6 — Adversarial Test Cases

Adversarial cases verify that specific knowledge corruption paths are blocked. Each case describes a scenario where corruption WOULD occur without the prevention mechanism.

**ADV-E-01 (Dangling refutation):** Input: text containing ورد عليه بأن (refutation) WITHOUT the position being refuted (it was in a prior division). Expected: self-containment evaluates as DEPENDENT; `self_containment_notes` identifies the missing position; review flag `decontextualization_risk` is present. The engine does NOT silently produce a FULL excerpt that contains only the refutation.

**ADV-E-02 (Implicit reference chain):** Input: text containing كما تقدم → which references another كما تقدم → which eventually resolves to a concrete statement. Expected: IR-1 applies; `self_containment` is PARTIAL (not FULL); `context_hint` describes the unresolved reference chain. The engine does NOT treat a chain of unresolved references as self-contained.

**ADV-E-03 (Multi-layer boundary collision):** Input: matn verse ends mid-sharh paragraph (the verse boundary does not align with a paragraph boundary in the commentary layer). Expected: Phase 2 respects the verse boundary (VC-1) and the sharh paragraph boundary independently; the resulting teaching unit contains the complete verse + its complete commentary paragraph, even if this means one segment spans both boundary types. The engine does NOT split the commentary mid-paragraph to align with the verse boundary.

**ADV-E-04 (Decontextualized evidence):** Input: a hadith cited with its full isnad but WITHOUT the ruling it supports (the ruling is in the next division). Expected: EV-2 (evidence-context binding) flags the isolation; `self_containment` is PARTIAL; `context_hint` notes the missing ruling context. The engine does NOT produce a FULL excerpt containing only the hadith citation without its scholarly application.

**ADV-E-05 (Mixed-attribution unit):** Input: a teaching unit where the first segment is matn (Ibn Malik) and the second segment is sharh (Ibn Aqil) and the third is hashiyah (al-Khudari). Expected: LA-1 assigns `primary_author_layer` based on the dominant layer (most words). `quoted_scholars` includes the non-dominant layer authors with appropriate roles. The engine does NOT attribute the entire unit to one author and silently drop the others.

**ADV-E-06 (Empty division):** Input: a division with 0 content units (e.g., a heading-only division). Expected: Phase 1 skips this division with a documented reason (§4.2 empty division handling). No AssembledChunk is produced. V-P1-1 is satisfied (skip is explicit). The engine does NOT crash or produce an empty chunk.

**ADV-E-07 (Single-sentence division):** Input: a division with <10 words (e.g., a single بسم الله الرحمن الرحيم line). Expected: Phase 1 merges this with an adjacent sibling (§4.4). If no mergeable sibling exists, the tiny division passes through as a single-segment, single-unit chunk. The engine does NOT silently drop it.

**ADV-E-08 (Massive division):** Input: a division with >10,000 words (e.g., an entire dictionary letter under one heading). Expected: Phase 1 splits it into chunks of ≤ OVERSIZED_DIVISION_WORDS, preferring structural markers (§4.5). If no structural markers exist, falls back to word-count splitting with EX-A-006 warning. The engine does NOT send >10K words to the LLM in a single call.

**ADV-E-09 (Overlapping LLM segments):** Input: mock LLM response where segment 3 has `end_word: 50` and segment 4 has `start_word: 48` (overlap of 2 tokens). Expected: §5.4 offset normalization detects the overlap and adjusts boundaries to eliminate it. V-P2-2 (contiguity) passes after normalization. The engine does NOT silently accept overlapping segments (which would cause double-counting in downstream analysis).

**ADV-E-10 (LLM produces 0 segments):** Input: mock LLM response with an empty segments list for a non-empty chunk. Expected: V-P2-5 (full coverage) fails because there are no segments. The retry strategy (§5.5.2) re-attempts classification with error feedback. If all retries are exhausted, `EX-C-001` (classification failed) is emitted and the chunk is skipped — no teaching units are produced. The chunk is flagged for reprocessing in the processing log. The engine does NOT silently drop the chunk without flagging, and does NOT produce fallback segments with artificial classifications.

**ADV-E-11 (Gate write failure):** Input: trigger a gate condition (EX-G-001), but the gate file write fails (simulate I/O error). Expected: EX-M-008 is emitted. The engine retries the write. If the retry fails, the engine HALTS processing for this source (§8.2 — invisible uncertainty is more dangerous than a visible stop). The engine does NOT continue processing with an unwritten gate entry.

**ADV-E-12 (Consensus verification timeout):** Input: trigger consensus verification where the verification model times out on all retries. Expected: the enrichment model's result is kept with a `verification_skipped` flag. The excerpt is produced but with reduced confidence. The engine does NOT discard the excerpt just because verification failed — deterministic fields (F-DET-1–9) are still valid.

### §10.7 — Cross-Engine Contract Tests

These tests verify that the excerpting engine correctly consumes normalization output and produces output that downstream engines can consume.

**Upstream (normalization → excerpting):**

- Read a real `NormalizedPackage` from normalization engine test output. Verify Phase 1 accepts it without schema errors.
- Verify every `source_id` in the input appears in the output excerpts' `source_id` fields.
- Verify all `div_id` references in output excerpts exist in the input `division_tree`.
- Verify `text_layers` in each excerpt are a valid subset of the normalization `layer_map`.
- Verify no field from normalization is silently dropped — every metadata field present in the `ContentUnit` is either used by the engine or passed through to the ExcerptRecord. This is the D-023 test.

**Downstream (excerpting → taxonomy):**

- Produce ExcerptRecords from a test run. Verify they validate against the output schema (§2.2).
- Verify every required field listed in §2.2.4 (downstream consumer contract) is present and non-null.
- Verify the `excerpt_id` format matches the specification.

**End-to-end provenance:**

- Trace one excerpt from `source_id` → `div_id` → `chunk` → `teaching_unit` → `ExcerptRecord`. Verify the provenance chain is unbroken: every ID reference resolves to an actual object.

### §10.8 — Evaluation Methodology (C-7 Mitigation)

C-7 (same-model evaluation bias) is a concern because Claude Opus 4.6 both produces excerpts (Phases 2–3) and may evaluate them. The test suite must structurally mitigate this.

**Mechanical verification (model-independent):** Coverage checks (V-P1-*, V-P2-*, V-P3-*), schema validation, word-count verification, offset consistency, invariant verification — all run without LLM involvement. These catch structural failures regardless of model bias.

**Known-boundary test set:** The architect defines correct teaching unit boundaries for ≥10 divisions (from experiment baselines). Automated tests compare engine output against these known boundaries. Boundary accuracy metric: ≥80% of engine-produced units must overlap ≥80% (by word count) with a known-correct unit. This metric is model-independent because the ground truth was established by human evaluation, not by the same model.

**Cross-model spot checks:** During the evaluation probes (not in the unit test suite, but during the build evaluation phase), 10% of self-containment evaluations are re-run with a different model (the verification model, `openai/gpt-5.4`). Agreement rate between the primary model and the spot-check model is tracked. If agreement drops below 80%, the self-containment evaluation prompt needs revision.

**Owner spot-checks:** During evaluation, the owner reviews 5 excerpts per session for domain-level quality: Is the teaching unit a complete scholarly thought? Is the attribution correct? Does the self-containment level feel right? These checks are model-independent because they rely on domain judgment.

**Regression testing:** All gold baselines (experiment fixtures + owner-verified excerpts from evaluation) are re-run when: the LLM model string changes, a prompt template is modified, a configuration threshold is adjusted, or the consensus verification logic is modified. Regressions in boundary accuracy or self-containment accuracy block the change.

---

