You are an Islamic scholarly convention reviewer evaluating whether two new excerpting rules correctly capture how classical scholars structure definitions and evidence in their works.

CONTEXT:
The KR excerpting engine (branch: excerpting-foundations-hardening-20260404) splits scholarly text into teaching units. DR40 added two new split rules based on owner rejection of overly broad excerpts. The owner rejected excerpts from كتاب الطلاق where the definition pair (لغة/شرعا) and all evidence types (Quran/Sunnah/Ijma/Qiyas) were bundled into one excerpt instead of being granulated.

TASK:
Read these files in order, then answer the 5 evaluation questions below:
1. engines/excerpting/SPEC.md — search for "§6.24" and "§6.25" (two sections, ~40 lines each)
2. integration_tests/dr40_smoke_talaq_v2/excerpts.jsonl — 20 excerpts from كتاب الطلاق processed with the new rules
3. integration_tests/campaign_20260331/taysir/owner_feedback.jsonl — 2 owner rejections that motivated these rules

EVALUATION QUESTIONS:

Q1 — Definition pair bridging: §6.24 rule 3 says bridging sentences like "والتعريف الشرعي فَرْد من معناه اللغوي العام" attach to the شرعا unit, not standalone. Is this correct per scholarly convention? In classical texts like المغني or الأم, where does the bridging sentence conventionally belong — with the lughawi definition, the shar'i definition, or does it vary by author?

Q2 — Per-ayah evidence splitting: §6.25 rule 3 says "when multiple distinct verses are cited with separate istidlal reasoning, split per-ayah." Are there cases in fiqh texts where splitting per-ayah would break the author's istidlal coherence? For example, when a scholar uses two verses together as a composite proof (تعاضد الأدلة) rather than independent proofs.

Q3 — Missing exemptions: §6.25 lists three exemption conditions (syntactically embedded, brief parenthetical ≤15 words, dialogue/refutation integrity). Are there missing cases? Consider: when a scholar explicitly says "والدليل من الكتاب والسنة" then weaves Quran and hadith together in a single argument, should this be split?

Q4 — Other paired structures: DP-SPLIT-1 covers لغة/شرعا pairs. Are there other common paired definitional structures in Islamic scholarship that should trigger the same split rule? Consider: اصطلاحا/لغة, حقيقة/مجازا, عرفا/شرعا, and any madhab-specific patterns.

Q5 — Smoke test quality: Look at the 20 excerpts in excerpts.jsonl. For the first 5 excerpts specifically, assess: are the boundaries at natural scholarly break points? Is any excerpt missing critical context that a student would need?

OUTPUT FORMAT:
For each question, provide:
- FINDING: one-line answer
- EVIDENCE: specific Arabic text example from a classical work (not from the test data)
- RECOMMENDATION: CONFIRM (rule is correct) / AMEND (rule needs adjustment, specify what) / FLAG (needs further investigation)

Do NOT review: code quality, Python style, test coverage, or anything outside Islamic scholarly convention accuracy.
