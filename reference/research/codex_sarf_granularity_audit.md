# Sarf Granularity Audit

## Current Stage 2 State
- 214 candidate sarf books were processed
- 8 books were retained after current strict Stage 2 filtering
- 139 retained topics were found in the current Stage 2 topic-frequency output
- Topics with `>=2` support: 26
- Topics with `>=3` support: 8
- Topics with `>=4` support: 1
- Topics with `>=5` support: 0
- The current flat sarf tree and gaps file are empty because no topic reaches the current `>=5` threshold.

## Concrete Blockers In The Current Analysis Lane
- The current `assign_hierarchy_context` chain in the Stage 2 package is too weak for deep structure mapping because many `غير مصنف` headings collapse into a linear parent chain.
- The current Stage 2 package excludes 37 books with `not_taxonomy_usable`, a rule that does not come from the original Stage 1 sarf boundary docs and therefore needs explicit review before it is treated as doctrine.
- The current `>=5` threshold is informative for corpus-common topics, but by itself it hides whether the empty tree reflects genuine sparsity or under-granulated support bands.

## Proposed Leaf Criterion
- The topic is unambiguously morphology-first rather than sentence-structure-first.
- The label can stand alone as a lookup target without depending on one author's phrasing or a proof fragment.
- The topic names a stable process, pattern family, derivative class, or canonical sarf chapter unit.
- The topic survives nahw-overlap review against `library/sciences/nahw/tree.yaml`.

## Proposed Anti-Overgranulation Rule
- Do not create leaves for letter-by-letter buckets, proof fragments, exercises, or author-local presentation wrappers.
- Merge micro-cases under a broader stable process leaf when the subcase is only one manifestation of that process.
- Treat bare presentation headings like `الماضي`, `المضارع`, `الأمر`, and `الجمع` as too unstable unless stronger morphology framing exists.
- If uncertain between sarf and nahw, exclude rather than split.

## Threshold Review
- Keep `>=5` as the threshold for reporting corpus-common sarf topics.
- Use `>=2` as the threshold for allowing a topic to exist as a production leaf in the next sarf tree, provided it passes the leaf criterion and zero-bleed review.
- Empty-tree verdict as corpus-common report: The current empty sarf tree is correct as a `>=5 books` corpus-common report because no current topic reaches that threshold.
- Empty-tree verdict as production tree: The current empty sarf tree is too strict if read as a production leaf set, because the audit still yields stable zero-bleed candidates with `>=2` support.

## Candidate Topics That Should Definitely Split Further
- **المصدر وتفريعاته** — support=2 books; observed forms: broad family supported by structurally rich retained books
- Broad family note: `أبنية الأسماء`, `أبنية الأفعال`, `المصدر وتفريعاته`, and `المشتقات الصرفية` all show internal fine-grained structure in the top 3 retained books and should not remain as single undifferentiated production leaves.

## Candidate Topics That Should Remain Grouped
- **أحكام الهمزة** — support=3 books; grouped because observed micro-cases are too fine or too letter-slot-local.

## Candidate Topics That Should Be Renamed
- No rename-only candidates were identified beyond routine wrapper stripping.

## Candidate Topics To Exclude Despite Appearing In Retained Books
- **مدخل التصريف** — non_sarf; book=`الممتع الكبير في التصريف`
- **حروف الإبدال** — non_sarf; book=`الممتع الكبير في التصريف`
- **الحذف** — الحذف here is too unstable as a standalone production leaf; book=`الممتع الكبير في التصريف`
- **الجمع** — ambiguous; book=`الشافية في علم التصريف - معها الوافية نظم الشافية`
- **الوقف والإمالة** — ambiguous; book=`الشافية في علم التصريف - معها الوافية نظم الشافية`
- **الخط** — non_sarf; book=`الشافية في علم التصريف - معها الوافية نظم الشافية`
- **الوقف** — ambiguous; book=`الشافية في علمي التصريف والخط`

## Keep / Split / Merge / Rename / Exclude Recommendations

| Topic | Action | Support | Notes |
|---|---|---:|---|
| الإبدال | keep | 4 | - |
| الإدغام | keep | 4 | non_sarf |
| حروف الزيادة | keep | 4 | analysis-stage morphology-safe despite stricter Stage 2 gating; micro-case or wrapper should stay under the broader increase/augmentation leaf |
| أحكام الهمزة | merge | 3 | keep hamza microcases under one stable production leaf; letter-slot hamza cases are too fine for stable production leaves |
| الإعلال | keep | 3 | - |
| التصغير | keep | 3 | - |
| الصحيح والمعتل | keep | 3 | specific subtypes observed, but only one analyzed book carries the fine split clearly |
| المصدر | keep | 3 | shared with nahw discussion traditions; keep only as morphology-first in pure sarf ordering |
| المقصور والممدود | keep | 3 | - |
| الميزان الصرفي | keep | 3 | - |
| الصفة المشبهة | keep | 2 | shared with nahw usage traditions; keep only with explicit morphology-first framing |
| القلب المكاني | keep | 2 | - |
| المصدر الميمي | keep | 2 | - |
| النسب | keep | 2 | - |
| بناء الفعل الرباعي | keep | 2 | - |
| تعريف التصريف | keep | 2 | - |
| معاني الصيغ | keep | 2 | - |
| تقسيم التصريف | keep | 1 | - |
| جمع التكسير | keep | 1 | - |
| ما يدخله التصريف وما لا يدخله | keep | 1 | - |

## Nahw-Overlap Risk Notes
- `المصدر`, `اسم الفاعل`, `اسم المفعول`, and `الصفة المشبهة` overlap with established nahw working topics in `library/sciences/nahw/tree.yaml`, but can still be admitted when the book context is explicitly derivational and morphology-first.
- `المثنى`, `جمع المذكر السالم`, `جمع المؤنث السالم`, `الأفعال الخمسة`, and `ما لا ينصرف` remain high-risk nahw-overlap candidates and should not be recommended as sarf leaves in this stage.
