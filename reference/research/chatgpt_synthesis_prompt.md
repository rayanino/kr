# Nahw Taxonomy Tree Synthesis — Deep Analysis Task

You have been given a ZIP file containing research outputs from 4 independent researchers who each built a taxonomy tree for عِلْم النحو (Arabic syntax/grammar). None of the researchers saw the others' work. Your job is to synthesize them into one validated, merged tree through careful multi-step analysis.

## CRITICAL INSTRUCTION: Work in TINY steps

This is a 3-hour task compressed into careful sequential thinking. You MUST work in small steps, completing each one FULLY before moving to the next. After EACH step, STOP and present your findings. I will say "continue" to proceed. DO NOT skip ahead. DO NOT try to produce the final tree early. The quality of this tree determines how 2,500 Arabic grammar books get classified — every wrong node means wrong knowledge in the owner's mind.

If you feel the urge to rush or combine steps: STOP. Take the current step slower instead. Quality is the ONLY metric. There is no time pressure.

---

## Context: What this tree is for

This tree is for خزانة ريان (KR), a personal Islamic scholarly library that processes 2,500+ Shamela Arabic book exports. The taxonomy tree defines the topics for an encyclopedic reference — each leaf becomes an entry where the owner reads what every scholar said on that topic, where they agree, where they differ, and why.

This means:
- The tree must carve nahw at its NATURAL scholarly joints
- Every leaf must be a topic a nahw student would recognize
- The organization must serve encyclopedic LOOKUP, not pedagogical sequence
- Wrong nodes = wrong mental models in the owner's mind (SILENT error)

---

## Files in the ZIP (reference/research/)

### KNOWLEDGE-BASED RESEARCHERS (built trees from canonical texts + web research):

**Researcher 1: ChatGPT Pro (Deep Research mode)**
- `chatgpt_nahw_taxonomy.yaml` — 178 leaves, 8 Level-1 branches
- `chatgpt_nahw_justification_table.md` — Source citations per node (which books each topic comes from)
- `chatgpt_nahw_justification_table.csv` — Same in CSV format

**Researcher 2: Fresh Claude Opus (Research mode)**
- `claudechat_nahw_taxonomy.yaml` — 93 leaves, 3 Level-1 branches

### CORPUS-BASED RESEARCHERS (analyzed actual books in the owner's Shamela collection):

**Researcher 3: Codex CLI (heading extraction from 302 books)**
- `codex_nahw_corpus_tree.yaml` — 82 leaves from 302 books, 70,001 headings
- `codex_nahw_topic_frequency.json` — Topic frequency: how many books discuss each topic (THIS IS YOUR MOST IMPORTANT EVIDENCE FILE — it tells you what topics are real based on 302 actual nahw books)
- `codex_nahw_corpus_gaps.md` — 399 topics that appear in 5+ books but aren't in the corpus tree (POTENTIAL GAPS)
- `codex_nahw_headings_by_book.json` — Raw heading data per book
- `codex_nahw_hierarchy_patterns.json` — How books structure their chapters
- `codex_nahw_books_identified.json` — Which books were analyzed

**Researcher 4: Codex CLI (deep content analysis of 3 largest books)**
- `codex_nahw_content_analysis.md` — Sub-topic analysis of شرح المفصل لابن يعيش (970 headings), النحو الوافي (193 headings), ضياء السالك (187 headings). Shows how many distinct sub-topics exist WITHIN each chapter. Average: 4.52 sub-topics per chapter. Maximum total: 587 potential leaves.

**Also:**
- `claude_nahw_topic_frequency.json` — Additional frequency data

---

## STEP-BY-STEP METHODOLOGY

### Step 1: Read Researcher 1 (ChatGPT)

Open `chatgpt_nahw_taxonomy.yaml`. List:
- All 8 Level-1 branches with their Arabic titles
- The Level-2 topics under each branch
- Total leaf count per branch

Then open `chatgpt_nahw_justification_table.md` and note which canonical texts (Alfiyyah, Ajrumiyyah, Qatr al-Nada, النحو الوافي, etc.) support each Level-1 branch.

Present your inventory. STOP.

### Step 2: Read Researcher 2 (Claude)

Open `claudechat_nahw_taxonomy.yaml`. List:
- All 3 Level-1 branches with their Arabic titles  
- The Level-2 topics under each branch
- Total leaf count per branch

Note the review log at the top of the file — Claude did a multi-stage self-review.

Present your inventory. STOP.

### Step 3: Read Researcher 3 (Codex corpus tree)

Open `codex_nahw_corpus_tree.yaml`. List:
- All Level-1 branches (there are ~16, very flat structure)
- Note which branches are SARF (morphology) not NAHW — these must be excluded

Then open `codex_nahw_topic_frequency.json`. This is the empirical ground truth — it shows how many of the 302 actual nahw books discuss each topic. Find:
- The top 30 topics by book count
- How many topics appear in 20+ books
- How many topics appear in 10+ books

Present your findings. STOP.

### Step 4: Read Researcher 4 (content analysis)

Open `codex_nahw_content_analysis.md`. Read at least the first 300 lines to understand:
- Which books were deep-analyzed
- How chapters are structured (major headings → sub-topics)
- The chapter ordering in النحو الوافي (this is the canonical pedagogical sequence)
- The summary statistics at the end

This file tells you how much DEPTH exists under each topic — crucial for deciding whether a topic should be 1 leaf or 3 leaves.

Present your findings. STOP.

### Step 5: Branch alignment table

Now that you've read all 4 researchers, create a side-by-side alignment:

For each CONCEPTUAL AREA of nahw (مقدمات, المعارف, الجملة الاسمية, الفعلية, المفاعيل, المشتقات, التوابع, النداء, الأساليب, etc.):
- What does ChatGPT call it? What branch?
- What does Claude call it? What branch?
- What does Codex corpus call it? What branch(es)?
- What corpus frequency supports it?

This alignment is the FOUNDATION for everything that follows. Take your time. Be exhaustive.

Present the alignment table. STOP.

### Step 6: Choose Level-1 structure

Based on Step 5, propose the Level-1 branches for the merged tree.

THREE competing organizational principles exist:
1. **Case-based** (Codex corpus): مرفوعات / منصوبات / مجرورات — traditional Ajrumiyyah
2. **Functional** (ChatGPT): group by grammatical function (basics → nouns → sentences → verbs → complements → derivatives → dependents → constructions)
3. **Broad theoretical** (Claude): 3 mega-branches (theory → structure → constructions)

For EACH principle, give:
- The strongest argument FOR it
- The strongest argument AGAINST it
- Whether corpus evidence (how books actually organize their chapters) supports it

Then state your choice and defend it.

Present your proposed Level-1 structure with reasoning. STOP.

### Step 7: Level-2 topics for Branch 1

Take your FIRST proposed Level-1 branch. For this branch ONLY:
- List every Level-2 topic from all 4 researchers that belongs here
- For each topic, note: which researchers include it, corpus frequency (book count from codex_nahw_topic_frequency.json)
- Apply confidence scoring:
  - Knowledge (2/2) + Corpus → HIGH
  - Knowledge (2/2), no corpus → MEDIUM-HIGH  
  - Knowledge (1/2) + Corpus → HIGH
  - Knowledge (1/2) only → MEDIUM
  - Corpus only → MEDIUM
  - Single researcher only → LOW (investigate)
- Flag any topic only ONE researcher proposes AND has low corpus frequency

Present your Branch 1 L2 analysis. STOP.

### Step 8: Level-2 topics for Branch 2

Same as Step 7, for Branch 2 only. STOP.

### Step 9: Level-2 topics for Branch 3

Same. STOP.

### [Steps 10–15: Level-2 topics for remaining branches]

Continue one branch at a time. STOP after each.

### Step 16: Leaf-level decisions for Branches 1–3

For each Level-2 topic in Branches 1–3:
- What sub-topics do the researchers propose as leaves?
- Does `codex_nahw_content_analysis.md` provide evidence of distinct sub-topics?
- Is each proposed leaf DISTINCT from its siblings? (Can you state in one sentence what makes it different?)
- Does the leaf represent a topic a nahw student would recognize?

Target total: 150–250 leaves across the entire tree. Calibrate granularity accordingly.

Present your leaf decisions for Branches 1–3. STOP.

### Steps 17–20: Leaf-level decisions for remaining branches

Continue in groups of 2–3 branches. STOP after each.

### Step 21: Corpus gap check

Open `codex_nahw_corpus_gaps.md`. It lists 399 topics in 5+ books not captured by the corpus tree. Check your emerging tree against this list:
- Are any topics in 15+ books MISSING from your tree?
- Some gaps are sarf (exclude), biographical (exclude), or generic headings (exclude)
- But some are real nahw gaps — find them

Present your gap analysis. STOP.

### Step 22: Sarf boundary check

Verify your tree contains ZERO sarf/morphology topics. Exclude:
- التصريف, الإعلال, الإبدال, الإدغام
- أبنية المصادر, أبنية الأسماء والأفعال  
- النسب, التصغير, الوقف, الإمالة
- جمع التكسير (debatable — check if knowledge researchers included it)
- الممدود والمقصور (debatable — check)
- التأنيث (sarf, not nahw)

For debatable cases: explain your reasoning.

Present your sarf boundary decisions. STOP.

### Step 23: Produce the YAML tree

Now — and ONLY now — produce the complete merged tree in YAML format:

```yaml
taxonomy:
  id: nahw_v2_0
  title: علم النحو
  methodology: "4-researcher synthesis (2 knowledge + 2 corpus, 302 books)"
  validated: true
  date: 2026-03-31
  nodes:
  - id: branch_id          # Latin transliteration, underscores, no spaces
    title: العنوان العربي    # Arabic scholarly terminology
    children:
    - id: topic_id
      title: عنوان
      children:
      - id: leaf_id
        title: عنوان الورقة
        leaf: true
        confidence: HIGH    # HIGH, MEDIUM, or LOW
```

Rules:
- Leaf nodes: `leaf: true` + `confidence`
- Non-leaf nodes: `children: [...]` (no leaf flag)
- All IDs: lowercase Latin transliteration with underscores
- All titles: Arabic scholarly terminology
- No sarf topics anywhere

This step will be LONG. Take your time. Go branch by branch.

### Step 24: Final quality verification

After the YAML is complete, verify:

1. **Leaf count** — Is it between 150 and 250?
2. **ID uniqueness** — Are all IDs unique? (List any duplicates)
3. **Sarf scan** — Search all titles for: تصريف, إعلال, إبدال, إدغام, أبنية, نسب, تصغير, وقف, إمالة, تكسير. Report any hits.
4. **Structural check** — Does every non-leaf have children? Does every leaf have `leaf: true`?
5. **Top-10 corpus coverage** — List the 10 most frequent topics from `codex_nahw_topic_frequency.json` and confirm each is in your tree
6. **Lowest-confidence leaves** — List all LOW and MEDIUM confidence leaves with your reasoning
7. **Researcher disagreements** — List any topics where you had to make a judgment call between disagreeing researchers, and explain your resolution

Present the full quality report. STOP.

---

## Rules that apply to EVERY step

1. **Read files before analyzing.** Never work from assumptions about what a file contains. Open it and read it.

2. **Verify claims with data.** If you say "this topic appears in 30 books," that number must come from `codex_nahw_topic_frequency.json`, not from your training data.

3. **Arabic terminology must be real.** Every leaf title must use terminology that appears in actual Arabic grammar books. Do not invent divisions no grammarian has discussed.

4. **Exclude sarf topics.** The Alfiyyah covers both nahw and sarf. Many "nahw" books include sarf chapters. Your tree must contain ONLY nahw (syntax/sentence-level grammar), not sarf (word-level morphology).

5. **No rushing.** If a step feels like it needs more analysis, do more analysis. Split it into sub-steps. The owner will say "continue" when ready for the next step.

6. **When researchers disagree, explain your resolution.** Don't silently pick one — state the disagreement, present evidence for each side, and explain your decision.

7. **The corpus is the ground truth for "what topics exist."** The knowledge researchers tell you how to ORGANIZE topics. The corpus researchers tell you which topics are REAL (discussed in actual books). Both are needed.

---

## START NOW

Begin with Step 1: Read `chatgpt_nahw_taxonomy.yaml` and inventory Researcher 1's tree.

Remember: STOP after Step 1 and present your findings. Do not continue to Step 2 until I say "continue."
