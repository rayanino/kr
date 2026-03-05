# خزانة ريان — External Resources Catalog

This file maps known external tools, libraries, and services to KR engines. Every engine SPEC should consider whether existing tools can handle part of the work before designing custom solutions.

**Principle:** Build on existing tools wherever possible. Custom code is a last resort. If a library handles 80% of the job, use it and write custom code for the remaining 20%.

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
- Multi-document summarization tools
- RAG frameworks (LlamaIndex, LangChain)
- Citation generation tools

**Consensus engine:**
- OpenRouter (already cataloged — multi-model gateway)
- DSPy (already cataloged — pipeline orchestration)
- LiteLLM (provider routing, used by DSPy internally)

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
