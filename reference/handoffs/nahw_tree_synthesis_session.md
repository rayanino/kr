# Nahw Tree Validation — Synthesis Session Handoff

> **STATUS (2026-03-31):** Steps 1–9 are **COMPLETE** — the architect's draft tree is at `reference/research/nahw_v2_0_draft.yaml` (146 leaves, 9 branches). Steps 10–11 (merge process and finalization) are **SUPERSEDED** by `reference/protocols/TAXONOMY_TREE_PROTOCOL.md` §8 and §11, which are more current and handle ChatGPT's file upload requirement. The remaining sequence is in `engines/taxonomy/STATE.md`.
>
> This handoff is now **HISTORICAL** — it documents the methodology used for the nahw pilot synthesis. For future sciences, follow the Taxonomy Tree Protocol instead.

This is a KR (خزانة ريان) session focused on producing the final validated nahw taxonomy tree (v2.0). You are the architect. This is a MAJOR DECISION — the tree structure determines where every excerpt in the owner's 2,500-book Islamic scholarly library gets placed. A wrong tree means wrong mental models.

## Session start

After cloning the repo, read these files IN THIS ORDER:
1. `engines/taxonomy/STATE.md` — full context on where we are
2. `reference/GOVERNANCE.md` — review team rules (this session is a major decision)
3. `reference/protocols/QUALITY_AXIOM.md` — you are the sole quality gate

Then `ls /mnt/skills/user/` and invoke ALL relevant skills by name. At minimum: `critical-review`, `thinking-frameworks`, `kr-research`.

## What happened before this session

Gate G3 (tree validation) was never executed — the 5 existing taxonomy trees are unvalidated AI-generated structures. A previous architect session designed a 4-researcher methodology:

**2 knowledge-based researchers** (built trees from canonical texts + web research):
- ChatGPT Pro (Deep Research): `reference/research/chatgpt_nahw_taxonomy.yaml` — **178 leaves, 8 Level-1 branches** (functional grouping). Also: `chatgpt_nahw_justification_table.md`
- Fresh Claude Opus (Research mode): `reference/research/claudechat_nahw_taxonomy.yaml` — **93 leaves, 3 Level-1 branches** (broad theoretical grouping)

**2 corpus-based researchers** (analyzed actual books in owner's Shamela collection):
- CC (heading extraction): `reference/research/codex_nahw_corpus_tree.yaml` — **82 leaves from 302 books, 70,001 headings**. Also: `codex_nahw_topic_frequency.json`, `codex_nahw_corpus_gaps.md` (399 topics in 5+ books not captured), `codex_nahw_headings_by_book.json`, `codex_nahw_hierarchy_patterns.json`, `codex_nahw_books_identified.json`
- Codex (content analysis): `reference/research/codex_nahw_content_analysis.md` — **deep sub-topic analysis of 3 largest books** (شرح المفصل 970 headings, النحو الوافي 193 headings, ضياء السالك 187 headings). Found **587 potential leaves** at maximum granularity. Average 4.52 sub-topics per chapter.

**Additional frequency data**: `reference/research/claude_nahw_topic_frequency.json`

**ChatGPT Pro was also given a synthesis prompt** to merge all 4 trees. Run `ls reference/research/` and look for any file containing "synth", "merged", or "v2" in the name. If found, read it — but treat it as ONE INPUT to your review, not as the answer. You are the architect. You decide.

**Also in the repo**: `library/sciences/nahw/tree.yaml` — the CURRENT unvalidated tree (226 leaves, 12 branches, encyclopedic/case-based). This is what v2.0 replaces. **Do NOT read this file until Step 9.** Reading it earlier will anchor your judgment.

**YAML compatibility note:** The taxonomy engine's tree loader (`engines/taxonomy/src/tree_loader.py`) requires this exact top-level structure: `taxonomy:` with `id`, `title`, `nodes`. Per-node: `id` (required), `title`, `children` (list) or `leaf: true` (boolean). Extra fields like `confidence` and `methodology` are silently ignored by the loader — include them as metadata for the synthesis audit trail.

## What this session produces

The final validated `library/sciences/nahw/tree.yaml` (v2.0), committed to the repo with updated registry, after multi-step review.

## Code fix status

Session 1 code fixes (F-1/F-3/F-4/F-6/F-7/F-8) were implemented and ACCEPTED by the previous architect session. 145 tests passing. This blocker is cleared. You do NOT need to review code — only the tree.

## CRITICAL: Work in small steps

This is a long, judgment-heavy task. Working in one pass WILL produce quality loss. The owner will say "continue" between each step. Each step should be a SEPARATE response.

### Step 1: Read the 4 researcher outputs (orientation only)

Read all 4 tree files and the content analysis. Do NOT form conclusions yet. Just inventory:
- Each researcher's Level-1 branches (list them side by side)
- Each researcher's leaf count
- Each researcher's organizational principle
- Any obvious gaps or surprises

Present the inventory. Stop.

### Step 2: Branch-level alignment

Map Level-1 branches across all 4 researchers. Answer:
- Which branches represent the SAME conceptual division despite different names?
- Which branches appear in only one researcher's output?
- Does corpus evidence (topic frequency) suggest one organization over another?

Use thinking-frameworks: what are the competing organizational principles (case-based vs functional vs theoretical)? Which serves an encyclopedic reference best? What's the strongest argument AGAINST your emerging preference?

Present the alignment table and your proposed Level-1 structure with reasoning. Stop.

### Step 3: Topic-level validation (Level-2), branch by branch

For EACH Level-1 branch from Step 2:
- List the Level-2 topics from all 4 researchers that belong there
- Note which researchers included each topic
- Cross-reference with corpus frequency data: how many books discuss this topic?
- Flag any topic that only ONE researcher proposes AND has low corpus frequency

Apply cross-stream scoring:
- Knowledge + Corpus agree → HIGH confidence, include
- Both knowledge, no corpus → MEDIUM-HIGH, include
- One knowledge + corpus → HIGH, include
- One knowledge only → MEDIUM, flag
- Corpus only → MEDIUM, include (real topic)
- Single researcher only → LOW, investigate

Present per-branch. This step may span multiple responses. Stop after each branch or group of branches.

### Step 4: Leaf-level decisions

For each Level-2 topic from Step 3, determine the leaves:
- What sub-topics do the researchers propose?
- Does `codex_nahw_content_analysis.md` provide evidence of distinct sub-topics within this chapter?
- Is each proposed leaf DISTINCT from its siblings? (Can you state in one sentence what makes it different?)
- Does the leaf represent a topic a nahw student would recognize?

Target: **150-250 total leaves.** Fewer than 100 is too coarse for 2,500 books. More than 400 is too fine for LLM-based classification.

This is the longest step. Work through it systematically. Stop periodically.

### Step 5: Corpus gap check

Read `codex_nahw_corpus_gaps.md`. It lists 399 topics that appear in 5+ books but aren't in the corpus tree. Check your emerging tree against this list:
- Are any high-frequency topics (15+ books) MISSING from your tree?
- If so, where should they go?
- Some of these are sarf topics (exclude) or duplicates (already covered under different names). But some are real gaps.

Present your findings. Stop.

### Step 6: Sarf boundary verification

The Alfiyyah covers both nahw and sarf. Verify your tree contains NO sarf/morphology topics. Sarf topics to EXCLUDE: التصريف, الإعلال, الإبدال, الإدغام, أبنية المصادر, أبنية الأسماء والأفعال, النسب, التصغير, الوقف, الإمالة, جمع التكسير (debatable — check if researchers included it), الممدود والمقصور (debatable).

Also verify: did any researcher include topics that are BOTH nahw and sarf? How do you handle the boundary cases?

Present the boundary. Stop.

### Step 7: If ChatGPT synthesis exists — compare

If ChatGPT's synthesis file is in the repo, read it now. Compare against your independent analysis from Steps 1-6:
- Where does ChatGPT agree with your conclusions?
- Where does it disagree?
- For each disagreement: who has stronger evidence?
- Did ChatGPT catch anything you missed?
- Did you catch anything ChatGPT missed?

If no synthesis file exists, skip this step.

### Step 8: Produce the draft YAML tree

Build the complete tree. Schema:

```yaml
taxonomy:
  id: nahw_v2_0
  title: علم النحو
  methodology: "4-researcher synthesis (2 knowledge + 2 corpus, 302 books)"
  validated: true
  date: YYYY-MM-DD
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
- Leaf nodes: `leaf: true` + `confidence: HIGH|MEDIUM|LOW`
- Non-leaf nodes: `children: [...]`
- IDs: Latin transliteration, underscores, no spaces
- All titles in Arabic scholarly terminology
- No sarf topics

Save to a temporary location first. Stop.

### Step 9: Self-review (adversarial)

Review your own tree adversarially. For each check, use tool calls:
1. Valid YAML? (parse it with Python)
2. All IDs unique? (extract all IDs, check for duplicates)
3. Leaf count in range? (grep -c "leaf: true" — target 150-250)
4. No sarf leakage? (search for: تصريف, إعلال, إبدال, إدغام, أبنية, نسب, تصغير, وقف, إمالة)
5. Every Level-1 branch has children? No empty branches?
6. Granularity uniformity: count leaves per Level-1 branch. Is any branch dramatically over/under-represented relative to its importance? (e.g., a branch with 50 leaves next to one with 3 suggests inconsistency)
7. Sibling distinctness: for each Level-2 topic, read its leaves. Can you state in one sentence what makes each leaf different from its siblings? If two leaves overlap, merge them.
8. Scholarly reality check: pick 10 random leaves (not cherry-picked). For EACH, verify via web search that this is a real topic discussed in at least one named Arabic grammar book. If a leaf fails this check, it may be fabricated.
9. NOW read `library/sciences/nahw/tree.yaml` (the current unvalidated tree). Compare: are there topics in the old tree that your new tree lost? Any of those losses concerning?

Present findings. Fix any issues. Stop.

### Step 10: Prepare review team prompts

The 4-provider review team must validate this tree (reference/GOVERNANCE.md). Prepare:

1. **Fresh Claude Opus cold-read prompt:** Give it the tree YAML and ask: "Is every leaf a real nahw topic? Are there obvious gaps? Does the organization make scholarly sense?"

2. **Owner validation prompt:** A simplified Arabic summary the owner can read: "Here are the major divisions and some example topics. Does this match how you've encountered nahw organized?"

Present the prompts for the owner to fire. Stop and wait for results.

### Step 11: Incorporate feedback and finalize

After review team results come back:
1. Address any findings (if blocked, fix and re-review)
2. Archive the old tree: `mkdir -p library/sciences/nahw/tree_history/` then copy current `library/sciences/nahw/tree.yaml` to `library/sciences/nahw/tree_history/nahw_v1_0.yaml`
3. Write the validated tree to `library/sciences/nahw/tree.yaml`
4. Update `library/sciences/taxonomy_registry.yaml`: add nahw_v2_0 as active, demote v1_0 to historical
5. Update `engines/taxonomy/STATE.md` to reflect Gate G3 cleared
6. Commit everything with message: `taxonomy: validated nahw tree v2.0 (4-researcher synthesis, 302 books)`
7. Flag for NEXT session: gold baseline (`engines/taxonomy/tests/fixtures/gold_baseline_nahw.yaml`) is INVALID against the new tree — must be regenerated
8. Flag for NEXT session: Session 2 NEXT.md (`reference/archive/NEXT_taxonomy_session2_deferred.md`) needs updating with new tree references
9. Run taxonomy tests to verify the new tree loads: `PYTHONPATH=. python -m pytest engines/taxonomy/tests/ -q --tb=short` — all 145 tests should still pass (tests use fixtures, not the live tree, but verify no loader crash)

## Key constraints

- The Knowledge Integrity Axiom applies: every wrong node in this tree means excerpts placed in wrong categories, which means the owner builds wrong mental models of how nahw is organized. This is a SILENT error — no crash, no warning.
- The 4-provider review team is mandatory for this decision (reference/GOVERNANCE.md).
- Quality is the ONLY metric. Take as long as needed. There are no time or budget constraints.
- You are the architect. ChatGPT's synthesis (if present) is input, not authority. You decide.
- The owner has zero technical background but IS an Islamic studies student. His experiential validation ("does this match how I learned nahw?") is the final human gate.

## Drift check

Does this still serve the goal — a study companion where the owner reads an entry and sees what every scholar said on a topic, where they agree/differ/why, all cited to frozen sources?

The tree defines what those entries ARE. Every leaf becomes an entry. The tree's quality directly determines whether the entries carve nahw at its natural joints or impose artificial divisions that fragment scholarly discussions across unrelated leaves.
