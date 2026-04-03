# ChatGPT Pro / Deep Research Comparison Prompt — Sarf v2.0

Copy everything below into ChatGPT Pro / Deep Research.

Before sending:
- attach all repo files listed in `Mandatory Attached Files`
- do not summarize or compress any attached materials

---

You are reviewing a protocol-governed Arabic morphology taxonomy synthesis for **علم الصرف**.

Your job is not to defend any existing tree. Your job is to compare the architect draft against the independent knowledge streams and the corpus streams, then produce an evidence-based merged judgment.

## Core Rule

Every leaf in this tree becomes an encyclopedic entry in the owner’s knowledge system.

That means:
- zero fabricated topics
- zero nahw bleed
- zero imlaa bleed
- no unstable wrapper leaves
- no premature freezing of topics that still need standard internal splits

## Current Comparison Target

Compare the architect draft tree:
- `reference/research/sarf_v2_0_draft.yaml`

against:
- K-1 knowledge tree
- K-2 knowledge tree
- corpus-side C-1 outputs
- corpus-side C-2 outputs

Do **not** treat the architect draft as guaranteed truth. Treat it as a serious candidate that already passed an internal Step 9 review, but still may contain omissions, compressions, or boundary mistakes.

## Mandatory Attached Files

You must use all of these inputs:
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

## Boundary Law

Apply this strictly:
- `sarf` owns **word-form / isolated-word morphology**
- `nahw` owns **syntactic and declensional behavior**
- `imlaa` owns **orthographic representation**
- performance / recitation topics are excluded unless a narrow word-internal morphophonemic residue clearly remains

High-risk topics already intentionally narrowed in the draft:
- `اللزوم والتعدية من جهة الصيغة`
- `اسم الفاعل`
- `اسم المفعول`
- `الصفة المشبهة`
- `اسم التفضيل من جهة الصياغة`
- `المثنى`
- `جمع المذكر السالم`
- `جمع المؤنث السالم`
- `الهمزة في البنية الصرفية`
- `التقاء الساكنين في البنية الصرفية`

If you reject any of these, do so only with clear boundary evidence.

## Sparse-Corpus Rule

The clean retained sarf corpus is sparse. Do **not** use the original high threshold mechanically.

Use these review bands:
- `>=5 books`: corpus-common band
- `>=3 books`: strong sparse-corpus band
- `>=2 books`: admissible sparse-corpus investigation band

Do not force inclusion merely because something appears in the `>=2` band.

## Known Strengths Of The Current Draft

- resolved six-branch architecture
- explicit anti-bleed narrowing on high-risk topics
- recovered noun-pattern material from the sparse corpus:
  - `أبنية الأسماء`
  - `الاسم الثلاثي المجرد`
  - `الاسم الرباعي المجرد`
  - `الاسم الخماسي المجرد`
  - `الاسم المزيد`
- recovered `الإسناد الصرفي`
- explicit exclusion of:
  - `الممنوع من الصرف`
  - `الوقف`
  - `الإمالة`
  - independent `همزة الوصل`

## Known Risk Areas To Re-check Aggressively

- intro branch may still be slightly lean
- `الإلحاق` may be under-explicit
- `معاني صيغ الزيادة` may be knowledge-heavy relative to corpus support
- morphophonemic branch may be slightly over-compressed
- noun transformation branch remains the highest nahw-overlap zone
- sparse retained corpus is dominated by the Shafiya-family spine plus `الممتع`, so do not confuse pedagogical tradition with universal structure

## Required Tasks

1. Compare the architect draft against K-1, K-2, C-1, and C-2.
2. Detect branch disagreements that still matter.
3. Detect missing topics.
4. Detect duplicate topics or duplicated conceptual routes.
5. Detect remaining under-granulation.
6. Detect remaining over-granulation.
7. Audit nahw boundary leakage.
8. Audit imlaa boundary leakage.
9. Audit corpus under-capture using the sparse-corpus review bands.
10. Decide whether the current draft should stand substantially as-is, or whether specific corrections are needed before merge finalization.

## Overlay / Variant-Path Review

You must explicitly answer this question:

Does **علم الصرف** contain any genuine **route-level structural disagreement** that should be recorded as an **overlay / variant-path candidate** rather than silently omitted?

Use this standard:
- recommend an overlay only if there is a real, defensible alternate structural route through the science that is not just noise, redundancy, or unresolved bad organization
- do **not** recommend an overlay merely because two books arrange topics differently
- do **not** use overlays to excuse under-granulation or duplicate branches

Your answer must be one of:
- `overlay warranted`
- `no overlay warranted`

If you say `overlay warranted`, specify:
- exact topic family
- exact competing routes
- why both are legitimate

If you say `no overlay warranted`, say so explicitly with reasons.

## Output Format

Return your answer in exactly these sections:

1. `Merged Verdict`
- one-line verdict:
  - `architect draft is substantially sound`
  - `architect draft needs targeted correction`
  - `architect draft has structural defects`

2. `Branch Disagreements That Still Matter`
- only disagreements that still affect final tree quality

3. `Missing Topics`
- separate:
  - missing Level-2 topics
  - missing children under existing containers

4. `Duplicate / Overlapping Topics`
- exact duplicate or near-duplicate conceptual destinations

5. `Under-Granulation`
- topics still too coarse

6. `Over-Granulation`
- topics still too fine

7. `Boundary Audit`
- `Nahw leakage`
- `Imlaa leakage`
- `Performance / recitation leakage`

8. `Sparse-Corpus Gap Judgment`
- what the draft captures well
- what the sparse corpus suggests is still under-captured
- what looks like corpus noise or wrapper noise

9. `Overlay / Variant-Path Review`
- explicit verdict:
  - `overlay warranted`
  - `no overlay warranted`
- reasons

10. `Merged Correction List`
- exact corrections required before finalization
- grouped as:
  - must fix
  - should fix
  - optional refinement

11. `Final Merged Recommendation`
- either:
  - `accept architect draft with minor edits`
  - `revise architect draft before external adversarial review`

