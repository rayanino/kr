# KR Pipeline Architecture Challenge

**Date:** 2026-03-28
**Reviewer:** Architecture adversary (Opus 4.6, 1M context)
**Scope:** Full pipeline architecture, all 7 engine contracts (5,185 lines total), quality system, team architecture
**Stance:** Devil's advocate. Sacred cows questioned. Insight over diplomacy.

---

## 1. Over-Engineering Assessment

### 1.1 The Ghost Engines: Passaging and Atomization

The most glaring over-engineering is that **three engines exist where one would do**. The CLAUDE.md pipeline diagram says:

```
Source -> Normalization --- boundary --- Passaging -> Atomization -> Excerpting -> Taxonomy -> Synthesis
```

But the excerpting engine's own CLAUDE.md says:

> **Absorbs:** passaging (Phase 1) + atomization (Phase 2). Architecture rationale: `experiments/architecture_test/ARCHITECTURE_DECISION.md`.

So the project already discovered that passaging and atomization are unnecessary as separate engines. Yet:

- `engines/passaging/` has 25 source files (556 lines of contracts, 0 tests)
- `engines/atomization/` has 29 source files (676 lines of contracts, 0 tests)
- These are 1,232 lines of contract code for engines that will never run

The passaging contracts define `ReviewFlag` with 15 values, `PassagingStrategy` enums, elaborate boundary models -- all dead code. The atomization contracts duplicate `ScholarlyFunction` (16 values identical to excerpting's). Both import from normalization contracts, creating dependency chains for phantom engines.

**Verdict:** Delete passaging/ and atomization/ entirely. They are architectural ghosts. The decision to absorb them into excerpting was correct, but the corpses were never removed. Their contracts are 1,232 lines of misleading documentation that will confuse every future reader and agent.

### 1.2 Normalization Contracts: The ContentUnit Kitchen Sink

`engines/normalization/contracts.py` (725 lines) defines a `ContentUnit` with 12 fields, many of which are elaborate nested structures that are marked "deferred" in the CLAUDE.md:

- `discourse_flow: Optional[DiscourseFlow]` -- "None in core build." The `DiscourseFlow` model alone requires `DiscourseSegment`, `DiscourseSegmentType` (16 values), `DominantDiscourseType` (6 values), `DiscourseDetectionMethod` (2 values). That is **4 classes and 24 enum values** for a field that is always null.
- `layer_fingerprints: Optional[dict[str, LayerFingerprint]]` -- "Null for single-layer sources." The `LayerFingerprint` model has 10 float metrics (`type_token_ratio`, `connective_frequency`, `information_density`, etc.) and its own `FingerprintReliability` enum. **2 classes and 2 enum values** for a field that is null in the vast majority of sources.
- `tahqiq_topology: Optional[TahqiqTopology]` -- contains `ManuscriptWitness`, `DivisionDisagreement`, `EditionReliability`. **4 classes** for a deferred feature.
- `content_census: Optional[ContentCensus]` -- contains `TextDensityProfile`, `LayerComplexity`, `StructuralDepth`, `FootnoteDensity`, `VocabularyProfile`, `FidelityDistribution`. **7 classes** for a deferred feature.

Total: roughly **17 classes and 30+ enum values** defined in normalization contracts that are always null in the current implementation. These exist because SPECs were written speculatively before implementation reality.

**Verdict:** Move deferred models to a `normalization/contracts_deferred.py` or delete them until needed. YAGNI applies. The current contracts file is 725 lines; the core models that actually carry data would be under 350.

### 1.3 Source Engine: ScholarlyContext Is Speculative LLM Output Masquerading as a Data Model

`ScholarlyContext` in `engines/source/contracts.py` (lines 387-502, ~115 lines) defines 10 fields like `composition_period`, `tradition_position`, `muhaqiq_reputation`, `edition_known_issues`. Each field has a multi-line description explaining which downstream engine consumes it.

The problem: **these are free-text LLM narratives stored as structured fields**. The field `historical_significance` is described as:

> "What makes this work notable in its tradition -- historical importance, known controversies, composition context..."

This is not structured data. This is an LLM essay stored in a typed Optional[str] field. Putting it in a Pydantic model with a 6-line description does not make it structured -- it makes it a string with a long comment.

The `context_richness: Literal["rich", "partial", "minimal"]` field is "LLM self-assessment of its knowledge." An LLM rating its own knowledge reliability is a confidence metric about a confidence metric. The `uncertain_dimensions: list[str]` field is "names of specific fields the LLM flagged as uncertain" -- the LLM telling you which of its own answers it does not trust, stored as a list of strings.

**Verdict:** ScholarlyContext should be a single freeform JSON blob (or markdown string) until there is evidence that downstream engines actually parse individual fields programmatically. The elaborate typing gives false precision to inherently fuzzy LLM-generated narratives.

### 1.4 Consensus Mechanism: Blanket Rule vs. Calibrated Application

Critical Rule 7 states:

> Multi-model consensus for content decisions. Never single LLM call for attribution.

The `llm-call-optimization.md` rule says:

> For ALL content classification decisions (genre, author, science scope, madhab, authority level, structural format), use a minimum of 2 independent models.

This is applied as a blanket rule. But the source engine's own validation data tells a different story:

- Consensus pair accuracy was 92.3% "at-least-one-right" (from MEMORY.md)
- The validation in Step 2 showed 100% accuracy for multi-layer detection across **all 5 models**

If all 5 models agree 100% on multi-layer detection, consensus voting adds cost and latency for zero accuracy gain on that classification type. The "never single-model" rule was calibrated on the hardest classification tasks (genre, science scope) and then applied to all tasks regardless of difficulty.

Classification types where single-model would likely suffice (based on the validation data described):
- **is_multi_layer** -- 100% agreement across 5 models. This is a visual/structural feature, not a scholarly judgment call.
- **source_format** -- Shamela HTML vs. PDF is format detection, not content analysis. A single regex could do this.
- **text_fidelity** -- HIGH for Shamela, MEDIUM for PDF. This is source-type lookup, not LLM judgment.

Classification types where consensus is genuinely justified:
- **genre** -- sharh vs. hashiyah vs. taqrirat requires understanding scholarly relationships
- **science_scope** -- a text mentioning both fiqh and usul al-fiqh examples requires nuanced judgment
- **author identification** -- scholar disambiguation is the hardest task

**Verdict:** The consensus rule should be calibrated per classification type. A cost-to-accuracy analysis for each type would likely show that 4-5 classification types can safely use single-model, saving 40-50% of LLM costs on the source engine's inference phase.

### 1.5 Could Any Two Engines Be Merged?

**Yes -- taxonomy and synthesis should be merged.** Here is the reasoning:

Taxonomy's core job (from its CLAUDE.md): "Places each excerpt at the best-matching taxonomy leaf." Synthesis's core job: "Compiles placed excerpts into scholarly entries."

The current flow is: excerpts -> taxonomy places them on leaves -> synthesis reads placed excerpts and generates entries. But placement and compilation are conceptually a single operation: "given these excerpts and a tree, produce entries." The intermediate artifact (a "placed excerpt" which is just an excerpt with an extra field `confirmed_leaf`) does not justify an engine boundary.

The taxonomy contracts define `PlacedExcerptAdditions` with 10 fields. Seven of those (`placement_confidence`, `review_metadata`, `verified_flagged_status`, `taxonomy_version_at_placement`, `placement_reasoning`, `proposed_leaf_override`, `proposed_leaf_original`) are process metadata about the act of placement itself. Only `confirmed_leaf` is semantically load-bearing for synthesis.

A merged "taxonomy+synthesis" engine would:
1. Receive excerpts
2. Place them on leaves (current taxonomy Phase 1)
3. Compile entries per leaf (current synthesis core)

This eliminates one full engine boundary, one contracts.py (565 lines synthesis + 491 lines taxonomy = 1,056 lines reduced to ~700), and one set of cross-engine validation tests.

**Counter-argument:** Tree evolution (leaf splits, branch restructuring) is complex enough to warrant isolation. But tree evolution is a `§4.B` deferred feature. The core taxonomy engine is just "place excerpts." At the current stage, merging is safe and simplifying.

### 1.6 Unused Downstream Contract Fields

Fields defined in source contracts that are [NOT YET IMPLEMENTED] and never consumed:

- `SourceMetadata.compositional_profile: Optional[CompositionalProfile]` (§4.B.5 -- KITAB text reuse)
- `SourceMetadata.difficulty_prediction: Optional[DifficultyPrediction]` (§4.B.9)
- `SourceMetadata.tahqiq_fingerprint: Optional[TahqiqFingerprint]` (§4.B.10)
- `ScholarAuthorityRecord.genealogy_metadata: Optional[GenealogyMetadata]` (§4.B.7)
- `ScholarAuthorityRecord.cross_validation: Optional[CrossValidationResult]` (§4.B.8)

These are all `Optional` fields that are always `None`. They exist because SPECs were written to include Stage 2 capabilities. Together they account for roughly 150 lines of contract code (including their sub-models: `IntertextualMetrics`, `TextReuseEntry`, `CompositionalProfile`, `EditionDivergence`, `EditionComparisonSummary`, `EditionComparison`, `GenealogyMetadata`, `DeathDateAgreement`, `KnownWorksUnion`, `WikidataTeacherStudentLinks`, `CrossValidationDiscrepancy`, `CrossValidationResult`).

**Verdict:** These should be removed until the features exist. They are dead declarations that increase cognitive load and contract file size without providing any runtime value.

---

## 2. Weakest Assumptions

### 2.1 The Shamela Monoculture

The entire normalization engine (and the 63 test fixtures) is built around Shamela HTML. The `SourceFormat` enum lists 8 formats:

```python
SHAMELA_HTML = "shamela_html"
PDF_TEXT = "pdf_text"
PDF_SCANNED = "pdf_scanned"
IMAGE_SCAN = "image_scan"
PLAIN_TEXT = "plain_text"
EPUB = "epub"
WORD_DOC = "word_doc"
OWNER_AUTHORED = "owner_authored"
```

Only two are implemented: `shamela_html` and `plain_text`. The normalization engine has exactly two normalizers: `shamela.py` and `plain_text.py`.

The normalization boundary is described as:

> if adding a new source type requires changing any of these models, the boundary has been violated.

But the normalization contracts are deeply shaped by Shamela's structure:
- `PhysicalPage` with `volume` and `page_number_display` in Arabic numerals -- PDF sources number pages differently
- `Footnote` with `ref_marker` assumes numbered footnote references -- manuscripts have marginal annotations without markers
- `TextLayerSegment` with character offsets assumes layers are interleaved inline -- PDF scans may have layers on separate pages
- The 6-pass Shamela pipeline (parse -> footnotes -> clean -> structure -> layers -> assemble) is Shamela-specific; a PDF pipeline would be completely different

**The normalization boundary is not actually format-agnostic.** It is Shamela-agnostic-pretending-to-be-format-agnostic. Adding PDF support will require significant model changes or awkward adapter patterns.

### 2.2 The LLM Cost Assumption Will Shatter

The system currently uses:
- Claude Opus 4.6 for primary classification and enrichment
- GPT-5.4 for verification
- Mistral Large for escalation

At EUR 36.70 for 274 books in the source engine, extrapolate to:
- Excerpting: likely 3-5x more LLM calls per book (classification + grouping + enrichment + verification per chunk)
- Taxonomy: 1-2 LLM calls per excerpt for placement
- Synthesis: 3-5 LLM calls per entry (analysis + construction + entailment + verification)

For a 7,000-book library, the cost per full pipeline run could reach EUR 5,000-10,000. The project already has budget guard hooks (`cost-guard.sh`), but the fundamental question is: **does the per-call architecture scale?**

When models get 10x cheaper (likely within 12-18 months), the cost concern evaporates. But the latency concern does not. Processing 7,000 books sequentially through 3-5 LLM calls per engine per book, with consensus verification, at ~90 seconds per call... that is weeks of calendar time.

**What ages worst:** The assumption that each LLM call processes one chunk/excerpt/entry at a time. Batch APIs, prefill caching, and speculative decoding are evolving fast. The pipeline's per-item sequential architecture means it cannot exploit batch pricing or throughput optimizations.

### 2.3 What If Models Get 10x Better?

If a single model can reliably:
- Parse Shamela HTML into structured JSON (currently the normalization engine)
- Identify genre, author, school with 99% accuracy (currently multi-model consensus)
- Split text into self-contained teaching units (currently 3-phase excerpting)
- Place excerpts on taxonomy leaves (currently taxonomy engine)
- Generate scholarly entries (currently synthesis engine)

...then most of the pipeline's value is in its **schema definitions and quality constraints**, not in its processing logic. The pipeline becomes a validation harness around a single LLM call, not a multi-engine decomposition.

This is already partially true. The excerpting engine's Phase 1 (assembly) is the only fully deterministic phase. Phases 2 and 3 are both LLM-dependent. If the LLM could do assembly + classification + grouping + enrichment in one call, 80% of the excerpting engine's code is unnecessary.

**The pipeline's complexity is proportional to how little we trust the LLM.** As trust increases, the pipeline should contract. But the architecture has no mechanism for this contraction -- it is designed as if the current level of LLM capability is permanent.

### 2.4 Shamela Format Change Risk

Shamela publishes books as single `.htm` files with a specific HTML structure (PageText divs, metadata cards). If Shamela:
- Switches to a REST API (likely -- Shamela Zad already has one)
- Changes their HTML structure
- Adds or removes metadata fields
- Switches to JSON exports

...the entire Shamela normalizer (the most tested, most hardened code in the pipeline) becomes obsolete. The normalization boundary handles this correctly in theory (new normalizer, same output format). But in practice, the test fixtures, the HTML reference docs, and the domain knowledge encoded in 13 real Shamela fixtures would all need updating.

### 2.5 The "Personal Library" Assumption

The system is designed for one user. Every design decision reflects this:
- Human gates assume a single reviewer
- The scholar authority registry has no access control
- Trust tiers are calibrated to one person's standards
- The synthesis engine generates entries for one user's learning level

This makes multi-tenancy or even shared use architecturally impossible without fundamental redesign. If the owner ever wants to share his library or collaborate with other scholars, the single-user assumption is embedded in every contract.

---

## 3. Embeddings vs. LLM Calls

### 3.1 Topic Classification: Embedding Model

**Current approach:** LLM consensus (2 models) classifies each excerpt's `excerpt_topic` (1-3 Arabic keywords) and places it on a taxonomy leaf.

**Alternative:** Fine-tune an Arabic embedding model (e.g., `intfloat/multilingual-e5-large` or `aubmindlab/bert-base-arabertv2`) on the existing taxonomy tree. Each leaf gets an embedding from its title + description + existing excerpt samples. New excerpts are embedded and matched by cosine similarity.

**Estimated accuracy loss:** 5-10% for clear-cut topics (fiqh al-taharah, nahw al-i'rab), 15-25% for cross-science topics (niyyah in worship vs. contracts, qasd in usul vs. qawa'id). The long tail of ambiguous placements is where LLM reasoning genuinely helps.

**Cost/speed gain:** Embedding calls cost ~1/100th of LLM calls. Inference is 10-100x faster. A fine-tuned model could classify all 7,000 books' excerpts in minutes rather than days.

**Recommendation:** Use embeddings as a first-pass filter. If cosine similarity > 0.85, auto-place. If 0.6-0.85, use single LLM call. If < 0.6, use consensus. This would route ~60-70% of placements through embeddings, ~25% through single LLM, and ~5-10% through consensus. Cost reduction: ~80%.

### 3.2 Genre Detection: TF-IDF on Arabic Keywords

**Current approach:** LLM consensus classifies genre from the 20-value `Genre` enum.

**Alternative:** TF-IDF on Arabic structural keywords. The genre signals are remarkably consistent:
- `sharh` titles contain "شرح" in 95%+ of cases
- `hashiyah` titles contain "حاشية" in 90%+ of cases
- `mukhtasar` titles contain "مختصر" in 90%+ of cases
- `tafsir` books contain "تفسير" or "المراد بقوله تعالى" in the title or first 500 chars
- `hadith_collection` books have dense isnad chains (حدثنا / أخبرنا) in the first 10 pages

A TF-IDF model trained on the 274 already-classified books plus title keyword matching could handle 80-85% of genre classifications correctly.

**Estimated accuracy on the remaining 15-20%:** Poor. The hard cases are: `risalah` vs. `matn` (both are short standalone works), `fiqh_comparative` vs. `sharh` (both discuss multiple opinions), `usul_al_fiqh` vs. `fiqh` (methodological vs. applied). These genuinely require LLM reasoning about content, not keyword matching.

**Recommendation:** Keyword-based classification for the 8 genres with strong title signals (sharh, hashiyah, mukhtasar, nazm, tafsir, hadith_collection, tabaqat, mujam). LLM consensus only for the remaining 12 genres. Cost reduction: ~40-50% of source engine LLM calls.

### 3.3 Author Matching: Embedding Similarity

**Current approach:** `scholar_authority` module with name matching, capped at 0.65 for name-only matches.

**Alternative:** Embed Arabic scholar names (with all variants: kunya, laqab, nisba) into a vector space. New author names are embedded and matched by cosine similarity against the registry.

**Problem:** Arabic scholar names are highly structured (ism + nasab + kunya + laqab + nisba) but the overlap between scholars is extreme. "ابن حجر" matches both Ibn Hajar al-Asqalani (d. 852 AH, Shafi'i hadith scholar) and Ibn Hajar al-Haytami (d. 974 AH, Shafi'i fiqh scholar). Embedding similarity would match these as near-identical, while the current system uses death dates and science scope to disambiguate.

**Estimated accuracy loss:** 15-30% for scholars with common name components (there are dozens of scholars called "ابن قدامة" across centuries). The disambiguation requires biographical knowledge that embeddings do not capture.

**Recommendation:** Embedding similarity as a candidate retrieval step (top-5 matches), then deterministic disambiguation using death date + science scope + known works. This is roughly what the current system does but with embeddings replacing substring matching for the initial candidate set. Speed gain: moderate. Accuracy gain: potentially positive for unusual name variants that substring matching misses.

---

## 4. 10x Simplification

### 4.1 Three Engines Instead of Five

Keep: **Source, Normalization, Compilation** (where Compilation = excerpting + taxonomy + synthesis merged).

**Source Engine** (unchanged): Acquire, identify, freeze, extract metadata. This is genuinely distinct -- it deals with file formats, hashing, deduplication, and scholar authority. Cannot be merged.

**Normalization Engine** (unchanged): Transform source-specific formats into a universal schema. The normalization boundary is a real and valuable abstraction. Cannot be merged.

**Compilation Engine** (excerpting + taxonomy + synthesis merged): Take a normalized package, produce entries. This engine would:

1. Walk the division tree, assemble chunks (current excerpting Phase 1)
2. Classify segments, group into teaching units (current excerpting Phase 2)
3. Enrich with consensus verification (current excerpting Phase 3)
4. Place on taxonomy leaves (current taxonomy core)
5. Compile entries per leaf (current synthesis core)

The intermediate artifacts (ExcerptRecord, PlacedExcerpt) become internal data structures, not engine boundary contracts. The only output is the `Entry` -- the knowledge product.

**What is lost:** The ability to re-run taxonomy without re-running excerpting. The ability to re-run synthesis without re-running taxonomy. In practice, how often does this actually happen? Re-running taxonomy alone requires all excerpts to already exist. Re-running synthesis alone requires all placements to exist. The realistic workflow is: process a book end-to-end, or reprocess a book end-to-end.

**What is gained:**
- Eliminate 2 engine boundary contracts (1,056 lines)
- Eliminate 2 sets of cross-engine validation tests
- Eliminate intermediate artifact persistence (excerpts.jsonl, placed excerpts)
- Simplify the pipeline runner to 3 steps instead of 5
- Reduce total contracts.py from 5,185 lines to ~3,000 lines

### 4.2 The 10x Simpler Version

**Target:** Personal Arabic scholarly library with knowledge integrity guarantees.

```
Step 1: Ingest (source format -> structured JSON)
Step 2: Extract (structured JSON -> excerpts with metadata)
Step 3: Compile (excerpts + tree -> entries)
```

Each step is one Python module, not an engine. No Pydantic contracts -- just typed dataclasses. No multi-model consensus -- single model with confidence thresholds and human gates for low confidence. No elaborate error code system -- Python exceptions with structured logging.

The normalization boundary still exists (Step 1 output is format-agnostic). The quality constraints still hold (diacritics preserved, metadata traced, errors fail loud). But the ceremony is reduced by 10x.

**What is lost:** Multi-model consensus removes a genuine safety net for content classification. The elaborate error code system (28 error codes in excerpting alone) provides audit-grade traceability that simple exceptions do not. The Pydantic model validators catch data integrity issues at construction time.

**What is gained:** A system that a single developer can understand, modify, and debug. The current system has 5,185 lines of contracts alone -- before any implementation code. A new contributor must read ~10,000 lines of SPEC + contracts before writing a line of code.

### 4.3 Minimum Viable Pipeline Preserving Knowledge Integrity

The non-negotiable requirements (from CLAUDE.md Critical Rules):
1. Frozen sources are immutable
2. Primary text is never modified
3. Every claim is traceable
4. Errors fail loudly
5. Human gates for irreversible changes
6. Metadata flows forward

The minimum pipeline that satisfies all six:

```python
# Step 1: Ingest + Freeze
frozen_path, hash = freeze(source_file)
metadata = extract_metadata(source_file)  # single LLM call, structured output
if metadata.confidence < 0.7:
    metadata = human_review(metadata)  # human gate
save_metadata(metadata)

# Step 2: Normalize + Excerpt
normalized = normalize(frozen_path, metadata.source_format)  # deterministic
excerpts = excerpt(normalized)  # single LLM call per division, structured output
for exc in excerpts:
    exc.source_id = metadata.source_id  # traceability
    exc.metadata = metadata  # metadata flows forward
    if exc.self_containment == "DEPENDENT":
        exc = human_review(exc)  # human gate
save_excerpts(excerpts)

# Step 3: Place + Compile
for exc in excerpts:
    leaf = classify(exc, tree)  # single LLM call
    place(exc, leaf)
entries = compile_entries(tree)  # single LLM call per leaf
for entry in entries:
    verify(entry)  # different model verifies
save_entries(entries)
```

This is ~50 lines of pseudocode. The current pipeline is ~10,000 lines of implementation code. The gap is where justified complexity and unjustified ceremony meet.

---

## 5. Missing Capabilities

### 5.1 Search and Retrieval: The Elephant in the Room

The pipeline produces entries. But there is **no search system**. The owner has no way to:
- Search for "what do the Hanafis say about wiping over socks?"
- Find all excerpts by Ibn Taymiyyah on a topic
- Search by Quran verse or hadith reference
- Full-text search across 7,000 books of Arabic text

The synthesis engine produces entries organized by taxonomy leaf. But scholarly inquiry does not follow taxonomy trees. A student might want to find every mention of a specific hadith across all books. Or every place where a specific scholar is quoted. Or every excerpt that discusses a specific Quranic verse.

**Without search, the library is a bookshelf you can only browse by category.** You can find "the entry on wudu requirements" but not "everywhere Ibn Qudama discusses tayammum conditions."

The contracts already have the building blocks:
- `EvidenceRef` has Quran surah/ayah references -- these could power verse-level search
- `ScholarAttribution` tracks quoted scholars -- these could power scholar-level search
- `excerpt_topic` has Arabic keywords -- these could power topic search

But there is no indexing system, no search engine integration, no retrieval pipeline.

**Recommendation:** Add a vector index (Qdrant, Weaviate, or even FAISS) as a post-synthesis step. Embed every excerpt and every entry. This enables semantic search in Arabic, cross-reference discovery, and "more like this" recommendations. Cost: minimal (embedding is cheap). Value: transforms the library from a static encyclopedia to an interactive research tool.

### 5.2 Cross-Book Linking: The Scholarly Web

Islamic scholarly texts are deeply intertextual. A sharh quotes the matn. A hashiyah quotes the sharh. A later scholar cites all three. The pipeline currently models this at the work level (`GenreChain`, `WorkRelationshipEdge`) but not at the excerpt level.

**Missing:** Given an excerpt from Sharh al-Mumti' by Ibn Uthaymeen, the system cannot automatically link to:
- The corresponding passage in Zad al-Mustaqni' (the matn being explained)
- The corresponding passage in al-Rawdh al-Murbi' (another sharh of the same matn)
- Other excerpts that discuss the same fiqh ruling from different schools

The `cross_references` field in `ExcerptRecord` captures explicit references ("as mentioned in the chapter on sales"), but implicit connections (two excerpts discussing the same topic from different books) are not captured.

**Recommendation:** After excerpting, compute pairwise embedding similarity between excerpts at the same taxonomy leaf. Excerpts with similarity > 0.85 that come from different sources are "parallel discussions." Store these as a link graph. This enables the synthesis engine to produce richer entries ("Ibn Qudama and al-Nawawi both discuss this point, but differ on the condition of intention...").

### 5.3 Temporal Evolution and Corrections

The synthesis engine has version tracking (`EntryVersionRecord`, `ChangeSummary`, `StalenessSignal`). But the excerpting engine has no concept of corrections. Once an excerpt is produced, it is immutable. This means:

- If the owner finds an error in an excerpt's `school` attribution, there is no mechanism to correct it without re-running the entire excerpting pipeline for that source
- If a new edition of a book is acquired, there is no diff mechanism to identify what changed
- If the owner annotates an excerpt with a note, there is nowhere to store it

The `EditionComparison` model in source contracts is [NOT YET IMPLEMENTED]. Edition comparison is a genuinely valuable capability for a scholarly library -- knowing which edition to trust for a specific passage is core scholarly methodology.

### 5.4 Collaborative Features

The system is designed for a single owner. But Islamic scholarly study is inherently social:
- Students study with teachers who annotate texts
- Study circles (halaqat) discuss specific passages
- Scholars issue corrections or amendments to published works

**Missing:** Any concept of annotation, commentary, or shared review. The `OwnerCorrection` model in synthesis contracts is the closest thing, but it is limited to error reports, not scholarly engagement.

This is explicitly out of scope ("never optimizes for user experience"), but it represents a fundamental limit on the library's scholarly value. A library that only one person can use is a private notebook, not a scholarly tool.

### 5.5 Non-Arabic Content

The pipeline is hardcoded for Arabic. But Islamic scholarly texts exist in:
- Persian (significant corpus, especially in Hanafi fiqh and Sufi literature)
- Ottoman Turkish
- Urdu (major scholarly tradition, especially from the Indian subcontinent)
- Malay (Southeast Asian scholarly tradition)

The `language: str = Field(default="ar")` in `SourceMetadata` acknowledges this, but every Arabic-specific rule (diacritics preservation, the entire `arabic-text` skill, the Arabic scholarly conventions rules file) would need parallel implementations.

### 5.6 Incremental Processing

The pipeline processes one source at a time, end-to-end. There is no concept of incremental updates. If one new book is added:
- Source engine processes it (fast)
- Normalization processes it (fast)
- Excerpting processes it (slow -- LLM calls)
- Taxonomy must re-evaluate placements (the new book might shift leaf boundaries)
- Synthesis must regenerate entries for every leaf where the new book placed excerpts

The staleness detection mechanism in synthesis handles this in theory, but the cascade through taxonomy is not addressed. Adding one book could trigger regeneration of dozens of entries.

**The missing capability:** Incremental taxonomy placement that does not disturb existing placements unless the new excerpt genuinely conflicts. And incremental entry regeneration that patches rather than regenerates.

---

## Summary of Recommendations (Prioritized)

| Priority | Action | Impact | Effort |
|----------|--------|--------|--------|
| 1 | Delete passaging/ and atomization/ engine directories | Remove 1,232 lines of dead contracts, eliminate confusion | 1 hour |
| 2 | Move deferred contract models to separate files or delete | Reduce cognitive load by ~500 lines across contracts | 2 hours |
| 3 | Calibrate consensus per classification type | Save 40-50% of source engine LLM costs | 1 session |
| 4 | Add embedding-based first-pass for topic classification | Save 80% of taxonomy LLM costs | 2 sessions |
| 5 | Plan search/retrieval architecture now | Without search, the library is unusable for real scholarship | Design only |
| 6 | Evaluate taxonomy+synthesis merge | Eliminate 1 engine boundary, ~1,000 lines of contracts | Design study |
| 7 | Add keyword-based genre classification for clear cases | Save 40-50% of genre classification LLM calls | 1 session |
| 8 | Plan cross-book excerpt linking | Transforms the library from categorized to connected | Design only |

---

## Closing Thought

The KR pipeline is over-engineered in its ceremony (7 engines, 5,185 lines of contracts, 28+ error codes per engine) and under-engineered in its utility (no search, no cross-linking, no incremental updates). The contracts define elaborate data structures for features that do not exist, while omitting the systems that would make the library actually usable as a scholarly tool.

The strongest part of the architecture is the normalization boundary -- the insight that source-format-specific logic must be isolated from source-agnostic processing. This is a genuinely valuable abstraction that should be preserved regardless of simplification.

The weakest part is the assumption that complexity equals correctness. 1,232 lines of contracts for engines that were absorbed into another engine do not make the pipeline more correct. 17 deferred model classes that are always null do not prevent errors. A consensus mechanism applied uniformly to all classification types does not optimize for accuracy -- it optimizes for the appearance of rigor.

The pipeline should be as complex as necessary and no more. Currently, it is considerably more.
