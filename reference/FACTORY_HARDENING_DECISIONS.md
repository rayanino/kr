# Factory Hardening Decisions — Session Output

**Date:** 2026-03-28
**Session:** Factory Hardening (follows Roadmap Revision session)
**Method:** Claude Chat architect analysis + cross-provider consultation (ChatGPT deep research, Claude Code empirical verification, Gemini adversarial challenge)
**Authority:** This document records verified decisions from the hardening session. It supplements `FACTORY_ROADMAP_v3_OUTLINE.md` and supersedes corresponding sections of `FACTORY_HARDENING_BRIEFING.md` where findings have been resolved.

---

## Resolved Findings from Briefing

### Finding 1: RESOLVED — Codex CLI Exists

**Previous claim:** "Codex CLI does not exist."
**Actual status:** Codex CLI is OpenAI's open-source terminal coding agent (`npm i -g @openai/codex`), built in Rust, with `codex exec` for programmatic mode, AGENTS.md support, MCP integration, and multi-model switching. Verified installed and working (v0.116.0) on owner's Windows 11.

**Root cause of error:** The previous session's architect confused "Codex CLI" (OpenAI's product) with a non-existent tool. This was compounded by the hardening session initially accepting the claim without independent verification — a protocol violation.

**Impact:** The factory has FOUR CLI coding agents, not two:

| Tool | Provider | Version | Programmatic Syntax |
|------|----------|---------|-------------------|
| Claude Code | Anthropic | Current | Interactive + scripted |
| Codex CLI | OpenAI | 0.116.0 | `codex exec --full-auto "prompt"` |
| Copilot CLI | GitHub | 1.0.12 | `copilot -p "prompt" --model gpt-4.1` |
| Gemini CLI | Google | 0.35.3 | `gemini -p "prompt" -o text -y` |

All four verified working on owner's Windows 11 (2026-03-28).

### Finding 2: RESOLVED — Quota Architecture Redesigned

**Previous concern:** Quota limits invalidate "$0/call" assumption.
**Resolution:** Four-tool architecture distributes load across providers. Unlimited GPT-4.1 via Copilot (0x premium) handles bulk work. Codex CLI on Plus provides generous per-5hr windows for frontier model access. Gemini CLI on AI Pro provides 1,500 requests/day. Economics validated at factory scale (~20-30 findings/night).

See "D-H002: Four-Tool CLI Architecture" below.

### Finding 4: RESOLVED — Scholar Registry Seeding Path Identified

**Previous concern:** `scholars.json` is empty.
**Resolution:** Three-source seeding path verified:

1. **usul-data** (primary): 6,159 authors, 4,600 with Hijri death years, 15,655 books. 89.2% match rate against our 65-fixture sample (CC-verified). 7/7 author death years matched exactly. Two enrichment cases found (death years usul-data provides that we lack).
2. **Wikidata SPARQL** (triangulation): madhhab (P9929), teacher/student (P1066/P802). Our contracts already have cross-validation stubs for Wikidata integration.
3. **Shamela metadata** (bibliographic crosswalk): via `shamela` npm library or direct DB access.

See "D-H001: Reference Data Integration" below.

### Finding 5: PARTIALLY RESOLVED — Copilot SDK Deferred

**Previous concern:** Should Copilot SDK replace custom CLI dispatch?
**Resolution:** All four CLIs work via subprocess calls with verified syntax. SDK adds complexity without clear benefit at current scale. Subprocess dispatch is simpler, more portable, and tool-agnostic. DEFERRED — revisit if subprocess overhead becomes a bottleneck.

### Finding 6: RESOLVED — All "Codex" References Now Accurate

The term "Codex" in the factory documents correctly refers to OpenAI's Codex CLI product. No renaming needed — the previous session's Finding 1 was wrong. However, the v3 outline's FIX mode descriptions reference "Codex reviews" when the routing table now assigns different tools to different severity levels. These descriptions should be updated to reference the four-tool routing table (D-H002) instead of naming specific tools.

### Finding 7: RESOLVED — Cross-Provider Diversity Redesigned

**Previous design:** Three tools (CC + Codex + Gemini).
**New design:** Four tools from four providers. See D-H002.

---

## New Design Decisions

### D-H001: Reference Data Integration Architecture

**Decision:** The factory integrates external reference datasets as offline, read-only cross-reference indexes for HUNT mode verification. External data NEVER writes directly to canonical registries.

**Architecture:**

```
External Sources (frozen snapshots, downloaded during factory setup)
    │
    ├── usul-data → library/registries/usul_crossref.json
    │   Contains: Arabic author names, Hijri death years, Turath IDs,
    │   genre tags for matched books. 89% match rate verified.
    │
    ├── Wikidata SPARQL → library/registries/wikidata_crossref.json
    │   Contains: madhhab (P9929), teacher/student (P1066/P802),
    │   death dates for triangulation. Provenance-tagged.
    │
    └── (Future) Shamela metadata → library/registries/shamela_crossref.json
        Contains: Shamela category tree, page counts, author associations.

Factory HUNT Mode
    │
    ├── Cross-checks pipeline output against crossref indexes
    ├── Disagreements → findings (severity by field: author=CRITICAL, genre=HIGH)
    ├── Enrichment candidates → separate queue for architect review
    └── NEVER auto-writes to scholars.json or any canonical registry
```

**Firewall rule (non-negotiable):** External reference data writes to `*_crossref.json` files with provenance tags and match-confidence scores. Only the architect (human gate) promotes candidates to canonical registries after review. This prevents Gemini's identified risk of "silent registry poisoning."

**Matching strategy (for usul-data):** Two-factor matching (title + author), not title-only:
1. Normalize Arabic: strip diacritics, normalize alef/hamza, remove edition markers
2. Match title: exact → substring containment → Jaccard word overlap > 0.6
3. Validate with author: compare death year from OpenITI author ID prefix
4. Require title similarity > 0.7 to prevent same-author-different-book false positives
5. Match volume ordinals explicitly to prevent volume confusion

**Verified match rate:** 89.2% true matches across 65 test fixtures (CC empirical verification, 2026-03-28).

**Integration timeline:** Session 1 (factory setup). Pre-compute crosswalk for all 2,519 books.

### D-H002: Four-Tool CLI Architecture

**Decision:** The factory uses four CLI coding agents from four independent providers, each assigned to roles matching its structural strengths.

**Tool Inventory:**

| Tool | Provider | Subscription | Cost | Quota |
|------|----------|-------------|------|-------|
| Claude Code | Anthropic | Max | Owned | Unlimited |
| Codex CLI | OpenAI | ChatGPT Plus ($20/mo) | $20/mo | 33-168 msg/5hr (GPT-5.4); currently 2x promo |
| Copilot CLI | GitHub | Student (3yr) | $0 | 300 premium/mo + unlimited 0x models |
| Gemini CLI | Google | AI Pro ($19.99/mo) | $20/mo | ~1,500 requests/day |

**Total incremental cost:** ~$40/month (Plus + AI Pro). Claude Max and Copilot Student already owned.

**Role Assignments:**

| Factory Mode | Task | Tool | Model | Why |
|-------------|------|------|-------|-----|
| FIX | Implement code changes | Claude Code | Opus 4.6 | Deepest repo context, strongest builder, unlimited |
| HUNT | Bulk review (LOW/MEDIUM) | Copilot CLI | GPT-4.1 (0x) | Unlimited, different provider than builder |
| HUNT | Scholarly review (HIGH) | Codex CLI | GPT-5.4 | Frontier model, AGENTS.md for KR-specific review |
| HUNT | Adversarial challenge (HIGH+) | Gemini CLI | Gemini 3 Pro | Independent training data, structural adversary |
| HUNT | CRITICAL escalation | Copilot CLI | Claude Opus 4.5 (3x) | Different Claude version than builder |
| EVALUATE | Cross-provider consensus | Codex + Gemini + Copilot | Mixed | Three independent reviews on HIGH+ findings |

**Dispatch pattern:**

```bash
# Builder
# Claude Code — interactive or scripted (existing pattern)

# Bulk reviewer (unlimited)
copilot -p "$REVIEW_PROMPT" --model gpt-4.1

# Scholarly reviewer (frontier)
codex exec --full-auto "$REVIEW_PROMPT"

# Adversarial challenger
gemini -p "$CHALLENGE_PROMPT" -o text -y

# CRITICAL escalation
copilot -p "$ESCALATION_PROMPT" --model claude-opus-4.5
```

**Nightly budget at ~25 findings/night, ~22 nights/month:**

| Severity | Count/night | Tool | Monthly quota impact |
|----------|------------|------|---------------------|
| LOW (40%) | ~10 | Copilot GPT-4.1 | 0x = free |
| MEDIUM (35%) | ~9 | Copilot GPT-4.1 | 0x = free |
| HIGH (20%) | ~5 | Codex (GPT-5.4) + Gemini (3 Pro) | ~110/mo Codex (within window), ~110/mo Gemini (trivial vs 1,500/day) |
| CRITICAL (5%) | ~1 | Copilot (Claude Opus 4.5, 3x) | ~66 premium/mo of 300 |

**Graceful degradation:** If any tool hits limits, Copilot CLI can access multiple model families via `--model`. OpenRouter API is always available as pay-per-token backstop.

### D-H003: Severity Classification Is Deterministic

**Decision:** Reaffirms Finding 3 from the briefing with one addition: severity is classified by deterministic field-level rules BEFORE any LLM review. The routing table then selects tools based on severity.

| Finding affects... | Auto-classification | Review tools |
|---|---|---|
| `author`, `attribution`, `school`, `genre`, `multi_layer`, `self_containment` | CRITICAL | Codex + Gemini + Copilot (3-provider consensus) |
| Crash, contract violation, data loss, validation bypass | HIGH | Codex + Gemini (2-provider review) |
| Edge case handling, defensive code, missing validation | MEDIUM | Copilot GPT-4.1 (single review) |
| Logging, naming, formatting, dead code | LOW | Copilot GPT-4.1 (single review) |

This eliminates Finding 3's concern ("who classifies severity?") — the answer is: deterministic rules based on which fields are affected, not LLM judgment.

### D-H004: Testing Tools Integration

**Decision:** Hypothesis (property-based testing) and Mutmut (mutation testing) are integrated into the factory as HUNT sub-modes on WSL2.

**Hypothesis strategy:** Custom Arabic-aware generators, NOT raw string generation. Required patterns:
- Valid HTML DOM generators with adversarial Arabic text injection (ZWNJ, consecutive tatweels, RTL/LTR override marks)
- Property: normalization idempotence (`normalize(x) == normalize(normalize(x))`)
- Property: consensus determinism (any valid input → valid BookRecord OR deterministic error code)
- Property: contract roundtrip integrity (`model_validate(result.model_dump()) == result`)

**Mutmut strategy:** Targeted at pure-logic modules only:
- Confidence scoring algorithms
- Validation checks and contract validators
- Normalization functions
- NOT I/O-heavy HTML parsing or fixture-reading code
- Configure `max_stack_depth` to avoid running hundreds of integration tests per mutant

**Timeline:** WSL2 factory setup (Session 2.5+).

### D-H005: Tool Deferral Decisions

| Tool | Verdict | When | Rationale |
|------|---------|------|-----------|
| CAMeL Tools | DEFER | Scholar Interface phase | Morphological analysis useful for search, not for factory HUNT. Blocked by C extension issues on Windows. |
| KITAB passim | DEFER | Phase 2+ (Quality Level 3+) | Text reuse detection requires significant compute and corpus preparation |
| OpenITI mARkdown parser (oimdp) | DEFER | PDF format path (Phase 3) | Independent structure verification baseline |
| CheckList + TextAttack | DEFER | 30-book probe phase | Behavioral and adversarial NLP testing for excerpting |
| Shamela npm API | DEFER | Session 3+ | Requires Node.js + API key setup; crosswalk is lower priority than usul-data |
| Copilot SDK | DEFER | If subprocess overhead becomes bottleneck | Adds complexity without clear benefit at current scale |
| Great Expectations / Pandera | Session 1 | Factory setup | Lightweight data quality expectations mapping to existing invariants |

---

## Cross-Provider Consultation Record

This session used structured cross-provider consultation for every major decision:

| Aspect | ChatGPT (Deep Research) | Claude Code (Empirical) | Gemini (Adversarial) |
|--------|------------------------|------------------------|---------------------|
| **Reference data tools** | Found: Wikidata SPARQL (P9929, P1066/P802), Shamela S1.db narrators (18,989), CheckList methodology, Great Expectations, OpenITI mARkdown parsers, Europeana tiered quality model | Verified: usul-data structure (6,159 authors, 15,655 books, 39 genres), CAMeL Tools partial install, Mutmut blocked on Windows | Challenged: Schema mismatch risk (partially valid — fuzzy matching needed, but JSON-LD claim was wrong), silent registry poisoning (valid — firewall rule adopted), network dependency (valid — offline-first adopted) |
| **Shamela ID join** | N/A | Verified: 89.2% match rate, 7/7 author agreement, 3 false positive modes identified with fixes | N/A |
| **CLI architecture** | Verified: Codex exec scripted usage on Plus allowed; warned about 5hr window limits (valid but not blocking at our scale) | Verified: all 4 CLIs work programmatically, exact syntax documented | N/A (prompts prepared but not yet sent) |

---

## Outstanding Items (Not Yet Addressed in This Session)

### Remaining Aspects to Harden

- **Aspect 3:** Monitoring, alerting, and morning report architecture
- **Aspect 4:** Orchestrator extension design (extending overnight_orchestrator.py for multi-mode, multi-tool dispatch)
- **Aspect 5:** Synthetic adversarial data for Arabic text edge cases
- **Aspect 6:** Day 1 scope expansion (excerpting likely complete by factory launch)

### Outstanding Relay Prompts (Prepared, Not Sent)

None currently blocking. Session 3 preparation will require:
- Copilot CLI custom agent (`.agent.md`) design for KR review/adversary roles
- Codex CLI AGENTS.md design for KR scholarly review context
- Gemini CLI project context configuration
- WSL2 interop verification (all tools from within WSL2)

### Corrections to Apply to v3 Outline

1. FIX mode descriptions: replace tool-specific names with reference to D-H002 routing table
2. Session 3: rewrite CLI setup for four tools (was designed for three)
3. Session 4-5 benchmark: include all four tools in benchmark task assignments
4. Add D-H001 through D-H005 to Design Decisions section
