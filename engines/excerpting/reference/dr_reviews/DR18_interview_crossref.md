# DR18 × Owner Interview Cross-Reference

**Date:** 2026-04-07
**Sources:** DR18 (Claude DR decision map) + CC owner interview (2026-04-06)

This document maps the owner's interview answers to DR18 decision points, identifying which decisions are ALREADY PARTIALLY RESOLVED by the interview data.

## Resolved or Partially Resolved

| Decision ID | DR18 Description | Interview Answer | Resolution Status |
|---|---|---|---|
| SRC-D-004 | Science scope and priority ranking | Arabic sciences first (imla→sarf→nahw→balagha) for practical reasons; fiqh (#1), usul (#2), aqidah (#3) for passion | **PARTIALLY RESOLVED** — ranking provided but needs formal confirmation session with full 18-science list |
| SRC-D-005 | Study focus (science, school, level) | Beginner level, Arabic priority, no school preference stated | **PARTIALLY RESOLVED** — level and science confirmed, school preference and monthly refresh cadence TBD |
| SRC-D-010 | Book processing priority | Priority book: الفقه على المذاهب الأربعة (confirmed in shamela-export-samples) | **PARTIALLY RESOLVED** — one priority book identified, full 2,519-book triage session still needed |
| TAX-D-003 | Tree formation order | Implied by science ranking: nahw done → sarf → balagha → imlaa → aqidah | **INFERRED** — not explicitly stated for tree order. DR18 WRONG to assume sarf; owner's actual priority may differ for trees vs study. Needs explicit confirmation. |
| EXC-D-001 | Teaching unit granularity | Owner's #1 issue: engine UNDER-DIVIDES. Gets macro-boundaries right but misses sub-excerpts. | **CONFIRMED AS CRITICAL** — validates this is the highest-priority calibration task. 100+ labeled excerpts needed. |
| EXC-D-002 | Self-containment calibration | Context loss is #2 issue (lesser than granularity). | **CONFIRMED** — owner explicitly ranked context loss below granularity. Calibration can happen after granularity fix. |
| SYN-D-005 | Entry style preference | "Present every single thing to me and tell me 'just memorize it like this'" | **STRONG SIGNAL** — owner wants study-ready, elimination of preparation work. Not yet formal confirmation of ENTRY_EXAMPLE.md style. |
| UM-D-001 | Expertise level per science | Implied beginner across all. No explicit per-science declaration yet. | **PARTIALLY RESOLVED** — general level clear, formal per-science declaration needed in Session A |
| UM-D-002 | Study preferences | Heavy annotator; prefers highlighting/interactive; 10-15 excerpts/session; laptop; show reasoning always | **PARTIALLY RESOLVED** — preference signals captured, need formal user_model configuration |

## Not Yet Addressed by Interview

| Decision ID | Description | Next Step |
|---|---|---|
| SRC-D-001 | Muhaqiq trust list | Session B — present list for binary review |
| SRC-D-002 | Publisher reputation | Session B — classify ~30 publishers |
| SRC-D-003 | Commercial editor watchlist | Session B — free-form recall |
| SRC-D-006 | Edition preference for multi-source works | SUMMER — operational |
| SRC-D-008 | Library breadth policy | Session D — single threshold |
| EXC-D-004 | Hadith title retention | Session E — binary choice |
| EXC-D-009 | Error class halt thresholds | Session D — risk tolerance |
| EXC-D-010 | Flag budget percentage | Session D — single number |
| TAX-D-001 | Tree reviews (remaining 4) | As trees mature — ~30 min each |
| TAX-D-007 | Additional sciences beyond initial 5 | Session A — alongside science ranking |
| SYN-D-001 | SCIENCE.md configuration | SUMMER — after synthesis engine |
| SYN-D-002 | School lists per science | Session E — per-science confirmation |
| SYN-D-003 | Analytical layer depth | SUMMER — after seeing entries |
| SYN-D-006 | Cross-science reference policy | SUMMER — after seeing examples |

## Key Insight

The interview already provides **strong signals** for the top 3 critical-path items:
1. Science scope (SRC-D-004): Arabic → fiqh → usul → aqidah. Needs 18-science formal ranking.
2. Book priority (SRC-D-010): الفقه على المذاهب الأربعة first. Needs 2,519-book triage.
3. Granularity (EXC-D-001): #1 issue. Engine under-divides. Needs 100+ labeled excerpts.

These signals mean Session A can be SHORTER than estimated (some answers pre-populated) and the 30-book probe (summer) should prioritize sub-excerpting evaluation.
