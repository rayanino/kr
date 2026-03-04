# Pipeline Trace — One Passage Through Every Engine

This document traces a SINGLE passage through the entire KR pipeline, showing what each engine receives, what it produces, and what metadata accumulates. The architect should use this to understand the data transformations and ensure nothing is lost between stages.

**Source text:** A page from شرح ابن عقيل على ألفية ابن مالك, the chapter on المبتدأ والخبر.

---

## Stage 1: Source Engine

**Input:** Owner uploads a Shamela HTML export of شرح ابن عقيل.

**Engine actions:**
- Assigns source_id: `src_00147`
- Identifies work: شرح ابن عقيل على ألفية ابن مالك
- Identifies work relationships: this is a شرح of ألفية ابن مالك (work_id: `wrk_00023`)
- Looks up author: بهاء الدين عبد الله بن عقيل الهمداني (d. 769 AH / 1367 CE)
- Records: Shafi'i in fiqh, Egyptian, student of أبو حيان الأندلسي
- Trustworthiness: verified (major established commentary, published by reputable publishers for centuries)
- Freezes the raw HTML files

**Output (source metadata):** `{ source_id: "src_00147", work_id: "wrk_00089", work_title: "شرح ابن عقيل", author: { canonical_id: "sch_00312", name: "ابن عقيل", full_name: "بهاء الدين عبد الله بن عقيل الهمداني", death_hijri: 769, death_ce: 1367, school_fiqh: "شافعي", teachers: ["sch_00298"], ... }, genre: "sharh", sharh_of: "wrk_00023", science: ["nahw"], level: "intermediate", trust: "verified", ... }`

**What metadata is NEW here:** Everything. This is where author identity, work classification, genre chains, and trust assessment originate.

---

## Stage 2: Normalization Engine

**Input:** Frozen Shamela HTML files + source metadata.

**Engine actions:**
- Shamela normalizer strips HTML markup
- Separates footnotes from main text (Shamela encodes these as `<span class="footnote">`)
- Discovers structure: identifies 4 أبواب (chapters), 47 فصول (sections), heading hierarchy
- Detects encoding: UTF-8, no corruption
- Discovers: some footnotes are editor's tahqiq notes (modern), others are Ibn Aqil's own marginal notes (original)

**Output (normalized package):** Clean text + division tree + footnote layer + structure metadata. Source-format-specific markup is GONE. A PDF normalizer or a camera-photo normalizer would produce the same schema from different input.

**What metadata is NEW here:** Structure discovery (division tree, heading hierarchy), text quality assessment, footnote classification (author-original vs. editor-added). ALL source metadata passes through unchanged.

---

## Stage 3: Passaging Engine

**Input:** Normalized package.

**Engine actions:**
- Divides the chapter on المبتدأ والخبر into passages
- One passage covers Ibn Aqil's explanation of الألفية line 75: "المبتدأ اسم ابتداء..."
- This passage is ~400 words, containing: the verse line, Ibn Aqil's explanation, two examples, a footnote referencing سيبويه

**Output (passage):** `{ passage_id: "psg_00147_ch02_003", text: "...", division_path: ["المبتدأ والخبر", "تعريف المبتدأ"], footnotes: [{text: "...", type: "author_original"}], source_id: "src_00147", ... }`

**What metadata is NEW here:** Passage boundaries, division path (where in the book's structure this passage sits). ALL upstream metadata accessible via source_id.

---

## Stage 4: Atomization Engine

**Input:** Passage.

**Engine actions:**
- Identifies 6 atoms in this passage:
  1. **Verse line** (matn quotation): "المبتدأ اسم ابتداء..." — atom type: `primary_text_quotation`
  2. **Definition** (sharh): "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية" — atom type: `definition`
  3. **Example 1**: "نحو: زيدٌ قائمٌ" — atom type: `example`
  4. **Example 2**: "نحو: أقائمٌ الزيدان" — atom type: `example`
  5. **Cross-reference**: "وقد ذهب سيبويه إلى أن المبتدأ..." — atom type: `scholarly_reference`
  6. **Footnote**: tahqiq note on manuscript variants — atom type: `editorial_note`

**Output (atoms):** Each atom with precise character offsets, type, and content.

**What metadata is NEW here:** Atom boundaries, atom types, character offsets. Atom types are critical — the excerpting engine uses them to understand what KIND of content it's grouping.

---

## Stage 5: Excerpting Engine

**Input:** Atoms from this passage (+ potentially adjacent passages if context spans a boundary).

**Engine actions:**
- Groups atoms 1-5 into one excerpt (they form a coherent teaching unit: "Ibn Aqil's definition of المبتدأ with examples and a reference to Sibawayhi")
- Atom 6 (editorial note) is attached as metadata, not part of the excerpt's core text
- Determines: this excerpt is self-contained (a reader can understand the definition without needing other excerpts)
- Enriches metadata:
  - Topic: تعريف المبتدأ
  - Content type: definition with examples
  - Author attribution: ابن عقيل (but quoting سيبويه)
  - School: Basran grammatical tradition (inferred from the definition style)
  - Proposed leaf: nahw > المبتدأ والخبر > تعريف المبتدأ

**Output (draft excerpt):** `{ excerpt_id: "exc_00147_003_01", text: "...", topic: "تعريف المبتدأ", author_id: "sch_00312", quoted_scholars: ["sch_00001"], school: "بصري", content_type: "definition", proposed_leaf: "nahw/mubtada_wa_khabar/tarif_mubtada", self_contained: true, status: "draft", source_id: "src_00147", passage_id: "psg_00147_ch02_003", ... }`

**What metadata is NEW here:** Topic classification, school attribution, quoted scholars, content type, self-containment assessment, proposed leaf. This is where the excerpt becomes a knowledge unit, not just text.

---

## Stage 6: Taxonomy Engine

**Input:** Draft excerpt with proposed leaf.

**Engine actions:**
- Validates proposed leaf exists in the Nahw tree: nahw > المبتدأ والخبر > تعريف المبتدأ ✓
- Checks for placement conflicts (is another excerpt from the same source already at this leaf? No → good)
- Verifies coverage: this leaf now has 7 excerpts from 5 different sources
- Detects: no Kufan-school excerpt at this leaf yet → flags coverage gap
- Places the excerpt

**Output (placed excerpt):** Status changes from "draft" to "placed". Leaf assignment is final. Coverage metrics updated.

**What metadata is NEW here:** Final leaf assignment, coverage data, gap detection. ALL upstream metadata preserved.

---

## Stage 7: Synthesizing Engine

**Input:** ALL 7 placed excerpts at leaf `nahw/mubtada_wa_khabar/tarif_mubtada` + ALL their metadata chains.

**What the synthesizer has access to (this is the key):**
- 7 excerpt texts (the definitions from 5 different sources spanning 6 centuries)
- Per-excerpt metadata: author, death date, school, teachers, students, work genre
- Source metadata: trustworthiness, tahqiq quality, work relationships
- Taxonomy context: prerequisite topics, sibling topics, parent chapter, narrative ordering
- Its own LLM research capability: can look up historical context, verify chains, add connections

**Engine actions:**
- Arranges positions chronologically using author death dates from source metadata
- Discovers teacher-student chain: سيبويه → الأخفش → الجرمي → المبرد → ابن السراج (from scholar authority model)
- Identifies 2 major positions: Basran (meaning-based) and Kufan (form-based)
- Classifies the disagreement: خلاف حقيقي (substantive, not verbal) — the definitions genuinely produce different results in edge cases
- Identifies the post-classical consensus (Ibn Malik's merged definition)
- Generates edge cases and common misunderstandings
- Produces prerequisite list from taxonomy tree structure
- Produces "what to read next" from narrative ordering
- Writes the entry (see `reference/ENTRY_EXAMPLE.md` for what this looks like)

**Output (entry):** A complete encyclopedic article at the quality level shown in ENTRY_EXAMPLE.md.

**What the synthesizer ADDED that wasn't in ANY single source:**
- Chronological ordering (from metadata)
- Teacher-student chain (from scholar authority model + metadata)
- The Basran-Kufan institutional framing (from LLM research + school metadata)
- The consensus narrative (from cross-source analysis)
- Prerequisites and connections (from taxonomy tree)
- Edge cases aggregated across sources (from cross-excerpt analysis)

---

## The Metadata Accumulation Pattern

| Stage | Metadata Added | Cumulative |
|---|---|---|
| Source | Author identity, work classification, genre, trust, relationships | Foundation |
| Normalization | Structure, text quality, footnote classification | + structural |
| Passaging | Boundaries, division path | + positional |
| Atomization | Atom types, offsets | + content-type |
| Excerpting | Topic, school, quoted scholars, self-containment | + scholarly |
| Taxonomy | Final leaf, coverage, gaps | + organizational |
| Synthesizing | Temporal narrative, cross-source patterns, LLM research | → ENTRY |

**No stage removes metadata.** Every stage adds. The synthesizer receives the FULL accumulation.

This is why D-023 (metadata as synthesis fuel) is architecturally critical: if ANY stage strips metadata it doesn't "need," the synthesizer produces a poorer entry.
