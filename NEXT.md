# NEXT — Start Normalization Engine

## Current position: Source engine COMPLETE → Normalization engine SPEC
## What to do: Begin normalization engine Step 1 (SPEC design)
## Context: Source engine validated and complete (reference/SOURCE_ENGINE_COMPLETION.md). 582 tests, 209 books, 4 fixes verified. Contract to normalization verified. Budget: €30.60 spent, ~€69.40 remaining.
## Owner action needed: No

**CRITICAL CONTEXT CORRECTION:** The owner is an Islamic studies STUDENT
who has NOT yet studied Islamic texts. KR exists to CREATE the study
environment. The owner CANNOT independently validate domain correctness
of metadata. Domain validation is performed by Claude Chat via web
research. Human gates are resolved via AI-assisted research, not owner
expertise. All repo documents, SPECs, and prompts that imply the owner
has deep domain knowledge are INCORRECT and should be read with this
understanding.

## Starting the normalization engine

The normalization engine SPEC already exists at `engines/normalization/SPEC.md`
(2006 lines). Contracts exist at `engines/normalization/contracts.py` (697 lines).
Stubs exist for all source modules. The tracer bullet produced a working
prototype in `engines/normalization/src/tracer.py`.

The normalization engine's input contract is documented in
`reference/CONTRACT_VERIFICATION_REPORT.md`.

Next session: Read the normalization SPEC, assess readiness for build,
and plan the implementation.
