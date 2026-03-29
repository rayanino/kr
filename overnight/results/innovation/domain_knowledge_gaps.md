# Domain Knowledge Gaps in the KR Pipeline

**Date:** 2026-03-28
**Scope:** Research-only analysis of what the pipeline SHOULD know about but currently does not handle or under-specifies.
**Method:** Cross-referenced current domain knowledge (arabic-scholarly-conventions.md, islamic-sciences-classification SKILL, scholarly-attribution SKILL, quranic-text-handling SKILL, excerpting SPEC sections 4-7) against real-world Islamic scholarly text patterns discovered through web research and domain expertise.

---

## 1. Science-Specific Processing Differences

### 1.1 Fiqh: Khilaf (Disagreement) Passage Structure

**What the pipeline knows:** The excerpting SPEC section 6.1 (DP-1 through DP-6) handles position + refutation pairs, and the islamic-sciences-classification SKILL documents fiqh terminology. The StructuralFormat enum includes `TABULAR_KHILAF`.

**What the pipeline misses:**

- **Structured multi-opinion passages.** Real fiqh khilaf is not always a simple position-refutation pair. Classical works like al-Mughni or al-Majmu' present 3-5 opinions in a stereotyped sequence: (a) the author's madhab position, (b) each opposing position with its proponent and evidence, (c) tarjih (preponderance) with the author's reasoning. The SPEC's DP-1 models binary (position + refutation) but not multi-opinion chains. If a 4-opinion passage is split so that opinions 2 and 3 become separate teaching units, the tarjih in opinion 4 appears decontextualized.

- **The "fa-in qeela / qulna" dialectical pattern** (فإن قيل ... قلنا). This pattern can nest deeply: an opponent raises objection A, the author responds, the opponent counters with objection B (a refinement of A), the author responds again. The SPEC's DP-2 covers one-level Q&A, but not nested dialectical exchanges spanning 5+ turns. Splitting mid-chain loses the argumentative progression.

- **Legal maxim (qa'ida) instantiation patterns.** In qawa'id fiqhiyyah texts, the structure is: state the maxim (e.g., "اليقين لا يزول بالشك"), then list 5-20 furu' (applications). Each far' is a mini teaching unit, but it depends on the maxim for intelligibility. The SPEC does not address maxim-application grouping.

**Risk level:** HIGH for decontextualization in comparative fiqh texts.
**Engines affected:** Excerpting (Phase 2b grouping, section 6.1).
**Recommended action:** Add khilaf-specific grouping rules to SPEC section 6 as a new subsection (section 6.7). Add test fixture from mughni_comparative for multi-opinion passages.

---

### 1.2 Tafsir: Verse-by-Verse vs Thematic Commentary Structure

**What the pipeline knows:** The islamic-sciences-classification SKILL documents tafsir structure and the quranic-text-handling SKILL covers detection and preservation. The SPEC section 6.3 handles Quran evidence extraction.

**What the pipeline misses:**

- **Verse-by-verse vs thematic tafsir have fundamentally different excerpt boundaries.** In verse-by-verse tafsir (e.g., Tafsir al-Tabari, Tafsir Ibn Kathir), the natural teaching unit is the discussion of one ayah or ayah group. In thematic tafsir (e.g., al-Tahrir wa-l-Tanwir), the natural unit is the thematic discussion, which may span multiple disconnected ayahs. The SPEC does not distinguish these two structural patterns.

- **Tafsir bil-ma'thur (narration-based) creates isnad-heavy passages.** In Tafsir al-Tabari, a single ayah's discussion contains 10-30 isnads, each introducing a companion or tabi'i opinion. The SPEC section 6.3 says isnads stay as atomic units, but the teaching-unit question is different: is each narrated opinion a separate teaching unit, or is the entire ayah discussion one unit? Neither answer is universally correct -- it depends on the tafsir's purpose.

- **Intertextual tafsir references.** Mufassirun routinely reference other tafsir works: "وقد ذكر الطبري في تفسيره" or "خلافا لما ذهب إليه الزمخشري في الكشاف". These cross-tafsir references create a web of dependencies that the excerpting engine's IR-1 (intra-source) and IR-2 (epithet resolution) do not handle because they are inter-source. The excerpt mentions al-Zamakhshari's position but the reader cannot follow the reference.

- **Qira'at (variant reading) discussions in tafsir.** When a mufassir discusses variant readings of a verse, the discussion involves multiple valid Quranic texts side by side. The pipeline's quranic-text-handling SKILL correctly preserves variant readings (section 2.3), but the excerpting engine has no mechanism to tag "this teaching unit contains a qira'at discussion" versus "this teaching unit cites a single reading as evidence." This distinction matters for taxonomy (linking the excerpt to the correct qira'at tradition).

**Risk level:** MEDIUM. Verse-by-verse tafsir is well-structured enough that the LLM will likely produce reasonable groupings. Thematic tafsir and qira'at discussions are higher risk.
**Engines affected:** Excerpting (Phase 2b), Taxonomy (cross-referencing).
**Recommended action:** Add SPEC section 6.8 for tafsir-specific processing. Add a tafsir test fixture. Research further whether Phase 2 LLM naturally handles verse-by-verse structure without explicit guidance.

---

### 1.3 Hadith: Isnad-Matn Separation and Collection-Specific Patterns

**What the pipeline knows:** The arabic-scholarly-conventions.md covers transmission formulas. The SPEC section 6.3 handles evidence and hadith, and the islamic-sciences-classification SKILL has detailed hadith processing notes. The Phase 2a classification includes `evidence_hadith` and `narration` segment types.

**What the pipeline misses:**

- **Collection-specific structural patterns.** Major hadith collections have distinctive structural conventions that affect excerpting:
  - **Sahih al-Bukhari** uses chapter-heading tarajim (تراجم الأبواب) that embed the compiler's fiqh deduction in the chapter title. The chapter title IS a teaching unit. Current SPEC does not recognize heading-as-content.
  - **Jami' al-Tirmidhi** interleaves hadith with the compiler's grading and fiqh commentary. The commentary is a different layer from the hadith text, but both are by al-Tirmidhi. Current layer detection (sharh vs matn) does not model "compiler commentary within a compilation."
  - **Musnad collections** (e.g., Musnad Ahmad) organize by narrator, not by fiqh topic. Multiple hadith from the same narrator may be thematically unrelated. Merging adjacent hadith (as tiny-division merging in section 4.4 might) would create incoherent teaching units.

- **Mu'allaq (suspended-chain) hadith.** Al-Bukhari frequently cites hadith with truncated isnads: "وقال مالك عن نافع عن ابن عمر..." omitting the chain from al-Bukhari to Malik. These mu'allaq citations look like regular text (no حدثنا formula). The pipeline may fail to recognize them as hadith evidence.

- **Takhrij (source-tracing) notation.** The SPEC section 6.3 EV-2 extracts collection name and number from "رواه البخاري" patterns, but real takhrij is more complex: "أخرجه البخاري (2345) ومسلم (678) وأبو داود (901) من طريق فلان". This is a single evidence segment referencing three collections. The data model records one `evidence_ref` per segment; it should support multiple collection references per hadith citation.

- **Hadith grading disagreements.** When a muhaqqiq (editor) grades a hadith differently from the author ("قال المؤلف: حسن، وقال الألباني: ضعيف"), the SPEC section 6.3 records the grade and its source. But the data model does not explicitly support conflicting grades from different sources on the same hadith. This is a metadata modeling gap.

**Risk level:** HIGH for hadith collection processing. Mis-segmenting hadith or losing grading information directly affects knowledge integrity.
**Engines affected:** Source (genre sub-classification), Excerpting (Phase 2a classification, section 6.3).
**Recommended action:** Add hadith-collection-specific rules to SPEC section 6. Extend evidence_ref data model to support multiple collection references. Add fixture from a real hadith sharh text.

---

### 1.4 Usul al-Fiqh: Argumentative Structure

**What the pipeline knows:** The islamic-sciences-classification SKILL documents usul terminology and structure. The Genre enum includes `USUL_AL_FIQH`. The test fixtures include `waraqat_usul`.

**What the pipeline misses:**

- **Deep nested argumentation.** Usul texts follow a pattern of: state a principle, present the majority view, present dissenting views, cite evidence for each, present counter-arguments to each piece of evidence, respond to counter-arguments. This can nest 4-5 levels deep. The SPEC's DP-1 (position + refutation) and DP-5 (counter-argument + original) handle two levels. Deeper nesting risks producing teaching units that contain a counter-counter-argument without the original argument.

- **Technical logical terminology.** Usul texts use formal logical vocabulary (لازم, ملزوم, عكس, طرد, منع, سند, مطالبة) that the Phase 2a classifier's 16 scholarly functions do not capture. A "سند" in usul al-fiqh means "supporting argument," not a hadith chain. The terminology overlap (see SKILL Rule 4 on terminology shifts) is documented, but the segment classifier has no usul-specific function type for formal logical moves.

- **Istidlal (argumentation) chains.** In usul, evidence is not a simple citation but a structured argument: major premise (e.g., "every command implies obligation"), minor premise (e.g., "God commanded prayer"), conclusion (e.g., "therefore prayer is obligatory"). Splitting the syllogism across teaching units destroys the argument.

**Risk level:** MEDIUM. The waraqat_usul fixture is a beginner-level text. Advanced usul texts (e.g., al-Mustasfa, al-Burhan) have much more complex argumentation.
**Engines affected:** Excerpting (Phase 2a and 2b).
**Recommended action:** Research further with an advanced usul fixture. Potentially add a `formal_argument` scholarly function type or add usul-specific grouping rules.

---

### 1.5 Aqeedah/Kalam: Dialectical Structure

**What the pipeline knows:** The islamic-sciences-classification SKILL documents aqeedah terminology. The SPEC's DP-1 handles position + refutation.

**What the pipeline misses:**

- **Kalam dialectical method (jadal).** Classical kalam texts use a specific dialectical structure: (1) state the opponent's claim (shubha), (2) present the opponent's proof, (3) show the flaw in the proof (naqd), (4) present the correct view with proof. This is more structured than simple position-refutation. Works like al-Iqtisad fi'l-I'tiqad or Sharh al-Aqidah al-Tahawiyyah follow this pattern extensively.

- **Sect-attribution sensitivity.** The islamic-sciences-classification SKILL notes that "KR must RECORD the position, NOT evaluate it" and flags T-2 risk. But the specific risk is more nuanced: attributing a position to a sect when the author is presenting it to refute it. "قالت المعتزلة: القرآن مخلوق" in an Ash'ari text is the Mu'tazili position being presented for refutation. If excerpted alone, it could appear that the author holds this view. This is a domain-specific variant of DP-1 (position + refutation) that requires additional emphasis.

- **Creedal matn + sharh pattern.** Many aqeedah texts are structured as a creedal statement (matn, often memorized) plus explanation. The matn may be just one sentence per creedal point, with pages of explanation. Current layer detection handles sharh-matn, but the creedal matn has a specific characteristic: each matn sentence is a standalone creedal affirmation. Splitting "matn sentence + explanation" is DP-1, but recognizing that the matn sentence is a creedal affirmation (not just a definition or rule) affects taxonomy classification.

**Risk level:** HIGH for sect-attribution errors (T-2 threat). MEDIUM for structural handling.
**Engines affected:** Excerpting (Phase 2b, section 6.1), Taxonomy (school/sect attribution).
**Recommended action:** Add sect-attribution safeguard to SPEC section 6.1 as DP-7. Add aqeedah test fixture.

---

### 1.6 Tasawwuf: Experiential and Metaphorical Language

**What the pipeline knows:** The islamic-sciences-classification SKILL hierarchy includes "التزكية / التصوف" but provides no detailed processing guide (unlike the 8 sciences documented in detail).

**What the pipeline misses:**

- **Technical Sufi terminology has domain-specific meanings.** Key terms like فناء (annihilation), بقاء (subsistence), مقام (station), حال (state), كشف (unveiling), ذوق (taste), وجد (ecstasy), سكر (intoxication), صحو (sobriety) have precise technical meanings in tasawwuf that differ completely from their ordinary Arabic meanings. The LLM may classify passages about "spiritual intoxication" (سكر) as if they discuss literal intoxication.

- **Metaphorical language should not be classified literally.** Sufi poetry and prose use extended metaphors (wine = divine love, beloved = God, intoxication = spiritual ecstasy). The Phase 2a classifier might assign `unclassified` or wrong scholarly functions to these passages because the language does not match standard scholarly discourse patterns.

- **Maqamat/ahwal structure.** Tasawwuf texts organize spiritual development as a sequence of stations (maqamat) and states (ahwal). Each station has: definition, scriptural basis, stories of practitioners, and practical guidance. This structure maps naturally to teaching units, but the pipeline has no tasawwuf-aware recognition of this pattern.

**Risk level:** LOW for the immediate pipeline (tasawwuf texts are a minority in the current Shamela collection). HIGH if the library grows to include major Sufi works (e.g., Ihya Ulum al-Din, which spans multiple sciences).
**Engines affected:** Excerpting (Phase 2a classification), Taxonomy (science classification).
**Recommended action:** Add tasawwuf to the islamic-sciences-classification SKILL with processing guidance. Accept limitation for initial pipeline; revisit when tasawwuf fixtures are added.

---

## 2. Historical Period Differences

### 2.1 Pre-5th Century AH Texts: Less Differentiated Sciences

**What the pipeline knows:** The islamic-sciences-classification SKILL Rule 5 notes that "Pre-5th century AH: Sciences less differentiated. A single work may freely mix nahw, tafsir, and fiqh."

**What the pipeline misses:**

- **Practical processing implications of mixed-science texts.** The SKILL acknowledges the issue but does not specify how to handle it. If a 3rd-century text mixes fiqh rulings with hadith commentary and grammatical analysis in a single chapter, what is the `science_scope`? The current model is a list ordered by dominance, but in genuinely mixed texts, no science dominates.

- **Early Arabic scholarly prose style.** Pre-5th-century texts use different structural conventions: fewer formal section headings, more flowing narrative, less stereotyped scholarly formulas. The division tree construction (normalization section 4.A.6) relies on heading detection keywords (كتاب, باب, فصل). Early texts may use different markers or no markers at all, producing flat or minimal division trees.

- **Different isnad conventions.** Early hadith texts have longer, more varied isnads. Later texts abbreviated isnads with ta'liq (suspension) or used collective isnads (one chain for multiple hadith). The pipeline's isnad detection patterns may not cover early verbose patterns.

**Risk level:** MEDIUM. The pipeline handles minimal division trees (SPEC section 4.2 C-8), but early texts may produce low-quality LLM classifications due to unfamiliar structure.
**Engines affected:** Normalization (structure discovery), Excerpting (Phase 2).
**Recommended action:** Research further with an early classical fixture. Document as a known limitation (L-XXX) for the initial pipeline.

---

### 2.2 Post-8th Century AH: Commentary Tradition Dominance

**What the pipeline knows:** The SKILL Rule 5 acknowledges commentary dominance in this period. The SPEC handles sharh/hashiyah layer detection.

**What the pipeline misses:**

- **Multi-level commentary depth.** The pipeline handles 2-layer texts (matn + sharh) and the SKILL mentions up to 5+ layers for nahw. But the actual layer detection in normalization is typographic (bold, brackets, transition phrases). For a 4-layer text (matn + sharh + hashiyah + ta'liqat), the normalization engine's typographic detection may only identify 2 layers, collapsing hashiyah and ta'liqat into the sharh layer. The excerpting engine's layer attribution (section 6.2) then attributes hashiyah text to the sharh author -- a T-2 error.

- **Commentary chains across separate works.** The scholarly tradition creates dependency chains: a hashiyah references the sharh, which references the matn, which may reference earlier works. The pipeline processes each work independently. When Excerpt A (from the hashiyah) says "قوله: يريد..." referring to the sharh text, the reference is unresolvable because the sharh is a different source. This is a fundamental architectural constraint (D-011: each chunk is processed independently), not a bug, but it should be documented as a limitation.

**Risk level:** HIGH for 3+ layer texts (T-2 attribution errors). MEDIUM for cross-work references (incomplete but not incorrect).
**Engines affected:** Normalization (layer detection), Excerpting (section 6.2 attribution).
**Recommended action:** Add known limitation L-XXX for 3+ layer detection. Consider adding a `commentary_chain` metadata field to the source engine to link related works.

---

### 2.3 Modern Tahqiq Editions: Editorial Apparatus

**What the pipeline knows:** The arabic-scholarly-conventions.md documents marginal note indicators and editorial apparatus markers. The normalization SPEC handles footnotes.

**What the pipeline misses:**

- **Tahqiq footnote taxonomy.** Modern critical editions have multiple types of footnotes serving different scholarly functions:
  - **Variant readings (نسخ):** "في نسخة ب: كذا" -- manuscript variants
  - **Source identification (تخريج):** "أخرجه البخاري (2345)" -- hadith source tracing
  - **Editor's commentary (تعليق):** The muhaqqiq's own analysis
  - **Biographical notes (ترجمة):** Brief scholar biographies
  - **Cross-references:** "انظر: المجلد الثاني ص 45"
  The normalization engine treats all footnotes as a single `Footnote` type. The excerpting engine's Phase 3 enrichment could extract more value if footnotes were typed.

- **Apparatus criticus conventions.** Critical editions use standardized sigla (أ = manuscript A, ب = manuscript B, ط = printed edition) and formulaic expressions (في الأصل, سقط من, بياض في, كذا بالأصل). The normalization contracts have a `VariantReadingData` model, but the excerpting engine does not consume it for enrichment.

- **Editor vs author voice in footnotes.** Tahqiq editors often insert their opinions in footnotes: "والصواب كذا" (the correct reading is...) or "هذا وهم من المؤلف" (this is an error by the author). These are editorial assertions that should be attributed to the muhaqqiq, not the author. The pipeline's layer detection tags footnotes as `editorial`, but the fine-grained attribution of footnote content to the muhaqqiq is not implemented.

**Risk level:** MEDIUM. Footnotes are preserved and passed through (D-023). The gap is in footnote exploitation for enrichment, not in data loss.
**Engines affected:** Normalization (footnote classification), Excerpting (Phase 3 enrichment).
**Recommended action:** Add footnote type classification as a deferred enhancement to normalization SPEC section 4.B.4. Accept current generic footnote handling for the initial pipeline.

---

## 3. Manuscript vs Print Artifacts

### 3.1 Source Quality Detection

**What the pipeline knows:** The source engine evaluates `text_fidelity` and `trust_tier` using a 5-factor weighted algorithm. The arabic-text-quality SKILL detects OCR corruption and encoding artifacts.

**What the pipeline misses:**

- **Edition type detection.** Shamela texts come from diverse print sources: critical editions (tahqiq), lithographs, commercial prints, and sometimes direct manuscript transcriptions. The pipeline does not classify the edition type. This matters because:
  - Critical editions have editorial apparatus (footnotes with variants, sources) that is high-value metadata.
  - Lithographs may have different layout conventions (margin text is inline, not footnotes).
  - Commercial prints may have low-quality OCR or modernized spelling.
  - Manuscript transcriptions may preserve scribal errors that look like OCR corruption.

- **Lithograph-specific artifacts.** Lithographed Arabic texts (common in the Indian subcontinent and early Egyptian printing) have distinctive features: nasta'liq script (vs naskh), dense marginal commentary printed alongside the main text, and no modern punctuation. Shamela digitizations of lithographs may encode the marginal text inline, creating apparent text that is actually from a different work (the hashiyah printed in the margin). The normalization engine's layer detection relies on typographic markers that may not exist in lithograph transcriptions.

- **Manuscript provenance signals.** When Shamela sources derive from manuscript transcriptions rather than print editions, certain textual features appear: scribal colophons (preserved in the digital text), waqf endowment stamps (text descriptions), and audition certificates (sama'at). These are valuable metadata that the pipeline currently does not extract.

**Risk level:** MEDIUM for edition type detection (affects trust evaluation and processing strategy). LOW for lithograph artifacts (small percentage of Shamela collection).
**Engines affected:** Source (metadata extraction), Normalization (layer detection).
**Recommended action:** Add edition-type classification to the source engine as a deferred enhancement. Document lithograph handling as a known limitation.

---

## 4. Missing Scholarly Conventions

### 4.1 Waqf Marks (Quranic Recitation Notation)

**What the pipeline knows:** The quranic-text-handling SKILL covers ayah end markers (U+06DD) and rubic hizb marks (U+06DE).

**What the pipeline misses:**

- **Full waqf mark inventory.** Quranic text in digital editions may contain waqf marks that the pipeline does not recognize:
  - مـ (U+06D6 or annotated) -- waqf lazim (mandatory stop)
  - صلـ (U+06D7) -- waqf al-wasli (preferred connection)
  - ج (on its own or U+06D9) -- waqf ja'iz (permissible stop)
  - قلى / صل (U+06D8, U+06DA) -- preferred stop / preferred continuation
  - ۩ (U+06E9) -- sajdah mark (prostration indicator)
  - ۞ (U+06DE) -- rubic hizb (documented in the SKILL)
  These marks are part of the Quranic text and MUST be preserved (zero modification principle). But they may appear in Quranic quotations within scholarly texts and affect text matching (a quoted verse with waqf marks won't exactly match one without).

- **Waqf marks affect verse identification.** When the excerpting engine tries to match a Quranic quotation against a canonical text database (SPEC section 6.3 EV-1), waqf marks embedded in the quotation will cause match failure if the reference database lacks them (or vice versa). The matching algorithm needs to strip waqf marks for comparison while preserving them in the stored text.

**Risk level:** LOW. Waqf marks in non-mushaf scholarly texts are uncommon. When they appear, they are typically in tafsir or tajweed texts.
**Engines affected:** Excerpting (Phase 3, EV-1 Quran matching).
**Recommended action:** Add waqf mark stripping to the Quran text matching algorithm as a normalization step (for matching only, not storage). Document the Unicode codepoints in the quranic-text-handling SKILL.

---

### 4.2 Tashkeel (Diacritics) Provenance

**What the pipeline knows:** The pipeline preserves diacritics byte-for-byte. The quranic-text-handling SKILL uses diacritization level as an authenticity signal (section 2.2).

**What the pipeline misses:**

- **Author vs editor diacritics.** In modern tahqiq editions, the muhaqqiq (editor) often adds diacritics to the author's text for clarity. The original manuscript may have had minimal or no diacritics. The pipeline preserves all diacritics but cannot distinguish author-original from editor-added. This matters because:
  - Editor-added diacritics represent editorial interpretation, not the author's original intent.
  - In grammatical texts (nahw/sarf), diacritics are substantive content; in fiqh texts, they are usually disambiguation aids.
  - Over-reliance on diacritics as a "quality" signal may penalize faithfully undiacritized texts.

- **Inconsistent diacritization within a single source.** Some Shamela texts have sections with full tashkeel and sections with none. This typically indicates that the digitizer diacritized selectively (e.g., Quranic quotations and hadith get full tashkeel, author's prose gets none). The pipeline does not flag or handle this inconsistency.

**Risk level:** LOW. Diacritics are preserved regardless of provenance. The gap affects metadata quality (knowing which diacritics are authoritative) but does not cause data corruption.
**Engines affected:** Normalization (text fidelity assessment), Source (quality evaluation).
**Recommended action:** Accept limitation. Document in KNOWN_LIMITATIONS.md. Consider adding a `diacritization_level` metadata field in future.

---

### 4.3 Sama'at (Audition Certificates) and Ijazat (Transmission Licenses)

**What the pipeline knows:** The arabic-scholarly-conventions.md mentions "بلغ مقابلة بأصله" as a collation mark. No explicit handling of sama'at or ijazat.

**What the pipeline misses:**

- **Sama'at are high-value metadata.** An audition certificate (سماع) records: who read the text, to whom, when, and where. These certificates appear as marginal notes in manuscripts and may survive into Shamela digitizations as inline text blocks. They provide:
  - Terminus ante quem for the text (the audition happened after the text was written)
  - Transmission chain information
  - Geographic and institutional provenance
  The pipeline currently has no detection pattern for sama'at and would treat them as regular text.

- **Ijazat provide scholarly authority metadata.** Transmission licenses (إجازات) document the authority chain for a text. When preserved in Shamela sources, they appear as prefatory or appended text blocks. They contain scholar names and dates that could enrich the source engine's metadata.

**Risk level:** LOW. Sama'at and ijazat are uncommon in Shamela digitizations (more common in manuscript-based sources). When present, they are non-destructively treated as regular text.
**Engines affected:** Source (metadata extraction), Excerpting (classification -- should be tagged as `editorial_note` or a new function type).
**Recommended action:** Accept limitation for initial pipeline. Add detection patterns when manuscript-source normalizers are built (normalization SPEC section 4.A.4 deferred).

---

### 4.4 Matn/Sharh/Hashiyah Visual Markers in Print

**What the pipeline knows:** The normalization engine's layer detection uses typographic signals (bold, brackets, transition phrases). The excerpting SPEC section 6.2 handles multi-layer attribution.

**What the pipeline misses:**

- **Print convention inventory.** Arabic print editions use a variety of visual conventions to distinguish text layers:
  - **Matn in bold**, sharh in regular -- most common
  - **Matn between brackets** [ ] or ( ) -- common in older editions
  - **Matn in a different font size** (smaller/larger) -- some publishers
  - **Matn prefixed with "م"** or "متن" -- some modern editions
  - **Inline markers:** "قال المصنف" before matn text, "أقول" or "قال الشارح" before sharh
  - **Color coding** (in original print) lost in digitization
  - **Marginal text** (hashiyah printed in the margin) -- lost or scrambled in digitization
  The normalization engine implements a subset of these. Research suggests that the detection accuracy is "known limitations L-001 through L-012" -- the pipeline is already aware of gaps but may not have catalogued all the conventions it misses.

- **Layer detection failure modes.** When the normalization engine fails to detect a layer transition, the excerpting engine receives incorrectly layered text. The excerpting SPEC section 6.2 notes this risk and deliberately does not pass layer metadata to the LLM (to avoid LLM deferring to incorrect metadata). However, the LLM's own layer detection from content is also imperfect, creating a double-failure scenario: normalization misses the layer, AND the LLM classifies the passage as single-layer when it is multi-layer.

**Risk level:** HIGH for T-2 (attribution error) in texts where normalization layer detection fails. The excerpting engine's defensive design (not passing layers to LLM) mitigates but does not eliminate the risk.
**Engines affected:** Normalization (layer detection), Excerpting (section 6.2).
**Recommended action:** Inventory all common print layer conventions and map them to normalization detection capabilities. Add adversarial test cases for each convention the pipeline does not handle. Prioritize improving normalization layer detection over adding new conventions.

---

## 5. Edge Cases by Genre

### 5.1 Fiqh: Complex Khilaf with Tarjih

**Pattern:** A fiqh text presents 4 madhab opinions on a single mas'ala, each with evidence, then the author provides tarjih (preponderant view) with reasoning.

**What breaks:** The Phase 2b LLM may group each opinion as a separate teaching unit. The tarjih (which references all 4 opinions) becomes decontextualized -- it says "the strongest view is the second" but the reader does not know what "the second" refers to.

**Risk level:** HIGH
**Engines affected:** Excerpting (Phase 2b)
**Recommended action:** Add adversarial test case ADV-E-13 (multi-opinion khilaf with tarjih). Verify that the LLM groups the complete khilaf discussion as one teaching unit for passages with 3+ opinions.

---

### 5.2 Hadith: Mu'allaq (Suspended-Chain) and Mawquf (Stopped) References

**Pattern:** Al-Bukhari says "وقال مالك..." without a full isnad (mu'allaq). Or the text contains a mawquf report from a companion without attribution to the Prophet.

**What breaks:** The Phase 2a classifier may not recognize mu'allaq citations as `evidence_hadith` because they lack the standard transmission formulas (حدثنا, أخبرنا). They look like regular `opinion_statement` ("Malik said..."). The evidence is then lost from the metadata.

**Risk level:** MEDIUM
**Engines affected:** Excerpting (Phase 2a classification)
**Recommended action:** Add mu'allaq detection patterns to the Phase 2a prompt or post-processing. Add test cases with mu'allaq hadith from Bukhari fixtures.

---

### 5.3 Tafsir: Qira'at Discussion Passages

**Pattern:** A mufassir discusses 3 variant readings of a verse: "قرأ نافع كذا، وقرأ ابن كثير كذا، وقرأ عاصم كذا..."

**What breaks:** The pipeline correctly preserves each variant reading but has no mechanism to:
  (a) Tag the teaching unit as a qira'at discussion
  (b) Link each variant to its reciter/reading tradition
  (c) Record that this is a discussion ABOUT the Quran rather than a citation OF the Quran

**Risk level:** LOW (data is preserved; the gap is in enrichment metadata)
**Engines affected:** Excerpting (Phase 3), Taxonomy
**Recommended action:** Add `qiraat_discussion` flag to enrichment metadata as a deferred enhancement.

---

### 5.4 Nahw: I'rab (Grammatical Analysis) Notation

**Pattern:** A nahw text provides i'rab of a Quranic verse or hadith: "الحمد: مبتدأ مرفوع بالضمة... لله: جار ومجرور متعلق بمحذوف خبر..."

**What breaks:** The i'rab analysis is word-by-word, with each word getting a grammatical classification. Current segment classification has no function type for grammatical analysis. The LLM would likely classify this as `definition` or `unclassified`. More importantly, the i'rab of a Quranic verse is teaching content (not a Quran citation itself), but it includes the Quranic words. The quranic-text-handling SKILL section 5.4 addresses this partially (Quranic vocabulary in non-Quranic context).

**Risk level:** LOW for data integrity (text is preserved). MEDIUM for classification quality.
**Engines affected:** Excerpting (Phase 2a)
**Recommended action:** Consider adding `grammatical_analysis` to the 16 scholarly function types. Test with ibn_aqil fixture data to see if the LLM classifies i'rab passages correctly without a dedicated type.

---

### 5.5 Tarikh/Tabaqat: Genealogical Chains (Nasab) and Biographical Entries

**Pattern:** A biographical dictionary has stereotyped entries: name (with full nasab chain), kunyah, nisba, birth date, teachers, students, works, death date, evaluation. Example from Siyar A'lam al-Nubala.

**What breaks:** Each biographical entry is a natural teaching unit. But the pipeline's current approach treats all prose identically. For tabaqat:
  - The nasab chain contains structured data (names, relationships) that could be extracted
  - The teacher/student lists create a scholarly network graph
  - The evaluation section (jarh wa-ta'dil) is domain-specific content type
  Current segment classification has no function types for biographical data.

**Risk level:** LOW for the excerpting engine (biographical entries are well-structured; the LLM will group them correctly). MEDIUM for the taxonomy engine (missing structured biographical metadata).
**Engines affected:** Excerpting (Phase 2a -- no biographical function types), Taxonomy (scholar network), Synthesis.
**Recommended action:** Defer biographical structure extraction to the taxonomy engine. The excerpting engine should produce complete biographical entries as teaching units without decomposing them. Add test fixture from a tabaqat/tarajim source.

---

## 6. Cross-Cutting Gaps

### 6.1 Poetry (Shawahid) Handling

**What the pipeline knows:** The SPEC section 6.5 handles verse-commentary (nazm) texts. The islamic-sciences-classification SKILL mentions that nahw examples must preserve meter and diacritics.

**What the pipeline misses:**

- **Poetry quoted as evidence (shawahid) across all sciences.** Arabic scholarly tradition cites poetry as grammatical evidence (shawahid nahwiyyah), rhetorical examples (shawahid balaghiyyah), and moral illustration (shawahid adabiyyah). These poetic citations appear in fiqh, hadith commentary, tafsir, and other non-literary sciences. The pipeline has no mechanism to:
  - Detect quoted poetry in non-verse texts
  - Preserve poetic meter (bayt structure: sadr + 'ajz)
  - Tag the poet's name and the poem's title for attribution
  - Distinguish between a single bayt cited as evidence vs a complete poem

- **The bayt as an atomic unit.** A single line of Arabic poetry (bayt) has a fixed internal structure (two hemistichs). Splitting a bayt across teaching units or passages is equivalent to splitting a Quranic verse -- it destroys the content.

**Risk level:** MEDIUM. Poetry preservation is important for nahw and balagha texts where shawahid are central to the argument.
**Engines affected:** Normalization (structure detection), Excerpting (Phase 2a -- no `poetic_evidence` function type).
**Recommended action:** Add `poetic_evidence` or `shahid` scholarly function type. Add poetry detection to normalization. Test with nahw fixtures containing shawahid.

---

### 6.2 Du'a (Supplication) Texts

**What the pipeline knows:** The quranic-text-handling SKILL section 5.3 addresses du'a that embeds Quranic phrases.

**What the pipeline misses:**

- **Du'a compilations as a genre.** Books like Hisn al-Muslim or al-Adhkar are collections of supplications. They have a distinctive structure: situation/occasion, then the du'a text (often with tashkeel), then the source (hadith reference), then the count of repetitions. The pipeline has no Genre value for du'a collections (they would fall under `OTHER`) and no structural format for the situation-du'a-source pattern.

- **Du'a within non-du'a texts.** When a scholar includes a du'a mid-chapter (common in prefaces, colophons, and transitions), the LLM may classify it as `unclassified` or misclassify it as `evidence_hadith` (many du'as come from hadith).

**Risk level:** LOW. Du'a texts are a small subset. The text is preserved regardless of classification accuracy.
**Engines affected:** Source (genre classification), Excerpting (Phase 2a).
**Recommended action:** Accept limitation. Add du'a-related genre or sub-genre if the library includes du'a compilations.

---

### 6.3 Numbers, Dates, and Monetary Amounts

**What the pipeline knows:** The regex-arabic-digits.md rule warns about `\d` matching Arabic-Indic digits.

**What the pipeline misses:**

- **Hijri date extraction from running text.** Scholarly texts reference dates in multiple formats: "سنة خمس وخمسين ومائتين" (written out), "سنة 255هـ" (numeric), "في المحرم سنة ٢٥٥" (Arabic-Indic numeric). The pipeline has no date extraction beyond colophon patterns (arabic-scholarly-conventions.md).

- **Monetary and measurement amounts in fiqh.** Fiqh texts discuss zakat nisab, diyah amounts, weights and measures using both historical (dinar, dirham, sa', mudd) and numeric values. These are domain-specific structured data that the pipeline does not extract.

**Risk level:** LOW. Dates and amounts are preserved in the text. The gap is in structured extraction.
**Engines affected:** Excerpting (Phase 3 enrichment), Taxonomy.
**Recommended action:** Defer structured date/amount extraction. Accept as text content for the initial pipeline.

---

## Summary Risk Matrix

| Gap | Risk | Primary Engine | Action |
|-----|------|---------------|--------|
| Multi-opinion khilaf (1.1) | HIGH | Excerpting | Add SPEC section 6.7 |
| Hadith collection patterns (1.3) | HIGH | Excerpting | Add SPEC section 6 rules |
| Sect-attribution in aqeedah (1.5) | HIGH | Excerpting | Add DP-7 to SPEC section 6.1 |
| 3+ layer text detection (2.2) | HIGH | Normalization | Document limitation, improve detection |
| Layer convention inventory (4.4) | HIGH | Normalization | Audit and add adversarial tests |
| Multi-opinion tarjih (5.1) | HIGH | Excerpting | Add ADV-E-13 test case |
| Tafsir structure types (1.2) | MEDIUM | Excerpting | Add SPEC section 6.8 |
| Usul argumentation depth (1.4) | MEDIUM | Excerpting | Research with advanced fixture |
| Poetry/shawahid (6.1) | MEDIUM | Excerpting | Add scholarly function type |
| Tahqiq footnote taxonomy (2.3) | MEDIUM | Normalization | Deferred enhancement |
| Mu'allaq hadith detection (5.2) | MEDIUM | Excerpting | Add detection patterns |
| I'rab classification (5.4) | MEDIUM | Excerpting | Test with fixture data |
| Biographical structure (5.5) | MEDIUM | Taxonomy | Defer to taxonomy engine |
| Pre-5th century texts (2.1) | MEDIUM | Normalization | Document limitation |
| Hadith grading conflicts (1.3) | MEDIUM | Excerpting | Extend evidence_ref model |
| Tasawwuf terminology (1.6) | LOW | Excerpting | Add SKILL processing guide |
| Waqf marks (4.1) | LOW | Excerpting | Strip for matching only |
| Tashkeel provenance (4.2) | LOW | Normalization | Accept limitation |
| Sama'at/Ijazat (4.3) | LOW | Source | Defer to manuscript normalizers |
| Edition type detection (3.1) | MEDIUM | Source | Deferred enhancement |
| Qira'at discussion tag (5.3) | LOW | Excerpting | Deferred enhancement |
| Du'a texts (6.2) | LOW | Source | Accept limitation |
| Date/amount extraction (6.3) | LOW | Excerpting | Defer structured extraction |

---

## Research Sources

- [IslamicMMLU: A Benchmark for Evaluating LLMs on Islamic Knowledge](https://arxiv.org/html/2603.23750)
- [NLP Techniques for Qur'anic Studies](https://www.frontiersin.org/journals/signal-processing/articles/10.3389/frsip.2025.1535166/full)
- [Rezwan: LLM Hadith Text Processing 1.2M Corpus](https://arxiv.org/html/2510.03781)
- [Computational Studies of Hadith Literature Survey](https://link.springer.com/article/10.1007/s10462-019-09692-w)
- [Building a Digital Tabaqat](https://research.sabanciuniv.edu/47570/1/project_muse_902203.pdf)
- [KITAB Project: Mapping Who's Who in Isnads](https://kitab-project.org/Mapping-Who-s-Who-in-Isnads-First-Steps/)
- [Shamela: A Large-Scale Historical Arabic Corpus](https://aclanthology.org/W16-4007.pdf)
- [From Tashih to Tahqiq: Arabic Critical Edition History](https://www.researchgate.net/publication/338097749_From_Tashih_to_Tahqiq_Toward_a_History_of_the_Arabic_Critical_Edition)
- [Juristic Dialectic in Islamic Jadal and Khilaf](https://www.academia.edu/86000641/)
- [Audience Certificates in Arabic Manuscripts](https://www.academia.edu/26987851/Audience_Certificates_in_Arabic_Manuscripts_the_Genre_and_a_Case_Study)
- [A Glossary of Sufi Technical Terms](https://archive.org/details/sufi-technical-terms)
- [Unicode Proposals for Quranic Characters](https://www.unicode.org/L2/L2019/19306-quranic-additions.pdf)
- [Quranic Punctuation (Wikipedia)](https://en.wikipedia.org/wiki/Qur'anic_punctuation)
- [Dialectic in Islamic Philosophy (Encyclopedia.com)](https://www.encyclopedia.com/humanities/encyclopedias-almanacs-transcripts-and-maps/dialectic-islamic-and-jewish-philosophy)
- [Qira'at (Wikipedia)](https://en.wikipedia.org/wiki/Qira'at)
- [Audition Certificates Platform](https://www.audition-certificates-platform.org/about)
