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
