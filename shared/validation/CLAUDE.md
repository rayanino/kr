# Algorithmic Validation — التحقق الخوارزمي

Layer 2 of the quality architecture (VISION.md §8.1). A shared toolkit of deterministic checks that engines import and call directly — not a service.

## Purpose

Catch mechanical errors through four categories of algorithmic checks: schema validation (JSON Schema compliance), structural validation (domain invariants — offsets, containment, coverage), referential integrity (cross-artifact references resolve), and integrity verification (hash chains from frozen source to placed excerpt). Also provides background sweep for library-wide integrity checks (§8.4).

## Key Boundaries

- Does NOT do content-level validation (self-containment, topic relevance) — that's engine Layer 1 or consensus.
- Does NOT manage human gates — reports results; engines decide actions.
- Does NOT store corrections — that's shared/feedback.
- All checks are deterministic. No LLM calls. No consensus needed.

## Architecture

A Python library with four modules: schema validators, structural validators, referential integrity validators, integrity verifiers. Plus a background sweep runner and validation orchestrator.

**Technology:** jsonschema (v4.26+), Pydantic v2, hashlib (stdlib), NetworkX.

**Universal output:** Every check returns a `ValidationResult` (Pydantic model) with status, severity, error code, and details. Batch operations return `ValidationReport`.

## What Engines Use

- **Source engine:** Schema validation, referential integrity (scholar + work registries).
- **Normalization engine:** Arabic plausibility, layer coverage, division tree validity, footnote integrity.
- **Passaging engine:** Schema validation.
- **Atomization engine:** Offset integrity, atom coverage, monotonic sequencing.
- **Excerpting engine:** Passage containment, atom uniqueness, text integrity, excerpt size bounds.
- **Taxonomy engine:** Tree integrity, tree leaf reference.
- **Synthesizing engine:** Schema validation, provenance completeness scoring.

## Transformative Capabilities

1. **Failure pattern intelligence** — Clusters validation failures by source type, engine version, and time to detect systematic issues (not individual errors).
2. **Provenance completeness scoring** — Assigns 0.0–1.0 score to excerpts based on how many provenance chain links are verified. Feeds into synthesis and scholar interface.

## Current Status

See SPEC.md for complete specification. ABD-era code (`cross_validate.py`, `run_all_validations.py`) is legacy — useful as implementation hints only.

## SPEC Refinement Status
- Cycle 0 (not yet started)
- Implementation-ready: NO — refinement required before implementation

## Claude Code Behaviour Guidelines

- **Ownership, not deflection:** When you encounter an issue, take responsibility and work towards a solution. Don't say "not caused by my changes" or "pre-existing issue." Don't give up with "known limitation" or defer to "future work." Fix it now.
- **Persistence through obstacles:** Don't stop at the first problem. Don't declare "good stopping point" or "natural checkpoint." Keep pushing until you have a complete, verified solution.
- **Initiative over permission-seeking:** If you have the knowledge and capability to solve a problem, act. Don't ask "should I continue?" or "want me to keep going?" Take initiative and drive towards the solution.
- **Plan before acting:** For multi-step work, plan which files to read, in what order, which tools to use, and what the expected outcome is — before touching anything.
- **Convention recall:** Always re-read and apply project-specific conventions from CLAUDE.md files. Don't rely on memory of what they say.
- **Self-correction loops:** Catch your own mistakes by applying reasoning loops and self-checks. Fix errors before committing or asking for help.
- **Verify, don't assume:** After reaching a conclusion or making a change, verify it against the actual state of the codebase. A conclusion you haven't verified is a guess. Run the test, read the output, check the file.
- **Trace root causes:** When something fails, trace the full causal chain. Don't patch symptoms — find and fix the underlying cause. A surface fix hides the real bug for later.

### Tool Use

- **Research-first, never edit-first:** Before using any tool, research the context and requirements. Read the relevant code, SPEC, and contracts before making changes. Understand before you act.
- **Surgical edits over rewrites:** Make targeted, minimal changes. Never rewrite whole files or make large sweeping changes when a focused edit achieves the goal.
- **Reasoning loops are mandatory:** Apply reasoning loops frequently. Don't skip them to save tokens. The cost of a wrong action far exceeds the cost of thinking.

### Thinking Depth

- Always apply the **highest level of thinking depth**. Shallow thinking leads to the cheapest available action, which is rarely the correct one. Spending more tokens on reasoning produces dramatically better outcomes.
- **Never reason from assumptions.** Always reason from actual data — read and understand the actual code, SPEC, or documentation before making decisions. Assumptions compound into errors.
