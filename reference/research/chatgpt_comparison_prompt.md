# Nahw Tree Comparison & Merge

You just completed a deep 24-step synthesis of 4 independent researcher outputs into a nahw taxonomy tree. Now I'm giving you a SECOND independent synthesis of the exact same 4 inputs, produced by a different AI provider who followed a similar methodology.

Your task: compare both trees systematically, resolve every disagreement with evidence, and produce ONE final recommended tree.

## The second tree

[PASTE nahw_v2_0_draft.yaml HERE]

## Instructions

Work in small steps. STOP after each step. I will say "continue."

### Step 1: Structural overview

Compare the two trees at the highest level:
- How many L1 branches does each tree have?
- How many total leaves?
- What organizational principle does each use?

List both trees' L1 branches side by side. Note which branches map to the same conceptual area.

STOP.

### Step 2: Points of agreement

List everything the two trees AGREE on:
- L1 branches that cover the same area (even if named slightly differently)
- L2 topics that appear in both trees under the same parent
- Leaves that both trees include
- Sarf exclusions both trees make

This is the HIGH-CONFIDENCE foundation of the merged tree. These decisions don't need further debate.

STOP.

### Step 3: L1 structural disagreements

For each L1 disagreement (branches one tree has that the other doesn't, or different ways of grouping the same topics):
- State what each tree does
- What evidence supports each approach (from the 4 researcher files you already analyzed)
- Your recommended resolution with reasoning

STOP.

### Step 4: L2 topic disagreements  

For each L2 topic that appears in one tree but not the other, or is placed in a different L1 branch:
- State the disagreement
- Check corpus frequency (from codex_nahw_topic_frequency.json)
- Check which original researchers included it
- Your recommendation: include, exclude, or relocate — with reasoning

STOP.

### Step 5: Leaf-level disagreements

For areas where the two trees have different leaf granularity (one splits finer than the other):
- State the difference
- Is the finer split supported by codex_nahw_content_analysis.md (distinct sub-topics in actual books)?
- Does the coarser version lose important distinctions?
- Your recommendation

STOP.

### Step 6: Gap check

Are there any topics that NEITHER tree includes but should be there? Check:
- codex_nahw_corpus_gaps.md (topics in 15+ books)
- Your own notes from your 24-step analysis
- Any topic where a researcher's leaf was dropped by both syntheses

STOP.

### Step 7: Produce the final recommended YAML

Taking all agreements (Step 2) plus your resolutions (Steps 3-6), produce the complete merged tree in YAML format:

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

Rules:
- leaf: true on leaf nodes, confidence: HIGH/MEDIUM/LOW
- All IDs: lowercase Latin, underscores only
- All titles: Arabic scholarly terminology  
- No sarf topics
- Target: 150-250 leaves

### Step 8: Quality verification

1. Total leaf count
2. All IDs unique?
3. Sarf keyword scan (تصريف, إعلال, إبدال, إدغام, أبنية, نسب, تصغير, وقف, إمالة)
4. Top 10 corpus topics all present?
5. List all MEDIUM and LOW confidence leaves
6. List every disagreement you resolved and which tree you sided with

STOP.

## Rules

- When the two trees agree, keep it. Don't second-guess convergent decisions.
- When they disagree, resolve with EVIDENCE from the original research files, not from your general knowledge of Arabic grammar.
- If you cannot determine which is better, keep BOTH versions as separate leaves (it's better to have a slightly redundant leaf than to lose a real topic).
- Every resolution must cite specific evidence: corpus frequency, researcher inclusion count, or content analysis sub-topic count.
- The corpus data (codex_nahw_topic_frequency.json) is the ground truth for "what topics exist." The knowledge-based researchers are the authority on "how to organize them."
