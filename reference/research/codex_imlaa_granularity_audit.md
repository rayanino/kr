# Imlaa Granularity Audit

## Proposed Leaf Criterion
- A production leaf must represent a distinct orthography, spelling, or punctuation rule family rather than a chapter wrapper, drill section, or author-local exercise surface.
- A leaf is justified when it is either supported by 2+ retained books or is a closed-class punctuation sign family surfaced clearly inside a dedicated punctuation chapter.

## Proposed Anti-Overgranulation Rule
- Do not turn examples, drills, workbook prompts, meta-discussion headings, or token-level joining cases into production leaves.
- Keep grouped leaves when finer subcases appear in only one retained book or depend on one author’s presentation rather than a stable corpus pattern.

## Tiny-Corpus Review
- Retained books after Stage 1 filtering: 3
- Current stable-topic threshold: book_count >= 2
- Is the corpus large enough for broad deeper splitting? No. It is large enough only for targeted refinement where the structure is unusually explicit.
- Should the book_count >= 2 threshold stay? Yes. Keep it as the default production threshold.
- The punctuation sign split is a narrow closed-class exception to under-splitting pressure, not a threshold change.
- Should the current flat tree remain intentionally small? Yes. It should stay small except for two targeted refinement reviews: the hamza branch and the punctuation branch.
- Overall verdict: the current flat tree is broadly the correct precision-first baseline for a tiny corpus, but it is locally over-granulated in the flat hamza cluster and locally under-granulated in punctuation.

## Maximum Possible Granularity
- Maximum possible leaves observed across the analyzed books: الهمزة في أول الكلمة, الهمزة في آخر الكلمة, الهمزة في وسط الكلمة, الألف اللينة في وسط الكلمة, الألف اللينة في آخر الكلمة, معرفة الأصل الواوي واليائي, زيادة الألف, زيادة الواو, نقص الألف أول الكلمة, نقص الألف وسط الكلمة, نقص الألف آخر الكلمة, نقص أل, نقص الواو, نقص الياء, نقص النون, النقص للرمز, وصل من بما قبلها, وصل ما بما قبلها, وصل لا بما قبلها, الفصل, التاء المربوطة والتاء المفتوحة, الألف اللينة, الحذف من الكتابة, الزيادة في الكتابة, الوصل والفصل, الفاصلة, الفاصلة المنقوطة, النقطة, الشرطة, القوسان, علامات التنصيص, النقطتان الرأسيتان, علامة الاستفهام, علامة التعجب, علامة الحذف
## Recommended Production Granularity
- Recommended production leaves after tiny-corpus review:
  - الألف اللينة, التاء المربوطة والتاء المفتوحة, الحذف من الكتابة, الزيادة في الكتابة, الهمزة في أول الكلمة, الهمزة في وسط الكلمة, الهمزة في آخر الكلمة, الفاصلة, الفاصلة المنقوطة, النقطة, الشرطة, القوسان, علامات التنصيص, النقطتان الرأسيتان, علامة الاستفهام, علامة التعجب, علامة الحذف

## Candidate Nodes That Should Definitely Split Further
- الهمزة
- علامات الترقيم

## Candidate Nodes That Should Remain Grouped
- الألف اللينة
- التاء المربوطة والتاء المفتوحة
- الحذف من الكتابة
- الزيادة في الكتابة
- الوصل والفصل

## Candidate Nodes That Should Merge
- الهمزة + الهمزة في أول الكلمة + الهمزة في وسط الكلمة + الهمزة في آخر الكلمة should become one structured branch rather than four flat sibling leaves.

## Candidate Nodes That Should Be Renamed
- هاء التأنيث وتاؤه → التاء المربوطة والتاء المفتوحة
- الفصلة → الفاصلة
- الفصلة المنقوطة → الفاصلة المنقوطة
- علامة الانفعال أو التعجب → علامة التعجب

## Candidate Topics That Should Stay Excluded
- مفردات منوعة للتدريب على الهمزة
- نماذج وتعليلاتلرسم الهمزة والألف
- قواعد الإملاء على بساط البحث
- الاستفهام التعجبي

## Keep / Split / Merge / Rename / Exclude Review Of Current Tree
| Node | book_count | Action | Rationale |
|------|-----------:|--------|-----------|
| الألف اللينة | 2 | keep | Only one retained book supports internal sub-splits; keep the grouped production leaf under the tiny corpus. |
| التاء المربوطة والتاء المفتوحة | 2 | keep | The retained corpus shows the chapter clearly, but not a stable multi-book finer split. |
| الحذف من الكتابة | 2 | keep | One retained book exposes many subcases, but they are too fine and too local for production leaves. |
| الزيادة في الكتابة | 2 | keep | The chapter is stable across two retained books, while internal letter-by-letter splits remain too local. |
| الهمزة | 2 | split | Two retained books attest the positional subtopics أول/وسط/آخر الكلمة, so the umbrella leaf should become a parent branch. |
| الهمزة في آخر الكلمة | 2 | keep | Supported by 2 retained books and structurally stable. |
| الهمزة في أول الكلمة | 2 | keep | Supported by 2 retained books and structurally stable. |
| الهمزة في وسط الكلمة | 2 | keep | Supported by 2 retained books and structurally stable. |
| علامات الترقيم | 2 | split | The punctuation-only retained book enumerates a closed class of standard sign families, justifying a cautious sign-level split. |

## Excluded-Despite-Retained Review
- These headings appear inside retained books but should not become production leaves because they are drills, support matter, or rhetorical/composite usage rather than stable orthography nodes.
- مفردات منوعة للتدريب على الهمزة
- نماذج وتعليلاتلرسم الهمزة والألف
- قواعد الإملاء على بساط البحث
- الاستفهام التعجبي

## Corpus-Thinness Risks
- Only one retained book exposes fine internal structure for الألف اللينة, الحذف, and الزيادة, so splitting those chapters would overfit one author’s presentation.
- The punctuation split is the only serious single-book exception because the sign inventory is closed-class and domain-stable.

## Overfitting Risks
- Do not create leaves for وصل من / وصل ما / وصل لا.
- Do not create leaves for letter-by-letter deletion or addition subcases under the current corpus size.
- Do not promote meta-discussion or drill headings, even when they were retained in Stage 1 as broad umbrella topics.

## Supporting Stage 1 Evidence
- Current gaps file threshold implication: 2
- Current gaps file contents:
  # Imlaa Corpus Gaps
  
  - الألف اللينة — 2 books
  - التاء المربوطة والتاء المفتوحة — 2 books
  - الحذف من الكتابة — 2 books
  - الزيادة في الكتابة — 2 books
  - الهمزة — 2 books
  - الهمزة في آخر الكلمة — 2 books
  - الهمزة في أول الكلمة — 2 books
  - الهمزة في وسط الكلمة — 2 books
  - علامات الترقيم — 2 books

## Excluded Heading Evidence Sample
- ‌الفصلة — الطريق المستقيم في نظم علامات الترقيم — Stage 1 exclusion `ambiguous`
- ‌الفصلة المنقوطة — الطريق المستقيم في نظم علامات الترقيم — Stage 1 exclusion `ambiguous`
- ‌الاستفهام التعجبي — الطريق المستقيم في نظم علامات الترقيم — Stage 1 exclusion `ambiguous`
- ‌علامة الحذف — الطريق المستقيم في نظم علامات الترقيم — Stage 1 exclusion `mixed`

