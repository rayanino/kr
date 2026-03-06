# Preparatory Phase Roadmap — خارطة مرحلة الإعداد

The preparatory phase is NOT just SPEC refinement. It is everything needed before Claude Code can build autonomously with minimal intervention.

---

## Work Streams

### Stream 1: SPEC Refinement (current SPECs → implementation-ready SPECs)
Follow `SPEC_REFINEMENT.md`. Pipeline order: source → normalization → shared components → passaging → atomization → excerpting → taxonomy → synthesis → scholar interface.

Each SPEC refined with: creative exploration, threat analysis, concrete examples, technology verification, boundary checks, silent failure detection.

**Tracking:** `python3 scripts/refinement_status.py`

### Stream 2: Machine-Readable Contracts (prose SPECs → parseable schemas)

Each engine SPEC has prose §2 (Input Contract) and §3 (Output Contract). Claude Code implements better when these are ALSO expressed as machine-readable schemas.

For each engine, create a companion file `engines/{engine}/contracts.py` containing:
```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class SourceMetadata(BaseModel):
    """Output contract for source engine (SPEC §3)."""
    source_id: str = Field(description="Permanent ID: src_{8_char_hash}")
    work_id: str = Field(description="Work grouping: wrk_{author}_{title}")
    # ... all fields from SPEC §3 with types and validation
```

These Pydantic models serve THREE purposes:
1. Claude Code uses them as the ground truth for data model implementation
2. Runtime validation uses them to catch schema violations
3. Tests use them to generate valid/invalid test data

**Priority:** Create contracts.py for source and normalization engines first (Milestone 1 dependencies).

### Stream 3: Resource Survey (what tools exist → what tools we USE)

`reference/RESOURCES.md` was last updated during SPEC writing. Technology moves fast. Each SPEC refinement session includes tool searches, but a dedicated resource survey session would:

1. **Arabic NLP landscape 2026:** What's new in CAMeL Tools, Farasa, JAIS, ALLaM? Any new Arabic-specific tools?
2. **OCR landscape:** Mistral OCR 3 capabilities, Google Gemini for document understanding, any new Arabic OCR models?
3. **Embedding models:** Best Arabic embedding model as of early 2026? Benchmarks?
4. **Islamic studies tools:** OpenITI updates, Usul.ai, al-Maktaba al-Shamela digital tools, any new projects?
5. **LLM capabilities:** What can Claude Opus 4.6 / Sonnet 4.6 / GPT-5 do for Arabic text analysis that older models couldn't?
6. **Digital humanities:** Cross-tradition tools (Latin, Chinese, Hebrew) — what features could be adapted?

**Deliverable:** Updated RESOURCES.md with tool evaluations, version numbers, Arabic support status, and KR integration recommendations.

### Stream 4: Claude Code Environment Optimization

The `.claude/` directory needs optimization based on current best practices:

1. **Plan mode configuration:** Add to engine CLAUDE.md files: "Start with plan mode for any task touching >3 files."
2. **Agent memory:** Research shows subagents can maintain persistent memory across sessions. Configure `memory: project` for key agents (code-reviewer, integrity-checker).
3. **Compact instructions:** Add to engine CLAUDE.md files: "When compacting, preserve: current task from NEXT.md, SPEC section being implemented, test results."
4. **Output style:** Configure explanatory output style for SPEC-related work, concise for implementation.

### Stream 5: VISION.md Structure Optimization

VISION.md is 5000+ lines and ~47K tokens. Currently it can only be read via `extract_vision_sections.py`. Problems:
- Sections are not independently comprehensible (they reference each other)
- No index or lookup mechanism beyond section numbers
- Some sections are stale (written before SPECs existed)

Options:
1. **Split into per-topic files** under `reference/vision/` — one file per major section. Pro: each independently readable. Con: cross-references break.
2. **Create a condensed digest** (~5K tokens) with essential definitions and pointers. Pro: fits in context. Con: may drift from full VISION.
3. **Leave as-is but create better extraction** — expand extract_vision_sections.py to support keyword search, not just section numbers.

**Recommendation:** Option 3 (least disruption) + create `STEERING.md` as the condensed digest (DONE).

### Stream 6: Test Data Preparation

No engine can be properly tested without realistic test data:

1. **Shamela test corpus:** 3-5 Shamela directories of varying complexity (single-layer, multi-layer, multi-volume, with footnotes, without). These should be committed to the repo (or Git LFS if too large).
2. **OCR test corpus:** 2-3 scanned Arabic pages with known-good transcriptions for OCR accuracy testing.
3. **Gold baselines:** Hand-verified outputs for each engine. Starting with source engine metadata extraction.
4. **Arabic text test cases:** From `.claude/skills/arabic-text/SKILL.md` — diacritized text, mixed Arabic/Latin, Quran verses, isnad chains, poetry.

**Action required from owner:** Provide or point to sample Shamela directories. The system cannot test the Shamela intake path without real Shamela data.

### Stream 7: Architectural Validation

Before implementation, validate that the 7-engine pipeline is still the right architecture:

1. **Missing capabilities audit:** Read all USER_SCENARIOS.md scenarios. For each: can the current pipeline produce the required output? What's missing?
2. **Feedback loop analysis:** Does any engine need output from a downstream engine? (Currently the pipeline is strictly linear.)
3. **Shared component adequacy:** Are 6 shared components enough? Does any engine need a shared service that doesn't exist?
4. **Scale analysis:** At 100 sources? 1000? Where are the bottlenecks?

This is a DESIGN_REVIEW session type.

---

## Session Sequencing

Not all streams run sequentially. Here's a suggested interleaving:

```
Session  1: Stream 2 — Create contracts.py for source engine (machine-readable contracts)
Session  2: Stream 1 — Source SPEC refinement cycle 1 (uses contracts.py as reference)
Session  3: Stream 3 — Resource survey (dedicated research session)
Session  4: Stream 1 — Source SPEC refinement cycle 2 (if needed) OR normalization SPEC cycle 1
Session  5: Stream 2 — Create contracts.py for normalization engine
Session  6: Stream 1 — Normalization SPEC refinement
Session  7: Stream 7 — Architectural validation (design review)
Session  8: Stream 1 — Shared components SPEC refinement (consensus, validation, human_gate)
...continue alternating refinement with other streams...
Session N-2: Stream 4 — Claude Code environment final optimization
Session N-1: Stream 6 — Test data preparation (may need owner input)
Session N:   Stream 5 — VISION.md optimization (only after all SPECs refined)
```

The key insight: streams interleave. A pure SPEC refinement marathon would miss the broader preparatory work.

---

## Completion Criteria

The preparatory phase is complete when:
1. All 14 SPECs pass refinement (≤2 minor defects per cycle)
2. Source and normalization engines have machine-readable contracts (contracts.py)
3. RESOURCES.md is current (surveyed within last 30 days)
4. Test data exists for Milestone 1 engines
5. Architectural validation found no blocking issues
6. STEERING.md accurately reflects the architecture
7. NEXT.md directs to Milestone 1 implementation
