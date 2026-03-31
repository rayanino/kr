# Nahw Taxonomy Tree — Adversarial Cold-Read Review

You are reviewing a nahw (Arabic syntax) taxonomy tree that will be used to classify excerpts from 2,500 Arabic grammar books. The tree was produced through a multi-step process: 4 independent researchers built trees from different evidence sources, two AI providers independently synthesized them, then the syntheses were merged.

Your job: find what everyone else missed. You have ZERO context about the process — you're reading the tree cold. This is deliberate. Fresh eyes catch what deep-context reviewers miss.

## The tree to review

[PASTE THE FINAL MERGED YAML HERE]

## Supporting evidence files

Clone the repo: git clone https://{token}@github.com/rayanino/kr.git
Read: reference/research/codex_nahw_topic_frequency.json (302-book corpus — the ground truth for which topics exist)
Read: reference/research/codex_nahw_corpus_gaps.md (topics in 5+ books not captured)
Read: reference/research/codex_nahw_content_analysis.md (sub-topic analysis of 3 largest books)

## Your review checklist

Answer each question with EVIDENCE (tool calls, not memory):

### 1. Structural soundness
- Does every non-leaf node have children?
- Does every leaf have `leaf: true`?
- Are all IDs unique?
- Does the YAML parse without errors?

### 2. Scholarly reality
- Pick 15 leaves at RANDOM (use a random number generator, don't cherry-pick)
- For each: search the web to verify this is a real nahw topic discussed in at least one named Arabic grammar book
- Report any that appear to be fabricated or non-standard

### 3. Coverage completeness
- Read codex_nahw_topic_frequency.json
- List ALL topics appearing in 20+ books
- For each: is it in the tree? If not, is it sarf (acceptable exclusion) or a genuine gap?

### 4. Sarf boundary
- Search all leaf titles for: تصريف, إعلال, إبدال, إدغام, أبنية, نسب, تصغير, وقف, إمالة, تكسير, ممدود, مقصور, تأنيث
- Report any sarf topics that leaked into the nahw tree

### 5. Organizational critique
- Read the L1 branches. Does this organization make sense for an ENCYCLOPEDIC reference?
- Are there any L1 branches that should be merged (too small to stand alone)?
- Are there any that should be split (too large, covering unrelated topics)?
- Is any topic placed under a branch where a student would NOT think to look for it?

### 6. Sibling distinctness
- For every L2 topic with 4+ leaves: read all sibling leaves
- Can you state in ONE sentence what makes each leaf different from its siblings?
- Flag any pair of siblings that overlap

### 7. Granularity uniformity
- Count leaves per L1 branch
- Is any branch dramatically over/under-represented relative to its scholarly importance?
- Are there any L2 topics with 8+ leaves that should be split into sub-topics?
- Are there any L1 branches with only 1-2 L2 topics that might be too coarse?

### 8. What's the worst thing about this tree?
- If you had to name the single biggest problem, what would it be?
- If you could change ONE structural decision, what would you change and why?

## Verdict

After all checks: is this tree READY to be committed as the validated nahw taxonomy for a 2,500-book Islamic scholarly library?

If YES: state your confidence level and any minor concerns.
If NO: list the blocking findings that must be fixed before commit.

## Rules
- You are an ADVERSARIAL reviewer. Your job is to find problems, not to praise.
- Every claim must be backed by evidence (file data, web search, tool output)
- "Looks fine" is not an acceptable assessment for any check
- If you're unsure about a topic, search for it — don't guess
