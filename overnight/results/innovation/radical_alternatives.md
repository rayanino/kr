# Radical Alternatives to the KR Pipeline Architecture

**Date:** 2026-03-28
**Author:** Claude Opus 4.6 (research agent)
**Status:** RESEARCH ONLY — no code changes, no commitments

---

## Context: What the Current Pipeline Does

The KR pipeline processes Islamic scholarly Arabic texts through 5 engines:

```
Source --> Normalization --> Excerpting --> Taxonomy --> Synthesis
```

Source identifies and classifies books (274 books, EUR 36.70, multi-model consensus).
Normalization extracts clean structured text from Shamela HTML (7,475 books, 100% success).
Excerpting transforms text into self-contained teaching units (595 tests, LLM integration phase).
Taxonomy places excerpts in a hierarchical knowledge tree (not yet built).
Synthesis combines excerpts into encyclopedic entries with scholarly narrative (not yet built).

The pipeline's defining characteristics:
- **Multi-model consensus** (D-041) for every content decision (never single LLM)
- **Metadata flow** (D-023) — upstream fields pass through to synthesis, never deleted
- **Frozen sources** — bytes are immutable after ingestion
- **Human gates** — no irreversible change without owner approval
- **Self-contained excerpts** — every teaching unit stands alone
- **Scholarly attribution** — every claim traces to a source, author, and text layer

The quality target (ENTRY_EXAMPLE.md) shows the end product: a rich scholarly entry with temporal depth across 500+ years, intellectual genealogy (teacher-student chains), school context (Basran vs Kufan), edge cases, and reading paths. This requires metadata far beyond what raw text provides.

---

## Alternative 1: RAG (Retrieval-Augmented Generation) Instead of Pipeline

### The Idea

Skip excerpting, taxonomy, and synthesis entirely. After normalization:
1. Chunk all normalized text into overlapping windows (512-1024 tokens)
2. Embed each chunk using an Arabic-capable embedding model
3. Store in a vector database (Pinecone, Weaviate, ChromaDB, or Qdrant)
4. At query time, retrieve top-K relevant chunks and synthesize on-the-fly

The vector store replaces the taxonomy engine. The LLM prompt at query time replaces the synthesis engine. No excerpting needed — chunks are the raw material.

### Feasibility Assessment

**Arabic embedding quality:** This is the critical question. Current Arabic embedding models:
- **Arabic BERT / AraGPT2:** Trained primarily on modern standard Arabic and news corpora. Islamic scholarly Arabic uses specialized vocabulary (isnad formulas, fiqh terminology, nahw technical terms) that is underrepresented. Diacritics are typically stripped during training, losing information that distinguishes words in scholarly text (e.g., كَتَب "he wrote" vs كُتُب "books").
- **Multilingual models (e5-large, BGE-m3, multilingual-e5):** Better cross-lingual transfer but weaker on domain-specific Arabic. A nahw term like "المبتدأ" might embed close to its literal meaning ("the beginning") rather than its grammatical meaning ("the subject of a nominal sentence").
- **OpenAI text-embedding-3-large / Cohere embed-v3:** Commercial models with strong multilingual support. Likely the best off-the-shelf option, but no published benchmarks on classical Arabic scholarly text. Diacritic handling is unknown.

**Multi-layer text handling:** This is where RAG fundamentally breaks. A page from شرح ابن عقيل contains Ibn Malik's verse (Layer 1, 672 AH) and Ibn Aqil's commentary (Layer 2, 769 AH). A naive chunking window would embed both layers together. At retrieval time, there is no way to attribute which part of the chunk belongs to which author. The entire attribution chain (T-2 threat in the knowledge integrity model) is destroyed.

**Diacritic sensitivity:** Most embedding models normalize or ignore diacritics. In scholarly Arabic, diacritics carry grammatical analysis (i'rab), pronunciation (qira'at in Quranic text), and disambiguation. A RAG system that treats "كتب" and "كُتُبٌ" as identical vectors would produce incorrect retrievals for grammar-focused queries.

**Self-containment:** RAG chunks are arbitrary windows, not scholarly units. A definition that starts mid-chunk and ends in the next chunk would never be retrieved as a complete thought. The current excerpting engine's teaching-unit concept (the smallest segment from which a student can learn a complete scholarly thought) has no equivalent in RAG.

### What We Would Lose

- **Structured teaching units** — the core knowledge product. A RAG chunk is not a "definition with its evidence and edge cases." It is a window of tokens.
- **Scholarly attribution** — which scholar said what, in which text layer, from which school. RAG cannot distinguish layers within a retrieved chunk.
- **The ENTRY_EXAMPLE quality target** — temporal depth, intellectual genealogy, school context, reading paths. These require structured metadata that RAG does not produce. The synthesizer in the current pipeline draws from 7 excerpts across 5 sources with rich per-excerpt metadata. A RAG system would retrieve 10 chunks and hope the LLM can reconstruct the narrative. It cannot — the metadata is not in the text.
- **Human gates** — RAG answers are generated at query time. There is no point to review and approve quality, because every answer is novel.
- **Reproducibility** — the same query can produce different chunks (embedding drift, index updates) and different synthesis (LLM temperature). The pipeline produces a fixed library.

### What We Would Gain

- **Simplicity** — no excerpting, taxonomy, or synthesis engines to build and maintain.
- **Flexibility** — adding a new book means embedding its chunks, not rerunning the pipeline.
- **Instant queries** — no need to wait for the library to be fully built.
- **Exploratory use** — "find me everything about X across all 7,475 books" is trivial.

### Verdict

| Dimension | Score |
|-----------|-------|
| Feasibility | 2/5 |
| Value | 2/5 |
| Effort | M (3-4 weeks to prototype) |
| Recommendation | **Research further as COMPLEMENT, reject as replacement** |

RAG cannot produce the ENTRY_EXAMPLE quality target. The scholarly narrative requires structured metadata that embedding-based retrieval does not generate. However, RAG could be valuable as a complementary access layer AFTER the pipeline has produced its structured library. Users could query the vector store for exploratory searches, then follow links to the structured entries.

**What KR would need to try this:**
- Benchmark Arabic scholarly embedding quality (3-5 models on KR fixture texts)
- Solve the multi-layer chunking problem (layer-aware windowing)
- Accept lower quality for exploratory queries vs structured entries
- Budget: ~$50-100 for embedding 7,475 books, plus ongoing vector DB hosting

---

## Alternative 2: Fine-Tuned Models Instead of Few-Shot Prompting

### The Idea

Replace expensive multi-model consensus LLM calls with fine-tuned specialized models:
- Fine-tune Arabic BERT for genre classification (replacing Cohere + Claude consensus)
- Fine-tune a small model for scholarly function classification (the 16-type ScholarlyFunction enum)
- Fine-tune for topic keyword extraction, author attribution, school detection
- Cost drops from ~EUR 0.13/book (source engine) to near-zero inference

### Training Data Assessment

**What exists:**
- 274 books with source engine verdicts: genre, author, science scope, madhab, death date, structural format, authority level. Multi-model consensus with 92.3% at-least-one-right accuracy. This is labeled data.
- 7 real Arabic fixtures with ground truth (`GROUND_TRUTH.json`, `EXTRACTED_DATA.json`).
- Phase 2 classification results from the excerpting integration test: 23 excerpts with ScholarlyFunction labels.
- Library science trees (nahw, sarf, aqidah, balagha, imlaa) with taxonomy nodes.

**What is missing:**
- 274 books is a very small training set for fine-tuning. Modern fine-tuning guidance suggests 1,000+ examples minimum for reliable generalization.
- The labels are model-generated (consensus verdicts), not human-verified. Fine-tuning on model outputs is distillation, not supervised learning. Errors in the consensus propagate.
- The 23 excerpt-level classifications are far too few for ScholarlyFunction fine-tuning.
- No negative examples (adversarial cases where classification is ambiguous).

**Format requirements:**
- Genre classification: input = Arabic text excerpt (first 2000 tokens), output = one of ~10 genre labels. Standard text classification — Arabic BERT or CAMeL-BERT could handle this.
- ScholarlyFunction: input = Arabic text segment (50-500 tokens), output = one of 16 function labels. Needs segment-level training data, which we have almost none of.
- Author attribution: input = text + colophon + metadata, output = scholar ID. This is too complex for a simple classifier — it requires reasoning about honorifics, nasab chains, death dates, and cross-referencing.

### Accuracy Trade-Off

The fundamental tension: KR's design principle is "accuracy > everything." The project treats errors as corruption of the owner's knowledge. A fine-tuned BERT achieving 95% accuracy on genre means 5% of books are misclassified — approximately 374 books out of 7,475. Those 374 books would have wrong genres propagating through excerpting, taxonomy, and synthesis, producing incorrect scholarly entries.

The current consensus approach (2 large models agreeing) flags disagreements for human review. A fine-tuned model has no disagreement signal — it just outputs a label with a confidence score. Confidence calibration for Arabic scholarly text is an open research problem. A model might output 0.92 confidence for a wrong genre because the training data was too small to learn the distinction.

**Where fine-tuning COULD work:** Binary or near-binary decisions with clear signals.
- Is this text multi-layer? (yes/no — structural signal is strong)
- Is this a Quranic citation? (distinctive brackets and formulas)
- Does this segment contain an isnad? (transmission formula detection)

**Where fine-tuning CANNOT replace LLMs:** Nuanced scholarly judgments.
- What genre is this text? (sharh vs hashiyah requires understanding the commentary relationship)
- Who wrote this? (requires reasoning about colophon formulas, honorifics, historical context)
- What teaching units exist in this text? (requires understanding scholarly argument structure)

### Cost Analysis

- **Current cost:** EUR 36.70 for 274 books (source engine). Projected EUR ~1,000 for full 7,475-book run across all engines.
- **Fine-tuning cost:** ~$10-50 per model on current platforms (OpenAI, Cohere, Mistral). One-time.
- **Inference cost:** Near-zero. Arabic BERT runs locally on CPU in milliseconds.
- **Hidden cost:** Labeling additional training data (human expert time). If we need 1,000+ labeled examples per classification task and have 6+ classification tasks, that is 6,000+ labels. At 2 minutes per label, that is 200 hours of expert time.
- **Maintenance cost:** When the taxonomy evolves (new genres discovered, new sciences added), the model must be retrained. LLM prompts just need a prompt update.

### Verdict

| Dimension | Score |
|-----------|-------|
| Feasibility | 3/5 |
| Value | 2/5 |
| Effort | L (8-12 weeks including labeling) |
| Recommendation | **Prototype for binary tasks only, reject for scholarly judgments** |

Fine-tuning is attractive for cost reduction but fundamentally incompatible with KR's accuracy-first design. The project's multi-model consensus exists precisely because no single model (even a large one) is trusted for scholarly content decisions. Replacing consensus with a single fine-tuned small model inverts the safety architecture.

**What KR would need to try this:**
- Label 1,000+ examples per task (requires domain expert, not just any Arabic speaker)
- Benchmark CAMeL-BERT / AraBERT on KR fixture texts for binary tasks
- Establish confidence thresholds that match human-gate trigger rates
- Accept that fine-tuned models handle "easy" cases while LLMs handle "hard" ones (hybrid approach)

---

## Alternative 3: Incremental Pipeline Instead of Batch

### The Idea

Process books one at a time. Each new book's processing is informed by the existing library state:
- "This book discusses nahw topic X — we already have 5 excerpts on X from 3 other scholars"
- "This author (Ibn Qudama, d. 620 AH) is already in the scholar registry with known school and teachers"
- "This excerpt covers the same ruling as excerpt EXC-00342 from a different school — flag as cross-reference"

The library grows book by book, with each addition enriching the context for future books.

### Architectural Analysis

**What changes:**
- Every engine needs read access to the current library state (science trees, scholar registry, source registry, existing excerpts).
- The excerpting engine's LLM prompt includes: "Here are existing excerpts on this topic from other sources" — enabling better self-containment evaluation and cross-reference detection.
- The taxonomy engine can propose placement based on where similar excerpts already live, rather than classifying from scratch.
- The synthesis engine can incrementally update entries as new excerpts arrive, rather than building from scratch.

**Processing order matters — critically.** The first book processed has zero library context. It gets the worst treatment. If that first book is الكتاب by Sibawayhi (the foundational text of Arabic grammar), the most important book in the corpus gets the least contextual enrichment. By the 7,000th book, the library is rich enough to provide excellent context — but by then, most of the processing is done.

**Mitigation:** Process in chronological order by author death date. Earlier scholars (Sibawayhi d. 180 AH, al-Mubarrad d. 286 AH) are processed first. Since later scholars comment on earlier ones, processing in chronological order means each book's predecessors are already in the library. This is actually how traditional Islamic scholarship works — students study the foundational texts first.

**The "first book" problem is real but bounded.** After ~50 books covering the core texts of each science, the library context is rich enough that order matters less. The first 50 books should be manually selected to cover the foundational texts.

### Benefits

- **Cross-source enrichment:** The synthesis engine's job becomes easier. Instead of discovering cross-source connections from scratch, it can build on connections flagged during excerpting.
- **Earlier value delivery:** The owner can start reviewing entries after book 1, not after book 7,475. Scholarly review of the first 50 books informs processing of the next 50.
- **Error correction feedback loop:** If the owner finds an error in entry 23, the correction propagates to all subsequent processing. Batch processing discovers errors only after everything is done.
- **Scholar registry snowball:** Each processed book adds scholars to the registry. By book 500, the registry is comprehensive enough that author attribution becomes a lookup, not an LLM inference.

### Risks

- **Cascading errors:** An error in book 1 propagates to books 2-7,475. If Sibawayhi is misattributed to the Kufan school (a catastrophic but possible error), every subsequent book's school context is polluted.
- **Non-reproducibility:** Processing the same corpus in different orders produces different libraries. The current batch pipeline is order-independent.
- **Architectural complexity:** Every engine needs a library-read interface. The pipeline becomes stateful. Testing requires mock library states. Rollback after an error means undoing incremental state changes across the entire library.
- **Human gate bottleneck:** If each book triggers 2-3 human gates, and there are 7,475 books, the owner faces 15,000-22,000 review decisions. In batch mode, similar decisions can be grouped and reviewed in bulk.

### Verdict

| Dimension | Score |
|-----------|-------|
| Feasibility | 4/5 |
| Value | 4/5 |
| Effort | L (major refactor of engine interfaces) |
| Recommendation | **Adopt incrementally after batch pipeline is proven** |

This is the most promising alternative because it aligns with how scholarly knowledge actually accumulates. The key insight is that it does NOT replace the current pipeline — it enhances it with library-state context. The engines remain the same; they just receive additional context.

**Recommended adoption path:**
1. Finish the batch pipeline (current plan). This proves correctness.
2. Process the first 50 foundational books in batch mode.
3. Add a library-state reader to the excerpting engine's LLM prompt.
4. Process books 51-500 incrementally, with the library state enriching each run.
5. Owner reviews continuously, feeding corrections back into the pipeline.

**What KR would need to try this:**
- A "library state reader" module that extracts relevant context for a given topic
- A processing order algorithm (chronological by author death date, with manual overrides)
- Modified LLM prompts that include "here is what we already know about this topic"
- A rollback mechanism for library state changes
- Modified human gates that present similar decisions in batches

---

## Alternative 4: Multi-Modal Input (Vision Models on Page Images)

### The Idea

Instead of processing extracted HTML text from Shamela, process page images directly:
- Scan or screenshot each page
- Send to a vision model (GPT-5.4-vision, Gemini Pro Vision, Claude Opus vision)
- The model reads the Arabic text, identifies structural elements, detects layers, and extracts content
- Bypasses all HTML parsing, encoding, and extraction issues

### Feasibility Assessment

**Can vision models read dense Arabic scholarly pages?**

As of early 2026, the answer is "mostly yes, but with critical limitations":
- **Dense nastaliq/naskh script:** Vision models handle modern printed Arabic (Naskh typeface) reasonably well. Older printings with dense commentary margins (hashiyat) are harder. Manuscript facsimiles are very challenging.
- **Diacritics:** Vision models frequently miss or hallucinate diacritics. For nahw texts where diacritics ARE the analysis (i'rab), this is a fatal flaw.
- **Multi-layer layout:** A sharh page with matn in the center and hashiyah in the margins requires spatial understanding. Vision models can identify different text regions but struggle to maintain reading order across regions.
- **Footnotes and marginalia:** Vision models cannot reliably distinguish footnote numbers from text, especially in Arabic where footnote markers use Arabic-Indic numerals (١٢٣) that look like text.

**OCR error detection — the killer use case:** The real value is not replacing text extraction but validating it. Use vision to flag pages where the extracted HTML diverges from the page image:
- A page where Shamela's HTML has garbled text but the image shows clean text = OCR error
- A page where the image shows a table or diagram that the HTML missed = structural gap
- A page where the image shows interlinear text (e.g., Persian glosses) that the HTML merged = layer confusion

### Cost Analysis

- **Full vision processing:** At current pricing, processing a 1000-page book through vision costs approximately $10-30 (depending on resolution and model). For 7,475 books averaging ~500 pages, that is $37,000-$112,000. This is 1000x more expensive than the current pipeline (projected EUR ~1,000 total).
- **Selective vision (hybrid):** Flag 5% of pages as "ambiguous" by text-based heuristics (garbled characters, unusual Unicode, missing diacritics) and send only those to vision. Cost drops to $1,850-$5,600. Still expensive, but potentially worthwhile for quality.
- **Shamela already has clean text:** The Shamela library is a born-digital collection (texts were typed, not OCR'd). The normalization engine handles 7,475 books at 100% success rate. The text quality is high. Vision adds value primarily for non-Shamela sources (actual manuscript scans, poor-quality PDFs).

### Verdict

| Dimension | Score |
|-----------|-------|
| Feasibility | 3/5 |
| Value | 2/5 (for Shamela), 4/5 (for manuscripts) |
| Effort | M (hybrid validation layer) |
| Recommendation | **Prototype for non-Shamela sources only, reject for Shamela** |

The Shamela collection is born-digital with high text quality. Vision processing adds cost without proportional quality gain. However, when KR expands beyond Shamela to manuscript PDFs, poor scans, and non-standard digital editions, vision becomes essential. Build the capability now as an optional validation layer, activate it later for non-Shamela sources.

**What KR would need to try this:**
- A page-image source for test fixtures (screenshot Shamela pages or use manuscript scans)
- Benchmark vision model diacritic accuracy on 50 scholarly pages
- A "text vs. image comparison" module that flags divergences
- Budget allocation for vision processing of flagged pages only

---

## Alternative 5: Collaborative Scholarly Platform

### The Idea

Open the pipeline and library to other Islamic scholars:
- Each scholar adds books from their specialization
- Scholarly review replaces or supplements automated consensus
- Wikipedia-style editing with credentials (ijazah verification, institutional affiliation)
- Distributed expertise covers more sciences than any single owner

### Platform Comparison

**Existing scholarly platforms:**
- **Usul.ai** — Islamic scholarly search engine. Already indexes many of the same texts KR processes. Focused on search, not structured teaching units. No collaborative editing.
- **al-Maktaba al-Shamela** — the source collection itself. Read-only, no scholarly annotation layer.
- **Stanford Encyclopedia of Philosophy (SEP)** — commissioned expert articles, not collaborative editing. High quality, very slow publication cycle.
- **PhilPapers** — crowd-sourced classification of philosophy papers. Relevant model for taxonomy, but papers are much simpler objects than Islamic scholarly texts with multi-layer commentary traditions.
- **Wikipedia Arabic** — open editing, but quality varies wildly for specialized scholarly content. No credential system.

### Why This Conflicts with KR's Design

KR's fundamental design principle: "The library IS the user's knowledge. An error here is an error in his mind." This is a deeply personal statement. The library is not a public resource — it is one person's scholarly understanding.

A collaborative platform replaces one person's curated knowledge with consensus of many. This changes the nature of the product:
- The owner's school preferences (which scholarly positions to highlight) are diluted by other scholars' preferences
- Quality varies by contributor — a nahw expert's contributions are excellent, but their fiqh contributions might be mediocre
- Scholarly disagreements become editorial conflicts (the Ash'ari vs Athari aqidah debate, for instance, has real-world tension)
- The owner loses the "this is MY library reflecting MY understanding" quality

### Where Collaboration COULD Work

- **Expert review of LLM outputs:** Instead of multi-model consensus, send excerpts to domain experts for review. An isnad specialist reviews hadith classification; a nahw specialist reviews grammar excerpts. This is labor-intensive but produces ground truth that improves the pipeline for everyone.
- **Scholar registry curation:** A shared database of scholar identities (canonical names, death dates, school affiliations, teacher-student chains). This is factual, not interpretive, so scholarly disagreement is minimal. Something like Wikidata for Islamic scholars.
- **Taxonomy tree review:** Expert validation of the science tree structure. Is the nahw tree correctly organized? Do the leaf nodes represent real teachable topics? This requires expert knowledge that no LLM can replace.

### Verdict

| Dimension | Score |
|-----------|-------|
| Feasibility | 2/5 |
| Value | 3/5 (for shared infrastructure), 1/5 (for replacing KR) |
| Effort | XL (platform engineering + community building) |
| Recommendation | **Reject as replacement; research shared infrastructure (scholar registry, taxonomy review)** |

KR is a personal scholarly library, not a collaborative platform. The design is fundamentally single-user. However, specific infrastructure components (scholar registry, taxonomy tree) could benefit from expert curation. These are candidates for shared open-source resources that KR consumes but does not host.

**What KR would need to try this:**
- Nothing, for the core pipeline. The pipeline remains personal.
- For shared infrastructure: contribute the scholar registry as an open dataset, invite expert validation.
- For expert review: identify 3-5 domain specialists willing to review LLM outputs for specific sciences.

---

## Alternative 6: Autonomous Agents Instead of Fixed Pipeline

### The Idea

Replace the 5-engine linear pipeline with autonomous agents:
- An **analyst agent** reads a book and decides what processing it needs (is this a simple matn? a multi-layer commentary? a hadith collection with isnads?)
- A **librarian agent** examines each excerpt and decides where it belongs in the taxonomy, creating new nodes if needed
- A **reviewer agent** checks quality, flags issues, and decides whether to accept, revise, or escalate to human review
- A **researcher agent** gathers cross-source context for synthesis

Different books get different treatment. A simple risalah (treatise) on one topic might skip multi-layer processing entirely. A massive commentary with marginalia might get extra processing passes. The agents decide.

### Why This Is Tempting

The current pipeline treats all books identically. A 20-page risalah on a single topic goes through the same 5 engines as a 30-volume encyclopedia covering every Islamic science. The overhead is disproportionate for simple books and potentially insufficient for complex ones.

Real-world processing actually IS adaptive:
- The architecture decision already merged 3 engines into 1 (passaging + atomization into excerpting) because most divisions did not need the intermediate steps
- The source engine's consensus mechanism already adapts (disagreement triggers escalation to a third model)
- The human gate system already provides adaptive quality control (only flagged items go to human review)

Agents would make this adaptiveness explicit and general-purpose.

### Why This Is Dangerous for KR

**Non-determinism:** The analyst agent might classify the same book differently on two runs. The librarian agent might place the same excerpt differently. The reviewer agent might accept what it rejected yesterday. This violates KR's reproducibility requirement.

**Testing impossibility:** How do you write a test for "the analyst agent correctly decides that this book needs multi-layer processing"? The decision space is too large. The current pipeline is testable because each engine has a fixed contract: NormalizedPackage in, ExcerptRecords out. An agent's behavior depends on what it notices in the text, which is unbounded.

**Debugging opacity:** When an excerpt has a wrong attribution, the current pipeline lets you trace: Phase 3 enrichment call returned wrong author -> Phase 3 consensus disagreed -> human gate was not triggered because confidence was 0.87 (above threshold). With agents, the trace is: the reviewer agent decided the attribution was correct. Why? Because it "read" the text and "decided." The reasoning is opaque.

**The KR project has 1,660+ tests.** These tests verify specific behavioral rules from SPECs. An agent-based system has no SPECs — the agent IS the spec. This eliminates the entire quality assurance framework that KR has built.

### The Hybrid Opportunity

Agents for orchestration, pipeline for execution:
- An orchestrator agent examines each book and selects a processing profile (simple, standard, complex, multi-layer)
- Each profile maps to a specific pipeline configuration (which engines, which parameters, which LLM models)
- The engines themselves remain deterministic and testable
- The agent's decision is logged and reviewable; the processing is reproducible given the same profile

This already exists in embryonic form: the excerpting engine's Phase 1 handles tiny divisions differently from oversized ones (merge vs. split). The agent just elevates this to the book level.

### Verdict

| Dimension | Score |
|-----------|-------|
| Feasibility | 3/5 |
| Value | 3/5 (for orchestration), 1/5 (for replacing pipeline) |
| Effort | XL (full orchestrator), M (profile-based routing) |
| Recommendation | **Adopt orchestration layer with fixed profiles; reject autonomous processing** |

The insight is correct — not all books need the same treatment. But the implementation should be a routing layer that selects from tested, fixed pipelines, not autonomous agents that make ad-hoc decisions. Every possible processing path must be tested. The number of paths should be small (3-5 profiles, not unlimited agent discretion).

**What KR would need to try this:**
- Define 3-5 book processing profiles (simple_matn, standard_prose, multi_layer_commentary, hadith_collection, versified_text)
- Map each profile to specific engine configurations (skip Phase 2a for simple matn, add layer separation for multi-layer, etc.)
- Build a profile classifier (could be a simple rule-based system using source engine metadata: genre + structural_format + multi_layer flag)
- Each profile must have its own test suite covering profile-specific edge cases

---

## Summary Matrix

| Alternative | Feasibility | Value | Effort | Recommendation |
|------------|:-----------:|:-----:|:------:|----------------|
| 1. RAG | 2 | 2 | M | Research as complement; reject as replacement |
| 2. Fine-tuned models | 3 | 2 | L | Prototype for binary tasks; reject for scholarly judgments |
| 3. Incremental pipeline | 4 | 4 | L | **Adopt after batch pipeline is proven** |
| 4. Multi-modal vision | 3 | 2-4 | M | Prototype for non-Shamela sources only |
| 5. Collaborative platform | 2 | 1-3 | XL | Reject as replacement; research shared infrastructure |
| 6. Autonomous agents | 3 | 1-3 | M-XL | Adopt orchestration layer; reject autonomous processing |

## Top Recommendations (Prioritized)

### Priority 1: Incremental Processing (Alternative 3)

**Why:** Highest value, most aligned with KR's existing design. Does not replace the pipeline; enhances it with library-state context. The scholarly tradition itself is incremental — later scholars build on earlier ones. Processing in chronological order mirrors how knowledge actually accumulates.

**When:** After the batch pipeline is proven correct (post-excerpting, post-taxonomy).

**First step:** Add a "library context reader" to the excerpting engine that passes existing excerpts on the same topic to the LLM prompt.

### Priority 2: Book Processing Profiles (Alternative 6, hybrid)

**Why:** The pipeline already handles different structural formats differently. Formalizing this into named profiles with dedicated test suites reduces wasted processing on simple books and enables better treatment of complex ones.

**When:** During taxonomy or synthesis engine design, when the processing paths naturally diverge.

**First step:** Analyze the 274 source-engine-processed books to identify natural clusters by genre + format + layer count. See if 3-5 profiles cover 95% of cases.

### Priority 3: RAG as Complementary Access Layer (Alternative 1)

**Why:** Exploratory search across 7,475 books is genuinely useful and not served by the structured library. A student might ask "who discusses the definition of qiyas?" across the entire corpus — this is a retrieval task, not a structured-entry task.

**When:** After synthesis produces the first 100+ entries, so the structured library provides the quality baseline and RAG provides the exploratory layer.

**First step:** Benchmark 3 Arabic embedding models on KR fixture texts, measuring semantic similarity for known-related passages.

### Not Now: Fine-tuning, Vision, Collaboration

These either conflict with KR's accuracy-first design (fine-tuning replaces consensus with single-model inference), address problems KR does not currently have (vision for born-digital Shamela text), or require community infrastructure beyond a single-user project (collaboration platform). They remain research topics for when KR's core pipeline is complete and the first 500+ books are processed.

---

## Conclusion

None of these alternatives replace the current pipeline architecture. The pipeline's design — sequential engines with typed contracts, multi-model consensus, human gates, and metadata flow — exists for a reason: it makes errors visible, traceable, and correctable. The alternatives that are most valuable (incremental processing, book profiles, RAG search) are enhancements that layer on top of a working pipeline, not replacements for it.

The strongest signal from this analysis: **the current architecture is well-suited to its problem.** Arabic scholarly text processing with knowledge-integrity guarantees genuinely requires the structured, testable, metadata-rich approach that KR has built. The alternatives that would simplify the architecture (RAG, fine-tuning, agents) do so by sacrificing properties that the project explicitly values above all else — correctness, traceability, and scholarly attribution.

The most productive investment of innovation energy is not rearchitecting, but enriching: give the pipeline more context (incremental processing), more adaptiveness (profiles), and more access patterns (RAG as complement).
