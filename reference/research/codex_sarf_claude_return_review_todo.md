# Claude Return Review TODO — Sarf

## Status

Claude chat was unavailable during the sarf external review phase.

Because of that outage, the normal protocol flow was temporarily adjusted:

- Phase 2 external comparison was run through ChatGPT Pro / Deep Research.
- A Gemini adversarial review may be used as an interim external reviewer.
- **This does not replace the required Fresh Claude adversarial review.**

## Non-Negotiable Rule

Before the sarf tree is treated as fully finalized and ready for installation
into `library/sciences/sarf/tree.yaml`, a **fresh Claude adversarial review**
must still be run against the latest merged sarf tree.

This review must be treated as a real authority lane, not as an optional polish
pass.

## What Claude Must Review

Claude must receive:

- `reference/protocols/TAXONOMY_TREE_PROTOCOL.md`
- `.kr/CHARTER.md`
- `.kr/DECISIONS.md`
- `engines/taxonomy/SPEC_FULL_ORIGINAL.md`
- the latest merged sarf tree under review
- `reference/research/sarf_v2_0_draft.yaml` if still relevant as comparison
- `reference/research/codex_sarf_chatgpt_phase2_output.md`
- `reference/research/codex_sarf_architect_post_phase2_revision.md`
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

## What Claude Must Explicitly Answer

Claude must explicitly review and answer:

1. Is the merged sarf tree structurally sound?
2. Are there any fake, unstable, or under-defined leaves?
3. Is any remaining nahw bleed present?
4. Is any remaining imlaa bleed present?
5. Are any branches still under-granulated or over-granulated?
6. Does the tree contain any genuine overlay / variant-path need?
7. Is the tree ready for finalization, or does it require another revision cycle?

## Decision Rule

If Claude finds blocking defects, the sarf tree is **not final**.

If Claude finds only non-blocking issues, the sarf tree may proceed to the
final protocol lane after those issues are judged.

## Why This File Exists

This TODO exists so the Claude return review cannot be silently forgotten after
the temporary tool outage.
