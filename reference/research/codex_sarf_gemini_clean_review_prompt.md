# Gemini Clean Adversarial Review Prompt — Sarf v2.0

Use the uploaded files only. Do not rely on repo access.

You are acting as an interim external adversarial reviewer for KR's sarf taxonomy tree.

Protocol note:
- Claude is temporarily unavailable.
- You are temporarily filling the external adversarial-review role.
- Your output does NOT replace the required later Claude return review.

Review target:
- the current merged sarf tree under review at `sarf_v2_0_draft.yaml`

You must use all uploaded evidence files, especially:
- `TAXONOMY_TREE_PROTOCOL.md`
- `CHARTER.md`
- `DECISIONS.md`
- `SPEC_FULL_ORIGINAL.md`
- `sarf_v2_0_draft.yaml`
- `codex_sarf_chatgpt_phase2_output.md`
- `codex_sarf_architect_post_phase2_revision.md`
- `codex_sarf_books_identified.json`
- `codex_sarf_headings_by_book.json`
- `codex_sarf_topic_frequency.json`
- `codex_sarf_corpus_tree.yaml`
- `codex_sarf_corpus_gaps.md`
- `codex_sarf_content_analysis.md`
- `codex_sarf_granularity_audit.md`
- `codex_sarf_taxonomy_boundary.md`
- `codex_sarf_k1_knowledge_tree.md`
- `codex_sarf_k2_knowledge_tree.md`
- `nahw_tree.yaml`

Review priorities:
1. structural defects
2. fake or unstable leaves
3. under-granulation that still harms encyclopedic quality
4. over-granulation that creates brittle entries
5. boundary leakage into nahw
6. boundary leakage into imlaa
7. weak branch logic
8. unsupported recoveries

Apply this boundary law strictly:
- `sarf` = isolated-word morphology, derivation, pattern, internal form change
- `nahw` = syntax, governance, declension, agreement, `إعمال`
- `imlaa` = writing conventions and orthographic representation
- performance / recitation topics are excluded unless a narrow morphophonemic residue clearly remains

You must explicitly audit these high-risk topics:
- `اللزوم والتعدية من جهة الصيغة`
- `اسم الفاعل`
- `اسم المفعول`
- `الصفة المشبهة`
- `اسم التفضيل من جهة الصياغة`
- `المثنى من جهة الصياغة`
- `جمع المذكر السالم من جهة الصياغة`
- `جمع المؤنث السالم من جهة الصياغة`
- `أحكام الهمزة في البنية الصرفية`
- any residual `همزة الوصل` material
- `التقاء الساكنين في البنية الصرفية`
- `أبنية الأسماء`
- `الاسم الثلاثي المجرد`
- `الاسم الرباعي المجرد`
- `الاسم الخماسي المجرد`
- `الاسم المزيد`
- `الإلحاق`
- `القياسي والسماعي في الصرف`

Overlay / variant-path review is mandatory:
You must explicitly answer whether sarf has any genuine route-level structural disagreement that warrants an overlay / variant-path candidate, or whether the verdict is `no overlay warranted`.

Output format:
1. `Review Verdict`
   - `READY`
   - `NOT READY`
2. `Blocking Structural Findings`
3. `Non-Blocking Findings`
4. `Boundary Leakage Review`
   - `Nahw leakage`
   - `Imlaa leakage`
   - `Performance / recitation leakage`
5. `Granularity Review`
   - under-granulated areas
   - over-granulated areas
6. `Branch Logic Review`
7. `Overlay / Variant-Path Review`
   - `overlay warranted` or `no overlay warranted`
   - reasons
8. `Exit Recommendation`
   - `accept merged tree`
   - `revise merged tree and review again`

Be explicit and uncompromising about these 4 things:
1. whether any surviving leaves are still too broad to function as encyclopedic entries
2. whether any noun-transformation or derived-noun topics still leak nahw through internal scope
3. whether any hamza-related material still risks imlaa bleed
4. whether the correct overlay verdict is truly `no overlay warranted`

Do not soften conclusions. If a node is weak, say so directly.
