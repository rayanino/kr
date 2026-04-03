# Fresh Claude Adversarial Review Prompt — Sarf v2.0

Use this prompt only **after** Phase 2 comparison is complete and you have:
- the architect draft tree
- the ChatGPT comparison output
- the merged sarf tree or merged correction proposal

Before sending:
- attach all files listed in `Mandatory Attached Files`
- paste the full ChatGPT comparison output
- paste or attach the merged tree under review
- do not summarize, compress, or manually normalize the external outputs

---

You are a **fresh, zero-context adversarial reviewer** for a protocol-governed taxonomy tree in **علم الصرف**.

You are not asked to be polite or accommodating. You are asked to detect structural weakness, false stability, fake leaves, under-granulation, over-granulation, boundary leakage, and unsupported recoveries.

## Core Rule

Every leaf in this tree becomes an encyclopedic entry in the owner’s knowledge system.
If a leaf is fake, unstable, misplaced, or under-defined, that becomes wrong knowledge.

## Review Target

Review the **merged sarf tree** produced after Phase 2 comparison.

Use the architect draft and all upstream evidence as comparison inputs, but review the merged tree as the primary target.

## Mandatory Attached Files

You must use all of these:
- `reference/protocols/TAXONOMY_TREE_PROTOCOL.md`
- `.kr/CHARTER.md`
- `.kr/DECISIONS.md`
- `engines/taxonomy/SPEC_FULL_ORIGINAL.md`
- `reference/research/sarf_v2_0_draft.yaml`
- merged sarf tree under review
- full ChatGPT Phase 2 comparison output
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

## Review Priorities

1. structural defects
2. fake or unstable leaves
3. under-granulation that still harms encyclopedic quality
4. over-granulation that creates brittle entries
5. boundary leakage into nahw
6. boundary leakage into imlaa
7. weak branch logic
8. unsupported corpus recoveries

## Boundary Law

Apply this strictly:
- `sarf` = isolated-word morphology, derivation, pattern, internal form change
- `nahw` = syntax, governance, declension, agreement, `إعمال`
- `imlaa` = writing conventions and orthographic representation
- performance / recitation topics are excluded unless a narrow morphophonemic residue clearly remains

## High-Risk Topics To Audit Explicitly

You must explicitly review all of these:
- `اللزوم والتعدية من جهة الصيغة`
- `اسم الفاعل`
- `اسم المفعول`
- `الصفة المشبهة`
- `اسم التفضيل من جهة الصياغة`
- `المثنى`
- `جمع المذكر السالم`
- `جمع المؤنث السالم`
- `الهمزة في البنية الصرفية`
- any residual `همزة الوصل` material
- `التقاء الساكنين في البنية الصرفية`
- `أبنية الأسماء`
- `الاسم الثلاثي المجرد`
- `الاسم الرباعي المجرد`
- `الاسم الخماسي المجرد`
- `الاسم المزيد`

## Preservation Rule For Narrowed Topics

Do **not** reject a narrowed high-risk topic merely because nahw or imlaa also discuss adjacent material.

Reject it only if:
- its actual center of gravity in the merged tree has drifted out of sarf
- its remaining sarf-safe residue is too weak to justify keeping it

## Sparse-Corpus Rule

The retained sarf corpus is sparse.

Use these review bands:
- `>=5 books`: corpus-common
- `>=3 books`: strong sparse-corpus signal
- `>=2 books`: admissible sparse-corpus investigation

Do not inflate the tree to satisfy quota.
Do not ignore recurring morphology just because the clean corpus is sparse.

## Overlay / Variant-Path Review

You must explicitly answer this question:

Does the merged sarf tree reveal any genuine **overlay / variant-path** need?

Use this standard:
- an overlay is warranted only if there is a real, defensible alternate structural route through the science
- different chapter orderings alone are not enough
- overlay cannot be used to hide unresolved duplication or under-granulation

Your answer must be one of:
- `overlay warranted`
- `no overlay warranted`

If `overlay warranted`, specify:
- exact topic family
- exact competing routes
- why both are legitimate

If `no overlay warranted`, say so explicitly with reasons.

## Output Format

Return your answer in exactly these sections:

1. `Review Verdict`
- one-line verdict:
  - `READY`
  - `NOT READY`

2. `Blocking Structural Findings`
- exact node/path
- defect
- why it is blocking
- exact fix direction

3. `Non-Blocking Findings`

4. `Boundary Leakage Review`
- `Nahw leakage`
- `Imlaa leakage`
- `Performance / recitation leakage`

5. `Granularity Review`
- under-granulated areas
- over-granulated areas

6. `Branch Logic Review`
- weak branch logic
- duplicated destinations
- unsupported recoveries

7. `Overlay / Variant-Path Review`
- `overlay warranted` or `no overlay warranted`
- reasons

8. `Exit Recommendation`
- `accept merged tree`
- `revise merged tree and review again`

## Appendix A — Paste Full ChatGPT Phase 2 Output Below Before Sending

`<<PASTE FULL CHATGPT COMPARISON OUTPUT VERBATIM HERE>>`

## Appendix B — Paste Or Attach The Merged Sarf Tree Under Review

`<<PASTE OR ATTACH MERGED SARF TREE HERE>>`
