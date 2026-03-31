# Nahw Taxonomy Tree — Adversarial Cold-Read Review

## Your role

You are an adversarial reviewer with ZERO prior context. You have never seen this tree, the research that produced it, or the decisions behind it. This is deliberate — fresh eyes catch what deep-context reviewers miss. Your job is to find what everyone else missed.

## What you're reviewing and why it matters

A nahw (Arabic syntax) taxonomy tree that will classify excerpts from **2,500 Arabic grammar books** in the owner's Islamic scholarly library (خزانة ريان). Each leaf becomes an encyclopedic entry — where the owner reads what every scholar said on that topic, where they agree, where they differ, and why.

**THE KNOWLEDGE INTEGRITY AXIOM:** Every wrong node in this tree — a fabricated topic, a misplaced concept, a missing real topic — becomes a WRONG BELIEF in the owner's mind. The damage is **silent**: no crash, no error message. The owner is a beginning Islamic studies student who trusts this tree completely. If a leaf is wrong, the owner builds a wrong mental model of how nahw is organized. This is not hypothetical — it is the central risk the entire KR system is designed to prevent.

**How the tree was produced:** 4 independent researchers built trees from different evidence (2 from canonical texts + web research, 2 from analysis of 302 actual books with 70,001 headings). Two AI providers independently synthesized the 4 inputs, then the syntheses were merged. Multiple layers of review preceded you. Your job: find what all those layers missed.

---

## The tree to review

[PASTE THE FINAL MERGED YAML HERE]

---

## Setup: Clone the repo and read evidence files

```
git clone https://{token}@github.com/rayanino/kr.git
```

Read these files — they are your primary evidence:
1. `reference/research/codex_nahw_topic_frequency.json` — **302-book corpus frequency data. This is ground truth for which topics are real.** A topic appearing in 20+ books is definitely real. A topic in 0 books may be fabricated.
2. `reference/research/codex_nahw_corpus_gaps.md` — 399 topics in 5+ books not captured by the corpus tree. Potential gaps in the final tree.
3. `reference/research/codex_nahw_content_analysis.md` — Sub-topic analysis of 3 largest books (شرح المفصل, النحو الوافي, ضياء السالك). Shows how many distinct sub-topics exist within each chapter.
4. `reference/research/nahw_v2_leaf_inventory.md` — The leaf inventory with per-leaf reasoning. Explains WHY each leaf was included and what confidence level was assigned.

---

## Review instructions

Work through the checks below **one at a time**. Each check must be substantive — if a check takes fewer than ~300 words, you are not going deep enough. Present findings for each check before moving to the next. Use tool calls (code execution, web search, file reading) for every claim — never rely on memory or general knowledge alone.

**STOP after each major check.** I will say "continue" before you proceed. This prevents rushing.

---

### Check 1: Structural and mechanical soundness

Verify with tool calls (parse the YAML, run scripts):

- Does the YAML parse without errors? (Load it in Python with `yaml.safe_load`)
- Does every non-leaf node have `children`?
- Does every leaf have `leaf: true`?
- Are ALL IDs unique across the entire tree? (Extract all IDs, check for duplicates)
- Do all IDs use only lowercase Latin letters and underscores? (No spaces, no Arabic, no hyphens)
- Count: total nodes, total leaves, total L1 branches, total L2 topics
- Does the tree load in the KR taxonomy engine? Run:
  ```python
  import sys; sys.path.insert(0, '.')
  from pathlib import Path
  from engines.taxonomy.src.tree_loader import load_tree
  tree = load_tree(
      science_id="nahw",
      registry_path=Path("library/sciences/taxonomy_registry.yaml"),
      override_path=Path("PATH_TO_THE_MERGED_YAML"),
  )
  print(f"Loaded: {tree.leaf_count} leaves, version: {tree.tree_version}")
  ```
  (If the loader crashes, report the error — it means the YAML format is incompatible with the engine.)

**STOP. Wait for "continue."**

### Check 2: Scholarly reality verification

Pick **15 leaves using a systematic method** — not cherry-picked. Use this approach: count total leaves, generate 15 evenly-spaced indices (e.g., for 146 leaves: leaf 1, 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141). Read the Arabic title of each selected leaf.

For each of the 15 leaves:
1. Search the web for the Arabic title + "نحو" (to confirm it's specifically a nahw topic)
2. State whether you found it discussed as a nahw topic in at least one named Arabic grammar book
3. If you CANNOT find evidence it's a real nahw topic, flag it as **potentially fabricated**

Report: how many of the 15 passed? How many failed? List every failure.

**STOP. Wait for "continue."**

### Check 3: Coverage completeness

Read `codex_nahw_topic_frequency.json`. This file shows how many of the 302 actual nahw books discuss each topic.

1. List ALL topics appearing in **20+ books** (these are the most important nahw topics — any of them missing from the tree is a serious gap)
2. For each: is it in the tree? Check by searching for the Arabic term or close synonyms in the tree's leaf titles
3. If a topic is missing: is it sarf (acceptable exclusion)? Is it a generic heading (المقدمة, وفاته — acceptable exclusion)? Or is it a genuine nahw gap?
4. List ALL genuine gaps with their book count

Then check `codex_nahw_corpus_gaps.md` for any topics in **15+ books** that were flagged as uncaptured. Are any of these still missing from the final tree?

**STOP. Wait for "continue."**

### Check 4: Sarf boundary verification

Search ALL leaf titles (and L2 topic titles) in the tree for these sarf markers:
- تصريف, إعلال, إبدال, إدغام
- أبنية (as in أبنية المصادر or أبنية الأفعال)
- نسب, تصغير, وقف, إمالة
- تكسير (as in جمع التكسير — debatable, explain your reasoning)
- ممدود, مقصور (as in الممدود والمقصور — debatable, explain your reasoning)
- تأنيث (as in التأنيث — sarf topic)

Report any hits. For each hit:
- Is this a genuine sarf topic that leaked into the nahw tree? (Remove it.)
- Or is it a nahw topic that happens to share terminology with sarf? (Keep it, explain why.)
- For debatable cases (تكسير, مقصور/ممدود): which side do you come down on and why?

**STOP. Wait for "continue."**

### Check 5: Organizational critique

Read the L1 branches. Think about this tree as an **encyclopedic reference** — not a textbook. The owner looks up a topic to read what scholars say. The organization must serve LOOKUP, not learning sequence.

Answer these questions with reasoning:

1. **L1 coherence:** Does each L1 branch cover a coherent area of nahw? Or are any branches grab-bags of unrelated topics?
2. **L1 balance:** Count leaves per L1 branch. Is any branch dramatically over-represented (30+ leaves) or under-represented (fewer than 5 leaves) relative to its scholarly importance?
3. **Merge candidates:** Are there any L1 branches so small (fewer than 5 leaves total including children) that they should be merged into a larger branch?
4. **Split candidates:** Are there any L1 branches so large or heterogeneous that they should be split?
5. **Misplacement:** Is any topic placed under a branch where a nahw student would NOT think to look for it? (This is the most important question — a misplaced topic is functionally invisible.)

**Distinguish between two types of findings:**
- **Organizational preferences:** "I would group X under Y instead of Z" — these are opinions. Flag them as suggestions, not blocking findings.
- **Objective errors:** "Topic X is placed under branch Y, but no Arabic grammar book has ever discussed X as part of Y" — these are blocking findings.

Label each finding clearly as PREFERENCE or ERROR.

**STOP. Wait for "continue."**

### Check 6: Sibling distinctness

For every L2 topic that has **4 or more leaves**, read all sibling leaves under that topic.

For each sibling pair:
- Can you state in ONE sentence what makes each leaf different from its sibling?
- If two leaves overlap significantly (a student reading both entries would encounter mostly the same content), flag them as **potential merge candidates**

List every flagged pair with your reasoning.

**STOP. Wait for "continue."**

### Check 7: Granularity uniformity

1. Count leaves per L1 branch. Present the distribution.
2. Count leaves per L2 topic. Present the top 10 and bottom 10.
3. Is any L2 topic with **8+ leaves** so large it should be split into sub-topics (add an L3 level)?
4. Is any L1 branch with only **1–2 L2 topics** potentially too coarse?
5. Are there any "single-child" nodes? (An L2 topic with exactly 1 leaf — the leaf could just BE the L2 topic.)

**STOP. Wait for "continue."**

### Check 8: Adversarial synthesis — what's the worst thing about this tree?

Having completed all checks, step back and think holistically:

1. If you had to name the **single biggest problem** with this tree, what would it be?
2. If you could change **ONE structural decision** (an L1 branch split, a topic relocation, a granularity change), what would you change and why?
3. What is the most **dangerous false assumption** this tree might embed? (Example: assuming a topic is nahw when scholars actually classify it differently.)
4. Is there any **systematic bias** visible? (Example: over-representing topics from one canonical text while under-representing others.)

---

## Final verdict

After ALL checks are complete, deliver your verdict:

**READY** — The tree is ready to be committed as the validated nahw taxonomy for a 2,500-book Islamic scholarly library.
- State your confidence level (HIGH / MEDIUM / LOW)
- List any minor concerns that don't block but should be noted

**NOT READY** — The tree has blocking findings that must be fixed before commit.
- List every blocking finding with severity (HIGH / MEDIUM)
- For each: state what must be changed and why
- Distinguish between ERRORS (objective problems) and strong PREFERENCES (organizational opinions you feel strongly about)

---

## Rules

- You are an **ADVERSARIAL** reviewer. Your job is to find problems, not to praise. If you find yourself writing "this looks good" without having checked it with a tool call, stop and check it.
- Every claim must be backed by **evidence** (file data, web search, tool output, code execution). "Looks fine" is not an acceptable assessment for any check.
- If you're unsure about a topic, **search for it** — don't guess. An uncertain claim presented as fact is more dangerous than admitting uncertainty.
- **Permission to say "I don't know":** If you encounter a nahw concept you're not confident about, say so and flag it for human expert review rather than guessing.
- The Knowledge Integrity Axiom applies to YOUR output too: a false "READY" verdict means wrong beliefs enter the owner's library. A false "NOT READY" delays progress but causes no permanent harm. When in doubt, err on the side of flagging.
