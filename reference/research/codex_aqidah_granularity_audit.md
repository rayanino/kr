# Aqidah Granularity Audit

## Stage 2 Blocker

- Stage 1 `parent_heading` and `parent_core` fields are not safe as hierarchy ground truth for unclassified-heavy books; Stage 2 rebuilt structure directly from the source `.htm` files.

## Proposed Leaf Criterion

- Doctrine-first and science-pure.
- Understandable as a short neutral label without proof-chain or author context.
- Not merely a proof bucket, objection bucket, or pedagogical scaffold.
- Appears in at least 2 analyzed books, or in 1 pedagogical manual plus retained-book corpus frequency `>= 2`.
- If uncertain, exclude.

## Proposed Anti-Overgranulation Rule

- Exclude proof fragments such as `أدلته`, `أمثلته`, `الجواب`, `الشبهة`, and `الرد على شبهة`.
- Exclude pedagogical wrappers such as `أنواع`, `أركان`, `قواعد`, `مقدمة`, `تمهيد`, and `خاتمة` unless the wrapped concept is the real node.
- Exclude author-, event-, text-, and case-specific microheadings such as `موقف فلان`, `قوم نوح`, and `سورة كذا`.
- Exclude long sentence labels that cannot be renamed without guesswork.

## Current Tree Verdict

- The current flat tree is **too coarse**.

## Current Node Actions

| Current node | Action | Proposed target or children | Evidence books | Maximum possible granularity | Recommended production granularity | Contamination risk | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|
| توحيد الألوهية | split | العبادة, الشرك | [شرح] تسهيل العقيدة الإسلامية - ط ٢ - الكتاب, أصول الإيمان في ضوء الكتاب والسنة, الشرك في القديم والحديث, المختصر المفيد في عقائد أئمة التوحيد, شرح كشف الشبهات لخالد المصلح | العبادة, الشرك, الطاغوت | العبادة, الشرك | medium | high | Validated child evidence exists for العبادة and الشرك; الطاغوت remains below split threshold. |
| توحيد الربوبية | keep | توحيد الربوبية | — | توحيد الربوبية | توحيد الربوبية | low | medium | Current evidence supports overview treatment; no second stable child clears the split threshold. |
| الإيمان باليوم الآخر | split | عذاب القبر ونعيمه, الحوض, الميزان, الصراط, الجنة, النار | أصول الإيمان في ضوء الكتاب والسنة, التعليقات على متن لمعة الاعتقاد لابن جبرين, الجنة والنار | عذاب القبر ونعيمه, الحوض, الميزان, الصراط, الجنة, النار | عذاب القبر ونعيمه, الحوض, الميزان, الصراط, الجنة, النار | medium | high | The afterlife material is clearly broader than the current flat node. |
| الشفاعة | keep | الشفاعة | — | الشفاعة | الشفاعة | low | medium | Stable leaf; may nest under a future afterlife branch without losing identity. |
| توحيد الأسماء والصفات | keep | توحيد الأسماء والصفات | — | كلام الله, الرؤية, العلو, الاستواء | توحيد الأسماء والصفات | low | low | Sub-candidates exist, but Stage 2 evidence does not yet justify a production split. |
| الإيمان بالملائكة | keep | الإيمان بالملائكة | — | الإيمان بالملائكة | الإيمان بالملائكة | low | medium | Only overview-level treatment is stable in the analyzed books. |
| الإيمان بالرسل | keep | الإيمان بالرسل | — | الإيمان بالرسل | الإيمان بالرسل | low | medium | Only overview-level treatment is stable in the analyzed books. |
| الإيمان بالقدر | keep | الإيمان بالقدر | أصول الإيمان في ضوء الكتاب والسنة | مراتب القدر, أفعال العباد | الإيمان بالقدر | low | low | مراتب القدر is validated, but a second stable child does not clear the split threshold. |
| الشرك الأصغر | keep | الشرك الأصغر | — | الشرك الأصغر | الشرك الأصغر | low | medium | Valid leaf; may become a child under a future grouped node `الشرك`. |
| أنواع التوحيد | merge | توحيد الربوبية / توحيد الألوهية / توحيد الأسماء والصفات | — | توحيد الربوبية / توحيد الألوهية / توحيد الأسماء والصفات | توحيد الربوبية / توحيد الألوهية / توحيد الأسماء والصفات | low | high | Overview/grouping label, not a production leaf. |
| أنواع الكفر | merge | الكفر | — | الكفر | الكفر | low | high | Overview/grouping label; merge into a future grouped node `الكفر` rather than keep as a leaf. |
| الإيمان | split | تعريف الإيمان, الإيمان قول وعمل, زيادة الإيمان ونقصانه, الاستثناء في الإيمان, نواقض الإيمان | المختصر المفيد في عقائد أئمة التوحيد | تعريف الإيمان, الإيمان قول وعمل, زيادة الإيمان ونقصانه, الاستثناء في الإيمان, نواقض الإيمان | تعريف الإيمان, الإيمان قول وعمل, زيادة الإيمان ونقصانه, الاستثناء في الإيمان, نواقض الإيمان | medium | medium | The node mixes definition, composition, increase/decrease, exception, and nullifier material. Control-book evidence is partial, but corpus-backed dedicated retained books make the split stable enough for audit recommendation. |
| الاستثناء في الإيمان | keep | الاستثناء في الإيمان | — | الاستثناء في الإيمان | الاستثناء في الإيمان | low | medium | Stable leaf; may nest under a future `الإيمان` branch. |
| الشرك الأكبر | keep | الشرك الأكبر | — | الشرك الأكبر | الشرك الأكبر | low | medium | Stable leaf; may nest under a future grouped node `الشرك`. |
| زيادة الإيمان ونقصانه | keep | زيادة الإيمان ونقصانه | — | زيادة الإيمان ونقصانه | زيادة الإيمان ونقصانه | low | medium | Stable leaf; may nest under a future `الإيمان` branch. |

## Candidate Merges And Renames

| Source | Action | Target | Notes |
|---|---|---|---|
| الإيمان بالله + الإيمان بالله تعالى | merge | الإيمان بالله | Canonical shorter label; the `تعالى` variant is formulation-only. |
| الإيمان بأسماء الله وصفاته | rename | توحيد الأسماء والصفات | Prefer the more stable corpus canonical label already used by the current tree. |
| الجنة والنار | merge | Overview under الإيمان باليوم الآخر | Useful as a grouped overview label, not as the final production leaf set. |

## Recurring Candidates That Must Stay Excluded

| Candidate | Reason | Evidence books | Matched topics |
|---|---|---|---|
| أنواع العبادة | أنواع | أصول الإيمان في ضوء الكتاب والسنة, المختصر المفيد في عقائد أئمة التوحيد | أنواع العبادة, أركان العبادة, أركان العبادة وأصولها, ذكر بعض أنواع العبادة |
| القول الأول / الثاني / الثالث | القول الأول | الشرك في القديم والحديث | القول الأول: أنه يقول بالقدر., القول الأول: إن أول شرك في بني آدم كان من قابيل, القول الثالث: (قول الأشاعرة ومَن وافقهم كابن حزمٍ, القول الثالث: (قول الجبريَّة). |
| أدلته وبيان أهميته | أدلته | أصول الإيمان في ضوء الكتاب والسنة | أدلتهم من الكتاب والسنة على زيادة الإيمان ونقصانه ونقل بعض أقوالهم في ذلك, الحوض صفته وأدلته, الشفاعة تعريفها وأنواعها وأدلتها, الصراط صفته وأدلته |
| التعريف بهم | تعريف | — | التعريف بأهل السنة والجماعة |
| موقفه من الجهمية | موقفه من | موسوعة مواقف السلف في العقيدة والمنهج والتربية | موقفه من الجهمية, موقفه من الجهمية والرافضة والمرجئة والقدرية, موقفه من الجهمية والقدرية, موقفه من الجهمية والمرجئة |
| موقفه من المبتدعة | موقفه من | موسوعة مواقف السلف في العقيدة والمنهج والتربية | موقفه من المبتدعة والجهمية, موقفه من المبتدعة والجهمية والرافضة والخوارج والمرجئة, موقفه من المبتدعة والرافضة, موقفه من المبتدعة والرافضة والجهمية والخوارج والمرجئة |
| قوم نوح وما شابهه | قوم  | الشرك في القديم والحديث | القول الرابع: إن أول شرك وقع في بني آدم هو في قوم نوح, في بيان الشرك في قوم صالح عليه السلام, في بيان الشرك في قوم نوح, في بيان الشرك في قوم هود |

## Cross-Science Contamination Notes

- Fiqh-boundary topics such as `ترك الصلاة كفر` may remain doctrinally relevant, but they must not drive production splitting unless the doctrinal core is independent and stable.
- Historical case-study headings in `الشرك في القديم والحديث` are inventory evidence, not production leaves.
- Encyclopedia bucket labels such as `موقفه من الجهمية` and `موقفه من المبتدعة` are categorization shells, not production nodes.
- Empty Stage 1 gaps output must not be read as evidence that the current tree is complete; the flat `>=5` threshold already exhausts its own candidate set.

## Whole-Book Gate Review

- The Stage 1 strict whole-book gate remains authoritative for final node and count decisions.
- Exact-tie excluded books remain out of the mandatory analysis sample.
- Shadow-lane corroboration is limited to exact-tie excluded books and may never originate a node, merge, or rename.
- Current shadow-lane corroboration titles: [شرح] تسهيل العقيدة الإسلامية - ط ٢ - الكتاب, التعليقات على متن لمعة الاعتقاد لابن جبرين, شرح كشف الشبهات لخالد المصلح.
