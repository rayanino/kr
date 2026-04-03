# ChatGPT Phase 2 Output — Sarf

Source: raw ChatGPT Pro / Deep Research Phase 2 comparison output, relayed by the owner.

# Sarf Taxonomy Merge Review for علم الصرف

## Merged Verdict

**architect draft needs targeted correction**. 

The six-branch architecture in `reference/research/sarf_v2_0_draft.yaml` is broadly aligned with both knowledge streams (K‑1/K‑2) on the core morphology terrain (tools/measure → verb morphology → derivational nominals → nominal transformations → internal morphophonemics), and it tracks the sparse-corpus “strong band” signals for the retained corpus (e.g., الإعلال/الإبدال/الإدغام/الميزان/التصغير/المقصور-الممدود/اسم الآلة). fileciteturn5file1turn8file1turn8file2turn7file2turn6file1

However, several issues still materially affect “leaf-as-encyclopedia-entry” correctness and stability (knowledge integrity axiom): (a) under-explicit treatment of الإلحاق as a topic-family, (b) a likely over-split of **معاني صيغ الزيادة** relative to corpus capture, (c) a small number of ambiguous/overlapping morphophonemic destinations (especially hamza-related), and (d) a few missing “apparatus” children that are stable in K-knowledge even if sparsely surfaced in C‑headings. fileciteturn4file0turn5file1turn7file2turn8file1turn8file2turn7file1

## Branch Disagreements That Still Matter

The disagreements below are not mere re-orderings; they change whether the final tree yields stable, non-bleeding encyclopedic leaves.

**A principles/“qiyās vs samāʿ” branch: include explicitly or consciously omit.**  
K‑1 includes an explicit “القياس والسماع والشاذ والعلل” branch (qiyās/samāʿ/shādh/ʿilal) as a distinct macro-family; the architect draft omits any comparable principles branch. fileciteturn8file1turn5file1  
This matters because many sarf leaves (especially masdar formation, derived nouns, and weak-verb behavior) are structurally framed by “قياسي/سماعي” and by exception-handling. If the tree has no place for that framing, the system must either (i) push these distinctions inside many unrelated leaves (risking inconsistency), or (ii) ignore the distinction (risking wrong beliefs about rule universality). The architect draft should resolve this explicitly rather than leaving it implicit. fileciteturn4file0turn5file1turn8file1

**Granularity choice for “معاني صيغ الزيادة”.**  
The draft splits “معاني صيغ الزيادة” into multiple single-meaning leaves (e.g., التعدية/المشاركة/المطاوعة/…); K‑1 also splits heavily, while the retained-corpus headings emphasize a much coarser “معاني الصيغ” shape (often a single heading). fileciteturn5file1turn8file1turn6file1turn7file1  
This disagreement matters because meaning-functions are easy to over-fabricate as independent “topics” when, in practice, they behave as a compact semantic commentary layer on the patterns rather than as standalone chapters. The leaf-as-entry constraint makes over-splitting here higher-risk than under-splitting. fileciteturn4file0turn5file1turn7file1

**Placement and internal structure of hamza-related morphology.**  
Corpus-side analysis flags hamza subcases as real but warns against “letter-slot microcases” being frozen as stable leaves; it recommends merging microcases under a broader hamza-safe leaf (analysis-stage “أحكام الهمزة”). fileciteturn7file1turn7file2  
The architect draft includes both a broad hamza leaf (“الهمزة في البنية الصرفية”) and a hamza subtopic under الإبدال (“إبدال الهمزة”), which risks two competing encyclopedic destinations for “hamza morphophonemics” unless scoped precisely. fileciteturn5file1turn7file1

**Boundary treatment of “dual/sound plurals” and the danger of nahw drift.**  
Both K‑1 and K‑2 (and the architect draft) treat المثنى وجمعا التصحيح as sarf only in the strict sense of **formation/stem-shaping**, while the nahw tree owns them as iʿrāb-marker families and syntactic behavior. fileciteturn5file1turn8file1turn8file2turn9file0  
This is a real boundary fault-line, not a stylistic difference. The draft is directionally correct, but the remaining risk is semantic drift at the leaf level (entries accidentally absorbing iʿrāb rules or agreement behavior). fileciteturn4file0turn8file0turn9file0turn5file1

## Missing Topics

### Missing Level-2 topics

**A compact “قياسي/سماعي/شاذ” principles container is missing as an explicit topic-family.**  
K‑1 treats this as a major branch; the draft has no dedicated home for how sarf rules are licensed (qiyās vs samāʿ) and how irregularity is represented. fileciteturn8file1turn5file1  
If the architect rejects this as an L1 branch to preserve six-branch architecture, it still needs a clear L2 home (likely under “مدخل علم الصرف وحدوده” or under “الأبنية والأصول والميزان”) to prevent the qiyās/samāʿ distinction from being inconsistently scattered across leaves. fileciteturn5file1turn4file0

**An explicit “الإلحاق” topic-family is under-expressed at L2 scale.**  
The draft contains “الزيادة للإلحاق” (apparatus-level) and “الملحق بالرباعي” (verb-level), but does not clearly represent الإلحاق as a coherent, cross-cutting chapter-family (what it is, why it exists, what patterns are treated as ملحقات, and how it differs from مجرد/مزيد). fileciteturn5file1turn7file2turn7file1  
Given “الإلحاق may be under-explicit” is already a named risk-area, this is a true gap, not a preference. 

### Missing children under existing containers

**Under “عدد الأصول في الكلمة”: missing the “الثنائي” (and optionally “السداسي”).**  
K‑1 includes both biliteral and sexliteral categories as part of the standard “count of radicals” apparatus. fileciteturn8file1turn5file1  
Even if rare in the retained corpus, omitting them risks an incorrect mental model that “Arabic morphology only ranges 3–5.” Under the knowledge-integrity axiom, that kind of silent simplification is not harmless. 

**Under “الأصل والزائد”: missing “الزيادة بالتضعيف” as an explicit mechanism.**  
K‑1 lists “الزيادة بالتضعيف” as a distinct augmentation mechanism alongside letters of augmentation and augmentation-for-ilḥāq/meaning. fileciteturn8file1turn5file1  
The draft implicitly covers gemination via forms like فعّل, but the apparatus-level “how augmentation happens” would be cleaner and less error-prone with an explicit leaf. fileciteturn5file1turn4file0

**Under “الإسناد الصرفي”: missing a controlled child for weak/doubled special cases.**  
K‑1 includes “أحكام الإسناد في المعتل والمضعف”. fileciteturn8file1turn5file1  
Given the draft already marks إسناد leaves as MEDIUM, adding a tight “special-case” child often reduces drift because it stops “exceptions” being ad hoc appended to the three tense-based isnād leaves. fileciteturn5file1turn4file0

## Duplicate / Overlapping Topics

**Hamza appears as both a general morphophonemic leaf and as a subtopic inside الإبدال.**

- “الهمزة في البنية الصرفية” (broad, morphophonemic leaf)
- “إبدال الهمزة” (inside الإبدال) fileciteturn5file1turn7file1  
  This is not automatically wrong, but without tight scoping it creates two plausible “final destinations” for the same question (“what happens to hamza in word-formation?”), which violates the “single, stable encyclopedic entry per leaf” spirit. 

**قلب/مقلوب appears in both ‘measure’ technique and ‘internal change’ as a concept-family.**

- “تقدير المقلوب والملحق” (inside الميزان الصرفي)
- “القلب المكاني” (internal-change leaf)   
  This can be correct if one entry is strictly “how to weigh/recognize the mqlūb form” while the other is “the phenomenon and its types/evidence.” If that distinction is not enforced, it is a near-duplicate destination. 

## Under-Granulation

**الإلحاق is still too coarse as represented.**  
Right now it is split across (a) a single apparatus leaf (“الزيادة للإلحاق”), (b) a single verb-specific leaf (“الملحق بالرباعي”), and (c) scattered “ملحقات” leaves in plural topics.   
Because الإلحاق is a recurring chapter-family in sarf manuals (and a known risk area in this packet), it likely needs at least one dedicated explanatory leaf that controls: definition, motivation, and high-level classification of mulḥaq patterns—not just isolated mentions. fileciteturn5file1turn7file1

**“الهمزة في البنية الصرفية” is under-granulated relative to stable subfamilies suggested by the retained corpus.**  
Corpus analysis records multiple hamza-change headings and recommends merging microcases, not deleting the topic. fileciteturn7file1turn6file1  
Then a single hamza leaf can remain valid, but then it must explicitly carry the canonical substructure internally (takhfīf vs ibdāl vs deletion/other repair) to avoid “two-leaf hamza drift.” fileciteturn5file1turn4file0

**“التقاء الساكنين في البنية الصرفية” is likely too coarse if it remains a production leaf.**  
K‑1 treats it as a family with at least two stable repair strategies (by deletion vs by vowel/harakah). fileciteturn8file1turn5file1  
If the draft keeps it as a leaf, the entry will need an internal split anyway; if that split is stable, the tree should reflect it.

## Over-Granulation

**“معاني صيغ الزيادة” is probably over-split for a sparse retained corpus.**  
The draft creates multiple meaning-function leaves.   
But corpus-side analysis and frequency signals primarily capture “معاني الصيغ” as a coarse heading-family (and the granularity audit explicitly warns about not creating leaves for micro-buckets or author-local presentation). fileciteturn7file2turn7file1turn6file1  
A safer approach is one stable leaf “معاني صيغ الزيادة” with internal subheadings for the main meaning families, instead of freezing each meaning as a separate encyclopedic leaf.

**Potential over-splitting risk in dual/sound plural subcases.**  
The draft splits dual formation into multiple subtype leaves (تثنية الصحيح/المقصور/المنقوص/الممدود, etc.) and similarly splits sound plurals.   
This is not necessarily wrong (these are standard subcases), but it is the highest nahw-overlap zone; if the corpus does not robustly support these as standalone stable chapters, they may be better as internal substructure within one “المثنى (من جهة الصياغة)” entry. fileciteturn7file2turn9file0turn4file0

## Boundary Audit

### Nahw leakage

**Net judgment: no direct nahw topics appear as-is, but several leaves are “drift risks.”** fileciteturn5file1turn8file0

- The boundary guard explicitly lists must-exclude nahw topics (فاعل/مفعول/مبتدأ/خبر/إعراب/عامل/…); none of these appear in the architect draft as leaves, which is correct. fileciteturn8file0turn5file1
- However, the nahw tree contains overlapping *names* that can attract bleed: e.g., المثنى وجمعا التصحيح appear in nahw under “علامات الإعراب والنيابة فيها,” emphasizing declensional markers.   
  The sarf draft’s dual/plural leaves must remain strictly “formation and stem-change,” never “iʿrāb signs, syntactic agreement, or governance.” fileciteturn5file1turn4file0
- “البناء للمفاعل/للمفعول” overlaps the nahw area “النائب عن الفاعل/بناء الفعل للمجهول.” The sarf leaf must be explicitly “patterning/vowel-shape formation,” not syntactic نائب الفاعل behavior. fileciteturn5file1turn9file0

### Imlaa leakage

**Net judgment: draft mostly blocks imlaa bleed, but hamza is the main hazard.** fileciteturn5file1turn7file1turn8file0

- Corpus analysis explicitly excludes “الخط” as non-sarf. The draft likewise excludes orthography topics such as independent همزة الوصل. fileciteturn7file1turn5file1
- The remaining risk is that a hamza leaf can accidentally become “رسم الهمزة” content. This must be prevented by title scoping and by internal entry policy (form-change, not writing convention). fileciteturn5file1turn4file0

### Performance / recitation leakage

**Net judgment: only one controlled risk remains: التقاء الساكنين.** 

- The protocol boundary notes allow sarf to keep “morphophonemic residue” only when it is clearly word-internal. 
- “التقاء الساكنين” is often taught in tajwīd/phonology contexts; if retained, it must be framed as **word-internal repair affecting morphological form**, not as a recitation-performance rule. fileciteturn5file1turn8file1turn7file2

## Sparse-Corpus Gap Judgment

### What the draft captures well

The retained sarf corpus is extremely sparse after strict filtering (8 books retained; no topic reaches ≥5 books). fileciteturn7file2turn6file1  
Under the review bands (≥3 strong; ≥2 admissible for investigation), the main stable corpus signals are morphophonemic operations and core apparatus (الإعلال/الإبدال/الإدغام/الميزان) plus a small set of noun-side transformations (التصغير, المقصور/الممدود, اسم الآلة). fileciteturn6file1turn7file1  
The architect draft includes all of those core families in stable, morphology-first form. fileciteturn5file1turn6file1

### What the sparse corpus suggests is still under-captured

- **Hamza subfamily signals exist but should not be exploded.** The content analysis records multiple hamza-change headings and recommends merging microcases under a stable hamza leaf rather than freezing letter-slot microcases.   
  The draft’s current “hamza general + hamza-ibdāl subleaf under الإبدال” needs consolidation/scoping so corpus signal maps cleanly to one destination family.
- **“رد بعض الأبنية إلى بعض” (count≥2) suggests a qiyās/analogy concept-family.** This is one of the few repeated meta-pattern headings in the retained corpus list, and it points toward the principle layer that is currently missing from the draft as an explicit home. fileciteturn6file1turn7file2
- **الإلحاق remains a flagged risk area and is not yet sufficiently centralized.** The corpus and analysis repeatedly encounter mulḥaq markers (“ذو الزيادة,” “الزيادة للإلحاق,” “الملحق بالرباعي”) but warn against wrapper headings; this combination is exactly when the taxonomy needs a clean, explicit explanatory node-family. fileciteturn6file1turn7file2turn5file1

### What looks like corpus noise or wrapper noise

The audit explicitly warns against creating leaves for unstable presentation wrappers and ambiguous headings (e.g., الجمع as a bare heading, الحذف as a floating label, الوقف والإمالة, and الخط/imlaa). fileciteturn7file2turn7file1  
The draft’s exclusion stance on الوقف والإمالة and independent همزة الوصل matches this, and should not be reversed merely because a few retained books contain these headings. fileciteturn5file1turn7file1turn8file0

## Overlay / Variant-Path Review

**no overlay warranted**. fileciteturn4file0turn4file2turn5file1

Rationale:

- The main cross-stream differences (K‑1 vs K‑2 vs draft) are primarily about **(a) inclusion/exclusion of boundary topics** (e.g., همزة الوصل/الوقف/الإمالة, الممنوع من الصرف, نونا التوكيد) and **(b) granularity choices**, not about a stable, tradition-backed alternate route that re-parents the *same canonical nodes*. fileciteturn8file1turn8file2turn5file1
- Overlay policy is reserved for defensible route-level alternatives that should not be erased (project law), but here the disagreements are better resolved by boundary law and leaf-stability criteria rather than preserved as parallel routes. fileciteturn4file0turn4file1turn4file2turn8file0
- The only superficially “route-like” difference is whether to add a separate principles branch (qiyās/samāʿ) vs embed it throughout leaves. That is not an alternate path to the same nodes; it is a modeling choice about whether that concept-family exists as a node-family at all. Overlays should not be used to excuse that kind of unresolved modeling decision. fileciteturn4file0turn8file1turn5file1

## Merged Correction List

### Must fix

**Tighten hamza family scoping to prevent duplicate encyclopedic destinations.**  
Either:

- make “الهمزة في البنية الصرفية” a non-leaf container and route the hamza-relevant ibdāl material under it, **or**
- keep both but rename/scope so the hamza leaf is “غير الإبدال” aspects (and the ibdāl leaf is explicitly “substitution rules only”), with explicit non-imlaa disclaimer. fileciteturn5file1turn7file1turn4file0

**Make الإلحاق explicit as a coherent topic-family (not just scattered mentions).**  
Add one stable leaf (or convert an existing node) that defines الإلحاق and gives a high-level classification of mulḥaq patterns, then keep “الزيادة للإلحاق” as the apparatus hook or merge them if redundant. fileciteturn5file1turn7file2turn4file0

**Enforce “formation-only” policy on the high-risk nahw-overlap noun transformation leaves.**  
For المثنى وجمعا التصحيح: ensure titles and internal scope exclude iʿrāb signs and syntactic agreement. This is a correctness constraint, not stylistic tuning. fileciteturn5file1turn9file0turn8file0turn4file0

### Should fix

**Reduce over-granulation in “معاني صيغ الزيادة”.**  
Prefer one stable leaf “معاني صيغ الزيادة” with internal subheadings (التعدية/المشاركة/المطاوعة/…) instead of separate leaves per meaning-function—unless corpus capture materially strengthens. fileciteturn5file1turn6file1turn7file2

**Add apparatus children that are stable in knowledge streams and reduce drift:**

- add “الزيادة بالتضعيف” under الأصل والزائد,
- add “أحكام الإسناد في المعتل والمضعف” under الإسناد الصرفي. fileciteturn8file1turn5file1turn4file0

**Resolve the “qiyās/samāʿ” modeling question explicitly.**  
If a full L1 branch is too much, add one compact leaf under the intro/apparatus that sets the library-wide rule for how قياسي/سماعي distinctions are represented across sarf entries. fileciteturn8file1turn5file1turn4file0

### Optional refinement

**Extend “عدد الأصول في الكلمة” to include الثنائي (and optionally السداسي).**  
This is low-cost and reduces a potential “wrong belief” about the theoretical range. fileciteturn8file1turn5file1turn4file0

**Optionally split “التقاء الساكنين” into 2 stable repair strategies if it remains a leaf.**  
This mirrors a stable schema (by deletion vs by vowel) and reduces “one-leaf-is-too-big” pressure. fileciteturn8file1turn5file1

**Consider adding “التذكير والتأنيث” only if you can define it purely as form-marking and avoid semantic/syntactic drift.**  
K‑1 includes it; the corpus does not strongly surface it in retained headings, so this is clearly knowledge-driven and should be handled conservatively. fileciteturn8file1turn7file2turn4file0

## Final Merged Recommendation

**revise architect draft before external adversarial review**. fileciteturn4file0turn5file1
