Factory hardening session — continuation. The previous chat completed Aspects 1-2, committed the results, and ran out of context. This session integrates the final cross-provider challenge on Aspect 2, then continues with Aspects 3-6.

<session_start>
1. Clone the repo
2. Read `reference/FACTORY_HARDENING_DECISIONS.md` — this is the primary output from the previous session (commit `2306f636`). It contains 5 design decisions (D-H001 through D-H005) covering reference data integration, four-tool CLI architecture, severity classification, testing tools, and tool deferrals.
3. Read `reference/FACTORY_HARDENING_BRIEFING.md` — background context (7 original findings, tool inventory, owner resources)
4. Read `reference/FACTORY_ROADMAP_v3_OUTLINE.md` — the 8 roadmap decisions this factory is built on
5. `git log --oneline -10`
6. `ls /mnt/skills/user/` — use: factory-session, technology-landscape, critical-review, thinking-frameworks, tool-evaluation, deep-research
7. Drift check
</session_start>

<what_was_completed>
**Aspect 1: Arabic & Islamic Scholarly Tools + Reference Data Integration — COMPLETE**

Cross-provider research (ChatGPT deep research + CC empirical verification + Gemini adversarial challenge) produced these results:

- **usul-data** (seemorg/usul-data): 6,159 authors, 15,655 books, 39-genre taxonomy. CC verified 89.2% match rate against our 65 fixtures. 7/7 author death years matched exactly. Two enrichment cases found. Integration architecture committed as D-H001.
- **Wikidata SPARQL**: madhhab (P9929), teacher/student (P1066/P802) confirmed as triangulation layer. Our contracts already have cross-validation stubs.
- **CAMeL Tools**: Partial install, morphological analysis works but overlaps with existing KR normalization. DEFERRED to Scholar Interface phase.
- **Mutmut**: Blocked on native Windows, works on WSL2. DEFERRED to Session 2.5+.
- **Hypothesis**: Viable with custom Arabic-aware strategies (not raw string generation). Strategy documented in D-H004.
- **Firewall rule adopted from Gemini's challenge**: External data NEVER writes to canonical registries. Writes to `*_crossref.json` with provenance tags. Architect promotes to `scholars.json` via human gate.

Key correction: Our Shamela exports have NO numeric book IDs (filenames are Arabic titles). The join to usul-data requires fuzzy Arabic title + author matching, not numeric lookup. CC verified this works at 89%.

**Aspect 2: CLI Tool Architecture & Model Routing — DECISIONS COMMITTED, CROSS-PROVIDER CHALLENGE PENDING**

The previous session made a critical error: it initially accepted the briefing's claim that "Codex CLI does not exist" without verification. The owner corrected this — Codex CLI is real (OpenAI, v0.116.0). All four CLIs verified working on owner's Windows 11:

| Tool | Syntax |
|------|--------|
| Claude Code | Interactive + scripted |
| Codex CLI | `codex exec --full-auto "prompt"` |
| Copilot CLI | `copilot -p "prompt" --model gpt-4.1` |
| Gemini CLI | `gemini -p "prompt" -o text -y` |

Four-tool routing table committed as D-H002. Owner subscriptions: Claude Max (unlimited), ChatGPT Plus ($20/mo), Copilot Student (free, 300 premium/mo), Google AI Pro ($19.99/mo planned).

**HOWEVER: D-H002 was committed WITHOUT cross-provider consultation on the routing architecture.** The architect recognized this protocol violation and prepared two challenge prompts. The owner has sent these to ChatGPT (deep research) and Gemini (deep research/adversarial). Their reports are attached to this message.
</what_was_completed>

<immediate_task>
**TASK 1: Integrate ChatGPT and Gemini challenge reports on D-H002**

Read both attached reports. For each challenge raised:
1. Is it valid? (Check against the actual code and architecture in the repo)
2. If valid, does it break D-H002 or can it be addressed within the existing design?
3. If it breaks D-H002, propose a revision

Then update `reference/FACTORY_HARDENING_DECISIONS.md` with any changes. If no changes needed, add a section documenting that the cross-provider challenge was completed and what was evaluated.

The specific challenges the reports should address:
- **ChatGPT was asked:** Is GPT-4.1 strong enough for routine review? WSL2 interop with Windows-side CLIs? Better orchestration patterns than subprocess? Quota tracking across providers?
- **Gemini was asked:** Can the deterministic severity classifier miss CRITICAL bugs in LOW-severity fields? What if GPT-4.1 has systematic Arabic blind spots? How hard is it to extend overnight_orchestrator.py for four-tool dispatch? Can severity escalate mid-review?
</immediate_task>

<remaining_aspects>
After Task 1, continue with the remaining hardening aspects. Work in the same small-step methodology as the previous session:

**Aspect 3: Monitoring, alerting, and morning report architecture**
- How does the factory report its nightly findings to the owner?
- Alerting for CRITICAL findings (immediate notification vs. morning report)
- Dashboard vs. structured text report vs. both
- What metrics should the morning report track?

**Aspect 4: Orchestrator extension design**
- How to extend `scripts/overnight_orchestrator.py` (1,405 lines) for multi-mode, multi-tool dispatch
- Work queue design for severity-routed findings
- Error handling and recovery when CLI tools fail mid-review
- State management across nightly runs

**Aspect 5: Synthetic adversarial data for Arabic text**
- Generating adversarial test inputs for Arabic-specific edge cases
- Targeting decontextualization (T-2), wrong attribution (T-1), and boundary errors
- Which tool generates, which tool processes, which tool evaluates

**Aspect 6: Day 1 scope expansion**
- The excerpting engine is advancing fast (737+ tests, full 5-book integration run in progress)
- By factory launch (~week 8-10), all of Phase 1 (Source + Norm + Excerpting) may be complete
- Plan factory Day 1 scope for full Phase 1, not the conservative estimate in v3 outline

For each aspect: analyze, prepare relay prompts for ChatGPT/CC/Gemini, wait for results, integrate, finalize.
</remaining_aspects>

<lessons_from_previous_session>
The previous session made several errors that the new session should not repeat:

1. **Accepted "Codex CLI doesn't exist" without verification.** The briefing made a factual claim, the architect treated it as truth, and built architecture on top of it. ALWAYS verify factual claims from previous sessions against current evidence.

2. **Overcorrected based on ChatGPT's Codex quota warning.** ChatGPT warned that Plus limits make Codex "not reliable for high-volume overnight pipelines." The architect initially restricted Codex to "3-5 targeted reviews per night" — but our actual volume (~25 findings/night) is well within the 33-168 messages/5hr window. Check warnings against actual scale before constraining.

3. **Committed D-H002 without cross-provider consultation.** The cross-provider architect rule is non-negotiable — no architecture decision without consulting at least ChatGPT + one adversary. The architect recognized this after committing and prepared challenge prompts, but the protocol was violated.

4. **Asked the owner to validate architectural decisions the owner hasn't used.** The owner has experience with Claude Code and some Codex experience. The owner has never used Copilot CLI or Gemini CLI. Asking the owner to rank tools they haven't used is wasting their time — the architect should make the decision and verify empirically.

Do not repeat these patterns.
</lessons_from_previous_session>

<owner_context>
- Owner is an Islamic studies STUDENT (has NOT studied texts yet). Cannot validate domain correctness.
- Zero technical background. On Windows 11.
- Budget: UNLIMITED. Will buy any subscription/tool needed.
- Time: UNLIMITED. Quality is the only metric.
- Has all four CLIs installed and working.
- Currently building the excerpting engine in parallel (737+ tests per NEXT.md, full 5-book integration run in progress).
- Will relay prompts to ChatGPT (deep research mode), Codex CLI, and Gemini CLI on demand.
</owner_context>
