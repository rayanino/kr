# consensus — Multi-Model Agreement Component

Shared service called by engines that need independent LLM verification of high-stakes decisions.

## What It Does
Accepts a consensus request (prompt + schema + comparison strategy), dispatches to two LLMs in parallel via LiteLLM, compares structured responses via Instructor/Pydantic, returns a verdict (AGREE/DISAGREE/PARTIAL_AGREE/SINGLE_MODEL/FAILURE) with full audit trail.

## Consumers
- Source engine: author identification, work matching (categorical)
- Excerpting engine: self-containment (numerical, threshold 0.2), school attribution (categorical)
- Taxonomy engine: ambiguous placement 0.5–0.8 range (categorical)
- Atomization engine: explicitly NOT a consumer (D-035)

## Key Design Choices
- LiteLLM SDK (not proxy) for provider abstraction — one integration point for all LLM providers
- Instructor for structured output extraction with automatic schema validation retries
- Async parallel dispatch via asyncio.gather — both models called simultaneously
- Provider diversity mandatory — two models must be from different providers
- Three comparison strategies: categorical, numerical, structured
- Complete audit logging of every consensus round

## External Dependencies
LiteLLM, Instructor, Pydantic, PyYAML, asyncio (stdlib)

## Current State
ABD-era code (1749L consensus.py) — to be replaced entirely. Arabic text utils to be extracted to shared/arabic_text/. Everything in SPEC is [NOT YET IMPLEMENTED].

## Config
`config/consensus.yaml` — model roster, per-decision-type overrides, per-science hooks.

## SPEC Refinement Status
- Cycle 0 (not yet started)
- Implementation-ready: NO — refinement required before implementation
