Loaded cached credentials.
Based on a review of the provided excerpting rules (§6.24 and §6.25), the owner's feedback, and the smoke test results, here is the evaluation regarding Islamic scholarly convention accuracy:

**Q1 — Definition pair bridging**
- **FINDING:** The rule is correct; bridging sentences conventionally belong with the shar'i definition because they establish how the technical terminology was derived from or restricts the general linguistic root.
- **EVIDENCE:** في تعريف الصوم، يذكر العلماء: "الصوم لغة الإمساك، وشرعاً إمساك مخصوص... والمناسبة بينهما أن المعنى الشرعي أخص من المعنى اللغوي"؛ فبيان العلاقة متمم للفهم الشرعي.
- **RECOMMENDATION:** CONFIRM

**Q2 — Per-ayah evidence splitting**
- **FINDING:** Splitting per-ayah breaks *istidlal* coherence when the author employs composite reasoning (دلالة الاقتران) where a single ruling is derived from the mathematical or logical intersection of multiple verses.
- **EVIDENCE:** استنباط علي بن أبي طالب لأقل مدة الحمل (ستة أشهر) بالجمع بين قوله تعالى: {وحمله وفصاله ثلاثون شهرا} وقوله تعالى: {وفصاله في عامين}، ففصل الآيتين يهدم الاستدلال تماماً.
- **RECOMMENDATION:** AMEND (Exempt composite proofs / دلالة الاقتران where the reasoning strictly depends on the combination of multiple verses).

**Q3 — Missing exemptions**
- **FINDING:** An exemption is missing for cross-type composite arguments, particularly when a Hadith is cited immediately to explain (مبين), restrict (مقيد), or specify (مخصص) a general Quranic verse.
- **EVIDENCE:** الاستدلال بآية المواريث {مِن بَعْدِ وَصِيَّةٍ يُوصِي بِهَا أَوْ دَيْنٍ} مقترنة بحديث {لا وصية لوارث} لبيان تخصيص عموم الآية، وفصلهما يخل بمراد الماتن من إيراد الدليلين معاً.
- **RECOMMENDATION:** AMEND (Add an exemption for interdependent cross-type evidence, such as Sunnah specifying or restricting Quranic generality).

**Q4 — Other paired structures**
- **FINDING:** Islamic texts frequently utilize other paired definitional structures that follow the exact same logical flow and require identical splitting conventions.
- **EVIDENCE:** تقسيم دلالة الألفاظ إلى (حقيقة / مجاز) في كتب الأصول، أو (لغة / اصطلاحاً) في مصطلح الحديث، أو (حقيقة شرعية / حقيقة عرفية) كاستعمال لفظ "الدابة".
- **RECOMMENDATION:** AMEND (Expand the rule to include لغة/اصطلاحا, حقيقة/مجازا, and شرعا/عرفا pairs).

**Q5 — Smoke test quality**
- **FINDING:** The engine failed to apply DP-SPLIT-1 to Excerpt 0, incorrectly lumping the definitions together; additionally, while Excerpts 2 and 3 properly test EV-SPLIT-1 boundaries, they strip away the ruling subject (مشروعية الطلاق), leaving a student missing critical context if read as raw text.
- **EVIDENCE:** Excerpt 0's `primary_text` contains both definitions with a clear "وفي الشرع:" boundary but was bypassed due to a false positive `["content_intertwined"]` flag. Excerpts 2 and 3 start abruptly with "فأما الكتاب فنحو..." and "وأما السنة، فقوله...", relying entirely on metadata for context.
- **RECOMMENDATION:** FLAG (Investigate the overly aggressive "content_intertwined" detection bypassing DP-SPLIT-1, and consider whether EV-SPLIT units require context-fill text injection to be truly standalone).
