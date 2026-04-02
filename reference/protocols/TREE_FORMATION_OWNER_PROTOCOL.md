# Tree Formation Protocol — Owner-Executed with ChatGPT / Codex / Gemini

> **Purpose:** Form validated taxonomy trees for sarf, balagha, aqidah, and imlaa using the same 4-researcher methodology that produced the nahw v2.0 tree (183 leaves, all 14 quality gates passed). This protocol is self-contained — the owner executes every step without Claude Chat or Claude Code involvement.
>
> **Duration:** 4 days (April 2–5, 2026)
>
> **Tools used:** ChatGPT Pro (Deep Research), Codex CLI (5.4 xhigh, infinite quota), Gemini Pro 3.1 (CLI + Chat with Deep Research)
>
> **What comes back to Claude:** Raw tree YAMLs + all research artifacts. Claude runs quality gates §9, resolves findings, executes §11 installation. That's it.

---

## How This Protocol Was Derived

The nahw tree went through: (1) 4 independent researchers → (2) architect synthesis → (3) ChatGPT comparison → (4) Fresh Claude adversarial review → (5) finding resolution → (6) 14 quality gates → (7) installation. The whole process took ~10 architect sessions.

The bottleneck was not the research or synthesis — it was the back-and-forth relay between the owner and Claude for quality gates. This protocol front-loads ALL research and synthesis work so that when Claude receives the artifacts, the quality gates session is fast and focused.

**What made nahw succeed:**
- Corpus frequency data was the single strongest signal (302 books, 70,001 headings)
- Knowledge-based trees provided organization structure
- Cross-stream scoring (knowledge + corpus agreeing = HIGH confidence) eliminated fabricated topics
- The 24-step sequential synthesis prevented ChatGPT from rushing to a tree before analyzing the data
- Adversarial review caught 3 real issues that would have been silent errors

---

## Science Specifications

### Sarf (علم الصرف) — Arabic Morphology

**Scope:** Word-level formation — how individual words are built, modified, inflected. Covers verb patterns (أوزان), derivation (اشتقاق), morphological transformations (إعلال، إبدال، إدغام).

**Boundary with nahw:** Nahw = sentence-level syntax (how words relate in a sentence). Sarf = word-level morphology (how individual words are formed). The Alfiyyah and many classical texts cover both — the tree must contain ONLY sarf.

**Sarf-side boundary topics (INCLUDE in sarf):** التصريف، الإعلال، الإبدال، الإدغام، أبنية الأسماء والأفعال، النسب، التصغير، الوقف، الإمالة، جمع التكسير، المقصور والممدود، التأنيث، الميزان الصرفي

**Nahw-side topics (EXCLUDE from sarf):** الفاعل، المبتدأ، الخبر، المفعول به، الحال، التمييز، النعت، العطف — anything about sentence structure.

**Canonical starting texts:** الكتاب (سيبويه — sarf sections), شرح الشافية (ابن الحاجب), شذا العرف في فن الصرف (الحملاوي), المغني في تصريف الأفعال, التصريف الملوكي (ابن جني), المنصف شرح التصريف (ابن جني), الممتع في التصريف (ابن عصفور)

**Target leaf range:** 100–200 leaves

**Current v1.0:** 226 leaves, 12 branches. Unvalidated.

---

### Balagha (علم البلاغة) — Arabic Rhetoric

**Scope:** The art of effective expression — how to say things beautifully, persuasively, and precisely. Classical division into three sub-sciences: علم المعاني (meanings/sentence construction), علم البيان (figurative language/imagery), علم البديع (literary embellishment).

**Boundary with nahw:** Nahw deals with grammatical correctness. Balagha deals with eloquence beyond correctness. Some topics overlap (تقديم وتأخير, حذف) — in balagha, the focus is WHY the author chose a particular construction for rhetorical effect, not WHETHER it's grammatically valid.

**Boundary with tafsir/literary criticism:** Include only the formal categorizations of balagha as a science. Exclude applied analysis of specific Quranic verses or poems (those are downstream applications, not the science itself).

**Canonical starting texts:** مفتاح العلوم (السكاكي), الإيضاح في علوم البلاغة (القزويني), تلخيص المفتاح (القزويني), أسرار البلاغة (الجرجاني), دلائل الإعجاز (الجرجاني), البلاغة الواضحة (الجارم وأمين), جواهر البلاغة (الهاشمي)

**Target leaf range:** 150–250 leaves

**Current v1.0:** 335 leaves, 4 branches. Likely too granular — 335 leaves may make LLM classification unreliable. The 3-part structure (معاني/بيان/بديع) is standard but the مقدمات branch (66 leaves) seems oversized.

---

### Aqidah (علم العقيدة) — Islamic Creed

**Scope:** Core beliefs of Islam — the six articles of faith (الإيمان بالله، الملائكة، الكتب، الرسل، اليوم الآخر، القدر), Allah's names and attributes, tawheed, methodology of Ahl al-Sunnah in matters of belief.

**Boundary with fiqh:** Aqidah covers WHAT to believe. Fiqh covers WHAT to do. Rulings about prayer, fasting, etc. are fiqh even if they have a belief component.

**Boundary with seerah/history:** Include prophets and messengers as articles of faith. Exclude detailed biographical narratives.

**School sensitivity:** Different schools (Ash'ari, Maturidi, Athari/Hanbali, Mu'tazili) organize aqidah differently. The tree should capture the TOPICS, not impose one school's framework. A leaf like "الاستواء على العرش" is a topic; how different schools interpret it is synthesis-engine work, not tree-structure work.

**Canonical starting texts:** العقيدة الواسطية (ابن تيمية), العقيدة الطحاوية (الطحاوي), شرح العقيدة الطحاوية (ابن أبي العز), لمعة الاعتقاد (ابن قدامة), كتاب التوحيد (محمد بن عبد الوهاب), شرح أصول اعتقاد أهل السنة (اللالكائي), الإبانة (الأشعري)

**Target leaf range:** 80–150 leaves

**Current v0.2:** 30 leaves, evolved from الواسطية extraction. Very incomplete — only covers الإيمان بالله in any depth. Missing entire pillars (الملائكة, الكتب, الرسل, اليوم الآخر, القدر).

---

### Imlaa (علم الإملاء) — Arabic Spelling/Orthography

**Scope:** Rules of Arabic written representation — how to write words correctly. Covers the hamza in its various positions, the alif, ta' marbuta vs ha', joined vs separated writing, and modern punctuation.

**Boundary with sarf:** Sarf covers word formation (abstract patterns). Imlaa covers how those patterns are written (orthographic representation). Example: the hamza rules are imlaa because they're about WRITING, not about word meaning or formation.

**Boundary with rasm (Quranic orthography):** Exclude the specific orthographic conventions of the Uthmani Quran script (رسم المصحف). Those follow different rules from standard Arabic imlaa.

**Canonical starting texts:** قواعد الإملاء (عبد السلام هارون), المرجع في الإملاء, المطالع النصرية للمطابع المصرية, قواعد الكتابة والإملاء, الإملاء والترقيم في الكتابة العربية

**Target leaf range:** 50–120 leaves

**Current v1.0:** 105 leaves, 8 branches. Seems reasonable in size. Quality of content unknown.

---

## Phase 1: Corpus Extraction (Codex CLI)

> **When:** Day 1 (morning + afternoon). Start this FIRST — everything else depends on it.
>
> **Tool:** Codex CLI in your WSL2 terminal, running against the local `shamela-export-samples/` directory.
>
> **What it produces:** For each science: book list, heading extraction, topic frequency, corpus gaps.

### Step 1.1: Book Identification

The nahw extraction identified 302 books from 8,417 total by scanning Shamela category metadata. You need the same for all 4 sciences.

Open your WSL2 terminal. Navigate to your kr repo directory. Run Codex CLI with this prompt:

```
codex --model o4-mini-high "

TASK: Identify books per Islamic science from the Shamela export collection.

CONTEXT: The directory shamela-export-samples/ contains ~20,000 .htm files exported from المكتبة الشاملة. Each .htm file is a book or volume. The files contain Arabic scholarly text with HTML markup. Near the top of each file, there is typically category metadata (like 'النحو والصرف', 'البلاغة', 'العقيدة', etc.) embedded in the HTML.

The file reference/research/codex_nahw_books_identified.json shows the format used for nahw (302 books from 8417 scanned). Reproduce this format for 4 sciences.

SCIENCES TO IDENTIFY:
1. sarf (الصرف / التصريف) — Arabic morphology. Shamela categories likely include: 'النحو والصرف', 'الصرف'. Books with 'صرف' or 'تصريف' in titles.
2. balagha (البلاغة) — Arabic rhetoric. Categories: 'البلاغة'. Books with 'بلاغة' or 'بيان' or 'بديع' or 'معاني' in titles.
3. aqidah (العقيدة) — Islamic creed. Categories: 'العقيدة', 'التوحيد', 'أصول الدين'. Books with 'عقيدة' or 'توحيد' or 'اعتقاد' in titles.
4. imlaa (الإملاء) — Arabic spelling. Categories: 'الإملاء'. Books with 'إملاء' or 'كتابة' or 'رسم' in titles.

METHODOLOGY:
1. Scan all .htm files in shamela-export-samples/
2. For each file, extract the category from HTML metadata (look for it in the first 500 lines)
3. Also check the filename for science-specific keywords
4. Classify each book into a tier:
   - Tier A: Category explicitly matches the science
   - Tier B: Title contains science keywords but category is different (e.g., a nahw book that also covers sarf)
   - Tier C: Content analysis suggests the science (only if quick scan reveals it)
5. For sarf specifically: books in category 'النحو والصرف' need content analysis — they may be nahw books, sarf books, or both. Check if the book title or first few headings mention sarf-specific terms.

OUTPUT: Create 4 JSON files in reference/research/:
- codex_sarf_books_identified.json
- codex_balagha_books_identified.json
- codex_aqidah_books_identified.json
- codex_imlaa_books_identified.json

Each with the same format as codex_nahw_books_identified.json:
{
  'total_scanned': N,
  '{science}_count': N,
  'tier_counts': {'A': N, 'B': N, 'C': N},
  'books': [{'name': '...', 'title': '...', 'category': '...', 'match_tier': 'A/B/C', 'match_reason': '...', 'files': ['...'], 'first_file': '...'}]
}

IMPORTANT: Sarf and nahw share the same Shamela category ('النحو والصرف'). You need to distinguish them. A book is sarf if its title contains sarf-specific terms OR its chapter headings are predominantly about morphological patterns, NOT sentence structure. When in doubt, include it as Tier B.

Start by scanning 100 files to calibrate your category extraction, then process all files.
"
```

**Expected output:** 4 JSON files with book lists per science. Sarf will have the most overlap with nahw. Balagha should be cleanly separated. Aqidah may include some books from 'أصول الفقه' that need filtering. Imlaa will likely be the smallest set.

**Verification:** Check the counts. Rough expectations:
- Sarf: 100–300 books (shares category with nahw)
- Balagha: 50–200 books
- Aqidah: 100–400 books (broad category)
- Imlaa: 20–80 books (small science)

If any science has <20 books, the corpus data will be thin. That's OK — knowledge-based research compensates, and the tree gets more MEDIUM-confidence leaves.

### Step 1.2: Heading Extraction + Topic Frequency

After book identification, run Codex CLI again for each science. Do them one at a time — sarf first (closest to nahw, most data):

```
codex --model o4-mini-high "

TASK: Extract chapter headings and compute topic frequency for علم الصرف books.

INPUT: reference/research/codex_sarf_books_identified.json — contains the list of sarf books with file paths.

METHODOLOGY (same as nahw extraction that produced codex_nahw_topic_frequency.json):
1. For each book in the identified list, read the .htm file
2. Extract all chapter/section headings (look for: <h1>, <h2>, <h3>, <h4> tags, or bold text patterns like 'باب:', 'فصل:', 'مسألة:')
3. Normalize headings: strip HTML, remove leading 'باب', 'فصل', 'ذكر', 'في' particles
4. Cluster similar headings (e.g., 'الإعلال' and 'باب الإعلال' and 'فصل في الإعلال' are the same topic)
5. Count: for each unique topic, how many BOOKS discuss it (not occurrences — unique books)
6. Sort by frequency (most books first)

OUTPUT: Create these files in reference/research/:

1. codex_sarf_topic_frequency.json — Same format as codex_nahw_topic_frequency.json:
   {'total_books': N, 'total_headings': N, 'topics': [{'topic': 'الإعلال', 'count': 45, 'cluster_members': ['باب الإعلال', ...], 'variant_headings': [...]}]}

2. codex_sarf_headings_by_book.json — Raw headings per book

3. codex_sarf_corpus_gaps.md — Topics appearing in 5+ books. Format: one topic per line with book count.

4. codex_sarf_corpus_tree.yaml — A simple flat taxonomy tree built from the heading data:
   taxonomy:
     id: sarf_corpus
     title: علم الصرف (corpus-derived)
     nodes:
     - id: topic_id
       title: عنوان الموضوع
       leaf: true
       book_count: N

BOUNDARY: EXCLUDE nahw topics. If a heading is about sentence-level grammar (الفاعل, المبتدأ, المفعول, النعت, العطف, etc.), skip it. Include only word-level morphology.

Process all books. Take your time — accuracy matters more than speed.
"
```

**Repeat for balagha, aqidah, imlaa** — replace the science name, input file, and boundary instructions. For balagha, exclude nahw/sarf headings. For aqidah, exclude fiqh headings. For imlaa, exclude nahw/sarf/tajweed headings.

### Step 1.3: Content Analysis (2–3 largest books per science)

After topic frequency, run Codex CLI on the 2–3 most heading-rich books per science:

```
codex --model o4-mini-high "

TASK: Deep content analysis of the largest sarf books.

Look at codex_sarf_topic_frequency.json and codex_sarf_headings_by_book.json. Find the 3 books with the MOST headings. For each:

1. Read the full .htm file
2. Map the chapter structure: major heading → sub-headings → sub-sub-headings
3. Count distinct sub-topics per major chapter
4. Note the ORDERING of chapters (this shows pedagogical sequence)

OUTPUT: reference/research/codex_sarf_content_analysis.md

Format like codex_nahw_content_analysis.md — hierarchical outline with heading counts per chapter, summary statistics at the end (total headings, average sub-topics per chapter, maximum potential leaves at finest granularity).
"
```

**Repeat for each science.**

---

## Phase 2: Knowledge-Based Trees (ChatGPT DR + Gemini)

> **When:** Day 1 afternoon (start while Codex runs) through Day 2.
>
> **Tools:** ChatGPT Pro (Deep Research), Gemini Pro 3.1 (Chat with Deep Research or CLI)
>
> **What it produces:** 2 independent knowledge-based trees per science.

### Researcher K-1: ChatGPT Pro Deep Research

For each science, start a NEW ChatGPT conversation and enable Deep Research mode. Give this prompt (replace {science} placeholders):

---

**PROMPT FOR CHATGPT DR — SARF EXAMPLE:**

```
Build a comprehensive taxonomy tree for علم الصرف (Arabic morphology) for use in an Islamic scholarly digital library.

CONTEXT: This tree will organize 2,500+ Arabic scholarly books. Each leaf becomes an encyclopedic entry where a student reads what every scholar said on that topic. The tree must carve the science at its NATURAL scholarly joints — every leaf must be a topic a sarf student would recognize. The organization must serve encyclopedic LOOKUP (finding a topic), not pedagogical sequence (learning order).

SCOPE: Word-level morphology ONLY. This includes:
- Verb patterns and morphological scales (الميزان الصرفي, الأوزان)
- Derivation (الاشتقاق, المصادر, المشتقات from a sarf perspective)
- Morphological transformations (الإعلال, الإبدال, الإدغام, القلب المكاني)
- Noun morphology (التصغير, النسب, جمع التكسير, المقصور والممدود)
- Verb conjugation and tense formation (بناء الصيغ, الإسناد)
- Sound/weak/hamzated verb classes

EXCLUDE: Sentence-level syntax (nahw). The following are nahw topics, NOT sarf: الفاعل, المبتدأ والخبر, المفعول به, الحال, التمييز, النعت, العطف, البدل, etc.

CANONICAL TEXTS to research: الكتاب (سيبويه sarf sections), شرح الشافية (ابن الحاجب), شذا العرف في فن الصرف (الحملاوي), الممتع في التصريف (ابن عصفور), المنصف شرح التصريف (ابن جني), نزهة الطرف في علم الصرف

USE DEEP RESEARCH to:
1. Find the table of contents of at least 4 canonical sarf texts
2. Find modern Arabic university curricula for sarf
3. Check Arabic scholarly encyclopedias for sarf topic organization

DELIVERABLES:
1. A complete YAML tree following this format:
   taxonomy:
     id: sarf_v2_0
     title: علم الصرف
     nodes:
     - id: latin_transliteration    # lowercase, underscores
       title: العنوان العربي
       children:
       - id: child_id
         title: عنوان
         children:
         - id: leaf_id
           title: عنوان الورقة
           leaf: true
           confidence: HIGH   # HIGH / MEDIUM / LOW

2. A justification table: for each Level-1 branch and Level-2 topic, which canonical source(s) organize the science this way.

TARGET: 100-200 leaves, 7-12 Level-1 branches.

TREE STRUCTURE: 3 levels deep (L1 branch → L2 topic → L3 leaf). Deeper nesting only if unavoidable. Every leaf must be a distinct, recognizable sarf topic.
```

---

**Save the output** as `reference/research/chatgpt_{science}_taxonomy.yaml` and `reference/research/chatgpt_{science}_justification_table.md`.

Do this for all 4 sciences. Each DR run takes 15–60 minutes. You can start the next while one runs.

### Researcher K-2: Gemini Pro 3.1

For each science, use Gemini (Chat with Deep Research, or CLI). **The prompt is identical** to the ChatGPT DR prompt above, but given in a COMPLETELY SEPARATE session with zero context from ChatGPT's output. The two knowledge researchers MUST be independent.

**Save the output** as `reference/research/gemini_{science}_taxonomy.yaml`.

**If using Gemini CLI:** It can access the repo directly. Add this to the prompt:
```
The repo is at ~/kr/. You can read reference/research/codex_nahw_topic_frequency.json
to see an example of corpus data format, and library/sciences/nahw/tree.yaml
to see an example of a validated tree format. Do NOT read the current {science} tree
at library/sciences/{science}/tree.yaml — it is unvalidated and would bias you.
```

---

## Phase 3: Synthesis (ChatGPT Pro)

> **When:** Day 3, after all Phase 1 and Phase 2 outputs are ready.
>
> **Tool:** ChatGPT Pro (regular mode, NOT Deep Research — needs to be interactive with "continue" steps)
>
> **What it produces:** One merged tree per science.

### Preparation

For each science, create a ZIP file containing:
1. `chatgpt_{science}_taxonomy.yaml` — K-1 output
2. `gemini_{science}_taxonomy.yaml` — K-2 output (or copy to `researcher2_{science}_taxonomy.yaml`)
3. `codex_{science}_topic_frequency.json` — C-1 output
4. `codex_{science}_corpus_gaps.md` — C-1 output
5. `codex_{science}_content_analysis.md` — C-2 output
6. `codex_{science}_corpus_tree.yaml` — C-1 output
7. `codex_{science}_books_identified.json` — book list

### Synthesis Prompt

Upload the ZIP and give this prompt. **This is adapted from the nahw synthesis prompt that produced the 182-leaf tree ChatGPT built.** Replace `{SCIENCE}`, `{SCOPE}`, `{BOUNDARY}`, `{TARGET}` with the science-specific values from the specifications above.

```
You have been given a ZIP file containing research outputs from 4 independent
researchers who each built a taxonomy tree for {SCIENCE_ARABIC} ({SCIENCE_ENGLISH}).
None of the researchers saw the others' work. Your job is to synthesize them into
one validated, merged tree through careful multi-step analysis.

## CRITICAL INSTRUCTION: Work in TINY steps

This is a multi-hour task. You MUST work in small steps, completing each one FULLY
before moving to the next. After EACH step, STOP and present your findings. I will
say "continue" to proceed. DO NOT skip ahead. DO NOT try to produce the final tree
early. Quality is the ONLY metric.

## Context

This tree is for خزانة ريان (KR), a personal Islamic scholarly library processing
2,500+ Shamela Arabic book exports. Each leaf becomes an encyclopedic entry where
the owner reads what every scholar said on that topic. Wrong nodes = wrong mental
models (SILENT error — no crash, no error message).

## Scope

{SCOPE_DESCRIPTION}

## Boundary

{BOUNDARY_DESCRIPTION}

## Files in the ZIP

### KNOWLEDGE-BASED RESEARCHERS:
- Researcher 1 (ChatGPT DR): chatgpt_{science}_taxonomy.yaml
- Researcher 2 (Gemini DR): gemini_{science}_taxonomy.yaml (or researcher2_{science}_taxonomy.yaml)

### CORPUS-BASED RESEARCHERS:
- Researcher 3 (Codex heading extraction): codex_{science}_corpus_tree.yaml + codex_{science}_topic_frequency.json + codex_{science}_corpus_gaps.md + codex_{science}_books_identified.json
- Researcher 4 (Codex content analysis): codex_{science}_content_analysis.md

## STEPS (do one at a time, stop after each)

Step 1: Read Researcher 1. Inventory all L1 branches, L2 topics, leaf count per branch. STOP.
Step 2: Read Researcher 2. Same inventory. STOP.
Step 3: Read corpus data. Top 30 topics by book count. How many topics in 20+ books? STOP.
Step 4: Read content analysis. Chapter structure, sub-topic depth. STOP.
Step 5: Branch alignment table — map conceptual areas across all 4 researchers. STOP.
Step 6: Choose L1 structure. Present 2-3 competing principles, argue for/against each, choose. STOP.
Step 7-N: L2 topics per branch, one branch at a time. For each topic: which researchers include it, corpus frequency, confidence score. STOP after each branch.
Step N+1-M: Leaf decisions per branch group. Use content analysis for depth calibration. STOP after each group.
Step M+1: Corpus gap check — any topic in 15+ books missing from your tree? STOP.
Step M+2: Boundary check — verify zero {EXCLUDED_SCIENCE} topics in tree. STOP.
Step M+3: Produce the YAML tree. Go branch by branch. STOP.
Step M+4: Quality verification — leaf count ({TARGET} range), ID uniqueness, boundary scan, top-10 corpus coverage, LOW/MEDIUM confidence list, researcher disagreement log. STOP.

## Rules

1. Read files before analyzing. Never assume file contents.
2. Verify claims with corpus data (topic_frequency.json), not training data.
3. Arabic titles must use real scholarly terminology from actual books.
4. Exclude {BOUNDARY} topics.
5. When researchers disagree, state the disagreement and explain your resolution.
6. Corpus = ground truth for "what topics exist." Knowledge researchers = how to organize.
7. No rushing. If a step needs more analysis, split it.

START with Step 1.
```

**Execute by saying "continue" after each step.** This will take 20–40 "continue" messages per science. Be patient — the quality comes from the sequential analysis, not from speed.

**Save the final YAML output** as `reference/research/chatgpt_{science}_v2_synthesis.yaml`.

---

## Phase 4: Adversarial Review (Gemini Pro 3.1)

> **When:** Day 4, after all synthesis trees are ready.
>
> **Tool:** Gemini Pro 3.1 (CLI preferred — it can clone the repo and verify claims)
>
> **What it produces:** A review verdict per science with specific findings.

### Review Prompt (for Gemini CLI)

```
gemini --model gemini-2.5-pro "

TASK: Adversarial review of a taxonomy tree for {SCIENCE_ARABIC}.

CONTEXT: The repo at ~/kr/ contains a synthesized taxonomy tree at
reference/research/chatgpt_{science}_v2_synthesis.yaml. This tree was produced by
merging 4 independent researchers (2 knowledge-based, 2 corpus-based). Your job is
to find problems the synthesis missed.

READ FIRST:
1. The synthesized tree: reference/research/chatgpt_{science}_v2_synthesis.yaml
2. The corpus frequency data: reference/research/codex_{science}_topic_frequency.json
3. The validated nahw tree (as a quality reference): library/sciences/nahw/tree.yaml

CHECKS TO PERFORM:

1. FABRICATION CHECK: Pick 15 random leaves. For each, web-search the Arabic title
   as a standalone topic in {SCIENCE_ARABIC} scholarly texts. Does it appear as a
   real, distinct topic? Flag any leaf that seems fabricated or represents a
   sub-point rather than a standalone topic.

2. COMPLETENESS CHECK: Look at the top 30 topics by corpus frequency
   (codex_{science}_topic_frequency.json). Is every topic in 20+ books represented
   in the tree? For any missing: is the exclusion justified (cross-science topic,
   generic heading)?

3. BOUNDARY CHECK: Scan ALL titles for terms that belong to {EXCLUDED_SCIENCE},
   not {SCIENCE_ARABIC}. List any violations.

4. STRUCTURAL CHECK:
   - Any parent-child pairs with identical or near-identical titles?
   - Any L2 topics with a single leaf (redundant nesting)?
   - Is every leaf marked with 'leaf: true'?
   - Are all IDs unique?
   - Leaf count in target range?

5. ORGANIZATION CHECK: Do the L1 branches form coherent, non-overlapping domains?
   Would a student of {SCIENCE_ARABIC} recognize this organization?

6. METADATA CHECK: Does the tree have: id, title, language, policy fields?
   Do IDs follow the pattern ^[a-z][a-z0-9_]*$ ?

DELIVER: A verdict (READY / NOT READY) with specific findings. For each finding:
- Finding ID (e.g., F-1)
- Severity: BLOCKING (must fix) or OBSERVATION (document but don't fix)
- Description with evidence
- Suggested fix

Be adversarial. Assume the tree has errors until proven otherwise.
"
```

**If using Gemini Chat instead of CLI:** You'll need to paste the tree YAML content and the top-30 corpus topics directly into the chat, since Gemini Chat can't access local files.

**Save the review output** as `reference/research/gemini_{science}_review.md`.

---

## Day-by-Day Execution Plan

### Day 1 (April 2) — Corpus Foundation + Knowledge Trees Start

**Morning (2-3 hours):**
1. Open WSL2 terminal
2. `cd ~/kr && git pull`
3. Run Codex CLI Step 1.1: Book identification for ALL 4 sciences (one prompt, produces 4 JSON files)
4. Verify book counts seem reasonable. If a science has <20 books, note it.

**Afternoon (2-3 hours):**
5. Run Codex CLI Step 1.2: Heading extraction for **sarf** (longest — likely most books after nahw)
6. While Codex runs: Start ChatGPT DR for **sarf** knowledge tree (K-1). This runs in background.
7. Start Gemini DR for **sarf** knowledge tree (K-2) in a separate tab/session.
8. When Codex finishes sarf: start Codex on **balagha** heading extraction

**Evening (save outputs):**
9. Save all completed files to `reference/research/` in the repo
10. `git add reference/research/codex_*.json reference/research/codex_*.md reference/research/codex_*.yaml`
11. `git commit -m "corpus: book identification + heading extraction (sarf, partial)"`
12. `git push`

### Day 2 (April 3) — Corpus Complete + All Knowledge Trees

**Morning:**
1. Run Codex CLI: heading extraction for **balagha** (if not done), **aqidah**, **imlaa**
2. Run Codex CLI: content analysis for **sarf** (2-3 largest books)
3. Continue/collect ChatGPT DR and Gemini DR outputs for sarf

**Afternoon:**
4. Start ChatGPT DR for **balagha** + **aqidah** knowledge trees
5. Start Gemini DR for **balagha** + **aqidah** knowledge trees
6. Run content analysis for balagha

**Evening:**
7. Start ChatGPT DR for **imlaa** knowledge tree
8. Start Gemini DR for **imlaa** knowledge tree
9. Run content analysis for aqidah + imlaa
10. Commit all outputs: `git commit -m "corpus + knowledge trees: all 4 sciences"`

### Day 3 (April 4) — Synthesis

**Morning:**
1. Collect any remaining knowledge tree outputs
2. Prepare ZIP files for each science (all 4 researcher outputs)
3. Start ChatGPT synthesis for **sarf** (highest priority — closest to nahw)
4. Say "continue" through all steps. This takes 30-60 minutes of active interaction.

**Afternoon:**
5. Start ChatGPT synthesis for **balagha**
6. If time: start synthesis for **aqidah**

**Evening:**
7. Complete aqidah synthesis
8. Start synthesis for **imlaa** (smallest, fastest)
9. Commit all synthesis YAMLs

### Day 4 (April 5) — Adversarial Review + Handoff

**Morning:**
1. Complete any remaining syntheses
2. Run Gemini adversarial review for **sarf**
3. Run Gemini adversarial review for **balagha**

**Afternoon:**
4. Run Gemini adversarial review for **aqidah**
5. Run Gemini adversarial review for **imlaa**

**Evening:**
6. Commit all review outputs
7. `git push`
8. Handoff to Claude (next week): all artifacts in repo, ready for quality gates

---

## File Management

### Where to save everything

All files go in `reference/research/` with science-prefixed names:

```
reference/research/
  codex_{science}_books_identified.json    # Step 1.1
  codex_{science}_topic_frequency.json     # Step 1.2
  codex_{science}_headings_by_book.json    # Step 1.2
  codex_{science}_corpus_gaps.md           # Step 1.2
  codex_{science}_corpus_tree.yaml         # Step 1.2
  codex_{science}_content_analysis.md      # Step 1.3
  chatgpt_{science}_taxonomy.yaml          # Phase 2 K-1
  chatgpt_{science}_justification_table.md # Phase 2 K-1
  gemini_{science}_taxonomy.yaml           # Phase 2 K-2
  chatgpt_{science}_v2_synthesis.yaml      # Phase 3
  gemini_{science}_review.md               # Phase 4
```

### Git commits (do these at end of each day)

```bash
cd ~/kr
git add reference/research/
git commit -m "taxonomy research: {description of what was done today}"
git push
```

### If a tool produces output in a format you can't save directly

Copy-paste the output into a text file. For YAML trees, make sure the file starts with `taxonomy:` and uses proper indentation (2 spaces). If ChatGPT produces the tree in a code block, copy just the YAML content (without the ``` markers).

---

## Quality Checklist (Owner Self-Check Before Handoff)

Before declaring "ready for Claude," verify for EACH science:

- [ ] Corpus data exists: `codex_{science}_books_identified.json` has >10 books
- [ ] Topic frequency exists: `codex_{science}_topic_frequency.json` is not empty
- [ ] Knowledge tree 1 exists: `chatgpt_{science}_taxonomy.yaml` is valid YAML with Arabic titles
- [ ] Knowledge tree 2 exists: `gemini_{science}_taxonomy.yaml` is valid YAML with Arabic titles
- [ ] Synthesis tree exists: `chatgpt_{science}_v2_synthesis.yaml` is valid YAML
- [ ] Synthesis tree has `taxonomy:` top-level key with `id`, `title`, `nodes`
- [ ] Synthesis tree leaf count is within target range (check the science spec above)
- [ ] Adversarial review exists: `gemini_{science}_review.md`
- [ ] All files committed and pushed to GitHub

**If a science is incomplete** (e.g., Codex couldn't find enough books, or ChatGPT DR timed out): that's fine. Push what you have. Claude will assess what's usable and what needs re-running.

---

## What Claude Does With These Artifacts

When you're back next week with refreshed Claude usage:

1. **Clone repo, read artifacts** — inventory what's complete per science
2. **Run quality gates (§9)** — all 14 gates from `TAXONOMY_TREE_PROTOCOL.md` on each synthesis tree
3. **Resolve findings** — fix any issues found by quality gates or Gemini review
4. **Install trees (§11)** — archive old trees, install new ones, update registry, fix tests
5. **One session per science** — each science gets its own focused session

The more complete your artifacts are, the faster this goes. The corpus data is the MOST VALUABLE artifact — if you only get that done, Claude can work with it. The synthesis tree is SECOND most valuable. The knowledge trees alone (without corpus) are useful but weaker.

---

## Troubleshooting

**Codex CLI can't find the shamela-export-samples/ directory:**
- Make sure you're in the kr repo root: `cd ~/kr`
- Check: `ls shamela-export-samples/ | head -5`
- If the directory isn't there, you may need to re-download or link it

**ChatGPT DR takes too long or fails:**
- DR mode has a time limit. If it fails, try regular ChatGPT with web browsing enabled instead. Give it the same prompt but say "search the web for canonical texts."
- Alternatively, use Gemini DR as both K-1 and K-2 (in separate sessions)

**Gemini can't produce valid YAML:**
- Ask it to produce the tree, then ask: "Now output this as a clean YAML file with proper indentation, starting with 'taxonomy:' as the top-level key"
- If still broken, save as-is — Claude can fix YAML formatting during quality gates

**A science has very few books (<20):**
- This is expected for imlaa. The corpus data will be thin.
- Lean more heavily on knowledge-based trees for that science
- Set confidence to MEDIUM for any leaf without corpus backing

**Sarf/nahw overlap — can't tell which books are sarf:**
- Use the heading-based approach: if a book's headings are mostly about أوزان, تصريف, إعلال, إبدال → it's sarf
- If headings are mostly about فاعل, مبتدأ, مفعول, حال → it's nahw
- Books covering both: include as Tier B for sarf AND nahw already has them
