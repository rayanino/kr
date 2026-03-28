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

### D-H008: Morning Report Architecture — FINAL

**Decision:** The morning report is the primary interface between the factory and the architect/owner. It is restructured around action-orientation, CRITICAL-first visibility, four-tool routing auditability, escalation traceability, trend awareness, and a two-layer data model for long-term operation.

**Source:** Architect analysis of existing `generate_morning_report()` (lines 1086-1218 of orchestrator) against D-H002 through D-H007 requirements. Cross-provider challenged: ChatGPT deep research (CI/CD report patterns, MLOps monitoring, build-sheriff practices, canary analysis) + Gemini adversarial (mass cascade, tool outage, escalation traceability, alerting delay safety, clean-night UX).

**Design principles:**

1. **Actions first, evidence second.** The report opens with what the architect must *do*, not what *happened*. Build-sheriff and SRE practice converge on this: the top of the report is a triage queue, not a situation report. (Source: ChatGPT — Google SRE, Chromium sheriffing, Drake build-cop.)
2. **CRITICALs bounded, not unbounded.** The CRITICAL section caps at 3 detailed entries + an aggregate count. In a mass cascade (50 CRITICALs across engines), an unbounded top section buries the Summary and becomes unreadable. (Source: Gemini stress test #1.)
3. **Four-tool visibility with consensus degradation warnings.** Every finding shows which tools reviewed it. If a required reviewer was unavailable (e.g., Gemini down during a 3-provider CRITICAL review), the finding explicitly flags incomplete consensus — the architect must not infer review completeness from tool count alone. (Source: Gemini stress test #2.)
4. **Escalation provenance embedded in findings.** An escalated finding's full lifecycle (original severity, trigger path, reviewer rationale) is recorded in the finding entry itself, not in a separate section. The Escalation Events section is an aggregate summary (counts, patterns), not the primary record. This eliminates cross-referencing across three report sections. (Source: Gemini stress test #3.)
5. **Trend awareness via Δ vs previous night.** The report is not an isolated snapshot. Key metrics show delta from the previous run: findings per severity, escalations, shadow disagreements, task failures. This follows canary-analysis and MLOps-monitoring conventions where deviation-from-baseline is the primary signal. (Source: ChatGPT — Spinnaker canary analysis, SageMaker Model Monitor.)
6. **Clean-night fast path.** When zero CRITICAL/HIGH findings, zero escalations, zero shadow disagreements, and zero task failures: the report opens with "✅ All Clear" and collapses to Summary + Tests + Decisions only. Empty severity headers are dynamically omitted. The architect confirms health in one glance. (Source: ChatGPT + Gemini convergence.)
7. **Tool performance as exception metric.** Latency is reported only when it breaches a threshold (timeout, >2× historical baseline). Error rates are always shown — they're actionable daily. Nominal latency values are noise for a daily reader. (Source: Gemini stress test #7.)
8. **Two-layer data model.** Per-run JSON snapshot is necessary but insufficient for months of operation. The factory writes two complementary data stores: (a) an append-only JSONL event ledger for audit trail and trend computation, and (b) a per-run materialized snapshot for reproducible report rendering. (Source: ChatGPT — MLflow metadata stores, TFX ML Metadata, append-only event patterns.)

**Data model:**

```
overnight/
├── events.jsonl              # Append-only event ledger (never truncated)
│   One line per event: finding_detected, review_completed, escalated,
│   scope_paused, shadow_compared, task_started, task_finished, quota_sampled
│   Schema: {"ts": ISO-8601, "event": str, "run_id": str, "data": {...}}
│
├── report_data.json          # Per-run materialized snapshot (overwritten nightly)
│   Complete structured representation of the night's results.
│   Generated from events.jsonl + task outputs at run completion.
│   Includes: findings with full lifecycle, tool performance, scope status,
│   delta values (computed from previous archive), action items.
│
├── MORNING_REPORT.md         # Human-readable rendering of report_data.json
│
├── archive/                  # Preserved per-run snapshots
│   └── {YYYY-MM-DD}/
│       ├── report_data.json  # Frozen snapshot
│       ├── MORNING_REPORT.md # Frozen report
│       └── findings/         # Per-finding detail bundles
│
└── results/                  # Task outputs (existing, unchanged)
    └── {task_id}/
```

The event ledger enables: MTTR computation (finding first_seen → resolved_at across runs), trend analysis (findings/night over time), recurring-finding detection (same file+line across runs), and shadow routing calibration. SQLite query cache deferred to Session 8 (dashboard).

**Report structure (v3):**

```
# Overnight Report — {date}

## ✅ All Clear                              [ONLY if zero CRITICAL/HIGH, zero
                                              escalations, zero shadow disagreements,
                                              zero task failures. Replaces all
                                              findings/escalation/shadow sections.
                                              Report collapses to Summary+Tests+Decisions.]

— OR —

## 📋 Actions Required
[Top-level triage queue. ONLY items requiring human action.
Each entry: finding ID, concrete next step (review/approve/unpause),
severity, link to artifact. Ordered by severity then age.
This is the ONLY section the architect MUST read.]

## 🚨 CRITICAL Findings ({count})
[Only if CRITICALs exist. Max 3 detailed entries showing:
finding ID, affected fields, description, reviewing tools + models,
consensus status (complete/degraded with reason), scope pause status,
escalation provenance if applicable (original severity → CRITICAL, trigger path,
reviewer rationale). Remaining CRITICALs: count + paused-phase list only.
Full details for all CRITICALs in Findings by Severity below.]

## Summary
- Duration, task counts (completed/failed/skipped/rolled-back), total cost
- Scope status: active|paused|noise-breaker per engine phase
- Git range: {start_hash}..{end_hash}
- Δ vs previous night: findings by severity, escalations, shadow disagreements

## Findings by Severity
### HIGH ({count}) — Architect must approve fix
### MEDIUM ({count}) — Auto-fixed, cross-provider reviewed
### LOW ({count}) — Auto-fixed, self-reviewed
[CRITICAL findings also appear here as complete audit records.
Empty severity tiers dynamically omitted.]

Each finding entry (unified schema):
- ID, severity (current), affected field(s), description
- Reviewing tool(s) + model(s)
- Consensus status: complete | degraded [⚠ {tool} unavailable — {N}-provider consensus incomplete]
- Fix status: pending | fixed | architect_hold
- Escalation provenance (if escalated): original_severity → current_severity,
  trigger (pre-review field scan | mid-review interrupt), reviewer + rationale
- first_seen timestamp (for MTTR tracking across runs)
- Link to artifact (diff, review output, test log)

## Escalation Summary (D-H006)
[Only if escalations occurred. Aggregate metrics only — NOT the primary
record of escalation rationales (those are in finding entries above).]
- Escalation count, breakdown by trigger path (pre-scan vs mid-review)
- Pattern notes (e.g., "3 escalations in normalization this week")

## Shadow Routing Summary (D-H007)
[Only after D-H007 is active]
- Canary checks: {count}, Agreements: {count}, Blind spots: {count}
- Blind spot details with affected domain
- Δ vs previous night: blind_spots (+N/-N)

## Factory Changes
[Only if factory committed code during FIX mode.]
- Files modified (top N with diff stat)
- Commits in git range (overnight: prefixed only)
- Mapping: finding ID → commit that fixed it

## Tool Performance
| Tool | Model | Findings Reviewed | Errors | Escalations Triggered |
[Per-tool breakdown. Latency shown ONLY if it exceeded 2× baseline
or caused timeouts — otherwise omitted as noise.]

## Quota Usage
| Provider | Used | Remaining | Status |
[From Usage Ledger when available; omitted before Session 9-10]

## Tests
- Added: {count}, Net delta: +{n}, Total: {total} passing

## Autonomous Decisions
[From decisions.log — unchanged from current]
```

**Alerting (DEFERRED to Session 8):**

Immediate push notification for CRITICAL findings is a convenience, not a safety necessity. The CRITICAL pause mechanism (D-F016) already self-protects — the factory stops hunting the affected phase immediately. No additional CRITICALs can accumulate in that phase during the overnight delay.

Gemini challenged this: "pausing hunting doesn't prevent downstream phases from executing on compromised upstream data." This concern is **valid for FIX mode** (an upstream auto-fix could introduce regressions that downstream HUNT tasks then encounter as false positives) but **does not apply to HUNT mode** (HUNT reviews code in isolation, it doesn't run the pipeline to produce downstream data). The FIX-mode variant is addressed in D-H009 (orchestrator) as a cascading-pause consideration, not in the report design.

The owner reads the morning report first thing; the architect acts within hours. If push alerting is desired later:
- Windows notification via PowerShell script checking for `overnight/CRITICAL_ALERT.txt`
- Telegram bot (single API call, no server needed)
- Discord webhook (single HTTP POST)

These are Session 8 enhancements, not Day 1 requirements.

**Implementation timeline:** Session 6-7 (orchestrator extension). The event ledger (`events.jsonl`) and JSON snapshot (`report_data.json`) are built in Session 6. The Markdown renderer with action-first layout, clean-night fast path, and bounded CRITICAL section is built in Session 7. Report archival (`overnight/archive/{date}/`) is Session 6 infrastructure.

**Cross-provider challenge record:**
- ChatGPT (deep research): Identified 6 gaps — trend/baseline comparison, action queue, MTTR tracking, clean-night fast path, report archival, difference report. Recommended two-layer data model (JSONL + snapshot). All accepted.
- Gemini (adversarial): Identified 7 stress-test results — mass cascade overflow (accepted: cap at 3), consensus degradation (accepted: inline warning), escalation fragmentation (accepted: embed in finding), cascading downstream pause (partially accepted: valid for FIX mode, noted for D-H009), clean-night template rigidity (accepted: dynamic omission), trend absence (accepted: Δ values), latency noise (accepted: exception-only reporting).
- Cross-provider convergence: Trend data and clean-night fast path identified independently by both. CRITICAL bounding and consensus degradation unique to Gemini. Action queue, MTTR, archival, and data model unique to ChatGPT.

### D-H009: Orchestrator Extension Design — FINAL

**Decision:** The existing `scripts/overnight_orchestrator.py` (1,576 lines, four execution backends) is extended — not replaced — with severity-routing, scope management, event-sourced persistence, and mode dispatch capabilities.

**Source:** Architect analysis of current orchestrator architecture against D-H002 through D-H008 requirements. Cross-provider challenged: ChatGPT deep research (component decomposition, event-sourcing patterns, SARIF baseline comparison, concurrency analysis, line estimates) + Gemini adversarial (cascading failure, deduplication, escalation loops, quorum, crash safety, line estimates).

**Guiding principles:**

1. **Sequential at the top level, parallelizable per finding later.** At ~25 findings/night, top-level sequential dispatch is correct for Session 6. However, "parallelism pointless" was too strong in the original draft. For HIGH/CRITICAL findings requiring 2-3 tools, bounded parallelism per finding (run reviewer tools concurrently with per-tool semaphores) provides a favorable complexity/benefit ratio. Session 6 implements sequential; the ReviewOrchestrator interface is designed so per-finding parallelism can be added in Session 7 without restructuring. (Source: ChatGPT — Spinnaker canary pattern, bounded concurrency.)

2. **Event-sourced persistence.** All state changes are recorded as events in the JSONL ledger (D-H008) before side-effects execute. This gives: crash-recovery safety (resume dispatch from ledger without re-running HUNT), audit trail, and trend computation. The pattern: Ingest → Classify → Persist (always), then Route/Dispatch from persisted state. (Source: ChatGPT — event-sourcing in audit-heavy domains.)

3. **Deterministic fingerprinting for cross-run identity.** Findings need stable identity across nightly runs to avoid duplicate reviews and enable MTTR tracking. Fingerprint = deterministic hash of (file_path, rule_id, normalized_location, invariant_category). Only deterministic inputs — never LLM-produced fields. Matches SARIF's `baselineGuid` + `baselineState` pattern. (Source: ChatGPT — SARIF specification; Gemini — deduplication concern.)

**Extension components (Session 6) — 7 components:**

**1. ScopeManager** — reads/writes `ops_manifest.json`, enforces engine dependency DAG
- Loads `factory_scope` section at orchestrator start
- `is_phase_huntable(engine, phase) → bool`
- `pause_phase(engine, phase, reason)` — writes to manifest, logs decision, emits `scope_paused` event
- **Engine dependency DAG** (static, known at design time): `source → normalization → excerpting`. Pausing any upstream node automatically pauses all downstream nodes. (Source: Gemini stress test #1 — cascading FIX-mode failure; ChatGPT convergence.)
- `noise_check(engine, phase, finding_count) → bool` — pauses on >10 findings/phase/cycle
- Read-only for status transitions other than pausing — architect unpauses manually
- All writes use existing `_atomic_write` pattern

**2. SeverityClassifier** — pure function, deterministic field-level rules (D-H003)
- Input: finding dict (from HUNT task output) + associated diff
- Scans `affected_fields` list against CRITICAL fields: `author`, `attribution`, `school`, `genre`, `multi_layer`, `self_containment`, `primary_text`, `layer_id`
- Also scans for HIGH indicators: crash, contract violation keywords, `ValidationError`, `FATAL` error codes
- Pre-review field scan (D-H006 Path 1): greps associated diff for CRITICAL-field names, escalates to minimum HIGH if found
- Returns: classification decision + reasons (no I/O, no dispatch, no mutation)
- Pure function: testable with fixed inputs, no side effects

**3. ToolDispatcher** — maps severity to tool invocations (D-H002)
- `dispatch(finding, severity) → list[ReviewResult]`
- LOW/MEDIUM: `copilot -p "$PROMPT" --model gpt-4.1 --output-format=json`
- HIGH: sequential `codex exec` + `gemini --output-format json`
- CRITICAL: sequential `copilot --model claude-opus-4.5` + `codex exec` + `gemini --output-format json`
- Each invocation uses structured JSON output; result parsed into internal `ReviewResult` schema
- Each `ReviewResult` records: tool, model, success/failure, latency, parsed output or error reason
- **Minimum quorum enforcement** (Source: Gemini stress test #4):
  - CRITICAL: requires ≥2 independent provider reviews. If quorum not met → finding status = `architect_hold`
  - HIGH: requires ≥1 review
  - LOW/MEDIUM: requires ≥1 review (single provider)
- On tool failure: log error, record in `failed_reviews`, emit `review_failed` event. Continue dispatching remaining tools. Check quorum after all dispatches complete.
- All subprocess calls use the existing `_atomic_write` pattern for any state they persist

**4. EscalationDetector** — mid-review interrupt parsing (D-H006 Path 2)
- After each review result is received, scan for `ESCALATION_REQUIRED` signal
- If detected: propose escalation event (original_severity, proposed_severity, reviewer, rationale)
- **Max escalation depth = 1** (Source: Gemini stress test #3). A finding that has already been escalated once cannot be escalated again. A second `ESCALATION_REQUIRED` signal forces immediate `architect_hold` status. This prevents infinite escalation loops.
- Does NOT directly mutate finding state — proposes events that ReviewOrchestrator acts on
- Emits `finding_escalated` event

**5. FindingStore (RunJournal)** — persistence spine (D-H008 integration)
- Owns the **JSONL event ledger** (`overnight/events.jsonl`): single append-only writer interface. All other components emit events through `append_event()`.
- Owns **per-run snapshot** (`overnight/report_data.json`): materialized view built from events + task outputs at run completion
- Owns **report archival** (`overnight/archive/{YYYY-MM-DD}/`): copies snapshot + report + finding bundles at end-of-run
- Owns **finding fingerprint index**: deterministic hash → `{first_seen, last_seen, baseline_state}`. On each run, computes `baseline_state` vs previous archive: `new | unchanged | absent`. Unchanged findings skip re-review and carry forward `first_seen`. (Source: ChatGPT — SARIF baseline comparison.)
- Owns **trend delta computation**: loads previous archive's snapshot, computes Δ for findings per severity, escalations, shadow disagreements
- All writes use `_atomic_write` or atomic-append (Source: Gemini stress test #5)
- Event types: `finding_detected`, `finding_classified`, `review_requested`, `review_completed`, `review_failed`, `finding_escalated`, `scope_paused`, `shadow_compared`, `task_started`, `task_finished`, `quota_sampled`

**6. ReviewOrchestrator** — routing + lifecycle state machine
- Ingests raw findings from HUNT task outputs
- Applies SeverityClassifier (pure function call)
- Checks FindingStore fingerprint index: if finding is `unchanged` from previous run and still unresolved, transitions directly to `architect_hold` (no re-review). Emits `finding_deduplicated` event.
- For new or changed findings: creates review plan, calls ToolDispatcher
- After dispatch: checks EscalationDetector on each ReviewResult. If escalation proposed and depth < max: re-routes. If depth ≥ max: `architect_hold`.
- Computes `consensus_status` per finding:
  - `required_reviewers`: tools expected for the severity tier (from D-H002)
  - `completed_reviews`: tools that returned parsable output
  - `failed_reviews`: tool failures/timeouts + reason
  - `consensus_status`: `complete | degraded [⚠ {tool} unavailable]`
- Checks quorum (ToolDispatcher enforces, ReviewOrchestrator records)
- Writes events to FindingStore at each state transition
- Tracks finding lifecycle: `pending | reviewing | reviewed | escalated | deduplicated | fixed | architect_hold`
- Interface designed for per-finding parallelism in Session 7 (dispatch calls are independent per finding)

**7. MorningReportRenderer** — pure renderer, no computation
- Consumes `report_data.json` (built by FindingStore at end-of-run)
- Produces `MORNING_REPORT.md` per D-H008 layout: action-first, bounded CRITICALs, clean-night fast path, trend deltas, consensus degradation warnings, embedded escalation provenance
- Deterministic and testable from fixed JSON input — no data fetching, no computation
- All computation (deltas, consensus completeness, action queues, age from first_seen) happens in FindingStore's snapshot builder

**Integration with existing main loop (event-driven pattern):**

```
# Startup
finding_store = FindingStore(archive_dir, events_path)
scope_manager = ScopeManager(manifest, ENGINE_DAG)
classifier = SeverityClassifier(CRITICAL_FIELDS, HIGH_INDICATORS)
dispatcher = ToolDispatcher(TOOL_CONFIG, QUORUM_RULES)
escalation = EscalationDetector(max_depth=1)
orchestrator = ReviewOrchestrator(classifier, dispatcher, escalation, finding_store, scope_manager)

while not shutdown:
    # Phase A: HUNT — existing task execution (unchanged)
    task = pick_next_ready(manifest, state)
    finding_store.append_event("task_started", task)
    result = execute_task(task)
    quality_gate(task, result)
    finding_store.append_event("task_finished", task, result)

    # Phase B: INGEST → CLASSIFY → PERSIST → DISPATCH (new, event-driven)
    if result.status == "success" and has_findings(task):
        findings = load_findings(task)
        for finding in findings:
            # All state changes recorded as events before side-effects
            orchestrator.process_finding(finding, task)
            # process_finding internally:
            #   1. Classify (pure) → emit finding_classified
            #   2. Check fingerprint → if unchanged, emit finding_deduplicated, skip
            #   3. Noise check → if exceeded, emit scope_paused, break
            #   4. Dispatch reviews → emit review_requested, review_completed/failed
            #   5. Check escalation → if triggered, emit finding_escalated, re-dispatch
            #   6. Check quorum → if unmet, set architect_hold
            #   7. If CRITICAL (original or escalated) → scope_manager.pause_phase (cascading)

# End of run
finding_store.build_snapshot(scope_manager, previous_archive)
finding_store.archive_run()
renderer = MorningReportRenderer(finding_store.snapshot)
renderer.render()
```

**What is NOT in Session 6:**
- FIX mode auto-fixing with cross-provider review (Session 7)
- Shadow routing selection and comparison (Session 7, D-H007)
- Per-finding bounded parallelism for HIGH/CRITICAL dispatch (Session 7)
- Usage Ledger / quota tracking (Session 9-10)
- EVALUATE, BENCHMARK, and CROSS-ENGINE modes (Session 7)

**Estimated extension:** ~800-1,200 new lines. Orchestrator grows from ~1,576 to ~2,400-2,800 lines. The original estimate of 400-600 was systematically underestimated (both ChatGPT and Gemini converge on this). The "platform spine" — event ledger, fingerprinting, archival, lifecycle tracking, delta computation — is where the real complexity lives. Session 6 may need to be split into 6a (persistence spine + ScopeManager + SeverityClassifier) and 6b (ToolDispatcher + ReviewOrchestrator + MorningReportRenderer).

**Exit criteria for Session 6:**
- `ScopeManager` reads `ops_manifest.json`, pauses phases correctly, and cascading pause propagates through engine DAG
- `SeverityClassifier` classifies a test finding set with 100% accuracy against D-H003 rules (pure function, no I/O)
- `ToolDispatcher` invokes all four tools with structured JSON output, parses results, enforces quorum (CRITICAL ≥2 providers)
- `EscalationDetector` detects `ESCALATION_REQUIRED` signal in mock output; second escalation → `architect_hold`
- `FindingStore` appends events to JSONL ledger, builds snapshot, archives to `overnight/archive/{date}/`, computes fingerprints, deduplicates unchanged findings across runs
- `ReviewOrchestrator` processes a test finding set end-to-end: classify → deduplicate → dispatch → escalate → record
- `MorningReportRenderer` produces D-H008 layout from fixed `report_data.json` input
- All existing tests still pass
- Dry-run mode (`--dry-run`) shows routing decisions without executing tool calls
- Crash recovery: kill orchestrator mid-run, restart, verify it resumes from ledger state

**Cross-provider challenge record:**
- ChatGPT (deep research): Identified FindingsManager as unstable megaclass (accepted: split into FindingStore + ReviewOrchestrator). Proposed event-driven loop pattern solving escalation-pause bug in original pseudocode (accepted). Referenced SARIF baseline comparison for cross-run fingerprinting (accepted). Recommended bounded parallelism for HIGH/CRITICAL as Session 7 option (accepted as deferred). Estimated 600-1,200 LOC (accepted: revised to 800-1,200). MorningReportRenderer as pure renderer (accepted).
- Gemini (adversarial): Engine dependency DAG for cascading pause (accepted). Cross-run deduplication via fingerprinting (accepted, converges with ChatGPT's SARIF reference). Escalation loop guard max_depth=1 (accepted). Minimum quorum for CRITICAL reviews ≥2 providers (accepted). Atomic writes for all new state files (accepted). Estimated 1,000-1,200 LOC (accepted: contributes to revised 800-1,200 range).
- Cross-provider convergence: Deduplication/fingerprinting, line count underestimation, and cascading pause need identified independently by both. Event-sourcing pattern unique to ChatGPT. Escalation loop and quorum guards unique to Gemini.

### D-H010: Synthetic Adversarial Data Strategy — FINAL

**Decision:** Adversarial test data for Arabic text edge cases is generated through four complementary layers. Layer 3 is reframed from "LLM generates fixture books" to "mine seeds from real corpus + apply deterministic transforms + LLM-assisted local rewrites + cross-provider verification." A new Layer 4 covers prompt-level attacks for LLM-mediated phases.

**Source:** Architect analysis + ChatGPT deep research (Arabic adversarial NLP landscape, published attack families, tooling inventory, corpus mining vs generation feasibility, prompt adversarial patterns, CheckList-style coverage metrics).

**Layer 1 — Hypothesis property-based testing (D-H004, Session 2.5+):**
Arabic-aware generators produce structured adversarial inputs targeting deterministic properties. Already designed:
- Valid HTML DOM generators with ZWNJ, consecutive tatweels, RTL/LTR override marks
- Normalization idempotence: `normalize(x) == normalize(normalize(x))`
- Consensus determinism: any valid input → valid BookRecord OR deterministic error code
- Contract roundtrip: `model_validate(result.model_dump()) == result`

**Layer 2 — Overnight probe generation (existing, continuous):**
The overnight orchestrator already generates targeted adversarial tests nightly. Proven track record:
- `test_pathological_arabic.py`: 40 tests across 8 Unicode edge-case classes
- `test_fdet_adversarial.py`: 51 tests for all 9 F-DET deterministic field computations
- `test_boundary_exhaustive.py`: 16 boundary-value tests for TINY/OVERSIZED thresholds
- Net effect: 142 adversarial tests added across 3 overnight sessions

This layer continues operating — it's the factory's primary adversarial mechanism.

**Layer 3 — Mined seeds + constrained adversarial synthesis (Session 4.5):**

The original draft proposed "LLM generates adversarial fixture books." ChatGPT deep research found this is the wrong approach: published Arabic adversarial work is almost entirely token/character-level perturbations over real data. Generating realistic classical Arabic scholarly prose with precise adversarial properties is hard to control and verify. The evidence-based approach: mine real corpus seeds, apply deterministic transforms, use LLMs only for constrained local rewrites.

**Step 1: Mine seeds from the 2,519-book Shamela corpus.** CC scans for structural markers, tags spans by threat, stores as gold fixtures. LLMs assist with labeling — not fabrication. Targets: multi-layer sharḥ/matn boundaries (T-3), dense quotation chains and "قال/قلت" shifts (T-4), refutation→position patterns (T-2, T-4), heavy isnād lists (T-3), poetry blocks in prose, footnote-heavy pages (T-4), "فائدة/تنبيه" section markers.

**Step 2: Apply deterministic adversarial transforms from evidence-backed families.**

| Attack Family | Target Threat | Evidence | Tools/Resources |
|---|---|---|---|
| Diacritics manipulation | T-1 | Published black-box Arabic adversarial strategy (2025); meaning-changing in religious texts | CAMeL Tools morphological generator |
| Dot/letter-shape confusions | T-1 | Published character-level attacks exploiting ب/ت/ث, ج/ح/خ, ن/ي dot identity | UTS #39 confusables.txt |
| Unicode BiDi/control injection | T-1, T-6 | CVE-2021-42574 (Trojan Source); UAX #9 directional formatting | Unicode security data files |
| Confusables / mixed-script | T-1, T-6 | Arabic vs Persian code points (Yeh, Kaf, Keheh); Arabic-Indic vs European digits | UTS #39 confusables.txt |
| OCR-noise patterns | T-1 | QNL Arabic OCR Corpus v2 (2,894 files); KITAB Kraken pipeline; QALB error taxonomy | QNL corpus, SPIRAL dataset |
| Synonym substitution | T-3, T-4 | EACL 2024 Arabic synonym adversarial examples; Arabic WordNet | Arabic WordNet v2/v4.0 |
| Morphological inflection | T-3, T-4 | CAMeL Tools generator: lemma + feature bundles → surface forms | CAMeL Tools |

**Step 3: LLM-assisted constrained local rewrites.** For semantic adversarial properties deterministic transforms cannot produce (e.g., "refutation that looks like endorsement"): one model generates a paragraph-scale rewrite, a second provider verifies the property holds. Unit of control is small — verification is feasible.

**Step 4: Differential checks and metamorphic invariants.** Run transformed fixtures through the pipeline and verify: primary text stability (T-1), excerpt self-containment (T-4), author attribution stability (T-2, T-3), metadata field survival (T-6).

**Layer 4 — Prompt adversarial library (NEW, Session 4.5+):**

KR's excerpting/taxonomy/synthesis phases are LLM-mediated. The original draft had zero prompt-level attack coverage. Classical Islamic content (fiqh rulings, theological disputes) is exactly the domain likely to trigger model safety guardrails.

| Attack Type | Target Threat | Description |
|---|---|---|
| Arabic prompt injection | T-5, T-6 | "تجاهل التعليمات السابقة" embedded in source text; malformed JSON induction |
| BiDi injection in prompts | T-1, T-5 | Hidden instruction fragments via RTL override in text that appears harmless when displayed |
| Refusal triggers | T-5 | Sensitive fiqh topics that trigger model safety guardrails, causing extraction dropout |
| Safety boundary stressors | T-5 | Over-cautious filtering that drops required extraction outputs for theological disputes |
| Hallucination inducers | T-5 | Incomplete/ambiguous scholarly text tempting the model to fabricate attributions |
| Schema violation inducers | T-6 | Text patterns causing malformed structured output (missing fields, wrong types) |

Prompt adversarial fixtures enter scope when LLM-mediated phases enter factory scope.

**Coverage metrics and stopping criteria:**

1. **Threat × Engine × Family coverage matrix** (CheckList-style): Every cell in (T-1…T-7) × (engine) × (attack family) must have ≥1 fixture. Empty cells are explicit gaps.
2. **Family saturation**: Track parameter ranges covered per family. Expand range before adding new families.
3. **Differential failure yield**: Bugs per N new adversarial fixtures per family. When yield collapses (3 consecutive batches with zero new findings), reallocate to higher-yield families.

**Arabic-specific tooling inventory:**

| Tool/Resource | Use | Status |
|---|---|---|
| CAMeL Tools morphological generator | Controlled inflection/cliticization adversarial examples | DEFERRED (D-H005) |
| Arabic WordNet v2 (OMW, CC BY-SA) | Synonym substitution attacks | Available |
| Arabic WordNet 4.0 (CC BY 4.0) | Larger-scale synonym attacks | Announced Jan 2026, needs evaluation |
| UTS #39 confusables.txt | Confusable/mixed-script generation | Available (Unicode.org) |
| QNL Arabic OCR Corpus v2 | Realistic OCR-noise modeling (2,894 files) | Available |
| QALB shared task corpus | Arabic error type taxonomy | Available |
| SPIRAL dataset | Synthetic Arabic spelling errors (includes Shamela-derived) | Available |
| TextAttack / OpenAttack | Framework for plugging Arabic-specific transforms | Available |
| CheckList methodology | Behavioral test matrix generation | Available |

**Scoping constraint:** T-2 and T-3 adversarial fixtures are only useful after excerpting Phases 2-3 enter factory scope. T-1 and T-4 are testable against Phase 1 immediately. Prompt adversarial fixtures (Layer 4) enter scope with LLM-mediated phases.

**Cross-provider challenge record:**
- ChatGPT (deep research): Layer 3 "generate books" reframed to mined seeds + constrained synthesis (accepted). 7 evidence-backed Arabic adversarial attack families identified (accepted). Missing prompt adversarial coverage identified — new Layer 4 (accepted). CheckList-style coverage matrix + differential failure yield as stopping criteria (accepted). Arabic tooling inventory: CAMeL Tools, Arabic WordNet v2/v4.0, UTS #39, QNL OCR Corpus, QALB, SPIRAL (accepted). Mined-fixture lane from real corpus as highest-leverage approach (accepted).

### D-H011: Day 1 Scope — Dynamic Assessment

**Decision:** Factory Day 1 scope is determined by a dynamic gate assessment at launch time, not by the conservative static estimate in the v3 outline.

**Rationale:** The v3 outline (written 2026-03-28) conservatively estimated "Excerpting Phase 1 only" for Day 1. Since then, the excerpting engine has advanced significantly: 768+ tests passing, full 5-book integration run with 308 chunks in progress, pre-flight hardening complete. By factory launch (~week 8-10), excerpting Phases 2-3 are likely stable and tested.

**Gate criteria for including an engine phase in Day 1 scope:**

| Criterion | Evidence Required |
|-----------|-------------------|
| Tests passing | All tests for the phase pass with zero failures |
| Integration tested | At least one multi-book integration run completed |
| Owner probe | 30-book owner review initiated (NON-NEGOTIABLE for excerpting) |
| CLAUDE.md current | Module guide reflects actual code, not stale session |
| SPEC sections covered | Every SPEC section with a worked example has a corresponding test |
| No known blocking bugs | Zero CRITICAL/HIGH findings open against the phase |

**Assessment schedule:** The architect runs this gate assessment the week before factory launch (Session 7 timeframe). Whatever passes enters Day 1 scope. Whatever doesn't remains `wip` or `partial` in `ops_manifest.json`.

**Conservative fallback (if excerpting delays):** The v3 outline's original scope remains valid:

| Engine | Day 1 Status |
|--------|-------------|
| Source | All phases (gate approved a21aab9a) |
| Normalization | All phases (gate approved) |
| Excerpting | Phase 1 only (Phases 2-3 excluded) |

**Optimistic scenario (likely by week 8):**

| Engine | Day 1 Status |
|--------|-------------|
| Source | All phases |
| Normalization | All phases |
| Excerpting | All phases (Phase 1 deterministic + Phases 2-3 LLM) |
| Cross-engine | source→norm→excerpting boundary testing |

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

- **Aspect 3:** FINAL (cross-provider challenged 2026-03-28) — Morning report architecture (D-H008). Action-first layout, bounded CRITICALs (max 3 detail), clean-night fast path, trend deltas, consensus degradation warnings, embedded escalation provenance, two-layer data model (JSONL ledger + JSON snapshot), exception-only latency reporting, report archival. Alerting deferred to Session 8.
- **Aspect 4:** FINAL (cross-provider challenged 2026-03-28) — Orchestrator extension design (D-H009). 7 components (ScopeManager with engine DAG, SeverityClassifier as pure function, ToolDispatcher with minimum quorum, EscalationDetector with max_depth=1, FindingStore/RunJournal as persistence spine, ReviewOrchestrator as lifecycle state machine, MorningReportRenderer as pure renderer). Event-sourced persistence. Cross-run fingerprinting for deduplication. Cascading engine-DAG pause. Revised estimate 800-1,200 LOC. Session 6 may split into 6a/6b.
- **Aspect 5:** FINAL (cross-provider challenged 2026-03-28) — Synthetic adversarial data strategy (D-H010). 4 layers (was 3): Hypothesis property-based, overnight probes, mined seeds + constrained synthesis (was "generate books"), NEW prompt adversarial library. 7 evidence-backed Arabic attack families. Coverage matrix + differential failure yield as stopping criteria. Arabic tooling inventory. Corpus mining as highest-leverage approach.
- **Aspect 6:** RESOLVED — Day 1 scope expansion (D-H011). Dynamic assessment at launch: whatever passes gate criteria enters scope. Excerpting likely full-scope by factory launch. Conservative fallback preserved.

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
