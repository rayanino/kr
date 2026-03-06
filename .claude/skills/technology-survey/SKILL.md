---
name: technology-survey
description: Survey available tools, libraries, and techniques for a KR capability. Use before implementing any engine feature, when starting a new SPEC section, or when you suspect custom code could be replaced by an existing tool. Updates reference/RESOURCES.md with findings.
---

# Technology Survey for KR

Before building anything custom, verify that no existing tool handles it better. The owner has infinite budget for tools and API keys.

## Survey Protocol

### Step 1: Define What You Need
State the capability in one sentence:
- "I need to extract text from scanned Arabic PDF pages."
- "I need to detect topic boundaries in classical Arabic prose."
- "I need to build a semantic search index for Arabic scholarly text."

### Step 2: Search Broadly (minimum 5 searches)
Search patterns — adapt to your need:
1. `[capability] Arabic NLP library 2025` — language-specific tools
2. `[capability] Python library` — general tools
3. `[capability] LLM technique` — LLM-based approaches
4. `Islamic studies digital humanities tools` — domain-specific
5. `[capability] state of the art benchmark` — what's the best available?

### Step 3: Evaluate Each Candidate

For each tool found:
```
Tool: [name]
URL: [link]
What it does: [one sentence]
Arabic support: [YES/NO/PARTIAL — this is a dealbreaker for many tools]
Relevance to KR: [HIGH/MEDIUM/LOW]
Maturity: [production/beta/experimental]
License: [open source/commercial/API-only]
Integration effort: [trivial/moderate/significant]
KR-specific limitation: [what it CAN'T do that KR needs]
```

### Step 4: Make a Recommendation
Either:
- "Use [tool] for [capability]. Custom code for [remaining gap]."
- "No suitable tool exists. Custom implementation required because [reason]."
- "Multiple tools could work. Recommend [tool] because [tradeoff analysis]."

### Step 5: Update RESOURCES.md
Add findings to `reference/RESOURCES.md` under the appropriate category. Include the URL, a one-line description, and the evaluation result.

## Domain-Specific Search Directions

### Arabic NLP
- CAMeL Tools (NYU Abu Dhabi) — morphological analysis, dialectal handling
- Farasa — Arabic NLP toolkit from QCRI
- AraGPT2 / JAIS / ALLaM — Arabic language models
- Stanza (Stanford) — Arabic dependency parsing
- OpenITI / KITAB — Islamic text analysis tools

### OCR for Arabic
- Mistral OCR — multimodal OCR
- Tesseract with Arabic models
- Qari-OCR — specialized for Arabic diacritics
- Google Cloud Vision — Arabic text detection
- Amazon Textract — document processing

### Scholarly Text Analysis
- OpenITI corpus — largest open Islamic text collection
- Usul.ai (seemorg/usul-data) — Islamic studies metadata
- al-Maktaba al-Shamela API — if any exists
- Digital Orientalist tools — cross-tradition resources
- Voyant Tools — text analysis for digital humanities

### Vector Search / Embeddings
- Arabic embedding models: arabic-e5, arabert-base
- Qdrant, Milvus, Pinecone — vector databases
- Cross-encoder models for Arabic reranking
- Sentence-transformers with multilingual models

### Knowledge Graphs
- Neo4j — property graph database
- Apache Jena — RDF/SPARQL for linked data
- Wikidata integration for scholar metadata
- Ontology editors for Islamic knowledge structures

## Red Flags: When Custom Code Is Wrong

- You're writing a tokenizer for Arabic → use CAMeL Tools or Farasa
- You're writing an OCR pipeline → use Mistral OCR or Google Cloud Vision
- You're writing a search engine → use Qdrant with Arabic embeddings
- You're writing a PDF parser → use pdfplumber, pymupdf, or Mistral OCR
- You're writing HTML parsing → use BeautifulSoup or lxml
- You're writing JSON schema validation → use pydantic or jsonschema

Custom code is appropriate for: KR-specific business logic, pipeline orchestration, scholarly domain rules, taxonomy management, synthesis logic, and any capability that combines multiple tools in KR-specific ways.
