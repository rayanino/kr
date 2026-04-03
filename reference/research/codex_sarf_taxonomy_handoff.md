# Codex Sarf Taxonomy Handoff

Read this before any topic-frequency or taxonomy work on `codex_sarf_books_identified.json`.

## Current corpus state

- `codex_sarf_books_identified.json` is a **candidate pool**, not a clean sarf-only corpus.
- Current counts:
  - `total_scanned`: `8417`
  - `sarf_count`: `214`
  - `tier_counts`: `A=0, B=201, C=13`
- The dominant sarf match reason is:
  - `180` books: `inconclusive preview for category 'النحو والصرف'; included as Tier B`

This means most of the current sarf list was kept conservatively to avoid false negatives. It does **not** mean those books are safe to use wholesale for sarf topic extraction.

## Hard boundary rule

The next session must enforce a **heading-level science boundary**.

- A book being in the sarf candidate list does **not** authorize counting all of its headings.
- A heading must be excluded immediately if it is about sentence-level syntax or syntactic relations.
- If a book yields mostly nahw headings, that book must contribute **zero** topics to the sarf frequency and **zero** nodes to the sarf tree.
- When a heading is ambiguous between nahw and sarf, default to **exclude**, not include.

## Hard nahw exclusions

These are nahw/syntax markers and must not appear in the final sarf topic frequency, gaps list, or taxonomy tree:

- `الإعراب`
- `العامل`
- `المبتدأ`
- `الخبر`
- `الفاعل`
- `المفعول به`
- `النعت`
- `العطف`
- `التوكيد`
- `البدل`
- `الحال`
- `التمييز`
- `الجار والمجرور`
- `النواسخ`
- `الجملة الاسمية`
- `الجملة الفعلية`
- `الموصول`
- `النداء`

## Positive sarf scope

Only word-level morphology topics should survive into the next-stage outputs. Typical keepers include:

- `الأبنية`
- `الأوزان`
- `الميزان الصرفي`
- `الاشتقاق`
- `الإعلال`
- `الإبدال`
- `الإدغام`
- `المجرد والمزيد`
- `الثلاثي والرباعي`
- `المصادر`
- `اسم الفاعل`
- `اسم المفعول`
- `الصفة المشبهة`
- `اسم التفضيل`
- `التصغير`
- `النسب`
- `جمع التكسير`
- `المقصور والممدود`
- `الهمز`

## Safe operating protocol for the next session

1. Treat Tier `C` books as the clean seed set.
2. Treat Tier `B` books as provisional containers only.
3. Extract headings from all candidate books, but count only headings that pass the hard boundary above.
4. If a Tier `B` book produces only nahw headings, keep it out of the sarf topic counts entirely.
5. The final `codex_sarf_topic_frequency.json`, `codex_sarf_corpus_gaps.md`, and `codex_sarf_corpus_tree.yaml` must contain **zero** nahw headings and **zero** sentence-level grammar nodes.

## Non-negotiable success condition

No bleeding between sciences means:

- no nahw heading contributes to sarf frequency,
- no nahw heading appears in the sarf gaps file,
- no nahw heading becomes a sarf taxonomy node.
