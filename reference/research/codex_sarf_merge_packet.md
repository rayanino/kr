# Sarf Merge / Review Packet

## Current State Summary
- Step 9 verdict: `READY FOR STEP 10`
- Current architect draft: [sarf_v2_0_draft.yaml](/home/rayane/kr-codex/reference/research/sarf_v2_0_draft.yaml)
- K-1 complete
- K-2 complete
- corpus-side C-1 and C-2 complete
- explicit overlay / variant-path decision is now mandatory, even if the correct answer is `no overlay warranted`

## Exact Files The External Reviewers Must Read

Upload these files for both external review phases:
- `reference/protocols/TAXONOMY_TREE_PROTOCOL.md`
- `.kr/CHARTER.md`
- `.kr/DECISIONS.md`
- `engines/taxonomy/SPEC_FULL_ORIGINAL.md`
- `reference/research/sarf_v2_0_draft.yaml`
- `reference/research/codex_sarf_books_identified.json`
- `reference/research/codex_sarf_headings_by_book.json`
- `reference/research/codex_sarf_topic_frequency.json`
- `reference/research/codex_sarf_corpus_tree.yaml`
- `reference/research/codex_sarf_corpus_gaps.md`
- `reference/research/codex_sarf_content_analysis.md`
- `reference/research/codex_sarf_granularity_audit.md`
- `reference/research/codex_sarf_taxonomy_boundary.md`
- `reference/research/codex_sarf_k1_knowledge_tree.md`
- `reference/research/codex_sarf_k2_knowledge_tree.md`
- `library/sciences/nahw/tree.yaml`

## Exact Order Of Execution

1. Run Phase 2 comparison in ChatGPT Pro / Deep Research.
2. Bring back the full raw ChatGPT output here.
3. If ChatGPT proposes a merged tree or a merged correction list, preserve it exactly.
4. Run Phase 3 adversarial review with a fresh Claude instance using:
   - the architect draft
   - the full ChatGPT output
   - the merged tree or merged correction proposal
5. Bring back the full raw Fresh Claude output here.
6. Do not manually resolve disagreements yourself before relaying them back here.

## What To Paste Into ChatGPT Pro

Paste the contents of:
- `reference/research/codex_sarf_chatgpt_comparison_prompt.md`

Then:
- attach every file from the required file list

## What To Paste Into Fresh Claude

Paste the contents of:
- `reference/research/codex_sarf_fresh_claude_review_prompt.md`

Then:
- attach the required repo files again
- additionally paste or attach:
  - full raw ChatGPT comparison output
  - merged sarf tree or merged correction proposal

## What Outputs You Must Bring Back Here

Bring back all of the following **verbatim**:
- full raw ChatGPT comparison output
- any merged tree produced by ChatGPT
- any merged correction list produced by ChatGPT
- full raw Fresh Claude review output
- explicit overlay / variant-path verdict from ChatGPT
- explicit overlay / variant-path verdict from Fresh Claude

## Warnings

- Do **not** summarize external outputs before bringing them back.
- Do **not** manually edit the external outputs.
- Do **not** collapse disagreements into a personal summary.
- Do **not** omit tables, caveats, or dissenting judgments.
- If ChatGPT or Claude refuse, fail, or partially answer, bring back the failure surface exactly.

## Overlay / Variant-Path Reminder

Both external reviewers must explicitly answer:
- `overlay warranted`
- or `no overlay warranted`

Silence on overlays is not acceptable.
If neither reviewer finds a real overlay case, that conclusion must still be stated explicitly with reasons.

## Prompt Artifacts

- ChatGPT comparison prompt: [codex_sarf_chatgpt_comparison_prompt.md](/home/rayane/kr-codex/reference/research/codex_sarf_chatgpt_comparison_prompt.md)
- Fresh Claude review prompt: [codex_sarf_fresh_claude_review_prompt.md](/home/rayane/kr-codex/reference/research/codex_sarf_fresh_claude_review_prompt.md)
- K-1 knowledge tree: [codex_sarf_k1_knowledge_tree.md](/home/rayane/kr-codex/reference/research/codex_sarf_k1_knowledge_tree.md)
- K-2 knowledge tree: [codex_sarf_k2_knowledge_tree.md](/home/rayane/kr-codex/reference/research/codex_sarf_k2_knowledge_tree.md)
