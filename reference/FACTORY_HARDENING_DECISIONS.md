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
| Codex CLI | OpenAI | ChatGPT Plus ($20/mo) | $20/mo | ChatGPT auth: credit-based limits (plan-dependent); API key auth: per-token billing (recommended for factory) |
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
| EVALUATE | Cross-provider consensus | Codex + Gemini + Copilot | Mixed | Architect receives union of all three reviews; nothing discarded. No automated consensus algorithm — architect decides. |

**Dispatch pattern:**

```bash
# Builder
# Claude Code — interactive or scripted (existing pattern)

# Bulk reviewer (unlimited, structured JSON)
copilot -p "$REVIEW_PROMPT" --model gpt-4.1 --output-format=json

# Scholarly reviewer (frontier, structured JSON)
codex exec --full-auto "$REVIEW_PROMPT"

# Adversarial challenger (structured JSON)
gemini -p "$CHALLENGE_PROMPT" --output-format json -y

# CRITICAL escalation (structured JSON)
copilot -p "$ESCALATION_PROMPT" --model claude-opus-4.5 --output-format=json
```

**Codex CLI auth mode for factory:** Use API key auth (`preferred_auth_method = "apikey"` in config.toml or `OPENAI_API_KEY` env var) for factory automation. This gives per-token billing with predictable costs and avoids subscription credit limit uncertainty. ChatGPT auth is for interactive developer use; API key auth is OpenAI's recommendation for programmatic/CI workflows.

**Nightly budget at ~25 findings/night, ~22 nights/month:**

| Severity | Count/night | Tool | Monthly quota impact |
|----------|------------|------|---------------------|
| LOW (40%) | ~10 | Copilot GPT-4.1 | 0x = free |
| MEDIUM (35%) | ~9 | Copilot GPT-4.1 | 0x = free |
| HIGH (20%) | ~5 | Codex (GPT-5.4) + Gemini (3 Pro) | ~110/mo Codex (API key: per-token, ~$5-15/mo est.), ~110/mo Gemini (trivial vs 1,500/day) |
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

### D-H006: Severity Escalation Mechanisms

**Decision:** Severity classification (D-H003) is the default routing decision, but two escalation paths exist to catch "hidden CRITICALs" — findings initially classified at lower severity that actually affect knowledge-integrity fields.

**Source:** Independent convergence from ChatGPT deep research and Gemini adversarial challenge on the D-H002 cross-provider review (2026-03-28).

**Path 1 — Pre-review field scan (deterministic):**

Before routing a finding to its classified severity tier, the orchestrator greps the associated diff for CRITICAL-field names: `author`, `attribution`, `school`, `genre`, `multi_layer`, `self_containment`, `primary_text`, `layer_id`. If any are present in the diff, the finding is escalated to at minimum HIGH regardless of its initial classification. This catches cases where a "defensive code" fix in a utility function actually modifies how CRITICAL fields are computed.

**Path 2 — Mid-review escalation interrupt (LLM-signaled):**

All reviewer prompts (LOW through HIGH) include the instruction: "If during your review you discover that this finding affects author attribution, school classification, self-containment, or any other knowledge-integrity field listed in KNOWLEDGE_INTEGRITY.md threats T-1 through T-4, output the signal `ESCALATION_REQUIRED: <reason>` and stop your review."

When the orchestrator detects `ESCALATION_REQUIRED` in a reviewer's output, it:
1. Logs the escalation with the reviewer's reasoning
2. Mutates the finding's severity to CRITICAL
3. Re-queues the finding into the CRITICAL dispatch tier
4. The re-queued review includes the original reviewer's escalation rationale as context

**Design rationale:** Path 1 is cheap and deterministic — it runs before any LLM call. Path 2 is a safety net for cases Path 1 misses (indirect impact through call chains, data flow effects). Together they close the gap that both ChatGPT and Gemini identified: severity must not be permanently immutable after initial classification.

### D-H007: Shadow Routing Audit (Canary Check)

**Decision:** 5-10% of LOW/MEDIUM findings are duplicated to the HIGH+ review panel nightly as a canary check for systematic blind spots in the primary reviewer (GPT-4.1).

**Source:** Independent convergence — both ChatGPT and Gemini recommended this mechanism without coordination.

**Mechanism:**

Each night, the orchestrator randomly selects ~5-10% of findings classified as LOW or MEDIUM and duplicates them to the HIGH+ tier (Codex + Gemini dual review). The original LOW/MEDIUM review proceeds normally. The shadow reviews are compared offline.

**Disagreement handling:**
- If the shadow review agrees with GPT-4.1 → no action
- If the shadow review finds additional issues GPT-4.1 missed → log as a "blind spot" finding in the morning report
- If blind spot findings cluster around a specific domain (e.g., validation logic, Arabic text handling, Pydantic patterns) → the orchestrator permanently routes that domain to the HIGH+ tier

**Scale:** At ~19 LOW/MEDIUM findings/night, 5-10% = 1-2 shadow reviews/night. Minimal quota impact on Codex and Gemini.

**Timeline:** Session 6+ (orchestrator extension). Not needed for factory Day 1 — this is a maturity mechanism that improves the factory's self-awareness over time.

---

## Cross-Provider Consultation Record

This session used structured cross-provider consultation for every major decision:

| Aspect | ChatGPT (Deep Research) | Claude Code (Empirical) | Gemini (Adversarial) |
|--------|------------------------|------------------------|---------------------|
| **Reference data tools** | Found: Wikidata SPARQL (P9929, P1066/P802), Shamela S1.db narrators (18,989), CheckList methodology, Great Expectations, OpenITI mARkdown parsers, Europeana tiered quality model | Verified: usul-data structure (6,159 authors, 15,655 books, 39 genres), CAMeL Tools partial install, Mutmut blocked on Windows | Challenged: Schema mismatch risk (partially valid — fuzzy matching needed, but JSON-LD claim was wrong), silent registry poisoning (valid — firewall rule adopted), network dependency (valid — offline-first adopted) |
| **Shamela ID join** | N/A | Verified: 89.2% match rate, 7/7 author agreement, 3 false positive modes identified with fixes | N/A |
| **CLI architecture** | Verified: Codex exec scripted usage on Plus allowed; warned about 5hr window limits (valid but not blocking at our scale) | Verified: all 4 CLIs work programmatically, exact syntax documented | N/A (prompts prepared but not yet sent) |
| **D-H002 challenge (routing architecture)** | Verified GPT-4.1 adequate for LOW/MEDIUM (SWE-bench 54.6%). Corrected Codex CLI auth model: API key mode recommended for factory. Verified all 4 CLIs have structured JSON output. Documented WSL2 interop risks (path semantics, filesystem perf, interop config). Proposed canary audit lane + auto-escalation. Proposed Usage Ledger architecture for quota tracking. | N/A | Analyzed wrong repository (sparxsystems/krino ≠ rayanino/kr) — 60% of report invalidated. Pipe buffer / deadlock analysis invalid (orchestrator already uses Popen+communicate). DAG proposal overengineered. VALID findings: severity escalation mid-review (adopted as D-H006 Path 2), consensus algorithm underspecification (clarified in D-H002), shadow routing (adopted as D-H007). |

### D-H002 Challenge Verdict (2026-03-28)

**Cross-provider challenge completed.** D-H002's core architecture (four-tool routing, severity-based dispatch, role assignments) **SURVIVES** both challenges. Five additions adopted:

1. **D-H002 updated:** Codex CLI auth mode clarified (API key for factory), dispatch pattern updated with `--output-format json` flags, CRITICAL consensus clarified as architect-reviewed union
2. **D-H006 added:** Two-path severity escalation (pre-review field scan + mid-review LLM interrupt)
3. **D-H007 added:** Shadow routing audit (5-10% canary from LOW/MEDIUM to HIGH+ panel)
4. **Session 3 note:** All four CLIs support structured JSON output — orchestrator must use it
5. **WSL2 setup note:** Repo must live in WSL2 native filesystem; interop settings must be verified; Codex CLI recommends WSL install

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
- Gemini CLI project context configuration (GEMINI.md)
- WSL2 interop verification (all tools from within WSL2)

### WSL2 Setup Requirements (from D-H002 challenge)

- **Filesystem:** KR repo must live in WSL2 native filesystem (`/home/...`), NOT on Windows mount (`/mnt/c/...`). Cross-filesystem access degrades performance.
- **Interop:** Verify `/etc/wsl.conf` has `[interop] enabled=true` and `appendWindowsPath=true`. Document these settings in factory setup script.
- **Codex CLI:** Install inside WSL2 as Linux binary (official recommendation: "Windows support is experimental, use WSL"). Avoids path translation issues.
- **Path translation:** If any CLI runs as Windows executable from WSL2, the orchestrator must translate Linux paths to Windows paths before passing them as arguments.
- **Codex CLI network:** Codex CLI may sandbox network during execution. Factory review prompts must not depend on external network calls during review.

### Structured Output for Session 3 (from D-H002 challenge)

All four CLIs support machine-readable JSON output. The orchestrator MUST use these modes instead of parsing human-readable text:
- Copilot CLI: `--output-format=json` (JSONL)
- Claude Code: `--output-format json` (JSON, supports `--json-schema`)
- Gemini CLI: `--output-format json` (JSON with response + stats including per-model token usage)
- Codex CLI: `codex exec --full-auto` (structured output; also Codex App Server JSON-RPC for deeper integration)

The orchestrator should define an internal `AgentResult` schema that all tool outputs are normalized into, making dispatch boundaries clean and tool-agnostic.

### Quota Tracking Architecture (from D-H002 challenge)

Three-layer design for Session 6+:
1. **Usage Ledger** (append-only): keyed by (provider, model, run_id, finding_id). Stores request counts, token counts, latency, errors, cost fields from CLI telemetry.
2. **Quota Adapters** (per-provider): maps ledger entries to provider quota units — Copilot premium requests/multipliers, Gemini daily request caps, OpenAI API RPM/TPM and token spend, Claude Code per-run budget caps.
3. **Policy Layer**: implements graceful degradation from D-H002 — routes work away from constrained tools, downgrades to 0x models when premium requests scarce.

Both Copilot CLI and Gemini CLI expose OpenTelemetry-based telemetry, enabling quota tracking based on actual measured usage rather than estimates.

### Corrections to Apply to v3 Outline

1. FIX mode descriptions: replace tool-specific names with reference to D-H002 routing table
2. Session 3: rewrite CLI setup for four tools (was designed for three), add structured JSON output requirement
3. Session 4-5 benchmark: include all four tools in benchmark task assignments
4. Session 6: add D-H006 escalation mechanisms and D-H007 shadow routing to orchestrator extension scope
5. Add D-H001 through D-H007 to Design Decisions section
