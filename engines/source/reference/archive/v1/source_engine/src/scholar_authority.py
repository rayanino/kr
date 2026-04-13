"""Scholar Authority Model — SPEC §4.A.5

Central registry of all scholars (library/registries/scholars.json).
Handles: record creation, matching, progressive enrichment.

Matching: normalized name + death date + school affiliation + known works.
Match >= 0.85 → auto-link. 0.50-0.85 → human gate. < 0.50 → new record.

Consistency checks on update:
1. Death date drift > 5yr → SRC_SCHOLAR_DATE_CONFLICT
2. School affiliation change → SRC_SCHOLAR_SCHOOL_CONFLICT
3. canonical_name_ar change → blocked
4. Teacher/student self-reference → rejected
5. Temporal inconsistency (teacher died after student + 30yr) → flagged
"""
