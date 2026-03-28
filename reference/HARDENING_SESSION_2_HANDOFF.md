# Factory Hardening Session 2 — Continuation Handoff

**Date:** 2026-03-28
**Previous session error:** The architect rushed through Aspects 3-6 without cross-provider consultation, violating the methodology. D-H008 through D-H011 were committed as finished decisions but did NOT go through ChatGPT deep research, CC verification, or Gemini adversarial challenge. They must be treated as DRAFT proposals.

## What Is Actually Complete

**Aspect 1: Reference Data Integration — COMPLETE (previous session)**
D-H001 committed. Cross-provider: ChatGPT + CC + Gemini all consulted.

**Aspect 2: CLI Architecture + Cross-Provider Challenge — COMPLETE (this session)**
D-H002 updated with corrections from ChatGPT and Gemini challenge reports:
- D-H006: Severity escalation (two-path: pre-review field scan + mid-review LLM interrupt)
- D-H007: Shadow routing audit (5-10% canary check)
- D-H002: Codex CLI API key auth for factory, structured JSON output for all CLIs, consensus = architect-reviewed union
- Commits: `e7ca1a7b`

## What Needs Proper Cross-Provider Treatment

**Aspect 3: Morning Report Architecture — D-H008 is DRAFT**
The architect wrote this solo. Key decisions that need external challenge:
- Is morning report sufficient for CRITICALs, or does the factory need immediate alerting?
- Is the report structure (CRITICALs-first, per-tool visibility, escalation tracking) complete?
- Should there be a structured JSON intermediate for future dashboard?

**Aspect 4: Orchestrator Extension — D-H009 is DRAFT**
The architect designed 6 components (ScopeManager, SeverityClassifier, ToolDispatcher, EscalationDetector, FindingsManager, Morning Report v3) without external review. Key challenges:
- Is sequential dispatch correct at ~25 findings/night, or should HIGH+ reviews run concurrently?
- Is the component decomposition right? Too many? Too few? Wrong boundaries?
- What existing orchestration tools/patterns should we consider? (technology-landscape not run)

**Aspect 5: Synthetic Adversarial Data — D-H010 is DRAFT**
Three-layer strategy was written without consulting ChatGPT on what adversarial testing approaches exist in the Arabic NLP space. Missing: technology-landscape scan for adversarial testing tools.

**Aspect 6: Day 1 Scope — D-H011 is DRAFT**
Dynamic gate assessment concept is reasonable but was not challenged. Missing: Gemini adversarial challenge on whether the gate criteria are sufficient.

## Session Start Protocol

1. Clone the repo
2. Read `reference/FACTORY_HARDENING_DECISIONS.md` — the full document (D-H001–D-H011). D-H001 through D-H007 are FINAL. D-H008 through D-H011 are DRAFT.
3. Read `reference/FACTORY_HARDENING_BRIEFING.md` — background context
4. Read `reference/FACTORY_ROADMAP_v3_OUTLINE.md` — the 8 roadmap decisions
5. `git log --oneline -10`
6. `ls /mnt/skills/user/` — use: factory-session, technology-landscape, critical-review, thinking-frameworks
7. Drift check

## Methodology (DO NOT SKIP)

For EACH remaining aspect (3, 4, 5, 6):

1. Architect analyzes the aspect and reads the DRAFT decision (D-H008/9/10/11)
2. Architect prepares relay prompts for ChatGPT (deep research) and Gemini (adversarial)
3. Owner relays prompts, brings back results
4. Architect integrates findings — revises or confirms the DRAFT
5. If the DRAFT survives challenge: mark as FINAL
6. If the DRAFT needs revision: revise, re-challenge if significant changes, then finalize
7. Move to next aspect

For Aspect 4 specifically: run `use technology-landscape` BEFORE finalizing orchestrator design.

## Gemini Usage Note

Gemini web deep research CANNOT do codebase-specific analysis — it hallucinates repo contents. Two attempts in this session confirmed this (first: analyzed wrong repo sparxsystems/krino; second: right repo name but fabricated CAMeL Tools / PyArabic / NER integration that doesn't exist).

Use Gemini web ONLY for general design review questions ("Is this morning report structure missing anything?", "What orchestration patterns exist for multi-tool dispatch?"). Do NOT ask Gemini web to analyze the actual codebase.

For codebase-specific adversarial challenges, use Gemini CLI with local repo access.

## Previous Session Lessons (Still Apply)

1. Verify factual claims from previous sessions — don't trust briefings blindly
2. Check warnings against actual scale before constraining
3. Never commit architecture without cross-provider consultation
4. Don't ask the owner to validate tools they haven't used
5. NEW: Don't rush through aspects solo to "finish faster" — the methodology exists for a reason
