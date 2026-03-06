# NEXT SESSION

## Session Type
IMPLEMENTATION_PREP (see SESSION_TYPES.md for full framework)

## Immediate Task

**Prepare the source engine for Claude Code implementation.**

This session bridges the gap between a complete SPEC and buildable code. The goal: create everything Claude Code needs to implement the source engine without asking clarifying questions.

## What to Read

1. `engines/source/SPEC.md` — the full SPEC (now hardened). Focus on §4.A and §9.
2. `engines/source/contracts.py` — existing Pydantic models. Check alignment with SPEC.
3. `reference/RESOURCES.md` — external tools/libraries available.
4. `.claude/skills/technology-survey/SKILL.md` — check before building custom code.
5. `tests/fixtures/` — existing test fixtures and their structure.

**Do NOT read:** VISION.md, other engine SPECs, CREATIVE_MANDATE.md.

**Budget:** ~15K tokens on reading. ~50K tokens on implementation prep. ~15K tokens on verification. ~10K tokens on handoff.

## The Implementation Prep Work (follow this sequence)

### Step 1: Contracts alignment
Verify that `contracts.py` Pydantic models match every schema requirement in the SPEC. Add missing models. Remove stale models. Every field in every model must trace to a SPEC requirement.

### Step 2: File/directory structure
Create the directory skeleton: `engines/source/`, staging area, frozen storage, registry paths. Create empty module files with docstrings that reference SPEC sections.

### Step 3: Test fixtures review
Check existing fixtures in `tests/fixtures/` against SPEC requirements. Identify which fixtures serve which test cases. Create a test plan mapping SPEC sections → test cases → fixtures.

### Step 4: External dependency check
For each external tool in RESOURCES.md that the source engine uses (Docling, OpenITI, etc.): verify it's installable, check version compatibility, write a minimal smoke test.

### Step 5: Implementation order document
Write `engines/source/IMPLEMENTATION_ORDER.md` — a numbered list of implementation tasks in dependency order. Each task: what to build, which SPEC section it implements, what it depends on, how to test it. Claude Code reads this to know what to do first.

## Definition of Done

1. `contracts.py` fully aligned with SPEC (all models, all fields, all enums)
2. Directory skeleton created
3. Test plan document written
4. External dependencies verified
5. `IMPLEMENTATION_ORDER.md` written
6. `check_spec_quality.py` still ≤4 high-severity defects
7. NEXT.md written for IMPLEMENTATION session
8. SESSION_LOG.md updated
9. Committed and pushed

## What the Previous Session Did

HARDENING session (2026-03-06): Verified no knowledge corruption paths in the source engine SPEC.

Changes:
- Added 7 explicit enrichment invariants to §2 (previously "does not violate any invariant" without enumeration)
- Added critical field enrichment gate: human gate for changes to author, work_id, genre, science_scope
- Added post-freeze hash verification: staging hash vs frozen hash comparison prevents copy corruption
- Added staging lock + TOCTOU protection: lock file + timestamp comparison prevents file modification between analysis and freeze
- Added write-ahead log pattern for atomic registry writes (previously claimed "atomic" without mechanism)
- Added 5 scholar record consistency checks: death date drift, school affiliation change, name immutability, self-reference, temporal consistency
- Hardened single-model consensus fallback: author ID now requires human gate when one model fails
- Added biographical inference confidence cap: single-LLM biographical data capped at 0.85 confidence
- Added missing structural file handling for Shamela extractor (info.html absent)
- Concretized owner-authored content validation (3 specific checks replacing vague "intelligent validation")
- Added 10 new error codes for hardening failure modes
- Quality maintained: 4 HIGH defects (same baseline, all §4.B/§9 false positives), §4.B score 90/100

## Pending Owner Questions

- **API keys:** Will be needed for the IMPLEMENTATION session (after IMPLEMENTATION_PREP). Not needed yet. The owner should prepare: Anthropic API key, OpenAI API key (for multi-model consensus), and optionally Google Document AI credentials (for Arabic OCR on photo scans).
