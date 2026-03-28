# KR Governance — Cross-Provider Review Team

**This document defines a NON-NEGOTIABLE governance rule for the KR project.**

## The Rule

Every reasonably major decision — architecture choices, SPEC designs, pre-run audits, transition gates, and any decision where a mistake would cause silent knowledge corruption — MUST be reviewed by the cross-provider team before approval.

The architect (Claude Chat) NEVER approves alone. The owner relays findings between providers.

## Why This Exists

**Session 28 proof:** During the pre-overnight-run audit, the architect AND ChatGPT 5.4 (deep research) BOTH reviewed the excerpting engine in depth. Neither found Finding 7 — a BLOCKING bug where duplicate `unit_index` values in LLM enrichment results silently overwrite enrichment data (wrong school attribution, wrong topic, zero detection signal). A fresh Claude Chat instance, reading the same code with zero prior context, found it in its first pass.

Without the review team, wrong school attributions would have shipped silently into the owner's study library. This is the exact corruption the entire KR architecture exists to prevent.

## The Team

| Provider | Role | Access | Best for |
|----------|------|--------|----------|
| **Claude Chat** (Architect) | Lead decision-maker, quality gate | Full project context + memory | Architecture, synthesis, final judgment |
| **CC** (Claude Code) | Builder, empirical validator | Direct repo access, code execution | Implementation, tests, running scripts |
| **ChatGPT 5.4** | Deep researcher | GitHub repo access, deep research mode | Risk analysis, comprehensive reports, SPEC review |
| **Fresh Claude Chat** (Opus) | Independent cold-read auditor | Repo via clone, zero context/bias | Finding what biased sessions miss, adversarial review |
| **Codex CLI** | Independent model verification | Repo access | Code review from a different model |
| **Gemini CLI** (optional) | Adversarial challenger | Needs files uploaded manually | General design review, NOT codebase-specific analysis |
| **Copilot CLI** (optional) | Quick spot checks | Repo access | Targeted single-file audits |

## When to Invoke

- Architecture decisions
- SPEC design or modification
- Pre-run audits (integration tests, overnight runs)
- Engine transition gates
- Any decision where "wrong" = silent knowledge corruption (T-1 through T-7)
- Any decision the architect is uncertain about

## How It Works

1. Architect prepares targeted prompts for each provider (different angles, not duplicates)
2. Owner fires prompts to each provider in parallel
3. Owner relays all findings back to architect
4. Architect synthesizes: convergent findings = high confidence, divergent = investigate until resolved
5. BLOCKING findings from ANY provider block the decision until fixed
6. Synthesis document committed to `reference/archive/sessions/`

## What "Major Decision" Means

If you're asking "do we need the team for this?" — you need the team. The cost of running the team is 30 minutes of the owner's time. The cost of skipping it is potentially wrong beliefs in the owner's study library, discovered weeks later or never.

Specifically NOT requiring the team: routine CC tasks (bug fixes with clear specs), documentation updates, test additions, configuration changes.
