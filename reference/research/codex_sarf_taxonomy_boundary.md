# Sarf Taxonomy Boundary Guard

This note is a companion to `codex_sarf_books_identified.json`.
It exists to prevent science bleed during the next sarf taxonomy session.

## Corpus Reality

- `codex_sarf_books_identified.json` is intentionally broad.
- Current totals:
  - `sarf_count = 214`
  - `Tier A = 0`
  - `Tier B = 201`
  - `Tier C = 13`
- Almost the entire corpus is therefore candidate-level sarf, not a purity-certified sarf-only corpus.
- The main source of bleed risk is Shamela's shared category `النحو والصرف`.

## Hard Rule

Treat the file as a **sarf candidate set**, not as a clean sarf corpus.

For taxonomy work:

- Include only **word-level morphology** topics.
- Exclude all **sentence-level grammar** topics, even if they appear inside a retained Tier B book.
- If a heading is mixed or ambiguous between sarf and nahw, drop it unless the heading is clearly morphology-first.

## Must-Exclude Nahw Topics

These are not sarf topics and must not appear in the sarf taxonomy tree, topic frequency, or gaps file:

- `الفاعل`
- `المفعول`
- `المفعول به`
- `المبتدأ`
- `الخبر`
- `النعت`
- `العطف`
- `التوكيد`
- `البدل`
- `التمييز`
- `الحال`
- `الاستثناء`
- `النداء`
- `الجملة`
- `شبه الجملة`
- `العامل`
- `الإعراب`
- `النواسخ`
- any heading whose primary concern is case endings, syntactic position, or sentence structure

## Safe Sarf Topics

These are acceptable sarf-side morphology signals:

- `أبنية`
- `الميزان`
- `الاشتقاق`
- `الإعلال`
- `الإبدال`
- `المجرد`
- `المزيد`
- `الثلاثي`
- `الرباعي`
- `المصادر`
- `اسم الفاعل`
- `اسم المفعول`
- other headings whose primary concern is form, derivation, pattern, or word construction

## Operating Rule For The Next Session

When extracting headings and clustering topics:

1. First ask: is this heading about the **word as a form** or about the **sentence as a structure**?
2. Keep it only if the answer is form/morphology.
3. If uncertain, exclude it from the sarf taxonomy outputs.

Conservative exclusion is correct here.
Allowing nahw bleed into sarf is the bigger error.
