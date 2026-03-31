# Nahw Tree Comparison & Merge — Dual-Provider Synthesis

## What you're doing and why it matters

You completed an independent synthesis of 4 researcher outputs into a nahw taxonomy tree. A DIFFERENT AI provider (Claude Opus) independently synthesized the SAME 4 inputs using a similar methodology. You now have BOTH trees. Your task: compare them systematically, resolve every disagreement with evidence, and produce ONE final merged tree.

**THE KNOWLEDGE INTEGRITY AXIOM:** This tree classifies excerpts from 2,500 Arabic grammar books in the owner's Islamic scholarly library. Every leaf becomes an encyclopedic entry. Every wrong node — a fabricated topic, a misplaced concept, a missing real topic — becomes a WRONG BELIEF in the owner's mind. The damage is SILENT: no crash, no error message, no warning. The owner studies nahw trusting this tree to reflect how the science is actually organized. If a leaf is wrong, the owner builds a wrong mental model. This is the most dangerous kind of error in the entire KR system.

**Your output will be adversarially reviewed by a fresh Claude Opus instance with zero context.** Do not cut corners. Every resolution must be evidence-backed. The reviewer will check your work.

---

## The second tree (produced by Claude Opus, independent synthesis)

[PASTE THE FULL CONTENT OF reference/research/nahw_v2_0_draft.yaml HERE]

---

## Critical context about the second tree

This tree was produced by a Claude Opus architect session that followed an 11-step methodology:
- Steps 1–4: Read all 4 researcher outputs independently
- Step 5: Branch alignment across all researchers
- Step 6: Chose Level-1 structure (functional grouping, 9 branches)
- Steps 7–8: Level-2 and leaf decisions with cross-stream confidence scoring
- Step 9: Corpus gap check against codex_nahw_corpus_gaps.md
- Step 10: Sarf boundary verification
- Step 11: Self-review (YAML validation, ID uniqueness, leaf count, sarf scan, scholarly reality)

**Result:** 146 leaves, 9 Level-1 branches. All leaves have confidence ratings (HIGH/MEDIUM/LOW). The leaf inventory with per-leaf reasoning is at `reference/research/nahw_v2_leaf_inventory.md` — read it to understand WHY each leaf was included.

---

## Do you still have the research files in context?

If you completed your synthesis in THIS conversation, you should still have access to the research files. If you do NOT have them, you MUST clone the repo and read them before proceeding:

```
git clone https://{token}@github.com/rayanino/kr.git
```

**Files you need access to (verify you can reference them):**
- `reference/research/codex_nahw_topic_frequency.json` — corpus frequency (302 books). THIS IS GROUND TRUTH for which topics are real.
- `reference/research/codex_nahw_corpus_gaps.md` — 399 topics in 5+ books not captured by corpus tree
- `reference/research/codex_nahw_content_analysis.md` — sub-topic analysis of 3 largest books
- `reference/research/chatgpt_nahw_taxonomy.yaml` — Researcher 1 input (178 leaves)
- `reference/research/claudechat_nahw_taxonomy.yaml` — Researcher 2 input (93 leaves)
- `reference/research/codex_nahw_corpus_tree.yaml` — Researcher 3 input (82 leaves)
- `reference/research/nahw_v2_leaf_inventory.md` — Claude's per-leaf reasoning

**If you cannot access any of these files, STOP and tell me.** Do not proceed from memory alone.

---

## Instructions: Work in small steps. STOP after each step.

Each step must be a **substantive analysis**, not a brief summary. If a step takes less than ~400 words, you are going too fast and missing nuance. After each step, STOP and present your findings. I will say **"continue"** before you proceed to the next step. Do NOT combine steps. Do NOT skip ahead. Do NOT produce the final tree before completing Steps 1–6.

**Why this matters:** Rushing produces shallow analysis. Shallow analysis produces wrong resolutions. Wrong resolutions produce wrong nodes. Wrong nodes produce wrong beliefs in the owner's mind — permanently, silently, undetectably.

---

### Step 1: Structural overview

Compare the two trees at the highest level:
- How many L1 branches does each tree have? List them side by side with Arabic titles.
- How many total leaves does each tree have?
- What organizational principle does each use? (case-based? functional? theoretical? hybrid?)
- Which L1 branches in your tree map to which L1 branches in the Claude tree?
- Are there any L1 branches in one tree with NO equivalent in the other?

Present the side-by-side comparison. **STOP. Wait for "continue."**

### Step 2: Points of agreement

List everything the two trees AGREE on:
- L1 branches that cover the same conceptual area (even if named differently)
- L2 topics that appear in both trees under the same parent
- Leaves that both trees include (even if titled slightly differently)
- Sarf exclusions both trees make

**CRITICAL WARNING about convergence:** Agreement between the two trees is STRONG evidence but NOT proof of correctness. Both syntheses drew from the same 4 researcher inputs. If a researcher made an error, BOTH syntheses could inherit it. For each major point of agreement, ask: "Is there any reason the corpus data or canonical nahw sources would contradict this?" If yes, flag it for investigation.

This is the HIGH-CONFIDENCE foundation of the merged tree — but only AFTER you've verified it's not shared-source convergence on a wrong answer.

**STOP. Wait for "continue."**

### Step 3: L1 structural disagreements

For each L1 disagreement (branches one tree has that the other doesn't, or different groupings of the same topics):
- State what each tree does
- What evidence supports each approach? Cite specific data:
  - Corpus frequency from `codex_nahw_topic_frequency.json` (how many books?)
  - Which of the 4 original researchers organized it this way?
  - How do canonical nahw textbooks (Alfiyyah, Ajrumiyyah, Qatr al-Nada, النحو الوافي) organize this area?
- Your recommended resolution with reasoning
- What is the STRONGEST argument AGAINST your recommendation? (If you can't find one, you haven't thought hard enough.)

**STOP. Wait for "continue."**

### Step 4: L2 topic disagreements

For each L2 topic that appears in one tree but not the other, or is placed under a different L1 branch:
- State the disagreement
- Check corpus frequency from `codex_nahw_topic_frequency.json` — how many books discuss this topic?
- Check which of the original 4 researchers included it
- Apply confidence scoring:
  - Both knowledge researchers + corpus → **HIGH** (include)
  - Both knowledge researchers, no corpus → **MEDIUM-HIGH** (include)
  - One knowledge + corpus → **HIGH** (include)
  - One knowledge only → **MEDIUM** (flag for investigation)
  - Corpus only → **MEDIUM** (include — it's a real topic in actual books)
  - Single researcher only → **LOW** (investigate before including)
- Your recommendation: include, exclude, or relocate — with evidence-based reasoning

**STOP. Wait for "continue."**

### Step 5: Leaf-level disagreements

For areas where the two trees have different leaf granularity (one splits finer than the other):
- State the difference
- Is the finer split supported by `codex_nahw_content_analysis.md`? (Are there distinct sub-topics in actual books?)
- Does the coarser version lose important distinctions that a nahw student would recognize?
- Is any leaf in either tree potentially FABRICATED — a division no Arabic grammarian has ever discussed?
- Your recommendation with reasoning

Also check: are there any leaves in either tree where the title uses Arabic terminology you cannot verify in any canonical nahw source? If so, flag them — they may be LLM fabrications.

**STOP. Wait for "continue."**

### Step 6: Gap check

Are there topics that NEITHER tree includes but should be there?

Check these sources:
1. `codex_nahw_corpus_gaps.md` — focus on topics in **15+ books** (these are definitely real and common)
2. Your own notes from your synthesis
3. Any topic where an original researcher's leaf was dropped by BOTH syntheses — was the drop justified?

For each potential gap:
- Is it nahw or sarf? (If sarf, exclude.)
- Is it a generic heading like "المقدمة" or "وفاته" or "مصادر ومراجع"? (If so, exclude — not a nahw topic.)
- Is it already covered under a different name in one or both trees?
- If it's a real nahw gap: where should it go in the merged tree?

**STOP. Wait for "continue."**

### Step 7: Produce the final recommended YAML

Taking all agreements (Step 2) plus your resolutions (Steps 3–6), produce the complete merged tree in this exact YAML format:

```yaml
taxonomy:
  id: nahw_v2_0
  title: علم النحو
  methodology: "4-researcher synthesis (2 knowledge + 2 corpus, 302 books), dual-provider merge"
  validated: true
  date: 2026-03-31
  nodes:
  - id: branch_id
    title: العنوان العربي
    children:
    - id: topic_id
      title: عنوان
      children:
      - id: leaf_id
        title: عنوان الورقة
        leaf: true
        confidence: HIGH
```

**Schema rules:**
- `leaf: true` on leaf nodes only, plus `confidence: HIGH|MEDIUM|LOW`
- Non-leaf nodes have `children: [...]` and NO `leaf` field
- All IDs: lowercase Latin transliteration, underscores only, no spaces, no diacritics
- All titles: Arabic scholarly terminology (as used in actual grammar books)
- No sarf topics anywhere
- Target: **150–250 leaves** (fewer than 100 is too coarse for 2,500 books; more than 400 is too fine for LLM classification)

**Compatibility note:** The KR taxonomy engine's tree loader (`engines/taxonomy/src/tree_loader.py`) requires exactly this top-level structure: `taxonomy:` with `id`, `title`, `nodes`. Per-node: `id` (required), `title` (required), `children` (list) or `leaf: true` (boolean). Extra fields like `confidence` and `methodology` are silently ignored by the loader — include them as metadata for the audit trail.

Go branch by branch. Take your time. This is the most important step.

**STOP. Wait for "continue."**

### Step 8: Quality verification

After the YAML is complete, verify ALL of the following. Report results for each check:

1. **Leaf count** — Is it between 150 and 250?
2. **ID uniqueness** — Are ALL IDs across the entire tree unique? List any duplicates.
3. **ID format** — Do all IDs use only lowercase Latin letters and underscores? No spaces, no Arabic, no diacritics, no hyphens.
4. **Sarf keyword scan** — Search all leaf titles for these sarf markers: تصريف, إعلال, إبدال, إدغام, أبنية, نسب, تصغير, وقف, إمالة, تكسير, ممدود, مقصور, تأنيث. Report any hits and whether they should be removed.
5. **Structural integrity** — Does every non-leaf node have at least one child? Does every leaf have `leaf: true`? Are there any nodes with BOTH `children` and `leaf: true`?
6. **Top-10 corpus coverage** — List the 10 most frequent nahw topics from `codex_nahw_topic_frequency.json` (excluding sarf topics and generic headings like المقدمة/وفاته/مصادر). Is each one in the tree?
7. **Confidence inventory** — List ALL MEDIUM and LOW confidence leaves with your reasoning for each rating.
8. **Disagreement resolution log** — For EVERY disagreement you resolved in Steps 3–6, state: (a) what the disagreement was, (b) which tree you sided with, (c) the specific evidence that decided it. This is the audit trail for the adversarial reviewer.
9. **Scholarly reality spot-check** — Pick 5 leaves that were ADDED during merging (not in either original tree) or CHANGED significantly. For each, verify it is a real, recognized nahw topic by citing a named Arabic grammar textbook that discusses it.

**STOP. Wait for "continue."**

---

## Rules that apply to EVERY step

1. **When the two trees agree, keep it — but verify.** Convergence from the same inputs is evidence, not proof. If corpus data contradicts a convergent decision, flag it.

2. **When they disagree, resolve with EVIDENCE.** Evidence means: corpus frequency data (cite the number), researcher inclusion count, content analysis sub-topic count, or citation to a named canonical nahw textbook. "I think this is better" is not evidence.

3. **When evidence is ambiguous, keep BOTH versions as separate leaves.** A slightly redundant leaf is recoverable (merge later). A lost real topic is not recoverable (no one will notice it's missing).

4. **Every resolution must cite specific evidence.** Not "the corpus supports this" but "this topic appears in 23 books per codex_nahw_topic_frequency.json."

5. **The corpus data (`codex_nahw_topic_frequency.json`) is ground truth for "what topics exist."** The knowledge-based researchers are the authority for "how to organize them." Both are needed — neither alone is sufficient.

6. **No sarf topics.** If a topic is morphological (word-level formation) rather than syntactic (sentence-level grammar), exclude it. When in doubt, check: does this topic discuss how words RELATE to each other in a sentence (nahw), or how individual words are FORMED (sarf)?

7. **Arabic terminology must be real.** Every leaf title must use terminology that appears in actual Arabic grammar books. Do not invent divisions no grammarian has discussed. If you're unsure whether a term is standard, flag it.

8. **Quality over speed.** If a step needs more analysis, do more analysis. Split it into sub-steps. The owner will say "continue" when ready. There is no time pressure. There is no cost constraint. The only metric is correctness.
