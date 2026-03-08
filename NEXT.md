# NEXT SESSION

## Context
Protocol finalized (2026-03-08): Tracer bullet (Step 0), iterative spec depth,
extension hooks, lessons backward reviews, shared component dependencies,
mature SPEC handling, engine-specific guidance. All skills aligned.

## What the Owner Should Do Now

1. **Setup** — follow OPEN_PROBLEMS.md (enable capabilities, upload 6 skill zips, create source engine project, create .env)
2. **First chat in source engine project:** "We need to run Step 0 from ENGINE_PROTOCOL.md — the tracer bullet. Reconcile the existing 7 contracts.py files against each other, stub the 4 shared components (consensus, human_gate, scholar_authority, validation), build rough engine stubs, create scripts/run_pipeline.py, and run html_export_minimal through the full pipeline."
3. **Claude reconciles** the 7 existing contracts.py files (fixing boundary mismatches), stubs shared components, builds engine stubs, runs one fixture through
4. **Boundary issues** are documented in `reference/TRACER_FINDINGS.md`
5. **Then** source engine Step 1: "Use kr-core-extract on the source engine SPEC. Classify core vs deferred."
6. **Review** the classification table (with extension hooks), correct any mistakes
7. **Claude rewrites** the SPEC focused on core only (source SPEC is immature — full §4.A rewrite needed)
8. **You read** the rewritten SPEC, write domain comments (heavy review — source engine is your strongest domain area)
9. **Resolve comments** with kr-spec-review across 1-3 chats
10. **Run kr-integrity** audit as quality gate before Step 2
