"""Work Registry and Relationship Graph — SPEC §4.A.1, §4.A.9

Work identity: wrk_{author_slug}_{title_slug}
Work matching: normalized title + author canonical_id.
Confidence >= 0.85 → auto-link. 0.50-0.85 → human gate. < 0.50 → new work.

Relationship types: sharh_of, hashiyah_on, mukhtasar_of, nazm_of,
taqrirat_on, responds_to, cites.
Placeholder works: status="referenced_not_acquired" for works not yet in library.
"""
