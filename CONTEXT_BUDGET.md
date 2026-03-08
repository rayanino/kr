# Context Budget — ميزانية السياق

Claude Chat (the architect) has ~200K tokens total. This document provides concrete token costs so sessions can plan their reads strategically.

---

## Fixed Costs (every session)

| Item | Tokens (approx) | Notes |
|------|-----------------|-------|
| System prompt (project custom instructions) | ~5,000 | Loaded as project custom instructions |
| Knowledge file (DEEP_REASONING_PROTOCOL.md) | ~8,000 | Loaded automatically as project knowledge |
| Knowledge file (Github_key) | ~50 | GitHub access token |
| Startup (clone, NEXT.md, git log) | ~2,000 | Commands + output |
| Claude's reasoning overhead | ~30,000 | Internal chain-of-thought per session |

**Total fixed cost: ~45,000 tokens**
**Remaining for work: ~155,000 tokens**

---

## Variable Costs (per file read)

Measured by line count × ~1.3 tokens/line average for technical English/Arabic.

### Governance Documents
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| KNOWLEDGE_INTEGRITY.md | 168 | ~1,600 |
| CHALLENGE_PROTOCOL.md | 142 | ~1,300 |
| ORCHESTRATOR.md | 251 | ~2,400 |
| MILESTONES.md | 262 | ~2,500 |
| REVIEW_PROTOCOL.md | 220 | ~2,100 |
| OPEN_PROBLEMS.md | 232 | ~2,200 |

### Skills
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| knowledge-safety/SKILL.md | 74 | ~700 |
| arabic-text/SKILL.md | 98 | ~900 |
| technology-survey/SKILL.md | 94 | ~900 |
| scholarly-design/SKILL.md | 90 | ~850 |
| spec-examples/SKILL.md | 102 | ~950 |

### Engine SPECs
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| Source SPEC | 582 | ~5,500 |
| Normalization SPEC | 664 | ~6,300 |
| Passaging SPEC | 502 | ~4,800 |
| Atomization SPEC | 580 | ~5,500 |
| Excerpting SPEC | 559 | ~5,300 |
| Taxonomy SPEC | 562 | ~5,300 |
| Synthesis SPEC | 582 | ~5,500 |
| Scholar Interface SPEC | 872 | ~8,300 |

### Reference Documents
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| DOMAIN.md | ~750 | ~7,100 |
| ENTRY_EXAMPLE.md | ~170 | ~1,600 |
| USER_SCENARIOS.md | ~280 | ~2,700 |
| RESOURCES.md | ~320 | ~3,000 |
| kr_decisions.md | ~1,000 | ~9,500 |
| VISION.md | ~5,000 | ~47,000 (NEVER read whole) |

---

## Session Budgets by Type

### Engine Review Session — Phase 2/3 (~155K available)

Must read:
- ENGINE_PROTOCOL.md: ~2,500
- KNOWLEDGE_INTEGRITY.md: 1,600
- The SPEC being reviewed: ~5,500
- ENTRY_EXAMPLE.md: 1,600
- Owner comments file: ~1,000
**Subtotal reading: ~12,200**

Budget for output (SPEC edits, defect ledger, research): ~60,000
Budget for web searches (5-10 searches × ~2K per search result): ~20,000
**Total work: ~80,000**

**Remaining buffer: ~55,000** — comfortable margin.

**Optimization:** Do NOT read kr_decisions.md (9,500 tokens) — the SPEC already incorporates decisions. Do NOT read DOMAIN.md — the SPEC already incorporates domain knowledge.

### Implementation Session (~155K available)

Must read:
- ORCHESTRATOR.md: 2,200
- The SPEC section being implemented: ~2,000 (partial SPEC read)
- arabic-text skill: 900
- knowledge-safety skill: 700
- Existing code in the engine: variable (target <3,000)
**Subtotal reading: ~5,800**

Budget for code writing + tests: ~80,000
Budget for test execution output: ~10,000
**Total work: ~90,000**

**Remaining buffer: ~52,000** — very comfortable.

### Design Review Session (~155K available)

Must read:
- REVIEW_PROTOCOL.md: 2,100
- CHALLENGE_PROTOCOL.md: 1,300
- The component being reviewed: ~5,500
- ENTRY_EXAMPLE.md: 1,600
- scholarly-design skill: 850
**Subtotal reading: ~11,350**

Budget for review output + improvements: ~60,000
Budget for web searches: ~20,000
**Total work: ~80,000**

**Remaining buffer: ~56,000** — comfortable.

---

## Rules

1. **Never read VISION.md whole.** At ~47K tokens, it consumes nearly a third of available context. Use `python3 scripts/extract_vision_sections.py` for specific sections.

2. **Never read kr_decisions.md whole** unless specifically needed. At ~9.5K tokens, it's expensive. Decisions are already incorporated into SPECs.

3. **Read files in priority order.** If context starts getting tight, you can skip lower-priority files. NEXT.md specifies the order.

4. **One SPEC per session.** Don't try to refine two SPECs in one session. The SPEC + protocol + research easily fills a session.

5. **Track your budget.** After reading the required files, mentally note: "I've used about [X]K tokens for reading. I have about [Y]K tokens left for work."

6. **Stop clean.** If you're past 70% context usage and still have work to do: finish the current section, write NEXT.md with extra detail, commit, and stop. A clean handoff at 70% is better than a rushed completion at 95%.
