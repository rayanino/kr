# خزانة ريان — External Resources Catalog

**Last surveyed:** 2026-03-06 (Creative session — KITAB text reuse data, passim, eScriptorium/Kraken, NetworkX)

This file maps known external tools, libraries, and services to KR engines. Every engine SPEC should consider whether existing tools can handle part of the work before designing custom solutions.

**Principle:** Build on existing tools wherever possible. Custom code is a last resort. If a library handles 80% of the job, use it and write custom code for the remaining 20%.

## Technology Survey Update (2026-03-06, Creative Session)

**KITAB Text Reuse Statistics** — Pre-computed pairwise text reuse data for the entire OpenITI corpus (~4,300+ Arabic texts). Generated using the passim algorithm (Smith-Waterman alignment on 300-word chunks). Available on Zenodo (DOI: 10.5281/zenodo.4362369, latest release matches OpenITI corpus version). Bidirectional statistics files are ~1GB. Each record documents: book pair, shared word count, percentage overlap, milestone positions. **KR use: §4.B.5 (Source Compositional Profiling)** — query this dataset at intake to instantly reveal a source's place in the intertextual network of classical Arabic scholarship. Download: `https://kitab-project.org/data/download`. License: CC-BY-NC-SA 4.0 (academic/non-commercial).

**passim** — Open-source text reuse detection algorithm by David Smith (Northeastern). Uses locality-sensitive hashing for candidate detection + Smith-Waterman for alignment. Python interface available in development branch. GitHub: `https://github.com/dasmiq/passim`. Originally designed for newspaper corpora, adapted by KITAB for Arabic with specialized parameters (300-word chunks, Arabic-optimized). **KR use: §4.B.6 (Edition Comparison)** could use passim's approach for large-edition alignment as fallback when structural alignment fails. License: Apache 2.0.

**eScriptorium + Kraken** — Leading open-source OCR/HTR platform for Arabic manuscripts. Kraken (Python, Apache 2.0) is the engine; eScriptorium is the web interface. Arabic models available: `04-01-2021_ArabPersGeneralized.mlmodel` (KITAB's production model). BADAM dataset for baseline detection in Arabic manuscripts. GitHub: `https://github.com/mittagessen/kraken`. **KR use:** Could complement QARI-OCR for handwritten manuscript recognition (eScriptorium excels at HTR with custom training). Not needed for printed text (QARI-OCR is better for that).

**NetworkX** — Python graph library (BSD, v3.2+). Provides: shortest path, betweenness centrality, Louvain community detection, graph visualization. `pip install networkx`. **KR use: §4.B.7 (Scholarly Genealogy)** — computes centrality scores, scholarly communities, and generation numbers in the teacher-student network. Zero external dependencies for core algorithms.

## Technology Survey Update (2026-03-06, Hardening Round)

**QARI-OCR** — NEW. Open-source SOTA for Arabic OCR with diacritics. Based on Qwen2-VL-2B-Instruct, fine-tuned on specialized Arabic datasets. CER 0.061, WER 0.160, BLEU 0.737 on diacritized texts. Available on HuggingFace (`riotu-lab/QARI-OCR`). Handles: tashkeel, diverse fonts, document layouts, low-resolution images, handwritten text (v0.3). Use 8-bit quantization (NOT 4-bit) for OCR tasks. Paper: arXiv:2506.02295. **This should be evaluated as primary OCR for KR alongside Mistral OCR** — it's specifically optimized for diacritized Arabic scholarly text, which is KR's exact use case.

## Technology Survey Update (2026-03-06, Session 9)

Key findings from web research:

**Docling** — Production-stable v2.66+ (Jan 2026). Now under LF AI & Data Foundation (MIT license). Handles PDF, DOCX, PPTX, XLSX, HTML, images, audio/video. Granite-Docling-258M VLM model adds end-to-end document understanding. Arabic support is **experimental** — English is primary target. The Heron layout model (Dec 2025) improves PDF parsing speed. MCP server integration available. `pip install docling` — Python 3.10+.

**CAMeL Tools** — v1.5.2, actively maintained. Python 3.8-3.12. Widely used in ArabicNLP 2025 conference papers. Provides morphological analysis, dediacritization, tokenization, NER, dialect ID. Requires Rust compiler and CMake for installation.

**Arabic Embeddings** — Swan models (NYUAD/Omartificial) now outperform Multilingual-E5-large for Arabic tasks. Swan-Large achieves SOTA on ArabicMTEB. For KR: recommend **Swan-Large** for semantic search, or **Arabic-STS-Matryoshka** (score 83.16 on STS17) for efficient retrieval with Matryoshka dimensionality reduction. The SPEC's "arabic-e5-base or GTE-multilingual-base" are reasonable fallbacks.

**OpenITI** — Latest release Dec 2025 on Zenodo. Python package v0.1.6 (Nov 2025, `pip install openiti`). The metadata CSV at kitab-corpus-metadata.azurewebsites.net is the key resource for scholar authority bootstrapping (§4.B.1). CTS-compliant URIs encode author death dates (e.g., `0505Ghazali.IhyaCulumDin`). Over 7,000 texts integrated, 40,000+ raw texts available.

## Technology Survey Update (2026-03-06, Creative Session — Normalization Engine)

Key findings from web research on Arabic document processing and OCR landscape:

**Baseer** (Misraj AI, 2025) — Arabic-specific VLM for document-to-Markdown OCR. Based on Qwen2.5-VL-3B-Instruct, fine-tuned on 500K Arabic document-text pairs (300K synthetic + 200K real-world). WER 0.25 on Misraj-DocOCR benchmark (SOTA). Best TEDS score (56) and MARS score (68.13) for structural fidelity — tables, footnotes, column layouts. Launched commercially at AWS re:Invent 2025. Paper: arXiv:2509.18174. Open weights on HuggingFace: `Misraj/Baseer`. **KR use: §4.B.6 (Adaptive OCR Orchestration)** — best engine for multi-column Arabic layouts and structural document parsing. Complements QARI-OCR (better for diacritics) and PaddleOCR-VL (better for speed).

**PaddleOCR-VL 1.5** (Baidu, 2025) — Ultra-compact (0.9B params) VLM for multilingual document parsing. 109 languages including Arabic. Two-stage pipeline: PP-DocLayoutV2 for layout analysis + PaddleOCR-VL-0.9B for element recognition. 94.5% on OmniDocBench v1.5 (SOTA). Supports skewed, warped, scanned documents. Apache 2.0, local deployment. `pip install paddlepaddle-gpu && pip install -U "paddleocr[doc-parser]"`. **KR use: §4.B.6** — fast, cheap first-pass OCR for clean pages; PP-DocLayoutV2 as layout pre-analyzer for all pages before engine selection. Warning: Flash Attention 2 required for reasonable VRAM on Arabic pages (otherwise 40GB+ for a single page).

**Granite-Docling-258M** (IBM, Sep 2025) — 258M parameter VLM for end-to-end document conversion. Uses DocTags (IBM structural markup). Experimental Arabic support. Apache 2.0. Successor to SmolDocling. Integrated into Docling library. **KR use:** Potential lightweight alternative for simple Arabic document parsing, but Arabic support is still early-stage — monitor progress. Not recommended as primary for KR's scholarly Arabic texts.

**KITAB-Bench** (MBZUAI, ACL 2025) — Comprehensive Arabic OCR benchmark: 9 domains, 36 sub-domains, 8,809 samples. Tasks: OCR, layout detection, line recognition, table recognition, PDF-to-Markdown, chart extraction, VQA. Introduces MARS (Markdown Recognition Score), TEDS (Table Edit Distance), SCRM (Chart Extraction) metrics. Paper: arXiv:2502.14949. **KR use:** Benchmark for evaluating normalization engine OCR quality against standard Arabic documents.

**ArabiDoc** (ICLR 2026 submission) — Holistic Arabic-English evaluation benchmark for full-page document parsing. Covers text, tables, charts, and reading order jointly. Fills gap left by KITAB-Bench (which is task-specific, not end-to-end). **KR use:** When evaluating normalization engine end-to-end quality across mixed Arabic/English content.

**SARD** (2025) — Synthetic Arabic OCR dataset: 843,622 document images, 690M words, 10 Arabic fonts. Designed for book-style Arabic text recognition training. Paper: arXiv:2505.24600. **KR use:** Potential fine-tuning data if KR needs to train a domain-specific OCR model for classical Islamic scholarly texts.

---

## Document Processing

### Docling (IBM, open source)
- **URL:** https://github.com/docling-project/docling
- **What it does:** Converts PDF, DOCX, PPTX, XLSX, HTML, images, audio → structured JSON/Markdown. Advanced PDF understanding: layout, reading order, tables, formulas, code. Arabic support via OCR. 258M parameter VLM model (Granite-Docling).
- **Relevant engines:** Normalization engine (non-Shamela sources)
- **How to use:** `pip install docling`. The normalization engine for PDFs/DOCX should use Docling as its backend rather than building custom document parsing. Docling's `DoclingDocument` format could be the intermediate representation before KR's own normalization.
- **License:** Apache 2.0

---

## Shamela Integration

### shamela2epub (yshalsager)
- **URL:** https://github.com/yshalsager/shamela2epub
- **What it does:** Downloads books from shamela.ws and converts to EPUB format.
- **Relevant engines:** Source engine (automated discovery/acquisition from Shamela web)
- **How to use:** Could automate source acquisition from Shamela's online library beyond the desktop app's .bok format.
- **License:** Check repo

### shamela (ragaeeb) — NodeJS
- **URL:** https://github.com/ragaeeb/shamela
- **What it does:** Full Shamela v4 API client. Fetches metadata, downloads databases, queries in-memory. Content processing: HTML→Markdown, Arabic numeral cleanup, content sanitization.
- **Relevant engines:** Source engine (metadata extraction), Normalization engine (content processing algorithms)
- **How to use:** Reference for content processing algorithms even though it's NodeJS. The HTML→Markdown conversion and Shamela-specific sanitization patterns are directly transferable.
- **License:** Check repo

## Arabic NLP

### CAMeL Tools (NYU Abu Dhabi)
- **URL:** https://github.com/CAMeL-Lab/camel_tools
- **What it does:** Comprehensive Arabic NLP toolkit: morphological analysis, disambiguation, dialect identification, Named Entity Recognition, sentiment analysis, tokenization, transliteration, text normalization (Alef/Teh Marbuta/diacritics), dediacritization.
- **Relevant engines:** Normalization engine (Arabic text normalization, dediacritization), Excerpting engine (morphological analysis for text understanding), Taxonomy engine (NER for author/scholar identification)
- **How to use:** `pip install camel-tools` then `camel_data -i defaults`. The normalization engine should use CAMeL's text normalization utilities rather than implementing Arabic-specific rules from scratch. The excerpting engine may benefit from morphological analysis for understanding Arabic text structure.
- **License:** MIT

### awesome-arabic-nlp (curated list)
- **URL:** https://github.com/Curated-Awesome-Lists/awesome-arabic-nlp
- **What it does:** Curated collection of Arabic NLP resources, tools, datasets, and papers.
- **Relevant to:** Resource survey for any engine working with Arabic text. Check this list before building any Arabic text processing.

---

## OCR / Image-to-Text (for scanned/photographed books)

Owner confirmed: some books exist only in physical form (e.g., editions from bookstores like صفة الصفوة). Scans/photographs of pages are a primary acquisition path from day one. Arabic OCR is critical infrastructure for the normalization engine.

### Tesseract (Google, open source)
- **URL:** https://github.com/tesseract-ocr/tesseract
- **What it does:** General-purpose OCR engine. Arabic support via trained data (ara.traineddata). Works on printed text; struggles with manuscripts, poor scans, and mixed diacritics.
- **Relevant engines:** Normalization engine (image→text for scan-based sources)
- **How to use:** `apt install tesseract-ocr tesseract-ocr-ara`. Good baseline but likely insufficient alone for scholarly Arabic texts.
- **License:** Apache 2.0

### Kraken (open source)
- **URL:** https://github.com/mittagessen/kraken
- **What it does:** OCR engine specifically designed for historical and non-Latin scripts. Better than Tesseract for Arabic manuscripts and older prints. Trainable on custom datasets.
- **Relevant engines:** Normalization engine (higher-quality Arabic OCR)
- **How to use:** `pip install kraken`. May need custom training on scholarly Arabic fonts.
- **License:** Apache 2.0

### Mistral OCR 3 (Mistral AI, commercial API)
- **URL:** https://mistral.ai/solutions/document-ai / https://docs.mistral.ai/capabilities/document_ai
- **What it does:** State-of-the-art document understanding API. Extracts text + embedded images from PDFs and images into Markdown with HTML table reconstruction. Multilingual with strong Arabic support. Processes up to 2000 pages/minute. Handles complex layouts, handwriting, forms, scanned docs. Cost: $2/1000 pages ($1/1000 with batch).
- **Relevant engines:** Normalization engine (PRIMARY OCR for scanned PDFs and images)
- **How to use:** `pip install mistralai`. API endpoint: `client.ocr.process(model="mistral-ocr-latest", ...)`. Supports document_url (public URL), base64, or uploaded files. Returns per-page text in Markdown + extracted images.
- **License:** Commercial API (pay per page). Owner has infinite budget.
- **Arabic quality:** Outperforms most alternatives including Google Document AI on multilingual benchmarks. Arabic is explicitly supported with 99%+ fuzzy match scores in benchmark testing.

### Qari-OCR (open-source, Arabic-specialized)
- **URL:** https://arxiv.org/abs/2506.02295 / HuggingFace models
- **What it does:** Vision-language model (based on Qwen2-VL-2B) specifically fine-tuned for Arabic OCR. New open-source SOTA: CER 0.061, WER 0.160 on diacritically-rich texts. Superior handling of tashkeel, diverse fonts, and document layouts. v0.3 shows potential for structural document understanding and handwritten text.
- **Relevant engines:** Normalization engine (specialized Arabic OCR, especially for diacritics-heavy scholarly texts)
- **How to use:** Download from HuggingFace. Runs locally on GPU (NVIDIA A6000-class). Smaller model (2B params) so can run alongside other processes.
- **License:** Open-source (check repo)
- **Key advantage:** Specifically trained on synthetic data rich in diacritics and typographic variations — exactly what KR's scholarly Arabic sources contain. Best open-source option for diacritics preservation.

### Google Document AI / Cloud Vision
- **URL:** https://cloud.google.com/document-ai
- **What it does:** Commercial OCR with strong Arabic support. Layout understanding, table detection.
- **Relevant engines:** Normalization engine (fallback OCR option)
- **How to use:** API key required. Cost per page. Owner has stated infinite tool/API budget.
- **License:** Commercial (pay per use)

### Docling (IBM, noted above)
- Also handles images→text with Arabic OCR via its VLM model (Granite-Docling-258M). Early-stage Arabic support. Better suited as PDF structure extraction tool than as primary OCR for Arabic scholarly texts. Layout analysis (DocLayNet) and table structure (TableFormer) are mature. MCP server available for agent integration.

---

## LLM Orchestration

### DSPy (Stanford / Databricks)
- **URL:** https://dspy.ai / https://github.com/stanfordnlp/dspy
- **What it does:** Declarative framework for building LLM pipelines as code, not prompts. Define input/output signatures, compose modules, evaluate with metrics, auto-optimize prompts. Uses LiteLLM for provider routing. Supports structured outputs (JSON, Pydantic).
- **Relevant engines:** Consensus engine (multi-model orchestration), all engines with LLM calls (structured output extraction, prompt optimization)
- **How to use:** `pip install dspy`. The consensus engine could use DSPy signatures to define extraction tasks declaratively, with auto-optimization against gold baselines. Instead of hand-crafting extraction prompts, define what the output should look like and let DSPy optimize how to get it.
- **License:** MIT

---

### OpenRouter
- **URL:** https://openrouter.ai
- **What it does:** Single API gateway to 200+ LLM models (OpenAI, Anthropic, Google, Meta, Mistral, etc.). Unified API format. Automatic fallback. Cost tracking.
- **Relevant engines:** Consensus engine (multi-model consensus), all engines using LLM calls
- **How to use:** Instead of managing separate API keys for each provider, route all LLM calls through OpenRouter. Consensus engine can request responses from different models through one API. Simplifies provider strategy from "which APIs to integrate" to "which models to request."
- **API key:** Available (owner provides)

### Anthropic API (direct)
- **URL:** https://api.anthropic.com
- **What it does:** Direct access to Claude models.
- **Relevant engines:** Consensus engine, all engines with LLM calls
- **API key:** Available (owner provides)

### OpenAI API (direct)
- **URL:** https://api.openai.com
- **What it does:** Direct access to GPT models.
- **Relevant engines:** Consensus engine (second model for multi-model agreement)
- **API key:** Available (owner provides)

---

## AI Agent Infrastructure

### mem0
- **URL:** https://github.com/mem0ai/mem0
- **What it does:** Persistent memory layer for LLM applications. Stores/retrieves user interactions across sessions. Hybrid datastore (graph + vector + key-value). Sub-50ms retrieval. Reduces token usage ~90% vs full-context approaches.
- **Relevant to:** Claude Code build phase (cross-session memory), potentially the application itself (human gate memory, owner preference tracking)
- **How to use:** `pip install mem0ai`. Could be integrated into Claude Code's workflow for maintaining state across build sessions. For the application: could power the owner's interaction history with the library.
- **License:** Apache 2.0

---

## Evaluation & Quality

### Terminal Bench (Factory AI)
- **URL:** https://factory.ai/news/terminal-bench
- **What it does:** Benchmarks for AI coding agents. Tests how well AI handles real-world terminal/coding tasks.
- **Relevant to:** Phase 5 (build infrastructure planning) — evaluating Claude Code's capabilities, designing test strategies

### 100x.bot
- **URL:** https://100x.bot
- **What it does:** AI development productivity tools.
- **Relevant to:** Phase 5 (build infrastructure planning) — potential tooling for Claude Code workflows

---

## Islamic Scholarly Corpora & APIs

### OpenITI — Open Islamicate Texts Initiative
- **URL:** https://github.com/OpenITI
- **What it does:** The largest machine-actionable corpus of premodern Islamicate texts. 10,000+ texts organized using CTS-compliant URIs encoding author death date and author/work slugs (e.g., `0505Ghazali.IhyaCulumDin`). Metadata CSV available (~50MB) with author death dates, work titles, and corpus statistics. Texts organized by 25-year AH periods.
- **Relevant engines:** Source engine (§4.B.1 — scholar authority bootstrapping via metadata CSV lookup), Normalization engine (potential secondary text source for comparison)
- **How to use:** Download metadata CSV from GitHub releases. Query locally during intake to enrich scholar authority records with confirmed death dates, known works lists, and CTS URIs. No API — purely offline after initial download. Update quarterly to match OpenITI's release cycle.
- **License:** Various (primarily open access scholarly corpus)

### KITAB Project (Aga Khan University)
- **URL:** https://kitab-project.org
- **What it does:** Text reuse detection in Arabic literary tradition using passim algorithm (300-word chunks, Smith-Waterman alignment). Discovers how texts borrow from, cite, or plagiarize each other across the OpenITI corpus.
- **Relevant engines:** Source engine (edition comparison — detecting how different editions of the same work differ), Excerpting engine (implicit reference detection — finding when an author quotes another without attribution)
- **How to use:** KITAB's methodology and published data on text reuse pairs could inform citation network discovery. Their passim algorithm parameters are calibrated for Arabic scholarly text.
- **License:** Open research project

### sunnah.com API
- **URL:** https://sunnah.com/api (requires API key from sunnah.com)
- **What it does:** Structured hadith data from all major collections (Bukhari, Muslim, Abu Dawud, etc.) with English/Arabic text, hadith grading, chapter organization, and standard numbering.
- **Relevant engines:** Source engine (special source type: hadith collections — standard numbering capture), Excerpting engine (hadith reference resolution)
- **How to use:** Request API key. Query by collection + hadith number. Use as canonical hadith text source rather than OCR.
- **License:** Check sunnah.com terms

### hadith-json (GitHub community)
- **URL:** https://github.com/topics/hadith (multiple repos)
- **What it does:** 50K+ hadiths from 17 books in structured JSON format. Multiple implementations available.
- **Relevant engines:** Source engine (bulk hadith data for special source type handling)
- **How to use:** Static JSON files, no API needed. Use as fallback if sunnah.com API is unavailable.
- **License:** Various

## Resources to Survey (search before building each engine)

When writing each engine SPEC, the architect must search the web for existing tools. Minimum 3-5 searches per engine. Here are starting points:

**Source engine:**
- Arabic OCR tools, Shamela API alternatives, Islamic text databases
- Hadith databases with APIs (sunnah.com API, hadithapi.com)
- Islamic library APIs (quran.com, islamqa.info)
- Wikidata/DBpedia Islamic scholar data for enrichment

**Normalization engine:**
- Docling (already cataloged — primary tool for non-Shamela sources)
- Arabic text segmentation and sentence boundary detection
- CAMeL Tools normalization (already cataloged)
- PyArabic, arabicnlp, Farasa for Arabic text processing

**Passaging engine:**
- Text chunking libraries (semantic chunking, recursive splitters)
- LangChain text splitters, LlamaIndex node parsers
- Arabic-aware sentence tokenizers

**Atomization engine:**
- Semantic segmentation tools
- Topic segmentation for Arabic text

**Excerpting engine:**
- DSPy (already cataloged — structured extraction)
- Instructor library (structured LLM output with Pydantic)
- Outlines (structured generation)

**Taxonomy engine:**
- Knowledge graph tools (NetworkX, RDFLib)
- Taxonomy/ontology management libraries
- Topic modeling (BERTopic with Arabic support)
- Wikidata SPARQL for Islamic science classification

**Synthesis engine:**
- Instructor (structured LLM output, Pydantic-based schema enforcement — already cataloged)
- DSPy (pipeline orchestration, prompt optimization against gold baselines — already cataloged)
- LiteLLM (multi-provider routing for consensus — already cataloged)
- NetworkX (graph traversal for teacher-student chain discovery — already cataloged for taxonomy)
- Multi-LLM Text Summarization (Fang et al., 2025 RANLP): centralized and decentralized multi-LLM strategies for synthesis; 3x improvement over single-LLM baselines. Relevant for consensus-based entry generation.
- Attr-First (Slobodkin et al., 2024): decomposed generation — content selection → attribution → generation. Relevant for factual layer construction where claims must be traced to specific excerpts before generation.
- FRONT framework (fine-grained grounded citations): trains LLMs to anchor in supporting quotes before generating attributed answers. 14.21% improvement over baselines on ALCE benchmark. Architecture relevant for KR's citation-grounded factual layer.
- ContraDoc (Li et al., 2024 NAACL): self-contradiction detection in long documents. GPT-4 struggles with subtle internal inconsistencies. Relevant for intra-author contradiction detection in synthesis.
- ContraGen/LegalWiz (2025): multi-agent contradiction detection framework with hybrid NLI + LLM approach and confidence-weighted scoring. Architecture applicable to KR's cross-excerpt contradiction detection.
- DiverseSumm (Huang et al., 2024 NAACL): benchmark showing GPT-4 covers only ~40% of diverse information in multi-document summarization. Validates KR's need for explicit position tracking rather than relying on LLM to implicitly capture all positions.
- Hallucination in MDS (Belem et al., 2025): up to 75% of LLM-generated multi-document summary content is hallucinated; hallucinations increase toward end of summaries. Validates KR's citation-completeness integrity check and anti-hallucination verification approach.

**Consensus component:**
- OpenRouter (already cataloged — multi-model gateway)
- DSPy (already cataloged — pipeline orchestration)
- LiteLLM (already cataloged — provider routing, used as direct SDK for consensus)
- Instructor (already cataloged — structured output extraction with Pydantic)

## Consensus Component Resources (added 2026-03-06)

### LiteLLM as Consensus Provider Layer
- **Role in consensus:** Primary provider abstraction. All consensus LLM calls go through `litellm.acompletion()` for async parallel dispatch. Provides unified API across Anthropic, OpenAI, Google, and 100+ other providers. Handles authentication, retries, cost tracking per call.
- **Key capability for consensus:** Router with retry/fallback logic across multiple deployments. Supports `max_parallel_requests` semaphore for rate limiting. 8ms P95 latency overhead at 1k RPS.
- **Decision:** Use LiteLLM Python SDK directly (not proxy server) — the consensus component is a shared library, not a standalone service. No operational overhead of running a proxy.

### Instructor as Structured Output Layer
- **Role in consensus:** Enforces Pydantic schema on every model response. Automatic retries on schema validation failure. Works on top of LiteLLM via `instructor.from_litellm()`.
- **Key capability for consensus:** Schema violations trigger automatic retry with error feedback to the model, up to configurable limit. This handles the primary failure mode of multi-model structured output: different models may need different numbers of attempts to produce schema-conformant responses.

### Multi-LLM Consensus Research (2024-2025)
- **CONSENSAGENT (ACL 2025):** Framework that dynamically refines prompts to mitigate sycophancy in multi-agent debate — agents reinforcing each other's responses instead of critically evaluating. KR's consensus design avoids this by using independent (non-deliberative) evaluation: models never see each other's responses. The sycophancy risk applies to debate-style consensus, not to KR's parallel-independent-comparison approach.
- **Multi-LLM Consensus for Cell Annotation (bioRxiv 2025):** Iterative multi-LLM consensus framework achieving 15% accuracy improvement over single-model. Uses cross-model deliberation to quantify uncertainty and identify ambiguous cases for expert review. Validates KR's approach of using disagreement as a signal for human gate escalation.
- **Multi-LLM Consensus Survey (MDPI 2025):** Categorizes consensus into prompt-level, reasoning-to-detection, box-level, and hybrid approaches. KR's approach is "box-level" (compare independent structured outputs) — the simplest and most robust form, avoiding the complexity of reasoning-level consensus.

---

## Possibility Research Starting Points

These are NOT tools to use — they are projects and domains to study for inspiration about what's technologically feasible. The goal is to discover capabilities that can be designed into KR's engines.

**Digital Humanities / Textual Traditions:**
- Perseus Digital Library (Tufts) — Greek/Latin corpus with morphological analysis, citation linking
- CBDB (China Biographical Database, Harvard) — prosopographical database linking 470K historical figures
- OpenITI (Open Islamicate Texts Initiative) — 10K+ Islamicate texts with computational analysis
- Kitab Project (Aga Khan University) — text reuse detection in Arabic literary tradition
- al-Maqrizi (French CNRS) — semantic annotation of medieval Arabic texts
- Search "computational islamicate studies" for latest academic work

**Arabic AI/ML State of the Art:**
- AceGPT, Jais, ALLaM — Arabic-specific LLMs (what can they do that general LLMs can't?)
- Arabic BERT variants (AraBERT, MARBERT, CAMeLBERT) — what NLU tasks are solved?
- Arabic OCR: Tesseract Arabic, Google Document AI, Kraken — where are the limits?
- Arabic handwriting recognition — can medieval manuscripts be digitized?
- Arabic speech-to-text — can scholarly lectures be transcribed and ingested?

**Knowledge Graph / Semantic Web:**
- Wikidata's approach to scholarly/biographical data
- Neo4j, ArangoDB for scholarly network graphs
- RDF/SPARQL for Islamic scholarly ontologies
- How do citation analysis tools (Semantic Scholar, OpenAlex) work?

**Proactive / Intelligent Systems:**
- Recommendation systems for scholarly literature
- Research gap detection in academic literature
- Contradiction detection in large corpora
- Spaced repetition algorithms (Anki/SuperMemo) for scholarly memorization
- How does Elicit/Consensus/ScholarAI approach research questions?

---

## API Keys

API keys are stored in `.env` (gitignored, never committed). The owner provides them.

Required keys:
- `OPENROUTER_API_KEY` — for multi-model LLM access
- `ANTHROPIC_API_KEY` — for direct Claude access
- `OPENAI_API_KEY` — for direct GPT access

Optional keys (add as needed):
- `MEM0_API_KEY` — if using mem0's managed platform instead of self-hosted
- `SHAMELA_API_KEY` — if using ragaeeb/shamela's API features

---

## Text Chunking / Passage Segmentation

### Semantic Text Chunking (general approaches)
- **LangChain RecursiveCharacterTextSplitter** — hierarchical splitting using separators. Good default for structured text. Available via `langchain` Python package.
- **LlamaIndex SemanticSplitterNodeParser** — splits by analyzing consecutive sentence embeddings for coherence. Available via `llama-index`.
- **Agentic chunking** — LLM determines chunk boundaries dynamically. Experimental, high computational cost. IBM watsonx tutorial demonstrates approach. Not suitable for bulk processing but applicable to high-value sources.
- **Adaptive chunking** — aligns to section/sentence boundaries with variable window sizes. Clinical decision support study (MDPI Bioengineering, Nov 2025) showed 87% accuracy vs 13% for fixed-size baselines on structured documents.
- **Relevant to:** Passaging engine (§4.A.4 semantic splitting, §4.B.2 implicit structure discovery)

### Arabic-Specific Text Segmentation
- **AraWiki50k** — first large-scale Arabic dataset for semantic text chunking (MDPI, June 2025). Uses fine-tuned BERT embeddings from STS task. Demonstrates that Arabic semantic chunking is an active research area with limited but growing tool support.
- **Arabic sentence boundary detection** — research shows CRF-based methods achieve ~84% F-measure. DNN approaches achieve better results on MSA. PDTS (punctuation detection approach) uses multilingual BERT for segmenting unpunctuated Arabic text.
- **Key finding:** Arabic semantic chunking research is still early-stage. No production-ready Arabic-specific chunking library exists. KR's approach of using division tree structure as primary boundary guidance (supplemented by LLM-assisted splitting for oversized divisions) is more robust than purely embedding-based methods for structured scholarly texts.
- **Relevant to:** Passaging engine

### Multilingual Sentence Embedding Models
- **intfloat/multilingual-e5-large** — strong multilingual sentence embeddings. Arabic support via multilingual training. Suitable for computing sentence-level semantic similarity for topic coherence and boundary quality scoring.
- **sentence-transformers/paraphrase-multilingual-mpnet-base-v2** — alternative multilingual model with good Arabic performance. Smaller than e5-large.
- **Relevant to:** Passaging engine (§4.B.1 quality prediction, §4.B.2 implicit structure discovery)

---

## Atomization Engine Resources (added 2026-03-05)

### Quran_Detector (Python, open source)
- **URL:** https://github.com/SElBeltagy/Quran_Detector
- **What it does:** Identifies Quranic verse or verse fragment (≥3 words) in any piece of Arabic text. Handles minor typos and missing words. Returns surah/ayah identification.
- **Relevant engines:** Atomization engine (§4.A.4 — rule-based Quran detection in passage text)
- **How to use:** Python library. Feed passage_text, receive detected Quran spans with surah/ayah numbers and confidence scores. Needs canonical Quran text database (from Quranic Arabic Corpus).
- **License:** Check repo

### Quranic Arabic Corpus
- **URL:** https://corpus.quran.com
- **What it does:** Complete word-by-word morphological annotation, syntactic treebank, and semantic ontology for the entire Quran. Machine-readable data available.
- **Relevant engines:** Atomization engine (canonical Quran text database for detection), Excerpting engine (Quran reference resolution)
- **How to use:** Download corpus data. Use as the canonical Quran text source for the Quran_Detector and for embedded_refs verification.
- **License:** Academic/open access

### Hadith Segmenter (Altammami 2023, University of Leeds)
- **What it does:** Segments hadith text into isnad (chain of narrators) and matn (content) with 92.5% accuracy. Based on classical Arabic NLP and machine learning.
- **Relevant engines:** Atomization engine (isnad chain boundary detection), Excerpting engine (isnad preservation)
- **Status:** Academic research (PhD thesis). Implementation may need to be reproduced from paper. The key insight — that isnad/matn segmentation can be automated at >90% accuracy — validates the atomization engine's approach of detecting isnad chains as a bonded cluster type.
- **Reference:** Altammami, S.H. (2023). "Artificial Intelligence for Understanding the Hadith." PhD thesis, University of Leeds.

### CANERCorpus (Classical Arabic NER)
- **What it does:** Classical Arabic named entity recognition corpus annotated with Islamic topic-specific NE classes from 7000+ hadiths.
- **Relevant engines:** Atomization engine (scholar name detection in isnad chains), Excerpting engine (scholar identification)
- **Status:** Research corpus. Useful for training/evaluating NER on classical Arabic scholarly text.

### Instructor (Python, MIT)
- **URL:** https://python.useinstructor.com
- **What it does:** Structured LLM output extraction with Pydantic schema enforcement, automatic retries on validation failure, streaming support. 3M+ monthly downloads. Works with OpenAI, Anthropic, Google, Ollama, and 15+ providers.
- **Relevant engines:** Atomization engine (primary LLM interaction tool), Excerpting engine, all LLM-driven engines
- **How to use:** `pip install instructor`. Define Pydantic model for atom output schema. Use `instructor.from_provider()` to create typed LLM client. Schema violations automatically trigger retries with error feedback.
- **License:** MIT

### Arabic Discourse Segmentation Research
- **Key finding:** Rule-based Arabic discourse segmentation using punctuation marks + lexical cues achieves reasonable accuracy (Keskes et al., LREC 2012). 97 unambiguous lexical cues identified for Arabic clause boundaries. However, classical Arabic scholarly texts are significantly different from modern Arabic news text — these tools are useful as reference but not directly applicable.
- **Key finding:** PDTS (Punctuation Detector for Text Segmentation) using multilingual BERT achieves ~75% F-measure on Arabic text segmentation. Not designed for scholarly text but demonstrates that transformer-based segmentation is feasible.
- **Key finding (2026):** IslamicLegalBench benchmark shows even the best LLMs achieve only ~67% accuracy on Islamic legal REASONING tasks with 21% hallucination (arXiv:2602.21226). However, KR's atomization task is EXTRACTION (structured pattern detection), not reasoning — LLMs perform significantly better on extraction. FiqhQA (2025) confirms LLMs show significant variation by school of thought and language (Arabic performance lower than English).
- **Key finding (2025-2026):** Multiple papers confirm that structured output extraction from Arabic text (NER, attribution detection, classification) achieves 80-90% accuracy with LLMs when using Pydantic schema enforcement and few-shot examples. This validates the atomization engine's Instructor-based approach for scholarly function classification.
- **Implication for KR:** The atomization engine's LLM-driven approach is the right choice. Rule-based Arabic segmentation tools are insufficient for scholarly text pattern detection (they don't understand definitions, evidence, opinions). The LLM handles the semantic understanding; rule-based methods handle the mechanical detections (Quran, hadith markers).

## Taxonomy Engine Resources (added 2026-03-05)

### NetworkX (Python, BSD license)
- **URL:** https://networkx.org
- **What it does:** Python library for creating, manipulating, and studying complex networks and graphs. Supports directed acyclic graphs (DAGs), tree operations, topological sorting, path algorithms, connectivity checks.
- **Relevant engines:** Taxonomy engine (PRIMARY — tree structure representation, prerequisite DAG management, tree integrity validation, significance scoring via out-degree computation), Scholar interface (graph traversal for prerequisite chains)
- **How to use:** `pip install networkx`. Load science tree into DiGraph. Use `nx.is_arborescence()` for tree validation, `nx.descendants()`/`nx.ancestors()` for subtree operations, `nx.dag_longest_path_length()` for prerequisite depth, topological sort for study ordering.
- **License:** BSD 3-Clause

### Hierarchical Text Classification with LLMs (research)
- **Key finding (2024–2026):** Multiple papers demonstrate that LLMs can perform hierarchical text classification effectively when using a top-down multi-step strategy: first classify at the highest level, then narrow to the correct leaf. For large taxonomies (200+ labels), hierarchical prompting significantly outperforms flat classification. The TELEClass approach (Zhang et al., 2024) enriches taxonomy labels with corpus-mined terms to improve LLM classification accuracy. Sonnet-3.5 can restructure large taxonomies (500+ nodes) with zero invalid paths.
- **Relevance:** Validates the taxonomy engine's hierarchical placement approach (§4.A.1) — for trees with >200 leaves, first identify the branch, then the leaf within the branch. Also validates the corpus-driven tree construction approach (§4.B.3) — LLMs can reliably reorganize and refine large hierarchical structures.
- **References:** "Hierarchical Text Classification with LLM-Refined Taxonomies" (arxiv 2601.18375), TELEClass (arxiv 2403.00165), "Single-pass Hierarchical Text Classification with LLMs" (2024).

### nxontology (Python, Apache 2.0)
- **URL:** https://github.com/related-sciences/nxontology
- **What it does:** NetworkX-based library for representing ontologies. Provides semantic similarity measures between ontology nodes, information content computation, and ontology analysis utilities.
- **Relevant engines:** Taxonomy engine (potential — semantic similarity between tree nodes for evolution sibling coherence testing)
- **Status:** Reference. The taxonomy engine's core tree operations use NetworkX directly; nxontology may be useful if more sophisticated ontology operations are needed later.
- **License:** Apache 2.0

## Excerpting Engine Resources (added 2026-03-05)

### ContextGem (Shcherbak AI, open source)
- **URL:** https://github.com/shcherbak-ai/contextgem
- **What it does:** LLM extraction from documents with structured output. Designed for document-level information extraction with context preservation.
- **Relevant engines:** Excerpting engine (document-level extraction patterns), potentially all LLM-driven engines
- **Status:** Reference for extraction patterns. KR uses Instructor as its primary structured output tool, but ContextGem's approach to context preservation during extraction is informative for the excerpting engine's self-containment evaluation.
- **License:** Check repo

### LLM4IE Papers (curated list)
- **URL:** https://github.com/quqxui/Awesome-LLM4IE-Papers
- **What it does:** Curated collection of papers on LLM-based information extraction. Covers NER, relation extraction, event extraction, and unified extraction approaches.
- **Relevant engines:** All LLM-driven engines. Particularly useful for: (1) few-shot extraction techniques applicable to excerpting, (2) structured output strategies for complex nested schemas, (3) multi-task extraction combining NER + relation extraction (analogous to KR's combined scholar identification + school attribution).
- **Key finding:** State-of-the-art in LLM IE uses Instructor/Pydantic-style schema enforcement with few-shot examples. Fine-tuning is used when training data exists; zero/few-shot works well for domain-specific extraction when good examples are provided. This validates KR's approach of Instructor + gold baselines + DSPy optimization.

### Sentence-Transformers (Reimers & Gurevych)
- **URL:** https://www.sbert.net / https://github.com/UKPLab/sentence-transformers
- **What it does:** Framework for computing sentence and text embeddings. State-of-the-art multilingual models available. Used for semantic similarity, clustering, and search.
- **Relevant engines:** Excerpting engine (duplicate excerpt detection via embedding similarity), Taxonomy engine (topic similarity for placement), Scholar interface (semantic search over excerpts)
- **How to use:** `pip install sentence-transformers`. Use `paraphrase-multilingual-mpnet-base-v2` or `intfloat/multilingual-e5-large` for Arabic text embeddings. Compute cosine similarity between excerpt embeddings for duplicate detection.
- **License:** Apache 2.0

---

## Validation Component Resources

### jsonschema (Python JSON Schema validation)
- **URL:** https://github.com/python-jsonschema/jsonschema / https://pypi.org/project/jsonschema/
- **What it does:** JSON Schema validation for Python. Full support for Draft 2020-12, Draft 2019-09, Draft 7, Draft 6, Draft 4, Draft 3. Lazy validation via `iter_errors` reports all violations, not just the first. Format checking with optional dependencies.
- **Relevant component:** Validation (PRIMARY — schema validation for all engine artifacts)
- **How to use:** `pip install jsonschema[format]`. Use `Draft202012Validator` with `iter_errors` for comprehensive validation. Register custom format checkers for KR-specific formats.
- **Version:** v4.26+ (latest as of March 2026)
- **License:** MIT
- **Note:** jsonschema-rs (Rust-based, 43-240x faster) exists but is Beta and adds a native dependency. Use standard jsonschema for correctness guarantees; consider jsonschema-rs only if schema validation becomes a performance bottleneck.

### Pydantic v2 (Runtime validation for component outputs)
- **URL:** https://docs.pydantic.dev/
- **What it does:** Runtime data validation using Python type hints. Rust-powered core for performance. Used for ValidationResult, ValidationReport, and configuration models.
- **Relevant component:** Validation (output models, configuration), Consensus (already a dependency via Instructor)
- **How to use:** Already a project dependency. Define ValidationResult and ValidationReport as Pydantic v2 BaseModel classes.
- **Version:** v2.12+ (latest as of March 2026)
- **License:** MIT

### hashlib (Python stdlib — integrity hashing)
- **URL:** https://docs.python.org/3/library/hashlib.html
- **What it does:** Secure hash computation. SHA-256 for file integrity verification. Chunked reading for large files.
- **Relevant component:** Validation (file hash verification, provenance chain integrity)
- **How to use:** Python stdlib, no installation. `hashlib.sha256()` with 64KB chunk reads.
- **License:** Python Software Foundation License

## Human Gate Component Resources (added 2026-03-06)

### Design Decision: No External HITL Framework
- **Context:** Surveyed LangGraph HITL middleware, Temporal workflow approval, HumanLayer SDK, and various Python task queues (Celery, RQ, persist-queue).
- **Decision:** None applicable. KR's human gate is a persistent review queue for a single user reviewing batched decisions, not a real-time agent interrupt system. The complexity is in the gate type registry, bidirectional validation, and policy management — not in the queue infrastructure itself.
- **Implementation:** Python stdlib file operations (JSON read/write with atomic rename), Pydantic v2 for models, shared/validation for integrity checks. No additional dependencies required.

---

## Feedback Component Resources

### DSPy Optimizers (Prompt Optimization — used by individual engines, coordinated by feedback component)

**MIPROv2** (already cataloged above): Creates few-shot examples and instructions for each predictor, searches combinations via Bayesian Optimization. Best for: when you have 200+ training examples and want joint instruction + few-shot optimization. Cost: ~$2 USD / ~20 min per run. KR usage: engines run MIPROv2 against correction-derived training data when the feedback component detects enough new corrections.

**SIMBA** (Stochastic Introspective Mini-Batch Ascent):
- **URL:** https://dspy.ai/api/optimizers/SIMBA/
- **What it does:** Uses stochastic mini-batch sampling to identify challenging examples with high output variability, then applies the LLM to introspectively analyze failures and generate self-reflective improvement rules. Two strategies: `append_a_rule` (LLM reflects on failures and derives improvement rules) or `add_successful_demo` (adds working examples). More sample-efficient than MIPROv2.
- **Relevant for:** Engines with few corrections but clear failure patterns. SIMBA's self-reflective rules map directly to the feedback component's "systemic pattern → engine rule update" cycle.
- **KR usage:** Preferred optimizer for engines with <100 training examples. SIMBA generates explicit improvement rules from corrections, which are more interpretable than MIPROv2's Bayesian-optimized prompt variations.
- **License:** MIT (part of DSPy)

**GEPA** (Reflective Prompt Evolution):
- **URL:** https://dspy.ai/learn/optimization/optimizers/ (DSPy >= 3.1.0)
- **What it does:** Uses rich textual feedback (not just scalar rewards) and Pareto frontiers to evolve prompts. Analyzes what worked, what didn't, and proposes targeted prompt improvements. Up to 11% better than MIPROv2 on complex tasks.
- **Relevant for:** Complex reasoning tasks where the feedback component's correction `reason` field provides rich textual signal.
- **KR usage:** Potential future optimizer for synthesis engine (which receives the most detailed owner corrections). Requires DSPy >= 3.1.0.
- **License:** MIT (via dspy-gepa package)

### DeepEval (LLM Evaluation Framework)
- **URL:** https://deepeval.com
- **What it does:** Python framework for LLM testing and evaluation. Provides metrics (GEval, correctness, bias, toxicity), regression testing with side-by-side comparison, and test case management. Integrates with pytest.
- **Relevant for:** The feedback component's regression test coordination — DeepEval provides the regression testing infrastructure that engines can use for gold baseline evaluation.
- **KR usage:** Optional — engines may use DeepEval for regression testing, or implement their own simpler test harness. The feedback component coordinates the triggering and result tracking regardless of which testing framework the engine uses.
- **License:** Apache 2.0
- **How to use:** `pip install deepeval`. Define test cases with input/expected_output/actual_output. Run with pytest integration. Supports LLM-as-a-judge for nuanced evaluation.

## User Model Component Resources (added 2026-03-06)

### py-fsrs (Python, MIT license)
- **URL:** https://github.com/open-spaced-repetition/py-fsrs
- **Version:** 5.1+ (FSRS v6 model)
- **What it does:** Implements the Free Spaced Repetition Scheduler (FSRS) algorithm — state-of-the-art open-source spaced repetition scheduling backed by KDD 2022 research. Handles card state management, review scheduling (next due date computation), retrievability estimation, and JSON serialization. Uses a DSR (Difficulty-Stability-Retrievability) memory model with 21 trainable parameters.
- **How to use:** `pip install fsrs`. Card and Scheduler objects are JSON-serializable via `to_json()`/`from_json()`. Supports custom `desired_retention` (0.70–0.99), configurable learning/relearning steps, and parameter personalization.
- **KR usage:** Core spaced repetition engine in user model §4.A.3. Handles all scheduling logic — the user model wraps it but does not reimplement scheduling.
- **API key:** None required. Runs entirely locally.

### fsrs-optimizer (Python, MIT license)
- **URL:** https://github.com/open-spaced-repetition/fsrs-optimizer
- **What it does:** Personalizes FSRS parameters from a user's actual review history. Trains the 21-parameter model on the user's review logs to produce scheduling that matches their personal forgetting curve. Requires PyTorch.
- **How to use:** `pip install fsrs-optimizer`. Input: review log in standard format (card_id, review_datetime, rating). Output: optimized 21-parameter tuple.
- **KR usage:** Optional optimization in user model §4.A.3. Triggered after 200+ reviews to personalize scheduling.
- **API key:** None required. Runs entirely locally. PyTorch dependency is heavy — consider using `fsrs-rs-python` (Rust-based, lighter) as an alternative if PyTorch is not already in the stack.

### pyBKT (Python, MIT license)
- **URL:** https://github.com/CAHLR/pyBKT
- **What it does:** Bayesian Knowledge Tracing — estimates learner mastery from interaction sequences using a Hidden Markov Model. Models four probabilities per skill: P(know), P(learn), P(guess), P(slip). Primarily designed for ITS with binary correct/incorrect responses.
- **Evaluated and NOT adopted for KR.** BKT requires high-volume binary response data (correct/incorrect answers to specific questions). KR's assessment model is richer (LLM-evaluated Socratic dialogue) and lower-frequency (assessments happen periodically, not after every interaction). KR uses a weighted confidence score (§4.A.2) instead, combining engagement depth, assessment performance, recency, and prerequisite strength. BKT may be reconsidered if KR adds high-frequency quiz-style interactions.

---

## Scholar Authority Component Resources

### Entity Resolution / Record Linkage

### Python Record Linkage Toolkit
- **URL:** https://recordlinkage.readthedocs.io/
- **What it does:** Pandas-based toolkit for prototyping record linkage systems. Supports blocking, comparison (Jaro-Winkler, Levenshtein, etc.), and classification (supervised + unsupervised). Extensible framework.
- **Relevant components:** Scholar authority (§4.A.2 matching algorithm). The comparison methods (Jaro-Winkler for Arabic name similarity) are directly applicable. However, KR's matching needs are domain-specific enough (Arabic onomastic conventions, death date signals, school affiliation) that a custom implementation per the SPEC is more appropriate than using this as a framework.
- **License:** BSD-3

### Dedupe (Python, MIT license)
- **URL:** https://github.com/dedupeio/dedupe
- **What it does:** ML-based entity resolution using active learning. Engages user in labeling pairs, then predicts duplicates at scale. Supports deduplication within a dataset and record linkage across datasets.
- **Evaluated and NOT adopted for KR.** Dedupe's strength is learning matching rules from user feedback on large datasets with many field types. KR's scholar matching has a well-defined set of signals (name, date, school, works, teachers) where a custom weighted algorithm (SPEC §4.A.2) is more transparent and auditable than an ML model. The active learning approach is also misaligned — the owner should only see genuinely ambiguous cases, not training pairs. However, Dedupe's blocking strategies (especially sorted neighborhood indexing) may inform the candidate selection step.

### Splink (Python, MIT license)
- **URL:** https://moj-analytical-services.github.io/splink/
- **What it does:** Probabilistic record linkage using Fellegi-Sunter model. Scales to millions of records. Built for government/institutional use (NHS, MOJ).
- **Evaluated and NOT adopted for KR.** Splink is optimized for large-scale probabilistic matching where ground truth is unavailable. KR's scholar registry will likely contain tens of thousands of records (not millions) and the matching signals are domain-specific. The custom five-signal algorithm in the SPEC is more appropriate.

### Islamic Scholar Databases

### Muslim Scholars Database (muslimscholars.info)
- **URL:** https://muslimscholars.info/
- **What it does:** Comprehensive database of Muslim scholars from Companions era to present. Contains biographical data extracted from classical sources: Tahzeeb al-Tahzeeb, Taqrib al-Tahzeeb, at-Thiqat, Tarikh al-Kabir, Tabaqat ibn Sa'd, Siyar A'lam al-Nubala, Lisan al-Mizan, Tahzeeb al-Kamal. Records include: famous name (Arabic/English), lineage, kunya, laqab, generation, tabqa, birth/death dates+places, places of stay, hadith narration grade, teacher list, student list, brief biography. ~40,000+ records with teacher-student links.
- **Relevant components:** Scholar authority (§4.A.5 external enrichment). This database contains exactly the teacher-student graph data KR needs. However, it has no public API — data would need to be scraped or requested from the maintainers. The ~5% error/duplication rate they acknowledge is within acceptable limits for enrichment data (KR's own validation catches conflicts). Priority: HIGH if data access can be obtained.
- **License:** Not specified. Contact maintainers.

### Usul.ai Data (seemorg/usul-data) (JSON, MIT license)
- **URL:** https://github.com/seemorg/usul-data
- **What it does:** Structured JSON dataset of Islamic scholars with multilingual names (14 languages including Arabic, English, Persian, Urdu), death dates (Hijri year), biographical descriptions, and linked book metadata. Built on OpenITI and Shamela/Turath data. MIT-licensed, freely redistributable.
- **Relevant components:** Scholar authority (§4.B.1 bootstrapping, §4.A.5 external enrichment). Provides confirmed death dates, multilingual name variants, and author-book relationships. Complements OpenITI by adding richer multilingual biographical metadata. Can be bundled directly with KR.
- **How to use:** Download `authors.json` from the repo. Each author record: `id`, `primaryNameTranslations` (multilingual), `year` (Hijri death year), `bio` (multilingual descriptions). Books link via `authorId`.
- **License:** MIT.

### İSAM Ulema Database (Turkey)
- **URL:** Centre for Islamic Studies (İSAM), Istanbul
- **What it does:** Repository of 10,000+ Muslim scholars and Sufis with biographical data from classical texts integrated with modern historiography. Searchable by name, era, and madhhab.
- **Relevant components:** Scholar authority enrichment. Similar data to muslimscholars.info but with different coverage (stronger on Ottoman-era and Turkish scholars). Access restrictions unknown.
- **License:** Institutional.

### Wikidata Islamic Scholar Coverage
- **URL:** https://www.wikidata.org/ (Q13200659 = Islamic scholar occupation)
- **What it does:** Structured biographical data for scholars with Wikipedia articles. Properties: P569/P570 (birth/death dates), P1066 (student of), P802 (student), P106 (occupation), P140 (religion), plus Arabic labels and aliases.
- **Relevant components:** Scholar authority (§4.A.5 Wikidata enrichment). Coverage is incomplete for premodern scholars but useful when available. SPARQL endpoint enables programmatic queries. Main value: confirmed dates and teacher-student links with Wikidata QIDs for cross-referencing.
- **License:** CC0 (public domain)

## Scholar Interface Resources

### Socratic AI Tutoring Systems
- **SocraticAI** (arXiv 2512.03501) — scaffolded AI tutoring using LLMs with structured constraints. Key insight: enforcing well-formulated questions and reflective engagement produces better learning than unrestricted AI access. 75% of students produce substantive reflections within 2-3 weeks. Relevant for §4.A.3 assessment design.
- **KELE Framework** (EMNLP 2025 Findings) — multi-agent Socratic teaching with "consultant-teacher" collaboration. Uses structured rules (SocRule) to govern dialogue. Relevant for multi-turn Socratic assessment architecture.
- **S-ICA** (ScienceDirect, 2025) — Socratic Intelligent Conversational Agent combining LLM with structured questioning. Research shows significant improvement in reflective thinking and research design skills. Validates the Socratic approach for scholarly learning.
- **Key design insight from research:** The most effective Socratic systems combine AI questioning with structured scaffolds and feedback loops. Pure open-ended questioning is less effective than constrained, progressive questioning (recall → recognition → application → comparison).

### Knowledge Graph RAG Systems
- **GraphRAG** (Microsoft Research, 2024) — graph-based RAG that constructs knowledge graphs from documents for multi-hop reasoning. KR's approach is analogous but with pre-built domain-specific graphs (taxonomy trees, scholar authority, work relationships) rather than auto-constructed graphs.
- **StructRAG** (ACM WWW 2025) — structure-aware RAG using Deep Document Model to preserve hierarchical structure. Relevant for KR's use of taxonomy tree hierarchy in retrieval.
- **KG-RAG with Chain of Explorations** — uses LLM reasoning to explore knowledge graph nodes sequentially. Relevant for scholar network exploration and intellectual genealogy queries.

### Classical Islamic Pedagogical Progressions
- **islamclass.wordpress.com** — detailed madhab-specific study progressions for Hanafi, Shafi'i, and Hadith sciences. Key resource for curriculum knowledge base (§4.A.1.1). Documents the traditional mutun → shuruh → hawashi progression with specific text recommendations per level.
- **SeekersGuidance curriculum** — five-level systematic program. Useful as a reference for level classification (beginner → advanced).
- **Key domain insight:** Classical progressions are text-based (study this book, then that book), not topic-based. KR's curriculum system must bridge both: the classical text sequence AND the taxonomy's topic sequence. The curriculum follows the text order (الآجرومية then قطر الندى) but within each text, topics follow the taxonomy's narrative ordering.

### Arabic Embedding Models (for semantic retrieval)
- **Swan-Large** (NYUAD): SOTA for Arabic tasks on ArabicMTEB benchmark (2024). Outperforms Multilingual-E5-large in most Arabic tasks. Dialectally and culturally aware.
- **Arabic-STS-Matryoshka** (Omartificial-Intelligence-Space): Score 83.16 on STS17. Supports Matryoshka dimensionality reduction for efficient retrieval.
- **Multilingual-E5-base/large** (Microsoft): Strong multilingual baseline, good Arabic support.
- **GTE-multilingual-base** (Alibaba): Good Arabic support, efficient.
- **Relevant engines:** Scholar interface (semantic search), excerpting (similarity detection)
- **Recommendation:** Swan-Large for quality, Arabic-STS-Matryoshka for efficiency. Benchmark on KR's actual Arabic scholarly text before committing.
- **AraGemma-Embedding-300m:** https://huggingface.co/Omartificial-Intelligence-Space/AraGemma-Embedding-300m — Fine-tuned from Google's EmbeddingGemma-300M for Arabic semantic understanding. 300M params, supports Matryoshka dimensions (flexible truncation). Trained on 1M Arabic triplet pairs. Lightweight, deployable locally.
- **Swan-Large (MBZUAI):** https://arxiv.org/abs/2411.01192 — Dialect-aware Arabic-centric embedding model. Top performer on ArabicMTEB benchmark across retrieval, STS, classification, and clustering. Specifically designed for Arabic linguistic intricacies.
- **Arabic-triplet-Matryoshka-V2:** https://huggingface.co/collections/Omartificial-Intelligence-Space/arabic-matryoshka-and-gate-embedding-models — #1 on MTEB STS17 Arabic-Arabic leaderboard (score 85.3). Uses Matryoshka learning for efficient multi-resolution embeddings.
- **Microsoft E5-ML-Large:** Best overall multilingual performance on Arabic RAG retrieval (ARCD benchmark, >90% Recall@10). Not Arabic-specific but strong.
- **Evaluation needed:** These models are benchmarked on modern standard Arabic. KR must evaluate on classical Arabic scholarly text with diacritics, technical terminology, and multi-school vocabulary — performance may differ.

### Vector Database — Qdrant
- **URL:** https://qdrant.tech/ | https://github.com/qdrant/qdrant
- **What it does:** Open-source vector database written in Rust. Supports filtered vector search (combining semantic similarity with metadata constraints), disk persistence, HNSW indexing with binary quantization, and both gRPC and REST APIs.
- **Why chosen for KR:** The scholar interface requires frequent combined vector+metadata queries (e.g., "find similar excerpts in the Hanafi school from pre-400 AH scholars"). Qdrant's payload filtering overhead is ~1.1x regardless of filter complexity, compared to 2.3x for pgvector on text fields and 3-8x for ChromaDB. Self-hosted via Docker with disk persistence — suitable for a personal application.
- **Alternatives considered:** pgvector (strong baseline search but metadata filtering is slower; better when already heavily using PostgreSQL), ChromaDB (excellent prototyping but not optimized for production filtered search), Pinecone (managed service — unnecessary dependency for a personal local application).
- **License:** Apache 2.0. Python SDK: `qdrant-client` with full async support.

### Cross-Encoder Re-Ranking
- **Purpose:** After initial embedding-based retrieval (fast, approximate), re-rank top-K results with a cross-encoder (slower, precise). Standard in production RAG systems — significantly improves precision.
- **Arabic options:** (a) Multilingual cross-encoders from BGE or Cohere families, (b) fine-tune a cross-encoder on KR-specific relevance data as the library grows, (c) LLM-as-reranker (more expensive but potentially more accurate for classical Arabic scholarly text).
- **Latency:** Adds ~100-200ms per query. Acceptable for a personal scholarly application.
