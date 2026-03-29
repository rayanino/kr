# Arabic NLP Tools Survey for KR Pipeline

**Date:** 2026-03-28
**Scope:** Tools, models, and libraries NOT currently used by KR that could improve the 5-engine pipeline
**Current KR stack:** Claude Opus 4.6, GPT-5.4, Gemini 2.5 Pro via LLM calls; no dedicated Arabic NLP libraries

---

## Summary Ranking Table

All findings ranked by value-to-effort ratio. Value (1-5) measures impact on pipeline correctness and cost reduction. Effort (S/M/L) measures integration complexity.

| Rank | Tool / Model | Value | Effort | Pipeline Stage | Primary Benefit |
|------|-------------|-------|--------|----------------|-----------------|
| 1 | **Tanzil Quran Corpus** | 5 | S | Excerpting | Deterministic Quranic citation detection, zero LLM cost |
| 2 | **GATE / AraGemma Embeddings** | 5 | S | Taxonomy, Excerpting | Pre-filter/cluster before LLM calls, 95%+ cost reduction on simple classifications |
| 3 | **CAMeL Tools** | 5 | M | Normalization, Excerpting | Morphological analysis, NER, Classical Arabic BERT variant |
| 4 | **OpenITI Corpus + Passim** | 4 | M | Source, Excerpting | Text reuse detection, scholarly metadata for 6,236 works |
| 5 | **Quranic Arabic Corpus (Leeds)** | 4 | S | Excerpting, Taxonomy | Morphological/syntactic treebank for all Quran verses |
| 6 | **Farasa** | 4 | S | Normalization, Passaging | Fast Arabic segmentation, lemmatization, diacritization |
| 7 | **CAMeLBERT-CA** | 4 | M | Excerpting, Taxonomy | Classical Arabic BERT for cheap classification/NER |
| 8 | **Swan Embeddings** | 4 | M | Taxonomy | State-of-the-art Arabic embeddings on ArabicMTEB benchmark |
| 9 | **Isnad AI (AraBERTv2 fine-tuned)** | 4 | M | Excerpting | Hadith/Quran span detection in text (F1 87%) |
| 10 | **Shamela NodeJS API** | 3 | S | Source | Programmatic access to Shamela metadata and book downloads |
| 11 | **Jais 2 (70B)** | 3 | M | Consensus | Arabic-native LLM as consensus participant, open-weight |
| 12 | **ALLaM (7B-70B)** | 3 | M | Consensus | Arabic-English LLM from SDAIA, available on Hugging Face |
| 13 | **AraBERT / AraGPT2** | 3 | M | Excerpting, Taxonomy | Pre-trained Arabic transformers for classification without full LLM |
| 14 | **SILMA AI Embeddings** | 3 | S | Taxonomy | Lightweight Matryoshka Arabic embeddings |
| 15 | **AraMUS (11B)** | 3 | L | Taxonomy, Synthesis | Largest Arabic PLM, encoder-decoder, strong few-shot |
| 16 | **IslamicMMLU / IslamicLegalBench** | 2 | S | Validation | Benchmark datasets for testing Islamic knowledge quality |
| 17 | **Stanza Arabic** | 2 | M | Normalization | Stanford NLP Arabic pipeline, dependency parsing |
| 18 | **spaCy Arabic** | 2 | M | Normalization | Industrial NLP, but weak Arabic support |
| 19 | **SAFAR Framework** | 2 | L | Multiple | Comprehensive Arabic NLP framework, but heavyweight |

---

## 1. Arabic NLP Libraries

### 1.1 CAMeL Tools (NYU Abu Dhabi)

**What it is:** A comprehensive open-source Python toolkit for Arabic NLP developed by the CAMeL Lab at NYU Abu Dhabi. Current version: 1.5.7 on PyPI.

**Capabilities directly relevant to KR:**
- **Morphological analysis and disambiguation** -- can break Arabic words into root, pattern, stem, prefixes, suffixes. Critical for understanding scholarly terminology.
- **Named Entity Recognition** -- trained NER models that can identify person names (scholars), places, organizations in Arabic text.
- **Dialect identification** -- can distinguish MSA from dialects and from Classical Arabic (CA). Relevant for multi-layer text where commentary might be in a different register than the matn.
- **Diacritization** -- can add diacritics to undiacritized text. Useful for disambiguation in the Passaging engine where meaning depends on voweling.
- **Morphological databases:** Ships with calima-msa-r13 (MSA) database. Separate Classical Arabic models available.
- **Transliteration** -- conversions between Arabic script and various transliteration schemes (Buckwalter, HSB, etc.).
- **Text preprocessing** -- normalization, de-diacritization, cleaning utilities.

**Classical Arabic support:**
CAMeLBERT includes a dedicated Classical Arabic variant (bert-base-arabic-camelbert-ca) pre-trained specifically on classical Arabic texts. This is a key differentiator -- most Arabic NLP tools are MSA-only.

**How it could integrate with KR:**
- **Normalization engine:** Morphological analysis to validate text structure, detect encoding issues, identify text layer boundaries.
- **Excerpting engine:** NER for scholar name extraction in isnad chains. Morphological disambiguation to identify transmission formulas with high precision.
- **Taxonomy engine:** Lemmatization for building science trees. Dialect/register identification to distinguish matn from sharh from hashiyah layers.

**Domain sensitivity warning:**
A January 2026 multi-corpus evaluation (Farasa vs CAMeL vs ALP) across MSA, Quranic, and Hadith/jurisprudential domains showed that domain mismatch causes systematic degradation. CAMeL achieved 0.68 accuracy on MSA (NAFIS corpus) and 0.81 on the jurisprudential Sharaye corpus.

**Install:** pip install camel-tools && camel_data -i all
**License:** MIT | **Version:** 1.5.7 | **Python:** 3.8-3.12 | **GitHub:** https://github.com/CAMeL-Lab/camel_tools
**Integration effort:** M | **Value for KR:** 5/5

---

### 1.2 Farasa (QCRI)

**What it is:** Fast Arabic text processing toolkit from QCRI. Segmentation, lemmatization, POS tagging, diacritization, parsing, NER, spell-check.

**Key advantage:** 10x faster than QATARA, 100x faster than MADAMIRA. SVM-based with linear kernels.

**Domain performance (Noor-Ghateh benchmark, 223,690 words hadith/jurisprudence):**
- Farasa: 0.59 on MSA, competitive on Quranic and Sharaye
- CAMeL: 0.68 on MSA, 0.81 on Sharaye (tied highest)
- ALP: 0.81 on Quran (highest)

**Access:** Web API at https://farasa.qcri.org/ (free, registration required). Java segmenter for local use.
**Integration effort:** S | **Value for KR:** 4/5

---

### 1.3 AraBERT / AraGPT2 (AUB-MIND Lab)

Pre-trained Arabic transformers. AraBERT (encoder, classification/NER). AraGPT2 (decoder, generation). AraBERT v0.2/v2 base/large. AraGPT2 up to MEGA (1.46B). 77GB training data.

**Key finding:** AraBERT achieved 99.94% F1 on hadith authentication including isnad.

**Install:** transformers library, model ID: aubmindlab/bert-base-arabertv02
**License:** Apache 2.0 | **GitHub:** https://github.com/aub-mind/arabert
**Integration effort:** M | **Value for KR:** 3/5

---

### 1.4 Stanza / spaCy Arabic

Neither offers advantages over CAMeL Tools for Arabic scholarly text. spaCy has no dedicated Arabic models. Stanza is MSA-trained only.

**Integration effort:** M | **Value for KR:** 2/5

---

## 2. Pre-trained Models for Islamic Text

### 2.1 Isnad AI / IslamicEval 2025 Systems

Fine-tuned models for identifying Quranic verses and hadiths within text:
- **Isnad AI:** AraBERTv2 fine-tuned, F1 = 66.97%
- **BurhanAI:** F1 = 87.10% span detection, F1 = 90.06% with reasoning tools
- **TCE:** F1 = 86.11% identification, 89.82% verification accuracy

**Direct KR application:** Excerpting engine Quranic citation and hadith reference detection. Smaller models at 87%+ F1 could replace LLM calls.

**Integration effort:** M | **Value for KR:** 4/5

### 2.2 Hadith Authentication Models

AraBERT achieved 99.94% F1 on hadith authentication with isnad. Valuable as pre-filter before expensive LLM analysis.

### 2.3 IslamicMMLU Benchmark

Islamic knowledge evaluation across disciplines. Trims isnad from hadith -- validates KR treating isnad as separate structural element.

### 2.4 IslamicLegalBench

718 instances, 7 madhahib, 38 texts, 1,200 years. Best model: 68% correct, 21% hallucination. **Validates KR multi-model consensus approach -- single LLM calls for Islamic legal content are demonstrably unreliable.**

---

## 3. Text Segmentation

### 3.1 Arabic Sentence Boundary Detection

Best MSA SBD: 84.37% F-measure (CRF). Classical Arabic SBD is an open research problem. Classical texts lack modern punctuation; boundaries are discourse connectors. **KR current structural boundary approach is well-suited.**

### 3.2 Paragraph Detection in Unpunctuated Classical Text

No production-ready tool exists. OpenITI mARkdown has paragraph annotations for some texts. KR Passaging engine handles via structural markers.

---

## 4. Competing / Related Projects

### 4.1 Usul.ai

World first AI search engine grounded in 15,000 Islamic texts. Uses GPT-4o class LLMs. 13 core Islamic disciplines. Inspectable citations, near-zero hallucination. Closest system to KR but search/QA focused, not structured pipeline.

**What KR can learn:** Discipline taxonomy (13 sciences) could validate KR science tree. Citation verification approach for Excerpting. Scale (15K texts) validates pipeline approach.

**URL:** https://usul.ai/ | **API:** No public API

### 4.2 OpenITI / KITAB Project

- **OpenITI Corpus:** 10,202 text files, 6,236 works, 2,582 authors. Open-access.
- **mARkdown format:** Lightweight tagging for Arabic scholarly texts (alternative to TEI XML).
- **Passim text reuse detection:** 300-word segment comparison via Apache Spark, tuned for classical Arabic.
  - GitHub: https://github.com/dasmiq/passim | Install: pip install passim (requires Java)
- **OCR pipeline:** AOCP Phase Two (.75M funded, 2022-2025)

**KR applications:**
1. Source engine: cross-reference metadata against 2,582 author records
2. Excerpting: text reuse detection for citations, hadith quotations
3. Taxonomy: author/work metadata as ground truth
4. mARkdown compatibility for future OpenITI text ingestion

**Latest release:** Zenodo 2025 | **License:** Various open | **GitHub:** https://github.com/openiti
**Integration effort:** M | **Value for KR:** 4/5

### 4.3 Quranic Arabic Corpus (Leeds University)

Word-by-word grammar, syntax, morphology for every Quran word. Three levels: morphological annotation, syntactic treebank (QADT), semantic ontology.

**KR application -- deterministic Quranic citation detection:**
Build lookup index from corpus data. String matching against complete verse database. 100% accurate (no hallucination), zero cost per lookup, handles partial citations.

**Download:** https://corpus.quran.com/download/ (v0.4) | **License:** GNU
**Integration effort:** S | **Value for KR:** 4/5

### 4.4 Tanzil.net

Definitive digital Quran text, manually verified against Medina Mushaf. UTF-8, Uthmani/simple script. Use BOTH Tanzil (text matching) and Leeds (linguistic analysis).

**URL:** https://tanzil.net/download/ | **License:** Free, credit required
**Integration effort:** S | **Value for KR:** 5/5 (combined with Leeds)

### 4.5 Shamela API (NodeJS)

Unofficial libraries for programmatic Shamela access. getMasterMetadata(), downloadBook(), parse/sanitise utilities. sql.js WebAssembly for database ops.

**GitHub:** https://github.com/ragaeeb/shamela
**Integration effort:** S | **Value for KR:** 3/5

---

## 5. Arabic Embeddings

### 5.1 GATE (General Arabic Text Embedding)

State-of-the-art Arabic embeddings using Matryoshka Representation Learning. Supports dimensions: 768/512/256/128/64. Outperforms OpenAI embeddings by 20-25%% on Arabic STS benchmarks. Scores 85.3 on STS17 leaderboard.

**Key innovation:** Hybrid loss combining cosine similarity and softmax-based classification.

**Models:** Omartificial-Intelligence-Space/GATE-AraBert-v1 and Matryoshka variants on HuggingFace.

**KR application -- cost reduction through embedding pre-filtering:**
1. Embed all passages using GATE (local, free)
2. Cluster similar passages
3. Classify cluster centroids with LLM (expensive but few calls)
4. Propagate labels to all cluster members
5. Expected result: 90%%+ reduction in Taxonomy LLM calls

**Diacritics handling:** Normalizes diacritics during preprocessing. KR must embed NORMALIZED form for matching while preserving ORIGINAL in storage. Aligns with KR normalization-vs-preservation split.

**License:** Open (HuggingFace) | **Updated:** January 2025
**Integration effort:** S | **Value for KR:** 5/5

### 5.2 Swan Embeddings

Arabic-centric embedding models. Swan-Small (ARBERTv2-based, fast) and Swan-Large (ArMistral-based, accurate). Swan-Large: 62.45 on ArabicMTEB (94 datasets, 8 task types). Dialect-aware, culturally aware.

**Publication:** NAACL 2025 Findings | **License:** Research (publicly accessible)
**Integration effort:** M | **Value for KR:** 4/5

### 5.3 AraGemma-Embedding-300m

Fine-tuned Google EmbeddingGemma-300M for Arabic. Only 300M params -- CPU-friendly. 1M Arabic triplet pairs training. Good for quick similarity checks.

**Model:** Omartificial-Intelligence-Space/AraGemma-Embedding-300m
**Integration effort:** S | **Value for KR:** 3/5

### 5.4 SILMA AI Embeddings

Collection of Matryoshka-based Arabic embeddings from SILMA AI. Lightweight, efficient.

**URL:** https://huggingface.co/collections/silma-ai/arabic-embedding-models
**Integration effort:** S | **Value for KR:** 3/5

### 5.5 Can Embeddings Replace LLM Calls?

| Task | Replace LLM? | Confidence |
|------|-------------|------------|
| Genre clustering | YES -- embeddings excel at similarity | High |
| Binary classification (hadith/Quran) | YES -- with classifier head | High |
| Multi-class genre | PARTIALLY -- for common genres | Medium |
| Author attribution | NO -- requires name reasoning | Low |
| Madhab attribution | NO -- requires argumentative understanding | Low |
| Science scope | PARTIALLY -- pre-filter, LLM confirms | Medium |

**Recommendation:** Use embeddings as FIRST PASS to reduce LLM call volume. Send only ambiguous cases to full LLM consensus.

---

## 6. Arabic-Native LLMs (Potential Consensus Participants)

### 6.1 Jais 2 (70B)

Open-weight Arabic-centric LLM from Inception/MBZUAI/Cerebras. 70B parameters, 600B Arabic tokens. MSA, regional dialects, code-switching. Strong reasoning.

**Access:** Open-weight on HuggingFace (inceptionai/Jais-2-70B-Chat)
**Integration effort:** M | **Value for KR:** 3/5

### 6.2 ALLaM (SDAIA)

Arabic-English LLM from Saudi Arabia National Center for AI. 7B to 70B variants. 5.2T tokens. **Islamic studies is explicitly part of training data** -- potentially most domain-relevant LLM for KR.

**Access:** IBM watsonx and HuggingFace
**Integration effort:** M | **Value for KR:** 3/5

---

## 7. Key Benchmarks

| Benchmark | Size | Key Result | KR Relevance |
|-----------|------|------------|--------------|
| **Noor-Ghateh** | 223K words | CAMeL > Farasa on hadith/jurisprudence | Tool selection |
| **IslamicEval 2025** | 13 teams | Best F1 = 87-90%% span detection | Isnad/citation approach |
| **IslamicMMLU** | Multi-discipline | LLM Islamic knowledge eval | Taxonomy validation |
| **IslamicLegalBench** | 718, 7 madhahib | Best 68%% correct, 21%% hallucination | Validates consensus |
| **ArabicMTEB** | 94 datasets | Swan-Large leads at 62.45 | Embedding selection |

---

## 8. Rejected Alternatives

| Tool | Reason |
|------|--------|
| **spaCy Arabic** | No dedicated models; CAMeL Tools superior |
| **MADAMIRA** | Predecessor to CAMeL; no longer developed |
| **Qutuf** | Less maintained than CAMeL Tools |
| **AraVec** | Word2Vec superseded by GATE/Swan |
| **SAFAR** | Heavyweight Java; CAMeL covers same in Python |
| **Ibn Malik** | Minimally maintained |

---

## 9. Unknowns / Needs Testing

1. **CAMeL Tools on KR fixtures:** Validate morphological accuracy on KR 7 real Arabic scholarly sources.
2. **GATE embedding quality for scholarly text:** Performance on classical Arabic with diacritics is unknown.
3. **Isnad detection model availability:** IslamicEval 2025 systems achieved 87%%+ F1 but weight availability unclear.
4. **Tanzil/Leeds Quran matching precision:** Handling partial quotations and paraphrases needs testing.
5. **OpenITI corpus overlap with Shamela:** If high overlap, OpenITI metadata serves as validation ground truth.
6. **CAMeLBERT-CA fine-tuning:** Zero-shot vs fine-tuned on KR classification tasks.
7. **Jais 2 / ALLaM on classical Arabic:** Both trained on modern Arabic; classical performance needs eval.
8. **GATE dimension vs accuracy tradeoff:** Minimum dimension that preserves scholarly text distinctions.

---

## 10. Recommended Integration Roadmap

### Phase 1: Quick Wins (1-2 sessions)
1. **Tanzil + Quranic Arabic Corpus** -- deterministic Quran citation detector
2. **GATE embeddings** -- embedding-based pre-filtering for Taxonomy

### Phase 2: Core Infrastructure (2-4 sessions)
3. **CAMeL Tools** -- morphological analysis, NER, lemmatization
4. **OpenITI metadata** -- author/work lookup, Passim text reuse

### Phase 3: Model Fine-tuning (4-8 sessions)
5. **CAMeLBERT-CA classifier** -- cheap classification pre-filter
6. **Isnad detection model** -- hadith chain detection

### Phase 4: Evaluation (ongoing)
7. IslamicLegalBench + IslamicMMLU as validation benchmarks
8. Jais 2 / ALLaM as consensus participants

---

## Sources

### Libraries and Tools
- [CAMeL Tools GitHub](https://github.com/CAMeL-Lab/camel_tools) | [PyPI](https://pypi.org/project/camel-tools/)
- [CAMeL Lab NYU Abu Dhabi](https://nyuad.nyu.edu/en/research/faculty-labs-and-projects/computational-approaches-to-modeling-language-lab.html)
- [Farasa QCRI](https://farasa.qcri.org/)
- [AraBERT / AraGPT2](https://github.com/aub-mind/arabert)
- [Passim](https://github.com/dasmiq/passim)
- [Shamela NodeJS API](https://github.com/ragaeeb/shamela)

### Models and Embeddings
- [CAMeLBERT Classical Arabic](https://huggingface.co/CAMeL-Lab/bert-base-arabic-camelbert-ca)
- [GATE Arabic Embeddings](https://huggingface.co/collections/Omartificial-Intelligence-Space/arabic-matryoshka-and-gate-embedding-models)
- [GATE Paper](https://arxiv.org/abs/2505.24581)
- [Swan Embeddings (NAACL 2025)](https://aclanthology.org/2025.findings-naacl.263/)
- [AraGemma-Embedding-300m](https://huggingface.co/Omartificial-Intelligence-Space/AraGemma-Embedding-300m)
- [SILMA AI Embeddings](https://huggingface.co/collections/silma-ai/arabic-embedding-models)
- [Jais 2 70B](https://huggingface.co/inceptionai/Jais-2-70B-Chat)
- [ALLaM Paper](https://arxiv.org/abs/2407.15390)

### Corpora and Datasets
- [OpenITI](https://github.com/openiti) | [Zenodo](https://zenodo.org/records/17767721)
- [KITAB Text Reuse](https://kitab-project.org/methods/text-reuse)
- [Quranic Arabic Corpus](https://corpus.quran.com/)
- [Tanzil](https://tanzil.net/download/)
- [Usul.ai](https://usul.ai/)

### Benchmarks
- [Domain Sensitivity Farasa vs CAMeL (Jan 2026)](https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.418)
- [Noor-Ghateh](https://arxiv.org/abs/2307.09630)
- [IslamicEval 2025](https://www.researchgate.net/publication/397420777)
- [BurhanAI at IslamicEval](https://openreview.net/forum?id=r00SAkJo7o)
- [IslamicMMLU](https://arxiv.org/html/2603.23750)
- [IslamicLegalBench](https://arxiv.org/abs/2602.21226)
- [ArabicMTEB / Swan](https://arxiv.org/abs/2411.01192)

### Conferences
- [ArabicNLP 2025](https://aclanthology.org/2025.arabicnlp-main.0.pdf)
- [AbjadNLP 2026](https://wp.lancs.ac.uk/abjad/)
