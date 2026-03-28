# Empirical Back-Reference Scan — Summary
**Date:** 2026-03-28
**Scan:** `scripts/empirical_backrefs.py` against 89 HTM fixture files (19.1M chars)
**Decision: PROCEED — build Defense 1A**

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Files scanned | 89 |
| Total text | 19.1M chars |
| Total reference hits | 3,497 |
| Overall hit rate | ~183 / M chars |
| Patterns qualifying for PROCEED | 8 / 17 |

---

## Which Patterns Had the Most Hits?

### Tier 1 — High frequency (>15/M chars)
| Pattern | Arabic | Hits | Files | Rate/M |
|---------|--------|------|-------|--------|
| See/refer to | انظر | 1,761 | 39 | 92.2 |
| What preceded | ما تقدم | 410 | 37 | 21.5 |
| Refer back to | راجع | 410 | 49 | 21.5 |
| Will come later | سيأتي | 289 | 24 | 15.1 |

### Tier 2 — Moderate frequency (4–10/M chars)
| Pattern | Arabic | Hits | Files | Rate/M |
|---------|--------|------|-------|--------|
| As previously mentioned | كما تقدم | 148 | 17 | 7.75 |
| As preceded | كما سبق | 130 | 13 | 6.81 |
| It preceded that | تقدم أن | 84 | 9 | 4.40 |
| As will come | كما سيأتي | 79 | 14 | 4.14 |

### Tier 3 — Low but present (<3/M chars)
`كما مر` (51), `تقدم ذكره` (48), `يأتي بيانه` (48) — present in 5–18 files, below qualification threshold but non-trivial.

### Pattern family totals
| Type | Total hits | % of corpus |
|------|-----------|-------------|
| Cross-reference (انظر, راجع, ارجع إلى) | 2,180 | 62% |
| Back-reference (كما تقدم etc.) | 879 | 25% |
| Forward-reference (سيأتي etc.) | 420 | 12% |
| Section-reference | 18 | <1% |

---

## Is the Hit Rate Sufficient to Justify Defense 1A?

**Yes — decisively.**

The qualification threshold is: `hit_rate_per_million_chars > 1.0` AND `files_with_hits >= 10`. Eight patterns clear this bar. The combined signal is 3,497 hits across 19.1M chars.

Three concrete arguments:

1. **Breadth:** `راجع` appears in 49/89 files (55% of corpus). `انظر` in 39/89 (44%). This is a corpus-wide phenomenon, not an outlier in a few texts.

2. **Density in real excerpting targets:** The ibn_aqil fixture — the engine's primary test source — shows 12 distinct reference patterns across its three volume files (247 combined hits). Any excerpt drawn from this corpus has a high probability of containing at least one dangling reference.

3. **Knowledge integrity exposure:** When an excerpt contains `كما تقدم` ("as previously mentioned") or `انظر فصل X` ("see chapter X") but the referenced context is absent, the reader's knowledge is **actively harmed** — they receive a claim without its support structure, or a pointer that resolves to nothing. This is CLAUDE.md Principle 3: "The library IS the user's knowledge." Dangling references are not cosmetic issues; they are latent corruption.

The **section_reference** type (18 hits, 1 file) does NOT meet threshold. It can be deferred or treated as low-priority within Defense 1A.

---

## Recommended Decision

**PROCEED** — build Defense 1A (dangling reference detector).

**Priority order within Defense 1A:**
1. Cross-references (`انظر`, `راجع`) — highest frequency, widest file coverage
2. Back-references (`ما تقدم`, `كما تقدم`, `كما سبق`) — create decontextualised excerpts
3. Forward-references (`سيأتي`, `كما سيأتي`) — create broken promises to the reader
4. Section-references — defer; corpus signal too weak to prioritise

**Minimum viable detector:** flag any excerpt whose text contains one or more of the 8 qualifying patterns without the corresponding referent in the same or adjacent excerpt. The scanner patterns above are the exact string literals to check — no LLM required for detection, only for resolution.
