# Cross-Pollination Report: Digital Humanities and Scholarly Text Processing

**Date:** 2026-03-28
**Scope:** 8 projects/areas researched, 20+ web searches, tool validation performed
**Goal:** Identify actionable insights for the KR pipeline from peer projects

---

## 1. OpenITI / KITAB Project (Aga Khan University)

### What They Do

OpenITI maintains a corpus of 40,000+ Islamicate text files (7,000+ fully integrated) in a custom plain-text markup format called **mARkdown**. The KITAB project uses this corpus for large-scale text reuse detection.

### Key Technical Choices

**mARkdown Format:** Lightweight markup for pre-modern Arabic texts:
- Structural patterns: headers, section boundaries, page breaks
- Analytical patterns: morphological, semantic, and custom tags

**URI Naming Convention (CTS-compliant):**
- Format: `{HijriDeathYear}{AuthorShuhra}.{BookTitle}.{VersionID}`
- Example: `0414AbuHayyanTawhidi.AkhlaqWazirayn.Shamela0012345-ara1`
- AuthorID = Hijri death year (zero-padded 4 digits) + shuhra
- BookID = distinctive component of book title

**Text Reuse Detection with Passim (v2.0.1, Feb 2024):**
- Texts split into 300-word milestones; Smith-Waterman alignment
- Parameters tuned for classical Arabic; aggregation for boundary-crossing reuse
- Input: JSON Lines (`id`, `text`, `series`); Output: cluster IDs, offsets
- Requires: Java, Python 3, Apache Spark
- GitHub: https://github.com/dasmiq/passim

**openiti Python Package (v0.1.6.1):**
- `pip install openiti` | MIT | Python 3.6+
- `helper.ara`: `normalize_ara_light`, `normalize_ara_heavy`, tokenization, noise filtering
- `helper.yml`: YAML metadata; `new_books`: EPUB/HTML/TEI converters

**Kraken OCR:** Turn-key OCR for Arabic manuscripts, high-nineties accuracy, Apache 2.0
- GitHub: https://github.com/mittagessen/kraken

### What KR Could Adopt

| Insight | Tool/Technique | Effort | Value |
|---------|---------------|--------|-------|
| URI naming for books/authors | OpenITI URI scheme | S | 4 |
| Arabic normalization functions | `openiti.helper.ara` | S | 3 |
| 300-word milestone chunking | Adapt concept | M | 4 |
| Text reuse detection | Passim v2.0.1 | L | 3 |

**Recommendation:** Adopt CTS-compliant `{DeathYear}{Shuhra}.{BookTitle}` for interoperability with 40K+ OpenITI corpus. Use `openiti.helper.ara` for search normalization (never on primary text).

### What KR Does That They Do Not

- Multi-model consensus for classification (OpenITI uses manual annotation)
- LLM-based scholarly metadata extraction (OpenITI relies on crowd-sourced metadata)
- Structured pipeline with formal engine contracts (OpenITI uses ad-hoc scripts)

---

## 2. Perseus Digital Library (Tufts University)

### Key Technical Choices

**Canonical Text Services (CTS) Protocol:**
- URN format: `urn:cts:{namespace}:{textgroup}.{work}.{version}:{passage}`
- Citation at any granularity; precise passage retrieval across editions
- Content-encoded (semantics over layout); each layer independently addressable

| Insight | Tool/Technique | Effort | Value |
|---------|---------------|--------|-------|
| CTS URN passage citation | CTS specification | M | 5 |
| Content-over-form encoding | Architecture pattern | S | 4 |
| Multi-layer addressability | Architecture pattern | M | 5 |

**Recommendation:** Adopt CTS-like citation: `kr:0769IbnAqil.SharhAlfiyyah:v1.muqaddimah.p3`

---

## 3. Text Encoding Initiative (TEI)

### Should KR Adopt TEI-XML?

**No for internal representation.** TEI is verbose, requires specialized tooling. Pydantic+JSON is better for pipeline.

**Yes for conceptual models:** Critical apparatus (variant readings), commentary layers (base-text vs commentary).

**SARIT Commentary Encoding:** `<quote type="base-text">` pattern directly addresses matn-sharh-hashiyah layering.

| Insight | Tool/Technique | Effort | Value |
|---------|---------------|--------|-------|
| SARIT base-text encoding | `layer_type` field | S | 4 |
| Critical apparatus concepts | Architecture pattern | S | 3 |

---

## 4. Quranic Arabic Corpus (Leeds University)

77,430 words annotated: POS, morphology, syntax, semantics. 98.7% accuracy. Traditional Arabic grammar framework.
- 100+ sub-tags: gender, number, person, aspect, mood, voice, case, state
- https://corpus.quran.com/ | https://corpus.quran.com/download/

| Insight | Tool/Technique | Effort | Value |
|---------|---------------|--------|-------|
| Morphological data for citation matching | Corpus download | S | 4 |
| POS tag set for classical Arabic | NER reference | S | 3 |

---

## 5. CAMeL Tools (NYU Abu Dhabi)

Most comprehensive open-source Python NLP toolkit for Arabic.

**CamelMorph MSA (2024):** 100K+ lemmas, 1.45B analyses, 535M diacritizations.

**Classical Arabic performance (2025):**
- Token accuracy: Hadith 0.81, Quranic 0.80
- Stem segmentation: 0.601 (significant weakness)
- `pip install camel-tools` | MIT | https://github.com/CAMeL-Lab/camel_tools

| Insight | Tool/Technique | Effort | Value |
|---------|---------------|--------|-------|
| Morphological disambiguation | `camel_tools.disambig` | M | 4 |
| NER for person names | `camel_tools.ner` | M | 4 |
| Tokenization | `camel_tools.tokenizers` | M | 3 |

**Caveat:** Stem accuracy 0.601 on fiqh texts. Use as one signal, not ground truth.

---

## 6. Tanzil.net / Quran APIs

**Tanzil (v1.1):** Plain text, XML, JSON. UTF-8. https://tanzil.net/download/
**alquran.cloud:** Free API. `/v1/ayah/{ref}`, `/v1/search/{keyword}`
**DQQ (IEEE):** Quran quotation detection algorithm. LSTM: 99.98% accuracy.

| Insight | Tool/Technique | Effort | Value |
|---------|---------------|--------|-------|
| Tanzil as citation reference | Download + n-gram index | S | 5 |
| alquran.cloud for verification | HTTP client | S | 4 |
| nuqayah/quran-text Unicode | Git submodule | S | 4 |

**Recommendation:** Build local n-gram index from Tanzil for deterministic citation detection. Zero API cost.

---

## 7. Usul.ai / Shamela Infrastructure

**usul-data (GitHub: seemorg/usul-data, MIT):**
- `authors.json`: Hijri death years, multilingual names (14 languages), bios
- `books.json`: IDs, multilingual titles, version sources
- `genres.json`: Taxonomy (tafsir, creeds, jurisprudence)
- `locations.json` + `regions.json`: Geographic data

| Insight | Tool/Technique | Effort | Value |
|---------|---------------|--------|-------|
| usul-data scholar authority | JSON import | S | 5 |
| Genre taxonomy validation | Cross-reference | S | 4 |
| Book metadata enrichment | JSON merge | S | 4 |

**Highest-value item:** `authors.json` is the single best external resource for scholar_authority validation.

---

## 8. Academic Papers (2023-2026)

**IslamicLegalBench (arXiv Feb 2025):** 718 instances, 7 schools. Best model: 68% correct, 21% hallucination. Validates multi-model consensus.

**CANERCorpus:** 258K tokens, 7000+ hadith, 20 entity types. BERT+CRF F1=94.68.
- GitHub: https://github.com/RamziSalah/Classical-Arabic-Named-Entity-Recognition-Corpus

**Domain Sensitivity (JOHD 2025):** All morphological analyzers drop on classical Arabic. Stem segmentation weakest (0.55-0.60).

---

## Consolidated Recommendations (Priority Order)

### Immediate (S, This Week)

1. **Download usul-data authors.json** -- Scholar authority validation. MIT. https://github.com/seemorg/usul-data
2. **Download Tanzil Quran plain text** -- N-gram index for citation detection. https://tanzil.net/download/
3. **Adopt OpenITI URI naming** -- `{HijriDeathYear}{Shuhra}.{BookTitle}`. http://openiti.org/documentation/
4. **Install openiti package** -- `pip install openiti` for search normalization
5. **Download usul-data genres.json** -- Genre taxonomy cross-reference

### Medium-Term (M, Next Sprint)

6. **CTS-like passage citation scheme** -- Human-readable excerpt identifiers
7. **CAMeL Tools NER** -- `pip install camel-tools` (secondary signal)
8. **CANERCorpus entity types** -- 20-category Islamic NER schema
9. **Quranic citation detector** -- Deterministic, n-gram-based, zero cost
10. **SARIT-style layer encoding** -- Explicit layer_type for sharh/hashiyah

### Long-Term (L, Future)

11. **Passim for text reuse** -- When corpus exceeds 5,000 books
12. **Fine-tune NER on CANERCorpus** -- BERT+CRF training
13. **TEI XML export** -- Digital humanities interoperability

---

## Rejected Alternatives

| Tool/Approach | Why Not |
|---------------|--------|
| TEI XML internal format | Verbose; Pydantic+JSON faster for pipeline |
| Farasa analyzer | Lowest accuracy (0.76) on Quranic text |
| ALP analyzer | Less maintained than CAMeL |
| HathiTrust Arabic OCR | Poor quality, gibberish common |
| Shamela v4 API | Requires API key; usul-data is free |
| Full Passim now | 274 books too small for Spark infra |

---

## Unknowns / Needs Testing

1. **usul-data author coverage** -- Do KR 7 fixture authors appear in dataset?
2. **Tanzil n-gram precision/recall** -- Test on real excerpts with Quranic citations
3. **CAMeL on KR fixtures** -- Speed, accuracy, scholar name detection
4. **openiti vs KR normalization** -- Consistency check
5. **CTS URN + Shamela ID mapping** -- Bidirectional compatibility?
6. **IslamicLegalBench on consensus pair** -- Command A + Opus hallucination rates

---

## Key Architectural Insight

Three independent projects converge on **stable, human-readable, hierarchical text identifiers**:

- OpenITI: `{DeathYear}{Author}.{Book}.{Version}`
- Perseus: `urn:cts:{namespace}:{group}.{work}.{version}:{passage}`
- Usul.ai: structured IDs with Hijri dates and transliterations

KR should adopt this NOW. A teaching unit citing "excerpt #a7f3e2b1" is useless. One citing "kr:0769IbnAqil.SharhAlfiyyah:v1.muqaddimah.3" is a proper scholarly reference.

This is not optional -- it is a prerequisite for the knowledge product being useful as actual scholarly reference material.

---

## Sources

### Projects and Tools
- [OpenITI](https://maximromanov.github.io/OpenITI/) | [mARkdown](https://maximromanov.github.io/mARkdown/) | [PyPI](https://pypi.org/project/openiti/) | [GitHub](https://github.com/openiti)
- [KITAB Text Reuse](https://kitab-project.org/methods/text-reuse) | [Zenodo](https://zenodo.org/records/11501559)
- [Passim](https://github.com/dasmiq/passim) | [Tutorial](https://programminghistorian.org/en/lessons/detecting-text-reuse-with-passim)
- [Perseus](https://www.perseus.tufts.edu/hopper/) | [CTS API](https://sites.tufts.edu/perseusupdates/beta-features/perseus-cts-api/) | [CTS URN](https://sites.tufts.edu/perseusupdates/2021/01/05/what-is-a-cts-urn/)
- [TEI Guidelines](https://tei-c.org/guidelines/) | [Critical Apparatus](https://tei-c.org/release/doc/tei-p5-doc/en/html/TC.html)
- [SARIT Guidelines](https://sarit.indology.info/sarit-pm/docs/encoding-guidelines-full.html) | [Commentary](https://journals.openedition.org/jtei/3324)
- [Quranic Arabic Corpus](https://corpus.quran.com/) | [Download](https://corpus.quran.com/download/)
- [CAMeL Tools](https://github.com/CAMeL-Lab/camel_tools) | [CamelMorph](https://aclanthology.org/2024.lrec-main.240/)
- [Tanzil](https://tanzil.net/download/) | [nuqayah/quran-text](https://github.com/nuqayah/quran-text) | [alquran.cloud](https://alquran.cloud/api)
- [Usul.ai](https://usul.ai/) | [usul-data](https://github.com/seemorg/usul-data)
- [Kraken OCR](https://github.com/mittagessen/kraken)

### Academic Papers
- [Domain Sensitivity (JOHD 2025)](https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.418)
- [IslamicLegalBench](https://arxiv.org/abs/2602.21226) | [IslamicMMLU](https://arxiv.org/html/2603.23750)
- [CANERCorpus](https://github.com/RamziSalah/Classical-Arabic-Named-Entity-Recognition-Corpus) | [HuggingFace](https://huggingface.co/datasets/caner)
- [Arabic NLP Review (MDPI 2025)](https://www.mdpi.com/2073-431X/14/11/497)
- [DQQ Quran Detection (IEEE)](https://ieeexplore.ieee.org/abstract/document/9062853/)
- [Arabic OCR Advances (arXiv 2024)](https://arxiv.org/abs/2402.10943)
- [AbjadNLP 2026](https://wp.lancs.ac.uk/abjad/)
