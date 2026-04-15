# Data modeling for a digital Islamic scholarly library

**A FRBR-aligned data model can handle the full complexity of Islamic bibliographic relationships—layered commentaries, multi-volume sets, competing critical editions, and composite manuscripts—but only with significant adaptations for non-Western scholarly traditions.** The standard Western bibliographic models (FRBR, BIBFRAME, MARC) were designed primarily around individual-authored print monographs, and they struggle with the recursive commentary chains (sharḥ → ḥāshiya → taʿlīqa), multiple transmission versions (riwāyāt), posthumous compilations, and composite manuscripts (majmūʿāt) that define Islamic intellectual heritage. This report synthesizes findings from IFLA standards, digital repository architectures, classical Islamic bibliography, and practical collection management patterns into a unified framework for modeling an Islamic scholarly library's data pipeline.

---

## The FRBR hierarchy and where Islamic texts break it

The IFLA Functional Requirements for Bibliographic Records (1998) established four entities that remain foundational: **Work** (a distinct intellectual creation), **Expression** (a specific realization of that work in signs—text, translation, critical edition), **Manifestation** (a physical or digital embodiment sharing production characteristics), and **Item** (a single exemplar). The cardinalities are strict: each Expression realizes exactly one Work; each Item exemplifies exactly one Manifestation. The crucial exception is the **many-to-many relationship between Expression and Manifestation**, which enables aggregates—multiple distinct Expressions embodied in a single Manifestation.

For a work like Ṣaḥīḥ al-Bukhārī, this maps cleanly at first glance. The hadith compilation itself is the Work; the Arabic text as transmitted by al-Firabrī constitutes one Expression; Muḥsin Khan's English translation is another Expression; the Dār Ṭawq al-Najāh 1422 AH print is a Manifestation; a specific library copy with stamps and marginalia is an Item. A critical edition (taḥqīq) by Muṣṭafā Dīb al-Bughā, which involves collating manuscripts, selecting variant readings, and adding apparatus criticus, constitutes a **new Expression** because it modifies the intellectual content of the text. If the same taḥqīq text is merely reprinted by a different publisher with new typesetting but identical content, that is only a new Manifestation.

The model breaks down in several places critical for Islamic texts. **Multiple riwāyāt** (transmission versions), as with al-Muwaṭṭaʾ of Imām Mālik—which has over 20 famous transmissions, each with different hadith counts, different ordering, and different content—cannot simply be modeled as different Expressions of one Work. Yaḥyā ibn Yaḥyā al-Laythī's version contains approximately **1,942 hadith**, while Abū Muṣʿab al-Zuhrī's contains **3,069 narrations**. Muḥammad al-Shaybānī's version was so heavily edited—excluding Mālik's opinions, adding Abū Ḥanīfa's views, restructuring chapters—that it is typically called "the Muwaṭṭaʾ of Muḥammad" rather than a transmission of Mālik. FRBR's own guidance states that modification involving "a significant degree of independent intellectual effort" creates a new Work, but the boundary is culturally variable and FRBR itself acknowledges it "may be viewed differently from one culture to another."

The **IFLA Library Reference Model (LRM)**, published in 2017, consolidated FRBR with two related models (FRAD for authority data, FRSAD for subject authority) into a single coherent framework. It preserved the WEMI hierarchy but added several important features: a **Res** superclass from which all entities inherit; an **Agent** superclass unifying Person and Collective Agent; a **Nomen** entity for modeling appellations as first-class objects (critical for Arabic names with multiple transliteration forms); **Place** and **Time-span** as full entities; a fifth user task, **Explore**, emphasizing navigation through relationships; and formalized Work-to-Work relationships including *has part / is part of*, *is a transformation of*, *accompanies / complements*, and *is inspiration for / is inspired by*. The many-to-many expression-manifestation relationship was retained, and the 2011 IFLA Working Group on Aggregates recommendations were formally incorporated.

---

## Three types of aggregates and the commentary problem

The IFLA Working Group on Aggregates (final report 2011) addressed what Sally McCallum called "the biggest problem of inconsistency" in FRBR. They identified three aggregate types, all critical for Islamic scholarly texts.

**Collection aggregates** bundle distinct expressions of the same type: anthologies, collected works, journals. Majmūʿ Fatāwā Ibn Taymiyya—37 volumes of fatwas compiled posthumously by ʿAbd al-Raḥmān ibn Muḥammad ibn Qāsim—is a collection aggregate. Each individual fatwa is an independent Work by Ibn Taymiyya. The compilation arrangement constitutes a separate **aggregating work** attributed to Ibn Qāsim. The complete 37-volume set is one Manifestation, and individual physical volumes are component parts of a single Item.

**Augmentation aggregates** add content to a base expression: illustrations, forewords, footnotes, and critically for Islamic texts, **commentaries (شرح)**. When Fatḥ al-Bārī by Ibn Ḥajar al-ʿAsqalānī is published alongside the text of Ṣaḥīḥ al-Bukhārī, the resulting publication is an augmentation aggregate embodying the Expression of al-Bukhārī's Work (the hadith text), the Expression of Ibn Ḥajar's Work (the commentary), and the Expression of the aggregating Work (the particular editorial arrangement). A taḥqīq edition's scholarly apparatus—footnotes, variant readings, introductions—can similarly be modeled as augmenting content constituting its own Work.

**Parallel expression aggregates** embody two or more expressions of the same work together, such as bilingual editions with Arabic text and English translation side by side.

The deepest challenge lies in the **recursive commentary tradition**. Consider the chain: Matn Abī Shujāʿ (an elementary Shāfiʿī fiqh primer) → Fatḥ al-Qarīb al-Mujīb by Ibn Qāsim al-Ghazzī (a sharḥ) → Ḥāshiyat al-Bājūrī (a super-commentary on the sharḥ). Each layer is an independent Work that derives from and accompanies its predecessor. In Ḥanafī fiqh, the chain runs even deeper: Tanwīr al-Abṣār by al-Tumurtāshī (matn) → Durr al-Mukhtār by al-Ḥaṣkafī (sharḥ) → Radd al-Muḥtār by Ibn ʿĀbidīn (ḥāshiya) → Qurrat al-ʿUyūn al-Akhyār by Ibn ʿĀbidīn's son (takmila, a continuation of the unfinished ḥāshiya). A data model must express these **derives-from relationships as a directed acyclic graph** with typed edges (sharḥ, ḥāshiya, mukhtaṣar, talkhīṣ, naẓm, takmila), not a simple tree.

---

## How digital repository systems model complex objects

Six major repository systems offer contrasting architectural approaches relevant to this problem.

**Fedora Repository** (now at version 6.x) provides the most flexible foundation. Its core model consists of LDP Containers (holding RDF metadata and child resources) and LDP Non-RDF Sources (binaries with descriptions). All relationships are expressed as RDF triples, enabling arbitrary semantic graphs—exactly what Islamic bibliographic relationship networks require. Fedora 6 uses the **Oxford Common File Layout (OCFL)** for storage, with forward-delta versioning that stores only changed files in new version directories and an `inventory.json` tracking all versions. This supports the supersession pattern where a better digital scan replaces an earlier one while preserving complete provenance.

**Samvera/Hyrax**, built on Fedora, adds the **Portland Common Data Model (PCDM)** with three classes: Collection, Object, and File. The Hydra::Works extension adds Work and FileSet layers. Critically, PCDM supports **arbitrary-depth nesting** via `pcdm:hasMember`—a top-level Work can contain child Works (volumes), each containing FileSets (page images and OCR). This maps naturally to Islamic multi-volume works where a 37-volume fatwa collection needs hierarchical decomposition.

**DSpace** uses a flatter hierarchy (Community → Collection → Item → Bundle → Bitstream) with linear versioning that creates a new Item for each version, sharing bitstreams via copy-on-write semantics. Its simplicity becomes a limitation for complex hierarchical objects; DSpace 7's Configurable Entities feature partially addresses this by allowing typed relationships between Items.

**HathiTrust** takes a pragmatic MARC-centric approach: a bibliographic Record contains multiple Items (scanned volumes), each described by a METS structural metadata document. Their **Zephir** system manages bibliographic metadata across contributing institutions, using a scoring algorithm to select the "best" record when multiple institutions deposit records for the same title—a useful pattern for selecting among competing taḥqīq editions.

**OpenITI/KITAB** offers the most directly relevant model for Islamic texts. Their **CTS-compliant URI scheme** encodes three levels: AuthorID (`0748Dhahabi` = al-Dhahabī, d. 748 AH), BookID (`0748Dhahabi.TarikhIslam`), and VersionID (`0748Dhahabi.TarikhIslam.Shamela0035100-ara1`). YAML metadata files exist at all three levels. Multiple versions of the same text coexist as separate files within one book folder, with a `pri`/`sec` status field designating the primary version. Approximately **45% of their ~2-billion-word corpus** comes from Shamela, with other sources including the Shia Online Library and al-Jāmiʿ al-Kabīr. This three-level separation of author, abstract work, and specific digital version maps directly to the pipeline's need to distinguish submissions (specific digital files) from works (abstract intellectual creations).

**Shamela** (المكتبة الشاملة) uses the simplest architecture: each book is a Microsoft Access `.mdb` database file renamed with a `.bok` extension, containing a `title` table (hierarchical table of contents) and a `book` table (page-by-page text content with volume/page numbers matching printed editions). Each book's metadata card records author, editor (محقق), publisher, edition number, year, and number of volumes (أجزاء). Multi-volume works are single entries with volume enumeration tracked internally. Commentary-base text relationships are implicit through naming conventions and category placement rather than explicit linked metadata—a significant limitation that a new system should overcome.

---

## The Islamic bibliographic tradition demands richer relationship types

Classical Islamic bibliography established sophisticated systems for organizing knowledge centuries before Western library science. Ibn al-Nadīm's al-Fihrist (987 CE) cataloged approximately **10,000 books and 3,500 authors** organized by subject into ten maqālāt (discourses), each subdivided by genre. Ḥājjī Khalīfa's Kashf al-Ẓunūn (completed ~1652) advanced the practice dramatically, cataloging **15,000 titles and 9,500 authors** alphabetically by title, with each entry followed by related commentaries (shurūḥ), abridgments (mukhtaṣarāt), and glosses (ḥawāshī). This explicit tracking of derivative relationships is precisely what modern systems lack.

A robust data model for Islamic texts must capture at minimum eight distinct relationship types between works:

- **شرح (sharḥ)**: Commentary explaining and elaborating a base text (matn)
- **حاشية (ḥāshiya)**: Super-commentary written on a sharḥ, often in the margins
- **مختصر (mukhtaṣar)**: Abridgment retaining essential content
- **تلخيص (talkhīṣ)**: Interpretive summary
- **نظم (naẓm)**: Versification of prose for memorization (e.g., Alfiyyat Ibn Mālik for Arabic grammar)
- **تحقيق (taḥqīq)**: Critical edition with scholarly apparatus
- **تكملة (takmila)**: Continuation of an unfinished work
- **تعليقة (taʿlīqa)**: Marginal notes and annotations

The distinction between **logical divisions** (kitāb/bāb/faṣl—book/chapter/section within a work's intellectual structure) and **physical divisions** (juzʾ/mujallad—part/bound volume in a specific publication) is essential. Ṣaḥīḥ al-Bukhārī contains **97 kutub** organized by fiqh topic with approximately **3,450 abwāb**, but is published in varying physical formats: 9 volumes in the Khan translation, 30 equal parts like the Quran's ajzāʾ in other editions, or other configurations. A data model must track both hierarchies independently.

The **fahras/thabt/barnāmaj** tradition—scholars' catalogs of their teachers, books studied, and chains of transmission (asānīd)—created a provenance-tracking system centuries before PREMIS. The ijāza (certificate of authorization to transmit a text) embedded bibliographic records within the transmission chain itself, serving as quality control for textual authenticity. While modern digital libraries have not yet captured this rich provenance layer, a pipeline processing Islamic texts should preserve transmission chain metadata where available.

---

## Collection management patterns for incremental acquisition and holdings

Libraries handling multi-volume Islamic works arriving incrementally over time use the **MARC Format for Holdings Data (MFHD)** with field 866 tracking which volumes are held. The encoding `866 41 $a v.1-v.5,v.7,v.10-v.12` expresses gaps with commas between held ranges. Coded holdings in fields 853/863 enable algorithmic compression and expansion, with the `$w` break indicator value "g" marking published volumes lacking in the collection. The ANSI/NISO Z39.71-2006 standard governs formulation of these statements.

For **edition management and supersession**, MARC linking entry fields 760–787 encode three categories of bibliographic relationships: chronological (fields 780/785 for predecessors/successors), horizontal (fields 775/776 for other editions and physical forms), and vertical (fields 773/774 for whole-to-part relationships). Field 780 with second indicator values encodes subtypes like "Continues," "Formed by merger of," "Absorbed," while field 785 encodes "Continued by," "Absorbed by," "Split into," and "Merged with ... to form." These patterns translate directly to database relationship types.

**Analytics**—separate catalog records for parts of a larger work—use MARC field 773 (child record pointing to parent) and field 774 (parent record listing constituents). When a library holds both Majmūʿ Fatāwā Ibn Taymiyya as a complete set AND individual standalone editions of treatises within it, the cover record's 774 fields list each contained work, while each analytic record's 773 field points back to the cover record. This bidirectional linking pattern must be preserved in any digital repository model.

**Duplicate detection** for Arabic texts faces unique challenges: ALA-LC romanization of Arabic requires modeling phonology, morphology, and semantics, and accuracy reaches only about **89.3%** at the exact-word level. Short vowels are typically unwritten, creating ambiguity; author names have inconsistent forms across records. OCLC's 2023–2025 AI-powered deduplication initiative has extended machine learning models to handle all formats, languages, and scripts, testing **500,000 record pairs** in February 2025. For the pipeline, deduplication should combine ISBN/OCLC number matching with Arabic-aware string similarity (Levenshtein distance on normalized Arabic text, ignoring diacritics and hamza variants).

---

## The OAIS lifecycle maps directly to a processing pipeline

The **Open Archival Information System** (ISO 14721, most recently revised as ISO 14721:2025) defines three information package types that map naturally to a multi-engine processing pipeline. A **Submission Information Package (SIP)** arrives from a producer—this corresponds to a raw book submission entering the pipeline. The **Archival Information Package (AIP)** is the complete preserved object with full metadata—the processed, OCR'd, cataloged digital book stored in the repository. The **Dissemination Information Package (DIP)** is what consumers access—the searchable, browsable text delivered through the library interface.

OAIS defines six functional entities: **Ingest** (validates SIPs and generates AIPs), **Archival Storage** (stores and maintains AIPs), **Data Management** (maintains descriptive metadata indexes), **Administration** (manages policies and operations), **Preservation Planning** (monitors threats and develops preservation strategies), and **Access** (generates DIPs for consumers). This maps to the pipeline's stages: book submission → multi-engine processing → metadata extraction → storage → indexing → access.

**PREMIS** (Preservation Metadata: Implementation Strategies, Version 3.0) provides the standard for tracking preservation actions through five entities: Intellectual Entity, Object (with File, Bitstream, and Representation subtypes), **Event** (every preservation action with timestamp, agent, and outcome), Agent, and Rights. When a TIFF page scan is converted to JPEG2000, PREMIS records the migration event, the software agent used, the source and outcome objects, and the relationship `isDerivedFrom` linking the new file to the original. For a pipeline replacing a lower-quality OCR result with output from a better engine, PREMIS events maintain the complete provenance chain.

Bibliographic records themselves traverse a state machine from **CIP/pre-publication** (provisional skeleton record) through **draft/in-process** (imported but incomplete), **complete** (fully cataloged with authority-controlled headings), potentially to **suppressed** (hidden from public catalog but retained) or **withdrawn** (logically or physically removed). In Koha, management tags control publication state; in Evergreen, the `biblio.record_entry` table uses `active` and `deleted` boolean fields with soft deletion to `deletedbiblio` backup tables.

---

## Entity-relationship patterns for the data model

Four hierarchical data storage approaches suit the part-of relationships in Islamic bibliographic data. **Adjacency list** (self-referencing foreign key with `parent_id`) is simplest and handles frequent modifications well; modern PostgreSQL supports recursive CTEs for traversal. **Materialized path** (storing the full ancestry path as a string like `/work/volume/chapter/`) enables efficient ancestor/descendant lookups without recursion; PostgreSQL's `ltree` extension provides specialized operators and GiST indexing. **Closure table** (a separate table storing every ancestor-descendant pair with depth) offers the best balance of read and write performance for complex hierarchies. **Nested set** (left/right integer boundary values) excels at read-heavy stable hierarchies but is expensive for inserts—suitable for classification schemes but not for actively growing collections.

For derivation relationships, a **junction table with typed edges** models the directed acyclic graph of Islamic text relationships:

```sql
CREATE TABLE work_relationship (
    source_work_id  INT REFERENCES work(id),
    related_work_id INT REFERENCES work(id),
    relationship_type VARCHAR(50), -- 'sharh','hashiya','mukhtasar',
                                   -- 'talkhis','nazm','tahqiq','takmila'
    PRIMARY KEY (source_work_id, related_work_id, relationship_type)
);
```

For supersession, Martin Fowler's **temporal object pattern** provides the cleanest model: a **Continuity** entity (the enduring work identity) paired with **Version** entities (specific editions with `effective_from` and `effective_to` dates). Other entities reference the Continuity, never individual versions, ensuring stable identifiers. A `NULL` value for `effective_to` marks the current version. This pattern accommodates the common scenario where Majmūʿ Fatāwā Ibn Taymiyya has been compressed from 37 volumes into 20-volume editions (Dār Ibn Ḥazm; Dār al-Kutub al-ʿIlmiyya) that retain original volume numbering in margins for citation compatibility—different Manifestations that must link back to the same abstract work Continuity.

**BIBFRAME 2.0** (Library of Congress, 2016) simplifies FRBR to three classes: `bf:Work` (conceptual essence), `bf:Instance` (material embodiment, collapsing Expression and Manifestation), and `bf:Item` (specific copy). It provides relationship properties including `bf:hasDerivative`/`bf:derivativeOf`, `bf:translationOf`, `bf:supersedes`/`bf:supersededBy`, `bf:hasPart`/`bf:partOf`, and `bf:hasExpression`/`bf:expressionOf`. This three-level approach may be more practical than FRBR's four levels for implementation, while the expression-level properties remain available when needed.

---

## Practical schema recommendations for the pipeline

Drawing together all findings, a data model for this Islamic scholarly library pipeline should incorporate these structural elements:

**Core entities** should follow a modified FRBR/BIBFRAME hierarchy with five levels: **Submission** (the raw digital object entering the pipeline, analogous to an OAIS SIP), **Source** (the abstract intellectual work, corresponding to FRBR Work), **Edition** (a specific realization—taḥqīq, riwāya, or translation—corresponding to FRBR Expression), **Publication** (a specific physical or digital embodiment, corresponding to FRBR Manifestation), and **Volume** (a component part within a multi-volume Publication, tracked with both logical position and physical enumeration).

**Relationship tables** should use typed edges in a junction table to model the full range of Islamic text relationships (sharḥ, ḥāshiya, mukhtaṣar, talkhīṣ, naẓm, taḥqīq, takmila, taʿlīqa) as well as standard bibliographic relationships (translation, continuation, supersession, part-of). Each relationship should carry directionality and be queryable in both directions.

**Holdings tracking** should use a completeness model inspired by MARC 866, recording which volumes of a multi-volume work are held as a structured set (not just a count), enabling queries like "which works are incomplete" and "what volumes are missing." A status field per volume entry should track the OAIS-aligned lifecycle: `submitted` → `processing` → `processed` → `verified` → `superseded` → `withdrawn`.

**The OpenITI URI scheme** (`{DeathYear}{Shuhra}.{TitleCamelCase}.{SourceNumber}-{lang}{edition}`) provides an excellent model for persistent identifiers that encode author, work, and version provenance at the URI level. Adopting a compatible scheme would enable interoperability with the largest existing Islamicate text corpus.

The deepest lesson from this research is that **no existing system fully models Islamic bibliographic relationships**. Shamela's Access databases are pragmatic but structurally impoverished. OpenITI's CTS URIs elegantly separate author, work, and version but do not model commentary chains or hierarchical text structures. FRBR/LRM provides the richest conceptual framework but was designed for Western print traditions and struggles with transmission versions, composite manuscripts, and the recursive commentary networks that define the Islamic scholarly corpus. The data model for this library will need to synthesize the best elements of all these approaches: FRBR's conceptual rigor, OpenITI's identification scheme, PCDM's arbitrary-depth nesting, PREMIS's provenance tracking, and domain-specific relationship types drawn from the millennium-old Islamic bibliographic tradition of al-Fihrist and Kashf al-Ẓunūn.

## Conclusion

Building a data model for an Islamic scholarly library requires moving beyond any single existing standard. The FRBR/LRM Work-Expression-Manifestation-Item hierarchy provides a sound conceptual foundation, but **the critical innovation must be a richly typed relationship graph** connecting works through sharḥ, ḥāshiya, mukhtaṣar, and seven other Islamic-specific derivation types that Western standards never anticipated. Multi-volume works demand dual-hierarchy tracking—logical divisions (kitāb/bāb/faṣl) separate from physical divisions (juzʾ/mujallad)—with MARC 866-style gap-aware holdings for progressive completeness. The OAIS SIP→AIP→DIP pipeline, combined with PREMIS event logging, provides the lifecycle and provenance framework for a multi-engine processing system where OCR results, metadata extractions, and digital scans are versioned and superseded over time. OpenITI's three-level URI scheme offers the most practical identification model for Islamicate texts, while Samvera/PCDM's nested object membership provides the architectural pattern for arbitrary-depth hierarchical containment. The resulting system would be the first to formally model what Ḥājjī Khalīfa achieved informally in 1652: a comprehensive index where every commentary, abridgment, and gloss is explicitly linked to its source text in a navigable scholarly network.