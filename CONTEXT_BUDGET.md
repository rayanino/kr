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

### Active Governance Documents
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| KNOWLEDGE_INTEGRITY.md | 168 | ~1,600 |
| STEERING.md | ~100 | ~950 |
| OPEN_PROBLEMS.md | ~230 | ~2,200 |
| SILENT_FAILURES.md | ~170 | ~1,600 |
| ENGINE_PROTOCOL.md (skills/shared/) | ~300 | ~2,900 |

### Skills (Claude.ai — kr-* uploadable zips)
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| kr-core-extract/SKILL.md | ~120 | ~1,100 |
| kr-spec-review/SKILL.md | ~130 | ~1,200 |
| kr-integrity/SKILL.md | ~140 | ~1,300 |
| kr-research/SKILL.md | ~100 | ~950 |
| kr-build-prep/SKILL.md | ~120 | ~1,100 |
| kr-evaluate/SKILL.md | ~100 | ~950 |

### Skills (Claude Code — .claude/skills/)
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| arabic-text/SKILL.md | ~98 | ~900 |
| technology-survey/SKILL.md | ~94 | ~900 |
| knowledge-safety/SKILL.md | ~74 | ~700 |
| scholarly-design/SKILL.md | ~90 | ~850 |

### Engine SPECs
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| Source SPEC | 1,465 | ~14,000 |
| Normalization SPEC | 2,006 | ~19,000 |
| Passaging SPEC | 1,037 | ~9,900 |
| Atomization SPEC | 1,205 | ~11,400 |
| Excerpting SPEC | 1,038 | ~9,900 |
| Taxonomy SPEC | 945 | ~9,000 |
| Synthesis SPEC | 918 | ~8,700 |

### Engine Contracts
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| Source contracts.py | 825 | ~7,800 |
| Normalization contracts.py | 697 | ~6,600 |
| Passaging contracts.py | 556 | ~5,300 |
| Atomization contracts.py | 676 | ~6,400 |
| Excerpting contracts.py | 557 | ~5,300 |
| Taxonomy contracts.py | 491 | ~4,700 |
| Synthesis contracts.py | 565 | ~5,400 |

### Reference Documents
| File | Lines | Tokens (approx) |
|------|-------|-----------------|
| DOMAIN.md | ~750 | ~7,100 |
| ENTRY_EXAMPLE.md | ~170 | ~1,600 |
| USER_SCENARIOS.md | ~280 | ~2,700 |
| RESOURCES.md | ~320 | ~3,000 |
| TESTING_FRAMEWORK.md | ~700 | ~6,700 |
| kr_decisions.md | ~1,000 | ~9,500 |
| VISION.md | ~5,000 | ~47,000 (NEVER read whole) |

---

## Session Budgets by Step (ENGINE_PROTOCOL.md)

### Tracer Bullet (Step 0) — ~155K available

Must read:
- ENGINE_PROTOCOL.md: ~2,900
- All 7 contracts.py files: ~41,500
- STEERING.md: ~950
**Subtotal reading: ~45,350**

Budget for reconciliation + stub code: ~80,000
Budget for test execution output: ~10,000
**Total work: ~90,000**

**Remaining buffer: ~20,000** — tight. Read contracts in batches if needed.

### SPEC Core Architecture (Step 1) — ~155K available

Must read:
- ENGINE_PROTOCOL.md: ~2,900
- KNOWLEDGE_INTEGRITY.md: 1,600
- The SPEC being reviewed: ~9,000–19,000
- ENTRY_EXAMPLE.md: 1,600
- Owner comments file: ~1,000
**Subtotal reading: ~16,100–26,100**

Budget for output (SPEC rewrites, research): ~60,000
Budget for web searches (5-10 × ~2K each): ~20,000
**Total work: ~80,000**

**Remaining buffer: ~49,000–59,000** — comfortable.

### Build (Step 3) — ~155K available

Must read:
- ENGINE_PROTOCOL.md (Step 3 section): ~1,000
- The SPEC section being implemented: ~3,000 (partial)
- arabic-text skill: 900
- knowledge-safety skill: 700
- Existing code in the engine: variable (target <5,000)
**Subtotal reading: ~5,600**

Budget for code writing + tests: ~80,000
Budget for test execution output: ~10,000
**Total work: ~90,000**

**Remaining buffer: ~52,000** — very comfortable.

---

## Rules

1. **Never read VISION.md whole.** At ~47K tokens, it consumes nearly a third of available context. Use `python3 scripts/extract_vision_sections.py` for specific sections.

2. **Never read kr_decisions.md whole** unless specifically needed. At ~9.5K tokens, it's expensive. Decisions are already incorporated into SPECs.

3. **Read files in priority order.** If context starts getting tight, you can skip lower-priority files. NEXT.md specifies the order.

4. **One SPEC per session.** Don't try to refine two SPECs in one session. The SPEC + protocol + research easily fills a session.

5. **Track your budget.** After reading the required files, mentally note: "I've used about [X]K tokens for reading. I have about [Y]K tokens left for work."

6. **Stop clean.** If you're past 70% context usage and still have work to do: finish the current section, write NEXT.md with extra detail, commit, and stop. A clean handoff at 70% is better than a rushed completion at 95%.
