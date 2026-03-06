# NEXT SESSION

## Session Type
IMPLEMENTATION

## Immediate Task

**Add LLM-assisted metadata inference to the source engine.**

The source engine now has working intake (format detection, freezing, metadata extraction, registry).
21 tests pass. But metadata extraction is shallow — it only gets what the format provides.
The next layer is §4.A.4: LLM inference that transforms sparse metadata into rich scholarly context.

Target: Given the waraqat_usul PDF (which extracts title + muhaqiq name), the LLM inference step should:
1. Identify the actual author (al-Juwayni, not the muhaqiq)
2. Classify the genre (matn)
3. Determine the science scope (usul al-fiqh)
4. Infer the scholarly level (beginner)
5. Create a placeholder scholar authority record

This requires:
- API key setup (.env file with Anthropic or OpenAI key)
- LiteLLM + Instructor for structured LLM output
- The inference prompt from SPEC §4.A.4
- Multi-model consensus for author identification (SPEC §6)

## Definition of Done

1. `python -m pytest engines/source/tests/ -v` passes with ≥30 tests (existing 21 + new inference tests)
2. Intake with LLM enrichment fills: genre, science_scope, authority_level, structural_format
3. Author identification uses multi-model consensus (2 models agree)
4. Low-confidence fields are flagged with needs_review
5. Shamela HTML extractor added (using html_export_minimal fixture)

## Files to Read

1. `engines/source/contracts.py` — data models (refresh)
2. `engines/source/SPEC.md` §4.A.4 (LLM Inference), §4.A.5 (Scholar Authority), §6 (Consensus)
3. `shared/consensus/SPEC.md` — consensus component spec
4. `.env.template` — which API keys are needed
5. `reference/RESOURCES.md` §LLM Orchestration — LiteLLM, Instructor

## What Last Session Did

Session 9 (Claude Chat):
- Technology survey: Docling, CAMeL Tools, Arabic embeddings, OpenITI all confirmed active 2026
- Fixed source contracts.py (WORD_DOC, WorkLevel, ScholarAuthorityRecord, registries)
- Created normalization contracts.py (ContentUnit, NormalizedManifest, NormalizedPackage)
- Fixed field naming (source_type → source_format in normalization SPEC)
- **Built source engine foundation: 8 source files, 21 passing tests**
  - Format detection, freezing, PDF/text extraction, registry, intake orchestrator
  - Works on real Arabic scholarly fixtures (waraqat PDF, alfiyyah text)
  - Duplicate detection verified
- Updated RESOURCES.md with 2026 survey findings

## Pending Owner Questions

- **API keys:** Need .env file with at least one of: ANTHROPIC_API_KEY, OPENAI_API_KEY
  (for LLM inference and multi-model consensus). Fill from .env.template.
