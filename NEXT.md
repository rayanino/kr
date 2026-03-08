# NEXT SESSION

## Context
Protocol updated (2026-03-08): Added tracer bullet (Step 0), iterative spec depth,
extension hooks, lessons backward reviews. All skills and templates aligned.

## What the Owner Should Do Now

1. **Setup** — follow OPEN_PROBLEMS.md (enable capabilities, upload 6 skill zips, create source engine project, create .env)
2. **First chat in source engine project:** "We need to run Step 0 from ENGINE_PROTOCOL.md — the tracer bullet. Write contract SPECs (§2 and §3 only) for all 7 engines, then build rough stubs that pass one Shamela HTML file through the full pipeline."
3. **Claude writes** lightweight contracts for all 7 engines, builds stubs, runs one fixture through
4. **Boundary issues** are documented in `reference/TRACER_FINDINGS.md`
5. **Then** proceed to source engine Step 1: "Use kr-core-extract on the source engine SPEC. Classify core vs deferred."
6. **Review** the classification table (with extension hooks), correct any mistakes
7. **Claude rewrites** the SPEC focused on core only
8. **You read** the rewritten SPEC, write domain comments
9. **Resolve comments** with kr-spec-review across 1-3 chats
10. **Run kr-integrity** audit as quality gate before Step 2
